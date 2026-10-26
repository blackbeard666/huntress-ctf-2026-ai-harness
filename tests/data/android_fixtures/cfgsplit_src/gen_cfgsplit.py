#!/usr/bin/env python3
"""Generate the cfgsplit_* fixtures (coverage atlas rows 58, 104: split-config-device-select). A split bundle whose
base huntress_puzzle.json is `codec: split` with empty slots; ABI / density / language config splits each carry
assets/huntress_split.json {part, part_index}; only the splits the pinned emulator (x86_64 image, x86 then arm64-v8a
fallback, 420 dpi, en-US) installs hold the real fragments, the others are decoys placed FIRST in bundle order.
  abi_dpi_lang   .apks: split_config.{arm64_v8a,x86_64,xhdpi,xxhdpi,fr,en}.apk + a feature split
  xapk_fallback  .xapk (manifest.json split_apks): no x86_64 split -> config.x86 beats arm64_v8a; no xxhdpi ->
                 xhdpi (largest below 420) beats hdpi; feature_a.config.{arm64_v8a,x86} (configForSplit=feature_a)
  decoy_nearmiss abi_dpi_lang layout, the installed x86_64 fragment is non-hex and the arm64 one a 5-hex near-miss
usage: gen_cfgsplit.py <variant> <out.zip>
Build: apktool's bundled aapt2 `link -I android-framework.jar` for every member manifest (split= / configForSplit /
isFeatureSplit), python zipfile adds the assets, `zip -0 -j -X` makes the bundle.
ORACLE (independent of lib.android): `unzip` the bundle, `aapt2 dump xmltree` each member for split= / configForSplit,
pick the install set with the device table below (bundletool device-spec semantics), `unzip -p` the selected
fragments and join them into the puzzle slots."""
import json, random, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
PKG = "com.huntress.arena.cfg" + {"abi_dpi_lang": "1", "xapk_fallback": "2", "decoy_nearmiss": "3"}[variant]
rnd = random.Random(variant)
hx = lambda n: "".join(rnd.choice("0123456789ABCDEF") for _ in range(n))
good = [hx(6), hx(5), hx(5)]
bad = [hx(6), hx(5), hx(5)]
if variant == "decoy_nearmiss":
    good[0], bad[0] = good[0][:5] + "Q", bad[0][:5]
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%s"%s>
  <application android:hasCode="false"/>
</manifest>"""
if variant == "xapk_fallback":
    members = [  # file, split name, extra manifest attrs, (part_index, part) or None
        (f"{PKG}.apk", None, "", None),
        ("config.arm64_v8a.apk", "config.arm64_v8a", "", (1, bad[0])),
        ("config.x86.apk", "config.x86", "", (1, good[0])),
        ("config.hdpi.apk", "config.hdpi", "", (2, bad[1])),
        ("config.xhdpi.apk", "config.xhdpi", "", (2, good[1])),
        ("config.de.apk", "config.de", "", None),
        ("config.en.apk", "config.en", "", None),
        ("feature_a.apk", "feature_a", ' android:isFeatureSplit="true"', None),
        ("feature_a.config.arm64_v8a.apk", "feature_a.config.arm64_v8a", ' configForSplit="feature_a"', (3, bad[2])),
        ("feature_a.config.x86.apk", "feature_a.config.x86", ' configForSplit="feature_a"', (3, good[2])),
    ]
else:
    members = [
        ("base.apk", None, "", None),
        ("split_config.arm64_v8a.apk", "config.arm64_v8a", "", (1, bad[0])),
        ("split_config.x86_64.apk", "config.x86_64", "", (1, good[0])),
        ("split_config.xhdpi.apk", "config.xhdpi", "", (2, bad[1])),
        ("split_config.xxhdpi.apk", "config.xxhdpi", "", (2, good[1])),
        ("split_config.fr.apk", "config.fr", "", (3, bad[2])),
        ("split_config.en.apk", "config.en", "", (3, good[2])),
        ("split_feature_x.apk", "feature_x", ' android:isFeatureSplit="true"', None),
    ]
tmp = Path(tempfile.mkdtemp())
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
puzzle = {"schema": "huntress.mobile.puzzle.v1", "day": 27, "codec": "split", "parts": ["ANS-", "", "", ""],
          "order": [0, 1, 2, 3], "build": "cfgsplit-" + variant}
for fn, split, extra, frag in members:
    (tmp / "AndroidManifest.xml").write_text(MAN % (PKG, (f' split="{split}"' if split else "") + extra))
    subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                    str(tmp / "android-framework.jar"), "-o", str(tmp / "raw.apk")], check=True)
    with zipfile.ZipFile(tmp / "raw.apk") as zin, zipfile.ZipFile(tmp / fn, "w", zipfile.ZIP_DEFLATED) as z:
        for i in zin.infolist():
            z.writestr(i, zin.read(i))
        if split is None:
            z.writestr("assets/huntress_puzzle.json", json.dumps(puzzle))
        if frag:
            z.writestr("assets/huntress_split.json", json.dumps({"part_index": frag[0], "part": frag[1]}))
        elif split:
            z.writestr("assets/README.txt", "config split " + split)
if variant == "xapk_fallback":
    (tmp / "manifest.json").write_text(json.dumps({"xapk_version": 2, "package_name": PKG, "split_configs":
        [s for _f, s, _e, _p in members if s], "split_apks": [{"file": f, "id": s or "base"} for f, s, _e, _p in members]}))
out.unlink(missing_ok=True)
extra = [str(tmp / "manifest.json")] if variant == "xapk_fallback" else []
subprocess.run(["zip", "-q", "-0", "-j", "-X", str(out), *extra, *[str(tmp / f) for f, *_r in members]], check=True)

# --- oracle: unzip, aapt2 xmltree split names, device-table install set, unzip -p fragments ---
ex = tmp / "ex"
subprocess.run(["unzip", "-q", "-o", str(out), "-d", str(ex)], check=True)
names = [n for n in subprocess.run(["unzip", "-Z1", str(out)], check=True, capture_output=True, text=True).stdout.split()
         if n.endswith(".apk")]
ABI = ["x86_64", "x86", "arm64_v8a", "armeabi_v7a"]   # emulator x86_64 image + ARM translation
DPI = {"ldpi": 120, "mdpi": 160, "hdpi": 240, "xhdpi": 320, "xxhdpi": 480, "xxxhdpi": 640}
rows = []
for m in names:
    x = subprocess.run([str(tmp / "aapt2"), "dump", "xmltree", "--file", "AndroidManifest.xml", str(ex / m)],
                       check=True, capture_output=True, text=True).stdout
    s = re.search(r'A: split="([^"]+)"', x)
    c = re.search(r'configForSplit(?:\([^)]*\))?="([^"]*)"', x)
    rows.append((m, s[1] if s else None, c[1] if c else ""))
pick = set(m for m, s, _c in rows if not s or ".config." not in "." + s)
grp = {}
for m, s, c in rows:
    if s and ".config." in "." + s:
        q = s.split("config.")[-1]
        d = "abi" if q in ABI else "dpi" if q in DPI else "lang"
        grp.setdefault((c, d), []).append((m, q))
for (c, d), lst in grp.items():
    if d == "abi":
        b = min(ABI.index(q) for _m, q in lst); pick |= {m for m, q in lst if ABI.index(q) == b}
    elif d == "dpi":
        up = sorted((DPI[q], m) for m, q in lst if DPI[q] >= 420)
        pick.add(up[0][1] if up else max((DPI[q], m) for m, q in lst)[1])
    else:
        pick |= {m for m, q in lst if q == "en"}
slots = list(puzzle["parts"])
for m in names:
    if m in pick:
        r = subprocess.run(["unzip", "-p", str(ex / m), "assets/huntress_split.json"], capture_output=True, text=True)
        if r.returncode == 0:
            o = json.loads(r.stdout); slots[o["part_index"]] = o["part"]
v = "".join(slots)
shutil.rmtree(tmp)
print(f"installed={sorted(pick)}")
print("oracle=" + (v if re.fullmatch(r"ANS-[0-9A-F]{16}", v) else "none(" + v + ")"))
