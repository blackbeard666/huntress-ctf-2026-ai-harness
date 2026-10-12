"""Behavior checks for the Day 11 prep (Day 10 post-mortem): hex-width playbook law, variant-aware compound check,
test-gated ratchet, warm-start race, prior cases/ copied after the go, stamp-time pre-push dedup, TT-capped Mastery
estimate (offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_day11_prep.py      (exit 0 = all pass)
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
sys.path.insert(0, str(ROOT / "hctf"))
from hctf import orchestrate, workers  # noqa: E402
from lib import playbook  # noqa: E402

# 1) hex-width law: an unpadded metadata `_hex` value seeds its struct-width spellings; the D10 rejection is recorded
aid = "d09-pe-001-pe-address-of-entry-point-rva-hex"
seeds = playbook.seed_candidates("metadata-forensics", aid, solver_value="0x65bd0")
assert seeds[0] == "0x00065bd0", seeds
assert "0x65bd0" in playbook.rejected("metadata-forensics", "set1.d09-pe-003-pe-address-of-entry-point-rva-hex")
assert playbook.seed_candidates("metadata-forensics", "d09-pe-001-pe-coff-machine-u16-hex", solver_value="0x14c")[0] == "0x014c"
print("ok  playbook hex law: 0x65bd0 -> 0x00065bd0 first (u32), 0x14c -> 0x014c (u16); unpadded spelling rejected")

# 2) variant-aware compound check: re-rolled variant counters of the Single's own field are not "new questions"
assert orchestrate.field_shape("set2.d09-pe-004-pe-address-of-entry-point-rva-hex") == "d09-pe-N-pe-address-of-entry-point-rva-hex"
assert orchestrate.field_shape("set1.d01_artifact_sha256_1") == "d01_artifact_sha256_1"     # binary ids untouched
single = {"answer_ids": [aid], "questions": [{"id": aid, "artifact": "evidence.zip"}]}
timed = [{"questions": [{"id": "d09-pe-002-pe-address-of-entry-point-rva-hex", "artifact": "evidence.zip"}]},
         {"questions": [{"id": f"set{i}.d09-pe-00{i + 2}-pe-address-of-entry-point-rva-hex", "artifact": "e.zip"}
                        for i in (1, 2)]}]
assert orchestrate.mastery_delta(single, timed) == ""
grown = timed + [{"questions": [{"id": "set1.d04-jpeg-001-jpeg-sof-dimensions-pixels", "artifact": "e.zip"}]}]
delta = orchestrate.mastery_delta(single, grown)
assert "`d04-jpeg-001-jpeg-sof-dimensions-pixels`" in delta and "1 question id(s)" in delta, delta
print("ok  mastery_delta: d09-pe-00{2,3,4} variants of the Single's field add nothing; a real new family still shows")

# 3) ratchet: the TESTS gate lib/, not the worker's exit code (D8/D10 max_turns threw away GM-confirmed edits)
real = (orchestrate.ROOT, orchestrate.paths.CHALLENGES, workers.run_local, orchestrate.ratchet_gate,
        orchestrate.SPEED_HARDEN)


def run_ratchet(rc, gate_ok, edit=True):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "lib").mkdir()
        (root / "lib" / "knowledge.py").write_text("A = 1\n")
        (root / ".run").mkdir()
        (root / "challenges" / "day10" / "x").mkdir(parents=True)
        (root / "challenges" / "day10" / "x" / "meta.json").write_text("{}")

        def fake_run_local(chal_dir, stage, prompt, env, timeout):
            if edit:
                (root / "lib" / "knowledge.py").write_text("A = 1\nB = 2\n")
            return rc, str(root / "worker-ratchet.log")
        orchestrate.ROOT, orchestrate.paths.CHALLENGES = root, root / "challenges"
        workers.run_local, orchestrate.ratchet_gate, orchestrate.SPEED_HARDEN = fake_run_local, lambda tag: gate_ok, False
        try:
            orchestrate.ratchet(10)
        finally:
            (orchestrate.ROOT, orchestrate.paths.CHALLENGES, workers.run_local, orchestrate.ratchet_gate,
             orchestrate.SPEED_HARDEN) = real
        return (root / "lib" / "knowledge.py").read_text(), (root / ".run" / "ratchet-lib-day10").exists()


kept, backup_left = run_ratchet(rc=1, gate_ok=True)
assert "B = 2" in kept and not backup_left, (kept, backup_left)
reverted, backup_left = run_ratchet(rc=0, gate_ok=False)
assert "B = 2" not in reverted and not backup_left
unchanged, _ = run_ratchet(rc=1, gate_ok=False, edit=False)
assert unchanged == "A = 1\n"
assert workers.MAX_TURNS["ratchet"] >= 80
print("ok  ratchet: max_turns + green tests keeps lib/, red tests revert it, backup removed either way, cap 80")

# 4) warm-start race: send_task holds the warm flag until the READY turn's `result` line is logged
with tempfile.TemporaryDirectory() as d:
    w = workers.WarmWorker.__new__(workers.WarmWorker)
    w.log, w.flag = Path(d) / "worker.log", Path(d) / ".warm"
    w.flag.write_text("warm")
    w.log.write_text(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "READY"}]}}) + "\n")
    w.p = subprocess.Popen(["cat"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    seen = {}

    def end_turn():
        time.sleep(0.4)
        seen["flag_before_result"] = w.flag.exists()
        with open(w.log, "a") as f:   # the CLI's key order is not fixed: `type` is not first
            f.write(json.dumps({"duration_ms": 2153, "type": "result", "subtype": "success"}) + "\n")
    threading.Thread(target=end_turn).start()
    t0 = time.time()
    w.send_task("GO")
    waited = time.time() - t0
    w.p.wait(timeout=5)
    assert seen["flag_before_result"] and not w.flag.exists() and 0.35 < waited < 3, (seen, waited)
print(f"ok  WarmWorker.send_task: flag kept until the warm turn's result line ({waited:.2f}s), then the go is sent")

# 5) prior staging: the go waits for the code only; cases/ follows in the background
with tempfile.TemporaryDirectory() as d:
    prior, sdir = Path(d) / "prior", Path(d) / "today" / "solver"
    (prior / "cases" / "auto-1").mkdir(parents=True)
    (prior / "cases" / "auto-1" / "expected.json").write_text("{}")
    (prior / "solve.py").write_text("print(1)\n")
    orchestrate.stage_prior_solver(prior, sdir, cases=False)
    assert (sdir / "solve.py").exists() and not (sdir / "cases").exists()
    orchestrate.stage_prior_cases(prior, sdir)
    assert (sdir / "cases" / "auto-1" / "expected.json").exists()
print("ok  stage_prior_solver(cases=False) + stage_prior_cases: code first, the cases/ corpus after the go")

# 6) early pre-push: a speculative push ships files only; the verified push of the same code just warms the zygote;
#    concurrent pushes of identical code push once; changed code re-pushes
calls = {"push": 0, "warm": 0}
saved = (workers.sync_homebase_base, workers.push_hot_files, workers.push_solver, workers.hb_daemon)


class FakeDaemon:
    def call(self, op, **kw):
        calls["warm"] += 1
        return {"warm_ms": 1}


def fake_push(src, rel):
    calls["push"] += 1
    time.sleep(0.2)
    return "tar"


workers.sync_homebase_base, workers.push_hot_files = (lambda: None), (lambda: None)
workers.push_solver, workers.hb_daemon = fake_push, (lambda log=None: FakeDaemon())
sdir = ROOT / "challenges" / "day99" / "fake-prepush" / "solver"
quiet = {"log": lambda *a: None}
try:
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "solver"
        src.mkdir()
        (src / "solve.py").write_text("print(1)\n")
        assert workers.prepush_solver(src, sdir, warm=False, **quiet).wait(5)       # speculative: settled edit
        assert calls == {"push": 1, "warm": 0}, calls
        e1 = workers.prepush_solver(src, sdir, **quiet)                              # stamp-time
        e2 = workers.prepush_solver(src, sdir, **quiet)                              # verdict-time, while e1 runs
        assert e2.wait(5) and e1.is_set() and calls == {"push": 1, "warm": 1}, calls
        (src / "solve.py").write_text("print(2)\n")                                # code changed after the stamp
        assert workers.prepush_solver(src, sdir, **quiet).wait(5) and calls == {"push": 2, "warm": 2}, calls
finally:
    workers.sync_homebase_base, workers.push_hot_files, workers.push_solver, workers.hb_daemon = saved
    for reg in (workers._prepush, workers._pushed, workers._warmed):
        reg.pop(str(sdir), None)
print("ok  prepush_solver: speculative = files only; verified same code = warm only; one push per signature")

# 7) Mastery estimate capped by the passing Time Trial's in-window solve phase (one set, same executor)
with tempfile.TemporaryDirectory() as d:
    tt, mc = Path(d) / "last_timed.json", Path(d) / "contract.json"
    mc.write_text(json.dumps({"questions": [{"id": f"set{i}.message"} for i in range(1, 49)]}))
    tt.write_text(json.dumps({"result": "correct", "phases": {"solve": 0.02}}))
    assert orchestrate.tt_solve_cap(tt, mc) == 3.6          # floor 0.05 s/set x 48 x 1.5, vs a 17.51 s probe estimate
    tt.write_text(json.dumps({"result": "correct", "phases": {"solve": 0.9}}))
    mc.write_text(json.dumps({"questions": [{"id": "set1.a"}, {"id": "set2.a"}]}))
    assert orchestrate.tt_solve_cap(tt, mc) == 2.7          # D10 script: real Mastery solve 2.4 s stays under the cap
    tt.write_text(json.dumps({"result": "expired", "phases": {"solve": 0.02}}))
    assert orchestrate.tt_solve_cap(tt, mc) is None
print("ok  tt_solve_cap: a correct TT's solve phase bounds the Mastery estimate; no cap without a passing TT")

# 8) compounding misses before Mastery: held back (no blocking generalize) only for a never-attempted Mastery whose
#    status-time contract asks none of the missed fields; a Mastery-failure generalize still gets them
from hctf import compound  # noqa: E402

with tempfile.TemporaryDirectory() as d:
    old_case = Path(d) / "challenges" / "day07" / "metadata-x" / "solver" / "cases" / "auto-mastery-1"
    old_case.mkdir(parents=True)
    (old_case / "contract.json").write_text(json.dumps({"questions": [{"id": "set1.d07-zip-001-zip-eocd-total-entries"}]}))
    hard = [{"day": 7, "case": "auto-mastery-1", "path": str(old_case.relative_to(d)), "answered": 1}]
    fresh = {"error": "start_required", "questions": [{"id": "set1.d09-pe-003-pe-address-of-entry-point-rva-hex"}]}
    contracts = {"m": fresh}
    adopted = []
    saved = (orchestrate.ROOT, orchestrate.cli.load, compound.adopt)
    orchestrate.ROOT = Path(d)
    orchestrate.cli.load = lambda cid, name: contracts.get(cid) if name == "contract.json" else None
    compound.adopt = lambda sdir, h: adopted.extend(h) or len(h)
    try:
        ch = orchestrate.Chain.__new__(orchestrate.Chain)
        ch.sdir = Path(d) / "solver"
        ch._family_pre_result = lambda wait=True: ("", [])
        ch._mut_late_done = True
        ch._cmp_late_done = False
        ch._compound_pre_result = lambda wait=True: ("compound text", hard)
        assert ch._compound_relevant("m", hard) is False
        assert ch._late_probes("m", defer_compound=True) == {} and adopted == []          # Mastery starts at once
        late = ch._late_probes("m", wait=True)                                              # Mastery failed
        assert late == {"compound_pre": "compound text"} and adopted == hard
        contracts["m"] = dict(fresh, attempt_id="a1", started_at="2026-10-12T00:42:57Z")   # re-attempt: may escalate
        assert ch._compound_relevant("m", hard) is True
        contracts["m"] = {"questions": [{"id": "set2.d07-zip-009-zip-eocd-total-entries"}]}  # Mastery asks that field
        assert ch._compound_relevant("m", hard) is True
        contracts["m"] = {}                                                                   # unknown contract
        assert ch._compound_relevant("m", hard) is True
    finally:
        orchestrate.ROOT, orchestrate.cli.load, compound.adopt = saved
print("ok  compound pre-Mastery: unasked earlier-day misses held back on a first attempt; re-attempt/asked/unknown block")

print("\nALL DAY-11 PREP CHECKS PASSED")
