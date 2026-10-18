"""Offline check: gfortran_*.{bin,json} fixtures through lib.binary.gfortran_facts / gfortran_field / hcfg_find.
usage (repo root): python3 tests/data/binary_fixtures/gfortran_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
bad = 0
for fj in sorted(here.glob("gfortran_*.json")):
    f, data = json.loads(fj.read_text()), fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.gfortran_facts(data)
    ms = (time.time() - t) * 1e3
    diff = {k: (got.get(k) if got else None, v) for k, v in f["expected_facts"].items() if got is None or got.get(k) != v}
    hit = B.hcfg_find(data)
    if (hit.offset if hit else "none") != f["expected_offset"]:
        diff["expected_offset"] = (hit and hit.offset, f["expected_offset"])
    if f["expected_config"] != "none" and (not hit or B.gfortran_field(data, "hcfg_entity") != f["expected_facts"]["hcfg_entity"]):
        diff["hcfg_field"] = B.gfortran_field(data, "hcfg_entity")
    if B.gfortran_field(data[:100], "has_gfortran_runtime") not in ("none", "false") or B.gfortran_facts(b"MZ" + data[2:]) is not None:
        diff["truncated/impostor"] = True
    if ms > 1000:
        diff["ms"] = ms
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
