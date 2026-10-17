#!/bin/bash
# Anti-debug / root gate fixtures (target native-gated-branch-read): nativeCheck() returns a plaintext TRAP token on
# the debugged / rooted side of each ptrace / access / fopen / strstr branch, the real value only on the clean path.
# Tokens encoded with coreutils base64 / perl; libraries with gcc / aarch64-linux-gnu-gcc -O2; APKs with `zip`.
# Oracle: native_src/gated_harness.c dlopen()s the real .so (x86_64 natively, arm64 under qemu-aarch64) on a clean
# host (no tracer, no su, no LD_PRELOAD) and prints what reaches NewStringUTF.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"a clean device sees the real value"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
hexx() { perl -e 'print join "", map { sprintf "%02x", ord($_) ^ hex($ARGV[1]) } split //, $ARGV[0]' "$1" "$2"; }
T=$(mktemp -d)
# 1. x86_64: clean value base64, traps plaintext tokens
gcc -shared -fPIC -O2 -DARENA="\"$(printf %s 'ANS-5e81c0d93a7f2b64' | base64 -w0)\"" -DTRAP='"ANS-dead0000beef1111"' \
  -DTRAP2='"ANS-0badc0de00000001"' -o "$T/libguard.so" "$SRC/antidebug_gate.c"
mkapk antigate_ptrace_b64_x86_64 x86_64 "$T/libguard.so"
# 2. arm64: clean value hex(token ^ 0x5c), decoded in the export
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DXKEY=0x5c -DARENA="\"$(hexx 'ANS-29b4f7a10c8e6d35' 5c)\"" \
  -DTRAP='"ANS-feedface12345678"' -DTRAP2='"ANS-1337133713371337"' -o "$T/libguard.so" "$SRC/antidebug_gate.c"
mkapk antigate_root_hexxor_arm64 arm64-v8a "$T/libguard.so"
# 3. DECOY: valid tokens only on the debugged / rooted side; the clean path decodes a near-miss (15 hex + 'Q')
gcc -shared -fPIC -O2 -DARENA="\"$(printf %s 'ANS-5e81c0d93a7f2b6Q' | base64 -w0)\"" -DTRAP='"ANS-dead0000beef1111"' \
  -DTRAP2='"ANS-0badc0de00000001"' -o "$T/libguard.so" "$SRC/antidebug_gate.c"
mkapk antigate_decoy_trap_only x86_64 "$T/libguard.so"
rm -rf "$T"
