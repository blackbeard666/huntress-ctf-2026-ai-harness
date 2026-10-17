#!/bin/bash
# RegisterNatives-table fixtures (target registernatives-table, row 39): stripped .so, only JNI_OnLoad exported; the
# registered native vaultValue(int) decodes its xor blob only for n == 0x10000 (so emulating it with n = 0 misses).
# Blobs encoded with perl; libraries built with gcc / aarch64-linux-gnu-gcc -O2 -s; APKs zipped with `zip`.
# Oracle: native_src/regnat_harness.c dlopen()s the real .so (arm64 under qemu-aarch64), runs JNI_OnLoad with a fake
# JavaVM and calls the registered (I) native with 0x10000; `readelf -r` shows the table's R_*_RELATIVE relocations.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
enc() { perl -e 'print join ",", map { sprintf "0x%02x", ord($_) ^ hex($ARGV[1]) } split //, $ARGV[0]' "$1" "$2"; }
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"registered at load time"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
T=$(mktemp -d)
F="-shared -fPIC -O2 -s -fno-tree-vectorize"
# 1. x86_64, xor 0x5c
gcc $F -DBLOB="$(enc 'ANS-7e21c9a05fd3b648' 5c)" -DKEY=0x5c -DCLS='"com/huntress/arena/Vault"' \
  -o "$T/libregnat.so" "$SRC/regnat_gated.c"
mkapk regnat_gated_x86_64 x86_64 "$T/libregnat.so"
# 2. arm64, xor 0x37 (not an arm64 bitmask immediate: mov + eor)
aarch64-linux-gnu-gcc $F -DBLOB="$(enc 'ANS-c4085be1f9a2d736' 37)" -DKEY=0x37 -DCLS='"com/huntress/arena/Locker"' \
  -o "$T/libregnat.so" "$SRC/regnat_gated.c"
mkapk regnat_gated_arm64 arm64-v8a "$T/libregnat.so"
# 3. DECOY: as 1 but a near-miss token (15 hex + 'X')
gcc $F -DBLOB="$(enc 'ANS-7e21c9a05fd3b64X' 5c)" -DKEY=0x5c -DCLS='"com/huntress/arena/Vault"' \
  -o "$T/libregnat.so" "$SRC/regnat_gated.c"
mkapk regnat_decoy_gated_nearmiss x86_64 "$T/libregnat.so"
rm -rf "$T"
