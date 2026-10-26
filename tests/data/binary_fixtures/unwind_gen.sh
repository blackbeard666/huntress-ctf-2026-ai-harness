#!/bin/sh
# static-stack-unwinder fixtures: same crasher at -O0 (frame pointers) and -O2 -fomit-frame-pointer; core written
# by gdb (generate-core-file) at the SIGSEGV -- independent of lib.binary.  Oracle: unwind_oracle.sh (gdb bt / info frame).
set -e; cd "$(dirname "$0")"
gcc -O0 -fno-omit-frame-pointer -g0 -no-pie -o unwind_o0_exe.bin unwind_crasher.c
gcc -O2 -fomit-frame-pointer -g0 -fno-optimize-sibling-calls -o unwind_o2_exe.bin unwind_crasher.c
for v in o0 o2; do
  gdb -nx -batch -ex 'set disable-randomization on' -ex run -ex "generate-core-file unwind_${v}_core.bin" --args ./unwind_${v}_exe.bin >/dev/null 2>&1
done
# MinGW PE32+ (zig cc = clang + lld, x86_64-windows-gnu): .pdata/.xdata UNWIND_INFO; functions exported (dllexport via
# -Dnoinline=noinline,dllexport) because lld/zig drop the COFF symbol table.  PE32 i386 build = no-.pdata decoy.
R="$(cd ../../.. && pwd)"; W=$(mktemp -d); cp unwind_crasher.c "$W"
Z() { (cd "$W" && PYTHONPATH="$R/tools/pyziglang" python3 -m ziglang cc -fno-sanitize=all -g0 '-Dnoinline=noinline,dllexport' "$@" unwind_crasher.c); }
Z -target x86_64-windows-gnu -O0 -fno-omit-frame-pointer -o o0.exe; Z -target x86_64-windows-gnu -O2 -fomit-frame-pointer -o o2.exe
Z -target x86-windows-gnu -O2 -o x86.exe
cp "$W/o0.exe" unwind_pe_o0.bin; cp "$W/o2.exe" unwind_pe_o2.bin; cp "$W/x86.exe" unwind_pe_x86_decoy.bin
