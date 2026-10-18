"""Day 18 post-run fixes (offline: no GM / Homebase / real claude).
- hb_timed: never re-roll a short clock when the GM says unique_attempts_remaining == 0 (D18 warmups TT: the retry got
  retry_variants_unavailable; a ~1 s solve fit in the 4 s left).
- orchestrate: the TT pre-start fires at the verified handoff, never at a bare single CORRECT (D18 warmups: an
  answer-first CORRECT pre-started a clocked 30 s attempt 25 s before any solver was verified).
- workers: a prompt past MAX_ARG_STRLEN goes to `claude -p` on stdin (D18 prebuild metadata: E2BIG on bwrap).

Run:  source bin/env.sh && python3 tests/test_day18_fixes.py      (exit 0 = all pass)
"""
import datetime as dt
import inspect
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
import hb_timed  # noqa: E402
from hctf import orchestrate, workers  # noqa: E402


def stamp(s):
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=s)).isoformat().replace("+00:00", "Z")


_orig = {k: getattr(hb_timed, k) for k in ("_pool", "_post_start", "_run_solver", "_post")}


def restore():
    for k, v in _orig.items():
        setattr(hb_timed, k, v)


def short_clock_attempt(left, remaining):
    """A clocked 30 s attempt that `start` reconnects to with `left` s on it (pre-started 30-left s ago)."""
    sent = []

    def start(payload, tries=3):
        sent.append(payload)
        if payload.get("op") == "retry":
            return {"error": "retry_variants_unavailable"} if remaining == 0 else {
                "answer_ids": ["message"], "attempt_id": "fresh", "deadline": stamp(30), "started_at": stamp(0),
                "unique_attempts_remaining": remaining - 1}
        return {"answer_ids": ["message"], "attempt_id": "pre", "deadline": stamp(left), "started_at": stamp(left - 30),
                "unique_attempts_remaining": remaining}
    hb_timed._pool = lambda: object()
    hb_timed._post_start = start
    hb_timed._run_solver = lambda *a, **k: SimpleNamespace(stdout=json.dumps({"message": "a-b-c-48"}), stderr="",
                                                           returncode=0)
    hb_timed._post = lambda payload, timeout=None: {"result": "correct", "remaining": 0}
    return hb_timed.run_attempt("test/d18", "challenges/none/solver", op="start"), sent


# 1) no unique attempts left -> run on the short clock, never op=retry
try:
    out, sent = short_clock_attempt(4.0, 0)
    assert [p["op"] for p in sent] == ["start"], sent
    assert out["result"] == "correct" and "rerolled_short" not in out and out["attempt_id"] == "pre", out
    # control: with fresh variants left, a short resumed clock is still waited out and re-rolled (Day 8 rule)
    out, sent = short_clock_attempt(1.0, 3)
    assert [p["op"] for p in sent] == ["start", "retry"], sent
    assert out.get("rerolled_short") is not None and out["attempt_id"] == "fresh", out
finally:
    restore()
print("ok  hb_timed: unique_attempts_remaining 0 -> no short-clock re-roll (runs on the 4 s left); >0 still re-rolls")

# 2) the TT pre-start sits at the verified handoff (after the new-id hold), not at the bare single CORRECT
src = inspect.getsource(orchestrate.Chain._watch_ready)
i_complete = src.index("if cli.is_complete(cid):")
i_hold = src.index("self._newid_hold(")
i_snap = src.index("self._ready_snap = snap")
i_pre = src.index("self._prefetch_tt()")
i_set = src.index("ready.set()", i_snap)
assert src.count("self._prefetch_tt()") == 1, "one pre-start site"
assert i_complete < i_hold < i_snap < i_pre < i_set, (i_complete, i_hold, i_snap, i_pre, i_set)
print("ok  orchestrate: TT pre-start only at the verified handoff (after any new-id hold), right before ready.set()")

# 3) a prompt past MAX_ARG_STRLEN reaches the worker on stdin; a normal one stays on argv
TMPD = Path(tempfile.mkdtemp(dir=str(ROOT / ".run")))
STUB = TMPD / "claude"
STUB.write_text("#!/usr/bin/env python3\n"
                "import json, sys\n"
                "a = sys.argv[1:]\n"
                "on_stdin = a[0] == '-p' and a[1].startswith('--')\n"
                "got = sys.stdin.read() if on_stdin else a[1]\n"
                "print(json.dumps({'type': 'system', 'argv_len': sum(map(len, a)), 'on_stdin': on_stdin,\n"
                "                  'stream': '--input-format' in a, 'prompt_len': len(got), 'tail': got[-12:]}),\n"
                "      flush=True)\n"
                "print(json.dumps({'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'ok',\n"
                "                  'num_turns': 1, 'total_cost_usd': 0.0}), flush=True)\n")
STUB.chmod(0o755)
saved = (workers.CLAUDE_BIN, workers.WORKER_SANDBOX, workers.METRICS)
workers.CLAUDE_BIN, workers.WORKER_SANDBOX, workers.METRICS = str(STUB), False, TMPD / "metrics.tsv"
try:
    env = {"HCTF_CHAL": "metadata-forensics-day-99", "HCTF_BASE": "metadata-forensics-day-99",
           "HCTF_LANE": "metadata-forensics", "HCTF_STAGE": "prebuild"}
    big = "x" * 200_000 + "END-OF-PROMPT"      # past the 128 KiB single-arg cap: E2BIG before the fix
    for prompt, want_stdin in ((big, True), ("THE PROMPT", False)):
        cd = Path(tempfile.mkdtemp(dir=str(TMPD)))
        rc, log = workers.run_local(cd, "prebuild", prompt, env, 30)
        ev = [json.loads(x) for x in Path(log).read_text().splitlines() if '"system"' in x][0]
        assert rc == 0 and ev["on_stdin"] is want_stdin and not ev["stream"], ev
        assert ev["prompt_len"] == len(prompt) and ev["tail"] == prompt[-12:], ev
        assert ev["argv_len"] < 20_000 if want_stdin else True, ev
finally:
    workers.CLAUDE_BIN, workers.WORKER_SANDBOX, workers.METRICS = saved
assert workers._worker_cmd("single", "warmups", "p", stdin_prompt=True)[2] == "--dangerously-skip-permissions"
assert "--input-format" in workers._worker_cmd("single", "warmups")            # warm worker: stream-json as before
print("ok  workers: 200 KB prompt -> stdin (no E2BIG), short prompt -> argv, warm worker still stream-json")
from hctf import duel  # noqa: E402
assert duel.eligible("web")[0] or "duels already running" in duel.eligible("web")[1], duel.eligible("web")
assert "web" in duel.LANES and "binary-reverse-engineering" not in duel.LANES, duel.LANES
print("ok  duel: web lane eligible by default (binary still out)")
print("all Day 18 fix checks passed")
