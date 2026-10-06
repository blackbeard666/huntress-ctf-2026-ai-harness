#!/usr/bin/env python3
"""Offline self-test for the chain orchestrator's robustness/speed paths (no GM calls, no workers):

  - set_state is atomic + thread-safe (the speculative thread writes chain.json beside the chain thread)
  - a crashed chain is retried once, then marked crashed
  - solver reuse submits every answer in ONE request; per-set (forced) only to localize a failure
  - early handoff: the solver snapshot keeps the solver's directory depth and reproduces the Single Solve answers
    (uses a real solved challenge on disk); the speculative thread runs TT -> Mastery once and stops on failure

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


def test_reuse_submit():
    answers = {"set1.a": "x", "set1.b": "y", "set2.a": "z"}
    src = Path(tempfile.mkdtemp())
    (src / "solve.py").write_text("# library solver stub\n")
    for verdict, want_calls in (("correct", 1), ("incorrect", 3)):
        sent = []

        def fake_submit(cid, group, force=False, **kw):
            sent.append((dict(group), force))
            return (verdict if len(sent) == 1 else "accepted"), {}, []
        with mock.patch.object(cli, "load", lambda cid, n: {"answer_ids": list(answers)}), \
                mock.patch.object(orch.timed, "latest_artifacts", lambda cid: Path("/nonexistent")), \
                mock.patch.object(orch.solvers, "dispatch", lambda c: ({src: ["q"]}, None)), \
                mock.patch.object(orch.solvers, "solve_contract", lambda *a, **k: (dict(answers), [])), \
                mock.patch.object(cli, "submit", fake_submit), \
                mock.patch.object(cli, "is_complete", lambda cid: verdict == "correct" and len(sent) >= 1), \
                mock.patch.object(orch, "set_state", lambda *a, **k: None), \
                mock.patch.object(orch, "ensure_case_and_test", lambda *a: (True, [])), \
                mock.patch.object(orch, "say", lambda m: None):
            c = bare_chain(sdir=Path(tempfile.mkdtemp()))
            orch.Chain.try_existing_solvers(c, "s")
        first_all = sent and sent[0][0] == answers and not sent[0][1]
        if verdict == "correct":
            check("reuse: correct -> exactly ONE submit carrying every answer", first_all and len(sent) == want_calls)
        else:
            check("reuse: wrong -> one full submit, then forced per-set localization",
                  first_all and len(sent) == want_calls and all(f for _, f in sent[1:]))


def test_snapshot():
    cid = "script-analysis-day-05-python-carrier-lab"
    sdir, root = paths.solver_dir(cid), paths.challenge_root(cid)
    if not (sdir / "solve.py").exists() or not cli.confirmed_answers(cid):
        check("snapshot: (skipped: Day 5 script-analysis not solved in this copy)", True)
        return
    c = bare_chain(sdir=sdir, root=root, base=paths.base_id(cid))
    with mock.patch.object(orch, "say", lambda m: None):
        snap = c._snapshot_solver(cid)
    check("snapshot: verified against the GM-confirmed Single Solve answers", snap is not None)
    if snap:
        rel_live = sdir.relative_to(ROOT).parts
        rel_snap = snap.relative_to(ROOT).parts
        check("snapshot: same directory depth as the live solver (parents[N] root lookup)", len(rel_live) == len(rel_snap))
        check("snapshot: cases/ excluded, meta.json beside it",
              not (snap / "cases").exists() and (snap.parent / "meta.json").exists())
    with mock.patch.object(orch, "SPEC_STABLE", 10 ** 9):
        check("snapshot: refused while the worker is still editing (files too fresh)", c._snapshot_solver(cid) is None)


def test_speculate(tmp):
    for outcomes, want in ((["correct", "correct"], ["s/time_trial", "s/mastery"]), (["blocked"], ["s/time_trial"])):
        ran = []
        stop = threading.Event()
        c = bare_chain(sdir=tmp, root=tmp)
        it = iter(outcomes)
        with mock.patch.object(orch, "SPEC_POLL", 0.01), mock.patch.object(orch, "say", lambda m: None), \
                mock.patch.object(cli, "is_complete", lambda cid: cid == "s"), \
                mock.patch.object(cli, "gm_solved", lambda cid: False), \
                mock.patch.object(orch.workers, "run_timed_auto", lambda snap, cid, log=None: ran.append(cid) or {}), \
                mock.patch.object(orch.timed, "process_result", lambda cid, sd, res, log=None: next(it)), \
                mock.patch.object(orch, "record_timed_case", lambda *a: None), \
                mock.patch.object(orch, "set_state", lambda *a, **k: None):
            c._snapshot_solver = lambda cid: tmp
            orch.Chain._speculate(c, "s", stop)
        check(f"speculate: outcomes {outcomes} -> attempts {want}", ran == want)
    stop = threading.Event()
    stop.set()
    with mock.patch.object(orch, "SPEC_POLL", 0.01):
        c = bare_chain(sdir=tmp, root=tmp)
        c._snapshot_solver = lambda cid: (_ for _ in ()).throw(AssertionError("must not snapshot"))
        orch.Chain._speculate(c, "s", stop)
    check("speculate: worker already exited -> no attempt", True)


def main():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        print("set_state");   test_set_state(tmp)
        print("crash retry"); test_crash_retry()
        print("reuse");       test_reuse_submit()
        print("snapshot");    test_snapshot()
        print("speculate");   test_speculate(tmp)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
