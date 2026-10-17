"""Answer-first worker on a Single Solve (orchestrate.AnswerFirst, PLAN_SUB2MIN.md P2). Offline: no GM, no LLM.
- eligibility: lane set, field cap, concurrency cap
- the prompt lists every field with its format, the bytes dir and the triage; `.live_fields.json` tells the stop gate
  what the worker owes (stage live)
- the watcher posts every newly GM-confirmed value to the chain worker's inbox and ends the worker at CORRECT
- start() waits for the reuse race (bounded) and skips when the single is already complete
- run_worker passes env_extra (effort / log pool) through

Run:  source bin/env.sh && python3 tests/test_answer_first.py      (exit 0 = all pass)
"""
import json
import os
import re
import shutil
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["HCTF_ANSWER_FIRST"] = "1"
from hctf import cli, inbox, orchestrate  # noqa: E402

WORK = ROOT / ".run" / "af-test"
shutil.rmtree(WORK, ignore_errors=True)
CID = "metadata-forensics-day-99-answer-first"
CDIR = WORK / "chal" / "single_solve"
CDIR.mkdir(parents=True)
_ocdir = cli.cdir
cli.cdir = lambda cid: CDIR
if hasattr(orchestrate.timed, "cli"):
    orchestrate.timed.cli.cdir = cli.cdir

start = {"attempt_id": "att-1234-5678", "answer_ids": ["flag", "author"],
         "questions": [{"id": "flag", "question": "What is the flag hidden in the document?", "artifact": "doc.docx -> core.xml",
                        "answer_format": {"kind": "string", "pattern": "[0-9a-f]{32}"}},
                       {"id": "author", "question": "Who authored it?", "artifact": "doc.docx -> core.xml",
                        "answer_format": {"kind": "string"}}]}
(CDIR / "start.json").write_text(json.dumps(start))
(CDIR / "triage.md").write_text("# triage\n\n## STATUS\n- doc.docx: OOXML, core.xml has dc:creator\n")
art = CDIR / "artifacts" / "2026"
art.mkdir(parents=True)
(art / "doc.docx").write_bytes(b"PK\x03\x04fake")
(CDIR / "artifacts" / "latest").symlink_to(art)
sdir = WORK / "chal" / "solver"
sdir.mkdir()

said = []
orchestrate.say = said.append
calls = []
stop_seen = threading.Event()


def fake_run_worker(cid, stage, prompt, timeout, urgent=False, prefer_homebase=False, stop=None, warm=None,
                    warm_task=None, env_extra=None):
    """Stands in for the claude worker: 'submits' one accepted field, then the CORRECT one, and waits for `stop`."""
    calls.append({"stage": stage, "urgent": urgent, "env": dict(env_extra or {}), "prompt": prompt, "timeout": timeout})
    time.sleep(0.3)
    with open(CDIR / "submissions.jsonl", "a") as f:
        f.write(json.dumps({"ts": "x", "attempt": start["attempt_id"], "answers": {"author": "Mallory"}, "kind": "accepted",
                            "confirmed": ["author"]}) + "\n")
    (CDIR / "confirmed.json").write_text(json.dumps({start["attempt_id"]: {"author": "Mallory"}}))
    time.sleep(1.3)
    with open(CDIR / "submissions.jsonl", "a") as f:
        f.write(json.dumps({"ts": "x", "attempt": start["attempt_id"], "answers": {"flag": "a" * 32}, "kind": "correct",
                            "confirmed": ["flag"]}) + "\n")
    (CDIR / "confirmed.json").write_text(json.dumps({start["attempt_id"]: {"author": "Mallory", "flag": "a" * 32}}))
    if stop.wait(10):
        stop_seen.set()
    return 0


notes = []
chain = SimpleNamespace(lane="metadata-forensics", base=CID, sdir=sdir, root=WORK / "chal", run_worker=fake_run_worker,
                        _deliver_note=lambda cid, note, key: notes.append((key, note)) or inbox.post(CDIR, note, key=key))

fails = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f": {detail}"[:600]))
    if not cond:
        fails.append(name)


# 1) eligibility
ok, why = orchestrate.answer_first_eligible("metadata-forensics", 2)
check("eligible: metadata single with 2 fields", ok, why)
ok, why = orchestrate.answer_first_eligible("metadata-forensics", orchestrate.ANSWER_FIRST_MAX_FIELDS + 1)
check("not eligible above the field cap", not ok and "cap" in why, why)
ok, why = orchestrate.answer_first_eligible("web", 1)
check("not eligible outside HCTF_ANSWER_FIRST_LANES", not ok, why)
with orchestrate._af_lock:
    orchestrate._af_live.update({"a", "b", "c"})
ok, why = orchestrate.answer_first_eligible("warmups", 1)
check("not eligible when the concurrency cap is reached", not ok and "already running" in why, why)
with orchestrate._af_lock:
    orchestrate._af_live.clear()

# 2) prompt + stop-gate file + watcher + inbox + stop at CORRECT
af = orchestrate.AnswerFirst(chain, CID)
check("prompt lists every field with its format and the bytes dir",
      all(f"`{a}`" in af.prompt for a in ("flag", "author")) and "[0-9a-f]{32}" in af.prompt
      and "artifacts/2026" in af.prompt and "core.xml has dc:creator" in af.prompt and "hctf submit " in af.prompt
      and not re.search(r"\{[a-z_]+\}", af.prompt),
      af.prompt[:400])
race = threading.Event()
t0 = time.time()
af.start(race_done=race)
time.sleep(0.5)
check("start() waits for the reuse race (bounded)", not calls and not af.started.is_set())
race.set()
af.started.wait(5)
for _ in range(50):
    if calls:
        break
    time.sleep(0.1)
check("worker launched after the race finished", af.started.is_set() and calls and calls[0]["stage"] == "live",
      str(calls)[:200])
check(".live_fields.json names the attempt + every field (stop gate, stage live)",
      json.loads((CDIR / ".live_fields.json").read_text()) == {"attempt": start["attempt_id"], "fields": ["flag", "author"]})
check("run_worker got env_extra (effort + log pool) and urgent=True",
      calls[0]["urgent"] and calls[0]["env"].get("HCTF_X_EFFORT") == orchestrate.ANSWER_FIRST_EFFORT
      and calls[0]["env"].get("HCTF_LOG_POOL") == "answer-first", str(calls[0]["env"]))
af.done.wait(15)
check("watcher posted the confirmed value to the chain worker's inbox before the single was complete",
      any("Mallory" in n and "author" in n and "Still open: ['flag']" in n for _k, n in notes), str(notes)[:400])
check("... and the inbox file holds it (key answer-first)",
      any(t for t in inbox.texts(CDIR) if "ANSWER-FIRST" in t), str(inbox.texts(CDIR))[:200])
check("worker ended the moment the single went CORRECT (stop event set within the stand-in's wait)",
      stop_seen.is_set() and af.stop_evt.is_set() and time.time() - t0 < 12, f"{time.time() - t0:.1f}s")
check("the CORRECT was announced", any("ending the answer-first worker" in s for s in said), str(said)[-3:])

# 3) a single already complete when the race ends: no worker
calls.clear()
af2 = orchestrate.AnswerFirst(chain, CID)
r2 = threading.Event()
r2.set()
af2.start(race_done=r2)
af2.done.wait(5)
check("no worker when the single is already complete", not calls and any("already complete" in s for s in said[-3:]),
      str(said[-3:]))

# 4) Chain.run_worker accepts env_extra (signature check on the real method)
import inspect  # noqa: E402
check("Chain.run_worker has env_extra", "env_extra" in inspect.signature(orchestrate.Chain.run_worker).parameters)
check("Chain._single launches the answer-first worker beside the duel",
      "AnswerFirst(self, cid)" in inspect.getsource(orchestrate.Chain._single)
      and "af.stop()" in inspect.getsource(orchestrate.Chain._single))

cli.cdir = _ocdir
shutil.rmtree(WORK, ignore_errors=True)
if fails:
    print(f"\n{len(fails)} FAILED: {fails}")
    sys.exit(1)
print("\nall answer-first checks passed")
