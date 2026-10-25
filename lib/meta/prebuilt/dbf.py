"""dBase / FoxPro .dbf table header fields (fmt `dbf`, alias `dbase`) -- prebuilt, SPECULATIVE (never asked yet).

Header (little-endian): version byte @0, last update YY @1 (+1900), MM @2, DD @3, record_count u32 @4,
header_size u16 @8, record_size u16 @10; 32-byte field descriptors from @32 until the 0x0D terminator:
name[11] NUL-trimmed, type char @11, length u8 @16, decimals u8 @17. VFP (0x30/0x31/0x32) appends a 263-byte backlink.
No real magic, so the gate is structural: a known version byte, a valid MM/DD, the 0x0D terminator inside header_size
and record_size == 1 (deletion flag) + sum(field lengths). Anything else -> "none".
last_update is the stored date as YYYY-MM-DD (no time is stored). YY: dBase III writers store year-1900 (126 =
2026), VFP stores year%100 (26); like dbfread.expand_year, YY < 80 -> 2000+YY, else 1900+YY. Lists keep descriptor (stored) order.
Fixtures: python `dbf` package writer (db3 / db3+memo / vfp), `dbfread` 2.0.7 reader as oracle."""
import struct

FIELDS = {
    ("dbf", "version"): "dbf_value",
    ("dbf", "version_byte"): "dbf_value",
    ("dbf", "version_u8_hex"): "dbf_value",
    ("dbf", "version_byte_u8_hex"): "dbf_value",
    ("dbf", "file_type_u8_hex"): "dbf_value",
    ("dbf", "version_name"): "dbf_value",
    ("dbf", "file_type"): "dbf_value",
    ("dbf", "file_type_name"): "dbf_value",
    ("dbf", "dbf_version_name"): "dbf_value",
    ("dbf", "has_memo"): "dbf_value",
    ("dbf", "memo_present"): "dbf_value",
    ("dbf", "last_update"): "dbf_value",
    ("dbf", "last_update_date"): "dbf_value",
    ("dbf", "last_updated"): "dbf_value",
    ("dbf", "last_modified"): "dbf_value",
    ("dbf", "last_modified_date"): "dbf_value",
    ("dbf", "record_count"): "dbf_value",
    ("dbf", "num_records"): "dbf_value",
    ("dbf", "number_of_records"): "dbf_value",
    ("dbf", "records_count"): "dbf_value",
    ("dbf", "header_size"): "dbf_value",
    ("dbf", "header_size_bytes"): "dbf_value",
    ("dbf", "header_length"): "dbf_value",
    ("dbf", "header_len"): "dbf_value",
    ("dbf", "record_size"): "dbf_value",
    ("dbf", "record_size_bytes"): "dbf_value",
    ("dbf", "record_length"): "dbf_value",
    ("dbf", "record_len"): "dbf_value",
    ("dbf", "field_count"): "dbf_value",
    ("dbf", "number_of_fields"): "dbf_value",
    ("dbf", "num_fields"): "dbf_value",
    ("dbf", "field_names"): "dbf_value",
    ("dbf", "column_names"): "dbf_value",
    ("dbf", "field_types"): "dbf_value",
    ("dbf", "field_lengths"): "dbf_value",
    ("dbf", "field_decimal_counts"): "dbf_value",
    ("dbf", "language_driver_u8_hex"): "dbf_value",
    ("dbf", "code_page_mark_u8_hex"): "dbf_value",
    ("dbase", "version"): "dbf_value",
    ("dbase", "version_u8_hex"): "dbf_value",
    ("dbase", "version_byte_u8_hex"): "dbf_value",
    ("dbase", "version_name"): "dbf_value",
    ("dbase", "has_memo"): "dbf_value",
    ("dbase", "last_update"): "dbf_value",
    ("dbase", "last_update_date"): "dbf_value",
    ("dbase", "record_count"): "dbf_value",
    ("dbase", "num_records"): "dbf_value",
    ("dbase", "number_of_records"): "dbf_value",
    ("dbase", "header_size"): "dbf_value",
    ("dbase", "header_length"): "dbf_value",
    ("dbase", "record_size"): "dbf_value",
    ("dbase", "record_length"): "dbf_value",
    ("dbase", "field_count"): "dbf_value",
    ("dbase", "field_names"): "dbf_value",
    ("dbase", "field_types"): "dbf_value",
    ("dbase", "field_lengths"): "dbf_value",
}

# Version byte -> name (dBase/xBase file structure tables; the names are our spelling, speculative).
_NAMES = {0x02: "FoxBASE", 0x03: "dBase III", 0x05: "dBase V", 0x07: "dBase III",
          0x30: "Visual FoxPro", 0x31: "Visual FoxPro (autoincrement)", 0x32: "Visual FoxPro (varchar)",
          0x43: "dBase IV SQL table", 0x63: "dBase IV SQL system", 0x83: "dBase III with memo",
          0x87: "dBase III with memo", 0x8B: "dBase IV with memo", 0x8E: "dBase IV with SQL table",
          0xCB: "dBase IV SQL table with memo", 0xF5: "FoxPro 2.x with memo", 0xFB: "FoxBASE"}
_MEMO = {0x83, 0x87, 0x8B, 0x8E, 0xCB, 0xF5}


def parse_dbf(b):
    """Header dict, or None when the bytes are not a structurally valid .dbf."""
    if len(b) < 33:
        return None
    ver, yy, mm, dd = b[0], b[1], b[2], b[3]
    nrec, hsize, rsize = struct.unpack_from("<IHH", b, 4)
    if ver not in _NAMES or not (1 <= mm <= 12 and 1 <= dd <= 31) or hsize < 33 or rsize < 1:
        return None
    fields, off = [], 32
    while True:
        if off >= len(b) or off >= hsize:
            return None
        if b[off] == 0x0D:
            break
        if off + 32 > len(b):
            return None
        d = b[off:off + 32]
        name = d[:11].split(b"\0", 1)[0].decode("latin-1").strip()
        fields.append((name, chr(d[11]), d[16], d[17]))
        off += 32
    if not fields or 1 + sum(f[2] for f in fields) != rsize:
        return None
    if ver not in (0x30, 0x31, 0x32) and off + 1 != hsize and off + 2 != hsize:
        return None
    vfp = ver in (0x30, 0x31, 0x32)
    return {"version": ver, "version_name": _NAMES[ver],
            "has_memo": ver in _MEMO or (vfp and bool(b[28] & 0x02)) or any(f[1] == "M" for f in fields),
            "last_update": "%04d-%02d-%02d" % ((2000 if yy < 80 else 1900) + yy, mm, dd), "record_count": nrec, "header_size": hsize,
            "record_size": rsize, "fields": fields, "lang": b[29]}


def dbf_value(data, ctx):
    if not data:
        return None
    try:
        from ..spell import Hex
        p = parse_dbf(bytes(data))
        if p is None:
            return "none"   # not a .dbf (renamed impostor / wrong structure): the field is absent
        f = (ctx or {}).get("field") or ""
        if f.endswith("_u8_hex"):
            return Hex(p["lang"] if f.startswith(("language", "code_page")) else p["version"], 2)
        if f in ("version", "version_byte"):
            return p["version"]
        if "name" in f and "field" not in f and "column" not in f:
            return p["version_name"]
        if f == "file_type":
            return p["version_name"]
        if f in ("has_memo", "memo_present"):
            return p["has_memo"]
        if f.startswith("last_"):
            return p["last_update"]
        if "record" in f and ("count" in f or "num" in f):
            return p["record_count"]
        if f.startswith("header_"):
            return p["header_size"]
        if f.startswith("record_"):
            return p["record_size"]
        if f in ("field_count", "number_of_fields", "num_fields"):
            return len(p["fields"])
        idx = {"field_names": 0, "column_names": 0, "field_types": 1, "field_lengths": 2,
               "field_decimal_counts": 3}.get(f)
        if idx is not None:
            return [x[idx] for x in p["fields"]]
        return None
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None
