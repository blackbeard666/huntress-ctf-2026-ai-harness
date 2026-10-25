#!/usr/bin/env python3
"""Generate the nlbx_* fixtures (target dex-eval-native-bridge: a `codec: analysis` puzzle whose Release.code() calls
app `native` methods mid-chain). usage: gen_nlbx.py <overload_x86_64 | regnat_arm64 | decoy_nearmiss> <out.apk>
javac --release 8 -> dex2jar d2j-jar2dex -> gcc / aarch64-linux-gnu-gcc -shared -fPIC -O2 nlbx.c -> zipfile.
overload_x86_64: static overloaded natives mix(long,int) / mix(int) (JNI `__JI` / `__I` names) + an instance native
  String tag(String, long) (GetStringUTFChars + snprintf + NewStringUTF) on class Native_Secrets (`_1` escape).
regnat_arm64: static natives fold(long,long) / salt(int) bound only by JNI_OnLoad's RegisterNatives table.
decoy_nearmiss: overload_x86_64's dex, the .so built for class Native_Secret (exports never bind: no answer).
oracle.sh runs the same dex (dex2jar'd back) + an x86_64 build of nlbx.c on the real JVM (real JNI)."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d24"
JDK = "/usr/lib/jvm/java-21-openjdk-amd64/include"
if variant in ("overload_x86_64", "decoy_nearmiss"):
    java = {"Native_Secrets": f"""package {PKG};
public final class Native_Secrets {{
  static {{ System.loadLibrary("arena"); }}
  public static native long mix(long a, int b);
  public static native int mix(int a);
  public native String tag(String p, long v);
}}
""", "Release": f"""package {PKG};
public final class Release {{
  public static String code() {{
    Native_Secrets s = new Native_Secrets();
    long v = Native_Secrets.mix(0x5EED1234ABCDL, Native_Secrets.mix(41));
    return s.tag("ANS-", v);
  }}
}}
"""}
    cls = "com_huntress_mobile_d24_Native_1Secrets" if variant == "overload_x86_64" else \
        "com_huntress_mobile_d24_Native_1Secret"
    defs, abis = [f"-DNLBX_CLS={cls}"], ["x86_64"]
elif variant == "regnat_arm64":
    java = {"Vault": f"""package {PKG};
final class Vault {{
  static {{ System.loadLibrary("arena"); }}
  static native long fold(long a, long b);
  static native int salt(int x);
}}
""", "Release": f"""package {PKG};
public final class Release {{
  public static String code() {{
    long a = Vault.fold(0x0123456789ABCDEFL, (long) Vault.salt(17) << 9);
    return String.format("ANS-%016X", a);
  }}
}}
"""}
    defs, abis = ["-DNLBX_REGNAT", '-DNLBX_JCLS="com/huntress/mobile/d24/Vault"'], ["arm64-v8a"]
else:
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
                    "-o", str(so), str(HERE / "nlbx.c")], check=True)
    sos[abi] = so.read_bytes()
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"schema":"huntress.mobile.puzzle.v2","day":24,"codec":"analysis"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    for abi, b in sos.items():
        z.writestr(f"lib/{abi}/libarena.so", b)
shutil.rmtree(tmp)
print(out)
