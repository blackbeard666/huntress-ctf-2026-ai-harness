#!/bin/bash
# Same-source build PAIR fixtures for lib.binary.pair_route / pair_member_facts / zip_cd_sha256.
# Writers: gcc (-O0/-O2/-Os, -static, -pie/-no-pie, -g), strip, upx 4.x, Info-ZIP `zip` (member order = argv order).
# usage (from this dir): bash pair_gen.sh   -> pair_*.bin (zip archives)
set -euo pipefail
T=${TMPDIR:-/tmp}/pairgen; rm -rf "$T"; mkdir -p "$T"
cat > "$T/src.c" <<'C'
#include <stdio.h>
#include <string.h>
__attribute__((section(".hcfg"), used)) static const char hcfg[] = "HCFG\x01\x00\x10\x00{\"campaign\":\"pairs\"}";
static int mix(const char *s){int h=7;for(;*s;s++)h=h*31+*s;return h;}
int recover_code(void){return 0x1337;}
int main(int c,char**v){printf("%d %d %zu\n",mix(c>1?v[1]:"x"),recover_code(),strlen(hcfg));return 0;}
C
# freestanding static build (no libc: small enough for a fixture, still a real static ET_EXEC upx accepts)
cat > "$T/st.c" <<'C'
__attribute__((section(".hcfg"), used)) static const char hcfg[] = "HCFG\x01\x00\x10\x00{\"campaign\":\"pairs\"}";
__attribute__((used)) static const unsigned char pad[60000] = {1,2,3};
static long sys3(long n,long a,long b,long c){long r;__asm__ volatile("syscall":"=a"(r):"a"(n),"D"(a),"S"(b),"d"(c):"rcx","r11","memory");return r;}
void _start(void){sys3(1,1,(long)hcfg,4);sys3(1,1,(long)pad,1);sys3(60,0,0,0);for(;;);}
C
g() { gcc "$@"; }
g -O0 -o "$T/d17--variant-000-O0.elf" "$T/src.c"
g -O2 -o "$T/d17--variant-001-O2.elf" "$T/src.c"
g -O2 -fno-pie -no-pie -o "$T/d17--variant-001-no-pie.elf" "$T/src.c"
g -O2 -fpie -pie -o "$T/d17--variant-000-pie.elf" "$T/src.c"
g -O0 -g -o "$T/d17--variant-000-debug.elf" "$T/src.c"
g -O0 -g -o "$T/d17--variant-001-stripped.elf" "$T/src.c" && strip "$T/d17--variant-001-stripped.elf"
g -Os -static -nostdlib -fno-pie -no-pie -o "$T/d17--variant-000-static.elf" "$T/st.c"
g -Os -o "$T/d17--variant-001-dynamic.elf" "$T/src.c"
g -Os -static -nostdlib -fno-pie -no-pie -o "$T/d17--variant-001-unpacked.elf" "$T/st.c"
cp "$T/d17--variant-001-unpacked.elf" "$T/d17--variant-000-packed.elf" && upx -q -9 "$T/d17--variant-000-packed.elf" >/dev/null
# renamed (no tag in the name): structural fallback; members listed nopie-first so CD order != tag order
cp "$T/d17--variant-001-no-pie.elf" "$T/d17--variant-000.elf"; cp "$T/d17--variant-000-pie.elf" "$T/d17--variant-001.elf"
mkdir -p "$T/r2"; cp "$T/d17--variant-000-O0.elf" "$T/r2/d17--build-b.elf"; cp "$T/d17--variant-001-O2.elf" "$T/r2/d17--build-a.elf"
# decoy: a truncated ELF header + a text file wearing the .elf name
head -c 40 "$T/d17--variant-000-pie.elf" > "$T/d17--variant-000-pie.elf.t"; mkdir -p "$T/dc"
mv "$T/d17--variant-000-pie.elf.t" "$T/dc/d17--variant-000-pie.elf"; echo 'not an elf' > "$T/dc/d17--variant-001-no-pie.elf"
z() { out=$1; shift; rm -f "$out"; (cd "$T" && zip -q -X -j "$OLDPWD/$out" "$@"); }
z pair_opt_o0_o2.bin d17--variant-000-O0.elf d17--variant-001-O2.elf
z pair_pie_nopie.bin d17--variant-000-pie.elf d17--variant-001-no-pie.elf
z pair_debug_stripped.bin d17--variant-001-stripped.elf d17--variant-000-debug.elf
z pair_static_dynamic.bin d17--variant-000-static.elf d17--variant-001-dynamic.elf
z pair_packed_unpacked.bin d17--variant-000-packed.elf d17--variant-001-unpacked.elf
z pair_renamed_pie.bin d17--variant-000.elf d17--variant-001.elf
z pair_renamed_opt.bin r2/d17--build-b.elf r2/d17--build-a.elf
z pair_decoy.bin dc/d17--variant-000-pie.elf dc/d17--variant-001-no-pie.elf
