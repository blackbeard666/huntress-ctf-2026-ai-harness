#!/bin/bash
# Generates the dynlink_* fixtures (run from an empty scratch dir; FX = tests/data/binary_fixtures). gcc only.
set -e
FX=${FX:?}
cat > plug.c <<'C'
#include <stdio.h>
__attribute__((section(".hcfg"), used)) static const char hcfg[] = "HCFG\x01\x00{\"campaign\":\"dl-fixture\"}";
static int hits;
int hplug_init(int v) { hits += v; return hits; }
void hplug_register_handlers(void (*cb)(const char *)) { cb("ping"); }
int hplug_version(void) { return 3; }
C
cat > load.c <<'C'
#include <dlfcn.h>
#include <stdio.h>
static void cb(const char *s) { puts(s); }
int main(void) {
  void *h = dlopen("./libhplug.so", RTLD_NOW);
  if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
  int (*init)(int) = (int (*)(int))dlsym(h, "hplug_init");
  void (*reg)(void (*)(const char *)) = (void (*)(void (*)(const char *)))dlsym(h, "hplug_register_handlers");
  printf("%d\n", init(5)); reg(cb);
  return dlclose(h);
}
C
gcc -O2 -fPIC -shared -o libhplug.so plug.c
gcc -O2 -o loader_pie load.c -ldl
cp loader_pie $FX/dynlink_c_pie_o2.bin; cp libhplug.so $FX/dynlink_c_pie_o2.plugin.bin
# -O0 non-PIE -fno-plt: mov edi,imm / lea+mov reg,reg / call [rip+got]
sed -e 's#./libhplug.so#/opt/hctf/plugins/libnoplt.so#' -e 's/hplug_init/noplt_module_init/' -e 's/hplug_register_handlers/noplt_register/' load.c > load2.c
sed -e 's/hplug_init/noplt_module_init/' -e 's/hplug_register_handlers/noplt_register/' -e 's/hplug_version/noplt_version/' plug.c > plug2.c
gcc -O0 -fPIC -shared -o libnoplt.so plug2.c
gcc -O0 -no-pie -fno-plt -o loader_noplt load2.c -ldl
cp loader_noplt $FX/dynlink_c_noplt_o0.bin; cp libnoplt.so $FX/dynlink_c_noplt_o0.plugin.bin
# decoy: a plain program (no dl* imports) + a plain .so (no caml_plugin_header, no init/register export)
printf '#include <stdio.h>\nint main(void){puts("hi");return 0;}\n' > plain.c
printf 'int add2(int a,int b){return a+b;}\n' > lib.c
gcc -O2 -o plain plain.c; gcc -O2 -fPIC -shared -o libplain.so lib.c
cp plain $FX/dynlink_decoy_noload.bin; cp libplain.so $FX/dynlink_decoy_noload.plugin.bin
# synthetic OCaml-shaped plugin: caml_plugin_header = a hand-written Marshal (intext 0x8495A6BE) dynheader
python3 - > hdr.inc <<'PY'
import struct
S = lambda b: bytes([0x20 | len(b)]) + b                  # PREFIX_SMALL_STRING
B = lambda tag, *f: bytes([0x80 | len(f) << 4 | tag]) + b"".join(f)   # PREFIX_SMALL_BLOCK
L = lambda *xs: (B(0, xs[0], L(*xs[1:])) if xs else b"\x40")         # list, [] = int 0
crc = bytes(range(0x10, 0x20))
some = lambda d: B(0, S(d))
u1 = B(0, S(b"Plugin_042"), S(crc), L(B(0, S(b"Stdlib"), some(bytes(16))), B(0, S(b"Plugin_042"), some(crc))),
       L(B(0, S(b"Helper"), some(b"\xaa" * 16))), L(S(b"Plugin_042")))
u2 = B(0, S(b"Helper"), S(b"\xaa" * 16), L(), L(), L(S(b"Helper")))
body = B(0, S(b"Caml2007D002"), L(u2, u1))
blob = struct.pack(">IIIII", 0x8495A6BE, len(body), 0, 0, 0) + body
print(",".join(str(c) for c in blob))
PY
printf 'const unsigned char caml_plugin_header[] = {\n#include "hdr.inc"\n};\nint camlPlugin_042__entry(void){return 0;}\nint camlHelper__entry(void){return 1;}\n' > cmxs.c
gcc -O2 -fPIC -shared -o synth.cmxs cmxs.c
cp synth.cmxs $FX/dynlink_ocaml_synth.plugin.bin
# decoy cmxs: caml_plugin_header points at garbage (wrong intext magic)
printf 'const unsigned char caml_plugin_header[] = "Caml1999X0xxNOTMARSHAL";\nint camlFoo__entry(void){return 0;}\n' > bad.c
gcc -O2 -fPIC -shared -o bad.cmxs bad.c
cp bad.cmxs $FX/dynlink_decoy_badheader.plugin.bin
