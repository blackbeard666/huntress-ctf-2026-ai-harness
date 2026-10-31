#!/bin/sh
# Pair facts of the optimization twins vs cmp(1): diff byte count, first differing offset (0-based).
# python3 side calls lib.binary.generic_field with the two-member group, as the day solver does.
cd "$(dirname "$0")"
for p in "d29--sample-O0.elf d29--sample-O3.elf"; do
  set -- $p
  n=$(cmp -l "$1" "$2" | wc -l); f=$(( $(cmp "$1" "$2" | grep -oE 'byte [0-9]+' | cut -d' ' -f2) - 1 ))
  got=$(cd ../../../.. && python3 -c "
import sys; from lib.binary import generic_field as g
d='tests/data/binary_fixtures/generic/'; a=open(d+'$1','rb').read(); b=open(d+'$2','rb').read(); G=[('$1',a),('$2',b)]
print(g(a,'diff_byte_count','',group=G), g(a,'first_diff_offset','',group=G), g(a,'semantically_equivalent','',group=G))")
  echo "cmp: $n $f true | lib: $got"; [ "$got" = "$n $f true" ] || exit 1
done
