#!/bin/bash
# JNI narrowing-gate bypass fixtures (target jni-gate-bypass-input, row 65): nativeUnlock(a, b) xors its output with a
# key derived from the passing input, so only the SMALLEST passing input yields the token. ENC is built with perl
# (token[i] ^ key ^ i); libraries with gcc / aarch64-linux-gnu-gcc -O2; APKs with `zip`.
# Oracle: native_src/gate_harness2.c dlopen()s the real .so (x86_64 natively, arm64 under qemu-aarch64) and calls
# the export over the boundary inputs; the smallest non-"denied" one is the bypass (see gate_oracle.sh).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"the gate narrows what crosses the boundary"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
encx() { perl -e 'my $i = 0; print join ",", map { sprintf "0x%02x", ord($_) ^ hex($ARGV[1]) ^ $i++ } split //, $ARGV[0]' "$1" "$2"; }
T=$(mktemp -d)
# 1. x86_64, s16 narrowing: a > 0x7fff && (int16_t)a < 0 -> smallest pass 0x8000; key = a >> 8 = 0x80
gcc -shared -fPIC -O2 -DENC="$(encx 'ANS-3f9a07c2d4e8b615' 80)" -DGATE='a > 0x7fff && (int16_t)a < 0' -DKEY='a >> 8' \
  -o "$T/libgate.so" "$SRC/gate_bypass.c"
mkapk jnigate_s16_x86_64 x86_64 "$T/libgate.so"
# 2. arm64, u8 narrowing on a + u16 on b: (uint8_t)a == 0 && a > 0 && (uint16_t)b == 0xffff -> (0x100, 0xffff);
#    key = (a >> 8) ^ b = 0xfe
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DENC="$(encx 'ANS-a51c6e0f92d7b384' fe)" \
  -DGATE='(uint8_t)a == 0 && a > 0 && (uint16_t)b == 0xffff' -DKEY='(a >> 8) ^ b' -o "$T/libgate.so" "$SRC/gate_bypass.c"
mkapk jnigate_u8pair_arm64 arm64-v8a "$T/libgate.so"
# 3. DECOY: as 1 but a near-miss token (15 hex + 'Q')
gcc -shared -fPIC -O2 -DENC="$(encx 'ANS-3f9a07c2d4e8b61Q' 80)" -DGATE='a > 0x7fff && (int16_t)a < 0' -DKEY='a >> 8' \
  -o "$T/libgate.so" "$SRC/gate_bypass.c"
mkapk jnigate_decoy_s16_nearmiss x86_64 "$T/libgate.so"
rm -rf "$T"
