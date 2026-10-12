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
# 7) codec-family probe beside the first TT: an unfinished probe doesn't hold the TT; Mastery consumes it once
class _Fut:
    def __init__(self, val, done):
        self.val, self._done = val, done

    def done(self):
        return self._done

    def result(self, timeout=None):
        self._done = True
        return self.val


famdir = TMPD / "fam" / "sh" / "family-1"
famdir.mkdir(parents=True)
(famdir / "expected.json").write_text("{}")
ch = object.__new__(orchestrate.Chain)
ch.base, ch.sdir, ch.lane = "b", TMPD / "famsolver", "script-analysis"
(ch.sdir / "cases").mkdir(parents=True)
ch.entries = {"time_trial": {"id": "b/time_trial"}, "mastery": {"id": "b/mastery"}}
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
ch._fam_pre_fut = _Fut(("family: 1 miss", [str(famdir)]), done=False)
ch._mut_pre_fut = _Fut(("", [], {}), done=True)
ch._cmp_pre_fut = _Fut(("", []), done=True)
gens, runs = [], []
patches = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (orchestrate.timed, "run"): lambda cid, sdir, log=None, **k: (runs.append(cid), "correct")[1],
    (orchestrate.timed, "last_result"): lambda cid: None,
    (orchestrate.Chain, "generalize"): lambda self, cid, wrong=None, fixed=None, diag=None: gens.append(diag),
    (orchestrate.Chain, "_mastery_speed_gate"): lambda self, cid: None,
}
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert ch.timed_stage("time_trial") is True and runs == ["b/time_trial"] and not gens, (runs, gens)
    for _f in (ch._fam_pre_fut, ch._mut_pre_fut, ch._cmp_pre_fut):
        _f._done = True     # the probes finished beside the Time Trial (a still-running one: test_day10_prep)
    assert ch.timed_stage("mastery") is True and len(gens) == 1 and "family_pre" in gens[0], gens
    assert (ch.sdir / "cases" / "family-sh-1").exists()
    assert ch._family_pre_result() == ("", [])                 # consumed once
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
print("ok  codec-family probe beside the TT: TT not held; Mastery adopts + generalizes once")

# 8) solver skeleton: Mastery sets solved in parallel processes, same answers as sequential
import os  # noqa: E402
import subprocess  # noqa: E402
sk = TMPD / "skel"                     # .run/tmp/<X>/skel/solve.py: parents[4] is the project root
sk.mkdir(parents=True)
src = (ROOT / "hctf" / "templates" / "solve_skeleton.py").read_text()
(sk / "solve.py").write_text(src.replace("    return None  # TODO", "    import time; time.sleep(0.3); return answer_id.upper()"))
ids = [f"set{i}.f" for i in range(1, 5)]
(sk / "c.json").write_text(json.dumps({"answer_ids": ids, "questions": [{"id": x} for x in ids]}))
outs, secs = {}, {}
for par in ("1", "0"):
    t = time.time()
    r = subprocess.run([sys.executable, str(sk / "solve.py"), "--contract", str(sk / "c.json"), "--artifacts", str(sk)],
                       capture_output=True, text=True, timeout=60, env=dict(os.environ, HCTF_SOLVER_PARALLEL=par))
    secs[par], outs[par] = time.time() - t, json.loads(r.stdout.strip().splitlines()[-1])
assert outs["1"] == outs["0"] == {i: i.upper() for i in ids}, outs
if (os.cpu_count() or 1) >= 2:
    assert secs["1"] < secs["0"] * 0.75, secs
print(f"ok  skeleton parallel sets: same answers, {secs['1']:.2f}s vs {secs['0']:.2f}s sequential")
# 9) a finished CORRECT body after our submit timed out = the GM judged it late -> a pass (no re-roll loop)
from hctf import timed as _timed, cli as _cli  # noqa: E402
recorded = []
_o = (_timed._remember, _timed._keep_failed_attempt, _timed.capture_case, _cli.gm_latest_correct, _cli.record_remote_result)
_timed._remember = _timed._keep_failed_attempt = lambda *a, **k: None
_timed.capture_case = lambda *a, **k: None
_cli.record_remote_result = lambda cid, att, ans, kind, body=None: recorded.append((cid, att, kind))
try:
    late = {"result": "no_answer_ids", "attempt_id": None, "start_refused": True,
            "detail": {"result": "CORRECT", "status": "pending", "attempt_id": "abc"}}
    _cli.gm_latest_correct = lambda cid: True
    assert _timed.process_result("x/time_trial", TMPD, dict(late), log=lambda *a: None) == "correct"
    assert recorded == [("x/time_trial", "abc", "correct")]
    _cli.gm_latest_correct = lambda cid: False                       # GM disagrees -> plain runner error, retry
    assert _timed.process_result("x/time_trial", TMPD, dict(late), log=lambda *a: None) == "error:exec"
    assert _timed.process_result("x/time_trial", TMPD, {"result": "no_answer_ids", "detail": {}},
                                 log=lambda *a: None) == "error:exec"
finally:
    (_timed._remember, _timed._keep_failed_attempt, _timed.capture_case, _cli.gm_latest_correct,
     _cli.record_remote_result) = _o
print("ok  late-judged CORRECT (finished body + GM latest CORRECT) counts as the pass; otherwise retry")

# 10) parallel-sets need: a sequential solver whose multi-set case costs >= 0.3 s/set is flagged; a parallel one isn't
ps = TMPD / "psolver"
(ps / "cases" / "auto-mastery-x").mkdir(parents=True)
(ps / "cases" / "auto-mastery-x" / "contract.json").write_text(json.dumps({"answer_ids": [f"set{i}.f" for i in range(1, 6)]}))
(ps / "cases" / "single_solve").mkdir()
(ps / "cases" / "single_solve" / "contract.json").write_text(json.dumps({"answer_ids": ["f"]}))
(ps / "solve.py").write_text("for aid, q in pairs: pass\n")
res = [{"case": "auto-mastery-x", "seconds": 2.0}, {"case": "single_solve", "seconds": 0.9}]
need = orchestrate._parallel_sets_need(ps, res)
assert need == {"case": "auto-mastery-x", "sets": 5, "seconds": 2.0, "per_set": 0.4}, need
assert orchestrate._parallel_sets_need(ps, [{"case": "auto-mastery-x", "seconds": 1.0}]) is None      # 0.2 s/set
(ps / "solve.py").write_text("from lib.common import group_by_set\n")
assert orchestrate._parallel_sets_need(ps, res) is None                                             # already parallel
print("ok  parallel-sets need: sequential multi-set solver flagged; fast or already-parallel solvers left alone")
# 11) a generalize worker can't author expected answers: pre-existing expected.json edits are restored
gch = object.__new__(orchestrate.Chain)
gch.sdir = TMPD / "gsolver"
(gch.sdir / "cases" / "variant-mastery-x").mkdir(parents=True)
(gch.sdir / "cases" / "variant-mastery-x" / "expected.json").write_text("{}")
snap = gch._expected_snapshot()
(gch.sdir / "cases" / "variant-mastery-x" / "expected.json").write_text('{"set1.a": "worker-made"}')
(gch.sdir / "cases" / "new-case").mkdir()
(gch.sdir / "cases" / "new-case" / "expected.json").write_text('{"x": "1"}')       # new cases are not touched
_say = orchestrate.say
orchestrate.say = lambda *a, **k: None
try:
    gch._restore_expected("c", snap)
finally:
    orchestrate.say = _say
assert (gch.sdir / "cases" / "variant-mastery-x" / "expected.json").read_text() == "{}"
assert (gch.sdir / "cases" / "new-case" / "expected.json").read_text() == '{"x": "1"}'
print("ok  expected.json guard: worker edits to existing cases restored, new cases left alone")
print("ALL PASS")
