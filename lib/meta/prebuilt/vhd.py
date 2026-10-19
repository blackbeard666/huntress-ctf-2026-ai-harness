"""VHD (Microsoft Virtual Hard Disk, VPC/Virtual Server) footer + dynamic header fields (prebuilt, SPECULATIVE).

Footer (512 B, BIG-endian, spec "Virtual Hard Disk Image Format Specification" v1.0): cookie "conectix" @0,
features u32 @8, file_format_version u32 @12 (0x00010000), data_offset u64 @16 (0xFFFFFFFFFFFFFFFF on fixed disks),
timestamp u32 @24, creator_application 4 chars @28 ("qemu", "vpc ", "vs  ", "win ", qemu force_size writes "qem2"),
creator_version u32 @32 (major<<16|minor), creator_host_os u32 @36 ("Wi2k" / "Mac "), original_size u64 @40,
current_size u64 @48, disk_geometry @56 (cylinders u16, heads u8, sectors u8), disk_type u32 @60 (2 fixed,
3 dynamic, 4 differencing), checksum u32 @64 (one's complement of the byte sum with the checksum zeroed),
unique_id 16 B @68, saved_state u8 @84.
Footer location: the LAST 512 bytes (fixed and dynamic), else the last 511 (pre-VPC2004 writers), else the copy in
the FIRST 512 bytes (dynamic disks keep one there; a carved header-only member still answers).
Dynamic header "cxsparse" @data_offset (1024 B, big-endian): table_offset u64 @16, header_version u32 @24,
max_table_entries u32 @28, block_size u32 @32, checksum u32 @36, parent_unique_id 16 B @40, parent_timestamp u32 @56,
parent_unicode_name UTF-16BE 512 B @64.
Spellings: timestamp* = seconds since 2000-01-01T00:00:00Z rendered ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' (7-Zip
"Created"); *_u32_hex = the raw u32. creator_version = "major.minor" (`file`: "Creator qemu 5.3"). unique_id_guid =
the 16 stored bytes in STORED (RFC 4122 / big-endian) order -> 8-4-4-4-12 lowercase (7-Zip prints the same bytes as
"ID = 0B21F036EBE6..." and qemu's v4 uuid nibble sits where RFC order puts it). Not a VHD -> "none"."""
import datetime
import struct

from ..spell import Guid, Hex

FIELDS = {
    ("vhd", "cookie"): "vhd_value",
    ("vhd", "footer_cookie"): "vhd_value",
    ("vhd", "features_u32_hex"): "vhd_value",
    ("vhd", "file_format_version"): "vhd_value",
    ("vhd", "file_format_version_u32_hex"): "vhd_value",
    ("vhd", "data_offset"): "vhd_value",
    ("vhd", "data_offset_u64_hex"): "vhd_value",
    ("vhd", "timestamp"): "vhd_value",
    ("vhd", "timestamp_utc"): "vhd_value",
    ("vhd", "timestamp_u32_hex"): "vhd_value",
    ("vhd", "timestamp_raw"): "vhd_value",
    ("vhd", "creation_time"): "vhd_value",
    ("vhd", "creation_time_utc"): "vhd_value",
    ("vhd", "created_utc"): "vhd_value",
    ("vhd", "creator_application"): "vhd_value",
    ("vhd", "creator_app"): "vhd_value",
    ("vhd", "creator_version"): "vhd_value",
    ("vhd", "creator_version_u32_hex"): "vhd_value",
    ("vhd", "creator_host_os"): "vhd_value",
    ("vhd", "creator_host_os_u32_hex"): "vhd_value",
    ("vhd", "host_os"): "vhd_value",
    ("vhd", "original_size"): "vhd_value",
    ("vhd", "original_size_bytes"): "vhd_value",
    ("vhd", "current_size"): "vhd_value",
    ("vhd", "current_size_bytes"): "vhd_value",
    ("vhd", "virtual_size"): "vhd_value",
    ("vhd", "virtual_size_bytes"): "vhd_value",
    ("vhd", "disk_size_bytes"): "vhd_value",
    ("vhd", "disk_geometry"): "vhd_value",
    ("vhd", "geometry_chs"): "vhd_value",
    ("vhd", "geometry_cylinders"): "vhd_value",
    ("vhd", "geometry_heads"): "vhd_value",
    ("vhd", "geometry_sectors"): "vhd_value",
    ("vhd", "disk_type"): "vhd_value",
    ("vhd", "disk_type_u32_hex"): "vhd_value",
    ("vhd", "disk_type_name"): "vhd_value",
    ("vhd", "checksum"): "vhd_value",
    ("vhd", "checksum_u32_hex"): "vhd_value",
    ("vhd", "footer_checksum_u32_hex"): "vhd_value",
    ("vhd", "checksum_valid"): "vhd_value",
    ("vhd", "unique_id"): "vhd_value",
    ("vhd", "unique_id_guid"): "vhd_value",
    ("vhd", "unique_id_hex"): "vhd_value",
    ("vhd", "saved_state"): "vhd_value",
    ("vhd", "dynamic_header_cookie"): "vhd_value",
    ("vhd", "table_offset"): "vhd_value",
    ("vhd", "max_table_entries"): "vhd_value",
    ("vhd", "block_size"): "vhd_value",
    ("vhd", "block_size_bytes"): "vhd_value",
    ("vhd", "parent_unique_id_guid"): "vhd_value",
    ("vhd", "parent_timestamp_utc"): "vhd_value",
    ("vhd", "parent_name"): "vhd_value",
    ("vhd", "parent_unicode_name"): "vhd_value",
}

_EPOCH = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
_TYPES = {0: "none", 1: "reserved", 2: "fixed", 3: "dynamic", 4: "differencing", 5: "reserved", 6: "reserved"}


def _iso(secs):
    return (_EPOCH + datetime.timedelta(seconds=secs)).strftime("%Y-%m-%dT%H:%M:%SZ")


def footer(data):
    """The 512-byte footer (padded) or None."""
    if not data or len(data) < 85:
        return None
    for f in (data[-512:], data[-511:], data[:512]):
        if f[:8] == b"conectix" and len(f) >= 85:
            return f.ljust(512, b"\0")
    return None


def _text4(b):
    s = b.decode("latin-1").strip("\0 ")
    return s if s else "none"


def parse(data):
    """{field: raw value} of a VHD, or None."""
    f = footer(data)
    if f is None:
        return None
    (features, ver, doff, ts, app, cver, host, osz, csz, cyl, heads, secs, dtype, csum,
     uid, saved) = struct.unpack_from(">IIQI4sI4sQQHBBII16sB", f, 8)
    calc = (~sum(f[:64] + b"\0\0\0\0" + f[68:]) & 0xFFFFFFFF)
    out = {
        "cookie": "conectix",
        "features_u32_hex": Hex(features, 8),
        "file_format_version": "%d.%d" % (ver >> 16, ver & 0xFFFF),
        "file_format_version_u32_hex": Hex(ver, 8),
        "data_offset": doff, "data_offset_u64_hex": Hex(doff, 16),
        "timestamp": _iso(ts), "timestamp_u32_hex": Hex(ts, 8), "timestamp_raw": ts,
        "creator_application": _text4(app),
        "creator_version": "%d.%d" % (cver >> 16, cver & 0xFFFF),
        "creator_version_u32_hex": Hex(cver, 8),
        "creator_host_os": _text4(host),
        "creator_host_os_u32_hex": Hex(int.from_bytes(host, "big"), 8),
        "original_size": osz, "current_size": csz,
        "disk_geometry": "%d/%d/%d" % (cyl, heads, secs),
        "geometry_cylinders": cyl, "geometry_heads": heads, "geometry_sectors": secs,
        "disk_type": dtype, "disk_type_u32_hex": Hex(dtype, 8), "disk_type_name": _TYPES.get(dtype, "unknown"),
        "checksum": Hex(csum, 8), "checksum_valid": calc == csum,
        "unique_id": Guid("bytes_be", uid), "unique_id_hex": uid.hex(),
        "saved_state": bool(saved),
    }
    if dtype in (3, 4) and doff + 1024 <= len(data) and data[doff:doff + 8] == b"cxsparse":
        h = data[doff:doff + 1024]
        tbl, _hv, mte, bsz, _ck, puid, pts = struct.unpack_from(">QIIII16sI", h, 16)
        out.update({
            "dynamic_header_cookie": "cxsparse", "table_offset": tbl, "max_table_entries": mte, "block_size": bsz,
            "parent_unique_id": Guid("bytes_be", puid) if any(puid) else "none",
            "parent_timestamp": _iso(pts) if pts else "none",
            "parent_name": h[64:576].decode("utf-16-be", "replace").split("\0")[0] or "none",
        })
    return out


_ALIAS = {
    "footer_cookie": "cookie", "timestamp_utc": "timestamp", "creation_time": "timestamp",
    "creation_time_utc": "timestamp", "created_utc": "timestamp", "creator_app": "creator_application",
    "host_os": "creator_host_os", "original_size_bytes": "original_size", "current_size_bytes": "current_size",
    "virtual_size": "current_size", "virtual_size_bytes": "current_size", "disk_size_bytes": "current_size",
    "geometry_chs": "disk_geometry", "checksum_u32_hex": "checksum", "footer_checksum_u32_hex": "checksum",
    "unique_id_guid": "unique_id", "block_size_bytes": "block_size", "parent_unique_id_guid": "parent_unique_id",
    "parent_timestamp_utc": "parent_timestamp", "parent_unicode_name": "parent_name",
}


def field_value(data, field):
    """Value of a vhd field for `data` ("none" when not a VHD / field absent)."""
    try:
        p = parse(data)
    except (struct.error, ValueError, IndexError):
        p = None
    if p is None:
        return "none"
    v = p.get(_ALIAS.get(field, field))
    return "none" if v is None else v


def vhd_value(data, ctx):
    if data is None:
        return None
    return field_value(data, ctx.get("field") or "")
