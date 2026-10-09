"""Homebase credit ledger + Bedrock shadow worker gating (offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_hb_budget.py      (exit 0 = all pass)
"""
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import hbbudget, hbcost, hbshadow, remote  # noqa: E402

d = Path(tempfile.mkdtemp())
hbbudget.LEDGER = d / "ledger.jsonl"

# 1) Ledger day = drop-aligned (13:00 UTC); VM credits = boot->last-seen span x 2/h, max per boot, clipped to the day.
key = hbbudget.day_key()
lo = hbbudget._day_start(key)
assert lo <= time.time() < lo + 86400
boot = lo + 600
hbbudget.record_vm(boot, boot + 1800)
hbbudget.record_vm(boot, boot + 3600)          # later sighting of the same boot: span = 1 h
hbbudget.record_vm(boot, boot + 900)           # an out-of-order earlier sighting never shrinks it
hbbudget.record_vm(lo - 7200, lo + 1800)       # booted before the day started: only the in-day half hour counts
s = hbbudget.spend(key)
assert abs(s["vm_hours"] - 1.5) < 0.01 and abs(s["vm"] - 3.0) < 0.02, s

# 2) AI credits = list USD x CREDITS_PER_USD; rows outside the day are ignored.
hbbudget.record_ai(2.5, "shadow x")
hbbudget.record_ai(0, "nothing")               # zero-cost rows are not written
with open(hbbudget.LEDGER, "a") as f:
    f.write(json.dumps({"ts": lo - 10, "kind": "ai", "usd": 99, "credits": 99, "what": "yesterday"}) + "\n")
    f.write("not json\n")
s = hbbudget.spend(key)
assert s["ai_usd"] == 2.5 and s["runs"] == 1 and abs(s["total"] - 5.5) < 0.05, s

# 3) Governor: VM_RESERVE stays back; the per-run cap shrinks to what is left, never below $0.5.
ok, _ = hbbudget.allow_ai(1.0)
assert ok
hbbudget.record_ai(60 - 5.5 - hbbudget.VM_RESERVE - 0.5, "big")
ok, _ = hbbudget.allow_ai(1.0)
assert not ok
assert hbbudget.ai_cap_usd(8) == 0.5
assert "left" in hbbudget.summary_line()

# 4) Cost of a Claude stream-json log: the result line when present, else per-message usage at Opus 4.x list price
#    (the smoke run on the VM: 7 in / 174 out / 31762 cache-write / 31520 cache-read = $0.2186575).
log = d / "run.log"
msg = {"type": "assistant", "message": {"id": "m1", "usage": {"input_tokens": 7, "output_tokens": 174,
       "cache_creation_input_tokens": 31762, "cache_read_input_tokens": 31520}}}
log.write_text(json.dumps(msg) + "\n" + json.dumps(msg) + "\n")      # same message id twice: counted once
c = hbcost.cost(str(log))
assert abs(c["usd"] - 0.2187) < 0.001 and c["turns"] == 1 and not c["final"], c
log.write_text(json.dumps(msg) + "\n" + json.dumps({"type": "result", "total_cost_usd": 1.23, "num_turns": 9}) + "\n")
assert hbcost.cost(str(log)) == {"usd": 1.23, "turns": 9, "final": True}
assert hbcost.cost(str(d / "missing.log"))["usd"] == 0.0

# 5) Shadow gating: lane allow-list, replay GM, budget, concurrency (slots reserved per chain at eligibility time).
hbbudget.LEDGER = d / "fresh.jsonl"
os.environ.pop("HUNTRESS_GAME_MASTER_URL", None)
assert not hbshadow.ENABLED or os.environ.get("HCTF_HB_SHADOW") == "1"   # opt-in by default
ok, why = hbshadow.eligible("script-analysis", "s")
assert hbshadow.ENABLED or (not ok and "HCTF_HB_SHADOW" in why)
hbshadow.ENABLED = True
orig = (remote.gm_transport, hbshadow.workers.AUTO_HOMEBASE)
remote.gm_transport = lambda: "local"
hbshadow.workers.AUTO_HOMEBASE = True
try:
    assert not hbshadow.eligible("warmups", "w")[0]
    os.environ["HUNTRESS_GAME_MASTER_URL"] = "http://127.0.0.1:18767"
    ok, why = hbshadow.eligible("script-analysis", "s")
    assert not ok and "replay" in why
    os.environ.pop("HUNTRESS_GAME_MASTER_URL")
    hbshadow._live.clear()
    assert hbshadow.eligible("script-analysis", "s")[0]
    assert hbshadow.eligible("binary-reverse-engineering", "b")[0]
    ok, why = hbshadow.eligible("script-analysis", "s2")
    assert not ok and "already running" in why                        # MAX_CONCURRENT=2 reserved
    hbshadow._live.clear()
    hbbudget.record_ai(59, "spent")
    ok, why = hbshadow.eligible("script-analysis", "s")
    assert not ok and "budget" in why
finally:
    remote.gm_transport, hbshadow.workers.AUTO_HOMEBASE = orig
    hbshadow._live.clear()

# 6) Merge: VM confirmations land in local state once; a full VM CORRECT marks the local single complete.
from hctf import cli  # noqa: E402

store = {}
cid = "script-analysis-day-99-x"
mdir = d / "mode"
mdir.mkdir()
cli_orig = (cli.load, cli.cdir, cli.confirmed_answers, cli.is_complete, cli.record_remote_result, cli.chal_lock)
recs = []
cli.load = lambda c, n: {"attempt_id": "A1", "answer_ids": ["a", "b"]} if n == "start.json" else None
cli.cdir = lambda c: mdir
cli.confirmed_answers = lambda c, att=None: dict(store)
cli.is_complete = lambda c: set(store) >= {"a", "b"}
cli.record_remote_result = lambda c, att, ans, kind, body=None: (recs.append((att, dict(ans), kind)), store.update(ans))
import contextlib  # noqa: E402
cli.chal_lock = lambda c: contextlib.nullcontext()
cli.attempt_id = getattr(cli, "attempt_id")
try:
    sh = hbshadow.Shadow.__new__(hbshadow.Shadow)
    sh.cid, sh.say, sh._merged, sh.correct = cid, (lambda *a: None), {}, False
    sh._merge({"A1": {"a": "1"}}, False)
    assert recs == [("A1", {"a": "1"}, "accepted")], recs
    sh._merge({"A1": {"a": "1"}}, False)                                # nothing new: no second record
    assert len(recs) == 1
    sh._merge({"A1": {"a": "1", "b": "2"}, "OLD": {"z": "9"}}, True)   # other attempts ignored; full -> correct
    assert recs[-1] == ("A1", {"a": "1", "b": "2"}, "correct") and sh.correct, recs
finally:
    (cli.load, cli.cdir, cli.confirmed_answers, cli.is_complete, cli.record_remote_result, cli.chal_lock) = cli_orig

print("test_hb_budget: all checks passed")
