"""Offline check: every ilcs_*.{bin,json} fixture through lib.binary.dotnet_il_facts / dotnet_il_field /
dotnet_field_owner; expected from ilcs_oracle.py (ilspycmd -il + System.Reflection.Metadata).
usage (repo root): python3 tests/data/binary_fixtures/ilcs_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B


def norm(k, v, unordered):
    if k not in unordered:
        return v
    x = json.loads(v)
    if isinstance(x, dict):
        return json.dumps({a: sorted(b) for a, b in sorted(x.items())})
    return json.dumps(sorted(json.dumps(i, sort_keys=True) for i in x))


bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("ilcs_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    exp, un = f["expected"], set(f.get("unordered", ()))
    if exp.get("_all") == "none":
        diff = {k: v for k, v in (("facts", B.dotnet_il_facts(data)), ("field", B.dotnet_il_field(data, "native_edges")),
                                  ("owner", B.dotnet_field_owner(data, 4096))) if v is not None}
    else:
        got = dict(B.dotnet_il_facts(data))
        got["array_inits_brief"] = json.dumps([{k: a[k] for k in ("method", "il", "field", "rva", "offset")}
                                               for a in json.loads(got["array_inits"])])
        diff = {k: (got.get(k, "none"), v) for k, v in exp.items() if norm(k, got.get(k, "none"), un) != norm(k, v, un)}
        for k, v in f.get("expected_lookups", {}).items():
            g = B.dotnet_il_field(data, k)
            if norm("x", g, {"x"} if g != "none" else ()) != norm("x", v, {"x"} if v != "none" else ()):
                diff["lookup:" + k] = (g, v)
        for p in f.get("field_owner_probes", ()):
            o = B.dotnet_field_owner(data, p["offset"])
            if not o or o["field"] != p["field"]:
                diff[f"owner@{p['offset']}"] = (o, p["field"])
    ms = (time.time() - t) * 1e3
    bad += bool(diff) or ms > 1000
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {len(exp)} fields ({ms:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
