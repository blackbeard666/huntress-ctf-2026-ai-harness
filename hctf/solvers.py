"""Solver library: lookup, dispatch, regression cases.

Solver contract (every challenge, every mode):
  challenges/dayNN/<lane>-<title>/solver/solve.py --contract <contract.json> --artifacts <dir>
    -> prints JSON {answer_id: value} on stdout for every question it can answer.
  The contract is the GM start/status body: questions[] (id, question, artifact, answer_format,
  normalization, set) aligned with answer_ids[]. Solvers must read inputs from the contract and the
  artifact bytes, never hard-code values: Time Trial / Mastery hand out different variants.

Regression cases: .../solver/cases/<case>/{contract.json, artifacts/, expected.json}
  expected.json holds only answers the GM confirmed (CORRECT/accepted).
"""
import ast
import difflib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from .paths import (ROOT, TMP, VENV_PY, all_solver_dirs, base_id, lane_solver_dirs, mode_of,  # noqa: F401 (re-exported)
                    solver_dir)


def _norm(text):
    return re.sub(r"\s+", " ", re.sub(r"\d+", "#", (text or "").lower())).strip()


def question_index():
    """normalized question text -> solver dir, built from every solver's regression cases."""
    idx = {}
    for sdir in all_solver_dirs():
        for contract in sdir.glob("cases/*/contract.json"):
            for q in json.loads(contract.read_text()).get("questions", []):
                idx.setdefault(_norm(q.get("question")), sdir)
    return idx


def _pair_index(ids, qs):
    """D24 #2: lookup(answer_id) -> question by an exact-id index, else the LONGEST question id the answer id ends with
    at a `.`/`_`/`-` boundary (the old regex scan's rule), else None (the caller falls back to position). The scan was
    O(ids x questions): 12,480 script Mastery ids cost 12.9 s here and 17.8 s in hb_timed's start phase. None when the
    index can't promise the scan's exact answer (a non-dict question, a non-str id, an id with a newline -- `$` also
    matches before a trailing newline): the caller keeps the scan."""
    if not isinstance(ids, list) or not isinstance(qs, list):
        return None
    exact = {}
    for q in qs:
        if not isinstance(q, dict):
            return None
        qid = q.get("id")
        if qid is None:
            continue
        if not isinstance(qid, str) or "\n" in qid:
            return None
        exact.setdefault(qid, q)          # the scan's next(): the FIRST question with that id
    if any(not isinstance(a, str) or "\n" in a for a in ids):
        return None

    def lookup(aid):
        q = exact.get(aid)
        if q is None:
            for j, c in enumerate(aid):   # leftmost boundary first = the longest suffix (an empty id never matches)
                if c in "._-" and j + 1 < len(aid):
                    q = exact.get(aid[j + 1:])
                    if q is not None:
                        break
        return q
    return lookup


def paired_questions(contract):
    """[(answer_id, question)]: exact question id, else the question id the answer id ends with (bundles like
    answer_ids slot0_marker..slot3_marker sharing one 'marker' question), else by position.
    HCTF_PAIR_INDEX=0: the old per-id scan of every question (D24 #2)."""
    ids, qs = contract.get("answer_ids", []), contract.get("questions", [])
    look = _pair_index(ids, qs) if os.environ.get("HCTF_PAIR_INDEX", "1") != "0" else None
    out = []
    for i, aid in enumerate(ids):
        if look is not None:
            q = look(aid)
        else:
            q = next((q for q in qs if q.get("id") == aid), None)
            if q is None:
                sufs = [q for q in qs if q.get("id") and re.search(rf"(^|[._-]){re.escape(q['id'])}$", aid)]
                q = max(sufs, key=lambda q: len(q["id"]), default=None)
        if q is None and i < len(qs):
            q = qs[i]
        out.append((aid, q or {}))
    return out


def dispatch(contract, default_solver=None):
    """Group the contract's answer_ids by the solver that should answer them.
    Returns ({solver_dir: [answer_id, ...]}, [unmatched answer_ids])."""
    idx = question_index()
    keys = list(idx)
    # The challenge's own solver wins for questions its cases cover: identical wording is reused across days for a
    # different artifact type (Day 4 VBScript "Recover the primary MITRE ATT&CK technique ID, or none." = Day 3 Batch).
    own = set()
    if default_solver is not None:
        for c in Path(default_solver).glob("cases/*/contract.json"):
            own.update(_norm(q.get("question")) for q in json.loads(c.read_text()).get("questions", []))
    groups, unmatched = {}, []
    for aid, q in paired_questions(contract):
        n = _norm(q.get("question"))
        sdir = default_solver if n in own else idx.get(n)
        if sdir is None and keys:
            close = difflib.get_close_matches(n, keys, n=1, cutoff=0.85)
            sdir = idx[close[0]] if close else None
        sdir = sdir or default_solver
        if sdir is None:
            unmatched.append(aid)
        else:
            groups.setdefault(sdir, []).append(aid)
    return groups, unmatched


def sub_contract(contract, answer_ids):
    """The contract restricted to some answer_ids (lets one bundle be split across several solvers)."""
    ids = contract.get("answer_ids", [])
    qs = contract.get("questions", [])
    if len(ids) == len(qs) and all(q.get("id") in (None, a) for a, q in zip(ids, qs)):
        keep = [i for i, a in enumerate(ids) if a in answer_ids]
        c = dict(contract)
        c["answer_ids"] = [ids[i] for i in keep]
        c["questions"] = [qs[i] for i in keep if i < len(qs)]
        return c
    # answer_ids and questions not 1:1 (shared questions) -> keep the ids plus the questions they reference
    c = dict(contract)
    c["answer_ids"] = [a for a in ids if a in answer_ids]
    used = [id(q) for a, q in paired_questions(contract) if a in answer_ids]
    c["questions"] = [q for q in qs if id(q) in used]
    return c


def answer_str(v):
    """A solver's JSON value as the answer string: lists/dicts as COMPACT JSON, never Python's repr (D23 metadata
    Mastery: a returned list became `['box-06/part-6.log', ...]` via str() and was rejected on every set)."""
    if isinstance(v, str):
        return v
    if isinstance(v, (list, dict)):
        return json.dumps(v, separators=(",", ":"), ensure_ascii=False)
    return str(v)


def run_solver(sdir, contract, artifacts, timeout=120, background=None, deadline=None, env_extra=None):
    """Run one solver. Returns (answers dict, error string or None, seconds).
    Own process group, killed as a group on timeout (its fork pool too); background=True (or the calling thread's
    procgov flag) = the low-priority class -- see hctf/procgov.py. deadline = seconds from now: HCTF_SOLVE_DEADLINE
    (epoch) for the solver, so a partial-emit solver (lib.solverrt / lib.websolve.race) prints what it has by then
    instead of being killed silent at `timeout`. env_extra: overrides for the solver's environment (small_pool_env)."""
    from . import procgov
    if not (Path(sdir) / "solve.py").exists():
        return {}, f"no solver yet at {Path(sdir).relative_to(ROOT)}/solve.py", 0.0
    tmp = TMP / f"contract-{sdir.parent.name}-{time.time_ns()}.json"
    tmp.write_text(json.dumps(contract))
    py = str(VENV_PY) if VENV_PY.exists() else "python3"
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"  # solvers can `import lib.*`
    env.update(env_extra or {})
    t0 = time.time()
    if deadline is not None:
        env["HCTF_SOLVE_DEADLINE"] = f"{t0 + float(deadline):.3f}"
    try:
        r = procgov.run([py, str(sdir / "solve.py"), "--contract", str(tmp), "--artifacts", str(artifacts)],
                        timeout=timeout, cwd=sdir, env=env, background=background)
    except subprocess.TimeoutExpired:
        return {}, f"timeout after {timeout}s", time.time() - t0
    finally:
        tmp.unlink(missing_ok=True)
    dt = time.time() - t0
    if r.returncode:
        return {}, f"exit {r.returncode}: {r.stderr.strip()[-1500:]}", dt
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
        return {k: answer_str(v) for k, v in out.items()}, None, dt
    except (IndexError, ValueError):
        return {}, f"stdout is not JSON: {r.stdout[-500:]!r} stderr: {r.stderr[-800:]}", dt


def _rel_root(p):
    """`p` relative to the project root for display, else its absolute path (a prior solver copied under /tmp)."""
    try:
        return str(Path(p).resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(Path(p).resolve())


def dry_run_diagnostics(sdir, contract, artifacts, timeout=15, known=None, shape=None):
    """Run an EARLIER day's solver once on TODAY's contract + bytes and return DIAGNOSTICS ONLY -- never its values
    (user rule: old solvers are not an answer source). On a timeout it gets SIGINT first, so the traceback names the
    loop that hangs. Rehearsal D8: the copied Day 7 binary solver hung twice to the worker's 60 s cap on a 67 MB Swift ELF
    (~140 s of the single) before the worker found the slow path. Returns a dict (see render_dry_run)."""
    from . import procgov
    tmp = TMP / f"dryrun-{Path(sdir).parent.name}-{time.time_ns()}.json"
    tmp.write_text(json.dumps(contract))
    py = str(VENV_PY) if VENV_PY.exists() else "python3"
    env = dict(os.environ, PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}")
    t0 = time.time()
    timed_out = False
    try:
        # SIGINT to the group first (KeyboardInterrupt -> a traceback at the hot loop), then SIGKILL the group
        r = procgov.run([py, str(Path(sdir) / "solve.py"), "--contract", str(tmp), "--artifacts", str(artifacts)],
                        timeout=timeout, cwd=sdir, env=env, grace=3)
        out, err, rc = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        out, err, rc = e.output or "", e.stderr or "", -2     # SIGINT, then the group was killed
    finally:
        tmp.unlink(missing_ok=True)
    dt = time.time() - t0
    ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions") or [] if q.get("id")]
    got = {}
    try:
        got = json.loads((out or "").strip().splitlines()[-1])
    except (IndexError, ValueError):
        pass
    lines = (err or "").splitlines()
    allf = [ln.strip() for ln in lines if ln.strip().startswith("File ")]
    # The solver's OWN innermost frames say which function hangs; library frames (pyelftools...) only say where.
    own = [f for f in allf if str(Path(sdir).resolve()) in f or f"{ROOT}/lib/" in f]
    frames = [re.sub(r'"[^"]*/', '"', f) for f in own[-3:] + ([allf[-1]] if allf and allf[-1] not in own else [])]
    warn = []
    for ln in lines:
        if ("[!]" in ln or "unknown" in ln.lower() or "warning" in ln.lower()) and ln.strip() not in warn:
            warn.append(ln.strip()[:160])
    last = next((ln.strip() for ln in reversed(lines) if ln.strip()), "")
    empty = [i for i in ids if got.get(i) in (None, "")] if isinstance(got, dict) else list(ids)
    # The questions behind the empty ids (TODAY's contract text -- no solver values): D9 binary's worker spent 2 turns
    # (~15 s) jq-hunting the one new field the dry run had named.
    qs = {q.get("id"): q for q in contract.get("questions") or [] if q.get("id")}
    empty_q = {}
    for i in empty[:EMPTY_Q_MAX]:
        q = qs.get(i) or {}
        fmt = q.get("answer_format") or {}
        empty_q[i] = {"question": str(q.get("question", ""))[:240], "artifact": q.get("artifact"),
                      "format": {k: fmt[k] for k in ("kind", "syntax", "accepted_values") if fmt.get(k)} or None,
                      "normalization": q.get("normalization")}
    # NEW today = ids whose shape (set prefix + variant counter stripped) no prior case asks; grouped by the artifact
    # member they point at, so the worker reads exactly those files. Names + today's contract only, never values.
    new, new_by_art = [], {}
    if known:
        shape = shape or (lambda a: a)
        new = [i for i in dict.fromkeys(ids) if shape(i) not in known]
        for i in new:
            new_by_art.setdefault(str((qs.get(i) or {}).get("artifact") or "?"), []).append(i)
    return {"solver": _rel_root(sdir), "seconds": round(dt, 1), "timed_out": timed_out,
            "rc": rc, "frames": frames, "error": last[:200] if (rc and not timed_out) else "",
            "warnings": warn[:8], "answered": len(ids) - len(empty), "total": len(ids), "empty": empty[:15], "empty_all": empty,
            "empty_q": empty_q, "new": len(new), "new_by_art": new_by_art}


EMPTY_Q_MAX = 6   # dry-run render: full question text for this many empty ids (a 1-5 field delta is the usual day)
NEW_GROUPS_MAX = 10  # dry-run render: artifact groups of NEW-today ids listed


def profile_solver(sdir, case_dir, timeout=45, top=25, interrupt=False):
    """cProfile of solve.py on one regression case -> the top `top` rows by cumulative time (text), or ''. Handed to a
    speed generalize so the worker starts at the hot path (rehearsal D8 + d8tc1: both speed workers lost a turn to a profile
    piped to /dev/null). interrupt=True: SIGINT at `timeout` instead of giving up -- cProfile still prints the stats of
    the run so far (a solver too slow to finish is exactly the one worth profiling)."""
    from . import procgov
    case_dir = Path(case_dir)
    if not (case_dir / "contract.json").exists():
        return ""
    py = str(VENV_PY) if VENV_PY.exists() else "python3"
    env = dict(os.environ, PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}")
    argv = [py, "-m", "cProfile", "-s", "cumtime", str(Path(sdir).resolve() / "solve.py"), "--contract",
            str(case_dir.resolve() / "contract.json"), "--artifacts", str(case_dir.resolve() / "artifacts")]
    cut = ""
    try:
        # interrupt: SIGINT to the group at `timeout` -- cProfile still prints the stats so far -- then SIGKILL it
        stdout = procgov.run(argv, timeout=timeout, cwd=sdir, env=env, grace=10 if interrupt else 0).stdout
    except subprocess.TimeoutExpired as e:
        if not interrupt:
            return f"(profile of {case_dir.name} did not finish in {timeout}s)"
        stdout = e.output or ""
        cut = f", INTERRUPTED at {timeout:g}s"
    out = (stdout or "").splitlines()
    i = next((k for k, ln in enumerate(out) if ln.strip().startswith("ncalls")), None)
    if i is None:
        return f"(profile of {case_dir.name} did not finish in {timeout:g}s)" if cut else ""
    head = next((ln.strip() for ln in out if "function calls" in ln), "")
    rows = [re.sub(r"/[^\s]*/(site-packages|huntress-2026[^/]*)/", r"\1/", ln.rstrip()) for ln in out[i:i + top + 1]]
    return f"cProfile of `cases/{case_dir.name}` ({head}{cut}):\n" + "\n".join(rows)


def render_dry_run(d):
    """Markdown for the worker: how yesterday's solver behaved on today's bytes. Field NAMES only, never values."""
    if not d:
        return ""
    head = (f"PRIOR SOLVER DRY RUN (harness ran `{d['solver']}/solve.py` on TODAY's contract + bytes; diagnostics only, "
            f"its values are withheld): ")
    if d["timed_out"]:
        head += f"did NOT finish in {d['seconds']:g} s (interrupted)."
    elif d["error"]:
        head += f"crashed after {d['seconds']:g} s: {d['error']}"
    else:
        head += f"finished in {d['seconds']:g} s, answered {d['answered']}/{d['total']} ids."
    parts = [head]
    if d["frames"]:
        parts.append("Where it was (innermost last): " + " | ".join(d["frames"][-4:]))
    if d["empty"] and not d["timed_out"]:
        parts.append(f"Left empty ({d['total'] - d['answered']}): " + ", ".join(f"`{x}`" for x in d["empty"][:15]))
        eq = d.get("empty_q") or {}
        if eq and d["total"] - d["answered"] <= EMPTY_Q_MAX:
            parts.append("The empty fields' questions (today's contract; the ids it DID answer still need checking against today's bytes):")
            for i, q in eq.items():
                bits = [f"artifact {q['artifact']!r}" if q.get("artifact") else "",
                        f"format {json.dumps(q['format'], ensure_ascii=False)[:200]}" if q.get("format") else "",
                        f"normalization {q['normalization']}" if q.get("normalization") else ""]
                parts.append(f"  - `{i}`: {q.get('question') or '(no question text)'}"
                             + (f" [{'; '.join(b for b in bits if b)}]" if any(bits) else ""))
    groups = d.get("new_by_art") or {}
    if groups:
        parts.append(f"NEW today ({d['new']} ids no earlier regression case asks -- what today's bytes must back; "
                     f"the rest are earlier families), by artifact:")
        k = 15 if d["new"] <= 15 else 4  # a small delta (D11 binary: 10 ids, one zip) is listed whole
        for art, ids_ in list(groups.items())[:NEW_GROUPS_MAX]:
            shown = ", ".join(f"`{x}`" for x in ids_[:k]) + (f", ... (+{len(ids_) - k})" if len(ids_) > k else "")
            parts.append(f"  - `{art}` ({len(ids_)}): {shown}")
        if len(groups) > NEW_GROUPS_MAX:
            parts.append(f"  - ... {len(groups) - NEW_GROUPS_MAX} more artifact(s)")
    if d["warnings"]:
        parts.append("Its own warnings: " + " / ".join(d["warnings"][:6]))
    if d["timed_out"] or d["seconds"] > 2.5:
        parts.append("Fix that slow path FIRST (Mastery runs it once per set inside the clock); don't re-run the whole "
                     "copied solver blind.")
    return "\n".join(parts)


def _day_key(sdir):
    if "_lane" in Path(sdir).parts:
        return LANE_DAY_KEY       # challenges/_lane/<lane>/solver: cumulative over every day -> newest of all
    m = re.search(r"day(\d+)", str(sdir))
    return int(m.group(1)) if m else -1


LANE_DAY_KEY = 999


def whole_contract_solver(contract, artifacts, candidates, timeout=120):
    """The first candidate solver (NEWEST day first) that answers EVERY answer_id of the FULL contract, as
    (solver_dir, answers), else (None, {}). Question-text dispatch splits a compound bundle across days because
    question wording repeats (Day 4 'Dim and Dimmer' = Day 3 batch questions + VBScript): the Day 4 solver handles all
    231 ids on the whole contract but only 20/46 on its slice, so reuse-first missed and an LLM worker re-solved it."""
    ids = contract.get("answer_ids") or []
    for sdir in sorted(set(candidates), key=_day_key, reverse=True):
        got, err, _ = run_solver(sdir, contract, artifacts, timeout)
        if not err and ids and all(got.get(a) not in (None, "") for a in ids):
            return sdir, {a: got[a] for a in ids}
    return None, {}


def solve_contract(contract, artifacts, default_solver=None, timeout=120, try_whole=True):
    """Dispatch a whole contract across solvers. Returns (answers, problems list).
    When dispatch splits the bundle across several solvers, first try each of them on the FULL contract."""
    groups, unmatched = dispatch(contract, default_solver)
    if try_whole and len(groups) > 1:
        _, got = whole_contract_solver(contract, artifacts, list(groups), timeout)
        if got:
            return got, []
    answers, problems = {}, [f"{a}: no solver matches this question" for a in unmatched]
    for sdir, aids in groups.items():
        got, err, _ = run_solver(sdir, sub_contract(contract, aids), artifacts, timeout)
        if err:
            problems.append(f"{sdir.relative_to(ROOT)}: {err}")
        for a in aids:
            if a in got and got[a] != "":
                answers[a] = got[a]
            elif not err:
                problems.append(f"{a}: solver {sdir.name} returned no answer")
    return answers, problems


def add_case(sdir, name, contract, artifacts, expected):
    """Save a regression case (variant) into the solver's cases/ directory."""
    case = Path(sdir) / "cases" / name
    if case.exists():
        shutil.rmtree(case)
    (case / "artifacts").mkdir(parents=True)
    for f in (Path(artifacts).iterdir() if artifacts else ()):   # a live-target (web) attempt has no bytes
        if f.is_file() and f.name not in ("manifest.json", "contract.json", "result.json"):
            shutil.copy2(f, case / "artifacts" / f.name)
    (case / "contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False))
    (case / "expected.json").write_text(json.dumps(expected, indent=2, ensure_ascii=False))
    from . import webtarget
    if webtarget.is_live_body(contract):
        # replayable only while its attempt's target is up (hctf/webtarget.case_stale): test_solver skips it after
        (case / "live_target.json").write_text(json.dumps({"attempt": contract.get("attempt_id"),
                                                           "targets": webtarget.target_urls(contract)}))
    return case


# A variant case's gm_feedback.json (orchestrate.capture_variant) = the GM's verdicts on that attempt beyond the accepted
# answers in expected.json: values it REJECTED per field + require_complete. With it a case passes only if no rejected
# value comes back and (require_complete) every field is answered -- not just "the verified subset still matches".
VERIFIED_GREEN = os.environ.get("HCTF_VERIFIED_GREEN", "1") != "0"


def targets_pass(sdir, targets, fill=(), timeout=8, reject_free=()):
    """Cheap pre-check for the generalize green watchers: do the TARGET cases pass, the FILL cases come out complete and
    the REJECT_FREE cases come out complete with no GM-rejected value? Only then is the whole corpus worth replaying
    (rehearsal D13 replay: up to 4 full suites at once on every edit, most of them on code that still failed its target).
    True when there is nothing to pre-check."""
    names = set(targets) | set(fill) | set(reject_free)
    if not names:
        return True
    res = test_solver(sdir, timeout=timeout, cases=sorted(names))
    by = {r["case"]: r for r in res}
    if any(not (by.get(t) or {}).get("ok") for t in targets):
        return False
    if any(not (by.get(t) or {}).get("reject_free") for t in reject_free):
        return False
    return all((by.get(f) or {}).get("total") and by[f].get("answered") == by[f].get("total") and not by[f].get("error")
               for f in fill)


# D25 post-mortem C2: an UNVERIFIED case (empty expected.json: a failed variant, an old carried variant-*) can never be
# `ok`, so the generalize Stop gate (ensure_case_and_test: every case ok) blocked a worker that had the fix at +39 s for
# ~130 s more, until it wrote HELP.md. For the GATE such a case passes when the solver answers every field, reproduces no
# value the GM rejected (gm_feedback.json) and does not error -- `reject_free`. `ok` itself is unchanged (the
# transactional accept and the verified-green watchers still read it). 0 = the old gate (every case ok).
GATE_REJECT_FREE = os.environ.get("HCTF_GATE_REJECT_FREE", "1") != "0"
# C1: cases with byte-identical contract + artifacts (D25 warmups: mastery-X / variant-mastery-X / auto-mastery-X
# triplets, 33 of 36 cases carried over from earlier days) run the solver ONCE; each case is still judged against its
# own expected.json / gm_feedback.json. 0 = one solver run per case.
CASE_DEDUPE = os.environ.get("HCTF_CASE_DEDUPE", "1") != "0"
_SHA_CACHE = {}


def _file_sha(p):
    """sha256 of a file, cached by (device, inode, size, mtime): hard-linked case artifacts hash once per process."""
    import hashlib
    try:
        st = p.stat()
    except OSError:
        return None
    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
    h = _SHA_CACHE.get(key)
    if h is None:
        d = hashlib.sha256()
        try:
            with open(p, "rb") as f:
                for blk in iter(lambda: f.read(1 << 20), b""):
                    d.update(blk)
        except OSError:
            return None
        h = _SHA_CACHE[key] = d.hexdigest()
    return h


def case_key(case, full=True):
    """Identity of what a solver run on this case sees: its contract.json bytes + every artifact's (name, sha256), or
    (full=False, the cheap pre-key) its (name, size). None when unreadable (never deduped)."""
    import hashlib
    try:
        h = hashlib.sha256(Path(case, "contract.json").read_bytes())
        for f in sorted(Path(case, "artifacts").rglob("*")):
            if f.is_file():
                s = _file_sha(f) if full else str(f.stat().st_size)
                if s is None:
                    return None
                h.update(f"\0{f.relative_to(Path(case, 'artifacts'))}\0{s}".encode())
    except OSError:
        return None
    return h.hexdigest()


def _dedupe_groups(cases):
    """[[case, ...], ...]: byte-identical cases grouped (first = the one the solver runs on), order kept. Only cases that
    share the cheap (contract, artifact sizes) pre-key are hashed in full (a fresh Stop-gate process re-hashes)."""
    if not CASE_DEDUPE:
        return [[c] for c in cases]
    pre = {}
    for c in cases:
        pre.setdefault(case_key(c, full=False) or f"\0{c}", []).append(c)
    full = {}
    for k, cs in pre.items():
        for c in cs:
            full[c] = (case_key(c) if len(cs) > 1 else None) or f"\0{c}"
    groups, by = [], {}
    for c in cases:
        k = full[c]
        if k in by:
            by[k].append(c)
        else:
            by[k] = [c]
            groups.append(by[k])
    return groups


def gate_ok(r):
    """Does one test_solver result pass the Stop gate? `ok`, or (GATE_REJECT_FREE) an unverified case that is
    reject-free, or an unverified duplicate (`dup_of`) of a verified case that passes (its result carries `gate_ok`)."""
    if "gate_ok" in r:
        return bool(r["gate_ok"])
    return bool(r.get("ok")) or bool(GATE_REJECT_FREE and r.get("unverified") and r.get("reject_free"))


def _mem_avail_gb():
    try:
        for ln in open("/proc/meminfo"):
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1]) / 1048576
    except (OSError, ValueError, IndexError):
        pass
    return None


# GB of MemAvailable per parallel case: D16 post-run, 8 cases x a solver's own fork pool (~195 MB per process) OOM'd
# WSL. Background runs are single-process (procgov), foreground ones may fork.
CASE_MEM_GB = float(os.environ.get("HCTF_CASE_MEM_GB", "1.25"))


def case_parallel(cap=8):
    """Parallel case runs this box can afford right now: min(cap, cpus, MemAvailable / HCTF_CASE_MEM_GB), >= 1."""
    n = min(cap, os.cpu_count() or 4)
    gb = _mem_avail_gb()
    if gb is not None:
        n = min(n, int(gb / CASE_MEM_GB))
    return max(1, n)


# ---------------------------------------------------------------------------------------------- id()-keyed caches
# D25 binary Mastery (46 fields wrong on the first try): module caches keyed on id(member bytes). A pool worker on the
# 2-vCPU Homebase solves several sets in turn; a freed member's address comes back as the NEXT set's member, which then
# reads the earlier set's cached facts. Invisible on 12 local cores (one set per process) and in background replays
# (single process). Static check: a lookup keyed on id(...) in a container that outlives the call (module global or an
# attribute) is unsafe unless the same function verifies identity with `is` (cache entry = (obj, value)).
ID_CACHE_CHECK = os.environ.get("HCTF_ID_CACHE_CHECK", "1") != "0"
ID_CACHE_OK = "id-cache-ok"   # line pragma for a reviewed exception


def _has_id_key(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "id":
        return True
    return isinstance(node, ast.Tuple) and any(_has_id_key(e) for e in node.elts)


def id_cache_findings(src, name="solve.py"):
    """[(line, text)] of unsafe id()-keyed cache lookups in Python source `src` (see above). Unparsable -> []."""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return []
    lines = src.splitlines()
    module_names = set()
    for st in tree.body:
        for t in (st.targets if isinstance(st, ast.Assign) else [st.target] if isinstance(st, ast.AnnAssign) else []):
            module_names |= {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}

    def own_nodes(fn):
        """Nodes of `fn`'s own body (nested defs / lambdas are scopes of their own)."""
        todo = list(ast.iter_child_nodes(fn))
        while todo:
            n = todo.pop()
            yield n
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                todo.extend(ast.iter_child_nodes(n))

    out = []
    scopes = [tree] + [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))]
    for fn in scopes:
        nodes = list(own_nodes(fn))
        if any(isinstance(n, ast.Compare) and any(isinstance(o, (ast.Is, ast.IsNot)) for o in n.ops)
               and any(isinstance(x, ast.Subscript) for x in [n.left] + n.comparators) for n in nodes):
            continue   # `entry[0] is obj` in this function: the safe (obj, value) entry
        glob = {x for n in nodes if isinstance(n, ast.Global) for x in n.names}
        local = set() if fn is tree else ({n.id for n in nodes if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
                                          | {a.arg for a in ast.walk(fn.args) if isinstance(a, ast.arg)}) - glob
        for n in nodes:
            box = None
            if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load) and _has_id_key(n.slice):
                box = n.value
            elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("get", "setdefault", "pop")
                  and n.args and _has_id_key(n.args[0])):
                box = n.func.value
            elif (isinstance(n, ast.Compare) and _has_id_key(n.left) and len(n.ops) == 1
                  and isinstance(n.ops[0], (ast.In, ast.NotIn))):
                box = n.comparators[0]
            if box is None:
                continue
            persistent = (isinstance(box, ast.Attribute)
                          or (isinstance(box, ast.Name) and box.id in module_names and box.id not in local))
            ln = lines[n.lineno - 1] if 0 < n.lineno <= len(lines) else ""
            if persistent and ID_CACHE_OK not in ln:
                out.append((n.lineno, ln.strip()))
    return sorted(set(out))


def id_cache_problems(sdir):
    """Problem strings for every unsafe id()-keyed cache lookup in the solver dir's .py files (case generators and
    tests skipped). Reported by the single / generalize stop gate and `hctf solver-test`."""
    if not ID_CACHE_CHECK:
        return []
    probs = []
    for f in sorted(Path(sdir).glob("*.py")):
        if f.name.startswith(("make_", "test_", "gen_")):
            continue
        try:
            src = f.read_text(errors="replace")
        except OSError:
            continue
        if "id(" not in src:
            continue
        for ln, text in id_cache_findings(src, f.name):
            probs.append(f"{f.name}:{ln}: cache keyed on a bare id() -- `{text[:90]}`: a Mastery pool process solves "
                         "several sets and a freed object's id() comes back for the next set's object (D25: stale facts "
                         "on 46 fields). Store (obj, value) and check `entry[0] is obj`, or key on content, or clear the "
                         "cache at the start of each set's solve")
    return probs


# Case replays run a multi-set contract on a fork pool of this many processes (lib.solverrt.max_procs via
# HCTF_SOLVER_MAX_PROCS) -- the Homebase VM's 2 vCPUs -- so state leaking from one set into the next fails a case here
# instead of on the GM. 0 = the solver's own default (cpu_count, single-process in background runs).
CASE_MAX_PROCS = int(os.environ.get("HCTF_CASE_MAX_PROCS", "2"))


def _set_count(contract):
    try:
        from lib.common import group_by_set
        ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions") or [] if q.get("id")]
        return len(group_by_set([(a, None) for a in ids]))
    except Exception:  # noqa: BLE001 - the count only decides the pool size
        return 1


def small_pool_env(contract, procs=None):
    """Env overrides for a solver run that must rehearse the 2-vCPU pool: {} for a single-set contract."""
    procs = CASE_MAX_PROCS if procs is None else procs
    if procs <= 0 or _set_count(contract) < 2:
        return {}
    # POOL_REHEARSAL: procgov keeps this run's pool even in the background class (which is otherwise single-process)
    return {"HCTF_SOLVER_PARALLEL": "1", "HCTF_SOLVER_MAX_PROCS": str(procs), "HCTF_SOLVER_POOL_REHEARSAL": "1"}


def test_solver(sdir, timeout=120, parallel=None, cases=None):
    """Run the solver on every case (cases in parallel: they are independent; replay run 2 spent 141s replaying a
    slow solver's cases one by one). Returns list of {case, ok, seconds, diff/error}, in case-name order.
    Also verified_n (GM-verified fields), rejected_hits (GM-rejected values produced again, gm_feedback.json) and
    fully_verified (every asked field has a verified answer).
    `cases`: only case names matching any of these names / fnmatch globs (None = all) -- the generalize watchers and
    `hctf solver-test --case` test the target cases first instead of the whole corpus on every edit.
    A multi-set case runs on a CASE_MAX_PROCS (2) fork pool, background or not: cross-set state leaks show here."""
    from . import procgov

    from . import webtarget
    lane = _lane_of(sdir)

    def judge(case, contract, got, err, dt):
        """One case's verdict on a solver output (shared by every byte-identical case: CASE_DEDUPE)."""
        expected = json.loads((case / "expected.json").read_text()) if (case / "expected.json").exists() else {}
        diff = {k: {"expected": v, "got": got.get(k)} for k, v in expected.items() if got.get(k) != v}
        ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions") or [] if q.get("id")]
        answered = sum(1 for i in ids if got.get(i) not in (None, ""))
        ok = not err and not diff and bool(expected)
        fb = {}
        if VERIFIED_GREEN and (case / "gm_feedback.json").exists():
            try:
                fb = json.loads((case / "gm_feedback.json").read_text())
            except (OSError, ValueError):
                fb = {}
        rejected = fb.get("rejected") or {}
        hits = {a: got.get(a) for a, vals in rejected.items() if got.get(a) not in (None, "") and got.get(a) in vals}
        if fb:
            ok = ok and not hits and (answered == len(ids) or not fb.get("require_complete"))
        return {"case": case.name, "ok": ok, "seconds": round(dt, 2),
                "error": err, "diff": diff, "unverified": not expected,
                "answered": answered, "total": len(ids),
                "verified_n": len(expected), "rejected_hits": len(hits), "rejected_got": hits,
                "rejected_n": sum(len(v or []) for v in rejected.values()),
                # C2: every field answered, no GM-rejected value reproduced, no verified field wrong, no error
                "reject_free": bool(ids) and not err and not diff and not hits and answered == len(ids),
                "fully_verified": bool(ids) and set(ids) <= set(expected)}

    def group(members):
        """Run the solver once on the first case of a group of byte-identical cases; judge every member."""
        case = members[0]
        contract = json.loads((case / "contract.json").read_text())
        if webtarget.case_stale(case, sdir, lane):
            # a FINISHED live-target (web) attempt: its target answers 410 now -- nothing to replay. Counted as
            # passing (it can't break) and marked, so no gate fails a GM-confirmed web solver on it.
            out = []
            for c in members:
                exp = json.loads((c / "expected.json").read_text()) if (c / "expected.json").exists() else {}
                ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions") or [] if q.get("id")]
                out.append({"case": c.name, "ok": True, "seconds": 0.0, "error": None, "diff": {}, "unverified": not exp,
                            "answered": len(ids), "total": len(ids), "verified_n": len(exp), "rejected_hits": 0,
                            "rejected_got": {}, "rejected_n": 0, "reject_free": True, "fully_verified": False,
                            "skipped": "live_target_finished"})
            return out
        got, err, dt = run_solver(Path(sdir), contract, case / "artifacts", timeout, env_extra=small_pool_env(contract))
        out = [judge(c, contract, got, err, dt) for c in members]
        if len(out) > 1:
            # an unverified duplicate of a VERIFIED case (an old variant-mastery-X beside auto-mastery-X): the gate
            # follows the verified twin (same solver output, GM-checked answers) -- C1
            ver = [r for r in out if not r["unverified"]]
            for r in out:
                if r["unverified"] and ver:
                    r["dup_of"] = ver[0]["case"]
                    r["gate_ok"] = bool(ver[0]["ok"]) or bool(GATE_REJECT_FREE and r["reject_free"])
        return out

    pats = list(cases) if cases is not None else None
    cases = sorted((Path(sdir) / "cases").glob("*/"))
    if pats is not None:
        import fnmatch
        cases = [c for c in cases if any(fnmatch.fnmatchcase(c.name, p) for p in pats)]
    # a case dir still being written (record_timed_case / add_case mid-copy) has no contract.json yet: D26's async
    # baselines failed whole on one (FileNotFoundError) -- skip it; the next run sees it complete
    cases = [c for c in cases if (c / "contract.json").exists()]
    groups = _dedupe_groups(cases)
    if parallel is None:
        parallel = case_parallel()
    with procgov.Executor(max_workers=max(1, parallel)) as ex:   # the caller's background flag flows into each run
        res = [r for rs in ex.map(group, groups) for r in rs]
    return sorted(res, key=lambda r: r["case"])


# ---------------------------------------------------------------------------------------------- merged reuse
# Day 6 review: reuse matched solvers by QUESTION TEXT (one arbitrary solver per question, unsorted glob) and was
# all-or-nothing, so it discarded prior solvers that already produced the right answers -- every prior mobile solver
# answered Day 6 mobile; Day 5's script solver got 357/399 and prior binary solvers 40/48, all with 0 wrong. Now every
# same-lane solver runs on the FULL contract and the answers merge per field; the GM (untimed single) is the oracle.

def _lane_of(sdir):
    try:
        return json.loads((Path(sdir).parent / "meta.json").read_text()).get("lane")
    except (OSError, ValueError):
        return None


# Hand-made cases (synthetic-*) were never judged by the GM: their expected.json is OUR belief, not a verification
# (hctf/compound.py VERIFIED_PREFIXES excludes them too). HCTF_KNOWN_NO_SYNTHETIC=0 = the old behaviour (counted).
KNOWN_NO_SYNTHETIC = os.environ.get("HCTF_KNOWN_NO_SYNTHETIC", "1") != "0"
# GM-captured case prefixes; D1 metadata used the pre-`auto-` names `mastery-<att>` / `time_trial-<att>`.
LANE_VERIFIED_PREFIXES = ("single_solve", "auto-mastery-", "auto-time_trial-", "variant-mastery-", "variant-time_trial-",
                          "mastery-", "time_trial-")


def _known_ids(sdir):
    """answer_ids this solver has GM-verified answers for in its own regression cases (confidence signal).
    For a LANE solver (challenges/_lane/<lane>/solver): the (fmt, field) keys of every GM-verified case of that lane
    on every day (see _lane_known_fields) -- its own dir has no cases."""
    if _day_key(sdir) == LANE_DAY_KEY:
        return _lane_known_fields(_lane_of(sdir))
    known = set()
    for exp in Path(sdir).glob("cases/*/expected.json"):
        if KNOWN_NO_SYNTHETIC and exp.parent.name.startswith("synthetic-"):
            continue
        try:
            known.update(json.loads(exp.read_text()))
        except (OSError, ValueError):
            pass
    return known


def _field_key(aid, q):
    """Day-independent key of one answer id: lib.meta's (fmt, field) -- `d09-pe-003-...` on D10 and D11 = the same
    field as Day 9's `d09-pe-001-...`. None for a lane without a field grammar."""
    try:
        from lib import meta
    except ImportError:
        return None
    f = meta.parse_field(aid, q)
    return (f.fmt, f.field) if f else None


def _lane_known_fields(lane):
    """{(fmt, field)} with a GM-verified answer in any regression case of `lane` (GM-captured case names only:
    LANE_VERIFIED_PREFIXES; days >= HCTF_META_MAX_DAY are skipped for fair runs)."""
    if lane != "metadata-forensics":
        return set()
    try:
        cap = int(os.environ.get("HCTF_META_MAX_DAY", "0"))
    except ValueError:
        cap = 0
    known = set()
    for sdir in all_solver_dirs():
        if _lane_of(sdir) != lane or (cap and _day_key(sdir) >= cap):
            continue
        for exp in sdir.glob("cases/*/expected.json"):
            if not exp.parent.name.startswith(LANE_VERIFIED_PREFIXES):
                continue
            try:
                expected = json.loads(exp.read_text())
                contract = json.loads((exp.parent / "contract.json").read_text())
            except (OSError, ValueError):
                continue
            qs = dict(paired_questions(contract))
            for aid in expected:
                k = _field_key(aid, qs.get(aid) or {})
                if k:
                    known.add(k)
    return known


def reuse_plan(contract, artifacts, lane, exclude=(), timeout=60, max_parallel=6, limit=None, by_question=True,
               rank=None):
    """Run every solver of `lane` (+ any question-text match) on the FULL contract, in parallel, and merge per field.
    Returns {"high": {aid: v}, "spec": {aid: v}, "source": {aid: sdir}, "runs": {sdir: (n_answered, err, secs)},
             "best": sdir|None}. high = some solver whose own GM-verified cases contain that answer_id produced it
    (newest such solver wins); spec = produced only by solvers that never had that field verified."""
    from concurrent.futures import ThreadPoolExecutor
    ids = list(contract.get("answer_ids") or [])
    cands, lane_dirs = reuse_cands(lane, exclude, limit, rank, contract if by_question else None)
    if not cands or not ids:
        return {"high": {}, "spec": {}, "source": {}, "runs": {}, "best": None, "alts": {}, "outs": {}}
    with ThreadPoolExecutor(max_workers=max_parallel) as ex:
        outs = dict(zip(cands, ex.map(lambda s: run_solver(s, contract, artifacts, timeout), cands)))
    return reuse_merge(contract, cands, lane_dirs, outs)


def reuse_cands(lane, exclude=(), limit=None, rank=None, question_contract=None):
    """reuse_plan's solver choice -> (candidate dirs newest-first with the lane solver(s) first, the lane solver dirs).
    Needs no bytes (the in-network race picks + pushes them before the single's download lands); question_contract:
    also every solver whose cases match its question texts (by_question)."""
    excl = {Path(e).resolve() for e in exclude}
    lane_dirs = [d for d in lane_solver_dirs(lane) if Path(d).resolve() not in excl]
    cands = {p for p in all_solver_dirs() if _lane_of(p) == lane}
    if question_contract is not None:   # the question-text index is pure-Python over every solver's cases: ~2 s idle, 18-24 s at a drop
        try:
            cands |= set(dispatch(question_contract)[0])
        except Exception:  # noqa: BLE001 - question index is optional here
            pass
    cands = sorted((c for c in cands if Path(c).resolve() not in excl), key=_day_key, reverse=True)
    if limit and rank and len(cands) > limit:
        # rank = {solver dir: similarity} (hctf/retrieval.py): the newest solver always runs (a cumulative lane's
        # latest already covers the earlier families); the other slots go to the most similar past challenges.
        # Merge precedence below stays newest-first.
        rest = sorted(cands[1:], key=lambda c: (rank.get(Path(c).resolve(), 0.0), _day_key(c)), reverse=True)
        cands = sorted([cands[0]] + rest[:limit - 1], key=_day_key, reverse=True)
    elif limit:
        cands = cands[:limit]   # newest first: a cumulative lane's latest solver already covers the earlier families
    return lane_dirs + [c for c in cands if c not in lane_dirs], lane_dirs   # the lane solver first, never sliced away


def reuse_merge(contract, cands, lane_dirs, outs):
    """reuse_plan's per-field merge of every candidate's (answers, err, secs) in `outs` (run locally, or on Homebase by
    the in-network race) -> the reuse_plan dict."""
    ids = list(contract.get("answer_ids") or [])
    if not cands or not ids:
        return {"high": {}, "spec": {}, "source": {}, "runs": {}, "best": None, "alts": {}, "outs": {}}
    outs = {c: outs.get(c) or ({}, "not run", 0.0) for c in cands}
    high, spec, source, runs, alts = {}, {}, {}, {}, {}
    qs = dict(paired_questions(contract)) if lane_dirs else {}
    for sdir in cands:                      # newest first: the first producer of a field wins
        got, err, dt = outs[sdir]
        runs[sdir] = (sum(1 for a in ids if got.get(a) not in (None, "")), err, round(dt, 2))
        known = _known_ids(sdir)
        is_lane = sdir in lane_dirs
        for a in ids:
            v = got.get(a)
            if v in (None, ""):
                continue
            if v not in alts.setdefault(a, []):
                alts[a].append(v)           # every distinct candidate, newest first (fallbacks for a judged-wrong field)
            if (_field_key(a, qs.get(a) or {}) in known if is_lane else a in known) and a not in high:
                high[a], source[a] = v, sdir
                spec.pop(a, None)
            elif a not in high and a not in spec:
                spec[a], source[a] = v, sdir
    merged = {**spec, **high}
    # The seed for this challenge's own solver: the one reproducing the most merged values (ties -> newest).
    def agree(sdir):
        got = outs[sdir][0]
        return sum(1 for a, v in merged.items() if got.get(a) == v), _day_key(sdir)
    best = max(cands, key=agree) if merged else None
    # outs: every solver's raw (answers, err, secs) -- the race verifies its seed from this run, no re-run (D24 #6)
    return {"high": high, "spec": spec, "source": source, "runs": runs, "best": best, "alts": alts, "outs": outs}


def lane_race_plan(sdir, contract, artifacts, deadline, timeout=None):
    """ONE lane-solver run as a reuse_plan()-shaped result (D24 #9, web): challenges/_lane/web/solver already races every
    plugin, the `default` ladder and every earlier web day's answer() (`prior:` probes) in one process, so running the
    newest dated web solvers beside it only re-ran the same race 3x against one live target. Its live-exploited proofs
    count as confident (`high`), as a prior web solver's were (proof-* is in every web solver's cases)."""
    ids = list(contract.get("answer_ids") or [])
    got, err, dt = run_solver(Path(sdir), contract, artifacts, timeout=timeout or float(deadline) + 4, deadline=deadline)
    high = {a: got[a] for a in ids if got.get(a) not in (None, "")}
    return {"high": high, "spec": {}, "source": {a: Path(sdir) for a in high},
            "runs": {Path(sdir): (len(high), err, round(dt, 2))}, "best": Path(sdir) if high else None,
            "alts": {a: [v] for a, v in high.items()}, "outs": {Path(sdir): (got, err, dt)}}
