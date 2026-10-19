#!/bin/bash
# Generate the sysc_* fixtures: gcc -nostdlib -static C programs whose APIs are raw inline syscalls (no imports).
# usage (from tests/data/binary_fixtures): bash sysc_gen.sh
set -e
T=${TMPDIR:-/tmp}/sysc_src; mkdir -p "$T"
# x86-64: ptrace(PTRACE_ATTACH) + process_vm_writev + write + exit  (injection T1055.009)
cat > "$T/x64_inject.c" <<'C'
static long sc(long n, long a, long b, long c, long d, long e, long f) {
    long r; register long r10 asm("r10") = d; register long r8 asm("r8") = e; register long r9 asm("r9") = f;
    asm volatile("syscall" : "=a"(r) : "a"(n), "D"(a), "S"(b), "d"(c), "r"(r10), "r"(r8), "r"(r9) : "rcx", "r11", "memory");
    return r; }
static char buf[64] = "patched";
void _start(void) {
    long pid = 4242;
    asm volatile("syscall" :: "a"(101), "D"(16), "S"(pid), "d"(0) : "rcx", "r11", "memory");          /* ptrace ATTACH */
    struct { void *b; unsigned long l; } lo = {buf, 7}, re = {(void *)0x400000, 7};
    asm volatile("mov %0, %%r10\n\tmov $1, %%r8\n\txor %%r9d, %%r9d\n\tmov $311, %%eax\n\tsyscall"
                 :: "r"(&re), "D"(pid), "S"(&lo), "d"(1L) : "rax", "rcx", "r10", "r8", "r9", "r11", "memory");
    asm volatile("syscall" :: "a"(1), "D"(1), "S"(buf), "d"(7) : "rcx", "r11", "memory");               /* write */
    for (;;) asm volatile("syscall" :: "a"(60), "D"(0) : "rcx", "r11");                                 /* exit */
}
C
# x86-64: memfd_create + write + execveat-free execve + exit_group  (fileless exec T1620)
cat > "$T/x64_memfd.c" <<'C'
static const char nm[] = "x", path[] = "/proc/self/fd/3";
static const char elf[] = "\177ELF";
void _start(void) {
    long fd;
    asm volatile("syscall" : "=a"(fd) : "a"(319), "D"(nm), "S"(1) : "rcx", "r11", "memory");          /* memfd_create */
    asm volatile("syscall" :: "a"(1), "D"(fd), "S"(elf), "d"(4) : "rcx", "r11", "memory");             /* write */
    asm volatile("syscall" :: "a"(59), "D"(path), "S"(0), "d"(0) : "rcx", "r11", "memory");            /* execve */
    for (;;) asm volatile("syscall" :: "a"(231), "D"(1) : "rcx", "r11");                                /* exit_group */
}
C
# i386: int 0x80 ptrace(PTRACE_POKEDATA) + getpid + exit  (ptrace injection T1055.008)
cat > "$T/i386_poke.c" <<'C'
void _start(void) {
    long pid;
    asm volatile("int $0x80" : "=a"(pid) : "a"(20) : "memory");                                         /* getpid */
    asm volatile("int $0x80" :: "a"(26), "b"(5), "c"(pid), "d"(0x8048000), "S"(0x90909090) : "memory");  /* ptrace POKEDATA */
    for (;;) asm volatile("int $0x80" :: "a"(1), "b"(0));                                                /* exit */
}
C
# aarch64: svc #0 write + getpid + exit  (benign, no injection)
cat > "$T/a64_benign.c" <<'C'
static const char msg[] = "hello\n";
static long sc3(long n, long a, long b, long c) {
    register long x8 asm("x8") = n, x0 asm("x0") = a, x1 asm("x1") = b, x2 asm("x2") = c;
    asm volatile("svc #0" : "+r"(x0) : "r"(x8), "r"(x1), "r"(x2) : "memory");
    return x0; }
void _start(void) {
    register long x8 asm("x8") = 172, x0 asm("x0");
    asm volatile("svc #0" : "=r"(x0) : "r"(x8) : "memory");                                              /* getpid */
    register long y8 asm("x8") = 64, y0 asm("x0") = 1, y1 asm("x1") = (long)msg, y2 asm("x2") = 6;
    asm volatile("svc #0" : "+r"(y0) : "r"(y8), "r"(y1), "r"(y2) : "memory");                           /* write */
    register long z8 asm("x8") = 93, z0 asm("x0") = 0;
    for (;;) asm volatile("svc #0" :: "r"(z8), "r"(z0));                                                  /* exit */
}
C
gcc -O1 -nostdlib -static -fno-pie -no-pie -o sysc_x64_inject.bin "$T/x64_inject.c"
gcc -O1 -nostdlib -static -fno-pie -no-pie -o sysc_x64_memfd.bin "$T/x64_memfd.c"
gcc -m32 -O1 -nostdlib -static -fno-pie -no-pie -o sysc_i386_poke.bin "$T/i386_poke.c"
aarch64-linux-gnu-gcc -O1 -nostdlib -static -o sysc_a64_benign.bin "$T/a64_benign.c"
gcc -O1 -nostdlib -static -fno-pie -no-pie -o sysc_x64_inject_stripped.bin "$T/x64_inject.c" -s
# decoys: text impostor with syscall opcode bytes; dynamic libc ELF with no inline syscall instruction
printf '\x7fELF? not an ELF: \x0f\x05 \xcd\x80 mov eax,310; syscall; process_vm_writev ptrace memfd_create\n' > sysc_decoy_text.bin
printf '#include <stdio.h>\nint main(void){puts("hi");return 0;}\n' > "$T/dyn.c"
gcc -O1 -o sysc_decoy_dynlibc.bin "$T/dyn.c"
# dynamic libc syscall(SYS_process_vm_writev, ...) wrapper: the API is the call's 1st argument, not an import
cat > "$T/libc_wrap.c" <<'C'
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/uio.h>
int main(int argc, char **argv) {
    char b[8] = "patched";
    struct iovec lo = {b, 7}, re = {(void *)0x400000, 7};
    long r = syscall(SYS_process_vm_writev, (long)argc + 4000, &lo, 1L, &re, 1L, 0L);
    printf("%ld\n", r);
    return 0;
}
C
gcc -O1 -fno-pie -no-pie -o sysc_x64_libc_wrapper.bin "$T/libc_wrap.c"
