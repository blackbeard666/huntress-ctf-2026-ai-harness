#!/bin/bash
# Multi-ABI native fixtures (coverage atlas row 40: armeabi-v7a Thumb, x86, arm64-only, the same lib in several ABIs).
# Each library: native_src/<src>.c compiled ONCE to an object with zig cc (tools/pyziglang) / aarch64-linux-gnu-gcc / gcc,
# the object linked into the .so (zip'd into lib/<abi>/) and, for the oracle, statically into native_src/static_harness.c
# run under qemu-arm / qemu-i386 / qemu-aarch64 (x86_64 natively) -- the token printed by the real machine code.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
Z=${ZIG:-$HERE/../../../tools/pyziglang/ziglang/zig}
add_blob() { perl -e '$i=0; print join ",", map { sprintf "0x%02x", (ord($_) + 13*$i++ + 7) & 255 } split //, $ARGV[0]' "$1"; }
roll_blob() { perl -e '$i=0; print join ",", map { sprintf "0x%02x", ord($_) ^ ((0x21 + 3*$i++) & 255) } split //, $ARGV[0]' "$1"; }
T=$(mktemp -d)
cc_for() {  # abi -> compiler command (object + .so + static exe)
  case $1 in
    armeabi-v7a) echo "$Z cc -target arm-linux-musleabihf -mcpu=cortex_a7 -mthumb";;
    x86) echo "$Z cc -target x86-linux-musl";;
    arm64-v8a) echo "$Z cc -target aarch64-linux-musl";;
    x86_64) echo "$Z cc -target x86_64-linux-musl";;
  esac
}
qemu_for() { case $1 in armeabi-v7a) echo qemu-arm;; x86) echo qemu-i386;; arm64-v8a) echo qemu-aarch64;; *) echo;; esac; }
build() {  # dir abi src blob soname -> $dir/lib/$abi/$soname, oracle output on stdout
  local cc; cc=$(cc_for "$2"); mkdir -p "$1/lib/$2"
  $cc -c -fPIC -O2 -g0 -DBLOB="$4" -o "$T/o.o" "$SRC/$3.c"
  $cc -shared -s -o "$1/lib/$2/$5" "$T/o.o"
  $cc -static -O2 -o "$T/h" "$SRC/static_harness.c" "$T/o.o"
  echo "[$2] $(readelf -h "$1/lib/$2/$5" | grep Machine | tr -s ' ')"; $(qemu_for "$2") "$T/h"
}
mkapk() {  # name dir
  printf '{"hint":"the vault is native"}' > "$2/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$2" && zip -qX -r "$OUT/$1.apk" assets lib)
}
new() { local d; d=$(mktemp -d -p "$T"); mkdir -p "$d/assets"; echo "$d"; }
# 1. armeabi-v7a only, Thumb-2, no-arg export, add-by-index decode (no xor imm: needs ARM emulation)
D=$(new); build "$D" armeabi-v7a noarg_add "$(add_blob ANS-5b9e07c3a1f2d864)" libcore.so; mkapk native_abi_armv7_thumb_add "$D"
# 2. x86 (i386) only, JNI_OnLoad + RegisterNatives (12-byte entries), rolling xor, stripped
D=$(new); build "$D" x86 onload_reg "$(roll_blob ANS-0e7d4c2b9a183f56)" libreg.so; mkapk native_abi_x86_onload_register "$D"
# 3. all four ABIs: the real token in arm64-v8a / armeabi-v7a / x86, a different token in x86_64 (lone ABI disagrees)
D=$(new)
for a in arm64-v8a armeabi-v7a x86; do build "$D" $a onload_reg "$(roll_blob ANS-71c3e9a05d2b48f6)" libreg.so; done
build "$D" x86_64 onload_reg "$(roll_blob ANS-dead0000beef1111)" libreg.so
mkapk native_abi_multi_consensus "$D"
# 4. DECOY: armeabi-v7a Thumb like 1, near-miss token (15 hex + 'Q')
D=$(new); build "$D" armeabi-v7a noarg_add "$(add_blob ANS-5b9e07c3a1f2d86Q)" libcore.so; mkapk native_abi_decoy_armv7_nearmiss "$D"
rm -rf "$T"
