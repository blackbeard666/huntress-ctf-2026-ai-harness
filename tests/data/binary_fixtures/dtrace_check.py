"""Offline check: every dtrace_*.{bin,json} fixture through lib.binary.dynamic_trace_field.
usage (repo root): python3 tests/data/binary_fixtures/dtrace_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("dtrace_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.dynamic_trace_field(data, k) for k in f["expected_facts"]}
    ms = (time.time() - t) * 1e3
    ok = got == f["expected_facts"]
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    for k in f["expected_facts"]:
        if got[k] != f["expected_facts"][k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {f['expected_facts'][k]!r}")
sys.exit(1 if bad else 0)
