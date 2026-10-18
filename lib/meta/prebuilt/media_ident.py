"""`media` renamed / transcoded containers -- prebuilt, SPECULATIVE. Flavor D17: "Voice notes have been transcoded,
renamed" -- the member's extension is a label, the magic is the truth.

Fields (fmt tokens `media` / `audio` / `av`, like prebuilt media.py):
  - container_format_by_magic (+ actual_/detected_/magic_ aliases): short container token from the MAGIC bytes --
    wav (RIFF/RIFX WAVE), rf64 (RF64/BW64 WAVE), aiff (FORM AIFF/AIFC), mp3 (ID3 / MPEG-audio sync), ogg (OggS),
    flac (fLaC), mp4 (ftyp), matroska (EBML), amr (#!AMR), au (.snd), adts (ADTS AAC sync), caf (caff),
    asf (ASF header GUID 3026b275-8e66-cf11-a6d9-00aa0062ce6c). `media.container_format` itself is owned by prebuilt
    media.py (ffprobe format_name spelling) and is NOT re-registered here.
  - declared_extension: the member name's extension as stored, without the dot ("audio-001.wav" -> "wav"); no dot
    -> none.
  - extension_matches_content: bool, the declared extension is one the magic's container is normally saved under
    (.wav for RF64 counts as a match; .m4a/.mp4/.m4b/.3gp for ftyp; .aac/.adts for ADTS; .wma/.asf/.wmv for ASF).
  - mime_type_by_magic: exiftool's MIMEType spelling for the content (audio/x-wav, audio/mpeg, audio/ogg, audio/flac,
    audio/mp4, audio/x-aiff, audio/aac, audio/x-matroska) plus audio/amr, audio/basic, audio/x-caf (exiftool has no
    MIMEType for those; libmagic / Python mimetypes spellings). ASF is video/x-ms-asf even audio-only: exiftool only
    says audio/x-ms-wma when the NAME ends .wma, and libmagic agrees on video/x-ms-asf. A video track flips mp4 /
    matroska to video/*. NOTE: the coverage atlas guessed IANA-style audio/wav; three readers (exiftool, libmagic, Python
    mimetypes) all say audio/x-wav, so that is what this returns.
  - actual_audio_codec_name (+ aliases, NOT the verified primary_audio_codec_name): the builtin D17 reader extended
    with ASF/WMA (Stream Properties WAVEFORMATEX tag -> wmav2 ...), CAF ('desc' format id -> pcm_s16le / aac / alac
    ...) and MP4 esds objectTypeIndication (0x40 aac, 0x69/0x6b mp3), where the builtin says None or always 'aac'.
Non-audio bytes: container/codec -> none; mime_type_by_magic still names common non-audio magics (a PNG renamed
.wav is image/png). Unrecognised bytes -> None (cannot answer)."""
import struct

_ASF_HDR = bytes.fromhex("3026b2758e66cf11a6d900aa0062ce6c")
_ASF_STREAM = bytes.fromhex("9107dcb7b7a9cf118ee600c00c205365")
_ASF_AUDIO = bytes.fromhex("409e69f84d5bcf11a8fd00805f5c442b")
_ASF_VIDEO = bytes.fromhex("c0ef19bc4d5bcf11a8fd00805f5c442b")

_EXT_OK = {"wav": ("wav", "rf64"), "wave": ("wav", "rf64"), "bwf": ("wav", "rf64"), "rf64": ("rf64",),
           "aif": ("aiff",), "aiff": ("aiff",), "aifc": ("aiff",), "mp3": ("mp3",), "mp2": ("mp3",),
           "ogg": ("ogg",), "oga": ("ogg",), "opus": ("ogg",), "spx": ("ogg",), "flac": ("flac",),
           "m4a": ("mp4",), "mp4": ("mp4",), "m4b": ("mp4",), "m4p": ("mp4",), "m4v": ("mp4",), "mov": ("mp4",),
           "3gp": ("mp4",), "3g2": ("mp4",), "mka": ("matroska",), "mkv": ("matroska",), "webm": ("matroska",),
           "amr": ("amr",), "awb": ("amr",), "au": ("au",), "snd": ("au",), "aac": ("adts",), "adts": ("adts",),
           "caf": ("caf",), "wma": ("asf",), "asf": ("asf",), "wmv": ("asf",)}

_MIME = {"wav": "audio/x-wav", "rf64": "audio/x-wav", "aiff": "audio/x-aiff", "mp3": "audio/mpeg", "ogg": "audio/ogg",
         "flac": "audio/flac", "mp4": "audio/mp4", "matroska": "audio/x-matroska", "amr": "audio/amr",
         "au": "audio/basic", "adts": "audio/aac", "caf": "audio/x-caf", "asf": "video/x-ms-asf"}
_VIDEO_MIME = {"mp4": "video/mp4", "matroska": "video/x-matroska"}
_OTHER_MIME = ((b"\x89PNG\r\n\x1a\n", "image/png"), (b"\xff\xd8\xff", "image/jpeg"), (b"GIF87a", "image/gif"),
               (b"GIF89a", "image/gif"), (b"%PDF-", "application/pdf"), (b"PK\x03\x04", "application/zip"),
               (b"BM", "image/bmp"), (b"\x1f\x8b", "application/gzip"), (b"\x7fELF", "application/x-elf"),
               (b"MZ", "application/x-dosexec"))
_NON_AUDIO = tuple(m for m, _ in _OTHER_MIME) + (b"\xd0\xcf\x11\xe0", b"{\\rtf", b"SQLite format 3")

_WAV_TAGS = {0x0001: None, 0x0002: "adpcm_ms", 0x0006: "pcm_alaw", 0x0007: "pcm_mulaw", 0x000A: "wmavoice",
             0x0011: "adpcm_ima_wav", 0x0055: "mp3", 0x0160: "wmav1", 0x0161: "wmav2", 0x0162: "wmapro",
             0x0163: "wmalossless", 0x00FF: "aac", 0x1610: "aac", 0x2000: "ac3"}
_CAF_IDS = {b"aac ": "aac", b"alac": "alac", b"ulaw": "pcm_mulaw", b"alaw": "pcm_alaw", b".mp3": "mp3",
            b".mp2": "mp2", b"ima4": "adpcm_ima_qt", b"opus": "opus", b"flac": "flac", b"samr": "amr_nb",
            b"sawb": "amr_wb", b"ac-3": "ac3", b"MAC3": "mace3", b"MAC6": "mace6", b"Qclp": "qcelp", b"QDM2": "qdm2"}
_ESDS_OTI = {0x40: "aac", 0x66: "aac", 0x67: "aac", 0x68: "aac", 0x69: "mp3", 0x6B: "mp3", 0xA5: "ac3",
             0xA6: "eac3", 0xA9: "dts", 0xDD: "vorbis", 0xAD: "opus"}


def _mpeg_ok(h):
    """A plausible MPEG-audio (layer I-III) frame header at h[0:4]."""
    return (len(h) >= 4 and h[0] == 0xFF and (h[1] & 0xE0) == 0xE0 and ((h[1] >> 3) & 3) != 1 and (h[1] & 6)
            and (h[2] >> 4) not in (0, 15) and ((h[2] >> 2) & 3) != 3)


def _container(b):
    """Short container token by MAGIC, or None."""
    if b[8:12] == b"WAVE":
        if b[:4] in (b"RIFF", b"RIFX"):
            return "wav"
        if b[:4] in (b"RF64", b"BW64"):
            return "rf64"
    if b[:4] == b"FORM" and b[8:12] in (b"AIFF", b"AIFC"):
        return "aiff"
    if b[:4] == b"OggS":
        return "ogg"
    if b[:4] == b"fLaC":
        return "flac"
    if b[4:8] == b"ftyp":
        return "mp4"
    if b[:4] == b"\x1a\x45\xdf\xa3":
        return "matroska"
    if b[:5] == b"#!AMR":
        return "amr"
    if b[:4] == b".snd":
        return "au"
    if b[:4] == b"caff":
        return "caf"
    if b[:16] == _ASF_HDR:
        return "asf"
    i = 0
    if b[:3] == b"ID3" and len(b) > 10:
        sz = b[6:10]
        i = 10 + ((sz[0] << 21) | (sz[1] << 14) | (sz[2] << 7) | sz[3])
        if b[i:i + 4] == b"fLaC":
            return "flac"
    if len(b) >= i + 4 and b[i] == 0xFF and (b[i + 1] & 0xF6) == 0xF0:
        return "adts"
    if b[:3] == b"ID3" or _mpeg_ok(b[i:i + 4]):
        return "mp3"
    return None


def _non_audio(b):
    if b.startswith(_NON_AUDIO):
        return True
    head = b[:512]
    return bool(head) and all(c in b"\t\n\r" or 32 <= c < 127 for c in head)


def _asf_streams(b):
    """[(stream_type_guid16, type_specific_bytes)] from the ASF Header Object's Stream Properties Objects."""
    out = []
    hsize, = struct.unpack_from("<Q", b, 16)
    i, end = 30, min(len(b), hsize)
    while i + 24 <= end:
        guid, size = b[i:i + 16], struct.unpack_from("<Q", b, i + 16)[0]
        if size < 24:
            break
        if guid == _ASF_STREAM and i + 78 <= len(b):
            tlen, = struct.unpack_from("<I", b, i + 64)
            out.append((b[i + 24:i + 40], b[i + 78:i + 78 + tlen]))
        i += size
    return out


def _asf_codec(b):
    for st, ts in _asf_streams(b):
        if st == _ASF_AUDIO and len(ts) >= 16:
            tag, = struct.unpack_from("<H", ts, 0)
            if tag in (1, 3):
                bits, = struct.unpack_from("<H", ts, 14)
                return "pcm_f%dle" % bits if tag == 3 else ("pcm_u8" if bits == 8 else "pcm_s%dle" % bits)
            return _WAV_TAGS.get(tag)
    return None


def _caf_codec(b):
    i = 8
    while i + 12 <= len(b):
        ctype, size = b[i:i + 4], struct.unpack_from(">q", b, i + 4)[0]
        if ctype == b"desc" and i + 44 <= len(b):
            fid = b[i + 20:i + 24]
            flags, = struct.unpack_from(">I", b, i + 24)
            bits, = struct.unpack_from(">I", b, i + 40)
            if fid == b"lpcm":
                e = "le" if flags & 2 else "be"
                if flags & 1:
                    return "pcm_f%d%s" % (bits, e)
                return "pcm_s8" if bits == 8 else "pcm_s%d%s" % (bits, e)
            return _CAF_IDS.get(fid)
        if size < 0:
            break
        i += 12 + size
    return None


def _desc_len(b, i):
    n = 0
    for _ in range(4):
        c = b[i]
        i += 1
        n = (n << 7) | (c & 0x7F)
        if not c & 0x80:
            break
    return n, i


def _esds_oti(b, k):
    """objectTypeIndication of the DecoderConfigDescriptor in the esds box whose type starts at k."""
    i = k + 8                                   # 'esds' + version/flags
    if b[i] != 0x03:
        return None
    _n, i = _desc_len(b, i + 1)
    fl = b[i + 2]
    i += 3 + (2 if fl & 0x80 else 0) + (1 + b[i + 3] if fl & 0x40 else 0)
    if fl & 0x20:
        i += 2
    if b[i] != 0x04:
        return None
    _n, i = _desc_len(b, i + 1)
    return b[i]


def _mp4_codec(b):
    k = b.find(b"stsd")
    if k < 0 or k + 20 > len(b):
        return None
    if b[k + 16:k + 20] != b"mp4a":   # stsd ver/flags, entry_count, entry size, entry type
        return None
    e = b.find(b"esds", k, k + 512)
    if e < 0:
        return None
    oti = _esds_oti(b, e)
    return _ESDS_OTI.get(oti) if oti is not None else None


def _codec(b):
    c = _container(b)
    if c == "asf":
        return _asf_codec(b)
    if c == "caf":
        return _caf_codec(b)
    v = _mp4_codec(b) if c == "mp4" else None
    if v:
        return v
    from ..media import _audio_codec
    return _audio_codec(b)


def _has_video(b, c):
    if c == "asf":
        return any(st == _ASF_VIDEO for st, _ in _asf_streams(b))
    if c == "mp4":
        return b.find(b"hdlr\x00\x00\x00\x00\x00\x00\x00\x00vide") >= 0
    if c == "matroska":
        return b.find(b"\x83\x81\x01") >= 0      # TrackType (0x83), 1-byte size, 1 = video
    return False


def _ext(member):
    name = str(member or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    if "." not in name.lstrip("."):
        return None
    return name.rsplit(".", 1)[1] or None


def container_by_magic(data, ctx):
    if not data:
        return None
    try:
        b = bytes(data)
        c = _container(b)
        return c or ("none" if _non_audio(b) else None)
    except Exception:  # noqa: BLE001
        return None


def declared_extension(data, ctx):
    e = _ext((ctx or {}).get("member"))
    return e if e else "none"


def extension_matches(data, ctx):
    """bool: the declared extension fits the container the magic names. Field names saying *mismatch* get the
    negation. Unknown content (neither audio nor a recognised non-audio magic) -> None."""
    if not data:
        return None
    try:
        b = bytes(data)
        e = _ext((ctx or {}).get("member"))
        if e is None:
            return None
        c = _container(b)
        if c is None and not _non_audio(b):
            return None
        ok = c is not None and c in _EXT_OK.get(e.lower(), ())
        return (not ok) if "mismatch" in ((ctx or {}).get("field") or "") else ok
    except Exception:  # noqa: BLE001
        return None


def mime_by_magic(data, ctx):
    if not data:
        return None
    try:
        b = bytes(data)
        c = _container(b)
        if c is not None:
            return _VIDEO_MIME[c] if c in _VIDEO_MIME and _has_video(b, c) else _MIME[c]
        for m, t in _OTHER_MIME:
            if b.startswith(m):
                return t
        return "text/plain" if _non_audio(b) else None
    except Exception:  # noqa: BLE001
        return None


def actual_codec(data, ctx):
    if not data:
        return None
    try:
        b = bytes(data)
        v = _codec(b)
        if v is None and _non_audio(b):
            return "none"
        return v
    except Exception:  # noqa: BLE001
        return None


FIELDS = {
    ("media", "container_format_by_magic"): "container_by_magic",
    ("media", "actual_container_format"): "container_by_magic",
    ("media", "detected_container_format"): "container_by_magic",
    ("media", "magic_container_format"): "container_by_magic",
    ("media", "container_by_magic"): "container_by_magic",
    ("media", "actual_container"): "container_by_magic",
    ("media", "detected_container"): "container_by_magic",
    ("media", "true_container_format"): "container_by_magic",
    ("media", "content_container_format"): "container_by_magic",
    ("media", "declared_extension"): "declared_extension",
    ("media", "declared_file_extension"): "declared_extension",
    ("media", "file_extension"): "declared_extension",
    ("media", "filename_extension"): "declared_extension",
    ("media", "extension"): "declared_extension",
    ("media", "extension_matches_content"): "extension_matches",
    ("media", "extension_matches_magic"): "extension_matches",
    ("media", "extension_matches_container"): "extension_matches",
    ("media", "declared_extension_matches_content"): "extension_matches",
    ("media", "extension_mismatch"): "extension_matches",
    ("media", "extension_content_mismatch"): "extension_matches",
    ("media", "extension_magic_mismatch"): "extension_matches",
    ("media", "mime_type_by_magic"): "mime_by_magic",
    ("media", "magic_mime_type"): "mime_by_magic",
    ("media", "detected_mime_type"): "mime_by_magic",
    ("media", "actual_mime_type"): "mime_by_magic",
    ("media", "content_mime_type"): "mime_by_magic",
    ("media", "mime_type"): "mime_by_magic",
    ("media", "actual_audio_codec_name"): "actual_codec",
    ("media", "detected_audio_codec_name"): "actual_codec",
    ("media", "audio_codec_by_magic"): "actual_codec",
    ("media", "actual_codec_name"): "actual_codec",
    ("media", "actual_codec"): "actual_codec",
    ("audio", "container_format_by_magic"): "container_by_magic",
    ("audio", "actual_container_format"): "container_by_magic",
    ("audio", "detected_container_format"): "container_by_magic",
    ("audio", "declared_extension"): "declared_extension",
    ("audio", "file_extension"): "declared_extension",
    ("audio", "extension_matches_content"): "extension_matches",
    ("audio", "extension_matches_magic"): "extension_matches",
    ("audio", "extension_mismatch"): "extension_matches",
    ("audio", "mime_type_by_magic"): "mime_by_magic",
    ("audio", "mime_type"): "mime_by_magic",
    ("audio", "actual_audio_codec_name"): "actual_codec",
    ("audio", "actual_codec_name"): "actual_codec",
    ("av", "container_format_by_magic"): "container_by_magic",
    ("av", "actual_container_format"): "container_by_magic",
    ("av", "declared_extension"): "declared_extension",
    ("av", "file_extension"): "declared_extension",
    ("av", "extension_matches_content"): "extension_matches",
    ("av", "extension_mismatch"): "extension_matches",
    ("av", "mime_type_by_magic"): "mime_by_magic",
    ("av", "mime_type"): "mime_by_magic",
    ("av", "actual_audio_codec_name"): "actual_codec",
}
