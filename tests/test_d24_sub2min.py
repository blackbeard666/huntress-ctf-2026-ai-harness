"""D24 sub-2-min plan (reference: ~/.claude/plans/1-implement-all-fixes-tranquil-flask.md), offline: fakes only, no GM,
no workers.

Track B (single -> TT handoff):
- B5 async handoff: the stopped-at-CORRECT path returns at once and its bookkeeping (prior cases join, the single's case,
     probes, baseline) runs aside; every consumer (generalize, Mastery _late_probes, probe/baseline results, the
     background generalize, the chain's end) joins it first; the TT pre-attempt block does not; duel signal + aside
     join; triage's deferred recon stops at the single's CORRECT; kill switches restore the old path.

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


shutil.rmtree(TMP, ignore_errors=True)
if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D24 sub-2-min checks passed")
