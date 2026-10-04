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


def timed_dir(cid):
    """Where the one-shot timed runner (hb_timed) keeps the attempt's contract.json + downloads."""
    return cli.ROOT / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", cid)


def artifacts_for(cid, contract):
    """Artifacts dir holding THIS attempt's bytes: artifacts/latest if its manifest names the attempt, else the
    timed runner's download dir if its contract.json is the same attempt, else a fresh download. Never pair a
    contract with another attempt's bytes (that seeded variant-mastery-efc3d9e4 with 6605fd8c's delivery 2)."""
    aid = cli.attempt_id(contract or {})
    art = latest_artifacts(cid)
    if art and (art / "manifest.json").exists():
        if json.loads((art / "manifest.json").read_text()).get("attempt") == aid:
            return art
    tdir = timed_dir(cid)
    if aid and (tdir / "contract.json").exists() and cli.attempt_id(json.loads((tdir / "contract.json").read_text())) == aid:
        return tdir
    class A:
        id, delivery = cid, None
    import contextlib
    import io
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            cli.c_artifact(A)
    except Exception:
        return None
    art = latest_artifacts(cid)
    m = art / "manifest.json" if art else None
    return art if m and m.exists() and json.loads(m.read_text()).get("attempt") == aid else None


def ensure_started(cid):
    """Start (or resume: start is idempotent while the clock runs) and download the variant."""
    with cli.chal_lock(cid):
        env = cli.call(cid, "start", cid)
    body = env["body"] or {}
    if env["http"] != 200 or body.get("error"):
        return None, body
    if not cli.attempt_id(body):
        # 200 {"result": "expired"} (the timed run overshot its deadline): never save that over the contract.
        # Adopt the timed runner's contract instead, so capture_variant/solver-run see the attempt that just ran.
        tdir = timed_dir(cid)
        tc = json.loads((tdir / "contract.json").read_text()) if (tdir / "contract.json").exists() else None
        if cli.attempt_id(tc) and cli.attempt_id(tc) != cli.attempt_id(cli.load(cid, "start.json")):
            cli.save(cid, "start.json", tc)
            cli.save(cid, "contract.json", tc)
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
    """Execute one timed attempt. The clock-critical start->download->solve->submit runs LOCALLY against
    the public GM (pairing token; direct HTTPS is fast enough for the ~6s windows), or on Homebase over SSH
    as a fallback. The solver must already be correct (built/generalised offline).
    Returns: correct | expired | blocked | error:<x>.
      correct            -> GM accepted everything
      blocked            -> solver incomplete/wrong for this variant (caller generalises offline, then retries)
      expired            -> the attempt's clock ran out before we could submit a complete answer
    """
    from . import workers
    res = workers.run_timed_auto(solver_dir, cid, op=op)
    r = str(res.get("result", "")).lower()
    log(f"[{cid}] timed: {json.dumps({k: res.get(k) for k in ('result', 'remaining', 'elapsed', 'missing', 'per_set', 'bad_sets', 'attempt_id') if k in res})}")
    if r == "correct":
        # Record the confirmed answers + a correct submission locally (the timed runner submits to the GM
        # directly), so cli.is_complete and the dashboard reflect reality.
        cli.record_remote_result(cid, res.get("attempt_id"), res.get("submitted") or {}, "correct", res.get("detail"))
        return "correct"
    if cli.is_complete(cid):
        return "correct"
    if r in ("solver_incomplete", "solver_error", "incorrect", "accepted", "exec_error"):
        return "blocked"       # the solver needs work; caller will generalise offline then retry
    if r in ("expired", "start_required") or "expired" in json.dumps(res).lower():
        return "expired"
    if "prerequisite" in r:
        return "error:prerequisite"
    return "blocked"
