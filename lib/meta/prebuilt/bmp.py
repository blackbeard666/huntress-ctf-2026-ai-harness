"""BMP (Windows DIB) header fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout: BITMAPFILEHEADER (14 bytes) = "BM", bfSize u32le, 2x reserved u16, bfOffBits u32le; then the DIB header whose
first u32 is its size: 12 = BITMAPCOREHEADER (width u16, height u16, planes u16, bitcount u16), 40/52/56/64/108/124 =
BITMAPINFOHEADER family (width i32, height i32, planes u16, bitcount u16, compression u32, ...).
dib_dimensions_pixels = width x |height| (a negative height only means top-down row order; exiftool/`file` report the
magnitude). bits_per_pixel = biBitCount. Not "BM" + a known DIB size (decoy / renamed) -> "none"."""
import struct

from ..spell import Dims

FIELDS = {
    ("bmp", "dib_dimensions_pixels"): "bmp_value",
    ("bmp", "dib_header_dimensions_pixels"): "bmp_value",
    ("bmp", "info_header_dimensions_pixels"): "bmp_value",
    ("bmp", "bitmap_info_header_dimensions_pixels"): "bmp_value",
    ("bmp", "bitmapinfoheader_dimensions_pixels"): "bmp_value",
    ("bmp", "dimensions_pixels"): "bmp_value",
    ("bmp", "image_dimensions_pixels"): "bmp_value",
    ("bmp", "bits_per_pixel"): "bmp_value",
    ("bmp", "dib_bits_per_pixel"): "bmp_value",
    ("bmp", "bit_count"): "bmp_value",
    ("bmp", "bi_bit_count"): "bmp_value",
    ("bmp", "dib_bit_count"): "bmp_value",
    ("bmp", "bit_depth"): "bmp_value",
    ("bmp", "dib_header_size"): "bmp_value",
    ("bmp", "dib_header_size_bytes"): "bmp_value",
    ("bmp", "bf_size"): "bmp_value",
    ("bmp", "file_header_size_bytes"): "bmp_value",
    ("bmp", "bf_off_bits"): "bmp_value",
    ("bmp", "pixel_data_offset"): "bmp_value",
    ("bmp", "compression"): "bmp_value",
    ("bmp", "dib_compression"): "bmp_value",
}

_DIB_SIZES = (12, 16, 40, 52, 56, 64, 108, 124)


def _parse(b):
    if not b or len(b) < 26 or bytes(b[:2]) != b"BM":
        return None
    bf_size, bf_off, dib = struct.unpack_from("<I4xII", b, 2)
    if dib not in _DIB_SIZES:
        return None
    if dib == 12:
        w, h, _, bpp = struct.unpack_from("<HHHH", b, 18)
        comp = 0
    else:
        if len(b) < 34:
            return None
        w, h, _, bpp = struct.unpack_from("<iiHH", b, 18)
        comp = struct.unpack_from("<I", b, 30)[0] if len(b) >= 34 else 0
    return {"w": abs(w), "h": abs(h), "bpp": bpp, "dib": dib, "bf_size": bf_size, "bf_off": bf_off, "comp": comp}


def bmp_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed BMP never raises past the extractor
        return None


def _value(b, f):
    p = _parse(b)
    if p is None:
        return "none"
    if f.endswith("dimensions_pixels"):
        return Dims(p["w"], p["h"])
    if "bit" in f and "off" not in f:
        return p["bpp"]
    if f.startswith("dib_header_size"):
        return p["dib"]
    if f in ("bf_size", "file_header_size_bytes"):
        return p["bf_size"]
    if f in ("bf_off_bits", "pixel_data_offset"):
        return p["bf_off"]
    if "compression" in f:
        return p["comp"]
    return None
