"""Compounding check: does TODAY's solver still answer EARLIER days' concepts of its lane?

Organizer signal (Day 8): Mastery should compound -- today's new concept plus at least one concept from days past.
So far only warmups Mastery really mixed earlier days in; binary/script carry earlier days inside the Single, metadata
and mobile barely. When Mastery starts mixing earlier concepts in every lane, a solver built only for today's Single
fails Mastery (failed attempt + evidence pull + generalize). This replays the solver on every earlier day's GM-verified
cases of the same lane (their own contracts, unchanged) -- local, no GM -- and reports what it lost.

Used by the orchestrator as a pre-attempt probe (orchestrate.Chain._compound_pre) and by `hctf compound-check`.
"""
import json
import time
from pathlib import Path

from .procgov import Executor as _BgExecutor
from . import paths, solvers

ROOT = paths.ROOT
# Cases whose expected answers the GM verified (synthetic-*/mutation-*/family-*/compound-* are ours, never replayed).
VERIFIED_PREFIXES = ("single_solve", "auto-mastery-", "auto-time_trial-", "variant-mastery-", "variant-time_trial-")


def _lane(chal_dir):
    try:
        return json.loads((chal_dir / "meta.json").read_text()).get("lane")
    except (OSError, ValueError):
        return None


def _day(chal_dir):
    try:
        return int(chal_dir.parent.name[3:])
    except ValueError:
        return -1


def earlier_cases(sdir, per_day=3):
    """[(day, case_dir)] of every EARLIER day of this solver's lane: the Single case + the newest GM-verified Time
    Trial and Mastery cases (per_day caps the count per day). per_day=None: EVERY GM-verified case (hctf.train)."""
    chal = Path(sdir).parent
    lane, today = _lane(chal), _day(chal)
    out = []
    for other in sorted(paths.CHALLENGES.glob("day*/*/meta.json")):
        od = other.parent
        if od == chal or _day(od) >= today or _lane(od) != lane:
            continue
        cases = [c for c in (od / "solver" / "cases").glob("*/") if c.name.startswith(VERIFIED_PREFIXES)
                 and (c / "expected.json").exists() and (c / "contract.json").exists()]
        single = [c for c in cases if c.name == "single_solve"]
        rest = sorted((c for c in cases if c.name != "single_solve"), key=lambda c: c.stat().st_mtime, reverse=True)
        picked, kinds = list(single), set()
        if per_day is None:
            out += [(_day(od), c) for c in single + rest]
            continue
        for c in rest:
            kind = "mastery" if "mastery" in c.name else "time_trial"
            if kind not in kinds:
                picked.append(c)
                kinds.add(kind)
        out += [(_day(od), c) for c in picked[:per_day]]
    return out


def check(sdir, per_day=3, timeout=30, parallel=6, deadline=None):
    """Run the solver on each earlier-day case. Returns [{day, case, path, expected, correct, answered, total, wrong,
    error, seconds}]. `deadline` (epoch s): cases not started by then are skipped (bounded probe)."""
    sdir = Path(sdir)

    def one(item):
        day, case = item
        if deadline and time.time() > deadline:
            return None
        contract = json.loads((case / "contract.json").read_text())
        expected = json.loads((case / "expected.json").read_text())
        got, err, dt = solvers.run_solver(sdir, contract, case / "artifacts", timeout)
        wrong = {k: {"expected": v, "got": got.get(k)} for k, v in expected.items() if got.get(k) != v}
        ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions") or [] if q.get("id")]
        return {"day": day, "case": case.name, "path": str(case.relative_to(ROOT)), "expected": len(expected),
                "correct": len(expected) - len(wrong), "answered": sum(1 for i in ids if got.get(i) not in (None, "")),
                "total": len(ids), "wrong": wrong, "error": err, "seconds": round(dt, 2)}

    items = earlier_cases(sdir, per_day)
    with _BgExecutor(max_workers=max(1, parallel)) as ex:
        return [r for r in ex.map(one, items) if r]


def misses(results):
    """Cases the solver no longer gets fully right (crash, wrong or unanswered verified fields)."""
    return [r for r in results if r["error"] or r["correct"] < r["expected"]]


def hard_misses(results):
    """Misses worth a pre-attempt generalize: a crash, or verified fields the solver answers WRONG/empty while it does
    answer the case. A case it answers nothing for at all is soft: an earlier day's retired answer-id scheme (binary
    D1/D2 ids before the D3 `d01_*` rename), not a lost concept."""
    return [r for r in misses(results) if r["error"] or r["answered"] > 0]


def summary(results, limit=12):
    """Short text for logs / the generalize prompt."""
    bad = hard_misses(results)
    if not bad:
        return ""
    lines = []
    for r in bad[:limit]:
        if r["error"]:
            why = f"crashed: {r['error'][:160]}"
        else:
            sample = "; ".join(f"{k} expected {v['expected']!r} got {v['got']!r}" for k, v in list(r["wrong"].items())[:3])
            why = f"{r['correct']}/{r['expected']} verified fields right ({sample})"
        lines.append(f"Day {r['day']} `{r['path']}`: {why}")
    return "\n".join(lines)


def adopt(sdir, results, limit=6):
    """Copy missed earlier-day cases into this solver's cases/ as `compound-dKK-<case>` regression cases (same bytes,
    contract and GM-verified expected answers). Returns the number adopted."""
    import shutil
    n = 0
    for r in hard_misses(results)[:limit]:
        src = ROOT / r["path"]
        dst = Path(sdir) / "cases" / f"compound-d{r['day']:02d}-{src.name}"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        n += 1
    return n


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="replay earlier days' verified cases through today's solver(s)")
    ap.add_argument("id", nargs="?", help="challenge id (any mode) -- its lane's solver")
    ap.add_argument("--day", type=int, help="every lane's solver of this day")
    ap.add_argument("--per-day", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.id:
        sdirs = [paths.solver_dir(paths.base_id(a.id))]
    elif a.day:
        sdirs = sorted(p.parent for p in paths.CHALLENGES.glob(f"day{a.day:02d}/*/solver/solve.py"))
    else:
        ap.error("give a challenge id or --day N")
    report = {}
    for sd in sdirs:
        res = check(sd, per_day=a.per_day)
        report[str(sd.relative_to(ROOT))] = res
        if not a.json:
            ok = len(res) - len(misses(res))
            print(f"{sd.parent.relative_to(ROOT)}: {ok}/{len(res)} earlier-day cases fully right")
            for r in res:
                flag = ("ok  " if not (r["error"] or r["correct"] < r["expected"])
                        else "MISS" if (r["error"] or r["answered"]) else "soft")
                print(f"  {flag} d{r['day']:02d} {r['case']:<28} {r['correct']}/{r['expected']} verified, "
                      f"answered {r['answered']}/{r['total']}, {r['seconds']}s"
                      + (f"  ERROR {r['error'][:100]}" if r["error"] else ""))
    if a.json:
        print(json.dumps(report, indent=1, default=str))
    return 0 if all(not hard_misses(v) for v in report.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
