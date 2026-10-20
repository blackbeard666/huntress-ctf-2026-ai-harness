#!/usr/bin/env python3
"""Generate the erc_* fixtures (coverage atlas row 78: N generated look-alike classes with the same bytecode shape each
hold an ANS- literal; only one is wired from ChallengeActivity.onCreate into `...evidence?proof=`).
usage: gen_erc.py <variant: reflect_rev | virtual_factory | decoy_nearmiss> <out.apk>
javac --release 8 -> dex2jar d2j-jar2dex -> zipfile. The oracle (oracle.sh) RUNS ChallengeActivity.onCreate on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d19.cg"
P = f"package {PKG};\n"
TOKS = ["ANS-3a91c07e5d24b6f8", "ANS-b4e20f9d7c1a3856", "ANS-6d0c8b2fa7e41935", "ANS-f17a5e3b09c2d846",
        "ANS-9c4d1b7e2a60f538"]
files = {}
if variant in ("reflect_rev", "decoy_nearmiss"):
    # g0..g4: identical shape; Router resolves ONE by a reversed class name + Base64-free method name
    for i, t in enumerate(TOKS):
        files[f"g{i}"] = P + f"final class g{i} {{ static String t() {{ return \"{t}\"; }} }}\n"
    wired = "g3"
    if variant == "decoy_nearmiss":
        files["g5"] = P + "final class g5 { static String t() { return \"ANS-6d0c8b2fa7e4193\"; } }\n"
        wired = "g5"
    files["Router"] = P + """
final class Router {
  static String route() throws Exception {
    Class<?> k = Class.forName(new StringBuilder("%s").reverse().toString());
    java.lang.reflect.Method m = k.getDeclaredMethod("t");
    return (String) m.invoke(null);
  }
}
""" % (PKG + "." + wired)[::-1]
    files["ChallengeActivity"] = P + """
public class ChallengeActivity {
  public String last;
  public void onCreate(Object state) throws Exception {
    last = "https://backend.invalid/evidence?proof=" + Router.route();
  }
}
"""
elif variant == "virtual_factory":
    files["Node"] = P + "abstract class Node { abstract String v(); }\n"
    for i, t in enumerate(TOKS):
        files[f"n{i}"] = P + f"final class n{i} extends Node {{ String v() {{ return \"{t}\"; }} }}\n"
    files["Factory"] = P + "final class Factory { static Node make() { return new n1(); } }\n"
    files["ChallengeActivity"] = P + """
public class ChallengeActivity {
  public String last;
  public void onCreate(Object state) {
    Node n = Factory.make();
    last = "https://backend.invalid/evidence?proof=" + n.v();
  }
}
"""
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
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "callgraph", "hint": "only one of them is wired"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
