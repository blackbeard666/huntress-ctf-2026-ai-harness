#!/usr/bin/env bash
# Generator for crash_* fixtures (crash/trace SIDECAR). Independent writers: javac + zip, gcc + objcopy, iconv.
# usage: bash crash_gen.sh  (from tests/data/binary_fixtures; d26 jar copied from the D26 GM artifact)
set -euo pipefail
here=$(pwd); w=$(mktemp -d); trap 'rm -rf "$w"' EXIT
cp ../../../challenges/day26/binary-crash-course/single_solve/work/extracted/evidence/d26--sample.jar crash_d26_jar.bin 2>/dev/null || true
cd "$w"
cat > Crash.java <<'J'
public class Crash {
    static int helperValue = 3;
    public static void stageThree() { throw new IllegalStateException("boom"); }
    public static void stageTwo() { stageThree(); }
    public static void stageOne() { stageTwo(); }
    public static void main(String[] a) { stageOne(); }
}
J
javac --release 8 Crash.java 2>/dev/null || javac Crash.java
printf 'Manifest-Version: 1.0\nMain-Class: Crash\n' > m.mf
mkdir -p META-INF/diag crash; cp m.mf META-INF/MANIFEST.MF
# 1 renamed entry, "stack" key, Class.method(File:line) frames
printf '{"schema":"huntress.synthetic_crash.v1","kind":"IllegalStateException","stack":["Crash.stageThree(Crash.java:3)","Crash.stageTwo(Crash.java:4)","Crash.stageOne(Crash.java:5)"]}' > META-INF/diag/crash-0001.json
rm -f a.jar; zip -q -X a.jar META-INF/MANIFEST.MF Crash.class META-INF/diag/crash-0001.json; cp a.jar "$here/crash_jar_renamed.bin"
# 2 JVM descriptor frames, one frame not a method, not a call chain
rm -rf META-INF/diag; mkdir -p META-INF/diag
printf '{"schema":"huntress.synthetic_crash.v1","kind":"ArithmeticException","frames":["stageTwo()V","helperValue(I)I","main([Ljava/lang/String;)V"]}' > crash/trace.json
rm -f b.jar; zip -q -X b.jar META-INF/MANIFEST.MF Crash.class crash/trace.json; cp b.jar "$here/crash_jar_desc_mismatch.bin"
# 3 text Java stack trace in crash/stack.txt
rm -f crash/trace.json
printf 'Exception in thread "main" java.lang.IllegalStateException: boom\n\tat Crash.stageThree(Crash.java:3)\n\tat Crash.stageTwo(Crash.java:4)\n\tat Crash.stageOne(Crash.java:5)\n\tat Crash.main(Crash.java:6)\n' > crash/stack.txt
rm -f c.jar; zip -q -X c.jar META-INF/MANIFEST.MF Crash.class crash/stack.txt; cp c.jar "$here/crash_jar_texttrace.bin"
# decoy jar: no trace entry, a JSON resource without any frames list
rm -f crash/stack.txt; printf '{"schema":"huntress.synthetic_crash.v1","kind":"none","calls":["stageThree"]}' > crash/report.json
rm -f d.jar; zip -q -X d.jar META-INF/MANIFEST.MF Crash.class crash/report.json; cp d.jar "$here/crash_decoy_jar.bin"
# ELF: static call chain stageOne -> stageTwo -> stageThree
cat > c.c <<'C'
#include <stdlib.h>
__attribute__((noinline)) void stageThree(void) { abort(); }
__attribute__((noinline)) void stageTwo(void) { stageThree(); __asm__ volatile(""); }
__attribute__((noinline)) void stageOne(void) { stageTwo(); __asm__ volatile(""); }
int main(void) { stageOne(); return 0; }
C
gcc -O0 -no-pie -fno-pie -o c.elf c.c
# 4 sidecar in an ELF section, module!func+off frames
printf '{"schema":"huntress.synthetic_crash.v1","kind":"SIGABRT","frames":["c.elf!stageThree+0x9","c.elf!stageTwo+0x9","c.elf!stageOne+0x9","c.elf!main+0x9"]}' > t.json
objcopy --add-section .crash_trace=t.json --set-section-flags .crash_trace=noload,readonly c.elf e1.elf; cp e1.elf "$here/crash_elf_section.bin"
# 5 raw address frames (from nm), UTF-16LE JSON with a backtrace key, appended as overlay
a3=$(nm c.elf | awk '$3=="stageThree"{print $1}'); a2=$(nm c.elf | awk '$3=="stageTwo"{print $1}'); a1=$(nm c.elf | awk '$3=="stageOne"{print $1}')
printf '{"kind":"SIGSEGV","backtrace":["0x%x","0x%x","0x%x"]}' $((0x$a3+4)) $((0x$a2+4)) $((0x$a1+4)) | iconv -f UTF-8 -t UTF-16LE > t16.bin
cat c.elf t16.bin > "$here/crash_elf_utf16_addr.bin"
# decoy ELF: JSON section without a frames list
printf '{"schema":"huntress.synthetic_crash.v1","kind":"SIGABRT","functions":["stageThree","stageTwo"]}' > n.json
objcopy --add-section .crash_trace=n.json --set-section-flags .crash_trace=noload,readonly c.elf e2.elf; cp e2.elf "$here/crash_decoy_elf.bin"
