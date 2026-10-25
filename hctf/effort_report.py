"""Effort A/B report: the same day played by two harness copies (week of 2026-10-16: main at `--effort xhigh`, alt at
`high`), side by side per lane -- time to CORRECT per mode, LLM worker wall time / turns / seconds per turn / output
tokens per stage, and wrong submits per Single. Read-only; works on either copy's .run/dayNN.log + metrics.tsv.

    hctf effort-report --day 16                       (main + ~/huntress-2026-rehearsal when present)
    hctf effort-report --day 16 --root ~/huntress-2026
"""
import json
import re
from collections import defaultdict
from pathlib import Path

from . import paths
from .timeline import lane_label, timed_passed

LINE = re.compile(r"^(\d\d):(\d\d):(\d\d) \[([^\]]+)\] (.*)$")
MODES = ("single_solve", "time_trial", "mastery")
SHORT = {"single_solve": "single", "time_trial": "TT", "mastery": "Mastery"}


def _secs(h, m, s):
    return int(h) * 3600 + int(m) * 60 + int(s)


def _lane(base):
    return lane_label(base)   # `web:<slug>` per web chain (D24 plan #15), the GM lane otherwise


def _log(root, day):
    p = Path(root) / ".run" / f"day{int(day):02d}.log"
    return p.read_text(errors="replace").splitlines() if p.exists() else []


def effort(root, day):
    for ln in _log(root, day)[:40]:
        m = re.search(r"\[effort\] global=(\w+)", ln)
        if m:
            return m.group(1)
    return "?"


def solves(root, day):
    """{(lane, mode): seconds after the release line} for the first CORRECT of each mode."""
    t0, out = None, {}
    for ln in _log(root, day):
        m = LINE.match(ln)
        if not m:
            if t0 is None and ("released" in ln or re.search(r"\d+ chains \(", ln)):   # replays / no --wait: run start
                mm = re.match(r"^(\d\d):(\d\d):(\d\d)", ln)
                t0 = _secs(*mm.groups()) if mm else None
            continue
        t = _secs(*m.groups()[:3])
        tag, msg = m.group(4), m.group(5)
        if t0 is None and "released" in msg:
            t0 = t
        base, _, mode = tag.partition("/")
        mode = mode or "single_solve"
        hit = (timed_passed(msg)
               or (mode == "single_solve" and ("reuse race WON" in msg or msg.startswith("after worker: stopped at CORRECT"))))
        if hit and t0 is not None and (_lane(base), mode) not in out:
            out[(_lane(base), mode)] = t - t0
    return out


def _window(root, day):
    """(first, last) HH:MM:SS seconds of the copy's day log (both arms of an A/B on ONE copy share metrics.tsv)."""
    ts = [_secs(*m.groups()) for ln in _log(root, day) for m in [re.match(r"^(\d\d):(\d\d):(\d\d)", ln)] if m]
    return (min(ts), max(ts)) if ts else (None, None)


def worker_stats(root, day):
    """{(lane, stage): {n, wall, turns, out_tok}} from the copy's metrics.tsv rows of that day, inside its log window."""
    p = Path(root) / ".run" / "metrics.tsv"
    agg = defaultdict(lambda: {"n": 0, "wall": 0.0, "turns": 0.0, "out_tok": 0.0})
    if not p.exists():
        return agg
    lines = p.read_text(errors="replace").splitlines()
    cols = lines[0].split("\t") if lines else []
    tag = f"-day-{int(day):02d}"
    lo, hi = _window(root, day)
    for ln in lines[1:]:
        r = dict(zip(cols, ln.split("\t")))
        if tag not in (r.get("base") or "") or r.get("stage") in ("prebuild", "ratchet", "ratchet_log"):
            continue
        m = re.search(r"T(\d\d):(\d\d):(\d\d)", r.get("ts") or "")
        if lo is not None and m and not (lo - 60 <= _secs(*m.groups()) <= hi + 60):
            continue
        a = agg[(_lane(r["base"]) if r.get("base") else r.get("lane"), r.get("stage"))]
        a["n"] += 1
        for k, col in (("wall", "wall_s"), ("turns", "turns"), ("out_tok", "out_tok")):
            try:
                a[k] += float(r.get(col) or 0)
            except ValueError:
                pass
    return agg


def wrong_submits(root, day):
    """{lane: incorrect worker submits on the Single} (harness probes / race / alternates excluded)."""
    out = {}
    for sj in sorted((Path(root) / "challenges" / f"day{int(day):02d}").glob("*/single_solve/submissions.jsonl")):
        try:
            meta = json.loads((sj.parent.parent / "meta.json").read_text())
            lane = _lane(meta["base"]) if meta.get("base") else meta.get("lane")
        except (OSError, ValueError):
            continue
        n = 0
        for ln in sj.read_text().splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("kind") == "incorrect" and not r.get("probe") and not r.get("harness"):
                n += 1
        out[lane] = n
    return out


def _fmt(v):
    return "-" if v is None else (f"{v // 60}:{v % 60:02d}" if isinstance(v, int) else f"{v:.0f}")


def report(day, roots=None):
    roots = [Path(r) for r in (roots or [paths.ROOT] + ([Path.home() / "huntress-2026-rehearsal"]
                                                         if (Path.home() / "huntress-2026-rehearsal").exists() else []))]
    roots = [r for r in roots if _log(r, day)]
    if not roots:
        return f"no day{int(day):02d}.log under {', '.join(map(str, roots or [paths.ROOT]))}"
    names = [f"{r.name}({effort(r, day)})" for r in roots]
    sv = [solves(r, day) for r in roots]
    ws = [worker_stats(r, day) for r in roots]
    wr = [wrong_submits(r, day) for r in roots]
    lanes = sorted({k[0] for s in sv for k in s} | {k[0] for w in ws for k in w})
    out = [f"== effort report day {int(day):02d}: " + "  vs  ".join(names) + " ==", "", "time to CORRECT (m:ss after release)"]
    out.append("lane".ljust(28) + "".join(f"{SHORT[m]:>18}" for m in MODES) + "   (per copy: " + " / ".join(names) + ")")
    for lane in lanes:
        cells = []
        for m in MODES:
            cells.append(" / ".join(_fmt(s.get((lane, m))) for s in sv))
        out.append(lane.ljust(28) + "".join(f"{c:>18}" for c in cells))
    out += ["", "LLM workers per stage: n, wall s, turns, s/turn, out tok (per copy)"]
    for lane in lanes:
        for st in sorted({k[1] for w in ws for k in w if k[0] == lane}):
            parts = []
            for w in ws:
                a = w.get((lane, st))
                if not a or not a["n"]:
                    parts.append("-")
                    continue
                spt = a["wall"] / a["turns"] if a["turns"] else 0
                parts.append(f"{a['n']}x {a['wall']:.0f}s {a['turns']:.0f}t {spt:.1f}s/t {a['out_tok']:.0f}tok")
            out.append(f"  {lane:<26} {st:<16} " + "  |  ".join(parts))
    out += ["", "wrong Single submits: " + "  ".join(
        f"{lane}={'/'.join(str(w.get(lane, '-')) for w in wr)}" for lane in lanes)]
    return "\n".join(out)
