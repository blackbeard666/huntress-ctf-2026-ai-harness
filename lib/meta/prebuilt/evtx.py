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
Not ElfFile (e.g. a renamed legacy .evt "LfLe") -> "none"; ElfFile but no readable chunk -> None."""
import struct

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
