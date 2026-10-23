#!/bin/sh
# Offline fixture generator for predbr_* (lib.binary.predicate_branch_facts). Independent writer: gcc (no harness code).
set -e
cd "$(dirname "$0")"
gcc -O0 -no-pie -o predbr_c_gates.bin predbr_src/predbr_gates.c                    # symbols kept, non-PIE, PLT
gcc -O2 -fPIE -pie -s -o predbr_c_memcmp_pie.bin predbr_src/predbr_memcmp.c       # stripped PIE, main via _start
gcc -O1 -s -fno-plt -o predbr_c_gates_noplt.bin predbr_src/predbr_gates.c          # call [rip+GOT], stripped
gcc -O1 -s -o predbr_decoy_noenv.bin predbr_src/predbr_decoy_noenv.c               # decoy: no getenv import
cp dtrace_c_strcmp.bin predbr_dtrace_c_strcmp.bin                                  # earlier gcc dtrace fixture
head -c 3000 predbr_c_gates.bin > predbr_decoy_trunc.bin                           # decoy: truncated ELF
printf 'HUNTRESS_HOST_MODEL analysis sandbox workstation "branch":"decoy"\n' > predbr_decoy_text.bin
for f in predbr_*.bin; do python3 predbr_oracle.py "$f" > "${f%.bin}.json"; done
