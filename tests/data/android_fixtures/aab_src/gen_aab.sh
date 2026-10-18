#!/bin/bash
# AAB fixtures (coverage atlas row 58): protobuf manifests from aapt2 `link --proto-format` (apktool's bundled aapt2
# 2.20 + its prebuilt android-framework.jar as -I), laid out as a bundle with python zipfile:
#   BundleConfig.pb, base/manifest/AndroidManifest.xml, base/resources.pb, base/assets/..., <feature>/manifest/...
# usage: gen_aab.sh <out_dir>
set -euo pipefail
OUT=$(realpath "$1"); SRC=$(dirname "$(realpath "$0")"); W=$(mktemp -d "${TMPDIR:-/tmp}/aabgen.XXXX")
unzip -o -q -j /usr/local/bin/apktool.jar prebuilt/linux/aapt2 prebuilt/android-framework.jar -d "$W"
chmod +x "$W/aapt2"; A2="$W/aapt2"; FW="$W/android-framework.jar"
mkdir -p "$W/res/values"; echo '<resources><string name="app_name">Bundle</string></resources>' > "$W/res/values/strings.xml"
"$A2" compile --dir "$W/res" -o "$W/res.zip"
man() {  # man <name> <package> <application body> -> $W/<name>.zip (AndroidManifest.xml proto + resources.pb)
  cat > "$W/$1.xml" <<XML
<manifest xmlns:android="http://schemas.android.com/apk/res/android" xmlns:dist="http://schemas.android.com/apk/distribution" package="$2" android:versionCode="7" android:versionName="1.7">
  <uses-permission android:name="android.permission.INTERNET"/>
  <application android:label="@string/app_name" android:allowBackup="false">$3</application>
</manifest>
XML
  "$A2" link --proto-format -I "$FW" --manifest "$W/$1.xml" -o "$W/$1.zip" "$W/res.zip"
}
bundle() {  # bundle <out.zip> <base manifest zip> [feature=<zip>] [asset:<path>=<file>]...
  python3 - "$@" <<'PY'
import sys, zipfile
out, base, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("BundleConfig.pb", b"\x0a\x08\x0a\x061.17.2")  # BundleConfig{bundletool{version}}
    with zipfile.ZipFile(base) as b:
        z.writestr("base/manifest/AndroidManifest.xml", b.read("AndroidManifest.xml"))
        z.writestr("base/resources.pb", b.read("resources.pb"))
    for e in extra:
        k, v = e.split("=", 1)
        if k.startswith("asset:"):
            z.write(v, "base/assets/" + k[6:])
        else:
            with zipfile.ZipFile(v) as f:
                z.writestr(k + "/manifest/AndroidManifest.xml", f.read("AndroidManifest.xml"))
PY
}
APP='<activity android:name=".MainActivity" android:exported="true"><intent-filter><action android:name="android.intent.action.VIEW"/><category android:name="android.intent.category.BROWSABLE"/><data android:scheme="huntress" android:host="proof"/></intent-filter></activity><service android:name=".SyncService" android:exported="false"/>'
# 1) application <meta-data android:value> = base64(token)
man m1 com.huntress.bundle "<meta-data android:name=\"com.huntress.PROOF\" android:value=\"$(printf 'ANS-3f9a0c7e21d4b685' | base64)\"/>$APP"
bundle "$OUT/aab_meta_b64.zip" "$W/m1.zip"
# 2) feature module activity meta-data = hex(token); base manifest clean
man m2b com.huntress.bundle "$APP"
man m2f com.huntress.bundle.dynfeature "<activity android:name=\".ProofActivity\" android:exported=\"false\"><meta-data android:name=\"proof\" android:value=\"$(printf 'ANS-c40e9b17a2d58f63' | xxd -p | tr -d '\n')\"/></activity>"
bundle "$OUT/aab_feature_hex.zip" "$W/m2b.zip" "dynfeature=$W/m2f.zip"
# 3) token only in base/assets/www/app.js as a String.fromCharCode list (reached by the base-module re-layout)
mkdir -p "$W/www"; python3 -c "import sys; print('var p = String.fromCharCode(' + ','.join(str(ord(c)) for c in 'ANS-9be4271d0c6af358') + ');')" > "$W/www/app.js"
echo '<html><body><script src="app.js"></script></body></html>' > "$W/www/index.html"
bundle "$OUT/aab_asset_js.zip" "$W/m2b.zip" "asset:www/app.js=$W/www/app.js" "asset:www/index.html=$W/www/index.html"
# 4) DECOY: same layout, near-miss tokens only (15 hex digits; 'g' in the hex) in meta-data and asset js
man m4 com.huntress.bundle "<meta-data android:name=\"com.huntress.PROOF\" android:value=\"$(printf 'ANS-3f9a0c7e21d4b68' | base64)\"/>$APP"
python3 -c "print('var p = String.fromCharCode(' + ','.join(str(ord(c)) for c in 'ANS-9be4271d0c6ag358') + ');')" > "$W/www/app.js"
bundle "$OUT/aab_decoy_nearmiss.zip" "$W/m4.zip" "asset:www/app.js=$W/www/app.js"
rm -rf "$W"
