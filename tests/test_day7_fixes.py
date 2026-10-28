"""Behavior checks for the Day 7 harness fixes (offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_day7_fixes.py      (exit 0 = all pass)
"""
import os
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("HCTF_AUTO_EARLY", "0")   # D23 #2 auto-armed early event: covered by test_d23_postmortem
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
assert orchestrate.prior_solver_dir("metadata-forensics", _root / "challenges/day07/metadata-seven-zip-no-relation/solver") is None   # lane-seeded, not cumulative (warmups/mobile joined binary/script 2026-10-15)
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
# D16 post-mortem: on the REAL GM a CORRECT latest attempt is reported (already_passed), never re-rolled; the re-roll
# stays for replays (local stand-in GM) and HCTF_REROLL_CORRECT=1
os.environ["HCTF_REROLL_CORRECT"] = "1"
sys.argv, sys.stdout = ["hb_timed.py", "c/time_trial", "solver"], _io.StringIO()
try:
    hb_timed.main()
    assert posts == ["start", "retry"], posts
    del os.environ["HCTF_REROLL_CORRECT"]
    posts.clear()
    sys.stdout = _io.StringIO()
    hb_timed.main()
    _passed = _json.loads(sys.stdout.getvalue().strip().splitlines()[-1])
finally:
    os.environ.pop("HCTF_REROLL_CORRECT", None)
    sys.argv, sys.stdout = _oargv, _ostdout
    hb_timed._post, hb_timed._pool = _op, _opool
assert posts == ["start"] and _passed.get("already_passed") and _passed["result"] == "correct", (posts, _passed)
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
_our = orchestrate.UNTIMED_ROUNDS
orchestrate.UNTIMED_ROUNDS = 0   # opt-out path (HCTF_UNTIMED_ROUNDS=0); the untimed fallback: tests/test_untimed_fallback.py
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert not ch.timed_stage("mastery") and len(calls) == 1, calls
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
    orchestrate.Chain.generalize = _ogen
    orchestrate.UNTIMED_ROUNDS = _our
print("ok  rotation_exhausted (HCTF_UNTIMED_ROUNDS=0): one attempt, stage stops, no generalize")

# 16) harvest: `start` after the failed attempt's deadline RESUMES it ({"result": "expired"}, no attempt_id) -> re-roll
#     with op retry (rehearsal Day 7 fair run: both script harvests stopped on 'start refused' with 0 variants). A real GM
#     error (rotation_exhausted) still stops the harvest without a retry.
import contextlib  # noqa: E402

_STARTED = {"attempt_id": "abcdef1234", "deadline": None, "answer_ids": ["a"], "questions": [{"id": "a"}]}
for first, want_ops, want_refused in (
        ({"http": 200, "body": {"result": "expired", "name": "x"}}, ["start", "retry"], False),
        # D16 post-mortem: a CORRECT latest attempt = the mode PASSED (live answer) -> stop, never re-roll it (rehearsal fair
        # D16: the re-roll made Mastery's prerequisite check fail -- latest TT attempt not CORRECT)
        ({"http": 200, "body": {"result": "CORRECT", "name": "x"}}, ["start"], False),
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
print("ok  harvest: expired start -> retry for a fresh variant; CORRECT (mode passed) / rotation_exhausted -> stop")

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
# C1 (D25): the watch sets are computed by _gen_watch_sets (synchronously, or once the async baseline lands) before
# the watcher fills its targets -- speed_watch_sets must still feed it
assert "_gen_watch_sets" in _g25 and _g25.index("_gen_watch_sets") < _g25.index("watch.start()")
assert "watch_sets(" in inspect.getsource(orchestrate.Chain._gen_watch_sets) and "speed_watch_sets" in inspect.getsource(orchestrate.watch_sets)

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
    ch._expect_untimed = lambda: False   # the clock-era gate (a clocked HoF pool); untimed below
    ch._note_single_speed("c", 1.2)
    assert ch._single_slow is None
    ch._note_single_speed("c", 5.9)
    assert ch._single_slow == 5.9 and "speed generalize" in _said26[-1]
    ch._expect_untimed = lambda: True    # D22 post-mortem #2: untimed pool -> no pre-TT speed generalize for 5.9 s
    ch._note_single_speed("c", 5.9)
    assert ch._single_slow is None and "untimed" in _said26[-1], _said26[-1]
finally:
    orchestrate.say = _osay26
    del ch._expect_untimed
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
    ch._family_pre_result = lambda **k: ("probe: 3/5 reproduced", [str(fam30)])
    assert ch.timed_stage("mastery")
    assert gen30 == [{"solver_too_slow": True, "single_seconds": 4.0, "family_pre": "probe: 3/5 reproduced"}], gen30
    assert (ch.sdir / "cases" / "family-sh-1" / "expected.json").exists()
    gen30.clear()
    ch._single_slow, ch._pre_attempt_done = None, False
    ch._family_pre_result = lambda **k: ("", [])
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

# Day 9 ratchet: iter_entries(leaf_ext=SCRIPT_LEAF_EXT) never loads a script/text leaf to sniff for a nested zip
# (Day 9 script Mastery bundle: same 421 entries, 0.81 s -> 0.05 s); the default still recurses into anything PK.
import io as _io, tempfile as _tf, zipfile as _zf
from lib.common import iter_entries as _ie, SCRIPT_LEAF_EXT as _SLE
_inner = _io.BytesIO(); _zf.ZipFile(_inner, "w").writestr("deep.js", "x")
with _tf.TemporaryDirectory() as _d:
    with _zf.ZipFile(Path(_d) / "evidence.zip", "w") as _z:
        _z.writestr("stage.ps1", _inner.getvalue())      # PK bytes behind a script name
    assert "deep.js" in [n for n, _, _ in _ie(_d)] and "deep.js" not in [n for n, _, _ in _ie(_d, leaf_ext=_SLE)]
print("ok  iter_entries: leaf_ext leaves script names lazy (no PBKDF2 sniff); default recursion unchanged")

# Day 9 ratchet: decode_chunk's strict JSON/C escape branch (warmups "Escape Room" line 9 = '"er..."'),
# incl. non-ASCII that the old ASCII-only generic fallback lost to rot-N
from lib.decode import decode_chunk as _dc
_bs = chr(92)
assert _dc('"' + "".join(f"{_bs}u{ord(c):04x}" for c in "er-ripple-76") + '"') == "er-ripple-76"
assert _dc('"' + "".join(f"{_bs}u{ord(c):04x}" for c in "café words here") + '"') == "café words here"
assert _dc("".join(f"{_bs}x{ord(c):02x}" for c in "plain text words")) == "plain text words"
print("ok  decode_chunk: \\uXXXX / \\xXX escape fragments (quoted or bare) decode strictly")

# Day 11 ratchet: decode_chunk's URL-safe base64 branch, '=' dropped (warmups "Safe Travels": 147-char blob,
# len % 4 == 3, so the strict b64 class never fired and the line fell through to rot-N)
import base64 as _b64
_u = _b64.urlsafe_b64encode(b"Nice work? yes>> crisp-starfish-petal-89").decode().rstrip("=")
assert ("-" in _u or "_" in _u) and _dc(_u) == "Nice work? yes>> crisp-starfish-petal-89", _dc(_u)
assert _dc(_b64.b64encode(b"Nice work decoding this warmup!").decode().rstrip("=")) == "Nice work decoding this warmup!"
assert _dc("74686973207761726d75") == "this warmu" and _dc("qrpbqvat") == "decoding"   # hex / rot13 unchanged
print("ok  decode_chunk: unpadded URL-safe base64 (- _ alphabet, no '=') decodes strictly")

# Day 12 ratchet: decode_chunk's plain-REVERSED branch (warmups "Back at You": line 12 = '69-enud-m', whole blob
# '...:retsaM emaG'); rot-N used to win ('69-fove-n'). Forward plain / rot13 fragments unchanged.
assert _dc("69-enud-m") == "m-dune-96" and _dc("21-teggun") == "nugget-12" and _dc("36-yvi-ma") == "am-ivy-63"
assert _dc("56-ztrauq-tesnus-ytsez :retsaM emaG eht ot rewsna tcaxe siht timbus") \
    == "submit this exact answer to the Game Master: zesty-sunset-quartz-65"
assert _dc("x qrpbqvat") == "k decoding" and _dc("-vfynaq-crgny-75") == "-island-petal-75"
print("ok  decode_chunk: plain reversed fragments ('NN-word' slug tail / reversed sentence) read back-to-front")

# Day 13 "Opposite Day": a whole-blob ATBASH line (a<->z mirror) beats every rot-N and the reversal; the best rot-N
# ('ovisx-tviskr-fbvecw-31', rot22) was submitted and REJECTED before the branch existed.
assert _dc("Mrxv dlip wvxlwrmt gsrh dzinfk! Gl hloev, hfynrg gsrh vczxg zmhdvi gl gsv Tznv Nzhgvi: szmwb-xzmwov-jfziga-31") \
    == "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: handy-candle-quartz-31"
print("ok  decode_chunk: Atbash (a<->z mirror) free text competes with rot-N / reversal")

# Day 14 "Seven Steps": a fixed Caesar +7 (decode rot-7) -- line 14 of a Mastery blob is a FOURTH free-text codec beside
# rot13 (2), reversal (12), Atbash (13); registered in lib.decode.FREE_CODECS + lib.warmups_codecs.DAYS. The joint
# assignment also ranks a 3-word adj-noun-noun-NN slug end above a 2-word one (set22 swapped rev/atb on lines 12/13).
from lib.decode import decode_chunked as _dch
from lib import warmups_codecs as _wc
assert _dc("Upjl dvyr kljvkpun aopz dhytbw! Av zvscl, zbitpa aopz lehja huzdly av aol Nhtl Thzaly: khwwly-zwyvba-ivbskly-71") \
    .endswith("Game Master: dapper-sprout-boulder-71")
_b22 = ["TmljZSB3bw==", "ex qrpbq", "696e672074686973",
        "00100000 01110111 01100001 01110010 01101101 01110101 01110000 00100001", "32 84 111 32 115 111 108 118",
        "145 054 040 163 165 142 155 151", "%74%20%74%68%69%73%20%65", "&#120;&#97;&#99;&#116;&#32;&#97;&#110;",
        '"\\u0073\\u0077\\u0065\\u0072\\u0020\\u0074\\u006f\\u0020"', "ORUGKICHMFWWK===", "IE1hc3Rlcjo", "-yvoorg ",
        "kfaaov-g", "byasl-60"]
assert _dch("".join(f"{k:02d}\t{p}\n" for k, p in enumerate(_b22, 1))).endswith("Game Master: groovy-puzzle-turtle-60")
assert _wc.day_codec(14)[1]("Hi ab-cd-ef-12") == "Op hi-jk-lm-12"
print("ok  decode_chunked: Caesar+7 (D14) as a 4th free-text codec; 3-word slug end wins the joint assignment")

# Day 14 "The Shortcut Home": lnk.target_path_windows verified (LinkInfo LocalBasePath, else the IDList path)
from lib import meta as _meta14
assert _meta14.lookup("lnk", "target_path_windows")[0].tier == _meta14.VERIFIED
assert _meta14.parse_field("d14-lnk-001-lnk-target-path-windows", {})[:2] == ("lnk", "target_path_windows")
print("ok  lib.meta: lnk.target_path_windows registered (verified D14)")

# Day 15 "Room Forty-Seven": ROT47 over printable ASCII 33..126 (punctuation spins too) -- a 5th free-text codec
# (lib.decode.FREE_CODECS + lib.warmups_codecs.DAYS day 15), whole-blob branch in decode_chunk (3-word slug end), and the
# speculative 'rot47' registration must not demote the confirmed day-15 entry.
from lib import decode as _dec15
assert _dc("}:46 H@C< 564@5:?8 E9:D H2C>FAP %@ D@=G6[ DF3>:E E9:D 6I24E 2?DH6C E@ E96 v2>6 |2DE6Ci DF??J\\42DE=6\\@A2=\\he") \
    == "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: sunny-castle-opal-96"
assert _wc.day_codec(15)[1]("Master: ab-cd-ef-12") == "|2DE6Ci 23\\45\\67\\`a" and _wc.day_codec(15)[3] is True
assert ("rot47", 15) in [(n, d) for n, d, _f in _dec15._FREE]
_b15 = ["TmljZSB3bw==", "ex qrpb", "64696e67207468", "01101001 01110011 00100000 01110111 01100001 01110010 01101101",
        "117 112 33 32 84 111 32 115", "157 154 166 145 054 040 163", "%75%62%6d%69%74%20%74",
        "&#104;&#105;&#115;&#32;&#101;&#120;&#97;", '"\\u0063\\u0074\\u0020\\u0061\\u006e\\u0073\\u0077"',
        "MVZCA5DPEB2GQ===", "ZSBHYW1lIA", ":retsaM", " grwb-y", "hzrla-j", "@AA6C\\eg"]
_t15 = _dch("".join(f"{k:02d}\t{p}\n" for k, p in enumerate(_b15, 1)))
assert _t15 == "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: " \
    "tidy-basket-copper-68", _t15   # D15 Mastery 81f42697 set1, GM-confirmed
print("ok  decode: ROT47 (D15) as a 5th free-text codec + whole-blob decode_chunk branch")

# Day 15 "A Word to the Wise": ooxml.external_relationship_targets verified (TargetMode=External across all .rels,
# sorted); lib.meta.synthesis.digest_order for the cross-file `metadata-day-NN-synthesis-<algo>-order` id.
import hashlib as _hl15
import io as _io15
import json as _js15
from lib.meta import synthesis as _syn15
assert _meta14.lookup("ooxml", "external_relationship_targets")[0].tier == _meta14.VERIFIED
_buf = _io15.BytesIO()
with zipfile.ZipFile(_buf, "w") as _z:
    _z.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="t/officeDocument" Target="word/document.xml"/></Relationships>')
    _z.writestr("word/_rels/document.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
                'relationships"><Relationship Id="rId9" Type="t/hyperlink" Target="https://example.test/evidence/d8" '
                'TargetMode="External"/><Relationship Id="rId10" Type="t/hyperlink" Target="https://example.test/control"'
                ' TargetMode="External"/></Relationships>')
assert _meta14.answer("d15-ooxml-001-ooxml-external-relationship-targets", {}, _buf.getvalue())[0] \
    == '["https://example.test/control","https://example.test/evidence/d8"]'
_files15 = {"a.txt": b"a", "b.txt": b"b", "c.txt": b"c"}
_q15 = {"question": "Compute the full-file SHA-256 digest of each named file, then submit a compact JSON array of their "
                    'filenames in ascending digest order. Files: ["a.txt","b.txt","c.txt"]'}
assert _syn15.digest_order(_q15, _files15.get) == _js15.dumps(
    sorted(_files15, key=lambda n: _hl15.sha256(_files15[n]).hexdigest()), separators=(",", ":"))
assert _syn15.ID.search("set1.metadata-day-15-synthesis-sha256-order")
print("ok  lib.meta: ooxml.external_relationship_targets (verified D15) + synthesis.digest_order")

# Day 16 "Dot Com": Morse whose symbols spell the HEX digits of the UTF-8 sentence (lib.warmups_codecs.DAYS day 16 exact
# encoder + decode_chunk's Morse branch; the hex reading outranks the equally 'wordy' raw hex digits).
_s16 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: silly-banner-marble-88"
_m16 = _wc.day_codec(16)[1](_s16)
assert _m16.startswith("....- . -.... ----. ") and _wc.day_codec(16)[2](_m16) == _s16 and _wc.day_codec(16)[3] is False
assert _dc(_m16) == _s16 and _dc("... --- ...") == "SOS"   # GM-confirmed D16 single slug
print("ok  decode: Morse-hex (D16) exact encoder + decode_chunk branch")

# Day 16 "Return to Sender": email.message_id verified (Message-ID verbatim, <> kept; GM format token `email`, prebuilt
# eml.py promoted) + resolve() aliases email <-> eml for the remaining speculative eml.* fields.
_e16 = (b"From: a <a@example.test>\r\nTo: b@example.test\r\nMessage-ID: <artifact-assembly-line@example.test>\r\n"
        b"Return-Path: <bounce@example.test>\r\nSubject: hi\r\n\r\nbody\r\n")
assert _meta14.lookup("email", "message_id")[0].tier == _meta14.VERIFIED
assert _meta14.answer("d16-email-001-email-message-id",
                      {"question": "Determine email.message_id for message-001.eml."}, _e16) \
    == ("<artifact-assembly-line@example.test>", _meta14.VERIFIED)
assert _meta14.answer("d17-email-001-email-return-path", {}, _e16) == ("bounce@example.test", _meta14.SPECULATIVE)
assert ("eml", "message_id") not in _meta14.REGISTRY and not _meta14.CONFLICTS
print("ok  lib.meta: email.message_id registered (verified D16) + email<->eml format alias")

# Day 17 "Bacon Bits": each HEX digit of the UTF-8 sentence as a 5-symbol a/b Bacon group (lib.warmups_codecs.DAYS day 17
# exact encoder + decode_chunk's bacon-hex branch); GM-confirmed D17 single slug.
_s17 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: tidy-rocket-harbor-20"
_b17 = _wc.day_codec(17)[1](_s17)
assert _b17.startswith("aabaa abbba aabba abaab ") and _wc.day_codec(17)[2](_b17) == _s17 and _wc.day_codec(17)[3] is False
assert _dc(_b17) == _s17 and _dc(_wc.day_codec(17)[1]("-NN")) == "-NN"
print("ok  decode: Bacon-hex (D17) exact encoder + decode_chunk branch")

# Day 17 "Hear Me Out": media.primary_audio_codec_name verified (ffprobe codec_name of the first audio stream from the
# container header; 16-bit PCM WAV -> pcm_s16le, GM-confirmed).
import struct as _st17
_fmt17 = _st17.pack("<HHIIHH", 1, 1, 8000, 16000, 2, 16)
_w17 = b"RIFF" + _st17.pack("<I", 4 + 8 + len(_fmt17) + 8) + b"WAVE" + b"fmt " + _st17.pack("<I", len(_fmt17)) + _fmt17 \
    + b"data" + _st17.pack("<I", 0)
assert _meta14.lookup("media", "primary_audio_codec_name")[0].tier == _meta14.VERIFIED
assert _meta14.answer("d17-audio-001-media-primary-audio-codec-name",
                      {"question": "Determine media.primary_audio_codec_name for audio-001.wav."}, _w17) \
    == ("pcm_s16le", _meta14.VERIFIED)
print("ok  lib.meta: media.primary_audio_codec_name registered (verified D17)")

# Day 17 "Decoder Ring": hcfg_storage closed enum (base64 / raw_hcfg_section / raw_const_array, GM-confirmed d08-d14) +
# stripped d01 recover_code -> "none" (TT + Mastery); playbook serves both, vocab.json caches the labels.
from lib import knowledge as _K17, playbook as _pb17  # noqa: E402
assert _K17.hcfg_storage("base64") == "base64" and _K17.hcfg_storage("raw", ".hcfg") == "raw_hcfg_section"
assert _K17.hcfg_storage("raw", ".data") == "raw_const_array" and _K17.hcfg_storage("hex", ".rodata") is None
assert set(_pb17.seed_candidates(_pb17.BINARY, "d12_analysis_hcfg_storage")[:len(_K17.HCFG_STORAGE)]) == \
    set(_K17.HCFG_STORAGE)   # the GM later PUBLISHED 5 tokens (+ wasm_data_segment, raw)
# `raw` was wrong for d12/d14 only (their carriers have a better rule); it is the published enum's fallback token
assert "raw" not in _pb17.rejected(_pb17.BINARY, "set2.d14_analysis_hcfg_storage")
assert "hcfg_section" in _pb17.rejected(_pb17.BINARY, "set2.d14_analysis_hcfg_storage")
assert "8114" in _pb17.rejected(_pb17.BINARY, "d01_analysis_recover_code") and _K17.RECOVER_CODE_ABSENT == "none"
assert {"raw_hcfg_section", "raw_const_array"} <= set(_json.load(open(os.path.join(os.path.dirname(_K17.__file__), "vocab.json")))["storage"])
print("ok  knowledge/playbook: D17 hcfg_storage enum + stripped recover_code none")

# Day 18 "Off the Rails" ("Three rails. One very zigzag commute."): classic 3-rail fence (offset 0, spaces are ciphertext)
# -- lib.warmups_codecs.DAYS day 18 exact encoder, a 6th confirmed free-text codec (lib.decode.FREE_CODECS 'rail') and a
# whole-blob decode_chunk branch; GM-confirmed D18 single bytes + slug.
_s18 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: dapper-summit-brook-29"
_r18 = "N kcnhwuTo,b saaeoemararm-o9iewr eoigti amp osle umtti xc nwrt h aeMse:dpe-umtbok2codd sr! vsihets tG t psir-"
assert _wc.day_codec(18)[1](_s18) == _r18 and _wc.day_codec(18)[2](_r18) == _s18 and _wc.day_codec(18)[3] is True
assert _dc(_r18) == _s18 and ("rail", 18) in [(n, d) for n, d, _f in _dec15._FREE]
_l18 = [_wc.day_codec(k)[1](p) for k, p in enumerate([_s18[i:i + 6] for i in range(0, 102, 6)], 1)]
_b18 = "".join(f"{k:02d}\t{p}\n" for k, p in enumerate(_l18 + [_wc.day_codec(18)[1](_s18[102:])], 1))
assert _dch(_b18) == _s18, _dch(_b18)
print("ok  decode: rail fence 3 (D18) exact encoder + free codec + whole-blob decode_chunk branch")

# Day 18 "Frame of Reference": media.primary_video_dimensions verified (coded WxH of the first video stream, MP4 stsd
# visual entry; prebuilt media_video.video_value promoted, GM-confirmed 320x180).
def _bx18(t, body):
    return _st17.pack(">I", 8 + len(body)) + t + body
_stsd18 = _bx18(b"stsd", b"\0" * 4 + _st17.pack(">I", 1) + _bx18(b"avc1", b"\0" * 6 + b"\0\1" + b"\0" * 16
                                                                    + _st17.pack(">HH", 320, 180) + b"\0" * 50))
_mp418 = _bx18(b"ftyp", b"isom\0\0\2\0isom") + _bx18(b"moov", _bx18(b"trak", _bx18(b"mdia", _bx18(
    b"hdlr", b"\0" * 8 + b"vide" + b"\0" * 13) + _bx18(b"minf", _bx18(b"stbl", _stsd18)))))
assert _meta14.lookup("media", "primary_video_dimensions")[0].tier == _meta14.VERIFIED
assert _meta14.answer("d18-video-001-media-primary-video-dimensions",
                      {"question": "Determine media.primary_video_dimensions for video-001.mp4."}, _mp418) \
    == ("320x180", _meta14.VERIFIED)
print("ok  lib.meta: media.primary_video_dimensions registered (verified D18)")

# Day 18 "Orphan Process" (Google Apps Script v=3): bare `// HUNTRESS_ANALYSIS_V1:SPLIT` marker + the material as a
# literal array `["<TAG>-chunk", "chunk", ..].join("")` -> lib.codec.find_codecs / v3_plan read it (35/35 D18 members).
_p18 = "v=3|language=google_apps_script|role=downloader|attack=T1105|campaign_id=GOOGLE_APPS_SCRIPT-0123abcd"
_h18 = "HEX-" + _p18.encode().hex()
_g18 = ("// HUNTRESS_ANALYSIS_V1:SPLIT\nconst HUNTRESS_ANALYSIS_V1_SPLIT_0123abcd = [\n"
        + ",\n".join(f'    "{_h18[i:i + 40]}"' for i in range(0, len(_h18), 40)) + '\n].join("");\n')
assert _codec.v3_plan(_g18) == _p18 and _codec.is_v3(_g18.encode())
print("ok  codec: D18 SPLIT marker + literal-array material (Google Apps Script v=3)")

# Day 19 "Little Things" ("Two bytes walk into a bar. The little one goes first."): lowercase hex of BOM fffe + UTF-16LE
# -- lib.warmups_codecs.DAYS day 19 exact encoder + decode_chunk's hex-of-UTF-16 branch; GM-confirmed D19 single slug.
_s19 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: jaunty-raven-glade-73"
_u19 = _wc.day_codec(19)[1](_s19)
assert _u19.startswith("fffe4e0069006300") and _wc.day_codec(19)[2](_u19) == _s19 and _wc.day_codec(19)[3] is False
assert _dc(_u19) == _s19 and _dc(_s19.encode("utf-16-be").hex()) == _s19 and _dc("4e696365") == "Nice"
print("ok  decode: hex of UTF-16LE (D19) exact encoder + decode_chunk branch")

# Day 20 "Big Entrance" ("Same bar. This time the big one goes first."): lowercase hex of BOM feff + UTF-16BE
# -- lib.warmups_codecs.DAYS day 20 exact encoder; decode_chunk's D19 hex-of-UTF-16 branch reads the BE BOM too.
_s20 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: deft-blanket-clover-43"
_u20 = _wc.day_codec(20)[1](_s20)
assert _u20.startswith("feff004e0069") and _wc.day_codec(20)[2](_u20) == _s20 and _wc.day_codec(20)[3] is False
assert _dc(_u20) == _s20
print("ok  decode: hex of UTF-16BE (D20) exact encoder + decode_chunk branch")

# Day 20 "Universal Appeal": macho.cpu_type_set verified (cputype "0x%08x" per slice, fat_arch order, thin = header;
# GM-confirmed thin arm64 -> ["0x0100000c"], the arch-name list ["arm64"] REJECTED).
_mo20 = b"\xcf\xfa\xed\xfe" + _st17.pack("<II", 0x0100000c, 0) + b"\0" * 20
_fat20 = b"\xca\xfe\xba\xbe" + _st17.pack(">I", 2) + _st17.pack(">5I", 0x01000007, 3, 4096, 32, 12) \
    + _st17.pack(">5I", 0x0100000c, 0, 8192, 32, 14)
assert _meta14.lookup("macho", "cpu_type_set")[0].tier == _meta14.VERIFIED
assert _meta14.answer("d20-macho-001-macho-cpu-type-set",
                      {"question": "Determine macho.cpu_type_set for macos-001.bin."}, _mo20) \
    == ('["0x0100000c"]', _meta14.VERIFIED)
assert _meta14.answer("d20-macho-001-macho-cpu-type-set", {}, _fat20)[0] == '["0x01000007","0x0100000c"]'
print("ok  lib.meta: macho.cpu_type_set registered (verified D20)")

# Day 19 "Little Endian on the Prairie": elf.e_machine_u16_hex verified (e_machine u16 @0x12 in EI_DATA byte order,
# speculative pe.elf_machine promoted; GM-confirmed x86-64 -> 0x003e).
_elf19 = b"\x7fELF\x02\x01\x01" + b"\0" * 9 + _st17.pack("<HH", 2, 0x3e) + b"\0" * 44
assert _meta14.lookup("elf", "e_machine_u16_hex")[0].tier == _meta14.VERIFIED
assert _meta14.answer("d19-elf-001-elf-e-machine-u16-hex",
                      {"question": "Determine elf.e_machine_u16_hex for collector-001.elf."}, _elf19) \
    == ("0x003e", _meta14.VERIFIED)
print("ok  lib.meta: elf.e_machine_u16_hex registered (verified D19)")

# Day 19 "Jack in the Box": final PK19 overlay (+5 k1, +6 k2, +8 u32 len, +12 sha256, +44 packed), unpacked[i] =
# ror8(packed[i] ^ k2, 3) ^ k1 = an HCFG record (lib.binary.overlay_unpack; GM-confirmed config + crc on Single/TT/Mastery).
import hashlib as _hl19  # noqa: E402
_pl19 = _json.dumps({"campaign": "BR19-000"}).encode()
_hc19 = b"HCFG" + _st17.pack("<BBHI", 1, 0, len(_pl19), _bin27.zlib.crc32(_pl19)) + _pl19
_pk19 = bytes(((((b ^ 0x21) << 3) | ((b ^ 0x21) >> 5)) & 255) ^ 0x5a for b in _hc19)   # rol3(b ^ k1) ^ k2
_ov19 = b"\x7fELF" + b"\0" * 60 + b"PK19\0" + bytes([0x21, 0x5a, 0]) + _st17.pack("<I", len(_pk19)) \
    + _hl19.sha256(_hc19).digest() + _pk19
assert _bin27.overlay_unpack(_ov19, "PK19") == _hc19 and _bin27._parse_blob(_hc19)[5]
assert _bin27.overlay_unpack(_ov19, "RS20") is None
print("ok  binary: D19 PK19 packed overlay -> HCFG (overlay_unpack)")

# Day 20 "Resourceful": final RS20 resource overlay (+8 u32le HCFG len, +12 u16le scratch len, +16 sha256(scratch),
# +48 HCFG resource, scratch after it, exact EOF) -> lib.binary.resource_overlay / overlay_unpack(data, "RS20")
# (GM-confirmed config + hcfg_resource_size 380 on Single/TT/Mastery).
_sc20 = b"scratch-bytes"
_rs20 = b"\x7fELF" + b"\0" * 60 + b"RS20" + b"\1\0\0\0" + _st17.pack("<IH", len(_hc19), len(_sc20)) + b"\0\0" \
    + _hl19.sha256(_sc20).digest() + _hc19 + _sc20
_ro20 = _bin27.resource_overlay(_rs20)
assert _ro20["offset"] == 64 and _ro20["hcfg_resource_size"] == len(_hc19) and _ro20["scratch_size"] == len(_sc20)
assert _bin27.overlay_unpack(_rs20, "RS20") == _hc19 and _bin27.resource_overlay(_rs20 + b"x") is None
assert _bin27.resource_overlay(_ov19) is None and _bin27.overlay_unpack(_ov19, "PK19") == _hc19
print("ok  binary: D20 RS20 resource overlay -> HCFG (resource_overlay)")

# Day 21 "Under Pressure" ("A familiar wrapper. Something compressed inside."): std base64 of gzip (mtime 0, XFL 2, OS 3,
# level 9 Z_FILTERED) -- lib.warmups_codecs.DAYS day 21 exact encoder (the Single's own bytes) + decode_chunk's
# base64-of-compressed branch (gzip and zlib); GM-confirmed D21 single slug.
_s21 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: eager-compass-mosaic-50"
_u21 = _wc.day_codec(21)[1](_s21)
assert _u21 == ("H4sIAAAAAAACAyXJMQ7CQAwEwK8sPSfR0PABKqj4gHFWyQkcR7bD8XwKpp17V2J4vDBRferrjFp6YkjYvh3wcKS/Pzwi96f1+i+/ogVZ"
                "czBQjlqIqxhxkyzGBZSZ0dRtk8xmntK1nU8/iFIChW4AAAA=")
assert _wc.day_codec(21)[2](_u21) == _s21 and _wc.day_codec(21)[3] is False
assert _dc(_u21) == _s21 and _dc("H4sIAAAAAAACA8urrNA1NQMA2EdrhAYAAAA=") == "nyx-56"
assert _dc(_b64.b64encode(_bin27.zlib.compress(_s21.encode())).decode()) == _s21
print("ok  decode: base64 of gzip (D21) exact encoder + decode_chunk branch")

# Day 21 "Package Deal": apk.package_name verified (<manifest package> of the binary AndroidManifest.xml, stdlib AXML
# walk; GM-confirmed "com.huntress.arena.p08281778" on single/TT/Mastery).
def _axml21(pkg):
    strs = ["package", "manifest", pkg]
    data = b"".join(_st17.pack("<H", len(s)) + s.encode("utf-16-le") + b"\0\0" for s in strs)
    offs, o = [], 0
    for s in strs:
        offs.append(o)
        o += 2 + 2 * len(s) + 2
    data += b"\0" * (-len(data) % 4)
    sp_hdr = 28
    sp = _st17.pack("<HHIIIIII", 1, sp_hdr, sp_hdr + 4 * len(strs) + len(data), len(strs), 0, 0,
                    sp_hdr + 4 * len(strs), 0) + b"".join(_st17.pack("<I", x) for x in offs) + data
    attr = _st17.pack("<IIIHBBI", 0xFFFFFFFF, 0, 2, 8, 0, 3, 2)
    el = _st17.pack("<HHIII", 0x0102, 16, 16 + 20 + len(attr), 1, 0xFFFFFFFF) \
        + _st17.pack("<IIHHHHHH", 0xFFFFFFFF, 1, 20, 20, 1, 0, 0, 0) + attr
    return _st17.pack("<HHI", 3, 8, 8 + len(sp) + len(el)) + sp + el


_zb21 = _io27.BytesIO()
with zipfile.ZipFile(_zb21, "w") as _z21:
    _z21.writestr("AndroidManifest.xml", _axml21("com.huntress.arena.p08281778"))
assert _meta14.lookup("apk", "package_name")[0].tier == _meta14.VERIFIED
assert _meta14.answer("d21-apk-001-apk-package-name", {"question": "Determine apk.package_name for mobile-001.apk."},
                      _zb21.getvalue()) == ("com.huntress.arena.p08281778", _meta14.VERIFIED)
print("ok  lib.meta: apk.package_name registered (verified D21)")

# Day 21 "Reflect Upon This": the XSS callback is /api/clues `secondary_route` by KEY (single /callback-, TT /internal-)
from lib import knowledge as _K21  # noqa: E402
assert _K21.WEB_XSS_CLUE_ROUTE_KEYS["callback"] == "secondary_route" and "internal" in _K21.WEB_XSS_CALLBACK_ROUTE_WORDS_SEEN
print("ok  knowledge: D21 web XSS callback route picked by clue key")

# Day 22 "Deflated Ego": std padded base64 of zlib (78 da, level 9 Z_FILTERED) -- GM-confirmed single slug, byte-exact
_s22 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: tidy-cloud-tulip-70"
_u22 = _wc.day_codec(22)[1](_s22)
assert _u22 == ("eNolyTEOgzAMBdCr/O5E6obUC3SCiQu4iVUsEoxih5Tbd+Ctb5bI6Fo3JI6aZP/CVzF0qqUdDywK03zyAGufIn4v/yg6aLfOFa7wlfGmwpjI"
                "nOsLLukKMWtLwVuWI4zPPwZ3Jg8=")
assert _wc.day_codec(22)[2](_u22) == _s22 and _wc.day_codec(22)[3] is False and _dc(_u22) == _s22
print("ok  warmups_codecs: D22 base64 of zlib exact encoder")

# Day 22 "Main Character Energy": jar.main_class promoted from prebuilt jar.jar_manifest (verified D22)
_zb22 = _io27.BytesIO()
with zipfile.ZipFile(_zb22, "w") as _z22:
    _z22.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\r\nMain-Class: arena.evidence.Artifact\r\n Main\r\n\r\n")
assert _meta14.lookup("jar", "main_class")[0].tier == _meta14.VERIFIED
assert _meta14.answer("d22-jar-001-jar-main-class", {"question": "Determine jar.main_class for application-001.jar."},
                      _zb22.getvalue()) == ("arena.evidence.ArtifactMain", _meta14.VERIFIED)
print("ok  lib.meta: jar.main_class registered (verified D22)")

# Day 22 web: csrf + upload handlers keyed on ANY clue key (dispatch key was current_user / preview_guide), lib.web
# targets in parallel (module-level job: the old local closure failed every target of a >=2-target contract), and an
# expired target (410 {"state":"completed"}) returns None at once.
import json as _j22  # noqa: E402
import threading as _th22  # noqa: E402
import time as _tm22  # noqa: E402
import urllib.parse as _up22  # noqa: E402
from http.server import BaseHTTPRequestHandler as _BH22, ThreadingHTTPServer as _HS22  # noqa: E402
from lib import web as _web22  # noqa: E402
from lib.web import handlers as _wh22  # noqa: E402


class _H22(_BH22):
    def _send(self, st, body, cookie=None):
        self.send_response(st)
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        u = _up22.urlparse(self.path)
        kind, path, qs = self.server.kind, u.path, _up22.parse_qs(u.query)
        if kind == "dead":
            return self._send(410, '{"state":"completed"}')
        if path == "/api/clues":
            return self._send(200, _j22.dumps(
                {"framework": "x", "current_user": "analyst", "feature_route": "/submit-ab12cd",
                 "preferences_route": "/preferences", "browser_session": "established"} if kind == "csrf" else
                {"feature_route": "/action-ef679c", "framework": "net/http", "preview_guide": "/preview-guide",
                 "render_route": "/internal-a0d2c4", "upload_shape": "POST JSON: filename, content, content_type"}))
        if kind == "csrf" and path == "/preferences":
            return self._send(200, "<p>Current: daily</p><form method='get' action='/submit-ab12cd'><select "
                                   "name=destination><option value=daily><option value='review-7@outside.example."
                                   "invalid'></select><input type=hidden name=csrf_token value=s1></form>",
                              "arena_session=s1; Path=/")
        if kind == "csrf" and path == "/submit-ab12cd":
            xs = self.headers.get("Sec-Fetch-Site") == "cross-site" and "@" in qs.get("destination", [""])[0]
            return self._send(200, "proof_" + "c5" * 16 if xs else '{"changed_across_sites":false}')
        if kind == "up" and path == "/internal-a0d2c4":
            return self._send(200, "proof_" + "a7" * 16 if self.server.notes.get(qs.get("file", [""])[0]) else "no")
        return self._send(404, "nf")

    def do_POST(self):
        body = _j22.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.server.kind == "up" and self.path == "/action-ef679c":
            self.server.notes[body.get("filename", "")] = "{{objective}}" in body.get("content", "")
            return self._send(200, _j22.dumps({"path": "/internal-a0d2c4?file=" + body.get("filename", "")}))
        return self._send(404, "nf")

    def log_message(self, *a):
        pass


class _QS22(_HS22):
    def handle_error(self, request, client_address):
        pass   # a client the parallel solve already abandoned (BrokenPipe): no traceback at interpreter shutdown


_b22, _srv22 = {}, []
for _kind22 in ("csrf", "up", "dead"):
    _s22v = _QS22(("127.0.0.1", 0), _H22)
    _srv22.append(_s22v)
    _s22v.kind, _s22v.notes = _kind22, {}
    _th22.Thread(target=_s22v.serve_forever, daemon=True).start()
    _b22[_kind22] = f"http://127.0.0.1:{_s22v.server_address[1]}/"
_cl22, _k22 = _wh22.websolve.clues(_b22["csrf"])
assert _k22 == "current_user" and [n for n, _ in _wh22.for_key(_k22, _cl22)][0] == "csrf", (_k22, _cl22)
assert _wh22.csrf(_b22["csrf"], _cl22) == "proof_" + "c5" * 16
_cu22, _ku22 = _wh22.websolve.clues(_b22["up"])
assert [n for n, _ in _wh22.for_key(_ku22, _cu22)] == ["upload"], (_ku22, _cu22)
assert _wh22.upload(_b22["up"], _cu22) == "proof_" + "a7" * 16
_c22 = {"answer_ids": ["proof-1", "proof-2", "proof-3"],
        "questions": [{"artifact": "Target 1"}, {"artifact": "Target 2"}, {"artifact": "Target 3"}],
        "targets": [{"id": "Target 1", "url": _b22["csrf"]}, {"id": "Target 2", "url": _b22["up"]},
                    {"id": "Target 3", "url": _b22["dead"]}]}
_t022 = _tm22.time()
assert _web22.solve_target({"artifact": "Target 3"}, _c22) is None and _tm22.time() - _t022 < 3
_o22 = _web22.solve(_c22)
assert _o22 == {"proof-1": "proof_" + "c5" * 16, "proof-2": "proof_" + "a7" * 16}, _o22
for _s22v in _srv22:   # D23: left running, their handler threads printed to stderr during interpreter finalization
    _s22v.shutdown()   # -> "Fatal Python error: _enter_buffered_busy" (rc 134) on some runs
    _s22v.server_close()
print("ok  lib.web: D22 csrf + upload handlers, parallel targets, dead target skipped")

# Day 23 "Eighty-Five Alive": Adobe Ascii85 (<~ ~>) of the UTF-8 sentence -- GM-confirmed single slug, byte-exact
_s23 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: crisp-starfish-quartz-70"
_u23 = _wc.day_codec(23)[1](_s23)
assert _u23 == ("<~:2+3L+EqaECER/!@rGmlDJ()6BPDN1G@>N/F`8KH<,Wn#DesT./0K\"V@Voh$+EV:2F!,%=@:OC%@;^.1ATAo8D]j.8AKXKOD.Oha"
                "@<6O%E]P=QEbTT6/TZ#BEb9$,BJ\"4H@<-I9/N5?~>")
assert _wc.day_codec(23)[2](_u23) == _s23 and _wc.day_codec(23)[3] is False and _dc(_u23) == _s23
print("ok  warmups_codecs: D23 Adobe Ascii85 exact encoder")

# Day 23 "Page Me Maybe": sqlite.page_size_bytes promoted from prebuilt sqlite.sqlite_value (verified D23; 1 = 65536),
# zip CD names and macho fat cputypes SORTED (GM rejected CD / fat_arch order on TT / Mastery)
_sq23 = b"SQLite format 3\0" + _st17.pack(">H", 1) + b"\1\1\0\x40\x20\x20" + b"\0" * 76
assert _meta14.lookup("sqlite", "page_size_bytes")[0].tier == _meta14.VERIFIED
assert ("sqlite", "page_size_bytes") not in _meta14._prebuilt_fields(_meta14.PREBUILT_DIR / "sqlite.py")
assert _meta14.answer("d23-sqlite-001-sqlite-page-size-bytes", {}, _sq23) == ("65536", _meta14.VERIFIED)
assert _meta14.answer("d23-sqlite-001-sqlite-page-size-bytes", {}, _sq23[:16] + b"\x10\0" + _sq23[18:])[0] == "4096"
_fat23 = b"\xca\xfe\xba\xbe" + _st17.pack(">I", 3) + _st17.pack(">5I", 0x0100000c, 0, 4096, 32, 12) \
    + _st17.pack(">5I", 0x0000000c, 9, 8192, 32, 14) + _st17.pack(">5I", 7, 3, 12288, 32, 12)
assert _meta14.answer("d20-macho-001-macho-cpu-type-set", {}, _fat23)[0] == '["0x00000007","0x0000000c","0x0100000c"]'
_zb23 = _io27.BytesIO()
with zipfile.ZipFile(_zb23, "w") as _z23:
    for _n23 in ("room-18/item-5.log", "box-06/part-6.log", "cabinet-10/entry-6.txt"):
        _z23.writestr(_n23, "x")
assert _meta14.answer("d07-zip-001-zip-central-directory-member-names", {}, _zb23.getvalue())[0] \
    == '["box-06/part-6.log","cabinet-10/entry-6.txt","room-18/item-5.log"]'
print("ok  lib.meta: sqlite.page_size_bytes verified D23; zip CD names / macho cpu set sorted (D23)")

# Day 23 "Hook Line and Signal": `codec: analysis` puzzle (no data) -> puzzle_candidates runs the static String methods
# under the deep dex evaluator (Release.code(), 2M steps) instead of stopping on the dex's literal decoy token
from lib import android as _and23  # noqa: E402
_apk23 = Path(__file__).resolve().parent / "data" / "android_fixtures" / "d23_analysis_release_code.apk"
_c23 = [c for c in _and23.puzzle_candidates(str(_apk23)) if _and23.ANS_RE_T.search(c)]
assert _c23 and _c23[0] == "ANS-E4F679E90A7D1CAE" and "ANS-0123456789ABCDEF" not in _c23, _c23
print("ok  android: D23 codec=analysis computed code via dex_eval_scan(deep=True)")

# Day 23 "Press Start to Decode": HUNTRESS_ANALYSIS_V1:LYR-<encode layers>-<material> -> codec.peel_plan undoes the named
# chain last-first (a frag below the top layer, e.g. hex_frag_hex, defeated the generic BFS)
from lib import codec as _cx23  # noqa: E402
import base64 as _b6423  # noqa: E402
_h23 = b"v=3|role=stager|campaign_id=c-1".hex()
_m23 = _b6423.b32encode((_h23[:20] + "." + _h23[20:]).encode()).decode()   # encode order: hex, frag, b32
assert _cx23.peel_plan("hex_frag_b32-" + _m23, "LYR") == "v=3|role=stager|campaign_id=c-1"
assert _cx23.lyr_undo("LYR-hex_frag_b32-" + _m23) == "v=3|role=stager|campaign_id=c-1"
print("ok  codec: D23 LYR-<layers> named chain peel")

# Day 24 "String Theory": warmups line codec = one netstring `1:c,` per character (exact encoder; decode_chunk branch)
_s24 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: jaunty-compass-mosaic-76"
_u24 = _wc.day_codec(24)[1](_s24)
assert _u24.startswith("1:N,1:i,1:c,1:e,1: ,") and "1:,,1: ," in _u24 and _u24.endswith("1:7,1:6,")
assert _wc.day_codec(24)[2](_u24) == _s24 and _wc.day_codec(24)[3] is False and _dc(_u24) == _s24
print("ok  warmups_codecs: D24 netstring exact encoder + decode_chunk")

# Day 24 "Event Horizon": evtx.record_count promoted from prebuilt evtx.record_value (verified D24) -- records walked
# through every physical ElfChnk, NOT the header's next_record_id
def _evtx24(n, nxt):
    hdr = bytearray(4096)
    _st17.pack_into("<8sQQQIHHHH", hdr, 0, b"ElfFile\0", 0, 0, nxt, 128, 1, 3, 4096, 1)
    recs = b"".join(b"**\0\0" + _st17.pack("<IQ", 32, i + 1) + b"\0" * 12 + _st17.pack("<I", 32) for i in range(n))
    chk = bytearray(b"ElfChnk\0" + b"\0" * (0x200 - 8))
    _st17.pack_into("<I", chk, 48, 0x200 + len(recs))
    return bytes(hdr + chk + recs) + b"\0" * (0x10000 - 0x200 - len(recs))
assert _meta14.lookup("evtx", "record_count")[0].tier == _meta14.VERIFIED
assert ("evtx", "record_count") not in _meta14._prebuilt_fields(_meta14.PREBUILT_DIR / "evtx.py")
assert _meta14.answer("d24-evtx-001-evtx-record-count", {}, _evtx24(3, 99)) == ("3", _meta14.VERIFIED)
assert _meta14.answer("d24-evtx-001-evtx-record-count", {}, _evtx24(0, 1))[0] == "0"
print("ok  lib.meta: evtx.record_count verified D24 (physical chunk walk)")
# D24: _prebuilt_fields reads only the `FIELDS = {...}` statement (full ast.parse of every prebuilt module was 0.5 s per
# lane-solver process) -- same dict as the whole-module parse on every prebuilt module
import ast as _ast24  # noqa: E402
for _p24 in sorted(_meta14.PREBUILT_DIR.glob("*.py")):
    _f24 = next((_ast24.literal_eval(n.value) for n in _ast24.parse(_p24.read_text()).body if isinstance(n, _ast24.Assign)
                 and any(isinstance(t, _ast24.Name) and t.id == "FIELDS" for t in n.targets)), {})
    assert _meta14._prebuilt_fields(_p24) == (_f24 if isinstance(_f24, dict) else {}), _p24.name
print("ok  lib.meta: prebuilt FIELDS fast read == full parse")

# Day 25 "You Have a Point": warmups line codec = one `U+XXXX` code point per character (exact encoder; decode_chunk
# branch); Mastery line 25 goes through DAYS positionally (D25: a pre-decoded plain last line was re-"decoded" -> -07)
_s25 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: brave-beacon-wizard-34"
_u25 = _wc.day_codec(25)[1](_s25)
assert _u25.startswith("U+004E U+0069 U+0063 U+0065 U+0020") and _u25.endswith("U+0033 U+0034")
assert _wc.day_codec(25)[2](_u25) == _s25 and _wc.day_codec(25)[3] is False and _dc(_u25) == _s25
_c25 = [_s25[i * len(_s25) // 25:(i + 1) * len(_s25) // 25] for i in range(25)]
_m25 = "\n".join("%02d\t%s" % (k, _wc.day_codec(k)[1](p)) for k, p in enumerate(_c25, 1))
from lib import decode as _dec25  # noqa: E402
assert _dec25.decode_chunked(_m25) == _s25, _dec25.decode_chunked(_m25)
print("ok  warmups_codecs: D25 U+XXXX exact encoder + decode_chunk + Mastery line 25")

# Day 25 "Hive Mind": registry.hive_root_name = the ROOT nk cell's name (base block root cell offset @0x24), not the
# base-block file name
def _regf25(name, fname="renamed.hiv"):
    b = bytearray(0x2000)
    b[:4] = b"regf"
    _st17.pack_into("<I", b, 0x24, 0x20)
    b[48:48 + 2 * len(fname)] = fname.encode("utf-16-le")
    b[0x1000:0x1004] = b"hbin"
    p = 0x1020
    _st17.pack_into("<i2sH", b, p, -0x60, b"nk", 0x2C)
    _st17.pack_into("<H", b, p + 0x4C, len(name))
    b[p + 0x50:p + 0x50 + len(name)] = name.encode("latin-1")
    return bytes(b)
assert _meta14.lookup("registry", "hive_root_name")[0].tier == _meta14.VERIFIED
assert _meta14.answer("d25-registry-001-registry-hive-root-name", {}, _regf25("HuntressArtifactAssemblyLine")) \
    == ("HuntressArtifactAssemblyLine", _meta14.VERIFIED)
assert _meta14.answer("d25-registry-001-registry-hive-root-name", {}, b"CREG" + b"\0" * 600)[0] is None
print("ok  lib.meta: registry.hive_root_name verified D25 (root nk cell name)")

# Day 26 "Food for Thought": warmups line codec = Brainfuck from ONE cell (+/- delta per UTF-8 byte, then '.'), exact
# encoder; decode_chunk branch (a Morse run of '-'/'.' is not Brainfuck); Mastery line 26 through DAYS positionally
_s26 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: happy-comet-blossom-79"
_b26 = _wc.day_codec(26)[1](_s26)
assert _b26.startswith("+" * 78 + "." + "+" * 27 + ".------.++.") and _b26.endswith("-" * 64 + "." + "+" * 10 + ".++.")
assert _wc.day_codec(26)[2](_b26) == _s26 and _wc.day_codec(26)[3] is False and _dc(_b26) == _s26
assert _dc("--... ...-- --...") != _wc.day_codec(26)[2]("+" * 55 + ".")
_c26 = [_s26[i * len(_s26) // 26:(i + 1) * len(_s26) // 26] for i in range(26)]
_m26 = "\n".join("%02d\t%s" % (k, _wc.day_codec(k)[1](p)) for k, p in enumerate(_c26, 1))
assert _dec25.decode_chunked(_m26) == _s26, _dec25.decode_chunked(_m26)
print("ok  warmups_codecs: D26 Brainfuck exact encoder + decode_chunk + Mastery line 26")

# Day 27 "Monkey Business": warmups line codec = the D26 Brainfuck in Ook! token pairs (single spaces), exact encoder;
# decode_chunk branch; Mastery line 27 through DAYS positionally
_s27 = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: hearty-castle-fern-71"
_b27 = _wc.day_codec(27)[1](_s27)
assert _b27.startswith("Ook. Ook. " * 78 + "Ook! Ook. ") and _b27.endswith("Ook! Ook! " * 6 + "Ook! Ook.")
assert _wc.day_codec(27)[2](_b27) == _s27 and _wc.day_codec(27)[3] is False and _dc(_b27) == _s27
_c27 = [_s27[i * len(_s27) // 27:(i + 1) * len(_s27) // 27] for i in range(27)]
_m27 = "\n".join("%02d\t%s" % (k, _wc.day_codec(k)[1](p)) for k, p in enumerate(_c27, 1))
assert _dec25.decode_chunked(_m27) == _s27, _dec25.decode_chunked(_m27)
print("ok  warmups_codecs: D27 Ook! exact encoder + decode_chunk + Mastery line 27")

# Day 26 "Split Decision": a split bundle (.apks = base.apk + feature split) -- the base puzzle's `split` parts have an
# empty slot, the split's json carries `part` + `part_index`; lib.android.puzzle_candidates fills and assembles it
# (GM-confirmed single ANS-7E37D134754DEA01). v2 (`codec: analysis` base reading the split's huntress_feature.bin)
# goes through _dex_eval_deep(assets=...) (GM-confirmed TT ANS-2DF27FDEEFEF5A67, Mastery set10 ANS-BD603675DE19471A).
import io as _io26, zipfile as _zf26  # noqa: E402
def _zip26(entries):
    b = _io26.BytesIO()
    with _zf26.ZipFile(b, "w") as z:
        for n, v in entries.items():
            z.writestr(n, v)
    return b.getvalue()
_apks26 = _zip26({
    "base.apk": _zip26({"assets/huntress_puzzle.json": '{"schema":"huntress.mobile.puzzle.v1","day":26,"codec":"split",'
                        '"data":"","parts":["","ANS-7","E37D13"],"order":[2,0,1]}'}),
    "feature.apk": _zip26({"assets/huntress_feature.json": '{"codec":"split","day":26,"feature":"arena_feature",'
                           '"part":"4754DEA01","part_index":0}'})})
assert _android.puzzle_candidates(_io26.BytesIO(_apks26))[0] == "ANS-7E37D134754DEA01"
assert _android._bundle_apks(_io26.BytesIO(_zip26({"assets/x.json": "{}"}))) == []
print("ok  lib.android: D26 split bundle (.apks) part fill + split-asset deep eval hook")

# Day 26 "Before You Go": prefetch.executable_name = SCCA header name (UTF-16LE @0x10) -- prebuilt prefetch.pf_value
# promoted to verified (single CMD.EXE, TT PACKAGER.EXE, 10/10 Mastery); the key lives in _BUILTIN only
assert _meta14.lookup("prefetch", "executable_name")[0].tier == _meta14.VERIFIED
assert _meta14.lookup("prefetch", "executable_name")[0].days == (26,)
assert ("prefetch", "executable_name") not in _meta14._prebuilt_fields(_meta14.PREBUILT_DIR / "prefetch.py")
_pf26 = bytearray(0x100)
_st17.pack_into("<I4sI", _pf26, 0, 30, b"SCCA", 0x100)
_pf26[16:16 + 14] = "CMD.EXE".encode("utf-16-le")
assert _meta14.answer("d26-prefetch-001-prefetch-executable-name", {}, bytes(_pf26)) == ("CMD.EXE", _meta14.VERIFIED)
assert _meta14.answer("d26-prefetch-001-prefetch-executable-name", {}, b"L\0\0\0" + b"\0" * 200)[0] == "none"
print("ok  lib.meta: prefetch.executable_name verified D26 (SCCA header name, MAM-compressed too)")

# Day 27 "Packet Loss Prevention": pcap.packet_count = complete classic-pcap records -- prebuilt pcap_value promoted
assert _meta14.lookup("pcap", "packet_count")[0].days == (27,)
_pc27 = _st17.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
_pc27 += b"".join(_st17.pack("<IIII", 1, 0, 4, 4) + b"abcd" for _ in range(3)) + _st17.pack("<IIII", 1, 0, 64, 64) + b"x"
assert _meta14.answer("d27-pcap-001-pcap-packet-count", {}, _pc27) == ("3", _meta14.VERIFIED)
assert _meta14.answer("d27-pcap-001-pcap-packet-count", {}, b"PK\3\4" + b"\0" * 60)[0] == "none"
print("ok  lib.meta: pcap.packet_count verified D27 (complete records, truncated tail not counted)")
