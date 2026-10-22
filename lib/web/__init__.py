"""Generic web-exploitation solver (B1): one solver that handles every web challenge of the known kit, so a web day
needs NO drop-time generalize.

The apps since D05 are one kit: `GET /api/clues` returns a JSON object whose single concept-specific KEY names the
vuln class. `solve_target` dispatches on that key (never the value -- the documented pitfall), races the matching
class handler(s), and returns the `proof_<hex>`. Handlers come from three sources, raced together so the first proof
wins and an unknown class still gets a real try:
  1. built-in class handlers in lib/web/handlers/ (lifted from the proven Day-21 solvers),
  2. every earlier web day's own solver `answer()` (compounded Mastery targets mix earlier classes in),
  3. a `default` general ladder (R1) driven by the invariant kit shape -- the no-fail path for a never-seen class.

Hardened off-peak against free earlier-day Time Trial targets (hctf web-harden), so it is first-try-correct at the
drop. LLM-first: this is dispatch + proven exploit code, not a re-implemented parser; a genuinely new class is the
adaptive worker's job and the ratchet folds its fix back here.
"""
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from lib import solverrt, websolve  # noqa: E402
from lib.web import handlers  # noqa: E402


def _prior_web_solvers():
    """(day-id, module) for every earlier web day's solver that exposes answer(), newest first. Loaded once; a
    compounded Mastery target may be any earlier class, so racing their answer() covers the whole history for free."""
    mods = []
    base = ROOT / "challenges"
    dirs = sorted((p for p in base.glob("day*/web-*/solver") if (p / "solve.py").exists()),
                  key=lambda p: p.parts, reverse=True)
    for d in dirs:
        try:
            import importlib.util
            name = "webprior_" + re.sub(r"\W", "_", str(d.relative_to(base)))
            spec = importlib.util.spec_from_file_location(name, d / "solve.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "answer"):
                mods.append((str(d.relative_to(base).parent), mod))
        except Exception as e:  # noqa: BLE001 - a broken prior solver must not sink the dispatch
            print(f"prior web solver {d}: {e!r}", file=sys.stderr)
    return mods


def candidates(base, clues_json, dispatch_key, question=None, contract=None):
    """Ordered (name, fn) probes to race for one target: the built-in handler for the clue key first, then the
    general `default` ladder, then every earlier web day's answer()."""
    out = []
    for name, fn in handlers.for_key(dispatch_key, clues_json):
        out.append((name, lambda fn=fn: fn(base, clues_json)))
    out.append(("default", lambda: handlers.default(base, clues_json)))
    if question is not None and contract is not None:
        for day, mod in _prior_web_solvers():
            out.append((f"prior:{day}", lambda mod=mod: _safe_answer(mod, question, contract)))
    return out


def _safe_answer(mod, question, contract):
    try:
        v = mod.answer(None, question, None, contract)
    except Exception:  # noqa: BLE001
        return None
    return v if v and websolve.PROOF_RE.fullmatch(str(v).strip()) else None


def solve_target(question, contract, budget=40):
    """Proof for one live target (a contract question whose `artifact` is a Target), or None."""
    base = websolve.base_of(question, contract)
    if not base:
        return None
    clues_json, key = websolve.clues(base)
    return websolve.race(candidates(base, clues_json, key, question, contract), budget=budget)


def _iter_pairs(contract):
    ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions", [])]
    qs = contract.get("questions", [])
    return [(aid, qs[i] if i < len(qs) else {}) for i, aid in enumerate(ids)]


def solve(contract, artifacts=None):
    """{answer_id: proof} for every target in the contract. Targets run in parallel (I/O bound); partials are emitted
    at the deadline by the caller's emit path."""
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    jobs = _iter_pairs(contract)

    def run(job):
        aid, q = job
        p = solve_target(q, contract)
        return {aid: p} if p else {}

    solverrt.run_sets(jobs, run, out, pool, io_bound=True)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=False)
    a = ap.parse_args()
    contract = json.loads(Path(a.contract).read_text())
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    for aid, q in _iter_pairs(contract):
        p = solve_target(q, contract)
        if p:
            out[aid] = p
    solverrt.emit_and_exit(out, pool)


if __name__ == "__main__":
    main()
