"""MIME tree + attachment fields for `email` / `mime` / `mail` (prebuilt, SPECULATIVE -- never GM-asked yet).
`eml.*` reaches these through lib.meta._FMT_ALIASES. attachment_count / attachment_names live in eml.py / email.py
(not re-registered here); this module uses the SAME attachment rule so its lists line up index-for-index with them.

Parse: stdlib email.message_from_bytes(policy.default) after the eml.py rejects (zip/pdf/MZ magic, NUL in the first
512 bytes, mbox "From " line stripped). Not an e-mail (no From/Received/Message-ID/Date/Return-Path/MIME-Version/
Content-Type header) -> "none".
mime_part_count = len(list(msg.walk())) (root + every container + every leaf); mime_leaf_part_count = non-multipart.
content_type = msg.get_content_type() of the TOP-level message (lowercase type/subtype, no params; RFC 2045 default
text/plain). mime_boundary = the top-level boundary param verbatim (not multipart -> "none").
Attachments = non-multipart parts with a filename (Content-Disposition filename, else Content-Type name; RFC 2231
continuations/charsets and RFC 2047 encoded-words decoded by policy.default), MIME walk order.
attachment_sizes_bytes / *_sha256s / *_md5s / *_sha1s / magic prefix = of get_payload(decode=True) (the DECODED
payload; CTE base64/quoted-printable undone). Plural names -> list (compact JSON); singular names
(attachment_sha256, attachment_size_bytes, attachment_name, ...) -> the FIRST attachment's value.
attachment_magic_prefix_hex_N = lowercase hex of the first N decoded bytes, no 0x (the GM-verified D2
file.magic_prefix_hex_* spelling), always a list (one entry per attachment); attachment_magic_hex = the first
attachment's 16 bytes.
attachment_declared_vs_magic_mismatch = true when ANY attachment's sniffed magic family (pdf/zip/pe/ole/png/jpeg/...)
disagrees with its filename extension or its specific (non-octet-stream) declared Content-Type; an e-mail
with no attachments -> false.
content_transfer_encodings = Content-Transfer-Encoding of every LEAF part in walk order, lowercased, absent ->
"7bit" (RFC 2045 6.1 default). body_text_sha256 = sha256 of the first text/plain non-attachment part's decoded
payload bytes (msg.get_body(("plain",)) -- bytes as stored after CTE decoding, line endings untouched)."""
import hashlib
import re

FIELDS = {
    ("email", "mime_part_count"): "mime_value",
    ("email", "part_count"): "mime_value",
    ("email", "mime_parts_count"): "mime_value",
    ("email", "total_part_count"): "mime_value",
    ("email", "mime_leaf_part_count"): "mime_value",
    ("email", "leaf_part_count"): "mime_value",
    ("email", "non_multipart_part_count"): "mime_value",
    ("email", "mime_part_content_types"): "mime_value",
    ("email", "part_content_types"): "mime_value",
    ("email", "mime_content_types"): "mime_value",
    ("email", "content_type"): "mime_value",
    ("email", "top_level_content_type"): "mime_value",
    ("email", "root_content_type"): "mime_value",
    ("email", "mime_content_type"): "mime_value",
    ("email", "top_content_type"): "mime_value",
    ("email", "message_content_type"): "mime_value",
    ("email", "mime_boundary"): "mime_value",
    ("email", "boundary"): "mime_value",
    ("email", "top_level_boundary"): "mime_value",
    ("email", "multipart_boundary"): "mime_value",
    ("email", "root_boundary"): "mime_value",
    ("email", "is_multipart"): "mime_value",
    ("email", "mime_version"): "mime_value",
    ("email", "attachment_content_types"): "mime_value",
    ("email", "attachment_mime_types"): "mime_value",
    ("email", "attachment_types"): "mime_value",
    ("email", "attachment_content_type"): "mime_value",
    ("email", "attachment_mime_type"): "mime_value",
    ("email", "attachment_sizes_bytes"): "mime_value",
    ("email", "attachment_sizes"): "mime_value",
    ("email", "attachment_size_bytes"): "mime_value",
    ("email", "attachment_size"): "mime_value",
    ("email", "attachment_decoded_sizes_bytes"): "mime_value",
    ("email", "attachment_total_size_bytes"): "mime_value",
    ("email", "attachment_sha256s"): "mime_value",
    ("email", "attachment_sha256"): "mime_value",
    ("email", "attachment_sha256_hashes"): "mime_value",
    ("email", "attachment_md5s"): "mime_value",
    ("email", "attachment_md5"): "mime_value",
    ("email", "attachment_md5_hashes"): "mime_value",
    ("email", "attachment_sha1s"): "mime_value",
    ("email", "attachment_sha1"): "mime_value",
    ("email", "attachment_sha1_hashes"): "mime_value",
    ("email", "attachment_name"): "mime_value",
    ("email", "attachment_filename"): "mime_value",
    ("email", "first_attachment_name"): "mime_value",
    ("email", "first_attachment_sha256"): "mime_value",
    ("email", "first_attachment_size_bytes"): "mime_value",
    ("email", "attachment_extensions"): "mime_value",
    ("email", "attachment_file_extensions"): "mime_value",
    ("email", "attachment_magic_prefix_hex_*"): "mime_value",
    ("email", "attachment_magic_hex"): "mime_value",
    ("email", "attachment_declared_vs_magic_mismatch"): "mime_value",
    ("email", "declared_vs_magic_mismatch"): "mime_value",
    ("email", "attachment_magic_mismatch"): "mime_value",
    ("email", "attachment_type_mismatch"): "mime_value",
    ("email", "attachment_extension_mismatch"): "mime_value",
    ("email", "mismatched_attachment_names"): "mime_value",
    ("email", "attachment_mismatch_names"): "mime_value",
    ("email", "attachment_content_dispositions"): "mime_value",
    ("email", "attachment_content_transfer_encodings"): "mime_value",
    ("email", "attachment_transfer_encodings"): "mime_value",
    ("email", "content_transfer_encodings"): "mime_value",
    ("email", "transfer_encodings"): "mime_value",
    ("email", "mime_content_transfer_encodings"): "mime_value",
    ("email", "part_content_transfer_encodings"): "mime_value",
    ("email", "body_text_sha256"): "mime_value",
    ("email", "body_sha256"): "mime_value",
    ("email", "text_body_sha256"): "mime_value",
    ("email", "plain_body_sha256"): "mime_value",
    ("email", "body_plain_sha256"): "mime_value",
    ("email", "text_plain_sha256"): "mime_value",
    ("email", "body_text_md5"): "mime_value",
    ("email", "body_text_sha1"): "mime_value",
    ("email", "body_html_sha256"): "mime_value",
    ("email", "html_body_sha256"): "mime_value",
    ("email", "body_text_size_bytes"): "mime_value",
    ("mime", "mime_part_count"): "mime_value",
    ("mime", "part_count"): "mime_value",
    ("mime", "mime_parts_count"): "mime_value",
    ("mime", "total_part_count"): "mime_value",
    ("mime", "mime_leaf_part_count"): "mime_value",
    ("mime", "leaf_part_count"): "mime_value",
    ("mime", "non_multipart_part_count"): "mime_value",
    ("mime", "mime_part_content_types"): "mime_value",
    ("mime", "part_content_types"): "mime_value",
    ("mime", "mime_content_types"): "mime_value",
    ("mime", "content_type"): "mime_value",
    ("mime", "top_level_content_type"): "mime_value",
    ("mime", "root_content_type"): "mime_value",
    ("mime", "mime_content_type"): "mime_value",
    ("mime", "top_content_type"): "mime_value",
    ("mime", "message_content_type"): "mime_value",
    ("mime", "mime_boundary"): "mime_value",
    ("mime", "boundary"): "mime_value",
    ("mime", "top_level_boundary"): "mime_value",
    ("mime", "multipart_boundary"): "mime_value",
    ("mime", "root_boundary"): "mime_value",
    ("mime", "is_multipart"): "mime_value",
    ("mime", "mime_version"): "mime_value",
    ("mime", "attachment_content_types"): "mime_value",
    ("mime", "attachment_mime_types"): "mime_value",
    ("mime", "attachment_types"): "mime_value",
    ("mime", "attachment_content_type"): "mime_value",
    ("mime", "attachment_mime_type"): "mime_value",
    ("mime", "attachment_sizes_bytes"): "mime_value",
    ("mime", "attachment_sizes"): "mime_value",
    ("mime", "attachment_size_bytes"): "mime_value",
    ("mime", "attachment_size"): "mime_value",
    ("mime", "attachment_decoded_sizes_bytes"): "mime_value",
    ("mime", "attachment_total_size_bytes"): "mime_value",
    ("mime", "attachment_sha256s"): "mime_value",
    ("mime", "attachment_sha256"): "mime_value",
    ("mime", "attachment_sha256_hashes"): "mime_value",
    ("mime", "attachment_md5s"): "mime_value",
    ("mime", "attachment_md5"): "mime_value",
    ("mime", "attachment_md5_hashes"): "mime_value",
    ("mime", "attachment_sha1s"): "mime_value",
    ("mime", "attachment_sha1"): "mime_value",
    ("mime", "attachment_sha1_hashes"): "mime_value",
    ("mime", "attachment_name"): "mime_value",
    ("mime", "attachment_filename"): "mime_value",
    ("mime", "first_attachment_name"): "mime_value",
    ("mime", "first_attachment_sha256"): "mime_value",
    ("mime", "first_attachment_size_bytes"): "mime_value",
    ("mime", "attachment_extensions"): "mime_value",
    ("mime", "attachment_file_extensions"): "mime_value",
    ("mime", "attachment_magic_prefix_hex_*"): "mime_value",
    ("mime", "attachment_magic_hex"): "mime_value",
    ("mime", "attachment_declared_vs_magic_mismatch"): "mime_value",
    ("mime", "declared_vs_magic_mismatch"): "mime_value",
    ("mime", "attachment_magic_mismatch"): "mime_value",
    ("mime", "attachment_type_mismatch"): "mime_value",
    ("mime", "attachment_extension_mismatch"): "mime_value",
    ("mime", "mismatched_attachment_names"): "mime_value",
    ("mime", "attachment_mismatch_names"): "mime_value",
    ("mime", "attachment_content_dispositions"): "mime_value",
    ("mime", "attachment_content_transfer_encodings"): "mime_value",
    ("mime", "attachment_transfer_encodings"): "mime_value",
    ("mime", "content_transfer_encodings"): "mime_value",
    ("mime", "transfer_encodings"): "mime_value",
    ("mime", "mime_content_transfer_encodings"): "mime_value",
    ("mime", "part_content_transfer_encodings"): "mime_value",
    ("mime", "body_text_sha256"): "mime_value",
    ("mime", "body_sha256"): "mime_value",
    ("mime", "text_body_sha256"): "mime_value",
    ("mime", "plain_body_sha256"): "mime_value",
    ("mime", "body_plain_sha256"): "mime_value",
    ("mime", "text_plain_sha256"): "mime_value",
    ("mime", "body_text_md5"): "mime_value",
    ("mime", "body_text_sha1"): "mime_value",
    ("mime", "body_html_sha256"): "mime_value",
    ("mime", "html_body_sha256"): "mime_value",
    ("mime", "body_text_size_bytes"): "mime_value",
    ("mail", "mime_part_count"): "mime_value",
    ("mail", "part_count"): "mime_value",
    ("mail", "mime_parts_count"): "mime_value",
    ("mail", "total_part_count"): "mime_value",
    ("mail", "mime_leaf_part_count"): "mime_value",
    ("mail", "leaf_part_count"): "mime_value",
    ("mail", "non_multipart_part_count"): "mime_value",
    ("mail", "mime_part_content_types"): "mime_value",
    ("mail", "part_content_types"): "mime_value",
    ("mail", "mime_content_types"): "mime_value",
    ("mail", "content_type"): "mime_value",
    ("mail", "top_level_content_type"): "mime_value",
    ("mail", "root_content_type"): "mime_value",
    ("mail", "mime_content_type"): "mime_value",
    ("mail", "top_content_type"): "mime_value",
    ("mail", "message_content_type"): "mime_value",
    ("mail", "mime_boundary"): "mime_value",
    ("mail", "boundary"): "mime_value",
    ("mail", "top_level_boundary"): "mime_value",
    ("mail", "multipart_boundary"): "mime_value",
    ("mail", "root_boundary"): "mime_value",
    ("mail", "is_multipart"): "mime_value",
    ("mail", "mime_version"): "mime_value",
    ("mail", "attachment_content_types"): "mime_value",
    ("mail", "attachment_mime_types"): "mime_value",
    ("mail", "attachment_types"): "mime_value",
    ("mail", "attachment_content_type"): "mime_value",
    ("mail", "attachment_mime_type"): "mime_value",
    ("mail", "attachment_sizes_bytes"): "mime_value",
    ("mail", "attachment_sizes"): "mime_value",
    ("mail", "attachment_size_bytes"): "mime_value",
    ("mail", "attachment_size"): "mime_value",
    ("mail", "attachment_decoded_sizes_bytes"): "mime_value",
    ("mail", "attachment_total_size_bytes"): "mime_value",
    ("mail", "attachment_sha256s"): "mime_value",
    ("mail", "attachment_sha256"): "mime_value",
    ("mail", "attachment_sha256_hashes"): "mime_value",
    ("mail", "attachment_md5s"): "mime_value",
    ("mail", "attachment_md5"): "mime_value",
    ("mail", "attachment_md5_hashes"): "mime_value",
    ("mail", "attachment_sha1s"): "mime_value",
    ("mail", "attachment_sha1"): "mime_value",
    ("mail", "attachment_sha1_hashes"): "mime_value",
    ("mail", "attachment_name"): "mime_value",
    ("mail", "attachment_filename"): "mime_value",
    ("mail", "first_attachment_name"): "mime_value",
    ("mail", "first_attachment_sha256"): "mime_value",
    ("mail", "first_attachment_size_bytes"): "mime_value",
    ("mail", "attachment_extensions"): "mime_value",
    ("mail", "attachment_file_extensions"): "mime_value",
    ("mail", "attachment_magic_prefix_hex_*"): "mime_value",
    ("mail", "attachment_magic_hex"): "mime_value",
    ("mail", "attachment_declared_vs_magic_mismatch"): "mime_value",
    ("mail", "declared_vs_magic_mismatch"): "mime_value",
    ("mail", "attachment_magic_mismatch"): "mime_value",
    ("mail", "attachment_type_mismatch"): "mime_value",
    ("mail", "attachment_extension_mismatch"): "mime_value",
    ("mail", "mismatched_attachment_names"): "mime_value",
    ("mail", "attachment_mismatch_names"): "mime_value",
    ("mail", "attachment_content_dispositions"): "mime_value",
    ("mail", "attachment_content_transfer_encodings"): "mime_value",
    ("mail", "attachment_transfer_encodings"): "mime_value",
    ("mail", "content_transfer_encodings"): "mime_value",
    ("mail", "transfer_encodings"): "mime_value",
    ("mail", "mime_content_transfer_encodings"): "mime_value",
    ("mail", "part_content_transfer_encodings"): "mime_value",
    ("mail", "body_text_sha256"): "mime_value",
    ("mail", "body_sha256"): "mime_value",
    ("mail", "text_body_sha256"): "mime_value",
    ("mail", "plain_body_sha256"): "mime_value",
    ("mail", "body_plain_sha256"): "mime_value",
    ("mail", "text_plain_sha256"): "mime_value",
    ("mail", "body_text_md5"): "mime_value",
    ("mail", "body_text_sha1"): "mime_value",
    ("mail", "body_html_sha256"): "mime_value",
    ("mail", "html_body_sha256"): "mime_value",
    ("mail", "body_text_size_bytes"): "mime_value",
}

_IDENT = ("from", "received", "message-id", "date", "return-path", "mime-version", "content-type")

# magic family -> leading bytes
_MAGIC = (("pdf", (b"%PDF",)), ("zip", (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")),
          ("pe", (b"MZ",)), ("ole", (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",)), ("png", (b"\x89PNG\r\n\x1a\n",)),
          ("jpeg", (b"\xff\xd8\xff",)), ("gif", (b"GIF87a", b"GIF89a")), ("rar", (b"Rar!\x1a\x07",)),
          ("7z", (b"7z\xbc\xaf\x27\x1c",)), ("gzip", (b"\x1f\x8b",)), ("elf", (b"\x7fELF",)), ("rtf", (b"{\\rtf",)),
          ("lnk", (b"L\x00\x00\x00\x01\x14\x02\x00",)), ("cab", (b"MSCF",)), ("iso", ()), ("bmp", (b"BM",)),
          ("onenote", (b"\xe4\x52\x5c\x7b\x8c\xd8\xa7\x4d",)))
_EXT = {"pdf": "pdf", "zip": "zip", "docx": "zip", "xlsx": "zip", "pptx": "zip", "docm": "zip", "xlsm": "zip",
        "pptm": "zip", "jar": "zip", "apk": "zip", "odt": "zip", "ods": "zip", "exe": "pe", "dll": "pe", "scr": "pe",
        "sys": "pe", "com": "pe", "cpl": "pe", "ocx": "pe", "doc": "ole", "xls": "ole", "ppt": "ole", "msi": "ole",
        "msg": "ole", "png": "png", "jpg": "jpeg", "jpeg": "jpeg", "gif": "gif", "rar": "rar", "7z": "7z",
        "gz": "gzip", "tgz": "gzip", "rtf": "rtf", "lnk": "lnk", "cab": "cab", "bmp": "bmp", "one": "onenote",
        "elf": "elf", "so": "elf", "txt": "text", "csv": "text", "htm": "text", "html": "text", "js": "text",
        "vbs": "text", "ps1": "text", "bat": "text", "cmd": "text", "hta": "text", "xml": "text", "eml": "text"}
_CT = {"application/pdf": "pdf", "application/zip": "zip", "application/x-zip-compressed": "zip",
       "application/x-msdownload": "pe", "application/x-dosexec": "pe", "application/x-msdos-program": "pe",
       "application/vnd.microsoft.portable-executable": "pe", "application/msword": "ole",
       "application/vnd.ms-excel": "ole", "application/vnd.ms-powerpoint": "ole", "application/x-msi": "ole",
       "image/png": "png", "image/jpeg": "jpeg", "image/gif": "gif", "image/bmp": "bmp",
       "application/x-rar-compressed": "rar", "application/vnd.rar": "rar", "application/x-7z-compressed": "7z",
       "application/gzip": "gzip", "application/x-gzip": "gzip", "application/rtf": "rtf", "text/rtf": "rtf",
       "application/onenote": "onenote", "text/plain": "text", "text/html": "text", "text/csv": "text"}


def _parse(b):
    import email
    import email.policy
    b = bytes(b)
    if not b or b[:4] in (b"PK\x03\x04", b"%PDF") or b[:2] == b"MZ" or b"\x00" in b[:512]:
        return None
    b = b[3:] if b[:3] == b"\xef\xbb\xbf" else b
    if b[:5] == b"From ":   # mbox envelope line
        b = b.split(b"\n", 1)[1] if b"\n" in b else b""
    msg = email.message_from_bytes(b, policy=email.policy.default)
    if not any(k.lower() in _IDENT for k in msg.keys()):
        return None
    return msg


def _filename(part):
    try:
        fn = part.get_filename()
    except Exception:  # noqa: BLE001
        fn = part.get_param("filename", header="content-disposition") or part.get_param("name")
    return str(fn).strip() if fn else None


def _payload(part):
    try:
        p = part.get_payload(decode=True)
    except Exception:  # noqa: BLE001
        p = None
    return bytes(p) if p is not None else b""


def _attachments(msg):
    return [(fn, part) for part in msg.walk() if not part.is_multipart() for fn in [_filename(part)] if fn]


def _family(data):
    for fam, sigs in _MAGIC:
        if any(data.startswith(s) for s in sigs):
            return fam
    if not data:
        return None
    head = data[:512]
    try:
        head.decode("utf-8")
        return "text"
    except UnicodeDecodeError:
        return None


def _mismatch(fn, part, data):
    got = _family(data)
    ext = fn.rsplit(".", 1)[-1].lower() if "." in fn else ""
    declared = [_EXT.get(ext), _CT.get(part.get_content_type())]
    declared = [d for d in declared if d]
    if not declared:
        return False
    return any(d != got for d in declared)


def _cte(part):
    v = part.get("content-transfer-encoding")
    return str(v).strip().lower() if v is not None else "7bit"


def _body(msg, kind):
    try:
        part = msg.get_body(preferencelist=(kind,))
    except Exception:  # noqa: BLE001
        part = None
    if part is None and kind == "plain" and not msg.is_multipart() and msg.get_content_type() == "text/plain":
        part = msg
    return None if part is None else _payload(part)


def _nbytes(ctx, field):
    m = re.search(r"_(\d+)$", field)
    if m:
        return int(m.group(1))
    p = str((ctx or {}).get("param") or "")
    return int(p) if p.isdigit() else 16


def mime_value(data, ctx):
    if data is None:
        return None
    field = (ctx or {}).get("field") or ""
    try:
        v = _value(data, field, ctx)
    except Exception:  # noqa: BLE001 -- a malformed message never raises past the extractor
        return None
    return "none" if v is None or v == "" else v


_HASH = {"sha256": hashlib.sha256, "md5": hashlib.md5, "sha1": hashlib.sha1}


def _value(b, f, ctx):
    msg = _parse(b)
    if msg is None:
        return None
    if f in ("mime_part_count", "part_count", "mime_parts_count", "total_part_count"):
        return len(list(msg.walk()))
    if f in ("mime_leaf_part_count", "leaf_part_count", "non_multipart_part_count"):
        return sum(1 for p in msg.walk() if not p.is_multipart())
    if f in ("mime_part_content_types", "part_content_types", "mime_content_types"):
        return [p.get_content_type() for p in msg.walk()]
    if f.endswith("content_type") and not f.startswith("attachment"):
        return msg.get_content_type()
    if f.endswith("boundary"):
        return msg.get_boundary() if msg.is_multipart() else None
    if f == "is_multipart":
        return msg.is_multipart()
    if f == "mime_version":
        v = msg.get("mime-version")
        return str(v).strip() if v is not None else None
    if f in ("content_transfer_encodings", "transfer_encodings", "mime_content_transfer_encodings",
             "part_content_transfer_encodings"):
        return [_cte(p) for p in msg.walk() if not p.is_multipart()] or None
    if f.startswith(("body_", "text_body", "plain_body", "text_plain", "html_body")):
        kind = "html" if "html" in f else "plain"
        body = _body(msg, kind)
        if body is None:
            return None
        if f.endswith("size_bytes"):
            return len(body)
        algo = f.rsplit("_", 1)[-1]
        return _HASH[algo](body).hexdigest() if algo in _HASH else None
    if "attachment" not in f and "mismatch" not in f:
        return None
    atts = [(fn, part, _payload(part)) for fn, part in _attachments(msg)]
    if not atts:   # an e-mail without attachments: nothing mismatches; every list/value is absent
        return False if "mismatch" in f and not f.endswith("names") else None
    if "mismatch" in f:
        bad = [fn for fn, part, data in atts if _mismatch(fn, part, data)]
        return bad or None if f.endswith("names") else bool(bad)
    if f == "attachment_total_size_bytes":
        return sum(len(d) for _, _, d in atts)
    if "magic" in f:
        if f == "attachment_magic_hex":
            return atts[0][2][:16].hex()
        n = _nbytes(ctx, f)
        return [d[:n].hex() for _, _, d in atts]
    if f.startswith("first_attachment_"):
        f, single = "attachment_" + f[len("first_attachment_"):], True
    else:
        single = not (f.endswith("sizes_bytes") or (f.endswith("s") and not f.endswith("_bytes")))
    if f in ("attachment_name", "attachment_filename"):
        vals = [fn for fn, _, _ in atts]
    elif "content_type" in f or "mime_type" in f or f == "attachment_types":
        vals = [p.get_content_type() for _, p, _ in atts]
    elif "size" in f:
        vals = [len(d) for _, _, d in atts]
    elif "extension" in f:
        vals = [fn.rsplit(".", 1)[-1].lower() if "." in fn else "" for fn, _, _ in atts]
    elif "disposition" in f:
        vals = [p.get_content_disposition() or "none" for _, p, _ in atts]
    elif "transfer_encoding" in f:
        vals = [_cte(p) for _, p, _ in atts]
    else:
        algo = next((a for a in ("sha256", "sha1", "md5") if a in f), None)
        if algo is None:
            return None
        vals = [_HASH[algo](d).hexdigest() for _, _, d in atts]
    return vals[0] if single else vals
