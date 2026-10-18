#!/usr/bin/env bash
# ZIP-structure anomaly fixtures (coverage atlas row 62) -- built with Info-ZIP `zip`, coreutils and the CPython zipfile
# WRITER only; the expected tokens are read back with funzip / unzip -z / tail+base32 (see each fixture's oracle_cmd).
# usage: gen_zip_structure.sh <outdir>
set -euo pipefail
out=$(realpath "${1:?outdir}"); w=$(mktemp -d); cd "$w"
mkdir -p assets
printf 'not here\n' > assets/readme.txt
printf 'dex\n035\0' > classes.dex
puz() { printf '{"codec":"base64","data":"%s"}' "$(printf '%s' "$1" | base64 -w0)"; }

# 1. duplicate name: the real puzzle first (what Android installs), a decoy shadow last (what zipfile.read returns)
python3 -I -W ignore -c 'import sys, zipfile
z = zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED)
z.write("classes.dex"); z.writestr("assets/huntress_puzzle.json", sys.argv[2]); z.writestr("assets/huntress_puzzle.json", sys.argv[3]); z.close()' \
  "$out/zipanom_dup_shadow.apk" "$(puz ANS-7c41e09b3d5f2a86)" "$(puz 'decoy: nothing to see here')"

# 2. local-only entry: a zip with its central directory cut off, prepended to an ordinary apk (zip -A re-bases it)
puz ANS-d2096fb4ae1c8357 > assets/huntress_puzzle.json; rm -f inner.zip; zip -qX inner.zip assets/huntress_puzzle.json
cut=$(grep -obUaP 'PK\x01\x02' inner.zip | head -1 | cut -d: -f1); head -c "$cut" inner.zip > hidden.bin
rm assets/huntress_puzzle.json; zip -qX outer.zip classes.dex assets/readme.txt
cat hidden.bin outer.zip > "$out/zipanom_local_only.apk"; zip -qA "$out/zipanom_local_only.apk"

# 3. data after the EOCD: base32 of the token appended to an ordinary apk
rm -f t.zip; zip -qX t.zip classes.dex assets/readme.txt
{ cat t.zip; printf '%s' ANS-5be38a0f91c46d27 | base32 -w0; } > "$out/zipanom_eocd_trailer.apk"

# 4. archive comment: gzip+base64 of the token (zip -z)
rm -f t.zip; zip -qX t.zip classes.dex assets/readme.txt
printf '%s' ANS-3f8e1a7c60b2d945 | gzip -9n | base64 -w0 | zip -qz t.zip; cp t.zip "$out/zipanom_comment.apk"

# 5. non-standard extra field 0x6873 ("sh") on a local + central record: hex of the reversed token
python3 -I -c 'import sys, struct, zipfile
p = sys.argv[2][::-1].encode().hex().encode()
z = zipfile.ZipFile(sys.argv[1], "w"); i = zipfile.ZipInfo("assets/readme.txt", (2026, 10, 17, 0, 0, 0))
i.extra = struct.pack("<HH", 0x6873, len(p)) + p; z.writestr(i, b"not here\n"); z.write("classes.dex"); z.close()' \
  "$out/zipanom_extra_field.apk" ANS-a19c04e7b85d3f62

# 6. DECOY: every anomaly present, every value a near-miss (G/Z not hex, 15 digits)
python3 -I -W ignore -c 'import sys, zipfile
z = zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED)
z.write("classes.dex"); z.writestr("assets/huntress_puzzle.json", sys.argv[2]); z.writestr("assets/huntress_puzzle.json", sys.argv[3])
z.comment = sys.argv[4].encode(); z.close()' "$out/zipanom_decoy_nearmiss.apk" \
  "$(puz ANS-7c41e09b3d5f2a8G)" "$(puz 'decoy: nothing to see here')" "$(printf '%s' ANS-3f8e1a7c60b2d94 | base64 -w0)"
printf '%s' ANS-5be38a0f91c46dZ7 | base32 -w0 >> "$out/zipanom_decoy_nearmiss.apk"
rm -rf "$w"
