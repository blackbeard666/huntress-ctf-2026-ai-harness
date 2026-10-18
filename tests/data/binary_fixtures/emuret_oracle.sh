#!/bin/bash
# Independent oracle: RUN the fixture (it prints recover_code()) natively or under qemu-aarch64, and show whether
# readelf lists a recover_code FUNC symbol. usage: bash emuret_oracle.sh emuret_<name>.bin
f=$1
readelf -sW "$f" | grep -w 'FUNC.*recover_code' || echo "no recover_code FUNC symbol"
if readelf -h "$f" | grep -q AArch64; then qemu-aarch64 -L /usr/aarch64-linux-gnu "./$f"; else "./$f"; fi
objdump -d --no-show-raw-insn "$f" | awk '/<recover_code>:/,/^$/' | grep -o 'call.*' || true
