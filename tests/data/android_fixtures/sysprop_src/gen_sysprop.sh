#!/bin/bash
# Native system-property / popen / mounts probe fixtures (target native-system-property-and-mounts-stubs):
# sysprop_probe.c built with gcc / aarch64-linux-gnu-gcc -O2 -shared; ENC = token ^ ((KEY * (i + 1) + 0x29) & 0xff),
# KEY = the clean fold computed below in python3 from the C source's constants; APKs with `zip`.
# Oracle: sysprop_harness.c dlopen()s the real .so (x86_64 natively, arm64 under qemu-aarch64) and prints what
# reaches NewStringUTF.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); OUT=${1:-$HERE/..}
KEY=$(python3 -c 'k=0x37; k+=0x11; k^=0x05; k+=0x09; k^=0x22; k+=0x03; k^=0x18; k+=0x2b; k^=0x14; k+=0x07; k^=0x21; k+=0x02; k^=0x30; print(hex(k & 0xff))')
enc() { python3 -c 'import sys; t=sys.argv[1].encode(); k=int(sys.argv[2],0); print("{" + ",".join(str(c ^ ((k*(i+1)+0x29) & 0xff)) for i, c in enumerate(t)) + "}")' "$1" "$2"; }
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"the guard only answers a stock, locked phone"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
T=$(mktemp -d)
gcc -shared -fPIC -O2 -DENC="$(enc ANS-3b9d05e7c1a2f864 "$KEY")" -o "$T/libguard.so" "$HERE/sysprop_probe.c" -ldl
mkapk sysprop_mounts_x86_64 x86_64 "$T/libguard.so"
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DENC="$(enc ANS-a61f2c8e04d97b35 "$KEY")" -o "$T/libguard.so" "$HERE/sysprop_probe.c" -ldl
mkapk sysprop_mounts_arm64 arm64-v8a "$T/libguard.so"
# DECOY: same probes, the clean fold decodes a near-miss (15 hex + 'Q'); no ANS literal anywhere in the .so
gcc -shared -fPIC -O2 -DENC="$(enc ANS-3b9d05e7c1a2f86Q "$KEY")" -o "$T/libguard.so" "$HERE/sysprop_probe.c" -ldl
mkapk sysprop_decoy_nearmiss x86_64 "$T/libguard.so"
rm -rf "$T"
