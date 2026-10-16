"""Windows Recycle Bin $I index file fields (prebuilt, SPECULATIVE -- never GM-asked yet).

$I<random>.<ext> (Vista+, sits beside its $R twin in C:\\$Recycle.Bin\\<SID>\\), little-endian, no magic beyond the
version: header/version u64 @0 (1 = Vista/7/8, 2 = Win10+), original file size u64 @8 (bytes; for a folder the total of
its contents), deletion time FILETIME u64 @16. v1: original path = 260 WCHARs (520 B) UTF-16LE @24, NUL-padded (file is
544 B). v2: path length u32 @24 in WCHARs INCLUDING the terminating NUL, path UTF-16LE @28.
Times: FILETIME (100 ns since 1601-01-01 UTC) -> ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ' (sub-second part dropped, same
spelling as lnk.*_time / regf.*_time); zero FILETIME -> "none". format_version -> the u64 as int ("1"/"2").
original_size -> int bytes. original_path -> the stored path verbatim up to the first NUL.
Decoys: header not 1/2 (an XP INFO2 file, a $R data file renamed $I, anything else) -> "none"; a v1/v2 header whose
body is truncated -> None. Both fmt spellings `recycle` and `recyclebin` are registered."""
import datetime
import struct

_ALIASES = {
    "original_path": "path", "original_file_path": "path", "original_filename": "path", "original_file_name": "path",
    "original_name": "path", "file_name": "path", "filename": "path", "file_path": "path", "path": "path",
    "deleted_path": "path",
    "deleted_time_utc": "time", "deleted_time": "time", "deletion_time": "time", "deletion_time_utc": "time",
    "deleted_timestamp": "time", "deletion_timestamp": "time", "deleted_at": "time", "deletion_date": "time",
    "original_size": "size", "original_file_size": "size", "file_size": "size", "file_size_bytes": "size",
    "original_size_bytes": "size", "size": "size", "size_bytes": "size", "deleted_size": "size",
    "format_version": "version", "version": "version", "header_version": "version", "header": "version",
    "file_version": "version",
}

FIELDS = {
    ("recycle", "original_path"): "index_value",
    ("recycle", "original_file_path"): "index_value",
    ("recycle", "original_filename"): "index_value",
    ("recycle", "original_file_name"): "index_value",
    ("recycle", "original_name"): "index_value",
    ("recycle", "file_name"): "index_value",
    ("recycle", "filename"): "index_value",
    ("recycle", "file_path"): "index_value",
    ("recycle", "path"): "index_value",
    ("recycle", "deleted_path"): "index_value",
    ("recycle", "deleted_time_utc"): "index_value",
    ("recycle", "deleted_time"): "index_value",
    ("recycle", "deletion_time"): "index_value",
    ("recycle", "deletion_time_utc"): "index_value",
    ("recycle", "deleted_timestamp"): "index_value",
    ("recycle", "deletion_timestamp"): "index_value",
    ("recycle", "deleted_at"): "index_value",
    ("recycle", "deletion_date"): "index_value",
    ("recycle", "original_size"): "index_value",
    ("recycle", "original_file_size"): "index_value",
    ("recycle", "file_size"): "index_value",
    ("recycle", "file_size_bytes"): "index_value",
    ("recycle", "original_size_bytes"): "index_value",
    ("recycle", "size"): "index_value",
    ("recycle", "size_bytes"): "index_value",
    ("recycle", "deleted_size"): "index_value",
    ("recycle", "format_version"): "index_value",
    ("recycle", "version"): "index_value",
    ("recycle", "header_version"): "index_value",
    ("recycle", "header"): "index_value",
    ("recycle", "file_version"): "index_value",
    ("recyclebin", "original_path"): "index_value",
    ("recyclebin", "original_file_path"): "index_value",
    ("recyclebin", "original_filename"): "index_value",
    ("recyclebin", "original_file_name"): "index_value",
    ("recyclebin", "original_name"): "index_value",
    ("recyclebin", "file_name"): "index_value",
    ("recyclebin", "filename"): "index_value",
    ("recyclebin", "file_path"): "index_value",
    ("recyclebin", "path"): "index_value",
    ("recyclebin", "deleted_path"): "index_value",
    ("recyclebin", "deleted_time_utc"): "index_value",
    ("recyclebin", "deleted_time"): "index_value",
    ("recyclebin", "deletion_time"): "index_value",
    ("recyclebin", "deletion_time_utc"): "index_value",
    ("recyclebin", "deleted_timestamp"): "index_value",
    ("recyclebin", "deletion_timestamp"): "index_value",
    ("recyclebin", "deleted_at"): "index_value",
    ("recyclebin", "deletion_date"): "index_value",
    ("recyclebin", "original_size"): "index_value",
    ("recyclebin", "original_file_size"): "index_value",
    ("recyclebin", "file_size"): "index_value",
    ("recyclebin", "file_size_bytes"): "index_value",
    ("recyclebin", "original_size_bytes"): "index_value",
    ("recyclebin", "size"): "index_value",
    ("recyclebin", "size_bytes"): "index_value",
    ("recyclebin", "deleted_size"): "index_value",
    ("recyclebin", "format_version"): "index_value",
    ("recyclebin", "version"): "index_value",
    ("recyclebin", "header_version"): "index_value",
    ("recyclebin", "header"): "index_value",
    ("recyclebin", "file_version"): "index_value",
}


def _filetime(v):
    if not v:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=v // 10)
    except (OverflowError, ValueError):
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_index(b):
    """{version, size, time, path} of a $I file; "none" = not a $I (header not 1/2); None = truncated."""
    if not b or len(b) < 24:
        return "none"
    version, size, ft = struct.unpack_from("<QQQ", b, 0)
    if version == 1:
        if len(b) < 24 + 2:
            return None
        raw = bytes(b[24:24 + 520])
    elif version == 2:
        if len(b) < 28:
            return None
        n, = struct.unpack_from("<I", b, 24)
        if not n or 28 + 2 * n > len(b) + 2:     # tolerate a dropped final NUL, nothing more
            return None
        raw = bytes(b[28:28 + 2 * n])
    else:
        return "none"
    raw = raw[:len(raw) & ~1]
    path = raw.decode("utf-16-le", "replace").split("\x00", 1)[0].strip()
    return {"version": version, "size": size, "time": ft, "path": path}


def index_value(data, ctx):
    """recycle.<field>: one value of the $I header (path / deletion time / size / version)."""
    if data is None:
        return None
    try:
        rec = parse_index(data)
    except (struct.error, ValueError):
        return None
    if not isinstance(rec, dict):
        return rec
    key = _ALIASES.get(ctx.get("field") or "")
    if key == "time":
        return _filetime(rec["time"])
    if key == "path":
        return rec["path"] or "none"
    if key in ("size", "version"):
        return rec[key]
    return None
