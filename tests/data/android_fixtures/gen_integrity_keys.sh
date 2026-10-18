#!/bin/sh
# Integrity-derived-key fixtures (coverage atlas rows 49 / 33) for lib.android.integrity_key_scan.
# usage: gen_integrity_keys.sh <outdir>   (needs unzip, zip, xxd, openssl, base64, keytool, apksigner, python3 stdlib)
# Dex = classes.dex of idk_xor_sha256_secret.apk (a real d8 dex); decoy key dex = classes.dex of dexeval_b64_parse.apk.
set -e
OUT=$(cd "$1" && pwd); W=$(mktemp -d); cd "$W"
unzip -p "$OUT/idk_xor_sha256_secret.apk" classes.dex > classes.dex
unzip -p "$OUT/idk_xor_sha256_secret.apk" AndroidManifest.xml > AndroidManifest.xml
unzip -p "$OUT/dexeval_b64_parse.apk" classes.dex > other.dex
pj() { printf '{"schema":"huntress.mobile.puzzle.v1","day":18,"codec":"%s","data":"%s"}' "$1" "$2"; }
xorb64() { python3 -I -c 'import sys,base64;k=sys.argv[1].encode() if sys.argv[2]=="t" else bytes.fromhex(sys.argv[1]);p=sys.argv[3].encode();print(base64.b64encode(bytes(c^k[i%len(k)] for i,c in enumerate(p))).decode())' "$@"; }
mk() {  # name puzzle-json [dex]
  rm -rf s; mkdir -p s/assets; cp "${3:-classes.dex}" s/classes.dex; cp AndroidManifest.xml s/; printf '%s' "$2" > s/assets/huntress_puzzle.json
  (cd s && zip -X -q ../"$1".apk classes.dex AndroidManifest.xml assets/huntress_puzzle.json); mv "$1".apk "$OUT/"
}
# 1. AES-128-CBC (IV 0), key = first 16 bytes of the dex header SHA-1 signature (offset 12)
K=$(xxd -s 12 -l 16 -p classes.dex)
mk integ_dexsig_aes128_cbc "$(pj aes "$(printf 'ANS-3f9a07c2e5b1d846' | openssl enc -aes-128-cbc -K "$K" -iv 00000000000000000000000000000000 | base64 -w0)")"
# 2. xor, key = Long.toHexString(zip CRC32 of classes.dex) as text (8 lower hex), payload base64
mk integ_crc32_hex_xor "$(pj xor "$(xorb64 "$(python3 -I -c 'import sys,zlib;print("%08x"%zlib.crc32(open(sys.argv[1],"rb").read()))' classes.dex)" t 'ANS-c70e4b19a2d85f36')")"
# 3. xor, key = the 4 raw bytes of the dex header adler32 checksum (offset 8, as stored)
mk integ_adler32_raw_xor "$(pj xor "$(xorb64 "$(xxd -s 8 -l 4 -p classes.dex)" h 'ANS-81d6f2a09c4e3b57')")"
# 4. AES-128-ECB, key = first 16 bytes of the v2 signer cert SHA-256 (apksigner v2 only: no META-INF/*.RSA)
keytool -genkeypair -keystore k.jks -storepass hunter22 -keypass hunter22 -alias k -keyalg RSA -keysize 2048 \
        -validity 3650 -dname "CN=Huntress Tamper, O=Huntress Labs, C=US" >/dev/null 2>&1
FP=$(keytool -exportcert -keystore k.jks -storepass hunter22 -alias k | sha256sum | cut -c1-32)
mk integ_cert16_aes128_ecb "$(pj aes "$(printf 'ANS-e2b49c07d1f6a385' | openssl enc -aes-128-ecb -K "$FP" | base64 -w0)")"
mv "$OUT/integ_cert16_aes128_ecb.apk" u.zip
apksigner sign --ks k.jks --ks-pass pass:hunter22 --min-sdk-version 28 --v1-signing-enabled false --v2-signing-enabled true \
  --v3-signing-enabled false --v4-signing-enabled false --out "$OUT/integ_cert16_aes128_ecb.apk" u.zip
# 5. DECOY: near-miss token (Q) under this dex's signature key + a valid token keyed by an UNRELATED dex's signature
K2=$(xxd -s 12 -l 16 -p other.dex)
mk integ_decoy_nearmiss "{\"schema\":\"huntress.mobile.puzzle.v1\",\"day\":18,\"codec\":\"aes\",\"data\":\"$(printf 'ANS-3f9a07c2e5b1d84Q' | openssl enc -aes-128-cbc -K "$K" -iv 00000000000000000000000000000000 | base64 -w0)\",\"blob\":\"$(printf 'ANS-5b0e7d3c19a2f468' | openssl enc -aes-128-cbc -K "$K2" -iv 00000000000000000000000000000000 | base64 -w0)\"}"
rm -rf "$W"
