#!/usr/bin/env python3
"""Day 26 speed post-mortem offline checks (the GM routing fix lives in tests/test_gm_relay.py section 6).

P2: a non-web TT / Mastery gets the parallel live answer (WebParLive) on its first no-clock attempt when a solver gap is
    predicted -- id shapes new to the lane, artifact kinds the Single doesn't ship, an earlier mode of the chain passed
    only by a live answer, or the lane's same mode needed a live answer / generalize the day before -- with the racing
    solver capped; nothing predicted / a clocked pool / a retry -> no parallel live answer.
A1-A5 (rehearsal fair D26 follow-ups, 10-27): single duels off by default, earlier-day artifact kinds are no gap, a field list
    too long for a live answer leaves the runner uncapped, small live answers at medium effort, background triage
    extract when recon is deferrable.
No GM, no workers: fakes only.

Run:  source bin/env.sh && python3 tests/test_d26_speed.py      (exit 0 = all pass)
"""
import contextlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, orchestrate  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {str(detail)[:400]}"))
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


TD = Path(tempfile.mkdtemp(prefix="d26speed-"))
said = []


def bare_chain(lane="warmups", base="warmups-day-26", chal="warmups-x"):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base = lane, base
    ch.entries = {"single_solve": {"id": base}, "time_trial": {"id": f"{base}/time_trial"},
                  "mastery": {"id": f"{base}/mastery"}}
    ch.sdir = TD / "challenges" / "day26" / chal / "solver"
    return ch


def contract(ids, arts):
    return {"answer_ids": ids, "questions": [{"id": a, "artifact": f"evidence.zip -> {f}"} for a, f in zip(ids, arts)]}


SINGLE = contract(["answer"], ["base.apk"])
loads = {}
started = []


def fake_start(self):
    started.append(self)
    return self


ENV = {(orchestrate, "say"): lambda *a, **k: said.append(a[0] if a else ""),
       (orchestrate, "PAR_LIVE"): True, (orchestrate, "LIVE_ANSWER"): True, (orchestrate, "LIVE_FIRST"): True,
       (orchestrate.WebParLive, "start"): fake_start,
       (orchestrate.Chain, "_expect_untimed"): lambda self: True,
       (orchestrate.Chain, "_ahead_new"): lambda self, mode: 0,
       (orchestrate, "ROOT"): TD,
       (cli, "load"): lambda cid, name: loads.get((cid, name))}

with patched(ENV):
    # nothing predicted
    loads.clear()
    loads[("warmups-day-26", "start.json")] = SINGLE
    loads[("warmups-day-26/mastery", "contract.json")] = contract(["set1.answer"], ["base.apk"])
    ch = bare_chain()
    r = orchestrate.Chain._web_par_live(ch, "warmups-day-26/mastery", "mastery", 0, False)
    check("P2 no predicted gap: no parallel live answer (the runner alone, as before)", r is None and not started, said[-2:])

    # artifact kinds the Single doesn't ship (D26 mobile: split APK in the TT)
    loads[("mobile-android-day-26-x/time_trial", "contract.json")] = contract(["answer"], ["feature.apk.zip"])
    loads[("mobile-android-day-26-x", "start.json")] = SINGLE
    ch = bare_chain("mobile-android", "mobile-android-day-26-x", "mobile-x")
    r = orchestrate.Chain._web_par_live(ch, "mobile-android-day-26-x/time_trial", "time_trial", 0, False)
    check("P2 artifact kinds the Single doesn't ship -> parallel live answer, solver capped",
          isinstance(r, orchestrate.WebParLive) and r.budget == orchestrate.PAR_LIVE_BUDGET
          and any("artifact kinds" in m and ".zip" in m for m in said), said[-1:])

    # id shapes new to the lane
    started.clear()
    with patched({(orchestrate.Chain, "_ahead_new"): lambda self, mode: 1677}):
        ch = bare_chain()
        r = orchestrate.Chain._web_par_live(ch, "warmups-day-26/mastery", "mastery", 0, False)
    check("P2 contract-ahead (1677 new id shapes) -> parallel live answer", r is not None and len(started) == 1)

    # an earlier mode of this chain passed only by a live answer (D26 mobile Mastery after its TT)
    started.clear()
    ch = bare_chain()
    ch._live_passed = {"time_trial"}
    r = orchestrate.Chain._web_par_live(ch, "warmups-day-26/mastery", "mastery", 0, False)
    check("P2 the TT passed only by a live answer -> the Mastery gets one at once",
          r is not None and any("time_trial passed only by a live answer" in m for m in said), said[-1:])

    # the lane's same mode needed a live answer the previous day (D25 warmups Mastery -> D26 repeated it)
    started.clear()
    prev = TD / "challenges" / "day25" / "warmups-old"
    (prev / "mastery").mkdir(parents=True)
    (prev / "meta.json").write_text(json.dumps({"lane": "warmups"}))
    (prev / "mastery" / "worker-live-local-1.log").write_text("{}")
    ch = bare_chain()
    r = orchestrate.Chain._web_par_live(ch, "warmups-day-26/mastery", "mastery", 0, False)
    check("P2 yesterday's warmups Mastery needed a live answer -> today's gets one",
          r is not None and any("needed a live answer yesterday" in m for m in said), said[-1:])
    r = orchestrate.Chain._web_par_live(ch, "warmups-day-26/time_trial", "time_trial", 0, False)
    check("P2 ... but not the TT (yesterday's TT was clean)", r is None)

    # never on a retry, a resumed attempt, or a clocked pool
    for label, args, extra in (("a retry (attempt 1)", (1, False), {}), ("a resumed / untimed-pool op", (0, True), {}),
                               ("a clocked pool", (0, False),
                                {(orchestrate.Chain, "_expect_untimed"): lambda self: False}),
                               ("HCTF_PAR_LIVE=0", (0, False), {(orchestrate, "PAR_LIVE"): False})):
        started.clear()
        with patched(extra):
            ch = bare_chain()
            r = orchestrate.Chain._web_par_live(ch, "warmups-day-26/mastery", "mastery", *args)
        check(f"P2 {label}: no parallel live answer", r is None and not started)

# ---- P4: CPU contention + today's two bugs -------------------------------------------------------------------------
from hctf import duel, solvers, timed, workers  # noqa: E402


class FakeChain:
    base = "warmups-day-26"
    lane = "warmups"
    sdir = ROOT / "challenges" / "day26" / "warmups-x" / "solver"

    def _worker_env(self, cid, stage):
        return {}


launched, logs, done = [], [], {"v": False}
with patched({(duel, "_reserve"): lambda key, extra=False: True, (duel, "_release"): lambda key: None,
              (duel, "_copy_solver"): lambda src, dst, cases: done.update(v=True),   # CORRECT lands during the copy
              (workers, "run_local"): lambda *a, **k: launched.append(a) or (0, Path("x.log")),
              (duel, "_mirror"): lambda sdir, stage, n: TD / f"duel{n}" / "solver"}):
    d = duel.Duel(FakeChain(), "warmups-day-26", "single", "prompt", 60, cases=False)
    d.start(delay=0, skip=lambda: done["v"], log=logs.append)
    d.thread.join(5)
check("P4 a single duel whose mode completed during the solver copy is not launched (D26 warmups racers +3-5 s)",
      not launched and any("not launched" in m for m in logs), logs)
d = duel.Duel(FakeChain(), "warmups-day-26", "single", "prompt", 60, cases=False)
d2 = duel.Duel(FakeChain(), "warmups-day-26/time_trial", "generalize", "prompt", 60, cases=False)
check("P4 single-duel racers run niced (HCTF_NICE); generalize duels are untouched",
      d._env().get("HCTF_NICE") == duel.SINGLE_NICE and duel.SINGLE_NICE and "HCTF_NICE" not in d2._env())

# a case dir still being written (no contract.json yet) no longer fails the whole baseline
sd = TD / "solvecase" / "solver"
(sd / "cases" / "auto-mastery-done").mkdir(parents=True)
(sd / "cases" / "auto-mastery-writing").mkdir(parents=True)
(sd / "cases" / "auto-mastery-done" / "contract.json").write_text(json.dumps({"answer_ids": ["a"]}))
(sd / "cases" / "auto-mastery-done" / "expected.json").write_text(json.dumps({"a": "1"}))
(sd / "solve.py").write_text("import json,sys\nprint(json.dumps({'a': '1'}))\n")
with patched({(solvers, "run_solver"): lambda sdir, c, art, timeout=120, env_extra=None: ({"a": "1"}, None, 0.01)}):
    try:
        res = solvers.test_solver(sd, parallel=1)
        err = None
    except FileNotFoundError as e:
        res, err = None, e
check("P4 test_solver skips a case without contract.json instead of raising (D26 async baseline FileNotFoundError)",
      err is None and [r["case"] for r in res] == ["auto-mastery-done"] and res[0]["ok"], (err, res))

# the early generalize stands down when the runner already returned on that attempt (D26: two generalize workers)
ch = bare_chain()
ch._early = None
att_dir = TD / "att"
att_dir.mkdir()
(att_dir / "contract.json").write_text(json.dumps({"attempt_id": "ca7796e4", "answer_ids": ["set1.message"]}))
said.clear()
with patched({(orchestrate, "say"): lambda *a, **k: said.append(a[0] if a else ""),
              (workers, "EARLY_GENERALIZE"): True,
              (timed, "last_result"): lambda cid: {"attempt_id": "ca7796e4", "result": "solver_incomplete"},
              (cli, "attempt_id"): lambda c: c.get("attempt_id"),
              (cli, "save"): lambda *a, **k: (_ for _ in ()).throw(AssertionError("saved"))}):
    orchestrate.Chain._early_event(ch, "warmups-day-26/mastery",
                                   {"event": "solved", "local": str(att_dir), "attempt_id": "ca7796e4",
                                    "result": "solver_incomplete", "missing": ["set1.message"]})
check("P4 early generalize: the runner already returned on this attempt -> no second generalize",
      ch._early is None and any("already returned" in m for m in said), said[-2:])

# P5: a slow mastery_delta reaches the worker through the inbox instead of holding the go text
import threading  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
gate = threading.Event()
ch = bare_chain()
notes = []
with patched({(orchestrate, "DELTA_WAIT"): 0.1, (orchestrate, "say"): lambda *a, **k: None,
              (orchestrate.Chain, "_deliver_note"): lambda self, cid, note, key: notes.append((key, note))}):
    fut = ThreadPoolExecutor(max_workers=1).submit(lambda: gate.wait(5) and "MASTERY COMPOUNDS: x")
    t0 = __import__("time").time()
    got = orchestrate.Chain._delta_or_late(ch, "warmups-day-26", fut)
    took = __import__("time").time() - t0
    gate.set()
    fut.result(5)
    __import__("time").sleep(0.2)
check("P5 a slow mastery_delta: the go text gets '' after DELTA_WAIT, the text follows via the inbox",
      got == "" and took < 1.0 and notes == [("delta", "MASTERY COMPOUNDS: x")], (got, took, notes))
fut = ThreadPoolExecutor(max_workers=1).submit(lambda: "MASTERY COMPOUNDS: y")
fut.result()
check("P5 a ready mastery_delta is inlined as before", orchestrate.Chain._delta_or_late(ch, "w", fut) == "MASTERY COMPOUNDS: y")

# ---- rehearsal fair D26 follow-ups (10-27): host load at the drop, noisy gap trigger, slow small live answers ---------------
# A1: single duels are off by default; generalize duels are not
check("A1 single duel off by default (HCTF_DUEL_SINGLE=0)",
      duel.eligible("warmups", stage="single") == (False, "single duels off (HCTF_DUEL_SINGLE=0)"))
check("A1 generalize duels unaffected", duel.eligible("warmups")[0] is True)
with patched({(duel, "SINGLE"): True}):
    check("A1 HCTF_DUEL_SINGLE=1 -> single duels as before", duel.eligible("warmups", stage="single")[0] is True)

# A2: an artifact kind the lane shipped on an earlier day is not a gap (rehearsal D26 metadata: ~20 kinds every timed mode)
with patched(ENV):
    orchestrate._SHAPE_MEMO.clear()
    (TD / ".run").mkdir(exist_ok=True)
    old = TD / "challenges" / "day24" / "meta-old"
    (old / "mastery").mkdir(parents=True)
    (old / "meta.json").write_text(json.dumps({"lane": "metadata-forensics"}))
    (old / "mastery" / "contract.json").write_text(json.dumps(contract(["set1.a", "set2.b"], ["x.evtx", "y.lnk"])))
    loads.clear(); started.clear(); said.clear()
    loads[("metadata-forensics-day-26-x", "start.json")] = contract(["answer"], ["notes.txt"])
    loads[("metadata-forensics-day-26-x/time_trial", "contract.json")] = contract(["set1.a", "set2.b"],
                                                                               ["a.evtx", "b.lnk"])
    ch = bare_chain("metadata-forensics", "metadata-forensics-day-26-x", "meta-x")
    r = orchestrate.Chain._web_par_live(ch, "metadata-forensics-day-26-x/time_trial", "time_trial", 0, False)
    check("A2 kinds shipped on an earlier day (.evtx/.lnk) -> no predicted gap", r is None and not started, said[-2:])
    loads[("metadata-forensics-day-26-x/time_trial", "contract.json")] = contract(["set1.a", "set2.b"],
                                                                               ["a.evtx", "b.pcap"])
    r = orchestrate.Chain._web_par_live(ch, "metadata-forensics-day-26-x/time_trial", "time_trial", 0, False)
    check("A2 ... a kind NEW to the lane (.pcap) still predicts one",
          r is not None and any(".pcap" in m and ".evtx" not in m for m in said), said[-1:])

    # A3: more fields than a live answer takes -> the runner alone, its solver NOT capped (rehearsal D26 script: 16770 ids)
    started.clear(); said.clear()
    loads[("warmups-day-26", "start.json")] = SINGLE
    loads[("warmups-day-26/mastery", "contract.json")] = {"answer_ids": [f"set{i}.q{i}-x{i % 7}" for i in range(2000)]}
    with patched({(orchestrate.Chain, "_ahead_new"): lambda self, mode: 1677}):
        r = orchestrate.Chain._web_par_live(bare_chain(), "warmups-day-26/mastery", "mastery", 0, False)
    check("A3 2000 fields + a predicted gap -> no parallel live answer (runner uncapped)",
          r is None and not started and any("too many for a live answer" in m for m in said), said[-1:])

# A4: a live answer on a few fields runs at medium effort; a longer list keeps the lane's effort
check("A4 live answer on 1 field -> medium", orchestrate.live_effort_env(1) == {"HCTF_X_EFFORT": "medium"})
check("A4 live answer on 10 fields -> lane effort", orchestrate.live_effort_env(10) == {})
with patched({(orchestrate, "LIVE_SMALL_EFFORT"): ""}):
    check("A4 HCTF_LIVE_SMALL_EFFORT='' -> lane effort", orchestrate.live_effort_env(1) == {})

# A5: triage unpacks in the background when recon is deferrable at its start (D26 binary: 7z 12.7-47.8 s on the go path)
import time as _t  # noqa: E402
from hctf import triage, toolchain  # noqa: E402
mdir = TD / "tri" / "single_solve"
(mdir / "artifacts" / "latest").mkdir(parents=True)
(mdir / "artifacts" / "latest" / "crash.zip").write_bytes(b"PK")
ext_gate = threading.Event()
logs = []


def slow_extract(files, dest, depth=2):
    ext_gate.wait(5)
    return ["", "## Extracted (pre-unpacked for you -- read these instead of unzipping again)", "", "- MEMBERS-LISTED"]


TRI = {(cli, "cdir"): lambda cid: mdir, (cli, "load"): lambda cid, name: {"answer_ids": ["a"]},
       (cli, "confirmed_answers"): lambda cid: {}, (triage, "check_shape"): lambda *a, **k: None,
       (triage, "_describe"): lambda f: [f"- {f.name}"], (triage, "_extract_all"): slow_extract,
       (triage, "_recon"): lambda cid, ex, **k: ["", "## Recon", "RECON-LINES"],
       (toolchain, "scan_order"): lambda ex: [], (toolchain, "check"): lambda *a, **k: ["", "## Toolchain", "TC"],
       (toolchain, "challenge_text"): lambda *a, **k: "", (triage, "TOOLCHAIN_WAIT"): 0.1}
with patched(TRI):
    t0 = _t.time()
    path = triage.triage("tri", defer_recon=lambda: True, log=logs.append)
    took = _t.time() - t0
    first = path.read_text()
    ext_gate.set()
    for _ in range(50):
        if "MEMBERS-LISTED" in path.read_text() and "RECON-LINES" in path.read_text():
            break
        _t.sleep(0.1)
    final = path.read_text()
check("A5 deferrable recon at triage start -> the go path does not wait for the extract",
      took < 2 and "in the background" in first and "MEMBERS-LISTED" not in first, (took, first[-400:]))
check("A5 ... the member list + recon + toolchain land in triage.md afterwards",
      "MEMBERS-LISTED" in final and "RECON-LINES" in final and "TC" in final
      and any("extract" in m and "landed" in m for m in logs), (final[-400:], logs))
ext_gate.clear()
with patched({**TRI, (triage, "_extract_all"): lambda files, dest, depth=2: ["", "- INLINE-MEMBERS"]}):
    path = triage.triage("tri", defer_recon=lambda: False, log=logs.append)
check("A5 not deferrable -> extract inline as before", "INLINE-MEMBERS" in path.read_text())

print(f"\n{len(failures)} failure(s)" + (": " + ", ".join(failures) if failures else ""))
sys.exit(1 if failures else 0)
