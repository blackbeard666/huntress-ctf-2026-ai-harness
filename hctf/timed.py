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


def run(cid, solver_dir, fix=None, log=print, op="start"):
    """Execute one timed attempt. The clock-critical start->download->solve->submit runs ON Homebase
    (adjacent to the GM; windows are ~6s so SSH-per-op from WSL can't make it). The solver must already be
    correct (built/generalised offline). Returns: correct | expired | blocked | error:<x>.
      correct            -> GM accepted everything
      blocked            -> solver incomplete/wrong for this variant (caller generalises offline, then retries)
      expired            -> the attempt's clock ran out before we could submit a complete answer
    """
    from . import workers
    res = workers.run_hb_timed(solver_dir, cid, op=op)
    r = str(res.get("result", "")).lower()
    log(f"[{cid}] hb_timed: {json.dumps({k: res.get(k) for k in ('result', 'remaining', 'elapsed', 'missing') if k in res})}")
    if r in ("correct",) or cli.is_complete(cid):
        return "correct"
    if r in ("solver_incomplete", "solver_error", "incorrect", "accepted", "exec_error"):
        return "blocked"       # the solver needs work; caller will generalise offline then retry
    if r in ("expired", "start_required") or "expired" in json.dumps(res).lower():
        return "expired"
    if "prerequisite" in r:
        return "error:prerequisite"
    return "blocked"
