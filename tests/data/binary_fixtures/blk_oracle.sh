#!/bin/sh
# blk_oracle.sh <file> <offset> <cipher> <key-hex> <iv-hex>: decrypt 256 bytes at <offset> with `openssl enc -d`
# (aes-*-ecb/cbc/ctr, chacha20) or blk_xtea.pl (cipher xtea-cbc, key = the 16-char string), then check the HCFG
# header crc32 + JSON with python stdlib and print {"offset", "config"}.
set -e
f=$1; off=$2; c=$3; k=$4; iv=$5
ct() { dd if="$f" bs=1 skip="$off" count=256 status=none; }
case $c in
  xtea-cbc) ct | perl "$(dirname "$0")/blk_xtea.pl" dec "$k" "$iv" ;;
  *-ecb)    ct | openssl enc -d -"$c" -K "$k" -nopad ;;
  *)        ct | openssl enc -d -"$c" -K "$k" -iv "$iv" -nopad ;;
esac | python3 -c 'import sys,zlib,json,struct
b=sys.stdin.buffer.read();assert b[:4]==b"HCFG",b[:4];v,x,n,c=struct.unpack_from("<BBHI",b,4);p=bytes(y^x for y in b[12:12+n])
assert zlib.crc32(p)==c,"crc";print(json.dumps({"offset":int(sys.argv[1]),"config":json.loads(p)}))' "$off"
