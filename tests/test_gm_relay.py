"""D24 #13 GM relay channels + measured routing (hctf/gmroute.py, workers.hb_relays), offline: fake channels, no VM.
- the critical property: a submit is NEVER sent twice -- any relay failure after the request left -> Unreachable,
  today's path is not called; only a request the relay never took (channel down / write failed) goes today's way
- start: any relay failure -> today's path (it resumes the attempt); status: hedged, first judged reply wins
- D25 B2: start hedged (faster path first, the other after HEDGE_START_S unless the first failed); a reply sized
  > 32 KB by TODAY's <mode>/contract.json goes today's path alone; differing attempt ids -> `!!!`
- decide(): relay only when its average < 0.8 x local - 0.1 s; unmeasured -> local; > 32 KB request/reply -> local
- kill switch HCTF_GM_RELAY=0 / not activated / a replay's stand-in GM: remote.gm = today's path, gmroute untouched
- hb_relays(): 2 channels, own ssh connection (no ControlMaster), INSIDE_GM, NO bearer; two missed pings = down

Run:  source bin/env.sh && python3 tests/test_gm_relay.py      (exit 0 = all pass)
"""
import contextlib
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import gmroute, remote, workers  # noqa: E402

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


class Chan:
    """A relay channel stand-in: `behave(kw)` -> reply dict or raises."""

    def __init__(self, behave, delay=0.0, k=0):
        self.behave, self.delay, self.k, self.busy, self.calls = behave, delay, k, 0, []

    def alive(self):
        return True

    def call(self, op, timeout=60, **kw):
        self.calls.append((op, kw))
        time.sleep(self.delay)
        return self.behave(kw)


def ok_reply(kw):
    return {"ok": True, "http": 200, "body": {"result": "correct", "op": kw["kind"]}, "elapsed": 0.05}


def reset(relay=None, local=None, op="status"):
    gmroute._avg.clear()
    gmroute._reply.clear()
    gmroute._state["decision"].clear()
    if relay is not None:
        gmroute.record(op, "relay", relay)
    if local is not None:
        gmroute.record(op, "local", local)


local_calls = []


def local_fn_factory(env=None, delay=0.0):
    def fn():
        local_calls.append(1)
        time.sleep(delay)
        return dict(env or {"http": 200, "body": {"result": "local"}, "transport": "inproc"})
    return fn


QUIET = {(gmroute, "_say"): lambda m: None}
SUB = ["submit", "warmups-day-25-x", json.dumps({"q1": "a"})]

# ---------------------------------------------------------------- 1. submit is never resent
for label, exc in (("a timeout after send", workers.DaemonError("daemon gm timed out after 60s")),
                   ("a channel closed mid-request", workers.DaemonError("daemon channel closed")),
                   ("the VM's GM call failing", workers.DaemonError("ConnectionResetError: reset"))):
    def boom(kw, exc=exc):
        raise exc
    ch = Chan(boom)
    local_calls.clear()
    reset(relay=0.1, local=2.0)
    with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
        try:
            gmroute.call(SUB, 30, local_fn_factory())
            raised = None
        except remote.Unreachable as e:
            raised = e
    check(f"1 submit + {label}: Unreachable, today's path never called, ONE relay request",
          raised is not None and not local_calls and len(ch.calls) == 1 and "never resent" in str(raised),
          (raised, local_calls, ch.calls))

ch = Chan(lambda kw: {"ok": True, "http": 0, "body": "connection refused"})
local_calls.clear()
reset(relay=0.1, local=2.0)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    try:
        gmroute.call(SUB, 30, local_fn_factory())
        raised = None
    except remote.Unreachable as e:
        raised = e
check("1 submit + http 0 from the VM's GM: Unreachable, never resent", raised is not None and not local_calls)

for msg in ("daemon not running", "daemon write failed: broken pipe"):
    def notsent(kw, msg=msg):
        raise workers.DaemonError(msg)
    ch = Chan(notsent)
    local_calls.clear()
    reset(relay=0.1, local=2.0)
    with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
        env = gmroute.call(SUB, 30, local_fn_factory())
    check(f"1 submit the relay never took ({msg.split(':')[0]}): today's path, exactly once",
          env.get("body", {}).get("result") == "local" and len(local_calls) == 1, (env, local_calls))

ch = Chan(ok_reply)
local_calls.clear()
reset(relay=0.1, local=2.0)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    env = gmroute.call(SUB, 30, local_fn_factory())
check("1 submit via the relay: one request, the answers passed as a dict, transport `relay0`, no bearer in it",
      len(ch.calls) == 1 and ch.calls[0][1]["answers"] == {"q1": "a"} and env["transport"] == "relay0"
      and not local_calls and "token" not in json.dumps(ch.calls), (ch.calls, env))

# ---------------------------------------------------------------- 2. start falls back; status hedged
ch = Chan(lambda kw: (_ for _ in ()).throw(workers.DaemonError("daemon gm timed out after 60s")))
local_calls.clear()
reset(relay=0.1, local=2.0)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch, (gmroute, "_size_ok"): lambda a: True}):
    env = gmroute.call(["start", "warmups-day-25-x"], 30, local_fn_factory())
check("2 start: relay failure -> today's path (start resumes the attempt)",
      env["body"]["result"] == "local" and len(local_calls) == 1)
check("2 ... and the failure pushes the relay's start average up", (gmroute.avg("start", "relay") or 0) >= 5.0 * 0.3)

ch = Chan(ok_reply, delay=0.05)
local_calls.clear()
reset()
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    t0 = time.time()
    env = gmroute.call(["status", "warmups-day-25-x"], 30, local_fn_factory(delay=0.6))
    took = time.time() - t0
check("2 status hedged: both paths sent, the faster relay reply returns at once",
      env["transport"] == "relay0" and took < 0.4 and len(ch.calls) == 1, (env, took))
time.sleep(0.7)
check("2 ... the slower local reply still lands in the averages",
      gmroute.avg("status", "local") is not None and gmroute.avg("status", "relay") is not None)

ch = Chan(lambda kw: (_ for _ in ()).throw(workers.DaemonError("boom")))
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    env = gmroute.call(["status", "x-day-25-y"], 30, local_fn_factory(delay=0.1))
check("2 status: relay raising -> the local reply", env["body"]["result"] == "local")

ch = Chan(ok_reply, delay=0.2)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    env = gmroute.call(["status", "x-day-25-y"], 30,
                       local_fn_factory(env={"http": 429, "body": {"error": "rate"}, "transport": "inproc"}))
check("2 status: a local 429 (unjudged) does not win over the relay's judged reply", env.get("http") == 200, env)

ch = Chan(lambda kw: {"ok": True, "http": 404, "body": {"error": "not_found"}}, delay=0.0)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    t0 = time.time()
    env = gmroute.call(["status", "warmups-day-25"], 30,
                       local_fn_factory(env={"http": 409, "body": {"error": "start_required"}}, delay=0.3))
check("2 status: a fast 404 (a proxy lagging the drop) never masks the other path's 409 (release probe)",
      env.get("http") == 409 and time.time() - t0 >= 0.25, env)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    env = gmroute.call(["status", "warmups-day-25"], 30,
                       local_fn_factory(env={"http": 404, "body": {"error": "not_found"}}, delay=0.1))
check("2 status: both 404 -> 404 (not released yet)", env.get("http") == 404, env)

# ---------------------------------------------------------------- 2b. start hedged (D25 B2)
SMALL = {(gmroute, "_size_ok"): lambda a: True, (gmroute, "HEDGE_START_S"): 0.3}
ch = Chan(lambda kw: (_ for _ in ()).throw(workers.DaemonError("daemon gm timed out after 60s")), delay=5.0)
local_calls.clear()
reset(relay=0.1, local=2.0)
with patched({**QUIET, **SMALL, (gmroute, "_chan"): lambda: ch}):
    t0 = time.time()
    env = gmroute.call(["start", "script-analysis-day-25-x/mastery"], 30, local_fn_factory(delay=0.1))
    took = time.time() - t0
check("2b start: a relay channel that hangs (D25 38 s) -> today's path answers after the hedge lag, not the timeout",
      env["body"]["result"] == "local" and took < 1.5 and len(local_calls) == 1, (env, took))

ch = Chan(ok_reply, delay=0.05)
local_calls.clear()
reset(relay=0.1, local=2.0)
with patched({**QUIET, **SMALL, (gmroute, "_chan"): lambda: ch}):
    env = gmroute.call(["start", "warmups-day-25-x/time_trial"], 30, local_fn_factory(delay=0.1))
time.sleep(0.5)
check("2b start: the faster relay answers inside the lag -> the second start is NEVER sent",
      env["transport"] == "relay0" and not local_calls and len(ch.calls) == 1, (env, local_calls, ch.calls))

ch = Chan(ok_reply, delay=0.05)
local_calls.clear()
reset(relay=3.0, local=1.0)
with patched({**QUIET, **SMALL, (gmroute, "_chan"): lambda: ch}):
    env = gmroute.call(["start", "warmups-day-25-x/time_trial"], 30, local_fn_factory(delay=0.05))
time.sleep(0.5)
check("2b start: local measured faster -> local goes first, the relay never sent",
      env["body"]["result"] == "local" and len(local_calls) == 1 and not ch.calls, (env, ch.calls))

ch = Chan(lambda kw: (_ for _ in ()).throw(workers.DaemonError("daemon not running")))
local_calls.clear()
reset(relay=0.1, local=2.0)
with patched({**QUIET, **SMALL, (gmroute, "_chan"): lambda: ch, (gmroute, "HEDGE_START_S"): 5.0}):
    t0 = time.time()
    env = gmroute.call(["start", "warmups-day-25-x/time_trial"], 30, local_fn_factory())
    took = time.time() - t0
check("2b start: the first path FAILING starts the second at once (no wait for the lag)",
      env["body"]["result"] == "local" and took < 1.0, (env, took))

said = []
ch = Chan(lambda kw: {"ok": True, "http": 200, "body": {"attempt_id": "bbbbbbbb-2"}}, delay=0.4)
local_calls.clear()
reset(relay=3.0, local=1.0)
with patched({(gmroute, "_say"): said.append, **SMALL, (gmroute, "_chan"): lambda: ch, (gmroute, "HEDGE_START_S"): 0.1}):
    env = gmroute.call(["start", "warmups-day-25-x/time_trial"], 30,
                       local_fn_factory(env={"http": 503, "body": {"error": "x"}}, delay=0.3))
    time.sleep(0.1)
check("2b start: an unjudged local 503 does not win; the relay's judged reply does", env.get("http") == 200, env)
ch = Chan(lambda kw: {"ok": True, "http": 200, "body": {"attempt_id": "bbbbbbbb-2"}}, delay=0.4)
with patched({(gmroute, "_say"): said.append, **SMALL, (gmroute, "_chan"): lambda: ch, (gmroute, "HEDGE_START_S"): 0.1}):
    env = gmroute.call(["start", "warmups-day-25-x/time_trial"], 30,
                       local_fn_factory(env={"http": 200, "body": {"attempt_id": "aaaaaaaa-1"}}, delay=0.15))
    time.sleep(0.6)
check("2b start: two different attempt ids -> the first wins and a `!!!` line names both",
      env["body"]["attempt_id"] == "aaaaaaaa-1" and any(m.startswith("!!!") and "bbbbbbbb" in m for m in said), said)

with patched({**QUIET, (gmroute, "_chan"): lambda: Chan(ok_reply), (gmroute, "START_HEDGE"): False,
              (gmroute, "_size_ok"): lambda a: True}):
    reset(relay=0.1, local=2.0)
    local_calls.clear()
    env = gmroute.call(["start", "warmups-day-25-x/time_trial"], 30, local_fn_factory())
check("2b HCTF_GM_START_HEDGE=0: the old relay-only start", env["transport"] == "relay0" and not local_calls)

# start sizing from TODAY's status-time contract (<mode dir>/contract.json), not an earlier day's start.json
import tempfile  # noqa: E402
from hctf import paths  # noqa: E402
_tmpc = Path(tempfile.mkdtemp(prefix="gmroute-contract-"))
(_tmpc / "day25" / "scripting-x" / "mastery").mkdir(parents=True)
(_tmpc / "day25" / "scripting-x" / "time_trial").mkdir(parents=True)
(_tmpc / "day25" / "scripting-x" / "mastery" / "contract.json").write_text("x" * 200_000)
(_tmpc / "day25" / "scripting-x" / "time_trial" / "contract.json").write_text("x" * 9_000)
_idx = {"script-analysis-day-25-x": {"dir": "day25/scripting-x", "day": 25, "lane": "script-analysis"}}
with patched({(paths, "CHALLENGES"): _tmpc, (paths, "lookup"): lambda cid: _idx.get(paths.base_id(cid))}):
    gmroute._reply.clear()
    gmroute._reply[("start", "script-analysis/mastery")] = 1_000      # an earlier day's small start: must not decide
    big_ok = gmroute._size_ok(["start", "script-analysis-day-25-x/mastery"])
    small_ok = gmroute._size_ok(["start", "script-analysis-day-25-x/time_trial"])
    none = gmroute._contract_bytes("script-analysis-day-25-x")
    ch = Chan(ok_reply)
    local_calls.clear()
    reset(relay=0.1, local=2.0)
    with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
        gmroute.call(["start", "script-analysis-day-25-x/mastery"], 30, local_fn_factory())
check("2b today's 200 KB Mastery contract -> too big for the relay (an earlier day's 1 KB start is ignored)",
      big_ok is False and small_ok is True, (big_ok, small_ok))
check("2b no contract on disk for the mode -> None (the earlier-day estimate decides)", none is None, none)
check("2b a big start goes today's path ALONE (no relay request, no hedge)", not ch.calls and len(local_calls) == 1,
      (ch.calls, local_calls))
gmroute._reply.clear()

# ---------------------------------------------------------------- 3. decide + size limits
reset(relay=0.2, local=1.4)
check("3 relay 0.2 s vs local 1.4 s -> relay", gmroute.decide("submit") == "relay")
reset(relay=1.1, local=1.4)
check("3 relay 1.1 s vs local 1.4 s (> 0.8 x 1.4 - 0.1) -> local", gmroute.decide("submit") == "local")
reset()
check("3 unmeasured -> local", gmroute.decide("submit") == "local")
reset(relay=0.2, local=1.4)
gmroute.record("submit", "relay", 3.0)
gmroute.record("submit", "local", 1.0)
check("3 the op's own averages (both sides) beat the status calibration", gmroute.decide("submit") == "local")

ch = Chan(ok_reply)
local_calls.clear()
reset(relay=0.1, local=2.0)
big = ["submit", "script-analysis-day-25-x", json.dumps({f"q{i}": "v" * 40 for i in range(800)})]
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    gmroute.call(big, 30, local_fn_factory())
check("3 a > 32 KB submit goes today's path", not ch.calls and len(local_calls) == 1)
gmroute._reply[("start", "script-analysis")] = 650_000
local_calls.clear()
with patched({**QUIET, (gmroute, "_chan"): lambda: ch}):
    gmroute.call(["start", "script-analysis-day-25-x"], 30, local_fn_factory())
check("3 a start whose lane's reply was 650 KB goes today's path", not ch.calls and len(local_calls) == 1)
check("3 shape key: lane + mode across days", gmroute._shape("binary-reverse-engineering-day-25-abc/mastery")
      == "binary-reverse-engineering/mastery" and gmroute._shape("warmups-day-03-x") == "warmups")
gmroute._reply.clear()

# ---------------------------------------------------------------- 4. kill switch / not active / replay through remote.gm
hits = []
with patched({(remote, "gm_transport"): lambda: "local", (remote, "_gm_public"): lambda a, t: {"http": 200, "body": "today", "transport": "inproc"},
              (gmroute, "call"): lambda *a, **k: hits.append(a) or {"http": 200, "body": "routed"}}):
    gmroute._state["active"] = True
    try:
        with patched({(remote, "GM_RELAY"): False}):
            e1 = remote.gm(*SUB)
        e2 = remote.gm(*SUB)
        with patched({(gmroute, "RELAY"): False}):
            e3 = remote.gm("status", "x")
        os.environ["HUNTRESS_GAME_MASTER_URL"] = "http://127.0.0.1:9"
        try:
            e4 = remote.gm("status", "x")
        finally:
            os.environ.pop("HUNTRESS_GAME_MASTER_URL", None)
        e5 = remote.gm("list", "--day", "25")
    finally:
        gmroute._state["active"] = False
    e6 = remote.gm("status", "x")
check("4 HCTF_GM_RELAY=0 (remote.GM_RELAY False): today's path, gmroute never called", e1["body"] == "today")
check("4 relay on + active: remote.gm hands status/start/submit to gmroute", e2["body"] == "routed" and len(hits) == 1)
check("4 gmroute.RELAY off: today's path", e3["body"] == "today")
check("4 a replay's stand-in GM: today's path", e4["body"] == "today")
check("4 other ops (list) never routed", e5["body"] == "today")
check("4 not activated (workers, hb_timed, CLI processes): today's path", e6["body"] == "today" and len(hits) == 1)

with patched({(gmroute, "RELAY"): False}):
    check("4 activate() is a no-op with the relay off", gmroute.activate() is False)
os.environ["HUNTRESS_GAME_MASTER_URL"] = "http://127.0.0.1:9"
try:
    check("4 activate() is a no-op against a replay's stand-in GM", gmroute.activate() is False)
finally:
    os.environ.pop("HUNTRESS_GAME_MASTER_URL", None)
out = subprocess.run([sys.executable, "-m", "hctf.gmroute", "calibrate"], capture_output=True, text=True, cwd=str(ROOT),
                     env={**os.environ, "HCTF_GM_RELAY": "0"}, timeout=60).stdout
check("4 `gmroute calibrate` with HCTF_GM_RELAY=0 prints SKIP and touches nothing", out.startswith("SKIP relay off"), out)

# ---------------------------------------------------------------- 5. hb_relays: channels, pings, no bearer
made = []


class FakeDaemon:
    def __init__(self, log=print, argv=None, gm_url=None, token=None):
        made.append({"argv": argv, "gm": gm_url, "token": token})
        self.gm, self.dead, self.pings = gm_url, False, 0

    def alive(self):
        return True

    def call(self, op, timeout=60, **kw):
        self.pings += 1
        if self.dead:
            raise workers.DaemonError("daemon ping timed out after 1.5s")
        return {"ok": True}

    def close(self):
        pass


logs = []
with patched({(workers, "HbDaemon"): FakeDaemon, (workers, "RELAY_PING_S"): 0.05, (workers, "RELAY_RETRY_S"): 60,
              (workers, "_relays"): {"chans": [], "thread": None, "failed_at": 0.0},
              (workers, "start_homebase_health"): lambda log=print: None}):
    workers._hb.update(ok=True, provisioned=True)
    try:
        workers.hb_relays(logs.append)
        end = time.time() + 3
        while len(workers.hb_relays(start=False)) < 2 and time.time() < end:
            time.sleep(0.02)
        chans = workers.hb_relays(start=False)
        check("5 two relay channels come up", len(chans) == 2, (len(chans), logs[-3:]))
        check("5 each talks to the VM's inside proxy with NO bearer",
              all(m["gm"] == remote.INSIDE_GM and m["token"] is None for m in made), made)
        check("5 each on its own ssh connection (no ControlMaster), via hb_daemon --stdio",
              all("ControlMaster=no" in m["argv"] and "ControlPath=none" in m["argv"] and "hb_daemon.py --stdio" in m["argv"][-1]
                  for m in made))
        time.sleep(0.2)
        check("5 pinged every RELAY_PING_S", all(c.d.pings >= 2 for c in chans), [c.d.pings for c in chans])
        chans[0].d.dead = True
        end = time.time() + 2
        while len(workers.hb_relays(start=False)) > 1 and time.time() < end:
            time.sleep(0.02)
        check("5 two missed pings -> that channel is down (dropped; the other stays)",
              len(workers.hb_relays(start=False)) == 1 and any("down (2 missed pings)" in m for m in logs), logs[-3:])
        check("5 the retry waits RELAY_RETRY_S (no reconnect storm)", len(made) == 2, len(made))
    finally:
        workers._hb.update(ok=False, provisioned=False)
        workers.RELAY_CHANNELS = 0    # park the keeper thread (it keeps running in this process)

print(f"\n{len(failures)} failure(s)" + (": " + ", ".join(failures) if failures else ""))
sys.exit(1 if failures else 0)
