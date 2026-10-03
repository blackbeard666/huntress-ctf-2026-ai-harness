"""Scripted Time Trial / Mastery runs: start -> download -> dispatch solvers -> submit per set.

Clock-aware: if solvers fail or some answers are rejected, a fix worker (an LLM process) gets the
remaining time to patch the solver; we re-run and submit again until done or the deadline passes.
"""
import datetime as dt
import json
import re
import time
from pathlib import Path

from . import cli, solvers

SUBMIT_MARGIN = 8          # seconds kept in reserve for the final submit round-trip (~1-3s over ssh)
MAX_WRONG_TIMED = 6        # incorrect submissions allowed per timed attempt (several sets per bundle)


def seconds_left(contract):
    d = (contract or {}).get("deadline")
    if not d:
        return None
    end = dt.datetime.fromisoformat(d.replace("Z", "+00:00"))
    return (end - dt.datetime.now(dt.timezone.utc)).total_seconds()


def _set_key(aid):
    m = re.match(r"(set\d+)\.", aid)
    return m.group(1) if m else "_"


def latest_artifacts(cid):
    p = cli.cdir(cid) / "artifacts" / "latest"
    return p.resolve() if p.exists() else None


def ensure_started(cid):
    """Start (or resume: start is idempotent while the clock runs) and download the variant."""
    with cli.chal_lock(cid):
        env = cli.call(cid, "start", cid)
    body = env["body"] or {}
    if env["http"] != 200 or body.get("error"):
        return None, body
    cli.save(cid, "start.json", body)
    cli.save(cid, "contract.json", body)
    art = latest_artifacts(cid)
    manifest = json.loads((art / "manifest.json").read_text()) if art and (art / "manifest.json").exists() else {}
    if manifest.get("attempt") != cli.attempt_id(body):  # fetch this attempt's artifacts if we don't have them
        class A:  # argparse-like namespace for cli.c_artifact
            id, delivery = cid, None
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            cli.c_artifact(A)
    return body, None


def run(cid, default_solver, fix=None, log=print):
    """Run one timed challenge to completion. fix(cid, contract, artifacts, problems, seconds_left) is
    called (blocking) when something is missing. Returns one of: correct, expired, blocked, error:<x>."""
    contract, err = ensure_started(cid)
    if contract is None:
        return f"error:{(err or {}).get('error', 'start failed')}"
    att = cli.attempt_id(contract)
    art = latest_artifacts(cid)
    log(f"[{cid}] attempt {att} started, {len(contract.get('answer_ids', []))} answers, "
        f"{seconds_left(contract) or 0:.0f}s left")
    rounds = 0
    while True:
        rounds += 1
        left = seconds_left(contract)
        if left is not None and left <= 0:
            return "expired"
        done = cli.confirmed_answers(cid, att)
        todo = [a for a in contract.get("answer_ids", []) if a not in done]
        if not todo:
            return "correct"
        answers, problems = solvers.solve_contract(solvers.sub_contract(contract, todo), art, default_solver,
                                                   timeout=max(10, min(120, (left or 120) - SUBMIT_MARGIN)))
        rejected = []
        # Submit per set, so a wrong answer in one set doesn't hide which set was wrong.
        by_set = {}
        for aid in todo:
            if aid in answers:
                by_set.setdefault(_set_key(aid), {})[aid] = answers[aid]
        for key, group in by_set.items():
            kind, body, refused = cli.submit(cid, group, max_wrong=MAX_WRONG_TIMED)
            log(f"[{cid}] submit {key} ({len(group)}): {kind or 'refused'} {json.dumps(body or refused)[:200]}")
            if kind == "correct":
                return "correct"
            if kind == "expired":
                return "expired"
            if kind == "incorrect" or refused:
                rejected.append(f"{key}: GM said {kind or 'refused'} for {group}: {body or refused}")
        if cli.is_complete(cid):
            return "correct"
        left = seconds_left(contract)
        if fix is None or (left is not None and left < 30) or rounds > 6:
            return "expired" if left is not None and left <= 0 else "blocked"
        fix(cid, contract, art, problems + rejected, left)
