#!/usr/bin/env bash
# autoit-ripper: extract the AutoIt script (AU3!EA06 / EA05) from compiled AutoIt executables (venv).
source "$(dirname "$0")/_lib.sh"
"$ROOT/tools/uv/uv" pip install -q --python .venv/bin/python autoit-ripper 2>/dev/null || uv pip install -q --python .venv/bin/python autoit-ripper
link "$ROOT/.venv/bin/autoit-ripper" autoit-ripper
