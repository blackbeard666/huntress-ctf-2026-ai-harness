"""Offline check: every macho_*.{bin,json} fixture through lib.binary.macho_layout + machine_facts + hcfg_scan.
usage (repo root): python3 tests/data/binary_fixtures/macho_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("macho_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    lay = B.macho_layout(data) or {}
    mf = B.machine_facts(data) or {}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    got = {"format": lay.get("format", "none"), "machine": lay.get("machine", "none"),
           "machine_num": lay.get("machine_num", "none"), "machines": lay.get("machines", []),
           "fat": lay.get("fat", False), "sections": lay.get("section_names", []),
           "has": lay.get("has_hcfg_section", "none"), "sec_offs": sorted(o for _, o, _ in B.macho_hcfg_section(data)),
           "mf": (mf.get("format", "none"), mf.get("machine", "none")),
           "offset": hit and hit.offset, "config": hit and hit.config}
    want = {"format": f["expected_format"], "machine": f["expected_machine"], "machine_num": f["expected_machine_num"],
            "machines": f["expected_machines"], "fat": f["expected_fat"], "sections": f["expected_section_names"],
            "has": f["expected_has_hcfg_section"], "sec_offs": f["expected_hcfg_section_offsets"],
            "mf": (f["expected_format"], f["expected_machine"]),
            "offset": f["expected_offset"], "config": f["expected_config"]}
    diff = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {got['machines']} has={got['has']} off={got['offset']} "
          f"({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
