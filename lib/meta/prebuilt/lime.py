"""LiME (Linux Memory Extractor) memory images (prebuilt, SPECULATIVE -- never GM-asked yet). Format words: lime,
memory_image (aliases). Crash dumps (MDMP / PAGEDU64 / hiberfil) live in crashdump.py.

Layout (LiME's lime.h, mirrored by volatility3 layers/lime.py LimeLayer `<IIQQQ`), all little-endian: the file is a
chain of range records, each = a 32-byte header {magic u32 @0 = 0x4C694D45 (bytes `EMiL` on disk), version u32 @4
(1), start u64 @8, end u64 @16 (INCLUSIVE physical address), reserved 8 B @24} followed by (end - start + 1) bytes of
memory. range_count = headers walked until EOF; total_size_bytes = sum of the range lengths (captured memory, NOT the
file size); ranges = JSON list of `0x%x-0x%x` (start-end inclusive, file order, as volatility prints segments);
*_hex addresses are u64 struct fields -> Hex(v, 16). A trailing record whose data is cut off still counts (the header is
intact); a header with a bad magic mid-chain stops the walk. Not LiME at offset 0 (raw .vmem/.raw, AVML `AVML`, ELF
core, ...) -> "none"."""
import struct

from ..spell import Hex

FIELDS = {
    ("lime", "magic_u32_hex"): "lime_value",
    ("lime", "header_magic_u32_hex"): "lime_value",
    ("lime", "magic"): "lime_value",
    ("lime", "header_magic"): "lime_value",
    ("lime", "version"): "lime_value",
    ("lime", "header_version"): "lime_value",
    ("lime", "format_version"): "lime_value",
    ("lime", "lime_version"): "lime_value",
    ("lime", "range_count"): "lime_value",
    ("lime", "number_of_ranges"): "lime_value",
    ("lime", "memory_range_count"): "lime_value",
    ("lime", "range_header_count"): "lime_value",
    ("lime", "segment_count"): "lime_value",
    ("lime", "header_count"): "lime_value",
    ("lime", "total_size_bytes"): "lime_value",
    ("lime", "total_range_size_bytes"): "lime_value",
    ("lime", "memory_size_bytes"): "lime_value",
    ("lime", "captured_size_bytes"): "lime_value",
    ("lime", "total_memory_bytes"): "lime_value",
    ("lime", "first_range_start_hex"): "lime_value",
    ("lime", "first_range_start_u64_hex"): "lime_value",
    ("lime", "first_range_start"): "lime_value",
    ("lime", "first_range_end_hex"): "lime_value",
    ("lime", "first_range_end_u64_hex"): "lime_value",
    ("lime", "first_range_end"): "lime_value",
    ("lime", "first_range_size_bytes"): "lime_value",
    ("lime", "last_range_start_hex"): "lime_value",
    ("lime", "last_range_start_u64_hex"): "lime_value",
    ("lime", "last_range_end_hex"): "lime_value",
    ("lime", "last_range_end_u64_hex"): "lime_value",
    ("lime", "max_address_hex"): "lime_value",
    ("lime", "highest_address_hex"): "lime_value",
    ("lime", "max_address_u64_hex"): "lime_value",
    ("lime", "ranges"): "lime_value",
    ("lime", "range_list"): "lime_value",
    ("lime", "memory_ranges"): "lime_value",
    ("lime", "segments"): "lime_value",
    ("lime", "range_sizes"): "lime_value",
    ("lime", "range_sizes_bytes"): "lime_value",
    ("lime", "range_starts_hex"): "lime_value",
    ("memory_image", "magic_u32_hex"): "lime_value",
    ("memory_image", "header_magic_u32_hex"): "lime_value",
    ("memory_image", "magic"): "lime_value",
    ("memory_image", "version"): "lime_value",
    ("memory_image", "header_version"): "lime_value",
    ("memory_image", "lime_version"): "lime_value",
    ("memory_image", "range_count"): "lime_value",
    ("memory_image", "number_of_ranges"): "lime_value",
    ("memory_image", "memory_range_count"): "lime_value",
    ("memory_image", "range_header_count"): "lime_value",
    ("memory_image", "segment_count"): "lime_value",
    ("memory_image", "total_size_bytes"): "lime_value",
    ("memory_image", "total_range_size_bytes"): "lime_value",
    ("memory_image", "memory_size_bytes"): "lime_value",
    ("memory_image", "captured_size_bytes"): "lime_value",
    ("memory_image", "first_range_start_hex"): "lime_value",
    ("memory_image", "first_range_start_u64_hex"): "lime_value",
    ("memory_image", "first_range_end_hex"): "lime_value",
    ("memory_image", "first_range_end_u64_hex"): "lime_value",
    ("memory_image", "first_range_size_bytes"): "lime_value",
    ("memory_image", "last_range_end_hex"): "lime_value",
    ("memory_image", "last_range_end_u64_hex"): "lime_value",
    ("memory_image", "max_address_hex"): "lime_value",
    ("memory_image", "ranges"): "lime_value",
    ("memory_image", "range_list"): "lime_value",
    ("memory_image", "memory_ranges"): "lime_value",
    ("memory_image", "segments"): "lime_value",
    ("memory_image", "range_sizes"): "lime_value",
    ("memory_image", "format"): "lime_value",
    ("memory_image", "image_format"): "lime_value",
}

NONE = "none"
MAGIC = 0x4C694D45
_HDR = struct.Struct("<IIQQQ")


def _walk(b):
    """[(version, start, end)] of the LiME range headers, [] when offset 0 is not LiME."""
    out, off, n = [], 0, len(b)
    while off + _HDR.size <= n:
        magic, ver, start, end, _ = _HDR.unpack_from(b, off)
        if magic != MAGIC or end < start:
            break
        out.append((ver, start, end))
        off += _HDR.size + (end - start + 1)
    return out


def _field(field):
    for suf in ("_u64_hex", "_u32_hex"):
        if field.endswith(suf):
            return field[: -len(suf)] + "_hex"
    return field


def lime_value(data, ctx):
    if data is None:
        return None
    try:
        rs = _walk(bytes(data))
    except Exception:
        return None
    if not rs:
        return NONE
    f = _field(ctx.get("field") or "")
    if f in ("magic_hex", "header_magic_hex"):
        return Hex(MAGIC, 8)
    if f in ("magic", "header_magic"):
        return "EMiL"
    if f in ("format", "image_format"):
        return "LiME"
    if f in ("version", "header_version", "format_version", "lime_version"):
        return rs[0][0]
    if f in ("range_count", "number_of_ranges", "memory_range_count", "range_header_count", "segment_count",
             "header_count"):
        return len(rs)
    if f in ("total_size_bytes", "total_range_size_bytes", "memory_size_bytes", "captured_size_bytes",
             "total_memory_bytes"):
        return sum(e - s + 1 for _, s, e in rs)
    if f in ("first_range_start_hex", "first_range_start"):
        return Hex(rs[0][1], 16)
    if f in ("first_range_end_hex", "first_range_end"):
        return Hex(rs[0][2], 16)
    if f == "first_range_size_bytes":
        return rs[0][2] - rs[0][1] + 1
    if f == "last_range_start_hex":
        return Hex(rs[-1][1], 16)
    if f in ("last_range_end_hex", "max_address_hex", "highest_address_hex"):
        return Hex(max(e for _, _, e in rs), 16)
    if f in ("ranges", "range_list", "memory_ranges", "segments"):
        return ["0x%x-0x%x" % (s, e) for _, s, e in rs]
    if f in ("range_sizes", "range_sizes_bytes"):
        return [e - s + 1 for _, s, e in rs]
    if f == "range_starts_hex":
        return ["0x%x" % s for _, s, _ in rs]
    return None
