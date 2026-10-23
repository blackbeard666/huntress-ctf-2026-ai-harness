"""Offline check: every xbridge_*.json fixture through lib.binary.extension_bridge_facts (+ hcfg_scan stays empty).
usage (repo root): .venv/bin/python tests/data/binary_fixtures/xbridge_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

here, bad = pathlib.Path(__file__).parent, 0
for fj in sorted(here.glob("xbridge_*.json")):
    f = json.loads(fj.read_text())
    data = (here / f["file"]).read_bytes()
    t = time.time()
    got = B.extension_bridge_facts(data)
    ms = (time.time() - t) * 1e3
    want = f["expected_facts"]
    ok = got is None if want is None else got is not None and all(got.get(k) == v for k, v in want.items())
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ok = ok and hit is None and ms < 1000
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms" + ("" if hit is None else f" unexpected hcfg {hit}"))
    for k, v in (want or {}).items():
        if got is None or got.get(k) != v:
            print(f"     {k}: got {None if got is None else got.get(k)!r}\n     {' ' * len(k)}  want {v!r}")
    if want is not None and got is None:
        print("     got None")
sys.exit(1 if bad else 0)
