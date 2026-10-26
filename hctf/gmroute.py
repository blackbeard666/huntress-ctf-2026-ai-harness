"""Measured GM routing for the ORCHESTRATOR's own calls (D24 #13): Homebase relay vs today's path, per op.

Only `status`, `start` and `submit` calls made inside the orchestrator process (remote.gm, once activate() ran in
orchestrate.run) -- never workers' `hctf submit`, never hb_timed / the timed runner (P1). The relay is one of
workers.hb_relays(): an `hb_daemon --stdio` channel on its own ssh connection, talking to the VM's in-network proxy
(remote.INSIDE_GM) with NO bearer token (event guidance: never enter credentials into Homebase).

Routing (every decision measured, never assumed -- 10-25: status 1.4 s from WSL vs 0.1 s on the VM):
  - per-op running averages (EWMA) for the relay and for today's path, refreshed by real calls and by a status
    calibration on both every CAL_S (15 s);
  - the relay is used only if its average < RATIO x today's - MARGIN (0.8 x local - 0.1 s), compared like with like
    (the op's own averages when both exist, else the status calibration's), and the request / the reply expected
    are <= MAX_BYTES (32 KB);
  - status: hedged -- both paths at once, the first judged reply wins (no side effects);
  - start: hedged too (D25: script Mastery's start sat 38 s on a relay channel that died mid-call) -- `start` RESUMES
    the live attempt (GM: "start always reconnects to the same attempt"), so a second one is safe. The path decide()
    prefers goes first, the other HEDGE_START_S later unless the first already failed (two near-simultaneous FIRST
    starts of a mode must not race the GM's attempt creation); the first judged reply wins, and differing attempt ids
    are logged `!!!`. A reply expected > MAX_BYTES -- sized from TODAY's status-time contract of that mode
    (<mode>/contract.json), else the lane's earlier start -- never takes the relay (one stdio channel: it would hold
    every reply queued behind it), so it goes today's path alone;
  - submit: relay; a failure BEFORE the request left (channel down / write failed) -> today's path; ANY failure after
    it was sent -> remote.Unreachable (outcome unknown). A submit is NEVER sent twice.
Kill switch HCTF_GM_RELAY=0: remote.gm never calls this module = exactly today's paths.

CLI (read-only; preflight runs it):  python3 -m hctf.gmroute calibrate [--n 5] [--cid ID] [--wait 60]
"""
import json
import os
import sys
import threading
import time

RELAY = os.environ.get("HCTF_GM_RELAY", "1") != "0"
RATIO = float(os.environ.get("HCTF_GM_RELAY_RATIO", "0.8"))
MARGIN = float(os.environ.get("HCTF_GM_RELAY_MARGIN", "0.1"))
MAX_BYTES = int(os.environ.get("HCTF_GM_RELAY_MAX_KB", "32")) * 1024
CAL_S = float(os.environ.get("HCTF_GM_RELAY_CAL_S", "15"))
# start hedging (D25 B2): the second path's head start. HCTF_GM_START_HEDGE=0 = the old relay-then-fallback start.
START_HEDGE = os.environ.get("HCTF_GM_START_HEDGE", "1") != "0"
HEDGE_START_S = float(os.environ.get("HCTF_GM_START_HEDGE_S", "1.5"))
ALPHA = 0.3                      # EWMA weight of the newest sample
OPS = ("status", "start", "submit")

_lock = threading.Lock()
_avg = {}                        # (op, "relay"|"local") -> [ewma seconds, samples]
_reply = {}                      # (op, shape key) -> last reply bytes (start: predicts the next start's size)
_state = {"active": False, "log": None, "cal": None, "last_cid": None, "decision": {}}


class _NotSent(Exception):
    """The relay never took the request: today's path is safe for any op (a submit too)."""


def _say(msg):
    log = _state.get("log")
    if log:
        try:
            log(msg)
        except Exception:  # noqa: BLE001
            pass


def record(op, path, seconds):
    with _lock:
        a = _avg.get((op, path))
        _avg[(op, path)] = [seconds, 1] if a is None else [a[0] + ALPHA * (seconds - a[0]), a[1] + 1]


def avg(op, path):
    with _lock:
        a = _avg.get((op, path))
    return None if a is None else a[0]


def _shape(cid):
    """`<lane>-day-NN-x/mastery` -> `<lane>/mastery`: start replies are about the same size across days per lane+mode."""
    import re
    m = re.match(r"(.+?)-day-\d+.*?(/(?:time_trial|mastery))?$", str(cid))
    return (m.group(1) + (m.group(2) or "")) if m else str(cid)


def _reply_bytes(env):
    try:
        return len(json.dumps(env.get("body"))) + len(env.get("text") or "")
    except (TypeError, ValueError):
        return 0


def _size_ok(args):
    op = args[0]
    if op == "submit":
        return len(str(args[2]) if len(args) > 2 else "") <= MAX_BYTES
    if op == "start" and len(args) > 1:
        cid = str(args[1])
        today = _contract_bytes(cid)
        if today is not None:
            return today <= MAX_BYTES        # this mode's own status-time contract: the best predictor there is
        with _lock:
            known = _reply.get(("start", _shape(cid)))
        if known is not None:
            return known <= MAX_BYTES
        from . import remote
        if "/" not in cid and remote._big_start(cid):
            return False
        return _earlier_start_bytes(cid) <= MAX_BYTES
    return True


def _contract_bytes(cid):
    """Bytes of TODAY's saved contract of this mode (<mode dir>/contract.json: the status-time contract, or the start
    body that replaced it) -- a start reply carries the same questions (+ answer_ids), within ~15 %. D25 script
    Mastery: 14,625 ids = 8.3 MB, while the lane's earlier Mastery start that _earlier_start_bytes saw was smaller /
    absent. None when the mode has no contract on disk yet (never creates the mode dir)."""
    from . import paths
    try:
        entry = paths.lookup(cid)
        if not entry:
            return None
        p = paths.CHALLENGES / entry["dir"] / paths.mode_of(cid) / "contract.json"
        return p.stat().st_size if p.exists() else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _earlier_start_bytes(cid):
    """Size of the newest earlier start.json of the same lane + mode (0 = none seen: assume small)."""
    from . import paths
    shape = _shape(cid)
    mode = paths.mode_of(cid)
    lane = shape.split("/")[0]
    best = (0, 0)
    try:
        for meta in paths.CHALLENGES.glob("day*/*/meta.json"):
            st = meta.parent / mode / "start.json"
            if not st.exists():
                continue
            m = json.loads(meta.read_text())
            if _shape(m.get("base") or "") != lane or str(m.get("base")) == paths.base_id(cid):
                continue
            best = max(best, (st.stat().st_mtime, st.stat().st_size))
    except (OSError, ValueError):
        return 0
    with _lock:
        _reply[("start", shape)] = best[1]
    return best[1]


def decide(op):
    """'relay' or 'local' from the averages; unmeasured -> 'local'."""
    r, l = avg(op, "relay"), avg(op, "local")
    if r is None or l is None:
        r, l = avg("status", "relay"), avg("status", "local")
    if r is None or l is None:
        return "local"
    return "relay" if r < RATIO * l - MARGIN else "local"


def _chan():
    from . import workers
    chans = workers.hb_relays(start=False)
    return min(chans, key=lambda c: c.busy) if chans else None


SLOW_S = float(os.environ.get("HCTF_GM_SLOW_TRANSPORT_S", "5"))


def note_slow(op, cid, env):
    """Flag a Homebase-carried GM call whose client time exceeds the GM's own by > SLOW_S (D26: 59.6 s vs 1.75 s went
    unnoticed until the post-mortem read client_elapsed out of log.jsonl)."""
    try:
        gap = float(env.get("client_elapsed") or 0) - float(env.get("elapsed") or 0)
    except (TypeError, ValueError):
        return
    if gap > SLOW_S:
        _say(f"!!! [gmroute] slow transport: {op} {cid} took {env.get('client_elapsed')}s on {env.get('transport')} "
             f"for a {env.get('elapsed')}s GM call ({_reply_bytes(env) // 1024} KB reply)")


def _relay_call(chan, args, timeout):
    """One GM call over a relay channel -> gm.py-shaped envelope (transport relay). _NotSent when the request never
    left this process; any other failure raises as is (the caller decides what it means per op)."""
    from . import workers
    kind, kw = str(args[0]), {"kind": str(args[0]), "cid": str(args[1])}
    if kind == "submit":
        try:
            kw["answers"] = json.loads(args[2])
        except (IndexError, ValueError, TypeError):
            raise _NotSent("submit answers not JSON") from None
    t0 = time.time()
    try:
        res = chan.call("gm", timeout=min(float(timeout), 60.0), **kw)
    except workers.DaemonError as e:
        if str(e).startswith(("daemon not running", "daemon write failed")):
            raise _NotSent(str(e)) from None
        raise
    env = {k: res.get(k) for k in ("http", "body", "text", "saved", "content_type", "elapsed", "retries", "slept")}
    env["saved"] = env["saved"] or []
    env["transport"] = f"relay{getattr(chan, 'k', '')}"
    env["client_elapsed"] = round(time.time() - t0, 3)
    if env.get("http") in (0, None):
        raise RuntimeError(f"relay: GM unreachable from the VM ({str(env.get('body'))[:120]})")
    note_slow(kind, kw["cid"], env)
    return env


def _timed(fn, op, path):
    t0 = time.time()
    env = fn()
    if isinstance(env, dict) and env.get("http") not in (0, None):
        record(op, path, time.time() - t0)
    return env


def _note_decision(op, how):
    if _state["decision"].get(op) != how:
        _state["decision"][op] = how
        r, l = avg(op, "relay") or avg("status", "relay"), avg(op, "local") or avg("status", "local")
        _say(f"[gmroute] {op} via {how} (relay {r if r is None else round(r, 2)}s vs local "
             f"{l if l is None else round(l, 2)}s)")


def _how(op):
    """The routing label _note_decision logs for op (the calibrator and call() must agree, or the line flaps)."""
    if op == "status":
        return "hedged"
    if op == "start" and START_HEDGE:
        return f"hedged, {decide(op)} first"
    return decide(op)


def _judged(env):
    return isinstance(env, dict) and env.get("http") not in (0, None, 429, 503)


def call(args, timeout, local_fn, public_fn=None):
    """remote.gm's hook for status / start / submit: the routed envelope. local_fn() = today's path, unchanged.
    public_fn() = the public GM client alone (never Homebase): a big start and the hedged start's non-relay leg use it.
    D26: local_fn sends `start` through the Homebase daemon, so the "local" leg shared the VPN with the relay and a
    9.5 MB Mastery reply crossed it at ~160 KB/s (59.6 s for a 1.75 s GM call)."""
    op = str(args[0])
    if len(args) > 1:
        _state["last_cid"] = str(args[1])
    pub = public_fn or local_fn
    chan = _chan()
    if chan is None or op not in OPS:
        return _timed(local_fn, op, "local")
    if op == "status":
        return _hedge(args, timeout, chan, local_fn)
    how = decide(op)
    if op == "start" and START_HEDGE:
        if not _size_ok(args):
            return _timed(pub, op, "local")   # a big reply never rides the relay or the daemon (not hedged either)
        _note_decision(op, _how(op))
        env = _hedge(args, timeout, chan, pub, op="start", first=how, lag=HEDGE_START_S)
        if str(env.get("transport") or "").startswith("relay"):
            with _lock:
                _reply[("start", _shape(args[1]))] = _reply_bytes(env)
        return env
    _note_decision(op, how)
    if how != "relay" or not _size_ok(args):
        return _timed(local_fn, op, "local")
    t0 = time.time()
    try:
        env = _relay_call(chan, args, timeout)
    except _NotSent as e:
        _say(f"[gmroute] {op} {args[1]}: relay did not take it ({str(e)[:80]}) -- today's path")
        return _timed(local_fn, op, "local")
    except Exception as e:  # noqa: BLE001
        record(op, "relay", max(time.time() - t0, 5.0))   # a failure costs: the average backs off the relay
        if op == "submit":
            from . import remote
            raise remote.Unreachable(f"submit via the GM relay: outcome unknown ({str(e)[:200]}) -- check `hctf "
                                     "status` before resubmitting (never resent)") from None
        _say(f"[gmroute] {op} {args[1]}: relay failed ({str(e)[:80]}) -- today's path (start resumes the attempt)")
        return _timed(local_fn, op, "local")
    record(op, "relay", time.time() - t0)
    if op == "start":
        with _lock:
            _reply[("start", _shape(args[1]))] = _reply_bytes(env)
    return env


def _hedge(args, timeout, chan, local_fn, op="status", first=None, lag=0.0):
    """`op` on both paths: the first judged non-404 reply wins; the other still lands in the averages. Idempotent ops
    only (status; start, which resumes the live attempt). lag > 0: the `first` path ('relay' | 'local') goes at once,
    the other after `lag` s -- or at once when the first one ends without a winner (raised / unjudged / 404)."""
    done, out, lock = threading.Event(), {}, threading.Lock()
    left = [2]
    first_over = threading.Event()

    def run(path, fn, delayed):
        if delayed and lag > 0:
            first_over.wait(lag)
            with lock:
                if "win" in out:          # the first path already won: never send the second request
                    left[0] -= 1
                    if left[0] == 0:
                        done.set()
                    return
        t0 = time.time()
        try:
            env = fn()
            err = None
        except Exception as e:  # noqa: BLE001
            env, err = None, e
        if _judged(env):
            record(op, path, time.time() - t0)
        elif err is not None and path == "relay" and op != "status":
            record(op, "relay", max(time.time() - t0, 5.0))   # a failure costs: the average backs off the relay
        with lock:
            left[0] -= 1
            # a 404 never wins alone: the release probe (status on the day's warmups id) reads 404 as "not yet" -- a
            # proxy that lags the drop must not mask the other path's 409/200. Both 404 -> 404 once both answered.
            if _judged(env) and env.get("http") != 404 and "win" not in out:
                out["win"] = env
                done.set()
            elif _judged(env) and "win" in out and op == "start":
                a, b = _attempt_of(out["win"]), _attempt_of(env)
                if a and b and a != b:
                    _say(f"!!! [gmroute] start {args[1]}: the two paths returned different attempts ({a[:8]} won, "
                         f"{b[:8]} on {path}) -- check `hctf status`")
            elif env is not None:
                out.setdefault(path, env)
            elif err is not None:
                out.setdefault(f"{path}_err", err)
            if left[0] == 0:
                done.set()
        if not delayed:
            first_over.set()

    lead = first if first in ("relay", "local") else "relay"
    fns = {"relay": lambda: _relay_call(chan, args, timeout), "local": local_fn}
    for path in (lead, "local" if lead == "relay" else "relay"):
        threading.Thread(target=run, args=(path, fns[path], path != lead and lag > 0), daemon=True,
                         name=f"gm-hedge-{op}-{path}").start()
    done.wait(timeout + lag + 5)
    with lock:
        if "win" in out:
            return out["win"]
        if "local" in out:
            return out["local"]
        if "relay" in out:
            return out["relay"]
        err = out.get("local_err") or out.get("relay_err")
    if err is not None:
        raise err
    from . import remote
    raise remote.Unreachable(f"{op}: neither the relay nor the local GM answered in time")


def _attempt_of(env):
    body = env.get("body") if isinstance(env, dict) else None
    if not isinstance(body, dict):
        return None
    v = body.get("attempt_id") or body.get("attempt")
    return str(v.get("id") if isinstance(v, dict) else v) if v else None


def calibrate_once(cid=None):
    """One status on each path (sequential: neither queues behind the other) -> (relay s | None, local s | None)."""
    from . import remote
    cid = cid or _state.get("last_cid") or "warmups-day-01"
    out = []
    chan = _chan()
    for path in ("relay", "local"):
        t0 = time.time()
        try:
            if path == "relay":
                if chan is None:
                    out.append(None)
                    continue
                env = _relay_call(chan, ["status", cid], 15)
            else:
                env = remote._gm_local(["status", cid], 15)
        except Exception:  # noqa: BLE001
            out.append(None)
            continue
        dt = time.time() - t0
        if _judged(env):
            record("status", path, dt)
            out.append(dt)
        else:
            out.append(None)
    return tuple(out)


def _calibrator():
    while _state["active"]:
        try:
            if _chan() is not None:
                calibrate_once()
                _note_decision("status", "hedged")
                for op in ("start", "submit"):
                    _note_decision(op, _how(op))
        except Exception as e:  # noqa: BLE001
            _say(f"[gmroute] calibration note: {str(e)[:120]}")
        time.sleep(CAL_S)


def active():
    return RELAY and _state["active"]


def activate(log=None):
    """Called once by orchestrate.run(): this process's own status/start/submit become routable. No-op when the relay
    is off, Homebase is off, or this is a replay (stand-in GM)."""
    from . import remote, workers
    if not RELAY or _state["active"] or not remote._public_gm() or not workers.AUTO_HOMEBASE:
        return False
    _state.update(active=True, log=log)
    workers.hb_relays(log or print)
    t = threading.Thread(target=_calibrator, daemon=True, name="gm-route-cal")
    _state["cal"] = t
    t.start()
    _say(f"[gmroute] on: relay channels starting; status hedged, "
         f"{'start hedged (the faster path first, the other ' + format(HEDGE_START_S, 'g') + ' s later), submit' if START_HEDGE else 'start/submit'}"
         f" via the relay only when its average < {RATIO:g} x local - {MARGIN:g}s and <= {MAX_BYTES // 1024} KB "
         "(HCTF_GM_RELAY=0 = off)")
    return True


def deactivate():
    _state["active"] = False


def summary():
    rows = []
    for op in OPS:
        r, l = avg(op, "relay"), avg(op, "local")
        rows.append(f"{op}: relay {'-' if r is None else f'{r:.2f}s'} local {'-' if l is None else f'{l:.2f}s'} "
                    f"-> {_how(op)}")
    return "; ".join(rows)


def _cli(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="python3 -m hctf.gmroute")
    ap.add_argument("cmd", choices=["calibrate"])
    ap.add_argument("--n", type=int, default=5, help="status rounds per path")
    ap.add_argument("--cid", default=None, help="challenge id the status calls name (default warmups-day-01)")
    ap.add_argument("--wait", type=float, default=60, help="seconds to wait for a relay channel")
    a = ap.parse_args(argv)
    from . import remote, workers
    if not RELAY:
        print("SKIP relay off (HCTF_GM_RELAY=0): every GM call takes today's path")
        return 0
    if not remote._public_gm():
        print("SKIP not the public GM (replay stand-in): the relay is never used")
        return 0
    # one probe, no provisioning / attempt daemon / VM bench (the run's health thread does those): read-only
    if not remote.probe(timeout=20):
        print("WARN Homebase SSH not answering: no relay -- the run uses today's paths")
        return 0
    workers._hb.update(ok=True, provisioned=True, checked=time.time())
    workers.hb_relays(lambda m: print(m, flush=True), health=False)
    end = time.time() + a.wait
    while not workers.hb_relays(start=False) and time.time() < end:
        time.sleep(0.5)
    if not workers.hb_relays(start=False):
        print(f"WARN no relay channel within {a.wait:g}s (Homebase off / SSH failing): the run uses today's paths")
        return 0
    rel, loc = [], []
    for _ in range(max(1, a.n)):
        r, l = calibrate_once(a.cid)
        rel += [r] if r is not None else []
        loc += [l] if l is not None else []
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else None  # noqa: E731
    r, l = med(rel), med(loc)
    if r is None or l is None:
        print(f"WARN calibration incomplete (relay {len(rel)}/{a.n}, local {len(loc)}/{a.n} answered): today's paths")
        return 0
    verdict = "relay" if r < RATIO * l - MARGIN else "local"
    print(f"OK status p50 relay {r:.2f}s vs local {l:.2f}s over {a.n} rounds -> start/submit via {verdict} "
          f"(threshold {RATIO:g} x local - {MARGIN:g}s = {RATIO * l - MARGIN:.2f}s); status hedged")
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
