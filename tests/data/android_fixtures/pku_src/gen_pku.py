#!/usr/bin/env python3
"""Generate the pku_* fixtures (coverage atlas: payload-magic-known-plaintext-unwrap -- a WRAPPED secondary payload in
assets, no class-loader hint, no key anywhere in the APK; the wrapper is only recoverable from the payload's own magic).
usage: gen_pku.py <variant: xor12_dex | add_rev_b64_jar | rolling_elf | gzip_sub_sqlite | decoy_nearmiss> <out.apk>
Inner payloads come from independent writers: javac --release 8 + dex2jar d2j-jar2dex (dex), `zip` (jar), gcc -shared
(ELF .so), the sqlite3 CLI (db); wrappers from coreutils `base64`, `gzip -n`, `rev`-style byte reversal and plain python
byte arithmetic with the key written below. Outer classes.dex = a javac/d2j class with no loader / key."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOK = {"xor12_dex": "ANS-7d3e91b0c5a2f468", "add_rev_b64_jar": "ANS-0f6b2c9e83d1a547", "rolling_elf": "ANS-c41f8a2d6e09b375",
       "gzip_sub_sqlite": "ANS-92a5e0d71c3b8f46", "decoy_nearmiss": "ANS-5e8b1d4c27a0f9g3"}[variant]  # decoy: 'g' is not hex
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def run(*a, data=None, cwd=None):
    return subprocess.run(a, input=data, check=True, capture_output=True, cwd=cwd).stdout


def dex(pkg, cls, body):
    src, o = tmp / ("src_" + cls), tmp / ("cls_" + cls)
    (src / pkg.replace(".", "/")).mkdir(parents=True)
    (src / pkg.replace(".", "/") / (cls + ".java")).write_text(f"package {pkg};\n{body}\n")
    o.mkdir()
    run("javac", "--release", "8", "-d", str(o), *map(str, src.rglob("*.java")))
    shutil.make_archive(str(tmp / cls), "zip", o)
    run(str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / (cls + ".dex")), str(tmp / (cls + ".zip")))
    return (tmp / (cls + ".dex")).read_bytes()


def payload_dex():
    return dex("com.huntress.mobile.d22.update", "Core",
               'public final class Core { public static String token() { return "%s"; } }' % TOK)


if variant in ("xor12_dex", "decoy_nearmiss"):
    key = bytes.fromhex("5ac3197e02f4b8d16e9a3c27") if variant == "xor12_dex" else bytes.fromhex("e1724bc93d0a58")
    name, asset = "assets/core.dat", bytes(b ^ key[i % len(key)] for i, b in enumerate(payload_dex()))
elif variant == "add_rev_b64_jar":
    (tmp / "jar").mkdir()
    (tmp / "jar/classes.dex").write_bytes(payload_dex())
    run("zip", "-q", "-X", str(tmp / "update.jar"), "classes.dex", cwd=tmp / "jar")
    added = bytes((b + 0x5A) & 255 for b in (tmp / "update.jar").read_bytes())  # c = p + 0x5a
    name, asset = "assets/update.txt", run("base64", "-w", "76", data=added[::-1])  # reversed, then base64 text
elif variant == "rolling_elf":
    (tmp / "n.c").write_text('__attribute__((used)) const char kTok[] = "%s";\nint jni_ok(void){return 1;}\n' % TOK)
    run("gcc", "-shared", "-fPIC", "-O0", "-o", str(tmp / "libcore.so"), str(tmp / "n.c"))
    name = "res/raw/blob.bin"
    asset = bytes(b ^ ((0x37 + i) & 255) for i, b in enumerate((tmp / "libcore.so").read_bytes()))  # c = p ^ (0x37+i)
elif variant == "gzip_sub_sqlite":
    run("sqlite3", str(tmp / "s.db"), "CREATE TABLE secrets(name TEXT, value TEXT);"
        "INSERT INTO secrets VALUES('session','%s');" % TOK)
    key = bytes.fromhex("13a7c45e9b")
    subbed = bytes((b - key[i % 5]) & 255 for i, b in enumerate((tmp / "s.db").read_bytes()))  # c = p - key
    name, asset = "assets/store.bin.gz", run("gzip", "-n", "-9", "-c", data=subbed)
outer = dex("com.huntress.mobile.d22", "Main", """
public final class Main {
  public static String hint() { return "the update ships wrapped; only its magic is known"; }
}""")
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "wrapped", "hint": "the next stage is not stored plain"}')
    z.writestr("classes.dex", outer)
    z.writestr(name, asset)
    if variant == "decoy_nearmiss":
        z.writestr("assets/noise.bin", os.urandom(4096))
shutil.rmtree(tmp)
print(out)
