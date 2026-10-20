#!/bin/bash
# Appended-archive (SFX) fixtures: gcc ELF stub + an archive written by the standard tool (zip / tar / mksquashfs / 7z).
# usage (repo root): bash tests/data/binary_fixtures/sfx_gen.sh   -> sfx_*.bin (expected values: sfx_oracle.sh)
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"; W="$(mktemp -d "${TMPDIR:-/tmp}/sfxgen.XXXX")"; trap 'rm -rf "$W"' EXIT
cd "$W"
printf 'int main(void){return 0;}\n' > s.c && gcc -O0 -s -o stub s.c
printf 'const char *decoy = "ustar  this-is-not-a-tar hsqs not-squashfs 7z PK";\nint main(void){return decoy[0]==0;}\n' > d.c
gcc -O0 -s -o stub_decoy d.c
mkdir -p p/conf p/bin
printf '{"magic":"HCFG","flag":"ANS-0123456789abcdef","build":19}\n' > p/HCFG.json
printf 'readme for the payload\n' > p/README.txt
head -c 9000 /dev/zero | tr '\0' 'A' > p/bin/blob.dat
printf 'key=value\n' > p/conf/app.ini
find p -exec touch -h -d '2026-10-01 00:00:00Z' {} +
# 1. zip, central directory relative to the archive start (plain `cat stub a.zip`, like escript / zipapp)
(cd p && zip -X -q -r ../a.zip HCFG.json README.txt bin conf)
cat stub a.zip > "$D/sfx_elf_zip_relative.bin"
# 2. same zip with `zip -A` (offsets rewritten to absolute file offsets, Info-ZIP SFX style)
cat stub a.zip > sfxA && zip -q -A sfxA && cp sfxA "$D/sfx_elf_zip_adjusted.bin"
# 3. ZipCrypto zip with the GM password 'infected'
(cd p && zip -X -q -P infected ../e.zip HCFG.json README.txt)
cat stub e.zip > "$D/sfx_elf_zip_encrypted.bin"
# 4. ustar tar
tar --format=ustar --owner=0 --group=0 --numeric-owner --mtime='2026-10-01 00:00:00Z' -C p -cf a.tar HCFG.json README.txt bin conf
cat stub a.tar > "$D/sfx_elf_tar.bin"
# 5./6. AppImage-style: runtime ELF + squashfs (gzip; xz with a fragment + nested dirs)
mksquashfs p g.sqfs -comp gzip -noappend -all-root -mkfs-time 0 -all-time 0 -quiet >/dev/null
cat stub g.sqfs > "$D/sfx_elf_squashfs_gzip.bin"
mksquashfs p x.sqfs -comp xz -noappend -all-root -mkfs-time 0 -all-time 0 -quiet >/dev/null
cat stub x.sqfs > "$D/sfx_elf_squashfs_xz.bin"
# 7. 7z (signature header only; members not decoded)
(cd p && /usr/bin/7z a -bd -y ../a.7z HCFG.json README.txt >/dev/null)
cat stub a.7z > "$D/sfx_elf_7z.bin"
# decoys: magic strings in .rodata with no archive behind them; a truncated squashfs
cp stub_decoy "$D/sfx_decoy_magic_strings.bin"
cat stub g.sqfs | head -c $(( $(stat -c%s stub) + 200 )) > "$D/sfx_decoy_trunc_squashfs.bin"
