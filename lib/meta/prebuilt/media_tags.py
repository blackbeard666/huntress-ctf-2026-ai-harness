"""`media` container/stream TAGS (aliases `audio`, `av`) -- prebuilt, SPECULATIVE, stdlib only.

ffprobe-style `format.tags` (falling back to the first stream's tags: Ogg keeps its Vorbis comments on the stream):
  media.tag_<key>   = the tag value, <key> matched CASE-INSENSITIVELY against the ffmpeg demuxer's key
                      (title, artist, album, comment, encoder, date, creation_time, language, x_custom, ...)
  media.encoder     = tag 'encoder' (ID3 TSSE, Vorbis/Opus ENCODER comment, MP4 \\xa9too, MKV Tags ENCODER else
                      Info MuxingApp, WAV ISFT); the Vorbis/Opus vendor string is NOT ffmpeg's encoder tag
  media.opus_vendor / vorbis_vendor = the vendor string of the OpusTags / Vorbis comment header.
Key mapping copies ffmpeg 7.0 (libavformat id3v2.c, riff.c ff_riff_info_conv, vorbiscomment.c, mov.c, matroskadec.c),
checked against ffmpeg 7.0.2 `-i` / `-f ffmetadata` output on the fixtures:
  - ID3v2.2-2.4: T*** frames -> conv table (TIT2 title, TPE1 artist, TSSE encoder, TDRC date, TDEN creation_time ...),
    unknown frames keep their 4CC; TXXX -> its description; COMM -> "comment" (empty desc) else its description;
    v2.3 TYER+TDAT(+TIME) merged to "YYYY-MM-DD[ HH:MM]". ID3v1 only when there is no ID3v2 tag.
  - WAV LIST/INFO 4CCs -> riff conv (INAM title, IART artist, ICMT comment, ICRD date, ISFT encoder, ILNG language),
    else the 4CC; an embedded "id3 " chunk adds the ID3 keys.
  - Vorbis comments (Ogg Vorbis/Opus/FLAC, native FLAC): key as stored, duplicates joined with ";",
    DESCRIPTION -> comment, ALBUMARTIST -> album_artist, TRACKNUMBER -> track, DISCNUMBER -> disc.
  - MP4 moov/udta/meta/ilst (+ QuickTime udta \\xa9 strings): \\xa9nam title ... \\xa9too encoder, freeform `----`
    -> its name; first value only; creation_time from mvhd (seconds since 1904-01-01 UTC) rendered like ffmpeg
    "%Y-%m-%dT%H:%M:%S.000000Z" (an all-zero mvhd time sets nothing).
  - Matroska: Info Title -> title, MuxingApp -> encoder, DateUTC (ns since 2001-01-01) -> creation_time
    "...%06dZ"; global Tags (no track/edition/chapter/attachment target) SimpleTag name (+ "-<lang>" when TagLanguage
    is set and not "und") override.
tag_creation_time_utc renders that same instant as "%Y-%m-%dT%H:%M:%SZ" (fraction kept only if non-zero).
Tag absent from a parseable container / a non-media member -> "none"; unknown bytes -> None."""
import struct
from datetime import datetime, timedelta, timezone

_TAG_FIELDS = ("tag_title", "tag_artist", "tag_album", "tag_album_artist", "tag_comment", "tag_encoder", "tag_date",
               "tag_creation_time", "tag_creation_time_utc", "tag_language", "tag_genre", "tag_track",
               "tag_composer", "tag_copyright", "tag_encoded_by", "tag_publisher", "tag_description")
_ENC_FIELDS = ("encoder", "format_encoder", "encoder_tag", "format_tag_encoder_name", "encoder_name",
               "container_encoder", "muxing_app", "writing_application")
_VENDOR_FIELDS = ("opus_vendor", "opus_vendor_string", "opustags_vendor", "vorbis_vendor", "vorbis_vendor_string",
                  "vorbis_comment_vendor", "vendor", "vendor_string", "flac_vendor")

FIELDS = {
    ("media", "tag_title"): "tag_value",
    ("media", "tag_artist"): "tag_value",
    ("media", "tag_album"): "tag_value",
    ("media", "tag_album_artist"): "tag_value",
    ("media", "tag_comment"): "tag_value",
    ("media", "tag_encoder"): "tag_value",
    ("media", "tag_date"): "tag_value",
    ("media", "tag_creation_time"): "tag_value",
    ("media", "tag_creation_time_utc"): "tag_value",
    ("media", "tag_language"): "tag_value",
    ("media", "tag_genre"): "tag_value",
    ("media", "tag_track"): "tag_value",
    ("media", "tag_composer"): "tag_value",
    ("media", "tag_copyright"): "tag_value",
    ("media", "tag_encoded_by"): "tag_value",
    ("media", "tag_publisher"): "tag_value",
    ("media", "tag_description"): "tag_value",
    ("media", "tag_*"): "tag_value",
    ("media", "tags_*"): "tag_value",
    ("media", "format_tag_*"): "tag_value",
    ("media", "format_tags_*"): "tag_value",
    ("media", "encoder"): "encoder",
    ("media", "format_encoder"): "encoder",
    ("media", "encoder_tag"): "encoder",
    ("media", "format_tag_encoder_name"): "encoder",
    ("media", "encoder_name"): "encoder",
    ("media", "container_encoder"): "encoder",
    ("media", "muxing_app"): "encoder",
    ("media", "writing_application"): "encoder",
    ("media", "opus_vendor"): "vendor",
    ("media", "opus_vendor_string"): "vendor",
    ("media", "opustags_vendor"): "vendor",
    ("media", "vorbis_vendor"): "vendor",
    ("media", "vorbis_vendor_string"): "vendor",
    ("media", "vorbis_comment_vendor"): "vendor",
    ("media", "vendor"): "vendor",
    ("media", "vendor_string"): "vendor",
    ("media", "flac_vendor"): "vendor",
    ("audio", "tag_title"): "tag_value",
    ("audio", "tag_artist"): "tag_value",
    ("audio", "tag_album"): "tag_value",
    ("audio", "tag_comment"): "tag_value",
    ("audio", "tag_encoder"): "tag_value",
    ("audio", "tag_date"): "tag_value",
    ("audio", "tag_creation_time"): "tag_value",
    ("audio", "tag_creation_time_utc"): "tag_value",
    ("audio", "tag_language"): "tag_value",
    ("audio", "tag_*"): "tag_value",
    ("audio", "format_tag_*"): "tag_value",
    ("audio", "encoder"): "encoder",
    ("audio", "opus_vendor"): "vendor",
    ("audio", "vorbis_vendor"): "vendor",
    ("av", "tag_title"): "tag_value",
    ("av", "tag_artist"): "tag_value",
    ("av", "tag_album"): "tag_value",
    ("av", "tag_comment"): "tag_value",
    ("av", "tag_encoder"): "tag_value",
    ("av", "tag_date"): "tag_value",
    ("av", "tag_creation_time"): "tag_value",
    ("av", "tag_creation_time_utc"): "tag_value",
    ("av", "tag_language"): "tag_value",
    ("av", "tag_*"): "tag_value",
    ("av", "format_tag_*"): "tag_value",
    ("av", "encoder"): "encoder",
    ("av", "opus_vendor"): "vendor",
    ("av", "vorbis_vendor"): "vendor",
}

_NON_MEDIA = (b"\x89PNG", b"\xff\xd8\xff", b"%PDF", b"PK\x03\x04", b"MZ", b"\x7fELF", b"\xd0\xcf\x11\xe0",
              b"GIF8", b"BM", b"{", b"<", b"\x1f\x8b", b"7z\xbc\xaf", b"Rar!")

# ---------------------------------------------------------------- ID3

_ID3_CONV = {"TALB": "album", "TCOM": "composer", "TCON": "genre", "TCOP": "copyright", "TENC": "encoded_by",
             "TIT2": "title", "TLAN": "language", "TPE1": "artist", "TPE2": "album_artist", "TPE3": "performer",
             "TPOS": "disc", "TPUB": "publisher", "TRCK": "track", "TSSE": "encoder", "USLT": "lyrics",
             "TCMP": "compilation", "TDRC": "date", "TDRL": "date", "TDEN": "creation_time", "TSOA": "album-sort",
             "TSOP": "artist-sort", "TSOT": "title-sort", "TIT1": "grouping"}


def _id3_tags(b):
    """[(key, value)] of a leading ID3v2 tag (ffmpeg naming), or None when there is none."""
    from . import mp3
    v2 = mp3._id3v2(b)
    if v2 is None:
        return None
    out, raw = [], {}
    for fid, body in v2[3]:
        if not body:
            continue
        if fid == "TXXX":
            desc, txt = mp3._split_term(body[0], body[1:])
            k, v = mp3._dec(body[0], desc).lstrip("﻿").strip("\x00 "), mp3._text(bytes([body[0]]) + txt)
            k = k or "TXXX"
        elif fid == "COMM":
            d, v = mp3._comm(body)
            k = d or "comment"
        elif fid[:1] == "T":
            k, v = _ID3_CONV.get(fid, fid), mp3._text(body)
            if fid == "TDEN":
                v = v.replace(" ", "T", 1)
        else:
            continue
        if fid in ("TYER", "TDAT", "TIME"):
            raw[fid] = v
            continue
        out.append((k, v))
    y = raw.get("TYER", "")[:4]
    if y and not any(k == "date" for k, _ in out):
        d, t = raw.get("TDAT", ""), raw.get("TIME", "")
        if len(d) >= 4:
            y += "-%s-%s" % (d[2:4], d[:2])
            if len(t) >= 4:
                y += " %s:%s" % (t[:2], t[2:4])
        out.append(("date", y))
    return out


def _id3v1_tags(b):
    from . import mp3
    t = mp3._id3v1(b)
    if t is None:
        return None
    out = [(k, mp3._v1_str(t[s:e])) for k, (s, e) in (("title", (3, 33)), ("artist", (33, 63)),
                                                      ("album", (63, 93)), ("date", (93, 97)))]
    v11 = t[125] == 0 and t[126] != 0
    out.append(("comment", mp3._v1_str(t[97:125] if v11 else t[97:127])))
    if v11:
        out.append(("track", str(t[126])))
    return [(k, v) for k, v in out if v]


def _mp3(b):
    if b[:3] == b"ID3":
        return _id3_tags(b) or []
    if len(b) > 4 and b[0] == 0xFF and (b[1] & 0xE0) == 0xE0 or (len(b) >= 128 and b[-128:-125] == b"TAG"):
        return _id3v1_tags(b) or []
    return None


# ---------------------------------------------------------------- WAV

_RIFF_CONV = {"IART": "artist", "ICMT": "comment", "ICOP": "copyright", "ICRD": "date", "IGNR": "genre",
              "ILNG": "language", "INAM": "title", "IPRD": "album", "IPRT": "track", "ITRK": "track",
              "ISFT": "encoder", "ISMP": "timecode", "ITCH": "encoded_by"}


def _s(raw):
    raw = raw.split(b"\0")[0]
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw.decode("latin-1").strip()


def _wav(b):
    if not (b[:4] in (b"RIFF", b"RIFX", b"RF64") and b[8:12] == b"WAVE"):
        return None
    fmt = ">I" if b[:4] == b"RIFX" else "<I"
    out, off = [], 12
    while off + 8 <= len(b):
        cid, sz = b[off:off + 4], struct.unpack_from(fmt, b, off + 4)[0]
        body = b[off + 8:off + 8 + sz]
        if cid == b"LIST" and body[:4] == b"INFO":
            o = 4
            while o + 8 <= len(body):
                sid, ss = body[o:o + 4], struct.unpack_from(fmt, body, o + 4)[0]
                k = sid.decode("latin-1")
                v = _s(body[o + 8:o + 8 + ss])
                if v and k.isalnum():
                    out.append((_RIFF_CONV.get(k, k), v))
                o += 8 + ss + (ss & 1)
        elif cid in (b"id3 ", b"ID3 "):
            out.extend(_id3_tags(body) or [])
        off += 8 + sz + (sz & 1)
    return out


# ---------------------------------------------------------------- Vorbis comment

_VC_CONV = {"ALBUMARTIST": "album_artist", "TRACKNUMBER": "track", "DISCNUMBER": "disc", "DESCRIPTION": "comment"}


def _vcomment(c):
    """(vendor, [(key, value)]) of a Vorbis comment body (after the packet signature)."""
    vl, = struct.unpack_from("<I", c, 0)
    vendor = c[4:4 + vl].decode("utf-8", "replace")
    o = 4 + vl
    n, = struct.unpack_from("<I", c, o)
    o += 4
    tags, idx = [], {}
    for _ in range(min(n, 4096)):
        if o + 4 > len(c):
            break
        ln, = struct.unpack_from("<I", c, o)
        k, eq, v = c[o + 4:o + 4 + ln].decode("utf-8", "replace").partition("=")
        o += 4 + ln
        if not eq or not k or k.upper() == "METADATA_BLOCK_PICTURE":
            continue
        k = _VC_CONV.get(k.upper(), k)
        if k.lower() in idx:                                   # ffmpeg AV_DICT_APPEND with ";"
            i = idx[k.lower()]
            tags[i] = (tags[i][0], tags[i][1] + ";" + v)
        else:
            idx[k.lower()] = len(tags)
            tags.append((k, v))
    return vendor, tags


def _flac(b):
    """(vendor, tags, kind) of native FLAC, or None."""
    o = 0
    pre = []
    if b[:3] == b"ID3":
        from . import mp3
        v2 = mp3._id3v2(b)
        o = 10 + (v2[2] if v2 else 0)
        pre = _id3_tags(b) or []
    if b[o:o + 4] != b"fLaC":
        return None
    o += 4
    while o + 4 <= len(b):
        h = b[o]
        ln = int.from_bytes(b[o + 1:o + 4], "big")
        if h & 0x7F == 4:
            vendor, tags = _vcomment(b[o + 4:o + 4 + ln])
            return vendor, pre + tags, "flac"
        if h & 0x80:
            break
        o += 4 + ln
    return None, pre, "flac"


def _ogg(b):
    """(vendor, tags of the first stream with a comment header, kind 'opus'|'vorbis'|'flac'|...), or None."""
    if b[:4] != b"OggS":
        return None
    from .media_streams import _ogg_packets
    pk, order, _ = _ogg_packets(b)
    for s in order:
        ps = pk[s]
        if len(ps) < 2:
            continue
        h, c = ps[0], ps[1]
        if h[:8] == b"OpusHead" and c[:8] == b"OpusTags":
            return _vcomment(c[8:]) + ("opus",)
        if h[:7] == b"\x01vorbis" and c[:7] == b"\x03vorbis":
            return _vcomment(c[7:]) + ("vorbis",)
        if h[:5] == b"\x7fFLAC" and c[:1] and c[0] & 0x7F == 4:
            return _vcomment(c[4:]) + ("flac",)
        if h[:7] == b"\x80theora" and c[:7] == b"\x81theora":
            return _vcomment(c[7:]) + ("theora",)
        if h[:8] == b"Speex   ":
            return _vcomment(c) + ("speex",)
    return None, [], None


# ---------------------------------------------------------------- MP4

_MP4_KEYS = {"\xa9nam": "title", "\xa9ART": "artist", "aART": "album_artist", "\xa9alb": "album",
             "\xa9cmt": "comment", "\xa9day": "date", "\xa9too": "encoder", "\xa9enc": "encoder",
             "\xa9swr": "encoder", "\xa9wrt": "composer", "\xa9gen": "genre", "gnre": "genre",
             "\xa9grp": "grouping", "\xa9lyr": "lyrics", "cprt": "copyright", "\xa9cpy": "copyright",
             "desc": "description", "ldes": "synopsis", "tvsh": "show", "tven": "episode_id", "tvnn": "network",
             "tves": "episode_sort", "tvsn": "season_number", "\xa9pub": "publisher", "\xa9mak": "make",
             "\xa9mod": "model", "\xa9xyz": "location", "keyw": "keywords", "\xa9key": "keywords",
             "\xa9dir": "director", "\xa9prd": "producer", "\xa9st3": "subtitle", "\xa9inf": "comment",
             "soal": "sort_album", "soar": "sort_artist", "soaa": "sort_album_artist", "sonm": "sort_name",
             "soco": "sort_composer", "sosn": "sort_show", "purl": "podcast_url", "catg": "category",
             "pcst": "podcast", "cpil": "compilation", "pgap": "gapless_playback", "hdvd": "hd_video",
             "stik": "media_type", "rtng": "rating", "trkn": "track", "disk": "disc", "\xa9mvn": "movement_name",
             "\xa9wrk": "work", "\xa9aut": "author", "\xa9ard": "director"}
_EPOCH_1904 = datetime(1904, 1, 1, tzinfo=timezone.utc)


def _mp4_data(b, s, e, key):
    from .media_streams import _boxes
    for t, cs, ce in _boxes(b, s, e):
        if t != b"data" or ce - cs < 8:
            continue
        typ = int.from_bytes(b[cs + 1:cs + 4], "big")
        p = b[cs + 8:ce]
        if key in ("track", "disc") and len(p) >= 6:
            n, tot = struct.unpack_from(">HH", p, 2)
            return "%d/%d" % (n, tot) if tot else "%d" % n
        if key == "genre" and typ in (0, 21) and len(p) == 2:
            return None
        if typ in (21, 22) or (typ == 0 and len(p) in (1, 2, 4, 8) and key not in ("title",)):
            return str(int.from_bytes(p, "big", signed=typ != 22))
        return p.decode("utf-16-be" if typ == 2 else "utf-8", "replace").rstrip("\0")
    return None


def _mp4(b):
    from .media_streams import _boxes, _child
    if b[4:8] not in (b"ftyp", b"moov", b"mdat", b"free", b"wide", b"skip"):
        return None
    out = []
    ft = _child(b, 0, len(b), b"ftyp")
    if ft and ft[1] - ft[0] >= 8:
        cs, ce = ft
        out += [("major_brand", b[cs:cs + 4].decode("latin-1")), ("minor_version", str(struct.unpack_from(">I", b, cs + 4)[0])),
                ("compatible_brands", b[cs + 8:ce].decode("latin-1"))]
    mv = _child(b, 0, len(b), b"moov")
    if mv is None:
        return out if ft else None
    mh = _child(b, mv[0], mv[1], b"mvhd")
    if mh:
        ver = b[mh[0]]
        ct = struct.unpack_from(">Q" if ver == 1 else ">I", b, mh[0] + 4)[0]
        if ct:
            t = _EPOCH_1904 + timedelta(seconds=ct)
            out.append(("creation_time", t.strftime("%Y-%m-%dT%H:%M:%S.000000Z")))
    ud = _child(b, mv[0], mv[1], b"udta")
    if ud is None:
        return out
    for t, cs, ce in _boxes(b, ud[0], ud[1]):
        if t == b"meta":
            ms = cs if b[cs + 4:cs + 8] in (b"hdlr", b"ilst") else cs + 4    # QuickTime meta has no full-box header
            il = _child(b, ms, ce, b"ilst")
            if il is None:
                continue
            for it, ics, ice in _boxes(b, il[0], il[1]):
                name = it.decode("latin-1")
                if name == "----":
                    nm = _child(b, ics, ice, b"name")
                    key = b[nm[0] + 4:nm[1]].decode("utf-8", "replace") if nm else None
                else:
                    key = _MP4_KEYS.get(name)
                if not key or any(k == key for k, _ in out):
                    continue
                v = _mp4_data(b, ics, ice, key)
                if v is not None:
                    out.append((key, v))
        elif t[:1] == b"\xa9" and ce - cs >= 4:
            key = _MP4_KEYS.get(t.decode("latin-1"))
            ln = struct.unpack_from(">H", b, cs)[0]
            if key and not any(k == key for k, _ in out) and cs + 4 + ln <= ce:
                out.append((key, b[cs + 4:cs + 4 + ln].decode("utf-8", "replace").rstrip("\0")))
    return out


# ---------------------------------------------------------------- Matroska

_EPOCH_2001 = datetime(2001, 1, 1, tzinfo=timezone.utc)


def _mkv(b):
    if b[:4] != b"\x1a\x45\xdf\xa3":
        return None
    from .media_streams import _ebml, _str
    info, tags = [], []
    for eid, s, e, _ in _ebml(b, 0, len(b)):
        if eid != 0x18538067:
            continue
        for cid, cs, ce, _ in _ebml(b, s, e):
            if cid == 0x1549A966:
                for iid, i_s, i_e, _ in _ebml(b, cs, ce):
                    if iid == 0x7BA9:
                        info.append(("title", _str(b, i_s, i_e)))
                    elif iid == 0x4D80:
                        info.append(("encoder", _str(b, i_s, i_e)))
                    elif iid == 0x4461 and i_e - i_s == 8:
                        ns = struct.unpack(">q", b[i_s:i_e])[0]
                        t = _EPOCH_2001 + timedelta(microseconds=ns // 1000)
                        info.append(("creation_time", t.strftime("%Y-%m-%dT%H:%M:%S.%fZ")))
            elif cid == 0x1254C367:
                for tid, ts, te, _ in _ebml(b, cs, ce):
                    if tid != 0x7373:
                        continue
                    glob, simple = True, []
                    for xid, xs, xe, _ in _ebml(b, ts, te):
                        if xid == 0x63C0:
                            glob = not any(k in (0x63C5, 0x63C9, 0x63C4, 0x63C6) and b[ks:ke].strip(b"\0")
                                           for k, ks, ke, _ in _ebml(b, xs, xe))
                        elif xid == 0x67C8:
                            simple.append((xs, xe))
                    if not glob:
                        continue
                    for xs, xe in simple:
                        name = val = lang = None
                        for k, ks, ke, _ in _ebml(b, xs, xe):
                            if k == 0x45A3:
                                name = _str(b, ks, ke)
                            elif k == 0x4487:
                                val = _str(b, ks, ke)
                            elif k == 0x447A:
                                lang = _str(b, ks, ke)
                        if name and val is not None:
                            tags.append((name + ("-" + lang if lang and lang != "und" else ""), val))
        break
    out = list(info)
    for k, v in tags:                                          # av_dict_set: same key (any case) replaces in place
        for i, (ok, _) in enumerate(out):
            if ok.lower() == k.lower():
                out[i] = (k, v)
                break
        else:
            out.append((k, v))
    return out


# ---------------------------------------------------------------- dispatch

def _parse(b):
    """(format tags [(k, v)], stream tags [(k, v)], vendor info (vendor, kind) | None) or None (not a known container)."""
    fl = _flac(b) if b[:4] == b"fLaC" or b[:3] == b"ID3" else None
    if fl is not None:
        return fl[1], [], (fl[0], "flac") if fl[0] is not None else None
    og = _ogg(b)
    if og is not None:
        return [], og[1], (og[0], og[2]) if og[0] is not None else None
    for fn in (_wav, _mp4, _mkv, _mp3):
        r = fn(b)
        if r is not None:
            return r, [], None
    return None


def _load(data):
    if data is None:
        return None
    b = bytes(data)
    try:
        r = _parse(b)
    except (ValueError, IndexError, struct.error, OverflowError, TypeError):
        r = None
    if r is None:
        return "none" if b.startswith(_NON_MEDIA) or (b[:512] and all(c in b"\t\n\r" or 32 <= c < 127 for c in b[:512])) else None
    return r


def _find(r, key):
    key = key.lower()
    for tags in (r[0], r[1]):
        for k, v in tags:
            if k.lower() == key:
                return v
    return None


def _utc(v):
    s = v.strip().replace(" ", "T", 1).rstrip("Z")
    for f in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            t = datetime.strptime(s, f)
        except ValueError:
            continue
        return t.strftime("%Y-%m-%dT%H:%M:%S") + (".%06d" % t.microsecond if t.microsecond else "") + "Z"
    return v


def tag_value(data, ctx):
    """media.tag_<key>: ffprobe format tag (else first-stream tag) <key>, case-insensitive; absent -> "none"."""
    try:
        r = _load(data)
        if not isinstance(r, tuple):
            return r
        field = (ctx or {}).get("field") or ""
        param = (ctx or {}).get("param")
        if field.endswith("_*"):
            key = param or ""
        else:
            key = field
            for p in ("format_tags_", "format_tag_", "tags_", "tag_"):
                if key.startswith(p):
                    key = key[len(p):]
                    break
        utc = False
        if key.endswith("_utc") and key != "_utc":
            key, utc = key[:-4], True
        if not key:
            return None
        v = _find(r, key)
        if v is None and "_" in key:
            v = _find(r, key.replace("_", "-")) or _find(r, key.replace("_", " "))
        if v is None:
            return "none"
        v = v.strip()
        return _utc(v) if utc else v
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None


def encoder(data, ctx):
    """media.encoder: ffprobe format tag 'encoder' (first-stream tag for Ogg); absent -> "none"."""
    try:
        r = _load(data)
        if not isinstance(r, tuple):
            return r
        v = _find(r, "encoder")
        return v.strip() if v is not None else "none"
    except Exception:  # noqa: BLE001
        return None


def vendor(data, ctx):
    """media.opus_vendor / vorbis_vendor: the comment header's vendor string; opus_* needs OpusTags, else "none"."""
    try:
        r = _load(data)
        if not isinstance(r, tuple):
            return r
        field = (ctx or {}).get("field") or ""
        if r[2] is None:
            return "none"
        vend, kind = r[2]
        if field.startswith("opus") and kind != "opus":
            return "none"
        if field.startswith("vorbis") and kind not in ("vorbis", "flac"):
            return "none"
        if field.startswith("flac") and kind != "flac":
            return "none"
        return vend
    except Exception:  # noqa: BLE001
        return None
