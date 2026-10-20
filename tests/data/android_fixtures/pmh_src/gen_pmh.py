#!/usr/bin/env python3
"""Generate the pmh_* fixtures (coverage atlas row 80: the answer is reached through dynamic dispatch that never names a
class by string -- an invoke-custom lambda, MethodHandles.Lookup.findStatic + invokeExact (invoke-polymorphic), a
java.lang.reflect.Proxy InvocationHandler keyed by Method.getName(), a D8-style desugared $$ExternalSyntheticLambda).
usage: gen_pmh.py <variant: lambda | mhandle | proxy | desugared | decoy_nearmiss> <out.apk>
javac --release 8 -> Android dx (dex2jar's bundled com.android.dx, --min-sdk-version=26 => dex 038 with call_site_ids /
method_handles) -> zipfile. The oracle (oracle.sh) runs the SAME classes on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d20.pmh"
P = f"package {PKG};\n"
TOK = {"lambda": "ANS-3b8e0f71c2d94a65", "mhandle": "ANS-a09c4e2d71f53b86", "proxy": "ANS-6d1f2a9e0b7c3458",
       "desugared": "ANS-e4c07a3b912d6f85", "decoy_nearmiss": "ANS-3b8e0f71c2d94a6"}[variant]


def xs(s, k):
    return ", ".join(str(ord(c) ^ k) for c in s)


K = P + """
final class k {
  static final char[] T = {%s};
  static final char[] U = {%s};
  static String q(int key) { char[] o = new char[T.length];
    for (int i = 0; i < T.length; i++) o[i] = (char) (T[i] ^ key);
    return new String(o); }
  static String shift(int key) { return q(key); }
  static String shift(long key) { char[] o = new char[U.length];
    for (int i = 0; i < U.length; i++) o[i] = (char) (U[i] ^ (int) key);
    return new String(o); }
  static String z() { return shift(0x11L); }
}
""" % (xs(TOK, 0x2C), xs("ANS-0000111122223333", 0x11))
GATE = {
    "lambda": """
public final class Gate {
  public static String reveal() {
    int key = 0x2c;
    java.util.function.Supplier<String> s = () -> k.q(key);
    java.util.function.IntFunction<String> f = k::q;
    return s.get().equals(f.apply(key)) ? s.get() : null;
  }
}""",
    "mhandle": """
import java.lang.invoke.*;
public final class Gate {
  public static String reveal() throws Throwable {
    MethodHandles.Lookup l = MethodHandles.lookup();
    String n = new StringBuilder("tfihs").reverse().toString();
    MethodHandle h = l.findStatic(k.class, n, MethodType.methodType(String.class, int.class));
    return (String) h.invokeExact(0x2c);
  }
}""",
    "proxy": """
import java.lang.reflect.*;
interface Api { String token(); String other(); }
final class H implements InvocationHandler {
  public Object invoke(Object p, Method m, Object[] a) {
    if (m.getName().equals("token")) return k.q(0x2c);
    return k.z();
  }
}
public final class Gate {
  public static String reveal() {
    Api a = (Api) Proxy.newProxyInstance(Gate.class.getClassLoader(), new Class<?>[]{Api.class}, new H());
    return a.token();
  }
}""",
    "desugared": """
final class Gate$$ExternalSyntheticLambda0 implements java.util.function.Supplier {
  public final int f$0;
  public Gate$$ExternalSyntheticLambda0(int x) { f$0 = x; }
  public final Object get() { return Gate.lambda$reveal$0(f$0); }
}
public final class Gate {
  static String lambda$reveal$0(int key) { return k.q(key); }
  public static String reveal() {
    java.util.function.Supplier s = new Gate$$ExternalSyntheticLambda0(0x2c);
    return (String) s.get();
  }
}""",
}
GATE["decoy_nearmiss"] = GATE["lambda"]
files = {"k": K, "Gate": P + GATE[variant]}
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
pdir = src / PKG.replace(".", "/")
pdir.mkdir(parents=True)
for name, body in files.items():
    (pdir / f"{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
cp = ":".join(map(str, (ROOT / "tools/dex2jar/lib").glob("*.jar")))
subprocess.run(["java", "-cp", cp, "com.android.dx.command.Main", "--dex", "--min-sdk-version=26",
                f"--output={tmp / 'classes.dex'}", str(tmp / "app.zip")], check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "dispatch", "hint": "no Class.forName here"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
