"""Windows Registry hive (regf) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Base block (libregf spec, little-endian, 4096 bytes): "regf" signature, primary sequence number u32 @4, secondary
sequence number u32 @8 (they differ in a dirty hive), last written time FILETIME u64 @12, major version u32 @20 (1),
minor version u32 @24 (3 NT4..XP, 5 Vista+), file type u32 @28, file format u32 @32, root cell offset u32 @36
(relative to the first hbin at 0x1000), hive bins data size u32 @40, clustering factor u32 @44, file name 64 bytes
UTF-16LE @48 (the last 31 chars of the hive's path, NUL-padded), XOR-32 checksum of bytes 0..507 @508.
Root key = the nk cell at 0x1000 + root cell offset (cell-relative): i32 size, "nk" @4, flags u16 @6 (0x20 COMP_NAME = name
is ASCII/latin-1, else UTF-16LE), FILETIME @8, subkeys u32 @0x18, values u32 @0x28, name len u16 @0x4C, name @0x50.
Times: FILETIME (100 ns since 1601-01-01 UTC) -> ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ' (same spelling as lnk.*_time);
zero FILETIME -> "none". Versions: the u32 as int (major_version "1", minor_version "5"); `version`/`format_version`
-> "major.minor". Values are as stored (no checksum gate: a dirty/edited hive is still answered).
Not "regf" (e.g. a Win9x "CREG" hive renamed .dat) -> "none"; regf with an unreadable root cell -> None."""
import datetime
import struct

FIELDS = {
    ("regf", "primary_sequence_number"): "base_value",
    ("regf", "base_block_primary_sequence_number"): "base_value",
    ("regf", "sequence_number_1"): "base_value",
    ("regf", "primary_sequence"): "base_value",
    ("regf", "secondary_sequence_number"): "base_value",
    ("regf", "base_block_secondary_sequence_number"): "base_value",
    ("regf", "sequence_number_2"): "base_value",
    ("regf", "secondary_sequence"): "base_value",
    ("regf", "last_written_time"): "base_value",
    ("regf", "last_written_time_utc"): "base_value",
    ("regf", "last_written_timestamp"): "base_value",
    ("regf", "base_block_last_written_time"): "base_value",
    ("regf", "last_modification_time"): "base_value",
    ("regf", "hive_file_name"): "base_value",
    ("regf", "file_name"): "base_value",
    ("regf", "base_block_file_name"): "base_value",
    ("regf", "hive_name"): "base_value",
    ("regf", "major_version"): "base_value",
    ("regf", "base_block_major_version"): "base_value",
    ("regf", "format_major_version"): "base_value",
    ("regf", "minor_version"): "base_value",
    ("regf", "base_block_minor_version"): "base_value",
    ("regf", "format_minor_version"): "base_value",
    ("regf", "version"): "base_value",
    ("regf", "format_version"): "base_value",
    ("regf", "hive_version"): "base_value",
    ("regf", "root_key_name"): "root_value",
    ("regf", "root_nk_name"): "root_value",
    ("regf", "root_cell_key_name"): "root_value",
    ("regf", "root_key_last_written_time"): "root_value",
    ("regf", "root_key_subkey_count"): "root_value",
    ("regf", "root_key_number_of_subkeys"): "root_value",
    ("regf", "root_key_value_count"): "root_value",
    ("regf", "root_key_number_of_values"): "root_value",
    ("regf", "root_cell_offset_u32_hex"): "base_value",
}


def _filetime(v):
    if not v:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=v // 10)
    except (OverflowError, ValueError):
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def base_block(b):
    """The regf base block as a dict, or None (not regf / truncated)."""
    if not b or len(b) < 512 or bytes(b[:4]) != b"regf":
        return None
    seq1, seq2, ts, major, minor, ftype, ffmt, root, size, clus = struct.unpack_from("<IIQIIIIIII", b, 4)
    name = bytes(b[48:112]).decode("utf-16-le", "replace").split("\x00", 1)[0].strip()
    return {"seq1": seq1, "seq2": seq2, "ts": ts, "major": major, "minor": minor, "root": root, "name": name}


def root_nk(b, h):
    """(name, last written FILETIME, subkey count, value count) of the root nk cell, or None."""
    off = 0x1000 + h["root"]
    if len(b) < off + 0x50 or bytes(b[off + 4:off + 6]) != b"nk":
        return None
    flags, ts = struct.unpack_from("<HQ", b, off + 6)
    nsub, = struct.unpack_from("<I", b, off + 0x18)
    nval, = struct.unpack_from("<I", b, off + 0x28)
    nlen, = struct.unpack_from("<H", b, off + 0x4C)
    raw = bytes(b[off + 0x50:off + 0x50 + nlen])
    if len(raw) < nlen:
        return None
    name = raw.decode("latin-1") if flags & 0x20 else raw.decode("utf-16-le", "replace")
    return name, ts, nsub, nval


def base_value(data, ctx):
    """regf.<base block field>."""
    if data is None:
        return None
    try:
        h = base_block(data)
        if h is None:
            return "none"
        f = ctx.get("field") or ""
        if "primary" in f or f.endswith("_1"):
            return h["seq1"]
        if "secondary" in f or f.endswith("_2"):
            return h["seq2"]
        if "time" in f:
            return _filetime(h["ts"])
        if "name" in f:
            return h["name"] or "none"
        if "major" in f:
            return h["major"]
        if "minor" in f:
            return h["minor"]
        if f.startswith("root_cell_offset"):
            return h["root"]
        if "version" in f:
            return "%d.%d" % (h["major"], h["minor"])
    except Exception:
        return None
    return None


def root_value(data, ctx):
    """regf.root_key_<field>: from the root nk cell."""
    if data is None:
        return None
    try:
        h = base_block(data)
        if h is None:
            return "none"
        r = root_nk(data, h)
        if r is None:
            return None
        f = ctx.get("field") or ""
        if "time" in f:
            return _filetime(r[1])
        if "subkey" in f:
            return r[2]
        if "value" in f:
            return r[3]
        return r[0]
    except Exception:
        return None
