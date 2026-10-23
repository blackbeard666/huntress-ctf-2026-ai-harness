"""Android App Bundle (.aab) and split-APK containers (.apks / .xapk / .apkm).
AAB = zip: <module>/manifest/AndroidManifest.xml in aapt2 PROTOBUF (Resources.proto XmlNode{element=1
XmlElement{namespace_declaration=1, namespace_uri=2, name=3, attribute=4 XmlAttribute{namespace_uri=1, name=2,
value=3, source=4, resource_id=5, compiled_item=6 Item{str=2 String{value=1}, raw_str=3, prim=7
Primitive{int_decimal_value=6, int_hexadecimal_value=7, boolean_value=8}}}, child=5 XmlNode}}), modules = top dirs
holding manifest/AndroidManifest.xml (zip stored order, base first only if stored first), BundleConfig.pb
BundleConfig{bundletool=1 Bundletool{version=2}}. Hand varint/length-delimited walk, no protobuf lib. A binary-AXML
manifest in the bundle slot is read with apk_manifest's walk.
Split containers = zip of *.apk (+ toc.pb for bundletool .apks; manifest.json {package_name, version_code,
version_name, split_apks[{file, id}]} for APKPure .xapk; info.json {pname, versioncode, release_version} for
APKMirror .apkm). JSON wins; else the inner APKs' binary AndroidManifest (package, `split` attr; no split attr =
"base"). Zip without the bundle manifest / without inner APKs -> "none"; non-zip -> None. All speculative; fixtures
are protobuf-library / aapt2-link built, checked with `aapt2 dump xmltree`, aapt, jq, unzip -Z1."""
import io
import json
import struct
import zipfile
import zlib

from . import apk_manifest as _am

FIELDS = {
    ("aab", "package_name"): "aab_package",
    ("aab", "package"): "aab_package",
    ("aab", "manifest_package"): "aab_package",
    ("aab", "version_code"): "aab_version_code",
    ("aab", "android_version_code"): "aab_version_code",
    ("aab", "manifest_version_code"): "aab_version_code",
    ("aab", "version_name"): "aab_version_name",
    ("aab", "android_version_name"): "aab_version_name",
    ("aab", "manifest_version_name"): "aab_version_name",
    ("aab", "min_sdk_version"): "aab_min_sdk",
    ("aab", "min_sdk"): "aab_min_sdk",
    ("aab", "uses_sdk_min_sdk_version"): "aab_min_sdk",
    ("aab", "target_sdk_version"): "aab_target_sdk",
    ("aab", "target_sdk"): "aab_target_sdk",
    ("aab", "module_names"): "aab_modules",
    ("aab", "modules"): "aab_modules",
    ("aab", "module_count"): "aab_module_count",
    ("aab", "feature_module_names"): "aab_feature_modules",
    ("aab", "bundletool_version"): "aab_bundletool",
    ("aab", "bundle_config_bundletool_version"): "aab_bundletool",
    ("aab", "bundletool"): "aab_bundletool",
    ("aab", "has_native_libs"): "aab_has_native",
    ("aab", "native_libs_present"): "aab_has_native",
    ("aab", "native_abis"): "aab_native_abis",
    ("android_bundle", "package_name"): "aab_package",
    ("android_bundle", "version_code"): "aab_version_code",
    ("android_bundle", "version_name"): "aab_version_name",
    ("android_bundle", "min_sdk_version"): "aab_min_sdk",
    ("android_bundle", "target_sdk_version"): "aab_target_sdk",
    ("android_bundle", "module_names"): "aab_modules",
    ("android_bundle", "module_count"): "aab_module_count",
    ("android_bundle", "bundletool_version"): "aab_bundletool",
    ("android_bundle", "has_native_libs"): "aab_has_native",
    ("android_bundle", "native_abis"): "aab_native_abis",
    ("apks", "package_name"): "split_package",
    ("apks", "split_names"): "split_names",
    ("apks", "apk_member_names"): "apk_members",
    ("apks", "base_apk_name"): "base_apk",
    ("apks", "apk_count"): "apk_count",
    ("apks", "split_count"): "apk_count",
    ("apks", "version_code"): "split_version_code",
    ("apks", "version_name"): "split_version_name",
    ("xapk", "package_name"): "split_package",
    ("xapk", "split_names"): "split_names",
    ("xapk", "split_apk_ids"): "split_names",
    ("xapk", "apk_member_names"): "apk_members",
    ("xapk", "base_apk_name"): "base_apk",
    ("xapk", "apk_count"): "apk_count",
    ("xapk", "split_count"): "apk_count",
    ("xapk", "version_code"): "split_version_code",
    ("xapk", "version_name"): "split_version_name",
    ("apkm", "package_name"): "split_package",
    ("apkm", "split_names"): "split_names",
    ("apkm", "apk_member_names"): "apk_members",
    ("apkm", "base_apk_name"): "base_apk",
    ("apkm", "apk_count"): "apk_count",
    ("apkm", "version_code"): "split_version_code",
    ("apkm", "version_name"): "split_version_name",
    ("split_apk", "package_name"): "split_package",
    ("split_apk", "split_names"): "split_names",
    ("split_apk", "apk_member_names"): "apk_members",
    ("split_apk", "base_apk_name"): "base_apk",
    ("split_apk", "apk_count"): "apk_count",
    ("split_apk", "version_code"): "split_version_code",
    ("split_apk", "version_name"): "split_version_name",
}

_ZIP = (zipfile.BadZipFile, KeyError, OSError, RuntimeError, ValueError, NotImplementedError, EOFError,
        zlib.error)
_ANDROID_NS = "http://schemas.android.com/apk/res/android"
_RID = {"versionCode": 0x0101021B, "versionName": 0x0101021C, "minSdkVersion": 0x0101020C,
        "targetSdkVersion": 0x01010270}


# --- protobuf wire walk -------------------------------------------------------------------------------------------
def _varint(b, p):
    v = s = 0
    while p < len(b) and s < 70:
        c = b[p]
        p += 1
        v |= (c & 0x7F) << s
        if not c & 0x80:
            return v, p
        s += 7
    raise ValueError("truncated varint")


def _fields(b):
    """[(field_number, value)] of one message: varint -> int, length-delimited -> bytes; fixed32/64 skipped."""
    out, p = [], 0
    while p < len(b):
        key, p = _varint(b, p)
        num, wt = key >> 3, key & 7
        if wt == 0:
            v, p = _varint(b, p)
        elif wt == 2:
            ln, p = _varint(b, p)
            if p + ln > len(b):
                raise ValueError("truncated field")
            v, p = b[p:p + ln], p + ln
        elif wt == 1:
            v, p = None, p + 8
        elif wt == 5:
            v, p = None, p + 4
        else:
            raise ValueError("bad wire type %d" % wt)
        out.append((num, v))
    return out


def _s(v):
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else None


def _item(b):
    """Display value of a compiled Item: String/RawString value, or Primitive int/bool."""
    for num, v in _fields(b):
        if num in (2, 3) and isinstance(v, bytes):          # str / raw_str -> {value=1}
            for n2, v2 in _fields(v):
                if n2 == 1:
                    return _s(v2)
        if num == 7 and isinstance(v, bytes):               # prim
            for n2, v2 in _fields(v):
                if n2 in (6, 7) and isinstance(v2, int):    # int_decimal / int_hexadecimal (int32 two's complement)
                    v2 &= 0xFFFFFFFF
                    return v2 - (1 << 32) if v2 & 0x80000000 else v2
                if n2 == 8 and isinstance(v2, int):
                    return bool(v2)
    return None


class _PEl:
    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag, attrs, children):
        self.tag, self.attrs, self.children = tag, attrs, children

    def get(self, name):
        """android:<name> (by resource id, then by name) or a bare <name>: the raw `value` text, else the compiled
        item."""
        rid, hit = _RID.get(name), None
        for a in self.attrs:
            if rid is not None and a["rid"] == rid:
                hit = a
                break
        if hit is None:
            hit = next((a for a in self.attrs if a["name"] == name), None)
        if hit is None:
            return None
        if hit["value"]:
            return hit["value"]
        return hit["item"]

    def first(self, tag):
        stack = [self]
        while stack:
            el = stack.pop()
            if el.tag == tag:
                return el
            stack.extend(reversed(el.children))
        return None


def _xml_node(b, depth=0):
    """XmlNode bytes -> _PEl (element nodes only), or None."""
    if depth > 64:
        return None
    for num, v in _fields(b):
        if num == 1 and isinstance(v, bytes):
            tag, attrs, kids = None, [], []
            for n2, v2 in _fields(v):
                if n2 == 3:
                    tag = _s(v2)
                elif n2 == 4 and isinstance(v2, bytes):
                    a = {"ns": None, "name": None, "value": None, "rid": None, "item": None}
                    for n3, v3 in _fields(v2):
                        if n3 == 1:
                            a["ns"] = _s(v3)
                        elif n3 == 2:
                            a["name"] = _s(v3)
                        elif n3 == 3:
                            a["value"] = _s(v3)
                        elif n3 == 5 and isinstance(v3, int):
                            a["rid"] = v3
                        elif n3 == 6 and isinstance(v3, bytes):
                            a["item"] = _item(v3)
                    attrs.append(a)
                elif n2 == 5 and isinstance(v2, bytes):
                    k = _xml_node(v2, depth + 1)
                    if k is not None:
                        kids.append(k)
            return _PEl(tag, attrs, kids)
    return None


# --- AAB ------------------------------------------------------------------------------------------------------------
def _zip_names(data):
    """(ZipFile bytes, [names in central-directory order]) or None when not a zip."""
    if data is None:
        return None
    b = bytes(data)
    if b[:2] != b"PK":
        return None
    try:
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            return b, [i.filename for i in z.infolist()]
    except _ZIP:
        return None


def _read(b, name):
    try:
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            return z.read(name)
    except _ZIP:
        return None


def _modules(names):
    out = []
    for n in names:
        parts = n.split("/")
        if len(parts) == 3 and parts[1:] == ["manifest", "AndroidManifest.xml"] and parts[0] not in out:
            out.append(parts[0])
    return out


def _aab(data):
    """(zip bytes, names, base manifest root) | "none" (zip, no bundle base manifest) | None."""
    zn = _zip_names(data)
    if zn is None:
        return None
    b, names = zn
    if "base/manifest/AndroidManifest.xml" not in names:
        return "none"
    raw = _read(b, "base/manifest/AndroidManifest.xml")
    if raw is None:
        return None
    root = None
    try:
        if raw[:2] == b"\x03\x00":                      # a binary-AXML manifest in the bundle slot
            t = _am._tree(raw)
            if t is not None and t.tag == "manifest":
                root = _AxmlWrap(t)
        else:
            root = _xml_node(raw)
    except (ValueError, struct.error, IndexError):
        root = None
    if root is None or root.tag != "manifest":
        return "none"
    return b, names, root


class _AxmlWrap:
    """apk_manifest._El seen through the _PEl interface."""
    __slots__ = ("el", "tag")

    def __init__(self, el):
        self.el, self.tag = el, el.tag

    def get(self, name):
        v = self.el.get(name)
        if v is None:
            return None
        raw, dt, dv = v
        if raw is not None:
            return raw
        return _am._int(v) if dt in (0x10, 0x11) else _am._strs(v)

    def first(self, tag):
        el = _am._first(self.el, tag)
        return _AxmlWrap(el) if el is not None else None


def _aab_attr(data, tag, name, as_int=False):
    a = _aab(data)
    if not isinstance(a, tuple):
        return a
    el = a[2] if tag == "manifest" else a[2].first(tag)
    v = el.get(name) if el is not None else None
    if v is None or v == "":
        return "none"
    if as_int and isinstance(v, str):
        try:
            return int(v.strip(), 0)
        except ValueError:
            return v.strip()                            # a preview codename minSdkVersion="UpsideDownCake"
    return v.strip() if isinstance(v, str) else v


def aab_package(data, ctx):
    return _aab_attr(data, "manifest", "package")


def aab_version_code(data, ctx):
    return _aab_attr(data, "manifest", "versionCode", True)


def aab_version_name(data, ctx):
    return _aab_attr(data, "manifest", "versionName")


def aab_min_sdk(data, ctx):
    return _aab_attr(data, "uses-sdk", "minSdkVersion", True)


def aab_target_sdk(data, ctx):
    return _aab_attr(data, "uses-sdk", "targetSdkVersion", True)


def aab_modules(data, ctx):
    """Module directories holding manifest/AndroidManifest.xml, central-directory order (no sorting)."""
    a = _aab(data)
    return _modules(a[1]) if isinstance(a, tuple) else a


def aab_module_count(data, ctx):
    m = aab_modules(data, ctx)
    return len(m) if isinstance(m, list) else m


def aab_feature_modules(data, ctx):
    m = aab_modules(data, ctx)
    return [x for x in m if x != "base"] if isinstance(m, list) else m


def aab_bundletool(data, ctx):
    """BundleConfig.pb bundletool{version=2}; no BundleConfig / no version -> "none"."""
    a = _aab(data)
    if not isinstance(a, tuple):
        return a
    raw = _read(a[0], "BundleConfig.pb") if "BundleConfig.pb" in a[1] else None
    if not raw:
        return "none"
    try:
        for num, v in _fields(raw):
            if num == 1 and isinstance(v, bytes):
                for n2, v2 in _fields(v):
                    if n2 == 2 and isinstance(v2, bytes):
                        return _s(v2).strip() or "none"
    except ValueError:
        return None
    return "none"


def _abis(names):
    out = []
    for n in names:
        p = n.split("/")
        if len(p) >= 4 and p[1] == "lib" and p[-1].endswith(".so") and p[2] not in out:
            out.append(p[2])
    return out


def aab_has_native(data, ctx):
    """Any <module>/lib/<abi>/*.so member."""
    a = _aab(data)
    return bool(_abis(a[1])) if isinstance(a, tuple) else a


def aab_native_abis(data, ctx):
    a = _aab(data)
    return _abis(a[1]) if isinstance(a, tuple) else a


# --- split-APK containers -----------------------------------------------------------------------------------------
def _split(data):
    """{b, names, apks, json} | "none" (zip without inner APKs) | None (not a zip)."""
    zn = _zip_names(data)
    if zn is None:
        return None
    b, names = zn
    apks = [n for n in names if n.lower().endswith(".apk") and not n.endswith("/")]
    js = {}
    for jn in ("manifest.json", "info.json"):
        if jn in names:
            try:
                j = json.loads((_read(b, jn) or b"").decode("utf-8-sig", "replace"))
                if isinstance(j, dict):
                    js = j
                    break
            except ValueError:
                pass
    if not apks:
        return "none"
    return {"b": b, "names": names, "apks": apks, "json": js}


def _inner(s, name):
    """(root _El, package) of an inner APK's binary manifest, or None."""
    if "_m" not in s:
        s["_m"] = {}
    if name not in s["_m"]:
        raw = _read(s["b"], name)
        m = _am._manifest(raw) if raw else None
        s["_m"][name] = m if isinstance(m, tuple) else None
    return s["_m"][name]


def _split_attr(m):
    v = m[0].get("split")
    return _am._strs(v) if v else None


def _json_splits(js):
    sp = js.get("split_apks")
    return [x for x in sp if isinstance(x, dict)] if isinstance(sp, list) else []


def _base_name(s):
    js, apks = s["json"], s["apks"]
    for x in _json_splits(js):
        if x.get("id") == "base" and x.get("file") in apks:
            return x["file"]
    pkg = js.get("package_name") or js.get("pname")
    for n in apks:
        bn = n.rsplit("/", 1)[-1]
        if bn in ("base.apk", "base-master.apk") or (pkg and bn == "%s.apk" % pkg):
            return n
    for n in apks:
        m = _inner(s, n)
        if m is not None and not _split_attr(m):
            return n
    return None


def split_package(data, ctx):
    s = _split(data)
    if not isinstance(s, dict):
        return s
    pkg = s["json"].get("package_name") or s["json"].get("pname")
    if isinstance(pkg, str) and pkg.strip():
        return pkg.strip()
    base = _base_name(s)
    m = _inner(s, base) if base else None
    return (m[1] or "none") if m else "none"


def split_names(data, ctx):
    """manifest.json split_apks[].id in stored order; else each inner APK's manifest `split` attr (none -> "base"),
    zip stored order."""
    s = _split(data)
    if not isinstance(s, dict):
        return s
    ids = [x.get("id") for x in _json_splits(s["json"]) if isinstance(x.get("id"), str)]
    if ids:
        return ids
    out = []
    for n in s["apks"]:
        m = _inner(s, n)
        if m is not None:
            out.append(_split_attr(m) or "base")
    return out or "none"


def apk_members(data, ctx):
    s = _split(data)
    return s["apks"] if isinstance(s, dict) else s


def apk_count(data, ctx):
    s = _split(data)
    return len(s["apks"]) if isinstance(s, dict) else s


def base_apk(data, ctx):
    s = _split(data)
    if not isinstance(s, dict):
        return s
    return _base_name(s) or "none"


def _split_manifest_value(data, keys, attr, as_int):
    s = _split(data)
    if not isinstance(s, dict):
        return s
    for k in keys:
        v = s["json"].get(k)
        if isinstance(v, (int, str)) and str(v).strip():
            v = str(v).strip()
            return int(v) if as_int and v.isdigit() else v
    base = _base_name(s)
    m = _inner(s, base) if base else None
    if m is None:
        return "none"
    v = m[0].get(attr)
    if v is None:
        return "none"
    return _am._int(v) if as_int else _am._strs(v)


def split_version_code(data, ctx):
    return _split_manifest_value(data, ("version_code", "versioncode"), "versionCode", True)


def split_version_name(data, ctx):
    return _split_manifest_value(data, ("version_name", "release_version"), "versionName", False)
