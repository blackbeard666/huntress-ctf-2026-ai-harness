#!/bin/bash
# usage: rotb64_gen.sh out.bin wrap_cols tr_from tr_to rev(0|1) json [crc_xor]
# blob: printf header + crc32 from the gzip trailer; text: coreutils base64 -w <cols> | tr <from> <to> | [util-linux /usr/bin/rev]
set -e
P="$6"
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
CRC=$(printf %08x $(( 0x$CRC ^ ${7:-0} )))
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > blob.raw
{ head -c 1800 /dev/zero | tr '\0' '\220'; printf 'usage: %%s <cfg>\0';
  head -c 700 /dev/zero | tr '\0' '\314';
  if [ "$5" = 1 ]; then base64 -w "$2" blob.raw | tr "$3" "$4" | /usr/bin/rev; else base64 -w "$2" blob.raw | tr "$3" "$4"; fi;
  printf '\0'; head -c 900 /dev/zero; } > "$1"
rm -f blob.raw
