"""Offline check: decoder_*.{bin,json} fixtures through lib.binary.decoder_field (blob located by hcfg_find).
usage (repo root): python3 tests/data/binary_fixtures/decoder_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
bad = 0
for fj in sorted(here.glob("decoder_*.json")):
    f, data = json.loads(fj.read_text()), fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.decoder_field(data, k) for k in f["expected_fields"]}
    got["xrefs"] = [hex(x) for x in got["xrefs"]] if isinstance(got["xrefs"], list) else got["xrefs"]
    ms = (time.time() - t) * 1e3
    diff = {k: (got[k], v) for k, v in f["expected_fields"].items() if got[k] != v}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem} ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
