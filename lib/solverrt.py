"""Solver runtime: fast exit + partial-emit-on-deadline, shared by every lane's solver (via the skeleton)
and by the web lane (lib.websolve re-exports emit_and_exit).

Why this exists (Day 21 post-mortem): a solver that is still computing when the timed runner's
HCTF_SOLVE_DEADLINE passes gets SIGKILLed with NO output -> the attempt is scored `exec_error`
("solver too slow for the window") with nothing to finish in-attempt, which forced a blocking
generalize onto the critical path (warmups Mastery, ~100 s; and every web Mastery). The fix is a board-
wide contract:
  * `arm_deadline(out, pool)` -- a daemon watchdog that, just before the deadline, prints WHATEVER has
    been collected so far (a partial the untimed runner can finish in-attempt) and exits promptly.
  * `run_sets(...)` -- collects each set's answers AS IT FINISHES (as_completed), so `out` grows with
    partials instead of being empty until every set is done.
  * `emit_and_exit(out, pool)` -- print the JSON line once (flushed), hard-kill any pool/race children
    so a lingering non-daemon pool / poll loop cannot hold the process open, then os._exit(0).

All three coordinate on ONE `out` dict and ONE `pool` list (passed by reference) and a single emit
guard, so the watchdog and the normal path never double-print or race.
"""
import json
import os
import sys
import threading
import time

_emit_lock = threading.Lock()
_emitted = False


def emit_and_exit(out, pool=()):
    """Print `out` as one JSON line (the harness reads the last line), flush, hard-kill `pool` procs,
    then os._exit(0). Idempotent: only the first caller prints; a second (e.g. the watchdog racing the
    normal path) is a no-op. Call ONLY from the solver's main process, after answers are collected."""
    global _emitted
    with _emit_lock:
        if _emitted:
            return
        _emitted = True
    try:
        sys.stdout.write(json.dumps(out) + "\n")
        sys.stdout.flush()
    except Exception as e:  # noqa: BLE001 - never die before the kill/exit below
        try:
            sys.stderr.write(f"emit failed: {e!r}\n")
        except Exception:
            pass
    for p in pool or ():
        try:
            p.kill()
        except Exception:  # noqa: BLE001
            pass
    try:
        sys.stderr.flush()
    except Exception:  # noqa: BLE001
        pass
    os._exit(0)


def _deadline(margin):
    """HCTF_SOLVE_DEADLINE (epoch) minus a safety margin, or None when unset (untimed single solve)."""
    try:
        return float(os.environ["HCTF_SOLVE_DEADLINE"]) - margin
    except (KeyError, ValueError):
        return None


def arm_deadline(out, pool, margin=0.6):
    """Start a daemon watchdog that emits the partial `out` (and kills `pool`) just before the solve
    deadline. `out` and `pool` are shared by reference with the solver's main loop, so whatever has been
    collected by deadline is what gets printed. No-op (returns None) when there is no deadline."""
    end = _deadline(margin)
    if end is None:
        return None

    def _fire():
        while time.time() < end:
            time.sleep(0.1)
        emit_and_exit(out, list(pool))

    t = threading.Thread(target=_fire, name="solve-deadline", daemon=True)
    t.start()
    return t


def run_sets(jobs, solve_fn, out, pool, io_bound=False):
    """Run solve_fn(job)->dict for each job, merging each result into `out` AS IT COMPLETES (so `out`
    holds partials if we are cut off), and recording live pool procs into `pool` (so arm_deadline's
    watchdog can kill them). Forks one process per job when there are >=2 and HCTF_SOLVER_PARALLEL!='0';
    `io_bound` sizes the pool per job (live targets wait on I/O, not CPU) rather than per CPU. Falls back
    to a sequential loop on any pool error. Returns `out`."""
    jobs = list(jobs)
    if len(jobs) >= 2 and os.environ.get("HCTF_SOLVER_PARALLEL", "1") != "0":
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor, as_completed
        workers = len(jobs) if io_bound else min(len(jobs), os.cpu_count() or 2)
        try:
            ex = ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("fork"))
            futs = [ex.submit(solve_fn, j) for j in jobs]
            pool.extend((getattr(ex, "_processes", None) or {}).values())
            for f in as_completed(futs):
                try:
                    out.update(f.result())
                except Exception as e:  # noqa: BLE001 - one bad set must not sink the others
                    print(f"set failed: {e!r}", file=sys.stderr)
                pool[:] = list((getattr(ex, "_processes", None) or {}).values())
            return out
        except Exception as e:  # noqa: BLE001 - never lose a solve to the pool
            print(f"parallel sets failed ({e!r}); sequential", file=sys.stderr)
    for j in jobs:
        try:
            out.update(solve_fn(j))
        except Exception as e:  # noqa: BLE001
            print(f"set failed: {e!r}", file=sys.stderr)
    return out
