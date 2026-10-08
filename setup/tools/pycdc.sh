#!/usr/bin/env bash
# Decompyle++ (zrax/pycdc): Python bytecode decompiler/disassembler for modern Python versions (uncompyle6 stops at 3.8).
source "$(dirname "$0")/_lib.sh"
if [ ! -x tools/pycdc/build/pycdc ]; then
  rm -rf tools/pycdc && git clone -q --depth 1 https://github.com/zrax/pycdc tools/pycdc
  cmake -S tools/pycdc -B tools/pycdc/build -DCMAKE_BUILD_TYPE=Release >/dev/null
  cmake --build tools/pycdc/build -j"$(nproc)" >/dev/null
fi
link "$ROOT/tools/pycdc/build/pycdc" pycdc; link "$ROOT/tools/pycdc/build/pycdas" pycdas
