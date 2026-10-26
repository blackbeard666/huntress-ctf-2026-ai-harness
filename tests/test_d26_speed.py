#!/usr/bin/env python3
"""Day 26 speed post-mortem offline checks (the GM routing fix lives in tests/test_gm_relay.py section 6).

P2: a non-web TT / Mastery gets the parallel live answer (WebParLive) on its first no-clock attempt when a solver gap is
    predicted -- id shapes new to the lane, artifact kinds the Single doesn't ship, an earlier mode of the chain passed
    only by a live answer, or the lane's same mode needed a live answer / generalize the day before -- with the racing
    solver capped; nothing predicted / a clocked pool / a retry -> no parallel live answer.
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

print(f"\n{len(failures)} failure(s)" + (": " + ", ".join(failures) if failures else ""))
sys.exit(1 if failures else 0)
