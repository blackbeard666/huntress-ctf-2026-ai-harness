"""Day 16 prep (D15 review + "train on previous days"). Offline: no GM / Homebase / workers.
Part A (D15 run fixes):
- mastery_delta lists ids NEW to the lane first, all of them (D15 metadata: the synthesis id was cut at 12).
- A Single whose lane's previous start reply was large starts on the public GM (daemon channel head-of-line block).
- A failed live untimed attempt is re-fetched from the public GM (not over the VPN); a different attempt -> fallback.
- Binary duel only with HCTF_DUEL_BINARY_MIN_AVAIL_GB set and that much memory free.

Run:  source bin/env.sh && python3 tests/test_day16_prep.py      (exit 0 = all pass)
"""
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import duel, orchestrate, remote, workers  # noqa: E402
from hctf import hb_timed as ht  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="hctf-d16p-"))

# A1) mastery_delta: new-to-lane ids first and complete; carried-over ones sampled after
single = {"answer_ids": ["d16-x-001-x-new-field"], "questions": [{"id": "d16-x-001-x-new-field"}]}
timed_c = {"answer_ids": [f"set1.d0{i}-f-001-f-old-{i}" for i in range(1, 10)] + ["set1.day-16-synthesis-zzz-order",
                                                                                     "set1.d16-x-001-x-new-field"]}
known = {orchestrate.field_shape(f"d0{i}-f-001-f-old-{i}") for i in range(1, 10)}
txt = orchestrate.mastery_delta(single, [timed_c], known=lambda: known)
assert "1 question id(s) NEW to this lane" in txt and "`day-16-synthesis-zzz-order`" in txt, txt
assert txt.index("synthesis") < txt.index("carried over"), txt
assert "9 id(s) carried over" in txt, txt
txt0 = orchestrate.mastery_delta(single, [timed_c], known=lambda: (_ for _ in ()).throw(OSError("boom")))
assert "MASTERY COMPOUNDS" in txt0 and "NEW to this lane" not in txt0   # a failing lookup never costs the single
d15 = ROOT / "challenges/day15/metadata-a-word-to-the-wise"
if (d15 / "single_solve/start.json").exists() and (d15 / "time_trial/contract.json").exists():
    txt = orchestrate.mastery_delta(json.loads((d15 / "single_solve/start.json").read_text()),
                                    [json.loads((d15 / f"{m}/contract.json").read_text()) for m in ("time_trial", "mastery")],
                                    known=lambda: orchestrate.lane_known_shapes("metadata-forensics", 15))
    assert "NEW to this lane" in txt and "metadata-day-15-synthesis-sha256-order" in txt.split("carried over")[0], txt[:400]
    print("ok  A1 mastery_delta: D15 metadata -> the synthesis id is listed first as NEW to the lane")
else:
    print("ok  A1 mastery_delta: new-to-lane ids first (D15 data absent here)")

# A3) large previous start reply -> public start, never via the daemon / Homebase
saved = {k: getattr(remote, k) for k in ("ROOT", "_BIG_START")}
try:
    remote.ROOT, remote._BIG_START = TMP, {}
    for day, lane, size in ((14, "script-analysis", 650_000), (14, "warmups", 3_000)):
        d = TMP / f"challenges/day{day:02d}/{lane}-x"
        (d / "single_solve").mkdir(parents=True)
        (d / "meta.json").write_text(json.dumps({"lane": lane}))
        (d / "single_solve/start.json").write_bytes(b"x" * size)
    assert remote._big_start("script-analysis-day-15-crumb") is True
    assert remote._big_start("warmups-day-15") is False
    assert remote._big_start("script-analysis-day-15-crumb/mastery") is False      # timed modes: their own path
    assert remote._big_start("script-analysis-day-14-x") is False                  # no EARLIER day
finally:
    for k, v in saved.items():
        setattr(remote, k, v)
print("ok  A3 start routing: previous start.json > 200 KB -> public; small lanes / timed modes / no history unchanged")

# A2) public refetch of a failed live untimed attempt: same files as scoped_pull, sha-checked; wrong attempt -> raise
blob = b"evidence-bytes"
body = {"attempt_id": "A1", "answer_ids": ["set1.a", "set2.b"],
        "questions": [{"id": "set1.a", "artifact": "ev-01.zip -> a.txt"}, {"id": "set2.b", "artifact": "ev-02.zip -> b.txt"}],
        "artifacts": [{"download": "/?op=download&capability=" + "1" * 64, "sha256": hashlib.sha256(blob).hexdigest()},
                      {"download": "/?op=download&capability=" + "2" * 64, "sha256": hashlib.sha256(blob).hexdigest()}]}
saved = {k: getattr(ht, k) for k in ("_post_start", "_get_bytes")}
got_caps = []
try:
    ht._post_start = lambda payload, tries=3: body
    ht._get_bytes = lambda cap, timeout=20: (got_caps.append(cap), blob)[1]
    local = TMP / "tmp-timed" / "c_mastery"
    res = {"attempt_id": "A1", "result": "incorrect", "wrong": [["set2.b", "x"]], "deadline": None, "run_for_time": False}
    names = workers.public_pull(res, "c_mastery", local, "c/mastery")
    assert names == ["ev-02.zip"] and got_caps == ["2" * 64], (names, got_caps)          # only the failing set
    assert json.loads((local / "contract.json").read_text())["attempt_id"] == "A1" and (local / "result.json").exists()
    ht._post_start = lambda payload, tries=3: {**body, "attempt_id": "OTHER"}
    try:
        workers.public_pull(res, "c_mastery", local, "c/mastery")
        raise AssertionError("a different attempt must not be adopted")
    except RuntimeError:
        pass
finally:
    for k, v in saved.items():
        setattr(ht, k, v)
print("ok  A2 public refetch: failing set only, contract/result saved, sha-checked; another attempt -> fallback")

# A4) binary duel gate
saved = duel.BINARY_MIN_AVAIL_GB, duel._mem_avail_gb
try:
    duel.BINARY_MIN_AVAIL_GB = 0
    assert duel.eligible("binary-reverse-engineering")[0] is False
    duel.BINARY_MIN_AVAIL_GB, duel._mem_avail_gb = 3.0, (lambda: 5.0)
    assert duel.eligible("binary-reverse-engineering")[0] is True
    duel._mem_avail_gb = lambda: 2.0
    assert duel.eligible("binary-reverse-engineering")[0] is False
finally:
    duel.BINARY_MIN_AVAIL_GB, duel._mem_avail_gb = saved
print("ok  A4 binary duel: off by default; on only with the knob set and enough MemAvailable")

shutil.rmtree(TMP, ignore_errors=True)
print("ALL PASS")
