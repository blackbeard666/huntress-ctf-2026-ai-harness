#!/usr/bin/env python3
"""split-resources-arsc-overlay fixtures (coverage atlas rows 22, 61, 104).

Generator: apktool's bundled aapt2 (`compile` + `link --split <apk>:<config>` -> real config split APKs with their own
resources.arsc re-declaring base ids under xxhdpi / xhdpi / fr qualifiers; a feature split linked alone with
`--package-id 0x80 --allow-reserved-package-id`), smali -> classes.dex via `apktool b`, `zip -0 -j -X` bundle (.apks).
Oracle: `aapt2 dump resources` of every member (id -> config -> value), selection by the device table below (en-US,
420 dpi -> xxhdpi bucket per the Android density docs, sdk 34) and `unzip -p <member> res/raw/... | base64 -d`.

usage: gen_splitres.py <dpi_locale|feature_raw|decoy> <out.zip>
"""
import base64, json, random, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
rnd = random.Random("splitres-" + variant)
hx = lambda n: "".join(rnd.choice("0123456789abcdef") for _ in range(n))  # noqa: E731
PKG = "com.huntress.arena.splitres"
tmp = Path(tempfile.mkdtemp())
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
AAPT2, FW = str(tmp / "aapt2"), str(tmp / "android-framework.jar")


def xml(body):
    return f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n{body}\n</resources>\n'


def link(name, res, manifest_extra="", app_extra="", args=(), raw=None):
    d = tmp / name
    for q, body in res.items():
        (d / "res" / q).mkdir(parents=True, exist_ok=True)
        (d / "res" / q / "strings.xml").write_text(xml(body))
    for rel, data in (raw or {}).items():
        (d / "res" / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / "res" / rel).write_bytes(data)
    (d / "AndroidManifest.xml").write_text(
        f'<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{PKG}"{manifest_extra}>'
        f'<application{app_extra}/></manifest>')
    subprocess.run([AAPT2, "compile", "--dir", str(d / "res"), "-o", str(d / "res.zip")], check=True)
    subprocess.run([AAPT2, "link", "--manifest", str(d / "AndroidManifest.xml"), "-I", FW, "-o", str(d / "out.apk"),
                    str(d / "res.zip")] + list(args), check=True, cwd=d)
    return d


def dex(proof_body):
    """classes.dex of a one-class smali project (apktool b)."""
    d = tmp / "smaliproj"
    (d / "smali/com/huntress/arena/splitres").mkdir(parents=True)
    (d / "apktool.yml").write_text("version: 3.0.3\napkFileName: x.apk\nusesFramework:\n  ids:\n  - 1\nsdkInfo:\n  minSdkVersion: 24\n"
                                   "  targetSdkVersion: 34\nversionInfo:\n  versionCode: 1\n  versionName: 1.0\n")
    (d / "AndroidManifest.xml").write_text(f'<manifest xmlns:android="http://schemas.android.com/apk/res/android" '
                                           f'package="{PKG}"><application/></manifest>')
    (d / "smali/com/huntress/arena/splitres/ChallengeActivity.smali").write_text(f""".class public Lcom/huntress/arena/splitres/ChallengeActivity;
.super Landroid/app/Activity;

.method public proof()Ljava/lang/String;
    .registers 6
{proof_body}
.end method
""")
    subprocess.run(["apktool", "b", "-q", "-o", str(tmp / "dex.apk"), str(d)], check=True, capture_output=True)
    with zipfile.ZipFile(tmp / "dex.apk") as z:
        return z.read("classes.dex")


def add(apk, files):
    with zipfile.ZipFile(apk, "a") as z:
        for k, v in files.items():
            z.writestr(k, v)


GETSTR = """    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v1
    const v0, 0x7f010001
    invoke-virtual {v1, v0}, Landroid/content/res/Resources;->getString(I)Ljava/lang/String;
    move-result-object v0
    return-object v0"""
ids = tmp / "ids.txt"
ids.write_text(f"{PKG}:string/app_name = 0x7f010000\n{PKG}:string/proof_token = 0x7f010001\n"
               f"{PKG}:string/unused_token = 0x7f010002\n")
members = []  # (file name, path)
if variant in ("dpi_locale", "decoy"):
    tok = lambda: f"ANS-{hx(16)}" if variant == "dpi_locale" else f"ANS-{hx(15)}"  # noqa: E731 (decoy: 15 hex)
    v = {"default": tok(), "xxhdpi": tok(), "xhdpi": tok(), "fr": tok(), "v35": tok(), "night": tok()}
    res = {"values": f'  <string name="app_name">SplitRes</string>\n  <string name="proof_token">{v["default"]}</string>\n'
                     f'  <string name="unused_token">ANS-{hx(16)}</string>',
           "values-xxhdpi": f'  <string name="proof_token">{v["xxhdpi"]}</string>',
           "values-xhdpi": f'  <string name="proof_token">{v["xhdpi"]}</string>',
           "values-fr": f'  <string name="proof_token">{v["fr"]}</string>',
           "values-v35": f'  <string name="proof_token">{v["v35"]}</string>',
           "values-night": f'  <string name="proof_token">{v["night"]}</string>'}
    d = link("base", res, args=["--stable-ids", str(ids), "--split", "split_config.xxhdpi.apk:xxhdpi",
                                "--split", "split_config.xhdpi.apk:xhdpi", "--split", "split_config.fr.apk:fr"])
    add(d / "out.apk", {"classes.dex": dex(GETSTR),
                        "assets/huntress_puzzle.json": json.dumps({"codec": "analysis", "hint": "proof() reads the "
                                                                   "device's R.string.proof_token"})})
    members = [("base.apk", d / "out.apk")] + [(f"split_config.{q}.apk", d / f"split_config.{q}.apk")
                                               for q in ("xxhdpi", "xhdpi", "fr")]
elif variant == "feature_raw":
    real, base_decoy = f"ANS-{hx(16)}", f"ANS-{hx(16)}"
    d = link("base", {"values": '  <string name="app_name">SplitRes</string>'},
             raw={"raw/vault.bin": base_decoy.encode()}, args=["--stable-ids", str(ids)])
    f = link("feat", {"values": '  <string name="feature_label">Vault</string>'},
             manifest_extra=' split="arena_vault" android:isFeatureSplit="true"', app_extra=' android:hasCode="false"',
             raw={"raw/vault.bin": base64.b64encode(real.encode())},
             args=["--package-id", "0x80", "--allow-reserved-package-id"])
    dump = subprocess.run([AAPT2, "dump", "resources", str(f / "out.apk")], capture_output=True, text=True).stdout
    rid = int(re.search(r"resource (0x80[0-9a-f]{6}) raw/vault", dump).group(1), 16)
    add(d / "out.apk", {"classes.dex": dex(f"""    invoke-virtual {{p0}}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v1
    const v0, {rid:#x}
    invoke-virtual {{v1, v0}}, Landroid/content/res/Resources;->openRawResource(I)Ljava/io/InputStream;
    move-result-object v0
    const/4 v0, 0x0
    return-object v0""")})
    members = [("base.apk", d / "out.apk"), ("split_arena_vault.apk", f / "out.apk")]

# --- oracle: aapt2 dump resources per member, device selection, raw bytes via unzip -p ---
DENS = {"xxhdpi": 480, "xhdpi": 320}  # 420 dpi request: Android picks xxhdpi (scale down) over xhdpi
vals = []  # (member, id, name, qualifier, value)
for fn, p in members:
    cur = None
    for line in subprocess.run([AAPT2, "dump", "resources", str(p)], capture_output=True, text=True).stdout.splitlines():
        m = re.match(r"\s+resource (0x[0-9a-f]{8}) (\S+)", line)
        if m:
            cur = m.groups()
            continue
        m = re.match(r"\s+\(([^)]*)\) (?:\(file\) )?(.*?)(?: type=\S+)?$", line)
        if cur and m:
            vals.append((fn, cur[0], cur[1], m.group(1), m.group(2).strip('"')))


def ok(q):  # the device (en-US, 420 dpi, sdk 34, notnight) matches the qualifier
    return all(x in ("", "en", "xxhdpi", "xhdpi") or (x.startswith("v") and int(x[1:]) <= 34)
               for x in q.split("-"))


def rank(q):
    return ("en" in q.split("-"), max([DENS.get(x, 0) for x in q.split("-")] or [0]))


installed = {"base.apk", "split_config.xxhdpi.apk", "split_arena_vault.apk"}  # xhdpi / fr config splits not installed
want = "0x7f010001" if variant != "feature_raw" else f"{rid:#010x}"
cands = [x for x in vals if x[1] == want and x[0] in installed and ok(x[3])]
fn, _id, name, q, value = max(cands, key=lambda x: rank(x[3]))
if value.startswith("res/"):
    value = base64.b64decode(subprocess.run(["unzip", "-p", str(dict(members)[fn]), value], capture_output=True)
                             .stdout).decode()
print("oracle:", fn, name, repr(q), "->", value, file=sys.stderr)
tok = re.fullmatch(r"ANS-[0-9a-f]{16}", value)
print(value if tok else "none")
bundle = tmp / "bundle"
bundle.mkdir()
for fn, p in members:
    shutil.copy(p, bundle / fn)
out.unlink(missing_ok=True)
subprocess.run(["zip", "-0", "-j", "-X", "-q", str(out)] + [str(bundle / fn) for fn, _ in members], check=True)
shutil.rmtree(tmp)
