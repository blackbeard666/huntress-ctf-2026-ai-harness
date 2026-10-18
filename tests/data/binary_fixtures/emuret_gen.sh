#!/bin/bash
# Generate emuret_<name>.bin: a gcc / aarch64-linux-gnu-gcc ELF whose recover_code() return value is COMPUTED (not a
# `mov eax, imm; ret` leaf). main prints it, so the oracle is simply running the binary (natively / qemu-aarch64).
# usage: bash emuret_gen.sh <name>     (run from this directory)
set -e
n=$1; src=$(mktemp --suffix=.c)
trap 'rm -f "$src"' EXIT
case $n in
xor_O0) cc="gcc -O0"; cat > "$src" <<'C'
#include <stdio.h>
__attribute__((noinline)) unsigned recover_code(void){ volatile unsigned a = 0x5a5a1234u, b = 0x0f0f4321u; return (a ^ b) + 17; }
int main(void){ printf("%u\n", recover_code()); return 0; }
C
;;
table_O2) cc="gcc -O2"; cat > "$src" <<'C'
#include <stdio.h>
static const unsigned short T[16] = {311, 4127, 59, 8100, 723, 1999, 4242, 65000, 17, 909, 3333, 12, 777, 5150, 61, 2718};
__attribute__((noinline)) unsigned recover_code(void){ volatile int i = 6, j = 13; return T[i] * 3u + T[j] - T[i ^ j]; }
int main(void){ printf("%u\n", recover_code()); return 0; }
C
;;
switch_O2) cc="gcc -O2"; cat > "$src" <<'C'
#include <stdio.h>
__attribute__((noinline)) static unsigned mix(unsigned x){ return (x << 5) ^ (x >> 3) ^ 0x9e37u; }
__attribute__((noinline)) unsigned recover_code(void){
  volatile unsigned st = 7; unsigned acc = 0x1337;
  for (;;) switch (st) {
    case 7: acc = mix(acc); st = 3; break;  case 3: acc += 0x41; st = 11; break;
    case 11: acc ^= 0xbeef; st = 5; break;  case 5: acc = mix(acc) & 0xffff; st = 9; break;
    case 9: acc *= 3; st = 1; break;        case 2: acc = 0; st = 1; break;
    case 1: return acc;                     default: return 0xdead; } }
int main(void){ printf("%u\n", recover_code()); return 0; }
C
;;
fptr_O2) cc="gcc -O2"; cat > "$src" <<'C'
#include <stdio.h>
__attribute__((noinline)) static unsigned f0(unsigned x){ return x * 7 + 1; }
__attribute__((noinline)) static unsigned f1(unsigned x){ return x ^ 0xa5a5; }
__attribute__((noinline)) static unsigned f2(unsigned x){ return (x >> 2) + 4000; }
static unsigned (*const OPS[3])(unsigned) = {f1, f0, f2};
__attribute__((noinline)) unsigned recover_code(void){ volatile int k = 2; unsigned v = 0x2024;
  for (int r = 0; r < 5; r++) v = OPS[(k + r) % 3](v); return v; }
int main(void){ printf("%u\n", recover_code()); return 0; }
C
;;
a64_O2) cc="aarch64-linux-gnu-gcc -O2"; cat > "$src" <<'C'
#include <stdio.h>
static const unsigned T[8] = {0x1111, 0x2f2f, 0x0abc, 0x7777, 0x1fa4, 0x3c3c, 0x0101, 0x4e4e};
__attribute__((noinline)) unsigned recover_code(void){ volatile unsigned st = 2, i = 5; unsigned acc = 0;
  for (;;) switch (st) { case 2: acc = T[i] ^ 0x55aa; st = 4; break; case 4: acc = acc * 13 + T[i ^ 3]; st = 6; break;
    case 6: acc = (acc << 3) | (acc >> 29); st = 0; break; case 0: return acc; default: return 1; } }
int main(void){ printf("%u\n", recover_code()); return 0; }
C
;;
decoy_stripped) cc="gcc -O2 -s"; cat > "$src" <<'C'
#include <stdio.h>
__attribute__((noinline)) unsigned recover_code(void){ volatile unsigned a = 1234, b = 4321; return a * b; }
int main(void){ printf("%u\n", recover_code()); return 0; }
C
;;
decoy_libcall) cc="gcc -O2"; cat > "$src" <<'C'
#include <stdio.h>
#include <unistd.h>
__attribute__((noinline)) unsigned recover_code(void){ volatile unsigned a = 99; return a + (unsigned)getpid() * 0; }
int main(void){ printf("%u\n", recover_code()); return 0; }
C
;;
*) echo "unknown $n" >&2; exit 2;;
esac
$cc -o "emuret_$n.bin" "$src"
