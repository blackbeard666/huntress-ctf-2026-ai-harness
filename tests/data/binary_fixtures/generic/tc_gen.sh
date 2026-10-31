#!/bin/sh
# theme-backfill-d18-d28-fields: D27 per-role toolchain members (gcc + GNU as; oracles = binutils readelf)
set -e
cd "$(dirname "$0")"
# gcc role: DWARF + DT_GNU_HASH only
gcc -g -O1 -Wl,--hash-style=gnu -Wl,--build-id=none -o gf_tc_gcc.elf gf_toolchain.c
# tcc-like role: stabs (GNU as --gstabs over gcc's asm) + SysV DT_HASH only
gcc -O1 -S -o /tmp/gf_tc_stabs.$$.s gf_toolchain.c
as --gstabs -o /tmp/gf_tc_stabs.$$.o /tmp/gf_tc_stabs.$$.s
gcc -Wl,--hash-style=sysv -Wl,--build-id=none -o gf_tc_stabs.elf /tmp/gf_tc_stabs.$$.o
rm -f /tmp/gf_tc_stabs.$$.s /tmp/gf_tc_stabs.$$.o
# no debug info, both hash tables
gcc -O1 -Wl,--hash-style=both -Wl,--build-id=none -o gf_tc_both.elf gf_toolchain.c
