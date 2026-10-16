#!/bin/bash
# usage: macho_gen.sh out.o target json key
# target: x86_64-apple-macos | arm64-apple-macos (clang-18 -c -> MH_OBJECT, no ld64 here) | fat (both, glued by
# llvm-lipo-18 -create into a FAT_MAGIC universal file) | nosect (arm64, blob kept in __DATA,__const: no __hcfg).
# The HCFG blob is the march_gen.sh C struct {char m[4]; u8 ver, key; u16 len; u32 crc; u8 body[]} placed in
# section("__DATA,__hcfg"); crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl).
set -e
P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
SEC='__DATA,__hcfg'; [ "$2" = nosect ] && SEC='__DATA,__const'
cat > "$W/m.c" <<C
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };
__attribute__((section("$SEC"), used)) const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
int check(const char *s) { int n = 0; while (s[n]) n++; return n == hcfg_blob.len; }
C
case "$2" in
  fat) clang-18 --target=x86_64-apple-macos -O2 -c -o "$W/x.o" "$W/m.c"
       clang-18 --target=arm64-apple-macos -O2 -c -o "$W/a.o" "$W/m.c"
       llvm-lipo-18 -create "$W/x.o" "$W/a.o" -output "$1" ;;
  nosect) clang-18 --target=arm64-apple-macos -O2 -c -o "$1" "$W/m.c" ;;
  *) clang-18 --target="$2" -O2 -c -o "$1" "$W/m.c" ;;
esac
rm -rf "$W"
