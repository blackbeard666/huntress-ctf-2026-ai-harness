#!/bin/bash
# Generate api-intent fixtures: gcc ELF (compiled only, never run) + stdlib-struct PE32+ import tables.
# usage (from this dir): bash apiint_gen.sh
set -e
T=${TMPDIR:-/tmp}/apiint; mkdir -p "$T"
cat > "$T/inj.c" <<'C'
#define _GNU_SOURCE
#include <sys/ptrace.h>
#include <sys/uio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <stdio.h>
int main(int c, char **v) {
  pid_t p = atoi(v[1]); long w = 0x90909090;
  struct iovec l = {&w, 8}, r = {(void *)0x401000, 8};
  ptrace(PTRACE_ATTACH, p, 0, 0);
  ptrace(PTRACE_POKETEXT, p, (void *)0x401000, (void *)w);
  process_vm_writev(p, &l, 1, &r, 1, 0);
  ptrace(PTRACE_DETACH, p, 0, 0);
  printf("%s\n", getenv("HOME"));
  return 0;
}
C
cat > "$T/peek.c" <<'C'
#define _GNU_SOURCE
#include <sys/ptrace.h>
#include <sys/uio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
int main(int c, char **v) {
  pid_t p = atoi(v[1]); long w; char b[64], path[64];
  struct iovec l = {b, 8}, r = {(void *)0x401000, 8};
  snprintf(path, sizeof path, "/proc/%d/mem", p);
  ptrace(PTRACE_ATTACH, p, 0, 0);
  w = ptrace(PTRACE_PEEKDATA, p, (void *)0x401000, 0);
  process_vm_readv(p, &l, 1, &r, 1, 0);
  ptrace(PTRACE_DETACH, p, 0, 0);
  if (strcmp(getenv("USER"), "root") == 0) puts(path);
  printf("%lx\n", w);
  return 0;
}
C
gcc -O2 -o apiint_elf_ptrace_poke.bin "$T/inj.c"
gcc -O0 -no-pie -o apiint_elf_ptrace_peek.bin "$T/peek.c"
python3 apiint_pe_gen.py apiint_pe_crt_inject.bin kernel32.dll:OpenProcess,VirtualAllocEx,WriteProcessMemory,CreateRemoteThread,LoadLibraryA,GetProcAddress,CloseHandle msvcrt.dll:printf,getenv
python3 apiint_pe_gen.py apiint_pe_benign_net.bin kernel32.dll:GetEnvironmentVariableA,ExitProcess,lstrcmpA ws2_32.dll:WSAStartup,socket,connect msvcrt.dll:printf,strcmp
head -c 200 apiint_elf_ptrace_poke.bin | tail -c 136 > apiint_decoy_trunc.bin   # ELF body without the magic
printf 'MZ not really a PE: ptrace PTRACE_POKETEXT WriteProcessMemory CreateRemoteThread\n' > apiint_decoy_text.bin
cp gfortran_d18_flow_v000.bin apiint_d18_fortran.bin
