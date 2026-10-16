#!/bin/sh
# Signing-certificate fixtures (coverage atlas rows 9 / 49 / 59) for lib.android.signing_cert_scan.
# usage: gen_signing_certs.sh <outdir>      (needs keytool, apksigner, zip, base64, python3 stdlib)
# Each APK = a zip (`zip -X`) of a stub manifest + assets/huntress_puzzle.json, signed by apksigner with a fresh keytool key.
set -e
OUT=$(cd "$1" && pwd); W=$(mktemp -d); cd "$W"
key() { keytool -genkeypair -keystore "$1.jks" -storepass hunter22 -keypass hunter22 -alias k -keyalg RSA -keysize 2048 \
          -validity 3650 -dname "$2" >/dev/null 2>&1; }
mk() {  # name puzzle-json keystore apksigner-scheme-flags...
  n=$1; pj=$2; ks=$3; shift 3; rm -rf s; mkdir -p s/assets; printf 'stub' > s/AndroidManifest.xml
  printf '%s' "$pj" > s/assets/huntress_puzzle.json; (cd s && zip -X -q -r ../u.zip .)
  apksigner sign --ks "$ks.jks" --ks-pass pass:hunter22 --min-sdk-version 28 --v4-signing-enabled false "$@" --out "$OUT/$n.apk" u.zip; rm -f u.zip
}
NOTE='{"schema":"huntress.mobile.puzzle.v1","day":16,"codec":"none","data":"see the signer"}'
# 1. token in the subject OU (plain), v1 JAR signature + v2 block
key k1 "CN=Huntress Release, OU=ANS-5A0C7E19D3B46F28, O=Huntress Labs, C=US"
mk sig_dn_plain_v1v2 "$NOTE" k1 --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled false
# 2. token base64'd in the subject O, v3 block only (no META-INF/*.RSA, no v2)
key k2 "CN=Huntress Release, O=$(printf 'ANS-C41E8B7290DF365A' | base64 -w0), C=US"
mk sig_dn_b64_v3only "$NOTE" k2 --v1-signing-enabled false --v2-signing-enabled false --v3-signing-enabled true
# 3. integrity-check key: puzzle data = b64(token xor sha256(signing cert DER)), codec xor, no key field; v1+v2
key k3 "CN=Huntress Release, O=Huntress Labs, C=US"
FP=$(keytool -exportcert -keystore k3.jks -storepass hunter22 -alias k | sha256sum | cut -c1-64)
CT=$(python3 -I -c 'import sys,base64;k=bytes.fromhex(sys.argv[1]);p=b"ANS-9E27D05B6C1AF843";print(base64.b64encode(bytes(c^k[i%32] for i,c in enumerate(p))).decode())' "$FP")
mk sig_key_sha256_xor "{\"schema\":\"huntress.mobile.puzzle.v1\",\"day\":16,\"codec\":\"xor\",\"data\":\"$CT\"}" k3 \
   --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled false
# 4. DECOY: near-miss DN token (15 hex) and a payload keyed by the sha256 of an UNRELATED cert (k3's), signed by k4
key k4 "CN=Huntress Release, OU=ANS-5A0C7E19D3B46F2, O=Huntress Labs, C=US"
CT=$(python3 -I -c 'import sys,base64;k=bytes.fromhex(sys.argv[1]);p=b"ANS-1B8F6E3D20C7A954";print(base64.b64encode(bytes(c^k[i%32] for i,c in enumerate(p))).decode())' "$FP")
mk sig_decoy_nearmiss "{\"schema\":\"huntress.mobile.puzzle.v1\",\"day\":16,\"codec\":\"xor\",\"data\":\"$CT\"}" k4 \
   --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled false
rm -rf "$W"
