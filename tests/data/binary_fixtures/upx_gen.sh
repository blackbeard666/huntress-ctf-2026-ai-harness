#!/bin/sh
# UPX fixtures: gcc (ELF) / lief add_section on setuptools cli-64.exe (PE) carrying an HCFG blob in a `.hcfg` section,
# packed with the real `upx -9` (4.2.4); *_scrub = every `UPX!` zeroed + UPX0/UPX1 renamed .pk0/.pk1 (upx -d refuses).
# usage: sh upx_gen.sh <outdir>  (needs gcc, upx, python3 with lief)
set -e; O=$(cd "$1" && pwd); W=$(mktemp -d); cd "$W"
PY=${PY:-python3}
blob() { $PY -c 'import zlib,struct,sys,json;p=json.dumps({"c2":sys.argv[1],"beacon":sys.argv[2],"sleep":int(sys.argv[3]),"flag":sys.argv[4]},separators=(",",":")).encode();k=0x5a;b=b"HCFG"+struct.pack("<BBHI",1,k,len(p),zlib.crc32(p))+bytes(a^k for a in p);sys.stdout.buffer.write(b)' "$@"; }
blob 10.20.30.40:443 upx-elf 30 'flag{upx_3lf_unp4ck3d}' > elf.blob
blob 172.16.9.9:8080 upx-pe 60 'flag{upx_p3_unp4ck3d}' > pe.blob
$PY -c 'import sys;print("unsigned char hcfg[] __attribute__((section(\".hcfg\"),used)) = {"+",".join(str(b) for b in open("elf.blob","rb").read())+"};")' > elf_blob.h
echo 'unsigned char hcfg[] = {1,2,3};' > none_blob.h
cat > m.c <<'C'
#include <stdio.h>
#include <string.h>
#include BLOB
static char pad[20000] = {1};
int main(int c, char**v){ for(int i=0;i<c;i++) pad[i]=v[0][0]; printf("hello %d %d\n", hcfg[1], pad[3]); return strlen(v[0]); }
C
gcc -O2 -DBLOB='"elf_blob.h"' -o elf_plain m.c
gcc -O2 -DBLOB='"none_blob.h"' -DIMPOSTOR -o none_plain m.c
$PY -c 'import lief;pe=lief.parse(__import__("sys").argv[1]);b=open("pe.blob","rb").read();s=lief.PE.Section(".hcfg");s.content=list(b+bytes(512-len(b)));s.characteristics=0x40000040;pe.add_section(s);pe.write("pe_plain.exe")' "${PE_BASE:-$OLDPWD/../../../tools/pychepy/setuptools/cli-64.exe}"
cp elf_plain upx_elf.bin; upx -9 -q upx_elf.bin >/dev/null
cp pe_plain.exe upx_pe.bin; upx -9 -q upx_pe.bin >/dev/null
cp none_plain upx_decoy_nohcfg.bin; upx -9 -q upx_decoy_nohcfg.bin >/dev/null
scrub='import sys;d=open(sys.argv[1],"rb").read().replace(b"UPX!",bytes(4)).replace(b"UPX0\0",b".pk0\0").replace(b"UPX1\0",b".pk1\0");open(sys.argv[2],"wb").write(d)'
$PY -c "$scrub" upx_elf.bin upx_elf_scrub.bin
$PY -c "$scrub" upx_pe.bin upx_pe_scrub.bin
# impostor: an UNPACKED ELF whose .rodata says UPX!/UPX0/UPX1 and holds a crc-broken HCFG header -> no valid blob
$PY -c 'import sys;d=bytearray(open("elf_plain","rb").read());i=d.find(b"HCFG");d[i+20]^=0xff;d+=b"UPX!\x0e\x16\x02\x09UPX0\0UPX1\0";open("upx_decoy_impostor.bin","wb").write(d)'
cp upx_elf.bin upx_elf_scrub.bin upx_pe.bin upx_pe_scrub.bin upx_decoy_nohcfg.bin upx_decoy_impostor.bin "$O/"
rm -rf "$W"
