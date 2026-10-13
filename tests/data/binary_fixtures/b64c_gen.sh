#!/bin/bash
# usage: gen.sh out.bin stored_alphabet encode_alphabet json prefix
set -e
STD='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
P="$4"
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > blob.raw
{ head -c 2048 /dev/zero | tr '\0' '\220'; printf '%s%s\0' "$5" "$2"; head -c 1500 /dev/zero | tr '\0' '\314';
  base64 -w0 blob.raw | tr -d '=' | tr "$STD" "$3"; printf '\0'; head -c 700 /dev/zero; } > "$1"
