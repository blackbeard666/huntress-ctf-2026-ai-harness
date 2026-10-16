"""Day 16 post-mortem fixes. Offline: no GM / Homebase / workers.
- procgov: a timed-out solver's whole process group dies (its fork pool too); background runs are niced, pinned,
  single-process (HCTF_SOLVER_PARALLEL=0), oom-adjusted and slot-limited; a chain's leftover runs die by owner tag.
- grouptest: parallel waves find k wrong fields of n in ~log2 waves; 429 = unjudged (retried, concurrency halves);
  already_solved stops; the budget leaves the rest unjudged. cli._bisect_rejected submits CONCURRENTLY (no chal_lock
  across the GM call) and banks accepted groups.
- timed runner: the no-clock timeout scales with the contract (5475 ids -> > 259 s of localization fits); a CORRECT
  latest attempt is reported (already_passed), never re-rolled; the attempt id + banked sets survive a kill (progress
  file -> exec_error carries them); the runner stops before the caller's deadline; one runner per mode (lock).
- post-run: phase markers + state file; recover() restores an interrupted generalize; the feed follows the post-run
  to "post-run finished" and reports a dead run instead of going silent.

Run:  source bin/env.sh && python3 tests/test_day16_postmortem.py      (exit 0 = all pass)
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, grouptest, procgov, solvers, workers  # noqa: E402
sys.path.insert(0, str(ROOT / "hctf"))
import hb_timed as H  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="hctf-d16pm-"))


def alive(pids):
    out = []
    for p in pids:
        try:
            os.kill(p, 0)
            st = Path(f"/proc/{p}/stat").read_text().split()[2]
            if st != "Z":
                out.append(p)
        except (OSError, IndexError):
            pass
    return out


# ------------------------------------------------------------------------------------------------ procgov
# A solver that forks a pool which outlives the leader's timeout (the D16 orphan shape).
sdir = TMP / "dayX" / "chal" / "solver"
sdir.mkdir(parents=True)
pidfile = TMP / "pids.txt"
(sdir / "solve.py").write_text(f"""
import os, sys, time, json
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
def w(_):
    open({str(pidfile)!r}, "a").write(str(os.getpid()) + "\\n")
    time.sleep(60)
if os.environ.get("HCTF_SOLVER_PARALLEL", "1") == "0":
    open({str(pidfile)!r}, "a").write("serial\\n")
    print(json.dumps({{"a": "1"}})); sys.exit(0)
with ProcessPoolExecutor(3, mp_context=mp.get_context("fork")) as ex:
    list(ex.map(w, range(3)))
""")
t0 = time.time()
got, err, dt = solvers.run_solver(sdir, {"answer_ids": ["a"], "questions": []}, TMP, timeout=2)
assert err and "timeout" in err, err
time.sleep(0.5)
pids = [int(x) for x in pidfile.read_text().split() if x.isdigit()]
assert len(pids) == 3, pids
assert not alive(pids), f"orphaned forks survived the timeout: {alive(pids)}"
assert time.time() - t0 < 15
print("ok  procgov: a timed-out solver's fork pool dies with it (group kill), no orphans")

# background class: single-process (HCTF_SOLVER_PARALLEL=0), niced, pinned, oom-adjusted
pidfile.write_text("")
probe = TMP / "probe.py"
probe.write_text("import os, json; print(json.dumps({'nice': os.nice(0), 'aff': sorted(os.sched_getaffinity(0)), "
                 "'oom': open('/proc/self/oom_score_adj').read().strip(), "
                 "'par': os.environ.get('HCTF_SOLVER_PARALLEL')}))")
fg = json.loads(procgov.run([sys.executable, str(probe)], timeout=20).stdout)
bg = json.loads(procgov.run([sys.executable, str(probe)], timeout=20, background=True).stdout)
assert fg["oom"] == str(procgov.FG_OOM_ADJ) and fg["par"] in (None, "1"), fg
assert bg["oom"] == str(procgov.BG_OOM_ADJ) and bg["par"] == "0" and bg["nice"] >= fg["nice"] + 10, bg
cpus = procgov.bg_cpus()
if cpus:
    assert set(bg["aff"]) == cpus and len(bg["aff"]) < len(fg["aff"]), (bg["aff"], fg["aff"])
got, err, _ = solvers.run_solver(sdir, {"answer_ids": ["a"], "questions": []}, TMP, timeout=10, background=True)
assert got == {"a": "1"} and not err and "serial" in pidfile.read_text(), (got, err)
print(f"ok  procgov: background runs are single-process, nice +{bg['nice'] - fg['nice']}, pinned to {len(bg['aff'])}/"
      f"{len(fg['aff'])} cores, oom_score_adj {bg['oom']} (foreground {fg['oom']})")

# the flag flows: thread-local -> procgov.Executor tasks; test_solver inherits it
with procgov.background():
    with procgov.Executor(max_workers=2) as ex:
        flags = list(ex.map(lambda _: procgov.is_bg(), range(4)))
assert flags == [True] * 4 and not procgov.is_bg()
with procgov.Executor(max_workers=2) as ex:
    assert not any(ex.map(lambda _: procgov.is_bg(), range(4)))
print("ok  procgov: background flag inherited by procgov.Executor tasks, off outside")

# slot limit: at most BG_SOLVERS background runs at once
slow = TMP / "slow.py"
slow.write_text("import time; time.sleep(0.6); print('{}')")
peak, cur, lock = [0], [0], threading.Lock()
orig_popen = subprocess.Popen


class CountPopen(orig_popen):
    def __init__(self, *a, **k):
        with lock:
            cur[0] += 1
            peak[0] = max(peak[0], cur[0])
        super().__init__(*a, **k)

    def communicate(self, *a, **k):
        try:
            return super().communicate(*a, **k)
        finally:
            with lock:
                cur[0] -= 1


subprocess.Popen = CountPopen
try:
    ths = [threading.Thread(target=procgov.run, args=([sys.executable, str(slow)],), kwargs={"timeout": 20,
                                                                                              "background": True})
           for _ in range(procgov.BG_SOLVERS + 4)]
    [t.start() for t in ths]
    [t.join() for t in ths]
finally:
    subprocess.Popen = orig_popen
assert peak[0] <= procgov.BG_SOLVERS, peak
print(f"ok  procgov: {procgov.BG_SOLVERS + 4} background runs at once -> peak {peak[0]} (slot limit "
      f"{procgov.BG_SOLVERS})")

# kill_owner: a chain's leftover background runs die when the chain ends
long = TMP / "long.py"
long.write_text("import time; time.sleep(60)")
res = {}
th = threading.Thread(target=procgov.bg_wrap(lambda: res.setdefault("r", _run_long()), owner_tag="day99/x"))


def _run_long():
    try:
        procgov.run([sys.executable, str(long)], timeout=60)
        return "finished"
    except Exception as e:  # noqa: BLE001
        return repr(e)


th.start()
time.sleep(1.0)
t0 = time.time()
assert procgov.kill_owner("day99/x") == 1
th.join(10)
assert not th.is_alive() and time.time() - t0 < 5, res
assert procgov.kill_owner("day99/x") == 0
print("ok  procgov: kill_owner(chain) ends that chain's leftover background runs")

# test_solver: parallelism follows MemAvailable
gb = solvers._mem_avail_gb()
assert gb and 1 <= solvers.case_parallel() <= max(1, min(8, int(gb / solvers.CASE_MEM_GB)))
print(f"ok  test_solver: {solvers.case_parallel()} parallel case(s) at {gb:.1f} GB available "
      f"({solvers.CASE_MEM_GB} GB per case)")

# ------------------------------------------------------------------------------------------------ grouptest
ids = [f"{fam}-{i}" for fam in ("resource", "collection", "impact", "jscript", "batch", "vbs", "ps") for i in range(150)]
ans = {a: "v" for a in ids}
WRONG = {"batch-3", "batch-17", "batch-88", "batch-140", "jscript-5"}
inflight, peak_in = [0], [0]
lk = threading.Lock()


def fake_probe(g, delay=0.05):
    with lk:
        inflight[0] += 1
        peak_in[0] = max(peak_in[0], inflight[0])
    time.sleep(delay)
    with lk:
        inflight[0] -= 1
    return "bad" if WRONG & set(g) else "ok"


t0 = time.time()
bad, st = grouptest.find_rejected(fake_probe, ans)
wall = time.time() - t0
assert bad == WRONG, bad
assert st["waves"] <= 9 and st["probes"] <= 90 and peak_in[0] >= 8, st
seq = st["probes"] * 0.05
assert wall < seq / 3, (wall, seq)
print(f"ok  grouptest: {len(WRONG)} wrong of {len(ids)} found in {st['waves']} waves / {st['probes']} probes, "
      f"{peak_in[0]} in flight ({wall:.2f}s vs {seq:.2f}s sequential)")

# 429 -> unjudged: retried next wave, concurrency halves, never counted wrong
calls = {}


def rate_probe(g):
    k = min(g)
    calls[k] = calls.get(k, 0) + 1
    if calls[k] == 1 and hash(k) % 3 == 0:
        return "rate"
    return fake_probe(g, 0.0)


bad, st = grouptest.find_rejected(rate_probe, ans)
assert bad == WRONG and st["rate_limited"] > 0 and st["conc_min"] < grouptest.CONC, st
print(f"ok  grouptest: {st['rate_limited']} rate-limited probe(s) retried (concurrency down to {st['conc_min']}), "
      "same answer")

# always-unjudged groups are left unjudged, never wrong
bad, st = grouptest.find_rejected(lambda g: None if "impact-1" in g else fake_probe(g, 0), ans)
assert bad == WRONG and st["unjudged_fields"] > 0 and not ({"impact-1"} & bad), st
# already_solved stops at once
bad, st = grouptest.find_rejected(lambda g: "solved", ans)
assert st["solved"] and st["waves"] == 1 and not bad, st
# budget: stops, the rest unjudged
bad, st = grouptest.find_rejected(fake_probe, ans, budget=10)
assert st["probes"] <= 10 and st["unjudged_fields"] > 0, st
print("ok  grouptest: unjudged never wrong; already_solved stops; budget bounds probes")
waves = [0]
bad, st = grouptest.find_rejected(lambda g: (waves.__setitem__(0, waves[0] + 1), fake_probe(g, 0))[1], ans,
                                  stop=lambda: waves[0] >= 24)
assert st.get("stopped") and st["unjudged_ids"] and set(st["unjudged_ids"]).isdisjoint(bad), st["waves"]
print("ok  grouptest: stop() (the worker took over) ends the bisect; the open fields come back unjudged")

# cli._bisect_rejected through the real cli.submit against a fake GM: concurrent, banked
CT = TMP / "cdirs"
cli_cdir = cli.cdir
cli.cdir = lambda cid: CT / cid
(CT / "s1").mkdir(parents=True)
(CT / "s1" / "start.json").write_text(json.dumps({"attempt_id": "A1", "answer_ids": ids,
                                                  "questions": [{"id": a, "answer_format": {"kind": "exact_text"}}
                                                                for a in ids]}))
gm_inflight, gm_peak = [0], [0]


def fake_call(cid, op, *args, timeout=180):
    a = json.loads(args[1])
    with lk:
        gm_inflight[0] += 1
        gm_peak[0] = max(gm_peak[0], gm_inflight[0])
    time.sleep(0.1)
    with lk:
        gm_inflight[0] -= 1
    if WRONG & set(a):
        return {"http": 200, "body": {"result": "incorrect"}}
    return {"http": 200, "body": {"result": "accepted", "remaining": 1, "accepted_ids": sorted(a)}}


orig_call = cli.call
cli.call = fake_call
try:
    t0 = time.time()
    bad = cli._bisect_rejected("s1", ans)
    wall = time.time() - t0
finally:
    cli.call = orig_call
conf = cli.confirmed_answers("s1")
assert bad == WRONG, bad
assert gm_peak[0] >= 6, gm_peak
assert set(conf) == set(ids) - WRONG, len(conf)
rows = [json.loads(x) for x in (CT / "s1" / "submissions.jsonl").read_text().splitlines()]
assert all("elapsed" in r for r in rows) and all(r.get("probe") for r in rows)
print(f"ok  bisect: cli.submit probes run concurrently ({gm_peak[0]} in flight at the GM, {len(rows)} probes, "
      f"{wall:.1f}s); {len(conf)} banked, exactly the {len(WRONG)} wrong ids returned; per-submit elapsed logged")
cli.cdir = cli_cdir

# ------------------------------------------------------------------------------------------------ timed runner
big = {"answer_ids": [f"set{k}.f{i}" for k in range(1, 6) for i in range(1095)],
       "artifacts": [{"size": 561628}]}
(CT / "sm" / "mastery").mkdir(parents=True)
(CT / "sm" / "mastery" / "contract.json").write_text(json.dumps(big))
cli.cdir = lambda cid: CT / cid
tmo, loc = workers.untimed_plan("sm/mastery")
assert loc >= 180 and tmo >= loc + 120, (tmo, loc)
assert workers.timed_env("sm/mastery")["HCTF_LOCALIZE_UNTIMED_S"] == str(loc)
(CT / "small" / "time_trial").mkdir(parents=True)
(CT / "small" / "time_trial" / "contract.json").write_text(json.dumps({"answer_ids": ["a"]}))
t2, l2 = workers.untimed_plan("small/time_trial")
assert l2 == 75 and t2 < tmo, (t2, l2)
print(f"ok  timed: no-clock runner timeout {tmo}s / localize {loc}s for 5475 ids x 5 sets (was a flat 120 s); "
      f"{t2}s / {l2}s for a 1-field mode")


class _NoPool:
    def fresh(self):
        return self


H._pool = lambda: _NoPool()
H._post_start = lambda payload: {"attempt_id": "E50", "result": "CORRECT", "flag": "x", "deadline": None}
os.environ.pop("HCTF_RUNNER_DEADLINE", None)
out = H.run_attempt("t16-correct/mastery", "challenges/day16/x/solver", op="start")
assert out["result"] == "correct" and out["already_passed"] and out["attempt_id"] == "E50", out
retried = []
H._post_start = lambda payload: retried.append(payload["op"]) or {"error": "stop"}
H.run_attempt("t16-correct/mastery", "challenges/day16/x/solver", op="retry")
assert retried == ["retry", "start"], retried       # an explicit retry still asks for a new variant
prog = workers.runner_progress("t16-correct/mastery")
assert prog.get("attempt_id") == "E50" and "result" not in prog, prog
print("ok  timed: start/resume on a CORRECT attempt -> already_passed (no re-roll); op=retry still re-rolls")

H._write_progress("t16-kill/mastery", {"attempt_id": "A9", "no_clock": True, "per_set": {"set1": {"result": "accepted"}}},
                  "submitted")
pr = workers.runner_progress("t16-kill/mastery", since=time.time() - 5)
from hctf import orchestrate  # noqa: E402
assert pr["attempt_id"] == "A9" and orchestrate._prev_banked({"result": "exec_error", **pr}), pr
assert workers.runner_progress("t16-kill/mastery", since=time.time() + 5) == {}
os.environ["HCTF_RUNNER_DEADLINE"] = f"{time.time() + 30:.3f}"
assert 10 < H._runner_left() < 16
os.environ.pop("HCTF_RUNNER_DEADLINE")
H._CTX.t0 = time.time()
H._CTX.opts = {"HCTF_RUNNER_BUDGET": "40"}
assert 20 < H._runner_left() < 26
H._CTX.opts = H._CTX.t0 = None
print("ok  timed: a killed runner's attempt id + accepted sets come back from its progress file (-> resume, banked); "
      "runner deadline / Homebase budget leave the 15 s margin")

os.environ["HCTF_RUNNER_DEADLINE"] = f"{time.time() + 16.5:.3f}"
l1 = H._mode_lock("t16-lock/mastery")
assert l1 is not None
t0 = time.time()
assert H._mode_lock("t16-lock/mastery") is None and time.time() - t0 < 4    # held: waits only to our deadline
l1.close()
l3 = H._mode_lock("t16-lock/mastery")
assert l3 is not None
l3.close()
os.environ.pop("HCTF_RUNNER_DEADLINE")
print("ok  timed: one runner per mode (a second one waits, then gives up at its own deadline)")

# harvest: a mode the live answer just passed is never re-rolled (rehearsal fair D16: Mastery 409 prerequisite_required)
import threading as _th  # noqa: E402
from hctf import orchestrate as _orch  # noqa: E402
calls_h = []
ch_h = object.__new__(_orch.Chain)
ch_h.base, ch_h.root, ch_h.sdir = "hv", CT / "hv", CT / "hv" / "solver"
ch_h._harvest_sleep = lambda prev, done: True
(CT / "hv" / "time_trial").mkdir(parents=True)
cli.cdir = lambda cid: CT / cid
_oc, _oic = cli.call, cli.is_complete
cli.is_complete = lambda cid: False
cli.call = lambda cid, op, *a, **k: calls_h.append(op) or {"http": 200, "body": {"result": "CORRECT", "attempt_id": "P1"}}
try:
    ch_h._harvest("hv/time_trial", 2, set(), _th.Event())
finally:
    cli.call, cli.is_complete, cli.cdir = _oc, _oic, cli_cdir
assert calls_h == ["start"], calls_h
print("ok  harvest: the mode's latest attempt is CORRECT -> stop, never `retry` (the GM's latest stays the pass)")
cli.cdir = cli_cdir
for f in (ROOT / ".run" / "tmp-timed").glob("t16_*"):
    f.unlink(missing_ok=True)

# ------------------------------------------------------------------------------------------------ post-run
from hctf import feed, postrun  # noqa: E402
lines = ["21:00:14 5 chains (15 challenge modes), slots local=5 homebase=0, credits=None",
         "21:00:24 [mobile-android-day-16-x] reuse race WON: single CORRECT at +5.7s",
         "21:15:58 all chains finished",
         "21:15:58 [postrun] ratchet start",
         "21:19:23 [ratchet-log] day16 warmups: worker exit 0 (w.log)",
         "21:23:47 [ratchet] day16: merged (worker-ratchet.log)",
         "21:23:47 [postrun] ratchet done (469s)",
         "21:23:48 [postrun] speed-harden start",
         "21:25:51 [speed-harden] binary-reverse-engineering-day-16-x: slowest case case-1 115.6s > 2.5s -> speed generalize",
         "21:26:11 [binary-reverse-engineering-day-16-x] generalize worker -> local (timeout 720s)"]
f = feed.Feed(follow_post=True)
out = [m for ln in lines for m in f.process(ln)]
assert not f.done and f.post and f.phase[0] == "speed-harden", (f.done, f.phase)
assert any("post-run: ratchet done" in m for m in out) and any("technique log" in m for m in out), out
assert "post-run: speed-harden" in f.heartbeat() and "binary single generalize" in f.heartbeat(), f.heartbeat()
f.process("22:39:08 [postrun] day16: restored challenges/day16/x/solver from its interrupted generalize (w)")
assert "generalize" not in f.heartbeat(), f.heartbeat()
out = f.process("23:10:00 post-run finished")
assert f.done and "post-run finished" in out[-1], out
f2 = feed.Feed()                       # not a day.sh run: ends at the chains, as before
[f2.process(ln) for ln in lines[:3]]
assert f2.done
print("ok  feed: follows the post-run (phases, technique logs, ratchet, speed-harden) to 'post-run finished'; "
      "a restore clears the dead generalize")

lp = TMP / "d.log"
lp.write_text("\n".join(lines) + "\n")
pf = TMP / "d.pid"
dead = subprocess.Popen([sys.executable, "-c", "pass"])
dead.wait()
pf.write_text(str(dead.pid))
r = subprocess.run([sys.executable, "-c", f"import sys; sys.path.insert(0, {str(ROOT)!r}); from hctf import feed; "
                    f"sys.exit(feed.follow({str(lp)!r}, heartbeat=0.5, poll=0.1, pidfile={str(pf)!r}))"],
                   capture_output=True, text=True, timeout=30)
assert r.returncode == 1 and "run process is gone" in r.stdout and "speed-harden" in r.stdout, (r.returncode, r.stdout)
print("ok  feed: a dead run (pid file, no end marker) -> ⚠ died during post-run phase speed-harden, exit 1")

import hctf.paths as _paths  # noqa: E402
ROOT_RUN = ROOT / ".run"
day = 98
logs = []
with postrun.phase(day, "speed-harden", log=logs.append):
    pass
try:
    with postrun.phase(day, "train", log=logs.append):
        raise RuntimeError("boom")
except RuntimeError:
    pass
st = postrun.load(day)
assert st["phases"]["speed-harden"]["status"] == "done" and st["phases"]["train"]["status"] == "FAILED", st
assert logs[0] == "[postrun] speed-harden start" and logs[-1].startswith("[postrun] train FAILED"), logs
postrun.state_path(day).unlink()
chal = _paths.CHALLENGES / "day98" / "x-chal"
(chal / ".generalize-snapshot").mkdir(parents=True)
(chal / ".generalize-snapshot" / "solve.py").write_text("ORIGINAL")
(chal / "solver").mkdir()
(chal / "solver" / "solve.py").write_text("HALF-EDITED")
(chal / "meta.json").write_text(json.dumps({"ids": {}}))
(chal / "chain.json").write_text(json.dumps({"stage": "single_solve:generalizing", "worker": "generalize@local"}))
try:
    acts = postrun.recover(day, log=logs.append)
    assert (chal / "solver" / "solve.py").read_text() == "ORIGINAL" and not (chal / ".generalize-snapshot").exists()
    assert json.loads((chal / "chain.json").read_text())["stage"] == "interrupted" and acts, acts
finally:
    import shutil as _sh
    _sh.rmtree(_paths.CHALLENGES / "day98", ignore_errors=True)
print("ok  postrun: phase markers + state (done / FAILED); recover() restores an interrupted generalize snapshot")

print("ALL PASS")
