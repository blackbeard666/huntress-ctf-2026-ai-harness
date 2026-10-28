"""Multidex class-resolution fixtures (row 107): the answer chain spans classes.dex .. classesN.dex, and a later dex
carries a SHADOW copy of a chain class (same descriptor, different value) that PathClassLoader never loads.

javac --release 8 + d8 (tools/r8) per dex group -> classes.dex, classes2.dex, ... ; `zip` for the APK. Manifest = the
stock binary AndroidManifest.xml of skc_decoy_cbc_wrong_key.apk. Oracle: the JVM itself, `java -cp g1:g2:..:gN
com.hctf.mdx.Challenge` (classpath first-definition-wins, the same order ART resolves classes.dex, classes2.dex, ...).
Usage: python3 gen_mdx.py {split_shadow3|numeric10|literal10|decoy_shadow_only} out.apk"""
import shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
R8 = ROOT / "tools/r8/r8-8.5.35.jar"
kind, out = sys.argv[1], Path(sys.argv[2]).resolve()
tmp = Path(tempfile.mkdtemp())


def tok_arr(s, k):
    return ", ".join(str(ord(c) ^ k) for c in s)


def src(root, fqcn, body):
    p = root / (fqcn.replace(".", "/") + ".java")
    p.parent.mkdir(parents=True, exist_ok=True)
    pkg, cls = fqcn.rsplit(".", 1)
    p.write_text(f"package {pkg};\npublic class {cls} {{\n{body}\n}}\n")


def mixer(hexpart, key, via_hex=False):
    body = (f"  static final int[] E = {{ {tok_arr(hexpart, key)} }};\n"
            "  public static String build() {\n"
            f"    StringBuilder sb = new StringBuilder({'' if via_hex else chr(34) + 'ANS-' + chr(34)});\n"
            "    for (int i = 0; i < E.length; i++) sb.append((char) (E[i] ^ com.hctf.mdx.Key.K));\n")
    body += ("    return com.hctf.util.Hex.wrap(sb.toString());\n  }" if via_hex else "    return sb.toString();\n  }")
    return body


# group index (1 = classes.dex) -> {fqcn: body}
groups = {1: {"com.hctf.mdx.Challenge": "  public static String answer() { return com.hctf.lib.Mixer.build(); }\n"
                                         "  public static void main(String[] a) { System.out.println(answer()); }",
              "com.hctf.mdx.Key": "  public static int K;\n  static { K = 0x2c + 0x11; }"}}
KEY = 0x3D
if kind == "split_shadow3":
    groups[2] = {"com.hctf.lib.Mixer": mixer("9b04e7c1a35d6f28", KEY)}
    groups[3] = {"com.hctf.lib.Mixer": mixer("0f1e2d3c4b5a6978", KEY), "com.hctf.lib.Extra":
                 "  public static int n() { return 3; }"}
elif kind in ("numeric10", "literal10"):
    for g in range(3, 10):
        groups[g] = {f"com.hctf.fill.F{g}": f"  public static int f() {{ return {g}; }}"}
    if kind == "numeric10":
        groups[2] = {"com.hctf.lib.Mixer": mixer("c47a1e93b0d2f586", KEY, via_hex=True)}
        groups[7]["com.hctf.util.Hex"] = "  public static String wrap(String hex) { return \"ANS-\" + hex; }"
        groups[10] = {"com.hctf.lib.Mixer": mixer("aaaa5555bbbb6666", KEY, via_hex=True)}
    else:
        groups[1]["com.hctf.mdx.Challenge"] = (
            "  public static String answer() { return com.hctf.lib.Vault.TOKEN; }\n"
            "  public static void main(String[] a) { System.out.println(answer()); }")
        groups[2] = {"com.hctf.lib.Vault": '  public static final String TOKEN = "ANS-5e81c0d7a29b4f36";'}
        groups[10] = {"com.hctf.lib.Vault": '  public static final String TOKEN = "ANS-1234abcd5678ef90";'}
elif kind == "decoy_shadow_only":  # the loaded Mixer yields a 15-hex near miss; only the shadow copy has a token
    groups[2] = {"com.hctf.lib.Mixer": mixer("6b2f0d9e4c1a873", KEY)}
    groups[3] = {"com.hctf.lib.Mixer": mixer("e3d2c1b0a9f8e7d6", KEY)}
else:
    sys.exit(f"unknown kind {kind}")

stage = tmp / "apk"
stage.mkdir()
shutil.copy(HERE.parent / "skc_decoy_cbc_wrong_key.apk", tmp / "base.apk")
subprocess.run(["unzip", "-q", "-o", str(tmp / "base.apk"), "AndroidManifest.xml", "-d", str(stage)], check=True)
# javac: the first definition of each class is compiled on one classpath; each later (shadow) copy against it
first, cps = {}, []
for g in sorted(groups):
    for fq, body in groups[g].items():
        first.setdefault(fq, g)
cdir = {}
srcs = tmp / "src_main"
for g in sorted(groups):
    for fq, body in groups[g].items():
        if first[fq] == g:
            src(srcs, fq, body)
main_cls = tmp / "cls_main"
subprocess.run(["javac", "--release", "8", "-d", str(main_cls), *map(str, srcs.rglob("*.java"))], check=True)
for g in sorted(groups):
    gdir = tmp / f"g{g}"
    gdir.mkdir()
    sh = {fq: b for fq, b in groups[g].items() if first[fq] != g}
    if sh:
        ssrc = tmp / f"src_shadow{g}"
        for fq, b in sh.items():
            src(ssrc, fq, b)
        subprocess.run(["javac", "--release", "8", "-cp", str(main_cls), "-d", str(gdir),
                        *map(str, ssrc.rglob("*.java"))], check=True)
    for fq in groups[g]:
        if first[fq] == g:
            rel = fq.replace(".", "/") + ".class"
            (gdir / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(main_cls / rel, gdir / rel)
    cps.append(str(gdir))
    dout = tmp / f"d{g}"
    dout.mkdir()
    subprocess.run(["java", "-cp", str(R8), "com.android.tools.r8.D8", "--min-api", "21", "--output", str(dout),
                    *map(str, gdir.rglob("*.class"))], check=True)
    shutil.copy(dout / "classes.dex", stage / ("classes.dex" if g == 1 else f"classes{g}.dex"))
print("oracle classpath:", ":".join(cps))
print("jvm says:", subprocess.run(["java", "-cp", ":".join(cps), "com.hctf.mdx.Challenge"], capture_output=True,
                                  text=True).stdout.strip())
out.unlink(missing_ok=True)
names = ["AndroidManifest.xml"] + sorted((p.name for p in stage.glob("classes*.dex")), reverse=True)  # zip order != load order
subprocess.run(["zip", "-q", "-X", str(out), *names], cwd=stage, check=True)
