"""`media` primary VIDEO stream geometry fields (aliases `video`, `av`) -- prebuilt, SPECULATIVE.

Spelling follows ffprobe -show_streams on the FIRST video stream (container stream order):
  - width / height: coded size from the container (MP4 stsd visual entry, Matroska Video/PixelWidth|PixelHeight,
    AVI strf BITMAPINFOHEADER biWidth/|biHeight|), NOT rotated (ffprobe keeps the coded size; rotation is side data).
  - frame_rate: ffprobe r_frame_rate "num/den" reduced. MP4 = mdhd timescale / dominant stts delta; Matroska =
    1e9 / DefaultDuration snapped to the NTSC/integer rates ffprobe guesses (59.94006 -> 60000/1001); AVI = strh
    dwRate/dwScale.
  - pix_fmt: avcC high-profile tail / SPS chroma_format_idc + bit depth, hvcC chromaFormat/bitDepthLuma, vpcC (Matroska
    CodecPrivate features for VP9), av1C flags, MJPEG first-frame SOF sampling (yuvj*), mpeg4 -> yuv420p, ProRes
    apc* -> yuv422p10le / ap4* -> yuv444p10le.
  - profile: ffprobe profile names ("High", "Constrained Baseline", "Main 10", "Profile 1", "Simple Profile",
    "Standard"); level = ffprobe int (h264 level_idc, hevc general_level_idc, av1 seq_level_idx).
  - rotation: ffprobe displaymatrix "rotation" = -atan2(b, a) of the tkhd matrix, a signed int (a phone-portrait
    matrix [0 1 -1 0] -> -90; 180 -> -180); no matrix / identity -> 0. `rotate` = the legacy clockwise tag
    (exiftool / mediainfo Rotation: 0..359, same matrix -> 90).
  - codec_tag_string / codec_tag: the stsd fourcc / AVI biCompression, ffprobe hex "0x31637661"; Matroska has none
    ("[0][0][0][0]" / 0x00000000 in ffprobe).
A member that is not audio/video -> "none"; audio-only media -> "none"; unreadable media -> None."""
import math
import struct

from ..spell import Dims

FIELDS = {
    ("media", "primary_video_width"): "video_value",
    ("media", "video_width"): "video_value",
    ("media", "primary_video_stream_width"): "video_value",
    ("media", "first_video_width"): "video_value",
    ("media", "video_stream_width"): "video_value",
    ("media", "primary_video_height"): "video_value",
    ("media", "video_height"): "video_value",
    ("media", "primary_video_stream_height"): "video_value",
    ("media", "first_video_height"): "video_value",
    ("media", "video_stream_height"): "video_value",
    ("media", "primary_video_dimensions_pixels"): "video_value",
    ("media", "primary_video_dimensions"): "video_value",
    ("media", "video_dimensions_pixels"): "video_value",
    ("media", "video_dimensions"): "video_value",
    ("media", "video_stream_dimensions_pixels"): "video_value",
    ("media", "primary_video_resolution"): "video_value",
    ("media", "video_resolution"): "video_value",
    ("media", "primary_video_frame_rate"): "video_value",
    ("media", "primary_video_r_frame_rate"): "video_value",
    ("media", "primary_video_avg_frame_rate"): "video_value",
    ("media", "video_frame_rate"): "video_value",
    ("media", "video_r_frame_rate"): "video_value",
    ("media", "r_frame_rate"): "video_value",
    ("media", "frame_rate"): "video_value",
    ("media", "primary_video_pix_fmt"): "video_value",
    ("media", "primary_video_pixel_format"): "video_value",
    ("media", "video_pix_fmt"): "video_value",
    ("media", "video_pixel_format"): "video_value",
    ("media", "pix_fmt"): "video_value",
    ("media", "pixel_format"): "video_value",
    ("media", "primary_video_profile"): "video_value",
    ("media", "primary_video_codec_profile"): "video_value",
    ("media", "video_profile"): "video_value",
    ("media", "video_codec_profile"): "video_value",
    ("media", "primary_video_level"): "video_value",
    ("media", "video_level"): "video_value",
    ("media", "rotation"): "video_value",
    ("media", "primary_video_rotation"): "video_value",
    ("media", "video_rotation"): "video_value",
    ("media", "display_matrix_rotation"): "video_value",
    ("media", "displaymatrix_rotation"): "video_value",
    ("media", "rotate"): "video_value",
    ("media", "rotate_tag"): "video_value",
    ("media", "primary_video_codec_tag_string"): "video_value",
    ("media", "video_codec_tag_string"): "video_value",
    ("media", "primary_video_fourcc"): "video_value",
    ("media", "video_fourcc"): "video_value",
    ("media", "primary_video_codec_tag"): "video_value",
    ("media", "primary_video_codec_tag_hex"): "video_value",
    ("media", "video_codec_tag_hex"): "video_value",
    ("media", "primary_video_nb_frames"): "video_value",
    ("media", "video_nb_frames"): "video_value",
    ("media", "video_frame_count"): "video_value",
    ("video", "primary_video_codec_name"): "video_value",
    ("video", "codec_name"): "video_value",
    ("video", "video_codec_name"): "video_value",
    ("video", "primary_video_width"): "video_value",
    ("video", "width"): "video_value",
    ("video", "primary_video_height"): "video_value",
    ("video", "height"): "video_value",
    ("video", "primary_video_dimensions_pixels"): "video_value",
    ("video", "dimensions_pixels"): "video_value",
    ("video", "primary_video_frame_rate"): "video_value",
    ("video", "frame_rate"): "video_value",
    ("video", "r_frame_rate"): "video_value",
    ("video", "primary_video_pix_fmt"): "video_value",
    ("video", "pix_fmt"): "video_value",
    ("video", "primary_video_profile"): "video_value",
    ("video", "profile"): "video_value",
    ("video", "rotation"): "video_value",
    ("video", "video_stream_count"): "video_value",
}

# ---------------------------------------------------------------- codec tables

_MP4_V = {b"avc1": "h264", b"avc3": "h264", b"hvc1": "hevc", b"hev1": "hevc", b"mp4v": "mpeg4", b"vp08": "vp8",
          b"vp09": "vp9", b"av01": "av1", b"jpeg": "mjpeg", b"mjpa": "mjpeg", b"mjpb": "mjpegb", b"s263": "h263",
          b"h263": "h263", b"apcn": "prores", b"apch": "prores", b"apcs": "prores", b"apco": "prores",
          b"ap4h": "prores", b"ap4x": "prores", b"dvh1": "hevc", b"dvhe": "hevc", b"png ": "png",
          b"mp2v": "mpeg2video", b"raw ": "rawvideo"}
_MKV_V = {"V_MPEG4/ISO/AVC": "h264", "V_MPEGH/ISO/HEVC": "hevc", "V_VP8": "vp8", "V_VP9": "vp9", "V_AV1": "av1",
          "V_MPEG4/ISO/ASP": "mpeg4", "V_MPEG4/ISO/SP": "mpeg4", "V_MPEG4/ISO/AP": "mpeg4", "V_MJPEG": "mjpeg",
          "V_MPEG2": "mpeg2video", "V_MPEG1": "mpeg1video", "V_THEORA": "theora", "V_PRORES": "prores",
          "V_UNCOMPRESSED": "rawvideo", "V_FFV1": "ffv1"}
_AVI_V = {"H264": "h264", "X264": "h264", "AVC1": "h264", "DAVC": "h264", "VSSH": "h264", "HEVC": "hevc",
          "H265": "hevc", "HVC1": "hevc", "XVID": "mpeg4", "DIVX": "mpeg4", "DX50": "mpeg4", "FMP4": "mpeg4",
          "MP4V": "mpeg4", "MJPG": "mjpeg", "AVRN": "mjpeg", "JPEG": "mjpeg", "VP80": "vp8", "VP90": "vp9",
          "AV01": "av1", "MPG2": "mpeg2video", "DIV3": "msmpeg4v3", "MP43": "msmpeg4v3", "WMV2": "wmv2",
          "CVID": "cinepak", "FFV1": "ffv1", "UYVY": "rawvideo"}
_H264_PROF = {66: "Baseline", 77: "Main", 88: "Extended", 100: "High", 110: "High 10", 122: "High 4:2:2",
              244: "High 4:4:4 Predictive", 44: "CAVLC 4:4:4"}
_HEVC_PROF = {1: "Main", 2: "Main 10", 3: "Main Still Picture", 4: "Rext", 9: "SCC"}
_AV1_PROF = {0: "Main", 1: "High", 2: "Professional"}
_PRORES = {b"apco": ("Proxy", "yuv422p10le"), b"apcs": ("LT", "yuv422p10le"), b"apcn": ("Standard", "yuv422p10le"),
           b"apch": ("HQ", "yuv422p10le"), b"ap4h": ("4444", "yuv444p10le"), b"ap4x": ("4444XQ", "yuv444p10le")}
_NON_MEDIA = (b"\x89PNG", b"\xff\xd8\xff", b"%PDF", b"PK\x03\x04", b"MZ", b"\x7fELF", b"\xd0\xcf\x11\xe0",
              b"GIF8", b"BM", b"{", b"<", b"\x1f\x8b", b"7z\xbc\xaf", b"Rar!")
_STD_RATES = [(n * 1000, 1001) for n in (24, 30, 48, 60, 120, 240)] + [(n, 1) for n in range(1, 241)]


def _pix(chroma, depth):
    """(chroma_format_idc 0..3, bit depth) -> ffprobe pix_fmt."""
    if chroma is None:
        return None
    base = {0: "gray", 1: "yuv420p", 2: "yuv422p", 3: "yuv444p"}.get(chroma)
    if base is None:
        return None
    depth = depth or 8
    if depth == 8:
        return base
    return ("gray%dle" % depth) if chroma == 0 else "%s%dle" % (base, depth)


def _ratio(num, den):
    if not num or not den:
        return None
    g = math.gcd(int(num), int(den))
    return "%d/%d" % (num // g, den // g)


def _snap(fps):
    if not fps or fps <= 0:
        return None
    for n, d in _STD_RATES:
        if abs(fps - n / d) < 1e-3 * (n / d):
            return "%d/%d" % (n, d)
    return None


# ---------------------------------------------------------------- bitstream helpers

class _Bits:
    def __init__(self, b):
        self.b, self.p = b, 0

    def u(self, n):
        v = 0
        for _ in range(n):
            if self.p >= len(self.b) * 8:
                raise ValueError("eof")
            v = (v << 1) | ((self.b[self.p >> 3] >> (7 - (self.p & 7))) & 1)
            self.p += 1
        return v

    def ue(self):
        z = 0
        while self.u(1) == 0:
            z += 1
            if z > 31:
                raise ValueError("ue")
        return (1 << z) - 1 + self.u(z)


def _rbsp(nal):
    return nal.replace(b"\x00\x00\x03", b"\x00\x00")


def _h264_sps(sps):
    """SPS NAL (with header byte) -> {profile, level, pix_fmt}."""
    if len(sps) < 4 or sps[0] & 0x1F != 7:
        return {}
    prof, cons, lvl = sps[1], sps[2], sps[3]
    name = _H264_PROF.get(prof)
    if prof == 66 and cons & 0x40:
        name = "Constrained Baseline"
    elif prof in (110, 122, 244) and cons & 0x10:
        name = name + " Intra"
    out = {"profile": name, "level": lvl, "pix_fmt": "yuv420p"}
    if prof in (100, 110, 122, 244, 44, 83, 86, 118, 128, 138, 139, 134, 135):
        try:
            r = _Bits(_rbsp(sps[4:]))
            r.ue()
            cf = r.ue()
            if cf == 3:
                r.u(1)
            depth = r.ue() + 8
            out["pix_fmt"] = _pix(cf, depth)
        except ValueError:
            pass
    return out


def _avcc(c):
    if len(c) < 7 or c[0] != 1:
        return {}
    n_sps, p = c[5] & 0x1F, 6
    out = {}
    if n_sps and p + 2 <= len(c):
        ln, = struct.unpack_from(">H", c, p)
        out = _h264_sps(c[p + 2:p + 2 + ln])
    for _ in range(n_sps):
        if p + 2 > len(c):
            return out
        p += 2 + struct.unpack_from(">H", c, p)[0]
    if p < len(c):
        n_pps = c[p]
        p += 1
        for _ in range(n_pps):
            if p + 2 > len(c):
                return out
            p += 2 + struct.unpack_from(">H", c, p)[0]
        if c[1] in (100, 110, 122, 144) and p + 3 <= len(c):   # avcC high-profile tail: chroma + bit depth
            out["pix_fmt"] = _pix(c[p] & 3, (c[p + 1] & 7) + 8)
    return out


def _hvcc(c):
    if len(c) < 23:
        return {}
    prof = c[1] & 0x1F
    return {"profile": _HEVC_PROF.get(prof), "level": c[12], "pix_fmt": _pix(c[16] & 3, (c[17] & 7) + 8)}


def _vpcc(c, full_box):
    """MP4 vpcC (FullBox: version/flags first) -> fields."""
    if full_box:
        c = c[4:]
    if len(c) < 3:
        return {}
    depth, ss = c[2] >> 4, (c[2] >> 1) & 7
    return {"profile": "Profile %d" % c[0], "level": c[1],
            "pix_fmt": _pix({0: 1, 1: 1, 2: 2, 3: 3}.get(ss), depth)}


def _vp9_mkv_private(c):
    """Matroska VP9 CodecPrivate: (id, len, value) features 1 profile, 2 level, 3 bit depth, 4 chroma subsampling."""
    f, p = {}, 0
    while p + 2 <= len(c):
        i, ln = c[p], c[p + 1]
        f[i] = int.from_bytes(c[p + 2:p + 2 + ln], "big")
        p += 2 + ln
    if 1 not in f:
        return {}
    out = {"profile": "Profile %d" % f[1]}
    if 2 in f:
        out["level"] = f[2]
    ss = f.get(4)
    out["pix_fmt"] = _pix({0: 1, 1: 1, 2: 2, 3: 3}.get(ss, 3 if ss is None and f[1] in (1, 3) else 1), f.get(3, 8))
    return out


def _vp9_frame(fr):
    """VP9 uncompressed frame header -> profile / pix_fmt (keyframe only)."""
    try:
        r = _Bits(fr[:16])
        if r.u(2) != 2:
            return {}
        lo, hi = r.u(1), r.u(1)
        prof = (hi << 1) | lo
        if prof == 3:
            r.u(1)
        if r.u(1):
            return {"profile": "Profile %d" % prof}
        if r.u(1) != 0:
            return {"profile": "Profile %d" % prof}
        r.u(2)
        if r.u(24) != 0x498342:
            return {}
        depth = 8
        if prof >= 2:
            depth = 12 if r.u(1) else 10
        cs = r.u(3)
        chroma = 1
        if cs != 7:
            r.u(1)
            if prof in (1, 3):
                sx, sy = r.u(1), r.u(1)
                chroma = 3 if (sx, sy) == (0, 0) else 2 if (sx, sy) == (1, 0) else 1
        else:
            chroma = 3
        return {"profile": "Profile %d" % prof, "pix_fmt": _pix(chroma, depth)}
    except ValueError:
        return {}


def _av1c(c):
    if len(c) < 4 or c[0] & 0x7F != 1:
        return {}
    prof, lvl, fl = c[1] >> 5, c[1] & 0x1F, c[2]
    hbd, twelve, mono, sx, sy = (fl >> 6) & 1, (fl >> 5) & 1, (fl >> 4) & 1, (fl >> 3) & 1, (fl >> 2) & 1
    depth = (12 if twelve else 10) if hbd else 8
    chroma = 0 if mono else 1 if (sx and sy) else 2 if sx else 3
    return {"profile": _AV1_PROF.get(prof), "level": lvl, "pix_fmt": _pix(chroma, depth)}


def _mpeg4_vos(b):
    """MPEG-4 Part 2 VOS start code 00 00 01 B0 <profile_and_level_indication> -> ffprobe profile name."""
    i = b.find(b"\x00\x00\x01\xb0")
    if i < 0 or i + 4 >= len(b):
        return {"pix_fmt": "yuv420p"}
    pl = b[i + 4]
    name = ("Simple Profile" if pl in (1, 2, 3, 4, 5, 6, 8) else "Advanced Simple Profile" if 0xF0 <= pl <= 0xF7
            else "Simple Scalable Profile" if pl in (0x10, 0x11, 0x12) else "Core Profile" if pl in (0x21, 0x22)
            else "Main Profile" if 0x32 <= pl <= 0x34 else None)
    return {"profile": name, "level": pl & 0x0F if name else None, "pix_fmt": "yuv420p"}


def _jpeg_pix(b):
    """First JPEG frame's SOF component sampling -> ffprobe yuvj* pix_fmt (MJPEG decodes to full-range yuvj)."""
    i = b.find(b"\xff\xd8\xff")
    if i < 0:
        return {}
    p = i + 2
    while p + 4 <= len(b):
        if b[p] != 0xFF:
            return {}
        m = b[p + 1]
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            p += 2
            continue
        ln, = struct.unpack_from(">H", b, p + 2)
        if m in (0xC0, 0xC1, 0xC2):
            depth, nc = b[p + 4], b[p + 9]
            if nc == 1:
                return {"pix_fmt": "gray", "profile": None}
            if nc != 3:
                return {}
            hs = [b[p + 11 + 3 * k] >> 4 for k in range(3)]
            vs = [b[p + 11 + 3 * k] & 15 for k in range(3)]
            if hs[1] != hs[2] or vs[1] != vs[2] or not hs[1] or not vs[1] or hs[0] % hs[1] or vs[0] % vs[1]:
                return {}
            ratio = (hs[0] // hs[1], vs[0] // vs[1])        # ffmpeg classifies by luma:chroma ratio (2x2/1x2 = 422)
            sub = {(1, 1): "444", (2, 1): "422", (2, 2): "420", (1, 2): "440", (4, 1): "411"}.get(ratio)
            prof = "Baseline" if m == 0xC0 else "Progressive" if m == 0xC2 else "Sequential"
            return {"pix_fmt": ("yuvj%sp" % sub) if sub and depth == 8 else None, "profile": prof}
        if m == 0xDA:
            return {}
        p += 2 + ln
    return {}


def _prores_pix(b, fourcc):
    """First ProRes frame header ('icpf' + hdr): frame_flags bits 7-6 = chroma (2 = 4:2:2, 3 = 4:4:4), byte 17 low
    nibble = alpha_info. ffmpeg's decoder: 4:2:2 -> yuv422p10le; 4:4:4 -> yuv444p10le, but 12-bit (and yuva with
    alpha) for the 4444 / 4444XQ fourccs. The fourcc alone lies when an encoder writes 4:4:4 frames under apcn."""
    i = b.find(b"icpf")
    if i < 4 or i + 4 + 18 > len(b):
        return None
    h = i + 4
    chroma, alpha = b[h + 12] >> 6, b[h + 17] & 0x0F
    if chroma == 2:
        return "yuv422p10le"
    if chroma == 3:
        if fourcc in (b"ap4h", b"ap4x"):
            return "yuva444p12le" if alpha else "yuv444p12le"
        return "yuva444p10le" if alpha else "yuv444p10le"
    return None


def _annexb_sps(b):
    i = 0
    while True:
        i = b.find(b"\x00\x00\x01", i)
        if i < 0 or i + 4 > len(b):
            return {}
        if b[i + 3] & 0x1F == 7:
            j = b.find(b"\x00\x00\x01", i + 3)
            return _h264_sps(b[i + 3:j if j > 0 else len(b)])
        i += 3


# ---------------------------------------------------------------- MP4 / MOV

def _boxes(b, s, e):
    while s + 8 <= e:
        sz, = struct.unpack_from(">I", b, s)
        typ, hl = b[s + 4:s + 8], 8
        if sz == 1 and s + 16 <= e:
            sz, hl = struct.unpack_from(">Q", b, s + 8)[0], 16
        elif sz == 0:
            sz = e - s
        if sz < hl or s + sz > e:
            return
        yield typ, s + hl, s + sz
        s += sz


def _child(b, s, e, typ):
    for t, cs, ce in _boxes(b, s, e):
        if t == typ:
            return cs, ce
    return None


def _path(b, s, e, *typs):
    r = (s, e)
    for t in typs:
        r = _child(b, r[0], r[1], t)
        if r is None:
            return None
    return r


def _fix(v):
    return struct.unpack(">i", struct.pack(">I", v))[0] / 65536.0


def _rot(a, b_):
    """ffprobe av_display_rotation_get: -(atan2(b, a) in degrees), printed as int."""
    if a == 0 and b_ == 0:
        return 0
    r = -math.degrees(math.atan2(b_, a))
    r = int(round(r))
    return 0 if r == 0 else r


def _mp4(b):
    if b[4:8] not in (b"ftyp", b"moov", b"mdat", b"free", b"wide", b"skip", b"pnot"):
        return None
    moov = None
    for t, s, e in _boxes(b, 0, len(b)):
        if t == b"moov":
            moov = (s, e)
    if moov is None:
        return None
    vids = []
    for t, ts, te in _boxes(b, *moov):
        if t != b"trak":
            continue
        md = _child(b, ts, te, b"mdia")
        hd = md and _child(b, md[0], md[1], b"hdlr")
        if not hd or b[hd[0] + 8:hd[0] + 12] != b"vide":
            continue
        st = {"rotation": 0}
        tk = _child(b, ts, te, b"tkhd")
        if tk:
            mo = tk[0] + (52 if b[tk[0]] == 1 else 40)
            if mo + 36 <= tk[1]:
                m = struct.unpack_from(">9I", b, mo)
                st["rotation"] = _rot(_fix(m[0]), _fix(m[1]))
        scale = 0
        h = _child(b, md[0], md[1], b"mdhd")
        if h:
            scale, = struct.unpack_from(">I", b, h[0] + (20 if b[h[0]] == 1 else 12))
        stbl = _path(b, md[0], md[1], b"minf", b"stbl")
        if stbl:
            tt = _child(b, stbl[0], stbl[1], b"stts")
            if tt and tt[0] + 8 <= tt[1]:
                n, = struct.unpack_from(">I", b, tt[0] + 4)
                ents = [struct.unpack_from(">II", b, tt[0] + 8 + 8 * k) for k in range(min(n, 4096))
                        if tt[0] + 16 + 8 * k <= tt[1]]
                tot = sum(c for c, _ in ents)
                if ents:
                    best = max(ents, key=lambda x: x[0])[1]
                    st["frame_rate"] = _ratio(scale, best) if best else None
                    st["nb_frames"] = tot
            sz = _child(b, stbl[0], stbl[1], b"stsz")
            if sz and sz[0] + 12 <= sz[1]:
                st["nb_frames"] = struct.unpack_from(">I", b, sz[0] + 8)[0]
            sd = _child(b, stbl[0], stbl[1], b"stsd")
            if sd and sd[0] + 16 <= sd[1]:
                es = sd[0] + 8
                esz, = struct.unpack_from(">I", b, es)
                fourcc, ee = b[es + 4:es + 8], min(es + esz, sd[1])
                st["tag"] = fourcc
                st["codec_name"] = _MP4_V.get(fourcc) or (fourcc.decode("latin-1").strip().lower()
                                                          if fourcc.isalnum() else None)
                if es + 36 <= ee:
                    st["width"], st["height"] = struct.unpack_from(">HH", b, es + 32)
                kids = {}
                if es + 86 <= ee:
                    for kt, ks, ke in _boxes(b, es + 86, ee):
                        kids.setdefault(kt, b[ks:ke])
                if fourcc in (b"avc1", b"avc3") and b"avcC" in kids:
                    st.update({k: v for k, v in _avcc(kids[b"avcC"]).items() if v is not None})
                elif b"hvcC" in kids:
                    st.update({k: v for k, v in _hvcc(kids[b"hvcC"]).items() if v is not None})
                elif b"vpcC" in kids:
                    st.update({k: v for k, v in _vpcc(kids[b"vpcC"], True).items() if v is not None})
                elif b"av1C" in kids:
                    st.update({k: v for k, v in _av1c(kids[b"av1C"]).items() if v is not None})
                elif fourcc == b"mp4v" and b"esds" in kids:
                    st.update({k: v for k, v in _mpeg4_vos(kids[b"esds"]).items() if v is not None})
                elif fourcc in _PRORES:
                    st["profile"], st["pix_fmt"] = _PRORES[fourcc]
                    st["pix_fmt"] = _prores_pix(b, fourcc) or st["pix_fmt"]
                elif st["codec_name"] == "mjpeg":
                    st["pix_fmt"] = "yuvj420p"
        vids.append(st)
    return vids


# ---------------------------------------------------------------- Matroska / WebM

def _vint(b, i, strip):
    if i >= len(b):
        raise ValueError("eof")
    c, n = b[i], 1
    while n <= 8 and not c & (0x80 >> (n - 1)):
        n += 1
    if n > 8 or i + n > len(b):
        raise ValueError("vint")
    v = c & ((0x80 >> (n - 1)) - 1) if strip else c
    for k in range(1, n):
        v = (v << 8) | b[i + k]
    if strip and v == (1 << (7 * n)) - 1:
        v = -1                                          # unknown size
    return v, i + n


def _ebml(b, s, e):
    while s < e:
        eid, p = _vint(b, s, False)
        sz, p = _vint(b, p, True)
        end = e if sz < 0 else min(p + sz, e)
        yield eid, p, end
        s = end


def _mkv(b):
    if b[:4] != b"\x1a\x45\xdf\xa3":
        return None
    vids, first_block = [], {}
    for eid, s, e in _ebml(b, 0, len(b)):
        if eid != 0x18538067:
            continue
        for sid, ss, se in _ebml(b, s, e):
            if sid == 0x1654AE6B:
                for tid, ts, te in _ebml(b, ss, se):
                    if tid != 0xAE:
                        continue
                    t = {"rotation": 0, "tag": b"\0\0\0\0"}
                    ttype = num = None
                    for fid, fs, fe in _ebml(b, ts, te):
                        if fid == 0x83:
                            ttype = int.from_bytes(b[fs:fe], "big")
                        elif fid == 0xD7:
                            num = int.from_bytes(b[fs:fe], "big")
                        elif fid == 0x86:
                            t["cid"] = b[fs:fe].rstrip(b"\0").decode("latin-1")
                        elif fid == 0x63A2:
                            t["priv"] = b[fs:fe]
                        elif fid == 0x23E383:
                            dd = int.from_bytes(b[fs:fe], "big")
                            if dd:
                                fps = 1e9 / dd
                                t["frame_rate"] = _snap(fps) or _ratio(int(round(fps * 1000)), 1000)
                        elif fid == 0xE0:
                            for vid, vs, ve in _ebml(b, fs, fe):
                                if vid == 0xB0:
                                    t["width"] = int.from_bytes(b[vs:ve], "big")
                                elif vid == 0xBA:
                                    t["height"] = int.from_bytes(b[vs:ve], "big")
                                elif vid == 0x7670:
                                    for pid, ps, pe in _ebml(b, vs, ve):
                                        if pid == 0x7675 and pe - ps in (4, 8):
                                            roll = struct.unpack(">f" if pe - ps == 4 else ">d", b[ps:pe])[0]
                                            t["rotation"] = int(round(-roll)) or 0
                    if ttype == 1:
                        t["num"] = num
                        t["codec_name"] = _MKV_V.get(t.get("cid", ""), (t.get("cid") or "").lower() or None)
                        if t["codec_name"] == "mpeg4" and t.get("priv"):
                            t["tag"] = None
                        vids.append(t)
            elif sid == 0x1F43B675 and vids and not first_block:
                for cid, cs, ce in _ebml(b, ss, se):
                    blk = None
                    if cid == 0xA3:
                        blk = (cs, ce)
                    elif cid == 0xA0:
                        for gid, gs, ge in _ebml(b, cs, ce):
                            if gid == 0xA1:
                                blk = (gs, ge)
                    if blk:
                        tn, p = _vint(b, blk[0], True)
                        first_block.setdefault(tn, b[p + 3:blk[1]])
                    if len(first_block) >= 4:
                        break
    for t in vids:
        priv, c = t.pop("priv", b""), t["codec_name"]
        fb = first_block.get(t.pop("num", None), b"")
        extra = {}
        if c == "h264":
            extra = _avcc(priv) if priv else _annexb_sps(fb)
        elif c == "hevc" and priv:
            extra = _hvcc(priv)
        elif c == "vp9":
            extra = _vp9_mkv_private(priv) if priv else {}
            if not extra.get("pix_fmt"):
                extra = dict(_vp9_frame(fb), **{k: v for k, v in extra.items() if v is not None})
        elif c == "av1" and priv:
            extra = _av1c(priv)
        elif c == "mpeg4":
            extra = _mpeg4_vos(priv or fb)
        elif c == "mjpeg":
            extra = _jpeg_pix(fb)
        elif c == "vp8":
            extra = {"pix_fmt": "yuv420p"}
        t.update({k: v for k, v in extra.items() if v is not None})
        t.pop("cid", None)
    return vids


# ---------------------------------------------------------------- AVI

def _riff(b, s, e):
    while s + 8 <= e:
        cid = b[s:s + 4]
        sz, = struct.unpack_from("<I", b, s + 4)
        end = min(s + 8 + sz, e)
        yield cid, s + 8, end
        s = s + 8 + sz + (sz & 1)


def _avi(b):
    if b[:4] != b"RIFF" or b[8:12] != b"AVI ":
        return None
    vids, movi, idx = [], None, 0
    for cid, s, e in _riff(b, 12, len(b)):
        if cid == b"LIST" and b[s:s + 4] == b"hdrl":
            for hid, hs, he in _riff(b, s + 4, e):
                if hid != b"LIST" or b[hs:hs + 4] != b"strl":
                    continue
                strh = strf = None
                for kid, ks, ke in _riff(b, hs + 4, he):
                    if kid == b"strh":
                        strh = b[ks:ke]
                    elif kid == b"strf":
                        strf = b[ks:ke]
                if strh and strh[:4] == b"vids" and len(strh) >= 36:
                    scale, rate = struct.unpack_from("<II", strh, 20)
                    length, = struct.unpack_from("<I", strh, 32)
                    t = {"rotation": 0, "frame_rate": _ratio(rate, scale), "nb_frames": length, "idx": idx}
                    tag = strh[4:8]
                    if strf and len(strf) >= 20:
                        w, h = struct.unpack_from("<ii", strf, 4)
                        t["width"], t["height"] = w, abs(h)
                        if strf[16:20] != b"\0\0\0\0":
                            tag = strf[16:20]
                        if len(strf) > 40:
                            t["priv"] = strf[40:]
                    t["tag"] = tag
                    t["codec_name"] = _AVI_V.get(tag.decode("latin-1").upper().strip(),
                                                 "rawvideo" if tag in (b"\0\0\0\0", b"DIB ", b"RGB ") else
                                                 tag.decode("latin-1").strip().lower() or None)
                    vids.append(t)
                if strh:
                    idx += 1
        elif cid == b"LIST" and b[s:s + 4] == b"movi":
            movi = (s + 4, e)
    for t in vids:
        fr, priv = b"", t.pop("priv", b"")
        if movi:
            want = b"%02d" % t.pop("idx")
            for kid, ks, ke in _riff(b, *movi):
                if kid == b"LIST":
                    for k2, s2, e2 in _riff(b, ks + 4, ke):
                        if k2[:2] == want and k2[2:] in (b"dc", b"db") and e2 > s2:
                            fr = b[s2:e2]
                            break
                elif kid[:2] == want and kid[2:] in (b"dc", b"db") and ke > ks:
                    fr = b[ks:ke]
                if fr:
                    break
        t.pop("idx", None)
        c, extra = t["codec_name"], {}
        if c == "h264":
            extra = _annexb_sps(priv + fr)
        elif c == "mpeg4":
            extra = _mpeg4_vos(priv + fr)
        elif c == "mjpeg":
            extra = _jpeg_pix(fr)
        t.update({k: v for k, v in extra.items() if v is not None})
    return vids


# ---------------------------------------------------------------- dispatch

def video_streams(data):
    """[{codec_name, width, height, frame_rate, pix_fmt, profile, level, rotation, tag, nb_frames}] (all video
    streams, container order) or None when the bytes are not a parsable MP4/MOV, Matroska/WebM or AVI."""
    b = bytes(data)
    for fn in (_mp4, _mkv, _avi):
        try:
            r = fn(b)
        except (ValueError, IndexError, struct.error, OverflowError, UnicodeDecodeError):
            r = None
        if r is not None:
            return r
    return None


def _kind(field):
    f = field
    for p in ("primary_video_stream_", "primary_video_", "first_video_", "video_stream_", "video_"):
        if f.startswith(p):
            f = f[len(p):]
            break
    if f in ("width", "height", "rotation", "rotate", "level", "profile", "pix_fmt", "nb_frames"):
        return f
    return {"dimensions_pixels": "dims", "dimensions": "dims", "resolution": "dims", "frame_rate": "frame_rate",
            "r_frame_rate": "frame_rate", "avg_frame_rate": "frame_rate", "pixel_format": "pix_fmt",
            "codec_profile": "profile", "display_matrix_rotation": "rotation", "displaymatrix_rotation": "rotation",
            "rotate_tag": "rotate", "codec_tag_string": "tag_string", "fourcc": "tag_string",
            "codec_tag": "tag_hex", "codec_tag_hex": "tag_hex", "frame_count": "nb_frames",
            "codec_name": "codec_name", "count": "count"}.get(f)


def video_value(data, ctx):
    if not data:
        return None
    k = _kind((ctx or {}).get("field") or "")
    if k is None:
        return None
    vs = video_streams(data)
    if vs is None:
        head = bytes(data[:512])
        text = all(32 <= c < 127 or c in (9, 10, 13) for c in head)
        return "none" if head.startswith(_NON_MEDIA) or text else None
    if k == "count":
        return len(vs)
    if not vs:
        return "none"
    v = vs[0]
    if k == "dims":
        return Dims(v["width"], v["height"]) if v.get("width") and v.get("height") else None
    if k == "rotate":
        r = v.get("rotation")
        return None if r is None else (-r) % 360
    if k == "tag_string":
        t = v.get("tag")
        if t is None:
            return None
        return "".join(chr(c) if 32 < c < 127 else "[%d]" % c for c in t)
    if k == "tag_hex":
        t = v.get("tag")
        return None if t is None else "0x%08x" % int.from_bytes(t, "little")
    r = v.get(k)
    return r if r is not None else None
