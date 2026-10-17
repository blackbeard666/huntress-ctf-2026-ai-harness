"""Day 17 prep: closing the remaining gap to ~2 min (plan: GM round trips, new labels, mode chaining). Offline.
- grouptest k-ary waves: 1 wrong field of ~1100 in 3 waves, <= 12 in flight.
- labels.resolve_parallel: an isolated ENUM field resolves from the contract's accepted_values in one parallel wave,
  ranked by the value the GM accepted for a sibling field + label hints; derived fields only try `extra` values.
- the worker's `hctf submit` waits for the race's bisect (race_bisect.json) instead of a second one.
- untimed Mastery never waits for the today-probe.
- hb_timed: prefetched TT bytes (same attempt) are reused, not re-downloaded; a no-clock attempt's per-set breakdown
  runs in parallel; in-attempt localization ranks an enum's accepted_values / sibling-accepted values / hints and
  fixes the field; gzip replies are decoded; daemon submit replies are trimmed to the request's ids.

Run:  source bin/env.sh && python3 tests/test_day17_prep.py      (exit 0 = all pass)
"""
import gzip
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, grouptest, labels  # noqa: E402
sys.path.insert(0, str(ROOT / "hctf"))
import hb_timed as H  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="hctf-d17-"))
_cdir = cli.cdir
cli.cdir = lambda cid: TMP / cid

# ------------------------------------------------------------------------------------------------ k-ary waves
ids = [f"{f}-{i}" for f in "abcdefg" for i in range(157)]
ans = {a: "v" for a in ids}
peak, cur, lk = [0], [0], threading.Lock()


def probe(g, wrong):
    with lk:
        cur[0] += 1
        peak[0] = max(peak[0], cur[0])
    time.sleep(0.01)
    with lk:
        cur[0] -= 1
    return "bad" if wrong & set(g) else "ok"


bad, st = grouptest.find_rejected(lambda g: probe(g, {"e-3"}), ans)
assert bad == {"e-3"} and st["waves"] <= 3 and peak[0] <= grouptest.CONC, (st, peak)
five = {"e-3", "e-17", "e-88", "e-140", "c-5"}
bad, st5 = grouptest.find_rejected(lambda g: probe(g, five), ans)
assert bad == five and st5["waves"] <= 6, st5
print(f"ok  grouptest k-ary: 1 wrong of {len(ids)} in {st['waves']} waves ({st['probes']} probes), 5 wrong in "
      f"{st5['waves']}; <= {peak[0]} in flight")

# ------------------------------------------------------------------------------------------------ enum resolution
EV = ["percent", "delayed", "call_double", "for_indirect"]
qs = [{"id": f"batch-{r}-expansion", "answer_format": {"kind": "enum", "accepted_values": EV}}
      for r in ("relay", "chain", "impact", "uploader", "launcher", "downloader")]
qs.append({"id": "batch-relay-url", "answer_format": {"kind": "exact_text"}})
truth = {q["id"]: "percent" for q in qs[:5]}
truth["batch-downloader-expansion"] = "call_double"
truth["batch-relay-url"] = "https://x.example/a"
(TMP / "s1").mkdir()
(TMP / "s1" / "start.json").write_text(json.dumps({"attempt_id": "A1", "answer_ids": [q["id"] for q in qs],
                                                   "questions": qs}))
gm_calls = []


def fake_call(cid, op, *a, **k):
    sub = json.loads(a[1])
    gm_calls.append(sub)
    time.sleep(0.02)
    conf = set(cli.confirmed_answers(cid))
    if any(truth.get(x) != v for x, v in sub.items()):
        return {"http": 200, "body": {"result": "incorrect"}}
    done = conf | set(sub)
    if done >= set(truth):
        return {"http": 200, "body": {"result": "CORRECT"}}
    return {"http": 200, "body": {"result": "accepted", "remaining": len(truth) - len(done), "accepted_ids": sorted(sub)}}


_ocall = cli.call
cli.call = fake_call
try:
    # the GM already accepted `percent` for a sibling (relay) -> ranked first for the 4 isolated `delayed` fields
    cli.submit("s1", {"batch-relay-expansion": "percent", "batch-downloader-expansion": "call_double",
                      "batch-relay-url": "https://x.example/a"}, force=True, probe=True)
    wrong = {f"batch-{r}-expansion": "delayed" for r in ("chain", "impact", "uploader", "launcher")}
    gm_calls.clear()
    t0 = time.time()
    won = labels.resolve_parallel("s1", wrong, harness="race")
    assert won == {k: "percent" for k in wrong}, won
    assert cli.is_complete("s1"), "all fields banked -> the attempt is CORRECT without the LLM"
    firsts = [c for c in gm_calls if list(c.values()) == ["percent"]]
    assert len(firsts) == 4, gm_calls
    print(f"ok  labels.resolve_parallel: 4 isolated enum fields -> 'percent' (sibling-accepted first), attempt CORRECT, "
          f"{len(gm_calls)} probes in {time.time() - t0:.2f}s")
    # ranking from hints (no sibling evidence): call_double -> for_indirect seen before
    hints = {"-expansion": {"call_double": {"for_indirect": 6}}}
    r = labels.ranked_alternatives("s1", "set4.batch-uploader-expansion", "call_double", hints=hints)
    assert r[0] == "for_indirect" and "call_double" not in r, r
    # a derived field gets only `extra` values (no vocabulary guesses)
    (TMP / "s2").mkdir()
    (TMP / "s2" / "start.json").write_text(json.dumps({"attempt_id": "A2", "answer_ids": ["x-sha256"],
                                                       "questions": [{"id": "x-sha256",
                                                                      "answer_format": {"kind": "exact_text"}}]}))
    truth = {"x-sha256": "bb"}
    gm_calls.clear()
    won = labels.resolve_parallel("s2", {"x-sha256": "aa"}, extra={"x-sha256": ["cc", "bb"]})
    assert won == {"x-sha256": "bb"} and len(gm_calls) == 2, (won, gm_calls)
    print("ok  labels: hints rank call_double -> for_indirect first; a derived field only tries other solvers' values")
finally:
    cli.call = _ocall

# ------------------------------------------------------------------------------------------------ one bisect / attempt
(TMP / "s3").mkdir()
(TMP / "s3" / "start.json").write_text(json.dumps({"attempt_id": "A3", "answer_ids": ["a"], "questions": [{"id": "a"}]}))
cli.save("s3", "race_bisect.json", {"attempt": "A3", "pid": os.getpid(), "started": time.time(), "done": False})


def finish():
    time.sleep(1.0)
    cli.save("s3", "race_bisect.json", {"attempt": "A3", "pid": os.getpid(), "done": True, "wrong": ["a"],
                                        "resolved": {}})


threading.Thread(target=finish, daemon=True).start()
t0 = time.time()
m = cli._await_race("s3", max_wait=10)
assert m and m.get("done") and 0.8 < time.time() - t0 < 5, (m, time.time() - t0)
cli.save("s3", "race_bisect.json", {"attempt": "OTHER", "pid": os.getpid(), "started": time.time(), "done": False})
assert cli._await_race("s3", max_wait=1) is None           # another attempt's marker: no wait
print("ok  worker `hctf submit` waits for the race's bisect of THIS attempt (one bisector per attempt)")

# ------------------------------------------------------------------------------------------------ untimed probe wait
from concurrent.futures import Future  # noqa: E402
from hctf import orchestrate as O  # noqa: E402
ch = object.__new__(O.Chain)
ch.lane, ch.base = "warmups", "w"
ch._today_fut = Future()          # never finishes
ch._today_kind = lambda: "codec"
t0 = time.time()
assert ch._today_pre_result("w/mastery", wait=False) == {} and time.time() - t0 < 0.5
print("ok  untimed Mastery: an unfinished today-probe is not waited for (was up to 30 s)")

# ------------------------------------------------------------------------------------------------ hb_timed attempt
SOLV = ROOT / ".run" / "tmp" / "d17solver" / "chal" / "solver"
SOLV.mkdir(parents=True, exist_ok=True)
(SOLV / "solve.py").write_text("print('{}')\n")
CAP = "c" * 64
EVQ = {"kind": "enum", "accepted_values": EV}
q2 = [{"id": "batch-uploader-expansion", "artifact": "e.zip -> x.cmd", "answer_format": EVQ},
      {"id": "batch-uploader-url", "artifact": "e.zip -> x.cmd", "answer_format": {"kind": "exact_text"}}]
aids = ["set1.batch-uploader-expansion", "set1.batch-uploader-url", "set2.batch-uploader-expansion",
        "set2.batch-uploader-url"]
body = {"attempt_id": "T1", "deadline": None, "answer_ids": aids, "questions": q2 * 2,
        "download": f"/?op=download&capability={CAP}"}
gt = dict(zip(aids, ["percent", "u1", "for_indirect", "u2"]))
solver_out = dict(zip(aids, ["percent", "u1", "call_double", "u2"]))
state = {"conf": set(), "subs": [], "dl": 0}


def fake_post(payload, timeout=None):
    if payload.get("op") in ("start", "retry"):
        return dict(body)
    a = payload.get("answers") or {}
    state["subs"].append(dict(a))
    time.sleep(0.05)
    if any(gt.get(k) != v for k, v in a.items()):
        return {"result": "incorrect"}
    state["conf"] |= set(a)
    rem = len(gt) - len(state["conf"])
    return {"result": "CORRECT"} if rem == 0 else {"result": "accepted", "remaining": rem, "accepted_ids": sorted(a)}


class FakePool:
    def fresh(self):
        return self


def fake_bytes(cap, timeout=20):
    state["dl"] += 1
    return b"PK\x05\x06" + b"\0" * 18


class Res:
    returncode, stderr = 0, ""

    def __init__(self, out):
        self.stdout = json.dumps(out)


saved = (H._post, H._pool, H._get_bytes, H.SOLVER)
H._post, H._pool, H._get_bytes = fake_post, (lambda: FakePool()), fake_bytes
H.SOLVER = lambda path, args, env, timeout: Res(solver_out)
os.environ["HCTF_LABEL_HINTS"] = json.dumps({"-expansion": {"call_double": {"for_indirect": 3}}})
try:
    cid = "d17-binary/time_trial"
    adir = H.HW / ".run" / "tmp-timed" / "d17_binary_time_trial"
    adir.mkdir(parents=True, exist_ok=True)
    for f in adir.glob("*"):
        f.unlink()
    (adir / "e.zip").write_bytes(b"prefetched")
    (adir / ".prefetch.json").write_text(json.dumps({"attempt_id": "T1", "files": ["e.zip"]}))
    out = H.run_attempt(cid, str(SOLV.relative_to(H.HW)), op="start")
    assert out.get("prefetched") and state["dl"] == 0 and (adir / "e.zip").read_bytes() == b"prefetched", out
    assert out["result"] == "correct" and out.get("breakdown") == "parallel", out
    assert out["fixed"] == {"set2.batch-uploader-expansion": "for_indirect"}, out.get("fixed")
    tries = [x["set2.batch-uploader-expansion"] for x in state["subs"] if list(x) == ["set2.batch-uploader-expansion"]]
    assert [t for t in tries if t != "call_double"][0] == "for_indirect", tries     # the hinted value first
    print("ok  hb_timed: prefetched TT bytes reused (0 downloads); per-set breakdown in parallel (no clock); the wrong "
          "enum field fixed in-attempt with the hinted value first -> CORRECT")
    # a different attempt id: the prefetch is ignored, the runner downloads itself
    (adir / ".prefetch.json").write_text(json.dumps({"attempt_id": "OLD", "files": ["e.zip"]}))
    state.update(conf=set(), subs=[], dl=0)
    out = H.run_attempt(cid, str(SOLV.relative_to(H.HW)), op="start")
    assert not out.get("prefetched") and state["dl"] == 1, (out.get("prefetched"), state["dl"])
    print("ok  hb_timed: a prefetch of another attempt is ignored (fresh download)")
finally:
    H._post, H._pool, H._get_bytes, H.SOLVER = saved
    os.environ.pop("HCTF_LABEL_HINTS", None)

# ------------------------------------------------------------------------------------------------ gzip + daemon trim
from hctf import gm as G  # noqa: E402
raw = json.dumps({"result": "ok", "q": "x" * 5000}).encode()
assert G._gunzip(gzip.compress(raw), "gzip") == raw and G._gunzip(raw, None) == raw
assert G._gz({}, {"op": "status"})["Accept-Encoding"] == "gzip" and "Accept-Encoding" not in G._gz({}, {"op": "download"})
from hctf import hb_daemon as D  # noqa: E402


class TrimPool:
    def request(self, *a, **k):
        return 200, json.dumps({"result": "accepted", "remaining": 3,
                                "accepted_ids": [f"f{i}" for i in range(1000)]}).encode()


class FakeH:
    @staticmethod
    def _pool():
        return TrimPool()

    @staticmethod
    def _auth(h=None):
        return h or {}

    @staticmethod
    def _refusal(*a):
        return False


env = D._gm_call(FakeH, {"kind": "submit", "cid": "c", "answers": {"f1": "a", "f7": "b", "zz": "c"}})
assert env["body"]["accepted_ids"] == ["f1", "f7"], env["body"]
print("ok  gzip: requested on API calls (never on artifact bytes) and decoded; daemon submit replies trimmed to the "
      "request's ids (was the attempt's cumulative list)")

cli.cdir = _cdir
print("ALL PASS")
