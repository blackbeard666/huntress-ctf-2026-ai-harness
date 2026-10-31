#!/bin/sh
# toolchain-attribution-verdicts: one C file built by gcc / clang-18 / zig cc / aarch64-linux-gnu-gcc (+ strip variants)
set -e
cd "$(dirname "$0")"
Z=${ZIG:-../../../../tools/pyziglang/ziglang/zig}
B="-Wl,--build-id=none"
gcc -g -O1 $B -o ta_gcc_g.elf gf_toolchain.c                                  # gcc, DWARF, dynamic PIE, glibc, bfd
clang-18 -g -O1 -no-pie $B -o ta_clang18_g.elf gf_toolchain.c                 # clang 18, DWARF, dynamic non-PIE
gcc -O1 -static -s $B -o ta_gcc_static_s.elf gf_toolchain.c                   # static glibc, stripped, .comment kept
aarch64-linux-gnu-gcc -g -O1 -static $B -o ta_a64_static_g.elf gf_toolchain.c # aarch64 static glibc + DWARF
"$Z" cc -target x86_64-linux-musl -O1 -o ta_zig_musl.elf gf_toolchain.c        # zig cc: clang banner + LLD, static musl
gcc -O1 $B -o ta_nobanner.elf gf_toolchain.c && strip -s -R .comment ta_nobanner.elf   # decoy: no banner, no DWARF
