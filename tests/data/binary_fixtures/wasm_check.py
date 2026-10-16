"""Offline check: every wasm_*.{bin,json} fixture through lib.binary.wasm_layout / wasm_hcfg_segment / machine_facts
+ hcfg_scan. usage (repo root): python3 tests/data/binary_fixtures/wasm_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("wasm_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    lay = B.wasm_layout(data) or {}
    mf = B.machine_facts(data) or {}
    seg = next(iter(B.wasm_hcfg_segment(data)), {})
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    got = {"format": lay.get("format", "none"), "machine": lay.get("machine", "none"),
           "mf": (mf.get("format", "none"), mf.get("machine", "none")),
           "offset": hit.offset if hit else "none", "seg_file": seg.get("file_offset", "none"),
           "mem": seg.get("mem_offset", "none"), "segmem": seg.get("segment_mem_offset"),
           "config": hit.config if hit else "none"}
    want = {"format": f["expected_format"], "machine": f["expected_machine"],
            "mf": (f["expected_format"], f["expected_machine"]), "offset": f["expected_offset"],
            "seg_file": f["expected_offset"] if f["expected_mem_offset"] != "none" else "none",
            "mem": f["expected_mem_offset"], "segmem": f["expected_segment_mem_offset"], "config": f["expected_config"]}
    diff = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {got['format']}/{got['machine']} off={got['offset']} "
          f"mem={got['mem']} ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
