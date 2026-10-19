"""`media` per-stream fields of multi-stream containers (aliases `audio`, `av`) -- prebuilt, SPECULATIVE.

D17 flavor: "find the stream that breaks the sender's story" -- a container with several tracks where one track's codec /
language / sample rate / creation time disagrees with the rest. Every list is in CONTAINER STREAM INDEX ORDER (ffprobe
`streams[].index`): MP4 = moov/trak order, Matroska = Tracks/TrackEntry order, Ogg = order of the BOS pages.
  - MP4/MOV: moov/trak/{tkhd, mdia/{mdhd, hdlr, minf/stbl/stsd}, udta/name}. mdhd creation_time is seconds since
    1904-01-01 UTC (ffprobe stream tag creation_time, from mdhd); mdhd language is the packed ISO-639-2 code (ffmpeg
    ff_mov_lang_to_iso639: >= 0x400 packed, 0 = Mac code "eng", 0x7fff = unspecified -> "und").
  - Matroska/WebM: EBML Segment/Tracks/TrackEntry (TrackType 1 video, 2 audio, 0x11 subtitle); CodecID -> ffprobe
    codec_name; Language absent -> "eng" (Matroska spec default; ffmpeg matroskadec), stored "und" kept as "und";
    Name = title; per-track DURATION from Segment/Tags (ffmpeg muxer), else Info Duration.
  - Ogg: pages grouped by serial; BOS packet names the codec, the comment packet gives LANGUAGE / TITLE.
Timestamps render "%Y-%m-%dT%H:%M:%SZ"; durations ffprobe "%f" strings. A non-media member -> "none"; unreadable -> None.
odd_stream_index: within each codec_type group of >= 3 streams (then all streams, for type-free attributes), the
single stream whose codec / language / sample_rate / creation_time / channels differs from a strict majority;
attributes vote in that priority order. odd_stream_diagnostic emits the JSON evidence."""
import struct
from datetime import datetime, timedelta, timezone

FIELDS = {
    ("media", "stream_codec_names"): "codec_names",
    ("media", "streams_codec_names"): "codec_names",
    ("media", "stream_codecs"): "codec_names",
    ("media", "codec_names"): "codec_names",
    ("media", "track_codec_names"): "codec_names",
    ("media", "audio_stream_codec_names"): "codec_names",
    ("media", "audio_codec_names"): "codec_names",
    ("media", "audio_track_codec_names"): "codec_names",
    ("media", "video_stream_codec_names"): "codec_names",
    ("media", "video_codec_names"): "codec_names",
    ("media", "stream_codec_types"): "codec_types",
    ("media", "stream_types"): "codec_types",
    ("media", "codec_types"): "codec_types",
    ("media", "track_types"): "codec_types",
    ("media", "primary_video_codec_name"): "video_codec",
    ("media", "primary_video_codec"): "video_codec",
    ("media", "video_codec_name"): "video_codec",
    ("media", "video_codec"): "video_codec",
    ("media", "first_video_codec_name"): "video_codec",
    ("media", "video_stream_codec_name"): "video_codec",
    ("media", "video_stream_count"): "video_count",
    ("media", "nb_video_streams"): "video_count",
    ("media", "number_of_video_streams"): "video_count",
    ("media", "stream_languages"): "languages",
    ("media", "stream_language_codes"): "languages",
    ("media", "track_languages"): "languages",
    ("media", "languages"): "languages",
    ("media", "audio_stream_languages"): "languages",
    ("media", "audio_languages"): "languages",
    ("media", "audio_track_languages"): "languages",
    ("media", "stream_titles"): "titles",
    ("media", "stream_names"): "titles",
    ("media", "track_names"): "titles",
    ("media", "track_titles"): "titles",
    ("media", "audio_stream_titles"): "titles",
    ("media", "audio_track_names"): "titles",
    ("media", "stream_handler_names"): "handler_names",
    ("media", "handler_names"): "handler_names",
    ("media", "track_handler_names"): "handler_names",
    ("media", "stream_creation_times_utc"): "creation_times",
    ("media", "stream_creation_times"): "creation_times",
    ("media", "track_creation_times_utc"): "creation_times",
    ("media", "track_creation_times"): "creation_times",
    ("media", "mdhd_creation_times_utc"): "creation_times",
    ("media", "audio_stream_creation_times_utc"): "creation_times",
    ("media", "stream_durations_seconds"): "durations",
    ("media", "stream_durations"): "durations",
    ("media", "track_durations_seconds"): "durations",
    ("media", "audio_stream_durations_seconds"): "durations",
    ("media", "stream_sample_rates"): "sample_rates",
    ("media", "stream_sample_rates_hz"): "sample_rates",
    ("media", "audio_stream_sample_rates"): "sample_rates",
    ("media", "audio_sample_rates"): "sample_rates",
    ("media", "track_sample_rates"): "sample_rates",
    ("media", "stream_channels"): "channel_counts",
    ("media", "audio_stream_channels"): "channel_counts",
    ("media", "audio_stream_channel_counts"): "channel_counts",
    ("media", "odd_stream_index"): "odd_stream",
    ("media", "odd_audio_stream_index"): "odd_stream",
    ("media", "odd_stream"): "odd_stream",
    ("media", "odd_one_out_stream_index"): "odd_stream",
    ("media", "anomalous_stream_index"): "odd_stream",
    ("media", "outlier_stream_index"): "odd_stream",
    ("media", "mismatched_stream_index"): "odd_stream",
    ("media", "inconsistent_stream_index"): "odd_stream",
    ("media", "odd_stream_diagnostic"): "odd_stream",
    ("media", "odd_stream_codec_name"): "odd_stream",
    ("media", "odd_stream_language"): "odd_stream",
    ("media", "odd_stream_sample_rate"): "odd_stream",
    ("media", "odd_stream_creation_time_utc"): "odd_stream",
    ("media", "odd_stream_title"): "odd_stream",
    ("av", "stream_codec_names"): "codec_names",
    ("av", "audio_stream_codec_names"): "codec_names",
    ("av", "video_stream_codec_names"): "codec_names",
    ("av", "stream_codec_types"): "codec_types",
    ("av", "primary_video_codec_name"): "video_codec",
    ("av", "video_codec_name"): "video_codec",
    ("av", "video_stream_count"): "video_count",
    ("av", "stream_languages"): "languages",
    ("av", "audio_stream_languages"): "languages",
    ("av", "stream_titles"): "titles",
    ("av", "stream_handler_names"): "handler_names",
    ("av", "stream_creation_times_utc"): "creation_times",
    ("av", "stream_durations_seconds"): "durations",
    ("av", "stream_sample_rates"): "sample_rates",
    ("av", "audio_stream_sample_rates"): "sample_rates",
    ("av", "odd_stream_index"): "odd_stream",
    ("av", "odd_stream_diagnostic"): "odd_stream",
    ("audio", "stream_codec_names"): "codec_names",
    ("audio", "audio_stream_codec_names"): "codec_names",
    ("audio", "stream_languages"): "languages",
    ("audio", "audio_stream_languages"): "languages",
    ("audio", "stream_titles"): "titles",
    ("audio", "stream_creation_times_utc"): "creation_times",
    ("audio", "stream_durations_seconds"): "durations",
    ("audio", "stream_sample_rates"): "sample_rates",
    ("audio", "audio_stream_sample_rates"): "sample_rates",
    ("audio", "odd_stream_index"): "odd_stream",
    ("audio", "odd_stream_diagnostic"): "odd_stream",
}

# ---------------------------------------------------------------- MP4 / MOV

_MP4_CODECS = {b"avc1": "h264", b"avc3": "h264", b"hvc1": "hevc", b"hev1": "hevc", b"mp4v": "mpeg4",
               b"vp08": "vp8", b"vp09": "vp9", b"av01": "av1", b"jpeg": "mjpeg", b"mjpa": "mjpeg",
               b"s263": "h263", b"apcn": "prores", b"apch": "prores", b"apcs": "prores", b"apco": "prores",
               b"Opus": "opus", b"fLaC": "flac", b"ac-3": "ac3", b"ec-3": "eac3", b"alac": "alac",
               b"sowt": "pcm_s16le", b"twos": "pcm_s16be", b"ulaw": "pcm_mulaw", b"alaw": "pcm_alaw",
               b"samr": "amr_nb", b"sawb": "amr_wb", b".mp3": "mp3", b"dtsc": "dts", b"mha1": "mpegh_3d_audio",
               b"tx3g": "mov_text", b"text": "mov_text", b"wvtt": "webvtt", b"stpp": "ttml",
               b"c608": "eia_608", b"tmcd": "none"}
_MP4_TYPES = {b"vide": "video", b"soun": "audio", b"subt": "subtitle", b"sbtl": "subtitle", b"text": "subtitle",
              b"clcp": "subtitle", b"tmcd": "data", b"meta": "data", b"hint": "data"}
_ESDS_OTI = {0x40: "aac", 0x66: "aac", 0x67: "aac", 0x68: "aac", 0x69: "mp3", 0x6B: "mp3", 0xA5: "ac3",
             0xA6: "eac3", 0xA9: "dts", 0xDD: "vorbis", 0xAD: "opus", 0x20: "mpeg4", 0x21: "h264",
             0x60: "mpeg2video", 0x61: "mpeg2video", 0x6A: "mpeg1video", 0x6C: "mjpeg"}
_MAC_LANG = ["eng", "fra", "ger", "ita", "dut", "swe", "spa", "dan", "por", "nor", "heb", "jpn", "ara", "fin",
             "gre", "ice", "mlt", "tur", "hr ", "chi", "urd", "hin", "tha", "kor", "lit", "pol", "hun", "est",
             "lav", "", "fo ", "", "rus", "chi"]
_EPOCH_1904 = datetime(1904, 1, 1, tzinfo=timezone.utc)


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


def _mp4_lang(code):
    if code >= 0x400 and code != 0x7FFF:
        return "".join(chr(0x60 + ((code >> sh) & 0x1F)) for sh in (10, 5, 0))
    if code < len(_MAC_LANG) and _MAC_LANG[code]:
        return _MAC_LANG[code].strip()
    return "und"


def _esds_oti(b, s, e):
    """objectTypeIndication of the esds DecoderConfigDescriptor (tag 4), or None."""
    r = _child(b, s, e, b"esds")
    if r is None:
        return None
    i, end = r[0] + 4, r[1]
    while i < end:
        tag = b[i]
        i += 1
        ln = 0
        for _ in range(4):
            c = b[i]
            i += 1
            ln = ln << 7 | (c & 0x7F)
            if not c & 0x80:
                break
        if tag == 3:
            fl = b[i + 2]
            i += 3 + (2 if fl & 0x80 else 0) + ((1 + b[i + 3]) if fl & 0x40 else 0) + (2 if fl & 0x20 else 0)
            continue
        if tag == 4:
            return b[i]
        i += ln
    return None


def _mp4_streams(b):
    if b[4:8] not in (b"ftyp", b"moov", b"mdat", b"free", b"wide", b"skip", b"pnot"):
        return None
    moov = None
    for t, s, e in _boxes(b, 0, len(b)):
        if t == b"moov":
            moov = (s, e)
    if moov is None:
        return None
    out, mvscale = [], 0
    mh = _child(b, moov[0], moov[1], b"mvhd")
    if mh:
        mvscale, = struct.unpack_from(">I", b, mh[0] + (20 if b[mh[0]] == 1 else 12))
    for t, ts, te in _boxes(b, *moov):
        if t != b"trak":
            continue
        st = {"codec_type": None, "codec_name": None, "language": "und", "title": None, "handler_name": None}
        md = _child(b, ts, te, b"mdia")
        if md:
            h = _child(b, md[0], md[1], b"mdhd")
            if h:
                v = b[h[0]]
                if v == 1:
                    ct, _mt, scale, dur = struct.unpack_from(">QQIQ", b, h[0] + 4)
                    lang, = struct.unpack_from(">H", b, h[0] + 32)
                else:
                    ct, _mt, scale, dur = struct.unpack_from(">IIII", b, h[0] + 4)
                    lang, = struct.unpack_from(">H", b, h[0] + 20)
                st["language"] = _mp4_lang(lang)
                st["timescale"] = scale
                if ct:
                    st["creation_time"] = (_EPOCH_1904 + timedelta(seconds=ct)).strftime("%Y-%m-%dT%H:%M:%SZ")
                if scale and dur not in (0, 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF):
                    st["duration"] = "%.6f" % (dur / scale)
            hd = _child(b, md[0], md[1], b"hdlr")
            htype = None
            if hd:
                htype = b[hd[0] + 8:hd[0] + 12]
                st["codec_type"] = _MP4_TYPES.get(htype, "data")
                nm = b[hd[0] + 24:hd[1]]
                if nm[:1] and nm[0] and nm[0] == len(nm.rstrip(b"\0")) - 1:
                    nm = nm[1:]                                    # QuickTime pascal string
                nm = nm.split(b"\0")[0].decode("utf-8", "replace").strip()
                st["handler_name"] = nm or None
            sd = _path(b, md[0], md[1], b"minf", b"stbl", b"stsd")
            if sd and sd[0] + 16 <= sd[1]:
                es = sd[0] + 8
                esz, = struct.unpack_from(">I", b, es)
                fourcc, ee = b[es + 4:es + 8], min(es + esz, sd[1])
                codec = _MP4_CODECS.get(fourcc)
                if htype == b"soun" and es + 36 <= ee:
                    ver, = struct.unpack_from(">H", b, es + 16)
                    ch, bits = struct.unpack_from(">HH", b, es + 24)
                    rate = struct.unpack_from(">I", b, es + 32)[0] >> 16
                    kids = es + 36 + {1: 16, 2: 36}.get(ver, 0)
                    if ver == 2 and es + 56 <= ee:
                        rate = int(struct.unpack_from(">d", b, es + 40)[0])
                        ch, = struct.unpack_from(">I", b, es + 48)
                    if fourcc in (b"Opus",):
                        rate = 48000
                    if not rate:
                        rate = st.get("timescale")
                    st["sample_rate"], st["channels"] = rate, ch
                    if fourcc in (b"mp4a", b"enca"):
                        codec = _ESDS_OTI.get(_esds_oti(b, kids, ee), "aac" if fourcc == b"mp4a" else None)
                    elif fourcc in (b"lpcm", b"in24", b"in32", b"fl32", b"fl64", b"raw "):
                        codec = {b"in24": "pcm_s24be", b"in32": "pcm_s32be", b"fl32": "pcm_f32be",
                                 b"fl64": "pcm_f64be", b"raw ": "pcm_u8"}.get(fourcc)
                elif fourcc in (b"mp4v", b"encv") and es + 86 <= ee:
                    codec = _ESDS_OTI.get(_esds_oti(b, es + 86, ee), "mpeg4")
                if codec is None and fourcc.isalnum():
                    codec = fourcc.decode("latin-1").strip().lower()
                st["codec_name"] = codec
        el = _path(b, ts, te, b"edts", b"elst")
        if el and mvscale and el[0] + 8 <= el[1]:      # edit list: ffprobe's stream duration is the presented span
            v, n = b[el[0]], struct.unpack_from(">I", b, el[0] + 4)[0]
            w = 20 if v == 1 else 12
            segs = [struct.unpack_from(">Qq" if v == 1 else ">Ii", b, el[0] + 8 + k * w) for k in range(n)
                    if el[0] + 8 + (k + 1) * w <= el[1]]
            tot = sum(d for d, mt in segs if mt != -1)
            if tot:
                st["duration"] = "%.6f" % (tot / mvscale)
        ud = _child(b, ts, te, b"udta")
        if ud:
            nm = _child(b, ud[0], ud[1], b"name")
            if nm:
                st["title"] = b[nm[0]:nm[1]].split(b"\0")[0].decode("utf-8", "replace").strip() or None
        out.append(st)
    return out


# ---------------------------------------------------------------- Matroska / WebM

_MKV_CODECS = {"A_OPUS": "opus", "A_VORBIS": "vorbis", "A_AAC": "aac", "A_FLAC": "flac", "A_MPEG/L3": "mp3",
               "A_MPEG/L2": "mp2", "A_MPEG/L1": "mp1", "A_AC3": "ac3", "A_EAC3": "eac3", "A_DTS": "dts",
               "A_TRUEHD": "truehd", "A_ALAC": "alac", "A_TTA1": "tta", "A_WAVPACK4": "wavpack",
               "V_MPEG4/ISO/AVC": "h264", "V_MPEGH/ISO/HEVC": "hevc", "V_VP8": "vp8", "V_VP9": "vp9",
               "V_AV1": "av1", "V_MPEG4/ISO/ASP": "mpeg4", "V_MPEG4/ISO/SP": "mpeg4", "V_MPEG4/ISO/AP": "mpeg4",
               "V_MPEG2": "mpeg2video", "V_MPEG1": "mpeg1video", "V_MJPEG": "mjpeg", "V_THEORA": "theora",
               "V_PRORES": "prores", "V_FFV1": "ffv1", "S_TEXT/UTF8": "subrip", "S_TEXT/ASS": "ass",
               "S_TEXT/SSA": "ass", "S_ASS": "ass", "S_SSA": "ass", "S_TEXT/WEBVTT": "webvtt",
               "S_HDMV/PGS": "hdmv_pgs_subtitle", "S_VOBSUB": "dvd_subtitle", "S_DVBSUB": "dvb_subtitle"}
_MKV_TYPES = {1: "video", 2: "audio", 3: "video", 0x10: "video", 0x11: "subtitle", 0x12: "subtitle",
              0x20: "data"}


def _vint(b, i, strip):
    c = b[i]
    n = 1
    while n <= 8 and not c & (0x80 >> (n - 1)):
        n += 1
    if n > 8 or i + n > len(b):
        raise ValueError("vint")
    v = c & ((0xFF >> n) if strip else 0xFF)
    for k in range(1, n):
        v = v << 8 | b[i + k]
    unknown = strip and v == (1 << (7 * n)) - 1
    return v, i + n, unknown


def _ebml(b, s, e):
    while s < e:
        eid, i, _ = _vint(b, s, False)
        ln, i, unk = _vint(b, i, True)
        end = e if unk else min(i + ln, e)
        yield eid, i, end, unk
        s = end


def _uint(b, s, e):
    return int.from_bytes(b[s:e], "big") if e > s else 0


def _float(b, s, e):
    return struct.unpack(">f" if e - s == 4 else ">d", b[s:e])[0] if e - s in (4, 8) else 0.0


def _str(b, s, e):
    return b[s:e].split(b"\0")[0].decode("utf-8", "replace").strip()


def _mkv_codec(cid, bits):
    if cid in _MKV_CODECS:
        return _MKV_CODECS[cid]
    if cid.startswith("A_AAC"):
        return "aac"
    if cid == "A_PCM/INT/LIT":
        return "pcm_u8" if bits == 8 else "pcm_s%dle" % (bits or 16)
    if cid == "A_PCM/INT/BIG":
        return "pcm_s8" if bits == 8 else "pcm_s%dbe" % (bits or 16)
    if cid == "A_PCM/FLOAT/IEEE":
        return "pcm_f%dle" % (bits or 32)
    if cid.startswith("A_REAL/") or cid.startswith("V_REAL/"):
        return cid[7:].lower()
    return None


def _hms(t):
    try:
        h, m, s = t.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    except ValueError:
        return None


def _mkv_streams(b):
    if b[:4] != b"\x1a\x45\xdf\xa3":
        return None
    out, tags, info = [], {}, {}
    for eid, s, e, _ in _ebml(b, 0, len(b)):
        if eid != 0x18538067:
            continue
        for cid, cs, ce, cunk in _ebml(b, s, e):
            if cid == 0x1549A966:
                for iid, is_, ie, _ in _ebml(b, cs, ce):
                    if iid == 0x2AD7B1:
                        info["scale"] = _uint(b, is_, ie)
                    elif iid == 0x4489:
                        info["dur"] = _float(b, is_, ie)
            elif cid == 0x1654AE6B:
                for tid, ts, te, _ in _ebml(b, cs, ce):
                    if tid != 0xAE:
                        continue
                    st = {"language": "eng", "title": None, "codec_type": None, "codec_name": None}
                    cidstr, bits = "", 0
                    for k, ks, ke, _ in _ebml(b, ts, te):
                        if k == 0x83:
                            st["codec_type"] = _MKV_TYPES.get(_uint(b, ks, ke), "data")
                        elif k == 0x86:
                            cidstr = _str(b, ks, ke)
                        elif k == 0x73C5:
                            st["uid"] = _uint(b, ks, ke)
                        elif k == 0x536E:
                            st["title"] = _str(b, ks, ke) or None
                        elif k == 0x22B59C and "bcp47" not in st:
                            st["language"] = _str(b, ks, ke) or "eng"
                        elif k == 0x22B59D:
                            st["language"] = st["bcp47"] = _str(b, ks, ke) or "und"
                        elif k == 0xE1:
                            rate, orate, ch = 8000.0, None, 1
                            for a, as_, ae, _ in _ebml(b, ks, ke):
                                if a == 0xB5:
                                    rate = _float(b, as_, ae)
                                elif a == 0x78B5:
                                    orate = _float(b, as_, ae)
                                elif a == 0x9F:
                                    ch = _uint(b, as_, ae)
                                elif a == 0x6264:
                                    bits = _uint(b, as_, ae)
                            st["sample_rate"], st["channels"] = int(orate or rate), ch
                    st.pop("bcp47", None)
                    st["codec_name"] = _mkv_codec(cidstr, bits)
                    if st["codec_type"] == "audio" and cidstr == "A_OPUS":
                        st["sample_rate"] = 48000
                    out.append(st)
            elif cid == 0x1254C367:
                for gid, gs, ge, _ in _ebml(b, cs, ce):
                    if gid != 0x7373:
                        continue
                    uids, simple = [], {}
                    for k, ks, ke, _ in _ebml(b, gs, ge):
                        if k == 0x63C0:
                            uids += [_uint(b, x, y) for t2, x, y, _ in _ebml(b, ks, ke) if t2 == 0x63C5]
                        elif k == 0x67C8:
                            nm = val = None
                            for t2, x, y, _ in _ebml(b, ks, ke):
                                if t2 == 0x45A3:
                                    nm = _str(b, x, y).upper()
                                elif t2 == 0x4487:
                                    val = _str(b, x, y)
                            if nm:
                                simple[nm] = val
                    for u in uids:
                        tags.setdefault(u, {}).update(simple)
            if cunk:
                break
        break
    if not out:
        return None
    segdur = None
    if info.get("dur"):
        segdur = info["dur"] * (info.get("scale") or 1000000) / 1e9
    for st in out:
        tg = tags.get(st.get("uid"), {})
        d = _hms(tg["DURATION"]) if tg.get("DURATION") else segdur
        if d is not None:
            st["duration"] = "%.6f" % d
        if tg.get("CREATION_TIME"):
            st["creation_time"] = tg["CREATION_TIME"]
    return out


# ---------------------------------------------------------------- Ogg

def _ogg_packets(b):
    """{serial: [packets...]} (first 3 packets per stream), BOS-ordered serial list, last granule per serial."""
    pk, order, gran, cur = {}, [], {}, {}
    i = b.find(b"OggS")
    while 0 <= i and i + 27 <= len(b):
        if b[i:i + 4] != b"OggS":
            i = b.find(b"OggS", i + 1)
            continue
        htype, g, serial = b[i + 5], struct.unpack_from("<q", b, i + 6)[0], struct.unpack_from("<I", b, i + 14)[0]
        nseg = b[i + 26]
        lace = b[i + 27:i + 27 + nseg]
        p = i + 27 + nseg
        if htype & 2 and serial not in pk:
            order.append(serial)
            pk[serial], cur[serial] = [], b""
        if serial in pk:
            if g != -1:
                gran[serial] = g
            for L in lace:
                if len(pk[serial]) < 3:
                    cur[serial] += b[p:p + L]
                p += L
                if L < 255 and len(pk[serial]) < 3:
                    pk[serial].append(cur[serial])
                    cur[serial] = b""
            i = p
        else:
            i += 27 + nseg + sum(lace)
    return pk, order, gran


def _vcomments(c):
    out = {}
    try:
        vl, = struct.unpack_from("<I", c, 0)
        o = 4 + vl
        n, = struct.unpack_from("<I", c, o)
        o += 4
        for _ in range(min(n, 1000)):
            ln, = struct.unpack_from("<I", c, o)
            k, _, v = c[o + 4:o + 4 + ln].decode("utf-8", "replace").partition("=")
            out.setdefault(k.upper(), v.strip())
            o += 4 + ln
    except struct.error:
        pass
    return out


def _ogg_streams(b):
    if b[:4] != b"OggS":
        return None
    pk, order, gran = _ogg_packets(b)
    out = []
    for s in order:
        ps = pk[s]
        h = ps[0] if ps else b""
        st = {"codec_type": "audio", "codec_name": None, "language": "und", "title": None}
        com, rate, skip = None, None, 0
        if h[:8] == b"OpusHead":
            st["codec_name"], rate, st["channels"] = "opus", 48000, h[9]
            skip = struct.unpack_from("<H", h, 10)[0]
            com = ps[1][8:] if len(ps) > 1 and ps[1][:8] == b"OpusTags" else None
        elif h[:7] == b"\x01vorbis":
            st["codec_name"], st["channels"], rate = "vorbis", h[11], struct.unpack_from("<I", h, 12)[0]
            com = ps[1][7:] if len(ps) > 1 and ps[1][:7] == b"\x03vorbis" else None
        elif h[:5] == b"\x7fFLAC" and len(h) >= 30:
            si = h[17:]
            rate = int.from_bytes(si[10:13], "big") >> 4
            st["codec_name"], st["channels"] = "flac", ((si[12] >> 1) & 7) + 1
            com = ps[1][4:] if len(ps) > 1 and ps[1][:1] and ps[1][0] & 0x7F == 4 else None
        elif h[:8] == b"Speex   ":
            st["codec_name"], rate = "speex", struct.unpack_from("<I", h, 36)[0]
            com = ps[1] if len(ps) > 1 else None
        elif h[:7] == b"\x80theora":
            st["codec_type"], st["codec_name"] = "video", "theora"
            com = ps[1][7:] if len(ps) > 1 and ps[1][:7] == b"\x81theora" else None
        elif h[:5] == b"OVP80":
            st["codec_type"], st["codec_name"] = "video", "vp8"
        elif h[:8] == b"fishead\0":
            continue                                   # Skeleton: ffmpeg exposes no codec for it
        else:
            st["codec_type"] = "data"
        if st["codec_type"] == "audio" and rate:
            st["sample_rate"] = rate
            if s in gran and gran[s] >= 0:
                st["duration"] = "%.6f" % (max(gran[s] - skip, 0) / rate)
        if com:
            c = _vcomments(com)
            st["language"] = c.get("LANGUAGE") or "und"
            st["title"] = c.get("TITLE") or None
        out.append(st)
    return out or None


# ---------------------------------------------------------------- shared

_NON_MEDIA = (b"\x89PNG", b"\xff\xd8\xff", b"%PDF", b"PK\x03\x04", b"MZ", b"\x7fELF", b"\xd0\xcf\x11\xe0",
              b"GIF8", b"BM", b"{", b"<", b"\x1f\x8b", b"7z\xbc\xaf", b"Rar!")


def streams(data):
    """[{codec_type, codec_name, language, title, sample_rate?, channels?, creation_time?, duration?}] or None."""
    b = bytes(data)
    for fn in (_mp4_streams, _mkv_streams, _ogg_streams):
        try:
            r = fn(b)
        except (ValueError, IndexError, struct.error, OverflowError):
            r = None
        if r:
            return r
    return None


def _get(data, ctx):
    """(streams filtered by the field's audio_/video_ prefix, field) | "none" | None."""
    if not data:
        return None, ""
    f = (ctx or {}).get("field") or ""
    ss = streams(data)
    if ss is None:
        b = bytes(data[:512])
        text = all(32 <= c < 127 or c in (9, 10, 13) for c in b)
        return ("none" if b.startswith(_NON_MEDIA) or text else None), f
    if f.startswith("audio_"):
        ss = [s for s in ss if s["codec_type"] == "audio"]
    elif f.startswith("video_"):
        ss = [s for s in ss if s["codec_type"] == "video"]
    return ss, f


def _col(data, ctx, key):
    ss, f = _get(data, ctx)
    if ss is None or ss == "none":
        return ss
    return [s.get(key) for s in ss]


def codec_names(data, ctx):
    return _col(data, ctx, "codec_name")


def codec_types(data, ctx):
    return _col(data, ctx, "codec_type")


def languages(data, ctx):
    return _col(data, ctx, "language")


def handler_names(data, ctx):
    return _col(data, ctx, "handler_name")


def titles(data, ctx):
    """MKV Name / Ogg TITLE / MP4 trak udta `name`, falling back to the MP4 hdlr name (ffprobe handler_name)."""
    ss, f = _get(data, ctx)
    if ss is None or ss == "none":
        return ss
    return [s.get("title") or s.get("handler_name") for s in ss]


def creation_times(data, ctx):
    v = _col(data, ctx, "creation_time")
    return None if isinstance(v, list) and not any(v) else v


def durations(data, ctx):
    v = _col(data, ctx, "duration")
    return None if isinstance(v, list) and not any(v) else v


def sample_rates(data, ctx):
    """Sample rates of the AUDIO streams (stream order); video/subtitle streams carry none."""
    ss, f = _get(data, ctx)
    if ss is None or ss == "none":
        return ss
    return [s.get("sample_rate") for s in ss if s["codec_type"] == "audio"]


def channel_counts(data, ctx):
    ss, f = _get(data, ctx)
    if ss is None or ss == "none":
        return ss
    return [s.get("channels") for s in ss if s["codec_type"] == "audio"]


def _still_or_audio(data):
    """(video streams list) for a still image (ffprobe: one video stream), [] for audio-only media, else None."""
    from .media_video import _audio_only, _still
    b = bytes(data)
    try:
        st = _still(b)
    except (ValueError, IndexError, struct.error, OverflowError):
        st = None
    if st:
        return st
    return [] if _audio_only(b) else None


def video_codec(data, ctx):
    ss, f = _get(data, ctx)
    if ss is None or ss == "none":
        alt = _still_or_audio(data) if data else None
        if alt is not None:
            return alt[0]["codec_name"] if alt else "none"
        return ss
    v = [s["codec_name"] for s in ss if s["codec_type"] == "video"]
    return (v[0] or None) if v else "none"


def video_count(data, ctx):
    ss, f = _get(data, ctx)
    if ss is None or ss == "none":
        alt = _still_or_audio(data) if data else None
        return len(alt) if alt is not None else ss
    return sum(s["codec_type"] == "video" for s in ss)


_ATTRS = ("codec_name", "language", "sample_rate", "creation_time", "channels")


def find_odd(ss):
    """[{index, attribute, value, majority, codec_type}] -- every (group, attribute) with exactly one dissenter."""
    hits = []
    groups = {}
    for i, s in enumerate(ss):
        groups.setdefault(s["codec_type"], []).append(i)
    pools = [(t, ix) for t, ix in groups.items() if len(ix) >= 3]
    if len(ss) >= 3:
        pools.append((None, list(range(len(ss)))))
    for t, ix in pools:
        for a in _ATTRS if t else ("language", "creation_time"):
            vals = [ss[i].get(a) for i in ix]
            if any(v is None for v in vals):
                continue
            cnt = {}
            for v in vals:
                cnt[v] = cnt.get(v, 0) + 1
            if len(cnt) != 2:
                continue
            (maj, mc), (mino, nc) = sorted(cnt.items(), key=lambda kv: -kv[1])
            i = ix[vals.index(mino)]
            if nc == 1 and mc >= 2 and not any(h["index"] == i and h["attribute"] == a for h in hits):
                hits.append({"index": i, "attribute": a, "value": mino, "majority": maj,
                             "codec_type": ss[i]["codec_type"]})
    return hits


def odd_stream(data, ctx):
    """The container stream index of the stream that disagrees with the majority (see module doc), or "none"."""
    ss, f = _get(data, ctx)
    if ss is None or ss == "none":
        return ss
    hits = find_odd(ss)
    if f.endswith("_diagnostic"):
        return {"odd_stream_index": hits[0]["index"] if hits else None, "evidence": hits}
    if not hits:
        return "none"
    i = hits[0]["index"]
    if f == "odd_stream_codec_name":
        return ss[i]["codec_name"]
    if f == "odd_stream_language":
        return ss[i]["language"]
    if f == "odd_stream_sample_rate":
        return ss[i].get("sample_rate")
    if f == "odd_stream_creation_time_utc":
        return ss[i].get("creation_time")
    if f == "odd_stream_title":
        return ss[i].get("title") or ss[i].get("handler_name")
    return i
