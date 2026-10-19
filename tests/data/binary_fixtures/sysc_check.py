"""Offline check: every sysc_*.{bin,json} fixture through lib.binary.syscall_field (+ api_intent_field verdicts,
hcfg_scan stays empty). usage (repo root): python3 tests/data/binary_fixtures/sysc_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("sysc_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = {k: B.syscall_field(data, k) for k in f["expected_facts"]}
    want = dict(f["expected_facts"])
    if f.get("expected_api_intent"):
        got.update({"api:" + k: B.api_intent_field(data, k) for k in f["expected_api_intent"]})
        want.update({"api:" + k: v for k, v in f["expected_api_intent"].items()})
    ms = (time.time() - t) * 1e3
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ok = got == want and hit is None
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms" + ("" if hit is None else f" unexpected hcfg {hit}"))
    for k in want:
        if got[k] != want[k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {want[k]!r}")
sys.exit(1 if bad else 0)
