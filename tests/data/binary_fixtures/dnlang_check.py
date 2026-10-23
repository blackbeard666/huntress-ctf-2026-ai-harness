"""Offline check: every dnlang_*.{bin,json} fixture through lib.binary.dotnet_language_of / dotnet_language_field
(expected from System.Reflection.Metadata, see dnlang_oracle.cs); the F# fixture also pins pe_cli / i386 and the
HCFG byte[] blob as the first hcfg_scan hit. usage (repo root): python3 tests/data/binary_fixtures/dnlang_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("dnlang_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.dotnet_language_of(data)
    ms = (time.time() - t) * 1e3
    exp = f["expected"]
    if exp.get("_all") == "none":
        diff = {"got": got and got["language"]} if got is not None or B.dotnet_language_field(data) != "none" else {}
    else:
        diff = {k: ((got or {}).get(k), v) for k, v in exp.items() if (got or {}).get(k) != v}
        if f.get("decoy") and isinstance(v := B.dotnet_language_field(data, "fsharp_resources"), str) and v != "[]":
            diff["fsharp_resources_field"] = v
    if "expected_format" in f:
        fmt = (B.dotnet_build_facts(data) or {}).get("format")
        mach = B.pe_header_field(data, "machine")
        hits = B.hcfg_scan(data)
        h = hits[0] if hits else None
        if fmt != f["expected_format"] or mach != f["expected_machine"]:
            diff["format/machine"] = (fmt, mach)
        if not h or (h.offset, h.encoding, h.config) != (f["expected_offset"], f["encoding"], f["expected_config"]):
            diff["hcfg"] = h and (h.offset, h.encoding, h.config)
    if ms > 1000:
        diff["ms"] = round(ms)
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {got and got['language']} ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
