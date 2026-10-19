"""VMDK (VMware virtual disk) sparse header + embedded descriptor fields (prebuilt, SPECULATIVE -- never GM-asked).

Hosted sparse extent header (little-endian, VMware "Virtual Disk Format 1.1"): magic "KDMV" @0, version u32 @4, flags
u32 @8, capacity u64 @12 (sectors), grainSize u64 @20 (sectors), descriptorOffset u64 @28 (sectors),
descriptorSize u64 @36 (sectors), numGTEsPerGT u32 @44, rgdOffset u64 @48, gdOffset u64 @56, overHead u64 @64,
uncleanShutdown u8 @72, compressAlgorithm u16 @77. The descriptor (embedded at descriptorOffset*512, or the whole
member when it is a stand-alone text descriptor "# Disk DescriptorFile") is `key=value` lines: version, CID,
parentCID, createType, parentFileNameHint; extent lines `RW <sectors> SPARSE|FLAT|... "<file>" [offset]`; and
`ddb.<key> = "<value>"` entries.
Spellings: descriptor values VERBATIM as stored, quotes stripped (CID "36d658a5" lowercase hex text as written --
7-Zip "ID = 36d658a5"; parentCID "ffffffff" = no parent); cid_u32_hex / parent_cid_u32_hex = Hex of the same u32.
ddb keys map camelCase -> snake_case (`ddb.virtualHWVersion` -> ddb_virtual_hw_version, `ddb.adapterType` ->
ddb_adapter_type / adapter_type, `ddb.uuid` -> ddb_uuid, `ddb.geometry.heads` -> ddb_geometry_heads); any other
`ddb.*` key via the ddb_* family. extent_files = the quoted file names in stored order (list); capacity_sectors raw,
capacity_bytes / virtual_size_bytes = sectors * 512. Not a VMDK -> "none"; key absent -> "none"."""
import re
import struct

from ..spell import Hex

FIELDS = {
    ("vmdk", "magic"): "vmdk_value",
    ("vmdk", "sparse_header_version"): "vmdk_value",
    ("vmdk", "header_version"): "vmdk_value",
    ("vmdk", "flags_u32_hex"): "vmdk_value",
    ("vmdk", "capacity"): "vmdk_value",
    ("vmdk", "capacity_sectors"): "vmdk_value",
    ("vmdk", "capacity_bytes"): "vmdk_value",
    ("vmdk", "virtual_size_bytes"): "vmdk_value",
    ("vmdk", "size_bytes"): "vmdk_value",
    ("vmdk", "grain_size"): "vmdk_value",
    ("vmdk", "grain_size_sectors"): "vmdk_value",
    ("vmdk", "grain_size_bytes"): "vmdk_value",
    ("vmdk", "descriptor_offset"): "vmdk_value",
    ("vmdk", "descriptor_size"): "vmdk_value",
    ("vmdk", "num_gtes_per_gt"): "vmdk_value",
    ("vmdk", "overhead"): "vmdk_value",
    ("vmdk", "unclean_shutdown"): "vmdk_value",
    ("vmdk", "compress_algorithm"): "vmdk_value",
    ("vmdk", "descriptor_version"): "vmdk_value",
    ("vmdk", "version"): "vmdk_value",
    ("vmdk", "cid"): "vmdk_value",
    ("vmdk", "content_id"): "vmdk_value",
    ("vmdk", "cid_u32_hex"): "vmdk_value",
    ("vmdk", "parent_cid"): "vmdk_value",
    ("vmdk", "parent_content_id"): "vmdk_value",
    ("vmdk", "parent_cid_u32_hex"): "vmdk_value",
    ("vmdk", "create_type"): "vmdk_value",
    ("vmdk", "createtype"): "vmdk_value",
    ("vmdk", "parent_file_name_hint"): "vmdk_value",
    ("vmdk", "parent_filename_hint"): "vmdk_value",
    ("vmdk", "has_parent"): "vmdk_value",
    ("vmdk", "encoding"): "vmdk_value",
    ("vmdk", "extent_files"): "vmdk_value",
    ("vmdk", "extent_file_names"): "vmdk_value",
    ("vmdk", "extent_filenames"): "vmdk_value",
    ("vmdk", "extent_count"): "vmdk_value",
    ("vmdk", "extent_types"): "vmdk_value",
    ("vmdk", "extent_access"): "vmdk_value",
    ("vmdk", "extent_sizes_sectors"): "vmdk_value",
    ("vmdk", "extents"): "vmdk_value",
    ("vmdk", "ddb_uuid"): "vmdk_value",
    ("vmdk", "uuid"): "vmdk_value",
    ("vmdk", "ddb_virtual_hw_version"): "vmdk_value",
    ("vmdk", "virtual_hw_version"): "vmdk_value",
    ("vmdk", "hw_version"): "vmdk_value",
    ("vmdk", "ddb_adapter_type"): "vmdk_value",
    ("vmdk", "adapter_type"): "vmdk_value",
    ("vmdk", "ddb_tools_version"): "vmdk_value",
    ("vmdk", "tools_version"): "vmdk_value",
    ("vmdk", "ddb_long_content_id"): "vmdk_value",
    ("vmdk", "long_content_id"): "vmdk_value",
    ("vmdk", "ddb_geometry_cylinders"): "vmdk_value",
    ("vmdk", "ddb_geometry_heads"): "vmdk_value",
    ("vmdk", "ddb_geometry_sectors"): "vmdk_value",
    ("vmdk", "ddb_*"): "vmdk_value",
    ("vmdk", "ddb_keys"): "vmdk_value",
}

_EXTENT = re.compile(r'^(RW|RDONLY|NOACCESS)\s+(\d+)\s+(\w+)(?:\s+"([^"]*)")?', re.M)
_KV = re.compile(r'^\s*([A-Za-z][\w.]*)\s*=\s*"?([^"\r\n]*?)"?\s*$', re.M)


def _snake(k):
    k = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", k)
    k = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", k)
    return k.replace(".", "_").lower()


def descriptor(data):
    """(header dict or None, descriptor text or None) -- None, None when not a VMDK."""
    hdr = None
    if data[:4] == b"KDMV" and len(data) >= 79:
        (ver, fl, cap, grain, doff, dsz, ngte, _rgd, _gd, ovh, unclean) = struct.unpack_from("<IIQQQQIQQQB", data, 4)
        comp = struct.unpack_from("<H", data, 77)[0]
        hdr = {"magic": "KDMV", "sparse_header_version": ver, "flags_u32_hex": Hex(fl, 8), "capacity_sectors": cap,
               "capacity_bytes": cap * 512, "grain_size": grain, "grain_size_bytes": grain * 512,
               "descriptor_offset": doff, "descriptor_size": dsz, "num_gtes_per_gt": ngte, "overhead": ovh,
               "unclean_shutdown": bool(unclean), "compress_algorithm": comp}
        raw = data[doff * 512:(doff + dsz) * 512] if doff and dsz else b""
        return hdr, raw.split(b"\0")[0].decode("utf-8", "replace") or None
    head = data[:4096].lstrip()
    if head.startswith(b"# Disk DescriptorFile") or (b"createType" in head and b"CID=" in head):
        return None, data[:1 << 20].split(b"\0")[0].decode("utf-8", "replace")
    return None, None


def parse(data):
    if not data:
        return None
    hdr, text = descriptor(data)
    if hdr is None and text is None:
        return None
    out = dict(hdr or {})
    if text:
        kv = {}
        for k, v in _KV.findall(text):
            kv.setdefault(k, v.strip())
        out["_kv"] = kv
        for k, v in kv.items():
            if not k.startswith("ddb."):
                out.setdefault({"version": "descriptor_version", "CID": "cid", "parentCID": "parent_cid"}.get(
                    k, _snake(k)), v)
            else:
                out.setdefault("ddb_" + _snake(k[4:]), v)
        out["ddb_keys"] = [k for k in kv if k.startswith("ddb.")]
        for name in ("cid", "parent_cid"):
            if re.fullmatch(r"[0-9a-fA-F]{1,8}", out.get(name) or ""):
                out[name + "_u32_hex"] = Hex(int(out[name], 16), 8)
        if "parent_cid" in out:
            out["has_parent"] = out["parent_cid"].lower() != "ffffffff"
        ext = _EXTENT.findall(text)
        out.update({"extent_files": [e[3] for e in ext if e[3]], "extent_count": len(ext),
                    "extent_types": [e[2] for e in ext], "extent_access": [e[0] for e in ext],
                    "extent_sizes_sectors": [int(e[1]) for e in ext],
                    "extents": [m.group(0).strip() for m in re.finditer(r"^(?:RW|RDONLY|NOACCESS)\s.*$", text, re.M)]})
        if hdr is None and ext:
            out["capacity_sectors"] = sum(int(e[1]) for e in ext)
            out["capacity_bytes"] = out["capacity_sectors"] * 512
    return out


_ALIAS = {"header_version": "sparse_header_version", "capacity": "capacity_sectors",
          "virtual_size_bytes": "capacity_bytes", "size_bytes": "capacity_bytes", "grain_size_sectors": "grain_size",
          "version": "descriptor_version", "content_id": "cid", "parent_content_id": "parent_cid",
          "createtype": "create_type", "parent_filename_hint": "parent_file_name_hint",
          "extent_file_names": "extent_files", "extent_filenames": "extent_files", "uuid": "ddb_uuid",
          "virtual_hw_version": "ddb_virtual_hw_version", "hw_version": "ddb_virtual_hw_version",
          "adapter_type": "ddb_adapter_type", "tools_version": "ddb_tools_version",
          "long_content_id": "ddb_long_content_id"}


def field_value(data, field):
    try:
        p = parse(data)
    except (struct.error, ValueError, IndexError):
        p = None
    if p is None:
        return "none"
    f = _ALIAS.get(field, field)
    v = p.get(f)
    if v is None and f.startswith("ddb_"):     # ddb_* family: compare the squashed key ("ddb_virtualhwversion")
        want = f[4:].replace("_", "")
        v = next((vv for k, vv in p.get("_kv", {}).items()
                  if k.startswith("ddb.") and k[4:].replace(".", "").replace("_", "").lower() == want), None)
    if f == "parent_file_name_hint" and v is None and "cid" in p:
        v = "none"
    return "none" if v is None or v == "" else v


def vmdk_value(data, ctx):
    if data is None:
        return None
    return field_value(data, ctx.get("field") or "")
