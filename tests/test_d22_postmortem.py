"""D22 post-mortem fixes (reference/D22_POSTMORTEM.md), offline: fake GM state, no network, no workers.
- P0 #2  no clock -> the clock-era speed gates stay off (pre-TT single speed, Mastery estimate, untimed non-web harden)
- P0 #3  no clock + slow VM -> a multi-set mode's FIRST attempt runs locally (the pre-measurement Homebase estimate lies)
- P0 #4  a solver-budget cut-off on the VM (`solver_incomplete`, every field empty) re-runs locally, no generalize

Run:  source bin/env.sh && python3 tests/test_d22_postmortem.py      (exit 0 = all pass)
"""
import contextlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import orchestrate, timed, webtarget, workers  # noqa: E402

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


def chain(lane="script-analysis", untimed=True):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base = lane, "x"
    ch.entries = {"time_trial": {"id": "x/time_trial"}, "mastery": {"id": "x/mastery"}}
    ch.sdir = ROOT / ".run" / "nonexistent-solver"
    ch._expect_untimed = lambda: untimed
    return ch


QUIET = {(orchestrate, "say"): lambda *a, **k: None}

# ---------------------------------------------------------------- P0 #2: no clock -> no clock-era speed gates
retimes = []
with patched({**QUIET, (orchestrate.solvers, "run_solver"): lambda *a, **k: (retimes.append(1), ({}, None, a[-1] / 3))[1]}):
    ch = chain(untimed=True)
    orchestrate.Chain._note_single_speed(ch, "x", 3.1, rerun=("s", {}, "a"))
    check("#2 untimed: a 3.1 s single solver sets off no pre-TT speed generalize (and no re-time run)",
          ch._single_slow is None and not retimes, (ch._single_slow, retimes))
    ch = chain(untimed=False)
    orchestrate.Chain._note_single_speed(ch, "x", 6.4, rerun=("s", {}, "a"))
    check("#2 clocked: the 2.5 s clock-era budget still applies (re-timed, still over -> flagged)",
          ch._single_slow is not None and retimes, (ch._single_slow, retimes))

with patched({**QUIET, (orchestrate.solvers, "run_solver"): lambda *a, **k: ({}, None, 24.0)}):
    ch = chain(untimed=True)
    orchestrate.Chain._note_single_speed(ch, "x", 25.0, rerun=("s", {}, "a"))
    check("#2 untimed: a budget-threatening single solver (24 s alone) is still flagged", ch._single_slow == 24.0,
          ch._single_slow)

with patched({**QUIET, (orchestrate, "NO_CLOCK_SPEED", ): False,
              (orchestrate.solvers, "run_solver"): lambda *a, **k: ({}, None, 3.0)}):
    ch = chain(untimed=True)
    orchestrate.Chain._note_single_speed(ch, "x", 3.1, rerun=("s", {}, "a"))
    check("#2 HCTF_NO_CLOCK_SPEED=0 restores the clock-era gate", ch._single_slow == 3.0, ch._single_slow)

gens = []
GEN = {(orchestrate.Chain, "generalize"): lambda self, cid, wrong=None, fixed=None, diag=None: gens.append(diag)}
with patched({**QUIET, **GEN}):
    ch = chain(untimed=True)
    ch._mastery_gate_done = False
    orchestrate.Chain._mastery_speed_gate(ch, "x/mastery")
    check("#2 untimed: the Mastery speed-estimate gate is a no-op", not gens, gens)


def web_gate(lane, tt_solve, n_ids, nsets, untimed=True, routed="local"):
    gens.clear()
    with patched({**QUIET, **GEN,
                  (timed, "last_result"): lambda cid: {"phases": {"solve": tt_solve}, "routed": routed},
                  (workers, "_contract_shape"): lambda cid: (n_ids, 0, nsets),
                  (os, "cpu_count"): lambda: 12}):
        ch = chain(lane=lane, untimed=untimed)
        ch._web_gate_done = False
        orchestrate.Chain._web_speed_gate(ch, "x/mastery")
    return list(gens)


check("#2 untimed non-web: a 20 s TT solver whose 5-set Mastery fits the solver budget -> no blocking harden",
      web_gate("binary-reverse-engineering", 20.0, 50, 5) == [])
check("#2 untimed non-web: a 60 s TT solver x 30 sets (3 waves, est 180 s > 0.8 x 61.5 s) -> still hardens first",
      len(web_gate("binary-reverse-engineering", 60.0, 30, 30)) == 1)
workers._hb["cpu_ratio"] = 8.0
check("#2 untimed non-web: a TT measured on the x8 VM is de-rated before the fit check (60 s VM ~ 7.5 s local)",
      web_gate("binary-reverse-engineering", 60.0, 30, 30, routed="homebase (window unknown)") == [])
workers._hb.pop("cpu_ratio", None)
check("#2 clocked non-web keeps the old blocking harden", len(web_gate("binary-reverse-engineering", 20.0, 50, 5,
                                                                        untimed=False)) == 1)
check("#2 live web lane keeps pole #1 (never blocks)", web_gate("web-exploitation", 40.0, 3, 0) == [])

# ---------------------------------------------------------------- P0 #3: first-attempt routing on a slow VM, no clock
msgs = []
SHAPE108 = {(workers, "_contract_shape"): lambda cid: (108, 0, 108), (workers, "slow_vm"): lambda: True,
            (timed, "last_result"): lambda cid: None}
with patched(SHAPE108):
    check("#3 108-set Mastery, slow VM, unmeasured -> local", workers.no_clock_local("w/mastery", msgs.append) is True)
    check("#3 ... and says why", any("runs locally" in m for m in msgs), msgs)
with patched({**SHAPE108, (workers, "_contract_shape"): lambda cid: (1, 0, 0)}):
    check("#3 single-set TT keeps Homebase (its GM round trips are cheaper)", workers.no_clock_local("w/tt") is False)
with patched({**SHAPE108, (workers, "_contract_shape"): lambda cid: (6, 0, 6)}):
    check("#3 a small fan-out (6-set Mastery) is left to route_costs (replay: mobile 8.5 s local vs 1.25 s Homebase)",
          workers.no_clock_local("w/mastery") is False)
with patched({**SHAPE108, (timed, "last_result"): lambda cid: {"phases": {"solve": 63.9}, "routed": "homebase"}}):
    check("#3 once measured, route_costs decides (no override)", workers.no_clock_local("w/mastery") is False)
with patched({**SHAPE108, (workers, "slow_vm"): lambda: False}):
    check("#3 a fast VM is left to route_costs", workers.no_clock_local("w/mastery") is False)
os.environ["HCTF_RUN_FOR_TIME"] = "1"
with patched(SHAPE108):
    check("#3 HCTF_RUN_FOR_TIME=1 (clocked HoF pool) never forces local", workers.no_clock_local("w/mastery") is False)
del os.environ["HCTF_RUN_FOR_TIME"]

calls = []
ROUTE = {**SHAPE108,
         (workers.webtarget if hasattr(workers, "webtarget") else webtarget, "is_live_cid"): lambda cid: False,
         (workers, "known_window"): lambda cid: None,
         (workers, "untimed_plan"): lambda cid: (10, 0, 0),
         (workers, "_homebase_ready"): lambda log=None: True,
         (workers, "AUTO_HOMEBASE"): True,
         (workers.remote, "gm_transport"): lambda: "local",
         (workers, "run_timed"): lambda *a, **k: (calls.append("local"), {"result": "correct"})[1],
         (workers, "run_hb_timed"): lambda *a, **k: (calls.append("homebase"), {"result": "correct"})[1]}
with patched(ROUTE):
    res = workers.run_timed_auto(ROOT, "w/mastery", log=lambda m: None)
check("#3 run_timed_auto: the 108-set no-clock Mastery's first attempt goes local, not to the VM",
      calls == ["local"] and res.get("routed") == "local", (calls, res))

# ---------------------------------------------------------------- P0 #4: a VM budget cut-off re-runs locally
CUT = {"result": "solver_incomplete", "routed": "homebase (window unknown)", "deadline": None, "no_clock": True,
       "run_for_time": False, "phases": {"solve": 63.88}, "missing": [f"set{i}.message" for i in range(108)]}


def slow_rerun(last, slow=True, n=108):
    with patched({(timed, "last_result"): lambda cid: last, (workers, "slow_vm"): lambda: slow,
                  (workers, "_contract_shape"): lambda cid: (n, 0, n)}):
        return orchestrate.Chain._slow_vm_no_clock("w/mastery")


check("#4 D22 warmups Mastery shape (63.9 s of 65.4 s, 108/108 empty, VM, no clock) -> local re-run", slow_rerun(CUT))
check("#4 a genuine miss (8 s solve, 1 field empty) is NOT a cut-off -> generalize as before",
      not slow_rerun({**CUT, "phases": {"solve": 8.1}, "missing": ["set1.x"]}))
check("#4 a local cut-off is not re-run locally", not slow_rerun({**CUT, "routed": "local"}))
check("#4 a fast VM: no re-run", not slow_rerun(CUT, slow=False))
check("#4 explicit solver_too_slow still re-runs", slow_rerun({**CUT, "result": "solver_too_slow",
                                                               "solver_too_slow": True, "missing": []}))
check("#4 unknown contract size falls back to the result's own counts", slow_rerun(CUT, n=0))

# ---------------------------------------------------------------- P1 #6: the winning method reaches the live answers
import json  # noqa: E402
import tempfile  # noqa: E402
from hctf import cli  # noqa: E402

mm = orchestrate.method_matches
check("#6 same shape matches (any lane)", mm({"d21-apk-N-apk-package-name"}, {"d21-apk-N-apk-package-name"}))
check("#6 live lane: TT proof-1's method applies to Mastery's proof-3 (shuffled slot)", mm({"proof-1"}, {"proof-3"}, live=True))
check("#6 non-live lanes keep exact-shape matching", not mm({"proof-1"}, {"proof-3"}, live=False))
check("#6 live lane: a non-proof method is not offered to a proof field", not mm({"d21-apk-N-x"}, {"proof-3"}, live=True))


def _log(path, cmds, text=None):
    with open(path, "w") as f:
        for c in cmds:
            f.write(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": c}}]}}) + "\n")
        if text:
            f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}) + "\n")


with tempfile.TemporaryDirectory() as d:
    _log(Path(d) / "worker-live-answer-first-20261022T000001.log",
         ["curl -sS -F 'f=@shell.phtml;type=image/gif' $T/upload", "hctf submit web-x --answer proof-1=proof_abcdef123"],
         "Uploaded a GIF89a-prefixed .phtml via /upload, fetched /render?f=shell.phtml -> proof.")
    _log(Path(d) / "worker-single-local-20261022T000000.log", ["python3 solve.py --contract c.json"])
    txt = orchestrate.single_method_text(d)
    check("#6 single_method_text keeps answer-first's exploit + the single worker's work",
          "GIF89a" in txt and "phtml" in txt and "solve.py" in txt, txt[:300])
    ch = chain(lane="web-exploitation")
    with patched({**QUIET, (cli, "cdir"): lambda cid: Path(d),
                  (cli, "load"): lambda cid, name: {"answer_ids": ["proof-1"]} if name == "start.json" else None}):
        orchestrate.Chain._record_single_method(ch, "web-x")
        orchestrate.Chain._record_single_method(ch, "web-x")
    lm = getattr(ch, "_live_methods", [])
    check("#6 recorded once at the single's CORRECT under the single's field shapes",
          len(lm) == 1 and lm[0][0] == {"proof-1"} and "GIF89a" in lm[0][1], lm)

with tempfile.TemporaryDirectory() as d:
    ch = chain()
    with patched({**QUIET, (cli, "cdir"): lambda cid: Path(d), (cli, "load"): lambda cid, name: {"answer_ids": ["a"]}}):
        orchestrate.Chain._record_single_method(ch, "x")
    check("#6 no logs -> nothing recorded, no error", not getattr(ch, "_live_methods", []))

# ---------------------------------------------------------------- P1 #7: the never-seen-class race is capped + logged
import lib.web as libweb  # noqa: E402
from lib import websolve  # noqa: E402
from lib.web import handlers as webhandlers  # noqa: E402

UPLOAD = {"feature_route": "/feature", "render_route": "/render", "preview_guide": "png only",
          "upload_policy": "images", "upload_shape": "multipart"}
with patched({(webhandlers, "for_key"): lambda key, clues: [], (libweb, "_prior_sources"): lambda: ["def answer(): pass"]}):
    check("#7 never-seen class: no handler, no earlier solver names a concept key -> unknown",
          libweb.class_known(UPLOAD, "preview_guide") is False)
with patched({(webhandlers, "for_key"): lambda key, clues: [],
              (libweb, "_prior_sources"): lambda: ["if 'upload_policy' in clues: return upload(base)"]}):
    check("#7 an earlier web solver that names a concept key -> known", libweb.class_known(UPLOAD, "preview_guide"))
with patched({(webhandlers, "for_key"): lambda key, clues: [], (libweb, "_prior_sources"): lambda: ["feature_route render_route"]}):
    check("#7 route-valued / common kit keys never make a class known",
          libweb.class_known({"feature_route": "/f", "render_route": "/r", "secret_note": "x"}, "secret_note") is False)
with patched({(webhandlers, "for_key"): lambda key, clues: [("upload", None)], (libweb, "_prior_sources"): lambda: []}):
    check("#7 a built-in handler for any clue key -> known", libweb.class_known(UPLOAD, "preview_guide"))

budgets = []
race_log = Path(tempfile.mkdtemp()) / "race.jsonl"
os.environ["HCTF_WEB_RACE_LOG"] = str(race_log)
RACE = {(websolve, "base_of"): lambda q, c: "https://t.example/",
        (websolve, "fetch"): lambda *a, **k: (200, ""),
        (libweb, "candidates"): lambda *a, **k: [],
        (websolve, "race"): lambda probes, budget=40, report=None: (budgets.append(budget),
                                                                    report.update(winner=None, elapsed=0.1), None)[2]}
with patched({**RACE, (libweb, "class_known"): lambda c, k: False}):
    libweb.solve_target({"id": "proof-1"}, {}, clues=UPLOAD)
with patched({**RACE, (libweb, "class_known"): lambda c, k: True}):
    libweb.solve_target({"id": "proof-2"}, {}, clues=UPLOAD)
check("#7 unknown class -> race capped at HCTF_WEB_UNKNOWN_KEY_BUDGET (12 s); known -> full 40 s",
      budgets == [libweb.UNKNOWN_KEY_BUDGET, 40] and libweb.UNKNOWN_KEY_BUDGET == 12, budgets)
recs = [json.loads(ln) for ln in race_log.read_text().splitlines()] if race_log.exists() else []
check("#7 every target race is logged (qid, key, known, budget, winner)",
      [(r["qid"], r["known"], r["budget"]) for r in recs] == [("proof-1", False, 12.0), ("proof-2", True, 40)], recs)
del os.environ["HCTF_WEB_RACE_LOG"]

rep = {}
won = websolve.race([("slow-none", lambda: None), ("handler", lambda: "proof_abc12345XYZ")], budget=5, report=rep)
check("#7 race() reports its winner and elapsed", won == "proof_abc12345XYZ" and rep.get("winner") == "handler"
      and rep.get("elapsed") is not None and rep.get("probes") == ["slow-none", "handler"], rep)
rep = {}
import time as _time  # noqa: E402
websolve.race([("hang", lambda: _time.sleep(3))], budget=0.3, report=rep)
check("#7 a race that hits its budget says so", rep.get("timed_out") is True and rep.get("winner") is None, rep)

# ---------------------------------------------------------------- P1 #8/#9: in-run clue-keyed plugins + codify worker
import importlib  # noqa: E402
import threading  # noqa: E402

HDIR = ROOT / "lib" / "web" / "handlers"
plug, bad, clash = HDIR / "zz_d22test_plugin.py", HDIR / "zz_d22test_broken.py", HDIR / "zz_d22test_clash.py"
builtin_upload = webhandlers._HANDLERS["upload"]
try:
    plug.write_text('KEY_MAP = [(r"upload_policy", "zz_d22test_plugin"), (r"preview_guide", "zz_d22test_plugin")]\n'
                    'HANDLERS = {"zz_d22test_plugin": lambda base, clues: "proof_d22test1234"}\n')
    bad.write_text("this is not python(\n")
    clash.write_text('KEY_MAP = [(r"anything", "upload")]\nHANDLERS = {"upload": lambda b, c: None}\n')
    importlib.reload(webhandlers)
    names = [n for n, _fn in webhandlers.for_key("preview_guide", {"preview_guide": "x"})]
    check("#8 a plugin file in lib/web/handlers is auto-loaded and dispatched by its clue KEY",
          "zz_d22test_plugin" in names, names)
    check("#8 one plugin may map several clue-key patterns to its handler",
          sum(1 for _p, n in webhandlers._KEY_MAP if n == "zz_d22test_plugin") == 2)
    check("#8 a broken plugin is skipped; the built-ins still load",
          {"upload", "csrf", "session_fixation"} <= set(webhandlers._HANDLERS))
    check("#8 a plugin cannot hijack a built-in handler name",
          webhandlers._HANDLERS["upload"] is webhandlers.upload and ("anything", "upload") not in webhandlers._KEY_MAP)
finally:
    for p in (plug, bad, clash):
        p.unlink(missing_ok=True)
    importlib.reload(webhandlers)
check("#8 removing a plugin file removes it on the next import", "zz_d22test_plugin" not in webhandlers._HANDLERS)

sd = ROOT / "challenges" / "day22" / "zz-d22test-chal" / "solver"
check("#8 plugin path = lib/web/handlers/<dayNN>_<challenge>.py, its stem the handler name",
      orchestrate.web_plugin_path(sd) == HDIR / "day22_zz_d22test_chal.py")
note = orchestrate.web_plugin_note(sd)
check("#9 the web generalize/seed note names THE per-challenge plugin and forbids the shared __init__ + slot keys",
      "day22_zz_d22test_chal.py" in note and "__init__.py" in note and "proof-N" in note)
check("#9 the single's seed note tells it to submit first, then codify into the plugin",
      "submit the proof first" in orchestrate.web_seed_note(sd) and "day22_zz_d22test_chal.py" in orchestrate.web_seed_note(sd))

fake_chain = type("C", (), {"sdir": sd, "lane": "web-exploitation", "entries": {}})()
wc = orchestrate.WebCodify(fake_chain, "web-x")
try:
    check("#8 landed(): no plugin yet -> False", wc.landed() is False)
    wc.plugin.write_text(f'KEY_MAP = [(r"upload_policy", "{wc.name}")]\nHANDLERS = {{"{wc.name}": lambda b, c: None}}\n')
    check("#8 landed(): this worker's plugin maps its handler -> True", wc.landed() is True)
    wc.t0 += 3600
    check("#8 landed(): a plugin older than this worker does not count", wc.landed() is False)
finally:
    wc.plugin.unlink(missing_ok=True)


class FakeCodify:
    started = []

    def __init__(self, chain, cid):
        self.cid, self.done, self.calls = cid, threading.Event(), 0

    def start(self):
        FakeCodify.started.append(self.cid)
        return self

    def landed(self):
        self.calls += 1
        return self.calls >= 3

    def stop(self, join=5.0):
        self.done.set()


with patched({**QUIET, (orchestrate, "WebCodify"): FakeCodify, (cli, "is_complete"): lambda cid: False}):
    ch = chain(lane="web-exploitation")
    ch._start_codify("web-x")
    ch._start_codify("web-x")
    check("#8 the codify worker starts once per web chain", FakeCodify.started == ["web-x"], FakeCodify.started)
    FakeCodify.started.clear()
    chain(lane="script-analysis")._start_codify("s")
    check("#8 never for a non-web lane", FakeCodify.started == [])
with patched({**QUIET, (orchestrate, "WebCodify"): FakeCodify, (cli, "is_complete"): lambda cid: True}):
    chain(lane="web-exploitation")._start_codify("web-x")
    check("#8 not when the Time Trial and Mastery are already complete", FakeCodify.started == [])

msgs = []
with patched({(orchestrate, "say"): lambda m, *a, **k: msgs.append(m), (orchestrate, "WEB_CODIFY_HOLD"): 5.0}):
    ch = chain(lane="web-exploitation")
    ch._codify = FakeCodify(ch, "web-x")
    ch._codify_hold("web-x/time_trial", poll=0.01)
    check("#8 HCTF_WEB_CODIFY_HOLD: the first TT attempt waits until the plugin lands",
          ch._codify.calls == 3 and "landed" in msgs[-1], (ch._codify.calls, msgs[-1:]))
with patched({**QUIET, (orchestrate, "WEB_CODIFY_HOLD"): 0.0}):
    ch = chain(lane="web-exploitation")
    ch._codify = FakeCodify(ch, "web-x")
    ch._codify_hold("web-x/time_trial", poll=0.01)
    check("#8 default (hold 0): the TT never waits", ch._codify.calls == 0)

# ---------------------------------------------------------------- P2 #11: reuse-race seeds checked on carry-over cases
shape21 = orchestrate.field_shape("d21-apk-001-apk-package-name")
cc = orchestrate.carry_cases("metadata-forensics", 22, {shape21})
check("#11 carry_cases finds the newest earlier GM-verified case for a carry-over shape (D21 apk package name)",
      shape21 in cc and "day21" in str(cc[shape21][0]) and cc[shape21][2], cc)
check("#11 ... and never looks at today or later", orchestrate.carry_cases("metadata-forensics", 21, {shape21}) == {})

with tempfile.TemporaryDirectory() as d:
    case = Path(d) / "auto-mastery-x"
    (case / "artifacts").mkdir(parents=True)
    (case / "contract.json").write_text(json.dumps({"answer_ids": ["set1.d21-apk-001-apk-package-name"]}))
    fake_cases = {shape21: (case, "set1.d21-apk-001-apk-package-name", "com.huntress.arena.p1")}

    def gaps_with(got, err=None):
        with patched({(orchestrate, "carry_cases"): lambda lane, day, shapes: dict(fake_cases),
                      (orchestrate.solvers, "run_solver"): lambda *a, **k: (got, err, 0.1),
                      (cli, "load"): lambda cid, name: ({"answer_ids": ["set1.d21-apk-001-apk-package-name"]}
                                                        if "/" in cid else {"answer_ids": ["today-field"]})}):
            ch = chain(lane="metadata-forensics")
            ch.sdir = ROOT / "challenges" / "day22" / "metadata-x" / "solver"
            return ch._carry_gaps("snap")

    check("#11 a seed that leaves the carry-over field empty on its earlier case -> gap",
          gaps_with({}) == [shape21])
    check("#11 a seed that reproduces it -> covered",
          gaps_with({"set1.d21-apk-001-apk-package-name": "com.huntress.arena.p1"}) == [])
    check("#11 a seed that cannot run that case at all -> inconclusive (no hold)", gaps_with({}, err="boom") == [])

posted, calls = [], {"n": 0}


def _gaps_seq(snap):
    calls["n"] += 1
    return [shape21] if snap == "race-snap" else []


ticks = iter(range(10, 1000))
with patched({(orchestrate, "say"): lambda *a, **k: None, (orchestrate, "SPEC_POLL"): 0.01,
              (orchestrate, "NEWID_STABLE"): 0.0, (orchestrate, "NEWID_HOLD"): 5.0,
              (orchestrate, "carry_cases"): lambda lane, day, shapes: {s: (Path("c"), "a", "v") for s in shapes}}):
    import hctf.inbox as _inbox
    with patched({(_inbox, "post"): lambda cdir, note, key=None: posted.append((key, note))}):
        ch = chain(lane="metadata-forensics")
        ch.sdir = ROOT / "challenges" / "day22" / "metadata-x" / "solver"
        ch._carry_gaps = _gaps_seq
        ch._solver_mtimes = lambda: {"solve.py": float(next(ticks))}
        ch._spec_snapshot = lambda cid: "worker-snap"
        out = ch._carry_hold("x", "race-snap", threading.Event(), threading.Event())
check("#11 race handoff with a carry gap: the worker is told (inbox) and the hold hands over its covering snapshot",
      out == "worker-snap" and posted and posted[0][0] == "carry" and shape21 in posted[0][1], (out, posted[:1]))

# ---------------------------------------------------------------- P0 #1 (prebuild side): stop this copy only, fully
import re as _re  # noqa: E402
import subprocess  # noqa: E402
import time as _t13  # noqa: E402
from hctf import prebuild  # noqa: E402

ss = prebuild._shell_script
check("#1 prebuild chain-shell script found for -c / -lc / -l -c shapes",
      ss(["bash", "-c", "s1"]) == "s1" and ss(["bash", "-lc", "s2"]) == "s2" and ss(["/bin/bash", "-l", "-c", "s3"]) == "s3")
check("#1 ... and not for a script file or a non-shell", ss(["bash", "run.sh"]) is None and ss(["python3", "-c", "x"]) is None)
seg = lambda script: any(prebuild._PREBUILD_SEG.match(s.strip()) for s in _re.split(r"&&|\|\||;", script))  # noqa: E731
check("#1 the post-run/restart chain `cd ROOT && source ...; python -m hctf.cli prebuild` is recognised",
      seg("cd /home/x/huntress-2026 && source bin/env.sh >/dev/null 2>&1; "
          "/home/x/huntress-2026/.venv/bin/python3 -m hctf.cli prebuild --parallel --n 999 >> .run/p.log 2>&1"))
check("#1 the original `prebuild --lane A ; prebuild --lane B` chain still is",
      seg("python3 -m hctf.cli prebuild --lane a ; python3 -m hctf.cli prebuild --lane b"))
check("#1 a --stop / a mere mention never is",
      not seg("timeout 120 python3 -m hctf.cli prebuild --stop") and not seg("python3 -m hctf.cli prebuild --stop")
      and not seg("grep -n 'hctf.cli prebuild' .run/x.log") and not seg("echo python3 -m hctf.cli prebuild"))
p_here = subprocess.Popen(["sleep", "5"], cwd=str(ROOT))
p_alt = subprocess.Popen(["sleep", "5"], cwd="/")   # (not TMPDIR: bin/env.sh puts it inside ROOT/.run/tmp)
try:
    _t13.sleep(0.2)
    check("#1 a process working in this copy is this copy's; one elsewhere is not",
          prebuild._in_root(p_here.pid) and not prebuild._in_root(p_alt.pid))
finally:
    p_here.kill()
    p_alt.kill()
with tempfile.TemporaryDirectory(prefix=ROOT.name + "-alt") as d:   # e.g. /tmp/huntress-2026-rehearsalXXXX
    with patched({(prebuild, "ROOT"): Path(str(Path(d).parent / ROOT.name))}):
        p = subprocess.Popen(["sleep", "5"], cwd=d)
        try:
            _t13.sleep(0.2)
            check("#1 a sibling copy whose path merely STARTS with this root's (…-alt) is not this copy",
                  not prebuild._in_root(p.pid))
        finally:
            p.kill()

# ---------------------------------------------------------------- P2 #13: the runner reuses a fresh pre-start once
import re as _re  # noqa: E402
import shutil  # noqa: E402
import time as _t13  # noqa: E402
from hctf import hb_timed  # noqa: E402

CID13 = "zz-d22test-chal/mastery"
ADIR = hb_timed.HW / ".run" / "tmp-timed" / _re.sub(r"[^A-Za-z0-9]+", "_", CID13)


def prestart(body=None, pj=None, files=("delivery-1.bin",)):
    shutil.rmtree(ADIR, ignore_errors=True)
    ADIR.mkdir(parents=True)
    body = body if body is not None else {"attempt_id": "att-13", "answer_ids": ["set1.x"], "deadline": None}
    (ADIR / "contract.json").write_text(json.dumps(body))
    for f in files:
        (ADIR / f).write_text("bytes")
    pj = pj if pj is not None else {"attempt_id": "att-13", "files": ["delivery-1.bin"], "t": _t13.time()}
    (ADIR / ".prefetch.json").write_text(json.dumps(pj))


try:
    prestart()
    b1, b2 = hb_timed._prestarted_body(CID13), hb_timed._prestarted_body(CID13)
    check("#13 a fresh untimed pre-start is reused instead of a second `start`", (b1 or {}).get("attempt_id") == "att-13")
    check("#13 ... exactly once (a later `start`, e.g. after a pass, asks the GM again)", b2 is None)
    prestart(body={"attempt_id": "att-13", "answer_ids": ["x"], "deadline": "2026-10-23T00:00:06Z"})
    check("#13 a clocked pre-start is never reused", hb_timed._prestarted_body(CID13) is None)
    prestart(pj={"attempt_id": "att-13", "files": ["delivery-1.bin"], "t": _t13.time() - 3600})
    check("#13 a stale pre-start (> HCTF_PRESTART_TRUST_S) is not reused", hb_timed._prestarted_body(CID13) is None)
    prestart(files=())
    check("#13 a pre-start whose bytes are missing is not reused", hb_timed._prestarted_body(CID13) is None)
    prestart(pj={"attempt_id": "att-OTHER", "files": ["delivery-1.bin"], "t": _t13.time()})
    check("#13 an attempt-id mismatch is not reused", hb_timed._prestarted_body(CID13) is None)
    prestart()
    os.environ["HCTF_PRESTART_REUSE"] = "0"
    check("#13 HCTF_PRESTART_REUSE=0 disables it", hb_timed._prestarted_body(CID13) is None)
    del os.environ["HCTF_PRESTART_REUSE"]
finally:
    shutil.rmtree(ADIR, ignore_errors=True)

if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D22 post-mortem checks passed")
