"""gzip (RFC 1952) member header / trailer fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Member header (little-endian): ID1 0x1f, ID2 0x8b, CM u8 (8 = deflate), FLG u8 (FTEXT 0x01, FHCRC 0x02, FEXTRA 0x04,
FNAME 0x08, FCOMMENT 0x10), MTIME u32 @4, XFL u8 @8, OS u8 @9; then by FLG: FEXTRA (XLEN u16 + XLEN bytes), FNAME
(zero-terminated ISO-8859-1), FCOMMENT (zero-terminated ISO-8859-1), FHCRC (CRC16 u16). Trailer = the last 8 bytes:
CRC32 u32, ISIZE u32 (uncompressed size mod 2^32) -- what `gzip -l` / `file` report ("original size modulo 2^32").
Only the FIRST member's header is read; ISIZE / CRC32 come from the file's last 8 bytes. No decompression.
Times: MTIME is Unix seconds (UTC). The bare name (header_mtime / mtime) and *_utc render ISO-8601 UTC
'YYYY-MM-DDTHH:MM:SSZ' (same spelling as lnk/pe *_utc); *_unix is the raw integer; *_u32_hex the raw u32.
MTIME 0 = "no time stamp is available" (RFC 1952) -> "none". FNAME/FCOMMENT flag clear -> "none".
header_os_u8_hex = the OS byte as 0x%02x (3 = Unix, 0 = FAT, 11 = NTFS, 255 = unknown; CPython's gzip writes 0xff);
header_os_name = the RFC 1952 name of that byte. Not gzip (wrong magic / truncated header) -> "none"."""
import datetime
import struct

from ..spell import Hex

FIELDS = {
    ("gzip", "header_mtime"): "gzip_value",
    ("gzip", "mtime"): "gzip_value",
    ("gzip", "header_mtime_utc"): "gzip_value",
    ("gzip", "mtime_utc"): "gzip_value",
    ("gzip", "header_mtime_unix"): "gzip_value",
    ("gzip", "mtime_unix"): "gzip_value",
    ("gzip", "header_mtime_u32_hex"): "gzip_value",
    ("gzip", "mtime_u32_hex"): "gzip_value",
    ("gzip", "header_original_filename"): "gzip_value",
    ("gzip", "original_filename"): "gzip_value",
    ("gzip", "header_original_name"): "gzip_value",
    ("gzip", "original_name"): "gzip_value",
    ("gzip", "header_filename"): "gzip_value",
    ("gzip", "header_fname"): "gzip_value",
    ("gzip", "fname"): "gzip_value",
    ("gzip", "header_comment"): "gzip_value",
    ("gzip", "header_fcomment"): "gzip_value",
    ("gzip", "fcomment"): "gzip_value",
    ("gzip", "header_os_u8_hex"): "gzip_value",
    ("gzip", "os_u8_hex"): "gzip_value",
    ("gzip", "header_os"): "gzip_value",
    ("gzip", "header_os_name"): "gzip_value",
    ("gzip", "os_name"): "gzip_value",
    ("gzip", "header_flags_u8_hex"): "gzip_value",
    ("gzip", "header_flg_u8_hex"): "gzip_value",
    ("gzip", "flags_u8_hex"): "gzip_value",
    ("gzip", "flg_u8_hex"): "gzip_value",
    ("gzip", "header_xfl_u8_hex"): "gzip_value",
    ("gzip", "xfl_u8_hex"): "gzip_value",
    ("gzip", "header_cm_u8_hex"): "gzip_value",
    ("gzip", "cm_u8_hex"): "gzip_value",
    ("gzip", "header_compression_method"): "gzip_value",
    ("gzip", "compression_method"): "gzip_value",
    ("gzip", "isize"): "gzip_value",
    ("gzip", "trailer_isize"): "gzip_value",
    ("gzip", "isize_bytes"): "gzip_value",
    ("gzip", "uncompressed_size"): "gzip_value",
    ("gzip", "original_size"): "gzip_value",
    ("gzip", "trailer_crc32_u32_hex"): "gzip_value",
    ("gzip", "crc32_u32_hex"): "gzip_value",
    ("gzip", "trailer_crc32_hex"): "gzip_value",
    ("gzip", "crc32_hex"): "gzip_value",
}

_OS = {0: "FAT", 1: "Amiga", 2: "VMS", 3: "Unix", 4: "VM/CMS", 5: "Atari TOS", 6: "HPFS", 7: "Macintosh",
       8: "Z-System", 9: "CP/M", 10: "TOPS-20", 11: "NTFS", 12: "QDOS", 13: "Acorn RISCOS", 255: "unknown"}


def _cstr(b, p):
    """(latin-1 text, offset past the NUL) of a zero-terminated header string, or (None, None) when unterminated."""
    end = b.find(b"\0", p)
    if end < 0:
        return None, None
    return bytes(b[p:end]).decode("latin-1"), end + 1


def parse_gzip(b):
    """The first member's header + the file trailer as a dict, or None (not gzip / truncated header)."""
    if not b or len(b) < 18 or bytes(b[:2]) != b"\x1f\x8b":
        return None
    cm, flg, mtime, xfl, os_ = struct.unpack_from("<BBIBB", b, 2)
    if flg & 0xE0:
        return None   # reserved bits set: gzip(1) refuses the file
    h = {"cm": cm, "flg": flg, "mtime": mtime, "xfl": xfl, "os": os_, "fname": None, "fcomment": None}
    p = 10
    if flg & 0x04:
        if p + 2 > len(b):
            return None
        xlen, = struct.unpack_from("<H", b, p)
        p += 2 + xlen
    if flg & 0x08:
        h["fname"], p = _cstr(b, p)
        if p is None:
            return None
    if flg & 0x10:
        h["fcomment"], p = _cstr(b, p)
        if p is None:
            return None
    if p > len(b) - 8:
        return None
    h["crc32"], h["isize"] = struct.unpack_from("<II", b, len(b) - 8)
    return h


def _iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gzip_value(data, ctx):
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- defensive: a hostile member never raises past the extractor
        return None


def _value(data, f):
    if data is None:
        return None
    h = parse_gzip(data)
    if h is None:
        return "none"
    if "mtime" in f:
        if f.endswith("_u32_hex"):
            return Hex(h["mtime"], 8)
        if not h["mtime"]:
            return "none"
        return h["mtime"] if f.endswith("_unix") else _iso(h["mtime"])
    if "name" in f and "os" not in f:
        return h["fname"] if h["fname"] is not None else "none"
    if "comment" in f:
        return h["fcomment"] if h["fcomment"] is not None else "none"
    if f.startswith(("header_os", "os")):
        if f.endswith("_hex"):
            return Hex(h["os"], 2)
        if f.endswith("_name"):
            return _OS.get(h["os"], "unknown")
        return h["os"]
    if "fl" in f and f.endswith("_hex"):
        return Hex(h["xfl"] if "xfl" in f else h["flg"], 2)
    if f.startswith(("header_cm", "cm")) or "compression_method" in f:
        return Hex(h["cm"], 2) if f.endswith("_hex") else ("deflate" if h["cm"] == 8 else h["cm"])
    if "crc32" in f:
        return Hex(h["crc32"], 8)
    if "size" in f:
        return h["isize"]
    return None
