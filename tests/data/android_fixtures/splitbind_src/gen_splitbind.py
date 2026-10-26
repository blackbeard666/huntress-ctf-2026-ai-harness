#!/usr/bin/env python3
"""Generate the splitbind_* fixtures (coverage atlas rows 49, 59, 83, 104: split-signature-digest-binding). A `.apks`
bundle: base.apk (v1 split puzzle `["ANS-", ""]`, signed by key A, versionCode 8) + TWO candidate feature splits that
both carry assets/huntress_split.json {part_index: 1, part}; the decoy comes FIRST in bundle order and fails one binding:
  signer   decoy split signed by key B (v1 + v2), the real one by the base's key A
  version  both signed by A; decoy versionCode 7, real one versionCode 8 + android:revisionCode 3
  pin      both signed by A, same versionCode; base classes.dex (javac + dex2jar) holds the SHA-256 hex of the real
           split's assets/huntress_split.json
  decoy    signer layout, the real split's fragment is non-hex and the decoy's a 15-hex near-miss (no token at all)
usage: gen_splitbind.py <variant> <out.zip>
Build: apktool's bundled aapt2 `link -I android-framework.jar` (split= / versionCode / revisionCode manifests), python
zipfile assets, keytool RSA keys + `apksigner sign` (v1 + v2), `zip -0 -j -X` bundle.
ORACLE (independent of lib.android): `apksigner verify --print-certs` per member (signer SHA-256), `aapt2 dump xmltree`
(versionCode), `unzip -p | sha256sum` vs `strings` of the base classes.dex; the member passing every binding fills the
slot (PackageManager rejects a split with another signer / versionCode)."""
import hashlib, json, random, re, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
PKG = "com.huntress.arena.bind" + {"signer": "1", "version": "2", "pin": "3", "decoy": "4"}[variant]
rnd = random.Random("splitbind-" + variant)
hx = lambda n: "".join(rnd.choice("0123456789abcdef") for _ in range(n))
good, bad = hx(16), hx(16)
if variant == "decoy":
    good, bad = good[:15] + "q", bad[:15]
tmp = Path(tempfile.mkdtemp(prefix="splitbind-"))
run = lambda *a, **k: subprocess.run([str(x) for x in a], check=True, **k)
run("unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2", "prebuilt/android-framework.jar",
    "-d", tmp)
(tmp / "aapt2").chmod(0o755)
for k in "AB":
    run("keytool", "-genkeypair", "-keystore", tmp / f"{k}.jks", "-storepass", "android", "-keypass", "android",
        "-alias", k, "-keyalg", "RSA", "-keysize", "2048", "-validity", "3650", "-dname", f"CN=Arena {k}, O=Huntress",
        capture_output=True)
frag_good = json.dumps({"part_index": 1, "part": good})
frag_bad = json.dumps({"part_index": 1, "part": bad})
dex = None
if variant == "pin":
    src = tmp / "src/com/huntress/arena/SplitPin.java"
    src.parent.mkdir(parents=True)
    src.write_text("package com.huntress.arena;\npublic final class SplitPin {\n  public static String expected() {\n"
                   '    return "%s";\n  }\n}\n' % hashlib.sha256(frag_good.encode()).hexdigest())
    run("javac", "--release", "8", "-nowarn", "-d", tmp / "cls", src)
    run("jar", "cf", tmp / "app.jar", "-C", tmp / "cls", ".")
    run(ROOT / "tools/dex2jar/d2j-jar2dex.sh", "-f", "-o", tmp / "app.dex", tmp / "app.jar", capture_output=True)
    dex = (tmp / "app.dex").read_bytes()
MAN = '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%s" %s>\n' \
      '  <application android:hasCode="%s"/>\n</manifest>'
dv = 7 if variant == "version" else 8
members = [  # file, manifest attrs, key, fragment
    ("base.apk", 'android:versionCode="8"', "A", None),
    ("split_arena_feature_alt.apk", f'split="arena_feature_alt" android:versionCode="{dv}" android:isFeatureSplit="true"',
     "B" if variant in ("signer", "decoy") else "A", frag_bad),
    ("split_arena_feature.apk", 'split="arena_feature" android:versionCode="8" android:revisionCode="3" '
     'android:isFeatureSplit="true"', "A", frag_good),
]
puzzle = {"schema": "huntress.mobile.puzzle.v1", "day": 27, "codec": "split", "parts": ["ANS-", ""], "order": [0, 1],
          "build": "splitbind-" + variant}
for fn, attrs, key, frag in members:
    (tmp / "AndroidManifest.xml").write_text(MAN % (PKG, attrs, "true" if fn == "base.apk" and dex else "false"))
    run(tmp / "aapt2", "link", "--manifest", tmp / "AndroidManifest.xml", "-I", tmp / "android-framework.jar",
        "-o", tmp / "raw.apk")
    with zipfile.ZipFile(tmp / "raw.apk") as zin, zipfile.ZipFile(tmp / "u.apk", "w", zipfile.ZIP_DEFLATED) as z:
        for i in zin.infolist():
            z.writestr(i, zin.read(i))
        if frag is None:
            z.writestr("assets/huntress_puzzle.json", json.dumps(puzzle))
            if dex:
                z.writestr("classes.dex", dex)
        else:
            z.writestr(zipfile.ZipInfo("assets/huntress_split.json", (2026, 10, 26, 0, 0, 0)), frag)
    (tmp / fn).unlink(missing_ok=True)
    run("apksigner", "sign", "--ks", tmp / f"{key}.jks", "--ks-pass", "pass:android", "--v1-signing-enabled", "true",
        "--v2-signing-enabled", "true", "--min-sdk-version", "21", "--out", tmp / fn, tmp / "u.apk")
out.unlink(missing_ok=True)
run("zip", "-q", "-0", "-j", "-X", out, *[tmp / f for f, *_r in members])

# --- oracle: apksigner certs, aapt2 versionCode, sha256sum vs base dex strings; the bound split fills the slot ---
ex = tmp / "ex"
run("unzip", "-q", "-o", out, "-d", ex)
def cert(m):
    o = run("apksigner", "verify", "--min-sdk-version", "21", "--print-certs", ex / m, capture_output=True, text=True).stdout
    return re.search(r"certificate SHA-256 digest: ([0-9a-f]{64})", o)[1]
def vcode(m):
    o = run(tmp / "aapt2", "dump", "xmltree", "--file", "AndroidManifest.xml", ex / m, capture_output=True, text=True).stdout
    return re.search(r"versionCode\(0x0101021b\)=(\d+)", o)[1]
base_dex = subprocess.run(["unzip", "-p", ex / "base.apk", "classes.dex"], capture_output=True).stdout
pins = set(re.findall(r"[0-9a-f]{64}", subprocess.run(["strings", "-n", "64"], input=base_dex, capture_output=True)
                       .stdout.decode()))  # a dex string_data_item keeps its ULEB128 length byte in front
bound = []
for m, *_r in members[1:]:
    sha = subprocess.run(f"unzip -p {ex / m} assets/huntress_split.json | sha256sum", shell=True, capture_output=True,
                         text=True).stdout.split()[0]
    ok = cert(m) == cert("base.apk") and vcode(m) == vcode("base.apk") and (not pins or sha in pins)
    print(m, "cert", cert(m)[:16], "vc", vcode(m), "pinned", sha in pins, "->", "BOUND" if ok else "decoy")
    if ok:
        bound.append(json.loads(subprocess.run(["unzip", "-p", ex / m, "assets/huntress_split.json"],
                                               capture_output=True, text=True).stdout)["part"])
tok = "ANS-" + bound[0] if len(bound) == 1 else None
print("ORACLE", tok if tok and re.fullmatch(r"ANS-[0-9a-fA-F]{16}", tok) else None)
