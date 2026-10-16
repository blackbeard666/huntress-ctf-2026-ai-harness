#!/bin/sh
# Identity-derived-key fixtures (coverage atlas rows 32/33). Base = D11 local_secrets.apk (dex carries
# SECRET-056A507A3C2FDE027BFBA2 + MOB-11-4049003462; manifest package com.huntress.mobile.d11.v40490034623b).
# usage: gen_identity_keys.sh <local_secrets.apk> <outdir>    (needs apktool, openssl, python3 stdlib)
set -e
BASE=$1; OUT=$2; W=$(mktemp -d); cd "$W"
apktool d -r -o proj "$BASE" >/dev/null
SECRET=SECRET-056A507A3C2FDE027BFBA2; CASE=MOB-11-4049003462; PKG=com.huntress.mobile.d11.v40490034623b
pj() { printf '{"schema":"huntress.mobile.puzzle.v1","day":11,"codec":"%s","data":"%s"}' "$1" "$2" > proj/assets/huntress_puzzle.json; apktool b -o "$OUT/$3.apk" proj >/dev/null; }
# 1. xor (no key field) with sha256(client secret) digest bytes
CT=$(python3 -I -c 'import hashlib,base64,sys;k=hashlib.sha256(sys.argv[1].encode()).digest();p=b"ANS-7C3E91A05BD2F648";print(base64.b64encode(bytes(c^k[i%len(k)] for i,c in enumerate(p))).decode())' "$SECRET")
pj xor "$CT" idk_xor_sha256_secret
# 2. AES-128-ECB, key = md5(package name) (package only in the binary manifest)
CT=$(printf 'ANS-E05A6B19C4D7F832' | openssl enc -aes-128-ecb -K $(printf "$PKG" | md5sum | cut -c1-32) | base64 -w0)
pj aes "$CT" idk_aes_ecb_md5_package
# 3. AES-256-CBC zero IV, key = sha256(case ref)
CT=$(printf 'answer=ANS-1F9D04C7A2B86E53' | openssl enc -aes-256-cbc -K $(printf "$CASE" | sha256sum | cut -c1-64) -iv 00000000000000000000000000000000 | base64 -w0)
pj aes "$CT" idk_aes_cbc_sha256_case
# 4. DECOY: AES-128-ECB keyed by md5 of a near-miss package (last hex digit changed) -> no derivable key
CT=$(printf 'ANS-B6A2D8E04F1C9735' | openssl enc -aes-128-ecb -K $(printf "${PKG%?}c" | md5sum | cut -c1-32) | base64 -w0)
pj aes "$CT" idk_decoy_aes_nearmiss_package
rm -rf "$W"
