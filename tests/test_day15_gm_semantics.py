"""GM-semantics checks adopted from a reviewer's single-lane runbook (2026-10-15). Offline: no GM / Homebase / workers.
- A rate_limited / empty / non-JSON reply is UNJUDGED: resent, never "incorrect", never a wrong field.
- Progress = `remaining`: an accepted that does not move it is a re-confirmation.
- Never op=retry an attempt that holds banked ids while it is live: reconnect (op=resume -> start).
- The drop wait is clock-aware (the GM rate limit is shared per token).
- Workers can't run commands that wait forever (.claude/hooks/no_block.py).

Run:  source bin/env.sh && python3 tests/test_day15_gm_semantics.py      (exit 0 = all pass)
"""
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
import hb_timed  # noqa: E402
from hctf import cli, orchestrate  # noqa: E402

hb_timed.UNJUDGED_RESENDS = (0.01, 0.01)
RL = {"error": "rate_limited"}


def deadline(s):
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=s)).isoformat().replace("+00:00", "Z")


def scripted(replies, sent):
    """_post stand-in: replies is a list (consumed in order) or a callable(answers) -> reply."""
    it = iter(replies) if isinstance(replies, list) else None

    def post(payload, timeout=None):
        sent.append(payload)
        return next(it) if it is not None else replies(payload.get("answers") or {})
    return post


_orig = {k: getattr(hb_timed, k) for k in ("_post", "_open", "_post_start", "_pool", "_run_solver", "_post_untimed")}


def restore():
    for k, v in _orig.items():
        setattr(hb_timed, k, v)


# 1) _post: a non-JSON 2xx / an HTML 5xx comes back as an unjudged error body instead of crashing the attempt
try:
    hb_timed._open = lambda *a, **k: b"<html>bad gateway</html>"
    assert hb_timed._post({"op": "submit"})["error"] == "unjudged_nonjson"
    hb_timed._open = lambda *a, **k: b""
    assert hb_timed._post({"op": "submit"})["error"] == "unjudged_nonjson"

    def raise_rt(*a, **k):
        raise RuntimeError("GM HTTP 502: b'<html>'")
    hb_timed._open = raise_rt
    assert hb_timed._post({"op": "submit"})["error"] == "unjudged_http"
    hb_timed._open = lambda *a, **k: b'{"result": "incorrect"}'
    assert hb_timed._post({"op": "submit"}) == {"result": "incorrect"}
finally:
    restore()
assert hb_timed._unjudged(RL) and hb_timed._unjudged({}) and hb_timed._unjudged(None)
assert not hb_timed._unjudged({"result": "incorrect"}) and not hb_timed._unjudged({"result": "accepted"})
assert hb_timed._transient(RL) and hb_timed._transient({"error": "unjudged_nonjson"})
assert not hb_timed._transient({"error": "unknown_answer_id"})
print("ok  _post: non-JSON / empty / HTML-5xx -> unjudged error body (no crash); classifier + transient split")

# 2) _submit: a 429 is resent and then judged; a deterministic refusal is not resent; a reconfirm is counted
body = {"deadline": deadline(30)}
sent = []
try:
    hb_timed._post = scripted([RL, {"result": "correct", "remaining": 0}], sent)
    out = {}
    r = hb_timed._submit("c", {"a": "1"}, body, out)
    assert r["result"] == "correct" and len(sent) == 2 and out["unjudged_resends"] == 1 and "unjudged" not in out, out
    sent.clear()
    hb_timed._post = scripted([RL, RL, RL], sent)
    out = {}
    r = hb_timed._submit("c", {"a": "1"}, body, out)
    assert hb_timed._unjudged(r) and len(sent) == 3 and out["unjudged"] == ["rate_limited"], (sent, out)
    sent.clear()
    hb_timed._post = scripted([{"error": "unknown_answer_id"}], sent)
    out = {}
    hb_timed._submit("c", {"a": "1"}, body, out)
    assert len(sent) == 1 and out["unjudged"] == ["unknown_answer_id"], out
    sent.clear()
    hb_timed._post = scripted([RL, {"result": "correct"}], sent)
    out = {}
    hb_timed._submit("c", {"a": "1"}, {"deadline": deadline(0.5)}, out)   # no clock left for a resend
    assert len(sent) == 1, sent
    sent.clear()
    hb_timed._post = scripted([{"result": "accepted", "remaining": 5}], sent)
    out = {"gm_remaining": 5}
    hb_timed._submit("c", {"a": "1"}, body, out)
    assert out["reconfirms"] == 1 and out["gm_remaining"] == 5, out
finally:
    restore()
assert hb_timed._progress({"result": "accepted", "remaining": 4}, 5) == "progress"
assert hb_timed._progress({"result": "accepted", "remaining": 5}, 5) == "reconfirm"
assert hb_timed._progress({"result": "accepted", "accepted_ids": ["a"]}) == "progress"
assert hb_timed._progress({"result": "incorrect"}, 5) is None
print("ok  _submit: 429 resent then judged, capped resends, refusals not resent, no resend past the clock, reconfirms")

# 3) _localize: a subset submit the GM never judged leaves those fields UNJUDGED, never wrong
sent = []
try:
    def verdict(a):
        if "set1.b" in a and len(a) == 1:
            return RL                                            # the culprit's own probe is rate-limited
        return {"result": "incorrect"} if "set1.b" in a else {"result": "accepted", "remaining": 3}
    hb_timed._post = scripted(verdict, sent)
    out = {}
    answers = {"set1.a": "1", "set1.b": "2"}
    hb_timed._localize("c", answers, {"set1": dict(answers)}, {"set1": {"result": "incorrect"}}, body, out)
    assert out["wrong"] == [] and out["localize_unjudged"] == ["set1.b"] and not out["localize_complete"], out
    assert out["verified"] == {"set1.a": "1"}, out
finally:
    restore()
print("ok  _localize: an unjudged probe marks the field unjudged (no wrong -> no gm_feedback rejected value)")


# 4) the full attempt: every submit rate-limited -> result 'unjudged' (no per-set wrong, no localize); one set judged
#    incorrect -> localize runs on that set only
def fake_attempt(post_fn, ids=("set1.a", "set2.a"), answers=None, start=None):
    answers = answers or {"set1.a": "1", "set2.a": "2"}
    hb_timed._pool = lambda: object()
    hb_timed._post_start = lambda payload, tries=3: dict(start or {}, answer_ids=list(ids), deadline=deadline(30),
                                                         started_at=deadline(0), attempt_id="att1")
    hb_timed._run_solver = lambda *a, **k: SimpleNamespace(stdout=json.dumps(answers), stderr="", returncode=0)
    hb_timed._post = post_fn
    return hb_timed.run_attempt("test/gm_semantics", "challenges/none/solver", op="start")


sent = []
try:
    out = fake_attempt(scripted(lambda a: RL, sent))
    assert out["result"] == "unjudged" and out["bad_sets"] == [] and "wrong" not in out, out
    assert all(v["result"] == "unjudged" for v in out["per_set"].values()), out
    sent.clear()
    out = fake_attempt(scripted(lambda a: RL if len(a) == 2 else (
        {"result": "incorrect"} if "set2.a" in a else {"result": "accepted", "remaining": 1}), sent))
    assert out["result"] == "incorrect" and out["bad_sets"] == ["set2"] and out["wrong"] == [["set2.a", "2"]], out
    assert out["verified"] == {"set1.a": "1"}, out
    sent.clear()
    out = fake_attempt(scripted([RL, {"result": "correct", "remaining": 0}], sent))
    assert out["result"] == "correct" and out["unjudged_resends"] == 1, out
finally:
    restore()
print("ok  attempt: all-unjudged -> 'unjudged' (no wrong / no localize); a judged-incorrect set still localizes")

# 5) timed.process_result maps 'unjudged' to the rate backoff (never 'blocked' -> generalize)
from hctf import timed  # noqa: E402
_sv = {k: getattr(timed, k) for k in ("_remember", "_keep_failed_attempt", "capture_case")}
_isc = cli.is_complete
try:
    timed._remember = lambda *a, **k: None
    timed._keep_failed_attempt = lambda *a, **k: None
    timed.capture_case = lambda *a, **k: None
    cli.is_complete = lambda cid: False
    for r in ("unjudged", "unjudged_nonjson"):
        got = timed.process_result("c/mastery", "x", {"result": r, "attempt_id": "a", "phases": {}}, log=lambda *_: None)
        assert got == "error:rate", (r, got)
finally:
    for k, v in _sv.items():
        setattr(timed, k, v)
    cli.is_complete = _isc
print("ok  process_result: unjudged -> error:rate (back off + retry, never a generalize)")

# 6) never retry over banked ids: op=resume reconnects with `start` and never re-rolls a short live clock
sent = []
try:
    hb_timed._pool = lambda: object()
    hb_timed._post_start = lambda payload, tries=3: (sent.append(payload), {
        "answer_ids": ["a"], "attempt_id": "att", "deadline": deadline(2), "started_at": deadline(-28)})[1]
    hb_timed._run_solver = lambda *a, **k: SimpleNamespace(stdout=json.dumps({"a": "1"}), stderr="", returncode=0)
    hb_timed._post = lambda payload, timeout=None: {"result": "correct", "remaining": 0}
    out = hb_timed.run_attempt("test/gm_semantics", "challenges/none/solver", op="resume")
    assert [p["op"] for p in sent] == ["start"] and out.get("resumed_banked") and "rerolled_short" not in out, (sent, out)
finally:
    restore()
pb = orchestrate._prev_banked
assert pb({"attempt_id": "a", "result": "solver_incomplete", "partial_submit": {"result": "accepted"}})
assert pb({"attempt_id": "a", "result": "incorrect", "verified": {"x": "1"}})
assert pb({"attempt_id": "a", "result": "incorrect", "per_set": {"set1": {"result": "accepted"}}})
assert not pb({"attempt_id": "a", "result": "correct", "verified": {"x": "1"}})
assert not pb({"attempt_id": "a", "result": "incorrect", "per_set": {"set1": {"result": "incorrect"}}})
assert not pb({})
print("ok  banked guard: op=resume = start, no short-clock re-roll; _prev_banked reads accepted partial/per-set/verified")

# 7) clock-aware drop wait
drop = 1_000_000.0
ri = orchestrate.release_interval
assert ri(drop - 600, drop, 0.3) == orchestrate.RELEASE_HEARTBEAT
assert abs(ri(drop - orchestrate.RELEASE_LEAD - 1, drop, 0.3) - 1) < 1e-6       # lands exactly on T-lead
assert ri(drop - 10, drop, 0.3) == 0.3 and ri(drop - 0.5, drop, 0.3) == orchestrate.RELEASE_POLL_HOT
assert ri(drop + 20, drop, 0.3) == orchestrate.RELEASE_POLL_HOT and ri(drop + 60, drop, 0.3) == 0.3
d0 = dt.datetime(2026, 10, 15, 20, 50)
assert dt.datetime.fromtimestamp(orchestrate._drop_instant(d0)) == dt.datetime(2026, 10, 15, 21, 0)
assert dt.datetime.fromtimestamp(orchestrate._drop_instant(dt.datetime(2026, 10, 15, 21, 10))).day == 15  # late arm
assert dt.datetime.fromtimestamp(orchestrate._drop_instant(dt.datetime(2026, 10, 15, 22, 0))).day == 16
print("ok  release_interval: heartbeat until T-lead, poll, hot poll T-1..T+30, late arm keeps today's drop")

# 8) cli bisect: an unjudged probe is never "bad"
_sub, _conf = cli.submit, cli.confirmed_answers
try:
    cli.confirmed_answers = lambda cid, *a: {}
    cli.submit = lambda cid, g, **k: ("error", {"error": "rate_limited"}, [])
    assert cli._bisect_rejected("c", {"a": "1", "b": "2"}, families=False) == set()
    cli.submit = lambda cid, g, **k: ("incorrect" if "b" in g else "accepted", {}, [])
    assert cli._bisect_rejected("c", {"a": "1", "b": "2"}, families=False) == {"b"}
finally:
    cli.submit, cli.confirmed_answers = _sub, _conf
print("ok  bisect: unjudged probes leave fields unjudged; real rejections still isolate the field")

# 9) worker hook: commands that wait forever are refused (workers only), bounded/normal ones pass
H = ROOT / ".claude" / "hooks" / "no_block.py"
env = dict(os.environ, HCTF_CHAL="test/x")
for cmd, want in [("tail -f x.log", 2), ("timeout 20 tail -f x.log", 0), ("sleep 30", 2), ("sleep 1", 0),
                  ("cat f | less", 2), ("python3", 2), ("python3 - <<'EOF'\nsleep 9\nEOF", 0), ("curl https://x", 2),
                  ("curl --max-time 20 https://x", 0), ("ssh hb ls", 2), ("nc -lvnp 9", 2), ("read x", 2),
                  ("cat f | while read l; do echo $l; done", 0), ("7z x a.7z </dev/null", 0), ("echo 'unbal", 0)]:
    r = subprocess.run([sys.executable, str(H)], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}),
                       capture_output=True, text=True, env=env)
    assert r.returncode == want, (cmd, r.returncode, r.stderr)
r = subprocess.run([sys.executable, str(H)], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "sleep 99"}}),
                   capture_output=True, text=True, env={k: v for k, v in os.environ.items() if k != "HCTF_CHAL"})
assert r.returncode == 0
settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
assert any("no_block.py" in h["command"] for e in settings["hooks"]["PreToolUse"] for h in e["hooks"])
print("ok  no_block hook: pagers / follows / REPLs / listeners / untimed curl+ssh / long sleeps refused; registered")
print("ALL OK")
