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
_o = (remote.gm_transport, workers.known_window, workers._homebase_ready, workers.run_hb_timed, workers.run_timed,
      workers.AUTO_HOMEBASE)
used = []
workers.AUTO_HOMEBASE = True   # the routing rule under test, whatever this copy's bin/env.sh says (alt: Homebase off)
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
    (remote.gm_transport, workers.known_window, workers._homebase_ready, workers.run_hb_timed, workers.run_timed,
     workers.AUTO_HOMEBASE) = _o
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

# 21) name-agnostic decode (rehearsal Day 7 review: a name table that silently returns nothing on an unknown name is what
#     costs a generalize cycle). lib.android: renamed/unknown puzzle codecs decode via decode_any() with the ANS answer
#     shape as the oracle; lib.decode: unnamed line encodings + a bigram English scorer for rot-N (unigram scoring
#     chose rot16 'Dysu meha tusetydw' over 'Nice work decoding').
import base64 as _b64  # noqa: E402
import codecs as _codecs  # noqa: E402

_ans = "ANS-8AFEA54099F3106E"
_xk = lambda b, k: bytes(x ^ k[i % len(k)] for i, x in enumerate(b))  # noqa: E731
for _name, _data, _key in (("shifted_chars", "".join(chr(ord(c) + 10) for c in _ans), 10),
                           ("b64_reverse", _b64.b64encode(_ans.encode()).decode()[::-1], None),
                           ("xor_b64_v2", _b64.b64encode(_xk(_ans.encode(), b"k3y")).decode(), "k3y"),
                           ("hex_xor", _xk(_ans.encode(), b"\x5a").hex(), "90"),
                           ("decimal_list", ",".join(str(b) for b in _ans.encode()), None)):
    assert _ans in (_android.decode_payload(_name, _data, _key) or ""), _name
assert _android.decode_payload("weird", "hello world") == "hello world"          # no answer anywhere: unchanged
_w7 = "-island-petal-75"
for _enc in (_b64.b64encode(_w7.encode()).decode()[::-1], _b64.b85encode(_w7.encode()).decode(),
             "".join(f"\\u{ord(c):04x}" for c in _w7), "".join(f"&#{ord(c)};" for c in _w7),
             "".join(f"={ord(c):02X}" for c in _w7), _codecs.encode(_w7, "rot13")):
    assert _decode.decode_chunk(_enc) == _w7, (_enc, _decode.decode_chunk(_enc))
for _n in (3, 13, 16, 22):
    assert _decode.decode_chunk(_decode._rot("Nice work decoding", _n)) == "Nice work decoding", _n
assert _decode.decode_chunk(".... . .-.. .-.. ---") == "HELLO"
print("ok  name-agnostic decode: renamed puzzle codecs (ANS oracle), unnamed line encodings, bigram rot-N scorer")

# 22) harvest pacing: retry ~0.5 s after the deadline; a reply carrying the PREVIOUS attempt's id means it is still live
#     (retry/start resume it for free -- verified on a rehearsal copy) -> poll once a second until a new id arrives.
ops, said = [], []
_replies = iter([{"http": 200, "body": {"attempt_id": "old1", "answer_ids": ["a"]}},
                 {"http": 200, "body": {"attempt_id": "old1", "answer_ids": ["a"]}},
                 {"http": 200, "body": dict(_STARTED)}])
_waits = []


class _Done:
    def wait(self, t):
        _waits.append(t)
        return False

    def is_set(self):
        return False


hp = {(orchestrate.cli, "call"): lambda cid, op, *a, **k: (ops.append(op), next(_replies))[1],
      (orchestrate.cli, "chal_lock"): lambda cid: contextlib.nullcontext(),
      (orchestrate.cli, "_planned_downloads"): lambda body: [],
      (orchestrate.cli, "load"): lambda *a, **k: None,
      (timed, "last_result"): lambda cid: {"attempt_id": "old1", "deadline": None},
      (orchestrate.Chain, "_harvest_sleep"): staticmethod(lambda deadline, done: True),
      (orchestrate, "ROOT"): d,
      (orchestrate, "say"): lambda msg, *a, **k: said.append(msg)}
hsaved = {k: getattr(*k) for k in hp}
try:
    for (mod, name), fn in hp.items():
        setattr(mod, name, fn)
    hc = object.__new__(orchestrate.Chain)
    hc.root, hc.sdir = d, d
    hc._harvest("c/time_trial", 1, set(), _Done())
finally:
    for (mod, name), fn in hsaved.items():
        setattr(mod, name, fn)
assert ops == ["start", "start", "start"] and _waits == [1.0, 1.0], (ops, _waits)
assert not any("refused" in s for s in said), said
assert orchestrate.HARVEST_GAP <= 1.0
print("ok  harvest pacing: same attempt id = still live -> poll 1 s until a new variant; gap after deadline <= 1 s")

# 23) generalize evidence: construct census (the codec FAMILY the failing file has used across cases, normalized
#     through lib.codec._spec) + handler pointer (densest solver function mentioning the construct, plan file for the
#     fixture's language first, case generators skipped).
(ed / "bashplan.py").write_text("def analyse(data):\n    return 1\n\n\ndef codec_decode(material, codec):\n"
                                "    # xor_hex, base64_literal: material -> bytes via the declared codec\n    return material\n")
(ed / "batchplan.py").write_text("def expansion_form(b):\n    return 'indirect expansion'\n")
(ed / "make_synthetic.py").write_text("def build():\n    return 'codec material decode xor_hex xor_hex xor_hex'\n")
ev = orchestrate.failing_evidence(ed, "time_trial", ["bash-indirect-role"], lane="script-analysis")
assert "Codec census" in ev and "xor_hex|repeating_key_xor" in ev and "base64_literal|identity" in ev, ev
_hp = ev[ev.index("Solver functions"):].splitlines()
assert "bashplan.py" in _hp[1] and "codec_decode" in _hp[1] and "make_synthetic" not in ev, _hp
assert orchestrate.construct_census(ed, "warmups") == ""
print("ok  generalize evidence: codec family census + handler pointer (bashplan.codec_decode first)")

# 24) codec-family probe (hctf/family.py): lib.codec.encode round-trips every encodable known rep x transform; the
#     probe re-encodes only the failing language's fixtures, outside cases/ (never gates green), and reports misses.
from lib import codec as _codec  # noqa: E402

_plain = "v=1|role=staging|url=https://ex.example/x|campaign_id=X-1"
for _rep, _tr, _key, _sample in (("hex_dash", "single_byte_xor", "5c", "76-3d-31"),
                                 ("decimal_csv", "rolling_xor", "21", "118,61,49"),
                                 ("reversed_base64", "identity", "", None), ("percent_hex", "add_modulo_256", "07", None),
                                 ("hex_compact", "reverse_then_xor", "a1b2", "763d31"), ("xor_hex", "cd", None, "763d31")):
    _m = _codec.encode(_plain, _rep, _tr, _key, _sample)
    assert _m and _codec.decode(_m, _rep, _tr, _key) == _plain, (_rep, _tr, _m)
assert _codec.encode(_plain, "no_such_rep", "identity") is None
assert "FAMILY_PROBE" in dir(orchestrate) and "family_text" in inspect.signature(orchestrate.failing_evidence).parameters
_gsrc = inspect.getsource(orchestrate.Chain.generalize)
assert _gsrc.index("family_probe") < _gsrc.index("ensure_case_and_test"), "probe must start before the baseline replay"
print("ok  codec family: encode() round-trips; probe starts beside the baseline replay, reported not gated")

# 25) speed-only generalize gets an early stop (blind D7 replay: binary 6 s -> 0.3 s by call 7, worker ran to 284 s
#     because every case already PASSED, so targets/fill were empty and the watcher never started).
sd25 = Path(tempfile.mkdtemp()) / "solver"
for n in ("single_solve", "variant-time_trial-aaaa1111", "auto-mastery-x"):
    (sd25 / "cases" / n).mkdir(parents=True)
    __import__("time").sleep(0.02)
_res25 = [{"case": "single_solve", "ok": True, "seconds": 5.9, "unverified": False},
          {"case": "auto-mastery-x", "ok": True, "seconds": 0.4, "unverified": False},
          {"case": "variant-time_trial-aaaa1111", "ok": False, "seconds": 6.1, "unverified": True}]
_t25, _f25 = orchestrate.speed_watch_sets(_res25, sd25, "time_trial")
assert _t25 == {"single_solve"} and _f25 == {"variant-time_trial-aaaa1111"}, (_t25, _f25)
assert orchestrate.speed_watch_sets(_res25, sd25, "mastery")[1] == set()
_g25 = inspect.getsource(orchestrate.Chain.generalize)
assert "speed_watch_sets" in _g25 and _g25.index("speed_watch_sets") < _g25.index("watch.start()")

# 26) single-time speed gate: a verified-but-slow single solver -> one speed generalize BEFORE the first timed attempt
#     (no attempt spent; blind D7 replay burned a TT attempt + ~30 s on it), at most once per chain.
gen_calls, seen26 = [], []
p26 = dict(patches)
p26[(timed, "run")] = lambda cid, sdir, log=None, op="start": (seen26.append(op), "correct")[1]
p26[(timed, "last_result")] = lambda cid: None
s26 = {k: getattr(*k) for k in p26}
_ogen26 = orchestrate.Chain.generalize
orchestrate.Chain.generalize = lambda self, cid, wrong=None, fixed=None, diag=None: gen_calls.append((cid, diag))
try:
    for (mod, name), fn in p26.items():
        setattr(mod, name, fn)
    ch._single_slow, ch._pre_attempt_done = 5.9, False
    assert ch.timed_stage("mastery") and ch.timed_stage("mastery")
finally:
    for (mod, name), fn in s26.items():
        setattr(mod, name, fn)
    orchestrate.Chain.generalize = _ogen26
assert len(gen_calls) == 1 and gen_calls[0][1] == {"solver_too_slow": True, "single_seconds": 5.9}, gen_calls
assert seen26 == ["start", "start"]
_said26 = []
_osay26, orchestrate.say = orchestrate.say, lambda m, *a, **k: _said26.append(m)
try:
    ch._note_single_speed("c", 1.2)
    assert ch._single_slow is None
    ch._note_single_speed("c", 5.9)
    assert ch._single_slow == 5.9 and "speed generalize" in _said26[-1]
finally:
    orchestrate.say = _osay26
print("ok  speed: speed-only generalize watched for speed; slow single -> one speed generalize before the first attempt")

# 27) lib.binary jar helpers (blind D7 replay: a binary solver scanned all ~18k classes of a Kotlin fat jar, 5.9 s):
#     jar_app_classes skips bundled library packages (one list with triage), class_utf8 parses the constant pool.
import io as _io27  # noqa: E402
import struct as _st27  # noqa: E402
from lib import binary as _bin27  # noqa: E402


def _cls27(*strings):
    pool = b"".join(b"\x01" + _st27.pack(">H", len(x)) + x.encode() for x in strings)
    return b"\xca\xfe\xba\xbe\x00\x00\x00\x34" + _st27.pack(">H", len(strings) + 1) + pool + b"\x00" * 8


_buf27 = _io27.BytesIO()
with zipfile.ZipFile(_buf27, "w") as _z:
    _z.writestr("Day07Variant000.class", _cls27("HCFG", "staged"))
    _z.writestr("kotlin/collections/ArraysKt.class", _cls27("x"))
    _z.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
    _inner = _io27.BytesIO()
    with zipfile.ZipFile(_inner, "w") as _zi:
        _zi.writestr("app/Inner.class", _cls27("inner"))
        _zi.writestr("java/lang/Fake.class", _cls27("y"))
    _z.writestr("lib/app-core.jar", _inner.getvalue())
_apps27 = _bin27.jar_app_classes(_buf27.getvalue())
assert [n for n, _ in _apps27] == ["Day07Variant000.class", "lib/app-core.jar!app/Inner.class"], _apps27
assert _bin27.class_utf8(_apps27[0][1]) == ["HCFG", "staged"] and _bin27.class_utf8(b"not a class") == []
assert triage._JVM_LIB is _bin27.JVM_LIBRARY
from hctf import workers as _w27  # noqa: E402
assert "jar_app_classes(" in _w27.lane_helpers("binary-reverse-engineering")
print("ok  lib.binary: jar_app_classes skips bundled libraries (nested jars too), class_utf8 parses the pool")

# 28) Homebase transfers (blind2 replay, ~130 KB/s VPN): (a) a non-pass result with no new attempt (rotation_exhausted,
#     rate limit, start errors) never pulls the remote tmp-timed dir (13 MB of stale Mastery evidence took ~100 s);
#     (b) a passed attempt's background capture pull waits until no timed attempt / solver push is in flight.
from hctf import workers as _w28  # noqa: E402

assert _w28.needs_variant_pull({"result": "solver_incomplete", "attempt_id": "a1"})
assert _w28.needs_variant_pull({"result": "incorrect", "attempt_id": "a1"})
for _r in ({"result": "rotation_exhausted", "attempt_id": None}, {"result": "exec_error"},
           {"result": "exec_error", "attempt_id": "a1", "gm_rate_limited": True},
           {"result": "no_answer_ids", "attempt_id": "a1"}):
    assert not _w28.needs_variant_pull(_r), _r
_t28 = __import__("time")
_ws = _t28.time()
timed._inflight = 1
_th = __import__("threading").Timer(0.6, lambda: setattr(timed, "_inflight", 0))
_th.start()
timed.wait_idle(max_wait=5, poll=0.05)
_waited = _t28.time() - _ws
assert 0.5 <= _waited < 2, _waited
timed._inflight = 1
_ws = _t28.time()
timed.wait_idle(max_wait=0.3, poll=0.05)            # capped: a capture is delayed, never lost
assert _t28.time() - _ws < 1
timed._inflight = 0
_src = inspect.getsource(timed.process_result)
assert _src.index("wait_idle()") < _src.index("pull()")
print("ok  Homebase transfers: no pull without a new attempt; background captures wait for an idle VPN (capped)")

# 29) hb_timed submit: bounded by the clock (+1.5 s grace), never resent (blind3: a hung GM submit took 40.7 s = the
#     pool's 20 s socket timeout + one resend, for an 11 s window, and could have POSTed the answers twice).
import socket as _sock29  # noqa: E402
import threading as _thr29  # noqa: E402

_hits29 = []
_srv29 = _sock29.socket()
_srv29.bind(("127.0.0.1", 0))
_srv29.listen(5)


def _hang29():
    while True:
        try:
            conn, _ = _srv29.accept()
        except OSError:
            return
        _hits29.append(conn.recv(65536)[:4])   # read the request, never answer
        _thr29.Timer(5, conn.close).start()


_thr29.Thread(target=_hang29, daemon=True).start()
_p29 = hb_timed._Pool(f"http://127.0.0.1:{_srv29.getsockname()[1]}", size=1)
_t0 = time.time() if "time" in dir() else __import__("time").time()
try:
    _p29.request("POST", "", b"{}", {}, timeout=0.6)
    raise AssertionError("a hung submit must raise")
except OSError:
    pass
_dt29 = __import__("time").time() - _t0
assert _dt29 < 1.5, _dt29
__import__("time").sleep(0.2)
assert [h for h in _hits29 if h] == [b"POST"], _hits29   # exactly one POST (b"" = an idle pooled socket closed)
_srv29.close()
import datetime as _dt_29  # noqa: E402
_soon = (_dt_29.datetime.now(_dt_29.timezone.utc) + _dt_29.timedelta(seconds=3)).isoformat().replace("+00:00", "Z")
_gone = (_dt_29.datetime.now(_dt_29.timezone.utc) - _dt_29.timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
assert 4.0 <= hb_timed._submit_timeout({"deadline": _soon}) <= 4.6
assert hb_timed._submit_timeout({"deadline": _gone}) == 2.0 and hb_timed._submit_timeout({}) == 20.0
print("ok  hb_timed submit: bounded by the clock + 1.5 s, one POST only, raises -> 'expired' (clock retry)")

# 30) codec-family probe BEFORE the first timed attempt (blind2/blind3: TT passed clean, then Mastery met the next bash
#     codec every run). Misses on judgeable languages -> family-* cases adopted + one pre-attempt generalize (merged with
#     the speed gate); no calibration -> nothing pre-emptive; noise languages (VBScript) never trigger it.
gen30 = []
p30 = dict(patches)
p30[(timed, "run")] = lambda cid, sdir, log=None, op="start": "correct"
p30[(timed, "last_result")] = lambda cid: None
s30 = {k: getattr(*k) for k in p30}
_og30 = orchestrate.Chain.generalize
orchestrate.Chain.generalize = lambda self, cid, wrong=None, fixed=None, diag=None: gen30.append(diag)
fam30 = Path(tempfile.mkdtemp()) / "sh" / "family-1"
fam30.mkdir(parents=True)
(fam30 / "expected.json").write_text("{}")
(fam30 / "contract.json").write_text("{}")
ch.sdir = Path(tempfile.mkdtemp()) / "solver"
(ch.sdir / "cases").mkdir(parents=True)
try:
    for (mod, name), fn in p30.items():
        setattr(mod, name, fn)
    ch._single_slow, ch._pre_attempt_done = 4.0, False
    ch._family_pre_result = lambda: ("probe: 3/5 reproduced", [str(fam30)])
    assert ch.timed_stage("mastery")
    assert gen30 == [{"solver_too_slow": True, "single_seconds": 4.0, "family_pre": "probe: 3/5 reproduced"}], gen30
    assert (ch.sdir / "cases" / "family-sh-1" / "expected.json").exists()
    gen30.clear()
    ch._single_slow, ch._pre_attempt_done = None, False
    ch._family_pre_result = lambda: ("", [])
    assert ch.timed_stage("mastery") and gen30 == []
finally:
    for (mod, name), fn in s30.items():
        setattr(mod, name, fn)
    orchestrate.Chain.generalize = _og30
    del ch._family_pre_result
ch._fam_noise_fut = None
assert ch._family_noise() is None                       # no calibration -> never pre-emptive
_fut30 = __import__("concurrent.futures").futures.Future()
_fut30.set_result({"noise": ["vbs"], "ratio": {"vbs": 0.3, "sh": 1.0}})
ch._fam_noise_fut = _fut30
assert ch._family_noise() == {"vbs"}
print("ok  family pre-probe: misses -> family-* adopted + ONE pre-attempt generalize (merged with speed); none -> none")

# 31) harvest re-roll rule = hb_timed's: an expired/finished attempt needs `retry` even WITH its attempt_id (main's GM
#     keeps the id -> the harvest polled `start` 8x and gave up, mainblind1); live attempts are left alone. GM calls in
#     the harvest are bounded and the accept waits at most HARVEST_JOIN_MAX for it.
_past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(seconds=5)).isoformat().replace("+00:00", "Z")
_live = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(seconds=8)).isoformat().replace("+00:00", "Z")
assert orchestrate.attempt_over({"result": "expired", "attempt_id": "x1", "answer_ids": ["a"]})
assert orchestrate.attempt_over({"attempt_id": "x1", "answer_ids": ["a"], "deadline": _past})
assert orchestrate.attempt_over({"result": "CORRECT", "name": "n"}) and orchestrate.attempt_over({"name": "n"})
assert not orchestrate.attempt_over({"attempt_id": "x1", "answer_ids": ["a"], "deadline": _live})
assert not orchestrate.attempt_over({"error": "rotation_exhausted"})
ops = []
hp = {(orchestrate.cli, "call"): lambda cid, op, *a, **k: (ops.append((op, k.get("timeout"))), {
          "http": 200, "body": {"result": "expired", "attempt_id": "old1", "answer_ids": ["a"]} if op == "start"
          else dict(_STARTED)})[1],
      (orchestrate.cli, "chal_lock"): lambda cid: contextlib.nullcontext(),
      (orchestrate.cli, "_planned_downloads"): lambda body: [],
      (orchestrate.cli, "load"): lambda *a, **k: None,
      (timed, "last_result"): lambda cid: {"attempt_id": "old1", "deadline": None},
      (orchestrate.Chain, "_harvest_sleep"): staticmethod(lambda deadline, done: True),
      (orchestrate, "ROOT"): d, (orchestrate, "say"): lambda *a, **k: None}
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
assert [o for o, _ in ops] == ["start", "retry"], ops
assert all(t == orchestrate.HARVEST_CALL_TIMEOUT for _, t in ops), ops
assert "reaper.join(timeout=HARVEST_JOIN_MAX)" in inspect.getsource(orchestrate.Chain.generalize)
print("ok  harvest: expired-with-id -> retry (no 8x poll); bounded GM calls; accept waits <= HARVEST_JOIN_MAX")
