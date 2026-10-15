#!/usr/bin/env python3
"""Offline self-test for hctf/feed.py (the live milestone feed): solved k/N counting, in-attempt passes, blocked /
generalize / duel / hint / error lines, heartbeat, summary, and that `follow` streams + exits on "all chains finished".

Run:  source bin/env.sh && python3 tests/test_feed.py      (exit 0 = all pass)
"""
import io
import sys
import tempfile
import threading
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hctf import feed  # noqa: E402

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


S = "script-analysis-day-13-archive-delivery-chain"
M = "metadata-forensics-day-13-product-placement"
LOG = f"""19:00:00 [homebase] pre-warming
19:00:05 2 chains (6 challenge modes), slots local=5 homebase=0, credits=99.0
19:00:08 [{S}] reuse race WON: single CORRECT at +3.0s from prior solver output (seed x)
19:00:09 [{M}] single worker -> local (warm) (timeout 1500s)
19:00:10 [{M}] duel single worker -> local (effort medium) on .run/duel-day13/x/solver
19:00:30 [{M}] duel reached a verified solver first -> ending the chain's worker
19:00:30 [{M}] after worker: stopped at CORRECT with a verified solver
19:00:40 [{S}/time_trial] timed: {{"result": "correct", "elapsed": 30.1, "resubmit_fixed": "completed_by_localize"}}
19:00:40 [{S}/time_trial] result: correct
19:00:45 [{M}/time_trial] result: blocked
19:00:46 [{M}/time_trial] generalize worker -> local (timeout 720s)
19:00:46 [{M}/time_trial] duel generalize worker -> local (effort medium) on y
19:01:10 [{M}/time_trial] coordinator hint -> generalize worker: Stop hunting; fit one rule now.
19:01:28 [{M}] generalize accepted: now also passes ['variant-x']
19:01:30 [{M}/time_trial] result: correct
19:01:40 [{S}/mastery] result: error:exec
19:01:41 !!! [{S}] something loud
19:02:00 [{S}/mastery] result: correct
19:02:05 [{M}/mastery] result: correct
19:02:05 all chains finished
""".splitlines(keepends=True)

out = feed.parse_lines(LOG)
text = "\n".join(out)
print("\n".join("    " + o for o in out))
check("run start counts from the chains line", out[0].startswith("T+0:00 ▶ run started: 2 chains, 6 modes"))
check("6 solved events with k/N", sum("✅" in o for o in out) == 6 and "[6/6]" in text)
check("reuse race + duel single", "script single solved (reuse race) [1/6]" in text and "metadata duel won the single" in text)
check("in-attempt pass flagged", "script TT solved (in-attempt fix)" in text)
check("blocked -> generalize -> accepted with duration",
      "metadata TT blocked" in text and "metadata TT generalize started" in text
      and "metadata generalize accepted (42s)" in text)
check("hint, error and !!! surfaced", "💬 metadata TT hint: Stop hunting" in text and "script Mastery error:exec" in text
      and "something loud" in text)
check("summary", out[-1].endswith("all chains finished: 6/6 solved"))

f = feed.Feed()
for ln in LOG[:12]:
    f.process(ln)
hb = f.heartbeat()
check("heartbeat shows solved count + current work", "3/6 solved" in hb and "metadata TT generalize" in hb)

# follow(): streams appended lines and exits at "all chains finished"
with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "day99.log"
    p.write_text("".join(LOG[:3]))
    buf = io.StringIO()

    def writer():
        time.sleep(0.4)
        with open(p, "a") as fh:
            for ln in LOG[3:]:
                fh.write(ln)
                fh.flush()
                time.sleep(0.01)
    threading.Thread(target=writer, daemon=True).start()
    t0 = time.time()
    with redirect_stdout(buf):
        rc = feed.follow(p, from_start=False, heartbeat=999, poll=0.05)
    got = buf.getvalue()
    check("follow streams new milestones and exits at the end",
          rc == 0 and "(following day99.log)" in got and "[6/6]" in got and "🏁" in got and time.time() - t0 < 10)

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
