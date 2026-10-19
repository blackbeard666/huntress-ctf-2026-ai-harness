#!/usr/bin/env python3
"""Generate the sobf_* fixtures (coverage atlas row 71: open-source Android string obfuscators). Each variant ships the
obfuscator's runtime class under its real package name plus an app class calling it the way the tool rewrites call
sites; the oracle (oracle.sh) RUNS the compiled classes on the JVM.
usage: gen_sobf.py <stringfog_b64 | stringfog_bytes | obfuscapk_aes | allatori | decoy_stringfog> <out.apk>
javac --release 8 -> dex2jar d2j-jar2dex -> zipfile; obfuscapk ciphertext from `openssl enc -aes-256-ecb`."""
import base64, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def jstr(s):
    return "".join(c if 0x20 <= ord(c) < 0x7F and c not in '"\\' else "\\u%04x" % ord(c) for c in s)


def jbytes(b):
    return ", ".join(str(x - 256 if x > 127 else x) for x in b)


SF_IMPL = """package com.github.megatronking.stringfog.xor;
public final class StringFogImpl {
  public String decrypt(String data, String key) {
    return new String(xor(java.util.Base64.getDecoder().decode(data), key.getBytes(java.nio.charset.StandardCharsets.UTF_8)),
                      java.nio.charset.StandardCharsets.UTF_8);
  }
  public String decrypt(byte[] data, byte[] key) {
    return new String(xor(data, key), java.nio.charset.StandardCharsets.UTF_8);
  }
  private static byte[] xor(byte[] d, byte[] k) {
    byte[] o = new byte[d.length];
    for (int i = 0; i < d.length; i++) o[i] = (byte) (d[i] ^ k[i % k.length]);
    return o;
  }
}
"""
SF_GEN = """package com.huntress.mobile.d21.sf;
public final class StringFog {
  private static final com.github.megatronking.stringfog.xor.StringFogImpl IMPL =
      new com.github.megatronking.stringfog.xor.StringFogImpl();
  public static String decrypt(String value, String key) { return IMPL.decrypt(value, key); }
  public static String decrypt(byte[] value, byte[] key) { return IMPL.decrypt(value, key); }
}
"""
APP = """package com.huntress.mobile.d21.sf;
public class Main {
  public void show(java.io.PrintStream out) {
    out.println(%s);
    out.println(%s);
  }
}
"""
pk = "com/huntress/mobile/d21/sf"
if variant in ("stringfog_b64", "decoy_stringfog"):
    tok, key = ("flag:ANS-5d0e8a3c71b94f26" if variant == "stringfog_b64" else "flag:ANS-5d0e8a3c71b94f2"), "Hx7#qLp2"
    enc = lambda p: base64.b64encode(bytes(c ^ key.encode()[i % len(key)] for i, c in enumerate(p.encode()))).decode()
    files = {"com/github/megatronking/stringfog/xor/StringFogImpl": SF_IMPL, f"{pk}/StringFog": SF_GEN,
             f"{pk}/Main": APP % (f'StringFog.decrypt("{enc("welcome back")}", "{key}")',
                                  f'StringFog.decrypt("{enc(tok)}", "{key}")')}
elif variant == "stringfog_bytes":
    key = bytes([0x3A, 0x91, 0x5C, 0x07, 0xE4])
    enc = lambda p: bytes(c ^ key[i % len(key)] for i, c in enumerate(p.encode()))
    arr = lambda b: "new byte[]{%s}" % jbytes(b)
    files = {"com/github/megatronking/stringfog/xor/StringFogImpl": SF_IMPL, f"{pk}/StringFog": SF_GEN,
             f"{pk}/Main": APP % (f"StringFog.decrypt({arr(enc('session ok'))}, {arr(key)})",
                                  f"StringFog.decrypt({arr(enc('ANS-c2f7104e9ba36d85'))}, {arr(key)})")}
elif variant == "obfuscapk_aes":
    secret = "This-key-need-to-be-32-character"  # obfuscapk's default encryption_secret

    def enc(p):
        return subprocess.run(["openssl", "enc", "-aes-256-ecb", "-nosalt", "-K", secret.encode().hex()],
                              input=p.encode(), capture_output=True, check=True).stdout.hex()
    files = {"com/decryptstringmanager/DecryptString": """package com.decryptstringmanager;
public class DecryptString {
  public static String decryptString(String hex) {
    try {
      byte[] ct = new byte[hex.length() / 2];
      for (int i = 0; i < ct.length; i++) ct[i] = (byte) Integer.parseInt(hex.substring(2 * i, 2 * i + 2), 16);
      javax.crypto.Cipher c = javax.crypto.Cipher.getInstance("AES/ECB/PKCS5Padding");
      c.init(javax.crypto.Cipher.DECRYPT_MODE, new javax.crypto.spec.SecretKeySpec("%s".getBytes("UTF-8"), "AES"));
      return new String(c.doFinal(ct), "UTF-8");
    } catch (Exception e) { return hex; }
  }
}
""" % secret, f"{pk}/Main": APP % (f'com.decryptstringmanager.DecryptString.decryptString("{enc("loading")}")',
                                  f'com.decryptstringmanager.DecryptString.decryptString("{enc("ANS-71e3b0a9c4d6f258")}")')}
elif variant == "allatori":
    k1, k2 = 0x2E, 0x51  # last char ^ k1, previous ^ k2, alternating from the end

    def enc(p):
        n = len(p)
        return "".join(chr(ord(c) ^ (k1 if (n - 1 - i) % 2 == 0 else k2)) for i, c in enumerate(p))
    files = {f"{pk}/a": """package com.huntress.mobile.d21.sf;
public final class a {
  public static String ALLATORIxDEMO(String s) {
    int n = s.length();
    char[] c = new char[n];
    int i = n - 1;
    while (i >= 0) {
      c[i] = (char) (s.charAt(i) ^ %d);
      if (--i < 0) break;
      c[i] = (char) (s.charAt(i) ^ %d);
      i--;
    }
    return new String(c);
  }
}
""" % (k1, k2), f"{pk}/Main": APP % (f'a.ALLATORIxDEMO("{jstr(enc("hello"))}")', f'a.ALLATORIxDEMO("{jstr(enc("token=ANS-08ad5f3e6c2b9174"))}")')}
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for name, body in files.items():
    (src / name).parent.mkdir(parents=True, exist_ok=True)
    (src / f"{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "strings", "hint": "the obfuscator hides them"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
