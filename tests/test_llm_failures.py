"""LLM-side worker failures + per-worker metrics (ilio-mini gaps; offline, fake `claude`).

Run:  source bin/env.sh && python3 tests/test_llm_failures.py      (exit 0 = all pass)
"""
import json
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import workers  # noqa: E402

TMPD = Path(tempfile.mkdtemp(dir=str(ROOT / ".run")))
STUB = TMPD / "claude"
# Fake claude: plays the scripted results in $STUB_PLAN (one per launch, counted in $STUB_PLAN.n), echoing its argv.
STUB.write_text("#!/usr/bin/env python3\n"
                "import json, os, sys\n"
                "plan = json.load(open(os.environ['STUB_PLAN']))\n"
                "cnt = os.environ['STUB_PLAN'] + '.n'\n"
                "n = int(open(cnt).read()) if os.path.exists(cnt) else 0\n"
                "open(cnt, 'w').write(str(n + 1))\n"
                "print(json.dumps({'type': 'system', 'argv': sys.argv[1:]}), flush=True)\n"
                "print(json.dumps(plan[min(n, len(plan) - 1)]), flush=True)\n")
STUB.chmod(0o755)


def result(is_error=False, text="done", reason="completed", subtype="success", cost=0.5, turns=7):
    return {"type": "result", "subtype": subtype, "is_error": is_error, "result": text, "terminal_reason": reason,
            "session_id": "s1", "num_turns": turns, "total_cost_usd": cost, "ttft_ms": 1500,
            "modelUsage": {"claude-opus-5-5": {"inputTokens": 10, "outputTokens": 200, "cacheReadInputTokens": 900,
                                               "cacheCreationInputTokens": 90, "costUSD": cost}}}


AUTH = result(True, "Failed to authenticate: OAuth session expired and could not be refreshed", "api_error")
LIMIT = result(True, "Claude AI usage limit reached|1793525161", "api_error")
OVERLOAD = result(True, "API Error: 529 Overloaded", "api_error")
MAXTURNS = result(True, None, "max_turns", "error_max_turns")


def run(plan, timeout=30, stop=None):
    pf = TMPD / f"plan-{time.time_ns()}.json"
    pf.write_text(json.dumps(plan))
    import os
    os.environ["STUB_PLAN"] = str(pf)
    cd = Path(tempfile.mkdtemp(dir=str(TMPD)))
    env = {"HCTF_CHAL": "warmups-day-99", "HCTF_BASE": "warmups-day-99", "HCTF_LANE": "warmups", "HCTF_STAGE": "single"}
    rc, log = workers.run_local(cd, "single", "THE PROMPT", env, timeout, stop=stop)
    launches = int(Path(str(pf) + ".n").read_text())
    argv = [json.loads(x)["argv"] for x in Path(log).read_text().splitlines() if '"system"' in x][0]
    return rc, log, launches, argv


saved = (workers.CLAUDE_BIN, workers.WORKER_SANDBOX, workers.METRICS, workers.API_BACKOFF, workers.API_MIN_LEFT)
workers.CLAUDE_BIN, workers.WORKER_SANDBOX = str(STUB), False   # never the real claude
workers.METRICS = TMPD / "metrics.tsv"
workers.API_BACKOFF, workers.API_MIN_LEFT = [0.2], 0.0
try:
    # 1) classifier on the real failure shapes seen in our logs
    for ev, want in ((result(), "ok"), (AUTH, "auth"), (LIMIT, "limit"), (OVERLOAD, "transient"), (MAXTURNS, "max_turns")):
        f = TMPD / "one.log"
        f.write_text(json.dumps({"type": "system", "subtype": "model_refusal_fallback"}) + "\n" + json.dumps(ev) + "\n")
        o = workers.worker_outcome(f)
        assert o["outcome"] == want, (want, o)
        assert o["refusal_fallbacks"] == 1 and o["out_tok"] == 200 and o["cost_usd"] == 0.5, o
    (TMPD / "empty.log").write_text('{"type":"system"}\n')
    assert workers.worker_outcome(TMPD / "empty.log")["outcome"] == "no_result"
    print("ok  worker_outcome: ok / auth / limit / transient / max_turns / no_result, tokens + refusal fallbacks")

    # 2) clean run: one launch, rc 0, one metrics row
    rc, log, n, argv = run([result()])
    assert rc == 0 and n == 1, (rc, n)
    rows = workers.read_metrics()
    assert len(rows) == 1 and rows[0]["outcome"] == "ok" and rows[0]["cost_usd"] == 0.5 and rows[0]["turns"] == 7, rows
    assert rows[0]["base"] == "warmups-day-99" and rows[0]["stage"] == "single", rows
    print("ok  clean worker: single launch, metrics row (cost, turns, chain, stage)")

    # 3) auth failure: AUTH_RC at once, no relaunch
    rc, log, n, argv = run([AUTH, result()])
    assert rc == workers.AUTH_RC and n == 1, (rc, n)
    print("ok  auth failure: AUTH_RC, no relaunch")

    # 4) usage limit then overload then success: relaunched twice with the resume note, same prompt
    rc, log, n, argv = run([LIMIT, OVERLOAD, result()])
    assert rc == 0 and n == 3, (rc, n)
    prompt = argv[argv.index("-p") + 1]
    assert prompt.startswith("THE PROMPT") and "ended on an API error" in prompt and "529" in prompt, prompt[:300]
    print("ok  limit/overload: backed off + relaunched (fresh session, same prompt + resume note) until it finished")

    # 5) relaunch budget is bounded
    rc, log, n, argv = run([OVERLOAD])
    assert n == workers.API_RELAUNCHES + 1, (rc, n)
    # ...and no relaunch when the stage has too little time left
    workers.API_MIN_LEFT = 3600.0
    rc, log, n, argv = run([OVERLOAD, result()])
    assert n == 1, n
    workers.API_MIN_LEFT = 0.0
    print("ok  relaunches bounded by HCTF_API_RELAUNCHES and by the stage time left")

    # 6) stop during the backoff -> STOPPED_RC, no relaunch
    workers.API_BACKOFF = [5.0]
    ev = threading.Event()
    threading.Timer(0.5, ev.set).start()
    t = time.time()
    rc, log, n, argv = run([OVERLOAD, result()], stop=ev)
    assert rc == workers.STOPPED_RC and n == 1 and time.time() - t < 4, (rc, n)
    workers.API_BACKOFF = [0.2]
    print("ok  stop during backoff: STOPPED_RC, no relaunch")

    # 7) report: totals + non-ok exits listed
    rep = workers.metrics_report()
    assert "TOTAL" in rep and "auth" in rep and "non-ok worker exits" in rep, rep
    assert workers.chain_cost()["warmups-day-99"] > 0
    print("ok  hctf cost report: totals, non-ok exits, per-chain cost for the dash")

    # 8) a worker killed at CORRECT (no session-final result; warm-up result first) -> stream-summed tokens, est cost,
    #    outcome `stopped` (not listed as non-ok)
    def asst(mid, out_tok):
        return {"type": "assistant", "message": {"id": mid, "model": "claude-opus-5-5", "usage": {
            "input_tokens": 2, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": 50000, "output_tokens": out_tok}}}
    f = TMPD / "killed.log"
    f.write_text("\n".join(json.dumps(x) for x in (asst("m0", 4), result(cost=0.2, turns=1), asst("m1", 300),
                                                     asst("m1", 300), asst("m2", 500))) + "\n")
    o = workers.worker_outcome(f)
    assert o["cost_src"] == "est" and o["turns"] == 3 and o["out_tok"] == 804, o
    R = workers.EST_RATES
    want = (R["write"] * 3 * 1002 + R["read"] * 150000 + R["out"] * 804) / 1e6
    assert abs(o["cost_usd"] - round(want, 4)) < 1e-4, (o["cost_usd"], want)
    workers.record_metrics(f, "single", {"HCTF_STAGE": "single", "HCTF_BASE": "killed-day-99"}, workers.STOPPED_RC, 9.0)
    r = workers.read_metrics()[-1]
    assert r["outcome"] == "stopped" and r["cost_src"] == "est", r
    assert "killed-day-99" not in workers.metrics_report().split("non-ok worker exits:")[-1]
    # a whole-session result stays exact
    f.write_text("\n".join(json.dumps(x) for x in (asst("m0", 4), result(cost=0.2, turns=1))) + "\n")
    assert workers.worker_outcome(f)["cost_src"] == "exact" and workers.worker_outcome(f)["cost_usd"] == 0.2
    print("ok  killed-at-CORRECT worker: tokens summed from the stream, cost estimated, outcome `stopped`")
finally:
    workers.CLAUDE_BIN, workers.WORKER_SANDBOX, workers.METRICS, workers.API_BACKOFF, workers.API_MIN_LEFT = saved
print("ALL PASS")
