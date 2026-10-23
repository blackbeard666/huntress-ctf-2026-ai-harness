"""Offline check: every dnprot_*.{bin,json} fixture through lib.binary.dotnet_protector_field + hcfg_scan.
usage (repo root): python3 tests/data/binary_fixtures/dnprot_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("dnprot_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.dotnet_protector_field(data, k) for k in f["expected_facts"]}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ms = (time.time() - t) * 1e3
    if f["expected_config"] is None:
        hok = hit is None
    else:
        hok = hit is not None and (hit.offset, hit.encoding, hit.config) == (f["expected_offset"], f["encoding"], f["expected_config"])
    ok = got == f["expected_facts"] and hok
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms" + ("" if hok else f" hcfg {hit}"))
    for k in f["expected_facts"]:
        if got[k] != f["expected_facts"][k]:
            print(f"     {k}: got {got[k]!r}  want {f['expected_facts'][k]!r}")
sys.exit(1 if bad else 0)
