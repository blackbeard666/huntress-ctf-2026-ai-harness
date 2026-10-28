"""D27 web track, offline: the one-shot credit-kit (Double Spent) dispatch fix. Fakes only -- no GM, no live target.

Day 27 burned `web-double-spent`: a one-credit race/double-spend kit whose single credit is spent by any sequential
POST, yet lib.web raced the class handler against the `default` ladder + every prior-day solver -- their POSTs spent
the credit before the burst. The fix (lib.web.solve_target): when a target is a confirmed credit kit, race ONLY the
RUN_ALONE handler(s), never the ladder / priors / other furniture-key handlers, with a budget wide enough for the
burst + audit. Detection is a side-effect-free audit GET (the RUN_ALONE flag alone over-triggers: the handler keys on
`secondary_route`, which is kit furniture many non-credit kits ship).

Run:  source bin/env.sh && python3 tests/test_d27_web.py      (exit 0 = all pass)
"""
import contextlib
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import websolve  # noqa: E402
import lib.web as libweb  # noqa: E402
from lib.web import handlers as webhandlers  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


# The Double Spent kit is ALL furniture: the class is identified only by the audit route's response, never a clue key.
KIT = {"framework": "flask", "feature_route": "/api/buy", "current_role": "user", "secondary_route": "/api/audit"}
AUDIT_CREDIT = '{"error":"credit_not_overspent","credits":1}'   # a live, un-overspent credit kit
AUDIT_PLAIN = '{"items":[{"id":1,"name":"ok"}]}'                  # a non-credit kit that merely has a secondary_route


def fetch_router(audit_body):
    def _fetch(url, *a, **k):
        if url.endswith("/api/audit"):
            return 200, audit_body, []
        return 200, "", []
    return _fetch


def run(clues, audit_body, known=False):
    """solve_target with race() stubbed to capture (probe names, budget); returns (names, budget, candidates_called)."""
    seen = {"names": None, "budget": None, "cand": False}

    def fake_race(probes, budget=40, report=None):
        seen["names"] = [n for n, _f in probes]
        seen["budget"] = budget
        if isinstance(report, dict):
            report.update(winner=None, elapsed=0.0, timed_out=False)
        return None

    def fake_candidates(*a, **k):
        seen["cand"] = True
        return [("default", lambda: None)]

    with patched({(websolve, "fetch"): fetch_router(audit_body),
                  (websolve, "race"): fake_race,
                  (libweb, "candidates"): fake_candidates,
                  (libweb, "class_known"): lambda c, key: known,
                  (libweb, "_prior_sources"): lambda: []}):
        libweb.solve_target({"id": "proof-1", "artifact": "Target 1"},
                            {"targets": [{"id": "Target 1", "url": "https://t.example/"}]}, clues=clues)
    return seen["names"], seen["budget"], seen["cand"]


# 1) a confirmed credit kit -> solo: ONLY the one-shot handler, wide budget, the ladder/candidates NEVER built
names, budget, cand = run(KIT, AUDIT_CREDIT)
check("confirmed credit kit races ONLY the run-alone handler", names == ["day27_web_double_spent"], names)
check("confirmed credit kit does NOT build the default ladder / prior solvers (no credit-burning POSTs beside it)",
      cand is False)
check("confirmed credit kit gets the RUN_ALONE budget (burst + audit room)", budget == libweb.RUN_ALONE_BUDGET, budget)

# 2) a furniture kit whose audit is NOT a credit kit -> normal path (the flag alone must not hijack it)
names, budget, cand = run(KIT, AUDIT_PLAIN)
check("a non-credit kit that merely has a secondary_route takes the normal ladder path", cand is True, (names, cand))
check("the normal unknown-class path keeps the 12 s cap (not the run-alone budget)",
      budget == libweb.UNKNOWN_KEY_BUDGET, budget)

# 3) an UNFLAGGED future credit kit (probe says credit, but no RUN_ALONE handler maps it) -> solo with NO probe:
#    returns None without ever POSTing, so the one credit is never burned; the adaptive worker then writes the plugin.
with patched({(webhandlers, "_RUN_ALONE"): set()}):
    names, budget, cand = run(KIT, AUDIT_CREDIT)
check("an unflagged credit kit runs NOTHING (empty race) rather than burning the credit on the ladder",
      names == [] and cand is False, (names, cand))

# 4) the real plugin is actually flagged + wired
check("day27_web_double_spent is registered as RUN_ALONE", "day27_web_double_spent" in webhandlers._RUN_ALONE)
check("run_alone_handlers returns exactly the one-shot handler for the kit shape",
      [n for n, _ in webhandlers.run_alone_handlers(websolve.dispatch_key(KIT), KIT)] == ["day27_web_double_spent"])

# ---------------------------------------------------------------- orchestrator self-heal: arena reset + re-solve
import types  # noqa: E402

from hctf import cli, orchestrate, webtarget  # noqa: E402


def selfheal(lane="web", kit=True, ready=True, proof="proof_abcdef12", tries=0, complete=True):
    """Call Chain._web_credit_kit_selfheal on a stub self, recording the arena ops + the submitted answers."""
    rec = {"stop": 0, "start": 0, "submitted": None}
    fresh = {"targets": [{"url": "https://fresh.example/"}], "answer_ids": ["proof-1"]}
    pairs = {
        (orchestrate, "say"): lambda *a, **k: None,
        (webtarget, "is_live_lane"): lambda ln: ln == "web",
        (cli, "load"): lambda c, f: {"targets": [{"url": "https://t.example/"}], "answer_ids": ["proof-1"],
                                     "questions": [{"id": "proof-1", "artifact": "Target 1"}]},
        (webtarget, "arena_stop"): lambda c: rec.__setitem__("stop", rec["stop"] + 1) or {},
        (webtarget, "arena_start"): lambda c: rec.__setitem__("start", rec["start"] + 1) or fresh,
        (webtarget, "wait_ready"): lambda c, b, log=None: fresh,
        (webtarget, "ready"): lambda b: ready,
        (websolve, "clues"): lambda base: ({"framework": "f", "feature_route": "/b", "secondary_route": "/a",
                                            "current_role": "u"}, None),
        (webhandlers, "run_alone_handlers"): (lambda key, cl: [("day27_web_double_spent", lambda *a: None)]) if kit
                                             else (lambda key, cl: []),
        (libweb, "_credit_kit_probe"): lambda base, cl: False,
        (libweb, "solve"): lambda contract: {"proof-1": proof} if proof else {},
        (cli, "submit"): lambda c, ans, **k: rec.__setitem__("submitted", ans) or ("correct", {}, []),
        (cli, "is_complete"): lambda c: complete,
        (cli, "gm_solved"): lambda c: complete,
    }
    me = types.SimpleNamespace(lane=lane, _credit_selfheal_tries=tries)
    with patched(pairs):
        got = orchestrate.Chain._web_credit_kit_selfheal(me, "cid-1")
    return got, rec, me


got, rec, me = selfheal()
check("self-heal on a burned credit kit resets (stop->start) and re-solves to CORRECT",
      got is True and rec["stop"] == 1 and rec["start"] == 1 and rec["submitted"] == {"proof-1": "proof_abcdef12"},
      (got, rec))
check("self-heal counts the reset against the per-chain cap", me._credit_selfheal_tries == 1)

got, rec, _ = selfheal(lane="metadata-forensics")
check("self-heal is a no-op off the web lane (no reset)", got is False and rec["stop"] == 0)

got, rec, _ = selfheal(kit=False)
check("self-heal does NOT reset a non-credit-kit web single (would waste another class's target)",
      got is False and rec["stop"] == 0)

got, rec, _ = selfheal(proof=None)
check("self-heal that re-solves to no proof resets once but reports failure (-> escalates to help)",
      got is False and rec["stop"] == 1)

got, rec, _ = selfheal(tries=orchestrate.CREDIT_SELFHEAL_MAX)
check("self-heal stops resetting once the per-chain cap is reached", got is False and rec["stop"] == 0)

# ---------------------------------------------------------------- post-run all-solved gate (driftwatch.unsolved)
from hctf import driftwatch  # noqa: E402

_metas = {"P_web": {"lane": "web", "ids": {"single_solve": "web-x"}},
          "P_meta": {"lane": "metadata-forensics", "ids": {"single_solve": "meta-y"}}}
with patched({(driftwatch.paths, "CHALLENGES"): types.SimpleNamespace(glob=lambda pat: ["P_meta", "P_web"]),
              (driftwatch.cli, "load_json"): lambda p: _metas[p],
              (driftwatch.cli, "load"): lambda c, f: {"ok": 1},
              (driftwatch.cli, "gm_solved"): lambda c: False,
              (webtarget, "is_live_lane"): lambda ln: ln == "web"}):
    default = [c for _b, c in driftwatch.unsolved(99)]
    withweb = {c for _b, c in driftwatch.unsolved(99, include_web=True)}
check("post-run gate: unsolved() skips web by default (resume would re-roll the live target)", default == ["meta-y"],
      default)
check("post-run gate: include_web=True counts an unsolved web mode too (so post-run is HELD at <24/24)",
      withweb == {"meta-y", "web-x"}, withweb)

# ---------------------------------------------------------------- P1-E straggler escalation (default off, bounded)
def straggler(enabled, holds, groups, rounds=1):
    launched = []

    class FakeChain:
        def __init__(self, base, entries, pools, gov, modes):
            self.base = base

        def run(self):
            launched.append(self.base)
    with patched({(orchestrate, "Chain"): FakeChain,
                  (orchestrate, "STRAGGLER_ESCALATE"): enabled,
                  (orchestrate, "STRAGGLER_ROUNDS"): rounds,
                  (orchestrate, "say"): lambda *a, **k: None,
                  (driftwatch, "unsolved"): lambda day, include_web=False: holds}):
        orchestrate._straggler_escalation(99, groups, None, None, None)
    return sorted(launched)


HOLDS = [("meta-y", "meta-y"), ("web-x", "web-x/time_trial")]
check("straggler escalation is a no-op when disabled (default)",
      straggler(False, HOLDS, {"meta-y": [], "web-x": []}) == [])
check("straggler escalation re-launches every unsolved chain (incl. web) when enabled",
      straggler(True, HOLDS, {"meta-y": [], "web-x": []}) == ["meta-y", "web-x"])
check("straggler escalation launches nothing when the board is complete",
      straggler(True, [], {"meta-y": []}) == [])
check("straggler escalation skips holdouts with no re-runnable chain (e.g. a stale base)",
      straggler(True, [("gone", "gone")], {"meta-y": []}) == [])

# ---------------------------------------------------------------- web Mastery miss-retry (not-ready target caught in-budget)
import os as _os
import time as _time


def miss_retry(one_shot=False, deadline_in=30.0):
    """_solve_into with solve_target stubbed: proof-1 always solves; proof-2 misses the first pass, solves on retry."""
    calls = {}

    def fake_solve_target(q, contract):
        aid = q.get("id")
        calls[aid] = calls.get(aid, 0) + 1
        if aid == "proof-1":
            return "proof_aaaaaaaa"
        if aid == "proof-2" and calls[aid] >= 2:   # ready only on the 2nd attempt
            return "proof_bbbbbbbb"
        return None

    def fake_run_sets(jobs, fn, out, pool, io_bound=True):
        for job in jobs:
            out.update(fn(job))

    contract = {"answer_ids": ["proof-1", "proof-2"],
                "questions": [{"id": "proof-1", "artifact": "T1"}, {"id": "proof-2", "artifact": "T2"}],
                "targets": [{"id": "T1", "url": "https://t1/"}, {"id": "T2", "url": "https://t2/"}]}
    _os.environ["HCTF_SOLVE_DEADLINE"] = str(_time.time() + deadline_in)
    try:
        with patched({(libweb, "solve_target"): fake_solve_target,
                      (libweb.solverrt, "run_sets"): fake_run_sets,
                      (libweb, "WEB_MISS_RETRY_DELAY"): 0.0,
                      (libweb, "WEB_MISS_RETRY_MIN_LEFT"): 0.0,
                      (websolve, "base_of"): lambda q, c: "https://t/",
                      (websolve, "clues"): lambda b: ({}, None),
                      (webhandlers, "run_alone_handlers"): (lambda k, c: [("x", lambda: None)]) if one_shot else (lambda k, c: [])}):
            out, pool = {}, []
            libweb.solverrt.arm_deadline(out, pool) if hasattr(libweb.solverrt, "arm_deadline") else None
            libweb._solve_into(contract, out, pool)
        return out, calls
    finally:
        _os.environ.pop("HCTF_SOLVE_DEADLINE", None)


out, calls = miss_retry(one_shot=False)
check("miss-retry catches a not-ready target on a later pass (no 2-min worker)",
      out.get("proof-2") == "proof_bbbbbbbb" and out.get("proof-1") == "proof_aaaaaaaa", out)
check("miss-retry re-attempted only the MISSED target (proof-2), not the one already solved (proof-1)",
      calls.get("proof-1") == 1 and calls.get("proof-2", 0) >= 2, calls)

out, calls = miss_retry(one_shot=True)
check("miss-retry does NOT retry a one-shot credit kit (a miss there is a burn, not a race)",
      out.get("proof-2") is None and calls.get("proof-2") == 1, (out, calls))

print()
if failures:
    print(f"FAILED ({len(failures)}): " + "; ".join(failures))
    sys.exit(1)
print("all D27 web dispatch + self-heal + post-run-gate + straggler + miss-retry checks passed")
