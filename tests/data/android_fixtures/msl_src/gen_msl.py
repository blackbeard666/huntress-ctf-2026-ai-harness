#!/usr/bin/env python3
"""Generate the msl_* fixtures (coverage atlas row 85: a multi-stage loader -- the stage-1 dex decrypted from an asset
names ANOTHER entry + its key, and decrypts it into stage 2 / 3).
usage: gen_msl.py <variant: aes_rc4 | jar_aes_rc4 | decoy_rc4_wrong_key> <out.apk>
Every dex: javac --release 8 + dex2jar d2j-jar2dex. Ciphers from independent writers: `openssl enc` (AES-128-CBC with
the IV prefixed, AES-128-ECB, RC4 legacy provider); the jar is built with `zip`."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOK = {"aes_rc4": "ANS-4d7c19e3a05b82f6", "jar_aes_rc4": "ANS-a83f5e0217c9d64b",
       "decoy_rc4_wrong_key": "ANS-0e6b93d1c4a7f528"}[variant]
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


def jbytes(b):
    return ", ".join(str(x - 256 if x > 127 else x) for x in b)


def loader(pkg, cls, key_s, nxt, arr=b""):
    return dex(pkg, cls, """
public final class %s {
  static final String KEY = "%s";
  static final byte[] K2 = {%s};
  public static Object load(String dir) throws Exception {
    Class<?> c = Class.forName("dalvik.system.DexClassLoader");
    return c.getName() + KEY + K2.length + dir + "/%s";
  }
}""" % (cls, key_s, jbytes(arr), nxt))


def rc4(key, data):
    return run("openssl", "enc", "-rc4", "-provider", "legacy", "-provider", "default", "-K", key.hex(), data=data)


final = dex("com.huntress.mobile.d22.core", "Core",
            'public final class Core { public static String token() { return "%s"; } }' % TOK)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
iv = bytes.fromhex("5e1a9c3b7d20f4861e3a5c7b9d0f2468")
entries = {}
if variant in ("aes_rc4", "decoy_rc4_wrong_key"):
    outer_key = "0uterStage1Key!!"
    k2 = bytes.fromhex("9f3c61e2a7b04d58c19e2f7a63b8d045")
    real = k2 if variant == "aes_rc4" else bytes.fromhex("9f3c61e2a7b04d58c19e2f7a63b8d046")  # decoy: near-miss key
    stage1 = loader("com.huntress.mobile.d22.stage1", "Stage1", "", "assets/core.dat", k2)
    entries["assets/stage1.bin"] = iv + run("openssl", "enc", "-aes-128-cbc", "-K", outer_key.encode().hex(),
                                            "-iv", iv.hex(), data=stage1)
    entries["assets/core.dat"] = rc4(real, final)
else:  # jar_aes_rc4: outer RC4 -> stage-1 jar (classes.dex + assets/next.enc) -> AES-ECB stage-2 dex -> RC4 stage-3 dex
    outer_key = "l0ader-Outer-K3y"
    k2s = "Inner#Key-2026$q"
    xk = bytes.fromhex("5ac31e77902be4d1086fa93c27b5e04d")
    stage2 = loader("com.huntress.mobile.d22.stage2", "Stage2", "", "assets/final.bin", xk)
    stage1 = loader("com.huntress.mobile.d22.stage1", "Stage1", k2s, "assets/next.enc")
    (tmp / "jar/assets").mkdir(parents=True)
    (tmp / "jar/classes.dex").write_bytes(stage1)
    (tmp / "jar/assets/next.enc").write_bytes(run("openssl", "enc", "-aes-128-ecb", "-K", k2s.encode().hex(), data=stage2))
    subprocess.run(["zip", "-q", "-X", "-r", str(tmp / "stage1.jar"), "classes.dex", "assets"], cwd=tmp / "jar", check=True)
    entries["assets/stage1.bin"] = rc4(outer_key.encode(), (tmp / "stage1.jar").read_bytes())
    entries["assets/final.bin"] = rc4(xk, final)
outer = loader("com.huntress.mobile.d22.loader", "Loader", outer_key, "assets/stage1.bin")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "loader", "hint": "stage one loads stage two"}')
    z.writestr("classes.dex", outer)
    for n, b in entries.items():
        z.writestr(n, b)
shutil.rmtree(tmp)
print(out)
