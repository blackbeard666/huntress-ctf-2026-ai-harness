"""Web lane = LIVE TARGET challenges (2026-10-19, first web day). One notion used across the harness.

GM facts (observed on the first web day):
- No downloadable artifact (`artifact` -> 400 invalid_delivery). A started attempt carries
  `targets: [{"id": "Target 1", "url": "https://<hash>.2026.huntress.ctf.games/"}]` (+ `routes`); solve.py reads
  `contract["targets"][*].url`, matched by each question's `artifact: "Target N"`.
- `start` answers `{"result": "preparing"}` (no attempt_id / answer_ids / targets, no deadline) for ~20 s .. ~2.5 min,
  then `status` shows `result: "active"` with targets. There is no clock while preparing.
- D19: ONE live web target per TEAM: extra starts sat in `preparing`; three parallel Time Trial starts all went
  preparing -> `cleaned` (`routes: []`) and wedged (start/retry kept returning the dead attempt). The browser arena's
  endpoint (`POST /arena/api {"op": "start", ...}`, hctf/gm.py cmd_arena) revived a cleaned attempt.
- 2026-10-20 the organizers raised it: five targets live at once (probe), so web chains run in parallel up to SLOTS.
  The OpenAPI's `switch_target: true` (start, web only) stops the team's least recently used UNTIMED target on another
  challenge when the team limit is full -- never sent by the harness (it could stop another chain's working target).
- After a CORRECT the target answers HTTP 410 {"state": "completed"} and the team slot frees -- so a regression case
  of a FINISHED web attempt can never be replayed (its target is gone); one of the LIVE attempt still can.

Stdlib only at module level: hctf/hb_timed.py imports this file next to the GM (Homebase copy) too.
"""
import contextlib
import json
import os
import re
import threading
import time
from pathlib import Path

LIVE_LANES = {"web"}
PREPARING = ("preparing",)
DEAD = ("cleaned", "stopped")
TERMINAL = ("correct", "incorrect", "expired", "completed")
WAIT = float(os.environ.get("HCTF_WEB_PREPARE_WAIT", "480"))      # s a start may sit in `preparing` (no clock then)
POLL = float(os.environ.get("HCTF_WEB_PREPARE_POLL", "4"))
REVIVE_EVERY = float(os.environ.get("HCTF_WEB_REVIVE_EVERY", "30"))
MAX_REVIVES = int(os.environ.get("HCTF_WEB_MAX_REVIVES", "6"))
CLI_WAIT = float(os.environ.get("HCTF_WEB_CLI_WAIT", "90"))       # `hctf start` by a worker (its Bash call caps ~120 s)
SLOT = os.environ.get("HCTF_WEB_SLOT", "1") != "0"
# Live web targets the team may hold at once. D19: ONE (a 2nd start clobbered the 1st). Probed 2026-10-20 22:16: five
# TT targets active together (every web challenge released so far), Mastery (2 targets) up in 12-17 s beside them; the GM
# OpenAPI now has `switch_target` for "if a team limit is full". 5 = what was measured, not the GM's cap.
SLOTS = max(1, int(os.environ.get("HCTF_WEB_SLOTS", "5")))
STOP_AFTER_CORRECT = os.environ.get("HCTF_WEB_STOP_AFTER_CORRECT", "1") != "0"
# Kick a start stuck in `preparing`: D20 both Mastery first starts sat 5:21 (alt Admin 5:17 off-peak) while every
# `retry` came up in 11-18 s (10/10) -- and a retry on an unsolved attempt hands back the SAME attempt once it is live.
# Kicks alternate public `retry` / arena `start` (a Single Solve has no retry: arena only); never `switch_target`.
KICK = os.environ.get("HCTF_WEB_KICK", "1") != "0"
KICK_AFTER = float(os.environ.get("HCTF_WEB_KICK_AFTER", "5"))    # C1: a fresh start can wedge minutes, but a retry
KICK_EVERY = float(os.environ.get("HCTF_WEB_KICK_EVERY", "15"))   # returns the SAME attempt in 11-18 s -> kick EARLY
MAX_KICKS = int(os.environ.get("HCTF_WEB_MAX_KICKS", "4"))
LIVE_CASE_TTL = 25 * 60     # a live compounding case's target: an idle untimed web target stops after ~30 min


# ------------------------------------------------------------------ predicates

def is_live_lane(lane):
    lane = (lane or "").strip().lower()
    return lane in LIVE_LANES or lane.startswith("web")


def is_live_cid(cid):
    """A web challenge id (GM `web-exploitation-day-NN-...`), or one the index files under the web lane."""
    base = re.sub(r"/(time_trial|mastery)$", "", str(cid or ""))
    if base.startswith("web-") or base.startswith("web_"):
        return True
    try:
        from . import paths
    except ImportError:
        return False
    try:
        return is_live_lane((paths.lookup(base) or {}).get("lane"))
    except Exception:  # noqa: BLE001 - unknown -> not live
        return False


def _result(body):
    return str((body or {}).get("result") or "").lower() if isinstance(body, dict) else ""


def is_live_body(body):
    """A start/status body of a live-target attempt (web): it names targets/routes or is in a target lifecycle state."""
    return isinstance(body, dict) and ("targets" in body or "routes" in body or _result(body) in PREPARING + DEAD)


def target_urls(body):
    ts = (body or {}).get("targets") if isinstance(body, dict) else None
    return [t.get("url") for t in ts or [] if isinstance(t, dict) and t.get("url")]


def ready(body):
    """A live attempt whose target is up: answer ids + at least one target url, not preparing/cleaned."""
    return (isinstance(body, dict) and bool(body.get("answer_ids")) and bool(target_urls(body))
            and _result(body) not in PREPARING + DEAD)


def dead(body):
    return _result(body) in DEAD


# GM errors that are TRANSIENT -- resend, never give up: a rate limit, and `control_unavailable`, which was
# measured 2026-10-22 as a transient op=start hiccup (a 26.7 s hang) that a plain resend cleared on try 1. Both
# read as a non-rate-limit error otherwise, so a naive "error -> terminal" test would abandon a workable route.
_TRANSIENT_ERRORS = ("rate_limited", "control_unavailable")


def _transient_error(err):
    e = str(err or "")
    return any(t in e for t in _TRANSIENT_ERRORS)


def terminal(body):
    """Nothing to wait for: a verdict, or a GM refusal that is NOT transient (not a rate limit / control_unavailable)."""
    if not isinstance(body, dict):
        return True
    if body.get("error"):
        return not _transient_error(body.get("error"))
    return _result(body) in TERMINAL


def needs_wait(body):
    return is_live_body(body) and not ready(body) and not terminal(body)


# ------------------------------------------------------------------ waiting for a target

def _timed_cid(cid):
    return bool(re.search(r"/(time_trial|mastery)$", str(cid or "")))


def kick_plan(cid, n):
    """The n-th kick (0-based) of a start stuck in `preparing`: `retry` on even n, arena `start` on odd n; a Single Solve
    (no /time_trial|/mastery suffix) has no retry (GM 405) -> always the arena."""
    return "retry" if _timed_cid(cid) and n % 2 == 0 else "arena"


def _att(body):
    return str((body or {}).get("attempt_id") or "")[:8] if isinstance(body, dict) else ""


def await_target(cid, body, status, revive=None, log=print, wait=None, poll=None, revive_every=None,
                 max_revives=None, sleep=time.sleep, clock=time.time, kick=None, trace=None, kick_after=None,
                 kick_every=None, max_kicks=None):
    """`body` = a start/retry reply. While it is `preparing` (no clock yet) poll `status(cid)` until the target is up;
    when the attempt is `cleaned` (dead target), `revive(cid)` (the arena start) at most every `revive_every` s; while it
    stays `preparing` past `kick_after` s, `kick(cid, n)` (kick_plan: retry / arena start) at most every `kick_every` s,
    `max_kicks` times. Every state change, revive and kick is appended to `trace` (a list) and logged.
    Returns the last body (ready, terminal, or still waiting with `_web_wait: "timeout"` after `wait` s). Never raises
    on a failed poll: an empty/failed status keeps the previous body; an error reply to a kick never replaces it."""
    if not needs_wait(body):
        return body
    wait = WAIT if wait is None else wait
    poll = POLL if poll is None else poll
    revive_every = REVIVE_EVERY if revive_every is None else revive_every
    max_revives = MAX_REVIVES if max_revives is None else max_revives
    kick_after = KICK_AFTER if kick_after is None else kick_after
    kick_every = KICK_EVERY if kick_every is None else kick_every
    max_kicks = (MAX_KICKS if KICK else 0) if max_kicks is None else max_kicks
    t0, revives, last_revive, last_state = clock(), 0, None, None
    kicks, last_kick = 0, None

    def note(ev, **kw):
        if trace is not None:
            trace.append({"t": round(clock() - t0, 1), "ev": ev, **kw})

    while True:
        st = _result(body) or str(body.get("error") or "?")
        if ready(body) or terminal(body):
            if last_state is not None:
                note("state", state="ready" if ready(body) else st, att=_att(body))
                log(f"[{cid}] web target {'up' if ready(body) else st} after {clock() - t0:.0f}s"
                    + (f" ({len(target_urls(body))} target(s))" if ready(body) else "")
                    + (f" after {kicks} kick(s)" if kicks else ""))
            return body
        if st != last_state:
            note("state", state=st, att=_att(body))
            log(f"[{cid}] web target {st} (+{clock() - t0:.0f}s): waiting for it (no clock while it prepares; "
                "web chains are capped at SLOTS live targets)")
            last_state = st
        if dead(body) and revive is not None and revives < max_revives and (
                last_revive is None or clock() - last_revive >= revive_every):
            revives += 1
            last_revive = clock()
            try:
                rb = revive(cid)
            except Exception as e:  # noqa: BLE001 - the poll goes on
                rb = {"error": f"revive failed: {type(e).__name__}"}
            note("revive", n=revives, result=_result(rb) or (rb or {}).get("error") or "?", att=_att(rb))
            log(f"[{cid}] web attempt {st}: arena start (revive {revives}/{max_revives}) -> "
                f"{_result(rb) or (rb or {}).get('error') or '?'}")
            if ready(rb):
                return rb
        elif (st in PREPARING and kick is not None and kicks < max_kicks and clock() - t0 >= kick_after
              and (last_kick is None or clock() - last_kick >= kick_every)):
            how = kick_plan(cid, kicks)
            kicks += 1
            tk = clock()
            try:
                kb = kick(cid, kicks - 1)
            except Exception as e:  # noqa: BLE001 - the poll goes on
                kb = {"error": f"kick failed: {type(e).__name__}"}
            last_kick = clock()
            res = _result(kb) or (kb or {}).get("error") or "?" if isinstance(kb, dict) else "?"
            note("kick", n=kicks, how=how, result=res, att=_att(kb), took=round(clock() - tk, 1))
            log(f"[{cid}] web target preparing +{tk - t0:.0f}s: kick {kicks}/{max_kicks} {how} -> {res} "
                f"({clock() - tk:.1f}s)")
            if ready(kb):
                note("state", state="ready", att=_att(kb), via=how)
                return kb
            if isinstance(kb, dict) and kb and not kb.get("error"):
                body = kb
        if clock() - t0 >= wait:
            out = dict(body)
            out["_web_wait"] = "timeout"
            note("timeout", state=st)
            log(f"[{cid}] web target still {st} after {wait:.0f}s: giving up this wait (`hctf arena status {cid}`; "
                "a `cleaned` attempt is revived by `hctf arena start`)")
            return out
        sleep(poll)
        try:
            nb = status(cid)
        except Exception:  # noqa: BLE001 - one failed poll: keep waiting
            nb = None
        if isinstance(nb, dict) and nb and not _transient_error(nb.get("error")):
            body = nb   # a transient error (rate_limited / control_unavailable) never overwrites the good body


# ------------------------------------------------------------------ orchestrator-side GM helpers (need hctf.*)

def gm_status(cid):
    from . import cli
    with cli.quiet():
        return cli.call(cid, "status", cid).get("body") or {}


def arena(cid, op="start", log=None):
    """The browser arena's op on `cid` (hctf/gm.py cmd_arena; always the local client: Homebase's inside proxy has no
    arena) -> its body. Logged into the mode's log.jsonl like any GM call."""
    from . import cli, remote
    # run_for_time only on the timed (dual-pool) routes: a Single Solve answers 409 timed_intent_not_available to it
    # (probe 2026-10-21), so a single's revive / kick never reached the target
    rft = False if op in ("start", "retry") and _timed_cid(cid) else None
    env = remote.gm_client().cmd_arena(op, cid, run_for_time=rft)
    try:
        cli.log(cid, f"arena-{op}", env)
    except Exception:  # noqa: BLE001 - logging only
        pass
    body = env.get("body") if isinstance(env.get("body"), dict) else {"error": f"arena http {env.get('http')}"}
    if log is not None:
        log(f"[{cid}] arena {op} -> HTTP {env.get('http')} {_result(body) or body.get('error') or ''}")
    return body


def arena_start(cid):
    return arena(cid, "start")


def arena_stop(cid):
    return arena(cid, "stop")


def kick(cid, n):
    """Orchestrator-side kick of a `preparing` start (kick_plan): public `retry` or arena `start`."""
    if kick_plan(cid, n) == "retry":
        from . import cli
        with cli.quiet():
            return cli.call(cid, "retry", cid).get("body") or {}
    return arena_start(cid)


def log_trace(cid, trace):
    """The wait's trace into the mode's log.jsonl (`web-trace`), when there was anything to wait for."""
    if not trace:
        return
    try:
        from . import cli
        cli.log(cid, "web-trace", {"http": 200, "body": {"trace": trace}})
    except Exception:  # noqa: BLE001 - logging only
        pass


def wait_ready(cid, body, log=print, wait=None):
    """Orchestrator form of await_target: GM status polls + arena revive + kicks of a stuck `preparing`."""
    trace = []
    try:
        return await_target(cid, body, gm_status, revive=arena_start, log=log, wait=wait, kick=kick, trace=trace)
    finally:
        log_trace(cid, trace)


def empty_artifacts(mode_dir, attempt):
    """A web attempt has no bytes: give it an empty artifacts/<ts>/ + latest (manifest names the attempt), so
    `hctf submit --from-solver`, the stop-at-correct snapshot and the regression case work as for any lane."""
    mode_dir = Path(mode_dir)
    latest = mode_dir / "artifacts" / "latest"
    try:
        if json.loads((latest / "manifest.json").read_text()).get("attempt") == attempt:
            return latest.resolve()
    except (OSError, ValueError):
        pass
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    d = mode_dir / "artifacts" / ts
    d.mkdir(parents=True, exist_ok=True)
    (d / "manifest.json").write_text(json.dumps({"ts": ts, "attempt": attempt, "files": [], "live_target": True},
                                                indent=2))
    if latest.is_symlink() or latest.exists():
        latest.unlink()
    latest.symlink_to(ts)
    return d


# ------------------------------------------------------------------ the team's live web target slots

_held = threading.local()


def _lock_path():
    from . import paths
    return paths.LOCKS / "web-target.lock"


@contextlib.contextmanager
def slot(key, log=print, path=None, poll=2.0, note_every=60.0, n=None):
    """Hold ONE of the team's `n` (default SLOTS) web target slots: flock on lock files <path>, <path>.1 .. <path>.n-1,
    shared by every thread of this process AND every other hctf process. Re-entrant per thread. A web chain holds one
    for its whole run (Chain._run), so at most n chains have live targets at once."""
    n = SLOTS if n is None else max(1, int(n))
    if not SLOT:
        yield
        return
    if getattr(_held, "n", 0):
        _held.n += 1
        try:
            yield
        finally:
            _held.n -= 1
        return
    import fcntl
    base = Path(path) if path else _lock_path()
    base.parent.mkdir(parents=True, exist_ok=True)
    files = [open(base if i == 0 else base.with_name(f"{base.name}.{i}"), "a+") for i in range(n)]
    f = None
    t0, noted = time.time(), 0.0
    try:
        while f is None:
            for cand in files:
                try:
                    fcntl.flock(cand, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    f = cand
                    break
                except BlockingIOError:
                    continue
            if f is None:
                if time.time() - noted >= note_every:
                    noted = time.time()
                    holders = []
                    for cand in files:
                        try:
                            holders.append(json.loads(Path(cand.name).read_text() or "{}").get("key") or "?")
                        except (OSError, ValueError):
                            holders.append("?")
                    log(f"[{key}] waiting for one of the team's {n} live web target slot(s) (held by "
                        f"{', '.join(holders)}; +{time.time() - t0:.0f}s)")
                time.sleep(poll)
        f.seek(0)
        f.truncate()
        f.write(json.dumps({"key": key, "pid": os.getpid(), "thread": threading.current_thread().name,
                            "since": time.strftime("%H:%M:%S")}))
        f.flush()
        if time.time() - t0 > 1:
            log(f"[{key}] web target slot acquired after {time.time() - t0:.0f}s")
        _held.n = 1
        try:
            yield
        finally:
            _held.n = 0
            try:
                f.seek(0)
                f.truncate()
                f.flush()
            except OSError:
                pass
            fcntl.flock(f, fcntl.LOCK_UN)
    finally:
        for cand in files:
            cand.close()


def after_stage(cid, ok, log=print):
    """A web stage ended. CORRECT: if the GM still shows OUR attempt active (it normally goes `completed` by itself),
    arena-stop it to free the team slot sooner. Not solved: say loudly that the live attempt still holds the slot
    (never stopped automatically -- it may hold progress)."""
    from . import cli
    try:
        st = gm_status(cid)
    except Exception:  # noqa: BLE001
        return
    live = _result(st) == "active" and bool(target_urls(st))
    if not live:
        return
    att = cli.attempt_id(st)
    if ok and STOP_AFTER_CORRECT and att and att in cli._correct_attempts(cli.cdir(cid) / "submissions.jsonl"):
        arena(cid, "stop", log=log)   # ours, and judged CORRECT: only frees the slot
    elif not ok:
        log(f"!!! [{cid}] web attempt {str(att)[:8]} is still ACTIVE and unsolved: it holds one of the team's live web "
            f"target slots; free it with `hctf arena stop {cid}` once given up")


# ------------------------------------------------------------------ regression cases

def _case_contract(case_dir):
    try:
        return json.loads((Path(case_dir) / "contract.json").read_text())
    except (OSError, ValueError):
        return None


def is_live_case(case_dir, lane=None):
    """A case recorded from a live-target attempt (marker, a contract naming targets/routes, or a web-lane solver)."""
    case_dir = Path(case_dir)
    if (case_dir / "live_target.json").exists():
        return True
    c = _case_contract(case_dir)
    return is_live_body(c) or (lane is not None and is_live_lane(lane))


def _mode_dir_for(sdir, mode):
    """The real challenge mode dir of a solver dir -- also for copies (.run/duel-dayNN/<chal>/solver, spec-dayNN)."""
    from . import paths
    sdir = Path(sdir)
    m = re.search(r"(day\d+)$", sdir.parent.parent.name)
    if not m:
        return None
    d = paths.CHALLENGES / m.group(1) / sdir.parent.name / mode
    return d if d.exists() else None


def _case_mode(case_dir, contract):
    from . import paths
    mode = (contract or {}).get("mode")
    if mode in paths.MODES:
        return mode
    name = Path(case_dir).name
    for m in ("time_trial", "mastery"):
        if m in name:
            return m
    return "single_solve"


def case_stale(case_dir, sdir, lane=None):
    """True = a live-target case that can no longer be replayed: its attempt is finished (CORRECT -> target 410) or
    superseded, or it never had a target. A case of the mode's CURRENT unsolved attempt (a failed timed variant being
    generalized while its target is still up) is replayable -> False. Non-live cases -> False."""
    if not is_live_case(case_dir, lane):
        return False
    mk = Path(case_dir) / "live_compound.json"
    if mk.exists():
        # a live compounding case (hctf.compound.web_live_check): an EARLIER challenge's open Time Trial attempt, kept
        # open for the generalize -- stale once re-solved or past the idle-stop age of its target
        try:
            m = json.loads(mk.read_text())
        except (OSError, ValueError):
            return True
        return bool(m.get("restored")) or time.time() - float(m.get("created") or 0) > LIVE_CASE_TTL
    c = _case_contract(case_dir) or {}
    from . import cli
    att = cli.attempt_id(c)
    if not att or not target_urls(c):
        return True
    mdir = _mode_dir_for(sdir, _case_mode(case_dir, c))
    if mdir is None:
        return True
    cur = None
    for f in ("last_timed.json", "start.json"):
        try:
            cur = cli.attempt_id(json.loads((mdir / f).read_text())) or cur
        except (OSError, ValueError):
            continue
        if cur:
            break
    if cur != att:
        return True
    try:
        return att in cli._correct_attempts(mdir / "submissions.jsonl")
    except Exception:  # noqa: BLE001
        return True
