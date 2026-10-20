#!/bin/bash
# Build the jvm_lang_* fixtures with the REAL compilers: scalac 2.11.12 (Debian scala deb), Clojure 1.12 AOT
# (clojure.lang.Compile, Debian libclojure-java), groovyc 4.0.12 (FileSystemCompiler in groovy-4.0.12.jar), jar (JDK 21).
# Jars come from `apt-get download` + `dpkg-deb -x` into tools/jvmlangs/x (no root). usage: bash jvm_lang_gen.sh
set -e
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../../.." && pwd)
J=$root/tools/jvmlangs/x/usr/share/java
G=$root/tools/ghidra/Ghidra/Features/GhidraServer/data/yajsw-stable-13.18/lib/extended/groovy/groovy-4.0.12.jar
w=$(mktemp -d); cd "$w"; mkdir -p sc/src sc/out cl/src/hello cl/out gr/out
# Scala: object + companion class -> acme/Beacon.class (static forwarders, ScalaSig) + acme/Beacon$.class (module)
cat > sc/src/Beacon.scala <<'S'
package acme
object Beacon { val key = "SEhDRg"; def main(args: Array[String]): Unit = println(decode(key)); def decode(s: String): String = s.reverse }
class Beacon(val id: Int) { def ping(): Int = id + 1 }
S
java -cp "$J/scala-compiler.jar:$J/scala-library.jar:$J/scala-reflect.jar" scala.tools.nsc.Main -usejavacp -d sc/out sc/src/Beacon.scala
printf 'Main-Class: acme.Beacon\nCreated-By: scalac 2.11.12\n' > sc/m.txt
(cd sc/out && jar --create --file "$w/scala.jar" --manifest "$w/sc/m.txt" acme)
cp scala.jar "$here/jvm_lang_scala_jar.bin"
cp 'sc/out/acme/Beacon$.class' "$here/jvm_lang_scala_module_class.bin"
# Clojure: AOT namespace with :gen-class -> hello/core.class, hello/core__init.class, hello/core$_main.class, ...
cat > cl/src/hello/core.clj <<'C'
(ns hello.core (:gen-class))
(def secret "SEhDRg")
(defn decode [s] (apply str (reverse s)))
(defn -main [& args] (println (decode secret)))
C
java -cp "$J/clojure-1.12.jar:$J/spec.alpha.jar:$J/core.specs.alpha.jar:cl/src" -Dclojure.compile.path=cl/out clojure.lang.Compile hello.core
(cd cl/out && jar --create --file "$w/clojure.jar" hello)   # app classes only, no Main-Class (library-style uberjar slice)
cp clojure.jar "$here/jvm_lang_clojure_jar.bin"
# Groovy: a class compiled by groovyc -> implements groovy/lang/GroovyObject, has $getStaticMetaClass
cat > gr/Beacon.groovy <<'R'
package acme
class Beacon {
    String key = "SEhDRg"
    String decode(String s) { s.reverse() }
    static void main(String[] args) { println new Beacon().decode("x") }
}
R
java -cp "$G" org.codehaus.groovy.tools.FileSystemCompiler -d gr/out gr/Beacon.groovy
printf 'Main-Class: acme.Beacon\n' > gr/m.txt
(cd gr/out && jar --create --file "$w/groovy.jar" --manifest "$w/gr/m.txt" acme)
cp groovy.jar "$here/jvm_lang_groovy_jar.bin"
# decoy: a renamed impostor -- a jar whose acme/Beacon.class entry is a Mach-O fat header (0xcafebabe, nfat_arch=2)
mkdir -p dc/acme
python3 -c "import struct,sys; sys.stdout.buffer.write(b'\xca\xfe\xba\xbe'+struct.pack('>I',2)+b'\0'*48)" > dc/acme/Beacon.class
(cd dc && jar --create --file "$w/decoy.jar" acme)
cp decoy.jar "$here/jvm_lang_decoy_impostor_jar.bin"
rm -rf "$w"
