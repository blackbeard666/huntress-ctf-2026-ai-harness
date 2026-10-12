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
import difflib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from .paths import ROOT, TMP, VENV_PY, all_solver_dirs, base_id, mode_of, solver_dir  # noqa: F401 (re-exported)


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


def paired_questions(contract):
    """[(answer_id, question)]: exact question id, else the question id the answer id ends with (bundles like
    answer_ids slot0_marker..slot3_marker sharing one 'marker' question), else by position."""
    ids, qs = contract.get("answer_ids", []), contract.get("questions", [])
    out = []
    for i, aid in enumerate(ids):
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


def run_solver(sdir, contract, artifacts, timeout=120):
    """Run one solver. Returns (answers dict, error string or None, seconds)."""
    if not (Path(sdir) / "solve.py").exists():
        return {}, f"no solver yet at {Path(sdir).relative_to(ROOT)}/solve.py", 0.0
    tmp = TMP / f"contract-{sdir.parent.name}-{time.time_ns()}.json"
    tmp.write_text(json.dumps(contract))
    py = str(VENV_PY) if VENV_PY.exists() else "python3"
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"  # solvers can `import lib.*`
    t0 = time.time()
    try:
        r = subprocess.run([py, str(sdir / "solve.py"), "--contract", str(tmp), "--artifacts", str(artifacts)],
                           capture_output=True, text=True, timeout=timeout, cwd=sdir, env=env)
    except subprocess.TimeoutExpired:
        return {}, f"timeout after {timeout}s", time.time() - t0
    finally:
        tmp.unlink(missing_ok=True)
    dt = time.time() - t0
    if r.returncode:
        return {}, f"exit {r.returncode}: {r.stderr.strip()[-1500:]}", dt
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
        return {k: str(v) for k, v in out.items()}, None, dt
    except (IndexError, ValueError):
        return {}, f"stdout is not JSON: {r.stdout[-500:]!r} stderr: {r.stderr[-800:]}", dt


def dry_run_diagnostics(sdir, contract, artifacts, timeout=15, known=None, shape=None):
    """Run an EARLIER day's solver once on TODAY's contract + bytes and return DIAGNOSTICS ONLY -- never its values
    (user rule: old solvers are not an answer source). On a timeout it gets SIGINT first, so the traceback names the
    loop that hangs. Rehearsal D8: the copied Day 7 binary solver hung twice to the worker's 60 s cap on a 67 MB Swift ELF
    (~140 s of the single) before the worker found the slow path. Returns a dict (see render_dry_run)."""
    import signal
    tmp = TMP / f"dryrun-{Path(sdir).parent.name}-{time.time_ns()}.json"
    tmp.write_text(json.dumps(contract))
    py = str(VENV_PY) if VENV_PY.exists() else "python3"
    env = dict(os.environ, PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}")
    t0 = time.time()
    p = subprocess.Popen([py, str(Path(sdir) / "solve.py"), "--contract", str(tmp), "--artifacts", str(artifacts)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=sdir, env=env,
                         start_new_session=True)
    timed_out = False
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        p.send_signal(signal.SIGINT)              # KeyboardInterrupt -> a traceback at the hot loop
        try:
            out, err = p.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
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
    return {"solver": str(Path(sdir).relative_to(ROOT)), "seconds": round(dt, 1), "timed_out": timed_out,
            "rc": p.returncode, "frames": frames, "error": last[:200] if (p.returncode and not timed_out) else "",
            "warnings": warn[:8], "answered": len(ids) - len(empty), "total": len(ids), "empty": empty[:15],
            "empty_q": empty_q, "new": len(new), "new_by_art": new_by_art}


EMPTY_Q_MAX = 6   # dry-run render: full question text for this many empty ids (a 1-5 field delta is the usual day)
NEW_GROUPS_MAX = 10  # dry-run render: artifact groups of NEW-today ids listed


def profile_solver(sdir, case_dir, timeout=45, top=25):
    """cProfile of solve.py on one regression case -> the top `top` rows by cumulative time (text), or ''. Handed to a
    speed generalize so the worker starts at the hot path (rehearsal D8 + d8tc1: both speed workers lost a turn to a profile
    piped to /dev/null)."""
    case_dir = Path(case_dir)
    if not (case_dir / "contract.json").exists():
        return ""
    py = str(VENV_PY) if VENV_PY.exists() else "python3"
    env = dict(os.environ, PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}")
    try:
        r = subprocess.run([py, "-m", "cProfile", "-s", "cumtime", str(Path(sdir) / "solve.py"), "--contract",
                            str(case_dir / "contract.json"), "--artifacts", str(case_dir / "artifacts")],
                           capture_output=True, text=True, timeout=timeout, cwd=sdir, env=env)
    except subprocess.TimeoutExpired:
        return f"(profile of {case_dir.name} did not finish in {timeout}s)"
    out = r.stdout.splitlines()
    i = next((k for k, ln in enumerate(out) if ln.strip().startswith("ncalls")), None)
    if i is None:
        return ""
    head = next((ln.strip() for ln in out if "function calls" in ln), "")
    rows = [re.sub(r"/[^\s]*/(site-packages|huntress-2026[^/]*)/", r"\1/", ln.rstrip()) for ln in out[i:i + top + 1]]
    return f"cProfile of `cases/{case_dir.name}` ({head}):\n" + "\n".join(rows)


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
    m = re.search(r"day(\d+)", str(sdir))
    return int(m.group(1)) if m else -1


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
    for f in Path(artifacts).iterdir():
        if f.is_file() and f.name not in ("manifest.json", "contract.json", "result.json"):
            shutil.copy2(f, case / "artifacts" / f.name)
    (case / "contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False))
    (case / "expected.json").write_text(json.dumps(expected, indent=2, ensure_ascii=False))
    return case


def test_solver(sdir, timeout=120, parallel=min(8, os.cpu_count() or 4)):
    """Run the solver on every case (cases in parallel: they are independent; replay run 2 spent 141s replaying a
    slow solver's cases one by one). Returns list of {case, ok, seconds, diff/error}, in case-name order."""
    from concurrent.futures import ThreadPoolExecutor

    def one(case):
        contract = json.loads((case / "contract.json").read_text())
        expected = json.loads((case / "expected.json").read_text()) if (case / "expected.json").exists() else {}
        got, err, dt = run_solver(Path(sdir), contract, case / "artifacts", timeout)
        diff = {k: {"expected": v, "got": got.get(k)} for k, v in expected.items() if got.get(k) != v}
        ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions") or [] if q.get("id")]
        return {"case": case.name, "ok": not err and not diff and bool(expected), "seconds": round(dt, 2),
                "error": err, "diff": diff, "unverified": not expected,
                "answered": sum(1 for i in ids if got.get(i) not in (None, "")), "total": len(ids)}
    cases = sorted((Path(sdir) / "cases").glob("*/"))
    with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
        return list(ex.map(one, cases))


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


def _known_ids(sdir):
    """answer_ids this solver has GM-verified answers for in its own regression cases (confidence signal)."""
    known = set()
    for exp in Path(sdir).glob("cases/*/expected.json"):
        try:
            known.update(json.loads(exp.read_text()))
        except (OSError, ValueError):
            pass
    return known


def reuse_plan(contract, artifacts, lane, exclude=(), timeout=60, max_parallel=6):
    """Run every solver of `lane` (+ any question-text match) on the FULL contract, in parallel, and merge per field.
    Returns {"high": {aid: v}, "spec": {aid: v}, "source": {aid: sdir}, "runs": {sdir: (n_answered, err, secs)},
             "best": sdir|None}. high = some solver whose own GM-verified cases contain that answer_id produced it
    (newest such solver wins); spec = produced only by solvers that never had that field verified."""
    from concurrent.futures import ThreadPoolExecutor
    ids = list(contract.get("answer_ids") or [])
    excl = {Path(e).resolve() for e in exclude}
    cands = {p for p in all_solver_dirs() if _lane_of(p) == lane}
    try:
        cands |= set(dispatch(contract)[0])
    except Exception:  # noqa: BLE001 - question index is optional here
        pass
    cands = sorted((c for c in cands if Path(c).resolve() not in excl), key=_day_key, reverse=True)
    if not cands or not ids:
        return {"high": {}, "spec": {}, "source": {}, "runs": {}, "best": None, "alts": {}}
    with ThreadPoolExecutor(max_workers=max_parallel) as ex:
        outs = dict(zip(cands, ex.map(lambda s: run_solver(s, contract, artifacts, timeout), cands)))
    high, spec, source, runs, alts = {}, {}, {}, {}, {}
    for sdir in cands:                      # newest first: the first producer of a field wins
        got, err, dt = outs[sdir]
        runs[sdir] = (sum(1 for a in ids if got.get(a) not in (None, "")), err, round(dt, 2))
        known = _known_ids(sdir)
        for a in ids:
            v = got.get(a)
            if v in (None, ""):
                continue
            if v not in alts.setdefault(a, []):
                alts[a].append(v)           # every distinct candidate, newest first (fallbacks for a judged-wrong field)
            if a in known and a not in high:
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
    return {"high": high, "spec": spec, "source": source, "runs": runs, "best": best, "alts": alts}
