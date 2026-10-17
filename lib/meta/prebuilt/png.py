"""PNG chunk-stream fields (prebuilt, SPECULATIVE -- never GM-asked yet). png.ihdr_dimensions_pixels is GM-verified
(D5) in lib/meta/images.py and deliberately NOT registered here.

Layout (PNG spec / RFC 2083): 8-byte signature 89 50 4E 47 0D 0A 1A 0A, then chunks: length u32be, type[4], data,
CRC u32be. IHDR (first chunk, 13 bytes): width u32, height u32, bit depth u8, colour type u8 (0 grey, 2 RGB,
3 palette, 4 grey+alpha, 6 RGBA), compression u8, filter u8, interlace u8. The walk stops at IEND (bytes appended
after IEND are not chunks) or at a truncated chunk; CRCs are not enforced (the stored names/values are still the data).
Text chunks: tEXt = keyword \\0 latin-1 text; zTXt = keyword \\0 method u8 zlib(latin-1 text); iTXt = keyword \\0
compression flag u8, method u8, language tag \\0, translated keyword \\0, UTF-8 text (zlib'd when the flag is 1).
text_chunks = {keyword: text} of every tEXt/zTXt/iTXt in stored order (first occurrence of a keyword wins; exiftool
shows the same keyword/value pairs). text_<keyword> / text_chunk_<keyword> = that keyword's text, matched
case-insensitively with spaces/underscores/dashes folded ("text_creation_time" -> "Creation Time").
tIME = year u16, month, day, hour, minute, second u8 -- the spec says it is UTC, so the bare name renders ISO-8601
'YYYY-MM-DDTHH:MM:SSZ' (same spelling as gzip/lnk/pe *_utc); exiftool calls it PNG:ModifyDate.
chunk_names = every chunk type in stored order, duplicates kept (["IHDR","tEXt","IDAT","IDAT","IEND"]).
Not a PNG signature (decoy / renamed file) -> "none"; an absent tIME / text keyword -> "none"."""
import re
import struct
import zlib

FIELDS = {
    ("png", "text_chunks"): "png_value",
    ("png", "text_chunk_entries"): "png_value",
    ("png", "textual_chunks"): "png_value",
    ("png", "text_chunk_key_values"): "png_value",
    ("png", "text_metadata"): "png_value",
    ("png", "text_keywords"): "png_value",
    ("png", "text_chunk_keywords"): "png_value",
    ("png", "text_chunk_count"): "png_value",
    ("png", "text_*"): "png_value",
    ("png", "text_chunk_*"): "png_value",
    ("png", "itxt_*"): "png_value",
    ("png", "ztxt_*"): "png_value",
    ("png", "time_chunk"): "png_value",
    ("png", "time_chunk_utc"): "png_value",
    ("png", "time_chunk_iso8601"): "png_value",
    ("png", "time"): "png_value",
    ("png", "time_utc"): "png_value",
    ("png", "last_modification_time"): "png_value",
    ("png", "modification_time"): "png_value",
    ("png", "modify_date"): "png_value",
    ("png", "chunk_names"): "png_value",
    ("png", "chunk_types"): "png_value",
    ("png", "chunk_order"): "png_value",
    ("png", "chunk_list"): "png_value",
    ("png", "chunk_type_names"): "png_value",
    ("png", "chunk_count"): "png_value",
    ("png", "ancillary_chunk_names"): "png_value",
    ("png", "idat_count"): "png_value",
    ("png", "idat_chunk_count"): "png_value",
    ("png", "ihdr_bit_depth"): "png_value",
    ("png", "bit_depth"): "png_value",
    ("png", "ihdr_color_type"): "png_value",
    ("png", "ihdr_colour_type"): "png_value",
    ("png", "color_type"): "png_value",
    ("png", "colour_type"): "png_value",
    ("png", "ihdr_compression_method"): "png_value",
    ("png", "ihdr_filter_method"): "png_value",
    ("png", "ihdr_interlace_method"): "png_value",
    ("png", "interlace_method"): "png_value",
}

_SIG = b"\x89PNG\r\n\x1a\n"


def _inflate(b):
    try:
        d = zlib.decompressobj()
        out = d.decompress(bytes(b), 1 << 20)
        return out
    except Exception:  # noqa: BLE001
        return None


def _text(typ, d):
    """(keyword, text) of a tEXt/zTXt/iTXt chunk body, or None."""
    k, sep, rest = bytes(d).partition(b"\0")
    if not sep:
        return None
    key = k.decode("latin-1")
    if typ == "tEXt":
        return key, rest.decode("latin-1")
    if typ == "zTXt":
        t = _inflate(rest[1:]) if rest else None
        return None if t is None else (key, t.decode("latin-1"))
    if len(rest) < 2:
        return None
    flag, body = rest[0], rest[2:]
    _lang, _, body = body.partition(b"\0")
    _tkey, _, body = body.partition(b"\0")
    if flag:
        body = _inflate(body)
        if body is None:
            return None
    return key, body.decode("utf-8", "replace")


def _parse(b):
    if not b or len(b) < 33 or bytes(b[:8]) != _SIG or bytes(b[12:16]) != b"IHDR":
        return None
    p = {"names": [], "text": [], "time": None, "ihdr": bytes(b[16:29])}
    off = 8
    while off + 8 <= len(b):
        n, = struct.unpack_from(">I", b, off)
        typ = bytes(b[off + 4:off + 8])
        if not re.fullmatch(rb"[A-Za-z]{4}", typ) or off + 12 + n > len(b):
            break
        t = typ.decode()
        d = b[off + 8:off + 8 + n]
        p["names"].append(t)
        if t in ("tEXt", "zTXt", "iTXt"):
            kv = _text(t, d)
            if kv:
                p["text"].append(kv)
        elif t == "tIME" and n >= 7 and p["time"] is None:
            p["time"] = struct.unpack_from(">HBBBBB", d, 0)
        off += 12 + n
        if t == "IEND":
            break
    return p


def _fold(s):
    return re.sub(r"[\s_\-]+", "", s or "").lower()


def png_value(data, ctx):
    if data is None:
        return None
    try:
        ctx = ctx or {}
        return _value(data, ctx.get("field") or "", ctx.get("param"))
    except Exception:  # noqa: BLE001 -- a malformed PNG never raises past the extractor
        return None


def _value(b, f, param):
    p = _parse(b)
    if p is None:
        return "none"
    ih = p["ihdr"]
    if f in ("ihdr_bit_depth", "bit_depth"):
        return ih[8]
    if "colo" in f and f.endswith("_type"):
        return ih[9]
    if f == "ihdr_compression_method":
        return ih[10]
    if f == "ihdr_filter_method":
        return ih[11]
    if f.endswith("interlace_method"):
        return ih[12]
    if f in ("chunk_names", "chunk_types", "chunk_order", "chunk_list", "chunk_type_names"):
        return p["names"]
    if f == "chunk_count":
        return len(p["names"])
    if f == "ancillary_chunk_names":
        return [n for n in p["names"] if n[0].islower()]
    if f.startswith("idat"):
        return p["names"].count("IDAT")
    if f.startswith("time") or f in ("last_modification_time", "modification_time", "modify_date"):
        if p["time"] is None:
            return "none"
        y, mo, d, h, mi, s = p["time"]
        return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (y, mo, d, h, mi, s)
    texts = {}
    for k, v in p["text"]:
        texts.setdefault(k, v)
    if f in ("text_chunks", "text_chunk_entries", "textual_chunks", "text_chunk_key_values", "text_metadata"):
        return texts or "none"
    if f in ("text_keywords", "text_chunk_keywords"):
        return list(texts) or "none"
    if f == "text_chunk_count":
        return len(p["text"])
    if param is not None or re.match(r"(text_chunk_|text_|itxt_|ztxt_)", f):
        want = _fold(param if param is not None else re.sub(r"^(text_chunk_|text_|itxt_|ztxt_)", "", f))
        for k, v in texts.items():
            if _fold(k) == want:
                return v
        return "none"
    return None
