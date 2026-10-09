#!/usr/bin/env bash
# Nim symbol demangler: ESET's nimfilt (PyPI `nimfilt`, github.com/eset/nimfilt) -> bin/nim-demangle.
# `nim-demangle '<sym>'` / `nm X | nim-demangle`: `name__<module>_u<n>` -> module + name (Nim's C codegen mangling).
source "$(dirname "$0")/_lib.sh"
[ -x .venv/bin/nimfilt ] || "$ROOT/tools/uv/uv" pip install -q --python .venv/bin/python nimfilt 2>/dev/null \
  || uv pip install -q --python .venv/bin/python nimfilt
link "$ROOT/.venv/bin/nimfilt" nim-demangle
