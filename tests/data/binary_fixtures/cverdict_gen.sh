#!/bin/bash
# Crash exploitability VERDICT fixtures (lib.binary.crash_verdict_facts). Our own tiny crashers; one gdb session per
# crasher stops at the fatal signal, runs the CERT `exploitable` plugin (tools/exploitable, the independent oracle for
# rating / rule) and writes the core with generate-core-file. Mitigations come from readelf (cverdict_oracle.py).
# usage: bash cverdict_gen.sh
set -e
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); X=$R/tools/exploitable/exploitable
W=${TMPDIR:-/tmp}/cverdict_gen; rm -rf "$W"; mkdir -p "$W"; cd "$W"
cat > nullr.c <<'C'
#include <stdio.h>
__attribute__((noinline)) int peek(volatile int *p) { return *p; }
int main(void) { puts("go"); return peek((int *)0x18); }
C
cat > wildw.c <<'C'
__attribute__((noinline)) void poke(volatile long *p) { *p = 0x4242; }
int main(void) { poke((long *)0x7f0000dead00); return 0; }
C
cat > wildr.c <<'C'
__attribute__((noinline)) long peek(volatile long *p) { return *p; }
int main(void) { return (int)peek((long *)0x7f0000dead00); }
C
cat > callreg.c <<'C'
typedef void (*fn)(void);
__attribute__((noinline)) void go(fn f) { f(); }
int main(void) { go((fn)0x7f0000c0de00); return 0; }
C
cat > div0.c <<'C'
#include <stdlib.h>
__attribute__((noinline)) int divide_it(int a, int b) { return a / b; }
int main(int c, char **v) { return divide_it(c + 99, atoi(c > 1 ? v[1] : "0")); }
C
cat > smash.c <<'C'
#include <string.h>
__attribute__((noinline)) void smash(const char *s) { char b[8]; strcpy(b, s); }
int main(void) { smash("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"); return 0; }
C
cat > dfree.c <<'C'
#include <stdlib.h>
#include <stdio.h>
int main(void) { char *volatile p = malloc(32); puts("x"); free(p); free(p); return 0; }
C
cat > assrt.c <<'C'
#include <assert.h>
#include <stdlib.h>
__attribute__((noinline)) void check(int n) { assert(n < 4 && "len within table"); }
int main(int c, char **v) { check(c + 7); return 0; }
C
cat > retov.c <<'C'
#include <string.h>
__attribute__((noinline)) void cp(const char *s) { char b[8]; strcpy(b, s); }
int main(void) { cp("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"); return 0; }
C
cc() { gcc -g0 "$@"; }
cc -O1 -o cv_nullr.exe nullr.c
cc -O1 -fstack-protector-strong -Wl,-z,relro,-z,now -o cv_wildw.exe wildw.c
cc -O1 -no-pie -fno-stack-protector -o cv_wildr.exe wildr.c
cc -O1 -o cv_callreg.exe callreg.c
cc -O1 -o cv_div0.exe div0.c
cc -O0 -fstack-protector-all -D_FORTIFY_SOURCE=0 -o cv_smash.exe smash.c
cc -O0 -o cv_dfree.exe dfree.c
cc -O1 -o cv_assrt.exe assrt.c
cc -O0 -fno-stack-protector -no-pie -z execstack -Wl,-z,norelro -o cv_retov.exe retov.c
for n in nullr wildw wildr callreg div0 smash dfree assrt retov; do
  env -u PYTHONPATH -u PYTHONSAFEPATH gdb -nx -batch -ex "set debuginfod enabled off" \
    -ex "python import sys; sys.path.insert(0,'$X'); [sys.modules.pop(k) for k in list(sys.modules) if k=='lib' or k.startswith('lib.')]" \
    -ex "source $X/exploitable.py" -ex run -ex "generate-core-file cv_$n.core" -ex "bt 12" \
    -ex 'printf "SIGINFO signo=%d code=%d\n", $_siginfo.si_signo, $_siginfo.si_code' \
    -ex 'printf "SIADDR %#lx\n", (long)$_siginfo._sifields._sigfault.si_addr' -ex 'printf "REGS pc=%#lx sp=%#lx\n", $pc, $sp' \
    -ex 'printf "RETWORD %#lx\n", *(long*)$sp' -ex "x/i \$pc" -ex "info proc mappings" -ex exploitable ./cv_$n.exe 2>/dev/null </dev/null \
    > cv_$n.expl || true
  cp cv_$n.core "$D/cverdict_$n.bin"; cp cv_$n.exe "$D/cverdict_${n}_exe.elf"; cp cv_$n.expl "$D/cverdict_$n.expl"
done
# decoys: a plain executable (no core) and a core truncated inside its program headers
cp cv_nullr.exe "$D/cverdict_decoy_exe.bin"; cp cv_nullr.exe "$D/cverdict_decoy_exe_exe.elf"
head -c 300 cv_nullr.core > "$D/cverdict_decoy_trunc.bin"; cp cv_nullr.exe "$D/cverdict_decoy_trunc_exe.elf"
