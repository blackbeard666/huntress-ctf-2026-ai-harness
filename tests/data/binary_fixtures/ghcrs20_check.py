"""Offline check: ghcrs20_*.{bin,json} (D20 GHC 9.12.2 + RS20 members, decoys) through lib.binary.ghc_facts /
ghc_field / resource_overlay_facts. usage (repo root): python3 tests/data/binary_fixtures/ghcrs20_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
bad = 0
for fj in sorted(here.glob("ghcrs20_*.json")):
    f, data = json.loads(fj.read_text()), fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got, rs = B.ghc_facts(data) or {}, B.resource_overlay_facts(data) or {}
    ms = (time.time() - t) * 1e3
    diff = {k: (got.get(k), v) for k, v in f["expected_facts"].items() if got.get(k) != v}
    diff.update({k: (rs.get(k), v) for k, v in f["expected_rs20"].items() if rs.get(k) != v})
    if B.ghc_field(data, "base_version") != f["expected_facts"]["base_version"]:
        diff["ghc_field"] = B.ghc_field(data, "base_version")
    if B.resource_overlay_facts(b"MZ" + data[2:200]).get("overlay_offset") != "none":
        diff["impostor"] = True
    if ms > 1000:
        diff["ms"] = ms
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
