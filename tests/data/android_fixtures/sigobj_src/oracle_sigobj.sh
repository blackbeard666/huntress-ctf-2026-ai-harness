#!/bin/sh
# usage: oracle_sigobj.sh <fixture.apk>  -- independent reader: jadx decompiles the apk's classes.dex back to Java,
# javac recompiles it against a stub android.content.Context, and the JVM RUNS Release.code(null), printing what it
# computes. Never touches lib.android. (jadx, not d2j-dex2jar: dex2jar writes default interface methods into
# class-file v50, which the JVM rejects.)
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/sigo.XXXX"); cd "$t"
"$root/tools/jadx/bin/jadx" -q -d j "$apk" >/dev/null 2>&1 || true
mkdir -p j/sources/android/content cls
# jadx drops the generics (jar2dex keeps no Signature): `for (T v : raw)` -> `for (Object _v : raw) { T v = (T) _v;`
find j/sources -name '*.java' -exec sed -i -E 's/for \(([A-Za-z.]+) ([a-z][A-Za-z0-9]*) : ([^;]+)\) \{/for (Object _\2 : \3) { \1 \2 = (\1) _\2;/' {} +
echo 'package android.content; public abstract class Context {}' > j/sources/android/content/Context.java
cat > j/sources/Run.java <<'J'
public class Run { public static void main(String[] a) throws Exception {
  System.out.println("code -> " + com.huntress.mobile.d25.sig.Release.code(null)); } }
J
javac -nowarn -d cls $(find j/sources -name '*.java') && java -cp cls Run
cd /; rm -rf "$t"
