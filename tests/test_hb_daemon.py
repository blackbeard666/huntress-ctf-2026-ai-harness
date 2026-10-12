"""Warm timed-attempt daemon (hctf/hb_daemon.py + hb_zygote.py + workers.HbDaemon), offline:
1) zygote answers == fresh-interpreter answers on saved cases of every day's solvers (all lanes);
2) the daemon runs concurrent attempts end-to-end against a local stand-in GM through the real client, with the bearer
   only in its memory (never in the solver's environment, the daemon log or argv); re-warm on a solver change;
   solve timeouts come back as hb_timed's solver_too_slow path.

Run:  source bin/env.sh && python3 tests/test_hb_daemon.py      (exit 0 = all pass)
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import workers  # noqa: E402

PY = str(ROOT / ".venv" / "bin" / "python") if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
ENV = dict(os.environ, PYTHONPATH=str(ROOT))

# 1) zygote == subprocess on saved cases (single_solve + up to 2 more per solver, artifacts <= 8 MB)
checked, skipped = 0, 0
for sd in sorted(ROOT.glob("challenges/day0*/*/solver")):
    if not (sd / "solve.py").exists():
        continue
    cases = [c for c in sorted((sd / "cases").glob("*/")) if (c / "contract.json").exists() and (c / "artifacts").is_dir()]
    cases = sorted(cases, key=lambda c: (c.name != "single_solve", c.name))[:3]
    cases = [c for c in cases if sum(f.stat().st_size for f in (c / "artifacts").rglob("*") if f.is_file()) <= 8e6]
    if not cases:
        skipped += 1
        continue
    z = subprocess.Popen([PY, str(ROOT / "hctf" / "hb_zygote.py"), str(sd)], cwd=ROOT, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=ENV)
    hello = json.loads(z.stdout.readline())
    assert hello.get("ready"), (sd, hello)
    for c in cases:
        args = ["--contract", str(c / "contract.json"), "--artifacts", str(c / "artifacts")]
        ref = subprocess.run([PY, str(sd / "solve.py"), *args], capture_output=True, text=True, env=ENV, timeout=120)
        z.stdin.write(json.dumps({"id": c.name, "args": args, "env": ENV, "timeout": 120}) + "\n")
        z.stdin.flush()
        got = json.loads(z.stdout.readline())
        last = lambda t: (t.strip().splitlines() or [""])[-1]  # noqa: E731
        try:
            a, b = json.loads(last(ref.stdout)), json.loads(last(got["stdout"]))
        except ValueError:
            a, b = last(ref.stdout), last(got["stdout"])
        assert a == b and (ref.returncode == 0) == (got["rc"] == 0), (sd, c.name, ref.returncode, got["rc"],
                                                                       got["stderr"][-300:])
        checked += 1
    z.stdin.write('{"op": "exit"}\n')
    z.stdin.flush()
    z.wait(timeout=20)
assert checked >= 20, checked
print(f"ok  zygote == fresh interpreter on {checked} saved cases ({skipped} solvers without small cases skipped)")

# 2) daemon end-to-end against a stand-in GM, through the real client (workers.HbDaemon)
TOKEN = "tok-" + os.urandom(8).hex()
state = {"attempts": {}, "auth_bad": 0}
lock = threading.Lock()


class GM(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, obj, code=200, raw=None):
        body = raw if raw is not None else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/octet-stream" if raw is not None else "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth(self):
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            with lock:
                state["auth_bad"] += 1
            self._send({"error": "unauthorized"}, 401)
            return False
        return True

    def do_GET(self):
        if not self._auth():
            return
        from urllib.parse import parse_qs, urlsplit
        q = parse_qs(urlsplit(self.path).query)
        cap = q.get("capability", [""])[0]
        self._send(None, raw=f"payload-{cap[:8]}".encode())

    def do_POST(self):
        if not self._auth():
            return
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        cid = body.get("challenge")
        now = time.time()
        if body.get("op") in ("start", "retry", None):
            cap = os.urandom(32).hex()
            with lock:
                state["attempts"][cid] = cap
            iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + f".{int(t % 1 * 1000):03d}Z"  # noqa: E731
            self._send({"attempt_id": os.urandom(8).hex(), "started_at": iso(now), "deadline": iso(now + 8),
                        "answer_ids": ["x"], "questions": [{"id": "x", "artifact": "evidence.bin"}],
                        "artifacts": [{"download": f"/?op=download&capability={cap}", "filename": "evidence.bin"}]})
        elif body.get("op") == "submit":
            want = f"payload-{state['attempts'].get(cid, '')[:8]}"
            ok = body.get("answers", {}).get("x") == want
            self._send({"result": "CORRECT" if ok else "INCORRECT", "remaining": [] if ok else ["x"]})
        else:
            self._send({"error": "bad op"}, 400)


srv = ThreadingHTTPServer(("127.0.0.1", 0), GM)
threading.Thread(target=srv.serve_forever, daemon=True).start()
gm_url = f"http://127.0.0.1:{srv.server_address[1]}"

tmp = Path(tempfile.mkdtemp(dir=ROOT / ".run"))
rel = tmp.relative_to(ROOT)
sdir = tmp / "chal" / "solver"
sdir.mkdir(parents=True)
(tmp / "chal" / "meta.json").write_text(json.dumps({"lane": "warmups"}))
(sdir / "solve.py").write_text('''import argparse, json, os
from pathlib import Path
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--contract"); ap.add_argument("--artifacts"); a = ap.parse_args()
    data = (Path(a.artifacts) / "evidence.bin").read_bytes().decode()
    leak = any("tok-" in v for v in os.environ.values())
    print(json.dumps({"x": data if not leak else "TOKEN-LEAKED"}))
if __name__ == "__main__":
    main()
''')
log_path = ROOT / ".run" / "hb_daemon.log"
log_before = log_path.read_text() if log_path.exists() else ""
d = workers.HbDaemon(log=lambda m: None, argv=[PY, str(ROOT / "hctf" / "hb_daemon.py"), "--stdio"], gm_url=gm_url,
                     token=TOKEN)
try:
    assert d.call("ping", timeout=10)["ok"]
    w = d.call("warm", timeout=30, solver=str(rel / "chal" / "solver"))
    assert w["ok"] and w.get("error") is None, w

    def one(i):
        return d.call("attempt", timeout=60, cid=f"warmups-day-99-{i}/time_trial", solver=str(rel / "chal" / "solver"),
                      op_mode="start", opts={"HCTF_RUN_FOR_TIME": "1"})["result"]
    t0 = time.time()
    with ThreadPoolExecutor(5) as ex:
        results = list(ex.map(one, range(5)))
    assert all(r["result"] == "correct" for r in results), [r.get("result") or r for r in results]
    assert all(r["submitted"]["x"].startswith("payload-") for r in results), results[0]["submitted"]
    assert state["auth_bad"] == 0, state
    solve_ms = [r["phases"]["solve"] for r in results]
    print(f"ok  daemon: 5 concurrent attempts correct in {time.time() - t0:.2f}s (solve phases {solve_ms} s); "
          "bearer sent on every call, never in the solver's environment")
    # solver change -> the zygote re-warms (new answers), no restart needed
    (sdir / "solve.py").write_text((sdir / "solve.py").read_text().replace('data if not leak', '"v2-" + data if not leak'))
    r = one(9)
    assert r["result"] == "incorrect" and r["submitted"]["x"].startswith("v2-payload-"), r.get("submitted")
    print("ok  daemon: solver edited -> zygote re-warmed on the next solve (signature check)")
    # solve timeout -> hb_timed's TimeoutExpired path (exec_error + solver_too_slow), daemon still healthy
    (sdir / "solve.py").write_text("import time\nif __name__ == '__main__':\n    time.sleep(60)\n")
    r = one(10)
    assert r["result"] in ("exec_error", "expired") and ("solver_too_slow" in r or r.get("clock_short")), r
    assert d.call("ping", timeout=10)["ok"]
    print(f"ok  daemon: a hung solver is cut at the solve budget ({r['result']}), daemon keeps serving")
finally:
    d.close()
    srv.shutdown()
log_new = (log_path.read_text() if log_path.exists() else "")[len(log_before):]
assert TOKEN not in log_new and "attempt warmups-day-99-0/time_trial" in log_new, log_new[-500:]
r = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True)
assert TOKEN not in r.stdout
print("ok  daemon: token absent from the daemon log and from every process's argv")

# 3) the client falls back when the daemon can't start (bad command) and backs off before retrying
try:
    workers.HbDaemon(log=lambda m: None, argv=[PY, "-c", "import sys; sys.stdin.readline()"], gm_url=gm_url, token="t")
    raise AssertionError("a daemon that never says hello must not be accepted")
except workers.DaemonError:
    pass
saved = (workers.HB_DAEMON, dict(workers._daemon))
try:
    workers.HB_DAEMON = True
    workers._daemon.update(d=None, failed_at=time.time())
    assert workers.hb_daemon(log=lambda m: None) is None      # recent failure -> no retry storm, ssh-exec path
finally:
    workers.HB_DAEMON = saved[0]
    workers._daemon.clear()
    workers._daemon.update(saved[1])
print("ok  client: a daemon that never comes up is rejected; recent failure -> per-attempt ssh path, no retry storm")

import shutil  # noqa: E402
shutil.rmtree(tmp, ignore_errors=True)
print("\nALL HB-DAEMON CHECKS PASSED")
