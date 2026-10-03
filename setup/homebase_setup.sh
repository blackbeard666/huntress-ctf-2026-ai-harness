#!/usr/bin/env bash
# Provision Homebase so ANY solver can run next to the Game Master (hb_timed executes solvers there).
# Light deps only (no angr/ghidra — Homebase has ~3GB RAM); heavy analysis stays on the local box.
# Idempotent; re-run after a Homebase factory reset.
set -uo pipefail
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
