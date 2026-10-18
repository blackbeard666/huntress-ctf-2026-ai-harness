#!/usr/bin/env python3
"""Generate the rchain_* fixtures (coverage atlas row 45: R8-renamed class chain; D17 TT hint
`follow b -> a and ignore field c`). The answer is no longer in the asset: ChallengeActivity.onCreate calls into
1-2 letter classes (hand-renamed like R8 output) that hold it encoded in a <clinit> / constructor field.
usage: gen_rchain.py <variant: hint_follow | ctor_chain | decoy_nearmiss> <out.apk>
Writes Java sources, compiles with javac --release 8, converts with dex2jar's d2j-jar2dex, zips classes.dex +
a decoy assets/huntress_puzzle.json (+ the manifest of a stock fixture) with zipfile."""
import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
pkg = "com/huntress/mobile/d17/r8c"
P = "package com.huntress.mobile.d17.r8c;\n"
ACT = P + """
public class ChallengeActivity {
  static final String TAG = "chk";
  String shown;
  protected void onCreate(Object state) {
    android_log(TAG, "follow b -> a and ignore field c");
    shown = new b().a(state != null);
  }
  static void android_log(String t, String m) { System.out.println(t + m); }
}
"""
B = P + """
final class b {
  String c = "%s";
  String a(boolean f) { if (f) return c; return a.b(); }
}
"""
A = P + """
final class a {
  static String k;
  static { k = "%s"; }
  static String b() { return new String(java.util.Base64.getDecoder().decode(k)); }
}
"""
ZZ = P + """
final class zz {
  static String q = "ANS-0123456789abcdef";
}
"""
if variant == "hint_follow":
    asset = {"challenge": "renamed", "answer": "ANS-1111222233334444"}
    files = {"ChallengeActivity": ACT, "b": B % "ANS-deadbeefcafe0042", "a": A % "QU5TLTNiOWQwYzdlNDFhMmY4NTY=",
             "zz": ZZ}
elif variant == "decoy_nearmiss":  # the only well-formed token sits in the ignored field / an unreached class
    asset = {"challenge": "renamed", "answer": "ANS-1111222233334444"}
    files = {"ChallengeActivity": ACT, "b": B % "ANS-deadbeefcafe0042", "a": A % "QU5TLTc3ZTBkMWMyYjNhNDk1OA==",
             "zz": ZZ}
elif variant == "ctor_chain":  # no hint; onCreate -> x.y() -> ab.c() -> new d().e() -> d.<init> iput of a hex const
    asset = {"challenge": "renamed", "answer": "ANS-5555666677778888"}
    files = {"ChallengeActivity": P + """
public class ChallengeActivity {
  String shown;
  protected void onCreate(Object state) { shown = x.y(); }
}
""", "x": P + """
final class x { static String y() { return ab.c(); } }
""", "ab": P + """
final class ab { static String c() { return new d().e(); } }
""", "d": P + """
final class d {
  private final String f;
  d() { f = "414e532d63346532393137613064366233353866"; }
  String e() { return hx(f); }
  static String hx(String s) {
    StringBuilder o = new StringBuilder();
    for (int i = 0; i < s.length(); i += 2) o.append((char) Integer.parseInt(s.substring(i, i + 2), 16));
    return o.toString();
  }
}
""", "zz": ZZ}
else:
    raise SystemExit("unknown variant")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for name, body in files.items():
    (src / pkg / f"{name}.java").parent.mkdir(parents=True, exist_ok=True)
    (src / pkg / f"{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", json.dumps(asset))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
