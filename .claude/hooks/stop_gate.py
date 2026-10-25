#!/usr/bin/env python3
"""Stop hook for harness workers (no-op in normal sessions, i.e. when HCTF_STAGE is unset).

single: may stop only when the Single Solve is complete AND the solver passes its regression cases
        (orientation challenges: completion only), or HELP.md exists.
fix:    may stop only when the solver yields every answer_id for the live timed contract,
        or the deadline is nearly gone.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
MAX_BLOCKS = int(os.environ.get("HCTF_MAX_BLOCKS", "10"))  # escalate to HELP sooner instead of grinding


def allow():
    sys.exit(0)


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


stage, cid = os.environ.get("HCTF_STAGE"), os.environ.get("HCTF_CHAL")
if not stage or not cid:
    allow()
# A warm worker (hctf/workers.py WarmWorker) ends its warm-up turn ("READY") while the GM download + triage are still
# running; the harness deletes the flag right before it sends the real task.
if os.environ.get("HCTF_WARM_FLAG") and Path(os.environ["HCTF_WARM_FLAG"]).exists():
    allow()

from hctf import cli, orchestrate, paths, solvers, timed  # noqa: E402

mdir = paths.mode_dir(cid)
if (mdir / "HELP.md").exists():
    allow()
counter = mdir / f".stop-blocks-{os.environ.get('HCTF_WORKER_START', '0')}"
n = int(counter.read_text()) if counter.exists() else 0
if n >= MAX_BLOCKS:
    allow()
counter.write_text(str(n + 1))

if stage == "single":
    complete = cli.is_complete(cid)
    if os.environ.get("HCTF_LANE") == "welcome":
        if complete:
            allow()
        block("The challenge is not complete yet: no CORRECT result recorded. Keep going, or write HELP.md if truly blocked.")
    ok, res = orchestrate.ensure_case_and_test(paths.base_id(cid), paths.solver_dir(cid))
    static = solvers.id_cache_problems(paths.solver_dir(cid))
    if complete and ok and not static:
        allow()
    todo = []
    if not complete:
        todo.append("the Single Solve is not fully CORRECT yet (check `hctf status`, keep investigating, then `hctf submit`)")
    if not ok:
        todo.append(f"`hctf solver-test {cid}` does not pass yet: {json.dumps(res)[:600]}")
    if static:
        todo.append("unsafe solver cache (fix it now, before the Mastery: it breaks multi-set runs): " + static[0][:400]
                    + (f" (+{len(static) - 1} more)" if len(static) > 1 else ""))
    block("Not done: " + "; ".join(todo) + ". Re-read notes.md, pick the next most promising lead, and continue. "
          "If you have been stuck for a while, use the explore-alternatives skill.")

if stage == "generalize":
    # passing = solvers.gate_ok: a verified case matches its expected.json; an UNVERIFIED one (a failed variant) needs every
    # field answered with no GM-rejected value (D25 C2: it could never pass before, ~130 s of a fixed worker held here)
    ok, res = orchestrate.ensure_case_and_test(paths.base_id(cid), paths.solver_dir(cid))
    static = solvers.id_cache_problems(paths.solver_dir(cid))
    if ok and not static:
        allow()
    if ok:
        block("Every case passes, but the solver has an unsafe cache (it breaks multi-set Mastery runs): "
              + "; ".join(static[:2])[:700] + ". Fix it, then re-run `hctf solver-test`.")
    bad = [r for r in res if not solvers.gate_ok(r)] if isinstance(res, list) else res
    block(f"`hctf solver-test {paths.base_id(cid)}` does not pass for every case yet: {json.dumps(bad)[:700]}. "
          "Fix solve.py (never edit cases/*/expected.json -- it is GM-verified only), then re-run. An unverified "
          "variant passes once every field is answered and no GM-rejected value comes back."
          + (f" Also: {static[0][:300]}" if static else ""))

if stage == "live":
    # done = the attempt is CORRECT or every field this worker owes (orchestrate.LiveAnswer) has been ACCEPTED
    try:
        owe = json.loads((mdir / ".live_fields.json").read_text())
    except (OSError, ValueError):
        allow()
    att, fields, acc, correct = owe.get("attempt"), set(owe.get("fields") or []), set(), False
    try:
        for ln in (mdir / "submissions.jsonl").read_text().splitlines():
            r = json.loads(ln)
            if r.get("attempt") == att and r.get("kind") in ("accepted", "correct"):
                acc |= set(r.get("answers") or {})
                correct = correct or r.get("kind") == "correct"
    except (OSError, ValueError):
        pass
    if correct or fields <= acc:
        allow()
    block(f"Not done: {len(fields - acc)} listed field(s) not accepted yet: {sorted(fields - acc)[:12]}. Derive each "
          f"from the attempt's bytes and `hctf submit {cid} '{{\"<id>\": \"<value>\"}}'` (never a REJECTED value).")

if stage == "fix":
    contract = cli.load(cid, "start.json") or {}
    left = timed.seconds_left(contract)
    if left is not None and left < 25:
        allow()
    art = timed.latest_artifacts(cid)
    answers, problems = solvers.solve_contract(contract, art, paths.solver_dir(cid), timeout=60)
    missing = [a for a in contract.get("answer_ids", []) if a not in answers]
    if not missing and not problems:
        allow()
    block(f"{int(left or 0)}s left. `hctf solver-run {cid}` still has missing={missing} problems={problems[:3]}. Fix and re-run.")
allow()
