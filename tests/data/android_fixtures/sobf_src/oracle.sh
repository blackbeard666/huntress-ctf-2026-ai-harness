#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-dex2jar the apk's classes.dex back to JVM classes
# and RUN Main.show(PrintStream) on the JVM (the obfuscator's own runtime decrypts), printing its output.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/sobfo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  Class<?> k = Class.forName("com.huntress.mobile.d21.sf.Main");
  k.getDeclaredMethod("show", java.io.PrintStream.class).invoke(k.getDeclaredConstructor().newInstance(), System.out);
} }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run
cd /; rm -rf "$t"
