"""ASF / WMA (Advanced Systems Format) fields -- prebuilt, SPECULATIVE (never asked yet).

Routed by MAGIC: the ASF Header Object GUID 75B22630-668E-11CF-A6D9-00AA0062CE6C (on disk 30 26 b2 75 8e 66 cf 11 ...),
never the extension. Header Object = GUID(16) size(u64) n_objects(u32) reserved(2), then sub-objects GUID(16) size(u64):
  File Properties     8CABDCA1-A947-11CF-8EE4-00C00C205365: file id, file size, creation date (FILETIME), data packets,
                      play duration (100 ns), send duration, preroll (ms), flags, min/max packet, max bitrate
  Stream Properties   B7DC0791-A9B7-11CF-8EE6-00C00C205365: stream type (audio F8699E40-...), then WAVEFORMATEX
                      (wFormatTag, nChannels, nSamplesPerSec, nAvgBytesPerSec, nBlockAlign, wBitsPerSample)
  Content Description 75B22633-668E-11CF-A6D9-00AA0062CE6C: title / author / copyright / description / rating (UTF-16LE)
  Extended Content    D2D0A440-E307-11D2-97F0-00A0C95EA850: name/value attributes (WM/AlbumTitle, WM/EncodingSettings)
codec_name = ffmpeg riff.c ff_codec_wav_tags of wFormatTag (0x160 wmav1, 0x161 wmav2, 0x162 wmapro, 0x163 wmalossless,
0x0A wmavoice, 1 -> pcm by bits). format_name = ffprobe's `asf`. A non-ASF member (renamed impostor) -> "none" for the
content fields; unreadable -> None. Fixtures: ffmpeg 7.0.2 writer, ffmpeg -i / exiftool readers."""
import struct
from datetime import datetime, timedelta, timezone

from ..spell import Hex

_F = ("asf", "wma")
_KEYS = {
    "primary_audio_codec_name": "codec", "primary_audio_codec": "codec", "audio_codec_name": "codec",
    "audio_codec": "codec", "codec_name": "codec", "first_audio_codec_name": "codec",
    "audio_stream_codec_name": "codec", "actual_audio_codec_name": "codec",
    "primary_audio_sample_rate": "rate", "primary_audio_sample_rate_hz": "rate", "audio_sample_rate": "rate",
    "sample_rate": "rate", "sample_rate_hz": "rate", "samples_per_sec": "rate",
    "primary_audio_channels": "channels", "primary_audio_channel_count": "channels", "audio_channels": "channels",
    "channels": "channels", "channel_count": "channels", "num_channels": "channels",
    "primary_audio_bits_per_sample": "bits", "bits_per_sample": "bits", "audio_bits_per_sample": "bits",
    "primary_audio_codec_tag_hex": "tag", "codec_tag_hex": "tag", "audio_codec_tag_hex": "tag",
    "format_tag_u16_hex": "tag", "wave_format_tag_u16_hex": "tag", "waveformatex_format_tag_u16_hex": "tag",
    "audio_format_tag_u16_hex": "tag", "w_format_tag_u16_hex": "tag", "format_tag": "tag_int",
    "audio_format": "tag_int", "avg_bytes_per_sec": "avg", "block_align": "align",
    "container_format": "fmtname", "format_name": "fmtname", "container_format_name": "fmtname",
    "container": "fmtname", "container_name": "fmtname", "detected_container_format": "fmtname",
    "title": "title", "author": "author", "artist": "author", "copyright": "copyright", "description": "description",
    "comment": "description", "rating": "rating",
    "content_description_title": "title", "content_description_author": "author",
    "content_description_copyright": "copyright", "content_description_description": "description",
    "content_description_rating": "rating",
    "creation_date": "created", "creation_date_utc": "created", "creation_time_utc": "created",
    "file_properties_creation_date": "created", "file_properties_creation_date_utc": "created",
    "creation_date_filetime": "created_raw", "file_properties_creation_date_filetime": "created_raw",
    "play_duration": "play", "file_properties_play_duration": "play",
    "send_duration": "send", "file_properties_send_duration": "send",
    "preroll": "preroll", "preroll_ms": "preroll", "file_properties_preroll": "preroll",
    "data_packets": "packets", "data_packets_count": "packets", "file_properties_data_packets_count": "packets",
    "max_bitrate": "maxbr", "file_properties_max_bitrate": "maxbr", "file_size": "fsize",
    "file_properties_file_size": "fsize", "file_id_guid": "fileid", "file_properties_file_id_guid": "fileid",
    "stream_count": "nstreams", "nb_streams": "nstreams", "number_of_streams": "nstreams",
    "audio_stream_count": "naudio", "nb_audio_streams": "naudio", "header_object_count": "nobj",
    "header_objects_count": "nobj", "extended_content_names": "extnames", "extended_content_descriptor_names": "extnames",
}
FIELDS = {
    ("asf", "primary_audio_codec_name"): "asf_value",
    ("asf", "primary_audio_codec"): "asf_value",
    ("asf", "audio_codec_name"): "asf_value",
    ("asf", "audio_codec"): "asf_value",
    ("asf", "codec_name"): "asf_value",
    ("asf", "first_audio_codec_name"): "asf_value",
    ("asf", "audio_stream_codec_name"): "asf_value",
    ("asf", "actual_audio_codec_name"): "asf_value",
    ("asf", "primary_audio_sample_rate"): "asf_value",
    ("asf", "primary_audio_sample_rate_hz"): "asf_value",
    ("asf", "audio_sample_rate"): "asf_value",
    ("asf", "sample_rate"): "asf_value",
    ("asf", "sample_rate_hz"): "asf_value",
    ("asf", "samples_per_sec"): "asf_value",
    ("asf", "primary_audio_channels"): "asf_value",
    ("asf", "primary_audio_channel_count"): "asf_value",
    ("asf", "audio_channels"): "asf_value",
    ("asf", "channels"): "asf_value",
    ("asf", "channel_count"): "asf_value",
    ("asf", "num_channels"): "asf_value",
    ("asf", "primary_audio_bits_per_sample"): "asf_value",
    ("asf", "bits_per_sample"): "asf_value",
    ("asf", "audio_bits_per_sample"): "asf_value",
    ("asf", "primary_audio_codec_tag_hex"): "asf_value",
    ("asf", "codec_tag_hex"): "asf_value",
    ("asf", "audio_codec_tag_hex"): "asf_value",
    ("asf", "format_tag_u16_hex"): "asf_value",
    ("asf", "wave_format_tag_u16_hex"): "asf_value",
    ("asf", "waveformatex_format_tag_u16_hex"): "asf_value",
    ("asf", "audio_format_tag_u16_hex"): "asf_value",
    ("asf", "w_format_tag_u16_hex"): "asf_value",
    ("asf", "format_tag"): "asf_value",
    ("asf", "audio_format"): "asf_value",
    ("asf", "avg_bytes_per_sec"): "asf_value",
    ("asf", "block_align"): "asf_value",
    ("asf", "container_format"): "asf_value",
    ("asf", "format_name"): "asf_value",
    ("asf", "container_format_name"): "asf_value",
    ("asf", "container"): "asf_value",
    ("asf", "container_name"): "asf_value",
    ("asf", "detected_container_format"): "asf_value",
    ("asf", "title"): "asf_value",
    ("asf", "author"): "asf_value",
    ("asf", "artist"): "asf_value",
    ("asf", "copyright"): "asf_value",
    ("asf", "description"): "asf_value",
    ("asf", "comment"): "asf_value",
    ("asf", "rating"): "asf_value",
    ("asf", "content_description_title"): "asf_value",
    ("asf", "content_description_author"): "asf_value",
    ("asf", "content_description_copyright"): "asf_value",
    ("asf", "content_description_description"): "asf_value",
    ("asf", "content_description_rating"): "asf_value",
    ("asf", "creation_date"): "asf_value",
    ("asf", "creation_date_utc"): "asf_value",
    ("asf", "creation_time_utc"): "asf_value",
    ("asf", "file_properties_creation_date"): "asf_value",
    ("asf", "file_properties_creation_date_utc"): "asf_value",
    ("asf", "creation_date_filetime"): "asf_value",
    ("asf", "file_properties_creation_date_filetime"): "asf_value",
    ("asf", "play_duration"): "asf_value",
    ("asf", "file_properties_play_duration"): "asf_value",
    ("asf", "send_duration"): "asf_value",
    ("asf", "file_properties_send_duration"): "asf_value",
    ("asf", "preroll"): "asf_value",
    ("asf", "preroll_ms"): "asf_value",
    ("asf", "file_properties_preroll"): "asf_value",
    ("asf", "data_packets"): "asf_value",
    ("asf", "data_packets_count"): "asf_value",
    ("asf", "file_properties_data_packets_count"): "asf_value",
    ("asf", "max_bitrate"): "asf_value",
    ("asf", "file_properties_max_bitrate"): "asf_value",
    ("asf", "file_size"): "asf_value",
    ("asf", "file_properties_file_size"): "asf_value",
    ("asf", "file_id_guid"): "asf_value",
    ("asf", "file_properties_file_id_guid"): "asf_value",
    ("asf", "stream_count"): "asf_value",
    ("asf", "nb_streams"): "asf_value",
    ("asf", "number_of_streams"): "asf_value",
    ("asf", "audio_stream_count"): "asf_value",
    ("asf", "nb_audio_streams"): "asf_value",
    ("asf", "header_object_count"): "asf_value",
    ("asf", "header_objects_count"): "asf_value",
    ("asf", "extended_content_names"): "asf_value",
    ("asf", "extended_content_descriptor_names"): "asf_value",
    ("asf", "extended_content_*"): "asf_value",
    ("asf", "wm_*"): "asf_value",
    ("wma", "primary_audio_codec_name"): "asf_value",
    ("wma", "primary_audio_codec"): "asf_value",
    ("wma", "audio_codec_name"): "asf_value",
    ("wma", "audio_codec"): "asf_value",
    ("wma", "codec_name"): "asf_value",
    ("wma", "first_audio_codec_name"): "asf_value",
    ("wma", "audio_stream_codec_name"): "asf_value",
    ("wma", "actual_audio_codec_name"): "asf_value",
    ("wma", "primary_audio_sample_rate"): "asf_value",
    ("wma", "primary_audio_sample_rate_hz"): "asf_value",
    ("wma", "audio_sample_rate"): "asf_value",
    ("wma", "sample_rate"): "asf_value",
    ("wma", "sample_rate_hz"): "asf_value",
    ("wma", "samples_per_sec"): "asf_value",
    ("wma", "primary_audio_channels"): "asf_value",
    ("wma", "primary_audio_channel_count"): "asf_value",
    ("wma", "audio_channels"): "asf_value",
    ("wma", "channels"): "asf_value",
    ("wma", "channel_count"): "asf_value",
    ("wma", "num_channels"): "asf_value",
    ("wma", "primary_audio_bits_per_sample"): "asf_value",
    ("wma", "bits_per_sample"): "asf_value",
    ("wma", "audio_bits_per_sample"): "asf_value",
    ("wma", "primary_audio_codec_tag_hex"): "asf_value",
    ("wma", "codec_tag_hex"): "asf_value",
    ("wma", "audio_codec_tag_hex"): "asf_value",
    ("wma", "format_tag_u16_hex"): "asf_value",
    ("wma", "wave_format_tag_u16_hex"): "asf_value",
    ("wma", "waveformatex_format_tag_u16_hex"): "asf_value",
    ("wma", "audio_format_tag_u16_hex"): "asf_value",
    ("wma", "w_format_tag_u16_hex"): "asf_value",
    ("wma", "format_tag"): "asf_value",
    ("wma", "audio_format"): "asf_value",
    ("wma", "avg_bytes_per_sec"): "asf_value",
    ("wma", "block_align"): "asf_value",
    ("wma", "container_format"): "asf_value",
    ("wma", "format_name"): "asf_value",
    ("wma", "container_format_name"): "asf_value",
    ("wma", "container"): "asf_value",
    ("wma", "container_name"): "asf_value",
    ("wma", "detected_container_format"): "asf_value",
    ("wma", "title"): "asf_value",
    ("wma", "author"): "asf_value",
    ("wma", "artist"): "asf_value",
    ("wma", "copyright"): "asf_value",
    ("wma", "description"): "asf_value",
    ("wma", "comment"): "asf_value",
    ("wma", "rating"): "asf_value",
    ("wma", "content_description_title"): "asf_value",
    ("wma", "content_description_author"): "asf_value",
    ("wma", "content_description_copyright"): "asf_value",
    ("wma", "content_description_description"): "asf_value",
    ("wma", "content_description_rating"): "asf_value",
    ("wma", "creation_date"): "asf_value",
    ("wma", "creation_date_utc"): "asf_value",
    ("wma", "creation_time_utc"): "asf_value",
    ("wma", "file_properties_creation_date"): "asf_value",
    ("wma", "file_properties_creation_date_utc"): "asf_value",
    ("wma", "creation_date_filetime"): "asf_value",
    ("wma", "file_properties_creation_date_filetime"): "asf_value",
    ("wma", "play_duration"): "asf_value",
    ("wma", "file_properties_play_duration"): "asf_value",
    ("wma", "send_duration"): "asf_value",
    ("wma", "file_properties_send_duration"): "asf_value",
    ("wma", "preroll"): "asf_value",
    ("wma", "preroll_ms"): "asf_value",
    ("wma", "file_properties_preroll"): "asf_value",
    ("wma", "data_packets"): "asf_value",
    ("wma", "data_packets_count"): "asf_value",
    ("wma", "file_properties_data_packets_count"): "asf_value",
    ("wma", "max_bitrate"): "asf_value",
    ("wma", "file_properties_max_bitrate"): "asf_value",
    ("wma", "file_size"): "asf_value",
    ("wma", "file_properties_file_size"): "asf_value",
    ("wma", "file_id_guid"): "asf_value",
    ("wma", "file_properties_file_id_guid"): "asf_value",
    ("wma", "stream_count"): "asf_value",
    ("wma", "nb_streams"): "asf_value",
    ("wma", "number_of_streams"): "asf_value",
    ("wma", "audio_stream_count"): "asf_value",
    ("wma", "nb_audio_streams"): "asf_value",
    ("wma", "header_object_count"): "asf_value",
    ("wma", "header_objects_count"): "asf_value",
    ("wma", "extended_content_names"): "asf_value",
    ("wma", "extended_content_descriptor_names"): "asf_value",
    ("wma", "extended_content_*"): "asf_value",
    ("wma", "wm_*"): "asf_value",
}


def _g(s):
    """On-disk (little-endian Windows GUID) bytes of a canonical GUID string."""
    import uuid
    return uuid.UUID(s).bytes_le


_HDR = b"\x30\x26\xb2\x75\x8e\x66\xcf\x11\xa6\xd9\x00\xaa\x00\x62\xce\x6c"
_FILE_PROPS = "8cabdca1-a947-11cf-8ee4-00c00c205365"
_STREAM_PROPS = "b7dc0791-a9b7-11cf-8ee6-00c00c205365"
_CONTENT = "75b22633-668e-11cf-a6d9-00aa0062ce6c"
_EXT_CONTENT = "d2d0a440-e307-11d2-97f0-00a0c95ea850"
_AUDIO_MEDIA = "f8699e40-5b4d-11cf-a8fd-00805f5c442b"
# ffmpeg libavformat/riff.c ff_codec_wav_tags (the WAVEFORMATEX tags an ASF audio stream carries)
_TAGS = {0x0002: "adpcm_ms", 0x0006: "pcm_alaw", 0x0007: "pcm_mulaw", 0x000A: "wmavoice", 0x0011: "adpcm_ima_wav",
         0x0031: "gsm_ms", 0x0050: "mp2", 0x0055: "mp3", 0x0092: "ac3", 0x00FF: "aac", 0x1610: "aac",
         0x0160: "wmav1", 0x0161: "wmav2", 0x0162: "wmapro", 0x0163: "wmalossless", 0x2000: "ac3", 0x2001: "dts",
         0xF1AC: "flac", 0x0130: "sipr", 0x0022: "truespeech", 0x0045: "g726"}
_FT_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)


def _u16s(b):
    return b.decode("utf-16-le", "replace").split("\x00", 1)[0].strip()


def parse(b):
    """{objects, file, streams[{type, tag, channels, rate, avg, align, bits}], content{}, ext{}} of an ASF header,
    or None when the bytes are not ASF."""
    if len(b) < 30 or b[:16] != _HDR:
        return None
    hsize, nobj = struct.unpack_from("<QI", b, 16)
    end = min(len(b), hsize if hsize >= 30 else len(b))
    g = {k: _g(v) for k, v in (("fp", _FILE_PROPS), ("sp", _STREAM_PROPS), ("cd", _CONTENT), ("ecd", _EXT_CONTENT),
                               ("aud", _AUDIO_MEDIA))}
    out = {"objects": nobj, "file": {}, "streams": [], "content": {}, "ext": {}}
    i = 30
    while i + 24 <= end:
        gid, osz = b[i:i + 16], struct.unpack_from("<Q", b, i + 16)[0]
        if osz < 24:
            break
        body = b[i + 24:min(i + osz, len(b))]
        if gid == g["fp"] and len(body) >= 80:
            fid = body[:16]
            fsize, created, packets, play, send, preroll, flags, mn, mx, maxbr = struct.unpack_from(
                "<QQQQQQIIII", body, 16)
            out["file"] = {"fileid": fid, "fsize": fsize, "created": created, "packets": packets, "play": play,
                           "send": send, "preroll": preroll, "maxbr": maxbr}
        elif gid == g["sp"] and len(body) >= 54:
            st = {"type": "audio" if body[:16] == g["aud"] else "other"}
            tlen = struct.unpack_from("<I", body, 40)[0]
            ts = body[54:54 + tlen]
            if st["type"] == "audio" and len(ts) >= 16:
                tag, ch, rate, avg, align, bits = struct.unpack_from("<HHIIHH", ts, 0)
                st.update(tag=tag, channels=ch, rate=rate, avg=avg, align=align, bits=bits)
            out["streams"].append(st)
        elif gid == g["cd"] and len(body) >= 10:
            lens = struct.unpack_from("<5H", body, 0)
            p = 10
            for name, ln in zip(("title", "author", "copyright", "description", "rating"), lens):
                out["content"][name] = _u16s(body[p:p + ln])
                p += ln
        elif gid == g["ecd"] and len(body) >= 2:
            n, p = struct.unpack_from("<H", body, 0)[0], 2
            for _ in range(n):
                if p + 2 > len(body):
                    break
                nl = struct.unpack_from("<H", body, p)[0]
                name = _u16s(body[p + 2:p + 2 + nl])
                p += 2 + nl
                vt, vl = struct.unpack_from("<HH", body, p)
                raw = body[p + 4:p + 4 + vl]
                p += 4 + vl
                if vt == 0:
                    val = _u16s(raw)
                elif vt in (2, 3) and len(raw) >= 4:
                    val = struct.unpack_from("<I", raw)[0]
                    val = bool(val) if vt == 2 else val
                elif vt == 4 and len(raw) >= 8:
                    val = struct.unpack_from("<Q", raw)[0]
                elif vt == 5 and len(raw) >= 2:
                    val = struct.unpack_from("<H", raw)[0]
                else:
                    val = raw.hex()
                out["ext"].setdefault(name, val)
        i += osz
    return out


def codec_of(st):
    """ffmpeg codec_name of one parsed ASF audio stream (riff.c ff_wav_codec_get_id: PCM width from wBitsPerSample)."""
    tag, bits = st.get("tag"), st.get("bits") or 16
    if tag is None:
        return None
    if tag == 1:
        return "pcm_u8" if bits == 8 else "pcm_s%dle" % bits
    if tag == 3:
        return "pcm_f64le" if bits == 64 else "pcm_f32le"
    return _TAGS.get(tag)


def _norm(s):
    return "".join(c for c in s.lower() if c.isalnum())


def _filetime_utc(ft):
    # FILETIME = 100 ns ticks since 1601-01-01 UTC (ASF File Properties creation date); 0 = not set -> "none"
    if not ft:
        return "none"
    t = _FT_EPOCH + timedelta(microseconds=ft // 10)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def asf_value(data, ctx):
    if not data:
        return None
    try:
        b = bytes(data)
        p = parse(b)
        field = (ctx or {}).get("field") or ""
        if p is None:
            return "none"   # not an ASF member (renamed impostor): the field is absent
        if field.endswith("_*"):
            param = _norm((ctx or {}).get("param") or "")
            if not param:
                return None
            pre = "wm" if field.startswith("wm_") else ""
            for k, v in p["ext"].items():
                if _norm(k) in (param, pre + param):
                    return v
            return "none"
        key = _KEYS.get(field)
        aud = next((s for s in p["streams"] if s.get("type") == "audio" and "tag" in s), None)
        fp = p["file"]
        if key == "fmtname":
            return "asf"
        if key in ("codec", "rate", "channels", "bits", "tag", "tag_int", "avg", "align"):
            if aud is None:
                return "none"
            if key == "codec":
                return codec_of(aud)
            if key == "tag":
                return Hex(aud["tag"], 4)
            if key == "tag_int":
                return aud["tag"]
            return aud[key]
        if key in ("title", "author", "copyright", "description", "rating"):
            v = p["content"].get(key)
            if not v:   # ffmpeg/WMP also store these as Extended Content attributes (ffmpeg puts `comment` there only)
                v = next((x for k, x in p["ext"].items() if _norm(k) in (key, "wm" + key) and isinstance(x, str)), "")
            return v if v else "none"
        if key == "nstreams":
            return len(p["streams"])
        if key == "naudio":
            return sum(1 for s in p["streams"] if s.get("type") == "audio")
        if key == "nobj":
            return p["objects"]
        if key == "extnames":
            return list(p["ext"])
        if not fp:
            return None
        if key == "created":
            return _filetime_utc(fp["created"])
        if key == "created_raw":
            return fp["created"]
        if key == "fileid":
            from ..spell import Guid
            return Guid("bytes_le", fp["fileid"])
        return fp.get(key)
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None
