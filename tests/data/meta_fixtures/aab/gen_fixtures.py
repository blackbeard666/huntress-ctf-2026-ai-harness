"""Fixture generator for aab / android_bundle / apks / xapk / apkm / split_apk (run offline, NOT used by lib.meta).
Writer: google.protobuf (dynamic messages from a hand-declared subset of aapt2 Resources.proto + bundletool
config.proto) for the AAB proto manifest / BundleConfig.pb; aapt2 link for binary-AXML config splits; zipfile for
the containers. Usage: python3 gen_fixtures.py <outdir> <base_apk> <split_apk_dir>"""
import json, sys, zipfile
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

F = descriptor_pb2.FieldDescriptorProto
fdp = descriptor_pb2.FileDescriptorProto(name="r.proto", package="aapt.pb", syntax="proto3")
def msg(name, *fields):
    m = fdp.message_type.add(name=name)
    for num, fname, typ, label, tname in fields:
        f = m.field.add(name=fname, number=num, type=typ, label=label)
        if tname:
            f.type_name = ".aapt.pb." + tname
O, R = F.LABEL_OPTIONAL, F.LABEL_REPEATED
msg("Primitive", (6, "int_decimal_value", F.TYPE_INT32, O, None), (8, "boolean_value", F.TYPE_BOOL, O, None))
msg("String", (1, "value", F.TYPE_STRING, O, None))
msg("Item", (2, "str", F.TYPE_MESSAGE, O, "String"), (7, "prim", F.TYPE_MESSAGE, O, "Primitive"))
msg("XmlNamespace", (1, "prefix", F.TYPE_STRING, O, None), (2, "uri", F.TYPE_STRING, O, None))
msg("XmlAttribute", (1, "namespace_uri", F.TYPE_STRING, O, None), (2, "name", F.TYPE_STRING, O, None),
    (3, "value", F.TYPE_STRING, O, None), (5, "resource_id", F.TYPE_UINT32, O, None),
    (6, "compiled_item", F.TYPE_MESSAGE, O, "Item"))
msg("XmlElement", (1, "namespace_declaration", F.TYPE_MESSAGE, R, "XmlNamespace"),
    (2, "namespace_uri", F.TYPE_STRING, O, None), (3, "name", F.TYPE_STRING, O, None),
    (4, "attribute", F.TYPE_MESSAGE, R, "XmlAttribute"), (5, "child", F.TYPE_MESSAGE, R, "XmlNode"))
msg("XmlNode", (1, "element", F.TYPE_MESSAGE, O, "XmlElement"), (2, "text", F.TYPE_STRING, O, None))
msg("Bundletool", (2, "version", F.TYPE_STRING, O, None))
msg("BundleConfig", (1, "bundletool", F.TYPE_MESSAGE, O, "Bundletool"))
pool = descriptor_pool.DescriptorPool(); pool.Add(fdp)
M = {n: message_factory.GetMessageClass(pool.FindMessageTypeByName("aapt.pb." + n))
     for n in ("XmlNode", "BundleConfig")}
A = "http://schemas.android.com/apk/res/android"

def attr(el, name, value=None, rid=None, ival=None, sval=None, ns=A, keep_raw=True):
    a = el.attribute.add(name=name)
    if ns: a.namespace_uri = ns
    if rid: a.resource_id = rid
    if value is not None and keep_raw: a.value = value
    if ival is not None: a.compiled_item.prim.int_decimal_value = ival
    if sval is not None: a.compiled_item.str.value = sval

def manifest(pkg, vc, vn, minsdk, split=None, keep_raw=True):
    n = M["XmlNode"](); e = n.element; e.name = "manifest"
    e.namespace_declaration.add(prefix="android", uri=A)
    attr(e, "versionCode", str(vc), 0x0101021B, ival=vc, keep_raw=keep_raw)
    attr(e, "versionName", vn, 0x0101021C, sval=vn, keep_raw=keep_raw)
    attr(e, "package", pkg, ns=None)
    if split: attr(e, "split", split, ns=None)
    if minsdk is not None:
        u = e.child.add().element; u.name = "uses-sdk"
        attr(u, "minSdkVersion", str(minsdk), 0x0101020C, ival=minsdk, keep_raw=keep_raw)
        attr(u, "targetSdkVersion", "34", 0x01010270, ival=34, keep_raw=keep_raw)
    app = e.child.add().element; app.name = "application"
    return n.SerializeToString()

def bundle_config(v):
    c = M["BundleConfig"](); c.bundletool.version = v; return c.SerializeToString()

out, base_apk, sdir = sys.argv[1], open(sys.argv[2], "rb").read(), sys.argv[3]
W = lambda name, entries: _w(out + "/" + name, entries)
def _w(path, entries):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for k, v in entries:
            z.writestr(k, v)
# AAB 1: base + 2 feature modules (stored order base, onboarding, camera), native libs, bundletool 1.15.6
W("aab_full.aab", [("BundleConfig.pb", bundle_config("1.15.6")),
    ("base/manifest/AndroidManifest.xml", manifest("com.huntress.bundledemo", 4207, "3.1.4-beta", 24)),
    ("base/dex/classes.dex", b"dex\n035\0" + b"\0" * 104), ("base/resources.pb", b""),
    ("base/lib/arm64-v8a/libnative.so", b"\x7fELF" + b"\0" * 60),
    ("onboarding/manifest/AndroidManifest.xml", manifest("com.huntress.bundledemo", 4207, "3.1.4-beta", None, "onboarding")),
    ("camera/manifest/AndroidManifest.xml", manifest("com.huntress.bundledemo", 4207, "3.1.4-beta", None, "camera")),
    ("camera/dex/classes.dex", b"dex\n035\0" + b"\0" * 104),
    ("BUNDLE-METADATA/com.android.tools.build.obfuscation/proguard.map", b"# map\n")])
# AAB 2: base only, no raw `value` strings (compiled_item only), no native libs, bundletool 1.17.2
W("aab_min.aab", [("base/manifest/AndroidManifest.xml", manifest("org.example.compiledonly", 91, "9.1", 21, keep_raw=False)),
    ("base/dex/classes.dex", b"dex\n035\0" + b"\0" * 104), ("BundleConfig.pb", bundle_config("1.17.2"))])
# AAB decoy: an ordinary jar renamed .aab (no base/manifest/AndroidManifest.xml, no BundleConfig.pb)
W("aab_decoy_jar.aab", [("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n"), ("com/x/Main.class", b"\xca\xfe\xba\xbe")])
cfg = {n: open(sdir + "/" + n + ".apk", "rb").read() for n in ("config.arm64_v8a", "config.xxhdpi")}
# .apks (bundletool build-apks layout): toc.pb + splits/*.apk
W("split.apks", [("toc.pb", b"\x0a\x00"), ("splits/base-master.apk", base_apk),
    ("splits/base-arm64_v8a.apk", cfg["config.arm64_v8a"]), ("splits/base-xxhdpi.apk", cfg["config.xxhdpi"])])
# .xapk (APKPure): manifest.json + <package>.apk + config.*.apk; JSON split order differs from zip order
pkg = "com.huntress.arena.p08281778"
mj = {"xapk_version": 2, "package_name": pkg, "name": "Arena", "version_code": "1", "version_name": "1.0",
      "min_sdk_version": "23", "target_sdk_version": "23",
      "split_apks": [{"file": pkg + ".apk", "id": "base"}, {"file": "config.xxhdpi.apk", "id": "config.xxhdpi"},
                     {"file": "config.arm64_v8a.apk", "id": "config.arm64_v8a"}]}
W("bundle.xapk", [("manifest.json", json.dumps(mj, indent=2)), ("icon.png", b"\x89PNG\r\n\x1a\n"),
    ("config.arm64_v8a.apk", cfg["config.arm64_v8a"]), (pkg + ".apk", base_apk), ("config.xxhdpi.apk", cfg["config.xxhdpi"])])
# .apkm (APKMirror): info.json + base.apk + split_config.*.apk
info = {"apkm_version": 5, "app_name": "Arena", "pname": pkg, "versioncode": 1, "release_version": "1.0", "min_api": "23"}
W("bundle.apkm", [("info.json", json.dumps(info)), ("base.apk", base_apk),
    ("split_config.arm64_v8a.apk", cfg["config.arm64_v8a"]), ("icon.png", b"\x89PNG\r\n\x1a\n")])
# split decoy: a .xapk-named zip with only a readme (no inner APKs, no manifest.json)
W("decoy.xapk", [("readme.txt", "not a split bundle\n"), ("data.bin", b"\0" * 32)])
