"""stw_check.py [FIXTURE_DIR]: run lib.binary.stripped_twin_field over every stw_*.json and report mismatches."""
import glob, json, os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from lib.binary import stripped_twin_match, stripped_twin_field, hcfg_scan
D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
rd = lambda n: open(f"{D}/{n}", "rb").read() if n else None
bad = 0
for jp in sorted(glob.glob(f"{D}/stw_*.json")):
    j = json.load(open(jp))
    a, b, s = rd(j["file_a"]), rd(j["file_b"]), rd(j.get("file_sym"))
    t = time.time()
    for k, v in j["expected_facts"].items():
        got = stripped_twin_match(a, b, s) if k == "stripped_twin_match" else stripped_twin_field(a, b, k, s)
        if got != v:
            bad += 1
            print("MISMATCH", os.path.basename(jp), k, "expected", v, "got", got)
    if any(h.valid for h in hcfg_scan(a)):
        bad += 1
        print("UNEXPECTED hcfg", os.path.basename(jp))
    print(f"{os.path.basename(jp)}: {(time.time() - t) * 1e3:.0f} ms")
print("mismatches:", bad)
sys.exit(bool(bad))
