"""Offline check: every groovy_*.{bin,json} fixture through lib.binary.groovy_facts + jvm_field (question routes the
unit's primary class) + hcfg_find on the hcfg_class bytes (expected from groovy_oracle.py: javap -v -p text).
usage (repo root): python3 tests/data/binary_fixtures/groovy_check.py"""
import io, json, pathlib, sys, time, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("groovy_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    q = f["question"]
    t = time.time()
    g = B.groovy_facts(data, q) or {}
    got = {k: g[k] if k in g else B.jvm_field(data, k, question=q) for k in f["expected"]}
    via = {k: B.jvm_field(data, k, question=q) for k in ("closures", "hcfg_class", "groovy_kind")}
    diff = {k: (got[k], v) for k, v in f["expected"].items() if got[k] != v}
    diff.update({"jvm_field:" + k: (v, f["expected"][k]) for k, v in via.items() if v != f["expected"][k]})
    hc = f["expected"].get("hcfg_class", "none")
    if hc != "none":
        h = B.hcfg_find(zipfile.ZipFile(io.BytesIO(data)).read(hc + ".class"))
        if not h or h.config != f["expected_config"]:
            diff["hcfg_config"] = (h and h.config, f["expected_config"])
    ms = (time.time() - t) * 1e3
    bad += bool(diff) or ms > 1000
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: {len(got)} fields ({ms:.1f} ms) {diff or ''}")
for junk in (b"", b"PK\x03\x04trunc", b"\xca\xfe\xba\xbe\x00\x00\x00\x34", b"MZ" + b"\0" * 64):
    if B.groovy_facts(junk) is not None:
        bad += 1
        print("BAD junk", junk)
sys.exit(1 if bad else 0)
