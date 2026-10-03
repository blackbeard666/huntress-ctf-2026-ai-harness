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
import time
from contextlib import contextmanager
from pathlib import Path

from . import paths, remote
from .paths import ROOT

# Guard against flag brute-forcing. Structured non-flag fields (enum spellings, ATT&CK IDs) may need a
# few more legitimate probes on untimed single-solves; raise via HCTF_MAX_WRONG for those, never for flags.
MAX_WRONG_PER_ATTEMPT = int(os.environ.get("HCTF_MAX_WRONG", "3"))
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


def emit(obj):
    json.dump(obj, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def http_exit(env):
    return 0 if env["http"] == 200 else (EXIT["error"])


# ---------------------------------------------------------------- commands

def c_hb(a):
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
    if env["body"] is not None and env["http"] == 200:
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
    cap_re = re.compile(r"/download/([0-9a-f]{64})")

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
    rdir = f"{remote.HB_DIR}/dl/{paths.slugify(a.id)}/{ts}"
    saved = []
    for name, cap, sha in plan:
        env = call(a.id, "download", cap, rdir, "--name", name, timeout=600)
        if not env["saved"]:
            emit(env["body"] if env["body"] is not None else env)
            return http_exit(env) or EXIT["error"]
        s = env["saved"][0]
        if sha and s["sha256"] != sha:
            raise RuntimeError(f"sha256 mismatch for {name}: GM said {sha}, got {s['sha256']}")
        saved.append((name, s))
    local = cdir(a.id) / "artifacts" / ts
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


def c_submit(a):
    kind, body, problems = submit(a.id, json.loads(a.answers), force=a.force)
    if problems:
        print("refused:\n  " + "\n  ".join(problems), file=sys.stderr)
        return EXIT["refused"]
    emit(body)
    return EXIT.get(kind, EXIT["error"])


def submit(cid, answers, force=False, max_wrong=MAX_WRONG_PER_ATTEMPT):
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
    same_attempt = [h for h in history if h.get("attempt") == att]
    wrong = sum(1 for h in same_attempt if h.get("kind") == "incorrect")
    confirmed = confirmed_answers(cid, att)

    problems = []
    if qmap:
        for k in answers:
            if k not in qmap:
                problems.append(f"{k}: not an answer_id of the current attempt {sorted(qmap)}")
    for k, v in answers.items():
        prob = _format_problem(str(v), qmap.get(k, {}))
        if prob:
            problems.append(f"{k}: {prob}")
        for h in same_attempt:
            if h.get("kind") == "incorrect" and h["answers"].get(k) == v and len(h["answers"]) == 1:
                problems.append(f"{k}: this exact value was already judged incorrect in this attempt")
    # Flag-format answers stay strictly capped (anti-brute-force) even if HCTF_MAX_WRONG is raised.
    flag_like = any(FLAG_RE.fullmatch(str(v)) for v in answers.values())
    cap = min(3, max_wrong) if flag_like else max_wrong
    if wrong >= cap:
        problems.append(f"{wrong} incorrect submissions already in this attempt (cap {cap}); "
                        "investigate instead of guessing")
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
        before = [h for h in same_attempt if isinstance((h.get("body") or {}).get("remaining"), int)]
        prev = before[-1]["body"]["remaining"] if before else len(qmap) - len(confirmed) if qmap else None
        if len(answers) == 1 or (isinstance(remaining, int) and prev is not None and prev - remaining == len(answers)):
            newly = dict(answers)
    if newly:
        allc = load(cid, "confirmed.json") or {}
        allc.setdefault(att or "_", {}).update(newly)
        save(cid, "confirmed.json", allc)

    with open(subs_path, "a") as f:
        f.write(json.dumps({"ts": now(), "attempt": att, "answers": answers, "http": env["http"],
                            "kind": kind, "confirmed": sorted(newly), "body": env["body"]},
                           ensure_ascii=False) + "\n")
    return kind, body, []


def confirmed_answers(cid, att=None):
    """Answers the GM has confirmed for this challenge's attempt (default: the current start.json attempt)."""
    if att is None:
        att = attempt_id(load(cid, "start.json"))
    return (load(cid, "confirmed.json") or {}).get(att or "_", {})


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
    orchestrate.run(day=a.day, only=a.only, local_slots=a.local, hb_slots=a.homebase, modes=a.modes)
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


def main(argv=None):
    p = argparse.ArgumentParser(prog="hctf", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    ph = sub.add_parser("hb", help="Homebase VM: status|on|off|ensure|deploy|exec -- <cmd>")
    ph.add_argument("action", choices=["status", "on", "off", "ensure", "deploy", "exec"])
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
    ps.add_argument("answers")
    ps.add_argument("--force", action="store_true")
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
    pr2.add_argument("--modes", nargs="*", choices=list(paths.MODES))
    sub.add_parser("dash", help="chain status table")
    pw = sub.add_parser("watch", help="live board of every challenge + each agent's current action")
    pw.add_argument("--interval", type=float, default=2.0)
    sub.add_parser("tail", help="follow one agent's reasoning + tool calls live").add_argument("id")
    a = p.parse_args(argv)
    fn = {"hb": c_hb, "list": c_list, "status": c_status, "start": c_start, "retry": c_retry,
          "artifact": c_artifact, "submit": c_submit, "openapi": c_openapi, "solver-test": c_solver_test,
          "solver-run": c_solver_run, "timed": c_timed, "run": c_run, "dash": c_dash,
          "triage": c_triage, "watch": c_watch, "tail": c_tail}[a.cmd]
    try:
        return fn(a)
    except remote.Unreachable as e:
        print(f"unreachable: {e}\n(hint: `hctf hb ensure`, and check the VPN)", file=sys.stderr)
        return EXIT["unreachable"]


if __name__ == "__main__":
    sys.exit(main())
