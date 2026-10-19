#!/usr/bin/env python3
"""Generate the opq_* fixtures (coverage atlas row 72, opaque predicates + unreachable decoy literals). The request
builder appends `proof=` + a value chosen behind an opaque predicate; the never-taken arm holds a decoy ANS- that sits
LAST in bytecode order, so a last-write-wins walk picks the decoy.
usage: gen_opq.py <variant: mulpar | getter_sq | field_orn | decoy_nearmiss> <out.apk>
javac --release 8 + dex2jar d2j-jar2dex + zipfile (assets/huntress_puzzle.json lists every candidate)."""
import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[4]
D2J = ROOT / "tools/dex2jar"
pkg = "com/huntress/mobile/d20/opq"
P = "package com.huntress.mobile.d20.opq;\n"
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def java(files):
    src, cls = tmp / "src", tmp / "cls"
    for name, body in files.items():
        (src / pkg / f"{name}.java").parent.mkdir(parents=True, exist_ok=True)
        (src / pkg / f"{name}.java").write_text(P + body)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    shutil.make_archive(str(tmp / "app"), "zip", cls)
    subprocess.run([str(D2J / "d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")], check=True)


BUILD = """
public class ChallengeActivity {
  public String buildRequest(String host, String dev) {
    StringBuilder sb = new StringBuilder();
    sb.append("https://").append(host).append("/evidence?");
    sb.append("device=").append(dev);
    sb.append("&proof=").append(%s);
    return sb.toString();
  }
%s
}
"""
if variant in ("mulpar", "decoy_nearmiss"):
    real = "ANS-6d2a91f0c7e43b85" if variant == "mulpar" else "ANS-6d2a91f0c7e43b8"
    decoy = "ANS-f19b3c7e0a2d5864"
    files = {"ChallengeActivity": BUILD % ("pick(dev.length())", """
  static String pick(int x) {
    String v;
    if (x * (x + 1) %% 2 == 0) { v = "%s"; } else { v = "%s"; }
    return v;
  }""" % (real, decoy))}
    cands = [decoy] + ([real] if variant == "mulpar" else [])
elif variant == "getter_sq":
    real, decoy = "ANS-0e8c4b27d1f9a356", "ANS-a7350d9e2bc1f048"
    files = {"ChallengeActivity": BUILD % ("K.a(dev.length(), host.length())", ""), "K": """
final class K {
  static String a(int x, int y) {
    if (7 * y * y - 1 != x * x) return "%s";
    if ((x * x) %% 4 > 1) return "ANS-1111222233334444";
    return "%s";
  }
}""" % (real, decoy)}
    cands = [decoy, real, "ANS-1111222233334444"]
elif variant == "field_orn":
    real, decoy = "ANS-b4d07e2f913c6a58", "ANS-3c9e1a70f5b2d846"
    files = {"ChallengeActivity": BUILD % ("T.t", ""), "T": """
final class T {
  static String t;
  static {
    int z = (int) System.nanoTime();
    if ((z | ~z) == -1) t = "%s"; else t = "%s";
  }
}""" % (real, decoy)}
    cands = [real, decoy]
else:
    raise SystemExit("unknown variant")
java(files)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00" + b"\x00" * 4)
    z.write(tmp / "classes.dex", "classes.dex")
    z.writestr("assets/huntress_puzzle.json", json.dumps({"challenge": "dead branch", "candidates": cands}))
shutil.rmtree(tmp)
