#!/bin/bash
# Regenerate retrace_*.bin: javac (JDK 21, --release 11) -> R8 8.5.35 (tools/r8/r8-8.5.35.jar, Google maven) obfuscates
# and writes mapping.txt -> the obfuscated jar is RUN to produce the real obfuscated stack trace -> zip / tar pack it.
set -euo pipefail
H=$(cd "$(dirname "$0")" && pwd); J=/usr/lib/jvm/java-21-openjdk-amd64; R8=$H/../../../tools/r8/r8-8.5.35.jar
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT; cd "$W"
r8() { $J/bin/java -cp "$R8" com.android.tools.r8.R8 --classfile --release --output "$1" --pg-conf "$2" --pg-map-output "$3" --lib $J "$4"; }
# vault: line-numbered, overloaded minified name `a` with line ranges
$J/bin/javac --release 11 -g -d cv "$H"/retrace_src/vault/com/acme/vault/*.java; $J/bin/jar cf vault.jar -C cv .
printf -- '-keep class com.acme.vault.Main { public static void main(java.lang.String[]); }\n-keepattributes SourceFile,LineNumberTable\n' > v.pro
r8 app-release.jar v.pro mapping.txt vault.jar
$J/bin/java -cp app-release.jar com.acme.vault.Main 2> crash.txt || true
rm -f "$H"/retrace_r8_overload.bin; zip -X -q "$H"/retrace_r8_overload.bin crash.txt mapping.txt app-release.jar
rm -f "$H"/retrace_decoy_nomap.bin; zip -X -q "$H"/retrace_decoy_nomap.bin crash.txt app-release.jar
cp mapping.txt vault_mapping.txt; cp crash.txt vault_crash.txt
# pay: inlined frames (one minified range -> 4 original frames), logcat-prefixed trace, tar.gz with build/ path
$J/bin/javac --release 11 -g -d cp "$H"/retrace_src/pay/org/demo/pay/*.java; $J/bin/jar cf pay.jar -C cp .
printf -- '-keep class org.demo.pay.App { public static void main(java.lang.String[]); }\n-keepattributes SourceFile,LineNumberTable\n' > p.pro
mkdir -p build/outputs/mapping/release logs; r8 p.jar p.pro build/outputs/mapping/release/mapping.txt pay.jar
$J/bin/java -cp p.jar org.demo.pay.App 2> t.txt || true
{ echo "10-26 23:20:01.120  4242  4242 E AndroidRuntime: FATAL EXCEPTION: main"
  echo "10-26 23:20:01.120  4242  4242 E AndroidRuntime: Process: org.demo.pay, PID: 4242"
  sed 's/^Exception in thread "main" //; s/^/10-26 23:20:01.121  4242  4242 E AndroidRuntime: /' t.txt; } > logs/logcat.txt
tar --sort=name --mtime=@0 --owner=0 --group=0 -czf "$H"/retrace_r8_inline_logcat.bin logs/logcat.txt build/outputs/mapping/release/mapping.txt
# pay without LineNumberTable / optimisation: `a.b(SourceFile)` frames, member lines without ranges
printf -- '-keep class org.demo.pay.App { public static void main(java.lang.String[]); }\n-dontoptimize\n' > n.pro
r8 n.jar n.pro mapping.txt pay.jar; $J/bin/java -cp n.jar org.demo.pay.App 2> stacktrace.txt || true
rm -f "$H"/retrace_nolines.bin; zip -X -q "$H"/retrace_nolines.bin stacktrace.txt mapping.txt
# decoy: vault trace + the (unrelated) pay mapping -> no frame maps
rm -f "$H"/retrace_decoy_wrongmap.bin; cp vault_crash.txt crash.txt; zip -X -q "$H"/retrace_decoy_wrongmap.bin crash.txt mapping.txt
