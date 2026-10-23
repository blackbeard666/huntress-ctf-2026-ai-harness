#!/bin/bash
# Generates the route_* fixtures (run from an empty scratch dir; FX = tests/data/binary_fixtures). gcc, strip,
# wat2wasm, python3 stdlib (zlib.crc32 for the HCFG header), zip -X -j (central-directory order = argument order).
set -e
FX=${FX:?}
hcfg() {   # $1 = JSON, $2 = xor key, $3 = 1 for a valid crc, 0 for a decoy (crc+1) -> C string literal on stdout
python3 - "$1" "$2" "$3" <<'PY'
import struct, sys, zlib
plain, key, ok = sys.argv[1].encode(), int(sys.argv[2]), sys.argv[3] == "1"
crc = (zlib.crc32(plain) + (0 if ok else 1)) & 0xFFFFFFFF
blob = b"HCFG" + struct.pack("<BBHI", 1, key, len(plain), crc) + bytes(c ^ key for c in plain)
print('"' + "".join("\\x%02x" % c for c in blob) + '"')
PY
}
GOOD=$(hcfg '{"campaign":"route-alpha","domain":"alpha.example","mutex":"Global\\RA","url":"https://alpha.example/c"}' 90 1)
BAD=$(hcfg '{"campaign":"route-decoy","domain":"decoy.example","mutex":"Global\\RD","url":"https://decoy.example/c"}' 90 0)
cat > alpha.c <<C
__attribute__((section(".hcfg"), used)) static const char hcfg[] = $GOOD;
int alpha_init(int v) { return v + 1; }
C
cat > beta.c <<'C'
int beta_run(int v) { return v * 3; }
C
cat > loader.c <<C
#include <dlfcn.h>
#include <stdio.h>
__attribute__((used)) static const char decoy[] = $BAD;
int alpha_init(int);
int main(void) {
  void *h = dlopen("./libbeta.so", RTLD_NOW);
  int (*run)(int) = h ? (int (*)(int))dlsym(h, "beta_run") : 0;
  printf("%d %d\n", alpha_init(1), run ? run(2) : -1);
  return h ? dlclose(h) : 1;
}
C
gcc -O2 -fPIC -shared -Wl,-soname,libalpha.so -o libalpha.so alpha.c
gcc -O2 -fPIC -shared -Wl,-soname,libbeta.so -o libbeta.so beta.c
gcc -O2 -o loader loader.c -L. -lalpha -ldl
# 1) 3-member group, role tokens in the names
cp loader d22--variant-000-loader.elf; cp libalpha.so d22--variant-000-plugin_a.so; cp libbeta.so d22--variant-000-plugin_b.so
rm -f route_3member.zip; zip -X -j -q route_3member.zip d22--variant-000-loader.elf d22--variant-000-plugin_a.so d22--variant-000-plugin_b.so
cp route_3member.zip $FX/route_3member.bin
# 2) same bytes, renamed (no role tokens), plugin first: structural roles
cp libbeta.so d23--variant-000.so; cp loader d23--variant-001.elf; cp libalpha.so d23--variant-002.so
rm -f route_renamed.zip; zip -X -j -q route_renamed.zip d23--variant-000.so d23--variant-001.elf d23--variant-002.so
cp route_renamed.zip $FX/route_renamed.bin
# 3) D15 / D16 / D21 shapes in one evidence zip (routing is per dNN-- group)
printf '#include <stdio.h>\nstatic const char c[] = %s;\nint main(void){puts(c+12);return 0;}\n' "$GOOD" > d15.c
gcc -O2 -o d15--variant-000-symbolized.elf d15.c; strip -o d15--variant-000-stripped.elf d15--variant-000-symbolized.elf
printf '(module (memory (export "memory") 1) (data (i32.const 1024) "HCFG") (func (export "f") (result i32) i32.const 7))\n' > d16.wat
wat2wasm d16.wat -o d16--variant-000-compact.wasm
printf '(module (memory (export "memory") 1) (data (i32.const 2048) "HCFG") (func (export "g") (result i32) i32.const 9))\n' > d16b.wat
wat2wasm d16b.wat -o d16--variant-000-direct.wasm
cp loader d21--variant-000-loader.elf; cp libalpha.so d21--variant-000-plugin.cmxs
rm -f route_days.zip; zip -X -j -q route_days.zip d15--variant-000-stripped.elf d15--variant-000-symbolized.elf \
  d16--variant-000-compact.wasm d16--variant-000-direct.wasm d21--variant-000-loader.elf d21--variant-000-plugin.cmxs
cp route_days.zip $FX/route_days.bin
# 4) DECOY: only the loader carries an HCFG and its crc is bad; two look-alike plugins; a text file renamed .elf
cat > loader2.c <<C
#include <stdio.h>
__attribute__((used)) static const char decoy[] = $BAD;
int main(void) { puts(decoy + 12); return 0; }
C
gcc -O2 -o loader2 loader2.c
cp loader2 d24--variant-000-loader.elf; cp libbeta.so d24--variant-000-plugin_x.so; cp libbeta.so d24--variant-000-plugin_y.so
printf 'HCFG not a binary\n' > d24--variant-000-notes.elf
rm -f route_decoy.zip; zip -X -j -q route_decoy.zip d24--variant-000-loader.elf d24--variant-000-plugin_x.so d24--variant-000-plugin_y.so d24--variant-000-notes.elf
cp route_decoy.zip $FX/route_decoy.bin
