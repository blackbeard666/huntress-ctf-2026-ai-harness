#!/usr/bin/env bash
# Install the non-apt analysis tools workers' lane skills call for, under the project (tools/) with wrappers/symlinks in
# bin/ (on every worker's PATH and visible inside the worker sandbox). Idempotent. apt packages: see setup/README or run
#   sudo apt-get install -y radare2 qpdf poppler-utils mupdf-tools pngcheck steghide sqlite3 mediainfo yara aapt \
#        apksigner dotnet-sdk-10.0 cargo rustc foremost ruby
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$ROOT" || exit 1
mkdir -p tools/bin bin
link() { ln -sfn "$1" "bin/$2" && echo "  bin/$2 -> $1"; }

echo "== GoReSym (Go symbol recovery)"
GOBIN="$ROOT/tools/bin" go install github.com/mandiant/GoReSym@latest 2>&1 | tail -2
[ -x tools/bin/GoReSym ] && link "$ROOT/tools/bin/GoReSym" GoReSym

echo "== rustfilt (Rust demangler)"
cargo install --root "$ROOT/tools/cargo" rustfilt 2>&1 | tail -1
[ -x tools/cargo/bin/rustfilt ] && link "$ROOT/tools/cargo/bin/rustfilt" rustfilt

echo "== ilspycmd (.NET decompiler)"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
dotnet tool install --tool-path "$ROOT/tools/dotnet-tools" ilspycmd 2>&1 | tail -1 \
  || dotnet tool update --tool-path "$ROOT/tools/dotnet-tools" ilspycmd 2>&1 | tail -1
[ -x tools/dotnet-tools/ilspycmd ] && link "$ROOT/tools/dotnet-tools/ilspycmd" ilspycmd
command -v dotnet >/dev/null && link "$(command -v dotnet)" dotnet

echo "== dex2jar"
if [ ! -d tools/dex2jar ]; then
  url=$(curl -s --max-time 20 https://api.github.com/repos/ThexXTURBOXx/dex2jar/releases/latest | grep -o '"browser_download_url": "[^"]*dex-tools[^"]*zip"' | cut -d'"' -f4 | head -1)
  curl -sL --max-time 120 -o .run/dex2jar.zip "$url" && unzip -q -o .run/dex2jar.zip -d tools/dex2jar.tmp \
    && mv "$(find tools/dex2jar.tmp -maxdepth 1 -mindepth 1 -type d | head -1)" tools/dex2jar && rm -rf tools/dex2jar.tmp .run/dex2jar.zip
fi
chmod +x tools/dex2jar/*.sh 2>/dev/null
[ -x tools/dex2jar/d2j-dex2jar.sh ] && link "$ROOT/tools/dex2jar/d2j-dex2jar.sh" d2j-dex2jar && link "$ROOT/tools/dex2jar/d2j-dex2jar.sh" dex2jar

echo "== pdf-parser / pdfid (Didier Stevens)"
mkdir -p tools/didier
for f in pdf-parser.py pdfid.py; do
  [ -f tools/didier/$f ] || curl -sL --max-time 30 -o tools/didier/$f "https://raw.githubusercontent.com/DidierStevens/DidierStevensSuite/master/$f"
  printf '#!/usr/bin/env bash\nexec python3 "%s/tools/didier/%s" "$@"\n' "$ROOT" "$f" > "bin/${f%.py}"; chmod +x "bin/${f%.py}"
  echo "  bin/${f%.py} -> tools/didier/$f"
done

echo "== zsteg (PNG/BMP stego)"
GEM_HOME="$ROOT/tools/gems" gem install --no-document zsteg 2>&1 | tail -1
printf '#!/usr/bin/env bash\nGEM_HOME="%s/tools/gems" exec "%s/tools/gems/bin/zsteg" "$@"\n' "$ROOT" "$ROOT" > bin/zsteg; chmod +x bin/zsteg

echo "== uncompyle6 (Python bytecode decompiler, venv)"
uv pip install -q --python .venv/bin/python uncompyle6 2>&1 | tail -1

echo "== rabin2 alias check (radare2 from apt)"
command -v rabin2 >/dev/null && echo "  rabin2 ok"
