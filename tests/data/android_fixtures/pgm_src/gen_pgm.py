#!/usr/bin/env python3
"""Generate the pgm_* fixtures (coverage atlas row 45, original-name restore): R8-style renamed classes whose hint
string uses the ORIGINAL names (`follow com.huntress.vault.SecretVault -> com.huntress.vault.KeyStore and ignore field
SecretVault.cachedToken`); the original names come back from a shipped assets/mapping.txt (ProGuard format), from the
dex SourceFile attribute (class `a` declared in KeyStore.java), or from a kotlin.Metadata d2 array. The answer sits in
a class NOT reached from onCreate (only the follow hint finds it); the reached class holds a decoy in the ignored field.
usage: gen_pgm.py <variant: mapping | sourcefile | kmeta | decoy_nearmiss> <out.apk>
Writes Java sources, compiles with javac --release 8, converts with dex2jar's d2j-jar2dex, zips classes.dex +
assets (+ the manifest of a stock fixture) with zipfile."""
import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
pkg = "com/huntress/mobile/d18/pg"
P = "package com.huntress.mobile.d18.pg;\n"
HINT = "follow com.huntress.vault.SecretVault -> com.huntress.vault.KeyStore and ignore field SecretVault.cachedToken"
if variant == "sourcefile":
    HINT = "follow SecretVault -> KeyStore and ignore field SecretVault.c"
ACT = P + """
public class ChallengeActivity {
  String shown;
  protected void onCreate(Object state) {
    android_log("hint", "%s");
    shown = new b().a(state != null);
  }
  static void android_log(String t, String m) { System.out.println(t + m); }
}
""" % HINT
KMETA_B = KMETA_A = ""
if variant == "kmeta":
    KMETA_B = '@kotlin.Metadata(mv = {1, 9, 0}, k = 1, d2 = {"Lcom/huntress/vault/SecretVault;", "", "cachedToken", "a"})\n'
    KMETA_A = '@kotlin.Metadata(mv = {1, 9, 0}, k = 1, d2 = {"Lcom/huntress/vault/KeyStore;", "", "secret", "b"})\n'
B = P + KMETA_B + """final class b {
  String c = "%s";
  String a(boolean f) { if (f) return c; return "ok"; }
}
"""
A = P + KMETA_A + """final class a {
  static String k;
  static { k = "%s"; }
  static String b() { return new String(java.util.Base64.getDecoder().decode(k)); }
}
"""
ZZ = P + """final class zz {
  static String q = "ANS-0123456789abcdef";
}
"""
KM = """package kotlin;
@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
public @interface Metadata { int k() default 1; int[] mv() default {}; String[] d1() default {}; String[] d2() default {}; }
"""
MAPPING = """# compiler: R8
# compiler_version: 8.5.35
# min_api: 24
# pg_map_id: 5b1c0de
com.huntress.vault.ChallengeActivity -> com.huntress.mobile.d18.pg.ChallengeActivity:
    java.lang.String shown -> shown
    1:3:void onCreate(java.lang.Object):5:7 -> onCreate
com.huntress.vault.KeyStore -> com.huntress.mobile.d18.pg.a:
    java.lang.String secret -> k
    1:1:void <clinit>():3:3 -> <clinit>
    1:1:java.lang.String reveal():4:4 -> b
com.huntress.vault.SecretVault -> com.huntress.mobile.d18.pg.b:
    java.lang.String cachedToken -> c
    1:1:java.lang.String open(boolean):3:3 -> a
com.huntress.vault.Unused -> com.huntress.mobile.d18.pg.zz:
    java.lang.String q -> q
"""
files = {"ChallengeActivity": ACT, "b": B % "ANS-deadbeefcafe0042", "zz": ZZ}
assets = {"assets/huntress_puzzle.json": json.dumps({"challenge": "renamed", "answer": "ANS-1111222233334444"})}
if variant == "mapping":
    files["a"] = A % "QU5TLTllNGMyYTcwZDFiODM1ZjY="  # ANS-9e4c2a70d1b835f6
    assets["assets/mapping.txt"] = MAPPING
elif variant == "decoy_nearmiss":  # followed class holds a near-miss (G), the valid tokens sit in the ignored field/zz
    files["a"] = A % "QU5TLTllNGMyYTcwZDFiODM1Zkc="  # ANS-9e4c2a70d1b835fG
    assets["assets/mapping.txt"] = MAPPING
elif variant == "sourcefile":
    files["a"] = A % "QU5TLTRmMGE2ZDJlOGMxYjk3MzU="  # ANS-4f0a6d2e8c1b9735
elif variant == "kmeta":
    files["a"] = A % "QU5TLTcyYzNlOWQwNWIxNmY4YTQ="  # ANS-72c3e9d05b16f8a4
else:
    raise SystemExit("unknown variant")
src_name = {"a": "KeyStore", "b": "SecretVault"} if variant == "sourcefile" else {}
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for name, body in files.items():
    f = src / pkg / f"{src_name.get(name, name)}.java"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(body)
if variant == "kmeta":
    (src / "kotlin").mkdir(parents=True)
    (src / "kotlin" / "Metadata.java").write_text(KM)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    for k, v in assets.items():
        z.writestr(k, v)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
