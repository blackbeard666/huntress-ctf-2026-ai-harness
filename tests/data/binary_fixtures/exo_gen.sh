#!/bin/bash
# usage: exo_gen.sh out.bin mode json [badcrc]
# blob: printf header + crc32 from the gzip trailer; stream: node zlib.zstdCompressSync (libzstd) / python-lz4 frame writer
# + coreutils base64 / xxd -p (never lib.binary)
set -e
H=/home/testpwn/huntress-2026
P="$3"
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
[ -n "$4" ] && CRC=deadbeef
T=$(mktemp)
{ printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))";
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$T"
[ "$5" = magic ] && printf 'HCFX' | dd of="$T" conv=notrunc 2>/dev/null
ZS() { "$H/tools/node/bin/node" -e 'process.stdout.write(require("zlib").zstdCompressSync(require("fs").readFileSync(0)))' < "$T"; }
L4() { "$H/.venv/bin/python" -I -c 'import sys,lz4.frame;sys.stdout.buffer.write(lz4.frame.compress(sys.stdin.buffer.read()))' < "$T"; }
case "$2" in
  raw-zstd) S() { ZS; } ;;
  b64-zstd) S() { ZS | base64 -w0; } ;;
  hex-zstd) S() { ZS | xxd -p -c0; } ;;
  raw-lz4)  S() { L4; } ;;
  b64-lz4)  S() { L4 | base64 -w0; } ;;
  hex-lz4)  S() { L4 | xxd -p -c0; } ;;
esac
{ head -c 4096 /dev/urandom | tr -d 'HCFGKBk\050\004' | head -c 3000; printf 'GetConfig\0\0\0'; S; printf '\0';
  head -c 900 /dev/zero; } > "$1"
rm -f "$T"
