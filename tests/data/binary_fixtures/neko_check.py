"""Offline check: every neko_*.{bin,json} fixture (raw nekoc / haxe -neko / nekotools boot / decoys) through
lib.binary.machine_facts + neko_facts + hcfg_scan. usage (repo root): python3 tests/data/binary_fixtures/neko_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("neko_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    mf = B.machine_facts(data) or {}
    nf = B.neko_facts(data) or {}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    got = {"format": mf.get("format", "none"), "machine": mf.get("machine", "none"),
           "has_neko_runtime": nf.get("has_neko_runtime", "none"), "bytecode_offset": nf.get("bytecode_offset", "none"),
           "encoding": hit.encoding if hit else "none", "offset": hit.offset if hit else None,
           "config": hit.config if hit else None}
    if f["expected_format"] == "none":
        got["format"] = nf.get("format", "none") if not mf else got["format"]
    want = {"format": f["expected_format"], "machine": f["expected_machine"],
            "has_neko_runtime": f["expected_has_neko_runtime"], "bytecode_offset": f["expected_bytecode_offset"],
            "encoding": f["encoding"], "offset": f["expected_offset"], "config": f["expected_config"]}
    for k in ("globals_count", "fields_count", "code_size"):
        if "expected_" + k in f:
            got[k], want[k] = nf.get(k, "none"), f["expected_" + k]
    if f["expected_offset"] is not None:   # neko_facts' own string-global locator agrees with the scan
        got["neko_hcfg_offset"], want["neko_hcfg_offset"] = nf.get("hcfg_offset"), str(f["expected_offset"])
    diff = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {got['format']}/{got['machine']} {got['encoding']}@"
          f"{got['offset']} ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
