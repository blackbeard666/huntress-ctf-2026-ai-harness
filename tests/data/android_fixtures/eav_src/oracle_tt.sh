#!/bin/sh
# Oracle for eav_d23tt_nopuzzle.apk: jadx-decompile it, compile the jadx Java of Release + its callees against a stub
# android.content.Context, and print Release.code(null) on the host JVM.  usage: oracle_tt.sh <apk>
set -e
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
jadx -q -d "$T/jx" "$1" >/dev/null 2>&1 || true
mkdir -p "$T/src/android/content"; echo 'package android.content; public class Context { }' > "$T/src/android/content/Context.java"
D=$(dirname "$(grep -rl 'public final class Release' "$T/jx/sources")")
P=$(sed -n 's/^package \(.*\);/\1/p' "$D/Release.java")
for c in Release Util Mix HookScan Probe HookLineAndSignal; do cp "$D/$c.java" "$T/src/"; done
printf 'public class O { public static void main(String[] a) { System.out.println(%s.Release.code(null)); } }\n' "$P" > "$T/src/O.java"
mkdir -p "$T/cls"; javac -nowarn -d "$T/cls" $(find "$T/src" -name '*.java') 2>/dev/null
java -cp "$T/cls" O
