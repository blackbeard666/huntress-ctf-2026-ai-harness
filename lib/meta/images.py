"""Image header fields. COPIED from the GM-verified D4 (jpeg.sof_dimensions_pixels) / D5 (png.ihdr_dimensions_pixels)
logic as carried by the D10 solver. Not-that-format bytes -> the literal "none" (decoys)."""
import struct

from .spell import Dims


def jpeg_sof_dimensions(data, ctx):
    d = data
    if d is None:
        return None
    if d[:2] != b"\xff\xd8":
        return "none"
    i = 2
    while i + 4 <= len(d):
        if d[i] != 0xFF:
            i += 1
            continue
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
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack_from(">HH", d, i + 5)
            return Dims(w, h)
        i += 2 + ln
    return "none"


def png_ihdr_dimensions(data, ctx):
    if data is None:
        return None
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return "none"
    w, h = struct.unpack_from(">II", data, 16)
    return Dims(w, h)
