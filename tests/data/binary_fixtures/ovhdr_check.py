"""Offline check: every ovhdr_*.{bin,json} fixture through lib.binary.overlay_header_facts(data, magic); each expected
key must match and the call must stay < 1 s. usage (repo root): python3 tests/data/binary_fixtures/ovhdr_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("ovhdr_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.overlay_header_facts(data, f["magic"]) or {}
    auto = B.overlay_header_facts(data) or {}
    ms = (time.time() - t) * 1e3
    diff = {k: (got.get(k), v) for k, v in f["expected"].items() if got.get(k) != v or auto.get(k) != v}
    ok = not diff and ms < 1000 and B.overlay_header_field(data, "nonexistent_field") == "none"
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms {diff or ''}")
print(B.overlay_header_facts(b"garbage"), B.overlay_header_field(b"\x7fELF\x02", "has_overlay"))
sys.exit(1 if bad else 0)
