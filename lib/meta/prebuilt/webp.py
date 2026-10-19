"""WebP (RIFF/WEBP) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout (RFC 9649): "RIFF" + u32le size + "WEBP", then chunks (4cc + u32le size + payload, padded to even).
  VP8  (lossy): 3-byte frame tag, start code 9d 01 2a, then u16le width & 0x3fff, u16le height & 0x3fff.
  VP8L (lossless): signature 0x2f, then 14-bit (width-1), 14-bit (height-1), alpha bit, 3-bit version (LSB first).
  VP8X (extended): flags u8 (0x20 ICC, 0x10 alpha, 0x08 EXIF, 0x04 XMP, 0x02 animation), 3 reserved, then
        24-bit (canvas width-1), 24-bit (canvas height-1).  ANIM: bgcolor u32 + loop count u16; ANMF per frame.
dimensions_pixels = the VP8X canvas when present, else the VP8/VP8L bitstream size (exiftool ImageWidth/Height).
chunk_ids = top-level 4ccs in stored order, verbatim (the lossy chunk is "VP8 " WITH its space).
frame_count = number of ANMF chunks for an animation, 1 for a still. has_* = the VP8X flag OR the chunk itself.
ICC fields read the ICCP chunk (lib.meta.prebuilt.image ICC parser). Not RIFF....WEBP -> "none"."""
import struct

from ..spell import Dims, Hex

FIELDS = {
    ("webp", "dimensions_pixels"): "webp_value",
    ("webp", "image_dimensions_pixels"): "webp_value",
    ("webp", "canvas_dimensions_pixels"): "webp_value",
    ("webp", "vp8x_canvas_dimensions_pixels"): "webp_value",
    ("webp", "vp8x_dimensions_pixels"): "webp_value",
    ("webp", "bitstream_dimensions_pixels"): "webp_value",
    ("webp", "vp8_dimensions_pixels"): "webp_value",
    ("webp", "vp8l_dimensions_pixels"): "webp_value",
    ("webp", "frame_dimensions_pixels"): "webp_value",
    ("webp", "width"): "webp_value",
    ("webp", "height"): "webp_value",
    ("webp", "image_width"): "webp_value",
    ("webp", "image_height"): "webp_value",
    ("webp", "canvas_width"): "webp_value",
    ("webp", "canvas_height"): "webp_value",
    ("webp", "chunk_ids"): "webp_value",
    ("webp", "chunk_names"): "webp_value",
    ("webp", "chunk_list"): "webp_value",
    ("webp", "chunk_order"): "webp_value",
    ("webp", "riff_chunk_ids"): "webp_value",
    ("webp", "chunk_count"): "webp_value",
    ("webp", "riff_size"): "webp_value",
    ("webp", "bitstream_format"): "webp_value",
    ("webp", "image_chunk_id"): "webp_value",
    ("webp", "compression"): "webp_value",
    ("webp", "is_lossless"): "webp_value",
    ("webp", "vp8x_flags_u8_hex"): "webp_value",
    ("webp", "has_exif"): "webp_value",
    ("webp", "exif_present"): "webp_value",
    ("webp", "has_xmp"): "webp_value",
    ("webp", "xmp_present"): "webp_value",
    ("webp", "has_icc"): "webp_value",
    ("webp", "has_icc_profile"): "webp_value",
    ("webp", "icc_present"): "webp_value",
    ("webp", "icc_profile_present"): "webp_value",
    ("webp", "has_alpha"): "webp_value",
    ("webp", "alpha_present"): "webp_value",
    ("webp", "has_animation"): "webp_value",
    ("webp", "is_animated"): "webp_value",
    ("webp", "animated"): "webp_value",
    ("webp", "frame_count"): "webp_value",
    ("webp", "number_of_frames"): "webp_value",
    ("webp", "anmf_count"): "webp_value",
    ("webp", "animation_frame_count"): "webp_value",
    ("webp", "loop_count"): "webp_value",
    ("webp", "animation_loop_count"): "webp_value",
    ("webp", "anim_loop_count"): "webp_value",
    ("webp", "icc_profile_description"): "webp_value",
    ("webp", "icc_description"): "webp_value",
    ("webp", "profile_description"): "webp_value",
    ("webp", "icc_color_space"): "webp_value",
    ("webp", "icc_colour_space"): "webp_value",
    ("webp", "icc_device_class"): "webp_value",
    ("webp", "icc_profile_class"): "webp_value",
    ("webp", "icc_version"): "webp_value",
    ("webp", "icc_profile_version"): "webp_value",
}


def chunks(b):
    """[(4cc str, payload bytes)] of a RIFF/WEBP file, or None when not WebP."""
    if not b or len(b) < 12 or bytes(b[:4]) != b"RIFF" or bytes(b[8:12]) != b"WEBP":
        return None
    out, off = [], 12
    while off + 8 <= len(b):
        cid = bytes(b[off:off + 4]).decode("latin-1")
        n = struct.unpack_from("<I", b, off + 4)[0]
        out.append((cid, bytes(b[off + 8:off + 8 + n])))
        off += 8 + n + (n & 1)
    return out


def _bitstream_dims(cid, p):
    if cid == "VP8 " and len(p) >= 10 and p[3:6] == b"\x9d\x01\x2a":
        w, h = struct.unpack_from("<HH", p, 6)
        return w & 0x3FFF, h & 0x3FFF
    if cid == "VP8L" and len(p) >= 5 and p[0] == 0x2F:
        v = struct.unpack_from("<I", p, 1)[0]
        return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    return None


def parse(b):
    cs = chunks(b)
    if cs is None:
        return None
    ids = [c for c, _ in cs]
    w = {"ids": ids, "riff_size": struct.unpack_from("<I", b, 4)[0], "flags": None, "canvas": None,
         "bits": None, "bits_id": None, "loop": None, "frames": ids.count("ANMF"), "icc": None}
    for cid, p in cs:
        if cid == "VP8X" and len(p) >= 10 and w["flags"] is None:
            w["flags"] = p[0]
            w["canvas"] = (int.from_bytes(p[4:7], "little") + 1, int.from_bytes(p[7:10], "little") + 1)
        elif cid in ("VP8 ", "VP8L") and w["bits"] is None:
            w["bits"], w["bits_id"] = _bitstream_dims(cid, p), cid
        elif cid == "ANMF" and w["bits"] is None and len(p) >= 24:
            # frame payload: x,y,w-1,h-1 (24-bit each), duration (24), flags (8), then the frame's own chunks
            sub = chunks(b"RIFF\0\0\0\0WEBP" + p[16:]) or []
            for scid, sp in sub:
                if scid in ("VP8 ", "VP8L"):
                    w["bits"], w["bits_id"] = _bitstream_dims(scid, sp), scid
                    break
        elif cid == "ANIM" and len(p) >= 6 and w["loop"] is None:
            w["loop"] = struct.unpack_from("<H", p, 4)[0]
        elif cid == "ICCP" and w["icc"] is None:
            w["icc"] = p
    return w


def dims(b):
    """(w, h) of a WebP (VP8X canvas, else bitstream), "none" when not WebP / unreadable."""
    w = parse(b)
    if w is None:
        return "none"
    d = w["canvas"] or w["bits"]
    return d or "none"


def webp_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed WebP never raises past the extractor
        return None


def _flag(w, bit, cid):
    return bool((w["flags"] or 0) & bit) or cid in w["ids"]


def _value(b, f):
    w = parse(b)
    if w is None:
        return "none"
    if f.endswith("dimensions_pixels") or f in ("width", "height", "image_width", "image_height",
                                                  "canvas_width", "canvas_height"):
        if f.startswith(("bitstream", "vp8_", "vp8l", "frame")):
            d = w["bits"]
            if f.startswith("vp8l") and w["bits_id"] != "VP8L" or f.startswith("vp8_") and w["bits_id"] != "VP8 ":
                return "none"
        elif f.startswith(("canvas", "vp8x")):
            d = w["canvas"]
        else:
            d = w["canvas"] or w["bits"]
        if not d:
            return "none"
        if f.endswith("width"):
            return d[0]
        if f.endswith("height"):
            return d[1]
        return Dims(*d)
    if f in ("chunk_ids", "chunk_names", "chunk_list", "chunk_order", "riff_chunk_ids"):
        return list(w["ids"])
    if f == "chunk_count":
        return len(w["ids"])
    if f == "riff_size":
        return w["riff_size"]
    if f in ("bitstream_format", "image_chunk_id"):
        return w["bits_id"] or "none"
    if f == "compression":
        return {"VP8 ": "lossy", "VP8L": "lossless"}.get(w["bits_id"], "none")
    if f == "is_lossless":
        return w["bits_id"] == "VP8L"
    if f == "vp8x_flags_u8_hex":
        return "none" if w["flags"] is None else Hex(w["flags"], 2)
    if "exif" in f:
        return _flag(w, 0x08, "EXIF")
    if "xmp" in f:
        return _flag(w, 0x04, "XMP ")
    if f in ("has_icc", "has_icc_profile", "icc_present", "icc_profile_present"):
        return _flag(w, 0x20, "ICCP")
    if "alpha" in f:
        return _flag(w, 0x10, "ALPH") or w["bits_id"] == "VP8L" and _vp8l_alpha(b)
    if f in ("has_animation", "is_animated", "animated"):
        return _flag(w, 0x02, "ANIM")
    if f in ("frame_count", "number_of_frames", "anmf_count", "animation_frame_count"):
        return w["frames"] if w["frames"] or _flag(w, 0x02, "ANIM") else 1
    if "loop" in f:
        return "none" if w["loop"] is None else w["loop"]
    if "icc" in f or f == "profile_description":
        from .image import icc_field
        return icc_field(w["icc"], f)
    return None


def _vp8l_alpha(b):
    for cid, p in chunks(b) or []:
        if cid == "VP8L" and len(p) >= 5:
            return bool((struct.unpack_from("<I", p, 1)[0] >> 28) & 1)
    return False
