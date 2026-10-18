#!/bin/bash
# resources.arsc entries reached via R.string id constants (target resource-id-const-resolve, rows 22/61). Several
# ANS-shaped strings.xml values; the dex (smali) reads exactly one by id (`const` / `const/high16` + getString /
# getStringArray) or by name (Resources.getIdentifier). Ids are pinned with res/values/public.xml; each APK is assembled
# by `apktool b` (smali + aapt2). Oracle: `aapt dump --values resources` (id -> name/value) + d2j-baksmali (const ids).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); OUT=${1:-$HERE}
mk() {  # name strings.xml-body public.xml-body smali-proof-body [values-fr body]
  local d; d=$(mktemp -d); mkdir -p "$d/res/values" "$d/smali/com/huntress/resid"
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
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.huntress.resid">
    <application android:label="@string/app_name">
        <activity android:name=".ChallengeActivity" android:exported="true"/>
    </application>
</manifest>
M
  printf '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n%s\n</resources>\n' "$2" > "$d/res/values/strings.xml"
  printf '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n%s\n</resources>\n' "$3" > "$d/res/values/public.xml"
  if [ -n "${5:-}" ]; then mkdir -p "$d/res/values-fr"
    printf '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n%s\n</resources>\n' "$5" > "$d/res/values-fr/strings.xml"; fi
  cat > "$d/smali/com/huntress/resid/ChallengeActivity.smali" <<S
.class public Lcom/huntress/resid/ChallengeActivity;
.super Landroid/app/Activity;

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V
    return-void
.end method

.method public title()Ljava/lang/String;
    .registers 2
    const/high16 v0, 0x7f0c0000
    invoke-virtual {p0, v0}, Landroid/content/Context;->getString(I)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method

.method public proof()Ljava/lang/String;
    .registers 6
$4
.end method
S
  rm -f "$OUT/$1.apk"; apktool b -q -o "$OUT/$1.apk" "$d" >/dev/null; rm -rf "$d"
}
STR='  <string name="app_name">ResId</string>
  <string name="answer_token">ANS-0f1e2d3c4b5a6978</string>
  <string name="flag">ANS-1a2b3c4d5e6f7081</string>
  <string name="s_17">ANS-9c4e17a2b5d03f68</string>
  <string name="cfg_k9">QU5TLTNlN2IxZDA1YzlhODQyZjY=</string>
  <string name="part_a">ANS-5b08e3f1a7c2d496</string>
  <string-array name="parts"><item>@string/part_a</item><item>ok</item></string-array>'
PUB='  <public type="array" name="parts" id="0x7f010000"/>
  <public type="string" name="app_name" id="0x7f0c0000"/>
  <public type="string" name="answer_token" id="0x7f0c0001"/>
  <public type="string" name="flag" id="0x7f0c0002"/>
  <public type="string" name="s_17" id="0x7f0c0003"/>
  <public type="string" name="cfg_k9" id="0x7f0c0004"/>
  <public type="string" name="part_a" id="0x7f0c0005"/>'
RET='    move-result-object v0
    return-object v0'
# 1. proof() reads R.string.s_17 by `const` id; three other ANS-shaped values (incl. names answer_token / flag) are decoys
mk resid_const_getstring "$STR" "$PUB" "    const v0, 0x7f0c0003
    invoke-virtual {p0, v0}, Landroid/content/Context;->getString(I)Ljava/lang/String;
$RET" '  <string name="app_name">ResIdFr</string>'
# 2. proof() resolves getIdentifier("cfg_k9", "string", pkg) -> a base64 value (decodes to ANS-3e7b1d05c9a842f6)
mk resid_identifier_b64 "$STR" "$PUB" "    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v0
    const-string v1, \"cfg_k9\"
    const-string v2, \"string\"
    const-string v3, \"com.huntress.resid\"
    invoke-virtual {v0, v1, v2, v3}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I
    move-result v1
    invoke-virtual {v0, v1}, Landroid/content/res/Resources;->getString(I)Ljava/lang/String;
$RET"
# 3. proof() reads R.array.parts (const/high16 0x7f010000) whose first item is @string/part_a
mk resid_array_ref "$STR" "$PUB" "    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v0
    const/high16 v1, 0x7f010000
    invoke-virtual {v0, v1}, Landroid/content/res/Resources;->getStringArray(I)[Ljava/lang/String;
    move-result-object v0
    const/4 v1, 0x0
    aget-object v0, v0, v1
    return-object v0"
# 4. DECOY: same arsc (five ANS-shaped values), proof() never touches a resource id (only title() reads app_name)
mk resid_decoy_unreferenced "$STR" "$PUB" "    const-string v0, \"pending\"
    return-object v0"
