"""ICO / CUR (ICONDIR) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout: ICONDIR = idReserved u16le (0), idType u16le (1 = icon, 2 = cursor), idCount u16le; then idCount 16-byte
ICONDIRENTRY (bWidth u8, bHeight u8 -- 0 means 256 --, bColorCount, bReserved, wPlanes u16, wBitCount u16,
dwBytesInRes u32, dwImageOffset u32). image_count = idCount as stored (`file`: "MS Windows icon resource - N icons").
image_dimensions = the entries' "WxH" in directory order (JSON list). Reserved != 0, type not 1/2, count 0, or the
directory not fitting the file (decoy / renamed BMP) -> "none"."""
import struct

FIELDS = {
    ("ico", "image_count"): "ico_value",
    ("ico", "icondir_image_count"): "ico_value",
    ("ico", "icondir_count"): "ico_value",
    ("ico", "id_count"): "ico_value",
    ("ico", "icon_count"): "ico_value",
    ("ico", "entry_count"): "ico_value",
    ("ico", "icondir_entry_count"): "ico_value",
    ("ico", "number_of_images"): "ico_value",
    ("ico", "image_type"): "ico_value",
    ("ico", "icondir_type"): "ico_value",
    ("ico", "id_type"): "ico_value",
    ("ico", "image_dimensions"): "ico_value",
    ("ico", "entry_dimensions"): "ico_value",
    ("ico", "icondir_entry_dimensions"): "ico_value",
}


def _parse(b):
    if not b or len(b) < 6:
        return None
    res, typ, cnt = struct.unpack_from("<HHH", b, 0)
    if res != 0 or typ not in (1, 2) or cnt == 0 or 6 + 16 * cnt > len(b):
        return None
    ents = []
    for i in range(cnt):
        w, h = b[6 + 16 * i], b[7 + 16 * i]
        ents.append("%dx%d" % (w or 256, h or 256))
    return {"type": typ, "count": cnt, "dims": ents}


def ico_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed ICO never raises past the extractor
        return None


def _value(b, f):
    p = _parse(b)
    if p is None:
        return "none"
    if "dimensions" in f:
        return p["dims"]
    if "type" in f:
        return p["type"]
    return p["count"]
