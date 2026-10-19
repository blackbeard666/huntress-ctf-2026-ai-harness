#!/usr/bin/env python3
"""Generate the dcall_* fixtures (coverage atlas rows 35/70: a dex string-decrypt helper `decrypt("<cipher>", 7)` whose
answer only appears when the helper runs with the CALL SITE's constant arguments).
usage: gen_dcall.py <variant: str_int | bytes_sget | fallback_arr | decoy_nearmiss> <out.apk> [token]
Writes Java sources, compiles with javac --release 8, converts with dex2jar's d2j-jar2dex, zips classes.dex + the
manifest of a stock fixture with zipfile. The oracle (oracle.sh) runs the SAME compiled classes on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d20.dc;\n"


def jstr(s):
    return "".join(c if 0x20 <= ord(c) < 0x7F and c not in '"\\' else "\\u%04x" % ord(c) for c in s)


def enc_si(plain, k):  # inverse of A.a(String, int): c ^ ((k + 3*i) & 0xff)
    return "".join(chr(ord(c) ^ ((k + 3 * i) & 0xFF)) for i, c in enumerate(plain))


STR_INT = P + """
public final class A {
  private int n;
  String a(String s, int k) {
    StringBuilder b = new StringBuilder();
    for (int i = 0; i < s.length(); i++) b.append((char) (s.charAt(i) ^ ((k + 3 * i) & 0xff)));
    return b.toString();
  }
  public void show(java.io.PrintStream out) {
    out.println("starting");
    n = out.hashCode();
    out.println(a("%s", %d));
  }
}
"""
if variant in ("str_int", "decoy_nearmiss"):
    tok = "flag:ANS-3b9e07d1c45af862" if variant == "str_int" else "flag:ANS-3b9e07d1c45af86"
    files = {"A": STR_INT % (jstr(enc_si(tok, 0x4D)), 0x4D)}
elif variant == "bytes_sget":
    key = b"q7#Lm"
    plain = b"ANS-e15c0a9d7f2b4368"
    ct = ", ".join(str(((b ^ key[i % len(key)]) + 128) % 256 - 128) for i, b in enumerate(plain))
    files = {"Codec": P + """
public class Codec {
  static String K;
  static { K = "q7" + "#Lm"; }
  public static byte[] decode(byte[] d, String key) {
    byte[] kb = key.getBytes();
    byte[] o = new byte[d.length];
    for (int i = 0; i < d.length; i++) o[i] = (byte) (d[i] ^ kb[i % kb.length]);
    return o;
  }
}
""", "Main": P + """
public class Main {
  public void show(java.io.PrintStream out) {
    out.println("boot");
    out.println(new String(Codec.decode(new byte[]{%s}, Codec.K), java.nio.charset.StandardCharsets.UTF_8));
  }
}
""" % ct}
elif variant == "fallback_arr":  # cipher reached through a runtime index: only the per-const-string fallback finds it
    plain = "ANS-90c4e2a7b16fd358"
    ct = "".join(chr(ord(c) + 5 + (i & 3)) for i, c in enumerate(plain))
    files = {"Z": P + """
public class Z {
  static final String[] T = {"%s", "%s"};
  static String deobf(String s) {
    char[] c = s.toCharArray();
    for (int i = 0; i < c.length; i++) c[i] = (char) (c[i] - 5 - (i & 3));
    return new String(c);
  }
  public void show(java.io.PrintStream out) {
    out.println(deobf(T[out.hashCode() & 1]));
  }
}
""" % (jstr(ct), jstr("".join(chr(ord(c) + 5 + (i & 3)) for i, c in enumerate("hello-world-xyz"))))}
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for name, body in files.items():
    (src / "com/huntress/mobile/d20/dc").mkdir(parents=True, exist_ok=True)
    (src / f"com/huntress/mobile/d20/dc/{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "decrypt", "hint": "the helper needs its arguments"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
