"""ZIP per-member central-directory fields + the archive comment (prebuilt, SPECULATIVE -- never GM-asked yet).

APPNOTE 4.3.12 central directory header (all little-endian): "PK\\x01\\x02", version made by u16, version needed u16,
general purpose flags u16 (bit 0 = encrypted, bit 11 = UTF-8 name), compression method u16, last mod time u16,
last mod date u16, crc-32 u32, compressed size u32, uncompressed size u32, name len u16, extra len u16,
comment len u16, disk start u16, internal attrs u16, external attrs u32, local header offset u32, name, extra, comment.
Values come from the CENTRAL DIRECTORY (what `zipinfo -v` / `7z l -slt` / Python zipfile report), walked from the real
EOCD (the last "PK\\x05\\x06" whose comment ends at EOF, same rule as the GM-verified D7/D8 zipx logic); a 0xFFFFFFFF
size is replaced from the ZIP64 extra (0x0001). archive_comment = the EOCD comment (absent/empty -> "none").

Which member: the longest central-directory name that appears in the question text or in the artifact path after
'->' (a nested "a.zip -> b.zip -> c.txt"), else the only/first non-directory entry in CD order.
member_dos_mtime: the stored MS-DOS date/time has NO time zone, so it is rendered naive ISO-8601 "YYYY-MM-DDTHH:MM:SS"
(seconds are even; no "Z" -- the archive does not claim UTC); an answer_format asking for an integer/hex gets the raw
(date << 16 | time) u32 instead. member_compression_method: the APPNOTE method number (0 stored, 8 deflate, ...)
unless answer_format lists non-numeric accepted values, then the matching method name.
member_extra_field_ids: the CD extra block's header IDs in stored order as "0x%04x" strings (none -> "none")."""
import struct

from ..spell import Hex

FIELDS = {
    ("zip", "member_crc32_hex"): "member_value",
    ("zip", "member_crc32_u32_hex"): "member_value",
    ("zip", "member_crc_32_hex"): "member_value",
    ("zip", "crc32_hex"): "member_value",
    ("zip", "crc32_u32_hex"): "member_value",
    ("zip", "central_directory_crc32_hex"): "member_value",
    ("zip", "member_compression_method"): "member_value",
    ("zip", "compression_method"): "member_value",
    ("zip", "member_compression_method_u16_hex"): "member_value",
    ("zip", "member_dos_mtime"): "member_value",
    ("zip", "dos_mtime"): "member_value",
    ("zip", "member_mtime"): "member_value",
    ("zip", "member_last_mod_time"): "member_value",
    ("zip", "member_last_modified"): "member_value",
    ("zip", "member_last_mod_file_time"): "member_value",
    ("zip", "member_dos_datetime"): "member_value",
    ("zip", "member_uncompressed_size"): "member_value",
    ("zip", "uncompressed_size"): "member_value",
    ("zip", "member_compressed_size"): "member_value",
    ("zip", "compressed_size"): "member_value",
    ("zip", "member_is_encrypted"): "member_value",
    ("zip", "is_encrypted"): "member_value",
    ("zip", "member_encrypted"): "member_value",
    ("zip", "member_extra_field_ids"): "member_value",
    ("zip", "extra_field_ids"): "member_value",
    ("zip", "member_extra_field_header_ids"): "member_value",
    ("zip", "member_general_purpose_flags_u16_hex"): "member_value",
    ("zip", "member_general_purpose_bit_flag_u16_hex"): "member_value",
    ("zip", "member_flags_u16_hex"): "member_value",
    ("zip", "archive_comment"): "archive_comment",
    ("zip", "eocd_comment"): "archive_comment",
    ("zip", "zip_comment"): "archive_comment",
    ("zip", "comment"): "archive_comment",
}

_METHODS = {0: "stored", 1: "shrunk", 6: "imploded", 8: "deflated", 9: "deflate64", 12: "bzip2", 14: "lzma",
            93: "zstd", 95: "xz", 98: "ppmd", 99: "aes"}


def _dec(raw, utf8):
    if utf8:
        return raw.decode("utf-8", "replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp437")


def _eocd(b):
    """Offset of the real EOCD (comment ends at EOF; else the last one), or None."""
    i, last = len(b), None
    while True:
        i = b.rfind(b"PK\x05\x06", 0, i)
        if i < 0:
            return last
        if i + 22 <= len(b):
            if i + 22 + struct.unpack_from("<H", b, i + 20)[0] == len(b):
                return i
            if last is None:
                last = i


def _extras(ext):
    out, p = [], 0
    while p + 4 <= len(ext):
        hid, ln = struct.unpack_from("<HH", ext, p)
        out.append((hid, bytes(ext[p + 4:p + 4 + ln])))
        p += 4 + ln
    return out


def central_directory(b):
    """[dict per CD entry] in CD order, or None (not a zip / no central directory)."""
    eo = _eocd(b)
    if eo is None:
        return None
    _n, _cd_size, cd_off = struct.unpack_from("<HII", b, eo + 10)
    p = cd_off if b[cd_off:cd_off + 4] == b"PK\x01\x02" else b.find(b"PK\x01\x02")
    out = []
    while 0 <= p and b[p:p + 4] == b"PK\x01\x02" and p + 46 <= len(b):
        (_vm, _vn, flags, meth, mtime, mdate, crc, csize, usize, nl, el, cl) = struct.unpack_from("<HHHHHHIIIHHH", b, p + 4)
        name = _dec(bytes(b[p + 46:p + 46 + nl]), flags & 0x800)
        ext = _extras(b[p + 46 + nl:p + 46 + nl + el])
        for hid, body in ext:   # ZIP64: only the 0xFFFFFFFF fields are present, uncompressed size first
            if hid == 0x0001:
                q = 0
                if usize == 0xFFFFFFFF and q + 8 <= len(body):
                    usize = struct.unpack_from("<Q", body, q)[0]
                    q += 8
                if csize == 0xFFFFFFFF and q + 8 <= len(body):
                    csize = struct.unpack_from("<Q", body, q)[0]
        out.append({"name": name, "flags": flags, "method": meth, "time": mtime, "date": mdate, "crc": crc,
                    "csize": csize, "usize": usize, "extra_ids": [h for h, _ in ext]})
        p += 46 + nl + el + cl
    return out


def _pick(ents, ctx):
    q = ctx.get("question") or {}
    texts = [str(q.get("question") or "") if isinstance(q, dict) else ""]
    art = str(ctx.get("artifact") or "")
    texts += [s.strip() for s in art.split("->")[1:]]
    best = None
    for e in ents:
        n = e["name"]
        if n and any(n in t for t in texts) and (best is None or len(n) > len(best["name"])):
            best = e
    if best is None:
        tail = [s.strip() for s in art.split("->")[2:]]
        for e in ents:   # a nested path naming the entry by its base name
            if tail and e["name"].rsplit("/", 1)[-1] == tail[-1].rsplit("/", 1)[-1]:
                return e
    if best is not None:
        return best
    files = [e for e in ents if not e["name"].endswith("/")]
    return (files or ents or [None])[0]


def _fmt(ctx):
    q = ctx.get("question") or {}
    af = q.get("answer_format") if isinstance(q, dict) else None
    return af if isinstance(af, dict) else {}


def _dos_iso(date, time):
    y, mo, d = 1980 + (date >> 9), (date >> 5) & 0xF, date & 0x1F
    h, mi, s = time >> 11, (time >> 5) & 0x3F, (time & 0x1F) * 2
    return "%04d-%02d-%02dT%02d:%02d:%02d" % (y, mo, d, h, mi, s)


def member_value(data, ctx):
    if data is None:
        return None
    try:
        ents = central_directory(bytes(data))
        if not ents:
            return "none"
        e = _pick(ents, ctx)
        if e is None:
            return "none"
        f = ctx.get("field") or ""
        if "crc" in f:
            return Hex(e["crc"], 8)
        if "compression" in f:
            if f.endswith("_hex"):
                return Hex(e["method"], 4)
            acc = _fmt(ctx).get("accepted_values") or []
            if acc and not all(str(a).isdigit() for a in acc):
                name = _METHODS.get(e["method"], str(e["method"]))
                for a in acc:
                    al = str(a).lower()
                    if al == name or al.rstrip("d") == name.rstrip("d") or (name == "deflated" and al == "deflate"):
                        return str(a)
                return name
            return e["method"]
        if "mtime" in f or "mod" in f or "datetime" in f:
            af = _fmt(ctx)
            syn = (str(af.get("syntax") or "") + " " + str(af.get("kind") or "")).lower()
            raw = (e["date"] << 16) | e["time"]
            if "hex" in syn:
                return Hex(raw, 8)
            if af.get("kind") == "integer":
                return raw
            return _dos_iso(e["date"], e["time"])
        if "uncompressed" in f:
            return e["usize"]
        if "compressed" in f:
            return e["csize"]
        if "encrypt" in f:
            return bool(e["flags"] & 1)
        if "extra" in f:
            return ["0x%04x" % h for h in e["extra_ids"]] or "none"
        if "flag" in f:
            return Hex(e["flags"], 4)
    except (struct.error, ValueError, IndexError, TypeError):
        return None
    return None


def archive_comment(data, ctx):
    if data is None:
        return None
    try:
        b = bytes(data)
        eo = _eocd(b)
        if eo is None:
            return "none"
        cl = struct.unpack_from("<H", b, eo + 20)[0]
        c = _dec(b[eo + 22:eo + 22 + cl], False).strip()
        return c or "none"
    except (struct.error, ValueError, IndexError):
        return None
