"""Offline check: every jnib_*.json fixture through lib.binary.jni_bridge_facts (jar + native lib pair).
usage (repo root): python3 tests/data/binary_fixtures/jnib_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

here, bad = pathlib.Path(__file__).parent, 0
for fj in sorted(here.glob("jnib_*.json")):
    f = json.loads(fj.read_text())
    jar, so = (here / f["jar"]).read_bytes(), (here / f["so"]).read_bytes()
    t = time.time()
    got = B.jni_bridge_facts(jar, so)
    swapped = B.jni_bridge_facts(so, jar)   # order-free
    ms = (time.time() - t) * 1e3 / 2
    want = f["expected_facts"]
    ok = got is None if want is None else got is not None and all(got.get(k) == v for k, v in want.items())
    ok = ok and got == swapped
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    for k, v in (want or {}).items():
        if got is not None and got.get(k) != v:
            print(f"     {k}: got {got.get(k)!r}\n     {' ' * len(k)}  want {v!r}")
sys.exit(1 if bad else 0)
