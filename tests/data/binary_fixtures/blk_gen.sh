#!/bin/sh
# Block/stream-cipher HCFG fixtures (aes-tea-chacha-hcfg). Writers: `openssl enc` (AES ECB/CBC/CTR), python
# `cryptography` ChaCha20 (NOT pycryptodome, which lib.binary uses), pure-Perl XTEA (blk_xtea.pl). Oracles: blk_oracle.sh
# (`openssl enc -d` for AES/ChaCha20, perl XTEA decrypt) + a python crc/json check. Run from this directory.
set -e
PY=${PY:-../../../.venv/bin/python}
T=${TMPDIR:-/tmp}
blob() {   # blob <ver> <xorbyte> <json> -> HCFG header + body on stdout
  $PY -c 'import sys,zlib,struct;v,k,p=int(sys.argv[1],0),int(sys.argv[2],0),sys.argv[3].encode();sys.stdout.buffer.write(b"HCFG"+struct.pack("<BBHI",v,k,len(p),zlib.crc32(p))+bytes(c^k for c in p))' "$@"
}
rnd() { $PY -c 'import random,sys;r=random.Random(int(sys.argv[1]));sys.stdout.buffer.write(bytes(r.randrange(256) for _ in range(int(sys.argv[2]))))' "$@"; }
hexs() { printf '%s' "$1" | xxd -p | tr -d '\n'; }
SBOX=$(printf '637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0' | xxd -r -p | xxd -p | tr -d '\n')
TE0=c66363a5f87c7c84ee777799f67b7b8d
# 1: AES-128-CBC, key + IV = adjacent 16-char C strings, ciphertext 600 B later; S-box in .rodata
blob 1 0x41 '{"c2":"198.51.100.77:8443","beacon":"aes-cbc-wren","sleep":30,"flag":"flag{a3s_cbc_k3y_n3xt_d00r}"}' > $T/p1
{ rnd 11 3000; printf "$SBOX" | xxd -r -p; rnd 12 900; printf '\0Sup3rS3cr3tK3y!!\0InitVector123456\0'; rnd 13 600;
  openssl enc -aes-128-cbc -K $(hexs 'Sup3rS3cr3tK3y!!') -iv $(hexs 'InitVector123456') -in $T/p1; rnd 14 700; } > blk_aes_cbc_strkey.bin
# 2: AES-256-ECB, key = sha256("campaign:nightjar-2026"), the string 1.5 KB before the ciphertext; Te0 table only
blob 2 0x00 '{"c2":"nightjar.example.net:443","beacon":"aes-ecb-sha","sleep":120,"flag":"flag{sha256_d3r1v3d_k3y}"}' > $T/p2
K2=$(printf 'campaign:nightjar-2026' | openssl dgst -sha256 -r | cut -c1-64)
{ rnd 21 5000; printf "$TE0" | xxd -r -p; rnd 22 300; printf '\0campaign:nightjar-2026\0'; rnd 23 1500;
  openssl enc -aes-256-ecb -K $K2 -in $T/p2; rnd 24 400; } > blk_aes_ecb_sha256.bin
# 3: AES-256-CTR, raw 32-byte key + raw 16-byte IV + ciphertext contiguous (16-aligned), 2 KB after the S-box
blob 1 0x5a '{"c2":"203.0.113.40:9001","beacon":"aes-ctr-raw","sleep":45,"flag":"flag{r4w_k3y_1v_ctr}"}' > $T/p3
K3=$(rnd 31 32 | xxd -p | tr -d '\n'); IV3=$(rnd 32 16 | xxd -p | tr -d '\n')
{ rnd 33 4096; printf "$SBOX" | xxd -r -p; rnd 34 2016; printf "$K3$IV3" | xxd -r -p;
  openssl enc -aes-256-ctr -K $K3 -iv $IV3 -in $T/p3; rnd 35 900; } > blk_aes_ctr_raw.bin
# 4: AES-128-CBC, key = md5("hctf-orchid"), random IV prepended to the ciphertext
blob 3 0x13 '{"c2":"orchid.example.org:8080","beacon":"aes-cbc-ivpre","sleep":10,"flag":"flag{1v_pr3p3nd3d_md5}"}' > $T/p4
K4=$(printf 'hctf-orchid' | openssl dgst -md5 -r | cut -c1-32); IV4=$(rnd 41 16 | xxd -p | tr -d '\n')
{ rnd 42 2500; printf "$SBOX" | xxd -r -p; rnd 43 200; printf '\0hctf-orchid\0'; rnd 44 333; printf "$IV4" | xxd -r -p;
  openssl enc -aes-128-cbc -K $K4 -iv $IV4 -in $T/p4; rnd 45 500; } > blk_aes_cbc_ivpre_md5.bin
# 5: ChaCha20 (python cryptography; RFC 7539 counter 0 + 12-char nonce string), 32-char key string; sigma in code
blob 1 0x77 '{"c2":"192.0.2.150:4433","beacon":"chacha-kite","sleep":75,"flag":"flag{ch4ch4_s1gm4_f0und}"}' > $T/p5
{ rnd 51 3500; printf 'expand 32-byte k'; rnd 52 800; printf '\0K1te-ChaCha-Key-0123456789abcdef\0nonce-ABC123\0'; rnd 53 1200;
  $PY -c 'import sys;from cryptography.hazmat.primitives.ciphers import Cipher,algorithms;sys.stdout.buffer.write(Cipher(algorithms.ChaCha20(b"K1te-ChaCha-Key-0123456789abcdef",b"\0\0\0\0nonce-ABC123"),mode=None).encryptor().update(open(sys.argv[1],"rb").read()))' $T/p5;
  rnd 54 600; } > blk_chacha20_strkey.bin
# 6: XTEA-CBC (32 cycles, big-endian words, pure Perl), key = 16-char string, 8-byte IV right after it, then ciphertext
blob 2 0x29 '{"c2":"198.18.0.9:53","beacon":"xtea-cbc","sleep":5,"flag":"flag{xt34_d3lt4_9e3779b9}"}' > $T/p6
{ rnd 61 2000; printf '\271\171\067\236'; rnd 62 700; printf '\0XteaKey_16bytes!\0'; perl blk_xtea.pl enc 'XteaKey_16bytes!' a1b2c3d4e5f60718 < $T/p6; rnd 63 400; } > blk_xtea_cbc_strkey.bin
# decoy: S-box + strings; one AES-CBC blob under a key that is NOT stored, one under a stored key with a broken crc
$PY -c 'import sys;b=bytearray(open(sys.argv[1],"rb").read());b[8]^=1;open(sys.argv[2],"wb").write(b)' $T/p1 $T/p7
{ rnd 71 2000; printf "$SBOX" | xxd -r -p; rnd 72 300; printf '\0NotTheKey_123456\0InitVector123456\0'; rnd 73 200;
  openssl enc -aes-128-cbc -K $(hexs 'MissingKey_99999') -iv $(hexs 'InitVector123456') -in $T/p1; rnd 74 300;
  printf '\0Sup3rS3cr3tK3y!!\0InitVector123456\0'; rnd 75 100;
  openssl enc -aes-128-cbc -K $(hexs 'Sup3rS3cr3tK3y!!') -iv $(hexs 'InitVector123456') -in $T/p7; rnd 76 300; } > blk_decoy.bin
