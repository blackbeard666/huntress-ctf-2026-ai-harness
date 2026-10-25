"""In-network reuse race (D25 post-mortem B3b): hb_daemon `race` op + workers.hb_race + Chain._hb_race, offline.
1) the real daemon (no bearer, as a relay channel) reconnects to the open single, downloads in-network, runs the given
   solvers and returns answers only; the stand-in GM never sees an Authorization header and no submit is made;
2) a daemon holding the bearer refuses the op; an attempt-id mismatch comes back as an error (nothing run);
3) Chain._hb_race: the plan is merged from the VM's outs and handed to the shared submit path; it stands down when the
   local bytes land first or no start body arrives; the first race plan to reach the submit claims it;
   _race_snapshot verifies from the plan when there are no local bytes; the lane-size gate picks binary only.

Run:  source bin/env.sh && python3 tests/test_hb_race.py      (exit 0 = all pass)
"""
import json
import os
import sys
import tempfile
import threading
import time
from concurrent.futures import Future
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import orchestrate, solvers, workers  # noqa: E402

PY = str(ROOT / ".venv" / "bin" / "python") if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
FAILS = []


def check(name, ok, detail=""):
    print(("ok  " if ok else "FAIL ") + name + ("" if ok else f"  -- {detail}"))
    if not ok:
        FAILS.append(name)


# ---------------------------------------------------------------------------------------------- stand-in GM (inside)
state = {"auth_seen": 0, "starts": 0, "submits": 0, "attempt": None, "cap": os.urandom(32).hex()}
lock = threading.Lock()
PAYLOAD = b"big-single-bytes-" + os.urandom(4).hex().encode()


class GM(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, obj, raw=None):
        body = raw if raw is not None else json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream" if raw is not None else "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _note_auth(self):
        if self.headers.get("Authorization"):
            with lock:
                state["auth_seen"] += 1

    def do_GET(self):
        self._note_auth()
        self._send(None, raw=PAYLOAD)

    def do_POST(self):
        self._note_auth()
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        if body.get("op") == "start":
            with lock:
                state["starts"] += 1
                state["attempt"] = state["attempt"] or os.urandom(8).hex()   # start RECONNECTS to the open attempt
            self._send({"attempt_id": state["attempt"], "answer_ids": ["a", "b"],
                        "questions": [{"id": "a", "artifact": "evidence.bin"}, {"id": "b", "artifact": "evidence.bin"}],
                        "artifacts": [{"download": f"/?op=download&capability={state['cap']}"}]})
        else:
            with lock:
                state["submits"] += 1
            self._send({"error": "no submit expected"})


srv = ThreadingHTTPServer(("127.0.0.1", 0), GM)
threading.Thread(target=srv.serve_forever, daemon=True).start()
gm_url = f"http://127.0.0.1:{srv.server_address[1]}"

tmp = Path(tempfile.mkdtemp(dir=ROOT / ".run"))
rel = tmp.relative_to(ROOT)
good, bad = tmp / "good" / "solver", tmp / "bad" / "solver"
for d in (good, bad):
    d.mkdir(parents=True)
(good / "solve.py").write_text('''import argparse, json, os
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--contract"); ap.add_argument("--artifacts"); a = ap.parse_args()
data = (Path(a.artifacts) / "evidence.bin").read_bytes().decode()
ids = json.loads(Path(a.contract).read_text())["answer_ids"]
print(json.dumps({"a": data, "b": len(data), "procs": os.environ.get("HCTF_SOLVER_MAX_PROCS")}))
''')
(bad / "solve.py").write_text("raise SystemExit('boom')\n")
env_saved = os.environ.pop("HUNTRESS_GM_TOKEN", None)
try:
    # ------------------------------------------------------------------------------------- 1) the daemon's race op
    d = workers.HbDaemon(log=lambda m: None, argv=[PY, str(ROOT / "hctf" / "hb_daemon.py"), "--stdio"], gm_url=gm_url,
                         token=None)
    try:
        r = d.call("race", timeout=60, cid="binary-day-99/single_solve", attempt_id=None,
                   solvers=[str(rel / "good" / "solver"), str(rel / "bad" / "solver"), str(rel / "none" / "solver")],
                   solve_timeout=20)["result"]
        outs = r.get("outs") or {}
        g = outs.get(str(rel / "good" / "solver")) or [{}, "missing", 0]
        check("1 race: in-network bytes reach the solver (answers come back, nothing submitted)",
              g[0].get("a") == PAYLOAD.decode() and g[1] is None and r.get("bytes") == len(PAYLOAD)
              and r.get("files") == 1 and state["submits"] == 0, r)
        check("1 race: the solvers see HCTF_SOLVER_MAX_PROCS=2 (the VM's 2 vCPUs)", g[0].get("procs") == "2", g)
        b = outs.get(str(rel / "bad" / "solver")) or [{}, None, 0]
        n = outs.get(str(rel / "none" / "solver")) or [{}, None, 0]
        check("1 race: a crashing / missing solver is that solver's error, not the op's",
              b[0] == {} and "exit" in str(b[1]) and "no solver on Homebase" in str(n[1]), (b, n))
        check("1 race: the stand-in GM never saw an Authorization header (no bearer on this channel)",
              state["auth_seen"] == 0, state)
        att = r.get("attempt_id")
        r2 = d.call("race", timeout=60, cid="binary-day-99/single_solve", attempt_id=att,
                    solvers=[str(rel / "good" / "solver")], solve_timeout=20)["result"]
        check("1 race: start only reconnects (same attempt id); the client's attempt id is checked",
              r2.get("attempt_id") == att and not r2.get("error") and state["starts"] == 2, r2)
        r3 = d.call("race", timeout=60, cid="binary-day-99/single_solve", attempt_id="someone-else",
                    solvers=[str(rel / "good" / "solver")], solve_timeout=20)["result"]
        check("2 race: an attempt mismatch is an error and runs nothing",
              "attempt mismatch" in str(r3.get("error")) and not r3.get("outs"), r3)
    finally:
        d.close()
    d2 = workers.HbDaemon(log=lambda m: None, argv=[PY, str(ROOT / "hctf" / "hb_daemon.py"), "--stdio"], gm_url=gm_url,
                          token="tok-should-refuse")
    try:
        try:
            d2.call("race", timeout=30, cid="binary-day-99/single_solve", solvers=[str(rel / "good" / "solver")])
            check("2 race: refused on a channel holding the bearer", False, "accepted")
        except workers.DaemonError as e:
            check("2 race: refused on a channel holding the bearer", "no-bearer" in str(e), e)
    finally:
        d2.close()
finally:
    srv.shutdown()
    if env_saved is not None:
        os.environ["HUNTRESS_GM_TOKEN"] = env_saved

# ------------------------------------------------------------------------------- workers.hb_race: rel -> local dirs
saved = (workers.hb_race_prepare, workers.hb_race_chan)
try:
    calls = {}

    class Chan:
        k = 0

        def call(self, op, timeout=60, **kw):
            calls[op] = kw
            return {"ok": True, "result": {"attempt_id": "A1", "outs": {kw["solvers"][0]: [{"a": "1"}, None, 0.5]}}}
    workers.hb_race_prepare = lambda sdirs, log=print: [str(Path(s).relative_to(ROOT)) for s in sdirs]
    workers.hb_race_chan = lambda log=print: Chan()
    res = workers.hb_race("x/single_solve", [good], "A1", 15, log=lambda m: None)
    check("workers.hb_race: VM outs keyed back to the local solver dirs; attempt id + solve timeout sent",
          res["outs"] == {good: ({"a": "1"}, None, 0.5)} and calls["race"]["attempt_id"] == "A1"
          and calls["race"]["solve_timeout"] == 15, (res, calls))
    workers.hb_race_chan = lambda log=print: None
    check("workers.hb_race: no relay channel -> None (the local race runs)",
          workers.hb_race("x/single_solve", [good], "A1", log=lambda m: None) is None)
finally:
    workers.hb_race_prepare, workers.hb_race_chan = saved

# ---------------------------------------------------------------------------------------- 3) Chain._hb_race logic
C = orchestrate.Chain
cdir = tmp / "cid"
cdir.mkdir()
contract = {"attempt_id": "A1", "answer_ids": ["a", "b"], "questions": []}
(cdir / "start.json").write_text(json.dumps(contract))
saved = {k: getattr(orchestrate.cli, k) for k in ("load", "cdir", "is_complete", "attempt_id")}
saved_w = (workers.hb_race, workers.hb_race_prepare, workers.hb_race_chan)
saved_s = (solvers.reuse_cands, solvers.reuse_merge)
try:
    orchestrate.cli.load = lambda cid, name: json.loads((cdir / name).read_text()) if (cdir / name).exists() else None
    orchestrate.cli.cdir = lambda cid: cdir
    orchestrate.cli.is_complete = lambda cid: False
    orchestrate.cli.attempt_id = lambda b: (b or {}).get("attempt_id")
    workers.hb_race_prepare = lambda sdirs, log=print: []
    chan = {"up": object()}
    workers.hb_race_chan = lambda log=print: chan["up"]
    solvers.reuse_cands = lambda lane, exclude=(), limit=None, rank=None, question_contract=None: ([good, bad], [])
    merged_in = {}

    def fake_merge(c, cands, lane_dirs, outs):
        merged_in["outs"] = outs
        return {"high": {}, "spec": {"a": "1", "b": "2"}, "runs": {}, "best": good, "outs": outs, "alts": {}}
    solvers.reuse_merge = fake_merge

    def chain():
        ch = C.__new__(C)
        ch.lane, ch.sdir, ch.base = "binary-reverse-engineering", tmp / "today" / "solver", "b"
        ch._chain_t0 = time.time() - 5
        ch._race_done = threading.Event()
        ch.sub = []
        ch._race_submit = lambda cid, c, ids, plan, art, t0, tr, where="": ch.sub.append((ids, plan, art, where))
        return ch
    workers.hb_race = lambda cid, cands, att, t, log=print: {
        "attempt_id": "A1", "bytes": 35_700_000, "dl_s": 1.7, "start_s": 0.3, "race_s": 6.0,
        "outs": {good: ({"a": 1, "b": "2"}, None, 4.0), bad: ({}, "exit 1", 0.1)}}
    ch = chain()
    pending = Future()
    ch._hb_race("b/single_solve", pending)
    check("3 _hb_race: VM outs merged (values normalized to str) -> the shared submit path, art=None, tagged",
          ch.sub and ch.sub[0][0] == ["a", "b"] and ch.sub[0][2] is None and "in-network" in ch.sub[0][3]
          and merged_in["outs"][good][0] == {"a": "1", "b": "2"}, (ch.sub, merged_in))
    done = Future()
    done.set_result((contract, None))
    ch = chain()
    ch._hb_race("b/single_solve", done)
    check("3 _hb_race: stands down when the local bytes landed first", ch.sub == [], ch.sub)
    workers.hb_race = lambda cid, cands, att, t, log=print: {"attempt_id": "OTHER", "outs": {}}
    ch = chain()
    ch._hb_race("b/single_solve", Future())
    check("3 _hb_race: a different attempt on the VM -> nothing submitted", ch.sub == [], ch.sub)
    workers.hb_race = lambda cid, cands, att, t, log=print: None
    ch = chain()
    ch._hb_race("b/single_solve", Future())
    check("3 _hb_race: no relay channel -> nothing submitted", ch.sub == [], ch.sub)
    # no relay channel YET at the single's start (rehearsal fair D25: up 3-8 s later): the race waits for one beside the
    # local download, then runs
    calls = []
    workers.hb_race = lambda cid, cands, att, t, log=print: calls.append(1) or {
        "attempt_id": "A1", "outs": {good: ({"a": "1", "b": "2"}, None, 1.0)}}
    chan["up"] = None
    threading.Timer(0.6, lambda: chan.update(up=object())).start()
    ch = chain()
    ch._hb_race("b/single_solve", Future())
    check("3 _hb_race: waits for a relay channel that comes up after the single's start, then races",
          calls == [1] and ch.sub, (calls, ch.sub))
    chan["up"] = None
    old_wait = orchestrate.HB_RACE_WAIT_START
    orchestrate.HB_RACE_WAIT_START = 0.5
    calls.clear()
    ch = chain()
    ch._hb_race("b/single_solve", Future())
    orchestrate.HB_RACE_WAIT_START = old_wait
    check("3 _hb_race: no relay channel within HB_RACE_WAIT_START -> stands down, nothing raced",
          calls == [] and ch.sub == [], (calls, ch.sub))
    chan["up"] = object()
    (cdir / "start.json").unlink()
    old_wait = orchestrate.HB_RACE_WAIT_START
    orchestrate.HB_RACE_WAIT_START = 0.5
    ch = chain()
    t0 = time.time()
    ch._hb_race("b/single_solve", Future())
    orchestrate.HB_RACE_WAIT_START = old_wait
    check("3 _hb_race: no local start body -> stands down after HB_RACE_WAIT_START (never starts the attempt itself)",
          ch.sub == [] and time.time() - t0 < 3, ch.sub)
finally:
    for k, v in saved.items():
        setattr(orchestrate.cli, k, v)
    workers.hb_race, workers.hb_race_prepare, workers.hb_race_chan = saved_w
    solvers.reuse_cands, solvers.reuse_merge = saved_s

ch = C.__new__(C)
wins = []
saved = orchestrate.cli.load
att = {"id": "A1"}
try:
    orchestrate.cli.load = lambda cid, name: {"attempt_id": att["id"]}
    ths = [threading.Thread(target=lambda: wins.append(ch._race_claimed("b/single_solve"))) for _ in range(8)]
    [t.start() for t in ths]
    [t.join() for t in ths]
    att["id"] = "A2"
    again = ch._race_claimed("b/single_solve")
finally:
    orchestrate.cli.load = saved
check("3 _race_claimed: exactly one race plan reaches the submit per attempt (a new attempt races again)",
      sorted(wins) == [False] * 7 + [True] and again is True, (wins, again))

ch = C.__new__(C)
ch.sdir, ch.root, ch.base = tmp / "dayX" / "c" / "solver", tmp / "dayX" / "c", "b"
saved = orchestrate.cli.confirmed_answers
try:
    orchestrate.cli.confirmed_answers = lambda cid: {"a": "1"}
    snap = tmp / "snap" / "solver"
    snap.mkdir(parents=True)
    got = ch._race_snapshot("b/single_solve", good, contract, None, plan_out=({"a": "1"}, None, 1.0), presnap=snap)
    old = orchestrate.RACE_VERIFY_FROM_PLAN
    orchestrate.RACE_VERIFY_FROM_PLAN = False
    got2 = ch._race_snapshot("b/single_solve", good, contract, None, plan_out=({"a": "1"}, None, 1.0), presnap=snap)
    got3 = ch._race_snapshot("b/single_solve", good, contract, None, plan_out=None, presnap=snap)
    orchestrate.RACE_VERIFY_FROM_PLAN = old
    check("3 _race_snapshot: no local bytes -> verified from the plan's own run (even with verify-from-plan off); "
          "no plan either -> not verified", got == snap and got2 == snap and got3 is None, (got, got2, got3))
finally:
    orchestrate.cli.confirmed_answers = saved

mb = {ln: orchestrate._lane_last_single_mb(ln) for ln in
      ("binary-reverse-engineering", "script-analysis", "metadata-forensics", "mobile-android", "warmups")}
big = [ln for ln, v in mb.items() if v >= workers.HB_RACE_MIN_MB]
check("3 lane gate: only binary's last single is >= HB_RACE_MIN_MB (D20-D25: 32-35 MB vs ~1 MB)",
      big == ["binary-reverse-engineering"] or not any(mb.values()), mb)
ch = SimpleNamespace(lane="web", sdir=ROOT / "challenges" / "day99" / "w" / "solver")
check("3 lane gate: live-target web never races on Homebase", C._hb_race_wanted(ch) is False)
src = (ROOT / "hctf" / "orchestrate.py").read_text()
check("3 wiring: armed beside the single's start; race-first handoff before the download; bookkeeping joins it",
      "self._hb_race_fut = hpool.submit(self._hb_race, cid, start_fut)" in src
      and "in-network race, the single's download still running" in src and "dl.result()" in src
      and "target=_hb_race_predrop" in src)

import shutil  # noqa: E402
shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{len(FAILS)} failure(s)" + (": " + ", ".join(FAILS) if FAILS else ""))
sys.exit(1 if FAILS else 0)
