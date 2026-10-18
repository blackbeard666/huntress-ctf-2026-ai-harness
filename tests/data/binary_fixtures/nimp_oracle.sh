#!/bin/bash
# usage: nimp_oracle.sh file.bin  -> JSON {needed, imports, interpreter, exports[, imphash, imports_qualified, install_name]}
# from tools that never touch lib/: GNU readelf -dW / --dyn-syms -W / -lW + nm -D --defined-only (ELF);
# GNU objdump -p import tables + export table, LIEF get_imphash(PEFILE mode) (PE);
# llvm-objdump-18 --macho --private-headers (LC_LOAD_DYLIB / LC_ID_DYLIB / LC_LOAD_DYLINKER) + llvm-nm-18 -u -p / -gU (Mach-O).
# Absent field -> "none". Not a recognised image -> every field "none".
F="$1"; T=$(mktemp -d)
case "$(file -b "$F")" in
 ELF*)
  readelf -dW "$F" 2>/dev/null | sed -n 's/.*(NEEDED).*\[\(.*\)\]$/\1/p' > "$T/needed"
  readelf --dyn-syms -W "$F" 2>/dev/null | awk '$7=="UND" && $8!="" {sub(/@.*/,"",$8); print $8}' | awk '!s[$0]++' > "$T/imports"
  readelf -lW "$F" 2>/dev/null | sed -n 's/.*\[Requesting program interpreter: \(.*\)\]$/\1/p' > "$T/interp"
  LC_ALL=C nm -D --defined-only "$F" 2>/dev/null | awk '$2 ~ /^[TDRBWV]$/ {print $3}' | grep -vxE '_init|_fini|_edata|_end|__bss_start' | LC_ALL=C sort -u > "$T/exports" ;;
 PE32*)
  objdump -p "$F" > "$T/p"
  awk '/^\tDLL Name: /{d=$3} /^\tvma: /{f=1;next} f&&/^\t[0-9a-f]+ +/{print d"!"(NF>=4 ? $4 : "ord"$2)} /^\tDLL Name: |^$/{f=0}' "$T/p" > "$T/qual"
  sed -n 's/^\tDLL Name: //p' "$T/p" > "$T/needed"
  cut -d'!' -f2 "$T/qual" > "$T/imports"
  awk '/^\[Ordinal\/Name Pointer\] Table/{f=1;next} f&&/^\t\[ *[0-9]+\] /{print $NF} /^$/{f=0}' "$T/p" | LC_ALL=C sort -u > "$T/exports"
  : > "$T/interp"
  python3 -I -c 'import lief,sys; b=lief.PE.parse(sys.argv[1]); print(lief.PE.get_imphash(b, lief.PE.IMPHASH_MODE.PEFILE))' "$F" > "$T/imphash" ;;
 Mach-O*)
  llvm-objdump-18 --macho --private-headers "$F" > "$T/h"
  awk '/cmd LC_(LOAD|LOAD_WEAK|REEXPORT|LAZY_LOAD|LOAD_UPWARD)_DYLIB$/{f=1} /cmd LC_ID_DYLIB$/{g=1} /^ +name /{if(f)print $2; f=0} ' "$T/h" > "$T/needed"
  awk '/cmd LC_ID_DYLIB$/{g=1} /^ +name /{if(g)print $2; g=0}' "$T/h" > "$T/install"
  awk '/cmd LC_LOAD_DYLINKER$/{g=1} /^ +name /{if(g)print $2; g=0}' "$T/h" > "$T/interp"
  llvm-nm-18 -u -p "$F" | awk 'NF==1' | awk '!s[$0]++' > "$T/imports"
  llvm-nm-18 -gU "$F" | awk '{print $3}' | LC_ALL=C sort -u > "$T/exports" ;;
esac
python3 -I - "$T" <<'PY'
import json, os, sys
T = sys.argv[1]
def L(n):
    p = os.path.join(T, n)
    v = [x for x in open(p).read().split("\n") if x] if os.path.exists(p) else []
    return v or "none"
out = {"needed": L("needed"), "imports": L("imports"), "interpreter": (L("interp") if L("interp") == "none" else L("interp")[0]),
       "exports": L("exports")}
if os.path.exists(os.path.join(T, "imphash")):
    out["imphash"] = L("imphash")[0]; out["imports_qualified"] = L("qual")
if os.path.exists(os.path.join(T, "install")):
    out["install_name"] = L("install") if L("install") == "none" else L("install")[0]
print(json.dumps(out))
PY
rm -rf "$T"
