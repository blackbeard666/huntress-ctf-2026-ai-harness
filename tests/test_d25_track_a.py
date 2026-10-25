#!/usr/bin/env python3
"""D25 post-mortem Track A (first-try correctness), offline: fakes and fixtures only, no GM, no workers.

A2 small-pool rehearsal: lib.solverrt.max_procs honours HCTF_SOLVER_MAX_PROCS; test_solver replays a multi-set case
   on a 2-process pool even in the background class (procgov keeps a POOL_REHEARSAL run's pool), a 1-set case as
   before; a fake solver with a cross-set leak fails its case on the pool and passes single-process.

Run:  source bin/env.sh && python3 tests/test_d25_track_a.py      (exit 0 = all pass)
"""
import json
import os
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import procgov, solvers  # noqa: E402
from lib import solverrt  # noqa: E402

failures = []
TMP = Path(tempfile.mkdtemp(prefix="d25a-", dir=os.environ.get("TMPDIR")))


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


def env_set(**kw):
    old = {k: os.environ.get(k) for k in kw}
    for k, v in kw.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    return old


# ------------------------------------------------------------------------------------------------ A2 max_procs
old = env_set(HCTF_SOLVER_MAX_PROCS=None)
cpus = os.cpu_count() or 2
check("A2 max_procs: no cap -> min(n, cpus)", solverrt.max_procs(50) == min(50, cpus) and solverrt.max_procs(1) == 1)
check("A2 max_procs: io_bound -> n", solverrt.max_procs(50, io_bound=True) == 50)
env_set(HCTF_SOLVER_MAX_PROCS="2")
check("A2 max_procs: HCTF_SOLVER_MAX_PROCS=2 caps cpu and io pools",
      solverrt.max_procs(50) == 2 and solverrt.max_procs(50, io_bound=True) == 2 and solverrt.max_procs(1) == 1)
env_set(HCTF_SOLVER_MAX_PROCS="junk")
check("A2 max_procs: a junk cap is ignored", solverrt.max_procs(3) == min(3, cpus))
env_set(**old)

one_set = {"answer_ids": ["d01_a", "d01_b"], "questions": [{"id": "d01_a"}, {"id": "d01_b"}]}
two_sets = {"answer_ids": ["set1.d01_a", "set2.d01_a", "set3.d01_a"], "questions": [{"id": "d01_a"}]}
check("A2 small_pool_env: 1-set contract -> {}", solvers.small_pool_env(one_set) == {})
spe = solvers.small_pool_env(two_sets)
check("A2 small_pool_env: multi-set -> parallel on, 2 procs, rehearsal marker",
      spe == {"HCTF_SOLVER_PARALLEL": "1", "HCTF_SOLVER_MAX_PROCS": "2", "HCTF_SOLVER_POOL_REHEARSAL": "1"}, spe)
check("A2 small_pool_env: procs=0 disables", solvers.small_pool_env(two_sets, procs=0) == {})

# procgov: a background run is single-process, unless it is a pool rehearsal
probe = [sys.executable, "-c", "import os, json; print(json.dumps({k: os.environ.get(k) for k in "
         "('HCTF_SOLVER_PARALLEL', 'HCTF_SOLVER_MAX_PROCS')}))"]
r = procgov.run(probe, background=True, env=dict(os.environ), timeout=30)
check("A2 procgov: background run -> HCTF_SOLVER_PARALLEL=0", json.loads(r.stdout)["HCTF_SOLVER_PARALLEL"] == "0", r.stdout)
r = procgov.run(probe, background=True, env=dict(os.environ, **spe), timeout=30)
got = json.loads(r.stdout)
check("A2 procgov: background POOL_REHEARSAL run keeps its 2-proc pool",
      got == {"HCTF_SOLVER_PARALLEL": "1", "HCTF_SOLVER_MAX_PROCS": "2"}, got)

# a solver with a cross-set leak (module state carried from one set into the next in the same pool process):
# test_solver must FAIL its multi-set case (2 procs, 4 sets), even as a background run.
LEAKY = textwrap.dedent('''
    import argparse, json, multiprocessing as mp, os, sys
    sys.path.insert(0, os.environ["HCTF_TEST_ROOT"])
    from concurrent.futures import ProcessPoolExecutor
    from lib.common import group_by_set
    from lib.solverrt import max_procs
    _CACHE = {}   # keyed on the k-th object of a call: like id(), unique within one call, reused by the next one
    def solve(job):
        art, pairs = job
        return {aid: _CACHE.setdefault(i, aid.split(".")[0]) for i, (aid, _) in enumerate(pairs)}
    ap = argparse.ArgumentParser(); ap.add_argument("--contract"); ap.add_argument("--artifacts")
    a = ap.parse_args()
    c = json.load(open(a.contract))
    pairs = [(x, {}) for x in c["answer_ids"]]
    groups, out = group_by_set(pairs), {}
    if len(groups) >= 2 and os.environ.get("HCTF_SOLVER_PARALLEL", "1") != "0":   # the binary solvers' skeleton
        with ProcessPoolExecutor(max_workers=max_procs(len(groups)), mp_context=mp.get_context("fork")) as ex:
            for part in ex.map(solve, [(a.artifacts, g) for g in groups.values()]):
                out.update(part)
    else:
        out = solve((a.artifacts, pairs))
    print(json.dumps(out))
''')
sd = TMP / "leaky" / "solver"
case = sd / "cases" / "auto-mastery-x"
(case / "artifacts").mkdir(parents=True)
(sd / "solve.py").write_text(LEAKY)
ids = [f"set{i}.d01_a" for i in range(1, 5)]
(case / "contract.json").write_text(json.dumps({"answer_ids": ids, "questions": [{"id": "d01_a"}]}))
(case / "expected.json").write_text(json.dumps({a: a.split(".")[0] for a in ids}))
old = env_set(HCTF_TEST_ROOT=str(ROOT))
with procgov.background():
    res = solvers.test_solver(sd, timeout=60)
check("A2 test_solver: a cross-set leak fails its 4-set case on the 2-proc pool (background run)",
      len(res) == 1 and not res[0]["ok"] and res[0]["diff"], res)
old2 = env_set(HCTF_CASE_MAX_PROCS="0")
solvers.CASE_MAX_PROCS = 0
with procgov.background():
    res0 = solvers.test_solver(sd, timeout=60)
solvers.CASE_MAX_PROCS = 2
env_set(**old2)
check("A2 test_solver: HCTF_CASE_MAX_PROCS=0 -> the old single-process background replay (leak hidden)",
      len(res0) == 1 and res0[0]["ok"], res0)
env_set(**old)

shutil.rmtree(TMP, ignore_errors=True)
if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D25 Track A checks passed")
