"""Offline check: every scalamod_*.{bin,json} fixture through lib.binary.jvm_field (expected from scalamod_oracle.py:
javap -v -p + unzip). usage (repo root): python3 tests/data/binary_fixtures/scalamod_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("scalamod_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.jvm_field(data, k, f.get("member"), f.get("question")) for k in f["expected"]}
    diff = {k: (got[k], v) for k, v in f["expected"].items() if got[k] != v}
    ms = (time.time() - t) * 1e3
    bad += bool(diff) or ms > 1000
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {len(got)} fields ({ms:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
