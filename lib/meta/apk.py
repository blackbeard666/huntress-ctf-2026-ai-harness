"""Android APK fields (GM-verified). AndroidManifest.xml in an APK is binary AXML (<androidfw/ResourceTypes.h>):
ResChunk_header {u16 type, u16 headerSize, u32 size}, file chunk RES_XML_TYPE 0x0003, then a RES_STRING_POOL_TYPE
0x0001 pool (UTF-16 or UTF-8 flag 0x100) and RES_XML_START_ELEMENT_TYPE 0x0102 nodes (ResXMLTree_attrExt: ns, name,
attributeStart, attributeSize, attributeCount, ...; each ResXMLTree_attribute 20 B: ns, name, rawValue, Res_value).
Stdlib walk first (no androguard import inside the timed window); androguard only when the walk finds no <manifest>."""
import io
import struct
import zipfile


def _pool(b, off):
    """Strings of the RES_STRING_POOL chunk at off."""
    _t, hs, _sz, n, _st, flags, s_start = struct.unpack_from("<HHIIIII", b, off)
    utf8, base, out = bool(flags & 0x100), off + s_start, []
    for i in range(n):
        p = base + struct.unpack_from("<I", b, off + hs + 4 * i)[0]
        if utf8:
            p += 2 if b[p] & 0x80 else 1               # utf16 length
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
    return out


def manifest_attr(axml, tag, attr):
    """Raw string value of `attr` on the first <tag> element of a binary AXML document (None = no such element)."""
    b = bytes(axml)
    if len(b) < 8 or struct.unpack_from("<H", b, 0)[0] != 0x0003:
        return None
    off, strings = struct.unpack_from("<H", b, 2)[0], []
    while off + 8 <= len(b):
        t, hs, sz = struct.unpack_from("<HHI", b, off)
        if sz < 8:
            break
        if t == 0x0001:
            strings = _pool(b, off)
        elif t == 0x0102 and strings:
            ext = off + hs
            _ns, name, a_start, a_size, a_count = struct.unpack_from("<IIHHH", b, ext)
            if strings[name] == tag:
                for i in range(a_count):
                    a = ext + a_start + i * (a_size or 20)
                    _ans, aname, raw = struct.unpack_from("<III", b, a)
                    if aname < len(strings) and strings[aname] == attr:
                        if raw != 0xFFFFFFFF:
                            return strings[raw]
                        dtype, data = struct.unpack_from("<xxxBI", b, a + 12)   # Res_value: size, res0, type, data
                        return strings[data] if dtype == 0x03 else str(data)
                return "none"
        off += sz
    return None


def package_name(data, ctx):
    """D21: <manifest package="..."> of the APK's AndroidManifest.xml, verbatim -- "com.huntress.arena.p08281778"
    (GM-confirmed single/TT/all 5 Mastery sets). Not a zip -> None; manifest without the attribute -> "none"."""
    if data is None or bytes(data[:2]) != b"PK":
        return None
    try:
        with zipfile.ZipFile(io.BytesIO(bytes(data))) as z:
            axml = z.read("AndroidManifest.xml")
    except (zipfile.BadZipFile, KeyError, OSError, RuntimeError, ValueError):
        return None
    try:
        v = manifest_attr(axml, "manifest", "package")
    except (struct.error, IndexError):
        v = None
    if v is not None:
        return v
    try:
        from androguard.core.apk import APK
        return APK(bytes(data), raw=True).get_package() or "none"
    except Exception:  # noqa: BLE001 - malformed / proto manifest
        return None
