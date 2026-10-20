#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-dex2jar the apk's classes.dex back to JVM classes
# and RUN each app class's show(PrintStream) on the JVM, printing what the flattened state machine emits.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/fcfo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  for (String c : new String[]{"F", "G"}) {
    Class<?> k; try { k = Class.forName("com.huntress.mobile.d20.fcf." + c); } catch (ClassNotFoundException e) { continue; }
    k.getDeclaredMethod("show", java.io.PrintStream.class).invoke(k.getDeclaredConstructor().newInstance(), System.out);
  } } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run
cd /; rm -rf "$t"
