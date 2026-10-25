#!/bin/sh
# usage: oracle.sh <bundle.zip>  -- independent reader: unzip the bundle's set01.apk, dex2jar d2j-dex2jar its
# classes.dex back to JVM classes and RUN Rng.code() on the JVM (real java.util.Random / SplittableRandom / UUID).
set -e
b=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/dxro.XXXX"); cd "$t"
unzip -q -o "$b" set01.apk
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar set01.apk >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  System.out.println(Class.forName("com.huntress.mobile.d26.rnd.Rng").getMethod("code").invoke(null)); } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run
cd /; rm -rf "$t"
