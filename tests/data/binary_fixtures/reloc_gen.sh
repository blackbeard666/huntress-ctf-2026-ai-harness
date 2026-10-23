#!/bin/sh
# Fixture generator for lib.binary.elf_reloc_facts / the hcfg_scan 'reloc-ptrtable' pass.
# usage: FX=<repo>/tests/data/binary_fixtures sh reloc_gen.sh   (run from an empty scratch dir; gcc 15 + GNU ld, x86-64)
# HCFG blobs are built here by python3 stdlib (zlib.crc32 + struct), NOT by lib.binary.
set -eu
FX=${FX:?set FX to tests/data/binary_fixtures}
# --- facts fixtures: lazy PIE / BIND_NOW PIE / non-PIE with COPY + IRELATIVE ---------------------------------------
cat > facts.c <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern char **environ;
static int impl_a(int x) { return x + 1; }
static int (*resolve_pick(void))(int) { return impl_a; }
int pick(int) __attribute__((ifunc("resolve_pick")));
static int h0(int x) { return x * 3; }
static int h1(int x) { return x ^ 7; }
int (*const handlers[])(int) = {h0, h1, impl_a};
int main(int argc, char **argv) {
    char *p = malloc(32);
    strcpy(p, argc > 1 ? argv[1] : "x");
    printf("%zu %d %d %s\n", strlen(p), handlers[argc % 3](argc), pick(argc), environ[0] ? "e" : "-");
    fputs("done\n", stdout);
    free(p);
    return 0;
}
EOF
gcc -O1 -fPIE -pie -Wl,-z,relro -Wl,-z,lazy facts.c -o "$FX/reloc_pie_lazy.bin"
gcc -O1 -fPIE -pie -Wl,-z,relro -Wl,-z,now facts.c -o "$FX/reloc_pie_now.bin"
gcc -O1 -fno-pie -no-pie -Wl,-z,norelro -Wl,-z,lazy facts.c -o "$FX/reloc_nopie_copy.bin"
# --- HCFG pieces reachable only through RELATIVE addends ------------------------------------------------------------
# blob = "HCFG" ver key len crc32(plain) + plain^key ; chunks defined in SHUFFLED order, the pointer table in true order
mkblob() {  # $1 json  $2 key  $3 mode(ptrlen|strtab)  $4 badcrc(0|1) -> hc.c
python3 - "$1" "$2" "$3" "$4" <<'EOF'
import sys, struct, zlib, base64
cfg, key, mode, bad = sys.argv[1].encode(), int(sys.argv[2]), sys.argv[3], sys.argv[4] == "1"
blob = b"HCFG" + struct.pack("<BBHI", 1, key, len(cfg), zlib.crc32(cfg) ^ (0x5A5A if bad else 0)) + bytes(c ^ key for c in cfg)
data = blob if mode == "ptrlen" else base64.b64encode(blob)
n = 5
cut = [len(data) * k // n for k in range(n + 1)]
parts = [data[cut[k]:cut[k + 1]] for k in range(n)]
order = [3, 0, 4, 1, 2]            # file (definition) order != table order
src = ["#include <stdio.h>", "#include <string.h>"]
for k in order:
    if mode == "ptrlen":
        src.append("static const unsigned char c%d[] __attribute__((used)) = {%s};" % (k, ",".join("0x%02x" % b for b in parts[k])))
    else:
        src.append('static const char c%d[] __attribute__((used)) = "%s";' % (k, parts[k].decode()))
if mode == "ptrlen":
    src.append("struct piece { const unsigned char *p; unsigned long n; };")
    src.append("const struct piece cfg_tab[] = {%s};" % ", ".join("{c%d, sizeof c%d}" % (k, k) for k in range(n)))
    src.append("int main(void){ unsigned long t = 0; for (int i = 0; i < %d; i++) t += cfg_tab[i].n; printf(\"%%lu\\n\", t); return 0; }" % n)
else:
    src.append("const char *const cfg_tab[] = {%s};" % ", ".join("c%d" % k for k in range(n)))
    src.append("int main(void){ size_t t = 0; for (int i = 0; i < %d; i++) t += strlen(cfg_tab[i]); printf(\"%%zu\\n\", t); return 0; }" % n)
open("hc.c", "w").write("\n".join(src) + "\n")
EOF
}
# zero the RELATIVE-relocated pointer slots of cfg_tab on disk (= lld's default: RELA addends not applied in place)
zero_tab() {  # $1 elf
python3 - "$1" <<'EOF'
import sys, subprocess, re
p = sys.argv[1]
sym = subprocess.run(["readelf", "-sW", p], capture_output=True, text=True).stdout
m = re.search(r"\s([0-9a-f]+)\s+(\d+)\s+OBJECT\s+GLOBAL\s+\w+\s+\S+\s+cfg_tab$", sym, re.M)
va, sz = int(m.group(1), 16), int(m.group(2))
secs = subprocess.run(["readelf", "-SW", p], capture_output=True, text=True).stdout
for s in re.finditer(r"\]\s+(\S+)\s+\S+\s+([0-9a-f]{16})\s+([0-9a-f]+)\s+([0-9a-f]+)", secs):
    a, o, n = int(s.group(2), 16), int(s.group(3), 16), int(s.group(4), 16)
    if a and a <= va < a + n:
        off = o + va - a
rel = subprocess.run(["readelf", "-rW", p], capture_output=True, text=True).stdout
b = bytearray(open(p, "rb").read())
for r in re.finditer(r"^([0-9a-f]{16})\s+\S+\s+R_X86_64_RELATIVE\s", rel, re.M):
    ro = int(r.group(1), 16)
    if va <= ro < va + sz:
        b[off + ro - va:off + ro - va + 8] = bytes(8)
open(p, "wb").write(bytes(b))
EOF
}
mkblob '{"campaign":"RL-1","domain":"got.reloc.example.invalid","mutex":"Global\\HRELOC1"}' 91 ptrlen 0
gcc -O1 -fPIE -pie -Wl,-z,now hc.c -o "$FX/reloc_hcfg_ptrlen.bin"; zero_tab "$FX/reloc_hcfg_ptrlen.bin"
mkblob '{"campaign":"RL-2","domain":"relative.addend.example.invalid","mutex":"Global\\HRELOC2","port":8443}' 44 strtab 0
gcc -O1 -fPIE -pie -Wl,-z,now hc.c -o "$FX/reloc_hcfg_strtab.bin"; zero_tab "$FX/reloc_hcfg_strtab.bin"
mkblob '{"campaign":"RL-3","domain":"decoy.reloc.example.invalid","mutex":"Global\\HRELOC3"}' 17 ptrlen 1
gcc -O1 -fPIE -pie -Wl,-z,now hc.c -o "$FX/reloc_decoy_badcrc.bin"; zero_tab "$FX/reloc_decoy_badcrc.bin"
# --- decoy: an ELF-looking text file --------------------------------------------------------------------------------
printf 'ELF relocation notes: R_X86_64_JUMP_SLOT puts, R_X86_64_RELATIVE 0x1140; HCFG lives here (not really)\n' > "$FX/reloc_decoy_text.bin"
