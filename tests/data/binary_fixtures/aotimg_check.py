"""Offline check: every aotimg_*.{bin,json} fixture through lib.binary.aot_image_field (+ hcfg_scan agrees with
expected_offset / expected_config). usage (repo root): python3 tests/data/binary_fixtures/aotimg_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("aotimg_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.aot_image_field(data, k) for k in f["expected_facts"]}
    ms = (time.time() - t) * 1e3
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    hit_ok = (hit is None) if f["expected_offset"] is None else (
        hit is not None and hit.offset == f["expected_offset"] and hit.config == f["expected_config"])
    ok = got == f["expected_facts"] and hit_ok
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms" + ("" if hit_ok else f" hcfg_scan {hit}"))
    for k in f["expected_facts"]:
        if got[k] != f["expected_facts"][k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {f['expected_facts'][k]!r}")
sys.exit(1 if bad else 0)
