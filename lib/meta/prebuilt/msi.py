"""MSI SummaryInformation fields (prebuilt, SPECULATIVE) -- siblings of the GM-verified D13 msi.product_code_guid.

The CFB stream "\\x05SummaryInformation" is an OLE property set (MS-OLEPS): header 0xFFFE byte order, version,
system id, CLSID, section count; then (FMTID, offset) per section; a section = size, property count, (PID, offset)
pairs (offsets relative to the section), each value = u32 VARTYPE + payload. MSI usage of the PIDs (MS docs
"Summary Information Stream Property Set"): 2 Title, 3 Subject, 4 Author, 5 Keywords, 6 Comments, 7 Template
("Intel;1033" = platform;languages), 8 LastSavedBy, 9 RevisionNumber (= the PackageCode GUID, stored as TEXT with
{UPPER} braces -> kept verbatim like ProductCode), 14 PageCount (minimum installer version, e.g. 200),
15 WordCount (source image flags), 18 CreatingApplication, 19 Security. Strings are VT_LPSTR in the codepage of PID 1.
Not a CFB / no SummaryInformation / PID absent -> "none"."""
import struct

from ..cfb import cfb_streams
from ..spell import Guid

FIELDS = {
    ("msi", "package_code_guid"): "package_code",
    ("msi", "revision_number_guid"): "package_code",
    ("msi", "summary_revision_number_guid"): "package_code",
    ("msi", "summary_package_code_guid"): "package_code",
    ("msi", "summary_title"): "summary_value",
    ("msi", "summary_subject"): "summary_value",
    ("msi", "summary_author"): "summary_value",
    ("msi", "summary_keywords"): "summary_value",
    ("msi", "summary_comments"): "summary_value",
    ("msi", "summary_template"): "summary_value",
    ("msi", "summary_last_saved_by"): "summary_value",
    ("msi", "summary_page_count"): "summary_value",
    ("msi", "summary_word_count"): "summary_value",
    ("msi", "summary_creating_application"): "summary_value",
    ("msi", "summary_security"): "summary_value",
}

_PID = {"title": 2, "subject": 3, "author": 4, "keywords": 5, "comments": 6, "template": 7, "last_saved_by": 8,
        "revision_number": 9, "page_count": 14, "word_count": 15, "creating_application": 18, "security": 19}
_ENC = {1252: "cp1252", 65001: "utf-8", 1200: "utf-16le", 437: "cp437", 932: "cp932", 936: "gbk", 949: "cp949",
        950: "cp950", 1250: "cp1250", 1251: "cp1251", 1253: "cp1253", 1254: "cp1254"}


def summary_props(b):
    """{PID: python value} of an MSI/OLE file's SummaryInformation (first section), or None."""
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
        ents = [struct.unpack_from("<II", s, off + 8 + 8 * i) for i in range(min(n, 256))]
        raw = {}
        for pid, po in ents:
            p = off + po
            if p + 4 <= len(s):
                raw[pid] = p
        cp = 1252
        if 1 in raw and struct.unpack_from("<I", s, raw[1])[0] == 2:
            cp = struct.unpack_from("<H", s, raw[1] + 4)[0]
        enc = _ENC.get(cp, "cp1252")
        out = {}
        for pid, p in raw.items():
            vt, = struct.unpack_from("<I", s, p)
            vt &= 0xFFFF
            if vt == 2:
                out[pid] = struct.unpack_from("<h", s, p + 4)[0]
            elif vt in (3, 0x13):
                out[pid] = struct.unpack_from("<i" if vt == 3 else "<I", s, p + 4)[0]
            elif vt == 0x1E:
                ln, = struct.unpack_from("<I", s, p + 4)
                out[pid] = s[p + 8:p + 8 + ln].decode(enc, "replace").split("\x00")[0]
            elif vt == 0x1F:
                ln, = struct.unpack_from("<I", s, p + 4)
                out[pid] = s[p + 8:p + 8 + 2 * ln].decode("utf-16le", "replace").split("\x00")[0]
            elif vt == 0x40:
                out[pid] = struct.unpack_from("<Q", s, p + 4)[0]   # FILETIME (not exposed as a field yet)
        return out
    except (struct.error, ValueError):
        return None


def _get(data, pid):
    if data is None:
        return None
    v = (summary_props(data) or {}).get(pid)
    if v is None or (isinstance(v, str) and not v.strip()):
        return "none"
    return v.strip() if isinstance(v, str) else v


def package_code(data, ctx):
    """msi.package_code_guid: SummaryInformation PID_REVNUMBER (9) VERBATIM (MSI stores '{UPPER-GUID}' text)."""
    v = _get(data, 9)
    if not isinstance(v, str) or v == "none":
        return v
    return Guid("text", v)


def summary_value(data, ctx):
    """msi.summary_<name>: the SummaryInformation property as stored (strings trimmed, counts base-10 ints)."""
    field = (ctx or {}).get("field") or ""
    pid = _PID.get(field[len("summary_"):] if field.startswith("summary_") else field)
    if pid is None:
        return None
    return _get(data, pid)
