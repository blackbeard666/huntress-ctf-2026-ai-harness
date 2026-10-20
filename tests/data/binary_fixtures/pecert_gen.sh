#!/bin/bash
# PE + Authenticode-style certificate table fixtures: zig cc -target x86_64-windows-gnu (MinGW PE), openssl req/cms
# (self-signed cert, DER PKCS#7 SignedData), pefile writer (Security dir, CheckSum via generate_checksum), stdlib blob.
set -e
H="$(cd "$(dirname "$0")" && pwd)"; R="$(cd "$H/../../.." && pwd)"; W="${TMPDIR:-/tmp}/pecertgen"; mkdir -p "$W"
PY="$R/.venv/bin/python"
(cd "$W" && PYTHONPATH="$R/tools/pyziglang" python3 -m ziglang cc -target x86_64-windows-gnu -O1 -s -o "$W/a.exe" "$H/pecert_src.c")
openssl req -x509 -newkey rsa:2048 -nodes -keyout "$W/k.pem" -out "$W/c.pem" -days 30 -subj "/CN=Huntress Fixture Signer" 2>/dev/null
openssl cms -sign -binary -in "$W/a.exe" -signer "$W/c.pem" -inkey "$W/k.pem" -outform DER -out "$W/p7.der"
$PY "$H/pecert_asm.py" "$W/a.exe" "$W/p7.der" "$H/pecert_after_cert.bin" tail '{"c2":"198.51.100.40:8443","campaign":"cert-tail","sleep":45,"flag":"flag{p4st_th3_s1gn4tur3}"}'
$PY "$H/pecert_asm.py" "$W/a.exe" "$W/p7.der" "$H/pecert_in_padding.bin" pad '{"c2":"203.0.113.9:443","campaign":"cert-pad","jitter":7,"flag":"flag{h1d1ng_1n_th3_p4dd1ng}"}'
$PY "$H/pecert_asm.py" "$W/a.exe" "$W/p7.der" "$H/pecert_decoy_unsigned.bin" ovl '{"c2":"192.0.2.77:80","campaign":"no-sig","sleep":5,"flag":"flag{n0_c3rt_h3r3}"}'
$PY "$H/pecert_asm.py" "$W/a.exe" "$W/p7.der" "$H/pecert_decoy_badptr.bin" badptr
for f in after_cert:0 in_padding:0 decoy_unsigned:1 decoy_badptr:1; do
  b="$H/pecert_${f%%:*}.bin"
  $PY "$H/pecert_oracle.py" "$b" | $PY "$H/pecert_json.py" "$b" "${f##*:}" > "${b%.bin}.json"
done
