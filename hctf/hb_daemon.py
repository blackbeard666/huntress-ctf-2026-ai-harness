#!/usr/bin/env python3
"""Homebase timed-attempt daemon: one long-lived process per run, driven over ONE persistent ssh stdio channel.

Per attempt it saves the ssh exec + interpreter start + GM pool warm-up (~0.6-1.0 s before the clock) and, inside the
clock, the solver's interpreter start (warm zygote fork: 15-51 ms vs 150-230 ms) and ~60 ms per GM call (public GM over
HTTPS with the bearer: 170 ms vs 232 ms through the inside proxy). The attempt itself is hb_timed.run_attempt -- every GM
rule stays in hb_timed; only the solver launch (hb_timed.SOLVER -> a zygote, see hb_zygote.py) differs.

Protocol: JSON lines on stdin/stdout.
  first line  {"hello": 1, "gm": "<GM base url>", "token": "<bearer or null>"}   (token kept in memory only: never
              env/argv/disk/log -- the solvers' environment never sees it)
  requests    {"id", "op": "ping" | "warm" | "attempt" | "shutdown", ...}
              warm    {"solver": "<dir rel to ~/hw>"}
              attempt {"cid", "solver", "op": "start"|"retry", "min_left", "opts": {HCTF_* knobs}}
  responses   {"id", "ok": true, ...} / {"id", "ok": false, "error"}; one thread per request (5 chains at once).
Usage (Homebase, cwd ~/hw): python3 hctf/hb_daemon.py --stdio
"""
import json
import os
import subprocess
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path
from types import SimpleNamespace

HW = Path(__file__).resolve().parent.parent
LOG = HW / ".run" / "hb_daemon.log"
_out_lock = threading.Lock()


def log(msg):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a") as f:
            f.write(time.strftime("%H:%M:%S ") + msg + "\n")
    except OSError:
        pass


def send(obj):
    with _out_lock:
        sys.stdout.write(json.dumps(obj) + "\n")
        sys.stdout.flush()


def _sig(sdir):
    sdir = Path(sdir)
    return tuple(sorted((str(f.relative_to(sdir)), f.stat().st_mtime_ns, f.stat().st_size) for f in sdir.rglob("*")
                        if f.is_file() and "cases" not in f.relative_to(sdir).parts and "__pycache__" not in f.parts))


class Zygote:
    """One hb_zygote.py process for one solver dir; solve() is thread-safe."""

    def __init__(self, sdir):
        self.sdir, self.sig = str(sdir), _sig(sdir)
        self.p = subprocess.Popen([sys.executable, str(HW / "hctf" / "hb_zygote.py"), self.sdir], cwd=str(HW),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                  env=dict(os.environ, PYTHONPATH=str(HW)))
        hello = json.loads(self.p.stdout.readline() or "{}")
        if not hello.get("ready"):
            raise RuntimeError(f"zygote for {sdir} did not start")
        self.warm_ms, self.warm_error = hello.get("warm_ms"), hello.get("error")
        self.lock, self.pending = threading.Lock(), {}
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.p.stdout:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            slot = self.pending.pop(r.get("id"), None)
            if slot:
                slot[1].update(r)
                slot[0].set()
        for ev, res in list(self.pending.values()):     # zygote died: wake everyone
            res.update(dead=True)
            ev.set()

    def alive(self):
        return self.p.poll() is None

    def solve(self, args, env, timeout):
        rid, ev, res = uuid.uuid4().hex, threading.Event(), {}
        self.pending[rid] = (ev, res)
        with self.lock:
            self.p.stdin.write(json.dumps({"id": rid, "args": args, "env": env, "timeout": timeout}) + "\n")
            self.p.stdin.flush()
        ev.wait(timeout + 10)
        if res.get("dead") or not res:
            raise RuntimeError("zygote died mid-solve")
        if res.get("timed_out"):
            raise subprocess.TimeoutExpired(["solve.py", *args], timeout, output=res.get("stdout"), stderr=res.get("stderr"))
        return SimpleNamespace(stdout=res.get("stdout", ""), stderr=res.get("stderr", ""), returncode=res.get("rc"))

    def close(self):
        try:
            self.p.stdin.write('{"op": "exit"}\n')
            self.p.stdin.flush()
        except (OSError, ValueError):
            pass


class Zygotes:
    def __init__(self):
        self.lock, self.by_dir = threading.Lock(), {}

    def get(self, sdir):
        sdir = str(Path(sdir).resolve())
        with self.lock:
            z = self.by_dir.get(sdir)
            if z is not None and z.alive() and z.sig == _sig(sdir):
                return z
            if z is not None:
                z.close()                                  # solver changed (generalize) or died: re-warm
            z = self.by_dir[sdir] = Zygote(sdir)
            log(f"zygote {Path(sdir).parent.name}: warm {z.warm_ms} ms{' (' + z.warm_error + ')' if z.warm_error else ''}")
            return z

    def solve(self, solve_path, args, env, timeout):
        """hb_timed.SOLVER: a zygote fork; a cold interpreter if the zygote can't be had."""
        try:
            return self.get(Path(solve_path).parent).solve(args, env, timeout)
        except subprocess.TimeoutExpired:
            raise
        except Exception as e:  # noqa: BLE001 - never lose an attempt to the warm path
            log(f"zygote fallback ({e}); cold solve")
            return subprocess.run([sys.executable, solve_path, *args], capture_output=True, text=True, timeout=timeout,
                                  env=env)

    def close(self):
        for z in self.by_dir.values():
            z.close()


def main():
    hello = json.loads(sys.stdin.readline() or "{}")
    if hello.get("gm"):
        os.environ["HUNTRESS_GAME_MASTER_URL"] = hello["gm"]     # hb_timed reads it at import
    sys.path.insert(0, str(HW / "hctf"))
    import hb_timed
    hb_timed._TOKEN = hello.get("token") or None
    zyg = Zygotes()
    hb_timed.SOLVER = zyg.solve
    try:
        hb_timed._pool()                                          # TLS handshakes now, not inside the first clock
    except Exception as e:  # noqa: BLE001
        log(f"pool warm note: {e}")
    log(f"up: gm={hb_timed.GM} bearer={'yes' if hb_timed._TOKEN else 'no'} pid={os.getpid()}")
    send({"id": "hello", "ok": True, "pid": os.getpid(), "gm": hb_timed.GM})

    def handle(req):
        rid, op = req.get("id"), req.get("op")
        try:
            if op == "ping":
                send({"id": rid, "ok": True, "zygotes": len(zyg.by_dir)})
            elif op == "warm":
                z = zyg.get(HW / req["solver"])
                send({"id": rid, "ok": True, "warm_ms": z.warm_ms, "error": z.warm_error})
            elif op == "attempt":
                t = time.time()
                out = hb_timed.run_attempt(req["cid"], req["solver"], op=req.get("op_mode") or "start",
                                           min_left=req.get("min_left"), opts=req.get("opts"))
                out["daemon_s"] = round(time.time() - t, 2)
                log(f"attempt {req['cid']}: {out.get('result')} elapsed={out.get('elapsed')}")
                send({"id": rid, "ok": True, "result": out})
            else:
                send({"id": rid, "ok": False, "error": f"unknown op {op!r}"})
        except Exception as e:  # noqa: BLE001
            log(f"{op} failed: {traceback.format_exc()[-800:]}")
            send({"id": rid, "ok": False, "error": f"{type(e).__name__}: {str(e)[:300]}"})

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue
        if req.get("op") == "shutdown":
            send({"id": req.get("id"), "ok": True})
            break
        threading.Thread(target=handle, args=(req,), daemon=True).start()
    zyg.close()
    log("down")


if __name__ == "__main__":
    if "--stdio" not in sys.argv:
        sys.exit(__doc__)
    main()
