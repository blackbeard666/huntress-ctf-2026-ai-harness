"""Offline check: every ovchain_*.{bin,json} fixture through lib.binary.overlay_chain (multi-layer / decoy overlays);
expected values come from ovchain_oracle.py (independent reader). usage (repo root): python3 tests/data/binary_fixtures/ovchain_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("ovchain_*.json")):
    want = json.loads(fj.read_text())["expected"]
    t = time.time()
    got = B.overlay_chain(fj.with_suffix(".bin").read_bytes())
    diff = {k: (got.get(k) if got else None, v) for k, v in want.items() if not got or got.get(k) != v}
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem} ({(time.time() - t) * 1e3:.0f} ms) {diff or ''}")
for junk in (b"", b"PK19", b"\x7fELF" + b"PK19" * 20, b"MZ" + b"\0" * 62 + b"PK19" + b"\xff" * 60):
    r = B.overlay_chain(junk)
    if r is None or r["layer_count"] != 0:
        bad += 1
        print(f"BAD junk {junk[:8]!r}: {r!r}")
sys.exit(1 if bad else 0)
