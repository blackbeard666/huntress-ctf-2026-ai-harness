#!/bin/bash
# Independent oracle: openssl SPKI pin of every shipped cert (res/raw DER / assets PEM), `aapt dump xmltree` NSC pins +
# `unzip -p classes.dex | strings` OkHttp pins -> the matching cert's digest decrypts assets/huntress_puzzle.json "data"
# with `openssl enc -d -aes-256-ecb` or a python3 repeating-key XOR. Prints "match <pin> <cert>" and the token (or none).
set -uo pipefail
A=$1; w=$(mktemp -d)
pins=$( { aapt dump xmltree "$A" res/xml/network_security_config.xml | grep -oP 'C: "\K[A-Za-z0-9+/=]{40,}';
          unzip -p "$A" classes.dex | strings | grep -oP 'sha256/\K[A-Za-z0-9+/]{43}='; } )
unzip -Z1 "$A" | grep -E '^(res/raw|assets)/' | while read -r e; do
  unzip -p "$A" "$e" > "$w/f"
  if head -c 11 "$w/f" | grep -q -- '-----BEGIN'; then
    csplit -s -z -f "$w/c" "$w/f" '/-----BEGIN/' '{*}'; for c in "$w"/c*; do openssl x509 -in "$c" -outform der -out "$c.der" 2>/dev/null && echo "$c.der"; done
  else openssl x509 -inform der -in "$w/f" -noout 2>/dev/null && cp "$w/f" "$w/$(basename "$e").der" && echo "$w/$(basename "$e").der"; fi
done > "$w/certs"
ct=$(unzip -p "$A" assets/huntress_puzzle.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"])')
found=none
while read -r c; do
  pin=$(openssl x509 -inform der -in "$c" -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64 -w0)
  grep -qxF "$pin" <<<"$pins" || continue
  echo "match sha256/$pin $(openssl x509 -inform der -in "$c" -noout -subject -enddate | tr '\n' ' ')" >&2
  k=$(echo "$pin" | base64 -d | xxd -p -c64)
  t=$( { echo "$ct" | base64 -d | openssl enc -d -aes-256-ecb -K "$k" 2>/dev/null;
         python3 -c 'import sys,base64; k=bytes.fromhex(sys.argv[1]); c=base64.b64decode(sys.argv[2]);
print(bytes(x ^ k[i % len(k)] for i, x in enumerate(c)).decode("latin1"))' "$k" "$ct"; } | grep -aoE 'ANS-[0-9a-fA-F]{16}' | head -1)
  [ -n "$t" ] && found=$t
done < "$w/certs"
echo "$found"; rm -rf "$w"
