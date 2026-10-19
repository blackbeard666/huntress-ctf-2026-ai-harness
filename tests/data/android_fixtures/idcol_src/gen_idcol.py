#!/usr/bin/env python3
"""Generate the idcol_* fixtures (coverage atlas row 68, "Name Collapse": same-name members told apart only by their
descriptor, plus case-twin classes `a` / `A`). The request builder appends `proof=` + ONE overload; the other overload
holds a decoy ANS-, so resolving by simple name (or shorty) picks the wrong one.
usage: gen_idcol.py <variant: overload_param | field_overload | decoy_nearmiss> <out.apk>
overload_param / decoy_nearmiss: javac --release 8 + dex2jar d2j-jar2dex; field_overload: smali text assembled with
dex2jar's d2j-smali (Java cannot declare `a:Ljava/lang/String;` and `a:Ljava/lang/Object;` in one class); zipfile."""
import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D2J = ROOT / "tools/dex2jar"
pkg = "com/huntress/mobile/d19/n4me"
P = "package com.huntress.mobile.d19.n4me;\n"
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def java(files):
    src, cls = tmp / "src", tmp / "cls"
    for name, body in files.items():
        (src / pkg / f"{name}.java").parent.mkdir(parents=True, exist_ok=True)
        (src / pkg / f"{name}.java").write_text(body)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    shutil.make_archive(str(tmp / "app"), "zip", cls)
    subprocess.run([str(D2J / "d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")], check=True)


def ovl(real, decoy):
    return {"ChallengeActivity": P + """
public class ChallengeActivity {
  public String telemetry(String dev) { return "debug=" + a.a(dev); }
  public String buildRequest(String host, String dev) {
    StringBuilder sb = new StringBuilder();
    sb.append("https://").append(host).append("/evidence?");
    sb.append("device=").append(dev);
    sb.append("&proof=").append(a.a((Object) dev));
    return sb.toString();
  }
}
""", "a": P + """
final class a {
  static String a(String s) { return "%s"; }
  static String a(Object o) { return "%s"; }
}
""" % (decoy, real), "A": P + """
final class A {
  static String a(Object o) { return "ANS-0000aaaa0000aaaa"; }
}
"""}


if variant == "overload_param":
    asset = {"challenge": "name collapse", "candidates": ["ANS-5e0d1c2b3a49f876", "ANS-0000aaaa0000aaaa"]}
    java(ovl("ANS-c4f1a09e7d2b3368", "ANS-5e0d1c2b3a49f876"))
elif variant == "decoy_nearmiss":
    asset = {"challenge": "name collapse", "candidates": ["ANS-5e0d1c2b3a49f876"]}
    java(ovl("ANS-c4f1a09e7d2b336", "ANS-5e0d1c2b3a49f876"))
elif variant == "field_overload":
    asset = {"challenge": "name collapse", "candidates": ["ANS-71e0c3b5a2d49f08", "ANS-bbbb1111bbbb1111"]}
    L = "Lcom/huntress/mobile/d19/n4me/"
    smali = {"a": f""".class final {L}a;
.super Ljava/lang/Object;
.field static a:Ljava/lang/String;
.field static a:Ljava/lang/Object;
.method static constructor <clinit>()V
    .registers 1
    const-string v0, "ANS-71e0c3b5a2d49f08"
    sput-object v0, {L}a;->a:Ljava/lang/String;
    const-string v0, "ANS-3a6f92d0e1b4c578"
    sput-object v0, {L}a;->a:Ljava/lang/Object;
    return-void
.end method
""", "A": f""".class final {L}A;
.super Ljava/lang/Object;
.field static a:Ljava/lang/Object;
.method static constructor <clinit>()V
    .registers 1
    const-string v0, "ANS-bbbb1111bbbb1111"
    sput-object v0, {L}A;->a:Ljava/lang/Object;
    return-void
.end method
""", "ChallengeActivity": f""".class public {L}ChallengeActivity;
.super Ljava/lang/Object;
.method public buildRequest(Ljava/lang/String;)Ljava/lang/String;
    .registers 4
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct {{v0}}, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "https://"
    invoke-virtual {{v0, v1}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {{v0, p1}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v1, "/evidence?proof="
    invoke-virtual {{v0, v1}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    sget-object v1, {L}a;->a:Ljava/lang/Object;
    invoke-virtual {{v0, v1}}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual {{v0}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method
"""}
    sd = tmp / "smali"
    for name, body in smali.items():
        (sd / f"{name}_.smali").parent.mkdir(parents=True, exist_ok=True)
        (sd / f"{name}_.smali").write_text(body)
    subprocess.run([str(D2J / "d2j-smali.sh"), "-o", str(tmp / "classes.dex"), str(sd)], check=True)
else:
    raise SystemExit("unknown variant")
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", json.dumps(asset))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
