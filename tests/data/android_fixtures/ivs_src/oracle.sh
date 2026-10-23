#!/bin/sh
# Independent oracle: keytool -printcert -jarfile (signer cert sha256) + unzip + jq / openssl (verdict JSON, JWS payload, nonce) -> the
# ANS tied to the clean verdict. Usage: sh oracle.sh plain|legacy <apk>
set -e
K=$1; X=$2
CERT=$(keytool -printcert -jarfile "$X" | sed -n "s/.*SHA256: //p" | head -1 | tr -d ":" | xxd -r -p | base64 | tr -d "=")
if [ "$K" = plain ]; then
  N=$(unzip -p "$X" assets/integrity/request.json | jq -r .nonce)
  unzip -p "$X" assets/integrity/verdicts.json | jq -r --arg c "$CERT" --arg n "$N" '.responses[] | .payload as $p | select($p.appIntegrity.appRecognitionVerdict=="PLAY_RECOGNIZED" and any($p.deviceIntegrity.deviceRecognitionVerdict[]; .=="MEETS_DEVICE_INTEGRITY" or .=="MEETS_STRONG_INTEGRITY") and $p.accountDetails.appLicensingVerdict=="LICENSED" and any($p.appIntegrity.certificateSha256Digest[]; .==$c) and $p.requestDetails.nonce==$n) | .unlock'
else
  N=$(unzip -p "$X" res/raw/session.json | jq -j .challenge | openssl dgst -sha256 -binary | base64)
  unzip -p "$X" res/raw/attest.json | jq -r --arg n "$N" --arg c "$CERT" '.attempts[] | (.jws|split(".")[1]|gsub("-";"+")|gsub("_";"/")|. + ("=" * ((4 - length % 4) % 4))|@base64d|fromjson) as $p | select($p.ctsProfileMatch==true and $p.basicIntegrity==true and $p.nonce==$n and any($p.apkCertificateDigestSha256[]; .==$c)) | .reward'
fi
