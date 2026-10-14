#!/bin/bash
# usage: int_gen.sh out.bin layout(u32arr|u64arr|u32words|u16words|decimal) json [crc_xor]
# blob: printf header + crc32 from the gzip trailer; element lists: coreutils od -An -tu1 (byte values) / xxd -p -c W
# (big-endian words, last word zero-padded); binary: a C program holding the list as a const array (u32arr: uint32_t
# per byte, u64arr: uint64_t per byte, u32words/u16words: uint32_t/uint16_t 0x48434647-style words) or as one string
# literal "72,67,70,..." (decimal), compiled by gcc -O2 on x86-64 (little-endian storage).
set -e
P="$3"; W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
CRC=$(printf %08x $(( 0x$CRC ^ ${4:-0} )))
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"
BYTES=$(od -An -tu1 -v "$W/blob.raw" | tr -s ' \n' ' ' | sed 's/^ //; s/ $//')
words() { xxd -p -c "$1" "$W/blob.raw" | awk -v n=$((2*$1)) '{ while (length($0) < n) $0 = $0 "0"; printf "0x%s,\n", $0 }'; }
{ echo '#include <stdio.h>'; echo '#include <stdint.h>'; echo '#include <string.h>'
  case "$2" in
    u32arr) echo 'static const uint32_t cfg[] = {'; echo "$BYTES" | sed 's/ /, /g'; echo '};' ;;
    u64arr) echo 'static const uint64_t cfg[] = {'; echo "$BYTES" | sed 's/ /, /g'; echo '};' ;;
    u32words) echo 'static const uint32_t cfg[] = {'; words 4; echo '};' ;;
    u16words) echo 'static const uint16_t cfg[] = {'; words 2; echo '};' ;;
    decimal) printf 'static const char cfg[] = "%s";\n' "$(echo "$BYTES" | sed 's/ /,/g')" ;;
  esac
  echo 'int main(int c, char **v) { volatile unsigned s = 0; for (unsigned i = 0; i < sizeof cfg / sizeof cfg[0]; i++)'
  echo '  s += (unsigned)cfg[i] * (i + 1); if (c > 1 && (unsigned)strlen(v[1]) == s) puts("ok"); else printf("usage: %s <cfg>\n", v[0]); return 0; }'
} > "$W/m.c"
gcc -O2 -o "$1" "$W/m.c"
rm -rf "$W"
