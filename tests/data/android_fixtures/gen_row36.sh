#!/bin/bash
# Row 36 fixtures: assets/huntress_puzzle.json payloads built with standard tools (gzip/xz/bzip2/base64/base32/xxd/tr/perl).
set -euo pipefail
OUT=${1:?outdir}
mk() {  # name codec data [key]
  local d; d=$(mktemp -d)
  mkdir -p "$d/assets"
  if [ $# -ge 4 ]; then jq -cn --arg c "$2" --arg d "$3" --arg k "$4" '{codec:$c,data:$d,key:$k}' > "$d/assets/huntress_puzzle.json"
  else jq -cn --arg c "$2" --arg d "$3" '{codec:$c,data:$d}' > "$d/assets/huntress_puzzle.json"; fi
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets); rm -rf "$d"
}
mk chain_gzip_b64   "gz64"       "$(printf 'token=ANS-4be19c07d3a25f86' | gzip -9n | base64 -w0)"
mk chain_xz_hex     "xzhex"      "$(printf 'pad=%s ANS-0d7e3a91c58b26f4' "$(printf '=%.0s' $(seq 64))" | xz -9 -c | xxd -p | tr -d '\n')"
mk chain_bz2_b32    "bzb32"      "$(printf 'answer ANS-e5c3907b1f2a64d8' | bzip2 -9 -c | base32 -w0)"
mk chain_binary     "bits"       "$(printf 'ANS-71f0a2c9e4d38b56' | perl -ne 'print join " ", map { unpack "B8", $_ } split //')"
mk chain_rot47      "r47"        "$(printf 'code: ANS-9c4e2b7a0f13d865' | tr '!-~' 'P-~!-O')"
mk chain_atbash_b64 "mirror64"   "$(printf 'ANS-b2d84f6e09a1c357' | tr 'A-Za-z' 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba' | base64 -w0)"
mk chain_vigenere   "vig"        "$(printf 'flag ANS-3a6f0e9d2c81b74e' | perl -ne '@k=map{ord($_)-65}split//,"HUNTRESS";$j=0;for(split//){if(/[A-Za-z]/){$b=/[a-z]/?97:65;print chr((ord($_)-$b+$k[$j++%@k])%26+$b)}else{print}}')" "HUNTRESS"
mk chain_railfence  "zigzag"     "$(printf 'ANS-c80f5e2b9d4a7136 ok' | perl -ne '$r=3;@row=();$i=0;$d=1;for(split//){$row[$i].=$_;$d=-1 if $i==$r-1;$d=1 if $i==0;$i+=$d}print join "",@row')" "3"
mk chain_decoy_gzip_nearmiss "gz64" "$(printf 'token=ANS-3fa9c2e17b04d68' | gzip -9n | base64 -w0)"
mk chain_decoy_rot47_nearmiss "r47" "$(printf 'code: ANS-91d0e7a4c35b2fZZ' | tr '!-~' 'P-~!-O')"
