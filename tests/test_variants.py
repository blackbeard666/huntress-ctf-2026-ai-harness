"""Variant-robustness checks (organizer, Day 8: Time Trial / Mastery hand out "new, dynamic variations/mutations ...
new unseen effects"). Offline: no GM / no Homebase / no workers.

Run:  source bin/env.sh && .venv/bin/python tests/test_variants.py      (exit 0 = all pass)
"""
import datetime as dt
import hashlib
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import hb_timed, mutate, orchestrate  # noqa: E402

NOTE = b"\xef\xbb\xbfcase notes\nline two\n"
GENERIC = '''import argparse, hashlib, json, sys
from lib.common import find_artifact, load_contract
ap = argparse.ArgumentParser(); ap.add_argument("--contract"); ap.add_argument("--artifacts"); a = ap.parse_args()
contract, pairs = load_contract(a.contract)
out = {}
for aid, q in pairs:
    try:
        data = find_artifact(a.artifacts, q.get("artifact") or "")
        fam = aid.split(".")[-1].rsplit("-", 1)[-1]
        v = {"sha256": hashlib.sha256(data).hexdigest(), "size": str(len(data)),
             "bom": "yes" if data[:3] == b"\\xef\\xbb\\xbf" else "no"}.get(fam)
    except Exception as e:
        print(aid, e, file=sys.stderr); v = None
    if v is not None:
        out[aid] = v
print(json.dumps(out))
'''
# keyed to the single: the delivery's file name, the question POSITIONS, one set; any unknown question raises
FRAGILE = '''import argparse, hashlib, json, zipfile
ap = argparse.ArgumentParser(); ap.add_argument("--contract"); ap.add_argument("--artifacts"); a = ap.parse_args()
c = json.load(open(a.contract))
data = zipfile.ZipFile(a.artifacts + "/evidence.zip").read("note.txt")
vals = [hashlib.sha256(data).hexdigest(), str(len(data)), "yes" if data[:3] == b"\\xef\\xbb\\xbf" else "no"]
ids = c["answer_ids"]
assert len(ids) <= 3, "unexpected question"
print(json.dumps({aid: vals[i] for i, aid in enumerate(ids)}))
'''


def toy_solver(code):
    sdir = Path(tempfile.mkdtemp()) / "chal" / "solver"
    case = sdir / "cases" / "single_solve"
    (case / "artifacts").mkdir(parents=True)
    with zipfile.ZipFile(case / "artifacts" / "evidence.zip", "w") as z:
        z.writestr("note.txt", NOTE)
    qs = [{"id": f"note-{f}", "question": f"What is the {f} of note.txt?", "artifact": "evidence.zip -> note.txt",
           "answer_format": {"kind": "exact_text"}, "normalization": "trim"} for f in ("sha256", "size", "bom")]
    contract = {"mode": "single_solve", "questions": qs, "answer_ids": [q["id"] for q in qs],
                "sha256": hashlib.sha256((case / "artifacts" / "evidence.zip").read_bytes()).hexdigest()}
    (case / "contract.json").write_text(json.dumps(contract))
    (case / "expected.json").write_text(json.dumps({"note-sha256": hashlib.sha256(NOTE).hexdigest(),
                                                    "note-size": str(len(NOTE)), "note-bom": "yes"}))
    (sdir / "solve.py").write_text(code)
    return sdir


# 1) the mutator writes answer-invariant cases: same expected answers (per set for mastery-shape), renamed delivery
sdir = toy_solver(GENERIC)
out = Path(tempfile.mkdtemp())
s = mutate.make(sdir, out)
names = {m["mutation"] for m in s["made"]}
assert names == {"renamed", "reordered", "subset", "unknown-field", "mastery-shape"}, names   # no `wrapped`: already a zip
ms = json.loads((out / "mutation-mastery-shape" / "contract.json").read_text())
assert ms["answer_ids"][0] == "set1.note-sha256" and ms["answer_ids"][-1] == "set2.note-bom", ms["answer_ids"]
assert json.loads((out / "mutation-mastery-shape" / "expected.json").read_text())["set2.note-size"] == str(len(NOTE))
rn = json.loads((out / "mutation-renamed" / "contract.json").read_text())
assert "evidence.zip" not in json.dumps(rn["questions"]) and (out / "mutation-renamed" / "artifacts").iterdir()
print("ok  mutate.make: 5 answer-invariant mutations, mastery-shape = 2 sets, renamed contract follows the file")

# 2) a generic solver survives every HARD mutation; a solver keyed to the single's name/positions does not
g = mutate.probe(sdir, Path(tempfile.mkdtemp()))
assert g["base_ok"] and all(r["ok"] for r in g["results"] if r["hard"]), [r for r in g["results"] if not r["ok"]]
txt, hard = mutate.report(g)
assert not hard, hard
f = mutate.probe(toy_solver(FRAGILE), Path(tempfile.mkdtemp()))
bad = {r["mutation"] for r in f["results"] if not r["ok"] and r["hard"]}
assert f["base_ok"] and {"renamed", "reordered", "unknown-field", "mastery-shape"} <= bad, bad
txt, hard = mutate.report(f)
assert len(hard) == len(bad) and "HARD `renamed`" in txt, txt
print(f"ok  mutate.probe: generic solver passes all HARD mutations; fragile one fails {sorted(bad)}")

# 3) carry-over pointers: an escalated Day 8 contract with d04-/d06- ids names Day 4/6's metadata solvers (all lanes)
d8 = ROOT / "challenges" / "day08" / "metadata-x" / "solver"
note = orchestrate.carry_over_note("metadata-forensics", d8, ["evidence-note-md5", "d04-jpeg-001-jpeg-sof-dimensions-pixels",
                                                              "set2.d06-pdf-001-pdf-header-version", "d08-new-001-x"])
assert "challenges/day04/metadata-picture-this/solver" in note and "day06/metadata-portable-deception" in note, note
assert "Day 8" not in note and orchestrate.carry_over_note("metadata-forensics", d8, ["evidence-note-md5"]) == ""
assert set(orchestrate.prior_solver_dirs("mobile-android", d8)) == {1, 2, 3, 4, 5, 6, 7}
print("ok  carry_over_note: dNN- ids from earlier days point at that day's same-lane solver; none for today's ids")

# 4) hb_timed partial submit: an incomplete solve still submits its answered fields (GM saves partial progress)
deadline = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
body = {"deadline": deadline}
calls = []
_orig_post = hb_timed._post


def fake(verdict):
    def post(payload, timeout=None):
        calls.append(payload)
        a = payload.get("answers") or {}
        return {"result": verdict(a), "remaining": 3}
    return post


try:
    hb_timed._post = fake(lambda a: "accepted")
    out = {}
    hb_timed._partial_submit("cid", {"set1.a": "1", "set2.a": "2"}, body, out)
    assert out["verified"] == {"set1.a": "1", "set2.a": "2"} and out["partial_submit"]["result"] == "accepted", out
    assert len(calls) == 1, calls
    calls.clear()
    hb_timed._post = fake(lambda a: "incorrect" if a.get("set2.b") == "bad" else "accepted")
    out = {}
    hb_timed._partial_submit("cid", {"set1.a": "1", "set2.a": "2", "set2.b": "bad"}, body, out)
    assert out["partial_wrong"] == [["set2.b", "bad"]], out
    assert out["verified"] == {"set1.a": "1", "set2.a": "2"} and "wrong" not in out, out
    calls.clear()

    def boom(payload, timeout=None):
        raise TimeoutError("no answer")
    hb_timed._post = boom
    out = {}
    hb_timed._partial_submit("cid", {"a": "1"}, body, out)
    assert out["partial_submit"]["result"] == "no_answer" and "verified" not in out, out
finally:
    hb_timed._post = _orig_post
print("ok  hb_timed._partial_submit: accepted subset verified; wrong ones localized under partial_wrong; never resent")

# 5) the skeleton calls fallback() only when answer() found nothing
sk = (ROOT / "hctf" / "templates" / "solve_skeleton.py").read_text()
assert "def fallback(" in sk and "if v is None:" in sk
print("ok  solve_skeleton: per-field fallback hook")
# 6) pre-attempt gate: HARD mutation misses -> mutation-* cases adopted + ONE generalize with mutation_pre, before any
#    timed attempt; no misses -> no generalize
from hctf import timed  # noqa: E402
fragile = toy_solver(FRAGILE)
fr = mutate.probe(fragile, Path(tempfile.mkdtemp()))
ftxt, fhard = mutate.report(fr)
ch = object.__new__(orchestrate.Chain)
ch.base, ch.entries, ch.sdir, ch.lane = "b", {"mastery": {"id": "b/mastery"}}, fragile, "metadata-forensics"
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
gen = []
patches = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (timed, "run"): lambda cid, sdir, log=None, op="start": "correct",
    (timed, "last_result"): lambda cid: None,
    (orchestrate.Chain, "generalize"): lambda self, cid, wrong=None, fixed=None, diag=None: gen.append(diag),
}
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    ch._single_slow, ch._pre_attempt_done = None, False
    ch._family_pre_result = lambda: ("", [])
    ch._mutation_pre_result = lambda wait=True: (ftxt, fhard)
    assert ch.timed_stage("mastery")
    assert len(gen) == 1 and gen[0].get("mutation_pre") == ftxt, gen
    adopted = sorted(p.name for p in (fragile / "cases").glob("mutation-*"))
    assert adopted and "mutation-renamed" in adopted and not list((fragile / "cases").glob("*/mutation.json")), adopted
    gen.clear()
    ch._pre_attempt_done = False
    ch._mutation_pre_result = lambda wait=True: ("", [])
    assert ch.timed_stage("mastery") and gen == []
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
print(f"ok  pre-attempt gate: {len(adopted)} HARD mutation miss(es) adopted + ONE generalize (mutation_pre); none -> none")
# 7) window fixes: questions paired by id (not position); solver budget = clock left AFTER the download
qs7 = [{"id": "b", "normalization": "exact"}, {"id": "a", "normalization": "trim"}, {"id": "marker"}]
pm = hb_timed._paired(["a", "b", "slot0_marker"], qs7)
assert pm["a"]["normalization"] == "trim" and pm["b"]["normalization"] == "exact" and pm["slot0_marker"]["id"] == "marker"
soon = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=6)).isoformat().replace("+00:00", "Z")
assert 4.0 <= hb_timed._solve_budget({"deadline": soon}, 30) <= 4.6
assert hb_timed._solve_budget({}, None) == 28.5 and hb_timed._solve_budget({"deadline": deadline[:0]}, 1) == 2
print("ok  hb_timed: questions paired by id; solve budget from the clock left after downloading")
# 8) start/retry: a hung GM call is cut at START_TIMEOUT and resent (idempotent before the clock), never left at 20 s
seen = []


def flaky(payload, timeout=None):
    seen.append(timeout)
    if len(seen) < 3:
        raise TimeoutError("hung")
    return {"attempt_id": "x"}


try:
    hb_timed._post = flaky
    assert hb_timed._post_start({"op": "start", "challenge": "c"}) == {"attempt_id": "x"}
    assert seen == [hb_timed.START_TIMEOUT] * 3, seen
    seen.clear()
    hb_timed._post = lambda payload, timeout=None: (seen.append(timeout), (_ for _ in ()).throw(TimeoutError()))[1]
    try:
        hb_timed._post_start({"op": "start", "challenge": "c"})
        raise AssertionError("must raise after the last try")
    except TimeoutError:
        assert len(seen) == 3
finally:
    hb_timed._post = _orig_post
print(f"ok  hb_timed._post_start: {hb_timed.START_TIMEOUT:g} s per call, resent up to 3x, then raises")

# 9) speed gate first: a slow single never waits on the mutation probe (it probes the solver about to be rewritten)
import concurrent.futures as _cf  # noqa: E402
ch2 = object.__new__(orchestrate.Chain)
ch2.base, ch2.sdir = "b", fragile
ch2._mut_pre_fut = _cf.Future()          # still running
assert ch2._mutation_pre_result(wait=False) == ("", [])
ch2._mut_pre_fut.set_result(("txt", ["c"], {}))
assert ch2._mutation_pre_result(wait=False) == ("txt", ["c"])
print("ok  mutation pre-probe: never blocks the speed gate; a finished result is still used")

# 10) a Mastery BUNDLE saved under set 1's container name: set 1 resolves to the inner container, not the bundle
#     (D7 metadata Mastery failed set1.evidence-note-filename this way in 2/2 blind replays)
from lib.common import container_by_sha, find_artifact  # noqa: E402
bd = Path(tempfile.mkdtemp())
inner = {}
for k in (1, 2):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("evidence-note.txt", f"note {k}")
    inner[f"evidence-0{k}.zip"] = b.getvalue()
with zipfile.ZipFile(bd / "evidence-01.zip", "w") as z:     # how hb_timed saves the one bundle download
    for n, data in inner.items():
        z.writestr(n, data)
bc = {"artifacts": [{"filename": "x-mastery.zip", "kind": "bundle",
                     "sha256": hashlib.sha256((bd / "evidence-01.zip").read_bytes()).hexdigest()}],
      "questions": [{"artifact": "evidence-01.zip"}, {"artifact": "evidence-02.zip -> evidence-note.txt"}]}
assert container_by_sha(bd, bc, "evidence-01.zip") is None
assert find_artifact(bd, "evidence-01.zip") == inner["evidence-01.zip"]
assert find_artifact(bd, "evidence-02.zip") == inner["evidence-02.zip"]
assert find_artifact(bd, "evidence-01.zip -> evidence-note.txt") == b"note 1"
assert find_artifact(bd, "evidence-02.zip -> evidence-note.txt") == b"note 2"
cd = Path(tempfile.mkdtemp())                                 # a container holding a same-named FILE stays itself
with zipfile.ZipFile(cd / "evidence.zip", "w") as z:
    z.writestr("evidence.zip", b"inner")
    z.writestr("readme.txt", b"x")
assert find_artifact(cd, "evidence.zip")[:2] == b"PK"
print("ok  bundle saved under set 1's name: each set's container resolves to its own inner zip")

# 11) present_only keeps set 2 of a bundled Mastery (its container is a member of the bundle), still drops a set whose
#     delivery is really missing
from hctf import timed as _timed  # noqa: E402
pc = {"answer_ids": ["set1.a", "set2.a"],
      "questions": [{"artifact": "evidence-01.zip -> n.txt"}, {"artifact": "evidence-02.zip -> n.txt"}]}
assert _timed.present_only(pc, bd, {"set1.a": "1", "set2.a": "2"}) == {"set1.a": "1", "set2.a": "2"}
md = Path(tempfile.mkdtemp())
(md / "evidence-01.zip").write_bytes(inner["evidence-01.zip"])     # set 2's delivery never fetched
assert _timed.present_only(pc, md, {"set1.a": "1", "set2.a": "2"}) == {"set1.a": "1"}
print("ok  present_only: bundled set 2 kept, a genuinely missing delivery still dropped")
print("ALL PASS")
