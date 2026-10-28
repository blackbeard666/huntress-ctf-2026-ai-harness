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
  - status: hedged -- both paths at once, the first judged reply wins (no side effects) -- unless the reply is
    known/predicted > STATUS_HEDGE_MAX (200 KB: this cid's last status reply, else TODAY's <mode>/contract.json, else
    the lane's earlier start of the mode), which goes today's path alone (D28: a 3.6 MB binary Mastery status held
    relay1 for 6.4 s; a 10 MB script status starved channel 0's pings until the keeper closed it);
  - per-channel demotion: a relay call whose client time exceeds the GM's by > SLOW_S (or that timed out) keeps NEW
    calls off that channel for DEMOTE_S; so does a missed keeper ping; all channels demoted -> today's path;
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
from pathlib import Path

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
# D28 #20 relay hygiene. HCTF_GM_STATUS_HEDGE_MAX_KB=0: every status hedged (old). HCTF_GM_RELAY_DEMOTE_S=0: no
# per-channel demotion (the least-busy live channel, old).
STATUS_HEDGE_MAX = int(float(os.environ.get("HCTF_GM_STATUS_HEDGE_MAX_KB", "200")) * 1024)
DEMOTE_S = float(os.environ.get("HCTF_GM_RELAY_DEMOTE_S", "30"))
# Reply-size predictors read every past challenge's meta.json / start.json: ~0.1 s idle, 5-8 s per start under the drop's
# GIL convoy (measured with 3 CPU-bound threads). The meta rows are read once (activate() prewarms them before the drop)
# and each (lane, mode) answer is kept. HCTF_GM_SIZE_MEMO=0 = scan every time (old).
SIZE_MEMO = os.environ.get("HCTF_GM_SIZE_MEMO", "1") != "0"

_lock = threading.Lock()
_avg = {}                        # (op, "relay"|"local") -> [ewma seconds, samples]
_reply = {}                      # (op, shape key) -> last reply bytes (start: predicts the next start's size;
                                 # ("status", cid): that cid's last status reply)
_demoted = {}                    # relay channel k -> time.time() until which new calls avoid it
_meta_memo = {}                  # challenges root -> [row] (see _meta_rows)
_earlier_memo = {}               # (lane shape, mode, excluded base | None) -> bytes
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


_meta_lock = threading.Lock()


def _meta_rows(root):
    """[{"day", "lane", "base", "shape", "dir"}] of every <root>/day*/*/meta.json, read once per root (SIZE_MEMO): a
    past day's meta never changes, and today's dirs (created after the drop) are never an EARLIER day's."""
    import re
    root = Path(root)
    key = str(root)
    with _meta_lock:
        if SIZE_MEMO and key in _meta_memo:
            return _meta_memo[key]
        rows = []
        for meta in root.glob("day*/*/meta.json"):
            dm = re.match(r"day(\d+)$", meta.parent.parent.name)
            try:
                m = json.loads(meta.read_text())
            except (OSError, ValueError):
                continue
            if not isinstance(m, dict):
                continue
            rows.append({"day": int(dm.group(1)) if dm else -1, "lane": m.get("lane"), "base": str(m.get("base") or ""),
                         "shape": _shape(m.get("base") or ""), "dir": meta.parent})
        rows.sort(key=lambda r: (r["day"], str(r["dir"])), reverse=True)
        if SIZE_MEMO:
            _meta_memo[key] = rows
        return rows


def _earlier_start_bytes(cid):
    """Size of the newest earlier start.json of the same lane + mode (0 = none seen: assume small)."""
    from . import paths
    shape = _shape(cid)
    mode = paths.mode_of(cid)
    lane = shape.split("/")[0]
    base = paths.base_id(cid)
    try:
        rows = [r for r in _meta_rows(paths.CHALLENGES) if r["shape"] == lane]
    except OSError:
        return 0
    excl = base if any(r["base"] == base for r in rows) else None   # today's new base has no row: same answer as None
    mk = (lane, mode, excl)
    with _lock:
        hit = _earlier_memo.get(mk) if SIZE_MEMO else None
    if hit is None:
        best = (0, 0)
        for r in rows:
            if r["base"] == base:
                continue
            try:
                st = (r["dir"] / mode / "start.json").stat()
            except OSError:
                continue
            best = max(best, (st.st_mtime, st.st_size))
        hit = best[1]
        with _lock:
            _earlier_memo[mk] = hit
    with _lock:
        _reply[("start", shape)] = hit
    return hit


def prewarm_sizes(log=None):
    """Before the drop (activate's thread): read the meta rows once and answer _earlier_start_bytes for every lane x
    mode, so no start / status at the drop scans the challenge tree. Best effort. -> seconds taken."""
    from . import paths, remote
    t0 = time.time()
    try:
        rows = _meta_rows(paths.CHALLENGES)
        remote._meta_rows_prewarm()
        for lane in sorted({r["shape"] for r in rows if r["shape"]}):
            for mode in ("single_solve", "time_trial", "mastery"):
                mk = (lane, mode, None)
                with _lock:
                    if mk in _earlier_memo:
                        continue
                best = (0, 0)
                for r in rows:
                    if r["shape"] != lane:
                        continue
                    try:
                        st = (r["dir"] / mode / "start.json").stat()
                    except OSError:
                        continue
                    best = max(best, (st.st_mtime, st.st_size))
                with _lock:
                    _earlier_memo[mk] = best[1]
    except Exception as e:  # noqa: BLE001 - the drop then scans as before
        if log:
            log(f"[gmroute] size prewarm note: {str(e)[:120]}")
    return time.time() - t0


def _approx_bytes(env):
    """_reply_bytes without serializing a multi-MB body: > 2000 questions (D28: ~0.9 KB each) is counted ~1 KB each."""
    body = env.get("body") if isinstance(env, dict) else None
    qs = body.get("questions") if isinstance(body, dict) else None
    if isinstance(qs, list) and len(qs) > 2000:
        return len(qs) * 1024
    return _reply_bytes(env) if isinstance(env, dict) else 0


# rehearsal D28 fair run: binary single submits (292 KB replies) took 8.8-14.1 s each on relay1 for 0.3-0.8 s GM calls; a
# submit reply tracks the mode's contract size (binary 340 KB contract -> 292 KB reply, script 852 KB) -> a submit whose
# contract (or this lane+mode's last submit reply) exceeds this many KB never rides a relay channel. 0 = off.
SUBMIT_RELAY_MAX = float(os.environ.get("HCTF_GM_SUBMIT_RELAY_MAX_KB", "200")) * 1024


def _submit_big(args):
    if SUBMIT_RELAY_MAX <= 0 or len(args) < 2:
        return False
    cid = str(args[1])
    with _lock:
        learned = _reply.get(("submit", _shape(cid))) or 0
    return max(learned, _contract_bytes(cid) or 0) > SUBMIT_RELAY_MAX


def _status_big(args):
    """True when this status reply is known / predicted > STATUS_HEDGE_MAX: then the relay leg is not sent. The LARGEST
    known size wins: a short 409 status/start reply (prerequisite_required before the Time Trial passes) must not mask
    the mode's multi-MB contract -- rehearsal D28 fair run: three 4.7 MB binary Mastery statuses rode the relay, ~11 s each."""
    if STATUS_HEDGE_MAX <= 0 or len(args) < 2:
        return False
    cid = str(args[1])
    with _lock:
        last = _reply.get(("status", cid))
        known = _reply.get(("start", _shape(cid))) if "/" in cid else None
    sizes = [last or 0, _contract_bytes(cid) or 0, known or 0]
    if "/" in cid:            # a Single's status before its start is a short 409; its contract.json appears with start
        sizes.append(_earlier_start_bytes(cid))
    return max(sizes) > STATUS_HEDGE_MAX


def _note_status_bytes(args, env):
    if len(args) > 1 and isinstance(env, dict) and env.get("http") not in (0, None):
        n = _approx_bytes(env)
        with _lock:
            _reply[("status", str(args[1]))] = n


def decide(op):
    """'relay' or 'local' from the averages; unmeasured -> 'local'."""
    r, l = avg(op, "relay"), avg(op, "local")
    if r is None or l is None:
        r, l = avg("status", "relay"), avg("status", "local")
    if r is None or l is None:
        return "local"
    return "relay" if r < RATIO * l - MARGIN else "local"


def _chan():
    """The least-busy live relay channel that is not demoted (recent slow call / timeout) and did not miss its last
    keeper ping; None (= today's path) when there is none."""
    from . import workers
    chans = workers.hb_relays(start=False)
    if not chans:
        return None
    if DEMOTE_S > 0:
        now = time.time()
        chans = [c for c in chans if _demoted.get(getattr(c, "k", None), 0.0) <= now and not getattr(c, "misses", 0)]
        if not chans:
            return None
    return min(chans, key=lambda c: c.busy)


def demote(chan, why=""):
    """Keep new calls off `chan` for DEMOTE_S (logged once per demotion)."""
    if DEMOTE_S <= 0 or chan is None:
        return
    k = getattr(chan, "k", None)
    now = time.time()
    with _lock:
        was = _demoted.get(k, 0.0) > now
        _demoted[k] = now + DEMOTE_S
    if not was:
        _say(f"[gmroute] relay channel {k} demoted for {DEMOTE_S:g}s ({why[:120]}) -- new calls take the other "
             "channel / today's path")


SLOW_S = float(os.environ.get("HCTF_GM_SLOW_TRANSPORT_S", "5"))
START_MARK_S = float(os.environ.get("HCTF_GM_START_MARK_S", "1"))    # log a start's reply-size check past this
START_SLOW_S = float(os.environ.get("HCTF_GM_START_SLOW_S", "5"))    # log a hedged start's leg timings past this


def _lag_note():
    try:
        from . import workers
        return workers._lag_note()
    except Exception:  # noqa: BLE001
        return ""


def _gap(env):
    try:
        return float(env.get("client_elapsed") or 0) - float(env.get("elapsed") or 0)
    except (TypeError, ValueError, AttributeError):
        return 0.0


def note_slow(op, cid, env, lost_to=None):
    """Flag a Homebase-carried GM call whose client time exceeds the GM's own by > SLOW_S (D26: 59.6 s vs 1.75 s went
    unnoticed until the post-mortem read client_elapsed out of log.jsonl). lost_to: the hedge leg that answered first
    ('local') -- then nothing waited on this one: logged as the losing leg, without the `!!!` alarm (D28 21:00:29)."""
    if _gap(env) > SLOW_S:
        nbytes = _approx_bytes(env)
        if lost_to:
            _say(f"[gmroute] slow transport on the LOSING hedge leg (the {lost_to} reply was used; nothing waited on "
                 f"this one): {op} {cid} took {env.get('client_elapsed')}s on {env.get('transport')} for a "
                 f"{env.get('elapsed')}s GM call ({nbytes // 1024} KB reply)")
            return
        _say(f"!!! [gmroute] slow transport: {op} {cid} took {env.get('client_elapsed')}s on {env.get('transport')} "
             f"for a {env.get('elapsed')}s GM call ({nbytes // 1024} KB reply)")
        if op == "submit":   # P2-H: a slow submit is usually a large reply on the daemon's one channel -> route the
            try:             # NEXT submit on this lane+mode public (remote._submit_off_hb). No-op unless enabled.
                from . import remote
                remote.note_big_submit(cid, nbytes)
            except Exception:  # noqa: BLE001 - learning only
                pass


def _relay_call(chan, args, timeout, note=True):
    """One GM call over a relay channel -> gm.py-shaped envelope (transport relay). _NotSent when the request never
    left this process; any other failure raises as is (the caller decides what it means per op). A slow transport or
    a timeout demotes the channel (DEMOTE_S). note=False: the caller (a hedge) logs a slow transport itself, knowing
    whether this leg's reply was the one used."""
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
        if "timed out" in str(e):
            demote(chan, f"{kind} {kw['cid']} timed out after {time.time() - t0:.1f}s")
        raise
    env = {k: res.get(k) for k in ("http", "body", "text", "saved", "content_type", "elapsed", "retries", "slept")}
    env["saved"] = env["saved"] or []
    env["transport"] = f"relay{getattr(chan, 'k', '')}"
    env["client_elapsed"] = round(time.time() - t0, 3)
    if env.get("http") in (0, None):
        raise RuntimeError(f"relay: GM unreachable from the VM ({str(env.get('body'))[:120]})")
    if _gap(env) > SLOW_S:
        demote(chan, f"{kind} {kw['cid']}: {env['client_elapsed']}s for a {env.get('elapsed')}s GM call")
    if note:
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
        if _status_big(args):    # a multi-MB contract never rides (and blocks) a relay channel's one stdio stream
            env = _timed(local_fn, op, "local")
        else:
            env = _hedge(args, timeout, chan, local_fn)
        _note_status_bytes(args, env)
        return env
    how = decide(op)
    if op == "start" and START_HEDGE:
        t_size = time.time()
        small = _size_ok(args)
        t_size = time.time() - t_size
        if t_size >= START_MARK_S:   # D28 #16: ~15 s passed before the breach single's start request left
            _say(f"[gmroute] start {args[1]}: reply-size check took {t_size:.1f}s before the request{_lag_note()}")
        if not small:
            return _timed(pub, op, "local")   # a big reply never rides the relay or the daemon (not hedged either)
        _note_decision(op, _how(op))
        marks = {}
        t_h = time.time()
        env = _hedge(args, timeout, chan, pub, op="start", first=how, lag=HEDGE_START_S, marks=marks)
        if time.time() - t_h >= START_SLOW_S:   # where a slow start went: which leg, when sent, how long each took
            legs = ", ".join(f"{k} sent +{v[0]:.1f}s took {v[1]:.1f}s" for k, v in sorted(marks.items()))
            _say(f"[gmroute] slow start {args[1]}: {time.time() - t_h:.1f}s hedged ({how} first on "
                 f"relay{getattr(chan, 'k', '?')} busy {getattr(chan, 'busy', '?')}; {legs or 'no leg finished'}; "
                 f"won by {env.get('transport')}){_lag_note()}")
        if str(env.get("transport") or "").startswith("relay"):
            with _lock:
                _reply[("start", _shape(args[1]))] = _reply_bytes(env)
        return env
    _note_decision(op, how)
    if how != "relay" or not _size_ok(args) or (op == "submit" and _submit_big(args)):
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
    if op in ("start", "submit"):
        with _lock:
            _reply[(op, _shape(args[1]))] = _reply_bytes(env)
    return env


def _hedge(args, timeout, chan, local_fn, op="status", first=None, lag=0.0, marks=None):
    """`op` on both paths: the first judged non-404 reply wins; the other still lands in the averages. Idempotent ops
    only (status; start, which resumes the live attempt). lag > 0: the `first` path ('relay' | 'local') goes at once,
    the other after `lag` s -- or at once when the first one ends without a winner (raised / unjudged / 404).
    marks: {path: (sent +s, took s)} filled in as each leg ends (timing attribution)."""
    done, out, lock = threading.Event(), {}, threading.Lock()
    left = [2]
    first_over = threading.Event()
    t_h0 = time.time()

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
        if marks is not None:
            marks[path] = (t0 - t_h0, time.time() - t0)
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
                out["win_path"] = path
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
            won = out.get("win") is env
            winner = out.get("win_path")
        if path == "relay" and isinstance(env, dict):
            # only the leg whose reply was used (or that everyone waited on) raises the `!!!` alarm
            note_slow(op, str(args[1]) if len(args) > 1 else "", env,
                      lost_to=None if won or winner is None else winner)
        if not delayed:
            first_over.set()

    lead = first if first in ("relay", "local") else "relay"
    fns = {"relay": lambda: _relay_call(chan, args, timeout, note=False), "local": local_fn}
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
    from . import procgov, remote, workers
    procgov.start_lag_probe()   # D28 #15: scheduling-lag probe (cheap; diagnostics for the drop's GIL convoy)
    if not RELAY or _state["active"] or not remote._public_gm() or not workers.AUTO_HOMEBASE:
        return False
    _state.update(active=True, log=log)

    def prewarm():   # before the drop: the reply-size predictors' disk scans + the kickoff's label hints
        took = prewarm_sizes(log)
        workers.prewarm_kickoff_caches(log)
        if took > 2 and log:
            log(f"[gmroute] reply-size predictors prewarmed in {took:.1f}s")
    threading.Thread(target=prewarm, daemon=True, name="gm-route-prewarm").start()
    workers.hb_relays(log or print)
    t = threading.Thread(target=_calibrator, daemon=True, name="gm-route-cal")
    _state["cal"] = t
    t.start()
    _say(f"[gmroute] on: relay channels starting; status hedged (not > {STATUS_HEDGE_MAX // 1024} KB), "
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
