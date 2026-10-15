"""Nightly offline training on previous days (post-run, after the ratchet + speed-harden, before the prebuild).

Discord tip (2026-10-15): "train your bots on previous days' challenges -- they build off the previous day". Every
lane adds one concept a day and the timed modes compound earlier days (D1-D15 audit), so the solver tomorrow starts
from (cumulative lanes copy it; every lane races it) must still answer EVERY earlier day and survive answer-invariant
variation. Per lane, off the clock:
  1. replay ALL earlier days' GM-verified cases of the lane through day N's solver (hctf.compound, no timebox,
     no per-day sampling) -> hard misses adopted as `compound-dKK-*` regression cases;
  2. run the mutation probe (hctf.mutate: renamed / reordered / subset / unknown-field / mastery-shape variants of
     the solver's own cases) -> HARD failures adopted as `mutation-*` cases;
  3. any adopted case -> one transactional generalize (the normal worker + regression gate; kept only if every case
     passes), up to TRAIN_ROUNDS rounds while misses remain and the deadline (next drop - margin) allows.
The solver code stays the LLM worker's own output; nothing here answers a field. Writes only under challenges/.
"""
import json
import time
from pathlib import Path

from . import compound, paths

ROUNDS = 2


def day_solvers(day):
    """[(base id, lane, solver dir)] of every lane solved on `day`."""
    out = []
    for m in sorted(paths.CHALLENGES.glob(f"day{int(day):02d}/*/meta.json")):
        try:
            meta = json.loads(m.read_text())
        except (OSError, ValueError):
            continue
        sdir = m.parent / "solver"
        if (sdir / "solve.py").exists() and meta.get("base"):
            out.append((meta["base"], meta.get("lane") or "", sdir))
    return out


def assess(sdir, mutation=True, timeout=60):
    """-> {"compound": [results], "hard": [hard-miss results], "mut_text", "mut_hard": [case dirs]} (no edits)."""
    from . import orchestrate
    res = compound.check(sdir, per_day=None, timeout=timeout)
    out = {"compound": res, "hard": compound.hard_misses(res), "mut_text": "", "mut_hard": []}
    if mutation:
        mc = sorted((Path(sdir).parent / "mastery").glob("contract.json"))
        text, hard, _ = orchestrate.mutation_probe(sdir, mc[0] if mc else None, timeout=180)
        out["mut_text"], out["mut_hard"] = text, hard
    return out


def _line(a):
    ok = len(a["compound"]) - len(compound.misses(a["compound"]))
    return (f"{ok}/{len(a['compound'])} earlier-day cases right, {len(a['hard'])} hard miss(es), "
            f"{len(a['mut_hard'])} hard mutation failure(s)")


def run(day, log=print, rounds=None, mutation=True, dry_run=False, deadline=None, lanes=None):
    """Train every lane solver of `day`. Returns {base: {"before": str, "after": str|None, "generalized": n}}."""
    from . import orchestrate, prebuild
    rounds = ROUNDS if rounds is None else rounds
    if deadline is None:
        deadline = prebuild.default_deadline().timestamp()
    report = {}
    for base, lane, sdir in day_solvers(day):
        if lanes and lane not in lanes:
            continue
        t0 = time.time()
        a = assess(sdir, mutation=mutation)
        before = _line(a)
        log(f"[train] {base}: {before} ({time.time() - t0:.0f}s)")
        rep = {"before": before, "after": None, "generalized": 0}
        report[base] = rep
        if dry_run:
            for r in a["hard"][:6]:
                log(f"[train]   miss d{r['day']:02d} {r['case']}: {r['correct']}/{r['expected']} verified"
                    + (f" ERROR {r['error'][:80]}" if r["error"] else ""))
            continue
        for rnd in range(rounds):
            if not (a["hard"] or a["mut_hard"]):
                break
            if time.time() > deadline:
                log(f"[train] {base}: deadline reached, stopping before round {rnd + 1}")
                break
            diag = {}
            if a["hard"]:
                n = compound.adopt(sdir, a["compound"], limit=12)
                diag["compound_pre"] = compound.summary(a["compound"])
                log(f"[train] {base}: round {rnd + 1}: {n} earlier-day case(s) adopted as compound-dKK-* cases")
            if a["mut_hard"]:
                gov = orchestrate.Governor()
                chain = orchestrate.chain_for(base, orchestrate.Pools(1, 0, gov), gov)
                n = chain._adopt_mutation_cases(a["mut_hard"])
                diag["mutation_pre"] = a["mut_text"]
                log(f"[train] {base}: round {rnd + 1}: {n} mutation case(s) adopted")
            gov = orchestrate.Governor()
            orchestrate.chain_for(base, orchestrate.Pools(1, 0, gov), gov).generalize(base, wrong=None, fixed=None,
                                                                                     diag=diag)
            rep["generalized"] += 1
            a = assess(sdir, mutation=mutation)
            rep["after"] = _line(a)
            log(f"[train] {base}: after round {rnd + 1}: {rep['after']}")
    return report


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="offline training of a day's lane solvers on every earlier day")
    ap.add_argument("--day", type=int, required=True)
    ap.add_argument("--lane", action="append", help="limit to these lanes (repeatable)")
    ap.add_argument("--rounds", type=int, default=ROUNDS)
    ap.add_argument("--no-mutation", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="assess only (no case adoption, no generalize)")
    a = ap.parse_args(argv)
    rep = run(a.day, rounds=a.rounds, mutation=not a.no_mutation, dry_run=a.dry_run, lanes=a.lane)
    return 0 if all(r["after"] is None or "0 hard miss(es)" in r["after"] for r in rep.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
