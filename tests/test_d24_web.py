"""D24 web track (plan items 8-11), offline: fakes only, no GM, no live targets, no workers.
- #8  every lib/web/handlers/*.py plugin compiles, imports, and maps each KEY_MAP name to a callable handler
- #9  class_known counts concept keys only; known/unknown race budgets 20/12 s; run_solver(deadline=); the web reuse race
      is ONE lane-solver run (14 s deadline) that still races prior answer() + every plugin; answer-first never waits on web
- #10 a web single on a fresh drop (no local trace + this run's list entry says solved: false) skips gm_solved; a
      solved / unknown entry or local state still asks it (a solved live-web single is still ACCEPTED); polls 2 s

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


if __name__ == "__main__":
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
    sys.exit(1 if failures else 0)
