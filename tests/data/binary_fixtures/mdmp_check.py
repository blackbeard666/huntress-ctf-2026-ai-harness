"""Offline check: every mdmp_*.{bin,json} fixture through lib.binary.minidump_field (+ hcfg_scan stays empty).
usage (repo root): python3 tests/data/binary_fixtures/mdmp_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("mdmp_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    pe = (fj.parent / f["companion"]).read_bytes() if f.get("companion") else None
    t = time.time()
    got = {k: B.minidump_field(data, k, pe=pe) for k in f["expected_facts"]}
    ms = (time.time() - t) * 1e3
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ok = got == f["expected_facts"] and hit is None
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms" + ("" if hit is None else f" unexpected hcfg {hit}"))
    for k in f["expected_facts"]:
        if got[k] != f["expected_facts"][k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {f['expected_facts'][k]!r}")
sys.exit(1 if bad else 0)
