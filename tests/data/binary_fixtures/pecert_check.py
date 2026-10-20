"""Offline check: every pecert_*.{bin,json} fixture through lib.binary.hcfg_scan (offset/encoding/config of the valid
hit) and lib.binary.pe_cert_field (expected_facts). usage (repo root): python3 tests/data/binary_fixtures/pecert_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("pecert_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    got = {k: B.pe_cert_field(data, k) for k in f["expected_facts"]}
    ms = (time.time() - t) * 1e3
    want = (f["expected_offset"], f["encoding"], f["expected_config"])
    ok = (hit is None) if f["expected_offset"] is None else (
        hit is not None and (hit.offset, hit.encoding, hit.config) == want)
    ok = ok and got == f["expected_facts"]
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms " + (f"{hit.offset} {hit.encoding}" if hit else "-"))
    for k in f["expected_facts"]:
        if got[k] != f["expected_facts"][k]:
            print(f"     {k}: got {got[k]!r} want {f['expected_facts'][k]!r}")
sys.exit(1 if bad else 0)
