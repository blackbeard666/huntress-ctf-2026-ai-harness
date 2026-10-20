#!/usr/bin/env python3
"""Generate the clshadow_* fixtures (coverage atlas row 84: the same class descriptor com.huntress.arena.Gate is defined
in the host dex AND in an asset payload; the class-loader delegation order decides which Gate.token() runs).
usage: gen_clshadow.py <variant: childfirst | nullparent | parentfirst | decoy_parentfirst> <out.apk>
Writes Java sources, compiles the host (Main, optional ChildFirstLoader, host Gate) and the payload Gate separately with
javac --release 8 against a compile-only dalvik.system.DexClassLoader stub (never packaged), converts each jar with
dex2jar's d2j-jar2dex, zips classes.dex (+ classes2.dex) + the payload (bare dex or a jar holding classes.dex) + a stock
manifest with zipfile. The oracle (oracle.sh) runs the SAME host Main on the JVM with a URLClassLoader-backed stub."""
import os, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[4]
J2D = ROOT / "tools/dex2jar/d2j-jar2dex.sh"

STUB = """package dalvik.system;
public class DexClassLoader extends ClassLoader {
  public DexClassLoader(String dexPath, String optimizedDirectory, String librarySearchPath, ClassLoader parent) { super(parent); }
}
"""
GATE = """package com.huntress.arena;
public final class Gate {
  public static final String TOKEN = "%s";
  public static String token() { return TOKEN; }
}
"""
MAIN = """package com.huntress.arena;
public final class Main {
  public static String run(String path) throws Exception {
    ClassLoader cl = new %s(path, "/data/local/tmp/dex", null, %s);
    return (String) cl.loadClass("com.huntress.arena.Gate").getMethod("token").invoke(null);
  }
}
"""
CHILD = """package com.huntress.arena;
public class ChildFirstLoader extends dalvik.system.DexClassLoader {
  public ChildFirstLoader(String p, String o, String l, ClassLoader parent) { super(p, o, l, parent); }
  @Override protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
    Class<?> c = findLoadedClass(name);
    if (c == null) { try { c = findClass(name); } catch (ClassNotFoundException e) { return super.loadClass(name, resolve); } }
    return c;
  }
}
"""
V = {  # variant: (loader class, parent expr, host token, payload token, payload entry, host Gate in classes2.dex)
    "childfirst": ("ChildFirstLoader", "Main.class.getClassLoader()", "ANS-11aa22bb33cc44dd", "ANS-7e4c19a0d2b85f36",
                   "assets/modules/gate.dex", False),
    "nullparent": ("dalvik.system.DexClassLoader", "null", "ANS-0badc0de0badc0de", "ANS-c3f0a9e1b7d24856",
                   "assets/plugin.jar", False),
    "parentfirst": ("dalvik.system.DexClassLoader", "Main.class.getClassLoader()", "ANS-5d81e2f4a6c09b37",
                    "ANS-9f9f0000aaaa5555", "assets/update.dex", True),
    "decoy_parentfirst": ("dalvik.system.DexClassLoader", "Main.class.getClassLoader()", "ANS-5d81e2f4a6c09b3",
                          "ANS-9f9f0000aaaa5555", "assets/update.dex", False),
}
loader, parent, host_tok, pay_tok, entry, multidex = V[variant]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def build(name, files, cp=None):
    src, cls = tmp / f"{name}_src", tmp / f"{name}_cls"
    for rel, body in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / f"{rel}.java").write_text(body)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *(["-cp", cp] if cp else []),
                    *map(str, src.rglob("*.java"))], check=True)
    return cls


def dex(cls, keep, name):
    jar = tmp / f"{name}.jar"
    with zipfile.ZipFile(jar, "w") as z:
        for f in sorted(cls.rglob("*.class")):
            rel = f.relative_to(cls).as_posix()
            if keep(rel):
                z.write(f, rel)
    d = tmp / f"{name}.dex"
    subprocess.run([str(J2D), "-f", "-o", str(d), str(jar)], check=True, capture_output=True)
    return d.read_bytes()


stub = build("stub", {"dalvik/system/DexClassLoader": STUB})
host_files = {"com/huntress/arena/Main": MAIN % (loader, parent), "com/huntress/arena/Gate": GATE % host_tok}
if loader == "ChildFirstLoader":
    host_files["com/huntress/arena/ChildFirstLoader"] = CHILD
host = build("host", host_files, cp=str(stub))
pay = build("pay", {"com/huntress/arena/Gate": GATE % pay_tok})
is_gate = lambda r: r.endswith("/Gate.class")  # noqa: E731
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00" + bytes(4))
    if multidex:
        z.writestr("classes.dex", dex(host, lambda r: not is_gate(r), "h1"))
        z.writestr("classes2.dex", dex(host, is_gate, "h2"))
    else:
        z.writestr("classes.dex", dex(host, lambda r: True, "h1"))
    pd = dex(pay, lambda r: True, "p")
    if entry.endswith(".jar"):
        import io
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, "w") as jz:
            jz.writestr("classes.dex", pd)
        pd = bio.getvalue()
    z.writestr(entry, pd)
print(out)
