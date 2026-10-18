#!/bin/bash
# usage: locate_gen.sh out.bin kind   -- fixtures for lib.binary.locate_offset (file offset -> section/segment/VA/RVA)
# The probe offset is the first file occurrence of the 12-byte marker LOCMARK<kind-tag> (grep -obUa).
#  elf_rodata  gcc -O0 -no-pie: const char[] in .rodata          elf_hcfg  gcc -O2 -pie: section(".hcfg") const
#  elf_sstrip  elf_rodata with every section header dropped (python3 zeroes e_shoff/e_shnum/e_shstrndx, truncates)
#  pe_rdata    zig cc -target x86_64-windows-gnu: const in .rdata  pe_data  same, writable global in .data
#  macho_const zig cc -target x86_64-macos: const in __TEXT,__const  macho_data  aarch64-macos: writable __DATA,__data
#  wasm_seg    wat2wasm: 2 active data segments (i32.const 1024 / 4096), marker 5 bytes into segment 1
#  decoy_text  plain text carrying the marker (no container -> null)
set -e
O=$(realpath -m "$1"); K="$2"; R=$(cd "$(dirname "$0")/../../.." && pwd); W=$(mktemp -d)
Z() { (cd "$W" && PYTHONPATH="$R/tools/pyziglang" python3 -m ziglang cc "$@"); }
cat > "$W/ro.c" <<'C'
#include <stdio.h>
const char pad[] = "rodata-padding-before-the-marker";
const char blob[] = "LOCMARK_RODA:payload";
int main(void) { puts(pad); puts(blob); return 0; }
C
cat > "$W/hc.c" <<'C'
#include <stdio.h>
__attribute__((section(".hcfg"), used)) const char blob[] = "xxLOCMARK_HCFG:payload";
int main(void) { puts(blob); return 0; }
C
cat > "$W/rw.c" <<'C'
#include <stdio.h>
int counter = 7;
char blob[] = "zzzLOCMARK_DATA:payload";
int main(void) { blob[0] ^= counter; puts(blob); return 0; }
C
case "$K" in
  elf_rodata) gcc -O0 -no-pie -o "$O" "$W/ro.c" ;;
  elf_hcfg) gcc -O2 -pie -fPIE -o "$O" "$W/hc.c" ;;
  elf_sstrip) gcc -O0 -no-pie -o "$W/a" "$W/ro.c"
     python3 -c 'import struct,sys; d=bytearray(open(sys.argv[1],"rb").read()); so=struct.unpack_from("<Q",d,40)[0]
d[40:48]=bytes(8); d[60:64]=bytes(4); open(sys.argv[2],"wb").write(bytes(d[:so]))' "$W/a" "$O" ;;
  pe_rdata) Z -target x86_64-windows-gnu -O0 -o p.exe ro.c && cp "$W/p.exe" "$O" ;;
  pe_data) Z -target x86_64-windows-gnu -O0 -o p.exe rw.c && cp "$W/p.exe" "$O" ;;
  macho_const) Z -target x86_64-macos -O0 -o m ro.c && cp "$W/m" "$O" ;;
  macho_data) Z -target aarch64-macos -O0 -o m rw.c && cp "$W/m" "$O" ;;
  wasm_seg) cat > "$W/m.wat" <<'WAT'
(module (memory 1)
  (data (i32.const 1024) "first-segment-bytes")
  (data (i32.const 4096) "pad::LOCMARK_WASM:payload")
  (func (export "f") (result i32) i32.const 4096))
WAT
     wat2wasm -o "$O" "$W/m.wat" ;;
  decoy_text) printf 'not a binary, just text\nLOCMARK_TEXT:payload\n\x7fELF later in the file\n' > "$O" ;;
esac
rm -rf "$W"
