"""vcls_check.py [DIR]: run lib.binary.patch_vuln_class_field over every vcls_*.json and report mismatches."""
import glob, json, os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from lib.binary import patch_vuln_class_field
D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
bad = 0
for jp in sorted(glob.glob(f"{D}/vcls_*.json")):
    j = json.load(open(jp))
    a, b = (open(f"{D}/{j[k]}", "rb").read() for k in ("file_a", "file_b"))
    t = time.time()
    for k, v in j["expected_facts"].items():
        got = patch_vuln_class_field(a, b, k)
        if got != v:
            bad += 1
            print("MISMATCH", os.path.basename(jp), k, "expected", v, "got", got)
    print(f"{os.path.basename(jp)}: {(time.time() - t) * 1e3:.0f} ms")
print("mismatches:", bad)
sys.exit(bool(bad))
