"""Hall of Fame = the GM's public speed scoreboard (separate from CourseStack points): per challenge, each team's
fastest GM-measured `hall_of_fame_eligible` timed attempt. `hctf hof [--day N]` -> our rank/ms vs #1 per challenge and
the day's summed time vs the teams that rank on every row. No auth; read-only.
"""
import json
import os
import re
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

URL = "https://2026.huntress.ctf.games/api/speed-scoreboard"
ROOT = Path(__file__).resolve().parents[1]
# main / alt team names (reference/gm-api.md "Hall of Fame")
TEAMS = tuple(t for t in os.environ.get("HCTF_HOF_TEAMS", "sec1-huntress-harness,[redacted]").split(",") if t)
PAGE = 1000


def fetch(mode, timeout=30):
    """Every ranking row of one mode (time_trial | mastery), paginated until a short page."""
    rows, offset = [], 0
    while True:
        q = f"{URL}?mode={mode}&view=rankings&limit={PAGE}&offset={offset}&sort=elapsed_ms&direction=asc"
        with urllib.request.urlopen(urllib.request.Request(q, headers={"User-Agent": "hctf-hof"}), timeout=timeout) as r:
            page = json.loads(r.read()).get("rows") or []
        rows += page
        if len(page) < PAGE:
            return rows
        offset += PAGE


def _day(cid):
    m = re.search(r"day-(\d+)", cid)
    return int(m.group(1)) if m else 0


def report(day=None, rows=None, teams=TEAMS):
    """Text table. rows: pre-fetched rows (tests); default: live fetch of both modes."""
    if rows is None:
        rows = fetch("time_trial") + fetch("mastery")
    best = {}
    for r in rows:   # one row per (team, challenge) -- dedupe across overlapping pages
        k = (r["team_name"], r["challenge_id"])
        if k not in best or r["elapsed_ms"] < best[k]["elapsed_ms"]:
            best[k] = r
    rows = list(best.values())
    days = [day] if day else sorted({_day(r["challenge_id"]) for r in rows})
    out = []
    for d in days:
        chal = sorted({r["challenge_id"] for r in rows if _day(r["challenge_id"]) == d})
        if not chal:
            out.append(f"Day {d}: no Hall of Fame rows (route not eligible yet, or nobody ranked)")
            continue
        out.append(f"== Day {d}  ({len(chal)} ranked challenge-modes)")
        out.append(f"{'challenge':58s} {'#1':>22s}  " + "  ".join(f"{t[:18]:>18s}" for t in teams))
        sums = defaultdict(lambda: [0, 0])
        for c in chal:
            rs = sorted((r for r in rows if r["challenge_id"] == c), key=lambda r: r["elapsed_ms"])
            for r in rs:
                sums[r["team_name"]][0] += r["elapsed_ms"]
                sums[r["team_name"]][1] += 1
            mine = {r["team_name"]: r for r in rs if r["team_name"] in teams}
            cells = [f"#{mine[t]['rank']:>3} {mine[t]['elapsed_ms']:>6}ms" if t in mine else f"{'-':>12s}" for t in teams]
            out.append(f"{c[:58]:58s} {rs[0]['team_name'][:12]:>12s} {rs[0]['elapsed_ms']:>6}ms  "
                       + "  ".join(f"{x:>18s}" for x in cells) + f"   (n={len(rs)})")
        full = sorted(((t, v[0]) for t, v in sums.items() if v[1] == len(chal)), key=lambda x: x[1])
        pos = {t: i + 1 for i, (t, _) in enumerate(full)}
        out.append(f"sum over all {len(chal)}: leader {full[0][0] if full else '-'} {full[0][1] if full else 0} ms; "
                   + "; ".join(f"{t} {sums[t][0]} ms over {sums[t][1]} row(s)"
                               + (f" = #{pos[t]} of {len(full)} complete teams" if t in pos else "")
                               for t in teams if t in sums))
    return "\n".join(out)


def snapshot(rows_tt, rows_m):
    """Save today's board under reference/hof/ (same shape as the 2026-10-12 snapshot: a list of rows per mode)."""
    d = ROOT / "reference" / "hof"
    d.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d")
    for mode, rows in (("time_trial", rows_tt), ("mastery", rows_m)):
        (d / f"{stamp}-{mode}.json").write_text(json.dumps(rows))
    return d
