"""vcls_mkjson.py DIR: write vcls_*.json (expected CWE = the bug class planted in vcls_gen.sh's source / the
reused npd_/pdiff_ twins' source; oracle evidence = vcls_oracle.py output)."""
import json, os, subprocess, sys
D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
CASES = {  # name: (file_a, file_b, cwe, name, planted source change)
    "divzero": (None, None, 369, "divide_by_zero", "C: n / d -> if (d == 0) return -1"),
    "intovf": (None, None, 190, "integer_overflow", "C: malloc(n * sz) -> __builtin_mul_overflow guard"),
    "cmdinj": (None, None, 78, "command_injection", "C: system(user) -> strpbrk(s, \";|&`$\") reject first"),
    "path": (None, None, 22, "path_traversal", "C: open(/srv/files/+s) -> strstr(s, \"..\") reject first"),
    "toctou": (None, None, 367, "toctou", "C: access() then open() -> open(O_NOFOLLOW)+fstat"),
    "dfree": (None, None, 415, "double_free", "C: conditional free(p) + free(p) -> one free"),
    "jdes": (None, None, 502, "unsafe_deserialization", "Java: readObject -> setObjectInputFilter first"),
    "jdiv": (None, None, 369, "divide_by_zero", "Java: total / parts -> if (parts == 0) return 0"),
    "jovf": (None, None, 190, "integer_overflow", "Java: n * w + 16 -> Math.addExact(Math.multiplyExact)"),
    "jobo": (None, None, 193, "off_by_one", "Java: i <= n -> i < n"),
    "jcmd": (None, None, 78, "command_injection", "Java: exec(\"ping \"+host) -> matches() + exec(String[])"),
    "jpath": (None, None, 22, "path_traversal", "Java: new File(base, name) -> getCanonicalPath().startsWith(base)"),
    "jsql": (None, None, 89, "sql_injection", "Java: createStatement/executeQuery(concat) -> prepareStatement+setString"),
    "npd_nullchk": ("npd_nullchk_a.bin", "npd_nullchk_b.bin", 476, "null_pointer_dereference", "C: gn->v -> if (!gn)"),
    "npd_uaf": ("npd_uaf_a.bin", "npd_uaf_b.bin", 416, "use_after_free", "C: free(gp); gp[0] -> gp = NULL after free"),
    "npd_fmt": ("npd_fmt_a.bin", "npd_fmt_b.bin", 134, "format_string", "C: printf(s) -> printf(\"%s\", s)"),
    "npd_signed": ("npd_signed_a.bin", "npd_signed_b.bin", 195, "signedness_error", "C: len > 64 -> (unsigned)len > 64"),
    "npd_offbyone": ("npd_offbyone_a.bin", "npd_offbyone_b.bin", 193, "off_by_one", "C: k <= i -> k < i"),
    "npd_bounds": ("npd_bounds_a.bin", "npd_bounds_b.bin", 787, "out_of_bounds_write", "C: buf[idx] = 1 -> idx >= sizeof buf guard"),
    "npd_strcpy": ("npd_strcpy_a.bin", "npd_strcpy_b.bin", 787, "out_of_bounds_write", "C: strcpy(d[24], s) -> strncpy"),
    "npd_go_bounds": ("npd_go_bounds_a.bin", "npd_go_bounds_b.bin", 125, "out_of_bounds_read", "Go: return buf[i] -> i range guard"),
    "pdiff_d24": ("pdiff_d24_a.bin", "pdiff_d24_b.bin", 476, "null_pointer_dereference", "Scala (GM D24 twin): nonEmpty(s)/charAt -> Option(s) guard"),
    "pdiff_bounds": ("pdiff_bounds_a.bin", "pdiff_bounds_b.bin", 125, "out_of_bounds_read", "Java: TABLE[i] -> i < 0 || i >= TABLE.length guard"),
}
for k, (fa, fb, n, name, why) in CASES.items():
    fa, fb = fa or f"vcls_{k}_a.bin", fb or f"vcls_{k}_b.bin"
    ev = subprocess.run([sys.executable, "-I", os.path.join(D, "vcls_oracle.py"), os.path.join(D, fa), os.path.join(D, fb)],
                        capture_output=True, text=True).stdout.strip()
    j = {"family": "patch_vuln_class", "encoding": "none", "expected_offset": None, "expected_config": None,
         "file_a": fa, "file_b": fb,
         "expected_facts": {"cwe": f"CWE-{n}", "cwe_number": str(n), "vulnerability_class": name},
         "generator_cmd": "bash vcls_gen.sh OUT   # gcc -fno-inline C twins / javac --release 11 + jar twins"
                          if fa.startswith("vcls_") else f"reused twin (see {fa.split('_')[0]}_gen.sh / json)",
         "oracle_cmd": f"python3 vcls_oracle.py {fa} {fb}   # objdump -d -M intel / javap -c -p added/removed: {ev}",
         "decoy": False,
         "note": f"lib.binary.patch_vuln_class_field(a, b, key). Expected = planted source change ({why}); CWE "
                 "spelling SPECULATIVE until a GM label is seen (D24 single solve = CWE-476)"}
    json.dump(j, open(os.path.join(D, f"vcls_{k}.json"), "w"), indent=1)
for k, fa, fb, exp, why in (
        ("decoy_text", "vcls_decoy_text_a.bin", "vcls_decoy_text_b.bin", {"cwe": None, "vulnerability_class": None},
         "A is a renamed text impostor (PK magic, not a zip): not comparable twins -> None"),
        ("decoy_same", "vcls_decoy_same_a.bin", "vcls_decoy_same_b.bin", {"cwe": "none", "vulnerability_class": "none"},
         "byte-identical ELF twins: nothing fixed -> none")):
    ev = subprocess.run([sys.executable, "-I", os.path.join(D, "vcls_oracle.py"), os.path.join(D, fa), os.path.join(D, fb)],
                        capture_output=True, text=True).stdout.strip()
    json.dump({"family": "patch_vuln_class", "encoding": "none", "expected_offset": None, "expected_config": None,
               "file_a": fa, "file_b": fb, "expected_facts": exp, "generator_cmd": "bash vcls_gen.sh OUT",
               "oracle_cmd": f"python3 vcls_oracle.py {fa} {fb}; cmp {fa} {fb}   # {ev}", "decoy": True, "note": why},
              open(os.path.join(D, f"vcls_{k}.json"), "w"), indent=1)
