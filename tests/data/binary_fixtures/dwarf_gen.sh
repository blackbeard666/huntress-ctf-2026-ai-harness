#!/bin/bash
# DWARF fixtures (lib.binary.dwarf_facts): gcc 15 -gdwarf-4 / -gdwarf-5 (+ objcopy zstd-compressed .debug_*),
# clang-18 -g (DWARF 5, strx/addrx forms) + zlib-gnu .zdebug_*, a stripped decoy (no .debug_info) and a text decoy.
set -e
cd "$(dirname "$0")"
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
cp dwarf_src.c dwarf_util.c dwarf_cfg.h "$W"/
( cd "$W"
  gcc -O0 -g -gdwarf-4 -fdebug-prefix-map="$W"=/build/beacon dwarf_src.c dwarf_util.c -o g4
  gcc -O0 -g -gdwarf-5 -fdebug-prefix-map="$W"=/build/beacon dwarf_src.c dwarf_util.c -o g5
  objcopy --compress-debug-sections=zstd g5 g5z
  clang-18 -O0 -g -fdebug-prefix-map="$W"=/src/clang dwarf_src.c dwarf_util.c -o c18
  objcopy --compress-debug-sections=zlib-gnu c18 c18z
  strip --strip-debug g4 -o g4s )
cp "$W"/g4 dwarf_gcc_dwarf4.bin; cp "$W"/g5z dwarf_gcc_dwarf5_zstd.bin
cp "$W"/c18 dwarf_clang18_dwarf5.bin; cp "$W"/c18z dwarf_clang18_zdebug.bin
cp "$W"/g4s dwarf_decoy_stripdebug.bin
printf 'DW_AT_producer GNU C17 DW_TAG_subprogram main .debug_info\n' > dwarf_decoy_text.bin
