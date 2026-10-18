"""Offline check: cobol_*.{bin,json} fixtures through lib.binary.cobol_facts / cobol_field / hcfg_find / hcfg_storage.
usage (repo root): python3 tests/data/binary_fixtures/cobol_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
bad = 0
for fj in sorted(here.glob("cobol_*.json")):
    f, data = json.loads(fj.read_text()), fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.cobol_facts(data)
    hit = B.hcfg_find(data)
    ms = (time.time() - t) * 1e3
    diff = {k: (got.get(k) if got else None, v) for k, v in f["expected_facts"].items() if got is None or got.get(k) != v}
    if (hit.offset if hit else "none") != f["expected_offset"] or (hit.encoding if hit else "none") != f["encoding"]:
        diff["hcfg"] = (hit and (hit.offset, hit.encoding), f["expected_offset"], f["encoding"])
    if (hit.config if hit else "none") != f["expected_config"]:
        diff["config"] = hit and hit.config
    if f["encoding"] == "split-raw" and B.hcfg_storage(data) != "raw_const_array":
        diff["storage"] = B.hcfg_storage(data)
    if B.cobol_field(data[:100], "has_cobol_runtime") not in ("none", "false") or B.cobol_facts(b"MZ" + data[2:]) is not None:
        diff["truncated/impostor"] = True
    if ms > 1000:
        diff["ms"] = ms
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
