"""APK manifest references resolved through resources.arsc (the D21 'borrowed product name' flavor). D21's label was
an inline string; a variant can make android:label / android:icon a reference 0xPPTTEEEE (package / 1-based type /
0-based entry) that only resources.arsc turns into text.
resources.arsc (<androidfw/ResourceTypes.h>): RES_TABLE_TYPE 0x0002 {header, u32 packageCount} -> global string pool
0x0001 (the values) -> package chunk 0x0200 {u32 id, u16 name[128] @+12, u32 typeStrings @+268, u32 keyStrings @+276}
-> TYPE_SPEC 0x0202 / TYPE 0x0201 {u8 id, u8 flags (0x01 sparse, 0x02 offset16), u16, u32 entryCount,
u32 entriesStart, ResTable_config @+20} + entry offsets -> ResTable_entry {u16 size, u16 flags (0x01 complex,
0x08 compact), u32 key} + Res_value {u16 size, u8 0, u8 dataType, u32 data}.
Resolution prefers the default config (all-zero ResTable_config), else the first stored one (aapt badging does the
same: `application: label=` / `icon=`). Locale keys are aapt badging's (`fr`, `de-AT`; `default` = no locale).
Input: the APK zip. No AndroidManifest.xml -> "none"; no resources.arsc -> "none" for the arsc-only fields and None
(cannot answer) for an unresolvable reference; non-zip bytes -> None. Stdlib only. All fields speculative; fixtures
are aapt2-linked APKs checked with `aapt dump badging` / `aapt2 dump resources`."""
import io
import struct
import zipfile
import zlib

from ..spell import Hex

FIELDS = {
    ("apk", "application_label_resolved"): "label_resolved",
    ("apk", "app_label_resolved"): "label_resolved",
    ("apk", "label_resolved"): "label_resolved",
    ("apk", "resolved_label"): "label_resolved",
    ("apk", "resolved_application_label"): "label_resolved",
    ("apk", "application_label_default"): "label_resolved",
    ("apk", "application_label_raw"): "label_raw",
    ("apk", "app_label_raw"): "label_raw",
    ("apk", "label_raw"): "label_raw",
    ("apk", "application_label_reference"): "label_raw",
    ("apk", "label_reference"): "label_raw",
    ("apk", "app_label_locales"): "label_locales",
    ("apk", "application_label_locales"): "label_locales",
    ("apk", "label_locales"): "label_locales",
    ("apk", "localized_labels"): "label_locales",
    ("apk", "application_labels"): "label_locales",
    ("apk", "resources_package_name"): "res_package_name",
    ("apk", "resource_package_name"): "res_package_name",
    ("apk", "arsc_package_name"): "res_package_name",
    ("apk", "resources_arsc_package_name"): "res_package_name",
    ("apk", "res_table_package_name"): "res_package_name",
    ("apk", "resource_table_package_name"): "res_package_name",
    ("apk", "resources_package_id_hex"): "res_package_id",
    ("apk", "resource_package_id_hex"): "res_package_id",
    ("apk", "arsc_package_id_hex"): "res_package_id",
    ("apk", "resources_package_id"): "res_package_id",
    ("apk", "resources_package_matches_manifest"): "res_package_matches",
    ("apk", "resources_package_mismatch"): "res_package_mismatch",
    ("apk", "package_name_mismatch"): "res_package_mismatch",
    ("apk", "icon_path"): "icon_path",
    ("apk", "application_icon_path"): "icon_path",
    ("apk", "app_icon_path"): "icon_path",
    ("apk", "application_icon"): "icon_path",
    ("apk", "app_icon"): "icon_path",
    ("apk", "icon"): "icon_path",
    ("apk", "icon_resolved"): "icon_path",
    ("apk", "application_icon_raw"): "icon_raw",
    ("apk", "icon_raw"): "icon_raw",
    ("apk", "icon_reference"): "icon_raw",
    ("android", "application_label_resolved"): "label_resolved",
    ("android", "app_label_resolved"): "label_resolved",
    ("android", "label_resolved"): "label_resolved",
    ("android", "resolved_label"): "label_resolved",
    ("android", "resolved_application_label"): "label_resolved",
    ("android", "application_label_default"): "label_resolved",
    ("android", "application_label_raw"): "label_raw",
    ("android", "app_label_raw"): "label_raw",
    ("android", "label_raw"): "label_raw",
    ("android", "application_label_reference"): "label_raw",
    ("android", "label_reference"): "label_raw",
    ("android", "app_label_locales"): "label_locales",
    ("android", "application_label_locales"): "label_locales",
    ("android", "label_locales"): "label_locales",
    ("android", "localized_labels"): "label_locales",
    ("android", "application_labels"): "label_locales",
    ("android", "resources_package_name"): "res_package_name",
    ("android", "resource_package_name"): "res_package_name",
    ("android", "arsc_package_name"): "res_package_name",
    ("android", "resources_arsc_package_name"): "res_package_name",
    ("android", "res_table_package_name"): "res_package_name",
    ("android", "resource_table_package_name"): "res_package_name",
    ("android", "resources_package_id_hex"): "res_package_id",
    ("android", "resource_package_id_hex"): "res_package_id",
    ("android", "arsc_package_id_hex"): "res_package_id",
    ("android", "resources_package_id"): "res_package_id",
    ("android", "resources_package_matches_manifest"): "res_package_matches",
    ("android", "resources_package_mismatch"): "res_package_mismatch",
    ("android", "package_name_mismatch"): "res_package_mismatch",
    ("android", "icon_path"): "icon_path",
    ("android", "application_icon_path"): "icon_path",
    ("android", "app_icon_path"): "icon_path",
    ("android", "application_icon"): "icon_path",
    ("android", "app_icon"): "icon_path",
    ("android", "icon"): "icon_path",
    ("android", "icon_resolved"): "icon_path",
    ("android", "application_icon_raw"): "icon_raw",
    ("android", "icon_raw"): "icon_raw",
    ("android", "icon_reference"): "icon_raw",
    ("mobile", "application_label_resolved"): "label_resolved",
    ("mobile", "app_label_resolved"): "label_resolved",
    ("mobile", "label_resolved"): "label_resolved",
    ("mobile", "resolved_label"): "label_resolved",
    ("mobile", "resolved_application_label"): "label_resolved",
    ("mobile", "application_label_default"): "label_resolved",
    ("mobile", "application_label_raw"): "label_raw",
    ("mobile", "app_label_raw"): "label_raw",
    ("mobile", "label_raw"): "label_raw",
    ("mobile", "application_label_reference"): "label_raw",
    ("mobile", "label_reference"): "label_raw",
    ("mobile", "app_label_locales"): "label_locales",
    ("mobile", "application_label_locales"): "label_locales",
    ("mobile", "label_locales"): "label_locales",
    ("mobile", "localized_labels"): "label_locales",
    ("mobile", "application_labels"): "label_locales",
    ("mobile", "resources_package_name"): "res_package_name",
    ("mobile", "resource_package_name"): "res_package_name",
    ("mobile", "arsc_package_name"): "res_package_name",
    ("mobile", "resources_arsc_package_name"): "res_package_name",
    ("mobile", "res_table_package_name"): "res_package_name",
    ("mobile", "resource_table_package_name"): "res_package_name",
    ("mobile", "resources_package_id_hex"): "res_package_id",
    ("mobile", "resource_package_id_hex"): "res_package_id",
    ("mobile", "arsc_package_id_hex"): "res_package_id",
    ("mobile", "resources_package_id"): "res_package_id",
    ("mobile", "resources_package_matches_manifest"): "res_package_matches",
    ("mobile", "resources_package_mismatch"): "res_package_mismatch",
    ("mobile", "package_name_mismatch"): "res_package_mismatch",
    ("mobile", "icon_path"): "icon_path",
    ("mobile", "application_icon_path"): "icon_path",
    ("mobile", "app_icon_path"): "icon_path",
    ("mobile", "application_icon"): "icon_path",
    ("mobile", "app_icon"): "icon_path",
    ("mobile", "icon"): "icon_path",
    ("mobile", "icon_resolved"): "icon_path",
    ("mobile", "application_icon_raw"): "icon_raw",
    ("mobile", "icon_raw"): "icon_raw",
    ("mobile", "icon_reference"): "icon_raw",
}

_ZIP = (zipfile.BadZipFile, OSError, RuntimeError, ValueError, NotImplementedError, EOFError, zlib.error)
_PARSE = (struct.error, IndexError, ValueError, UnicodeDecodeError)
_LABEL, _ICON = 0x01010001, 0x01010002          # android.R.attr.label / .icon
_REF, _DYN_REF, _STRING = 0x01, 0x07, 0x03
_MAX = 64 << 20


def _pool(b, off):
    """Strings of the RES_STRING_POOL chunk at off (flag 0x100 = UTF-8, else UTF-16LE)."""
    _t, hs, _sz, n, _st, flags, s_start = struct.unpack_from("<HHIIIII", b, off)
    utf8, base, out = bool(flags & 0x100), off + s_start, []
    for i in range(min(n, max(0, (len(b) - off - hs) // 4))):
        try:
            p = base + struct.unpack_from("<I", b, off + hs + 4 * i)[0]
            if utf8:
                p += 2 if b[p] & 0x80 else 1                     # skip the UTF-16 char count
                ln, p = (((b[p] & 0x7F) << 8) | b[p + 1], p + 2) if b[p] & 0x80 else (b[p], p + 1)
                out.append(b[p:p + ln].decode("utf-8", "replace"))
            else:
                ln = struct.unpack_from("<H", b, p)[0]
                if ln & 0x8000:
                    ln, p = ((ln & 0x7FFF) << 16) | struct.unpack_from("<H", b, p + 2)[0], p + 4
                else:
                    p += 2
                out.append(b[p:p + 2 * ln].decode("utf-16-le", "replace"))
        except _PARSE:
            out.append("")
    return out


def _app_attrs(axml):
    """({'label': (raw, type, data), 'icon': ...}, manifest package) from a binary AndroidManifest.xml, or None."""
    b = axml
    if len(b) < 8 or struct.unpack_from("<H", b, 0)[0] != 0x0003:
        return None
    off, strings, rmap, out, pkg = struct.unpack_from("<H", b, 2)[0], [], [], {}, None
    s = lambda i: strings[i] if 0 <= i < len(strings) else None  # noqa: E731
    while off + 8 <= len(b):
        t, hs, sz = struct.unpack_from("<HHI", b, off)
        if sz < 8:
            break
        if t == 0x0001:
            strings = _pool(b, off)
        elif t == 0x0180:
            rmap = list(struct.unpack_from("<%dI" % ((sz - hs) // 4), b, off + hs))
        elif t == 0x0102:
            ext = off + hs
            _ns, name, a_start, a_size, a_count = struct.unpack_from("<IIHHH", b, ext)
            tag, attrs = s(name), []
            for i in range(a_count):
                a = ext + a_start + i * (a_size or 20)
                if a + 20 > len(b):
                    break
                _ans, an, raw, _vs, _r0, dt, dv = struct.unpack_from("<IIIHBBI", b, a)
                attrs.append((s(an), rmap[an] if an < len(rmap) else None,
                              (None if raw == 0xFFFFFFFF else s(raw), dt, dv)))
            if tag == "manifest" and pkg is None:
                pkg = next((v[0] for n, _r, v in attrs if n == "package"), None)
            elif tag == "application":
                for key, rid in (("label", _LABEL), ("icon", _ICON)):
                    v = next((v for _n, r, v in attrs if r == rid), None)
                    out[key] = v if v is not None else next((v for n, _r, v in attrs if n == key), None)
                return out, pkg
        off += sz
    return {}, pkg


def _locale(cfg):
    """aapt-badging locale of a ResTable_config ('' = no locale; 'fr', 'de-AT'; packed 3-letter codes unpacked)."""
    if len(cfg) < 12:
        return ""

    def unpack(two, base):
        if not two[0]:
            return ""
        if two[0] & 0x80:
            return "".join(chr(base + c) for c in (two[1] & 0x1F, ((two[1] & 0xE0) >> 5) | ((two[0] & 0x03) << 3),
                                                   (two[0] & 0x7C) >> 2))
        return two.decode("latin-1").rstrip("\0")
    lang, region = unpack(cfg[8:10], ord("a")), unpack(cfg[10:12], ord("0"))
    return lang + ("-" + region if lang and region else "")


class _Table:
    """Parsed resources.arsc: global pool + {package id: (name, [type strings], [(type id, config, offsets...)])}."""

    def __init__(self, b):
        t, hs, _sz, _n = struct.unpack_from("<HHII", b, 0)
        if t != 0x0002:
            raise ValueError("not a ResTable")
        self.b, self.values, self.packages = b, [], []
        off = hs
        while off + 8 <= len(b):
            t, phs, sz = struct.unpack_from("<HHI", b, off)
            if sz < 8:
                break
            if t == 0x0001 and not self.values:
                self.values = _pool(b, off)
            elif t == 0x0200:
                self.packages.append(self._package(off, phs, sz))
            off += sz

    def _package(self, off, hs, size):
        b = self.b
        pid = struct.unpack_from("<I", b, off + 8)[0]
        name = b[off + 12:off + 12 + 256].decode("utf-16-le", "replace").split("\0", 1)[0]
        tstr_off = struct.unpack_from("<I", b, off + 268)[0]
        types = _pool(b, off + tstr_off) if tstr_off and off + tstr_off + 28 <= len(b) else []
        chunks, c, end = [], off + hs, min(off + size, len(b))
        while c + 8 <= end:
            t, chs, sz = struct.unpack_from("<HHI", b, c)
            if sz < 8:
                break
            if t == 0x0201:
                chunks.append((c, chs))
            c += sz
        return pid, name, types, chunks

    def _entry(self, c, hs, idx):
        """Res_value (dataType, data) of entry idx in the TYPE chunk at c, or None (absent / complex / bad)."""
        b = self.b
        flags, count, start = b[c + 9], *struct.unpack_from("<II", b, c + 12)
        tab = c + hs
        if flags & 0x01:                                     # sparse: {u16 idx, u16 offset/4}
            o = next((struct.unpack_from("<H", b, tab + 4 * i + 2)[0] * 4 for i in range(count)
                      if struct.unpack_from("<H", b, tab + 4 * i)[0] == idx), None)
        elif idx >= count:
            return None
        elif flags & 0x02:                                   # offset16: u16 offset/4, 0xffff = no entry
            o = struct.unpack_from("<H", b, tab + 2 * idx)[0]
            o = None if o == 0xFFFF else o * 4
        else:
            o = struct.unpack_from("<I", b, tab + 4 * idx)[0]
            o = None if o == 0xFFFFFFFF else o
        if o is None:
            return None
        e = c + start + o
        esize, eflags = struct.unpack_from("<HH", b, e)
        if eflags & 0x08:                                    # compact entry: dataType in the flags' high byte
            return eflags >> 8, struct.unpack_from("<I", b, e + 4)[0]
        if eflags & 0x01:                                    # complex (bag) entry: no single value
            return None
        _vs, _r0, dt, dv = struct.unpack_from("<HBBI", b, e + esize)
        return dt, dv

    def lookup(self, ref):
        """[(locale, config is default, (dataType, data))] for resource id ref, stored config order."""
        pid, tid, idx = ref >> 24, (ref >> 16) & 0xFF, ref & 0xFFFF
        pk = [p for p in self.packages if p[0] == pid] or (self.packages[:1] if pid == 0x7F else [])
        out = []
        for _pid, _name, _types, chunks in pk[:1]:
            for c, hs in chunks:
                if self.b[c + 8] != tid:
                    continue
                csize = struct.unpack_from("<I", self.b, c + 20)[0]
                cfg = self.b[c + 20:c + 20 + max(4, min(csize, 256))]
                v = self._entry(c, hs, idx)
                if v is not None:
                    out.append((_locale(cfg), not any(cfg[4:]), v))
        return out

    def text(self, v, locale="", depth=0):
        """Display text of a Res_value, following references up to 8 hops; each hop picks the config of `locale`,
        else the default config, else the first stored one. None if unresolvable."""
        dt, dv = v
        if dt == _STRING:
            return self.values[dv] if dv < len(self.values) else None
        if dt in (_REF, _DYN_REF):
            if depth >= 8 or not dv:
                return None
            hits = self.lookup(dv)
            best = next((h for h in hits if locale and h[0] == locale), None) or \
                next((h for h in hits if h[1]), hits[0] if hits else None)
            return self.text(best[2], locale, depth + 1) if best else None
        if dt == 0x12:
            return "true" if dv else "false"
        if dt == 0x10:
            return str(dv - (1 << 32) if dv & 0x80000000 else dv)
        return str(dv)

    def locales(self, v, depth=0, out=None):
        """Locales of every config met along v's reference chain, first-seen (stored) order."""
        out = [] if out is None else out
        if v[0] in (_REF, _DYN_REF) and depth < 8 and v[1]:
            for loc, _d, val in self.lookup(v[1]):
                if loc not in out:
                    out.append(loc)
                self.locales(val, depth + 1, out)
        return out


def _load(data):
    """(app attrs dict, manifest package, _Table or None) of an APK; "none" = zip without a binary manifest;
    None = not an APK."""
    if data is None:
        return None
    b = bytes(data)
    if b[:2] != b"PK":
        return None
    try:
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            names = set(z.namelist())
            if "AndroidManifest.xml" not in names:
                return "none"
            if z.getinfo("AndroidManifest.xml").file_size > _MAX:
                return None
            man = z.read("AndroidManifest.xml")
            arsc = None
            if "resources.arsc" in names and z.getinfo("resources.arsc").file_size <= _MAX:
                arsc = z.read("resources.arsc")
    except _ZIP:
        return None
    try:
        m = _app_attrs(man)
    except _PARSE:
        return None
    if m is None:
        return "none"
    table = None
    if arsc:
        try:
            table = _Table(arsc)
        except _PARSE:
            table = None
    return m[0], m[1], table


def _raw(v):
    """The manifest's stored spelling: the inline string, or `@0x7f0b0001` for a reference."""
    raw, dt, dv = v
    if raw is not None:
        return raw
    if dt in (_REF, _DYN_REF):
        return "@0x%08x" % dv
    return str(dv)


def _resolved(data, key):
    m = _load(data)
    if not isinstance(m, tuple):
        return m
    v = m[0].get(key)
    if v is None:
        return "none"
    if v[0] is not None:
        return v[0]
    if m[2] is None:
        return None
    try:
        return m[2].text(v[1:])
    except _PARSE:
        return None


def label_resolved(data, ctx):
    """android:label as shown: inline string verbatim, or the referenced string's default-config value."""
    return _resolved(data, "label")


def icon_path(data, ctx):
    """android:icon resolved to its res/... file path (default config, else the first stored one)."""
    return _resolved(data, "icon")


def _raw_attr(data, key):
    m = _load(data)
    if not isinstance(m, tuple):
        return m
    v = m[0].get(key)
    return "none" if v is None else _raw(v)


def label_raw(data, ctx):
    return _raw_attr(data, "label")


def icon_raw(data, ctx):
    return _raw_attr(data, "icon")


def label_locales(data, ctx):
    """{locale: label} over every locale of a ResTable_config met along the label's reference chain (aapt badging's
    application-label-<locale> lines; stored first-seen order, `default` = no locale); inline -> {"default": label}."""
    m = _load(data)
    if not isinstance(m, tuple):
        return m
    v = m[0].get("label")
    if v is None:
        return "none"
    if v[0] is not None:
        return {"default": v[0]}
    if m[2] is None or v[1] not in (_REF, _DYN_REF):
        return None
    out = {}
    try:
        for loc in m[2].locales(v[1:]):
            t = m[2].text(v[1:], loc)
            if t is not None:
                out.setdefault(loc or "default", t)
    except _PARSE:
        return None
    return out or None


def _pkg(data):
    m = _load(data)
    if not isinstance(m, tuple):
        return m
    if m[2] is None or not m[2].packages:
        return "none"
    return m[2].packages[0], m[1]


def res_package_name(data, ctx):
    """ResTable_package.name (UTF-16, 128 chars) of the first package -- may differ from <manifest package>."""
    p = _pkg(data)
    return p[0][1] if isinstance(p, tuple) else p


def res_package_id(data, ctx):
    p = _pkg(data)
    return Hex(p[0][0], 2) if isinstance(p, tuple) else p


def res_package_matches(data, ctx):
    p = _pkg(data)
    return (p[0][1] == p[1]) if isinstance(p, tuple) else p


def res_package_mismatch(data, ctx):
    p = _pkg(data)
    return (p[0][1] != p[1]) if isinstance(p, tuple) else p
