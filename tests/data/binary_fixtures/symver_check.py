"""Offline check: every symver_*.{bin,json} fixture through lib.binary.elf_version_field (+ elf_version_facts None
for non-ELF decoys). usage (repo root): python3 tests/data/binary_fixtures/symver_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("symver_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    exp = f["expected_facts"]
    got = B.elf_version_facts(data) if exp is None else {k: B.elf_version_field(data, k) for k in exp}
    ms = (time.time() - t) * 1e3
    ok = got == exp
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    for k in (exp or {}):
        if got[k] != exp[k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {exp[k]!r}")
sys.exit(1 if bad else 0)
