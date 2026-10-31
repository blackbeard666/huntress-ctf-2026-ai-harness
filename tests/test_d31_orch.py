"""D31 orchestrator fixes (before the final drop), offline: fakes only -- no GM, no LLM, no Homebase.

 #1  binary single: the race's answers are never held behind local triage
     - solvers._known_ids is memoized per (solver dir, cases/ mtime) and warmed before the drop (the merge + gate read no
       case files under drop load: D29 in-network race had 398/406 at +23.8 s, first submit +63 s)
     - a race that loses the submit claim says so (D29: silent)
     - a race that banked part of the single starts answer-first on its RESIDUAL at once (no race wait, no dry-run wait),
       one answer-first per single (the launch prep's side workers share the lock)
 #2  speed_harden: a speed generalize is kept only if the re-timed slowest case (min of N, old vs new interleaved) got
     faster or a failing case now passes, else .generalize-snapshot/ is restored; single-only challenges are skipped
 #3  hof_race never stamps an unsolved (single-only) chain "done"; `hctf why` never says "all modes solved" over an
     unsolved mode

Run:  source bin/env.sh && python3 tests/test_d31_orch.py      (exit 0 = all pass)
"""
import contextlib
import inspect
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["HCTF_ANSWER_FIRST"] = "1"
from hctf import cli, orchestrate, solvers  # noqa: E402

failures = []


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


def wait_for(cond, secs=5.0):
    end = time.time() + secs
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.05)
    return cond()


TD = Path(tempfile.mkdtemp(prefix="d31orch-", dir=str(ROOT / ".run")))
said = []
QUIET = {(orchestrate, "say"): lambda *a, **k: said.append(a[0] if a else "")}


def mk_solver(path, cases):
    """A solver dir with cases/<name>/expected.json = {id: value}."""
    (path / "cases").mkdir(parents=True, exist_ok=True)
    (path / "solve.py").write_text("print('{}')\n")
    for name, exp in cases.items():
        (path / "cases" / name).mkdir(exist_ok=True)
        (path / "cases" / name / "expected.json").write_text(json.dumps(exp))
    return path


# ------------------------------------------------------------------ #1a known-ids memo
check("#1 the memo is installed (reuse_merge looks solvers._known_ids up at call time)",
      solvers._known_ids is orchestrate._known_ids_memo and orchestrate.RACE_KNOWN_MEMO)
sd = mk_solver(TD / "challenges" / "day28" / "binary-a" / "solver", {"auto-mastery-1": {"d01_x": "1", "d02_y": "2"}})
raw_calls = []


REAL_RAW = orchestrate._known_raw


def counting_raw(sdir):
    raw_calls.append(str(sdir))
    return REAL_RAW(sdir)


with patched({(orchestrate, "_known_raw"): counting_raw}):
    orchestrate._known_memo.clear()
    k1 = solvers._known_ids(sd)
    k2 = solvers._known_ids(sd)
    check("#1 first call reads the cases, the second is a memo hit (no file reads)",
          k1 == {"d01_x", "d02_y"} and k2 == k1 and raw_calls == [str(sd)], raw_calls)
    time.sleep(0.02)
    mk_solver(sd, {"auto-time_trial-2": {"d03_z": "3"}})   # a new case dir = a new cases/ mtime
    k3 = solvers._known_ids(sd)
    check("#1 a new case invalidates the memo (cases/ mtime)", "d03_z" in k3 and len(raw_calls) == 2, raw_calls)
    lane_sd = mk_solver(TD / "challenges" / "_lane" / "metadata-forensics" / "solver", {})
    raw_calls.clear()
    with patched({(solvers, "_day_key"): lambda p: solvers.LANE_DAY_KEY if "_lane" in str(p) else 28}):
        solvers._known_ids(lane_sd)
        solvers._known_ids(lane_sd)
    check("#1 a lane solver (cross-day known set) is never memoized", len(raw_calls) == 2, raw_calls)
    big = mk_solver(TD / "challenges" / "day27" / "script-b" / "solver",
                    {"auto-mastery-9": {f"f{i}": str(i) for i in range(20)}})
    raw_calls.clear()
    with patched({(orchestrate, "RACE_KNOWN_MEMO_MAX"): 10}):
        solvers._known_ids(big)
        solvers._known_ids(big)
    check("#1 a set over RACE_KNOWN_MEMO_MAX ids is not kept (script: ~50 MB)", len(raw_calls) == 2, raw_calls)
    nocases = TD / "challenges" / "day26" / "x" / "solver"
    nocases.mkdir(parents=True)
    check("#1 a solver without cases/ -> the raw read (no memo key)", solvers._known_ids(nocases) == set())

# reuse_merge (unchanged) consumes the memo: confident vs speculative is the same as the raw read
orchestrate._known_memo.clear()
contract = {"answer_ids": ["d01_x", "d02_y", "d09_new"]}
outs = {sd: ({"d01_x": "1", "d02_y": "2", "d09_new": "9"}, None, 1.0)}
plan1 = solvers.reuse_merge(contract, [sd], [], outs)
with patched({(orchestrate, "_known_raw"): lambda p: (_ for _ in ()).throw(AssertionError("file read on a hit"))}):
    plan2 = solvers.reuse_merge(contract, [sd], [], outs)
check("#1 reuse_merge on a warm memo: same high/spec, no case file read",
      plan1["high"] == plan2["high"] == {"d01_x": "1", "d02_y": "2"} and plan2["spec"] == {"d09_new": "9"},
      (plan1["high"], plan2["spec"]))

# ------------------------------------------------------------------ #1b pre-drop warm
orchestrate._known_memo.clear()
warm_log, slug_calls = [], []
from lib import slug  # noqa: E402
from hctf import webtarget  # noqa: E402
with patched({(orchestrate, "REUSE_RACE_LANES"): {"binary-reverse-engineering", "web", "welcome"},
              (solvers, "reuse_cands"): lambda lane, exclude=(), limit=None, rank=None, question_contract=None:
              ([sd], []) if lane == "binary-reverse-engineering" else (_ for _ in ()).throw(AssertionError(lane)),
              (webtarget, "is_live_lane"): lambda ln: ln == "web",
              (slug, "vocab"): lambda: slug_calls.append("vocab") or set(),
              (slug, "english"): lambda: slug_calls.append("english") or set()}):
    orchestrate.warm_race_known_async(log=warm_log.append)
    wait_for(lambda: warm_log)
check("#1 warm_race_known_async: the non-web race lanes' candidates memoized + the slug vocab loaded before the drop",
      str(sd) in orchestrate._known_memo and slug_calls == ["vocab", "english"]
      and warm_log and "warmed" in warm_log[0], (warm_log, slug_calls, list(orchestrate._known_memo)))
src_run = inspect.getsource(orchestrate.run)
check("#1 run() warms it before the release wait",
      src_run.index("warm_race_known_async(") < src_run.index("wait_for_release(day"))
src_hb = inspect.getsource(orchestrate.Chain._hb_race)
check("#1 _hb_race also warms its candidates beside the VM's download", "solvers._known_ids(c) for c in cands" in src_hb)

# ------------------------------------------------------------------ #1c the race: claim lost is logged; residual AF
CID = "binary-reverse-engineering-day-29-variant-diffing"
CDIR = TD / "chal" / "single_solve"
(CDIR / "artifacts" / "1").mkdir(parents=True)
(CDIR / "artifacts" / "latest").symlink_to(CDIR / "artifacts" / "1")
ids = [f"d{(i % 28) + 1:02d}_analysis_f{i}" for i in range(406)]
(CDIR / "start.json").write_text(json.dumps({"attempt_id": "att-29", "answer_ids": ids, "questions": [
    {"id": a, "question": f"q {a}", "artifact": "x.bin", "answer_format": {"kind": "string"}} for a in ids]}))
banked = ids[:398]


def race_chain(lane="binary-reverse-engineering"):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base, ch.name = lane, CID, "variant-diffing"
    ch.root = TD / "chal"
    ch.sdir = ch.root / "solver"
    ch.sdir.mkdir(parents=True, exist_ok=True)
    ch.notes = []
    ch._deliver_note = lambda cid, note, key: ch.notes.append(key)
    ch._race_note = lambda cid, ids_, merged, plan: "RACE NOTE"

    def bank(cid, ids_, high, spec, merged, plan):
        (CDIR / "confirmed.json").write_text(json.dumps({"att-29": {a: "1" for a in banked}}))
        return 2
    ch._race_bank = bank
    return ch


class FakeAF:
    made = []

    def __init__(self, chain, cid):
        self.chain, self.cid, self.kw = chain, cid, None
        FakeAF.made.append(self)

    def start(self, race_done=None, residual=None):
        self.kw = {"race_done": race_done, "residual": residual}
        return self


plan = {"high": {a: "1" for a in banked[:392]}, "spec": {a: "1" for a in banked[392:]}, "runs": {"s": (398, None, 1.0)},
        "best": None, "alts": {}, "outs": {}}
base_patch = {**QUIET, (cli, "cdir"): lambda cid: CDIR,
              (orchestrate.timed, "latest_artifacts"): lambda cid: CDIR / "artifacts" / "1",
              (orchestrate, "AnswerFirst"): FakeAF,
              (orchestrate, "answer_first_eligible"): lambda lane, n: (0 < n <= 80, f"{n} fields")}
with patched(base_patch):
    ch = race_chain()
    ch._race_claimed = lambda cid: False
    said.clear()
    ch._race_submit(CID, json.loads((CDIR / "start.json").read_text()), ids, plan, None, time.time() - 24, {},
                    where=" (in-network)")
    check("#1 a race that loses the submit claim logs it (D29's in-network race returned silently)",
          any("reuse race (in-network): stands down" in s and "holds this attempt's submit" in s for s in said), said)

    FakeAF.made.clear()
    ch = race_chain()
    t0 = time.time()
    ch._race_submit(CID, json.loads((CDIR / "start.json").read_text()), ids, plan, None, t0 - 24, {"rank": t0, "plan": t0},
                    where=" (in-network)")
    wait_for(lambda: getattr(ch, "_af", None) is not None)
    af = getattr(ch, "_af", None)
    res = (af.kw or {}).get("residual") if af else None
    check("#1 race banked 398/406 -> answer-first on the 8-field RESIDUAL at once (from the race, no launch prep)",
          af is not None and res and res[0] == ids[398:] and "banked 398/406" in res[1]
          and af.kw["race_done"] is None, (af and af.kw, said[-3:]))
    check("#1 ... and the race note still reaches the solver worker", ch.notes == ["race"], ch.notes)
    n_made = len(FakeAF.made)
    ch._race_residual_af(CID, ids, "")
    time.sleep(0.3)
    check("#1 one answer-first per single (an existing _af is never replaced)", len(FakeAF.made) == n_made, len(FakeAF.made))

    # nothing banked -> the launch prep decides (no early worker); web / kill switch / no bytes -> no-op
    (CDIR / "confirmed.json").unlink()
    ch = race_chain()
    ch._race_residual_af(CID, ids, "")
    time.sleep(0.3)
    check("#1 nothing banked -> no race-residual answer-first", getattr(ch, "_af", None) is None)
    (CDIR / "confirmed.json").write_text(json.dumps({"att-29": {a: "1" for a in banked}}))
    for name, extra in (("live-target web", {}), ("kill switch HCTF_RACE_RESIDUAL_AF=0", {(orchestrate, "RACE_RESIDUAL_AF"): False}),
                        ("no local bytes yet", {(orchestrate.timed, "latest_artifacts"): lambda cid: None})):
        with patched(extra):
            ch = race_chain(lane="web" if name.startswith("live") else "binary-reverse-engineering")
            with patched({(webtarget, "is_live_lane"): lambda ln: ln == "web"}):
                ch._race_residual_af(CID, ids, "")
            time.sleep(0.2)
        check(f"#1 {name} -> no race-residual answer-first", getattr(ch, "_af", None) is None)
    # a single that went CORRECT meanwhile -> no worker
    with patched({(cli, "is_complete"): lambda cid: True}):
        ch = race_chain()
        ch._race_residual_af(CID, ids, "")
        time.sleep(0.3)
    check("#1 single complete before the launch -> no race-residual answer-first", getattr(ch, "_af", None) is None)
src_single = inspect.getsource(orchestrate.Chain._single)
check("#1 the launch prep's answer-first start takes the same lock (no second worker beside the race's)",
      "with self._af_launch_lock():" in src_single and "AnswerFirst(self, cid)" in src_single)

# AnswerFirst.start(residual=...): no race wait, no dry-run wait, .live_fields.json = the residual
calls = []


def fake_run_worker(cid, stage, prompt, timeout, urgent=False, prefer_homebase=False, stop=None, warm=None,
                    warm_task=None, env_extra=None, force_local=False):
    calls.append({"stage": stage, "prompt": prompt, "t": time.time()})
    stop.wait(5)
    return 0


(CDIR / "triage.md").write_text("# triage\n\n## STATUS\n- x.bin\n")
never = Future()   # the dry run still running (D29: its result came at +53.8 s)
chain = SimpleNamespace(lane="binary-reverse-engineering", base=CID, sdir=TD / "chal" / "solver", root=TD / "chal",
                        run_worker=fake_run_worker, _dry_fut=never, _deliver_note=lambda *a, **k: None)
race_never = threading.Event()
with patched({**QUIET, (cli, "cdir"): lambda cid: CDIR,
              (orchestrate.timed, "latest_artifacts"): lambda cid: CDIR / "artifacts" / "1",
              (orchestrate, "answer_first_eligible"): lambda lane, n: (True, ""),
              (orchestrate, "ANSWER_FIRST_RACE_WAIT"): 10.0, (orchestrate, "AF_DRY_WAIT"): 8.0}):
    afr = orchestrate.AnswerFirst(chain, CID)
    t0 = time.time()
    afr.start(race_done=race_never, residual=(ids[398:], "the reuse race banked 398/406 GM-confirmed"))
    wait_for(lambda: calls, 5)
    lf = json.loads((CDIR / ".live_fields.json").read_text()) if (CDIR / ".live_fields.json").exists() else {}
    check("#1 AnswerFirst.start(residual=...) launches at once: no race wait (10 s), no dry-run wait (8 s)",
          calls and calls[0]["t"] - t0 < 3 and lf.get("fields") == ids[398:], (calls[:1] and calls[0]["t"] - t0, lf))
    check("#1 ... its prompt lists only the residual + says why",
          calls and all(f"`{a}`" in calls[0]["prompt"] for a in ids[398:]) and f"`{ids[0]}`" not in calls[0]["prompt"]
          and "banked 398/406" in calls[0]["prompt"], calls and calls[0]["prompt"][-600:])
    afr.stop_evt.set()
    afr.done.wait(10)
(CDIR / "confirmed.json").unlink()

# ------------------------------------------------------------------ #2 speed_harden keep-or-restore
class SpeedChain:
    """Stands in for chain_for(): the real snapshot semantics (copy before the worker; accept keeps it while
    _keep_gen_snap, else drops it) with a scripted 'worker' edit."""

    def __init__(self, root, edit):
        self.root, self.sdir, self.edit = root, root / "solver", edit
        self.keep_seen, self.restored = None, None

    def _snap_dir(self):
        return self.root / ".generalize-snapshot"

    def generalize(self, cid, wrong=None, fixed=None, diag=None, live=None):
        if not diag:   # speed_harden's correctness generalize (a failing case): leaves the solver as it was here
            return
        shutil.copytree(self.sdir, self._snap_dir())
        (self.sdir / "solve.py").write_text(self.edit)
        self.keep_seen = getattr(self, "_keep_gen_snap", False)
        if not self.keep_seen:
            shutil.rmtree(self._snap_dir())

    def _restore_snapshot(self, why):
        orchestrate.Chain._restore_snapshot(self, why)
        self.restored = why

    base = "binary-reverse-engineering-day-30-x"


def speed_case(tag, suite, retime, edit="NEW", gained=False):
    """suite: {"old"/"new": [(case, secs, ok)]} full-suite runs; retime: {"old"/"new": [secs per run]} for the slow case."""
    root = TD / "speed" / tag
    (root / "single_solve").mkdir(parents=True)
    (root / "single_solve" / "start.json").write_text("{}")
    (root / "mastery").mkdir()
    (root / "mastery" / "contract.json").write_text("{}")
    mk_solver(root / "solver", {"auto-mastery-1": {"a": "1"}, "auto-time_trial-2": {"b": "2"}})
    (root / "solver" / "solve.py").write_text("OLD")
    ch = SpeedChain(root, edit)
    it = {"old": iter(retime["old"]), "new": iter(retime["new"])}
    seen = []

    def fake_test(sdir, timeout=120, parallel=None, cases=None):
        sdir = Path(sdir)
        which = "new" if (sdir / "solve.py").read_text() == edit else "old"
        seen.append((which, cases, parallel))
        if cases is not None:   # a re-time of the slowest case(s)
            t = next(it[which])
            return [{"case": c, "ok": True, "seconds": t, "error": None, "unverified": False} for c in cases]
        return [{"case": c, "ok": ok, "seconds": s, "error": None, "unverified": False} for c, s, ok in suite[which]]
    logs = []
    with patched({**QUIET, (orchestrate.solvers, "test_solver"): fake_test,
                  (orchestrate.paths, "solver_dir"): lambda b: root / "solver",
                  (orchestrate, "chain_for"): lambda b, pools, gov: ch,
                  (orchestrate, "SINGLE_SPEED_BUDGET"): 2.5, (orchestrate, "SPEED_RETIME_RUNS"): 2,
                  (orchestrate, "_parallel_sets_need"): lambda sdir, res: None}):
        out = orchestrate.speed_harden(cid=SpeedChain.base, log=logs.append)
    return ch, out[SpeedChain.base], logs, root, seen


# D30 shape: 4.3 s before; the one "after" suite run (beside the post-run workers) says 6.5 s; re-timed: no gain
ch, out, logs, root, seen = speed_case(
    "slower", {"old": [("auto-mastery-1", 4.3, True), ("auto-time_trial-2", 1.0, True)],
               "new": [("auto-mastery-1", 6.5, True), ("auto-time_trial-2", 1.0, True)]},
    {"old": [4.4, 4.2], "new": [6.1, 5.9]})
check("#2 D30 shape (4.3 s -> 6.5 s, re-timed 4.2 vs 5.9): the pre-generalize solver is RESTORED from the snapshot",
      ch.restored and (root / "solver" / "solve.py").read_text() == "OLD" and not (root / ".generalize-snapshot").exists()
      and (root / ".generalize-rejected" / "solve.py").read_text() == "NEW" and out == (4.3, 4.2), (out, logs))
check("#2 ... the snapshot was kept through the accept (_keep_gen_snap) and the flag reset after",
      ch.keep_seen is True and getattr(ch, "_keep_gen_snap", None) is False)
check("#2 ... re-timed old vs new interleaved, min of 2 sequential runs each, slowest case only",
      [w for w, c, p in seen if c is not None] == ["new", "old", "new", "old"]
      and all(c == ["auto-mastery-1"] and p == 1 for w, c, p in seen if c is not None), seen)
check("#2 ... and logged", any("no speed gain -> pre-generalize solver restored" in s and "min of 2" in s for s in logs), logs)

# a noisy single "after" run (6.0 s beside the post-run load) but really faster: kept
ch, out, logs, root, _ = speed_case(
    "faster", {"old": [("auto-mastery-1", 5.1, True), ("auto-time_trial-2", 1.0, True)],
               "new": [("auto-mastery-1", 6.0, True), ("auto-time_trial-2", 1.0, True)]},
    {"old": [5.0, 5.2], "new": [3.1, 2.9]})
check("#2 really faster (re-timed 5.0 -> 2.9; the one suite run said 6.0): kept, snapshot dropped",
      not ch.restored and (root / "solver" / "solve.py").read_text() == "NEW"
      and not (root / ".generalize-snapshot").exists() and out == (5.1, 2.9) and any(": kept" in s for s in logs),
      (out, logs))

# within noise (< 5 %): restored
ch, out, logs, root, _ = speed_case(
    "noise", {"old": [("auto-mastery-1", 5.0, True)], "new": [("auto-mastery-1", 4.9, True)]},
    {"old": [5.0, 5.0], "new": [4.9, 4.9]})
check("#2 a 2 % 'gain' is noise -> restored", ch.restored and (root / "solver" / "solve.py").read_text() == "OLD", logs)

# slower but it made a failing case pass: correctness wins, kept
ch, out, logs, root, _ = speed_case(
    "gained", {"old": [("auto-mastery-1", 5.1, True), ("auto-mastery-4d45", 1.0, False)],
               "new": [("auto-mastery-1", 6.0, True), ("auto-mastery-4d45", 1.0, True)]},
    {"old": [5.0, 5.0], "new": [5.8, 5.9]})
check("#2 not faster but now also passes a failing case (D29 binary: auto-mastery-4d45c8fb) -> kept",
      not ch.restored and (root / "solver" / "solve.py").read_text() == "NEW"
      and not (root / ".generalize-snapshot").exists() and any("now also passes" in s for s in logs), logs)

# single-only challenge (D30 sha1-hulud): no generalize, no replay
root = TD / "speed" / "single-only"
(root / "single_solve").mkdir(parents=True)
(root / "single_solve" / "start.json").write_text("{}")
(root / "time_trial").mkdir()
(root / "mastery").mkdir()
mk_solver(root / "solver", {"auto-mastery-1": {"a": "1"}})
gen, tests_run, logs = [], [], []
with patched({**QUIET, (orchestrate.solvers, "test_solver"): lambda *a, **k: tests_run.append(1) or [],
              (orchestrate.paths, "solver_dir"): lambda b: root / "solver",
              (orchestrate, "chain_for"): lambda b, pools, gov: gen.append(b)}):
    out = orchestrate.speed_harden(cid="binary-reverse-engineering-day-30-sha1-hulud", log=logs.append)
check("#2 single-only challenge (empty time_trial/ + mastery/): skipped -- no replay, no generalize",
      out == {} and not gen and not tests_run and any("single-only" in s for s in logs), (out, logs))
check("#2 _single_only: timed state present / unknown layout -> False",
      not orchestrate._single_only(TD / "speed" / "slower") and not orchestrate._single_only(TD / "nowhere"))

# the real accept step honours _keep_gen_snap
acc = orchestrate.Chain.__new__(orchestrate.Chain)
acc.base, acc.root = "acc", TD / "acc"
acc.sdir = mk_solver(acc.root / "solver", {"c1": {"a": "1"}})
acc._baseline = {"c1"}
for keep in (True, False):
    acc._snap_dir().mkdir(parents=True, exist_ok=True)
    acc._keep_gen_snap = keep
    with patched({**QUIET, (orchestrate.solvers, "test_solver"): lambda sdir, **k: [{"case": "c1", "ok": True, "seconds": 0.1}]}):
        acc._accept_or_restore("acc")
    check(f"#2 _accept_or_restore on accept: snapshot {'kept' if keep else 'dropped'} with _keep_gen_snap={keep}",
          acc._snap_dir().exists() == keep)
shutil.rmtree(acc._snap_dir(), ignore_errors=True)

# ------------------------------------------------------------------ #3 hof_race + `hctf why`
states = []
solved = {}
with patched({**QUIET, (orchestrate, "set_state"): lambda base, **kw: states.append((base, kw.get("stage"))),
              (cli, "gm_solved"): lambda cid: solved.get(cid, False),
              (orchestrate.timed, "last_result"): lambda cid: {"untimed": True},
              (orchestrate.paths, "solver_dir"): lambda b: TD / "hof" / b / "solver"}):
    os.environ.pop("HUNTRESS_GAME_MASTER_URL", None)
    hulud = "binary-reverse-engineering-day-30-sha1-hulud"
    full = "binary-reverse-engineering-day-30-multi-binary-campaign"
    for m in ("", "/time_trial", "/mastery"):
        solved[full + m] = True
    orchestrate.hof_race({hulud: [{"mode": "single_solve", "id": hulud, "lane": "binary-reverse-engineering"}],
                          full: [{"mode": m, "id": full + s, "lane": "binary-reverse-engineering"}
                                 for m, s in (("single_solve", ""), ("time_trial", "/time_trial"), ("mastery", "/mastery"))]})
check("#3 hof_race: an UNSOLVED single-only chain (D30 sha1-hulud at single:help) is never stamped done",
      (hulud, "done") not in states, states)
check("#3 hof_race: a fully solved chain is still done (unchanged)", (full, "done") in states, states)

WHY = TD / "why"


def run_why(chain_state, single_solved, tt_state):
    shutil.rmtree(WHY, ignore_errors=True)
    for m in ("single_solve", "time_trial", "mastery"):
        (WHY / m).mkdir(parents=True)
    (WHY / "chain.json").write_text(json.dumps(chain_state))
    (WHY / "single_solve" / "start.json").write_text(json.dumps({"attempt_id": "a1", "answer_ids": ["flag"]}))
    if single_solved:
        (WHY / "single_solve" / "submissions.jsonl").write_text(json.dumps({"attempt": "a1", "kind": "correct"}) + "\n")
    if tt_state:
        for m in ("time_trial", "mastery"):
            (WHY / m / "contract.json").write_text("{}")
    modes = {"b": "single_solve", "b/time_trial": "time_trial", "b/mastery": "mastery"}
    buf = io.StringIO()
    with patched({(cli.paths, "resolve_id"): lambda x: x, (cli.paths, "base_id"): lambda x: x.split("/")[0],
                  (cli.paths, "challenge_root"): lambda b: WHY, (cli, "cdir"): lambda cid: WHY / modes[cid]}):
        with contextlib.redirect_stdout(buf):
            cli.c_why(SimpleNamespace(id="b"))
    return buf.getvalue()


o = run_why({"stage": "done", "lane": "binary-reverse-engineering"}, single_solved=False, tt_state=False)
check("#3 why: chain.json 'done' over an UNSOLVED single -> NOT DONE (never 'all modes solved')",
      "all modes solved" not in o and "NOT DONE" in o and "single_solve" in o.split("=>")[-1], o)
o = run_why({"stage": "done", "time_trial_result": "correct", "mastery_result": "correct"}, single_solved=True, tt_state=True)
check("#3 why: every mode solved -> DONE - all modes solved", "DONE - all modes solved." in o, o)
o = run_why({"stage": "done"}, single_solved=True, tt_state=False)
check("#3 why: a solved single-only chain (empty timed dirs) -> DONE", "DONE - all modes solved." in o, o)
o = run_why({"stage": "done"}, single_solved=True, tt_state=True)
check("#3 why: timed modes with state but unsolved -> NOT DONE naming them",
      "NOT DONE" in o and "time_trial, mastery" in o, o)
o = run_why({"stage": "single:help"}, single_solved=False, tt_state=False)
check("#3 why: single:help -> BLOCKED (unchanged)", "BLOCKED" in o, o)

# ------------------------------------------------------------------ #1d in-network race arming: largest single of the day
LR = TD / "lastmb"
for day, chal, size in (("day29", "binary-twins", 36_000_000), ("day30", "binary-campaign", 35_000_000),
                        ("day30", "binary-hulud", 230_000), ("day30", "script-x", 160_000)):
    lat = LR / "challenges" / day / chal / "single_solve" / "artifacts" / "1"
    lat.mkdir(parents=True)
    with open(lat / "artifact-0.bin", "wb") as f:
        f.truncate(size)   # sparse: st_size only
    (lat.parent / "latest").symlink_to(lat)
    (LR / "challenges" / day / chal / "meta.json").write_text(json.dumps(
        {"lane": "script-analysis" if chal.startswith("script") else "binary-reverse-engineering"}))
with patched({(orchestrate, "ROOT"): LR}):
    for _ in range(3):   # glob order must not matter
        mb30 = orchestrate._lane_last_single_mb("binary-reverse-engineering")
    mb_before = orchestrate._lane_last_single_mb("binary-reverse-engineering", before_day="day30")
    mb_script = orchestrate._lane_last_single_mb("script-analysis")
check("#1 D30 shipped binary 35 MB + a 0.23 MB single-only bonus: the lane's last single = the LARGEST (race armed)",
      abs(mb30 - 35.0) < 0.01 and abs(mb_before - 36.0) < 0.01 and abs(mb_script - 0.16) < 0.01,
      (mb30, mb_before, mb_script))

shutil.rmtree(TD, ignore_errors=True)
print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAILURE(S)'}")
sys.exit(1 if failures else 0)
