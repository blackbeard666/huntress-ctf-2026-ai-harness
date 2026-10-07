"""Behavior checks for the Day 7 harness fixes (offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_day7_fixes.py      (exit 0 = all pass)
"""
import os
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hctf import orchestrate, remote, timed, triage  # noqa: E402
from lib.common import find_artifact  # noqa: E402

# 1) find_artifact: a bundle zip saved under its FIRST member's name ('blob-01.txt') resolves to that member, not to
#    the whole zip (warmups Mastery set1 answered from the bundle's raw bytes); other members and real .zip names keep
#    their old behavior.
d = Path(tempfile.mkdtemp())
with zipfile.ZipFile(d / "blob-01.txt", "w") as z:
    for i in (1, 2, 3):
        z.writestr(f"blob-0{i}.txt", f"01\tbody {i}\n")
with zipfile.ZipFile(d / "evidence.zip", "w") as z:
    z.writestr("evidence.zip", b"inner")
    z.writestr("readme.txt", b"x")
assert find_artifact(d, "blob-01.txt") == b"01\tbody 1\n", find_artifact(d, "blob-01.txt")[:8]
assert find_artifact(d, "blob-03.txt") == b"01\tbody 3\n"
assert find_artifact(d, "evidence.zip")[:2] == b"PK", "a .zip artifact name must still return the zip itself"
print("ok  find_artifact: bundle saved as 'blob-01.txt' -> member blob-01.txt; .zip names unchanged")

# 2) _clock_expiry: a GM-judged wrong answer is the SOLVER even when the clock then ran out.
base = {"result": "expired", "phases": {"solve": 0.2}}
cases = [
    ({}, True),                                                        # answered everything, clock ran out
    ({"missing": ["set3.message"]}, False),                            # solver left a field empty
    ({"full_result": "incorrect"}, False),                             # full submit judged wrong
    ({"per_set": {"set1": {"result": "incorrect"}, "set2": {"result": "accepted"}}}, False),
    ({"per_set": {"set1": {"result": "accepted"}, "set2": {"result": "expired"}}}, True),
]
_orig_last = timed.last_result
try:
    for extra, want in cases:
        timed.last_result = lambda cid, _r={**base, **extra}: _r
        assert orchestrate.Chain._clock_expiry("c") is want, (extra, want)
finally:
    timed.last_result = _orig_last
print("ok  _clock_expiry: false on missing / full incorrect / any per-set incorrect; true on a pure clock expiry")

# 3) timed_stage: pure clock expiries are RETRIED (up to CLOCK_RETRIES), not blocked after the first one.
ch = object.__new__(orchestrate.Chain)
ch.base, ch.entries, ch.sdir = "b", {"mastery": {"id": "b/mastery"}}, d
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
results = iter(["expired", "expired", "expired", "correct"])
calls = []
patches = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (timed, "run"): lambda cid, sdir, log=None: (calls.append(cid), next(results))[1],
    (timed, "last_result"): lambda cid: {"result": "expired", "phases": {"solve": 0.1}, "window": 9, "in_window": 9.2},
    (orchestrate.time, "sleep"): lambda s: None,
}
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert ch.timed_stage("mastery") is True and len(calls) == 4, calls
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
print("ok  timed_stage: 3 clock expiries retried, 4th attempt correct (no block after the first expiry)")

# 4) binary recon: bundled JVM library classes are skipped (and counted) BEFORE the 400-file cap; app classes kept.
r = Path(tempfile.mkdtemp())
(r / "app_x" / "kotlin" / "collections").mkdir(parents=True)
for i in range(450):
    (r / "app_x" / "kotlin" / "collections" / f"K{i:03}.class").write_bytes(b"\xca\xfe\xba\xbe")
(r / "app_x" / "zApp.class").write_bytes(b"\xca\xfe\xba\xbe")      # sorts AFTER 'kotlin/': lost under the old cap
out = "\n".join(triage._recon("binary-reverse-engineering-x", r))
assert "skipped 450 bundled library .class files: kotlin/ x450" in out, out[:300]
assert "zApp.class" in out and "K000.class" not in out, out[:300]
print("ok  binary recon: 450 kotlin/ classes skipped + counted; the app class survives the cap")

# 5) hb_timed: a download 429 / error body is NEVER returned as evidence bytes (Day 7 script TT saved
#    '{"error":"rate_limited"}' as evidence.zip -> a 2-min generalize on a solver that was fine); a POST verdict
#    (409 prerequisite_required JSON) is still returned for the caller to classify.
from hctf import hb_timed  # noqa: E402


class _FakePool:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), 0

    def request(self, method, query, body=None, headers=None):
        self.calls += 1
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


_orig_pool, _orig_sleep = hb_timed._POOL, hb_timed.time.sleep
hb_timed.time.sleep = lambda s: None
try:
    hb_timed._POOL = _FakePool([(429, b'{"error":"rate_limited"}')])
    try:
        hb_timed._get_bytes("ab" * 32)
        raise AssertionError("a 429 download must raise, not return the error body")
    except hb_timed.GMError as e:
        assert e.rate_limited and hb_timed._POOL.calls == 4, (e, hb_timed._POOL.calls)   # 3 backoffs + final
    hb_timed._POOL = _FakePool([(429, b"x"), (200, b"PK\x03\x04real-bytes")])
    assert hb_timed._get_bytes("ab" * 32) == b"PK\x03\x04real-bytes", "a transient 429 is retried"
    hb_timed._POOL = _FakePool([(200, b'{"error":"rate_limited"}')])
    try:
        hb_timed._get_bytes("ab" * 32)
        raise AssertionError("an error body served with 200 is not bytes")
    except hb_timed.GMError as e:
        assert e.rate_limited
    hb_timed._POOL = _FakePool([(409, b'{"error":"prerequisite_required"}')])
    assert b"prerequisite_required" in hb_timed._open("POST", "", b"{}"), "POST verdicts are still returned"
finally:
    hb_timed._POOL, hb_timed.time.sleep = _orig_pool, _orig_sleep
print("ok  hb_timed: download 429/error body raises GMError(rate_limited); transient 429 retried; POST verdict kept")

# 6) classification + timed_stage: a GM rate limit is transient -> back off + retry on its own budget, never generalize.
_orig = (timed._remember, timed._keep_failed_attempt, timed.capture_case)
timed._remember = timed._keep_failed_attempt = lambda *a, **k: None
timed.capture_case = lambda *a, **k: None
try:
    assert timed.process_result("c/time_trial", d, {"result": "exec_error", "gm_rate_limited": True,
                                                    "detail": "download failed"}, log=lambda *a: None) == "error:rate"
    assert timed.process_result("c/time_trial", d, {"result": "rate_limited"}, log=lambda *a: None) == "error:rate"
    assert timed.process_result("c/time_trial", d, {"result": "exec_error", "detail": "ssh"},
                                log=lambda *a: None) == "error:exec"
finally:
    timed._remember, timed._keep_failed_attempt, timed.capture_case = _orig
results = iter(["error:rate", "error:rate", "correct"])
calls, slept = [], []
patches[(timed, "run")] = lambda cid, sdir, log=None: (calls.append(cid), next(results))[1]
patches[(orchestrate.time, "sleep")] = lambda s: slept.append(s)
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert ch.timed_stage("mastery") is True and len(calls) == 3 and slept[:2] == [5, 10], (calls, slept)
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
print("ok  rate limit: classified error:rate; timed_stage backs off 5s, 10s and retries (no generalize)")

# 7) routing: Homebase is used for a KNOWN roomy window too (Day 7 script TT: 11s window ran local, 9.53s in-window).
from hctf import workers, remote  # noqa: E402
_o = (remote.gm_transport, workers.known_window, workers._homebase_ready, workers.run_hb_timed, workers.run_timed)
used = []
remote.gm_transport = lambda: "local"
workers.known_window = lambda cid: 11.0
workers._homebase_ready = lambda log=print: True
workers.run_hb_timed = lambda *a, **k: (used.append("hb"), {"result": "correct"})[1]
workers.run_timed = lambda *a, **k: (used.append("local"), {"result": "correct"})[1]
try:
    r = workers.run_timed_auto("sdir", "c/time_trial", log=lambda *a: None)
    assert used == ["hb"] and r["routed"].startswith("homebase"), (used, r)
    used.clear()
    workers._homebase_ready = lambda log=print: False
    workers.run_timed_auto("sdir", "c/time_trial", log=lambda *a: None)
    assert used == ["local"], used
finally:
    remote.gm_transport, workers.known_window, workers._homebase_ready, workers.run_hb_timed, workers.run_timed = _o
print("ok  routing: known 11s window -> Homebase when healthy; local only as the fallback")

# 8) harvest yields to another chain's live clock (process-wide in-flight count), but never forever.
import threading  # noqa: E402
import time as _t  # noqa: E402
_oi, _oy, _og = timed.inflight, orchestrate.HARVEST_YIELD_MAX, orchestrate.HARVEST_GAP
orchestrate.HARVEST_GAP, orchestrate.HARVEST_YIELD_MAX = -2, 1.0
state = {"n": 1}
timed.inflight = lambda: state["n"]
try:
    threading.Timer(0.6, lambda: state.update(n=0)).start()
    t0 = _t.time()
    assert orchestrate.Chain._harvest_sleep(None, threading.Event()) is True
    assert 0.5 <= _t.time() - t0 < 1.2, _t.time() - t0                  # waited for the live clock to end
    state["n"] = 1
    t0 = _t.time()
    assert orchestrate.Chain._harvest_sleep(None, threading.Event()) is True
    assert _t.time() - t0 < 1.6                                          # bounded by HARVEST_YIELD_MAX
    ev = threading.Event(); ev.set()
    assert orchestrate.Chain._harvest_sleep(None, ev) is False           # generalize already done
finally:
    timed.inflight, orchestrate.HARVEST_YIELD_MAX, orchestrate.HARVEST_GAP = _oi, _oy, _og
print("ok  harvest: waits out another chain's live timed attempt (bounded), stops when the generalize ends")

# 9) lane helpers carry Day 7's new branches (so tomorrow's worker imports instead of re-typing them).
from lib import android as _android, decode as _decode  # noqa: E402
assert _android.decode_payload("caesar", "KX]7BKPOK?>:CCP=;:@O", 10) == "ANS-8AFEA54099F3106E"   # GM-confirmed D7
assert _decode.decode_chunk("%2d%69%73%6c%61%6e%64%2d%70%65%74%61%6c%2d%37%35") == "-island-petal-75"
assert _decode.decode_chunk("TmljZSB3b3JrIGRlY29k") == "Nice work decod"                             # b64 unchanged
print("ok  lane helpers: lib.android caesar (every code point - key), lib.decode url %XX")

# 10) single prompt: lane skill, triage and helper index are inlined; prior solver named only for cumulative lanes.
from hctf import workers as _w  # noqa: E402
assert "decode_payload(" in _w.lane_helpers("mobile-android") and "read_member(" in _w.lane_helpers("warmups")
assert _w.lane_skill("binary-reverse-engineering").startswith("**Installed") and "---" not in _w.lane_skill("warmups")[:5]
_t = (Path(__file__).resolve().parents[1] / "hctf" / "prompts" / "single.md").read_text()
assert all(k in _t for k in ("{skill}", "{triage}", "{lane_helpers}", "{prior_solver}")) and "FIRST call: load" not in _t
_root = Path(__file__).resolve().parents[1]
assert orchestrate.prior_solver_dir("warmups", _root / "challenges/day07/warmups-percent-chance/solver") is None
_ps = orchestrate.prior_solver_dir("script-analysis", _root / "challenges/day07/scripting-node-by-node/solver")
assert _ps is None or (_ps / "solve.py").exists() and _ps.parent.parent.name < "day07"
print("ok  single prompt: skill/triage/helpers inlined; prior same-lane solver only for binary/script")

# 11) submit via Homebase: fall back to the public GM ONLY if the remote command provably never ran (no marker);
#     a failure after it started must NOT trigger a second POST.
import subprocess as _sp  # noqa: E402
from types import SimpleNamespace as _NS  # noqa: E402
_orun, _oal, _oloc = remote.subprocess.run, remote._master_alive, remote._gm_local
remote._master_alive = lambda: True
local_calls = []
remote._gm_local = lambda args, timeout: (local_calls.append(args), {"http": 200, "body": {"result": "correct"}})[1]
try:
    remote.subprocess.run = lambda *a, **k: _NS(returncode=0, stdout='{"http": 200, "body": {"result": "correct"}}\n',
                                                stderr="HCTF-EXEC\n")
    env = remote.gm("submit", "c", '{"a": "1"}')
    assert env["transport"] == "homebase" and not local_calls, (env, local_calls)
    remote.subprocess.run = lambda *a, **k: _NS(returncode=255, stdout="", stderr="ssh: connect refused\n")
    env = remote.gm("submit", "c", '{"a": "1"}')
    assert local_calls == [("submit", "c", '{"a": "1"}')], local_calls          # never ran -> public GM
    local_calls.clear()
    remote.subprocess.run = lambda *a, **k: _NS(returncode=255, stdout="", stderr="HCTF-EXEC\nconnection reset\n")
    try:
        remote.gm("submit", "c", '{"a": "1"}')
        raise AssertionError("a drop after the submit started must not fall back (double POST)")
    except remote.Unreachable:
        assert not local_calls
    def _to(*a, **k):
        raise _sp.TimeoutExpired("ssh", 5, stderr=b"HCTF-EXEC\n")
    remote.subprocess.run = _to
    try:
        remote.gm("submit", "c", '{"a": "1"}')
        raise AssertionError("timeout after start must not fall back")
    except remote.Unreachable:
        assert not local_calls
    remote.subprocess.run = lambda *a, **k: (_ for _ in ()).throw(AssertionError("status must not go via HB"))
    remote.gm("status", "c")                                                     # non-submit ops stay local
    assert local_calls == [("status", "c")]
finally:
    remote.subprocess.run, remote._master_alive, remote._gm_local = _orun, _oal, _oloc
print("ok  submit via Homebase: no marker -> public fallback; started-then-failed -> Unreachable (no double POST)")

# 12) gm.py reports 429 backoff in the envelope (Day 7 submits took 9.5-18 s with no trace of why).
from hctf import gm as _gm  # noqa: E402
import urllib.error as _ue  # noqa: E402
import io as _io  # noqa: E402
_ourl, _osl = _gm.urllib.request.urlopen, _gm.time.sleep
seq = [429, 429, 200]


class _Resp:
    status = 200
    headers = {"Content-Type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return b'{"result": "CORRECT"}'


def _fake(req, timeout=None):
    code = seq.pop(0)
    if code == 429:
        raise _ue.HTTPError(req.full_url, 429, "Too Many", {}, _io.BytesIO(b"{}"))
    return _Resp()


_gm.urllib.request.urlopen, _gm.time.sleep = _fake, lambda s: None
_gm.STATS.update(retries=0, slept=0.0)
_out = _io.StringIO()
_ostdout, _ostderr = sys.stdout, sys.stderr
sys.stdout, sys.stderr = _out, _io.StringIO()
try:
    _gm.main(["status", "x"])
finally:
    sys.stdout, sys.stderr = _ostdout, _ostderr
    _gm.urllib.request.urlopen, _gm.time.sleep = _ourl, _osl
import json as _json  # noqa: E402
_env = _json.loads(_out.getvalue().strip().splitlines()[-1])
assert _env["retries"] == 2 and _env["slept"] == 6.0 and "elapsed" in _env, _env
print("ok  gm.py: 429 retries + backoff seconds reported in every envelope")

# 13) a replay (HUNTRESS_GAME_MASTER_URL -> local stand-in) never re-routes its submits to the real GM via Homebase.
os.environ["HUNTRESS_GAME_MASTER_URL"] = "http://127.0.0.1:18766"
try:
    assert remote._public_gm() is False
finally:
    del os.environ["HUNTRESS_GAME_MASTER_URL"]
assert remote._public_gm() is True
print("ok  submit via Homebase is skipped when the GM URL is not the public GM (replays)")

# 14) `start` on an already-passed mode returns the FINISHED attempt (no answer_ids, no deadline): hb_timed must ask
#     for a fresh clock (op retry), and 'no_answer_ids' is a runner problem -> retry, never a generalize.
posts = []


def _fake_post(payload, timeout=20):
    posts.append(payload["op"])
    if payload["op"] == "start":
        return {"result": "CORRECT", "questions": [{"id": "answer"}]}
    return {"error": "stop_here"}                      # end main() right after the retry


_op, _opool = hb_timed._post, hb_timed._pool
hb_timed._post, hb_timed._pool = _fake_post, (lambda: None)
_oargv, _ostdout = sys.argv, sys.stdout
sys.argv, sys.stdout = ["hb_timed.py", "c/time_trial", "solver"], _io.StringIO()
try:
    hb_timed.main()
finally:
    sys.argv, sys.stdout = _oargv, _ostdout
    hb_timed._post, hb_timed._pool = _op, _opool
assert posts == ["start", "retry"], posts
timed._remember = timed._keep_failed_attempt = lambda *a, **k: None
_occ = timed.capture_case
timed.capture_case = lambda *a, **k: None
try:
    assert timed.process_result("c/time_trial", d, {"result": "no_answer_ids"}, log=lambda *a: None) == "error:exec"
finally:
    timed._remember, timed._keep_failed_attempt, timed.capture_case = _orig[0], _orig[1], _occ
print("ok  start on a passed mode -> op retry for a fresh clock; no_answer_ids -> error:exec (no generalize)")

# 15) GM 'rotation_exhausted' is terminal: stop the stage, never generalize (replay d7fix3 burned 5 workers on it).
timed._remember = timed._keep_failed_attempt = lambda *a, **k: None
timed.capture_case = lambda *a, **k: None
try:
    assert timed.process_result("c/time_trial", d, {"result": "rotation_exhausted"}, log=lambda *a: None) == "error:exhausted"
finally:
    timed._remember, timed._keep_failed_attempt, timed.capture_case = _orig[0], _orig[1], _occ
calls = []
patches[(timed, "run")] = lambda cid, sdir, log=None: (calls.append(cid), "error:exhausted")[1]
saved = {k: getattr(*k) for k in patches}
_ogen = getattr(orchestrate.Chain, "generalize", None)
orchestrate.Chain.generalize = lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not generalize"))
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert not ch.timed_stage("mastery") and len(calls) == 1, calls
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
    orchestrate.Chain.generalize = _ogen
print("ok  rotation_exhausted: one attempt, stage stops, no generalize")

# 16) harvest: `start` after the failed attempt's deadline RESUMES it ({"result": "expired"}, no attempt_id) -> re-roll
#     with op retry (rehearsal Day 7 fair run: both script harvests stopped on 'start refused' with 0 variants). A real GM
#     error (rotation_exhausted) still stops the harvest without a retry.
import contextlib  # noqa: E402

_STARTED = {"attempt_id": "abcdef1234", "deadline": None, "answer_ids": ["a"], "questions": [{"id": "a"}]}
for first, want_ops, want_refused in (
        ({"http": 200, "body": {"result": "expired", "name": "x"}}, ["start", "retry"], False),
        ({"http": 200, "body": {"result": "CORRECT", "name": "x"}}, ["start", "retry"], False),
        ({"http": 409, "body": {"error": "rotation_exhausted"}}, ["start"], True)):
    ops, said = [], []

    def _fake_call(cid, op, *a, _first=first, **k):
        ops.append(op)
        return _first if op == "start" else {"http": 200, "body": dict(_STARTED)}
    hp = {(orchestrate.cli, "call"): _fake_call,
          (orchestrate.cli, "chal_lock"): lambda cid: contextlib.nullcontext(),
          (orchestrate.cli, "_planned_downloads"): lambda body: [],
          (orchestrate.cli, "load"): lambda *a, **k: None,
          (timed, "last_result"): lambda cid: None,
          (orchestrate.Chain, "_harvest_sleep"): staticmethod(lambda deadline, done: True),
          (orchestrate, "ROOT"): d,
          (orchestrate, "say"): lambda msg, *a, **k: said.append(msg)}
    hsaved = {k: getattr(*k) for k in hp}
    try:
        for (mod, name), fn in hp.items():
            setattr(mod, name, fn)
        hc = object.__new__(orchestrate.Chain)
        hc.root, hc.sdir = d, d
        hc._harvest("c/time_trial", 1, set(), __import__("threading").Event())
    finally:
        for (mod, name), fn in hsaved.items():
            setattr(mod, name, fn)
    assert ops == want_ops, (first, ops)
    assert any("start refused" in s for s in said) is want_refused, said
print("ok  harvest: expired/finished start -> retry for a fresh variant; rotation_exhausted -> stop, no retry")

# 17) _accept_or_restore reuses the watcher's green suite result when the solver code + case set are unchanged (alt
#     Day 7: a second full run added 5-10 s between "green" and the retry); any change -> a fresh run.
gd = Path(tempfile.mkdtemp())
(gd / "solver" / "cases" / "c1").mkdir(parents=True)
(gd / "solver" / "solve.py").write_text("print('{}')\n")
gc = object.__new__(orchestrate.Chain)
gc.base, gc.root, gc.sdir, gc._baseline = "b", gd, gd / "solver", {"c1"}
_ots, _osay = orchestrate.solvers.test_solver, orchestrate.say
runs = []
orchestrate.solvers.test_solver = lambda *a, **k: (runs.append(1), [{"case": "c1", "ok": True}])[1]
orchestrate.say = lambda *a, **k: None
try:
    for touch, want_runs in ((False, 0), (True, 1)):
        runs.clear()
        (gd / ".generalize-snapshot").mkdir(exist_ok=True)
        gc._green_res = (gc._solver_mtimes(), gc._case_names(), [{"case": "c1", "ok": True}])
        if touch:
            (gd / "solver" / "cases" / "c2").mkdir()  # harvest added a case after the watcher's run
        gc._accept_or_restore("b/time_trial")
        assert len(runs) == want_runs and not (gd / ".generalize-snapshot").exists(), (touch, runs)
        assert gc._green_res is None
finally:
    orchestrate.solvers.test_solver, orchestrate.say = _ots, _osay
print("ok  accept: reuses the watcher's green result on identical code + cases; reruns the suite otherwise")

# 18) re-attempts go straight to op retry once the mode's previous attempt is over (rehearsal Day 7 script Mastery: start ->
#     expired -> retry cost a 5.1 s start phase); a live/unknown previous attempt keeps op start; hb_timed falls back
#     to start when the GM refuses a retry.
import datetime as _dt  # noqa: E402

past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
future = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
for prev, want in (({"attempt_id": "x", "deadline": past}, "retry"), ({"attempt_id": "x", "deadline": future}, "start"),
                   (None, "start"), ({"deadline": past}, "start")):
    seen = []
    p18 = dict(patches)
    p18[(timed, "run")] = lambda cid, sdir, log=None, op="start": (seen.append(op), "correct")[1]
    p18[(timed, "last_result")] = lambda cid, _p=prev: _p
    s18 = {k: getattr(*k) for k in p18}
    try:
        for (mod, name), fn in p18.items():
            setattr(mod, name, fn)
        assert ch.timed_stage("mastery") and seen == [want], (prev, seen)
    finally:
        for (mod, name), fn in s18.items():
            setattr(mod, name, fn)
posts = []


def _fake_post_retry(payload, timeout=20):
    posts.append(payload["op"])
    return {"error": "no_attempt"} if payload["op"] == "retry" and len(posts) == 1 else {"error": "stop_here"}


hb_timed._post, hb_timed._pool = _fake_post_retry, (lambda: None)
sys.argv, sys.stdout = ["hb_timed.py", "c/time_trial", "solver", "--op", "retry"], _io.StringIO()
try:
    hb_timed.main()
finally:
    sys.argv, sys.stdout = _oargv, _ostdout
    hb_timed._post, hb_timed._pool = _op, _opool
assert posts == ["retry", "start"], posts
print("ok  re-attempt: op retry only when the previous attempt's deadline passed; hb_timed retry refused -> start")

# 19) generalize prompt: the failing file's head + a passing same-named counterpart are inlined (rehearsal Day 7: the script
#     generalize workers spent 4-6 calls reaching them), and the harvest note is built BEFORE render (it used to be
#     appended after the prompt was rendered, so no worker ever saw it).
import inspect  # noqa: E402

ed = Path(tempfile.mkdtemp()) / "solver"
for name, codec in (("single_solve", "base64_literal|"), ("variant-time_trial-abcd1234", "xor_hex|cd")):
    (ed / "cases" / name / "artifacts").mkdir(parents=True)
    with zipfile.ZipFile(ed / "cases" / name / "artifacts" / "evidence.zip", "w") as z:
        z.writestr("indirect-expansion.sh", f"readonly Codec_1='{codec}'\nDecode() {{ :; }}\n")
        z.writestr("other.sh", "echo hi\n")
    (ed / "cases" / name / "contract.json").write_text(__import__("json").dumps({"questions": [
        {"id": "bash-indirect-role", "artifact": "evidence.zip -> indirect-expansion.sh"},
        {"id": "other-role", "artifact": "evidence.zip -> other.sh"}]}))
ev = orchestrate.failing_evidence(ed, "time_trial", ["bash-indirect-role"])
assert "FAILING `evidence.zip -> indirect-expansion.sh`" in ev and "xor_hex|cd" in ev, ev
assert "PASSING counterpart" in ev and "base64_literal|" in ev and "other.sh" not in ev.split("\n", 1)[1], ev
assert orchestrate.failing_evidence(ed, "mastery", ["bash-indirect-role"]) == ""   # no variant case of that mode
assert "{evidence}" in (Path(orchestrate.__file__).parent / "prompts" / "generalize.md").read_text()
gsrc = inspect.getsource(orchestrate.Chain.generalize)
assert gsrc.index("MORE VARIANTS ARRIVE") < gsrc.index('workers.render("generalize"'), "harvest note must precede render"
print("ok  generalize prompt: failing bytes + passing counterpart inlined; harvest note reaches the prompt")

# 20) hctf timeline: per-chain T+ per mode, attempts, generalize cycles, harvest counts from a dayNN.log.
from hctf import timeline  # noqa: E402

_log = """[effort] global=high
23:59:58 [homebase] pre-warming
23:59:59 [s-day-07] single worker -> local (timeout 1500s)
00:00:20 [s-day-07] single CORRECT + solver verified -> ending the worker, timed modes start now
00:00:20 [s-day-07] single worker exit -15 (w.log)
00:00:30 [s-day-07/time_trial] timed: {"result": "solver_incomplete"}
00:00:31 [s-day-07/time_trial] generalize worker -> local (timeout 720s)
00:00:40 [s-day-07/time_trial] harvest: start refused ({'result': 'expired'}); stopping the harvest
00:01:31 [s-day-07/time_trial] generalize worker exit -15 (g.log)
00:01:40 [s-day-07/time_trial] timed: {"result": "correct"}
00:01:40 [s-day-07/time_trial] result: correct
00:01:45 [s-day-07/mastery] timed: {"result": "correct"}
00:01:45 [s-day-07/mastery] result: correct""".splitlines()
_t0, _ch = timeline.parse(_log)
_c = _ch["s-day-07"]
assert {m: v - _t0 for m, v in _c["done"].items()} == {"single_solve": 22, "time_trial": 102, "mastery": 107}, _c["done"]
assert _c["attempts"] == {"single_solve": 0, "time_trial": 2, "mastery": 1} and _c["harvest_refused"] == 1
assert [(s, b - a) for _, s, a, b in _c["workers"]] == [("single", 21), ("generalize", 60)]
print("ok  timeline: midnight wrap, per-mode T+, attempts, worker durations, harvest refusals")
