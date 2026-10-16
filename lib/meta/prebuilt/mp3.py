"""MP3 ID3v2 / ID3v1 tag fields (prebuilt, SPECULATIVE -- never GM-asked yet).

ID3v2 (id3.org 2.2/2.3/2.4): "ID3" major u8 revision u8 flags u8 size[4] (syncsafe, 7 bits per byte, excludes the
10-byte header); flag 0x40 = an extended header follows (v2.3: size u32be excluding itself; v2.4: syncsafe size
including itself). Frames: v2.3/2.4 id[4] size[4] (v2.3 plain u32be, v2.4 syncsafe) flags[2]; v2.2 id[3] size[3]
(the v2.2 ids TT2/TP1/TAL/COM/... are mapped onto their v2.3 names). Text frames (T***): encoding u8 (0 latin-1,
1 UTF-16 with BOM, 2 UTF-16BE, 3 UTF-8) + text; a v2.4 multi-value list is NUL-separated -> joined with "/" (how
exiftool prints it). COMM: encoding, language[3], short description NUL-terminated, text -> id3_comment = the text
of the first COMM with an empty description (else the first COMM; iTunes' "iTunNORM"-style COMMs are skipped).
id3_version = "2.<major>.<revision>" (the `file` spelling "ID3 version 2.3.0"; mutagen version tuple); a file with
only an ID3v1 trailer -> "1.0" / "1.1" (v1.1 = comment byte 28 is 0 and byte 29 the track).
ID3v1 fallback for title/artist/album/year/comment/genre: the last 128 bytes "TAG" title[30] artist[30] album[30]
year[4] comment[30] genre u8 (latin-1, NUL/space trimmed). id3_<frameid> (family) = any text frame by its 4-char id
(id3_tit2, id3_tpe1, ...). id3_frame_ids = frame ids in stored order. Unsynchronisation (header flag 0x80) is
undone before frame parsing (v2.3 whole-tag). Not an ID3-tagged file (decoy: a WAV/FLAC renamed .mp3) -> "none";
a frame the tag lacks -> "none"."""
import struct

FIELDS = {
    ("mp3", "id3_title"): "mp3_value",
    ("mp3", "id3_artist"): "mp3_value",
    ("mp3", "id3_album"): "mp3_value",
    ("mp3", "id3_album_artist"): "mp3_value",
    ("mp3", "id3_year"): "mp3_value",
    ("mp3", "id3_date"): "mp3_value",
    ("mp3", "id3_recording_time"): "mp3_value",
    ("mp3", "id3_genre"): "mp3_value",
    ("mp3", "id3_track"): "mp3_value",
    ("mp3", "id3_track_number"): "mp3_value",
    ("mp3", "id3_composer"): "mp3_value",
    ("mp3", "id3_encoder"): "mp3_value",
    ("mp3", "id3_encoded_by"): "mp3_value",
    ("mp3", "id3_encoder_settings"): "mp3_value",
    ("mp3", "id3_publisher"): "mp3_value",
    ("mp3", "id3_copyright"): "mp3_value",
    ("mp3", "id3_comment"): "mp3_value",
    ("mp3", "id3_comments"): "mp3_value",
    ("mp3", "id3_comm"): "mp3_value",
    ("mp3", "id3_comment_text"): "mp3_value",
    ("mp3", "id3_version"): "mp3_value",
    ("mp3", "id3v2_version"): "mp3_value",
    ("mp3", "id3_tag_version"): "mp3_value",
    ("mp3", "tag_version"): "mp3_value",
    ("mp3", "id3v2_major_version"): "mp3_value",
    ("mp3", "id3_major_version"): "mp3_value",
    ("mp3", "id3_tag_size"): "mp3_value",
    ("mp3", "id3v2_tag_size"): "mp3_value",
    ("mp3", "id3_size"): "mp3_value",
    ("mp3", "id3_frame_ids"): "mp3_value",
    ("mp3", "id3_frame_names"): "mp3_value",
    ("mp3", "id3v2_frame_ids"): "mp3_value",
    ("mp3", "frame_ids"): "mp3_value",
    ("mp3", "title"): "mp3_value",
    ("mp3", "artist"): "mp3_value",
    ("mp3", "album"): "mp3_value",
    ("mp3", "comment"): "mp3_value",
    ("mp3", "id3v2_title"): "mp3_value",
    ("mp3", "id3v2_artist"): "mp3_value",
    ("mp3", "id3v2_album"): "mp3_value",
    ("mp3", "id3v2_comment"): "mp3_value",
    ("mp3", "id3v1_title"): "mp3_value",
    ("mp3", "id3v1_artist"): "mp3_value",
    ("mp3", "id3v1_album"): "mp3_value",
    ("mp3", "id3v1_year"): "mp3_value",
    ("mp3", "id3v1_comment"): "mp3_value",
    ("mp3", "id3v1_genre"): "mp3_value",
    ("mp3", "id3_*"): "mp3_value",
    ("id3", "title"): "mp3_value",
    ("id3", "artist"): "mp3_value",
    ("id3", "album"): "mp3_value",
    ("id3", "comment"): "mp3_value",
    ("id3", "version"): "mp3_value",
    ("id3", "id3_title"): "mp3_value",
    ("id3", "id3_artist"): "mp3_value",
    ("id3", "id3_album"): "mp3_value",
    ("id3", "id3_comment"): "mp3_value",
    ("id3", "id3_version"): "mp3_value",
    ("id3", "tag_size"): "mp3_value",
    ("id3", "frame_ids"): "mp3_value",
}

# field stem -> v2.3 frame id (title/artist/... also fall back to ID3v1)
_FRAMES = {"title": "TIT2", "artist": "TPE1", "album": "TALB", "album_artist": "TPE2", "year": "TYER",
           "date": "TDRC", "recording_time": "TDRC", "genre": "TCON", "track": "TRCK", "track_number": "TRCK",
           "composer": "TCOM", "encoder": "TSSE", "encoded_by": "TENC", "encoder_settings": "TSSE",
           "publisher": "TPUB", "copyright": "TCOP"}
_V22 = {"TT2": "TIT2", "TP1": "TPE1", "TP2": "TPE2", "TAL": "TALB", "TYE": "TYER", "TCO": "TCON", "TRK": "TRCK",
        "TCM": "TCOM", "TEN": "TENC", "TSS": "TSSE", "TPB": "TPUB", "TCR": "TCOP", "COM": "COMM", "TT1": "TIT1",
        "TT3": "TIT3", "TXX": "TXXX", "PIC": "APIC", "ULT": "USLT"}
_V1 = {"title": (3, 33), "artist": (33, 63), "album": (63, 93), "year": (93, 97), "comment": (97, 127)}


def _syncsafe(b):
    return (b[0] & 0x7F) << 21 | (b[1] & 0x7F) << 14 | (b[2] & 0x7F) << 7 | (b[3] & 0x7F)


def _dec(enc, raw):
    if enc == 1:
        s = raw.decode("utf-16", "replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-16-le", "replace")
    elif enc == 2:
        s = raw.decode("utf-16-be", "replace")
    elif enc == 3:
        s = raw.decode("utf-8", "replace")
    else:
        s = raw.decode("latin-1")
    return s


def _split_term(enc, raw):
    """(head, rest) split at the first encoding-appropriate NUL terminator."""
    if enc in (1, 2):
        i = 0
        while i + 1 < len(raw):
            if raw[i] == 0 and raw[i + 1] == 0:
                return raw[:i], raw[i + 2:]
            i += 2
        return raw, b""
    i = raw.find(b"\x00")
    return (raw, b"") if i < 0 else (raw[:i], raw[i + 1:])


def _text(body):
    if not body:
        return ""
    enc, raw = body[0], body[1:]
    vals = [v.strip() for v in _dec(enc, raw).split("\x00")]
    vals = [v.lstrip("﻿") for v in vals if v.lstrip("﻿")]
    return "/".join(vals)


def _comm(body):
    """(description, text) of a COMM frame body."""
    if len(body) < 4:
        return "", ""
    enc = body[0]
    desc, txt = _split_term(enc, body[4:])
    return _dec(enc, desc).lstrip("﻿").strip("\x00 "), _dec(enc, txt).lstrip("﻿").rstrip("\x00").strip()


def _id3v2(b):
    """(major, revision, tag_size, [(frame_id, body)]) or None."""
    if len(b) < 10 or bytes(b[:3]) != b"ID3" or b[3] not in (2, 3, 4) or any(x & 0x80 for x in b[6:10]):
        return None
    major, rev, flags = b[3], b[4], b[5]
    size = _syncsafe(b[6:10])
    tag = bytes(b[10:10 + size])
    if flags & 0x80 and major < 4:
        tag = tag.replace(b"\xff\x00", b"\xff")
    off = 0
    if flags & 0x40 and major >= 3 and len(tag) >= 4:
        off = struct.unpack_from(">I", tag, 0)[0] + 4 if major == 3 else _syncsafe(tag[:4])
    frames = []
    while True:
        if major == 2:
            if off + 6 > len(tag) or tag[off] == 0:
                break
            fid = tag[off:off + 3].decode("latin-1")
            fsz = int.from_bytes(tag[off + 3:off + 6], "big")
            body = tag[off + 6:off + 6 + fsz]
            off += 6 + fsz
            fid = _V22.get(fid, fid)
        else:
            if off + 10 > len(tag) or tag[off] == 0:
                break
            fid = tag[off:off + 4].decode("latin-1")
            fsz = _syncsafe(tag[off + 4:off + 8]) if major == 4 else struct.unpack_from(">I", tag, off + 4)[0]
            fflags = tag[off + 9]
            body = tag[off + 10:off + 10 + fsz]
            off += 10 + fsz
            if major == 4 and fflags & 0x02:
                body = body.replace(b"\xff\x00", b"\xff")
            if major == 4 and fflags & 0x01 and len(body) >= 4:     # data length indicator
                body = body[4:]
        if not fid.isalnum():
            break
        frames.append((fid, body))
    return major, rev, size, frames


def _id3v1(b):
    t = bytes(b[-128:]) if len(b) >= 128 else b""
    return t if t[:3] == b"TAG" else None


def _v1_str(raw):
    return raw.split(b"\x00")[0].decode("latin-1").strip()


def mp3_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), ctx or {})
    except Exception:  # noqa: BLE001 -- a malformed tag never raises past the extractor
        return None


def _value(b, ctx):
    f = ctx.get("field") or ""
    v2, v1 = _id3v2(b), _id3v1(b)
    if v2 is None and v1 is None:
        return "none"
    if f.endswith("_*") or f in ("id3_*",):
        f = "id3_" + (ctx.get("param") or "")
    stem = f
    for p in ("id3v2_", "id3v1_", "id3_"):
        if stem.startswith(p):
            stem = stem[len(p):]
            break
    only_v1 = f.startswith("id3v1_")
    only_v2 = f.startswith("id3v2_")
    if stem in ("version", "tag_version"):
        if v2:
            return "2.%d.%d" % (v2[0], v2[1])
        return "1.1" if v1[125] == 0 and v1[126] != 0 else "1.0"
    if stem == "major_version":
        return v2[0] if v2 else "none"
    if stem in ("tag_size", "size"):
        return v2[2] if v2 else "none"
    if stem in ("frame_ids", "frame_names"):
        return [fid for fid, _ in v2[3]] if v2 else "none"
    frames = v2[3] if (v2 and not only_v1) else []
    if stem in ("comment", "comments", "comm", "comment_text"):
        comms = [_comm(body) for fid, body in frames if fid == "COMM"]
        comms = [c for c in comms if not c[0].lower().startswith("itun")] or comms
        pick = next((c for c in comms if not c[0]), comms[0] if comms else None)
        if pick is not None:
            return pick[1]
        if v1 and not only_v2:
            return _v1_str(v1[97:125] if v1[125] == 0 and v1[126] != 0 else v1[97:127]) or "none"
        return "none"
    fid = _FRAMES.get(stem) or (stem.upper() if len(stem) in (3, 4) and stem.isalnum() else None)
    if fid is None:
        return None
    if fid == "TYER":
        cands = ("TYER", "TDRC")
    elif fid == "TDRC":
        cands = ("TDRC", "TYER")
    else:
        cands = (_V22.get(fid, fid),)
    for c in cands:
        for fi, body in frames:
            if fi == c:
                return _text(body)
    if v1 and not only_v2:
        if stem in _V1:
            s, e = _V1[stem]
            return _v1_str(v1[s:e]) or "none"
        if stem == "genre":
            return str(v1[127]) if v1[127] != 255 else "none"
    return "none"
