"""Codec-level audio parameters -- AAC profile + MPEG audio (MP3) frame / Xing / LAME fields. Prebuilt, SPECULATIVE.

primary_audio_profile (ffprobe `profile` spelling of the first audio stream): the AAC Audio Object Type from the MP4
esds DecoderSpecificInfo (AudioSpecificConfig, ISO 14496-3 1.6.2.1: aot 5 bits [31 -> 32 + 6 bits], sfi 4 [15 -> 24-bit
rate], channel config 4; aot 5/29 = explicit SBR/PS, then ext sfi + the base aot; a GASpecificConfig followed by the
0x2b7 sync extension may signal SBR (0x548 -> PS) backward-compatibly -- libfdk_aac's MP4 default; an ext sfi equal to
the core sfi is NOT SBR, as in ffmpeg's mpeg4audio.c. Caveat: ffprobe's profile comes from the DECODER, so a
sync-extension SBR flag over a stream with no SBR payload still probes `LC` (checked with a patched ffmpeg file)), the ADTS header (profile 2 bits = aot - 1), or a
Matroska A_AAC CodecPrivate (legacy ids A_AAC/MPEG4/LC/SBR etc.). ffprobe names (libavcodec profiles.c):
1 Main, 2 LC, 3 SSR, 4 LTP, 5 HE-AAC, 29 HE-AACv2, 23 LD, 39 ELD, 42 xHE-AAC. Implicit SBR (only discoverable by
decoding fill elements) stays LC. A recognised non-AAC audio file (mp3/flac/ogg/wav/...) -> "none" (ffprobe -of json
omits `profile` there); unrecognised bytes -> None.
MPEG audio (ISO 11172-3 / 13818-3 header: sync 11 bits, version 2 [3 = 1, 2 = 2, 0 = 2.5], layer 2 [1 = III],
bitrate idx 4, sfi 2, padding 1, ..., channel mode 2), after any ID3v2 tag(s); the first header must be followed by a
second valid header (junk/ADTS/decoy rejection: ADTS has layer bits 00):
  mp3_mpeg_version  "1" / "2" / "2.5" (exiftool MPEGAudioVersion spelling)      mp3_layer      1 / 2 / 3
  mp3_bitrate_kbps  bitrate of the FIRST frame header (= the Xing/Info frame when present; exiftool MPEG:AudioBitrate)
  mp3_vbr_header    "Xing" / "Info" / "VBRI" / "none" (Xing/Info at side-info offset 4+{17,32,9,17}; VBRI at 4+32)
  mp3_lame_encoder  the 9-byte encoder string after the Xing/Info TOC+quality (`LAME3.100`; ffmpeg writes `Lavc62.11`)
  mp3_frame_count   the Xing/Info/VBRI frames field when present (LAME/ffmpeg: audio frames, tag frame excluded), else
                    the scanned frame count; mp3_scanned_frame_count = scan, tag frame excluded.
A non-MPEG-audio input -> "none"."""

FIELDS = {
    ("media", "primary_audio_profile"): "aac_value", ("media", "audio_profile"): "aac_value",
    ("media", "audio_codec_profile"): "aac_value", ("media", "primary_audio_codec_profile"): "aac_value",
    ("media", "aac_profile"): "aac_value", ("media", "aac_audio_object_type"): "aac_value",
    ("media", "aac_object_type"): "aac_value", ("media", "audio_object_type"): "aac_value",
    ("audio", "primary_audio_profile"): "aac_value", ("audio", "audio_profile"): "aac_value",
    ("audio", "audio_codec_profile"): "aac_value", ("audio", "primary_audio_codec_profile"): "aac_value",
    ("audio", "aac_profile"): "aac_value", ("audio", "aac_audio_object_type"): "aac_value",
    ("av", "primary_audio_profile"): "aac_value", ("av", "audio_profile"): "aac_value",
    ("av", "audio_codec_profile"): "aac_value", ("av", "primary_audio_codec_profile"): "aac_value",
    ("av", "aac_profile"): "aac_value", ("av", "aac_audio_object_type"): "aac_value",
    ("m4a", "primary_audio_profile"): "aac_value", ("m4a", "audio_profile"): "aac_value",
    ("m4a", "aac_profile"): "aac_value", ("m4a", "aac_audio_object_type"): "aac_value",
    ("mp4", "primary_audio_profile"): "aac_value", ("mp4", "audio_profile"): "aac_value",
    ("mp4", "aac_profile"): "aac_value", ("mp4", "aac_audio_object_type"): "aac_value",
    ("mkv", "primary_audio_profile"): "aac_value", ("mkv", "aac_profile"): "aac_value",
    ("media", "mp3_mpeg_version"): "mp3_value", ("media", "mp3_version"): "mp3_value",
    ("media", "mpeg_audio_version"): "mp3_value", ("media", "mpeg_version"): "mp3_value",
    ("media", "mp3_layer"): "mp3_value", ("media", "mpeg_layer"): "mp3_value", ("media", "audio_layer"): "mp3_value",
    ("media", "mp3_bitrate_kbps"): "mp3_value", ("media", "mp3_first_frame_bitrate_kbps"): "mp3_value",
    ("media", "first_frame_bitrate_kbps"): "mp3_value",
    ("media", "mp3_vbr_header"): "mp3_value", ("media", "mp3_vbr_header_type"): "mp3_value",
    ("media", "vbr_header"): "mp3_value", ("media", "vbr_header_type"): "mp3_value",
    ("media", "mp3_lame_encoder"): "mp3_value", ("media", "lame_encoder"): "mp3_value",
    ("media", "mp3_encoder_tag"): "mp3_value", ("media", "lame_tag"): "mp3_value",
    ("media", "mp3_frame_count"): "mp3_value", ("media", "mp3_frames"): "mp3_value",
    ("media", "mp3_scanned_frame_count"): "mp3_value", ("media", "mp3_vbr_frames"): "mp3_value",
    ("media", "xing_frames"): "mp3_value", ("media", "vbr_frames"): "mp3_value",
    ("media", "mp3_channel_mode"): "mp3_value", ("media", "mp3_sample_rate"): "mp3_value",
    ("audio", "mp3_mpeg_version"): "mp3_value", ("audio", "mpeg_version"): "mp3_value",
    ("audio", "mp3_layer"): "mp3_value", ("audio", "mp3_bitrate_kbps"): "mp3_value",
    ("audio", "mp3_vbr_header"): "mp3_value", ("audio", "mp3_lame_encoder"): "mp3_value",
    ("audio", "mp3_frame_count"): "mp3_value", ("audio", "mp3_channel_mode"): "mp3_value",
    ("audio", "lame_encoder"): "mp3_value", ("audio", "vbr_header"): "mp3_value",
    ("av", "mp3_mpeg_version"): "mp3_value", ("av", "mp3_layer"): "mp3_value",
    ("av", "mp3_bitrate_kbps"): "mp3_value", ("av", "mp3_vbr_header"): "mp3_value",
    ("av", "mp3_lame_encoder"): "mp3_value", ("av", "mp3_frame_count"): "mp3_value",
    ("mp3", "mp3_mpeg_version"): "mp3_value", ("mp3", "mpeg_version"): "mp3_value",
    ("mp3", "mpeg_audio_version"): "mp3_value", ("mp3", "mp3_layer"): "mp3_value",
    ("mp3", "mpeg_layer"): "mp3_value", ("mp3", "audio_layer"): "mp3_value", ("mp3", "layer"): "mp3_value",
    ("mp3", "mp3_bitrate_kbps"): "mp3_value", ("mp3", "bitrate_kbps"): "mp3_value",
    ("mp3", "first_frame_bitrate_kbps"): "mp3_value",
    ("mp3", "mp3_vbr_header"): "mp3_value", ("mp3", "vbr_header"): "mp3_value",
    ("mp3", "vbr_header_type"): "mp3_value",
    ("mp3", "mp3_lame_encoder"): "mp3_value", ("mp3", "lame_encoder"): "mp3_value",
    ("mp3", "lame_tag"): "mp3_value", ("mp3", "encoder_tag"): "mp3_value",
    ("mp3", "mp3_frame_count"): "mp3_value", ("mp3", "frame_count"): "mp3_value",
    ("mp3", "mp3_frames"): "mp3_value", ("mp3", "mp3_scanned_frame_count"): "mp3_value",
    ("mp3", "xing_frames"): "mp3_value", ("mp3", "vbr_frames"): "mp3_value",
    ("mp3", "mp3_channel_mode"): "mp3_value", ("mp3", "channel_mode"): "mp3_value",
}

_AOT = {1: "Main", 2: "LC", 3: "SSR", 4: "LTP", 5: "HE-AAC", 29: "HE-AACv2", 23: "LD", 39: "ELD", 42: "xHE-AAC"}
_MKV_LEGACY = {"MAIN": 1, "LC": 2, "SSR": 3, "LTP": 4, "SBR": 5}


class _Bits:
    def __init__(self, b):
        self.b, self.p = b, 0

    def get(self, n):
        v = 0
        for _ in range(n):
            if self.p >= 8 * len(self.b):
                raise ValueError("short")
            v = v << 1 | (self.b[self.p >> 3] >> (7 - (self.p & 7))) & 1
            self.p += 1
        return v

    def left(self):
        return 8 * len(self.b) - self.p


def _aot(bs):
    a = bs.get(5)
    return 32 + bs.get(6) if a == 31 else a


def asc_profile_aot(asc):
    """The ffprobe-relevant AOT of an AudioSpecificConfig: 5/29 when SBR/PS is signalled, else the base aot."""
    bs = _Bits(asc)
    aot = _aot(bs)
    sfi = bs.get(4)
    if sfi == 15:
        bs.get(24)
    bs.get(4)
    if aot in (5, 29):
        return aot
    if aot in (1, 2, 3, 4, 6, 7, 17, 19, 20, 21, 22, 23):        # GASpecificConfig, then the sync extension
        try:
            bs.get(1)                                           # frameLengthFlag
            if bs.get(1):
                bs.get(14)                                      # coreCoderDelay
            ext = bs.get(1)
            if aot in (6, 20):
                bs.get(3)
            if ext and aot in (17, 19, 20, 21, 22, 23):
                return aot
            while bs.left() >= 16:
                if bs.get(11) == 0x2B7:
                    if _aot(bs) == 5 and bs.get(1):
                        if bs.get(4) == sfi:                    # ffmpeg mpeg4audio: ext index == core -> no SBR
                            return aot
                        if bs.left() >= 12 and bs.get(11) == 0x548 and bs.get(1):
                            return 29
                        return 5
                    break
                break
        except ValueError:
            pass
    return aot


def _boxes(b, s, e):
    while s + 8 <= e:
        n = int.from_bytes(b[s:s + 4], "big")
        t = bytes(b[s + 4:s + 8])
        h = 8
        if n == 1 and s + 16 <= e:
            n, h = int.from_bytes(b[s + 8:s + 16], "big"), 16
        elif n == 0:
            n = e - s
        if n < h or s + n > e:
            return
        yield t, s + h, s + n
        s += n


def _child(b, s, e, typ):
    for t, cs, ce in _boxes(b, s, e):
        if t == typ:
            return cs, ce
    return None


def _desc_len(b, i):
    n = 0
    for _ in range(4):
        if i >= len(b):
            return None, i
        c = b[i]
        i += 1
        n = n << 7 | c & 0x7F
        if not c & 0x80:
            break
    return n, i


def _esds_asc(b, s, e):
    """(objectTypeIndication, DecoderSpecificInfo bytes or None) of an esds box body, or None."""
    i = s + 4
    if i >= e or b[i] != 0x03:
        return None
    n, i = _desc_len(b, i + 1)
    if n is None or i + 3 > e:
        return None
    fl = b[i + 2]
    i += 3
    if fl & 0x80:
        i += 2
    if fl & 0x40 and i < e:
        i += 1 + b[i]
    if fl & 0x20:
        i += 2
    if i >= e or b[i] != 0x04:
        return None
    n, i = _desc_len(b, i + 1)
    if n is None or i + 13 > e:
        return None
    oti, dend, i = b[i], min(e, i + n), i + 13
    if i < dend and b[i] == 0x05:
        n, i = _desc_len(b, i + 1)
        if n is not None and i + n <= e:
            return oti, bytes(b[i:i + n])
    return oti, None


def _mp4_profile(b):
    moov = _child(b, 0, len(b), b"moov")
    if not moov:
        return None
    for t, ts, te in _boxes(b, *moov):
        if t != b"trak":
            continue
        mdia = _child(b, ts, te, b"mdia")
        hdlr = mdia and _child(b, mdia[0], mdia[1], b"hdlr")
        if not hdlr or bytes(b[hdlr[0] + 8:hdlr[0] + 12]) != b"soun":
            continue
        minf = _child(b, mdia[0], mdia[1], b"minf")
        stbl = minf and _child(b, minf[0], minf[1], b"stbl")
        stsd = stbl and _child(b, stbl[0], stbl[1], b"stsd")
        if not stsd:
            return "none"
        es = stsd[0] + 8
        if es + 8 > stsd[1]:
            return "none"
        fourcc = bytes(b[es + 4:es + 8])
        if fourcc not in (b"mp4a", b"enca"):
            return "none"
        ee = min(stsd[1], es + int.from_bytes(b[es:es + 4], "big"))
        ver = int.from_bytes(b[es + 16:es + 18], "big")
        kids = es + 36 + {1: 16, 2: 36}.get(ver, 0)
        r = _child(b, kids, ee, b"esds")
        if r is None:
            k = bytes(b[es:ee]).find(b"esds")                 # wave/other wrappers: fall back to a scan
            if k < 4:
                return None
            r = (es + k + 4, min(ee, es + k - 4 + int.from_bytes(b[es + k - 4:es + k], "big")))
        got = _esds_asc(b, *r)
        if not got:
            return None
        oti, asc = got
        if oti not in (0x40, 0x66, 0x67, 0x68):
            return "none"
        if oti in (0x66, 0x67, 0x68):                         # MPEG-2 AAC: Main / LC / SSR
            return {0x66: "Main", 0x67: "LC", 0x68: "SSR"}[oti]
        return _AOT.get(asc_profile_aot(asc)) if asc else None
    return "none"


def _vint(b, i):
    if i >= len(b) or b[i] == 0:
        return None, i
    c, ln = b[i], 1
    while not c & (0x80 >> (ln - 1)):
        ln += 1
    v = c & (0xFF >> ln)
    for k in range(1, ln):
        v = v << 8 | b[i + k]
    return v, i + ln


def _mkv_profile(b):
    k = b.find(b"A_AAC")
    if k < 0:
        return "none" if b.find(b"\x86", 0, 4096) >= 0 and b.find(b"A_", 0) >= 0 else None
    tail = bytes(b[k + 5:k + 24]).split(b"\x00")[0]
    if tail.startswith(b"/MPEG"):
        name = tail.decode("latin-1", "replace").rsplit("/", 1)[-1]
        if name in _MKV_LEGACY:
            return _AOT[_MKV_LEGACY[name]]
    j = b.find(b"\x63\xa2", max(0, k - 400), k + 400)
    if j < 0:
        return None
    n, i = _vint(b, j + 2)
    if not n or i + n > len(b):
        return None
    return _AOT.get(asc_profile_aot(bytes(b[i:i + n])))


def _skip_id3(b):
    o = 0
    while o + 10 <= len(b) and b[o:o + 3] == b"ID3" and not any(x & 0x80 for x in b[o + 6:o + 10]):
        o += 10 + (b[o + 6] << 21 | b[o + 7] << 14 | b[o + 8] << 7 | b[o + 9]) + (10 if b[o + 5] & 0x10 else 0)
    return o


def _profile(b):
    if b[:4] == b"\x1a\x45\xdf\xa3":
        return _mkv_profile(b)
    if b[4:8] == b"ftyp" or b[4:8] in (b"moov", b"mdat", b"wide", b"free"):
        return _mp4_profile(b)
    o = _skip_id3(b)
    h = b[o:o + 4]
    if len(h) == 4 and h[0] == 0xFF and h[1] & 0xF6 == 0xF0:           # ADTS
        return _AOT.get((h[2] >> 6) + 1)
    if _mpa_header(b, o) is not None or b[:4] in (b"fLaC", b"OggS", b"RIFF", b"FORM", b".snd", b"caff") \
            or b[:4] == b"\x30\x26\xb2\x75" or b[:6] == b"#!AMR\n":
        return "none"
    return None


def aac_value(data, ctx):
    if data is None:
        return None
    try:
        b = bytes(data)
        v = _profile(b)
        f = (ctx or {}).get("field") or ""
        if v not in (None, "none") and f.endswith("object_type"):
            return {n: a for a, n in _AOT.items()}.get(v)
        return v
    except Exception:  # noqa: BLE001 -- malformed input never raises past the extractor
        return None


_BR = {(1, 1): (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448),
       (1, 2): (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384),
       (1, 3): (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320),
       (2, 1): (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256),
       (2, 2): (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160)}
_SR = {3: (44100, 48000, 32000), 2: (22050, 24000, 16000), 0: (11025, 12000, 8000)}
_VER = {3: "1", 2: "2", 0: "2.5"}
_MODE = ("Stereo", "Joint Stereo", "Dual Channel", "Single Channel")


def _mpa_header(b, o):
    """dict of the MPEG audio frame header at o, or None."""
    if o + 4 > len(b) or b[o] != 0xFF or b[o + 1] & 0xE0 != 0xE0:
        return None
    v, lay, bi, si = (b[o + 1] >> 3) & 3, 4 - ((b[o + 1] >> 1) & 3), b[o + 2] >> 4, (b[o + 2] >> 2) & 3
    if v == 1 or lay == 4 or bi in (0, 15) or si == 3:
        return None
    br = _BR[(1, lay)][bi] if v == 3 else _BR[(2, 1 if lay == 1 else 2)][bi]
    sr = _SR[v][si]
    pad = (b[o + 2] >> 1) & 1
    if lay == 1:
        size = (12 * br * 1000 // sr + pad) * 4
    else:
        size = (144 if v == 3 or lay == 2 else 72) * br * 1000 // sr + pad
    return {"v": v, "layer": lay, "br": br, "sr": sr, "size": size, "mode": b[o + 3] >> 6}


def _first_frame(b):
    o = _skip_id3(b)
    end = min(len(b) - 4, o + 65536)
    while o < end:
        h = _mpa_header(b, o)
        if h and h["size"] > 4:
            nxt = o + h["size"]
            h2 = _mpa_header(b, nxt)
            if (h2 and h2["v"] == h["v"] and h2["layer"] == h["layer"] and h2["sr"] == h["sr"]) or nxt == len(b):
                return o, h
        o = b.find(b"\xff", o + 1, end)
        if o < 0:
            break
    return None, None


def _vbr_tag(b, o, h):
    """(kind, frames or None, encoder9 or None) of a Xing/Info/VBRI tag in the frame at o, or None."""
    if h["layer"] != 3:
        return None
    side = (32 if h["mode"] != 3 else 17) if h["v"] == 3 else (17 if h["mode"] != 3 else 9)
    x = o + 4 + side
    tag = bytes(b[x:x + 4])
    if tag in (b"Xing", b"Info"):
        flags = int.from_bytes(b[x + 4:x + 8], "big")
        i, frames = x + 8, None
        if flags & 1:
            frames = int.from_bytes(b[i:i + 4], "big")
            i += 4
        i += (4 if flags & 2 else 0) + (100 if flags & 4 else 0) + (4 if flags & 8 else 0)
        enc = bytes(b[i:i + 9])
        enc = enc.decode("latin-1").rstrip("\x00 ") if enc and all(32 <= c < 127 or c == 0 for c in enc) and enc[0] else None
        return tag.decode(), frames, enc or None
    v = o + 4 + 32
    if bytes(b[v:v + 4]) == b"VBRI":
        return "VBRI", int.from_bytes(b[v + 14:v + 18], "big"), None
    return None


def mp3_value(data, ctx):
    if data is None:
        return None
    try:
        return _mp3(bytes(data), (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001
        return None


def _mp3(b, f):
    o, h = _first_frame(b)
    if h is None:
        return "none"
    if f.endswith(("mpeg_version", "mp3_version", "mpeg_audio_version")):
        return _VER[h["v"]]
    if f.endswith("layer"):
        return h["layer"]
    if f.endswith("bitrate_kbps"):
        return h["br"]
    if f.endswith("channel_mode"):
        return _MODE[h["mode"]]
    if f.endswith("sample_rate"):
        return h["sr"]
    tag = _vbr_tag(b, o, h)
    if "vbr_header" in f:
        return tag[0] if tag else "none"
    if f.endswith(("lame_encoder", "encoder_tag", "lame_tag")):
        return (tag[2] if tag else None) or "none"
    if f in ("mp3_vbr_frames", "xing_frames", "vbr_frames"):
        return tag[1] if tag and tag[1] is not None else "none"
    # frame count: scan (the VBR tag frame is not audio), the header's frames field wins when present
    n, p = 0, o + (h["size"] if tag else 0)
    while True:
        hh = _mpa_header(b, p)
        if hh is None or hh["size"] <= 4 or p + hh["size"] > len(b) + 1:
            break
        n += 1
        p += hh["size"]
    if f == "mp3_scanned_frame_count":
        return n
    return tag[1] if tag and tag[1] is not None else n
