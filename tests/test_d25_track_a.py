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

# ------------------------------------------------------------------------------------------------ A2 pool rehearsal
from concurrent.futures import Future  # noqa: E402
from hctf import orchestrate, today_probe as tp, workers  # noqa: E402

# per-set answer = <artifact text>:<field>; LEAK caches it on the k-th pair of a call (an id()-like key)
POOLED = textwrap.dedent('''
    import argparse, json, multiprocessing as mp, os, sys
    sys.path.insert(0, os.environ["HCTF_TEST_ROOT"])
    from concurrent.futures import ProcessPoolExecutor
    from lib.common import group_by_set
    from lib.solverrt import max_procs
    KIND = "%s"
    _CACHE = {}
    def solve(job):
        art, pairs = job
        out = {}
        for i, (aid, q) in enumerate(pairs):
            txt = open(os.path.join(art, q["artifact"])).read().strip()
            v = _CACHE.setdefault(i, txt) if KIND == "leak" else txt
            out[aid] = ("x" if KIND == "shape" else v) + ":" + aid.rsplit(".", 1)[-1]
        return out
    ap = argparse.ArgumentParser(); ap.add_argument("--contract"); ap.add_argument("--artifacts")
    a = ap.parse_args()
    c = json.load(open(a.contract))
    qs = {q["id"]: q for q in c["questions"]}
    pairs = [(x, qs[x]) for x in c["answer_ids"]]
    groups, out = group_by_set(pairs), {}
    if len(groups) >= 2 and os.environ.get("HCTF_SOLVER_PARALLEL", "1") != "0":
        with ProcessPoolExecutor(max_workers=max_procs(len(groups)), mp_context=mp.get_context("fork")) as ex:
            for part in ex.map(solve, [(a.artifacts, g) for g in groups.values()]):
                out.update(part)
    else:
        out = solve((a.artifacts, pairs))
    print(json.dumps(out))
''')


def half(case, text, n=3):
    (case / "artifacts").mkdir(parents=True)
    (case / "artifacts" / "evidence.zip").write_text(text)
    (case / "artifacts" / ".prefetch.json").write_text("{}")    # pre-start bookkeeping: never a set's bytes
    ids = [f"d01_f{i}" for i in range(n)]
    (case / "contract.json").write_text(json.dumps({"attempt_id": case.name, "answer_ids": ids,
                                                    "questions": [{"id": i, "artifact": "evidence.zip"} for i in ids]}))
    (case / "expected.json").write_text(json.dumps({i: f"{text}:{i}" for i in ids}))
    return case


def chal(kind):
    sd = TMP / "day25" / f"binary-{kind}" / "solver"
    sd.mkdir(parents=True)
    (sd / "solve.py").write_text(POOLED % kind)
    half(sd / "cases" / "single_solve", "SINGLE")
    return sd


old = env_set(HCTF_TEST_ROOT=str(ROOT))
sd = chal("clean")
tt = half(TMP / "tt-case", "TRIAL")
case = tp.pool_case(sd, tt, sample="delivery 3: evidence.zip", out_dir=TMP / "pool")
c = json.loads((case / "contract.json").read_text())
truth = json.loads((case / "truth.json").read_text())
arts = sorted(p.name for p in (case / "artifacts").iterdir())
check("A2 pool_case: 8 sets S,S,T,T,S,S,T,T of the two verified halves", truth["layout"] == "SSTTSSTT" and
      len(c["answer_ids"]) == 24 and c["answer_ids"][0] == "set1.d01_f0", (truth, c["answer_ids"][:4]))
check("A2 pool_case: deliveries renamed in the Mastery's convention, no dotfiles",
      arts == [f"delivery {n}: evidence.zip" for n in range(1, 9)], arts)
exp = json.loads((case / "expected.json").read_text())
check("A2 pool_case: expected = each half's GM-verified answers per set",
      exp["set1.d01_f0"] == "SINGLE:d01_f0" and exp["set3.d01_f2"] == "TRIAL:d01_f2" and len(exp) == 24, exp)
same = half(TMP / "same-case", "SINGLE")
check("A2 pool_case: identical bytes in both halves -> None (they hide a leak)",
      tp.pool_case(sd, same, out_dir=TMP / "pool2") is None)
part = half(TMP / "part-case", "PART", n=4)
(part / "expected.json").write_text(json.dumps({"d01_f0": "PART:d01_f0"}))
check("A2 pool_case: a half with < half its ids verified -> None", tp.pool_case(sd, part, out_dir=TMP / "pool3") is None)

for kind, want in (("clean", "clean"), ("leak", "leak"), ("shape", "shape")):
    sdk = sd if kind == "clean" else chal(kind)
    with procgov.background():
        r = tp.pool_rehearsal(sdk, tt, out_dir=TMP / f"pool-{kind}", tag="tt")
    check(f"A2 pool_rehearsal: {kind} solver -> {want}", r["status"] == want,
          {k: r.get(k) for k in ("status", "error")} | {"pooled": (r.get("pooled") or {}).get("wrong")})
    if kind == "leak":
        leak_res = r
        check("A2 pool_summary names the case, the pool and a wrong field",
              "rehearsal-pool-d25-tt" in tp.pool_summary(r) and "2-process" in tp.pool_summary(r)
              and "expected 'TRIAL:" in tp.pool_summary(r), tp.pool_summary(r)[:300])

# orchestrator consumption: once, adopts the case; the Mastery attempt's early event generalizes beside it
ch = orchestrate.Chain.__new__(orchestrate.Chain)
ch.sdir, ch.base, ch.lane = TMP / "day25" / "binary-leak" / "solver", "day25/binary-leak", "binary-reverse-engineering"
fut = Future()
fut.set_result(leak_res)
ch._pool_fut = fut
got = ch._pool_rehearsal_result("day25/binary-leak/mastery")
check("A2 _pool_rehearsal_result: a finished leak -> diag + case adopted",
      "pool_rehearsal" in got and (ch.sdir / "cases" / "rehearsal-pool-d25-tt" / "expected.json").exists(), got)
check("A2 _pool_rehearsal_result: consumed once", ch._pool_rehearsal_result("day25/binary-leak/mastery") == {})
pending = Future()
ch2 = orchestrate.Chain.__new__(orchestrate.Chain)
ch2.sdir, ch2._pool_fut = ch.sdir, pending
check("A2 _pool_rehearsal_result: a still-running rehearsal is never waited for",
      ch2._pool_rehearsal_result("x/mastery") == {} and not getattr(ch2, "_pool_done", False))

att = TMP / "attempt"
att.mkdir()
(att / "contract.json").write_text(json.dumps({"attempt_id": "att-1", "answer_ids": ["set1.d01_f0"]}))
fut3 = Future()
fut3.set_result(leak_res)
ch3 = orchestrate.Chain.__new__(orchestrate.Chain)
ch3.sdir, ch3.base, ch3.lane, ch3._pool_fut, ch3._early = ch.sdir, ch.base, ch.lane, fut3, None
seen = {}
ch3.generalize = lambda cid, wrong=None, fixed=None, diag=None, live=None: seen.update(diag=diag)
saved = (workers.EARLY_GENERALIZE, orchestrate.capture_variant, orchestrate.cli.save)
workers.EARLY_GENERALIZE = False
orchestrate.capture_variant = lambda cid, sdir: TMP / "variant-mastery-att"
orchestrate.cli.save = lambda *a, **k: None
ch3._ahead_new = lambda mode: 0
try:
    ch3._early_event("day25/binary-leak/mastery", {"event": "solved", "local": str(att), "attempt_id": "att-1",
                                                   "result": "solved", "missing": []})
    if ch3._early:
        ch3._early["thread"].join(5)
finally:
    workers.EARLY_GENERALIZE, orchestrate.capture_variant, orchestrate.cli.save = saved
check("A2 _early_event: a leak landing during a COMPLETE Mastery attempt starts the early generalize with its diag",
      (seen.get("diag") or {}).get("early") and "pool_rehearsal" in (seen.get("diag") or {}), seen)
ch4 = orchestrate.Chain.__new__(orchestrate.Chain)
ch4.sdir, ch4.base, ch4.lane, ch4._pool_fut, ch4._early = ch.sdir, ch.base, ch.lane, None, None
ch4._ahead_new = lambda mode: 0
ch4._early_event("day25/binary-leak/mastery", {"event": "solved", "local": str(att), "attempt_id": "att-1",
                                               "result": "solved", "missing": []})
check("A2 _early_event: no leak + a complete solve -> no early generalize (unchanged)", ch4._early is None)
tt_c = json.loads((tt / "contract.json").read_text())
tt_exp = json.loads((tt / "expected.json").read_text())
m_multi = {"answer_ids": ["set1.a", "set2.a"], "questions": [{"id": "set1.a", "artifact": "delivery 1: evidence.zip"}]}
saved = (orchestrate.cli.load, orchestrate.timed.latest_artifacts, orchestrate.cli.confirmed_answers,
         orchestrate.cli.is_complete)
try:
    for mc, lane, want in ((m_multi, "binary-reverse-engineering", True), ({}, "binary-reverse-engineering", True),
                           ({"answer_ids": ["d01_a"]}, "binary-reverse-engineering", False), (m_multi, "web", False)):
        orchestrate.cli.load = lambda cid, name, _mc=mc: _mc if cid.endswith("/mastery") else tt_c
        orchestrate.timed.latest_artifacts = lambda cid: tt / "artifacts"
        orchestrate.cli.confirmed_answers = lambda cid, *a: tt_exp
        orchestrate.cli.is_complete = lambda cid: False
        ch5 = orchestrate.Chain.__new__(orchestrate.Chain)
        ch5.sdir, ch5.base, ch5.lane = sd, "day25/binary-clean", lane
        ch5.entries = {"time_trial": {"id": "day25/binary-clean/time_trial"}, "mastery": {"id": "day25/binary-clean/mastery"}}
        ch5._start_pool_rehearsal("day25/binary-clean/time_trial")
        f5 = getattr(ch5, "_pool_fut", None)
        r5 = f5.result(60) if f5 else None
        check(f"A2 _start_pool_rehearsal: lane {lane}, Mastery ids {len(mc.get('answer_ids') or [])} -> "
              f"{'runs (clean)' if want else 'skipped'}",
              (r5 is not None and r5["status"] == "clean" and r5["sequential"] is not None) if want else f5 is None, r5)
finally:
    (orchestrate.cli.load, orchestrate.timed.latest_artifacts, orchestrate.cli.confirmed_answers,
     orchestrate.cli.is_complete) = saved
src = (ROOT / "hctf" / "orchestrate.py").read_text()
check("A2 wiring: started at the TT's CORRECT + before Mastery; untimed pools do not hold a leak",
      "self._start_pool_rehearsal(cid)  # A2" in src and "self._start_pool_rehearsal((self.entries.get" in src
      and '"pool_rehearsal" not in late' in src)
env_set(**old)

shutil.rmtree(TMP, ignore_errors=True)
if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D25 Track A checks passed")
