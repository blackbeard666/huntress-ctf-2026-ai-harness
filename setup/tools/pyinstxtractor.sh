#!/usr/bin/env bash
# PyInstaller archive extractor (extremecoders-re/pyinstxtractor): unpacks the CArchive/PYZ of a frozen exe/ELF.
source "$(dirname "$0")/_lib.sh"
mkdir -p tools/pyinstxtractor
[ -s tools/pyinstxtractor/pyinstxtractor.py ] || curl -sfL --max-time 60 -o tools/pyinstxtractor/pyinstxtractor.py \
  https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py
printf '#!/usr/bin/env bash\nexec python3 "%s/tools/pyinstxtractor/pyinstxtractor.py" "$@"\n' "$ROOT" > bin/pyinstxtractor
chmod +x bin/pyinstxtractor; echo "bin/pyinstxtractor"
