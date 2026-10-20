"""Offline check: every hl_*.{bin,json} fixture (haxe -hl v4 debug / no-debug, base64 / utf8-raw blob, decoys) through
lib.binary.machine_facts + hashlink_facts + hcfg_scan. usage (repo root): python3 tests/data/binary_fixtures/hl_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("hl_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    mf = B.machine_facts(data) or {}
    hf = B.hashlink_facts(data) or {}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    fmt = mf.get("format", "none") if mf.get("format") == "hashlink_bytecode" else hf.get("format", "none")
    got = {"format": fmt, "machine": hf.get("machine", "none"), "encoding": hit.encoding if hit else "none",
           "offset": hit.offset if hit else None, "config": hit.config if hit else None}
    want = {"format": f["expected_format"], "machine": f["expected_machine"], "encoding": f["encoding"],
            "offset": f["expected_offset"], "config": f["expected_config"]}
    for k in [k[9:] for k in f if k.startswith("expected_") and k[9:] not in want]:
        got[k], want[k] = hf.get(k, "none"), f["expected_" + k]
    if f["expected_offset"] is not None:   # hashlink_facts' own string-table locator agrees with the scan
        got["hl_hcfg_offset"], want["hl_hcfg_offset"] = hf.get("hcfg_offset"), str(f["expected_offset"])
    diff = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {got['format']} {got['encoding']}@{got['offset']} "
          f"({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
