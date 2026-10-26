#!/bin/bash
# Faulting-instruction-locator fixtures (lib.binary.fault_insn_facts). Our own tiny crashers only (gcc /
# aarch64-linux-gnu-gcc, strip, gdb generate-core-file); also reuses core_x64_*.bin + core_*_exe.elf from core_gen.sh.
# usage: bash fault_gen.sh   (then: python3 fault_oracle.py --write)
set -e
D=$(cd "$(dirname "$0")" && pwd); W=${TMPDIR:-/tmp}/fault_gen; rm -rf "$W"; mkdir -p "$W"; cd "$W"
cat > idx.c <<'C'
__attribute__((noinline)) int rd_elem(int *a, long i) { return a[i + 2]; }
int main(int c, char **v) { return rd_elem(c > 5 ? (int *)v : 0, c + 3); }
C
cat > badcall.c <<'C'
void (*volatile handler)(void);
int main(void) { handler(); return 0; }
C
cat > int3.c <<'C'
__attribute__((noinline)) void trap_me(void) { __asm__ volatile("nop; int3"); }
int main(void) { trap_me(); return 0; }
C
cat > a64.c <<'C'
__attribute__((noinline)) char peek5(volatile char *p) { return p[5]; }
void _start(void) { peek5((volatile char *)0); for (;;) ; }
C
gcore() { gdb -nx -batch -ex "run" -ex "generate-core-file $2" ./$1 >/dev/null 2>&1 </dev/null; }
# 1) stripped no-pie x86-64: the question is a text report (rip + si_addr), functions only via .eh_frame FDEs
gcc -O1 -no-pie -o idx.exe idx.c
REP=$(gdb -nx -batch -ex run -ex 'printf "rip=0x%lx si_addr=0x%lx\n", $pc, $_siginfo._sifields._sigfault.si_addr' ./idx.exe 2>/dev/null | grep '^rip=')
strip -s idx.exe -o fault_x64_strip_idx.bin
echo "Program received signal SIGSEGV, Segmentation fault. $REP" > fault_x64_strip_idx.question
# 2) call through a NULL function pointer (pc = 0): core + exe
gcc -O1 -no-pie -o fault_x64_badcall.bin badcall.c && gcore fault_x64_badcall.bin fault_x64_badcall.core
# 3) int3 located by FILE OFFSET (objdump VA -> readelf PT_LOAD mapping)
gcc -O1 -o fault_x64_int3_off.bin int3.c
VA=$(objdump -d fault_x64_int3_off.bin | awk '/<trap_me>:/{f=1} f && /\tint3/{print $1; exit}' | tr -d :)
python3 -I - fault_x64_int3_off.bin "$VA" > fault_x64_int3_off.question <<'PY'
import subprocess, sys
va = int(sys.argv[2], 16)
for l in subprocess.run(['readelf', '-lW', sys.argv[1]], capture_output=True, text=True).stdout.splitlines():
    t = l.split()
    if t and t[0] == 'LOAD' and int(t[2], 16) <= va < int(t[2], 16) + int(t[4], 16):
        print(f'The program traps at file offset {hex(va - int(t[2], 16) + int(t[1], 16))}; find the faulting instruction.')
PY
# 4) AArch64 freestanding: byte load through NULL+5, given as a bare VA
aarch64-linux-gnu-gcc -O1 -static -nostdlib -ffreestanding -o fault_a64_ldrb.bin a64.c
aarch64-linux-gnu-objdump -d fault_a64_ldrb.bin | awk '/<peek5>:/{f=1} f && /\tldrb/{print "0x"$1; exit}' | tr -d : > fault_a64_ldrb.va
# decoys: a text crash report with no binary; an ELF whose asked pc is outside every PT_LOAD
printf 'Segmentation fault (core dumped)\nrip 0x401136 in crash_here\n' > fault_decoy_text.bin
cp idx.exe fault_decoy_unmapped.bin
for f in fault_*.bin fault_*.core fault_*.question fault_*.va; do cp "$f" "$D/$f"; done
