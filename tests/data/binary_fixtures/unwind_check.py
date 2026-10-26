"""Offline check: every unwind_*.json fixture through lib.binary.stack_unwind_field (+ hcfg_scan stays empty).
usage (repo root): python3 tests/data/binary_fixtures/unwind_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

here, bad = pathlib.Path(__file__).parent, 0
for fj in sorted(here.glob("unwind_*.json")):
    f = json.loads(fj.read_text())
    data = (here / f["data_file"]).read_bytes()
    exe = (here / f["exe_file"]).read_bytes() if f.get("exe_file") else None
    t = time.time()
    got = {k: B.stack_unwind_field(data, k, exe=exe) for k in f["expected_facts"]}
    ms = (time.time() - t) * 1e3
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ok = got == f["expected_facts"] and hit is None
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms" + ("" if hit is None else f" unexpected hcfg {hit}"))
    for k in f["expected_facts"]:
        if got[k] != f["expected_facts"][k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {f['expected_facts'][k]!r}")
sys.exit(1 if bad else 0)
