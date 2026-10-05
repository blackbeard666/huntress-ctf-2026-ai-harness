#!/usr/bin/env bash
# Reproducible environment prep for the hardening upgrades (reference/HARDENING.md). Idempotent.
# Run once on a fresh WSL checkout:  bash setup/harden-env.sh
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"

echo "== apt packages (JDK21 for Ghidra, upx, john, foremost) =="
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    openjdk-21-jdk-headless upx-ucl john foremost || echo "WARN: some apt packages failed"

echo "== point Ghidra at JDK 21 (it rejects JDK 25) =="
JDK21="$(ls -d /usr/lib/jvm/java-21-openjdk-amd64 2>/dev/null | head -1)"
LP="$ROOT/tools/ghidra/support/launch.properties"
if [ -n "$JDK21" ] && [ -f "$LP" ]; then
  if grep -q '^JAVA_HOME_OVERRIDE=' "$LP"; then
    sed -i "s#^JAVA_HOME_OVERRIDE=.*#JAVA_HOME_OVERRIDE=$JDK21#" "$LP"
  else
    echo "JAVA_HOME_OVERRIDE=$JDK21" >> "$LP"
  fi
  echo "  set JAVA_HOME_OVERRIDE=$JDK21"
else
  echo "  WARN: JDK21 or launch.properties not found"
fi

echo "== python decompilers / recovery tools into the venv =="
# pyc->source for extracted PyInstaller apps (decompyle3 covers 3.7-3.8; for 3.9+ prefer a pycdc build).
"$ROOT/.venv/bin/pip" install -q decompyle3 2>/dev/null || echo "  WARN: decompyle3 install failed"
# zip/office/pdf cracking: john-jumbo ships *2john; the distro 'john' may lack them. Check:
command -v zip2john >/dev/null || echo "  NOTE: zip2john missing (install john-jumbo for the hashcat crack pipeline)"

echo "== optional downloads (manual — not all have apt packages) =="
echo "  GoReSym (stripped-Go recovery, nicer than lib.binary.go_pclntab_funcs): https://github.com/mandiant/GoReSym/releases"
echo "  rustfilt:  cargo install rustfilt   (Rust symbol demangling)"
echo "  de4dot / ilspycmd:  need mono/dotnet for .NET deobfuscation"
echo "  pycdc:  cmake build from https://github.com/zrax/pycdc  (pyc->source for modern Python)"
echo "done."
