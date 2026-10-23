"""Offline check: every garble_*.{bin,json} fixture through lib.binary.garble_facts / garble_field (+ hcfg_scan empty).
usage (repo root): python3 tests/data/binary_fixtures/garble_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("garble_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.garble_facts(data)
    ms = (time.time() - t) * 1e3
    exp = f["expected_facts"]
    ok = got == exp and (exp is None or all(B.garble_field(data, k) == v for k, v in exp.items()))
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ok = ok and hit is None
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    if got != exp:
        print(f"     got  {got!r}\n     want {exp!r}")
sys.exit(1 if bad else 0)
