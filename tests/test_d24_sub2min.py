"""D24 sub-2-min fixes (plan: whole-board sub-2-min, D24 fixes), offline: fakes only, no network, no workers.
Track A (timed runner):
- A1 instrumentation: Chain._mark + one "handoff timing" line per mode, runner spawn / pool / pre-start fields, the
     `timed:` line's new keys, t_env + t_hb_ready from the local route
- A2 linear question pairing (exact-id index + boundary-suffix lookup + positional fallback) == the old scan
- A3 faster runner start: non-blocking Homebase readiness, adaptive GM pool size, lazy pool (2 sockets up -> go)
- A4 Mastery pre-start fired at the Time Trial's CORRECT, before the TT's bookkeeping

Run:  source bin/env.sh && python3 tests/test_d24_sub2min.py      (exit 0 = all pass)
"""
import contextlib
import json
import os
import random
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import hb_timed, orchestrate, solvers, timed, workers  # noqa: E402

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


@contextlib.contextmanager
def envset(**kv):
    """Set (or with None: unset) environment variables, restore afterwards."""
    saved = {k: os.environ.get(k) for k in kv}
    try:
        for k, v in kv.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


TMP_A = Path(tempfile.mkdtemp(prefix="d24A-", dir=str(ROOT / ".run")))


def bare_chain_a(**kw):
    """A Chain without __init__ side effects."""
    c = object.__new__(orchestrate.Chain)
    c.base, c.pools, c.gov, c.only_modes = "d24a-base", None, None, None
    c.lane, c.name = "warmups", "test"
    c.entries = {"single_solve": {"id": "d24a"}, "time_trial": {"id": "d24a/time_trial"},
                 "mastery": {"id": "d24a/mastery"}}
    c.__dict__.update(kw)
    return c


# ================================================================ Track A
# ---------------------------------------------------------------- A1 instrumentation
said = []
with patched({(orchestrate, "say"): said.append, (workers, "TIMING_MARKS"): True}):
    ch = bare_chain_a(_chain_t0=time.time() - 30)
    for m in ("correct", "ready", "after_worker", "time_trial:stage"):
        ch._mark(m)
    ch._mark("time_trial:run", "d24a/time_trial")
    ch._mark("time_trial:run", "d24a/time_trial")          # a retry: no second line
    ch._mark("time_trial:correct")
    ch._mark("mastery:stage")
    ch._mark("mastery:run", "d24a/mastery")
lines = [s for s in said if "handoff timing" in s]
check("A1 one handoff timing line per mode (a retry adds none)", len(lines) == 2, said)
check("A1 the TT line lays out single CORRECT -> ready -> worker ended -> stage -> run, with the chain offset",
      lines and all(k in lines[0] for k in ("correct +0.0s", "ready +", "after_worker +", "time_trial:stage +",
                                            "time_trial:run +", "(chain +3")), lines[:1])
check("A1 the Mastery line starts at the TT's CORRECT",
      len(lines) > 1 and "(mastery): time_trial:correct +0.0s > mastery:stage +" in lines[1], lines[1:])
check("A1 marks keep the FIRST time", ch._marks["time_trial:run"] <= ch._marks["time_trial:correct"])
said.clear()
with patched({(orchestrate, "say"): said.append, (workers, "TIMING_MARKS"): False}):
    ch2 = bare_chain_a()
    ch2._mark("time_trial:stage")
    ch2._mark("time_trial:run", "d24a/time_trial")
check("A1 HCTF_TIMING_MARKS=0: no marks, no line", not said and not getattr(ch2, "_marks", None))

# hb_timed: spawn {main, lock, pool} and why a pre-start was not used
seen = {}


def fake_attempt(a):
    seen["spawn"] = dict(hb_timed._CTX.spawn or {})
    return {"result": "correct"}


with patched({(hb_timed, "_attempt"): fake_attempt}), envset(HCTF_T_SPAWN=f"{time.time() - 0.4:.3f}"):
    hb_timed.run_attempt("d24a-spawn/time_trial", "challenges/x/solver")
check("A1 hb_timed reports spawn.main (interpreter start, from HCTF_T_SPAWN) and spawn.lock",
      0.3 <= seen.get("spawn", {}).get("main", -1) < 5 and "lock" in seen.get("spawn", {}), seen)
check("A1 hb_timed clears the per-attempt spawn state", hb_timed._CTX.spawn is None)
with patched({(hb_timed, "_attempt"): fake_attempt}), envset(HCTF_T_SPAWN=f"{time.time() - 999:.3f}"):
    hb_timed.run_attempt("d24a-spawn/time_trial", "challenges/x/solver")
check("A1 a stale/foreign HCTF_T_SPAWN is ignored", "main" not in seen.get("spawn", {}), seen)

_pcid = "d24a-prestart/mastery"
_padir = hb_timed.HW / ".run" / "tmp-timed" / "d24a_prestart_mastery"
_padir.mkdir(parents=True, exist_ok=True)
(_padir / "contract.json").write_text(json.dumps({"attempt_id": "att1", "answer_ids": ["a"]}))
(_padir / "f.bin").write_bytes(b"x")
(_padir / ".prefetch.json").write_text(json.dumps({"attempt_id": "att1", "files": ["f.bin"], "t": time.time() - 9999}))
why = []
check("A1 a stale pre-start is not reused and says why", hb_timed._prestarted_body(_pcid, why) is None and why == ["stale"],
      why)
(_padir / ".prefetch.json").write_text(json.dumps({"attempt_id": "other", "files": ["f.bin"], "t": time.time()}))
why = []
check("A1 a pre-start of another attempt says mismatch", hb_timed._prestarted_body(_pcid, why) is None
      and why == ["mismatch"], why)
(_padir / ".prefetch.json").write_text(json.dumps({"attempt_id": "att1", "files": ["f.bin"], "t": time.time()}))
why = []
check("A1 a fresh pre-start is reused (no reason recorded)", hb_timed._prestarted_body(_pcid, why) is not None and not why)
shutil.rmtree(_padir, ignore_errors=True)

check("A1 the `timed:` line carries the runner's pre-clock timings",
      all(k in timed._TIMED_KEYS for k in ("spawn", "pool_warm", "prestart_reused", "prestart_miss", "t_env",
                                           "t_hb_ready")) and timed._TIMED_KEYS[0] == "result")


# run_timed_auto: the Homebase readiness seconds land on the result
def fake_route(*a, **k):
    workers._homebase_ready(lambda *x: None)
    return {"result": "correct"}


def slow_probe():
    time.sleep(0.05)
    return False


with patched({(workers, "_run_timed_auto"): fake_route, (workers, "start_homebase_health"): lambda log=None: None,
              (workers.remote, "probe"): slow_probe, (workers, "TIMING_MARKS"): True}):
    _saved_hb = dict(workers._hb)
    workers._hb.update(checked=0.0, ok=False)
    try:
        r = workers.run_timed_auto(Path("/x"), "d24a/time_trial")
    finally:
        workers._hb.clear()
        workers._hb.update(_saved_hb)
check("A1 run_timed_auto reports the seconds its Homebase readiness check cost",
      r.get("t_hb_ready", 0) >= 0.04, r)

# ---------------------------------------------------------------- A2 linear question pairing
_TOK = ["a", "b", "marker", "field", "x.y", "q-1", "set1", "a+b", "x$", "(", "", "sec_2", "b.c_d", "1", "ß"]


def _rid(rng):
    parts = [rng.choice(_TOK) for _ in range(rng.randint(1, 3))]
    out = parts[0]
    for p in parts[1:]:
        out += rng.choice("._-/ x") + p
    return out


def _rcase(rng):
    qs = []
    for k in range(rng.randint(0, 10)):
        r = rng.random()
        if r < 0.05:
            qs.append({})
        elif r < 0.12:
            qs.append({"question": f"q{k}"})                       # no id
        elif r < 0.15:
            qs.append({"id": None, "question": f"q{k}"})
        else:
            qs.append({"id": _rid(rng), "question": f"q{k}"})
    ids = []
    for _ in range(rng.randint(0, 12)):
        r = rng.random()
        qids = [q.get("id") for q in qs if isinstance(q.get("id"), str)]
        if r < 0.3 and qids:
            ids.append(rng.choice(qids))                           # exact
        elif r < 0.6 and qids:
            ids.append(_rid(rng) + rng.choice("._-x") + rng.choice(qids))   # boundary (or not) suffix
        elif r < 0.65 and ids:
            ids.append(rng.choice(ids))                            # duplicate answer id
        else:
            ids.append(_rid(rng))
    if qs and rng.random() < 0.08:
        qs[rng.randrange(len(qs))]["id"] = qs[0].get("id")        # duplicate question ids
    r = rng.random()
    if r < 0.03 and qs:
        qs.insert(rng.randrange(len(qs) + 1), "junk")              # non-dict question (scan path)
    elif r < 0.06 and qs:
        qs[rng.randrange(len(qs))]["id"] = rng.randint(0, 3)       # int question id (scan path; may raise)
    elif r < 0.09 and qs and isinstance(qs[-1].get("id"), str):
        ids.append("slot0_" + qs[-1]["id"] + "\n")                 # `$` before a trailing newline (scan path)
    elif r < 0.11 and qs:
        qs[rng.randrange(len(qs))]["id"] = "mark\ner"              # newline inside a question id (scan path)
    return ids, qs


def _shape(res, qs):
    pairs = res.items() if isinstance(res, dict) else res
    out = []
    for aid, q in pairs:
        k = next((i for i, x in enumerate(qs) if x is q), None)
        out.append((aid, ("idx", k) if k is not None else ("val", repr(q))))
    return out


def _both(fn, ids, qs):
    got = {}
    for flag in ("0", "1"):
        with envset(HCTF_PAIR_INDEX=flag):
            try:
                got[flag] = ("ok", _shape(fn(ids, qs), qs))
            except Exception as e:  # noqa: BLE001 - the scan's own exceptions must be kept
                got[flag] = ("raise", type(e).__name__)
    return got["0"], got["1"]


_sv = lambda ids, qs: solvers.paired_questions({"answer_ids": ids, "questions": qs})   # noqa: E731
_rng = random.Random(2024)
_bad = []
for _n in range(4000):
    _ids, _qs = _rcase(_rng)
    for _name, _fn in (("solvers", _sv), ("hb_timed", hb_timed._paired)):
        _old, _new = _both(_fn, _ids, _qs)
        if _old != _new:
            _bad.append((_name, _ids, _qs, _old, _new))
check("A2 randomized: indexed pairing == the old scan (4000 cases x solvers + hb_timed)", not _bad, _bad[:2])

_edge = [
    (["slot0_a.marker"], [{"id": "marker"}, {"id": "a.marker"}]),           # longest boundary suffix wins
    (["xmarker"], [{"id": "q0"}, {"id": "marker"}]),                       # no boundary -> position
    (["m", "slot1-m"], [{"id": "m", "n": 1}, {"id": "m", "n": 2}]),         # duplicate question ids -> the first
    (["slot_marker\n"], [{"id": "z"}, {"id": "marker"}]),                  # trailing newline: `$` still matches
    ([""], [{"id": "x"}, {"id": ""}]),                                     # empty id: exact only
    (["a_", "b-"], [{"id": ""}, {}]),                                      # empty suffix never matches; {} -> {}
    (["a.b.c"], [{"id": "c"}, {"id": "b.c"}, {"id": "a.b.c.d"}]),
    (["s1.k", "s2.k", "s3.zz"], [{"id": "k"}]),                            # shared question; past the end -> {}
    (["5"], [{"id": 5}]),                                                  # int question id: the scan's TypeError
    (["a"], ["junk", {"id": "a"}]),
]
_eb = [(i, q, *_both(f, i, q)) for i, q in _edge for f in (_sv, hb_timed._paired) if len(set(map(str, _both(f, i, q)))) > 1]
check("A2 edge cases (longest suffix, boundary, duplicates, newline, empty ids, int ids, non-dict) == the scan", not _eb,
      _eb[:2])
with envset(HCTF_PAIR_INDEX="1"):
    _r = dict(_sv(["slot0_a.marker", "xmarker"], [{"id": "marker"}, {"id": "a.marker"}]))
check("A2 longest boundary suffix + positional fallback",
      _r["slot0_a.marker"]["id"] == "a.marker" and _r["xmarker"]["id"] == "a.marker", _r)

# 12,480 ids (D16/D24 script Mastery scale): 1:1 ids, shared-question bundles, and no id match at all (positional)
_N = 12480
_ids = [f"set-{k // 2496 + 1}.field_{k % 2496:04d}" for k in range(_N)]
_cases = {"1:1": (_ids, [{"id": a, "question": "q"} for a in _ids]),
          "bundle": ([f"set-{k // 2496 + 1}.slot{k}_marker{k % 40}" for k in range(_N)],
                     [{"id": f"marker{n}", "question": "q"} for n in range(40)]),
          "positional": (_ids, [{"id": f"other-{k}", "question": "q"} for k in range(_N)])}
_times = {}
with envset(HCTF_PAIR_INDEX="1"):
    for _name, (_i, _q) in _cases.items():
        t = time.perf_counter()
        _a = solvers.paired_questions({"answer_ids": _i, "questions": _q})
        _b = hb_timed._paired(_i, _q)
        _times[_name] = round(time.perf_counter() - t, 3)
        if _name == "1:1":
            _ok11 = all(q is _q[k] for k, (_x, q) in enumerate(_a)) and all(_b[a] is _q[k] for k, a in enumerate(_i))
print(f"   (A2 12,480-id pairing, solvers + hb_timed together: {_times})")
check("A2 12,480 ids pair in < 0.5 s (each shape, both implementations)", max(_times.values()) < 0.5, _times)
check("A2 12,480 1:1 ids pair to their own questions", _ok11)

# ================================================================ end of Track A
shutil.rmtree(TMP_A, ignore_errors=True)
if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall D24 sub-2-min checks passed")
