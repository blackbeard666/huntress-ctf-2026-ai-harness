"""NTFS change journal $Extend\\$UsnJrnl:$J records (prebuilt, SPECULATIVE -- never GM-asked yet).

$J is a sparse stream: a huge zero prefix (the deallocated part of the journal) and zero padding at the tail of each
4 KiB journal page (records never straddle a page). Walk: at an 8-byte aligned offset a zero u32 RecordLength = a zero
run -> step 8; otherwise validate the header and step RecordLength (8-aligned); garbage -> step 8 and resync.
USN_RECORD_V2 (Major 2): RecordLength u32 @0, Major u16 @4, Minor u16 @6, FileReferenceNumber u64 @8,
  ParentFileReferenceNumber u64 @16, Usn i64 @24, TimeStamp FILETIME @32, Reason u32 @40, SourceInfo u32 @44,
  SecurityId u32 @48, FileAttributes u32 @52, FileNameLength u16 @56, FileNameOffset u16 @58 (= 60), UTF-16LE name.
USN_RECORD_V3 (Major 3): 128-bit file refs @8/@24, Usn @40, TimeStamp @48, Reason @56, ..., name len/offset @0x4C/0x4E.
USN_RECORD_V4 (Major 4): range-tracking record, no name/timestamp: counted, otherwise ignored.

Fields (fmt usn; aliases usnjrnl, usn_journal, j):
  record_count          = walked valid V2/V3/V4 records (dissect.ntfs yields V2 only; identical on a V2 journal).
  first_usn / last_usn  = Usn of the first / last record in STORED order (int).
  file_names            = distinct names, SORTED, compact JSON.   first_file_name / last_file_name = stored order.
  reason_flags_set      = union of Reason bits over all records as sorted `USN_REASON_*` names (JSON).
  deleted_file_names    = sorted distinct names of records with Reason & FILE_DELETE (0x200).
  renamed_pairs         = [[old, new], ...] in stored order: each RENAME_NEW_NAME (0x2000) record paired with the
                          latest RENAME_OLD_NAME (0x1000) record of the same FileReferenceNumber; duplicates dropped.
  first_time_utc / last_time_utc = TimeStamp (FILETIME, 100 ns since 1601 UTC) of the first / last record in stored
                          order, ISO-8601 to the second with `Z` (the GM's *_utc convention elsewhere).
  file_reference_number_hex (+ mft_entry_number, sequence_number, parent_*) of the file the QUESTION names
                          (longest record name found in the question/member text; else the only distinct name);
                          the 64-bit V2 ref = MFT entry (low 48 bits) | sequence (high 16) -> Hex(.., 16).
A buffer with no valid record (wrong format / all zeros) -> "none"."""
import datetime
import re
import struct

from ..spell import Hex

FIELDS = {
    ("usn", "record_count"): "usn_value",
    ("usn", "records_count"): "usn_value",
    ("usn", "number_of_records"): "usn_value",
    ("usn", "entry_count"): "usn_value",
    ("usn", "first_usn"): "usn_value",
    ("usn", "last_usn"): "usn_value",
    ("usn", "file_names"): "usn_value",
    ("usn", "distinct_file_names"): "usn_value",
    ("usn", "unique_file_names"): "usn_value",
    ("usn", "first_file_name"): "usn_value",
    ("usn", "last_file_name"): "usn_value",
    ("usn", "reason_flags_set"): "usn_value",
    ("usn", "reason_flags"): "usn_value",
    ("usn", "reasons"): "usn_value",
    ("usn", "reason_names"): "usn_value",
    ("usn", "deleted_file_names"): "usn_value",
    ("usn", "renamed_pairs"): "usn_value",
    ("usn", "rename_pairs"): "usn_value",
    ("usn", "first_time_utc"): "usn_value",
    ("usn", "last_time_utc"): "usn_value",
    ("usn", "first_timestamp_utc"): "usn_value",
    ("usn", "last_timestamp_utc"): "usn_value",
    ("usn", "earliest_time_utc"): "usn_value",
    ("usn", "latest_time_utc"): "usn_value",
    ("usn", "file_reference_number_hex"): "usn_value",
    ("usn", "file_reference_number_u64_hex"): "usn_value",
    ("usn", "file_reference_hex"): "usn_value",
    ("usn", "mft_entry_number"): "usn_value",
    ("usn", "mft_record_number"): "usn_value",
    ("usn", "entry_number"): "usn_value",
    ("usn", "sequence_number"): "usn_value",
    ("usn", "parent_file_reference_number_hex"): "usn_value",
    ("usn", "parent_mft_entry_number"): "usn_value",
    ("usn", "parent_entry_number"): "usn_value",
    ("usn", "major_versions"): "usn_value",
    ("usn", "record_versions"): "usn_value",
    ("usnjrnl", "record_count"): "usn_value",
    ("usnjrnl", "records_count"): "usn_value",
    ("usnjrnl", "number_of_records"): "usn_value",
    ("usnjrnl", "entry_count"): "usn_value",
    ("usnjrnl", "first_usn"): "usn_value",
    ("usnjrnl", "last_usn"): "usn_value",
    ("usnjrnl", "file_names"): "usn_value",
    ("usnjrnl", "distinct_file_names"): "usn_value",
    ("usnjrnl", "unique_file_names"): "usn_value",
    ("usnjrnl", "first_file_name"): "usn_value",
    ("usnjrnl", "last_file_name"): "usn_value",
    ("usnjrnl", "reason_flags_set"): "usn_value",
    ("usnjrnl", "reason_flags"): "usn_value",
    ("usnjrnl", "reasons"): "usn_value",
    ("usnjrnl", "reason_names"): "usn_value",
    ("usnjrnl", "deleted_file_names"): "usn_value",
    ("usnjrnl", "renamed_pairs"): "usn_value",
    ("usnjrnl", "rename_pairs"): "usn_value",
    ("usnjrnl", "first_time_utc"): "usn_value",
    ("usnjrnl", "last_time_utc"): "usn_value",
    ("usnjrnl", "first_timestamp_utc"): "usn_value",
    ("usnjrnl", "last_timestamp_utc"): "usn_value",
    ("usnjrnl", "earliest_time_utc"): "usn_value",
    ("usnjrnl", "latest_time_utc"): "usn_value",
    ("usnjrnl", "file_reference_number_hex"): "usn_value",
    ("usnjrnl", "file_reference_number_u64_hex"): "usn_value",
    ("usnjrnl", "file_reference_hex"): "usn_value",
    ("usnjrnl", "mft_entry_number"): "usn_value",
    ("usnjrnl", "mft_record_number"): "usn_value",
    ("usnjrnl", "entry_number"): "usn_value",
    ("usnjrnl", "sequence_number"): "usn_value",
    ("usnjrnl", "parent_file_reference_number_hex"): "usn_value",
    ("usnjrnl", "parent_mft_entry_number"): "usn_value",
    ("usnjrnl", "parent_entry_number"): "usn_value",
    ("usnjrnl", "major_versions"): "usn_value",
    ("usnjrnl", "record_versions"): "usn_value",
    ("usn_journal", "record_count"): "usn_value",
    ("usn_journal", "first_usn"): "usn_value",
    ("usn_journal", "last_usn"): "usn_value",
    ("usn_journal", "file_names"): "usn_value",
    ("usn_journal", "first_file_name"): "usn_value",
    ("usn_journal", "reason_flags_set"): "usn_value",
    ("usn_journal", "deleted_file_names"): "usn_value",
    ("usn_journal", "renamed_pairs"): "usn_value",
    ("usn_journal", "first_time_utc"): "usn_value",
    ("usn_journal", "last_time_utc"): "usn_value",
    ("usn_journal", "file_reference_number_hex"): "usn_value",
    ("j", "record_count"): "usn_value",
    ("j", "first_usn"): "usn_value",
    ("j", "last_usn"): "usn_value",
    ("j", "file_names"): "usn_value",
    ("j", "first_file_name"): "usn_value",
    ("j", "reason_flags_set"): "usn_value",
    ("j", "deleted_file_names"): "usn_value",
    ("j", "renamed_pairs"): "usn_value",
    ("j", "first_time_utc"): "usn_value",
    ("j", "last_time_utc"): "usn_value",
    ("j", "file_reference_number_hex"): "usn_value",
}

_REASONS = ((0x00000001, "DATA_OVERWRITE"), (0x00000002, "DATA_EXTEND"), (0x00000004, "DATA_TRUNCATION"),
            (0x00000010, "NAMED_DATA_OVERWRITE"), (0x00000020, "NAMED_DATA_EXTEND"),
            (0x00000040, "NAMED_DATA_TRUNCATION"), (0x00000100, "FILE_CREATE"), (0x00000200, "FILE_DELETE"),
            (0x00000400, "EA_CHANGE"), (0x00000800, "SECURITY_CHANGE"), (0x00001000, "RENAME_OLD_NAME"),
            (0x00002000, "RENAME_NEW_NAME"), (0x00004000, "INDEXABLE_CHANGE"), (0x00008000, "BASIC_INFO_CHANGE"),
            (0x00010000, "HARD_LINK_CHANGE"), (0x00020000, "COMPRESSION_CHANGE"), (0x00040000, "ENCRYPTION_CHANGE"),
            (0x00080000, "OBJECT_ID_CHANGE"), (0x00100000, "REPARSE_POINT_CHANGE"), (0x00200000, "STREAM_CHANGE"),
            (0x00400000, "TRANSACTED_CHANGE"), (0x00800000, "INTEGRITY_CHANGE"),
            (0x01000000, "DESIRED_STORAGE_CLASS_CHANGE"), (0x80000000, "CLOSE"))
_MAX_RECORDS = 500000
_NONZERO = re.compile(rb"[^\0]")


def _iso(ft):
    if not ft:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ft // 10)
    except (OverflowError, ValueError):
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_one(b, o, n):
    """The record at o as a dict, or None if the bytes there are not a valid USN_RECORD_V2/V3/V4."""
    if o + 8 > n:
        return None
    rl, maj, mnr = struct.unpack_from("<IHH", b, o)
    if rl % 8 or o + rl > n:
        return None
    if maj == 2 and mnr == 0 and rl >= 0x40:
        frn, pfrn, usn, ts, reason, src, sec, attr, nl, no = struct.unpack_from("<QQqQIIIIHH", b, o + 8)
        if no < 0x3C:
            return None
    elif maj == 3 and mnr == 0 and rl >= 0x50:
        frn = int.from_bytes(b[o + 8:o + 24], "little")
        pfrn = int.from_bytes(b[o + 24:o + 40], "little")
        usn, ts, reason, src, sec, attr, nl, no = struct.unpack_from("<qQIIIIHH", b, o + 40)
        if no < 0x4C:
            return None
    elif maj == 4 and mnr == 0 and rl >= 0x38:
        frn = int.from_bytes(b[o + 8:o + 24], "little")
        pfrn = int.from_bytes(b[o + 24:o + 40], "little")
        usn, reason = struct.unpack_from("<qI", b, o + 40)
        return {"major": 4, "len": rl, "frn": frn, "pfrn": pfrn, "usn": usn, "ts": None, "reason": reason,
                "name": None}
    else:
        return None
    if nl % 2 or no + nl > rl or usn < 0:
        return None
    try:
        name = b[o + no:o + no + nl].decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    return {"major": maj, "len": rl, "frn": frn, "pfrn": pfrn, "usn": usn, "ts": ts, "reason": reason, "name": name}


def records(b):
    """Every valid record in stored order (zero runs and garbage skipped 8 bytes at a time)."""
    out, n = [], len(b)
    o = 0
    while o + 8 <= n and len(out) < _MAX_RECORDS:
        if b[o:o + 4] == b"\0\0\0\0":
            # fast-forward over the sparse zero run
            m = _NONZERO.search(b, o)
            if m is None:
                break
            o = m.start() & ~7
            if b[o:o + 4] == b"\0\0\0\0":
                o += 8
            continue
        r = _parse_one(b, o, n)
        if r is None:
            o += 8
            continue
        out.append(r)
        o += r["len"]
    return out


def _named(recs, ctx):
    """Records of the file the question / member text names (longest matching name), else of the only name."""
    names = sorted({r["name"] for r in recs if r["name"]}, key=len, reverse=True)
    text = "%s %s" % (ctx.get("question") or "", ctx.get("member") or "")
    for nm in names:
        if re.search(r"(?<![\w.-])" + re.escape(nm) + r"(?![\w-])", text, re.I):
            return [r for r in recs if r["name"] == nm]
    if len(names) == 1:
        return [r for r in recs if r["name"] == names[0]]
    return None


def usn_value(data, ctx):
    if data is None:
        return None
    try:
        recs = records(bytes(data))
    except Exception:  # noqa: BLE001 -- defensive: never raise past the extractor
        return None
    if not recs:
        return "none"
    f = ctx.get("field") or ""
    named = [r for r in recs if r["name"] is not None]
    timed = [r for r in recs if r["ts"] is not None]
    if f in ("record_count", "records_count", "number_of_records", "entry_count"):
        return len(recs)
    if f == "first_usn":
        return recs[0]["usn"]
    if f == "last_usn":
        return recs[-1]["usn"]
    if f in ("file_names", "distinct_file_names", "unique_file_names"):
        return sorted({r["name"] for r in named}) or "none"
    if f == "first_file_name":
        return named[0]["name"] if named else "none"
    if f == "last_file_name":
        return named[-1]["name"] if named else "none"
    if f in ("reason_flags_set", "reason_flags", "reasons", "reason_names"):
        acc = 0
        for r in recs:
            acc |= r["reason"]
        return sorted("USN_REASON_" + nm for bit, nm in _REASONS if acc & bit) or "none"
    if f == "deleted_file_names":
        return sorted({r["name"] for r in named if r["reason"] & 0x200}) or "none"
    if f in ("renamed_pairs", "rename_pairs"):
        old, pairs = {}, []
        for r in named:
            if r["reason"] & 0x1000:
                old[r["frn"]] = r["name"]
            if r["reason"] & 0x2000 and r["frn"] in old:
                p = [old[r["frn"]], r["name"]]
                if p not in pairs:
                    pairs.append(p)
        return pairs or "none"
    if f in ("first_time_utc", "first_timestamp_utc"):
        return _iso(timed[0]["ts"]) if timed else "none"
    if f in ("last_time_utc", "last_timestamp_utc"):
        return _iso(timed[-1]["ts"]) if timed else "none"
    if f in ("earliest_time_utc", "latest_time_utc"):
        ts = [r["ts"] for r in timed if r["ts"]]
        return _iso((min if f.startswith("earliest") else max)(ts)) if ts else "none"
    if f in ("major_versions", "record_versions"):
        return sorted({r["major"] for r in recs})
    sel = _named(recs, ctx)
    if not sel:
        return None
    r = sel[0]
    if f in ("file_reference_number_hex", "file_reference_number_u64_hex", "file_reference_hex"):
        return Hex(r["frn"], 16 if r["major"] == 2 else 32)
    if f == "parent_file_reference_number_hex":
        return Hex(r["pfrn"], 16 if r["major"] == 2 else 32)
    if f in ("mft_entry_number", "mft_record_number", "entry_number"):
        return r["frn"] & 0xFFFFFFFFFFFF
    if f == "sequence_number":
        return (r["frn"] >> 48) & 0xFFFF
    if f in ("parent_mft_entry_number", "parent_entry_number"):
        return r["pfrn"] & 0xFFFFFFFFFFFF
    return None
