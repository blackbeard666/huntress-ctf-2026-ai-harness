#!/bin/sh
# Independent oracle (row 107 multidex fixtures): every classesN.dex of the APK -> jar with dex2jar, then the JVM runs
# com.hctf.mdx.Challenge with the jars on the classpath in numeric dex order (first definition wins, as in ART).
# Usage: sh oracle.sh <apk>
set -e
D2J="$(dirname "$(realpath "$0")")/../../../../tools/dex2jar/d2j-dex2jar.sh"
APK=$(realpath "$1"); D=$(mktemp -d); cd "$D"
unzip -q "$APK" 'classes*.dex'
CP=""
for n in $(ls classes*.dex | sed -e 's/^classes\.dex$/1/' -e 's/classes\([0-9]*\)\.dex/\1/' | sort -n); do
  f="classes$n.dex"; [ "$n" = 1 ] && f=classes.dex
  sh "$D2J" -f -o "c$n.jar" "$f" >/dev/null 2>&1
  CP="$CP${CP:+:}c$n.jar"
done
echo "classpath: $CP"
java -cp "$CP" com.hctf.mdx.Challenge
