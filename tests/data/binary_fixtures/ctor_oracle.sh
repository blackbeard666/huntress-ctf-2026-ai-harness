#!/bin/bash
# usage: ctor_oracle.sh file -> "<file offset of enc[]> <magic> <len> <header crc> <json> <gzip crc32 of body>"
# independent reader: the program itself RUNS (natively, or qemu-aarch64 -L /usr/aarch64-linux-gnu) so the dynamic
# loader runs its .init_array constructor, then dumps the decoded buffer; perl unpack parses the header; gzip's trailer
# gives crc32(body). Offset: binutils nm gives the address of the stored encoded array `enc`, readelf -SW maps it to a
# file offset through the section that holds it.
set -e
f="$1"; W=$(mktemp -d)
mach=$(readelf -h "$f" | awk -F: '/Machine/ {print $2}')
case "$mach" in
  *AArch64*) qemu-aarch64 -L /usr/aarch64-linux-gnu "$f" dump > "$W/b" ;;
  *)         "$(realpath "$f")" dump > "$W/b" ;;
esac
NM=nm; case "$mach" in *AArch64*) NM=aarch64-linux-gnu-nm ;; esac
addr=$($NM "$f" | awk '$3 == "enc" {print $1}')
read -r sa so <<< "$(readelf -SW "$f" | sed 's/^ *\[ *[0-9]*\]//' | awk -v a=$((16#$addr)) '
  NF >= 6 && $3 ~ /^[0-9a-f]+$/ && $5 ~ /^[0-9a-f]+$/ { s = strtonum("0x" $3); z = strtonum("0x" $5);
    if (s && a >= s && a < s + z) print $3, $4 }')"
off=$(( 0x$addr - 0x$sa + 0x$so ))
LC_ALL=C perl -0777 -ne '($m,$v,$k,$l,$c)=unpack("a4CCvV",$_);printf "%s %s %d %d %s ", $ARGV[0], $m, $l, $c, substr($_,12,$l)' "$W/b" | sed "s/^[^ ]*/$off/"
len=$(perl -0777 -ne 'print unpack("x6v",$_)' "$W/b"); tail -c +13 "$W/b" | head -c "$len" | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' '
rm -rf "$W"
