#!/bin/sh
# Independent oracle for the kobj_* fixtures: dex2jar's d2j-dex2jar turns classes.dex into a jar, javac builds stubs of
# the kotlin stdlib / android classes it links (Intrinsics, ULong, StringsKt.padStart, Function1,
# DefaultConstructorMarker, Context; d2j-dex2jar rewrites ULong's `-impl` refs to `_impl`, so the stub declares those), and a real JVM prints
# ReleaseKt.code(ctx) / Release.code(ctx).   usage: oracle_kobj.sh <fixture.apk>
set -e
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
unzip -q -p "$1" classes.dex > "$W/classes.dex"
sh "$ROOT/tools/dex2jar/d2j-dex2jar.sh" -f -o "$W/app.jar" "$W/classes.dex" >/dev/null 2>&1
mkdir -p "$W/s/kotlin/jvm/internal" "$W/s/kotlin/text" "$W/s/kotlin/jvm/functions" "$W/s/android/content" "$W/c"
cat > "$W/s/kotlin/jvm/internal/Intrinsics.java" <<'J'
package kotlin.jvm.internal;
public class Intrinsics {
  public static void checkNotNullParameter(Object o, String n) { if (o == null) throw new NullPointerException(n); }
  public static void checkNotNullExpressionValue(Object o, String n) { if (o == null) throw new NullPointerException(n); }
}
J
echo 'package kotlin.jvm.internal; public final class DefaultConstructorMarker {}' > "$W/s/kotlin/jvm/internal/DefaultConstructorMarker.java"
echo 'package kotlin.jvm.functions; public interface Function1<P, R> { R invoke(P p); }' > "$W/s/kotlin/jvm/functions/Function1.java"
echo 'package kotlin.text; public class StringsKt { public static String padStart(String s, int n, char c) { StringBuilder b = new StringBuilder(); for (int i = s.length(); i < n; i++) b.append(c); return b.append(s).toString(); } }' > "$W/s/kotlin/text/StringsKt.java"
echo 'package kotlin; public final class ULong { final long v; ULong(long v) { this.v = v; } public static long constructor_impl(long v) { return v; } public static ULong box_impl(long v) { return new ULong(v); } public long unbox_impl() { return v; } }' > "$W/s/kotlin/ULong.java"
echo 'package android.content; public class Context {}' > "$W/s/android/content/Context.java"
cat > "$W/s/Main.java" <<'J'
public class Main { public static void main(String[] a) throws Exception {
  for (String c : new String[]{"com.huntress.mobile.d24.kt.ReleaseKt", "com.huntress.mobile.d24.kt.Release"}) {
    try { System.out.println(Class.forName(c).getMethod("code", android.content.Context.class).invoke(null, new android.content.Context())); }
    catch (ClassNotFoundException e) { }
  } } }
J
javac -nowarn -d "$W/c" $(find "$W/s" -name '*.java') 2>/dev/null
java -cp "$W/c:$W/app.jar" Main
