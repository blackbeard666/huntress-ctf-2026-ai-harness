"""Offline check: every fault_*.json fixture through lib.binary.fault_insn_field (args: va / offset / question /
core companion). usage (repo root): python3 tests/data/binary_fixtures/fault_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("fault_*.json")):
    f = json.loads(fj.read_text())
    data = (fj.parent / f["input"]).read_bytes()
    a = dict(f["args"])
    if "core" in a:
        a["core"] = (fj.parent / a["core"]).read_bytes()
    t = time.time()
    exp = f["expected_facts"]
    got = B.fault_insn_facts(data, **a) if exp is None else {k: B.fault_insn_field(data, k, **a) for k in exp}
    ms = (time.time() - t) * 1e3
    ok = got == exp
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    if not ok and exp is None:
        print(f"     want None, got {got}")
    for k in exp or ():
        if got[k] != exp[k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {exp[k]!r}")
sys.exit(1 if bad else 0)
