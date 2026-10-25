"""npd_mkjson.py DIR: fixture json from npd_oracle.py (objdump/nm) output; fix_kind from the source change in npd_gen.sh."""
import json, re, subprocess, sys
from collections import Counter
D = sys.argv[1]
KIND = {"offbyone": "off_by_one", "bounds": "bounds_check", "strcpy": "replaced_unsafe_call",
        "signed": "signedness", "fmt": "format_string", "uaf": "null_after_free",
        "sprintf": "replaced_unsafe_call", "nullchk": "null_check", "strip": "replaced_unsafe_call", "go_bounds": "bounds_check"}
SIGNED = {"jl", "jle", "jg", "jge"}
def facts(p):
    a, b = f"{D}/npd_{p}_a.bin", f"{D}/npd_{p}_b.bin"
    args = [a, b] + ([f"{D}/npd_{p}_a_unstripped.tmp", f"{D}/npd_{p}_b_unstripped.tmp"] if p == "strip" else [])
    o = json.loads(subprocess.run(["python3", f"{D}/npd_oracle.py", *args], capture_output=True, text=True).stdout)
    ch = o["changed_functions"]
    names = [("sub_" + o["addr_a"][n][2:]) if p == "strip" else n for n in ch]
    ex = {"changed_functions": json.dumps(names, separators=(",", ":")), "changed_function_count": str(len(ch))}
    if not ch:
        ex["fix_kind"] = "none"
        return ex, ""
    n = ch[0]; r = o[n]
    ex.update({"changed_function": names[0], "changed_function_address": o["addr_a"][n],
               "changed_function_address_b": o["addr_b"][n], "fix_kind": KIND[p]})
    rem = [c for c in dict.fromkeys(r["calls_a"]) if c not in r["calls_b"]]
    add = [c for c in dict.fromkeys(r["calls_b"]) if c not in r["calls_a"]]
    if rem and add:
        ex["replaced_call"] = f"{rem[0]}->{add[0]}"
    fr = lambda xs: str(int(re.search(r"\$(0x[0-9a-f]+)", xs[0]).group(1), 16)) if xs else "none"
    ex["frame_size_a"], ex["frame_size_b"] = fr(r["frame_a"]), fr(r["frame_b"])
    ja, jb = Counter(r["jcc_a"]), Counter(r["jcc_b"])
    gone, new = list((ja - jb).elements()), list((jb - ja).elements())
    if len(gone) == len(new) == 1:
        ex["comparison_flip"] = f"{gone[0]}->{new[0]}"
    return ex, json.dumps({k: v for k, v in r.items() if k.startswith(("calls", "jcc", "frame"))})
for p in [*KIND, "decoy_same", "decoy_text"]:
    if p == "decoy_text":
        ex, ev = {"native_patch_diff": None}, "file(1): ASCII text -> not ELF; objdump: file format not recognized"
    else:
        ex, ev = facts(p)
    j = {"family": "native_patch_diff", "encoding": "none", "expected_offset": None, "expected_config": None,
         "file_a": f"npd_{p}_a.bin", "file_b": f"npd_{p}_b.bin", "expected_facts": ex,
         "generator_cmd": "bash npd_gen.sh OUT   # gcc (-O0/-O2, -fno-inline, FORTIFY off) vuln/fixed C twins" +
                          ("; strip -s both after copying unstripped" if p == "strip" else ""),
         "oracle_cmd": f"python3 npd_oracle.py npd_{p}_a.bin npd_{p}_b.bin" +
                       (" <unstripped a> <unstripped b>" if p == "strip" else "") +
                       "   # binutils objdump -d (AT&T) + nm, masked per-function text compare; oracle: " + ev,
         "decoy": p.startswith("decoy"),
         "note": "lib.binary.native_patch_diff_field(a, b, key). fix_kind from the source change by construction "
                 "(vocabulary SPECULATIVE until a GM label is seen); instruction_count_* not asserted "
                 "(objdump counts alignment nops, the lib drops them)" +
                 ("; decoy: expect None (not x86 ELF twins)" if p == "decoy_text" else "") +
                 ("; decoy: identical twins -> changed_functions [] / fix_kind none" if p == "decoy_same" else "")}
    json.dump(j, open(f"{D}/npd_{p}.json", "w"), indent=1)
    print(p, ex)
