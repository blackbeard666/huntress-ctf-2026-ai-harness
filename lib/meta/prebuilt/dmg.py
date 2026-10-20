"""Apple disk images (UDIF .dmg) -- the `koly` trailer (prebuilt, SPECULATIVE -- never GM-asked yet).

UDIF puts a 512-byte big-endian `koly` block in the LAST 512 bytes of the file: signature "koly" @0, version u32 @4
(4), header_size u32 @8 (512), flags u32 @12, running_data_fork_offset u64 @16, data_fork_offset u64 @24,
data_fork_length u64 @32, rsrc_fork_offset u64 @40, rsrc_fork_length u64 @48, segment_number u32 @56,
segment_count u32 @60, segment_id 16 B @64, data checksum (type, size, 128 B) @80, xml_offset u64 @216, xml_length u64
@224, master checksum @352, image_variant u32 @0x1E8, sector_count u64 @0x1EC (512-byte sectors).
xml_plist_partition_names = the XML property list's resource-fork/blkx dicts' `Name` (CFName fallback) in stored
order -- what `7z l` shows as "<index>.<Name>" items and `hdiutil imageinfo` lists as partitions.
No `koly` in the last 512 bytes (or truncated) -> "none"."""
import plistlib
import re
import struct

from ..spell import Hex

FIELDS = {
    ("dmg", "koly_version"): "koly_value",
    ("dmg", "version"): "koly_value",
    ("dmg", "udif_version"): "koly_value",
    ("dmg", "koly_header_size"): "koly_value",
    ("dmg", "header_size"): "koly_value",
    ("dmg", "koly_flags_u32_hex"): "koly_value",
    ("dmg", "flags_u32_hex"): "koly_value",
    ("dmg", "data_fork_offset"): "koly_value",
    ("dmg", "koly_data_fork_offset"): "koly_value",
    ("dmg", "data_fork_length"): "koly_value",
    ("dmg", "koly_data_fork_length"): "koly_value",
    ("dmg", "rsrc_fork_offset"): "koly_value",
    ("dmg", "rsrc_fork_length"): "koly_value",
    ("dmg", "xml_offset"): "koly_value",
    ("dmg", "koly_xml_offset"): "koly_value",
    ("dmg", "xml_length"): "koly_value",
    ("dmg", "koly_xml_length"): "koly_value",
    ("dmg", "plist_offset"): "koly_value",
    ("dmg", "plist_length"): "koly_value",
    ("dmg", "segment_number"): "koly_value",
    ("dmg", "segment_count"): "koly_value",
    ("dmg", "image_variant"): "koly_value",
    ("dmg", "koly_image_variant"): "koly_value",
    ("dmg", "sector_count"): "koly_value",
    ("dmg", "koly_sector_count"): "koly_value",
    ("dmg", "xml_plist_partition_names"): "partition_value",
    ("dmg", "partition_names"): "partition_value",
    ("dmg", "blkx_names"): "partition_value",
    ("dmg", "plist_partition_names"): "partition_value",
    ("dmg", "xml_plist_partition_count"): "partition_value",
    ("dmg", "partition_count"): "partition_value",
    ("dmg", "blkx_count"): "partition_value",
}

_KOLY = ">4sIIIQQQQQII16sII128sQQ"   # through xml_length (232 bytes)


def koly(b):
    """The koly trailer as a dict, or None (no koly in the last 512 bytes / truncated)."""
    if not b or len(b) < 512:
        return None
    t = bytes(b[-512:])
    if t[:4] != b"koly":
        return None
    (_, ver, hsz, flags, rdfo, dfo, dfl, rfo, rfl, segn, segc, _sid, _ct, _cs, _cd, xo, xl) = \
        struct.unpack_from(_KOLY, t, 0)
    variant, sectors = struct.unpack_from(">IQ", t, 0x1E8)
    return {"version": ver, "header_size": hsz, "flags": flags, "data_fork_offset": dfo, "data_fork_length": dfl,
            "rsrc_fork_offset": rfo, "rsrc_fork_length": rfl, "segment_number": segn, "segment_count": segc,
            "xml_offset": xo, "xml_length": xl, "image_variant": variant, "sector_count": sectors}


_ALIAS = {"udif_version": "version", "plist_offset": "xml_offset", "plist_length": "xml_length"}


def koly_value(data, ctx):
    if data is None:
        return None
    try:
        k = koly(data)
    except Exception:
        return None
    if k is None:
        return "none"
    f = (ctx or {}).get("field") or ""
    if f.endswith("_u32_hex"):
        return Hex(k["flags"], 8) if "flags" in f else None
    key = _ALIAS.get(f) or re.sub(r"^koly_", "", f)
    return k.get(key)


def blkx_names(b):
    """[Name] of the plist resource-fork/blkx entries in stored order, or None (no koly / no plist)."""
    k = koly(b)
    if k is None:
        return None
    xo, xl = k["xml_offset"], k["xml_length"]
    if not xl or xo + xl > len(b):
        return None
    raw = bytes(b[xo:xo + xl])
    if re.search(rb"<!ENTITY", raw[:4096], re.I):
        return None
    pl = plistlib.loads(raw)
    blkx = ((pl or {}).get("resource-fork") or {}).get("blkx")
    if not isinstance(blkx, list):
        return None
    return [str(e.get("Name", e.get("CFName", ""))) for e in blkx if isinstance(e, dict)]


def partition_value(data, ctx):
    if data is None:
        return None
    try:
        names = blkx_names(data)
    except Exception:
        return None
    if names is None:
        return "none"
    f = (ctx or {}).get("field") or ""
    return len(names) if f.endswith("count") else names
