"""Outlook .msg ([MS-OXMSG] on a CFB container) message properties (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout: the ROOT storage is the message; each variable-length property is a stream `__substg1.0_<TAG>` where TAG =
PropId(4 hex) + PropType(4 hex): 001F = PT_UNICODE (UTF-16LE), 001E = PT_STRING8 (8-bit, code page PR_MESSAGE_CODEPAGE
0x3FFD, cp1252 default), 0102 = binary. Fixed-size properties sit in `__properties_version1.0`: a 32-byte header at the
root (24 in an embedded message, 8 in a recipient/attachment storage) then 16-byte entries {tag u32le, flags u32le,
value 8 bytes}. Attachments are `__attach_version1.0_#XXXXXXXX` storages, recipients `__recip_version1.0_#XXXXXXXX`.
Only ROOT-level streams are message properties (an attachment's embedded message repeats the same stream names one
level down), so the walk is path-aware (olefile) rather than lib.meta.cfb.cfb_streams (flat names, collide).

message_id = PR_INTERNET_MESSAGE_ID 0x1035 verbatim (angle brackets KEPT, as the GM-verified D16 email.message_id);
in_reply_to = PR_IN_REPLY_TO_ID 0x1042; subject = PR_SUBJECT 0x0037 (prefix "RE: " kept); message_class = 0x001A
(IPM.Note); transport_headers = PR_TRANSPORT_MESSAGE_HEADERS 0x007D (trimmed); sender_email = PR_SENDER_EMAIL_ADDRESS
0x0C1F when it is an SMTP address, else PR_SENDER_SMTP_ADDRESS 0x5D01 (an Exchange sender stores an X.500 DN in 0C1F),
else 0C1F as stored; attachment_names = per attachment storage in storage order, PR_ATTACH_LONG_FILENAME 0x3707 else
PR_ATTACH_FILENAME 0x3704 else PR_DISPLAY_NAME 0x3001 (JSON list); attachment_count = number of attachment storages.
Times: PT_SYSTIME 0x0040 FILETIME (100 ns since 1601-01-01, UTC by spec) -> ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ'
(same spelling as lnk/ole *_time); client_submit_time = PR_CLIENT_SUBMIT_TIME 0x0039 (sent), message_delivery_time =
PR_MESSAGE_DELIVERY_TIME 0x0E06 (received). Absent property / zero FILETIME -> "none"; not an Outlook .msg (decoy:
other CFB without __substg1.0_ / IPM class, renamed .eml/zip) -> "none"."""
import datetime
import io
import struct

FIELDS = {
    ("msg", "message_id"): "message_value", ("msg", "internet_message_id"): "message_value",
    ("msg", "header_message_id"): "message_value", ("msg", "in_reply_to"): "message_value",
    ("msg", "in_reply_to_id"): "message_value", ("msg", "subject"): "message_value",
    ("msg", "normalized_subject"): "message_value", ("msg", "conversation_topic"): "message_value",
    ("msg", "sender_email"): "message_value", ("msg", "sender_email_address"): "message_value",
    ("msg", "sender_address"): "message_value", ("msg", "sender_smtp_address"): "message_value",
    ("msg", "from_address"): "message_value", ("msg", "from_email"): "message_value",
    ("msg", "sender_name"): "message_value", ("msg", "from_name"): "message_value",
    ("msg", "from_display_name"): "message_value", ("msg", "display_to"): "message_value",
    ("msg", "display_cc"): "message_value", ("msg", "message_class"): "message_value",
    ("msg", "transport_headers"): "message_value", ("msg", "transport_message_headers"): "message_value",
    ("msg", "internet_headers"): "message_value", ("msg", "attachment_names"): "message_value",
    ("msg", "attachment_filenames"): "message_value", ("msg", "attachment_file_names"): "message_value",
    ("msg", "attachment_long_filenames"): "message_value", ("msg", "attachment_count"): "message_value",
    ("msg", "number_of_attachments"): "message_value", ("msg", "recipient_count"): "message_value",
    ("msg", "client_submit_time_utc"): "message_value", ("msg", "client_submit_time"): "message_value",
    ("msg", "submit_time_utc"): "message_value", ("msg", "sent_time_utc"): "message_value",
    ("msg", "sent_date_utc"): "message_value", ("msg", "message_delivery_time_utc"): "message_value",
    ("msg", "message_delivery_time"): "message_value", ("msg", "delivery_time_utc"): "message_value",
    ("msg", "received_time_utc"): "message_value",
    ("outlook", "message_id"): "message_value", ("outlook", "in_reply_to"): "message_value",
    ("outlook", "subject"): "message_value", ("outlook", "sender_email"): "message_value",
    ("outlook", "message_class"): "message_value", ("outlook", "transport_headers"): "message_value",
    ("outlook", "attachment_names"): "message_value", ("outlook", "attachment_count"): "message_value",
    ("outlook", "client_submit_time_utc"): "message_value",
}

_STR = {"message_id": (0x1035,), "internet_message_id": (0x1035,), "header_message_id": (0x1035,),
        "in_reply_to": (0x1042,), "in_reply_to_id": (0x1042,), "subject": (0x0037,),
        "normalized_subject": (0x0E1D,), "conversation_topic": (0x0070,), "sender_name": (0x0C1A,),
        "from_name": (0x0C1A,), "from_display_name": (0x0C1A,), "display_to": (0x0E04,), "display_cc": (0x0E03,),
        "message_class": (0x001A,), "transport_headers": (0x007D,), "transport_message_headers": (0x007D,),
        "internet_headers": (0x007D,), "sender_smtp_address": (0x5D01, 0x0C1F)}
_SENDER = ("sender_email", "sender_email_address", "sender_address", "from_address", "from_email")
_ATT = ("attachment_names", "attachment_filenames", "attachment_file_names", "attachment_long_filenames")
_TIME = {"client_submit_time": 0x0039, "submit_time": 0x0039, "sent_time": 0x0039, "sent_date": 0x0039,
         "message_delivery_time": 0x0E06, "delivery_time": 0x0E06, "received_time": 0x0E06}


def _ole(b):
    if not b or b[:8] != bytes.fromhex("d0cf11e0a1b11ae1"):
        return None
    try:
        import olefile
        o = olefile.OleFileIO(io.BytesIO(b))
    except Exception:
        return None
    try:
        root = {"/".join(p) for p in o.listdir(streams=True, storages=True)}
    except Exception:
        return None
    if not any(p.startswith("__substg1.0_") for p in root) and "__properties_version1.0" not in root:
        return None
    return o, root


def _read(o, path):
    try:
        return o.openstream(path).read()
    except Exception:
        return None


def _codepage(o):
    raw = _props(o, "__properties_version1.0", 32).get(0x3FFD0003)
    cp = struct.unpack_from("<I", raw)[0] if raw else 1252
    return {65001: "utf-8", 20127: "ascii", 28591: "latin-1"}.get(cp, "cp%d" % cp)


def _str(o, base, pid, root):
    """A string property of storage `base` ('' = message): PT_UNICODE first, then PT_STRING8; None when absent."""
    pre = base + "/" if base else ""
    raw = _read(o, "%s__substg1.0_%04X001F" % (pre, pid)) if pre + "__substg1.0_%04X001F" % pid in root else None
    if raw is not None:
        return raw[:len(raw) // 2 * 2].decode("utf-16le", "replace").split("\x00")[0].strip()
    if pre + "__substg1.0_%04X001E" % pid in root:
        raw = _read(o, "%s__substg1.0_%04X001E" % (pre, pid)) or b""
        try:
            s = raw.decode(_codepage(o), "replace")
        except LookupError:
            s = raw.decode("cp1252", "replace")
        return s.split("\x00")[0].strip()
    return None


def _props(o, path, hdr):
    """{tag: 8 value bytes} of a __properties_version1.0 stream."""
    raw = _read(o, path) or b""
    out = {}
    for i in range(hdr, len(raw) - 15, 16):
        tag, = struct.unpack_from("<I", raw, i)
        out.setdefault(tag, raw[i + 8:i + 16])
    return out


def _filetime(v):
    ft, = struct.unpack("<Q", v)
    if not ft:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ft // 10)
    except OverflowError:
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def message_value(data, ctx):
    try:
        return _value(data, ctx)
    except Exception:
        return None


def _value(data, ctx):
    if data is None:
        return None
    field = ctx.get("field") or ""
    p = _ole(data)
    if p is None:
        return "none"
    o, root = p
    try:
        if field in _STR:
            for pid in _STR[field]:
                v = _str(o, "", pid, root)
                if v:
                    return v
            return "none"
        if field in _SENDER:
            a = _str(o, "", 0x0C1F, root)
            if a and "@" in a:
                return a
            s = _str(o, "", 0x5D01, root) or _str(o, "", 0x0065, root)
            return s or a or "none"
        tops = sorted(p for p in root if "/" not in p)
        atts = sorted(p for p in tops if p.startswith("__attach_version1.0_#"))
        atts = [a for a in atts if a + "/__properties_version1.0" in root or any(r.startswith(a + "/") for r in root)]
        if field in ("attachment_count", "number_of_attachments"):
            return len(atts)
        if field == "recipient_count":
            return len([r for r in tops if r.startswith("__recip_version1.0_#")])
        if field in _ATT:
            names = []
            for a in atts:
                n = _str(o, a, 0x3707, root) or _str(o, a, 0x3704, root) or _str(o, a, 0x3001, root)
                if n:
                    names.append(n)
            return names if names else "none"
        base = field[:-4] if field.endswith("_utc") else field
        if base in _TIME:
            v = _props(o, "__properties_version1.0", 32).get((_TIME[base] << 16) | 0x0040)
            return _filetime(v) if v else "none"
        return None
    finally:
        o.close()
