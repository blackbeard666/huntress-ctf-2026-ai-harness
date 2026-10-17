"""Offline check: every sstrip_*.{bin,json} fixture through lib.binary.elf_header_facts (+ hcfg_scan), and pyelftools
(lib.elf) must not be needed: the header facts come from the raw structs.
usage (repo root): python3 tests/data/binary_fixtures/sstrip_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("sstrip_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    ef = B.elf_header_facts(data)
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    want = f["expected_elf_header_facts"]
    diff = {k: (ef.get(k) if ef else None, v) for k, v in want.items() if not ef or ef.get(k) != v} \
        if want != "none" else ({"elf_header_facts": (ef, None)} if ef is not None else {})
    if want == "none" and B.elf_header_field(data, "entry_point") != "none":
        diff["field"] = B.elf_header_field(data, "entry_point")
    got_off = hit.offset if hit else "none"
    if got_off != f["expected_offset"]:
        diff["offset"] = (got_off, f["expected_offset"])
    if (hit.config if hit else "none") != f["expected_config"]:
        diff["config"] = (hit.config if hit else "none", f["expected_config"])
    if ef and ef["hcfg_config"] != f["expected_config"]:
        diff["hcfg_config"] = (ef["hcfg_config"], f["expected_config"])
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: off={got_off} ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
