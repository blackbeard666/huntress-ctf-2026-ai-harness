#!/bin/sh
# Offline fixture generator for dtrace_* (lib.binary.dynamic_trace_facts). Independent writer: gcc; the D18 member is
# the real gfortran-built challenge program (day18 binary-flow-state single_solve evidence d18--variant-000.elf).
set -e
cd "$(dirname "$0")"
gcc -O1 -s -o dtrace_c_strcmp.bin dtrace_src/dtrace_c.c
gcc -O1 -s -o dtrace_decoy_schema.bin dtrace_src/dtrace_decoy.c
D18=../../../challenges/day18/binary-flow-state/single_solve/work/extracted/evidence/d18--variant-000.elf
[ -f "$D18" ] && cp "$D18" dtrace_d18_fortran.bin || true
head -c 8000 dtrace_d18_fortran.bin > dtrace_decoy_trunc.bin   # cut before the template/env strings
