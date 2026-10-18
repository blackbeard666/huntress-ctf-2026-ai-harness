#!/bin/sh
# usage: decoder_oracle.sh <bin> <symbolized twin (same build, before strip)> <stored blob len>
# Independent reader: binutils nm (blob VA + FUNC symbols of the twin) + objdump -d -M intel (xrefs annotated
# "# <va>", backward jcc loops, cmp bound, and the byte ops between the loop's byte load and byte store).
bin=$1; twin=${2:-$1}; len=${3:-68}
file -b "$bin"
bva=$(nm "$twin" 2>/dev/null | awk '$3=="hcfg_blob"{print $1}')
echo "blob_va=0x$bva len=$len"
[ -n "$bva" ] || exit 0
objdump -d -M intel --no-show-raw-insn "$bin" | perl -ne '
  BEGIN { $lo = hex(shift @ARGV); $hi = $lo + shift @ARGV; %f = map { /^(\S+) [Tt] (\S+)/ ? (hex($1), $2) : () } `nm $ARGV[0]`; shift @ARGV }
  if (/^\s+([0-9a-f]+):\t(\S+)\s*(.*)$/) { push @ins, [hex $1, $2, $3] }
  END {
    for $i (@ins) { next unless $i->[2] =~ /# ([0-9a-f]+) / && hex($1) >= $lo && hex($1) < $hi && $i->[1] !~ /^j/;
      ($fs) = sort { $b <=> $a } grep { $_ <= $i->[0] } keys %f;
      printf "xref 0x%x %s %s  func=%s\@0x%x\n", $i->[0], $i->[1], $i->[2], $f{$fs} // "none", $fs // 0; }
    for $k (0..$#ins) { $j = $ins[$k]; next unless $j->[1] =~ /^j(?!mp)/ && $j->[2] =~ /^([0-9a-f]+) / && hex($1) <= $j->[0];
      $t = hex($1); @b = grep { $_->[0] >= $t && $_->[0] <= $j->[0] } @ins; next if $j->[0] - $t > 0x200;
      printf "loop 0x%x..0x%x %s\n", $t, $j->[0], $j->[1];
      printf "   %x: %s %s\n", @$_ for @b; }
  }' "$bva" "$len" "$twin"
