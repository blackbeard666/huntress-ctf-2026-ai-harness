"""Offline check: every jvm_*.{bin,json} fixture through lib.binary.jvm_field (expected from javap -v -p, see
jvm_oracle.py). usage (repo root): python3 tests/data/binary_fixtures/jvm_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("jvm_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    exp = f["expected"]
    if exp.get("_all") == "none":   # not a jar/class at all: nothing answerable
        probe = ("methods", "access_flags", "method_count", "major_version", "main_class", "constant_pool_count")
        diff = {k: B.jvm_field(data, k) for k in probe if B.jvm_field(data, k) not in (None, "none")}
    else:
        got = {k: B.jvm_field(data, k, f.get("member"), f.get("question")) for k in exp}   # question names the class
        diff = {k: (got[k], v) for k, v in exp.items() if got[k] != v}
    ms = (time.time() - t) * 1e3
    bad += bool(diff) or ms > 1000
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {len(exp)} fields ({ms:.1f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
