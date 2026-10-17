"""Offline check: every dnsf_*.{bin,json} fixture through lib.binary.hcfg_scan + dotnet_build_facts + hcfg_locate.
usage (repo root): python3 tests/data/binary_fixtures/dnsf_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("dnsf_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    df = B.dotnet_build_facts(data) or {}
    facts = {k: df.get(k) for k in f["expected_facts"]}
    loc = B.hcfg_locate(data, hit.offset) if hit and f["expected_locate"] else None
    loc = {k: loc.get(k) for k in f["expected_locate"]} if loc else None
    got = (hit.encoding if hit else "none", hit and hit.offset, hit and hit.config, facts, loc,
           hit.detail if hit and "expected_detail" in f else f.get("expected_detail"))
    want = (f["encoding"], f["expected_offset"], f["expected_config"], f["expected_facts"], f["expected_locate"],
            f.get("expected_detail"))
    ok = got == want
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {got[0]} @{got[1]} {got[3]} {got[4]} ({(time.time() - t) * 1e3:.1f} ms)")
    if not ok:
        print("     want", want)
sys.exit(1 if bad else 0)
