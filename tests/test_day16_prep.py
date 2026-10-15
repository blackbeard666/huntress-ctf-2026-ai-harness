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
saved = {k: getattr(ht, k) for k in ("_post_start", "_get_bytes")}
got_caps = []
try:
    ht._post_start = lambda payload, tries=3: body
    ht._get_bytes = lambda cap, timeout=20: (got_caps.append(cap), blob)[1]
    local = TMP / "tmp-timed" / "c_mastery"
    res = {"attempt_id": "A1", "result": "incorrect", "wrong": [["set2.b", "x"]], "deadline": None, "run_for_time": False}
    names = workers.public_pull(res, "c_mastery", local, "c/mastery")
    assert names == ["ev-02.zip"] and got_caps == ["2" * 64], (names, got_caps)          # only the failing set
    assert json.loads((local / "contract.json").read_text())["attempt_id"] == "A1" and (local / "result.json").exists()
    ht._post_start = lambda payload, tries=3: {**body, "attempt_id": "OTHER"}
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

shutil.rmtree(TMP, ignore_errors=True)
print("ALL PASS")
