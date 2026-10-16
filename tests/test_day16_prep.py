"""Day 16 prep (D15 review + "train on previous days"). Offline: no GM / Homebase / workers.
Part A (D15 run fixes):
- mastery_delta lists ids NEW to the lane first, all of them (D15 metadata: the synthesis id was cut at 12).
- A Single whose lane's previous start reply was large starts on the public GM (daemon channel head-of-line block).
- A failed live untimed attempt is re-fetched from the public GM (not over the VPN); a different attempt -> fallback.
- Binary duel only with HCTF_DUEL_BINARY_MIN_AVAIL_GB set and that much memory free.

Run:  source bin/env.sh && python3 tests/test_day16_prep.py      (exit 0 = all pass)
"""
import hashlib
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import duel, orchestrate, prebuild, remote, workers  # noqa: E402  (prebuild before any ROOT patch)
from hctf import hb_timed as ht  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="hctf-d16p-"))

# A1) mastery_delta: new-to-lane ids first and complete; carried-over ones sampled after
single = {"answer_ids": ["d16-x-001-x-new-field"], "questions": [{"id": "d16-x-001-x-new-field"}]}
timed_c = {"answer_ids": [f"set1.d0{i}-f-001-f-old-{i}" for i in range(1, 10)] + ["set1.day-16-synthesis-zzz-order",
                                                                                     "set1.d16-x-001-x-new-field"]}
known = {orchestrate.field_shape(f"d0{i}-f-001-f-old-{i}") for i in range(1, 10)}
txt = orchestrate.mastery_delta(single, [timed_c], known=lambda: known)
assert "1 question id(s) NEW to this lane" in txt and "`day-16-synthesis-zzz-order`" in txt, txt
assert txt.index("synthesis") < txt.index("carried over"), txt
assert "9 id(s) carried over" in txt, txt
txt0 = orchestrate.mastery_delta(single, [timed_c], known=lambda: (_ for _ in ()).throw(OSError("boom")))
assert "MASTERY COMPOUNDS" in txt0 and "NEW to this lane" not in txt0   # a failing lookup never costs the single
d15 = ROOT / "challenges/day15/metadata-a-word-to-the-wise"
if (d15 / "single_solve/start.json").exists() and (d15 / "time_trial/contract.json").exists():
    txt = orchestrate.mastery_delta(json.loads((d15 / "single_solve/start.json").read_text()),
                                    [json.loads((d15 / f"{m}/contract.json").read_text()) for m in ("time_trial", "mastery")],
                                    known=lambda: orchestrate.lane_known_shapes("metadata-forensics", 15))
    assert "NEW to this lane" in txt and "metadata-day-15-synthesis-sha256-order" in txt.split("carried over")[0], txt[:400]
    print("ok  A1 mastery_delta: D15 metadata -> the synthesis id is listed first as NEW to the lane")
else:
    print("ok  A1 mastery_delta: new-to-lane ids first (D15 data absent here)")

# A3) large previous start reply -> public start, never via the daemon / Homebase
saved = {k: getattr(remote, k) for k in ("ROOT", "_BIG_START")}
try:
    remote.ROOT, remote._BIG_START = TMP, {}
    for day, lane, size in ((14, "script-analysis", 650_000), (14, "warmups", 3_000)):
        d = TMP / f"challenges/day{day:02d}/{lane}-x"
        (d / "single_solve").mkdir(parents=True)
        (d / "meta.json").write_text(json.dumps({"lane": lane}))
        (d / "single_solve/start.json").write_bytes(b"x" * size)
    assert remote._big_start("script-analysis-day-15-crumb") is True
    assert remote._big_start("warmups-day-15") is False
    assert remote._big_start("script-analysis-day-15-crumb/mastery") is False      # timed modes: their own path
    assert remote._big_start("script-analysis-day-14-x") is False                  # no EARLIER day
finally:
    for k, v in saved.items():
        setattr(remote, k, v)
print("ok  A3 start routing: previous start.json > 200 KB -> public; small lanes / timed modes / no history unchanged")

# A2) public refetch of a failed live untimed attempt: same files as scoped_pull, sha-checked; wrong attempt -> raise
blob = b"evidence-bytes"
body = {"attempt_id": "A1", "answer_ids": ["set1.a", "set2.b"],
        "questions": [{"id": "set1.a", "artifact": "ev-01.zip -> a.txt"}, {"id": "set2.b", "artifact": "ev-02.zip -> b.txt"}],
        "artifacts": [{"download": "/?op=download&capability=" + "1" * 64, "sha256": hashlib.sha256(blob).hexdigest()},
                      {"download": "/?op=download&capability=" + "2" * 64, "sha256": hashlib.sha256(blob).hexdigest()}]}
saved = {k: getattr(ht, k) for k in ("_post_once", "_get_bytes", "_POOL")}
got_caps = []
try:
    ht._POOL = object()        # never open a real pool here
    ht._post_once = lambda payload, tries=3: body
    ht._get_bytes = lambda cap, timeout=20: (got_caps.append(cap), blob)[1]
    local = TMP / "tmp-timed" / "c_mastery"
    res = {"attempt_id": "A1", "result": "incorrect", "wrong": [["set2.b", "x"]], "deadline": None, "run_for_time": False}
    names = workers.public_pull(res, "c_mastery", local, "c/mastery")
    assert names == ["ev-02.zip"] and got_caps == ["2" * 64], (names, got_caps)          # only the failing set
    assert json.loads((local / "contract.json").read_text())["attempt_id"] == "A1" and (local / "result.json").exists()
    ht._post_once = lambda payload, tries=3: {**body, "attempt_id": "OTHER"}
    try:
        workers.public_pull(res, "c_mastery", local, "c/mastery")
        raise AssertionError("a different attempt must not be adopted")
    except RuntimeError:
        pass
finally:
    for k, v in saved.items():
        setattr(ht, k, v)
print("ok  A2 public refetch: failing set only, contract/result saved, sha-checked; another attempt -> fallback")

# A4) binary duel gate
saved = duel.BINARY_MIN_AVAIL_GB, duel._mem_avail_gb
try:
    duel.BINARY_MIN_AVAIL_GB = 0
    assert duel.eligible("binary-reverse-engineering")[0] is False
    duel.BINARY_MIN_AVAIL_GB, duel._mem_avail_gb = 3.0, (lambda: 5.0)
    assert duel.eligible("binary-reverse-engineering")[0] is True
    duel._mem_avail_gb = lambda: 2.0
    assert duel.eligible("binary-reverse-engineering")[0] is False
finally:
    duel.BINARY_MIN_AVAIL_GB, duel._mem_avail_gb = saved
print("ok  A4 binary duel: off by default; on only with the knob set and enough MemAvailable")

# B1) train: today's solver lost an earlier day's concept -> case adopted + ONE generalize; dry run edits nothing
from hctf import compound, paths, train  # noqa: E402
TR = TMP / "train"
SOLVE = """import argparse, json, pathlib
ap = argparse.ArgumentParser(); ap.add_argument('--contract'); ap.add_argument('--artifacts'); a = ap.parse_args()
c = json.load(open(a.contract))
print(json.dumps({i: pathlib.Path(a.artifacts, 'blob.txt').read_text().strip()[::-1] if %s else None
                  for i in c['answer_ids']}))
"""


def chal(day, name, solve_ok_for_reverse):
    d = TR / "challenges" / f"day{day:02d}" / name
    (d / "solver" / "cases" / "single_solve" / "artifacts").mkdir(parents=True)
    (d / "meta.json").write_text(json.dumps({"lane": "warmups", "base": f"warmups-day-{day:02d}"}))
    (d / "solver" / "solve.py").write_text(SOLVE % solve_ok_for_reverse)
    case = d / "solver" / "cases" / "single_solve"
    (case / "contract.json").write_text(json.dumps({"answer_ids": ["message"], "questions": [{"id": "message"}]}))
    (case / "expected.json").write_text(json.dumps({"message": "abc"}))
    (case / "artifacts" / "blob.txt").write_text("cba")
    return d


saved = (paths.CHALLENGES, compound.ROOT, paths.ROOT)
calls = []
try:
    paths.CHALLENGES, compound.ROOT, paths.ROOT = TR / "challenges", TR, TR
    chal(14, "warmups-old", "True")
    today = chal(15, "warmups-new", "False")            # day 15's solver no longer decodes day 14's concept
    import hctf.orchestrate as _o
    saved_o = (_o.chain_for, _o.mutation_probe)
    _o.mutation_probe = lambda sdir, mc=None, timeout=90: ("", [], {})

    class StubChain:
        def generalize(self, base, wrong=None, fixed=None, diag=None):
            calls.append((base, sorted(diag)))
            (today / "solver" / "solve.py").write_text(SOLVE % "True")      # the "worker" fixes it
    _o.chain_for = lambda base, pools, gov: StubChain()
    rep = train.run(15, log=lambda m: None, dry_run=True, deadline=time.time() + 600)
    assert not calls and not list((today / "solver" / "cases").glob("compound-*")), calls
    assert "1 hard miss(es)" in rep["warmups-day-15"]["before"], rep
    rep = train.run(15, log=lambda m: None, deadline=time.time() + 600)
    assert calls == [("warmups-day-15", ["compound_pre"])], calls
    assert (today / "solver" / "cases" / "compound-d14-single_solve" / "expected.json").exists()
    assert rep["warmups-day-15"]["generalized"] == 1 and "0 hard miss(es)" in rep["warmups-day-15"]["after"], rep
finally:
    paths.CHALLENGES, compound.ROOT, paths.ROOT = saved
    _o.chain_for, _o.mutation_probe = saved_o
print("ok  B1 train: earlier-day miss -> compound-d14 case adopted + one generalize, re-checked clean; dry run edits nothing")

# B2) cumulative lanes: mobile + warmups seed from yesterday's solver; metadata keeps its lane seed
assert {"mobile-android", "warmups", "binary-reverse-engineering", "script-analysis"} <= set(orchestrate.CUMULATIVE_LANES)
assert "metadata-forensics" not in orchestrate.CUMULATIVE_LANES
print("ok  B2 cumulative lanes: binary, script, mobile, warmups (metadata = lane solver seed)")

# C1) live-answer race on a failed UNTIMED attempt: pass -> mode done (no retry); all accepted -> free reconnect;
#     clocked / too many fields -> no live worker; accepted values flow into the resumed attempt (timed_env)
from hctf import cli, timed  # noqa: E402
untimed_last = {"result": "incorrect", "attempt_id": "M1", "deadline": None, "run_for_time": False,
                "verified": {"x": "1"}, "localize_complete": True, "wrong": [["set1.a-field", "bad"]], "fixed": {}}
assert orchestrate._live_fields(untimed_last, [("set1.a-field", "bad")], {}) == ["set1.a-field"]
assert orchestrate._live_fields({**untimed_last, "deadline": "2026-10-16T13:00:00Z"}, [("set1.a-field", "bad")], {}) == []
assert orchestrate._live_fields(untimed_last, [("set1.a-field", "bad")], {"set1.a-field": "ok"}) == []
assert orchestrate._live_fields({**untimed_last, "missing": ["set2.b"]}, [], {}) == ["set2.b"]

ch = object.__new__(orchestrate.Chain)
ch.base, ch.sdir, ch.lane = "b", TMP, "warmups"
ch.entries = {"mastery": {"id": "b/mastery"}}
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
runs, gens, lives = [], [], []


class FakeLive:
    mode = "pass"

    def __init__(self, chain, cid, last, fields, wrong, fixed):
        self.fields, self.attempt = fields, last.get("attempt_id")
        self.passed = self.all_accepted = False
        lives.append(fields)

    def start(self):
        self.passed, self.all_accepted = FakeLive.mode == "pass", FakeLive.mode == "accepted"
        return self

    def link(self, evt):
        evt.set()

    def finish(self, wait=5.0):
        return self


def stage(results, last):
    it = iter(results)
    patches = {
        (orchestrate, "set_state"): lambda *a, **k: None, (orchestrate, "record_timed_case"): lambda *a, **k: None,
        (orchestrate, "say"): lambda *a, **k: None, (orchestrate.cli, "is_complete"): lambda cid: False,
        (orchestrate.cli, "gm_solved"): lambda cid: False, (timed, "last_result"): lambda cid: last,
        (orchestrate.time, "sleep"): lambda s: None, (orchestrate, "LiveAnswer"): FakeLive,
        (orchestrate.Chain, "generalize"): lambda self, cid, wrong=None, fixed=None, diag=None, live=None:
            gens.append(live is not None),
        (orchestrate.Chain, "_await_probes"): lambda self, w: True,
        (orchestrate.Chain, "_late_probes"): lambda self, cid, wait=False, defer_compound=False: {},
        (orchestrate.Chain, "_mastery_speed_gate"): lambda self, cid: None,
        (orchestrate.Chain, "_tt_fix_gate"): lambda self, cid: None,
        (orchestrate.Chain, "_early_kw"): lambda self, cid, untimed=False: {},
        (orchestrate.Chain, "_early_join"): lambda self, cid: False,
        (orchestrate, "capture_variant"): lambda *a, **k: None,
        (timed, "resolve_labels_online"): lambda *a, **k: set(),
        (timed, "run"): lambda cid, sdir, log=None, **k: (runs.append(k.get("op", "start")), next(it))[1],
    }
    saved = {k: getattr(*k) for k in patches}
    ch._pre_attempt_done = True
    try:
        for (mod, name), fn in patches.items():
            setattr(mod, name, fn)
        return ch.timed_stage("mastery")
    finally:
        for (mod, name), fn in saved.items():
            setattr(mod, name, fn)


FakeLive.mode = "pass"
runs.clear(), gens.clear(), lives.clear()
assert stage(["blocked"], untimed_last) is True and len(runs) == 1 and gens == [True] and lives == [["set1.a-field"]], (runs, gens, lives)
FakeLive.mode = "accepted"
runs.clear(), gens.clear(), lives.clear()
assert stage(["blocked", "correct"], untimed_last) is True and runs == ["resume", "resume"], runs   # live banked attempt: reconnect, never re-roll
FakeLive.mode = "pass"
runs.clear(), gens.clear(), lives.clear()
clocked = {**untimed_last, "deadline": "2026-10-16T13:00:00Z", "run_for_time": True}
assert stage(["blocked", "correct"], clocked) is True and not lives and gens == [False], (lives, gens)
many = {**untimed_last, "wrong": [[f"set1.f{i}", "x"] for i in range(orchestrate.LIVE_MAX_FIELDS + 1)]}
runs.clear(), gens.clear(), lives.clear()
assert stage(["blocked", "correct"], many) is True and not lives, lives
print("ok  C1 live-answer: pass ends the mode (no retry); all-accepted -> free reconnect; clocked / >max fields -> none")

LV = TMP / "live"
saved_cdir = cli.cdir
try:
    cli.cdir = lambda cid: LV
    LV.mkdir(parents=True, exist_ok=True)
    (LV / "last_timed.json").write_text(json.dumps({"attempt_id": "M1"}))
    (LV / "submissions.jsonl").write_text("\n".join(json.dumps(x) for x in (
        {"attempt": "M1", "answers": {"set1.a-field": "good"}, "kind": "accepted"},
        {"attempt": "M1", "answers": {"set1.b": "nope"}, "kind": "incorrect"},
        {"attempt": "OLD", "answers": {"set1.c": "x"}, "kind": "accepted"})) + "\n")
    ov = workers.live_overlay("b/mastery")
    assert ov == {"attempt": "M1", "answers": {"set1.a-field": "good"}}, ov
    env = workers.timed_env("b/mastery")
    assert json.loads(env["HCTF_LIVE_OVERLAY"])["answers"] == {"set1.a-field": "good"}
    saved_ctx = ht._CTX.opts
    ht._CTX.opts = {"HCTF_LIVE_OVERLAY": env["HCTF_LIVE_OVERLAY"]}
    assert ht._bank_load("b/mastery", "M1") == {"set1.a-field": "good"} and ht._bank_load("b/mastery", "M2") == {}
    ht._CTX.opts = saved_ctx
finally:
    cli.cdir = saved_cdir
print("ok  C1 overlay: GM-accepted live answers of THIS attempt -> timed_env -> hb_timed bank (other attempts ignored)")

# B3) prebuild: 5 lanes; targets ranked atlas p1 -> TARGETS.json -> atlas p2/p3; DFIR libs allowed; D1 cues inline
from hctf import prebuild  # noqa: E402
assert {"mobile-android", "script-analysis"} <= set(prebuild.enabled_lanes()) and len(prebuild.AUTO_LANES) == 5
cfg = {"targets": "tests/data/x/TARGETS.json", "atlas": "reference/coverage/x.md"}
AT = TMP / "atlas"
(AT / "tests/data/x").mkdir(parents=True)
(AT / "reference/coverage").mkdir(parents=True)
(AT / "tests/data/x/TARGETS.json").write_text(json.dumps({"targets": [{"id": "hand-a", "goal": "a"},
                                                                       {"id": "both", "goal": "own fields"}]}))
(AT / "reference/coverage/x.md").write_text("# x\n## Readiness gaps\n```json\n" + json.dumps([
    {"id": "p2-gap", "concept": "c2", "priority": 2, "action": "prebuild", "detail": "d"},
    {"id": "both", "concept": "cb", "priority": 1, "action": "prebuild", "detail": "d"},
    {"id": "tool-x", "concept": "t", "priority": 1, "action": "tool", "detail": "d"},
    {"id": "p1-gap", "concept": "c1", "priority": 1, "action": "prebuild", "detail": "d"}]) + "\n```\n")
saved_root = prebuild.ROOT
try:
    prebuild.ROOT = AT
    order = [t["id"] for t in prebuild.targets(cfg)]
    assert order == ["both", "p1-gap", "hand-a", "p2-gap"], order          # tool gaps never become prebuild targets
    assert prebuild.targets(cfg)[0]["goal"] == "own fields"                # a TARGETS entry keeps its own fields
finally:
    prebuild.ROOT = saved_root
assert {"Evtx", "olefile", "dnfile", "sqlite3", "ordlookup", "mutagen"} <= prebuild.ALLOWED_IMPORTS
assert "open" in prebuild.BANNED_CALLS
for lane in ("warmups", "mobile-android", "binary-reverse-engineering", "script-analysis", "metadata-forensics"):
    if (ROOT / f"reference/coverage/{lane}.md").exists():
        assert "NOT-YET-SEEN concepts of this lane" in orchestrate.technique_log(lane), lane
assert "reference/coverage/{lane}.md" in (ROOT / "hctf/prompts/ratchet_log.md").read_text()
print("ok  B3/D1 prebuild: 5 lanes, atlas-ranked targets (tools excluded), DFIR libs allowed (open() still banned); "
      "atlas cues inlined; ratchet_log refreshes the atlas")

# FIX16 (pre-D16 review): cut-off start resent; ctx in localize threads; overlay filter; no_clock; feed; train drop
sent16 = []
saved16 = ht._post
try:
    replies = iter([{"error": "unjudged_transport", "detail": "IncompleteRead"}, {"attempt_id": "A", "answer_ids": ["x"]}])
    ht._post = lambda payload, timeout=None: (sent16.append(payload), next(replies))[1]
    assert ht._post_once({"op": "start", "challenge": "c"})["attempt_id"] == "A" and len(sent16) == 2
finally:
    ht._post = saved16
seen_lane = []
saved16 = (ht._post, ht._playbook_alts, ht._vocab)
try:
    ht._vocab = lambda: {}
    ht._playbook_alts = lambda aid, cur: (seen_lane.append(ht._CTX.lane), ["good"])[1]
    ht._post = lambda payload, timeout=None: ({"result": "accepted", "remaining": 3}
                                              if (payload.get("answers") or {}).get("s1.f-x") == "good"
                                              else {"result": "incorrect"})
    ht._CTX.lane = "warmups"
    out = {}
    ht._localize("c", {"s1.f-x": "bad"}, {"s1": {"s1.f-x": "bad"}}, {"s1": {"result": "incorrect"}}, {"deadline": None}, out)
    assert seen_lane == ["warmups"] and out["fixed"] == {"s1.f-x": "good"}, (seen_lane, out)
finally:
    ht._post, ht._playbook_alts, ht._vocab = saved16
    ht._CTX.lane = None
print("ok  FIX16 hb_timed: cut-off start/retry resent; localize threads keep the attempt's lane (playbook alternatives)")

LV2 = TMP / "live2"
saved_cdir = cli.cdir
try:
    cli.cdir = lambda cid: LV2
    LV2.mkdir(parents=True, exist_ok=True)
    (LV2 / "last_timed.json").write_text(json.dumps({"attempt_id": "M1"}))
    big = {f"set1.f{i}": "v" for i in range(800)}
    (LV2 / "submissions.jsonl").write_text("\n".join(json.dumps(x) for x in (
        {"attempt": "M1", "answers": big, "kind": "accepted", "probe": True},
        {"attempt": "M1", "answers": {"set2.k": "ok"}, "kind": "accepted", "harness": "race"},
        {"attempt": "M1", "answers": {"set1.live": "yes"}, "kind": "accepted"})) + "\n")
    assert workers.live_overlay("b/mastery") == {"attempt": "M1", "answers": {"set1.live": "yes"}}
finally:
    cli.cdir = saved_cdir
noclock = {"result": "incorrect", "attempt_id": "M1", "deadline": None, "no_clock": True, "verified": {"x": "1"},
           "localize_complete": False}
assert orchestrate._cut_short(noclock) and orchestrate._live_fields(noclock, [("a", "b")], {}) == ["a"]
print("ok  FIX16 overlay: only the live worker's own small submits (no probe/race batches); no_clock = resumable")

from hctf import feed as _feed  # noqa: E402
fd = _feed.Feed()
fd.process("21:00:00 5 chains (15 challenge modes), slots local=5")
fd.process("21:02:00 [warmups-day-16/mastery] live-answer worker on attempt M1 for 2 field(s), racing the generalize")
got = fd.process("21:03:00 [warmups-day-16/mastery] passed by the live-answer worker (attempt M1)") or []
assert any("solved" in x and "live-answer" in x for x in got), got
print("ok  FIX16 feed: live-answer start shown, its pass counts as solved")

assert "time" in prebuild.ALLOWED_IMPORTS
saved_root = prebuild.ROOT
try:
    prebuild.ROOT = AT
    (AT / "reference/coverage/x.md").write_text("## Readiness gaps\n```json\n" + json.dumps([
        {"id": "hi", "concept": "c", "priority": "high", "action": "prebuild", "detail": "d"}]) + "\n```\n")
    assert prebuild.atlas_gaps(cfg)[0]["priority"] == 1
finally:
    prebuild.ROOT = saved_root
print("ok  FIX16 prebuild: `time` allowed; an LLM-written priority 'high' -> 1")

# train: an adopted case the generalize could not fix is removed (never rides into tomorrow's copy)
saved = (paths.CHALLENGES, compound.ROOT, paths.ROOT)
saved_o = (_o.chain_for, _o.mutation_probe)
try:
    shutil.rmtree(TR, ignore_errors=True)
    paths.CHALLENGES, compound.ROOT, paths.ROOT = TR / "challenges", TR, TR
    chal(14, "warmups-old", "True")
    today = chal(15, "warmups-new", "False")
    _o.mutation_probe = lambda sdir, mc=None, timeout=90: ("", [], {})

    class NoFix:
        def generalize(self, base, wrong=None, fixed=None, diag=None):
            pass
    _o.chain_for = lambda base, pools, gov: NoFix()
    from hctf import solvers as _solvers  # noqa: E402
    saved_ts = _solvers.test_solver
    _solvers.test_solver = lambda sdir: [{"case": p.name, "ok": False} for p in (Path(sdir) / "cases").glob("compound-*")]
    rep = train.run(15, log=lambda m: None, rounds=1, deadline=time.time() + 600)
    _solvers.test_solver = saved_ts
    assert rep["warmups-day-15"].get("dropped") == ["compound-d14-single_solve"], rep
    assert not (today / "solver/cases/compound-d14-single_solve").exists()
finally:
    paths.CHALLENGES, compound.ROOT, paths.ROOT = saved
    _o.chain_for, _o.mutation_probe = saved_o
print("ok  FIX16 train: adopted cases still failing after the rounds are removed")

# FIX16b: prebuild drain pass + xhigh prebuild workers; effort report renders
calls16 = []
saved16 = (prebuild.default_deadline, prebuild.lock_holder)
try:
    import datetime as _dt
    prebuild.default_deadline = lambda now=None: _dt.datetime.now() + _dt.timedelta(hours=5)
    prebuild.lock_holder = lambda: None
    prebuild.launch_background(16, log=lambda m: None, popen=lambda cmd, **kw: calls16.append(cmd))
    cmd = calls16[0][2]
    if prebuild.PARALLEL:   # one process: every lane at once, each draining its ranked list
        assert cmd.count("hctf.cli prebuild") == 1 and "--parallel" in cmd and f"--n {prebuild.DRAIN_N}" in cmd, cmd
    else:
        assert cmd.count("hctf.cli prebuild") == 2 * len(prebuild.AUTO_LANES) and f"--n {prebuild.DRAIN_N}" in cmd
        assert cmd.index("--n 5") < cmd.index(f"--n {prebuild.DRAIN_N}")  # first pass (n/lane) before the drain
finally:
    prebuild.default_deadline, prebuild.lock_holder = saved16
assert prebuild.EFFORT == "high" and prebuild.TIMEOUT == 25 * 60
envs = []
saved16 = (prebuild.pending, prebuild.snapshot, prebuild.gate, prebuild.restore, prebuild.regress_baseline,
           prebuild.LOCK, prebuild._render, prebuild.STATE, prebuild.LOGDIR)
try:
    prebuild.LOCK, prebuild.STATE, prebuild.LOGDIR = TMP / "pb.lock", TMP / "pb-state.json", TMP / "pblogs"
    prebuild.pending = lambda lane, cfg, n, only=None: [{"id": "t1", "goal": "g"}]
    prebuild.snapshot = lambda cfg: (TMP / "snap").mkdir(exist_ok=True) or (TMP / "snap")
    prebuild.regress_baseline = lambda lane: {}
    prebuild._render = lambda *a, **k: "prompt"
    prebuild.gate = lambda *a, **k: (False, ["stub"])
    prebuild.restore = lambda *a, **k: True
    prebuild.run("warmups", n=1, budget_usd=99, log=lambda m: None,
                 runner=lambda d, stage, prompt, env, timeout, stop: (envs.append(env), (0, str(TMP / "w.log")))[1])
finally:
    (prebuild.pending, prebuild.snapshot, prebuild.gate, prebuild.restore, prebuild.regress_baseline,
     prebuild.LOCK, prebuild._render, prebuild.STATE, prebuild.LOGDIR) = saved16
assert envs and envs[0].get("HCTF_X_EFFORT") == "high", envs
from hctf import effort_report  # noqa: E402
assert "no day99.log" in effort_report.report(99, [TMP])
print("ok  FIX16b prebuild: n/lane pass then drain every pending target; workers at high (HCTF_PREBUILD_EFFORT), 25 min; effort report")

# PARALLEL prebuild: lanes run at once on PRIVATE lib/ copies; merged + gated one at a time on the real tree
import threading as _th  # noqa: E402
PR = TMP / "par"
(PR / "lib").mkdir(parents=True)
(PR / "tests" / "data").mkdir(parents=True)
for nm in ("lane_a", "lane_b", "lane_c", "shared"):
    (PR / "lib" / f"{nm}.py").write_text(f"NAME = {nm!r}\n")
keys = ("ROOT", "RUN", "SNAP", "PRIV", "LOCK", "STATE", "LOGDIR", "pending", "_render", "LANES", "history_costs")
saved_pb = {k: getattr(prebuild, k) for k in keys}
inflight, peak = [0], [0]
lk = _th.Lock()


def stub_runner(d, stage, prompt, env, timeout, stop):
    binds = dict((dst, src) for src, dst in json.loads(env["HCTF_SANDBOX_BINDS"]))
    priv_lib = Path(binds[str(PR / "lib")])
    with lk:
        inflight[0] += 1
        peak[0] = max(peak[0], inflight[0])
    time.sleep(0.4)                       # overlap the three workers
    lane = env["HCTF_LANE"]
    if lane == "la":
        (priv_lib / "lane_a.py").write_text("NAME = 'lane_a'\nEXTRA = 1\n")
        with prebuild.GATE_LOCK:      # another lane's candidate lands in the REAL tree meanwhile (its gate): not ours
            (PR / "lib" / "lane_b.py").write_text("NAME = 'lane_b_candidate'\n")
            prebuild._TREE["sig"] = prebuild._tree_sig()
    elif lane == "lb":
        (priv_lib / "lane_b.py").write_text("import subprocess\nNAME = 'lane_b'\n")      # AST gate must revert it
    else:
        (priv_lib / "shared.py").write_text("NAME = 'hijacked'\n")                         # outside its allowlist
    with lk:
        inflight[0] -= 1
    return 0, str(TMP / "w.log")


try:
    prebuild.ROOT, prebuild.RUN = PR, PR / ".run"
    prebuild.SNAP, prebuild.PRIV = PR / ".run/snap", PR / ".run/pb-lane"
    prebuild.LOCK, prebuild.STATE, prebuild.LOGDIR = PR / ".run/lock", PR / ".run/state.json", PR / ".run/logs"
    prebuild.history_costs = lambda: []
    prebuild.pending = lambda lane, cfg, n, only=None: [{"id": f"{lane}-t1"}]
    prebuild._render = lambda *a, **k: "prompt"
    prebuild.LANES = {ln: {"writable": (f"lib/lane_{ln[1]}.py", f"tests/data/{ln}/"), "snapshot": ("lib", "tests/data"),
                           "gate": (), "requires": ()} for ln in ("la", "lb", "lc")}
    res = prebuild.run_parallel(lanes=["la", "lb", "lc"], n=1, budget_usd=99, log=lambda m: None, runner=stub_runner)
finally:
    for k, v in saved_pb.items():
        setattr(prebuild, k, v)
by = {r["lane"]: r for r in res}
assert peak[0] == 3, peak                                                # all three lanes worked at the same time
assert by["la"]["ok"] and "EXTRA = 1" in (PR / "lib/lane_a.py").read_text()
assert not by["lb"]["ok"] and "import subprocess" not in (PR / "lib/lane_b.py").read_text(), by["lb"]
assert by["la"]["ok"], by["la"]       # la not blamed for the other lane's file that changed in the real tree
assert not by["lc"]["ok"] and "outside the allowlist" in by["lc"]["reasons"][0]
assert (PR / "lib/shared.py").read_text() == "NAME = 'shared'\n" and not (PR / ".run/pb-lane").exists()
print("ok  parallel prebuild: 3 lanes at once on private lib/ copies; good kept, AST-bad reverted, outside write "
      "rejected; real tree only holds gated work")

# BIND SURVIVES RESTORE: a parallel worker's bwrap bind on lib/ must survive a gate restore (in-place sync). The old
# rmtree + copytree detached the bind (Linux >= 3.18) and the worker wrote into the real tree (2026-10-16 leak).
import shutil as _shu  # noqa: E402
import subprocess as _sp  # noqa: E402
if _shu.which("bwrap") and workers.WORKER_SANDBOX:
    def bind_case(restorer):
        B = Path(tempfile.mkdtemp(dir=str(ROOT / ".run")))
        real, priv, snapd = B / "real_lib", B / "priv_lib", B / "snap_lib"
        for d in (real, priv, snapd):
            d.mkdir()
            (d / "a.py").write_text("orig\n")
        (snapd / "a.py").write_text("restored\n")
        cmd = workers.sandboxed(["bash", "-c", f"sleep 1.2; echo w > {real}/w.txt"], "prebuild", [(priv, real)])
        proc = _sp.Popen(cmd)
        time.sleep(0.4)
        restorer(snapd, real)
        proc.wait(10)
        leaked, kept_private = (real / "w.txt").exists(), (priv / "w.txt").exists()
        restored = (real / "a.py").read_text()
        _shu.rmtree(B, ignore_errors=True)
        return leaked, kept_private, restored

    def old_restore(src, dst):
        _shu.rmtree(dst)
        _shu.copytree(src, dst)
    leaked, private, restored = bind_case(prebuild._sync_dir)
    assert not leaked and private and restored == "restored\n", (leaked, private, restored)
    old_leak = bind_case(old_restore)[0]
    print(f"ok  bind survives an in-place restore (old rmtree+copytree leaked: {old_leak})")
else:
    print("skip bind-survives-restore: no bwrap sandbox here")

shutil.rmtree(TMP, ignore_errors=True)
print("ALL PASS")
