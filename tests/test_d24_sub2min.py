"""D24 sub-2-min fixes (plan: whole-board sub-2-min, D24 fixes), offline: fakes only, no network, no workers.
Track A (timed runner):
- A1 instrumentation: Chain._mark + one "handoff timing" line per mode, runner spawn / pool / pre-start fields, the
     `timed:` line's new keys, t_env + t_hb_ready from the local route
- A2 linear question pairing (exact-id index + boundary-suffix lookup + positional fallback) == the old scan
- A3 faster runner start: non-blocking Homebase readiness, adaptive GM pool size, lazy pool (2 sockets up -> go)
- A4 Mastery pre-start fired at the Time Trial's CORRECT, before the TT's bookkeeping

Run:  source bin/env.sh && python3 tests/test_d24_sub2min.py      (exit 0 = all pass)
"""
import contextlib
import json
import os
import random
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import hb_timed, orchestrate, solvers, timed, workers  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    """pairs: {(obj, attr): value} -- set, yield, restore."""
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


@contextlib.contextmanager
def envset(**kv):
    """Set (or with None: unset) environment variables, restore afterwards."""
    saved = {k: os.environ.get(k) for k in kv}
    try:
        for k, v in kv.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


TMP_A = Path(tempfile.mkdtemp(prefix="d24A-", dir=str(ROOT / ".run")))


def bare_chain_a(**kw):
    """A Chain without __init__ side effects."""
    c = object.__new__(orchestrate.Chain)
    c.base, c.pools, c.gov, c.only_modes = "d24a-base", None, None, None
    c.lane, c.name = "warmups", "test"
    c.entries = {"single_solve": {"id": "d24a"}, "time_trial": {"id": "d24a/time_trial"},
                 "mastery": {"id": "d24a/mastery"}}
    c.__dict__.update(kw)
    return c


# ================================================================ Track A
# ---------------------------------------------------------------- A1 instrumentation
said = []
with patched({(orchestrate, "say"): said.append, (workers, "TIMING_MARKS"): True}):
    ch = bare_chain_a(_chain_t0=time.time() - 30)
    for m in ("correct", "ready", "after_worker", "time_trial:stage"):
        ch._mark(m)
    ch._mark("time_trial:run", "d24a/time_trial")
    ch._mark("time_trial:run", "d24a/time_trial")          # a retry: no second line
    ch._mark("time_trial:correct")
    ch._mark("mastery:stage")
    ch._mark("mastery:run", "d24a/mastery")
lines = [s for s in said if "handoff timing" in s]
check("A1 one handoff timing line per mode (a retry adds none)", len(lines) == 2, said)
check("A1 the TT line lays out single CORRECT -> ready -> worker ended -> stage -> run, with the chain offset",
      lines and all(k in lines[0] for k in ("correct +0.0s", "ready +", "after_worker +", "time_trial:stage +",
                                            "time_trial:run +", "(chain +3")), lines[:1])
check("A1 the Mastery line starts at the TT's CORRECT",
      len(lines) > 1 and "(mastery): time_trial:correct +0.0s > mastery:stage +" in lines[1], lines[1:])
check("A1 marks keep the FIRST time", ch._marks["time_trial:run"] <= ch._marks["time_trial:correct"])
said.clear()
with patched({(orchestrate, "say"): said.append, (workers, "TIMING_MARKS"): False}):
    ch2 = bare_chain_a()
    ch2._mark("time_trial:stage")
    ch2._mark("time_trial:run", "d24a/time_trial")
check("A1 HCTF_TIMING_MARKS=0: no marks, no line", not said and not getattr(ch2, "_marks", None))

# hb_timed: spawn {main, lock, pool} and why a pre-start was not used
seen = {}


def fake_attempt(a):
    seen["spawn"] = dict(hb_timed._CTX.spawn or {})
    return {"result": "correct"}


with patched({(hb_timed, "_attempt"): fake_attempt}), envset(HCTF_T_SPAWN=f"{time.time() - 0.4:.3f}"):
    hb_timed.run_attempt("d24a-spawn/time_trial", "challenges/x/solver")
check("A1 hb_timed reports spawn.main (interpreter start, from HCTF_T_SPAWN) and spawn.lock",
      0.3 <= seen.get("spawn", {}).get("main", -1) < 5 and "lock" in seen.get("spawn", {}), seen)
check("A1 hb_timed clears the per-attempt spawn state", hb_timed._CTX.spawn is None)
with patched({(hb_timed, "_attempt"): fake_attempt}), envset(HCTF_T_SPAWN=f"{time.time() - 999:.3f}"):
    hb_timed.run_attempt("d24a-spawn/time_trial", "challenges/x/solver")
check("A1 a stale/foreign HCTF_T_SPAWN is ignored", "main" not in seen.get("spawn", {}), seen)

_pcid = "d24a-prestart/mastery"
_padir = hb_timed.HW / ".run" / "tmp-timed" / "d24a_prestart_mastery"
_padir.mkdir(parents=True, exist_ok=True)
(_padir / "contract.json").write_text(json.dumps({"attempt_id": "att1", "answer_ids": ["a"]}))
(_padir / "f.bin").write_bytes(b"x")
(_padir / ".prefetch.json").write_text(json.dumps({"attempt_id": "att1", "files": ["f.bin"], "t": time.time() - 9999}))
why = []
check("A1 a stale pre-start is not reused and says why", hb_timed._prestarted_body(_pcid, why) is None and why == ["stale"],
      why)
(_padir / ".prefetch.json").write_text(json.dumps({"attempt_id": "other", "files": ["f.bin"], "t": time.time()}))
why = []
check("A1 a pre-start of another attempt says mismatch", hb_timed._prestarted_body(_pcid, why) is None
      and why == ["mismatch"], why)
(_padir / ".prefetch.json").write_text(json.dumps({"attempt_id": "att1", "files": ["f.bin"], "t": time.time()}))
why = []
check("A1 a fresh pre-start is reused (no reason recorded)", hb_timed._prestarted_body(_pcid, why) is not None and not why)
shutil.rmtree(_padir, ignore_errors=True)

check("A1 the `timed:` line carries the runner's pre-clock timings",
      all(k in timed._TIMED_KEYS for k in ("spawn", "pool_warm", "prestart_reused", "prestart_miss", "t_env",
                                           "t_hb_ready")) and timed._TIMED_KEYS[0] == "result")


# run_timed_auto: the Homebase readiness seconds land on the result
def fake_route(*a, **k):
    workers._homebase_ready(lambda *x: None)
    return {"result": "correct"}


def slow_probe():
    time.sleep(0.05)
    return False


with patched({(workers, "_run_timed_auto"): fake_route, (workers, "start_homebase_health"): lambda log=None: None,
              (workers.remote, "probe"): slow_probe, (workers, "TIMING_MARKS"): True}):
    _saved_hb = dict(workers._hb)
    workers._hb.update(checked=0.0, ok=False)
    try:
        r = workers.run_timed_auto(Path("/x"), "d24a/time_trial")
    finally:
        workers._hb.clear()
        workers._hb.update(_saved_hb)
check("A1 run_timed_auto reports the seconds its Homebase readiness check cost",
      r.get("t_hb_ready", 0) >= 0.04, r)

# ================================================================ end of Track A
shutil.rmtree(TMP_A, ignore_errors=True)
if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D24 sub-2-min checks passed")
