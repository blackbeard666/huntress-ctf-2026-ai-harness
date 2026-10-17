#!/bin/bash
# usage: wasmhid_oracle.sh file   (wabt wasm-validate / wasm-objdump -x -d + perl; never executes the module)
# Rebuilds linear memory from objdump's Data hexdumps (active "init i32=" segments), memory.init copies of passive
# segments (the 3 i32.const before memory.init in -d) and `i32.const A; i32.const V; i32.store [align] OFF` runs in -d
# (bytes V LE at A+OFF; file offset = the address const's -d offset). Prints:
# valid|invalid | custom sections | <mem addr of HCFG|none> | <file offset: grep -obUa HCFG, else the store's const> |
# <hdr> <crc32(plain)> | <plain>
F="$1"; W=$(mktemp -d)
wasm-validate "$F" >/dev/null 2>&1 && V=valid || V=invalid
wasm-objdump -x "$F" > "$W/x" 2>/dev/null; wasm-objdump -d "$F" > "$W/d" 2>/dev/null
CUS=$(grep -oP '^ - name: "\K[^"]+' "$W/x" | tr '\n' ',' ); [ -z "$CUS" ] && CUS=none
perl -e '
  open X, $ARGV[0]; while (<X>) { if (/^Data\[/) { $d = 1; next } if (/^\S/) { $d = 0 } next unless $d;
    if (/^ - segment\[(\d+)\]/) { $cur = $1; $seg{$cur} = ""; $base{$cur} = /init i32=(\d+)/ ? $1 : undef; next }
    if (/^  - [0-9a-f]+: ((?:[0-9a-f]{2,4} ?)+)/) { ($t = $1) =~ s/ //g; $seg{$cur} .= pack "H*", $t } }
  for $s (sort { $a <=> $b } keys %seg) { next unless defined $base{$s};
    for $j (0 .. length($seg{$s}) - 1) { $m{$base{$s} + $j} = substr($seg{$s}, $j, 1) } }
  open D, $ARGV[1]; @c = ();
  while (<D>) { next unless /^ ([0-9a-f]+): [0-9a-f ]+\| (\S+) ?(.*)$/; ($o, $op, $a) = (hex $1, $2, $3);
    if ($op eq "i32.const") { push @c, [$a & 0xffffffff, $o]; next }
    if ($op eq "i32.store" && @c >= 2) { ($al, $off) = split " ", $a; $A = $c[-2][0] + $off;
      for $j (0 .. 3) { $m{$A + $j} = chr(($c[-1][0] >> 8 * $j) & 255); $src{$A + $j} = $c[-2][1] } }
    if ($op eq "memory.init" && @c >= 3) { ($sg) = split " ", $a; $sg =~ s/\D//g;
      for $j (0 .. $c[-1][0] - 1) { $m{$c[-3][0] + $j} = substr($seg{$sg}, $c[-2][0] + $j, 1) } }
    @c = () }
  @k = sort { $a <=> $b } keys %m; $img = ""; $lo = $k[0]; $prev = $lo - 1; @runs = ();
  for (@k) { if ($_ != $prev + 1) { push @runs, [$lo, $img]; ($lo, $img) = ($_, "") } $img .= $m{$_}; $prev = $_ }
  push @runs, [$lo, $img];
  for (@runs) { $i = index($_->[1], "HCFG"); if ($i >= 0) { $A = $_->[0] + $i; print "$A ", ($src{$A} // "none"), "\n";
    print STDERR substr($_->[1], $i); exit } } print "none none\n"' "$W/x" "$W/d" > "$W/m" 2> "$W/memblob"
read MEM SRC < "$W/m"
OFF=$(grep -obUa HCFG "$F" | head -1 | cut -d: -f1); [ -z "$OFF" ] && OFF=$SRC
B="$W/memblob"; [ "$MEM" = none ] && B="$F"
if [ "$MEM" != none ] || [ "$OFF" != none ]; then
  [ "$MEM" = none ] && S=$OFF || S=0
  H=$(perl -e 'local $/; open F, $ARGV[0]; $d = <F>; $d = substr($d, $ARGV[2]); ($m,$v,$k,$n,$c) = unpack("a4 C C v V", $d);
    $b = join "", map { chr(ord($_) ^ $k) } split //, substr($d, 12, $n); open O, ">$ARGV[1]"; print O $b; print "$m $v $k $n $c"' "$B" "$W/p" "$S")
  PC=$(gzip -c < "$W/p" | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
  echo "$V | $CUS | $MEM | $OFF | $H $PC | $(cat "$W/p")"
else echo "$V | $CUS | none | none"; fi
rm -rf "$W"
