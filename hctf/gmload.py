"""GM load / rate-limit report for one day (`hctf cost --day N` appends it).

The GM rate limit is shared by every call on our token (reviewer: a contended bucket banked 128 of 1506 ids, the same
run alone 1506 of 1506). Before building a host-wide limiter, measure: where did 429s / unjudged replies land, from
which caller, how many seconds after the drop?

Sources (all already written by the harness):
- challenges/dayNN/*/*/log.jsonl   cli.call rows (worker + race + chain GM calls): http, retries, slept
- challenges/dayNN/*/*/last_timed.json, attempts/*/result.json   hb_timed results: unjudged, unjudged_resends,
  gm_rate_limited, reconfirms
- .run/dayNN.log                    orchestrator lines: `result: error:rate`, retry_skipped_banked
"""
import datetime as dt
import json
import re
from collections import Counter

from . import paths

ROOT = paths.ROOT


def _epoch(row):
    if isinstance(row.get("t"), (int, float)):
        return float(row["t"])
    try:
        return dt.datetime.strptime(row["ts"], "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
    except (KeyError, TypeError, ValueError):
        return None


def _rows(path):
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def _limited(row):
    body = row.get("body") if isinstance(row.get("body"), dict) else {}
    return (row.get("http") == 429 or (row.get("retries") or 0) > 0
            or "rate_limited" in str(body.get("error") or "") or "rate_limited" in str(row.get("text") or ""))


def report(day):
    dd = ROOT / "challenges" / f"day{int(day):02d}"
    if not dd.is_dir():
        return f"gm429: no challenges/day{int(day):02d}"
    calls, limited, slept, by_bucket = Counter(), Counter(), Counter(), Counter()
    t_first = None
    rows = []
    for lp in sorted(dd.glob("*/*/log.jsonl")):
        caller = f"{lp.parent.parent.name.split('-')[0]}/{lp.parent.name}"
        for r in _rows(lp):
            t = _epoch(r)
            rows.append((t, caller, r))
            if r.get("op") == "start" and t is not None:
                t_first = t if t_first is None else min(t_first, t)
    for t, caller, r in rows:
        key = (caller, r.get("op"))
        calls[key] += 1
        if _limited(r):
            limited[key] += 1
            slept[key] += float(r.get("slept") or 0)
            if t is not None and t_first is not None:
                by_bucket[int((t - t_first) // 30) * 30] += 1
    timed = Counter()
    for rp in list(dd.glob("*/*/last_timed.json")) + list(dd.glob("*/*/attempts/*/result.json")):
        try:
            res = json.loads(rp.read_text())
        except (OSError, ValueError):
            continue
        timed["unjudged"] += len(res.get("unjudged") or [])
        timed["unjudged_resends"] += int(res.get("unjudged_resends") or 0)
        timed["gm_rate_limited"] += int(bool(res.get("gm_rate_limited")))
        timed["reconfirms"] += int(res.get("reconfirms") or 0)
        timed["resumed_banked"] += int(bool(res.get("resumed_banked")))
    for sp in dd.glob("*/*/submissions.jsonl"):   # cli.submit rows: kind error/unknown = a submit the GM never judged
        for r in _rows(sp):
            if r.get("kind") not in ("correct", "accepted", "incorrect", "expired"):
                timed["unjudged cli submits"] += 1
    logp = ROOT / ".run" / f"day{int(day):02d}.log"
    try:
        text = logp.read_text(errors="replace")
    except OSError:
        text = ""
    timed["error:rate lines"] = len(re.findall(r"result: error:rate", text))
    timed["retry_skipped_banked"] = text.count("retry_skipped_banked")

    lines = [f"== gm429 day {int(day)}: {sum(limited.values())} rate-limited of {sum(calls.values())} logged GM calls "
             f"({sum(slept.values()):.0f}s backoff) =="]
    for key, n in sorted(limited.items(), key=lambda kv: -kv[1])[:15]:
        lines.append(f"  {key[0]:<34} {str(key[1]):<10} {n:>4}/{calls[key]:<5} slept {slept[key]:.0f}s")
    if by_bucket:
        lines.append("  by 30 s bucket from the first start: "
                     + ", ".join(f"T+{b}s:{n}" for b, n in sorted(by_bucket.items())))
    lines.append("  timed attempts: " + ", ".join(f"{k} {v}" for k, v in timed.items()))
    return "\n".join(lines)
