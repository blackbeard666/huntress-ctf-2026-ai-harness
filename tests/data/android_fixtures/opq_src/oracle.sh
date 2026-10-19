#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: dex2jar d2j-dex2jar the apk's classes.dex back to JVM classes,
# RUN ChallengeActivity.buildRequest(host, dev) on the JVM for several inputs and print the proof= value when it is a
# valid ANS- token and the same for every input (the opaque predicate's taken arm), else None.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/opqo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  Class<?> k = Class.forName("com.huntress.mobile.d20.opq.ChallengeActivity");
  java.util.Set<String> vals = new java.util.HashSet<>();
  for (String h : new String[]{"h", "host.example", "x.io"}) for (String d : new String[]{"", "p", "pixel7", "emulator-5554"}) {
    String u = (String) k.getMethod("buildRequest", String.class, String.class).invoke(k.getDeclaredConstructor().newInstance(), h, d);
    vals.add(u.substring(u.indexOf("proof=") + 6)); }
  String v = vals.size() == 1 ? vals.iterator().next() : null;
  System.out.println(v != null && v.matches("ANS-[0-9a-fA-F]{16}") ? v : "None"); } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run
cd /; rm -rf "$t"
