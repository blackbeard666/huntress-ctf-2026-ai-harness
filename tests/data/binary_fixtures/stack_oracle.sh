#!/bin/bash
# usage: stack_oracle.sh file -> "<file offset of first mov-imm 'H'> <magic> <len> <header crc> <json> <gzip crc32 of body>"
# independent reader: the program itself RUNS (natively, or qemu-aarch64 -L /usr/aarch64-linux-gnu) and dumps the buffer
# it built; perl unpack parses the header; gzip's trailer gives crc32(body). Offset: binutils objdump -d finds the first
# `movb $0x48,` (x86-64) / `mov wN, #0x48` (AArch64) in main, readelf -SW maps its address to a file offset via .text.
set -e
f="$1"; W=$(mktemp -d)
mach=$(readelf -h "$f" | awk -F: '/Machine/ {print $2}')
case "$mach" in
  *AArch64*) qemu-aarch64 -L /usr/aarch64-linux-gnu "$f" dump > "$W/b"
             addr=$(aarch64-linux-gnu-objdump -d "$f" | sed -n '/<main>:/,/^$/p' | grep -m1 -P '\tmov\tw\d+, #0x48\b' | awk -F: '{print $1}' | tr -d ' ') ;;
  *)         "$(realpath "$f")" dump > "$W/b"
             addr=$(objdump -d "$f" | sed -n '/<main>:/,/^$/p' | grep -m1 -P '\tmovb\s+\$0x48,' | awk -F: '{print $1}' | tr -d ' ') ;;
esac
read -r sa so <<< "$(readelf -SW "$f" | awk '{ for (i = 1; i <= NF; i++) if ($i == ".text") print $(i+2), $(i+3) }')"
off=$(( 0x$addr - 0x$sa + 0x$so ))
LC_ALL=C perl -0777 -ne '($m,$v,$k,$l,$c)=unpack("a4CCvV",$_);printf "%s %s %d %d %s ", $ARGV[0], $m, $l, $c, substr($_,12,$l)' "$W/b" | sed "s/^[^ ]*/$off/"
len=$(perl -0777 -ne 'print unpack("x6v",$_)' "$W/b"); tail -c +13 "$W/b" | head -c "$len" | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' '
rm -rf "$W"
