"""Check lib.binary file_map_field against every fmap_*.json `expected` (oracle_cmd output). usage: python3 -I
tests/data/binary_fixtures/fmap_check.py  (run from the repo root)"""
import glob, json, sys, time

sys.path.insert(0, ".")
from lib import binary as B  # noqa: E402

bad = 0
for j in sorted(glob.glob("tests/data/binary_fixtures/fmap_*.json")):
    fx = json.load(open(j))
    data = open(j[:-5] + ".bin", "rb").read()
    exp, t = fx["expected"], time.time()
    if exp is None:
        got = {k: B.file_map_field(data, k) for k in ("cave_offset", "gaps", "hcfg_storage")}
        ok = all(v is None for v in got.values())
    else:
        got = {k: B.file_map_field(data, k) for k in exp if k != "gaps_offsets_sizes"}
        got["gaps_offsets_sizes"] = [[g["offset"], g["size"]] for g in json.loads(B.file_map_field(data, "gaps"))]
        ok = all(str(got[k]) == str(v) for k, v in exp.items())
    bad += not ok
    print("ok  " if ok else "FAIL", j.rsplit("/", 1)[1], "%.3fs" % (time.time() - t), "" if ok else got)
sys.exit(1 if bad else 0)
