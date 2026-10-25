"""Per-day KPI row -- the numbers reference/PLAN_SUB2MIN.md judges a day (and every post-run change) by:
T+ to 14/15 and 15/15 from the release (the five regular lanes; web from D19 is its own column: one live target per
team + GM target provisioning make it a different clock), release detection lag, reuse-race wins, timed modes passed first try,
generalizes (count / seconds / on the critical path), live-answer and in-attempt passes, untimed fallbacks, `!!!`
alerts, worker cost (live vs post-run).

    hctf kpi --day 16            one day
    hctf kpi --all               every day with a .run/dayNN.log
    hctf kpi --day 16 --record   append the row to reference/KPI.md
    hctf kpi --day 20 --log <replay run.log> --label replay-a --record   a replay's row (`D20 replay-a`) beside the day's
    hctf kpi --day 24 --legacy   only the pre-D25 row above (5 regular lanes, T0 = the release line)

v2 (D24 plan #15; `--record` writes the legacy row AND the two v2 tables, `--legacy` only the legacy row): the WHOLE
board (every mode, web included -- the user's SLO: "board N/N incl. web by T+2:00 from the drop") from T0 = the drop
(21:00, when the run was armed with --wait before it) or the launch (a late / unarmed start: D24 launched 16 min late);
per lane (`web:<slug>` per web chain): start / single / TT / Mastery T+, and each segment's wall split into GM (relay vs
local, from the modes' log.jsonl `elapsed` + `transport`) / LLM (worker wall) / harness (the rest).
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


def compute(day=None, log=None, root=None):
    """The day's KPI dict (legacy keys + `v2`). `root`: the harness copy whose challenges/ hold the modes' GM logs
    (default this one; the D20-D24 backfill read main's from a worktree)."""
    root = Path(root) if root else ROOT
    path = Path(log) if log else root / ".run" / f"day{int(day):02d}.log"
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
    rows = [r for r in _metrics(root) if day and f"challenges/day{int(day):02d}/" in r.get("log", "")]
    live_cost = sum(r["cost_usd"] for r in rows if r.get("stage") not in POST_STAGES)
    post_cost = sum(r["cost_usd"] for r in rows if r.get("stage") in POST_STAGES)
    lanes = {b: timeline.lane_label(b) for b in chains}
    k = {
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
    k["_start"] = start
    try:
        k["v2"] = _v2(lines, path, t0, chains, n_modes, drop_s, rel, run0, root)
        k["_t0v2"] = k["v2"].get("t0_s", start)
    except Exception as e:  # noqa: BLE001 - the legacy row never depends on the v2 parse
        k["v2"] = {"error": f"{e.__class__.__name__}: {e}"}
    return k


# --- v2: the whole board from the drop, per lane, per segment ---------------------------------------------------------
# GM "relay" time = calls that went through Homebase: the gmroute relay channels (D24 plan #13; any `relay*` transport)
# and the older hb-daemon / hb ssh transports (timed windows routed to Homebase). Everything else (`inproc`) is local.
RELAY_TRANSPORTS = ("relay", "hb")


def _is_relay(transport):
    t = str(transport or "").lower()
    return any(t.startswith(x) or x in t.split("-") for x in RELAY_TRANSPORTS)


def _union(iv, lo, hi):
    """Total length of the union of intervals clipped to [lo, hi]."""
    iv = sorted((max(a, lo), min(b, hi)) for a, b in iv if b > lo and a < hi)
    tot, cur_a, cur_b = 0.0, None, None
    for a, b in iv:
        if cur_b is None or a > cur_b:
            if cur_b is not None:
                tot += cur_b - cur_a
            cur_a, cur_b = a, b
        else:
            cur_b = max(cur_b, b)
    return tot + ((cur_b - cur_a) if cur_b is not None else 0.0)


def _minus(iv, holes):
    """Intervals `iv` with every `holes` interval cut out (GM time spent outside any LLM worker)."""
    out = list(iv)
    for ha, hb in holes:
        nxt = []
        for a, b in out:
            if hb <= a or ha >= b:
                nxt.append((a, b))
                continue
            if a < ha:
                nxt.append((a, ha))
            if hb < b:
                nxt.append((hb, b))
        out = nxt
    return out


def _midnight(path, last_sod):
    """Epoch of the local midnight the log's seconds-of-day count from: the log's last line was written about at its
    mtime (true of a day log, a replay's run.log and a copy that kept its mtime)."""
    try:
        end = path.stat().st_mtime
    except OSError:
        return None
    d = datetime.datetime.fromtimestamp(end - last_sod + 43200).date()   # noon of that day: robust to a few s of drift
    return datetime.datetime.combine(d, datetime.time()).timestamp()


def gm_calls(root, base, midnight, lo, hi):
    """[(mode, start_sod, end_sod, elapsed_s, relay?)] of this chain's GM calls (each mode's log.jsonl) inside the
    run's [lo, hi] seconds-of-day -- a later replay / HoF race writing the same folders falls outside."""
    entry = paths._load_index().get(base) if Path(root) == paths.ROOT else None
    if entry is None:
        try:
            entry = json.loads((Path(root) / "challenges" / "index.json").read_text()).get(base)
        except (OSError, ValueError):
            entry = None
    if not entry or midnight is None:
        return []
    out = []
    for mode in timeline.MODES:
        p = Path(root) / "challenges" / entry["dir"] / mode / "log.jsonl"
        if not p.exists():
            continue
        for ln in p.read_text(errors="replace").splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            t = r.get("t")
            if not isinstance(t, (int, float)) or r.get("op") in ("web-trace",):
                continue
            el = r.get("client_elapsed") or r.get("elapsed") or 0
            try:
                el = float(el)
            except (TypeError, ValueError):
                el = 0.0
            end = t - midnight
            if lo - 5 <= end <= hi + 5:
                out.append((mode, end - el, end, el, _is_relay(r.get("transport"))))
    return out


SEGS = (("single", None, "single_solve"), ("TT", "single_solve", "time_trial"), ("Mastery", "time_trial", "mastery"))


def _v2(lines, path, first, chains, n_modes, drop_s, rel, run0, root):
    """T0, the whole board, per lane times + per segment GM (relay/local) / LLM / harness split."""
    secs = []
    last, wrap = None, 0
    waited_at = None
    timed_gm = {}
    for raw in lines:
        m = re.match(r"^(\d\d):(\d\d):(\d\d) (.*)$", raw)
        if not m:
            continue
        t = _secs(*m.groups()[:3]) + wrap
        if last is not None and t < last - 3600:
            wrap += 86400
            t += 86400
        last = t
        secs.append(t)
        if waited_at is None and m.group(4).startswith("[wait] polling the GM"):
            waited_at = t
        tm = timeline.LINE.match(raw)
        if tm and tm.group(5).startswith("timed: {"):
            # the timed runner's own GM phases (start / download / submit) never reach log.jsonl
            try:
                d = json.loads(tm.group(5)[len("timed: "):])
                ph = d.get("phases") or {}
                gm = sum(float(ph.get(x) or 0) for x in ("start", "download", "submit"))
            except (ValueError, TypeError, AttributeError):
                continue
            routed = str(d.get("routed") or "").lower()
            base, mode = timeline._split(tm.group(4))
            timed_gm.setdefault(base, []).append((mode, t - gm, t, gm, routed.startswith(("homebase", "hb", "relay"))))
    if not secs:
        return {}
    launch = secs[0]
    # armed before the drop (and the release followed it) -> score from the drop; else from the launch
    if waited_at is not None and waited_at <= drop_s and (rel is None or rel >= drop_s - 60):
        t0, t0_how = drop_s, "drop"
    else:
        t0, t0_how = launch, "launch"
    midnight = _midnight(path, secs[-1])
    chain_end = max((max(c["done"].values()) for c in chains.values() if c["done"]), default=t0)
    lanes = {}
    gm_relay = gm_local = 0.0
    for b, c in sorted(chains.items(), key=lambda x: x[1].get("first", 10 ** 9)):
        lab = timeline.lane_label(b)
        start = c.get("first", run0 if run0 is not None else t0)
        calls = gm_calls(root, b, midnight, t0, chain_end + 60) + timed_gm.get(b, [])
        workers_iv = [(a, e) for (_m, _st, a, e) in c["workers"]]
        row = {"base": b, "start": start - t0, "slot_wait": round(c.get("slot_wait", 0.0), 1), "segs": {}}
        prev = start
        for name, frm, mode in SEGS:
            row[name] = (c["done"][mode] - t0) if mode in c["done"] else None
            seg_lo = c["done"].get(frm, prev) if frm else start
            seg_hi = c["done"].get(mode)
            if seg_hi is None or seg_hi < seg_lo:
                continue
            wall = seg_hi - seg_lo
            llm = _union(workers_iv, seg_lo, seg_hi)
            gm_iv = [(a, e) for (_m, a, e, _el, _r) in calls]
            gm = _union(_minus(gm_iv, workers_iv), seg_lo, seg_hi)
            # relay vs local: the calls (any overlap) finishing inside the segment, summed per transport
            rl = sum(el for (_m, a, e, el, r) in calls if r and seg_lo <= e <= seg_hi)
            lc = sum(el for (_m, a, e, el, r) in calls if not r and seg_lo <= e <= seg_hi)
            row["segs"][name] = {"wall": wall, "gm": round(gm, 1), "llm": round(llm, 1),
                                 "harness": round(max(0.0, wall - gm - llm), 1), "gm_relay": round(rl, 1),
                                 "gm_local": round(lc, 1)}
            gm_relay += rl
            gm_local += lc
            prev = seg_hi
        ends = [row[n] for n, _f, _m in SEGS if row[n] is not None]
        row["end"] = max(ends) if len(ends) == len(SEGS) else None
        lanes[lab] = row
    n_board = max(n_modes or 0, 3 * len(chains))
    done = sorted(c["done"][m] - t0 for c in chains.values() for m in c["done"])
    t_board = done[n_board - 1] if n_board and len(done) >= n_board else None
    t_but1 = done[n_board - 2] if n_board > 1 and len(done) >= n_board - 1 else None
    crit = max((lab for lab in lanes if lanes[lab]["end"] is not None), key=lambda lab: lanes[lab]["end"], default=None)
    return {"t0": t0_how, "t0_s": t0, "t0_hms": "%02d:%02d:%02d" % ((t0 // 3600) % 24, (t0 // 60) % 60, t0 % 60),
            "launch": launch - t0, "board_solved": len(done), "board_modes": n_board, "t_board": t_board,
            "t_board_but1": t_but1, "critical": crit, "lanes": lanes, "gm_relay": round(gm_relay, 1),
            "gm_local": round(gm_local, 1)}


def _metrics(root):
    """workers.read_metrics() of `root`'s .run/metrics.tsv (another copy's: the backfill read main's)."""
    if Path(root) == ROOT:
        return workers.read_metrics()
    keep = workers.METRICS
    try:
        workers.METRICS = Path(root) / ".run" / "metrics.tsv"
        return workers.read_metrics()
    finally:
        workers.METRICS = keep


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
    # into the legacy table itself: the Board v2 / Lanes v2 tables follow it in the file (record_v2)
    head = [i for i, ln in enumerate(lines) if ln.startswith("| day | date | 15/15 |")]
    j = head[0] if head else len(lines)
    while j < len(lines) and lines[j].startswith("|"):
        j += 1
    if j == len(lines) and lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    lines.insert(j, row(k))
    path.write_text("".join(lines))
    return path


def days_with_logs():
    out = []
    for p in sorted((ROOT / ".run").glob("day[0-9][0-9].log")):
        m = re.match(r"day(\d\d)\.log", p.name)
        if m:
            out.append(int(m.group(1)))
    return out


# --- v2 rendering + KPI.md tables ---------------------------------------------------------------------------------------
BOARD_TITLE = "## Board v2 (whole board incl. web, T0 = drop; launch when not armed)"
BOARD_HEADER = ("| day | date | T0 | board | board N-1 | regular 15/15 | web (all) | release lag | critical lane | "
                "critical GM / LLM / harness s | GM s relay / local | !!! | live $ |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
LANES_TITLE = "## Lanes v2 (T+ from the board's T0; segment s = GM / LLM / harness)"
LANES_HEADER = ("| day | lane | start | single | TT | Mastery | single seg | TT seg | Mastery seg | GM relay / local s | "
                "slot wait s |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n")


def _seg(s):
    return f"{s['wall']} = {s['gm']:g} / {s['llm']:g} / {s['harness']:g}" if s else "-"


def _crit(v):
    ln = v.get("lanes", {}).get(v.get("critical"))
    if not ln:
        return "-"
    tot = {x: sum(s[x] for s in ln["segs"].values()) for x in ("gm", "llm", "harness")}
    return f"{tot['gm']:g} / {tot['llm']:g} / {tot['harness']:g}"


def render_v2(k):
    v = k.get("v2") or {}
    if not v or v.get("error"):
        return f"  v2                {v.get('error', 'no timestamped lines')}"
    out = [f"  board (v2)        {v['board_solved']}/{v['board_modes']} at T+{_fmt(v['t_board'])}   "
           f"{v['board_modes'] - 1}/{v['board_modes']} at T+{_fmt(v['t_board_but1'])}   (T0 = {v['t0']} {v['t0_hms']}; "
           f"launch {'T+' + _fmt(v['launch']) if v['launch'] >= 0 else 'armed ' + _fmt(-v['launch']) + ' before'}; SLO: N/N by T+2:00)",
           f"  GM time           relay {v['gm_relay']:g} s / local {v['gm_local']:g} s (sum of call times, all lanes)",
           f"  {'lane':26} {'start':>6} {'single':>7} {'TT':>6} {'Mastery':>8}   single / TT / Mastery segment s "
           "(wall = GM / LLM / harness)"]
    for lab, ln in sorted(v["lanes"].items(), key=lambda x: (x[1]["end"] is None, x[1]["end"] or 0)):
        out.append(f"  {lab[:26]:26} {_fmt(ln['start']):>6} {_fmt(ln['single']):>7} {_fmt(ln['TT']):>6} "
                   f"{_fmt(ln['Mastery']):>8}   " + "  |  ".join(_seg(ln["segs"].get(n)) for n, _f, _m in SEGS)
                   + (f"   slot wait {ln['slot_wait']:g}s" if ln["slot_wait"] else ""))
    return "\n".join(out)


def board_row(k):
    v = k.get("v2") or {}
    if not v or v.get("error"):
        return None
    return (f"| {_key(k)} | {k['date']} | {v['t0']} {v['t0_hms']} | {_fmt(v['t_board'])} "
            f"({v['board_solved']}/{v['board_modes']}) | {_fmt(v['t_board_but1'])} | "
            f"{_fmt(None if k['t_all'] is None else k['t_all'] + _shift(k))} ({k['modes_solved']}/{k['modes']}) | "
            f"{_fmt(None if k['t_web'] is None else k['t_web'] + _shift(k))} ({k['web_solved']}/{k['web_modes']}) | "
            f"{_lag(k)} | {v['critical'] or '-'} | {_crit(v)} | {v['gm_relay']:g} / {v['gm_local']:g} | "
            f"{k['alerts']} | {k['live_cost']:.2f} |\n")


def _shift(k):
    """Legacy T+ (from the release line) -> v2 T+ (from the board's T0)."""
    return k.get("_start", 0) - k.get("_t0v2", 0)


def lane_rows(k):
    v = k.get("v2") or {}
    if not v or v.get("error"):
        return []
    out = []
    for lab, ln in sorted(v["lanes"].items()):
        rl = sum(s["gm_relay"] for s in ln["segs"].values())
        lc = sum(s["gm_local"] for s in ln["segs"].values())
        out.append(f"| {_key(k)} | {lab} | {_fmt(ln['start'])} | {_fmt(ln['single'])} | {_fmt(ln['TT'])} | "
                   f"{_fmt(ln['Mastery'])} | " + " | ".join(_seg(ln["segs"].get(n)) for n, _f, _m in SEGS)
                   + f" | {rl:g} / {lc:g} | {ln['slot_wait']:g} |\n")
    return out


def _upsert(text, title, header, key, rows):
    """Replace `key`'s rows in the table under `title` (created at the end when missing) with `rows`."""
    lines = text.splitlines(keepends=True)
    if not any(ln.rstrip("\n") == title for ln in lines):
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines += ["\n", title + "\n", "\n", *header.splitlines(keepends=True)]
    i = next(i for i, ln in enumerate(lines) if ln.rstrip("\n") == title)
    j = i + 1
    while j < len(lines) and not lines[j].startswith("|"):
        j += 1
    end = j
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    body = [ln for ln in lines[j:end] if not ln.startswith(f"| {key} |")]
    lines[j:end] = body + rows
    return "".join(lines)


def record_v2(k, path=None):
    """Upsert the day's Board v2 row and Lanes v2 rows (the legacy table is record()'s)."""
    path = Path(path) if path else ROOT / "reference" / "KPI.md"
    br = board_row(k)
    if br is None:
        return path
    text = path.read_text() if path.exists() else "# Daily KPI rows (hctf kpi --record)\n"
    text = _upsert(text, BOARD_TITLE, BOARD_HEADER, _key(k), [br])
    text = _upsert(text, LANES_TITLE, LANES_HEADER, _key(k), lane_rows(k))
    path.write_text(text)
    return path
