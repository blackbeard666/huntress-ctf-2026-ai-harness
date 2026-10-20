#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-dex2jar the apk's classes.dex back to JVM classes
# and RUN the app's entry points (Vault.token() / Gate.show()) on the JVM, printing what the VM computes.
# Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/vmbo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  for (String[] cm : new String[][]{{"Vault", "token"}, {"Gate", "show"}}) {
    Class<?> k; try { k = Class.forName("com.huntress.mobile.d20.vm." + cm[0]); } catch (ClassNotFoundException e) { continue; }
    System.out.println(cm[0] + "." + cm[1] + " -> " + k.getDeclaredMethod(cm[1]).invoke(null));
  } } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run 2>/dev/null
cd /; rm -rf "$t"
