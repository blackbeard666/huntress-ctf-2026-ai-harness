"""`media` primary VIDEO stream crop / aspect / display geometry (aliases `video`, `av`) -- prebuilt, SPECULATIVE.

D18 flavor "originals, crops": the GM asks the size of the first video stream; this module answers the other sizes a
crop question can name. Semantics follow ffprobe -show_streams (first video stream, container order):
  - width/height (media_video.py, incl. the verified primary_video_dimensions): the DECODER size = the SPS size after
    frame_cropping (h264: pic_width_in_mbs*16 - CropUnitX*(left+right); hevc conf_win_*), stsd/PixelWidth fallback.
  - coded_width/height: the MB/CTB-aligned SPS size (h264 1920x1088, hevc pic_width_in_luma_samples); no SPS -> width.
  - sample_aspect_ratio "N:M" (ffprobe av_guess_sample_aspect_ratio: the STREAM sar wins over the codec's): MP4 pasp
    hSpacing:vSpacing; else MP4 tkhd vs stsd size (mov.c legacy rule); Matroska DisplayWidth/DisplayHeight (unit < 4)
    -> (PixelHeight*DW):(PixelWidth*DH); else the SPS VUI aspect_ratio_idc table / 255 = explicit sar_w:sar_h; else
    "none" (ffprobe prints N/A and omits it from JSON). display_aspect_ratio = reduced (w*sarN):(h*sarD).
  - sps_dimensions_pixels: the SPS size AFTER cropping (sps_coded_dimensions_pixels: before). stsd_dimensions_pixels:
    VisualSampleEntry width x height. tkhd_dimensions_pixels: 16.16 fixed -> int when whole, else 3 decimals.
    display_dimensions_pixels: tkhd size, swapped when |rotation| = 90 (Matroska: DisplayWidth x DisplayHeight when
    DisplayUnit = 0 pixels).
  - clean_aperture_dimensions: MP4/MOV `clap` widthN/D x heightN/D (+ horiz/vert offsets); tapt_clef/prof/enof:
    QuickTime track aperture boxes (16.16). Matroska PixelCropTop/Bottom/Left/Right (0x54BB/54AA/54CC/54DD) and
    DisplayWidth/Height/Unit (0x54B0/54BA/54B2); mkv_pixel_crop -> {"top","bottom","left","right"} JSON.
  - is_cropped: SPS crop / clap smaller than stsd / PixelCrop non-zero / tkhd smaller than coded.
  - geometry_mismatch: stsd (or PixelWidth) != SPS-cropped size, or tkhd != SPS width scaled by the SAR.
Absent box / no video stream / non-media -> "none"; unreadable media -> None."""
import math
import struct

from ..spell import Dims
from .media_video import _NON_MEDIA, _audio_only, _boxes, _child, _ebml, _fix, _path, _rot, video_streams

FIELDS = {
    ("media", "primary_video_sample_aspect_ratio"): "geometry_value",
    ("media", "sample_aspect_ratio"): "geometry_value",
    ("media", "video_sample_aspect_ratio"): "geometry_value",
    ("media", "primary_video_sar"): "geometry_value",
    ("media", "sar"): "geometry_value",
    ("media", "pixel_aspect_ratio"): "geometry_value",
    ("media", "primary_video_pixel_aspect_ratio"): "geometry_value",
    ("media", "pasp_ratio"): "geometry_value",
    ("media", "pasp_aspect_ratio"): "geometry_value",
    ("media", "primary_video_display_aspect_ratio"): "geometry_value",
    ("media", "display_aspect_ratio"): "geometry_value",
    ("media", "video_display_aspect_ratio"): "geometry_value",
    ("media", "primary_video_dar"): "geometry_value",
    ("media", "dar"): "geometry_value",
    ("media", "primary_video_coded_width"): "geometry_value",
    ("media", "coded_width"): "geometry_value",
    ("media", "video_coded_width"): "geometry_value",
    ("media", "primary_video_coded_height"): "geometry_value",
    ("media", "coded_height"): "geometry_value",
    ("media", "video_coded_height"): "geometry_value",
    ("media", "primary_video_coded_dimensions"): "geometry_value",
    ("media", "primary_video_coded_dimensions_pixels"): "geometry_value",
    ("media", "coded_dimensions"): "geometry_value",
    ("media", "coded_dimensions_pixels"): "geometry_value",
    ("media", "video_coded_dimensions_pixels"): "geometry_value",
    ("media", "sps_coded_dimensions_pixels"): "geometry_value",
    ("media", "sps_dimensions_pixels"): "geometry_value",
    ("media", "primary_video_sps_dimensions_pixels"): "geometry_value",
    ("media", "sps_dimensions"): "geometry_value",
    ("media", "sps_crop"): "geometry_value",
    ("media", "sps_frame_cropping"): "geometry_value",
    ("media", "stsd_dimensions_pixels"): "geometry_value",
    ("media", "primary_video_stsd_dimensions_pixels"): "geometry_value",
    ("media", "sample_entry_dimensions_pixels"): "geometry_value",
    ("media", "visual_sample_entry_dimensions_pixels"): "geometry_value",
    ("media", "stsd_dimensions"): "geometry_value",
    ("media", "tkhd_dimensions_pixels"): "geometry_value",
    ("media", "primary_video_tkhd_dimensions_pixels"): "geometry_value",
    ("media", "track_header_dimensions_pixels"): "geometry_value",
    ("media", "tkhd_dimensions"): "geometry_value",
    ("media", "tkhd_width"): "geometry_value",
    ("media", "tkhd_height"): "geometry_value",
    ("media", "display_dimensions_pixels"): "geometry_value",
    ("media", "primary_video_display_dimensions_pixels"): "geometry_value",
    ("media", "display_dimensions"): "geometry_value",
    ("media", "video_display_dimensions_pixels"): "geometry_value",
    ("media", "clean_aperture_dimensions"): "geometry_value",
    ("media", "clean_aperture_dimensions_pixels"): "geometry_value",
    ("media", "clap_dimensions_pixels"): "geometry_value",
    ("media", "clap_dimensions"): "geometry_value",
    ("media", "clean_aperture_horiz_offset"): "geometry_value",
    ("media", "clean_aperture_vert_offset"): "geometry_value",
    ("media", "clap_horiz_offset"): "geometry_value",
    ("media", "clap_vert_offset"): "geometry_value",
    ("media", "tapt_clef_dimensions_pixels"): "geometry_value",
    ("media", "tapt_prof_dimensions_pixels"): "geometry_value",
    ("media", "tapt_enof_dimensions_pixels"): "geometry_value",
    ("media", "clef_dimensions_pixels"): "geometry_value",
    ("media", "prof_dimensions_pixels"): "geometry_value",
    ("media", "enof_dimensions_pixels"): "geometry_value",
    ("media", "clean_aperture_display_dimensions_pixels"): "geometry_value",
    ("media", "production_aperture_dimensions_pixels"): "geometry_value",
    ("media", "encoded_pixels_dimensions_pixels"): "geometry_value",
    ("media", "mkv_pixel_crop"): "geometry_value",
    ("media", "pixel_crop"): "geometry_value",
    ("media", "mkv_pixel_crop_top"): "geometry_value",
    ("media", "mkv_pixel_crop_bottom"): "geometry_value",
    ("media", "mkv_pixel_crop_left"): "geometry_value",
    ("media", "mkv_pixel_crop_right"): "geometry_value",
    ("media", "pixel_crop_top"): "geometry_value",
    ("media", "pixel_crop_bottom"): "geometry_value",
    ("media", "pixel_crop_left"): "geometry_value",
    ("media", "pixel_crop_right"): "geometry_value",
    ("media", "mkv_display_width"): "geometry_value",
    ("media", "mkv_display_height"): "geometry_value",
    ("media", "mkv_display_unit"): "geometry_value",
    ("media", "display_width"): "geometry_value",
    ("media", "display_height"): "geometry_value",
    ("media", "display_unit"): "geometry_value",
    ("media", "mkv_display_dimensions"): "geometry_value",
    ("media", "mkv_display_dimensions_pixels"): "geometry_value",
    ("media", "is_cropped"): "geometry_value",
    ("media", "primary_video_is_cropped"): "geometry_value",
    ("media", "video_is_cropped"): "geometry_value",
    ("media", "cropped"): "geometry_value",
    ("media", "geometry_mismatch"): "geometry_value",
    ("media", "primary_video_geometry_mismatch"): "geometry_value",
    ("media", "video_geometry_mismatch"): "geometry_value",
    ("media", "dimensions_mismatch"): "geometry_value",
    ("video", "primary_video_sample_aspect_ratio"): "geometry_value",
    ("video", "sample_aspect_ratio"): "geometry_value",
    ("video", "video_sample_aspect_ratio"): "geometry_value",
    ("video", "primary_video_sar"): "geometry_value",
    ("video", "sar"): "geometry_value",
    ("video", "pixel_aspect_ratio"): "geometry_value",
    ("video", "primary_video_pixel_aspect_ratio"): "geometry_value",
    ("video", "pasp_ratio"): "geometry_value",
    ("video", "pasp_aspect_ratio"): "geometry_value",
    ("video", "primary_video_display_aspect_ratio"): "geometry_value",
    ("video", "display_aspect_ratio"): "geometry_value",
    ("video", "video_display_aspect_ratio"): "geometry_value",
    ("video", "primary_video_dar"): "geometry_value",
    ("video", "dar"): "geometry_value",
    ("video", "primary_video_coded_width"): "geometry_value",
    ("video", "coded_width"): "geometry_value",
    ("video", "video_coded_width"): "geometry_value",
    ("video", "primary_video_coded_height"): "geometry_value",
    ("video", "coded_height"): "geometry_value",
    ("video", "video_coded_height"): "geometry_value",
    ("video", "primary_video_coded_dimensions"): "geometry_value",
    ("video", "primary_video_coded_dimensions_pixels"): "geometry_value",
    ("video", "coded_dimensions"): "geometry_value",
    ("video", "coded_dimensions_pixels"): "geometry_value",
    ("video", "video_coded_dimensions_pixels"): "geometry_value",
    ("video", "sps_coded_dimensions_pixels"): "geometry_value",
    ("video", "sps_dimensions_pixels"): "geometry_value",
    ("video", "primary_video_sps_dimensions_pixels"): "geometry_value",
    ("video", "sps_dimensions"): "geometry_value",
    ("video", "sps_crop"): "geometry_value",
    ("video", "sps_frame_cropping"): "geometry_value",
    ("video", "stsd_dimensions_pixels"): "geometry_value",
    ("video", "primary_video_stsd_dimensions_pixels"): "geometry_value",
    ("video", "sample_entry_dimensions_pixels"): "geometry_value",
    ("video", "visual_sample_entry_dimensions_pixels"): "geometry_value",
    ("video", "stsd_dimensions"): "geometry_value",
    ("video", "tkhd_dimensions_pixels"): "geometry_value",
    ("video", "primary_video_tkhd_dimensions_pixels"): "geometry_value",
    ("video", "track_header_dimensions_pixels"): "geometry_value",
    ("video", "tkhd_dimensions"): "geometry_value",
    ("video", "tkhd_width"): "geometry_value",
    ("video", "tkhd_height"): "geometry_value",
    ("video", "display_dimensions_pixels"): "geometry_value",
    ("video", "primary_video_display_dimensions_pixels"): "geometry_value",
    ("video", "display_dimensions"): "geometry_value",
    ("video", "video_display_dimensions_pixels"): "geometry_value",
    ("video", "clean_aperture_dimensions"): "geometry_value",
    ("video", "clean_aperture_dimensions_pixels"): "geometry_value",
    ("video", "clap_dimensions_pixels"): "geometry_value",
    ("video", "clap_dimensions"): "geometry_value",
    ("video", "clean_aperture_horiz_offset"): "geometry_value",
    ("video", "clean_aperture_vert_offset"): "geometry_value",
    ("video", "clap_horiz_offset"): "geometry_value",
    ("video", "clap_vert_offset"): "geometry_value",
    ("video", "tapt_clef_dimensions_pixels"): "geometry_value",
    ("video", "tapt_prof_dimensions_pixels"): "geometry_value",
    ("video", "tapt_enof_dimensions_pixels"): "geometry_value",
    ("video", "clef_dimensions_pixels"): "geometry_value",
    ("video", "prof_dimensions_pixels"): "geometry_value",
    ("video", "enof_dimensions_pixels"): "geometry_value",
    ("video", "clean_aperture_display_dimensions_pixels"): "geometry_value",
    ("video", "production_aperture_dimensions_pixels"): "geometry_value",
    ("video", "encoded_pixels_dimensions_pixels"): "geometry_value",
    ("video", "mkv_pixel_crop"): "geometry_value",
    ("video", "pixel_crop"): "geometry_value",
    ("video", "mkv_pixel_crop_top"): "geometry_value",
    ("video", "mkv_pixel_crop_bottom"): "geometry_value",
    ("video", "mkv_pixel_crop_left"): "geometry_value",
    ("video", "mkv_pixel_crop_right"): "geometry_value",
    ("video", "pixel_crop_top"): "geometry_value",
    ("video", "pixel_crop_bottom"): "geometry_value",
    ("video", "pixel_crop_left"): "geometry_value",
    ("video", "pixel_crop_right"): "geometry_value",
    ("video", "mkv_display_width"): "geometry_value",
    ("video", "mkv_display_height"): "geometry_value",
    ("video", "mkv_display_unit"): "geometry_value",
    ("video", "display_width"): "geometry_value",
    ("video", "display_height"): "geometry_value",
    ("video", "display_unit"): "geometry_value",
    ("video", "mkv_display_dimensions"): "geometry_value",
    ("video", "mkv_display_dimensions_pixels"): "geometry_value",
    ("video", "is_cropped"): "geometry_value",
    ("video", "primary_video_is_cropped"): "geometry_value",
    ("video", "video_is_cropped"): "geometry_value",
    ("video", "cropped"): "geometry_value",
    ("video", "geometry_mismatch"): "geometry_value",
    ("video", "primary_video_geometry_mismatch"): "geometry_value",
    ("video", "video_geometry_mismatch"): "geometry_value",
    ("video", "dimensions_mismatch"): "geometry_value",
    ("av", "primary_video_sample_aspect_ratio"): "geometry_value",
    ("av", "sample_aspect_ratio"): "geometry_value",
    ("av", "video_sample_aspect_ratio"): "geometry_value",
    ("av", "primary_video_sar"): "geometry_value",
    ("av", "sar"): "geometry_value",
    ("av", "pixel_aspect_ratio"): "geometry_value",
    ("av", "primary_video_pixel_aspect_ratio"): "geometry_value",
    ("av", "pasp_ratio"): "geometry_value",
    ("av", "pasp_aspect_ratio"): "geometry_value",
    ("av", "primary_video_display_aspect_ratio"): "geometry_value",
    ("av", "display_aspect_ratio"): "geometry_value",
    ("av", "video_display_aspect_ratio"): "geometry_value",
    ("av", "primary_video_dar"): "geometry_value",
    ("av", "dar"): "geometry_value",
    ("av", "primary_video_coded_width"): "geometry_value",
    ("av", "coded_width"): "geometry_value",
    ("av", "video_coded_width"): "geometry_value",
    ("av", "primary_video_coded_height"): "geometry_value",
    ("av", "coded_height"): "geometry_value",
    ("av", "video_coded_height"): "geometry_value",
    ("av", "primary_video_coded_dimensions"): "geometry_value",
    ("av", "primary_video_coded_dimensions_pixels"): "geometry_value",
    ("av", "coded_dimensions"): "geometry_value",
    ("av", "coded_dimensions_pixels"): "geometry_value",
    ("av", "video_coded_dimensions_pixels"): "geometry_value",
    ("av", "sps_coded_dimensions_pixels"): "geometry_value",
    ("av", "sps_dimensions_pixels"): "geometry_value",
    ("av", "primary_video_sps_dimensions_pixels"): "geometry_value",
    ("av", "sps_dimensions"): "geometry_value",
    ("av", "sps_crop"): "geometry_value",
    ("av", "sps_frame_cropping"): "geometry_value",
    ("av", "stsd_dimensions_pixels"): "geometry_value",
    ("av", "primary_video_stsd_dimensions_pixels"): "geometry_value",
    ("av", "sample_entry_dimensions_pixels"): "geometry_value",
    ("av", "visual_sample_entry_dimensions_pixels"): "geometry_value",
    ("av", "stsd_dimensions"): "geometry_value",
    ("av", "tkhd_dimensions_pixels"): "geometry_value",
    ("av", "primary_video_tkhd_dimensions_pixels"): "geometry_value",
    ("av", "track_header_dimensions_pixels"): "geometry_value",
    ("av", "tkhd_dimensions"): "geometry_value",
    ("av", "tkhd_width"): "geometry_value",
    ("av", "tkhd_height"): "geometry_value",
    ("av", "display_dimensions_pixels"): "geometry_value",
    ("av", "primary_video_display_dimensions_pixels"): "geometry_value",
    ("av", "display_dimensions"): "geometry_value",
    ("av", "video_display_dimensions_pixels"): "geometry_value",
    ("av", "clean_aperture_dimensions"): "geometry_value",
    ("av", "clean_aperture_dimensions_pixels"): "geometry_value",
    ("av", "clap_dimensions_pixels"): "geometry_value",
    ("av", "clap_dimensions"): "geometry_value",
    ("av", "clean_aperture_horiz_offset"): "geometry_value",
    ("av", "clean_aperture_vert_offset"): "geometry_value",
    ("av", "clap_horiz_offset"): "geometry_value",
    ("av", "clap_vert_offset"): "geometry_value",
    ("av", "tapt_clef_dimensions_pixels"): "geometry_value",
    ("av", "tapt_prof_dimensions_pixels"): "geometry_value",
    ("av", "tapt_enof_dimensions_pixels"): "geometry_value",
    ("av", "clef_dimensions_pixels"): "geometry_value",
    ("av", "prof_dimensions_pixels"): "geometry_value",
    ("av", "enof_dimensions_pixels"): "geometry_value",
    ("av", "clean_aperture_display_dimensions_pixels"): "geometry_value",
    ("av", "production_aperture_dimensions_pixels"): "geometry_value",
    ("av", "encoded_pixels_dimensions_pixels"): "geometry_value",
    ("av", "mkv_pixel_crop"): "geometry_value",
    ("av", "pixel_crop"): "geometry_value",
    ("av", "mkv_pixel_crop_top"): "geometry_value",
    ("av", "mkv_pixel_crop_bottom"): "geometry_value",
    ("av", "mkv_pixel_crop_left"): "geometry_value",
    ("av", "mkv_pixel_crop_right"): "geometry_value",
    ("av", "pixel_crop_top"): "geometry_value",
    ("av", "pixel_crop_bottom"): "geometry_value",
    ("av", "pixel_crop_left"): "geometry_value",
    ("av", "pixel_crop_right"): "geometry_value",
    ("av", "mkv_display_width"): "geometry_value",
    ("av", "mkv_display_height"): "geometry_value",
    ("av", "mkv_display_unit"): "geometry_value",
    ("av", "display_width"): "geometry_value",
    ("av", "display_height"): "geometry_value",
    ("av", "display_unit"): "geometry_value",
    ("av", "mkv_display_dimensions"): "geometry_value",
    ("av", "mkv_display_dimensions_pixels"): "geometry_value",
    ("av", "is_cropped"): "geometry_value",
    ("av", "primary_video_is_cropped"): "geometry_value",
    ("av", "video_is_cropped"): "geometry_value",
    ("av", "cropped"): "geometry_value",
    ("av", "geometry_mismatch"): "geometry_value",
    ("av", "primary_video_geometry_mismatch"): "geometry_value",
    ("av", "video_geometry_mismatch"): "geometry_value",
    ("av", "dimensions_mismatch"): "geometry_value",
}


def _num(v):
    """16.16 / rational value -> int when whole, else a 3-decimal string."""
    return int(round(v)) if abs(v - round(v)) < 1e-9 else "%.3f" % v


def _dims(w, h):
    if w is None or h is None:
        return None
    return Dims(_num(w), _num(h))


def _reduce(n, d):
    if not n or not d or n < 0 or d < 0:
        return None
    g = math.gcd(int(n), int(d))
    return int(n) // g, int(d) // g


def _mp4_geo(b):
    """First video trak -> {tkhd, matrix rotation, stsd, pasp, clap, tapt clef/prof/enof} (raw container geometry)."""
    if b[4:8] not in (b"ftyp", b"moov", b"mdat", b"free", b"wide", b"skip", b"pnot"):
        return None
    moov = None
    for t, s, e in _boxes(b, 0, len(b)):
        if t == b"moov":
            moov = (s, e)
    if moov is None:
        return None
    for t, ts, te in _boxes(b, *moov):
        if t != b"trak":
            continue
        md = _child(b, ts, te, b"mdia")
        hd = md and _child(b, md[0], md[1], b"hdlr")
        if not hd or b[hd[0] + 8:hd[0] + 12] != b"vide":
            continue
        g = {"kind": "mp4", "rotation": 0}
        tk = _child(b, ts, te, b"tkhd")
        if tk:
            mo = tk[0] + (52 if b[tk[0]] == 1 else 40)
            if mo + 44 <= tk[1]:
                m = struct.unpack_from(">9I", b, mo)
                g["rotation"] = _rot(_fix(m[0]), _fix(m[1]))
                w, h = struct.unpack_from(">II", b, mo + 36)
                g["tkhd"] = (w / 65536.0, h / 65536.0)
        ta = _child(b, ts, te, b"tapt")
        if ta:
            for at, as_, ae in _boxes(b, *ta):
                if at in (b"clef", b"prof", b"enof") and as_ + 12 <= ae:
                    w, h = struct.unpack_from(">II", b, as_ + 4)
                    g[at.decode()] = (w / 65536.0, h / 65536.0)
        stbl = _path(b, md[0], md[1], b"minf", b"stbl")
        sd = stbl and _child(b, stbl[0], stbl[1], b"stsd")
        if sd and sd[0] + 16 <= sd[1]:
            es = sd[0] + 8
            esz, = struct.unpack_from(">I", b, es)
            ee = min(es + esz, sd[1])
            if es + 36 <= ee:
                g["stsd"] = struct.unpack_from(">HH", b, es + 32)
            if es + 86 <= ee:
                for kt, ks, ke in _boxes(b, es + 86, ee):
                    if kt == b"pasp" and ks + 8 <= ke and "pasp" not in g:
                        g["pasp"] = struct.unpack_from(">II", b, ks)
                    elif kt == b"clap" and ks + 32 <= ke and "clap" not in g:
                        v = struct.unpack_from(">IIIIiIiI", b, ks)
                        if v[1] and v[3] and v[5] and v[7]:
                            g["clap"] = (v[0] / v[1], v[2] / v[3], v[4] / v[5], v[6] / v[7])
        return g
    return {"kind": "mp4"}


_MKV_IDS = {0x54BB: "crop_top", 0x54AA: "crop_bottom", 0x54CC: "crop_left", 0x54DD: "crop_right",
            0x54B0: "display_width", 0x54BA: "display_height", 0x54B2: "display_unit", 0xB0: "pixel_width",
            0xBA: "pixel_height"}


def _mkv_geo(b):
    """First video TrackEntry -> {PixelCrop*, Display*, Pixel*} or None."""
    if b[:4] != b"\x1a\x45\xdf\xa3":
        return None
    for eid, s, e in _ebml(b, 0, len(b)):
        if eid != 0x18538067:
            continue
        for sid, ss, se in _ebml(b, s, e):
            if sid != 0x1654AE6B:
                continue
            for tid, ts, te in _ebml(b, ss, se):
                if tid != 0xAE:
                    continue
                g, ttype = {"kind": "mkv"}, None
                for fid, fs, fe in _ebml(b, ts, te):
                    if fid == 0x83:
                        ttype = int.from_bytes(b[fs:fe], "big")
                    elif fid == 0xE0:
                        for vid, vs, ve in _ebml(b, fs, fe):
                            if vid in _MKV_IDS:
                                g[_MKV_IDS[vid]] = int.from_bytes(b[vs:ve], "big")
                if ttype == 1:
                    return g
        return {"kind": "mkv"}
    return None


def _geometry(data):
    """-> (stream dict from media_video, raw container geometry dict), or "none" / None."""
    b = bytes(data)
    vs = video_streams(b)
    if vs is None:
        if _audio_only(b):
            return "none"
        head = b[:512]
        text = all(32 <= c < 127 or c in (9, 10, 13) for c in head)
        return "none" if head.startswith(_NON_MEDIA) or text else None
    if not vs:
        return "none"
    g = None
    for fn in (_mp4_geo, _mkv_geo):
        try:
            g = fn(b)
        except (ValueError, IndexError, struct.error, OverflowError, ZeroDivisionError):
            g = None
        if g is not None:
            break
    return vs[0], (g or {})


def _sar(v, g):
    """ffprobe sample_aspect_ratio as (n, d) or None."""
    if g.get("kind") == "mp4":
        p = g.get("pasp")
        if p and p[0] and p[1]:
            return _reduce(*p)
        tk, sd = g.get("tkhd"), g.get("stsd")
        if tk and sd and all(tk) and all(sd) and (int(tk[0]) != sd[0] or int(tk[1]) != sd[1]):
            r = _reduce(int(round(sd[1] * tk[0] * 65536)), int(round(sd[0] * tk[1] * 65536)))
            if r:
                return r
    if g.get("kind") == "mkv":
        dw, dh, pw, ph = g.get("display_width"), g.get("display_height"), g.get("pixel_width"), g.get("pixel_height")
        if dw and dh and pw and ph and g.get("display_unit", 0) < 4:
            return _reduce(ph * dw, pw * dh)
    s = v.get("sps_sar")
    return _reduce(*s) if s and s[0] and s[1] else None


def _crop_any(v, g):
    if any(v.get("sps_crop") or ()):
        return True
    if any(g.get(k) for k in ("crop_top", "crop_bottom", "crop_left", "crop_right")):
        return True
    c, sd = g.get("clap"), g.get("stsd")
    if c and sd and (c[0] < sd[0] or c[1] < sd[1]):
        return True
    tk = g.get("tkhd")
    cw, ch = v.get("coded_width") or v.get("width"), v.get("coded_height") or v.get("height")
    return bool(tk and cw and ch and all(tk) and (tk[0] < cw or tk[1] < ch))


def _mismatch(v, g):
    w, h = v.get("width"), v.get("height")
    if not w or not h:
        return None
    if "coded_width" in v:                               # an SPS parsed: compare the container's claims to it
        cont = g.get("stsd") or (g.get("pixel_width"), g.get("pixel_height"))
        if cont[0] and cont[1] and (cont[0], cont[1]) != (w, h):
            return True
    tk = g.get("tkhd")
    if tk and all(tk):
        s = _sar(v, g) or (1, 1)
        if abs(tk[0] - w * s[0] / s[1]) >= 1 or abs(tk[1] - h) >= 1:
            return True
    return False


# substring -> kind, first match wins (order matters: "coded_dimensions" before "dimensions", "sar" last)
_KIND = [("sample_aspect_ratio", "sar"), ("pixel_aspect_ratio", "sar"), ("pasp_", "sar"),
         ("display_aspect_ratio", "dar"), ("coded_width", "coded_w"), ("coded_height", "coded_h"),
         ("coded_dimensions", "coded"), ("sps_crop", "sps_crop"), ("sps_frame_cropping", "sps_crop"),
         ("sps_dimensions", "sps"), ("stsd_dimensions", "stsd"), ("sample_entry_dimensions", "stsd"),
         ("tkhd_width", "tkhd_w"), ("tkhd_height", "tkhd_h"), ("tkhd_dimensions", "tkhd"),
         ("track_header_dimensions", "tkhd"), ("mkv_display_dimensions", "mkv_disp"),
         ("clean_aperture_display", "clef"), ("production_aperture", "prof"), ("encoded_pixels", "enof"),
         ("clef_", "clef"), ("prof_", "prof"), ("enof_", "enof"), ("display_dimensions", "disp"),
         ("horiz_offset", "clap_h"), ("vert_offset", "clap_v"), ("clean_aperture_dimensions", "clap"),
         ("clap_dimensions", "clap"), ("pixel_crop_top", "crop_top"), ("pixel_crop_bottom", "crop_bottom"),
         ("pixel_crop_left", "crop_left"), ("pixel_crop_right", "crop_right"), ("pixel_crop", "crop"),
         ("display_width", "display_width"), ("display_height", "display_height"),
         ("display_unit", "display_unit"), ("is_cropped", "cropped"), ("cropped", "cropped"),
         ("mismatch", "mismatch"), ("sar", "sar"), ("dar", "dar")]


def _kind(field):
    for key, k in _KIND:
        if key in field:
            return k
    return None


def geometry_value(data, ctx):
    if not data:
        return None
    k = _kind((ctx or {}).get("field") or "")
    if k is None:
        return None
    r = _geometry(data)
    if not isinstance(r, tuple):
        return r
    v, g = r
    w, h = v.get("width"), v.get("height")
    if k in ("sar", "dar"):
        s = _sar(v, g)
        if s is None:
            return "none"
        if k == "sar":
            return "%d:%d" % s
        d = _reduce(w * s[0], h * s[1]) if w and h else None
        return "%d:%d" % d if d else None
    if k in ("coded_w", "coded_h", "coded"):
        cw, ch = v.get("coded_width", w), v.get("coded_height", h)
        if not cw or not ch:
            return None
        return cw if k == "coded_w" else ch if k == "coded_h" else Dims(cw, ch)
    if k == "sps":
        return Dims(w, h) if "coded_width" in v else "none"
    if k == "sps_crop":
        c = v.get("sps_crop")
        return dict(zip(("left", "right", "top", "bottom"), c)) if c else "none"
    if k == "stsd":
        sd = g.get("stsd")
        return Dims(*sd) if sd else "none"
    if k in ("tkhd", "tkhd_w", "tkhd_h"):
        tk = g.get("tkhd")
        if not tk:
            return "none"
        return _dims(*tk) if k == "tkhd" else _num(tk[0] if k == "tkhd_w" else tk[1])
    if k == "disp":
        tk = g.get("tkhd")
        if tk:
            return _dims(*(tk[::-1] if abs(g.get("rotation") or 0) == 90 else tk))
        dw, dh = g.get("display_width"), g.get("display_height")
        return Dims(dw, dh) if dw and dh and not g.get("display_unit") else "none"
    if k == "mkv_disp":
        dw, dh = g.get("display_width"), g.get("display_height")
        return Dims(dw, dh) if dw and dh else "none"
    if k in ("clef", "prof", "enof"):
        a = g.get(k)
        return _dims(*a) if a else "none"
    if k in ("clap", "clap_h", "clap_v"):
        c = g.get("clap")
        if not c:
            return "none"
        return _dims(c[0], c[1]) if k == "clap" else _num(c[2] if k == "clap_h" else c[3])
    if k == "crop":
        if g.get("kind") != "mkv":
            return "none"
        return {s: g.get("crop_" + s, 0) for s in ("top", "bottom", "left", "right")}
    if k.startswith("crop_"):
        return g.get(k, 0) if g.get("kind") == "mkv" else "none"
    if k in ("display_width", "display_height", "display_unit"):
        if g.get("kind") != "mkv":
            return "none"
        if k == "display_unit":
            return g.get(k, 0)
        return g.get(k, g.get("pixel_" + k[8:]))       # spec default: Display* = Pixel* when absent
    if k == "cropped":
        return _crop_any(v, g)
    if k == "mismatch":
        return _mismatch(v, g)
    return None
