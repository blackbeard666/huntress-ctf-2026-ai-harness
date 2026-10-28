#!/usr/bin/env python3
"""Generate the zsl_* fixtures (coverage atlas row 110: zip slip in an extracted asset archive).
usage: gen_zsl.py <variant: config_three_collide | codecache_dex | decoy_shadowed> <out.apk>
classes.dex = javac --release 8 + dex2jar d2j-jar2dex of zsl_src/Loader.java (ZipInputStream + new File(dir, name) +
FileOutputStream, no canonical check; reads files/config.json / code_cache/plugin.dex). assets/bundle.zip is written by
python zipfile with raw names: in-dir, backslash, absolute (re-rooted), and several '..' names resolving to the SAME
escaped path, only the last of which is what the app reads. Oracle: oracle.sh runs the same Loader on a desktop JVM."""
import json, os, shutil, subprocess, sys, tempfile, warnings, zipfile
from pathlib import Path

warnings.simplefilter("ignore")  # zipfile warns on the deliberate duplicate names
variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def dex_of(srcs, name):
    cls = tmp / ("cls_" + name)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, srcs)], check=True)
    shutil.make_archive(str(tmp / name), "zip", cls)
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / (name + ".dex")),
                    str(tmp / (name + ".zip"))], check=True, capture_output=True)
    return (tmp / (name + ".dex")).read_bytes()


def payload_dex(tok):
    src = tmp / ("p_" + tok) / "com/huntress/mobile/d28/plugin"
    src.mkdir(parents=True)
    (src / "Payload.java").write_text("package com.huntress.mobile.d28.plugin;\npublic final class Payload { public "
                                      "static String token() { return \"%s\"; } }\n" % tok)
    return dex_of([src / "Payload.java"], "payload_" + tok[4:])


def cfg(tok, note):
    return json.dumps({"feature": "sync", "note": note, "unlock": tok}).encode()


if variant == "config_three_collide":
    entries = [("config.json", cfg("ANS-1a2b3c4d5e6f7081", "stays in unpacked/")),
               ("..\\config.json", cfg("ANS-2b3c4d5e6f708192", "backslash is a literal name char")),
               ("/config.json", cfg("ANS-3c4d5e6f708192a3", "absolute: re-rooted under unpacked/")),
               ("../config.json", cfg("ANS-4d5e6f708192a3b4", "escapes, then overwritten")),
               ("sub/readme.txt", b"creates unpacked/sub/ so the next name's kernel walk succeeds"),
               ("./sub/../../config.json", cfg("ANS-5e6f708192a3b4c5", "escapes, then overwritten")),
               ("/../config.json", cfg("ANS-6f708192a3b4c5d6", "escapes last: this is files/config.json")),
               ("../../config.json", cfg("ANS-708192a3b4c5d6e7", "escapes too far: <data>/config.json"))]
elif variant == "codecache_dex":
    entries = [("plugin.dex", payload_dex("ANS-8192a3b4c5d6e7f8")),
               ("../../code_cache/plugin.dex", payload_dex("ANS-92a3b4c5d6e7f809")),
               ("..\\..\\code_cache\\plugin.dex", payload_dex("ANS-a3b4c5d6e7f8091a")),
               ("/code_cache/plugin.dex", payload_dex("ANS-b4c5d6e7f8091a2b")),
               ("x/", b""),
               ("x/../../../code_cache/./plugin.dex", payload_dex("ANS-c5d6e7f8091a2b3c")),
               ("config.json", cfg("pending", "no token here"))]
elif variant == "decoy_shadowed":  # every token is in-dir, backslash, re-rooted or overwritten by a later escape
    entries = [("config.json", cfg("ANS-d6e7f8091a2b3c4d", "stays in unpacked/")),
               ("..\\config.json", cfg("ANS-e7f8091a2b3c4d5e", "backslash is a literal name char")),
               ("/config.json", cfg("ANS-f8091a2b3c4d5e6f", "absolute: re-rooted under unpacked/")),
               ("../config.json", cfg("ANS-091a2b3c4d5e6f70", "escapes, then overwritten")),
               ("sub/", b""),
               ("sub/../../config.json", cfg("ANS-1a2b3c4d5e6f7a8b", "escapes, then overwritten")),
               ("/./../config.json", cfg("ANS-pending-rotation", "escapes last: no valid token")),
               ("ghost/../../config.json", cfg("ANS-2b3c4d5e6f7a8b9c", "lexically the last escape, but ghost/ does "
                                               "not exist: open() fails and the extraction stops"))]
else:
    raise SystemExit("unknown variant " + variant)

with zipfile.ZipFile(tmp / "bundle.zip", "w", zipfile.ZIP_DEFLATED) as zb:
    for n, data in entries:
        zb.writestr(zipfile.ZipInfo(n, (2026, 10, 27, 0, 0, 0)), data, zipfile.ZIP_DEFLATED)
outer = dex_of([HERE / "Loader.java"], "loader")
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "slip", "hint": "the app unpacks its bundle on first run"}')
    z.writestr("classes.dex", outer)
    z.writestr("assets/bundle.zip", (tmp / "bundle.zip").read_bytes(), zipfile.ZIP_STORED)
shutil.rmtree(tmp)
print(out)
