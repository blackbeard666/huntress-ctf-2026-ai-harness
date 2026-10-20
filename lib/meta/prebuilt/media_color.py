"""`media` primary VIDEO stream colour / timing fields (aliases `video`, `av`, `mp4`, `mov`) -- prebuilt, SPECULATIVE.

MP4/MOV only (the first `vide` trak). Spelling follows ffprobe -show_streams (libavformat mov.c + the h264 decoder that
ffprobe's find_stream_info opens), cross-checked against PyAV 19 / ffmpeg 7.0.2 on the fixtures:
  - color_range / color_space / color_transfer / color_primaries: av_color_*_name() ("tv"/"pc", "bt709", "smpte170m",
    "bt2020nc", "smpte2084", "arib-std-b67", ...). The H.264 SPS VUI wins when it signals the value
    (video_signal_type_present -> range; colour_description_present -> primaries/transfer/matrix), otherwise the
    stsd `colr` nclx/nclc box (nclx full_range bit -> pc/tv; nclc has no range). Unspecified (2 / 0) -> "none": ffprobe
    -print_format json omits these optional fields (the default writer prints "unknown").
  - field_order: stsd `fiel` box (1 -> progressive; 2 + 0x01 tt / 0x06 bb / 0x09 tb / 0x0e bt), else H.264
    frame_mbs_only_flag=1 -> "progressive", else "tt" (best effort: x264 --tff; a bff stream decodes to "bb").
  - has_b_frames: H.264 avctx->has_b_frames at decoder open = SPS VUI bitstream_restriction max_num_reorder_frames
    (PyAV codec_context.reorder_depth); without bitstream_restriction: 0 for (Constrained) Baseline / no ctts, else 2.
  - avg_frame_rate: mov.c timescale * stts sample count / sum(stts count*delta), reduced ("100/81" for VFR, D18 "10/1").
  - is_variable_frame_rate (not an ffprobe field; mediainfo FrameRate_Mode VFR): stts has >1 distinct delta, ignoring a
    final single-sample entry. frame_rate_mode -> "VFR"/"CFR".
  - start_time: "%.6f" seconds = empty-edit time (mvhd timescale) + (min composition time - first elst media_time) /
    mdhd timescale, floored at 0 (ffprobe "0.000000" for an ffmpeg mux with B-frames: elst media_time = ctts shift).
  - primary_video_duration: "%.6f" of mdhd duration / mdhd timescale (ffprobe stream duration); duration_ts = raw int.
  - primary_video_bit_rate: ffprobe stream bit_rate = sum(stsz) * 8 * timescale // mdhd duration (TRUNCATED: VFR
    fixture 2505.68 -> 2505 in both PyAV and mediainfo).
  - nb_frames: stsz sample_count (D18 video-001.mp4 = 5).
Non-MP4 / no video trak -> "none" for audio-only or obvious non-media; unparsable -> None."""
import math
import struct

from .media_video import _Bits, _boxes, _child, _path, _rbsp, _se

FIELDS = {
    ("media", "color_range"): "color_value",
    ("media", "primary_video_color_range"): "color_value",
    ("media", "video_color_range"): "color_value",
    ("media", "video_stream_color_range"): "color_value",
    ("media", "color_space"): "color_value",
    ("media", "primary_video_color_space"): "color_value",
    ("media", "video_color_space"): "color_value",
    ("media", "video_stream_color_space"): "color_value",
    ("media", "colorspace"): "color_value",
    ("media", "primary_video_colorspace"): "color_value",
    ("media", "color_matrix"): "color_value",
    ("media", "primary_video_color_matrix"): "color_value",
    ("media", "matrix_coefficients"): "color_value",
    ("media", "primary_video_matrix_coefficients"): "color_value",
    ("media", "color_transfer"): "color_value",
    ("media", "primary_video_color_transfer"): "color_value",
    ("media", "video_color_transfer"): "color_value",
    ("media", "video_stream_color_transfer"): "color_value",
    ("media", "color_trc"): "color_value",
    ("media", "primary_video_color_trc"): "color_value",
    ("media", "transfer_characteristics"): "color_value",
    ("media", "primary_video_transfer_characteristics"): "color_value",
    ("media", "color_primaries"): "color_value",
    ("media", "primary_video_color_primaries"): "color_value",
    ("media", "video_color_primaries"): "color_value",
    ("media", "video_stream_color_primaries"): "color_value",
    ("media", "field_order"): "color_value",
    ("media", "primary_video_field_order"): "color_value",
    ("media", "video_field_order"): "color_value",
    ("media", "video_stream_field_order"): "color_value",
    ("media", "has_b_frames"): "color_value",
    ("media", "primary_video_has_b_frames"): "color_value",
    ("media", "video_has_b_frames"): "color_value",
    ("media", "video_stream_has_b_frames"): "color_value",
    ("media", "avg_frame_rate"): "color_value",
    ("media", "video_avg_frame_rate"): "color_value",
    ("media", "video_stream_avg_frame_rate"): "color_value",
    ("media", "is_variable_frame_rate"): "color_value",
    ("media", "primary_video_is_variable_frame_rate"): "color_value",
    ("media", "video_is_variable_frame_rate"): "color_value",
    ("media", "variable_frame_rate"): "color_value",
    ("media", "primary_video_variable_frame_rate"): "color_value",
    ("media", "is_vfr"): "color_value",
    ("media", "primary_video_is_vfr"): "color_value",
    ("media", "frame_rate_mode"): "color_value",
    ("media", "primary_video_frame_rate_mode"): "color_value",
    ("media", "start_time"): "color_value",
    ("media", "primary_video_start_time"): "color_value",
    ("media", "video_start_time"): "color_value",
    ("media", "video_stream_start_time"): "color_value",
    ("media", "primary_video_duration"): "color_value",
    ("media", "primary_video_duration_seconds"): "color_value",
    ("media", "video_duration"): "color_value",
    ("media", "video_duration_seconds"): "color_value",
    ("media", "video_stream_duration"): "color_value",
    ("media", "primary_video_duration_ts"): "color_value",
    ("media", "video_duration_ts"): "color_value",
    ("media", "primary_video_bit_rate"): "color_value",
    ("media", "primary_video_bitrate"): "color_value",
    ("media", "video_bit_rate"): "color_value",
    ("media", "video_bitrate"): "color_value",
    ("media", "video_stream_bit_rate"): "color_value",
    ("media", "nb_frames"): "color_value",
    ("media", "video_stream_nb_frames"): "color_value",
    ("video", "color_range"): "color_value",
    ("video", "primary_video_color_range"): "color_value",
    ("video", "color_space"): "color_value",
    ("video", "primary_video_color_space"): "color_value",
    ("video", "color_transfer"): "color_value",
    ("video", "primary_video_color_transfer"): "color_value",
    ("video", "color_primaries"): "color_value",
    ("video", "primary_video_color_primaries"): "color_value",
    ("video", "field_order"): "color_value",
    ("video", "primary_video_field_order"): "color_value",
    ("video", "has_b_frames"): "color_value",
    ("video", "primary_video_has_b_frames"): "color_value",
    ("video", "avg_frame_rate"): "color_value",
    ("video", "primary_video_avg_frame_rate"): "color_value",
    ("video", "is_variable_frame_rate"): "color_value",
    ("video", "primary_video_is_variable_frame_rate"): "color_value",
    ("video", "start_time"): "color_value",
    ("video", "primary_video_start_time"): "color_value",
    ("video", "primary_video_duration"): "color_value",
    ("video", "primary_video_bit_rate"): "color_value",
    ("video", "nb_frames"): "color_value",
    ("video", "primary_video_nb_frames"): "color_value",
    ("av", "color_range"): "color_value",
    ("av", "primary_video_color_range"): "color_value",
    ("av", "color_space"): "color_value",
    ("av", "primary_video_color_space"): "color_value",
    ("av", "color_transfer"): "color_value",
    ("av", "primary_video_color_transfer"): "color_value",
    ("av", "color_primaries"): "color_value",
    ("av", "primary_video_color_primaries"): "color_value",
    ("av", "field_order"): "color_value",
    ("av", "primary_video_field_order"): "color_value",
    ("av", "has_b_frames"): "color_value",
    ("av", "primary_video_has_b_frames"): "color_value",
    ("av", "primary_video_avg_frame_rate"): "color_value",
    ("av", "primary_video_is_variable_frame_rate"): "color_value",
    ("av", "primary_video_start_time"): "color_value",
    ("av", "primary_video_duration"): "color_value",
    ("av", "primary_video_bit_rate"): "color_value",
    ("av", "primary_video_nb_frames"): "color_value",
    ("mp4", "color_range"): "color_value",
    ("mp4", "color_space"): "color_value",
    ("mp4", "color_transfer"): "color_value",
    ("mp4", "color_primaries"): "color_value",
    ("mp4", "field_order"): "color_value",
    ("mp4", "has_b_frames"): "color_value",
    ("mp4", "primary_video_avg_frame_rate"): "color_value",
    ("mp4", "primary_video_start_time"): "color_value",
    ("mp4", "primary_video_duration"): "color_value",
    ("mp4", "primary_video_bit_rate"): "color_value",
    ("mp4", "primary_video_nb_frames"): "color_value",
    ("mov", "color_range"): "color_value",
    ("mov", "color_space"): "color_value",
    ("mov", "color_transfer"): "color_value",
    ("mov", "color_primaries"): "color_value",
    ("mov", "field_order"): "color_value",
}

# av_color_*_name() (libavutil/pixdesc.c); 2 = unspecified -> absent
_PRI = {1: "bt709", 4: "bt470m", 5: "bt470bg", 6: "smpte170m", 7: "smpte240m", 8: "film", 9: "bt2020",
        10: "smpte428", 11: "smpte431", 12: "smpte432", 22: "jedec-p22"}
_TRC = {1: "bt709", 4: "gamma22", 5: "gamma28", 6: "smpte170m", 7: "smpte240m", 8: "linear", 9: "log100",
        10: "log316", 11: "iec61966-2-4", 12: "bt1361e", 13: "iec61966-2-1", 14: "bt2020-10", 15: "bt2020-12",
        16: "smpte2084", 17: "smpte428", 18: "arib-std-b67"}
_SPC = {0: "gbr", 1: "bt709", 4: "fcc", 5: "bt470bg", 6: "smpte170m", 7: "smpte240m", 8: "ycgco", 9: "bt2020nc",
        10: "bt2020c", 11: "smpte2085", 12: "chroma-derived-nc", 13: "chroma-derived-c", 14: "ictcp"}
_FIEL = {1: "tt", 6: "bb", 9: "tb", 14: "bt"}
_NON_MEDIA = (b"\x89PNG", b"\xff\xd8\xff", b"%PDF", b"PK\x03\x04", b"MZ", b"\x7fELF", b"\xd0\xcf\x11\xe0",
              b"GIF8", b"BM", b"{", b"<", b"\x1f\x8b", b"7z\xbc\xaf", b"Rar!", b"RIFF", b"ID3", b"fLaC", b"OggS",
              b"\x1a\x45\xdf\xa3")


def _hrd(r):
    cnt = r.ue() + 1
    r.u(8)
    for _ in range(min(cnt, 32)):
        r.ue()
        r.ue()
        r.u(1)
    r.u(20)


def _h264_vui(sps):
    """SPS NAL (with header) -> {profile, frame_mbs_only, full_range, pri, trc, spc, reorder} (VUI keys only when
    signalled)."""
    if len(sps) < 4 or sps[0] & 0x1F != 7:
        return {}
    prof = sps[1]
    out = {"profile": prof, "constrained": bool(sps[2] & 0x40)}
    r = _Bits(_rbsp(sps[4:]))
    r.ue()
    if prof in (100, 110, 122, 244, 44, 83, 86, 118, 128, 138, 139, 134, 135):
        cf = r.ue()
        if cf == 3:
            r.u(1)
        r.ue()
        r.ue()
        r.u(1)
        if r.u(1):
            for i in range(8 if cf != 3 else 12):
                if r.u(1):
                    last = nxt = 8
                    for _ in range(16 if i < 6 else 64):
                        if nxt:
                            nxt = (last + _se(r) + 256) % 256
                        last = nxt or last
    r.ue()
    poc = r.ue()
    if poc == 0:
        r.ue()
    elif poc == 1:
        r.u(1)
        _se(r)
        _se(r)
        for _ in range(min(r.ue(), 255)):
            _se(r)
    r.ue()
    r.u(1)
    r.ue()
    r.ue()
    fmo = r.u(1)
    out["frame_mbs_only"] = fmo
    if not fmo:
        r.u(1)
    r.u(1)
    if r.u(1):
        r.ue()
        r.ue()
        r.ue()
        r.ue()
    try:
        if not r.u(1):                                   # vui_parameters_present_flag
            return out
        if r.u(1) and r.u(8) == 255:                     # aspect_ratio_info
            r.u(32)
        if r.u(1):                                       # overscan_info_present
            r.u(1)
        if r.u(1):                                       # video_signal_type_present
            r.u(3)
            out["full_range"] = r.u(1)
            if r.u(1):
                out["pri"], out["trc"], out["spc"] = r.u(8), r.u(8), r.u(8)
        if r.u(1):                                       # chroma_loc_info
            r.ue()
            r.ue()
        if r.u(1):                                       # timing_info
            r.u(65)
        nal, vcl = r.u(1), None
        if nal:
            _hrd(r)
        vcl = r.u(1)
        if vcl:
            _hrd(r)
        if nal or vcl:
            r.u(1)
        r.u(1)                                           # pic_struct_present
        if r.u(1):                                       # bitstream_restriction
            r.u(1)
            for _ in range(4):
                r.ue()
            out["reorder"] = r.ue()
    except ValueError:
        pass
    return out


def _avcc_sps(c):
    if len(c) < 8 or c[0] != 1 or not c[5] & 0x1F:
        return b""
    ln, = struct.unpack_from(">H", c, 6)
    return c[8:8 + ln]


def _u32s(b, s, n, e):
    n = min(n, max(0, (e - s) // 4))
    return struct.unpack_from(">%dI" % n, b, s) if n else ()


def _video_trak(b):
    if b[4:8] not in (b"ftyp", b"moov", b"mdat", b"free", b"wide", b"skip", b"pnot"):
        return None
    moov = None
    for t, s, e in _boxes(b, 0, len(b)):
        if t == b"moov":
            moov = (s, e)
    if moov is None:
        return None
    mvts = 0
    mv = _child(b, moov[0], moov[1], b"mvhd")
    if mv:
        mvts, = struct.unpack_from(">I", b, mv[0] + (20 if b[mv[0]] == 1 else 12))
    for t, ts, te in _boxes(b, *moov):
        if t != b"trak":
            continue
        md = _child(b, ts, te, b"mdia")
        hd = md and _child(b, md[0], md[1], b"hdlr")
        if not hd or b[hd[0] + 8:hd[0] + 12] != b"vide":
            continue
        st = {"mvts": mvts}
        h = _child(b, md[0], md[1], b"mdhd")
        if h:
            if b[h[0]] == 1:
                st["ts"], st["dur"] = struct.unpack_from(">IQ", b, h[0] + 20)
            else:
                st["ts"], st["dur"] = struct.unpack_from(">II", b, h[0] + 12)
        el = _path(b, ts, te, b"edts", b"elst")
        if el:
            v, = struct.unpack_from(">B", b, el[0])
            n, = struct.unpack_from(">I", b, el[0] + 4)
            ents, p = [], el[0] + 8
            for _ in range(min(n, 64)):
                if v == 1 and p + 20 <= el[1]:
                    sd, mt = struct.unpack_from(">Qq", b, p)
                    p += 20
                elif v != 1 and p + 12 <= el[1]:
                    sd, mt = struct.unpack_from(">Ii", b, p)
                    p += 12
                else:
                    break
                ents.append((sd, mt))
            st["elst"] = ents
        stbl = _path(b, md[0], md[1], b"minf", b"stbl")
        if not stbl:
            return st
        tt = _child(b, stbl[0], stbl[1], b"stts")
        if tt and tt[0] + 8 <= tt[1]:
            n, = struct.unpack_from(">I", b, tt[0] + 4)
            raw = _u32s(b, tt[0] + 8, 2 * min(n, 1 << 20), tt[1])
            st["stts"] = list(zip(raw[0::2], raw[1::2]))
        ct = _child(b, stbl[0], stbl[1], b"ctts")
        if ct and ct[0] + 8 <= ct[1]:
            v = b[ct[0]]
            n, = struct.unpack_from(">I", b, ct[0] + 4)
            raw = _u32s(b, ct[0] + 8, 2 * min(n, 1 << 20), ct[1])
            st["ctts"] = [(c, (o - (1 << 32) if v == 1 and o & 0x80000000 else o)) for c, o in zip(raw[0::2], raw[1::2])]
        sz = _child(b, stbl[0], stbl[1], b"stsz")
        if sz and sz[0] + 12 <= sz[1]:
            fixed, n = struct.unpack_from(">II", b, sz[0] + 4)
            st["nb_frames"] = n
            st["data_size"] = fixed * n if fixed else sum(_u32s(b, sz[0] + 12, n, sz[1]))
        sd = _child(b, stbl[0], stbl[1], b"stsd")
        if sd and sd[0] + 16 <= sd[1]:
            es = sd[0] + 8
            esz, = struct.unpack_from(">I", b, es)
            st["fourcc"], ee = b[es + 4:es + 8], min(es + esz, sd[1])
            kids = {}
            if es + 86 <= ee:
                for kt, ks, ke in _boxes(b, es + 86, ee):
                    kids.setdefault(kt, b[ks:ke])
            st["kids"] = kids
        return st
    return []


def _color(st):
    k = st.get("kids") or {}
    out = {}
    c = k.get(b"colr")
    if c and len(c) >= 10 and c[:4] in (b"nclx", b"nclc"):
        out["pri"], out["trc"], out["spc"] = struct.unpack_from(">HHH", c, 4)
        if c[:4] == b"nclx" and len(c) >= 11:
            out["full_range"] = c[10] >> 7
    if b"avcC" in k:
        try:
            v = _h264_vui(_avcc_sps(k[b"avcC"]))
        except (ValueError, IndexError):
            v = {}
        for key in ("pri", "trc", "spc", "full_range"):
            if key in v:
                out[key] = v[key]
    return out


def _field_order(st):
    f = (st.get("kids") or {}).get(b"fiel")
    if f and len(f) >= 2:
        if f[0] == 1:
            return "progressive"
        if f[0] == 2 and f[1] in _FIEL:
            return _FIEL[f[1]]
    if b"avcC" in (st.get("kids") or {}):
        v = _h264_vui(_avcc_sps(st["kids"][b"avcC"]))
        if "frame_mbs_only" in v:
            return "progressive" if v["frame_mbs_only"] else "tt"
    return None


def _has_b(st):
    k = st.get("kids") or {}
    if b"avcC" not in k:
        return None
    v = _h264_vui(_avcc_sps(k[b"avcC"]))
    if not v:
        return None
    if "reorder" in v:
        return v["reorder"]
    if v.get("profile") == 66 or not st.get("ctts"):
        return 0
    return 2


def _start_time(st):
    ts = st.get("ts")
    if not ts:
        return None
    empty, mt = 0, 0
    for sd, m in st.get("elst") or []:
        if m == -1:
            empty += sd
        else:
            mt = m
            break
    stts, ctts = st.get("stts") or [], st.get("ctts") or []
    minpts, dts, i = None, 0, 0
    offs = iter([o for c, o in ctts for _ in range(min(c, 1 << 16))]) if ctts else None
    for c, d in stts:
        for _ in range(min(c, 1 << 16)):
            pts = dts + (next(offs, 0) if offs else 0)
            minpts = pts if minpts is None else min(minpts, pts)
            dts += d
            i += 1
            if i > 200000:
                break
    minpts = minpts or 0
    sec = (empty / st["mvts"] if st.get("mvts") else 0) + max(0, minpts - mt) / ts
    return "%.6f" % sec


def _vfr(st):
    ents = [e for e in st.get("stts") or [] if e[0]]
    if len(ents) > 1 and ents[-1][0] == 1:
        ents = ents[:-1]
    return len({d for _, d in ents}) > 1


def _base(field):
    f = field
    for p in ("primary_video_stream_", "primary_video_", "video_stream_", "video_"):
        if f.startswith(p):
            return f[len(p):]
    return f


def color_value(data, ctx):
    if not data:
        return None
    k = _base((ctx or {}).get("field") or "")
    b = bytes(data)
    try:
        st = _video_trak(b)
    except (ValueError, IndexError, struct.error, OverflowError):
        return None
    if st is None:
        head = b[:512]
        text = all(32 <= c < 127 or c in (9, 10, 13) for c in head)
        return "none" if head.startswith(_NON_MEDIA) or text else None
    if st == []:
        return "none"                                    # MP4 without a video track (audio-only m4a)
    try:
        if k in ("color_range", "color_space", "colorspace", "color_matrix", "matrix_coefficients", "color_transfer",
                 "color_trc", "transfer_characteristics", "color_primaries"):
            c = _color(st)
            if k == "color_range":
                fr = c.get("full_range")
                return "none" if fr is None else ("pc" if fr else "tv")
            if k == "color_primaries":
                return _PRI.get(c.get("pri"), "none")
            if k in ("color_transfer", "color_trc", "transfer_characteristics"):
                return _TRC.get(c.get("trc"), "none")
            return _SPC.get(c.get("spc"), "none")
        if k == "field_order":
            return _field_order(st)
        if k == "has_b_frames":
            return _has_b(st)
        if k == "avg_frame_rate":
            stts = st.get("stts") or []
            n, tot = sum(c for c, _ in stts), sum(c * d for c, d in stts)
            if not n or not tot or not st.get("ts"):
                return "0/0"
            num, den = st["ts"] * n, tot
            g = math.gcd(num, den)
            return "%d/%d" % (num // g, den // g)
        if k in ("is_variable_frame_rate", "variable_frame_rate", "is_vfr"):
            return _vfr(st) if st.get("stts") else None
        if k == "frame_rate_mode":
            return ("VFR" if _vfr(st) else "CFR") if st.get("stts") else None
        if k == "start_time":
            return _start_time(st)
        if k in ("duration", "duration_seconds"):
            return "%.6f" % (st["dur"] / st["ts"]) if st.get("ts") and "dur" in st else None
        if k == "duration_ts":
            return st.get("dur")
        if k in ("bit_rate", "bitrate"):
            if not st.get("dur") or "data_size" not in st:
                return None
            return st["data_size"] * 8 * st["ts"] // st["dur"]
        if k == "nb_frames":
            return st.get("nb_frames")
    except (ValueError, IndexError, struct.error, OverflowError, ZeroDivisionError):
        return None
    return None
