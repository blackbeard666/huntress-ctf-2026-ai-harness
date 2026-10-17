"""Fault-injection replay of the TIMED RUNNER against a local GM stand-in (hctf/replay_gm.py --timed, no real GM, no
Homebase, no LLM workers). Every scenario is a harness failure that set a day's T+ once; each must now end CORRECT
in-attempt (or in the verdict the orchestrator expects) with no manual step. Preflight runs this suite before every
drop (reference/PLAN_SUB2MIN.md P1).

  1. wrong labels on an untimed attempt -> localized + fixed in-attempt, CORRECT, no generalize      (D15/D16 shape)
  2. a submit reply cut off mid-body (IncompleteRead) after the GM judged it -> resent, CORRECT       (D15)
  3. a slow GM (per-submit latency) on a large multi-set contract -> CORRECT inside the scaled budget (D16)
  4. 429 rate limits on a quarter of the submits -> unjudged, never incorrect, CORRECT                (reviewer rule)
  5. a stalled first download -> CORRECT
  6. 503 training_rotation_invalid on the first starts -> error:start (no generalize), then CORRECT   (D8)
  7. Mastery before its Time Trial -> error:prerequisite; a prerequisite flap after the TT pass too    (rehearsal D16)
  8. a start on a passed mode hands back the FINISHED CORRECT body -> counted as the pass, no re-roll  (r9b / D16)
  9. a 1-variant pool -> retry = error:exhausted -> the untimed (practice) continuation passes          (D14)
 10. the runner's own deadline cuts localization short -> result carries the banked ids; op=resume finishes  (D16)
 11. release detection: status probe + lane-list race (offline fakes)

Run:  source bin/env.sh && python3 tests/test_fault_replay.py      (exit 0 = all pass)
"""
import json
import os
import random
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# runner knobs BEFORE the harness imports (module-level constants): local-only, modest budgets, real-GM re-roll rule
os.environ.update({
    "HCTF_AUTO_HOMEBASE": "0", "HCTF_UNTIMED_ON_HOMEBASE": "0", "HCTF_GM_VIA_DAEMON": "0", "HCTF_REPLAY_REROLL": "0",
    "HCTF_RUN_FOR_TIME": "auto", "HCTF_UNTIMED_BUDGET": "20", "HCTF_LOCALIZE_UNTIMED_S": "45",
    "HCTF_PREFETCH_TT": "0", "HCTF_RELEASE_CLOCK": "0",
})
os.environ.pop("HCTF_GM_TRANSPORT", None)
os.environ.pop("HUNTRESS_GAME_MASTER_URL", None)

WORK = ROOT / ".run" / "fault-replay"
shutil.rmtree(WORK, ignore_errors=True)
(WORK / "cdirs").mkdir(parents=True)
SOLVER = WORK / "solver"
SOLVER.mkdir()
(WORK / "meta.json").write_text(json.dumps({"lane": "script-analysis", "base": "fault-lane-day-99-replay"}))

LABELS = ["percent", "delayed", "call_double", "for_indirect"]
(SOLVER / "solve.py").write_text(f"""#!/usr/bin/env python3
import argparse, glob, json, os
LABELS = {LABELS!r}
ap = argparse.ArgumentParser(); ap.add_argument("--contract"); ap.add_argument("--artifacts")
a, _ = ap.parse_known_args()
c = json.load(open(a.contract))
ev = None
for p in glob.glob(os.path.join(a.artifacts, "*")):
    try:
        d = json.load(open(p))
    except Exception:
        continue
    if isinstance(d, dict) and "truth" in d:
        ev = d
out = {{}}
for aid in c.get("answer_ids") or []:
    v = (ev or {{}}).get("truth", {{}}).get(aid)
    if v is None:
        continue
    if aid in (ev or {{}}).get("wrong", []):
        v = LABELS[(LABELS.index(v) + 1) % len(LABELS)]
    out[aid] = v
print(json.dumps(out))
""")

BASE = "fault-lane-day-99-replay"
TT, MS = f"{BASE}/time_trial", f"{BASE}/mastery"


def make_case(name, n, sets, wrong_idx, seed, mode="time_trial"):
    d = WORK / "cases" / name
    d.mkdir(parents=True)
    rnd = random.Random(seed)
    qs, truth, ids = [], {}, []
    for i in range(n):
        s = i % sets + 1
        label = i % 3 == 0
        aid = f"set{s}.q{i:04d}-{'label' if label else 'value'}"
        if label:
            v, af = rnd.choice(LABELS), {"kind": "enum", "accepted_values": LABELS}
        else:
            v, af = f"val-{rnd.randrange(10 ** 6):06d}", {"kind": "string"}
        qs.append({"id": aid, "question": f"Question {i}?", "artifact": "evidence.json -> item",
                   "answer_format": af, "normalization": "trim", "set": s})
        truth[aid], ids = v, ids + [aid]
    wrong = [ids[i] for i in wrong_idx]
    assert all(w.endswith("-label") for w in wrong), wrong
    (d / "contract.json").write_text(json.dumps({"mode": mode, "name": f"fault {name}", "prompt": "p",
                                                 "questions": qs, "answer_ids": ids}))
    (d / "expected.json").write_text(json.dumps(truth))
    (d / "evidence.json").write_text(json.dumps({"truth": truth, "wrong": wrong}))
    return d


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class GM:
    def __init__(self, *flags, timed):
        self.port = free_port()
        self.events = WORK / f"events-{self.port}.jsonl"
        cmd = [sys.executable, str(ROOT / "hctf" / "replay_gm.py"), "--port", str(self.port), "--events",
               str(self.events), "--upstream", ""] + list(flags)
        for cid, dirs in timed.items():
            cmd += ["--timed", f"{cid}=" + ",".join(str(x) for x in dirs)]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", self.port), timeout=0.2).close()
                break
            except OSError:
                if self.p.poll() is not None:
                    raise RuntimeError(f"replay GM died: {self.p.stdout.read()[-800:]}")
                time.sleep(0.05)
        os.environ["HUNTRESS_GAME_MASTER_URL"] = f"http://127.0.0.1:{self.port}"

    def ev(self):
        try:
            return [json.loads(x) for x in self.events.read_text().splitlines() if x.strip()]
        except OSError:
            return []

    def stop(self):
        self.p.kill()
        self.p.wait()


from hctf import cli, timed, workers, orchestrate, remote  # noqa: E402

CT = WORK / "cdirs"
cli.cdir = lambda cid: (CT / re.sub(r"[^A-Za-z0-9]+", "_", cid)).mkdir(parents=True, exist_ok=True) or (
    CT / re.sub(r"[^A-Za-z0-9]+", "_", cid))
if hasattr(timed, "cli"):
    timed.cli.cdir = cli.cdir
# the solver dir is given relative to ROOT (hb_timed joins HW / solver_dir)
SREL = SOLVER.relative_to(ROOT)
LOG = []


def say(m):
    LOG.append(m)
    if os.environ.get("HCTF_TEST_VERBOSE"):
        print("   |", m)


def reset(cid):
    shutil.rmtree(cli.cdir(cid), ignore_errors=True)
    cli.cdir(cid)
    for p in (ROOT / ".run" / "timed-bank").glob(re.sub(r"[^A-Za-z0-9]+", "_", cid) + "*"):
        p.unlink()
    shutil.rmtree(ROOT / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", cid), ignore_errors=True)
    for p in SOLVER.glob("cases/*"):
        shutil.rmtree(p, ignore_errors=True)


def run(cid, op="start"):
    t0 = time.time()
    r = timed.run(cid, SOLVER, log=say, op=op)
    return r, timed.last_result(cid) or {}, time.time() - t0


def gm_calls(g, op):
    return [e for e in g.ev() if e.get("op") == op]


failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"ok  {name}")
    else:
        failures.append(name)
        print(f"FAIL {name}: {detail}"[:900])


cases = {
    "a": make_case("tt-a", 600, 3, [0, 201, 402], 1),
    "b": make_case("tt-b", 600, 3, [3, 300], 2),
    "big": make_case("tt-big", 1500, 5, [0, 303, 606, 909, 1212, 1497], 3),
    "ms": make_case("ms-a", 300, 2, [0, 150], 4, mode="mastery"),
    "ms2": make_case("ms-b", 300, 2, [3], 5, mode="mastery"),
}

# ------------------------------------------------------------------------------ 1. wrong labels, fixed in-attempt
reset(TT)
g = GM(timed={TT: [cases["a"], cases["b"]]})
try:
    res, last, dt = run(TT)
    check("1 untimed attempt with 3 wrong labels ends CORRECT in-attempt",
          res == "correct" and len(last.get("fixed") or {}) == 3 and last.get("localize_complete"),
          f"{res} fixed={last.get('fixed')} complete={last.get('localize_complete')} err={last.get('localize_error')}")
    check("1 ... via the in-attempt resubmit (no generalize involved)",
          last.get("resubmit_fixed") in ("completed_by_localize", "correct", "accepted") or last.get("result") == "correct",
          str(last.get("resubmit_fixed")))
    check("1 ... in a sane wall time", dt < 90, f"{dt:.1f}s")
    check("1 ... label hints learned for the next attempt",
          (WORK / "label_hints.json").exists() and "-label" in (WORK / "label_hints.json").read_text(),
          str((WORK / "label_hints.json").exists()))
finally:
    g.stop()

# ------------------------------------------------------------------------------ 2. cut-off replies
reset(TT)
g = GM("--fault-cut", "3", timed={TT: [cases["a"]]})
try:
    res, last, dt = run(TT)
    cuts = [e for e in g.ev() if e.get("result") == "fault_cut"]
    check("2 submit replies cut off mid-body: still CORRECT in-attempt",
          res == "correct" and cuts, f"{res} cuts={len(cuts)} err={last.get('localize_error')} unj={last.get('unjudged')}")
    check("2 ... cut replies were resent (unjudged_resends) or re-judged", (last.get("unjudged_resends") or 0) >= 1
          or len(gm_calls(g, "submit")) > len(cuts), f"resends={last.get('unjudged_resends')}")
finally:
    g.stop()

# ------------------------------------------------------------------------------ 3. slow GM, large contract
reset(TT)
g = GM("--fault-latency", "0.35", timed={TT: [cases["big"]]})
try:
    plan_t, _loc = workers.untimed_plan(TT)
    res, last, dt = run(TT)
    check("3 slow GM (0.35 s/submit) on 1500 fields x 5 sets x 6 wrong labels: CORRECT inside the scaled budget",
          res == "correct" and dt < plan_t, f"{res} {dt:.1f}s of {plan_t}s fixed={len(last.get('fixed') or {})} "
          f"err={last.get('localize_error')} waves={last.get('localize_waves')}")
finally:
    g.stop()

# ------------------------------------------------------------------------------ 4. 429 bursts
reset(TT)
g = GM("--fault-429", "0.25", "--seed", "7", timed={TT: [cases["a"]]})
try:
    res, last, dt = run(TT)
    n429 = len([e for e in g.ev() if e.get("result") == "fault_429"])
    check("4 a quarter of the submits rate-limited: never counted wrong, CORRECT",
          res == "correct" and n429 > 0, f"{res} 429s={n429} err={last.get('localize_error')}")
finally:
    g.stop()

# ------------------------------------------------------------------------------ 5. stalled download
reset(TT)
g = GM("--fault-dl-stall", "2.5", timed={TT: [cases["b"]]})
try:
    res, last, dt = run(TT)
    check("5 stalled first download: CORRECT", res == "correct" and (last.get("phases") or {}).get("download", 0) >= 2.0,
          f"{res} phases={last.get('phases')}")
finally:
    g.stop()

# ------------------------------------------------------------------------------ 6. start refused (503), then fine
reset(TT)
g = GM("--fault-start-503", "2", timed={TT: [cases["a"]]})
try:
    res1, last1, _ = run(TT)
    check("6 503 training_rotation_invalid on start: error:start (no generalize path)", res1 == "error:start",
          f"{res1} {str(last1.get('result'))[:80]} refused={last1.get('start_refused')}")
    res2, last2, _ = run(TT)
    check("6 ... the next start is served and passes", res2 == "correct", f"{res2}")
finally:
    g.stop()

# ------------------------------------------------------------------------------ 7+8. prerequisite, flap, finished body
reset(TT)
reset(MS)
g = GM("--fault-prereq-flap", "1", timed={TT: [cases["a"]], MS: [cases["ms"], cases["ms2"]]})
try:
    res, last, _ = run(MS)
    check("7 Mastery before its Time Trial: error:prerequisite", res == "error:prerequisite", f"{res} {last.get('result')}")
    res, last, _ = run(TT)
    check("7 ... Time Trial passes", res == "correct", res)
    res, last, _ = run(MS)
    check("7 ... one prerequisite flap after the pass is reported as such (the orchestrator re-checks the TT)",
          res == "error:prerequisite", f"{res}")
    res, last, _ = run(MS)
    check("7 ... Mastery then passes", res == "correct", f"{res} {last.get('result')} {last.get('detail')!s:.120}")
    res, last, _ = run(TT, op="start")
    check("8 a start on the passed Time Trial hands back the FINISHED CORRECT body: counted as the pass, no re-roll",
          res == "correct" and last.get("already_passed"), f"{res} already_passed={last.get('already_passed')} "
          f"starts={len(gm_calls(g, 'start'))}")
finally:
    g.stop()

# ------------------------------------------------------------------------------ 9. one-variant pool
reset(TT)
g = GM("--pool", "1", timed={TT: [cases["a"], cases["b"]]})
try:
    res, last, _ = run(TT)
    check("9 1-variant pool: the first attempt passes", res == "correct", res)
    res, last, _ = run(TT, op="retry")
    check("9 ... a retry for a fresh variant: error:exhausted (retry_variants_unavailable)", res == "error:exhausted",
          f"{res} {last.get('result')}")
    res, last, _ = run(TT, op="untimed")
    check("9 ... the untimed continuation (practice) passes", res == "correct" and last.get("untimed"),
          f"{res} {last.get('result')} practice={last.get('practice')}")
finally:
    g.stop()

# ------------------------------------------------------------------------------ 10. runner deadline -> resume
reset(TT)
g = GM("--fault-latency", "1.0", timed={TT: [cases["big"]]})
try:
    t0 = time.time()
    r = workers.run_timed(SOLVER, TT, op="start", timeout=22)
    out = timed.process_result(TT, SOLVER, r, log=say)
    last = timed.last_result(TT) or {}
    check("10 the runner's deadline cuts localization short: a result with the attempt id + banked ids, not a kill",
          out == "blocked" and last.get("attempt_id") and not last.get("localize_complete")
          and (last.get("per_set") or last.get("verified")),
          f"{out} {last.get('result')} att={str(last.get('attempt_id'))[:8]} complete={last.get('localize_complete')} "
          f"{time.time() - t0:.1f}s")
    check("10 ... the orchestrator reads it as cut short (reconnect, no generalize)", orchestrate._cut_short(last),
          json.dumps({k: last.get(k) for k in ('result', 'localize_complete', 'deadline', 'no_clock', 'untimed',
                                                'run_for_time', 'wrong', 'fixed')})[:300])
    import urllib.request
    urllib.request.urlopen(urllib.request.Request(os.environ["HUNTRESS_GAME_MASTER_URL"], method="POST",
                                                  data=json.dumps({"op": "_fault", "latency": 0.0}).encode(),
                                                  headers={"Content-Type": "application/json"}), timeout=5).read()
    att1 = last.get("attempt_id")
    res, last2, _ = run(TT, op="resume")
    check("10 ... op=resume reconnects to the SAME attempt and finishes it (bank overlay of the GM-accepted ids)",
          res == "correct" and last2.get("attempt_id") == att1 and last2.get("resumed_banked")
          and (last2.get("bank_overlay") or 0) >= 0,
          f"{res} att={str(last2.get('attempt_id'))[:8]} vs {str(att1)[:8]} resumed={last2.get('resumed_banked')} "
          f"overlay={last2.get('bank_overlay')}")
finally:
    g.stop()

# ------------------------------------------------------------------------------ 11. release detection (offline fakes)
_ogm, _orel = remote.gm, orchestrate.released_challenges
try:
    calls = []

    def fake_gm(*args, timeout=180):
        calls.append(args)
        if args[0] == "status":
            return {"http": 409 if args[1] == "warmups-day-17" else 404, "body": {"error": "start_required"}}
        if args[0] == "list" and "--lane" in args:
            ln = args[args.index("--lane") + 1]
            time.sleep(0.05)
            return {"http": 200, "body": {"challenges": [{"id": f"{ln}-day-17-x" + ("" if m == "single_solve" else f"/{m}"),
                                                          "lane": ln, "mode": m, "day": 17, "name": ln}
                                                         for m in ("single_solve", "time_trial", "mastery")]}}
        return {"http": 200, "body": {"challenges": []}}

    def slow_full(day=None):
        time.sleep(1.5)
        return [{"id": "late", "lane": "warmups", "mode": "single_solve", "day": 17, "name": "late"}]

    remote.gm, orchestrate.released_challenges = fake_gm, slow_full
    check("11 the status probe sees the drop", orchestrate._released_fast(17) and not orchestrate._released_fast(18))
    t0 = time.time()
    lanes = ["warmups", "metadata-forensics", "script-analysis", "binary-reverse-engineering", "mobile-android"]
    got = orchestrate._list_race(17, lanes, log=say)
    check("11 the lane-list race returns every lane's modes before the slow full list",
          len(got) == 15 and time.time() - t0 < 1.4 and len({c["id"] for c in got}) == 15,
          f"{len(got)} in {time.time() - t0:.2f}s")
    idx = json.loads((ROOT / "challenges" / "index.json").read_text())
    check("11 ... registers the folders like a list does", all(c["id"] in idx or c["id"].split("/")[0] in idx for c in got))
finally:
    remote.gm, orchestrate.released_challenges = _ogm, _orel
    # drop the fake day-17 registrations
    idx = json.loads((ROOT / "challenges" / "index.json").read_text())
    for k in list(idx):
        if k.endswith("-day-17-x"):
            idx.pop(k)
    (ROOT / "challenges" / "index.json").write_text(json.dumps(idx, indent=2, ensure_ascii=False, sort_keys=True))
    shutil.rmtree(ROOT / "challenges" / "day17", ignore_errors=True) if not any(
        (ROOT / "challenges" / "day17").glob("*/solver")) else None

# cleanup of the harness-side state this suite created
for cid in (TT, MS):
    shutil.rmtree(ROOT / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", cid), ignore_errors=True)
    for p in (ROOT / ".run" / "timed-bank").glob(re.sub(r"[^A-Za-z0-9]+", "_", cid) + "*"):
        p.unlink()
os.environ.pop("HUNTRESS_GAME_MASTER_URL", None)

if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall fault-replay scenarios passed")
