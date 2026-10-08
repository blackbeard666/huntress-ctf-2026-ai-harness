# Shared by setup/tools/<tool>.sh recipes: ROOT, link(), set -euo pipefail. Each recipe is idempotent, installs under
# the project (tools/ or .venv) and links bin/<tool> (on every worker's PATH and visible inside the worker sandbox).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p tools bin .run
link() { ln -sfn "$1" "bin/$2"; echo "bin/$2 -> $1"; }
export PATH="$ROOT/tools/node/bin:$ROOT/.venv/bin:$HOME/cmake/bin:$PATH"
