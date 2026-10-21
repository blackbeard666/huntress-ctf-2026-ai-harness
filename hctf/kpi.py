"""Per-day KPI row -- the numbers reference/PLAN_SUB2MIN.md judges a day (and every post-run change) by:
T+ to 14/15 and 15/15 from the release (the five regular lanes; web from D19 is its own column: one live target per
team + GM target provisioning make it a different clock), release detection lag, reuse-race wins, timed modes passed first try,
generalizes (count / seconds / on the critical path), live-answer and in-attempt passes, untimed fallbacks, `!!!`
alerts, worker cost (live vs post-run).

    hctf kpi --day 16            one day
    hctf kpi --all               every day with a .run/dayNN.log
    hctf kpi --day 16 --record   append the row to reference/KPI.md
    hctf kpi --day 20 --log <replay run.log> --label replay-a --record   a replay's row (`D20 replay-a`) beside the day's
"""
import datetime
import json
import re
from pathlib import Path

from . import paths, timeline, workers
from .paths import ROOT

CTF_DAY1 = datetime.date(2026, 10, 1)   # day N is released 21:00 Asia/Manila on Oct N (D14 = 2026-10-14)
NON_CHAIN = {"wait", "hof", "speed-harden", "toolchain", "coord", "ratchet-log", "prebuild", "train", "postrun",
             "tool-gaps", "homebase", "warm", "run", "attack-coverage", "effort", "capture"}
POST_STAGES = {"ratchet", "ratchet_log", "prebuild", "speed-harden", "train", "coverage"}


def _secs(h, m, s):
    return int(h) * 3600 + int(m) * 60 + int(s)


def _fmt(s):
    if s is None:
        return "-"
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def compute(day=None, log=None):
    path = Path(log) if log else ROOT / ".run" / f"day{int(day):02d}.log"
    lines = path.read_text(errors="replace").splitlines()
    t0, chains = timeline.parse(lines)
    chains = {b: c for b, c in chains.items() if b not in NON_CHAIN}
    rel = run0 = announced = None
    n_modes = None
    race, live, inatt, untimed_fb, duel, gen_rej = set(), set(), set(), set(), set(), 0
    bang = 0
    last, wrap = None, 0
    for raw in lines:
        m = re.match(r"^(\d\d):(\d\d):(\d\d) (.*)$", raw)
        if not m:
            continue
        t = _secs(*m.groups()[:3]) + wrap
        if last is not None and t < last - 3600:
            wrap += 86400
            t += 86400
        last = t
        msg = m.group(4)
        if msg.startswith("[wait] day") and " released (" in msg:
            rel = t
        am = re.search(r"announced by the GM \(status probe, ([+-][\d.]+)s from the drop\)", msg)
        if am:
            announced = float(am.group(1))   # sub-second detection lag; `released` is that + the list fetch
        cm = re.match(r"(\d+) chains \((\d+) challenge modes\)", msg)
        if cm:
            run0, n_modes = t, int(cm.group(2))
        if "!!!" in raw:
            bang += 1
        tm = timeline.LINE.match(raw)
        if not tm:
            continue
        tag, body = tm.group(4), tm.group(5)
        base, mode = timeline._split(tag)
        if "reuse race WON" in body:
            race.add(base)
        if body.startswith("passed by the live-answer worker"):
            live.add((base, mode))
        if body.startswith("timed: {") and '"resubmit_fixed"' in body and '"result": "correct"' in body:
            inatt.add((base, mode))
        if "passed on an UNTIMED attempt" in body:
            untimed_fb.add((base, mode))
        if "duel reached a verified solver first" in body or "duel generalize green first" in body:
            duel.add(base)
        if body.startswith("generalize REJECTED"):
            gen_rej += 1
    start = rel if rel is not None else (run0 if run0 is not None else t0)
    from .prebuild import DROP_LOCAL
    hh, mm = (int(x) for x in DROP_LOCAL.split(":"))
    drop_s = hh * 3600 + mm * 60
    launch_lag = (rel - drop_s) if rel is not None and 0 <= rel - drop_s <= 1800 else None
    lag = announced if announced is not None else launch_lag
    # web (D19+) is reported apart: one live target per team, chains serialized, ~5 min GM provisioning per timed
    # target -- folded into "15/15" it read D20 (5 lanes done T+1:29) as "15/15 never, 14/15 at 14:52"
    web = {b for b in chains if _is_web(b)}
    n_web = 3 * len(web)
    reg = {b: c for b, c in chains.items() if b not in web}
    done = sorted(c["done"][m] - start for c in reg.values() for m in c["done"])
    n = (n_modes - n_web) if n_modes else 15
    t_all = done[n - 1] if len(done) >= n else None
    t_but1 = done[n - 2] if len(done) >= n - 1 else None
    wdone = sorted(chains[b]["done"][m] - start for b in web for m in chains[b]["done"])
    t_web = wdone[-1] if web and len(wdone) == n_web else None
    ends = {b: max(c["done"].values()) for b, c in reg.items() if len(c["done"]) == len(timeline.MODES)}
    crit = max(ends, key=ends.get) if ends else None
    # live-run generalizes only: the post-run speed-harden generalizes log under the same chain tag (D20: binary's 173 s
    # speed pass at T+24 showed as "on the critical path")
    last = {b: max(c["done"].values()) for b, c in chains.items() if len(c["done"]) == len(timeline.MODES)}
    gens = [(b, bb - a) for b, c in chains.items() for (_m, st, a, bb) in c["workers"]
            if st == "generalize" and (b not in last or a <= last[b])]
    crit_gen = sum(s for b, s in gens if b == crit)
    timed_modes = [(b, m) for b, c in chains.items() for m in ("time_trial", "mastery") if m in c["done"]]
    first_try = sum(1 for b, m in timed_modes if chains[b]["attempts"][m] <= 1)
    rows = [r for r in workers.read_metrics() if day and f"challenges/day{int(day):02d}/" in r.get("log", "")]
    live_cost = sum(r["cost_usd"] for r in rows if r.get("stage") not in POST_STAGES)
    post_cost = sum(r["cost_usd"] for r in rows if r.get("stage") in POST_STAGES)
    lanes = {b: b.split("-day-")[0] for b in chains}
    return {
        "day": int(day) if day else None, "date": str(CTF_DAY1 + datetime.timedelta(days=int(day) - 1)) if day else "",
        "modes_solved": len(done), "modes": n, "t_all": t_all, "t_but1": t_but1, "release_lag": lag,
        "launch_lag": launch_lag, "web_solved": len(wdone), "web_modes": n_web, "t_web": t_web,
        "race_wins": sorted(lanes.get(b, b) for b in race), "duel_wins": sorted(lanes.get(b, b) for b in duel),
        "timed_first_try": first_try, "timed_modes": len(timed_modes),
        "generalizes": len(gens), "generalize_s": sum(s for _b, s in gens), "generalize_rejected": gen_rej,
        "critical_chain": lanes.get(crit, crit), "critical_generalize_s": crit_gen,
        "live_passes": len(live), "in_attempt_passes": len(inatt), "untimed_fallbacks": len(untimed_fb),
        "alerts": bang, "live_cost": live_cost, "post_cost": post_cost, "log": str(path),
    }


def _is_web(base):
    return paths.canonical_lane(base.split("-day-")[0]) == "web"


def _lag(k):
    s = ("%+.1fs" % k["release_lag"]) if k.get("release_lag") is not None else "-"
    if k.get("launch_lag") is not None and k["launch_lag"] != k.get("release_lag"):
        s += " (launch %+ds)" % k["launch_lag"]
    return s


def _web(k):
    if not k.get("web_modes"):
        return "-"
    return f"{_fmt(k['t_web'])} ({k['web_solved']}/{k['web_modes']})"


def render(k):
    out = [f"KPI day {k['day']}{' ' + k['label'] if k.get('label') else ''} ({k['date']})  --  {k['log']}",
           f"  solved            {k['modes_solved']}/{k['modes']}   {k['modes']}/{k['modes']} at T+{_fmt(k['t_all'])}   "
           f"{k['modes'] - 1}/{k['modes']} at T+{_fmt(k['t_but1'])}   release seen {_lag(k)} after the drop",
           *([f"  web               {k['web_solved']}/{k['web_modes']}   all at T+{_fmt(k['t_web'])} "
              "(live targets: GM provisioning + the chains' own serial modes)"] if k.get("web_modes") else []),
           f"  singles           reuse race won: {', '.join(k['race_wins']) or 'none'}"
           + (f"; duel won: {', '.join(k['duel_wins'])}" if k['duel_wins'] else ""),
           f"  timed             first try {k['timed_first_try']}/{k['timed_modes']}; live-answer passes {k['live_passes']}; "
           f"in-attempt fixes {k['in_attempt_passes']}; untimed fallbacks {k['untimed_fallbacks']}",
           f"  generalizes       {k['generalizes']} ({k['generalize_s']} s total, {k['generalize_rejected']} rejected); "
           f"on the critical path ({k['critical_chain']}): {k['critical_generalize_s']} s",
           f"  alerts (!!!)      {k['alerts']}",
           f"  worker cost       live ${k['live_cost']:.2f}, post-run ${k['post_cost']:.2f}"]
    return "\n".join(out)


HEADER = ("| day | date | 15/15 | 14/15 | release lag | race wins | timed first try | generalizes (n / s / crit s) | "
          "live / in-attempt / untimed | !!! | live $ | post-run $ | web (all) |\n"
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")


def _key(k):
    """The row's first cell: `D20`, or `D20 <label>` for a replay / rehearsal of that day."""
    return f"D{k['day']:02d}" + (f" {k['label']}" if k.get("label") else "")


def row(k):
    return (f"| {_key(k)} | {k['date']} | {_fmt(k['t_all'])} ({k['modes_solved']}/{k['modes']}) | {_fmt(k['t_but1'])} | "
            f"{_lag(k)} | "
            f"{len(k['race_wins'])}/5 ({', '.join(x[:6] for x in k['race_wins'])}) | {k['timed_first_try']}/{k['timed_modes']} | "
            f"{k['generalizes']} / {k['generalize_s']} / {k['critical_generalize_s']} ({k['critical_chain'] or '-'}) | "
            f"{k['live_passes']} / {k['in_attempt_passes']} / {k['untimed_fallbacks']} | {k['alerts']} | "
            f"{k['live_cost']:.2f} | {k['post_cost']:.2f} | {_web(k)} |\n")


def record(k, path=None):
    path = Path(path) if path else ROOT / "reference" / "KPI.md"
    text = path.read_text() if path.exists() else ("# Daily KPI rows (hctf kpi --record)\n\nTargets (PLAN_SUB2MIN.md): "
                                                    "15/15 <= 2:00 on 4 of 5 days, 14/15 <= 1:00 median, 0 manual steps.\n\n"
                                                    + HEADER)
    lines = [ln for ln in text.splitlines(keepends=True) if not ln.startswith(f"| {_key(k)} |")]
    # upgrade a pre-web header in place (older rows just leave the new last cell empty)
    old_head = [i for i, ln in enumerate(lines) if ln.startswith("| day | date |") and "web (all)" not in ln]
    if old_head:
        i = old_head[0]
        lines[i:i + 2] = HEADER.splitlines(keepends=True)
    lines.append(row(k))
    path.write_text("".join(lines))
    return path


def days_with_logs():
    out = []
    for p in sorted((ROOT / ".run").glob("day[0-9][0-9].log")):
        m = re.match(r"day(\d\d)\.log", p.name)
        if m:
            out.append(int(m.group(1)))
    return out
