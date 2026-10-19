#!/bin/sh
# Java serialization stream fixtures (coverage atlas row 73). Writer = the JDK's ObjectOutputStream (Gen.java);
# dex = javac --release 8 + dex2jar d2j-jar2dex; APK = Info-ZIP `zip -X`. Oracle = the JDK's ObjectInputStream (Read.java).
# usage: sh gen_jser.sh <mode: session|map|array|decoy> <token> <out.apk>
set -e
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../../../.." && pwd)
mode=$1; tok=$2; out=$(realpath -m "$3"); tmp=$(mktemp -d)
mkdir -p "$tmp/src/com/example/vault" "$tmp/cls" "$tmp/apk/assets" "$tmp/apk/res/raw"
cp "$here/com/example/vault/Session.java" "$tmp/src/com/example/vault/"
javac --release 11 -d "$tmp/gen" "$here/Gen.java" "$here/com/example/vault/Session.java"
case $mode in
  session) java -cp "$tmp/gen" Gen session "$tok" "$tmp/apk/assets/session.ser" ;;
  decoy)   java -cp "$tmp/gen" Gen session "$tok" "$tmp/apk/assets/session.ser" ;;
  map)     java -cp "$tmp/gen" Gen map "$tok" "$tmp/apk/res/raw/state.txt" ;;
  array)   java -cp "$tmp/gen" Gen array "$tok" "$tmp/src/com/example/vault/Holder.java" ;;
esac
javac --release 8 -d "$tmp/cls" $(find "$tmp/src" -name '*.java')
(cd "$tmp/cls" && zip -q -r -X ../classes.zip .)
"$root/tools/dex2jar/d2j-jar2dex.sh" -f -o "$tmp/apk/classes.dex" "$tmp/classes.zip" >/dev/null 2>&1
printf 'manifest-placeholder' > "$tmp/apk/AndroidManifest.xml"
rm -f "$out"; (cd "$tmp/apk" && zip -q -r -X "$out" AndroidManifest.xml classes.dex assets res)
rm -rf "$tmp"
