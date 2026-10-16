"""RFC 5322 / MIME e-mail (.eml) header fields (prebuilt, SPECULATIVE; message_id PROMOTED: lib.meta _BUILTIN
("email", "message_id") -> lib.meta.eml.message_id, GM-verified D16).

Parsed with stdlib email.message_from_bytes(b, policy=email.policy.default); header values come from raw_items()
(unfolded: CRLF + leading whitespace -> one space, then trimmed) so a malformed header never raises.
message_id = the stored Message-ID VERBATIM (angle brackets kept, as the header stores it).
return_path / from_address / to_address / reply_to_address / sender_address = the addr-spec only (no display name, no
<>; first address when several). subject = RFC 2047-decoded text. date = the Date header verbatim; date_utc = Date
parsed (RFC 5322 date-time with its zone) -> ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ' (same spelling as lnk/pe *_utc);
a "-0000" zone is read as UTC.
Received headers are prepended by each hop, so the LAST (bottom-most) Received is the first hop = the origin:
first_received_ip = the IP of that header's from-clause: the TCP-info "(rdns [1.2.3.4])" first (the peer the server
saw, not a "[HELO-literal]"), then any bracketed "[ip]" / "[IPv6:..]", then any IPv4 before "by"), last_received_ip = the same from the TOP header. received_hops = number of Received headers.
x_mailer = X-Mailer verbatim. attachment_names = filenames of the non-multipart parts with a filename or
Content-Disposition: attachment, in MIME walk order (list -> compact JSON); no attachment -> "none".
dkim_domain / dkim_selector = d= / s= of the FIRST DKIM-Signature. Not an e-mail (no From/Received/Message-ID/Date/
Return-Path header, binary magic) -> "none"; an absent header -> "none"."""
import re

FIELDS = {
    ("eml", "header_message_id"): "eml_value",
    ("eml", "return_path"): "eml_value",
    ("eml", "return_path_address"): "eml_value",
    ("eml", "envelope_from"): "eml_value",
    ("eml", "from_address"): "eml_value",
    ("eml", "from"): "eml_value",
    ("eml", "sender_address"): "eml_value",
    ("eml", "from_display_name"): "eml_value",
    ("eml", "from_name"): "eml_value",
    ("eml", "to_address"): "eml_value",
    ("eml", "to_addresses"): "eml_value",
    ("eml", "reply_to"): "eml_value",
    ("eml", "reply_to_address"): "eml_value",
    ("eml", "subject"): "eml_value",
    ("eml", "date"): "eml_value",
    ("eml", "date_utc"): "eml_value",
    ("eml", "date_iso8601"): "eml_value",
    ("eml", "sent_date_utc"): "eml_value",
    ("eml", "first_received_ip"): "eml_value",
    ("eml", "originating_ip"): "eml_value",
    ("eml", "source_ip"): "eml_value",
    ("eml", "sender_ip"): "eml_value",
    ("eml", "origin_ip"): "eml_value",
    ("eml", "first_hop_ip"): "eml_value",
    ("eml", "last_received_ip"): "eml_value",
    ("eml", "x_originating_ip"): "eml_value",
    ("eml", "received_hops"): "eml_value",
    ("eml", "received_count"): "eml_value",
    ("eml", "received_header_count"): "eml_value",
    ("eml", "hop_count"): "eml_value",
    ("eml", "x_mailer"): "eml_value",
    ("eml", "mailer"): "eml_value",
    ("eml", "user_agent"): "eml_value",
    ("eml", "attachment_names"): "eml_value",
    ("eml", "attachment_filenames"): "eml_value",
    ("eml", "attachment_file_names"): "eml_value",
    ("eml", "attachments"): "eml_value",
    ("eml", "attachment_count"): "eml_value",
    ("eml", "dkim_domain"): "eml_value",
    ("eml", "dkim_signature_domain"): "eml_value",
    ("eml", "dkim_d"): "eml_value",
    ("eml", "dkim_selector"): "eml_value",
    ("eml", "dkim_signature_selector"): "eml_value",
}

_IDENT = ("from", "received", "message-id", "date", "return-path")
_BRACKET_IP = re.compile(r"\[(?:IPv6:)?([0-9A-Fa-f:.]*[0-9A-Fa-f])\]")
_IPV4 = re.compile(r"(?<![\d.])((?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3})(?![\d.])")


def _unfold(v):
    return re.sub(r"\r?\n[ \t]+", " ", str(v)).strip()


def _parse(b):
    import email
    import email.policy
    b = bytes(b)
    if not b or b[:4] in (b"PK\x03\x04", b"%PDF", b"MZ\x90\x00") or b[:2] == b"MZ" or b"\x00" in b[:512]:
        return None
    b = b[3:] if b[:3] == b"\xef\xbb\xbf" else b
    if b[:5] == b"From ":   # mbox envelope line
        b = b.split(b"\n", 1)[1] if b"\n" in b else b""
    msg = email.message_from_bytes(b, policy=email.policy.default)
    raw = [(k.lower(), _unfold(v)) for k, v in msg.raw_items()]
    if not any(k in _IDENT for k, _ in raw):
        return None
    return msg, raw


def _hdr(raw, name):
    for k, v in raw:
        if k == name:
            return v
    return None


def _addr(v):
    from email.utils import getaddresses
    if v is None:
        return None
    for name, a in getaddresses([v]):
        if a:
            return a
    m = re.search(r"<([^<>]*)>", v)
    return m.group(1).strip() if m else (v.strip() or None)


def _received_ip(v):
    head = re.split(r"\sby\s", v, maxsplit=1)[0]
    # RFC 5321 4.4 TCP-info: "(rdns [peer-ip])" is the address the server saw; a bare "[ip]" before it is the
    # client's own (spoofable) HELO literal
    tcp_info = " ".join(re.findall(r"\(([^()]*)\)", head))
    for part in (tcp_info, head, v):
        for m in _BRACKET_IP.finditer(part):
            ip = m.group(1)
            if _IPV4.fullmatch(ip) or ":" in ip:
                return ip
        m = _IPV4.search(part)
        if m:
            return m.group(1)
    return None


def _dkim_tag(raw, tag):
    v = _hdr(raw, "dkim-signature")
    if v is None:
        return None
    m = re.search(r"(?:^|;)\s*%s\s*=\s*([^;]*)" % tag, v)
    return re.sub(r"\s+", "", m.group(1)) if m and m.group(1).strip() else None


def _attachments(msg):
    out = []
    for part in msg.walk():
        if part.is_multipart():
            continue
        try:
            fn = part.get_filename()
        except Exception:  # noqa: BLE001
            fn = part.get_param("filename", header="content-disposition") or part.get_param("name")
        if fn:
            out.append(str(fn).strip())
    return out


def _date_utc(v):
    import datetime
    from email.utils import parsedate_to_datetime
    if not v:
        return None
    dt = parsedate_to_datetime(v)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def eml_value(data, ctx):
    if data is None:
        return None
    try:
        v = _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed message never raises past the extractor
        return None
    return "none" if v is None or v == "" else v


def _value(b, f):
    p = _parse(b)
    if p is None:
        return "none"
    msg, raw = p
    if "message_id" in f:
        return _hdr(raw, "message-id")
    if f in ("return_path", "return_path_address", "envelope_from"):
        return _addr(_hdr(raw, "return-path"))
    if f in ("from_address", "from"):
        return _addr(_hdr(raw, "from"))
    if f == "sender_address":
        return _addr(_hdr(raw, "sender"))
    if f in ("from_display_name", "from_name"):
        try:
            h = msg["from"]
            return h.addresses[0].display_name if h is not None and h.addresses else None
        except Exception:  # noqa: BLE001
            return None
    if f in ("to_address", "to_addresses"):
        return _addr(_hdr(raw, "to"))
    if f.startswith("reply_to"):
        return _addr(_hdr(raw, "reply-to"))
    if f == "subject":
        h = msg["subject"]
        return None if h is None else _unfold(h)
    if f == "date":
        return _hdr(raw, "date")
    if f.startswith("date") or f == "sent_date_utc":
        return _date_utc(_hdr(raw, "date"))
    rec = [v for k, v in raw if k == "received"]
    if f in ("received_hops", "received_count", "received_header_count", "hop_count"):
        return len(rec)
    if f == "last_received_ip":
        return _received_ip(rec[0]) if rec else None
    if f == "x_originating_ip":
        v = _hdr(raw, "x-originating-ip")
        return None if v is None else v.strip().strip("[]").strip()
    if f.endswith("_ip"):
        return _received_ip(rec[-1]) if rec else None
    if f in ("x_mailer", "mailer"):
        return _hdr(raw, "x-mailer")
    if f == "user_agent":
        return _hdr(raw, "user-agent")
    if f == "attachment_count":
        return len(_attachments(msg))
    if f.startswith("attachment"):
        return _attachments(msg) or None
    if f.startswith("dkim"):
        return _dkim_tag(raw, "s" if "selector" in f else "d")
    return None
