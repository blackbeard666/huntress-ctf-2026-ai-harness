"""Offline check: every pinv_*.{bin,json} fixture through lib.binary.dotnet_pinvoke_field (+ the dotnet_meta_field
fallback); expected from System.Reflection.Metadata, see pinv_oracle.cs. usage (repo root): python3 tests/data/binary_fixtures/pinv_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("pinv_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    exp = dict(f["expected"], **f.get("expected_absent", {}))
    if exp.get("_all") == "none":   # not a CLI assembly: nothing answerable
        probe = ("pinvoke_count", "native_modules", "pinvoke_imports", "getpid_module")
        diff = {k: B.dotnet_pinvoke_field(data, k) for k in probe if B.dotnet_pinvoke_field(data, k) is not None}
        if B.dotnet_pinvoke_facts(data) is not None:
            diff["facts"] = "not None"
    else:
        got = B.dotnet_pinvoke_facts(data)
        diff = {k: (got.get(k, "none"), v) for k, v in exp.items() if got.get(k, "none") != v}
        diff.update({"meta:" + k: B.dotnet_meta_field(data, k) for k in ("pinvoke_count", "native_modules")
                     if B.dotnet_meta_field(data, k) != exp[k]})
    ms = (time.time() - t) * 1e3
    bad += bool(diff) or ms > 1000
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {len(exp)} fields ({ms:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
