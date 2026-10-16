#!/bin/bash
# usage: stack_push_oracle.sh file -> "<file offset of the first movabs> <magic> <len> <header crc> <json> <gzip crc32>"
# independent reader: the program RUNS natively and write(2)s its stack buffer; perl unpack parses the header; gzip's
# trailer gives crc32(body); binutils objdump -d + readelf -SW map the first movabs in _start to a file offset.
set -e
f="$1"; W=$(mktemp -d)
"$(realpath "$f")" > "$W/b"
addr=$(objdump -d "$f" | grep -m1 -P '\tmovabs\s+\$0x' | awk -F: '{print $1}' | tr -d ' ')
read -r sa so <<< "$(readelf -SW "$f" | awk '{ for (i = 1; i <= NF; i++) if ($i == ".text") print $(i+2), $(i+3) }')"
off=$(( 0x$addr - 0x$sa + 0x$so ))
LC_ALL=C perl -0777 -ne '($m,$v,$k,$l,$c)=unpack("a4CCvV",$_);printf "%s %s %d %d %s ", $ARGV[0], $m, $l, $c, substr($_,12,$l)' "$W/b" | sed "s/^[^ ]*/$off/"
len=$(perl -0777 -ne 'print unpack("x6v",$_)' "$W/b"); tail -c +13 "$W/b" | head -c "$len" | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' '
rm -rf "$W"
