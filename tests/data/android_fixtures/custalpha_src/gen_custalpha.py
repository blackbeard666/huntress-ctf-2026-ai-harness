#!/usr/bin/env python3
"""Generate the custalpha_* fixtures (coverage atlas rows 35/36: puzzle data written in a custom base64 / base32 /
base58 alphabet, or substituted with an alphabet as key, the alphabet carried in the dex or an asset).
usage: gen_custalpha.py <variant: b64_dex | b32_asset | b58_dex | subst_dex | decoy_nearmiss> <out.apk>
Encoding uses coreutils (base64 / base32 piped through tr) or the `base58` pip writer; the alphabet lives in a Java
class compiled with javac --release 8 + dex2jar d2j-jar2dex, or in assets/cfg.json (jq). The oracle (oracle.sh) reads
the alphabet back with dex2jar + javap -constants (or jq) and decodes with tr + base64/base32 -d (or int arithmetic)."""
import json, os, random, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STD64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
STD32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
STD58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def shuffled(s, seed):
    l = list(s)
    random.Random(seed).shuffle(l)
    return "".join(l)


def sh(cmd, inp):
    return subprocess.run(["sh", "-c", cmd], input=inp, capture_output=True, check=True).stdout.decode().strip()


alpha_dex = alpha_asset = None
if variant in ("b64_dex", "decoy_nearmiss"):
    alpha_dex = shuffled(STD64, 2026 if variant == "b64_dex" else 77)
    plain = b"answer: ANS-5f1c8e03a7d94b26" if variant == "b64_dex" else b"answer: ANS-5f1c8e03a7d94b2"
    data = sh(f"base64 -w0 | tr '{STD64}' '{alpha_dex}'", plain)
    puzzle = {"codec": "custom64", "data": data}
elif variant == "b32_asset":
    alpha_asset = shuffled(STD32, 32)
    data = sh(f"base32 -w0 | tr '{STD32}' '{alpha_asset}'", b"flag=ANS-c3a09e7d15f2b864")
    puzzle = {"codec": "t32", "data": data}
elif variant == "b58_dex":
    import base58
    alpha_dex = shuffled(STD58, 58)
    data = base58.b58encode(b"ANS-0b9d4e6a2c71f853", alphabet=alpha_dex.encode()).decode()
    puzzle = {"codec": "b58x", "data": data}
elif variant == "subst_dex":
    alpha_dex = shuffled(STD64, 6464)
    data = sh(f"tr '{''.join(sorted(alpha_dex))}' '{alpha_dex}'", b"token ANS-7e2f0a95c4d1b638 ok")
    puzzle = {"codec": "mono", "data": data}
else:
    sys.exit("variant?")

tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
dex = None
if alpha_dex:
    src, cls = tmp / "src/com/huntress/mobile/d20/k7", tmp / "cls"
    src.mkdir(parents=True)
    cls.mkdir()
    (src / "Table.java").write_text("package com.huntress.mobile.d20.k7;\npublic final class Table {\n"
                                    f"  public static final String T = {json.dumps(alpha_dex)};\n"
                                    "  public static String table() { return T; }\n}\n")
    subprocess.run(["javac", "--release", "8", "-d", str(cls), str(src / "Table.java")], check=True)
    shutil.make_archive(str(tmp / "app"), "zip", cls)
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"),
                    str(tmp / "app.zip")], check=True)
    dex = (tmp / "classes.dex").read_bytes()
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", json.dumps(puzzle))
    if dex:
        z.writestr("classes.dex", dex)
    if alpha_asset:
        z.writestr("assets/cfg.json", json.dumps({"theme": "dark", "table": alpha_asset}))
shutil.rmtree(tmp)
print(out)
