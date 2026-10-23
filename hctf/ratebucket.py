"""Account-wide GM request governor — the one thing every worker's GM traffic shares.

The Game Master request bucket is shared across every concurrent worker/process on the account
(the reviewer's loudest lesson, and our own: "29 concurrent agents -> everything throttled; cut to
6 and serialise"). Until now each process backed off a 429 on its own (gm.py's retry loop is
thread-local) and narrowed its fan-out on its own (grouptest, labels.resolve) — so one worker
hitting the ceiling told the others nothing. This module is the shared signal:

  admit()      record a GM request in the rolling window; if a hard cap is set and exceeded, wait
               briefly (bounded) before proceeding. Call once per GM API request.
  note_429()   a 429/503-rate-limit was seen anywhere -> raise the shared "pressure" flag.
  pressure()   True while that flag is hot -> every worker's fan-out should narrow NOW.
  wave_width() narrow a fan-out width while pressure is hot (used by grouptest / labels / downloads).

Design rules that keep this safe to run in a live competition:
  * FAIL-OPEN, ALWAYS. If the lock/state file is unavailable, or a hard cap can't be satisfied
    within the bounded wait, the call PROCEEDS anyway and lets gm.py's existing 429 backoff take
    over. The governor may add latency; it can never stall the run.
  * The limiter is a rolling-window request-RATE cap, not an in-flight semaphore: a crashed
    worker's entries simply age out of the window, so nothing leaks and nothing needs releasing.
  * The lock is held only for a tiny read-modify-write — never across a sleep.
  * TARGET-HOST web fetches never call this (they don't touch the GM bucket); only hctf/gm.py's
    and hb_timed's GM-API requests do.

Everything is tunable with HCTF_GM_* env vars. The hard numeric cap ships OFF by default
(HCTF_GM_RATE_MAX=0): the real ceiling is risky to guess and a too-low value only adds latency, so
the operator sets it from a measured baseline (`hctf cost` gm429). The pressure narrowing — the
part that actually coordinates the run — is safe and on by default.
"""
import json
import os
import random
import time
from pathlib import Path

try:
    import fcntl
except ImportError:          # non-POSIX: governor disables itself (fail-open)
    fcntl = None

_RUN = Path(__file__).resolve().parent.parent / ".run"
_STATE = _RUN / "gm_governor.json"

WINDOW = float(os.environ.get("HCTF_GM_RATE_WINDOW", "8"))       # rolling window, seconds
MAX = int(os.environ.get("HCTF_GM_RATE_MAX", "0"))              # requests/window across ALL workers; 0 = no hard cap
PRESSURE_TTL = float(os.environ.get("HCTF_GM_PRESSURE_TTL", "6"))   # how long a 429 keeps fan-out narrowed
ADMIT_MAX_WAIT = float(os.environ.get("HCTF_GM_ADMIT_MAX_WAIT", "3"))   # bounded fail-open wait when over the cap


def _on():
    return fcntl is not None and os.environ.get("HCTF_GM_GOVERNOR", "1") != "0"


class _Locked:
    """Open .run/gm_governor.json, flock it exclusively, yield its parsed state. Fail-open: yields None
    (the caller then does nothing) if anything about the lock/file fails."""
    def __init__(self):
        self.fh = None

    def __enter__(self):
        if not _on():
            return None, None
        try:
            _RUN.mkdir(parents=True, exist_ok=True)
            self.fh = open(_STATE, "a+")
            fcntl.flock(self.fh, fcntl.LOCK_EX)
            self.fh.seek(0)
            try:
                st = json.loads(self.fh.read() or "{}")
            except ValueError:
                st = {}
            return self.fh, st
        except OSError:
            if self.fh:
                try:
                    self.fh.close()
                except OSError:
                    pass
                self.fh = None
            return None, None

    def __exit__(self, *exc):
        if self.fh:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                self.fh.close()
            except OSError:
                pass
            self.fh = None
        return False


def _save(fh, st):
    fh.seek(0)
    fh.truncate()
    fh.write(json.dumps(st))
    fh.flush()


def admit():
    """Record one GM API request in the shared rolling window. With a hard cap set (HCTF_GM_RATE_MAX>0),
    wait — bounded by ADMIT_MAX_WAIT, then proceed anyway — while the window is full. Cumulative wait stats
    (reqs, waited, waited_s) are kept in the state file for post-run tuning (`hctf cost` / manual read)."""
    if not _on() or MAX <= 0:
        return            # no hard cap set -> nothing to enforce; skip the per-call lock entirely (cap-off = free).
    t_enter = time.time()
    deadline = t_enter + ADMIT_MAX_WAIT
    while True:
        over = False
        with _Locked() as (fh, st):
            if fh is None:
                return                               # fail-open
            now = time.time()
            ts = [t for t in st.get("ts", []) if now - t < WINDOW]
            if MAX > 0 and len(ts) >= MAX and now < deadline:
                over = True                          # don't record yet; back off and recheck
                st["ts"] = ts
            else:
                ts.append(now)
                st["ts"] = ts
                st["reqs"] = st.get("reqs", 0) + 1
                waited = now - t_enter
                if waited > 0.01:
                    st["waited"] = st.get("waited", 0) + 1
                    st["waited_s"] = round(st.get("waited_s", 0.0) + waited, 3)
            _save(fh, st)
        if not over:
            return
        time.sleep(0.05 + random.random() * 0.15)


def note_429():
    """A rate-limit (429/503 rate_limited) was seen on a GM call anywhere -> narrow the whole run's fan-out."""
    if not _on():
        return
    with _Locked() as (fh, st):
        if fh is None:
            return
        st["pressure"] = time.time()
        _save(fh, st)


def pressure():
    """True while any worker's recent 429 is still 'hot' -> fan-out helpers should run narrower waves."""
    if not _on():
        return False
    with _Locked() as (fh, st):
        if fh is None:
            return False
        p = st.get("pressure")
    return bool(p) and (time.time() - float(p)) < PRESSURE_TTL


def wave_width(base, floor=2):
    """Narrow a fan-out width while the account is under throttle pressure; otherwise unchanged
    (so clean runs are never slowed)."""
    try:
        base = int(base)
    except (TypeError, ValueError):
        return base
    if base <= floor or not pressure():
        return base
    return max(floor, base // 2)
