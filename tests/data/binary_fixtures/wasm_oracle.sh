#!/bin/bash
# usage: wasm_oracle.sh file
# file(1) label; wasm-validate (exit 0 = a well-formed module, memory64 enabled); wasm-objdump -x (Memory "i64" flag,
# Data segments: "init i32=/i64=" memory offset + memory-addressed hexdump -> linear-memory address of 'HCFG');
# grep -obUa (file offset of 'HCFG'); perl unpack (little-endian header) + xor, gzip trailer = crc32(body). Prints:
# <file label> | valid|invalid | i64|i32 | <mem addr of HCFG or none> | <file offset of HCFG or none> | <hdr> <crc32(plain)> | <plain>
F="$1"; W=$(mktemp -d)
LABEL=$(file -b "$F")
wasm-validate --enable-memory64 "$F" >/dev/null 2>&1 && V=valid || V=invalid
X=$(wasm-objdump -x "$F" 2>/dev/null)
printf '%s\n' "$X" | grep -q '^ - memory\[.*\bi64\b' && M=i64 || M=i32
MEM=$(printf '%s\n' "$X" | perl -ne 'if (/^Data\[/) { $d = 1; next } if (/^\S/) { $d = 0 } next unless $d;
  if (/^ - segment\[\d+\].*init i(?:32|64)=(-?\d+)/) { ($b, $h) = ($1, ""); push @s, [\$b, \$h]; $cur = \$h; next }
  if (/^ - segment/) { $x = ""; $cur = \$x; next }
  if (/^  - [0-9a-f]+: ((?:[0-9a-f]{2,4} ?)+)/) { ($t = $1) =~ s/ //g; $$cur .= $t }
  END { for (@s) { $i = index(${$_->[1]}, "48434647"); while ($i >= 0 && $i % 2) { $i = index(${$_->[1]}, "48434647", $i + 1) }
        if ($i >= 0) { print ${$_->[0]} + $i / 2; exit } } print "none" }')
OFF=$(grep -obUa HCFG "$F" | head -1 | cut -d: -f1); [ -z "$OFF" ] && OFF=none
if [ "$OFF" != none ]; then
  H=$(perl -e 'local $/; open F, $ARGV[0]; $d = <F>; $d = substr($d, $ARGV[2]); ($m,$v,$k,$n,$c) = unpack("a4 C C v V", $d);
    $b = join "", map { chr(ord($_) ^ $k) } split //, substr($d, 12, $n); open O, ">$ARGV[1]"; print O $b; print "$m $v $k $n $c"' "$F" "$W/p" "$OFF")
  PC=$(gzip -c < "$W/p" | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
  echo "$LABEL | $V | $M | $MEM | $OFF | $H $PC | $(cat "$W/p")"
else echo "$LABEL | $V | $M | $MEM | none"; fi
rm -rf "$W"
