#!/usr/bin/env python3
"""Generate the strdec_* fixtures (coverage atlas rows 35/43/70/100: a D18 "Encrypted Strings" v2 chain -- the app
decrypts its own byte[]/char[] strings with decryptByte(b, i) (b ^ k ^ i, (b - k) & 0xff, key array cycled), builds
String(bytes, StandardCharsets.* | charset name | Charset.forName), String.valueOf(char[]), toCharArray, getBytes,
intern, String.format, and feeds the names to Class.forName + getDeclaredMethod / getDeclaredField (D25 reflection) and
the `0123456789ABCDEF` table to a hex formatter; sibling members hold decoy / near-miss values).
usage: gen_strdec.py <variant: xor_method | sub_field | decoy_nearmiss> <out.apk>
javac --release 8 -> dex2jar d2j-jar2dex -> zipfile. The oracle (oracle.sh) RUNS the same dex on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d18.enc"
P = f"package {PKG};\n"
K = [0x93, 0x37, 0xC5, 0x7F, 0xA9]  # key array, cycled; >= 0x80 entries force byte sign extension


def sb(v):
    v &= 0xFF
    return str(v - 256 if v >= 128 else v)


def enc_xor(s):  # decryptByte: b ^ k[i % n] ^ i
    return ", ".join(sb(c ^ K[i % len(K)] ^ i) for i, c in enumerate(s.encode()))


def enc_sub(s):  # decryptByte: (b - k[i % n]) & 0xff
    return ", ".join(sb(c + K[i % len(K)]) for i, c in enumerate(s.encode("latin-1")))


def enc_chr(s, k):  # char arithmetic: (char) (e[i] - k - i)
    return ", ".join(str((ord(c) + k + i) & 0xFFFF) for i, c in enumerate(s))


S = P + """
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
final class S {
  private static final byte[] K = {%s};
  static byte decryptByte(byte b, int i) { return (byte) (b ^ K[i %% K.length] ^ i); }
  static byte decryptSub(byte b, int i) { return (byte) ((b - K[i %% K.length]) & 0xff); }
  static String d(byte[] e) { byte[] o = new byte[e.length];
    for (int i = 0; i < e.length; i++) o[i] = decryptByte(e[i], i);
    return new String(o, StandardCharsets.UTF_8); }
  static String n(byte[] e, String cs) throws Exception { byte[] o = new byte[e.length];
    for (int i = 0; i < e.length; i++) o[i] = decryptSub(e[i], i);
    return new String(o, cs); }
  static String l(byte[] e) { byte[] o = new byte[e.length];
    for (int i = 0; i < e.length; i++) o[i] = decryptSub(e[i], i);
    return new String(o, Charset.forName("ISO-8859-1")); }
  static String t(char[] e, int k) { char[] o = new char[e.length];
    for (int i = 0; i < e.length; i++) o[i] = (char) (e[i] - k - i);
    return String.valueOf(o); }
}
""" % ", ".join(sb(k) for k in K)

if variant in ("xor_method", "decoy_nearmiss"):
    seed = 0x6B1E39C47A20D58F
    lo = 4 if variant == "decoy_nearmiss" else 0  # near-miss: 15 hex digits
    files = {"S": S, "h": P + """
final class h {
  static String a(long v) { return S.d(new byte[]{%s}) + Long.toHexString(v); }
  private static String q(long v) {
    char[] tc = S.t(new char[]{%s}, 0x31).toCharArray();
    StringBuilder sb = new StringBuilder(new String(S.d(new byte[]{%s}).getBytes(java.nio.charset.StandardCharsets.US_ASCII), java.nio.charset.StandardCharsets.US_ASCII));
    for (int i = 60; i >= %d; i -= 4) sb.append(tc[(int) ((v >>> i) & 15)]);
    return sb.toString(); }
}
""" % (enc_xor("ANS-"), enc_chr("0123456789ABCDEF", 0x31), enc_xor("ANS-"), lo), "Locator": P + """
public final class Locator {
  public static String reveal() throws Exception {
    Class<?> k = Class.forName(S.d(new byte[]{%s}).intern());
    java.lang.reflect.Method m = k.getDeclaredMethod(S.n(new byte[]{%s}, "US-ASCII"), long.class);
    m.setAccessible(true);
    return String.format("%%s", m.invoke(null, %dL));
  }
}
""" % (enc_xor(PKG + ".h"), enc_sub("q"), seed)}
elif variant == "sub_field":
    files = {"S": S, "f": P + """
final class f {
  static final String a = "ANS-0f1e2d3c4b5a6979";
  static String r;
  static { r = S.l(new byte[]{%s}); }
  static String z = "ANS-9999aaaabbbbcccc";
}
""" % enc_sub("ANS-3d90c7e1a25b48f6"), "Locator": P + """
public final class Locator {
  public static String reveal() throws Exception {
    Class<?> k = Class.forName(new String(S.t(new char[]{%s}, 7).toCharArray()));
    java.lang.reflect.Field fl = k.getDeclaredField(new String(S.d(new byte[]{%s}).getBytes(), java.nio.charset.StandardCharsets.ISO_8859_1));
    fl.setAccessible(true);
    return String.format("%%s", fl.get(null));
  }
}
""" % (enc_chr(PKG + ".f", 7), enc_xor("r"))}
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
pdir = src / PKG.replace(".", "/")
pdir.mkdir(parents=True)
for name, body in files.items():
    (pdir / f"{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "encrypted-strings", "hint": "the app decrypts its own names"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
