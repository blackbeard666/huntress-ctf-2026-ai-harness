"""Offline check: every cljns_*.{bin,json} fixture through lib.binary.clojure_facts (expected from javap text, see
cljns_oracle.py). usage (repo root): python3 tests/data/binary_fixtures/cljns_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("cljns_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    got = B.clojure_facts(data) or {}
    jv = {k: B.jvm_field(data, k) for k in ("namespace", "vars", "fn_classes")}   # merged into jar_jvm_facts
    ms = (time.time() - t) * 1e3
    diff = {k: (got.get(k), v) for k, v in f["expected"].items() if got.get(k) != v}
    diff.update({k: (v, f["expected"][k]) for k, v in jv.items() if v != f["expected"][k]})
    bad += bool(diff) or ms > 1000
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {len(f['expected'])} fields ({ms:.1f} ms) {diff or ''}")
for junk in (b"", b"PK\x03\x04trunc", b"\xca\xfe\xba\xbe\x00\x00\x00\x34"):
    if B.clojure_facts(junk) is not None:
        bad += 1
        print("BAD junk", junk)
sys.exit(1 if bad else 0)
