"""Day 10 prep checks that need the Day 9 challenge data (contracts, saved Mastery cases, artifacts) of THIS copy:
per-set Mastery pipeline on real cases, deferred triage recon, timed_env byte hint. Skips (exit 0) on a copy without
challenges/day09 (the rehearsal copy never played Day 9 -- never copy main's solutions there).

Run:  source bin/env.sh && python3 tests/test_day10_data.py      (exit 0 = all pass / skipped)
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
D9 = ROOT / "challenges" / "day09"
if not (D9 / "binary-nimble" / "mastery" / "contract.json").exists():
    print("skip: no challenges/day09 data in this copy")
    sys.exit(0)
from hctf import triage, workers  # noqa: E402
import hb_timed  # noqa: E402

# 1) _set_plan: per-set deliveries -> pipeline plan; a shared delivery or a single set -> None (plain path)
mc = json.loads((D9 / "binary-nimble" / "mastery" / "contract.json").read_text())
ids = mc["answer_ids"]
plan = hb_timed._plan(mc)
sp = hb_timed._set_plan(mc, plan, ids)
assert sp and list(sp) == ["set1", "set2", "set3", "set4", "set5"], sp
assert sp["set3"] == ["delivery 3: evidence.zip"], sp
shared = json.loads(json.dumps(mc))
for q in shared["questions"]:
    if q["id"].startswith("set2."):
        q["artifact"] = "delivery 1: evidence.zip"
assert hb_timed._set_plan(shared, plan, ids) is None
tt = json.loads((D9 / "binary-nimble" / "time_trial" / "contract.json").read_text())
assert hb_timed._set_plan(tt, hb_timed._plan(tt), tt.get("answer_ids") or [q["id"] for q in tt["questions"]]) is None
assert hb_timed._total_bytes(mc) > 150e6
print("ok  _set_plan: 5 own-delivery sets planned; shared delivery / single-set TT -> plain path")

# 2) _pipelined on a real saved Mastery case (D9 mobile, 5 sets): every set solved by its own early run, answers match
#    the GM-verified expected values, scratch dirs removed; a failing set run -> None (whole-solver fallback)
case = next((D9 / "mobile-trust-everyone" / "solver" / "cases").glob("auto-mastery-*"))
body = json.loads((case / "contract.json").read_text())
exp = json.loads((case / "expected.json").read_text())
mids = body["answer_ids"]
mplan = [(n, n) for n in sorted(p.name for p in (case / "artifacts").iterdir())]
msets = hb_timed._set_plan(body, mplan, mids)
assert msets and len(msets) == 5, msets
solve = (D9 / "mobile-trust-everyone" / "solver" / "solve.py").resolve()
env = hb_timed._solver_env()
env["PYTHONPATH"] = str(ROOT)


def fetch_into(adir):
    return lambda item: shutil.copy(case / "artifacts" / item[0], adir / item[0])


with tempfile.TemporaryDirectory() as d:
    adir = Path(d)
    out = {}
    r = hb_timed._pipelined(msets, mplan, dict(body, deadline=None), mids, adir, solve, env, fetch_into(adir), 60,
                            out, time.time())
    assert r is not None, out
    got = json.loads(r.stdout)
    assert all(got.get(k) == v for k, v in exp.items()), {k: (got.get(k), v) for k, v in exp.items() if got.get(k) != v}
    assert out["pipelined"]["sets"] == 5 and "_t_downloaded" in out
    assert not list(adir.glob(".set-*")), list(adir.glob(".set-*"))
with tempfile.TemporaryDirectory() as d:
    adir = Path(d)
    bad = Path(d) / "bad_solve.py"
    bad.write_text("import sys; sys.exit(3)\n")
    out = {}
    r = hb_timed._pipelined(msets, mplan, dict(body, deadline=None), mids, adir, bad, env, fetch_into(adir), 60, out,
                            time.time())
    assert r is None and out.get("pipeline_fallback"), out
print("ok  _pipelined: D9 mobile Mastery 5/5 sets match expected; a failing set run falls back (no partial answers)")

# 6) triage: deferred recon writes a placeholder at once and the full recon section afterwards; no deferral when the
#    callable says no
cid = "warmups-day-09"
from hctf import cli  # noqa: E402
tpath = cli.cdir(cid) / "triage.md"
orig = tpath.read_text() if tpath.exists() else None
real_recon = triage._recon
gate = threading.Event()


def slow_recon(c, root):
    gate.wait(5)
    return ["", "## Recon (standard tools, pre-run for you -- facts, not answers)", "", "RECON-DONE-MARK"]


try:
    triage._recon = slow_recon
    logs = []
    p = triage.triage(cid, defer_recon=lambda: True, log=logs.append)
    first = p.read_text()
    assert "Still running in the background" in first and "RECON-DONE-MARK" not in first, first[-400:]
    gate.set()
    for _ in range(50):
        if "RECON-DONE-MARK" in p.read_text():
            break
        time.sleep(0.1)
    final = p.read_text()
    assert "RECON-DONE-MARK" in final and "Still running" not in final and logs, final[-300:]
    gate.clear()
    threading.Timer(0.3, gate.set).start()
    p = triage.triage(cid, defer_recon=lambda: False)
    assert "RECON-DONE-MARK" in p.read_text() and "Still running" not in p.read_text()
finally:
    triage._recon = real_recon
    if orig is not None:
        tpath.write_text(orig)
print("ok  triage: deferred recon -> placeholder now, full section later; no deferral -> written once, complete")

# 15) timed_env: the status-time contract's delivery bytes reach hb_timed (live start bodies carry no sizes)
env15 = workers.timed_env("binary-reverse-engineering-day-09-nim-generated-runtime/mastery")
assert int(env15.get("HCTF_EXPECT_BYTES", 0)) > 150e6, env15
os.environ["HCTF_EXPECT_BYTES"] = env15["HCTF_EXPECT_BYTES"]
try:
    live = dict(mc, artifacts=[{k: v for k, v in a.items() if k != "size"} for a in mc["artifacts"]])
    assert hb_timed._total_bytes(live) > 150e6
finally:
    del os.environ["HCTF_EXPECT_BYTES"]
assert hb_timed._total_bytes(live) == 0
print("ok  timed_env: HCTF_EXPECT_BYTES from the saved contract gates the pipeline on a size-less live body")

print("\nALL DAY-10 DATA CHECKS PASSED")
