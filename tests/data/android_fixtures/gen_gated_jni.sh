#!/bin/bash
# Gated JNI export fixtures (coverage atlas rows 37/65, target jni-export-return-trace): Java_*_nativeEvidence(len)
# returns the (encoded) arena_value only for len 65536; .rodata padded with 40 filler strings. Encodings: coreutils
# base64 / perl hex+xor; libraries built with gcc / aarch64-linux-gnu-gcc (-O2); each APK zipped with `zip`.
# Oracle: native_src/gated_harness.c dlopen()s the real .so (x86_64 natively, arm64 under qemu-aarch64) and calls the
# export with len 0x10000 (and 0 -> "denied").
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"evidence crosses the boundary"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
hexx() { perl -e 'print join "", map { sprintf "%02x", ord($_) ^ hex($ARGV[1]) } split //, $ARGV[0]' "$1" "$2"; }
T=$(mktemp -d)
# 1. x86_64 -O2: arena_value = base64(token), returned as-is behind the gate (Java decodes it)
gcc -shared -fPIC -O2 -DARENA="\"$(printf %s 'ANS-7d20c4e9a1b5f386' | base64 -w0)\"" -o "$T/libboundary.so" "$SRC/gated_evidence.c"
mkapk native_gated_b64_x86_64 x86_64 "$T/libboundary.so"
# 2. arm64 -O2: arena_value = hex(token ^ 0x2a), hex-decoded + xor'd inside the gated export (eor #0x2a)
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DXKEY=0x2a -DARENA="\"$(hexx 'ANS-c81e5f02b7a94d63' 2a)\"" -o "$T/libboundary.so" "$SRC/gated_evidence.c"
mkapk native_gated_hexxor_arm64 arm64-v8a "$T/libboundary.so"
# 3. DECOY: as 1 but a near-miss token (15 hex + 'Q')
gcc -shared -fPIC -O2 -DARENA="\"$(printf %s 'ANS-7d20c4e9a1b5f38Q' | base64 -w0)\"" -o "$T/libboundary.so" "$SRC/gated_evidence.c"
mkapk native_decoy_gated_b64_nearmiss x86_64 "$T/libboundary.so"
rm -rf "$T"
