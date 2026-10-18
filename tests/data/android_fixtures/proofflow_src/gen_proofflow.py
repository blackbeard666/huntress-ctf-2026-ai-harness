#!/usr/bin/env python3
"""Generate the proofflow_* fixtures (coverage atlas row 67: decoy insertion -- several ANS- candidates in the asset /
dex, the code picks ONE by appending it after `proof=` in ChallengeActivity's request builder).
usage: gen_proofflow.py <variant: sget_clinit | getter_chain | decoy_nearmiss> <out.apk>
Writes Java sources, compiles with javac --release 8 (StringBuilder chains), converts with dex2jar's d2j-jar2dex,
zips classes.dex + a decoy assets/huntress_puzzle.json (+ the manifest of a stock fixture) with zipfile."""
import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
pkg = "com/huntress/mobile/d18/p7c2"
P = "package com.huntress.mobile.d18.p7c2;\n"
if variant == "sget_clinit":
    asset = {"challenge": "proof", "candidates": ["ANS-0f1e2d3c4b5a6978", "ANS-9a8b7c6d5e4f3021"]}
    files = {"ChallengeActivity": P + """
public class ChallengeActivity {
  static String a = "ANS-0f1e2d3c4b5a6978";
  static String b = "ANS-5c3a91e07bd2f468";
  static String c = "ANS-9a8b7c6d5e4f3021";
  public String telemetry() { return "debug=" + a + ";" + c; }
  public String buildRequest(String host, String dev) {
    StringBuilder sb = new StringBuilder();
    sb.append("https://").append(host).append("/evidence?");
    sb.append("device=").append(dev);
    sb.append("&proof=").append(b);
    return sb.toString();
  }
}
"""}
elif variant == "getter_chain":
    asset = {"challenge": "proof", "answer": "ANS-1234abcd5678ef90"}
    files = {"ChallengeActivity": P + """
public class ChallengeActivity {
  public String hint() { return "evidence?hint=" + a.c(); }
  public String buildRequest(String host) {
    return "https://" + host + "/api/evidence?proof=" + a.b() + "&v=2";
  }
}
""", "a": P + """
final class a {
  static String b() { return d.f; }
  static String c() { return "ANS-aa55aa55aa55aa55"; }
}
""", "d": P + """
final class d {
  static String e = "ANS-feedface00c0ffee";
  static String f;
  static { f = new String("ANS-e71b04c9d2a6385f").intern(); f = "ANS-e71b04c9d2a6385f"; }
}
"""}
elif variant == "decoy_nearmiss":
    asset = {"challenge": "proof", "candidates": ["ANS-0f1e2d3c4b5a6978", "ANS-9a8b7c6d5e4f3021"]}
    files = {"ChallengeActivity": P + """
public class ChallengeActivity {
  static String a = "ANS-0f1e2d3c4b5a6978";
  static String b = "ANS-5c3a91e07bd2f46";
  static String c = "ANS-9a8b7c6d5e4f3021";
  public String telemetry() { return "debug=" + a + ";" + c; }
  public String buildRequest(String host) {
    StringBuilder sb = new StringBuilder("https://");
    sb.append(host).append("/evidence?").append("proof=").append(b);
    return sb.toString();
  }
}
"""}
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
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")], check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", json.dumps(asset))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
