"""TIFF fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout (TIFF 6.0): "II*\\0" (little-endian) | "MM\\0*" (big-endian) + u32 offset of IFD0; each IFD = u16 count +
12-byte entries (tag, type, count, value-or-offset) + u32 next-IFD offset (0 ends the chain).
byte_order = the stored 2-letter mark "II" / "MM" (same spelling as jpeg.exif_byte_order). dimensions_pixels =
IFD0 ImageWidth (0x100) x ImageLength (0x101). ifd0_* / bare tag names = IFD0 ASCII/SHORT values as stored (trimmed;
DateTime keeps the TIFF "YYYY:MM:DD HH:MM:SS" text). ifd_count = length of the IFD0 -> next chain (one per page;
SubIFDs/ExifIFD not counted). Not a TIFF magic -> "none"; tag absent -> "none"."""
import struct

from ..spell import Dims
from .jpeg import _decode, _ifd

FIELDS = {
    ("tiff", "byte_order"): "tiff_value",
    ("tiff", "endianness"): "tiff_value",
    ("tiff", "header_byte_order"): "tiff_value",
    ("tiff", "dimensions_pixels"): "tiff_value",
    ("tiff", "image_dimensions_pixels"): "tiff_value",
    ("tiff", "ifd0_dimensions_pixels"): "tiff_value",
    ("tiff", "image_width"): "tiff_value",
    ("tiff", "image_length"): "tiff_value",
    ("tiff", "image_height"): "tiff_value",
    ("tiff", "ifd0_image_width"): "tiff_value",
    ("tiff", "ifd0_image_length"): "tiff_value",
    ("tiff", "make"): "tiff_value",
    ("tiff", "model"): "tiff_value",
    ("tiff", "software"): "tiff_value",
    ("tiff", "date_time"): "tiff_value",
    ("tiff", "datetime"): "tiff_value",
    ("tiff", "modify_date"): "tiff_value",
    ("tiff", "artist"): "tiff_value",
    ("tiff", "copyright"): "tiff_value",
    ("tiff", "image_description"): "tiff_value",
    ("tiff", "host_computer"): "tiff_value",
    ("tiff", "document_name"): "tiff_value",
    ("tiff", "page_name"): "tiff_value",
    ("tiff", "orientation"): "tiff_value",
    ("tiff", "compression"): "tiff_value",
    ("tiff", "photometric_interpretation"): "tiff_value",
    ("tiff", "bits_per_sample"): "tiff_value",
    ("tiff", "samples_per_pixel"): "tiff_value",
    ("tiff", "ifd0_make"): "tiff_value",
    ("tiff", "ifd0_model"): "tiff_value",
    ("tiff", "ifd0_software"): "tiff_value",
    ("tiff", "ifd0_date_time"): "tiff_value",
    ("tiff", "ifd0_datetime"): "tiff_value",
    ("tiff", "ifd0_artist"): "tiff_value",
    ("tiff", "ifd0_copyright"): "tiff_value",
    ("tiff", "ifd0_image_description"): "tiff_value",
    ("tiff", "ifd0_entry_count"): "tiff_value",
    ("tiff", "ifd0_tag_count"): "tiff_value",
    ("tiff", "ifd0_offset"): "tiff_value",
    ("tiff", "ifd_count"): "tiff_value",
    ("tiff", "number_of_ifds"): "tiff_value",
    ("tiff", "page_count"): "tiff_value",
    ("tiff", "image_count"): "tiff_value",
    ("tiff", "frame_count"): "tiff_value",
    ("tiff", "ifd0_*"): "tiff_value",
}

_TAG = {"image_width": 0x100, "image_length": 0x101, "image_height": 0x101, "bits_per_sample": 0x102,
        "compression": 0x103, "photometric_interpretation": 0x106, "document_name": 0x10D,
        "image_description": 0x10E, "make": 0x10F, "model": 0x110, "orientation": 0x112,
        "samples_per_pixel": 0x115, "page_name": 0x11D, "software": 0x131, "date_time": 0x132,
        "datetime": 0x132, "modify_date": 0x132, "artist": 0x13B, "host_computer": 0x13C, "copyright": 0x8298}


def header(b):
    """(struct byte-order char, IFD0 offset) of a TIFF, or None."""
    if not b or len(b) < 8:
        return None
    if bytes(b[:4]) == b"II*\x00":
        e = "<"
    elif bytes(b[:4]) == b"MM\x00*":
        e = ">"
    else:
        return None
    return e, struct.unpack_from(e + "I", b, 4)[0]


def ifd_chain(b, e, off):
    """IFD offsets IFD0 -> next ..., loop-safe."""
    seen = []
    while 8 <= off and off + 2 <= len(b) and off not in seen and len(seen) < 4096:
        seen.append(off)
        n = struct.unpack_from(e + "H", b, off)[0]
        p = off + 2 + 12 * n
        if p + 4 > len(b):
            break
        off = struct.unpack_from(e + "I", b, p)[0]
    return seen


def tag_value(b, e, ifd, tag):
    v = ifd.get(tag)
    return None if v is None else _decode(v[0], v[1], v[2], e)


def dims(b):
    """(w, h) from IFD0, "none" when not a TIFF / tags missing."""
    h = header(b)
    if h is None:
        return "none"
    ifd = _ifd(bytes(b), h[1], h[0])
    w, ln = tag_value(b, h[0], ifd, 0x100), tag_value(b, h[0], ifd, 0x101)
    if not isinstance(w, int) or not isinstance(ln, int):
        return "none"
    return w, ln


def tiff_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed TIFF never raises past the extractor
        return None


def _value(b, f):
    h = header(b)
    if h is None:
        return "none"
    e, off0 = h
    if f in ("byte_order", "endianness", "header_byte_order"):
        return "II" if e == "<" else "MM"
    if f in ("ifd_count", "number_of_ifds", "page_count", "image_count", "frame_count"):
        return len(ifd_chain(b, e, off0))
    if f == "ifd0_offset":
        return off0
    ifd = _ifd(b, off0, e)
    if f in ("ifd0_entry_count", "ifd0_tag_count"):
        return struct.unpack_from(e + "H", b, off0)[0] if off0 + 2 <= len(b) else "none"
    if f.endswith("dimensions_pixels"):
        d = dims(b)
        return d if d == "none" else Dims(*d)
    name = f[5:] if f.startswith("ifd0_") else f
    tag = _TAG.get(name)
    if tag is None:
        return None
    v = tag_value(b, e, ifd, tag)
    if v is None or v == "":
        return "none"
    if isinstance(v, bytes):
        return None
    if isinstance(v, list):
        return v
    return v
