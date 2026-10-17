#!/bin/bash
# Oracle for gen_gate_bypass.sh: unzip the .so, run the real export over the boundary inputs (and pairs), print the
# first (smallest) non-denied call. Usage: gate_oracle.sh <apk> [qemu]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); unzip -q -d "$T" "$1" 'lib/*'; SO=$(ls "$T"/lib/*/*.so)
IN="0 1 0x7f 0x80 0xff 0x100 0x7fff 0x8000 0xffff 0x10000 0x10001 0x7fffffff -1 -0x8000 -0x10000"
if [ "${2:-}" = qemu ]; then
  aarch64-linux-gnu-gcc -o "$T/h" "$HERE/native_src/gate_harness2.c" -ldl; RUN="qemu-aarch64 -L /usr/aarch64-linux-gnu $T/h"
else gcc -o "$T/h" "$HERE/native_src/gate_harness2.c" -ldl; RUN="$T/h"; fi
for b in 0 $IN; do for a in $IN; do
  r=$($RUN "$SO" Java_com_huntress_arena_Gate_nativeUnlock "$a" "$b")
  [ "$r" != "NewStringUTF denied" ] && { echo "a=$a b=$b $r"; rm -rf "$T"; exit 0; }
done; done; rm -rf "$T"; echo none
