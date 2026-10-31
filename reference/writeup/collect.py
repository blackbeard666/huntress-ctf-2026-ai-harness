"""Phase 1 of the retrospective: aggregate every source into reference/writeup/data/stats.json.

Every block carries `source` and `coverage` so the writeup can cite where a number came from.
Run: python3 reference/writeup/collect.py   (read-only over the repo; writes only stats.json)
"""
import bisect
import collections
import csv
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "reference", "writeup", "data")
UTC = dt.timezone.utc
OUR_TEAM = "_blackb3ard_and_friends"
OUR_HOF = "_blackb3ard"
LANES = ["warmups", "metadata-forensics", "script-analysis", "binary-reverse-engineering", "mobile-android", "web"]


def drop(day):
    """Day N drops 2026-10-N 13:00Z (09:00 ET, 21:00 Manila)."""
    return dt.datetime(2026, 10, day, 13, 0, tzinfo=UTC)


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def ctf_day(t):
    """The drop window a UTC instant belongs to (day N = [drop N, drop N+1))."""
    d = (t - dt.datetime(2026, 10, 1, 13, 0, tzinfo=UTC)).total_seconds() // 86400 + 1
    return int(d)


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


# ---------------------------------------------------------------- official scoreboard (CourseStack)
def scoreboard():
    sb = load("coursestack/huntress_scoreboard.json")
    teams, qs = sb["scoreboard"], sb["questions"]
    qday, qmode, qpts = {}, {}, {}
    for q in qs:
        m = re.search(r"Day (\d+)", q.get("chapter_name") or "")
        qday[q["question_id"]] = int(m.group(1)) if m else 0
        txt = q.get("question_text") or ""
        qmode[q["question_id"]] = ("single" if txt.startswith("Single") else "tt" if txt.startswith("Time")
                                   else "mastery" if txt.startswith("Mastery") else "other")
        qpts[q["question_id"]] = q.get("points") or 0
    # per team: sorted score times + cumulative points
    series = []
    for t in teams:
        sc = sorted(t["scores"], key=lambda s: s["scored_at"])
        times = [ts(s["scored_at"]).timestamp() for s in sc]
        cum, c = [], 0
        for s in sc:
            c += s["points"]
            cum.append(c)
        series.append((t["group_name"] or "(anon)", times, cum, sc))
    ours = next(s for s in series if s[0] == OUR_TEAM)

    def standing(at):
        """(rank, points, n_scoring) of our team at instant `at` (UTC epoch); ties -> earlier last score wins."""
        def state(s):
            i = bisect.bisect_right(s[1], at)
            return (s[2][i - 1], s[1][i - 1]) if i else (0, None)
        mp, ml = state(ours)
        better = scoring = 0
        for s in series:
            p, last = state(s)
            if p > 0:
                scoring += 1
            if s is ours:
                continue
            if p > mp or (p == mp and p > 0 and last is not None and ml is not None and last < ml):
                better += 1
        return better + 1, mp, scoring

    # rank timeline: end of each day window, +15 min / +1 h after each drop, and hourly for the chart
    by_day = []
    for d in range(1, 32):
        t0 = drop(d).timestamp()
        end = min(t0 + 86400 - 1, max(s[1][-1] for s in series if s[1]) + 1) if d == 31 else t0 + 86400 - 1
        r15, _, _ = standing(t0 + 900)
        r60, _, _ = standing(t0 + 3600)
        rend, pend, nsc = standing(end)
        by_day.append({"day": d, "rank_t15m": r15, "rank_t1h": r60, "rank_end": rend, "points_end": pend,
                       "teams_scoring": nsc})
    hourly = []
    t, last = drop(1).timestamp(), max(s[1][-1] for s in series if s[1]) + 60
    while t <= last:
        r, p, _ = standing(t)
        hourly.append([int(t), r, p])
        t += 3600

    # per-day race: when each team finished ALL of that day's questions (drop-relative)
    day_qs = collections.defaultdict(set)
    for qid, d in qday.items():
        day_qs[d].add(qid)
    daily = []
    for d in range(1, 32):
        need, t0 = day_qs[d], drop(d).timestamp()
        fin = []
        for name, times, cum, sc in series:
            got = {s["question_id"]: ts(s["scored_at"]).timestamp() for s in sc if s["question_id"] in need}
            if len(got) == len(need) and need:
                fin.append((max(got.values()) - t0, name))
        fin.sort()
        mine = next((i + 1, f) for i, (f, n) in enumerate(fin) if n == OUR_TEAM) if any(
            n == OUR_TEAM for _, n in fin) else (None, None)
        our_sc = [s for s in ours[3] if s["question_id"] in need]
        first_s = min((ts(s["scored_at"]).timestamp() - t0 for s in our_sc), default=None)
        daily.append({"day": d, "questions": len(need), "points": sum(qpts[q] for q in need),
                      "our_finish_s": mine[1], "our_day_rank": mine[0], "teams_finished": len(fin),
                      "leader_finish_s": fin[0][0] if fin else None,
                      "top10_finish_s": [round(f, 1) for f, _ in fin[:10]],
                      "our_first_score_s": first_s})
    # per lane x day: when we finished that lane's questions (all modes, all of the lane's challenges that day)
    emoji = {"👶": "warmups", "🔎": "metadata-forensics", "📜": "script-analysis", "⚙": "binary-reverse-engineering",
             "📱": "mobile-android", "🌐": "web"}
    qlane = {q["question_id"]: next((v for k, v in emoji.items() if (q.get("lesson_name") or "").startswith(k)), None)
             for q in qs}
    lane_day = collections.defaultdict(dict)
    for s in ours[3]:
        lane, d = qlane.get(s["question_id"]), qday.get(s["question_id"])
        if lane and d:
            t = ts(s["scored_at"]).timestamp() - drop(d).timestamp()
            lane_day[lane][d] = max(lane_day[lane].get(d, 0), t)
    # first bloods
    fb = collections.Counter()
    fb_by_day = collections.Counter()
    for q in qs:
        b = q.get("first_blood") or {}
        if b.get("group_name") == OUR_TEAM:
            fb[qmode[q["question_id"]]] += 1
            fb_by_day[qday[q["question_id"]]] += 1
    me = next(t for t in teams if t["group_name"] == OUR_TEAM)
    pts_hist = collections.Counter(t["total_points"] for t in teams)
    return {
        "source": "CourseStack scoreboard API (ctf.huntress.com /api/student/huntress/scoreboard), captured 2026-10-31",
        "coverage": "every scored question of every team with its timestamp; ranks reconstructed by replaying "
                    "timestamps (ties broken by earlier last score, as the live board does)",
        "final": {"place": int(me["place"]), "points": me["total_points"], "max_points": max(pts_hist),
                  "teams_total": len(teams), "teams_scoring": sum(1 for t in teams if t["total_points"] > 0),
                  "teams_max_points": pts_hist[max(pts_hist)], "questions": len(qs),
                  "our_scored": len(me["scores"]), "last_scored_at": me["last_scored_at"]},
        "first_bloods": {"total": sum(fb.values()), "by_mode": dict(fb), "by_day": dict(fb_by_day)},
        "rank_by_day": by_day,
        "rank_hourly": hourly,
        "daily_race": daily,
        "lane_day_finish_s": {k: dict(sorted(v.items())) for k, v in lane_day.items()},
        "points_by_mode": dict(collections.Counter(qmode[q["question_id"]] for q in qs)),
    }


# ---------------------------------------------------------------- Hall of Fame speed board
def hof():
    out = {"source": "public speed scoreboard /api/speed-scoreboard, captured 2026-10-31", "modes": {}}
    for mode in ("time_trial", "mastery"):
        rows = load(f"hof_{mode}_rankings.json")["rows"]
        per = collections.defaultdict(list)
        for r in rows:
            per[r["challenge_id"]].append(r)
        mine = []
        for cid, rs in per.items():
            me = [r for r in rs if r["team_name"] == OUR_HOF]
            if not me:
                continue
            r = min(me, key=lambda x: x["rank"])
            lead = min(rs, key=lambda x: x["rank"])
            m = re.search(r"-day-(\d+)", cid)
            mine.append({"challenge": cid, "title": r.get("challenge_title"), "day": int(m.group(1)) if m else None,
                         "rank": r["rank"], "of": len(rs), "ms": r["elapsed_ms"], "leader_ms": lead["elapsed_ms"],
                         "par_ms": r.get("par_ms"), "answers": r.get("answer_count"), "sets": r.get("set_count")})
        mine.sort(key=lambda x: (x["day"] or 0, x["challenge"]))
        ranks = [m["rank"] for m in mine]
        out["modes"][mode] = {
            "teams": len({r["team_name"] for r in rows}), "entries": len(mine),
            "rank1": sum(r == 1 for r in ranks), "top3": sum(r <= 3 for r in ranks),
            "top10": sum(r <= 10 for r in ranks), "median_rank": sorted(ranks)[len(ranks) // 2] if ranks else None,
            "rows": mine}
    # biggest artifacts (answers per attempt) seen on the board
    out["largest"] = sorted(({"challenge": m["challenge"], "answers": m["answers"]}
                             for md in out["modes"].values() for m in md["rows"] if m["answers"]),
                            key=lambda x: -x["answers"])[:8]
    return out


# ---------------------------------------------------------------- GM list (inventory + our GM solve times)
def inventory():
    days = load("gm_list_by_day.json")
    per_day, lanes = [], collections.Counter()
    for d in range(1, 32):
        cs = days[str(d)]["challenges"]
        bases = {}
        for c in cs:
            base = c["id"].split("/")[0]
            bases.setdefault(base, {"name": c.get("name"), "lane": c.get("lane"), "modes": 0, "solved": 0,
                                    "sets": 0})
            bases[base]["modes"] += 1
            bases[base]["solved"] += bool(c.get("solved"))
            bases[base]["sets"] = max(bases[base]["sets"], c.get("ranked_set_count") or c.get("regular_set_count") or 0)
        for b in bases.values():
            lanes[b["lane"]] += 1
        per_day.append({"day": d, "challenges": len(bases), "modes": len(cs),
                        "solved": sum(bool(c.get("solved")) for c in cs),
                        "titles": [{"lane": b["lane"], "name": b["name"]} for b in bases.values()]})
    return {"source": "GM op=list for days 1-31, captured 2026-10-31", "per_day": per_day,
            "challenges": sum(p["challenges"] for p in per_day), "modes": sum(p["modes"] for p in per_day),
            "by_lane": dict(lanes)}


# ---------------------------------------------------------------- harness internals per day (hctf.kpi)
def kpis():
    from hctf import kpi
    out = []
    for d in range(1, 32):
        log = os.path.join(ROOT, ".run", f"day{d:02d}.log")
        if not os.path.exists(log):
            continue
        try:
            k = kpi.compute(d)
        except Exception as e:  # pragma: no cover - old log formats
            out.append({"day": d, "error": repr(e)})
            continue
        v2 = k.get("v2") or {}
        lanes = {}
        for name, ln in (v2.get("lanes") or {}).items():
            lanes[name] = {m: ln.get(m) for m in ("single", "TT", "Mastery", "end")}
            lanes[name]["llm_s"] = sum((s or {}).get("llm", 0) for s in (ln.get("segs") or {}).values())
            lanes[name]["gm_s"] = sum((s or {}).get("gm", 0) for s in (ln.get("segs") or {}).values())
        out.append({k2: k.get(k2) for k2 in (
            "day", "modes_solved", "modes", "t_all", "t_but1", "release_lag", "race_wins", "duel_wins",
            "timed_first_try", "timed_modes", "generalizes", "generalize_s", "generalize_rejected", "critical_chain",
            "untimed_fallbacks", "alerts", "live_cost", "post_cost", "web_solved", "web_modes", "t_web")}
                   | {"t_board": v2.get("t_board"), "board": f"{v2.get('board_solved')}/{v2.get('board_modes')}"
                      if v2 else None, "t0": v2.get("t0"), "lanes": lanes})
    return {"source": "hctf.kpi.compute over .run/dayNN.log (read-only)",
            "coverage": "day logs exist for D06-D31; D01-D05 predate the day log format", "days": out}


# ---------------------------------------------------------------- worker cost + tokens (metrics.tsv)
STAGE_GROUP = {"single": "solve", "live": "solve", "answer_first": "solve", "codify": "solve",
               "single-duel": "duels", "generalize-duel": "duels", "generalize": "generalize", "fix": "generalize",
               "prebuild": "prebuild", "ratchet": "post-run", "ratchet_log": "post-run", "speed-harden": "post-run",
               "train": "post-run"}


def workers():
    path = os.path.join(ROOT, ".run", "metrics.tsv")
    by_day = collections.defaultdict(lambda: collections.defaultdict(float))
    stage = collections.defaultdict(lambda: collections.defaultdict(float))
    models, outcomes = collections.Counter(), collections.Counter()
    tot = collections.defaultdict(float)
    with open(path) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = dt.datetime.fromisoformat(r["ts"]).replace(tzinfo=dt.timezone(dt.timedelta(hours=8)))
            d = ctf_day(t.astimezone(UTC))
            m = re.search(r"challenges/day(\d+)/", r.get("log") or "")
            if m and r["stage"] not in ("prebuild",):
                d = int(m.group(1))
            g = STAGE_GROUP.get(r["stage"], "other")
            cost = float(r["cost_usd"] or 0)
            toks = {k: float(r[k] or 0) for k in ("in_tok", "cache_read_tok", "cache_write_tok", "out_tok")}
            for b in (by_day[d], stage[g], tot):
                b["usd"] += cost
                b["workers"] += 1
                b["turns"] += float(r["turns"] or 0)
                b["wall_s"] += float(r["wall_s"] or 0)
                for k, v in toks.items():
                    b[k] += v
            by_day[d]["usd_" + g] += cost
            for mdl in (r["models"] or "").split(","):
                if mdl:
                    models[mdl] += 1
            outcomes[r["outcome"]] += 1
    return {"source": ".run/metrics.tsv (one row per claude -p worker; cost = API-equivalent $, exact or "
                      "token-estimated)",
            "coverage": "instrumented from Day 9 (10-09); days 1-8 workers are not in the ledger",
            "total": dict(tot), "by_stage": {k: dict(v) for k, v in stage.items()},
            "by_day": {d: dict(v) for d, v in sorted(by_day.items())},
            "models": dict(models), "outcomes": dict(outcomes)}


# ---------------------------------------------------------------- orchestrator sessions (Claude Code transcripts)
def transcripts():
    base = os.path.expanduser("~/.claude/projects")
    dirs = [d for d in os.listdir(base) if "huntress" in d and "alt" not in d]
    seen, tot = set(), collections.defaultdict(float)
    by_day = collections.defaultdict(lambda: collections.defaultdict(float))
    by_entry = collections.defaultdict(lambda: collections.defaultdict(float))
    sessions = set()
    for d in dirs:
        for p in glob.glob(os.path.join(base, d, "**", "*.jsonl"), recursive=True):
            with open(p, errors="replace") as f:
                for line in f:
                    if '"usage"' not in line:
                        continue
                    try:
                        j = json.loads(line)
                    except ValueError:
                        continue
                    msg = j.get("message") or {}
                    u, mid = msg.get("usage"), msg.get("id")
                    if not u or not mid or mid in seen:
                        continue
                    seen.add(mid)
                    sessions.add(j.get("sessionId"))
                    day = ctf_day(ts(j["timestamp"])) if j.get("timestamp") else 0
                    vals = {"in_tok": u.get("input_tokens", 0), "cache_read_tok": u.get("cache_read_input_tokens", 0),
                            "cache_write_tok": u.get("cache_creation_input_tokens", 0),
                            "out_tok": u.get("output_tokens", 0), "messages": 1}
                    kind = "subagent" if "/subagents/" in p else (j.get("entrypoint") or "cli")
                    for b in (tot, by_day[day], by_entry[kind]):
                        for k, v in vals.items():
                            b[k] += v or 0
    return {"source": "Claude Code session transcripts (~/.claude/projects, usage blocks deduped by message id)",
            "coverage": "orchestrator sessions, their subagents and sdk sessions that survive on disk; "
                        "pruned worker transcripts are covered by metrics.tsv instead",
            "sessions": len(sessions), "total": dict(tot), "by_kind": {k: dict(v) for k, v in by_entry.items()},
            "by_day": {d: dict(v) for d, v in sorted(by_day.items())}}


# ---------------------------------------------------------------- Homebase VM hours
def homebase():
    boots = collections.defaultdict(lambda: [None, None])
    with open(os.path.join(ROOT, ".run", "hb_ledger.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r.get("kind") != "vm":
                continue
            b = boots[r["boot"]]
            b[1] = max(b[1] or 0, r["ts"])
    by_day = collections.defaultdict(float)
    for boot, (_, last) in boots.items():
        h = max(0.0, (last - boot) / 3600)
        by_day[ctf_day(dt.datetime.fromtimestamp(boot, UTC))] += h
    hours = sum(by_day.values())
    return {"source": ".run/hb_ledger.jsonl (VM samples per boot; 2 credits per VM hour)",
            "coverage": "ledger starts 10-08; lower bound (samples only while the harness was watching)",
            "boots": len(boots), "vm_hours": round(hours, 1), "credits": round(hours * 2, 1),
            "by_day": {d: round(v, 2) for d, v in sorted(by_day.items())}}


# ---------------------------------------------------------------- engineering (git + code size)
def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True).stdout


def engineering():
    dates = git("log", "--all", "--format=%ad", "--date=short").split()
    per = collections.Counter(dates)
    loc = {}
    for d in ("hctf", "lib", "tests", "skills", "bin", "setup"):
        files = [f for f in git("ls-files", d).split("\n") if f.endswith((".py", ".sh", ".md", ".js"))]
        n = 0
        for f in files:
            try:
                with open(os.path.join(ROOT, f), errors="replace") as fh:
                    n += sum(1 for _ in fh)
            except OSError:
                pass
        loc[d] = {"files": len(files), "lines": n}
    # LOC growth: hctf+lib python lines at the last commit of each day
    growth = []
    for day in sorted(per):
        sha = git("rev-list", "-1", f"--before={day} 23:59:59", "HEAD").strip()
        if not sha:
            continue
        out = git("ls-tree", "-r", "-l", sha, "hctf", "lib")
        size = sum(int(p.split()[3]) for p in out.splitlines() if p.endswith(".py") and p.split()[3].isdigit())
        growth.append({"date": day, "py_bytes": size})
    tests = len(glob.glob(os.path.join(ROOT, "tests", "test_*.py")))
    return {"source": "git log --all + ls-files of the harness repo", "commits": len(dates),
            "branches": len([b for b in git("branch", "--format=%(refname:short)").split() if b]),
            "commits_by_date": dict(sorted(per.items())), "loc": loc, "growth": growth, "test_files": tests,
            "skills": len(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md"))),
            "first_commit": min(dates), "last_commit": max(dates)}


def main():
    stats = {"generated": dt.datetime.now(UTC).isoformat(timespec="seconds")}
    for name, fn in (("scoreboard", scoreboard), ("hof", hof), ("inventory", inventory), ("kpi", kpis),
                     ("workers", workers), ("transcripts", transcripts), ("homebase", homebase),
                     ("engineering", engineering)):
        print(f"[collect] {name}", file=sys.stderr, flush=True)
        stats[name] = fn()
    with open(os.path.join(DATA, "stats.json"), "w") as f:
        json.dump(stats, f, indent=1, default=str)
    print("wrote stats.json", file=sys.stderr)


if __name__ == "__main__":
    main()
