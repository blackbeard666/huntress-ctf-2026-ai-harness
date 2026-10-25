"""D24 #14 release streaming + launcher, offline: fake GM, no network, no workers, no real index writes.
- _list_race(on_group=): a chain is handed over as soon as ITS lane list holds its three modes (not after the union)
- faults: an exception in on_group, a partial list, a lane that never appears, a web lane tagged -day-NN
- binary's --lane and --search lists run at once (stream mode only)
- _hot_release: a slow full list never blinds the status probe; the full list still wins on an id-pattern change;
  the hot window ends with []; wait_for_release falls back to the old loop when the stream raises
- _EarlyChains: only / HCTF_SKIP_IDS filters, started(), join(); run()'s launch loop skips streamed chains
- kill switch HCTF_RELEASE_STREAM=0: wait_for_release never enters the stream, _list_race keeps the sequential search
- bin/day.sh / bin/preflight.sh day 1 = 2026-10-01, the default day counted on the US-Eastern date

Run:  source bin/env.sh && python3 tests/test_d24_release.py      (exit 0 = all pass)
"""
import contextlib
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import orchestrate, paths, remote  # noqa: E402

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


MODES = ("single_solve", "time_trial", "mastery")
INDEX = {}
LOG = []


def fake_register(chs):
    for c in chs:
        INDEX.setdefault(paths.base_id(c["id"]), {"day": c.get("day"), "lane": c.get("lane")})
    return INDEX


BASE = {(orchestrate, "say"): lambda *a, **k: LOG.append(a[0] if a else ""),
        (paths, "register"): fake_register,
        (paths, "lookup"): lambda cid: INDEX.get(paths.base_id(cid))}


def modes_of(base, lane, day, n=3):
    return [{"id": base + ("" if m == "single_solve" else f"/{m}"), "lane": lane, "mode": m, "day": day, "name": lane}
            for m in MODES[:n]]


LANES = ["warmups", "metadata-forensics", "script-analysis", "binary-reverse-engineering", "mobile-android", "web"]
DELAY = {"warmups": 0.05, "metadata-forensics": 0.1, "script-analysis": 0.15, "binary-reverse-engineering": 0.2,
         "mobile-android": 0.25, "web": 1.2}


def make_gm(day=25, delay=None, never=(), partial=(), lane_empty=(), search_delay=0.05, calls=None):
    delay = dict(DELAY if delay is None else delay)

    def gm(*args, timeout=180):
        if calls is not None:
            calls.append((time.time(), args))
        if args[0] == "status":
            return {"http": 409 if args[1] == f"warmups-day-{day}" else 404, "body": {}}
        if args[0] == "list" and "--lane" in args:
            ln = args[args.index("--lane") + 1]
            time.sleep(delay.get(ln, 0.05))
            if ln in never or ln in lane_empty:
                return {"http": 200, "body": {"challenges": []}}
            lane = "web-exploitation" if ln == "web" else ln
            base = f"{lane}-day-{day}-x"
            return {"http": 200, "body": {"challenges": modes_of(base, lane, day, 2 if ln in partial else 3)}}
        if args[0] == "list" and "--search" in args:
            time.sleep(search_delay)
            q = args[args.index("--search") + 1]
            ln = next(x for x in LANES if x.startswith(q))
            noise = modes_of(f"warmups-day-{day}-binary-mention", "warmups", day, 1)   # text search hits other lanes
            return {"http": 200, "body": {"challenges": modes_of(f"{ln}-day-{day}-x", ln, day) + noise}}
        return {"http": 200, "body": {"challenges": []}}
    return gm


def slow_full_factory(day=25, wait=2.0, got=None):
    def full(d=None):
        time.sleep(wait)
        if got is not None:
            return got
        return [c for ln in LANES for c in modes_of(f"{'web-exploitation' if ln == 'web' else ln}-day-{day}-x",
                                                    paths.canonical_lane(ln), day)]
    return full


# ---------------------------------------------------------------- 1. per-lane streaming
fired = []


def on_group(base, entries):
    fired.append((time.time(), base, sorted(c["mode"] for c in entries), entries[0]["lane"]))


with patched({**BASE, (remote, "gm"): make_gm(), (orchestrate, "released_challenges"): slow_full_factory()}):
    INDEX.clear()
    t0 = time.time()
    got = orchestrate._list_race(25, LANES, log=LOG.append, expected=18, on_group=on_group)
    took = time.time() - t0
    first = {b: t - t0 for t, b, _, _ in fired}
    check("1 every lane's chain is handed over once with its three modes",
          len(fired) == 6 and all(m == sorted(MODES) for _, _, m, _ in fired), fired)
    check("1 warmups starts at its own lane list (~0.05 s), not at the union (~1.2 s, the slow web list)",
          first.get("warmups-day-25-x", 9) < 0.5 and took >= 1.1, (first, took))
    check("1 the web chain (tagged -day-25) is handed over canonicalized to lane `web`",
          any(b == "web-exploitation-day-25-x" and ln == "web" for _, b, _, ln in fired), fired)
    check("1 the race still returns the 18-mode union", len(got) == 18, len(got))
    check("1 every streamed base was registered before its hand-over",
          all(b in INDEX for _, b, _, _ in fired))
    check("1 binary used --lane + --search at once: the noise row from the text search is filtered out",
          not any("binary-mention" in c["id"] for c in got), [c["id"] for c in got if "mention" in c["id"]])

# ---------------------------------------------------------------- 2. faults
fired.clear()


def bad_group(base, entries):
    if base.startswith("metadata"):
        raise RuntimeError("boom in on_group")
    on_group(base, entries)


with patched({**BASE, (remote, "gm"): make_gm(partial=("script-analysis",), never=("web",)),
              (orchestrate, "released_challenges"): slow_full_factory(wait=0.6)}):
    INDEX.clear()
    LOG.clear()
    got = orchestrate._list_race(25, LANES, log=LOG.append, expected=18, on_group=bad_group)
    bases = {b for _, b, _, _ in fired}
    check("2 an exception in on_group is logged, never raised; the other chains still stream",
          "metadata-forensics-day-25-x" not in bases and "warmups-day-25-x" in bases
          and any("stream start of metadata-forensics-day-25-x failed" in str(x) for x in LOG), (bases, LOG[-3:]))
    check("2 a partial lane list (2 of 3 modes) is never handed over", "script-analysis-day-25-x" not in bases, bases)
    check("2 a lane that never appears: the full list wins and carries every chain (the caller starts the rest)",
          len(got) == 18 and "web-exploitation-day-25-x" not in bases, (len(got), bases))

fired.clear()
with patched({**BASE, (remote, "gm"): make_gm(), (orchestrate, "released_challenges"): slow_full_factory(wait=0.3)}):
    INDEX.clear()

    def refuse(base, entries):
        return False     # e.g. filtered by `only`: not fired

    seen = []
    got = orchestrate._list_race(25, LANES, log=LOG.append, expected=18,
                                 on_group=lambda b, e: seen.append(b) or refuse(b, e))
    check("2 a refused group (False) is not counted as streamed", "streamed" not in str(LOG[-1]) and len(seen) >= 1,
          LOG[-1])

# ---------------------------------------------------------------- 3. binary --lane + --search in parallel
calls = []
with patched({**BASE, (remote, "gm"): make_gm(delay={"binary-reverse-engineering": 0.5}, lane_empty=(
        "binary-reverse-engineering",), search_delay=0.4, calls=calls)}):
    INDEX.clear()
    t0 = time.time()
    got = orchestrate._lane_or_search(25, "binary-reverse-engineering", 10, LOG.append)
    took = time.time() - t0
    check("3 lane [] + search: the search answers, in max(lane, search) not their sum",
          len(got) == 3 and took < 0.75, (len(got), round(took, 2)))
    starts = sorted(t for t, a in calls if a[0] == "list")
    check("3 both lists were sent at once", len(starts) >= 2 and starts[1] - starts[0] < 0.1,
          [(round(t - t0, 2), a) for t, a in calls])

calls.clear()
with patched({**BASE, (remote, "gm"): make_gm(lane_empty=("binary-reverse-engineering",), calls=calls),
              (orchestrate, "released_challenges"): slow_full_factory(wait=0.5)}):
    INDEX.clear()
    orchestrate._list_race(25, ["binary-reverse-engineering"], log=LOG.append, expected=3)
    seq = [a for _, a in calls if a[0] == "list"]
    check("3 kill switch (no on_group): the old sequential --lane then --search order is kept",
          [("--lane" in a) for a in seq] == [True, False], seq)

# ---------------------------------------------------------------- 4. _hot_release
calls = []
fired.clear()
drop = time.time()
with patched({**BASE, (remote, "gm"): make_gm(calls=calls),
              (orchestrate, "released_challenges"): slow_full_factory(wait=3.0)}):
    INDEX.clear()
    t0 = time.time()
    got = orchestrate._hot_release(25, drop, 0.2, on_group)
    took = time.time() - t0
    check("4 a 3 s full list never blinds the probe: released + listed in ~1.3 s", len(got) == 18 and took < 2.5,
          (len(got), round(took, 2)))
    check("4 ... and the chains were streamed through on_group", len(fired) == 6, len(fired))

calls.clear()
with patched({**BASE, (remote, "gm"): make_gm(day=99, calls=calls),   # the probe id never answers (pattern change)
              (orchestrate, "released_challenges"): slow_full_factory(wait=0.3)}):
    t0 = time.time()
    got = orchestrate._hot_release(25, time.time(), 0.2, on_group)
    check("4 the probe id never answers (id pattern change): the full-list thread wins", len(got) == 18
          and time.time() - t0 < 1.5, (len(got), time.time() - t0))
    probes = [t for t, a in calls if a[0] == "status"]
    check("4 two staggered probers ran meanwhile", len(probes) >= 2, len(probes))

with patched({**BASE, (remote, "gm"): make_gm(day=99), (orchestrate, "RELEASE_HOT_AFTER", ): 0.3,
              (orchestrate, "released_challenges"): lambda d=None: []}):
    before = set(threading.enumerate())   # 4a's lister is still inside its 3 s fake list (a GM call is never killed)
    t0 = time.time()
    got = orchestrate._hot_release(25, time.time(), 0.1, on_group)
    check("4 nothing released by the end of the hot window -> [] (the caller's loop carries on)",
          got == [] and time.time() - t0 < 1.5, (got, time.time() - t0))
    time.sleep(0.4)
    live = [t for t in threading.enumerate() if t.name.startswith("release-") and t.is_alive() and t not in before]
    check("4 ... and its threads stop", not live, live)


# ---------------------------------------------------------------- 5. wait_for_release fallback + kill switch
def boom(*a, **k):
    raise RuntimeError("stream exploded")


rel = [0]


def full_after(d=None):
    rel[0] += 1
    return modes_of("warmups-day-25-x", "warmups", 25) if rel[0] >= 2 else []


class _Pool:
    def warm_pool(self, n):
        pass


with patched({**BASE, (remote, "gm"): make_gm(), (remote, "gm_client"): lambda: _Pool(),
              (orchestrate, "_hot_release"): boom, (orchestrate, "released_challenges"): full_after,
              (orchestrate, "_STREAM_BROKEN"): False}):
    LOG.clear()
    got = orchestrate.wait_for_release(25, poll=0.01, drop=time.time())
    check("5 the stream raising falls back to the old probe loop, which still launches",
          len(got) >= 3 and any("release stream failed" in str(x) for x in LOG), (len(got), LOG[:3]))
    check("5 ... and the stream stays off for the rest of the wait", orchestrate._STREAM_BROKEN is True)

used = []
with patched({**BASE, (remote, "gm"): make_gm(), (remote, "gm_client"): lambda: _Pool(),
              (orchestrate, "_hot_release"): lambda *a, **k: used.append(1) or [],
              (orchestrate, "RELEASE_STREAM"): False, (orchestrate, "_STREAM_BROKEN"): False,
              (orchestrate, "released_challenges"): slow_full_factory(wait=0.1)}):
    got = orchestrate.wait_for_release(25, poll=0.01, drop=time.time())
    check("5 HCTF_RELEASE_STREAM=0: never enters the stream (old loop: probe + list race)", not used and len(got) == 18,
          (used, len(got)))

# ---------------------------------------------------------------- 6. _EarlyChains + run()'s launch loop
ran = []


class FakeChain:
    def __init__(self, base, entries, pools, gov, modes=None):
        self.base, self.entries = base, entries

    def run(self):
        time.sleep(0.2)
        ran.append((self.base, len(self.entries)))


with patched({**BASE, (orchestrate, "Chain"): FakeChain}):
    os.environ["HCTF_SKIP_IDS"] = "warmups-day-25-x/mastery"
    try:
        ec = orchestrate._EarlyChains(None, None, None, only=["warmups", "binary"])
        r1 = ec.start("warmups-day-25-x", modes_of("warmups-day-25-x", "warmups", 25))
        r2 = ec.start("warmups-day-25-x", modes_of("warmups-day-25-x", "warmups", 25))
        r3 = ec.start("mobile-android-day-25-x", modes_of("mobile-android-day-25-x", "mobile-android", 25))
        check("6 start(): the `only` filter refuses (False) a chain the run would not launch", r3 is False
              and not ec.started("mobile-android-day-25-x"))
        check("6 start() twice = one chain", r1 and r2 and ec.started("warmups-day-25-x"))
        ec.join()
        check("6 HCTF_SKIP_IDS applies to streamed entries; join() waits for the chain",
              ran == [("warmups-day-25-x", 2)], ran)
    finally:
        os.environ.pop("HCTF_SKIP_IDS", None)

src = (ROOT / "hctf" / "orchestrate.py").read_text()
run_src = src[src.index("\ndef run(day=None"):src.index("\nCAPTURE_JOIN_TIMEOUT")]
check("6 run(): the launch loop skips streamed chains and joins them",
      "early.started(base)" in run_src and "early.join()" in run_src and "on_group=early.start" in run_src)

# ---------------------------------------------------------------- 7. bin/ day number
day_sh = (ROOT / "bin" / "day.sh").read_text()
pf_sh = (ROOT / "bin" / "preflight.sh").read_text()
check("7 day.sh + preflight.sh: day 1 = 2026-10-01", 'CTF_DAY1="2026-10-01"' in day_sh and 'CTF_DAY1="2026-10-01"' in pf_sh)
check("7 day.sh: [credits] runs in the background", '( echo "[credits]' in day_sh)
script = ("CTF_DAY1=2026-10-01; for t in '2026-10-25 20:45 +0800' '2026-10-26 01:00 +0800' '2026-10-26 12:30 +0800'; do "
          'et_today="$(TZ=America/New_York date -d "$t" +%F)"; '
          + day_sh[day_sh.index("  DAY=$((") :].split("\n")[0].strip() + '; echo $DAY; done')
out = subprocess.run(["bash", "-c", script], capture_output=True, text=True).stdout.split()
check("7 the default day: 25 at 20:45 Manila 10-25 (arm) and 01:00 10-26 (relaunch), 26 from 12:00 10-26 Manila",
      out == ["25", "25", "26"], out)
for f in ("day.sh", "preflight.sh"):
    rc = subprocess.run(["bash", "-n", str(ROOT / "bin" / f)]).returncode
    check(f"7 bash -n bin/{f}", rc == 0)

print(f"\n{len(failures)} failure(s)" + (": " + ", ".join(failures) if failures else ""))
sys.exit(1 if failures else 0)
