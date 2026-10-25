"""D24 plan #15 (measurement: web counted as a lane), offline on synthetic logs -- no GM, no workers.
- timeline: a chain = any `-day-NN` tag ([res]/[hof]/[postrun] are not chains); lane_label() = `web:<slug>` per web chain;
  slot waits (`[slot] <cid>: waited Ns for a local slot` + the web target slot line) per chain
- kpi v2: T0 = the drop when armed before it, else the launch; the board counts every mode incl. web; per lane
  start/single/TT/Mastery; per segment GM (relay vs local) / LLM / harness; the timed runner's GM phases count as GM
- kpi.record_v2 upserts the Board v2 / Lanes v2 tables and leaves the legacy table (and kpi.row) as they were
- feed + effort_report key by lane_label (two web chains stay distinct)

Run:  source bin/env.sh && python3 tests/test_d24_measure.py      (exit 0 = all pass)
"""
import contextlib
import datetime
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import effort_report, feed, kpi, timeline  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    """pairs: {(obj, attr): value} -- set, yield, restore."""
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


TMP = Path(tempfile.mkdtemp(prefix="d24m-", dir=str(ROOT / ".run")))
WA, WB = "web-exploitation-day-14-the-api-has-opinions", "web-exploitation-day-15-fetch-quest"
W, S = "warmups-day-25", "script-analysis-day-25-x"

# ---------------------------------------------------------------- timeline: chains, lane_label, slot waits
check("lane_label: web chain -> web:<slug>", timeline.lane_label(WA) == "web:the-api-has-opinions"
      and timeline.lane_label(WB) == "web:fetch-quest", (timeline.lane_label(WA), timeline.lane_label(WB)))
check("lane_label: regular lanes keep the GM lane", timeline.lane_label(S) == "script-analysis"
      and timeline.lane_label(W) == "warmups")
check("is_chain: only -day-NN tags", timeline.is_chain(W) and timeline.is_chain(WA) and not timeline.is_chain("res")
      and not timeline.is_chain("hof") and not timeline.is_chain("postrun"))

LOG = [
    "20:40:00 [wait] polling the GM for day 25 (every 0.3s + call time)",
    "21:00:02 [wait] day 25 announced by the GM (status probe, +2.0s from the drop) -- fetching its list",
    "21:00:05 [wait] day 25 released (12 challenge modes) -- launching",
    "21:00:05 4 chains (12 challenge modes), slots local=5 homebase=0, credits=99.0",
    "21:00:05 [res] T+0:00 mem_avail 6836MB",
    f"21:00:06 [{W}] single worker warming up beside start/download/triage",
    f"21:00:06 [{S}] single worker warming up beside start/download/triage",
    f"21:00:07 [{WA}] single worker warming up beside start/download/triage",
    f"21:00:07 [{WB}] single worker warming up beside start/download/triage",
    f"21:00:10 [slot] {S}: waited 3.5s for a local slot",
    f"21:00:10 [{S}] single worker -> local (warm) (timeout 1500s)",
    f"21:00:30 [{S}] single CORRECT + solver verified -> ending the worker, timed modes start now",
    f"21:00:30 [{S}] single worker exit -15 (w.log)",
    f"21:00:20 [{W}] reuse race WON -- single CORRECT",
    f"21:00:30 [{W}/time_trial] timed: {{\"result\": \"correct\", \"elapsed\": 3, \"routed\": \"local (Homebase unavailable)\", "
    "\"phases\": {\"start\": 0.5, \"download\": 0.5, \"solve\": 1, \"submit\": 1}}",
    f"21:00:40 [{W}/mastery] timed: {{\"result\": \"correct\", \"elapsed\": 4, \"routed\": \"homebase\", "
    "\"phases\": {\"start\": 1, \"download\": 0, \"solve\": 1, \"submit\": 2}}",
    f"21:00:45 [{S}/time_trial] timed: {{\"result\": \"correct\"}}",
    f"21:00:55 [{S}/mastery] timed: {{\"result\": \"correct\"}}",
    f"21:01:00 [{WA}] single complete -> ending the answer-first worker",
    f"21:01:10 [{WB}] single CORRECT + solver verified",
    f"21:01:20 [{WA}/time_trial] timed: {{\"result\": \"correct\"}}",
    f"21:01:25 [{WB}/time_trial] web target slot acquired after 12s",
    f"21:01:30 [{WB}/time_trial] timed: {{\"result\": \"correct\"}}",
    f"21:01:40 [{WA}/mastery] passed by the live-answer worker (attempt x)",
    f"21:01:50 [{WB}/mastery] timed: {{\"result\": \"correct\"}}",
    "21:01:51 [hof] race skipped",
    "21:01:52 all chains finished",
    "21:05:00 [postrun] ratchet start",
]
LOG.sort(key=lambda s: s[:8])
first, ch = timeline.parse(LOG)
check("timeline: 4 chains ([res]/[hof]/[postrun] not counted)", sorted(ch) == sorted([W, S, WA, WB]), sorted(ch))
check("timeline: slot waits per chain (Pools line + web target slot line)",
      ch[S]["slot_wait"] == 3.5 and ch[WB]["slot_wait"] == 12.0 and ch[W]["slot_wait"] == 0, {b: c["slot_wait"] for b, c in ch.items()})
check("timeline: chain launch = its first line", ch[S]["first"] == 21 * 3600 + 6)
logp = TMP / "day25.log"
logp.write_text("\n".join(LOG) + "\n")
rep = timeline.report(log=logp)
check("timeline report: 4/4 chains complete", "4/4 chains complete" in rep, rep[-300:])

# GM calls in the modes' log.jsonl (a fake harness copy under TMP), mtime of the day log = its last line
day = datetime.date(2026, 10, 25)
midnight = datetime.datetime.combine(day, datetime.time()).timestamp()
os.utime(logp, (midnight + 21 * 3600 + 5 * 60, midnight + 21 * 3600 + 5 * 60))
idx = {W: {"dir": "day25/warmups-w"}, S: {"dir": "day25/scripting-x"}, WA: {"dir": "day25/web-a"}, WB: {"dir": "day25/web-b"}}
(TMP / "challenges").mkdir()
(TMP / "challenges" / "index.json").write_text(json.dumps(idx))


def gm(d, mode, at, el, transport="inproc", op="start"):
    p = TMP / "challenges" / d / mode / "log.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps({"t": midnight + at, "op": op, "elapsed": el, "transport": transport}) + "\n")


H = 21 * 3600
gm("day25/scripting-x", "single_solve", H + 9, 2.0)                # before the worker: GM time on the single
gm("day25/scripting-x", "single_solve", H + 20, 1.0, op="submit")  # inside the worker: counted as LLM time
gm("day25/scripting-x", "time_trial", H + 40, 4.0, transport="relay-1")
gm("day25/scripting-x", "mastery", midnight - 3600, 9.0)            # a call from another run: outside the window
gm("day25/web-a", "single_solve", H + 50, 5.0)

k = kpi.compute(25, log=logp, root=TMP)
v = k["v2"]
check("v2: armed before the drop -> T0 = the drop", v.get("t0") == "drop" and v.get("t0_hms") == "21:00:00", v)
check("v2: board counts every mode incl. web (12/12) at the last pass", v["board_modes"] == 12 and v["board_solved"] == 12
      and v["t_board"] == 110 and v["t_board_but1"] == 100, (v["board_modes"], v["board_solved"], v["t_board"]))
check("v2: two web chains are two lanes", {"web:the-api-has-opinions", "web:fetch-quest"} <= set(v["lanes"]), list(v["lanes"]))
ls = v["lanes"]["script-analysis"]
check("v2 lane: start / single / TT / Mastery from T0", (ls["start"], ls["single"], ls["TT"], ls["Mastery"]) == (6, 30, 45, 55), ls)
sg = ls["segs"]["single"]
check("v2 segment: GM outside the worker / LLM worker / harness rest (single 24 s = 2 / 20 / 2)",
      sg["wall"] == 24 and sg["gm"] == 2.0 and sg["llm"] == 20 and sg["harness"] == 2.0, sg)
check("v2 segment: a `relay*` transport is relay GM time, inproc is local",
      ls["segs"]["TT"]["gm_relay"] == 4.0 and ls["segs"]["TT"]["gm_local"] == 0 and sg["gm_local"] == 3.0, ls["segs"])
check("v2 segment: a GM call of another run (outside the log window) is ignored",
      ls["segs"]["Mastery"]["gm"] == 0, ls["segs"]["Mastery"])
lw = v["lanes"]["warmups"]["segs"]
check("v2 segment: the timed runner's GM phases count (TT local 2 s, Mastery via Homebase 3 s = relay)",
      lw["TT"]["gm"] == 2.0 and lw["TT"]["gm_local"] == 2.0 and lw["Mastery"]["gm_relay"] == 3.0, lw)
check("v2: slot wait carried per lane", v["lanes"]["script-analysis"]["slot_wait"] == 3.5
      and v["lanes"]["web:fetch-quest"]["slot_wait"] == 12.0)
check("v2: critical lane = the last to finish (a web chain)", v["critical"] == "web:fetch-quest", v["critical"])
check("render_v2 names the SLO and both web lanes", "N/N by T+2:00" in kpi.render_v2(k)
      and "web:fetch-quest" in kpi.render_v2(k) and "web:the-api-has-opinions" in kpi.render_v2(k))

# legacy row unchanged: 5-lane fields from the release line (21:00:05)
check("legacy: regular 6/6 from the release line, web apart", k["t_all"] == 50 and k["modes_solved"] == 6
      and k["t_web"] == 105 and k["web_modes"] == 6, (k["t_all"], k["modes_solved"], k["t_web"]))

# not armed: T0 = the launch (the first line), not the drop
late = [ln.replace("21:0", "21:1", 1) for ln in LOG if "[wait] polling" not in ln and "announced" not in ln]
lp = TMP / "late.log"
lp.write_text("\n".join(late) + "\n")
v2 = kpi.compute(25, log=lp, root=TMP)["v2"]
check("v2: a run launched after the drop without arming -> T0 = the launch", v2["t0"] == "launch"
      and v2["t0_hms"] == "21:10:05", (v2["t0"], v2["t0_hms"]))

# ---------------------------------------------------------------- record: v2 tables upserted, legacy untouched
md = TMP / "KPI.md"
md.write_text("# Daily KPI rows\n\n" + kpi.HEADER + "| D24 | x |\n")
kpi.record(k, md)
legacy_before = md.read_text()
kpi.record_v2(k, md)
kpi.record_v2(k, md)   # idempotent
t = md.read_text()
check("record_v2: the legacy table is left exactly as record() wrote it", t.startswith(legacy_before.rstrip("\n")), t[:400])
check("record_v2: one Board v2 row + one Lanes v2 row per lane, idempotent",
      t.count("| D25 | 2026-10-25 | drop 21:00:00 |") == 1 and t.count(kpi.BOARD_TITLE) == 1
      and sum(ln.startswith("| D25 | web:") for ln in t.splitlines()) == 2
      and sum(ln.startswith("| D25 |") for ln in t.splitlines()) == 1 + 1 + 4, t)
kpi.record(k, md)   # a later legacy record lands in the legacy table, not under the v2 tables
t2 = md.read_text().splitlines()
check("record (legacy) after v2 exists: the legacy row is replaced, the v2 tables are kept",
      sum(ln.startswith("| D25 | 2026-10-25 | 0:50") for ln in t2) == 1 and kpi.BOARD_TITLE in t2
      and next(i for i, ln in enumerate(t2) if ln.startswith("| D25 | 2026-10-25 | 0:50")) < t2.index(kpi.BOARD_TITLE)
      and "| D24 | x |" in t2, t2)

# ---------------------------------------------------------------- feed + effort report keyed by lane_label
check("feed: web chains distinct, regular lanes as before", feed.lane_of(WA) != feed.lane_of(WB)
      and feed.lane_of(WB) == "web:fetch-quest" and feed.lane_of(S) == "script" and feed.lane_of(W) == "warmups")
check("effort_report: lane key = lane_label", effort_report._lane(WA) == "web:the-api-has-opinions"
      and effort_report._lane(S) == "script-analysis")

shutil.rmtree(TMP, ignore_errors=True)
if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D24 measurement checks passed")
