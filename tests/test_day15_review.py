"""Day 15 review fixes (script Mastery tail, T+2:38 -> T+6:43). Offline: no GM / Homebase / workers.
- A cut-off reply (http.client.IncompleteRead) is UNJUDGED and resent, never an exception out of _post.
- One failing localization submit / set never ends the other sets' localization.
- label_hints.json: an earlier attempt's in-window fixes (TT) rank the next attempt's (Mastery) alternatives.
- Attempt bank: GM-accepted values of a live attempt are reapplied verbatim when it is reconnected.
- orchestrate._cut_short: a cut-short untimed localization reconnects instead of a generalize.
- Replay of the real D15 script Mastery variant (main only): one cut-off reply, still CORRECT in-attempt.

Run:  source bin/env.sh && python3 tests/test_day15_review.py      (exit 0 = all pass)
"""
import http.client
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
import hb_timed  # noqa: E402
from hctf import orchestrate  # noqa: E402

hb_timed.UNJUDGED_RESENDS = (0.0, 0.0)
_orig = {k: getattr(hb_timed, k) for k in ("_post", "_open", "_vocab", "HW")}
TMP = Path(tempfile.mkdtemp(prefix="hctf-d15r-"))


def restore():
    for k, v in _orig.items():
        setattr(hb_timed, k, v)
    hb_timed._CTX.solver_dir = None


def gm(truth, sent, cut=()):
    """_post stand-in judging by `truth`: a subset is accepted iff every value matches; the full id set -> correct.
    `cut`: 1-based submit numbers whose reply is cut off mid-body (IncompleteRead raised from _open)."""
    def post(payload, timeout=None):
        ans = payload.get("answers") or {}
        sent.append(ans)
        if len(sent) in cut:
            hb_timed._open = lambda *a, **k: (_ for _ in ()).throw(http.client.IncompleteRead(b"x" * 10, 99))
            try:
                return _orig["_post"](payload, timeout)
            finally:
                hb_timed._open = _orig["_open"]
        good = all(truth.get(k) == v for k, v in ans.items())
        if not good:
            return {"result": "incorrect"}
        return {"result": "correct", "remaining": 0} if set(ans) >= set(truth) else {"result": "accepted", "remaining": 5}
    return post


# 1) _post: IncompleteRead -> unjudged_transport (resendable); RemoteDisconnected (an OSError) still propagates
try:
    def cut(*a, **k):
        raise http.client.IncompleteRead(b"x" * 69702, 2684239)
    hb_timed._open = cut
    r = hb_timed._post({"op": "submit"})
    assert r["error"] == "unjudged_transport" and hb_timed._unjudged(r) and hb_timed._transient(r), r

    def dropped(*a, **k):
        raise http.client.RemoteDisconnected("closed")
    hb_timed._open = dropped
    try:
        hb_timed._post({"op": "submit"})
        raise AssertionError("RemoteDisconnected must propagate (the full submit owns its one resend)")
    except ConnectionError:
        pass
finally:
    restore()
print("ok  _post: IncompleteRead -> unjudged_transport (resent by _submit); RemoteDisconnected still raises")

# 2) _localize: a set whose submits blow up stays in that set; the others are still narrowed + fixed
truth = {"s1.a-expansion": "percent", "s1.b-x": "1", "s2.a-expansion": "percent", "s2.b-x": "2"}
answers = {"s1.a-expansion": "delayed", "s1.b-x": "1", "s2.a-expansion": "delayed", "s2.b-x": "2"}
groups = {"s1": {k: answers[k] for k in answers if k.startswith("s1.")},
          "s2": {k: answers[k] for k in answers if k.startswith("s2.")}}
try:
    hb_timed._vocab = lambda: {"-expansion": ["delayed", "percent", "for_indirect"]}
    sent = []
    good = gm(truth, sent)

    def post(payload, timeout=None):
        if any(k.startswith("s1.") for k in payload.get("answers") or {}):
            raise TimeoutError("timed out")       # every set-1 submit: no verdict
        return good(payload, timeout)
    hb_timed._post = post
    out = {}
    hb_timed._localize("c", answers, groups, {"s1": {"result": "incorrect"}, "s2": {"result": "incorrect"}},
                       {"deadline": None}, out)
    assert out["fixed"] == {"s2.a-expansion": "percent"}, out
    assert out["localize_complete"] is False and out.get("localize_error") and out.get("localize_unjudged"), out
    assert ["s2.a-expansion", "delayed"] in out["wrong"] and not any(w[0].startswith("s1.") for w in out["wrong"]), out
finally:
    restore()
print("ok  _localize: set 1's submits time out -> set 2 still narrowed + fixed; incomplete + error recorded, s1 not wrong")

# 3) label hints: TT's fixes are recorded per family + rejected value and tried FIRST on the next attempt
chal = TMP / "challenges" / "day99" / "x"
(chal / "solver").mkdir(parents=True)
try:
    hb_timed.HW = TMP
    hb_timed._CTX.solver_dir = "challenges/day99/x/solver"
    hb_timed._vocab = lambda: {"-expansion": ["for_indirect", "call_double", "percent", "delayed"]}
    tt_truth = {"t.a-expansion": "percent"}
    sent = []
    hb_timed._post = gm(tt_truth, sent)
    out = {}
    tt_ans = {"t.a-expansion": "delayed"}
    hb_timed._localize("c", tt_ans, {"t": dict(tt_ans)}, {"t": {"result": "incorrect"}}, {"deadline": None}, out)
    assert out["fixed"] == {"t.a-expansion": "percent"} and len(sent) == 3, sent   # for_indirect, call_double, percent
    h = json.loads((chal / "label_hints.json").read_text())
    assert h == {"-expansion": {"delayed": {"percent": 1}}}, h
    sent.clear()
    m_truth = {"m.a-expansion": "percent", "m.b-expansion": "for_indirect"}
    m_ans = {"m.a-expansion": "delayed", "m.b-expansion": "call_double"}
    hb_timed._post = gm(m_truth, sent)
    out = {}
    hb_timed._localize("c", m_ans, {"m1": {"m.a-expansion": "delayed"}, "m2": {"m.b-expansion": "call_double"}},
                       {"m1": {"result": "incorrect"}, "m2": {"result": "incorrect"}}, {"deadline": None}, out)
    assert out["fixed"] == m_truth, out
    first_alt = [s for s in sent if list(s) == ["m.a-expansion"] and s["m.a-expansion"] != "delayed"][0]
    assert first_alt["m.a-expansion"] == "percent", sent     # hinted value first, not vocab order
    h = json.loads((chal / "label_hints.json").read_text())
    assert h["-expansion"]["delayed"]["percent"] == 2 and h["-expansion"]["call_double"]["for_indirect"] == 1, h
finally:
    restore()
print("ok  label_hints.json: TT delayed->percent recorded, Mastery tries `percent` first; hints accumulate per value")

# 4) attempt bank: saved for a failed attempt, merged across reconnects, reapplied only for the SAME attempt, dropped on pass
try:
    hb_timed.HW = TMP
    hb_timed._bank_save({"cid": "c/mastery", "attempt_id": "A1", "result": "incorrect", "verified": {"x": "1"}})
    hb_timed._bank_save({"cid": "c/mastery", "attempt_id": "A1", "result": "incorrect", "verified": {"y": "2"},
                         "partial_fixed": {"z": "3"}})
    assert hb_timed._bank_load("c/mastery", "A1") == {"x": "1", "y": "2", "z": "3"}
    assert hb_timed._bank_load("c/mastery", "A2") == {} and hb_timed._bank_load("c/mastery", None) == {}
    hb_timed._bank_save({"cid": "c/mastery", "attempt_id": "A2", "result": "incorrect", "verified": {"q": "9"}})
    assert hb_timed._bank_load("c/mastery", "A1") == {} and hb_timed._bank_load("c/mastery", "A2") == {"q": "9"}
    hb_timed._bank_save({"cid": "c/mastery", "attempt_id": "A2", "result": "correct", "verified": {"q": "9"}})
    assert not hb_timed._bank_path("c/mastery").exists()
finally:
    restore()
print("ok  attempt bank: merge across reconnects, same-attempt only, a new attempt replaces it, removed on CORRECT")

# 5) orchestrate._cut_short: reconnect only for an untimed, banked, unfinished localization
base = {"result": "incorrect", "attempt_id": "A", "verified": {"x": "1"}, "deadline": None, "run_for_time": False}
assert orchestrate._cut_short({**base, "localize_complete": False, "localize_error": "IncompleteRead()"})
assert orchestrate._cut_short({**base, "localize_complete": True, "wrong": [["a", "d"]], "fixed": {"a": "p"}})
assert not orchestrate._cut_short({**base, "localize_complete": True, "wrong": [["a", "d"]], "fixed": {}})  # real gap
assert not orchestrate._cut_short({**base, "localize_complete": False, "deadline": "2026-10-15T13:00:00Z"})  # clocked
assert not orchestrate._cut_short({**base, "localize_complete": False, "run_for_time": None})   # pool unknown
assert not orchestrate._cut_short({**base, "localize_complete": False, "verified": {}})          # nothing banked
assert not orchestrate._cut_short({**base, "result": "solver_incomplete", "localize_complete": False})
print("ok  _cut_short: untimed + banked + (unfinished | all fixed) -> reconnect; a real gap / clock / no bank -> generalize")

# 5b) timed_stage (Mastery): a cut-short attempt reconnects (op=resume) with no generalize; a real gap generalizes;
#     the TT gate: untimed TT fixes -> Mastery now, clocked TT fixes -> generalize BEFORE the first Mastery attempt
from hctf import timed  # noqa: E402

ch = object.__new__(orchestrate.Chain)
ch.base, ch.sdir = "b", TMP
ch.entries = {"time_trial": {"id": "b/time_trial"}, "mastery": {"id": "b/mastery"}}
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
calls, gen, last = [], [], {}
patches = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (timed, "last_result"): lambda cid: last.get(cid, {}),
    (timed, "join_capture"): lambda cid, t=120: 0,
    (orchestrate.time, "sleep"): lambda s: None,
    (orchestrate.Chain, "generalize"): lambda self, cid, wrong=None, fixed=None, diag=None: gen.append((cid, diag)),
    (orchestrate.Chain, "_await_probes"): lambda self, w: True,
    (orchestrate.Chain, "_late_probes"): lambda self, cid, wait=False, defer_compound=False: {},
    (orchestrate.Chain, "_mastery_speed_gate"): lambda self, cid: None,
    (orchestrate.Chain, "_early_kw"): lambda self, cid, untimed=False: {},
    (orchestrate.Chain, "_early_join"): lambda self, cid: False,
}


def stage_run(results, mastery_last):
    it = iter(results)

    def run(cid, sdir, log=None, **k):
        calls.append(k.get("op", "start"))
        r = next(it)
        last[cid] = mastery_last if r != "correct" else {"result": "correct"}
        return r
    patches[(timed, "run")] = run
    saved = {k: getattr(*k) for k in patches}
    ch._pre_attempt_done, ch._tt_gate_done = True, False
    try:
        for (mod, name), fn in patches.items():
            setattr(mod, name, fn)
        return ch.timed_stage("mastery")
    finally:
        for (mod, name), fn in saved.items():
            setattr(mod, name, fn)


untimed_pool = {"deadline": None, "run_for_time": False, "attempt_id": "M1", "verified": {"x": "1"}}
cut_m = {**untimed_pool, "result": "incorrect", "localize_complete": False, "localize_error": "IncompleteRead()",
         "wrong": [["set1.a-expansion", "delayed"]], "fixed": {"set1.a-expansion": "percent"}}
gap_m = {**untimed_pool, "result": "incorrect", "localize_complete": True, "wrong": [["set1.a-expansion", "delayed"]],
         "fixed": {}}
last.clear(), calls.clear(), gen.clear()
assert stage_run(["blocked", "correct"], cut_m) is True
assert calls == ["start", "resume"] and not gen, (calls, gen)
last.clear(), calls.clear(), gen.clear()
assert stage_run(["blocked", "blocked", "blocked", "correct"], cut_m) is True
assert calls == ["start", "resume", "resume", "resume"] and len(gen) == 1, (calls, gen)   # 2 continues, then generalize
last.clear(), calls.clear(), gen.clear()
assert stage_run(["blocked", "correct"], gap_m) is True and len(gen) == 1, (calls, gen)   # a real gap: generalize
tt_fixed = {"result": "correct", "wrong": [["a-expansion", "delayed"]], "fixed": {"a-expansion": "percent"}}
last.clear(), calls.clear(), gen.clear()
last["b/time_trial"] = {**tt_fixed, "deadline": None, "run_for_time": False}
assert stage_run(["correct"], {}) is True and not gen and calls == ["start"], (calls, gen)
last.clear(), calls.clear(), gen.clear()
last["b/time_trial"] = {**tt_fixed, "deadline": "2026-10-15T13:01:20Z", "run_for_time": True}
assert stage_run(["correct"], {}) is True and gen == [("b/mastery", {"tt_inwindow_fixes": 1})], gen
print("ok  timed_stage: cut short -> op=resume, no generalize (2 continues max); real gap -> generalize; "
      "TT gate: untimed -> Mastery now, clocked -> generalize first")

# 6) replay: the real D15 script Mastery variant (5 sets x ~1026 fields, 21 wrong expansions), one reply cut off
REL = "challenges/day15/scripting-crumb-trail/mastery"
d = next((r / REL for r in (ROOT, Path.home() / "huntress-2026") if (r / REL / "attempts/7fbfc526/result.json").exists()),
         None)
if d is not None and (d / "last_timed.json").exists():
    first = json.loads((d / "attempts/7fbfc526/result.json").read_text())["submitted"]
    truth = json.loads((d / "last_timed.json").read_text())["verified"]
    if set(first) == set(truth):
        try:
            hb_timed.HW = TMP
            hb_timed._CTX.solver_dir = "challenges/day99/x/solver"
            (chal / "label_hints.json").write_text(json.dumps({"-expansion": {"delayed": {"percent": 8}}}))  # D15 TT
            hb_timed._vocab = lambda: {"-expansion": ["for_indirect", "call_double", "percent", "delayed"]}
            sent = []
            hb_timed._post = gm(truth, sent, cut=(3,))
            grp = {}
            for k, v in first.items():
                grp.setdefault(hb_timed._setkey(k), {})[k] = v
            out = {"result": "incorrect"}
            hb_timed._localize("c", first, grp, {k: {"result": "incorrect"} for k in grp}, {"deadline": None}, out)
            nwrong = sum(first[k] != truth[k] for k in first)
            assert out["localize_complete"] and len(out["fixed"]) == nwrong == len(out["wrong"]), \
                (out["localize_complete"], len(out["fixed"]), nwrong, out.get("localize_errors"))
            assert out.get("unjudged_resends", 0) >= 1, out.get("unjudged_resends")
            assert hb_timed._resubmit_fixed("c", first, {"deadline": None, "answer_ids": list(truth)}, out)
            assert out["result"] == "correct", out.get("resubmit_fixed")
            print(f"ok  D15 replay: {nwrong} wrong fixed in-attempt despite a cut-off reply, resubmit CORRECT "
                  f"({len(sent)} submits)")
        finally:
            restore()
    else:
        print("skip D15 replay: data shape changed")
else:
    print("skip D15 replay: no D15 script Mastery data here (rehearsal)")

shutil.rmtree(TMP, ignore_errors=True)
print("ALL PASS")
