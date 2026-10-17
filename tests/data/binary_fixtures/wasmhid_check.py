"""Offline check: every wasmhid_*.{bin,json} fixture (hidden HCFG in wasm: custom section / passive+memory.init /
split over adjacent segments / built by i32.store immediates) through lib.binary hcfg_scan + wasm_fields.
usage (repo root): python3 tests/data/binary_fixtures/wasmhid_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("wasmhid_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    wf = B.wasm_fields(data) or {}
    got = {"format": wf.get("format", "none"), "machine": wf.get("machine", "none"),
           "offset": hit.offset if hit else "none", "encoding": hit.encoding if hit else f["encoding"],
           "config": hit.config if hit else "none", "fields_offset": wf.get("hcfg_offset"),
           "mem": wf.get("hcfg_mem_offset"), "has_sec": wf.get("has_hcfg_section"), "storage": wf.get("hcfg_storage")}
    want = {"format": f["expected_format"], "machine": f["expected_machine"], "offset": f["expected_offset"],
            "encoding": f["encoding"], "config": f["expected_config"], "fields_offset": f["expected_offset"],
            "mem": f["expected_mem_offset"], "has_sec": f["expected_has_hcfg_section"], "storage": f["expected_storage"]}
    diff = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {got['encoding']} off={got['offset']} mem={got['mem']} "
          f"({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
