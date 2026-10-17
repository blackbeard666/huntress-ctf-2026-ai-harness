#!/bin/bash
# usage: ebpf_oracle.sh file.o -- independent readers only: file -b, GNU readelf -h/-S/-s/-p, grep -obUa, perl unpack + xor, gzip crc
F="$1"
file -b "$F"
readelf -h "$F" | grep -E 'Type:|Machine:|Entry point'
echo "programs: $(readelf -SW "$F" | perl -ne 'print "$1 " if /\]\s+(\S+)\s+PROGBITS\s+\S+\s+\S+\s+([0-9a-f]+)\s+\S+\s+(\S*X\S*)/ && hex($2) && $1 ne ".text"')"
echo "license: $(readelf -p license "$F" 2>/dev/null | sed -n 's/.*\]  //p')"
for S in .maps maps; do
  IDX=$(readelf -SW "$F" | perl -ne "print \$1 if /\[\s*(\d+)\]\s+\Q$S\E\s/")
  [ -n "$IDX" ] && echo "maps($S): $(readelf -sW "$F" | awk -v i="$IDX" '$7==i && $4=="OBJECT"{print $8}' | tr '\n' ' ')"
done
echo "sections: $(readelf -SW "$F" | perl -ne 'print "$1 " if /\]\s+(\S+)\s+[A-Z_]+\s/')"
for O in $(grep -obUa HCFG "$F" | cut -d: -f1); do
  perl -e 'open F, "<", $ARGV[0]; binmode F; seek F, $ARGV[1], 0; read F, $h, 12; ($m,$v,$k,$n,$c) = unpack "a4 C C v V", $h; read F, $b, $n;
    $p = join "", map { chr(ord($_) ^ $k) } split //, $b; print "$ARGV[1] $m $v $k $n $c\n$p\n"' "$F" "$O" > /tmp/ebpf_o.$$
  C2=$(tail -n +2 /tmp/ebpf_o.$$ | head -c -1 | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
  echo "blob@$(head -1 /tmp/ebpf_o.$$) gzipcrc=$C2 | $(tail -n +2 /tmp/ebpf_o.$$)"
done
rm -f /tmp/ebpf_o.$$
