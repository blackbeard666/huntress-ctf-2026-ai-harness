#!/usr/bin/env python3
"""Tests for lib.solverrt: fast exit, single emit, partial-emit-on-deadline, as-completed set collection.
emit_and_exit() calls os._exit(0), so each case runs in a subprocess and we inspect its stdout + rc.
Run: python3 tests/test_solverrt.py"""
import json
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(body, deadline_in=None, timeout=25):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    if deadline_in is not None:
        env["HCTF_SOLVE_DEADLINE"] = str(time.time() + deadline_in)
    else:
        env.pop("HCTF_SOLVE_DEADLINE", None)
    return subprocess.run([sys.executable, "-c", textwrap.dedent(body)],
                          capture_output=True, text=True, env=env, timeout=timeout)


def _json_lines(out):
    return [l for l in out.strip().splitlines() if l.startswith("{")]


def test_emit_prints_and_exits_zero():
    r = _run("from lib import solverrt\nsolverrt.emit_and_exit({'a': '1'})\nprint('UNREACHABLE')")
    assert r.returncode == 0, r
    assert json.loads(_json_lines(r.stdout)[-1]) == {"a": "1"}
    assert "UNREACHABLE" not in r.stdout, "os._exit must skip code after emit_and_exit"


def test_single_emit_under_race():
    r = _run('''
        import threading, time
        from lib import solverrt
        threading.Thread(target=lambda: solverrt.emit_and_exit({"w": "1"}), daemon=True).start()
        time.sleep(0.2)
        solverrt.emit_and_exit({"m": "1"})
    ''')
    assert r.returncode == 0, r
    assert len(_json_lines(r.stdout)) == 1, f"exactly one JSON line, got: {r.stdout!r}"


def test_partial_emit_on_deadline():
    r = _run('''
        import time
        from lib import solverrt
        def solve(job):
            name, delay = job
            time.sleep(delay)
            return {name: "ok"}
        out, pool = {}, []
        solverrt.arm_deadline(out, pool, margin=0.3)
        solverrt.run_sets([("fast", 0.2), ("slow", 20.0)], solve, out, pool, io_bound=True)
        solverrt.emit_and_exit(out, pool)
    ''', deadline_in=1.0)
    assert r.returncode == 0, r
    got = json.loads(_json_lines(r.stdout)[-1])
    assert got.get("fast") == "ok", f"partial must contain the finished set: {got}"
    assert "slow" not in got, f"the unfinished set must be absent: {got}"


def test_run_sets_collects_all_when_fast():
    r = _run('''
        from lib import solverrt
        def solve(job):
            return {job: "ok"}
        out, pool = {}, []
        solverrt.run_sets(["a", "b", "c"], solve, out, pool)
        solverrt.emit_and_exit(out, pool)
    ''')
    assert r.returncode == 0, r
    assert json.loads(_json_lines(r.stdout)[-1]) == {"a": "ok", "b": "ok", "c": "ok"}, r.stdout


def test_sequential_path_when_parallel_disabled():
    env_body = '''
        import os
        os.environ["HCTF_SOLVER_PARALLEL"] = "0"
        from lib import solverrt
        def solve(job):
            return {job: "ok"}
        out, pool = {}, []
        solverrt.run_sets(["a", "b"], solve, out, pool)
        assert pool == [], pool
        solverrt.emit_and_exit(out, pool)
    '''
    r = _run(env_body)
    assert r.returncode == 0, r
    assert json.loads(_json_lines(r.stdout)[-1]) == {"a": "ok", "b": "ok"}, r.stdout


def test_no_deadline_no_watchdog():
    r = _run('''
        from lib import solverrt
        t = solverrt.arm_deadline({}, [])
        print("WATCHDOG", t)
    ''')
    assert r.returncode == 0, r
    assert "WATCHDOG None" in r.stdout, r.stdout


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}: {e!r}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
