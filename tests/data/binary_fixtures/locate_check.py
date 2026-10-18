"""Offline check: every locate_*.{bin,json} fixture through lib.binary.locate_offset (expected = locate_oracle.py:
readelf / pefile / lief / wasm-objdump), plus the cached Day 17 members (D17 .rodata, D14 .hcfg, D12 .data, readelf).
usage (repo root): python3 tests/data/binary_fixtures/locate_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

HERE = pathlib.Path(__file__).parent
cases = [(fj.stem, fj.with_suffix(".bin"), j["probe_offset"], j["expected"])
         for fj in sorted(HERE.glob("locate_*.json")) for j in [json.loads(fj.read_text())]]
ev = ROOT / "challenges/day17/binary-decoder-ring/single_solve/work/extracted/evidence"
D17 = {"d17--variant-000.elf": (207432, {"section": ".rodata", "vaddr": "0x432a48"}),
       "d14--variant-000.elf": (4000, {"section": ".hcfg", "vaddr": "0x400fa0"}),
       "d12--variant-000.elf": (82928, {"section": ".data", "section_flags": "WA", "vaddr": "0x4153f0"}),
       "d16--variant-000-direct.wasm": (125, {"wasm_data_index": 0, "wasm_mem_offset": 1024})}
cases += [("d17/" + n, ev / n, o, dict(want, container="wasm" if n.endswith("wasm") else "elf"))
          for n, (o, want) in D17.items() if (ev / n).is_file()]
bad = 0
for name, path, off, want in cases:
    t = time.time()
    try:
        got = B.locate_offset(path.read_bytes(), off)
    except Exception as e:   # noqa: BLE001 -- must never raise
        got = f"RAISED {e!r}"
    ok = got is None if want is None else isinstance(got, dict) and all(got.get(k) == v for k, v in want.items())
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{name} @{off}: {got!r} (want {want!r}, {(time.time() - t) * 1e3:.0f} ms)")
for junk in (b"", b"\x7fELF", b"\x7fELF\2\1" + b"\xff" * 60, b"MZ" + b"\0" * 62, b"\0asm\1\0\0\0\x0b\xff",
             b"\xcf\xfa\xed\xfe" + b"\xff" * 40, b"\xca\xfe\xba\xbe\0\0\0\x34" + b"\0" * 40):
    try:
        r = B.locate_offset(junk, 4)
    except Exception as e:   # noqa: BLE001
        r, bad = f"RAISED {e!r}", bad + 1
        print(f"BAD junk {junk[:8]!r}: {r}")
sys.exit(1 if bad else 0)
