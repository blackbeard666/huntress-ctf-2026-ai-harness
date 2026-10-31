"""D31 web fixes, offline: fakes only, no GM, no live targets, no workers.
- #1 the fresh-drop gm_solved skip of a web single FIRES on a real GM list entry: the live list omits `solved` for an
     unsolved mode (never `solved: false`), so an entry is fresh when it says false OR it is a live list entry (pool
     fields) with no solved / solved_by / flag. Solved / index-synthesized entries and local state still ask gm_solved.
     gm_solved's sticky-list fallback lists the day the mode is REGISTERED under (web ids run on their own day track).
- #2 a live-web single's answer-first worker starts at target-up (Chain._web_target_af), once, under the one-per-single
     lock; not on a non-ready start, a stale start.json, a non-web lane, the kill switch, or when ineligible.

Run:  source bin/env.sh && python3 tests/test_d31_web.py      (exit 0 = all pass)
"""
import contextlib
import inspect
import json
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hctf import cli, orchestrate, webtarget  # noqa: E402

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


class _Stop(Exception):
    pass


# ---------------------------------------------------------------- #1: fresh-drop detection on real list shapes
# Verbatim (minus prompt/guidance) from the D29 drop list (gm.jsonl 20261029T130011Z) and the D30 list after the solve.
LIVE_UNSOLVED = {"id": "web-exploitation-day-27-internal-affairs", "name": "Internal Affairs", "mode": "single_solve",
                 "day": 29, "curriculum_day": 27, "lane": "web-exploitation", "title": "Internal Affairs",
                 "run_for_time_supported": False, "ranked_deadline_ms": None, "ranked_pool_size": 0,
                 "regular_pool_size": 1, "ranked_set_count": 0, "regular_set_count": 1}
LIVE_SOLVED = dict(LIVE_UNSOLVED, solved=True, solved_by={"name": "_blackb3ard", "at": "2026-10-29T13:01:45.000Z"},
                   flag="486b71f78a751f4dd92ba4483350acf5")
# chain_for(): an entry synthesized from the local index -- no list fields at all
INDEX_SYNTH = {"id": "web-exploitation-day-27-internal-affairs", "mode": "single_solve", "lane": "web",
               "name": "Internal Affairs"}
# _stream_groups / run canonicalize the lane in place: the list fields survive
CANON = dict(LIVE_UNSOLVED, lane="web", gm_lane="web-exploitation")

f = orchestrate._web_fresh_drop
check("#1 live list entry WITHOUT `solved` (the GM's unsolved shape) = fresh drop", f(LIVE_UNSOLVED) is True)
check("#1 lane-canonicalized live entry is still fresh", f(CANON) is True)
check("#1 explicit `solved: false` = fresh (old rule kept)", f(dict(LIVE_UNSOLVED, solved=False)) is True
      and f({"id": "w", "solved": False}) is True)
check("#1 solved entry (solved: true + solved_by + flag) is NOT fresh", f(LIVE_SOLVED) is False)
check("#1 `solved_by` or `flag` without `solved` is NOT fresh (any solve marker -> ask)",
      f(dict(LIVE_UNSOLVED, solved_by={"name": "x"})) is False and f(dict(LIVE_UNSOLVED, flag="abc")) is False)
check("#1 `solved: null` is NOT fresh (unknown -> ask)", f(dict(LIVE_UNSOLVED, solved=None)) is False)
check("#1 index-synthesized entry (chain_for: no list fields) is NOT fresh", f(INDEX_SYNTH) is False)
check("#1 bare / partial / non-dict entries are NOT fresh",
      f({"id": "w"}) is False and f({"id": "w", "regular_pool_size": 1}) is False and f(None) is False
      and f("x") is False)
with patched({(orchestrate, "WEB_FRESH_SKIP_SOLVED"): False}):
    check("#1 kill switch HCTF_WEB_FRESH_SKIP_SOLVED=0: never fresh",
          not f(LIVE_UNSOLVED) and not f({"solved": False}))

# against the real recorded GM list replies (if the log is here): fresh <=> the GM did not mark the mode solved
GMLOG = ROOT / ".run" / "logs" / "gm.jsonl"
if not GMLOG.exists():
    GMLOG = Path.home() / "huntress-2026" / ".run" / "logs" / "gm.jsonl"
n_real, bad = 0, []
if GMLOG.exists():
    with open(GMLOG, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"op": "list"' not in line[:80] or line[8:16] < "20261028":
                continue
            try:
                body = json.loads(line).get("body") or {}
            except ValueError:
                continue
            for c in body.get("challenges") or []:
                if not isinstance(c, dict):
                    continue
                n_real += 1
                if f(c) is not (not c.get("solved")):
                    bad.append((c.get("id"), c.get("solved")))
    check(f"#1 real GM list entries since D28 ({n_real}): fresh exactly when the GM did not mark the mode solved",
          n_real > 0 and not bad, bad[:5])
else:
    print("skip #1 real gm.jsonl replay (no log here)")


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


check("#1 web fresh drop on the REAL unsolved list shape: no gm_solved round trip, the single starts at once",
      single_gate("web", LIVE_UNSOLVED) == ([], "continued"), single_gate("web", LIVE_UNSOLVED))
check("#1 web, solved list entry, no local state (resume/replay): asked AND accepted -> timed modes",
      single_gate("web", LIVE_SOLVED, gm=True) == (["web-x"], True))
check("#1 web, live unsolved entry but local state (crash resume): gm_solved still asked",
      single_gate("web", LIVE_UNSOLVED, trace=True, gm=True) == (["web-x"], True))
check("#1 web, index-synthesized entry (hctf solve <cid>): gm_solved still asked",
      single_gate("web", INDEX_SYNTH) == (["web-x"], "continued"))
check("#1 regular lane fresh drop: unchanged (no local trace -> no gm_solved, whatever the entry)",
      single_gate("warmups", dict(LIVE_UNSOLVED, lane="warmups")) == ([], "continued")
      and single_gate("warmups", INDEX_SYNTH) == ([], "continued"))
check("#1 regular lane with local state: unchanged (gm_solved asked)",
      single_gate("warmups", LIVE_UNSOLVED, trace=True, gm=True) == (["web-x"], True))

# gm_solved's sticky-list fallback: the REGISTERED day, not the id's own `-day-NN`
WEB_ID = "web-exploitation-day-27-internal-affairs"
idx = {WEB_ID: {"day": 29, "lane": "web"}, "warmups-day-30": {"day": 30, "lane": "warmups"}}
lk = lambda cid: idx.get(cid.split("/")[0])  # noqa: E731
with patched({(cli.paths, "lookup"): lk}):
    check("#1 _list_day: a web id lists under its registered day (29), not its id day (27)",
          cli._list_day(WEB_ID) == 29 and cli._list_day(WEB_ID + "/mastery") == 29,
          (cli._list_day(WEB_ID), cli._list_day(WEB_ID + "/mastery")))
    check("#1 _list_day: non-web id = its id day (registered day equals it)", cli._list_day("warmups-day-30") == 30)
    check("#1 _list_day: unregistered id falls back to its id day", cli._list_day("script-analysis-day-31") == 31)
with patched({(cli.paths, "lookup"): lambda cid: {"day": 19, "gm_day": 2}}):
    check("#1 _list_day: a recorded gm_day wins", cli._list_day("web-exploitation-day-02-idor") == 2)


def _boom(cid):
    raise RuntimeError("index torn")


with patched({(cli.paths, "lookup"): _boom}):
    check("#1 _list_day: index error -> id day (never raises)", cli._list_day(WEB_ID) == 27)
with patched({(cli.paths, "lookup"): lambda cid: None}):
    check("#1 _list_day: no day anywhere -> None", cli._list_day("no-day-here-x") is None)

listed = []
tmp = Path(tempfile.mkdtemp())
with patched({(cli.paths, "lookup"): lk, (cli, "cdir"): lambda cid: tmp, (cli, "ever_correct"): lambda cid: False,
              (cli, "call"): lambda *a, **k: {"body": {"result": "start_required"}},
              (cli, "gm_list_solved"): lambda day, max_age=20.0: (listed.append(day), {WEB_ID: "2026-10-29T13:01Z"})[1]}):
    got = cli.gm_solved(WEB_ID)
check("#1 gm_solved(web id): the sticky-list fallback lists day 29 (where the GM files it) and finds the solve",
      listed == [29] and got is True, (listed, got))

# ---------------------------------------------------------------- #2: answer-first at target-up
READY = {"attempt_id": "att-1", "answer_ids": ["proof-1"], "result": "active",
         "targets": [{"label": "Target 1", "url": "https://t1.example.invalid/"}]}
PREPARING = {"result": "preparing", "attempt_id": "att-1"}
made = []


class FakeAF:
    def __init__(self, chain, cid):
        self.chain, self.cid, self.ids = chain, cid, ["proof-1"]
        self.race_done = None
        made.append(self)

    def start(self, race_done=None, residual=None):
        self.race_done, self.residual = race_done, residual
        return self


def af_chain(lane="web"):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base, ch.sdir = lane, "web-x", Path(tempfile.mkdtemp()) / "solver"
    ch._race_done = threading.Event()
    return ch


def drive_af(ch, body, start_json=None, eligible=(True, ""), complete=False, extra=None):
    made.clear()
    says = []
    pairs = {(orchestrate, "say"): lambda m, *a, **k: says.append(m), (orchestrate, "AnswerFirst"): FakeAF,
             (orchestrate.cli, "load"): lambda cid, name: (start_json if start_json is not None else body)
             if name == "start.json" else None,
             (orchestrate.cli, "is_complete"): lambda cid: complete,
             (orchestrate, "answer_first_eligible"): lambda lane, n: eligible,
             (orchestrate, "ANSWER_FIRST"): True}
    pairs.update(extra or {})
    with patched(pairs):
        t = orchestrate.Chain._web_target_af(ch, "web-x", body)
        if t is not None:
            t.join(5)
    return t, says


ch = af_chain()
t, says = drive_af(ch, READY)
check("#2 web target up: ONE answer-first worker starts, wired to the race event (the launch prep's own call)",
      t is not None and len(made) == 1 and getattr(ch, "_af", None) is made[0] and made[0].race_done is ch._race_done
      and made[0].residual is None, (t, made, says))
check("#2 target-up launch is logged", any("answer-first worker starts now" in m for m in says), says)
t2, _ = drive_af(ch, READY)
check("#2 a second call (or the launch prep after it) never starts another: `_af` is set", t2 is None and not made)

# the launch prep's side_workers block, run after the early launch, sees `_af` and skips (same lock + check)
src = inspect.getsource(orchestrate.Chain._single)
check("#2 the launch prep keeps its `_af is None` guard under _af_launch_lock",
      'with self._af_launch_lock():' in src and 'if getattr(self, "_af", None) is not None:' in src)
i_dry, i_af = src.find("self._start_prior_dry_run(cid)"), src.find("self._web_target_af(cid, body)")
i_tri, i_go = src.find("def run_triage"), src.find("go text ready at")
check("#2 call site: after the start + prior dry-run start, before triage and the go-text / prompt build",
      0 <= i_dry < i_af < i_tri < i_go, (i_dry, i_af, i_tri, i_go))

ch = af_chain()
t, _ = drive_af(ch, PREPARING)
check("#2 target not ready (preparing) -> no early launch (the launch prep decides)", t is None and not made)
t, _ = drive_af(ch, None)
check("#2 start failed (no body) -> no early launch", t is None and not made)
t, _ = drive_af(ch, READY, start_json=dict(READY, attempt_id="att-OLD"))
check("#2 start.json of ANOTHER attempt (stale) -> no worker", not made and getattr(ch, "_af", None) is None)
t, _ = drive_af(ch, READY, complete=True)
check("#2 single already complete -> no worker", not made and getattr(ch, "_af", None) is None)
t, says = drive_af(ch, READY, eligible=(False, "3 answer-first workers already running (cap 3)"))
check("#2 ineligible (cap / memory) -> nothing set, so the launch prep retries; reason logged",
      getattr(ch, "_af", None) is None and any("launch prep retries" in m for m in says), says)
t, _ = drive_af(af_chain("metadata-forensics"), READY)
check("#2 non-web lane -> no early launch (unchanged)", t is None and not made)
t, _ = drive_af(af_chain("welcome"), READY)
check("#2 welcome -> no early launch", t is None and not made)
t, _ = drive_af(af_chain(), READY, extra={(orchestrate, "WEB_AF_AT_TARGET"): False})
check("#2 kill switch HCTF_WEB_AF_AT_TARGET=0 -> no early launch (old path)", t is None and not made)
t, _ = drive_af(af_chain(), READY, extra={(orchestrate, "ANSWER_FIRST"): False})
check("#2 HCTF_ANSWER_FIRST=0 -> no early launch", t is None and not made)


class Boom(FakeAF):
    def __init__(self, chain, cid):
        raise RuntimeError("render failed")


ch = af_chain()
t, says = drive_af(ch, READY, extra={(orchestrate, "AnswerFirst"): Boom})
check("#2 a construction error never raises into the chain (noted; the launch prep still runs)",
      getattr(ch, "_af", None) is None and any("target-up answer-first note" in m for m in says), says)

# race: the early thread and a concurrent launch-prep style check under the same lock -> exactly one worker
ch = af_chain()
made.clear()
barrier = threading.Barrier(9)


def prep_like():
    barrier.wait()
    with ch._af_launch_lock():
        if getattr(ch, "_af", None) is None:
            ch._af = FakeAF(ch, "web-x").start()


with patched({(orchestrate, "say"): lambda *a, **k: None, (orchestrate, "AnswerFirst"): FakeAF,
              (orchestrate.cli, "load"): lambda cid, name: READY, (orchestrate.cli, "is_complete"): lambda cid: False,
              (orchestrate, "answer_first_eligible"): lambda lane, n: (True, ""), (orchestrate, "ANSWER_FIRST"): True}):
    ths = [threading.Thread(target=prep_like) for _ in range(8)]
    for th in ths:
        th.start()
    barrier.wait()
    t = orchestrate.Chain._web_target_af(ch, "web-x", READY)
    for th in ths:
        th.join(5)
    if t is not None:
        t.join(5)
    time.sleep(0.05)
check("#2 early launch racing the launch prep: exactly ONE answer-first worker", len(made) == 1, len(made))


if __name__ == "__main__":
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
    sys.exit(1 if failures else 0)
