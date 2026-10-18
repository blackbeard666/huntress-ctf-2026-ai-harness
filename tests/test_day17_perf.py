"""Day 17 performance review: the fixes for the run's lost time. Offline.
- lib.decode joint search: each (codec, line) decodes once, _best_rot is cached, and only slug-ending assignments are
  bigram-scored (D17 warmups Mastery: 83 blobs 751 s -> 17 s serial; 1139-blob corpus identical) -- same results.
- route_costs: one submit for the whole attempt (not one per set) and the solve run in waves of each host's CPUs.
- a no-clock solve that ran out of its budget on a slow VM is re-run locally before a speed generalize.
- the new-id hold no longer skips silently when no background dry run exists for the final code (sync dry run).
- contract drift: a question the GM rewrote in place is saved + stamped; the submit guards forget its old rejections.

Run:  source bin/env.sh && python3 tests/test_day17_perf.py      (exit 0 = all pass)
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# drop-time state: today's (D17) warmups codec not registered yet -> the joint free-codec search is what runs
os.environ["HCTF_CODEC_MAX_DAY"] = "16"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, orchestrate, timed, workers  # noqa: E402
from lib import decode  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="hctf-d17perf-"))
cli.cdir = lambda cid: TMP / cid

# ------------------------------------------------------------------------------------------------ lib.decode speed
DATA = ROOT / "tests" / "data" / "d17_warmups_mastery"
exp = json.loads((DATA / "expected.json").read_text())
t0 = time.time()
for name, want in exp.items():
    text = (DATA / name).read_text()
    assert decode.decode_candidates(text, 5) == want["candidates"], name
    assert decode.decode_chunked(text) == want["chunked"], name
dt = time.time() - t0
assert dt < 6, f"3 D17 Mastery blobs took {dt:.1f}s (pre-patch: ~11.5 s)"
print(f"ok  lib.decode: 3 of D17's slowest warmups blobs decode as before in {dt:.2f}s (pre-patch ~11.5 s, D17 codec hidden)")

# ------------------------------------------------------------------------------------------------ route_costs
cid = "warmups-day-17/mastery"
ids = [f"set{i}.message" for i in range(1, 84)]
(TMP / cid).mkdir(parents=True)
(TMP / cid / "contract.json").write_text(json.dumps({"answer_ids": ids,
                                                     "artifacts": [{"size": 138859}]}))
tt = "warmups-day-17/time_trial"
(TMP / tt).mkdir(parents=True)
(TMP / tt / "last_timed.json").write_text(json.dumps({"phases": {"solve": 0.05}, "routed": "homebase (window unknown)"}))
workers._hb.update(cpu_ratio=5.61, vm_cores=2)
loc, hb = workers.route_costs(cid)
assert loc < 20, f"local estimate {loc:.1f}s still counts one submit per set (old model: 155 s)"
n, nb, nsets = workers._contract_shape(cid)
solve, per_set = workers._solve_estimate(cid)
assert per_set and abs(solve - 0.05 / 5.61) < 1e-6, (solve, per_set)
assert hb > (nb / nsets / workers.HB_DL_BPS) + 0.05 * 42 - 0.01, "the VM's 2 cores serialize 83 sets into 42 waves"
(TMP / cid / "last_timed.json").write_text(json.dumps({"phases": {"solve": 4.0}, "routed": "local (untimed)"}))
assert workers._solve_estimate(cid) == (4.0, False), "the mode's own measurement is the whole mode, not per set"
print(f"ok  route_costs: 83-set Mastery local {loc:.1f}s (was 155 s) vs Homebase {hb:.1f}s with 42 VM solve waves")

# ------------------------------------------------------------------------------------------------ slow-VM local rerun
last = {"result": "exec_error", "solver_too_slow": True, "routed": "homebase (window unknown)", "deadline": None,
        "no_clock": True, "run_for_time": False}
_lr = timed.last_result
timed.last_result = lambda c: last
assert orchestrate.Chain._slow_vm_no_clock(cid), "no-clock + too slow + slow VM -> local rerun"
last["deadline"] = "2026-10-17T13:05:00Z"
assert not orchestrate.Chain._slow_vm_no_clock(cid), "a real clock: never a long local rerun"
last.update(deadline=None, routed="local (untimed)")
assert not orchestrate.Chain._slow_vm_no_clock(cid), "already local: nothing to gain"
last["routed"] = "homebase (untimed)"
workers._hb["cpu_ratio"] = 1.2
assert not orchestrate.Chain._slow_vm_no_clock(cid), "a fast VM: the solver itself is slow -> generalize"
workers._hb["cpu_ratio"] = 5.61
timed.last_result = _lr
calls = []
_rt = workers.run_timed
workers.run_timed = lambda sd, c, op="start", timeout=60, budget=None: calls.append((op, timeout, budget)) or {"result": "correct"}
res = workers.run_timed_auto(ROOT / "hctf", cid, op="start", force_local=True)
workers.run_timed = _rt
assert calls and calls[0][2] == workers.UNTIMED_LOCAL_BUDGET and res["routed"].startswith("local"), (calls, res)
print(f"ok  slow-VM rerun: only no-clock + too-slow + slow VM; forced local run gets {workers.UNTIMED_LOCAL_BUDGET:g}s")

# ------------------------------------------------------------------------------------------------ new-id sync dry run
base = "metadata-forensics-day-17-x"
sdir = TMP / "day17" / "metadata-x" / "solver"
sdir.mkdir(parents=True)
(sdir / "solve.py").write_text("# code\n")
snap = TMP / "snap" / "solver"
snap.mkdir(parents=True)
(snap / "solve.py").write_text("# final code, saved < 1 s before the CORRECT submit\n")
old_ids = [f"meta-old-{i}" for i in range(10)]
new_id = "metadata-day-17-synthesis-sha256-order"
for m, ids_ in (("", old_ids), ("/time_trial", old_ids + [new_id])):
    (TMP / f"{base}{m}").mkdir(parents=True, exist_ok=True)
    body = {"attempt_id": "A", "answer_ids": ids_, "questions": [{"id": a, "artifact": "evidence.zip"} for a in ids_]}
    (TMP / f"{base}{m}" / ("start.json" if not m else "contract.json")).write_text(json.dumps(body))
art = TMP / "art"
art.mkdir()
(art / "evidence.zip").write_bytes(b"PK")
orchestrate.lane_known_shapes = lambda lane, day: {orchestrate.field_shape(a) for a in old_ids}
_la, _rs = orchestrate.timed.latest_artifacts, orchestrate.solvers.run_solver
orchestrate.timed.latest_artifacts = lambda c: art
orchestrate.solvers.run_solver = lambda sd, c, a, timeout=20: ({x: "v" for x in old_ids}, None, 0.1)
ch = orchestrate.Chain.__new__(orchestrate.Chain)
ch.base, ch.lane, ch.sdir, ch._newid = base, "metadata-forensics", sdir, {}
gaps = ch._newid_result(snap)
orchestrate.timed.latest_artifacts, orchestrate.solvers.run_solver = _la, _rs
assert gaps == [new_id], gaps
print("ok  new-id hold: no background run for the final code -> synchronous dry run names the empty new field")

# ------------------------------------------------------------------------------------------------ contract drift
dc = "binary-day-17-x"
(TMP / dc).mkdir()
q_old = {"id": "d12_analysis_hcfg_storage", "question": "What is the exact analysis hcfg storage value?",
         "answer_format": {"kind": "exact_text"}}
q_new = {**q_old, "answer_format": {"kind": "enum", "accepted_values": ["raw", "raw_const_array"]}}
other = {"id": "d12_analysis_hcfg_offset", "question": "offset?", "answer_format": {"kind": "integer"}}
start = {"attempt_id": "B1", "answer_ids": [other["id"], q_old["id"]], "questions": [other, q_old]}
(TMP / dc / "start.json").write_text(json.dumps(start))
wrong = [{"ts": f"20261017T13{i:02d}00Z", "attempt": "B1", "answers": {q_old["id"]: v}, "kind": "incorrect"}
         for i, v in enumerate(["raw", "plain", "none", "xor", "section", "data", "bytes", "blob"])]
wrong.append({"ts": "20261017T135900Z", "attempt": "B1", "answers": {other["id"]: "1"}, "kind": "incorrect"})
(TMP / dc / "submissions.jsonl").write_text("".join(json.dumps(h) + "\n" for h in wrong))
_call = cli.call
cli.call = lambda c, op, *a, **k: {"http": 200, "body": {**start, "questions": [other, q_new]}}
changed = cli.contract_drift(dc)
assert changed == [q_old["id"]], changed
saved = json.loads((TMP / dc / "start.json").read_text())
assert saved["questions"][1]["answer_format"]["kind"] == "enum" and saved["attempt_id"] == "B1"
assert q_old["id"] in json.loads((TMP / dc / "drift.json").read_text())
assert cli.contract_drift(dc) == [], "a second check finds nothing new"
cli.call = lambda c, op, *a, **k: {"http": 200, "body": {**start, "attempt_id": "B2", "questions": [other, q_new]}}
assert cli.contract_drift(dc) == [], "a different attempt is not drift"
sent = []


def fake_gm(c, op, *a, **k):
    sent.append(json.loads(a[1]))
    return {"http": 200, "body": {"result": "accepted", "remaining": 1}}


cli.call = fake_gm
kind, _b, problems = cli.submit(dc, {q_old["id"]: "raw"})
assert not problems and sent, ("'raw' was judged on the OLD question: the rewrite must clear it", problems)
kind, _b, problems = cli.submit(dc, {other["id"]: "1"})
assert problems and "already judged incorrect" in problems[0], "an untouched field keeps its rejections"
cli.call = _call
print("ok  contract drift: rewritten question saved + stamped; its 8 old rejections no longer block; others kept")
print("ALL PASS")
