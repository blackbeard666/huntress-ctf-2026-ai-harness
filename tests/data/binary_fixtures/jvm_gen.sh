#!/bin/bash
# Build the jvm_* ClassFile fixtures with javac/jar (JDK 21). usage: bash jvm_gen.sh   (writes jvm_*.bin here)
set -e
here=$(cd "$(dirname "$0")" && pwd); w=$(mktemp -d); cd "$w"
mkdir -p a/com/acme b/kotlin c/pkg
cat > a/com/acme/Main.java <<'J'
package com.acme;
public final class Main implements Runnable, java.io.Serializable {
    private static final String KEY = "SEhDRkcxMjM0";
    static int counter;
    private final long stamp = 7L;
    double ratio;
    static { counter = 3; }
    public Main() {}
    public void run() { counter++; }
    private static String decodeConfig(String s) { return new StringBuilder(s).reverse().toString(); }
    protected int evaluate(int a, long b) { return (int) (a + b); }
    public static void main(String[] args) { System.out.println(decodeConfig(KEY)); }
}
J
cat > a/com/acme/Helper.java <<'J'
package com.acme;
class Helper { int h() { return 1; } }
J
javac --release 11 -d a.out a/com/acme/*.java
printf 'Main-Class: com.acme.Main\nCreated-By: huntress-fixture\n' > m.txt
(cd a.out && jar --create --file "$w/main.jar" --manifest "$w/m.txt" com)
cp main.jar "$here/jvm_jar_java_main.bin"
# Kotlin @Metadata without kotlinc: a stand-in kotlin.Metadata annotation (same element names/encoding)
cat > b/kotlin/Metadata.java <<'J'
package kotlin;
import java.lang.annotation.*;
@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.TYPE)
public @interface Metadata { int k() default 1; int[] mv() default {}; String[] d1() default {}; String[] d2() default {}; int xi() default 0; }
J
cat > b/Box.java <<'J'
@kotlin.Metadata(k = 1, mv = {1, 9, 0}, d1 = {"\u0000\u0010\n\u0002\u0018\u0002"}, d2 = {"LBox;", "", "<init>", "()V", "value", "invokeSuspend"}, xi = 48)
public abstract class Box<T> implements Comparable<Box<T>> {
    protected T value;
    public abstract Object invokeSuspend(Object r);
    public int compareTo(Box<T> o) { return 0; }
}
J
javac --release 17 -d b.out b/kotlin/Metadata.java b/Box.java
cp b.out/Box.class "$here/jvm_class_kotlin_meta.bin"
# decoy 1: Mach-O universal header (0xcafebabe, nfat_arch=2) -- not a class file
python3 -c "import struct,sys; sys.stdout.buffer.write(b'\xca\xfe\xba\xbe'+struct.pack('>I',2)+struct.pack('>5I',7,3,4096,64,12)+struct.pack('>5I',0x01000007,3,8192,64,12)+b'\0'*64)" > "$here/jvm_decoy_macho_fat.bin"
# decoy 2: a jar without Main-Class (library jar): jar facts present, class facts absent
cat > c/pkg/Lib.java <<'J'
package pkg;
public class Lib { public static int one() { return 1; } }
J
javac --release 11 -d c.out c/pkg/Lib.java
(cd c.out && jar --create --file "$w/lib.jar" pkg)
cp lib.jar "$here/jvm_decoy_jar_nomain.bin"
rm -rf "$w"
