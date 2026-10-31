#!/usr/bin/env python3
"""D31 harness-overhead fixes (critical-path seconds that are neither LLM nor GM), offline checks.

#1 the ready-watcher adopts the reuse race's verified snapshot (waits <= RACE_SNAP_WAIT s for its seed verify) instead
   of building + re-running its own and taking the new-id hold (script single CORRECT -> ready +5-7 s, D28-D30)
#2 a timed pre-start downloads every delivery in ONE wave (PRESTART_DL_WORKERS 8 -> 16; narrowed under 429 pressure)
#3 the timed runner's mode-lock wait (behind the pre-start) polls every 0.05 s instead of 0.5 s
#4 a runner pass ends the parallel live-answer worker without waiting for its exit (LIVE_END_ASYNC)
#5 the reuse race logs per-solver seconds
No GM, no workers: fakes only.

Run:  source bin/env.sh && python3 tests/test_d31_ovh.py      (exit 0 = all pass)
"""
import contextlib
import inspect
import fcntl
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, hb_timed, orchestrate  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {str(detail)[:400]}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


TD = Path(tempfile.mkdtemp(prefix="d31ovh-"))
said = []


def bare_chain(lane="script-analysis", base="script-analysis-day-31"):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base = lane, base
    ch.entries = {"single_solve": {"id": base}, "time_trial": {"id": f"{base}/time_trial"},
                  "mastery": {"id": f"{base}/mastery"}}
    ch.sdir = TD / "challenges" / "day31" / "scripting-x" / "solver"
    return ch


def later(dt, fn):
    t = threading.Thread(target=lambda: (time.sleep(dt), fn()), daemon=True)
    t.start()
    return t


# ---------------------------------------------------------------- #1 _race_snap_wait
with patched({(orchestrate, "say"): lambda m: said.append(m)}):
    snap = TD / "race-snap"
    # a) no race claim (the race never reached its submit): no wait at all
    ch = bare_chain()
    ch._race_done = threading.Event()
    t0 = time.time()
    got = ch._race_snap_wait(3.0)
    check("1a no race claim -> no wait, None", got is None and time.time() - t0 < 0.05, (got, time.time() - t0))

    # b) the race saw its own CORRECT and verifies its seed 0.4 s later -> the watcher gets the race snapshot
    ch = bare_chain()
    ch._race_done, ch._race_claim_by, ch._race_won_at = threading.Event(), ("cid", "att"), time.time()
    later(0.4, lambda: setattr(ch, "_race_snap", snap))
    t0 = time.time()
    got = ch._race_snap_wait(3.0)
    dt = time.time() - t0
    check("1b race verifying its seed -> its snapshot after ~0.4 s", got == snap and 0.3 <= dt < 1.0, (got, dt))
    check("1b says it adopted the race snapshot", any("adopted the reuse race's verified snapshot" in m for m in said),
          said[-3:])

    # c) the race holds the claim but has NOT seen the CORRECT (worker / answer-first won while it banks) -> bounded
    ch = bare_chain()
    ch._race_done, ch._race_claim_by = threading.Event(), ("cid", "att")
    t0 = time.time()
    got = ch._race_snap_wait(3.0)
    dt = time.time() - t0
    check("1c race still banking (no win seen) -> None within RACE_SNAP_NOTICE",
          got is None and dt <= orchestrate.RACE_SNAP_NOTICE + 0.15, (got, dt))

    # c2) ... but it notices the CORRECT inside the notice window -> waited for
    ch = bare_chain()
    ch._race_done, ch._race_claim_by = threading.Event(), ("cid", "att")
    later(0.1, lambda: setattr(ch, "_race_won_at", time.time()))
    later(0.5, lambda: setattr(ch, "_race_snap", snap))
    got = ch._race_snap_wait(3.0)
    check("1c2 race sees the CORRECT within the notice window -> its snapshot", got == snap, got)

    # d) the race already ended (no verified seed) -> immediate, nothing to wait for
    ch = bare_chain()
    ch._race_done, ch._race_claim_by, ch._race_won_at = threading.Event(), ("cid", "att"), time.time()
    ch._race_done.set()
    t0 = time.time()
    got = ch._race_snap_wait(3.0)
    check("1d race done -> immediate", got is None and time.time() - t0 < 0.05, (got, time.time() - t0))

    # e) the race ends WITHOUT a verified snapshot while we wait -> released by _race_done, not the timeout
    ch = bare_chain()
    ch._race_done, ch._race_claim_by, ch._race_won_at = threading.Event(), ("cid", "att"), time.time()
    later(0.3, ch._race_done.set)
    t0 = time.time()
    got = ch._race_snap_wait(3.0)
    dt = time.time() - t0
    check("1e race ends without a snapshot -> None at its end (not the 3 s cap)", got is None and dt < 0.8, (got, dt))

    # f) seed verify never finishes -> capped at the wait
    ch = bare_chain()
    ch._race_done, ch._race_claim_by, ch._race_won_at = threading.Event(), ("cid", "att"), time.time()
    t0 = time.time()
    got = ch._race_snap_wait(0.4)
    dt = time.time() - t0
    check("1f stuck seed verify -> None at the cap", got is None and 0.35 <= dt < 0.8, (got, dt))

    # g) kill switch: wait 0 -> whatever is there now
    ch = bare_chain()
    ch._race_done, ch._race_claim_by, ch._race_won_at = threading.Event(), ("cid", "att"), time.time()
    t0 = time.time()
    check("1g HCTF_RACE_SNAP_WAIT=0 -> no wait", ch._race_snap_wait(0) is None and time.time() - t0 < 0.05)

# 1h the watcher end to end: the race's CORRECT lands 0.4 s before its snapshot -> handed over the RACE snapshot, no
#    own snapshot + re-run, no new-id hold (D29 script: spec-day29/scripting-make-it-make-sense built at +1 s,
#    `new-id check` at +7.4 s)
calls = {"spec": 0, "newid": 0, "carry": 0, "prefetch": 0}
ch = bare_chain()
ch._race_done, ch._race_claim_by = threading.Event(), None
ch._launch_mtimes = {"solve.py": 1.0}
ch._solver_mtimes = lambda: {"solve.py": 1.0}
ch._submit_stamp = lambda cid, m: None
ch._newid_kick = lambda: None
ch._single_correct = lambda cid, why: None
ch._mark = lambda name, cid=None: None
ch._web_tt_kick = lambda: None
ch._record_single_method = lambda cid: None
ch._start_codify = lambda cid: None
ch._prepush_verified = lambda *a, **k: None
ch._spec_snapshot = lambda cid: (calls.__setitem__("spec", calls["spec"] + 1), TD / "own-snap")[1]
ch._newid_hold = lambda cid, s, r, d: (calls.__setitem__("newid", calls["newid"] + 1), s)[1]
ch._carry_hold = lambda cid, s, r, d: (calls.__setitem__("carry", calls["carry"] + 1), s)[1]
ch._prefetch_tt = lambda: calls.__setitem__("prefetch", calls["prefetch"] + 1)
complete = threading.Event()


def race_wins():
    ch._race_claim_by = ("cid", "att")   # the race reached its submit
    time.sleep(0.2)
    complete.set()                       # GM CORRECT recorded (the watcher may see it first)
    time.sleep(0.01)
    ch._race_won_at = time.time()
    time.sleep(0.4)                      # seed verify
    ch._race_snap = TD / "race-snap"
    ch._race_done.set()


ready, done = threading.Event(), threading.Event()
with patched({(orchestrate, "say"): lambda m: said.append(m), (cli, "is_complete"): lambda cid: complete.is_set(),
              (orchestrate, "PREPUSH_AT_STAMP", ): False, (orchestrate, "SPEC_POLL"): 0.02}):
    threading.Thread(target=race_wins, daemon=True).start()
    w = threading.Thread(target=ch._watch_ready, args=("cid", ready, done), daemon=True)
    w.start()
    ok = ready.wait(5)
    done.set()
    w.join(2)
check("1h watcher handed over", ok)
check("1h ... the race's snapshot (not its own)", getattr(ch, "_ready_snap", None) == TD / "race-snap",
      getattr(ch, "_ready_snap", None))
check("1h ... no own snapshot + re-run, no new-id hold", calls["spec"] == 0 and calls["newid"] == 0, calls)
check("1h ... carry-over check + TT pre-start still run", calls["carry"] == 1 and calls["prefetch"] == 1, calls)

# 1i same race, kill switch off -> the old path (own snapshot + new-id hold) still works
calls.update(spec=0, newid=0, carry=0, prefetch=0)
ch._race_snap = None
ch._race_won_at = None
ch._race_done, ch._race_claim_by = threading.Event(), None
complete.clear()
ready, done = threading.Event(), threading.Event()
with patched({(orchestrate, "say"): lambda m: said.append(m), (cli, "is_complete"): lambda cid: complete.is_set(),
              (orchestrate, "PREPUSH_AT_STAMP", ): False, (orchestrate, "SPEC_POLL"): 0.02,
              (orchestrate, "RACE_SNAP_WAIT"): 0.0}):
    threading.Thread(target=race_wins, daemon=True).start()
    w = threading.Thread(target=ch._watch_ready, args=("cid", ready, done), daemon=True)
    w.start()
    ok = ready.wait(5)
    done.set()
    w.join(2)
check("1i HCTF_RACE_SNAP_WAIT=0 -> old path: own snapshot + new-id hold",
      ok and calls["spec"] == 1 and calls["newid"] == 1 and ch._ready_snap == TD / "own-snap", (calls, ch._ready_snap))

# 1j the race marks _race_won_at at its CORRECT (source: before _single_correct / the seed verify)
src = inspect.getsource(orchestrate.Chain._race_submit)
check("1j _race_submit stamps _race_won_at before the seed verify",
      0 <= src.find("self._race_won_at = time.time()") < src.find("self._race_snapshot("), src[:0])
src = inspect.getsource(orchestrate.Chain._watch_ready)
check("1j _watch_ready asks _race_snap_wait before its own snapshot",
      0 <= src.find("_race_snap_wait(RACE_SNAP_WAIT)") < src.find("self._spec_snapshot(cid)"))

# ---------------------------------------------------------------- #2 pre-start download width
from hctf import ratebucket  # noqa: E402
check("2a default pre-start download width covers 14 deliveries in one wave", orchestrate.PRESTART_DL_WORKERS >= 14,
      orchestrate.PRESTART_DL_WORKERS)
with patched({(ratebucket, "pressure"): lambda: False}):
    check("2b no 429 pressure -> full width", orchestrate._prestart_dl_width() == orchestrate.PRESTART_DL_WORKERS)
with patched({(ratebucket, "pressure"): lambda: True}):
    w = orchestrate._prestart_dl_width()
    check("2c run-wide 429 pressure -> narrowed (>= 2)", 2 <= w < orchestrate.PRESTART_DL_WORKERS, w)
with patched({(ratebucket, "wave_width"): lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))}):
    check("2d governor failure -> fail-open to the configured width",
          orchestrate._prestart_dl_width() == orchestrate.PRESTART_DL_WORKERS)
src = inspect.getsource(orchestrate.Chain._prefetch_mode_start)
check("2e the pre-start's download pool uses _prestart_dl_width()", "_prestart_dl_width()" in src)

# 2f functional: 13 deliveries x 0.3 s each with the pre-start's pool -> one wave
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
plan = [(f"delivery {i}", f"cap{i}") for i in range(13)]
t0 = time.time()
with patched({(ratebucket, "pressure"): lambda: False}):
    with ThreadPoolExecutor(max_workers=max(1, min(orchestrate._prestart_dl_width(), len(plan)))) as ex:
        list(ex.map(lambda it: time.sleep(0.3), plan))
dt = time.time() - t0
check("2f 13 deliveries -> one wave (~0.3 s, was two waves ~0.6 s)", dt < 0.5, dt)

# ---------------------------------------------------------------- #3 mode-lock poll
check("3a mode-lock poll default 0.05 s", abs(hb_timed.MODE_LOCK_POLL - 0.05) < 1e-9, hb_timed.MODE_LOCK_POLL)
lockdir = TD / "tmp-timed"
lockdir.mkdir(parents=True, exist_ok=True)
with patched({(hb_timed, "_progress_path"): lambda cid: lockdir / "x_time_trial.progress.json"}):
    holder = open(lockdir / "x_time_trial.lock", "w")
    fcntl.flock(holder, fcntl.LOCK_EX)
    released = {}

    def release():
        released["t"] = time.time()
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()
    later(0.33, release)
    got = hb_timed._mode_lock("x/time_trial")
    lag = time.time() - released.get("t", time.time())
    check("3b runner gets the lock <= 0.12 s after the pre-start releases it (was up to 0.5 s)",
          got is not None and lag <= 0.12, lag)
    if got is not None:
        got.close()
    # the deadline path still returns None
    holder = open(lockdir / "x_time_trial.lock", "w")
    fcntl.flock(holder, fcntl.LOCK_EX)
    with patched({(hb_timed, "_runner_left"): lambda: 0.2}):
        t0 = time.time()
        got = hb_timed._mode_lock("x/time_trial")
        check("3c still held at the runner's deadline -> None", got is None and time.time() - t0 < 0.5,
              time.time() - t0)
    holder.close()


# ---------------------------------------------------------------- #4 async live end on a runner pass
class FakeLive:
    def __init__(self, block=1.0):
        self.stop_evt, self.block, self.finished = threading.Event(), block, threading.Event()

    def finish(self, wait=5.0):
        self.stop_evt.set()
        time.sleep(self.block)        # joining a worker thread still launching its claude process
        self.finished.set()
        return self


class FakePar:
    def __init__(self, live):
        self.live = live

    def close(self):
        return self.live


with patched({(orchestrate, "say"): lambda m: said.append(m)}):
    ch = bare_chain("mobile-android", "mobile-android-day-31")
    live = FakeLive()
    t0 = time.time()
    res = ch._web_par_settle("mobile-android-day-31/time_trial", FakePar(live), "correct")
    dt = time.time() - t0
    check("4a runner pass -> settle returns at once (not after the worker's exit)", res == "correct" and dt < 0.2, dt)
    check("4b ... the live worker is told to stop at once", live.stop_evt.is_set())
    check("4c ... and still reaped in the background", live.finished.wait(3))
    with patched({(orchestrate, "LIVE_END_ASYNC"): False}):
        live = FakeLive(0.5)
        t0 = time.time()
        ch._web_par_settle("mobile-android-day-31/time_trial", FakePar(live), "correct")
        check("4d HCTF_LIVE_END_ASYNC=0 -> the old blocking end", time.time() - t0 >= 0.45 and live.finished.is_set())
    # a runner that did NOT pass keeps the synchronous path (its verdict decides the mode)
    live = FakeLive(0.0)
    live._state = lambda: (False, False)
    live.passed = False
    res = ch._web_par_settle("mobile-android-day-31/time_trial", FakePar(live), "blocked")
    check("4e runner blocked + live not passed -> verdict unchanged", res == "blocked")
    check("4f _end_live_async(None) is a no-op", orchestrate.Chain._end_live_async(None) is None)

# ---------------------------------------------------------------- #5 race per-solver note
note = orchestrate._race_runs_note({Path("/x/challenges/day30/scripting-spill-the-beans/solver"): (1747, None, 0.52),
                                    Path("/x/challenges/day24/scripting-web-of-lies/solver"): (0, "timeout", 9.8)})
check("5a per-solver seconds in the race line",
      note == " [runs: scripting-spill-the-beans 0.5s, scripting-web-of-lies 9.8s ERR]", note)
check("5b no runs -> empty", orchestrate._race_runs_note({}) == "" and orchestrate._race_runs_note(None) == "")
check("5c malformed -> empty, never raises", orchestrate._race_runs_note({"a": None}) == "")

print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAILURE(S): ' + ', '.join(failures)}")
sys.exit(1 if failures else 0)
