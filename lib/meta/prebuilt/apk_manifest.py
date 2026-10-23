"""APK AndroidManifest.xml siblings of the GM-verified D21 `apk.package_name` (lib/meta/apk.py is the reference walk).
Binary AXML (<androidfw/ResourceTypes.h>): ResChunk_header {u16 type, u16 headerSize, u32 size}; file chunk 0x0003,
string pool 0x0001 (UTF-8 flag 0x100 else UTF-16LE), resource map 0x0180 (u32 android attr id per string index),
START_ELEMENT 0x0102 / END_ELEMENT 0x0103; ResXMLTree_attribute (20 B) {ns, name, rawValue, Res_value{u16 size,
u8 res0, u8 dataType, u32 data}}. Attributes are found by android.R.attr id first, then by name (obfuscators strip the
name strings). Input: the APK zip, or a bare binary AndroidManifest.xml (fmt axml). Stdlib only (no androguard).
Absent attribute -> "none"; except debuggable (absent -> false) and allowBackup (absent -> true), the platform
defaults. Zip without AndroidManifest.xml -> "none"; non-APK/AXML bytes -> None. All fields speculative (never
GM-asked); fixtures are D05/D08/D21 GM APKs checked against `aapt dump xmltree` / `aapt dump badging`."""
import io
import struct
import zipfile
import zlib

from ..spell import Hex

FIELDS = {
    ("apk", "version_code"): "version_code",
    ("apk", "android_version_code"): "version_code",
    ("apk", "manifest_version_code"): "version_code",
    ("apk", "version_code_u32_hex"): "version_code_hex",
    ("apk", "version_name"): "version_name",
    ("apk", "android_version_name"): "version_name",
    ("apk", "manifest_version_name"): "version_name",
    ("apk", "min_sdk_version"): "min_sdk",
    ("apk", "min_sdk"): "min_sdk",
    ("apk", "sdk_version"): "min_sdk",
    ("apk", "uses_sdk_min_sdk_version"): "min_sdk",
    ("apk", "target_sdk_version"): "target_sdk",
    ("apk", "target_sdk"): "target_sdk",
    ("apk", "uses_sdk_target_sdk_version"): "target_sdk",
    ("apk", "max_sdk_version"): "max_sdk",
    ("apk", "max_sdk"): "max_sdk",
    ("apk", "uses_sdk_max_sdk_version"): "max_sdk",
    ("apk", "compile_sdk_version"): "compile_sdk",
    ("apk", "compile_sdk_version_codename"): "compile_sdk_codename",
    ("apk", "platform_build_version_code"): "platform_build_code",
    ("apk", "platform_build_version_name"): "platform_build_name",
    ("apk", "application_label"): "application_label",
    ("apk", "app_label"): "application_label",
    ("apk", "label"): "application_label",
    ("apk", "app_name"): "application_label",
    ("apk", "application_name"): "application_name",
    ("apk", "application_class"): "application_name",
    ("apk", "application_class_name"): "application_name",
    ("apk", "main_activity"): "launcher_activity",
    ("apk", "launcher_activity"): "launcher_activity",
    ("apk", "launchable_activity"): "launcher_activity",
    ("apk", "main_activity_name"): "launcher_activity",
    ("apk", "launcher_activity_name"): "launcher_activity",
    ("apk", "activity_names"): "activity_names",
    ("apk", "activities"): "activity_names",
    ("apk", "service_names"): "service_names",
    ("apk", "services"): "service_names",
    ("apk", "receiver_names"): "receiver_names",
    ("apk", "receivers"): "receiver_names",
    ("apk", "provider_names"): "provider_names",
    ("apk", "providers"): "provider_names",
    ("apk", "provider_authorities"): "provider_authorities",
    ("apk", "activity_count"): "activity_count",
    ("apk", "service_count"): "service_count",
    ("apk", "receiver_count"): "receiver_count",
    ("apk", "provider_count"): "provider_count",
    ("apk", "exported_component_names"): "exported_components",
    ("apk", "exported_components"): "exported_components",
    ("apk", "exported_component_count"): "exported_count",
    ("apk", "uses_permissions"): "uses_permissions",
    ("apk", "permissions"): "uses_permissions",
    ("apk", "uses_permission_names"): "uses_permissions",
    ("apk", "permission_names"): "uses_permissions",
    ("apk", "requested_permissions"): "uses_permissions",
    ("apk", "uses_permissions_sorted"): "uses_permissions_sorted",
    ("apk", "permissions_sorted"): "uses_permissions_sorted",
    ("apk", "permission_count"): "permission_count",
    ("apk", "uses_permission_count"): "permission_count",
    ("apk", "debuggable"): "debuggable",
    ("apk", "is_debuggable"): "debuggable",
    ("apk", "application_debuggable"): "debuggable",
    ("apk", "allow_backup"): "allow_backup",
    ("apk", "application_allow_backup"): "allow_backup",
    ("apk", "uses_cleartext_traffic"): "cleartext",
    ("apk", "application_uses_cleartext_traffic"): "cleartext",
    ("apk", "shared_user_id"): "shared_user_id",
    ("apk", "install_location"): "install_location",
    ("apk", "app_component_factory"): "app_component_factory",
    ("apk", "application_app_component_factory"): "app_component_factory",
    ("apk", "package"): "package_name",
    ("apk", "manifest_package"): "package_name",
    ("android", "version_code"): "version_code",
    ("android", "android_version_code"): "version_code",
    ("android", "manifest_version_code"): "version_code",
    ("android", "version_code_u32_hex"): "version_code_hex",
    ("android", "version_name"): "version_name",
    ("android", "android_version_name"): "version_name",
    ("android", "manifest_version_name"): "version_name",
    ("android", "min_sdk_version"): "min_sdk",
    ("android", "min_sdk"): "min_sdk",
    ("android", "sdk_version"): "min_sdk",
    ("android", "uses_sdk_min_sdk_version"): "min_sdk",
    ("android", "target_sdk_version"): "target_sdk",
    ("android", "target_sdk"): "target_sdk",
    ("android", "uses_sdk_target_sdk_version"): "target_sdk",
    ("android", "max_sdk_version"): "max_sdk",
    ("android", "max_sdk"): "max_sdk",
    ("android", "uses_sdk_max_sdk_version"): "max_sdk",
    ("android", "compile_sdk_version"): "compile_sdk",
    ("android", "compile_sdk_version_codename"): "compile_sdk_codename",
    ("android", "platform_build_version_code"): "platform_build_code",
    ("android", "platform_build_version_name"): "platform_build_name",
    ("android", "application_label"): "application_label",
    ("android", "app_label"): "application_label",
    ("android", "label"): "application_label",
    ("android", "app_name"): "application_label",
    ("android", "application_name"): "application_name",
    ("android", "application_class"): "application_name",
    ("android", "application_class_name"): "application_name",
    ("android", "main_activity"): "launcher_activity",
    ("android", "launcher_activity"): "launcher_activity",
    ("android", "launchable_activity"): "launcher_activity",
    ("android", "main_activity_name"): "launcher_activity",
    ("android", "launcher_activity_name"): "launcher_activity",
    ("android", "activity_names"): "activity_names",
    ("android", "activities"): "activity_names",
    ("android", "service_names"): "service_names",
    ("android", "services"): "service_names",
    ("android", "receiver_names"): "receiver_names",
    ("android", "receivers"): "receiver_names",
    ("android", "provider_names"): "provider_names",
    ("android", "providers"): "provider_names",
    ("android", "provider_authorities"): "provider_authorities",
    ("android", "activity_count"): "activity_count",
    ("android", "service_count"): "service_count",
    ("android", "receiver_count"): "receiver_count",
    ("android", "provider_count"): "provider_count",
    ("android", "exported_component_names"): "exported_components",
    ("android", "exported_components"): "exported_components",
    ("android", "exported_component_count"): "exported_count",
    ("android", "uses_permissions"): "uses_permissions",
    ("android", "permissions"): "uses_permissions",
    ("android", "uses_permission_names"): "uses_permissions",
    ("android", "permission_names"): "uses_permissions",
    ("android", "requested_permissions"): "uses_permissions",
    ("android", "uses_permissions_sorted"): "uses_permissions_sorted",
    ("android", "permissions_sorted"): "uses_permissions_sorted",
    ("android", "permission_count"): "permission_count",
    ("android", "uses_permission_count"): "permission_count",
    ("android", "debuggable"): "debuggable",
    ("android", "is_debuggable"): "debuggable",
    ("android", "application_debuggable"): "debuggable",
    ("android", "allow_backup"): "allow_backup",
    ("android", "application_allow_backup"): "allow_backup",
    ("android", "uses_cleartext_traffic"): "cleartext",
    ("android", "application_uses_cleartext_traffic"): "cleartext",
    ("android", "shared_user_id"): "shared_user_id",
    ("android", "install_location"): "install_location",
    ("android", "app_component_factory"): "app_component_factory",
    ("android", "application_app_component_factory"): "app_component_factory",
    ("android", "package_name"): "package_name",
    ("android", "package"): "package_name",
    ("android", "manifest_package"): "package_name",
    ("mobile", "version_code"): "version_code",
    ("mobile", "android_version_code"): "version_code",
    ("mobile", "manifest_version_code"): "version_code",
    ("mobile", "version_code_u32_hex"): "version_code_hex",
    ("mobile", "version_name"): "version_name",
    ("mobile", "android_version_name"): "version_name",
    ("mobile", "manifest_version_name"): "version_name",
    ("mobile", "min_sdk_version"): "min_sdk",
    ("mobile", "min_sdk"): "min_sdk",
    ("mobile", "sdk_version"): "min_sdk",
    ("mobile", "uses_sdk_min_sdk_version"): "min_sdk",
    ("mobile", "target_sdk_version"): "target_sdk",
    ("mobile", "target_sdk"): "target_sdk",
    ("mobile", "uses_sdk_target_sdk_version"): "target_sdk",
    ("mobile", "max_sdk_version"): "max_sdk",
    ("mobile", "max_sdk"): "max_sdk",
    ("mobile", "uses_sdk_max_sdk_version"): "max_sdk",
    ("mobile", "compile_sdk_version"): "compile_sdk",
    ("mobile", "compile_sdk_version_codename"): "compile_sdk_codename",
    ("mobile", "platform_build_version_code"): "platform_build_code",
    ("mobile", "platform_build_version_name"): "platform_build_name",
    ("mobile", "application_label"): "application_label",
    ("mobile", "app_label"): "application_label",
    ("mobile", "label"): "application_label",
    ("mobile", "app_name"): "application_label",
    ("mobile", "application_name"): "application_name",
    ("mobile", "application_class"): "application_name",
    ("mobile", "application_class_name"): "application_name",
    ("mobile", "main_activity"): "launcher_activity",
    ("mobile", "launcher_activity"): "launcher_activity",
    ("mobile", "launchable_activity"): "launcher_activity",
    ("mobile", "main_activity_name"): "launcher_activity",
    ("mobile", "launcher_activity_name"): "launcher_activity",
    ("mobile", "activity_names"): "activity_names",
    ("mobile", "activities"): "activity_names",
    ("mobile", "service_names"): "service_names",
    ("mobile", "services"): "service_names",
    ("mobile", "receiver_names"): "receiver_names",
    ("mobile", "receivers"): "receiver_names",
    ("mobile", "provider_names"): "provider_names",
    ("mobile", "providers"): "provider_names",
    ("mobile", "provider_authorities"): "provider_authorities",
    ("mobile", "activity_count"): "activity_count",
    ("mobile", "service_count"): "service_count",
    ("mobile", "receiver_count"): "receiver_count",
    ("mobile", "provider_count"): "provider_count",
    ("mobile", "exported_component_names"): "exported_components",
    ("mobile", "exported_components"): "exported_components",
    ("mobile", "exported_component_count"): "exported_count",
    ("mobile", "uses_permissions"): "uses_permissions",
    ("mobile", "permissions"): "uses_permissions",
    ("mobile", "uses_permission_names"): "uses_permissions",
    ("mobile", "permission_names"): "uses_permissions",
    ("mobile", "requested_permissions"): "uses_permissions",
    ("mobile", "uses_permissions_sorted"): "uses_permissions_sorted",
    ("mobile", "permissions_sorted"): "uses_permissions_sorted",
    ("mobile", "permission_count"): "permission_count",
    ("mobile", "uses_permission_count"): "permission_count",
    ("mobile", "debuggable"): "debuggable",
    ("mobile", "is_debuggable"): "debuggable",
    ("mobile", "application_debuggable"): "debuggable",
    ("mobile", "allow_backup"): "allow_backup",
    ("mobile", "application_allow_backup"): "allow_backup",
    ("mobile", "uses_cleartext_traffic"): "cleartext",
    ("mobile", "application_uses_cleartext_traffic"): "cleartext",
    ("mobile", "shared_user_id"): "shared_user_id",
    ("mobile", "install_location"): "install_location",
    ("mobile", "app_component_factory"): "app_component_factory",
    ("mobile", "application_app_component_factory"): "app_component_factory",
    ("mobile", "package_name"): "package_name",
    ("mobile", "package"): "package_name",
    ("mobile", "manifest_package"): "package_name",
    ("axml", "version_code"): "version_code",
    ("axml", "android_version_code"): "version_code",
    ("axml", "manifest_version_code"): "version_code",
    ("axml", "version_code_u32_hex"): "version_code_hex",
    ("axml", "version_name"): "version_name",
    ("axml", "android_version_name"): "version_name",
    ("axml", "manifest_version_name"): "version_name",
    ("axml", "min_sdk_version"): "min_sdk",
    ("axml", "min_sdk"): "min_sdk",
    ("axml", "sdk_version"): "min_sdk",
    ("axml", "uses_sdk_min_sdk_version"): "min_sdk",
    ("axml", "target_sdk_version"): "target_sdk",
    ("axml", "target_sdk"): "target_sdk",
    ("axml", "uses_sdk_target_sdk_version"): "target_sdk",
    ("axml", "max_sdk_version"): "max_sdk",
    ("axml", "max_sdk"): "max_sdk",
    ("axml", "uses_sdk_max_sdk_version"): "max_sdk",
    ("axml", "compile_sdk_version"): "compile_sdk",
    ("axml", "compile_sdk_version_codename"): "compile_sdk_codename",
    ("axml", "platform_build_version_code"): "platform_build_code",
    ("axml", "platform_build_version_name"): "platform_build_name",
    ("axml", "application_label"): "application_label",
    ("axml", "app_label"): "application_label",
    ("axml", "label"): "application_label",
    ("axml", "app_name"): "application_label",
    ("axml", "application_name"): "application_name",
    ("axml", "application_class"): "application_name",
    ("axml", "application_class_name"): "application_name",
    ("axml", "main_activity"): "launcher_activity",
    ("axml", "launcher_activity"): "launcher_activity",
    ("axml", "launchable_activity"): "launcher_activity",
    ("axml", "main_activity_name"): "launcher_activity",
    ("axml", "launcher_activity_name"): "launcher_activity",
    ("axml", "activity_names"): "activity_names",
    ("axml", "activities"): "activity_names",
    ("axml", "service_names"): "service_names",
    ("axml", "services"): "service_names",
    ("axml", "receiver_names"): "receiver_names",
    ("axml", "receivers"): "receiver_names",
    ("axml", "provider_names"): "provider_names",
    ("axml", "providers"): "provider_names",
    ("axml", "provider_authorities"): "provider_authorities",
    ("axml", "activity_count"): "activity_count",
    ("axml", "service_count"): "service_count",
    ("axml", "receiver_count"): "receiver_count",
    ("axml", "provider_count"): "provider_count",
    ("axml", "exported_component_names"): "exported_components",
    ("axml", "exported_components"): "exported_components",
    ("axml", "exported_component_count"): "exported_count",
    ("axml", "uses_permissions"): "uses_permissions",
    ("axml", "permissions"): "uses_permissions",
    ("axml", "uses_permission_names"): "uses_permissions",
    ("axml", "permission_names"): "uses_permissions",
    ("axml", "requested_permissions"): "uses_permissions",
    ("axml", "uses_permissions_sorted"): "uses_permissions_sorted",
    ("axml", "permissions_sorted"): "uses_permissions_sorted",
    ("axml", "permission_count"): "permission_count",
    ("axml", "uses_permission_count"): "permission_count",
    ("axml", "debuggable"): "debuggable",
    ("axml", "is_debuggable"): "debuggable",
    ("axml", "application_debuggable"): "debuggable",
    ("axml", "allow_backup"): "allow_backup",
    ("axml", "application_allow_backup"): "allow_backup",
    ("axml", "uses_cleartext_traffic"): "cleartext",
    ("axml", "application_uses_cleartext_traffic"): "cleartext",
    ("axml", "shared_user_id"): "shared_user_id",
    ("axml", "install_location"): "install_location",
    ("axml", "app_component_factory"): "app_component_factory",
    ("axml", "application_app_component_factory"): "app_component_factory",
    ("axml", "package_name"): "package_name",
    ("axml", "package"): "package_name",
    ("axml", "manifest_package"): "package_name",
}


_ZIP = (zipfile.BadZipFile, KeyError, OSError, RuntimeError, ValueError, NotImplementedError, EOFError,
        zlib.error)
# android:* attribute resource ids (android.R.attr); obfuscated manifests strip/rename the attribute NAME strings but
# the resource map (chunk 0x0180) keeps the ids, so lookups go by id first, then by name.
_RID = {"versionCode": 0x0101021B, "versionName": 0x0101021C, "label": 0x01010001, "name": 0x01010003,
        "minSdkVersion": 0x0101020C, "targetSdkVersion": 0x01010270, "maxSdkVersion": 0x01010271,
        "debuggable": 0x0101000F, "allowBackup": 0x01010280, "exported": 0x01010010,
        "usesCleartextTraffic": 0x010104EC, "compileSdkVersion": 0x01010572,
        "compileSdkVersionCodename": 0x01010573, "sharedUserId": 0x0101000B, "installLocation": 0x010102B7,
        "appComponentFactory": 0x0101057A, "authorities": 0x01010018}
_INSTALL = {0: "auto", 1: "internalOnly", 2: "preferExternal"}
_COMPONENTS = ("activity", "activity-alias", "service", "receiver", "provider")


def _pool(b, off):
    """Strings of the RES_STRING_POOL chunk at off (UTF-8 flag 0x100, else UTF-16LE)."""
    _t, hs, _sz, n, _st, flags, s_start = struct.unpack_from("<HHIIIII", b, off)
    utf8, base, out = bool(flags & 0x100), off + s_start, []
    for i in range(min(n, max(0, (len(b) - off - hs) // 4))):     # a damaged count must not spin
        try:
            p = base + struct.unpack_from("<I", b, off + hs + 4 * i)[0]
            if utf8:
                p += 2 if b[p] & 0x80 else 1
                ln = b[p] & 0x7F
                if b[p] & 0x80:
                    ln, p = ((b[p] & 0x7F) << 8) | b[p + 1], p + 2
                else:
                    p += 1
                out.append(b[p:p + ln].decode("utf-8", "replace"))
            else:
                ln = struct.unpack_from("<H", b, p)[0]
                if ln & 0x8000:
                    ln, p = ((ln & 0x7FFF) << 16) | struct.unpack_from("<H", b, p + 2)[0], p + 4
                else:
                    p += 2
                out.append(b[p:p + 2 * ln].decode("utf-16-le", "replace"))
        except (struct.error, IndexError):
            out.append("")
    return out


class _El:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.children, self.parent = tag, attrs, [], parent

    def get(self, attr):
        """(raw string or None, dataType, data) of android:<attr> (by resource id, then by name), or None."""
        rid = _RID.get(attr)
        if rid is not None:
            for a in self.attrs:
                if a[1] == rid:
                    return a[2:]
        for a in self.attrs:
            if a[0] == attr:
                return a[2:]
        return None

    def iter(self):
        """Document order, iterative (a crafted deep nesting must not hit the recursion limit)."""
        stack = [self]
        while stack:
            el = stack.pop()
            yield el
            stack.extend(reversed(el.children))


def _tree(axml):
    """Root _El of a binary AXML document (ResXMLTree), or None."""
    b = bytes(axml)
    if len(b) < 8 or struct.unpack_from("<H", b, 0)[0] != 0x0003:
        return None
    off, strings, rmap, root, cur = struct.unpack_from("<H", b, 2)[0], [], [], None, None
    s = lambda i: strings[i] if 0 <= i < len(strings) else None  # noqa: E731
    while off + 8 <= len(b):
        t, hs, sz = struct.unpack_from("<HHI", b, off)
        if sz < 8:
            break
        if t == 0x0001:
            strings = _pool(b, off)
        elif t == 0x0180:                       # RES_XML_RESOURCE_MAP_TYPE: u32 attr res id per string index
            rmap = list(struct.unpack_from("<%dI" % ((sz - hs) // 4), b, off + hs))
        elif t == 0x0102:                       # START_ELEMENT
            ext = off + hs
            _ns, name, a_start, a_size, a_count = struct.unpack_from("<IIHHH", b, ext)
            attrs = []
            for i in range(a_count):
                a = ext + a_start + i * (a_size or 20)
                if a + 20 > len(b):
                    break
                _ans, an, raw, _vs, _r0, dt, dv = struct.unpack_from("<IIIHBBI", b, a)
                attrs.append((s(an), rmap[an] if an < len(rmap) else None,
                              None if raw == 0xFFFFFFFF else s(raw), dt, dv))
            el = _El(s(name), attrs, cur)
            if cur is None:
                root = root or el
            else:
                cur.children.append(el)
            cur = el
        elif t == 0x0103 and cur is not None:   # END_ELEMENT
            cur = cur.parent
        off += sz
    return root


def _strs(v, strings=None):
    """Display text of an attribute value tuple (raw, dataType, data)."""
    raw, dt, dv = v
    if raw is not None:
        return raw
    if dt == 0x12:
        return "true" if dv else "false"
    if dt == 0x10:
        return str(dv - (1 << 32) if dv & 0x80000000 else dv)
    if dt == 0x01:
        return "@0x%08x" % dv
    return str(dv)


def _manifest(data):
    """(root <manifest> _El, package) of an APK (zip) or a bare binary AndroidManifest.xml; "none" = a zip without
    a binary manifest (renamed impostor); None = not an APK/AXML at all."""
    if data is None:
        return None
    b = bytes(data)
    if b[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                b = z.read("AndroidManifest.xml")
        except KeyError:
            return "none"
        except _ZIP:
            return None
    try:
        root = _tree(b)
    except (struct.error, IndexError, ValueError):
        return None
    if root is None or root.tag != "manifest":
        return "none" if b[:2] == b"\x03\x00" else None
    pk = root.get("package")
    return root, (_strs(pk) if pk else "")


def _first(root, tag):
    for el in root.iter():
        if el.tag == tag:
            return el
    return None


def _expand(name, pkg):
    """Android class-name expansion: leading '.' -> package + name; no dot at all -> package + '.' + name."""
    if not name:
        return name
    if name.startswith("."):
        return pkg + name
    if "." not in name and pkg:
        return pkg + "." + name
    return name


def _attr(data, tag, attr, conv=None):
    m = _manifest(data)
    if not isinstance(m, tuple):
        return m
    el = m[0] if tag == "manifest" else _first(m[0], tag)
    v = el.get(attr) if el is not None else None
    if v is None:
        return "none"
    return conv(v, m[1]) if conv else _strs(v)


def _int(v, _pkg=None):
    raw, dt, dv = v
    if raw is not None:
        try:
            return int(raw.strip(), 0)
        except ValueError:
            return raw.strip()       # e.g. a preview codename minSdkVersion="P"
    return dv - (1 << 32) if dt == 0x10 and dv & 0x80000000 else dv


def _bool(v):
    raw, dt, dv = v
    if raw is not None:
        return raw.strip().lower() == "true"
    return bool(dv)


def _named(v, pkg):
    t = _strs(v)
    return _expand(t, pkg) if not t.startswith("@") else None


# --- manifest ---------------------------------------------------------------------------------------------------
def package_name(data, ctx):
    """<manifest package=> verbatim (same value as the GM-verified apk.package_name, for the alias formats)."""
    return _attr(data, "manifest", "package")


def version_code(data, ctx):
    """android:versionCode (TYPE_INT_DEC data, or the rawValue string) as a base-10 int."""
    return _attr(data, "manifest", "versionCode", _int)


def version_code_hex(data, ctx):
    v = version_code(data, ctx)
    return Hex(v & 0xFFFFFFFF, 8) if isinstance(v, int) else v


def version_name(data, ctx):
    return _attr(data, "manifest", "versionName")


def compile_sdk(data, ctx):
    return _attr(data, "manifest", "compileSdkVersion", _int)


def compile_sdk_codename(data, ctx):
    return _attr(data, "manifest", "compileSdkVersionCodename")


def platform_build_code(data, ctx):
    """platformBuildVersionCode (aapt-added, no android: namespace / res id) -- int."""
    return _attr(data, "manifest", "platformBuildVersionCode", _int)


def platform_build_name(data, ctx):
    return _attr(data, "manifest", "platformBuildVersionName")


def shared_user_id(data, ctx):
    return _attr(data, "manifest", "sharedUserId")


def install_location(data, ctx):
    """android:installLocation enum name (auto / internalOnly / preferExternal); absent -> "none"."""
    def conv(v, _pkg):
        n = _int(v)
        return _INSTALL.get(n, str(n)) if isinstance(n, int) else n
    return _attr(data, "manifest", "installLocation", conv)


# --- uses-sdk: absent attribute -> "none" (aapt badging would print its implied default instead) -----------------
def min_sdk(data, ctx):
    return _attr(data, "uses-sdk", "minSdkVersion", _int)


def target_sdk(data, ctx):
    return _attr(data, "uses-sdk", "targetSdkVersion", _int)


def max_sdk(data, ctx):
    return _attr(data, "uses-sdk", "maxSdkVersion", _int)


# --- application ------------------------------------------------------------------------------------------------
def application_label(data, ctx):
    """Inline android:label string; a resource reference (@0x7f......, needs resources.arsc) -> None (cannot answer)."""
    def conv(v, _pkg):
        return None if v[0] is None and v[1] == 0x01 else _strs(v)
    return _attr(data, "application", "label", conv)


def application_name(data, ctx):
    return _attr(data, "application", "name", _named)


def app_component_factory(data, ctx):
    return _attr(data, "application", "appComponentFactory", _named)


def debuggable(data, ctx):
    """android:debuggable; absent -> false (the platform default)."""
    v = _attr(data, "application", "debuggable", lambda v, _p: _bool(v))
    return False if v == "none" and _manifest(data) not in (None, "none") else v


def allow_backup(data, ctx):
    """android:allowBackup; absent -> true (the platform default)."""
    v = _attr(data, "application", "allowBackup", lambda v, _p: _bool(v))
    return True if v == "none" and _manifest(data) not in (None, "none") else v


def cleartext(data, ctx):
    """android:usesCleartextTraffic; absent -> "none" (its default depends on targetSdk / network-security-config)."""
    return _attr(data, "application", "usesCleartextTraffic", lambda v, _p: _bool(v))


# --- components -------------------------------------------------------------------------------------------------
def _components(data, tags):
    """[(el, expanded name)] of the <application> components with tag in `tags`, manifest order; or the sentinel."""
    m = _manifest(data)
    if not isinstance(m, tuple):
        return m
    app = _first(m[0], "application")
    out = []
    for el in (app.children if app is not None else ()):
        if el.tag in tags:
            v = el.get("name")
            out.append((el, _expand(_strs(v), m[1]) if v else None))
    return out


def _names(data, tags):
    c = _components(data, tags)
    return [n for _e, n in c if n] if isinstance(c, list) else c


def _count(data, tags):
    c = _components(data, tags)
    return len(c) if isinstance(c, list) else c


def activity_names(data, ctx):
    return _names(data, ("activity",))


def service_names(data, ctx):
    return _names(data, ("service",))


def receiver_names(data, ctx):
    return _names(data, ("receiver",))


def provider_names(data, ctx):
    return _names(data, ("provider",))


def activity_count(data, ctx):
    return _count(data, ("activity",))


def service_count(data, ctx):
    return _count(data, ("service",))


def receiver_count(data, ctx):
    return _count(data, ("receiver",))


def provider_count(data, ctx):
    return _count(data, ("provider",))


def provider_authorities(data, ctx):
    c = _components(data, ("provider",))
    if not isinstance(c, list):
        return c
    return [_strs(e.get("authorities")) for e, _n in c if e.get("authorities")]


def _exported(data):
    """Components exported explicitly (android:exported=true) or implicitly (no android:exported + an
    <intent-filter>, the pre-Android-12 rule), manifest order."""
    c = _components(data, _COMPONENTS)
    if not isinstance(c, list):
        return c
    out = []
    for el, n in c:
        v = el.get("exported")
        if n and (_bool(v) if v is not None else any(k.tag == "intent-filter" for k in el.children)):
            out.append(n)
    return out


def exported_components(data, ctx):
    return _exported(data)


def exported_count(data, ctx):
    v = _exported(data)
    return len(v) if isinstance(v, list) else v


def launcher_activity(data, ctx):
    """First activity / activity-alias whose intent-filter has action MAIN + category LAUNCHER (expanded FQCN)."""
    c = _components(data, ("activity", "activity-alias"))
    if not isinstance(c, list):
        return c
    for el, n in c:
        for f in el.children:
            if f.tag != "intent-filter":
                continue
            acts = {_strs(k.get("name")) for k in f.children if k.tag == "action" and k.get("name")}
            cats = {_strs(k.get("name")) for k in f.children if k.tag == "category" and k.get("name")}
            if "android.intent.action.MAIN" in acts and "android.intent.category.LAUNCHER" in cats and n:
                return n
    return "none"


# --- permissions ------------------------------------------------------------------------------------------------
def _perms(data):
    m = _manifest(data)
    if not isinstance(m, tuple):
        return m
    return [_strs(el.get("name")) for el in m[0].children if el.tag == "uses-permission" and el.get("name")]


def uses_permissions(data, ctx):
    return _perms(data)


def uses_permissions_sorted(data, ctx):
    p = _perms(data)
    return sorted(p) if isinstance(p, list) else p


def permission_count(data, ctx):
    p = _perms(data)
    return len(p) if isinstance(p, list) else p
