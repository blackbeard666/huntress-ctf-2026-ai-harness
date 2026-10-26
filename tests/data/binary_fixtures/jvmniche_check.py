"""Offline check: every jvmniche_*.{bin,json} fixture through lib.binary.jvm_niche_facts (+ jvm_field merge and
hcfg_find on the niche_hcfg_classfile bytes); expected from jvmniche_oracle.py (javap -v -p text).
usage (repo root): python3 tests/data/binary_fixtures/jvmniche_check.py"""
import io, json, pathlib, sys, time, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("jvmniche_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    q = f["question"]
    t = time.time()
    g = B.jvm_niche_facts(data, q)
    if f["expected"] is None:
        diff = {} if g is None and B.jvm_field(data, "niche_language", question=q) is None else {"not None": g}
    else:
        diff = {k: (g.get(k), v) for k, v in f["expected"].items() if g.get(k) != v}
        lang = B.jvm_field(data, "jvm_language", question=q)
        want = f["expected"]["niche_language"]
        if want != "none" and lang not in (want, "kotlin"):
            diff["jvm_field:jvm_language"] = (lang, want)
        if want == "none" and B.jvm_field(data, "jvm_language", question=q) != "java":
            diff["jvm_field:jvm_language"] = (lang, "java")
        hc = f["expected"]["niche_hcfg_classfile"]
        if hc != "none":
            cls = data if data[:4] == b"\xca\xfe\xba\xbe" else zipfile.ZipFile(io.BytesIO(data)).read(hc)
            h = B.hcfg_find(cls)
            if not h or h.config != f["expected_config"]:
                diff["hcfg_config"] = (h and h.config, f["expected_config"])
            if B.jvm_field(data, "hcfg_config", question=q) in (None, "none"):
                diff["jvm_field:hcfg_config"] = "none"
    ms = (time.time() - t) * 1e3
    bad += bool(diff) or ms > 1000
    print(("ok  " if not diff else "BAD ") + f"{fj.stem}: ({ms:.1f} ms) {diff or ''}")
for junk in (b"", b"PK\x03\x04trunc", b"\xca\xfe\xba\xbe\x00\x00\x00\x34", b"MZ" + b"\0" * 64):
    if B.jvm_niche_facts(junk) is not None:
        bad += 1
        print("BAD junk", junk)
sys.exit(1 if bad else 0)
