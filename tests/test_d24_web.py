"""D24 web track (plan items 8-11), offline: fakes only, no GM, no live targets, no workers.
- #8  every lib/web/handlers/*.py plugin compiles, imports, and maps each KEY_MAP name to a callable handler
- #9  class_known counts concept keys only; known/unknown race budgets 20/12 s; run_solver(deadline=); the web reuse race
      is ONE lane-solver run (14 s deadline) that still races prior answer() + every plugin; answer-first never waits on web
- #10 a web single on a fresh drop (no local trace + this run's list entry says solved: false) skips gm_solved; a
      solved / unknown entry or local state still asks it (a solved live-web single is still ACCEPTED); polls 2 s
- #11 parallel web TT live answer bound to the runner's attempt; runner pass ends it, its pass maps to correct (no
      _gm_passed); a block while codify runs waits for the live answer / plugin (reconnect with start, never retry)
      before any generalize; codify is ended before a generalize takes its plugin file; no bg generalize beside codify

Run:  source bin/env.sh && python3 tests/test_d24_web.py      (exit 0 = all pass)
"""
import contextlib
import importlib
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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


# ---------------------------------------------------------------- #8: every web plugin compiles + imports + maps
HDIR = ROOT / "lib" / "web" / "handlers"
plugins = sorted(p for p in HDIR.glob("*.py") if not p.name.startswith("_"))
check("#8 the D23 + D24 web plugins are present",
      {"day23_web_ask_again_later", "day23_web_posted_too_much", "day23_web_template_temper",
       "day24_web_fetch_quest", "day24_web_the_api_has_opinions"} <= {p.stem for p in plugins},
      [p.stem for p in plugins])
for p in [HDIR / "__init__.py"] + plugins:
    try:
        py_compile.compile(str(p), doraise=True)
        ok, err = True, ""
    except py_compile.PyCompileError as e:
        ok, err = False, str(e)[:300]
    check(f"#8 compiles: {p.name}", ok, err)
from lib.web import handlers as webhandlers  # noqa: E402
for p in plugins:
    try:
        mod = importlib.import_module(f"lib.web.handlers.{p.stem}")
        err = ""
    except Exception as e:  # noqa: BLE001
        mod, err = None, repr(e)[:300]
    check(f"#8 imports: {p.name}", mod is not None, err)
    if mod is None:
        continue
    km, hs = list(getattr(mod, "KEY_MAP", None) or []), dict(getattr(mod, "HANDLERS", None) or {})
    check(f"#8 {p.stem}: KEY_MAP + HANDLERS present", bool(km) and bool(hs), (km, list(hs)))
    for pat, name in km:
        try:
            re.compile(pat)
            rx = True
        except re.error:
            rx = False
        check(f"#8 {p.stem}: {pat!r} -> {name} (valid regex, callable handler, loaded by the dispatcher)",
              rx and callable(hs.get(name)) and webhandlers._HANDLERS.get(name) is hs.get(name)
              and (pat, name) in webhandlers._KEY_MAP, (rx, name in hs, name in webhandlers._HANDLERS))
import lib.web as libweb  # noqa: E402
check("#8 the generic web solver (lane seed entry) imports with every plugin loaded",
      callable(getattr(libweb, "solve_target", None)) and callable(getattr(libweb, "main", None)))


# ---------------------------------------------------------------- #9: class detection, budgets, web race, answer-first
import json  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402

from lib import websolve  # noqa: E402
from hctf import orchestrate, solvers  # noqa: E402

FURN = {"framework": "Express", "feature_route": "/fetch", "secondary_route": "/internal", "current_role": "guest"}
TEMPLATE = {"framework": "Flask", "current_role": "guest", "feature_route": "/render"}
API = {"framework": "x", "feature_route": "/api/notes", "inventory_route": "/api/inv", "current_role": "user",
       "protected_reference": 7}
CSRF = {"browser_session": "s", "current_user": "bob", "feature_route": "/f", "framework": "x", "preferences_route": "/p"}
names = lambda pairs: [n for n, _f in pairs]  # noqa: E731
fk = names(webhandlers.for_key(websolve.dispatch_key(FURN), FURN))
check("#9 dispatch unchanged: an all-furniture kit still races the D23/D24 plugins that key on furniture",
      {"day23_web_ask_again_later", "day24_web_fetch_quest"} <= set(fk), fk)
check("#9 concept_handlers: an all-furniture kit (D23 / D24 fetch-quest shape) names NO handler",
      webhandlers.concept_handlers(websolve.dispatch_key(FURN), FURN) == []
      and webhandlers.concept_handlers(None, TEMPLATE) == [])
check("#9 concept_handlers: concept keys still name their handler (D24 API inventory, D22 csrf)",
      names(webhandlers.concept_handlers("inventory_route", API)) == ["day24_web_the_api_has_opinions"]
      and "csrf" in names(webhandlers.concept_handlers("current_user", CSRF)),
      (webhandlers.concept_handlers("inventory_route", API), webhandlers.concept_handlers("current_user", CSRF)))
with patched({(libweb, "_prior_sources"): lambda: []}):
    check("#9 class_known: a furniture-only match is NOT a known class (the D24 furniture bug)",
          libweb.class_known(FURN, None) is False and libweb.class_known(TEMPLATE, None) is False)
    check("#9 class_known: a concept-key handler match is known", libweb.class_known(API, "inventory_route") is True)
    with patched({(libweb, "CONCEPT_KNOWN"): False}):
        check("#9 kill switch HCTF_WEB_CONCEPT_KNOWN=0: any for_key match counts again (old behaviour)",
              libweb.class_known(FURN, None) is True)
with patched({(libweb, "_prior_sources"): lambda: ["if 'callback_nonce' in clues: ..."]}):
    check("#9 class_known: an earlier web solver naming a concept key is still known (prior-day reuse)",
          libweb.class_known(dict(FURN, callback_nonce="n"), "callback_nonce") is True)

budgets = []
os.environ["HCTF_WEB_RACE_LOG"] = str(Path(tempfile.mkdtemp()) / "race.jsonl")
RACE = {(websolve, "base_of"): lambda q, c: "https://t.example/",
        (websolve, "fetch"): lambda *a, **k: (200, "", []),
        (libweb, "candidates"): lambda *a, **k: [],
        (websolve, "race"): lambda probes, budget=40, report=None: (budgets.append(budget),
                                                                    report.update(winner=None, elapsed=0.1), None)[2]}
with patched({**RACE, (libweb, "class_known"): lambda c, k: True}):
    libweb.solve_target({"id": "proof-1"}, {}, clues=API)
    libweb.solve_target({"id": "proof-1"}, {}, budget=33, clues=API)
with patched({**RACE, (libweb, "class_known"): lambda c, k: False}):
    libweb.solve_target({"id": "proof-1"}, {}, clues=FURN)
    libweb.solve_target({"id": "proof-1"}, {}, budget=8, clues=FURN)
check("#9 budget=None: known class -> HCTF_WEB_KNOWN_BUDGET 20 s, unknown -> 12 s; an explicit budget is kept "
      "(capped at 12 s for an unknown class)", budgets == [20.0, 33, 12.0, 8] and libweb.KNOWN_BUDGET == 20, budgets)
del os.environ["HCTF_WEB_RACE_LOG"]

# prior-day reuse is kept: the lane solver's race = built-in/plugin handlers + `default` + every prior answer()
fake_prior = types.SimpleNamespace(answer=lambda *a: "proof_0123456789abcdef")
with patched({(libweb, "_prior_web_solvers"): lambda: [("day21/web-reflect-upon-this", fake_prior)]}):
    cn = names(libweb.candidates("https://t.example/", FURN, None, {"id": "proof-1"}, {"targets": []}))
check("#9 the lane solver still races every furniture-keyed plugin, `default` and each prior day's answer()",
      {"day23_web_ask_again_later", "day24_web_fetch_quest", "default", "prior:day21/web-reflect-upon-this"} <= set(cn),
      cn)

# run_solver(deadline=) -> HCTF_SOLVE_DEADLINE (epoch) in the solver's env; none without it
sd = Path(tempfile.mkdtemp()) / "solver"
sd.mkdir()
(sd / "solve.py").write_text("import json, os\nprint(json.dumps({'d': os.environ.get('HCTF_SOLVE_DEADLINE', '')}))\n")
os.environ.pop("HCTF_SOLVE_DEADLINE", None)
t0 = time.time()
got, err, _dt = solvers.run_solver(sd, {"answer_ids": ["d"]}, sd, timeout=30, deadline=14)
check("#9 run_solver(deadline=14) sets HCTF_SOLVE_DEADLINE ~ now + 14 s",
      not err and got.get("d") and abs(float(got["d"]) - (t0 + 14)) < 3, (got, err))
got, err, _dt = solvers.run_solver(sd, {"answer_ids": ["d"]}, sd, timeout=30)
check("#9 run_solver without deadline leaves HCTF_SOLVE_DEADLINE unset", not err and got.get("d") == "", (got, err))

calls = []
with patched({(solvers, "run_solver"): lambda sdir, c, a, timeout=120, background=None, deadline=None: (
        calls.append((Path(sdir).name, timeout, deadline)), ({"proof-1": "proof_abcdef0123456789"}, None, 3.2))[1]}):
    plan = solvers.lane_race_plan(sd, {"answer_ids": ["proof-1", "proof-2"]}, sd, 14)
check("#9 lane_race_plan: one run, deadline 14 s, kill at deadline + 4 s", calls == [("solver", 18.0, 14)], calls)
check("#9 lane_race_plan: a reuse_plan-shaped result, its proofs confident, the lane solver the seed",
      plan["high"] == {"proof-1": "proof_abcdef0123456789"} and plan["spec"] == {} and plan["best"] == sd
      and plan["runs"][sd][0] == 1 and plan["alts"] == {"proof-1": ["proof_abcdef0123456789"]}, plan)


class _Stop(Exception):
    pass


def race_chain(lane):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base, ch.sdir = lane, "x", ROOT / ".run" / "nonexistent-solver"
    return ch


seen, says = [], []
RACE_ENV = {(orchestrate, "say"): lambda m, *a, **k: says.append(m),
            (orchestrate.cli, "load"): lambda cid, name: {"answer_ids": ["proof-1"]},
            (orchestrate.timed, "latest_artifacts"): lambda cid: sd,
            (orchestrate.cli, "is_complete"): lambda cid: False,
            (orchestrate, "RETRIEVAL"): False,
            (orchestrate.solvers, "lane_race_plan"): lambda sdir, c, a, dl: (seen.append(("lane", Path(sdir), dl)),
                                                                            (_ for _ in ()).throw(_Stop()))[1],
            (orchestrate.solvers, "reuse_plan"): lambda *a, **k: (seen.append(("reuse", k.get("limit"))),
                                                                 (_ for _ in ()).throw(_Stop()))[1]}
with patched(RACE_ENV):
    orchestrate.Chain._reuse_race(race_chain("web"), "web-x")
    web_call = list(seen)
    seen.clear()
    orchestrate.Chain._reuse_race(race_chain("script-analysis"), "s-x")
    other_call = list(seen)
    seen.clear()
    with patched({(orchestrate, "WEB_RACE_LANE"): False}):
        orchestrate.Chain._reuse_race(race_chain("web"), "web-x")
    off_call = list(seen)
check("#9 web reuse race = ONE challenges/_lane/web/solver run with a 14 s deadline",
      web_call == [("lane", orchestrate.paths.LANE_SOLVERS / "web" / "solver", 14.0)], web_call)
check("#9 other lanes keep the newest-N reuse_plan race", other_call == [("reuse", orchestrate.REUSE_RACE_SOLVERS)],
      other_call)
check("#9 kill switch HCTF_WEB_RACE_LANE=0: web runs the old newest-N race", off_call == [("reuse", 3)], off_call)


def af_wait(lane, race_wait):
    af = orchestrate.AnswerFirst.__new__(orchestrate.AnswerFirst)
    af.chain, af.cid, af.ids = types.SimpleNamespace(lane=lane), "x", ["proof-1"]
    af.stop_evt, af.done, af.started = threading.Event(), threading.Event(), threading.Event()
    af.stop_evt.set()       # past the wait: "already complete" -> returns without a worker
    t0 = time.time()
    with patched({(orchestrate, "say"): lambda *a, **k: None, (orchestrate, "ANSWER_FIRST_RACE_WAIT"): race_wait}):
        af._run(threading.Event())    # the race never finishes
    return time.time() - t0


check("#9 answer-first on web does not wait for the reuse race (HCTF_ANSWER_FIRST_RACE_WAIT_WEB=0)",
      orchestrate.ANSWER_FIRST_RACE_WAIT_WEB == 0 and af_wait("web", 1.0) < 0.5)
check("#9 answer-first on other lanes still waits for the race (bounded)", af_wait("metadata-forensics", 0.6) >= 0.55)
with patched({(orchestrate, "ANSWER_FIRST_RACE_WAIT_WEB"): 0.6}):
    check("#9 HCTF_ANSWER_FIRST_RACE_WAIT_WEB > 0 restores a web wait", af_wait("web", 1.0) >= 0.55)


# ---------------------------------------------------------------- #10: web start -- fresh-drop gm_solved skip, 2 s polls
from hctf import webtarget  # noqa: E402

check("#10 fresh drop = the list entry says solved: false explicitly",
      orchestrate._web_fresh_drop({"id": "w", "solved": False}) is True
      and orchestrate._web_fresh_drop({"id": "w", "solved": True}) is False
      and orchestrate._web_fresh_drop({"id": "w"}) is False and orchestrate._web_fresh_drop(None) is False)
with patched({(orchestrate, "WEB_FRESH_SKIP_SOLVED"): False}):
    check("#10 kill switch HCTF_WEB_FRESH_SKIP_SOLVED=0: never fresh", not orchestrate._web_fresh_drop({"solved": False}))


def single_gate(lane, entry, trace=False, gm=False):
    """Drive Chain._single up to its first post-gate step -> (gm_solved calls, returned / 'continued')."""
    d = Path(tempfile.mkdtemp())
    if trace:
        (d / "start.json").write_text("{}")
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base, ch.sdir = lane, "x", d / "solver"
    ch.entries = {"single_solve": dict(entry, id="web-x")}
    ch._start_family_calibration = lambda: None
    asked = []

    def stop(*a, **k):
        raise _Stop()
    with patched({(orchestrate, "say"): lambda *a, **k: None, (orchestrate.cli, "cdir"): lambda cid: d,
                  (orchestrate.cli, "is_complete"): lambda cid: False,
                  (orchestrate.cli, "gm_solved"): lambda cid: (asked.append(cid), gm)[1],
                  (orchestrate, "set_state"): stop}):
        try:
            out = orchestrate.Chain._single(ch)
        except _Stop:
            out = "continued"
    return asked, out


check("#10 web fresh drop: no gm_solved round trip, the single starts at once",
      single_gate("web", {"solved": False}) == ([], "continued"), single_gate("web", {"solved": False}))
check("#10 web, list entry without `solved`: gm_solved still asked (old behaviour)",
      single_gate("web", {}) == (["web-x"], "continued"))
check("#10 web resume/replay of a SOLVED single (list solved: true, no local state): asked AND accepted -> timed modes",
      single_gate("web", {"solved": True}, gm=True) == (["web-x"], True))
check("#10 web with local state (resume after a crash): gm_solved asked even if the stale entry said unsolved",
      single_gate("web", {"solved": False}, trace=True, gm=True) == (["web-x"], True))
check("#10 regular lane fresh drop: unchanged (no local trace -> no gm_solved)",
      single_gate("warmups", {"solved": False}) == ([], "continued"))
check("#10 prepare / ready polls default to 2 s (were 4 / 5)",
      webtarget.POLL == 2 and orchestrate.WEB_READY_POLL == 2, (webtarget.POLL, orchestrate.WEB_READY_POLL))


# ---------------------------------------------------------------- #11: parallel web TT live answer, codify as generalize
from hctf import cli, timed, workers  # noqa: E402

TD = Path(tempfile.mkdtemp())
TT = "web-exploitation-day-25-x/time_trial"
CONTRACT = {"attempt_id": "att-1", "answer_ids": ["proof-1"], "targets": [{"id": "Target 1", "url": "https://t/"}],
            "questions": [{"id": "proof-1", "artifact": "Target 1"}]}
LAST = {"result": "solver_incomplete", "attempt_id": "att-1", "no_clock": True, "deadline": None,
        "missing": ["proof-1"]}


class FakeLive:
    def __init__(self, attempt, pass_after=None):
        self.attempt, self.done = attempt, threading.Event()
        self.passed = self.all_accepted = False
        self.t0, self.pass_after, self.finished = time.time(), pass_after, 0

    def _state(self):
        ok = self.pass_after is not None and time.time() - self.t0 >= self.pass_after
        return ok, ok

    def finish(self, wait=5.0):
        self.finished += 1
        self.done.set()
        self.passed, self.all_accepted = self._state()
        return self

    def link(self, evt):
        pass


class FakeCodify:
    """The codify worker: writes its plugin `land_after` s after the TT blocks (armed by the first run), or ends
    without one after `ends_after` s."""

    def __init__(self, land_after=None, ends_after=None):
        self.plugin, self.t0 = TD / "day25_web_x.py", time.time() - 5
        self.done, self.stopped = threading.Event(), 0
        self.land_after, self.ends_after = land_after, ends_after
        self.plugin.unlink(missing_ok=True)

    def arm(self):
        if self.land_after is not None:
            threading.Timer(self.land_after, lambda: self.plugin.write_text("KEY_MAP = []\n")).start()
        if self.ends_after is not None:
            threading.Timer(self.ends_after, self.done.set).start()

    def landed(self, timeout=15):
        return self.plugin.exists() and self.plugin.stat().st_mtime >= self.t0

    def stop(self, join=5.0):
        self.stopped += 1
        self.done.set()


class _Gov:
    @staticmethod
    def allow_timed():
        return True


PROG = {}
GM_CALLS = []


def web_chain(codify=None, live_pass_after=None):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base = "web", "web-exploitation-day-25-x"
    ch.entries = {"time_trial": {"id": TT}, "mastery": {"id": TT.replace("time_trial", "mastery")}}
    ch.sdir, ch.root = TD / "nosolver", TD
    ch._pre_attempt_done, ch._tstatus, ch.gov = True, {"time_trial": "start_required"}, _Gov()
    ch._codify = codify
    ch._codify_hold = lambda cid: None
    ch._ahead_new = lambda mode: 0
    ch._slow_vm_no_clock = lambda cid: False
    ch._early_join = lambda cid: False
    ch._early_kw = lambda cid, untimed: {}
    ch._bg_gen_take = lambda cid, why, only_won=False: False
    ch._late_probes = lambda cid, wait=False, defer_compound=False: {}
    ch._prefetch_mastery_start = lambda: ch.calls["prefetch"].append(1)
    # D25 D3: a web TT pass requests the Mastery target at once (_tt_pass_kick) -- stubbed: never a GM call in a test
    ch._web_mastery_kick = lambda: ch.calls["kick"].append(1)
    ch.calls = {"run": [], "gen": [], "lives": [], "gm_passed": [], "prefetch": [], "kick": []}

    def gen(cid, **kw):
        ch.calls["gen"].append(kw.get("live"))
        if kw.get("live") is not None:
            kw["live"].pass_after = 0       # the generalize's linked live answer passes meanwhile
    ch.generalize = gen

    def start_live(cid, last, fields, wrong, fixed):
        lv = FakeLive(last.get("attempt_id"), live_pass_after)
        ch.calls["lives"].append((last.get("attempt_id"), list(fields), lv))
        return lv
    ch._start_live = start_live
    ch._gm_passed = lambda cid: (ch.calls["gm_passed"].append(cid), False)[1]
    return ch


def runner(ch, results, bind=True, hold=1.0):
    """Fake timed.run: like hb_timed, write the attempt's progress + contract at attempt start, then 'solve' for `hold` s."""
    seq = iter(results)

    def run(cid, sdir, log=None, **kw):
        ch.calls["run"].append(kw.get("op", "start"))
        if len(ch.calls["run"]) == 1 and hasattr(ch._codify, "arm"):
            ch._codify.arm()
        if bind:
            (TD / "tdir").mkdir(exist_ok=True)
            (TD / "tdir" / "contract.json").write_text(json.dumps(CONTRACT))
            PROG.clear()
            PROG.update(attempt_id="att-1", no_clock=True, deadline=None)
        time.sleep(hold)
        return next(seq)
    return run


def drive(ch, results, bind=True, hold=1.0, extra=None):
    PROG.clear()
    env = {(orchestrate, "say"): lambda *a, **k: None, (orchestrate, "set_state"): lambda *a, **k: None,
           (orchestrate, "AUTO_EARLY"): False, (orchestrate, "LIVE_ANSWER"): True,
           (orchestrate, "label_only_failure"): lambda w: False, (orchestrate, "_code_sig"): lambda d: {},
           (orchestrate, "capture_variant"): lambda *a: None, (orchestrate, "record_timed_case"): lambda *a: None,
           (orchestrate, "WEB_GEN_WAIT_POLL"): 0.05,
           (cli, "is_complete"): lambda cid: False, (cli, "gm_solved"): lambda cid: False,
           (cli, "save"): lambda *a, **k: None,
           (cli, "call"): lambda *a, **k: (GM_CALLS.append(a), {"http": 0, "body": {}})[1],   # never the real GM
           (timed, "run"): runner(ch, results, bind, hold), (timed, "last_result"): lambda cid: dict(LAST),
           (timed, "timed_dir"): lambda cid: TD / "tdir", (timed, "ensure_started"): lambda cid: (None, None),
           (timed, "resolve_format_alternates"): lambda *a, **k: set(),
           (timed, "resolve_labels_online"): lambda *a, **k: set(),
           (workers, "runner_progress"): lambda cid, since=0.0: dict(PROG)}
    env.update(extra or {})
    with patched(env):
        return orchestrate.Chain.timed_stage(ch, "time_trial")


# runner passes: the live answer bound at attempt start is ended, nothing else runs
ch = web_chain(codify=FakeCodify())
ok = drive(ch, ["correct"])
lv = ch.calls["lives"][0][2] if ch.calls["lives"] else None
check("#11 first web TT attempt: a live answer is bound to the runner's attempt + contract at attempt start",
      [(a, f) for a, f, _l in ch.calls["lives"]] == [("att-1", ["proof-1"])], ch.calls["lives"])
check("#11 the runner passing ends the parallel live answer; no generalize, no _gm_passed",
      ok is True and lv is not None and lv.finished >= 1 and not ch.calls["gen"] and not ch.calls["gm_passed"],
      (ok, ch.calls))

check("#11 (D25 D3) the TT pass requests the web Mastery target", ch.calls["kick"], ch.calls)

# the live answer passes while the runner blocks: correct at once, no generalize, no extra GM round trip
ch = web_chain(codify=FakeCodify(), live_pass_after=0.2)
ok = drive(ch, ["blocked"])
check("#11 the parallel live answer's pass maps the blocked runner to correct (one run, no generalize, no _gm_passed)",
      ok is True and ch.calls["run"] == ["start"] and not ch.calls["gen"] and not ch.calls["gm_passed"]
      and len(ch.calls["lives"]) == 1, ch.calls)

# a block while codify runs: wait for the plugin -> reconnect with START (never retry); the same live answer is kept
ch = web_chain(codify=FakeCodify(land_after=0.3))
ok = drive(ch, ["blocked", "correct"])
check("#11 codify plugin lands during the wait: reconnect with op=start (never retry), no generalize",
      ok is True and ch.calls["run"] == ["start", "start"] and "retry" not in ch.calls["run"] and not ch.calls["gen"],
      ch.calls)
check("#11 ... ONE live answer for the whole attempt (kept across the reconnect, ended by the runner's pass)",
      len(ch.calls["lives"]) == 1 and ch.calls["lives"][0][2].finished >= 1, ch.calls["lives"])

# the wait runs out: codify is ended BEFORE the generalize (one writer per plugin file); the generalize gets the
# parallel live answer (no second live worker)
cod = FakeCodify()
ch = web_chain(codify=cod)
t0 = time.time()
ok = drive(ch, ["blocked"], extra={(orchestrate, "WEB_CODIFY_GEN_WAIT"): 0.5})
check("#11 no live pass / plugin within HCTF_WEB_CODIFY_GEN_WAIT: codify ended, then ONE generalize",
      cod.stopped == 1 and len(ch.calls["gen"]) == 1, (cod.stopped, ch.calls))
check("#11 ... the generalize races the SAME live answer (no second live worker)",
      len(ch.calls["lives"]) == 1 and ch.calls["gen"][0] is ch.calls["lives"][0][2] and ok is True, ch.calls)
check("#11 ... and the wait was bounded", time.time() - t0 < 10, time.time() - t0)

# codify ends without a plugin during the wait: straight to the generalize
cod = FakeCodify(ends_after=0.2)
ch = web_chain(codify=cod)
ok = drive(ch, ["blocked"])
check("#11 codify ended without a plugin: the wait stops early and ONE generalize runs",
      len(ch.calls["gen"]) == 1 and cod.stopped == 0, (cod.stopped, ch.calls))

# a landed plugin before the first attempt: no parallel live answer (the solver dispatches to it)
cod = FakeCodify()
cod.plugin.write_text("KEY_MAP = []\n")
ch = web_chain(codify=cod)
ok = drive(ch, ["correct"])
check("#11 codify plugin already landed: no parallel live answer", ok is True and not ch.calls["lives"], ch.calls)
cod.plugin.unlink()

# a clocked attempt never gets a parallel live answer
ch = web_chain(codify=FakeCodify())
with patched({(workers, "runner_progress"): lambda cid, since=0.0: dict(PROG, deadline="2026-10-25T13:00:06Z")}):
    pl = orchestrate.WebParLive(ch, TT, time.time() - 1)
    PROG.update(attempt_id="att-1")
    (TD / "tdir").mkdir(exist_ok=True)
    (TD / "tdir" / "contract.json").write_text(json.dumps(CONTRACT))
    with patched({(orchestrate, "say"): lambda *a, **k: None, (timed, "timed_dir"): lambda cid: TD / "tdir"}):
        pl.start()
        time.sleep(0.8)
        check("#11 a clocked runner attempt is never bound", pl.close() is None and not ch.calls["lives"])
PROG.clear()

# kill switches: HCTF_WEB_PAR_LIVE=0 -> no live answer at attempt start; HCTF_WEB_CODIFY_IS_GEN=0 -> no codify wait
cod = FakeCodify(land_after=0.1)
ch = web_chain(codify=cod)
ok = drive(ch, ["blocked"], extra={(orchestrate, "WEB_PAR_LIVE"): False, (orchestrate, "WEB_CODIFY_IS_GEN"): False})
check("#11 both flags off: today's blocked path (one run, live answer started at the block, generalize, codify kept)",
      ch.calls["run"] == ["start"] and len(ch.calls["lives"]) == 1 and len(ch.calls["gen"]) == 1 and cod.stopped == 0,
      (cod.stopped, ch.calls))

# no background generalize while codify still writes the plugin (it would edit the same file)
ch = web_chain(codify=FakeCodify())
says = []
with patched({(orchestrate, "say"): lambda m, *a, **k: says.append(m), (orchestrate, "LIVE_BG_GEN"): True}):
    orchestrate.Chain._start_bg_gen(ch, TT, dict(LAST))
check("#11 a live pass starts no background generalize while codify is alive",
      any("codify worker is still writing" in m for m in says), says)

time.sleep(0.3)   # any background kick thread
check("#11 the timed-stage drives never reached the real GM (cli.call stubbed and unused)", not GM_CALLS, GM_CALLS)


if __name__ == "__main__":
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
    sys.exit(1 if failures else 0)
