"""GIF header / block-stream fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout (GIF89a spec): Header = "GIF" + version[3] ("87a" | "89a"); Logical Screen Descriptor at +6: width u16le,
height u16le, packed u8 (bit 7 = global color table flag, bits 0-2 = size N -> 2^(N+1) entries), background color
index u8, pixel aspect ratio u8; then the global color table (3 * 2^(N+1) bytes) when flagged. Block stream: 0x2C Image
Descriptor (9 bytes + optional local color table + LZW min code size + data sub-blocks), 0x21 Extension (label +
sub-blocks; 0xFF "NETSCAPE2.0" carries the loop count, 0xFE is a Comment), 0x3B Trailer.
version = the 3 stored version bytes verbatim ("89a", exiftool GIFVersion). logical_screen_dimensions_pixels = the LSD
WxH (NOT a frame's own size -- a frame descriptor may be smaller/offset). frame_count = number of Image Descriptors
(exiftool FrameCount); a truncated stream counts the frames read so far. loop_count = the NETSCAPE2.0 u16 (0 = forever),
"none" when the extension is absent. Not "GIF8[79]a" (decoy / renamed PNG) -> "none"."""
import struct

from ..spell import Dims

FIELDS = {
    ("gif", "logical_screen_dimensions_pixels"): "gif_value",
    ("gif", "logical_screen_descriptor_dimensions_pixels"): "gif_value",
    ("gif", "lsd_dimensions_pixels"): "gif_value",
    ("gif", "screen_dimensions_pixels"): "gif_value",
    ("gif", "dimensions_pixels"): "gif_value",
    ("gif", "image_dimensions_pixels"): "gif_value",
    ("gif", "logical_screen_width"): "gif_value",
    ("gif", "logical_screen_height"): "gif_value",
    ("gif", "version"): "gif_value",
    ("gif", "header_version"): "gif_value",
    ("gif", "gif_version"): "gif_value",
    ("gif", "signature_version"): "gif_value",
    ("gif", "frame_count"): "gif_value",
    ("gif", "image_count"): "gif_value",
    ("gif", "image_descriptor_count"): "gif_value",
    ("gif", "number_of_frames"): "gif_value",
    ("gif", "frames_count"): "gif_value",
    ("gif", "global_color_table_present"): "gif_value",
    ("gif", "has_global_color_table"): "gif_value",
    ("gif", "global_color_table_flag"): "gif_value",
    ("gif", "global_color_table_size"): "gif_value",
    ("gif", "global_color_table_entries"): "gif_value",
    ("gif", "background_color_index"): "gif_value",
    ("gif", "loop_count"): "gif_value",
    ("gif", "netscape_loop_count"): "gif_value",
    ("gif", "comment"): "gif_value",
    ("gif", "comment_text"): "gif_value",
}


def _skip_subblocks(b, off):
    """Offset after a data sub-block chain (terminated by a 0 length), or None when truncated."""
    while off < len(b):
        n = b[off]
        off += 1
        if n == 0:
            return off
        off += n
    return None


def _subblocks(b, off):
    out = bytearray()
    while off < len(b):
        n = b[off]
        if n == 0:
            break
        out += b[off + 1:off + 1 + n]
        off += 1 + n
    return bytes(out)


def _parse(b):
    if not b or len(b) < 13 or bytes(b[:3]) != b"GIF" or bytes(b[3:6]) not in (b"87a", b"89a"):
        return None
    w, h, packed, bg = struct.unpack_from("<HHBB", b, 6)
    g = {"version": bytes(b[3:6]).decode(), "w": w, "h": h, "gct": bool(packed & 0x80),
         "gct_size": 2 << (packed & 7), "bg": bg, "frames": 0, "loop": None, "comments": []}
    off = 13 + (3 * g["gct_size"] if g["gct"] else 0)
    while off < len(b):
        t = b[off]
        if t == 0x3B:
            break
        if t == 0x2C:
            if off + 10 > len(b):
                break
            g["frames"] += 1
            lp = b[off + 9]
            off += 10 + (3 * (2 << (lp & 7)) if lp & 0x80 else 0) + 1     # + LZW minimum code size
        elif t == 0x21:
            if off + 2 > len(b):
                break
            label = b[off + 1]
            if label == 0xFF and off + 3 < len(b) and b[off + 2] == 11:
                app = bytes(b[off + 3:off + 14])
                if app in (b"NETSCAPE2.0", b"ANIMEXTS1.0"):
                    d = _subblocks(b, off + 14)
                    if len(d) >= 3 and d[0] == 1 and g["loop"] is None:
                        g["loop"] = struct.unpack_from("<H", d, 1)[0]
            elif label == 0xFE:
                g["comments"].append(_subblocks(b, off + 2))
            off += 2
        else:
            break
        nxt = _skip_subblocks(b, off)
        if nxt is None:
            break
        off = nxt
    return g


def gif_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed GIF never raises past the extractor
        return None


def _value(b, f):
    g = _parse(b)
    if g is None:
        return "none"
    if f.endswith("dimensions_pixels"):
        return Dims(g["w"], g["h"])
    if f == "logical_screen_width":
        return g["w"]
    if f == "logical_screen_height":
        return g["h"]
    if "version" in f:
        return g["version"]
    if f in ("frame_count", "image_count", "image_descriptor_count", "number_of_frames", "frames_count"):
        return g["frames"]
    if f in ("global_color_table_present", "has_global_color_table", "global_color_table_flag"):
        return g["gct"]
    if f in ("global_color_table_size", "global_color_table_entries"):
        return g["gct_size"] if g["gct"] else "none"
    if f == "background_color_index":
        return g["bg"]
    if "loop" in f:
        return "none" if g["loop"] is None else g["loop"]
    if "comment" in f:
        if not g["comments"]:
            return "none"
        return g["comments"][0].decode("utf-8", "replace").strip()
    return None
