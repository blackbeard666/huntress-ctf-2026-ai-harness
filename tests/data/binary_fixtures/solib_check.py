"""Offline check: every solib_*.{bin,json} fixture through lib.binary.object_facts + hcfg_scan.
usage (repo root): python3 tests/data/binary_fixtures/solib_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("solib_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    of = B.object_facts(data)
    facts = {k: of.get(k) for k in f["expected_facts"]} if of and f["expected_facts"] else None
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    got = (facts, hit and hit.offset, hit and hit.config, hit.encoding if hit else "none")
    want = (f["expected_facts"], f["expected_offset"], f["expected_config"], f["encoding"])
    ok = got == want
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {got[0]} @{got[1]} {got[3]} ({(time.time() - t) * 1e3:.1f} ms)")
    if not ok:
        print("     want", want[0], want[1], want[3])
sys.exit(1 if bad else 0)
