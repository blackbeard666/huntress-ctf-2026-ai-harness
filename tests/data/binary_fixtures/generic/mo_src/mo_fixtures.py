"""gf-macho fixtures: expected = the oracle_cmd's stdout (llvm-otool-18 / llvm-nm-18 / macholib), never lib.binary."""
import json, subprocess, sys
D = sys.argv[1]
INT = {"kind": "integer", "syntax": "base-10 integer with no units, separators, whitespace, or explanatory text"}
TF = {"kind": "enum", "accepted_values": ["true", "false"]}
GEN = "sh mo_src/mo_gen.sh (zig cc -target x86_64-macos / aarch64-macos [-g] [-c], llvm-lipo-18 -create)"
MOSYM = ("python3 -c \"from macholib.MachO import MachO; from macholib.SymbolTable import SymbolTable; "
         "m=MachO('{m}'); h=m.headers[{i}]; print(sum(1 for n,s in SymbolTable(m,h).nlists if {c}))\"")
SEGQ = "Count the Mach-O LC_SEGMENT_64 load commands{x}. Submit the count in base 10."
F = [
    ("mo_x64.bin", "segment_count", SEGQ.format(x=""), INT, "llvm-otool-18 -l mo_x64.bin | grep -c 'cmd LC_SEGMENT'"),
    ("mo_obj.o", "segment_count", SEGQ.format(x=" of the object file"), INT,
     "llvm-otool-18 -l mo_obj.o | grep -c 'cmd LC_SEGMENT'"),
    ("mo_plain.bin", "segment_count", SEGQ.format(x=", excluding __PAGEZERO"), INT,
     "llvm-otool-18 -l mo_plain.bin | grep -A2 'cmd LC_SEGMENT' | grep segname | grep -vc __PAGEZERO"),
    ("mo_fat.bin", "load_command_count", "Use the arm64 slice of the universal binary. Submit its Mach-O header ncmds "
     "in base 10.", INT, "llvm-objdump-18 --macho --arch=arm64 --private-header mo_fat.bin | tail -1 | awk '{print $6}'"),
    ("mo_x64.bin", "load_command_count", "Submit the Mach-O header ncmds in base 10.", INT,
     "llvm-otool-18 -h mo_x64.bin | tail -1 | awk '{print $6}'"),
    ("mo_fat.bin", "section_count", "Sum nsects over every LC_SEGMENT_64 of the arm64 slice. Submit the count in base 10.",
     INT, "llvm-objdump-18 --macho --arch=arm64 --private-headers mo_fat.bin | awk '/nsects/{s+=$2}END{print s}'"),
    ("mo_fat.bin", "x86_64_section_count", "Count the sections of the x86_64 slice. Submit the count in base 10.",
     INT, "llvm-objdump-18 --macho --arch=x86_64 --private-headers mo_fat.bin | awk '/nsects/{s+=$2}END{print s}'"),
    ("mo_fat.bin", "section_count", "Sum nsects across all slices of the fat binary. Submit the count in base 10.",
     INT, "llvm-objdump-18 --macho --arch=all --private-headers mo_fat.bin | awk '/nsects/{s+=$2}END{print s}'"),
    ("mo_arm64_g.bin", "text_section_count", "Count the sections whose segname is __TEXT. Submit the count in base 10.",
     INT, "llvm-otool-18 -l mo_arm64_g.bin | grep -A1 '^  sectname' | grep -c 'segname __TEXT$'"),
    ("mo_obj.o", "data_section_count", "Count the sections in the __DATA segment. Submit the count in base 10.",
     INT, "llvm-otool-18 -l mo_obj.o | grep -A1 '^  sectname' | grep -c 'segname __DATA$'"),
    ("mo_arm64_g.bin", "symbol_count", "Count the LC_SYMTAB nlist entries whose name is nonempty, N_STAB entries "
     "included. Submit the count in base 10.", INT, MOSYM.format(m="mo_arm64_g.bin", i=0, c="s")),
    ("mo_arm64_g.bin", "symbol_count", "Count the LC_SYMTAB symbols excluding N_STAB debug entries. Submit the count "
     "in base 10.", INT, "llvm-nm-18 mo_arm64_g.bin | wc -l"),
    ("mo_x64.bin", "stab_symbol_count", "Count the N_STAB (debug map) nlist entries. Submit the count in base 10.", INT,
     MOSYM.format(m="mo_x64.bin", i=0, c="n.n_type & 0xe0")),
    ("mo_fat.bin", "nsyms", "Use the arm64 slice. Submit the LC_SYMTAB nsyms value in base 10.", INT,
     "llvm-objdump-18 --macho --arch=arm64 --private-headers mo_fat.bin | awk '/nsyms/{print $2}'"),
    ("mo_arm64_g.bin", "undefined_symbol_count", "Count the undefined (imported) non-debug symbols. Submit the count in "
     "base 10.", INT, "llvm-nm-18 -u mo_arm64_g.bin | wc -l"),
    ("mo_x64.bin", "external_symbol_count", "Count the external (N_EXT) non-debug symbols. Submit the count in base 10.",
     INT, "llvm-nm-18 -g mo_x64.bin | wc -l"),
    ("mo_x64.bin", "has_hctf_section", "Submit true exactly when the Mach-O has a __TEXT,__hctf section.", TF,
     "llvm-otool-18 -l mo_x64.bin | grep -A1 'sectname __hctf$' | grep -q 'segname __TEXT$' && echo true || echo false"),
    ("mo_obj.o", "has_cfg_section", "Submit true exactly when the Mach-O has a __DATA,__cfg section.", TF,
     "llvm-otool-18 -l mo_obj.o | grep -A1 'sectname __cfg$' | grep -q 'segname __DATA$' && echo true || echo false"),
    ("mo_plain.bin", "has_hctf_section", "Submit true exactly when the Mach-O has a __TEXT,__hctf section.", TF,
     "llvm-otool-18 -l mo_plain.bin | grep -q 'sectname __hctf$' && echo true || echo false"),
    ("mo_fat.bin", "slice_count", "Count the fat_arch entries of the universal binary. Submit the count in base 10.",
     INT, "llvm-otool-18 -f mo_fat.bin | awk '/nfat_arch/{print $2}'"),
    ("mo_fat.bin", "is_fat", "Submit true exactly when the member is a fat (universal) Mach-O.", TF,
     "file -b mo_fat.bin | grep -q '^Mach-O universal' && echo true || echo false"),
]
DECOYS = [   # expected null: the rule must stay unsure
    ("mo_x64.bin", "slice_count", "Count the fat_arch entries of the universal binary. Submit the count in base 10.",
     INT, "llvm-otool-18 -f mo_x64.bin  (thin: no fat header -> no fat_arch entries to count)"),
    ("bp_trace_records.elf", "load_command_count", "Submit the Mach-O header ncmds in base 10.", INT,
     "file -b bp_trace_records.elf  (ELF, not Mach-O: no ncmds)"),
]
for decoy, rows in ((False, F), (True, DECOYS)):
    for m, f, q, af, oc in rows:
        exp = None if decoy else subprocess.run(["sh", "-c", oc], cwd=D, capture_output=True, text=True).stdout.strip()
        j = {"kind": "generic_field", "member": m, "field": f, "question": "In evidence.zip, use the d99-- member. " + q,
             "answer_format": af, "expected": exp, "generator_cmd": GEN if m.startswith("mo_") else "existing fixture",
             "oracle_cmd": oc}
        if decoy:
            j["decoy"] = True
        name = f"{m}.{f}.json"
        if any(r[0] == m and r[1] == f for r in rows if r[2] != q):
            name = f"{m}.{f}.{'all' if 'all slices' in q else 'arm64' if 'arm64' in q else 'nostab' if 'excluding' in q else 'v2'}.json"
        open(f"{D}/{name}", "w").write(json.dumps(j, indent=1) + "\n")
        print(name, exp)
