#!/usr/bin/env python3
"""Generate the jnicb_* fixtures (coverage atlas row 82: native code calls back into Java BY NAME -- FindClass /
GetStaticMethodID / NewStringUTF literal args / CallStaticObjectMethod; the named Java method computes the answer from
the native's string args, sibling methods with the same signature compute decoys).
usage: gen_jnicb.py <variant: xor_x86_64 | concat_arm64 | decoy_nearmiss> <out.apk>
javac --release 8 -> dex2jar d2j-jar2dex -> gcc / aarch64-linux-gnu-gcc -shared -O2 cbk.c -> zipfile.
The oracle (oracle.sh) runs the SAME classes + the x86_64 build of cbk.c on the real JVM (real JNI)."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d21"
JDK = "/usr/lib/jvm/java-21-openjdk-amd64/include"


def xt(s, key):
    return ", ".join(str(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(s))


BRIDGE = f"""package {PKG};
public final class Bridge {{
  static {{ System.loadLibrary("cbk"); }}
  public static native String nativeAnswer();
}}
"""
# k.q(seed) xors a char table with the seed passed from native; k.p / k.r: same signature, decoy tables
ONE = f"""package {PKG};
final class k {{
  private static final char[] P = {{%s}};
  private static final char[] Q = {{%s}};
  private static final char[] R = {{%s}};
  private static String x(char[] t, String s) {{ char[] o = new char[t.length];
    for (int i = 0; i < t.length; i++) o[i] = (char) (t[i] ^ s.charAt(i %% s.length()));
    return new String(o); }}
  static String p(String s) {{ return x(P, s); }}
  static String q(String s) {{ return x(Q, s); }}
  static String r(String s) {{ return x(R, s); }}
}}
"""
# u.m(prefix, seed): prefix + xor(table, seed); u.n / u.o decoys
TWO = f"""package {PKG};
final class u {{
  private static final char[] T = {{%s}};
  private static final char[] D = {{%s}};
  static String n(String a, String b) {{ return a + "0000000000000000"; }}
  static String m(String a, String b) {{ StringBuilder sb = new StringBuilder(a);
    for (int i = 0; i < T.length; i++) sb.append((char) (T[i] ^ b.charAt(i %% b.length())));
    return sb.toString(); }}
  static String o(String a, String b) {{ StringBuilder sb = new StringBuilder(a);
    for (int i = 0; i < D.length; i++) sb.append((char) (D[i] ^ b.charAt(i %% b.length())));
    return sb.toString(); }}
}}
"""
SEED = "h7Kq!zP2"
if variant in ("xor_x86_64", "decoy_nearmiss"):
    tok = "ANS-3b9e0c17f5a2d846" if variant == "xor_x86_64" else "ANS-3b9e0c17f5a2d84"
    java = ONE % (xt("ANS-a1a1b2b2c3c3d4d4", SEED), xt(tok, SEED), xt("ANS-9f8e7d6c5b4a3928", SEED))
    defs = {"CB_CLASS": "com/huntress/mobile/d21/k", "CB_NAME": "q", "CB_SIG": "(Ljava/lang/String;)Ljava/lang/String;",
            "CB_ARG1": SEED}
    cls_name, abis = "k", ["x86_64"]
elif variant == "concat_arm64":
    java = TWO % (xt("6d04a9e2b81fc357", SEED), xt("1234567890abcdef", SEED))
    defs = {"CB_CLASS": "com/huntress/mobile/d21/u", "CB_NAME": "m",
            "CB_SIG": "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;", "CB_ARG1": "ANS-", "CB_ARG2": SEED}
    cls_name, abis = "u", ["arm64-v8a"]
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
pdir = src / PKG.replace(".", "/")
pdir.mkdir(parents=True)
(pdir / "Bridge.java").write_text(BRIDGE)
(pdir / f"{cls_name}.java").write_text(java)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
dflags = [f'-D{k}="{v}"' for k, v in defs.items()]
cc = {"x86_64": "gcc", "arm64-v8a": "aarch64-linux-gnu-gcc"}
sos = {}
for abi in abis:
    so = tmp / f"{abi}.so"
    subprocess.run([cc[abi], "-shared", "-fPIC", "-O2", "-s", "-I", JDK, "-I", JDK + "/linux", *dflags,
                    "-o", str(so), str(HERE / "cbk.c")], check=True)
    sos[abi] = so.read_bytes()
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "jni-callback", "hint": "the native side asks Java"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    for abi, b in sos.items():
        z.writestr(f"lib/{abi}/libcbk.so", b)
shutil.rmtree(tmp)
print(out)
