#!/usr/bin/env python3
"""Generate the natsplit_* fixtures (coverage atlas rows 37, 58, 104: split-native-lib-config-abi). The GM D23 Mastery
set5 native hop (Release.token() -> Util.nativeSecret03 -> static native long nativeShare(long) in libarena.so,
`codec: analysis`) repackaged as a bundletool-style .apks: base.apk = the set5 APK without lib/, the .so moved into an
ABI config split or a feature split.
  cfg_x86_64      base + split_config.arm64_v8a.apk (arm64 lib, first in bundle order, not installed on the x86_64
                  device) + split_config.x86_64.apk (x86_64 lib, extractNativeLibs=false, stored)
  feature_arm64   base + split_nativefeat.apk (isFeatureSplit, lib/arm64-v8a/ only: no x86_64 lib anywhere)
  noext_deflated  base + split_config.x86_64.apk (extractNativeLibs=false but the .so DEFLATED: not loadable in place)
                  + split_nativefeat.apk (feature, stored arm64 lib)
  decoy_renamed   base + split_config.arm64_v8a.apk whose lib exports ..._nativeShore (nativeShare unbound)
usage: gen_natsplit.py <variant> <out.zip>
Build: aapt2 link (apktool bundle) for split manifests, `zip -X` (-0 / -9 per member) for split APKs, `zip -0 -j -X`
for the bundle. Libs / base entries are copied byte-for-byte from the d23_analysis_native_bridge_* fixtures.
ORACLE (independent of lib.android): `aapt2 dump xmltree` each member (split= / isFeatureSplit / extractNativeLibs),
`unzip -Zv` for the .so compression method, device table (x86_64 > x86 > arm64_v8a; feature splits always installed;
a deflated lib under extractNativeLibs=false is not loadable), then sha256sum of the loaded .so against the source
fixture lib whose token the javac + java -Djava.library.path oracle produced (see d23_analysis_native_bridge_*.json)."""
import hashlib, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
FX = Path(__file__).resolve().parents[1]
SRC = {"x86_64": (FX / "d23_analysis_native_bridge_x86_64.apk", "lib/x86_64/libarena.so"),
       "arm64": (FX / "d23_analysis_native_bridge_arm64.apk", "lib/arm64-v8a/libarena.so"),
       "renamed": (FX / "d23_analysis_native_bridge_decoy_renamed.apk", "lib/arm64-v8a/libarena.so")}
TOKEN = {"x86_64": "ANS-FB40A37095232860", "arm64": "ANS-1F4819F1FB4F4149", "renamed": None}  # source fixtures' oracles
PKG = "com.huntress.mobile.d23"
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%s" split="%s"%s>
  <application android:hasCode="false"%s/>
</manifest>"""
# file, split name, isFeatureSplit, extractNativeLibs=false, lib source, zip level
V = {"cfg_x86_64": [("split_config.arm64_v8a.apk", "config.arm64_v8a", False, False, "arm64", "-9"),
                    ("split_config.x86_64.apk", "config.x86_64", False, True, "x86_64", "-0")],
     "feature_arm64": [("split_nativefeat.apk", "nativefeat", True, True, "arm64", "-0")],
     "noext_deflated": [("split_config.x86_64.apk", "config.x86_64", False, True, "x86_64", "-9"),
                        ("split_nativefeat.apk", "nativefeat", True, True, "arm64", "-0")],
     "decoy_renamed": [("split_config.arm64_v8a.apk", "config.arm64_v8a", False, False, "renamed", "-9")]}[variant]
tmp = Path(tempfile.mkdtemp())
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
# base.apk: the set5 APK minus lib/ (zip -d)
shutil.copy(SRC["x86_64"][0], tmp / "base.apk")
subprocess.run(["zip", "-q", "-d", str(tmp / "base.apk"), "lib/*"], check=True)
for fn, split, feat, noext, lib, lvl in V:
    d = tmp / ("m_" + fn)
    d.mkdir()
    (d / "AndroidManifest.xml").write_text(MAN % (PKG, split, ' android:isFeatureSplit="true"' if feat else "",
                                                  ' android:extractNativeLibs="false"' if noext else ""))
    subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(d / "AndroidManifest.xml"), "-I",
                    str(tmp / "android-framework.jar"), "-o", str(d / "raw.apk")], check=True)
    subprocess.run(["unzip", "-q", "-o", str(d / "raw.apk"), "AndroidManifest.xml", "-d", str(d / "x")], check=True)
    so_path = SRC[lib][1] if lib != "renamed" else "lib/arm64-v8a/libarena.so"
    (d / "x" / so_path).parent.mkdir(parents=True)
    (d / "x" / so_path).write_bytes(zipfile.ZipFile(SRC[lib][0]).read(SRC[lib][1]))
    subprocess.run(["zip", "-q", "-X", "-0", str(tmp / fn), "AndroidManifest.xml"], cwd=d / "x", check=True)
    subprocess.run(["zip", "-q", "-X", lvl, str(tmp / fn), so_path], cwd=d / "x", check=True)
out.unlink(missing_ok=True)
subprocess.run(["zip", "-q", "-0", "-j", "-X", str(out), str(tmp / "base.apk"), *[str(tmp / f) for f, *_r in V]],
               check=True)

# --- oracle: unzip, aapt2 xmltree, unzip -Zv compression, device table, sha256 of the loaded lib ---
ex = tmp / "ex"
subprocess.run(["unzip", "-q", "-o", str(out), "-d", str(ex)], check=True)
ABI = ["x86_64", "x86", "arm64-v8a", "armeabi-v7a"]
rows = []
for m in subprocess.run(["unzip", "-Z1", str(out)], check=True, capture_output=True, text=True).stdout.split():
    x = subprocess.run([str(tmp / "aapt2"), "dump", "xmltree", "--file", "AndroidManifest.xml", str(ex / m)],
                       check=True, capture_output=True, text=True).stdout
    s = re.search(r'A: split="([^"]+)"', x)
    noext = bool(re.search(r'extractNativeLibs\(0x[0-9a-f]+\)=(false|0x0|0)\b', x))
    zv = subprocess.run(["unzip", "-Zv", str(ex / m)], capture_output=True, text=True).stdout
    for blk in zv.split("Central directory entry")[1:]:
        f = re.search(r"\n\s*(lib/([^/\s]+)/\S+\.so)\s*\n", blk)
        if f:
            stored = "compression method:" in blk and re.search(r"compression method:\s+none", blk) is not None
            rows.append((m, s[1] if s else None, f[2], f[1], noext and not stored))
cfg = [r for r in rows if r[1] and r[1].startswith("config.")]
best = min((ABI.index(r[2]) for r in cfg), default=None)
installed = [r for r in rows if not (r[1] and r[1].startswith("config.")) or ABI.index(r[2]) == best]
loadable = [r for r in installed if not r[4]]
loadable.sort(key=lambda r: ABI.index(r[2]))
v = "none"
if loadable:
    m, _s, _a, so, _bad = loadable[0]
    h = hashlib.sha256(subprocess.run(["unzip", "-p", str(ex / m), so], check=True, capture_output=True).stdout).hexdigest()
    for k, (apk, path) in SRC.items():
        if hashlib.sha256(zipfile.ZipFile(apk).read(path)).hexdigest() == h:
            v = TOKEN[k] or "none"
            print(f"loaded={m}:{so} sha256={h} source={k}")
shutil.rmtree(tmp)
print(f"rows={[(r[0], r[1], r[2], 'unloadable' if r[4] else 'ok') for r in rows]}")
print("oracle=" + v)
