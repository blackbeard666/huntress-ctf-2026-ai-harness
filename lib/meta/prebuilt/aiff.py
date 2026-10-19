"""AIFF / AIFC and Sun AU (.snd) fields under their own fmt tokens -- prebuilt, SPECULATIVE (never asked yet).

The `media.*` namespace (prebuilt media.py) already reads both containers; this module answers when the GM files the
member under `aiff` / `aifc` / `au` / `snd` instead, and adds the container-specific structure fields.
AIFF: `FORM` size `AIFF`|`AIFC`, chunks id[4] u32 size (big-endian, pad to even). COMM = i16 numChannels,
u32 numSampleFrames, i16 sampleSize, 80-bit IEEE extended sampleRate, AIFC + compressionType[4] + pstring
compressionName. codec_name = ffmpeg aiffdec.c ff_codec_aiff_tags (NONE/twos -> pcm_sNNbe, sowt -> pcm_sNNle,
fl32 -> pcm_f32be, ulaw/ULAW -> pcm_mulaw, alaw/ALAW -> pcm_alaw, ima4 -> adpcm_ima_qt, raw -> pcm_u8). NAME/AUTH/
ANNO/`(c) ` text chunks. format_name = ffprobe `aiff`.
AU: `.snd` u32 data offset, data size, encoding (1 mulaw, 2 s8, 3 s16be, 4 s24be, 5 s32be, 6 f32be, 7 f64be,
27 alaw), sample rate, channels; annotation = bytes 24..offset (NUL-trimmed). format_name = ffprobe `au`.
Wrong-magic member -> "none"; unreadable -> None. Fixtures: ffmpeg 7.0.2 writer, ffmpeg -i / exiftool readers."""
import struct

FIELDS = {
    ("aiff", "primary_audio_codec_name"): "aiff_value",
    ("aiff", "primary_audio_codec"): "aiff_value",
    ("aiff", "audio_codec_name"): "aiff_value",
    ("aiff", "audio_codec"): "aiff_value",
    ("aiff", "codec_name"): "aiff_value",
    ("aiff", "first_audio_codec_name"): "aiff_value",
    ("aiff", "actual_audio_codec_name"): "aiff_value",
    ("aiff", "primary_audio_sample_rate"): "aiff_value",
    ("aiff", "primary_audio_sample_rate_hz"): "aiff_value",
    ("aiff", "audio_sample_rate"): "aiff_value",
    ("aiff", "sample_rate"): "aiff_value",
    ("aiff", "sample_rate_hz"): "aiff_value",
    ("aiff", "comm_sample_rate"): "aiff_value",
    ("aiff", "primary_audio_channels"): "aiff_value",
    ("aiff", "primary_audio_channel_count"): "aiff_value",
    ("aiff", "audio_channels"): "aiff_value",
    ("aiff", "channels"): "aiff_value",
    ("aiff", "channel_count"): "aiff_value",
    ("aiff", "num_channels"): "aiff_value",
    ("aiff", "comm_num_channels"): "aiff_value",
    ("aiff", "comm_channels"): "aiff_value",
    ("aiff", "num_sample_frames"): "aiff_value",
    ("aiff", "comm_num_sample_frames"): "aiff_value",
    ("aiff", "sample_frames"): "aiff_value",
    ("aiff", "sample_size"): "aiff_value",
    ("aiff", "comm_sample_size"): "aiff_value",
    ("aiff", "bits_per_sample"): "aiff_value",
    ("aiff", "compression_type"): "aiff_value",
    ("aiff", "comm_compression_type"): "aiff_value",
    ("aiff", "compression_name"): "aiff_value",
    ("aiff", "comm_compression_name"): "aiff_value",
    ("aiff", "encoding"): "aiff_value",
    ("aiff", "au_encoding"): "aiff_value",
    ("aiff", "header_encoding"): "aiff_value",
    ("aiff", "data_offset"): "aiff_value",
    ("aiff", "header_data_offset"): "aiff_value",
    ("aiff", "data_size"): "aiff_value",
    ("aiff", "header_data_size"): "aiff_value",
    ("aiff", "annotation"): "aiff_value",
    ("aiff", "container_format"): "aiff_value",
    ("aiff", "format_name"): "aiff_value",
    ("aiff", "container_format_name"): "aiff_value",
    ("aiff", "container"): "aiff_value",
    ("aiff", "container_name"): "aiff_value",
    ("aiff", "detected_container_format"): "aiff_value",
    ("aiff", "name"): "aiff_value",
    ("aiff", "name_chunk"): "aiff_value",
    ("aiff", "title"): "aiff_value",
    ("aiff", "author"): "aiff_value",
    ("aiff", "auth_chunk"): "aiff_value",
    ("aiff", "artist"): "aiff_value",
    ("aiff", "anno"): "aiff_value",
    ("aiff", "anno_chunk"): "aiff_value",
    ("aiff", "comment"): "aiff_value",
    ("aiff", "copyright"): "aiff_value",
    ("aiff", "chunk_ids"): "aiff_value",
    ("aiff", "chunk_list"): "aiff_value",
    ("aiff", "form_type"): "aiff_value",
    ("aifc", "primary_audio_codec_name"): "aiff_value",
    ("aifc", "primary_audio_codec"): "aiff_value",
    ("aifc", "audio_codec_name"): "aiff_value",
    ("aifc", "audio_codec"): "aiff_value",
    ("aifc", "codec_name"): "aiff_value",
    ("aifc", "first_audio_codec_name"): "aiff_value",
    ("aifc", "actual_audio_codec_name"): "aiff_value",
    ("aifc", "primary_audio_sample_rate"): "aiff_value",
    ("aifc", "primary_audio_sample_rate_hz"): "aiff_value",
    ("aifc", "audio_sample_rate"): "aiff_value",
    ("aifc", "sample_rate"): "aiff_value",
    ("aifc", "sample_rate_hz"): "aiff_value",
    ("aifc", "comm_sample_rate"): "aiff_value",
    ("aifc", "primary_audio_channels"): "aiff_value",
    ("aifc", "primary_audio_channel_count"): "aiff_value",
    ("aifc", "audio_channels"): "aiff_value",
    ("aifc", "channels"): "aiff_value",
    ("aifc", "channel_count"): "aiff_value",
    ("aifc", "num_channels"): "aiff_value",
    ("aifc", "comm_num_channels"): "aiff_value",
    ("aifc", "comm_channels"): "aiff_value",
    ("aifc", "num_sample_frames"): "aiff_value",
    ("aifc", "comm_num_sample_frames"): "aiff_value",
    ("aifc", "sample_frames"): "aiff_value",
    ("aifc", "sample_size"): "aiff_value",
    ("aifc", "comm_sample_size"): "aiff_value",
    ("aifc", "bits_per_sample"): "aiff_value",
    ("aifc", "compression_type"): "aiff_value",
    ("aifc", "comm_compression_type"): "aiff_value",
    ("aifc", "compression_name"): "aiff_value",
    ("aifc", "comm_compression_name"): "aiff_value",
    ("aifc", "encoding"): "aiff_value",
    ("aifc", "au_encoding"): "aiff_value",
    ("aifc", "header_encoding"): "aiff_value",
    ("aifc", "data_offset"): "aiff_value",
    ("aifc", "header_data_offset"): "aiff_value",
    ("aifc", "data_size"): "aiff_value",
    ("aifc", "header_data_size"): "aiff_value",
    ("aifc", "annotation"): "aiff_value",
    ("aifc", "container_format"): "aiff_value",
    ("aifc", "format_name"): "aiff_value",
    ("aifc", "container_format_name"): "aiff_value",
    ("aifc", "container"): "aiff_value",
    ("aifc", "container_name"): "aiff_value",
    ("aifc", "detected_container_format"): "aiff_value",
    ("aifc", "name"): "aiff_value",
    ("aifc", "name_chunk"): "aiff_value",
    ("aifc", "title"): "aiff_value",
    ("aifc", "author"): "aiff_value",
    ("aifc", "auth_chunk"): "aiff_value",
    ("aifc", "artist"): "aiff_value",
    ("aifc", "anno"): "aiff_value",
    ("aifc", "anno_chunk"): "aiff_value",
    ("aifc", "comment"): "aiff_value",
    ("aifc", "copyright"): "aiff_value",
    ("aifc", "chunk_ids"): "aiff_value",
    ("aifc", "chunk_list"): "aiff_value",
    ("aifc", "form_type"): "aiff_value",
    ("au", "primary_audio_codec_name"): "aiff_value",
    ("au", "primary_audio_codec"): "aiff_value",
    ("au", "audio_codec_name"): "aiff_value",
    ("au", "audio_codec"): "aiff_value",
    ("au", "codec_name"): "aiff_value",
    ("au", "first_audio_codec_name"): "aiff_value",
    ("au", "actual_audio_codec_name"): "aiff_value",
    ("au", "primary_audio_sample_rate"): "aiff_value",
    ("au", "primary_audio_sample_rate_hz"): "aiff_value",
    ("au", "audio_sample_rate"): "aiff_value",
    ("au", "sample_rate"): "aiff_value",
    ("au", "sample_rate_hz"): "aiff_value",
    ("au", "comm_sample_rate"): "aiff_value",
    ("au", "primary_audio_channels"): "aiff_value",
    ("au", "primary_audio_channel_count"): "aiff_value",
    ("au", "audio_channels"): "aiff_value",
    ("au", "channels"): "aiff_value",
    ("au", "channel_count"): "aiff_value",
    ("au", "num_channels"): "aiff_value",
    ("au", "comm_num_channels"): "aiff_value",
    ("au", "comm_channels"): "aiff_value",
    ("au", "num_sample_frames"): "aiff_value",
    ("au", "comm_num_sample_frames"): "aiff_value",
    ("au", "sample_frames"): "aiff_value",
    ("au", "sample_size"): "aiff_value",
    ("au", "comm_sample_size"): "aiff_value",
    ("au", "bits_per_sample"): "aiff_value",
    ("au", "compression_type"): "aiff_value",
    ("au", "comm_compression_type"): "aiff_value",
    ("au", "compression_name"): "aiff_value",
    ("au", "comm_compression_name"): "aiff_value",
    ("au", "encoding"): "aiff_value",
    ("au", "au_encoding"): "aiff_value",
    ("au", "header_encoding"): "aiff_value",
    ("au", "data_offset"): "aiff_value",
    ("au", "header_data_offset"): "aiff_value",
    ("au", "data_size"): "aiff_value",
    ("au", "header_data_size"): "aiff_value",
    ("au", "annotation"): "aiff_value",
    ("au", "container_format"): "aiff_value",
    ("au", "format_name"): "aiff_value",
    ("au", "container_format_name"): "aiff_value",
    ("au", "container"): "aiff_value",
    ("au", "container_name"): "aiff_value",
    ("au", "detected_container_format"): "aiff_value",
    ("au", "name"): "aiff_value",
    ("au", "name_chunk"): "aiff_value",
    ("au", "title"): "aiff_value",
    ("au", "author"): "aiff_value",
    ("au", "auth_chunk"): "aiff_value",
    ("au", "artist"): "aiff_value",
    ("au", "anno"): "aiff_value",
    ("au", "anno_chunk"): "aiff_value",
    ("au", "comment"): "aiff_value",
    ("au", "copyright"): "aiff_value",
    ("au", "chunk_ids"): "aiff_value",
    ("au", "chunk_list"): "aiff_value",
    ("au", "form_type"): "aiff_value",
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
    "comm_sample_rate": "rate",
    "primary_audio_channels": "channels",
    "primary_audio_channel_count": "channels",
    "audio_channels": "channels",
    "channels": "channels",
    "channel_count": "channels",
    "num_channels": "channels",
    "comm_num_channels": "channels",
    "comm_channels": "channels",
    "num_sample_frames": "frames",
    "comm_num_sample_frames": "frames",
    "sample_frames": "frames",
    "sample_size": "bits",
    "comm_sample_size": "bits",
    "bits_per_sample": "bits",
    "compression_type": "ctype",
    "comm_compression_type": "ctype",
    "compression_name": "cname",
    "comm_compression_name": "cname",
    "encoding": "enc",
    "au_encoding": "enc",
    "header_encoding": "enc",
    "data_offset": "off",
    "header_data_offset": "off",
    "data_size": "dsize",
    "header_data_size": "dsize",
    "annotation": "anno",
    "container_format": "fmtname",
    "format_name": "fmtname",
    "container_format_name": "fmtname",
    "container": "fmtname",
    "container_name": "fmtname",
    "detected_container_format": "fmtname",
    "name": "NAME",
    "name_chunk": "NAME",
    "title": "NAME",
    "author": "AUTH",
    "auth_chunk": "AUTH",
    "artist": "AUTH",
    "anno": "ANNO",
    "anno_chunk": "ANNO",
    "comment": "ANNO",
    "copyright": "(c) ",
    "chunk_ids": "chunks",
    "chunk_list": "chunks",
    "form_type": "formtype",
}
_AIFC = {b"NONE": "be", b"twos": "be", b"sowt": "le", b"fl32": "pcm_f32be", b"FL32": "pcm_f32be",
         b"fl64": "pcm_f64be", b"FL64": "pcm_f64be", b"ulaw": "pcm_mulaw", b"ULAW": "pcm_mulaw",
         b"alaw": "pcm_alaw", b"ALAW": "pcm_alaw", b"ima4": "adpcm_ima_qt", b"raw ": "pcm_u8", b"in24": "pcm_s24be",
         b"42ni": "pcm_s24le", b"in32": "pcm_s32be", b"23ni": "pcm_s32le", b"MAC3": "mace3", b"MAC6": "mace6",
         b"GSM ": "gsm", b"QDM2": "qdm2", b"QDMC": "qdmc", b"QCLP": "qcelp"}
_AU = {1: "pcm_mulaw", 2: "pcm_s8", 3: "pcm_s16be", 4: "pcm_s24be", 5: "pcm_s32be", 6: "pcm_f32be", 7: "pcm_f64be",
       27: "pcm_alaw"}


def _f80(x):
    exp = ((x[0] & 0x7F) << 8 | x[1]) - 16383 - 63
    mant = int.from_bytes(x[2:10], "big")
    return int(mant * 2.0 ** exp) if mant else 0


def _txt(raw):
    return raw.split(b"\x00", 1)[0].decode("latin-1").strip()


def parse_aiff(b):
    if len(b) < 12 or b[:4] != b"FORM" or b[8:12] not in (b"AIFF", b"AIFC"):
        return None
    out = {"fmtname": "aiff", "formtype": b[8:12].decode(), "chunks": []}
    i = 12
    while i + 8 <= len(b):
        cid, ln = b[i:i + 4], struct.unpack_from(">I", b, i + 4)[0]
        body = b[i + 8:i + 8 + ln]
        out["chunks"].append(cid.decode("latin-1"))
        if cid == b"COMM" and len(body) >= 18 and "channels" not in out:
            ch, frames, bits = struct.unpack_from(">hIh", body, 0)
            out.update(channels=ch, frames=frames, bits=bits, rate=_f80(body[8:18]))
            ct = body[18:22] if out["formtype"] == "AIFC" and len(body) >= 22 else b"NONE"
            out["ctype"] = ct.decode("latin-1")
            if len(body) > 22:
                out["cname"] = body[23:23 + body[22]].decode("latin-1")
            c = _AIFC.get(ct)
            if c in ("be", "le"):
                c = "pcm_s8" if bits <= 8 else "pcm_s%d%s" % ((bits + 7) // 8 * 8, c)
            out["codec"] = c
        elif cid in (b"NAME", b"AUTH", b"ANNO", b"(c) ") and cid.decode("latin-1") not in out:
            out[cid.decode("latin-1")] = _txt(body)
        i += 8 + ln + (ln & 1)
    return out


def parse_au(b):
    if len(b) < 24 or b[:4] != b".snd":
        return None
    off, size, enc, rate, ch = struct.unpack_from(">5I", b, 4)
    return {"fmtname": "au", "off": off, "dsize": size, "enc": enc, "rate": rate, "channels": ch,
            "codec": _AU.get(enc), "anno": _txt(b[24:off]) if off > 24 else ""}


def aiff_value(data, ctx):
    if not data:
        return None
    try:
        b = bytes(data)
        p = parse_aiff(b) or parse_au(b)
        if p is None:
            return "none"   # neither AIFF nor AU (renamed impostor): the field is absent
        key = _KEYS.get((ctx or {}).get("field") or "")
        if key is None:
            return None
        v = p.get(key)
        if v is None or v == "":
            return "none" if key in ("NAME", "AUTH", "ANNO", "(c) ", "anno", "cname", "ctype", "enc", "off",
                                     "dsize", "frames", "chunks", "formtype") else None
        return v
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None
