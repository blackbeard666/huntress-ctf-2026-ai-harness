"""Offline check: every mmnat_*.{bin,json} fixture through lib.binary.dotnet_native_facts / dotnet_native_field
(expected from System.Reflection.PortableExecutable (mmnat_oracle.cs), the program's own run of the shellcode via mmap,
objdump and sha256sum -- see each json). usage (repo root): python3 tests/data/binary_fixtures/mmnat_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("mmnat_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.dotnet_native_facts(data)
    dt = time.time() - t
    exp = f["expected"]
    if exp is None:
        errs = [] if got is None and B.dotnet_native_field(data, "cor20_flags") is None else [("facts", got)]
    else:
        errs = [(k, (got or {}).get(k), v) for k, v in exp.items() if (got or {}).get(k) != v]
        errs += [(q, B.dotnet_native_field(data, q), v) for q, v in f.get("expected_lookups", {}).items()
                 if B.dotnet_native_field(data, q) != v]
    if dt > 1.0:
        errs.append(("slow", round(dt, 3)))
    bad += bool(errs)
    print(("FAIL " if errs else "ok   ") + fj.stem, round(dt, 3), errs[:6])
sys.exit(1 if bad else 0)
