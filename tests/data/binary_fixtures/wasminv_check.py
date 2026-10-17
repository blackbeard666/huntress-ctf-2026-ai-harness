"""Offline check: every wasminv_*.{bin,json} fixture through lib.binary.wasm_field (each expected_fields entry) +
hcfg_scan (raw offset / config). usage (repo root): python3 tests/data/binary_fixtures/wasminv_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("wasminv_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.wasm_field(data, k) for k in f["expected_fields"]}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    got["_offset"], got["_config"] = (hit.offset, hit.config) if hit else ("none", "none")
    want = dict(f["expected_fields"], _offset=f["expected_offset"], _config=f["expected_config"])
    diff = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {len(want)} fields ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
