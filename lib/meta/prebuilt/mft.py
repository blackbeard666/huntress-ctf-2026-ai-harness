"""NTFS $MFT FILE record fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Input = one FILE record (1024 B) or a small $MFT run of records. Record header (little-endian, libfsntfs / MS
NTFS docs): "FILE" @0, update sequence array offset u16 @4, its count u16 @6 (1 USN + one entry per 512-B stride),
$LogFile LSN u64 @8, sequence number u16 @0x10, hard-link count u16 @0x12, first attribute offset u16 @0x14,
flags u16 @0x16 (0x01 IN_USE, 0x02 DIRECTORY), used size u32 @0x18, allocated size u32 @0x1C, base record ref u64 @0x20,
next attribute id u16 @0x28, record number u32 @0x2C (NTFS 3.1+, usa offset 0x30). FIXUPS FIRST: the last u16 of
every stride must equal the USN and is replaced by the matching USA entry (a torn record still gets its USA entries
written back -- the bytes are answered as stored).
Attributes: type u32, length u32, non-resident u8 @8, name len u8 @9, name off u16 @10; resident: content size u32
@0x10, content off u16 @0x14. $STANDARD_INFORMATION (0x10): created/modified/mft-changed/accessed FILETIMEs @0/8/16/24.
$FILE_NAME (0x30): parent ref u64 @0 (low 48 bits = parent record number, high 16 = parent sequence), created/
modified/mft-changed/accessed FILETIMEs @8/16/24/32, ..., name length (chars) u8 @0x40, namespace u8 @0x41
(0 POSIX, 1 Win32, 2 DOS, 3 Win32&DOS), UTF-16LE name @0x42. The $FN chosen is the long name (Win32 / Win32&DOS /
POSIX) over a DOS 8.3 short name. $DATA (0x80, unnamed): resident_data_hex_16 = its first 16 content bytes as
lowercase hex without 0x (same spelling as file.magic_prefix_hex_N); non-resident or absent -> "none".
Times: FILETIME (100 ns since 1601-01-01 UTC, the stored representation) -> 'YYYY-MM-DDTHH:MM:SSZ' (same spelling as
lnk.*_time / regf.*_time); when the contract's answer_format shows a fractional part, the full 7-digit 100-ns
fraction is kept ('...SS.fffffffZ'). Zero FILETIME -> "none".
timestomp_suspected = the classic $SI-vs-$FN tells: $SI created or modified EARLIER than $FN created, or the $SI
created/modified time has a zero 100-ns fraction while the matching $FN time does not (tools like SetMACE/timestomp
write whole seconds into $SI only).
Several records: the record the question names ("record 42", "entry #42", "inode 42", or a quoted/ending file name),
else the first in-use record that is not a $-metafile, else the first FILE record.
Not a FILE record (e.g. "BAAD", an INDX block, a renamed impostor) -> "none"."""
import datetime
import json
import re
import struct

FIELDS = {
    ("mft", "file_name"): "mft_value",
    ("mft", "fn_file_name"): "mft_value",
    ("mft", "filename"): "mft_value",
    ("mft", "fn_name"): "mft_value",
    ("mft", "name"): "mft_value",
    ("mft", "record_number"): "mft_value",
    ("mft", "mft_record_number"): "mft_value",
    ("mft", "entry_number"): "mft_value",
    ("mft", "mft_entry_number"): "mft_value",
    ("mft", "header_record_number"): "mft_value",
    ("mft", "parent_record_number"): "mft_value",
    ("mft", "fn_parent_record_number"): "mft_value",
    ("mft", "parent_entry_number"): "mft_value",
    ("mft", "parent_mft_record_number"): "mft_value",
    ("mft", "parent_sequence_number"): "mft_value",
    ("mft", "fn_parent_sequence_number"): "mft_value",
    ("mft", "sequence_number"): "mft_value",
    ("mft", "hard_link_count"): "mft_value",
    ("mft", "si_created_utc"): "mft_value",
    ("mft", "si_creation_time_utc"): "mft_value",
    ("mft", "si_created"): "mft_value",
    ("mft", "si_modified_utc"): "mft_value",
    ("mft", "si_modification_time_utc"): "mft_value",
    ("mft", "si_modified"): "mft_value",
    ("mft", "si_mft_modified_utc"): "mft_value",
    ("mft", "si_accessed_utc"): "mft_value",
    ("mft", "fn_created_utc"): "mft_value",
    ("mft", "fn_creation_time_utc"): "mft_value",
    ("mft", "fn_created"): "mft_value",
    ("mft", "fn_modified_utc"): "mft_value",
    ("mft", "fn_modification_time_utc"): "mft_value",
    ("mft", "fn_modified"): "mft_value",
    ("mft", "fn_mft_modified_utc"): "mft_value",
    ("mft", "fn_accessed_utc"): "mft_value",
    ("mft", "timestomp_suspected"): "mft_value",
    ("mft", "timestomped"): "mft_value",
    ("mft", "is_timestomped"): "mft_value",
    ("mft", "timestomping_suspected"): "mft_value",
    ("mft", "is_directory"): "mft_value",
    ("mft", "directory"): "mft_value",
    ("mft", "is_in_use"): "mft_value",
    ("mft", "in_use"): "mft_value",
    ("mft", "flags_u16_hex"): "mft_value",
    ("mft", "header_flags_u16_hex"): "mft_value",
    ("mft", "resident_data_hex_16"): "mft_value",
    ("mft", "data_hex_16"): "mft_value",
    ("mft", "resident_data_hex"): "mft_value",
    ("mft", "resident_data_size"): "mft_value",
    ("mft", "is_resident"): "mft_value",
    ("mft", "data_is_resident"): "mft_value",
}

_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
_SI_KEYS = ("created", "modified", "mft_modified", "accessed")


def _fixup(rec):
    """The record with update-sequence fixups applied (bytearray)."""
    r = bytearray(rec)
    ofs, cnt = struct.unpack_from("<HH", r, 4)
    if cnt < 2 or ofs + 2 * cnt > len(r):
        return r
    stride = len(r) // (cnt - 1)
    if stride < 256 or stride % 2:
        stride = 512
    for i in range(1, cnt):
        end = i * stride
        if end > len(r):
            break
        r[end - 2:end] = r[ofs + 2 * i:ofs + 2 * i + 2]
    return r


def _times(b, off):
    return dict(zip(_SI_KEYS, struct.unpack_from("<4Q", b, off)))


def parse_record(rec):
    """{header + $SI + long-name $FN + $DATA} of one raw FILE record, or None."""
    if len(rec) < 0x38 or rec[:4] != b"FILE":
        return None
    r = _fixup(rec)
    usa_ofs, = struct.unpack_from("<H", r, 4)
    seq, links, a_off, flags, used = struct.unpack_from("<HHHHI", r, 0x10)
    out = {"sequence_number": seq, "hard_link_count": links, "flags": flags,
           "record_number": struct.unpack_from("<I", r, 0x2C)[0] if usa_ofs >= 0x30 else None,
           "si": None, "fns": [], "data": None}
    end = min(len(r), used or len(r))
    while a_off + 16 <= end:
        atype, alen = struct.unpack_from("<II", r, a_off)
        if atype == 0xFFFFFFFF or alen < 16 or a_off + alen > len(r):
            break
        nonres, nlen = r[a_off + 8], r[a_off + 9]
        if not nonres:
            csz, coff = struct.unpack_from("<IH", r, a_off + 0x10)
            c = bytes(r[a_off + coff:a_off + coff + csz])
            if atype == 0x10 and len(c) >= 32 and out["si"] is None:
                out["si"] = _times(c, 0)
            elif atype == 0x30 and len(c) >= 0x42:
                ln, ns = c[0x40], c[0x41]
                ref, = struct.unpack_from("<Q", c, 0)
                fn = _times(c, 8)
                fn.update(parent=ref & 0xFFFFFFFFFFFF, parent_seq=ref >> 48, ns=ns,
                          name=c[0x42:0x42 + 2 * ln].decode("utf-16-le", "replace"))
                out["fns"].append(fn)
            elif atype == 0x80 and nlen == 0 and out["data"] is None:
                out["data"] = c
        elif atype == 0x80 and nlen == 0 and out["data"] is None:
            out["data"] = False                        # non-resident unnamed $DATA
        a_off += alen
    return out


def _fn(p):
    fns = p["fns"]
    return next((f for f in fns if f["ns"] != 2), fns[0] if fns else None)


def _records(b):
    """[(index, parsed)] of every FILE record in a $MFT run (record size from the first header)."""
    if len(b) < 0x38 or b[:4] != b"FILE":
        return []
    size, = struct.unpack_from("<I", b, 0x1C)
    if size not in (1024, 2048, 4096) or size > len(b):
        size = len(b) if len(b) < 1024 else 1024
    out = []
    for i in range(0, len(b) - 0x37, size):
        p = parse_record(b[i:i + size])
        if p:
            out.append((i // size, p))
    return out


def _pick(recs, q):
    if len(recs) == 1:
        return recs[0][1]
    text = str((q or {}).get("question") or "")
    m = re.search(r"(?:record|entry|inode|segment)[\s_#-]*(?:number|no\.?)?[\s_#:-]*(\d+)", text, re.I)
    if m:
        n = int(m.group(1))
        for idx, p in recs:
            if (p["record_number"] if p["record_number"] is not None else idx) == n:
                return p
    for idx, p in recs:
        f = _fn(p)
        if f and f["name"] and re.search(r"(?<![\w.])%s(?![\w])" % re.escape(f["name"]), text) \
                and not f["name"].startswith("$"):
            return p
    for idx, p in recs:
        f = _fn(p)
        if p["flags"] & 1 and f and not f["name"].startswith("$"):
            return p
    return recs[0][1]


def _frac(q):
    af = (q or {}).get("answer_format") or {}
    s = json.dumps(af) if isinstance(af, dict) else str(af)
    return bool(re.search(r"\d{2}:\d{2}:\d{2}\.\d|fraction|sub-?second|100.?ns|7 digits", s, re.I))


def _filetime(v, frac=False):
    if not v:
        return "none"
    try:
        t = _EPOCH + datetime.timedelta(microseconds=v // 10)
    except OverflowError:
        return None
    if frac:
        return t.strftime("%Y-%m-%dT%H:%M:%S") + ".%07dZ" % (v % 10_000_000)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def timestomp_suspected(si, fn):
    if not si or not fn:
        return None
    if si["created"] < fn["created"] or si["modified"] < fn["created"]:
        return True
    for k in ("created", "modified"):
        if si[k] and si[k] % 10_000_000 == 0 and fn[k] % 10_000_000:
            return True
    return False


def _field(field):
    f = re.sub(r"_(utc|iso8601|text|string|value)$", "", field)
    f = f.replace("creation_time", "created").replace("modification_time", "modified")
    return f


def mft_value(data, ctx):
    """mft.<field> of the selected FILE record (see module doc)."""
    if data is None:
        return None
    try:
        recs = _records(bytes(data))
        if not recs:
            return "none"
        p = _pick(recs, ctx.get("question"))
        return _value(p, _field(ctx.get("field") or ""), ctx.get("question"))
    except (struct.error, IndexError, ValueError):
        return None


def _value(p, f, q):
    from ..spell import Hex
    fn = _fn(p)
    if f in ("file_name", "fn_file_name", "filename", "fn_name", "name"):
        return fn["name"] if fn else "none"
    if f in ("record_number", "mft_record_number", "entry_number", "mft_entry_number", "header_record_number"):
        return p["record_number"] if p["record_number"] is not None else "none"
    if f in ("parent_record_number", "fn_parent_record_number", "parent_entry_number", "parent_mft_record_number"):
        return fn["parent"] if fn else "none"
    if f in ("parent_sequence_number", "fn_parent_sequence_number"):
        return fn["parent_seq"] if fn else "none"
    if f in ("sequence_number", "hard_link_count"):
        return p[f]
    m = re.fullmatch(r"(si|fn)_(created|modified|mft_modified|accessed)", f)
    if m:
        src = p["si"] if m.group(1) == "si" else fn
        return _filetime(src[m.group(2)], _frac(q)) if src else "none"
    if f in ("timestomp_suspected", "timestomped", "is_timestomped", "timestomping_suspected"):
        v = timestomp_suspected(p["si"], fn)
        return "none" if v is None else v
    if f in ("is_directory", "directory"):
        return bool(p["flags"] & 2)
    if f in ("is_in_use", "in_use"):
        return bool(p["flags"] & 1)
    if f in ("flags_u16_hex", "header_flags_u16_hex"):
        return Hex(p["flags"], 4)
    d = p["data"]
    if f in ("is_resident", "data_is_resident"):
        return "none" if d is None else d is not False
    if f == "resident_data_size" and d is not None and d is not False:
        return len(d)
    if not d:
        return "none"
    if f in ("resident_data_hex_16", "data_hex_16"):
        return bytes(d[:16])
    if f == "resident_data_hex":
        return bytes(d)
    return None
