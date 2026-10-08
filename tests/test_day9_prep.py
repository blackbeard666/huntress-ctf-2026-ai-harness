"""Behavior checks for the Day 9 prep: compounding probe, Mastery delta, scoped failed-variant pull, warm workers,
probe overlap, Mastery speed gate, GM backoff cap (offline: no GM / no Homebase / no real workers).

Run:  source bin/env.sh && python3 tests/test_day9_prep.py      (exit 0 = all pass)
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
from hctf import compound, orchestrate, timed, workers  # noqa: E402
import gm  # noqa: E402

# 1) compounding: hard vs soft misses (soft = answered nothing: a retired answer-id scheme, not a lost concept)
res = [
    {"day": 1, "case": "single_solve", "path": "x", "expected": 9, "correct": 0, "answered": 0, "total": 9, "wrong": {},
     "error": None, "seconds": 0.1},
    {"day": 3, "case": "single_solve", "path": "y", "expected": 24, "correct": 23, "answered": 24, "total": 24,
     "wrong": {"d01_x": {"expected": "[]", "got": "[\"ret\"]"}}, "error": None, "seconds": 0.1},
    {"day": 4, "case": "auto-mastery-1", "path": "z", "expected": 3, "correct": 3, "answered": 3, "total": 3,
     "wrong": {}, "error": None, "seconds": 0.1},
    {"day": 5, "case": "single_solve", "path": "w", "expected": 1, "correct": 0, "answered": 0, "total": 1,
     "wrong": {}, "error": "exit 1: boom", "seconds": 0.1},
]
assert len(compound.misses(res)) == 3
assert [r["day"] for r in compound.hard_misses(res)] == [3, 5]
txt = compound.summary(res)
assert "Day 3" in txt and "Day 5" in txt and "Day 1" not in txt, txt
# real run: today's mobile solver vs every earlier mobile day (fast, local)
msd = ROOT / "challenges/day08/mobile-cleartext-session/solver"
if (msd / "solve.py").exists():
    real = compound.check(msd)
    assert real and not compound.hard_misses(real), compound.summary(real)
    assert {r["day"] for r in real} >= {1, 7}
print("ok  compounding probe: hard/soft split; D8 mobile solver passes every earlier mobile day")

# 2) Mastery delta: what the timed contracts ask that the Single doesn't (positive control: D7 metadata replay)
d7 = ROOT / "challenges/day07/metadata-seven-zip-no-relation"
single = json.loads(((d7 / "single_solve" / "start.json") if (d7 / "single_solve" / "start.json").exists()
                     else (d7 / "single_solve" / "contract.json")).read_text())
rep = d7 / "solver/cases/auto-mastery-0d13f2e8/contract.json"
if rep.exists():
    delta = orchestrate.mastery_delta(single, [json.loads(rep.read_text())])
    assert "d04-jpeg-001" in delta and ".png" in delta, delta
same = {"answer_ids": ["set1.a", "set2.a"], "questions": [{"id": "set1.a", "artifact": "delivery 1: x.zip"},
                                                           {"id": "set2.a", "artifact": "delivery 2: x.zip"}]}
assert orchestrate.mastery_delta({"answer_ids": ["a"], "questions": [{"id": "a", "artifact": "x.zip"}]}, [same]) == ""
print("ok  mastery_delta: earlier-day ids + artifact kinds detected; N x Single -> no delta")

# 3) scoped pull: fewest sets covering the failing families
contract = {"answer_ids": [f"set{s}.{f}" for s in (1, 2, 3) for f in ("d01_dis", "d08_x")],
            "questions": [{"id": f"set{s}.{f}", "artifact": f"delivery {s}: evidence.zip"}
                          for s in (1, 2, 3) for f in ("d01_dis", "d08_x")]}
pick = workers.deliveries_for
assert pick({"wrong": [["set1.d01_dis", "x"], ["set2.d01_dis", "x"]]}, contract) == ["delivery 1: evidence.zip"]
assert pick({"missing": ["set2.d08_x", "set3.d01_dis", "set3.d08_x"]}, contract) == ["delivery 3: evidence.zip"]
assert pick({"result": "solver_error", "bad_sets": ["set2"]}, contract) == ["delivery 2: evidence.zip"]
assert pick({"result": "solver_error"}, contract) == ["delivery 1: evidence.zip"]
one = {"answer_ids": ["a", "b"], "questions": [{"id": "a", "artifact": "evidence.zip -> x"}, {"id": "b", "artifact": "evidence.zip"}]}
assert pick({"wrong": [["a", "1"]]}, one) == ["evidence.zip"]
print("ok  deliveries_for: minimal covering set; one representative when unlocalized; single-delivery contracts whole")

# 4) trim_to_present: a subset case's contract only asks what its bytes can answer (artifacts[] matched by sha256)
art = Path(tempfile.mkdtemp())
(art / "delivery 2: evidence.zip").write_bytes(b"two")
full = {"answer_ids": ["set1.a", "set2.a"],
        "questions": [{"id": "set1.a", "artifact": "delivery 1: evidence.zip"},
                      {"id": "set2.a", "artifact": "delivery 2: evidence.zip"}],
        "artifacts": [{"sha256": hashlib.sha256(b"one").hexdigest()}, {"sha256": hashlib.sha256(b"two").hexdigest()}]}
t = timed.trim_to_present(full, art)
assert t["answer_ids"] == ["set2.a"] and [q["id"] for q in t["questions"]] == ["set2.a"]
assert t["artifacts"] == [full["artifacts"][1]]
(art / "delivery 1: evidence.zip").write_bytes(b"one")
assert timed.trim_to_present(full, art) is full
print("ok  trim_to_present: contract + artifacts[] trimmed to the deliveries present; unchanged when complete")

# 5) pass captures wait a grace period before checking for an in-flight attempt (TT pass -> Mastery kickoff gap)
import inspect  # noqa: E402
src = inspect.getsource(timed.process_result)
assert src.index("CAPTURE_GRACE") < src.index("wait_idle()") < src.index("pull()")
print("ok  capture: grace for the next mode's kickoff, then wait_idle, then pull")

# 6) Mastery speed gate estimate: (2-set mastery-shape seconds / 2) x sets x 1.5
mc = Path(tempfile.mkdtemp()) / "contract.json"
mc.write_text(json.dumps({"answer_ids": [f"set{i}.x" for i in range(1, 6)]}))
summ = {"results": [{"mutation": "mastery-shape", "ok": True, "seconds": 3.4}]}
assert orchestrate.mastery_estimate(summ, mc) == 12.75                      # no base timing: shape / 2 per set
summ["base_seconds"] = 1.75                                                # binary-like: 1.65 s per set, 0.1 s startup
assert orchestrate.mastery_estimate(summ, mc) == 12.47, orchestrate.mastery_estimate(summ, mc)
mc.write_text(json.dumps({"answer_ids": [f"set{i}.message" for i in range(1, 39)]}))
light = {"base_seconds": 0.15, "results": [{"mutation": "mastery-shape", "ok": True, "seconds": 0.2}]}
assert orchestrate.mastery_estimate(light, mc) < 3.2, orchestrate.mastery_estimate(light, mc)   # was 5.7 (warmups)
assert orchestrate.mastery_estimate({"results": []}, mc) is None
print("ok  Mastery speed estimate from the mutation probe's mastery-shape run")

# 7) GM backoff without Retry-After: 2, 4, 4, ... (cap) and ~30 s total over the retries
waits = [gm._retry_after({}, a) for a in range(gm.RATE_RETRIES)]
assert waits[:3] == [2.0, 4.0, 4.0] and max(waits) <= gm.BACKOFF_CAP and 25 <= sum(waits) <= 40, waits
assert gm._retry_after({"Retry-After": "7"}, 0) == 7.0
print(f"ok  GM backoff: {waits} (total {sum(waits):g}s)")

# 8) stop gate lets a WARM worker end its warm-up turn while the flag exists
flag = Path(tempfile.mkdtemp()) / ".warm-x"
flag.write_text("warm")
env = dict(os.environ, HCTF_STAGE="single", HCTF_CHAL="warmups-day-08", HCTF_WARM_FLAG=str(flag))
r = subprocess.run([sys.executable, str(ROOT / ".claude/hooks/stop_gate.py")], env=env, capture_output=True, text=True,
                   timeout=60)
assert r.returncode == 0 and '"block"' not in r.stdout, (r.stdout, r.stderr[-300:])
print("ok  stop gate: warm-up turn allowed to end while the warm flag exists")

# 9) warm worker end to end with a fake `claude` (echoes each stdin message as an event, exits at EOF)
stub_dir = Path(tempfile.mkdtemp(dir=str(ROOT / ".run")))
(stub_dir / "claude").write_text("#!/usr/bin/env python3\n"
                                 "import sys, json\n"
                                 "print(json.dumps({'type': 'system', 'argv': sys.argv[1:]}), flush=True)\n"
                                 "for line in (sys.stdin if '--input-format' in sys.argv else []):\n"
                                 "    m = json.loads(line)['message']['content']\n"
                                 "    print(json.dumps({'type': 'echo', 'text': m[:40]}), flush=True)\n")
(stub_dir / "claude").chmod(0o755)
saved = (workers.CLAUDE_BIN, workers.WORKER_SANDBOX)
workers.CLAUDE_BIN = str(stub_dir / "claude")      # never the real claude (PATH puts ~/.local/bin first)
workers.WORKER_SANDBOX = False
try:
    cd = Path(tempfile.mkdtemp(dir=str(ROOT / ".run")))
    w = workers.WarmWorker(cd, "single", "WARM: reply READY", {"HCTF_LANE": "warmups"})
    assert w.alive() and w.flag.exists()
    time.sleep(0.5)
    rc, log = workers.run_local(cd, "single", "unused", {}, 30, warm=w, warm_task="GO: triage here")
    lines = [json.loads(x) for x in Path(log).read_text().splitlines() if x.strip()]
    assert rc == 0 and not w.flag.exists(), rc
    assert [x.get("text") for x in lines if x.get("type") == "echo"] == ["WARM: reply READY", "GO: triage here"], lines
    argv = next(x["argv"] for x in lines if x.get("type") == "system")
    assert "--input-format" in argv and "--tools" in argv and "unused" not in argv, argv
    assert lines[0].get("event") == "warm_launch"
    # a dead warm worker -> cold launch with the prompt instead
    w2 = workers.WarmWorker(cd, "single", "WARM", {})
    w2.p.kill()
    w2.p.wait()
    rc, log = workers.run_local(cd, "single", "COLD PROMPT", {}, 30, warm=w2, warm_task="GO")
    argv = next(json.loads(x)["argv"] for x in Path(log).read_text().splitlines() if '"system"' in x)
    assert rc == 0 and "COLD PROMPT" in argv and "--input-format" not in argv, argv
finally:
    workers.CLAUDE_BIN, workers.WORKER_SANDBOX = saved
print("ok  warm worker: message 1 at launch, task on handoff, flag cleared; dead warm -> cold launch")

# 10) probe overlap: the first Time Trial does NOT wait for the mutation/compound probes; Mastery does
class _Fut:
    def __init__(self, val, done):
        self.val, self._done = val, done

    def done(self):
        return self._done

    def result(self, timeout=None):
        self._done = True
        return self.val


ch = object.__new__(orchestrate.Chain)
ch.base, ch.sdir, ch.lane = "b", Path(tempfile.mkdtemp()), "warmups"
ch.entries = {"time_trial": {"id": "b/time_trial"}, "mastery": {"id": "b/mastery"}}
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
ch._mut_pre_fut = _Fut(("", [], {}), done=False)
ch._cmp_pre_fut = _Fut(("Day 3 `x`: 1/2 verified fields right", [{"day": 3, "path": "x", "error": None,
                                                                 "answered": 1}], []), done=False)
gens, runs = [], []
patches = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (timed, "run"): lambda cid, sdir, log=None, **k: (runs.append(cid), "correct")[1],
    (timed, "last_result"): lambda cid: None,
    (orchestrate.Chain, "generalize"): lambda self, cid, wrong=None, fixed=None, diag=None: gens.append(diag),
    (orchestrate.Chain, "_family_pre_result"): lambda self, **k: ("", []),
    (orchestrate.Chain, "_mastery_speed_gate"): lambda self, cid: None,
    (compound, "adopt"): lambda sdir, hard, limit=6: len(hard),
}
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert ch.timed_stage("time_trial") is True and runs == ["b/time_trial"] and not gens, (runs, gens)
    assert ch.timed_stage("mastery") is True and runs[-1] == "b/mastery"
    assert len(gens) == 1 and "compound_pre" in gens[0], gens
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
print("ok  probe overlap: TT runs without waiting; Mastery awaits the probes and generalizes on a compounding miss")
print("ALL PASS")
