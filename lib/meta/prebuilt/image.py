"""Abstract `image.*` fields (prebuilt, SPECULATIVE -- never GM-asked yet). One namespace over every still format:
the container is chosen BY MAGIC (never by extension), then the format's own structure answers:
  JPEG (FF D8 FF) SOF0..15 (not DHT/JPG/DAC) | PNG IHDR | GIF Logical Screen Descriptor | BMP DIB header (|height|)
  | WebP VP8X canvas else VP8/VP8L | TIFF IFD0 ImageWidth x ImageLength | HEIF/AVIF primary-item ispe.
dimensions_pixels -> "<w>x<h>" (the D4/D5 rendering). format / container_format = the lowercase short name
("jpeg", "png", "gif", "bmp", "webp", "tiff", "heic", "avif"; ffprobe/Pillow style), mime_type = the IANA type.
ICC (shared by webp/heic): JPEG APP2 "ICC_PROFILE\\0" seq/count chunks (joined in seq order), PNG iCCP (keyword\\0 +
method 0 + zlib), WebP ICCP, TIFF tag 34675, HEIF colr prof. icc_profile_description = the 'desc' tag text (v2
textDescriptionType ASCII, or v4 'mluc' first record UTF-16BE), exiftool ProfileDescription. icc_color_space = the
header data colour space 4cc trimmed ("RGB"), icc_device_class = the stored class 4cc ("mntr"; *_name -> exiftool's
"Display Device Profile"), icc_version = "major.minor.bugfix" from the BCD header byte pair (exiftool "4.4.0").
Not an image magic -> "none"; an image without an ICC profile -> "none" for the icc_* fields."""
import struct
import zlib

from ..spell import Dims

FIELDS = {
    ("image", "dimensions_pixels"): "image_value",
    ("image", "image_dimensions_pixels"): "image_value",
    ("image", "pixel_dimensions"): "image_value",
    ("image", "dimensions"): "image_value",
    ("image", "resolution"): "image_value",
    ("image", "image_size"): "image_value",
    ("image", "width"): "image_value",
    ("image", "height"): "image_value",
    ("image", "image_width"): "image_value",
    ("image", "image_height"): "image_value",
    ("image", "width_pixels"): "image_value",
    ("image", "height_pixels"): "image_value",
    ("image", "format"): "image_value",
    ("image", "image_format"): "image_value",
    ("image", "container_format"): "image_value",
    ("image", "actual_format"): "image_value",
    ("image", "actual_container_format"): "image_value",
    ("image", "detected_format"): "image_value",
    ("image", "format_by_magic"): "image_value",
    ("image", "file_type"): "image_value",
    ("image", "mime_type"): "image_value",
    ("image", "actual_mime_type"): "image_value",
    ("image", "has_icc"): "image_value",
    ("image", "has_icc_profile"): "image_value",
    ("image", "icc_present"): "image_value",
    ("image", "icc_profile_present"): "image_value",
    ("image", "icc_profile_description"): "image_value",
    ("image", "icc_description"): "image_value",
    ("image", "profile_description"): "image_value",
    ("image", "icc_color_space"): "image_value",
    ("image", "icc_colour_space"): "image_value",
    ("image", "icc_data_color_space"): "image_value",
    ("image", "color_space"): "image_value",
    ("image", "icc_device_class"): "image_value",
    ("image", "icc_profile_class"): "image_value",
    ("image", "icc_device_class_name"): "image_value",
    ("image", "icc_profile_class_name"): "image_value",
    ("image", "icc_version"): "image_value",
    ("image", "icc_profile_version"): "image_value",
    ("image", "icc_profile_size"): "image_value",
    ("image", "icc_cmm_type"): "image_value",
    ("image", "icc_profile_copyright"): "image_value",
    ("image", "icc_copyright"): "image_value",
    ("image", "icc_rendering_intent"): "image_value",
    ("jpeg", "icc_profile_description"): "image_value",
    ("jpeg", "icc_color_space"): "image_value",
    ("jpeg", "icc_device_class"): "image_value",
    ("jpeg", "icc_version"): "image_value",
    ("jpeg", "has_icc"): "image_value",
    ("jpeg", "has_icc_profile"): "image_value",
    ("png", "icc_profile_description"): "image_value",
    ("png", "icc_color_space"): "image_value",
    ("png", "icc_device_class"): "image_value",
    ("png", "icc_version"): "image_value",
    ("png", "has_icc"): "image_value",
    ("png", "has_icc_profile"): "image_value",
    ("png", "iccp_profile_name"): "image_value",
    ("icc", "profile_description"): "icc_value",
    ("icc", "description"): "icc_value",
    ("icc", "color_space"): "icc_value",
    ("icc", "colour_space"): "icc_value",
    ("icc", "data_color_space"): "icc_value",
    ("icc", "device_class"): "icc_value",
    ("icc", "profile_class"): "icc_value",
    ("icc", "device_class_name"): "icc_value",
    ("icc", "profile_class_name"): "icc_value",
    ("icc", "version"): "icc_value",
    ("icc", "profile_version"): "icc_value",
    ("icc", "profile_size"): "icc_value",
    ("icc", "cmm_type"): "icc_value",
    ("icc", "copyright"): "icc_value",
    ("icc", "profile_copyright"): "icc_value",
    ("icc", "rendering_intent"): "icc_value",
    ("icc", "pcs"): "icc_value",
    ("icc", "connection_space"): "icc_value",
}

_MIME = {"jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif", "bmp": "image/bmp", "webp": "image/webp",
         "tiff": "image/tiff", "heic": "image/heic", "avif": "image/avif"}
_CLASS = {"scnr": "Input Device Profile", "mntr": "Display Device Profile", "prtr": "Output Device Profile",
          "link": "DeviceLink Profile", "spac": "ColorSpace Conversion Profile", "abst": "Abstract Profile",
          "nmcl": "NamedColor Profile", "cenc": "ColorEncodingSpace Profile", "mid ": "MultiplexIdentification Profile",
          "mlnk": "MultiplexLink Profile", "mvis": "MultiplexVisualization Profile"}
_INTENT = {0: "Perceptual", 1: "Media-Relative Colorimetric", 2: "Saturation", 3: "ICC-Absolute Colorimetric"}


def kind(b):
    """The container by magic: jpeg/png/gif/bmp/webp/tiff/heic/avif, or None."""
    if not b or len(b) < 12:
        return None
    h = bytes(b[:16])
    if h[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if h[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if h[:2] == b"BM" and len(b) >= 26 and struct.unpack_from("<I", b, 14)[0] in (12, 16, 40, 52, 56, 64, 108, 124):
        return "bmp"
    if h[:4] == b"RIFF" and h[8:12] == b"WEBP":
        return "webp"
    if h[:4] in (b"II*\x00", b"MM\x00*"):
        return "tiff"
    if h[4:8] == b"ftyp":
        from .heic import parse
        hf = parse(b)
        if hf is not None:
            return "avif" if hf["major"] in ("avif", "avis") or (hf["major"] in ("mif1", "msf1") and
                                                                 "avif" in hf["compat"]) else "heic"
    return None


def dims(b, k=None):
    """(w, h) by magic, or None."""
    k = k or kind(b)
    if k == "jpeg":
        from ..images import jpeg_sof_dimensions
        d = jpeg_sof_dimensions(b, {})
    elif k == "png":
        from ..images import png_ihdr_dimensions
        d = png_ihdr_dimensions(b, {})
    elif k == "gif":
        d = struct.unpack_from("<HH", b, 6)
    elif k == "bmp":
        sz = struct.unpack_from("<I", b, 14)[0]
        if sz == 12:
            d = struct.unpack_from("<HH", b, 18)
        else:
            w, h = struct.unpack_from("<ii", b, 18)
            d = (abs(w), abs(h))
    elif k == "webp":
        from .webp import dims as wd
        d = wd(b)
    elif k == "tiff":
        from .tiff import dims as td
        d = td(b)
    elif k in ("heic", "avif"):
        from .heic import dims as hd
        d = hd(b)
    else:
        return None
    return tuple(d) if isinstance(d, tuple) else None


# ---- ICC ---------------------------------------------------------------------------------------------------------

def icc_bytes(b, k=None):
    """The embedded ICC profile of an image, or None."""
    k = k or kind(b)
    b = bytes(b)
    if k == "jpeg":
        from .jpeg import _segments
        parts = []
        for m, p in _segments(b) or []:
            if m == 0xE2 and p.startswith(b"ICC_PROFILE\x00") and len(p) >= 14:
                parts.append((p[12], p[14:]))
        return b"".join(x for _, x in sorted(parts, key=lambda t: t[0])) if parts else None
    if k == "png":
        off = 8
        while off + 12 <= len(b):
            n = struct.unpack_from(">I", b, off)[0]
            t = b[off + 4:off + 8]
            if t == b"iCCP":
                d = b[off + 8:off + 8 + n]
                z = d.find(b"\x00")
                if z < 0:
                    return None
                try:
                    return zlib.decompressobj().decompress(d[z + 2:])
                except zlib.error:
                    return None
            if t in (b"IDAT", b"IEND"):
                return None
            off += 12 + n
        return None
    if k == "webp":
        from .webp import parse
        w = parse(b)
        return w and w["icc"]
    if k == "tiff":
        from .jpeg import _ifd
        from .tiff import header
        h = header(b)
        v = _ifd(b, h[1], h[0]).get(0x8773) if h else None
        return bytes(v[2]) if v else None
    if k in ("heic", "avif"):
        from .heic import icc
        return icc(b)
    return None


def _png_icc_name(b):
    off = 8
    while off + 12 <= len(b):
        n = struct.unpack_from(">I", b, off)[0]
        if b[off + 4:off + 8] == b"iCCP":
            return bytes(b[off + 8:off + 8 + n]).split(b"\x00", 1)[0].decode("latin-1")
        off += 12 + n
    return "none"


def _icc_tags(p):
    if len(p) < 132:
        return {}
    n = struct.unpack_from(">I", p, 128)[0]
    out = {}
    for i in range(min(n, 256)):
        q = 132 + 12 * i
        if q + 12 > len(p):
            break
        sig, off, sz = struct.unpack_from(">4sII", p, q)
        out.setdefault(sig, p[off:off + sz])
    return out


def _icc_text(t):
    """desc (textDescriptionType), mluc (first record), or text tag -> str, or None."""
    if not t or len(t) < 12:
        return None
    typ = t[:4]
    if typ == b"desc":
        n = struct.unpack_from(">I", t, 8)[0]
        return t[12:12 + n].split(b"\x00", 1)[0].decode("latin-1").strip()
    if typ == b"mluc" and len(t) >= 28:
        cnt, rsz = struct.unpack_from(">II", t, 8)
        if cnt:
            ln, off = struct.unpack_from(">II", t, 16 + 4 + 0)
            return t[off:off + ln].decode("utf-16-be", "replace").rstrip("\x00").strip()
    if typ == b"text":
        return t[8:].split(b"\x00", 1)[0].decode("latin-1").strip()
    return None


def icc_field(p, f):
    """An ICC header/tag field of profile bytes `p` (field names with or without the icc_ prefix)."""
    f = f[4:] if f.startswith("icc_") else f
    f = f[8:] if f.startswith("profile_") and f not in ("profile_size", "profile_version") else f
    if f in ("present", "profile_present"):
        return p is not None
    if not p or len(p) < 128 or p[36:40] != b"acsp":
        return "none"
    if f in ("description", "profile_description"):
        return _icc_text(_icc_tags(p).get(b"desc")) or "none"
    if f in ("copyright", "profile_copyright"):
        return _icc_text(_icc_tags(p).get(b"cprt")) or "none"
    if f in ("color_space", "colour_space", "data_color_space"):
        return p[16:20].decode("latin-1").strip()
    if f in ("pcs", "connection_space"):
        return p[20:24].decode("latin-1").strip()
    if f in ("device_class", "class"):
        return p[12:16].decode("latin-1").strip()
    if f in ("device_class_name", "class_name"):
        return _CLASS.get(p[12:16].decode("latin-1"), "none")
    if f in ("version", "profile_version"):
        return "%d.%d.%d" % (p[8], p[9] >> 4, p[9] & 0xF)
    if f in ("size", "profile_size"):
        return struct.unpack_from(">I", p, 0)[0]
    if f == "cmm_type":
        return p[4:8].decode("latin-1").strip("\x00 ") or "none"
    if f == "rendering_intent":
        return _INTENT.get(struct.unpack_from(">I", p, 64)[0], "none")
    return None


def icc_value(data, ctx):
    """icc.<field>: the member is a bare .icc/.icm profile -- or an image carrying one."""
    if data is None:
        return None
    try:
        b = bytes(data)
        p = b if len(b) >= 128 and b[36:40] == b"acsp" else icc_bytes(b)
        return icc_field(p, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001
        return None


def image_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), (ctx or {}).get("field") or "", (ctx or {}).get("fmt") or "image")
    except Exception:  # noqa: BLE001 -- a malformed image never raises past the extractor
        return None


def _value(b, f, fmt):
    k = kind(b)
    if k is None or (fmt in ("jpeg", "png") and k != fmt):
        return "none"
    if f == "iccp_profile_name":
        return _png_icc_name(b)
    if "icc" in f or f in ("profile_description", "color_space"):
        if f == "color_space":
            f = "icc_color_space"
        p = icc_bytes(b, k)
        if f.startswith("has_") or f.endswith("_present"):
            return p is not None
        return icc_field(p, f)
    if f in ("format", "image_format", "container_format", "actual_format", "actual_container_format",
             "detected_format", "format_by_magic", "file_type"):
        return k
    if f in ("mime_type", "actual_mime_type"):
        return _MIME[k]
    d = dims(b, k)
    if d is None:
        return "none"
    if "width" in f:
        return d[0]
    if "height" in f:
        return d[1]
    return Dims(*d)
