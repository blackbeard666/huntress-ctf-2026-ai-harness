#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-dex2jar the apk's classes.dex back to JVM classes
# and RUN each app class's show(PrintStream) on the JVM (twice for the runtime-indexed variant), printing its output.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/dcallo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  for (String c : new String[]{"A", "Main", "Z"}) {
    Class<?> k; try { k = Class.forName("com.huntress.mobile.d20.dc." + c); } catch (ClassNotFoundException e) { continue; }
    java.lang.reflect.Method m = k.getDeclaredMethod("show", java.io.PrintStream.class);
    for (int i = 0; i < 2; i++) m.invoke(k.getDeclaredConstructor().newInstance(), new java.io.PrintStream(System.out) {
      int h = 0; @Override public int hashCode() { return h++; } });
  } } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run
cd /; rm -rf "$t"
