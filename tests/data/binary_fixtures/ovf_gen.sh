#!/bin/bash
# Generator for the ovf_* (stack-overflow exploitability facts) fixtures: gcc builds of tiny vulnerable / corrected
# programs (compiled only; the oracle may run them under gdb).  usage: bash ovf_gen.sh   (writes ovf_*.bin here)
set -e
cd "$(dirname "$0")"
T=$(mktemp -d)
cat > $T/gets.c <<'C'
#include <stdio.h>
char *gets(char *);
__attribute__((noinline)) void vuln(void) { char buf[64]; gets(buf); puts(buf); }
int main(void) { setvbuf(stdout, 0, 2, 0); vuln(); return 0; }
C
cat > $T/read.c <<'C'
#include <unistd.h>
__attribute__((noinline)) void handle(void) { char buf[40]; ssize_t n = read(0, buf, 200); write(1, buf, n > 0 ? n : 0); }
int main(void) { handle(); return 0; }
C
cat > $T/fgets.c <<'C'
#include <stdio.h>
__attribute__((noinline)) void handle(void) { char buf[40]; fgets(buf, sizeof buf, stdin); puts(buf); }
int main(void) { handle(); return 0; }
C
cat > $T/scanf.c <<'C'
#include <stdio.h>
__attribute__((noinline)) void login(void) { char name[32]; int age = 7; scanf("%s", name); printf("%s %d\n", name, age); }
int main(void) { login(); return 0; }
C
cat > $T/strcpy.c <<'C'
#include <string.h>
#include <stdio.h>
__attribute__((noinline)) void copy(const char *s) { char buf[100]; strcpy(buf, s); puts(buf); }
int main(int argc, char **argv) { if (argc > 1) copy(argv[1]); return 0; }
C
gcc -O0 -w -fno-stack-protector -no-pie -z execstack -Wl,-z,norelro -o ovf_gets_nossp.bin $T/gets.c
gcc -O0 -w -fstack-protector-strong -pie -fPIE -Wl,-z,relro,-z,now -o ovf_read_ssp.bin $T/read.c
gcc -O0 -w -fno-stack-protector -pie -fPIE -o ovf_read_nossp.bin $T/read.c
gcc -O0 -w -fstack-protector-strong -pie -fPIE -Wl,-z,relro,-z,now -o ovf_fgets_fixed.bin $T/fgets.c
gcc -O2 -w -fno-stack-protector -no-pie -o ovf_scanf_O2.bin $T/scanf.c
gcc -O0 -w -fstack-protector-strong -o ovf_strcpy_ssp.bin $T/strcpy.c
printf 'This is not an ELF: char buf[64]; gets(buf); mov rax, fs:0x28\n' > ovf_decoy_text.bin
head -c 300 ovf_read_ssp.bin > ovf_decoy_trunc.bin
rm -rf $T
