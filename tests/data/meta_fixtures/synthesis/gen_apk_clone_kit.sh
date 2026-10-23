#!/bin/sh
# Builds the APK clone/rebuild fixture kits with aapt2 (link against a stub 'android' framework declaring the public
# android.R.attr ids), keytool (3 RSA signers), apksigner (v1+v2+v3) and zip.  usage: gen_apk_clone_kit.sh <workdir> <outdir>
set -e
W=$1; OUT=$2; mkdir -p "$W/fw/res/values" "$OUT"; cd "$W"
cat > fw/res/values/attrs.xml <<'X'
<resources>
  <attr name="label" format="string|reference"/><attr name="name" format="string"/>
  <attr name="versionCode" format="integer"/><attr name="versionName" format="string"/>
  <attr name="minSdkVersion" format="integer|string"/>
  <public type="attr" name="label" id="0x01010001"/><public type="attr" name="name" id="0x01010003"/>
  <public type="attr" name="versionCode" id="0x0101021b"/><public type="attr" name="versionName" id="0x0101021c"/>
  <public type="attr" name="minSdkVersion" id="0x0101020c"/>
</resources>
X
echo '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="android"/>' > fw/AndroidManifest.xml
aapt2 compile --dir fw/res -o fw/res.zip && aapt2 link --manifest fw/AndroidManifest.xml -o fw.apk fw/res.zip
for k in alpha bravo charlie; do
  [ -f $k.jks ] || keytool -genkeypair -keystore $k.jks -alias $k -keyalg RSA -keysize 2048 -validity 10000 \
    -dname "CN=$k signer, O=Fixture" -storepass pass123 -keypass pass123 >/dev/null 2>&1
done
# mk <out.apk> <package> <versionCode> <label> <key> <inline|res> [extra-asset-text]
mk() {
  d=build/$1; rm -rf $d; mkdir -p $d/res/values $d/assets
  if [ "$6" = res ]; then L='@string/app_name'; else L="$4"; fi
  printf '<resources><string name="app_name">%s</string></resources>\n' "$4" > $d/res/values/strings.xml
  cat > $d/AndroidManifest.xml <<X
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="$2" android:versionCode="$3" android:versionName="1.$3">
  <uses-sdk android:minSdkVersion="21"/>
  <application android:label="$L"/>
</manifest>
X
  [ -n "$7" ] && echo "$7" > $d/assets/build.txt
  aapt2 compile --dir $d/res -o $d/res.zip
  if [ -n "$7" ]; then A="-A $d/assets"; else A=""; fi
  aapt2 link -I fw.apk --manifest $d/AndroidManifest.xml $A -o $d/u.apk $d/res.zip
  apksigner sign --ks $5.jks --ks-pass pass:pass123 --v1-signing-enabled true --v2-signing-enabled true \
    --v3-signing-enabled true --min-sdk-version 21 --out "$KIT/$1" $d/u.apk
  rm -f "$KIT/$1.idsig"
}
KIT=kit_a; rm -rf $KIT; mkdir -p $KIT
mk bank-v10.apk com.acme.bank 10 "Acme Bank" alpha res
mk bank-v11.apk com.acme.bank 11 "Acme Bank" alpha res
mk bank-v12-mod.apk com.acme.bank 12 "Acme Bank" bravo res
mk wallet-v3.apk com.acme.wallet 3 "Acme Wallet" alpha inline
mk acme-bank-lite.apk com.acrne.bank 1 "Acme Bank" charlie inline
echo "release notes" > $KIT/readme.txt; echo "not an apk" > $KIT/notes.apk
KIT=kit_b; rm -rf $KIT; mkdir -p $KIT
mk chat-a.apk org.talk.chat 7 "Talk" alpha res "build A"
mk chat-b.apk org.talk.chat 7 "Talk" alpha res "build B"
mk chat-c.apk org.talk.chat 9 "Talk" alpha res
mk maps.apk org.talk.maps 7 "Talk Maps" bravo inline
KIT=kit_decoy; rm -rf $KIT; mkdir -p $KIT
echo "not an apk" > $KIT/fake.apk; printf 'PK\003\004 truncated' > $KIT/broken.apk; echo hi > $KIT/readme.txt
for k in kit_a kit_b kit_decoy; do rm -f "$OUT/$k.zip"; (cd $k && zip -q -X "$OUT/$k.zip" $(ls)); done
