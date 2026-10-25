#!/bin/sh
# stw_gen.sh OUTDIR: stripped twin fixtures (gcc -O2, strip -s; the *_sym builds are the oracle's symbol source).
set -e; O=${1:-.}; S=$(dirname "$0")/stw_src.c
gcc -O2 -no-pie -o $O/stw_nopie_bounds_a_sym $S && gcc -O2 -no-pie -DFIXED -o $O/stw_nopie_bounds_b_sym $S
gcc -O2 -o $O/stw_pie_const_a_sym $S && gcc -O2 -DMIXK=0x5bd1e997 -o $O/stw_pie_const_b_sym $S
gcc -O2 -o $O/stw_decoy_same_b_sym $S; cp $O/stw_pie_const_a_sym $O/stw_decoy_same_a_sym
for t in nopie_bounds pie_const decoy_same; do for s in a b; do
  strip -s -o $O/stw_${t}_$s.bin $O/stw_${t}_${s}_sym; done; done
mv $O/stw_nopie_bounds_b_sym $O/stw_nopie_bounds_sym.bin; mv $O/stw_pie_const_a_sym $O/stw_pie_const_sym.bin
rm -f $O/stw_*_sym
printf 'this is not an ELF twin\n' > $O/stw_decoy_text_a.bin; cp $O/stw_decoy_text_a.bin $O/stw_decoy_text_b.bin
