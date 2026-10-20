"""Android DEX header fields (dalvik/dex-format header_item; prebuilt, SPECULATIVE -- never GM-asked yet).

header_item (little-endian, 0x70 bytes): magic 'dex\\n' + 3-digit version + '\\0' @0 (version '035', '037', '038',
'039', '040' -> the 3 digits as stored); checksum u32 @8 = adler32 of bytes [12:]; signature 20 bytes @12 = SHA-1 of
bytes [32:] (lowercase hex as stored); file_size u32 @32; header_size @36 (0x70); endian_tag @40 (0x12345678);
link_size/off @44/48; map_off @52; then (size, off) u32 pairs: string_ids @56, type_ids @64, proto_ids @72,
field_ids @80, method_ids @88, class_defs @96, data @104.
*_valid = the stored checksum/signature equals the one recomputed over the bytes (bool).
Not a DEX (wrong magic / < 0x70 bytes) -> "none"."""
import hashlib
import struct
import zlib

from ..spell import Hex

FIELDS = {
    ("dex", "magic"): "dex_value",
    ("dex", "dex_magic"): "dex_value",
    ("dex", "version"): "dex_value",
    ("dex", "dex_version"): "dex_value",
    ("dex", "format_version"): "dex_value",
    ("dex", "checksum_u32_hex"): "dex_value",
    ("dex", "adler32_u32_hex"): "dex_value",
    ("dex", "checksum_valid"): "dex_value",
    ("dex", "signature_sha1_hex"): "dex_value",
    ("dex", "signature_hex"): "dex_value",
    ("dex", "sha1_signature_hex"): "dex_value",
    ("dex", "signature_valid"): "dex_value",
    ("dex", "file_size"): "dex_value",
    ("dex", "file_size_bytes"): "dex_value",
    ("dex", "header_size"): "dex_value",
    ("dex", "endian_tag_u32_hex"): "dex_value",
    ("dex", "link_size"): "dex_value",
    ("dex", "map_off"): "dex_value",
    ("dex", "map_off_u32_hex"): "dex_value",
    ("dex", "string_ids_size"): "dex_value",
    ("dex", "string_ids_count"): "dex_value",
    ("dex", "string_count"): "dex_value",
    ("dex", "type_ids_size"): "dex_value",
    ("dex", "type_ids_count"): "dex_value",
    ("dex", "proto_ids_size"): "dex_value",
    ("dex", "proto_ids_count"): "dex_value",
    ("dex", "field_ids_size"): "dex_value",
    ("dex", "field_ids_count"): "dex_value",
    ("dex", "method_ids_size"): "dex_value",
    ("dex", "method_ids_count"): "dex_value",
    ("dex", "method_count"): "dex_value",
    ("dex", "class_defs_size"): "dex_value",
    ("dex", "class_defs_count"): "dex_value",
    ("dex", "class_count"): "dex_value",
    ("dex", "data_size"): "dex_value",
    ("dex", "data_off"): "dex_value",
}

_SIZES = {"string_ids": 56, "type_ids": 64, "proto_ids": 72, "field_ids": 80, "method_ids": 88, "class_defs": 96}
_ALIASES = {"string_count": "string_ids_size", "method_count": "method_ids_size", "class_count": "class_defs_size"}


def dex_value(data, ctx):
    try:
        return _dex_value(data, (ctx or {}).get("field") or "")
    except (struct.error, ValueError):
        return "none"


def _dex_value(b, field):
    if b is None:
        return None
    if (not isinstance(b, (bytes, bytearray)) or len(b) < 0x70 or b[:4] != b"dex\n" or b[7] != 0
            or not bytes(b[4:7]).isdigit()):
        return "none"
    ver = bytes(b[4:7]).decode()
    field = _ALIASES.get(field, field)
    if field in ("magic", "dex_magic"):
        return "dex\\n%s\\0" % ver
    if field in ("version", "dex_version", "format_version"):
        return ver
    ck, = struct.unpack_from("<I", b, 8)
    if field in ("checksum_u32_hex", "adler32_u32_hex"):
        return Hex(ck, 8)
    if field == "checksum_valid":
        return ck == zlib.adler32(bytes(b[12:])) & 0xFFFFFFFF
    sig = bytes(b[12:32])
    if field in ("signature_sha1_hex", "signature_hex", "sha1_signature_hex"):
        return sig.hex()
    if field == "signature_valid":
        return sig == hashlib.sha1(bytes(b[32:])).digest()
    simple = {"file_size": 32, "file_size_bytes": 32, "header_size": 36, "link_size": 44, "map_off": 52,
              "data_size": 104, "data_off": 108}
    if field in simple:
        return struct.unpack_from("<I", b, simple[field])[0]
    if field == "endian_tag_u32_hex":
        return Hex(struct.unpack_from("<I", b, 40)[0], 8)
    if field == "map_off_u32_hex":
        return Hex(struct.unpack_from("<I", b, 52)[0], 8)
    for k, off in _SIZES.items():
        if field in (k + "_size", k + "_count"):
            return struct.unpack_from("<I", b, off)[0]
    return None
