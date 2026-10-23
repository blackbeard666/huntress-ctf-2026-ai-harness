"""Offline check: every mlink_*.{bin,json} fixture through lib.binary.macho_link_facts / macho_link_field + hcfg_scan.
usage (repo root): python3 tests/data/binary_fixtures/mlink_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("mlink_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    facts = B.macho_link_facts(data)
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    want = f["expected_facts"]
    if want is None:
        diff = {"facts": facts} if facts is not None or B.macho_link_field(data, "dylibs") != "none" else {}
    else:
        diff = {k: (facts and facts.get(k), v) for k, v in want.items() if not facts or facts.get(k) != v}
    if (hit and hit.offset, hit and hit.config) != (f["expected_offset"], f["expected_config"]):
        diff["hcfg"] = (hit and hit.offset, f["expected_offset"])
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem} ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
