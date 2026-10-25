"""Explorer thumbcache_*.db / iconcache_*.db (fmt `thumbcache`, aliases `thumbcache_db`, `iconcache`) -- prebuilt,
SPECULATIVE (never asked yet).

File header (little-endian): "CMMM" @0, format version u32 @4 (20 Vista, 21 Win7, 30 Win8, 31 Win8.1, 32 Win10),
cache type u32 @8 (an index; its size label depends on the version, see _TYPE_LABELS). Then, by version:
  20/21: first_cache_entry_offset @0x0C, available_cache_entry_offset @0x10, number_of_cache_entries @0x14 (0x18 hdr)
  30   : unknown @0x0C, first @0x10, available @0x14, number_of_cache_entries @0x18 (0x1C hdr)
  31/32: unknown @0x0C, first @0x10, available @0x14 (0x18 hdr, no entry count stored -> header_entry_count "none")
Cache entry ("CMMM"): size u32 @4, entry hash u64 @8, then
  Vista (20): extension wchar[4] @0x10, identifier_size @0x18, padding_size @0x1C, data_size @0x20, unknown @0x24,
              data_checksum u64 @0x28, header_checksum u64 @0x30  -> 0x38 bytes
  Win7  (21): identifier_size @0x10, padding_size @0x14, data_size @0x18, unknown @0x1C, data_checksum @0x20,
              header_checksum @0x28                                  -> 0x30 bytes
  Win8+ (>=30): identifier_size @0x10, padding_size @0x14, data_size @0x18, width @0x1C, height @0x20, unknown @0x24,
              data_checksum @0x28, header_checksum @0x30             -> 0x38 bytes
then the UTF-16LE identifier (identifier_size bytes), padding, data. Entries are walked from first_cache_entry_offset
by entry size until a non-"CMMM" signature / zero size / EOF. entry_count counts every walked entry (empty slots too,
like dissect.thumbcache); non_empty_entry_count only data_size > 0. Hashes/checksums are the stored u64 rendered
0x%016x (file order). data_magic_set = sorted distinct first-2-byte hex of the entry data ("ffd8" JPEG, "8950" PNG,
"424d" BMP). A file without the "CMMM" header (incl. thumbcache_idx.db "IMMM") -> "none".
Fixtures: stdlib struct writer per the layout above (PIL payloads); oracle dissect.thumbcache 3.x (Fox-IT).
RDP bitmap cache (Cache0000.bin / bcache*.bmc) is NOT covered: no independent reader was available offline."""
import struct

FIELDS = {
    ("thumbcache", "format_version"): "tc_value",
    ("thumbcache", "version"): "tc_value",
    ("thumbcache", "header_version"): "tc_value",
    ("thumbcache", "file_format_version"): "tc_value",
    ("thumbcache", "windows_version"): "tc_value",
    ("thumbcache", "os_version"): "tc_value",
    ("thumbcache", "cache_type"): "tc_value",
    ("thumbcache", "cache_type_id"): "tc_value",
    ("thumbcache", "cache_type_name"): "tc_value",
    ("thumbcache", "cache_type_label"): "tc_value",
    ("thumbcache", "cache_size_label"): "tc_value",
    ("thumbcache", "thumbnail_size"): "tc_value",
    ("thumbcache", "first_cache_entry_offset"): "tc_value",
    ("thumbcache", "first_entry_offset"): "tc_value",
    ("thumbcache", "available_cache_entry_offset"): "tc_value",
    ("thumbcache", "available_entry_offset"): "tc_value",
    ("thumbcache", "header_entry_count"): "tc_value",
    ("thumbcache", "number_of_cache_entries"): "tc_value",
    ("thumbcache", "header_number_of_entries"): "tc_value",
    ("thumbcache", "entry_count"): "tc_value",
    ("thumbcache", "cache_entry_count"): "tc_value",
    ("thumbcache", "number_of_entries"): "tc_value",
    ("thumbcache", "non_empty_entry_count"): "tc_value",
    ("thumbcache", "thumbnail_count"): "tc_value",
    ("thumbcache", "entry_hashes"): "tc_value",
    ("thumbcache", "cache_entry_hashes"): "tc_value",
    ("thumbcache", "entry_hash_list"): "tc_value",
    ("thumbcache", "first_entry_hash"): "tc_value",
    ("thumbcache", "entry_identifiers"): "tc_value",
    ("thumbcache", "entry_extensions"): "tc_value",
    ("thumbcache", "entry_data_sizes"): "tc_value",
    ("thumbcache", "entry_dimensions"): "tc_value",
    ("thumbcache", "entry_data_checksums"): "tc_value",
    ("thumbcache", "entry_header_checksums"): "tc_value",
    ("thumbcache", "data_magic_set"): "tc_value",
    ("thumbcache", "data_magic_hex_set"): "tc_value",
    ("thumbcache", "entry_data_magic_set"): "tc_value",
    ("thumbcache", "data_formats"): "tc_value",
    ("thumbcache", "data_format_set"): "tc_value",
    ("thumbcache", "image_formats"): "tc_value",
    ("thumbcache_db", "format_version"): "tc_value",
    ("thumbcache_db", "version"): "tc_value",
    ("thumbcache_db", "windows_version"): "tc_value",
    ("thumbcache_db", "cache_type"): "tc_value",
    ("thumbcache_db", "cache_type_name"): "tc_value",
    ("thumbcache_db", "cache_type_label"): "tc_value",
    ("thumbcache_db", "first_cache_entry_offset"): "tc_value",
    ("thumbcache_db", "available_cache_entry_offset"): "tc_value",
    ("thumbcache_db", "header_entry_count"): "tc_value",
    ("thumbcache_db", "number_of_cache_entries"): "tc_value",
    ("thumbcache_db", "entry_count"): "tc_value",
    ("thumbcache_db", "non_empty_entry_count"): "tc_value",
    ("thumbcache_db", "entry_hashes"): "tc_value",
    ("thumbcache_db", "first_entry_hash"): "tc_value",
    ("thumbcache_db", "entry_identifiers"): "tc_value",
    ("thumbcache_db", "entry_dimensions"): "tc_value",
    ("thumbcache_db", "data_magic_set"): "tc_value",
    ("thumbcache_db", "data_formats"): "tc_value",
    ("iconcache", "format_version"): "tc_value",
    ("iconcache", "version"): "tc_value",
    ("iconcache", "windows_version"): "tc_value",
    ("iconcache", "cache_type"): "tc_value",
    ("iconcache", "cache_type_name"): "tc_value",
    ("iconcache", "cache_type_label"): "tc_value",
    ("iconcache", "first_cache_entry_offset"): "tc_value",
    ("iconcache", "available_cache_entry_offset"): "tc_value",
    ("iconcache", "header_entry_count"): "tc_value",
    ("iconcache", "number_of_cache_entries"): "tc_value",
    ("iconcache", "entry_count"): "tc_value",
    ("iconcache", "non_empty_entry_count"): "tc_value",
    ("iconcache", "entry_hashes"): "tc_value",
    ("iconcache", "first_entry_hash"): "tc_value",
    ("iconcache", "entry_identifiers"): "tc_value",
    ("iconcache", "entry_dimensions"): "tc_value",
    ("iconcache", "data_magic_set"): "tc_value",
    ("iconcache", "data_formats"): "tc_value",
}

_WINVER = {20: "Windows Vista", 21: "Windows 7", 30: "Windows 8", 31: "Windows 8.1", 32: "Windows 10"}
# cache-type index -> size label (Thumbcache Viewer / libyal documentation)
_TYPE_LABELS = {
    20: ["32", "96", "256", "1024", "sr"],
    21: ["32", "96", "256", "1024", "sr"],
    30: ["16", "32", "48", "96", "256", "1024", "sr", "wide", "exif"],
    31: ["16", "32", "48", "96", "256", "1024", "1600", "sr", "wide", "exif", "wide_alternate"],
    32: ["16", "32", "48", "96", "256", "768", "1280", "1920", "2560", "sr", "wide", "exif", "wide_alternate",
         "custom_stream"],
}
_MAGIC_NAMES = {"ffd8": "jpeg", "8950": "png", "424d": "bmp"}


def _parse(b):
    """Header + walked entries, or None when this is not a CMMM thumbcache file."""
    if not b or len(b) < 0x18 or b[:4] != b"CMMM":
        return None
    ver, ctype = struct.unpack_from("<II", b, 4)
    h = {"version": ver, "cache_type": ctype, "header_count": None}
    if ver < 30:
        h["first"], h["avail"], h["header_count"] = struct.unpack_from("<III", b, 0x0C)
    elif ver == 30 and len(b) >= 0x1C:
        h["first"], h["avail"], h["header_count"] = struct.unpack_from("<III", b, 0x10)
    else:
        h["first"], h["avail"] = struct.unpack_from("<II", b, 0x10)
    ents, off = [], h["first"]
    hdr = 0x30 if ver == 21 else 0x38
    while 0 < off and off + hdr <= len(b) and b[off:off + 4] == b"CMMM" and len(ents) < 100000:
        size, = struct.unpack_from("<I", b, off + 4)
        hsh, = struct.unpack_from("<Q", b, off + 8)
        e = {"hash": hsh, "ext": None, "w": None, "h": None}
        if ver == 20:
            e["ext"] = b[off + 0x10:off + 0x18].decode("utf-16-le", "replace").split("\x00")[0]
            idsz, pad, dsz, _u, dck, hck = struct.unpack_from("<IIIIQQ", b, off + 0x18)
        elif ver == 21:
            idsz, pad, dsz, _u, dck, hck = struct.unpack_from("<IIIIQQ", b, off + 0x10)
        else:
            idsz, pad, dsz, e["w"], e["h"], _u, dck, hck = struct.unpack_from("<IIIIIIQQ", b, off + 0x10)
        ids = off + hdr
        e["ident"] = b[ids:ids + idsz].decode("utf-16-le", "replace").rstrip("\x00")
        dstart = ids + idsz + pad
        e["data"] = b[dstart:dstart + dsz]
        e["dsz"], e["dck"], e["hck"] = dsz, dck, hck
        ents.append(e)
        if size < hdr:
            break
        off += size
    h["entries"] = ents
    return h


def tc_value(data, ctx):
    if data is None:
        return None
    try:
        p = _parse(data)
    except (struct.error, ValueError):
        p = None
    if p is None:
        return "none"
    f = ctx.get("field") or ""
    ver, ents = p["version"], p["entries"]
    if f in ("format_version", "version", "header_version", "file_format_version"):
        return ver
    if f in ("windows_version", "os_version"):
        return _WINVER.get(ver, "none")
    if f in ("cache_type", "cache_type_id"):
        return p["cache_type"]
    if f in ("cache_type_name", "cache_type_label", "cache_size_label", "thumbnail_size"):
        labels = _TYPE_LABELS.get(ver) or []
        return labels[p["cache_type"]] if p["cache_type"] < len(labels) else "none"
    if f in ("first_cache_entry_offset", "first_entry_offset"):
        return p["first"]
    if f in ("available_cache_entry_offset", "available_entry_offset"):
        return p["avail"]
    if f in ("header_entry_count", "number_of_cache_entries", "header_number_of_entries"):
        return "none" if p["header_count"] is None else p["header_count"]
    if f in ("entry_count", "cache_entry_count", "number_of_entries"):
        return len(ents)
    if f in ("non_empty_entry_count", "thumbnail_count"):
        return sum(1 for e in ents if e["dsz"] > 0)
    if f in ("entry_hashes", "cache_entry_hashes", "entry_hash_list"):
        return ["0x%016x" % e["hash"] for e in ents]
    if f == "first_entry_hash":
        return "0x%016x" % ents[0]["hash"] if ents else "none"
    if f == "entry_identifiers":
        return [e["ident"] for e in ents]
    if f == "entry_extensions":
        return [e["ext"] for e in ents] if ver == 20 else "none"
    if f == "entry_data_sizes":
        return [e["dsz"] for e in ents]
    if f == "entry_dimensions":
        return ["%dx%d" % (e["w"], e["h"]) for e in ents] if ver >= 30 else "none"
    if f == "entry_data_checksums":
        return ["0x%016x" % e["dck"] for e in ents]
    if f == "entry_header_checksums":
        return ["0x%016x" % e["hck"] for e in ents]
    magics = sorted({e["data"][:2].hex() for e in ents if len(e["data"]) >= 2})
    if f in ("data_magic_set", "data_magic_hex_set", "entry_data_magic_set"):
        return magics
    if f in ("data_formats", "data_format_set", "image_formats"):
        return sorted({_MAGIC_NAMES.get(m, m) for m in magics})
    return None
