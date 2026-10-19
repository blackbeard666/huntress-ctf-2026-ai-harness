"""AppleDouble / AppleSingle (`._name`, `__MACOSX/._name`) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout (RFC 1740, big-endian): magic u32 00051607 (AppleDouble; 00051600 = AppleSingle, same table), version u32
(00020000), 16-byte home-file-system filler ("Mac OS X        "), u16 entry count, then 12-byte entries
(id u32, offset u32, length u32; offsets from file start). Entry 2 = resource fork, 9 = Finder info: 32 bytes
FInfo/FXInfo (fdType 4cc, fdCreator 4cc, ...) then, as macOS `ditto`/Archive Utility write it, 2 pad bytes and an
`ATTR` extended-attribute header: magic, debug_tag, total_size, data_start, data_length, 3 reserved u32, flags u16,
num_attrs u16; entries at ATTR+36: offset u32 (from FILE start), length u32, flags u16, name_len u8, name (NUL
included), each entry padded to 4. Checked against two macOS-made `._` files (exiftool 13.59 "MacOS:XAttr*").
xattr_names = names in stored order (JSON list). xattr_<name> = the value as UTF-8 text (trailing NULs trimmed)
when printable, else lowercase hex of the raw bytes; <name> is matched with every non-alphanumeric run as "_"
(xattr_com_apple_quarantine). finder_type_creator = "TYPE/CREA" (both 4ccs verbatim); all-zero Finder info -> "none".
Wrong magic / truncated table -> "none"; an xattr / entry that is absent -> "none"."""
import re
import struct

from ..spell import Hex

FIELDS = {
    ("appledouble", "xattr_names"): "ad_value",
    ("appledouble", "xattr_name_list"): "ad_value",
    ("appledouble", "extended_attribute_names"): "ad_value",
    ("appledouble", "attr_names"): "ad_value",
    ("appledouble", "xattr_count"): "ad_value",
    ("appledouble", "attr_count"): "ad_value",
    ("appledouble", "num_attrs"): "ad_value",
    ("appledouble", "xattr_*"): "ad_xattr",
    ("appledouble", "finder_type_creator"): "ad_value",
    ("appledouble", "finder_info_type_creator"): "ad_value",
    ("appledouble", "finder_type"): "ad_value",
    ("appledouble", "finder_file_type"): "ad_value",
    ("appledouble", "file_type"): "ad_value",
    ("appledouble", "finder_creator"): "ad_value",
    ("appledouble", "creator"): "ad_value",
    ("appledouble", "file_creator"): "ad_value",
    ("appledouble", "entry_ids"): "ad_value",
    ("appledouble", "entry_count"): "ad_value",
    ("appledouble", "num_entries"): "ad_value",
    ("appledouble", "number_of_entries"): "ad_value",
    ("appledouble", "magic_u32_hex"): "ad_value",
    ("appledouble", "version_u32_hex"): "ad_value",
    ("appledouble", "home_file_system"): "ad_value",
    ("appledouble", "filler"): "ad_value",
    ("appledouble", "has_resource_fork"): "ad_value",
    ("appledouble", "resource_fork_present"): "ad_value",
    ("appledouble", "resource_fork_size"): "ad_value",
    ("appledouble", "resource_fork_size_bytes"): "ad_value",
    ("appledouble", "resource_fork_length"): "ad_value",
    ("appledouble", "has_quarantine"): "ad_value",
    ("appledouble", "quarantine_present"): "ad_value",
}

_MAGICS = (0x00051607, 0x00051600)


def entries(b):
    """{entry_id: (offset, length)} plus the stored id order, or None when not AppleSingle/AppleDouble."""
    if not isinstance(b, (bytes, bytearray)) or len(b) < 26:
        return None
    magic, ver = struct.unpack_from(">II", b, 0)
    if magic not in _MAGICS:
        return None
    n, = struct.unpack_from(">H", b, 24)
    if n > 64 or 26 + 12 * n > len(b):
        return None
    out, order = {}, []
    for i in range(n):
        eid, off, ln = struct.unpack_from(">III", b, 26 + 12 * i)
        out.setdefault(eid, (off, ln))
        order.append(eid)
    return out, order, magic, ver


def finder_info(b):
    e = entries(b)
    if not e or 9 not in e[0]:
        return None
    off, ln = e[0][9]
    return bytes(b[off:off + ln])


def xattrs(b):
    """[(name, raw value bytes)] of the ATTR block in the Finder-info entry, stored order; [] if none, None if not AD."""
    e = entries(b)
    if e is None:
        return None
    fi = finder_info(b)
    if not fi:
        return []
    off9 = e[0][9][0]
    pos = fi.find(b"ATTR", 32)
    if pos < 0 or pos + 36 > len(fi):
        return []
    base = off9 + pos
    num, = struct.unpack_from(">H", b, base + 34)
    p, out = base + 36, []
    for _ in range(min(num, 512)):
        if p + 11 > len(b):
            break
        voff, vlen, _flags, nlen = struct.unpack_from(">IIHB", b, p)
        name = bytes(b[p + 11:p + 11 + nlen]).split(b"\0")[0].decode("utf-8", "replace")
        out.append((name, bytes(b[voff:voff + vlen])))
        p = (p + 11 + nlen + 3) & ~3
    return out


def xattr(b, name):
    for k, v in xattrs(b) or ():
        if k == name:
            return v
    return None


def _norm(s):
    return re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")


def _render(v):
    t = v.rstrip(b"\0")
    try:
        s = t.decode("utf-8")
    except UnicodeDecodeError:
        return v.hex()
    if s and all(c.isprintable() or c in "\t\r\n" for c in s):
        return s.strip()
    return v.hex()


def ad_xattr(data, ctx):
    """appledouble.xattr_<name>: one extended attribute's value."""
    if data is None:
        return None
    try:
        xs = xattrs(data)
        if xs is None:
            return "none"
        want = _norm(ctx.get("param") or "")
        for k, v in xs:
            if _norm(k) == want:
                return _render(v)
        return "none"
    except Exception:  # noqa: BLE001
        return None


def _value(data, field):
    e = entries(data)
    if e is None:
        return "none"
    ents, order, magic, ver = e
    if field in ("magic_u32_hex",):
        return Hex(magic, 8)
    if field == "version_u32_hex":
        return Hex(ver, 8)
    if field in ("home_file_system", "filler"):
        return bytes(data[8:24]).decode("latin-1").strip(" \0") or "none"
    if field == "entry_ids":
        return order
    if field in ("entry_count", "num_entries", "number_of_entries"):
        return len(order)
    if field in ("has_resource_fork", "resource_fork_present"):
        return 2 in ents and ents[2][1] > 0
    if field.startswith("resource_fork_"):
        return ents[2][1] if 2 in ents else "none"
    if field in ("has_quarantine", "quarantine_present"):
        return any(k == "com.apple.quarantine" for k, _ in xattrs(data) or ())
    if field in ("xattr_names", "xattr_name_list", "extended_attribute_names", "attr_names"):
        return [k for k, _ in xattrs(data) or ()]
    if field in ("xattr_count", "attr_count", "num_attrs"):
        return len(xattrs(data) or ())
    fi = finder_info(data)
    if not fi or len(fi) < 8 or fi[:8] == b"\0" * 8:
        return "none"
    typ, cre = fi[:4].decode("latin-1"), fi[4:8].decode("latin-1")
    if field in ("finder_type", "finder_file_type", "file_type"):
        return typ if fi[:4] != b"\0" * 4 else "none"
    if field in ("finder_creator", "creator", "file_creator"):
        return cre if fi[4:8] != b"\0" * 4 else "none"
    return f"{typ}/{cre}"


def ad_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, ctx.get("field") or "")
    except Exception:  # noqa: BLE001
        return None
