#!/bin/sh
# In-dex integrity-gate fixtures (coverage atlas: dex-bytecode-integrity-gate) for lib.android.dex_integrity_gate_scan.
# usage: gen_dex_integrity_gate.sh <outdir>   (needs unzip, zip, openssl, sha1sum, base64, xxd, python3 + androguard)
# Dex = classes.dex of idk_xor_sha256_secret.apk (a real d8 dex); decoy key dex = classes.dex of dexeval_b64_parse.apk.
# Method code_item offsets come from androguard (EncodedMethod.get_code_off / DalvikCode.get_insns_size).
set -e
OUT=$(cd "$1" && pwd); W=$(mktemp -d); cd "$W"
unzip -p "$OUT/idk_xor_sha256_secret.apk" classes.dex > classes.dex
unzip -p "$OUT/idk_xor_sha256_secret.apk" AndroidManifest.xml > AndroidManifest.xml
unzip -p "$OUT/dexeval_b64_parse.apk" classes.dex > other.dex
pj() { printf '{"schema":"huntress.mobile.puzzle.v1","day":20,"codec":"%s","data":"%s"}' "$1" "$2"; }
xorb() { python3 -I -c 'import sys;k=sys.argv[1].encode() if sys.argv[2]=="t" else bytes.fromhex(sys.argv[1]);p=sys.argv[3].encode();sys.stdout.buffer.write(bytes(c^k[i%len(k)] for i,c in enumerate(p)))' "$@"; }
# code_item bytes (header + insns, or insns only with "i") of <class-suffix> <method>
ci() { python3 -I -c 'import sys
from loguru import logger; logger.remove()
from androguard.core.dex import DEX
b=open("classes.dex","rb").read();d=DEX(b)
m=[m for c in d.get_classes() if c.get_name().endswith(sys.argv[1]) for m in c.get_methods() if m.get_name()==sys.argv[2]][0]
o=m.get_code_off();n=m.get_code().get_insns_size();sys.stdout.buffer.write(b[o+16:o+16+2*n] if sys.argv[3]=="i" else b[o:o+16+2*n])' "$@"; }
mk() {  # name puzzle-json [extra-asset-file]
  rm -rf s; mkdir -p s/assets; cp classes.dex AndroidManifest.xml s/; printf '%s' "$2" > s/assets/huntress_puzzle.json
  [ -n "$3" ] && cp "$3" s/assets/
  (cd s && zip -X -q -r ../"$1".apk classes.dex AndroidManifest.xml assets); mv "$1".apk "$OUT/"
}
# 1. xor, key = the 20 raw bytes of SHA-1 over the WHOLE classes.dex (MessageDigest over the zip entry), base64
K=$(sha1sum classes.dex | cut -c1-40)
mk dbi_wholedex_sha1_xor "$(pj integrity "$(xorb "$K" h 'ANS-9c41e07b2d5af386' | base64 -w0)")"
# 2. AES-128-CBC with the IV prepended, key = MD5 of ChallengeActivity.onCreate's whole code_item; raw asset assets/gate.bin
K=$(ci ChallengeActivity\; onCreate c | md5sum | cut -c1-32); IV=$(openssl rand -hex 16)
{ printf '%s' "$IV" | xxd -r -p; printf 'ANS-47e2b9d05c18fa63' | openssl enc -aes-128-cbc -K "$K" -iv "$IV"; } > gate.bin
mk dbi_codeitem_md5_aes_cbc "$(pj integrity 'see gate.bin')" gate.bin
# 3. xor, key = Integer.toHexString-style 8-hex text of CRC32 over MainActivity.onCreate's insns only, payload hex
K=$(ci MainActivity\; onCreate i | python3 -I -c 'import sys,zlib;print("%08x"%zlib.crc32(sys.stdin.buffer.read()))')
mk dbi_insns_crc32_hex_xor "$(pj integrity "$(xorb "$K" t 'ANS-d3086af1c75e294b' | xxd -p | tr -d '\n')")"
# 4. DECOY: near-miss token (Z) under this dex's whole SHA-1 + a valid token keyed by an UNRELATED dex's whole SHA-1
K=$(sha1sum classes.dex | cut -c1-40); K2=$(sha1sum other.dex | cut -c1-40)
mk dbi_decoy_nearmiss "{\"schema\":\"huntress.mobile.puzzle.v1\",\"day\":20,\"codec\":\"integrity\",\"data\":\"$(xorb "$K" h 'ANS-9c41e07b2d5af38Z' | base64 -w0)\",\"blob\":\"$(xorb "$K2" h 'ANS-60b8e2f14d9a7c35' | base64 -w0)\"}"
rm -rf "$W"
