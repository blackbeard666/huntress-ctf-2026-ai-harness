"""ISO 9660 (+ Joliet / UDF bridge detection) volume-descriptor fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Raw ECMA-119 parse, no library: volume descriptors start at sector 16 (2048-byte sectors, byte 32768), each = type u8
@0, "CD001" @1, version @6. Primary VD (type 1): system_id @8 (a-chars 32), volume_id @40 (d-chars 32),
volume_space_size @80 (both-endian u32, LE half read), volume_set_size @120 / volume_sequence_number @124 (u16),
logical_block_size @128 (u16), path_table_size @132, root directory record @156 (34 bytes: extent LBA @2, data length
@10), volume_set_id @190 (128), publisher_id @318 (128), data_preparer_id @446 (128), application_id @574 (128),
creation / modification / expiration / effective dates @813 / @830 / @847 / @864 (17-byte dec-datetime: 16 ASCII digits
YYYYMMDDHHMMSScc + int8 GMT offset in 15-minute units). Text ids are space-padded: trimmed; empty -> "none".
Dates: the *_utc rendering applies the stored GMT offset and prints ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' (same spelling as
gzip/lnk *_utc); an all-zero / unset date ("0000..." digits) -> "none".
joliet_present = a Supplementary VD (type 2) whose escape sequences @88 are %/@, %/C or %/E (UCS-2 levels 1-3).
udf_present = a Volume Recognition Sequence entry "BEA01" / "NSR02" / "NSR03" in the sectors after the VD set.
root_member_names = the root directory records in stored order (ISO sort order), names exactly as stored ("README.TXT;1"
keeps its ;1 version, directories have none), "." / ".." (0x00 / 0x01) skipped -- the primary (8.3) tree, not Joliet.
No CD001 at sector 16 -> "none"."""
import datetime
import struct

FIELDS = {
    ("iso", "system_id"): "iso_value",
    ("iso", "pvd_system_id"): "iso_value",
    ("iso", "volume_id"): "iso_value",
    ("iso", "pvd_volume_id"): "iso_value",
    ("iso", "volume_label"): "iso_value",
    ("iso", "volume_set_id"): "iso_value",
    ("iso", "pvd_volume_set_id"): "iso_value",
    ("iso", "publisher_id"): "iso_value",
    ("iso", "pvd_publisher_id"): "iso_value",
    ("iso", "data_preparer_id"): "iso_value",
    ("iso", "pvd_data_preparer_id"): "iso_value",
    ("iso", "application_id"): "iso_value",
    ("iso", "pvd_application_id"): "iso_value",
    ("iso", "volume_creation_date_utc"): "iso_value",
    ("iso", "volume_creation_date"): "iso_value",
    ("iso", "pvd_volume_creation_date_utc"): "iso_value",
    ("iso", "volume_creation_time_utc"): "iso_value",
    ("iso", "creation_date_utc"): "iso_value",
    ("iso", "volume_modification_date_utc"): "iso_value",
    ("iso", "volume_modification_date"): "iso_value",
    ("iso", "pvd_volume_modification_date_utc"): "iso_value",
    ("iso", "modification_date_utc"): "iso_value",
    ("iso", "volume_space_size"): "iso_value",
    ("iso", "pvd_volume_space_size"): "iso_value",
    ("iso", "volume_space_size_blocks"): "iso_value",
    ("iso", "logical_block_size"): "iso_value",
    ("iso", "pvd_logical_block_size"): "iso_value",
    ("iso", "logical_block_size_bytes"): "iso_value",
    ("iso", "volume_size_bytes"): "iso_value",
    ("iso", "joliet_present"): "iso_value",
    ("iso", "has_joliet"): "iso_value",
    ("iso", "is_joliet"): "iso_value",
    ("iso", "udf_present"): "iso_value",
    ("iso", "has_udf"): "iso_value",
    ("iso", "is_udf"): "iso_value",
    ("iso", "root_member_names"): "iso_value",
    ("iso", "root_directory_names"): "iso_value",
    ("iso", "root_entry_names"): "iso_value",
    ("iso", "root_file_names"): "iso_value",
    ("iso", "member_names"): "iso_value",
    ("iso", "volume_descriptor_types"): "iso_value",
}

_SEC = 2048
_TEXT = {"system_id": (8, 32), "volume_id": (40, 32), "volume_label": (40, 32), "volume_set_id": (190, 128),
         "publisher_id": (318, 128), "data_preparer_id": (446, 128), "application_id": (574, 128)}


def _dec_datetime(b):
    """17-byte ECMA-119 8.4.26.1 dec-datetime -> ISO-8601 UTC text, or None when unset/garbage."""
    if len(b) != 17:
        return None
    digits = bytes(b[:16]).decode("latin-1")
    if not digits.isdigit() or int(digits[:4]) == 0:
        return None
    off = struct.unpack("b", b[16:17])[0]
    try:
        dt = datetime.datetime(int(digits[0:4]), int(digits[4:6]), int(digits[6:8]), int(digits[8:10]),
                               int(digits[10:12]), int(digits[12:14]))
    except ValueError:
        return None
    return (dt - datetime.timedelta(minutes=15 * off)).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(b):
    """{"pvd": bytes, "types": [..], "joliet": bool, "udf": bool} or None (no CD001 at sector 16)."""
    if not b or len(b) < 17 * _SEC or bytes(b[16 * _SEC + 1:16 * _SEC + 6]) != b"CD001":
        return None
    pvd, types, joliet, udf = None, [], False, False
    sec, term = 16, False
    while (sec + 1) * _SEC <= len(b) and sec < 16 + 64:
        d = bytes(b[sec * _SEC:(sec + 1) * _SEC])
        ident = d[1:6]
        if not term and ident == b"CD001":
            types.append(d[0])
            if d[0] == 1 and pvd is None:
                pvd = d
            elif d[0] == 2 and d[88:91] in (b"%/@", b"%/C", b"%/E"):
                joliet = True
            elif d[0] == 255:
                term = True
        elif ident in (b"BEA01", b"NSR02", b"NSR03", b"TEA01", b"BOOT2", b"CDW02"):
            if ident in (b"BEA01", b"NSR02", b"NSR03"):
                udf = True
        elif term:
            break
        sec += 1
    if pvd is None:
        return None
    return {"pvd": pvd, "types": types, "joliet": joliet, "udf": udf}


def _root_names(b, pvd):
    rec = pvd[156:190]
    lba, size = struct.unpack_from("<I", rec, 2)[0], struct.unpack_from("<I", rec, 10)[0]
    bs = struct.unpack_from("<H", pvd, 128)[0] or _SEC
    start = lba * bs
    if start <= 0 or start >= len(b):
        return None
    data = bytes(b[start:start + min(size, 1 << 20)])
    out, p = [], 0
    while p < len(data):
        ln = data[p]
        if ln == 0:   # records never straddle a sector: skip to the next one
            p = (p // _SEC + 1) * _SEC
            continue
        if ln < 34 or p + ln > len(data):
            break
        nl = data[p + 32]
        name = data[p + 33:p + 33 + nl]
        if name not in (b"\0", b"\1"):
            out.append(name.decode("latin-1"))
        p += ln
    return out


def iso_value(data, ctx):
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- defensive: a hostile member never raises past the extractor
        return None


def _value(data, f):
    if data is None:
        return None
    iso = parse_iso(data)
    if iso is None:
        return "none"
    pvd = iso["pvd"]
    g = f[4:] if f.startswith("pvd_") else f
    if g in _TEXT:
        o, n = _TEXT[g]
        s = pvd[o:o + n].decode("latin-1").strip(" \0")
        return s or "none"
    if "creation_" in g or "modification_" in g:
        o = 813 if "creation_" in g else 830
        return _dec_datetime(pvd[o:o + 17]) or "none"
    bs = struct.unpack_from("<H", pvd, 128)[0]
    vss = struct.unpack_from("<I", pvd, 80)[0]
    if g.startswith("volume_space_size"):
        return vss
    if g == "volume_size_bytes":
        return vss * bs
    if g.startswith("logical_block_size"):
        return bs
    if "joliet" in g:
        return iso["joliet"]
    if "udf" in g:
        return iso["udf"]
    if "names" in g:
        names = _root_names(data, pvd)
        return "none" if names is None else names
    if g == "volume_descriptor_types":
        return iso["types"]
    return None
