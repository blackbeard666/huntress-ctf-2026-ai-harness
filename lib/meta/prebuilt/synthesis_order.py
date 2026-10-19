"""Cross-FILE ordering / grouping synthesis with a non-sha256 key (prebuilt, SPECULATIVE; spelling never GM-verified).
Coverage-atlas row "synthesis siblings": ids `metadata-day-NN-synthesis-<key>-order|groups|<x>` over the question's
`Files: [...]` list (parsed like lib.meta.synthesis.digest_order; members of the artifact's container). Keys:
  * size = byte length; md5 / sha1 / sha512 = hashlib hexdigest of the full file (sha256_order is NOT registered:
    the D15-D17 `-synthesis-sha256-order` ids would parse here, and the lane call only holds the lone member);
  * mtime = the container's central-directory DOS date/time of each member (zipfile ZipInfo.date_time, naive local);
  * embedded time = the file's own timestamp, compared as UTC epoch: EXIF DateTimeOriginal (0x9003, else DateTime
    0x0132; naive -> UTC unless OffsetTimeOriginal), PDF /CreationDate (D:YYYYMMDDHHmmSS+hh'mm'), e-mail Date header
    (RFC 5322), MP4/MOV mvhd creation_time (1904 epoch), OOXML docProps/core.xml dcterms:created. A file with none
    sorts after the dated ones (then by name). The *_order / newest / oldest fields use the embedded time when the
    field or question text says created / captured / exif / embedded / Date header / creation, else the DOS mtime;
  * duration = media.duration_seconds (else format_duration_seconds) via lib.meta.answer; non-media files are left out;
  * codec = primary video codec_name, else primary audio codec_name (ffprobe names, lib.meta media extractors).
Orders ascending, ties by filename; "descending" / "newest first" / "largest first" / "longest first" / "most recent
first" in the text reverses the key (ties still by name). Lists -> compact JSON. codec_groups = {codec: [sorted
names]} (sorted keys). extension_mismatch_files = names whose magic family disagrees with their extension, in Files
order. largest/smallest/newest/oldest/longest/shortest_file = one name.
order_value(question, get_bytes, field, mtimes=None) is the solver-facing call; through lib.meta.answer the extractor
reads siblings from ctx["read"] when supplied, else from `data` when the artifact IS the container zip (all members
when the question names no Files list). A lone non-zip member / no reader -> None; a zip with no usable member ->
"none"."""
import datetime as _dt
import hashlib
import io
import re
import struct

FIELDS = {
    ("synthesis", "size_order"): "order_value",
    ("synthesis", "file_size_order"): "order_value",
    ("synthesis", "size_bytes_order"): "order_value",
    ("synthesis", "byte_size_order"): "order_value",
    ("synthesis", "md5_order"): "order_value",
    ("synthesis", "sha1_order"): "order_value",
    ("synthesis", "sha512_order"): "order_value",
    ("synthesis", "mtime_order"): "order_value",
    ("synthesis", "dos_mtime_order"): "order_value",
    ("synthesis", "zip_mtime_order"): "order_value",
    ("synthesis", "modification_time_order"): "order_value",
    ("synthesis", "modified_order"): "order_value",
    ("synthesis", "time_order"): "order_value",
    ("synthesis", "timestamp_order"): "order_value",
    ("synthesis", "chronological_order"): "order_value",
    ("synthesis", "date_order"): "order_value",
    ("synthesis", "creation_time_order"): "order_value",
    ("synthesis", "created_order"): "order_value",
    ("synthesis", "embedded_timestamp_order"): "order_value",
    ("synthesis", "capture_time_order"): "order_value",
    ("synthesis", "duration_order"): "order_value",
    ("synthesis", "media_duration_order"): "order_value",
    ("synthesis", "codec_groups"): "order_value",
    ("synthesis", "codec_name_groups"): "order_value",
    ("synthesis", "extension_mismatch_files"): "order_value",
    ("synthesis", "extension_mismatch_filenames"): "order_value",
    ("synthesis", "mismatched_extension_files"): "order_value",
    ("synthesis", "magic_mismatch_files"): "order_value",
    ("synthesis", "disguised_files"): "order_value",
    ("synthesis", "largest_file"): "order_value",
    ("synthesis", "largest_filename"): "order_value",
    ("synthesis", "smallest_file"): "order_value",
    ("synthesis", "smallest_filename"): "order_value",
    ("synthesis", "newest_file"): "order_value",
    ("synthesis", "newest_filename"): "order_value",
    ("synthesis", "oldest_file"): "order_value",
    ("synthesis", "oldest_filename"): "order_value",
    ("synthesis", "longest_file"): "order_value",
    ("synthesis", "shortest_file"): "order_value",
}

_DESC = re.compile(r"\b(descending|newest first|most recent first|latest first|largest first|biggest first|"
                   r"longest first|reverse chronological)\b", re.I)
_EMBEDDED = re.compile(r"creat|captur|exif|embedded|date header|datetimeoriginal|mvhd|internal timestamp", re.I)
_EPOCH_1904 = _dt.datetime(1904, 1, 1, tzinfo=_dt.timezone.utc)


# ---------------------------------------------------------------- magic vs extension

_TEXT_EXT = {"txt", "csv", "log", "md", "json", "xml", "html", "htm", "ini", "cfg", "conf", "yaml", "yml", "eml",
             "ps1", "js", "vbs", "bat", "cmd", "py", "sh", "url", "svg", "rtf", "hta", "tsv", "reg", "mbox"}


def _kind(b):
    """Set of extensions the content's magic allows, or None (unknown binary / no magic)."""
    if not b:
        return None
    h = b[:16]
    if h.startswith(b"\xff\xd8\xff"):
        return {"jpg", "jpeg", "jpe", "jfif"}
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return {"png"}
    if h.startswith((b"GIF87a", b"GIF89a")):
        return {"gif"}
    if h.startswith(b"BM") and len(b) > 14:
        return {"bmp", "dib"}
    if h.startswith((b"II*\0", b"MM\0*")):
        return {"tif", "tiff", "dng", "nef", "cr2", "arw"}
    if h.startswith(b"%PDF"):
        return {"pdf"}
    if h.startswith(b"PK\x03\x04") or h.startswith(b"PK\x05\x06"):
        return {"zip", "docx", "xlsx", "pptx", "docm", "xlsm", "pptm", "dotx", "dotm", "odt", "ods", "odp", "apk",
                "jar", "epub", "xpi", "vsix", "nupkg", "kmz", "ipa", "aar", "whl"}
    if h.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return {"doc", "xls", "ppt", "msi", "msg", "dot", "xlt", "pot", "msp", "mst", "ole", "cfb", "vsd", "pub"}
    if h.startswith(b"MZ"):
        return {"exe", "dll", "sys", "scr", "ocx", "cpl", "drv", "efi", "com", "mui", "ax"}
    if h.startswith(b"\x7fELF"):
        return {"elf", "so", "bin", "o", "ko", "out", ""}
    if h.startswith(b"RIFF") and len(b) >= 12:
        return {b"WAVE": {"wav", "wave", "bwf"}, b"AVI ": {"avi"}, b"WEBP": {"webp"}}.get(b[8:12], {"riff"})
    if h.startswith(b"fLaC"):
        return {"flac"}
    if h.startswith(b"OggS"):
        return {"ogg", "oga", "ogv", "opus", "spx", "ogx"}
    if h.startswith(b"ID3") or (len(b) > 1 and b[0] == 0xFF and (b[1] & 0xE0) == 0xE0 and (b[1] & 0x06)):
        return {"mp3", "mp2", "mpa"}
    if h.startswith(b"FORM") and b[8:12] in (b"AIFF", b"AIFC"):
        return {"aiff", "aif", "aifc"}
    if b[4:8] == b"ftyp":
        brand = b[8:12]
        if brand in (b"heic", b"heix", b"mif1", b"msf1", b"heim", b"heis", b"hevc", b"hevx"):
            return {"heic", "heif", "hif"}
        if brand in (b"avif", b"avis"):
            return {"avif"}
        if brand.startswith(b"3g"):
            return {"3gp", "3g2", "mp4"}
        return {"mp4", "m4a", "m4v", "m4b", "mov", "qt", "f4v", "3gp"}
    if b[4:8] in (b"moov", b"mdat", b"wide", b"free"):
        return {"mov", "qt", "mp4"}
    if h.startswith(b"\x1a\x45\xdf\xa3"):
        return {"mkv", "webm", "mka", "mk3d"}
    if h.startswith(b"\x1f\x8b"):
        return {"gz", "tgz", "gzip"}
    if h.startswith(b"7z\xbc\xaf\x27\x1c"):
        return {"7z"}
    if h.startswith(b"Rar!"):
        return {"rar"}
    if h.startswith(b"SQLite format 3\0"):
        return {"sqlite", "db", "sqlite3", "db3"}
    if h.startswith(b"L\0\0\0\x01\x14\x02\0"):
        return {"lnk"}
    if h.startswith(b"MSCF"):
        return {"cab"}
    if h.startswith(b"ElfFile\0"):
        return {"evtx"}
    if h.startswith(b"regf"):
        return {"dat", "hive", "regf", ""}
    if h.startswith(b"{\\rtf"):
        return {"rtf", "doc"}
    if h[:4] in (b"\xca\xfe\xba\xbe", b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"):
        return {"macho", "dylib", "bundle", "o", "", "class"}
    if h.startswith(b"dex\n"):
        return {"dex"}
    if h.startswith((b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\n\r\r\n")):
        return {"pcap", "pcapng", "cap"}
    if h.startswith(b"\0\0\1\0"):
        return {"ico"}
    if _is_text(b):
        return "text"
    return None


def _is_text(b):
    s = b[:4096]
    if s.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")):
        return True
    if b"\0" in s:
        return False
    try:
        s.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return sum(1 for c in s if c >= 0x80) < len(s) // 10


def _mismatch(name, b):
    """True / False, or None when undecidable (unknown binary magic and an extension with no magic)."""
    base = str(name).rsplit("/", 1)[-1]
    ext = base.rsplit(".", 1)[-1].lower() if "." in base else ""
    k = _kind(b)
    if k == "text":
        return ext not in _TEXT_EXT and ext != ""
    if k is None:
        return None
    return ext not in k


# ---------------------------------------------------------------- embedded timestamps

def _utc(d):
    return (d if d.tzinfo else d.replace(tzinfo=_dt.timezone.utc)).timestamp()


def _exif_time(b):
    try:
        from PIL import Image
        ex = Image.open(io.BytesIO(b)).getexif()
        sub = ex.get_ifd(0x8769) or {}
        v = sub.get(0x9003) or sub.get(0x9004) or ex.get(0x0132)
        if not v:
            return None
        v = v.decode("latin-1") if isinstance(v, bytes) else str(v)
        d = _dt.datetime.strptime(v.strip("\0 ")[:19], "%Y:%m:%d %H:%M:%S")
        off = sub.get(0x9011)
        m = re.match(r"([+-])(\d\d):(\d\d)", str(off or ""))
        if m:
            tz = _dt.timedelta(hours=int(m.group(2)), minutes=int(m.group(3)))
            d = d.replace(tzinfo=_dt.timezone(tz if m.group(1) == "+" else -tz))
        return _utc(d)
    except Exception:  # noqa: BLE001 - not an EXIF still
        return None


def _pdf_string(b, i):
    """The decoded PDF string object starting at b[i] ('(' literal with escapes, or '<hex>'), or None."""
    if b[i:i + 1] == b"<":
        j = b.find(b">", i)
        raw = bytes.fromhex(re.sub(rb"\s", b"", b[i + 1:j]).decode("ascii", "replace")) if j > 0 else b""
    elif b[i:i + 1] == b"(":
        out, depth, j = bytearray(), 1, i + 1
        while j < len(b) and depth:
            c = b[j]
            if c == 0x5C and j + 1 < len(b):
                n = b[j + 1:j + 2]
                oc = re.match(rb"[0-7]{1,3}", b[j + 1:j + 4])
                if oc:
                    out.append(int(oc.group(0), 8) & 0xFF)
                    j += 1 + len(oc.group(0))
                    continue
                out += {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f"}.get(n, n)
                j += 2
                continue
            depth += (c == 0x28) - (c == 0x29)
            if depth:
                out.append(c)
            j += 1
        raw = bytes(out)
    else:
        return None
    if raw[:2] == b"\xfe\xff":
        return raw[2:].decode("utf-16-be", "replace")
    return raw.decode("latin-1")


def _pdf_time(b):
    m = re.search(rb"/CreationDate\s*([(<])", b)
    try:
        v = _pdf_string(b, m.start(1)) if m else None
    except ValueError:
        v = None
    if v is None:   # Info dict inside a compressed object stream
        try:
            from pypdf import PdfReader
            v = str((PdfReader(io.BytesIO(b)).metadata or {}).get("/CreationDate") or "") or None
        except Exception:  # noqa: BLE001
            return None
    m = re.match(r"\s*(?:D:)?(\d{4})(\d\d)?(\d\d)?(\d\d)?(\d\d)?(\d\d)?([Zz+-])?(\d\d)?'?(\d\d)?", v or "")
    if not m:
        return None
    g = [int(x) if x else d for x, d in zip(m.groups()[:6], (0, 1, 1, 0, 0, 0))]
    try:
        d = _dt.datetime(*g)
    except ValueError:
        return None
    sign = m.group(7)
    if sign in ("+", "-") and m.group(8):
        tz = _dt.timedelta(hours=int(m.group(8)), minutes=int(m.group(9) or 0))
        d = d.replace(tzinfo=_dt.timezone(tz if sign == "+" else -tz))
    return _utc(d)


def _mail_time(b):
    if b"\0" in b[:512]:
        return None
    head = re.split(rb"\r?\n\r?\n", b, 1)[0]
    if not re.search(rb"(?im)^(from|subject|message-id|received)[ \t]*:", head):
        return None
    m = re.search(rb"(?im)^Date[ \t]*:(.*(?:\r?\n[ \t].*)*)", head)
    if not m:
        return None
    from email.utils import parsedate_to_datetime
    try:
        return _utc(parsedate_to_datetime(re.sub(rb"\r?\n[ \t]", b" ", m.group(1)).decode("latin-1").strip()))
    except (TypeError, ValueError, IndexError, OverflowError):
        return None


def _mvhd_time(b):
    if b[4:8] not in (b"ftyp", b"moov", b"wide", b"free", b"mdat"):
        return None
    i = b.find(b"mvhd", 0, 1 << 22)
    if i < 4 or i + 16 > len(b):
        return None
    ver = b[i + 4]
    t = struct.unpack_from(">Q" if ver == 1 else ">I", b, i + 8)[0]
    return (_EPOCH_1904 + _dt.timedelta(seconds=t)).timestamp() if t else None


def _ooxml_time(b):
    if b[:4] != b"PK\x03\x04":
        return None
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
        x = z.read("docProps/core.xml").decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None
    m = re.search(r"<dcterms:created[^>]*>\s*([^<]+?)\s*<", x)
    if not m:
        return None
    try:
        return _utc(_dt.datetime.fromisoformat(m.group(1).replace("Z", "+00:00")))
    except ValueError:
        return None


def embedded_time(b):
    """UTC epoch of the file's own creation / capture timestamp, or None."""
    b = bytes(b)
    if b[:3] == b"\xff\xd8\xff" or b[:4] in (b"II*\0", b"MM\0*"):
        return _exif_time(b)
    if b[:4] == b"%PDF":
        return _pdf_time(b)
    for f in (_mvhd_time, _ooxml_time, _mail_time):
        t = f(b)
        if t is not None:
            return t
    return None


# ---------------------------------------------------------------- media

def _media(b, field):
    from .. import answer
    v, _ = answer("x", {"question": "Determine media.%s for x." % field}, b)
    return None if v in (None, "none", "") else v


def _duration(b):
    for f in ("duration_seconds", "format_duration_seconds"):
        v = _media(b, f)
        try:
            if v is not None:
                return float(v)
        except ValueError:
            continue
    try:   # MP3 (gapless decoded length) / MP4 audio / Ogg: the equivalence module's sample count
        from .synthesis_media import audio_info
        s = (audio_info(b) or {}).get("seconds")
        if s:
            return float(s)
    except Exception:  # noqa: BLE001
        pass
    try:   # MP4 / MOV / Matroska video: the longest stream duration
        from .media_streams import streams
        ds = [float(x["duration"]) for x in streams(b) or () if x.get("duration") not in (None, "", "N/A")]
        return max(ds) if ds else None
    except Exception:  # noqa: BLE001
        return None


def _codec(b):
    return _media(b, "primary_video_codec_name") or _media(b, "primary_audio_codec_name")


# ---------------------------------------------------------------- the solver-facing call

def _text(question):
    return str(((question or {}).get("question") if isinstance(question, dict) else question) or "")


def _key_kind(field, text):
    f = field or ""
    if f.startswith(("largest", "smallest")) or "size" in f:
        return "size"
    for a in ("md5", "sha1", "sha512"):
        if f.startswith(a):
            return a
    if "duration" in f or f.startswith(("longest", "shortest")):
        return "duration"
    if "codec" in f:
        return "codec"
    if "mismatch" in f or "disguised" in f:
        return "mismatch"
    if any(k in f for k in ("creat", "embedded", "capture")):
        return "embedded"
    if any(k in f for k in ("dos", "zip_", "modif", "mtime")):
        return "dos"
    return "embedded" if _EMBEDDED.search(text) else "dos"   # time/date/timestamp/chronological, newest/oldest


def order_value_of(names, get_bytes, field, text="", mtimes=None):
    """The raw value (list / dict / str) for `field` over `names`; None = cannot answer, "none" = nothing applies."""
    kind = _key_kind(field, text)
    keyed = []
    for n in names:
        if kind == "dos":
            t = (mtimes or {}).get(n)
            if t is None:
                return None
            keyed.append((tuple(t), n))
            continue
        b = get_bytes(n)
        if b is None:
            return None
        b = bytes(b)
        if kind == "size":
            keyed.append((len(b), n))
        elif kind in ("md5", "sha1", "sha512"):
            keyed.append((hashlib.new(kind, b).hexdigest(), n))
        elif kind == "embedded":
            keyed.append((embedded_time(b), n))
        elif kind == "duration":
            d = _duration(b)
            if d is not None:
                keyed.append((d, n))
        elif kind == "codec":
            c = _codec(b)
            if c is not None:
                keyed.append((str(c), n))
        else:
            mm = _mismatch(n, b)
            if mm:
                keyed.append((True, n))
    f = field or ""
    if kind == "mismatch":
        return [n for _, n in keyed] or "none"
    if not keyed:
        return "none"
    if kind == "codec":
        out = {}
        for c, n in keyed:
            out.setdefault(c, []).append(n)
        return {c: sorted(out[c]) for c in sorted(out)}
    if kind == "embedded":
        dated = [k for k in keyed if k[0] is not None]
        if not dated:
            return "none"
        undated = sorted(n for t, n in keyed if t is None)
    else:
        dated, undated = keyed, []
    if f.startswith(("largest", "newest", "longest")):
        return sorted(dated, key=lambda k: (_neg(k[0]), k[1]))[0][1]
    if f.startswith(("smallest", "oldest", "shortest")):
        return sorted(dated, key=lambda k: (k[0], k[1]))[0][1]
    if _DESC.search(text):
        return [n for _, n in sorted(dated, key=lambda k: (_neg(k[0]), k[1]))] + undated
    return [n for _, n in sorted(dated)] + undated


def _neg(v):
    if isinstance(v, tuple):
        return tuple(-x for x in v)
    if isinstance(v, str):
        return tuple(-ord(c) for c in v)
    return -v


def order_value_for(question, get_bytes, field, mtimes=None):
    """Solver-facing: the `field` value over the question's Files list read via get_bytes(name) ({name: DOS
    (Y, M, D, h, m, s)} in `mtimes` for the container-mtime keys), or None."""
    from .synthesis_media import file_list
    names = file_list(question)
    if not names:
        return None
    return order_value_of(names, get_bytes, field, _text(question), mtimes)


def _zip_mtimes(data):
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(bytes(data)))
    except (zipfile.BadZipFile, ValueError, OSError, EOFError, NotImplementedError):
        return None
    out = {}
    for i in z.infolist():
        if not i.is_dir():
            out.setdefault(i.filename, i.date_time)
            out.setdefault(i.filename.rsplit("/", 1)[-1], i.date_time)
    return out


def order_value(data, ctx):
    """synthesis.<order / group field> (see the module docstring)."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        if not names:
            return "none"
        mt = ctx.get("mtimes") if isinstance(ctx.get("mtimes"), dict) else None
        if mt is None and from_zip:
            mt = _zip_mtimes(data)
        v = order_value_of(names, read, ctx.get("field") or "", _text(ctx.get("question")), mt)
        return v if (v != "none" or from_zip) else None
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
