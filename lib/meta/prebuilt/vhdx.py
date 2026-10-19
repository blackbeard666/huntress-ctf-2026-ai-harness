"""VHDX (Hyper-V virtual hard disk v2, [MS-VHDX]) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Little-endian. File type identifier @0: signature "vhdxfile", creator UTF-16LE 512 B @8 (NUL-terminated;
"QEMU v10.2.1", "Microsoft Windows 10.0.19045.0"). Headers @64 KiB and @128 KiB ("head", checksum u32, sequence_number
u64 @8, file_write_guid @16, data_write_guid @32, log_guid @48, log_version u16 @64, version u16 @66, log_length u32
@68, log_offset u64 @72) -- the CURRENT header is the valid one with the larger sequence number.
Region table @192 KiB ("regi", entry_count u32 @8, 32-B entries @16: guid, file_offset u64, length u32, required u32);
the metadata region (2DC27766-F623-4200-9D64-115E9BFD4A08) holds "metadata" table (entry_count u16 @10, 32-B entries
@32: item guid, offset u32, length u32, flags u32): File Parameters (block_size u32, flags: bit0
LeaveBlocksAllocated = fixed, bit1 HasParent), Virtual Disk Size u64, Virtual Disk ID guid, Logical/Physical Sector
Size u32. GUIDs are Windows binary GUIDs -> Guid("bytes_le") (lowercase 8-4-4-4-12). *_hex32 spellings (`7z` style
"6eca88ee...") via *_hex. Not a VHDX -> "none"; metadata fields of a carved header-only copy -> "none"."""
import struct
import uuid

from ..spell import Guid

FIELDS = {
    ("vhdx", "signature"): "vhdx_value",
    ("vhdx", "file_type_identifier"): "vhdx_value",
    ("vhdx", "creator"): "vhdx_value",
    ("vhdx", "creator_application"): "vhdx_value",
    ("vhdx", "file_identifier_creator"): "vhdx_value",
    ("vhdx", "sequence_number"): "vhdx_value",
    ("vhdx", "header_sequence_number"): "vhdx_value",
    ("vhdx", "file_write_guid"): "vhdx_value",
    ("vhdx", "data_write_guid"): "vhdx_value",
    ("vhdx", "log_guid"): "vhdx_value",
    ("vhdx", "log_version"): "vhdx_value",
    ("vhdx", "version"): "vhdx_value",
    ("vhdx", "header_version"): "vhdx_value",
    ("vhdx", "log_length"): "vhdx_value",
    ("vhdx", "log_length_bytes"): "vhdx_value",
    ("vhdx", "log_offset"): "vhdx_value",
    ("vhdx", "region_count"): "vhdx_value",
    ("vhdx", "region_table_entry_count"): "vhdx_value",
    ("vhdx", "bat_offset"): "vhdx_value",
    ("vhdx", "metadata_offset"): "vhdx_value",
    ("vhdx", "block_size"): "vhdx_value",
    ("vhdx", "block_size_bytes"): "vhdx_value",
    ("vhdx", "leave_blocks_allocated"): "vhdx_value",
    ("vhdx", "is_fixed"): "vhdx_value",
    ("vhdx", "disk_type"): "vhdx_value",
    ("vhdx", "has_parent"): "vhdx_value",
    ("vhdx", "virtual_disk_size"): "vhdx_value",
    ("vhdx", "virtual_disk_size_bytes"): "vhdx_value",
    ("vhdx", "virtual_size_bytes"): "vhdx_value",
    ("vhdx", "virtual_disk_id"): "vhdx_value",
    ("vhdx", "virtual_disk_id_guid"): "vhdx_value",
    ("vhdx", "virtual_disk_id_hex"): "vhdx_value",
    ("vhdx", "logical_sector_size"): "vhdx_value",
    ("vhdx", "logical_sector_size_bytes"): "vhdx_value",
    ("vhdx", "physical_sector_size"): "vhdx_value",
    ("vhdx", "physical_sector_size_bytes"): "vhdx_value",
}

_BAT_REGION = uuid.UUID("2DC27766-F623-4200-9D64-115E9BFD4A08").bytes_le
_META_REGION = uuid.UUID("8B7CA206-4790-4B9A-B8FE-575F050F886E").bytes_le
_ITEMS = {
    uuid.UUID("CAA16737-FA36-4D43-B3B6-33F0AA44E76B").bytes_le: "file_parameters",
    uuid.UUID("2FA54224-CD1B-4876-B211-5DBED83BF4B8").bytes_le: "virtual_disk_size",
    uuid.UUID("BECA12AB-B2E6-4523-93EF-C309E000C746").bytes_le: "virtual_disk_id",
    uuid.UUID("8141BF1D-A96F-4709-BA47-F233A8FAAB5F").bytes_le: "logical_sector_size",
    uuid.UUID("CDA348C7-445D-4471-9CC9-E9885251C556").bytes_le: "physical_sector_size",
}


def parse(data):
    """{field: raw value} of a VHDX, or None."""
    if not data or len(data) < 520 or data[:8] != b"vhdxfile":
        return None
    out = {"signature": "vhdxfile",
           "creator": data[8:520].decode("utf-16-le", "replace").split("\0")[0].strip() or "none"}
    best = None
    for off in (0x10000, 0x20000):
        h = data[off:off + 80]
        if len(h) == 80 and h[:4] == b"head":
            seq = struct.unpack_from("<Q", h, 8)[0]
            if best is None or seq > best[0]:
                best = (seq, h)
    if best:
        seq, h = best
        lver, ver, llen, loff = struct.unpack_from("<HHIQ", h, 64)
        out.update({"sequence_number": seq, "file_write_guid": Guid("bytes_le", h[16:32]),
                    "data_write_guid": Guid("bytes_le", h[32:48]),
                    "log_guid": Guid("bytes_le", h[48:64]) if any(h[48:64]) else "none",
                    "log_version": lver, "version": ver, "log_length": llen, "log_offset": loff})
    rt = data[0x30000:0x30000 + 65536]
    if len(rt) >= 16 and rt[:4] == b"regi":
        n = struct.unpack_from("<I", rt, 8)[0]
        out["region_count"] = n
        for i in range(min(n, 2047)):
            e = rt[16 + 32 * i:48 + 32 * i]
            if len(e) < 32:
                break
            foff = struct.unpack_from("<Q", e, 16)[0]
            if e[:16] == _BAT_REGION:
                out["bat_offset"] = foff
            elif e[:16] == _META_REGION:
                out["metadata_offset"] = foff
    mo = out.get("metadata_offset")
    if mo is not None and data[mo:mo + 8] == b"metadata":
        n = struct.unpack_from("<H", data, mo + 10)[0]
        for i in range(min(n, 2047)):
            e = data[mo + 32 + 32 * i:mo + 64 + 32 * i]
            if len(e) < 32:
                break
            name = _ITEMS.get(e[:16])
            ioff, ilen = struct.unpack_from("<II", e, 16)
            v = data[mo + ioff:mo + ioff + ilen]
            if name is None or len(v) < ilen or ilen < 4:
                continue
            if name == "file_parameters" and ilen >= 8:
                bsz, fl = struct.unpack_from("<II", v)
                out.update({"block_size": bsz, "leave_blocks_allocated": bool(fl & 1), "has_parent": bool(fl & 2),
                            "disk_type": "differencing" if fl & 2 else ("fixed" if fl & 1 else "dynamic")})
            elif name == "virtual_disk_size" and ilen >= 8:
                out[name] = struct.unpack_from("<Q", v)[0]
            elif name == "virtual_disk_id" and ilen >= 16:
                out[name] = Guid("bytes_le", v[:16])
                out["virtual_disk_id_hex"] = v[:16].hex()   # raw stored bytes (7-Zip "Id:" spelling)
            elif name in ("logical_sector_size", "physical_sector_size"):
                out[name] = struct.unpack_from("<I", v)[0]
    return out


_ALIAS = {"file_type_identifier": "signature", "creator_application": "creator", "file_identifier_creator": "creator",
          "header_sequence_number": "sequence_number", "header_version": "version", "log_length_bytes": "log_length",
          "region_table_entry_count": "region_count", "block_size_bytes": "block_size",
          "is_fixed": "leave_blocks_allocated", "virtual_disk_size_bytes": "virtual_disk_size",
          "virtual_size_bytes": "virtual_disk_size", "virtual_disk_id_guid": "virtual_disk_id",
          "logical_sector_size_bytes": "logical_sector_size", "physical_sector_size_bytes": "physical_sector_size"}


def field_value(data, field):
    try:
        p = parse(data)
    except (struct.error, ValueError, IndexError):
        p = None
    if p is None:
        return "none"
    v = p.get(_ALIAS.get(field, field))
    return "none" if v is None else v


def vhdx_value(data, ctx):
    if data is None:
        return None
    return field_value(data, ctx.get("field") or "")
