#!/bin/bash
# Build the jvm_unit_* fixtures (bare .class / multi-class jar WITHOUT Main-Class; the question names the unit) with
# javac/jar (JDK 21). The HCFG record (HCFG|ver|key|len16le|crc32le|xor payload) is built by python3 stdlib
# struct+zlib+base64 and stored as a >=80-char base64 String constant. usage: bash jvmunit_gen.sh
set -e
here=$(cd "$(dirname "$0")" && pwd); w=$(mktemp -d); cd "$w"
rec() { python3 -I -c 'import base64,json,struct,sys,zlib
p=json.dumps(json.loads(sys.argv[1]),separators=(",",":")).encode(); k=int(sys.argv[2])
print(base64.b64encode(b"HCFG"+bytes([1,k])+struct.pack("<HI",len(p),zlib.crc32(p))+bytes(c^k for c in p)).decode())' "$1" "$2"; }
B1=$(rec '{"campaign":"BARE-26","domain":"bare26.example.invalid","mutex":"Global\\HBARE26","url":"https://bare26.example.invalid/c"}' 90)
B2=$(rec '{"campaign":"UNIT-26","domain":"unit26.example.invalid","mutex":"Global\\HUNIT26","url":"https://unit26.example.invalid/c"}' 51)
mkdir -p s1 s2/org/hunt
cat > s1/Beacon.java <<J
public final class Beacon {
    private static final String CFG = "$B1";
    static int ticks;
    public Beacon() {}
    static String cfg() { return CFG; }
    private int beat(int n) { return n + ticks; }
    protected void sleep(long ms) { ticks++; }
    public static void main(String[] a) { System.out.println(cfg().length()); }
}
J
javac --release 11 -d s1.out s1/Beacon.java
cp s1.out/Beacon.class "$here/jvm_unit_bare_class.bin"
# 3 classes, no Main-Class; the Day-26 unit is Relay.java (Relay + Relay\$Hop share SourceFile Relay.java)
cat > s2/org/hunt/Alpha.java <<'J'
package org.hunt;
public class Alpha { public int a() { return 1; } public static void main(String[] x) {} }
J
cat > s2/org/hunt/Relay.java <<J
package org.hunt;
public class Relay {
    static final String CFG = "$B2";
    static class Hop { int h() { return 2; } }
    String route() { return CFG; }
    private static long jitter(long s) { return s ^ 7; }
    public void run() {}
}
J
cat > s2/org/hunt/Gamma.java <<'J'
package org.hunt;
class Gamma { void g() {} void g2() {} }
J
javac --release 11 -d s2.out s2/org/hunt/*.java
printf 'Created-By: huntress-fixture\n' > m.txt
(cd s2.out && jar --create --file "$w/u.jar" --manifest "$w/m.txt" org)
cp u.jar "$here/jvm_unit_jar3_nomain.bin"
# decoy: a bare class whose this_class / SourceFile name a DIFFERENT unit than the question (Beacon.java)
cat > s1/Courier.java <<'J'
public class Courier { void c() {} }
J
javac --release 11 -d s3.out s1/Courier.java
cp s3.out/Courier.class "$here/jvm_unit_decoy_other_class.bin"
rm -rf "$w"
