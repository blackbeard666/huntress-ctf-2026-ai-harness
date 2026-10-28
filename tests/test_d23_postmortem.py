"""D23 post-mortem fixes (reference/D23_POSTMORTEM.md), offline: fake GM state, no network, no workers.
- #1a online label resolve: composite (`a|b|c`) labels and wrong-arity seeds are never probed; parallel + time-bounded
- #1b/#1e the blocked path: an attempt is not re-run on a solver the generalize left unchanged
- #1d generalize prompt: per-case diffs and the problem list are bounded
- #1f a live pass: unchanged code -> no replay; Mastery -> pre-worker solver kept without a replay
- #1g web Mastery: the compound-check wait ends as soon as the target is ready
- #2  contract-ahead: the runner's mid-attempt event reaches the orchestrator on LOCAL runs (file + poller), and the
      early generalize starts only on a large solver gap
- #3  list-order alternates; Python-literal -> compact JSON for json fields (cli + hb_timed + solver output)
- #4  hb_timed banks REJECTED values and a reconnect does not resubmit them; the resource sampler formats a line

Run:  source bin/env.sh && python3 tests/test_d23_postmortem.py      (exit 0 = all pass)
"""
import contextlib
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, hb_timed, labels, orchestrate, ressample, solvers, timed, workers  # noqa: E402

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


QUIET = {(orchestrate, "say"): lambda *a, **k: None}
TMP = Path(tempfile.mkdtemp(prefix="d23pm-", dir=str(ROOT / ".run")))

# ---------------------------------------------------------------- #1a composite labels / arity / parallel + bounded
check("#1a a `|`-joined value is composite", timed._composite_label("single|if_guard|percent"))
check("#1a a question asking for labels 'joined by |' is composite",
      timed._composite_label("x", {"question": "Recover ... as three labels joined by | in that order."}))
check("#1a a plain label is not composite", not timed._composite_label("percent", {"question": "Which expansion?"}))
check("#1a arity: a one-word seed never matches a 3-part value", not timed._same_arity("dot", "a|b|c"))
check("#1a arity: a 3-part seed matches a 3-part value", timed._same_arity("x|y|z", "a|b|c"))

probed = []


def fake_probe_first(cid, aid, cands, conc=None, harness="label", log=None, deadline=None):
    probed.append((aid, list(cands)))
    return cands[0] if aid == "lab-ok" else None


class _PB:
    @staticmethod
    def entry_for(lane, aid):
        return True

    @staticmethod
    def seed_candidates(lane, aid, solver_value=None):
        return ["dot", "bracket_literal", "declaration"] if "style" in aid else ["percent", "delayed"]


contract = {"answer_ids": ["batch-1-style", "lab-ok", "lab-no"],
            "questions": [{"id": "batch-1-style", "question": "three labels joined by | in that order"},
                          {"id": "lab-ok", "question": "expansion?"}, {"id": "lab-no", "question": "expansion?"}]}
import lib.playbook as _real_pb  # noqa: E402
with patched({(timed, "ensure_started"): lambda cid: ({"attempt_id": "a"}, None),
              (timed.cli, "load"): lambda cid, name: contract,
              (timed, "latest_artifacts"): lambda cid: TMP,
              (timed.solvers, "solve_contract"): lambda c, a, default_solver=None: (
                  {"batch-1-style": "single|if_guard|percent", "lab-ok": "x", "lab-no": "y"}, None),
              (labels, "load_vocab"): lambda: {}, (labels, "judged_wrong"): lambda cid, aid: set(),
              (labels, "probe_first"): fake_probe_first,
              (_real_pb, "entry_for"): _PB.entry_for, (_real_pb, "seed_candidates"): _PB.seed_candidates}):
    logs = []
    t0 = time.time()
    got = timed.resolve_labels_online("c/time_trial", TMP, ["batch-1-style", "lab-ok", "lab-no"], "script-analysis",
                                      log=logs.append)
    check("#1a the composite batch-style field is skipped (no one-word probes against it)",
          all(a != "batch-1-style" for a, _ in probed), probed)
    check("#1a plain label fields are still probed and an accept is returned", got == {"lab-ok"}, (got, probed))
    check("#1a the skip is logged", any("composite label" in x for x in logs), logs)
    check("#1a fast (parallel, no sequential sleeps)", time.time() - t0 < 5, time.time() - t0)

sent = []
with patched({(cli, "submit"): lambda *a, **k: (sent.append(a), ("incorrect", {}, []))[1],
              (cli, "is_complete"): lambda cid: False}):
    v = labels.probe_first("c", "f", ["a", "b"], conc=1, deadline=time.time() - 1)
    check("#1a probe_first: a passed deadline sends nothing", v is None and not sent, sent)
with patched({(cli, "submit"): lambda *a, **k: (sent.append(a), ("incorrect", {}, []))[1],
              (cli, "is_complete"): lambda cid: True}):
    sent.clear()
    labels.probe_first("c", "f", ["a", "b", "c"], conc=1)
    check("#1a probe_first: a mode that went CORRECT stops after the first wave", len(sent) == 1, sent)

# ---------------------------------------------------------------- #3 list-order alternates + JSON coercion
cd_order = '["room-18/item-5.log","cabinet-10/entry-6.txt","box-06/part-6.log"]'
alts = timed.list_alternates(cd_order, {"answer_format": {"kind": "json"}})
check("#3 a rejected JSON list: the SORTED compact list is the first alternate",
      alts and alts[0] == '["box-06/part-6.log","cabinet-10/entry-6.txt","room-18/item-5.log"]', alts)
check("#3 ... the original value itself is never re-proposed", cd_order not in alts, alts)
rep = "['room-18/item-5.log', 'box-06/part-6.log']"
alts2 = timed.list_alternates(rep, {"answer_format": {"kind": "json"}})
check("#3 a Python-repr list gets compact-JSON alternates (incl. the same order)",
      '["room-18/item-5.log","box-06/part-6.log"]' in alts2 and '["box-06/part-6.log","room-18/item-5.log"]' in alts2,
      alts2)
check("#3 hex set wants ascending: sorted first",
      timed.list_alternates('["0x0100000c","0x0000000c","0x00000007"]')[0] == '["0x00000007","0x0000000c","0x0100000c"]')
check("#3 a comma list (non-json field) keeps its separator", timed.list_alternates("b, a, c")[0] == "a, b, c")
check("#3 a scalar has no alternates", timed.list_alternates("percent") == [] and timed.list_alternates("12") == [])

jq = {"answer_format": {"kind": "json"}}
check("#3 cli: a Python-literal list in a json field -> compact JSON",
      cli._normalize("['a', 'b']", jq) == '["a","b"]', cli._normalize("['a', 'b']", jq))
check("#3 cli: valid JSON is never rewritten", cli._normalize('["a", "b"]', jq) == '["a", "b"]')
check("#3 cli: a non-json field is untouched", cli._normalize("['a', 'b']", {"answer_format": {"kind": "exact_text"}})
      == "['a', 'b']")
check("#3 hb_timed: same coercion on the timed runner", hb_timed._normalize("['a', 'b']", jq) == '["a","b"]')
check("#3 solver output: a list value -> compact JSON (never repr)",
      solvers.answer_str(["a", "b"]) == '["a","b"]' and hb_timed._answer_str({"k": 1}) == '{"k":1}'
      and solvers.answer_str(7) == "7" and solvers.answer_str("x") == "x")

# ---------------------------------------------------------------- #1d bounded prompt
big = {"case": "auto-mastery-1", "ok": False, "error": None, "unverified": False,
       "diff": {f"set1.f{i}": {"expected": "E" * 500, "got": None} for i in range(400)}}
line = orchestrate._case_problem(big)
check("#1d a 400-field diff becomes one bounded line", len(line) < 6000 and "+388 more field" in line, len(line))
tmo = dict(big, error="timeout after 8.0s")
line2 = orchestrate._case_problem(tmo)
check("#1d a replay timeout is named as such, no field dump", "timed out" in line2 and "EEEE" not in line2, line2[:200])
capped = orchestrate._cap_lines([f"  - {'x' * 1000}" for _ in range(100)], limit=10000)
check("#1d the problem list is capped with a count", len(capped) < 11500 and "more problem line" in capped, len(capped))

# ---------------------------------------------------------------- #1f code signature + accept after a live pass
a, b = TMP / "sa", TMP / "sb"
for d in (a, b):
    (d / "cases" / "c1").mkdir(parents=True)
    (d / "solve.py").write_text("print(1)\n")
    (d / "cases" / "c1" / "expected.json").write_text("{}")
(b / "cases" / "c1" / "expected.json").write_text('{"x": 1}')
check("#1f code signature ignores cases/", orchestrate._code_sig(a) == orchestrate._code_sig(b))
(b / "solve.py").write_text("print(2)\n")
check("#1f code signature sees a code edit", orchestrate._code_sig(a) != orchestrate._code_sig(b))


def live_chain(root):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base, ch.root = "script-analysis", "x", root
    ch.sdir = root / "solver"
    ch._snap_dir = lambda: root / ".solver-snapshot"
    return ch


R = TMP / "chain"
(R / "solver").mkdir(parents=True)
(R / "solver" / "solve.py").write_text("v = 1\n")
shutil.copytree(R / "solver", R / ".solver-snapshot")
replays = []
with patched({**QUIET, (orchestrate, "ROOT"): TMP, (orchestrate, "LIVE_ACCEPT_BG"): False}):  # D28 #5: bg accept
    ch = live_chain(R)
    ch._accept_or_restore = lambda cid, case_timeout=None: replays.append(case_timeout)
    ch._prefetch_mastery_start = lambda: replays.append("prefetch")
    orchestrate.Chain._accept_after_live(ch, "x/mastery", "mastery")
    check("#1f live pass + unchanged code: snapshot dropped, no replay",
          not (R / ".solver-snapshot").exists() and not replays, replays)
    shutil.copytree(R / "solver", R / ".solver-snapshot")
    (R / "solver" / "solve.py").write_text("v = 2  # unfinished worker edit\n")
    orchestrate.Chain._accept_after_live(ch, "x/mastery", "mastery")
    check("#1f live pass on Mastery: the pre-worker solver is back at once, edits set aside, no replay",
          (R / "solver" / "solve.py").read_text() == "v = 1\n" and (R / ".generalize-unjudged" / "solve.py").exists()
          and not replays, replays)
    shutil.copytree(R / "solver", R / ".solver-snapshot")
    (R / "solver" / "solve.py").write_text("v = 3\n")
    orchestrate.Chain._accept_after_live(ch, "x/time_trial", "time_trial")
    check("#1f live pass on the Time Trial: Mastery pre-start first, then a SHORT-timeout replay",
          replays == ["prefetch", orchestrate.BASELINE_CASE_TIMEOUT], replays)

# ---------------------------------------------------------------- #1b/#1e the blocked loop: no re-run of unchanged code
LAST = {"result": "incorrect", "attempt_id": "att-1", "no_clock": True, "run_for_time": False, "deadline": None,
        "verified": {"ok1": "v"}, "wrong": [["f1", "bad"]], "fixed": {}, "localize_complete": True}


class _Gov:
    @staticmethod
    def allow_timed():
        return True


def loop_chain(changes):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base = "script-analysis", "x"
    ch.entries = {"time_trial": {"id": "x/time_trial"}, "mastery": {"id": "x/mastery"}}
    ch.sdir, ch.root = TMP / "nosolver", TMP
    ch._pre_attempt_done, ch._tstatus, ch.gov = True, {}, _Gov()
    ch._codify_hold = lambda cid: None
    ch._ahead_new = lambda mode: 0
    ch._slow_vm_no_clock = lambda cid: False
    ch._early_join = lambda cid: False
    ch._bg_gen_take = lambda cid, why, only_won=False: False
    ch._late_probes = lambda cid, wait=False, defer_compound=False: {}
    ch.calls = {"run": 0, "gen": 0}
    ch.generalize = lambda cid, **kw: ch.calls.__setitem__("gen", ch.calls["gen"] + 1)
    sig = iter(range(1000))
    return ch, (lambda d: next(sig)) if changes else (lambda d: {})


for changes in (False, True):
    ch, sigfn = loop_chain(changes)

    def fake_run(cid, sdir, log=None, **kw):
        ch.calls["run"] += 1
        return "blocked"
    with patched({**QUIET, (orchestrate, "set_state"): lambda *a, **k: None, (orchestrate, "AUTO_EARLY"): False,
                  (orchestrate, "LIVE_ANSWER"): False, (orchestrate, "label_only_failure"): lambda w: False,
                  (orchestrate, "_code_sig"): sigfn, (orchestrate, "capture_variant"): lambda *a: None,
                  (cli, "is_complete"): lambda cid: False, (cli, "gm_solved"): lambda cid: False,
                  (timed, "run"): fake_run, (timed, "last_result"): lambda cid: dict(LAST),
                  (timed, "timed_dir"): lambda cid: TMP / "no-tdir",
                  (timed, "resolve_format_alternates"): lambda *a, **k: set(),
                  (timed, "resolve_labels_online"): lambda *a, **k: set()}):
        ok = orchestrate.Chain.timed_stage(ch, "time_trial")
    if not changes:
        check("#1e unchanged solver after each generalize: the open attempt is run ONCE, every later cycle goes "
              "straight to the next fix", ch.calls["run"] == 1 and ch.calls["gen"] == orchestrate.MAX_TIMED_RETRIES + 1,
              ch.calls)
    else:
        check("#1e a generalize that changed the code: the attempt is re-run each cycle (as before)",
              ch.calls["run"] == orchestrate.MAX_TIMED_RETRIES + 1, ch.calls)

# a localization that did NOT finish: the unchanged solver still re-runs (the reconnect learns more verdicts)
ch, sigfn = loop_chain(False)
CUT = dict(LAST, missing=["m1"], partial_localize_complete=False)


def fake_run2(cid, sdir, log=None, **kw):
    ch.calls["run"] += 1
    return "blocked"


with patched({**QUIET, (orchestrate, "set_state"): lambda *a, **k: None, (orchestrate, "AUTO_EARLY"): False,
              (orchestrate, "LIVE_ANSWER"): False, (orchestrate, "label_only_failure"): lambda w: False,
              (orchestrate, "_code_sig"): sigfn, (orchestrate, "capture_variant"): lambda *a: None,
              (cli, "is_complete"): lambda cid: False, (cli, "gm_solved"): lambda cid: False,
              (cli, "save"): lambda *a, **k: None,
              (timed, "run"): fake_run2, (timed, "last_result"): lambda cid: dict(CUT),
              (timed, "timed_dir"): lambda cid: TMP / "no-tdir", (timed, "ensure_started"): lambda cid: (None, None),
              (timed, "resolve_format_alternates"): lambda *a, **k: set(),
              (timed, "resolve_labels_online"): lambda *a, **k: set()}):
    orchestrate.Chain.timed_stage(ch, "time_trial")
check("#1e ... but a cut-short localization (partial_localize_complete False) still re-runs each cycle",
      ch.calls["run"] == orchestrate.MAX_TIMED_RETRIES + 1, ch.calls)

# ---------------------------------------------------------------- #1g web Mastery: stop waiting once the target is up
ch = orchestrate.Chain.__new__(orchestrate.Chain)
never = __import__("concurrent.futures").futures.Future()
ch._fam_pre_fut, ch._mut_pre_fut, ch._cmp_pre_fut = never, None, None
ready = threading.Event()
threading.Timer(0.3, ready.set).start()
t0 = time.time()
done = orchestrate.Chain._await_probes(ch, 30, ready=ready)
check("#1g the compound-check wait ends when the Mastery target is ready (not after 90 s)",
      done is False and time.time() - t0 < 3, time.time() - t0)

# ---------------------------------------------------------------- #2 early event on local runs + gating
evf = TMP / "evt.json"
os.environ["HCTF_EARLY_EVENT_FILE"], os.environ["HCTF_EARLY_GENERALIZE"] = str(evf), "1"
try:
    hb_timed._CTX.on_event = None
    hb_timed._event("solved", {"cid": "c", "attempt_id": "att", "missing": ["m1"], "submitted": {"x": "y"}},
                    result="solver_incomplete")
    d = json.loads(evf.read_text()) if evf.exists() else {}
    check("#2 hb_timed writes the mid-attempt event to the file a LOCAL parent polls (no daemon callback needed)",
          d.get("event") == "solved" and d.get("result") == "solver_incomplete" and "submitted" not in d, d)
finally:
    del os.environ["HCTF_EARLY_EVENT_FILE"], os.environ["HCTF_EARLY_GENERALIZE"]

seen = []
env = {}
stop = workers._local_event_poller("x/time_trial", env, seen.append)
Path(env["HCTF_EARLY_EVENT_FILE"]).write_text(json.dumps({"event": "solved", "missing": ["a"]}))
for _ in range(30):
    if seen:
        break
    time.sleep(0.1)
stop.set()
check("#2 the local poller hands the event over once, with `local` = the timed runner's bytes dir",
      seen and seen[0].get("local", "").endswith("x_time_trial") and env.get("HCTF_EARLY_GENERALIZE") == "1", seen)
Path(env["HCTF_EARLY_EVENT_FILE"]).unlink(missing_ok=True)


def early_chain():
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base, ch.sdir, ch.root = "script-analysis", "x", TMP / "nosolver", TMP
    ch._early = None
    ch._ahead_new = lambda mode: 0
    ch.started = []
    ch.generalize = lambda *a, **k: ch.started.append(a)
    return ch


ldir = TMP / "tdir"
ldir.mkdir()
(ldir / "contract.json").write_text(json.dumps({"attempt_id": "att", "answer_ids": ["a"]}))
case = TMP / "case-v"
case.mkdir()
with patched({**QUIET, (workers, "EARLY_GENERALIZE"): False, (orchestrate, "capture_variant"): lambda cid, sdir: case,
              (cli, "save"): lambda *a, **k: None, (cli, "attempt_id"): lambda c: (c or {}).get("attempt_id")}):
    ch = early_chain()
    orchestrate.Chain._early_event(ch, "x/time_trial", {"event": "solved", "local": str(ldir), "attempt_id": "att",
                                                        "result": "solver_incomplete", "missing": ["m"] * 3})
    check("#2 a small solver gap (3 empty) starts NO early generalize (the normal path / live answer handles it)",
          ch._early is None, ch._early)
    orchestrate.Chain._early_event(ch, "x/time_trial", {"event": "solved", "local": str(ldir), "attempt_id": "att",
                                                        "result": "solver_incomplete", "missing": ["m"] * 902})
    if ch._early:
        ch._early["thread"].join(timeout=5)
    check("#2 a large gap (902 empty, D23 script TT) starts the generalize at once, beside the attempt's banking",
          ch._early is not None and ch.started, (ch._early, ch.started))
    ch2 = early_chain()
    orchestrate.Chain._early_event(ch2, "x/time_trial", {"event": "solved", "local": str(ldir), "attempt_id": "att",
                                                         "result": "incorrect", "missing": []})
    check("#2 an all-answered wrong attempt never starts an early generalize (in-window localization owns it)",
          ch2._early is None, ch2._early)
    ch3 = early_chain()
    check("#2 _early_kw arms the event on untimed pools too", "on_event" in orchestrate.Chain._early_kw(ch3, "c", True))

# ---------------------------------------------------------------- #4 bank rejected values; sampler line
cid4 = "test-d23-bank/time_trial"
bp = hb_timed._bank_path(cid4)
try:
    hb_timed._bank_save({"cid": cid4, "attempt_id": "att", "result": "solver_incomplete",
                         "verified": {"ok": "1"}, "partial_wrong": [["bad", "x"], ["ok", "1"]]})
    rej = hb_timed._bank_rejected(cid4, "att")
    check("#4 a rejected value is banked (and a verified field never counts as rejected)",
          rej == {"bad": ["x"]}, rej)
    check("#4 ... only for the same attempt", hb_timed._bank_rejected(cid4, "other") == {})
    check("#4 the verified bank still loads", hb_timed._bank_load(cid4, "att") == {"ok": "1"})
finally:
    bp.unlink(missing_ok=True)
s = ressample.sample()
check("#4 resource sample has memory / pressure / worker fields",
      {"mem_avail_mb", "psi_mem_some", "claude", "cg_high"} <= set(s) and ressample.line(s, time.time()).startswith("[res] "),
      s)

# ---------------------------------------------------------------- #5 (rehearsal D23 run 1) usage-limit gate
import datetime as _dt  # noqa: E402
_now = _dt.datetime(2026, 10, 24, 1, 45, 17).timestamp()
_msg = "You've hit your session limit · resets 4:10am (Asia/Manila) 429 api_error"
_t = workers.limit_reset_epoch(_msg, _now)
check("#5 the stated reset is parsed (4:10am Asia/Manila -> 145 min after the 01:45 failure)",
      _t is not None and round((_t - _now) / 60) == 145, _t and (_t - _now) / 60)
check("#5 a 24 h clock reset parses; a limit with no stated reset does not (old backoff applies)",
      workers.limit_reset_epoch("resets 16:00", _now) is not None and workers.limit_reset_epoch("usage limit", _now) is None)
saved_gate = dict(workers._limit_gate)
try:
    with patched({(workers, "LIMIT_RESET_PAD"): 0.0, (workers, "limit_reset_epoch"): lambda d, now=None: time.time() + 0.6}):
        closed = workers.note_limit("You've hit your session limit · resets soon")
        t0 = time.time()
        waited = workers.wait_limit_gate()
    check("#5 a stated reset closes the gate and a launch waits for it (not a 20 s backoff that gives up)",
          closed and 0.4 < waited < 3 and time.time() - t0 < 3, (closed, waited))
    with patched({(workers, "limit_reset_epoch"): lambda d, now=None: time.time() + 10 ** 6}):
        check("#5 a reset further than HCTF_LIMIT_WAIT_MAX never closes the gate", not workers.note_limit("resets x"))
    workers._limit_gate.update(until=time.time() + 30)
    stop_e = threading.Event()
    threading.Timer(0.3, stop_e.set).start()
    check("#5 a stop event ends the wait (-1)", workers.wait_limit_gate(stop_e) == -1)
finally:
    workers._limit_gate.clear()
    workers._limit_gate.update(saved_gate)

runs5 = []
with patched({(workers, "_run_local_once"): lambda *a, **k: (runs5.append(time.time()), (1, TMP / "w.log"))[1],
              (workers, "record_metrics"): lambda log, *a: (
                  {"outcome": "limit", "detail": "You've hit your session limit · resets soon"} if len(runs5) == 1
                  else {"outcome": "ok", "detail": ""}),
              (workers, "limit_reset_epoch"): lambda d, now=None: time.time() + 0.5,
              (workers, "LIMIT_RESET_PAD"): 0.0}):
    (TMP / "w.log").parent.mkdir(parents=True, exist_ok=True)
    rc5, _ = workers.run_local(TMP, "single", "p", {"HCTF_CHAL": "c"}, timeout=1.0)
check("#5 run_local: a limit exit waits for the reset and relaunches even when the wait exceeds the stage timeout",
      len(runs5) == 2 and runs5[1] - runs5[0] >= 0.4, runs5)
workers._limit_gate.update(until=0.0, detail="")

# ---------------------------------------------------------------- #6 (rehearsal D23 web) per-target secrets aren't labels
check("#6 a web proof / hash / base64 token is token-like; real labels are not",
      labels.token_like("proof_26795dfbe6834ca79f73123806703548") and labels.token_like("aGVsbG8gd29ybGQhIFRoaXMgaXM0")
      and not any(labels.token_like(v) for v in ("if_guard", "call_double", "three_stage_decode_write_launch",
                                                 "T1059.003", "base64_literal")))
_sub_kw = {}
with patched({(cli, "submit"): lambda cid, ans, **k: (_sub_kw.update(k), ("incorrect", {}, []))[1],
              (cli, "load"): lambda cid, f: {}, (labels, "judged_wrong"): lambda cid, aid: set()}):
    labels.probe("c", "f", ["x"], budget=1, delay=0, log=lambda *a: None)
check("#6 resolver probes are tagged harness=label (never count against a worker's per-field cap)",
      _sub_kw.get("harness") == "label", _sub_kw)
probed6 = []
ch6 = orchestrate.Chain.__new__(orchestrate.Chain)
ch6.lane, ch6.sdir = "web", TMP / "web-solver"
ch6.sdir.mkdir(parents=True, exist_ok=True)
(ch6.sdir / "solve.py").write_text("print('{}')\n")
_c6 = {"answer_ids": ["proof-1"], "questions": [{"id": "proof-1", "artifact": "Target 1", "question": "Recover the proof"}]}
with patched({**QUIET, (cli, "load"): lambda cid, f: _c6, (timed, "latest_artifacts"): lambda cid: TMP,
              (solvers, "solve_contract"): lambda *a, **k: ({}, None), (cli, "confirmed_answers"): lambda cid: {},
              (cli, "is_complete"): lambda cid: False, (labels, "load_vocab"): lambda: {"1": ["x"]},
              (labels, "probe"): lambda *a, **k: (probed6.append(a), {"tried": []})[1]}):
    orchestrate.Chain.auto_labels(ch6, "web-x")
check("#6 auto_labels never probes a live web target's proof field", not probed6, probed6)

# ---------------------------------------------------------------- #7 day.sh keeps the previous run's log
import subprocess  # noqa: E402
_day = (ROOT / "bin" / "day.sh").read_text()
check("#7 day.sh rotates an existing .run/dayNN.log before a relaunch writes a fresh one",
      'KEEP=".run/${DAYTAG}-$(date -r "$LOG"' in _day and 'mv "$LOG" "$KEEP"' in _day
      and subprocess.run(["bash", "-n", str(ROOT / "bin" / "day.sh")]).returncode == 0)

shutil.rmtree(TMP, ignore_errors=True)
if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D23 post-mortem checks passed")
