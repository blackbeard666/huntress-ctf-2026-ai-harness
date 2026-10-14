"""OLE2 / Compound File Binary (legacy Office .doc/.xls/.ppt, .msg, thumbs.db) fields (prebuilt, SPECULATIVE).

SummaryInformation = stream "\\x05SummaryInformation" (MS-OLEPS property set, FMTID F29F85E0-4FF9-1068-AB91-
08002B27B3D9), first section: PIDs 2 title, 3 subject, 4 author, 5 keywords, 6 comments, 7 template, 8 last saved by,
9 revision number (VT_LPSTR text in Office, e.g. "2" -- returned as stored), 11 last printed, 12 create time,
13 last save time, 14 pages, 15 words, 16 chars, 18 application name, 19 security. String code page = PID 1.
Timestamps: VT_FILETIME (100 ns since 1601-01-01 UTC) rendered ISO-8601 UTC "YYYY-MM-DDTHH:MM:SSZ" (same spelling as
lnk.*_time); FILETIME is UTC by spec, so no local-time shift (exiftool's FlashPix:CreateDate prints it converted).
A present-but-empty string / zero FILETIME = "none" (Word writes an empty Title).
stream_names: every STREAM directory entry in STORED directory-entry order (not olefile's sorted listdir), full path
"Storage/Stream" for nested ones, names verbatim (control prefixes "\\x05"/"\\x01" kept, JSON-escaped by spell).
Not CFB / no SummaryInformation / damaged -> "none" for the summary fields; not CFB -> "none" for stream_names."""
import datetime
import struct

from ..cfb import MAGIC, cfb_streams

_PID = {"title": 2, "subject": 3, "author": 4, "keywords": 5, "comments": 6, "template": 7, "last_saved_by": 8,
        "last_author": 8, "last_modified_by": 8, "revision_number": 9, "last_printed": 11, "last_printed_time": 11,
        "create_time": 12, "create_time_utc": 12, "create_date": 12, "creation_time": 12, "created_time": 12,
        "last_save_time": 13, "last_save_time_utc": 13, "last_saved_time": 13, "modify_time": 13,
        "page_count": 14, "word_count": 15, "char_count": 16, "character_count": 16, "application_name": 18,
        "app_name": 18, "creating_application": 18, "security": 19}

FIELDS = {
    ("ole", "summary_title"): "summary_value",
    ("ole", "title"): "summary_value",
    ("ole", "summary_subject"): "summary_value",
    ("ole", "subject"): "summary_value",
    ("ole", "summary_author"): "summary_value",
    ("ole", "author"): "summary_value",
    ("ole", "summary_keywords"): "summary_value",
    ("ole", "keywords"): "summary_value",
    ("ole", "summary_comments"): "summary_value",
    ("ole", "comments"): "summary_value",
    ("ole", "summary_template"): "summary_value",
    ("ole", "template"): "summary_value",
    ("ole", "summary_last_saved_by"): "summary_value",
    ("ole", "last_saved_by"): "summary_value",
    ("ole", "summary_last_author"): "summary_value",
    ("ole", "last_author"): "summary_value",
    ("ole", "summary_last_modified_by"): "summary_value",
    ("ole", "summary_revision_number"): "summary_value",
    ("ole", "revision_number"): "summary_value",
    ("ole", "summary_create_time"): "summary_value",
    ("ole", "summary_create_time_utc"): "summary_value",
    ("ole", "create_time"): "summary_value",
    ("ole", "create_time_utc"): "summary_value",
    ("ole", "summary_creation_time"): "summary_value",
    ("ole", "creation_time"): "summary_value",
    ("ole", "summary_create_date"): "summary_value",
    ("ole", "summary_last_save_time"): "summary_value",
    ("ole", "summary_last_save_time_utc"): "summary_value",
    ("ole", "last_save_time"): "summary_value",
    ("ole", "summary_last_saved_time"): "summary_value",
    ("ole", "summary_last_printed"): "summary_value",
    ("ole", "summary_last_printed_time"): "summary_value",
    ("ole", "summary_page_count"): "summary_value",
    ("ole", "summary_word_count"): "summary_value",
    ("ole", "summary_char_count"): "summary_value",
    ("ole", "summary_character_count"): "summary_value",
    ("ole", "summary_application_name"): "summary_value",
    ("ole", "application_name"): "summary_value",
    ("ole", "summary_app_name"): "summary_value",
    ("ole", "app_name"): "summary_value",
    ("ole", "summary_creating_application"): "summary_value",
    ("ole", "creating_application"): "summary_value",
    ("ole", "summary_security"): "summary_value",
    ("ole", "stream_names"): "stream_names",
    ("ole", "cfb_stream_names"): "stream_names",
    ("ole", "directory_stream_names"): "stream_names",
    ("ole", "streams"): "stream_names",
}

_ENC = {1252: "cp1252", 65001: "utf-8", 1200: "utf-16le", 437: "cp437", 932: "cp932", 936: "gbk", 949: "cp949",
        950: "cp950", 1250: "cp1250", 1251: "cp1251", 1253: "cp1253", 1254: "cp1254", 10000: "mac_roman"}


def _filetime(v):
    if not v:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=v // 10)
    except OverflowError:
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def summary_props(b):
    """{PID: value} of the first section of \\x05SummaryInformation (FILETIMEs as ("ft", int)), or None."""
    try:
        st = cfb_streams(b, demangle=False)
    except Exception:  # noqa: BLE001  -- truncated / damaged CFB
        return None
    s = (st or {}).get("\x05SummaryInformation")
    if not s or len(s) < 48 or s[:2] != b"\xfe\xff":
        return None
    try:
        off, = struct.unpack_from("<I", s, 44)
        _size, n = struct.unpack_from("<II", s, off)
        raw = {}
        for i in range(min(n, 256)):
            pid, po = struct.unpack_from("<II", s, off + 8 + 8 * i)
            if off + po + 4 <= len(s):
                raw.setdefault(pid, off + po)
        cp = 1252
        if 1 in raw and struct.unpack_from("<H", s, raw[1])[0] == 2:
            cp = struct.unpack_from("<H", s, raw[1] + 4)[0]
        enc = _ENC.get(cp, "cp1252")
        out = {}
        for pid, p in raw.items():
            vt = struct.unpack_from("<I", s, p)[0] & 0xFFFF
            if vt == 2:
                out[pid] = struct.unpack_from("<h", s, p + 4)[0]
            elif vt in (3, 0x16):
                out[pid] = struct.unpack_from("<i", s, p + 4)[0]
            elif vt in (0x13, 0x17):
                out[pid] = struct.unpack_from("<I", s, p + 4)[0]
            elif vt == 0x1E:
                ln, = struct.unpack_from("<I", s, p + 4)
                if enc == "utf-16le":
                    out[pid] = s[p + 8:p + 8 + ln].decode(enc, "replace").split("\x00")[0]
                else:
                    out[pid] = s[p + 8:p + 8 + ln].split(b"\x00")[0].decode(enc, "replace")
            elif vt == 0x1F:
                ln, = struct.unpack_from("<I", s, p + 4)
                out[pid] = s[p + 8:p + 8 + 2 * ln].decode("utf-16le", "replace").split("\x00")[0]
            elif vt == 0x40:
                out[pid] = ("ft", struct.unpack_from("<Q", s, p + 4)[0])
        return out
    except (struct.error, ValueError, LookupError):
        return None


def summary_value(data, ctx):
    """ole.[summary_]<name>: the SummaryInformation property as stored (strings trimmed, ints base-10, FILETIME UTC)."""
    if data is None:
        return None
    field = (ctx or {}).get("field") or ""
    pid = _PID.get(field[len("summary_"):] if field.startswith("summary_") else field)
    if pid is None:
        return None
    if bytes(data[:8]) != MAGIC:
        return "none"
    v = (summary_props(data) or {}).get(pid)
    if isinstance(v, tuple):
        return _filetime(v[1])
    if v is None or (isinstance(v, str) and not v.strip()):
        return "none"
    return v.strip() if isinstance(v, str) else v


def _directory(b):
    """[(name, type, left, right, child)] of every CFB directory entry in stored order, or None."""
    if not b or len(b) < 512 or bytes(b[:8]) != MAGIC:
        return None
    ss = 1 << struct.unpack_from("<H", b, 0x1E)[0]
    if ss not in (512, 4096):
        return None
    nfat, dir0 = struct.unpack_from("<II", b, 0x2C)
    dif0, ndif = struct.unpack_from("<II", b, 0x44)
    sec = lambda n: b[512 + n * ss: 512 + (n + 1) * ss]  # noqa: E731
    difat = list(struct.unpack_from("<109I", b, 0x4C))
    d, seen = dif0, set()
    while ndif and d < 0xFFFFFFFA and d not in seen:
        seen.add(d)
        x = sec(d)
        if len(x) < ss:
            break
        e = struct.unpack("<%dI" % (ss // 4), x)
        difat += e[:-1]
        d = e[-1]
        ndif -= 1
    fat = []
    for f in difat[:nfat]:
        x = sec(f) if f < 0xFFFFFFFA else b""
        if len(x) == ss:
            fat += struct.unpack("<%dI" % (ss // 4), x)
    out, n, seen = [], dir0, set()
    while n < 0xFFFFFFFA and n < len(fat) and n not in seen:
        seen.add(n)
        out.append(sec(n))
        n = fat[n]
    dirb = b"".join(out)
    ents = []
    for i in range(0, len(dirb) - 127, 128):
        nl, typ = struct.unpack_from("<HB", dirb, i + 64)
        left, right, child = struct.unpack_from("<III", dirb, i + 68)
        name = dirb[i:i + min(max(nl - 2, 0), 62)].decode("utf-16le", "replace")
        ents.append((name, typ, left, right, child))
    return ents


def stream_names(data, ctx):
    """ole.stream_names: stream entries in stored directory order; nested streams as "Storage/Stream"."""
    if data is None:
        return None
    try:
        ents = _directory(data)
    except (struct.error, ValueError, OverflowError):
        return None
    if not ents:
        return "none"
    parent = {}

    def walk(i, par):
        stack = [i]
        while stack:
            j = stack.pop()
            if j >= len(ents) or j in parent:
                continue
            parent[j] = par
            _, _, left, right, child = ents[j]
            stack += [left, right]
            if ents[j][1] in (1, 5) and child < len(ents):
                pending.append((child, j))
    pending = [(ents[0][4], 0)] if ents[0][1] == 5 else []
    parent[0] = None
    while pending:
        walk(*pending.pop())

    def path(j):
        parts, seen = [], set()
        while j and j not in seen:
            seen.add(j)
            parts.append(ents[j][0])
            j = parent.get(j)
        return "/".join(reversed(parts))
    names = [path(j) for j, e in enumerate(ents) if e[1] == 2 and j in parent]
    return names or "none"
