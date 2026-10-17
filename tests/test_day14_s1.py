"""Day 14 prep, stream S1: GM accepted_ids, harness-tagged submits, slug gate, spelling alternates, partial reuse-race
banking + race note, the worker inbox (hook delivery), go-early. Offline: a FakeGM with replay_gm.judge semantics
(any wrong field -> the batch is `incorrect`; all-right partial -> `accepted` + accepted_ids; complete -> CORRECT).

Run:  source bin/env.sh && python3 tests/test_day14_s1.py      (exit 0 = all pass)
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import Future
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, fmtalt, inbox, orchestrate, solvers, timed  # noqa: E402
from lib import slug  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="d14s1-", dir=str(ROOT / ".run" / "tmp")))
SLUGQ = {"answer_format": {"kind": "pattern", "syntax": "three lowercase words separated by hyphens, followed by a "
                                                          "hyphen and a two-digit number; submit the slug only"}}


class FakeGM:
    """Patches cli.call/cli.cdir: one challenge `cid` with `truth`, GM submit semantics, a call log."""

    def __init__(self, cid, truth, qs=None, deadline=None, accepted_ids=True):
        self.cid, self.truth, self.conf, self.calls = cid, dict(truth), {}, []
        self.accepted_ids = accepted_ids
        self.dir = TMP / cid.replace("/", "_")
        self.dir.mkdir(parents=True, exist_ok=True)
        for f in self.dir.iterdir():
            f.unlink()
        ids = list(truth)
        (self.dir / "start.json").write_text(json.dumps({
            "attempt_id": "att-1", "mode": "single_solve", "deadline": deadline, "answer_ids": ids,
            "questions": [(qs or {}).get(a, {}) for a in ids]}))

    def call(self, cid, op, *args, timeout=180):
        assert op == "submit", op
        answers = json.loads(args[1])
        self.calls.append(answers)
        if any(self.truth.get(a) != str(v) for a, v in answers.items()):
            return {"http": 200, "body": {"result": "incorrect"}}
        self.conf.update(answers)
        if len(self.conf) == len(self.truth):
            return {"http": 200, "body": {"result": "CORRECT"}}
        body = {"result": "accepted", "remaining": len(self.truth) - len(self.conf)}
        if self.accepted_ids:
            body["accepted_ids"] = sorted(answers)
        return {"http": 200, "body": body}

    def __enter__(self):
        self._saved = (cli.call, cli.cdir)
        cli.call, cli.cdir = self.call, (lambda cid: self.dir)
        return self

    def __exit__(self, *exc):
        cli.call, cli.cdir = self._saved

    def subs(self):
        p = self.dir / "submissions.jsonl"
        return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


# --- A1 accepted_ids: confirm exactly what the GM names, even when `remaining` was moved by someone else -------------
with FakeGM("acc-1", {"a": "1", "b": "2", "c": "3", "d": "4"}) as gm:
    gm.conf["z"] = "x"                          # another submitter moved `remaining` meanwhile (inference would fail)
    gm.truth["z"] = "x"
    kind, body, _ = cli.submit("acc-1", {"a": "1", "b": "2"}, force=True, probe=True)
    assert kind == "accepted" and set(cli.confirmed_answers("acc-1")) == {"a", "b"}, cli.confirmed_answers("acc-1")
    cli.ACCEPTED_IDS = False
    kind, body, _ = cli.submit("acc-1", {"c": "3"}, force=True, probe=True)   # single field: always confirmable
    cli.ACCEPTED_IDS = True
    assert "c" in cli.confirmed_answers("acc-1")
print("ok  accepted_ids: exact confirmation of a partial accept (no `remaining` inference)")

# --- A2 harness wrongs don't eat the worker's per-field cap; the exact value stays refused --------------------------
with FakeGM("har-1", {"a": "good"}) as gm:
    for i in range(cli.MAX_WRONG_PER_ATTEMPT):
        cli.submit("har-1", {"a": f"bad{i}"}, harness="race")
    kind, _b, probs = cli.submit("har-1", {"a": "bad0"})
    assert kind is None and any("already judged incorrect" in p for p in probs), probs
    kind, _b, probs = cli.submit("har-1", {"a": "another"})
    assert kind == "incorrect" and not probs, probs           # still allowed: harness wrongs were free
    assert all(h.get("harness") == "race" for h in gm.subs()[:-1]) and "harness" not in gm.subs()[-1]
    cli.HARNESS_WRONG_FREE = False
    kind, _b, probs = cli.submit("har-1", {"a": "yet-another"})
    cli.HARNESS_WRONG_FREE = True
    assert kind is None and any("per-field cap" in p for p in probs), probs
print("ok  harness-tagged submits: free for the worker's per-field cap, rejected values still refused")

# --- B1 slug gate ------------------------------------------------------------------------------------------------------
import glob  # noqa: E402
import re  # noqa: E402
seen = set()
for f in glob.glob(str(ROOT / "challenges/day*/warmups-*/**/*.json"), recursive=True):
    if f.endswith(("confirmed.json", "expected.json")):
        seen |= set(re.findall(r'"([a-z]+-[a-z]+-[a-z]+-\d{2})"', open(f).read()))
assert len(seen) > 100 and all(slug.slug_problem(s, SLUGQ) is None for s in seen), \
    [s for s in seen if slug.slug_problem(s, SLUGQ)][:5]
assert slug.slug_problem("ovisx-tviskr-fbvecw-31", SLUGQ) and slug.slug_problem("handy-candle-quartz-31", SLUGQ) is None
assert slug.slug_problem("prou-ldami-vbeaver-20", SLUGQ)                        # D13 per-line mis-decode
assert slug.slug_problem("anything goes", {"answer_format": "free text"}) is None
with FakeGM("slug-1", {"message": "handy-candle-quartz-31"}, qs={"message": SLUGQ}) as gm:
    kind, _b, probs = cli.submit("slug-1", {"message": "ovisx-tviskr-fbvecw-31"})
    assert kind is None and "not English" in probs[0] and not gm.calls, probs
    kind, _b, probs = cli.submit("slug-1", {"message": "ovisx-tviskr-fbvecw-31"}, force=True)   # --force overrides
    assert kind == "incorrect" and len(gm.calls) == 1
with FakeGM("slug-2", {"message": "handy-candle-quartz-31"}, qs={"message": SLUGQ}, deadline="2026-10-14T00:00:00Z") as gm:
    kind, _b, probs = cli.submit("slug-2", {"message": "ovisx-tviskr-fbvecw-31"})
    assert kind == "incorrect" and not probs                                   # timed windows: never gated
print(f"ok  slug gate: all {len(seen)} confirmed slugs pass; gibberish refused (untimed only, --force overrides)")

# --- B2 spelling alternates ---------------------------------------------------------------------------------------------
HEXQ = {"answer_format": {"kind": "pattern", "syntax": "0x-prefixed lowercase hex"}}
assert fmtalt.alternates("d09-pe-001-pe-address-of-entry-point-rva-hex", "0x65bd0", HEXQ)[0][0] == "0x00065bd0"
assert fmtalt.alternates("d09-pe-001-pe-coff-machine-u16-hex", "0x14c", {})[0][0] == "0x014c"
g = fmtalt.alternates("d13-msi-001-msi-product-code-guid", "DD1A80D5-0250-4F4D-B289-13096D633C61", {})
assert "{DD1A80D5-0250-4F4D-B289-13096D633C61}" in [x for x, _ in g[:2]], g
assert fmtalt.alternates("f", "abc", {"answer_format": {"kind": "enum", "accepted_values": ["a"]}}) == []
assert fmtalt.alternates("flag", "0" * 32, {"answer_format": "32 lowercase hex md5"}) == []
assert len(fmtalt.alternates("x-hex", "0x1", {}, max_n=2)) == 2
assert all(v != "0x65bd0" for v, _ in fmtalt.alternates("rva-hex", "0x65bd0", {}))
saved_conv = fmtalt.CONV
fmtalt.CONV = TMP / "conv.json"
GUIDQ = {"answer_format": {"kind": "pattern", "syntax": "8-4-4-4-12 hex including hyphens"}}
truth_guid = "{DD1A80D5-0250-4F4D-B289-13096D633C61}"
with FakeGM("d13-msi", {"d13-msi-001-msi-product-code-guid": truth_guid},
            qs={"d13-msi-001-msi-product-code-guid": GUIDQ}) as gm:
    class A:
        id, from_solver, force = "d13-msi", False, False
        answers = json.dumps({"d13-msi-001-msi-product-code-guid": "DD1A80D5-0250-4F4D-B289-13096D633C61"})
    rc = cli.c_submit(A)
    assert cli.is_complete("d13-msi") and rc == cli.EXIT["correct"], (rc, gm.calls)
    assert len(gm.calls) == 2 and gm.subs()[-1].get("harness") == "alt"
    assert json.loads(fmtalt.CONV.read_text())["code-guid"]["braces-upper"] == 1
fmtalt.CONV = saved_conv
print("ok  spelling alternates: hex width / GUID braces; D13 replica CORRECT in 1 extra submit, convention recorded")

# --- C1 partial race banking ---------------------------------------------------------------------------------------------
ch = object.__new__(orchestrate.Chain)
ch.base, ch.lane, ch.sdir, ch.root = "race", "binary-reverse-engineering", TMP / "rsolver", TMP
ch._go_lock, ch._go_sent, ch._go_pending = threading.Lock(), False, []
msgs = []


def run_race(cid, truth, high, spec, alts=None, worker_at=None):
    saved = {k: getattr(*k) for k in [(timed, "latest_artifacts"), (solvers, "reuse_plan"), (orchestrate, "say"),
                                       (orchestrate, "set_state")]}
    msgs.clear()
    ch._go_sent, ch._go_pending = False, []
    with FakeGM(cid, truth) as gm:
        if worker_at is not None:
            orig = gm.call

            def call(c, op, *a, **k):        # the worker submits after `worker_at` race submits
                if len(gm.calls) == worker_at:
                    with open(gm.dir / "submissions.jsonl", "a") as f:
                        f.write(json.dumps({"attempt": "att-1", "answers": {}, "kind": "incorrect"}) + "\n")
                return orig(c, op, *a, **k)
            cli.call = call
        timed.latest_artifacts = lambda c: TMP
        solvers.reuse_plan = lambda *a, **k: {"high": high, "spec": spec, "runs": {"x": 1}, "best": None,
                                              "alts": alts or {}}
        orchestrate.say = lambda m, *a, **k: msgs.append(m)
        orchestrate.set_state = lambda *a, **k: None
        try:
            ch._reuse_race(cid)
        finally:
            for (mod, name), fn in saved.items():
                setattr(mod, name, fn)
        return gm, list(gm.calls), cli.confirmed_answers(cid)


truth = {f"d{i:02d}_f": str(i) for i in range(120)}
high = {k: v for k, v in list(truth.items())[:110]}
spec = dict(list(truth.items())[110:])
spec["d12_analysis_hcfg_offset"] = "999"          # the one wrong speculative field (D12)
truth["d12_analysis_hcfg_offset"] = "82928"
gm, calls, conf = run_race("race-d12", truth, high, spec)
# <= 12 submits (was 7 sequential): the bisect now runs in parallel waves (hctf/grouptest.py, D16 post-mortem) -- both
# halves of a failing group at once costs ~1 extra submit per level and saves a GM round trip per level
assert len(conf) >= 120 and len(calls) <= 12 and "d12_analysis_hcfg_offset" not in conf, (len(conf), len(calls))
note = ch._go_pending[0]
assert "1 remain, by family" in note and "d12_analysis_hcfg_offset" in note and '"999"' in note, note
print(f"ok  race D12 replica: {len(conf)}/121 banked in {len(calls)} submits; note names only hcfg_offset + its bad value")

gm, calls, conf = run_race("race-inc", truth, dict(list(truth.items())[:100]), {})
assert len(conf) == 100 and len(calls) == 1, (len(conf), len(calls))       # old code: incomplete -> nothing banked
gm, calls, conf = run_race("race-all", dict(list(truth.items())[:10]), dict(list(truth.items())[:10]), {})
assert len(calls) == 1 and len(conf) == 10 and any("WON" in m for m in msgs)
gm, calls, conf = run_race("race-yield", truth, high, spec, worker_at=1)
# D17 prep: the race no longer yields when the worker submits -- it is the attempt's ONE bisector (the worker's
# `hctf submit` waits on race_bisect.json instead of a second bisect over the same fields)
assert len(calls) > 2 and len(conf) >= 120, (len(calls), len(conf))
gm, calls, conf = run_race("race-alts", {"a": "1", "b": "2"}, {"a": "1"}, {"b": "x"}, alts={"b": ["x", "2"]})
assert conf == {"a": "1", "b": "2"} and len(calls) <= 4, calls              # isolated wrong -> other solver's value
SL = {"message": "handy-candle-quartz-31"}
saved_q = cli._questions
cli._questions = lambda c: {"message": SLUGQ}
gm, calls, conf = run_race("race-slug", SL, {"message": "ovisx-tviskr-fbvecw-31"}, {})
cli._questions = saved_q
assert calls == [] and any("implausible" in m for m in msgs), (calls, msgs)
orchestrate.RACE_PARTIAL = False
gm, calls, conf = run_race("race-old", truth, dict(list(truth.items())[:100]), {})
assert calls == []                                                           # kill switch: old all-or-nothing contract
orchestrate.RACE_PARTIAL = True
print("ok  race banking: incomplete banks confident, complete = 1 submit, keeps bisecting past a worker submit, alts, "
      "slug gate, kill switch")

# --- C2 note routing: before go -> pending (go text); after go -> inbox ------------------------------------------------
ch._go_sent, ch._go_pending = False, []
ch._deliver_note("route-1", "NOTE-A", key="race")
assert ch._go_pending == ["NOTE-A"]
with FakeGM("route-1", {"a": "1"}) as gm:
    ch._go_sent = True
    ch._deliver_note("route-1", "NOTE-B", key="race")
    assert inbox.texts(gm.dir) == ["NOTE-B"] and ch._go_pending == ["NOTE-A"]
print("ok  race note routing: before the go -> go text, after -> inbox (never both)")

# --- inbox + hook: delivered once per worker as additionalContext -----------------------------------------------------
hd = TMP / "hookdir"
hd.mkdir(exist_ok=True)
inbox.reset(hd)
inbox.post(hd, "119/120 confirmed; only d12_analysis_hcfg_offset remains", key="race")
env = dict(os.environ, HCTF_STAGE="single", HCTF_CHAL="x", HCTF_CHAL_DIR=str(hd), HCTF_WORKER_START=str(time.time()))
hook = str(ROOT / ".claude" / "hooks" / "nudge.py")
r1 = subprocess.run([sys.executable, hook], env=env, capture_output=True, text=True, timeout=30)
out = json.loads(r1.stdout)["hookSpecificOutput"]
assert out["hookEventName"] == "PostToolUse" and "HARNESS UPDATE" in out["additionalContext"] \
    and "hcfg_offset" in out["additionalContext"], r1.stdout
r2 = subprocess.run([sys.executable, hook], env=env, capture_output=True, text=True, timeout=30)
assert r2.stdout.strip() == "", r2.stdout                                   # delivered once
inbox.post(hd, "second", key="dry-run")
r3 = subprocess.run([sys.executable, hook], env=env, capture_output=True, text=True, timeout=30)
assert "second" in r3.stdout and "hcfg_offset" not in r3.stdout
r4 = subprocess.run([sys.executable, hook], env=dict(env, HCTF_INBOX="0"), capture_output=True, text=True, timeout=30)
assert r4.stdout.strip() == ""
print("ok  inbox hook: unread messages -> PostToolUse additionalContext once per worker; HCTF_INBOX=0 silent")

# --- C4 go-early: an unfinished dry run doesn't hold the go; its note arrives via the inbox -----------------------------
with FakeGM("go-1", {"a": "1"}) as gm:
    ch._go_sent, ch._go_pending = True, []
    fut = Future()
    ch._dry_fut = fut
    saved = (orchestrate.say, solvers.render_dry_run)
    orchestrate.say = lambda *a, **k: None
    solvers.render_dry_run = lambda d: f"answered {d['answered']}/{d['total']}"
    t = time.time()
    assert ch._prior_dry_run_text("go-1") == "" and time.time() - t < 0.5
    fut.set_result({"seconds": 4.5, "timed_out": False, "answered": 129, "total": 130})
    assert any("129/130" in x for x in inbox.texts(gm.dir)), inbox.texts(gm.dir)
    orchestrate.GO_EARLY = False
    fut2 = Future()
    ch._dry_fut = fut2
    threading.Timer(0.3, lambda: fut2.set_result({"seconds": 1, "timed_out": False, "answered": 1, "total": 1})).start()
    assert ch._prior_dry_run_text("go-1") == "answered 1/1"                  # kill switch: blocks as before
    orchestrate.GO_EARLY = True
    orchestrate.say, solvers.render_dry_run = saved
print("ok  go-early: the go doesn't wait for the dry run; its note follows through the inbox")

print("\nALL DAY-14 S1 CHECKS PASSED")
