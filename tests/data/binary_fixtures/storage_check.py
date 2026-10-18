"""Offline check: every storage_*.{bin,json} fixture through lib.binary.hcfg_storage (D17 hcfg_storage rule list), plus
the cached Day 17 single_solve members when they are on disk (GM-confirmed d08/d09/d11 base64, d12 raw_const_array,
d14 raw_hcfg_section; the rest by the rule list via readelf/pefile/wasm-objdump, NOT GM-confirmed).
usage (repo root): python3 tests/data/binary_fixtures/storage_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

D17 = {"d02--variant-000.elf": "raw_hcfg_section", "d03--variant-000.dll": "raw", "d04--variant-000.elf": "raw_const_array",
       "d05--variant-000.elf": "raw_const_array", "d06--variant-000.jar": "base64", "d07--variant-000.jar": "base64",
       "d08--variant-000.elf": "base64", "d09--variant-000.elf": "base64", "d10--variant-000.elf": "raw_hcfg_section",
       "d11--variant-000.elf": "base64", "d12--variant-000.elf": "raw_const_array", "d13--variant-000.elf": "base64",
       "d14--variant-000.elf": "raw_hcfg_section", "d15--variant-000-stripped.elf": "raw_hcfg_section",
       "d15--variant-000-symbolized.elf": "raw_hcfg_section", "d16--variant-000-direct.wasm": "wasm_data_segment",
       "d16--variant-000-compact.wasm": "wasm_data_segment", "d17--variant-000.elf": "raw_const_array",
       "d01--variant-000.elf": "none"}
bad = 0
cases = [(fj.stem, fj.with_suffix(".bin"), json.loads(fj.read_text())["expected_storage"])
         for fj in sorted(pathlib.Path(__file__).parent.glob("storage_*.json"))]
ev = ROOT / "challenges/day17/binary-decoder-ring/single_solve/work/extracted/evidence"
cases += [("d17/" + n, ev / n, want) for n, want in D17.items() if (ev / n).is_file()]
for name, path, want in cases:
    t = time.time()
    try:
        got = B.hcfg_storage(path.read_bytes())
    except Exception as e:   # noqa: BLE001 -- must never raise
        got = f"RAISED {e!r}"
    ok = got == want and (got is None or got in B.HCFG_STORAGE_TOKENS + ("none",))
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{name}: {got!r} (want {want!r}, {(time.time() - t) * 1e3:.0f} ms)")
for junk in (b"", b"\x7fELF", b"MZ" + b"\0" * 62, b"\0asm\1\0\0\0\x0b\xff", b"PK\3\4garbage", b"\xcf\xfa\xed\xfe" + b"\xff" * 40):
    r = B.hcfg_storage(junk)
    if r not in ("none", None):
        bad += 1
        print(f"BAD junk {junk[:8]!r}: {r!r}")
sys.exit(1 if bad else 0)
