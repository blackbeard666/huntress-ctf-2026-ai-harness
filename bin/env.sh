# source bin/env.sh -> puts the project toolbox on PATH. Nothing is installed outside the project.
HCTF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export HCTF_ROOT
export PATH="$HCTF_ROOT/bin:$HCTF_ROOT/tools/node/bin:$HCTF_ROOT/tools/uv:$HCTF_ROOT/.venv/bin:$PATH"
export TMPDIR="$HCTF_ROOT/.run/tmp" UV_CACHE_DIR="$HCTF_ROOT/.run/cache/uv" \
       UV_PYTHON_INSTALL_DIR="$HCTF_ROOT/tools/python" npm_config_cache="$HCTF_ROOT/.run/cache/npm"
mkdir -p "$TMPDIR"
