#!/bin/sh
# gf-predicate-grammar (prebuild): two zig cc Mach-O members (the ELF / PE members are the existing gf_c_* / gf_pe_*)
cd "$(dirname "$0")/.." || exit 1
Z=${ZIG:-../../../../tools/ziglang/ziglang/zig}
$Z cc -target x86_64-macos -O1 -o pg_macho.bin pg_src/pg_macho.c
$Z cc -target x86_64-macos -O1 -shared -o pg_macho.dylib pg_src/pg_lib.c
