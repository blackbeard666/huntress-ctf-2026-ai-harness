"""CPython .pyc header fields (importlib/_bootstrap_external, PEP 552; prebuilt, SPECULATIVE -- never GM-asked yet).

Header (little-endian): magic u16 @0 + b'\\r\\n' @2 (MAGIC_NUMBER = u16 LE + CRLF); then
  3.7+ (magic >= 3390, 16 bytes): flags u32 @4 (bit 0 = hash-based, bit 1 = check_source);
     flags & 1 == 0 -> source mtime u32 @8 (unix seconds) + source size u32 @12 (st_size mod 2^32);
     flags & 1 == 1 -> SipHash of the source, 8 raw bytes @8 (mtime/size absent -> "none").
  3.3-3.6 (12 bytes): mtime u32 @4, size u32 @8.  <= 3.2 / 2.x (8 bytes): mtime u32 @4.
magic_u16 = the decimal u16 (3531); magic_u32_hex = the 4 header bytes read as LE u32 (0x0a0d0dcb).
python_version from the magic RANGE of each release line (3.8 3400-3413 ... 3.12 3500-3531, 3.13 3550-3571,
3.14 3600-3627...) -> "3.12" ("none" for an unknown magic). source_mtime / *_utc render ISO-8601 UTC
'YYYY-MM-DDTHH:MM:SSZ' (same spelling as gzip/lnk *_utc); *_unix the raw integer.
Not a pyc (no CRLF after the magic / truncated) -> "none"."""
import datetime
import struct

from ..spell import Hex

FIELDS = {
    ("pyc", "magic_u16"): "pyc_value",
    ("pyc", "magic_number"): "pyc_value",
    ("pyc", "magic"): "pyc_value",
    ("pyc", "magic_u32_hex"): "pyc_value",
    ("pyc", "magic_u16_hex"): "pyc_value",
    ("pyc", "python_version"): "pyc_value",
    ("pyc", "version"): "pyc_value",
    ("pyc", "flags_u32_hex"): "pyc_value",
    ("pyc", "flags"): "pyc_value",
    ("pyc", "bit_field_u32_hex"): "pyc_value",
    ("pyc", "invalidation_mode"): "pyc_value",
    ("pyc", "is_hash_based"): "pyc_value",
    ("pyc", "hash_based"): "pyc_value",
    ("pyc", "source_mtime"): "pyc_value",
    ("pyc", "source_mtime_utc"): "pyc_value",
    ("pyc", "source_mtime_unix"): "pyc_value",
    ("pyc", "mtime"): "pyc_value",
    ("pyc", "mtime_utc"): "pyc_value",
    ("pyc", "mtime_unix"): "pyc_value",
    ("pyc", "source_mtime_u32_hex"): "pyc_value",
    ("pyc", "source_size"): "pyc_value",
    ("pyc", "source_size_bytes"): "pyc_value",
    ("pyc", "source_hash_hex"): "pyc_value",
    ("pyc", "source_hash_u64_hex"): "pyc_value",
    ("pyc", "header_size"): "pyc_value",
    ("pyc", "header_size_bytes"): "pyc_value",
    ("pyc", "code_object_offset"): "pyc_value",
}

# (first, last, version) -- final-release magic ranges from importlib/_bootstrap_external.py history
_VERSIONS = [(20121, 20121, "1.5"), (50428, 50428, "1.6"), (50823, 50823, "2.0"), (60202, 60202, "2.1"),
             (60717, 60717, "2.2"), (62011, 62021, "2.3"), (62041, 62061, "2.4"), (62071, 62131, "2.5"),
             (62151, 62161, "2.6"), (62171, 62211, "2.7"), (3000, 3131, "3.0"), (3141, 3151, "3.1"),
             (3160, 3180, "3.2"), (3190, 3230, "3.3"), (3250, 3310, "3.4"), (3320, 3351, "3.5"),
             (3360, 3379, "3.6"), (3390, 3399, "3.7"), (3400, 3419, "3.8"), (3420, 3429, "3.9"),
             (3430, 3449, "3.10"), (3450, 3499, "3.11"), (3500, 3549, "3.12"), (3550, 3599, "3.13"),
             (3600, 3649, "3.14"), (3650, 3699, "3.15")]


def _version(magic):
    for lo, hi, v in _VERSIONS:
        if lo <= magic <= hi:
            return v
    return None


def _utc(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pyc_value(data, ctx):
    try:
        return _pyc_value(data, (ctx or {}).get("field") or "")
    except (struct.error, ValueError, OverflowError, OSError):
        return "none"


def _pyc_value(b, field):
    if b is None:
        return None
    if not isinstance(b, (bytes, bytearray)) or len(b) < 8 or b[2:4] != b"\r\n":
        return "none"
    magic, = struct.unpack_from("<H", b, 0)
    ver = _version(magic)
    if ver is None:
        return "none"
    if field in ("magic_u16", "magic_number", "magic"):
        return magic
    if field == "magic_u16_hex":
        return Hex(magic, 4)
    if field == "magic_u32_hex":
        return Hex(struct.unpack_from("<I", b, 0)[0], 8)
    if field in ("python_version", "version"):
        return ver
    pep552 = 3390 <= magic < 20000
    hdr = 16 if pep552 else (12 if 3190 <= magic < 20000 else 8)
    if len(b) < hdr:
        return "none"
    if field in ("header_size", "header_size_bytes", "code_object_offset"):
        return hdr
    flags = struct.unpack_from("<I", b, 4)[0] if pep552 else None
    if field in ("flags_u32_hex", "flags", "bit_field_u32_hex"):
        return Hex(flags, 8) if flags is not None else "none"
    hashed = bool(flags is not None and flags & 1)
    if field in ("is_hash_based", "hash_based"):
        return hashed
    if field == "invalidation_mode":
        if not hashed:
            return "timestamp"
        return "checked_hash" if flags & 2 else "unchecked_hash"
    if field in ("source_hash_hex", "source_hash_u64_hex"):
        return bytes(b[8:16]).hex() if hashed else "none"
    if hashed:
        return "none"
    mo = 8 if pep552 else 4
    if field.startswith("source_size"):
        return struct.unpack_from("<I", b, mo + 4)[0] if hdr >= 12 else "none"
    if "mtime" in field:
        t, = struct.unpack_from("<I", b, mo)
        if field.endswith("_unix"):
            return t
        if field.endswith("_u32_hex"):
            return Hex(t, 8)
        return _utc(t)
    return None
