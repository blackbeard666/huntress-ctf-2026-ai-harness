#!/bin/bash
# Raw-syscall anti-hook probe fixtures (target native-inline-syscall-stubs): raw_syscall_probe.c built with gcc /
# aarch64-linux-gnu-gcc -O2 -shared -nostdlib (no libc imports: every probe is an inline syscall / svc #0);
# ENC = token ^ ((KEY * (i + 1) + 0x3d) & 0xff), KEY = 0x0c (the clean fold); APKs with `zip`.
# Oracle: ../native_src/harness.c-style dlopen of the real .so (x86_64 natively, arm64 under qemu-aarch64) on a clean
# host, printing what reaches NewStringUTF (rawsys_harness.c).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); OUT=$(cd "${1:-$HERE/..}" && pwd)
enc() { python3 -c 'import sys; t=sys.argv[1].encode(); k=int(sys.argv[2],0); print("{" + ",".join(str(c ^ ((k*(i+1)+0x3d) & 0xff)) for i, c in enumerate(t)) + "}")' "$1" "$2"; }
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"the guard talks to the kernel directly"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
T=$(mktemp -d)
F="-shared -fPIC -O2 -nostdlib -ffreestanding -fno-builtin -fno-stack-protector"
gcc $F -DENC="$(enc ANS-3b9e07c15da28f46 0x0c)" -o "$T/libguard.so" "$HERE/raw_syscall_probe.c"
mkapk rawsys_x86_64 x86_64 "$T/libguard.so"
aarch64-linux-gnu-gcc $F -DENC="$(enc ANS-d61a4f8e2c07b953 0x0c)" -o "$T/libguard.so" "$HERE/raw_syscall_probe.c"
mkapk rawsys_arm64 arm64-v8a "$T/libguard.so"
# DECOY: same raw-syscall probes, the clean fold decodes a near-miss (15 hex + 'Z'); no ANS literal in the .so
gcc $F -DENC="$(enc ANS-3b9e07c15da28f4Z 0x0c)" -o "$T/libguard.so" "$HERE/raw_syscall_probe.c"
mkapk rawsys_decoy_nearmiss x86_64 "$T/libguard.so"
rm -rf "$T"
