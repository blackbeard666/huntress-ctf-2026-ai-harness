#!/bin/sh
# optimization-equivalence-facts (prebuild): gcc -O0 / -O3 builds of ot_twin.c (-g records the -O flag in
# DW_AT_producer), the D29 Fraternal Twins pair copied from the GM evidence, and a random-bytes decoy (reused).
set -e
gcc -O0 -g -o gf_ot_twin-O0.elf ot_twin.c
gcc -O3 -g -o gf_ot_twin-O3.elf ot_twin.c
D29=../../../../challenges/day29/binary-fraternal-twins/single_solve/work/extracted/evidence
[ -f "$D29/d29--sample-O0.elf" ] && cp "$D29/d29--sample-O0.elf" "$D29/d29--sample-O3.elf" . || true
