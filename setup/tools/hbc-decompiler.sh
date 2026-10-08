#!/usr/bin/env bash
# hermes-dec: React Native Hermes bytecode (index.android.bundle, magic c6 1f bc 03) disassembler/decompiler (venv).
source "$(dirname "$0")/_lib.sh"
"$ROOT/tools/uv/uv" pip install -q --python .venv/bin/python hermes-dec 2>/dev/null || uv pip install -q --python .venv/bin/python hermes-dec
for b in hbc-decompiler hbc-disassembler hbc-file-parser; do [ -x .venv/bin/$b ] && link "$ROOT/.venv/bin/$b" $b; done
