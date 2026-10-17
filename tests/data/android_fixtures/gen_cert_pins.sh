#!/bin/bash
# Certificate-pinning fixtures (target cert-pin-and-nsc-facts, rows 27/28). Pins are base64 of 32 digest bytes built
# with printf/sha256sum/xxd/base64; the dex holds them as OkHttp CertificatePinner `sha256/<b64>` const-strings (smali)
# and res/xml/network_security_config.xml holds a <pin-set>; each APK is assembled by `apktool b` (smali + aapt2).
# Oracle: `unzip -p | strings` (dex) / `aapt dump xmltree` (NSC) -> `base64 -d`.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); OUT=${1:-$HERE}
pin() { (printf %s "$1"; printf %s "$2" | sha256sum | xxd -r -p | head -c $((32 - ${#1}))) | base64 -w0; }
mk() {  # name dexhost dexpin nschost nscpin
  local d; d=$(mktemp -d); mkdir -p "$d/res/xml" "$d/res/values" "$d/smali/com/huntress/pinned"
  cat > "$d/apktool.yml" <<Y
version: 3.0.3
apkFileName: $1.apk
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
  printf '<?xml version="1.0" encoding="utf-8"?>\n<resources><string name="app_name">Pinned</string></resources>\n' \
    > "$d/res/values/strings.xml"
  cat > "$d/res/xml/network_security_config.xml" <<N
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false"/>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">$4</domain>
        <pin-set expiration="2027-01-01">
            <pin digest="SHA-256">$5</pin>
            <pin digest="SHA-256">$(pin backup "$4")</pin>
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
    const-string v1, "$2"
    const/4 v2, 0x0
    aput-object v1, v0, v2
    const-string v1, "sha256/$3"
    const/4 v2, 0x1
    aput-object v1, v0, v2
    return-object v0
.end method
S
  rm -f "$OUT/$1.apk"; apktool b -q -o "$OUT/$1.apk" "$d" >/dev/null; rm -rf "$d"
}
# 1. token as the OkHttp dex pin's digest bytes; NSC pins a different host with plain digests
mk pin_dex_okhttp_b64 api.pinned-huntress.net "$(pin ANS-7c1e9a40d2b85f63 dexseed)" cdn.pinned-huntress.net "$(pin '' nscseed)"
# 2. token as an NSC <pin-set><pin digest="SHA-256"> value; the dex pin is a plain digest
mk pin_nsc_pinset_b64 api.pinned-huntress.net "$(pin '' dexseed2)" secure.pinned-huntress.net "$(pin ANS-e04b9d7a1c26f835 nscseed2)"
# 3. DECOY: same layout, plain digests in dex + NSC except a near-miss token (15 hex + 'Z') in the NSC pin
mk pin_decoy_nearmiss api.pinned-huntress.net "$(pin '' dexseed3)" secure.pinned-huntress.net "$(pin ANS-e04b9d7a1c26f83Z nscseed3)"
