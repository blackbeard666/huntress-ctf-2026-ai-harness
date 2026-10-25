#!/bin/bash
# SPKI cert-pin digest chain fixtures (target analysis-cert-pin-digest-chain, rows 27/28/96). Certs by `openssl req
# -x509`; pin = base64(sha256(SPKI DER)) by `openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64`;
# payload = `openssl enc -aes-256-ecb -K <spki sha256>` (1) or a python3 repeating-key XOR with the digest (2);
# NSC res/xml + smali OkHttp pin assembled by `apktool b` (aapt2 -> binary XML).
# Usage: gen_spkipin.sh <name> [OUT]   name = spkipin_nsc_der_aes | spkipin_dex_pem_xor | spkipin_decoy_wholecert
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); OUT=${2:-$HERE/..}; NAME=$1
w=$(mktemp -d); d=$w/apk; mkdir -p "$d/res/xml" "$d/res/values" "$d/res/raw" "$d/assets" "$d/smali/com/huntress/pinned"
cert() { openssl req -x509 -newkey "$2" -nodes -keyout "$w/$1.key" -subj "/CN=$1.pinned-huntress.net" -days "$3" \
           -outform der -out "$w/$1.der" 2>/dev/null; }
spki() { openssl x509 -inform der -in "$w/$1.der" -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary; }
other=$(printf 'unrelated-backup-key' | openssl dgst -sha256 -binary | base64 -w0)
dexpin=""; nscpin=$other
case $NAME in
  spkipin_nsc_der_aes)
    cert api rsa:2048 900; cp "$w/api.der" "$d/res/raw/server.der"
    nscpin2=$(spki api | base64 -w0)
    printf '{"answer":"ANS-5d0c7e93a1f42b68"}' | openssl enc -aes-256-ecb -K "$(spki api | xxd -p -c64)" | base64 -w0 > "$w/ct";;
  spkipin_dex_pem_xor)
    cert old ec:<(openssl ecparam -name prime256v1) 30; cert cur ec:<(openssl ecparam -name prime256v1) 400
    { openssl x509 -inform der -in "$w/old.der"; openssl x509 -inform der -in "$w/cur.der"; } > "$d/assets/chain.pem"
    nscpin2=$(printf 'second-unrelated' | openssl dgst -sha256 -binary | base64 -w0)
    dexpin="sha256/$(spki cur | base64 -w0)"
    python3 -c 'import sys,base64; k=bytes.fromhex(sys.argv[1]); p=b"ANS-b7e2049c6d13fa85";
print(base64.b64encode(bytes(c ^ k[i % len(k)] for i, c in enumerate(p))).decode(), end="")' \
      "$(spki cur | xxd -p -c64)" > "$w/ct";;
  spkipin_decoy_wholecert)  # near-miss: the NSC pin hashes the WHOLE cert DER, not its SPKI -> no cert matches
    cert api rsa:2048 900; cp "$w/api.der" "$d/res/raw/server.der"
    nscpin2=$(openssl dgst -sha256 -binary "$w/api.der" | base64 -w0)
    printf '{"answer":"ANS-9a41c3e07f5d2b86"}' | openssl enc -aes-256-ecb -K "$(spki api | xxd -p -c64)" | base64 -w0 > "$w/ct";;
  *) echo "unknown $NAME" >&2; exit 2;;
esac
printf '{"app":"pinned","note":"bypass the pin to read it","data":"%s"}\n' "$(cat "$w/ct")" > "$d/assets/huntress_puzzle.json"
cat > "$d/apktool.yml" <<Y
version: 3.0.3
apkFileName: $NAME.apk
usesFramework:
  ids:
  - 1
sdkInfo:
  minSdkVersion: 24
  targetSdkVersion: 33
versionInfo:
  versionCode: 1
  versionName: 1.0
Y
cat > "$d/AndroidManifest.xml" <<M
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.huntress.pinned">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application android:label="@string/app_name" android:networkSecurityConfig="@xml/network_security_config">
        <activity android:name=".MainActivity" android:exported="true"/>
    </application>
</manifest>
M
printf '<?xml version="1.0" encoding="utf-8"?>\n<resources><string name="app_name">Pinned</string></resources>\n' > "$d/res/values/strings.xml"
cat > "$d/res/xml/network_security_config.xml" <<N
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.pinned-huntress.net</domain>
        <pin-set expiration="2027-06-30">
            <pin digest="SHA-256">$nscpin</pin>
            <pin digest="SHA-256">$nscpin2</pin>
        </pin-set>
    </domain-config>
</network-security-config>
N
cat > "$d/smali/com/huntress/pinned/Pins.smali" <<S
.class public final Lcom/huntress/pinned/Pins;
.super Ljava/lang/Object;

.method public static pinner()[Ljava/lang/String;
    .registers 4
    const/4 v0, 0x2
    new-array v0, v0, [Ljava/lang/String;
    const-string v1, "api.pinned-huntress.net"
    const/4 v2, 0x0
    aput-object v1, v0, v2
    const-string v1, "${dexpin:-none}"
    const/4 v2, 0x1
    aput-object v1, v0, v2
    return-object v0
.end method
S
rm -f "$OUT/$NAME.apk"; apktool b -q -o "$OUT/$NAME.apk" "$d" >/dev/null; rm -rf "$w"
