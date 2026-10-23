#!/bin/bash
# Anti-disassembly fixtures: gcc -c objects whose functions are written as top-level inline asm with .byte junk,
# a jz+jnz pair to one target, an overlapping `eb ff c0` jump into its own instruction and a call $+5; pop; push; ret
# fake return; plus a -no-pie link of all three (ET_EXEC) and a clean decoy. Built here, run only by adis_oracle.py.
# usage (from this dir): bash adis_gen.sh
set -e
T=${TMPDIR:-/tmp}/adis; mkdir -p "$T"
cat > "$T/jzjnz.c" <<'C'
__asm__(".text\n.globl check_key\n.type check_key,@function\ncheck_key:\n"
        "  mov eax, 7\n  or eax, 1\n  jz 1f\n  jnz 1f\n  .byte 0xe8, 0x8b\n"
        "1:\n  mov eax, 0x1337\n  add eax, 0x11\n  ret\n.size check_key, .-check_key\n"
        ".globl skip_junk\n.type skip_junk,@function\nskip_junk:\n"
        "  xor eax, eax\n  jmp 2f\n  .byte 0xe9, 0x41, 0x42\n2:\n  mov eax, 0xc0de\n  ret\n.size skip_junk, .-skip_junk\n");
int plain_add(int a, int b) { return a + b; }
C
cat > "$T/ebff.c" <<'C'
__asm__(".text\n.globl get_flag\n.type get_flag,@function\nget_flag:\n"
        "  mov eax, 0x41\n  .byte 0xeb, 0xff, 0xc0\n  add eax, 0x100\n  ret\n.size get_flag, .-get_flag\n");
int helper(int x) { return x * 3; }
C
cat > "$T/callpop.c" <<'C'
__asm__(".text\n.globl decode_it\n.type decode_it,@function\ndecode_it:\n"
        "  call 1f\n1:\n  pop rax\n  add rax, 3f - 1b\n  push rax\n  ret\n  .byte 0x0f, 0x0b, 0xe8, 0x90\n"
        "3:\n  mov eax, 0xbeef\n  sub eax, 0xf\n  ret\n.size decode_it, .-decode_it\n");
C
cat > "$T/clean.c" <<'C'
int scale(int x) { return x * 5 + 1; }
int pick(int a) { if (a > 3) return 0x2a; return a - 1; }
C
cat > "$T/main.c" <<'C'
#include <stdio.h>
int check_key(void); int skip_junk(void); int get_flag(void); int decode_it(void);
int main(void) { printf("check_key=%d skip_junk=%d get_flag=%d decode_it=%d\n", check_key(), skip_junk(), get_flag(),
                        decode_it()); return 0; }
C
for n in jzjnz ebff callpop clean; do gcc -O1 -masm=intel -fno-asynchronous-unwind-tables -c -o "adis_obj_$n.bin" "$T/$n.c"; done
mv adis_obj_clean.bin adis_decoy_clean.bin
gcc -O1 -no-pie -masm=intel -o adis_exe_all.bin "$T/main.c" "$T/jzjnz.c" "$T/ebff.c" "$T/callpop.c"
printf 'jz/jnz same target, eb ff c0, call $+5; pop; ret -- a write-up, not code\n' > adis_decoy_text.bin
