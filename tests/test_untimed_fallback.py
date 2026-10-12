"""Behavior checks for the untimed fallback (top-team rule: out of unique attempts -> stop going for the Hall of Fame,
still take the flag on an untimed attempt). Offline: no GM / no Homebase / no workers.

Run:  source bin/env.sh && python3 tests/test_untimed_fallback.py      (exit 0 = all pass)
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
import hb_timed  # noqa: E402
from hctf import gm, orchestrate, timed, workers  # noqa: E402

d = Path(tempfile.mkdtemp())

# 1) _post_untimed: plain retry (NO run_for_time) first = the regular pool on a run_for_time_supported route; a legacy
#    route answers it with an exhausted verdict -> practice continuation; both refused -> the practice refusal.
sent = []


def fake_post(replies):
    it = iter(replies)
    return lambda payload, tries=3: (sent.append(payload), next(it))[1]


_opo = hb_timed._post_once
try:
    sent.clear()
    hb_timed._post_once = fake_post([{"answer_ids": ["a"], "deadline": None, "run_for_time": False,
                                      "variant_fresh": False}])
    b = hb_timed._post_untimed("c/time_trial")
    assert b["answer_ids"] == ["a"] and sent == [{"op": "retry", "challenge": "c/time_trial"}], sent
    sent.clear()
    hb_timed._post_once = fake_post([{"error": "retry_variants_unavailable"},
                                     {"answer_ids": ["a"], "deadline": None, "practice": True}])
    b = hb_timed._post_untimed("c/time_trial")
    assert b.get("practice") and [p["op"] for p in sent] == ["retry", "practice"], sent
    assert all("run_for_time" not in p for p in sent), sent
    sent.clear()
    hb_timed._post_once = fake_post([{"error": "rotation_exhausted"}, {"error": "practice_unavailable"}])
    assert hb_timed._post_untimed("c/time_trial") == {"error": "practice_unavailable"}
finally:
    hb_timed._post_once = _opo
print("ok  _post_untimed: plain retry (regular pool) -> practice on an exhausted legacy route; never run_for_time")

# 2) _attempt: an exhausted verdict is flagged `exhausted` (not a plain start refusal) and a refused `retry` is NOT
#    resent as a plain start (that only reconnects to the spent attempt).
_ops, _opool = hb_timed._post_start, hb_timed._pool
try:
    sent.clear()
    hb_timed._pool = lambda: object()
    hb_timed._post_start = lambda payload, tries=3: (sent.append(payload), {"error": "retry_variants_unavailable"})[1]
    out = hb_timed.run_attempt("c/time_trial", "challenges/x/solver", op="retry")
    assert out["result"] == "retry_variants_unavailable" and out.get("exhausted") and out.get("start_refused"), out
    assert [p["op"] for p in sent] == ["retry"], sent
    assert hb_timed._exhausted("rotation_exhausted") and not hb_timed._exhausted("training_rotation_invalid")
finally:
    hb_timed._post_start, hb_timed._pool = _ops, _opool
print("ok  _attempt: retry_variants_unavailable -> exhausted flag, no plain-start resend")

# 3) classification: both exhausted spellings (and the flag) -> error:exhausted, ahead of the start-refused backoff
_orig = (timed._remember, timed._keep_failed_attempt, timed.capture_case)
timed._remember = timed._keep_failed_attempt = lambda *a, **k: None
timed.capture_case = lambda *a, **k: None
try:
    pr = lambda res: timed.process_result("c/time_trial", d, res, log=lambda *a, **k: None)  # noqa: E731
    assert pr({"result": "retry_variants_unavailable", "start_refused": True}) == "error:exhausted"
    assert pr({"result": "rotation_exhausted", "start_refused": True}) == "error:exhausted"
    assert pr({"result": "some_new_error", "start_refused": True, "exhausted": True}) == "error:exhausted"
    assert pr({"result": "training_rotation_invalid", "start_refused": True}) == "error:start"
finally:
    timed._remember, timed._keep_failed_attempt, timed.capture_case = _orig
print("ok  classification: rotation_exhausted / retry_variants_unavailable -> error:exhausted")

# 4) timed_stage: exhausted -> the next attempts are op=untimed (own budget), a pass ends the stage; no generalize on
#    the verdict itself. An untimed attempt refused as exhausted too -> stop.
ch = object.__new__(orchestrate.Chain)
ch.base, ch.entries, ch.sdir = "b", {"time_trial": {"id": "b/time_trial"}}, d
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
ch._pre_attempt_done = True
calls, gen, stages = [], [], []
patches = {
    (orchestrate, "set_state"): lambda *a, **k: stages.append(k.get("stage")),
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (timed, "last_result"): lambda cid: {"result": "retry_variants_unavailable"},
    (orchestrate.time, "sleep"): lambda s: None,
    (orchestrate.Chain, "generalize"): lambda self, *a, **k: gen.append(1),
}


def stage_run(results):
    it = iter(results)
    patches[(timed, "run")] = lambda cid, sdir, log=None, **k: (calls.append(k.get("op", "start")), next(it))[1]
    saved = {k: getattr(*k) for k in patches}
    try:
        for (mod, name), fn in patches.items():
            setattr(mod, name, fn)
        return ch.timed_stage("time_trial")
    finally:
        for (mod, name), fn in saved.items():
            setattr(mod, name, fn)


calls.clear(), stages.clear()
assert stage_run(["error:exhausted", "correct"]) is True
assert calls == ["start", "untimed"] and not gen and "time_trial:untimed-pass" in stages, (calls, stages)
calls.clear()
assert stage_run(["error:exhausted", "error:exhausted"]) is False and calls == ["start", "untimed"] and not gen, calls
calls.clear()
_our = orchestrate.UNTIMED_ROUNDS
try:   # untimed rounds get their own budget even late in the timed retries
    orchestrate.UNTIMED_ROUNDS = 3
    assert stage_run(["error:exhausted", "blocked", "blocked", "correct"]) is True
    assert calls == ["start", "untimed", "untimed", "untimed"] and len(gen) == 2, (calls, gen)
finally:
    orchestrate.UNTIMED_ROUNDS = _our
print("ok  timed_stage: exhausted -> untimed attempts (own budget; generalize between rounds), pass -> untimed-pass")

# 5) workers: op=untimed never goes to Homebase; timed_env asks for the plain pool once ranked_attempts_remaining == 0
_ort, _ohb, _ocd = workers.run_timed, workers.run_hb_timed, workers.__dict__.get("cli")
seen = []
try:
    workers.run_timed = lambda sdir, cid, op="start", timeout=60: (seen.append((op, timeout)), {"result": "correct"})[1]
    workers.run_hb_timed = lambda *a, **k: (_ for _ in ()).throw(AssertionError("untimed must stay local"))
    r = workers.run_timed_auto(d, "c/time_trial", op="untimed")
    assert seen and seen[0][0] == "untimed" and seen[0][1] >= workers.UNTIMED_BUDGET and r["routed"] == "local (untimed)"
finally:
    workers.run_timed, workers.run_hb_timed = _ort, _ohb
from hctf import cli  # noqa: E402
_ocdir = cli.cdir
had = os.environ.pop("HCTF_RUN_FOR_TIME", None)
try:
    cli.cdir = lambda cid: d
    (d / "last_timed.json").write_text(json.dumps({"ranked_attempts_remaining": 0}))
    assert workers.timed_env("c/time_trial").get("HCTF_RUN_FOR_TIME") == "0"
    (d / "last_timed.json").write_text(json.dumps({"ranked_attempts_remaining": 4}))
    assert "HCTF_RUN_FOR_TIME" not in workers.timed_env("c/time_trial")
    (d / "last_timed.json").write_text(json.dumps({"attempts_remaining": 0}))   # legacy route: no ranked field
    assert "HCTF_RUN_FOR_TIME" not in workers.timed_env("c/time_trial")
    os.environ["HCTF_RUN_FOR_TIME"] = "1"                                         # explicit override wins
    (d / "last_timed.json").write_text(json.dumps({"ranked_attempts_remaining": 0}))
    assert "HCTF_RUN_FOR_TIME" not in workers.timed_env("c/time_trial")
finally:
    cli.cdir = _ocdir
    os.environ.pop("HCTF_RUN_FOR_TIME", None)
    if had is not None:
        os.environ["HCTF_RUN_FOR_TIME"] = had
print("ok  workers: untimed stays local; ranked_attempts_remaining == 0 -> plain pool (explicit env wins)")

# 6) gm.py knows the practice op (legacy-route untimed continuation)
_oreq = gm._request
try:
    got = []
    gm._request = lambda method, params=None, payload=None, **k: (got.append((method, payload)), (200, {}, b"{}"))[1]
    gm.run(["practice", "c/time_trial"])
    assert got == [("POST", {"op": "practice", "challenge": "c/time_trial"})], got
finally:
    gm._request = _oreq
print("ok  gm.py practice -> POST {op: practice}")

# 7) hb_timed: no deadline -> the solver gets the untimed budget, not 30 s
os.environ["HCTF_UNTIMED_BUDGET"] = "90"
try:
    assert hb_timed._solve_budget({"deadline": None, "practice": True}, None) == 90.0
    assert hb_timed._solve_budget({"deadline": None, "run_for_time": False}, None) == 90.0
    assert hb_timed._solve_budget({}, None) == 28.5                  # unknown clock: the old 30 s default
finally:
    os.environ.pop("HCTF_UNTIMED_BUDGET", None)
print("ok  hb_timed: untimed solve budget from HCTF_UNTIMED_BUDGET")

# 8) hof_race: Mastery first, up to HOF_RACE retries while >= max(MIN, RESERVE+1) left; stops on a failure; skips
#    untimed / ineligible modes and a Mastery that isn't solved; never runs against a replay proxy.
runs, said = [], []
left = {"b/mastery": 30, "b/time_trial": 9}
results = {"b/mastery": iter(["correct", "correct", "correct"]), "b/time_trial": iter(["correct", "blocked"])}


def fake_run(cid, sdir, log=None, op="start"):
    runs.append((cid, op))
    left[cid] -= 1
    return next(results[cid])


rp = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "say"): lambda m, *a, **k: said.append(m),
    (orchestrate.cli, "gm_solved"): lambda cid: True,
    (orchestrate, "_gm_ms"): lambda cid: 400,
    (timed, "last_result"): lambda cid: {"hall_of_fame_eligible": True, "ranked_attempts_remaining": left[cid]},
    (timed, "run"): fake_run,
}
saved = {k: getattr(*k) for k in rp}
_env = os.environ.pop("HUNTRESS_GAME_MASTER_URL", None)
try:
    for (mod, name), fn in rp.items():
        setattr(mod, name, fn)
    groups = {"b": [{"mode": "single_solve", "id": "b"}, {"mode": "time_trial", "id": "b/time_trial"},
                    {"mode": "mastery", "id": "b/mastery"}]}
    orchestrate.hof_race(groups)
    assert runs[:3] == [("b/mastery", "retry")] * 3, runs                  # Mastery first, 3 races (30 left)
    assert runs[3:] == [("b/time_trial", "retry"), ("b/time_trial", "retry")], runs   # 9, 8 left -> 2nd fails: stop
    runs.clear()
    left.update({"b/mastery": 6, "b/time_trial": 100})                     # 6 < max(8, 6): no Mastery race
    results["b/time_trial"] = iter(["correct"] * 3)
    timed.last_result = lambda cid: ({"untimed": True, "ranked_attempts_remaining": 100} if cid == "b/time_trial"
                                     else {"hall_of_fame_eligible": True, "ranked_attempts_remaining": left[cid]})
    orchestrate.hof_race(groups)
    assert runs == [], runs                                                # untimed TT pass: no race either
    os.environ["HUNTRESS_GAME_MASTER_URL"] = "http://127.0.0.1:18769"
    timed.last_result = lambda cid: {"hall_of_fame_eligible": True, "ranked_attempts_remaining": 100}
    orchestrate.hof_race(groups)
    assert runs == [] and any("replay GM proxy" in m for m in said), runs
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
    os.environ.pop("HUNTRESS_GAME_MASTER_URL", None)
    if _env is not None:
        os.environ["HUNTRESS_GAME_MASTER_URL"] = _env
print("ok  hof_race: Mastery first, thresholds + reserve, stop on failure, skip untimed, no race on a replay proxy")

# 9) hof.report: per-challenge #1 vs ours, day sum + position among complete teams
from hctf import hof  # noqa: E402
rows = [{"team_name": t, "challenge_id": c, "rank": r, "elapsed_ms": ms}
        for t, c, r, ms in [("X", "w-day-11/time_trial", 1, 200), ("us", "w-day-11/time_trial", 2, 400),
                            ("X", "w-day-11/mastery", 1, 300), ("us", "w-day-11/mastery", 2, 500),
                            ("Y", "w-day-11/mastery", 3, 900)]]
txt = hof.report(day=11, rows=rows, teams=("us",))
assert "us 900 ms over 2 row(s) = #2 of 2 complete teams" in txt and "leader X 500 ms" in txt, txt
print("ok  hof.report: day sum + rank among teams with every row")

# 10) reuse race: submits only when the merged prior answers cover every field; bisects within the probe cap; touches
#     no solver files; an incomplete plan submits nothing.
from hctf import solvers  # noqa: E402
ch2 = object.__new__(orchestrate.Chain)
ch2.base, ch2.lane, ch2.sdir = "r", "script-analysis", d / "rsolver"
subs, confirmed, msgs = [], {}, []
truth = {"a": "1", "b": "2", "c": "3", "e": "5"}


def fake_submit(cid, group, force=False, probe=False):
    subs.append(dict(group))
    if all(truth.get(k) == v for k, v in group.items()):
        confirmed.update(group)
        return ("correct" if len(confirmed) == len(truth) else "accepted"), {}, None
    return "incorrect", {}, None


def race(high, spec, cap=3):
    subs.clear(), confirmed.clear(), msgs.clear()
    rp = {
        (orchestrate.cli, "load"): lambda cid, name: {"answer_ids": list(truth)},
        (orchestrate.cli, "is_complete"): lambda cid: len(confirmed) == len(truth),
        (orchestrate.cli, "confirmed_answers"): lambda cid, att=None: dict(confirmed),
        (orchestrate.cli, "submit"): fake_submit,
        (timed, "latest_artifacts"): lambda cid: d,
        (solvers, "reuse_plan"): lambda *a, **k: {"high": high, "spec": spec, "runs": {"x": 1}, "best": None},
        (orchestrate, "say"): lambda m, *a, **k: msgs.append(m),
        (orchestrate, "set_state"): lambda *a, **k: None,
        (orchestrate, "REUSE_RACE_PROBES"): cap,
    }
    sv = {k: getattr(*k) for k in rp}
    try:
        for (mod, name), fn in rp.items():
            setattr(mod, name, fn)
        ch2._reuse_race("r")
    finally:
        for (mod, name), fn in sv.items():
            setattr(mod, name, fn)


race({"a": "1", "b": "2", "c": "3"}, {"e": "5"})
assert len(subs) == 1 and len(confirmed) == 4 and any("WON" in m for m in msgs), (subs, msgs)
race({"a": "1", "b": "2"}, {})                                   # can't finish: nothing submitted
assert subs == [], subs
race({"a": "1", "b": "X", "c": "3"}, {"e": "5"}, cap=3)          # one wrong: full set, then halves, within the cap
assert len(subs) == 3 and not len(confirmed) == 4 and any("not complete" in m for m in msgs), (subs, msgs)
assert not ch2.sdir.exists()
print("ok  reuse race: submit only a complete set, bisect within the cap, no solver files touched")
