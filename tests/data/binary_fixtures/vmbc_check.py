"""Offline check: every vmbc_*.{bin,json} fixture through lib.binary.hcfg_scan (+ vm_trace program size).
usage (repo root): python3 tests/data/binary_fixtures/vmbc_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("vmbc_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ms = (time.time() - t) * 1e3
    got = (hit.encoding, hit.offset, hit.config) if hit else ("none", None, None)
    want = (f["encoding"], f["expected_offset"], f["expected_config"])
    r = B.vm_trace(data) if hit else None
    ok = got == want and ms < 1000 and (not hit or r["program_size"] == f["expected_program_size"])
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms {got[0]} @{got[1]}" + ("" if ok else f"  want {want[:2]}"))
sys.exit(1 if bad else 0)
