#!/usr/bin/env python3
"""Generate the janus_* fixtures (coverage atlas rows 62, 105: Janus dex/APK polyglot, CVE-2017-13156).
usage: gen_janus.py <variant: prepended_literal | prepended_b64 | appended_inert | decoy_nearmiss> <out.apk>
Dex: javac --release 8 + dex2jar d2j-jar2dex. APK: Info-ZIP `zip -X` (manifest = minSdk 23 skc fixture's, v1-only, no
signing block). Janus: `cat payload.dex base.apk`, Info-ZIP `zip -A` re-bases the central directory offsets, header
file_size patched to the whole file, checksums by d2j-dex-recompute-checksum. Reverse: `cat base.apk inert.dex`."""
import base64, os, shutil, struct, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D2J = ROOT / "tools/dex2jar"
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
RUNTIME = {"prepended_literal": "ANS-3e91c07d5a2b8f64", "prepended_b64": "ANS-b70f2d9e4c18a536",
           "appended_inert": "ANS-0c5e8a17f3d29b46", "decoy_nearmiss": "ANS-9a4d2e7c1b0f835"}[variant]  # decoy: 15 hex
ZIPVIEW = {"prepended_literal": "ANS-d41f7a2c98e0b153", "prepended_b64": "ANS-6f2b90c4e7a1d385",
           "appended_inert": "ANS-e8b3471d0c9f2a65", "decoy_nearmiss": None}[variant]


def dex(name, body):
    src, cls = tmp / name / "src", tmp / name / "cls"
    (src / "com/huntress/mobile/janus").mkdir(parents=True)
    (src / "com/huntress/mobile/janus/Main.java").write_text("package com.huntress.mobile.janus;\n" + body + "\n")
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    shutil.make_archive(str(tmp / name / "c"), "zip", cls)
    subprocess.run([str(D2J / "d2j-jar2dex.sh"), "-f", "-o", str(tmp / name / "c.dex"), str(tmp / name / "c.zip")],
                   check=True, capture_output=True)
    return (tmp / name / "c.dex").read_bytes()


def app(field):
    return ("public final class Main {\n  %s\n  public static String answer() { return K; }\n"
            "  public static void main(String[] a) { System.out.println(answer()); }\n}" % field)


lit = lambda t: 'static final String K = "%s";' % t
b64 = lambda t: 'static final String K = new String(java.util.Base64.getDecoder().decode("%s"));' % \
    base64.b64encode(t.encode()).decode()
zipdex = dex("zipview", app(lit(ZIPVIEW) if ZIPVIEW else 'static final String K = "hello";'))
if variant in ("prepended_literal", "appended_inert"):
    other = dex("other", app(lit(RUNTIME)))
else:  # base64 in a const-string: no literal token in the bytes
    other = dex("other", app(b64(RUNTIME)))
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    (tmp / "a").mkdir()
    (tmp / "a/AndroidManifest.xml").write_bytes(zin.read("AndroidManifest.xml"))
(tmp / "a/assets").mkdir()
(tmp / "a/assets/huntress_puzzle.json").write_text('{"challenge": "janus", "hint": "which dex does the runtime load?"}')
(tmp / "a/classes.dex").write_bytes(zipdex)
subprocess.run(["zip", "-q", "-X", "-9", str(tmp / "base.apk"), "AndroidManifest.xml", "classes.dex",
                "assets/huntress_puzzle.json"], cwd=tmp / "a", check=True)
base = (tmp / "base.apk").read_bytes()
if variant == "appended_inert":  # reverse polyglot: inert dex after the EOCD; the zip view is what runs
    out.write_bytes(base + other)
else:
    (tmp / "j.apk").write_bytes(other + base)
    subprocess.run(["zip", "-q", "-A", str(tmp / "j.apk")], check=True)  # re-base central-directory offsets
    j = (tmp / "j.apk").read_bytes()
    (tmp / "p.dex").write_bytes(j[:0x20] + struct.pack("<I", len(j)) + j[0x24:])  # file_size = whole file (Janus)
    subprocess.run([str(D2J / "d2j-dex-recompute-checksum.sh"), "-f", "-o", str(out), str(tmp / "p.dex")],
                   check=True, capture_output=True)
shutil.rmtree(tmp)
print(out)
