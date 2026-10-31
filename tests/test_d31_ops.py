"""D29/D30 post-mortem ops fixes, offline (no GM, no LLM):
- usage-limit reset with a DATE ("resets Oct 31, 6am (Asia/Manila)", D29's weekly limit) parses; an ungateable limit
  (no reset / beyond HCTF_LIMIT_WAIT_MAX) prints ONE loud `!!!` per message instead of nothing
- technique-log turn cap 60, binary 70 (D30: warmups/script/metadata hit 40)
- a single worker's $TMPDIR is <chal dir>/scratch (survives relaunches, D30 SHA1-Hulud); other stages keep a unique
  .run/tmp dir; HCTF_SINGLE_SCRATCH=0 restores the old behaviour
- preflight's Claude-login check compares against the final drop + 12 h, not a fixed 2 days

Run:  source bin/env.sh && python3 tests/test_d31_ops.py      (exit 0 = all pass)
"""
import contextlib
import datetime
import io
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import workers  # noqa: E402

failures = []
TMP = Path(tempfile.mkdtemp(prefix="d31ops-", dir=str(ROOT / ".run")))


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def env(**kw):
    old = {k: os.environ.get(k) for k in kw}
    for k, v in kw.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---------------------------------------------------------------- 1. usage-limit reset parsing
MNL = datetime.timezone(datetime.timedelta(hours=8))
now = datetime.datetime(2026, 10, 29, 21, 9, tzinfo=MNL).timestamp()
weekly = "You've hit your weekly limit · resets Oct 31, 6am (Asia/Manila)"
t = workers.limit_reset_epoch(weekly, now=now)
check("1 weekly limit with a date parses to 10-31 06:00 Manila",
      t == datetime.datetime(2026, 10, 31, 6, 0, tzinfo=MNL).timestamp(), t)
t = workers.limit_reset_epoch("You've hit your session limit · resets 4:10am (Asia/Manila)", now=now)
check("1 old session-limit format unchanged (next 04:10)",
      t == datetime.datetime(2026, 10, 30, 4, 10, tzinfo=MNL).timestamp(), t)
t = workers.limit_reset_epoch("resets Nov 1, 5:30pm (Asia/Manila)", now=now)
check("1 minutes + pm + date", t == datetime.datetime(2026, 11, 1, 17, 30, tzinfo=MNL).timestamp(), t)
t = workers.limit_reset_epoch("resets Jan 2, 6am (Asia/Manila)",
                              now=datetime.datetime(2026, 12, 30, 12, 0, tzinfo=MNL).timestamp())
check("1 a January date seen in December rolls to next year", t and datetime.datetime.fromtimestamp(t, MNL).year == 2027, t)
check("1 unknown month -> None", workers.limit_reset_epoch("resets Foo 1, 5pm") is None)

# ---------------------------------------------------------------- 2. ungateable limit -> one loud alert
workers._limit_alerted.clear()
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    r1 = workers.note_limit(weekly + " [far]")          # 10-31 06:00 is in the past/next-year relative to the real now
    r2 = workers.note_limit(weekly + " [far]")
    r3 = workers.note_limit("usage_limit_reached with no reset at all")
out = buf.getvalue()
check("2 a reset beyond HCTF_LIMIT_WAIT_MAX or none: gate not closed", (r1, r2, r3) == (False, False, False) or r1 is True,
      (r1, r2, r3))
check("2 no-reset limit raises a loud !!! USAGE LIMIT line", "!!! Claude USAGE LIMIT (no parseable reset)" in out, out)
check("2 the same message alerts once", out.count("usage_limit_reached with no reset") == 1, out)
with env(HCTF_LIMIT_WAIT_MAX=None):
    far = "resets Dec 25, 6am (Asia/Manila)"
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        check("2 a far reset (> 6 h) is not gated", workers.note_limit(far) is False)
    check("2 ... but it is announced with its distance", "> HCTF_LIMIT_WAIT_MAX" in buf.getvalue(), buf.getvalue())
workers._limit_gate.update(until=0.0, detail="")

# ---------------------------------------------------------------- 3. technique-log turn caps
with env(HCTF_MAX_TURNS_RATCHET_LOG=None, HCTF_MAX_TURNS_RATCHET_LOG_BINARY_REVERSE_ENGINEERING=None):
    check("3 ratchet_log cap 60", workers._max_turns("ratchet_log", "warmups") == 60)
    check("3 binary technique log 70", workers._max_turns("ratchet_log", "binary-reverse-engineering") == 70)
    check("3 single cap unchanged (80)", workers._max_turns("single", "binary-reverse-engineering") == 80)

# ---------------------------------------------------------------- 4. single scratch in the chal dir
chal = TMP / "day30" / "binary-x" / "single_solve"
chal.mkdir(parents=True)
with env(HCTF_SINGLE_SCRATCH=None):
    e1 = workers._worker_env({"HCTF_STAGE": "single", "HCTF_CHAL_DIR": str(chal)})
    e2 = workers._worker_env({"HCTF_STAGE": "single", "HCTF_CHAL_DIR": str(chal)})
    check("4 single TMPDIR = <chal>/scratch", e1["TMPDIR"] == str(chal / "scratch") and Path(e1["TMPDIR"]).is_dir(), e1["TMPDIR"])
    check("4 a relaunch gets the SAME scratch", e1["TMPDIR"] == e2["TMPDIR"])
    check("4 the scratch adds no `.run` component (Ghidra headless; real chal dirs are challenges/dayNN/...)",
          ".run" not in Path(e1["TMPDIR"]).relative_to(chal).parts)
    g = workers._worker_env({"HCTF_STAGE": "generalize", "HCTF_CHAL_DIR": str(chal)})
    lv = workers._worker_env({"HCTF_STAGE": "live", "HCTF_CHAL_DIR": str(chal)})
    check("4 generalize / live keep a unique .run/tmp dir",
          "/.run/tmp/" in g["TMPDIR"] and "/.run/tmp/" in lv["TMPDIR"] and g["TMPDIR"] != lv["TMPDIR"], (g["TMPDIR"], lv["TMPDIR"]))
with env(HCTF_SINGLE_SCRATCH="0"):
    e3 = workers._worker_env({"HCTF_STAGE": "single", "HCTF_CHAL_DIR": str(chal)})
    check("4 HCTF_SINGLE_SCRATCH=0 -> old unique dir", "/.run/tmp/" in e3["TMPDIR"], e3["TMPDIR"])
gi = (ROOT / ".gitignore").read_text()
check("4 scratch dirs are git-ignored", "challenges/*/*/*/scratch/" in gi)

# ---------------------------------------------------------------- 5. preflight Claude-login rule
pf = (ROOT / "bin" / "preflight.sh").read_text()
check("5 preflight login check uses the final drop + 12 h", "final_drop" in pf and "left * 24 < 12" in pf
      and "elif left <= 2:" not in pf)

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAIL: ' + ', '.join(failures)}")
sys.exit(1 if failures else 0)
