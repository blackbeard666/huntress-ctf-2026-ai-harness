#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-dex2jar the apk's classes.dex back to JVM classes
# and RUN Proof.token() on the JVM (java), printing what it computes. Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/acso.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  System.out.println("token -> " + Class.forName("com.huntress.mobile.d20.c69.Proof").getMethod("token").invoke(null)); } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run
cd /; rm -rf "$t"
