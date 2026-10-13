#!/bin/bash
# usage: split_gen.sh out.bin codec(base64|base64url|base32|hex) chunk_chars layout(ptrs|table) json [crc_xor]
# blob: printf header + crc32 from the gzip trailer; text: coreutils base64/basenc/base32 / xxd -p; chunks: coreutils
# fold -w N; binary: a C program with the chunks as separate literals (ptrs: const char *parts[]; table: char[][N+1]),
# compiled by gcc -O2 (literals land in .rodata in file order, NUL-terminated / NUL-padded).
set -e
P="$5"; W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
CRC=$(printf %08x $(( 0x$CRC ^ ${6:-0} )))
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"
case "$2" in
  base64) base64 -w0 "$W/blob.raw" ;; base64url) basenc --base64url -w0 "$W/blob.raw" ;;
  base32) base32 -w0 "$W/blob.raw" ;; hex) xxd -p -c0 "$W/blob.raw" ;;
esac | fold -w "$3" > "$W/chunks.txt"
{ echo '#include <stdio.h>'; echo '#include <string.h>'
  if [ "$4" = table ]; then echo "static const char parts[][$(( $3 + 1 ))] = {"; else echo 'static const char *parts[] = {'; fi
  sed 's/.*/  "&",/' "$W/chunks.txt"; echo '};'
  echo 'int main(int c, char **v) { char buf[4096] = {0}; for (unsigned i = 0; i < sizeof parts / sizeof parts[0]; i++)'
  echo '  strcat(buf, parts[i]); if (c > 1 && !strcmp(v[1], buf)) puts("ok"); else printf("usage: %s <cfg>\n", v[0]); return 0; }'
} > "$W/m.c"
gcc -O2 -o "$1" "$W/m.c"
rm -rf "$W"
