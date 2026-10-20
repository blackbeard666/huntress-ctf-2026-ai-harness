#!/bin/sh
# usage: oracle.sh <fixture.apk>  -- independent reader: unzip the host classes*.dex and the asset payload (a bare dex,
# or a jar's classes.dex), d2j-dex2jar each back to JVM classes, and RUN the host's own Main.run(<payload jar>) on the
# JVM with a runtime dalvik.system.DexClassLoader = URLClassLoader(payload, parent). The JVM's real delegation (parent-
# first ClassLoader.loadClass, the host ChildFirstLoader override, a null = bootstrap parent) picks which Gate runs and
# prints its token(). Never touches lib.android.
set -e
apk=$(realpath "$1"); root=$(realpath "$(dirname "$(realpath "$0")")/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/clso.XXXX"); cd "$t"
d2j() { "$root/tools/dex2jar/d2j-dex2jar.sh" -f -o "$2" "$1" >/dev/null 2>&1; }
cp=""
for n in $(unzip -Z1 "$apk" | grep -E '^classes[0-9]*\.dex$'); do unzip -p "$apk" "$n" > "$n"; d2j "$n" "$n.jar"; cp="$cp:$t/$n.jar"; done
entry=$(unzip -Z1 "$apk" | grep -E '^assets/.*\.(dex|jar)$' | head -1)
unzip -p "$apk" "$entry" > pay.bin
case "$entry" in *.jar) unzip -p pay.bin classes.dex > pay.dex ;; *) cp pay.bin pay.dex ;; esac
d2j pay.dex pay.jar
mkdir -p rt/dalvik/system
cat > rt/dalvik/system/DexClassLoader.java <<'J'
package dalvik.system;
public class DexClassLoader extends java.net.URLClassLoader {
  static java.net.URL[] u(String p) { try { return new java.net.URL[]{new java.io.File(p).toURI().toURL()}; } catch (Exception e) { throw new RuntimeException(e); } }
  public DexClassLoader(String dexPath, String o, String l, ClassLoader parent) { super(u(dexPath), parent); }
}
J
cat > rt/Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  Object r = Class.forName("com.huntress.arena.Main").getMethod("run", String.class).invoke(null, a[0]);
  System.out.println("payload " + a[1] + " -> Gate.token() = " + r); } }
J
javac -nowarn -d rt rt/dalvik/system/DexClassLoader.java rt/Run.java 2>/dev/null
java -cp "rt$cp" Run "$t/pay.jar" "$entry"
cd /; rm -rf "$t"
