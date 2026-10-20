#!/bin/sh
# usage: oracle.sh <fixture.apk>  -- independent reader: the KEY comes from `aapt dump xmltree` (intent-filter pathPrefix
# last segment) or python json over assets/huntress_puzzle.json (dispatch.route / entry); dex2jar d2j-dex2jar turns the
# apk's classes.dex back into JVM classes and the JVM RUNS the real dispatcher with that key. Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/dspo.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
pj=$(unzip -p "$apk" assets/huntress_puzzle.json)
route=$(printf '%s' "$pj" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("dispatch",{}).get("route",""))')
entry=$(printf '%s' "$pj" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("entry",""))')
seg=$(aapt dump xmltree "$apk" AndroidManifest.xml | sed -n 's/.*pathPrefix[^=]*="\([^"]*\)".*/\1/p' | sed 's#.*/##')
echo "manifest pathPrefix segment=$seg puzzle route=$route entry=$entry"
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  String P = "com.huntress.mobile.d19.dispatch.";
  if (!a[1].isEmpty()) { System.out.println("Dispatcher.handle(" + a[1] + ") -> " + Class.forName(P + "Dispatcher").getMethod("handle", String.class).invoke(Class.forName(P + "Dispatcher").newInstance(), a[1])); return; }
  if (!a[2].isEmpty()) { System.out.println("Picker.pick(" + a[2] + ") -> " + Class.forName(P + "Picker").getMethod("pick", int.class).invoke(null, Integer.parseInt(a[2]))); return; }
  System.out.println("Router.dispatch(" + a[0] + ") -> " + Class.forName(P + "Router").getMethod("dispatch", String.class).invoke(null, a[0])); } }
J
javac -cp app.jar Run.java && java -cp app.jar:. Run "$seg" "$route" "$entry"
cd /; rm -rf "$t"
