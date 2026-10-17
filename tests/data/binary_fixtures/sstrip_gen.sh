#!/bin/bash
# usage: sstrip_gen.sh out.elf kind json key
# gcc -O1 build of a tiny program holding an HCFG blob in .rodata, then the header is damaged by a stdlib python patch:
# kind: zero      sstrip-style: e_shoff/e_shnum/e_shstrndx = 0 and the section header table cut off the file tail
#     | badstrndx e_shstrndx = 0x7a7a (garbage, > e_shnum): section headers still parse, names do not
#     | badshoff  e_shoff points past EOF (e_shnum/e_shstrndx kept): no section table can be read
#     | fakehcfg  intact headers, `objcopy --rename-section .comment=.hcfg`: a literal .hcfg section WITHOUT the blob
#     | trunc     DECOY: the zero build cut to its first 40 bytes (no full ELF header, no blob)
# blob = {char m[4]; u8 ver, key; u16 len; u32 crc; u8 body[]}; crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl).
set -e
P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
cat > "$W/p.c" <<C
#include <stdio.h>
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };
const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
int main(int c, char **v) { (void)v; printf("beacon %d\n", hcfg_blob.body[c & 3]); return 0; }
C
gcc -O1 -o "$W/a" "$W/p.c"
case "$2" in
  fakehcfg) objcopy --rename-section .comment=.hcfg "$W/a" "$1" ;;
  *) python3 -I - "$W/a" "$1" "$2" <<'PY'
import struct, sys
d = bytearray(open(sys.argv[1], "rb").read()); kind = sys.argv[3]
shoff, = struct.unpack_from("<Q", d, 0x28)
if kind in ("zero", "trunc"):
    struct.pack_into("<Q", d, 0x28, 0); struct.pack_into("<HHH", d, 0x3a, 0, 0, 0)
    d = d[:shoff]
    if kind == "trunc":
        d = d[:40]
elif kind == "badstrndx":
    struct.pack_into("<H", d, 0x3e, 0x7a7a)
elif kind == "badshoff":
    struct.pack_into("<Q", d, 0x28, len(d) + 0x100000)
open(sys.argv[2], "wb").write(d)
PY
  ;;
esac
rm -rf "$W"
