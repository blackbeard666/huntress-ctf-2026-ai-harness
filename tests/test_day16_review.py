"""Day 16 pre-drop review (rehearsal D15 A/B arms + main D15 run). Offline: no GM / Homebase / workers.
- GM submit replies are stored without the re-sent challenge text; is_complete survives a torn line and is cached.
- `already_solved` is a final verdict: submit short-circuits on a CORRECT attempt, the bisect stops.
- Stopping a worker also kills its background processes (other session), never another pool's (duel).
- An untimed pool skips the pre-Mastery generalize + speed gate; held probe results reach a failure generalize.
- The label table flags a GENERATION SPLIT (GM label changed from one attempt-start date on).
- Prebuild gate runs only the suites a lane can break.

Run:  source bin/env.sh && python3 tests/test_day16_review.py      (exit 0 = all pass)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, orchestrate, prebuild, timed, workers  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="hctf-d16r-"))
_cdir = cli.cdir
cli.cdir = lambda cid: TMP / cid

# 1) slim bodies + robust/cached is_complete
big = {"result": "accepted", "remaining": 3, "questions": [{"q": "x" * 1000}] * 50, "prompt": "p" * 5000}
slim = cli.slim_body(big)
assert slim == {"result": "accepted", "remaining": 3}, slim
cd = TMP / "c1"
cd.mkdir()
(cd / "start.json").write_text(json.dumps({"attempt_id": "A1", "answer_ids": ["a", "b"]}))
subs = cd / "submissions.jsonl"
subs.write_text(json.dumps({"attempt": "A1", "kind": "accepted", "answers": {"a": "1"}}) + "\n"
                + '{"attempt": "A1", "kind": "corr')   # torn: a writer mid-append
assert cli.is_complete("c1") is False
with open(subs, "a") as f:
    f.write("\n" + json.dumps({"attempt": "A1", "kind": "correct", "answers": {"b": "2"}}) + "\n")
assert cli.is_complete("c1") is True
assert cli._correct_attempts(subs) == {"A1"}
print("ok  slim GM bodies; is_complete skips a torn line, cached by size+mtime")

# 2) already_solved: verdict kind, local short-circuit, EXIT 0
assert cli.result_kind({"result": "already_solved"}) == "already_solved"
assert cli.EXIT["already_solved"] == 0
calls = []
_call = cli.call
cli.call = lambda *a, **k: calls.append(a) or {"http": 200, "body": {"result": "accepted"}}
kind, body, probs = cli.submit("c1", {"a": "1"}, force=True)
assert kind == "already_solved" and body.get("local") and not probs and not calls, (kind, body, calls)
cli.call = _call
print("ok  submit on a CORRECT attempt: already_solved locally, no GM call")

# 3) stray background processes of an ended worker are killed; another pool's (duel) are not
env_main = {"HCTF_CHAL": "d16r-x", "HCTF_STAGE": "single"}
penv = dict(os.environ, **env_main)
penv.pop("HCTF_LOG_POOL", None)
p_main = subprocess.Popen(["sleep", "60"], env=penv, start_new_session=True)
p_duel = subprocess.Popen(["sleep", "60"], env=dict(penv, HCTF_LOG_POOL="duel"), start_new_session=True)
time.sleep(0.2)
n = workers._kill_strays(env_main)
time.sleep(0.2)
assert p_main.poll() is not None and p_duel.poll() is None and n == 1, (n, p_main.poll(), p_duel.poll())
p_duel.kill()
p_main.wait()
p_duel.wait()
print("ok  _kill_strays: the worker's own background process killed, the duel's left alone")

# 4) untimed pool: no pre-Mastery generalize, held results go to the failure generalize
_last = timed.last_result
results = {}
timed.last_result = lambda cid: results.get(cid)
ch = SimpleNamespace(entries={"time_trial": {"id": "tt"}, "mastery": {"id": "m"}})
results["tt"] = {"attempt_id": "x", "deadline": None, "run_for_time": False, "result": "correct"}
assert orchestrate.Chain._tt_pool_untimed(ch) is True
results["tt"] = {"attempt_id": "x", "deadline": "2026-10-14T13:00:56.008Z", "result": "correct"}
assert orchestrate.Chain._tt_pool_untimed(ch) is False
results["tt"] = {"attempt_id": "x", "deadline": None, "run_for_time": True}
assert orchestrate.Chain._tt_pool_untimed(ch) is False
results.pop("tt")
assert orchestrate.Chain._tt_pool_untimed(ch) is False
timed.last_result = _last
src = Path(orchestrate.__file__).read_text()
assert 'held = getattr(self, "_late_held", None)' in src and "self._late_held = late" in src
print("ok  _tt_pool_untimed: regular-pool TT -> untimed Mastery; clocked / HoF / unknown -> not")

# 5) label table: GENERATION SPLIT
assert "changed between 2026-10-14 and 2026-10-15" in orchestrate.generation_split({"2026-10-03", "2026-10-14"},
                                                                                   {"2026-10-15"})
assert orchestrate.generation_split({"2026-10-03", "2026-10-15"}, {"2026-10-10"}) == ""
assert orchestrate.generation_split({"2026-10-03"}, set()) == ""
sd = TMP / "solver"
for name, day, lab in (("compound-d12-a", "2026-10-12", "delayed"), ("compound-d14-b", "2026-10-14", "delayed"),
                       ("auto-mastery-c", "2026-10-15", "percent"), ("single_solve", "2026-10-15", "percent")):
    (sd / "cases" / name).mkdir(parents=True)
    (sd / "cases" / name / "contract.json").write_text(json.dumps({"started_at": f"{day}T13:00:00.000Z"}))
    (sd / "cases" / name / "expected.json").write_text(json.dumps({"batch-1-expansion": lab}))
res = [{"case": "compound-d12-a", "ok": False, "diff": {"batch-1-expansion": {"expected": "delayed", "got": "percent"}}},
       {"case": "compound-d14-b", "ok": False, "diff": {"batch-1-expansion": {"expected": "delayed", "got": "percent"}}},
       {"case": "auto-mastery-c", "ok": True, "diff": {}}, {"case": "single_solve", "ok": True, "diff": {}}]
tab = orchestrate.label_table(sd, res, [("batch-1-expansion", "percent")])
if orchestrate.label_only_failure([("batch-1-expansion", "percent")]):
    assert "GENERATION SPLIT" in tab and "2026-10-14 and 2026-10-15" in tab, tab
    print("ok  label table flags the D15 batch-expansion GENERATION SPLIT")
else:
    print("skip label table: batch expansion is not a cacheable label family here")
gen = (ROOT / "hctf/prompts/generalize.md").read_text()
assert "GENERATION SPLIT" in gen and "do NOT re-run the whole suite before your first edit" in gen

# 6) prebuild: only the suites a lane can break
assert prebuild.gate_suites("binary-reverse-engineering", prebuild.LANES["binary-reverse-engineering"]) == []
meta = prebuild.gate_suites("metadata-forensics", prebuild.LANES["metadata-forensics"])
assert "tests/test_meta_lane.py" in meta and "tests/test_orchestrate.py" not in meta and "tests/test_codec.py" not in meta
scr = prebuild.gate_suites("script-analysis", prebuild.LANES["script-analysis"])
assert {"tests/test_lane_fixtures.py", "tests/test_codec.py", "tests/test_day7_fixes.py"} <= set(scr), scr
assert "tests/test_day6_fixes.py" not in scr
assert "Never loop over `tests/test_*.py`" in (ROOT / "hctf/prompts/prebuild.md").read_text()
print(f"ok  prebuild gate suites: binary none, metadata {len(meta)}, script {len(scr)}")

cli.cdir = _cdir
shutil.rmtree(TMP, ignore_errors=True)
print("ALL PASS")
