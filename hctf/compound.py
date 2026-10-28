"""Compounding check: does TODAY's solver still answer EARLIER days' concepts of its lane?

Organizer signal (Day 8): Mastery should compound -- today's new concept plus at least one concept from days past.
So far only warmups Mastery really mixed earlier days in; binary/script carry earlier days inside the Single, metadata
and mobile barely. When Mastery starts mixing earlier concepts in every lane, a solver built only for today's Single
fails Mastery (failed attempt + evidence pull + generalize). This replays the solver on every earlier day's GM-verified
cases of the same lane (their own contracts, unchanged) -- local, no GM -- and reports what it lost.

Used by the orchestrator as a pre-attempt probe (orchestrate.Chain._compound_pre) and by `hctf compound-check`.
"""
import json
import os
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
    D1/D2 ids before the D3 `d01_*` rename), not a lost concept. A web LIVE miss is always hard: a web target has the
    same `proof-N` id every day, so an empty answer there IS the lost concept."""
    return [r for r in misses(results) if r["error"] or r["answered"] > 0 or r.get("live")]


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
        dst = Path(sdir) / "cases" / (f"compound-d{r['day']:02d}-{src.name}" if not r.get("live")
                                      else f"compound-live-{src.name}")
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        n += 1
    return n


# ------------------------------------------------------------------ web: live compounding check
# A web case can't be replayed once its attempt is finished (target 410), so earlier days' web cases tell nothing.
# Instead: "Play again" each earlier web challenge's Time Trial (GM retry -> a fresh single-bug target, ~18 s; probe
# 2026-10-21: TT 5/5 by each day's own solver) and run today's solver on it. Expected = that day's OWN solver on the same
# target. Nothing is submitted during a check: every touched attempt stays OPEN (a miss's target is replayed by the
# generalize as a `compound-live-*` case marked live_compound.json; a second web chain's check of the same earlier TT
# gets the same open attempt back from `retry` -- a submit there killed the first chain's miss case, 10-21 probe) and is
# recorded in .run/webcmp/touched.jsonl; web_live_restore() re-solves them with each day's own solver once the run's
# web chains are done. D20 rerun: D02/D03/D04 Mastery each missed Target 1 = an earlier day's bug (backup exposure,
# IDOR) while their TT solvers were fine; the live check reproduced exactly those misses.


def _empty(v):
    """solvers.run_solver str()s every value: a solver's null comes back as 'None'."""
    return v in (None, "", "None", "null")


def web_earlier(sdir):
    """[(day, chal_dir, time_trial id)] of every earlier web challenge with a solver (folder day < this solver's)."""
    chal = Path(sdir).parent
    lane, today = _lane(chal), _day(chal)
    out = []
    for other in sorted(paths.CHALLENGES.glob("day*/*/meta.json")):
        od = other.parent
        if od == chal or _day(od) >= today or _lane(od) != lane or not (od / "solver" / "solve.py").exists():
            continue
        try:
            tt = (json.loads(other.read_text()).get("ids") or {}).get("time_trial")
        except (OSError, ValueError):
            tt = None
        if tt:
            out.append((_day(od), od, tt))
    return out


def _live_lock(tt):
    """One live check per earlier Time Trial at a time (two web chains of a day probe the same earlier challenges; one's
    submit would 410 the other's target)."""
    import fcntl
    p = paths.LOCKS / f"web-compound-{tt.replace('/', '_')}.lock"
    p.parent.mkdir(parents=True, exist_ok=True)
    f = open(p, "a+")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


FOREIGN_PROMPT = os.environ.get("HCTF_WEB_LIVE_FOREIGN_PROMPT", "1") != "0"


def _today_prompt(sdir):
    """The prompt today's chain runs under (Mastery's, else the Single's) -- what a compounded target is solved with."""
    for mode in ("mastery", "single_solve"):
        try:
            p = json.loads((Path(sdir).parent / mode / "contract.json").read_text()).get("prompt")
        except (OSError, ValueError, AttributeError):
            continue
        if p:
            return p
    return None


def web_live_check(sdir, timeout=40, parallel=6, deadline=None, log=None):
    """Today's web solver vs a fresh target of every earlier web challenge's Time Trial. Same result dicts as check()
    (+ live=True, cid, attempt); a miss's `path` is a case dir under .run/webcmp/ (contract = the live attempt,
    expected = the earlier day's own solver on it). Skips (no result) when the target never comes up, the earlier solver
    answers nothing, or the GM refuses the re-roll."""
    import tempfile
    from . import cli, webtarget
    sdir = Path(sdir)
    log = log or (lambda m: None)
    run_root = ROOT / ".run" / "webcmp"
    run_root.mkdir(parents=True, exist_ok=True)
    today_prompt = _today_prompt(sdir)

    def one(item):
        day, od, tt = item
        if deadline and time.time() > deadline:
            return None
        lock = _live_lock(tt)
        try:
            with cli.quiet():
                env = cli.call(tt, "retry", tt)
            body = env.get("body") if isinstance(env.get("body"), dict) else {}
            if not webtarget.ready(body):
                body = webtarget.wait_ready(tt, body, log=lambda m: None, wait=120)
            if not webtarget.ready(body):
                log(f"web live check: {tt} target not up ({body.get('result') or body.get('error')}) -- skipped")
                return None
            empty = Path(tempfile.mkdtemp(prefix="webcmp-art-", dir=str(run_root)))
            exp, err0, _ = solvers.run_solver(od / "solver", body, empty, timeout)
            exp = {k: v for k, v in (exp or {}).items() if not _empty(v)}
            if err0 or not exp:
                log(f"web live check: {tt} own solver gave nothing ({err0 or 'empty'}) -- skipped")
                return None
            # in a compounded Mastery the earlier class's target arrives under TODAY's prompt (D27/D28: the day-20 LFI
            # solver found the proof only when its own prompt named the path) -> today's solver sees today's prompt
            if FOREIGN_PROMPT and today_prompt:
                body = dict(body, prompt=today_prompt)
            got, err, dt = solvers.run_solver(sdir, body, empty, timeout)
            wrong = {k: {"expected": v, "got": got.get(k)} for k, v in exp.items() if got.get(k) != v}
            ids = body.get("answer_ids") or list(exp)
            att = cli.attempt_id(body)
            res = {"day": day, "case": f"{od.name}-{str(att)[:8]}", "path": "", "expected": len(exp),
                   "correct": len(exp) - len(wrong), "answered": sum(1 for i in ids if not _empty(got.get(i))),
                   "total": len(ids), "wrong": wrong, "error": err, "seconds": round(dt, 2), "live": True, "cid": tt,
                   "attempt": att}
            _touched(tt, od, att)
            if not wrong and not err:
                return res
            case = run_root / f"{od.name}-{str(att)[:8]}"
            if case.exists():
                import shutil
                shutil.rmtree(case)
            (case / "artifacts").mkdir(parents=True)
            (case / "contract.json").write_text(json.dumps(body, indent=2))
            (case / "expected.json").write_text(json.dumps(exp, indent=2))
            (case / "live_compound.json").write_text(json.dumps({"cid": tt, "attempt": att, "day": day,
                                                                  "created": time.time(), "restored": False}))
            res["path"] = str(case.relative_to(ROOT))
            return res
        except Exception as e:  # noqa: BLE001 - one earlier challenge never sinks the probe
            log(f"web live check: {tt} note: {str(e)[:160]}")
            return None
        finally:
            lock.close()

    items = web_earlier(sdir)
    with _BgExecutor(max_workers=max(1, parallel)) as ex:
        return [r for r in ex.map(one, items) if r]


def _rel_root(p):
    """`p` relative to the project root, else absolute (a challenges tree outside it: tests, replay copies)."""
    try:
        return str(Path(p).resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(Path(p).resolve())


def _touched(tt, od, att):
    """Record an earlier Time Trial attempt a live check left open (re-solved by web_live_restore)."""
    with open(ROOT / ".run" / "webcmp" / "touched.jsonl", "a") as f:
        f.write(json.dumps({"cid": tt, "dir": _rel_root(od), "attempt": att, "t": time.time()}) + "\n")


def web_live_restore(log=None):
    """Once the run's web chains are done: re-solve every earlier Time Trial a live check touched that is still open
    (status not CORRECT and its target up) with that day's OWN solver on the CURRENT attempt, and mark every
    `compound-live-*` case restored (stale for every later replay). Returns the number of Time Trials re-solved."""
    import tempfile
    from . import cli, webtarget
    log = log or (lambda m: None)
    reg = ROOT / ".run" / "webcmp" / "touched.jsonl"
    seen, n = {}, 0
    try:
        for ln in reg.read_text().splitlines():
            try:
                r = json.loads(ln)
                seen[r["cid"]] = r
            except (ValueError, KeyError):
                continue
    except OSError:
        pass
    for tt, r in seen.items():
        try:
            with cli.quiet():
                body = cli.call(tt, "status", tt).get("body") or {}
            if str(body.get("result", "")).upper() == "CORRECT" or not webtarget.ready(body):
                continue
            empty = Path(tempfile.mkdtemp(prefix="webcmp-art-", dir=str(ROOT / ".run" / "webcmp")))
            ans, err, _ = solvers.run_solver(ROOT / r["dir"] / "solver", body, empty, 40)
            ans = {k: v for k, v in (ans or {}).items() if not _empty(v)}
            if err or not ans:
                log(f"web live check: {tt} left open (its own solver gave nothing)")
                continue
            with cli.quiet():
                sub = cli.call(tt, "submit", tt, json.dumps(ans)).get("body") or {}
            n += 1
            log(f"web live check: re-solved {tt} ({sub.get('result') or sub.get('error')})")
        except Exception as e:  # noqa: BLE001
            log(f"web live check: restore note {tt}: {str(e)[:120]}")
    try:
        reg.write_text("")
    except OSError:
        pass
    for marker in paths.CHALLENGES.glob("day*/*/solver/cases/compound-live-*/live_compound.json"):
        try:
            m = json.loads(marker.read_text())
            m["restored"] = True
            marker.write_text(json.dumps(m))
        except (OSError, ValueError):
            continue
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
