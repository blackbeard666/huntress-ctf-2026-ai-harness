"""Offline check: every mpd_*.json (.NET twin IL patch diff) through lib.binary.dotnet_patch_diff_field.
usage (repo root): python3 tests/data/binary_fixtures/mpd_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("mpd_*.json")):
    f = json.loads(fj.read_text())
    a, b = (fj.parent / f["dll_a"]).read_bytes(), (fj.parent / f["dll_b"]).read_bytes()
    t = time.time()
    got = {k: B.dotnet_patch_diff_field(a, b, k) for k in f["expected_facts"]}
    ms = (time.time() - t) * 1e3
    ok = got == f["expected_facts"]
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms")
    for k in f["expected_facts"]:
        if got[k] != f["expected_facts"][k]:
            print(f"     {k}: got {got[k]!r}\n     {' ' * len(k)}  want {f['expected_facts'][k]!r}")
sys.exit(1 if bad else 0)
