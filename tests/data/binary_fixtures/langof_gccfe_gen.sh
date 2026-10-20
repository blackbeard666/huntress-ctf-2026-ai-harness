#!/usr/bin/env bash
# language_of fixtures for GCC front ends gm2 (Modula-2) + gcobol (GCC 15 COBOL), built by the real Ubuntu 15.2.0-16
# compilers extracted (no root) from `apt-get download gm2-15-x86-64-linux-gnu libgm2-20 libgm2-15-dev
# gcobol-15-x86-64-linux-gnu libgcobol-15-dev libgcobol1` + `dpkg -x` into tools/gccfe/root (system gcc-15/g++-15 base).
# usage (repo root): bash tests/data/binary_fixtures/langof_gccfe_gen.sh
set -euo pipefail
OUT=$(cd "$(dirname "$0")" && pwd); R=$(cd "$OUT/../../.." && pwd)/tools/gccfe/root
W=${TMPDIR:-/tmp}/langof_gccfe; rm -rf "$W"; mkdir -p "$W"; cd "$W"
for f in /usr/lib/gcc/x86_64-linux-gnu/15/*; do b=$(basename "$f")
  [ -e "$R/usr/lib/gcc/x86_64-linux-gnu/15/$b" ] || ln -s "$f" "$R/usr/lib/gcc/x86_64-linux-gnu/15/$b"; done
FL="-fno-use-linker-plugin -B$R/usr/libexec/gcc/x86_64-linux-gnu/15/ -B$R/usr/lib/gcc/x86_64-linux-gnu/15/ -L$R/usr/lib/x86_64-linux-gnu"
printf 'MODULE hello;\nFROM StrIO IMPORT WriteString, WriteLn;\nBEGIN\n  WriteString("hello modula-2"); WriteLn\nEND hello.\n' > hello.mod
"$R/usr/bin/x86_64-linux-gnu-gm2-15" $FL -O2 -o "$OUT/langof_gm2_pim_O2.bin" hello.mod
printf 'MODULE cfg;\nIMPORT STextIO;\nBEGIN\n  STextIO.WriteString("iso modula-2"); STextIO.WriteLn\nEND cfg.\n' > cfg.mod
"$R/usr/bin/x86_64-linux-gnu-gm2-15" $FL -fiso -O0 -o cfg cfg.mod && strip -s -o "$OUT/langof_gm2_iso_stripped.bin" cfg
printf '       IDENTIFICATION DIVISION.\n       PROGRAM-ID. HELLO.\n       PROCEDURE DIVISION.\n           DISPLAY "hello gcobol".\n           STOP RUN.\n' > hello.cob
"$R/usr/bin/x86_64-linux-gnu-gcobol-15" $FL -O2 -o "$OUT/langof_gcobol_O2.bin" hello.cob
"$R/usr/bin/x86_64-linux-gnu-gcobol-15" $FL -O0 -o hc hello.cob && strip -s -o "$OUT/langof_gcobol_stripped.bin" hc
# decoy: plain C whose string literal names the gm2/gcobol runtime symbols (not linked against them)
printf '#include <stdio.h>\nint main(void){puts("m2pim_M2RTS_ConstructModules libm2pim.so.20 __gg__init_program_state libgcobol.so.1");return 0;}\n' > d.c
gcc -O2 -o "$OUT/langof_decoy_c_gccfe_cues.bin" d.c
printf 'gm2 _M2RTS_ConstructModules libgcobol.so.1 __gg__init_program_state -- notes, not an ELF\n' > "$OUT/langof_decoy_gccfe_text.bin"
