"""Audio embedded in mail (flavor D17 'embedded in mail') -- prebuilt, SPECULATIVE. fmt tokens `email` / `eml` /
`mime` / `mail`.

Attachments use the email_mime.py rule (non-multipart parts with a filename -- Content-Disposition filename, else
Content-Type name, RFC 2231 continuations / RFC 2047 encoded-words decoded by policy.default -- in MIME walk order),
payload = get_payload(decode=True). An attachment is an AUDIO attachment when its decoded bytes carry an audio codec
(media_ident: the GM-verified D17 reader + ASF/CAF/MP4 esds) OR it is DECLARED audio (Content-Type audio/* or an
audio file extension). Every list below is over that audio set, MIME order, index-aligned:
  - attachment_audio_codec_names: ffprobe codec_name of the decoded payload (pcm_s16le, mp3, vorbis, opus, flac,
    aac, ...); declared-audio payload with no audio codec -> "none" entry.
  - attachment_media_container_formats: ffprobe format.format_name by magic (prebuilt media.py: wav, mp3, ogg, flac,
    aiff, aac, mov,mp4,m4a,3gp,3g2,mj2, matroska,webm), else the media_ident short token (asf, caf, rf64), else "none".
  - attachment_declared_content_types: Content-Type as declared (lowercase type/subtype, no params).
  - attachment_audio_durations_seconds: ffprobe stream duration "%f" (prebuilt media.py stream_info; Ogg/MP4/MKV via
    media_streams), None entry when the header cannot give it.
  - attachment_audio_mismatch_names: filenames whose declared Content-Type (when specific, i.e. not
    application/octet-stream) or extension disagrees with the container the magic names (a WAV sent as audio/mpeg
    "voice.mp3"; declared audio that is not audio). None mismatched -> [] .
  - audio_attachment_count: len(audio set).
Not an e-mail -> "none"; an e-mail with no audio attachment -> lists [] / count 0.
Helper for artifact refs (`message-001.eml -> voice-001.ogg`, `zip -> eml -> wav`): attachment_bytes(eml, filename)."""
FIELDS = {
    ("email", "attachment_audio_codec_names"): "audio_value",
    ("email", "attachment_audio_codecs"): "audio_value",
    ("email", "audio_attachment_codec_names"): "audio_value",
    ("email", "attachment_media_container_formats"): "audio_value",
    ("email", "attachment_container_formats"): "audio_value",
    ("email", "audio_attachment_container_formats"): "audio_value",
    ("email", "attachment_declared_content_types"): "audio_value",
    ("email", "audio_attachment_declared_content_types"): "audio_value",
    ("email", "attachment_audio_mismatch_names"): "audio_value",
    ("email", "audio_attachment_mismatch_names"): "audio_value",
    ("email", "attachment_audio_durations_seconds"): "audio_value",
    ("email", "attachment_audio_durations"): "audio_value",
    ("email", "audio_attachment_durations_seconds"): "audio_value",
    ("email", "audio_attachment_count"): "audio_value",
    ("email", "attachment_audio_count"): "audio_value",
    ("email", "audio_attachment_names"): "audio_value",
    ("email", "attachment_audio_names"): "audio_value",
    ("eml", "attachment_audio_codec_names"): "audio_value",
    ("eml", "attachment_audio_codecs"): "audio_value",
    ("eml", "audio_attachment_codec_names"): "audio_value",
    ("eml", "attachment_media_container_formats"): "audio_value",
    ("eml", "attachment_container_formats"): "audio_value",
    ("eml", "audio_attachment_container_formats"): "audio_value",
    ("eml", "attachment_declared_content_types"): "audio_value",
    ("eml", "audio_attachment_declared_content_types"): "audio_value",
    ("eml", "attachment_audio_mismatch_names"): "audio_value",
    ("eml", "audio_attachment_mismatch_names"): "audio_value",
    ("eml", "attachment_audio_durations_seconds"): "audio_value",
    ("eml", "attachment_audio_durations"): "audio_value",
    ("eml", "audio_attachment_durations_seconds"): "audio_value",
    ("eml", "audio_attachment_count"): "audio_value",
    ("eml", "attachment_audio_count"): "audio_value",
    ("eml", "audio_attachment_names"): "audio_value",
    ("eml", "attachment_audio_names"): "audio_value",
    ("mime", "attachment_audio_codec_names"): "audio_value",
    ("mime", "attachment_audio_codecs"): "audio_value",
    ("mime", "audio_attachment_codec_names"): "audio_value",
    ("mime", "attachment_media_container_formats"): "audio_value",
    ("mime", "attachment_container_formats"): "audio_value",
    ("mime", "audio_attachment_container_formats"): "audio_value",
    ("mime", "attachment_declared_content_types"): "audio_value",
    ("mime", "audio_attachment_declared_content_types"): "audio_value",
    ("mime", "attachment_audio_mismatch_names"): "audio_value",
    ("mime", "audio_attachment_mismatch_names"): "audio_value",
    ("mime", "attachment_audio_durations_seconds"): "audio_value",
    ("mime", "attachment_audio_durations"): "audio_value",
    ("mime", "audio_attachment_durations_seconds"): "audio_value",
    ("mime", "audio_attachment_count"): "audio_value",
    ("mime", "attachment_audio_count"): "audio_value",
    ("mime", "audio_attachment_names"): "audio_value",
    ("mime", "attachment_audio_names"): "audio_value",
    ("mail", "attachment_audio_codec_names"): "audio_value",
    ("mail", "attachment_audio_codecs"): "audio_value",
    ("mail", "audio_attachment_codec_names"): "audio_value",
    ("mail", "attachment_media_container_formats"): "audio_value",
    ("mail", "attachment_container_formats"): "audio_value",
    ("mail", "audio_attachment_container_formats"): "audio_value",
    ("mail", "attachment_declared_content_types"): "audio_value",
    ("mail", "audio_attachment_declared_content_types"): "audio_value",
    ("mail", "attachment_audio_mismatch_names"): "audio_value",
    ("mail", "audio_attachment_mismatch_names"): "audio_value",
    ("mail", "attachment_audio_durations_seconds"): "audio_value",
    ("mail", "attachment_audio_durations"): "audio_value",
    ("mail", "audio_attachment_durations_seconds"): "audio_value",
    ("mail", "audio_attachment_count"): "audio_value",
    ("mail", "attachment_audio_count"): "audio_value",
    ("mail", "audio_attachment_names"): "audio_value",
    ("mail", "attachment_audio_names"): "audio_value",
}

# Content-Types that name each magic container (lowercase); application/octet-stream & co. are generic, never a mismatch.
_CT_OK = {"wav": ("audio/wav", "audio/x-wav", "audio/wave", "audio/x-pn-wav", "audio/vnd.wave"),
          "rf64": ("audio/wav", "audio/x-wav", "audio/wave", "audio/vnd.wave"),
          "mp3": ("audio/mpeg", "audio/mp3", "audio/mpeg3", "audio/x-mpeg", "audio/x-mpeg-3", "audio/mpa"),
          "ogg": ("audio/ogg", "application/ogg", "audio/opus", "audio/vorbis", "audio/x-ogg", "audio/x-vorbis+ogg",
                  "audio/x-opus+ogg"),
          "flac": ("audio/flac", "audio/x-flac"),
          "mp4": ("audio/mp4", "audio/m4a", "audio/x-m4a", "audio/aac", "video/mp4", "audio/3gpp", "video/3gpp"),
          "adts": ("audio/aac", "audio/x-aac", "audio/aacp", "audio/x-hx-aac-adts"),
          "aiff": ("audio/aiff", "audio/x-aiff"),
          "amr": ("audio/amr", "audio/3gpp"),
          "au": ("audio/basic", "audio/au", "audio/x-au"),
          "matroska": ("audio/x-matroska", "audio/webm", "video/webm", "video/x-matroska"),
          "caf": ("audio/x-caf",),
          "asf": ("audio/x-ms-wma", "video/x-ms-asf", "video/x-ms-wmv", "audio/x-ms-asf")}
_GENERIC_CT = ("application/octet-stream", "application/x-download", "application/binary", "application/unknown",
               "binary/octet-stream", "application/force-download")


def _ct(part):
    try:
        return (part.get_content_type() or "").lower()
    except Exception:  # noqa: BLE001
        return ""


def _audio_atts(msg):
    """[(filename, declared content type, decoded bytes, container token, codec)] of the audio set, MIME order."""
    from . import email_mime, media_ident
    out = []
    for fn, part in email_mime._attachments(msg):
        data = email_mime._payload(part)
        ct = _ct(part)
        try:
            cont = media_ident._container(data) if data else None
            codec = media_ident._codec(data) if data else None
        except Exception:  # noqa: BLE001
            cont = codec = None
        ext = (media_ident._ext(fn) or "").lower()
        if codec or cont or ct.startswith("audio/") or ext in media_ident._EXT_OK:
            out.append((fn, ct, data, cont, codec))
    return out


def _mismatch(fn, ct, cont):
    from . import media_ident
    ext = (media_ident._ext(fn) or "").lower()
    if cont is None:        # declared audio (type or extension) but the bytes are not audio
        return True
    if ext and cont not in media_ident._EXT_OK.get(ext, (cont,)):
        return True
    if ct and ct not in _GENERIC_CT and ct not in _CT_OK.get(cont, ()):
        return True
    return False


def _container_name(data, cont):
    from . import media
    try:
        v = media.format_name(data, {"field": "format_name"}) if data else None
    except Exception:  # noqa: BLE001
        v = None
    if v and v != "none":
        return v
    return cont or "none"


def _duration(data):
    from . import media, media_streams
    if not data:
        return None
    try:
        v = media.stream_info(data, {"field": "primary_audio_duration_seconds"})
    except Exception:  # noqa: BLE001
        v = None
    if v and v != "none":
        return v
    try:
        for s in media_streams.streams(data) or ():
            if s.get("codec_type") == "audio" and s.get("duration") is not None:
                d = s["duration"]
                return d if isinstance(d, str) else "%.6f" % float(d)
    except Exception:  # noqa: BLE001
        pass
    return None


def attachment_bytes(eml_bytes, filename):
    """Decoded payload of the attachment named `filename` (RFC 2231/2047-decoded name; exact, then case-insensitive,
    then basename match) in an .eml, or None. Resolves artifact refs like `message-001.eml -> voice-001.ogg`."""
    from . import email_mime
    try:
        msg = email_mime._parse(eml_bytes)
        if msg is None or not filename:
            return None
        want = str(filename).strip()
        atts = email_mime._attachments(msg)
        base = lambda s: s.replace("\\", "/").rsplit("/", 1)[-1]  # noqa: E731
        for test in (lambda fn: fn == want, lambda fn: fn.lower() == want.lower(),
                     lambda fn: base(fn).lower() == base(want).lower()):
            for fn, part in atts:
                if test(fn):
                    return email_mime._payload(part)
    except Exception:  # noqa: BLE001
        return None
    return None


def audio_value(data, ctx):
    if not data:
        return None
    try:
        from . import email_mime
        msg = email_mime._parse(data)
        if msg is None:
            return "none"
        f = (ctx or {}).get("field") or ""
        atts = _audio_atts(msg)
        if f.endswith("count"):
            return len(atts)
        if "mismatch" in f:
            return [fn for fn, ct, _, cont, _ in atts if _mismatch(fn, ct, cont)]
        if "codec" in f:
            return [codec or "none" for _, _, _, _, codec in atts]
        if "container" in f:
            return [_container_name(d, cont) for _, _, d, cont, _ in atts]
        if "declared_content_type" in f:
            return [ct for _, ct, _, _, _ in atts]
        if "duration" in f:
            return [_duration(d) if cont else None for _, _, d, cont, _ in atts]
        if f.endswith("names"):
            return [fn for fn, _, _, _, _ in atts]
        return None
    except Exception:  # noqa: BLE001
        return None
