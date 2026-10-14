#!/bin/bash
# usage: int_oracle.sh file layout -> "<file offset> <magic> <len> <header crc> <json> <gzip crc32 of body>"
# independent reader: GNU grep -obUaP finds the stored magic, od -tu4/-tu8/-tu1 reads the elements, xxd -r -p re-packs
# big-endian words, perl pack/unpack rebuilds the bytes and parses the header, gzip's trailer gives crc32(body).
set -e
f="$1"; W=$(mktemp -d)
case "$2" in
  u32arr) off=$(LC_ALL=C grep -obUaP 'H\x00\x00\x00C\x00\x00\x00F\x00\x00\x00G' "$f" | head -1 | cut -d: -f1)
          od -An -tu4 -v -j "$off" "$f" | tr -s ' \n' '\n' | grep . | awk '$1>255{exit} {print}' | perl -ne 'print pack("C", $_)' > "$W/b" ;;
  u64arr) off=$(LC_ALL=C grep -obUaP 'H\x00{7}C\x00{7}F\x00{7}G' "$f" | head -1 | cut -d: -f1)
          od -An -tu8 -v -j "$off" "$f" | tr -s ' \n' '\n' | grep . | awk '$1>255{exit} {print}' | perl -ne 'print pack("C", $_)' > "$W/b" ;;
  u32words) off=$(LC_ALL=C grep -obUa 'GFCH' "$f" | head -1 | cut -d: -f1)
          od -An -tx4 -v -j "$off" "$f" | tr -s ' \n' '\n' | grep . | xxd -r -p > "$W/b" ;;
  u16words) off=$(LC_ALL=C grep -obUa 'CHGF' "$f" | head -1 | cut -d: -f1)
          od -An -tx2 -v -j "$off" "$f" | tr -s ' \n' '\n' | grep . | xxd -r -p > "$W/b" ;;
  decimal) off=$(LC_ALL=C grep -obUa '72,67,70,71' "$f" | head -1 | cut -d: -f1)
          tail -c +$((off+1)) "$f" | LC_ALL=C grep -aoE '^[0-9,]+' | head -1 | tr ',' '\n' | perl -ne 'print pack("C", $_)' > "$W/b" ;;
esac
LC_ALL=C perl -0777 -ne '($m,$v,$k,$l,$c)=unpack("a4CCvV",$_);printf "%s %s %d %d %s ", $ARGV[0], $m, $l, $c, substr($_,12,$l)' "$W/b" | sed "s/^[^ ]*/$off/"
len=$(perl -0777 -ne 'print unpack("x6v",$_)' "$W/b"); tail -c +13 "$W/b" | head -c "$len" | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' '
rm -rf "$W"
