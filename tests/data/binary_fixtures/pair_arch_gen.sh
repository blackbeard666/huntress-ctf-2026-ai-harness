#!/bin/bash
# Cross-arch same-source build PAIR fixtures for lib.binary.pair_route (arch tags: x86_64 / aarch64 / riscv64 / armv7).
# Writers: gcc (x86-64, linked), aarch64-linux-gnu-gcc-15 (linked), clang-18 --target=riscv64/armv7 -c (ET_REL .o),
# Info-ZIP `zip -X -j` (member order = argv order).  usage (from this dir): bash pair_arch_gen.sh
set -euo pipefail
T=${TMPDIR:-/tmp}/pairarch; rm -rf "$T"; mkdir -p "$T"
cat > "$T/src.c" <<'C'
#include <stdio.h>
#include <string.h>
__attribute__((section(".hcfg"), used)) static const char hcfg[] = "HCFG\x01\x00\x10\x00{\"campaign\":\"arch\"}";
static int mix(const char *s){int h=7;for(;*s;s++)h=h*31+*s;return h;}
int recover_code(void){return 0x1337;}
int main(int c,char**v){printf("%d %d %zu\n",mix(c>1?v[1]:"x"),recover_code(),strlen(hcfg));return 0;}
C
# the .o builds: same HCFG + functions without libc headers (no riscv64/armhf sysroot installed)
sed -e '/#include/d' -e 's/^int main.*/int pick(int c){return mix(c?"y":"x")+recover_code();}/' "$T/src.c" > "$T/obj.c"
gcc -O2 -o "$T/d17--variant-000-x86_64.elf" "$T/src.c"
aarch64-linux-gnu-gcc-15 -O2 -o "$T/d17--variant-001-aarch64.elf" "$T/src.c"
clang-18 --target=riscv64-linux-gnu -O2 -c -o "$T/d17--variant-000-riscv64.o" "$T/obj.c"
clang-18 --target=armv7-linux-gnueabihf -O2 -c -o "$T/d17--variant-001-armv7.o" "$T/obj.c"
# renamed (no tag in the names): e_machine fallback; aarch64 listed first so CD order != variant order
mkdir -p "$T/r"; cp "$T/d17--variant-001-aarch64.elf" "$T/r/d17--build-a.elf"; cp "$T/d17--variant-000-x86_64.elf" "$T/r/d17--build-b.elf"
# arm64-named aarch64 member + amd64-named x86-64 member (alias tags must still route by name or by e_machine)
mkdir -p "$T/al"; cp "$T/d17--variant-001-aarch64.elf" "$T/al/d17--variant-001-arm64.elf"; cp "$T/d17--variant-000-x86_64.elf" "$T/al/d17--variant-000-amd64.elf"
# decoy: arch-tagged names on a 40-byte truncated ELF header and a text file
mkdir -p "$T/dc"; head -c 40 "$T/d17--variant-001-aarch64.elf" > "$T/dc/d17--variant-001-aarch64.elf"; echo 'not an elf' > "$T/dc/d17--variant-000-x86_64.elf"
z() { out=$1; shift; rm -f "$out"; (cd "$T" && zip -q -X -j "$OLDPWD/$out" "$@"); }
z pair_arch_x86_64_aarch64.bin d17--variant-001-aarch64.elf d17--variant-000-x86_64.elf
z pair_arch_riscv_arm_obj.bin d17--variant-000-riscv64.o d17--variant-001-armv7.o
z pair_arch_renamed.bin r/d17--build-a.elf r/d17--build-b.elf
z pair_arch_alias.bin al/d17--variant-001-arm64.elf al/d17--variant-000-amd64.elf
z pair_arch_decoy.bin dc/d17--variant-001-aarch64.elf dc/d17--variant-000-x86_64.elf
