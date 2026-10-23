"""Offline check: every msdec_*.{bin,json} fixture through lib.binary.hcfg_scan (managed string decryptor branch).
usage (repo root): python3 tests/data/binary_fixtures/msdec_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("msdec_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    dt = time.time() - t
    got = (hit.encoding, hit.offset, hit.config) if hit else ("none", None, None)
    want = (f["encoding"], f["expected_offset"], f["expected_config"])
    ok = got == want and dt < 1.0
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {got[0]} @{got[1]} ({dt * 1e3:.1f} ms)")
    if not ok:
        print("     want", want)
sys.exit(1 if bad else 0)
