#!/bin/bash
# ELF core-dump fixtures (lib.binary.elf_core_facts). Our own tiny crashers only; cores via gdb generate-core-file
# (x86-64 dynamic + i386 static freestanding) and qemu-aarch64 user-mode core dumps. usage: bash core_gen.sh
set -e
D=$(cd "$(dirname "$0")" && pwd); W=${TMPDIR:-/tmp}/core_gen; rm -rf "$W"; mkdir -p "$W"; cd "$W"
cat > nullw.c <<'C'
#include <stdio.h>
__attribute__((noinline)) void crash_here(volatile int *p) { *p = 0x41; }
int main(int c, char **v) { puts("go"); crash_here((int *)0x10); return 0; }
C
cat > div0.c <<'C'
#include <stdlib.h>
__attribute__((noinline)) int divide_it(int a, int b) { return a / b; }
int main(int c, char **v) { return divide_it(c + 99, atoi(c > 1 ? v[1] : "0")); }
C
cat > smash.c <<'C'
#include <string.h>
__attribute__((noinline)) void smash(const char *s) { char b[8]; strcpy(b, s); }
int main(int c, char **v) { smash("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"); return 0; }
C
cat > ud2.c <<'C'
__attribute__((noinline)) void bad_op(void) { __asm__ volatile("ud2"); }
int main(void) { bad_op(); return 0; }
C
cat > ro32.c <<'C'
static const char msg[] = "ro";
__attribute__((noinline)) void poke_ro(volatile char *p) { *p = 'X'; }
void _start(void) { poke_ro((volatile char *)msg); for (;;) ; }
C
cat > arm.c <<'C'
__attribute__((noinline)) void arm_crash(volatile long *p) { *p = 7; }
int main(void) { arm_crash((long *)0x20); return 0; }
C
gcore() {  # exe core args...
  local exe=$1 core=$2; shift 2
  gdb -nx -batch -ex "run $*" -ex "generate-core-file $core" ./$exe >/dev/null 2>&1 </dev/null
}
gcc -O1 -g0 -o core_x64_nullw.exe nullw.c && gcore core_x64_nullw.exe core_x64_nullw.core
gcc -O1 -o core_x64_div0.exe div0.c && gcore core_x64_div0.exe core_x64_div0.core
gcc -O0 -fstack-protector-all -D_FORTIFY_SOURCE=0 -o core_x64_smash.exe smash.c && gcore core_x64_smash.exe core_x64_smash.core
gcc -O1 -no-pie -o core_x64_ud2.exe ud2.c && gcore core_x64_ud2.exe core_x64_ud2.core
gcc -m32 -O1 -static -nostdlib -ffreestanding -fno-pic -no-pie -o core_i386_ro.exe ro32.c && gcore core_i386_ro.exe core_i386_ro.core
aarch64-linux-gnu-gcc -O1 -static -o core_a64_nullw.exe arm.c
( ulimit -c unlimited; qemu-aarch64 ./core_a64_nullw.exe || true ) 2>/dev/null
mv qemu_core_a64_nullw.exe_*.core core_a64_nullw.full
# synthetic rewrite (struct writer, independent of lib/): keep headers + notes, shrink each PT_LOAD > 1 MB to its top 64 KB
python3 -I - core_a64_nullw.full core_a64_nullw.core <<'PY'
import struct, sys
d = open(sys.argv[1], 'rb').read()
phoff, = struct.unpack_from('<Q', d, 32); phes, phn = struct.unpack_from('<HH', d, 54)
ph = [list(struct.unpack_from('<IIQQQQQQ', d, phoff + k * phes)) for k in range(phn)]
head_end = max(p[2] + p[5] for p in ph if p[0] == 4)
out = bytearray(d[:head_end]); out += b'\0' * (-len(out) % 4096)
for p in ph:
    if p[0] != 1 or not p[5]:
        continue
    blob = d[p[2]:p[2] + p[5]]
    if p[5] > 1 << 20:
        cut = p[5] - 0x10000; blob = blob[cut:]; p[3] += cut; p[4] += cut; p[5] = p[6] = len(blob)
    p[2] = len(out); out += blob; out += b'\0' * (-len(out) % 4096)
for k, p in enumerate(ph):
    struct.pack_into('<IIQQQQQQ', out, phoff + k * phes, *p)
open(sys.argv[2], 'wb').write(out)
PY
head -c 4096 core_x64_nullw.core > core_decoy_trunc.core          # ET_CORE header + phdrs, notes cut off
cp core_x64_nullw.exe core_decoy_trunc.exe
cp core_x64_div0.exe core_decoy_exe.core && cp core_x64_div0.exe core_decoy_exe.exe   # an executable posing as a core
for s in x64_nullw x64_div0 x64_smash x64_ud2 i386_ro a64_nullw decoy_trunc decoy_exe; do
  cp core_$s.core "$D/core_$s.bin"; cp core_$s.exe "$D/core_${s}_exe.elf"
done
