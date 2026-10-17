#!/bin/bash
# Oracle for gen_regnat.sh: run the real .so's JNI_OnLoad + registered natives (n = 0x10000). Usage: regnat_oracle.sh <apk> [qemu]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); unzip -q -d "$T" "$1" 'lib/*'; SO=$(ls "$T"/lib/*/*.so)
if [ "${2:-}" = qemu ]; then
  aarch64-linux-gnu-gcc -o "$T/h" "$HERE/native_src/regnat_harness.c" -ldl; qemu-aarch64 -L /usr/aarch64-linux-gnu "$T/h" "$SO" 0x10000
else gcc -o "$T/h" "$HERE/native_src/regnat_harness.c" -ldl; "$T/h" "$SO" 0x10000; fi
readelf -rW "$SO" | grep -c RELATIVE | sed 's/^/RELATIVE relocs: /'; rm -rf "$T"
