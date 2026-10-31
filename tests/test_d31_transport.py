"""D31 GM transport (hctf/gmroute.py), offline: fake relay channels, no VM, no GM.

Day 29's three `!!! [gmroute] slow transport: status ...` lines (script TT 905 KB 8.07 s on relay0, binary Mastery
5278 KB 8.08 s on relay0, binary Mastery timed out 15.1 s on relay1) were NOT the routed/hedged status path -- every
big status in that run's log.jsonl went `inproc` -- but the 15 s CALIBRATOR: calibrate_once() named the last cid any
call touched (a just-started big mode) and sent its status on a relay channel with no size check (timeout 15 = the
15.1 s), then a second multi-MB public download for the local sample, and averaged both.
- 1 the D29 sequence: last cid = a multi-MB mode -> the calibrator names a small cid; the big one never rides a relay
- 2 the last routed small status's cid is preferred; a small last cid is still used (unchanged behaviour)
- 3 a calibration reply that turns out big: not averaged, the local leg not sent, never picked again
- 4 explicit cid (preflight `calibrate --cid`) honoured; HCTF_GM_CAL_MAX_KB=0 = the old pick (the last cid)
- 5 the routed status path (unchanged): a predicted-big status (today's contract / the lane's earlier start of the mode
  for a never-seen mode) goes today's path alone; a small one is hedged; a 404 / big reply never becomes the cal cid

Run:  source bin/env.sh && python3 tests/test_d31_transport.py      (exit 0 = all pass)
"""
import contextlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import gmroute, remote  # noqa: E402

failures = []


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


class Chan:
    def __init__(self, nbytes_for=None, k=0):
        self.nbytes_for, self.k, self.busy, self.misses, self.calls = nbytes_for or (lambda cid: 2000), k, 0, 0, []

    def alive(self):
        return True

    def call(self, op, timeout=60, **kw):
        self.calls.append((op, kw, timeout))
        n = self.nbytes_for(kw["cid"])
        return {"ok": True, "http": 409, "body": {"error": "start_required", "blob": "x" * n}, "elapsed": 0.05}


BIG = "binary-reverse-engineering-day-29-variant-diffing/mastery"     # 4.6 MB contract on D29
TT = "script-analysis-day-29-makefile-variant-diff/time_trial"        # 905 KB status / 998 KB contract on D29
SMALL = "web-exploitation-day-27-internal-affairs/mastery"            # ~4 KB
SIZES = {BIG: 4_598_790, TT: 998_354}


def contract(cid):
    return SIZES.get(cid)


def earlier(cid):
    return 0


local_calls = []


def gm_local(args, timeout):
    local_calls.append(list(args))
    n = SIZES.get(str(args[1]), 2000)
    return {"http": 409, "body": {"blob": "x" * n}, "transport": "inproc", "elapsed": 0.1}


def reset():
    gmroute._avg.clear()
    gmroute._reply.clear()
    gmroute._demoted.clear()
    gmroute._state["decision"].clear()
    for k in ("cal_cid", "last_cid"):
        gmroute._state.pop(k, None)
    local_calls.clear()


said = []
BASE = {(gmroute, "_say"): said.append, (gmroute, "_contract_bytes"): contract,
        (gmroute, "_earlier_start_bytes"): earlier, (remote, "_gm_local"): gm_local}

# ---------------------------------------------------------------- 1. the D29 sequence
for big in (BIG, TT):
    reset()
    ch = Chan(lambda cid: SIZES.get(cid, 2000))
    with patched({**BASE, (gmroute, "_chan"): lambda: ch}):
        gmroute._state["last_cid"] = big            # a just-started big mode (D29 21:00:12 / 21:00:37)
        r, l = gmroute.calibrate_once()
    named = [kw["cid"] for _op, kw, _t in ch.calls] + [a[1] for a in local_calls]
    check(f"1 last cid {big.split('-day-')[0]} ({SIZES[big] // 1024} KB): the calibrator never names it on either path",
          big not in named and named == [gmroute.CAL_DEFAULT_CID, gmroute.CAL_DEFAULT_CID], named)
    check("1 ... and both small samples are averaged", r is not None and l is not None
          and gmroute.avg("status", "relay") is not None and gmroute.avg("status", "local") is not None, (r, l))

# the never-seen mode: no contract yet, only the lane's earlier start of the mode (D29 21:00:14, binary Mastery)
reset()
ch = Chan()
with patched({**BASE, (gmroute, "_chan"): lambda: ch, (gmroute, "_contract_bytes"): lambda cid: None,
              (gmroute, "_earlier_start_bytes"): lambda cid: 2_500_235 if "binary" in cid else 0}):
    gmroute._state["last_cid"] = BIG
    gmroute.calibrate_once()
check("1 never-seen big mode (lane history only): not the calibration cid",
      [kw["cid"] for _o, kw, _t in ch.calls] == [gmroute.CAL_DEFAULT_CID], ch.calls)

# ---------------------------------------------------------------- 2. which small cid
reset()
ch = Chan()
with patched({**BASE, (gmroute, "_chan"): lambda: ch}):
    gmroute._note_status_bytes(["status", SMALL], {"http": 200, "body": {"x": "y" * 3000}})
    gmroute._state["last_cid"] = BIG
    gmroute.calibrate_once()
check("2 the last routed small status's cid is the sample (not the big last cid, not the default)",
      [kw["cid"] for _o, kw, _t in ch.calls] == [SMALL] and local_calls == [["status", SMALL]], (ch.calls, local_calls))

reset()
ch = Chan()
with patched({**BASE, (gmroute, "_chan"): lambda: ch}):
    gmroute._state["last_cid"] = SMALL               # small predicted, no routed status yet
    gmroute.calibrate_once()
check("2 a small last cid is still used (unchanged behaviour)", [kw["cid"] for _o, kw, _t in ch.calls] == [SMALL],
      ch.calls)
check("2 the relay sample keeps its 15 s timeout", ch.calls and ch.calls[0][2] == 15, ch.calls)

# ---------------------------------------------------------------- 3. a sample that turns out big
reset()
said.clear()
SURPRISE = "mobile-android-day-31-x/mastery"
ch = Chan(lambda cid: 900_000 if cid == SURPRISE else 2000)
with patched({**BASE, (gmroute, "_chan"): lambda: ch}):
    gmroute._state["last_cid"] = SURPRISE            # nothing predicts it (no contract, no lane history)
    r, l = gmroute.calibrate_once()
check("3 a reply > CAL_MAX: no sample averaged, the local leg not sent",
      (r, l) == (None, None) and gmroute.avg("status", "relay") is None and gmroute.avg("status", "local") is None
      and not local_calls, ((r, l), local_calls, gmroute._avg))
check("3 ... logged as a dropped sample", any("calibration sample dropped" in m for m in said), said)
ch.calls.clear()
with patched({**BASE, (gmroute, "_chan"): lambda: ch}):
    gmroute.calibrate_once()
check("3 ... and learned: the next sample names the default cid",
      [kw["cid"] for _o, kw, _t in ch.calls] == [gmroute.CAL_DEFAULT_CID], ch.calls)

# ---------------------------------------------------------------- 4. explicit cid / kill switch
reset()
ch = Chan(lambda cid: 3000)
with patched({**BASE, (gmroute, "_chan"): lambda: ch}):
    gmroute.calibrate_once("script-analysis-day-25-x")
check("4 explicit cid (preflight `calibrate --cid`) honoured",
      [kw["cid"] for _o, kw, _t in ch.calls] == ["script-analysis-day-25-x"], ch.calls)

reset()
ch = Chan(lambda cid: 2000)
with patched({**BASE, (gmroute, "_chan"): lambda: ch, (gmroute, "CAL_MAX"): 0}):
    gmroute._state["last_cid"] = BIG
    gmroute._state["cal_cid"] = SMALL
    gmroute.calibrate_once()
check("4 HCTF_GM_CAL_MAX_KB=0: the old pick (the last cid, any size)",
      [kw["cid"] for _o, kw, _t in ch.calls] == [BIG], ch.calls)

# ---------------------------------------------------------------- 5. the routed status path
for cid, ctr, lane, label in ((TT, 998_354, 0, "today's contract 998 KB"),
                              (BIG, None, 2_500_235, "never-seen mode, lane's earlier start 2.5 MB")):
    reset()
    ch = Chan()
    with patched({**BASE, (gmroute, "_chan"): lambda: ch, (gmroute, "_contract_bytes"): lambda c, v=ctr: v,
                  (gmroute, "_earlier_start_bytes"): lambda c, v=lane: v}):
        env = gmroute.call(["status", cid], 30, lambda: gm_local(["status", cid], 30))
    check(f"5 routed status, {label}: today's path alone, no relay leg",
          not ch.calls and len(local_calls) == 1 and env.get("transport") == "inproc", (ch.calls, local_calls))
    check("5 ... and a big reply never becomes the calibration cid", gmroute._state.get("cal_cid") is None,
          gmroute._state.get("cal_cid"))

reset()
ch = Chan()
with patched({**BASE, (gmroute, "_chan"): lambda: ch}):
    def slow_local():
        time.sleep(0.3)
        return gm_local(["status", SMALL], 30)
    env = gmroute.call(["status", SMALL], 30, slow_local)
    time.sleep(0.5)
check("5 routed small status: hedged (relay leg sent) and it becomes the cal cid",
      len(ch.calls) == 1 and gmroute._state.get("cal_cid") == SMALL, (ch.calls, gmroute._state.get("cal_cid")))

reset()
with patched(BASE):
    gmroute._note_status_bytes(["status", "warmups-day-31"], {"http": 404, "body": {"error": "not_found"}})
check("5 a 404 status (the release probe before the drop) never becomes the cal cid",
      gmroute._state.get("cal_cid") is None, gmroute._state.get("cal_cid"))

with patched({(gmroute, "STATUS_HEDGE_MAX"): 0, (gmroute, "_contract_bytes"): contract}):
    check("5 HCTF_GM_STATUS_HEDGE_MAX_KB=0 still hedges everything", not gmroute._status_big(["status", BIG]))

print(f"\n{'FAIL' if failures else 'PASS'}: {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
