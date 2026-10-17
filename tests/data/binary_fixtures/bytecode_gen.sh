#!/bin/bash
# usage: bytecode_gen.sh out.bin kind json key form
# kind: llvm (clang-18 -c -emit-llvm) | llvm-darwin (wrapper 0x0B17C0DE) | pyc (.venv python3 -m py_compile) |
#       pyc314 (/usr/bin/python3.14 -m py_compile) | luac (luac5.4) | class (javac) | dex (javac + d2j-jar2dex)
# form: raw (blob bytes as the string constant, \xNN escapes) | b64 (coreutils base64 -w0 of the blob)
# BADCRC=1: header crc = 0xefbeadde (decoy). blob = 'HCFG' u8 ver=1, u8 key, u16le len, u32le crc32 (gzip trailer, coreutils) + JSON xor key (perl).
set -e
OUT=$(realpath -m "$1"); P="$3"; K=$(( ${4:-0} )); F="$5"; W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
{ printf 'HCFG\x01'; perl -e 'print pack("Cv", $ARGV[0], $ARGV[1])' "$K" "$LEN"
  if [ -n "$BADCRC" ]; then printf '\xde\xad\xbe\xef'; else printf '%s' "$P" | gzip -c | tail -c8 | head -c4; fi
  perl -e 'print join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]' "$P" "$K"; } > "$W/blob"
if [ "$F" = b64 ]; then S=$(base64 -w0 "$W/blob"); else S=$(perl -0777 -ne 'print map { sprintf "\\x%02x", ord } split //' "$W/blob"); fi
case "$2" in
  llvm|llvm-darwin)
    T=""; [ "$2" = llvm-darwin ] && T="--target=x86_64-apple-macosx11"
    printf 'const char cfg[] = "%s";\nint main(int c, char **v) { return cfg[c] == v[0][0]; }\n' "$S" > "$W/m.c"
    clang-18 $T -O0 -c -emit-llvm -o "$OUT" "$W/m.c" ;;
  pyc|pyc314)
    PY=python3; [ "$2" = pyc314 ] && PY=/usr/bin/python3.14
    if [ "$F" = b64 ]; then printf 'CFG = "%s"\nprint(len(CFG))\n' "$S" > "$W/m.py"; else printf 'CFG = b"%s"\nprint(len(CFG))\n' "$S" > "$W/m.py"; fi
    $PY -m py_compile "$W/m.py"; cp "$W"/__pycache__/m.*.pyc "$OUT" ;;
  luac)
    printf 'local cfg = "%s"\nprint(#cfg)\n' "$S" > "$W/m.lua"; luac5.4 -o "$OUT" "$W/m.lua" ;;
  class|dex)
    printf 'public class M { static final String CFG = "%s"; public static void main(String[] a) { System.out.println(CFG.length() + a.length); } }\n' "$S" > "$W/M.java"
    (cd "$W" && javac --release 11 M.java)
    if [ "$2" = class ]; then cp "$W/M.class" "$OUT"; else
      (cd "$W" && zip -q m.jar M.class && "$(dirname "$(realpath "$0")")"/../../../tools/dex2jar/d2j-jar2dex.sh -f -o m.dex m.jar >/dev/null 2>&1) || \
        (cd "$W" && d2j-jar2dex.sh -f -o m.dex m.jar)
      cp "$W/m.dex" "$OUT"; fi ;;
esac
rm -rf "$W"
