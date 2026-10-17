"""RFC 5322 e-mail THREADING fields for `email` / `eml` (prebuilt, SPECULATIVE). Parsing is eml.py's (_parse: stdlib
email, policy.default, raw_items() unfolded + trimmed; not an e-mail -> "none"); this module only adds fields.

in_reply_to = the In-Reply-To header verbatim (angle brackets kept, like the GM-verified D16 message_id).
references = every "<msg-id>" token of the References header, stored order, brackets kept (list -> compact JSON);
references_count = its length (0 when the header is absent but the file is an e-mail).
thread_root_message_id = References[0], else the first In-Reply-To id, else the message's own Message-ID.
parent_message_id = the LAST References id (RFC 5322 3.6.4: References ends with the parent), else In-Reply-To.
is_reply = In-Reply-To / References present or a "Re:" subject prefix; is_forward = a "Fwd:/Fw:/FW:" subject prefix
or any X-Forwarded-* header. normalized_subject = the RFC 2047-decoded Subject with Re:/Fwd:/Fw: (and "Re[2]:")
prefixes stripped repeatedly (RFC 5256 base-subject style, case-insensitive).
Outlook Thread-Index = base64 of a 22-byte header block (1 reserved byte + 5 FILETIME bytes: the first 6 bytes
big-endian are FILETIME >> 16; then a 16-byte GUID in Windows bytes_le order) + 5-byte child blocks:
thread_index_guid = bytes 6..22 as a Windows GUID (lowercase 8-4-4-4-12, no braces); thread_index_reply_count =
number of 5-byte child blocks; thread_index_time_utc = (first 6 bytes BE << 16) as FILETIME -> ISO-8601 UTC 'Z'.
thread_topic = Thread-Topic (RFC 2047-decoded, like subject); resent_message_id = Resent-Message-ID verbatim.
header_<name> = the FIRST <name> header (underscores -> hyphens, case-insensitive), unfolded, verbatim (no decoding).
Absent header -> "none"."""
import re

FIELDS = {
    ("email", "in_reply_to"): "thread_value",
    ("email", "in_reply_to_message_id"): "thread_value",
    ("email", "references"): "thread_value",
    ("email", "references_ids"): "thread_value",
    ("email", "references_message_ids"): "thread_value",
    ("email", "reference_ids"): "thread_value",
    ("email", "references_count"): "thread_value",
    ("email", "reference_count"): "thread_value",
    ("email", "thread_root_message_id"): "thread_value",
    ("email", "thread_root"): "thread_value",
    ("email", "root_message_id"): "thread_value",
    ("email", "parent_message_id"): "thread_value",
    ("email", "is_reply"): "thread_value",
    ("email", "is_forward"): "thread_value",
    ("email", "is_forwarded"): "thread_value",
    ("email", "normalized_subject"): "thread_value",
    ("email", "base_subject"): "thread_value",
    ("email", "thread_index"): "thread_value",
    ("email", "thread_index_guid"): "thread_value",
    ("email", "thread_index_reply_count"): "thread_value",
    ("email", "thread_index_child_block_count"): "thread_value",
    ("email", "thread_index_time_utc"): "thread_value",
    ("email", "thread_topic"): "thread_value",
    ("email", "resent_message_id"): "thread_value",
    ("email", "header_*"): "header_value",
    ("eml", "in_reply_to"): "thread_value",
    ("eml", "in_reply_to_message_id"): "thread_value",
    ("eml", "references"): "thread_value",
    ("eml", "references_ids"): "thread_value",
    ("eml", "references_message_ids"): "thread_value",
    ("eml", "reference_ids"): "thread_value",
    ("eml", "references_count"): "thread_value",
    ("eml", "reference_count"): "thread_value",
    ("eml", "thread_root_message_id"): "thread_value",
    ("eml", "thread_root"): "thread_value",
    ("eml", "root_message_id"): "thread_value",
    ("eml", "parent_message_id"): "thread_value",
    ("eml", "is_reply"): "thread_value",
    ("eml", "is_forward"): "thread_value",
    ("eml", "is_forwarded"): "thread_value",
    ("eml", "normalized_subject"): "thread_value",
    ("eml", "base_subject"): "thread_value",
    ("eml", "thread_index"): "thread_value",
    ("eml", "thread_index_guid"): "thread_value",
    ("eml", "thread_index_reply_count"): "thread_value",
    ("eml", "thread_index_child_block_count"): "thread_value",
    ("eml", "thread_index_time_utc"): "thread_value",
    ("eml", "thread_topic"): "thread_value",
    ("eml", "resent_message_id"): "thread_value",
    ("eml", "header_*"): "header_value",
}

_MSGID = re.compile(r"<[^<>\s]+>")
_RE = re.compile(r"^\s*(?:re|fwd?|fw)\s*(?:\[\d+\])?\s*:\s*", re.I)
_FWD = re.compile(r"^\s*(?:fwd?|fw)\s*(?:\[\d+\])?\s*:", re.I)
_REPLY = re.compile(r"^\s*re\s*(?:\[\d+\])?\s*:", re.I)


def _hdr(raw, name):
    for k, v in raw:
        if k == name:
            return v
    return None


def _ids(v):
    return _MSGID.findall(v or "")


def _decoded(msg, name):
    h = msg[name]
    return None if h is None else re.sub(r"\s*\r?\n\s*", " ", str(h)).strip()


def _thread_index(v):
    import base64
    import binascii
    if not v:
        return None
    s = re.sub(r"\s+", "", v)
    try:
        b = base64.b64decode(s + "=" * (-len(s) % 4), validate=True)
    except (binascii.Error, ValueError):
        return None
    return b if len(b) >= 22 else None


def _filetime_utc(ft):
    import datetime
    if ft <= 0:
        return None
    dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ft // 10)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _value(b, f):
    from .eml import _parse
    from ..spell import Guid
    p = _parse(b)
    if p is None:
        return None
    msg, raw = p
    irt, refs = _hdr(raw, "in-reply-to"), _ids(_hdr(raw, "references"))
    if f.startswith("in_reply_to"):
        return irt
    if f in ("references_count", "reference_count"):
        return len(refs)
    if f.startswith("reference"):
        return refs or None
    if f in ("thread_root_message_id", "thread_root", "root_message_id"):
        return (refs or _ids(irt) or [None])[0] or _hdr(raw, "message-id")
    if f == "parent_message_id":
        return refs[-1] if refs else ((_ids(irt) or [irt])[-1] if irt else None)
    subj = _decoded(msg, "subject") or ""
    if f == "is_reply":
        return bool(irt or refs or _REPLY.match(subj))
    if f in ("is_forward", "is_forwarded"):
        return bool(_FWD.match(subj) or any(k.startswith("x-forwarded-") for k, _ in raw))
    if f in ("normalized_subject", "base_subject"):
        if msg["subject"] is None:
            return None
        prev = None
        while prev != subj:
            prev, subj = subj, _RE.sub("", subj, count=1)
        return subj.strip()
    if f.startswith("thread_index"):
        v = _hdr(raw, "thread-index")
        if f == "thread_index":
            return v
        ti = _thread_index(v)
        if ti is None:
            return None
        if f == "thread_index_guid":
            return Guid("bytes_le", ti[6:22])
        if f.endswith("_count"):
            return (len(ti) - 22) // 5
        if f == "thread_index_time_utc":
            return _filetime_utc(int.from_bytes(ti[:6], "big") << 16)
        return None
    if f == "thread_topic":
        return _decoded(msg, "thread-topic")
    if f == "resent_message_id":
        return _hdr(raw, "resent-message-id")
    return None


def thread_value(data, ctx):
    if data is None:
        return None
    try:
        v = _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed message never raises past the extractor
        return None
    return "none" if v is None or v == "" or v == [] else v


def header_value(data, ctx):
    """<email|eml>.header_<name>: first <name> header (underscores -> hyphens), unfolded, verbatim."""
    if data is None:
        return None
    name = str((ctx or {}).get("param") or "").strip("_").lower().replace("_", "-")
    if not name:
        return None
    try:
        from .eml import _parse
        p = _parse(data)
        v = None if p is None else _hdr(p[1], name)
    except Exception:  # noqa: BLE001
        return None
    return "none" if v is None or v == "" else v
