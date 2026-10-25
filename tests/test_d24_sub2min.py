"""D24 sub-2-min plan (reference: ~/.claude/plans/1-implement-all-fixes-tranquil-flask.md), offline: fakes only, no GM,
no workers.

Track B (single -> TT handoff):
- B5 async handoff: the stopped-at-CORRECT path returns at once and its bookkeeping (prior cases join, the single's case,
     probes, baseline) runs aside; every consumer (generalize, Mastery _late_probes, probe/baseline results, the
     background generalize, the chain's end) joins it first; the TT pre-attempt block does not; duel signal + aside
     join; triage's deferred recon stops at the single's CORRECT; kill switches restore the old path.
- B6 race path: reuse_plan's outs verify the seed (no re-run); seed snapshot + carry check before the race submit; the
     race snapshot goes first when the worker hasn't edited; untimed-evidence caps on the carry / new-id holds.
- B7 TT pre-start at the single's first GM CORRECT: once, only on evidence of an untimed pool, never on a clocked one
     (legacy route / HCTF_RUN_FOR_TIME=1 / clocked TT / a clocked pre-start body latches it off for the run).

Run:  source bin/env.sh && python3 tests/test_d24_sub2min.py      (exit 0 = all pass)
"""
import contextlib
import json
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, duel, orchestrate, solvers, timed, triage, workers  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    """pairs: {(obj, attr): value} -- set, yield, restore."""
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


QUIET = {(orchestrate, "say"): lambda *a, **k: None, (orchestrate, "set_state"): lambda *a, **k: None}
TMP = Path(tempfile.mkdtemp(prefix="d24sub2-", dir=str(ROOT / ".run")))


# ================================================================ Track B
def b_chain(name="b", lane="warmups"):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.base, ch.lane, ch.name = f"{lane}-day-99", lane, name
    ch.root = TMP / name
    ch.sdir = ch.root / "solver"
    ch.sdir.mkdir(parents=True, exist_ok=True)
    (ch.sdir / "solve.py").write_text("print('{}')\n")
    ch.entries = {m: {"id": ch.base if m == "single_solve" else f"{ch.base}/{m}", "mode": m}
                  for m in ("single_solve", "time_trial", "mastery")}
    ch._genx()
    return ch


def slow_bookkeeping(ch, secs=0.4):
    """A stand-in handoff bookkeeping thread: sets ch._bk_done after `secs`."""
    ch._bk_done = False

    def body():
        time.sleep(secs)
        ch._bk_done = True
    ch._handoff_thr = threading.Thread(target=body, daemon=True)
    ch._handoff_thr.start()


# ---------------------------------------------------------------- B5 every consumer joins the bookkeeping first
class _Live:
    passed = True


consumers = {
    "generalize": lambda ch: ch.generalize(f"{ch.base}/time_trial", live=_Live()),   # FAST_LIVE_ACCEPT: returns at once
    "_late_probes(mastery, wait=False)": lambda ch: ch._late_probes(f"{ch.base}/mastery", wait=False),
    "_late_probes(wait=True)": lambda ch: ch._late_probes(f"{ch.base}/time_trial", wait=True),
    "_await_probes": lambda ch: ch._await_probes(0.1),
    "_bg_gen_take": lambda ch: ch._bg_gen_take(ch.base, "test"),
    "_start_bg_gen": lambda ch: ch._start_bg_gen(f"{ch.base}/time_trial", {}),
    "_baseline_results": lambda ch: ch._baseline_results(),
    "_family_pre_result(wait=True)": lambda ch: ch._family_pre_result(wait=True),
    "_mutation_pre_result(wait=True)": lambda ch: ch._mutation_pre_result(wait=True),
    "_compound_pre_result(wait=True)": lambda ch: ch._compound_pre_result(wait=True),
    "_today_pre_result(wait=True)": lambda ch: ch._today_pre_result(f"{ch.base}/mastery", wait=True),
}
STUBS = {**QUIET, (orchestrate, "MUTATION_PROBE"): False, (orchestrate, "COMPOUND_PROBE"): False,
         (orchestrate, "TODAY_PROBE"): False, (orchestrate, "TODAY_MERGE_PROBE"): False,
         (solvers, "test_solver"): lambda *a, **k: [], (cli, "is_complete"): lambda cid: False,
         (cli, "load"): lambda cid, f: {}, (timed, "last_result"): lambda cid: {}}
for name, fn in consumers.items():
    ch = b_chain(f"cons-{name.split('(')[0].strip('_')}")
    slow_bookkeeping(ch)
    with patched(STUBS):
        try:
            fn(ch)
            err = None
        except Exception as e:  # noqa: BLE001
            err = repr(e)
    check(f"B5_{name} joins the handoff bookkeeping before it reads its products", ch._bk_done and err is None,
          err or "returned before the bookkeeping finished")

# the first Time Trial's pre-attempt block takes the probes only if done: it must NOT wait for the bookkeeping
ch = b_chain("cons-tt-nowait")
slow_bookkeeping(ch, 0.6)
with patched(STUBS):
    t0 = time.time()
    ch._family_pre_result(wait=False)
    ch._late_probes(f"{ch.base}/time_trial", wait=False)
    dt = time.time() - t0
check("B5_the TT pre-attempt probes (wait=False) never wait for the bookkeeping", dt < 0.3 and not ch._bk_done, dt)
ch._handoff_thr.join()

# the chain's end (post-run reads cases/) joins it too
ch = b_chain("cons-run")
slow_bookkeeping(ch)
with patched({**STUBS, (orchestrate.procgov, "kill_owner"): lambda tag: 0}):
    ch._run_retrying = lambda: True
    ch.run()
check("B5_Chain.run's end joins the handoff bookkeeping", ch._bk_done)

# a join from the bookkeeping thread itself never deadlocks; no thread / finished thread = no-op
ch = b_chain("cons-self")
ok_self = []
with patched(QUIET):
    def selfjoin():
        ch._handoff_join("self")
        ok_self.append(True)
    ch._handoff_thr = threading.Thread(target=selfjoin, daemon=True)
    ch._handoff_thr.start()
    ch._handoff_thr.join(2)
    ch2 = b_chain("cons-none")
    ch2._handoff_join("nothing")
check("B5__handoff_join from the bookkeeping thread itself / with no thread returns at once", ok_self == [True])

# ---------------------------------------------------------------- B5 the bookkeeping keeps the old order
order = []
ch = b_chain("bk-order")
ch._cases_fut = None
with patched({**QUIET,
              (orchestrate.Chain, "_join_prior_cases"): lambda self, cid: order.append("join_prior_cases"),
              (orchestrate, "ensure_case_and_test"): lambda cid, sdir, full=True: (order.append(f"case full={full}"),
                                                                                   (True, None))[1],
              (orchestrate.Chain, "_start_family_pre"): lambda self, cid: order.append("family"),
              (orchestrate.Chain, "_start_mutation_pre"): lambda self, cid: order.append("mutation"),
              (orchestrate.Chain, "_start_compound_pre"): lambda self, cid: order.append("compound"),
              (orchestrate.Chain, "_start_today_pre"): lambda self, cid: order.append("today"),
              (orchestrate.Chain, "_start_baseline_pre"): lambda self, cid: order.append("baseline")}):
    ch._start_handoff_bookkeeping(ch.base)
    ch._handoff_join("test")
check("B5_bookkeeping order: prior cases joined before the single's case is written, then the probes + baseline",
      order == ["join_prior_cases", "case full=False", "family", "mutation", "compound", "today", "baseline"], order)


# ---------------------------------------------------------------- B5 _single's handoff end to end (fakes)
class FakeDuel:
    def __init__(self):
        self.signalled, self.stopped = None, None

    def signal_stop(self):
        self.signalled = time.time()

    def stop(self, join=10.0):
        time.sleep(0.8)          # a slow racer join
        self.stopped = time.time()

    def alive(self):
        return False


def drive_single(async_on, duel_on=True, bk_secs=0.6):
    """Drive Chain._single through a verified stopped-at-CORRECT handoff -> (seconds until single() returned, events)."""
    ch = b_chain(f"drive-{async_on}-{duel_on}", lane="metadata-forensics")
    ch.sdir = TMP / "drive" / "solver"      # not under dayNN: no lane-shape scan
    ch.sdir.mkdir(parents=True, exist_ok=True)
    (ch.sdir / "solve.py").write_text("print('{}')\n")
    cdir = TMP / f"drive-cdir-{async_on}-{duel_on}"
    cdir.mkdir(parents=True, exist_ok=True)
    ev = {"order": []}
    fd = FakeDuel() if duel_on else None
    ch._duel = fd
    ch._shadow_done = None
    ch._af = None

    def fake_run_worker(cid, stage, prompt, timeout, stop=None, **k):
        stop.wait(5)
        return workers.STOPPED_RC

    def fake_watch(cid, ready, done):
        time.sleep(0.05)
        ch._ready_snap = TMP / "snap"
        ready.set()
        done.wait(3)           # a watcher still busy after the handoff (e.g. mid-verification)
        time.sleep(1.5)
        ev["watch_end"] = time.time()

    def fake_ensure(cid, sdir, full=True):
        time.sleep(bk_secs)
        ev["order"].append(f"case full={full}")
        return True, None

    ch.run_worker = fake_run_worker
    ch._watch_ready = fake_watch
    pairs = {**QUIET, (orchestrate, "ASYNC_HANDOFF"): async_on, (orchestrate, "DUEL_STOP_AT_READY"): async_on,
             (orchestrate, "REUSE_RACE"): False, (orchestrate, "ANSWER_FIRST"): False,
             (orchestrate, "WARM_WORKERS"): False, (orchestrate, "RETRIEVAL"): False, (orchestrate, "INBOX"): False,
             (orchestrate, "PRESTAGE_PRIOR"): False, (orchestrate, "STOP_WHEN_READY"): True,
             (orchestrate, "prior_solver_dir"): lambda lane, sdir: None, (orchestrate, "lane_seed_dir"): lambda lane: None,
             (orchestrate, "triage_summary"): lambda cid, cap=0: "", (orchestrate, "technique_log"): lambda lane: "",
             (orchestrate, "subagent_policy"): lambda lane: "", (orchestrate, "mastery_delta"): lambda *a, **k: "",
             (orchestrate, "carry_over_note"): lambda *a, **k: "",
             (orchestrate, "ensure_case_and_test"): fake_ensure,
             (workers, "render"): lambda *a, **k: "prompt", (workers, "lane_skill"): lambda lane: "",
             (workers, "lane_helpers"): lambda lane: "", (workers, "lane_persona"): lambda lane: "",
             (workers, "lane_playbook"): lambda lane: "",
             (timed, "ensure_started"): lambda cid: ({"answer_ids": ["a"]}, None),
             (cli, "is_complete"): lambda cid: False, (cli, "gm_solved"): lambda cid: False,
             (cli, "cdir"): lambda cid: cdir, (cli, "call"): lambda *a, **k: {"body": {}},
             (cli, "load"): lambda cid, f: {}, (cli, "save"): lambda *a, **k: None,
             (triage, "triage"): lambda *a, **k: None,
             (orchestrate.Chain, "_tool_prefetch"): lambda self, cid, src: None,
             (orchestrate.Chain, "_start_prior_dry_run"): lambda self, cid: None,
             (orchestrate.Chain, "_start_family_calibration"): lambda self: None,
             (orchestrate.Chain, "_maybe_start_shadow"): lambda self, cid, prompt: None,
             (orchestrate.Chain, "_maybe_start_duel"): lambda self, cid, prompt: None,
             (orchestrate.Chain, "_restore_ready_snapshot"): lambda self, snap: ev["order"].append("restore"),
             (orchestrate.Chain, "_record_labels"): lambda self, cid: ev["order"].append("labels"),
             (orchestrate.Chain, "_join_prior_cases"): lambda self, cid: ev["order"].append("join_prior_cases"),
             (orchestrate.Chain, "_start_family_pre"): lambda self, cid: ev["order"].append("probes"),
             (orchestrate.Chain, "_start_mutation_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_start_compound_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_start_today_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_start_baseline_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_single_after_drift"): lambda self: False}
    with patched(pairs):
        t0 = time.time()
        ok = ch.single()
        dt = time.time() - t0
        ev["returned_order"] = list(ev["order"])
        ch._handoff_join("test")
    ev["ok"], ev["duel"], ev["t0"], ev["ch"] = ok, fd, t0, ch
    return dt, ev


dt_on, ev_on = drive_single(True)
check("B5_async: the verified handoff returns without waiting for the bookkeeping / watcher / duel join",
      ev_on["ok"] and dt_on < 1.6 and "case full=False" not in ev_on["returned_order"], (dt_on, ev_on["returned_order"]))
check("B5_async: the snapshot is restored and labels recorded BEFORE return (the TT runs from sdir; in-window localize "
      "reads vocab.json)", ev_on["returned_order"][:2] == ["restore", "labels"], ev_on["returned_order"])
check("B5_async: the bookkeeping still ran (prior cases joined, single's case, probes) after the handoff",
      ev_on["order"][2:] == ["join_prior_cases", "case full=False", "probes"], ev_on["order"])
check("B5_duel: signalled at ready (before single() returned), joined aside",
      ev_on["duel"].signalled is not None and ev_on["duel"].signalled - ev_on["t0"] < dt_on
      and (ev_on["duel"].stopped is None or ev_on["duel"].stopped - ev_on["t0"] > dt_on), vars(ev_on["duel"]))
dt_off, ev_off = drive_single(False)
check("B5_kill switch (HCTF_ASYNC_HANDOFF=0 + HCTF_DUEL_STOP_AT_READY=0): the old synchronous path (watch join, "
      "prior cases, case, duel stop) before return",
      ev_off["ok"] and dt_off >= 1.4 and ev_off["returned_order"] == ["join_prior_cases", "restore", "case full=False",
                                                                       "labels", "probes"]
      and ev_off["duel"].signalled is None and ev_off["duel"].stopped is not None,
      (dt_off, ev_off["returned_order"], vars(ev_off["duel"])))

# ---------------------------------------------------------------- B5 Duel / DuelGroup.signal_stop never blocks
d1 = duel.Duel.__new__(duel.Duel)
d1.stop_evt, d1.thread = threading.Event(), None
g = duel.DuelGroup([d1])
t0 = time.time()
g.signal_stop()
check("B5_DuelGroup.signal_stop sets every racer's stop event without a join", d1.stop_evt.is_set() and time.time() - t0 < 0.1)

# ---------------------------------------------------------------- B5 _single_correct + triage stop
ch = b_chain("correct-evt")
ch._correct_evt = threading.Event()
with patched(QUIET):
    ch._single_correct(ch.base, "test")
check("B5__single_correct sets the CORRECT event (triage's deferred recon stop)", ch._correct_evt.is_set())
ch2 = b_chain("correct-noevt")
ch2._single_correct(ch2.base, "test")   # no event (an earlier-run single): no error
rdir = TMP / "recon"
rdir.mkdir()
(rdir / "a.bin").write_bytes(b"\x7fELF" + b"\0" * 64)
with patched(QUIET):
    full = triage._recon("binary-reverse-engineering-day-99", rdir)
    cut = triage._recon("binary-reverse-engineering-day-99", rdir, stop=lambda: True)
check("B5_triage recon: per-file tool runs skipped once the single is CORRECT",
      any("a.bin" in ln for ln in full) and not any("a.bin" in ln for ln in cut), (full[:4], cut[:4]))

# triage(): a DEFERRED recon whose single went CORRECT is dropped (triage.md keeps the placeholder)
tcid = "binary-reverse-engineering-day-99"
tdir = TMP / "tri"
(tdir / "artifacts" / "latest").mkdir(parents=True)
(tdir / "artifacts" / "latest" / "x.bin").write_bytes(b"\x7fELF" + b"\0" * 64)
gate = threading.Event()
logs = []
real_recon = triage._recon


def slow_recon(cid, root, stop=None):
    gate.wait(5)
    return real_recon(cid, root, stop=stop)


with patched({(cli, "cdir"): lambda cid: tdir, (cli, "load"): lambda cid, f: {}, (triage, "_recon"): slow_recon,
              (triage, "check_shape"): lambda *a, **k: None}):
    stopped = threading.Event()
    p = triage.triage(tcid, defer_recon=lambda: True, log=logs.append, stop=stopped.is_set)
    stopped.set()
    gate.set()
    for _ in range(50):
        if any("dropped" in str(m) for m in logs):
            break
        time.sleep(0.1)
check("B5_triage: the deferred recon/toolchain rewrite is dropped once the single is CORRECT",
      any("dropped" in str(m) for m in logs) and "Still running in the background" in p.read_text(), logs[-3:])


# ---------------------------------------------------------------- B6 race path

B6 = TMP / "b6"
CH6 = B6 / "challenges"


def race_chain(name="race"):
    ch = b_chain(name, lane="script-analysis")
    ch.root = CH6 / "day99" / name
    ch.sdir = ch.root / "solver"
    ch.sdir.mkdir(parents=True, exist_ok=True)
    (ch.sdir / "solve.py").write_text("print('{}')\n")
    return ch


seed = B6 / "prior" / "solver"
(seed / "cases" / "c1").mkdir(parents=True)
(seed / "solve.py").write_text("print('{\"a\": \"1\"}')\n")
(seed / "helper.py").write_text("X = 1\n")
RACEP = {**QUIET, (orchestrate.paths, "CHALLENGES"): CH6, (orchestrate, "ROOT"): B6}

# reuse_plan hands back every solver's raw output
s1, s2 = B6 / "day97" / "x" / "solver", B6 / "day98" / "y" / "solver"
with patched({(solvers, "lane_solver_dirs"): lambda lane: [], (solvers, "all_solver_dirs"): lambda: [s1, s2],
              (solvers, "_lane_of"): lambda p: "script-analysis", (solvers, "_known_ids"): lambda p: set(),
              (solvers, "run_solver"): lambda s, c, a, t=60: ({"a": "1"} if s == s2 else {"a": "0"}, None, 0.1)}):
    plan = solvers.reuse_plan({"answer_ids": ["a"]}, B6, "script-analysis", by_question=False)
check("B6_ reuse_plan returns `outs` (each solver's raw answers, err, secs)",
      set(plan.get("outs") or {}) == {s1, s2} and plan["outs"][s2][0] == {"a": "1"} and plan["best"] == s2, plan)

# _race_snapshot verifies from the plan's run (no re-run); a mismatch is still refused; kill switch re-runs
runs = []


def counting_run(sdir, contract, art, timeout=120, **k):
    runs.append(str(sdir))
    return {"a": "1"}, None, 0.2


for flag, out, want_snap, want_runs in ((True, ({"a": "1"}, None, 0.1), True, 0), (True, ({"a": "2"}, None, 0.1), False, 0),
                                        (True, ({"a": "1"}, "Timeout", 0.1), False, 0), (False, ({"a": "2"}, None, 0.1), True, 1)):
    ch = race_chain(f"verify-{flag}-{out[0]['a']}-{out[1]}")
    runs.clear()
    with patched({**RACEP, (orchestrate, "RACE_VERIFY_FROM_PLAN"): flag, (orchestrate, "CARRY_CHECK"): False,
                  (cli, "confirmed_answers"): lambda cid: {"a": "1"}, (solvers, "run_solver"): counting_run}):
        snap = ch._race_snapshot(ch.base, seed, {"answer_ids": ["a"]}, B6, plan_out=out)
    check(f"B6_ _race_snapshot verify_from_plan={flag} plan_out={out[:2]} -> snapshot={want_snap}, solver re-runs={want_runs}",
          (snap is not None) == want_snap and len(runs) == want_runs
          and (snap is None or ((snap / "helper.py").exists() and not (snap / "cases").exists())), (snap, runs))

# presnap: copy + carry check BEFORE the submit; the post-win snapshot reuses both (no second copy / carry run)
carry_calls = []
ch = race_chain("presnap")
with patched({**RACEP, (orchestrate, "CARRY_CHECK"): True, (cli, "confirmed_answers"): lambda cid: {"a": "1"},
              (orchestrate.Chain, "_carry_gaps"): lambda self, snap: (carry_calls.append(snap), [])[1],
              (solvers, "run_solver"): counting_run}):
    runs.clear()
    pre = ch._race_presnap(seed)
    fut1 = ch._carry_fut
    fut1.result(2)
    no_snap_yet = getattr(ch, "_race_snap", None) is None
    (pre / "marker").write_text("x")           # a second copy would wipe it
    snap = ch._race_snapshot(ch.base, seed, {"answer_ids": ["a"]}, B6, plan_out=({"a": "1"}, None, 0.1), presnap=pre)
check("B6_ presnap: seed copied + carry check started before the submit, not a ready snapshot until verified; the win "
      "reuses both (no re-copy, no second carry run, no solver re-run)",
      pre is not None and no_snap_yet and snap == pre and (pre / "marker").exists() and ch._carry_fut is fut1
      and len(carry_calls) == 1 and not runs and ch._race_snap == pre, (pre, snap, carry_calls, runs))

# _reuse_race end to end: the carry check is running BEFORE the race submit, and the win needs no seed re-run
ev6 = {}
ch = race_chain("race-e2e")
ch._go_lock, ch._go_sent, ch._go_pending = threading.Lock(), True, []
done6 = []


def fake_plan(contract, art, lane, **k):
    return {"high": {"a": "1"}, "spec": {}, "source": {}, "runs": {seed: (1, None, 0.1)}, "best": seed, "alts": {},
            "outs": {seed: ({"a": "1"}, None, 0.1)}}


def fake_bank(self, cid, ids, high, spec, merged, plan):
    ev6["carry_before_submit"] = getattr(self, "_carry_fut", None) is not None
    done6.append(1)
    return 1


with patched({**RACEP, (orchestrate, "CARRY_CHECK"): True, (orchestrate, "RETRIEVAL"): False,
              (orchestrate, "RACE_FORMAT_GATE"): False, (orchestrate, "RACE_PARTIAL"): True,
              (cli, "load"): lambda cid, f: {"answer_ids": ["a"]}, (timed, "latest_artifacts"): lambda cid: B6,
              (cli, "is_complete"): lambda cid: bool(done6), (cli, "confirmed_answers"): lambda cid: {"a": "1"},
              (solvers, "reuse_plan"): fake_plan, (orchestrate.Chain, "_race_bank"): fake_bank,
              (orchestrate.Chain, "_carry_gaps"): lambda self, snap: [], (solvers, "run_solver"): counting_run}):
    runs.clear()
    ch._reuse_race(ch.base)
check("B6_ _reuse_race: the carry-over check runs before the race submit; the win adopts the seed without a re-run",
      ev6.get("carry_before_submit") and getattr(ch, "_race_snap", None) is not None and not runs, (ev6, runs))

# _watch_ready: the race snapshot goes first when the worker hasn't touched the staged code
def watch_with(edited):
    ch = race_chain(f"watch-{edited}")
    ch._race_snap = B6 / "racesnap"
    ch._launch_mtimes = ch._solver_mtimes()
    if edited:
        time.sleep(0.02)
        (ch.sdir / "solve.py").write_text("print('{\"a\": 1}')\n")
    calls = {"spec": 0, "carry": 0}
    ready, done = threading.Event(), threading.Event()
    with patched({**RACEP, (orchestrate, "PREPUSH_AT_STAMP"): False, (orchestrate, "SPEC_POLL"): 0.01,
                  (cli, "is_complete"): lambda cid: True,
                  (orchestrate.Chain, "_newid_kick"): lambda self: None,
                  (orchestrate.Chain, "_web_tt_kick"): lambda self: None,
                  (orchestrate.Chain, "_record_single_method"): lambda self, cid: None,
                  (orchestrate.Chain, "_start_codify"): lambda self, cid: None,
                  (orchestrate.Chain, "_prefetch_tt"): lambda self: None,
                  (orchestrate.Chain, "_prepush_verified"): lambda self, cid, snap, warm=True: None,
                  (orchestrate.Chain, "_spec_snapshot"): lambda self, cid: (calls.__setitem__("spec", calls["spec"] + 1),
                                                                             None)[1],
                  (orchestrate.Chain, "_carry_hold"): lambda self, cid, snap, r, d: (calls.__setitem__(
                      "carry", calls["carry"] + 1), snap)[1]}):
        t = threading.Thread(target=ch._watch_ready, args=(ch.base, ready, done), daemon=True)
        t.start()
        ready.wait(3)
        done.set()
        t.join(3)
    return ch, calls


chw, cw = watch_with(False)
check("B6_ _watch_ready: worker hasn't edited -> the race snapshot is handed over without a spec copy/re-run",
      chw._ready_snap == chw._race_snap and cw == {"spec": 0, "carry": 1}, cw)
chw, cw = watch_with(True)
check("B6_ _watch_ready: worker edited -> its own snapshot is tried first (old order), race snapshot as fallback",
      chw._ready_snap == chw._race_snap and cw["spec"] >= 1 and cw["carry"] == 1, cw)
with patched({(orchestrate, "RACE_SNAP_FIRST"): False}):
    chw, cw = watch_with(False)
check("B6_ kill switch HCTF_RACE_SNAP_FIRST=0: the spec snapshot is always tried first", cw["spec"] >= 1, cw)

# untimed evidence (the GM gives ONE timed attempt per mode: unknown = clocked)
def ev_chain(rfts, last=None):
    ch = b_chain("evidence")
    for m, v in rfts.items():
        if v is not None:
            ch.entries[m]["run_for_time_supported"] = v
    return ch, (lambda cid: (last or {}) if cid.endswith("time_trial") else {})


cases6 = [("every timed list entry run_for_time_supported", {"time_trial": True, "mastery": True}, None, "auto", True),
          ("one timed entry without it (legacy route)", {"time_trial": True, "mastery": None}, None, "auto", False),
          ("no list flag, no attempt yet", {"time_trial": None, "mastery": None}, None, "auto", False),
          ("HCTF_RUN_FOR_TIME=1 (HoF pool first)", {"time_trial": True, "mastery": True}, None, "1", False),
          ("the TT's last attempt came back untimed", {"time_trial": None, "mastery": None},
           {"attempt_id": "a", "deadline": None, "run_for_time": False, "no_clock": True}, "auto", True),
          ("the TT's last plain attempt was CLOCKED", {"time_trial": True, "mastery": True},
           {"attempt_id": "a", "deadline": "2026-10-25T13:00:00Z"}, "auto", False)]
for label, rfts, last, rft, want in cases6:
    ch, lr = ev_chain(rfts, last)
    import os as _os
    old = _os.environ.get("HCTF_RUN_FOR_TIME")
    _os.environ["HCTF_RUN_FOR_TIME"] = rft
    try:
        with patched({(timed, "last_result"): lr}):
            got = ch._untimed_evidence()
    finally:
        if old is None:
            _os.environ.pop("HCTF_RUN_FOR_TIME", None)
        else:
            _os.environ["HCTF_RUN_FOR_TIME"] = old
    check(f"B6_ untimed evidence: {label} -> {want}", got is want, got)
ch, lr = ev_chain({"time_trial": True, "mastery": True})
with patched({(timed, "last_result"): lr, (orchestrate, "_CLOCKED_PRESTART"): [1]}):
    check("B6_ untimed evidence: a clocked pre-start seen this run -> False for everyone", ch._untimed_evidence() is False)

# _carry_hold: bounded wait on an untimed pool; the full wait otherwise
def carry_with(evidence, secs=1.0):
    ch = race_chain(f"carry-{evidence}")
    ch._carry_fut = orchestrate.ThreadPoolExecutor(max_workers=1).submit(lambda: (time.sleep(secs), ["d01-x"])[1])
    with patched({**RACEP, (orchestrate, "CARRY_WAIT_UNTIMED"): 0.2, (orchestrate, "CARRY_CHECK_MAX"): 0.0,
                  (orchestrate, "NEWID_HOLD"): 0.0, (orchestrate.Chain, "_untimed_evidence"): lambda self: evidence}):
        t0 = time.time()
        out = ch._carry_hold(ch.base, B6 / "s", threading.Event(), threading.Event())
        return out, time.time() - t0


out, dt = carry_with(True)
check("B6_ untimed pool: the carry-over wait is capped (HCTF_CARRY_WAIT_UNTIMED) and the snapshot handed over",
      out == B6 / "s" and dt < 0.6, dt)
out, dt = carry_with(False)
check("B6_ clocked / unknown pool: the carry-over check is awaited as before", out == B6 / "s" and dt >= 0.9, dt)

# _newid_result: untimed -> skip a huge new-id dry run, cap a small one; unknown -> NEWID_SYNC_MAX as before
def newid_with(evidence, n_new, gap_secs=1.0):
    ch = race_chain(f"newid-{evidence}-{n_new}")
    called = []
    snapd = B6 / f"nsnap-{evidence}-{n_new}"
    snapd.mkdir(exist_ok=True)
    (snapd / "solve.py").write_text("")
    with patched({**RACEP, (orchestrate, "NEWID_SYNC_MAX"): 1.5, (orchestrate, "NEWID_SYNC_UNTIMED"): 0.2,
                  (orchestrate, "NEWID_SYNC_SKIP_IDS"): 2000,
                  (orchestrate.Chain, "_untimed_evidence"): lambda self: evidence,
                  (orchestrate.Chain, "_newid_ids"): lambda self: [f"n{i}" for i in range(n_new)],
                  (orchestrate.Chain, "_newid_gaps"): lambda self, cid, s: (called.append(1), time.sleep(gap_secs),
                                                                             ["n0"])[2]}):
        ch._newid = {}
        t0 = time.time()
        res = ch._newid_result(snapd)
        return res, time.time() - t0, called


res, dt, called = newid_with(True, 2500)
check("B6_ untimed pool, > HCTF_NEWID_SYNC_SKIP_IDS new ids: no synchronous dry run, no hold", res is None and not called
      and dt < 0.2, (res, dt, called))
res, dt, called = newid_with(True, 10)
check("B6_ untimed pool, few new ids: the dry run is capped at HCTF_NEWID_SYNC_UNTIMED", res is None and called
      and dt < 0.6, (res, dt))
res, dt, called = newid_with(False, 2500, gap_secs=0.3)
check("B6_ clocked / unknown pool: the synchronous dry run runs as before (even for many new ids)",
      res == ["n0"] and called, (res, dt))


# ---------------------------------------------------------------- B7 TT pre-start at the single's first GM CORRECT
from hctf import hb_timed  # noqa: E402


def pre_chain(name, rfts=True):
    ch = b_chain(name)
    ch._correct_evt = threading.Event()
    for m in ("time_trial", "mastery"):
        if rfts:
            ch.entries[m]["run_for_time_supported"] = True
    return ch


def prestart_calls(ch, why_list=("single",), env_rft="auto", extra=None):
    calls = []
    import os as _os
    old = _os.environ.get("HCTF_RUN_FOR_TIME")
    _os.environ["HCTF_RUN_FOR_TIME"] = env_rft
    try:
        with patched({**QUIET, (timed, "last_result"): lambda cid: {}, (orchestrate, "_CLOCKED_PRESTART"): [],
                      (orchestrate.Chain, "_prefetch_mode_start"): lambda self, mode, when: (calls.append((mode, when)),
                                                                                               True)[1],
                      **(extra or {})}):
            ts = [threading.Thread(target=ch._single_correct, args=(ch.base, w)) for w in why_list]
            for t in ts:
                t.start()
            for t in ts:
                t.join(3)
    finally:
        if old is None:
            _os.environ.pop("HCTF_RUN_FOR_TIME", None)
        else:
            _os.environ["HCTF_RUN_FOR_TIME"] = old
    return calls


calls = prestart_calls(pre_chain("pre-ok"), why_list=("single", "reuse race", "answer-first"))
check("B7_ first GM CORRECT on an untimed-evidence route: ONE TT pre-start even when watcher, race and answer-first "
      "report it at once", len(calls) == 1 and calls[0][0] == "time_trial" and "first GM CORRECT" in calls[0][1], calls)
calls = prestart_calls(pre_chain("pre-legacy", rfts=False))
check("B7_ never on a route without untimed evidence (legacy timed-by-default: a plain start starts the clock)", not calls,
      calls)
calls = prestart_calls(pre_chain("pre-rft1"), env_rft="1")
check("B7_ never with HCTF_RUN_FOR_TIME=1 (HoF pool first = clocked)", not calls, calls)
calls = prestart_calls(pre_chain("pre-latched"), extra={(orchestrate, "_CLOCKED_PRESTART"): ["x/time_trial"]})
check("B7_ never once a clocked pre-start was seen this run (latch)", not calls, calls)
calls = prestart_calls(pre_chain("pre-clockedtt"),
                       extra={(timed, "last_result"): lambda cid: {"attempt_id": "a", "deadline": "2026-10-25T13:00:06Z"}
                              if cid.endswith("time_trial") else {}})
check("B7_ never when this TT's last plain attempt was clocked", not calls, calls)
with patched({(orchestrate, "PRESTART_AT_CORRECT"): False}):
    calls = prestart_calls(pre_chain("pre-off"))
check("B7_ kill switch HCTF_PRESTART_AT_CORRECT=0: no pre-start at CORRECT (the handoff one only)", not calls, calls)
ch = pre_chain("pre-done")
ch._prefetch_started = True
calls = prestart_calls(ch)
check("B7_ no second pre-start once one was launched", not calls, calls)

# a CLOCKED pre-start body latches the feature off for every chain of the run
TD7 = TMP / "b7-timed"
ch = pre_chain("pre-clocked-body")
latch = []
with patched({**QUIET, (orchestrate, "_CLOCKED_PRESTART"): latch, (orchestrate, "PREFETCH_TT"): True,
              (cli, "is_complete"): lambda cid: False, (timed, "timed_dir"): lambda cid: TD7 / "tt",
              (cli, "call"): lambda *a, **k: {"http": 200, "body": {"answer_ids": ["a"], "attempt_id": "att",
                                                                   "deadline": "2026-10-25T13:00:30Z"}}}):
    launched = ch._prefetch_mode_start("time_trial", "test")
    for _ in range(50):
        if latch:
            break
        time.sleep(0.05)
    ch2 = pre_chain("pre-after-latch")
    with patched({(timed, "last_result"): lambda cid: {}}):
        ev_after = ch2._untimed_evidence()
check("B7_ a clocked pre-start body latches the feature off (no untimed evidence for any chain after it)",
      launched and latch == [f"{ch.base}/time_trial"] and ev_after is False and not (TD7 / "tt" / ".prefetch.json").exists(),
      (launched, latch, ev_after))

# the call sites: _watch_ready's first is_complete, the race win, answer-first's watch
srcw = __import__("inspect").getsource(orchestrate.Chain._watch_ready)
srcr = __import__("inspect").getsource(orchestrate.Chain._race_submit)   # _reuse_race's submit half (D25 B3b)
srca = __import__("inspect").getsource(orchestrate.AnswerFirst._watch)
check("B7_ _single_correct is called at the watcher's first is_complete, right after the race submit, and by answer-first",
      "_single_correct(cid" in srcw and srcr.index("_single_correct(cid") < srcr.index("_race_snapshot(cid")
      and "_single_correct" in srca)

# hb_timed trusts a pre-start for 300 s, then reconnects with a normal start
hw = TMP / "b7-hw"
adir = hw / ".run" / "tmp-timed" / "x_time_trial"
adir.mkdir(parents=True)
(adir / "contract.json").write_text(json.dumps({"answer_ids": ["a"], "attempt_id": "att1"}))
(adir / "f.bin").write_bytes(b"x")
for age, want in ((10, True), (400, False)):
    (adir / ".prefetch.json").write_text(json.dumps({"attempt_id": "att1", "files": ["f.bin"], "t": time.time() - age}))
    (adir / ".prefetch.reused").unlink(missing_ok=True)
    with patched({(hb_timed, "HW"): hw}):
        got = hb_timed._prestarted_body("x/time_trial")
    check(f"B7_ hb_timed reuses a {age} s old pre-start: {want} (HCTF_PRESTART_TRUST_S 300)", (got is not None) == want, got)


shutil.rmtree(TMP, ignore_errors=True)
if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D24 sub-2-min checks passed")
