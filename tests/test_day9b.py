"""Day 9 prep, round 2 (from the rehearsal Day 8 review): prior-solver dry-run diagnostics, harness profile for speed
generalizes, submit stamp, Mastery estimate on questions-only contracts, post-run speed hardening (offline).

Run:  source bin/env.sh && python3 tests/test_day9b.py      (exit 0 = all pass)
"""
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import orchestrate, solvers  # noqa: E402

TMPD = Path(tempfile.mkdtemp(dir=str(ROOT / ".run" / "tmp")))
contract = {"answer_ids": ["d01_x", "d08_y"], "questions": [{"id": "d01_x"}, {"id": "d08_y"}]}
art = TMPD / "art"
art.mkdir()

# 1) prior-solver dry run: a solver that hangs -> interrupted, its OWN frames named, no values
hang = TMPD / "hang"
hang.mkdir()
(hang / "solve.py").write_text("import json, sys\n"
                               "def slow_parse():\n    while True:\n        pass\n"
                               "def main():\n    print('[!] unknown field analysis_new', file=sys.stderr)\n    slow_parse()\n"
                               "main()\n")
t = time.time()
d = solvers.dry_run_diagnostics(hang, contract, art, timeout=2)
assert d["timed_out"] and time.time() - t < 8, d
txt = solvers.render_dry_run(d)
assert "did NOT finish" in txt and "slow_parse" in txt and "unknown field analysis_new" in txt, txt
# 2) a solver that answers part: count + empty ids named, VALUES withheld
part = TMPD / "part"
part.mkdir()
(part / "solve.py").write_text("import json\nprint(json.dumps({'d01_x': 'SECRET-VALUE-123'}))\n")
d = solvers.dry_run_diagnostics(part, contract, art, timeout=10)
txt = solvers.render_dry_run(d)
assert d["answered"] == 1 and d["total"] == 2 and "`d08_y`" in txt and "SECRET-VALUE-123" not in txt, txt
print("ok  prior-solver dry run: hang interrupted with the solver's own frame; empty ids named; values never shown")

# 3) harness profile for a speed generalize: hot function named
slowp = TMPD / "slowp"
(slowp / "cases" / "single_solve" / "artifacts").mkdir(parents=True)
(slowp / "cases" / "single_solve" / "contract.json").write_text(json.dumps(contract))
(slowp / "solve.py").write_text("import json\ndef hot_loop():\n    return sum(i * i for i in range(2_000_000))\n"
                                "hot_loop()\nprint(json.dumps({}))\n")
prof = solvers.profile_solver(slowp, slowp / "cases" / "single_solve")
assert "hot_loop" in prof and "cumtime" in prof, prof[:400]
print("ok  harness profile: top cumulative rows, hot function visible")

# 4) Mastery speed estimate works on the real GM's questions-only status contract (no answer_ids)
mc = TMPD / "mastery.json"
mc.write_text(json.dumps({"questions": [{"id": f"set{i}.x"} for i in range(1, 6)]}))
summ = {"base_seconds": 1.0, "results": [{"mutation": "mastery-shape", "ok": True, "seconds": 2.0}]}
est = orchestrate.mastery_estimate(summ, mc)
assert est is not None and 7 < est < 8, est        # 1.0 s/set x 5 x 1.5
print(f"ok  mastery_estimate on a questions-only contract: {est}s")

# 5) submit stamp: matches only the exact solver code that produced it
ch = object.__new__(orchestrate.Chain)
ch.base, ch.sdir = "b", part
cdir = TMPD / "cdir"
cdir.mkdir()
_orig = orchestrate.cli.cdir
orchestrate.cli.cdir = lambda cid: cdir
try:
    m = ch._solver_mtimes()
    (cdir / ".solver_stamp.json").write_text(json.dumps({"mtimes": m, "seconds": 0.4, "answers": {"d01_x": "v"}}))
    assert ch._submit_stamp("b", ch._solver_mtimes())["seconds"] == 0.4      # mtimes survive the JSON round trip
    time.sleep(0.01)
    (part / "solve.py").write_text((part / "solve.py").read_text() + "\n")
    assert ch._submit_stamp("b", ch._solver_mtimes()) is None                 # edited since -> re-verify
finally:
    orchestrate.cli.cdir = _orig
print("ok  submit stamp: reused only for unchanged solver code")

# 6) speed hardening picks only solvers whose slowest verified case is over budget, one generalize each
calls = []
_o = (orchestrate.solvers.test_solver, orchestrate.Chain.generalize, orchestrate.chain_for, orchestrate.paths.solver_dir)
fast_sd, slow_sd = TMPD / "fast", TMPD / "slow"
for sd in (fast_sd, slow_sd):
    sd.mkdir()
    (sd / "solve.py").write_text("print('{}')\n")
times = {str(fast_sd): [0.4, 1.1], str(slow_sd): [0.5, 3.6]}
orchestrate.solvers.test_solver = lambda sdir, **k: [{"case": f"c{i}", "seconds": s, "ok": True} for i, s in
                                                     enumerate(times[str(sdir)])]
orchestrate.paths.solver_dir = lambda base: fast_sd if base == "fast" else slow_sd
orchestrate.chain_for = lambda base, pools, gov: type("C", (), {"generalize": lambda self, cid, **k: (
    calls.append((cid, k["diag"])), times.__setitem__(str(slow_sd), [0.5, 0.9]))})()
try:
    out = orchestrate.speed_harden(cid="fast", log=lambda *a: None)
    assert out["fast"] == (1.1, None) and not calls
    out = orchestrate.speed_harden(cid="slow", log=lambda *a: None)
    assert out["slow"] == (3.6, 0.9) and calls == [("slow", {"solver_too_slow": True, "single_seconds": 3.6})], (out, calls)
finally:
    (orchestrate.solvers.test_solver, orchestrate.Chain.generalize, orchestrate.chain_for,
     orchestrate.paths.solver_dir) = _o
print("ok  speed_harden: only over-budget solvers get one speed generalize")
print("ALL PASS")
