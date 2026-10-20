#!/bin/sh
# usage: oracle.sh <fixture.apk> [-DCB_...=... for an arm64-only apk]  -- independent reader: dex2jar d2j-dex2jar the
# apk's classes.dex back to JVM classes, then RUN Bridge.nativeAnswer() on the real JVM with REAL JNI (FindClass /
# GetStaticMethodID / NewStringUTF / CallStaticObjectMethod): the apk's own lib/x86_64/libcbk.so, or, for an arm64-only
# apk, the x86_64 gcc build of the same cbk.c with the given defines (readelf -p .rodata on the shipped arm64 .so shows
# the same strings). Never touches lib.android.
set -e
apk=$(realpath "$1"); shift; here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/jcbo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
mkdir lib
if unzip -l "$apk" lib/x86_64/libcbk.so >/dev/null 2>&1; then unzip -qj "$apk" lib/x86_64/libcbk.so -d lib
else unzip -qj "$apk" 'lib/*/libcbk.so' -d arm && readelf -p .rodata arm/libcbk.so | grep '\]' >&2
     gcc -shared -fPIC -O2 -I /usr/lib/jvm/java-21-openjdk-amd64/include -I /usr/lib/jvm/java-21-openjdk-amd64/include/linux "$@" -o lib/libcbk.so "$here/cbk.c"; fi
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  System.out.println("nativeAnswer -> " + Class.forName("com.huntress.mobile.d21.Bridge").getMethod("nativeAnswer").invoke(null)); } }
J
javac -cp app.jar Run.java && java -Djava.library.path=lib -cp app.jar:. Run
cd /; rm -rf "$t"
