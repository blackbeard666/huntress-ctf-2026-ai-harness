"""hctf/ratebucket.py (account-wide GM request governor) + per-worker scratch isolation.
Run: python3 tests/test_governor.py

The governor is the one thing every worker's GM traffic shares: a 429 anywhere raises a flag that
narrows every worker's fan-out, and an optional hard rate cap is fail-open (it can add latency but
never stall the run). The scratch check proves two workers never share a $TMPDIR."""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

fails = 0


def check(name, cond):
    global fails
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    fails += 0 if cond else 1


# clean slate
os.environ.pop("HCTF_GM_GOVERNOR", None)
os.environ["HCTF_GM_RATE_WINDOW"] = "5"
os.environ["HCTF_GM_RATE_MAX"] = "3"
os.environ["HCTF_GM_ADMIT_MAX_WAIT"] = "0.5"
from hctf import ratebucket as rb  # noqa: E402  (after env so module constants pick it up)
rb.WINDOW, rb.MAX, rb.ADMIT_MAX_WAIT = 5.0, 3, 0.5
rb._STATE.unlink(missing_ok=True)

# --- no pressure: fan-out widths unchanged (clean runs are never slowed) ---
check("no pressure -> pressure() False", rb.pressure() is False)
check("no pressure -> wave_width unchanged", rb.wave_width(12) == 12)

# --- admit under a hard cap: first MAX instant, then bounded fail-open wait, then proceed ---
t = time.time()
for _ in range(3):
    rb.admit()
check("3 admits within cap are instant", time.time() - t < 0.2)
t = time.time()
rb.admit()
dt = time.time() - t
check("4th admit (over cap) waits but is bounded by ADMIT_MAX_WAIT, then proceeds", 0.3 <= dt <= 1.2)

# --- pressure: a 429 narrows fan-out widths ---
rb.note_429()
check("note_429 -> pressure() True", rb.pressure() is True)
check("wave_width halves under pressure (12 -> 6)", rb.wave_width(12) == 6)
check("wave_width respects the floor (3 -> 2, 2 -> 2)", rb.wave_width(3) == 2 and rb.wave_width(2) == 2)

# --- cross-process: the pressure signal is shared via the flock'd state file ---
rb._STATE.unlink(missing_ok=True)
env = dict(os.environ)
env.pop("HCTF_GM_GOVERNOR", None)
subprocess.check_call([sys.executable, "-c", "from hctf import ratebucket as r; r.note_429()"], cwd=str(ROOT), env=env)
out = subprocess.check_output([sys.executable, "-c", "from hctf import ratebucket as r; print(r.pressure(), r.wave_width(12))"],
                              cwd=str(ROOT), env=env).decode().strip()
check("one process's 429 is seen by another process", out == "True 6")

# --- disabled: every call is a no-op (fail-open escape hatch) ---
env2 = dict(os.environ, HCTF_GM_GOVERNOR="0")
out2 = subprocess.check_output([sys.executable, "-c",
    "from hctf import ratebucket as r; r.note_429(); print(r.pressure(), r.wave_width(12))"],
    cwd=str(ROOT), env=env2).decode().strip()
check("HCTF_GM_GOVERNOR=0 disables everything", out2 == "False 12")
rb._STATE.unlink(missing_ok=True)

# --- 1B: each worker gets its OWN scratch dir (no shared $TMPDIR clobber) ---
from hctf import workers  # noqa: E402
a = workers._worker_env({"HCTF_STAGE": "single_solve"})["TMPDIR"]
b = workers._worker_env({"HCTF_STAGE": "single_solve"})["TMPDIR"]
check("two workers get DIFFERENT $TMPDIR", a != b)
check("each $TMPDIR exists and is under the project .run/tmp",
      os.path.isdir(a) and os.path.isdir(b) and "/.run/tmp/" in a)
for d in (a, b):
    try:
        os.rmdir(d)
    except OSError:
        pass

print(f"\n{'ALL PASS' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
