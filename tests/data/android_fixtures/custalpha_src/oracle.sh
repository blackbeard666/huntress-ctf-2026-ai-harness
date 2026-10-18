#!/bin/sh
# usage: oracle.sh <fixture.apk>  -- independent reader: the alphabet comes from dex2jar + javap -constants (Table.T)
# or jq (assets/cfg.json .table); the data from unzip + jq; decoding by tr + base64/base32 -d (codec custom64/t32),
# int arithmetic (b58x) or tr back through the sorted alphabet (mono). Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/cao.XXXX"); cd "$t"
codec=$(unzip -p "$apk" assets/huntress_puzzle.json | jq -r .codec)
data=$(unzip -p "$apk" assets/huntress_puzzle.json | jq -r .data)
if unzip -l "$apk" assets/cfg.json >/dev/null 2>&1; then alpha=$(unzip -p "$apk" assets/cfg.json | jq -r .table)
else "$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
  alpha=$(javap -cp app.jar -constants com.huntress.mobile.d20.k7.Table | sed -n 's/.*String T = "\(.*\)";/\1/p'); fi
case "$codec" in
  custom64) printf %s "$data" | tr "$alpha" 'A-Za-z0-9+/' | base64 -d ;;
  t32) printf %s "$data" | tr "$alpha" 'A-Z2-7' | base32 -d ;;
  b58x) python3 -I -c 'import sys; a,d=sys.argv[1:]; n=0
for c in d: n=n*58+a.index(c)
sys.stdout.write(n.to_bytes((n.bit_length()+7)//8,"big").decode())' "$alpha" "$data" ;;
  mono) printf %s "$data" | tr "$alpha" "$(printf %s "$alpha" | fold -w1 | LC_ALL=C sort | tr -d '\n')" ;;
esac; echo
cd /; rm -rf "$t"
