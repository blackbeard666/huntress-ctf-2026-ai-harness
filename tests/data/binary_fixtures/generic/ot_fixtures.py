"""optimization-equivalence-facts fixtures: expected = the binutils readelf / objcopy / sha256sum one-liner in
oracle_cmd (never lib.binary). Pair facts (diff_byte_count, first_diff_offset, semantically_equivalent) need a group,
which the fixture replay does not pass: ot_pair_check.sh checks them against cmp -l."""
import json
import subprocess

INT = {"kind": "integer", "syntax": "base-10 integer with no units, separators, whitespace, or explanatory text"}
HEX64 = {"kind": "pattern", "syntax": "exactly 64 lowercase hexadecimal characters; no prefix, whitespace, or explanatory text"}
ENUM_O = {"kind": "enum", "accepted_values": ["O0", "O1", "O2", "O3", "Os"]}
GEN = "sh ot_gen.sh  # gcc -O0 -g / gcc -O3 -g of ot_twin.c; d29--sample-O0/O3.elf copied from the D29 GM evidence"
PRE = "In evidence.zip, Use the unique {day}-- member whose basename ends {tag}.elf. "
Q = {
    "function_count": "Count the STT_FUNC entries of its SHT_SYMTAB symbol table that are defined (st_shndx is not "
                      "SHN_UNDEF). A stripped member has none. Submit the count in base 10.",
    "text_size": "Read the section header of the .text section and submit its sh_size in base 10.",
    "rodata_size": "Read the section header of the .rodata section and submit its sh_size in base 10.",
    "text_sha256": "Compute SHA-256 over the exact file bytes of the .text section (sh_offset, sh_size).",
    "opt_level": "Report the compiler optimization level this role member was built with, as one listed token.",
}
AF = {"function_count": INT, "text_size": INT, "rodata_size": INT, "text_sha256": HEX64, "opt_level": ENUM_O}
OR = {
    "function_count": "readelf -sW {m} | awk '/Symbol table .\\.symtab/{{s=1}} s && $4==\"FUNC\" && $7!=\"UND\"' | wc -l",
    "text_size": "printf '%d\\n' 0x$(readelf -SW {m} | awk '$2==\".text\"{{print $6}}')",
    "rodata_size": "printf '%d\\n' 0x$(readelf -SW {m} | awk '$2==\".rodata\"{{print $6}}')",
    "text_sha256": "objcopy -O binary --only-section=.text {m} /dev/stdout | sha256sum | cut -c1-64",
    "opt_level": "readelf --debug-dump=info {m} | grep -m1 DW_AT_producer | grep -oE ' -O[0-3s]' | tail -1 | tr -d ' -'",
}
OR_NAME = "echo {m} | grep -oE 'O[0-3s]\\.elf$' | cut -c1-2  # no DWARF: the GM role tag in the basename"


def oracle(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True).stdout.strip()


def write(member, field, day, tag, ocmd=None, decoy=False):
    oc = (ocmd or OR[field]).format(m=member)
    d = {"kind": "generic_field", "member": member, "field": field, "question": PRE.format(day=day, tag=tag) + Q[field],
         "answer_format": AF[field], "expected": None if decoy else oracle(oc), "generator_cmd": GEN, "oracle_cmd": oc}
    if decoy:
        d["decoy"] = True
    open(f"{member}.{field}.json", "w").write(json.dumps(d, indent=1) + "\n")
    print(member, field, d["expected"])


for m, tag in (("gf_ot_twin-O0.elf", "O0"), ("gf_ot_twin-O3.elf", "O3"), ("d29--sample-O0.elf", "O0"),
               ("d29--sample-O3.elf", "O3")):
    day = "d29" if m.startswith("d29") else "d31"
    for f in ("function_count", "text_size", "rodata_size", "text_sha256"):
        write(m, f, day, tag)
    write(m, "opt_level", day, tag, None if m.startswith("gf_") else OR_NAME)
# decoys: random bytes (not an ELF) -> None
for f in ("function_count", "text_size", "opt_level"):
    d = {"kind": "generic_field", "member": "gf_decoy_random.bin", "field": f, "question": PRE.format(day="d29", tag="O3")
         + Q[f], "answer_format": AF[f], "expected": None, "decoy": True,
         "generator_cmd": "existing gf_decoy_random.bin (head -c random bytes, see gen_generic.sh)",
         "oracle_cmd": "file gf_decoy_random.bin  # data, not ELF -> field cannot be answered"}
    open(f"gf_decoy_random.bin.{f}.json", "w").write(json.dumps(d, indent=1) + "\n")
