"""Windows XML Event Log (EVTX) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

ElfFile file header (libevtx spec, all little-endian, 4096-byte block): "ElfFile\\0" signature, first chunk number
u64 @8, last chunk number u64 @16, next record identifier u64 @24, header size u32 @32 (128), minor version u16 @36,
major version u16 @38 (3.1 Vista..8.1, 3.2 Win10+), header block size u16 @40 (4096), number of chunks u16 @42,
file flags u32 @120 (1 dirty, 2 full), CRC32 @124.
ElfChnk (64 KiB, first one at the header block size): "ElfChnk\\0", first event record number u64 @8, last u64 @16,
first event record identifier u64 @24, last u64 @32, header size u32 @40; records ("**\\0\\0") from chunk+0x200 carry
the EventRecordID u64 @8. first_event_record_id = the PHYSICALLY first chunk's @24 (libevtx "identifier"; python-evtx
calls it log_first_record_number) -- in normal logs @8, @24 and the first record's EventRecordID are equal.
Values come from the headers as stored (a dirty header's next_record_id may lag the chunks; the field asks the header).
Not ElfFile (e.g. a renamed legacy .evt "LfLe") -> "none"; ElfFile but no readable chunk -> None.

Record-level fields (BinXML rendered by python-evtx, System block only -- EventData/UserData never read):
record_count = records found by walking EVERY physical ElfChnk from chunk+0x200 ("**\\0\\0", size u32 @4, size copy at
the record's end, stopping at the chunk's free-space offset u32 @48); first_* = the PHYSICALLY first record (in a
normal log also the lowest EventRecordID), last_* = the physically last one. first_event_id = System/EventID text
(Qualifiers NOT folded in: SCM 7036 with Qualifiers=16384 -> "7036"). first_time_created_utc = System/TimeCreated
@SystemTime (a FILETIME) -> 'YYYY-MM-DDTHH:MM:SSZ', sub-second part dropped (house spelling of lnk/regf/recycle times;
Event Viewer would show 7 fraction digits -- the probe alternative). provider_names = distinct Provider @Name in
first-seen order (a JSON list); provider_name/channel/computer_name = the first record's value. ElfFile with no
records -> record_count 0, the rest "none"; a first record python-evtx cannot render -> None."""
import html
import re
import struct
import time

FIELDS = {
    ("evtx", "file_header_chunk_count"): "header_value",
    ("evtx", "chunk_count"): "header_value",
    ("evtx", "number_of_chunks"): "header_value",
    ("evtx", "file_header_number_of_chunks"): "header_value",
    ("evtx", "header_chunk_count"): "header_value",
    ("evtx", "next_record_id"): "header_value",
    ("evtx", "file_header_next_record_id"): "header_value",
    ("evtx", "next_record_identifier"): "header_value",
    ("evtx", "next_record_number"): "header_value",
    ("evtx", "next_event_record_id"): "header_value",
    ("evtx", "major_version"): "header_value",
    ("evtx", "file_header_major_version"): "header_value",
    ("evtx", "minor_version"): "header_value",
    ("evtx", "file_header_minor_version"): "header_value",
    ("evtx", "version"): "header_value",
    ("evtx", "file_header_version"): "header_value",
    ("evtx", "format_version"): "header_value",
    ("evtx", "first_event_record_id"): "chunk_value",
    ("evtx", "first_record_id"): "chunk_value",
    ("evtx", "first_event_record_identifier"): "chunk_value",
    ("evtx", "first_chunk_first_event_record_id"): "chunk_value",
    ("evtx", "chunk_first_event_record_id"): "chunk_value",
    ("evtx", "first_event_record_number"): "chunk_value",
    ("evtx", "record_count"): "record_value",
    ("evtx", "records_count"): "record_value",
    ("evtx", "event_record_count"): "record_value",
    ("evtx", "event_count"): "record_value",
    ("evtx", "number_of_records"): "record_value",
    ("evtx", "number_of_event_records"): "record_value",
    ("evtx", "total_records"): "record_value",
    ("evtx", "total_record_count"): "record_value",
    ("evtx", "num_records"): "record_value",
    ("evtx", "first_event_id"): "record_value",
    ("evtx", "first_record_event_id"): "record_value",
    ("evtx", "first_eventid"): "record_value",
    ("evtx", "last_event_id"): "record_value",
    ("evtx", "last_record_event_id"): "record_value",
    ("evtx", "event_ids"): "record_value",
    ("evtx", "first_time_created_utc"): "record_value",
    ("evtx", "first_time_created"): "record_value",
    ("evtx", "first_record_time_created_utc"): "record_value",
    ("evtx", "first_record_time_created"): "record_value",
    ("evtx", "first_timecreated_utc"): "record_value",
    ("evtx", "first_system_time_utc"): "record_value",
    ("evtx", "first_event_time_utc"): "record_value",
    ("evtx", "last_time_created_utc"): "record_value",
    ("evtx", "last_time_created"): "record_value",
    ("evtx", "provider_names"): "record_value",
    ("evtx", "providers"): "record_value",
    ("evtx", "unique_provider_names"): "record_value",
    ("evtx", "distinct_provider_names"): "record_value",
    ("evtx", "event_provider_names"): "record_value",
    ("evtx", "provider_name"): "record_value",
    ("evtx", "first_provider_name"): "record_value",
    ("evtx", "first_record_provider_name"): "record_value",
    ("evtx", "channel"): "record_value",
    ("evtx", "channel_name"): "record_value",
    ("evtx", "first_channel"): "record_value",
    ("evtx", "event_channel"): "record_value",
    ("evtx", "first_record_channel"): "record_value",
    ("evtx", "computer_name"): "record_value",
    ("evtx", "computer"): "record_value",
    ("evtx", "first_computer_name"): "record_value",
    ("evtx", "first_record_computer"): "record_value",
    ("evtx", "first_record_computer_name"): "record_value",
    ("evtx", "hostname"): "record_value",
}


def file_header(b):
    """ElfFile header as a dict, or None (not EVTX / truncated)."""
    if not b or len(b) < 128 or bytes(b[:8]) != b"ElfFile\x00":
        return None
    (_, first, last, nxt, hsize, minor, major, block, nchunks) = struct.unpack_from("<8sQQQIHHHH", b, 0)
    return {"first_chunk": first, "last_chunk": last, "next_record_id": nxt, "minor": minor, "major": major,
            "block_size": block, "chunk_count": nchunks}


def first_chunk(b, h):
    """(first record number @8, first record identifier @24, first record's EventRecordID or None) of the first
    ElfChnk, or None."""
    off = h["block_size"] if 128 <= h["block_size"] <= len(b) else 4096
    if bytes(b[off:off + 8]) != b"ElfChnk\x00":
        off = bytes(b).find(b"ElfChnk\x00", 128)
        if off < 0:
            return None
    if len(b) < off + 40:
        return None
    num, = struct.unpack_from("<Q", b, off + 8)
    ident, = struct.unpack_from("<Q", b, off + 24)
    rec = None
    if len(b) >= off + 0x200 + 16 and bytes(b[off + 0x200:off + 0x204]) == b"**\x00\x00":
        rec, = struct.unpack_from("<Q", b, off + 0x208)
    return num, ident, rec


def header_value(data, ctx):
    if data is None:
        return None
    try:
        h = file_header(data)
    except Exception:
        return None
    if h is None:
        return "none"
    f = ctx.get("field") or ""
    if "chunk" in f:
        return h["chunk_count"]
    if "next" in f:
        return h["next_record_id"]
    if "major" in f:
        return h["major"]
    if "minor" in f:
        return h["minor"]
    if "version" in f:
        return "%d.%d" % (h["major"], h["minor"])
    return None


def chunk_value(data, ctx):
    if data is None:
        return None
    try:
        h = file_header(data)
        if h is None:
            return "none"
        c = first_chunk(data, h)
    except Exception:
        return None
    if c is None:
        return None
    num, ident, rec = c
    if (ctx.get("field") or "").endswith("_number"):
        return num
    return ident or num or rec


def _records(b):
    """[(chunk offset, record offset)] of every record in every physical ElfChnk, in file order."""
    h = file_header(b)
    off = h["block_size"] if 128 <= h["block_size"] <= len(b) else 4096
    out = []
    while off + 0x200 <= len(b):
        if bytes(b[off:off + 8]) == b"ElfChnk\x00":
            free, = struct.unpack_from("<I", b, off + 48)
            end = min(off + (free if 0x200 < free <= 0x10000 else 0x10000), len(b))
            r = off + 0x200
            while r + 28 <= end and bytes(b[r:r + 4]) == b"**\x00\x00":
                size, = struct.unpack_from("<I", b, r + 4)
                if size < 28 or r + size > end or struct.unpack_from("<I", b, r + size - 4)[0] != size:
                    break
                out.append((off, r))
                r += size
        off += 0x10000
    return out


_SYS = {"provider": re.compile(r'<Provider\b[^>]*?\bName="([^"]*)"'),
        "event_id": re.compile(r"<EventID\b[^>]*>\s*(\d+)\s*</EventID>"),
        "time": re.compile(r'<TimeCreated\b[^>]*?\bSystemTime="(\d{4}-\d\d-\d\d)[ T](\d\d:\d\d:\d\d)'),
        "channel": re.compile(r"<Channel>([^<]*)</Channel>"),
        "computer": re.compile(r"<Computer>([^<]*)</Computer>")}


def _system(xml):
    """{provider, event_id, time, channel, computer} from a rendered record's <System> block (absent -> None)."""
    sysx = xml.split("</System>", 1)[0]
    out = {}
    for k, rx in _SYS.items():
        m = rx.search(sysx)
        if m is None:
            out[k] = None
        elif k == "time":
            out[k] = "%sT%sZ" % m.groups()
        elif k == "event_id":
            out[k] = int(m.group(1))
        else:
            out[k] = html.unescape(m.group(1)).strip()
    return out


def _render(b, recs, idxs, deadline=0.8):
    """[_system dict or None] for recs[i] in idxs (python-evtx; one ChunkHeader per chunk so templates resolve)."""
    from Evtx.Evtx import ChunkHeader, Record
    chunks, out, t0 = {}, [], time.monotonic()
    for i in idxs:
        if time.monotonic() - t0 > deadline:
            raise TimeoutError
        coff, roff = recs[i]
        try:
            ch = chunks.get(coff) or chunks.setdefault(coff, ChunkHeader(b, coff))
            out.append(_system(Record(b, roff, ch).xml()))
        except Exception:
            out.append(None)
    return out


def record_value(data, ctx):
    if data is None:
        return None
    f = ctx.get("field") or ""
    try:
        if file_header(data) is None:
            return "none"
        b = bytes(data)
        recs = _records(b)
        if "count" in f or "number_of" in f or "records" in f:
            return len(recs)
        if not recs:
            return "none"
        whole = f in ("event_ids", "providers") or f.endswith("_names")
        if whole:
            # chunk order matters for template resolution: render every record in file order
            rows = _render(b, recs, range(len(recs)))
            if any(r is None for r in rows):
                return None
            if f == "event_ids":
                return [r["event_id"] for r in rows]
            seen = []
            for r in rows:
                if r["provider"] is not None and r["provider"] not in seen:
                    seen.append(r["provider"])
            return seen or "none"
        idx = len(recs) - 1 if f.startswith("last_") else 0
        # a later record may reference a template defined by an earlier one in its chunk: render the chunk prefix
        first_in_chunk = next(i for i, (c, _) in enumerate(recs) if c == recs[idx][0])
        r = _render(b, recs, range(first_in_chunk, idx + 1))[-1]
    except Exception:
        return None
    if r is None:
        return None
    if "event_id" in f or "eventid" in f:
        k = "event_id"
    elif "time" in f:
        k = "time"
    elif "provider" in f:
        k = "provider"
    elif "channel" in f:
        k = "channel"
    elif "computer" in f or "hostname" in f:
        k = "computer"
    else:
        return None
    v = r.get(k)
    return "none" if v is None or v == "" else v
