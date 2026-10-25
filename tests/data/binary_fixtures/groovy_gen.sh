#!/bin/bash
# Build the groovy_* fixtures with the REAL groovyc 4.0.12 (org.codehaus.groovy.tools.FileSystemCompiler in the
# groovy-4.0.12.jar Ghidra ships) + jar (JDK 21). The HCFG blob is base64 from coreutils (`base64 -w0`), never from
# lib. Groovy jar is NOT bundled (as the Scala/Clojure GM jars). usage: bash groovy_gen.sh
set -e
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../../.." && pwd)
G=$root/tools/ghidra/Ghidra/Features/GhidraServer/data/yajsw-stable-13.18/lib/extended/groovy/groovy-4.0.12.jar
w=$(mktemp -d); cd "$w"; mkdir -p s/out c/out d/out
# HCFG v1 blob: magic, ver 1, key 0x5a, len, crc32(plain) LE, xor'd JSON
json='{"c2":"https://groovy.example/beacon","id":"day26-groovy"}'
blob=$(python3 -c '
import sys, zlib, struct
j = sys.argv[1].encode(); k = 0x5a
print((b"HCFG" + bytes([1, k]) + struct.pack("<H", len(j)) + struct.pack("<I", zlib.crc32(j)) + bytes(c ^ k for c in j)).hex())' "$json" | xxd -r -p | base64 -w0)
# 1) Groovy SCRIPT: Day26Vulnerable000 extends groovy/lang/Script; closures -> Day26Vulnerable000$_run_closure1..
cat > s/Day26Vulnerable000.groovy <<S
def encodedConfig = "$blob"
def parseFrame = { byte[] b -> b.collect { it & 0xff }.sum() }
def check = { String s -> s.reverse() == "olleh" }
[1, 2, 3].each { n -> println "frame " + n }
println parseFrame("abc".bytes)
println check("hello") ? "ok" : "bad"
S
java -cp "$G" org.codehaus.groovy.tools.FileSystemCompiler -d s/out s/Day26Vulnerable000.groovy
printf 'Main-Class: Day26Vulnerable000\nCreated-By: groovyc 4.0.12\n' > s/m.txt
(cd s/out && jar --create --file "$w/script.jar" --manifest "$w/s/m.txt" .)
cp script.jar "$here/groovy_script_unit_jar.bin"
# 2) Groovy CLASS in a package with a static main + a closure inside a method (acme/Relay$_decode_closure1)
cat > c/Relay.groovy <<C
package acme
class Relay {
    static final String CFG = "$blob"
    int port = 8443
    String decode(String s) { s.toList().collect { ch -> ch.toUpperCase() }.join() }
    static void main(String[] args) { println new Relay().decode("x"); [3, 4].each { println it } }
}
C
java -cp "$G" org.codehaus.groovy.tools.FileSystemCompiler -d c/out c/Relay.groovy
printf 'Main-Class: acme.Relay\nCreated-By: groovyc 4.0.12\n' > c/m.txt
(cd c/out && jar --create --file "$w/class.jar" --manifest "$w/c/m.txt" acme)
cp class.jar "$here/groovy_class_unit_jar.bin"
# 3) DECOY: javac class with the unit's name + a fake Day26Vulnerable000$_run_closure1 (plain Java, no groovy refs)
mkdir -p d/src
cat > d/src/Day26Vulnerable000.java <<J
public class Day26Vulnerable000 { static final String CFG = "not-a-config"; public static void main(String[] a) { System.out.println(CFG); } }
class Day26Vulnerable000\$_run_closure1 { int doCall(int x) { return x + 1; } }
J
javac --release 17 -d d/out d/src/Day26Vulnerable000.java
printf 'Main-Class: Day26Vulnerable000\n' > d/m.txt
(cd d/out && jar --create --file "$w/decoy.jar" --manifest "$w/d/m.txt" .)
cp decoy.jar "$here/groovy_decoy_java_impostor_jar.bin"

rm -rf "$w"
