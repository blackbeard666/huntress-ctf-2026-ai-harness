#!/bin/sh
# Byte-map HCFG fixtures (nibble swap / rotate-left / NOT / add-sub constant, raw or before/after base64).
# Generator: blob header via system python3 zlib.crc32, the byte maps in perl, base64 by coreutils `base64`.
# Oracle: bytemap_oracle.py (stdlib only, never imports lib.binary). Run from this directory.
set -e
T=${TMPDIR:-/tmp}/bytemap_gen; mkdir -p "$T"
blob() {  # blob <version> <xorkey> <json> > raw blob
  python3 -I -c 'import sys,zlib,struct;v,k,p=int(sys.argv[1],0),int(sys.argv[2],0),sys.argv[3].encode();sys.stdout.buffer.write(b"HCFG"+struct.pack("<BBHI",v,k,len(p),zlib.crc32(p))+bytes(c^k for c in p))' "$@"
}
fill() { perl -e 'srand($ARGV[0]); print map { chr(int(rand(256))) } 1..$ARGV[1]' "$1" "$2"; }
nib()  { perl -0777 -pe 's/(.)/chr(((ord($1)<<4)|(ord($1)>>4))&255)/ges'; }
rol()  { perl -0777 -pe 'BEGIN{$r=shift} s/(.)/chr(((ord($1)<<$r)|(ord($1)>>(8-$r)))&255)/ges' "$1"; }
inv()  { perl -0777 -pe '$_ = ~$_'; }
add()  { perl -0777 -pe 'BEGIN{$k=shift} s/(.)/chr((ord($1)+$k)%256)/ges' "$1"; }

# 1: nibble-swapped raw blob in random data
blob 1 0x21 '{"c2":"10.20.30.40:443","beacon":"nib-otter","sleep":30,"flag":"flag{n1bbl3s_sw4pp3d_4r0und}"}' > "$T/b1"
{ fill 11 3001; nib < "$T/b1"; fill 12 777; } > bytemap_nibswap_raw.bin
# 2: base64 text (coreutils, one line) then each char rotated left 3 bits; Go-style: packed after other text
blob 2 0x5a '{"c2":"192.0.2.77:8080","beacon":"rol-lynx","sleep":12,"flag":"flag{r0t4t3_l3ft_thr33}"}' > "$T/b2"
{ fill 21 2050; printf 'runtime.goexit'; base64 -w0 < "$T/b2" | rol 3; printf '\0'; fill 22 500; } > bytemap_rol3_after_b64.bin
# 3: base64 of NOT(blob) as a C string (transform BEFORE base64)
blob 1 0x00 '{"c2":"198.51.100.9:53","beacon":"not-heron","sleep":5,"flag":"flag{b1tw1s3_n0t_b4s364}"}' > "$T/b3"
{ fill 31 4096; printf '\0'; inv < "$T/b3" | base64 -w0; printf '\0'; fill 32 300; } > bytemap_b64_not.bin
# 4: raw blob + 0x2d per byte
blob 3 0x13 '{"c2":"203.0.113.50:8443","beacon":"add-falcon","sleep":60,"flag":"flag{4dd_c0nst4nt_2d}"}' > "$T/b4"
{ fill 41 5555; add 45 < "$T/b4"; fill 42 1000; } > bytemap_add_raw.bin
# 5: base64 (wrapped at 76, coreutils default) of (blob - 0x11), glued to preceding base64-alphabet text (phase test)
blob 1 0x44 '{"c2":"10.66.6.6:9001","beacon":"sub-marten","sleep":90,"flag":"flag{sub_th3n_b4s364_w1d3}","pad":"xxxxxxxxxxxxxxxxxxxxxxxx"}' > "$T/b5"
{ fill 51 3333; printf 'ConfigLoaderV2'; add 239 < "$T/b5" | base64; printf '\0'; fill 52 222; } > bytemap_sub_before_b64.bin
# 6: base64 text then +7 per char
blob 2 0x6b '{"c2":"172.16.9.9:4444","beacon":"add-b64-wren","sleep":7,"flag":"flag{b4s364_th3n_4dd}"}' > "$T/b6"
{ fill 61 1500; base64 -w0 < "$T/b6" | add 7; printf '\0'; fill 62 400; } > bytemap_add_after_b64.bin
# decoy: nibble-swapped blob with a corrupted crc byte, base64-of-NOT text truncated mid-body, rol5 'HCFG' magic alone
blob 1 0x21 '{"c2":"10.0.0.1:1","beacon":"decoy","sleep":1,"flag":"flag{n0t_th3_r34l_0n3}"}' > "$T/d"
perl -0777 -pe 'substr($_,8,1)=chr(ord(substr($_,8,1))^1)' "$T/d" > "$T/dbad"
{ fill 71 2000; nib < "$T/dbad"; fill 72 300; printf '\0'; inv < "$T/d" | base64 -w0 | head -c 60; printf '\0';
  printf 'HCFG\0\0\0\0' | rol 5; fill 73 300; } > bytemap_decoy.bin
