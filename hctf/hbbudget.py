"""Homebase credit ledger: the account gets HCTF_HB_DAILY_CREDITS (60) per day, and BOTH the VM's runtime (2 credits/h)
and the Bedrock AI the VM's instance role pays for (Claude Code on Homebase) draw from it. Nothing on the VM or the
GM reports the balance (the CourseStack API needs the browser session, which the rehearsal copy doesn't have), so this keeps
our own estimate:

  vm  -- per VM boot (`uptime -s`), the span we saw it running: (last_seen - boot) x VM_RATE
  ai  -- each Homebase worker's reported list-price cost (claude `total_cost_usd`) x CREDITS_PER_USD

CREDITS_PER_USD is a calibration constant (credits per list-price USD): read the CourseStack balance before and after a
metered Bedrock run and set HCTF_HB_CREDITS_PER_USD. 1.0 until measured (conservative if a credit is worth >= $1).
The ledger day starts at the drop (13:00 UTC = 9 AM ET), so a day's whole run + ratchet lands in one budget.
"""
import datetime as dt
import fcntl
import json
import os
import time
from contextlib import contextmanager

from .paths import RUN

LEDGER = RUN / "hb_ledger.jsonl"
DAILY = float(os.environ.get("HCTF_HB_DAILY_CREDITS", "60"))
VM_RATE = float(os.environ.get("HCTF_HB_VM_RATE", "2"))             # credits per VM hour (gbPerRuntime=2)
CREDITS_PER_USD = float(os.environ.get("HCTF_HB_CREDITS_PER_USD", "1.0"))
VM_RESERVE = float(os.environ.get("HCTF_HB_VM_RESERVE", "6"))       # kept back for VM uptime still to come today
RESET_UTC_HOUR = int(os.environ.get("HCTF_HB_RESET_UTC_HOUR", "13"))


def day_key(ts=None):
    t = dt.datetime.fromtimestamp(ts if ts is not None else time.time(), dt.timezone.utc)
    return (t - dt.timedelta(hours=RESET_UTC_HOUR)).date().isoformat()


def _day_start(key):
    d = dt.datetime.fromisoformat(key).replace(tzinfo=dt.timezone.utc)
    return (d + dt.timedelta(hours=RESET_UTC_HOUR)).timestamp()


@contextmanager
def _locked():
    RUN.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield f
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _rows():
    try:
        lines = LEDGER.read_text().splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def record_ai(usd, what, detail=None):
    """One Homebase LLM run's list-price cost (USD)."""
    if not usd:
        return
    with _locked() as f:
        f.write(json.dumps({"ts": time.time(), "kind": "ai", "usd": round(float(usd), 4),
                            "credits": round(float(usd) * CREDITS_PER_USD, 4), "what": what,
                            **({"detail": detail} if detail else {})}) + "\n")


def record_vm(boot_ts, seen_ts=None):
    """The VM (booted at boot_ts) was seen running now. Rows are cheap; spend() keeps the max span per boot."""
    with _locked() as f:
        f.write(json.dumps({"ts": seen_ts or time.time(), "kind": "vm", "boot": int(boot_ts)}) + "\n")


def spend(key=None):
    """{'vm': credits, 'ai': credits, 'total', 'left', 'vm_hours', 'ai_usd', 'runs'} for one ledger day."""
    key = key or day_key()
    lo = _day_start(key)
    hi = lo + 86400
    boots, ai_c, ai_usd, runs = {}, 0.0, 0.0, 0
    for r in _rows():
        if r.get("kind") == "vm":
            b, s = r.get("boot"), r.get("ts", 0)
            if b is None or s < lo or b >= hi:
                continue
            boots[b] = max(boots.get(b, 0), s)
        elif r.get("kind") == "ai" and lo <= r.get("ts", 0) < hi:
            ai_c += r.get("credits", 0)
            ai_usd += r.get("usd", 0)
            runs += 1
    vm_h = sum(max(0.0, min(seen, hi) - max(boot, lo)) for boot, seen in boots.items()) / 3600
    vm_c = vm_h * VM_RATE
    total = vm_c + ai_c
    return {"day": key, "vm": round(vm_c, 2), "vm_hours": round(vm_h, 2), "ai": round(ai_c, 2),
            "ai_usd": round(ai_usd, 2), "runs": runs, "total": round(total, 2), "left": round(DAILY - total, 2),
            "daily": DAILY}


def allow_ai(est_credits=0.0):
    """May a new Homebase LLM run start? Leaves VM_RESERVE for the VM's own runtime later today."""
    s = spend()
    return s["total"] + est_credits + VM_RESERVE <= DAILY, s


def ai_cap_usd(default_usd):
    """Per-run --max-budget-usd: the configured cap, shrunk to what the day still has (never below $0.5)."""
    s = spend()
    room = (DAILY - VM_RESERVE - s["total"]) / max(CREDITS_PER_USD, 1e-6)
    return round(max(0.5, min(default_usd, room)), 2)


def summary_line(key=None):
    s = spend(key)
    return (f"Homebase credits {s['day']}: {s['total']:.1f}/{s['daily']:.0f} used "
            f"(VM {s['vm']:.1f} = {s['vm_hours']:.2f} h; AI {s['ai']:.1f} = ${s['ai_usd']:.2f} over {s['runs']} runs "
            f"@ {CREDITS_PER_USD:g} cr/$), {s['left']:.1f} left")
