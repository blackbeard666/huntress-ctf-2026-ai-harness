"""JPEG APPn segment list + APP1 EXIF (TIFF IFD0 / ExifIFD / GPS IFD) tags (prebuilt, SPECULATIVE -- never GM-asked;
jpeg.sof_dimensions_pixels is the GM-verified D4 field in lib/meta/images.py and is not touched here).

Segments (ITU T.81): SOI FFD8, then FFxx markers with a u16 BE length (incl. itself) until SOS FFDA / EOI FFD9.
app_segments = the APPn markers (FFE0..FFEF) in FILE order, duplicates kept, spelled "APP<n>" (exiftool / jpegdump
naming). EXIF = the first APP1 whose payload starts b"Exif\\0\\0": a TIFF header (II*\\0 little / MM\\0* big endian, IFD0
offset u32), IFD entries (tag u16, type u16, count u32, value-or-offset u32; values <= 4 bytes inline), offsets relative
to the TIFF header. ExifIFD via IFD0 tag 0x8769, GPS IFD via 0x8825.
Spellings: ASCII tags = the stored string up to its first NUL, trimmed (exiftool prints the same). exif_orientation =
the stored SHORT 1..8 as base-10 (exiftool -n), mapped to exiftool's text ("Horizontal (normal)", ...) only when the
contract's accepted_values list text. exif_datetime_original = the stored EXIF text "YYYY:MM:DD HH:MM:SS" verbatim
(EXIF 2.3 has no zone in it); *_iso8601 = "YYYY-MM-DDTHH:MM:SS" (+ OffsetTimeOriginal when stored), *_utc = that
instant in UTC with "Z" (stored as UTC when no offset tag). exif_gps_latitude / _longitude = SIGNED decimal degrees
(deg + min/60 + sec/3600, negative for Ref S / W, exiftool -n Composite:GPSLatitude) rounded to 6 places, trailing
zeros stripped (or the N places an answer_format asks for). Not a JPEG / no EXIF / tag absent -> "none"."""
import re
import struct
from datetime import datetime, timedelta, timezone

FIELDS = {
    ("jpeg", "app_segments"): "app_segments",
    ("jpeg", "app_segment_list"): "app_segments",
    ("jpeg", "app_segment_markers"): "app_segments",
    ("jpeg", "app_markers"): "app_segments",
    ("jpeg", "appn_segments"): "app_segments",
    ("jpeg", "app_segment_names"): "app_segments",
    ("jpeg", "app_segment_count"): "app_segment_count",
    ("jpeg", "appn_segment_count"): "app_segment_count",
    ("jpeg", "app_segment_identifiers"): "app_segment_identifiers",
    ("jpeg", "app_segment_ids"): "app_segment_identifiers",
    ("jpeg", "has_exif"): "has_exif",
    ("jpeg", "exif_present"): "has_exif",
    ("jpeg", "exif_byte_order"): "exif_value",
    ("jpeg", "exif_make"): "exif_value",
    ("jpeg", "exif_model"): "exif_value",
    ("jpeg", "exif_software"): "exif_value",
    ("jpeg", "exif_artist"): "exif_value",
    ("jpeg", "exif_copyright"): "exif_value",
    ("jpeg", "exif_image_description"): "exif_value",
    ("jpeg", "exif_datetime"): "exif_value",
    ("jpeg", "exif_date_time"): "exif_value",
    ("jpeg", "exif_datetime_original"): "exif_value",
    ("jpeg", "exif_date_time_original"): "exif_value",
    ("jpeg", "exif_datetime_original_iso8601"): "exif_value",
    ("jpeg", "exif_datetime_original_utc"): "exif_value",
    ("jpeg", "exif_datetime_digitized"): "exif_value",
    ("jpeg", "exif_create_date"): "exif_value",
    ("jpeg", "exif_offset_time_original"): "exif_value",
    ("jpeg", "exif_orientation"): "exif_value",
    ("jpeg", "exif_lens_model"): "exif_value",
    ("jpeg", "exif_lens_make"): "exif_value",
    ("jpeg", "exif_body_serial_number"): "exif_value",
    ("jpeg", "exif_serial_number"): "exif_value",
    ("jpeg", "exif_camera_owner_name"): "exif_value",
    ("jpeg", "exif_owner_name"): "exif_value",
    ("jpeg", "exif_user_comment"): "exif_value",
    ("jpeg", "exif_image_unique_id"): "exif_value",
    ("jpeg", "exif_gps_latitude"): "exif_value",
    ("jpeg", "exif_gps_longitude"): "exif_value",
    ("jpeg", "exif_gps_latitude_ref"): "exif_value",
    ("jpeg", "exif_gps_longitude_ref"): "exif_value",
    ("jpeg", "exif_gps_altitude"): "exif_value",
    ("jpeg", "gps_latitude"): "exif_value",
    ("jpeg", "gps_longitude"): "exif_value",
    ("jpeg", "exif_*"): "exif_value",
}

# field (minus "exif_") -> (ifd, tag). ifd: 0 = IFD0, 1 = ExifIFD, 2 = GPS IFD.
_TAGS = {
    "make": (0, 0x010F), "model": (0, 0x0110), "software": (0, 0x0131), "artist": (0, 0x013B),
    "copyright": (0, 0x8298), "image_description": (0, 0x010E), "datetime": (0, 0x0132), "date_time": (0, 0x0132),
    "modify_date": (0, 0x0132), "orientation": (0, 0x0112), "host_computer": (0, 0x013C),
    "x_resolution": (0, 0x011A), "y_resolution": (0, 0x011B), "resolution_unit": (0, 0x0128),
    "datetime_original": (1, 0x9003), "date_time_original": (1, 0x9003),
    "datetime_digitized": (1, 0x9004), "date_time_digitized": (1, 0x9004), "create_date": (1, 0x9004),
    "offset_time": (1, 0x9010), "offset_time_original": (1, 0x9011), "offset_time_digitized": (1, 0x9012),
    "lens_model": (1, 0xA434), "lens_make": (1, 0xA433), "body_serial_number": (1, 0xA431),
    "serial_number": (1, 0xA431), "camera_owner_name": (1, 0xA430), "owner_name": (1, 0xA430),
    "user_comment": (1, 0x9286), "image_unique_id": (1, 0xA420), "exif_version": (1, 0x9000),
    "iso": (1, 0x8827), "iso_speed_ratings": (1, 0x8827), "f_number": (1, 0x829D), "exposure_time": (1, 0x829A),
    "focal_length": (1, 0x920A), "pixel_x_dimension": (1, 0xA002), "pixel_y_dimension": (1, 0xA003),
    "exif_image_width": (1, 0xA002), "exif_image_height": (1, 0xA003),
    "gps_latitude_ref": (2, 0x0001), "gps_longitude_ref": (2, 0x0003), "gps_altitude_ref": (2, 0x0005),
    "gps_altitude": (2, 0x0006), "gps_date_stamp": (2, 0x001D), "gps_map_datum": (2, 0x0012),
}
_ORIENT = {1: "Horizontal (normal)", 2: "Mirror horizontal", 3: "Rotate 180", 4: "Mirror vertical",
           5: "Mirror horizontal and rotate 270 CW", 6: "Rotate 90 CW", 7: "Mirror horizontal and rotate 90 CW",
           8: "Rotate 270 CW"}
_SIZES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8, 13: 4}


def _segments(d):
    """[(marker, payload bytes)] up to SOS/EOI, or None when the bytes are not a JPEG."""
    if not d or len(d) < 4 or bytes(d[:3]) != b"\xff\xd8\xff":
        return None
    out, i, n = [], 2, len(d)
    while i + 4 <= n:
        if d[i] != 0xFF:
            break
        m = d[i + 1]
        if m == 0xFF:
            i += 1
            continue
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        if m in (0xD9, 0xDA):
            break
        ln = struct.unpack_from(">H", d, i + 2)[0]
        if ln < 2:
            break
        out.append((m, bytes(d[i + 4:i + 2 + ln])))
        i += 2 + ln
    return out


def _ifd(t, off, e):
    """{tag: (type, count, raw value bytes)} of the IFD at `off` in TIFF blob `t` (byte order `e`)."""
    out = {}
    if off < 8 or off + 2 > len(t):
        return out
    cnt = struct.unpack_from(e + "H", t, off)[0]
    for k in range(min(cnt, 1024)):
        p = off + 2 + 12 * k
        if p + 12 > len(t):
            break
        tag, typ, count = struct.unpack_from(e + "HHI", t, p)
        size = _SIZES.get(typ, 1) * count
        if size <= 4:
            raw = t[p + 8:p + 8 + size]
        else:
            vo = struct.unpack_from(e + "I", t, p + 8)[0]
            if vo + size > len(t):
                continue
            raw = t[vo:vo + size]
        out.setdefault(tag, (typ, count, raw))
    return out


def _exif(d):
    """(byte order char, [IFD0, ExifIFD, GPS] dicts) of the first Exif APP1, "none" (JPEG without EXIF), None."""
    segs = _segments(d)
    if segs is None:
        return None
    for m, p in segs:
        if m != 0xE1 or not p.startswith(b"Exif\x00"):
            continue
        t = p[6:]
        if t[:4] == b"II*\x00":
            e = "<"
        elif t[:4] == b"MM\x00*":
            e = ">"
        else:
            continue
        ifd0 = _ifd(t, struct.unpack_from(e + "I", t, 4)[0], e)
        subs = []
        for ptr in (0x8769, 0x8825):
            v = ifd0.get(ptr)
            sub = {}
            if v and v[0] in (4, 13) and len(v[2]) >= 4:
                sub = _ifd(t, struct.unpack_from(e + "I", v[2], 0)[0], e)
            subs.append(sub)
        return e, [ifd0] + subs
    return "none"


def _decode(typ, count, raw, e):
    """ASCII -> str (to first NUL, trimmed); SHORT/LONG -> int or list; RATIONAL -> float or list; else bytes."""
    if typ == 2:
        return raw.split(b"\x00", 1)[0].decode("utf-8", "replace").strip()
    fmt = {3: "H", 4: "I", 8: "h", 9: "i", 1: "B", 6: "b"}.get(typ)
    if fmt:
        vals = list(struct.unpack(e + fmt * count, raw[:struct.calcsize(fmt) * count]))
        return vals[0] if count == 1 else vals
    if typ in (5, 10):
        f = "I" if typ == 5 else "i"
        vals = []
        for k in range(count):
            a, b = struct.unpack_from(e + f + f, raw, 8 * k)
            vals.append(a / b if b else 0.0)
        return vals[0] if count == 1 else vals
    if typ == 7 and raw[:8] in (b"ASCII\x00\x00\x00", b"UNICODE\x00", b"\x00" * 8):   # UserComment
        body = raw[8:].decode("utf-16-le" if raw[:7] == b"UNICODE" else "latin-1", "replace")
        return body.split("\x00", 1)[0].strip()
    if typ == 7:
        return raw.decode("latin-1").strip("\x00 ")
    return raw


def _tag(ex, ifd, tag):
    e, ifds = ex
    v = ifds[ifd].get(tag)
    return None if v is None else _decode(v[0], v[1], v[2], e)


def _places(ctx):
    fmt = (ctx.get("question") or {}).get("answer_format") or {}
    m = re.search(r"(\d+)\s*(?:decimal|digits|places)", str(fmt))
    return int(m.group(1)) if m else None


def _num(v, ctx):
    n = _places(ctx)
    if n is not None:
        return "%.*f" % (n, v)
    s = "%.6f" % round(v, 6)
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _gps(ex, which, ctx):
    tag, ref_tag = (0x0002, 0x0001) if which == "latitude" else (0x0004, 0x0003)
    v = _tag(ex, 2, tag)
    if v is None:
        return "none"
    if not isinstance(v, list):
        v = [v]
    dec = sum(float(x) / (60 ** k) for k, x in enumerate(v[:3]))
    ref = _tag(ex, 2, ref_tag)
    if isinstance(ref, str) and ref[:1].upper() in ("S", "W"):
        dec = -dec
    return _num(dec, ctx)


def _dt(ex, field):
    v = _tag(ex, 1, 0x9003)
    if not isinstance(v, str) or not v:
        return "none"
    if field.endswith(("_iso8601", "_utc")):
        try:
            t = datetime.strptime(v[:19], "%Y:%m:%d %H:%M:%S")
        except ValueError:
            return None
        off = _tag(ex, 1, 0x9011)
        m = re.match(r"^([+-])(\d\d):(\d\d)$", off) if isinstance(off, str) else None
        if field.endswith("_iso8601"):
            return t.strftime("%Y-%m-%dT%H:%M:%S") + (off if m else "")
        if m:
            sign = 1 if m.group(1) == "+" else -1
            t = t - sign * timedelta(hours=int(m.group(2)), minutes=int(m.group(3)))
        return t.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return v


def exif_value(data, ctx):
    """jpeg.exif_<tag>: one IFD0 / ExifIFD / GPS tag of the APP1 EXIF block (see module doc for spellings)."""
    if data is None:
        return None
    try:
        ex = _exif(data)
    except (struct.error, ValueError, IndexError):
        return None
    if ex is None or ex == "none":             # not a JPEG (renamed decoy) / a JPEG without an Exif APP1
        return "none"
    field = ctx.get("field") or ""
    name = field[5:] if field.startswith("exif_") else field
    if ctx.get("param") is not None:
        name = ctx["param"]
    try:
        if name == "byte_order":
            return "II" if ex[0] == "<" else "MM"
        if name in ("gps_latitude", "gps_longitude"):
            return _gps(ex, name[4:], ctx)
        if name.startswith(("datetime_original", "date_time_original")):
            return _dt(ex, field)
        loc = _TAGS.get(name)
        while loc is None and "_" in name:            # exif_make_string -> make (a rendering suffix)
            name = name.rsplit("_", 1)[0]
            if name in ("gps_latitude", "gps_longitude"):
                return _gps(ex, name[4:], ctx)
            loc = _TAGS.get(name)
        if loc is None:
            return None
        v = _tag(ex, *loc)
        if v is None or v == "":
            return "none"
        if name == "orientation" and isinstance(v, int):
            acc = [str(a) for a in (((ctx.get("question") or {}).get("answer_format") or {}).get("accepted_values")
                                    or [])]
            if acc and str(v) not in acc and v in _ORIENT:
                return _ORIENT[v]
            return v
        if isinstance(v, float):
            return _num(v, ctx)
        if isinstance(v, bytes):
            return v.decode("latin-1").strip("\x00 ")
        if isinstance(v, list):
            return " ".join(_num(x, ctx) if isinstance(x, float) else str(x) for x in v)
        return v
    except (struct.error, ValueError, IndexError, TypeError):
        return None


def app_segments(data, ctx):
    """jpeg.app_segments: the APPn markers in file order, e.g. ["APP0","APP1"]."""
    if data is None:
        return None
    segs = _segments(data)
    if segs is None:
        return "none"
    return ["APP%d" % (m - 0xE0) for m, _ in segs if 0xE0 <= m <= 0xEF]


def app_segment_count(data, ctx):
    v = app_segments(data, ctx)
    return len(v) if isinstance(v, list) else v


def app_segment_identifiers(data, ctx):
    """The NUL-terminated identifier each APPn payload starts with ("JFIF", "Exif", "http://ns.adobe.com/xap/1.0/",
    "ICC_PROFILE", "Adobe" ...), file order; "" when an APPn has none."""
    if data is None:
        return None
    segs = _segments(data)
    if segs is None:
        return "none"
    out = []
    for m, p in segs:
        if 0xE0 <= m <= 0xEF:
            ident = p.split(b"\x00", 1)[0] if b"\x00" in p[:64] else p[:5]
            out.append(ident.decode("latin-1").strip())
    return out


def has_exif(data, ctx):
    if data is None:
        return None
    segs = _segments(data)
    if segs is None:
        return "none"
    return any(m == 0xE1 and p.startswith(b"Exif\x00") for m, p in segs)
