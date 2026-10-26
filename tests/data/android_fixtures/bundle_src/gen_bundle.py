#!/usr/bin/env python3
"""Generate the bundle_* fixtures (coverage atlas rows 58, 62: bundle-container-formats). Each is a multi-APK container
whose base huntress_puzzle.json is `codec: split` with empty slots filled by {part, part_index} fragments elsewhere:
  toc_opaque   bundletool .apks: toc.pb (BuildApksResult) is the only place naming the splits (opaque splits/sN.apk
               paths, manifests without split=); decoy config splits (arm64_v8a, xhdpi, fr) come FIRST in zip order
  toc_decoy    toc_opaque layout, but the toc-selected x86_64 fragment is a 5-hex near-miss -> no valid token
  xapk_obb     .xapk: manifest.json + base apk + Android/obb/<pkg>/main.7.<pkg>.obb (a zip holding the fragments)
  zip_aab      a plain outer zip holding app.aab (stored): base/ module puzzle + feature module dyn/assets fragment
usage: gen_bundle.py <variant> <out.zip>
WRITERS: toc.pb via google.protobuf dynamic messages over bundletool's commands.proto / targeting.proto field numbers;
manifests via apktool's bundled aapt2 `link` (binary) / `link --proto-format` (AAB); python zipfile layouts.
ORACLE (independent of lib.android): google.protobuf parses toc.pb back, the install set is picked from the parsed
split ids with the device table (x86_64 > x86 > arm64, smallest density >= 420 dpi, language en), `unzip -p`-style
zipfile reads of the selected fragments fill the slots; prints the token."""
import io, json, random, subprocess, sys, tempfile, zipfile
from pathlib import Path
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
rnd = random.Random("bundle-" + variant)
hx = lambda n: "".join(rnd.choice("0123456789abcdef") for _ in range(n))
PKG = "com.huntress.arena.bdl." + variant.replace("_", "")
tmp = Path(tempfile.mkdtemp())
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)


def manifest(proto=False, extra=""):
    (tmp / "AndroidManifest.xml").write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" '
                                             f'package="{PKG}"{extra}><application android:hasCode="false"/></manifest>')
    o = tmp / "m.zip"
    subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                    str(tmp / "android-framework.jar"), "-o", str(o)] + (["--proto-format"] if proto else []), check=True)
    with zipfile.ZipFile(o) as z:
        return z.read("AndroidManifest.xml")


def apk(files, extra=""):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", manifest(extra=extra))
        for k, v in files.items():
            z.writestr(k, v)
    return bio.getvalue()


def frag(i, p):
    return json.dumps({"part": p, "part_index": i})


good, bad = [hx(6), hx(5), hx(5)], [hx(6), hx(5), hx(5)]
if variant == "toc_decoy":
    good[0], bad[0] = good[0][:5], bad[0][:5] + "q"
puzzle = json.dumps({"schema": "huntress.mobile.puzzle.v1", "day": 27, "codec": "split", "parts": ["ANS-", "", "", ""],
                     "order": [0, 1, 2, 3], "build": "bundle-" + variant})

# --- toc.pb writer: bundletool commands.proto subset (field numbers as upstream) -------------------------------------
fdp = descriptor_pb2.FileDescriptorProto(name="toc.proto", package="android.bundle")
def msg(name, *fields):
    m = fdp.message_type.add(name=name)
    for fname, num, typ, label, tname in fields:
        f = m.field.add(name=fname, number=num, type=typ, label=label)
        if tname:
            f.type_name = ".android.bundle." + tname
T, L = descriptor_pb2.FieldDescriptorProto, None
S, M, B, E, I = T.TYPE_STRING, T.TYPE_MESSAGE, T.TYPE_BOOL, T.TYPE_INT32, T.TYPE_INT32
O, R = T.LABEL_OPTIONAL, T.LABEL_REPEATED
msg("Abi", ("alias", 1, E, O, None))
msg("AbiTargeting", ("value", 1, M, R, "Abi"))
msg("ScreenDensity", ("density_alias", 1, E, O, None))
msg("ScreenDensityTargeting", ("value", 1, M, R, "ScreenDensity"))
msg("LanguageTargeting", ("value", 1, S, R, None))
msg("ApkTargeting", ("abi_targeting", 1, M, O, "AbiTargeting"), ("language_targeting", 3, M, O, "LanguageTargeting"),
    ("screen_density_targeting", 4, M, O, "ScreenDensityTargeting"))
msg("SplitApkMetadata", ("split_id", 1, S, O, None), ("is_master_split", 2, B, O, None))
msg("ApkDescription", ("targeting", 1, M, O, "ApkTargeting"), ("path", 2, S, O, None),
    ("split_apk_metadata", 3, M, O, "SplitApkMetadata"))
msg("ModuleMetadata", ("name", 1, S, O, None))
msg("ApkSet", ("module_metadata", 1, M, O, "ModuleMetadata"), ("apk_description", 2, M, R, "ApkDescription"))
msg("Variant", ("apk_set", 2, M, R, "ApkSet"), ("variant_number", 3, I, O, None))
msg("BuildApksResult", ("variant", 1, M, R, "Variant"), ("package_name", 4, S, O, None))
pool = descriptor_pool.DescriptorPool()
pool.Add(fdp)
Toc = message_factory.GetMessageClass(pool.FindMessageTypeByName("android.bundle.BuildApksResult"))
ABI, DPI = {"arm64_v8a": 3, "x86_64": 5}, {"xhdpi": 6, "xxhdpi": 7}

bundle = io.BytesIO()
if variant.startswith("toc"):
    # (path, split id, targeting, fragment) -- decoys first in zip order, opaque names
    rows = [("splits/s0.apk", "config.arm64_v8a", ("abi", "arm64_v8a"), (1, bad[0])),
            ("splits/s1.apk", "config.xhdpi", ("dpi", "xhdpi"), (2, bad[1])),
            ("splits/s2.apk", "config.fr", ("lang", "fr"), (3, bad[2])),
            ("splits/s3.apk", "", None, None),
            ("splits/s4.apk", "config.x86_64", ("abi", "x86_64"), (1, good[0])),
            ("splits/s5.apk", "config.xxhdpi", ("dpi", "xxhdpi"), (2, good[1])),
            ("splits/s6.apk", "config.en", ("lang", "en"), (3, good[2]))]
    toc = Toc(package_name=PKG)
    v = toc.variant.add(variant_number=0)
    aset = v.apk_set.add()
    aset.module_metadata.name = "base"
    for path, sid, tg, _f in rows:
        d = aset.apk_description.add(path=path)
        d.split_apk_metadata.split_id = sid
        d.split_apk_metadata.is_master_split = not sid
        if tg and tg[0] == "abi":
            d.targeting.abi_targeting.value.add(alias=ABI[tg[1]])
        elif tg and tg[0] == "dpi":
            d.targeting.screen_density_targeting.value.add(density_alias=DPI[tg[1]])
        elif tg:
            d.targeting.language_targeting.value.append(tg[1])
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_STORED) as z:
        z.writestr("toc.pb", toc.SerializeToString())
        for path, sid, _tg, f in rows:
            z.writestr(path, apk({"assets/huntress_puzzle.json": puzzle} if not sid else
                                 {"assets/huntress_split.json": frag(*f)}))
elif variant == "xapk_obb":
    obb = io.BytesIO()
    with zipfile.ZipFile(obb, "w", zipfile.ZIP_STORED) as z:
        for i, p in enumerate(good, 1):
            z.writestr(f"assets/huntress_split_{i}.json", frag(i, p))
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps({"xapk_version": 2, "package_name": PKG, "version_code": "7",
                                                "split_apks": [{"file": f"{PKG}.apk", "id": "base"}],
                                                "expansions": [{"file": f"Android/obb/{PKG}/main.7.{PKG}.obb",
                                                                "install_location": "EXTERNAL_STORAGE",
                                                                "install_path": f"Android/obb/{PKG}/main.7.{PKG}.obb"}]}))
        z.writestr("icon.png", b"\x89PNG\r\n\x1a\n")
        z.writestr(f"{PKG}.apk", apk({"assets/huntress_puzzle.json": puzzle}))
        z.writestr(f"Android/obb/{PKG}/main.7.{PKG}.obb", obb.getvalue())
elif variant == "zip_aab":
    aab = io.BytesIO()
    with zipfile.ZipFile(aab, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("BundleConfig.pb", b"\x0a\x07\x0a\x05" + b"1.8.0")
        z.writestr("base/manifest/AndroidManifest.xml", manifest(proto=True))
        z.writestr("base/assets/huntress_puzzle.json", puzzle)
        z.writestr("base/assets/huntress_split.json", frag(1, good[0]))
        z.writestr("dyn/manifest/AndroidManifest.xml", manifest(proto=True, extra=' split="dyn"'))
        z.writestr("dyn/assets/huntress_split.json", json.dumps([]) if False else frag(2, good[1]))
        z.writestr("dyn/assets/more/huntress_split.json", frag(3, good[2]))
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_STORED) as z:
        z.writestr("README.txt", "release build\n")
        z.writestr("app.aab", aab.getvalue())
out.write_bytes(bundle.getvalue())

# --- oracle: re-read the written container with google.protobuf / zipfile only --------------------------------------
def jsons(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        return [json.loads(z.read(n)) for n in z.namelist() if n.endswith(".json")]
parts = None
with zipfile.ZipFile(out) as z:
    if "toc.pb" in z.namelist():
        t = Toc.FromString(z.read("toc.pb"))
        ids = {d.path: d.split_apk_metadata.split_id for v in t.variant for a in v.apk_set for d in a.apk_description}
        keep = [p for p, s in ids.items() if s in ("", "config.x86_64", "config.xxhdpi", "config.en")]
        mem = [z.read(p) for p in keep]
    elif "app.aab" in z.namelist():
        inner = zipfile.ZipFile(io.BytesIO(z.read("app.aab")))
        js = [json.loads(inner.read(n)) for n in inner.namelist() if n.endswith(".json")]
        mem = None
    else:
        mem = [z.read(n) for n in z.namelist() if n.endswith((".apk", ".obb"))]
    js = [o for b in mem for o in jsons(b)] if mem is not None else js
pz = next(o for o in js if isinstance(o, dict) and o.get("codec") == "split")
parts = list(pz["parts"])
for o in js:
    if "part" in o:
        parts[o["part_index"]] = o["part"]
print("".join(parts[i] for i in pz["order"]))
