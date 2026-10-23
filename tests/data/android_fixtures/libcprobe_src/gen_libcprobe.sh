#!/bin/bash
# Native libc anti-debug probe fixtures (target native-libc-probe-stubs-emulate): libc_probe.c built with gcc /
# aarch64-linux-gnu-gcc -O2 -shared; ENC = token ^ ((KEY * (i + 1) + 0x3d) & 0xff), KEY = 0x0c (the clean fold:
# ((((((0x5a + 0x13) ^ 0x0c) + 7) ^ 0x21) + 3) ^ 0x40) & 0xff); APKs with `zip`.
# Oracle: ../native_src/antigate_harness.c dlopen()s the real .so (x86_64 natively, arm64 under qemu-aarch64) on a
# clean host and prints what reaches NewStringUTF.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); OUT=${1:-$HERE/..}
enc() { python3 -c 'import sys; t=sys.argv[1].encode(); k=int(sys.argv[2],0); print("{" + ",".join(str(c ^ ((k*(i+1)+0x3d) & 0xff)) for i, c in enumerate(t)) + "}")' "$1" "$2"; }
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"the guard only answers a clean device"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
T=$(mktemp -d)
gcc -shared -fPIC -O2 -DENC="$(enc ANS-7c3e91d04ab2f658 0x0c)" -o "$T/libguard.so" "$HERE/libc_probe.c" -lpthread
mkapk libcprobe_x86_64 x86_64 "$T/libguard.so"
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DENC="$(enc ANS-e04f2a9b6d18c375 0x0c)" -o "$T/libguard.so" "$HERE/libc_probe.c" -lpthread
mkapk libcprobe_arm64 arm64-v8a "$T/libguard.so"
# DECOY: same probes, the clean fold decodes a near-miss (15 hex + 'Z'); no ANS literal anywhere in the .so
gcc -shared -fPIC -O2 -DENC="$(enc ANS-7c3e91d04ab2f65Z 0x0c)" -o "$T/libguard.so" "$HERE/libc_probe.c" -lpthread
mkapk libcprobe_decoy_nearmiss x86_64 "$T/libguard.so"
rm -rf "$T"
