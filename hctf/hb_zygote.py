#!/usr/bin/env python3
"""Warm solver zygote: ONE solver dir pre-loaded, every solve a fork of it.

A fresh `python3 solve.py` costs 150-230 ms on the 2-vCPU Homebase VM before the solver does any work (interpreter +
imports: lib.*, androguard, capstone, ...); a fork of a process that already ran the solver's top level costs 15-51 ms
(measured 2026-10-12, identical answers). hb_daemon starts one zygote per solver dir (separate processes: no fork from
a threaded process, no module-name clashes between lanes/days) and sends it solve requests.

Warm-up: `runpy.run_path(solve.py, run_name="hctf_warm")` -- the top level only (imports + defs; every solver and the
skeleton guard main() with `if __name__ == "__main__"`). Each solve: fork -> the child gets its own process group,
stdout/stderr redirected to files at the fd level (so tools the solver spawns write there too), sys.argv/env set, then
`runpy.run_path(solve.py, run_name="__main__")`. Globals a solve mutates die with its fork.

Protocol (single-threaded event loop; requests are served concurrently -- Mastery sets fork in parallel):
  stdin  JSON lines {"id", "args": [...], "env": {...}, "timeout": s}      ({"op": "exit"} ends the zygote)
  stdout JSON lines {"ready": true, "warm_ms", "error"} once, then {"id", "rc", "stdout", "stderr", "timed_out", "ms"}
Usage: python3 hb_zygote.py <solver_dir>      (cwd = the project root on Homebase, ~/hw)
"""
import json
import os
import runpy
import select
import signal
import sys
import tempfile
import time

SOLVER_DIR = os.path.abspath(sys.argv[1])
SOLVE = os.path.join(SOLVER_DIR, "solve.py")
HW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("HCTF_ZYGOTE_TMP") or ("/dev/shm" if os.path.isdir("/dev/shm") else tempfile.gettempdir())
OUT = sys.stdout                      # the protocol channel (the fork's fd 1 is redirected away from it)


def send(obj):
    OUT.write(json.dumps(obj) + "\n")
    OUT.flush()


def warm():
    for p in (HW, SOLVER_DIR):
        if p not in sys.path:
            sys.path.insert(0, p)
    saved = sys.argv
    sys.argv = [SOLVE]
    t = time.time()
    try:
        runpy.run_path(SOLVE, run_name="hctf_warm")
        err = None
    except SystemExit:
        err = None
    except BaseException as e:  # noqa: BLE001 - a solver whose top level fails still runs (cold) in the fork
        err = f"{type(e).__name__}: {str(e)[:200]}"
    finally:
        sys.argv = saved
    return round((time.time() - t) * 1000, 1), err


def fork_solve(req):
    """-> (pid, out_path, err_path, t0)."""
    fd_o, out_path = tempfile.mkstemp(prefix="zyg-o-", dir=TMP)
    fd_e, err_path = tempfile.mkstemp(prefix="zyg-e-", dir=TMP)
    t0 = time.time()
    pid = os.fork()
    if pid == 0:                                          # child
        code = 0
        try:
            os.setpgid(0, 0)
            sys.stdout.flush()
            os.dup2(fd_o, 1)
            os.dup2(fd_e, 2)
            os.close(fd_o)
            os.close(fd_e)
            devnull = os.open(os.devnull, os.O_RDONLY)
            os.dup2(devnull, 0)
            sys.stdout = os.fdopen(1, "w", buffering=1)
            sys.stderr = os.fdopen(2, "w", buffering=1)
            env = req.get("env")
            if env is not None:
                os.environ.clear()
                os.environ.update({str(k): str(v) for k, v in env.items()})
            sys.argv = [SOLVE, *[str(a) for a in req.get("args") or []]]
            try:
                runpy.run_path(SOLVE, run_name="__main__")
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
                if e.code not in (None, 0) and not isinstance(e.code, int):
                    print(e.code, file=sys.stderr)
            except BaseException:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                code = 1
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            os._exit(code)
    os.close(fd_o)
    os.close(fd_e)
    return pid, out_path, err_path, t0


def reap(job, rc, timed_out):
    pid, out_path, err_path, t0 = job["proc"]
    data = {}
    for k, p in (("stdout", out_path), ("stderr", err_path)):
        try:
            with open(p, errors="replace") as f:
                data[k] = f.read()
        except OSError:
            data[k] = ""
        try:
            os.unlink(p)
        except OSError:
            pass
    send({"id": job["id"], "rc": rc, "timed_out": timed_out, "ms": round((time.time() - t0) * 1000, 1), **data})


def kill(pid, sig):
    try:
        os.killpg(pid, sig)
    except (ProcessLookupError, PermissionError):
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass


def main():
    warm_ms, err = warm()
    send({"ready": True, "warm_ms": warm_ms, "error": err, "pid": os.getpid()})
    jobs = {}                                             # pid -> job
    buf = b""
    stdin = sys.stdin.buffer.raw if hasattr(sys.stdin.buffer, "raw") else sys.stdin.buffer
    eof = False
    while not (eof and not jobs):
        r, _, _ = select.select([] if eof else [stdin], [], [], 0.003 if jobs else 0.5)
        if r:
            chunk = os.read(stdin.fileno(), 1 << 20)
            if not chunk:
                eof = True
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                if not line.strip():
                    continue
                req = json.loads(line)
                if req.get("op") == "exit":
                    eof = True
                    continue
                job = {"id": req.get("id"), "deadline": time.time() + float(req.get("timeout") or 60)}
                job["proc"] = fork_solve(req)
                jobs[job["proc"][0]] = job
        for pid, job in list(jobs.items()):
            done, status = os.waitpid(pid, os.WNOHANG)
            if done:
                del jobs[pid]
                reap(job, os.waitstatus_to_exitcode(status), job.get("timed_out", False))
            elif time.time() > job["deadline"]:
                if not job.get("timed_out"):
                    job["timed_out"] = True               # SIGINT first: the traceback names the slow loop
                    kill(pid, signal.SIGINT)
                    job["deadline"] = time.time() + 2
                else:
                    kill(pid, signal.SIGKILL)
                    job["deadline"] = time.time() + 5


if __name__ == "__main__":
    main()
