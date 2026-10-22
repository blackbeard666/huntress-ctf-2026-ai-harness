"""B3: off-peak hardening for the generic web solver (lib.web / challenges/_lane/web/solver).

Web can't be hardened offline (a finished target 410s, so static cases tell nothing), but each earlier web challenge's
Time Trial is a free, unlimited practice target: GM `retry` hands back a fresh single-bug target in ~18 s. For every
web challenge with a solver, this provisions that fresh target and runs the GENERIC solver on it; a class the generic
solver can't prove is reported (and, with --fix, flagged for a handler in lib/web/handlers). Submits NOTHING -- touched
attempts stay open and are re-solved by compound.web_live_restore afterwards. Run off-peak so the generic solver is
first-try-correct at the drop (no drop-time generalize).

    python -m hctf.webharden [--fix] [--timeout 40] [--solver <dir>]

Needs GM access (pairing token). LLM-first: --fix does not re-implement anything; it names the missing class so the
run's generalize/ratchet machinery folds a verified handler back into lib/web/handlers.
"""
import argparse
import json
import re
import tempfile
import time
from pathlib import Path

from . import cli, compound, paths, solvers, webtarget

GENERIC = paths.LANE_SOLVERS / "web" / "solver"
_PROOF = re.compile(r"proof_[0-9A-Za-z]{8,}")


def web_challenges_with_solver(modes=("time_trial", "mastery")):
    """[(day, chal_dir, mode, mode_id)] for every web challenge with a solver, for each of `modes` that has an id.
    Mastery is included by default (Day-21 showed the generic solver missed a field on the MASTERY multi-target
    variant while its TT was fine): hardening must exercise the mastery path, not just the single-bug TT."""
    out = []
    for meta in sorted(paths.CHALLENGES.glob("day*/web-*/meta.json")):
        od = meta.parent
        if not (od / "solver" / "solve.py").exists():
            continue
        try:
            ids = (json.loads(meta.read_text()).get("ids") or {})
        except (OSError, ValueError):
            ids = {}
        for mode in modes:
            if ids.get(mode):
                out.append((compound._day(od), od, mode, ids[mode]))
    return out


def check_solver(tt, sdir, timeout=40, log=print):
    """Provision a fresh Time Trial target for `tt` and run `sdir`'s solver on it. Returns
    (proofs, total, seconds) or None when the target never came up. Submits nothing (the attempt stays open)."""
    env = cli.call(tt, "retry", tt)
    body = env.get("body") if isinstance(env.get("body"), dict) else {}
    if not webtarget.ready(body):
        body = webtarget.wait_ready(tt, body, log=lambda m: None, wait=120)
    if not webtarget.ready(body):
        log(f"[web-harden] {tt}: target not up ({body.get('result') or body.get('error')}) -- skipped")
        return None
    empty = Path(tempfile.mkdtemp(prefix="webharden-", dir=str(paths.ROOT / ".run")))
    try:
        att = cli.attempt_id(body)
        compound._touched(tt, Path(sdir).parent, att)   # keep the attempt open; web_live_restore re-solves it
        got, err, dt = solvers.run_solver(sdir, body, empty, timeout)
        ids = body.get("answer_ids") or list(got or {})
        proofs = sum(1 for i in ids if _PROOF.fullmatch(str((got or {}).get(i) or "").strip()))
        if err:
            log(f"[web-harden] {tt}: solver error {str(err)[:120]}")
        return proofs, len(ids), round(dt, 2)
    except Exception as e:  # noqa: BLE001 - one challenge never sinks the sweep
        log(f"[web-harden] {tt}: note {str(e)[:160]}")
        return None


def harden(fix=False, timeout=60, solver=GENERIC, log=print):
    """Run the generic solver against every web day's fresh Time Trial AND Mastery target; report pass/fail per
    (class, mode). Mastery gets a longer budget (multiple targets, slow ones like the stored-XSS moderator bot)."""
    results = []
    for day, od, mode, cid in web_challenges_with_solver():
        budget = timeout if mode == "time_trial" else int(timeout * 2)   # mastery: multiple + slow targets
        r = check_solver(cid, solver, budget, log)
        if r is None:
            continue
        proofs, total, dt = r
        ok = total > 0 and proofs >= total
        log(f"[web-harden] D{day:02d} {od.name} {mode}: {'OK  ' if ok else 'MISS'} {proofs}/{total} proof(s) in {dt}s")
        results.append({"day": day, "chal": od.name, "mode": mode, "ok": ok, "proofs": proofs, "total": total})
        if not ok and fix:
            log(f"[web-harden] D{day:02d} {od.name} {mode}: the GENERIC solver missed {total - proofs}/{total} field(s) "
                f"-> add/repair a handler in lib/web/handlers (dispatch on this challenge's /api/clues key) or widen the "
                f"per-target budget for a slow target (e.g. the stored-XSS bot); note it under '## Proposed lib additions'")
    try:
        compound.web_live_restore(log=log)   # re-solve every attempt we left open with each day's own solver
    except Exception as e:  # noqa: BLE001
        log(f"[web-harden] restore note: {str(e)[:160]}")
    n_ok = sum(1 for r in results if r["ok"])
    tt_ok = sum(1 for r in results if r["ok"] and r["mode"] == "time_trial")
    m_ok = sum(1 for r in results if r["ok"] and r["mode"] == "mastery")
    tt_n = sum(1 for r in results if r["mode"] == "time_trial")
    m_n = sum(1 for r in results if r["mode"] == "mastery")
    log(f"[web-harden] generic solver: TT {tt_ok}/{tt_n}, Mastery {m_ok}/{m_n} (overall {n_ok}/{len(results)})"
        + ("" if n_ok == len(results) else " -- harden the misses before the next drop"))
    return results


def main():
    ap = argparse.ArgumentParser(prog="hctf web-harden", description=__doc__)
    ap.add_argument("--fix", action="store_true", help="flag each missed class for a handler/generalize")
    ap.add_argument("--timeout", type=float, default=40)
    ap.add_argument("--solver", default=str(GENERIC), help="solver dir to harden (default: the generic web seed)")
    a = ap.parse_args()
    res = harden(fix=a.fix, timeout=a.timeout, solver=Path(a.solver))
    raise SystemExit(0 if all(r["ok"] for r in res) else 1)


if __name__ == "__main__":
    main()
