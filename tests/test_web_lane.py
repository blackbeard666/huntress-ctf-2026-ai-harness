"""Web lane = live targets (D19 lessons; offline: fake GM, no network, temp challenges dir).
- webtarget.await_target: preparing -> active polling; cleaned -> arena revive; bounded wait
- hb_timed: a `preparing` start is awaited (never retry / no_answer_ids), a dead `cleaned` one revived via the arena; a
  target that never comes up = a start refusal (error:start), never the solver's fault
- timed.ensure_started (single): waits for the target, saves start.json with targets + an empty artifacts dir
- single gate: a GM-CORRECT live-target single is accepted without a replayable case
- test_solver: a FINISHED live-target case is skipped (target 410), the live attempt's own case still replays
- release detection: web in _lanes_for / _expected_modes from Day 19 on, lane-list race union includes it
- one live web target per team: webtarget.slot + Chain._web_slot serialize two web chains; TT pre-start, drift
  watcher and scout never start a web attempt; register keeps a known id's folder; unlisted web ids are found

Run:  source bin/env.sh && python3 tests/test_web_lane.py      (exit 0 = all pass)
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path
from types import SimpleNamespace

os.environ["HCTF_WEB_PREPARE_POLL"] = "0.01"
os.environ["HCTF_WEB_REVIVE_EVERY"] = "0"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
import hb_timed  # noqa: E402
from hctf import cli, driftwatch, orchestrate, paths, remote, solvers, timed, webtarget  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


CID = "web-exploitation-day-20-test"
TARGETS = [{"id": "Target 1", "url": "https://abc.2026.huntress.ctf.games/"}]
QS = [{"id": "proof-1", "artifact": "Target 1", "question": "proof?"}]


def preparing():
    return {"result": "preparing", "name": "t", "questions": QS}


def active(att="att-1"):
    return {"result": "active", "attempt_id": att, "answer_ids": ["proof-1"], "questions": QS, "targets": TARGETS,
            "routes": ["/"], "deadline": None}


def cleaned(att="att-1"):
    return {"result": "cleaned", "attempt_id": att, "answer_ids": ["proof-1"], "questions": QS, "routes": [],
            "deadline": None}


def seq(*bodies):
    it = iter(bodies)
    last = [bodies[-1]]

    def f(_cid):
        try:
            last[0] = next(it)
        except StopIteration:
            pass
        return last[0]
    return f


quiet = lambda m: None  # noqa: E731

# ------------------------------------------------------------------ 1. await_target
b = webtarget.await_target(CID, preparing(), seq(preparing(), preparing(), active()), revive=None, log=quiet,
                           poll=0, wait=5)
check("1 preparing -> active: waits for the target", webtarget.ready(b) and b["attempt_id"] == "att-1", b)
revived = []
b = webtarget.await_target(CID, cleaned(), seq(cleaned(), preparing(), active("att-2")),
                           revive=lambda c: revived.append(c) or preparing(), log=quiet, poll=0, wait=5)
check("1 cleaned -> arena revive -> active", revived and set(revived) == {CID} and webtarget.ready(b), (revived, b))
b = webtarget.await_target(CID, preparing(), seq(preparing()), log=quiet, poll=0, wait=0.05)
check("1 bounded: still preparing -> _web_wait timeout", b.get("_web_wait") == "timeout" and not webtarget.ready(b), b)
check("1 non-web bodies pass through", webtarget.await_target(CID, {"answer_ids": ["x"], "attempt_id": "a"},
                                                              seq({}), log=quiet) == {"answer_ids": ["x"], "attempt_id": "a"})
check("1 CORRECT is terminal", not webtarget.needs_wait({"result": "CORRECT", "routes": []}))

# ------------------------------------------------------------------ 2. hb_timed
_orig = {k: getattr(hb_timed, k) for k in ("_pool", "_post_start", "_run_solver", "_post", "_status_body", "_arena_start")}


def attempt(start_body, statuses, arena=None):
    sent, solved, arena_calls = [], [], []

    def start(payload, tries=3):
        sent.append(payload.get("op"))
        return dict(start_body)

    def run_solver(solve, contract, adir, budget, env):
        solved.append(json.loads(Path(contract).read_text()).get("targets"))
        return SimpleNamespace(stdout=json.dumps({"proof-1": "proof_abc123"}), stderr="", returncode=0)
    hb_timed._pool = lambda: object()
    hb_timed._post_start = start
    hb_timed._run_solver = run_solver
    hb_timed._post = lambda payload, timeout=None: {"result": "correct", "remaining": 0}
    hb_timed._status_body = seq(*statuses)
    hb_timed._arena_start = lambda c: arena_calls.append(c) or (arena or preparing())
    out = hb_timed.run_attempt(CID + "/time_trial", "challenges/none/solver", op="start")
    return out, sent, solved, arena_calls


try:
    out, sent, solved, ar = attempt(preparing(), [preparing(), active()])
    check("2 hb_timed: preparing start awaited, then solved on the live target (no retry)",
          out["result"] == "correct" and sent == ["start"] and solved == [TARGETS] and not ar, (out, sent, solved))
    out, sent, solved, ar = attempt(cleaned(), [cleaned(), cleaned(), active("att-9")])
    check("2 hb_timed: a dead `cleaned` attempt is revived via the arena (never solved without a target)",
          out["result"] == "correct" and ar and solved == [TARGETS] and out.get("attempt_id") == "att-9", (out, ar, solved))
    os.environ["HCTF_WEB_PREPARE_WAIT"] = "0.05"
    out, sent, solved, ar = attempt(preparing(), [preparing()])
    os.environ.pop("HCTF_WEB_PREPARE_WAIT")
    check("2 hb_timed: target never up -> web_target_preparing, start_refused, solver never ran, no retry",
          out["result"] == "web_target_preparing" and out.get("start_refused") and not solved and sent == ["start"],
          (out, sent))
    refused = dict(out)
finally:
    for k, v in _orig.items():
        setattr(hb_timed, k, v)

# ------------------------------------------------------------------ temp challenges tree for the rest
tmp = Path(tempfile.mkdtemp(prefix="hctf-web-"))
_paths = (paths.CHALLENGES, paths.INDEX, paths.LOCKS)
paths.CHALLENGES, paths.INDEX, paths.LOCKS = tmp / "challenges", tmp / "challenges" / "index.json", tmp / "locks"
paths.CHALLENGES.mkdir(parents=True)
paths.LOCKS.mkdir(parents=True)
_saved = {"call": cli.call, "gm_status": webtarget.gm_status, "arena_start": webtarget.arena_start, "gm": remote.gm,
          "is_complete": cli.is_complete, "gm_solved": cli.gm_solved, "after_stage": webtarget.after_stage,
          "set_state": orchestrate.set_state, "released": orchestrate.released_challenges}
try:
    paths.register([{"id": CID, "lane": "web", "day": 20, "name": "Test"},
                    {"id": "web-exploitation-day-01-backup-exposure", "lane": "web", "day": 1, "name": "Back Up"}])
    idx = paths.register([{"id": "web-exploitation-day-01-backup-exposure", "lane": "web", "day": 19, "name": "Back Up"}])
    e = idx["web-exploitation-day-01-backup-exposure"]
    check("3 register: a known id keeps its folder, the recorded day follows the GM relabel",
          e["dir"].startswith("day01/") and e["day"] == 19, e)

    # -------------------------------------------------------------- 4. ensure_started (single)
    calls = []

    def fake_call(cid, op, *args, timeout=180):
        calls.append(op)
        return {"http": 200, "body": preparing()}
    cli.call = fake_call
    webtarget.gm_status = seq(preparing(), active("att-s"))
    body, err = timed.ensure_started(CID, log=quiet)
    st = cli.load(CID, "start.json") or {}
    art = timed.latest_artifacts(CID)
    check("4 ensure_started: waits out `preparing`, saves start.json WITH targets", body and st.get("targets") == TARGETS
          and st.get("attempt_id") == "att-s", (body, err, st))
    check("4 ... an empty artifacts/latest for the attempt (no `artifact` call: it is a 400 on web)",
          art is not None and json.loads((art / "manifest.json").read_text())["attempt"] == "att-s"
          and "artifact" not in calls, (art, calls))
    cli.call = _saved["call"]

    # -------------------------------------------------------------- 5. single gate + case skipping
    sdir = paths.solver_dir(CID)
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / "solve.py").write_text("import sys\nsys.exit(3)\n")      # would fail any replay
    (paths.challenge_root(CID) / "meta.json").write_text(json.dumps({"base": CID, "lane": "web", "ids": {
        "single_solve": CID, "time_trial": CID + "/time_trial", "mastery": CID + "/mastery"}}))
    cli.save(CID, "confirmed.json", {"att-s": {"proof-1": "proof_abc123"}})
    with open(cli.cdir(CID) / "submissions.jsonl", "a") as f:
        f.write(json.dumps({"attempt": "att-s", "kind": "correct", "answers": {"proof-1": "proof_abc123"}}) + "\n")
    ok, res = orchestrate.ensure_case_and_test(CID, sdir)
    case = sdir / "cases" / "single_solve"
    check("5 single case recorded + marked live_target, and SKIPPED (finished attempt: target 410) -> solver ok",
          ok and (case / "live_target.json").exists() and res and res[0].get("skipped") == "live_target_finished",
          (ok, res))
    # the CURRENT unsolved attempt of a timed mode is still replayable
    tdir = cli.cdir(CID + "/time_trial")
    (tdir / "last_timed.json").write_text(json.dumps({"attempt_id": "att-t", "result": "solver_incomplete"}))
    vcase = solvers.add_case(sdir, "variant-time_trial-att-t", dict(active("att-t"), mode="time_trial"), None,
                             {"proof-1": "x"})
    check("5 a live case of the mode's current unsolved attempt still replays (generalize target)",
          not webtarget.case_stale(vcase, sdir, "web"))
    with open(tdir / "submissions.jsonl", "a") as f:
        f.write(json.dumps({"attempt": "att-t", "kind": "correct"}) + "\n")
    check("5 ... and is skipped once that attempt is CORRECT", webtarget.case_stale(vcase, sdir, "web"))
    check("2 ... process_result maps a never-up target to error:start (backoff, never a generalize)",
          timed.process_result(CID + "/time_trial", sdir, dict(refused), log=quiet) == "error:start")

    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.base, ch.lane, ch.sdir, ch.entries = CID, "web", sdir, {"single_solve": {"id": CID}}
    cli.is_complete = lambda c: True
    check("5 single gate: GM-CORRECT live-target single accepted without a replayable case",
          ch._live_target_accept(CID, [{"case": "x", "ok": False}]) and (sdir / "live_target.json").exists())
    ch2 = orchestrate.Chain.__new__(orchestrate.Chain)
    ch2.base, ch2.lane, ch2.sdir = "warmups-day-20", "warmups", sdir
    check("5 ... never for a non-live lane", not ch2._live_target_accept("warmups-day-20", []))
    cli.is_complete = _saved["is_complete"]
    check("5 present_only keeps web answers (artifact 'Target 1' is not a file)",
          timed.present_only(active(), None, {"proof-1": "v"}) == {"proof-1": "v"})

    # -------------------------------------------------------------- 6. release detection
    paths.INDEX.write_text(json.dumps({
        **{f"{ln}-day-19": {"day": 19, "lane": ln, "dir": f"day19/{ln}"} for ln in
           ("warmups", "metadata-forensics", "script-analysis", "binary-reverse-engineering", "mobile-android")},
        **{f"web-exploitation-day-0{i}": {"day": 19, "lane": "web", "dir": f"day0{i}/web"} for i in (2, 3)},
        "web-exploitation-day-01-backup-exposure": {"day": 19, "lane": "web", "dir": "day01/web-back-up"}}))
    lanes = orchestrate._lanes_for(20)
    check("6 _lanes_for(20) includes the web lane once (GM filter name)", lanes.count("web") == 1 and len(lanes) == 6,
          lanes)
    check("6 _lanes_for(18) unchanged (no web before Day 19)", "web" not in orchestrate._lanes_for(18))
    check("6 _expected_modes(20) = 5 lanes x 3 + one web chain x 3", orchestrate._expected_modes(20) == 18,
          orchestrate._expected_modes(20))
    web_today = [True]

    def fake_gm(*args, timeout=180):
        if args[0] == "list" and "--lane" in args:
            ln = args[args.index("--lane") + 1]
            if ln == "web" and not web_today[0]:
                return {"http": 200, "body": {"challenges": []}}
            lane = "web-exploitation" if ln == "web" else ln
            return {"http": 200, "body": {"challenges": [
                {"id": f"{lane}-day-20-x" + ("" if m == "single_solve" else f"/{m}"), "lane": lane, "mode": m,
                 "day": 20, "name": ln} for m in ("single_solve", "time_trial", "mastery")]}}
        return {"http": 200, "body": {"challenges": []}}

    def slow_full(day=None):
        time.sleep(1.0)
        return [{"id": "full-list", "lane": "warmups", "mode": "single_solve", "day": 20, "name": "f"}]
    remote.gm, orchestrate.released_challenges = fake_gm, slow_full
    got = orchestrate._list_race(20, lanes, log=quiet)
    check("6 lane-list race: the union carries the web modes (18) and canonicalizes the lane",
          len(got) == 18 and sum(c["lane"] == "web" for c in got) == 3, [c["id"] for c in got])
    web_today[0] = False
    got = orchestrate._list_race(20, lanes, log=quiet)
    check("6 ... a 5-lane union never wins when web is expected (the full list does)",
          [c["id"] for c in got] == ["full-list"], [c["id"] for c in got][:3])

    def fake_web_list(*args, timeout=180):
        return {"http": 200, "body": {"challenges": [
            {"id": "web-exploitation-day-04-new" + s, "lane": "web-exploitation", "mode": m, "day": 4, "name": "N"}
            for s, m in (("", "single_solve"), ("/time_trial", "time_trial"), ("/mastery", "mastery"))] + [
            {"id": "web-exploitation-day-01-backup-exposure", "lane": "web-exploitation", "mode": "single_solve",
             "day": 19}]}}
    remote.gm = fake_web_list
    late = orchestrate._web_unlisted(20, set())
    reg = paths.lookup("web-exploitation-day-04-new") or {}
    check("6 unlisted web: an UNSEEN web id filed under another day is picked up (known ids never)",
          list(late) == ["web-exploitation-day-04-new"] and len(late["web-exploitation-day-04-new"]) == 3
          and reg.get("dir", "").startswith("day20/") and late["web-exploitation-day-04-new"][0]["lane"] == "web",
          (list(late), reg))
    remote.gm, orchestrate.released_challenges = _saved["gm"], _saved["released"]

    # -------------------------------------------------------------- 7. one live web target per team
    spans, lock_path = [], tmp / "locks" / "w.lock"

    def holder(i):
        with webtarget.slot(f"c{i}", log=quiet, path=lock_path, poll=0.01):
            with webtarget.slot(f"c{i}-nested", log=quiet, path=lock_path):   # re-entrant in the holding thread
                t0 = time.time()
                time.sleep(0.15)
                spans.append((t0, time.time()))
    ts = [threading.Thread(target=holder, args=(i,)) for i in range(3)]
    [t.start() for t in ts]
    [t.join(10) for t in ts]
    spans.sort()
    check("7 slot: three holders never overlap (and nesting does not deadlock)",
          len(spans) == 3 and all(a[1] <= b[0] + 1e-3 for a, b in zip(spans, spans[1:])), spans)

    orchestrate.set_state = lambda *a, **k: None
    webtarget.after_stage = lambda *a, **k: None
    cli.is_complete = lambda c: False
    live, peak, spans2 = [0], [0], []
    mu = threading.Lock()

    def stage():
        with mu:
            live[0] += 1
            peak[0] = max(peak[0], live[0])
        time.sleep(0.15)
        with mu:
            live[0] -= 1
        return True
    chains = []
    for i in range(2):
        c = orchestrate.Chain.__new__(orchestrate.Chain)
        c.base, c.lane, c.entries = f"web-exploitation-day-2{i}-x", "web", {"time_trial": {"id": f"web-x{i}/time_trial"}}
        chains.append(c)
    ts = [threading.Thread(target=c._web_slot, args=("time_trial", stage)) for c in chains]
    [t.start() for t in ts]
    [t.join(10) for t in ts]
    check("7 Chain._web_slot: two web chains never hold a target at once", peak[0] == 1, peak)
    c3 = orchestrate.Chain.__new__(orchestrate.Chain)
    c3.base, c3.lane, c3.entries = "warmups-day-20", "warmups", {"time_trial": {"id": "warmups-day-20/time_trial"}}
    live[0] = peak[0] = 0
    ts = [threading.Thread(target=c3._web_slot, args=("time_trial", stage)) for _ in range(2)]
    [t.start() for t in ts]
    [t.join(10) for t in ts]
    check("7 ... other lanes are not serialized", peak[0] == 2, peak)
    cli.is_complete = _saved["is_complete"]

    def boom(*a, **k):
        raise AssertionError("GM start on a web chain")
    cli.call = boom
    cp = orchestrate.Chain.__new__(orchestrate.Chain)
    cp.base, cp.lane, cp.entries = CID, "web", {"time_trial": {"id": CID + "/time_trial"}}
    cp._prefetch_tt_start()
    check("7 TT pre-start never fires for web", not getattr(cp, "_prefetch_started", False))
    cp.scout_stage()
    check("7 scout never runs for web (no GM call)", True)
    cli.gm_solved = boom
    check("7 drift watcher skips web modes (never resumes a web chain)", driftwatch.unsolved(20) == [],
          driftwatch.unsolved(20))
    cli.call = _saved["call"]
    cli.gm_solved = _saved["gm_solved"]
    check("7 answer-first + reuse race cover web", "web" in orchestrate.ANSWER_FIRST_LANES
          and "web" in orchestrate.REUSE_RACE_LANES)

    # 8. web TT target requested at the single's CORRECT (rehearsal blind D19: the chain waited 34-52 s for the solver
    #    worker before even asking; timed targets then sat ~5 min in `preparing`) -- once, TT only, web only
    calls = []
    cli.call = lambda cid, *a, **k: (calls.append((cid,) + a), {"http": 200, "body": {"result": "preparing"}})[1]
    cli.is_complete = lambda cid: False
    kw = orchestrate.Chain.__new__(orchestrate.Chain)
    kw.base, kw.lane = CID, "web"
    kw.entries = {"time_trial": {"id": CID + "/time_trial"}, "mastery": {"id": CID + "/mastery"}}
    kw._web_tt_kick()
    kw._web_tt_kick()
    for t in threading.enumerate():
        if t.name.startswith("web-tt-kick-"):
            t.join(5)
    check("8 web: TT start requested once at the single's CORRECT", calls == [(CID + "/time_trial", "start",
                                                                              CID + "/time_trial")], calls)
    calls.clear()
    nw = orchestrate.Chain.__new__(orchestrate.Chain)
    nw.base, nw.lane, nw.entries = "warmups-day-20", "warmups", {"time_trial": {"id": "warmups-day-20/time_trial"}}
    nw._web_tt_kick()
    os.environ["HCTF_RUN_FOR_TIME"] = "1"
    rt = orchestrate.Chain.__new__(orchestrate.Chain)
    rt.base, rt.lane, rt.entries = CID, "web", {"time_trial": {"id": CID + "/time_trial"}}
    rt._web_tt_kick()
    os.environ.pop("HCTF_RUN_FOR_TIME", None)
    time.sleep(0.2)
    check("8 ... never for other lanes, never for a clocked (run_for_time) pool", calls == [], calls)
    cli.call = _saved["call"]

    # 9. the slot is held for the WHOLE web chain: a 2nd chain's single never starts between chain 1's stages (the TT
    #    requested at the single's CORRECT is already preparing then)
    order, olock = [], threading.Lock()

    def mk(i):
        c = orchestrate.Chain.__new__(orchestrate.Chain)
        c.base, c.lane, c.name, c.only_modes = f"web-exploitation-day-3{i}-x", "web", "x", None
        c.entries = {m: {"id": f"web-exploitation-day-3{i}-x" + ("" if m == "single_solve" else "/" + m)}
                     for m in ("single_solve", "time_trial", "mastery")}
        c.recover_interrupted_generalize = lambda: None
        c._bg_gen_take = lambda *a: None
        c.scout_stage = lambda: None

        def stage(name):
            with olock:
                order.append(f"{i}:{name}")
            time.sleep(0.05)
            return True
        c.single = lambda: stage("single")
        c.timed_stage = lambda m: stage(m)
        return c
    _ss = orchestrate.set_state
    orchestrate.set_state = lambda *a, **k: None
    webtarget.after_stage = lambda *a, **k: None
    ts = [threading.Thread(target=mk(i)._run) for i in (1, 2)]
    [t.start() for t in ts]
    [t.join(10) for t in ts]
    orchestrate.set_state = _ss
    webtarget.after_stage = _saved["after_stage"]
    firsts = [o.split(":")[0] for o in order]
    check("9 web chain holds the slot across single -> TT -> Mastery (no interleave)",
          len(order) == 6 and firsts in (["1"] * 3 + ["2"] * 3, ["2"] * 3 + ["1"] * 3), order)
    cli.is_complete = _saved["is_complete"]

    # 10. early handoff on a web single: the single's target is spent at CORRECT, so the replay can't verify the solver
    #     (D20 LFI: TT target active at 21:01:06, the TT waited until the workers exited at 21:01:47) -- hand the solver
    #     over once it is quiet WEB_SPEC_STABLE s, without a replay; never for other lanes or before the CORRECT
    hc = orchestrate.Chain.__new__(orchestrate.Chain)
    hc.base, hc.lane, hc.sdir, hc.root = CID, "web", sdir, paths.challenge_root(CID)
    cli.is_complete = lambda c: True
    os.utime(sdir / "solve.py", None)
    check("10 web handoff: waits while the solver is still being edited", hc._spec_snapshot(CID) is None)
    old = time.time() - orchestrate.WEB_SPEC_STABLE - 2
    os.utime(sdir / "solve.py", (old, old))
    snap = hc._spec_snapshot(CID)
    check("10 ... then hands over the quiet solver with no replay (this solve.py exits 3: any replay would fail)",
          snap is not None and (Path(snap) / "solve.py").exists(), snap)
    hn = orchestrate.Chain.__new__(orchestrate.Chain)
    hn.base, hn.lane, hn.sdir, hn.root = CID, "warmups", sdir, paths.challenge_root(CID)
    check("10 ... other lanes still need the replay", hn._spec_snapshot(CID) is None)
    cli.is_complete = lambda c: False
    hc._spec_rejected = None
    check("10 ... and web needs the single's CORRECT first", hc._spec_snapshot(CID) is None)
    cli.is_complete = _saved["is_complete"]
    if snap:
        shutil.rmtree(Path(snap).parent, ignore_errors=True)
finally:
    for k, v in _saved.items():
        if k == "call":
            cli.call = v
        elif k in ("gm_status", "arena_start", "after_stage"):
            setattr(webtarget, k, v)
        elif k == "gm":
            remote.gm = v
        elif k in ("is_complete", "gm_solved"):
            setattr(cli, k, v)
        elif k == "set_state":
            orchestrate.set_state = v
        elif k == "released":
            orchestrate.released_challenges = v
    paths.CHALLENGES, paths.INDEX, paths.LOCKS = _paths
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    for p in (ROOT / ".run" / "tmp-timed").glob("web_exploitation_day_20_test*"):
        shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink()

if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall web-lane checks passed")
