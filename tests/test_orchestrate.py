#!/usr/bin/env python3
"""Offline self-test for the chain orchestrator's robustness/speed paths (no GM calls, no workers):

  - set_state is atomic + thread-safe (the speculative thread writes chain.json beside the chain thread)
  - a crashed chain is retried once, then marked crashed
  - merged reuse: one submit when right, bisect + alternates when a field is wrong, partial -> worker gets the rest
  - the solver snapshot keeps the solver's directory depth and reproduces the Single Solve answers (real challenge)
  - stop-when-ready: CORRECT + verified snapshot sets `ready`, and run_local ends the worker on it

Run:  source bin/env.sh && python3 tests/test_orchestrate.py      (exit 0 = all pass)
"""
import json
import sys
import tempfile
import threading
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hctf import cli, orchestrate as orch, paths  # noqa: E402

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


def bare_chain(**kw):
    """A Chain without __init__ side effects (no meta.json written into the real tree)."""
    c = object.__new__(orch.Chain)
    c.base, c.pools, c.gov, c.only_modes = "test-base", None, mock.Mock(allow_timed=lambda: True), None
    c.lane, c.name = "warmups", "test"
    c.entries = {"single_solve": {"id": "s"}, "time_trial": {"id": "s/time_trial"}, "mastery": {"id": "s/mastery"}}
    c.__dict__.update(kw)
    return c


def test_set_state(tmp):
    with mock.patch.object(paths, "challenge_root", lambda base: tmp):
        errs = []

        def hammer(i):
            try:
                for n in range(150):
                    orch.set_state("x", **{f"k{i}": n})
            except Exception as e:  # noqa: BLE001
                errs.append(e)
        ts = [threading.Thread(target=hammer, args=(i,)) for i in range(8)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        st = json.loads((tmp / "chain.json").read_text())
    check("set_state: 8 threads x 150 writes, no errors", not errs)
    check("set_state: every thread's last write survived", all(st.get(f"k{i}") == 149 for i in range(8)))
    check("set_state: no temp files left behind", not list(tmp.glob(".chain.json.*")))


def test_crash_retry():
    states = []
    with mock.patch.object(orch, "set_state", lambda base, **kw: states.append(kw.get("stage"))), \
            mock.patch.object(orch.time, "sleep", lambda s: None), mock.patch.object(orch, "say", lambda m: None):
        c = bare_chain()
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("cp: cannot create regular file")
        c._run = flaky
        c.run()
        check("crash retry: transient crash -> chain re-run once", len(calls) == 2 and "crashed" not in states)

        c2, calls2 = bare_chain(), []
        c2._run = lambda: (calls2.append(1), (_ for _ in ()).throw(RuntimeError("persistent")))[1]
        states.clear()
        c2.run()
        check("crash retry: persistent crash -> crashed after 2 tries", len(calls2) == 2 and states[-1] == "crashed")


class FakeGM:
    """Single Solve judge: a batch with ANY wrong value is 'incorrect' (nothing pinned); all-right -> accepted/correct."""
    def __init__(self, truth):
        self.truth, self.conf, self.calls = dict(truth), {}, []

    def submit(self, cid, group, force=False, probe=False, **kw):
        self.calls.append((dict(group), probe))
        if any(self.truth.get(a) != v for a, v in group.items()):
            return "incorrect", {}, []
        self.conf.update(group)
        return ("correct" if len(self.conf) == len(self.truth) else "accepted"), {}, []


def run_reuse(truth, plan, solver_out=None):
    gm = FakeGM(truth)
    sdir = Path(tempfile.mkdtemp()) / "solver"
    seed = Path(tempfile.mkdtemp())
    (seed / "solve.py").write_text("# seed\n")
    plan = {"source": {}, "runs": {seed: (1, None, 0.1)}, "best": seed, "alts": {}, **plan}
    with mock.patch.object(cli, "load", lambda cid, n: {"answer_ids": list(truth)}), \
            mock.patch.object(orch.timed, "latest_artifacts", lambda cid: Path("/nonexistent")), \
            mock.patch.object(orch.solvers, "reuse_plan", lambda *a, **k: plan), \
            mock.patch.object(orch.solvers, "run_solver", lambda *a, **k: (dict(solver_out or truth), None, 0.1)), \
            mock.patch.object(cli, "submit", gm.submit), \
            mock.patch.object(cli, "confirmed_answers", lambda cid, att=None: dict(gm.conf)), \
            mock.patch.object(cli, "is_complete", lambda cid: len(gm.conf) == len(truth)), \
            mock.patch.object(orch, "set_state", lambda *a, **k: None), \
            mock.patch.object(orch, "ensure_case_and_test", lambda *a, **k: (True, [])), \
            mock.patch.object(orch, "say", lambda m: None):
        c = bare_chain(sdir=sdir)
        ok = orch.Chain.try_existing_solvers(c, "s")
    return ok, gm, c, sdir


def test_reuse_submit():
    truth = {f"f{i}": str(i) for i in range(8)}
    ok, gm, c, sdir = run_reuse(truth, {"high": dict(truth), "spec": {}})
    check("reuse: all fields right -> ONE submit, solved, seed copied", ok and len(gm.calls) == 1 and (sdir / "solve.py").exists())

    high = dict(truth); high["f3"] = "WRONG"
    ok, gm, c, _ = run_reuse(truth, {"high": high, "spec": {}, "alts": {"f3": ["WRONG", "3"]}})
    check("reuse: one wrong field -> bisected, then the alternate value finishes it", ok and gm.conf == truth
          and all(p for _, p in gm.calls))

    part = {k: v for k, v in truth.items() if k not in ("f6", "f7")}
    ok, gm, c, _ = run_reuse(truth, {"high": part, "spec": {"f6": "bad"}})
    check("reuse: partial -> accepted subset pinned, worker told the 2 remaining ids",
          not ok and len(gm.conf) == 6 and "f6, f7" in c._reuse_note and "ALREADY ACCEPTED" in c._reuse_note)
    check("reuse: speculative value NOT submitted when it cannot finish the challenge",
          not any("f6" in g for g, _ in gm.calls))

    ok, gm, c, _ = run_reuse(truth, {"high": part, "spec": {"f6": "6", "f7": "7"}})
    check("reuse: speculative values submitted when they complete it", ok and gm.conf == truth)


def test_probe_enums():
    truth = {"x-role": "stager", "x-url": "u"}
    gm = FakeGM(truth)
    gm.conf["x-url"] = "u"
    contract = {"answer_ids": ["x-role", "x-url"], "questions": [
        {"id": "x-role", "question": "Classify a.sh as benign_utility, stager, dropper, or launcher.",
         "answer_format": {"kind": "enum", "accepted_values": ["benign_utility", "dropper", "launcher", "relay", "stager"]}},
        {"id": "x-url", "question": "Recover the URL.", "answer_format": {"kind": "url"}}]}
    with mock.patch.object(cli, "submit", gm.submit), \
            mock.patch.object(cli, "confirmed_answers", lambda cid, att=None: dict(gm.conf)), \
            mock.patch.object(orch, "say", lambda m: None):
        orch.Chain._probe_enums(bare_chain(), "s", contract)
    tried = [list(g.values())[0] for g, _ in gm.calls]
    check("enum probe: question-named options in question order until accepted",
          gm.conf.get("x-role") == "stager" and tried == ["benign_utility", "stager"] and all(p for _, p in gm.calls))


def test_snapshot():
    cid = "script-analysis-day-05-python-carrier-lab"
    sdir, root = paths.solver_dir(cid), paths.challenge_root(cid)
    if not (sdir / "solve.py").exists() or not cli.confirmed_answers(cid):
        check("snapshot: (skipped: Day 5 script-analysis not solved in this copy)", True)
        return
    c = bare_chain(sdir=sdir, root=root, base=paths.base_id(cid))
    with mock.patch.object(orch, "say", lambda m: None):
        snap = c._spec_snapshot(cid)
    check("snapshot: verified against the GM-confirmed Single Solve answers", snap is not None)
    if snap:
        rel_live = sdir.relative_to(ROOT).parts
        rel_snap = snap.relative_to(ROOT).parts
        check("snapshot: same directory depth as the live solver (parents[N] root lookup)", len(rel_live) == len(rel_snap))
        check("snapshot: cases/ excluded, meta.json beside it",
              not (snap / "cases").exists() and (snap.parent / "meta.json").exists())
    with mock.patch.object(orch, "SPEC_STABLE", 10 ** 9):
        check("snapshot: refused while the worker is still editing (files too fresh)", c._spec_snapshot(cid) is None)


def test_watch_ready(tmp):
    ready, done = threading.Event(), threading.Event()
    c = bare_chain(sdir=tmp, root=tmp)
    with mock.patch.object(orch, "SPEC_POLL", 0.01), mock.patch.object(orch, "say", lambda m: None), \
            mock.patch.object(cli, "is_complete", lambda cid: True):
        c._spec_snapshot = lambda cid: tmp
        orch.Chain._watch_ready(c, "s", ready, done)
    check("watch: CORRECT + verified snapshot -> ready set, snapshot kept", ready.is_set() and c._ready_snap == tmp)

    ready, done = threading.Event(), threading.Event()
    done.set()
    c = bare_chain(sdir=tmp, root=tmp)
    with mock.patch.object(orch, "SPEC_POLL", 0.01):
        c._spec_snapshot = lambda cid: (_ for _ in ()).throw(AssertionError("must not snapshot"))
        orch.Chain._watch_ready(c, "s", ready, done)
    check("watch: worker already exited -> nothing", not ready.is_set())

    # run_local honours `stop`: a long-running worker process is ended promptly with STOPPED_RC.
    import time as _t
    stop = threading.Event()
    with mock.patch.object(orch.workers, "worker_model", lambda lane: "x"), \
            mock.patch.object(orch.workers.subprocess, "Popen", lambda cmd, _P=__import__("subprocess").Popen, **kw: _P(["sleep", "30"], **kw)):
        threading.Timer(0.5, stop.set).start()
        t0 = _t.time()
        rc, _log = orch.workers.run_local(tmp, "single", "p", {}, 60, stop=stop)
    check("run_local: stop event ends the worker within ~3s with STOPPED_RC",
          rc == orch.workers.STOPPED_RC and _t.time() - t0 < 4)


def test_watch_green(tmp):
    import time as _t
    c = bare_chain(sdir=tmp, root=tmp)
    # start; edit #1 (+ re-read after its test) -> target still failing; edit #2 (+ re-read) -> green
    seq = iter([{"solve.py": 1.0}, {"solve.py": 2.0}, {"solve.py": 2.0}, {"solve.py": 3.0}, {"solve.py": 3.0}])
    c._solver_mtimes = lambda: next(seq, {"solve.py": 3.0})
    runs = [[{"case": "v1", "ok": False, "seconds": 0.1}, {"case": "old", "ok": True, "seconds": 0.1}],
            [{"case": "v1", "ok": True, "seconds": 0.1}, {"case": "old", "ok": True, "seconds": 0.1}]]
    green, done = threading.Event(), threading.Event()
    with mock.patch.object(orch.solvers, "test_solver", lambda *a, **k: runs.pop(0) if runs else runs_last[0]), \
            mock.patch.object(orch, "say", lambda m: None), mock.patch.object(orch.time, "time", lambda: 10 ** 6):
        runs_last = [[{"case": "v1", "ok": True, "seconds": 0.1}, {"case": "old", "ok": True, "seconds": 0.1}]]
        t = threading.Thread(target=orch.Chain._watch_green, args=(c, {"v1"}, {"old"}, False, green, done))
        t.start(); green.wait(15); done.set(); t.join(5)
    check("generalize watch: waits through a failing edit, green once the target passes w/o regression", green.is_set())
    # unverified failed variant: green once every field is answered
    c2 = bare_chain(sdir=tmp, root=tmp)
    seq2 = iter([{"solve.py": 1.0}, {"solve.py": 2.0}, {"solve.py": 2.0}])
    c2._solver_mtimes = lambda: next(seq2, {"solve.py": 2.0})
    full = [{"case": "var", "ok": False, "unverified": True, "answered": 28, "total": 28, "seconds": 0.1},
            {"case": "old", "ok": True, "seconds": 0.1}]
    green2, done2 = threading.Event(), threading.Event()
    with mock.patch.object(orch.solvers, "test_solver", lambda *a, **k: full), \
            mock.patch.object(orch, "say", lambda m: None), mock.patch.object(orch.time, "time", lambda: 10 ** 6):
        t = threading.Thread(target=orch.Chain._watch_green, args=(c2, set(), {"old"}, False, green2, done2, {"var"}))
        t.start(); green2.wait(10); done2.set(); t.join(5)
    check("generalize watch: unverified variant -> green once every field is answered", green2.is_set())


def main():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        print("set_state");   test_set_state(tmp)
        print("crash retry"); test_crash_retry()
        print("reuse");       test_reuse_submit()
        print("enums");       test_probe_enums()
        print("snapshot");    test_snapshot()
        print("watch");       test_watch_ready(tmp)
        print("green");       test_watch_green(tmp)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
