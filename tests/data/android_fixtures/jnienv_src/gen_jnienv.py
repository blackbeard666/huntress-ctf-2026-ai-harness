#!/usr/bin/env python3
"""Generate the jnienv_* fixtures (target native-bridge-jnienv-callbacks: a `codec: analysis` v2 puzzle whose
Release.code() calls app `native` methods that use the JNIEnv: jstring / byte[] args, dex static fields, a static
Java mixer called back from C). usage: gen_jnienv.py <varargs_x86_64 | valist_arm64 | decoy_nearmiss> <out.apk>
javac --release 8 -> dex2jar d2j-jar2dex -> gcc / aarch64-linux-gnu-gcc -shared -fPIC -O2 -s jnienv.c -> zipfile.
varargs_x86_64: Bridge.fold (CallStaticLongMethod, variadic) + Bridge.seal (CallStaticLongMethodA), lib/x86_64.
valist_arm64: same chain, fold calls back via CallStaticLongMethodV (va_list), K2 set in <clinit>, lib/arm64-v8a.
decoy_nearmiss: varargs_x86_64's dex, the .so FindClass-es com/huntress/mobile/d26/Kx (absent: no answer).
oracle.sh runs the dex (dex2jar'd back) + an x86_64 build of jnienv.c on the real JVM (real JNI)."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d26"
JDK = "/usr/lib/jvm/java-21-openjdk-amd64/include"
arm = variant == "valist_arm64"
k2 = "static int K2;\n  static { K2 = (int) (K1 >>> 17) ^ 0x3C6EF372; }" if arm else "static int K2 = 0x3C6EF372;"
java = {"K": f"""package {PKG};
final class K {{
  static final long K1 = 0x6A09E667F3BCC908L;
  {k2}
  static long mixer(long a, int b) {{
    long x = a ^ (b * 0x9E3779B1L);
    x *= 0xBF58476D1CE4E5B9L;
    return x ^ (x >>> 31);
  }}
}}
""", "Bridge": f"""package {PKG};
final class Bridge {{
  static {{ System.loadLibrary("arena"); }}
  static native long fold(String tag, byte[] data, int n);
  static native String seal(long v, byte[] salt);
}}
""", "Release": f"""package {PKG};
public final class Release {{
  public static String code() {{
    byte[] d = {{104, 117, 110, 116, -42, 7, 99, -128, 0, 55, 21}};
    long v = Bridge.fold("{'arm-seed' if arm else 'x86-seed'}", d, {13 if arm else 7});
    return Bridge.seal(v, new byte[] {{-3, 17, 66, -91, 5}});
  }}
}}
"""}
defs = ["-DJE_CLS=com_huntress_mobile_d26_Bridge",
        '-DJE_K="com/huntress/mobile/d26/%s"' % ("Kx" if variant == "decoy_nearmiss" else "K")] + (["-DJE_V"] if arm else [])
abis = ["arm64-v8a"] if arm else ["x86_64"]
if variant not in ("varargs_x86_64", "valist_arm64", "decoy_nearmiss"):
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cdir = tmp / "src", tmp / "cls"
pdir = src / PKG.replace(".", "/")
pdir.mkdir(parents=True)
for n, t in java.items():
    (pdir / f"{n}.java").write_text(t)
cdir.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cdir), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cdir)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
cc = {"x86_64": "gcc", "arm64-v8a": "aarch64-linux-gnu-gcc"}
sos = {}
for abi in abis:
    so = tmp / f"{abi}.so"
    subprocess.run([cc[abi], "-shared", "-fPIC", "-O2", "-s", "-I", JDK, "-I", JDK + "/linux", *defs,
                    "-o", str(so), str(HERE / "jnienv.c")], check=True)
    sos[abi] = so.read_bytes()
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"schema":"huntress.mobile.puzzle.v2","day":26,"codec":"analysis"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    for abi, b in sos.items():
        z.writestr(f"lib/{abi}/libarena.so", b)
shutil.rmtree(tmp)
print(out)
