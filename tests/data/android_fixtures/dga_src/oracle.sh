#!/bin/sh
# usage: oracle.sh <fixture.apk>   -- independent reader: aapt2 reads the manifest package name, dex2jar d2j-dex2jar
# turns the apk's classes.dex back into JVM classes, and Proof.token(ctx) RUNS on the JVM with a Context stub whose
# getPackageName() returns that package. Prints what the app computes. Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
pkg=$(aapt2 dump xmltree --file AndroidManifest.xml "$apk" | sed -n 's/.* package="\([^"]*\)".*/\1/p' | head -1)
t=$(mktemp -d "${TMPDIR:-/tmp}/dgao.XXXX"); cd "$t"
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
mkdir -p android/content
echo 'package android.content; public abstract class Context { public abstract String getPackageName(); }' > android/content/Context.java
cat > Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  android.content.Context c = new android.content.Context() { public String getPackageName() { return a[0]; } };
  System.out.println("token -> " + Class.forName("com.huntress.mobile.d21.c33.Proof")
      .getMethod("token", android.content.Context.class).invoke(null, c)); } }
J
javac -cp app.jar -d . android/content/Context.java Run.java && java -cp app.jar:. Run "$pkg"
cd /; rm -rf "$t"
