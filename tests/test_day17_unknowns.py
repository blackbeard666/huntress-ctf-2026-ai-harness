"""Day 17 unknown-vocabulary readiness (the binary hcfg_storage lesson). Offline.
Item 3 -- drift watcher + under-specification alarm:
- driftwatch: unsolved modes of a day, next-deadline rule, one check pass resumes only a chain whose contract changed,
  the watcher is launched only for unsolved modes (one per day), never from a resume.
- labels.underspecified: open-vocab field, >= cap rejections, accepted siblings of its family -> named + reported.
- labels.judged_wrong forgets rejections given before an in-place rewrite (drift.json).
- feed: [drift] lines and the UNDER-SPECIFIED? alarm show up.

Run:  source bin/env.sh && python3 tests/test_day17_unknowns.py      (exit 0 = all pass)
"""
import datetime
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import cli, driftwatch, feed, labels, paths  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="hctf-d17unk-"))
cli.cdir = lambda cid: TMP / "modes" / cid

# ------------------------------------------------------------------------------------------------ driftwatch
d = driftwatch.deadline("20:15", now=datetime.datetime(2026, 10, 17, 21, 9))
assert datetime.datetime.fromtimestamp(d) == datetime.datetime(2026, 10, 18, 20, 15), datetime.datetime.fromtimestamp(d)
d = driftwatch.deadline("20:15", now=datetime.datetime(2026, 10, 18, 19, 50))
assert datetime.datetime.fromtimestamp(d) == datetime.datetime(2026, 10, 19, 20, 15), "< 30 min away -> tomorrow"

paths.CHALLENGES = TMP / "challenges"
chal = {"binary-x": ("binary-x", "binary-x/time_trial", "binary-x/mastery"), "warm-x": ("warm-x", "warm-x/time_trial", None)}
for name, (s, t, m) in chal.items():
    cd = paths.CHALLENGES / "day17" / name
    cd.mkdir(parents=True)
    (cd / "meta.json").write_text(json.dumps({"ids": {"single_solve": s, "time_trial": t, "mastery": m}}))
    for cid in (s, t, m):
        if cid:
            (TMP / "modes" / cid).mkdir(parents=True, exist_ok=True)
            (TMP / "modes" / cid / "contract.json").write_text(json.dumps({"questions": [{"id": "q"}]}))
solved = {"warm-x", "warm-x/time_trial"}
cli.gm_solved = lambda cid: cid in solved
got = driftwatch.unsolved(17)
assert got == [("binary-x", "binary-x"), ("binary-x", "binary-x/time_trial"), ("binary-x", "binary-x/mastery")], got

drifted = {"binary-x": ["d12_analysis_hcfg_storage"]}
cli.contract_drift = lambda cid: drifted.get(cid, [])
resumed = []
_res = driftwatch.resume
driftwatch.resume = lambda day, base, log=print: resumed.append(base) or 0
logs = []
found = driftwatch.check_once(17, do_resume=True, log=logs.append)
assert found == {"binary-x": ["d12_analysis_hcfg_storage"]} and resumed == ["binary-x"], (found, resumed)
assert any("DRIFT binary-x" in x for x in logs), logs
resumed.clear()
drifted.clear()
assert driftwatch.check_once(17, do_resume=True, log=logs.append) == {} and not resumed, "no change -> no resume"

started = []
driftwatch.ROOT = TMP
(TMP / ".run").mkdir()
p = driftwatch.start_watch(17, log=logs.append, popen=lambda argv, **k: started.append(argv) or "proc")
assert p == "proc" and started and "hctf.cli drift --day 17 --watch" in started[0][-1], started
os.environ["HCTF_DRIFT_RESUME"] = "1"
assert driftwatch.start_watch(17, log=logs.append, popen=lambda *a, **k: 1 / 0) is None, "never from a resume"
del os.environ["HCTF_DRIFT_RESUME"]
solved |= {"binary-x", "binary-x/time_trial", "binary-x/mastery"}
assert driftwatch.start_watch(17, log=logs.append, popen=lambda *a, **k: 1 / 0) is None, "all solved -> no watch"
driftwatch.resume = _res
print("ok  driftwatch: unsolved modes, deadline rule, resume only on a rewritten contract, launched once when unsolved")

# ------------------------------------------------------------------------------------------------ under-spec alarm
cid = "binary-day-17-u"
(TMP / "modes" / cid).mkdir(parents=True)
q = lambda i, fmt: {"id": i, "question": f"What is the exact analysis hcfg storage value for field {i}?",
                    "answer_format": fmt}
ot = {"kind": "exact_text"}
ids = ["d08_analysis_hcfg_storage", "d09_analysis_hcfg_storage", "d12_analysis_hcfg_storage",
       "d14_analysis_hcfg_storage", "d12_analysis_hcfg_offset"]
start = {"attempt_id": "U1", "answer_ids": ids, "questions": [q(i, ot) for i in ids]}
(TMP / "modes" / cid / "start.json").write_text(json.dumps(start))
(TMP / "modes" / cid / "confirmed.json").write_text(json.dumps({"U1": {"d08_analysis_hcfg_storage": "base64",
                                                                       "d09_analysis_hcfg_storage": "base64"}}))
subs = [{"ts": f"20261017T13{n:02d}00Z", "attempt": "U1", "answers": {f: v}, "kind": "incorrect"}
        for f in ("d12_analysis_hcfg_storage", "d14_analysis_hcfg_storage")
        for n, v in enumerate(["raw", "plain", "none", "xor", "section", "data", "bytes"])]
subs += [{"ts": "20261017T130000Z", "attempt": "U1", "answers": {"d12_analysis_hcfg_offset": "1"}, "kind": "incorrect"}]
(TMP / "modes" / cid / "submissions.jsonl").write_text("".join(json.dumps(h) + "\n" for h in subs))
(TMP / "modes" / cid / "HELP.md").write_text("d12 RAW HCFG in .data; d14 RAW HCFG in its own .hcfg section")
us = labels.underspecified(cid)
assert [f["id"] for f in us] == ["d12_analysis_hcfg_storage", "d14_analysis_hcfg_storage"], us
assert us[0]["siblings"] == {"d08_analysis_hcfg_storage": "base64", "d09_analysis_hcfg_storage": "base64"}
rp = labels.underspec_report(cid, us, TMP / "report.md")
txt = Path(rp).read_text()
assert "d12_analysis_hcfg_storage" in txt and "`base64`" in txt and "organizers" in txt and ".hcfg section" in txt
start["questions"][2]["answer_format"] = {"kind": "enum", "accepted_values": ["raw", "raw_const_array"]}
(TMP / "modes" / cid / "start.json").write_text(json.dumps(start))
assert [f["id"] for f in labels.underspecified(cid)] == ["d14_analysis_hcfg_storage"], "an enum is never 'unknown'"
print("ok  under-spec alarm: open-vocab fields past the cap with accepted siblings are named + reported; enums never")

# ------------------------------------------------------------------------------------------------ drift-aware ranking
assert "raw" in labels.judged_wrong(cid, "d14_analysis_hcfg_storage")
(TMP / "modes" / cid / "drift.json").write_text(json.dumps({"d14_analysis_hcfg_storage": "20261017T170000Z"}))
assert labels.judged_wrong(cid, "d14_analysis_hcfg_storage") == set(), "old-question rejections no longer count"
assert labels.judged_wrong(cid, "d12_analysis_hcfg_storage"), "an unchanged field keeps them"
print("ok  judged_wrong: rejections given before an in-place rewrite are forgotten")

# ------------------------------------------------------------------------------------------------ feed
f = feed.Feed()
f.process("21:09:00 [drift] 2 unsolved mode(s) (binary-x): contract watch every 600s until 20:15")
out = f.process("21:09:01 [binary-day-17-u] UNDER-SPECIFIED? 2 open-vocab field(s) (d12_analysis_hcfg_storage) ...")
out += f.process("01:03:00 [binary-day-17-u] GM REWROTE 2 question(s) in place (d12_analysis_hcfg_storage)")
assert any("❓" in x and "UNDER-SPECIFIED?" in x for x in out) and any("🔁" in x and "GM REWROTE" in x for x in out), out
print("ok  feed: ❓ under-spec alarm, 🔁 drift/rewrite events")

# ------------------------------------------------------------------------------------------------ item 4: knowledge
from lib import knowledge as K, playbook  # noqa: E402
assert [K.hcfg_storage("raw", ".hcfg"), K.hcfg_storage("raw", ".data"), K.hcfg_storage("raw", None, wasm=True),
        K.hcfg_storage("raw", None), K.hcfg_storage("base64"), K.hcfg_storage("hex")] == \
    ["raw_hcfg_section", "raw_const_array", "wasm_data_segment", "raw", "base64", None]
assert "raw" not in playbook.rejected("binary-reverse-engineering", "d12_analysis_hcfg_storage"), "raw is an enum value"
assert "hcfg_section" in playbook.rejected("binary-reverse-engineering", "d12_analysis_hcfg_storage")
assert "--compose" in playbook.NAMING_LAWS and "IDENTIFIER values only" in playbook.NAMING_LAWS
assert "storage" in labels.CACHEABLE_FAMILIES
print("ok  knowledge: 5-token hcfg_storage rules, `raw` not rejected, depth-3 + literal-grounding laws in the prompt")

# ------------------------------------------------------------------------------------------------ item 1: compose
bc = "binary-day-17-c"
(TMP / "modes" / bc).mkdir(parents=True)
qs = [{"id": i, "question": f"What is the exact analysis hcfg storage value for field {i}?",
       "answer_format": {"kind": "exact_text"}} for i in ("d08_analysis_hcfg_storage", "d12_analysis_hcfg_storage",
                                                          "d14_analysis_hcfg_storage", "d12_analysis_config_url")]
(TMP / "modes" / bc / "start.json").write_text(json.dumps({"attempt_id": "C1", "answer_ids": [q["id"] for q in qs],
                                                           "questions": qs}))
(TMP / "modes" / bc / "confirmed.json").write_text(json.dumps({"C1": {"d08_analysis_hcfg_storage": "base64"}}))
(TMP / "modes" / bc / "HELP.md").write_text((ROOT / "tests" / "data" / "d17_binary_help.md").read_text())
worker = [("d14_analysis_hcfg_storage", v) for v in ("raw", "section", "hcfg", "data", "hcfg_section", "data_section")]
worker += [("d12_analysis_hcfg_storage", v) for v in ("raw", "byte_array", "base64", "array", "blob", "xor")]
(TMP / "modes" / bc / "submissions.jsonl").write_text("".join(json.dumps(
    {"ts": "20261017T130500Z", "attempt": "C1", "answers": {a: v}, "kind": "incorrect"}) + "\n" for a, v in worker))
_pb = labels.playbook
labels.playbook = None    # the replay may not use what the GM published later
w14, s14 = labels.field_evidence(bc, "d14_analysis_hcfg_storage")
assert "section" in w14 and s14 == ["hcfg"] and "data" not in w14, ("d14's own sentence only", w14, s14)
w12, s12 = labels.field_evidence(bc, "d12_analysis_hcfg_storage")
assert s12 == ["data"] and "refused" not in w12, ("Rejected/Untried sentences are never evidence", w12)
c14 = labels.compose(bc, "d14_analysis_hcfg_storage", lane="binary-reverse-engineering", siblings=["base64"])
c12 = labels.compose(bc, "d12_analysis_hcfg_storage", lane="binary-reverse-engineering", siblings=["base64"])
r14, r12 = c14.index("raw_hcfg_section") + 1, c12.index("raw_const_array") + 1
assert r14 <= 25 and r12 <= 100 and len(c14) <= labels.COMPOSE_N, (r14, r12, len(c14))
assert not set(c14) & {v for a, v in worker if a == "d14_analysis_hcfg_storage"}, "never re-probe a rejected value"
labels.playbook = _pb
print(f"ok  compose: from the worker's own D17 HELP.md, raw_hcfg_section #{r14} and raw_const_array #{r12} "
      f"(flat 1-2 token search never reached them)")

assert labels.label_like(bc, "d12_analysis_hcfg_storage", "binary-reverse-engineering")
assert not labels.label_like(bc, "d12_analysis_config_url", "binary-reverse-engineering"), "a derived value"
sent = []


def fake_submit(c, ans, **k):
    (aid, v), = ans.items()
    sent.append(v)
    return ("accepted" if v == "raw_hcfg_section" else "incorrect"), {}, []


_sub, _rv = cli.submit, labels.record_values
cli.submit, labels.record_values = fake_submit, lambda *a, **k: None
got = labels.probe_first(bc, "d14_analysis_hcfg_storage", c14, conc=8)
cli.submit, labels.record_values = _sub, _rv
assert got == "raw_hcfg_section" and len(sent) <= (r14 // 8 + 1) * 8, (got, len(sent))
print(f"ok  probe_first: parallel waves of 8 stop at the accepting wave ({len(sent)} probes for rank #{r14})")

# ------------------------------------------------------------------------------------------------ item 2: escalation
from hctf import orchestrate  # noqa: E402
ch = orchestrate.Chain.__new__(orchestrate.Chain)
ch.lane, ch.sdir = "binary-reverse-engineering", TMP / "day17" / "b" / "solver"
probed = []
_pf = labels.probe_first
labels.probe_first = lambda c, a, cands, **k: probed.append((a, len(cands))) or None
_ic = cli.is_complete
cli.is_complete = lambda c: False
assert ch.compose_labels(bc) is False
assert [a for a, _n in probed] == ["d12_analysis_hcfg_storage", "d14_analysis_hcfg_storage"], probed
probed.clear()
st = json.loads((TMP / "modes" / bc / "start.json").read_text())
(TMP / "modes" / bc / "start.json").write_text(json.dumps({**st, "deadline": "2026-10-17T13:05:00Z"}))
ch.compose_labels(bc)
assert not probed, "a clocked attempt never runs the composed search"
labels.probe_first, cli.is_complete = _pf, _ic
print("ok  escalation: after auto-labels, only open LABEL fields of an untimed single get the composed search")
print("ALL PASS")
