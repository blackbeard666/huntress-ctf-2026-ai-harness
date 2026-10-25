#!/usr/bin/env python3
"""Day 25 web post-mortem (Track D) offline checks.

D1: feed / timeline / kpi / effort_report count a web Time Trial passed by the live answer during the codify wait
    (D25: shell-company + resolver-revolt TTs uncounted -> feed 22/24, kpi web 7/9 while the GM had 24/24).

Run:  source bin/env.sh && python3 tests/test_d25_web.py      (exit 0 = all pass)
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hctf import effort_report, feed, kpi, timeline  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {str(detail)[:400]}"))
    if not cond:
        failures.append(name)


# ---- D1: the D25 web lines, verbatim from .run/day25.log (5 regular lanes reduced to one solved line per mode) --------
SH, RE, RV = ("web-exploitation-day-16-shell-company", "web-exploitation-day-17-reset-expectations",
              "web-exploitation-day-18-resolver-revolt")
REG = ["mobile-android-day-25-integrity-signals", "metadata-forensics-day-25-hive-mind",
       "script-analysis-day-25-phoenix-stage-chain", "warmups-day-25",
       "binary-reverse-engineering-day-25-synthetic-vulnerability-root-cause"]
D25 = ["21:00:11 [wait] day 25 released (24 challenge modes) -- launching",
       "21:00:11 8 chains (24 challenge modes), slots local=5 homebase=0, credits=99.0"]
for i, b in enumerate(REG):
    D25 += [f"21:00:{20 + i:02d} [{b}] single CORRECT + solver verified -> ending the worker, timed modes start now",
            f"21:00:{40 + i:02d} [{b}/time_trial] result: correct",
            f"21:01:{30 + i:02d} [{b}/mastery] result: correct"]
D25 += [
    f"21:01:06 [{RV}] single complete -> ending the answer-first worker",
    f"21:01:09 [{SH}] single complete -> ending the answer-first worker",
    f"21:01:10 [{RE}] single CORRECT + solver verified -> ending the worker, timed modes start now",
    f"21:01:51 [{SH}/time_trial] live-answer: mode CORRECT -> ending the generalize",
    f"21:01:51 [{SH}/time_trial] passed by the live answer after 19s of the codify wait (no generalize)",
    f"21:02:14 [{RV}/time_trial] passed by the live answer after 36s of the codify wait (no generalize)",
    f"21:02:20 [{RE}/time_trial] result: correct",
    f'21:02:44 [{RV}/mastery] timed: {{"result": "correct", "elapsed": 13.96, "window": null}}',
    f"21:02:44 [{RV}/mastery] result: correct",
    f"21:02:51 [{RE}/mastery] result: correct",
    f"21:03:56 [{SH}/mastery] passed by the live answer: not waiting for the harvest",
    f"21:03:56 [{SH}/mastery] passed by the live-answer worker (attempt ddfc9d13)",
    "21:06:02 [hof] racing passed timed modes for the Hall of Fame (up to 3 each, >= 8 left, reserve 5)",
]
D25.sort(key=lambda s: s[:8])


with tempfile.TemporaryDirectory() as d:
    log = Path(d) / "day25.log"
    log.write_text("\n".join(D25) + "\n")
    k = kpi.compute(25, log=log, root=d)
    check("D1 kpi: regular 15/15", k["modes_solved"] == 15 and k["modes"] == 15, k)
    check("D1 kpi: web 9/9 (codify-wait live passes counted)", k["web_solved"] == 9 and k["web_modes"] == 9, k)
    check("D1 kpi: the two codify-wait passes are live-answer passes", k["live_passes"] >= 3, k)
    _t0, chains = timeline.parse(D25)
    check("D1 timeline: shell-company TT done at the codify-wait pass",
          chains[SH]["done"].get("time_trial") == 21 * 3600 + 60 + 51, chains.get(SH))
    check("D1 timeline: 8/8 chains complete", sum(1 for c in chains.values() if len(c["done"]) == 3) == 8)
    eff_root = Path(d) / "copy"
    (eff_root / ".run").mkdir(parents=True)
    (eff_root / ".run" / "day25.log").write_text("\n".join(D25) + "\n")
    try:
        s = effort_report.solves(eff_root, 25)
        web_tt = {lane for lane, m in s if m == "time_trial" and lane.startswith("web")}
        check("D1 effort_report: all three web TTs found (two codify-wait passes)", len(web_tt) == 3, s)
    except Exception as e:  # noqa: BLE001
        check("D1 effort_report: parses the log", False, e)

f = feed.Feed()
msgs = []
for ln in D25:
    msgs += f.process(ln)
check("D1 feed: 24/24 solved", len(f.solved) == 24, sorted(f.solved))
check("D1 feed: the codify-wait TT shows as a live-answer solve",
      any("web TT solved (live-answer)" in m or ("TT solved (live-answer)" in m and "web" in m) for m in msgs),
      [m for m in msgs if "TT" in m])
check("D1 orchestrate-style line `result: correct (live answer, codify wait)` is a timed pass",
      timeline.timed_passed("result: correct (live answer, codify wait)")
      and timeline.timed_passed("passed during the online resolution / live answer"))

# the real log, when this copy has it (main's .run/day25.log)
real = Path.home() / "huntress-2026" / ".run" / "day25.log"
if real.exists():
    k = kpi.compute(25, log=real, root=str(real.parents[1]))
    check("D1 real .run/day25.log: regular 15/15 + web 9/9", k["modes_solved"] == 15 and k["web_solved"] == 9,
          {x: k.get(x) for x in ("modes_solved", "web_solved", "web_modes")})

if __name__ == "__main__":
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
    sys.exit(1 if failures else 0)
