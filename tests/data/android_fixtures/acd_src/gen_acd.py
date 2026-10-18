#!/usr/bin/env python3
"""Generate the acd_* fixtures (coverage atlas rows 42, 44: an ENCRYPTED asset dex / jar loaded via DexClassLoader).
usage: gen_acd.py <variant: aes_cbc_ivprefix | rc4_jar | gcm_pkg_zlib | xor_bytes | decoy_wrong_key> <out.apk>
Inner payload: javac --release 8 + dex2jar d2j-jar2dex (a class returning the token), as a bare dex or `zip`ped into a
jar. Ciphers come from independent writers: `openssl enc` (AES-CBC, RC4 legacy provider), the `cryptography` package's
AESGCM, and a plain python xor. Outer classes.dex = javac/d2j class naming dalvik.system.DexClassLoader + the key."""
import hashlib, os, shutil, subprocess, sys, tempfile, zipfile, zlib
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOK = {"aes_cbc_ivprefix": "ANS-3f9a0c7e51d2b864", "rc4_jar": "ANS-b70e2d4c19f8a356", "gcm_pkg_zlib": "ANS-5c18e9a2f04d7b63",
       "xor_bytes": "ANS-e2a7419d0c6b58f3", "decoy_wrong_key": "ANS-91c4d7e02a5f3b86"}[variant]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def dex(pkg, cls, body):
    src, out_ = tmp / ("src_" + cls), tmp / ("cls_" + cls)
    (src / pkg.replace(".", "/")).mkdir(parents=True)
    (src / pkg.replace(".", "/") / (cls + ".java")).write_text(f"package {pkg};\n{body}\n")
    out_.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(out_), *map(str, src.rglob("*.java"))], check=True)
    shutil.make_archive(str(tmp / cls), "zip", out_)
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / (cls + ".dex")), str(tmp / (cls + ".zip"))],
                   check=True, capture_output=True)
    return (tmp / (cls + ".dex")).read_bytes()


def run(*a, data=None):
    return subprocess.run(a, input=data, check=True, capture_output=True).stdout


inner = dex("com.huntress.mobile.d21.plugin", "Payload",
            'public final class Payload { public static String token() { return "%s"; } }' % TOK)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
key_s, extra = "", ""
iv = bytes.fromhex("a1b2c3d4e5f60718293a4b5c6d7e8f90")
if variant in ("aes_cbc_ivprefix", "decoy_wrong_key"):
    key_s = "Hx7#qL2!vR9@tZ4$"
    enc_key = key_s if variant == "aes_cbc_ivprefix" else "Wq8!rT3#mZ6@pK1$"  # decoy: the dex key is NOT the real key
    asset = iv + run("openssl", "enc", "-aes-128-cbc", "-K", enc_key.encode().hex(), "-iv", iv.hex(), data=inner)
elif variant == "rc4_jar":
    key_s = "l0aderKey-2026!x"
    (tmp / "jar").mkdir()
    (tmp / "jar/classes.dex").write_bytes(inner)
    subprocess.run(["zip", "-q", "-X", str(tmp / "plugin.jar"), "classes.dex"], cwd=tmp / "jar", check=True)
    asset = run("openssl", "enc", "-rc4", "-provider", "legacy", "-provider", "default", "-K", key_s.encode().hex(),
                data=(tmp / "plugin.jar").read_bytes())
elif variant == "gcm_pkg_zlib":
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    pkg = sys.argv[3]  # package name of the stock manifest (aapt/androguard reader, passed in by the caller)
    nonce = bytes.fromhex("0badc0ffee1234567890abcd")
    asset = nonce + AESGCM(hashlib.sha256(pkg.encode()).digest()).encrypt(nonce, zlib.compress(inner, 9), None)
elif variant == "xor_bytes":
    xk = bytes([0x4b, 0x13, 0xa7, 0x5e, 0x90, 0x2c])
    extra = "static final byte[] XK = {%s};" % ", ".join(str(b - 256 if b > 127 else b) for b in xk)
    asset = bytes(b ^ xk[i % len(xk)] for i, b in enumerate(inner))
outer = dex("com.huntress.mobile.d21.loader", "Loader", """
public final class Loader {
  static final String KEY = "%s";
  %s
  public static Object load(String dir) throws Exception {
    Class<?> c = Class.forName("dalvik.system.DexClassLoader");
    return c.getName() + KEY + dir + "/assets/plugin.bin";
  }
}""" % (key_s, extra))
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "loader", "hint": "the real code ships encrypted"}')
    z.writestr("classes.dex", outer)
    z.writestr("assets/plugin.bin", asset)
shutil.rmtree(tmp)
print(out)
