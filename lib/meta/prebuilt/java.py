"""Java .class file header fields (JVMS ch.4 ClassFile; prebuilt, SPECULATIVE -- never GM-asked yet).

Big-endian: magic u4 0xCAFEBABE, minor_version u2 @4, major_version u2 @6, constant_pool_count u2 @8 (= entries + 1,
the value javap's last '#N' + 1; long/double take two slots), constant_pool[], access_flags u2, this_class u2,
super_class u2, interfaces_count u2 + u2[], fields_count, then fields/methods/attributes (SourceFile at the end).
java_version: major 52 -> "8", 55 -> "11", 61 -> "17", 65 -> "21" (major - 44 for major >= 49); 45..48 -> "1.1".."1.4".
this_class / super_class = the CONSTANT_Class name in INTERNAL form exactly as stored (`com/example/Foo`, the javap
`// com/example/Foo` comment); *_name / class_name are the same string.
Mach-O fat collision: 0xcafebabe is also FAT_MAGIC. Like `file`, the u4 at offset 4 decides: a class has
minor<<16|major with major >= 45 (value >= 45); a fat binary has nfat_arch there (small) -> "none".
Wrong magic / truncated header -> "none"; a damaged constant pool only blanks the pool-derived fields."""
import struct

from ..spell import Hex

FIELDS = {
    ("java", "magic_u32_hex"): "java_value",
    ("java", "magic"): "java_value",
    ("java", "minor_version"): "java_value",
    ("java", "major_version"): "java_value",
    ("java", "class_file_version"): "java_value",
    ("java", "version"): "java_value",
    ("java", "java_version"): "java_value",
    ("java", "target_java_version"): "java_value",
    ("java", "constant_pool_count"): "java_value",
    ("java", "this_class"): "java_value",
    ("java", "this_class_name"): "java_value",
    ("java", "class_name"): "java_value",
    ("java", "super_class"): "java_value",
    ("java", "super_class_name"): "java_value",
    ("java", "access_flags_u16_hex"): "java_value",
    ("java", "class_access_flags_u16_hex"): "java_value",
    ("java", "interfaces_count"): "java_value",
    ("java", "fields_count"): "java_value",
    ("java", "methods_count"): "java_value",
    ("java", "source_file"): "java_value",
    ("java", "sourcefile"): "java_value",
    ("class", "magic_u32_hex"): "java_value",
    ("class", "magic"): "java_value",
    ("class", "minor_version"): "java_value",
    ("class", "major_version"): "java_value",
    ("class", "class_file_version"): "java_value",
    ("class", "version"): "java_value",
    ("class", "java_version"): "java_value",
    ("class", "target_java_version"): "java_value",
    ("class", "constant_pool_count"): "java_value",
    ("class", "this_class"): "java_value",
    ("class", "this_class_name"): "java_value",
    ("class", "class_name"): "java_value",
    ("class", "super_class"): "java_value",
    ("class", "super_class_name"): "java_value",
    ("class", "access_flags_u16_hex"): "java_value",
    ("class", "class_access_flags_u16_hex"): "java_value",
    ("class", "interfaces_count"): "java_value",
    ("class", "fields_count"): "java_value",
    ("class", "methods_count"): "java_value",
    ("class", "source_file"): "java_value",
    ("class", "sourcefile"): "java_value",
    ("jvm", "magic_u32_hex"): "java_value",
    ("jvm", "magic"): "java_value",
    ("jvm", "minor_version"): "java_value",
    ("jvm", "major_version"): "java_value",
    ("jvm", "class_file_version"): "java_value",
    ("jvm", "version"): "java_value",
    ("jvm", "java_version"): "java_value",
    ("jvm", "target_java_version"): "java_value",
    ("jvm", "constant_pool_count"): "java_value",
    ("jvm", "this_class"): "java_value",
    ("jvm", "this_class_name"): "java_value",
    ("jvm", "class_name"): "java_value",
    ("jvm", "super_class"): "java_value",
    ("jvm", "super_class_name"): "java_value",
    ("jvm", "access_flags_u16_hex"): "java_value",
    ("jvm", "class_access_flags_u16_hex"): "java_value",
    ("jvm", "interfaces_count"): "java_value",
    ("jvm", "fields_count"): "java_value",
    ("jvm", "methods_count"): "java_value",
    ("jvm", "source_file"): "java_value",
    ("jvm", "sourcefile"): "java_value",
}

# tag -> fixed payload size (after the tag byte); Utf8 (1) is variable; Long/Double (5/6) take two slots
_CP_SIZE = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}


def _header(b):
    if not isinstance(b, (bytes, bytearray)) or len(b) < 10 or b[:4] != b"\xca\xfe\xba\xbe":
        return None
    minor, major, cpc = struct.unpack_from(">HHH", b, 4)
    if major < 45 or (minor << 16 | major) < 45:   # Mach-O fat: nfat_arch here
        return None
    return minor, major, cpc


def _pool(b, cpc):
    """({index: (tag, payload)}, offset after the pool) or None."""
    pool, off, i = {}, 10, 1
    while i < cpc:
        if off >= len(b):
            return None
        tag = b[off]
        if tag == 1:
            if off + 3 > len(b):
                return None
            ln, = struct.unpack_from(">H", b, off + 1)
            pool[i] = (1, bytes(b[off + 3:off + 3 + ln]))
            off += 3 + ln
            i += 1
        elif tag in _CP_SIZE:
            n = _CP_SIZE[tag]
            pool[i] = (tag, bytes(b[off + 1:off + 1 + n]))
            off += 1 + n
            i += 2 if tag in (5, 6) else 1
        else:
            return None
        if off > len(b):
            return None
    return pool, off


def _utf8(pool, idx):
    t = pool.get(idx)
    if not t or t[0] != 1:
        return None
    try:
        return t[1].decode("utf-8")
    except UnicodeDecodeError:
        return t[1].decode("utf-8", "replace")   # modified UTF-8 (\xc0\x80 NUL / surrogate pairs): best effort


def _class_name(pool, idx):
    t = pool.get(idx)
    if not t or t[0] != 7:
        return None
    return _utf8(pool, struct.unpack(">H", t[1])[0])


def _skip_members(b, off):
    """Offset after a fields[]/methods[] table (count already read), or None."""
    n, = struct.unpack_from(">H", b, off)
    off += 2
    for _ in range(n):
        if off + 8 > len(b):
            return None, n
        ac, = struct.unpack_from(">H", b, off + 6)
        off += 8
        for _ in range(ac):
            if off + 6 > len(b):
                return None, n
            ln, = struct.unpack_from(">I", b, off + 2)
            off += 6 + ln
    return off, n


def _java_version(major):
    if major >= 49:
        return str(major - 44)
    return "1.%d" % (major - 44)


def java_value(data, ctx):
    try:
        return _java_value(data, (ctx or {}).get("field") or "")
    except (struct.error, IndexError, ValueError):
        return "none"


def _java_value(b, field):
    if b is None:
        return None
    h = _header(b)
    if h is None:
        return "none"
    minor, major, cpc = h
    if field in ("magic_u32_hex", "magic"):
        return Hex(0xCAFEBABE, 8)
    if field == "minor_version":
        return minor
    if field == "major_version":
        return major
    if field in ("class_file_version", "version"):
        return "%d.%d" % (major, minor)
    if field in ("java_version", "target_java_version"):
        return _java_version(major)
    if field == "constant_pool_count":
        return cpc
    p = _pool(b, cpc)
    if p is None:
        return "none"
    pool, off = p
    if off + 8 > len(b):
        return "none"
    flags, this_i, super_i, nif = struct.unpack_from(">HHHH", b, off)
    if field in ("access_flags_u16_hex", "class_access_flags_u16_hex"):
        return Hex(flags, 4)
    if field in ("this_class", "this_class_name", "class_name"):
        return _class_name(pool, this_i) or "none"
    if field in ("super_class", "super_class_name"):
        return (_class_name(pool, super_i) or "none") if super_i else "none"
    if field == "interfaces_count":
        return nif
    off += 8 + 2 * nif
    off, nf = _skip_members(b, off)
    if field == "fields_count":
        return nf
    if off is None:
        return "none"
    off, nm = _skip_members(b, off)
    if field == "methods_count":
        return nm
    if off is None or off + 2 > len(b):
        return "none"
    na, = struct.unpack_from(">H", b, off)
    off += 2
    for _ in range(na):
        if off + 6 > len(b):
            break
        ni, ln = struct.unpack_from(">HI", b, off)
        if _utf8(pool, ni) == "SourceFile" and ln == 2:
            return _utf8(pool, struct.unpack_from(">H", b, off + 6)[0]) or "none"
        off += 6 + ln
    return "none"
