"""Legacy Windows event logs (.evt, NT/2000/XP/2003) and Event Viewer "reports" (prebuilt, SPECULATIVE -- never GM-asked
yet; D24 flavor "bundled with reports": a log shipped beside its CSV/XML/text export).

fmt evt / legacy_evt -- ELF_LOGFILE_HEADER (0x30 B, all u32 LE): HeaderSize @0 (0x30), `LfLe` @4, Major/Minor @8/@12
(1/1), StartOffset @16 (oldest record), EndOffset @20 (the EOF record), CurrentRecordNumber @24 (number the NEXT record
will get), OldestRecordNumber @28, MaxSize @32, Flags @36 (1 DIRTY, 2 WRAP, 4 LOGFULL, 8 ARCHIVE), Retention @40,
EndHeaderSize @44. EVENTLOGRECORD: Length @0, `LfLe` @4, RecordNumber @8, TimeGenerated @12 / TimeWritten @16 (unix
seconds -> 'YYYY-MM-DDTHH:MM:SSZ', the house spelling of evtx times), EventID u32 @20 (low 16 bits = the id Event Viewer
shows; event_ids_raw keeps all 32), EventType u16 @24, NumStrings @26, EventCategory @28, StringOffset @36, UserSid
len/off @40/@44, SourceName + Computername UTF-16LE NUL-terminated @56, Length copy at the end. EOF record = 0x28 B:
Length, 11111111 22222222 33333333 44444444, BeginRecord, EndRecord, CurrentRecordNumber, OldestRecordNumber, Length.
The walk starts at StartOffset and is WRAP-AWARE: the record area is circular over [0x30, file end), a record may be
split across the end, 0x00000027 dwords pad the tail. A dirty header (flags & 1) may be stale: next_record_number
prefers the EOF record's CurrentRecordNumber; current_/oldest_record_number are the HEADER values (eof_* = EOF record).
Lists follow the evtx house rules: event_ids = every record in walk order; *_names = distinct, first-seen order;
first_/last_* = first/last walked record; earliest_/latest_* = min/max.

fmt eventlog_report / csv_report / xml_report / report -- an export of a log, detected by content:
  Event Viewer "Save as CSV": header `Level,Date and Time,Source,Event ID,Task Category` (+ unnamed description column,
  multi-line quoted) -- no record ids, no computer; Get-WinEvent | Export-Csv (`#TYPE ...` line optional): `Id`,
  `RecordId`, `ProviderName`, `MachineName`, `TimeCreated`; Get-EventLog | Export-Csv: `EventID`, `Index`, `Source`,
  `MachineName`, `TimeGenerated`; wevtutil qe /f:xml (with or without the /e:Events root): EventID, EventRecordID,
  TimeCreated@SystemTime, Computer, Provider@Name; wevtutil qe /f:text: `Event[N]:` blocks of `Key: value` lines.
  CSV is split by hand (quoted-field state machine; `csv` is not an in-window import). record_ids = sorted ints;
  missing_record_ids = the gaps inside [min, max]; event_ids = file order (exports are usually newest-first);
  first_/earliest_ time = the chronological min, last_/latest_ = max (times without a zone are taken as written,
  US-culture `M/D/YYYY h:mm:ss AM/PM` -> ISO). Not a recognisable export / field the flavor lacks -> "none"."""
import datetime
import re
import struct
import time
import xml.etree.ElementTree as ET

from ..spell import Hex

FIELDS = {
    ("evt", "record_count"): "evt_value",
    ("evt", "number_of_records"): "evt_value",
    ("evt", "num_records"): "evt_value",
    ("evt", "records_count"): "evt_value",
    ("evt", "event_count"): "evt_value",
    ("evt", "total_records"): "evt_value",
    ("evt", "oldest_record_number"): "evt_value",
    ("evt", "header_oldest_record_number"): "evt_value",
    ("evt", "current_record_number"): "evt_value",
    ("evt", "header_current_record_number"): "evt_value",
    ("evt", "next_record_number"): "evt_value",
    ("evt", "eof_current_record_number"): "evt_value",
    ("evt", "eof_oldest_record_number"): "evt_value",
    ("evt", "first_record_number"): "evt_value",
    ("evt", "last_record_number"): "evt_value",
    ("evt", "record_numbers"): "evt_value",
    ("evt", "record_ids"): "evt_value",
    ("evt", "missing_record_numbers"): "evt_value",
    ("evt", "missing_record_ids"): "evt_value",
    ("evt", "is_dirty"): "evt_value",
    ("evt", "dirty"): "evt_value",
    ("evt", "is_wrapped"): "evt_value",
    ("evt", "wrapped"): "evt_value",
    ("evt", "is_log_full"): "evt_value",
    ("evt", "log_full"): "evt_value",
    ("evt", "is_archive"): "evt_value",
    ("evt", "archive"): "evt_value",
    ("evt", "flags_u32_hex"): "evt_value",
    ("evt", "header_flags_u32_hex"): "evt_value",
    ("evt", "flags"): "evt_value",
    ("evt", "header_size"): "evt_value",
    ("evt", "end_header_size"): "evt_value",
    ("evt", "major_version"): "evt_value",
    ("evt", "minor_version"): "evt_value",
    ("evt", "version"): "evt_value",
    ("evt", "start_offset"): "evt_value",
    ("evt", "end_offset"): "evt_value",
    ("evt", "max_size"): "evt_value",
    ("evt", "maximum_size"): "evt_value",
    ("evt", "max_size_bytes"): "evt_value",
    ("evt", "retention"): "evt_value",
    ("evt", "retention_seconds"): "evt_value",
    ("evt", "event_ids"): "evt_value",
    ("evt", "event_ids_raw"): "evt_value",
    ("evt", "distinct_event_ids"): "evt_value",
    ("evt", "unique_event_ids"): "evt_value",
    ("evt", "event_types"): "evt_value",
    ("evt", "event_categories"): "evt_value",
    ("evt", "source_names"): "evt_value",
    ("evt", "distinct_source_names"): "evt_value",
    ("evt", "sources"): "evt_value",
    ("evt", "computer_names"): "evt_value",
    ("evt", "distinct_computer_names"): "evt_value",
    ("evt", "user_sids"): "evt_value",
    ("evt", "first_event_id"): "evt_value",
    ("evt", "last_event_id"): "evt_value",
    ("evt", "first_source_name"): "evt_value",
    ("evt", "last_source_name"): "evt_value",
    ("evt", "first_computer_name"): "evt_value",
    ("evt", "last_computer_name"): "evt_value",
    ("evt", "first_time_generated_utc"): "evt_value",
    ("evt", "last_time_generated_utc"): "evt_value",
    ("evt", "earliest_time_generated_utc"): "evt_value",
    ("evt", "latest_time_generated_utc"): "evt_value",
    ("evt", "first_time_written_utc"): "evt_value",
    ("evt", "last_time_written_utc"): "evt_value",
    ("evt", "earliest_time_written_utc"): "evt_value",
    ("evt", "latest_time_written_utc"): "evt_value",
    ("legacy_evt", "record_count"): "evt_value",
    ("legacy_evt", "number_of_records"): "evt_value",
    ("legacy_evt", "num_records"): "evt_value",
    ("legacy_evt", "records_count"): "evt_value",
    ("legacy_evt", "event_count"): "evt_value",
    ("legacy_evt", "total_records"): "evt_value",
    ("legacy_evt", "oldest_record_number"): "evt_value",
    ("legacy_evt", "header_oldest_record_number"): "evt_value",
    ("legacy_evt", "current_record_number"): "evt_value",
    ("legacy_evt", "header_current_record_number"): "evt_value",
    ("legacy_evt", "next_record_number"): "evt_value",
    ("legacy_evt", "eof_current_record_number"): "evt_value",
    ("legacy_evt", "eof_oldest_record_number"): "evt_value",
    ("legacy_evt", "first_record_number"): "evt_value",
    ("legacy_evt", "last_record_number"): "evt_value",
    ("legacy_evt", "record_numbers"): "evt_value",
    ("legacy_evt", "record_ids"): "evt_value",
    ("legacy_evt", "missing_record_numbers"): "evt_value",
    ("legacy_evt", "missing_record_ids"): "evt_value",
    ("legacy_evt", "is_dirty"): "evt_value",
    ("legacy_evt", "dirty"): "evt_value",
    ("legacy_evt", "is_wrapped"): "evt_value",
    ("legacy_evt", "wrapped"): "evt_value",
    ("legacy_evt", "is_log_full"): "evt_value",
    ("legacy_evt", "log_full"): "evt_value",
    ("legacy_evt", "is_archive"): "evt_value",
    ("legacy_evt", "archive"): "evt_value",
    ("legacy_evt", "flags_u32_hex"): "evt_value",
    ("legacy_evt", "header_flags_u32_hex"): "evt_value",
    ("legacy_evt", "flags"): "evt_value",
    ("legacy_evt", "header_size"): "evt_value",
    ("legacy_evt", "end_header_size"): "evt_value",
    ("legacy_evt", "major_version"): "evt_value",
    ("legacy_evt", "minor_version"): "evt_value",
    ("legacy_evt", "version"): "evt_value",
    ("legacy_evt", "start_offset"): "evt_value",
    ("legacy_evt", "end_offset"): "evt_value",
    ("legacy_evt", "max_size"): "evt_value",
    ("legacy_evt", "maximum_size"): "evt_value",
    ("legacy_evt", "max_size_bytes"): "evt_value",
    ("legacy_evt", "retention"): "evt_value",
    ("legacy_evt", "retention_seconds"): "evt_value",
    ("legacy_evt", "event_ids"): "evt_value",
    ("legacy_evt", "event_ids_raw"): "evt_value",
    ("legacy_evt", "distinct_event_ids"): "evt_value",
    ("legacy_evt", "unique_event_ids"): "evt_value",
    ("legacy_evt", "event_types"): "evt_value",
    ("legacy_evt", "event_categories"): "evt_value",
    ("legacy_evt", "source_names"): "evt_value",
    ("legacy_evt", "distinct_source_names"): "evt_value",
    ("legacy_evt", "sources"): "evt_value",
    ("legacy_evt", "computer_names"): "evt_value",
    ("legacy_evt", "distinct_computer_names"): "evt_value",
    ("legacy_evt", "user_sids"): "evt_value",
    ("legacy_evt", "first_event_id"): "evt_value",
    ("legacy_evt", "last_event_id"): "evt_value",
    ("legacy_evt", "first_source_name"): "evt_value",
    ("legacy_evt", "last_source_name"): "evt_value",
    ("legacy_evt", "first_computer_name"): "evt_value",
    ("legacy_evt", "last_computer_name"): "evt_value",
    ("legacy_evt", "first_time_generated_utc"): "evt_value",
    ("legacy_evt", "last_time_generated_utc"): "evt_value",
    ("legacy_evt", "earliest_time_generated_utc"): "evt_value",
    ("legacy_evt", "latest_time_generated_utc"): "evt_value",
    ("legacy_evt", "first_time_written_utc"): "evt_value",
    ("legacy_evt", "last_time_written_utc"): "evt_value",
    ("legacy_evt", "earliest_time_written_utc"): "evt_value",
    ("legacy_evt", "latest_time_written_utc"): "evt_value",
    ("eventlog_report", "record_count"): "report_value",
    ("eventlog_report", "number_of_records"): "report_value",
    ("eventlog_report", "num_records"): "report_value",
    ("eventlog_report", "records_count"): "report_value",
    ("eventlog_report", "event_count"): "report_value",
    ("eventlog_report", "row_count"): "report_value",
    ("eventlog_report", "total_records"): "report_value",
    ("eventlog_report", "record_ids"): "report_value",
    ("eventlog_report", "event_record_ids"): "report_value",
    ("eventlog_report", "missing_record_ids"): "report_value",
    ("eventlog_report", "missing_record_count"): "report_value",
    ("eventlog_report", "first_record_id"): "report_value",
    ("eventlog_report", "last_record_id"): "report_value",
    ("eventlog_report", "min_record_id"): "report_value",
    ("eventlog_report", "max_record_id"): "report_value",
    ("eventlog_report", "event_ids"): "report_value",
    ("eventlog_report", "distinct_event_ids"): "report_value",
    ("eventlog_report", "unique_event_ids"): "report_value",
    ("eventlog_report", "computer_names"): "report_value",
    ("eventlog_report", "distinct_computer_names"): "report_value",
    ("eventlog_report", "source_names"): "report_value",
    ("eventlog_report", "provider_names"): "report_value",
    ("eventlog_report", "report_format"): "report_value",
    ("eventlog_report", "export_format"): "report_value",
    ("eventlog_report", "format"): "report_value",
    ("eventlog_report", "first_time_utc"): "report_value",
    ("eventlog_report", "last_time_utc"): "report_value",
    ("eventlog_report", "earliest_time_utc"): "report_value",
    ("eventlog_report", "latest_time_utc"): "report_value",
    ("eventlog_report", "first_time_created_utc"): "report_value",
    ("eventlog_report", "last_time_created_utc"): "report_value",
    ("eventlog_report", "first_time_generated_utc"): "report_value",
    ("eventlog_report", "last_time_generated_utc"): "report_value",
    ("eventlog_report", "first_event_time_utc"): "report_value",
    ("eventlog_report", "last_event_time_utc"): "report_value",
    ("eventlog_report", "earliest_time_created_utc"): "report_value",
    ("eventlog_report", "latest_time_created_utc"): "report_value",
    ("csv_report", "record_count"): "report_value",
    ("csv_report", "number_of_records"): "report_value",
    ("csv_report", "num_records"): "report_value",
    ("csv_report", "records_count"): "report_value",
    ("csv_report", "event_count"): "report_value",
    ("csv_report", "row_count"): "report_value",
    ("csv_report", "total_records"): "report_value",
    ("csv_report", "record_ids"): "report_value",
    ("csv_report", "event_record_ids"): "report_value",
    ("csv_report", "missing_record_ids"): "report_value",
    ("csv_report", "missing_record_count"): "report_value",
    ("csv_report", "first_record_id"): "report_value",
    ("csv_report", "last_record_id"): "report_value",
    ("csv_report", "min_record_id"): "report_value",
    ("csv_report", "max_record_id"): "report_value",
    ("csv_report", "event_ids"): "report_value",
    ("csv_report", "distinct_event_ids"): "report_value",
    ("csv_report", "unique_event_ids"): "report_value",
    ("csv_report", "computer_names"): "report_value",
    ("csv_report", "distinct_computer_names"): "report_value",
    ("csv_report", "source_names"): "report_value",
    ("csv_report", "provider_names"): "report_value",
    ("csv_report", "report_format"): "report_value",
    ("csv_report", "export_format"): "report_value",
    ("csv_report", "format"): "report_value",
    ("csv_report", "first_time_utc"): "report_value",
    ("csv_report", "last_time_utc"): "report_value",
    ("csv_report", "earliest_time_utc"): "report_value",
    ("csv_report", "latest_time_utc"): "report_value",
    ("csv_report", "first_time_created_utc"): "report_value",
    ("csv_report", "last_time_created_utc"): "report_value",
    ("csv_report", "first_time_generated_utc"): "report_value",
    ("csv_report", "last_time_generated_utc"): "report_value",
    ("csv_report", "first_event_time_utc"): "report_value",
    ("csv_report", "last_event_time_utc"): "report_value",
    ("csv_report", "earliest_time_created_utc"): "report_value",
    ("csv_report", "latest_time_created_utc"): "report_value",
    ("xml_report", "record_count"): "report_value",
    ("xml_report", "number_of_records"): "report_value",
    ("xml_report", "num_records"): "report_value",
    ("xml_report", "records_count"): "report_value",
    ("xml_report", "event_count"): "report_value",
    ("xml_report", "row_count"): "report_value",
    ("xml_report", "total_records"): "report_value",
    ("xml_report", "record_ids"): "report_value",
    ("xml_report", "event_record_ids"): "report_value",
    ("xml_report", "missing_record_ids"): "report_value",
    ("xml_report", "missing_record_count"): "report_value",
    ("xml_report", "first_record_id"): "report_value",
    ("xml_report", "last_record_id"): "report_value",
    ("xml_report", "min_record_id"): "report_value",
    ("xml_report", "max_record_id"): "report_value",
    ("xml_report", "event_ids"): "report_value",
    ("xml_report", "distinct_event_ids"): "report_value",
    ("xml_report", "unique_event_ids"): "report_value",
    ("xml_report", "computer_names"): "report_value",
    ("xml_report", "distinct_computer_names"): "report_value",
    ("xml_report", "source_names"): "report_value",
    ("xml_report", "provider_names"): "report_value",
    ("xml_report", "report_format"): "report_value",
    ("xml_report", "export_format"): "report_value",
    ("xml_report", "format"): "report_value",
    ("xml_report", "first_time_utc"): "report_value",
    ("xml_report", "last_time_utc"): "report_value",
    ("xml_report", "earliest_time_utc"): "report_value",
    ("xml_report", "latest_time_utc"): "report_value",
    ("xml_report", "first_time_created_utc"): "report_value",
    ("xml_report", "last_time_created_utc"): "report_value",
    ("xml_report", "first_time_generated_utc"): "report_value",
    ("xml_report", "last_time_generated_utc"): "report_value",
    ("xml_report", "first_event_time_utc"): "report_value",
    ("xml_report", "last_event_time_utc"): "report_value",
    ("xml_report", "earliest_time_created_utc"): "report_value",
    ("xml_report", "latest_time_created_utc"): "report_value",
    ("report", "record_count"): "report_value",
    ("report", "number_of_records"): "report_value",
    ("report", "num_records"): "report_value",
    ("report", "records_count"): "report_value",
    ("report", "event_count"): "report_value",
    ("report", "row_count"): "report_value",
    ("report", "total_records"): "report_value",
    ("report", "record_ids"): "report_value",
    ("report", "event_record_ids"): "report_value",
    ("report", "missing_record_ids"): "report_value",
    ("report", "missing_record_count"): "report_value",
    ("report", "first_record_id"): "report_value",
    ("report", "last_record_id"): "report_value",
    ("report", "min_record_id"): "report_value",
    ("report", "max_record_id"): "report_value",
    ("report", "event_ids"): "report_value",
    ("report", "distinct_event_ids"): "report_value",
    ("report", "unique_event_ids"): "report_value",
    ("report", "computer_names"): "report_value",
    ("report", "distinct_computer_names"): "report_value",
    ("report", "source_names"): "report_value",
    ("report", "provider_names"): "report_value",
    ("report", "report_format"): "report_value",
    ("report", "export_format"): "report_value",
    ("report", "format"): "report_value",
    ("report", "first_time_utc"): "report_value",
    ("report", "last_time_utc"): "report_value",
    ("report", "earliest_time_utc"): "report_value",
    ("report", "latest_time_utc"): "report_value",
    ("report", "first_time_created_utc"): "report_value",
    ("report", "last_time_created_utc"): "report_value",
    ("report", "first_time_generated_utc"): "report_value",
    ("report", "last_time_generated_utc"): "report_value",
    ("report", "first_event_time_utc"): "report_value",
    ("report", "last_event_time_utc"): "report_value",
    ("report", "earliest_time_created_utc"): "report_value",
    ("report", "latest_time_created_utc"): "report_value",
}

_SIG = b"LfLe"
_EOF_SIG = bytes.fromhex("11111111222222223333333344444444")


def _utc(secs):
    try:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(secs))
    except (OverflowError, OSError, ValueError):
        return None


def _wstr(b, off):
    """UTF-16LE NUL-terminated string at `off` -> (text, offset after the NUL)."""
    end = off
    while end + 1 < len(b) and b[end:end + 2] != b"\0\0":
        end += 2
    return b[off:end].decode("utf-16-le", "replace"), end + 2


def _sid(b):
    if len(b) < 8 or b[0] != 1:
        return None
    n = b[1]
    if len(b) < 8 + 4 * n:
        return None
    auth = int.from_bytes(b[2:8], "big")
    subs = struct.unpack_from("<%dI" % n, b, 8)
    return "S-1-%d" % auth + "".join("-%d" % x for x in subs)


def _record(rec):
    num, tgen, twr, eid, etype, nstr, cat = struct.unpack_from("<IIIIHHH", rec, 8)
    src, o = _wstr(rec, 56)
    comp, _ = _wstr(rec, o)
    sid_len, sid_off = struct.unpack_from("<II", rec, 40)
    sid = _sid(rec[sid_off:sid_off + sid_len]) if sid_len and sid_off + sid_len <= len(rec) else None
    return {"num": num, "tgen": tgen, "twr": twr, "eid": eid, "type": etype, "cat": cat, "src": src, "comp": comp,
            "sid": sid}


def _walk(b):
    """(header dict, [record dicts], eof dict | None) for a .evt, or None when it is not one."""
    if len(b) < 0x30 or b[4:8] != _SIG or struct.unpack_from("<I", b, 0)[0] != 0x30:
        return None
    hs, _, major, minor, start, end, cur, oldest, maxsize, flags, ret, ehs = struct.unpack_from("<12I", b, 0)
    hdr = {"header_size": hs, "major": major, "minor": minor, "start": start, "end": end, "cur": cur,
           "oldest": oldest, "max": maxsize, "flags": flags, "ret": ret, "ehs": ehs}
    lo, hi = 0x30, len(b)
    if hi - lo < 8:
        return hdr, [], None

    def rd(off, n):   # circular read over the record area [0x30, file end)
        out = bytearray()
        while n > 0:
            if off >= hi:
                off = lo
            k = min(n, hi - off)
            out += b[off:off + k]
            off += k
            n -= k
        return bytes(out)

    def adv(off, n):
        return lo + (off - lo + n) % (hi - lo)

    recs, eof = [], None
    pos = start if lo <= start < hi else lo
    seen = set()
    for _ in range(200000):
        if pos in seen:
            break
        seen.add(pos)
        ln = struct.unpack("<I", rd(pos, 4))[0]
        if ln == 0x27:                       # tail padding before the wrap
            pos = adv(pos, 4)
            continue
        if ln == 0x28 and rd(pos + 4, 16) == _EOF_SIG:
            e = rd(pos, 0x28)
            bg, en, c, o = struct.unpack_from("<IIII", e, 20)
            eof = {"begin": bg, "end": en, "cur": c, "oldest": o}
            break
        if ln < 0x38 or ln > hi - lo or rd(pos + 4, 4) != _SIG:
            break
        rec = rd(pos, ln)
        try:
            recs.append(_record(rec))
        except struct.error:
            break
        pos = adv(pos, ln)
    if not recs and eof is None:             # damaged header offsets: linear carve of whole records
        i = b.find(_SIG, 0x30)
        while i >= 4:
            ln = struct.unpack_from("<I", b, i - 4)[0]
            if 0x38 <= ln <= len(b) - (i - 4) and b[i - 4 + ln - 4:i + ln - 4] == b[i - 4:i]:
                try:
                    recs.append(_record(b[i - 4:i - 4 + ln]))
                except struct.error:
                    pass
                i = b.find(_SIG, i - 4 + ln)
            else:
                i = b.find(_SIG, i + 4)
    return hdr, recs, eof


def _distinct(vals):
    out = []
    for v in vals:
        if v not in (None, "") and v not in out:
            out.append(v)
    return out


def _missing(nums):
    s = sorted(set(nums))
    if not s:
        return []
    have = set(s)
    return [n for n in range(s[0], s[-1] + 1) if n not in have] if s[-1] - s[0] < 1000000 else []


def evt_value(data, ctx):
    if data is None:
        return None
    f = ctx.get("field") or ""
    try:
        w = _walk(bytes(data))
    except Exception:
        return None
    if w is None:
        return "none"
    hdr, recs, eof = w
    fl = hdr["flags"]
    simple = {
        "oldest_record_number": hdr["oldest"], "header_oldest_record_number": hdr["oldest"],
        "current_record_number": hdr["cur"], "header_current_record_number": hdr["cur"],
        "next_record_number": eof["cur"] if eof else hdr["cur"],
        "eof_current_record_number": eof["cur"] if eof else "none",
        "eof_oldest_record_number": eof["oldest"] if eof else "none",
        "is_dirty": bool(fl & 1), "dirty": bool(fl & 1), "is_wrapped": bool(fl & 2), "wrapped": bool(fl & 2),
        "is_log_full": bool(fl & 4), "log_full": bool(fl & 4), "is_archive": bool(fl & 8), "archive": bool(fl & 8),
        "flags_u32_hex": Hex(fl, 8), "header_flags_u32_hex": Hex(fl, 8), "flags": fl,
        "header_size": hdr["header_size"], "end_header_size": hdr["ehs"], "major_version": hdr["major"],
        "minor_version": hdr["minor"], "version": "%d.%d" % (hdr["major"], hdr["minor"]),
        "start_offset": hdr["start"], "end_offset": hdr["end"], "max_size": hdr["max"], "maximum_size": hdr["max"],
        "max_size_bytes": hdr["max"], "retention": hdr["ret"], "retention_seconds": hdr["ret"],
    }
    if f in simple:
        return simple[f]
    if f in ("record_count", "number_of_records", "num_records", "records_count", "event_count", "total_records"):
        return len(recs)
    nums = [r["num"] for r in recs]
    lists = {
        "record_numbers": nums, "record_ids": sorted(nums),
        "missing_record_numbers": _missing(nums), "missing_record_ids": _missing(nums),
        "event_ids": [r["eid"] & 0xFFFF for r in recs], "event_ids_raw": [r["eid"] for r in recs],
        "distinct_event_ids": sorted(set(r["eid"] & 0xFFFF for r in recs)),
        "unique_event_ids": sorted(set(r["eid"] & 0xFFFF for r in recs)),
        "event_types": [r["type"] for r in recs], "event_categories": [r["cat"] for r in recs],
        "source_names": _distinct(r["src"] for r in recs), "distinct_source_names": _distinct(r["src"] for r in recs),
        "sources": _distinct(r["src"] for r in recs), "computer_names": _distinct(r["comp"] for r in recs),
        "distinct_computer_names": _distinct(r["comp"] for r in recs), "user_sids": _distinct(r["sid"] for r in recs),
    }
    if f in lists:
        v = lists[f]
        return v if v or f.startswith("missing_") else "none"
    if not recs:
        return "none"
    key = "tgen" if "time_generated" in f else "twr" if "time_written" in f else None
    if key:
        ts = [r[key] for r in recs]
        v = min(ts) if f.startswith("earliest_") else max(ts) if f.startswith("latest_") else \
            ts[-1] if f.startswith("last_") else ts[0]
        return _utc(v)
    r = recs[-1] if f.startswith("last_") else recs[0]
    if f.endswith("record_number"):
        return r["num"]
    if f.endswith("event_id"):
        return r["eid"] & 0xFFFF
    if f.endswith("source_name"):
        return r["src"] or "none"
    if f.endswith("computer_name"):
        return r["comp"] or "none"
    return None


# ---------------------------------------------------------------- reports (CSV / XML / text exports)

def _text(b):
    if b.startswith(b"\xef\xbb\xbf"):
        return b[3:].decode("utf-8", "replace")
    if b.startswith((b"\xff\xfe", b"\xfe\xff")):
        return b.decode("utf-16", "replace")
    if len(b) > 3 and b[1:2] == b"\0" and b[3:4] == b"\0":
        return b.decode("utf-16-le", "replace")
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


def _csv_rows(t):
    """RFC 4180-ish split: quoted fields may hold commas, doubled quotes and newlines."""
    rows, row, fld, i, n, q = [], [], [], 0, len(t), False
    while i < n:
        c = t[i]
        if q:
            if c == '"':
                if i + 1 < n and t[i + 1] == '"':
                    fld.append('"')
                    i += 1
                else:
                    q = False
            else:
                fld.append(c)
        elif c == '"':
            q = True
        elif c == ",":
            row.append("".join(fld))
            fld = []
        elif c in "\r\n":
            if c == "\r" and i + 1 < n and t[i + 1] == "\n":
                i += 1
            row.append("".join(fld))
            fld = []
            if any(x.strip() for x in row):
                rows.append(row)
            row = []
        else:
            fld.append(c)
        i += 1
    if fld or row:
        row.append("".join(fld))
        if any(x.strip() for x in row):
            rows.append(row)
    return rows


_US = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp][Mm])?")
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})")


def _when(s):
    """A report time cell -> datetime (zone dropped: ISO 'Z' times are UTC, culture times are taken as written)."""
    s = (s or "").strip()
    m = _ISO.match(s)
    if m:
        return datetime.datetime(*map(int, m.groups()))
    m = _US.match(s)
    if m:
        mo, d, y, h, mi, sec, ap = m.groups()
        h = int(h)
        if ap:
            h = h % 12 + (12 if ap.lower() == "pm" else 0)
        return datetime.datetime(int(y), int(mo), int(d), h, int(mi), int(sec or 0))
    return None


def _int(s):
    s = (s or "").strip()
    return int(s) if re.fullmatch(r"\d+", s) else None


_COLS = {"eid": ("event id", "id", "eventid", "event_id"),
         "rid": ("recordid", "record id", "eventrecordid", "index", "record number", "recordnumber"),
         "time": ("timecreated", "date and time", "timegenerated", "date", "time created", "systemtime"),
         "comp": ("machinename", "computer", "computername", "machine name"),
         "src": ("providername", "source", "provider", "provider name")}


def _from_rows(header, body, kind):
    low = [h.strip().lower() for h in header]
    col = {k: next((low.index(n) for n in names if n in low), None) for k, names in _COLS.items()}
    if col["eid"] is None:
        return None
    out = []
    for r in body:
        g = {k: (r[i] if i is not None and i < len(r) else None) for k, i in col.items()}
        eid = _int(g["eid"])
        if eid is None:
            continue
        out.append({"eid": eid, "rid": _int(g["rid"]), "time": g["time"], "comp": (g["comp"] or "").strip(),
                    "src": (g["src"] or "").strip()})
    return kind, out, col["rid"] is not None, col["comp"] is not None


def _report(b):
    """(kind, [event dicts], has_record_ids, has_computer) for an event-log export, or None."""
    t = _text(b).lstrip("﻿")
    if "<Event" in t and "schemas.microsoft.com/win/2004/08/events/event" in t:
        body = re.sub(r"^\s*<\?xml[^>]*\?>", "", t)
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            root = ET.fromstring("<Events>" + body + "</Events>")
        evs = [e for e in root.iter() if e.tag.rsplit("}", 1)[-1] == "Event"]
        out = []
        for e in evs:
            g = {}
            for x in e.iter():
                tag = x.tag.rsplit("}", 1)[-1]
                if tag == "EventID" and "eid" not in g:
                    g["eid"] = _int(x.text)
                elif tag == "EventRecordID":
                    g["rid"] = _int(x.text)
                elif tag == "TimeCreated":
                    g["time"] = x.get("SystemTime")
                elif tag == "Computer":
                    g["comp"] = (x.text or "").strip()
                elif tag == "Provider" and "src" not in g:
                    g["src"] = x.get("EventSourceName") or x.get("Name") or ""
            if g.get("eid") is not None:
                out.append({"eid": g["eid"], "rid": g.get("rid"), "time": g.get("time"), "comp": g.get("comp", ""),
                            "src": g.get("src", "")})
        return ("wevtutil_xml", out, any(o["rid"] is not None for o in out), True) if evs else None
    if re.search(r"(?m)^Event\[\d+\]:", t):
        out = []
        for blk in re.split(r"(?m)^Event\[\d+\]:\s*$", t)[1:]:
            kv = {}
            for ln in blk.splitlines():
                m = re.match(r"^\s+([A-Za-z][A-Za-z ]*?)\s*:\s?(.*)$", ln)
                if m and m.group(1).lower() not in kv:
                    kv[m.group(1).lower()] = m.group(2).strip()
                if m and m.group(1).lower() == "description":
                    break
            out.append({"eid": _int(kv.get("event id")), "rid": _int(kv.get("record id") or kv.get("recordid")),
                        "time": kv.get("date"), "comp": kv.get("computer", ""), "src": kv.get("source", "")})
        return "wevtutil_text", out, any(o["rid"] is not None for o in out), True
    lines = t.splitlines()
    if lines and lines[0].startswith("#TYPE"):
        t = "\n".join(lines[1:])
    rows = _csv_rows(t)
    if len(rows) < 1:
        return None
    hdr = [h.strip().lower() for h in rows[0]]
    kind = "event_viewer_csv" if hdr[:4] == ["level", "date and time", "source", "event id"] else "export_csv"
    return _from_rows(rows[0], rows[1:], kind)


def report_value(data, ctx):
    if data is None:
        return None
    f = ctx.get("field") or ""
    try:
        rep = _report(bytes(data))
    except Exception:
        return None
    if rep is None:
        return "none"
    kind, evs, has_rid, has_comp = rep
    if f in ("report_format", "export_format", "format"):
        return kind
    if f in ("record_count", "number_of_records", "num_records", "records_count", "event_count", "row_count",
             "total_records"):
        return len(evs)
    if not evs:
        return "none"
    if f == "event_ids":
        return [e["eid"] for e in evs]
    if f in ("distinct_event_ids", "unique_event_ids"):
        return sorted(set(e["eid"] for e in evs if e["eid"] is not None))
    if f in ("computer_names", "distinct_computer_names"):
        return _distinct(e["comp"] for e in evs) or "none"
    if f in ("source_names", "provider_names"):
        return _distinct(e["src"] for e in evs) or "none"
    if "record_id" in f or f == "missing_record_count":
        rids = [e["rid"] for e in evs if e["rid"] is not None]
        if not has_rid or not rids:
            return "none"
        if f in ("record_ids", "event_record_ids"):
            return sorted(rids)
        if f == "missing_record_ids":
            return _missing(rids)
        if f == "missing_record_count":
            return len(_missing(rids))
        return min(rids) if f.startswith(("first_", "min_")) else max(rids)
    if "time" in f:
        ts = [w for w in (_when(e["time"]) for e in evs) if w is not None]
        if not ts:
            return "none"
        v = max(ts) if f.startswith(("last_", "latest_")) else min(ts)
        return v.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None
