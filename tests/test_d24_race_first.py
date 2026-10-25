"""D24 race-first handoff (HCTF_RACE_FIRST_HANDOFF), offline: fakes only, no GM, no workers.
- a reuse-race win with a verified seed during a slow triage hands over at once: no worker launch, no wait for triage,
  the snapshot restored + labels recorded + the bookkeeping started, the warm worker cancelled
- no verified handover within HCTF_RACE_FIRST_WAIT (e.g. a carry-over hold that needs a worker) -> the worker path runs
- a finished carry-over check with gaps -> no race-first attempt at all (the worker adds the carry-over shapes)
- kill switch: triage runs inline and the worker launches as before

Run:  source bin/env.sh && python3 tests/test_d24_race_first.py      (exit 0 = all pass)
"""
import contextlib
import shutil
import sys
import tempfile
import threading
import time
from concurrent.futures import Future
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, orchestrate, timed, triage, workers  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
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


TMP = Path(tempfile.mkdtemp(prefix="d24rf-", dir=str(ROOT / ".run")))


def drive(flag=True, handover=True, carry_gaps=None, race_at=0.3, triage_secs=3.0, wait=0.6):
    """Chain._single with a reuse race that wins at `race_at` s while triage takes `triage_secs` s."""
    name = f"{flag}-{handover}-{carry_gaps}"
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.base, ch.lane, ch.name = "binary-reverse-engineering-day-99", "binary-reverse-engineering", name
    ch.root = TMP / name
    ch.sdir = ch.root / "solver"
    ch.sdir.mkdir(parents=True, exist_ok=True)
    (ch.sdir / "solve.py").write_text("print('{}')\n")
    cdir = TMP / f"cdir-{name}"
    cdir.mkdir(parents=True, exist_ok=True)
    ch.entries = {"single_solve": {"id": ch.base, "mode": "single_solve"}}
    ch._shadow_done, ch._af, ch._duel = None, None, None
    ev = {"order": [], "workers": 0, "watchers": 0, "cancel_warm": 0, "triage_end": None}
    won = threading.Event()

    def fake_race(self, cid):
        time.sleep(race_at)
        self._race_snap = TMP / "racesnap"
        if carry_gaps is not None:
            f = Future()
            f.set_result(carry_gaps)
            self._carry_fut = f
        won.set()

    def fake_triage(*a, **k):
        time.sleep(triage_secs)
        ev["triage_end"] = time.time()

    def fake_watch(self, cid, ready, done):
        ev["watchers"] += 1
        # the race-first watcher hands over only when `handover`; the worker path's watcher always does
        if handover or ev["watchers"] > 1:
            time.sleep(0.05)
            self._ready_snap = TMP / "racesnap"
            ready.set()
            return
        done.wait(10)

    def fake_run_worker(self, cid, stage, prompt, timeout, stop=None, **k):
        ev["workers"] += 1
        ev["worker_at"] = time.time()
        stop.wait(5)
        return workers.STOPPED_RC

    pairs = {(orchestrate, "say"): lambda *a, **k: None, (orchestrate, "set_state"): lambda *a, **k: None,
             (orchestrate, "RACE_FIRST_HANDOFF"): flag, (orchestrate, "RACE_FIRST_WAIT"): wait,
             (orchestrate, "ASYNC_HANDOFF"): True, (orchestrate, "REUSE_RACE"): True,
             (orchestrate, "REUSE_OLD_SOLVERS"): False, (orchestrate, "REUSE_RACE_LANES"): {ch.lane},
             (orchestrate, "ANSWER_FIRST"): False, (orchestrate, "WARM_WORKERS"): False,
             (orchestrate, "RETRIEVAL"): False, (orchestrate, "INBOX"): False, (orchestrate, "PRESTAGE_PRIOR"): False,
             (orchestrate, "STOP_WHEN_READY"): True,
             (orchestrate, "prior_solver_dir"): lambda lane, sdir: None, (orchestrate, "lane_seed_dir"): lambda lane: None,
             (orchestrate, "triage_summary"): lambda cid, cap=0: "", (orchestrate, "technique_log"): lambda lane: "",
             (orchestrate, "subagent_policy"): lambda lane: "", (orchestrate, "mastery_delta"): lambda *a, **k: "",
             (orchestrate, "carry_over_note"): lambda *a, **k: "",
             (orchestrate, "ensure_case_and_test"): lambda cid, sdir, full=True: (True, None),
             (workers, "render"): lambda *a, **k: "prompt", (workers, "lane_skill"): lambda lane: "",
             (workers, "lane_helpers"): lambda lane: "", (workers, "lane_persona"): lambda lane: "",
             (workers, "lane_playbook"): lambda lane: "",
             (timed, "ensure_started"): lambda cid: ({"answer_ids": ["a"]}, None),
             (cli, "is_complete"): lambda cid: won.is_set(), (cli, "gm_solved"): lambda cid: False,
             (cli, "cdir"): lambda cid: cdir, (cli, "call"): lambda *a, **k: {"body": {}},
             (cli, "load"): lambda cid, f: {}, (cli, "save"): lambda *a, **k: None,
             (triage, "triage"): fake_triage,
             (orchestrate.Chain, "_reuse_race"): fake_race,
             (orchestrate.Chain, "_watch_ready"): fake_watch,
             (orchestrate.Chain, "run_worker"): fake_run_worker,
             (orchestrate.Chain, "_cancel_warm"): lambda self: ev.__setitem__("cancel_warm", ev["cancel_warm"] + 1),
             (orchestrate.Chain, "_tool_prefetch"): lambda self, cid, src: None,
             (orchestrate.Chain, "_start_prior_dry_run"): lambda self, cid: None,
             (orchestrate.Chain, "_start_family_calibration"): lambda self: None,
             (orchestrate.Chain, "_maybe_start_shadow"): lambda self, cid, prompt: None,
             (orchestrate.Chain, "_maybe_start_duel"): lambda self, cid, prompt: None,
             (orchestrate.Chain, "_restore_ready_snapshot"): lambda self, snap: ev["order"].append("restore"),
             (orchestrate.Chain, "_record_labels"): lambda self, cid: ev["order"].append("labels"),
             (orchestrate.Chain, "_start_handoff_bookkeeping"): lambda self, cid: ev["order"].append("bookkeeping"),
             (orchestrate.Chain, "_join_prior_cases"): lambda self, cid: None,
             (orchestrate.Chain, "_start_family_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_start_mutation_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_start_compound_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_start_today_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_start_baseline_pre"): lambda self, cid: None,
             (orchestrate.Chain, "_single_after_drift"): lambda self: False}
    with patched(pairs):
        t0 = time.time()
        ok = ch._single()
        ev["dt"] = time.time() - t0
        ev["ok"], ev["t0"] = ok, t0
    return ev


ev = drive()
check("race win during a slow triage -> handed over before triage ends, no worker launched",
      ev["ok"] and ev["dt"] < 1.5 and ev["workers"] == 0 and ev["triage_end"] is None, ev)
check("... the snapshot restored + labels recorded, then the bookkeeping started; the warm worker cancelled",
      ev["order"] == ["restore", "labels", "bookkeeping"] and ev["cancel_warm"] == 1, ev)

ev = drive(handover=False)
check("no verified handover within RACE_FIRST_WAIT -> the worker path runs (after triage), and hands over normally",
      ev["ok"] and ev["workers"] == 1 and ev["triage_end"] is not None and ev["worker_at"] >= ev["triage_end"]
      and ev["watchers"] == 2 and ev["order"][:2] == ["restore", "labels"] and ev["dt"] < 3.0 + 0.6 + 1.5, ev)

ev = drive(carry_gaps=["d07-x"])
check("carry-over check finished with gaps -> no race-first attempt; the worker path adds the carry-over shapes",
      ev["ok"] and ev["workers"] == 1 and ev["watchers"] == 1 and ev["triage_end"] is not None, ev)

ev = drive(carry_gaps=[])
check("carry-over check finished clean -> race-first handoff", ev["ok"] and ev["workers"] == 0 and ev["dt"] < 1.5, ev)

ev = drive(flag=False)
check("kill switch HCTF_RACE_FIRST_HANDOFF=0: triage inline, the worker launches as before",
      ev["ok"] and ev["workers"] == 1 and ev["triage_end"] is not None and ev["dt"] >= 3.0, ev)

shutil.rmtree(TMP, ignore_errors=True)
print()
if failures:
    print(f"{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("all race-first handoff checks passed")
