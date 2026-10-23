#!/usr/bin/env python3
"""Generate the pef_* fixtures (coverage atlas row 42 / D20 codec `dynamic`: a puzzle field or a host-dex string that
NAMES a zip entry; the answer lives in that entry, the pointer string is not an answer).
usage: gen_pef.py <variant: jar_multidex_url | host_ptr_xor | elf_stripped | decoy_nearmiss> <out.apk>
Dex: javac --release 8 + dex2jar d2j-jar2dex. Jar: Info-ZIP `zip`. ELF: gcc -shared. Xor: plain python. APK: python zipfile."""
import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOK = {"jar_multidex_url": "ANS-6d1f0b8e3a92c457", "host_ptr_xor": "ANS-a43e7c10d95b26f8",
       "elf_stripped": "ANS-0e8b5d27f1c4a693", "decoy_nearmiss": "ANS-c27e9a04b1f6d38"}[variant]  # decoy: 15 hex
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def dex(pkg, cls, body):
    src, o = tmp / ("src_" + cls), tmp / ("cls_" + cls)
    (src / pkg.replace(".", "/")).mkdir(parents=True)
    (src / pkg.replace(".", "/") / (cls + ".java")).write_text(f"package {pkg};\n{body}\n")
    o.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(o), *map(str, src.rglob("*.java"))], check=True)
    shutil.make_archive(str(tmp / cls), "zip", o)
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / (cls + ".dex")), str(tmp / (cls + ".zip"))],
                   check=True, capture_output=True)
    return (tmp / (cls + ".dex")).read_bytes()


PKG = "com.huntress.mobile.d22"
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
host_ptr = ""
entries = {}
puzzle = {"schema": "huntress.mobile.puzzle.v1", "day": 22, "codec": "dynamic"}
if variant == "jar_multidex_url":
    d1 = dex(PKG + ".core", "Filler", 'public final class Filler { public static String id() { return "core-module"; } }')
    d2 = dex(PKG + ".core", "Module", 'public final class Module { public static String moduleContract() { return "%s"; } }' % TOK)
    jd = tmp / "jar"
    jd.mkdir()
    (jd / "classes.dex").write_bytes(d1)
    (jd / "classes2.dex").write_bytes(d2)
    subprocess.run(["zip", "-q", "-X", str(tmp / "core.jar"), "classes.dex", "classes2.dex"], cwd=jd, check=True)
    entries["assets/modules/core.jar"] = (tmp / "core.jar").read_bytes()
    puzzle["data"] = "file:///android_asset/modules/core.jar"
elif variant == "host_ptr_xor":
    d = dex(PKG + ".payload", "Module", 'public final class Module { public static final String ANSWER = "%s"; }' % TOK)
    entries["assets/stage/payload.bin"] = bytes(b ^ 0x5A for b in d)
    host_ptr = "assets/stage/payload.bin:" + PKG + ".payload.Module"
    puzzle["data"] = "loader"
elif variant in ("elf_stripped", "decoy_nearmiss"):
    (tmp / "m.c").write_text('const char *module_contract(void) { return "%s"; }\n' % TOK)
    subprocess.run(["gcc", "-shared", "-fPIC", "-O0", "-o", str(tmp / "libmod.so"), str(tmp / "m.c")], check=True)
    entries["assets/native/libmod.so"] = (tmp / "libmod.so").read_bytes()
    puzzle["entry" if variant == "elf_stripped" else "data"] = "native/libmod.so"
host = dex(PKG, "MainActivity", 'public final class MainActivity { static final String MOD = "%s"; '
           'public static String load() { return "dalvik.system.DexClassLoader"; } }' % host_ptr)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", json.dumps(puzzle, separators=(",", ":")))
    for n, b in entries.items():
        z.writestr(n, b)
    z.writestr("classes.dex", host)
shutil.rmtree(tmp)
