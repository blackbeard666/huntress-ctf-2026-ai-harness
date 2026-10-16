"""VBA macro project fields (prebuilt, SPECULATIVE) -- fmt `vba`, with `ole.*` / `ooxml.*` aliases.

Containers: a CFB file (.doc "Macros/VBA", .xls "_VBA_PROJECT_CUR/VBA", a bare vbaProject.bin "VBA"), an OOXML zip
(word/ xl/ ppt/ vbaProject.bin), or a .ppt (VBA CFB zlib-packed in an ExOleObjStg record, type 0x1011, of the
"PowerPoint Document" stream). The first storage named "VBA" holding a "dir" stream (stored directory order) is THE
project; its parent storage holds the PROJECT text stream.
dir stream = MS-OVBA 2.3.4.2 records (u16 id, u32 size, data; PROJECTVERSION 0x0009 is 6 data bytes after its
Reserved=4 size), RLE-compressed per MS-OVBA 2.4.1 (decompressor ported below, stdlib).
  project_name = PROJECTNAME (0x0004), code_page = PROJECTCODEPAGE (0x0003, int), module_names = MODULENAME (0x0019;
  the MODULENAMEUNICODE 0x0047 twin wins when present) in dir order, module_stream_names = MODULESTREAMNAME (0x001A /
  0x0032), project_id_guid = PROJECT stream `ID="{...}"` verbatim.
  vba_stream_names = every stream inside the VBA storage, full CFB path ("VBA/dir", "Macros/VBA/dir"), stored
  directory-entry order (same law as ole.stream_names).
  autoexec_keywords = olevba's detect_autoexec semantics (the de-facto reader): its keyword table in table order, then
  its *_Click/_Change/... regexes, case-insensitive whole-word, the text as matched in the source, de-duplicated;
  source = each module stream decompressed from its MODULEOFFSET (0x0031), modules in dir order.
has_macros: bool -- a VBA project with >= 1 module present -> true; a CFB / OOXML package without one -> false.
Not CFB / not zip / damaged -> "none" (has_macros too); no project -> "none" for every other field; no auto-exec
keyword -> "none". Not covered: p-code / stomping detection (source vs. compiled p-code), Excel 4 XLM macros."""
import io
import re
import struct
import zipfile
import zlib

from ..cfb import MAGIC
from ..spell import Guid

FIELDS = {
    ("vba", "module_names"): "module_names",
    ("vba", "vba_module_names"): "module_names",
    ("vba", "modules"): "module_names",
    ("vba", "dir_module_names"): "module_names",
    ("vba", "module_count"): "module_count",
    ("vba", "modules_count"): "module_count",
    ("vba", "dir_module_count"): "module_count",
    ("vba", "module_stream_names"): "module_stream_names",
    ("vba", "project_name"): "project_name",
    ("vba", "vba_project_name"): "project_name",
    ("vba", "dir_project_name"): "project_name",
    ("vba", "has_macros"): "has_macros",
    ("vba", "has_vba"): "has_macros",
    ("vba", "has_vba_macros"): "has_macros",
    ("vba", "has_vba_project"): "has_macros",
    ("vba", "macros_present"): "has_macros",
    ("vba", "vba_present"): "has_macros",
    ("vba", "autoexec_keywords"): "autoexec_keywords",
    ("vba", "auto_exec_keywords"): "autoexec_keywords",
    ("vba", "autoexec_triggers"): "autoexec_keywords",
    ("vba", "autoexec_macros"): "autoexec_keywords",
    ("vba", "auto_exec_macros"): "autoexec_keywords",
    ("vba", "vba_stream_names"): "vba_stream_names",
    ("vba", "stream_names"): "vba_stream_names",
    ("vba", "code_page"): "code_page",
    ("vba", "codepage"): "code_page",
    ("vba", "project_code_page"): "code_page",
    ("vba", "dir_code_page"): "code_page",
    ("vba", "project_id_guid"): "project_id_guid",
    ("vba", "project_guid"): "project_id_guid",
    ("ole", "vba_module_names"): "module_names",
    ("ole", "module_names"): "module_names",
    ("ole", "vba_module_count"): "module_count",
    ("ole", "vba_module_stream_names"): "module_stream_names",
    ("ole", "vba_project_name"): "project_name",
    ("ole", "has_macros"): "has_macros",
    ("ole", "has_vba"): "has_macros",
    ("ole", "has_vba_macros"): "has_macros",
    ("ole", "vba_autoexec_keywords"): "autoexec_keywords",
    ("ole", "autoexec_keywords"): "autoexec_keywords",
    ("ole", "vba_stream_names"): "vba_stream_names",
    ("ole", "vba_code_page"): "code_page",
    ("ole", "vba_project_id_guid"): "project_id_guid",
    ("ooxml", "vba_module_names"): "module_names",
    ("ooxml", "module_names"): "module_names",
    ("ooxml", "vba_module_count"): "module_count",
    ("ooxml", "vba_project_name"): "project_name",
    ("ooxml", "has_macros"): "has_macros",
    ("ooxml", "has_vba"): "has_macros",
    ("ooxml", "has_vba_macros"): "has_macros",
    ("ooxml", "has_vba_project"): "has_macros",
    ("ooxml", "vba_autoexec_keywords"): "autoexec_keywords",
    ("ooxml", "autoexec_keywords"): "autoexec_keywords",
    ("ooxml", "vba_stream_names"): "vba_stream_names",
    ("ooxml", "vba_code_page"): "code_page",
}

_END = 0xFFFFFFFA


def _cfb(b):
    """CFB reader: ([(path, type, start, size)] in stored directory order, read(entry) -> bytes), or None."""
    if not b or len(b) < 512 or bytes(b[:8]) != MAGIC:
        return None
    ss = 1 << struct.unpack_from("<H", b, 0x1E)[0]
    mss = 1 << struct.unpack_from("<H", b, 0x20)[0]
    if ss not in (512, 4096):
        return None
    nfat, dir0 = struct.unpack_from("<II", b, 0x2C)
    cutoff, mf0, _nmf, dif0, ndif = struct.unpack_from("<IIIII", b, 0x38)
    sec = lambda n: b[512 + n * ss: 512 + (n + 1) * ss]  # noqa: E731
    difat = list(struct.unpack_from("<109I", b, 0x4C))
    d, seen = dif0, set()
    while ndif and d < _END and d not in seen:
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
        x = sec(f) if f < _END else b""
        if len(x) == ss:
            fat += struct.unpack("<%dI" % (ss // 4), x)

    def chain(start, tbl, get):
        out, n, seen = [], start, set()
        while n < _END and n < len(tbl) and n not in seen:
            seen.add(n)
            out.append(get(n))
            n = tbl[n]
        return b"".join(out)
    dirb = chain(dir0, fat, sec)
    ents = []
    for i in range(0, len(dirb) - 127, 128):
        nl, typ = struct.unpack_from("<HB", dirb, i + 64)
        left, right, child = struct.unpack_from("<III", dirb, i + 68)
        start, size = struct.unpack_from("<II", dirb, i + 116)
        name = dirb[i:i + min(max(nl - 2, 0), 62)].decode("utf-16le", "replace")
        ents.append([name, typ, left, right, child, start, size])
    if not ents or ents[0][1] != 5:
        return None
    parent, pending = {0: None}, [(ents[0][4], 0)]
    while pending:
        i, par = pending.pop()
        stack = [i]
        while stack:
            j = stack.pop()
            if j >= len(ents) or j in parent:
                continue
            parent[j] = par
            stack += [ents[j][2], ents[j][3]]
            if ents[j][1] in (1, 5) and ents[j][4] < len(ents):
                pending.append((ents[j][4], j))

    def path(j):
        parts, seen = [], set()
        while j and j not in seen:
            seen.add(j)
            parts.append(ents[j][0])
            j = parent.get(j)
        return "/".join(reversed(parts))
    listing = [(path(j), e[1], e[5], e[6]) for j, e in enumerate(ents) if j and j in parent]
    cache = {}

    def read(ent):
        _, typ, start, size = ent
        if typ != 2:
            return b""
        if size < cutoff:
            if "mini" not in cache:
                x = chain(mf0, fat, sec)
                cache["minifat"] = list(struct.unpack("<%dI" % (len(x) // 4), x[:len(x) // 4 * 4]))
                cache["mini"] = chain(ents[0][5], fat, sec)
            mini = cache["mini"]
            return chain(start, cache["minifat"], lambda n: mini[n * mss:(n + 1) * mss])[:size]
        return chain(start, fat, sec)[:size]
    return listing, read


def decompress(c):
    """MS-OVBA 2.4.1 CompressedContainer -> bytes (stops at the first malformed chunk)."""
    if not c or c[0] != 1:
        return b""
    out, pos = bytearray(), 1
    while pos + 2 <= len(c):
        hdr = c[pos] | c[pos + 1] << 8
        end = min(len(c), pos + 2 + (hdr & 0x0FFF) + 1)
        pos += 2
        start = len(out)
        if not hdr & 0x8000:            # raw chunk: 4096 literal bytes
            out += c[pos:pos + 4096]
            pos += 4096
            continue
        while pos < end:
            flags = c[pos]
            pos += 1
            for bit in range(8):
                if pos >= end:
                    break
                if not flags >> bit & 1:
                    out.append(c[pos])
                    pos += 1
                    continue
                if pos + 2 > end:
                    return bytes(out)
                tok = c[pos] | c[pos + 1] << 8
                pos += 2
                bc = max((len(out) - start - 1).bit_length(), 4)
                ln, off = (tok & (0xFFFF >> bc)) + 3, (tok >> (16 - bc)) + 1
                if off > len(out) - start or len(out) > 1 << 24:
                    return bytes(out)
                for _ in range(min(ln, 4096 - (len(out) - start))):   # a decompressed chunk is <= 4096 bytes
                    out.append(out[-off])
        pos = end
    return bytes(out)


def _codec(cp):
    try:
        "".encode("cp%d" % cp)
        return "cp%d" % cp
    except (LookupError, TypeError):
        return {65001: "utf-8", 10000: "mac_roman", 1200: "utf-16le"}.get(cp, "latin-1")


def _dir(d):
    """{code_page, project_name, modules: [{name, stream, offset}]} from a decompressed dir stream."""
    p = {"code_page": None, "project_name": None, "modules": []}
    enc, cur, i = "cp1252", None, 0
    while i + 6 <= len(d):
        rid, size = struct.unpack_from("<HI", d, i)
        if rid == 0x0009:               # PROJECTVERSION: Reserved(=4) + u32 major + u16 minor
            size = 6
        v = d[i + 6:i + 6 + size]
        i += 6 + size
        if rid == 0x0003 and len(v) >= 2:
            p["code_page"] = struct.unpack_from("<H", v)[0]
            enc = _codec(p["code_page"])
        elif rid == 0x0004:
            p["project_name"] = v.decode(enc, "replace")
        elif rid == 0x0019:
            cur = {"name": v.decode(enc, "replace"), "stream": None, "offset": 0}
            p["modules"].append(cur)
        elif cur is not None and rid == 0x0047 and v:
            cur["name"] = v.decode("utf-16le", "replace")
        elif cur is not None and rid == 0x001A:
            cur["stream"] = v.decode(enc, "replace")
        elif cur is not None and rid == 0x0032 and v:
            cur["stream"] = v.decode("utf-16le", "replace")
        elif cur is not None and rid == 0x0031 and len(v) >= 4:
            cur["offset"] = struct.unpack_from("<I", v)[0]
        elif rid == 0x002B:
            cur = None
        elif rid == 0x0010:
            break
    for m in p["modules"]:
        m["stream"] = m["stream"] or m["name"]
    return p


def _project_in_cfb(b, depth=0):
    """The first VBA project of a CFB: dict, False (a CFB without one), or None (not CFB)."""
    cf = _cfb(b)
    if cf is None:
        return None
    listing, read = cf
    paths = {e[0]: e for e in listing}
    for ent in listing:
        pth = ent[0]
        if ent[1] != 1 or pth.rsplit("/", 1)[-1].upper() != "VBA" or pth + "/dir" not in paths:
            continue
        p = _dir(decompress(read(paths[pth + "/dir"])))
        if not p["modules"] and p["project_name"] is None:
            continue
        p["vba_storage"] = pth
        p["streams"] = [e[0] for e in listing if e[1] == 2 and e[0].startswith(pth + "/")]
        p["read"] = lambda name, _p=pth: read(paths[_p + "/" + name]) if _p + "/" + name in paths else b""
        root = pth.rsplit("/", 1)[0] + "/" if "/" in pth else ""
        p["project_stream"] = read(paths[root + "PROJECT"]) if root + "PROJECT" in paths else b""
        return p
    ppt = paths.get("PowerPoint Document")
    if ppt is not None and depth == 0:
        s = read(ppt)
        for m in re.finditer(rb"\x11\x10", s):
            o = m.start() - 2
            if o < 0 or o + 8 > len(s):
                continue
            inst = struct.unpack_from("<H", s, o)[0] >> 4
            ln = struct.unpack_from("<I", s, o + 4)[0]
            body = s[o + 8:o + 8 + ln]
            try:
                # PowerPoint writes the zlib stream without its final block flush: decompressobj, not decompress()
                inner = zlib.decompressobj().decompress(body[4:], 1 << 26) if inst == 1 else body
            except zlib.error:
                continue
            got = _project_in_cfb(inner, 1)
            if got:
                return got
    return False


def project(data):
    """The VBA project of a CFB / OOXML zip / .ppt: dict, False (a container without macros), None (unrecognized)."""
    if not data:
        return None
    try:
        if bytes(data[:8]) == MAGIC:
            return _project_in_cfb(data)
        if bytes(data[:2]) == b"PK":
            z = zipfile.ZipFile(io.BytesIO(data))
            names = z.namelist()
            bins = [n for n in names if re.search(r"(?i)(^|/)vbaProject\.bin$", n)]
            for n in bins:
                got = _project_in_cfb(z.read(n))
                if got:
                    return got
            return False if bins or "[Content_Types].xml" in names else None
    except Exception:  # noqa: BLE001 -- damaged / truncated input never raises past the extractor
        return None
    return None


def _get(data, key):
    if data is None:
        return None
    p = project(data)
    if not p:
        return "none"
    try:
        return key(p)
    except Exception:  # noqa: BLE001
        return None


def module_names(data, ctx):
    """vba.module_names: MODULENAME records in dir-stream order (JSON list)."""
    return _get(data, lambda p: [m["name"] for m in p["modules"]] or "none")


def module_count(data, ctx):
    return _get(data, lambda p: len(p["modules"]))


def module_stream_names(data, ctx):
    return _get(data, lambda p: [m["stream"] for m in p["modules"]] or "none")


def project_name(data, ctx):
    return _get(data, lambda p: (p["project_name"] or "").strip() or "none")


def code_page(data, ctx):
    return _get(data, lambda p: p["code_page"] if p["code_page"] is not None else "none")


def vba_stream_names(data, ctx):
    """vba.vba_stream_names: streams inside the VBA storage, full CFB path, stored directory order."""
    return _get(data, lambda p: p["streams"] or "none")


def project_id_guid(data, ctx):
    def f(p):
        m = re.search(rb'(?im)^ID="(\{[0-9A-F-]{36}\})"', p["project_stream"])
        if not m:
            return "none"
        return Guid("text", m.group(1).decode())
    return _get(data, f)


def has_macros(data, ctx):
    """vba.has_macros: a VBA project with >= 1 module (bool); unrecognized container -> "none"."""
    if data is None:
        return None
    p = project(data)
    if p is None:
        return "none"
    return bool(p and p["modules"])


# olevba 0.60 AUTOEXEC_KEYWORDS / AUTOEXEC_KEYWORDS_REGEX, in its table order.
_AUTOEXEC = ("AutoExec", "AutoOpen", "DocumentOpen", "AutoExit", "AutoClose", "Document_Close", "DocumentBeforeClose",
             "DocumentChange", "AutoNew", "Document_New", "NewDocument", "Document_Open", "Document_BeforeClose",
             "Auto_Open", "Workbook_Open", "Workbook_Activate", "Auto_Ope", "Auto_Close", "Workbook_Close",
             "Workbook_BeforeClose", "Worksheet_Calculate")
_AUTOEXEC_RX = ("Painted", "Painting", "GotFocus", "LostFocus", "MouseHover", "Click", "Change", "Resize",
                "BeforeNavigate2", "BeforeScriptExecute", "DocumentComplete", "DownloadBegin", "DownloadComplete",
                "FileDownload", "NavigateComplete2", "NavigateError", "ProgressChange", "PropertyChange",
                "SetSecureLockIcon", "StatusTextChange", "TitleChange", "MouseMove", "MouseEnter", "MouseLeave",
                "Layout", "OnConnecting", "FollowHyperlink", "ContentControlOnEnter")


def source_code(p):
    """Decompressed VBA source of every module, dir order, as one text."""
    enc = _codec(p["code_page"] or 1252)
    parts = []
    for m in p["modules"]:
        raw = p["read"](m["stream"])
        parts.append(decompress(raw[m["offset"]:]).decode(enc, "replace"))
    return "\n".join(parts)


def autoexec_keywords(data, ctx):
    """vba.autoexec_keywords: olevba detect_autoexec hits (matched text, table order, de-duplicated)."""
    def f(p):
        code, out = source_code(p), []
        for kw in _AUTOEXEC:
            m = re.search(r"(?i)\b" + re.escape(kw) + r"\b", code)
            if m and m.group() not in out:
                out.append(m.group())
        for kw in _AUTOEXEC_RX:
            m = re.search(r"(?i)\b\w+_" + kw + r"\b", code)
            if m and m.group() not in out:
                out.append(m.group())
        return out or "none"
    return _get(data, f)
