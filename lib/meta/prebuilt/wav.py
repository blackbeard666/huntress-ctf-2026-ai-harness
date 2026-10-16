"""WAV (RIFF/WAVE) "fmt " chunk fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout: "RIFF" (or "RF64") size u32le "WAVE", then chunks (id[4], size u32le, data, padded to an even length). The
"fmt " chunk: wFormatTag u16, nChannels u16, nSamplesPerSec u32, nAvgBytesPerSec u32, nBlockAlign u16,
wBitsPerSample u16 (WAVE_FORMAT_EXTENSIBLE 0xFFFE keeps the same first 16 bytes). Values are the STORED fmt fields
(exiftool SampleRate / NumChannels / BitsPerSample / Encoding). data_size_bytes = the "data" chunk's declared size.
info_<tag> = a "LIST" chunk of list type "INFO": sub-chunks id[4] size u32le text (NUL-terminated, padded to even);
the value is the text up to the first NUL, trimmed (latin-1, the RIFF INFO convention; exiftool RIFF:Title etc.).
<tag> is the 4-char id (info_inam, info_icmt, ...) or its RIFF name (info_title=INAM, info_artist=IART,
info_comment=ICMT, info_software=ISFT, info_copyright=ICOP, info_creation_date=ICRD, info_genre=IGNR, ...);
info_tag_ids = sub-chunk ids in stored order. Stored text is returned verbatim (ICRD "2026-10-15", which exiftool
reformats as "2026:10:15"). No INFO list / tag absent -> "none".
Not RIFF....WAVE (decoy: a WebP / AVI is RIFF too) or no "fmt " chunk -> "none"."""
import struct

from ..spell import Hex

FIELDS = {
    ("wav", "fmt_sample_rate"): "wav_value",
    ("wav", "sample_rate"): "wav_value",
    ("wav", "fmt_samples_per_sec"): "wav_value",
    ("wav", "samples_per_sec"): "wav_value",
    ("wav", "fmt_sample_rate_hz"): "wav_value",
    ("wav", "sample_rate_hz"): "wav_value",
    ("wav", "fmt_channels"): "wav_value",
    ("wav", "channels"): "wav_value",
    ("wav", "num_channels"): "wav_value",
    ("wav", "fmt_num_channels"): "wav_value",
    ("wav", "channel_count"): "wav_value",
    ("wav", "fmt_bits_per_sample"): "wav_value",
    ("wav", "bits_per_sample"): "wav_value",
    ("wav", "fmt_block_align"): "wav_value",
    ("wav", "block_align"): "wav_value",
    ("wav", "fmt_byte_rate"): "wav_value",
    ("wav", "byte_rate"): "wav_value",
    ("wav", "fmt_avg_bytes_per_sec"): "wav_value",
    ("wav", "avg_bytes_per_sec"): "wav_value",
    ("wav", "fmt_audio_format"): "wav_value",
    ("wav", "audio_format"): "wav_value",
    ("wav", "fmt_format_tag"): "wav_value",
    ("wav", "format_tag"): "wav_value",
    ("wav", "fmt_audio_format_u16_hex"): "wav_value",
    ("wav", "fmt_format_tag_u16_hex"): "wav_value",
    ("wav", "audio_format_u16_hex"): "wav_value",
    ("wav", "format_tag_u16_hex"): "wav_value",
    ("wav", "data_size_bytes"): "wav_value",
    ("wav", "data_chunk_size"): "wav_value",
    ("wav", "data_chunk_size_bytes"): "wav_value",
    ("wav", "info_*"): "wav_info",
    ("wav", "list_info_*"): "wav_info",
    ("wav", "riff_info_*"): "wav_info",
    ("wav", "info_tag_ids"): "wav_info",
    ("wav", "info_chunk_ids"): "wav_info",
    ("wav", "title"): "wav_info",
    ("wav", "artist"): "wav_info",
    ("wav", "comment"): "wav_info",
    ("wav", "software"): "wav_info",
    ("wav", "copyright"): "wav_info",
}

_INFO = {"title": "INAM", "name": "INAM", "artist": "IART", "comment": "ICMT", "comments": "ICMT",
         "software": "ISFT", "copyright": "ICOP", "creation_date": "ICRD", "date_created": "ICRD", "date": "ICRD",
         "genre": "IGNR", "keywords": "IKEY", "subject": "ISBJ", "product": "IPRD", "album": "IPRD",
         "engineer": "IENG", "technician": "ITCH", "source": "ISRC", "medium": "IMED", "track_number": "ITRK",
         "commissioned": "ICMS", "archival_location": "IARL", "language": "ILNG", "encoded_by": "ITCH"}


def _chunks(b):
    """{chunk id: (offset, size)} of the first occurrence of each RIFF chunk, or None if not RIFF/WAVE."""
    if not b or len(b) < 12 or bytes(b[:4]) not in (b"RIFF", b"RF64") or bytes(b[8:12]) != b"WAVE":
        return None
    out, off = {}, 12
    while off + 8 <= len(b):
        cid, sz = bytes(b[off:off + 4]), struct.unpack_from("<I", b, off + 4)[0]
        out.setdefault(cid, (off + 8, sz))
        off += 8 + sz + (sz & 1)
    return out


def wav_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed WAV never raises past the extractor
        return None


def _value(b, f):
    ch = _chunks(b)
    if ch is None:
        return "none"
    if "data" in f:
        return ch[b"data"][1] if b"data" in ch else "none"
    if b"fmt " not in ch or ch[b"fmt "][0] + 16 > len(b):
        return "none"
    tag, nch, rate, byterate, align, bits = struct.unpack_from("<HHIIHH", b, ch[b"fmt "][0])
    if "sample_rate" in f or "samples_per_sec" in f:
        return rate
    if "channel" in f:
        return nch
    if "bits_per_sample" in f:
        return bits
    if "block_align" in f:
        return align
    if "byte" in f:
        return byterate
    if "format" in f:
        return Hex(tag, 4) if f.endswith("_hex") else tag
    return None


def _info(b):
    """[(id, text)] of the first LIST/INFO chunk, or None (no INFO list)."""
    off = 12
    while off + 12 <= len(b):
        cid, sz = bytes(b[off:off + 4]), struct.unpack_from("<I", b, off + 4)[0]
        if cid == b"LIST" and bytes(b[off + 8:off + 12]) == b"INFO":
            out, p, end = [], off + 12, min(off + 8 + sz, len(b))
            while p + 8 <= end:
                sid, ssz = bytes(b[p:p + 4]), struct.unpack_from("<I", b, p + 4)[0]
                txt = bytes(b[p + 8:p + 8 + ssz]).split(b"\x00")[0]
                out.append((sid.decode("latin-1"), txt.decode("latin-1").strip()))
                p += 8 + ssz + (ssz & 1)
            return out
        off += 8 + sz + (sz & 1)
    return None


def wav_info(data, ctx):
    if data is None:
        return None
    try:
        ctx = ctx or {}
        if _chunks(data) is None:
            return "none"
        f = ctx.get("field") or ""
        tags = _info(data)
        if f in ("info_tag_ids", "info_chunk_ids"):
            return [t for t, _ in tags] if tags else "none"
        key = (ctx.get("param") or "") if f.endswith("_*") else f
        for p in ("riff_info_", "list_info_", "info_"):
            if key.startswith(p):
                key = key[len(p):]
                break
        tid = _INFO.get(key) or (key.upper() if len(key) == 4 and key.isalnum() else None)
        if tid is None:
            return None
        return next((v for t, v in tags or () if t == tid), "none")
    except Exception:  # noqa: BLE001
        return None
