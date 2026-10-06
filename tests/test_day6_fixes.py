"""Behavior checks for the Day 6 harness fixes (no GM / no Homebase traffic: remote.ssh is stubbed)."""
import io, sys, threading, time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from hctf import cli, workers, remote

# 1) cli.quiet(): thread-local; never swaps sys.stdout; concurrent quiet/unquiet threads can't strand stdout.
real = sys.stdout
buf = io.StringIO()
sys.stdout = buf
def noisy():
    for _ in range(200):
        with cli.quiet():
            cli.emit({"x": 1})
errs = []
ts = [threading.Thread(target=noisy) for _ in range(5)]
[t.start() for t in ts]
cli.emit({"visible": True})
[t.join() for t in ts]
sys.stdout = real
out = buf.getvalue()
assert '"visible": true' in out, out
assert '"x": 1' not in out, "quiet() leaked another thread's output"
print("ok  quiet(): thread-local, main thread still prints, stdout never swapped")

# 2) _homebase_ready(): non-blocking verdict from the health thread; a failure is never latched.
seq = iter([False, True])
remote.probe = lambda timeout=8: next(seq, True)
workers._hb.update(provisioned=True, ok=False, checked=0.0, thread=object())  # no real health thread in the test
assert workers._homebase_ready() is False, "dead probe -> not ready"
workers._hb["checked"] = 0.0                                                  # verdict went stale -> re-probe
assert workers._homebase_ready() is True, "must recover on the next probe (no latch)"
workers._hb.update(ok=False, checked=time.time())
t = time.time(); assert workers._homebase_ready() is False and time.time() - t < 0.1, "fresh verdict: no SSH, instant"
print("ok  _homebase_ready(): non-blocking, re-probes a stale verdict, never latches a failure")

# 3) worker_effort(): LANE_EFFORT is a raise-only floor.
workers.WORKER_EFFORT = "high"
workers.LANE_EFFORT["script-analysis"] = "xhigh"
assert workers.worker_effort("script-analysis") == "xhigh" and workers.worker_effort("warmups") == "high"
workers.WORKER_EFFORT = "max"
assert workers.worker_effort("script-analysis") == "max", "a floor must never lower the global effort"
print("ok  worker_effort(): script/binary floor xhigh, never lowers a higher global")

# 5) No Chain method may be silently shadowed by a second definition (Day 6: the early-handoff _snapshot_solver(cid)
#    replaced generalize()'s _snapshot_solver(), so every generalize would have raised TypeError).
import ast, collections, pathlib
tree = ast.parse((pathlib.Path(__file__).resolve().parents[1] / "hctf" / "orchestrate.py").read_text())
for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
    dup = [k for k, v in collections.Counter(f.name for f in cls.body if isinstance(f, ast.FunctionDef)).items() if v > 1]
    assert not dup, f"{cls.name} defines {dup} more than once"
print("ok  orchestrate.py: no duplicate method definitions")
