#!/bin/bash
# Generator for the switch_* fixtures (lib.binary.switch_tables). Run from tests/data/binary_fixtures/.
# Compilers: gcc 13 (x86-64), clang-18, aarch64-linux-gnu-gcc; strip; head. Sources: switch_src_sw.c (7 cases 3..10
# with a gap at 7 + default), switch_src_sw2.c (12 dense cases 2..13 + default). The d18 member is a copy of
# gfortran_d18_flow_v000.bin (the D18 "Flow State" gfortran SELECT CASE shape).
set -e
gcc -O2 -fno-inline -o switch_gcc_pie.bin switch_src_sw.c
gcc -O2 -static -no-pie -o switch_gcc_static.bin switch_src_sw.c
clang-18 -O2 -o switch_clang18_pie.bin switch_src_sw.c
gcc -O2 -fcf-protection=none -fno-pie -no-pie -o switch_gcc_nopie_abs.bin switch_src_sw.c
aarch64-linux-gnu-gcc -O2 -o switch_a64_gcc.bin switch_src_sw2.c
aarch64-linux-gnu-gcc -O2 -static -o switch_a64_gcc_static.bin switch_src_sw2.c
gcc -O2 -o switch_gcc_stripped.bin switch_src_sw2.c && strip -s switch_gcc_stripped.bin
cp gfortran_d18_flow_v000.bin switch_d18_fortran.bin
gcc -O2 -fno-jump-tables -o switch_decoy_nojt.bin switch_src_sw.c          # decoy: compare tree, no table
head -c 4000 switch_gcc_pie.bin > switch_decoy_trunc.bin                    # decoy: ELF header, code cut off
head -c 3000 switch_src_sw.c > switch_decoy_text.bin                        # decoy: C text renamed .bin
