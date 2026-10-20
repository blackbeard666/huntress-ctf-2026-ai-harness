#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-dex2jar the apk's classes.dex back to JVM classes
# and RUN ChallengeActivity.onCreate on the JVM (real reflection / virtual dispatch); prints the built URL. The value
# after proof= is the answer (a 15-hex near-miss = no valid token). Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/erco.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  Class<?> c = Class.forName("com.huntress.mobile.d19.cg.ChallengeActivity"); Object o = c.newInstance();
  c.getMethod("onCreate", Object.class).invoke(o, (Object) null);
  System.out.println("url -> " + c.getField("last").get(o)); } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run
cd /; rm -rf "$t"
