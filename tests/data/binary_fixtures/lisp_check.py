"""Offline check: lisp_*.{bin,json} fixtures through lib.binary.lisp_facts / lisp_field / hcfg_find.
usage (repo root): python3 tests/data/binary_fixtures/lisp_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
bad = 0
for fj in sorted(here.glob("lisp_*.json")):
    f, data = json.loads(fj.read_text()), fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.lisp_facts(data)
    ms = (time.time() - t) * 1e3
    exp = f["expected_facts"]
    diff = {k: (got.get(k) if got else None, v) for k, v in exp.items() if got is None or got.get(k) != v}
    hit = B.hcfg_find(data)
    if (hit.offset if hit else "none") != f["expected_offset"] or (hit.encoding if hit else "none") != f["encoding"]:
        diff["hit"] = (hit and (hit.offset, hit.encoding), f["expected_offset"], f["encoding"])
    if (hit.config if hit else "none") != f["expected_config"]:
        diff["config"] = hit and hit.config
    if got and (got["hcfg_offset"], got["hcfg_encoding"]) != (f["expected_offset"], f["encoding"]):
        diff["facts_hit"] = (got["hcfg_offset"], got["hcfg_encoding"])
    if B.lisp_field(data[:100], "lisp_runtime") != "none" or B.lisp_facts(b"MZ" + data[2:]) is not None:
        diff["truncated/impostor"] = True
    if ms > 1000:
        diff["ms"] = ms
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
