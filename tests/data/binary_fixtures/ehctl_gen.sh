#!/bin/bash
# Exception/signal-handler fixtures (independent writers: g++/gcc; -Wa,-L twins keep .L labels for the oracle only).
set -e; cd "$(dirname "$0")"; T=$(mktemp -d)
g++ -O1 -fno-pie -no-pie -o ehctl_cxx_nopie.bin ehctl_cxx.cpp; g++ -O1 -fno-pie -no-pie -Wa,-L -o $T/cxx_nopie.lbl ehctl_cxx.cpp
g++ -O1 -fno-pie -S -o $T/cxx_nopie.s ehctl_cxx.cpp
g++ -O2 -fPIE -pie -o ehctl_cxx_pie_cold.bin ehctl_cxx.cpp; g++ -O2 -fPIE -pie -Wa,-L -o $T/cxx_pie_cold.lbl ehctl_cxx.cpp
g++ -O2 -fPIE -S -o $T/cxx_pie_cold.s ehctl_cxx.cpp
gcc -O0 -o ehctl_sig_o0.bin ehctl_sig.c; gcc -O2 -fno-plt -o ehctl_sig_o2_noplt.bin ehctl_sig.c
gcc -O1 -o ehctl_decoy_plain.bin ehctl_plain.c
printf 'not an elf at all, just text\n%.0s' {1..10} > ehctl_decoy_text.bin
echo "$T"
