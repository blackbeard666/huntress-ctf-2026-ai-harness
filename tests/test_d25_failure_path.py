"""D25 post-mortem Track C (failure-path latency), offline: fake GM state, no network, no workers.
- C1 generalize: the worker launches BEFORE the baseline replay finishes (it runs on the snapshot in a thread); the
     accept step joins it; failing cases reach the worker's inbox; byte-identical cases run the solver once
- C2 Stop gate: an unverified case answered completely with no GM-rejected value passes; the green watcher targets it
- C3 live-answer cap lifted for one field shape; the lib racer never sends a GM-rejected value (warmups candidates on
     the real D25 Mastery case)
- C4 hb_timed: no label retries on free-text formats, per-set events reach a local poller in order, the live answer
     starts once every bad set is localized; B4.2 ensure_started adopts the attempt's sha-verified local bytes

Run:  source bin/env.sh && python3 tests/test_d25_failure_path.py      (exit 0 = all pass)
"""
import contextlib
import hashlib
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, hb_timed, inbox, libracer, orchestrate as orch, solvers, timed, workers  # noqa: E402

failures = []
TMP = Path(tempfile.mkdtemp(prefix="d25c-", dir=str(ROOT / ".run")))


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


QUIET = {(orch, "say"): lambda *a, **k: None}

# a toy solver: answers from out.json beside it, one line per run appended to runs.log
SOLVE = '''import json, sys
from pathlib import Path
here = Path(__file__).resolve().parent
with open(here / "runs.log", "a") as f:
    f.write("run\\n")
print(json.dumps(json.loads((here / "out.json").read_text())))
'''


def toy_solver(name, out):
    chal = TMP / "day25" / f"warmups-{name}"
    sdir = chal / "solver"
    (sdir / "cases").mkdir(parents=True)
    (chal / "meta.json").write_text(json.dumps({"lane": "warmups", "name": name}))
    (sdir / "solve.py").write_text(SOLVE)
    (sdir / "out.json").write_text(json.dumps(out))
    return sdir


def add_case(sdir, name, ids, art=b"blob", expected=None, rejected=None):
    c = sdir / "cases" / name
    (c / "artifacts").mkdir(parents=True)
    (c / "artifacts" / "blob-01.txt").write_bytes(art)
    (c / "contract.json").write_text(json.dumps({"answer_ids": ids, "questions": [{"id": i} for i in ids]}))
    (c / "expected.json").write_text(json.dumps(expected or {}))
    if rejected is not None:
        (c / "gm_feedback.json").write_text(json.dumps({"rejected": rejected, "require_complete": True}))
    return c


def runs(sdir):
    p = sdir / "runs.log"
    return len(p.read_text().splitlines()) if p.exists() else 0


# ---------------------------------------------------------------- C1 dedupe + C2 gate
sd = toy_solver("gate", {"a": "1", "b": "2"})
add_case(sd, "auto-mastery-x", ["a", "b"], expected={"a": "1", "b": "2"})
add_case(sd, "mastery-x", ["a", "b"], expected={"a": "1", "b": "2"})
add_case(sd, "variant-mastery-x", ["a", "b"], rejected={"a": ["9"]})        # unverified twin of auto-mastery-x
add_case(sd, "variant-mastery-y", ["a", "b"], art=b"other", rejected={"a": ["9"]})   # unverified, no twin
res = solvers.test_solver(sd, timeout=20)
by = {r["case"]: r for r in res}
check("C1 byte-identical cases run the solver once (4 cases -> 2 runs)", runs(sd) == 2, runs(sd))
check("C1 every case is still judged on its own expected / feedback",
      by["auto-mastery-x"]["ok"] and by["mastery-x"]["ok"] and not by["variant-mastery-x"]["ok"]
      and by["variant-mastery-x"]["unverified"], res)
check("C1 results keep case-name order", [r["case"] for r in res] == sorted(by), [r["case"] for r in res])
check("C1 an unverified duplicate follows its verified twin (dup_of)", by["variant-mastery-x"].get("dup_of") == "auto-mastery-x",
      by["variant-mastery-x"])
check("C2 reject-free: complete + no rejected value -> passes the gate though unverified",
      by["variant-mastery-y"]["reject_free"] and solvers.gate_ok(by["variant-mastery-y"]), by["variant-mastery-y"])
check("C2 every case passes the gate", all(solvers.gate_ok(r) for r in res), [(r["case"], r.get("gate_ok")) for r in res])
with patched({(solvers, "GATE_REJECT_FREE", ): False}):
    check("C2 kill switch: HCTF_GATE_REJECT_FREE=0 -> the old gate (unverified never passes)",
          not solvers.gate_ok({k: v for k, v in by["variant-mastery-y"].items() if k != "gate_ok"}))
(sd / "out.json").write_text(json.dumps({"a": "9", "b": "2"}))          # reproduces the GM-rejected value
r2 = {r["case"]: r for r in solvers.test_solver(sd, timeout=20)}
check("C2 a reproduced GM-rejected value fails the gate", not solvers.gate_ok(r2["variant-mastery-y"])
      and r2["variant-mastery-y"]["rejected_hits"] == 1, r2["variant-mastery-y"])
(sd / "out.json").write_text(json.dumps({"a": "3"}))                    # incomplete
r3 = {r["case"]: r for r in solvers.test_solver(sd, timeout=20)}
check("C2 an incomplete answer set fails the gate", not solvers.gate_ok(r3["variant-mastery-y"]), r3["variant-mastery-y"])
with patched({(solvers, "CASE_DEDUPE"): False}):
    n0 = runs(sd)
    solvers.test_solver(sd, timeout=20)
    check("C1 kill switch: HCTF_CASE_DEDUPE=0 -> one run per case", runs(sd) - n0 == 4, runs(sd) - n0)

# watcher sets + targets_pass
ws = orch.watch_sets(r2.values(), {}, "mastery", sd)
check("C2 watch_sets: the unverified case with GM rejections still reproduced is a reject-free target",
      ws[2] == {"variant-mastery-y"} and "variant-mastery-x" not in ws[2], ws)
(sd / "out.json").write_text(json.dumps({"a": "5", "b": "2"}))
check("C2 targets_pass(reject_free) -> True once complete with no rejected value",
      solvers.targets_pass(sd, set(), set(), timeout=20, reject_free={"variant-mastery-y"}))
(sd / "out.json").write_text(json.dumps({"a": "9", "b": "2"}))
check("C2 targets_pass(reject_free) -> False while a rejected value comes back",
      not solvers.targets_pass(sd, set(), set(), timeout=20, reject_free={"variant-mastery-y"}))

# the generalize green watcher goes green on a reject-free target (no verified target at all)
sd2 = toy_solver("watch", {"a": "9", "b": "2"})
add_case(sd2, "variant-mastery-z", ["a", "b"], rejected={"a": ["9"]})
ch = object.__new__(orch.Chain)
ch.base, ch.lane, ch.sdir, ch.root = "warmups-day-25", "warmups", sd2, sd2.parent
green, done = threading.Event(), threading.Event()
with patched({**QUIET, (orch, "GREEN_POLL"): 0.1, (orch, "GREEN_QUIET"): 0.2}):
    t = threading.Thread(target=ch._watch_green, args=(set(), set(), False, green, done, set(), None,
                                                     {"variant-mastery-z"}, None), daemon=True)
    t.start()
    time.sleep(0.6)
    (sd2 / "out.json").write_text(json.dumps({"a": "4", "b": "2"}))      # the "fix"
    os.utime(sd2 / "solve.py")                                          # solver code changed
    got = green.wait(10)
    done.set()
check("C2 green watcher: a reject-free unverified target ends the worker (no verified target needed)", got)

# ---------------------------------------------------------------- C1 async baseline in generalize()
sd3 = toy_solver("async", {"a": "1"})
add_case(sd3, "auto-mastery-q", ["a"], expected={"a": "1"})
add_case(sd3, "variant-mastery-q", ["a"], art=b"v", rejected={"a": ["1"]})   # still reproduces the rejected value
ch3 = object.__new__(orch.Chain)
ch3.base, ch3.pools, ch3.gov, ch3.only_modes = "warmups-day-25", None, mock.Mock(allow_timed=lambda: True), None
ch3.lane, ch3.name, ch3.sdir, ch3.root = "warmups", "t", sd3, sd3.parent
cdir3 = TMP / "cdir3"
cdir3.mkdir()
launched, base_done_at, events = {}, {}, []
real_ts = solvers.test_solver


def slow_ts(sdir, **k):
    out = real_ts(sdir, **k)
    if Path(sdir).name == ".generalize-snapshot":
        time.sleep(1.5)
        base_done_at["t"] = time.time()
        events.append("baseline")
    return out


def run_worker(cid, stage, prompt, timeout, stop=None, **k):
    launched["t"] = time.time()
    launched["prompt"] = prompt
    events.append("worker")
    time.sleep(0.3)


ch3.run_worker = run_worker
with patched({**QUIET, (orch, "set_state"): lambda *a, **k: None,
              (orch, "ensure_case_and_test"): lambda *a, **k: (True, None),
              (orch.solvers, "test_solver"): slow_ts, (orch.timed, "last_result"): lambda cid: {},
              (orch.remote, "gm_transport"): lambda: "local", (orch.cli, "cdir"): lambda cid: cdir3,
              (orch, "STOP_WHEN_READY"): False}):
    t0 = time.time()
    ch3.generalize("warmups-day-25/mastery", wrong=[("a", "7")], fixed={}, diag={})
check("C1 the generalize worker launched before the baseline replay finished",
      launched.get("t") and base_done_at.get("t") and launched["t"] < base_done_at["t"] and events[0] == "worker",
      events)
check("C1 the accept step joined the baseline (pre-worker passing cases known) and accepted the unchanged solver",
      getattr(ch3, "_baseline", None) == {"auto-mastery-q"} and not (sd3.parent / ".generalize-snapshot").exists(),
      getattr(ch3, "_baseline", None))
msgs = inbox.texts(cdir3)
check("C1 failing cases found by the async baseline reach the worker inbox",
      any("variant-mastery-q" in m and "BASELINE REPLAY" in m for m in msgs), msgs)
check("C1 the prompt says the replay is running beside the worker", "replaying" in launched.get("prompt", ""))

# the E1b duel: started once the async baseline names a target, copying the PRE-worker snapshot
duel_calls = []


def fake_duel(cid, prompt, targets, fill, need_fast, green, **kw):
    duel_calls.append({"targets": set(targets), "fill": set(fill), "rfree": set(kw.get("rfree") or ()),
                       "src": kw.get("src"), "snap_exists": bool(kw.get("src") and Path(kw["src"]).exists())})
    return None


def run_worker_long(cid, stage, prompt, timeout, stop=None, **k):
    launched["t2"] = time.time()
    time.sleep(2.5)


ch3.run_worker, ch3._maybe_start_gen_duel, ch3._expect_untimed = run_worker_long, fake_duel, lambda: True
with patched({**QUIET, (orch, "set_state"): lambda *a, **k: None,
              (orch, "ensure_case_and_test"): lambda *a, **k: (True, None),
              (orch.solvers, "test_solver"): slow_ts, (orch.timed, "last_result"): lambda cid: {},
              (orch.remote, "gm_transport"): lambda: "local", (orch.cli, "cdir"): lambda cid: cdir3,
              (orch, "STOP_WHEN_READY"): True}):
    ch3.generalize("warmups-day-25/mastery", wrong=[("a", "1")], fixed={}, diag={})
check("C1+C2 the generalize duel starts after the async baseline, on the reject-free target, from the snapshot",
      len(duel_calls) == 1 and duel_calls[0]["rfree"] == {"variant-mastery-q"} and duel_calls[0]["snap_exists"]
      and str(duel_calls[0]["src"]).endswith(".generalize-snapshot"), duel_calls)

# a stale baseline thread never feeds a later generalize: join without one is a no-op
ch3._baseline = {"x"}
ch3._gen_base = None
ch3._gen_baseline_join()
check("C1 no async baseline -> _gen_baseline_join leaves _baseline alone", ch3._baseline == {"x"})

# ---------------------------------------------------------------- C3a live cap
uni = [f"set{i}.message" for i in range(1, 124)]
mixed = [f"set{i}.message" for i in range(1, 62)] + [f"set{i}.other" for i in range(1, 63)]
check("C3a 123 fields of one shape -> live answer allowed", orch.live_fields_ok(uni))
check("C3a 123 fields of two shapes -> over the cap", not orch.live_fields_ok(mixed))
check("C3a <= LIVE_MAX_FIELDS mixed -> allowed; none -> not", orch.live_fields_ok(mixed[:50]) and not orch.live_fields_ok([]))
with patched({(orch, "LIVE_UNIFORM_MAX"): 0}):
    check("C3a HCTF_LIVE_UNIFORM_MAX=0 -> the plain cap", not orch.live_fields_ok(uni))

# ---------------------------------------------------------------- C3b lib racer
sent = []
state = {"conf": {}, "complete": False}
ATT = "att-1"


def fake_submit(cid, ans, force=False, probe=False, harness=None, **k):
    sent.append(dict(ans))
    good = {"f1": "good1", "f2": "good2", "f3": "good3"}
    if all(good.get(a) == v for a, v in ans.items()):
        state["conf"].update(ans)
        if set(state["conf"]) >= set(good):
            state["complete"] = True
            return "correct", {}, []
        return "accepted", {}, []
    return "incorrect", {}, []


def fake_bisect(cid, ans, **k):
    good = {"f1": "good1", "f2": "good2", "f3": "good3"}
    bad = set()
    for a, v in ans.items():
        if good.get(a) == v:
            state["conf"][a] = v
        else:
            bad.add(a)
        sent.append({a: v})
    return bad


subs = TMP / "racer"
subs.mkdir()
(subs / "submissions.jsonl").write_text(json.dumps({"attempt": ATT, "kind": "incorrect", "answers": {"f3": "bad3b"}}) + "\n")
last = {"attempt_id": ATT, "no_clock": True, "wrong": [["f1", "bad1"], ["f2", "bad2"]],
        "localize_tried": {"f2": ["bad2b"]}}
cands = {"f1": ["bad1", "good1"], "f2": ["bad2b", "worse2", "good2"], "f3": ["bad3b", "good3"]}
pairs = {(cli, "submit"): fake_submit, (cli, "_bisect_rejected"): fake_bisect,
         (cli, "confirmed_answers"): lambda cid, att=None: dict(state["conf"]),
         (cli, "is_complete"): lambda cid: state["complete"], (cli, "cdir"): lambda cid: subs,
         (cli, "load"): lambda cid, name: {"attempt_id": ATT}, (cli, "attempt_id"): lambda b: (b or {}).get("attempt_id")}
with patched(pairs):
    rc = libracer.LibRacer("w/mastery", "warmups", last, ["f1", "f2", "f3"], TMP, TMP / "c.json", log=lambda m: None,
                           candidates=cands)
    rc.start().thread.join(10)
rejected = {"f1": {"bad1"}, "f2": {"bad2", "bad2b"}, "f3": {"bad3b"}}
resent = [(a, v) for s in sent for a, v in s.items() if v in rejected.get(a, set())]
check("C3b the lib racer never sends a value the GM rejected before (wrong / localize_tried / single-field log)",
      not resent, resent)
check("C3b after an isolated rejection it moves to the next candidate and passes the attempt",
      rc.passed and state["complete"], (rc.note, sent))
values_sent = [(a, v) for s in sent if len(s) > 1 for a, v in s.items()]
check("C3b batches never repeat a value it already sent", len(values_sent) == len(set(values_sent)), values_sent)
evt = threading.Event()
rc.link(evt)
check("C3b a passed racer sets a linked generalize stop at once", evt.is_set())

state.update(conf={}, complete=False)
sent.clear()
with patched({**pairs, (cli, "load"): lambda cid, name: {"attempt_id": "another"}}):
    rc2 = libracer.LibRacer("w/mastery", "warmups", last, ["f1"], TMP, TMP / "c.json", log=lambda m: None,
                            candidates=cands)
    rc2.start().thread.join(10)
check("C3b start.json on another attempt -> nothing is sent", not sent and not rc2.passed, sent)

# warmups candidates on the real D25 Mastery case (raw lib decode = the GM's answers)
# (the D25 case lives only in the main checkout until the prebuild commits it; D24's is committed)
case = next((c for c in (ROOT / "challenges" / "day25" / "warmups-you-have-a-point" / "solver" / "cases" / "auto-mastery-0b1ae1d0",
                         Path.home() / "huntress-2026" / "challenges" / "day25" / "warmups-you-have-a-point" / "solver"
                         / "cases" / "auto-mastery-0b1ae1d0",
                         ROOT / "challenges" / "day24" / "warmups-string-theory" / "solver" / "cases" / "auto-mastery-39a9fb2c")
             if (c / "contract.json").exists()), None)
if case is not None:
    print(f"    (real case: {case.relative_to(case.parents[4])})")
    c = json.loads((case / "contract.json").read_text())
    exp = json.loads((case / "expected.json").read_text())
    ids = list(exp)[:6]
    out, err = libracer.decode_candidates("warmups", case / "contract.json", case / "artifacts", ids, timeout=60)
    hits = sum(1 for a in ids if (out.get(a) or [None])[0] == exp[a])
    check("C3b warmups: lib.decode on the raw D25 Mastery blobs ranks the GM's slug first (subprocess decode)",
          not err and hits == len(ids), (err, hits, {a: (out.get(a), exp[a]) for a in ids}))
else:
    print("skip C3b warmups real-case check (no D25 fixture)")

# ---------------------------------------------------------------- C4 hb_timed / events
ff = hb_timed._free_text_format
check("C4 exact_text / integer / sha256 / 0x-hex are free text",
      ff({"kind": "exact_text"}) and ff({"kind": "integer"})
      and ff({"kind": "pattern", "syntax": "exactly 64 lowercase hexadecimal characters; no prefix"})
      and ff({"kind": "pattern", "syntax": "lowercase hexadecimal with a 0x prefix; preserve the field's required zero padding"}))
check("C4 label-ish patterns and enums keep their label retries",
      not ff({"kind": "enum"})
      and not ff({"kind": "pattern", "syntax": "executable-header machine architecture label or its equivalent decimal or "
                                               "hexadecimal code"})
      and not ff({"kind": "pattern", "syntax": "ELF or PE executable-container label"}) and not ff({"kind": "json"}))

evf = TMP / "evt.json"
os.environ["HCTF_EARLY_EVENT_FILE"], os.environ["HCTF_EARLY_GENERALIZE"] = str(evf), "1"
try:
    hb_timed._CTX.on_event = None
    out = {"cid": "c", "attempt_id": "att", "submitted": {"x": "y" * 50}}
    hb_timed._event("per_set", out, slim=True, per_set={"set1": {"result": "incorrect"}}, bad_sets=["set1"])
    hb_timed._event("set_localized", out, slim=True, set="set1", set_wrong=[["set1.a", "v"]])
    lines = [json.loads(x) for x in Path(str(evf) + "l").read_text().splitlines()]
    check("C4 hb_timed appends every event to the local log, in order, slim (no answers)",
          [x["event"] for x in lines] == ["per_set", "set_localized"] and all("submitted" not in x for x in lines), lines)
finally:
    del os.environ["HCTF_EARLY_EVENT_FILE"], os.environ["HCTF_EARLY_GENERALIZE"]

seen, env = [], {}
stop = workers._local_event_poller("x/mastery-c4", env, seen.append)
log = Path(env["HCTF_EARLY_EVENT_FILE"] + "l")
log.write_text(json.dumps({"event": "solved"}) + "\n" + json.dumps({"event": "per_set"}) + "\n")
time.sleep(0.8)
with open(log, "a") as f:
    f.write(json.dumps({"event": "set_localized"}) + "\n")
for _ in range(30):
    if len(seen) >= 3:
        break
    time.sleep(0.1)
stop.set()
check("C4 the local poller delivers every event once, in order", [x["event"] for x in seen] == ["solved", "per_set",
                                                                                                "set_localized"], seen)
log.unlink(missing_ok=True)

# early live answer: starts once every bad set is localized, with the union of their wrong fields
tdir = TMP / "tdir"
tdir.mkdir()
tc = {"attempt_id": "att9", "answer_ids": ["set1.a", "set2.b"],
      "questions": [{"id": "set1.a", "artifact": "delivery 1: e.zip"}, {"id": "set2.b", "artifact": "delivery 2: e.zip"}]}
(tdir / "contract.json").write_text(json.dumps(tc))
(tdir / "delivery 1: e.zip").write_bytes(b"1")
(tdir / "delivery 2: e.zip").write_bytes(b"2")
ch4 = object.__new__(orch.Chain)
ch4.base, ch4.lane, ch4.sdir, ch4.root = "b", "binary-reverse-engineering", sd, sd.parent
started = []
ch4._start_live = lambda cid, last, fields, wrong, fixed: started.append((last, fields)) or SimpleLive(last)


class SimpleLive:
    def __init__(self, last):
        self.attempt, self.done = last["attempt_id"], threading.Event()


saved = []
with patched({**QUIET, (orch.cli, "save"): lambda cid, name, body: saved.append(name)}):
    ch4._early_kw("b/mastery")
    base = {"attempt_id": "att9", "deadline": None, "local": str(tdir)}
    ch4._early_event("b/mastery", {**base, "event": "per_set", "bad_sets": ["set1", "set2"]})
    ch4._early_event("b/mastery", {**base, "event": "set_localized", "set": "set1", "set_wrong": [["set1.a", "x"]]})
    first = list(started)
    ch4._early_event("b/mastery", {**base, "event": "set_localized", "set": "set2", "set_wrong": [["set2.b", "y"]]})
    ch4._early_event("b/mastery", {**base, "event": "set_localized", "set": "set2", "set_wrong": [["set2.b", "y"]]})
check("C4 the early live answer waits for every bad set, then starts ONCE on the union of wrong fields",
      not first and len(started) == 1 and sorted(started[0][1]) == ["set1.a", "set2.b"] and "start.json" in saved,
      (first, started))
live = ch4._early_live_take({"attempt_id": "att9"})
check("C4 the blocked path adopts the early live answer of the same attempt", live is not None and live.attempt == "att9")
started.clear()
with patched(QUIET):
    ch4._early_kw("b/mastery")
    clocked = {"attempt_id": "att9", "deadline": "2026-10-25T13:00:00Z", "local": str(tdir)}
    ch4._early_event("b/mastery", {**clocked, "event": "per_set", "bad_sets": ["set1"]})
    ch4._early_event("b/mastery", {**clocked, "event": "set_localized", "set": "set1", "set_wrong": [["set1.a", "x"]]})
check("C4 a clocked attempt never gets an early live answer", not started)

# ---------------------------------------------------------------- B4.2 ensure_started adopts local bytes
cd5 = TMP / "cd5"
cd5.mkdir()
td5 = TMP / "td5"
td5.mkdir()
blob = b"x" * 1000
sha = hashlib.sha256(blob).hexdigest()
body = {"attempt_id": "att5", "artifacts": [{"download": "/download/" + "a" * 64, "sha256": sha}],
        "questions": [{"id": "q", "artifact": "evidence.zip -> m"}], "answer_ids": ["q"]}
(td5 / "contract.json").write_text(json.dumps(body))
plan = cli._planned_downloads(body)
(td5 / plan[0][0]).write_bytes(blob)
with patched({(cli, "cdir"): lambda cid: cd5, (timed, "timed_dir"): lambda cid: td5}):
    art = timed.adopt_local_bytes("c/mastery", body)
    man = json.loads((art / "manifest.json").read_text()) if art else {}
    check("B4.2 the attempt's sha-verified timed bytes are hard-linked into artifacts/<ts> with a manifest",
          art is not None and man.get("attempt") == "att5" and (cd5 / "artifacts" / "latest").resolve() == art.resolve()
          and os.stat(art / plan[0][0]).st_ino == os.stat(td5 / plan[0][0]).st_ino, man)
    (td5 / plan[0][0]).write_bytes(b"tampered")
    check("B4.2 a sha mismatch -> no adoption (the caller downloads)", timed.adopt_local_bytes("c/mastery", body) is None)
    check("B4.2 another attempt's bytes -> no adoption", timed.adopt_local_bytes("c/mastery", {**body, "attempt_id": "z"}) is None)

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAIL: {failures}'}")
sys.exit(1 if failures else 0)
