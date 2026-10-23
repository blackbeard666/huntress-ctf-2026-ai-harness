#!/bin/bash
# usage: kmod_oracle.sh file -- independent readers only: file -b, GNU readelf -h/-S/-s/-p/-x, kmod modinfo (on a .ko
# copy: it prints .modinfo REVERSED, so section order comes from readelf -p), modprobe --dump-modversions,
# grep -obUa, perl unpack + xor, gzip crc
F="$1"; T=$(mktemp -d); cp "$F" "$T/m.ko"
file -b "$F"
readelf -h "$F" 2>&1 | grep -E 'Type:|Machine:|Entry point|Error'
echo "modinfo(section order): $(readelf -p .modinfo "$F" 2>/dev/null | sed -n 's/^ *\[ *[0-9a-f]*\]  //p' | tr '\n' '|')"
echo "kmod modinfo: $(modinfo "$T/m.ko" 2>&1 | grep -v '^filename:' | tr '\n' '|')"
echo "modversions: $(modprobe --dump-modversions "$T/m.ko" 2>&1 | tr '\t\n' ' |')"
echo "ksymtab: $(readelf -sW "$F" 2>/dev/null | awk '$4!="SECTION" && $8 ~ /^__ksymtab_/ {print $7":"$8}' | tr '\n' ' ')"
echo "  in sections: $(readelf -SW "$F" 2>/dev/null | grep -o '_*ksymtab[_a-z]*+[A-Za-z0-9_]*' | tr '\n' ' ')"
echo "init/cleanup: $(readelf -sW "$F" 2>/dev/null | awk '$4=="FUNC" {print $7"/"$2":"$8}' | tr '\n' ' ')"
echo "this_module: $(readelf -x .gnu.linkonce.this_module "$F" 2>/dev/null | sed -n '3,6p' | cut -c 49- | tr -d '\n')"
for O in $(grep -obUa HCFG "$F" | cut -d: -f1); do
  perl -e 'open F, "<", $ARGV[0]; binmode F; seek F, $ARGV[1], 0; read F, $h, 12; ($m,$v,$k,$n,$c) = unpack "a4 C C v V", $h; read F, $b, $n;
    $p = join "", map { chr(ord($_) ^ $k) } split //, $b; print "$ARGV[1] $m $v $k $n $c\n$p\n"' "$F" "$O" > "$T/o"
  C2=$(tail -n +2 "$T/o" | head -c -1 | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
  echo "blob@$(head -1 "$T/o") gzipcrc=$C2 | $(tail -n +2 "$T/o")"
done
readelf -SW "$F" 2>/dev/null | perl -ne 'print "section $1 off ", hex($2), "\n" if /\]\s+(\.r?o?data)\s+\S+\s+\S+\s+([0-9a-f]+)/'
rm -rf "$T"
