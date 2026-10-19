"""QCOW / QCOW2 (QEMU copy-on-write) header fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Header (BIG-endian, qemu docs/interop/qcow2.txt): magic "QFI\\xfb" @0, version u32 @4 (2 or 3; 1 = legacy QCOW),
backing_file_offset u64 @8, backing_file_size u32 @16, cluster_bits u32 @20, size u64 @24 (virtual bytes),
crypt_method u32 @32 (0 none, 1 AES, 2 LUKS), l1_size u32 @36, l1_table_offset u64 @40, refcount_table_offset u64
@48, refcount_table_clusters u32 @56, nb_snapshots u32 @60, snapshots_offset u64 @64; v3 adds incompatible /
compatible / autoclear features u64 @72/@80/@88, refcount_order u32 @96, header_length u32 @100, compression_type u8
@104 (when header_length > 104). Header extensions follow the header (v2: @72): type u32, length u32, data padded to
8 -- 0xE2792ACA = backing file format name. Legacy v1: backing_file_offset u64 @8, backing_file_size u32 @16, mtime
u32 @20, size u64 @24, cluster_bits u8 @32, l2_bits u8 @33, crypt_method u32 @36.
backing_file_name = the backing_file_size bytes at backing_file_offset (no backing file -> "none"); cluster_size =
1 << cluster_bits; compat = "0.10" (v2) / "1.1" (v3) as qemu-img info prints. Not QCOW -> "none"."""
import struct

from ..spell import Hex

FIELDS = {
    ("qcow2", "magic"): "qcow2_value",
    ("qcow2", "magic_u32_hex"): "qcow2_value",
    ("qcow2", "version"): "qcow2_value",
    ("qcow2", "header_version"): "qcow2_value",
    ("qcow2", "compat"): "qcow2_value",
    ("qcow2", "size"): "qcow2_value",
    ("qcow2", "size_bytes"): "qcow2_value",
    ("qcow2", "virtual_size"): "qcow2_value",
    ("qcow2", "virtual_size_bytes"): "qcow2_value",
    ("qcow2", "backing_file"): "qcow2_value",
    ("qcow2", "backing_file_name"): "qcow2_value",
    ("qcow2", "backing_filename"): "qcow2_value",
    ("qcow2", "backing_file_offset"): "qcow2_value",
    ("qcow2", "backing_file_size"): "qcow2_value",
    ("qcow2", "backing_file_format"): "qcow2_value",
    ("qcow2", "backing_format"): "qcow2_value",
    ("qcow2", "has_backing_file"): "qcow2_value",
    ("qcow2", "cluster_bits"): "qcow2_value",
    ("qcow2", "cluster_size"): "qcow2_value",
    ("qcow2", "cluster_size_bytes"): "qcow2_value",
    ("qcow2", "crypt_method"): "qcow2_value",
    ("qcow2", "crypt_method_name"): "qcow2_value",
    ("qcow2", "encryption_method"): "qcow2_value",
    ("qcow2", "is_encrypted"): "qcow2_value",
    ("qcow2", "encrypted"): "qcow2_value",
    ("qcow2", "l1_size"): "qcow2_value",
    ("qcow2", "l1_table_offset"): "qcow2_value",
    ("qcow2", "refcount_table_offset"): "qcow2_value",
    ("qcow2", "refcount_table_clusters"): "qcow2_value",
    ("qcow2", "nb_snapshots"): "qcow2_value",
    ("qcow2", "snapshot_count"): "qcow2_value",
    ("qcow2", "number_of_snapshots"): "qcow2_value",
    ("qcow2", "snapshots_offset"): "qcow2_value",
    ("qcow2", "incompatible_features_u64_hex"): "qcow2_value",
    ("qcow2", "compatible_features_u64_hex"): "qcow2_value",
    ("qcow2", "autoclear_features_u64_hex"): "qcow2_value",
    ("qcow2", "refcount_order"): "qcow2_value",
    ("qcow2", "refcount_bits"): "qcow2_value",
    ("qcow2", "header_length"): "qcow2_value",
    ("qcow2", "compression_type"): "qcow2_value",
    ("qcow2", "header_extension_types"): "qcow2_value",
}

_CRYPT = {0: "none", 1: "aes", 2: "luks"}


def parse(data):
    if not data or len(data) < 48 or data[:4] != b"QFI\xfb":
        return None
    ver = struct.unpack_from(">I", data, 4)[0]
    out = {"magic": "QFI\\xfb", "magic_u32_hex": Hex(0x514649FB, 8), "version": ver}
    if ver == 1:
        boff, bsz, _mt, size, cbits, _l2, cm = struct.unpack_from(">QIIQBBxxI", data, 8)
        out.update({"size": size, "cluster_bits": cbits, "crypt_method": cm})
        ext_at = None
    else:
        if len(data) < 72:
            return None
        (boff, bsz, cbits, size, cm, l1, l1off, rtoff, rtcl, nsnap, snoff) = struct.unpack_from(">QIIQIIQQIIQ", data, 8)
        out.update({"size": size, "cluster_bits": cbits, "crypt_method": cm, "l1_size": l1, "l1_table_offset": l1off,
                    "refcount_table_offset": rtoff, "refcount_table_clusters": rtcl, "nb_snapshots": nsnap,
                    "snapshots_offset": snoff, "compat": "0.10" if ver == 2 else "1.1"})
        hlen, rorder = 72, 4
        if ver >= 3 and len(data) >= 104:
            inc, comp, auto, rorder, hlen = struct.unpack_from(">QQQII", data, 72)
            out.update({"incompatible_features_u64_hex": Hex(inc, 16), "compatible_features_u64_hex": Hex(comp, 16),
                        "autoclear_features_u64_hex": Hex(auto, 16), "header_length": hlen})
            out["compression_type"] = ({0: "zlib", 1: "zstd"}.get(data[104], data[104])
                                       if hlen > 104 and len(data) > 104 else "zlib")
        out.update({"refcount_order": rorder, "refcount_bits": 1 << rorder})
        ext_at = hlen
    out["cluster_size"] = 1 << out["cluster_bits"] if out["cluster_bits"] < 64 else None
    out["crypt_method_name"] = _CRYPT.get(cm, str(cm))
    out["is_encrypted"] = cm != 0
    out["backing_file_offset"], out["backing_file_size"] = boff, bsz
    out["has_backing_file"] = bool(boff and bsz)
    if boff and bsz and boff + bsz <= len(data):
        out["backing_file_name"] = data[boff:boff + bsz].decode("utf-8", "replace")
    types = []
    o = ext_at
    while o is not None and o + 8 <= len(data) and len(types) < 64:
        t, ln = struct.unpack_from(">II", data, o)
        if t == 0:
            break
        types.append(Hex(t, 8))
        if t == 0xE2792ACA:
            out["backing_file_format"] = data[o + 8:o + 8 + ln].decode("utf-8", "replace")
        o += 8 + ((ln + 7) & ~7)
    out["header_extension_types"] = types
    return out


_ALIAS = {"header_version": "version", "size_bytes": "size", "virtual_size": "size", "virtual_size_bytes": "size",
          "backing_file": "backing_file_name", "backing_filename": "backing_file_name",
          "backing_format": "backing_file_format", "cluster_size_bytes": "cluster_size",
          "encryption_method": "crypt_method_name", "encrypted": "is_encrypted", "snapshot_count": "nb_snapshots",
          "number_of_snapshots": "nb_snapshots"}


def field_value(data, field):
    try:
        p = parse(data)
    except (struct.error, ValueError, IndexError):
        p = None
    if p is None:
        return "none"
    v = p.get(_ALIAS.get(field, field))
    return "none" if v is None else v


def qcow2_value(data, ctx):
    if data is None:
        return None
    return field_value(data, ctx.get("field") or "")
