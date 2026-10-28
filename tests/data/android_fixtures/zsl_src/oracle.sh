#!/bin/sh
# usage: oracle.sh <fixture.apk> <config|plugin>  -- unzip the asset, run zsl_src/Loader.java's own unpack + read on a
# desktop JVM (java.util.zip.ZipInputStream + java.io.File, same '..' / '/' / '\' semantics as Android) in a temp data
# dir, and print the ANS token(s) in the bytes the app reads (none -> the decoy reads no valid token).
set -e
here=$(cd "$(dirname "$0")" && pwd); apk=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
t=$(mktemp -d "${TMPDIR:-/tmp}/zsl.XXXXXX"); mkdir -p "$t/cls" "$t/data"
javac -d "$t/cls" "$here/Loader.java"
unzip -p "$apk" assets/bundle.zip > "$t/bundle.zip"
java -cp "$t/cls" com.huntress.mobile.d28.slip.Loader "$t/bundle.zip" "$t/data" "$2" | strings | grep -oE 'ANS-[0-9a-f]{16}' || true
rm -rf "$t"
