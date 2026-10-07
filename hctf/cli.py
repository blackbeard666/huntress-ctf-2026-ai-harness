"""hctf: local Game Master CLI. Every GM call goes through Homebase (see remote.py).

State for each challenge mode lives in challenges/dayNN/<lane>-<title>/<mode>/ (see paths.py):
  log.jsonl            every GM envelope, timestamped
  start.json           latest start/retry body (questions, answer_ids, deadline, ...)
  contract.json        latest questions contract (also fetched for timed modes before they start)
  status.json          latest status body
  artifacts/<ts>/      downloaded bytes + manifest.json (sha256); artifacts/latest -> newest
  submissions.jsonl    one line per submit: attempt, answers, result
  confirmed.json       answers the GM confirmed, per attempt

Exit codes: 0 correct/ok, 1 incorrect, 2 accepted (partial), 3 expired, 4 refused locally,
            5 Homebase/GM unreachable, 6 GM conflict (409) or other HTTP error.
"""
import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path

from . import paths, remote
from .paths import ROOT

# Wrong-answer budgets. Per-field probing lets the harness resolve the GM's exact wording for structured,
# non-flag fields on its own; flags are brute-force-protected; a global ceiling stops runaway.
MAX_WRONG_PER_ATTEMPT = int(os.environ.get("HCTF_MAX_WRONG", "6"))   # per non-flag answer_id
FLAG_WRONG_CAP = int(os.environ.get("HCTF_FLAG_WRONG_CAP", "3"))     # wrong flag guesses per attempt
GLOBAL_WRONG_CAP = int(os.environ.get("HCTF_GLOBAL_WRONG_CAP", "80"))  # total wrong per attempt (sanity)
FLAG_RE = re.compile(r"^[0-9a-f]{32}$")
EXIT = {"correct": 0, "incorrect": 1, "accepted": 2, "expired": 3, "refused": 4, "unreachable": 5, "error": 6}


def cdir(cid):
    return paths.mode_dir(cid)


def now():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def log(cid, op, env):
    target = cdir(cid) / "log.jsonl" if cid else paths.LOGS / "gm.jsonl"
    with open(target, "a") as f:
        f.write(json.dumps({"ts": now(), "op": op, **env}, ensure_ascii=False) + "\n")


def load(cid, name):
    p = cdir(cid) / name
    return json.loads(p.read_text()) if p.exists() else None


def load_json(path):
    """Best-effort JSON from an absolute path (for read-only diagnostics like `hctf why`)."""
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def save(cid, name, obj):
    (cdir(cid) / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False))


@contextmanager
def chal_lock(cid):
    """Only one process may start/submit/retry a given challenge at a time."""
    with open(paths.LOCKS / ("chal-" + paths.slugify(cid) + ".lock"), "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def attempt_id(body):
    """Best-effort attempt identifier from a start/status body."""
    if not isinstance(body, dict):
        return None
    for k in ("attempt_id", "attempt", "attemptId"):
        v = body.get(k)
        if isinstance(v, dict):
            v = v.get("id")
        if v:
            return str(v)
    return None


def result_kind(body):
    r = str((body or {}).get("result", "")).lower()
    if r == "correct":
        return "correct"
    if r in ("incorrect", "accepted", "expired"):
        return r
    return None


def call(cid, op, *args, timeout=180):
    env = remote.gm(op, *args, timeout=timeout)
    log(cid, op, env)
    if op == "list" and isinstance(env.get("body"), dict):
        paths.register(env["body"].get("challenges", []))
    return env


_tls = threading.local()


@contextmanager
def quiet():
    """Silence emit() for the CALLING thread only. (contextlib.redirect_stdout swaps the process-global sys.stdout:
    with 5 chains in parallel, two overlapping redirects restored out of order and left sys.stdout stuck on a
    StringIO, so every later orchestrator line vanished from .run/dayNN.log -- Day 6.)"""
    prev = getattr(_tls, "quiet", False)
    _tls.quiet = True
    try:
        yield
    finally:
        _tls.quiet = prev


def emit(obj):
    if getattr(_tls, "quiet", False):
        return
    json.dump(obj, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def http_exit(env):
    return 0 if env["http"] == 200 else (EXIT["error"])


# ---------------------------------------------------------------- commands

def c_hb(a):
    if a.action == "setup":
        # Provision Homebase so solvers run next to the GM (hb_timed). Idempotent.
        remote.rsync_to(ROOT / "setup" / "homebase_setup.sh", "~/homebase_setup.sh")
        r = remote.ssh("bash ~/homebase_setup.sh", timeout=600, check=False)
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        return 0 if r.returncode == 0 else EXIT["error"]
    if a.action == "exec":
        # Run a command ON Homebase (inside the CTF network), e.g. to reach a live challenge backend.
        cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
        if not cmd:
            print("usage: hctf hb exec [--timeout N] -- <command ...>", file=sys.stderr)
            return EXIT["refused"]
        r = remote.ssh(" ".join(cmd), timeout=a.timeout, check=False)
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        return r.returncode
    if a.action == "deploy":
        remote.deploy()
        emit({"deployed": True})
    elif a.action == "ensure":
        emit(remote.ensure_up())
    else:
        emit(remote.power(a.action))
    return 0


def c_list(a):
    args = ["list"]
    if a.day is not None:
        args += ["--day", a.day]
    if a.lane:
        args += ["--lane", a.lane]
    if a.all:
        args.append("--all")
    env = call(None, *args)
    body = env["body"] or {}
    if a.json:
        emit(body)
    else:
        if body.get("message"):
            print(f"# {body['message']}")
        for c in body.get("challenges", []):
            print(f"D{c.get('day'):>02} {c.get('lane', ''):<28} {c.get('mode', ''):<13} {c.get('id')}  |  {c.get('name')}")
    return http_exit(env)


def c_status(a):
    env = call(a.id, "status", a.id)
    if env["body"] is not None:
        save(a.id, "status.json", env["body"])
        if env["body"].get("questions"):
            # The questions contract comes back even before a start (409 start_required), so solvers
            # can be written for Time Trial / Mastery without starting a clock.
            save(a.id, "contract.json", env["body"])
    emit(env["body"] if env["body"] is not None else env)
    return http_exit(env) if env["http"] != 409 else EXIT["error"]


def c_start(a, op="start"):
    with chal_lock(a.id):
        env = call(a.id, op, a.id)
    # An after-deadline start answers 200 {"result": "expired"} with no attempt_id/answer_ids; saving that would
    # clobber the last real contract (lost the Mastery 6279ad62 case and broke solver-run).
    if env["body"] is not None and env["http"] == 200 and attempt_id(env["body"]):
        save(a.id, "start.json", env["body"])
        save(a.id, "contract.json", env["body"])
    emit(env["body"] if env["body"] is not None else env)
    return http_exit(env)


def c_retry(a):
    st = load(a.id, "status.json") or {}
    if not a.force and "expired" not in json.dumps(st).lower():
        print("refused: retry is only allowed after the GM reports the attempt expired "
              "(run `hctf status` first, or --force)", file=sys.stderr)
        return EXIT["refused"]
    return c_start(a, op="retry")


def _planned_downloads(body):
    """From a start/status body, the deliverable files to fetch as (filename, capability, sha256).

    The GM delivers a handful of real files (one per set), but many questions may reference them, and
    questions[i].artifact is often a 'container.zip -> member' path. So pair the UNIQUE capabilities
    (from artifacts[]/downloads[]/download) with the UNIQUE container names from the questions, by order.
    Each file is saved under its container name; the solver resolves the '-> member' part itself."""
    cap_re = re.compile(r"(?:/download/|[?&]capability=)([0-9a-f]{64})")  # Homebase proxy or public GM

    def cap_of(x):
        s = x.get("download", "") if isinstance(x, dict) else str(x)
        m = cap_re.search(s)
        return m.group(1) if m else None

    # unique capabilities, in order, with any sha the body gives for them
    caps, sha_of = [], {}
    arts = body.get("artifacts")
    sources = arts if isinstance(arts, list) and arts else (body.get("downloads") or
              ([body["download"]] if body.get("download") else []))
    for x in sources:
        c = cap_of(x)
        if c and c not in caps:
            caps.append(c)
            if isinstance(x, dict) and x.get("sha256"):
                sha_of[c] = x["sha256"]
    if isinstance(arts, list):
        for x in arts:
            c = cap_of(x)
            if c and isinstance(x, dict) and x.get("sha256"):
                sha_of.setdefault(c, x["sha256"])
    if not caps:
        return []

    # unique container names, in order of first appearance in the questions
    containers = []
    for q in body.get("questions") or []:
        art = q.get("artifact")
        if not art:
            continue
        name = os.path.basename(art.split("->")[0].strip())
        if name and name not in containers:
            containers.append(name)

    out = []
    for i, cap in enumerate(caps):
        name = containers[i] if i < len(containers) else f"artifact-{i}.bin"
        out.append((name, cap, sha_of.get(cap)))
    return out


def c_artifact(a):
    """Download every assigned artifact on Homebase and rsync them into the mode dir artifacts/<ts>/,
    each named by its logical contract name (so Mastery's per-set blobs don't collide)."""
    body = load(a.id, "start.json") or load(a.id, "contract.json") or {}
    plan = _planned_downloads(body)
    if not plan:
        # No capability list (e.g. challenge with no artifact): fall back to the artifact op.
        env = call(a.id, "artifact", a.id, f"{remote.HB_DIR}/dl/probe", timeout=120)
        emit(env["body"] if env["body"] is not None else env)
        return http_exit(env) or EXIT["error"]
    ts = now()
    local = cdir(a.id) / "artifacts" / ts
    # Local transport: gm.py runs here, so save straight into the mode dir (no Homebase round trip).
    on_here = remote.gm_transport() == "local"
    rdir = str(local) if on_here else f"{remote.HB_DIR}/dl/{paths.slugify(a.id)}/{ts}"
    saved = []
    # Parallel downloads (8 at a time): a 28-set warmups Mastery fetched sequentially took ~61s (replay run 2).
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as ex:
        envs = list(ex.map(lambda item: call(a.id, "download", item[1], rdir, "--name", item[0], timeout=600), plan))
    for (name, cap, sha), env in zip(plan, envs):
        if not env["saved"]:
            emit(env["body"] if env["body"] is not None else env)
            return http_exit(env) or EXIT["error"]
        s = env["saved"][0]
        if sha and s["sha256"] != sha:
            raise RuntimeError(f"sha256 mismatch for {name}: GM said {sha}, got {s['sha256']}")
        saved.append((name, s))
    if not on_here:
        remote.rsync_from(f"~/{rdir}", local)
    manifest = []
    for name, s in saved:
        p = local / name
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if digest != s["sha256"]:
            raise RuntimeError(f"sha256 mismatch after rsync for {p}")
        manifest.append({"file": str(p.relative_to(ROOT)), "name": name, "bytes": s["bytes"], "sha256": digest})
    (local / "manifest.json").write_text(json.dumps(
        {"challenge": a.id, "ts": ts, "attempt": attempt_id(body), "files": manifest}, indent=2))
    latest = cdir(a.id) / "artifacts" / "latest"
    latest.unlink(missing_ok=True)
    latest.symlink_to(ts)
    emit({"dir": str(local.relative_to(ROOT)), "files": manifest})
    return 0


def _questions(start):
    """Map answer_id -> question dict, using the aligned questions/answer_ids arrays."""
    ids = (start or {}).get("answer_ids") or []
    qs = (start or {}).get("questions") or []
    return {aid: (qs[i] if i < len(qs) and isinstance(qs[i], dict) else {}) for i, aid in enumerate(ids)}


def _normalize(value, q):
    """Apply the question's normalization. 'exact' is left untouched; everything else is at least trimmed."""
    norm = (q or {}).get("normalization")
    if norm == "exact":
        return value
    v = value.strip()
    if norm == "case_insensitive":
        v = v.lower()
    return v


def _format_problem(value, q):
    af = q.get("answer_format") if isinstance(q.get("answer_format"), dict) else {}
    if af.get("kind") == "enum" and af.get("accepted_values"):
        allowed = [str(x) for x in af["accepted_values"]]
        v = value.strip()
        if v not in allowed and not (q.get("normalization") == "case_insensitive" and v.lower() in map(str.lower, allowed)):
            return f"not one of the accepted values {allowed}"
    fmt = json.dumps(q.get("answer_format", "")).lower()
    pattern = q.get("pattern") or q.get("regex")
    if isinstance(pattern, str):
        try:
            if not re.fullmatch(pattern, value):
                return f"does not match pattern {pattern!r}"
        except re.error:
            pass
    if ("md5" in fmt or "[0-9a-f]{32}" in fmt or "32 lowercase hex" in fmt) and not FLAG_RE.fullmatch(value):
        return "expected 32 lowercase hex characters"
    if value != value.strip():
        return "leading/trailing whitespace"
    return None


def _bisect_rejected(cid, answers, budget=40):
    """Split an incorrect batch by answer-id family (prefix before the last '-'/'_' field word), then halves, submitting
    each group (probe-tagged); accepted groups are banked. Returns the set of individually rejected answer_ids."""
    def family(aid):
        m = re.match(r"((?:set\d+\.)?[a-z0-9]+(?:[-_][a-z0-9]+)?)", aid)
        return m.group(1) if m else aid
    fams = {}
    for k, v in answers.items():
        fams.setdefault(family(k), {})[k] = v
    todo, bad, n = list(fams.values()), set(), [0]
    while todo and n[0] < budget:
        g = {k: v for k, v in todo.pop(0).items() if k not in confirmed_answers(cid)}
        if not g:
            continue
        n[0] += 1
        kind, _b, _p = submit(cid, g, force=True, probe=True)
        if kind in ("correct", "accepted"):
            continue
        if len(g) == 1:
            bad.update(g)
            continue
        ks = list(g)
        todo[:0] = [{k: g[k] for k in ks[:len(ks) // 2]}, {k: g[k] for k in ks[len(ks) // 2:]}]
    return bad


def _mastery_dry_run(cid):
    """Warn (stderr) if the solver can't even LOCATE/answer Mastery-shaped input: the Mastery contract's own artifact
    names (e.g. 'delivery 2: x.apk', fetched via status before any attempt) with this Single Solve's bytes under each.
    Values aren't checked -- only that every set gets answers. Mastery's real bytes may still differ in format."""
    import shutil
    import tempfile
    from . import solvers, timed
    base = paths.base_id(cid)
    if base != cid:
        return
    mc = load(f"{base}/mastery", "contract.json") or {}
    art = timed.latest_artifacts(cid)
    files = [p for p in (art.iterdir() if art else []) if p.is_file() and p.name != "manifest.json"]
    if not mc.get("questions") or len(files) != 1:
        return
    tmp = Path(tempfile.mkdtemp(prefix="mdry-", dir=str(paths.TMP)))
    try:
        for q in mc["questions"]:
            name = (q.get("artifact") or "").partition("->")[0].strip()
            if name and not (tmp / name).exists():
                shutil.copy2(files[0], tmp / name)
        ids = mc.get("answer_ids") or [q.get("id") for q in mc["questions"] if q.get("id")]
        # names only (no artifacts[]: no sha pairing possible on copies); status-time contracts carry ids on questions
        c = {**{k: v for k, v in mc.items() if k not in ("artifacts", "error")}, "answer_ids": ids}
        got, err, dt = solvers.run_solver(paths.solver_dir(cid), c, tmp, timeout=20)
        sets = {}
        for i in ids:
            sets.setdefault(i.split(".", 1)[0] if "." in i else "_", []).append(i)
        empty = [k for k, v in sets.items() if not any(got.get(i) for i in v)]
        if err or empty:
            print(f"WARNING (Mastery dry run): with the Mastery contract's artifact names "
                  f"({sorted({(q.get('artifact') or '') for q in mc['questions']})[:3]}) your solver answered nothing for "
                  f"{len(empty)}/{len(sets)} set(s){': ' + err[:200] if err else ''}. Mastery runs every set through "
                  "solve.py -- resolve each question's artifact (see the solve.py skeleton's artifact_bytes) before you stop.",
                  file=sys.stderr)
        else:
            print(f"Mastery dry run: all {len(sets)} set(s) answered on Mastery-named copies in {dt:.2f}s", file=sys.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def c_submit(a):
    if a.from_solver:
        # Submit exactly what solve.py emits (minus already-confirmed answers): the solver IS the answer source, so the
        # moment this comes back CORRECT the harness can verify the solver and hand the timed modes off.
        from . import solvers, timed
        contract = load(a.id, "start.json") or load(a.id, "contract.json")
        art = timed.latest_artifacts(a.id)
        if not contract or not art:
            print("refused:\n  no contract/artifacts for this mode yet", file=sys.stderr)
            return EXIT["refused"]
        # THIS challenge's solver only -- never dispatch questions to earlier days' solvers (owner rule).
        got, err, _ = solvers.run_solver(paths.solver_dir(a.id), contract, art)
        if err:
            print(f"refused:\n  your solve.py failed: {err[:600]}", file=sys.stderr)
            return EXIT["refused"]
        conf = confirmed_answers(a.id)
        answers = {k: v for k, v in got.items() if conf.get(k) != v}
        missing = [x for x in contract.get("answer_ids", []) if x not in got]
        if missing:
            print(f"note: solve.py left {len(missing)} answer_id(s) empty: {missing[:15]}", file=sys.stderr)
        if not answers:
            print("refused:\n  the solver produced nothing new to submit", file=sys.stderr)
            return EXIT["refused"]
    else:
        if not a.answers:
            print("refused:\n  give answers JSON or --from-solver", file=sys.stderr)
            return EXIT["refused"]
        answers = json.loads(a.answers)
    kind, body, problems = submit(a.id, answers, force=a.force)
    if a.from_solver and not problems and kind == "incorrect" and len(answers) > 1:
        # A bulk "incorrect" says nothing about WHICH field: bisect (probe-tagged, untimed single) and print the
        # rejected answer_ids, so the worker fixes exactly those (a script worker spent 88 s bisecting by hand).
        bad = _bisect_rejected(a.id, answers)
        print(f"bisect: {len(bad)} answer_id(s) REJECTED by the GM (everything else accepted): {sorted(bad)[:40]}",
              file=sys.stderr)
        kind = "correct" if is_complete(a.id) else ("accepted" if len(bad) < len(answers) else kind)
    if problems:
        print("refused:\n  " + "\n  ".join(problems), file=sys.stderr)
        return EXIT["refused"]
    emit(body)                        # the verdict first: the stop-at-correct watcher may end the worker any moment
    if a.from_solver:
        sys.stdout.flush()
        _mastery_dry_run(a.id)
    return EXIT.get(kind, EXIT["error"])


def submit(cid, answers, force=False, max_wrong=MAX_WRONG_PER_ATTEMPT, global_cap=None, probe=False):
    """Guarded submission shared by the CLI, the workers and the timed runner.
    Returns (kind, body, problems). kind is None when refused locally (problems explains why).
    Answers the GM confirms are merged into <mode dir>/confirmed.json (keyed by attempt)."""
    start = load(cid, "start.json")
    att = attempt_id(start)
    qmap = _questions(start)
    # Auto-apply the GM's stated normalization so a stray space/case never wastes a submission.
    answers = {k: _normalize(str(v), qmap.get(k, {})) for k, v in answers.items()}
    subs_path = cdir(cid) / "submissions.jsonl"
    history = [json.loads(l) for l in subs_path.read_text().splitlines()] if subs_path.exists() else []
    # probe=True submissions (harness reuse/localization batches) prove nothing about any single value when the
    # batch is incorrect, so they never feed the "already judged incorrect" / per-field wrong-count guards.
    same_attempt = [h for h in history if h.get("attempt") == att and not h.get("probe")]
    # Only a SINGLE-field rejection says anything about that one value (probe or not). A rejected multi-field batch
    # only says "something in here is wrong": replays 3-5 had every worker resubmit its fixed 399-field batch, get
    # refused locally ("already judged incorrect" x398), look up --help and resubmit with --force (6-16 s each).
    judged = [h for h in history if h.get("attempt") == att and len(h.get("answers") or {}) == 1]
    confirmed = confirmed_answers(cid, att)

    # Wrong-answer accounting. Flags are brute-force-protected (hard cap across the attempt). Structured
    # non-flag fields (enum spellings, ATT&CK ids, format strings) get a bounded PER-FIELD probe budget so
    # the harness can resolve the GM's exact vocabulary autonomously. A global ceiling stops true runaway.
    from collections import Counter
    field_wrong = Counter()
    flag_wrong = 0
    for h in judged:
        if h.get("kind") != "incorrect":
            continue
        for k, v in h.get("answers", {}).items():
            field_wrong[k] += 1
            if FLAG_RE.fullmatch(str(v)):
                flag_wrong += 1
    total_wrong = sum(1 for h in same_attempt if h.get("kind") == "incorrect")

    problems = []
    if qmap:
        for k in answers:
            if k not in qmap:
                problems.append(f"{k}: not an answer_id of the current attempt {sorted(qmap)}")
    for k, v in answers.items():
        prob = _format_problem(str(v), qmap.get(k, {}))
        if prob:
            problems.append(f"{k}: {prob}")
        for h in judged:
            if h.get("kind") == "incorrect" and h["answers"].get(k) == v:
                problems.append(f"{k}: value {v!r} already judged incorrect in this attempt")
                break
        if FLAG_RE.fullmatch(str(v)):
            if flag_wrong >= FLAG_WRONG_CAP:
                problems.append(f"{k}: {flag_wrong} wrong flag guesses already (cap {FLAG_WRONG_CAP}); do not brute-force flags")
        elif field_wrong[k] >= max_wrong:
            problems.append(f"{k}: {field_wrong[k]} wrong tries for this field (per-field cap {max_wrong}); "
                            "you have exhausted sensible candidates for its exact wording")

    # ATT&CK guard: an id-shaped value ATT&CK doesn't know (or an *-attack field holding a non-id, non-'none'
    # value) is a hallucination/typo the GM will reject, wasting an attempt — refuse it locally. The role tables
    # in lib/knowledge.py supply the correct id; this only catches malformed values. Disable with HCTF_ATTACK_GUARD=0.
    if os.environ.get("HCTF_ATTACK_GUARD", "1") != "0":
        try:
            from lib.refs import attack as _attack
            for aid, val, reason in _attack.validate_answers(answers):
                problems.append(f"{aid}: {reason} ({val!r}) [ATT&CK guard]")
        except Exception:  # noqa: BLE001 - the guard must never itself block a submission
            pass

    gcap = GLOBAL_WRONG_CAP if global_cap is None else global_cap
    if total_wrong >= gcap:
        problems.append(f"{total_wrong} wrong submissions in this attempt (global cap {gcap})")
    if problems and not force:
        return None, None, problems

    with chal_lock(cid):
        env = call(cid, "submit", cid, json.dumps(answers))
    body = env["body"] if env["body"] is not None else env
    kind = result_kind(env["body"]) or ("error" if env["http"] != 200 else "unknown")

    # Which answers does this result prove correct?
    newly = {}
    if kind == "correct":
        newly = dict(answers)
    elif kind == "accepted":
        remaining = (env["body"] or {}).get("remaining")
        before = [h for h in history if h.get("attempt") == att  # incl. probe batches: they move `remaining` too
                  and isinstance((h.get("body") or {}).get("remaining"), int)]
        prev = before[-1]["body"]["remaining"] if before else len(qmap) - len(confirmed) if qmap else None
        if len(answers) == 1 or (isinstance(remaining, int) and prev is not None and prev - remaining == len(answers)):
            newly = dict(answers)
    if newly:
        allc = load(cid, "confirmed.json") or {}
        allc.setdefault(att or "_", {}).update(newly)
        save(cid, "confirmed.json", allc)

    with open(subs_path, "a") as f:
        f.write(json.dumps({"ts": now(), "attempt": att, "answers": answers, "http": env["http"],
                            "kind": kind, "confirmed": sorted(newly), "body": env["body"],
                            **({"probe": True} if probe else {})}, ensure_ascii=False) + "\n")
    return kind, body, []


def record_remote_result(cid, att, answers, kind, body=None):
    """Record a submission made ON Homebase (by hb_timed) into local state, so is_complete/dash are accurate."""
    att = att or attempt_id(load(cid, "start.json"))
    with open(cdir(cid) / "submissions.jsonl", "a") as f:
        f.write(json.dumps({"ts": now(), "attempt": att, "answers": answers, "http": 200,
                            "kind": kind, "confirmed": sorted(answers) if kind in ("correct", "accepted") else [],
                            "body": body, "via": "homebase"}, ensure_ascii=False) + "\n")
    if kind in ("correct", "accepted") and answers:
        allc = load(cid, "confirmed.json") or {}
        allc.setdefault(att or "_", {}).update(answers)
        save(cid, "confirmed.json", allc)


def confirmed_answers(cid, att=None):
    """Answers the GM has confirmed for this challenge's attempt (default: the current start.json attempt)."""
    if att is None:
        att = attempt_id(load(cid, "start.json"))
    return (load(cid, "confirmed.json") or {}).get(att or "_", {})


def gm_solved(cid):
    """Ask the GM itself whether this mode is already solved (its status shows result CORRECT). Local state can
    lag (timed runs on Homebase, newer attempts started after a correct one), so reruns check this first and
    never redo or burn attempts on a mode the scoreboard already has.

    STICKY: GM status reflects only the LATEST attempt, so a scout attempt started after a pass reports
    live/expired even though the scoreboard (CourseStack) keeps the solve (verified 2026-10-05). Once seen solved
    (GM CORRECT or a locally recorded correct submission) we drop a `solved_once` marker and trust it from then on."""
    marker = cdir(cid) / "solved_once"
    if marker.exists() or ever_correct(cid):
        return True
    try:
        body = call(cid, "status", cid)["body"] or {}
    except Exception:  # noqa: BLE001 - unknown means "not known solved"
        return False
    if str(body.get("result", "")).upper() == "CORRECT":
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({"attempt": attempt_id(body), "seen": time.strftime("%Y-%m-%dT%H:%M:%S")}))
        return True
    return False


def gm_latest_correct(cid):
    """Non-sticky: is the GM's LATEST attempt for this mode CORRECT? (Mastery may check its prerequisite this way.)"""
    try:
        body = call(cid, "status", cid)["body"] or {}
    except Exception:  # noqa: BLE001
        return False
    return str(body.get("result", "")).upper() == "CORRECT"


def ever_correct(cid):
    """Any attempt of this mode ever recorded CORRECT locally (submissions.jsonl), regardless of start.json drift."""
    p = cdir(cid) / "submissions.jsonl"
    if not p.exists():
        return False
    for line in p.read_text().splitlines():
        try:
            if json.loads(line).get("kind") == "correct":
                return True
        except ValueError:
            continue
    return False


def is_complete(cid):
    """All answer_ids of the current attempt confirmed, or a CORRECT result recorded for it."""
    start = load(cid, "start.json")
    if not start:
        return False
    att = attempt_id(start)
    p = cdir(cid) / "submissions.jsonl"
    if p.exists() and any(json.loads(l).get("attempt") == att and json.loads(l).get("kind") == "correct"
                          for l in p.read_text().splitlines()):
        return True
    ids = start.get("answer_ids") or []
    return bool(ids) and set(ids) <= set(confirmed_answers(cid, att))


def c_solver_test(a):
    """Refresh the Single Solve regression case from confirmed answers, then replay every case."""
    from . import orchestrate
    base = paths.base_id(a.id)
    ok, res = orchestrate.ensure_case_and_test(base, paths.solver_dir(base))
    emit({"ok": ok, "solver": str(paths.solver_dir(base).relative_to(ROOT)), "results": res})
    return 0 if ok else 1


def c_solver_run(a):
    """Run the solver library against this mode's current contract + artifacts (no submission)."""
    from . import solvers, timed
    contract = load(a.id, "start.json") or load(a.id, "contract.json")
    art = timed.latest_artifacts(a.id)
    if not contract or not art:
        print("no contract/artifacts for this mode yet (it has not been started)", file=sys.stderr)
        return EXIT["refused"]
    answers, problems = solvers.solve_contract(contract, art, paths.solver_dir(a.id))
    missing = [x for x in contract.get("answer_ids", []) if x not in answers]
    emit({"answers": answers, "missing": missing, "problems": problems})
    return 0 if not missing and not problems else 1


def c_timed(a):
    """Run one Time Trial / Mastery end to end with the solver library (+ a fix worker on failure)."""
    from . import orchestrate
    return orchestrate.run_one_timed(a.id, local_slots=a.local)


def c_run(a):
    from . import orchestrate
    pre = None  # None -> run() applies the default-on heuristic (prewarm for timed runs)
    if getattr(a, "prewarm_homebase", False):
        pre = True
    if getattr(a, "no_prewarm_homebase", False):
        pre = False
    orchestrate.run(day=a.day, only=a.only, local_slots=a.local, hb_slots=a.homebase, modes=a.modes,
                    prewarm_homebase=pre, keep_homebase=getattr(a, "keep_homebase", False),
                    scout_rounds=getattr(a, "scout", None))
    return 0


def c_scout(a):
    """Standalone Time Trial scouting for one challenge (no generalize; prints the summary)."""
    from . import orchestrate, scout
    cid = a.id if a.id.endswith("/time_trial") else paths.base_id(a.id) + "/time_trial"
    sdir = paths.solver_dir(paths.base_id(cid))
    try:
        s = scout.scout(cid, sdir, rounds=a.n, clean=a.clean, log=print)
        print(json.dumps({k: s[k] for k in ("clean_streak", "last_correct", "new_labels", "fixed", "unresolved")}
                         | ({"solver_failed": s["solver_failed"]} if s.get("solver_failed") else {}),
                         indent=2, ensure_ascii=False))
    finally:
        if os.environ.get("HCTF_KEEP_HOMEBASE", "0") == "0":
            orchestrate.workers.power_off_homebase_if_ours(print)
    return 0


def _last_worker_result(d):
    """(logname, (subtype, text)) of the newest worker-*.log's final RESULT in a mode dir, or None."""
    logs = sorted(d.glob("worker-*.log"), key=lambda p: p.stat().st_mtime)
    if not logs:
        return None
    last = None
    for line in logs[-1].read_text(errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "result":
            last = (e.get("subtype"), str(e.get("result", "")).strip()[:280])
    return (logs[-1].name, last)


def c_why(a):
    """Explain a chain's state at a glance: is each mode converging or actually stuck? Prints the block reason,
    wrong fields, attempt/block counts, timing vs window, and the last worker RESULT -- the facts otherwise
    assembled by hand from last_timed.json / window.json / diagnosis.json / the worker logs."""
    base = paths.base_id(a.id)
    chain = load_json(paths.challenge_root(base) / "chain.json") or {}
    print(f"== {base}  [{chain.get('lane', '?')}]  {chain.get('name', '')}")
    print(f"   stage={chain.get('stage', '?')}  worker={chain.get('worker') or '-'}  "
          f"attempt={chain.get('attempt', '-')}  launches={chain.get('launches', '-')}  updated={chain.get('updated', '?')}")
    for mode in paths.MODES:
        cid = base if mode == "single_solve" else f"{base}/{mode}"
        d = cdir(cid)
        if not d.exists():
            continue
        done = False
        try:
            done = is_complete(cid)
        except Exception:  # noqa: BLE001
            pass
        blocks = len(list(d.glob(".stop-blocks-*")))
        line = f"  - {mode}: {'DONE' if done else (chain.get(mode + '_result') or 'pending')}"
        if blocks:
            line += f"  blocks={blocks}/10"
        print(line)
        lt = load_json(d / "last_timed.json")
        if lt:
            win = lt.get("window")
            el = lt.get("elapsed")
            inw = lt.get("in_window")  # excludes pre-clock start/retry overhead; this is what the deadline enforces
            clock = inw if inw is not None else el
            over = "  OVER-WINDOW" if (win and clock and clock > win) else ""
            inw_s = f" (in-window {inw}s)" if inw is not None and inw != el else ""
            print(f"      last attempt: {lt.get('result')}  elapsed={el}s{inw_s}/window={win}s{over}  routed={lt.get('routed') or 'local'}")
            if lt.get("phases"):
                print(f"      phases: {lt['phases']}")
            if lt.get("wrong"):
                print(f"      WRONG fields: {lt['wrong']}  (fixed in-window: {lt.get('fixed') or {}})")
            if lt.get("localize_tried"):
                print(f"      in-window tried: {lt['localize_tried']}")
            if lt.get("missing"):
                print(f"      MISSING (solver incomplete): {lt['missing'][:12]}")
        dg = load_json(d / "diagnosis.json")
        if dg and not done:
            print(f"      probe: {dg.get('ok')} ok / {len(dg.get('wrong', []))} wrong of {dg.get('probed')}/{dg.get('total')} judged"
                  + ("" if dg.get("complete") else "  (cut short by deadline)"))
            if dg.get("unjudged"):
                print(f"      unjudged (probe ran out of clock): {dg['unjudged'][:10]}")
        wr = _last_worker_result(d)
        if wr and wr[1]:
            print(f"      last worker ({wr[0]}): {wr[1][0]} -- {wr[1][1][:180]}")
    # verdict
    stage = str(chain.get("stage", ""))
    if stage == "done":
        verdict = "DONE - all modes solved."
    elif stage.endswith(("generalizing", "fixing", "solving", "running", "fetch", "reuse")):
        verdict = "WORKING - a worker/attempt is in progress; compare `updated` to now. If it keeps cycling the SAME wrong field, it's converging on a label (watch vocab.json)."
    elif stage.endswith(("blocked", "help")):
        verdict = "BLOCKED - needs attention: see the WRONG/unjudged fields above."
    else:
        verdict = f"stage={stage}"
    print(f"  => {verdict}")
    return 0


def c_reconcile(a):
    """Reconcile local chain.json with GM truth. Local state can lag reality (fixes applied out-of-band, timed runs
    that never rewrote the chain), so the dashboard under-reports — this asks the GM (status==CORRECT) for every mode
    and rewrites each chain's result/stage to match the scoreboard. Optional --day filter. Read-the-GM, write-local."""
    changed = 0
    daytag = f"day{int(a.day):02d}" if getattr(a, "day", None) else None
    for p in sorted(paths.CHALLENGES.glob("day*/*/chain.json")):
        if daytag and daytag not in str(p.parent.parent.name) and daytag not in str(p.parent.parent):
            # parent is the challenge dir; its parent is dayNN
            if daytag != p.parent.parent.name:
                continue
        meta = load_json(p.parent / "meta.json") or {}
        ids = meta.get("ids") or {}
        chain = load_json(p) or {}
        present = [m for m in paths.MODES if ids.get(m)]
        if not present:
            continue
        solved, upd = {}, {}
        for mode in present:
            solved[mode] = gm_solved(ids[mode])
            if mode in ("time_trial", "mastery") and solved[mode] and chain.get(f"{mode}_result") != "correct":
                upd[f"{mode}_result"] = "correct"
        if all(solved.get(m) for m in present) and chain.get("stage") != "done":
            upd["stage"] = "done"
        if upd:
            chain.update(upd, updated=time.strftime("%Y-%m-%dT%H:%M:%S"))
            p.write_text(json.dumps(chain, indent=2))
            changed += 1
            print(f"  reconciled {p.parent.parent.name}/{p.parent.name}: {upd}")
    print(f"reconcile: updated {changed} chain(s) from the GM scoreboard")
    return 0


def _front_matter(text):
    """Parse a leading `--- ... ---` YAML-ish block of `key: value` lines (values may be inline lists). Best effort."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def _first_concept(text):
    """First meaningful line of a NOTES.md as a one-line concept: first `#`/`##` heading, else first prose line."""
    for line in text.splitlines():
        s = line.strip().lstrip("#").strip()
        if s and not s.startswith("---"):
            return s[:160]
    return ""


def c_solutions(a):
    """Generate reference/SOLUTIONS.md: a single human-readable index of how every challenge was solved, assembled
    from each solver/NOTES.md (+ chain.json for name/status). NOTES front-matter (challenge/lane/status/gm_vocab)
    is used when present; otherwise the first heading/line becomes the concept. Regenerate anytime (and after runs)."""
    by_day = {}
    for notes in sorted(paths.CHALLENGES.glob("day*/*/solver/NOTES.md")):
        chal = notes.parent.parent
        day = chal.parent.name
        chain = load_json(chal / "chain.json") or {}
        meta = load_json(chal / "meta.json") or {}
        text = notes.read_text(errors="replace")
        fm = _front_matter(text)
        by_day.setdefault(day, []).append({
            "dir": chal.name,
            "lane": fm.get("lane") or meta.get("lane", ""),
            "name": chain.get("name", ""),
            "status": fm.get("status") or chain.get("stage", "?"),
            "concept": fm.get("concept") or _first_concept(text),
            "vocab": fm.get("gm_vocab", ""),
            "notes": str(notes.relative_to(ROOT)),
        })
    lines = ["# Huntress CTF 2026 — Solutions index", "",
             f"_Auto-generated {time.strftime('%Y-%m-%d %H:%M')} by `hctf solutions` from each solver/NOTES.md._", ""]
    total = 0
    for day in sorted(by_day):
        lines.append(f"## {day}")
        lines.append("")
        lines.append("| Challenge | Lane | Status | How it was solved | GM vocab |")
        lines.append("|---|---|---|---|---|")
        for r in sorted(by_day[day], key=lambda x: x["lane"]):
            total += 1
            concept = r["concept"].replace("|", "\\|")
            vocab = (r["vocab"] or "").replace("|", "\\|")
            name = r["name"] or r["dir"]
            lines.append(f"| [{name}]({r['notes']}) | {r['lane']} | {r['status']} | {concept} | {vocab} |")
        lines.append("")
    out = ROOT / "reference" / "SOLUTIONS.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"wrote {out.relative_to(ROOT)} ({total} challenges across {len(by_day)} days)")
    return 0


def c_timeline(a):
    from . import timeline
    if not a.day and not a.log:
        print("give --day N or --log PATH", file=sys.stderr)
        return 2
    print(timeline.report(day=a.day, log=a.log))
    return 0


def c_dash(a):
    from . import orchestrate
    orchestrate.dashboard()
    return 0


def c_watch(a):
    from . import watch
    watch.watch(interval=a.interval)
    return 0


def c_tail(a):
    from . import watch
    watch.tail(a.id)
    return 0


def c_triage(a):
    from . import triage as triage_mod
    p = triage_mod.triage(a.id)
    if not p:
        print("no artifacts to triage (start + artifact first)", file=sys.stderr)
        return EXIT["refused"]
    sys.stdout.write(p.read_text(encoding="utf-8"))
    return 0


def c_openapi(a):
    env = call(None, "openapi")
    emit(env["body"])
    return http_exit(env)


def c_labels(a):
    from . import labels
    cands = labels.candidates(a.id, a.answer_id, terms=a.term, solver_value=a.solver_value)
    if a.dry_run:
        emit({"answer_id": a.answer_id, "candidates": cands[:max(a.budget, 40)]})
        return 0
    res = labels.probe(a.id, a.answer_id, cands, budget=a.budget, delay=a.delay)
    emit(res)
    return 0 if res.get("accepted") else EXIT["incorrect"]


def main(argv=None):
    p = argparse.ArgumentParser(prog="hctf", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    ph = sub.add_parser("hb", help="Homebase VM: status|on|off|ensure|deploy|setup|exec -- <cmd>")
    ph.add_argument("action", choices=["status", "on", "off", "ensure", "deploy", "setup", "exec"])
    ph.add_argument("command", nargs=argparse.REMAINDER)
    ph.add_argument("--timeout", type=int, default=300)
    pl = sub.add_parser("list")
    pl.add_argument("--day")
    pl.add_argument("--lane")
    pl.add_argument("--all", action="store_true")
    pl.add_argument("--json", action="store_true")
    for name in ("status", "start"):
        sub.add_parser(name).add_argument("id")
    pr = sub.add_parser("retry")
    pr.add_argument("id")
    pr.add_argument("--force", action="store_true")
    pa = sub.add_parser("artifact")
    pa.add_argument("id")
    pa.add_argument("--delivery")
    ps = sub.add_parser("submit", help="submit '{\"<answer_id>\": \"<value>\"}'")
    ps.add_argument("id")
    ps.add_argument("answers", nargs="?")
    ps.add_argument("--force", action="store_true")
    ps.add_argument("--from-solver", action="store_true", help="submit what the challenge's solve.py emits")
    sub.add_parser("openapi")
    sub.add_parser("triage", help="deterministic no-LLM triage of a mode's artifacts").add_argument("id")
    sub.add_parser("solver-test", help="refresh + replay the solver's regression cases").add_argument("id")
    sub.add_parser("solver-run", help="run solvers on a mode's current contract (no submit)").add_argument("id")
    pt = sub.add_parser("timed", help="run one time_trial/mastery end to end")
    pt.add_argument("id")
    pt.add_argument("--local", type=int, default=2)
    pr2 = sub.add_parser("run", help="every challenge chain in parallel (single -> time_trial -> mastery)")
    pr2.add_argument("--day")
    pr2.add_argument("--only", nargs="*", help="substrings of challenge ids to include")
    pr2.add_argument("--local", type=int, default=5, help="concurrent local claude -p workers")
    pr2.add_argument("--homebase", type=int, default=0, help="concurrent Homebase codex workers")
    pr2.add_argument("--keep-homebase", action="store_true",
                     help="don't power Homebase off at end of run (keep it warm for the next burst); also HCTF_KEEP_HOMEBASE=1")
    pr2.add_argument("--no-prewarm-homebase", action="store_true",
                     help="disable the default background Homebase prewarm for timed runs (HCTF_PREWARM_HOMEBASE=0)")
    pr2.add_argument("--prewarm-homebase", action="store_true",
                     help="boot+provision Homebase at run start (in the background) so tight timed windows don't "
                          "wait for a cold VM; powers off at run end. Also via HCTF_PREWARM_HOMEBASE=1")
    pr2.add_argument("--modes", nargs="*", choices=list(paths.MODES))
    pr2.add_argument("--scout", type=int, default=None, metavar="N",
                     help="Time Trial scout rounds before Mastery (learn label spellings on the cheap clock); "
                          "0 = off (default HCTF_SCOUT_ROUNDS)")
    psc = sub.add_parser("scout", help="run N Time Trial attempts to harvest variants + learn GM labels (no generalize)")
    psc.add_argument("id", help="challenge base id or its /time_trial id")
    psc.add_argument("-n", type=int, default=3, help="max rounds (default 3)")
    psc.add_argument("--clean", type=int, default=2, help="stop after this many clean rounds in a row (default 2)")
    sub.add_parser("dash", help="chain status table")
    sub.add_parser("why", help="explain a chain's state: converging vs stuck, wrong fields, timing, last worker result"
                   ).add_argument("id")
    prc = sub.add_parser("reconcile", help="rewrite local chain.json from GM truth (fixes stale/under-reported dash)")
    prc.add_argument("--day")
    ptl = sub.add_parser("timeline", help="per-chain T+ per mode, attempts, generalize cycles, LLM vs overhead")
    ptl.add_argument("--day", type=int)
    ptl.add_argument("--log", help="a dayNN.log path (default .run/dayNN.log)")
    sub.add_parser("solutions", help="(re)generate reference/SOLUTIONS.md index from every solver/NOTES.md")
    pw = sub.add_parser("watch", help="live board of every challenge + each agent's current action")
    pw.add_argument("--interval", type=float, default=2.0)
    sub.add_parser("tail", help="follow one agent's reasoning + tool calls live").add_argument("id")
    pl2 = sub.add_parser("labels", help="resolve a non-flag field's exact GM label: rank candidates from sibling "
                                        "confirmed labels + artifact terms, then probe them one at a time")
    pl2.add_argument("id")
    pl2.add_argument("answer_id")
    pl2.add_argument("--term", action="append", default=[],
                     help="artifact-derived term (keyword, magic, spec name), e.g. --term if --term defined; repeatable")
    pl2.add_argument("--solver-value", default=None, help="the value you derived (its tokens become terms too)")
    pl2.add_argument("--budget", type=int, default=25, help="max candidates to submit (default 25)")
    pl2.add_argument("--delay", type=float, default=1.0, help="seconds between submits (rate limit)")
    pl2.add_argument("--dry-run", action="store_true", help="only print the ranked candidates")
    a = p.parse_args(argv)
    fn = {"hb": c_hb, "list": c_list, "status": c_status, "start": c_start, "retry": c_retry,
          "artifact": c_artifact, "submit": c_submit, "openapi": c_openapi, "solver-test": c_solver_test,
          "solver-run": c_solver_run, "timed": c_timed, "run": c_run, "dash": c_dash, "why": c_why,
          "reconcile": c_reconcile, "solutions": c_solutions,
          "triage": c_triage, "watch": c_watch, "tail": c_tail, "labels": c_labels, "scout": c_scout,
          "timeline": c_timeline}[a.cmd]
    try:
        return fn(a)
    except remote.Unreachable as e:
        print(f"unreachable: {e}\n(hint: `hctf hb ensure`, and check the VPN)", file=sys.stderr)
        return EXIT["unreachable"]


if __name__ == "__main__":
    sys.exit(main())
