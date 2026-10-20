"""Offline check: every rtab_*.{bin,json} fixture through lib.binary.resource_table_field(data, id): each oracle key
("expected", from rtab_oracle.sh) must match, < 1 s per fixture; garbage / None input -> "none" / None without raising.
usage (repo root): python3 tests/data/binary_fixtures/rtab_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("rtab_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.resource_table_field(data, k) for k in f["expected"]}
    ms = (time.time() - t) * 1e3
    diff = {k: (got[k], v) for k, v in f["expected"].items() if got[k] != v}
    ok = not diff and ms < 1000 and B.resource_table_field(data, "nonexistent_zzz") == "none"
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {len(got)} ids {ms:.1f} ms")
    for k, (g, w) in diff.items():
        print(f"     {k}: got {g!r}\n     {' ' * len(k)}  want {w!r}")
print(B.resource_table_field(b"garbage", "resource_count"), B.resource_table_field(None, "x"),
      B.resource_table_field(b"RT21" + b"\0" * 40, "boundaries"))
sys.exit(1 if bad else 0)
