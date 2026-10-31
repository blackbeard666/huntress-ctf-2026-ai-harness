"""Writes the fuzzy-hash-fields generic fixtures. Run with a python that has py-tlsh, pefile and telfhash (throwaway
venv: pip install py-tlsh pefile pyelftools telfhash); ssdeep values come from libfuzzy 2.14.1 (tools/ssdeep/ssdeep.sh,
Ubuntu ssdeep + libfuzzy2 debs). Never imports lib.binary."""
import json, pathlib, subprocess, sys, zipfile

D = pathlib.Path(__file__).resolve().parent
SS = str(D.parents[3] / "tools/ssdeep/ssdeep.sh")
STR = {"kind": "string"}
INT = {"kind": "integer"}


def ssdeep(member):
    out = subprocess.run([SS, "-s", "-b", str(D / member)], capture_output=True, text=True, check=True).stdout
    return out.splitlines()[1].rsplit(",", 1)[0]


def tlsh_(member):
    import tlsh
    return tlsh.hash((D / member).read_bytes())


def imphash(member):
    import pefile
    return pefile.PE(str(D / member)).get_imphash()


def telf(member):
    import telfhash
    return telfhash.telfhash(str(D / member))[0]["telfhash"]


def pair_ssdeep(member):
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        zipfile.ZipFile(D / member).extractall(t)
        out = subprocess.run([SS, "-s", "-b", "-a", "-d", "fh-family-a.elf", "fh-family-b.elf"], cwd=t,
                             capture_output=True, text=True, check=True).stdout
    return out.strip().rsplit("(", 1)[1].rstrip(")")


def pair_tlsh(member):
    import tlsh
    z = zipfile.ZipFile(D / member)
    return str(tlsh.diff(*(tlsh.hash(z.read(n)) for n in ("fh-family-a.elf", "fh-family-b.elf"))))


O_SS = "tools/ssdeep/ssdeep.sh -s -b {m}  # libfuzzy 2.14.1"
O_TL = "python3 -c 'import tlsh,sys;print(tlsh.hash(open(sys.argv[1],\"rb\").read()))' {m}  # py-tlsh"
O_IMP = "python3 -c 'import pefile,sys;print(pefile.PE(sys.argv[1]).get_imphash())' {m}"
O_TELF = "python3 -c 'import telfhash,sys;print(telfhash.telfhash(sys.argv[1])[0][\"telfhash\"])' {m}  # telfhash 0.9.8"
GEN = "existing member (gen_generic.sh)"
GEN_PAIR = ("gcc -O0 fh_src/fam.c -o fh-family-a.elf; gcc -O0 -DTAG='\"bravo-variant\"' fh_src/fam.c -o fh-family-b.elf;"
            " zip -X fh_pair.zip fh-family-a.elf fh-family-b.elf  (gen_generic.sh)")
# (member, field, question, answer_format, oracle fn | None (= expected null), oracle_cmd, decoy note)
CASES = [
    ("gf_c_imports.bin", "ssdeep", "What is the ssdeep (CTPH) fuzzy hash of the sample?", STR, ssdeep, O_SS, None),
    ("gf_pe_imports.exe", "ssdeep", "Submit the ssdeep hash of the executable.", STR, ssdeep, O_SS, None),
    ("d29--sample-O3.elf", "ssdeep", "What is the ssdeep hash of the .text section?", STR, None, O_SS,
     "region (section) digest, not the member bytes -> must stay None"),
    ("gf_pe_exports.dll", "tlsh", "What is the TLSH digest of the sample?", STR, tlsh_, O_TL, None),
    ("d29--sample-O3.elf", "tlsh", "Submit the TLSH (T1) hash of the binary.", STR, tlsh_, O_TL, None),
    ("gf_pe_imports.exe", "imphash", "What is the imphash of the PE?", STR, imphash, O_IMP, None),
    ("gf_pe_exports.dll", "imphash", "What is the PE import hash (imphash)?", STR, imphash, O_IMP, None),
    ("gf_c_imports.bin", "imphash", "What is the imphash of the sample?", STR, None, O_IMP,
     "ELF, not PE: imphash undefined -> None"),
    ("rtm_d27_v_gcc.elf", "telfhash", "What is the telfhash of the ELF?", STR, telf, O_TELF, None),
    ("d29--sample-O3.elf", "telfhash", "Submit the telfhash of the sample.", STR, telf, O_TELF, None),
    ("gf_pe_imports.exe", "telfhash", "What is the telfhash of the sample?", STR, None, O_TELF,
     "PE, not ELF -> None"),
    ("gf_c_imports.bin", "telfhash", "What is the telfhash of the sample?", STR, None, O_TELF,
     "reference prints tnull (too few symbols): left to the worker -> None"),
    ("fh_pair.zip", "family_a_family_b_ssdeep_score",
     "What is the ssdeep match score (0-100) between family-a and family-b?", INT, pair_ssdeep,
     "unzip fh_pair.zip; tools/ssdeep/ssdeep.sh -s -b -a -d fh-family-a.elf fh-family-b.elf", None),
    ("fh_pair.zip", "family_a_family_b_tlsh_distance",
     "What is the TLSH distance between family-a and family-b?", INT, pair_tlsh,
     "python3 -c 'import tlsh,zipfile;z=zipfile.ZipFile(\"fh_pair.zip\");print(tlsh.diff(*(tlsh.hash(z.read(n)) for n in "
     "(\"fh-family-a.elf\",\"fh-family-b.elf\"))))'", None),
    ("gf_decoy_random.bin", "family_a_family_b_ssdeep_score",
     "What is the ssdeep match score (0-100) between family-a and family-b?", INT, None, "file gf_decoy_random.bin  # data",
     "random bytes, no family-a/family-b members -> None"),
]

for member, field, q, af, fn, ocmd, decoy in CASES:
    d = {"kind": "generic_field", "member": member, "field": field, "question": q, "answer_format": af,
         "expected": fn(member) if fn else None,
         "generator_cmd": GEN_PAIR if member == "fh_pair.zip" else GEN, "oracle_cmd": ocmd.format(m=member)}
    if decoy:
        d["decoy"] = True
        d["note"] = decoy
    (D / f"{member}.{field}.json").write_text(json.dumps(d, indent=1) + "\n")
    print(member, field, d["expected"], file=sys.stderr)
