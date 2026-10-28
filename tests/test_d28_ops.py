"""D28 post-mortem ops/transport fixes (reference/D28_POSTMORTEM.md items 3, 15, 16, 17, 18, 19, 20, 21), offline: fake
relay channels, synthetic trees, no GM, no VM, no sudo.
- 17: technique-log turn cap 34 -> 40, binary 45 (per-lane hook), env precedence lane > stage > table
- 3: _solver_sig prunes cases/ + __pycache__ DURING the walk (never scandirs into them), same signature as the old
  rglob walk; hb_race_prepare with every solver already pushed + warm takes no base-sync lock, no ssh, no warm call
- 15/16: timed_env parses contract.json once per (mtime, size); label hints stale-while-revalidate; the reply-size
  predictors read the meta rows once (gmroute._meta_rows / remote._big_start) with the old answers; lag probe
- 20: a status whose reply is known/predicted > 200 KB never rides the relay; a slow / timed-out relay call demotes its
  channel; a channel with a missed ping is avoided; a busy channel survives missed pings longer; the slow-transport
  `!!!` only for the leg whose reply was used (the losing leg is tagged, no alarm)
- 18: hctf-vpn unit pins the Homebase /32 via --route-up + ExecStartPost (systemd-analyze verify when available)
- 19: the rehearsal sync scripts copy challenges/ (no --link-dest); 21: preflight's skip message names the >= 15 min rule

Run:  source bin/env.sh && python3 tests/test_d28_ops.py      (exit 0 = all pass)
"""
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import gmroute, procgov, remote, workers  # noqa: E402

failures = []
TMP = Path(tempfile.mkdtemp(prefix="d28ops-", dir=str(ROOT / ".run")))


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


@contextlib.contextmanager
def env(**kv):
    old = {k: os.environ.get(k) for k in kv}
    try:
        for k, v in kv.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = str(v)
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---------------------------------------------------------------- 17. technique-log turn cap
with env(HCTF_MAX_TURNS_RATCHET_LOG=None, HCTF_MAX_TURNS_RATCHET_LOG_BINARY_REVERSE_ENGINEERING=None):
    check("17 ratchet_log cap 40 (D28: binary/mobile/metadata hit 34)", workers._max_turns("ratchet_log") == 40
          and workers._max_turns("ratchet_log", "mobile-android") == 40, workers._max_turns("ratchet_log"))
    check("17 binary's technique log: 45 via the per-lane table",
          workers._max_turns("ratchet_log", "binary-reverse-engineering") == 45)
    check("17 other stages unchanged", workers._max_turns("single", "binary-reverse-engineering") == 80
          and workers._max_turns("generalize") == 50 and workers._max_turns("nosuchstage") == 60)
    with env(HCTF_MAX_TURNS_RATCHET_LOG="50"):
        check("17 HCTF_MAX_TURNS_RATCHET_LOG=50 beats the per-lane table (the plan's binary re-run)",
              workers._max_turns("ratchet_log", "binary-reverse-engineering") == 50)
        with env(HCTF_MAX_TURNS_RATCHET_LOG_BINARY_REVERSE_ENGINEERING="55"):
            check("17 a per-lane env beats the stage env", workers._max_turns("ratchet_log", "binary-reverse-engineering") == 55
                  and workers._max_turns("ratchet_log", "warmups") == 50)
    cmd = workers._worker_cmd("ratchet_log", "binary-reverse-engineering", prompt="x")
    check("17 the worker argv carries the lane's cap", cmd[cmd.index("--max-turns") + 1] == "45", cmd[:6])

# ---------------------------------------------------------------- 3. _solver_sig prunes cases/
sol = TMP / "solver"
(sol / "lib").mkdir(parents=True)
(sol / "solve.py").write_text("print(1)\n")
(sol / "lib" / "fam.py").write_text("X = 1\n")
(sol / "__pycache__").mkdir()
(sol / "__pycache__" / "solve.cpython-312.pyc").write_bytes(b"\0" * 10)
(sol / "lib" / "__pycache__").mkdir()
(sol / "lib" / "__pycache__" / "fam.pyc").write_bytes(b"\0")
os.symlink("solve.py", sol / "alias.py")
os.symlink("missing-target", sol / "dangling.py")
for i in range(40):                                  # a heavy regression-case tree (D28: ~300 entries, 4-5 GB)
    d = sol / "cases" / f"auto-{i:03d}" / "artifacts" / "latest"
    d.mkdir(parents=True)
    for j in range(25):
        (d / f"blob-{j:02d}.bin").write_bytes(b"x")
(sol / "lib" / "cases").mkdir()                       # a nested `cases` dir: excluded at any depth, like the old walk
(sol / "lib" / "cases" / "c.py").write_text("")

with patched({(workers, "SIG_PRUNE"): False}):
    old_sig = workers._solver_sig(sol)
seen = []
real_scandir = os.scandir


def spy_scandir(p="."):
    seen.append(str(p))
    return real_scandir(p)


with patched({(workers, "SIG_PRUNE"): True, (os, "scandir"): spy_scandir}):
    new_sig = workers._solver_sig(sol)
check("3 pruned walk = the old rglob signature (cases/, __pycache__, dangling links excluded; file links kept)",
      new_sig == old_sig and {r for r, _m, _s in new_sig} == {"solve.py", "lib/fam.py", "alias.py"}, (new_sig, old_sig))
check("3 ... and it never lists a directory under cases/ or __pycache__",
      seen and not any(re.search(r"/(cases|__pycache__)(/|$)", s) for s in seen), seen)
with patched({(workers, "SIG_PRUNE"): True}):
    t0 = time.perf_counter()
    for _ in range(20):
        workers._solver_sig(sol)
    t_new = (time.perf_counter() - t0) / 20
with patched({(workers, "SIG_PRUNE"): False}):
    t0 = time.perf_counter()
    for _ in range(20):
        workers._solver_sig(sol)
    t_old = (time.perf_counter() - t0) / 20
check(f"3 pruned walk is much cheaper on a 1000-entry cases/ tree ({t_new * 1000:.2f} ms vs {t_old * 1000:.2f} ms)",
      t_new * 5 < t_old, (t_new, t_old))
check("3 push_solver's size counts only the files the push ships",
      sum(st.st_size for _r, st in workers._solver_files(sol)) == sum(s for _r, _m, s in new_sig))

# hb_race_prepare at the drop: every solver already pushed + warm -> no base sync (lock / ssh), no push, no warm
calls = []


class WarmChan:
    k, misses, busy = 0, 0, 0

    def call(self, op, timeout=60, **kw):
        calls.append(op)
        return {"ok": True, "warm_ms": 1.0}


sol2 = TMP / "d27" / "solver"
shutil.copytree(sol, sol2, symlinks=True, ignore=shutil.ignore_patterns("cases"))
chan = WarmChan()
logs = []
fake_root = TMP
with patched({(workers, "hb_race_chan"): lambda log=print: chan, (workers, "ROOT"): fake_root,
              (workers, "_ROOT_RESOLVED"): [],
              (workers, "sync_homebase_base"): lambda force=False: calls.append("sync"),
              (workers, "push_solver"): lambda src, rel: calls.append("push"),
              (workers, "_pushed"): {}, (workers, "_race_ready"): {}}):
    r1 = workers.hb_race_prepare([sol, sol2], logs.append)
    first = list(calls)
    calls.clear()
    r2 = workers.hb_race_prepare([sol, sol2], logs.append)
check("3 hb_race_prepare cold: one base sync, push + warm per solver",
      first.count("sync") == 1 and first.count("push") == 2 and first.count("warm") == 2 and len(r1) == 2, first)
check("3 hb_race_prepare at the drop (pre-drop prepare done): no sync lock, no push, no warm -- just stat walks",
      calls == [] and r2 == r1, calls)
slow_logs = []
with patched({(workers, "hb_race_chan"): lambda log=print: chan, (workers, "ROOT"): fake_root,
              (workers, "_ROOT_RESOLVED"): [], (workers, "HB_RACE_PREP_SLOW_S"): 0.0,
              (workers, "_pushed"): {}, (workers, "_race_ready"): {},
              (workers, "sync_homebase_base"): lambda force=False: None,
              (workers, "push_solver"): lambda src, rel: None}):
    workers.hb_race_prepare([sol], slow_logs.append)
check("3 a slow prepare logs its phase marks (chan / sig / base-sync / push / warm)",
      any(m.startswith("[hb-race] prepare took") and "sig:" in m and "warm:" in m for m in slow_logs), slow_logs)

# ---------------------------------------------------------------- 15/16. kickoff caches + lag probe
from hctf import cli, labels  # noqa: E402

mdir = TMP / "mode"
mdir.mkdir()
contract = {"answer_ids": [f"set{s}.q{i}" for s in range(1, 4) for i in range(50)],
            "artifacts": [{"size": 1000}, {"size": 2000}, "junk"]}
(mdir / "contract.json").write_text(json.dumps(contract))
loads = []
real_loads = json.loads


def counting_loads(s, *a, **k):
    loads.append(len(s))
    return real_loads(s, *a, **k)


with patched({(cli, "cdir"): lambda cid: mdir, (json, "loads"): counting_loads, (workers, "_digests"): {},
              (workers, "GM_POOL_ADAPTIVE"): True}):
    shape = workers._contract_shape("binary-reverse-engineering-day-29-x/mastery")
    pool = workers.gm_pool_size("binary-reverse-engineering-day-29-x/mastery")
    plan = workers.untimed_plan("binary-reverse-engineering-day-29-x/mastery")
    big = [n for n in loads if n > 1000]
check("15 contract digest: shape / pool / plan from ONE parse of contract.json",
      shape == (150, 3000, 3) and pool == 8 and len(big) == 1, (shape, pool, plan, loads))
(mdir / "contract.json").write_text(json.dumps({**contract, "answer_ids": contract["answer_ids"][:10]}) + " ")
with patched({(cli, "cdir"): lambda cid: mdir}):
    shape2 = workers._contract_shape("binary-reverse-engineering-day-29-x/mastery")
check("15 ... a rewritten contract.json (new size/mtime) is re-read", shape2[0] == 10, shape2)
with patched({(cli, "cdir"): lambda cid: TMP / "nope"}):
    check("15 ... no contract -> zeros, like before", workers._contract_shape("x-day-1/mastery") == (0, 0, 0))

(mdir / "last_timed.json").write_text(json.dumps({"attempt_id": "att-1", "ranked_attempts_remaining": 0, "pad": "x" * 5000}))
rows = [{"attempt": "att-0", "kind": "accepted", "answers": {"a": "old"}},
        {"attempt": "att-1", "kind": "accepted", "answers": {"a": "1", "b": ""}},
        {"attempt": "att-1", "kind": "accepted", "answers": {f"p{i}": "x" for i in range(80)}, "harness": True},
        {"attempt": "att-1", "kind": "incorrect", "answers": {"c": "no"}},
        {"attempt": "att-1", "kind": "CORRECT", "answers": {"d": "4"}}]
(mdir / "submissions.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n{torn\n")
loads.clear()
with patched({(cli, "cdir"): lambda cid: mdir, (json, "loads"): counting_loads, (workers, "_digests"): {}}):
    ov1 = workers.live_overlay("m-day-29/mastery")
    n1 = len(loads)
    ov2 = workers.live_overlay("m-day-29/mastery")
    n2 = len(loads) - n1
    e2 = workers.timed_env("m-day-29/mastery")
check("15 live overlay: same answers as before (this attempt's plain accepted/correct submits only)",
      ov1 == ov2 == {"attempt": "att-1", "answers": {"a": "1", "d": "4"}}, ov1)
check("15 ... other attempts' lines are never parsed, and an unchanged file is not re-read", n1 <= 6 and n2 == 0, (n1, n2))
check("15 last_timed digest: ranked_attempts_remaining 0 -> HCTF_RUN_FOR_TIME=0 (as before)",
      e2.get("HCTF_RUN_FOR_TIME") == "0" or "HCTF_RUN_FOR_TIME" in os.environ, e2)

hint_calls = []


def fake_hints():
    hint_calls.append(1)
    return {"_x": {"a": {"b": len(hint_calls)}}}


with patched({(labels, "all_label_hints"): fake_hints, (workers, "LABEL_HINTS_TTL"): 0.2,
              (workers, "_hints_cache"): {"t": 0.0, "js": None, "busy": False}}):
    a = workers._label_hints_json()
    b = workers._label_hints_json()
    time.sleep(0.25)
    t0 = time.perf_counter()
    c = workers._label_hints_json()            # stale: returned at once, refreshed in the background
    stale_s = time.perf_counter() - t0
    time.sleep(0.1)
    d = workers._label_hints_json()
check("15 label hints: one read, reused within the TTL", a == b and len(hint_calls) >= 1 and '"b":1' in a, (a, b))
check("15 ... past the TTL the stale value returns at once and ONE background refresh lands",
      c == a and stale_s < 0.05 and len(hint_calls) == 2 and '"b":2' in d, (c, d, hint_calls))

with patched({(cli, "cdir"): lambda cid: mdir}):
    e = workers.timed_env("binary-reverse-engineering-day-29-x/mastery")
    br = workers._env_breakdown("binary-reverse-engineering-day-29-x/mastery")
check("16 timed_env stamps its phases (contract / pool / overlay / plan / hints) for a slow-t_env report",
      all(k in br for k in ("contract", "pool", "overlay", "plan", "hints")) and e.get("HCTF_EXPECT_BYTES") == "3000", (br, e))

# reply-size predictors: meta rows read once, same answers as the old scans
croot = TMP / "challenges"
for day, lane, base, sizes in ((26, "script-analysis", "script-analysis-day-26-a", {"single_solve": 900_000, "mastery": 9_000_000}),
                               (27, "script-analysis", "script-analysis-day-27-b", {"single_solve": 1_000_000, "mastery": 10_000_000}),
                               (27, "warmups", "warmups-day-27", {"single_solve": 3_000, "mastery": 60_000})):
    d = croot / f"day{day}" / f"{lane}-x"
    d.mkdir(parents=True)
    (d / "meta.json").write_text(json.dumps({"lane": lane, "base": base}))
    for mode, n in sizes.items():
        (d / mode).mkdir()
        (d / mode / "start.json").write_bytes(b"x" * n)
        os.utime(d / mode / "start.json", (1e9 + day, 1e9 + day))
from hctf import paths  # noqa: E402

answers = {}
for memo in (False, True):
    with patched({(paths, "CHALLENGES"): croot, (gmroute, "SIZE_MEMO"): memo, (gmroute, "_meta_memo"): {},
                  (gmroute, "_earlier_memo"): {}, (gmroute, "_reply"): {},
                  (remote, "ROOT"): TMP, (remote, "_BIG_START"): {}}):
        reads = []
        real_rt = Path.read_text

        def rt(self, *a, **k):
            if self.name == "meta.json":
                reads.append(str(self))
            return real_rt(self, *a, **k)
        with patched({(Path, "read_text"): rt}):
            if memo:
                gmroute.prewarm_sizes()
                reads.clear()
            answers[memo] = (gmroute._earlier_start_bytes("script-analysis-day-28-c/mastery"),
                             gmroute._earlier_start_bytes("warmups-day-28/mastery"),
                             gmroute._earlier_start_bytes("script-analysis-day-27-b/mastery"),  # its own base excluded
                             gmroute._earlier_start_bytes("mobile-android-day-28/mastery"),
                             remote._big_start("script-analysis-day-28-c"), remote._big_start("warmups-day-28"),
                             remote._big_start("script-analysis-day-26-a"))
            n_reads = len(reads)
check("16 size predictors: memoized answers == the old scans (newest earlier start, own base excluded, singles)",
      answers[True] == answers[False] == (10_000_000, 60_000, 9_000_000, 0, True, False, False), answers)
check("16 ... and after the pre-drop prewarm no meta.json is read at the drop", n_reads == 0, n_reads)

check("15 lag probe: off -> None", procgov.lag_stats() is None or procgov._lag["thread"] is not None)
procgov.start_lag_probe()
time.sleep(0.6)
st = procgov.lag_stats(5)
check("15 lag probe on: expected-vs-actual tick stats over a window, and a [res]-ready text",
      isinstance(st, dict) and st["n"] >= 1 and st["max_s"] >= 0 and procgov.lag_text(5).startswith(" lag max"), st)
check("15 ... start is idempotent (one thread)", procgov.start_lag_probe()
      and sum(1 for t in threading.enumerate() if t.name == "lag-probe") == 1)

# ---------------------------------------------------------------- 20. relay hygiene
class Chan:
    def __init__(self, behave, delay=0.0, k=0, misses=0):
        self.behave, self.delay, self.k, self.busy, self.calls, self.misses = behave, delay, k, 0, [], misses

    def alive(self):
        return True

    def call(self, op, timeout=60, **kw):
        self.calls.append((op, kw))
        time.sleep(self.delay)
        return self.behave(kw)


def ok_reply(kw, elapsed=0.05):
    return {"ok": True, "http": 200, "body": {"result": "ok", "op": kw["kind"]}, "elapsed": elapsed}


local_calls = []


def local_fn(env_=None, delay=0.0):
    def fn():
        local_calls.append(1)
        time.sleep(delay)
        return dict(env_ or {"http": 200, "body": {"result": "local"}, "transport": "inproc", "elapsed": 0.1})
    return fn


def reset():
    gmroute._avg.clear()
    gmroute._reply.clear()
    gmroute._demoted.clear()
    gmroute._state["decision"].clear()
    local_calls.clear()


logs = []
QUIET = {(gmroute, "_say"): logs.append}
ch = Chan(ok_reply)
reset()
with patched({**QUIET, (gmroute, "_chan"): lambda: ch, (gmroute, "_contract_bytes"): lambda cid: 3_650_000}):
    env1 = gmroute.call(["status", "binary-reverse-engineering-day-28-x/mastery"], 30, local_fn())
check("20 status with a 3.6 MB contract on disk: today's path alone, the relay never asked",
      env1["body"]["result"] == "local" and not ch.calls and len(local_calls) == 1, (env1, ch.calls))
reset()
with patched({**QUIET, (gmroute, "_chan"): lambda: ch, (gmroute, "_contract_bytes"): lambda cid: None,
              (gmroute, "_earlier_start_bytes"): lambda cid: 10_400_000}):
    gmroute.call(["status", "script-analysis-day-29-x/mastery"], 30, local_fn())
check("20 status before today's contract exists: the lane's earlier Mastery start (10 MB) predicts big -> no relay",
      not ch.calls and len(local_calls) == 1, ch.calls)
reset()
ch = Chan(ok_reply)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch, (gmroute, "_contract_bytes"): lambda cid: None}):
    env2 = gmroute.call(["status", "web-exploitation-day-29-x"], 30, local_fn(delay=0.3))
check("20 a Single's status before its start (a short 409): still hedged", ch.calls and env2["transport"] == "relay0",
      (ch.calls, env2))
reset()
ch = Chan(ok_reply)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch, (gmroute, "_contract_bytes"): lambda cid: 4_000_000}):
    gmroute._reply[("status", "binary-reverse-engineering-day-28-x/mastery")] = 900   # last reply was small (CORRECT)
    gmroute.call(["status", "binary-reverse-engineering-day-28-x/mastery"], 30, local_fn(delay=0.3))
check("20 a small LAST status reply never masks the multi-MB contract: local only (rehearsal D28 fair run: 4.7 MB binary "
      "Mastery statuses rode the relay ~11 s each)", len(ch.calls) == 0, ch.calls)
big_body = {"questions": [{"id": f"q{i}"} for i in range(2500)]}
reset()
with patched({**QUIET, (gmroute, "_chan"): lambda: Chan(ok_reply, delay=0.5), (gmroute, "_contract_bytes"): lambda cid: None}):
    gmroute.call(["status", "x-day-29"], 30, local_fn({"http": 409, "body": big_body, "elapsed": 0.2}))
check("20 a status reply's size is learnt (approx., no multi-MB re-serialization)",
      gmroute._reply.get(("status", "x-day-29"), 0) > gmroute.STATUS_HEDGE_MAX, gmroute._reply)
reset()
ch = Chan(ok_reply)
with patched({**QUIET, (gmroute, "_chan"): lambda: ch, (gmroute, "_contract_bytes"): lambda cid: 4_000_000,
              (gmroute, "STATUS_HEDGE_MAX"): 0}):
    gmroute.call(["status", "binary-reverse-engineering-day-28-x/mastery"], 30, local_fn(delay=0.3))
check("20 HCTF_GM_STATUS_HEDGE_MAX_KB=0: every status hedged (old)", len(ch.calls) == 1)


# demotion + channel choice
class FakeD:
    def alive(self):
        return True


c0, c1 = workers.RelayChan(FakeD(), 0), workers.RelayChan(FakeD(), 1)
reset()
with patched({**QUIET, (workers, "hb_relays"): lambda log=print, start=True, health=True: [c0, c1]}):
    c0.busy, c1.busy = 0, 1
    pick1 = gmroute._chan()
    gmroute.demote(c0, "test")
    pick2 = gmroute._chan()
    gmroute.demote(c1, "test")
    pick3 = gmroute._chan()
    gmroute._demoted.clear()
    c0.misses = 1
    pick4 = gmroute._chan()
    c0.misses = 0
    with patched({(gmroute, "DEMOTE_S"): 0}):
        gmroute.demote(c0, "off")
        pick5 = gmroute._chan()
check("20 _chan: least busy; a demoted channel is skipped; all demoted -> None (today's path)",
      pick1 is c0 and pick2 is c1 and pick3 is None, (pick1, pick2, pick3))
check("20 _chan: a channel that missed its last ping is avoided", pick4 is c1)
check("20 HCTF_GM_RELAY_DEMOTE_S=0: no demotion (old least-busy rule)", pick5 is c0 and not gmroute._demoted)

reset()
slow = Chan(lambda kw: {"ok": True, "http": 200, "body": {"r": 1}, "elapsed": 0.8}, delay=0.0, k=1)
with patched({**QUIET, (gmroute, "SLOW_S"): 0.05}):
    real_time = time.time
    base = [real_time()]

    def jumpy():   # the relay call "takes" 6.4 s on the client for a 0.8 s GM call
        base[0] += 3.2
        return base[0]
    with patched({(time, "time"): jumpy}):
        gmroute._relay_call(slow, ["status", "binary-x/mastery"], 30)
check("20 a slow relay call (client 6.4 s vs GM 0.8 s) demotes its channel", gmroute._demoted.get(1, 0) > real_time(),
      gmroute._demoted)
reset()
to = Chan(lambda kw: (_ for _ in ()).throw(workers.DaemonError("daemon gm timed out after 30s")), k=2)
try:
    gmroute._relay_call(to, ["start", "x-day-29"], 30)
except workers.DaemonError:
    pass
check("20 a relay timeout demotes its channel", 2 in gmroute._demoted)

# losing-leg slow note
logs.clear()
reset()
lose = Chan(lambda kw: {"ok": True, "http": 200, "body": {"r": "relay"}, "elapsed": 0.01}, delay=0.4, k=0)
with patched({**QUIET, (gmroute, "_chan"): lambda: lose, (gmroute, "_contract_bytes"): lambda cid: None,
              (gmroute, "SLOW_S"): 0.2}):
    envl = gmroute.call(["status", "x-day-29"], 30, local_fn(delay=0.05))
    time.sleep(0.6)
check("20 hedge: the losing relay leg's slow transport is tagged LOSING, no `!!!` alarm",
      envl["body"]["result"] == "local" and any("LOSING hedge leg" in m for m in logs)
      and not any(m.startswith("!!!") for m in logs), logs)
logs.clear()
reset()
win = Chan(lambda kw: {"ok": True, "http": 200, "body": {"r": "relay"}, "elapsed": 0.01}, delay=0.3, k=0)
with patched({**QUIET, (gmroute, "_chan"): lambda: win, (gmroute, "_contract_bytes"): lambda cid: None,
              (gmroute, "SLOW_S"): 0.2}):
    envw = gmroute.call(["status", "x-day-29"], 30, local_fn(delay=1.0))
    time.sleep(1.1)
check("20 hedge: a slow relay leg that WON (its reply was used) keeps the `!!!` alarm",
      envw["transport"] == "relay0" and any(m.startswith("!!! [gmroute] slow transport") for m in logs), logs)

# start timing marks (#16): the size check before the request, each hedge leg's send offset + duration
logs.clear()
reset()
with patched({**QUIET, (gmroute, "_chan"): lambda: Chan(ok_reply, delay=0.1), (gmroute, "START_SLOW_S"): 0.0,
              (gmroute, "START_MARK_S"): 0.0, (gmroute, "HEDGE_START_S"): 0.05,
              (gmroute, "_size_ok"): lambda a: (time.sleep(0.02), True)[1]}):
    gmroute.call(["start", "web-exploitation-day-29-x"], 30, local_fn(), public_fn=local_fn(delay=0.3))
check("16 start marks: the reply-size check time and the hedge legs (sent +s, took s, winner) are logged",
      any("reply-size check took" in m for m in logs)
      and any(m.startswith("[gmroute] slow start") and re.search(r"relay sent \+[\d.]+s took [\d.]+s", m) and "won by relay0" in m for m in logs),
      logs)

# busy channel survives missed pings
cb = workers.RelayChan(FakeD(), 3)
cb.misses = workers.RELAY_MISSES
idle_dead = not cb.alive()
cb.busy = 1
busy_alive = cb.alive()
cb.misses = workers.RELAY_BUSY_MISSES
busy_dead = not cb.alive()
check(f"20 relay keeper: idle channel down at {workers.RELAY_MISSES} missed pings, a busy one (carrying a big reply) "
      f"only at {workers.RELAY_BUSY_MISSES}", idle_dead and busy_alive and busy_dead)
with patched({(workers, "hb_relays"): lambda log=print, start=True, health=True: [workers.RelayChan(FakeD(), 0),
                                                                                  workers.RelayChan(FakeD(), 1)]}):
    cs = workers.hb_relays()
    cs[0].misses = 1
    with patched({(workers, "hb_relays"): lambda log=print, start=True, health=True: cs}):
        rc = workers.hb_race_chan()
check("3 hb_race_chan: channel 0 skipped while it misses pings when another is healthy", rc is cs[1])

# ---------------------------------------------------------------- 18. hctf-vpn unit + route script
unit = (ROOT / "setup" / "hctf-vpn.service").read_text()
exec_start = next(ln for ln in unit.splitlines() if ln.startswith("ExecStart="))
check("18 ExecStart: --script-security 2 --route-up runs setup/hctf-vpn-route.sh (quoted: one openvpn argument)",
      "--script-security 2" in exec_start
      and '--route-up "/bin/sh /home/testpwn/huntress-2026/setup/hctf-vpn-route.sh"' in exec_start, exec_start)
posts = [ln for ln in unit.splitlines() if ln.startswith("ExecStartPost=")]
check("18 ExecStartPost backup pins the /32 on tun0 and can never fail the unit ('-' prefix); MTU clamp kept",
      any(ln.startswith("ExecStartPost=-") and "hctf-vpn-route.sh tun0" in ln for ln in posts)
      and any("mtu 1200" in ln for ln in posts), posts)
script = ROOT / "setup" / "hctf-vpn-route.sh"
check("18 route script: present, executable, sh -n clean",
      script.exists() and os.access(script, os.X_OK)
      and subprocess.run(["sh", "-n", str(script)], capture_output=True).returncode == 0)
stub = TMP / "ipstub"
rec = TMP / "ip.calls"
stub.write_text(f"#!/bin/sh\necho \"$@\" >> {rec}\n"
                "case \"$*\" in *'addr show'*) echo '    inet 10.200.103.67/16 scope global tun0';; esac\nexit 0\n")
stub.chmod(0o755)
r = subprocess.run(["sh", str(script)], capture_output=True, text=True, timeout=10,
                   env={**os.environ, "HCTF_IP_BIN": str(stub), "dev": "tun7"})
check("18 route-up (OpenVPN's $dev): `ip route replace 10.1.50.243/32 dev <dev>`, exit 0",
      r.returncode == 0 and "route replace 10.1.50.243/32 dev tun7" in rec.read_text(), (r, rec.read_text()))
rec.unlink()
r = subprocess.run(["sh", str(script), "tun0"], capture_output=True, text=True, timeout=10,
                   env={**{k: v for k, v in os.environ.items() if k != "dev"}, "HCTF_IP_BIN": str(stub)})
check("18 ExecStartPost form (dev as $1)", "route replace 10.1.50.243/32 dev tun0" in rec.read_text())
if shutil.which("systemd-analyze"):
    v = subprocess.run(["systemd-analyze", "verify", str(ROOT / "setup" / "hctf-vpn.service")],
                       capture_output=True, text=True, timeout=60)
    check("18 systemd-analyze verify setup/hctf-vpn.service: clean", v.returncode == 0 and not v.stderr.strip(),
          (v.returncode, v.stderr[-400:]))
else:
    print("ok  18 systemd-analyze not installed: verify skipped")
pf = (ROOT / "bin" / "preflight.sh").read_text()
check("18 preflight names the tun1-shadowing cause and --fix pins the /32 with non-interactive sudo",
      "shadows the pushed 10.1.0.0/16" in pf and 'sudo -n ip route replace "$HB_HOST/32" dev "$VPN_DEV"' in pf)
check("18/21 bin/preflight.sh: bash -n clean",
      subprocess.run(["bash", "-n", str(ROOT / "bin" / "preflight.sh")], capture_output=True).returncode == 0)

# ---------------------------------------------------------------- 21. fault-replay skip message
check("21 preflight's fault-replay skip says to run the warm-up >= 15 min before the drop",
      re.search(r"fault-replay suite skipped: .*>= 15 min before the drop", pf) is not None)

# ---------------------------------------------------------------- 19. rehearsal sync: no hardlinks for challenges/
for name in ("sync_alt_main.sh", "sync_alt_d25.sh", "sync_alt_d26.sh"):
    p = ROOT / ".run" / name
    if not p.exists():
        print(f"ok  19 {name} absent: skipped")
        continue
    lines = [ln for ln in p.read_text().splitlines() if ln.strip().startswith("rsync")]
    linked = [ln for ln in lines if "--link-dest" in ln]
    chal = [ln for ln in lines if "ignored-fixtures-alt-challenges" in ln]
    check(f"19 {name}: challenges/ fixtures copied (no --link-dest); --link-dest only on the tests/lib list",
          chal and not any("--link-dest" in ln for ln in chal)
          and all("ignored-fixtures-alt-other" in ln for ln in linked)
          and subprocess.run(["bash", "-n", str(p)], capture_output=True).returncode == 0, (chal, linked))

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{len(failures)} failure(s)" + (": " + ", ".join(failures) if failures else ""))
sys.exit(1 if failures else 0)
