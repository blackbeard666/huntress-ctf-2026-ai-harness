"""Offline check: every vtp_*.json twin pair through lib.binary.jvm_trigger_field (expected_facts null -> None).
usage (repo root): python3 tests/data/binary_fixtures/vtp_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad, here = 0, pathlib.Path(__file__).parent
for fj in sorted(here.glob("vtp_*.json")):
    f = json.loads(fj.read_text())
    a, b = (here / f["jar_a"]).read_bytes(), (here / f["jar_b"]).read_bytes()
    t = time.time()
    if f["expected_facts"] is None:
        got = B.jvm_trigger_proof(a, b)
        ok = got is None
    else:
        got = {k: B.jvm_trigger_field(a, b, k) for k in f["expected_facts"]}
        ok = got == f["expected_facts"]
    ms = (time.time() - t) * 1e3
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    if not ok:
        print(f"     got  {got!r}\n     want {f['expected_facts']!r}")
sys.exit(1 if bad else 0)
