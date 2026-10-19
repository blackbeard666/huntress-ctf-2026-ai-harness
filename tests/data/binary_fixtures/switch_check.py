"""Offline check: every switch_*.{bin,json} fixture through lib.binary.switch_field / switch_tables (+ hcfg_scan stays empty).
usage (repo root): python3 tests/data/binary_fixtures/switch_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("switch_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    r = B.switch_tables(data)
    ms = (time.time() - t) * 1e3
    exp = f["expected_facts"]
    if exp is None:
        got = r
    else:
        got = json.loads(json.dumps({k: B.switch_field(data, k) for k in exp}))
    kind = "none" if not r or not r["switches"] else (r["switches"][0]["kind"] if r["switches"][0]["kind"] == "select_string"
                                                      else min(r["switches"], key=lambda s: (s["function"].startswith(("_", "none")), int(s["dispatch"], 16)))["kind"])
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ok = got == exp and kind == f["expected_kind"] and (hit is None or f.get("has_hcfg")) and ms < 1000
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms kind={kind}")
    if got != exp:
        for k in (exp or {}):
            if got.get(k) != exp[k]:
                print(f"     {k}: got {got.get(k)!r}\n     {' ' * len(k)}  want {exp[k]!r}")
        if exp is None:
            print(f"     got {got!r} want None")
sys.exit(1 if bad else 0)
