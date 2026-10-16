#!/bin/bash
# usage: march_gen.sh out.o target json key
# target: a clang-18 --target triple (ET_REL .o via `clang-18 -c`; no lld here) or "aarch64-gcc" (linked ET_EXEC/DYN by
# aarch64-linux-gnu-gcc). The HCFG blob is a C struct {char m[4]; u8 ver, key; u16 len; u32 crc; u8 body[]} placed in a
# `.hcfg` section, so the COMPILER writes len/crc in the target's native byte order (big-endian on mips/ppc/sparcv9).
# crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl).
set -e
P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
cat > "$W/m.c" <<C
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };
__attribute__((section(".hcfg"), used)) const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
int check(const char *s) { int n = 0; while (s[n]) n++; return n == hcfg_blob.len; }
int main(int c, char **v) { return c > 1 ? check(v[1]) : 0; }
C
if [ "$2" = aarch64-gcc ]; then aarch64-linux-gnu-gcc -O2 -o "$1" "$W/m.c"; else clang-18 --target="$2" -O2 -c -o "$1" "$W/m.c"; fi
rm -rf "$W"
