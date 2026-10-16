#!/bin/bash
# Native .so fixtures (coverage atlas rows 37/39/40): an ANS token computed inside a .so export, never a literal.
# Blobs are encoded with perl; the libraries built with gcc / aarch64-linux-gnu-gcc; each APK zipped with `zip`.
# Oracle: native_src/harness.c dlopen()s the real .so (x86_64 natively, arm64 under qemu-aarch64) with a fake JNIEnv.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
blob() {  # perl-expr-of-($c,$i) plaintext -> C byte list
  perl -e '$i=0; print join ",", map { $c=ord($_); sprintf "0x%02x", ('"$1"') & 255; } split //, $ARGV[0]' "$2"
}
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"the vault is native"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
T=$(mktemp -d)
# 1. Java_* export, xor 0x5a, -O0 x86_64
gcc -shared -fPIC -O0 -DBLOB="$(blob '$c ^ 0x5a' 'ANS-6c1f0e9b2d47a835')" -o "$T/libvault.so" "$SRC/jni_xor.c"
mkapk native_jni_xor_x86_64 x86_64 "$T/libvault.so"
# 2. no-arg char* export, add-by-index (computed, no xor imm), -O2 arm64
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DBLOB="$(perl -e '$i=0; print join ",", map { sprintf "0x%02x", (ord($_) + 13*$i++ + 7) & 255 } split //, $ARGV[0]' 'ANS-e40b7c91d3a2f586')" -o "$T/libcore.so" "$SRC/noarg_add.c"
mkapk native_noarg_add_arm64 arm64-v8a "$T/libcore.so"
# 3. JNI_OnLoad + RegisterNatives, rolling xor key 0x21+3i, -O2 x86_64, stripped
gcc -shared -fPIC -O2 -s -DBLOB="$(perl -e '$i=0; print join ",", map { sprintf "0x%02x", ord($_) ^ ((0x21 + 3*$i++) & 255) } split //, $ARGV[0]' 'ANS-93ad5e0f71c8b264')" -o "$T/libreg.so" "$SRC/onload_reg.c"
mkapk native_onload_register_x86_64 x86_64 "$T/libreg.so"
# 4. DECOY: same as 1 but a near-miss token (15 hex + 'Z')
gcc -shared -fPIC -O0 -DBLOB="$(blob '$c ^ 0x5a' 'ANS-6c1f0e9b2d47a83Z')" -o "$T/libvault.so" "$SRC/jni_xor.c"
mkapk native_decoy_jni_xor_nearmiss x86_64 "$T/libvault.so"
rm -rf "$T"
