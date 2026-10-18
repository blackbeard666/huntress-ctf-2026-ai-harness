#!/bin/sh
# prov_*.bin generator (provenance_facts): independent WRITERS = gcc/ld (--build-id, -g DWARF), rustc, MSVC-built
# setuptools launcher (Rich header), dotnet build (RSDS CodeView). usage: sh prov_gen.sh <out dir>
set -e
OUT=$(cd "$1" && pwd); ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
W=$(mktemp -d); cd "$W"
printf '#include <stdio.h>\nint main(void){puts("HCFG prov");return 0;}\n' > hello.c
gcc -g -O1 -Wl,--build-id=sha1 -o "$OUT/prov_gcc_g_sha1.bin" hello.c
gcc -O2 -Wl,--build-id=md5 -s -o "$OUT/prov_gcc_md5_stripped.bin" hello.c
gcc -O2 -Wl,--build-id=none -s -o "$OUT/prov_decoy_gcc_nobuildid.bin" hello.c
objcopy --remove-section .comment "$OUT/prov_decoy_gcc_nobuildid.bin"
printf 'fn main(){println!("HCFG prov");}\n' > hello.rs
rustc -C opt-level=s -C strip=symbols -o "$OUT/prov_rust.bin" hello.rs
cp "$ROOT/tools/pychepy/setuptools/cli-64.exe" "$OUT/prov_pe_msvc_rich.bin"   # setuptools 68 launcher, MSVC link.exe (Rich, no RSDS)
cp "$OUT/rsrc_pe_overlay.bin" "$OUT/prov_pe_dotnet_rsds.bin"   # dotnet build output (see rsrc_pe_overlay.json)
# decoy: an ELF header impostor truncated after 64 bytes + a text file renamed .bin
head -c 64 "$OUT/prov_gcc_g_sha1.bin" > "$OUT/prov_decoy_truncated_elf.bin"
printf 'GCC: (fake) 1.0\0RSDS not a pe\n' > "$OUT/prov_decoy_text.bin"
rm -rf "$W"
