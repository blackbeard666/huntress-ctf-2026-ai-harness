"""Offline check: every ldr_*.{bin,json} fixture through lib.binary.elf_loader_facts / elf_loader_field /
resolve_library (+ hcfg_scan stays empty). usage (repo root): python3 tests/data/binary_fixtures/ldr_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

here, bad = pathlib.Path(__file__).parent, 0
for fj in sorted(here.glob("ldr_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    lf = B.elf_loader_facts(data)
    want = f["expected_facts"]
    got = {k: lf.get(k) for k in want} if lf and want else lf
    errs = [] if got == want else [f"facts got {got}\n          want {want}"]
    for k, v in f.get("expected_field", {}).items():
        if B.elf_loader_field(data, k) != v:
            errs.append(f"field {k}: got {B.elf_loader_field(data, k)!r} want {v!r}")
    if "resolve" in f:
        r = f["resolve"]
        mem = {n: (here / b).read_bytes() for n, b in r["members"].items()}
        for nm, v in r["expected"].items():
            if B.resolve_library(data, nm, mem) != v:
                errs.append(f"resolve {nm}: got {B.resolve_library(data, nm, mem)!r} want {v!r}")
        if B.resolve_library(data, None, list(mem.items())) != r["expected_needed_map"]:
            errs.append(f"needed map: {B.resolve_library(data, None, mem)}")
    if any(h.valid for h in B.hcfg_scan(data)):
        errs.append("unexpected hcfg")
    bad += bool(errs)
    print(("ok  " if not errs else "BAD ") + f"{fj.stem}: {(time.time() - t) * 1e3:.1f} ms")
    for e in errs:
        print("     " + e)
sys.exit(1 if bad else 0)
