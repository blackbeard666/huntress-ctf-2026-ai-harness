#!/usr/bin/env bash
# Provision Homebase so ANY solver can run next to the Game Master (hb_timed executes solvers there).
# Light deps only (no angr/ghidra — Homebase has ~3GB RAM); heavy analysis stays on the local box.
# Idempotent; re-run after a Homebase factory reset.
set -uo pipefail

# System packages the solvers shell out to (we have sudo on Homebase). binutils => c++filt/strings/nm/objdump/
# readelf; p7zip-full => 7z (so investigation + unzip() use the real tool, not a pyzipper-only fallback).
# Non-fatal if apt is offline / no sudo: pyzipper still covers AES zips and the pure-Python paths still work.
if command -v apt-get >/dev/null 2>&1; then
  sudo -n DEBIAN_FRONTEND=noninteractive apt-get update -qq 2>/dev/null || true
  if sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        p7zip-full unzip file binutils nodejs 2>/dev/null; then
    echo "[hb-setup] apt tools installed (7z/unzip/file/binutils/node)"
  else
    echo "[hb-setup] apt install skipped/failed (offline or no passwordless sudo) — pyzipper covers AES zips"
  fi
fi

# No root (the VM): `hctf hb setup` pushed the official static 7-Zip as ~/.local/bin/7zz -- expose it as 7z when the
# system has none. hb_timed and Homebase workers put ~/.local/bin on PATH.
mkdir -p ~/.local/bin
if ! command -v 7z >/dev/null 2>&1 && [ -x ~/.local/bin/7zz ]; then
  ln -sf ~/.local/bin/7zz ~/.local/bin/7z && echo "[hb-setup] 7z -> ~/.local/bin/7zz (static 7-Zip, no root)"
fi
export PATH="$HOME/.local/bin:$PATH"

PIP="python3 -m pip install --user --break-system-packages -q"
$PIP pyelftools pefile capstone keystone-engine unicorn pycryptodome pyzipper \
     androguard oletools python-evtx regipy LnkParse3 binary-refinery \
     yara-python python-magic olefile pillow xdis dnfile droidasc requests 2>&1 | tail -2
echo "[hb-setup] python deps installed"
# tools that solvers shell out to
for t in node c++filt unzip 7z strings file; do
  command -v "$t" >/dev/null && echo "[ok] $t" || echo "[MISSING] $t"
done
python3 - <<'PY'
mods = ["elftools", "pefile", "capstone", "Crypto", "pyzipper", "androguard", "droidasc", "refinery"]
import importlib
bad = [m for m in mods if importlib.util.find_spec(m) is None]
print("[hb-setup] import check:", "ALL OK" if not bad else f"MISSING {bad}")
PY
