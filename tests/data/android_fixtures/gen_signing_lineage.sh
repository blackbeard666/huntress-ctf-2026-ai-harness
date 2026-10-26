#!/bin/sh
# APK Signature Scheme v3 / v3.1 key-rotation fixtures (coverage atlas rows 59 / 105) for lib.android.signing_lineage_scan.
# usage: gen_signing_lineage.sh <outdir>   (needs keytool, apksigner >= 33 (rotate, --lineage, --rotation-min-sdk-version), zip)
# Each APK = a zip (`zip -X`) of a stub manifest + assets/huntress_puzzle.json; `apksigner rotate` builds the
# proof-of-rotation lineage old -> new, `apksigner sign --lineage` embeds it (attr 0x3ba06f8c) in the v3 / v3.1 signer.
set -e
OUT=$(cd "$1" && pwd); W=$(mktemp -d); cd "$W"
key() { keytool -genkeypair -keystore "$1.jks" -storepass hunter22 -keypass hunter22 -alias k -keyalg "${3:-RSA}" \
          -validity 3650 -dname "$2" >/dev/null 2>&1; }
rot() { apksigner rotate --out "$3" --old-signer --ks "$1.jks" --ks-pass pass:hunter22 \
          --new-signer --ks "$2.jks" --ks-pass pass:hunter22 ${4:-}; }
mk() {  # name puzzle-json old new lineage apksigner-flags...
  n=$1; pj=$2; o=$3; nw=$4; lin=$5; shift 5; rm -rf s; mkdir -p s/assets; printf 'stub' > s/AndroidManifest.xml
  printf '%s' "$pj" > s/assets/huntress_puzzle.json; (cd s && zip -X -q -r ../u.zip .)
  apksigner sign --ks "$o.jks" --ks-pass pass:hunter22 --next-signer --ks "$nw.jks" --ks-pass pass:hunter22 \
    --lineage "$lin" "$@" --out "$OUT/$n.apk" u.zip; rm -f u.zip
}
NOTE='{"schema":"huntress.mobile.puzzle.v1","day":27,"codec":"none","data":"the app is signed by whoever the device trusts now"}'
# 1. v3.0 only (no v1/v2/v3.1, no META-INF; rotation from SDK 28 = the minSdk): token in the ORIGINAL signer's OU, present only in the proof-of-rotation lineage
key o1 "CN=Huntress Original, OU=ANS-3D7A0C59E1B48F26, O=Huntress Labs, C=US"
key n1 "CN=Huntress Rotated, O=Huntress Labs, C=US" EC
rot o1 n1 l1.bin
mk rot_v3_past_signer "$NOTE" o1 n1 l1.bin --min-sdk-version 28 --rotation-min-sdk-version 28 \
   --v1-signing-enabled false --v2-signing-enabled false --v3-signing-enabled true --v4-signing-enabled false
# 2. v3.1 rotation targeted at SDK 33+: v2/v3.0 by the original key (token A; minSdk 24 -> no v1), v3.1 by the rotated
#    key (token B, base64 in O) + a v4 .idsig (signed by the rotated key); a device at SDK 34 reports B via
#    getApkContentsSigners() and [A, B] via getSigningCertificateHistory()
key o2 "CN=Huntress Original, OU=ANS-0F1E2D3C4B5A6978, O=Huntress Labs, C=US"
key n2 "CN=Huntress Rotated, O=$(printf 'ANS-B62E09D4C7F1A385' | base64 -w0), C=US"
rot o2 n2 l2.bin "--set-installed-data true --set-permission false"
mk rot_v31_current_signer "$NOTE" o2 n2 l2.bin --min-sdk-version 24 --rotation-min-sdk-version 33 \
   --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true --v4-signing-enabled true
# 3. DECOY: same v3.1 layout, near-miss tokens (15 hex) in both signers
key o3 "CN=Huntress Original, OU=ANS-3D7A0C59E1B48F2, O=Huntress Labs, C=US"
key n3 "CN=Huntress Rotated, OU=ANS-B62E09D4C7F1A38, O=Huntress Labs, C=US"
rot o3 n3 l3.bin
mk rot_decoy_nearmiss "$NOTE" o3 n3 l3.bin --min-sdk-version 24 --rotation-min-sdk-version 33 --v4-signing-enabled false
rm -rf "$W"
