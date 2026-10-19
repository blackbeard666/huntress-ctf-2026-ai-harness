"""HEIF / HEIC / AVIF (ISO/IEC 23008-12, ISOBMFF) still-image fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout: ftyp (major_brand 4cc, minor_version u32, compatible brands) + meta FullBox { hdlr 'pict', pitm (primary
item id: u16 v0 / u32 v1), iinf (entry count; infe v2: item_ID u16, protection u16, item_type 4cc, name\\0; v3: u32
id), iloc, iprp { ipco (property boxes: ispe = FullBox + width u32 + height u32, colr 'prof'/'rICC' = ICC),
ipma (per item: 1-based property indices, 7-bit or 15-bit with the essential bit) } }.
dimensions_pixels = the ispe ASSOCIATED WITH THE PRIMARY ITEM (pitm) -- not the first ispe (a thumbnail / grid tile
can come first; exiftool ImageSpatialExtent of the primary). major_brand = the stored 4cc ("heic", "avif", "mif1"),
not exiftool's long name. item_count = iinf entry count (infe boxes read). has_exif = an infe of type "Exif".
A brand outside heic/heix/hevc/heim/heis/mif1/msf1/avif/avis -> "none" (an MP4 / MOV is not an image)."""
import struct

from ..spell import Dims

_BRANDS = {b"heic", b"heix", b"hevc", b"hevx", b"heim", b"heis", b"mif1", b"msf1", b"avif", b"avis", b"mif2"}

FIELDS = {
    ("heic", "major_brand"): "heif_value",
    ("heic", "ftyp_major_brand"): "heif_value",
    ("heic", "minor_version"): "heif_value",
    ("heic", "compatible_brands"): "heif_value",
    ("heic", "dimensions_pixels"): "heif_value",
    ("heic", "image_dimensions_pixels"): "heif_value",
    ("heic", "primary_item_dimensions_pixels"): "heif_value",
    ("heic", "primary_image_dimensions_pixels"): "heif_value",
    ("heic", "ispe_dimensions_pixels"): "heif_value",
    ("heic", "primary_ispe_dimensions_pixels"): "heif_value",
    ("heic", "image_spatial_extent"): "heif_value",
    ("heic", "image_width"): "heif_value",
    ("heic", "image_height"): "heif_value",
    ("heic", "primary_item_id"): "heif_value",
    ("heic", "pitm_item_id"): "heif_value",
    ("heic", "primary_item_type"): "heif_value",
    ("heic", "item_count"): "heif_value",
    ("heic", "iinf_entry_count"): "heif_value",
    ("heic", "item_types"): "heif_value",
    ("heic", "has_exif"): "heif_value",
    ("heic", "exif_present"): "heif_value",
    ("heic", "exif_item_present"): "heif_value",
    ("heic", "has_icc"): "heif_value",
    ("heic", "icc_profile_description"): "heif_value",
    ("heic", "icc_color_space"): "heif_value",
    ("heic", "icc_device_class"): "heif_value",
    ("heic", "icc_version"): "heif_value",
    ("heif", "major_brand"): "heif_value",
    ("heif", "ftyp_major_brand"): "heif_value",
    ("heif", "minor_version"): "heif_value",
    ("heif", "compatible_brands"): "heif_value",
    ("heif", "dimensions_pixels"): "heif_value",
    ("heif", "image_dimensions_pixels"): "heif_value",
    ("heif", "primary_item_dimensions_pixels"): "heif_value",
    ("heif", "primary_image_dimensions_pixels"): "heif_value",
    ("heif", "ispe_dimensions_pixels"): "heif_value",
    ("heif", "primary_ispe_dimensions_pixels"): "heif_value",
    ("heif", "image_spatial_extent"): "heif_value",
    ("heif", "image_width"): "heif_value",
    ("heif", "image_height"): "heif_value",
    ("heif", "primary_item_id"): "heif_value",
    ("heif", "pitm_item_id"): "heif_value",
    ("heif", "primary_item_type"): "heif_value",
    ("heif", "item_count"): "heif_value",
    ("heif", "iinf_entry_count"): "heif_value",
    ("heif", "item_types"): "heif_value",
    ("heif", "has_exif"): "heif_value",
    ("heif", "exif_present"): "heif_value",
    ("heif", "exif_item_present"): "heif_value",
    ("heif", "has_icc"): "heif_value",
    ("heif", "icc_profile_description"): "heif_value",
    ("heif", "icc_color_space"): "heif_value",
    ("heif", "icc_device_class"): "heif_value",
    ("heif", "icc_version"): "heif_value",
    ("avif", "major_brand"): "heif_value",
    ("avif", "ftyp_major_brand"): "heif_value",
    ("avif", "minor_version"): "heif_value",
    ("avif", "compatible_brands"): "heif_value",
    ("avif", "dimensions_pixels"): "heif_value",
    ("avif", "image_dimensions_pixels"): "heif_value",
    ("avif", "primary_item_dimensions_pixels"): "heif_value",
    ("avif", "primary_image_dimensions_pixels"): "heif_value",
    ("avif", "ispe_dimensions_pixels"): "heif_value",
    ("avif", "primary_ispe_dimensions_pixels"): "heif_value",
    ("avif", "image_spatial_extent"): "heif_value",
    ("avif", "image_width"): "heif_value",
    ("avif", "image_height"): "heif_value",
    ("avif", "primary_item_id"): "heif_value",
    ("avif", "pitm_item_id"): "heif_value",
    ("avif", "primary_item_type"): "heif_value",
    ("avif", "item_count"): "heif_value",
    ("avif", "iinf_entry_count"): "heif_value",
    ("avif", "item_types"): "heif_value",
    ("avif", "has_exif"): "heif_value",
    ("avif", "exif_present"): "heif_value",
    ("avif", "exif_item_present"): "heif_value",
    ("avif", "has_icc"): "heif_value",
    ("avif", "icc_profile_description"): "heif_value",
    ("avif", "icc_color_space"): "heif_value",
    ("avif", "icc_device_class"): "heif_value",
    ("avif", "icc_version"): "heif_value",
}


def _boxes(b, off, end):
    out = []
    while off + 8 <= end:
        n = struct.unpack_from(">I", b, off)[0]
        typ = bytes(b[off + 4:off + 8])
        hdr = 8
        if n == 1 and off + 16 <= end:
            n, hdr = struct.unpack_from(">Q", b, off + 8)[0], 16
        elif n == 0:
            n = end - off
        if n < hdr or off + n > end:
            out.append((typ, off + hdr, end))
            break
        out.append((typ, off + hdr, off + n))
        off += n
    return out


def parse(b):
    """dict of the HEIF image structure, or None when the bytes are not a HEIF/AVIF still."""
    if not b or len(b) < 16 or bytes(b[4:8]) != b"ftyp":
        return None
    top = _boxes(b, 0, len(b))
    ftyp = next((x for x in top if x[0] == b"ftyp"), None)
    s, e = ftyp[1], ftyp[2]
    major = bytes(b[s:s + 4])
    compat = [bytes(b[i:i + 4]) for i in range(s + 8, e - 3, 4)]
    if major not in _BRANDS and not (_BRANDS & set(compat) and b"meta" in [t for t, _, _ in top]):
        return None
    h = {"major": major.decode("latin-1"), "minor": struct.unpack_from(">I", b, s + 4)[0] if e - s >= 8 else None,
         "compat": [c.decode("latin-1") for c in compat], "pitm": None, "items": [], "props": [], "assoc": {}}
    meta = next((x for x in top if x[0] == b"meta"), None)
    if meta is None:
        return h
    for typ, cs, ce in _boxes(b, meta[1] + 4, meta[2]):
        ver = b[cs] if cs < ce else 0
        if typ == b"pitm":
            h["pitm"] = struct.unpack_from(">H" if ver == 0 else ">I", b, cs + 4)[0]
        elif typ == b"iinf":
            p = cs + 4 + (2 if ver == 0 else 4)
            for t2, s2, e2 in _boxes(b, p, ce):
                if t2 != b"infe":
                    continue
                v2 = b[s2]
                if v2 >= 2:
                    q = s2 + 4
                    iid = struct.unpack_from(">H" if v2 == 2 else ">I", b, q)[0]
                    q += 2 if v2 == 2 else 4
                    q += 2
                    itype = bytes(b[q:q + 4]).decode("latin-1")
                    h["items"].append((iid, itype))
                else:
                    h["items"].append((struct.unpack_from(">H", b, s2 + 4)[0], None))
        elif typ == b"iprp":
            for t2, s2, e2 in _boxes(b, cs, ce):
                if t2 == b"ipco":
                    h["props"] = [(t3, s3, e3) for t3, s3, e3 in _boxes(b, s2, e2)]
                elif t2 == b"ipma":
                    v2, fl = b[s2], int.from_bytes(b[s2 + 1:s2 + 4], "big")
                    n = struct.unpack_from(">I", b, s2 + 4)[0]
                    q = s2 + 8
                    for _ in range(min(n, 4096)):
                        if q + 3 > e2:
                            break
                        iid = struct.unpack_from(">H" if v2 < 1 else ">I", b, q)[0]
                        q += 2 if v2 < 1 else 4
                        cnt = b[q]
                        q += 1
                        idx = []
                        for _k in range(cnt):
                            if fl & 1:
                                idx.append(struct.unpack_from(">H", b, q)[0] & 0x7FFF)
                                q += 2
                            else:
                                idx.append(b[q] & 0x7F)
                                q += 1
                        h["assoc"].setdefault(iid, idx)
    return h


def _prop(b, h, typ, iid=None):
    """(start, end) of the first `typ` property associated with item `iid` (primary), else the first one at all."""
    iid = h["pitm"] if iid is None else iid
    for i in h["assoc"].get(iid, []):
        if 1 <= i <= len(h["props"]) and h["props"][i - 1][0] == typ:
            return h["props"][i - 1][1:]
    if iid is None or iid not in h["assoc"]:
        for t, s, e in h["props"]:
            if t == typ:
                return s, e
    return None


def dims(b):
    h = parse(b)
    if h is None:
        return "none"
    p = _prop(b, h, b"ispe")
    if not p or p[1] - p[0] < 12:
        return "none"
    return struct.unpack_from(">II", b, p[0] + 4)


def icc(b):
    """The ICC bytes of the primary item's colr 'prof'/'rICC', or None."""
    h = parse(b)
    if h is None:
        return None
    for i in h["assoc"].get(h["pitm"], []) or range(1, len(h["props"]) + 1):
        if 1 <= i <= len(h["props"]):
            t, s, e = h["props"][i - 1]
            if t == b"colr" and bytes(b[s:s + 4]) in (b"prof", b"rICC"):
                return bytes(b[s + 4:e])
    return None


def heif_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed HEIF never raises past the extractor
        return None


def _value(b, f):
    h = parse(b)
    if h is None:
        return "none"
    if f in ("major_brand", "ftyp_major_brand"):
        return h["major"]
    if f == "minor_version":
        return "none" if h["minor"] is None else h["minor"]
    if f == "compatible_brands":
        return h["compat"]
    if f.endswith("dimensions_pixels") or f in ("image_spatial_extent", "image_width", "image_height"):
        d = dims(b)
        if d == "none":
            return d
        return d[0] if f == "image_width" else d[1] if f == "image_height" else Dims(*d)
    if f in ("primary_item_id", "pitm_item_id"):
        return "none" if h["pitm"] is None else h["pitm"]
    if f == "primary_item_type":
        return next((t for i, t in h["items"] if i == h["pitm"]), None) or "none"
    if f in ("item_count", "iinf_entry_count"):
        return len(h["items"])
    if f == "item_types":
        return [t for _, t in h["items"]]
    if "exif" in f:
        return any(t == "Exif" for _, t in h["items"])
    if f == "has_icc":
        return icc(b) is not None
    if "icc" in f:
        from .image import icc_field
        return icc_field(icc(b), f)
    return None
