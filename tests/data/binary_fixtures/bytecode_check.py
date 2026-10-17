"""Offline check: every bytecode_*.{bin,json} fixture (LLVM bitcode / .pyc / luac / .class / .dex) through
lib.binary.machine_facts + hcfg_scan. usage (repo root): python3 tests/data/binary_fixtures/bytecode_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("bytecode_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    mf = B.machine_facts(data) or {}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    got = {"format": mf.get("format", "none"), "machine": mf.get("machine", "none"),
           "encoding": hit.encoding if hit else "none", "offset": hit.offset if hit else None,
           "config": hit.config if hit else None}
    want = {"format": f["expected_format"], "machine": f["expected_machine"], "encoding": f["encoding"],
            "offset": f["expected_offset"], "config": f["expected_config"]}
    if want["offset"] is None and hit:   # bit-packed bitcode string: no independent byte offset, not asserted
        want["offset"] = got["offset"]
    diff = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {got['format']}/{got['machine']} {got['encoding']}@"
          f"{got['offset']} ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
