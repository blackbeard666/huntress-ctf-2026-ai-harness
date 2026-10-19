"""CAF (Apple Core Audio Format) fields -- prebuilt, SPECULATIVE (never asked yet).

Routed by MAGIC `caff` + u16 file version (1) + u16 flags, then chunks type[4] + i64 size (big-endian; a `data` chunk
may carry size -1 = to EOF). `desc` (Audio Description): float64 mSampleRate, mFormatID[4], u32 mFormatFlags,
mBytesPerPacket, mFramesPerPacket, mChannelsPerFrame, mBitsPerChannel. `info`: u32 count + NUL-terminated key/value
UTF-8 pairs (title, artist, album, comments, copyright, encoding application, recorded date, ...).
codec_name follows ffmpeg libavformat/caf.c + cafdec.c: `lpcm` -> ff_mov_get_lpcm_codec_id(bits, (flags ^ 2) | 4)
(flag bit0 float, bit1 little-endian -> pcm_s16le / pcm_s24be / pcm_f32le ...), else ff_codec_caf_tags (`aac ` aac,
`alac` alac, `ulaw` pcm_mulaw, `alaw` pcm_alaw, `ima4` adpcm_ima_qt, `opus` opus, `.mp3` mp3, ...). format_name =
ffprobe's `caf`. Non-CAF member -> "none"; unreadable -> None. Fixtures: ffmpeg 7.0.2 writer, ffmpeg -i / mediainfo."""
import struct

from ..spell import Hex

FIELDS = {
    ("caf", "primary_audio_codec_name"): "caf_value",
    ("caf", "primary_audio_codec"): "caf_value",
    ("caf", "audio_codec_name"): "caf_value",
    ("caf", "audio_codec"): "caf_value",
    ("caf", "codec_name"): "caf_value",
    ("caf", "first_audio_codec_name"): "caf_value",
    ("caf", "actual_audio_codec_name"): "caf_value",
    ("caf", "primary_audio_sample_rate"): "caf_value",
    ("caf", "primary_audio_sample_rate_hz"): "caf_value",
    ("caf", "audio_sample_rate"): "caf_value",
    ("caf", "sample_rate"): "caf_value",
    ("caf", "sample_rate_hz"): "caf_value",
    ("caf", "desc_sample_rate"): "caf_value",
    ("caf", "primary_audio_channels"): "caf_value",
    ("caf", "primary_audio_channel_count"): "caf_value",
    ("caf", "audio_channels"): "caf_value",
    ("caf", "channels"): "caf_value",
    ("caf", "channel_count"): "caf_value",
    ("caf", "channels_per_frame"): "caf_value",
    ("caf", "desc_channels_per_frame"): "caf_value",
    ("caf", "bits_per_channel"): "caf_value",
    ("caf", "desc_bits_per_channel"): "caf_value",
    ("caf", "primary_audio_bits_per_sample"): "caf_value",
    ("caf", "bits_per_sample"): "caf_value",
    ("caf", "format_id"): "caf_value",
    ("caf", "desc_format_id"): "caf_value",
    ("caf", "primary_audio_codec_tag_string"): "caf_value",
    ("caf", "codec_tag_string"): "caf_value",
    ("caf", "format_flags"): "caf_value",
    ("caf", "desc_format_flags"): "caf_value",
    ("caf", "format_flags_u32_hex"): "caf_value",
    ("caf", "desc_format_flags_u32_hex"): "caf_value",
    ("caf", "bytes_per_packet"): "caf_value",
    ("caf", "desc_bytes_per_packet"): "caf_value",
    ("caf", "frames_per_packet"): "caf_value",
    ("caf", "desc_frames_per_packet"): "caf_value",
    ("caf", "container_format"): "caf_value",
    ("caf", "format_name"): "caf_value",
    ("caf", "container_format_name"): "caf_value",
    ("caf", "container"): "caf_value",
    ("caf", "container_name"): "caf_value",
    ("caf", "detected_container_format"): "caf_value",
    ("caf", "file_version"): "caf_value",
    ("caf", "version"): "caf_value",
    ("caf", "chunk_ids"): "caf_value",
    ("caf", "chunk_types"): "caf_value",
    ("caf", "chunk_list"): "caf_value",
    ("caf", "info_keys"): "caf_value",
    ("caf", "info_tag_keys"): "caf_value",
    ("caf", "info_entry_count"): "caf_value",
    ("caf", "info_num_entries"): "caf_value",
    ("caf", "title"): "caf_value",
    ("caf", "artist"): "caf_value",
    ("caf", "album"): "caf_value",
    ("caf", "comments"): "caf_value",
    ("caf", "comment"): "caf_value",
    ("caf", "copyright"): "caf_value",
    ("caf", "encoding_application"): "caf_value",
    ("caf", "encoder"): "caf_value",
    ("caf", "recorded_date"): "caf_value",
    ("caf", "year"): "caf_value",
    ("caf", "genre"): "caf_value",
    ("caf", "info_*"): "caf_value",
}

_KEYS = {
    "primary_audio_codec_name": "codec",
    "primary_audio_codec": "codec",
    "audio_codec_name": "codec",
    "audio_codec": "codec",
    "codec_name": "codec",
    "first_audio_codec_name": "codec",
    "actual_audio_codec_name": "codec",
    "primary_audio_sample_rate": "rate",
    "primary_audio_sample_rate_hz": "rate",
    "audio_sample_rate": "rate",
    "sample_rate": "rate",
    "sample_rate_hz": "rate",
    "desc_sample_rate": "rate",
    "primary_audio_channels": "channels",
    "primary_audio_channel_count": "channels",
    "audio_channels": "channels",
    "channels": "channels",
    "channel_count": "channels",
    "channels_per_frame": "channels",
    "desc_channels_per_frame": "channels",
    "bits_per_channel": "bits",
    "desc_bits_per_channel": "bits",
    "primary_audio_bits_per_sample": "bits",
    "bits_per_sample": "bits",
    "format_id": "fmtid",
    "desc_format_id": "fmtid",
    "primary_audio_codec_tag_string": "fmtid",
    "codec_tag_string": "fmtid",
    "format_flags": "flags",
    "desc_format_flags": "flags",
    "format_flags_u32_hex": "flags_hex",
    "desc_format_flags_u32_hex": "flags_hex",
    "bytes_per_packet": "bpp",
    "desc_bytes_per_packet": "bpp",
    "frames_per_packet": "fpp",
    "desc_frames_per_packet": "fpp",
    "container_format": "fmtname",
    "format_name": "fmtname",
    "container_format_name": "fmtname",
    "container": "fmtname",
    "container_name": "fmtname",
    "detected_container_format": "fmtname",
    "file_version": "version",
    "version": "version",
    "chunk_ids": "chunks",
    "chunk_types": "chunks",
    "chunk_list": "chunks",
    "info_keys": "infokeys",
    "info_tag_keys": "infokeys",
    "info_entry_count": "ninfo",
    "info_num_entries": "ninfo",
    "title": "info:title",
    "artist": "info:artist",
    "album": "info:album",
    "comments": "info:comments",
    "comment": "info:comments",
    "copyright": "info:copyright",
    "encoding_application": "info:encoding application",
    "encoder": "info:encoder",
    "recorded_date": "info:recorded date",
    "year": "info:year",
    "genre": "info:genre",
}
_TAGS = {b"aac ": "aac", b"alac": "alac", b"ulaw": "pcm_mulaw", b"alaw": "pcm_alaw", b"ima4": "adpcm_ima_qt",
         b"opus": "opus", b".mp3": "mp3", b".mp2": "mp2", b".mp1": "mp1", b"MAC3": "mace3", b"MAC6": "mace6",
         b"samr": "amr_nb", b"ilbc": "ilbc", b"QDM2": "qdm2", b"QDMC": "qdmc", b"Qclp": "qcelp", b"agsm": "gsm",
         b"ac-3": "ac3", b"ec-3": "eac3", b"flac": "flac"}


def parse(b):
    """{version, chunks[ids], desc{rate, fmtid, flags, bpp, fpp, channels, bits}, info{key: value}} or None."""
    if len(b) < 8 or b[:4] != b"caff":
        return None
    out = {"version": struct.unpack_from(">H", b, 4)[0], "chunks": [], "desc": None, "info": {}}
    i = 8
    while i + 12 <= len(b):
        cid, sz = b[i:i + 4], struct.unpack_from(">q", b, i + 4)[0]
        out["chunks"].append(cid.decode("latin-1"))
        body = b[i + 12:len(b) if sz < 0 else i + 12 + sz]
        if cid == b"desc" and len(body) >= 32:
            rate, = struct.unpack_from(">d", body, 0)
            flags, bpp, fpp, ch, bits = struct.unpack_from(">5I", body, 12)
            out["desc"] = {"rate": rate, "fmtid": body[8:12], "flags": flags, "bpp": bpp, "fpp": fpp,
                           "channels": ch, "bits": bits}
        elif cid == b"info" and len(body) >= 4:
            n = struct.unpack_from(">I", body, 0)[0]
            parts = body[4:].split(b"\x00")
            for k in range(min(n, len(parts) // 2)):
                key = parts[2 * k].decode("utf-8", "replace")
                out["info"].setdefault(key, parts[2 * k + 1].decode("utf-8", "replace"))
        if sz < 0:
            break
        i += 12 + sz
    return out


def codec_of(d):
    """ffmpeg codec_name of a parsed CAF desc chunk."""
    fid, bits, flags = d["fmtid"], d["bits"], d["flags"]
    if fid == b"lpcm":
        e = "le" if flags & 2 else "be"
        if flags & 1:
            return {32: "pcm_f32", 64: "pcm_f64"}.get(bits, "pcm_f32") + e if bits in (32, 64) else None
        if bits == 8:
            return "pcm_s8"
        return "pcm_s%d%s" % (bits, e) if bits in (16, 24, 32) else None
    return _TAGS.get(fid)


def _norm(s):
    return "".join(c for c in s.lower() if c.isalnum())


def caf_value(data, ctx):
    if not data:
        return None
    try:
        b = bytes(data)
        p = parse(b)
        if p is None:
            return "none"   # not a CAF member (renamed impostor): the field is absent
        field = (ctx or {}).get("field") or ""
        if field == "info_*":
            want = _norm((ctx or {}).get("param") or "")
            v = next((x for k, x in p["info"].items() if _norm(k) == want), None) if want else None
            return v if v else "none"
        key = _KEYS.get(field)
        if key is None:
            return None
        if key.startswith("info:"):
            v = next((x for k, x in p["info"].items() if k.lower() == key[5:]), None)
            return v if v else "none"
        if key == "fmtname":
            return "caf"
        if key == "version":
            return p["version"]
        if key == "chunks":
            return p["chunks"]
        if key == "infokeys":
            return list(p["info"])
        if key == "ninfo":
            return len(p["info"])
        d = p["desc"]
        if d is None:
            return None
        if key == "codec":
            return codec_of(d)
        if key == "rate":
            r = d["rate"]
            return int(r) if r == int(r) else r
        if key == "fmtid":
            return d["fmtid"].decode("latin-1")
        if key == "flags_hex":
            return Hex(d["flags"], 8)
        return d[key]
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None
