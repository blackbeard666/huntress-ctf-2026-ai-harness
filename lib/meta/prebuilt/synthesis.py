"""Cross-message e-mail THREADING synthesis (prebuilt, SPECULATIVE; spelling never GM-verified).
D16 flavor "rebuild which mail actually belongs together": the question lists `Files: [...]` (.eml members of the
artifact's container) and asks which belong to one conversation. Threads come from the HEADERS, never the Subject
(a same-subject message without References/In-Reply-To is a separate thread -- the decoy):
  * every Message-ID / In-Reply-To / References "<id>" is a union-find node; a message joins its own id with every id
    it references (a missing intermediate parent still links its siblings, RFC 5322 3.6.4 / JWZ-style containers);
    a message without a Message-ID is keyed by its filename;
  * dedupe by Message-ID: the first copy in (Date, filename) order is kept, the later copies are "duplicates" and
    are left out of the groups;
  * members ordered by Date (RFC 5322 -> UTC epoch; undated sorts last) then filename; threads ordered by their first
    member. thread_groups = compact JSON array of arrays of filenames in that order; thread_groups_sorted = the
    alternate spelling (each group's names sorted, groups sorted); thread_count = number of threads (singletons
    included); duplicate_filenames = the dropped copies, sorted; thread_root_filenames = per thread (same order) the
    earliest member referencing no other present member.
thread_groups(question, get_bytes) is the solver-facing call (like lib.meta.synthesis.digest_order): a day solver's
local_answer passes get_bytes(name) -> bytes|None over the container's siblings. Through lib.meta.answer (id
`...-synthesis-thread-groups`, fmt `synthesis`) the extractor reads siblings from ctx["read"] when a caller supplies
one, else from `data` itself when the artifact IS the container zip (all its .eml members when the question names no
Files list). A lone .eml / non-mail input -> None (cannot answer); a container holding no e-mail -> "none"."""
import io
import json
import re

FIELDS = {
    ("synthesis", "thread_groups"): "thread_value",
    ("synthesis", "email_thread_groups"): "thread_value",
    ("synthesis", "eml_thread_groups"): "thread_value",
    ("synthesis", "thread_groups_sorted"): "thread_value",
    ("synthesis", "thread_groups_by_date"): "thread_value",
    ("synthesis", "thread_count"): "thread_value",
    ("synthesis", "email_thread_count"): "thread_value",
    ("synthesis", "duplicate_filenames"): "thread_value",
    ("synthesis", "duplicate_files"): "thread_value",
    ("synthesis", "duplicate_message_filenames"): "thread_value",
    ("synthesis", "thread_root_filenames"): "thread_value",
    ("synthesis", "thread_roots"): "thread_value",
    ("synthesis", "root_filenames"): "thread_value",
}

_MSGID = re.compile(rb"<[^<>\s]+>")
_FILES = re.compile(r"Files:\s*(\[.*?\])", re.S)


def _header(b, name):
    """The first `name:` header of a raw message (unfolded, stripped) as bytes, or None."""
    head = re.split(rb"\r?\n\r?\n", b, 1)[0]
    m = re.search(rb"(?im)^" + re.escape(name) + rb"[ \t]*:(.*(?:\r?\n[ \t].*)*)", head)
    return re.sub(rb"\r?\n[ \t]", b" ", m.group(1)).strip() if m else None


def _message(b):
    """(message_id|None, [referenced ids], epoch|None) of one raw e-mail, or None when it isn't one."""
    if not b or b"\x00" in b[:512] or b[:2] in (b"PK", b"MZ") or b[:4] == b"%PDF":
        return None
    b = b[3:] if b[:3] == b"\xef\xbb\xbf" else b
    if b[:5] == b"From ":
        b = b.split(b"\n", 1)[1] if b"\n" in b else b""
    mid, irt, refs, date = (_header(b, n) for n in (b"Message-ID", b"In-Reply-To", b"References", b"Date"))
    if mid is None and _header(b, b"From") is None and _header(b, b"Subject") is None:
        return None
    m = _MSGID.search(mid or b"")
    mid = m.group(0).decode("latin-1") if m else None
    linked = [x.decode("latin-1") for x in _MSGID.findall(refs or b"") + _MSGID.findall(irt or b"")]
    ts = None
    if date:
        from email.utils import parsedate_to_datetime
        try:
            d = parsedate_to_datetime(date.decode("latin-1"))
            if d.tzinfo is None:
                import datetime
                d = d.replace(tzinfo=datetime.timezone.utc)
            ts = d.timestamp()
        except (TypeError, ValueError, IndexError, OverflowError):
            ts = None
    return mid, linked, ts


def threads(names, get_bytes):
    """{"groups", "sorted", "count", "duplicates", "roots"} for the named members, or None (a file unreadable / no
    member is an e-mail)."""
    msgs = []
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        p = _message(bytes(b))
        if p is not None:
            msgs.append((n,) + p)
    if not msgs:
        return None
    key = lambda m: (m[3] is None, m[3] or 0.0, m[0])  # noqa: E731 - Date, undated last, then filename
    msgs.sort(key=key)
    seen, kept, dups = set(), [], []
    for m in msgs:
        if m[1] is not None and m[1] in seen:
            dups.append(m[0])
            continue
        if m[1] is not None:
            seen.add(m[1])
        kept.append(m)
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    node = lambda m: m[1] or "file:" + m[0]  # noqa: E731
    for m in kept:
        a = find(node(m))
        for r in m[2]:
            b = find(r)
            if a != b:
                parent[b] = a
    groups = {}
    for m in kept:
        groups.setdefault(find(node(m)), []).append(m)
    ordered = list(groups.values())          # insertion order = first member's (Date, filename) order
    present = {m[1] for m in kept if m[1]}
    roots = []
    for g in ordered:
        r = [m for m in g if not (set(m[2]) & present - {m[1]})]
        roots.append((r or g)[0][0])
    names_of = [[m[0] for m in g] for g in ordered]
    return {"groups": names_of, "sorted": sorted(sorted(g) for g in names_of), "count": len(ordered),
            "duplicates": sorted(dups), "roots": roots}


def file_list(question):
    """The question's `Files: [...]` names, or None."""
    text = (question or {}).get("question") if isinstance(question, dict) else question
    m = _FILES.search(str(text or ""))
    if not m:
        return None
    try:
        v = json.loads(m.group(1))
    except ValueError:
        return None
    return [str(x) for x in v] if isinstance(v, list) else None


def thread_groups(question, get_bytes, field="thread_groups"):
    """The `field` value (raw: list / int) over the question's Files list read via get_bytes(name), or None."""
    names = file_list(question)
    if not names:
        return None
    t = threads(names, get_bytes)
    return _pick(t, field) if t is not None else None


def _pick(t, field):
    f = field or ""
    if "sorted" in f:
        return t["sorted"]
    if f.endswith("count"):
        return t["count"]
    if "duplicate" in f:
        return t["duplicates"]
    if "root" in f:
        return t["roots"]
    return t["groups"]


def _zip_reader(data):
    """(reader(name) -> bytes|None, [.eml member names in archive order]) over a zip's bytes, or None."""
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(bytes(data)))
        infos = [i for i in z.infolist() if not i.is_dir()]
    except (zipfile.BadZipFile, ValueError, OSError, EOFError, NotImplementedError):
        return None
    by_name = {i.filename: i for i in infos}
    by_base = {}
    for i in infos:
        by_base.setdefault(i.filename.rsplit("/", 1)[-1], i)

    def read(n):
        i = by_name.get(n) or by_base.get(str(n).rsplit("/", 1)[-1])
        if i is None:
            return None
        try:
            return z.read(i)
        except (zipfile.BadZipFile, ValueError, OSError, EOFError, NotImplementedError, RuntimeError):
            return None
    emls = [i.filename for i in infos if i.filename.lower().endswith((".eml", ".msg.txt", ".mail"))]
    return read, emls


def thread_value(data, ctx):
    """synthesis.<thread field> (see the module docstring)."""
    try:
        field = ctx.get("field") or ""
        q = ctx.get("question") or {}
        names = file_list(q)
        read = ctx.get("read") if callable(ctx.get("read")) else None
        if read is None and data is not None and bytes(data[:4]) == b"PK\x03\x04":
            zr = _zip_reader(data)
            if zr is None:
                return None
            read, emls = zr
            names = names or emls
            if not names:
                return "none"
            t = threads(names, read)
            return "none" if t is None else _pick(t, field)
        if read is None or not names:
            return None
        t = threads(names, read)
        return None if t is None else _pick(t, field)
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
