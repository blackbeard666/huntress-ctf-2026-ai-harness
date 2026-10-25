"""Offline check: every bpatch_*.json fixture (base + patch .bin) through lib.binary.binary_patch_field.
usage (repo root): python3 tests/data/binary_fixtures/bpatch_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad, d = 0, pathlib.Path(__file__).parent
for fj in sorted(d.glob("bpatch_*.json")):
    f = json.loads(fj.read_text())
    base, patch = (d / f["base"]).read_bytes(), fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.binary_patch_field(base, patch, k) for k in f["expected_facts"]}
    ms = (time.time() - t) * 1e3
    ok = got == f["expected_facts"]
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    for k in f["expected_facts"]:
        if got[k] != f["expected_facts"][k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {f['expected_facts'][k]!r}")
sys.exit(1 if bad else 0)
