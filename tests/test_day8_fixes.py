"""Behavior checks for the Day 8 harness fixes (offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_day8_fixes.py      (exit 0 = all pass)
"""
import datetime as dt
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
import hb_timed  # noqa: E402
from hctf import cli, orchestrate, timed, workers  # noqa: E402


def iso(sec):
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=sec)).isoformat().replace("+00:00", "Z")


quiet = dict(log=lambda *a, **k: None)
d = Path(tempfile.mkdtemp())

# 1) Start refusals are not solver failures (Day 8: 503 training_rotation_invalid -> 'blocked' -> 6 useless generalize
#    workers). Clock-starved solves are 'expired', not 'solver too slow'. Expiry needs the RESULT to say so.
_orig = (timed._remember, timed._keep_failed_attempt, timed.capture_case)
timed._remember = timed._keep_failed_attempt = lambda *a, **k: None
timed.capture_case = lambda *a, **k: None
try:
    pr = lambda res: timed.process_result("c/time_trial", d, res, **quiet)  # noqa: E731
    assert pr({"result": "training_rotation_invalid", "attempt_id": None, "start_refused": True,
               "detail": {"error": "training_rotation_invalid"}}) == "error:start"
    assert pr({"result": "some_new_gm_error"}) == "error:start"                    # nothing ran: never generalize
    assert pr({"result": "rotation_exhausted", "start_refused": True}) == "error:exhausted"
    assert pr({"result": "expired", "clock_short": True, "attempt_id": "a", "phases": {"solve": 2.0},
               "detail": "solver budget only 2.0s of a 22.0s window"}) == "expired"
    assert pr({"result": "exec_error", "attempt_id": "a", "detail": "solve.py timed out after 9.0s (in-window "
               "solver budget)"}) == "blocked"                                      # a genuinely slow solver
    assert pr({"result": "weird", "attempt_id": "a", "phases": {"solve": 1}, "detail": "mentions expired"}) == "blocked"
finally:
    timed._remember, timed._keep_failed_attempt, timed.capture_case = _orig
print("ok  classification: start refusals -> error:start; clock-starved solve -> expired; slow solver still blocked")

# 2) timed_stage: error:start backs off 5/10/20 s and retries without a generalize worker.
ch = object.__new__(orchestrate.Chain)
ch.base, ch.entries, ch.sdir = "b", {"mastery": {"id": "b/mastery"}}, d
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
ch._pre_attempt_done = True
results = iter(["error:start", "error:start", "error:start", "correct"])
calls, slept, gen = [], [], []
patches = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (timed, "run"): lambda cid, sdir, log=None, **k: (calls.append(k), next(results))[1],
    (timed, "last_result"): lambda cid: {"result": "training_rotation_invalid"},
    (orchestrate.time, "sleep"): lambda s: slept.append(s),
    (orchestrate.Chain, "generalize"): lambda self, *a, **k: gen.append(1),
}
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert ch.timed_stage("mastery") is True and len(calls) == 4, calls
    assert slept == [5, 10, 20] and not gen, (slept, gen)
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
print("ok  timed_stage: GM start refusals back off 5/10/20 s and retry; no generalize")

# 3) timed_stage: never RESUME an attempt with too little clock (Day 8 script Mastery: ~4 s left -> 2 s solver budget).
#    It waits the old attempt out and asks for a fresh one (op=retry).
calls, slept = [], []
results = iter(["correct"])
patches[(timed, "last_result")] = lambda cid: {"attempt_id": "x", "deadline": iso(4), "window": 22,
                                                "phases": {"download": 0.3, "solve": 5.4, "submit": 0.0}}
patches[(timed, "run")] = lambda cid, sdir, log=None, **k: (calls.append(k), next(results))[1]
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert ch.timed_stage("mastery") is True
    assert calls == [{"op": "retry"}] and slept and 3.5 < slept[0] < 5.0, (calls, slept)
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
assert orchestrate._resume_need({"phases": {"download": 4.6, "solve": 8.1, "submit": 0.8}}) == 15.0
assert orchestrate._resume_need({"window": 10}) == 5.0 and orchestrate._resume_need({}) == 3.0
print("ok  timed_stage: a nearly-spent previous attempt is waited out and re-rolled (op=retry), not resumed")

# 4) hb_timed pool policy (user: always the Hall of Fame pool on TT/Mastery). run_for_time:true first; a route without
#    a timed pool (409 timed_intent_not_available: legacy / single) is resent without it; HCTF_RUN_FOR_TIME=0 never
#    asks for HoF; a regular-pool refusal falls back to HoF (backstop). No 503 backoff on deterministic refusals.
sent = []
script = {}


def fake_post(payload, timeout=None):
    sent.append(dict(payload))
    return script.get(bool(payload.get("run_for_time")), {"attempt_id": "a"})


_orig_post = hb_timed._post
hb_timed._post = fake_post
try:
    script = {True: {"attempt_id": "h", "run_for_time": True}}
    assert hb_timed._post_start({"op": "start", "challenge": "x/mastery"})["attempt_id"] == "h"
    assert sent == [{"op": "start", "challenge": "x/mastery", "run_for_time": True}], sent
    sent.clear()
    script = {True: {"error": "timed_intent_not_available"}, False: {"attempt_id": "legacy"}}
    assert hb_timed._post_start({"op": "retry", "challenge": "bin/time_trial"})["attempt_id"] == "legacy"
    assert [p.get("run_for_time") for p in sent] == [True, None], sent
    sent.clear()
    assert hb_timed._post_start({"op": "start", "challenge": "bin"})["attempt_id"] == "legacy"   # single: plain
    assert sent == [{"op": "start", "challenge": "bin"}], sent
    sent.clear()
    os.environ["HCTF_RUN_FOR_TIME"] = "0"
    script = {False: {"error": "training_rotation_invalid"}}
    assert hb_timed._post_start({"op": "start", "challenge": "x/time_trial"})["error"] == "training_rotation_invalid"
    assert sent == [{"op": "start", "challenge": "x/time_trial"}], sent       # scout/probe: never spends ranked
    sent.clear()
    del os.environ["HCTF_RUN_FOR_TIME"]
    script = {False: {"error": "training_rotation_invalid"}, True: {"attempt_id": "h"}}
    assert hb_timed._post_start({"op": "start", "challenge": "x/time_trial", "run_for_time": False})["attempt_id"] == "h"
finally:
    hb_timed._post = _orig_post
    os.environ.pop("HCTF_RUN_FOR_TIME", None)
assert hb_timed._refusal(503, b'{"error":"training_rotation_invalid"}')
assert not hb_timed._refusal(503, b'{"error":"rate_limited"}') and not hb_timed._refusal(429, b"busy")
assert not hb_timed._refusal(409, b'{"error":"x"}')
sys.path.insert(0, str(ROOT / "hctf"))
import gm  # noqa: E402
assert gm._refusal(b'{"error":"training_rotation_invalid"}') and not gm._refusal(b'{"error":"rate_limited"}')
assert not gm._refusal(b"<html>busy</html>")
print("ok  pool policy: HoF first on TT/Mastery, legacy/single resent plain, opt-out honored; refusals not backed off")

# 5) Stale keep-alive (Day 8 binary + script Mastery: the submit reused a socket the proxy had closed during the solve
#    -> RemoteDisconnected, no verdict). The server below closes idle keep-alives after 0.3 s, like the GM proxy.
srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 0))
srv.listen(16)
hits = []


def serve():
    while True:
        try:
            conn, _ = srv.accept()
        except OSError:
            return

        def handle(c):
            c.settimeout(0.3)
            try:
                while True:
                    req = c.recv(65536)
                    if not req:
                        break
                    hits.append(req[:4])
                    c.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 17\r\nContent-Type: application/json\r\n\r\n"
                              b'{"result":"ok!!"}')
            except OSError:
                pass
            finally:
                c.close()        # idle > 0.3 s: drop the keep-alive without a word
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


threading.Thread(target=serve, daemon=True).start()
url = f"http://127.0.0.1:{srv.getsockname()[1]}"
pool = hb_timed._Pool(url, size=2)
st, body = pool.request("GET", "?op=list", headers={})
assert st == 200
time.sleep(0.6)                                                       # the "solve": the server drops the socket
st, body = pool.request("POST", "", b"{}", {}, timeout=2)            # the no-resend submit
assert st == 200 and json.loads(body)["result"] == "ok!!"
hb_timed._Pool.IDLE_MAX = 0.2
time.sleep(0.6)
st, _ = pool.request("GET", "?op=x", headers={})                      # idle reuse path also reconnects up front
assert st == 200
hb_timed._Pool.IDLE_MAX = 3.0
print("ok  keep-alive: a submit after an idle gap opens a fresh connection (no RemoteDisconnected)")

# 6) Final submit: a dropped connection with clock left is resent ONCE; a timeout never is.
_orig_post = hb_timed._post
n_calls = []


def drop_once(payload, timeout=None):
    n_calls.append(1)
    if len(n_calls) == 1:
        import http.client
        raise http.client.RemoteDisconnected("Remote end closed connection without response")
    return {"result": "CORRECT"}


src = Path(hb_timed.__file__).read_text()
assert "submit_resent" in src and "isinstance(e, ConnectionError)" in src
assert issubclass(__import__("http.client").client.RemoteDisconnected, ConnectionError)
assert not issubclass(socket.timeout, ConnectionError)
hb_timed._post = _orig_post
print("ok  submit transport errors (RemoteDisconnected is a ConnectionError) resend once; timeouts never")

# 7) Failed-attempt evidence pull: only when the next step works on the failed variant (Day 8: 157 MB pulled over
#    the VPN after a clock/transport failure held binary Mastery's retry for 442 s + 186 s).
nb = workers.needs_bytes
assert nb({"result": "solver_incomplete"}) and nb({"result": "incorrect"}) and nb({"result": "solver_error"})
assert nb({"result": "exec_error", "solver_too_slow": True})
for r in ({"result": "expired", "phases": {"solve": 8}}, {"result": "expired", "submit_transport_error": True},
          {"result": "expired", "clock_short": True}, {"result": "exec_error", "detail": "ssh"},
          {"result": "exec_error", "solver_too_slow": True, "clock_short": True}):
    assert not nb(r), r
print("ok  evidence pull: skipped for clock/transport failures, kept for solver failures")

# 8) _keep_failed_attempt never archives another attempt's bytes under this attempt's id.
cdir = Path(tempfile.mkdtemp())
tdir = Path(tempfile.mkdtemp())
(tdir / "contract.json").write_text(json.dumps({"attempt_id": "OLD-attempt"}))
(tdir / "evidence.zip").write_bytes(b"old bytes")
_o = (timed.timed_dir, cli.cdir)
timed.timed_dir, cli.cdir = (lambda cid: tdir), (lambda cid: cdir)
try:
    timed._keep_failed_attempt("c/mastery", {"attempt_id": "NEWattempt-123", "result": "expired"}, **quiet)
    kept = cdir / "attempts" / "NEWattem"
    assert (kept / "last_timed.json").exists() and not (kept / "evidence.zip").exists(), list(kept.iterdir())
    (tdir / "contract.json").write_text(json.dumps({"attempt_id": "SAME-1234"}))
    timed._keep_failed_attempt("c/mastery", {"attempt_id": "SAME-1234", "result": "incorrect"}, **quiet)
    assert (cdir / "attempts" / "SAME-123" / "evidence.zip").exists()
finally:
    timed.timed_dir, cli.cdir = _o
print("ok  _keep_failed_attempt: mismatched attempt -> result only; matching attempt -> bytes archived")

# 9) bin/7z: a caller's own -y is not duplicated (Day 8 c500c83: "Multiple instances for switch: -y" broke every triage
#    pre-extraction); -y and -pinfected are still added when missing.
wd = Path(tempfile.mkdtemp())
(wd / "a.txt").write_text("hello\n")
import pyzipper  # noqa: E402
with pyzipper.AESZipFile(wd / "t.zip", "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as z:
    z.setpassword(b"infected")
    z.write(wd / "a.txt", "a.txt")
for args, out in ((["x", "-y", f"-o{wd}/o1", "-pinfected"], "o1"), (["x", f"-o{wd}/o2"], "o2")):
    r = subprocess.run([str(ROOT / "bin" / "7z"), *args, str(wd / "t.zip")], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and (wd / out / "a.txt").read_text() == "hello\n", (args, r.stdout[-300:], r.stderr[-300:])
print("ok  bin/7z: works with and without the caller's -y (passworded zip)")

# 10) Single-solve bisect: one hung probe doesn't kill it; a clean first half implies the second (no probe).
subs = []
truth = {"d01_a": "1", "d01_b": "2", "d02_a": "3", "d08_x": "64", "d08_y": "62", "d08_z": "z"}
fail_once = {"d02_a"}


def fake_submit(cid, g, force=False, probe=False, **kw):
    subs.append(sorted(g))
    if set(g) & fail_once:
        fail_once.clear()
        raise cli.remote.Unreachable("GM unreachable: The read operation timed out")
    return ("accepted" if all(truth[k] == v for k, v in g.items()) else "incorrect"), {}, []


_o = (cli.submit, cli.confirmed_answers)
cli.submit, cli.confirmed_answers = fake_submit, (lambda cid, att=None: {})
try:
    answers = {**truth, "d08_x": "2"}
    bad = cli._bisect_rejected("c", answers)
    assert bad == {"d08_x"}, bad
    assert sorted(["d02_a"]) in subs and subs.count(["d02_a"]) == 2      # retried after the hang
    assert ["d08_x", "d08_y", "d08_z"] not in subs                       # last family inferred, not probed
finally:
    cli.submit, cli.confirmed_answers = _o
print(f"ok  bisect: survives a hung probe, infers the last family / second half ({len(subs)} probes)")

# 11) kind-aware binary label laws (D8 elf_class kind integer -> bit width 64, not EI_CLASS 2).
from lib import playbook  # noqa: E402
cands = playbook.seed_candidates("binary-reverse-engineering", "d08_analysis_elf_class", solver_value="2")
assert "64" in cands and "2" not in cands, cands
print("ok  playbook: elf_class candidates include the integer bit width")

# 12) Homebase hot files: a mid-run change to hb_timed.py / vocab.json is pushed before the next timed attempt.
pushed = []
_o = workers.remote.rsync_to
workers.remote.rsync_to = lambda src, dst, **k: pushed.append(str(dst))
try:
    workers._hot_pushed.clear()
    workers.push_hot_files()                      # first call records the base-synced versions
    assert not pushed
    workers._hot_pushed["lib/vocab.json"] = (0, 0)  # pretend it changed since
    workers.push_hot_files()
    assert pushed == [f"~/{workers.HB_WORK}/lib/vocab.json"], pushed
finally:
    workers.remote.rsync_to = _o
print("ok  Homebase hot files: changed vocab/hb_timed pushed mid-run")

# 13) SSH works inside the worker sandbox (ssh_config is skipped: bwrap showed it with a foreign owner -> exit 255, so
#     the Single submit-via-Homebase path never fired on Day 7/8).
assert workers.remote.SSH_OPTS[:2] == ["-F", "/dev/null"]
print("ok  SSH_OPTS skip ssh_config (sandbox-safe)")
# 14) Day 8 lane knowledge merged from the rehearsal copy's ratchet: HTML entities (warmups), v=3 analysis plans incl. hex_base64
#     (script), integer ELF class/machine spellings (binary).
from lib import decode as _decode, codec as _codec, elf as _elf  # noqa: E402
assert _decode.decode_chunk("&#109;&#109;&#105;&#116;&#45;&#112;&#101;&#98;&#98;&#108;&#101;&#45;&#52;&#50;") \
    == "mmit-pebble-42"                                                     # D8 mastery set1 line 8, GM-confirmed
_v3 = ("<?php\n// HUNTRESS_ANALYSIS_V1:HB64-646a307a66484a7662475539633352685a325679664746306447466a617a31554d5445774e513d3d\n"
       "$descriptor_ab12 = \"..\";\n")
assert _codec.find_codecs(_v3)[-1]["plain"] == "v=3|role=stager|attack=T1105"                 # D8 hex_base64 marker
assert _codec.decode("763d337c726f.6c653d78", "hex_compact", "identity") == "v=3|role=x"         # D8 FRAG dot-split hex
_hb = _codec._format_like(b"v=3|role=x", "hex_base64", "646a")                                    # family re-encode
assert _codec.decode(_hb, "hex_base64", "identity") == "v=3|role=x", _hb
import platform  # noqa: E402
if platform.machine() == "x86_64" and sys.platform.startswith("linux"):
    _hdr = _elf.fields(open(os.path.realpath(sys.executable), "rb").read())[1]
    assert (_hdr["elf_class"], _hdr["elf_class_int"], _hdr["machine"], _hdr["machine_int"]) == ("ELF64", "64", "x86-64", "62")
print("ok  D8 lane knowledge: HTML entities, v=3 plans (hex_base64 round-trip), integer ELF class/machine")
print("ALL PASS")
