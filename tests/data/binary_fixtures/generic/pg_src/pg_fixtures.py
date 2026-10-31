"""gf-predicate-grammar fixtures: expected = the oracle_cmd's stdout (readelf / objdump / pefile / macholib / lief),
never lib.binary. Run from anywhere: python3 pg_src/pg_fixtures.py"""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent.parent
PRE = "In evidence.zip, use the d99-- member. "
INT = {"kind": "integer", "syntax": "base-10 integer with no units, separators, whitespace, or explanatory text"}
BOOL = {"kind": "boolean", "syntax": "lowercase true or false"}
TF = " && echo true || echo false"
GEN_ELF = "gcc -O1 -o gf_c_imports.bin gf_imports.c -lm -lz (existing member)"
GEN_EV = "gcc -O1 -o gf_c_events.bin gf_events.c (existing member)"
GEN_SO = "gcc -O1 -shared -fPIC -o gf_c_exports.so gf_exports.c (existing member)"
GEN_EXE = "python3 -m ziglang cc -target x86_64-windows-gnu -O1 -o gf_pe_imports.exe gf_pe_imports.c -luser32 -lws2_32 (existing member)"
GEN_DLL = "zig cc -target x86_64-windows-gnu -shared -o gf_pe_exports.dll gf_exports.c (existing member)"
GEN_MO = "tools/ziglang/ziglang/zig cc -target x86_64-macos -O1 -o pg_macho.bin pg_src/pg_macho.c (pg_src/pg_gen.sh)"
GEN_MD = "tools/ziglang/ziglang/zig cc -target x86_64-macos -O1 -shared -o pg_macho.dylib pg_src/pg_lib.c (pg_src/pg_gen.sh)"
NEEDED = "readelf -d -W gf_c_imports.bin | sed -n 's/.*(NEEDED).*\\[\\(.*\\)\\]/\\1/p'"
PEDLL = "python3 -c \"import pefile; p=pefile.PE('{m}'); [print(e.dll.decode()) for e in p.DIRECTORY_ENTRY_IMPORT]\""
PEEXP = "python3 -c \"import pefile; p=pefile.PE('{m}'); [print(s.name.decode()) for s in p.DIRECTORY_ENTRY_EXPORT.symbols if s.name]\""
MODY = ("python3 -c \"from macholib.MachO import MachO; [print(c[2].rstrip(b'\\0').decode()) for h in MachO('{m}').headers"
        " for c in h.commands if c[0].cmd in (0xc, 0x80000018, 0x8000001f, 0x20, 0x80000023)]\"")
LIEFEXP = ("python3 -c \"import lief, sys; b = lief.parse('{m}'); n = [s.name for s in b.exported_symbols]; "
           "sys.stdout.write(''.join(x + chr(10) for x in n)); sys.stdout.flush()\" 2>/dev/null")

FX = [
    # --- ELF
    ("gf_c_imports.bin", "dt_needed_entries", "Count the DT_NEEDED entries of the ELF dynamic section. Submit the count "
     "in base 10.", INT, GEN_ELF, NEEDED + " | wc -l"),
    ("gf_c_imports.bin", "has_zlib_without_gnat", "Submit true exactly when any DT_NEEDED entry equals libz.so.1 and no "
     "nonempty ELF symbol name contains gnat. Submit lowercase true or false.", BOOL, GEN_ELF,
     "{ " + NEEDED + " | grep -qx libz.so.1 && ! readelf -sW gf_c_imports.bin | awk 'NR>3{print $8}' | grep -q gnat; }" + TF),
    ("gf_c_imports.bin", "deps_all_lib_prefixed", "Submit true exactly when every DT_NEEDED entry starts with lib. "
     "Submit lowercase true or false.", BOOL, GEN_ELF, "! " + NEEDED + " | grep -qv '^lib'" + TF),
    ("gf_c_imports.bin", "has_no_zlib_dep", "Submit true exactly when none of the DT_NEEDED entries contain libz. "
     "Submit lowercase true or false.", BOOL, GEN_ELF, "! " + NEEDED + " | grep -q libz" + TF),
    ("gf_c_imports.bin", "undefined_api_tally", "Count the imported functions (undefined named .dynsym symbols, "
     "@version dropped). Submit the count in base 10.", INT, GEN_ELF,
     "readelf --dyn-syms -W gf_c_imports.bin | awk '$7==\"UND\" && $8!=\"\"{sub(/@.*/,\"\",$8); print $8}' | wc -l"),
    ("gf_c_events.bin", "has_two_handlers", "Submit true exactly when at least 2 nonempty ELF symbol names match "
     "/event_(success|decoy)/ and the final bytes do not contain NimMain. Submit lowercase true or false.", BOOL, GEN_EV,
     "{ [ $(readelf -sW gf_c_events.bin | sed -n '/Symbol table .\\.symtab/,$p' | awk 'NR>2 && $8!=\"\"{print $8}' | "
     "grep -cE 'event_(success|decoy)') -ge 2 ] && ! grep -q NimMain gf_c_events.bin; }" + TF),
    ("gf_c_exports.so", "api_surface_size", "Count the exported symbol names of the ELF image. Submit the count in "
     "base 10.", INT, GEN_SO,
     "readelf --dyn-syms -W gf_c_exports.so | awk 'NR>3 && $7!=\"UND\" && ($5==\"GLOBAL\"||$5==\"WEAK\") && $8!=\"\""
     "{print $8}' | sort -u | wc -l"),
    # --- PE
    ("gf_pe_imports.exe", "dll_dependency_tally", "What is the imported DLL count? Count the PE import descriptors. "
     "Submit the count in base 10.", INT, GEN_EXE, PEDLL.format(m="gf_pe_imports.exe") + " | wc -l"),
    ("gf_pe_imports.exe", "has_kernel32_no_msvcrt", "Submit true exactly when any imported DLL name equals "
     "kernel32.dll (case-insensitive) and no imported DLL name contains msvcrt. Submit lowercase true or false.", BOOL,
     GEN_EXE, "{ " + PEDLL.format(m="gf_pe_imports.exe") + " | grep -qix kernel32.dll && ! " +
     PEDLL.format(m="gf_pe_imports.exe") + " | grep -q msvcrt; }" + TF),
    ("gf_pe_exports.dll", "has_three_ie_exports", "Submit true exactly when at least 3 exported symbol names start with "
     "ie_. Submit lowercase true or false.", BOOL, GEN_DLL,
     "[ $(" + PEEXP.format(m="gf_pe_exports.dll") + " | grep -c '^ie_') -ge 3 ]" + TF),
    # --- Mach-O
    ("pg_macho.bin", "has_libsystem_only", "Submit true exactly when any LC_LOAD_DYLIB dylib path ends with "
     "libSystem.B.dylib and every dylib path starts with /usr/lib/. Submit lowercase true or false.", BOOL, GEN_MO,
     "{ " + MODY.format(m="pg_macho.bin") + " | grep -q 'libSystem.B.dylib$' && ! " + MODY.format(m="pg_macho.bin") +
     " | grep -qv '^/usr/lib/'; }" + TF),
    ("pg_macho.bin", "dylib_dependency_tally", "Count the Mach-O dylib load commands (LC_LOAD_DYLIB dependencies). "
     "Submit the count in base 10.", INT, GEN_MO, MODY.format(m="pg_macho.bin") + " | wc -l"),
    ("pg_macho.dylib", "api_surface_size", "Count the exported symbol names of the Mach-O image. Submit the count in "
     "base 10.", INT, GEN_MD, LIEFEXP.format(m="pg_macho.dylib") + " | wc -l"),
    ("pg_macho.dylib", "has_three_pg_exports", "Submit true exactly when at least three exported symbol names start "
     "with _pg_lib_. Submit lowercase true or false.", BOOL, GEN_MD,
     "[ $(" + LIEFEXP.format(m="pg_macho.dylib") + " | grep -c '^_pg_lib_') -ge 3 ]" + TF),
]
# decoys: wrong container for the named table / unparseable bytes / a clause still outside the grammar -> null
DECOYS = [
    ("gf_decoy_random.bin", "dt_needed_entries", FX[0][2], INT, "head -c 4096 /dev/urandom (existing member)",
     "file -b gf_decoy_random.bin  # 'data': no ELF dynamic section"),
    ("gf_decoy_random.bin", "has_no_zlib_dep", FX[3][2], BOOL, "head -c 4096 /dev/urandom (existing member)",
     "file -b gf_decoy_random.bin  # 'data'"),
    ("gf_pe_imports.exe", "dt_needed_entries", FX[0][2], INT, GEN_EXE,
     "file -b gf_pe_imports.exe  # PE32+: an ELF DT_NEEDED question does not apply"),
    ("pg_macho.bin", "dll_dependency_tally", FX[7][2], INT, GEN_MO,
     "file -b pg_macho.bin  # Mach-O: no PE import descriptors"),
    ("gf_c_imports.bin", "has_mixed_and_or", "Submit true exactly when any DT_NEEDED entry equals libz.so.1 and any "
     "DT_NEEDED entry equals libm.so.6 or any nonempty ELF symbol name contains gnat. Submit lowercase true or false.",
     BOOL, GEN_ELF, "n/a: mixed and/or without stated precedence stays unsure (None)"),
]
for member, field, q, af, gen, orc in FX + DECOYS:
    decoy = (member, field, q, af, gen, orc) in DECOYS
    exp = None
    if not decoy:
        exp = subprocess.run(["bash", "-c", orc], cwd=D, capture_output=True, text=True).stdout.strip()
        assert exp, (member, field, orc)
    d = {"kind": "generic_field", "member": member, "field": field, "question": PRE + q, "answer_format": af,
         "expected": exp, "generator_cmd": gen, "oracle_cmd": orc}
    if decoy:
        d["decoy"] = True
    (D / f"pg_{member}.{field}.json").write_text(json.dumps(d, indent=1) + "\n")
    print(member, field, exp)
