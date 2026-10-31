"""D31 generalize concurrency (D30 warmups Mastery: solver/ left with ONE case dir and no solve.py), offline: toy solver in
a temp dir, stubbed workers -- no GM, no LLM.

D30 (.run/day30.log, warmups-day-30): the early (contract-ahead) generalize started 09:19:57 and was not adopted by
_early_join -> the blocked path started a second worker on the same variant (09:20:02 + 09:20:04). Both shared
.generalize-snapshot; at the live pass (09:21:21) both ran _accept_after_live: one rmtree'd the unchanged snapshot, the
other saw a half-deleted one, moved the real solver to .generalize-unjudged and the emptied snapshot into solver/.

 L1  two concurrent generalizes on one solver: never two workers at once; the second waits, then skips when the first
     left changed code (the caller retries on it)
 L2  the D30 shape: early generalize (no live) running, the blocked path's generalize (with the live answer) waits; the
     live pass ends the running worker through the waiter; fast accept; the waiter does not start a worker; solver
     intact (solve.py + every case), no .generalize-unjudged
 L3  the first generalize's edits rejected (code unchanged) -> the waiter runs its own worker afterwards
 G1  _accept_after_live (Mastery) never installs a snapshot without solve.py over a solver that has one
 G2  _restore_snapshot: same guard
 I1  invariant: solver/ lost solve.py during a generalize -> pre-generalize code + the lost cases come back, the case
     recorded after the pass stays
 R   the D30 race itself (both workers end at the live pass, the snapshot rmtree slowed like D30's loaded host): HEAD's
     code without the lock lost solve.py in 5/6 trials (.run/repro_d30.py in the shadow); with the lock: never
 K   kill switch HCTF_GEN_SOLVER_LOCK=0, the lock keyed by real path, speed_harden holds the lock over its re-time

Run:  source bin/env.sh && python3 tests/test_d31_gen.py      (exit 0 = all pass)
"""
import contextlib
import inspect
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, orchestrate as orch  # noqa: E402

failures = []
TMP = Path(tempfile.mkdtemp(prefix="d31gen-", dir=str(ROOT / ".run")))


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {str(detail)[:600]}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


said = []
QUIET = {(orch, "say"): lambda *a, **k: said.append(a[0] if a else "")}

SOLVE = '''import json, sys
from pathlib import Path
here = Path(__file__).resolve().parent
print(json.dumps(json.loads((here / "out.json").read_text())))
'''


def toy_chain(name, n_cases=5):
    chal = TMP / "day30" / f"warmups-{name}"
    sdir = chal / "solver"
    (sdir / "cases").mkdir(parents=True)
    (chal / "meta.json").write_text(json.dumps({"lane": "warmups", "name": name}))
    (sdir / "solve.py").write_text(SOLVE)
    (sdir / "out.json").write_text(json.dumps({"a": "1"}))
    for i in range(n_cases):
        c = sdir / "cases" / f"auto-mastery-{i:08x}"
        (c / "artifacts").mkdir(parents=True)
        (c / "artifacts" / "blob-01.txt").write_bytes(b"blob%d" % i)
        (c / "contract.json").write_text(json.dumps({"answer_ids": ["a"], "questions": [{"id": "a"}]}))
        (c / "expected.json").write_text(json.dumps({"a": "1"}))
    ch = object.__new__(orch.Chain)
    ch.base, ch.pools, ch.gov, ch.only_modes = f"warmups-day-30-{name}", None, mock.Mock(allow_timed=lambda: True), None
    ch.lane, ch.name, ch.sdir, ch.root = "warmups", name, sdir, chal
    cdir = TMP / f"cdir-{name}"
    cdir.mkdir()
    return ch, cdir


def cases(ch):
    return sorted(p.name for p in (ch.sdir / "cases").iterdir()) if (ch.sdir / "cases").is_dir() else []


class Workers:
    """run_worker stub: counts concurrent workers; `edit` writes a change into solve.py; waits for `stop` up to `hold` s."""

    def __init__(self, hold=1.0, edit=False):
        self.hold, self.edit, self.active, self.max_active, self.calls, self.mu = hold, edit, 0, 0, [], threading.Lock()

    def __call__(self, cid, stage, prompt, timeout, stop=None, **k):
        with self.mu:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            self.calls.append((threading.current_thread().name, time.time()))
        try:
            if self.edit:
                sp = self.sdir / "solve.py"
                sp.write_text(sp.read_text() + f"# edit by {threading.current_thread().name}\n")
            if stop is not None:
                stop.wait(self.hold)
            else:
                time.sleep(self.hold)
        finally:
            with self.mu:
                self.active -= 1


class FakeLive:
    """The live answer: passes the mode after `after` s (cli.is_complete follows)."""

    def __init__(self, after):
        self.t0, self.after, self.links, self.attempt = time.time(), after, [], "67adc0ee-x"

    @property
    def passed(self):
        return time.time() - self.t0 >= self.after

    all_accepted = False

    def link(self, evt):
        self.links.append(evt)
        if self.passed:
            evt.set()


def env(ch, cdir, complete=lambda cid: False):
    return {**QUIET, (orch, "set_state"): lambda *a, **k: None,
            (orch, "ensure_case_and_test"): lambda *a, **k: (True, None),
            (orch.timed, "last_result"): lambda cid: {},
            (orch.remote, "gm_transport"): lambda: "remote",   # no variant harvest
            (orch.cli, "cdir"): lambda cid: cdir,
            (orch.cli, "is_complete"): complete,
            (orch, "STOP_WHEN_READY"): False}


CID = "warmups-day-30/mastery"

# ------------------------------------------------------------------ L1 two at once: serialized, second skips on change
ch, cdir = toy_chain("l1")
w = Workers(hold=1.0, edit=True)
w.sdir = ch.sdir
ch.run_worker = w
before = cases(ch)
with patched(env(ch, cdir)):
    said.clear()
    t1 = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {"early": True}), name="early-gen")
    t2 = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {}), name="blocked-gen")
    t1.start()
    time.sleep(0.15)
    t2.start()
    t1.join(30)
    t2.join(30)
check("L1 two concurrent generalizes on one solver -> never two workers at once", w.max_active == 1, w.max_active)
check("L1 the second waited (logged) and skipped: the first left changed code -> ONE worker in all",
      len(w.calls) == 1 and any("waiting for it" in s for s in said) and any("changed the solver" in s for s in said),
      (w.calls, said[-6:]))
check("L1 solver intact: solve.py (with the accepted edit) + every case, no snapshot left",
      "edit by" in (ch.sdir / "solve.py").read_text() and cases(ch) == before
      and not (ch.root / ".generalize-snapshot").exists(), cases(ch))

# ------------------------------------------------------------------ L2 the D30 shape
ch, cdir = toy_chain("l2", n_cases=50)
(ch.sdir / "cases" / "variant-mastery-67adc0ee").mkdir()
(ch.sdir / "cases" / "variant-mastery-67adc0ee" / "contract.json").write_text(
    json.dumps({"answer_ids": ["a"], "questions": [{"id": "a"}]}))
(ch.sdir / "cases" / "variant-mastery-67adc0ee" / "expected.json").write_text("{}")
solve0 = (ch.sdir / "solve.py").read_text()
before = cases(ch)
w = Workers(hold=20.0, edit=False)     # D30: neither worker had edited solve.py when the live answer passed
w.sdir = ch.sdir
ch.run_worker = w
live = FakeLive(after=1.2)
ch._lib_racer = None
with patched(env(ch, cdir, complete=lambda cid: live.passed)):
    said.clear()
    t0 = time.time()
    early = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {"early": True}), name="early-gen")
    early.start()                       # 09:19:57 early generalize (no live answer)
    time.sleep(0.2)
    blocked = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {}), kwargs={"live": live},
                               name="blocked-gen")
    blocked.start()                     # 09:20:04 the blocked path's generalize (racing the live answer)
    early.join(30)
    blocked.join(30)
    dt = time.time() - t0
    # the chain records the passed attempt's case right after (record_timed_case)
    (ch.sdir / "cases" / "mastery-67adc0ee").mkdir(parents=True, exist_ok=True)
check("L2 the live pass ends the RUNNING worker through the waiting generalize (no 20 s hold)", dt < 8, f"{dt:.1f}s")
check("L2 only the early generalize ran a worker; the waiter saw the mode CORRECT and started none",
      len(w.calls) == 1 and w.calls[0][0] == "early-gen" and any("no generalize" in s for s in said), (w.calls, said[-8:]))
check("L2 solver intact: the original solve.py + all 51 cases + the post-pass case; no snapshot, no unjudged dir",
      (ch.sdir / "solve.py").read_text() == solve0 and set(before) <= set(cases(ch)) and "mastery-67adc0ee" in cases(ch)
      and not (ch.root / ".generalize-snapshot").exists() and not (ch.root / ".generalize-unjudged").exists(),
      (cases(ch)[:5], len(cases(ch)), list(ch.root.iterdir())))
check("L2 no D30 'live pass: pre-worker solver kept' swap (the code was unchanged)",
      not any("pre-worker solver kept" in s for s in said), said)

# L2b: same, the early worker HAD edited -> one swap (edits aside), the waiter still starts nothing, solver intact
ch, cdir = toy_chain("l2b", n_cases=10)
solve0 = (ch.sdir / "solve.py").read_text()
before = cases(ch)
w = Workers(hold=20.0, edit=True)
w.sdir = ch.sdir
ch.run_worker = w
live = FakeLive(after=1.0)
ch._lib_racer = None
with patched(env(ch, cdir, complete=lambda cid: live.passed)):
    said.clear()
    early = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {"early": True}), name="early-gen")
    early.start()
    time.sleep(0.2)
    blocked = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {}), kwargs={"live": live},
                               name="blocked-gen")
    blocked.start()
    early.join(30)
    blocked.join(30)
un = ch.root / ".generalize-unjudged"
check("L2b edited + live pass: pre-worker solver kept in solver/, the edits (only) in .generalize-unjudged",
      (ch.sdir / "solve.py").read_text() == solve0 and cases(ch) == before
      and "edit by early-gen" in (un / "solve.py").read_text() and len(w.calls) == 1,
      (cases(ch), w.calls, said[-6:]))
check("L2b exactly one accept-after-live swap", sum("pre-worker solver kept" in s for s in said) == 1, said)

# ------------------------------------------------------------------ L3 first rejected (unchanged) -> waiter runs its own
ch, cdir = toy_chain("l3")
w = Workers(hold=0.6, edit=False)
w.sdir = ch.sdir
ch.run_worker = w
with patched(env(ch, cdir)):
    said.clear()
    t1 = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {"early": True}), name="first")
    t2 = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {}), name="second")
    t1.start()
    time.sleep(0.15)
    t2.start()
    t1.join(30)
    t2.join(30)
check("L3 the first left the code unchanged -> the waiter runs its own worker AFTER it (serial, never overlapping)",
      [c[0] for c in w.calls] == ["first", "second"] and w.max_active == 1 and w.calls[1][1] - w.calls[0][1] >= 0.5,
      w.calls)

# ------------------------------------------------------------------ G1 / G2 snapshot-without-solve.py guards
ch, cdir = toy_chain("g1")
snap = ch._snap_dir()
(snap / "cases").mkdir(parents=True)        # D30: the other generalize's rmtree had emptied it (code sig differs)
solve0 = (ch.sdir / "solve.py").read_text()
before = cases(ch)
with patched(QUIET):
    ch._accept_after_live(CID, "mastery")
check("G1 _accept_after_live (Mastery): a snapshot without solve.py never replaces the solver",
      (ch.sdir / "solve.py").read_text() == solve0 and cases(ch) == before and not snap.exists()
      and not (ch.root / ".generalize-unjudged").exists(), list(ch.root.iterdir()))
(snap / "cases").mkdir(parents=True)
with patched(QUIET):
    ch._restore_snapshot("test")
check("G2 _restore_snapshot: same guard (solver kept, empty snapshot dropped, logged)",
      (ch.sdir / "solve.py").read_text() == solve0 and cases(ch) == before and not snap.exists()
      and any("restore SKIPPED" in s for s in said), said[-3:])
# a real snapshot still restores
shutil.copytree(ch.sdir, snap)
(ch.sdir / "solve.py").write_text("# broken edit\n")
with patched(QUIET):
    ch._restore_snapshot("broke previously-passing cases")
check("G2 ... a complete snapshot still restores as before", (ch.sdir / "solve.py").read_text() == solve0
      and (ch.root / ".generalize-rejected" / "solve.py").read_text() == "# broken edit\n")

# ------------------------------------------------------------------ I1 invariant
ch, cdir = toy_chain("i1", n_cases=6)
solve0 = (ch.sdir / "solve.py").read_text()
before = cases(ch)
w = Workers(hold=0.1)
w.sdir = ch.sdir
ch.run_worker = w


def d30_damage(self, cid, case_timeout=None):
    """What D30's interleaving left: the real solver in .generalize-unjudged, solver/ an empty dir + the post-pass case."""
    un = self.root / ".generalize-unjudged"
    shutil.rmtree(un, ignore_errors=True)
    shutil.move(str(self.sdir), str(un))
    shutil.rmtree(self._snap_dir(), ignore_errors=True)
    (self.sdir / "cases" / "mastery-67adc0ee").mkdir(parents=True)
    (self.sdir / "cases" / "mastery-67adc0ee" / "expected.json").write_text('{"a": "1"}')


with patched({**env(ch, cdir), (orch.Chain, "_accept_or_restore"): d30_damage}):
    said.clear()
    ch.generalize(CID, [("a", None)], {}, {})
check("I1 solver/ without solve.py after a generalize -> the pre-generalize code is written back",
      (ch.sdir / "solve.py").read_text() == solve0 and json.loads((ch.sdir / "out.json").read_text()) == {"a": "1"},
      list(ch.sdir.iterdir()))
check("I1 ... the lost cases come back (hard-linked from .generalize-unjudged) and the post-pass case stays",
      set(before) <= set(cases(ch)) and "mastery-67adc0ee" in cases(ch)
      and (ch.sdir / "cases" / "mastery-67adc0ee" / "expected.json").read_text() == '{"a": "1"}', cases(ch))
check("I1 ... loudly (!!! line)", any(s.startswith("!!!") and "NO solve.py" in s for s in said), said[-3:])
with patched(QUIET):
    res = orch.solvers.test_solver(ch.sdir, timeout=20)
check("I1 ... and the restored solver passes its cases", res and all(r.get("ok") for r in res if r["case"] in before),
      [(r["case"], r.get("ok")) for r in res][:4])
# no solve.py before -> nothing to guarantee (a generalize may start before the single wrote one)
ch2, _ = toy_chain("i1b", n_cases=1)
(ch2.sdir / "solve.py").unlink()
with patched(QUIET):
    check("I1 no solve.py before the generalize -> the invariant does nothing",
          ch2._solver_intact(CID, {}, orch._code_sig(ch2.sdir)) is False and not (ch2.sdir / "solve.py").exists())
# no in-memory copy (too big) -> only a dir holding EXACTLY the pre-generalize code is used
ch3, _ = toy_chain("i1c", n_cases=2)
sig = orch._code_sig(ch3.sdir)
un = ch3.root / ".generalize-unjudged"
shutil.copytree(ch3.sdir, un)
(ch3.sdir / "solve.py").unlink()
rj = ch3.root / ".generalize-rejected"
shutil.copytree(un, rj)
(rj / "solve.py").write_text("# worker edit, never restored as pre-generalize code\n")
with patched(QUIET):
    ok = ch3._solver_intact(CID, None, sig)
check("I1 no in-memory copy -> the code comes from the dir whose code sig matches the pre-generalize solver",
      ok and (ch3.sdir / "solve.py").read_text() == SOLVE, (ch3.sdir / "solve.py").read_text()[:80])

# ------------------------------------------------------------------ R the D30 race (slow snapshot rmtree, both end together)
import types  # noqa: E402
_rm = shutil.rmtree


def slow_rmtree(path, ignore_errors=False, **k):
    """D30's loaded host (load 21-27): the snapshot's top-level files go first, then each case dir takes a while."""
    p = Path(path)
    if p.name != ".generalize-snapshot":
        return _rm(path, ignore_errors=ignore_errors, **k)
    try:
        for c in sorted(p.iterdir(), key=lambda c: c.is_dir()):
            if c.is_dir():
                for cc in sorted(c.iterdir()):
                    _rm(cc, ignore_errors=True)
                    time.sleep(0.01)
                _rm(c, ignore_errors=True)
            else:
                c.unlink()
        p.rmdir()
    except OSError:
        if not ignore_errors:
            raise


SLOW = types.SimpleNamespace(**{k: getattr(shutil, k) for k in dir(shutil) if not k.startswith("__")})
SLOW.rmtree = slow_rmtree
out = []
for i in range(3):
    ch, cdir = toy_chain(f"r{i}", n_cases=50)
    before, end = cases(ch), threading.Event()
    ch.run_worker = lambda cid, stage, prompt, timeout, stop=None, **k: end.wait(30)
    live = FakeLive(after=1.0)
    # D30: the lib racer was still set when the workers ended -> the early generalize's _racer_passed was true too
    ch._lib_racer = type("R", (), {"passed": False, "link": lambda s, e: None, "finish": lambda s: None})()
    with patched({**env(ch, cdir, complete=lambda cid: live.passed), (orch, "shutil"): SLOW}):
        a = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {"early": True}))
        b = threading.Thread(target=ch.generalize, args=(CID, [("a", None)], {}, {}), kwargs={"live": live})
        a.start()
        time.sleep(0.1)
        b.start()
        while not live.passed:
            time.sleep(0.05)
        end.set()                     # both workers end at the live pass (D30 09:21:21)
        a.join(30)
        b.join(30)
    out.append((ch.sdir / "solve.py").exists() and cases(ch) == before and not (ch.root / ".generalize-unjudged").exists())
check("R the D30 race (slow snapshot rmtree, both workers end at the pass): solver intact every time", all(out), out)

# ------------------------------------------------------------------ K switches + keying + speed_harden
ch, cdir = toy_chain("k")
calls = []
with patched({**QUIET, (orch, "GEN_SOLVER_LOCK"): False,   # the body returns at once ("mode already CORRECT")
              (orch.Chain, "_racer_passed"): lambda self, cid, live: calls.append(cid) or True}):
    st = orch._gen_state(ch.sdir)
    st["lock"].acquire()
    try:
        t = threading.Thread(target=ch.generalize, args=(CID,))
        t.start()
        t.join(5)
    finally:
        st["lock"].release()
check("K HCTF_GEN_SOLVER_LOCK=0 -> the old unlocked generalize (does not wait on a held lock)", len(calls) == 1, calls)
link = TMP / "solver-link"
os.symlink(ch.sdir, link)
check("K one lock per solver dir by real path (symlinked challenges/ tree, any Chain object)",
      orch._gen_state(link) is orch._gen_state(ch.sdir) and orch._gen_state(link)["lock"] is orch._gen_state(ch.sdir)["lock"])
src = inspect.getsource(orch.speed_harden)
check("K generalize keeps its own source (decorator): source-inspecting suites still see the body",
      "_live_accept_join" in inspect.getsource(orch.Chain.generalize) and orch.Chain.generalize.__wrapped__)
check("K speed_harden holds the solver lock over generalize + re-time (its kept snapshot is read after generalize)",
      '_gen_state(sdir)["lock"]' in src and src.index('_gen_state(sdir)["lock"]') < src.index("_speed_keep_or_restore"))
check("K the lock state is cleared after each generalize (no stale green / passed)",
      all(s["green"] is None and s["passed"] is None and not s["lock"]._is_owned() for s in orch._gen_states.values()))

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAILED'}")
sys.exit(1 if failures else 0)
