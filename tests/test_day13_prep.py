"""Behavior checks for the Day 13 prep (Day 12 singles review): Claude Code's Bash edit-diff off for workers, fast
os.walk file listing in triage (same order as sorted(Path)), content-cached toolchain detection, and the reuse race's
single confirmed-answers lookup per bisect step (offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_day13_prep.py      (exit 0 = all pass)
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
from hctf import cli, orchestrate, solvers, timed, toolchain, workers  # noqa: E402

# 1) workers: Bash edit-diff off (env for local workers, flag setting for Homebase/shadow workers)
env = workers._worker_env({})
assert env["CLAUDE_CODE_BASH_EDIT_DIFF"] == "0", env.get("CLAUDE_CODE_BASH_EDIT_DIFF")
assert workers.worker_settings("binary-reverse-engineering")["bashEditDiffEnabled"] is False
print("ok  workers: CLAUDE_CODE_BASH_EDIT_DIFF=0 + bashEditDiffEnabled=false (first Bash 10-25 s -> 0.3 s)")

# 2) walk_files: sorted(Path) order (by parts, not by string: 'a/b' before 'a-b/x'), relative posix strings;
#    scan_order unchanged (shallow first, .class last)
with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    for rel in ("a-b/x.txt", "a/b.txt", "a/c/deep.class", "z.elf", "a/A.class", "m/n/o/p.bin"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(b"x" * 20)
    (root / "emptydir").mkdir()
    walked = toolchain.walk_files(root)
    assert [p for p, _ in walked] == sorted(p for p in root.rglob("*") if p.is_file())
    assert all(p.relative_to(root).as_posix() == r for p, r in walked)
    old = sorted((p for p in root.rglob("*") if p.is_file()),
                 key=lambda p: (p.suffix == ".class", len(p.relative_to(root).parts), str(p)))
    assert toolchain.scan_order(root) == old and toolchain.scan_order(root, cap=2) == old[:2]
    assert toolchain.walk_files(root / "missing") == []
print("ok  walk_files/scan_order: same files and order as rglob + sorted(Path), relative strings exact")

# 3) detect: cached by content + name + detector version; a hit skips the scan, a new detector version rescans
orig_cache, orig_one = toolchain.DETECT_CACHE, toolchain._detect_one
calls = []
try:
    with tempfile.TemporaryDirectory() as d:
        toolchain.DETECT_CACHE = Path(d) / "cache.json"
        f = Path(d) / "sample.bin"
        f.write_bytes(b"\x00" * 32 + b"__swift5_protocols" + b"\x00" * 32)
        toolchain._detect_one = lambda p: calls.append(p.name) or orig_one(p)
        first = toolchain.detect([f])
        assert "swift" in first and calls == ["sample.bin"], (first, calls)
        assert toolchain.detect([f]) == first and calls == ["sample.bin"]          # cache hit: no rescan
        f2 = Path(d) / "copy.bin"
        f2.write_bytes(f.read_bytes())
        assert toolchain.detect([f2]) == {"swift": ["copy.bin"]} and calls[-1] == "copy.bin"   # name is in the key
        f.write_bytes(b"\x00" * 80)                                               # new bytes -> rescan, no hit
        assert toolchain.detect([f]) == {} and calls[-1] == "sample.bin"
        toolchain._DETECT_VER, saved = "otherver", toolchain._detect_ver()
        n = len(calls)
        toolchain.detect([f])
        assert len(calls) == n + 1 and all(k.startswith("otherver:") for k in json.loads(toolchain.DETECT_CACHE.read_text()))
        toolchain._DETECT_VER = saved
finally:
    toolchain.DETECT_CACHE, toolchain._detect_one = orig_cache, orig_one
print("ok  toolchain.detect: content-keyed cache (hit skips the scan; new bytes / name / detector version rescan)")

# 4) reuse race: ONE confirmed_answers lookup per bisect step (it was one per FIELD: 855 x 572 KB start.json = 18 s)
ids = [f"f{i}" for i in range(400)]
lookups = []
saved = {k: getattr(cli, k) for k in ("load", "confirmed_answers", "submit", "is_complete")}
saved_plan, saved_art = solvers.reuse_plan, timed.latest_artifacts
state = {"done": False}
try:
    cli.load = lambda cid, name: {"answer_ids": ids}
    cli.confirmed_answers = lambda cid, att=None: lookups.append(1) or ({a: "v" for a in ids} if state["done"] else {})
    cli.is_complete = lambda cid: state["done"]

    def fake_submit(cid, group, **kw):
        state["done"] = True
        return "correct", {}, []
    cli.submit = fake_submit
    solvers.reuse_plan = lambda *a, **k: {"high": {a: "v" for a in ids}, "spec": {}, "runs": [1, 2, 3], "best": None}
    timed.latest_artifacts = lambda cid: Path("/nonexistent")
    ch = object.__new__(orchestrate.Chain)
    ch.base, ch.lane, ch.sdir = "b", "script-analysis", Path("/nonexistent/solver")
    ch._race_snapshot = lambda *a: None
    orchestrate.set_state, _ss = (lambda *a, **k: None), orchestrate.set_state
    orchestrate.say, _say = (lambda *a, **k: None), orchestrate.say
    try:
        ch._reuse_race("cid")
    finally:
        orchestrate.set_state, orchestrate.say = _ss, _say
finally:
    for k, v in saved.items():
        setattr(cli, k, v)
    solvers.reuse_plan, timed.latest_artifacts = saved_plan, saved_art
assert state["done"] and len(lookups) <= 3, len(lookups)
print(f"ok  reuse race: {len(lookups)} confirmed lookup(s) for a 400-field set (was one per field)")

# 5) remote.gm: start / submit go through the run's warm Homebase daemon first; a submit the daemon may have sent
#    without a verdict is "outcome unknown" (never re-POSTed by another transport); a start falls back
from hctf import remote  # noqa: E402


class FakeDaemon:
    def __init__(self, err=None):
        self.err, self.calls = err, []

    def alive(self):
        return True

    def call(self, op, timeout=60, **kw):
        self.calls.append((op, kw))
        if self.err:
            raise workers.DaemonError(self.err)
        return {"ok": True, "http": 200, "body": {"result": "CORRECT"}, "elapsed": 0.2, "retries": 0, "slept": 0}


saved_d, saved_pub, saved_local = workers._daemon.get("d"), remote._public_gm, remote._gm_local
saved_via = (remote.START_VIA_HB, remote.SUBMIT_VIA_HB)
fallbacks = []
try:
    remote._public_gm = lambda: True
    remote._gm_local = lambda args, timeout: fallbacks.append(args[0]) or {"http": 200, "body": {}, "transport": "inproc"}
    remote.START_VIA_HB = remote.SUBMIT_VIA_HB = False          # isolate: daemon or the local fallback only
    fd = workers._daemon["d"] = FakeDaemon()
    env = remote.gm("submit", "cid-1", json.dumps({"a": "1"}))
    assert env["transport"] == "hb-daemon" and env["body"]["result"] == "CORRECT" and env["saved"] == []
    assert fd.calls[-1] == ("gm", {"kind": "submit", "cid": "cid-1", "answers": {"a": "1"}})
    assert remote.gm("start", "cid-1")["transport"] == "hb-daemon" and not fallbacks
    workers._daemon["d"] = FakeDaemon("daemon gm timed out after 60s")
    try:
        remote.gm("submit", "cid-1", json.dumps({"a": "1"}))
        raise AssertionError("a submit with no verdict must be outcome-unknown, not resent")
    except remote.Unreachable:
        pass
    assert remote.gm("start", "cid-1")["transport"] == "inproc" and fallbacks == ["start"]   # start: safe fallback
    workers._daemon["d"] = FakeDaemon("daemon not running")
    assert remote.gm("submit", "cid-1", "{}")["transport"] == "inproc"                      # never sent: fallback
    workers._daemon["d"] = None
    assert remote.gm("status", "cid-1")["transport"] == "inproc"
finally:
    workers._daemon["d"] = saved_d
    remote._public_gm, remote._gm_local = saved_pub, saved_local
    remote.START_VIA_HB, remote.SUBMIT_VIA_HB = saved_via
print("ok  remote.gm: start/submit via the warm daemon; unsent -> fallback, sent-without-verdict submit -> Unreachable")

print("\nALL DAY-13 PREP CHECKS PASSED")
