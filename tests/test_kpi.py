#!/usr/bin/env python3
"""hctf kpi on a synthetic Day-20-shaped log: 5 regular lanes + 1 web chain (answer-first single, live-answer Mastery).
D20's real row read "- (20/21) | 14/15 at 14:52" while the five lanes were 15/15 at T+1:29 and the GM had 21/21."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import kpi  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


LANES = ["warmups-day-20", "metadata-forensics-day-20-x", "script-analysis-day-20-x",
         "binary-reverse-engineering-day-20-x", "mobile-android-day-20-x"]
WEB = "web-exploitation-day-04-lfi"
lines = ["20:55:10 [wait] polling the GM for day 20",
         "21:00:02 [wait] day 20 announced by the GM (status probe, +2.8s from the drop) -- fetching its list",
         "21:00:09 [wait] day 20 released (18 challenge modes) -- launching",
         "21:00:09 [run] 6 chains (18 challenge modes)"]
for i, b in enumerate(LANES):
    lines += [f"21:00:{20 + i:02d} [{b}] single CORRECT + solver verified -> ending the worker, timed modes start now",
              f"21:00:{40 + i:02d} [{b}/time_trial] timed: {{\"result\": \"correct\"}}",
              f"21:00:{40 + i:02d} [{b}/time_trial] result: correct",
              f"21:01:{i:02d} [{b}/mastery] timed: {{\"result\": \"correct\"}}",
              f"21:01:{i:02d} [{b}/mastery] result: correct"]
lines += [f"21:01:38 [{LANES[3]}/mastery] generalize worker -> local",      # a post-run speed pass, after the chain end
          f"21:04:31 [{LANES[3]}/mastery] generalize worker exit 0 (x.log)",
          f"21:01:02 [{WEB}] single complete -> ending the answer-first worker",
          f"21:01:59 [{WEB}/time_trial] timed: {{\"result\": \"correct\"}}",
          f"21:01:59 [{WEB}/time_trial] result: correct",
          f"21:07:36 [{WEB}/mastery] timed: {{\"result\": \"solver_incomplete\"}}",
          f"21:08:08 [{WEB}/mastery] passed by the live-answer worker (attempt b05c2803)"]
lines.sort(key=lambda s: s[:8])

with tempfile.TemporaryDirectory() as d:
    log = Path(d) / "day20.log"
    log.write_text("\n".join(lines) + "\n")
    k = kpi.compute(20, log=log)
    check("regular lanes: 15/15 at the last regular pass (web not folded in)",
          k["modes"] == 15 and k["modes_solved"] == 15 and k["t_all"] == 21 * 3600 + 64 - (21 * 3600 + 9), k)
    check("web: 3/3 counted -- answer-first single + live-answer Mastery", k["web_solved"] == 3 and k["web_modes"] == 3
          and k["t_web"] == 8 * 60 + 8 - 9, k)
    check("release lag = the status-probe detection (+2.8 s), launch lag kept apart",
          k["release_lag"] == 2.8 and k["launch_lag"] == 9, k)
    check("a generalize after the chain finished is not a live-run generalize", k["generalizes"] == 0, k)
    r = kpi.row(k)
    check("row: 15/15 column + web column", "| 0:55 (15/15) |" in r and r.rstrip().endswith("| 7:59 (3/3) |"), r)
    md = Path(d) / "KPI.md"
    md.write_text("# t\n\n| day | date | 15/15 | 14/15 | release lag | race wins | timed first try | generalizes (n / s / "
                  "crit s) | live / in-attempt / untimed | !!! | live $ | post-run $ |\n"
                  "|---|---|---|---|---|---|---|---|---|---|---|---|\n| D19 | x |\n| D20 | old |\n")
    kpi.record(k, md)
    t = md.read_text()
    check("record: pre-web header upgraded once, old D20 row replaced, D19 kept",
          t.count("web (all)") == 1 and sum(ln.startswith("|---") for ln in t.splitlines()) == 1
          and "| D20 | old |" not in t and "| D19 | x |" in t and t.splitlines()[3].count("|---") == 13, t)

if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall kpi checks passed")
