#!/bin/bash
# usage: march_oracle.sh file.o
# GNU readelf -h (Machine / Data) + -SW (.hcfg sh_offset); llvm-objcopy-18 dumps .hcfg; perl unpack reads the header in
# the ELF's byte order (n/N big, v/V little) and un-xors the body; gzip trailer = crc32(body). Prints:
# <readelf Machine> | <e_machine decimal> | <endian> | <.hcfg offset> | <ver> <key> <len> <crc> <crc32(plain)> | <plain>
set -e
F="$1"; W=$(mktemp -d)
M=$(readelf -h "$F" | sed -n 's/^ *Machine: *//p')
D=$(readelf -h "$F" | grep -q 'big endian' && echo big || echo little)
EM=$(od -An -j18 -N2 -tx1 "$F" | tr -d ' ')
[ $D = big ] && EM=$((16#$EM)) || EM=$((16#${EM:2:2}${EM:0:2}))
OFF=$(readelf -SW "$F" | awk '$2==".hcfg"{print $5} $3==".hcfg"{print $6}' | head -1)
llvm-objcopy-18 -O binary --only-section=.hcfg "$F" "$W/s"
H=$(perl -e 'local $/; open F, $ARGV[0]; $d = <F>; ($m,$v,$k,$n,$c) = unpack($ARGV[1] eq "big" ? "a4 C C n N" : "a4 C C v V", $d);
  $b = join "", map { chr(ord($_) ^ $k) } split //, substr($d, 12, $n); open O, ">$ARGV[2]"; print O $b; print "$m $v $k $n $c"' "$W/s" "$D" "$W/p")
PC=$(gzip -c < "$W/p" | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
echo "$M | $EM | $D | $((16#$OFF)) | $H $PC | $(cat "$W/p")"
rm -rf "$W"
