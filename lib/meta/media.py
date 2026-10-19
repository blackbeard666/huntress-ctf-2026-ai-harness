"""Media (audio stream) fields. COPIED from the GM-verified D17 solver (challenges/day17/metadata-hear-me-out/solver/solve.py):
media.primary_audio_codec_name = the ffprobe-style codec_name of the FIRST audio stream, read from the container header
bytes, never the extension ("transcoded, renamed" voice notes): RIFF/RIFX/RF64 WAVE fmt tag (+ WAVE_FORMAT_EXTENSIBLE
SubFormat), AIFF/AIFC COMM, fLaC, Ogg (opus/vorbis/flac/speex), AMR, .snd, MP4 stsd, Matroska codec ids, MPEG audio /
ADTS frame sync. GM-confirmed: 16-bit PCM WAV -> `pcm_s16le` (D17 Single); the other containers are ffprobe's names."""
import struct


_WAV_TAGS = {0x0002: "adpcm_ms", 0x0006: "pcm_alaw", 0x0007: "pcm_mulaw", 0x0011: "adpcm_ima_wav",
             0x0031: "gsm_ms", 0x0050: "mp2", 0x0055: "mp3", 0x0092: "ac3", 0x00FF: "aac", 0x1610: "aac",
             0x2000: "ac3", 0x2001: "dts", 0xF1AC: "flac", 0x0161: "wmav2", 0x0160: "wmav1", 0x0162: "wmapro"}


def _pcm_name(tag, bits, be=False, unsigned8=True):
    e = "be" if be else "le"
    if tag == 3:
        return "pcm_f%d%s" % (bits or 32, e)
    if bits == 8 and unsigned8:
        return "pcm_u8"
    if bits == 8:
        return "pcm_s8"
    return "pcm_s%d%s" % (bits or 16, e)


def _riff_codec(data):
    be = data[:4] == b"RIFX"
    en = ">" if be else "<"
    i = 12
    while i + 8 <= len(data):
        cid, ln = data[i:i + 4], struct.unpack(en + "I", data[i + 4:i + 8])[0]
        if cid == b"fmt ":
            body = data[i + 8:i + 8 + ln]
            tag, = struct.unpack(en + "H", body[:2])
            bits = struct.unpack(en + "H", body[14:16])[0] if len(body) >= 16 else 16
            if tag == 0xFFFE and len(body) >= 40:  # WAVE_FORMAT_EXTENSIBLE: SubFormat GUID's first u16
                tag = struct.unpack(en + "H", body[24:26])[0]
            if tag in (1, 3):
                return _pcm_name(tag, bits, be)
            return _WAV_TAGS.get(tag)
        i += 8 + ln + (ln & 1)
    return None


def _aiff_codec(data):
    aifc = data[8:12] == b"AIFC"
    i = 12
    while i + 8 <= len(data):
        cid, ln = data[i:i + 4], struct.unpack(">I", data[i + 4:i + 8])[0]
        if cid == b"COMM":
            bits = struct.unpack(">H", data[i + 14:i + 16])[0]
            comp = data[i + 26:i + 30] if aifc else b"NONE"
            m = {b"NONE": _pcm_name(1, bits, True, False), b"twos": _pcm_name(1, bits, True, False),
                 b"sowt": _pcm_name(1, bits, False, False), b"fl32": "pcm_f32be", b"FL32": "pcm_f32be",
                 b"fl64": "pcm_f64be", b"alaw": "pcm_alaw", b"ulaw": "pcm_mulaw", b"ima4": "adpcm_ima_qt"}
            return m.get(comp, comp.decode("latin-1").strip() or None)
        i += 8 + ln + (ln & 1)
    return None


def _mpeg_audio_codec(data):
    i = 0
    if data[:3] == b"ID3" and len(data) > 10:
        sz = data[6:10]
        i = 10 + ((sz[0] << 21) | (sz[1] << 14) | (sz[2] << 7) | sz[3])
    for j in range(i, min(len(data) - 1, i + 65536)):
        if data[j] == 0xFF and (data[j + 1] & 0xE0) == 0xE0:
            if (data[j + 1] & 0x06) == 0:  # layer bits 00 = ADTS AAC
                return "aac" if (data[j + 1] & 0xF6) == 0xF0 else None
            return {1: "mp3", 2: "mp2", 3: "mp1"}.get((data[j + 1] >> 1) & 3)
    return None


def _audio_codec(data):
    """ffprobe-style codec_name of the first audio stream, from the container header bytes."""
    if data[:4] in (b"RIFF", b"RIFX", b"RF64") and data[8:12] == b"WAVE":
        return _riff_codec(data)
    if data[:4] == b"FORM" and data[8:12] in (b"AIFF", b"AIFC"):
        return _aiff_codec(data)
    if data[:4] == b"fLaC":
        return "flac"
    if data[:4] == b"OggS":
        head = data[28:64]
        for sig, n in ((b"OpusHead", "opus"), (b"\x01vorbis", "vorbis"), (b"\x7fFLAC", "flac"), (b"Speex", "speex")):
            if head.startswith(sig):
                return n
        return None
    if data[:6] == b"#!AMR\n":
        return "amr_nb"
    if data[:9] == b"#!AMR-WB\n":
        return "amr_wb"
    if data[:4] == b".snd":
        enc = struct.unpack(">I", data[12:16])[0]
        return {1: "pcm_mulaw", 2: "pcm_s8", 3: "pcm_s16be", 4: "pcm_s24be", 5: "pcm_s32be", 6: "pcm_f32be",
                7: "pcm_f64be", 27: "pcm_alaw"}.get(enc)
    if data[4:8] == b"ftyp":
        for sig, n in ((b"mp4a", "aac"), (b"alac", "alac"), (b"Opus", "opus"), (b"fLaC", "flac"),
                       (b"ac-3", "ac3"), (b"ec-3", "eac3"), (b"samr", "amr_nb"), (b"sawb", "amr_wb")):
            k = data.find(b"stsd")
            if k >= 0 and data.find(sig, k, k + 64) >= 0:
                return n
        return None
    if data[:4] == b"\x1a\x45\xdf\xa3":
        for sig, n in ((b"A_OPUS", "opus"), (b"A_VORBIS", "vorbis"), (b"A_AAC", "aac"), (b"A_FLAC", "flac"),
                       (b"A_MPEG/L3", "mp3"), (b"A_AC3", "ac3"), (b"A_PCM/INT/LIT", "pcm_s16le")):
            if sig in data[:65536]:
                return n
        return None
    return _mpeg_audio_codec(data)


def primary_audio_codec_name(data, ctx):
    if not data:
        return None
    try:
        return _audio_codec(data)
    except (struct.error, IndexError, ValueError):
        return None


def primary_video_dimensions(data, ctx):
    """D18: coded width x height of the first video stream as Dims (MP4 stsd visual entry / Matroska PixelWidth|Height /
    AVI biWidth|biHeight, ffprobe -- not rotated), parsed by lib.meta.prebuilt.media_video (verified 320x180)."""
    from .prebuilt.media_video import video_value
    return video_value(data, dict(ctx or {}, field="primary_video_dimensions"))
