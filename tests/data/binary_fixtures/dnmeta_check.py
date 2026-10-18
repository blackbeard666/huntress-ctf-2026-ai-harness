"""Offline check: every dnmeta_*.{bin,json} fixture through lib.binary.dotnet_meta_field (expected from
System.Reflection.Metadata, see dnmeta_oracle.cs). usage (repo root): python3 tests/data/binary_fixtures/dnmeta_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("dnmeta_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    exp = f["expected"]
    if exp.get("_all") == "none":   # not a CLI assembly: nothing answerable
        probe = ("assembly_name", "mvid", "typedefs", "methods", "method_count", "entry_point_token", "has_field_rva")
        diff = {k: B.dotnet_meta_field(data, k) for k in probe if B.dotnet_meta_field(data, k) not in (None, "none")}
    else:
        diff = {k: (B.dotnet_meta_field(data, k), v) for k, v in exp.items() if B.dotnet_meta_field(data, k) != v}
    ms = (time.time() - t) * 1e3
    bad += bool(diff) or ms > 1000
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {len(exp)} fields ({ms:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
