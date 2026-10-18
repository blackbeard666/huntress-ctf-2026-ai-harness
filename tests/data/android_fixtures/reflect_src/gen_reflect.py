#!/usr/bin/env python3
"""Generate the reflect_* fixtures (coverage atlas row 43: the answer sits in an R8-renamed class's static field /
method, reached only via Class.forName + getDeclaredField / getDeclaredMethod with ENCODED names; sibling members hold
decoy tokens). usage: gen_reflect.py <variant: field_xor | method_b64 | decoy_nearmiss> <out.apk>
javac --release 8 -> dex2jar d2j-jar2dex -> zipfile. The oracle (oracle.sh) runs the SAME classes on the JVM."""
import base64, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d20.r8"
P = f"package {PKG};\n"


def xs(s, k):
    return ", ".join(str(ord(c) ^ k) for c in s)


FIELD_TARGET = P + """
final class b {
  static final String a = "ANS-0f1e2d3c4b5a6978";
  static String b = "%s";
  private static final String c = "ANS-8899aabbccddeeff";
}
"""
FIELD_LOC = P + """
public final class Locator {
  private static String d(char[] e, int k) { char[] o = new char[e.length];
    for (int i = 0; i < e.length; i++) o[i] = (char) (e[i] ^ (k + i));
    return new String(o); }
  public static String reveal() throws Exception {
    Class<?> k = Class.forName(d(new char[]{%s}, 0x21));
    java.lang.reflect.Field f = k.getDeclaredField(d(new char[]{%s}, 0x40));
    f.setAccessible(true);
    return (String) f.get(null);
  }
}
"""


def xk(s, k):
    return ", ".join(str(ord(c) ^ ((k + i) & 0xFFFF)) for i, c in enumerate(s))


if variant in ("field_xor", "decoy_nearmiss"):
    tok = "ANS-5c2e9a07d1b3f486" if variant == "field_xor" else "ANS-5c2e9a07d1b3f48"
    files = {"b": FIELD_TARGET % tok, "Locator": FIELD_LOC % (xk(PKG + ".b", 0x21), xk("b", 0x40))}
elif variant == "method_b64":
    plain = "ANS-e7a1c40b9f362d58"
    files = {"c": P + """
final class c {
  private static final char[] t = {%s};
  static String a() { return "ANS-1111222233334444"; }
  private static String q() { char[] o = new char[t.length];
    for (int i = 0; i < t.length; i++) o[i] = (char) (t[i] ^ 0x5a);
    return new String(o); }
  static String z() { return "ANS-aaaabbbbccccdddd"; }
}
""" % xs(plain, 0x5A), "Locator": P + """
public final class Locator {
  public static String reveal() throws Exception {
    Class<?> k = Class.forName(new StringBuilder("%s").reverse().toString());
    String mn = new String(java.util.Base64.getDecoder().decode("%s"), java.nio.charset.StandardCharsets.UTF_8);
    java.lang.reflect.Method m = k.getDeclaredMethod(mn);
    m.setAccessible(true);
    return (String) m.invoke(null);
  }
}
""" % ((PKG + ".c")[::-1], base64.b64encode(b"q").decode())}
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
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "reflect", "hint": "the app looks it up by name"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
