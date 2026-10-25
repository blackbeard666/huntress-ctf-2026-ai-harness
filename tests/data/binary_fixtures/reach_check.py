"""Offline check: every reach_*.{bin,json} fixture through lib.binary.reachability_field (+ hcfg_scan stays empty).
usage (repo root): python3 tests/data/binary_fixtures/reach_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("reach_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    want = f["expected_facts"]
    if want is None:
        got, ok = B.reachability_facts(data, f["target_fn"]), None
        ok = got is None
    else:
        got = {k: B.reachability_field(data, k, f["target_fn"]) for k in want}
        exp = {k: json.dumps(v, separators=(",", ":")) if isinstance(v, (list, dict)) else v for k, v in want.items()}
        ok = got == exp
    ms = (time.time() - t) * 1e3
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    if not ok:
        print(f"     got {got!r}\n     want {want!r}")
sys.exit(1 if bad else 0)
