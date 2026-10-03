#!/usr/bin/env bash
# Idempotent, no-sudo toolbox for the harness. Run it on the local WSL box and on Homebase.
# Everything stays inside the project: tools -> <repo>/tools, launchers -> <repo>/bin,
# Python venv -> <repo>/.venv (Python 3.12 via uv), downloads and caches -> <repo>/.run
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$ROOT/tools"; B="$ROOT/bin"; TMPD="$ROOT/.run/tmp"; mkdir -p "$T" "$B" "$TMPD"
export UV_INSTALL_DIR="$T/uv" UV_PYTHON_INSTALL_DIR="$T/python" UV_CACHE_DIR="$ROOT/.run/cache/uv" \
       UV_NO_MODIFY_PATH=1 npm_config_cache="$ROOT/.run/cache/npm" TMPDIR="$TMPD"
export PATH="$B:$T/uv:$PATH"
ok()   { echo "[ok]   $*"; }
fail() { echo "[FAIL] $*"; FAILED+=("$*"); }
FAILED=()
gh_asset() {  # gh_asset owner/repo regex -> download URL of the latest release asset matching regex
  curl -fsSL "https://api.github.com/repos/$1/releases/latest" | python3 -c \
    "import json,re,sys; a=[x['browser_download_url'] for x in json.load(sys.stdin)['assets'] if re.search(sys.argv[1], x['name'])]; print(a[0] if a else '')" "$2"
}

# --- uv + Python venv (3.12: angr/unicorn ship wheels for it; the system Python is 3.14)
[ -x "$T/uv/uv" ] || curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
[ -x "$T/uv/uv" ] && ok uv || fail uv
# Pin a project-local CPython (tools/python) so the venv never depends on interpreters outside the project.
uv python install -q 3.12 >/dev/null 2>&1
PY312=$(ls -d "$T"/python/cpython-3.12*/bin/python3.12 2>/dev/null | head -1)
case "$(readlink -f "$ROOT/.venv/bin/python" 2>/dev/null)" in "$T"/*) ;; *) rm -rf "$ROOT/.venv";; esac
[ -x "$ROOT/.venv/bin/python" ] || uv venv -q --python "$PY312" "$ROOT/.venv"
uv pip install -q --python "$ROOT/.venv/bin/python" \
  requests pefile lief capstone keystone-engine unicorn z3-solver pyelftools \
  androguard oletools python-evtx regipy LnkParse3 binary-refinery pycryptodome \
  yara-python python-magic pyzipper olefile pillow xdis pyinstxtractor-ng dnfile \
  && ok "python libs" || fail "python libs"
uv pip install -q --python "$ROOT/.venv/bin/python" angr && ok angr || fail angr

# --- jadx (APK/DEX decompiler)
if [ ! -x "$T/jadx/bin/jadx" ]; then
  u=$(gh_asset skylot/jadx '^jadx-[0-9.]+\.zip$'); curl -fsSL "$u" -o $TMPD/jadx.zip && rm -rf "$T/jadx" && unzip -q $TMPD/jadx.zip -d "$T/jadx"
fi
ln -sf "$T/jadx/bin/jadx" "$B/jadx"; command -v jadx >/dev/null && ok jadx || fail jadx

# --- exiftool (perl, no install needed)
if [ ! -x "$T/exiftool/exiftool" ]; then
  curl -fsSL https://codeload.github.com/exiftool/exiftool/tar.gz/refs/heads/master -o $TMPD/et.tgz \
    && rm -rf "$T/exiftool" && mkdir -p "$T/exiftool" && tar -xzf $TMPD/et.tgz -C "$T/exiftool" --strip-components=1
fi
ln -sf "$T/exiftool/exiftool" "$B/exiftool"; exiftool -ver >/dev/null 2>&1 && ok exiftool || fail exiftool

# --- PowerShell (script-analysis lane)
if [ ! -x "$T/pwsh/pwsh" ]; then
  u=$(gh_asset PowerShell/PowerShell 'linux-x64\.tar\.gz$'); curl -fsSL "$u" -o $TMPD/pwsh.tgz \
    && rm -rf "$T/pwsh" && mkdir -p "$T/pwsh" && tar -xzf $TMPD/pwsh.tgz -C "$T/pwsh" && chmod +x "$T/pwsh/pwsh"
fi
ln -sf "$T/pwsh/pwsh" "$B/pwsh"; pwsh -v >/dev/null 2>&1 && ok pwsh || fail pwsh

# --- rizin (disassembler/decompiler CLI)
if [ ! -x "$T/rizin/bin/rizin" ]; then
  u=$(gh_asset rizinorg/rizin 'static-x86_64\.tar\.xz$'); curl -fsSL "$u" -o $TMPD/rizin.txz \
    && rm -rf "$T/rizin" && mkdir -p "$T/rizin" && tar -xJf $TMPD/rizin.txz -C "$T/rizin"
fi
for f in "$T"/rizin/bin/*; do ln -sf "$f" "$B/$(basename "$f")"; done
command -v rizin >/dev/null && ok rizin || fail rizin

# --- Linux Node.js + npm (in WSL a bare `npm` can resolve to the Windows npm.exe through interop)
if [ ! -x "$T/node/bin/npm" ]; then
  v=$(curl -fsSL https://nodejs.org/dist/index.json | python3 -c 'import json,sys; print([r for r in json.load(sys.stdin) if r["lts"]][0]["version"])')
  curl -fsSL "https://nodejs.org/dist/$v/node-$v-linux-x64.tar.xz" -o $TMPD/node.txz \
    && rm -rf "$T/node" && mkdir -p "$T/node" && tar -xJf $TMPD/node.txz -C "$T/node" --strip-components=1
fi
export PATH="$T/node/bin:$PATH"
[ -x "$T/node/bin/npm" ] && ok "node $(node --version)" || fail node

# --- JS deobfuscation (script-analysis lane)
for pkg in webcrack js-beautify box-js; do
  [ -e "$T/npm/node_modules/.bin/$pkg" ] || "$T/node/bin/npm" install --prefix "$T/npm" "$pkg" >/dev/null 2>&1 || echo "  npm $pkg failed"
done
for x in webcrack js-beautify box-js; do
  [ -e "$T/npm/node_modules/.bin/$x" ] && printf '#!/bin/sh\nexec "%s" "%s" "$@"\n' "$T/node/bin/node" "$(readlink -f "$T/npm/node_modules/.bin/$x")" > "$B/$x" && chmod +x "$B/$x"
done
command -v js-beautify >/dev/null && ok "js tools: $(ls "$T/npm/node_modules/.bin" | tr '\n' ' ')" || fail "js tools"

# --- Ghidra headless (heavy binary lane) - needs JDK 21+
if [ ! -x "$T/ghidra/support/analyzeHeadless" ]; then
  u=$(gh_asset NationalSecurityAgency/ghidra '_PUBLIC_[0-9]+\.zip$'); curl -fsSL "$u" -o $TMPD/ghidra.zip \
    && rm -rf "$T/ghidra" "$T"/ghidra_* && unzip -q $TMPD/ghidra.zip -d "$T" && mv "$T"/ghidra_*_PUBLIC "$T/ghidra"
fi
ln -sf "$T/ghidra/support/analyzeHeadless" "$B/analyzeHeadless"
[ -x "$T/ghidra/support/analyzeHeadless" ] && ok "ghidra headless" || fail ghidra

echo; [ ${#FAILED[@]} -eq 0 ] && echo "ALL OK" || { echo "FAILED: ${FAILED[*]}"; exit 1; }
