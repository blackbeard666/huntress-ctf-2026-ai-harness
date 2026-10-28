#!/bin/sh
# usage: oracle.sh <fixture.apk> <fqcn>  -- independent reader: unzip the asset jar (or aar -> classes.jar), print the
# constants with `javap -constants`, and RUN every public static String no-arg method of <fqcn> on the JVM.
set -e
apk=$(realpath "$1"); t=$(mktemp -d "${TMPDIR:-/tmp}/jvmcf.XXXX"); cd "$t"
for a in $(unzip -Z1 "$apk" 'assets/*'); do unzip -p "$apk" "$a" > x.zip
  case "$a" in *.aar) unzip -p x.zip classes.jar > lib.jar;; *) cp x.zip lib.jar;; esac; done
javap -constants -cp lib.jar "$2" | grep -E 'String|ANS' || true
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  for (java.lang.reflect.Method m : Class.forName(a[0]).getDeclaredMethods())
    if (java.lang.reflect.Modifier.isStatic(m.getModifiers()) && m.getParameterCount() == 0 && m.getReturnType() == String.class) {
      m.setAccessible(true); System.out.println(m.getName() + "() -> " + m.invoke(null)); } } }
J
javac -d . Run.java && java -cp lib.jar:. Run "$2"
cd /; rm -rf "$t"
