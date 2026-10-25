#!/bin/bash
# Build the scalamod_* fixtures (Scala forwarder vs `$` module, Scala 3 TASTy, indy lambdas) with REAL writers:
# scalac 2.11.12 (tools/jvmlangs, Debian deb), javac/jar (JDK 21), ASM via groovy-4.0.12.jar (scalamod_Tasty3.java).
# usage: bash scalamod_gen.sh
set -e
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../../.." && pwd)
J=$root/tools/jvmlangs/x/usr/share/java
G=$root/tools/ghidra/Ghidra/Features/GhidraServer/data/yajsw-stable-13.18/lib/extended/groovy/groovy-4.0.12.jar
w=$(mktemp -d); cd "$w"; mkdir -p s2 jv t3 asm d1 d2
# 1) D24-shaped scalac object: Day24Vulnerable000.class (forwarder, Main-Class) + Day24Vulnerable000$.class (module)
cat > Day24Vulnerable000.scala <<'S'
object Day24Vulnerable000 {
  def encodedConfig: String = "SEhDRgEAAAA="
  def decodeConfig(s: String): Array[Byte] = java.util.Base64.getDecoder.decode(s)
  def score(xs: Array[Byte]): Int = xs.map(b => b & 0xff).sum
  def main(args: Array[String]): Unit = println(score(decodeConfig(encodedConfig)))
}
S
java -cp "$J/scala-compiler.jar:$J/scala-library.jar:$J/scala-reflect.jar" scala.tools.nsc.Main -usejavacp -d s2 Day24Vulnerable000.scala
printf 'Main-Class: Day24Vulnerable000\n' > m1.txt
(cd s2 && jar --create --file "$w/s2.jar" --manifest "$w/m1.txt" .)
cp s2.jar "$here/scalamod_s211_object_jar.bin"
# 2) javac lambdas: invokedynamic + BootstrapMethods (LambdaMetafactory + StringConcatFactory), synthetic lambda$ methods
cat > Beacon.java <<'JV'
import java.util.function.*;
public class Beacon {
    public static void main(String[] a) {
        Function<String, Integer> f = s -> s.length();
        Supplier<String> g = () -> "SEhDRg";
        System.out.println("n=" + f.apply(g.get()));
    }
}
JV
javac --release 11 -d jv Beacon.java
printf 'Main-Class: Beacon\n' > m2.txt
(cd jv && jar --create --file "$w/jv.jar" --manifest "$w/m2.txt" .)
cp jv.jar "$here/scalamod_javac_lambda_jar.bin"
# 3) Scala-3-shaped jar: ASM-written Hello.class (TASTY attr) + Hello$.class (module) + Hello.tasty entry
javac -cp "$G" -d asm "$here/scalamod_Tasty3.java"
java -cp "$G:asm" scalamod_Tasty3 t3
printf 'Main-Class: Hello\n' > m3.txt
(cd t3 && jar --create --file "$w/t3.jar" --manifest "$w/m3.txt" .)
cp t3.jar "$here/scalamod_scala3_tasty_jar.bin"
# 4) decoy: Main-Class X whose X$.class is a plain javac class (no MODULE$) -> no forwarder/module, no Scala
printf 'public class X { public static void main(String[] a) {} }\n' > X.java
printf 'public class X$ { int y; }\n' > 'X$.java'
javac --release 11 -d d1 X.java 'X$.java'
printf 'Main-Class: X\n' > m4.txt
(cd d1 && jar --create --file "$w/d1.jar" --manifest "$w/m4.txt" .)
cp d1.jar "$here/scalamod_decoy_dollar_not_module_jar.bin"
# 5) decoy: Main-Class Day24Vulnerable000 but its classfiles are text impostors (renamed .scala source)
cp Day24Vulnerable000.scala 'd2/Day24Vulnerable000$.class'; cp Day24Vulnerable000.scala d2/Day24Vulnerable000.class
(cd d2 && jar --create --file "$w/d2.jar" --manifest "$w/m1.txt" .)
cp d2.jar "$here/scalamod_decoy_text_impostor_jar.bin"
rm -rf "$w"
