#!/bin/sh
# reachability fixtures: C twins built with gcc; the jars are the GM D24/D25 evidence.zip role members (unchanged bytes)
set -e; cd "$(dirname "$0")"
gcc -O0 -fno-stack-protector -o reach_c_gate_pie.bin reach_gate.c
gcc -O0 -fno-stack-protector -fcf-protection=none -no-pie -o reach_c_gate_nopie.bin reach_gate.c
gcc -O0 -fno-stack-protector -o reach_c_decoy_nogate.bin reach_nogate.c
printf 'PK\003\004 not really a jar\n' > reach_decoy_text.bin
