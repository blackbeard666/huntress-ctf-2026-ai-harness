"""RTF fields: embedded OLE objects (\\objdata), the attached template and the {\\info} group (prebuilt, SPECULATIVE).

RTF 1.9.1: a document starts with "{\\rtf" (Word accepts "{\\rt"). An embedded object is {\\object ... {\\*\\objclass
X}{\\*\\objdata <hex>}}; \\objdata holds an OLE1 ObjectHeader ([MS-OLEDS] 2.2.4) hex-encoded: OLEVersion u32le
(0x00000501), FormatID u32le (1 linked / 2 embedded), ClassName = LengthPrefixedAnsiString (u32le length INCLUDING
the NUL, then the bytes), TopicName, ItemName, then (embedded) NativeDataSize u32le + data. Like oletools rtfobj, the
hex is read with whitespace / control words / non-hex bytes ignored (malware pads and splits it).
object_count = number of \\objdata destinations (rtfobj's object count, OLE1-parsable or not).
object_class_names = the OLE1 ClassName (NUL stripped) of each \\objdata in document order (rtfobj "OLE Object:
class name"); an \\objdata that is not OLE1 falls back to its \\object group's {\\*\\objclass}; no objects -> "none".
objclass_names = the {\\*\\objclass} texts (the RTF-level label, may disagree with the OLE1 header -- a decoy).
template_target = the {\\*\\template ...} destination text (Word's attached template; remote-template injection
points it at an http(s)/UNC .dotm), RTF-unescaped. info_<x> = the {\\info{\\<x> ...}} text, RTF-unescaped
(\\'hh in \\ansicpg, \\uN with \\ucN skip, \\{ \\} \\\\ literals), surrounding whitespace trimmed (exiftool Author).
Not RTF (decoy / renamed impostor) -> "none"; a field the document lacks -> "none"."""
import re

FIELDS = {
    ("rtf", "object_class_names"): "rtf_value",
    ("rtf", "objdata_class_names"): "rtf_value",
    ("rtf", "ole_object_class_names"): "rtf_value",
    ("rtf", "ole1_class_names"): "rtf_value",
    ("rtf", "ole1_object_class_names"): "rtf_value",
    ("rtf", "embedded_object_class_names"): "rtf_value",
    ("rtf", "object_classes"): "rtf_value",
    ("rtf", "class_names"): "rtf_value",
    ("rtf", "first_object_class_name"): "rtf_value",
    ("rtf", "object_class_name"): "rtf_value",
    ("rtf", "objclass_names"): "rtf_value",
    ("rtf", "object_count"): "rtf_value",
    ("rtf", "objdata_count"): "rtf_value",
    ("rtf", "ole_object_count"): "rtf_value",
    ("rtf", "embedded_object_count"): "rtf_value",
    ("rtf", "object_data_count"): "rtf_value",
    ("rtf", "objects_count"): "rtf_value",
    ("rtf", "template_target"): "rtf_value",
    ("rtf", "template"): "rtf_value",
    ("rtf", "template_path"): "rtf_value",
    ("rtf", "template_url"): "rtf_value",
    ("rtf", "attached_template"): "rtf_value",
    ("rtf", "info_author"): "rtf_value",
    ("rtf", "author"): "rtf_value",
    ("rtf", "info_operator"): "rtf_value",
    ("rtf", "operator"): "rtf_value",
    ("rtf", "info_title"): "rtf_value",
    ("rtf", "title"): "rtf_value",
    ("rtf", "info_subject"): "rtf_value",
    ("rtf", "subject"): "rtf_value",
    ("rtf", "info_keywords"): "rtf_value",
    ("rtf", "keywords"): "rtf_value",
    ("rtf", "info_company"): "rtf_value",
    ("rtf", "company"): "rtf_value",
    ("rtf", "info_manager"): "rtf_value",
    ("rtf", "info_category"): "rtf_value",
    ("rtf", "info_doccomm"): "rtf_value",
    ("rtf", "info_comment"): "rtf_value",
    ("rtf", "info_comments"): "rtf_value",
    ("rtf", "comments"): "rtf_value",
}

_CW = re.compile(rb"\\([a-zA-Z]{1,32})(-?\d{1,10})? ?")
_NONHEX = re.compile(rb"[^0-9A-Fa-f]+")
_TOK = re.compile(rb"\\.|[{}]", re.S)
_CP = re.compile(rb"\\ansicpg(\d+)")


def _group_end(b, i):
    """Index just past the group whose '{' is at b[i] (or len(b) when unterminated)."""
    depth = 0
    for m in _TOK.finditer(b, i):
        c = b[m.start()]
        if c == 0x7B:
            depth += 1
        elif c == 0x7D:
            depth -= 1
            if depth == 0:
                return m.end()
    return len(b)


def _dest(b, word, start=0, end=None):
    """[(content_start, group_end)] of every {\\word ...} / {\\*\\word ...} group in b[start:end]."""
    rx = re.compile(rb"\{\s*(?:\\\*\s*)?\\" + word + rb"(?![a-zA-Z])(-?\d+)? ?")
    out = []
    for m in rx.finditer(b, start, len(b) if end is None else end):
        out.append((m.end(), _group_end(b, m.start())))
    return out


def _text(s, enc):
    """Plain text of an RTF fragment."""
    out, raw = [], bytearray()
    uc, skip, i, n = 1, 0, 0, len(s)

    def flush():
        if raw:
            out.append(raw.decode(enc, "replace"))
            raw.clear()

    while i < n:
        c = s[i]
        if c == 0x5C and i + 1 < n:
            d = s[i + 1]
            if d == 0x27 and i + 3 < n + 1:
                hx = s[i + 2:i + 4]
                i += 4
                if skip:
                    skip -= 1
                    continue
                try:
                    raw.append(int(hx, 16))
                except ValueError:
                    pass
                continue
            if d in b"\\{}":
                if skip:
                    skip -= 1
                else:
                    raw.append(d)
                i += 2
                continue
            m = _CW.match(s, i)
            if m:
                w, arg = m.group(1), m.group(2)
                i = m.end()
                if w == b"u" and arg is not None:
                    flush()
                    out.append(chr(int(arg) & 0xFFFF))
                    skip = uc
                elif w == b"uc" and arg is not None:
                    uc = int(arg)
                elif w in (b"par", b"line"):
                    raw.extend(b"\n")
                elif w == b"tab":
                    raw.extend(b"\t")
                continue
            if d == 0x7E:
                raw.extend("\xa0".encode(enc, "replace"))
            i += 2
            continue
        i += 1
        if c in (0x7B, 0x7D, 0x0D, 0x0A):
            continue
        if skip:
            skip -= 1
            continue
        raw.append(c)
    flush()
    return "".join(out)


def _hexbytes(s):
    """\\objdata payload prefix (the OLE1 header needs < 9 KiB): control words dropped, then every hex digit paired up
    (rtfobj-style)."""
    hx = _NONHEX.sub(b"", _CW.sub(b"", s[:0x30000]))
    return bytes.fromhex(hx[:len(hx) & ~1].decode())


def _lpstr(b, off):
    if off + 4 > len(b):
        return None, off
    ln = int.from_bytes(b[off:off + 4], "little")
    if ln > 0x1000 or off + 4 + ln > len(b):
        return None, off
    return b[off + 4:off + 4 + ln].split(b"\0", 1)[0].decode("latin-1"), off + 4 + ln


def ole1_class(b):
    """OLE1 ObjectHeader ClassName, or None when b is not an OLE1 object."""
    if len(b) < 12:
        return None
    fmt_id = int.from_bytes(b[4:8], "little")
    if fmt_id not in (1, 2):
        return None
    name, _ = _lpstr(b, 8)
    return name if name else None


def parse(data):
    b = bytes(data or b"")
    if not b.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"{\\rt"):
        return None
    m = _CP.search(b, 0, 4096)
    enc = "cp%d" % int(m.group(1)) if m else "cp1252"
    try:
        "".encode(enc)
    except LookupError:
        enc = "cp1252"
    r = {"objects": [], "objclass": []}
    objs = _dest(b, b"object")
    for s, e in _dest(b, b"objclass"):
        r["objclass"].append(_text(b[s:e - 1], enc).strip())
    for s, e in _dest(b, b"objdata"):
        cls = ole1_class(_hexbytes(b[s:e - 1]))
        if cls is None:
            for os_, oe in objs:
                if os_ <= s < oe:
                    oc = _dest(b, b"objclass", os_, oe)
                    cls = _text(b[oc[0][0]:oc[0][1] - 1], enc).strip() if oc else None
                    break
        r["objects"].append(cls)
    for name in (b"template", b"author", b"operator", b"title", b"subject", b"keywords", b"company", b"manager",
                 b"category", b"doccomm"):
        g = _dest(b, name)
        if g:
            s, e = g[0]
            r[name.decode()] = _text(b[s:e - 1], enc).strip()
    return r


_ALIAS = {"author": "author", "operator": "operator", "title": "title", "subject": "subject", "keywords": "keywords",
          "company": "company", "manager": "manager", "category": "category", "doccomm": "doccomm",
          "comment": "doccomm", "comments": "doccomm"}


def rtf_value(data, ctx):
    if data is None:
        return None
    try:
        r = parse(data)
    except Exception:
        return None
    if r is None:
        return "none"
    f = ctx.get("field") or ""
    names = [c for c in r["objects"] if c]
    if f.endswith("_count"):
        return len(r["objects"])
    if f == "objclass_names":
        return r["objclass"] or "none"
    if f in ("first_object_class_name", "object_class_name"):
        return names[0] if names else "none"
    if f.endswith("class_names") or f == "object_classes":
        return names or "none"
    if f.startswith("template") or f == "attached_template":
        return r.get("template") or "none"
    key = _ALIAS.get(f[5:] if f.startswith("info_") else f)
    if key:
        return r.get(key) or "none"
    return None
