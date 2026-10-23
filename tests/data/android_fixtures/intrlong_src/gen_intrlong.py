#!/usr/bin/env python3
"""Generate the intrlong_* fixtures (coverage atlas row 96, dex-eval-long-intrinsics: a mixer chain that CALLS the
java.lang / java.util library instead of inlining shl/ushr pairs -- Long/Integer rotate / reverse / bitCount / nlz /
ntz / highestOneBit / signum / unsigned div+rem+compare+parse+toString, Math floorMod / floorDiv / multiplyHigh /
multiplyExact, Long.hashCode, Arrays.hashCode, String.hashCode, CRC32 / Adler32, MessageDigest SHA-256 / MD5 +
BigInteger(1, d).toString(16), String.format("%016X" / Locale.US "%08x"); no ANS-<16 hex> literal in the APK).
usage: gen_intrlong.py <variant: bits_mix | fmt_digest | decoy_runtime> <out.apk> [--oracle]
Writes Java sources, compiles with javac --release 11 (-XDstringConcat=inline: no indy), converts with dex2jar's
d2j-jar2dex, zips classes.dex + the manifest of a stock fixture with zipfile. --oracle instead RUNS Proof.token() of
the same compiled classes on the host JVM and prints it (never touches lib.android)."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
oracle = "--oracle" in sys.argv
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d24.c96;\nimport java.util.*;\nimport java.util.zip.*;\nimport java.math.BigInteger;\n" \
    "import java.security.MessageDigest;\n"
MIX = """
  static long mix(long x, int r) {
    x = Long.rotateLeft(x ^ 0x9E3779B97F4A7C15L, r);
    x = Long.reverseBytes(x) * 0xBF58476D1CE4E5B9L;
    x ^= Long.rotateRight(x, 31) + Long.bitCount(x);
    x += Long.reverse(x >>> 7) ^ Long.highestOneBit(x);
    x ^= ((long) Long.numberOfLeadingZeros(x) << 48) | ((long) Long.numberOfTrailingZeros(x | 1L << 40) << 40);
    x += Long.divideUnsigned(x, 0x1F3L) ^ Long.remainderUnsigned(x, 0x7FFFL) ^ Math.multiplyHigh(x, 0x94D049BB133111EBL);
    x ^= (long) Math.floorMod((int) x, -977) + Math.floorDiv(x, -12345L) + Long.signum(x) + Long.compareUnsigned(x, 7L);
    x += Integer.toUnsignedLong(Integer.rotateLeft((int) (x >>> 32), r) ^ Integer.reverse((int) x)
        ^ Integer.bitCount((int) x) ^ Integer.divideUnsigned((int) x, 3) ^ Integer.numberOfLeadingZeros((int) x));
    x ^= Long.hashCode(x) + Math.multiplyExact((long) (x & 0xFFFF), 31337L);
    return x;
  }
"""
SRC = {
    "bits_mix": """
public final class Proof {""" + MIX + """
  public static String token() {
    long v = Long.parseUnsignedLong("F1E2D3C4B5A69788", 16);
    for (int i = 0; i < 6; i++) v = mix(v, 7 + i * 5);
    v ^= Long.parseLong(Long.toString(v & 0xFFFFFFFFL, 36), 36) << 3;
    StringBuilder sb = new StringBuilder("ANS-");
    sb.append(String.format("%016X", v));
    return sb.toString();
  }
}
""",
    "fmt_digest": """
public final class Proof {
  public static String token() throws Exception {
    byte[] seed = "huntress-c96".getBytes("UTF-8");
    CRC32 c = new CRC32();
    c.update(seed);
    Adler32 ad = new Adler32();
    ad.update(seed, 2, 7);
    int h = Arrays.hashCode(seed) ^ "mixer".hashCode() ^ Arrays.hashCode(new long[] {c.getValue(), -5L});
    String mid = String.format(Locale.US, "%08x:%08X:%d:%s", c.getValue(), ad.getValue(), h,
        Integer.toUnsignedString(h, 7));
    MessageDigest md = MessageDigest.getInstance("SHA-256");
    byte[] d = md.digest(mid.getBytes("UTF-8"));
    MessageDigest m5 = MessageDigest.getInstance("MD5");
    m5.update(d);
    String hex = new BigInteger(1, m5.digest()).toString(16);
    return "ANS-".concat(String.format("%32s", hex).replace(' ', '0').substring(5, 21));
  }
}
""",
    # near-miss: the same library-calling mixer, but seeded at RUNTIME -- no static value to compute
    "decoy_runtime": """
public final class Proof {""" + MIX + """
  public static String token() {
    long v = new java.security.SecureRandom().nextLong() ^ System.nanoTime();
    for (int i = 0; i < 6; i++) v = mix(v, 7 + i * 5);
    return "ANS-".concat(String.format("%016X", v));
  }
}
""",
}
if variant not in SRC:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
(src / "com/huntress/mobile/d24/c96").mkdir(parents=True)
(src / "com/huntress/mobile/d24/c96/Proof.java").write_text(P + SRC[variant])
cls.mkdir()
subprocess.run(["javac", "--release", "11", "-XDstringConcat=inline", "-d", str(cls), *map(str, src.rglob("*.java"))],
               check=True)
if oracle:
    (tmp / "Run.java").write_text('public class Run { public static void main(String[] a) throws Exception {\n'
                                  '  System.out.println("token -> " + Class.forName("com.huntress.mobile.d24.c96.Proof")'
                                  '.getMethod("token").invoke(null)); } }\n')
    subprocess.run(["javac", "-cp", str(cls), "-d", str(cls), str(tmp / "Run.java")], check=True)
    subprocess.run(["java", "-cp", str(cls), "Run"], check=True)
    shutil.rmtree(tmp)
    sys.exit(0)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "mixer", "hint": "the app calls the library"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
