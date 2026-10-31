"""Phase 2 of the retrospective: render stats.json into Hugo partials (inline SVG charts, tiles, tables).

Writes into the blog repo (carlo-notes):
  themes/carlo/layouts/partials/hctf2026/<name>.html   one partial per chart / table / tile row
  themes/carlo/layouts/partials/hctf2026/dashboard.html  the tabbed dashboard body
The post embeds them with the `hctf2026` shortcode; the dashboard layout includes dashboard.html.

Colour follows the blog's two-accent rule: red = what we did (our series), green = the platform (targets,
reference lines), everything else neutral. Classes are styled in main.css (HCTF RETROSPECTIVE section), so
both themes work without any per-chart colour. Every mark carries an SVG <title> (native hover, no JS) and every
chart has a table-view twin.
"""
import datetime as dt
import html
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATS = json.load(open(os.path.join(HERE, "data", "stats.json")))
BLOG = sys.argv[1] if len(sys.argv) > 1 else "/mnt/c/Users/cavila/Desktop/site-development/carlo-notes"
OUT = os.path.join(BLOG, "themes", "carlo", "layouts", "partials", "hctf2026")
os.makedirs(OUT, exist_ok=True)
UTC = dt.timezone.utc
E = html.escape
LANES = [("warmups", "warmups"), ("metadata-forensics", "metadata"), ("script-analysis", "script"),
         ("binary-reverse-engineering", "binary"), ("mobile-android", "mobile"), ("web", "web")]

# Short public-safe notes per day (harness view). Kept here so the post and the dashboard agree.
NOTES = {
    1: "Scored before this harness existed (first commit Oct 3)",
    2: "Scored before this harness existed",
    3: "Harness's first live day: 1.5 h lost guessing the GM's label spellings",
    4: "Solver fixes now roll back if they break anything; timed runs go through Homebase first",
    5: "Timed submits via Homebase: 2.76 -> 0.55 s",
    6: "VPN flapped every ~4 min (duplicate client)",
    7: "Hand-built solvers reverted: LLM-first rule",
    8: "GM silently changed how variants are served; stale socket; 157 MB download",
    9: "First perfect day: every mode first try",
    10: "Host asleep at the drop; run two days late",
    11: "Run late, but harness T+66 s from launch",
    12: "Run late; falling back to an untimed attempt saved warmups Mastery",
    13: "First Mastery mixing earlier days' concepts, fixed automatically",
    14: "Race submits partial answers early; today's encodings probed up front; 14/15 at T+49 s",
    15: "A 2.7 MB GM reply cut off mid-transfer",
    16: "5,475-question Mastery; ran out of memory after the run",
    17: "GM-side bug: unanswerable field, fixed ~4 h later",
    18: "0 generalizes; reuse race won 3/5 singles",
    19: "Web lane launches; driven by hand",
    20: "Web automated; ~10 min waiting for targets to come up",
    21: "MTU blackhole on the VPN; 33% packet loss",
    22: "0 alerts; reuse race 5/5",
    23: "10,465-field Mastery; a worker overflowed its context (worst day)",
    24: "Launched 16 min late",
    25: "Mastery mixing 123 encoded blobs; a 322 MB binary",
    26: "Big GM replies stuck on one SSH channel; CPU saturated",
    27: "Web one-shot credit double-spent, recovered",
    28: "392-field binary single",
    29: "Fix for the last few unanswered binary fields; usage limit hit afterwards",
    30: "Missed the drop (weekly usage limit); the bonus binary needed human help",
    31: "21/21 at T+4:15 on the scoreboard -> 3rd overall",
}
LATE = {3, 10, 11, 12, 30}   # not run at the drop (caught up later)
PRE = {1, 2}                  # scored before this harness existed


# ---------------------------------------------------------------- formatting
def dur(s):
    if s is None:
        return "-"
    s = float(round(s))
    if s < 60:
        return f"{s:.0f}s"
    if s < 3600:
        return f"{int(s // 60)}:{int(s % 60):02d}"
    if s < 86400:
        return f"{int(s // 3600)}h{int(s % 3600 // 60):02d}m"
    return f"{int(s // 86400)}d{int(s % 86400 // 3600):02d}h"


def num(n, d=0):
    return f"{n:,.{d}f}"


def compact(n):
    n = float(n)
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            v = n / div
            return f"{v:.1f}{suf}" if v < 100 else f"{v:.0f}{suf}"
    return f"{n:.0f}"


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def write(name, body):
    with open(os.path.join(OUT, f"{name}.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(body.strip() + "\n")


# ---------------------------------------------------------------- figure scaffolding
def figure(cid, title, desc, w, h, body, caption, table):
    return f"""
<figure class="hc-fig" id="fig-{cid}">
<p class="hc-fig-title">{E(title)}</p>
<svg class="hc-svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{cid}-t {cid}-d" preserveAspectRatio="xMidYMid meet">
<title id="{cid}-t">{E(title)}</title><desc id="{cid}-d">{E(desc)}</desc>
{body}
</svg>
<figcaption>{caption}</figcaption>
{table}
</figure>"""


def table(head, rows, cls="", summary="table view"):
    th = "".join(f"<th>{E(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    t = f'<div class="hc-tablewrap"><table class="hc-table {cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
    return f'<details class="hc-tv"><summary>{E(summary)}</summary>{t}</details>' if summary else t


class Axes:
    """Plot frame: x in [x0,x1] px, y in [y0,y1] px (y0 top)."""

    def __init__(self, w, h, l=56, r=18, t=18, b=34):
        self.w, self.h = w, h
        self.x0, self.x1, self.y0, self.y1 = l, w - r, t, h - b


def logy(v, lo, hi, ax, invert=False):
    f = (math.log(v) - math.log(lo)) / (math.log(hi) - math.log(lo))
    f = min(1, max(0, f))
    return ax.y0 + f * (ax.y1 - ax.y0) if invert else ax.y1 - f * (ax.y1 - ax.y0)


def linx(v, lo, hi, ax):
    return ax.x0 + (v - lo) / (hi - lo) * (ax.x1 - ax.x0)


def grid_y(ax, ticks, fy, fmt):
    out = []
    for v in ticks:
        y = fy(v)
        out.append(f'<line class="hc-grid" x1="{ax.x0}" x2="{ax.x1}" y1="{y:.1f}" y2="{y:.1f}"/>'
                   f'<text class="hc-tick" x="{ax.x0 - 8}" y="{y + 4:.1f}" text-anchor="end">{E(fmt(v))}</text>')
    return "".join(out)


def day_axis(ax, days, fx, every=5):
    out = [f'<line class="hc-axis" x1="{ax.x0}" x2="{ax.x1}" y1="{ax.y1}" y2="{ax.y1}"/>']
    for d in days:
        if d == 1 or d % every == 0 or d == days[-1]:
            out.append(f'<text class="hc-tick" x="{fx(d):.1f}" y="{ax.y1 + 18}" text-anchor="middle">{d}</text>')
    return "".join(out)


# ---------------------------------------------------------------- charts
SB = STATS["scoreboard"]
RACE = {r["day"]: r for r in SB["daily_race"]}
RANKD = {r["day"]: r for r in SB["rank_by_day"]}


def our_day_finish(d):
    r = RACE[d]
    if r["our_finish_s"] is not None:
        return r["our_finish_s"]
    lanes = [v.get(str(d)) for v in SB["lane_day_finish_s"].values() if v.get(str(d))]
    return max(lanes) if lanes else None


def chart_rank_month():
    w, h = 860, 320
    ax = Axes(w, h, l=48)
    t0 = dt.datetime(2026, 10, 1, 13, tzinfo=UTC).timestamp()
    t1 = dt.datetime(2026, 10, 31, 16, tzinfo=UTC).timestamp()
    fx = lambda t: linx(t, t0, t1, ax)
    fy = lambda r: logy(r, 1, 128, ax, invert=True)
    pts = [(t, r) for t, r, p in SB["rank_hourly"] if p > 0]
    path = []
    for i, (t, r) in enumerate(pts):
        x, y = fx(t), fy(r)
        if i == 0:
            path.append(f"M{x:.1f},{y:.1f}")
        else:
            path.append(f"H{x:.1f}V{y:.1f}")
    body = [grid_y(ax, [1, 3, 10, 30, 100], fy, lambda v: ordinal(v))]
    for d in range(1, 32):
        x = fx(dt.datetime(2026, 10, d, 13, tzinfo=UTC).timestamp())
        if d in (1, 5, 10, 15, 20, 25, 31):
            body.append(f'<text class="hc-tick" x="{x:.1f}" y="{ax.y1 + 18}" text-anchor="middle">Oct {d}</text>')
        if d in LATE:
            body.append(f'<rect class="hc-late" x="{x:.1f}" y="{ax.y0}" width="{fx(t0 + 86400) - fx(t0):.1f}" '
                        f'height="{ax.y1 - ax.y0}"><title>Day {d}: not run at the drop</title></rect>')
    body.append(f'<line class="hc-axis" x1="{ax.x0}" x2="{ax.x1}" y1="{ax.y1}" y2="{ax.y1}"/>')
    body.append(f'<path class="hc-line hc-ours" d="{"".join(path)}"/>')
    for d in range(1, 32):
        r = RANKD[d]
        x = fx(dt.datetime(2026, 10, d, 13, tzinfo=UTC).timestamp() + 86400 - 60) if d < 31 else fx(t1 - 600)
        y = fy(r["rank_end"])
        body.append(f'<g class="hc-hit"><circle class="hc-dot hc-ours" cx="{x:.1f}" cy="{y:.1f}" r="4"/>'
                    f'<circle class="hc-hitarea" cx="{x:.1f}" cy="{y:.1f}" r="12"/>'
                    f'<title>End of day {d}: {ordinal(r["rank_end"])} of {r["teams_scoring"]} scoring teams '
                    f'({r["points_end"]} pts)</title></g>')
    fin = RANKD[31]
    xf, yf = fx(t1 - 600), fy(fin["rank_end"])
    body.append(f'<text class="hc-label" x="{xf - 10:.1f}" y="{yf - 10:.1f}" text-anchor="end">final: 3rd of '
                f'{SB["final"]["teams_total"]:,}</text>')
    worst = max(SB["rank_by_day"], key=lambda r: r["rank_end"])
    xw = fx(dt.datetime(2026, 10, worst["day"], 13, tzinfo=UTC).timestamp() + 86400 - 60)
    body.append(f'<text class="hc-label" x="{xw:.1f}" y="{fy(worst["rank_end"]) + 18:.1f}" text-anchor="middle">'
                f'{ordinal(worst["rank_end"])} (day {worst["day"]})</text>')
    rows = [[f"Day {r['day']}", ordinal(r["rank_t15m"]), ordinal(r["rank_t1h"]), ordinal(r["rank_end"]),
             num(r["points_end"]), num(r["teams_scoring"])] for r in SB["rank_by_day"]]
    return figure("rank", "Overall placement through October",
                  "Our overall rank on the official scoreboard, replayed hourly from every team's score timestamps. "
                  "Lower is better; the axis is logarithmic.", w, h, "".join(body),
                  "Overall rank on the CourseStack scoreboard, replayed hour by hour from every team's score "
                  "timestamps (ties broken by who scored last first, as the live board does). Shaded days were not "
                  "run at the drop. Log scale.",
                  table(["day", "rank +15 min", "rank +1 h", "rank end of day", "points", "teams scoring"], rows))


def chart_daily_finish():
    w, h = 860, 360
    ax = Axes(w, h, l=56, t=40)
    days = list(range(1, 32))
    fx = lambda d: linx(d, 0.5, 31.5, ax)
    lo, hi = 5, 3 * 86400
    fy = lambda s: logy(max(s, lo), lo, hi, ax)
    ticks = [10, 60, 300, 1800, 7200, 43200, 86400 * 2]
    body = [grid_y(ax, ticks, fy, lambda v: {10: "10s", 60: "1m", 300: "5m", 1800: "30m", 7200: "2h",
                                              43200: "12h", 172800: "2d"}[v])]
    y2 = fy(120)
    body.append(f'<line class="hc-target" x1="{ax.x0}" x2="{ax.x1}" y1="{y2:.1f}" y2="{y2:.1f}"/>'
                f'<text class="hc-label hc-plat-t" x="{ax.x0 + 6}" y="{y2 - 6:.1f}">2:00 target</text>')
    body.append(day_axis(ax, days, fx))
    rows = []
    for d in days:
        r, x = RACE[d], fx(d)
        top = r["top10_finish_s"]
        ours = our_day_finish(d)
        if top:
            body.append(f'<line class="hc-range" x1="{x:.1f}" x2="{x:.1f}" y1="{fy(top[0]):.1f}" '
                        f'y2="{fy(top[-1]):.1f}"/>')
            body.append(f'<circle class="hc-dot hc-field" cx="{x:.1f}" cy="{fy(top[0]):.1f}" r="4"/>')
        if ours is not None:
            cls = "hc-ours" + (" hc-hollow" if d in LATE | PRE else "")
            body.append(f'<g class="hc-hit"><circle class="hc-dot {cls}" cx="{x:.1f}" cy="{fy(ours):.1f}" r="5"/>'
                        f'<rect class="hc-hitarea" x="{x - 12:.1f}" y="{ax.y0}" width="24" height="{ax.y1 - ax.y0}"/>'
                        f'<title>Day {d}: we finished at T+{dur(ours)}'
                        f'{" (day rank " + str(r["our_day_rank"]) + ")" if r["our_day_rank"] else ""}; '
                        f'fastest team T+{dur(top[0]) if top else "-"}; 10th T+{dur(top[-1]) if top else "-"}'
                        f'{" - not run at the drop" if d in LATE else ""}{" - before this harness existed" if d in PRE else ""}</title></g>')
        rows.append([f"Day {d}", f"T+{dur(ours)}" + (" *" if d in LATE else " †" if d in PRE else ""),
                     ordinal(r["our_day_rank"]) if r["our_day_rank"] else "-", num(r["teams_finished"]),
                     f"T+{dur(top[0])}" if top else "-", f"T+{dur(top[-1])}" if top else "-"])
    lg = (f'<g class="hc-legend" transform="translate({ax.x0},{12})">'
          f'<circle class="hc-dot hc-ours" cx="5" cy="5" r="5"/><text x="16" y="9">us</text>'
          f'<circle class="hc-dot hc-ours hc-hollow" cx="56" cy="5" r="5"/><text x="67" y="9">us, late or pre-harness</text>'
          f'<circle class="hc-dot hc-field" cx="250" cy="5" r="4"/><text x="260" y="9">fastest team</text>'
          f'<line class="hc-range" x1="370" x2="370" y1="-1" y2="11"/><text x="378" y="9">fastest to 10th</text></g>')
    body.append(lg)
    return figure("finish", "Time to clear each day's board",
                  "For each of the 31 days, the time from the drop until we scored that day's last question, "
                  "against the fastest team and the spread of the ten fastest teams. Log scale.",
                  w, h, "".join(body),
                  "Drop to the day's last scored question, from the official scoreboard. Hollow dots: days the "
                  "harness did not run at the drop, and days 1-2, played before it existed. The grey bar spans the fastest to the 10th-fastest team "
                  "that cleared the whole day. Log scale.",
                  table(["day", "our finish", "our day rank", "teams that cleared the day", "fastest", "10th"], rows))


def chart_lane_heat():
    days = list(range(1, 32))
    cw, ch, l, t = 24, 26, 86, 22
    w, h = l + cw * 31 + 10, t + ch * 6 + 40
    bins = [(60, "≤1m"), (120, "≤2m"), (300, "≤5m"), (900, "≤15m"), (3600, "≤1h"), (1e12, ">1h")]
    body = []
    for i, d in enumerate(days):
        if d == 1 or d % 5 == 0 or d == 31:
            body.append(f'<text class="hc-tick" x="{l + i * cw + cw / 2:.1f}" y="{t - 8}" text-anchor="middle">{d}</text>')
    rows = []
    for j, (lane, short) in enumerate(LANES):
        y = t + j * ch
        body.append(f'<text class="hc-tick" x="{l - 8}" y="{y + ch / 2 + 4:.1f}" text-anchor="end">{short}</text>')
        v = SB["lane_day_finish_s"].get(lane, {})
        row = [short]
        for i, d in enumerate(days):
            s = v.get(str(d))
            row.append(dur(s) if s else "")
            if s is None:
                continue
            k = next(n for n, (lim, _) in enumerate(bins) if s <= lim)
            body.append(f'<rect class="hc-cell hc-b{k}" x="{l + i * cw + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}">'
                        f'<title>Day {d} {short}: T+{dur(s)}{" (run late)" if d in LATE else ""}</title></rect>')
        rows.append(row)
    ly = t + 6 * ch + 14
    for k, (_, lab) in enumerate(bins):
        x = l + k * 72
        body.append(f'<rect class="hc-cell hc-b{k}" x="{x}" y="{ly}" width="14" height="14"/>'
                    f'<text class="hc-tick" x="{x + 20}" y="{ly + 11}">{E(lab)}</text>')
    return figure("lanes", "Time to finish each lane, every day",
                  "A grid of six lanes by 31 days; darker green means the lane's last question was scored sooner "
                  "after the drop.", w, h, "".join(body),
                  "Drop to the lane's last scored question (all three modes; web counts every web challenge that "
                  "day). Web launched on day 19. Stronger fill = faster; see the key.",
                  table(["lane"] + [str(d) for d in days], rows, cls="hc-wide"))


def bars(cid, title, desc, caption, labels, values, fmt, w=860, h=240, hl=None, head=("day", "value"), tick_every=5,
         yfmt=None):
    ax = Axes(w, h, l=56)
    n = len(values)
    fx = lambda i: linx(i, -0.5, n - 0.5, ax)
    vmax = max(values) or 1
    step0 = 10 ** math.floor(math.log10(vmax))
    step = step0
    for m in (0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5):
        if vmax / (step0 * m) <= 6:
            step = step0 * m
            break
    top = math.ceil(vmax / step) * step
    fy = lambda v: ax.y1 - v / top * (ax.y1 - ax.y0)
    ticks = [i * step for i in range(int(top / step) + 1)]
    body = [grid_y(ax, ticks, fy, yfmt or fmt)]
    bw = min(16, (ax.x1 - ax.x0) / n * 0.6)
    body.append(f'<line class="hc-axis" x1="{ax.x0}" x2="{ax.x1}" y1="{ax.y1}" y2="{ax.y1}"/>')
    imax = values.index(vmax)
    for i, (lab, v) in enumerate(zip(labels, values)):
        x = fx(i)
        cls = "hc-bar hc-ours" if (hl and i in hl) else "hc-bar"
        body.append(f'<g class="hc-hit"><rect class="{cls}" x="{x - bw / 2:.1f}" y="{fy(v):.1f}" width="{bw:.1f}" '
                    f'height="{max(0.0, ax.y1 - fy(v)):.1f}"/><rect class="hc-hitarea" x="{x - 12:.1f}" y="{ax.y0}" '
                    f'width="24" height="{ax.y1 - ax.y0}"/><title>{E(str(lab))}: {E(fmt(v))}</title></g>')
        if i % tick_every == 0 or i == n - 1:
            body.append(f'<text class="hc-tick" x="{x:.1f}" y="{ax.y1 + 18}" text-anchor="middle">{E(str(lab))}</text>')
    body.append(f'<text class="hc-label" x="{fx(imax):.1f}" y="{fy(vmax) - 8:.1f}" text-anchor="middle">'
                f'{E(fmt(vmax))}</text>')
    rows = [[E(str(l_)), E(fmt(v))] for l_, v in zip(labels, values)]
    return figure(cid, title, desc, w, h, "".join(body), caption, table(list(head), rows))


def dumbbells():
    items = [  # (label, before_s, after_s, note)
        ("Timed submit (Homebase inside proxy)", 2.76, 0.55, "day 5"),
        ("Solver cold start (warm zygote fork)", 0.19, 0.033, "day 12"),
        ("Worker's first shell call (edit-diff off)", 24.6, 1.0, "day 13"),
        ("Warmups decode, 83 blobs (joint decode)", 751, 16.5, "day 17"),
        ("Metadata single (registry race, no LLM)", 43, 0.7, "day 15"),
        ("Script Mastery start (big-reply routing)", 60, 6.3, "day 26"),
        ("Failed-variant evidence pull", 900, 37.9, "day 8"),
        ("Release detection lag", 13.5, 2.6, "day 17"),
        ("Label cache write, 6.6k answers", 20, 0.05, "day 16"),
        ("Metadata Mastery solve (fast path)", 1.9, 0.74, "day 31"),
        ("Replayed board, 15 modes (race-first)", 163, 90, "day 24 replay"),
        ("Binary single, ~400 fields (answer-first)", 219, 79, "day 29"),
    ]
    w, rh, l, r, t = 860, 26, 300, 70, 30
    h = t + rh * len(items) + 30
    ax = Axes(w, h, l=l, r=r, t=t, b=30)
    lo, hi = 0.02, 2000
    fx = lambda s: ax.x0 + (math.log(s) - math.log(lo)) / (math.log(hi) - math.log(lo)) * (ax.x1 - ax.x0)
    body = []
    for v, lab in ((0.1, "0.1s"), (1, "1s"), (10, "10s"), (60, "1m"), (600, "10m")):
        x = fx(v)
        body.append(f'<line class="hc-grid" x1="{x:.1f}" x2="{x:.1f}" y1="{t - 6}" y2="{h - 26}"/>'
                    f'<text class="hc-tick" x="{x:.1f}" y="{h - 10}" text-anchor="middle">{lab}</text>')
    rows = []
    for i, (lab, b, a, when) in enumerate(items):
        y = t + i * rh + rh / 2
        xb, xa = fx(b), fx(a)
        sp = b / a
        body.append(f'<g class="hc-hit"><text class="hc-tick hc-rowlab" x="{l - 12}" y="{y + 4:.1f}" text-anchor="end">'
                    f'{E(lab)}</text><line class="hc-range" x1="{xa:.1f}" x2="{xb:.1f}" y1="{y:.1f}" y2="{y:.1f}"/>'
                    f'<circle class="hc-dot hc-field" cx="{xb:.1f}" cy="{y:.1f}" r="4"/>'
                    f'<circle class="hc-dot hc-ours" cx="{xa:.1f}" cy="{y:.1f}" r="5"/>'
                    f'<text class="hc-tick" x="{ax.x1 + 8}" y="{y + 4:.1f}">{sp:,.0f}x</text>'
                    f'<rect class="hc-hitarea" x="0" y="{y - rh / 2:.1f}" width="{w}" height="{rh}"/>'
                    f'<title>{E(lab)}: {b:g}s -> {a:g}s ({sp:,.1f}x faster, {when})</title></g>')
        rows.append([E(lab), f"{b:g}s", f"{a:g}s", f"{sp:,.1f}x", when])
    body.append(f'<g class="hc-legend" transform="translate({l},{12})"><circle class="hc-dot hc-field" cx="5" cy="0" r="4"/>'
                f'<text x="14" y="4">before</text><circle class="hc-dot hc-ours" cx="70" cy="0" r="5"/>'
                f'<text x="80" y="4">after</text></g>')
    return figure("wins", "The changes that moved the clock",
                  "Before and after timings for twelve harness changes, on a logarithmic time axis.",
                  w, h, "".join(body),
                  "Before (grey) and after (red) for the measured changes, from the run logs and post-mortems. Log "
                  "scale; the right column is the speed-up.",
                  table(["change", "before", "after", "speed-up", "landed"], rows))


def architecture():
    # Snake layout on a 4-column grid: row 1 solves the single (left -> right), row 2 runs the timed modes
    # (right -> left), row 3 learns from failures (left -> right). Orthogonal arrows only.
    cx = [10, 225, 440, 655]          # column x
    bw, bh, ry = 195, 58, [24, 132, 240]

    def box(c, r, ti, sub, cls="", span=1):
        x, y, w_ = cx[c], ry[r], bw * span + (215 - bw) * (span - 1)
        return (f'<g class="hc-node {("hc-node-" + cls) if cls else ""}"><rect x="{x}" y="{y}" width="{w_}" '
                f'height="{bh}"/><text class="hc-node-t" x="{x + 12}" y="{y + 24}">{E(ti)}</text>'
                f'<text class="hc-node-s" x="{x + 12}" y="{y + 43}">{E(sub)}</text></g>')

    def arrow(x1, y1, x2, y2):
        return (f'<line class="hc-edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#hc-arrow)"/>')

    mid = lambda r: ry[r] + bh / 2
    body = ['<defs><marker id="hc-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path class="hc-arrowhead" d="M0,0L8,4L0,8z"/></marker></defs>']
    for c in range(3):                                     # row 1 left -> right
        body.append(arrow(cx[c] + bw, mid(0), cx[c + 1] - 2, mid(0)))
    for c in (2, 3):                                       # race + worker both reach CORRECT
        body.append(arrow(cx[c] + bw / 2, ry[0] + bh, cx[c] + bw / 2, ry[1] - 2))
    body.append(arrow(cx[2], mid(1), cx[1] + bw + 2, mid(1)))      # CORRECT -> timed runner
    body.append(arrow(cx[1], mid(1), cx[0] + bw + 2, mid(1)))      # timed runner -> Homebase
    body.append(arrow(cx[1] + bw / 2, ry[1] + bh, cx[1] + bw / 2, ry[2] - 2))   # fail -> generalize
    body.append(arrow(cx[1] + bw, mid(2), cx[2] - 2, mid(2)))
    body.append(arrow(cx[2] + bw, mid(2), cx[3] - 2, mid(2)))
    body += [
        box(0, 0, "drop watcher", "GM probe every 0.3 s", "plat"),
        box(1, 0, "triage", "bytes -> tools, no LLM"),
        box(2, 0, "reuse race", "prior solvers race", "ours"),
        box(3, 0, "claude -p worker", "+ answer-first helper", "ours"),
        box(2, 1, "GM CORRECT + verified solve.py", "the chain moves on", "plat", span=2),
        box(1, 1, "timed runner", "solve.py, no LLM"),
        box(0, 1, "Homebase VM", "in-network relay", "plat"),
        box(1, 2, "generalize + duel", "+ live answer", "ours"),
        box(2, 2, "regression cases", "every failed variant"),
        box(3, 2, "ratchet + prebuild", "overnight, test-gated"),
    ]
    return figure("arch", "How one challenge flows through the harness",
                  "Row one: drop watcher, triage, reuse race and worker reach GM CORRECT with a verified solver. "
                  "Row two: the timed runner replays that solver, via Homebase. Row three: a failed variant goes to "
                  "generalize and duel, becomes a regression case, and feeds the overnight ratchet.", 860, 310,
                  "".join(body),
                  "One chain per challenge, all chains in parallel. Red: where answers come from. Green: the "
                  "platform. Overnight, the cases and the ratchet feed the next day's race.", "")


def chain_states():
    # One row of chain stages (left -> right), with the escalation / repair states underneath. Mirrors the
    # stateDiagram in the harness's ARCHITECTURE.md (stages as written to chain.json by set_state).
    cx = [10 + 170 * i for i in range(5)]
    bw, bh, ry = 156, 58, [30, 168]

    def box(c, r, ti, sub, cls="", span=1):
        x, y, w_ = cx[c], ry[r], bw + 170 * (span - 1)
        return (f'<g class="hc-node {("hc-node-" + cls) if cls else ""}"><rect x="{x}" y="{y}" width="{w_}" '
                f'height="{bh}"/><text class="hc-node-t" x="{x + 12}" y="{y + 24}">{E(ti)}</text>'
                f'<text class="hc-node-s" x="{x + 12}" y="{y + 43}">{E(sub)}</text></g>')

    def arrow(x1, y1, x2, y2):
        return f'<line class="hc-edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#hc-arrow-c)"/>'

    def lab(x, y, t, anchor):
        return f'<text class="hc-rowlab" x="{x}" y="{y}" text-anchor="{anchor}">{E(t)}</text>'

    mid0, top1, bot0 = ry[0] + bh / 2, ry[1], ry[0] + bh
    ym = (bot0 + top1) / 2 + 4
    body = ['<defs><marker id="hc-arrow-c" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path class="hc-arrowhead" d="M0,0L8,4L0,8z"/></marker></defs>']
    for c in range(4):
        body.append(arrow(cx[c] + bw, mid0, cx[c + 1] - 2, mid0))
    for c, down, up in ((0, "crash", "retry once"), (2, "variant fails", ""), (3, "", "accepted / restored")):
        x = cx[c] + bw / 2
        body.append(arrow(x - 18, bot0, x - 18, top1 - 2))
        body.append(arrow(x + 18, top1, x + 18, bot0 + 2))
        if down:
            body.append(lab(x - 26, ym, down, "end"))
        if up:
            body.append(lab(x + 26, ym, up, "start"))
    x = cx[1] + bw / 2
    body.append(arrow(x, bot0, x, top1 - 2))
    body.append(lab(x + 8, ym, "stuck", "start"))
    body += [
        box(0, 0, "queued", "armed before the drop"),
        box(1, 0, "single", "fetch · race · solve", "ours"),
        box(2, 0, "time_trial", "running · retrying"),
        box(3, 0, "mastery", "re-pass TT if needed"),
        box(4, 0, "done", "GM CORRECT on all 3", "plat"),
        box(0, 1, "crash-retry", "solved modes kept"),
        box(1, 1, "help / blocked", "HELP.md for a human"),
        box(2, 1, "generalizing", "transactional edit · duel · live answer", "ours", span=2),
    ]
    rows = [
        ("<code>queued</code>", "chain created the moment its lane lists"),
        ("<code>single:fetch</code> / <code>reuse-won</code> / <code>solving</code>",
         "download ∥ warm worker; the reuse race can finish it alone"),
        ("<code>single:help</code> / <code>blocked</code>", "worker wrote HELP.md, or launches ran out"),
        ("<code>&lt;mode&gt;:running</code> / <code>retrying</code> / <code>continuing</code>",
         "timed runner: start → download → solve.py → submit"),
        ("<code>&lt;mode&gt;:generalizing</code> / <code>fixing</code>",
         "variant captured as a case; worker edits the solver; kept only if nothing regresses"),
        ("<code>&lt;mode&gt;:untimed</code> / <code>rate-limited</code> / <code>start-refused</code>",
         "pool exhausted or GM pushback: fall back, wait, resume the same attempt"),
        ("<code>done</code>", "all three modes GM-CORRECT"),
        ("<code>crash-retry</code> / <code>crashed</code>", "exception: one retry that skips solved modes"),
    ]
    return figure("chain", "The chain state machine",
                  "Top row: queued, single, time_trial, mastery, done. Below: crash-retry under queued, "
                  "help or blocked under single, and a shared generalizing state that both timed modes drop into "
                  "when a variant fails and return from once the edit is accepted or restored.", 860, 240,
                  "".join(body),
                  "Every chain writes its stage to <code>chain.json</code> atomically; the feed, dashboard and "
                  "<code>hctf why</code> all read it.", table(("stage", "meaning"), rows, summary="all stages"))


REPO = "https://github.com/blackbeard666/huntress-ctf-2026-ai-harness/blob/HEAD/"


def system_loop():
    # The whole system as a daily loop. Top row: the drop, left -> right, from the operator session down to the GM.
    # Bottom row: overnight, right -> left, from what the run recorded back to the next warm-up.
    cx = [10 + 170 * i for i in range(5)]
    bw, bh, ry = 156, 58, [30, 168]

    def box(c, r, ti, sub, cls=""):
        x, y = cx[c], ry[r]
        return (f'<g class="hc-node {("hc-node-" + cls) if cls else ""}"><rect x="{x}" y="{y}" width="{bw}" '
                f'height="{bh}"/><text class="hc-node-t" x="{x + 12}" y="{y + 24}">{E(ti)}</text>'
                f'<text class="hc-node-s" x="{x + 12}" y="{y + 43}">{E(sub)}</text></g>')

    def arrow(x1, y1, x2, y2):
        return f'<line class="hc-edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#hc-arrow-s)"/>'

    def lab(x, y, t, anchor):
        return f'<text class="hc-rowlab" x="{x}" y="{y}" text-anchor="{anchor}">{E(t)}</text>'

    mid = lambda r: ry[r] + bh / 2
    bot0, top1 = ry[0] + bh, ry[1]
    ym = (bot0 + top1) / 2 + 4
    body = ['<defs><marker id="hc-arrow-s" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path class="hc-arrowhead" d="M0,0L8,4L0,8z"/></marker></defs>']
    for c in range(4):
        body.append(arrow(cx[c] + bw, mid(0), cx[c + 1] - 2, mid(0)))          # the drop, left -> right
        body.append(arrow(cx[c + 1], mid(1), cx[c] + bw + 2, mid(1)))          # overnight, right -> left
    x4, x0 = cx[4] + bw / 2, cx[0] + bw / 2
    body.append(arrow(x4, bot0, x4, top1 - 2))
    body.append(lab(x4 - 8, ym, "every attempt recorded", "end"))
    body.append(arrow(x0, top1, x0, bot0 + 2))
    body.append(lab(x0 + 8, ym, "next warm-up", "start"))
    body += [
        box(0, 0, "operator session", "Claude Code + me", "ours"),
        box(1, 0, "hctf run", "Python, no LLM"),
        box(2, 0, "chains, one each", "3 modes, in order"),
        box(3, 0, "workers", "claude -p in bwrap", "ours"),
        box(4, 0, "Game Master", "judges every answer", "plat"),
        box(4, 1, "the run's record", "logs, cases, cost"),
        box(3, 1, "post-run", "library merge, tests"),
        box(2, 1, "post-mortem + fixes", "operator + agents", "ours"),
        box(1, 1, "prebuild", "breadth, off-peak"),
        box(0, 1, "rehearsal", "replay + fault suite"),
    ]
    a = lambda path, text=None: f'<a href="{REPO}{path}"><code>{E(text or path)}</code></a>'
    rows = [
        ("operator session", "a long-running Claude Code session I direct: arms the day, watches the feed, intervenes, "
         "writes post-mortems and code", a("bin/day.sh") + ", " + a("hctf/feed.py")),
        ("hctf run", "detects the release, starts one chain per challenge, caps workers at five slots",
         a("hctf/orchestrate.py")),
        ("chains", "one thread per challenge: single → Time Trial → Mastery, state in chain.json",
         a("hctf/orchestrate.py")),
        ("workers", "headless Claude Code in a bubblewrap sandbox, steered by hooks", a("hctf/workers.py") + ", " +
         a(".claude/hooks/nudge.py")),
        ("Game Master", "the organizers' API; the only judge of right and wrong", a("hctf/gm.py")),
        ("the run's record", "chain states, worker logs, regression cases, the cost ledger", a("hctf/solvers.py")),
        ("post-run", "ratchet (library merge), speed-harden, train (replay every earlier day), behind tests",
         a("hctf/postrun.py")),
        ("post-mortem + fixes", "the operator reads the timeline and costs, writes a plan; parallel agents implement it",
         a("reference/D28_POSTMORTEM.md")),
        ("prebuild", "off-peak workers build decoders for variants not seen yet, kept behind fixtures",
         a("hctf/prebuild.py")),
        ("rehearsal", "replay a solved day on the fake GM; the fault suite and preflight gate the next launch",
         a("hctf/replay_gm.py") + ", " + a("bin/preflight.sh")),
    ]
    return figure("system", "How the whole system runs, day after day",
                  "Top row, during a drop: the operator session starts hctf run, which runs one chain per challenge, "
                  "whose workers submit to the Game Master. Bottom row, overnight: the run's record feeds the post-run, "
                  "then a post-mortem and fixes, then the prebuild, then a rehearsal, which leads back to the next "
                  "day's warm-up.", 860, 240, "".join(body),
                  "One loop per day. Red: where the thinking happens (the operator session, its agents and the workers). Green: "
                  "the platform.", table(("stage", "what it does", "code"), rows, summary="stages and code"))


# ---------------------------------------------------------------- tiles + tables
W, T, HB, ENG, HOF, INV = (STATS[k] for k in ("workers", "transcripts", "homebase", "engineering", "hof", "inventory"))
TOK_OUT = W["total"]["out_tok"] + T["total"]["out_tok"]
TOK_CACHE = W["total"]["cache_read_tok"] + T["total"]["cache_read_tok"]
TOK_WRITE = W["total"]["cache_write_tok"] + T["total"]["cache_write_tok"]
TOK_IN = W["total"]["in_tok"] + T["total"]["in_tok"]
TOK_ALL = TOK_OUT + TOK_CACHE + TOK_WRITE + TOK_IN
FINAL = SB["final"]


def tiles(items, cls=""):
    cells = "".join(f'<div class="hc-tile"><p class="hc-tile-l">{E(l_)}</p><p class="hc-tile-v">{E(v)}</p>'
                    f'{f"<p class=hc-tile-n>{E(n)}</p>" if n else ""}</div>' for l_, v, n in items)
    return f'<div class="hc-tiles {cls}">{cells}</div>'


def headline_tiles():
    return tiles([
        ("final placement", f"{ordinal(FINAL['place'])} of {FINAL['teams_total']:,}",
         f"{FINAL['teams_scoring']:,} teams scored"),
        ("points", f"{FINAL['points']:,} / {FINAL['max_points']:,}", f"{FINAL['our_scored']} of {FINAL['questions']} questions"),
        ("challenge modes cleared", f"{INV['modes']}", f"{INV['challenges']} challenges, 31 days, 6 lanes"),
        ("final day cleared", f"T+{dur(RACE[31]['our_finish_s'])}", "21 modes, drop to last point"),
        ("worker agents launched", f"{W['total']['workers']:,.0f}", f"{W['total']['turns']:,.0f} turns, from day 9"),
        ("tokens processed", compact(TOK_ALL), f"{compact(TOK_OUT)} output, {TOK_CACHE / TOK_ALL:.0%} cache reads"),
        ("worker spend (API-equivalent)", f"${W['total']['usd']:,.0f}", "list-price equivalent, from day 9"),
        ("harness commits", f"{ENG['commits']}", f"{ENG['loc']['hctf']['lines'] + ENG['loc']['lib']['lines']:,} lines in hctf + lib"),
    ])


def tokens_table():
    rows = []
    for name, src in (("claude -p workers", W["total"]), ("orchestrator sessions", T["by_kind"].get("cli", {})),
                      ("orchestrator subagents", T["by_kind"].get("subagent", {})),
                      ("sdk sessions", T["by_kind"].get("sdk-cli", {}))):
        if not src:
            continue
        rows.append([name, compact(src["in_tok"]), compact(src["cache_write_tok"]), compact(src["cache_read_tok"]),
                     compact(src["out_tok"])])
    rows.append(["<strong>total</strong>", compact(TOK_IN), compact(TOK_WRITE), compact(TOK_CACHE), compact(TOK_OUT)])
    return table(["who", "fresh input", "cache writes", "cache reads", "output"], rows, summary=None)


def stage_table():
    names = {"solve": "solving (singles, live answers, answer-first)", "generalize": "generalize (fix a failed timed variant)",
             "duels": "duels (best-of-N racers)", "post-run": "post-run (ratchet, technique logs, speed-harden)",
             "prebuild": "prebuild (overnight breadth)", "other": "other"}
    tot = W["total"]["usd"]
    rows = []
    for k, v in sorted(W["by_stage"].items(), key=lambda kv: -kv[1]["usd"]):
        rows.append([names.get(k, k), f"{v['workers']:,.0f}", f"{v['turns']:,.0f}", f"{v['wall_s'] / 3600:,.1f} h",
                     f"${v['usd']:,.0f}", f"{v['usd'] / tot:.0%}"])
    return table(["stage", "workers", "turns", "worker time", "spend", "share"], rows, summary=None)


def day_table():
    k = {r["day"]: r for r in STATS["kpi"]["days"]}
    wd = W["by_day"]
    rows = []
    for d in range(1, 32):
        r, rk = RACE[d], RANKD[d]
        live = sum(wd.get(str(d), {}).get(f"usd_{g}", 0) for g in ("solve", "generalize", "duels"))
        titles = INV["per_day"][d - 1]["challenges"]
        kk = k.get(d, {})
        gen = kk.get("generalizes")
        rows.append([f"<strong>{d}</strong>", f"{INV['per_day'][d - 1]['modes']}",
                     f"T+{dur(our_day_finish(d))}{' *' if d in LATE else ' †' if d in PRE else ''}",
                     ordinal(r["our_day_rank"]) if r["our_day_rank"] else "-", ordinal(rk["rank_end"]),
                     f"${live:,.2f}" if live and d >= 9 else "-", "-" if gen is None else str(gen), E(NOTES[d])])
        del titles
    return table(["day", "modes", "cleared", "day rank", "overall", "worker $", "generalizes", "what happened"], rows,
                 cls="hc-days", summary=None)


def hof_tiles():
    tt, m = HOF["modes"]["time_trial"], HOF["modes"]["mastery"]
    return tiles([
        ("Time Trial board entries", f"{tt['entries']}", f"best rank {min(r['rank'] for r in tt['rows'])}, median {tt['median_rank']} of ~{tt['teams']}"),
        ("Mastery board entries", f"{m['entries']}", f"best rank {min(r['rank'] for r in m['rows'])}, median {m['median_rank']} of ~{m['teams']}"),
        ("largest timed board", f"{HOF['largest'][0]['answers']:,} answers", "one Mastery attempt (day 9 script)"),
    ], cls="hc-tiles-3")


def hof_table():
    rows = []
    for mode in ("time_trial", "mastery"):
        for r in HOF["modes"][mode]["rows"]:
            rows.append([f"{r['day']}", E(r["title"] or ""), "TT" if mode == "time_trial" else "Mastery",
                         f"{r['rank']} / {r['of']}", f"{r['ms'] / 1000:.2f}s", f"{r['leader_ms'] / 1000:.2f}s",
                         f"{r['answers'] or '-'}"])
    rows.sort(key=lambda x: (int(x[0]), x[2]))
    return table(["day", "challenge", "mode", "rank", "our time", "fastest", "answers"], rows)


def hb_chart():
    days = list(range(8, 32))
    vals = [HB["by_day"].get(str(d), 0) for d in days]
    return bars("hb", "Homebase VM hours per day", "VM hours per drop window.",
                f"Hours the organizer's Homebase VM was up, per drop window ({HB['vm_hours']:.0f} h, about "
                f"{HB['credits']:.0f} credits in total; a lower bound from the harness's own ledger).",
                days, vals, lambda v: f"{v:.1f} h", head=("day", "VM hours"), tick_every=4)


def cost_charts():
    days = list(range(9, 32))
    wd = W["by_day"]
    live = [sum(wd.get(str(d), {}).get(f"usd_{g}", 0) for g in ("solve", "generalize", "duels")) for d in days]
    night = [sum(wd.get(str(d), {}).get(f"usd_{g}", 0) for g in ("post-run", "prebuild", "other")) for d in days]
    a = bars("cost-live", "Worker spend on each day's challenges",
             "API-equivalent dollars for workers that solved, generalized or duelled on each day's challenges.",
             "Workers that solved, generalized or duelled on that day's challenges, including any re-runs "
             "(list-price equivalent from token counts). The tallest bar is day 30's hardened bonus crackme.", days, live,
             lambda v: f"${v:,.0f}", head=("day", "worker $"), tick_every=4)
    b = bars("cost-night", "Overnight learning spend, per day",
             "API-equivalent dollars for post-run and prebuild workers per drop window.",
             "Post-run (ratchet, technique logs, speed-harden) and prebuild (speculative breadth for tomorrow's "
             "unknowns) in each drop window. Same units as above, on its own scale.", days, night,
             lambda v: f"${v:,.0f}", head=("day", "overnight $"), tick_every=4)
    return a, b


def commits_chart():
    c = ENG["commits_by_date"]
    days = list(range(3, 32))
    vals = [c.get(f"2026-10-{d:02d}", 0) for d in days]
    return bars("commits", "Commits per day", "Harness repository commits per calendar day.",
                f"{ENG['commits']} commits across {ENG['branches']} branches between Oct "
                f"{int(ENG['first_commit'][-2:])} and Oct {int(ENG['last_commit'][-2:])}.",
                [f"{d}" for d in days], vals, lambda v: f"{v:.0f}", head=("date (Oct)", "commits"), tick_every=4)


def growth_chart():
    g = ENG["growth"]
    labels = [x["date"][-2:].lstrip("0") for x in g]
    vals = [x["py_bytes"] / 1024 / 1024 for x in g]
    return bars("growth", "Harness code size", "Python bytes in hctf and lib at the end of each commit day.",
                "Size of the Python in hctf/ and lib/ at the last commit of each day (MB). Much of lib/ is generated "
                "codec tables and decoders the overnight ratchet added.", labels, vals, lambda v: f"{v:.1f} MB",
                head=("date (Oct)", "MB"), tick_every=4)


def day_rank_chart():
    days = [d for d in range(1, 32) if RACE[d]["our_day_rank"]]
    vals = [RACE[d]["our_day_rank"] for d in days]
    hl = [i for i, v in enumerate(vals) if v <= 5]
    return bars("dayrank", "Our finishing position each day",
                "For each day, our position among teams that cleared that whole day, ordered by finish time.",
                "Our position in each day's race to clear the board (lower is better; red = top five). Late days "
                "rank low by construction.", [str(d) for d in days], vals, lambda v: ordinal(int(v)),
                hl=hl, head=("day", "day rank"), tick_every=5, yfmt=lambda v: f"{v:.0f}")


# ---------------------------------------------------------------- write everything
def main():
    a, b = cost_charts()
    parts = {
        "rank": chart_rank_month(), "finish": chart_daily_finish(), "lanes": chart_lane_heat(), "wins": dumbbells(),
        "arch": architecture(), "chain": chain_states(), "system": system_loop(), "tiles": headline_tiles(), "tokens": tokens_table(), "stages": stage_table(),
        "days": day_table(), "hof-tiles": hof_tiles(), "hof-table": hof_table(), "hb": hb_chart(), "cost-live": a,
        "cost-night": b, "commits": commits_chart(), "growth": growth_chart(), "dayrank": day_rank_chart(),
    }
    for k, v in parts.items():
        write(k, v)
    tabs = [
        ("overview", "Overview", ["tiles", "finish"]),
        ("placement", "Placement", ["rank", "dayrank"]),
        ("speed", "Speed", ["lanes", "wins"]),
        ("days", "Day by day", ["days"]),
        ("cost", "Cost & tokens", ["cost-live", "cost-night", "stages", "tokens"]),
        ("engineering", "Engineering", ["commits", "growth", "hb"]),
        ("hof", "Hall of Fame", ["hof-tiles", "hof-table"]),
    ]
    nav = "".join(f'<a class="hc-tab" href="#{tid}" data-tab="{tid}">{E(lab)}</a>' for tid, lab, _ in tabs)
    panels = []
    for tid, lab, names in tabs:
        inner = "\n".join('{{ partial "hctf2026/' + n + '.html" . }}' for n in names)
        panels.append(f'<section class="hc-panel" id="{tid}" data-panel="{tid}"><h2 class="hc-panel-h">{E(lab)}</h2>\n{inner}\n</section>')
    snap = STATS["generated"][:10]
    write("dashboard", f'<nav class="hc-tabs" aria-label="Dashboard sections">{nav}</nav>\n' + "\n".join(panels) +
          f'\n<p class="hc-foot">Snapshot {E(snap)} · official scoreboard, Game Master list, public speed board and '
          f'the harness\'s own logs · no live refresh</p>')
    print(f"wrote {len(parts) + 1} partials to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
