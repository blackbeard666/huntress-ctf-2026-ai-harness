"""MP4 / M4A / MOV / 3GP ATOM metadata (fmt media; aliases audio, av, video, mp4, mov, quicktime, m4a, 3gp) --
prebuilt, SPECULATIVE, pure struct.

Box walk (ISO/IEC 14496-12 / QuickTime): size u32 BE + type 4CC; size 1 -> u64 largesize follows; size 0 -> to the end
of the parent. Fields (structure name + suffix, ffprobe spellings where ffprobe prints the same value):
  - ftyp_major_brand        = ftyp major brand, trailing spaces/NULs stripped ("qt  " -> "qt", "M4A " -> "M4A");
    ftyp_major_brand_raw    = the 4 bytes verbatim; ftyp_minor_version = u32 decimal (ffprobe minor_version);
    ftyp_compatible_brands  = JSON list in stored order, each 4CC verbatim.
  - mvhd_creation_time_utc / mvhd_modification_time_utc: v0 u32 / v1 u64 seconds since 1904-01-01T00:00:00Z ->
    "%Y-%m-%dT%H:%M:%SZ" (the epoch the spec defines; no ffmpeg <2082844800 heuristic here -- that is the raw field).
    mvhd_timescale = u32; mvhd_duration = raw units; mvhd_duration_seconds = duration/timescale "%.6f" (ffprobe).
    mvhd_next_track_id = u32. mvhd_version = 0/1.
  - track_count = number of moov/trak; track_handler_types = JSON list of mdia/hdlr handler_type 4CCs in trak order
    (soun/vide/text/meta/...); mdhd_languages = JSON list of the packed ISO-639-2 codes (ffmpeg
    ff_mov_lang_to_iso639: >= 0x400 packed, 0 -> Mac "eng", other < 0x400 / 0x7fff -> "und").
  - top_level_atoms = JSON list of top-level box types in file order.
  - tag_<key> = ffprobe format tag: udta/meta/ilst items and QuickTime udta \\xa9 int'l strings mapped like ffmpeg 7
    mov.c (\\xa9nam title, \\xa9too/\\xa9swr/\\xa9enc encoder, \\xa9day date, \\xa9xyz location (ISO 6709 kept
    verbatim), \\xa9ART artist, ...), mdta `keys` + moov/meta/ilst under the key name verbatim
    (com.apple.quicktime.make -> asked as tag_com_apple_quicktime_make: matched with every non-alnum folded to "_",
    case-insensitive), creation_time from mvhd rendered like ffprobe "%Y-%m-%dT%H:%M:%S.000000Z" (ffmpeg: 0 -> no tag;
    a value < 2082844800 is taken as already-unix seconds).
Non-MP4 member / box absent -> "none"; data None -> None. Never raises."""
import json
import struct
from datetime import datetime, timedelta, timezone

FIELDS = {
    ("media", "ftyp_major_brand"): "atom_value",
    ("media", "ftyp_major_brand_raw"): "atom_value",
    ("media", "major_brand"): "atom_value",
    ("media", "major_brand_raw"): "atom_value",
    ("media", "ftyp_minor_version"): "atom_value",
    ("media", "minor_version"): "atom_value",
    ("media", "ftyp_compatible_brands"): "atom_value",
    ("media", "compatible_brands"): "atom_value",
    ("media", "mvhd_creation_time_utc"): "atom_value",
    ("media", "mvhd_creation_time"): "atom_value",
    ("media", "mvhd_modification_time_utc"): "atom_value",
    ("media", "mvhd_modification_time"): "atom_value",
    ("media", "mvhd_timescale"): "atom_value",
    ("media", "mvhd_duration"): "atom_value",
    ("media", "mvhd_duration_seconds"): "atom_value",
    ("media", "mvhd_next_track_id"): "atom_value",
    ("media", "mvhd_version"): "atom_value",
    ("media", "track_count"): "atom_value",
    ("media", "trak_count"): "atom_value",
    ("media", "track_handler_types"): "atom_value",
    ("media", "handler_types"): "atom_value",
    ("media", "mdhd_languages"): "atom_value",
    ("media", "top_level_atoms"): "atom_value",
    ("media", "top_level_box_types"): "atom_value",
    ("audio", "ftyp_major_brand"): "atom_value",
    ("audio", "ftyp_major_brand_raw"): "atom_value",
    ("audio", "major_brand"): "atom_value",
    ("audio", "major_brand_raw"): "atom_value",
    ("audio", "ftyp_minor_version"): "atom_value",
    ("audio", "minor_version"): "atom_value",
    ("audio", "ftyp_compatible_brands"): "atom_value",
    ("audio", "compatible_brands"): "atom_value",
    ("audio", "mvhd_creation_time_utc"): "atom_value",
    ("audio", "mvhd_creation_time"): "atom_value",
    ("audio", "mvhd_modification_time_utc"): "atom_value",
    ("audio", "mvhd_modification_time"): "atom_value",
    ("audio", "mvhd_timescale"): "atom_value",
    ("audio", "mvhd_duration"): "atom_value",
    ("audio", "mvhd_duration_seconds"): "atom_value",
    ("audio", "mvhd_next_track_id"): "atom_value",
    ("audio", "mvhd_version"): "atom_value",
    ("audio", "track_count"): "atom_value",
    ("audio", "trak_count"): "atom_value",
    ("audio", "track_handler_types"): "atom_value",
    ("audio", "handler_types"): "atom_value",
    ("audio", "mdhd_languages"): "atom_value",
    ("audio", "top_level_atoms"): "atom_value",
    ("audio", "top_level_box_types"): "atom_value",
    ("av", "ftyp_major_brand"): "atom_value",
    ("av", "ftyp_major_brand_raw"): "atom_value",
    ("av", "major_brand"): "atom_value",
    ("av", "major_brand_raw"): "atom_value",
    ("av", "ftyp_minor_version"): "atom_value",
    ("av", "minor_version"): "atom_value",
    ("av", "ftyp_compatible_brands"): "atom_value",
    ("av", "compatible_brands"): "atom_value",
    ("av", "mvhd_creation_time_utc"): "atom_value",
    ("av", "mvhd_creation_time"): "atom_value",
    ("av", "mvhd_modification_time_utc"): "atom_value",
    ("av", "mvhd_modification_time"): "atom_value",
    ("av", "mvhd_timescale"): "atom_value",
    ("av", "mvhd_duration"): "atom_value",
    ("av", "mvhd_duration_seconds"): "atom_value",
    ("av", "mvhd_next_track_id"): "atom_value",
    ("av", "mvhd_version"): "atom_value",
    ("av", "track_count"): "atom_value",
    ("av", "trak_count"): "atom_value",
    ("av", "track_handler_types"): "atom_value",
    ("av", "handler_types"): "atom_value",
    ("av", "mdhd_languages"): "atom_value",
    ("av", "top_level_atoms"): "atom_value",
    ("av", "top_level_box_types"): "atom_value",
    ("video", "ftyp_major_brand"): "atom_value",
    ("video", "ftyp_major_brand_raw"): "atom_value",
    ("video", "major_brand"): "atom_value",
    ("video", "major_brand_raw"): "atom_value",
    ("video", "ftyp_minor_version"): "atom_value",
    ("video", "minor_version"): "atom_value",
    ("video", "ftyp_compatible_brands"): "atom_value",
    ("video", "compatible_brands"): "atom_value",
    ("video", "mvhd_creation_time_utc"): "atom_value",
    ("video", "mvhd_creation_time"): "atom_value",
    ("video", "mvhd_modification_time_utc"): "atom_value",
    ("video", "mvhd_modification_time"): "atom_value",
    ("video", "mvhd_timescale"): "atom_value",
    ("video", "mvhd_duration"): "atom_value",
    ("video", "mvhd_duration_seconds"): "atom_value",
    ("video", "mvhd_next_track_id"): "atom_value",
    ("video", "mvhd_version"): "atom_value",
    ("video", "track_count"): "atom_value",
    ("video", "trak_count"): "atom_value",
    ("video", "track_handler_types"): "atom_value",
    ("video", "handler_types"): "atom_value",
    ("video", "mdhd_languages"): "atom_value",
    ("video", "top_level_atoms"): "atom_value",
    ("video", "top_level_box_types"): "atom_value",
    ("video", "tag_*"): "tag_value",
    ("video", "tag_title"): "tag_value",
    ("video", "tag_encoder"): "tag_value",
    ("video", "tag_creation_time"): "tag_value",
    ("video", "tag_date"): "tag_value",
    ("video", "tag_location"): "tag_value",
    ("video", "tag_artist"): "tag_value",
    ("video", "tag_comment"): "tag_value",
    ("video", "tag_album"): "tag_value",
    ("mp4", "ftyp_major_brand"): "atom_value",
    ("mp4", "ftyp_major_brand_raw"): "atom_value",
    ("mp4", "major_brand"): "atom_value",
    ("mp4", "major_brand_raw"): "atom_value",
    ("mp4", "ftyp_minor_version"): "atom_value",
    ("mp4", "minor_version"): "atom_value",
    ("mp4", "ftyp_compatible_brands"): "atom_value",
    ("mp4", "compatible_brands"): "atom_value",
    ("mp4", "mvhd_creation_time_utc"): "atom_value",
    ("mp4", "mvhd_creation_time"): "atom_value",
    ("mp4", "mvhd_modification_time_utc"): "atom_value",
    ("mp4", "mvhd_modification_time"): "atom_value",
    ("mp4", "mvhd_timescale"): "atom_value",
    ("mp4", "mvhd_duration"): "atom_value",
    ("mp4", "mvhd_duration_seconds"): "atom_value",
    ("mp4", "mvhd_next_track_id"): "atom_value",
    ("mp4", "mvhd_version"): "atom_value",
    ("mp4", "track_count"): "atom_value",
    ("mp4", "trak_count"): "atom_value",
    ("mp4", "track_handler_types"): "atom_value",
    ("mp4", "handler_types"): "atom_value",
    ("mp4", "mdhd_languages"): "atom_value",
    ("mp4", "top_level_atoms"): "atom_value",
    ("mp4", "top_level_box_types"): "atom_value",
    ("mp4", "tag_*"): "tag_value",
    ("mp4", "tag_title"): "tag_value",
    ("mp4", "tag_encoder"): "tag_value",
    ("mp4", "tag_creation_time"): "tag_value",
    ("mp4", "tag_date"): "tag_value",
    ("mp4", "tag_location"): "tag_value",
    ("mp4", "tag_artist"): "tag_value",
    ("mp4", "tag_comment"): "tag_value",
    ("mp4", "tag_album"): "tag_value",
    ("mov", "ftyp_major_brand"): "atom_value",
    ("mov", "ftyp_major_brand_raw"): "atom_value",
    ("mov", "major_brand"): "atom_value",
    ("mov", "major_brand_raw"): "atom_value",
    ("mov", "ftyp_minor_version"): "atom_value",
    ("mov", "minor_version"): "atom_value",
    ("mov", "ftyp_compatible_brands"): "atom_value",
    ("mov", "compatible_brands"): "atom_value",
    ("mov", "mvhd_creation_time_utc"): "atom_value",
    ("mov", "mvhd_creation_time"): "atom_value",
    ("mov", "mvhd_modification_time_utc"): "atom_value",
    ("mov", "mvhd_modification_time"): "atom_value",
    ("mov", "mvhd_timescale"): "atom_value",
    ("mov", "mvhd_duration"): "atom_value",
    ("mov", "mvhd_duration_seconds"): "atom_value",
    ("mov", "mvhd_next_track_id"): "atom_value",
    ("mov", "mvhd_version"): "atom_value",
    ("mov", "track_count"): "atom_value",
    ("mov", "trak_count"): "atom_value",
    ("mov", "track_handler_types"): "atom_value",
    ("mov", "handler_types"): "atom_value",
    ("mov", "mdhd_languages"): "atom_value",
    ("mov", "top_level_atoms"): "atom_value",
    ("mov", "top_level_box_types"): "atom_value",
    ("mov", "tag_*"): "tag_value",
    ("mov", "tag_title"): "tag_value",
    ("mov", "tag_encoder"): "tag_value",
    ("mov", "tag_creation_time"): "tag_value",
    ("mov", "tag_date"): "tag_value",
    ("mov", "tag_location"): "tag_value",
    ("mov", "tag_artist"): "tag_value",
    ("mov", "tag_comment"): "tag_value",
    ("mov", "tag_album"): "tag_value",
    ("quicktime", "ftyp_major_brand"): "atom_value",
    ("quicktime", "ftyp_major_brand_raw"): "atom_value",
    ("quicktime", "major_brand"): "atom_value",
    ("quicktime", "major_brand_raw"): "atom_value",
    ("quicktime", "ftyp_minor_version"): "atom_value",
    ("quicktime", "minor_version"): "atom_value",
    ("quicktime", "ftyp_compatible_brands"): "atom_value",
    ("quicktime", "compatible_brands"): "atom_value",
    ("quicktime", "mvhd_creation_time_utc"): "atom_value",
    ("quicktime", "mvhd_creation_time"): "atom_value",
    ("quicktime", "mvhd_modification_time_utc"): "atom_value",
    ("quicktime", "mvhd_modification_time"): "atom_value",
    ("quicktime", "mvhd_timescale"): "atom_value",
    ("quicktime", "mvhd_duration"): "atom_value",
    ("quicktime", "mvhd_duration_seconds"): "atom_value",
    ("quicktime", "mvhd_next_track_id"): "atom_value",
    ("quicktime", "mvhd_version"): "atom_value",
    ("quicktime", "track_count"): "atom_value",
    ("quicktime", "trak_count"): "atom_value",
    ("quicktime", "track_handler_types"): "atom_value",
    ("quicktime", "handler_types"): "atom_value",
    ("quicktime", "mdhd_languages"): "atom_value",
    ("quicktime", "top_level_atoms"): "atom_value",
    ("quicktime", "top_level_box_types"): "atom_value",
    ("quicktime", "tag_*"): "tag_value",
    ("quicktime", "tag_title"): "tag_value",
    ("quicktime", "tag_encoder"): "tag_value",
    ("quicktime", "tag_creation_time"): "tag_value",
    ("quicktime", "tag_date"): "tag_value",
    ("quicktime", "tag_location"): "tag_value",
    ("quicktime", "tag_artist"): "tag_value",
    ("quicktime", "tag_comment"): "tag_value",
    ("quicktime", "tag_album"): "tag_value",
    ("m4a", "ftyp_major_brand"): "atom_value",
    ("m4a", "ftyp_major_brand_raw"): "atom_value",
    ("m4a", "major_brand"): "atom_value",
    ("m4a", "major_brand_raw"): "atom_value",
    ("m4a", "ftyp_minor_version"): "atom_value",
    ("m4a", "minor_version"): "atom_value",
    ("m4a", "ftyp_compatible_brands"): "atom_value",
    ("m4a", "compatible_brands"): "atom_value",
    ("m4a", "mvhd_creation_time_utc"): "atom_value",
    ("m4a", "mvhd_creation_time"): "atom_value",
    ("m4a", "mvhd_modification_time_utc"): "atom_value",
    ("m4a", "mvhd_modification_time"): "atom_value",
    ("m4a", "mvhd_timescale"): "atom_value",
    ("m4a", "mvhd_duration"): "atom_value",
    ("m4a", "mvhd_duration_seconds"): "atom_value",
    ("m4a", "mvhd_next_track_id"): "atom_value",
    ("m4a", "mvhd_version"): "atom_value",
    ("m4a", "track_count"): "atom_value",
    ("m4a", "trak_count"): "atom_value",
    ("m4a", "track_handler_types"): "atom_value",
    ("m4a", "handler_types"): "atom_value",
    ("m4a", "mdhd_languages"): "atom_value",
    ("m4a", "top_level_atoms"): "atom_value",
    ("m4a", "top_level_box_types"): "atom_value",
    ("m4a", "tag_*"): "tag_value",
    ("m4a", "tag_title"): "tag_value",
    ("m4a", "tag_encoder"): "tag_value",
    ("m4a", "tag_creation_time"): "tag_value",
    ("m4a", "tag_date"): "tag_value",
    ("m4a", "tag_location"): "tag_value",
    ("m4a", "tag_artist"): "tag_value",
    ("m4a", "tag_comment"): "tag_value",
    ("m4a", "tag_album"): "tag_value",
    ("3gp", "ftyp_major_brand"): "atom_value",
    ("3gp", "ftyp_major_brand_raw"): "atom_value",
    ("3gp", "major_brand"): "atom_value",
    ("3gp", "major_brand_raw"): "atom_value",
    ("3gp", "ftyp_minor_version"): "atom_value",
    ("3gp", "minor_version"): "atom_value",
    ("3gp", "ftyp_compatible_brands"): "atom_value",
    ("3gp", "compatible_brands"): "atom_value",
    ("3gp", "mvhd_creation_time_utc"): "atom_value",
    ("3gp", "mvhd_creation_time"): "atom_value",
    ("3gp", "mvhd_modification_time_utc"): "atom_value",
    ("3gp", "mvhd_modification_time"): "atom_value",
    ("3gp", "mvhd_timescale"): "atom_value",
    ("3gp", "mvhd_duration"): "atom_value",
    ("3gp", "mvhd_duration_seconds"): "atom_value",
    ("3gp", "mvhd_next_track_id"): "atom_value",
    ("3gp", "mvhd_version"): "atom_value",
    ("3gp", "track_count"): "atom_value",
    ("3gp", "trak_count"): "atom_value",
    ("3gp", "track_handler_types"): "atom_value",
    ("3gp", "handler_types"): "atom_value",
    ("3gp", "mdhd_languages"): "atom_value",
    ("3gp", "top_level_atoms"): "atom_value",
    ("3gp", "top_level_box_types"): "atom_value",
    ("3gp", "tag_*"): "tag_value",
    ("3gp", "tag_title"): "tag_value",
    ("3gp", "tag_encoder"): "tag_value",
    ("3gp", "tag_creation_time"): "tag_value",
    ("3gp", "tag_date"): "tag_value",
    ("3gp", "tag_location"): "tag_value",
    ("3gp", "tag_artist"): "tag_value",
    ("3gp", "tag_comment"): "tag_value",
    ("3gp", "tag_album"): "tag_value",
}

_TOP = {b"ftyp", b"moov", b"mdat", b"wide", b"free", b"skip", b"pnot", b"uuid", b"styp", b"sidx", b"moof", b"PICT"}
_CONT = {b"moov", b"trak", b"mdia", b"minf", b"stbl", b"udta", b"edts", b"dinf", b"ilst", b"tref", b"mvex"}
_EPOCH = datetime(1904, 1, 1, tzinfo=timezone.utc)
# ffmpeg 7 mov.c mov_read_udta_string key table (iTunes ilst items and QuickTime udta \xa9 strings).
_KEYS = {b"\xa9nam": "title", b"\xa9ART": "artist", b"aART": "album_artist", b"\xa9alb": "album",
         b"\xa9cmt": "comment", b"\xa9day": "date", b"\xa9too": "encoder", b"\xa9swr": "encoder",
         b"\xa9enc": "encoder", b"\xa9gen": "genre", b"\xa9wrt": "composer", b"\xa9aut": "artist",
         b"cprt": "copyright", b"\xa9cpy": "copyright", b"desc": "description", b"\xa9des": "description",
         b"ldes": "synopsis", b"\xa9xyz": "location", b"\xa9mak": "make", b"\xa9mod": "model",
         b"\xa9grp": "grouping", b"\xa9lyr": "lyrics", b"\xa9inf": "comment", b"\xa9st3": "subtitle",
         b"\xa9prd": "producer", b"\xa9pub": "publisher", b"\xa9dir": "director", b"\xa9ope": "original_artist",
         b"\xa9PRD": "producer", b"\xa9wrn": "warning", b"\xa9dis": "disclaimer", b"\xa9req": "requirements",
         b"\xa9fmt": "format", b"\xa9src": "source", b"\xa9snm": "sort_name", b"tvsh": "show",
         b"tven": "episode_id", b"tvnn": "network", b"keyw": "keywords", b"\xa9key": "keywords",
         b"gnre": "genre"}


def _boxes(b, s, e):
    """[(type, payload_start, payload_end)] of the boxes in b[s:e]; stops at the first malformed header."""
    out = []
    while s + 8 <= e:
        size, typ = struct.unpack_from(">I4s", b, s)
        h = 8
        if size == 1:
            if s + 16 > e:
                break
            size, h = struct.unpack_from(">Q", b, s + 8)[0], 16
        elif size == 0:
            size = e - s
        if size < h or s + size > e:
            break
        out.append((typ, s + h, s + size))
        s += size
    return out


def _child(b, s, e, typ):
    for t, cs, ce in _boxes(b, s, e):
        if t == typ:
            return cs, ce
    return None


def _meta_children(b, s, e):
    if s + 8 <= e and b[s + 4:s + 8] in (b"hdlr", b"keys", b"ilst"):
        return s     # QuickTime: children start immediately
    return s + 4     # ISO FullBox


def _utc(sec):
    try:
        return (_EPOCH + timedelta(seconds=sec)).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, ValueError):
        return None


def _lang(code):
    if code >= 0x400 and code != 0x7FFF:
        return "".join(chr(((code >> sh) & 0x1F) + 0x60) for sh in (10, 5, 0))
    return "eng" if code == 0 else "und"


def _txt(raw):
    raw = raw.rstrip(b"\0")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _data_value(b, s, e):
    """First `data` child of an ilst item: (well-known type, payload) -> str, or None."""
    for t, cs, ce in _boxes(b, s, e):
        if t == b"data" and ce - cs >= 8:
            wk = struct.unpack_from(">I", b, cs)[0] & 0xFFFFFF
            v = b[cs + 8:ce]
            if wk in (0, 1, 4):          # implicit / UTF-8 / UTF-8 sort
                return _txt(v)
            if wk in (2, 5):             # UTF-16 / UTF-16 sort
                return v.decode("utf-16-be", "replace")
            if wk == 23 and len(v) == 4:
                return "%f" % struct.unpack(">f", v)[0]
            if wk == 24 and len(v) == 8:
                return "%f" % struct.unpack(">d", v)[0]
            if wk in (21, 22, 65, 66, 67, 74, 75, 76, 77, 78) and 1 <= len(v) <= 8:
                return str(int.from_bytes(v, "big", signed=wk in (21, 65, 66, 67, 74)))
            return None
    return None


def _parse(b):
    """dict of the parsed atom facts, or None when b is not an MP4/QuickTime box stream."""
    if not isinstance(b, (bytes, bytearray)) or len(b) < 8:
        return None
    b = bytes(b)
    top = _boxes(b, 0, len(b))
    if not top or top[0][0] not in _TOP or not any(t in (b"ftyp", b"moov") for t, _, _ in top):
        return None
    r = {"top": [t.decode("latin-1") for t, _, _ in top], "tags": {}, "hdlr": [], "lang": []}
    for t, s, e in top:
        if t == b"ftyp" and "ftyp" not in r and e - s >= 8:
            r["ftyp"] = (b[s:s + 4], struct.unpack_from(">I", b, s + 4)[0],
                         [b[i:i + 4] for i in range(s + 8, e - 3, 4)])
    mv = next(((s, e) for t, s, e in top if t == b"moov"), None)
    if mv is None:
        return r
    tags = {}
    for t, s, e in _boxes(b, *mv):
        if t == b"mvhd" and e - s >= 20:
            v = b[s]
            if v == 1 and e - s >= 32:
                c, m, ts, du = struct.unpack_from(">QQIQ", b, s + 4)
                nxt = s + 4 + 28 + 76
            else:
                c, m, ts, du = struct.unpack_from(">IIII", b, s + 4)
                nxt = s + 4 + 16 + 76
            r["mvhd"] = {"version": v, "ctime": c, "mtime": m, "timescale": ts, "duration": du,
                         "next": struct.unpack_from(">I", b, nxt)[0] if nxt + 4 <= e else None}
        elif t == b"trak":
            md = _child(b, s, e, b"mdia")
            ht, lg = None, None
            if md:
                h = _child(b, md[0], md[1], b"hdlr")
                if h and h[1] - h[0] >= 12:
                    ht = b[h[0] + 8:h[0] + 12].decode("latin-1")
                m = _child(b, md[0], md[1], b"mdhd")
                if m and m[1] - m[0] >= 24:
                    off = m[0] + (32 if b[m[0]] == 1 else 20)
                    if off + 2 <= m[1]:
                        lg = _lang(struct.unpack_from(">H", b, off)[0])
            r["hdlr"].append(ht)
            r["lang"].append(lg)
        elif t == b"udta":
            _udta(b, s, e, tags)
        elif t == b"meta":
            _meta(b, s, e, tags)
    mvhd = r.get("mvhd")
    if mvhd and mvhd["ctime"] and "creation_time" not in tags:
        c = mvhd["ctime"]
        c = c - 2082844800 if c >= 2082844800 else c   # ffmpeg mov_metadata_creation_time
        try:
            tags["creation_time"] = datetime.fromtimestamp(c, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z")
        except (OverflowError, ValueError, OSError):
            pass
    r["tags"] = tags
    return r


def _udta(b, s, e, tags):
    for t, cs, ce in _boxes(b, s, e):
        if t == b"meta":
            _meta(b, cs, ce, tags)
            continue
        key = _KEYS.get(t)
        if key is None or key in tags:
            continue
        # QuickTime int'l text: u16 len + u16 lang + text. 3GPP asset atoms (titl/auth/dscp...) are NOT read by
        # ffmpeg 7 (checked: `ffmpeg -i` on a -f 3gp file with -metadata title shows no title) -> skipped.
        if t[:1] == b"\xa9" and ce - cs >= 4:
            n = struct.unpack_from(">H", b, cs)[0]
            if 0 < n and cs + 4 + n <= ce:
                tags[key] = _txt(b[cs + 4:cs + 4 + n])
                continue
            v = _data_value(b, cs, ce)
            if v is not None:
                tags[key] = v


def _meta(b, s, e, tags):
    cs = _meta_children(b, s, e)
    kids = _boxes(b, cs, e)
    keys = []
    for t, ks, ke in kids:
        if t == b"keys" and ke - ks >= 8:
            n = struct.unpack_from(">I", b, ks + 4)[0]
            p = ks + 8
            for _ in range(min(n, 4096)):
                if p + 8 > ke:
                    break
                sz = struct.unpack_from(">I", b, p)[0]
                if sz < 8 or p + sz > ke:
                    break
                keys.append(_txt(b[p + 8:p + sz]))
                p += sz
    for t, ls, le in kids:
        if t != b"ilst":
            continue
        for it, is_, ie in _boxes(b, ls, le):
            if keys and it[:1] != b"\xa9":
                idx = struct.unpack(">I", it)[0]
                key = keys[idx - 1] if 1 <= idx <= len(keys) else None
            elif it == b"----":
                nm = _child(b, is_, ie, b"name")
                key = _txt(b[nm[0] + 4:nm[1]]) if nm else None
            else:
                key = _KEYS.get(it) or (it.decode("latin-1") if it.isalnum() else None)
            if not key or key in tags:
                continue
            v = _data_value(b, is_, ie)
            if v is not None:
                tags[key] = v


def _norm(k):
    return "".join(c if c.isalnum() else "_" for c in (k or "").lower()).strip("_")


def atom_value(data, ctx):
    if data is None:
        return None
    try:
        r = _parse(data)
    except Exception:  # noqa: BLE001 -- defensive: never raise past the extractor
        return None
    if r is None:
        return "none"
    f = (ctx.get("field") or "").lower()
    if f.startswith("major_brand") or f.startswith("minor_version") or f == "compatible_brands":
        f = "ftyp_" + f
    ft = r.get("ftyp")
    if f.startswith("ftyp_"):
        if ft is None:
            return "none"
        if f == "ftyp_major_brand":
            return ft[0].rstrip(b" \0").decode("latin-1")
        if f == "ftyp_major_brand_raw":
            return ft[0].decode("latin-1")
        if f == "ftyp_minor_version":
            return ft[1]
        if f == "ftyp_compatible_brands":
            return [x.decode("latin-1") for x in ft[2]]
        return None
    if f in ("top_level_atoms", "top_level_box_types"):
        return r["top"]
    if f in ("track_count", "trak_count"):
        return len(r["hdlr"]) if "mvhd" in r or r["hdlr"] else "none"
    if f in ("track_handler_types", "handler_types"):
        return [h if h is not None else "none" for h in r["hdlr"]] if r["hdlr"] else "none"
    if f == "mdhd_languages":
        return [x if x is not None else "und" for x in r["lang"]] if r["lang"] else "none"
    mv = r.get("mvhd")
    if f.startswith("mvhd_"):
        if mv is None:
            return "none"
        if f in ("mvhd_creation_time_utc", "mvhd_creation_time"):
            return _utc(mv["ctime"])
        if f in ("mvhd_modification_time_utc", "mvhd_modification_time"):
            return _utc(mv["mtime"])
        if f == "mvhd_timescale":
            return mv["timescale"]
        if f == "mvhd_duration":
            return mv["duration"]
        if f == "mvhd_duration_seconds":
            return "%.6f" % (mv["duration"] / mv["timescale"]) if mv["timescale"] else "none"
        if f == "mvhd_next_track_id":
            return mv["next"] if mv["next"] is not None else "none"
        if f == "mvhd_version":
            return mv["version"]
    return None


def tag_value(data, ctx):
    """<fmt>.tag_<key>: ffprobe format tag of an MP4/MOV, key matched with non-alnum folded to '_'."""
    if data is None:
        return None
    try:
        r = _parse(data)
    except Exception:  # noqa: BLE001
        return None
    if r is None:
        return "none"
    f = (ctx.get("field") or "").lower()
    want = _norm(f[4:] if f.startswith("tag_") else f)
    for k, v in r["tags"].items():
        if _norm(k) == want:
            return v
    return "none"
