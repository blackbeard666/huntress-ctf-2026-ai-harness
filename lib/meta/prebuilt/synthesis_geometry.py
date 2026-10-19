"""Cross-FILE video / image geometry synthesis (prebuilt, SPECULATIVE; spelling never GM-verified).
Coverage-atlas row "originals vs crops, aspect groups, impossible device": the question lists `Files: [...]` members
(mp4/mov/mkv/avi video, jpg/png/gif/bmp/webp/tiff stills) of the artifact's container. Per file:
  * dims = ffprobe width x height of the first video stream (lib.meta.prebuilt.media_video.video_streams: the SPS
    cropped decoder size; a still image is ffprobe's single video stream), area = w*h; rotation = ffprobe displaymatrix
    rotation (signed int, stills / no matrix -> 0); DAR = reduced (w*sarN):(h*sarD) (media_geometry._sar, else 1:1).
  * correlation key = the first >= 12-hex-digit token of the title tag, else of any other tag value (mdta keys /
    udta / Matroska tags / EXIF / PNG text); else ("df", stream duration, nb_frames) -- same duration + frame count.
    A still with neither is a group of its own.
  * claimed device = media_device make/model (mdta com.apple.quicktime.* / com.android.* / udta (c)mak (c)mod), JPEG /
    TIFF EXIF Make (271) / Model (272) via PIL.
Fields (names in ascending order unless stated; JSON objects with sorted keys, compact):
  dimension_order / pixel_area_order = names by ascending area, ties by name ("descending"/"largest first" in the text
  reverses the area order, ties still by name); largest_frame_file / smallest_frame_file; aspect_ratio_groups =
  {DAR: [names]}; rotation_groups = {rotation: [names]}; original_files = per correlation group the largest frame (tie
  -> first name); cropped_files = a group member smaller than its original, or carrying an explicit container crop
  (MP4 clap smaller than stsd, Matroska PixelCrop*; the SPS macroblock-alignment crop does NOT count); crop_of =
  {crop: original}; odd_device_file = the one file whose claimed (make, model) disagrees with a strict majority of the
  other claimants, else the one claimant whose geometry is impossible for a camera: a desktop-screen frame size
  (1366x768, 1440x900, ...) or a portrait-orientation tag with an identity matrix and a landscape coded size.
  file_dimensions = {name: "WxH"} in Files order.
Through lib.meta.answer the extractor reads siblings like synthesis_media (ctx["read"] or the container zip `data`).
No media member in a container -> "none"; a lone member / no reader / undecidable odd device -> None."""
import io
import math
import re
import struct

FIELDS = {
    ("synthesis", "dimension_order"): "geometry_value",
    ("synthesis", "dimensions_order"): "geometry_value",
    ("synthesis", "pixel_area_order"): "geometry_value",
    ("synthesis", "area_order"): "geometry_value",
    ("synthesis", "frame_area_order"): "geometry_value",
    ("synthesis", "frame_size_order"): "geometry_value",
    ("synthesis", "resolution_order"): "geometry_value",
    ("synthesis", "largest_frame_file"): "geometry_value",
    ("synthesis", "largest_frame_filename"): "geometry_value",
    ("synthesis", "largest_frame"): "geometry_value",
    ("synthesis", "largest_resolution_file"): "geometry_value",
    ("synthesis", "highest_resolution_file"): "geometry_value",
    ("synthesis", "smallest_frame_file"): "geometry_value",
    ("synthesis", "aspect_ratio_groups"): "geometry_value",
    ("synthesis", "aspect_groups"): "geometry_value",
    ("synthesis", "dar_groups"): "geometry_value",
    ("synthesis", "display_aspect_ratio_groups"): "geometry_value",
    ("synthesis", "rotation_groups"): "geometry_value",
    ("synthesis", "original_files"): "geometry_value",
    ("synthesis", "original_filenames"): "geometry_value",
    ("synthesis", "originals"): "geometry_value",
    ("synthesis", "cropped_files"): "geometry_value",
    ("synthesis", "cropped_filenames"): "geometry_value",
    ("synthesis", "crops"): "geometry_value",
    ("synthesis", "crop_of"): "geometry_value",
    ("synthesis", "crop_map"): "geometry_value",
    ("synthesis", "crop_sources"): "geometry_value",
    ("synthesis", "crop_original_map"): "geometry_value",
    ("synthesis", "odd_device_file"): "geometry_value",
    ("synthesis", "odd_device_filename"): "geometry_value",
    ("synthesis", "odd_device"): "geometry_value",
    ("synthesis", "impossible_device_file"): "geometry_value",
    ("synthesis", "device_mismatch_file"): "geometry_value",
    ("synthesis", "file_dimensions"): "geometry_value",
    ("synthesis", "dimensions_by_file"): "geometry_value",
}

_CORR = re.compile(r"(?<![0-9A-Fa-f])([0-9A-Fa-f]{12,})(?![0-9A-Fa-f])")
_SCREEN = {(1024, 768), (1280, 800), (1280, 1024), (1360, 768), (1366, 768), (1440, 900), (1536, 864), (1600, 900),
           (1600, 1200), (1680, 1050), (1920, 1200), (2560, 1440), (2560, 1600), (2560, 1664), (2880, 1800),
           (2940, 1912), (3024, 1964), (3440, 1440), (3456, 2234)}
_PORTRAIT = re.compile(r"\bportrait\b", re.I)


def _exif_device(b):
    """(make, model, [text values]) of a JPEG/TIFF/PNG/WebP still via PIL, or (None, None, [])."""
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(b))
        ex = im.getexif()
        texts = [str(v) for v in ex.values() if isinstance(v, (str, bytes))]
        texts += [str(v) for v in (getattr(im, "text", None) or {}).values()]
        mk, md = ex.get(271), ex.get(272)
        clean = lambda v: (v.decode("latin-1") if isinstance(v, bytes) else str(v)).strip("\0 ") or None  # noqa: E731
        return (clean(mk) if mk else None), (clean(md) if md else None), texts
    except Exception:  # noqa: BLE001 - not a PIL-readable still
        return None, None, []


def _tags(b):
    """(title, [all tag values], mdta dict, (make, model))."""
    from . import media_device, media_tags
    title, vals, mdta, dev = None, [], {}, (None, None)
    try:
        r = media_tags._load(b)
        if isinstance(r, tuple):
            title = media_tags._find(r, "title")
            vals += [str(v) for _, v in list(r[0]) + list(r[1])]
    except Exception:  # noqa: BLE001
        pass
    try:
        d = media_device._load(b)
        if isinstance(d, dict):
            mdta = d.get("mdta") or {}
            title = title or mdta.get("title") or (d.get("udta") or {}).get("\xa9nam")
            for src in ("mdta", "udta", "raw", "mkv", "avi"):
                vals += [str(v) for v in (d.get(src) or {}).values()]
            mk, md = media_device._first(d, "make"), media_device._first(d, "model")
            dev = (None if mk == "none" else mk, None if md == "none" else md)
    except Exception:  # noqa: BLE001
        pass
    if dev == (None, None) and (b[:3] == b"\xff\xd8\xff" or b[:4] in (b"II*\0", b"MM\0*") or b[:4] == b"\x89PNG"):
        mk, md, texts = _exif_device(b)
        dev = (mk, md)
        vals += texts
    return title, vals, mdta, dev


def _explicit_crop(b):
    try:
        from . import media_geometry
        g = media_geometry._geometry(b)
        if not isinstance(g, tuple):
            return False
        g = g[1]
        if any(g.get(k) for k in ("crop_top", "crop_bottom", "crop_left", "crop_right")):
            return True
        c, sd = g.get("clap"), g.get("stsd")
        return bool(c and sd and (c[0] < sd[0] or c[1] < sd[1]))
    except Exception:  # noqa: BLE001
        return False


def _dar(b, v, w, h):
    sn = sd = 1
    try:
        from . import media_geometry
        g = media_geometry._geometry(b)
        if isinstance(g, tuple):
            s = media_geometry._sar(g[0], g[1])
            if s and s[0] and s[1]:
                sn, sd = s
    except Exception:  # noqa: BLE001
        pass
    n, d = w * sn, h * sd
    k = math.gcd(n, d) or 1
    return "%d:%d" % (n // k, d // k)


def file_info(b):
    """{w, h, area, rot, dar, key, make, model, crop, portrait} of one media member, or None (not video/still)."""
    from . import media_streams, media_video
    b = bytes(b)
    vs = media_video.video_streams(b)
    if not vs or not vs[0].get("width") or not vs[0].get("height"):
        return None
    v = vs[0]
    w, h = int(v["width"]), int(v["height"])
    title, vals, mdta, dev = _tags(b)
    corr = None
    for t in ([title] if title else []) + vals:
        m = _CORR.search(str(t))
        if m:
            corr = m.group(1).lower()
            break
    key = corr
    is_still = b[:3] == b"\xff\xd8\xff" or b[:4] in (b"\x89PNG", b"GIF8", b"II*\0", b"MM\0*") or b[:2] == b"BM" \
        or (b[:4] == b"RIFF" and b[8:12] == b"WEBP")
    if key is None and not is_still:
        dur = None
        try:
            dur = next((s.get("duration") for s in media_streams.streams(b) or () if s.get("codec_type") == "video"),
                       None)
        except Exception:  # noqa: BLE001
            dur = None
        if dur is not None or v.get("nb_frames") is not None:
            key = ("df", None if dur is None else round(float(dur), 3), v.get("nb_frames"))
    orient = " ".join(str(val) for k, val in mdta.items() if "orientation" in k.lower())
    return {"w": w, "h": h, "area": w * h, "rot": int(v.get("rotation") or 0), "dar": _dar(b, v, w, h), "key": key,
            "make": dev[0], "model": dev[1], "crop": _explicit_crop(b), "portrait": bool(_PORTRAIT.search(orient))}


def geometry(names, get_bytes):
    """{name: info} over the media members among `names`, or None (a file unreadable)."""
    info = {}
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        try:
            i = file_info(b)
        except Exception:  # noqa: BLE001 - a damaged member is simply not a media member
            i = None
        if i is not None:
            info[n] = i
    return info


def _groups(info):
    out, solo = {}, []
    for n in sorted(info):
        k = info[n]["key"]
        if k is None:
            solo.append([n])
        else:
            out.setdefault(repr(k), []).append(n)
    return list(out.values()) + solo


def _originals(info):
    """({crop: original}, [originals]) per correlation group."""
    crop_of, origs = {}, []
    for g in _groups(info):
        o = sorted(g, key=lambda n: (-info[n]["area"], n))[0]
        origs.append(o)
        for n in g:
            if n != o and (info[n]["area"] < info[o]["area"] or info[n]["crop"]):
                crop_of[n] = o
    return crop_of, sorted(origs)


def _odd_device(info):
    claims = {n: ((i["make"] or "").strip().casefold(), (i["model"] or "").strip().casefold())
              for n, i in info.items() if i["make"] or i["model"]}
    if len(claims) >= 3:
        counts = {}
        for c in claims.values():
            counts[c] = counts.get(c, 0) + 1
        top = max(counts.values())
        maj = [c for c, k in counts.items() if k == top]
        if len(maj) == 1 and top > len(claims) / 2:
            odd = sorted(n for n, c in claims.items() if c != maj[0])
            if len(odd) == 1:
                return odd[0]
    bad = []
    for n in claims:
        i = info[n]
        if (i["w"], i["h"]) in _SCREEN or (i["h"], i["w"]) in _SCREEN:
            bad.append(n)
        elif i["portrait"] and i["rot"] == 0 and i["w"] > i["h"]:
            bad.append(n)
    return bad[0] if len(bad) == 1 else None


def _pick(info, field, text):
    f = field or ""
    if f in ("file_dimensions", "dimensions_by_file"):
        return {n: "%dx%d" % (i["w"], i["h"]) for n, i in info.items()}
    if f.endswith("_order"):
        desc = bool(re.search(r"\bdescending\b|\blargest first\b|\bbiggest first\b", text, re.I))
        return sorted(info, key=lambda n: ((-1 if desc else 1) * info[n]["area"], n))
    if f.startswith(("largest", "highest")):
        return sorted(info, key=lambda n: (-info[n]["area"], n))[0]
    if f.startswith("smallest"):
        return sorted(info, key=lambda n: (info[n]["area"], n))[0]
    if f in ("aspect_ratio_groups", "aspect_groups", "dar_groups", "display_aspect_ratio_groups", "rotation_groups"):
        key = "rot" if f == "rotation_groups" else "dar"
        out = {}
        for n in sorted(info):
            out.setdefault(str(info[n][key]), []).append(n)
        return {k: out[k] for k in sorted(out)}
    if "device" in f:
        return _odd_device(info)
    crop_of, origs = _originals(info)
    if f.startswith("original"):
        return origs
    if f in ("cropped_files", "cropped_filenames", "crops"):
        return sorted(crop_of)
    return {k: crop_of[k] for k in sorted(crop_of)}


def geometry_value(data, ctx):
    """synthesis.<geometry field> (see the module docstring)."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        if not names:
            return "none"
        info = geometry(names, read)
        if info is None:
            return None
        if not info:
            return "none" if from_zip else None
        q = ctx.get("question") or {}
        text = str((q.get("question") if isinstance(q, dict) else q) or "")
        return _pick(info, ctx.get("field") or "", text)
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
