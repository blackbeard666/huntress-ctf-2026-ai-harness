#!/bin/bash
# usage: sstrip_oracle.sh file.elf -- independent readers only: file -b, GNU readelf -hW/-SW/-lW, grep -obUa, perl unpack + xor, gzip crc
F="$1"
file -b "$F"
readelf -hW "$F" 2>&1 | grep -E 'Class:|Data:|Type:|Machine:|Entry point|Number of program headers|Failed'
echo "interp: $(readelf -lW "$F" 2>/dev/null | grep -c '^  INTERP')"
SH=$(readelf -SW "$F" 2>/dev/null)
echo "sections: $(printf '%s\n' "$SH" | perl -ne 'print "$1 " if /^\s+\[\s*(\d+)\]\s/ && $1 > 0' | wc -w)"
echo "names: $(printf '%s\n' "$SH" | perl -ne 'print "$2 " if /^\s+\[\s*(\d+)\]\s+(\S+)\s+[A-Z_]+\s/ && $1 > 0 && $2 ne "<no-strings>"')"
echo "symtab: $(printf '%s\n' "$SH" | grep -c ' SYMTAB ')"
for O in $(grep -obUa HCFG "$F" | cut -d: -f1); do
  perl -e 'open F, "<", $ARGV[0]; binmode F; seek F, $ARGV[1], 0; read F, $h, 12; ($m,$v,$k,$n,$c) = unpack "a4 C C v V", $h; read F, $b, $n;
    $p = join "", map { chr(ord($_) ^ $k) } split //, $b; print "$ARGV[1] $m $v $k $n $c\n$p\n"' "$F" "$O" > /tmp/sstrip_o.$$
  C2=$(tail -n +2 /tmp/sstrip_o.$$ | head -c -1 | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
  echo "blob@$(head -1 /tmp/sstrip_o.$$) gzipcrc=$C2 | $(tail -n +2 /tmp/sstrip_o.$$)"
  printf '%s\n' "$SH" | perl -ne 'print "in section: $1\n" if /^\s+\[\s*\d+\]\s+(\S+)\s+([A-Z_]+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)/ && $2 ne "NOBITS" && hex($3) <= '"$O"' && '"$O"' < hex($3)+hex($4)'
done
rm -f /tmp/sstrip_o.$$
