#!/bin/sh
# usage: oracle.sh <fixture.apk>  -- independent reader: `strings` the host classes.dex for the `<entry>:<class>` pointer
# and the contract member name, unzip that entry (a jar's classes.dex if it is a jar), d2j-dex2jar it back to JVM
# classes and READ the named member by reflection on the JVM (method call or static field). Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/mco.XXXX"); cd "$t"
unzip -p "$apk" classes.dex > host.dex
ptr=$(strings -a host.dex | grep -oE 'assets/[^: ]+:[A-Za-z_.$]+' | head -1)
entry=${ptr%%:*}; cls=${ptr#*:}
unzip -p "$apk" "$entry" > pay.bin
case "$entry" in *.jar) unzip -p pay.bin classes.dex > pay.dex ;; *) cp pay.bin pay.dex ;; esac
for x in pay host; do "$root/tools/dex2jar/d2j-dex2jar.sh" -f -o $x.jar $x.dex >/dev/null 2>&1; done
members=$(strings -a host.dex | grep -oxE '.?(moduleContract|ANSWER|CONTRACT|answer)' | grep -oE '(moduleContract|ANSWER|CONTRACT|answer)$' | sort -u | tr '\n' ' ')
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  Class<?> k = Class.forName(a[0]);
  java.util.List<String> want = new java.util.ArrayList<>(java.util.Arrays.asList(a).subList(1, a.length));
  want.add("ANSWER"); want.add("CONTRACT");
  for (String n : want) {
    try { java.lang.reflect.Method m = k.getDeclaredMethod(n); m.setAccessible(true);
      Object self = java.lang.reflect.Modifier.isStatic(m.getModifiers()) ? null : k.getDeclaredConstructor().newInstance();
      System.out.println(n + "() -> " + m.invoke(self)); } catch (NoSuchMethodException e) {}
    try { java.lang.reflect.Field f = k.getDeclaredField(n); f.setAccessible(true);
      System.out.println(n + " = " + f.get(null)); } catch (NoSuchFieldException e) {}
  } } }
J
echo "pointer: $ptr"
javac -d . Run.java && java -cp pay.jar:host.jar:. Run "$cls" $members
cd /; rm -rf "$t"
