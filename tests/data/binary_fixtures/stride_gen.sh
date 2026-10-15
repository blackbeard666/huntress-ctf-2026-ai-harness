#!/bin/bash
# usage: stride_gen.sh out.bin layout(s2raw|s4raw|s3b64|halves|evenodd) json [crc_xor]
# blob: printf header + crc32 from the gzip trailer; layout applied by perl (filler = bytes 0x80+ of an LCG,
# base64 by coreutils base64 -w0); binary: a C program holding the stored bytes as a const array (xxd -i), gcc -O2.
set -e
P="$3"; W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
CRC=$(printf %08x $(( 0x$CRC ^ ${4:-0} )))
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"
case "$2" in
  s3b64) base64 -w0 "$W/blob.raw" > "$W/src"; K=3 ;;
  s2raw) cp "$W/blob.raw" "$W/src"; K=2 ;;
  s4raw) cp "$W/blob.raw" "$W/src"; K=4 ;;
esac
case "$2" in
  s*) perl -0777 -e '$k=shift; $_=<STDIN>; $s=7; for $c (split //) { print $c; for (2..$k) { $s=($s*1103515245+12345)%2**31; print chr(0x80 | ($s>>16)&0x7f) } }' "$K" < "$W/src" > "$W/stored" ;;
  halves) perl -0777 -e '$_=<STDIN>; $h=int(length($_)/2); @a=split //, substr($_,0,$h); @b=split //, substr($_,$h); while (@a||@b) { print shift @a if @a; print shift @b if @b }' < "$W/blob.raw" > "$W/stored" ;;
  evenodd) perl -0777 -e '$_=<STDIN>; @c=split //; print @c[grep { !($_%2) } 0..$#c], @c[grep { $_%2 } 0..$#c]' < "$W/blob.raw" > "$W/stored" ;;
esac
{ echo '#include <stdio.h>'; echo '#include <string.h>'
  cp "$W/stored" "$W/cfg"; (cd "$W" && xxd -i cfg) | sed 's/^unsigned char/static const unsigned char/; s/^unsigned int/static const unsigned int/'
  echo 'int main(int c, char **v) { volatile unsigned s = 0; for (unsigned i = 0; i < cfg_len; i++)'
  echo '  s += cfg[i] * (i + 1); if (c > 1 && (unsigned)strlen(v[1]) == s) puts("ok"); else printf("usage: %s <cfg>\n", v[0]); return 0; }'
} > "$W/m.c"
gcc -O2 -o "$1" "$W/m.c"
rm -rf "$W"
