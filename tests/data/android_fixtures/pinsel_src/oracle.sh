#!/bin/sh
# usage: oracle.sh <fixture.apk>  -- independent reader (unzip / strings / openssl only, never lib.android): for every
# assets/ payload print its sha256 (hex + base64), whether the host classes.dex strings pin it, whether a shipped
# module.sig verifies against the shipped public key (openssl dgst -verify), whether MANIFEST.MF still matches it, and
# the ANS- strings of every payload that is pinned/signed and not tampered.
set -e
apk=$(realpath "$1"); t=$(mktemp -d "${TMPDIR:-/tmp}/pso.XXXX"); cd "$t"
unzip -q "$apk"
strings -a classes.dex > host.txt
for p in $(find assets -type f \( -name '*.dex' -o -name '*.bin' \) | sort); do
  hex=$(openssl dgst -sha256 -r "$p" | cut -c1-64); b64=$(openssl dgst -sha256 -binary "$p" | base64)
  pinned=no; grep -qF -e "$hex" -e "$b64" host.txt && pinned=yes
  signed=no; sig=$(dirname "$p")/module.sig; pub=$(dirname "$p")/module_pub.pem
  [ -f "$sig" ] && openssl dgst -sha256 -verify "$pub" -signature "$sig" "$p" >/dev/null 2>&1 && signed=yes
  mf=n/a; if [ -f META-INF/MANIFEST.MF ]; then
    want=$(tr -d '\r' < META-INF/MANIFEST.MF | grep -A1 -x "Name: $p" | sed -n 's/^SHA-256-Digest: //p')
    [ "$want" = "$b64" ] && mf=ok || mf=MISMATCH; fi
  sel=; [ "$mf" != MISMATCH ] && { [ $pinned = yes ] || [ $signed = yes ]; } && sel="SELECTED $(strings -a "$p" | grep -oE 'ANS-[0-9a-fA-F]{16}' | tr '\n' ' ')"
  echo "$p sha256=$hex pinned=$pinned signed=$signed manifest=$mf $sel"
done
cd /; rm -rf "$t"
