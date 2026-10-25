#!/bin/sh
# usage: oracle.sh <fixture.apk> [-D... defines for the host build]  -- independent reader: dex2jar d2j-dex2jar the
# apk's classes.dex back to JVM classes, then RUN com.huntress.mobile.d24.Release.code() on the real JVM with REAL JNI:
# the apk's own lib/x86_64/libarena.so, or, for an arm64-only apk, the host x86_64 gcc build of nlbx.c with the given
# defines (the JVM binds RegisterNatives via JNI_OnLoad itself). Never touches lib.android.
set -e
apk=$(realpath "$1"); shift; here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/nlbxo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
mkdir lib
if unzip -l "$apk" lib/x86_64/libarena.so >/dev/null 2>&1; then unzip -qj "$apk" lib/x86_64/libarena.so -d lib
else gcc -shared -fPIC -O2 -I /usr/lib/jvm/java-21-openjdk-amd64/include -I /usr/lib/jvm/java-21-openjdk-amd64/include/linux "$@" -o lib/libarena.so "$here/nlbx.c"; fi
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  System.out.println("Release.code() -> " + Class.forName("com.huntress.mobile.d24.Release").getMethod("code").invoke(null)); } }
J
javac -cp app.jar Run.java && java -Djava.library.path=lib -cp app.jar:. Run
cd /; rm -rf "$t"
