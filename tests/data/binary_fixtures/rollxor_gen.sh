#!/bin/sh
# Rolling / index-dependent xor HCFG fixtures (key+i, key-3i, key^i, ciphertext feedback, plaintext feedback).
# Generator: blob header via system python3 zlib.crc32, the xor transforms in perl. Oracle: rollxor_oracle.sh
# (stdlib only, exhaustive, never imports lib.binary). Run from this directory.
set -e
T=${TMPDIR:-/tmp}/rollxor_gen; mkdir -p "$T"
blob() {  # blob <version> <xorkey> <json> > raw blob
  python3 -I -c 'import sys,zlib,struct;v,k,p=int(sys.argv[1],0),int(sys.argv[2],0),sys.argv[3].encode();sys.stdout.buffer.write(b"HCFG"+struct.pack("<BBHI",v,k,len(p),zlib.crc32(p))+bytes(c^k for c in p))' "$@"
}
fill() { perl -e 'srand($ARGV[0]); print map { chr(int(rand(256))) } 1..$ARGV[1]' "$1" "$2"; }
roll() { perl -0777 -pe 'BEGIN{($k,$s)=map{oct}@ARGV;@ARGV=()} $j=0; s/(.)/chr(ord($1)^(($k+$s*$j++)%256))/ges' "$1" "$2"; }
xidx() { perl -0777 -pe 'BEGIN{$k=oct shift} $j=0; s/(.)/chr(ord($1)^$k^($j++%256))/ges' "$1"; }
cbc()  { perl -0777 -pe 'BEGIN{$p=oct shift} s/(.)/$p=ord($1)^$p; chr($p)/ges' "$1"; }
chain(){ perl -0777 -pe 'BEGIN{$p=oct shift} s/(.)/$c=ord($1); $o=$c^$p; $p=$c; chr($o)/ges' "$1"; }

# 1: key+i (k0 0x37, step +1) in random data
blob 1 0x21 '{"c2":"10.9.8.7:443","beacon":"roll-heron","sleep":20,"flag":"flag{k3y_pl4s_1nd3x}"}' > "$T/b1"
{ fill 101 4100; roll 0x37 1 < "$T/b1"; fill 102 900; } > rollxor_add1_raw.bin
# 2: key-3i (k0 0xa5, step 0xfd), body > 256 bytes (keystream wraps)
blob 2 0x00 '{"c2":"198.51.100.23:8443","beacon":"roll-sub-ibis","sleep":75,"flag":"flag{subtr4ct_thr33_p3r_byt3}","note":"padding padding padding padding padding padding padding padding padding padding padding padding padding padding padding padding padding padding padding padding"}' > "$T/b2"
{ fill 201 7777; roll 0xa5 0xfd < "$T/b2"; fill 202 333; } > rollxor_sub3_raw.bin
# 3: key ^ index (k0 0x5c)
blob 1 0x11 '{"c2":"203.0.113.88:9000","beacon":"idx-plover","sleep":3,"flag":"flag{x0r_w1th_th3_1nd3x}"}' > "$T/b3"
{ fill 301 2222; xidx 0x5c < "$T/b3"; fill 302 444; } > rollxor_xoridx.bin
# 4: ciphertext feedback (stored[j] = blob[j] ^ stored[j-1], iv 0x99)
blob 3 0x42 '{"c2":"192.0.2.200:53","beacon":"cbc-gannet","sleep":11,"flag":"flag{x0r_w1th_pr3v_c1ph3r}"}' > "$T/b4"
{ fill 401 3000; cbc 0x99 < "$T/b4"; fill 402 500; } > rollxor_cbc.bin
# 5: plaintext feedback (stored[j] = blob[j] ^ blob[j-1], iv 0x0d)
blob 1 0x7e '{"c2":"172.31.0.4:4443","beacon":"chain-avocet","sleep":44,"flag":"flag{x0r_w1th_pr3v_pl41n}"}' > "$T/b5"
{ fill 501 5050; chain 0x0d < "$T/b5"; fill 502 600; } > rollxor_chain.bin
# decoy: key+i blob with a corrupted crc byte, a cbc'd blob truncated mid-body, a bare rolled 'HCFG' magic
blob 1 0x21 '{"c2":"10.0.0.1:1","beacon":"decoy","sleep":1,"flag":"flag{n0t_th3_r34l_0n3}"}' > "$T/d"
perl -0777 -pe 'substr($_,8,1)=chr(ord(substr($_,8,1))^1)' "$T/d" > "$T/dbad"
{ fill 601 2000; roll 0x37 1 < "$T/dbad"; fill 602 300; cbc 0x99 < "$T/d" | head -c 50; fill 603 300;
  printf 'HCFG\0\0\0\0' | roll 0x10 5; fill 604 300; } > rollxor_decoy.bin
