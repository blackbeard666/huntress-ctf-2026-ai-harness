"""EVTX integrity / "selectively shortened timeline" fields (prebuilt, SPECULATIVE; D24 flavor: "duplicated, truncated
... Count records accurately and find the selectively shortened timeline"). fmt evtx (+ aliases eventlog,
windows_event_log). All little-endian.

Records come from prebuilt/evtx.py's verified walk (`_records`: every physical ElfChnk at block_size + k*64 KiB,
"**\\0\\0" records from chunk+0x200, size u32 @4 with its copy at the record end, up to the free-space offset @0x30).
Per record: EventRecordID u64 @8, written FILETIME u64 @16 (the record header's own time, NOT BinXML TimeCreated).
- record_ids: every walked EventRecordID ascending, duplicates KEPT (a duplicated record shows twice).
- missing_record_ids / missing_record_count (= record_id_gap_count): ids in [min, max] absent from the walk;
  first_missing_record_id "none" when contiguous. duplicate_record_ids: ids walked more than once.
- header_next_record_id = ElfFile u64 @24; *_matches iff == max walked id + 1.
- walked_chunk_count: 64 KiB slots carrying the ElfChnk magic; empty_chunk_count: of those, chunks with 0 walked
  records; chunk_record_count_list: records per walked chunk in file order (zeros included).
- header_is_dirty = flags@120 & 1, header_is_full = flags & 2, header_crc32_valid: crc32(b[0:120]) == u32 @124.
- chunk_header_crc_valid: crc32(chunk[0:0x78] + chunk[0x80:0x200]) == u32 @0x7C for ALL walked chunks;
  event_records_crc_valid: crc32(chunk[0x200:free]) == u32 @0x34 for ALL walked chunks.
- truncated: len < block_size + header_chunk_count * 64 KiB, or a record whose size runs past EOF.
- Times: FILETIME (100 ns since 1601) -> 'YYYY-MM-DDTHH:MM:SSZ', sub-seconds dropped (house spelling of the evtx/lnk
  times). first/last_written_time_utc = the record with the LOWEST / HIGHEST EventRecordID ("timeline" = id order);
  earliest/latest_* = min / max time; time_span_seconds = latest - earliest in whole (truncated) seconds;
  time_out_of_order_count = records whose time < the previous record's in EventRecordID order.
Not ElfFile -> "none"; ElfFile with no records -> counts/lists 0 / [], id/time fields "none"."""
import collections
import datetime
import struct
import zlib

FIELDS = {
    ("evtx", "record_ids"): "integrity_value",
    ("evtx", "event_record_ids"): "integrity_value",
    ("evtx", "last_record_id"): "integrity_value",
    ("evtx", "last_event_record_id"): "integrity_value",
    ("evtx", "min_record_id"): "integrity_value",
    ("evtx", "max_record_id"): "integrity_value",
    ("evtx", "record_id_gap_count"): "integrity_value",
    ("evtx", "missing_record_ids"): "integrity_value",
    ("evtx", "missing_event_record_ids"): "integrity_value",
    ("evtx", "first_missing_record_id"): "integrity_value",
    ("evtx", "missing_record_count"): "integrity_value",
    ("evtx", "is_contiguous"): "integrity_value",
    ("evtx", "record_ids_contiguous"): "integrity_value",
    ("evtx", "duplicate_record_ids"): "integrity_value",
    ("evtx", "duplicate_record_count"): "integrity_value",
    ("evtx", "unique_record_count"): "integrity_value",
    ("evtx", "header_next_record_id"): "integrity_value",
    ("evtx", "header_next_record_id_matches"): "integrity_value",
    ("evtx", "next_record_id_matches"): "integrity_value",
    ("evtx", "walked_chunk_count"): "integrity_value",
    ("evtx", "empty_chunk_count"): "integrity_value",
    ("evtx", "chunk_record_count_list"): "integrity_value",
    ("evtx", "chunk_record_counts"): "integrity_value",
    ("evtx", "header_is_dirty"): "integrity_value",
    ("evtx", "is_dirty"): "integrity_value",
    ("evtx", "header_is_full"): "integrity_value",
    ("evtx", "is_full"): "integrity_value",
    ("evtx", "header_crc32_valid"): "integrity_value",
    ("evtx", "file_header_crc32_valid"): "integrity_value",
    ("evtx", "chunk_header_crc_valid"): "integrity_value",
    ("evtx", "chunk_header_crc32_valid"): "integrity_value",
    ("evtx", "event_records_crc_valid"): "integrity_value",
    ("evtx", "event_records_crc32_valid"): "integrity_value",
    ("evtx", "truncated"): "integrity_value",
    ("evtx", "is_truncated"): "integrity_value",
    ("evtx", "first_written_time_utc"): "integrity_value",
    ("evtx", "last_written_time_utc"): "integrity_value",
    ("evtx", "earliest_written_time_utc"): "integrity_value",
    ("evtx", "latest_written_time_utc"): "integrity_value",
    ("evtx", "time_span_seconds"): "integrity_value",
    ("evtx", "time_out_of_order_count"): "integrity_value",
    # format aliases a question could use for the same log (first_record_id / header_chunk_count / record_count are
    # evtx.py's under `evtx`; here they are the walked min id / header @42 / walked count)
    ("eventlog", "record_ids"): "integrity_value",
    ("eventlog", "record_count"): "integrity_value",
    ("eventlog", "first_record_id"): "integrity_value",
    ("eventlog", "last_record_id"): "integrity_value",
    ("eventlog", "record_id_gap_count"): "integrity_value",
    ("eventlog", "missing_record_ids"): "integrity_value",
    ("eventlog", "first_missing_record_id"): "integrity_value",
    ("eventlog", "missing_record_count"): "integrity_value",
    ("eventlog", "is_contiguous"): "integrity_value",
    ("eventlog", "duplicate_record_ids"): "integrity_value",
    ("eventlog", "header_next_record_id"): "integrity_value",
    ("eventlog", "header_next_record_id_matches"): "integrity_value",
    ("eventlog", "header_chunk_count"): "integrity_value",
    ("eventlog", "walked_chunk_count"): "integrity_value",
    ("eventlog", "empty_chunk_count"): "integrity_value",
    ("eventlog", "chunk_record_count_list"): "integrity_value",
    ("eventlog", "header_is_dirty"): "integrity_value",
    ("eventlog", "header_is_full"): "integrity_value",
    ("eventlog", "header_crc32_valid"): "integrity_value",
    ("eventlog", "chunk_header_crc_valid"): "integrity_value",
    ("eventlog", "event_records_crc_valid"): "integrity_value",
    ("eventlog", "truncated"): "integrity_value",
    ("eventlog", "first_written_time_utc"): "integrity_value",
    ("eventlog", "last_written_time_utc"): "integrity_value",
    ("eventlog", "time_span_seconds"): "integrity_value",
    ("eventlog", "time_out_of_order_count"): "integrity_value",
    ("windows_event_log", "record_ids"): "integrity_value",
    ("windows_event_log", "record_count"): "integrity_value",
    ("windows_event_log", "first_record_id"): "integrity_value",
    ("windows_event_log", "last_record_id"): "integrity_value",
    ("windows_event_log", "record_id_gap_count"): "integrity_value",
    ("windows_event_log", "missing_record_ids"): "integrity_value",
    ("windows_event_log", "first_missing_record_id"): "integrity_value",
    ("windows_event_log", "missing_record_count"): "integrity_value",
    ("windows_event_log", "is_contiguous"): "integrity_value",
    ("windows_event_log", "duplicate_record_ids"): "integrity_value",
    ("windows_event_log", "header_next_record_id"): "integrity_value",
    ("windows_event_log", "header_next_record_id_matches"): "integrity_value",
    ("windows_event_log", "header_chunk_count"): "integrity_value",
    ("windows_event_log", "walked_chunk_count"): "integrity_value",
    ("windows_event_log", "empty_chunk_count"): "integrity_value",
    ("windows_event_log", "chunk_record_count_list"): "integrity_value",
    ("windows_event_log", "header_is_dirty"): "integrity_value",
    ("windows_event_log", "header_is_full"): "integrity_value",
    ("windows_event_log", "header_crc32_valid"): "integrity_value",
    ("windows_event_log", "chunk_header_crc_valid"): "integrity_value",
    ("windows_event_log", "event_records_crc_valid"): "integrity_value",
    ("windows_event_log", "truncated"): "integrity_value",
    ("windows_event_log", "first_written_time_utc"): "integrity_value",
    ("windows_event_log", "last_written_time_utc"): "integrity_value",
    ("windows_event_log", "time_span_seconds"): "integrity_value",
    ("windows_event_log", "time_out_of_order_count"): "integrity_value",
}

_FT_EPOCH = datetime.datetime(1601, 1, 1)


def _ft_secs(ft):
    """FILETIME -> whole seconds since 1601 (sub-seconds dropped)."""
    return ft // 10_000_000


def _iso(ft):
    try:
        return (_FT_EPOCH + datetime.timedelta(seconds=_ft_secs(ft))).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, ValueError):
        return None


def analyse(b):
    """Integrity facts of an EVTX blob as a dict, or None (not ElfFile)."""
    from .evtx import _records, file_header
    h = file_header(b)
    if h is None:
        return None
    b = bytes(b)
    block = h["block_size"] if 128 <= h["block_size"] <= len(b) else 4096
    flags, crc = struct.unpack_from("<II", b, 120)
    recs = _records(b)
    rows = []                                   # (record id, FILETIME, physical index)
    for i, (_, r) in enumerate(recs):
        rid, ft = struct.unpack_from("<QQ", b, r + 8)
        rows.append((rid, ft, i))
    per_chunk, chunk_hdr_ok, data_ok, truncated = [], True, True, False
    off = block
    while off + 0x200 <= len(b):
        if b[off:off + 8] == b"ElfChnk\x00":
            per_chunk.append(sum(1 for c, _ in recs if c == off))
            ch = b[off:off + 0x200]
            if zlib.crc32(ch[:0x78] + ch[0x80:0x200]) != struct.unpack_from("<I", ch, 0x7C)[0]:
                chunk_hdr_ok = False
            free, dcrc = struct.unpack_from("<II", ch, 0x30)
            free = free if 0x200 <= free <= 0x10000 else 0x10000
            if off + free > len(b) or zlib.crc32(b[off + 0x200:off + free]) != dcrc:
                data_ok = False
            # a record header whose declared size runs past EOF = a cut-off log
            mine = [r for c, r in recs if c == off]
            r = (mine[-1] + struct.unpack_from("<I", b, mine[-1] + 4)[0]) if mine else off + 0x200
            if r + 8 <= len(b) and b[r:r + 4] == b"**\x00\x00" and r + struct.unpack_from("<I", b, r + 4)[0] > len(b):
                truncated = True
        off += 0x10000
    if off < len(b) and b[off:off + 8] == b"ElfChnk\x00":     # a chunk cut inside its own 512-byte header
        truncated = True
    if len(b) < block + h["chunk_count"] * 0x10000:
        truncated = True
    by_id = sorted(rows, key=lambda t: (t[0], t[2]))
    ids = [t[0] for t in by_id]
    uniq = sorted(set(ids))
    missing = sorted(set(range(uniq[0], uniq[-1] + 1)) - set(uniq)) if uniq and uniq[-1] - uniq[0] < 1_000_000 else []
    dups = sorted(i for i, n in collections.Counter(ids).items() if n > 1)
    times = [t[1] for t in by_id]
    ooo = sum(1 for a, c in zip(times, times[1:]) if c < a)
    return {"h": h, "flags": flags, "header_crc_ok": zlib.crc32(b[:120]) == crc, "ids": ids, "uniq": uniq,
            "missing": missing, "dups": dups, "times": times, "ooo": ooo, "per_chunk": per_chunk,
            "chunk_hdr_ok": chunk_hdr_ok, "data_ok": data_ok, "truncated": truncated}


def _value(a, f):
    h, ids, uniq, times = a["h"], a["ids"], a["uniq"], a["times"]
    if f in ("record_ids", "event_record_ids"):
        return ids
    if f == "record_count":
        return len(ids)
    if f == "unique_record_count":
        return len(uniq)
    if f in ("first_record_id", "min_record_id"):
        return uniq[0] if uniq else "none"
    if f in ("last_record_id", "last_event_record_id", "max_record_id"):
        return uniq[-1] if uniq else "none"
    if f in ("record_id_gap_count", "missing_record_count"):
        return len(a["missing"])
    if f in ("missing_record_ids", "missing_event_record_ids"):
        return a["missing"]
    if f == "first_missing_record_id":
        return a["missing"][0] if a["missing"] else "none"
    if f in ("is_contiguous", "record_ids_contiguous"):
        return not a["missing"]
    if f == "duplicate_record_ids":
        return a["dups"]
    if f == "duplicate_record_count":
        return len(ids) - len(uniq)
    if f == "header_next_record_id":
        return h["next_record_id"]
    if f in ("header_next_record_id_matches", "next_record_id_matches"):
        return h["next_record_id"] == uniq[-1] + 1 if uniq else "none"
    if f == "header_chunk_count":
        return h["chunk_count"]
    if f == "walked_chunk_count":
        return len(a["per_chunk"])
    if f == "empty_chunk_count":
        return sum(1 for n in a["per_chunk"] if n == 0)
    if f in ("chunk_record_count_list", "chunk_record_counts"):
        return a["per_chunk"]
    if f in ("header_is_dirty", "is_dirty"):
        return bool(a["flags"] & 1)
    if f in ("header_is_full", "is_full"):
        return bool(a["flags"] & 2)
    if f in ("header_crc32_valid", "file_header_crc32_valid"):
        return a["header_crc_ok"]
    if f in ("chunk_header_crc_valid", "chunk_header_crc32_valid"):
        return a["chunk_hdr_ok"] if a["per_chunk"] else "none"
    if f in ("event_records_crc_valid", "event_records_crc32_valid"):
        return a["data_ok"] if a["per_chunk"] else "none"
    if f in ("truncated", "is_truncated"):
        return a["truncated"]
    if f == "time_out_of_order_count":
        return a["ooo"]
    if not times:
        return "none"
    if f == "first_written_time_utc":
        return _iso(times[0]) or "none"
    if f == "last_written_time_utc":
        return _iso(times[-1]) or "none"
    if f == "earliest_written_time_utc":
        return _iso(min(times)) or "none"
    if f == "latest_written_time_utc":
        return _iso(max(times)) or "none"
    if f == "time_span_seconds":
        return _ft_secs(max(times)) - _ft_secs(min(times))
    return None


def integrity_value(data, ctx):
    if data is None:
        return None
    try:
        a = analyse(data)
        if a is None:
            return "none"
        return _value(a, ctx.get("field") or "")
    except Exception:
        return None
