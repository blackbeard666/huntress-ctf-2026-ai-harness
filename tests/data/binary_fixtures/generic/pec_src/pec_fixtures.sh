#!/usr/bin/env bash
# gf-pe-conventions fixtures: MinGW-w64 gcc PE members + expected values from mingw objdump / pefile ONLY (never lib.binary).
# MinGW is unpacked (no root) under tools/mingw/root: apt-get download gcc-mingw-w64-x86-64-win32 gcc-mingw-w64-base
#   binutils-mingw-w64-x86-64 mingw-w64-x86-64-dev mingw-w64-common gcc-mingw-w64-x86-64-win32-runtime; dpkg -x each.
set -euo pipefail
cd "$(dirname "$0")/.."
M=${MINGW_BIN:-../../../../tools/mingw/root/usr/bin}
GCC="$M/x86_64-w64-mingw32-gcc"; OD="$M/x86_64-w64-mingw32-objdump"
if [ "${PEC_REBUILD:-0}" = 1 ]; then
  "$GCC" -O1 -g1 -o pec_mingw_g.exe pec_src/pec.c       # debug sections -> '/N' long names + COFF symbols with aux
  "$GCC" -O2 -s -o pec_mingw_s.exe pec_src/pec.c        # stripped: no COFF symbol table, short names only
  head -c 512 pec_mingw_g.exe > pec_trunc.exe           # decoy: section table / raw data past EOF
fi
PYNAMES='import pefile,json,sys;p=pefile.PE(sys.argv[1]);print(json.dumps([s.Name.rstrip(b"\0").decode() for s in p.sections],separators=(",",":")))'
PYSHA='import pefile,hashlib,sys;p=pefile.PE(sys.argv[1]);print(hashlib.sha256(b"\n".join(s.Name.rstrip(b"\0") for s in p.sections)).hexdigest())'
PYNSYM='import pefile,sys;print(pefile.PE(sys.argv[1]).FILE_HEADER.NumberOfSymbols)'
PYRAW='import pefile,sys;d=open(sys.argv[1],"rb").read();p=pefile.PE(data=d);s=[s for s in p.sections if s.Name.rstrip(b"\0")==b".text"][0];print(d[s.PointerToRawData:s.PointerToRawData+s.SizeOfRawData].count(bytes([int(sys.argv[2],16)])))'
PYVS='import pefile,sys;d=open(sys.argv[1],"rb").read();p=pefile.PE(data=d);s=[s for s in p.sections if s.Name.rstrip(b"\0")==b".text"][0];print(d[s.PointerToRawData:s.PointerToRawData+min(s.Misc_VirtualSize,s.SizeOfRawData)].count(bytes([int(sys.argv[2],16)])))'
od_names() { "$OD" -h "$1" | awk '/^ +[0-9]+ /{print $2}' | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read().split(),separators=(",",":")))'; }
od_symcount() { "$OD" -t "$1" | grep -cE '^\[.*\) 0x[0-9a-f]+ .+' || true; }
INT='{"kind":"integer","syntax":"base-10 integer with no units, separators, whitespace, or explanatory text"}'
LIST='{"kind":"json_array","syntax":"compact JSON array of strings"}'
HEX='{"kind":"sha256","syntax":"64 lowercase hex characters"}'
fx() {  # member field answer_format expected(json) decoy question oracle
  python3 - "$@" <<'PY'
import json, sys
mem, field, af, exp, decoy, q, oracle = sys.argv[1:8]
d = {"kind": "generic_field", "member": mem, "field": field, "question": q, "answer_format": json.loads(af),
     "expected": json.loads(exp), "generator_cmd": "PEC_REBUILD=1 bash pec_src/pec_fixtures.sh  # mingw-w64 gcc 13 "
     "(see pec_src/pec_fixtures.sh: -O1 -g1 / -O2 -s / head -c 512 decoy)", "oracle_cmd": oracle}
if decoy == "1":
    d["decoy"] = True
open(f"{mem.rsplit('.', 1)[0]}.{field}.json", "w").write(json.dumps(d, indent=1) + "\n")
PY
}
js() { python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$1"; }
QRES="List the PE section names in section-header order, resolving '/N' long names through the COFF string table as objdump -h does. Submit a JSON array."
QRAW="List the raw 8-byte Name fields of the PE section headers in header order, NUL padding trimmed, without resolving '/N' long-name references. Submit a JSON array."
QSHA="Collect the raw PE section-header Name fields (do not resolve '/N' references), join them in header order with one LF byte and no trailing LF, then SHA-256."
QSYM="Count the nonempty PE COFF symbol names (primary records only; auxiliary records skipped). Submit the count in base 10."
QNSYM="Report the COFF file header's NumberOfSymbols for the symbol table (auxiliary records included). Submit the count in base 10."
QRAWX="In the PE .text section bytes, count every 0x00 byte; scan the section's full raw data (SizeOfRawData bytes from PointerToRawData). Submit the count in base 10."
QRET="In the PE .text section bytes, count every 0xc3 byte; scan the section's full raw data (SizeOfRawData bytes from PointerToRawData). Submit the count in base 10."
QVS="In the PE .text section bytes, count every 0x00 byte; scan VirtualSize bytes (min(VirtualSize, SizeOfRawData) from PointerToRawData). Submit the count in base 10."
for m in pec_mingw_g pec_mingw_s; do
  F=$m.exe
  fx $F section_names "$LIST" "$(js "$(od_names $F)")" 0 "$QRES" "x86_64-w64-mingw32-objdump -h $F | awk '/^ +[0-9]+ /{print \$2}'"
  fx $F raw_section_names "$LIST" "$(js "$(python3 -c "$PYNAMES" $F)")" 0 "$QRAW" "python3 -c '$PYNAMES' $F"
  fx $F symbol_count "$INT" "$(js "$(od_symcount $F)")" 0 "$QSYM" "x86_64-w64-mingw32-objdump -t $F | grep -cE '^\\[.*\\) 0x[0-9a-f]+ .+'"
  fx $F text_raw_zero_byte_count "$INT" "$(js "$(python3 -c "$PYRAW" $F 00)")" 0 "$QRAWX" "python3 -c '$PYRAW' $F 00"
done
F=pec_mingw_g.exe
fx $F raw_section_names_sha256 "$HEX" "$(js "$(python3 -c "$PYSHA" $F)")" 0 "$QSHA" "python3 -c '$PYSHA' $F"
fx $F coff_symbol_record_count "$INT" "$(js "$(python3 -c "$PYNSYM" $F)")" 0 "$QNSYM" "python3 -c '$PYNSYM' $F"
fx $F text_ret_byte_count "$INT" "$(js "$(python3 -c "$PYRAW" $F c3)")" 0 "$QRET" "python3 -c '$PYRAW' $F c3"
fx $F text_vs_zero_byte_count "$INT" "$(js "$(python3 -c "$PYVS" $F 00)")" 0 "$QVS" "python3 -c '$PYVS' $F 00"
F=pec_trunc.exe   # decoys: pefile warns 'PointerToRawData points beyond the end of the file' -> no answer
for p in "text_raw_zero_byte_count|$INT|$QRAWX" "raw_section_names|$LIST|$QRAW" "coff_symbol_record_count|$INT|$QNSYM"; do
  IFS='|' read -r fld af q <<<"$p"
  fx $F "$fld" "$af" null 1 "$q" "python3 -c 'import pefile;print(pefile.PE(\"$F\").get_warnings()[:3])'  # truncated at 512 bytes: section table + raw data past EOF"
done
