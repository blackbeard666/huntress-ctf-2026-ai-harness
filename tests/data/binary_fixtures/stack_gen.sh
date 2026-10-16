#!/bin/bash
# usage: stack_gen.sh out.bin cc opt json [crc_xor]     (cc: gcc | aarch64-linux-gnu-gcc; opt: 0 | 2)
# blob: printf header + crc32 from the gzip trailer (crc_xor != 0 -> corrupted header crc = decoy); byte values: coreutils
# od -An -tu1. Binary: a C program that assembles the blob at runtime into a `volatile unsigned char b[N]` on the STACK,
# one store statement per byte (b[0]=72; b[1]=67; ...), compiled by `cc -O<opt>` -> mov-immediate stores (x86-64
# movb $imm,disp(%rsp|%rbp); AArch64 mov wN,#imm + strb). `prog dump` writes the built buffer to stdout (oracle).
set -e
P="$4"; W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
CRC=$(printf %08x $(( 0x$CRC ^ ${5:-0} )))
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"
N=$(wc -c < "$W/blob.raw")
{ echo '#include <stdio.h>'; echo '#include <string.h>'
  echo 'int main(int c, char **v) {'
  echo "  volatile unsigned char b[$N];"
  od -An -tu1 -v "$W/blob.raw" | tr -s ' \n' '\n' | grep . | awk '{ printf "  b[%d] = %s;\n", NR-1, $1 }'
  echo '  unsigned s = 0; for (unsigned i = 0; i < sizeof b; i++) s += b[i] * (i + 1);'
  echo '  if (c > 1 && !strcmp(v[1], "dump")) { for (unsigned i = 0; i < sizeof b; i++) putchar(b[i]); return 0; }'
  echo '  if (c > 1 && (unsigned)strlen(v[1]) == s) puts("ok"); else printf("usage: %s <cfg>\n", v[0]); return 0; }'
} > "$W/m.c"
"$2" -O"$3" -o "$1" "$W/m.c"
rm -rf "$W"
