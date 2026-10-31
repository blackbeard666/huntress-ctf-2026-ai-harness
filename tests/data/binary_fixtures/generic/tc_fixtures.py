"""theme-backfill-d18-d28-fields fixtures: expected = the binutils `readelf` one-liner in oracle_cmd (never lib.binary)."""
import json
import subprocess

ENUM_DBG = {"kind": "enum", "accepted_values": ["dwarf", "stabs", "none"]}
ENUM_HASH = {"kind": "enum", "accepted_values": ["gnu", "sysv", "both", "none"]}
TEXT = {"kind": "exact_text", "syntax": "exact case-sensitive artifact-derived text only; no quotes or explanatory text"}
GEN = "sh tc_gen.sh  # gcc -g -Wl,--hash-style=gnu | gcc -S + as --gstabs + gcc -Wl,--hash-style=sysv | gcc -Wl,--hash-style=both"
PRE = "In evidence.zip, Use the unique d27-- member whose basename ends {role}.elf. "
Q_DBG = PRE + ("Classify the debug-information format the build carries: dwarf when a .debug_info section is present, "
               "stabs when a .stab section is present, none when neither. Submit exactly one listed lowercase token.")
Q_HASH = PRE + ("Read the dynamic section and classify the symbol hash table style: gnu when only DT_GNU_HASH is "
                "present, sysv when only DT_HASH is present, both when both are, none when neither.")
Q_PROD = PRE + ("Report the DW_AT_producer string of the first DWARF compile unit exactly as stored, or none when the "
                "member has no DWARF.")
OR_DBG = ("sh -c 'd=$(readelf -SW {m} | grep -c \"\\] \\.debug_info \"); s=$(readelf -SW {m} | grep -c \"\\] \\.stab \"); "
          "[ $d -gt 0 ] && echo dwarf || {{ [ $s -gt 0 ] && echo stabs || echo none; }}'")
OR_HASH = ("sh -c 't=$(readelf -d {m} | grep -oE \"\\((GNU_)?HASH\\)\" | sort | tr -d \"\\n\"); case $t in "
           "\"(GNU_HASH)(HASH)\") echo both;; \"(GNU_HASH)\") echo gnu;; \"(HASH)\") echo sysv;; *) echo none;; esac'")
OR_PROD = ("sh -c 'p=$(readelf --debug-dump=info {m} 2>/dev/null | grep -m1 DW_AT_producer | "
           "sed -E \"s/^.*DW_AT_producer[ ]*: (\\(indirect[^)]*\\): )?//\"); echo \"${{p:-none}}\"'")


def oracle(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True).stdout.rstrip("\n")


def write(member, field, q, af, ocmd, role, decoy=False, expected=None):
    oc = ocmd.format(m=member)
    d = {"kind": "generic_field", "member": member, "field": field, "question": q.format(role=role),
         "answer_format": af, "expected": expected if decoy else oracle(oc), "generator_cmd": GEN, "oracle_cmd": oc}
    if decoy:
        d["decoy"] = True
    open(f"{member}.{field}.json", "w").write(json.dumps(d, indent=1) + "\n")
    print(member, field, d["expected"])


for m, role in (("gf_tc_gcc.elf", "gcc"), ("gf_tc_stabs.elf", "tcc"), ("gf_tc_both.elf", "cc")):
    write(m, "debug_format", Q_DBG, ENUM_DBG, OR_DBG, role)
    write(m, "hash_style", Q_HASH, ENUM_HASH, OR_HASH, role)
for m, role in (("gf_tc_gcc.elf", "gcc"), ("gf_tc_stabs.elf", "tcc")):
    write(m, "dwarf_producer", Q_PROD, TEXT, OR_PROD, role)
# decoy: random bytes named like a role member (not an ELF) -> must stay None
d = {"kind": "generic_field", "member": "gf_decoy_random.bin", "field": "debug_format", "question": Q_DBG.format(role="gcc"),
     "answer_format": ENUM_DBG, "expected": None, "decoy": True,
     "generator_cmd": "existing gf_decoy_random.bin (head -c random bytes, see gen_generic.sh)",
     "oracle_cmd": "file gf_decoy_random.bin  # data, not ELF -> field cannot be answered"}
open("gf_decoy_random.bin.debug_format.json", "w").write(json.dumps(d, indent=1) + "\n")
d.update(field="hash_style", question=Q_HASH.format(role="gcc"), answer_format=ENUM_HASH)
open("gf_decoy_random.bin.hash_style.json", "w").write(json.dumps(d, indent=1) + "\n")
