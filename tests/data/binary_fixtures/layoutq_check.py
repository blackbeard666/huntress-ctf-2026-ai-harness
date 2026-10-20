"""Offline check: every layoutq_*.{bin,json} fixture through lib.binary.layout_field(data, question, id): each oracle
key ("expected", from layoutq_oracle.sh) and each answer-id alias ("ids": resource_size, setN.dNN_analysis_*, ...) must
resolve to the oracle value, < 1 s per fixture; unknown ids and garbage input -> "none" / None without raising.
usage (repo root): python3 tests/data/binary_fixtures/layoutq_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("layoutq_*.json")):
    f = json.loads(fj.read_text())
    data, q = fj.with_suffix(".bin").read_bytes(), f["question"]
    t = time.time()
    want = {}
    for k, v in f["expected"].items():
        if k.endswith("_sha256_actual"):
            r = k[:-len("_sha256_actual")]
            k = r + ("_sha256_computed" if r + "_sha256" in f["expected"] else "_sha256")
        want[k] = v
    want.update(f["ids"])
    diff = {k: (B.layout_field(data, q, k), v) for k, v in want.items() if B.layout_field(data, q, k) != str(v)}
    ms = (time.time() - t) * 1e3
    ok = not diff and ms < 1000 and B.layout_field(data, q, "nonexistent_zzz_field") == "none" and \
        len(B.layout_from_question(q)) >= 2
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {len(want)} ids {ms:.1f} ms {diff or ''}")
print(B.layout_field(b"garbage", "Find the final RS20 overlay. Read x length u32le at +8.", "x_size"),
      B.layout_field(None, None, "x"), B.layout_from_question(12345), B.layout_field(b"RS20", "Find the final RS20 "
      "overlay. Read x length u32le at +8 and y at +9; the body starts at +12.", "body_sha256"))
sys.exit(1 if bad else 0)
