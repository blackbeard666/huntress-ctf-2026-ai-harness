#!/bin/bash
# usage: zsec_gen.sh outdir   -- compressed-ELF-section fixtures; tools: gcc, GNU objcopy 2.46, system python3 stdlib
# (struct/zlib/json: the HCFG blob, a hand-written Elf64_Chdr + zlib wbits=10 stream, the sh_flags |= SHF_COMPRESSED
# patch). Never lib.binary.
set -e
O=${1:-.}; T=$(mktemp -d); cd "$T"
printf 'int main(){return 0;}' > m.c; gcc -O0 -s -o m m.c
blob() { python3 -c 'import json,struct,sys,zlib
p=json.dumps(json.loads(sys.argv[1]),separators=(",",":")).encode(); c=zlib.crc32(p)^int(sys.argv[2])
sys.stdout.buffer.write(b"HCFG\x01\x00"+struct.pack("<HI",len(p),c)+p)' "$1" "${2:-0}"; }
J1='{"c2":"203.0.113.77:8443","campaign":"shf-compressed","jitter":3,"flag":"flag{chdr_z1ib_s3ction}"}'
J2='{"c2":"198.51.100.9:443","campaign":"zstd-chdr","jitter":11,"flag":"flag{zstd_ch_typ3_2}"}'
J3='{"c2":"192.0.2.61:8080","campaign":"zdebug-legacy","jitter":5,"flag":"flag{zl1b_u64be_s1ze}"}'
J4='{"c2":"203.0.113.200:9001","campaign":"chdr-w10","jitter":2,"flag":"flag{h4nd_wr1tten_chdr}"}'
mk() {  # mk out json compress-type finalname [prefix-bytes]
  { printf '%s' "$5"; blob "$2"; head -c 600 /dev/zero; } > sec
  objcopy --add-section .debug_hcfg=sec m b; objcopy --compress-debug-sections=$3 b c
  if [ "$3" = zlib-gnu ]; then cp c "$O/$1"; else objcopy --rename-section .debug_hcfg=$4 c "$O/$1"; fi; }
mk zsec_gabi_zlib.bin "$J1" zlib .hcfg
mk zsec_gabi_zstd.bin "$J2" zstd .hcfg 'cfg-prefix:'
mk zsec_zdebug_gnu.bin "$J3" zlib-gnu .zdebug_hcfg
# manual: .hcfg = Elf64_Chdr{1,0,ch_size,8} + zlib(level 9, wbits 10: CMF 0x28, dynamic Huffman) behind a 1.2 MiB
# random .junk section (> the 1 MiB raw-deflate brute cap) -> no zlib/deflate anchor sees it
head -c 1300000 /dev/urandom > junk
{ blob "$J4"; python3 -c 'import random;random.seed(7);print(" ".join(random.choice(["alpha","beta","gamma","delta","eps"]) for _ in range(300)))'; } > sec
python3 -c 'import struct,sys,zlib
s=open("sec","rb").read(); c=zlib.compressobj(9,zlib.DEFLATED,10); z=c.compress(s)+c.flush()
open("pay","wb").write(struct.pack("<IIQQ",1,0,len(s),8)+z)'
objcopy --add-section .junk=junk --add-section .hcfg=pay m b
python3 -c 'import struct,sys
d=bytearray(open("b","rb").read()); so=struct.unpack_from("<Q",d,40)[0]; es,n,sx=struct.unpack_from("<3H",d,58)
sh=lambda k: struct.unpack_from("<IIQQQQ",d,so+k*es); st=sh(sx); names=d[st[4]:st[4]+st[5]]
k=[k for k in range(n) if names[sh(k)[0]:].split(b"\0")[0]==b".hcfg"][0]
struct.pack_into("<Q",d,so+k*es+8,sh(k)[2]|0x800); struct.pack_into("<Q",d,so+k*es+48,8)
open(sys.argv[1],"wb").write(d)' "$O/zsec_manual_w10.bin"
# decoy: '.zdebug_hcfg' impostor (no ZLIB header, random bytes) + '.hcfg' holding Chdr-looking bytes + zlib of a
# BAD-crc blob with SHF_COMPRESSED clear -> no compressed section, no valid HCFG
head -c 300 /dev/urandom > imp
blob "$J1" 1 > bad; python3 -c 'import struct,zlib;s=open("bad","rb").read()
open("fake","wb").write(struct.pack("<IIQQ",1,0,len(s),1)+zlib.compress(s,9))'
objcopy --add-section .zdebug_hcfg=imp --add-section .hcfg=fake m "$O/zsec_decoy_impostor.bin"
cd /; rm -rf "$T"
