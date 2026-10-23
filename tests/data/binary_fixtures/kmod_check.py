"""Offline check: every kmod_*.{bin,json} fixture through lib.binary.kmod_fields / hcfg_scan.
usage (repo root): python3 tests/data/binary_fixtures/kmod_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("kmod_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    bf = B.kmod_fields(data)
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    want = f["expected_kmod_fields"]
    diff = {k: (bf.get(k) if bf else None, v) for k, v in want.items() if not bf or bf.get(k) != v} \
        if want != "none" else ({"kmod_fields": (bf, None)} if bf is not None else {})
    got_off = hit.offset if hit else "none"
    if got_off != f["expected_offset"]:
        diff["offset"] = (got_off, f["expected_offset"])
    if (hit.config if hit else "none") != f["expected_config"]:
        diff["config"] = (hit.config if hit else "none", f["expected_config"])
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: off={got_off} ({(time.time() - t) * 1e3:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
