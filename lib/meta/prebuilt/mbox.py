"""MBOX mailbox-export fields (prebuilt, SPECULATIVE): fmt `mbox` (alias `mailbox`).

Split: the member must start with an mbox envelope line b"From " (UTF-8 BOM / leading blank lines skipped); messages
are split at every line that starts with "From " (b"\\nFrom ", CRLF tolerated), the envelope line dropped, mboxrd
escapes ">From " / ">>From " unescaped one level, then email.message_from_bytes per message (stdlib mailbox needs a
path). Not an mbox (no leading "From " line, or no message has any RFC 5322 header) -> "none".
message_count = number of messages; message_ids = every Message-ID in file order (angle brackets kept, trimmed;
messages without one are skipped); unique_message_id_count = len(set); duplicate_message_ids = ids seen > 1 time,
sorted, each once ([] when none); duplicate_message_id_count = its length.
Threads = connected components over Message-ID / In-Reply-To / References links (JWZ steps 1-4: a missing parent
still joins its children; no subject grouping). thread_count = component count; thread_root_ids = per thread in
order of first appearance: the first message (file order) with no In-Reply-To/References, else the oldest referenced
id (References[0] / In-Reply-To of the thread's first message).
subjects = RFC 2047-decoded Subject per message, file order (absent skipped).
first_date_utc / last_date_utc = chronological min / max of the Date headers (envelope-line date when Date is
absent), converted to UTC ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' (the eml date_utc spelling)."""
import re

FIELDS = {
    ("mbox", "message_count"): "mbox_value",
    ("mbox", "messages_count"): "mbox_value",
    ("mbox", "number_of_messages"): "mbox_value",
    ("mbox", "email_count"): "mbox_value",
    ("mbox", "count"): "mbox_value",
    ("mbox", "message_ids"): "mbox_value",
    ("mbox", "message_id_list"): "mbox_value",
    ("mbox", "unique_message_id_count"): "mbox_value",
    ("mbox", "unique_message_ids"): "mbox_value",
    ("mbox", "duplicate_message_ids"): "mbox_value",
    ("mbox", "duplicate_message_id_count"): "mbox_value",
    ("mbox", "duplicate_count"): "mbox_value",
    ("mbox", "thread_count"): "mbox_value",
    ("mbox", "threads_count"): "mbox_value",
    ("mbox", "number_of_threads"): "mbox_value",
    ("mbox", "thread_root_ids"): "mbox_value",
    ("mbox", "thread_root_message_ids"): "mbox_value",
    ("mbox", "thread_roots"): "mbox_value",
    ("mbox", "subjects"): "mbox_value",
    ("mbox", "subject_list"): "mbox_value",
    ("mbox", "first_message_id"): "mbox_value",
    ("mbox", "last_message_id"): "mbox_value",
    ("mbox", "first_date_utc"): "mbox_value",
    ("mbox", "earliest_date_utc"): "mbox_value",
    ("mbox", "last_date_utc"): "mbox_value",
    ("mbox", "latest_date_utc"): "mbox_value",
    ("mailbox", "message_count"): "mbox_value",
    ("mailbox", "messages_count"): "mbox_value",
    ("mailbox", "number_of_messages"): "mbox_value",
    ("mailbox", "email_count"): "mbox_value",
    ("mailbox", "count"): "mbox_value",
    ("mailbox", "message_ids"): "mbox_value",
    ("mailbox", "message_id_list"): "mbox_value",
    ("mailbox", "unique_message_id_count"): "mbox_value",
    ("mailbox", "unique_message_ids"): "mbox_value",
    ("mailbox", "duplicate_message_ids"): "mbox_value",
    ("mailbox", "duplicate_message_id_count"): "mbox_value",
    ("mailbox", "duplicate_count"): "mbox_value",
    ("mailbox", "thread_count"): "mbox_value",
    ("mailbox", "threads_count"): "mbox_value",
    ("mailbox", "number_of_threads"): "mbox_value",
    ("mailbox", "thread_root_ids"): "mbox_value",
    ("mailbox", "thread_root_message_ids"): "mbox_value",
    ("mailbox", "thread_roots"): "mbox_value",
    ("mailbox", "subjects"): "mbox_value",
    ("mailbox", "subject_list"): "mbox_value",
    ("mailbox", "first_message_id"): "mbox_value",
    ("mailbox", "last_message_id"): "mbox_value",
    ("mailbox", "first_date_utc"): "mbox_value",
    ("mailbox", "earliest_date_utc"): "mbox_value",
    ("mailbox", "last_date_utc"): "mbox_value",
    ("mailbox", "latest_date_utc"): "mbox_value",
}

_SPLIT = re.compile(rb"\r?\nFrom ")
_UNESC = re.compile(rb"(?m)^>(>*From )")
_MSGID = re.compile(r"<[^<>\s]+>")


def _unfold(v):
    return re.sub(r"\s*\r?\n\s*", " ", str(v)).strip() if v is not None else None


def _subject(v):
    from email.header import decode_header, make_header
    try:
        return _unfold(str(make_header(decode_header(v))))
    except Exception:  # noqa: BLE001 -- malformed encoded-word: keep the raw text
        return _unfold(v)


def _utc(v):
    import datetime
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(v)
    except (TypeError, ValueError, IndexError):
        return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _env_date(line):
    """asctime date of an envelope line 'From sender Thu Oct 15 10:00:00 2026' (treated as UTC), or None."""
    import datetime
    m = re.search(r"(\w{3})\s+(\w{3})\s+(\d{1,2})\s+(\d{1,2}:\d{2}:\d{2})\s+(\d{4})", line)
    if not m:
        return None
    try:
        return datetime.datetime.strptime(" ".join(m.groups()[1:]), "%b %d %H:%M:%S %Y").replace(
            tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


def _messages(b):
    """[(envelope_line, email.message.Message)] or None when `b` is not an mbox."""
    import email
    b = bytes(b)
    if b[:3] == b"\xef\xbb\xbf":
        b = b[3:]
    b = b.lstrip(b"\r\n")
    if not b.startswith(b"From ") or b"\x00" in b[:512]:
        return None
    out = []
    for chunk in _SPLIT.split(b):
        if chunk.startswith(b"From "):
            chunk = chunk[5:]
        env, _, rest = chunk.partition(b"\n")
        rest = _UNESC.sub(rb"\1", rest)
        out.append((env.decode("latin-1").strip(), email.message_from_bytes(rest)))
    if not any(m.keys() for _, m in out):
        return None
    return out


def _threads(msgs):
    """[(root_id, [message indexes])] in order of first appearance."""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, c):
        ra, rc = find(a), find(c)
        if ra != rc:
            parent[rc] = ra

    keys, links = [], []
    for i, (_, m) in enumerate(msgs):
        mid = (_MSGID.findall(_unfold(m.get("Message-ID")) or "") or [None])[0]
        refs = _MSGID.findall(_unfold(m.get("References")) or "")
        irt = _MSGID.findall(_unfold(m.get("In-Reply-To")) or "")
        chain = refs + [x for x in irt if x not in refs]
        key = mid or "\x00msg%d" % i
        keys.append(key)
        links.append(chain)
        find(key)
        for r in chain:
            union(r, key)
    groups = {}
    order = []
    for i, k in enumerate(keys):
        r = find(k)
        if r not in groups:
            groups[r] = []
            order.append(r)
        groups[r].append(i)
    out = []
    for r in order:
        idx = groups[r]
        root = next((keys[i] for i in idx if not links[i] and not keys[i].startswith("\x00")), None)
        if root is None:
            first = links[idx[0]]
            root = first[0] if first else keys[idx[0]]
        out.append((root, idx))
    return out


def _value(msgs, f):
    ids = []
    for _, m in msgs:
        mid = _unfold(m.get("Message-ID"))
        if mid:
            ids.append(mid)
    if f in ("message_count", "messages_count", "number_of_messages", "email_count", "count"):
        return len(msgs)
    if f in ("message_ids", "message_id_list"):
        return ids
    if f == "first_message_id":
        return ids[0] if ids else "none"
    if f == "last_message_id":
        return ids[-1] if ids else "none"
    if f == "unique_message_id_count":
        return len(set(ids))
    if f == "unique_message_ids":
        return list(dict.fromkeys(ids))
    dups = sorted(x for x in set(ids) if ids.count(x) > 1)
    if f == "duplicate_message_ids":
        return dups
    if f in ("duplicate_message_id_count", "duplicate_count"):
        return len(dups)
    if f in ("thread_count", "threads_count", "number_of_threads"):
        return len(_threads(msgs))
    if f in ("thread_root_ids", "thread_root_message_ids", "thread_roots"):
        return [r for r, _ in _threads(msgs) if not r.startswith("\x00")]
    if f in ("subjects", "subject_list"):
        return [_subject(m.get("Subject")) for _, m in msgs if m.get("Subject") is not None]
    if f in ("first_date_utc", "earliest_date_utc", "last_date_utc", "latest_date_utc"):
        dates = []
        for env, m in msgs:
            d = _utc(m.get("Date")) if m.get("Date") else None
            d = d or _env_date(env)
            if d is not None:
                dates.append(d)
        if not dates:
            return "none"
        d = min(dates) if f in ("first_date_utc", "earliest_date_utc") else max(dates)
        return d.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def mbox_value(data, ctx):
    if data is None:
        return None
    try:
        msgs = _messages(data)
        if not msgs:
            return "none"
        return _value(msgs, ctx.get("field") or "")
    except Exception:  # noqa: BLE001 -- defensive: never raise past the extractor
        return None
