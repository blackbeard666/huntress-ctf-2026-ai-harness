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

from . import contract, paths, remote
from .paths import ROOT

# Wrong-answer budgets. Per-field probing lets the harness resolve the GM's exact wording for structured,
# non-flag fields on its own; flags are brute-force-protected; a global ceiling stops runaway.
MAX_WRONG_PER_ATTEMPT = int(os.environ.get("HCTF_MAX_WRONG", "6"))   # per non-flag answer_id
FLAG_WRONG_CAP = int(os.environ.get("HCTF_FLAG_WRONG_CAP", "3"))     # wrong flag guesses per attempt
GLOBAL_WRONG_CAP = int(os.environ.get("HCTF_GLOBAL_WRONG_CAP", "80"))  # total wrong per attempt (sanity)
# Probe budget of one bisect (parallel waves, hctf/grouptest.py): ~24 groups + 2 halves per wrong field per level.
BISECT_BUDGET = int(os.environ.get("HCTF_BISECT_BUDGET", "160"))
# Confirm exactly the GM's `accepted_ids` on a partial accept (real GM and replay_gm both send it); off = infer from
# the drop in `remaining`, which a concurrent submit (race bisect beside the worker) can mis-attribute.
ACCEPTED_IDS = os.environ.get("HCTF_ACCEPTED_IDS", "1") != "0"
# Harness-made submissions (reuse race, spelling alternates) never consume the WORKER's per-field wrong budget; the
# exact rejected value stays refused ("already judged incorrect") either way.
HARNESS_WRONG_FREE = os.environ.get("HCTF_HARNESS_WRONG_FREE", "1") != "0"
# Untimed modes: refuse a warmups-style slug made of non-words (lib/slug.py) before it costs a GM submission (D13 race:
# rot-N gibberish of Atbash text). --force overrides; timed windows never run this check.
SLUG_GATE = os.environ.get("HCTF_SLUG_GATE", "1") != "0"
# After a single-field rejection on the untimed Single, probe <= N same-value SPELLING alternates (hctf/fmtalt.py) before
# the worker spends an LLM turn on it (D10 hex width, D13 GUID braces: ~20 s each).
FORMAT_ALTS = os.environ.get("HCTF_FORMAT_ALTS", "1") != "0"
FORMAT_ALTS_MAX = int(os.environ.get("HCTF_FORMAT_ALTS_MAX", "3"))
FLAG_RE = re.compile(r"^[0-9a-f]{32}$")
EXIT = {"correct": 0, "incorrect": 1, "accepted": 2, "expired": 3, "refused": 4, "unreachable": 5, "error": 6,
        "already_solved": 0}


def cdir(cid):
    return paths.mode_dir(cid)


def now():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


# Re-sent challenge text in GM submit replies (script D15: `questions` = 548 KB per reply). Stored per submit it made
# submissions.jsonl 53 MB (93 submits, alt armA) -> is_complete 0.79 s/call and a ready-watcher crash on a half-written line.
BIG_BODY_KEYS = ("questions", "prompt", "guidance", "instructions", "description")


def slim_body(body):
    """A GM reply minus the challenge text it re-sends (verdict, remaining, ids and errors are kept)."""
    if not isinstance(body, dict):
        return body
    return {k: v for k, v in body.items() if k not in BIG_BODY_KEYS}


def log(cid, op, env):
    target = cdir(cid) / "log.jsonl" if cid else paths.LOGS / "gm.jsonl"
    if op == "submit" and isinstance(env, dict) and isinstance(env.get("body"), dict):
        env = {**env, "body": slim_body(env["body"])}
    with open(target, "a") as f:   # t: sub-second wall clock (drop-time latency forensics; ts is 1 s resolution)
        f.write(json.dumps({"ts": now(), "t": round(time.time(), 3), "op": op, **env}, ensure_ascii=False) + "\n")


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
    """Atomic (temp file + rename): concurrent probe submits read confirmed.json while another one rewrites it."""
    p = cdir(cid) / name
    tmp = p.with_name(f".{name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False))
    os.replace(tmp, p)


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
    if r in ("incorrect", "accepted", "expired", "already_solved"):
        return r
    return None


def classify_reply(env):
    """Canonical GM-reply classifier -> 'correct' | 'accepted' | 'incorrect' | 'already_solved' | 'expired'
    | 'unjudged'. UNJUDGED means the GM never scored the request and folds in rate_limited, an empty /
    non-JSON body, a body with no `result` key, and any transport failure (http 0, or a non-200 carrying no
    scored verdict). The rule that costs points if a call site forgets it: UNJUDGED is NEVER `incorrect` --
    back off and re-send, never eliminate a candidate on it. (result_kind sees only the body string, so every
    caller had to re-layer this; route the whole envelope through here instead.)"""
    return result_kind((env or {}).get("body")) or "unjudged"


def call(cid, op, *args, timeout=180):
    env = remote.gm(op, *args, timeout=timeout)
    log(cid, op, env)
    if op == "list" and isinstance(env.get("body"), dict):
        for c in env["body"].get("challenges") or []:
            if isinstance(c, dict) and c.get("lane") and paths.canonical_lane(c["lane"]) != c["lane"]:
                c["gm_lane"], c["lane"] = c["lane"], paths.canonical_lane(c["lane"])
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
    if a.action == "budget":
        from . import hbbudget, workers
        if remote.probe():
            workers.meter_vm()
        print(hbbudget.summary_line())
        return 0
    if a.action == "keepalive":
        # Keep the VM metered + active for a window (warm-up -> run -> ratchet): one cheap ssh a minute books its uptime
        # in the credit ledger; stops on its own after --timeout seconds (default 300 -> use e.g. --timeout 7200).
        from . import hbbudget, workers
        end = time.time() + a.timeout
        while time.time() < end:
            up = remote.probe()
            if up:
                workers.meter_vm()
            print(time.strftime("%H:%M:%S"), "up" if up else "DOWN", "|", hbbudget.summary_line(), flush=True)
            time.sleep(60)
        return 0
    if a.action == "tools":
        # Heavy toolchain on the VM itself (JDK/jadx/apktool/Ghidra/rizin/ilspycmd/...; no root, ~/hbtools).
        remote.rsync_to(ROOT / "setup" / "homebase_tools.sh", "~/homebase_tools.sh")
        r = remote.ssh("nice -n 10 bash ~/homebase_tools.sh 2>&1 | grep -E '^\\[(ok|MISSING|hb-tools)'", timeout=1800,
                       check=False)
        sys.stdout.write(r.stdout)
        return 0 if "[MISSING]" not in r.stdout else 1
    if a.action == "setup":
        # Provision Homebase so solvers run next to the GM (hb_timed). Idempotent.
        remote.rsync_to(ROOT / "setup" / "homebase_setup.sh", "~/homebase_setup.sh")
        # user-level tools for VMs without passwordless sudo (rehearsal): setup/fetch_hb_tools.sh caches them locally
        tools = ROOT / ".run" / "cache" / "hb-tools" / "7zz"
        if tools.exists():
            remote.ssh("mkdir -p ~/.local/bin", check=False)
            remote.rsync_to(tools, "~/.local/bin/7zz")
        r = remote.ssh("bash ~/homebase_setup.sh", timeout=600, check=False)
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        return 0 if r.returncode == 0 else EXIT["error"]
    if a.action == "exec":
        # Run a command ON Homebase (inside the CTF network), e.g. to reach a live challenge backend.
        cmd = list(a.command)
        # argparse.REMAINDER swallows options written after the action: `hb exec --timeout 30 -- cmd` (D16: the
        # --timeout reached ssh as "unknown option --")
        while cmd[:1] == ["--timeout"] and len(cmd) >= 2:
            a.timeout, cmd = int(cmd[1]), cmd[2:]
        cmd = cmd[1:] if cmd[:1] == ["--"] else cmd
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
    a.id = paths.resolve_id(a.id)
    env = call(a.id, "status", a.id)
    if env["body"] is not None:
        save(a.id, "status.json", env["body"])
        if env["body"].get("questions"):
            # The questions contract comes back even before a start (409 start_required), so solvers
            # can be written for Time Trial / Mastery without starting a clock.
            save(a.id, "contract.json", env["body"])
        from . import webtarget
        if (paths.mode_of(a.id) == "single_solve" and webtarget.ready(env["body"]) and attempt_id(env["body"])
                and attempt_id(load(a.id, "start.json")) != attempt_id(env["body"])):
            # web single: the target came up after a `preparing` start (which saved no start.json): this is the contract
            save(a.id, "start.json", env["body"])
            webtarget.empty_artifacts(cdir(a.id), attempt_id(env["body"]))
    emit(env["body"] if env["body"] is not None else env)
    return http_exit(env) if env["http"] != 409 else EXIT["error"]


def contract_drift(cid):
    """Re-fetch cid's contract and diff its questions against start.json (same attempt only). Questions the GM REWROTE
    in place -- D17 binary: two open-vocab hcfg_storage fields became enums ~4 h after the drop, same attempt/sha/ids --
    are saved into start.json + contract.json and stamped in drift.json, so the submit guards forget their earlier
    (old-question) rejections. Returns the changed/added answer ids; [] when nothing changed or the GM is unreachable."""
    started = load(cid, "start.json") or {}
    # a never-started TT / Mastery: its status-time contract.json is what the next start is compared with
    old = started if started.get("questions") else (load(cid, "contract.json") or {})
    if not old.get("questions"):
        return []
    try:
        env = call(cid, "status", cid)
    except Exception:  # noqa: BLE001 - GM unreachable: no drift known
        return []
    new = env.get("body") if isinstance(env.get("body"), dict) else {}
    if not new.get("questions") or (attempt_id(new) and attempt_id(new) != attempt_id(old)):
        return []
    qo = {q.get("id"): q for q in old["questions"] if isinstance(q, dict)}
    qn = {q.get("id"): q for q in new["questions"] if isinstance(q, dict)}
    changed = [i for i in qn if i in qo and json.dumps(qn[i], sort_keys=True) != json.dumps(qo[i], sort_keys=True)]
    added = [i for i in qn if i not in qo]
    if not changed and not added:
        return []
    old["questions"] = [qn.get(q.get("id"), q) for q in old["questions"] if isinstance(q, dict)] + [qn[i] for i in added]
    if added:
        old["answer_ids"] = list(dict.fromkeys(list(old.get("answer_ids") or []) + added))
    if started.get("questions"):
        save(cid, "start.json", old)
    save(cid, "contract.json", old)
    drift = load(cid, "drift.json") or {}
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    drift.update({i: stamp for i in changed + added})
    save(cid, "drift.json", drift)
    return changed + added


def c_start(a, op="start"):
    with chal_lock(a.id):
        env = call(a.id, op, a.id)
    from . import webtarget
    if env["http"] == 200 and webtarget.needs_wait(env["body"]):
        # web: the target is still `preparing` (no clock yet) / the attempt was `cleaned`: wait for it here (bounded --
        # a worker's Bash call times out at ~2 min) instead of the worker polling `hctf status` by hand
        body = webtarget.wait_ready(a.id, env["body"], log=lambda m: print(m, file=sys.stderr),
                                    wait=webtarget.CLI_WAIT)
        env = dict(env, body=body)
        if not webtarget.ready(body):
            print("note: the web target is not up yet (no clock while it prepares) -- run `hctf start` again in a "
                  "minute", file=sys.stderr)
    # An after-deadline start answers 200 {"result": "expired"} with no attempt_id/answer_ids; saving that would
    # clobber the last real contract (lost the Mastery 6279ad62 case and broke solver-run).
    if env["body"] is not None and env["http"] == 200 and attempt_id(env["body"]):
        save(a.id, "start.json", env["body"])
        save(a.id, "contract.json", env["body"])
        if webtarget.ready(env["body"]):
            webtarget.empty_artifacts(cdir(a.id), attempt_id(env["body"]))
    emit(env["body"] if env["body"] is not None else env)
    return http_exit(env)


def c_arena(a):
    """`hctf arena start|stop|status <id>` (operators; workers never need it: `hctf start` waits/revives itself). Also the
    sanctioned reset for a BURNED one-shot credit kit (D27 Double Spent): `stop` then `start` gives a fresh target +
    fresh credit (there is no in-app reset route). The orchestrator does this automatically on a burn (see
    orchestrate/webtarget self-heal); a codify verify worker may do it too (its target is private)."""
    from . import webtarget
    a.id = paths.resolve_id(a.id)
    body = webtarget.arena(a.id, a.op)
    emit(slim_body(body))
    return 0 if not body.get("error") else EXIT["error"]


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
    """Map answer_id -> question dict, keyed by answer_ids (the authority; never drops an id)."""
    return contract.answer_map(start)


def _normalize(value, q):
    """Apply the question's normalization. 'exact' is left untouched; everything else is at least trimmed."""
    norm = (q or {}).get("normalization")
    v = _json_coerce(value, q)
    if norm == "exact":
        return v
    v = v.strip()
    if norm == "case_insensitive":
        v = v.lower()
    return v


def _json_coerce(value, q):
    """answer_format.kind == "json" but the value is a Python literal (`['a', 'b']`, `{'k': 1}`, True/None): send the
    same data as compact JSON. D23 metadata Mastery: a solver returned a list that was str()'d -> `['box-06/...', ...]`
    rejected on every set; the compact JSON of the same list was accepted. Valid JSON is never touched."""
    af = (q or {}).get("answer_format") if isinstance((q or {}).get("answer_format"), dict) else {}
    if str(af.get("kind")) != "json" or not isinstance(value, str):
        return value
    s = value.strip()
    if not s or s[0] not in "[{(":
        return value
    try:
        json.loads(s)
        return value
    except ValueError:
        pass
    import ast
    try:
        obj = ast.literal_eval(s)
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return value
    if isinstance(obj, tuple):
        obj = list(obj)
    if not isinstance(obj, (list, dict)):
        return value
    try:
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError):
        return value


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


def _slug_problem(value, q):
    """Warmups slug plausibility (lib/slug.py): a slug of non-words is a mis-decode, not a GM spelling question."""
    try:
        from lib import slug
        return slug.slug_problem(value, q)
    except Exception:  # noqa: BLE001 - the gate must never itself block a submission
        return None


def _bisect_rejected(cid, answers, budget=BISECT_BUDGET, harness=None, families=True, stop=None, resolve=True):
    """Which of a rejected batch's answer_ids does the GM reject? PARALLEL group testing (hctf/grouptest.py): the batch
    cut into ~24 family-ordered groups probed at once, then every failing group halved and both halves probed at once,
    each probe-tagged (accepted groups are banked). Returns the set of individually rejected answer_ids.
    families=False: the groups are plain contiguous cuts (the reuse race's speculative remainder spans many families).
    stop(): checked before every wave -- the reuse race yields to the worker's own submit (rehearsal fair D16: both bisected
    the same 1095 fields at once, ~5 s per probe).
    D16 script single: the sequential version took 55 submits / 4:04 for 5 wrong fields of 1095."""
    from . import grouptest
    conf0 = confirmed_answers(cid)
    answers = {k: v for k, v in answers.items() if conf0.get(k) != v}

    def probe(g):
        g = {k: v for k, v in g.items() if k not in confirmed_answers(cid)}
        if not g:
            return "ok"
        try:
            kind, body, _p = submit(cid, g, force=True, probe=True, **({"harness": harness} if harness else {}))
        except (remote.Unreachable, OSError, RuntimeError) as e:
            print(f"bisect: probe of {len(g)} field(s) failed ({str(e)[:80]})", file=sys.stderr)
            return None
        if kind in ("correct", "accepted"):
            return "ok"
        if kind == "incorrect":
            return "bad"
        if kind == "already_solved":
            return "solved"          # the attempt is CORRECT: nothing left to learn
        # rate_limited / empty / non-JSON / expired: UNJUDGED, never a rejection
        return "rate" if "rate_limited" in json.dumps(body or {})[:2000] else None

    bad, st = grouptest.find_rejected(probe, answers, budget=budget, families=families, stop=stop)
    print(f"bisect: {st['probes']} probe(s) in {st['waves']} parallel wave(s), {st['seconds']}s"
          + (f", {st['rate_limited']} rate-limited (concurrency down to {st['conc_min']})" if st["rate_limited"] else "")
          + (f", {st['unjudged_fields']} field(s) left unjudged" if st.get("unjudged_fields") else ""), file=sys.stderr)
    if resolve and bad and not is_complete(cid):
        # resolve the isolated fields' labels right away (enum: the contract's accepted_values) -- no LLM turn
        from . import labels
        won = labels.resolve_parallel(cid, {a: answers[a] for a in bad if a in answers},
                                      harness=harness or "label", log=lambda m: print(m, file=sys.stderr))
        _print_resolved(cid, won, answers)
        bad = {a for a in bad if a not in won}
    return bad


def _print_resolved(cid, won, answers):
    if won:
        print("RESOLVED by the harness (the GM ACCEPTED these on this attempt) -- make solve.py emit them: "
              + "; ".join(f"{a} = {v!r} (you sent {answers.get(a)!r})" for a, v in won.items()), file=sys.stderr)


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
        sd = paths.solver_dir(a.id)
        got, err, dt = solvers.run_solver(sd, contract, art)
        if not err:
            # Stamp for the stop-at-correct watcher: this exact solver code just produced these answers in dt seconds,
            # so a CORRECT verdict needs no second run of it (binary: ~3.6 s + the stability wait on the critical path).
            try:
                (cdir(a.id) / ".solver_stamp.json").write_text(json.dumps({
                    "mtimes": {p.name: p.stat().st_mtime for p in sd.iterdir() if p.is_file() and p.suffix == ".py"},
                    "seconds": round(dt, 2), "answers": got}))
            except OSError:
                pass
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
    bad = set()
    if a.from_solver and not problems and kind == "incorrect" and len(answers) > 1:
        race = _await_race(a.id)
        if race is not None:
            # the harness race bisected this attempt (one bisector per attempt): resubmit only what is still open
            if is_complete(a.id):
                kind = "correct"
            else:
                conf = confirmed_answers(a.id)
                rest = {k: v for k, v in answers.items() if conf.get(k) != v}
                if rest and rest != answers:
                    answers = rest
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
    if kind in ("incorrect", "accepted") and not is_complete(a.id):
        rejected = list(answers) if kind == "incorrect" and len(answers) == 1 else sorted(bad)
        if kind == "incorrect" and len(answers) == 1:
            from . import labels      # a lone rejected field: its other labels (enum: accepted_values) in parallel
            won = labels.resolve_parallel(a.id, dict(answers), harness="label", log=lambda m: print(m, file=sys.stderr))
            _print_resolved(a.id, won, answers)
            rejected = [k for k in rejected if k not in won]
            if is_complete(a.id):
                kind = "correct"
        k2, b2 = _try_format_alts(a.id, {k: answers[k] for k in rejected if k in answers})
        if k2:
            kind, body = k2, b2
    emit(body)                        # the verdict first: the stop-at-correct watcher may end the worker any moment
    if a.from_solver:
        sys.stdout.flush()
        _mastery_dry_run(a.id)
    return EXIT.get(kind, EXIT["error"])


RACE_DEFER_S = float(os.environ.get("HCTF_RACE_DEFER_S", "90"))


def _await_race(cid, max_wait=None):
    """If the orchestrator's reuse race is bisecting THIS attempt (race_bisect.json, pid alive), wait for it instead of
    running a second bisect over the same fields, then print what it found. -> the marker dict, or None."""
    m = load(cid, "race_bisect.json") or {}
    att = attempt_id(load(cid, "start.json"))
    if not m or m.get("attempt") != att:
        return None
    if not m.get("done"):
        try:
            os.kill(int(m.get("pid")), 0)
        except (OSError, TypeError, ValueError):
            return None
        if time.time() - float(m.get("started") or 0) > 600:
            return None
        print("the harness reuse race is bisecting this attempt -- waiting for it instead of a second bisect",
              file=sys.stderr)
        end = time.time() + (RACE_DEFER_S if max_wait is None else max_wait)
        while time.time() < end and not is_complete(cid):
            m = load(cid, "race_bisect.json") or {}
            if m.get("done") or m.get("attempt") != att:
                break
            time.sleep(0.5)
    if m.get("done"):
        print(f"race result: {len(confirmed_answers(cid))} field(s) banked; still REJECTED: {m.get('wrong') or []}; "
              f"labels resolved by the harness: {m.get('resolved') or {}}", file=sys.stderr)
    return m


def _try_format_alts(cid, rejected):
    """Untimed Single only: for each field the GM just rejected on its own (<= 3 fields), probe <= FORMAT_ALTS_MAX
    spelling alternates of the SAME value (hctf/fmtalt.py: hex width/0x/case, GUID braces/case/bytes_le, trim/quotes)
    as harness-tagged single-field submits -- they don't eat the worker's per-field budget. An accepted spelling is
    printed with the instruction to make solve.py emit it, and remembered per field ending. -> (kind, body) of the
    last accepting submit, or (None, None)."""
    if not FORMAT_ALTS or not rejected:
        return None, None
    start = load(cid, "start.json") or {}
    if start.get("deadline") or paths.base_id(cid) != cid:
        return None, None
    from . import fmtalt
    qmap = _questions(start)
    kind = body = None
    for aid, val in list(rejected.items())[:3]:
        if aid in confirmed_answers(cid):
            continue
        for alt, how in fmtalt.alternates(aid, val, qmap.get(aid, {}), max_n=FORMAT_ALTS_MAX):
            k, b, refused = submit(cid, {aid: alt}, harness="alt")
            if refused:
                continue
            if k in ("correct", "accepted"):
                fmtalt.record(aid, how)
                print(f"ACCEPTED alternate spelling for {aid}: {alt!r} (transform {how}; you sent {val!r}). Make "
                      f"solve.py emit exactly this, then run `hctf submit {cid} --from-solver`.", file=sys.stderr)
                kind, body = k, b
                break
            print(f"format alternate {alt!r} ({how}) for {aid}: {k}", file=sys.stderr)
    return kind, body


def submit(cid, answers, force=False, max_wrong=MAX_WRONG_PER_ATTEMPT, global_cap=None, probe=False, harness=None):
    """Guarded submission shared by the CLI, the workers and the timed runner.
    Returns (kind, body, problems). kind is None when refused locally (problems explains why).
    Answers the GM confirms are merged into <mode dir>/confirmed.json (keyed by attempt).
    `harness` ("race" / "alt"): a submission the HARNESS made (reuse race, spelling alternates), recorded as such: its
    single-field rejections still refuse that exact value later, but never count against the worker's per-field cap."""
    start = load(cid, "start.json")
    att = attempt_id(start)
    qmap = _questions(start)
    # Auto-apply the GM's stated normalization so a stray space/case never wastes a submission.
    answers = {k: _normalize(str(v), qmap.get(k, {})) for k, v in answers.items()}
    subs_path = cdir(cid) / "submissions.jsonl"
    if att and att in _correct_attempts(subs_path):
        # Already CORRECT: the GM answers already_solved ("not scored"). alt armA D15: a background bisect kept sending
        # 11 of those after its worker was ended, beside the Time Trial kickoff.
        print("note: this attempt is already CORRECT (already_solved): nothing sent", file=sys.stderr)
        return "already_solved", {"result": "already_solved", "local": True}, []
    history = []
    # force=True ignores every guard below: skip parsing the (multi-MB) log -- the parallel probes of a bisect each re-read
    # 2.3 MB of submissions.jsonl under the GIL (rehearsal fair D16)
    if subs_path.exists() and not force:
        for ln in subs_path.read_text().splitlines():
            try:
                history.append(json.loads(ln))
            except ValueError:
                continue          # a torn line (writer mid-append)
    # probe=True submissions (harness reuse/localization batches) prove nothing about any single value when the
    # batch is incorrect, so they never feed the "already judged incorrect" / per-field wrong-count guards.
    drift = load(cid, "drift.json") or {}
    if drift:
        # A question the GM rewrote in place (contract_drift): verdicts given BEFORE the rewrite judged the old question.
        # Drop every entry that holds such a field (a trimmed batch would read as a single-field rejection).
        history = [h for h in history if not any(k in drift and str(h.get("ts", "")) < drift[k]
                                                  for k in (h.get("answers") or {}))]
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
        if h.get("kind") != "incorrect" or (HARNESS_WRONG_FREE and h.get("harness")):
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
    untimed = not (start or {}).get("deadline")
    for k, v in answers.items():
        prob = _format_problem(str(v), qmap.get(k, {})) or (
            _slug_problem(str(v), qmap.get(k, {})) if SLUG_GATE and untimed else None)
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

    t_call = time.time()
    if ACCEPTED_IDS:
        # Concurrent submits are safe: the GM names what it accepted (accepted_ids), so nothing is inferred from
        # `remaining`; only the local bookkeeping below is locked. D16: holding chal_lock across the ~1.8 s GM call
        # serialized every probe of a bisect (the GM itself judges 12 concurrent submits in 3.3 s).
        env = call(cid, "submit", cid, json.dumps(answers))
    else:
        with chal_lock(cid):
            env = call(cid, "submit", cid, json.dumps(answers))
    dt_call = round(time.time() - t_call, 2)
    body = env["body"] if env["body"] is not None else env
    kind = classify_reply(env)   # 'correct'|'accepted'|'incorrect'|'already_solved'|'expired'|'unjudged'

    # Which answers does this result prove correct?
    newly = {}
    if kind == "correct":
        newly = dict(answers)
    elif kind == "accepted":
        remaining = (env["body"] or {}).get("remaining")
        acc_ids = (env["body"] or {}).get("accepted_ids")
        if ACCEPTED_IDS and isinstance(acc_ids, list):
            # the GM names exactly what it accepted: no inference from `remaining` (which a concurrent race/worker
            # submit moves too -- the race bisects while the worker submits from the same challenge dir)
            newly = {k: v for k, v in answers.items() if k in set(acc_ids)}
        else:
            if subs_path.exists():        # re-read: another submitter may have moved `remaining` since the guards ran
                history = [json.loads(l) for l in subs_path.read_text().splitlines()]
            before = [h for h in history if h.get("attempt") == att  # incl. probe batches: they move `remaining` too
                      and isinstance((h.get("body") or {}).get("remaining"), int)]
            prev = before[-1]["body"]["remaining"] if before else len(qmap) - len(confirmed) if qmap else None
            if len(answers) == 1 or (isinstance(remaining, int) and prev is not None and prev - remaining == len(answers)):
                newly = dict(answers)
    with chal_lock(cid):      # confirmed.json read-modify-write + the log append (concurrent probe submits)
        if newly:
            allc = load(cid, "confirmed.json") or {}
            allc.setdefault(att or "_", {}).update(newly)
            save(cid, "confirmed.json", allc)
        with open(subs_path, "a") as f:
            f.write(json.dumps({"ts": now(), "attempt": att, "answers": answers, "http": env["http"],
                                "kind": kind, "confirmed": sorted(newly), "body": slim_body(env["body"]),
                                **({"probe": True} if probe else {}), **({"harness": harness} if harness else {}),
                                **({"transport": env["transport"]} if env.get("transport") else {}),
                                "elapsed": dt_call},
                               ensure_ascii=False) + "\n")
    return kind, body, []


def record_remote_result(cid, att, answers, kind, body=None):
    """Record a submission made ON Homebase (by hb_timed) into local state, so is_complete/dash are accurate."""
    att = att or attempt_id(load(cid, "start.json"))
    with open(cdir(cid) / "submissions.jsonl", "a") as f:
        f.write(json.dumps({"ts": now(), "attempt": att, "answers": answers, "http": 200,
                            "kind": kind, "confirmed": sorted(answers) if kind in ("correct", "accepted") else [],
                            "body": slim_body(body), "via": "homebase"}, ensure_ascii=False) + "\n")
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
    at = gm_list_solved(_day_of(cid)).get(cid) if _day_of(cid) else None
    if at:
        # the scoreboard has it on an EARLIER attempt (D16 script Mastery: CORRECT out of band, then a re-roll made
        # the latest attempt not-correct and `reconcile` reported 0 updated)
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({"attempt": None, "solved_at": at, "seen": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                      "via": "list"}))
        return True
    return False


def _day_of(cid):
    m = re.search(r"-day-(\d+)", cid)
    return int(m.group(1)) if m else None


_list_cache = {}


def gm_list_solved(day, max_age=20.0):
    """{mode id: solved_at} from the GM's `list` for a day: `solved` is the scoreboard's per-mode truth (sticky across
    attempts), unlike status (the latest attempt only). One call per day, cached max_age s."""
    hit = _list_cache.get(day)
    if hit and time.time() - hit[0] < max_age:
        return hit[1]
    try:
        body = remote.gm("list", "--day", str(day))["body"] or {}
    except Exception:  # noqa: BLE001 - unknown = nothing known solved
        return {}
    out = {c["id"]: ((c.get("solved_by") or {}).get("at") or True) for c in body.get("challenges") or []
           if isinstance(c, dict) and c.get("solved") and c.get("id")}
    _list_cache[day] = (time.time(), out)
    return out


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


_correct_cache = {}


def _correct_attempts(p):
    """Attempt ids with a `correct` submission in submissions.jsonl. Cached by (size, mtime); a torn / bad line (a
    writer mid-append) is skipped, never raised (alt armA D15: `Unterminated string` killed the ready-watcher)."""
    try:
        st = p.stat()
    except OSError:
        return set()
    key = (st.st_size, st.st_mtime_ns)
    hit = _correct_cache.get(str(p))
    if hit and hit[0] == key:
        return hit[1]
    out = set()
    with open(p, "rb") as f:
        for raw in f:
            if b'"correct"' not in raw:
                continue
            try:
                r = json.loads(raw)
            except ValueError:
                continue
            if r.get("kind") == "correct":
                out.add(r.get("attempt"))
    _correct_cache[str(p)] = (key, out)
    return out


def is_complete(cid):
    """All answer_ids of the current attempt confirmed, or a CORRECT result recorded for it."""
    start = load(cid, "start.json")
    if not start:
        return False
    att = attempt_id(start)
    if att in _correct_attempts(cdir(cid) / "submissions.jsonl"):
        return True
    ids = start.get("answer_ids") or []
    return bool(ids) and set(ids) <= set(confirmed_answers(cid, att))


def c_solver_test(a):
    """Refresh the Single Solve regression case from confirmed answers, then replay every case."""
    from . import orchestrate, solvers
    base = paths.base_id(a.id)
    sdir = paths.solver_dir(base)
    pats = getattr(a, "case", None)
    if pats or getattr(a, "timeout", None):
        # targeted iteration (generalize workers): only the named / globbed cases, optional per-case timeout
        orchestrate.ensure_case_and_test(base, sdir, full=False)
        res = solvers.test_solver(sdir, timeout=a.timeout or 120, cases=pats or None)
        ok = bool(res) and all(r["ok"] for r in res)
    else:
        ok, res = orchestrate.ensure_case_and_test(base, sdir)
    static = solvers.id_cache_problems(sdir)   # D25: an id()-keyed cache passes 1-set cases, fails a pooled Mastery
    emit({"ok": ok and not static, "solver": str(sdir.relative_to(ROOT)), "results": res,
          **({"static_problems": static} if static else {})})
    return 0 if ok and not static else 1


def c_speed_harden(a):
    from . import orchestrate
    if not (a.id or a.day):
        print("give a challenge id or --day N", file=sys.stderr)
        return EXIT["refused"]
    res = orchestrate.speed_harden(day=a.day, cid=a.id, log=print)
    emit({b: {"before": v[0], "after": v[1]} for b, v in res.items()})
    return 0


def c_prebuild(a):
    """Off-peak LLM breadth for a lane (hctf/prebuild.py). --stop / --recover / --list are offline + instant."""
    from . import prebuild as pb
    if a.stop:
        pb.stop(log=print)
        return 0
    if a.recover:
        pb.recover(log=print)
        return 0
    if a.parallel and not a.list:
        res = pb.run_parallel(n=a.n, budget_usd=a.budget_usd,
                              deadline=pb.parse_deadline(a.deadline) if a.deadline else None, log=print)
        emit(res)
        return 0
    lane = pb.lane_key(a.lane)
    if a.list:
        cfg = pb.LANES.get(lane) or {}
        state = pb._load_json(pb.STATE, {})
        nxt = {t.get("id") for t in pb.pending(lane, cfg, 0)} if cfg and pb._requires_met(cfg) else set()
        for t in pb.targets(cfg) if cfg else []:
            st = state.get(f"{lane}:{t.get('id')}", {})
            print(f"{'next' if t.get('id') in nxt else 'done' if st.get('ok') else 'skip':5} {t.get('id'):22} "
                  f"attempts={st.get('attempts', 0)} {'; '.join(st.get('reasons') or [])[:100]}")
        print(f"enabled lanes: {', '.join(pb.enabled_lanes())}; budget for n={a.n or pb.DEFAULT_N}: "
              f"${pb.budget_for(a.n or pb.DEFAULT_N)}; default deadline {pb.default_deadline():%Y-%m-%d %H:%M}")
        return 0
    from . import orchestrate
    only = [x.strip() for x in (a.targets or "").split(",") if x.strip()] or None
    res = orchestrate.prebuild(lane, n=a.n, targets=only, budget_usd=a.budget_usd,
                               deadline=pb.parse_deadline(a.deadline) if a.deadline else None, log=print)
    emit(res)
    return 0 if all(r.get("ok") for r in res) else 1


def c_tool_wait(a):
    from . import toolchain
    return toolchain.main(["wait", a.tool, "--timeout", str(a.timeout)])


def c_tool_gaps(a):
    from . import toolchain
    return toolchain.main(["report"] + (["--day", str(a.day)] if a.day else []))


def c_effort_report(a):
    """Side-by-side effort A/B of one day across harness copies (hctf/effort_report.py)."""
    from . import effort_report
    print(effort_report.report(a.day, a.root or None))
    return 0


def c_train(a):
    """Offline training of a day's lane solvers on every earlier day (hctf/train.py)."""
    from . import train
    argv = ["--day", str(a.day), "--rounds", str(a.rounds)] + sum((["--lane", x] for x in a.lane or []), []) \
        + (["--no-mutation"] if a.no_mutation else []) + (["--dry-run"] if a.dry_run else [])
    return train.main(argv)


def c_postrun(a):
    """Resume a day's post-run after a crash (hctf/postrun.py): restore what the killed run left, then the phases from
    --from (default: the first phase not marked done in .run/dayNN.postrun.json)."""
    from . import postrun
    from .orchestrate import say     # timestamped lines: appended to .run/dayNN.log, `hctf feed --postrun` follows them
    if not a.no_recover:
        postrun.recover(a.day, log=say)
    start = a.start
    if start is None:
        done = {k for k, v in (postrun.load(a.day).get("phases") or {}).items() if v.get("status") == "done"}
        start = next((ph for ph in postrun.PHASES if ph not in done), None)
        if start is None:
            print(f"day {a.day}: every post-run phase is already done ({', '.join(postrun.PHASES)})")
            return 0
    say(f"[postrun] day {a.day}: resuming from '{start}' ({' -> '.join(postrun.PHASES[postrun.PHASES.index(start):])})")
    postrun.run_phases(a.day, start, log=say)
    return 0


def c_compound_check(a):
    """Compounding readiness: today's solver vs every earlier day's GM-verified cases of its lane (hctf/compound.py)."""
    from . import compound
    argv = ([a.id] if a.id else []) + (["--day", str(a.day)] if a.day else []) + ["--per-day", str(a.per_day)]
    return compound.main(argv)


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
                    scout_rounds=getattr(a, "scout", None), wait_release=getattr(a, "wait_release", False),
                    no_postrun=getattr(a, "no_postrun", False))
    # Clean exit: the run spawns many ThreadPoolExecutors that are never shut down, so concurrent.futures' atexit
    # handler joins their worker threads at interpreter exit -- a stuck background probe there HANGS the process after
    # the run has already finished (observed on live runs: needed a manual reap). Results + post-run are done and
    # driftwatch/prebuild are detached subprocesses, so flush and os._exit(0) to bypass that join.
    # HCTF_RUN_CLEAN_EXIT=0 restores the normal return (debugging).
    if os.environ.get("HCTF_RUN_CLEAN_EXIT", "1") != "0":
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
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
    base = paths.base_id(paths.resolve_id(a.id))
    chain = load_json(paths.challenge_root(base) / "chain.json") or {}
    print(f"== {base}  [{chain.get('lane', '?')}]  {chain.get('name', '')}")
    print(f"   stage={chain.get('stage', '?')}  worker={chain.get('worker') or '-'}  "
          f"attempt={chain.get('attempt', '-')}  launches={chain.get('launches', '-')}  updated={chain.get('updated', '?')}")
    open_modes = []   # D31 #3: modes with local state that are not solved (the verdict never says "all solved" over them)
    for mode in paths.MODES:
        cid = base if mode == "single_solve" else f"{base}/{mode}"
        d = paths.challenge_root(base) / mode   # (cdir() would create it: a single-only chain has no timed dirs)
        if not d.exists():
            continue
        done = False
        try:
            done = is_complete(cid)
        except Exception:  # noqa: BLE001
            pass
        if not done and str(chain.get(mode + "_result") or "").lower() != "correct" and any(d.iterdir()):
            open_modes.append(mode)
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
            if lt.get("partial_submit"):
                print(f"      partial submit: {lt['partial_submit']}  (wrong: {lt.get('partial_wrong') or []})")
            if lt.get("attempts_remaining") is not None:
                print(f"      GM unique attempts left for this mode: {lt['attempts_remaining']}")
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
    if stage == "done" and not open_modes:
        verdict = "DONE - all modes solved."
    elif stage == "done":
        verdict = (f"NOT DONE - chain.json says done but {', '.join(open_modes)} not solved locally: `hctf reconcile` "
                   "(GM truth) / `hctf status <id>`, then re-run the chain if the GM agrees.")
    elif stage.endswith(("generalizing", "fixing", "solving", "running", "fetch", "reuse")):
        verdict = "WORKING - a worker/attempt is in progress; compare `updated` to now. If it keeps cycling the SAME wrong field, it's converging on a label (watch vocab.json)."
    elif stage.endswith(("blocked", "help")):
        verdict = "BLOCKED - needs attention: see the WRONG/unjudged fields above."
    else:
        verdict = f"stage={stage}"
    print(f"  => {verdict}")
    return 0


def c_drift(a):
    """Re-fetch every UNSOLVED mode's contract of --day and report questions the GM rewrote in place (saved, so a
    resumed run / worker sees them and the guards forget the old rejections). --resume re-runs a changed chain;
    --watch keeps checking every --interval s until --until (what the run starts by itself when a mode is left
    unsolved). D17: the binary storage fix landed ~4 h after the drop with no notice."""
    from . import driftwatch
    if not getattr(a, "day", None):
        print("refused:\n  give --day N", file=sys.stderr)
        return EXIT["refused"]
    if a.watch:
        return driftwatch.watch(int(a.day), interval=a.interval, until=a.until)
    found = driftwatch.check_once(int(a.day), do_resume=a.resume, log=print)
    st = driftwatch.status(int(a.day))
    print(f"drift: {len(found)} mode(s) with rewritten questions"
          + (" -> resume with `hctf drift --day N --resume` (or `hctf run --day N --only <id>`)"
             if found and not a.resume else "")
          + f"; watcher {'running' if st['alive'] else 'not running'}")
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
    from . import retrieval   # the machine-readable twin the workers' prompts are retrieved from
    rows = retrieval.build_index()
    print(f"wrote {retrieval.INDEX.relative_to(ROOT)} ({len(rows)} challenges with a solver)")
    return 0


def c_feed(a):
    from . import feed
    if not a.day and not a.log:
        print("give --day N or --log PATH", file=sys.stderr)
        return 2
    return feed.main(day=a.day, log=a.log, from_start=a.from_start, follow_=not a.no_follow, heartbeat=a.heartbeat,
                     postrun=True if a.postrun else None)


def c_timeline(a):
    from . import timeline
    if not a.day and not a.log:
        print("give --day N or --log PATH", file=sys.stderr)
        return 2
    print(timeline.report(day=a.day, log=a.log, t0=getattr(a, "t0", None)))
    return 0


def c_kpi(a):
    from . import kpi
    days = kpi.days_with_logs() if a.all else ([a.day] if a.day else [])
    if not days:
        print("give --day N or --all", file=sys.stderr)
        return 2
    if a.log and len(days) != 1:
        print("--log needs exactly one --day", file=sys.stderr)
        return 2
    for d in days:
        try:
            k = kpi.compute(day=d, log=a.log, root=getattr(a, "root", None))
        except (OSError, ValueError) as e:
            print(f"day {d}: {e}")
            continue
        if a.label:
            k["label"] = a.label
        legacy = getattr(a, "legacy", False)
        print(kpi.render(k) if not a.all else kpi.row(k).rstrip())
        if not legacy:   # v2: the whole board from the drop + per lane / segment (kpi.py docstring)
            print(kpi.render_v2(k) if not a.all else (kpi.board_row(k) or "").rstrip())
        if a.record:
            print(f"  -> {kpi.record(k).relative_to(ROOT)}")
            if not legacy:
                kpi.record_v2(k)
    return 0


def c_hof(a):
    from . import hof
    tt, ms = hof.fetch("time_trial"), hof.fetch("mastery")
    print(hof.report(day=a.day, rows=tt + ms))
    if a.save:
        print(f"snapshot -> {hof.snapshot(tt, ms)}")
    return 0


def c_dash(a):
    from . import orchestrate
    orchestrate.dashboard()
    return 0


def c_cost(a):
    from . import workers
    print(workers.metrics_report(day=a.day))
    if a.day is not None:
        from . import gmload
        print()
        print(gmload.report(a.day))
    return 0


def c_watch(a):
    from . import watch
    watch.watch(interval=a.interval)
    return 0


def c_tail(a):
    from . import watch
    watch.tail(paths.resolve_id(a.id), n=a.n, follow=not a.no_follow)
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
    if a.compose:
        # depth-3 <form>_<home>_<kind> compounds from HELP.md/NOTES.md evidence + --term words + the lane lexicon,
        # probed in parallel waves (off the worker's per-field cap). Write what you observed into HELP.md/NOTES.md
        # first: the field's own slot sentence ("d14 (ObjC, RAW HCFG in its own .hcfg section)") ranks the slots.
        words, secs = labels.field_evidence(a.id, a.answer_id)
        terms = [t.lower() for t in a.term]
        cands = labels.compose(a.id, a.answer_id, limit=a.budget if a.budget != 25 else labels.COMPOSE_N,
                               words=list(dict.fromkeys(terms + words)), sections=secs)
        if a.dry_run:
            emit({"answer_id": a.answer_id, "evidence": words[:20], "sections": secs, "candidates": cands[:60],
                  "total": len(cands)})
            return 0
        v = labels.probe_first(a.id, a.answer_id, cands)
        emit({"answer_id": a.answer_id, "accepted": v, "tried_up_to": len(cands)})
        return 0 if v else EXIT["incorrect"]
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
    ph = sub.add_parser("hb", help="Homebase VM: status|on|off|ensure|deploy|setup|tools|budget|keepalive|exec -- <cmd>")
    ph.add_argument("action", choices=["status", "on", "off", "ensure", "deploy", "setup", "tools", "budget",
                                       "keepalive", "exec"])
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
    par = sub.add_parser("arena", help="web live targets via the browser arena endpoint: start (revives a `cleaned` "
                                       "attempt) | stop (frees the team's one live web target) | status")
    par.add_argument("op", choices=["start", "stop", "status"])
    par.add_argument("id")
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
    pst = sub.add_parser("solver-test", help="refresh + replay the solver's regression cases")
    pst.add_argument("id")
    pst.add_argument("--case", action="append", help="only cases matching this name/glob (repeatable), e.g. 'variant-*'")
    pst.add_argument("--timeout", type=float, help="per-case timeout in seconds (default 120)")
    psh = sub.add_parser("speed-harden", help="off-clock speed generalize for solvers whose slowest case is over budget")
    psh.add_argument("id", nargs="?")
    psh.add_argument("--day", type=int)
    ppb = sub.add_parser("prebuild", help="off-peak LLM breadth for a lane (speculative extractors + fixtures, gated)")
    ppb.add_argument("--lane", default="metadata-forensics", help="metadata-forensics | warmups | binary-reverse-engineering")
    ppb.add_argument("--n", type=int, default=None, help="max targets (workers) this batch (HCTF_PREBUILD_N)")
    ppb.add_argument("--targets", help="comma list of target ids (default: the ranked TARGETS.json order)")
    ppb.add_argument("--budget-usd", type=float, default=None, help="stop before a worker would exceed this")
    ppb.add_argument("--deadline", help="HH:MM host time: start no worker that can't finish by then")
    ppb.add_argument("--stop", action="store_true", help="stop a running batch + restore its snapshot (bin/day.sh)")
    ppb.add_argument("--recover", action="store_true", help="restore a snapshot a killed batch left behind")
    ppb.add_argument("--list", action="store_true", help="targets + their state, budget, deadline")
    ppb.add_argument("--parallel", action="store_true", help="every enabled lane at once (private lib/ per lane, gated "
                     "one at a time); --n per lane (default: drain), --lane ignored")
    ptw = sub.add_parser("tool-wait", help="block until a toolchain tool triage started installing is ready")
    ptw.add_argument("tool")
    ptw.add_argument("--timeout", type=int, default=600)
    ptg = sub.add_parser("tool-gaps", help="post-run review: toolchain tools that were missing (installed / no recipe)")
    ptg.add_argument("--day", type=int)
    per = sub.add_parser("effort-report", help="effort A/B: one day across harness copies (main xhigh vs the rehearsal copy high)")
    per.add_argument("--day", type=int, required=True)
    per.add_argument("--root", action="append", help="harness copy root (repeatable; default main)")
    ppr = sub.add_parser("postrun", help="resume a day's post-run after a crash (ratchet/speed-harden/train/prebuild/"
                                         "coverage); restores interrupted generalize/ratchet snapshots first")
    ppr.add_argument("--day", type=int, required=True)
    ppr.add_argument("--from", dest="start", choices=["ratchet", "speed-harden", "train", "prebuild", "coverage"])
    ppr.add_argument("--no-recover", action="store_true", help="skip restoring interrupted snapshots")
    ptr = sub.add_parser("train", help="offline training: a day's solvers vs every earlier day's verified cases")
    ptr.add_argument("--day", type=int, required=True)
    ptr.add_argument("--lane", action="append")
    ptr.add_argument("--rounds", type=int, default=2)
    ptr.add_argument("--no-mutation", action="store_true")
    ptr.add_argument("--dry-run", action="store_true")
    pcc = sub.add_parser("compound-check", help="replay earlier days' verified cases of the lane through today's solver")
    pcc.add_argument("id", nargs="?")
    pcc.add_argument("--day", type=int)
    pcc.add_argument("--per-day", type=int, default=3)
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
    pr2.add_argument("--wait-release", action="store_true",
                     help="start now, poll the GM in-process until --day is released, then launch at once "
                          "(bin/day.sh --wait uses this; HCTF_RELEASE_POLL s between polls)")
    pr2.add_argument("--no-prewarm-homebase", action="store_true",
                     help="disable the default background Homebase prewarm for timed runs (HCTF_PREWARM_HOMEBASE=0)")
    pr2.add_argument("--prewarm-homebase", action="store_true",
                     help="boot+provision Homebase at run start (in the background) so tight timed windows don't "
                          "wait for a cold VM; powers off at run end. Also via HCTF_PREWARM_HOMEBASE=1")
    pr2.add_argument("--modes", nargs="*", choices=list(paths.MODES))
    pr2.add_argument("--no-postrun", action="store_true",
                     help="skip post-run (ratchet/prebuild/coverage) after the board is done. Post-run is also held "
                          "automatically while any mode is still unsolved, and suppressed by HCTF_RATCHET=0")
    pr2.add_argument("--scout", type=int, default=None, metavar="N",
                     help="Time Trial scout rounds before Mastery (learn label spellings on the cheap clock); "
                          "0 = off (default HCTF_SCOUT_ROUNDS)")
    psc = sub.add_parser("scout", help="run N Time Trial attempts to harvest variants + learn GM labels (no generalize)")
    psc.add_argument("id", help="challenge base id or its /time_trial id")
    psc.add_argument("-n", type=int, default=3, help="max rounds (default 3)")
    psc.add_argument("--clean", type=int, default=2, help="stop after this many clean rounds in a row (default 2)")
    sub.add_parser("dash", help="chain status table")
    pco = sub.add_parser("cost", help="worker LLM cost/turns/tokens per chain x stage + non-ok exits (.run/metrics.tsv)")
    pco.add_argument("--day", type=int)
    sub.add_parser("why", help="explain a chain's state: converging vs stuck, wrong fields, timing, last worker result"
                   ).add_argument("id")
    prc = sub.add_parser("reconcile", help="rewrite local chain.json from GM truth (fixes stale/under-reported dash)")
    prc.add_argument("--day")
    pdr = sub.add_parser("drift", help="re-fetch unsolved modes' contracts; report + save questions the GM rewrote in place")
    pdr.add_argument("--day")
    pdr.add_argument("--resume", action="store_true", help="re-run a chain whose contract changed (no post-run)")
    pdr.add_argument("--watch", action="store_true", help="keep checking until --until (the run starts this itself)")
    pdr.add_argument("--interval", type=float, default=600.0)
    pdr.add_argument("--until", default="20:15", help="local HH:MM (next occurrence >= 30 min away)")
    ptl = sub.add_parser("timeline", help="per-chain T+ per mode, attempts, generalize cycles, LLM vs overhead")
    ptl.add_argument("--day", type=int)
    ptl.add_argument("--log", help="a dayNN.log path (default .run/dayNN.log)")
    ptl.add_argument("--t0", help="HH:MM:SS to count T+ from, e.g. the drop 21:00:00 (default: the run's release line)")
    pfd = sub.add_parser("feed", help="live milestone feed of a run (solved k/N, blocked, generalize, duel, hints)")
    pfd.add_argument("--day", type=int)
    pfd.add_argument("--log", help="a run log path (default .run/dayNN.log)")
    pfd.add_argument("--from-start", action="store_true", help="also print the milestones already in the log")
    pfd.add_argument("--no-follow", action="store_true", help="print what is there and exit")
    pfd.add_argument("--heartbeat", type=float, default=60.0, help="status line every N seconds while running")
    pfd.add_argument("--postrun", action="store_true",
                     help="follow the post-run to 'post-run finished' (default: only for a bin/day.sh run, by pid file)")
    pkp = sub.add_parser("kpi", help="per-day KPI row: T+ 14/15 and 15/15, release lag, race wins, first-try timed "
                                     "modes, generalizes on the critical path, cost (reference/PLAN_SUB2MIN.md)")
    pkp.add_argument("--day", type=int)
    pkp.add_argument("--all", action="store_true", help="one row per day with a .run/dayNN.log")
    pkp.add_argument("--record", action="store_true", help="append the row(s) to reference/KPI.md")
    pkp.add_argument("--log", help="score this log instead of .run/dayNN.log (a replay's run.log)")
    pkp.add_argument("--label", help="row label, e.g. replay-a (kept beside the real day's row)")
    pkp.add_argument("--legacy", action="store_true", help="only the pre-D25 row (5 regular lanes from the release)")
    pkp.add_argument("--root", help="harness copy whose challenges/ hold the GM logs (default this one; v2 GM split)")
    phf = sub.add_parser("hof", help="Hall of Fame speed board: our rank/ms vs #1 per challenge + day sums (public)")
    phf.add_argument("--day", type=int)
    phf.add_argument("--save", action="store_true", help="also snapshot the board to reference/hof/")
    sub.add_parser("solutions", help="(re)generate reference/SOLUTIONS.md index from every solver/NOTES.md")
    pw = sub.add_parser("watch", help="live board of every challenge + each agent's current action")
    pw.add_argument("--interval", type=float, default=2.0)
    ptl = sub.add_parser("tail", help="follow one agent's reasoning + tool calls live")
    ptl.add_argument("id", help="GM id or the dayNN/<dir>[/mode] name hctf dash prints")
    ptl.add_argument("-n", type=int, default=None, help="first print the last N events of the log")
    ptl.add_argument("--no-follow", action="store_true", help="print and exit (scripts / monitors)")
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
    pl2.add_argument("--compose", action="store_true", help="depth-3 <form>_<home>_<kind> compounds from HELP.md/NOTES.md evidence + the lane lexicon, probed in parallel (open-vocab label fields)")
    a = p.parse_args(argv)
    fn = {"hb": c_hb, "list": c_list, "status": c_status, "start": c_start, "retry": c_retry,
          "artifact": c_artifact, "submit": c_submit, "openapi": c_openapi, "solver-test": c_solver_test, "compound-check": c_compound_check, "train": c_train, "postrun": c_postrun, "effort-report": c_effort_report, "tool-wait": c_tool_wait, "speed-harden": c_speed_harden, "prebuild": c_prebuild, "tool-gaps": c_tool_gaps,
          "solver-run": c_solver_run, "timed": c_timed, "run": c_run, "dash": c_dash, "why": c_why,
          "reconcile": c_reconcile, "drift": c_drift, "solutions": c_solutions,
          "triage": c_triage, "watch": c_watch, "tail": c_tail, "labels": c_labels, "scout": c_scout,
          "timeline": c_timeline, "cost": c_cost, "hof": c_hof, "feed": c_feed, "kpi": c_kpi,
          "arena": c_arena}[a.cmd]
    try:
        return fn(a)
    except remote.Unreachable as e:
        # (Not `hctf hb ensure`: workers run sandboxed without /mnt/c, where the VM power helper lives -- Day 8 binary
        # worker crashed on it. Homebase health is the orchestrator's job.)
        print(f"unreachable: {e}\n(hint: the GM/Homebase hiccuped -- `hctf status <id>` to see what landed, then "
              "resubmit; the orchestrator handles Homebase power)", file=sys.stderr)
        return EXIT["unreachable"]


if __name__ == "__main__":
    sys.exit(main())
