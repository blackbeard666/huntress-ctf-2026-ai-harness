"""Offline check: every march_*.{bin,json} fixture through lib.binary.machine_facts + hcfg_scan.
usage (repo root): python3 tests/data/binary_fixtures/march_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("march_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    mf = B.machine_facts(data) or {}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    got = (mf.get("machine", "none"), mf.get("machine_num", "none"), hit and hit.offset, hit and hit.config,
           hit.encoding if hit else "none")
    want = (f["expected_machine"], f["expected_machine_num"], f["expected_offset"], f["expected_config"], f["encoding"])
    ok = got == want
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {got[:3]} {got[4]} ({(time.time() - t) * 1e3:.1f} ms)")
sys.exit(1 if bad else 0)
