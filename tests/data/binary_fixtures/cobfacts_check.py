"""Offline check: cobfacts_*.{bin,json} fixtures through lib.binary.cobol_facts / cobol_field (runtime version,
program-id, source file, NEEDED, cob_* imports). usage (repo root): python3 tests/data/binary_fixtures/cobfacts_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
bad = 0
for fj in sorted(here.glob("cobfacts_*.json")):
    f, data = json.loads(fj.read_text()), fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.cobol_facts(data)
    ms = (time.time() - t) * 1e3
    diff = {k: (got.get(k) if got else None, v) for k, v in f["expected_facts"].items() if got is None or got.get(k) != v}
    if B.cobol_field(data[:100], "cobol_runtime_version") != "none" or B.cobol_facts(b"MZ" + data[2:]) is not None:
        diff["truncated/impostor"] = True
    if ms > 1000:
        diff["ms"] = ms
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
