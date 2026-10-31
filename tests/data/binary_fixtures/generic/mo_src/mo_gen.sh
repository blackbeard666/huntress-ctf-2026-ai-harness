#!/bin/sh
# gf-macho (prebuild): zig cc Mach-O members (x86_64 -O1, arm64 -g with debug-map stabs, MH_OBJECT, plain decoy) and an
# llvm-lipo fat (x86_64 + arm64) member. Needs tools/ziglang + llvm-lipo-18.
cd "$(dirname "$0")/.." || exit 1
Z=${ZIG:-../../../../tools/ziglang/ziglang/zig}
$Z cc -target x86_64-macos -O1 -o mo_x64.bin mo_src/mo.c
$Z cc -target aarch64-macos -O0 -g -o mo_arm64_g.bin mo_src/mo.c
$Z cc -target x86_64-macos -O1 -c -o mo_obj.o mo_src/mo.c
$Z cc -target aarch64-macos -O1 -o mo_plain.bin mo_src/plain.c
llvm-lipo-18 -create mo_x64.bin mo_arm64_g.bin -output mo_fat.bin
