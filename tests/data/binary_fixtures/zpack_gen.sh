#!/bin/bash
# usage: zpack_gen.sh out.bin mode json [badcrc]
# blob: printf header + crc32 from the gzip trailer; stream/text: coreutils/xz/bzip2/gzip/zlib-flate (never lib.binary)
set -e
P="$3"
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
[ -n "$4" ] && CRC=deadbeef
T=$(mktemp)
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$T"
case "$2" in
  b64-gzip)  S() { gzip -9n -c "$T" | base64 -w0; } ;;
  b64-bz2)   S() { bzip2 -9 -c "$T" | base64 -w76; } ;;
  b64-xz)    S() { xz -c "$T" | base64 -w0; } ;;
  hex-zlib)  S() { zlib-flate -compress < "$T" | xxd -p -c0; } ;;
  hex-gzipU) S() { { printf 'junk-prefix-'; cat "$T"; } | gzip -6n -c | xxd -p -c0 | tr a-f A-F; } ;;
  raw-xz)    S() { xz -6 -c "$T"; } ;;
  raw-bz2)   S() { bzip2 -c "$T"; } ;;
  raw-lzma)  S() { xz --format=lzma -c "$T"; } ;;
esac
{ head -c 4096 /dev/urandom | tr -d 'HCFGBZ\135\170\037\375' | head -c 3000; printf 'GetConfig\0\0\0'; S; printf '\0';
  head -c 900 /dev/zero; } > "$1"
rm -f "$T"
