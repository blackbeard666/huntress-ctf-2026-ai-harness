#!/usr/bin/env python3
"""Generate the dexslack_* fixtures (coverage atlas rows 51, 62: data hidden in a dex OUTSIDE its declared structure).
usage: gen_dexslack.py <variant: appended_b64 | inside_zip | orphan_static_039 | decoy_deadmethod> <out.apk>
Dex: javac --release 8 + dex2jar d2j-jar2dex. Slack: plain byte appends (`base64`, `zip` writers), header file_size /
magic patched with struct, checksums recomputed by dex2jar's d2j-dex-recompute-checksum (independent of lib.android)."""
import base64, os, shutil, struct, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOK = {"appended_b64": "ANS-6d2f9a41c07e5b38", "inside_zip": "ANS-a39c0e7b5f1d8264", "orphan_static_039": "ANS-0f8e4c27b9a1d653",
       "decoy_deadmethod": "ANS-c5b1e8d40a2f7396"}[variant]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
D2J = ROOT / "tools/dex2jar"


def dex(pkg, cls, body):
    src, out_ = tmp / "src", tmp / "cls"
    (src / pkg.replace(".", "/")).mkdir(parents=True)
    (src / pkg.replace(".", "/") / (cls + ".java")).write_text(f"package {pkg};\n{body}\n")
    out_.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(out_), *map(str, src.rglob("*.java"))], check=True)
    shutil.make_archive(str(tmp / cls), "zip", out_)
    subprocess.run([str(D2J / "d2j-jar2dex.sh"), "-f", "-o", str(tmp / "c.dex"), str(tmp / (cls + ".zip"))],
                   check=True, capture_output=True)
    return (tmp / "c.dex").read_bytes()


def rechecksum(d):
    (tmp / "p.dex").write_bytes(d)
    subprocess.run([str(D2J / "d2j-dex-recompute-checksum.sh"), "-f", "-o", str(tmp / "q.dex"), str(tmp / "p.dex")],
                   check=True, capture_output=True)
    return (tmp / "q.dex").read_bytes()


APP = """public final class Main {
  %s
  public static String hello(String who) { return "hello " + who; }
  public static void main(String[] a) { System.out.println(hello(a.length > 0 ? a[0] : "world")); }
}"""
if variant == "appended_b64":  # payload past header file_size (file_size / checksum left stale)
    d = dex("com.huntress.mobile.d22.slack", "Main", APP % "") + base64.b64encode(TOK.encode()) + b"\n"
elif variant == "inside_zip":  # a `zip`ped note appended INSIDE file_size (no map_list item covers it), checksums fixed
    (tmp / "z").mkdir()
    (tmp / "z/note.txt").write_text("evidence: " + TOK + "\n")
    subprocess.run(["zip", "-q", "-X", "-9", str(tmp / "n.zip"), "note.txt"], cwd=tmp / "z", check=True)
    d = dex("com.huntress.mobile.d22.slack", "Main", APP % "")
    d = d + b"\0" * (-len(d) % 4) + (tmp / "n.zip").read_bytes()
    d = rechecksum(d[:0x20] + struct.pack("<I", len(d)) + d[0x24:])
elif variant == "orphan_static_039":  # never-read static final String (static_values only), magic bumped to 039
    blob = base64.b32encode(TOK.encode()).decode()
    d = dex("com.huntress.mobile.d22.slack", "Main", APP % ('private static final String BLOB = "%s";' % blob))
    d = rechecksum(b"dex\n039\0" + d[8:])
else:  # decoy: valid-looking token only in a never-invoked private method + a near-miss appended blob
    blob = base64.b64encode(TOK.encode()).decode()
    d = dex("com.huntress.mobile.d22.slack", "Main",
            APP % ('private static String decoyFlag() { return new String(java.util.Base64.getDecoder().decode("%s")); }' % blob))
    d += base64.b64encode(b"ANS-0123456789abcde")  # 15 hex digits: not a token
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "slack", "hint": "the dex says more than its header"}')
    z.writestr("classes.dex", d)
shutil.rmtree(tmp)
print(out)
