#!/usr/bin/env bash
# backfill-spec-grammar-extensions (prebuild): import / DT_NEEDED / export set fixtures. Members built by gcc and
# zig cc (pip ziglang under tools/ziglang, mingw target); expected from binutils readelf / nm / objdump -- never lib.binary.
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$(cd ../../../.. && pwd)/tools/ziglang${PYTHONPATH:+:$PYTHONPATH}"
G_ELF="gcc -O1 -o gf_c_imports.bin gf_imports.c -lm -lz"
G_SO="gcc -O1 -shared -fPIC -o gf_c_exports.so gf_exports.c"
G_PE="python3 -m ziglang cc -target x86_64-windows-gnu -O1 -o gf_pe_imports.exe gf_pe_imports.c -luser32 -lws2_32"
G_DLL="python3 -m ziglang cc -target x86_64-windows-gnu -O1 -shared -o gf_pe_exports.dll gf_exports.c"
if [ "${IE_REBUILD:-0}" = 1 ]; then
  for g in "$G_ELF" "$G_SO" "$G_PE" "$G_DLL"; do bash -c "$g"; done
  rm -f gf_pe_imports.pdb gf_pe_exports.pdb gf_pe_exports.lib
fi
INT='{"kind": "integer", "syntax": "base-10 integer with no units, separators, whitespace, or explanatory text"}'
HEX64='{"kind": "pattern", "syntax": "exactly 64 lowercase hexadecimal characters; no prefix, whitespace, or explanatory text"}'
emit() {   # emit MEMBER FIELD QUESTION ANSWER_FORMAT_JSON ORACLE_CMD GENERATOR [decoy]   (expected = oracle stdout)
  local exp
  if [ "$5" = null ]; then exp=null; else exp=$(bash -c "$5"); exp="\"$exp\""; fi
  python3 - "$1" "$2" "$3" "$4" "$exp" "$6" "$5" "${7:-}" <<'PY'
import json, sys
m, f, q, af, exp, gen, orc, decoy = sys.argv[1:9]
out = {"kind": "generic_field", "member": m, "field": f, "question": q, "answer_format": json.loads(af),
       "expected": json.loads(exp), "generator_cmd": gen, "oracle_cmd": orc}
if decoy:
    out["decoy"] = True
open(f"{m.rsplit('.', 1)[0]}.{f}.json", "w").write(json.dumps(out, indent=1) + "\n")
PY
}
U="In evidence.zip, use the d99-- member. "
SHA="sort strings by ascending code-unit order, join with one LF byte and no trailing LF, then SHA-256 those UTF-8 bytes."
NEEDED="readelf -d -W gf_c_imports.bin | sed -n 's/.*(NEEDED).*\[\(.*\)\]/\1/p'"
emit gf_c_imports.bin needed_count "${U}Count the ELF DT_NEEDED entries of the dynamic section. Submit the count in base 10." "$INT" "$NEEDED | wc -l" "$G_ELF"
emit gf_c_imports.bin needed_sha256 "${U}Collect every ELF DT_NEEDED library name, ${SHA}" "$HEX64" "printf %s \"\$($NEEDED | LC_ALL=C sort)\" | sha256sum | cut -c1-64" "$G_ELF"
emit gf_c_imports.bin imported_function_count "${U}Count the imported functions: undefined, nonempty-named .dynsym symbols with any @version suffix removed. Submit the count in base 10." "$INT" "readelf --dyn-syms -W gf_c_imports.bin | awk '\$7==\"UND\" && \$8!=\"\"{sub(/@.*/,\"\",\$8); print \$8}' | sort -u | wc -l" "$G_ELF"
EXP_SO="nm -D --defined-only gf_c_exports.so | awk '{print \$3}'"
emit gf_c_exports.so export_count "${U}Count the exported symbols (defined dynamic symbols). Submit the count in base 10." "$INT" "$EXP_SO | wc -l" "$G_SO"
emit gf_c_exports.so exports_sha256 "${U}Collect every exported symbol name, ${SHA}" "$HEX64" "printf %s \"\$($EXP_SO | LC_ALL=C sort)\" | sha256sum | cut -c1-64" "$G_SO"
DLLS="objdump -p gf_pe_imports.exe | sed -n 's/^\tDLL Name: //p'"
emit gf_pe_imports.exe import_dll_count "${U}Count the PE import descriptors (imported DLL names). Submit the count in base 10." "$INT" "$DLLS | wc -l" "$G_PE"
emit gf_pe_imports.exe import_dlls_sha256 "${U}Collect every imported DLL name from the PE import directory, lowercase each DLL name, ${SHA}" "$HEX64" "printf %s \"\$($DLLS | tr A-Z a-z | LC_ALL=C sort)\" | sha256sum | cut -c1-64" "$G_PE"
EXP_DLL="objdump -p gf_pe_exports.dll | sed -n '/\[Ordinal\/Name Pointer\] Table/,/^\$/p' | awk '/\+base/{print \$NF}'"
emit gf_pe_exports.dll export_count "${U}Count the named exports in the PE export directory. Submit the count in base 10." "$INT" "$EXP_DLL | wc -l" "$G_DLL"
emit gf_pe_exports.dll exports_sha256 "${U}Collect every PE export name, ${SHA}" "$HEX64" "printf %s \"\$($EXP_DLL | LC_ALL=C sort)\" | sha256sum | cut -c1-64" "$G_DLL"
# decoys: random bytes (no dynamic section / import directory) and an ambiguous bare import_count (DLLs or functions?)
emit gf_decoy_random.bin needed_count "${U}Count the ELF DT_NEEDED entries of the dynamic section. Submit the count in base 10." "$INT" null "head -c 4096 /dev/urandom > gf_decoy_random.bin  # file: data -> no dynamic section (None)" decoy
emit gf_pe_imports.exe import_count "${U}Count the imports. Submit the count in base 10." "$INT" null "$G_PE  # ambiguous: DLLs or functions -> None" decoy
