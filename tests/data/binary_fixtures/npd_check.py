"""npd_check.py FIXTURE_DIR: run lib.binary.native_patch_diff_field over every npd_*.json and report mismatches."""
import glob, json, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from lib.binary import native_patch_diff, native_patch_diff_field
D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
bad = 0
for jp in sorted(glob.glob(f"{D}/npd_*.json")):
    j = json.load(open(jp))
    a, b = (open(f"{D}/{j[k]}", "rb").read() for k in ("file_a", "file_b"))
    for k, v in j["expected_facts"].items():
        got = native_patch_diff(a, b) if k == "native_patch_diff" else native_patch_diff_field(a, b, k)
        if got != v:
            bad += 1
            print("MISMATCH", os.path.basename(jp), k, "expected", v, "got", got)
print("mismatches:", bad)
sys.exit(bool(bad))
