#!/bin/sh
# APK Signing Block id-value pair fixtures (coverage atlas rows 59 / 62) for lib.android.signing_block_scan.
# usage: gen_signing_block.sh <outdir>      (needs keytool, apksigner, zip, python3 stdlib)
# Each APK = `zip -X` of a stub manifest + an uninformative assets/huntress_puzzle.json, v2-signed by apksigner, then a
# channel-style pair is inserted into the APK Signing Block the way Walle / VasDolly do it (stdlib writer below: new
# uint64-length id-value pair before the footer, both block sizes and the EOCD central-directory offset patched).
set -e
OUT=$(cd "$1" && pwd); W=$(mktemp -d); cd "$W"
keytool -genkeypair -keystore k.jks -storepass hunter22 -keypass hunter22 -alias k -keyalg RSA -keysize 2048 \
        -validity 3650 -dname "CN=Huntress Release, O=Huntress Labs, C=US" >/dev/null 2>&1
cat > inject.py <<'PY'
import struct, sys
src, dst, pid, val = sys.argv[1], sys.argv[2], int(sys.argv[3], 16), sys.argv[4].encode()
b = open(src, "rb").read()
e = b.rfind(b"PK\x05\x06")
cd = struct.unpack_from("<I", b, e + 16)[0]
assert b[cd - 16:cd] == b"APK Sig Block 42"
size = struct.unpack_from("<Q", b, cd - 24)[0]
start = cd - size - 8
pairs = b[start + 8:cd - 24] + struct.pack("<QI", len(val) + 4, pid) + val
nsize = len(pairs) + 24
blk = struct.pack("<Q", nsize) + pairs + struct.pack("<Q", nsize) + b"APK Sig Block 42"
eocd = bytearray(b[e:])
struct.pack_into("<I", eocd, 16, start + len(blk))
open(dst, "wb").write(b[:start] + blk + b[cd:e] + bytes(eocd))
PY
mk() {  # name id-hex value
  rm -rf s u.zip; mkdir -p s/assets; printf 'stub' > s/AndroidManifest.xml
  printf '%s' '{"schema":"huntress.mobile.puzzle.v1","day":17,"codec":"none","data":"the channel knows"}' > s/assets/huntress_puzzle.json
  (cd s && zip -X -q -r ../u.zip .)
  apksigner sign --ks k.jks --ks-pass pass:hunter22 --min-sdk-version 24 --v1-signing-enabled false \
     --v2-signing-enabled true --v3-signing-enabled false --v4-signing-enabled false --out signed.apk u.zip
  python3 -I inject.py signed.apk "$OUT/$1.apk" "$2" "$3"; rm -f signed.apk
  apksigner verify --min-sdk-version 24 "$OUT/$1.apk"   # the v2 signature does not cover the block itself: still verifies
}
# 1. Walle channel pair (0x71777777) holding JSON with the token in plain text
mk sigblk_walle_json_plain 71777777 '{"channel":"huntress","answer":"ANS-3F9A0C6B21E7D854"}'
# 2. VasDolly-style channel pair (0x881155ff) holding the token base64'd
mk sigblk_vasdolly_b64 881155ff "$(printf 'ANS-B7046E1DC9A2F35E' | base64 -w0)"
# 3. DECOY: same layout, the Walle pair carries a near-miss token (15 hex) only
mk sigblk_decoy_nearmiss 71777777 '{"channel":"huntress","answer":"ANS-3F9A0C6B21E7D85"}'
rm -rf "$W"
