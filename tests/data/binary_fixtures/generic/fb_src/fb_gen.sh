#!/usr/bin/env bash
# gf-func-body members: gcc -O2 / -O0 x86-64 executables, strip -s, gcc -m32 -c (ET_REL i386 object)
set -euo pipefail
cd "$(dirname "$0")"
gcc -O2 -fcf-protection=none -fno-asynchronous-unwind-tables -o ../fb_d01.elf fb.c
strip -s -o ../fb_d01_stripped.elf ../fb_d01.elf
gcc -O0 -fcf-protection=full -fno-asynchronous-unwind-tables -o ../fb_d01_O0.elf fb.c
gcc -m32 -O2 -fcf-protection=none -fno-asynchronous-unwind-tables -c -o ../fb_d01_m32.o fb.c
