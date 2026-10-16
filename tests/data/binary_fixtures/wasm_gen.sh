#!/bin/bash
# usage: wasm_gen.sh out.wasm kind json key
# kind: c (clang-18 --target=wasm32 -O2 -c: a real compiler-made relocatable module (no wasm-ld on this host), the
#       blob = the march_gen.sh C struct {char m[4]; u8 ver, key; u16 len; u32 crc; u8 body[]} in its own .rodata
#       segment, after a banner segment -> nonzero memory offset)
#     | wat (wat2wasm: 2 active segments, blob 7 bytes into the 2nd one at i32.const 4096, a passive segment too)
#     | wat64 (wat2wasm --enable-memory64: memory i64, blob in an i64.const 65536 segment)
#     | badcrc (wat with the header crc off by one: a DECOY -- no valid HCFG)
#     | impostor (NOT wasm: '\0asm' + version 2 + garbage, then a valid raw blob: a DECOY for the format)
# crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl).
set -e
P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
[ "$2" = badcrc ] && CRC=$(printf '%08x' $(( 0x$CRC ^ 1 )))
# whole blob as wat "\xx" escapes: header packed little-endian by perl
ESC=$(perl -e '$b = pack("a4 C C v V", "HCFG", 1, $ARGV[1], length $ARGV[0], hex $ARGV[2]) .
  join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]; print join "", map { sprintf "\\%02x", ord } split //, $b' "$P" "$K" "$CRC")
case "$2" in
  c) BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
     cat > "$W/m.c" <<C
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };
const char banner[] = "orchard beacon v2";
__attribute__((used)) const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
__attribute__((export_name("check"))) int check(const char *s) { int n = 0; while (s[n]) n++; return n == hcfg_blob.len + banner[0]; }
C
     clang-18 --target=wasm32-unknown-unknown -O2 -c -o "$1" "$W/m.c" ;;
  wat|badcrc) cat > "$W/m.wat" <<WAT
(module
  (memory (export "memory") 1)
  (func (export "check") (param i32) (result i32) (i32.load8_u (i32.const 4103)))
  (data (i32.const 1024) "orchard beacon v2\00GET /tasks\00")
  (data (i32.const 4096) "cfg:v1\00$ESC")
  (data "passive-segment HCF\00"))
WAT
     wat2wasm -o "$1" "$W/m.wat" ;;
  wat64) cat > "$W/m.wat" <<WAT
(module
  (memory (export "memory") i64 2)
  (data (i64.const 1024) "orchard64\00")
  (data (i64.const 65536) "$ESC"))
WAT
     wat2wasm --enable-memory64 -o "$1" "$W/m.wat" ;;
  impostor) { printf '\0asm\2\0\0\0'; head -c 40 /dev/zero | tr '\0' 'Z'; printf "$(printf '%s' "$ESC" | sed 's/\\/\\x/g')"; } > "$1" ;;
esac
rm -rf "$W"
