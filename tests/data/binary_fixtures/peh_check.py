"""Offline check: every peh_*.{bin,json} fixture through lib.binary.pe_header_facts / pe_header_field / header_field
(raw structs, no pefile) against the pefile + objdump oracle values (*_flags compared as sets).
usage (repo root): python3 tests/data/binary_fixtures/peh_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("peh_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    pf = B.pe_header_facts(data)
    want = f["expected_pe_header_facts"]
    if want == "none":
        diff = {"pe_header_facts": pf} if pf is not None else {}
        for k in ("entry_point", "subsystem", "timestamp"):
            if B.pe_header_field(data, k) != "none" or B.header_field(data, k) != "none":
                diff[k] = B.pe_header_field(data, k)
    else:
        norm = lambda k, v: sorted(v) if k.endswith("_flags") else v
        diff = {k: (pf.get(k) if pf else None, v) for k, v in want.items()
                if not pf or norm(k, pf.get(k)) != norm(k, v)}
        if B.header_field(data, "entry_point") != want["entry_point"]:
            diff["header_field"] = B.header_field(data, "entry_point")
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem} ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
elf = (pathlib.Path(__file__).parent / "sstrip_zero.bin").read_bytes()   # dispatch: ELF still goes to elf_header_field
if B.header_field(elf, "entry_point") != B.elf_header_field(elf, "entry_point") or B.pe_header_facts(elf) is not None:
    bad += 1
    print("BAD header_field ELF dispatch")
sys.exit(1 if bad else 0)
