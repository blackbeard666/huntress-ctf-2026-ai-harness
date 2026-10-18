#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-dex2jar the apk's classes.dex back to JVM classes
# and RUN the app's method on the JVM (java), printing what it computes. Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/dxeo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  for (String c : new String[]{"Vault", "Cfg"}) {
    Class<?> k; try { k = Class.forName("com.huntress.mobile.d19.q4e." + c); } catch (ClassNotFoundException e) { continue; }
    for (java.lang.reflect.Method m : k.getDeclaredMethods()) {
      if (m.getReturnType() != String.class) continue; m.setAccessible(true);
      Object[] args = new Object[m.getParameterCount()]; java.util.Arrays.fill(args, "");
      Object self = java.lang.reflect.Modifier.isStatic(m.getModifiers()) ? null : k.getDeclaredConstructor().newInstance();
      if (m.getParameterCount() == 0 || m.getParameterTypes()[0] == String.class) System.out.println(m.getName() + " -> " + m.invoke(self, args));
    } } } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run
cd /; rm -rf "$t"
