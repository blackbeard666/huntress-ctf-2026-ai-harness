"""Process governance for solver runs: every run in its own process group (killed as a GROUP on timeout), and a
BACKGROUND class for work that is not on a mode's critical path.

D16 (2026-10-16): the five handoff probes, the new-id hold, the green watcher and speed-harden ran solvers at the same
time as the timed attempts. Each run forked a ProcessPoolExecutor(cpu_count). Load reached 27 on 12 cores: binary TT
took 68.6 s (the solver alone is 1.4 s) and the metadata reuse race 59.5 s. ~20 solve.py forks were orphaned because a
timeout killed only the leader. In the post-run, test_solver(parallel=8) x per-solver pools hit ~57 processes x 195 MB
and the kernel OOM killed WSL itself.

Background runs (thread-local flag, inherited by procgov.Executor pools, or process default for the post-run):
  * a global slot limit (HCTF_BG_SOLVERS, default 4), waiting for a slot is fine
  * nice 15, pinned to the top third of the cores, so the critical path keeps the rest
  * HCTF_SOLVER_PARALLEL=0 (the solver skeleton's switch: no per-run fork pool, one process per run)
  * oom_score_adj 800 (the kernel takes these first, never WSL init); foreground runs get 300
"""
import contextlib
import os
import signal
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

BG_SOLVERS = max(1, int(os.environ.get("HCTF_BG_SOLVERS", "4")))
BG_NICE = int(os.environ.get("HCTF_BG_NICE", "15"))
BG_OOM_ADJ = int(os.environ.get("HCTF_BG_OOM_ADJ", "800"))
FG_OOM_ADJ = int(os.environ.get("HCTF_FG_OOM_ADJ", "300"))
GOVERN = os.environ.get("HCTF_PROC_GOVERN", "1") != "0"

_tls = threading.local()
_default_bg = os.environ.get("HCTF_PROC_BG") == "1"     # a whole process marked background (mutate probe, post-run)
_bg_sem = threading.BoundedSemaphore(BG_SOLVERS)
_live = {}                # pid -> owner tag of every governed process still running
_live_lock = threading.Lock()
_stats = {"bg_runs": 0, "fg_runs": 0, "group_kills": 0, "bg_wait_s": 0.0}
_stats_lock = threading.Lock()


def bg_cpus():
    """The cores background runs are pinned to: the top third (at least 2) of what this process may use."""
    try:
        cpus = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        return None
    n = max(2, len(cpus) // 3)
    return set(cpus[-n:]) if len(cpus) > n else None


def is_bg():
    v = getattr(_tls, "bg", None)
    return _default_bg if v is None else v


def set_default_background(on=True):
    """Mark the whole process background (the post-run: speed-harden / train / prebuild gates)."""
    global _default_bg
    _default_bg = bool(on)


@contextlib.contextmanager
def background(on=True):
    prev = getattr(_tls, "bg", None)
    _tls.bg = bool(on)
    try:
        yield
    finally:
        _tls.bg = prev


def owner():
    return getattr(_tls, "owner", None)


def bg_wrap(fn, on=True, owner_tag=None):
    """fn run with the background flag (and an owner tag: the chain that may kill_owner() it) set in whatever thread
    executes it (ThreadPoolExecutor.submit / Thread targets)."""
    def run(*a, **k):
        prev = getattr(_tls, "owner", None)
        _tls.owner = owner_tag if owner_tag is not None else prev
        try:
            with background(on):
                return fn(*a, **k)
        finally:
            _tls.owner = prev
    return run


class Executor(ThreadPoolExecutor):
    """A ThreadPoolExecutor whose tasks inherit the SUBMITTING thread's background flag and owner tag."""
    def submit(self, fn, /, *args, **kwargs):
        return super().submit(bg_wrap(fn, is_bg(), owner()), *args, **kwargs)


def kill_owner(tag):
    """SIGKILL the process group of every governed run started under owner `tag` that is still alive (a finished
    chain's leftover probes). Returns how many groups were signalled."""
    with _live_lock:
        pids = [pid for pid, t in _live.items() if t == tag]
    n = 0
    for pid in pids:
        try:
            os.killpg(pid, signal.SIGKILL)
            n += 1
        except OSError:
            pass
    return n


def _preexec(bg, cpus):
    def f():
        try:
            with open("/proc/self/oom_score_adj", "w") as fh:
                fh.write(str(BG_OOM_ADJ if bg else FG_OOM_ADJ))
        except OSError:
            pass
        if bg:
            try:
                os.nice(BG_NICE)
            except OSError:
                pass
            if cpus:
                try:
                    os.sched_setaffinity(0, cpus)
                except OSError:
                    pass
    return f


def kill_group(p, sig=signal.SIGKILL):
    """Kill p's whole process group (p was started with start_new_session=True). Never raises."""
    try:
        os.killpg(p.pid, sig)
        with _stats_lock:
            _stats["group_kills"] += 1
    except (ProcessLookupError, PermissionError, OSError):
        pass


def run(cmd, timeout=None, background=None, env=None, grace=0.0, input=None, **kw):
    """subprocess.run() replacement: own session, group kill on timeout (and a sweep of leftover forks after a normal
    exit), background class when background is True (or None and the calling thread / process is background).
    grace > 0: SIGINT first and wait `grace` s (a traceback at the hot loop), then SIGKILL the group.
    Raises subprocess.TimeoutExpired like subprocess.run (output attached)."""
    bg = is_bg() if background is None else bool(background)
    if not GOVERN:
        return subprocess.run(cmd, timeout=timeout, env=env, input=input, capture_output=True, text=True, **kw)
    env = dict(os.environ if env is None else env)
    cpus = None
    if bg:
        env["HCTF_SOLVER_PARALLEL"] = "0"
        cpus = bg_cpus()
    import time as _t
    t_wait = _t.time()
    if bg:
        _bg_sem.acquire()
    try:
        with _stats_lock:
            _stats["bg_runs" if bg else "fg_runs"] += 1
            _stats["bg_wait_s"] += _t.time() - t_wait if bg else 0.0
        kw.setdefault("stdout", subprocess.PIPE)
        kw.setdefault("stderr", subprocess.PIPE)
        p = subprocess.Popen(cmd, env=env, text=True, start_new_session=True, preexec_fn=_preexec(bg, cpus),
                             stdin=subprocess.PIPE if input is not None else None, **kw)
        with _live_lock:
            _live[p.pid] = owner()
        try:
            out, err = p.communicate(input=input, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            out = err = ""
            if grace > 0:
                kill_group(p, signal.SIGINT)
                try:
                    out, err = p.communicate(timeout=grace)
                except subprocess.TimeoutExpired:
                    pass
            kill_group(p)
            try:
                o2, e2 = p.communicate(timeout=5)
                out, err = (out or "") + (o2 or ""), (err or "") + (e2 or "")
            except (subprocess.TimeoutExpired, ValueError, OSError):
                pass
            raise subprocess.TimeoutExpired(cmd, timeout, output=out, stderr=err) from e
        kill_group(p)       # forks a solver left behind after it exited (a pool that never joined)
        return subprocess.CompletedProcess(cmd, p.returncode, out, err)
    finally:
        if "p" in locals():
            with _live_lock:
                _live.pop(p.pid, None)
        if bg:
            _bg_sem.release()


def stats():
    with _stats_lock:
        return dict(_stats)
