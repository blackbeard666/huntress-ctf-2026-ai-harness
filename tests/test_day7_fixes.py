"""Behavior checks for the Day 7 harness fixes (offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_day7_fixes.py      (exit 0 = all pass)
"""
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hctf import orchestrate, timed, triage  # noqa: E402
from lib.common import find_artifact  # noqa: E402

# 1) find_artifact: a bundle zip saved under its FIRST member's name ('blob-01.txt') resolves to that member, not to
#    the whole zip (warmups Mastery set1 answered from the bundle's raw bytes); other members and real .zip names keep
#    their old behavior.
d = Path(tempfile.mkdtemp())
with zipfile.ZipFile(d / "blob-01.txt", "w") as z:
    for i in (1, 2, 3):
        z.writestr(f"blob-0{i}.txt", f"01\tbody {i}\n")
with zipfile.ZipFile(d / "evidence.zip", "w") as z:
    z.writestr("evidence.zip", b"inner")
    z.writestr("readme.txt", b"x")
assert find_artifact(d, "blob-01.txt") == b"01\tbody 1\n", find_artifact(d, "blob-01.txt")[:8]
assert find_artifact(d, "blob-03.txt") == b"01\tbody 3\n"
assert find_artifact(d, "evidence.zip")[:2] == b"PK", "a .zip artifact name must still return the zip itself"
print("ok  find_artifact: bundle saved as 'blob-01.txt' -> member blob-01.txt; .zip names unchanged")

# 2) _clock_expiry: a GM-judged wrong answer is the SOLVER even when the clock then ran out.
base = {"result": "expired", "phases": {"solve": 0.2}}
cases = [
    ({}, True),                                                        # answered everything, clock ran out
    ({"missing": ["set3.message"]}, False),                            # solver left a field empty
    ({"full_result": "incorrect"}, False),                             # full submit judged wrong
    ({"per_set": {"set1": {"result": "incorrect"}, "set2": {"result": "accepted"}}}, False),
    ({"per_set": {"set1": {"result": "accepted"}, "set2": {"result": "expired"}}}, True),
]
_orig_last = timed.last_result
try:
    for extra, want in cases:
        timed.last_result = lambda cid, _r={**base, **extra}: _r
        assert orchestrate.Chain._clock_expiry("c") is want, (extra, want)
finally:
    timed.last_result = _orig_last
print("ok  _clock_expiry: false on missing / full incorrect / any per-set incorrect; true on a pure clock expiry")

# 3) timed_stage: pure clock expiries are RETRIED (up to CLOCK_RETRIES), not blocked after the first one.
ch = object.__new__(orchestrate.Chain)
ch.base, ch.entries, ch.sdir = "b", {"mastery": {"id": "b/mastery"}}, d
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
results = iter(["expired", "expired", "expired", "correct"])
calls = []
patches = {
    (orchestrate, "set_state"): lambda *a, **k: None,
    (orchestrate, "record_timed_case"): lambda *a, **k: None,
    (orchestrate, "say"): lambda *a, **k: None,
    (orchestrate.cli, "is_complete"): lambda cid: False,
    (orchestrate.cli, "gm_solved"): lambda cid: False,
    (timed, "run"): lambda cid, sdir, log=None: (calls.append(cid), next(results))[1],
    (timed, "last_result"): lambda cid: {"result": "expired", "phases": {"solve": 0.1}, "window": 9, "in_window": 9.2},
    (orchestrate.time, "sleep"): lambda s: None,
}
saved = {k: getattr(*k) for k in patches}
try:
    for (mod, name), fn in patches.items():
        setattr(mod, name, fn)
    assert ch.timed_stage("mastery") is True and len(calls) == 4, calls
finally:
    for (mod, name), fn in saved.items():
        setattr(mod, name, fn)
print("ok  timed_stage: 3 clock expiries retried, 4th attempt correct (no block after the first expiry)")

# 4) binary recon: bundled JVM library classes are skipped (and counted) BEFORE the 400-file cap; app classes kept.
r = Path(tempfile.mkdtemp())
(r / "app_x" / "kotlin" / "collections").mkdir(parents=True)
for i in range(450):
    (r / "app_x" / "kotlin" / "collections" / f"K{i:03}.class").write_bytes(b"\xca\xfe\xba\xbe")
(r / "app_x" / "zApp.class").write_bytes(b"\xca\xfe\xba\xbe")      # sorts AFTER 'kotlin/': lost under the old cap
out = "\n".join(triage._recon("binary-reverse-engineering-x", r))
assert "skipped 450 bundled library .class files: kotlin/ x450" in out, out[:300]
assert "zApp.class" in out and "K000.class" not in out, out[:300]
print("ok  binary recon: 450 kotlin/ classes skipped + counted; the app class survives the cap")
