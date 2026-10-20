#!/bin/bash
# Asset-ELF fixtures (coverage atlas: native-payload-system-load): the .so is NOT under lib/<abi>/ but shipped in
# assets/ (plain, zlib-wrapped, xor'd, or inside a nested payload jar's res/raw) for System.load after extraction.
# Libraries built with gcc / aarch64-linux-gnu-gcc from native_src/, wrappers by perl / python3 zlib, APKs by `zip`.
# Oracle: native_src/harness.c dlopen()s the unwrapped .so (x86_64 natively, arm64 under qemu-aarch64).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
T=$(mktemp -d); cd "$T"
xblob() { perl -e 'print join ",", map { sprintf "0x%02x", ord($_) ^ 0x5a } split //, $ARGV[0]' "$1"; }
xorf() { perl -e 'local $/; $d=<STDIN>; @k=map hex, split /,/, $ARGV[0]; $i=0; print join "", map { chr(ord($_) ^ $k[$i++ % @k]) } split //, $d' "$1"; }
mk() { rm -f "$OUT/$1.apk"; printf '{"hint":"System.load(filesDir + \\"/libguard.so\\")"}' > assets/config.json; zip -qX -r "$OUT/$1.apk" assets; rm -rf assets; }
gcc -shared -fPIC -O0 -DBLOB="$(xblob 'ANS-2b8e41d07c9fa6e3')" -o libguard.so "$SRC/jni_xor.c"
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DBLOB="$(perl -e '$i=0; print join ",", map { sprintf "0x%02x", (ord($_) + 13*$i++ + 7) & 255 } split //, $ARGV[0]' 'ANS-71d4c0a9e8b3f25c')" -o libcore.so "$SRC/noarg_add.c"
gcc -shared -fPIC -O0 -DBLOB="$(xblob 'ANS-2b8e41d07c9fa6eZ')" -o libdecoy.so "$SRC/jni_xor.c"
# 1. plain ELF renamed assets/guard.bin, no lib/ dir
mkdir assets; cp libguard.so assets/guard.bin; mk anl_plain_asset_x86_64
# 2. arm64 ELF zlib-deflated at assets/core.dat
mkdir assets; python3 -c 'import sys, zlib; sys.stdout.buffer.write(zlib.compress(open(sys.argv[1], "rb").read(), 9))' libcore.so > assets/core.dat; mk anl_zlib_asset_arm64
# 3. x86_64 ELF xor'd with key 13,37,c0,de at res/raw/guard.enc inside assets/payload.jar
mkdir -p assets j/res/raw; xorf 13,37,c0,de < libguard.so > j/res/raw/guard.enc; (cd j && zip -qX -r ../assets/payload.jar res); rm -rf j; mk anl_jar_xor_asset_x86_64
# 4. DECOY: as 1 but xor 0x41-wrapped and a near-miss token (15 hex + 'Z')
mkdir assets; xorf 41 < libdecoy.so > assets/guard.bin; mk anl_decoy_xor_nearmiss
cd /; rm -rf "$T"
