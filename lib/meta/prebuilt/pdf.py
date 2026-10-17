"""PDF trailer / document-structure fields (prebuilt, SPECULATIVE -- never GM-asked yet; pdf.header_version is the
GM-verified D6 builtin in lib/meta/pdf.py and is NOT re-registered here).

Layout (ISO 32000-1): objects `N G obj ... endobj` (an incremental update APPENDS redefinitions, so the LAST
definition of a number wins; PDF 1.5 /ObjStm object streams hold compressed objects); every revision ends with its
own trailer (or /Type /XRef stream dict) + `startxref` + `%%EOF`. Trailer /Root -> catalog (/Version name overrides
the header, /Pages -> page tree root /Count = leaf pages), /Info -> document information dict, /Encrypt -> the
security handler (its presence = encrypted).
info_<key> = the /Info entry of the LAST trailer (pdfinfo / exiftool semantics), text strings decoded per 7.9.2.2
(UTF-16BE with BOM, UTF-8 with BOM, else PDFDocEncoding ~ latin-1); "none" when the dict or key is absent. An
encrypted file's strings are decrypted with the empty user password via pypdf; when that fails -> None (no guess).
info_creation_date / info_mod_date = the stored "D:YYYYMMDDHHmmSS+HH'mm'" converted to ISO-8601 UTC
"YYYY-MM-DDTHH:MM:SSZ" (same spelling as the OLE/OOXML timestamps; no offset = taken as UTC); `*_raw` keeps the
stored string verbatim. page_count = catalog /Pages /Count (pdfinfo "Pages"), falling back to counting /Type /Page
objects. catalog_version = the catalog /Version name ("1.7"), "none" when not overridden. eof_count = occurrences of
the `%%EOF` marker (1 + incremental updates). encrypted = /Encrypt in any trailer / xref-stream dict.
Not a PDF (no leading %PDF- magic: renamed impostor / decoy) -> "none" for every field."""
import re
import zlib
from datetime import datetime, timedelta, timezone

FIELDS = {
    ("pdf", "info_title"): "pdf_value",
    ("pdf", "title"): "pdf_value",
    ("pdf", "info_author"): "pdf_value",
    ("pdf", "author"): "pdf_value",
    ("pdf", "info_subject"): "pdf_value",
    ("pdf", "subject"): "pdf_value",
    ("pdf", "info_keywords"): "pdf_value",
    ("pdf", "keywords"): "pdf_value",
    ("pdf", "info_creator"): "pdf_value",
    ("pdf", "creator"): "pdf_value",
    ("pdf", "creator_tool"): "pdf_value",
    ("pdf", "info_producer"): "pdf_value",
    ("pdf", "producer"): "pdf_value",
    ("pdf", "info_creation_date"): "pdf_value",
    ("pdf", "creation_date"): "pdf_value",
    ("pdf", "create_date"): "pdf_value",
    ("pdf", "info_creation_date_raw"): "pdf_value",
    ("pdf", "info_mod_date"): "pdf_value",
    ("pdf", "info_modification_date"): "pdf_value",
    ("pdf", "mod_date"): "pdf_value",
    ("pdf", "modification_date"): "pdf_value",
    ("pdf", "modify_date"): "pdf_value",
    ("pdf", "info_mod_date_raw"): "pdf_value",
    ("pdf", "page_count"): "pdf_value",
    ("pdf", "pages"): "pdf_value",
    ("pdf", "pages_count"): "pdf_value",
    ("pdf", "number_of_pages"): "pdf_value",
    ("pdf", "num_pages"): "pdf_value",
    ("pdf", "page_tree_count"): "pdf_value",
    ("pdf", "pages_count_value"): "pdf_value",
    ("pdf", "catalog_version"): "pdf_value",
    ("pdf", "root_version"): "pdf_value",
    ("pdf", "catalog_version_override"): "pdf_value",
    ("pdf", "version_override"): "pdf_value",
    ("pdf", "eof_count"): "pdf_value",
    ("pdf", "eof_marker_count"): "pdf_value",
    ("pdf", "revision_count"): "pdf_value",
    ("pdf", "incremental_update_count"): "pdf_value",
    ("pdf", "incremental_updates"): "pdf_value",
    ("pdf", "encrypted"): "pdf_value",
    ("pdf", "is_encrypted"): "pdf_value",
    ("pdf", "encrypt_present"): "pdf_value",
    ("pdf", "has_encrypt"): "pdf_value",
    ("pdf", "has_encryption"): "pdf_value",
    ("pdf", "encryption_present"): "pdf_value",
    ("pdf", "trailer_encrypt_present"): "pdf_value",
}

_HEADER = re.compile(rb"%PDF-\d+\.\d+")
_LEAD = b"\xef\xbb\xbf\x00\t\n\x0c\r "
_OBJ = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj", re.S)
_REF = rb"\s+(\d+)\s+\d+\s+R"
_INFO_KEYS = {"title": "Title", "author": "Author", "subject": "Subject", "keywords": "Keywords",
              "creator": "Creator", "creator_tool": "Creator", "producer": "Producer",
              "creation_date": "CreationDate", "create_date": "CreationDate",
              "mod_date": "ModDate", "modification_date": "ModDate", "modify_date": "ModDate"}
_ALIAS = {"pages": "page_count", "pages_count": "page_count", "number_of_pages": "page_count",
          "num_pages": "page_count", "page_tree_count": "page_count", "pages_count_value": "page_count",
          "root_version": "catalog_version", "catalog_version_override": "catalog_version",
          "version_override": "catalog_version",
          "eof_marker_count": "eof_count", "revision_count": "eof_count",
          "is_encrypted": "encrypted", "encrypt_present": "encrypted", "has_encrypt": "encrypted",
          "has_encryption": "encrypted", "encryption_present": "encrypted", "trailer_encrypt_present": "encrypted"}


def _objects(data):
    """{obj_num: body}; later (incremental-update) definitions override earlier ones; /ObjStm members added."""
    objs = {}
    for m in _OBJ.finditer(data):
        objs[int(m.group(1))] = m.group(3)
    for body in list(objs.values()):
        if b"/ObjStm" not in body[:600]:
            continue
        sm = re.search(rb"stream\r?\n", body)
        n, first = re.search(rb"/N\s+(\d+)", body), re.search(rb"/First\s+(\d+)", body)
        if not (sm and n and first):
            continue
        raw = body[sm.end():]
        raw = raw[:raw.rfind(b"endstream")] if b"endstream" in raw else raw
        if b"/FlateDecode" in body[:sm.start()]:
            try:
                raw = zlib.decompressobj().decompress(raw)
            except zlib.error:
                continue
        try:
            base = int(first.group(1))
            nums = list(map(int, raw[:base].split()))
        except ValueError:
            continue
        pairs = list(zip(nums[0::2], nums[1::2]))[:int(n.group(1))]
        for i, (num, off) in enumerate(pairs):
            end = base + pairs[i + 1][1] if i + 1 < len(pairs) else len(raw)
            objs.setdefault(num, raw[base + off:end])
    return objs


def _last_ref(data, key):
    refs = re.findall(rb"/" + key + _REF, data)
    return int(refs[-1]) if refs else None


def _literal(b, i):
    """Decode a literal string starting after '(' at i -> bytes."""
    out, depth, n = bytearray(), 1, len(b)
    esc = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12}
    while i < n:
        c = b[i]
        if c == 0x5C and i + 1 < n:
            d = b[i + 1]
            if d in esc:
                out.append(esc[d])
                i += 2
            elif 0x30 <= d <= 0x37:
                j = i + 1
                while j < n and j < i + 4 and 0x30 <= b[j] <= 0x37:
                    j += 1
                out.append(int(b[i + 1:j], 8) & 0xFF)
                i = j
            elif d in b"\r\n":
                i += 2 + (d == 13 and i + 2 < n and b[i + 2] == 10)
            else:
                out.append(d)
                i += 2
            continue
        if c == 0x28:
            depth += 1
        elif c == 0x29:
            depth -= 1
            if depth == 0:
                break
        out.append(c)
        i += 1
    return bytes(out)


def _text(raw):
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", "replace")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", "replace")
    return raw.decode("latin-1")


def _dict_string(body, key):
    """Raw bytes of /<key> (literal or hex string) in a dict body, or None."""
    m = re.search(rb"/" + key.encode() + rb"(?![A-Za-z0-9])\s*([(<])", body or b"")
    if not m:
        return None
    if m.group(1) == b"(":
        return _literal(body, m.end())
    end = body.find(b">", m.end())
    hx = re.sub(rb"[^0-9A-Fa-f]", b"", body[m.end():end if end >= 0 else len(body)])
    return bytes.fromhex((hx + b"0" * (len(hx) % 2)).decode())


def _iso(s):
    """PDF date "D:YYYYMMDDHHmmSSOHH'mm'" -> ISO-8601 UTC, or None."""
    m = re.match(r"\s*(?:D:)?(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?\s*([Zz+-])?\s*(\d{2})?'?(\d{2})?", s)
    if not m:
        return None
    y, mo, d, h, mi, se = (int(m.group(k) or dflt) for k, dflt in zip(range(1, 7), (0, 1, 1, 0, 0, 0)))
    try:
        t = datetime(y, mo, d, h, mi, se, tzinfo=timezone.utc)
    except ValueError:
        return None
    if m.group(7) in ("+", "-"):
        off = timedelta(hours=int(m.group(8) or 0), minutes=int(m.group(9) or 0))
        t = t - off if m.group(7) == "+" else t + off
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _pypdf_info(data, key):
    """An encrypted file's /Info entry via pypdf (empty user password); None when it cannot be decrypted."""
    try:
        import io
        import pypdf
        r = pypdf.PdfReader(io.BytesIO(data), strict=False)
        if r.is_encrypted and not r.decrypt(""):
            return None
        info = r.trailer.get("/Info")
        info = info.get_object() if info is not None else None
        if info is None:
            return "none"
        v = info.get("/" + key)
        return "none" if v is None else str(v)
    except Exception:  # noqa: BLE001
        return None


def _value(data, field):
    if not _HEADER.match(data.lstrip(_LEAD)[:16]):
        return "none"
    field = _ALIAS.get(field, field)
    if field == "eof_count":
        return data.count(b"%%EOF")
    if field in ("incremental_update_count", "incremental_updates"):
        return max(data.count(b"%%EOF") - 1, 0)
    if field == "encrypted":
        return bool(re.search(rb"/Encrypt" + _REF, data) or re.search(rb"trailer\s*<<[^>]*/Encrypt\s*<<", data))
    objs = _objects(data)
    if field in ("catalog_version", "page_count"):
        root = _last_ref(data, b"Root")
        cat = objs.get(root) if root is not None else None
        if cat is None:
            cat = next((b for b in objs.values() if re.search(rb"/Type\s*/Catalog\b", b[:2000])), None)
        if field == "catalog_version":
            m = re.search(rb"/Version\s*/([0-9A-Za-z.#]+)", cat or b"")
            if not m:
                return "none"
            return re.sub(rb"#([0-9A-Fa-f]{2})", lambda x: bytes([int(x.group(1), 16)]), m.group(1)).decode("latin-1")
        m = re.search(rb"/Pages" + _REF, cat or b"")
        pages = objs.get(int(m.group(1))) if m else None
        c = re.search(rb"/Count\s+(\d+)", pages or b"")
        if c:
            return int(c.group(1))
        return len(re.findall(rb"/Type\s*/Page(?![A-Za-z])", b"\n".join(objs.values())))
    raw_wanted = field.endswith("_raw")
    base = field[:-4] if raw_wanted else field
    base = base[5:] if base.startswith("info_") else base
    key = _INFO_KEYS.get(base)
    if key is None:
        return None
    if re.search(rb"/Encrypt" + _REF, data):
        v = _pypdf_info(data, key)
        if v is None or v == "none" or key not in ("CreationDate", "ModDate") or raw_wanted:
            return v.strip() if isinstance(v, str) and v != "none" else v
        return _iso(v) or v.strip()
    ref = _last_ref(data, b"Info")
    info = objs.get(ref) if ref is not None else None
    if info is None:
        m = re.search(rb"trailer\s*<<.*?/Info\s*(<<.*?>>)", data, re.S)
        info = m.group(1) if m else None
    raw = _dict_string(info, key)
    if raw is None:
        return "none"
    s = _text(raw).strip()
    if key in ("CreationDate", "ModDate") and not raw_wanted:
        return _iso(s) or s
    return s


def pdf_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), (ctx.get("field") or "").lower())
    except Exception:  # noqa: BLE001
        return None
