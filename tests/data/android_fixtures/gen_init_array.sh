#!/bin/bash
# .init_array string-decrypt fixtures (coverage atlas rows 46/66): an OLLVM-style constructor decrypts a .data global
# at load time; the Java_* export returns that global. Blobs are encoded with perl; libraries built with gcc /
# aarch64-linux-gnu-gcc; each APK zipped with `zip`. Oracle: native_src/harness.c dlopen()s the real .so (the dynamic
# loader runs .init_array itself; x86_64 natively, arm64 under qemu-aarch64) and calls the export with a fake JNIEnv.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
enc() {  # perl-expr-of-($c,$i) plaintext -> C byte list
  perl -e '$i=0; print join ",", map { $c=ord($_); $r=sprintf "0x%02x", ('"$1"') & 255; $i++; $r } split //, $ARGV[0]' "$2"
}
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"decrypted when the library loads"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
T=$(mktemp -d)
# 1. x86_64 -O2 stripped: anonymous static constructor, rolling xor 0x37+5i
gcc -shared -fPIC -O2 -s -DBLOB="$(enc '$c ^ (0x37 + 5*$i)' 'ANS-4b9e07d2c61fa358')" -D'DECODE=secret[i] ^ (0x37 + 5 * i)' \
  -o "$T/libvault.so" "$SRC/init_array_decrypt.c"
mkapk initarr_xor_x86_64_stripped x86_64 "$T/libvault.so"
# 2. arm64 -O2: constructor named .datadiv_decode<N> (OLLVM), rolling add 0x2b+3i
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DBLOB="$(enc '$c + 0x2b + 3*$i' 'ANS-d073a5e19c4b862f')" \
  -D'DECODE=secret[i] - 0x2b - 3 * i' -D'DATADIV_NAME=".datadiv_decode9817364520193847561"' \
  -o "$T/libvault.so" "$SRC/init_array_decrypt.c"
mkapk initarr_datadiv_arm64 arm64-v8a "$T/libvault.so"
# 3. arm64 -O2 stripped: no symbol names left, the constructor is reached through .init_array (R_AARCH64_RELATIVE) only
aarch64-linux-gnu-gcc -shared -fPIC -O2 -s -DBLOB="$(enc '$c ^ (0xa1 - 7*$i)' 'ANS-71f2c8e04d9b3a56')" \
  -D'DECODE=secret[i] ^ (0xa1 - 7 * i)' -o "$T/libvault.so" "$SRC/init_array_decrypt.c"
mkapk initarr_xor_arm64_stripped arm64-v8a "$T/libvault.so"
# 4. DECOY: as 1 but a near-miss token (15 hex + 'Q')
gcc -shared -fPIC -O2 -s -DBLOB="$(enc '$c ^ (0x37 + 5*$i)' 'ANS-4b9e07d2c61fa35Q')" -D'DECODE=secret[i] ^ (0x37 + 5 * i)' \
  -o "$T/libvault.so" "$SRC/init_array_decrypt.c"
mkapk initarr_decoy_nearmiss x86_64 "$T/libvault.so"
rm -rf "$T"
