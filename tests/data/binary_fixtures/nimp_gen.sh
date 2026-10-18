#!/bin/bash
# usage: nimp_gen.sh out kind
# Native import/export tables (no HCFG blob: hcfg_scan must stay empty). kinds:
#  elf_dyn   gcc -O2 dynamic PIE linking -lz -lm (DT_NEEDED libz, libm, libc; UND getenv/strcmp/printf/zlibVersion/cos)
#  elf_so    gcc -shared -fPIC -Wl,-soname,libnimp.so.2 -lz (exports nimp_api/nimp_ver/nimp_table)
#  elf_static (decoy) gcc -static: no PT_INTERP, no .dynamic, no .dynsym imports
#  pe_exe    zig cc -target x86_64-windows-gnu (KERNEL32 + USER32 + WS2_32 imports via MessageBoxA / WSAStartup)
#  pe_dll    zig cc -target x86_64-windows-gnu -shared (dllexport nimp_api / nimp_ver)
#  pe_decoy  (decoy) an "MZ" text impostor: e_lfanew points at no PE signature
#  macho_exe zig cc -target x86_64-macos (LC_LOAD_DYLIB libSystem, LC_LOAD_DYLINKER /usr/lib/dyld, _getenv/_strcmp/_printf)
#  macho_dylib zig cc -target aarch64-macos -shared (LC_ID_DYLIB + exported _nimp_api/_nimp_ver)
#  macho_obj (decoy) zig cc -target aarch64-macos -c: MH_OBJECT, no dylibs / no dylinker
set -e
R="$(cd "$(dirname "$0")/../../.." && pwd)"; W=$(mktemp -d); O="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
Z() { (cd "$W" && PYTHONPATH="$R/tools/pyziglang" python3 -m ziglang cc "$@"); }
cat > "$W/exe.c" <<'C'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int nimp_check(const char *s) { const char *k = getenv("NIMP_KEY"); return strcmp(s, k ? k : "x"); }
int main(int c, char **v) { printf("%d\n", nimp_check(v[0])); return 0; }
C
cat > "$W/elf.c" <<'C'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <zlib.h>
int main(int c, char **v) { const char *k = getenv("K"); printf("%d %s %f\n", strcmp(v[0], k ? k : "x"), zlibVersion(), cos(c)); return 0; }
C
cat > "$W/so.c" <<'C'
#include <zlib.h>
int nimp_table[4] = {1, 2, 3, 4};
static int helper(int x) { return x * 3; }
const char *nimp_ver(void) { return zlibVersion(); }
int nimp_api(int x) { return helper(x) + nimp_table[x & 3]; }
C
cat > "$W/win.c" <<'C'
#include <winsock2.h>
#include <windows.h>
int main(void) { WSADATA d; WSAStartup(0x202, &d); MessageBoxA(0, "nimp", GetCommandLineA(), 0); Sleep(1); return 0; }
C
cat > "$W/dll.c" <<'C'
__declspec(dllexport) int nimp_api(int x) { return x * 7; }
__declspec(dllexport) const char *nimp_ver(void) { return "1.2"; }
C
cat > "$W/dylib.c" <<'C'
static int helper(int x) { return x ^ 5; }
int nimp_api(int x) { return helper(x) * 7; }
const char *nimp_ver(void) { return "1.2"; }
C
case "$2" in
  elf_dyn) gcc -O2 -o "$O" "$W/elf.c" -lz -lm ;;
  elf_so) gcc -O2 -shared -fPIC -Wl,-soname,libnimp.so.2 -o "$O" "$W/so.c" -lz ;;
  elf_static) gcc -O2 -static -o "$O" "$W/exe.c" ;;
  pe_exe) Z -target x86_64-windows-gnu -O2 -s -o p.exe win.c -lws2_32 -luser32 && cp "$W/p.exe" "$O" ;;
  pe_dll) Z -target x86_64-windows-gnu -shared -O2 -s -o nimp.dll dll.c && cp "$W/nimp.dll" "$O" ;;
  pe_decoy) printf 'MZ this is not a program: e_lfanew -> nowhere. KERNEL32.dll!GetProcAddress\n%0200d\n' 0 > "$O" ;;
  macho_exe) Z -target x86_64-macos -O2 -o m exe.c && cp "$W/m" "$O" ;;
  macho_dylib) Z -target aarch64-macos -shared -O2 -o libnimp.dylib dylib.c && cp "$W/libnimp.dylib" "$O" ;;
  macho_obj) Z -target aarch64-macos -O2 -c -o o.o exe.c && cp "$W/o.o" "$O" ;;
esac
rm -rf "$W"
