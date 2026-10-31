"""toolchain-attribution-verdicts fixtures: expected = binutils readelf / file / strings one-liners (never lib.binary)."""
import json
import subprocess

GEN = ("sh ta_gen.sh  # gcc -g | clang-18 -g -no-pie | gcc -static -s | aarch64-linux-gnu-gcc -g -static | "
       "zig cc -target x86_64-linux-musl | gcc + strip -s -R .comment; ta_d27_{gcc,tcc}.elf = D27 GM members verbatim")
E = lambda *v: {"kind": "enum", "accepted_values": list(v)}
TEXT = {"kind": "exact_text", "syntax": "exact case-sensitive artifact-derived text only; no quotes or explanatory text"}
PRE = "In evidence.zip, Use the unique d27-- member whose basename ends {m}. "
Q = {
    "compiler": ("Attribute the build to the compiler that produced its code from the DW_AT_producer / .comment "
                 "banners, stabs and runtime fingerprints. Submit exactly one listed lowercase token.",
                 E("gcc", "clang", "tcc", "zig", "msvc", "mingw", "odin", "v")),
    "compiler_version": ("Report the compiler version (dotted numeric, e.g. 12.2.1) named by the first-CU "
                         "DW_AT_producer or the .comment compiler banner.", TEXT),
    "linker": ("Name the linker that produced the image (gold version note, Linker: banner, tcc self-link). "
               "Submit exactly one listed lowercase token.", E("bfd", "gold", "lld", "mold", "tcc", "link.exe")),
    "libc": ("Name the C library the image is built against (PT_INTERP / DT_NEEDED, or the static libc banner). "
             "Submit exactly one listed lowercase token.", E("glibc", "musl", "bionic", "msvcrt", "ucrt")),
    "linkage": ("Is the image statically or dynamically linked? Submit exactly one listed lowercase token.",
                E("static", "dynamic")),
    "pie": ("Evaluate this public predicate and submit lowercase true or false: true exactly when the image is a "
            "position-independent executable.", E("true", "false")),
    "dwarf_version": ("Report the DWARF version of the first .debug_info compile-unit header in base 10, or none "
                      "when the member has no DWARF.", TEXT),
}
O = {
    "compiler": "sh -c 'p=$(readelf --debug-dump=info {m} 2>/dev/null | grep -m1 DW_AT_producer); "
                "c=$(readelf -p .comment {m} 2>/dev/null); if strings -a {m} | grep -q zig_probe_stack; then "
                "echo zig; elif echo \"$p$c\" | grep -q \"clang version\"; then echo clang; elif echo \"$p$c\" | "
                "grep -qE \"GCC:|GNU C\"; then echo gcc; elif readelf -SW {m} | grep -q \"\\] \\.stab \"; then echo tcc; "
                "else echo none; fi'",
    "compiler_version": "sh -c 'p=$(readelf --debug-dump=info {m} 2>/dev/null | grep -m1 DW_AT_producer); "
                        "[ -n \"$p\" ] || p=$(readelf -p .comment {m} 2>/dev/null | grep -E \"clang version\" || "
                        "readelf -p .comment {m} 2>/dev/null | grep GCC:); "
                        "echo \"$p\" | grep -oE \"(GNU C[0-9+]* |clang version |\\) )[0-9]+\\.[0-9]+(\\.[0-9]+)?\" | "
                        "head -1 | grep -oE \"[0-9]+\\.[0-9]+(\\.[0-9]+)?$\" || echo none'",
    "linker": "sh -c 'if readelf -n {m} | grep -q \"gold\"; then echo gold; elif readelf -p .comment {m} 2>/dev/null "
              "| grep -q \"Linker: LLD\"; then echo lld; elif readelf -p .comment {m} 2>/dev/null | grep -q mold; "
              "then echo mold; elif readelf -p .comment {m} 2>/dev/null | grep -qE \"GCC:|clang\"; then echo bfd; "
              "elif readelf -SW {m} | grep -q \"\\] \\.stab \"; then echo tcc; else echo none; fi'",
    "libc": "sh -c 'l=$(readelf -lW {m} | grep -o \"interpreter: [^]]*\"); d=$(readelf -d {m} | grep NEEDED); "
            "case \"$l$d\" in *musl*) echo musl;; *ld-linux*|*libc.so.6*) echo glibc;; *system/bin/linker*) "
            "echo bionic;; *) if strings -a {m} | grep -qE \"GNU C Library|Fatal glibc error\"; then echo glibc; elif strings -a {m} "
            "| grep -qx __init_libc; then echo musl; else echo none; fi;; esac'",
    "linkage": "sh -c 'file -b {m} | grep -oE \"(static|dynamic)ally linked\" | grep -oE \"^(static|dynamic)\"'",
    "pie": "sh -c 'file -b {m} | grep -q \"pie executable\" && echo true || echo false'",
    "dwarf_version": "sh -c 'v=$(readelf --debug-dump=info {m} 2>/dev/null | grep -m1 \" Version:\" | awk \"{{print \\$2}}\"); "
                     "echo ${{v:-none}}'",
}


def oracle(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True).stdout.strip()


def write(member, field, decoy=False):
    q, af = Q[field]
    oc = O[field].format(m=member)
    v = oracle(oc)
    if v == "none" and af.get("kind") == "enum" and "none" not in af["accepted_values"]:
        v = None   # no evidence the enum can express -> the field must stay unanswered
    if field == "compiler_version" and v == "none":
        v = None
    d = {"kind": "generic_field", "member": member, "field": field,
         "question": (PRE + q).format(m=member.split("_", 1)[1]), "answer_format": af, "expected": v,
         "generator_cmd": GEN, "oracle_cmd": oc}
    if decoy:
        d["decoy"] = True
    open(f"{member}.{field}.json", "w").write(json.dumps(d, indent=1) + "\n")
    print(member, field, v)


for m, fields in (("ta_gcc_g.elf", ("compiler", "compiler_version", "linker", "libc", "pie", "dwarf_version")),
                  ("ta_clang18_g.elf", ("compiler", "compiler_version", "pie", "linkage")),
                  ("ta_gcc_static_s.elf", ("linkage", "libc", "compiler_version", "dwarf_version")),
                  ("ta_a64_static_g.elf", ("compiler", "libc", "linkage")),
                  ("ta_zig_musl.elf", ("compiler", "linker", "libc")),
                  ("ta_d27_gcc.elf", ("compiler", "compiler_version", "libc", "linkage")),
                  ("ta_d27_tcc.elf", ("compiler", "linker", "libc", "dwarf_version"))):
    for f in fields:
        write(m, f)
for f in ("compiler", "compiler_version", "linker"):   # decoy: no banner, no DWARF -> unanswerable
    write("ta_nobanner.elf", f, decoy=True)
# decoy: random bytes (not an ELF) -> None
q, af = Q["compiler"]
d = {"kind": "generic_field", "member": "gf_decoy_random.bin", "field": "compiler", "question": (PRE + q).format(m="gcc.elf"),
     "answer_format": af, "expected": None, "decoy": True,
     "generator_cmd": "existing gf_decoy_random.bin (head -c random bytes, see gen_generic.sh)",
     "oracle_cmd": "file gf_decoy_random.bin  # data, not ELF -> field cannot be answered"}
open("gf_decoy_random.bin.compiler.json", "w").write(json.dumps(d, indent=1) + "\n")
