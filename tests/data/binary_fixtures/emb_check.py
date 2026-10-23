"""Offline check: every emb_*.{bin,json} fixture through lib.binary.embedded_modules / reflection_calls / hcfg_scan.
usage (repo root): python3 tests/data/binary_fixtures/emb_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("emb_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    mods = B.embedded_modules(data)
    got = [{"path": m["path"], "stored_offset": m["stored_offset"], "encoding": m["encoding"], "kind": m["kind"],
            "name": m["name"], "size": m["size"], "sha256": m["sha256"],
            "hcfg_offset": m["hcfg"]["offset"] if m["hcfg"] else None} for m in mods]
    refl = B.reflection_calls(data) or {}
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ms = (time.time() - t) * 1e3
    probs = []
    if got != f["expected_modules"]:
        probs.append(f"modules {got} != {f['expected_modules']}")
    if refl.get("apis") != f["expected_loader_apis"]:
        probs.append(f"apis {refl.get('apis')}")
    if any(s not in refl.get("strings", ()) for s in f.get("expected_loader_strings_include", ())):
        probs.append(f"strings {refl.get('strings')}")
    h = (hit.offset, hit.encoding, hit.config) if hit else (None, None, None)
    if h != (f["expected_offset"], f["encoding"], f["expected_config"]):
        probs.append(f"hcfg {h}")
    if B.embedded_module_field(data, "module_count") != str(len(f["expected_modules"])):
        probs.append("module_count")
    bad += bool(probs)
    print(("ok  " if not probs else "BAD ") + f"{fj.stem}: {ms:.1f} ms " + "; ".join(probs))
sys.exit(1 if bad else 0)
