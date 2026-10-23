#!/bin/sh
# envkey_oracle.sh <file> <kdf: sha256|crc32le> <literal> <whole|body>: key from `openssl dgst -sha256` (or python
# binascii.crc32), locate the stored blob (HCFG ^ key, or a plain 'HCFG' header for body mode) with a byte find,
# decrypt, check the header crc32 + JSON (python stdlib) and print {"offset", "config"}; exit 1 when nothing verifies.
set -e
f=$1; kdf=$2; lit=$3; mode=$4
case $kdf in
  sha256) k=$(printf '%s' "$lit" | openssl dgst -sha256 -r | cut -c1-64) ;;
  crc32le) k=$(python3 -c 'import binascii,sys;print(binascii.crc32(sys.argv[1].encode()).to_bytes(4,"little").hex())' "$lit") ;;
esac
python3 -c 'import sys,zlib,json,struct
d=open(sys.argv[1],"rb").read();k=bytes.fromhex(sys.argv[2]);whole=sys.argv[3]=="whole"
x=lambda b,o=0:bytes(c^k[(i+o)%len(k)] for i,c in enumerate(b))
pat=x(b"HCFG") if whole else b"HCFG";t=d.find(pat)
while t>=0:
    b=x(d[t:t+12]) if whole else d[t:t+12];v,y,n,c=struct.unpack_from("<BBHI",b,4)
    body=x(d[t:t+12+n])[12:] if whole else x(d[t+12:t+12+n]);p=bytes(q^y for q in body)
    if zlib.crc32(p)==c:
        print(json.dumps({"offset":t,"config":json.loads(p)}));sys.exit(0)
    t=d.find(pat,t+1)
sys.exit(1)' "$f" "$k" "$mode"
