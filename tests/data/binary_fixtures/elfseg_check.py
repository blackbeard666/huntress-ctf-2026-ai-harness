"""Offline check: every elfseg_*.{bin,json} fixture through lib.binary.elf_header_facts (program-header / ABI fields);
decoys must give elf_header_field(...) == "none" for every field, and no fixture may yield an HCFG hit.
usage (repo root): python3 tests/data/binary_fixtures/elfseg_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("elfseg_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    ef = B.elf_header_facts(data)
    want = f["expected_elf_segment_facts"]
    if want == "none":
        diff = {k: B.elf_header_field(data, k) for k in ("e_flags", "os_abi", "segments", "interpreter", "relro",
                                                         "is_pie") if B.elf_header_field(data, k) != "none"}
    else:
        diff = {k: (ef.get(k) if ef else None, v) for k, v in want.items() if not ef or ef.get(k) != v}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    if (hit.offset if hit else "none") != f["expected_offset"]:
        diff["offset"] = (hit.offset, f["expected_offset"])
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
