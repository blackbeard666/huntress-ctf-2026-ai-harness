"""Offline check: every dynlink_*.json fixture (loader + plugin pair) through lib.binary.dynlink_facts.
usage (repo root): python3 tests/data/binary_fixtures/dynlink_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

here, bad = pathlib.Path(__file__).parent, 0
for fj in sorted(here.glob("dynlink_*.json")):
    f = json.loads(fj.read_text())
    t = time.time()
    got = B.dynlink_facts((here / f["loader"]).read_bytes(), (here / f["plugin"]).read_bytes())
    ms = (time.time() - t) * 1e3
    want = f["expected_facts"]
    ok = got is None if want is None else got is not None and all(got.get(k) == v for k, v in want.items())
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    for k, v in (want or {}).items():
        if got is not None and got.get(k) != v:
            print(f"     {k}: got {got.get(k)!r}\n     {' ' * len(k)}  want {v!r}")
sys.exit(1 if bad else 0)
