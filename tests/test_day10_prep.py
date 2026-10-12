"""Behavior checks for the Day 10 prep (Day 9 post-mortem): per-set Mastery pipeline, Homebase pre-push signature,
prior-solver staging + dry-run questions, deferred triage recon, in-process keep-alive GM client + release wait,
family-probe memo, faster worker stop, noise-robust Mastery estimate (offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_day10_prep.py      (exit 0 = all pass)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
from hctf import orchestrate, solvers, triage, workers  # noqa: E402
import hb_timed  # noqa: E402

D9 = ROOT / "challenges" / "day09"

# 1) _set_plan: per-set deliveries -> pipeline plan; a shared delivery or a single set -> None (plain path)
mc = json.loads((D9 / "binary-nimble" / "mastery" / "contract.json").read_text())
ids = mc["answer_ids"]
plan = hb_timed._plan(mc)
sp = hb_timed._set_plan(mc, plan, ids)
assert sp and list(sp) == ["set1", "set2", "set3", "set4", "set5"], sp
assert sp["set3"] == ["delivery 3: evidence.zip"], sp
shared = json.loads(json.dumps(mc))
for q in shared["questions"]:
    if q["id"].startswith("set2."):
        q["artifact"] = "delivery 1: evidence.zip"
assert hb_timed._set_plan(shared, plan, ids) is None
tt = json.loads((D9 / "binary-nimble" / "time_trial" / "contract.json").read_text())
assert hb_timed._set_plan(tt, hb_timed._plan(tt), tt.get("answer_ids") or [q["id"] for q in tt["questions"]]) is None
assert hb_timed._total_bytes(mc) > 150e6
print("ok  _set_plan: 5 own-delivery sets planned; shared delivery / single-set TT -> plain path")

# 2) _pipelined on a real saved Mastery case (D9 mobile, 5 sets): every set solved by its own early run, answers match
#    the GM-verified expected values, scratch dirs removed; a failing set run -> None (whole-solver fallback)
case = next((D9 / "mobile-trust-everyone" / "solver" / "cases").glob("auto-mastery-*"))
body = json.loads((case / "contract.json").read_text())
exp = json.loads((case / "expected.json").read_text())
mids = body["answer_ids"]
mplan = [(n, n) for n in sorted(p.name for p in (case / "artifacts").iterdir())]
msets = hb_timed._set_plan(body, mplan, mids)
assert msets and len(msets) == 5, msets
solve = (D9 / "mobile-trust-everyone" / "solver" / "solve.py").resolve()
env = hb_timed._solver_env()
env["PYTHONPATH"] = str(ROOT)


def fetch_into(adir):
    return lambda item: shutil.copy(case / "artifacts" / item[0], adir / item[0])


with tempfile.TemporaryDirectory() as d:
    adir = Path(d)
    out = {}
    r = hb_timed._pipelined(msets, mplan, dict(body, deadline=None), mids, adir, solve, env, fetch_into(adir), 60,
                            out, time.time())
    assert r is not None, out
    got = json.loads(r.stdout)
    assert all(got.get(k) == v for k, v in exp.items()), {k: (got.get(k), v) for k, v in exp.items() if got.get(k) != v}
    assert out["pipelined"]["sets"] == 5 and "_t_downloaded" in out
    assert not list(adir.glob(".set-*")), list(adir.glob(".set-*"))
with tempfile.TemporaryDirectory() as d:
    adir = Path(d)
    bad = Path(d) / "bad_solve.py"
    bad.write_text("import sys; sys.exit(3)\n")
    out = {}
    r = hb_timed._pipelined(msets, mplan, dict(body, deadline=None), mids, adir, bad, env, fetch_into(adir), 60, out,
                            time.time())
    assert r is None and out.get("pipeline_fallback"), out
print("ok  _pipelined: D9 mobile Mastery 5/5 sets match expected; a failing set run falls back (no partial answers)")

# 3) pre-push signature: a snapshot restored with copy2 over the live dir has the SAME signature (push skipped)
with tempfile.TemporaryDirectory() as d:
    snap, live = Path(d) / "snap", Path(d) / "live"
    (snap / "lib").mkdir(parents=True)
    (snap / "solve.py").write_text("print(1)\n")
    (snap / "lib" / "x.py").write_text("y = 2\n")
    (live / "cases" / "c1").mkdir(parents=True)
    (live / "cases" / "c1" / "expected.json").write_text("{}")
    (live / "solve.py").write_text("print('mid-edit')\n")
    for src in snap.rglob("*"):
        if src.is_file():
            dst = live / src.relative_to(snap)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    assert workers._solver_sig(snap) == workers._solver_sig(live)
    (live / "solve.py").write_text("print(2)\n")
    assert workers._solver_sig(snap) != workers._solver_sig(live)
print("ok  pre-push: copy2-restored solver keeps the pushed signature (cases/ ignored); an edit changes it")

# 4) prior-solver staging: everything copied (cases/ too), __pycache__ / generalize scratch left out, existing kept
with tempfile.TemporaryDirectory() as d:
    prior, sdir = Path(d) / "prior", Path(d) / "today" / "solver"
    for f in ("solve.py", "cases/single_solve/expected.json", "__pycache__/solve.cpython-312.pyc",
              ".generalize-snapshot/solve.py", "helper.js"):
        (prior / f).parent.mkdir(parents=True, exist_ok=True)
        (prior / f).write_text(f)
    (sdir).mkdir(parents=True)
    (sdir / "keep.txt").write_text("k")
    orchestrate.stage_prior_solver(prior, sdir)
    names = sorted(str(p.relative_to(sdir)) for p in sdir.rglob("*") if p.is_file())
    assert names == ["cases/single_solve/expected.json", "helper.js", "keep.txt", "solve.py"], names
print("ok  stage_prior_solver: solver + cases copied, __pycache__/.generalize-* skipped, existing files kept")

# 5) dry-run render: the empty ids' questions (today's contract text) appear for a small delta, never for a big one
d = {"solver": "challenges/day08/x/solver", "seconds": 1.1, "timed_out": False, "rc": 0, "frames": [], "error": "",
     "warnings": [], "answered": 89, "total": 90, "empty": ["d09_analysis_hcfg_offset"],
     "empty_q": {"d09_analysis_hcfg_offset": {"question": "What is the exact analysis hcfg offset value?",
                                              "artifact": "evidence.zip", "format": {"kind": "integer"},
                                              "normalization": "exact"}}}
txt = solvers.render_dry_run(d)
assert "What is the exact analysis hcfg offset value?" in txt and '"integer"' in txt and "evidence.zip" in txt, txt
big = dict(d, answered=10, empty=[f"id{i}" for i in range(80)], empty_q={f"id{i}": {"question": "Q"} for i in range(6)})
assert "questions (today" not in solvers.render_dry_run(big)
print("ok  render_dry_run: question/format/artifact of each empty id for a <=6-field delta")

# 6) triage: deferred recon writes a placeholder at once and the full recon section afterwards; no deferral when the
#    callable says no
cid = "warmups-day-09"
from hctf import cli  # noqa: E402
tpath = cli.cdir(cid) / "triage.md"
orig = tpath.read_text() if tpath.exists() else None
real_recon = triage._recon
gate = threading.Event()


def slow_recon(c, root):
    gate.wait(5)
    return ["", "## Recon (standard tools, pre-run for you -- facts, not answers)", "", "RECON-DONE-MARK"]


try:
    triage._recon = slow_recon
    logs = []
    p = triage.triage(cid, defer_recon=lambda: True, log=logs.append)
    first = p.read_text()
    assert "Still running in the background" in first and "RECON-DONE-MARK" not in first, first[-400:]
    gate.set()
    for _ in range(50):
        if "RECON-DONE-MARK" in p.read_text():
            break
        time.sleep(0.1)
    final = p.read_text()
    assert "RECON-DONE-MARK" in final and "Still running" not in final and logs, final[-300:]
    gate.clear()
    threading.Timer(0.3, gate.set).start()
    p = triage.triage(cid, defer_recon=lambda: False)
    assert "RECON-DONE-MARK" in p.read_text() and "Still running" not in p.read_text()
finally:
    triage._recon = real_recon
    if orig is not None:
        tpath.write_text(orig)
print("ok  triage: deferred recon -> placeholder now, full section later; no deferral -> written once, complete")

# 7) _recon_deferrable: only a finished, mostly-answering, not-timed-out dry run allows the early hand-off
from concurrent.futures import Future  # noqa: E402


class _C:
    pass


ch = _C()


def fut(v):
    f = Future()
    f.set_result(v)
    return f


ch._dry_fut = fut({"answered": 89, "total": 90, "timed_out": False})
assert orchestrate.Chain._recon_deferrable(ch)
ch._dry_fut = fut({"answered": 10, "total": 90, "timed_out": False})
assert not orchestrate.Chain._recon_deferrable(ch)
ch._dry_fut = fut({"answered": 90, "total": 90, "timed_out": True})
assert not orchestrate.Chain._recon_deferrable(ch)
ch._dry_fut = Future()   # still running
assert not orchestrate.Chain._recon_deferrable(ch)
ch._dry_fut = None
assert not orchestrate.Chain._recon_deferrable(ch)
print("ok  _recon_deferrable: >=80% answered + finished + no timeout only")

# 8) in-process keep-alive GM client against a local stand-in: GETs reuse one connection, a dropped kept-alive socket
#    is resent once for a GET, a POST is never resent, envelopes match the CLI's
hits = {"conns": set(), "post": 0, "drop_next_get": False}


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        hits["conns"].add(self.client_address)
        if hits["drop_next_get"]:
            hits["drop_next_get"] = False
            self.close_connection = True
            self.connection.close()
            return
        self._send({"challenges": [{"id": "warmups-day-10"}]} if "op=list" in self.path else {"result": "ok"})

    def do_POST(self):
        hits["post"] += 1
        n = int(self.headers.get("Content-Length") or 0)
        self._send({"echo": json.loads(self.rfile.read(n))})


srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{srv.server_address[1]}"
code = (f"import sys, json; sys.path.insert(0, {str(ROOT / 'hctf')!r}); import gm; gm.POOL = True\n"
        "a = gm.run(['status', 'x']); b = gm.run(['status', 'y']); c = gm.run(['list', '--day', '10'])\n"
        "s = gm.run(['start', 'warmups-day-10'])\n"
        "print(json.dumps([a['http'], b['body'], c['body']['challenges'][0]['id'], s['body']['echo']['op']]))\n")
r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30,
                   env=dict(os.environ, HUNTRESS_GAME_MASTER_URL=url, HUNTRESS_GM_TOKEN="t"))
assert r.returncode == 0, r.stderr[-800:]
assert json.loads(r.stdout.strip().splitlines()[-1]) == [200, {"result": "ok"}, "warmups-day-10", "start"], r.stdout
assert len(hits["conns"]) == 1, hits["conns"]        # 3 GETs on one kept-alive connection
hits["conns"].clear()
hits["drop_next_get"] = False
code3 = (f"import sys, json; sys.path.insert(0, {str(ROOT / 'hctf')!r}); import gm; gm.POOL = True\n"
         "a = gm.run(['status', 'x'])\n"
         "print('ARM', flush=True); sys.stdin.readline()\n"
         "b = gm.run(['status', 'y'])\n"
         "print(json.dumps([a['http'], b['http'], b['body']]))\n")
p = subprocess.Popen([sys.executable, "-c", code3], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                     env=dict(os.environ, HUNTRESS_GAME_MASTER_URL=url, HUNTRESS_GM_TOKEN="t"))
assert p.stdout.readline().strip() == "ARM"
hits["drop_next_get"] = True      # the server drops the kept-alive socket on the next GET
p.stdin.write("\n")
p.stdin.flush()
outp = p.stdout.read()
p.wait(timeout=20)
assert json.loads(outp.strip().splitlines()[-1]) == [200, 200, {"result": "ok"}], outp
srv.shutdown()
print("ok  gm keep-alive: GETs share one connection, a dropped socket is resent once (GET), envelopes unchanged")

# 9) remote._gm_local runs gm.py in-process by default (no subprocess per call)
from hctf import remote  # noqa: E402
assert remote.GM_INPROC and hasattr(remote.gm_client(), "run") and remote.gm_client().POOL
print("ok  remote: local GM transport is in-process with keep-alive (HCTF_GM_INPROC=0 restores subprocesses)")

# 10) wait_for_release: polls until the day is listed and returns that list (no second list call)
calls = []
seq = [[], [], [{"id": "warmups-day-10"}]]
real_rel = orchestrate.released_challenges
try:
    orchestrate.released_challenges = lambda day=None: (calls.append(day), seq.pop(0))[1]
    got = orchestrate.wait_for_release(10, poll=0.01)
finally:
    orchestrate.released_challenges = real_rel
assert got == [{"id": "warmups-day-10"}] and calls == [10, 10, 10], (got, calls)
day_sh = (ROOT / "bin" / "day.sh").read_text()
assert "--wait-release" in day_sh and "hb keepalive --timeout" not in day_sh
print("ok  wait_for_release: polls in-process, hands the listed challenges to the launch; day.sh --wait uses it")

# 11) family probe memo: concurrent make()s compute rep_samples once
import family  # noqa: E402
n = {"calls": 0}
real = family._rep_samples
try:
    family._rep_samples = lambda cases: (n.__setitem__("calls", n["calls"] + 1), time.sleep(0.2), {"b64": "x"})[2]
    family._REP_CACHE.clear()
    cs = [ROOT / "tests"]
    ts = [threading.Thread(target=family.rep_samples, args=(cs,)) for _ in range(3)]
    [t.start() for t in ts]
    [t.join() for t in ts]
finally:
    family._rep_samples = real
    family._REP_CACHE.clear()
assert n["calls"] == 1, n
print("ok  family.rep_samples: memoized per process (3 parallel languages -> 1 computation)")

# 12) worker stop: the wait loop ends the worker as soon as `stop` is set (no 0.5 s poll lag), and a worker that
#     already exited reports its own rc
stop = threading.Event()
pr = subprocess.Popen(["sleep", "30"], start_new_session=True)
threading.Timer(0.2, stop.set).start()
t0 = time.time()
rc, _ = workers._wait_worker(pr, "x.log", 60, stop)
assert rc == workers.STOPPED_RC and time.time() - t0 < 1.5, (rc, time.time() - t0)
pr = subprocess.Popen(["true"], start_new_session=True)
time.sleep(0.2)
rc, _ = workers._wait_worker(pr, "x.log", 60, threading.Event())
assert rc == 0, rc
print("ok  _wait_worker: stop -> killed within ~0.2 s of the event; a finished worker keeps its rc")

# 13) Mastery estimate: 1-vs-2-set jitter is not extrapolated per set; a real per-set cost still is
with tempfile.TemporaryDirectory() as d:
    mcp = Path(d) / "contract.json"
    mcp.write_text(json.dumps({"answer_ids": [f"set{i}.x" for i in range(1, 44)]}))
    jitter = {"base_seconds": 0.15, "results": [{"mutation": "mastery-shape", "ok": True, "seconds": 0.26}]}
    real_cost = {"base_seconds": 0.3, "results": [{"mutation": "mastery-shape", "ok": True, "seconds": 1.3}]}
    e1 = orchestrate.mastery_estimate(jitter, mcp)
    e2 = orchestrate.mastery_estimate(real_cost, mcp)
assert e1 < 1.0, e1
assert e2 > 40, e2
print(f"ok  mastery_estimate: jitter-only {e1}s (was ~7 s for D9 warmups), real per-set cost {e2}s")

# 14) pre-Mastery probe wait is bounded: a probe still running after LATE_PROBE_WAIT -> Mastery starts, no generalize
from hctf import timed  # noqa: E402


class _SlowFut:
    def done(self):
        return False

    def result(self, timeout=None):
        raise AssertionError("must not block on a running probe before Mastery")


ch = orchestrate.Chain.__new__(orchestrate.Chain)
ch.base, ch.lane, ch.name = "b", "script-analysis", "x"
ch.entries = {"time_trial": {"id": "b/time_trial"}, "mastery": {"id": "b/mastery"}}
ch.sdir = Path(tempfile.mkdtemp()) / "solver"
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
ch._pre_attempt_done = True
ch._fam_pre_fut, ch._mut_pre_fut, ch._cmp_pre_fut = _SlowFut(), None, None
gens, runs = [], []
patches = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate, "LATE_PROBE_WAIT"): 0.1,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (timed, "run"): lambda cid, sdir, log=None, **k: (runs.append(cid), "correct")[1],
    (timed, "last_result"): lambda cid: None,
    (orchestrate.Chain, "generalize"): lambda self, cid, wrong=None, fixed=None, diag=None: gens.append(diag),
    (orchestrate.Chain, "_mastery_speed_gate"): lambda self, cid: None,
}
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    t0 = time.time()
    assert ch.timed_stage("mastery") is True and runs == ["b/mastery"] and not gens, (runs, gens)
    assert time.time() - t0 < 2, time.time() - t0
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
print("ok  pre-Mastery probes: a still-running probe no longer holds Mastery (bounded wait, no generalize)")

# 15) timed_env: the status-time contract's delivery bytes reach hb_timed (live start bodies carry no sizes)
env15 = workers.timed_env("binary-reverse-engineering-day-09-nim-generated-runtime/mastery")
assert int(env15.get("HCTF_EXPECT_BYTES", 0)) > 150e6, env15
os.environ["HCTF_EXPECT_BYTES"] = env15["HCTF_EXPECT_BYTES"]
try:
    live = dict(mc, artifacts=[{k: v for k, v in a.items() if k != "size"} for a in mc["artifacts"]])
    assert hb_timed._total_bytes(live) > 150e6
finally:
    del os.environ["HCTF_EXPECT_BYTES"]
assert hb_timed._total_bytes(live) == 0
print("ok  timed_env: HCTF_EXPECT_BYTES from the saved contract gates the pipeline on a size-less live body")

# 16) Mastery speed gate re-measures alone before acting: a contended-probe estimate over the gate that re-times under
#     it -> no speed generalize; one that stays over -> generalize with the re-measured number
with tempfile.TemporaryDirectory() as d:
    cdir = Path(d)
    (cdir / "window.json").write_text(json.dumps({"seconds": 7}))
    (cdir / "contract.json").write_text(json.dumps({"answer_ids": [f"set{i}.x" for i in range(1, 44)]}))
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.base, ch.sdir = "w", Path(d) / "solver"
    ch.entries = {"time_trial": {"id": "w/time_trial"}, "mastery": {"id": "w/mastery"}}
    ch._mut_summary = {"base": "single_solve", "base_seconds": 0.12,
                       "results": [{"mutation": "mastery-shape", "ok": True, "seconds": 0.34, "case": d}]}
    gens = []
    patches = {(orchestrate, "say"): lambda *a, **k: None, (orchestrate.cli, "cdir"): lambda cid: cdir,
               (orchestrate.Chain, "generalize"): lambda self, cid, wrong=None, fixed=None, diag=None: gens.append(diag)}
    saved = {k: getattr(*k) for k in patches}
    real_rm = orchestrate.remeasure_estimate
    try:
        for (mod, name), fn in patches.items():
            setattr(mod, name, fn)
        assert orchestrate.mastery_estimate(ch._mut_summary, cdir / "contract.json") > 14   # the contended number
        orchestrate.remeasure_estimate = lambda sdir, summ, mc, reps=2: 0.41
        orchestrate.Chain._mastery_speed_gate(ch, "w/mastery")
        assert not gens, gens
        ch._mastery_gate_done = False
        orchestrate.remeasure_estimate = lambda sdir, summ, mc, reps=2: 30.0
        orchestrate.Chain._mastery_speed_gate(ch, "w/mastery")
        assert len(gens) == 1 and gens[0]["mastery_estimate"] == 30.0, gens
    finally:
        orchestrate.remeasure_estimate = real_rm
        for (mod, name), fn in saved.items():
            setattr(mod, name, fn)
print("ok  Mastery speed gate: acts only on an estimate that is still over the gate when re-timed alone")

print("\nALL DAY-10 PREP CHECKS PASSED")
