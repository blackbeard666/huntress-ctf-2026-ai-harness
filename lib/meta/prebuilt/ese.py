"""ESE / JET Blue database header fields (SRUDB.dat, WebCacheV01.dat, Windows.edb, ntds.dit, *.edb) -- prebuilt,
SPECULATIVE (never GM-asked).  Format tokens: ese (aliases edb, esedb, jet, srum).

Header = ESE DBFILEHDR on physical page 0 (little-endian; offsets checked against the open-source ESE daedef.hxx
struct as carried by dissect.esedb c_esedb.DBFILEHDR, which matches the libesedb format doc):
  checksum u32 @0, magic 0x89abcdef @4 (bytes ef cd ab 89), ulVersion = format version u32 @8 (0x620),
  attrib = file type u32 @12 (0 database, 1 streaming file), dbtimeDirtied u64 @16,
  signDb (28 B) @24 = {random u32 @24, logtimeCreate @28, szComputerName[16] @36}, dbstate u32 @52,
  lgposConsistent @56, logtimeConsistent @64, logtimeAttach @72, lgposAttach @80, logtimeDetach @88,
  lgposDetach @96, dbid @104, ..., dwMajorVersion @216, dwMinorVersion @220, dwBuildNumber @224, lSPNumber @228,
  ulDaeUpdateMajor = format revision u32 @232, cbPageSize u32 @236 (0 -> 4096 on very old files).
Physical page 1 is the shadow copy of the header (header_shadow_match = page 0 bytes == page 1 bytes).
LOGTIME (8 B) = seconds, minutes, hours, day, month (1-12), year-1900, 2 flag bytes (NOT y/m/d order); modern ESE
writes UTC (fTimeIsUTC) -> rendered 'YYYY-MM-DDTHH:MM:SSZ' (house spelling of lnk/regf/evtx times); all-zero -> "none".
database_state: raw int by default; the name (libesedb/ESE JET_dbstate spelling in snake_case: just_created,
dirty_shutdown, clean_shutdown, being_converted, force_detach) for *_name fields or when the contract lists
non-numeric accepted_values.  file_type likewise: int, name 'database' / 'streaming_file'.
format_version/format_revision bare = esedbinfo style '0x620' / '0x14'; *_u32_hex = struct width '0x00000620'.
page_count = len(data) // page_size, the two header pages included.  Not ESE (wrong magic) -> "none"; ESE magic but
a header too short to hold the field -> None.  The catalog (table names) is NOT read here."""
import re
import struct

from ..spell import Hex

FIELDS = {
    ("ese", "page_size_bytes"): "header_value",
    ("ese", "page_size"): "header_value",
    ("ese", "cb_page_size"): "header_value",
    ("ese", "database_page_size"): "header_value",
    ("ese", "format_version_u32_hex"): "header_value",
    ("ese", "file_format_version_u32_hex"): "header_value",
    ("ese", "version_u32_hex"): "header_value",
    ("ese", "format_version"): "header_value",
    ("ese", "file_format_version"): "header_value",
    ("ese", "format_revision_u32_hex"): "header_value",
    ("ese", "format_revision"): "header_value",
    ("ese", "file_format_revision"): "header_value",
    ("ese", "database_state"): "header_value",
    ("ese", "db_state"): "header_value",
    ("ese", "dbstate"): "header_value",
    ("ese", "state"): "header_value",
    ("ese", "database_state_name"): "header_value",
    ("ese", "db_state_name"): "header_value",
    ("ese", "state_name"): "header_value",
    ("ese", "file_type"): "header_value",
    ("ese", "file_type_name"): "header_value",
    ("ese", "page_count"): "header_value",
    ("ese", "number_of_pages"): "header_value",
    ("ese", "total_pages"): "header_value",
    ("ese", "is_dirty"): "header_value",
    ("ese", "dirty_shutdown"): "header_value",
    ("ese", "is_clean_shutdown"): "header_value",
    ("ese", "clean_shutdown"): "header_value",
    ("ese", "header_shadow_match"): "header_value",
    ("ese", "shadow_header_match"): "header_value",
    ("ese", "signature_u32_hex"): "header_value",
    ("ese", "magic_u32_hex"): "header_value",
    ("ese", "checksum_u32_hex"): "header_value",
    ("ese", "header_checksum_u32_hex"): "header_value",
    ("ese", "database_time"): "header_value",
    ("ese", "database_time_u64_hex"): "header_value",
    ("ese", "db_time"): "header_value",
    ("ese", "database_signature_random_u32_hex"): "header_value",
    ("ese", "creation_time_utc"): "header_value",
    ("ese", "creation_time"): "header_value",
    ("ese", "database_creation_time_utc"): "header_value",
    ("ese", "last_attach_time_utc"): "header_value",
    ("ese", "last_attach_time"): "header_value",
    ("ese", "attach_time_utc"): "header_value",
    ("ese", "last_detach_time_utc"): "header_value",
    ("ese", "last_detach_time"): "header_value",
    ("ese", "detach_time_utc"): "header_value",
    ("ese", "consistent_time_utc"): "header_value",
    ("ese", "last_consistent_time_utc"): "header_value",
    ("ese", "computer_name"): "header_value",
    ("ese", "os_major_version"): "header_value",
    ("ese", "os_minor_version"): "header_value",
    ("ese", "os_build_number"): "header_value",
    ("ese", "os_version"): "header_value",
    ("ese", "windows_version"): "header_value",
    ("ese", "os_service_pack"): "header_value",
    ("edb", "page_size_bytes"): "header_value",
    ("edb", "page_size"): "header_value",
    ("edb", "cb_page_size"): "header_value",
    ("edb", "database_page_size"): "header_value",
    ("edb", "format_version_u32_hex"): "header_value",
    ("edb", "file_format_version_u32_hex"): "header_value",
    ("edb", "version_u32_hex"): "header_value",
    ("edb", "format_version"): "header_value",
    ("edb", "file_format_version"): "header_value",
    ("edb", "format_revision_u32_hex"): "header_value",
    ("edb", "format_revision"): "header_value",
    ("edb", "file_format_revision"): "header_value",
    ("edb", "database_state"): "header_value",
    ("edb", "db_state"): "header_value",
    ("edb", "dbstate"): "header_value",
    ("edb", "state"): "header_value",
    ("edb", "database_state_name"): "header_value",
    ("edb", "db_state_name"): "header_value",
    ("edb", "state_name"): "header_value",
    ("edb", "file_type"): "header_value",
    ("edb", "file_type_name"): "header_value",
    ("edb", "page_count"): "header_value",
    ("edb", "number_of_pages"): "header_value",
    ("edb", "total_pages"): "header_value",
    ("edb", "is_dirty"): "header_value",
    ("edb", "dirty_shutdown"): "header_value",
    ("edb", "is_clean_shutdown"): "header_value",
    ("edb", "clean_shutdown"): "header_value",
    ("edb", "header_shadow_match"): "header_value",
    ("edb", "shadow_header_match"): "header_value",
    ("edb", "signature_u32_hex"): "header_value",
    ("edb", "magic_u32_hex"): "header_value",
    ("edb", "checksum_u32_hex"): "header_value",
    ("edb", "header_checksum_u32_hex"): "header_value",
    ("edb", "database_time"): "header_value",
    ("edb", "database_time_u64_hex"): "header_value",
    ("edb", "db_time"): "header_value",
    ("edb", "database_signature_random_u32_hex"): "header_value",
    ("edb", "creation_time_utc"): "header_value",
    ("edb", "creation_time"): "header_value",
    ("edb", "database_creation_time_utc"): "header_value",
    ("edb", "last_attach_time_utc"): "header_value",
    ("edb", "last_attach_time"): "header_value",
    ("edb", "attach_time_utc"): "header_value",
    ("edb", "last_detach_time_utc"): "header_value",
    ("edb", "last_detach_time"): "header_value",
    ("edb", "detach_time_utc"): "header_value",
    ("edb", "consistent_time_utc"): "header_value",
    ("edb", "last_consistent_time_utc"): "header_value",
    ("edb", "computer_name"): "header_value",
    ("edb", "os_major_version"): "header_value",
    ("edb", "os_minor_version"): "header_value",
    ("edb", "os_build_number"): "header_value",
    ("edb", "os_version"): "header_value",
    ("edb", "windows_version"): "header_value",
    ("edb", "os_service_pack"): "header_value",
    ("esedb", "page_size_bytes"): "header_value",
    ("esedb", "page_size"): "header_value",
    ("esedb", "cb_page_size"): "header_value",
    ("esedb", "database_page_size"): "header_value",
    ("esedb", "format_version_u32_hex"): "header_value",
    ("esedb", "file_format_version_u32_hex"): "header_value",
    ("esedb", "version_u32_hex"): "header_value",
    ("esedb", "format_version"): "header_value",
    ("esedb", "file_format_version"): "header_value",
    ("esedb", "format_revision_u32_hex"): "header_value",
    ("esedb", "format_revision"): "header_value",
    ("esedb", "file_format_revision"): "header_value",
    ("esedb", "database_state"): "header_value",
    ("esedb", "db_state"): "header_value",
    ("esedb", "dbstate"): "header_value",
    ("esedb", "state"): "header_value",
    ("esedb", "database_state_name"): "header_value",
    ("esedb", "db_state_name"): "header_value",
    ("esedb", "state_name"): "header_value",
    ("esedb", "file_type"): "header_value",
    ("esedb", "file_type_name"): "header_value",
    ("esedb", "page_count"): "header_value",
    ("esedb", "number_of_pages"): "header_value",
    ("esedb", "total_pages"): "header_value",
    ("esedb", "is_dirty"): "header_value",
    ("esedb", "dirty_shutdown"): "header_value",
    ("esedb", "is_clean_shutdown"): "header_value",
    ("esedb", "clean_shutdown"): "header_value",
    ("esedb", "header_shadow_match"): "header_value",
    ("esedb", "shadow_header_match"): "header_value",
    ("esedb", "signature_u32_hex"): "header_value",
    ("esedb", "magic_u32_hex"): "header_value",
    ("esedb", "checksum_u32_hex"): "header_value",
    ("esedb", "header_checksum_u32_hex"): "header_value",
    ("esedb", "database_time"): "header_value",
    ("esedb", "database_time_u64_hex"): "header_value",
    ("esedb", "db_time"): "header_value",
    ("esedb", "database_signature_random_u32_hex"): "header_value",
    ("esedb", "creation_time_utc"): "header_value",
    ("esedb", "creation_time"): "header_value",
    ("esedb", "database_creation_time_utc"): "header_value",
    ("esedb", "last_attach_time_utc"): "header_value",
    ("esedb", "last_attach_time"): "header_value",
    ("esedb", "attach_time_utc"): "header_value",
    ("esedb", "last_detach_time_utc"): "header_value",
    ("esedb", "last_detach_time"): "header_value",
    ("esedb", "detach_time_utc"): "header_value",
    ("esedb", "consistent_time_utc"): "header_value",
    ("esedb", "last_consistent_time_utc"): "header_value",
    ("esedb", "computer_name"): "header_value",
    ("esedb", "os_major_version"): "header_value",
    ("esedb", "os_minor_version"): "header_value",
    ("esedb", "os_build_number"): "header_value",
    ("esedb", "os_version"): "header_value",
    ("esedb", "windows_version"): "header_value",
    ("esedb", "os_service_pack"): "header_value",
    ("jet", "page_size_bytes"): "header_value",
    ("jet", "page_size"): "header_value",
    ("jet", "cb_page_size"): "header_value",
    ("jet", "database_page_size"): "header_value",
    ("jet", "format_version_u32_hex"): "header_value",
    ("jet", "file_format_version_u32_hex"): "header_value",
    ("jet", "version_u32_hex"): "header_value",
    ("jet", "format_version"): "header_value",
    ("jet", "file_format_version"): "header_value",
    ("jet", "format_revision_u32_hex"): "header_value",
    ("jet", "format_revision"): "header_value",
    ("jet", "file_format_revision"): "header_value",
    ("jet", "database_state"): "header_value",
    ("jet", "db_state"): "header_value",
    ("jet", "dbstate"): "header_value",
    ("jet", "state"): "header_value",
    ("jet", "database_state_name"): "header_value",
    ("jet", "db_state_name"): "header_value",
    ("jet", "state_name"): "header_value",
    ("jet", "file_type"): "header_value",
    ("jet", "file_type_name"): "header_value",
    ("jet", "page_count"): "header_value",
    ("jet", "number_of_pages"): "header_value",
    ("jet", "total_pages"): "header_value",
    ("jet", "is_dirty"): "header_value",
    ("jet", "dirty_shutdown"): "header_value",
    ("jet", "is_clean_shutdown"): "header_value",
    ("jet", "clean_shutdown"): "header_value",
    ("jet", "header_shadow_match"): "header_value",
    ("jet", "shadow_header_match"): "header_value",
    ("jet", "signature_u32_hex"): "header_value",
    ("jet", "magic_u32_hex"): "header_value",
    ("jet", "checksum_u32_hex"): "header_value",
    ("jet", "header_checksum_u32_hex"): "header_value",
    ("jet", "database_time"): "header_value",
    ("jet", "database_time_u64_hex"): "header_value",
    ("jet", "db_time"): "header_value",
    ("jet", "database_signature_random_u32_hex"): "header_value",
    ("jet", "creation_time_utc"): "header_value",
    ("jet", "creation_time"): "header_value",
    ("jet", "database_creation_time_utc"): "header_value",
    ("jet", "last_attach_time_utc"): "header_value",
    ("jet", "last_attach_time"): "header_value",
    ("jet", "attach_time_utc"): "header_value",
    ("jet", "last_detach_time_utc"): "header_value",
    ("jet", "last_detach_time"): "header_value",
    ("jet", "detach_time_utc"): "header_value",
    ("jet", "consistent_time_utc"): "header_value",
    ("jet", "last_consistent_time_utc"): "header_value",
    ("jet", "computer_name"): "header_value",
    ("jet", "os_major_version"): "header_value",
    ("jet", "os_minor_version"): "header_value",
    ("jet", "os_build_number"): "header_value",
    ("jet", "os_version"): "header_value",
    ("jet", "windows_version"): "header_value",
    ("jet", "os_service_pack"): "header_value",
    ("srum", "page_size_bytes"): "header_value",
    ("srum", "page_size"): "header_value",
    ("srum", "cb_page_size"): "header_value",
    ("srum", "database_page_size"): "header_value",
    ("srum", "format_version_u32_hex"): "header_value",
    ("srum", "file_format_version_u32_hex"): "header_value",
    ("srum", "version_u32_hex"): "header_value",
    ("srum", "format_version"): "header_value",
    ("srum", "file_format_version"): "header_value",
    ("srum", "format_revision_u32_hex"): "header_value",
    ("srum", "format_revision"): "header_value",
    ("srum", "file_format_revision"): "header_value",
    ("srum", "database_state"): "header_value",
    ("srum", "db_state"): "header_value",
    ("srum", "dbstate"): "header_value",
    ("srum", "state"): "header_value",
    ("srum", "database_state_name"): "header_value",
    ("srum", "db_state_name"): "header_value",
    ("srum", "state_name"): "header_value",
    ("srum", "file_type"): "header_value",
    ("srum", "file_type_name"): "header_value",
    ("srum", "page_count"): "header_value",
    ("srum", "number_of_pages"): "header_value",
    ("srum", "total_pages"): "header_value",
    ("srum", "is_dirty"): "header_value",
    ("srum", "dirty_shutdown"): "header_value",
    ("srum", "is_clean_shutdown"): "header_value",
    ("srum", "clean_shutdown"): "header_value",
    ("srum", "header_shadow_match"): "header_value",
    ("srum", "shadow_header_match"): "header_value",
    ("srum", "signature_u32_hex"): "header_value",
    ("srum", "magic_u32_hex"): "header_value",
    ("srum", "checksum_u32_hex"): "header_value",
    ("srum", "header_checksum_u32_hex"): "header_value",
    ("srum", "database_time"): "header_value",
    ("srum", "database_time_u64_hex"): "header_value",
    ("srum", "db_time"): "header_value",
    ("srum", "database_signature_random_u32_hex"): "header_value",
    ("srum", "creation_time_utc"): "header_value",
    ("srum", "creation_time"): "header_value",
    ("srum", "database_creation_time_utc"): "header_value",
    ("srum", "last_attach_time_utc"): "header_value",
    ("srum", "last_attach_time"): "header_value",
    ("srum", "attach_time_utc"): "header_value",
    ("srum", "last_detach_time_utc"): "header_value",
    ("srum", "last_detach_time"): "header_value",
    ("srum", "detach_time_utc"): "header_value",
    ("srum", "consistent_time_utc"): "header_value",
    ("srum", "last_consistent_time_utc"): "header_value",
    ("srum", "computer_name"): "header_value",
    ("srum", "os_major_version"): "header_value",
    ("srum", "os_minor_version"): "header_value",
    ("srum", "os_build_number"): "header_value",
    ("srum", "os_version"): "header_value",
    ("srum", "windows_version"): "header_value",
    ("srum", "os_service_pack"): "header_value",
}

_MAGIC = 0x89ABCDEF
_STATES = {1: "just_created", 2: "dirty_shutdown", 3: "clean_shutdown", 4: "being_converted", 5: "force_detach"}
_FTYPES = {0: "database", 1: "streaming_file"}
_TIMES = {"creation": 28, "database_creation": 28, "last_attach": 72, "attach": 72, "last_detach": 88,
          "detach": 88, "consistent": 64, "last_consistent": 64}


def _hdr(data):
    """(page_size, header bytes) | "none" (not ESE) | None (truncated)."""
    if not isinstance(data, (bytes, bytearray)) or len(data) < 8:
        return "none"
    if struct.unpack_from("<I", data, 4)[0] != _MAGIC:
        return "none"
    if len(data) < 240:
        return None
    ps = struct.unpack_from("<I", data, 236)[0] or 4096
    if ps not in (2048, 4096, 8192, 16384, 32768, 65536):
        return None
    return ps, bytes(data[:ps])


def _logtime(b):
    if len(b) < 6 or not any(b[:6]):
        return "none"
    s, mi, h, d, mo, y = b[:6]
    if not (1 <= mo <= 12 and 1 <= d <= 31 and h < 24 and mi < 60 and s < 61):
        return None
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (y + 1900, mo, d, h, mi, s)


def _wants_name(ctx):
    fmt = ((ctx or {}).get("question") or {}).get("answer_format") or {}
    vals = fmt.get("accepted_values") or fmt.get("values") or []
    return isinstance(vals, (list, tuple)) and any(not str(v).strip().lstrip("-").isdigit() for v in vals)


def header_value(data, ctx):
    """ese.<field>: one value of the DBFILEHDR (see module doc)."""
    try:
        return _header_value(data, ctx)
    except Exception:  # noqa: BLE001 -- defensive: never raise past the extractor
        return None


def _header_value(data, ctx):
    field = (ctx or {}).get("field") or ""
    r = _hdr(data)
    if not isinstance(r, tuple):
        return r
    ps, h = r
    u32 = lambda o: struct.unpack_from("<I", data, o)[0]  # noqa: E731
    if field in ("page_size_bytes", "page_size", "cb_page_size", "database_page_size"):
        return ps
    if field in ("format_version_u32_hex", "file_format_version_u32_hex", "version_u32_hex"):
        return Hex(u32(8), 8)
    if field in ("format_version", "file_format_version"):
        return Hex(u32(8), 0)
    if field == "format_revision_u32_hex":
        return Hex(u32(232), 8)
    if field in ("format_revision", "file_format_revision"):
        return Hex(u32(232), 0)
    if field in ("signature_u32_hex", "magic_u32_hex"):
        return Hex(u32(4), 8)
    if field in ("checksum_u32_hex", "header_checksum_u32_hex"):
        return Hex(u32(0), 8)
    if field == "database_signature_random_u32_hex":
        return Hex(u32(24), 8)
    if field in ("database_time", "db_time"):
        return struct.unpack_from("<Q", data, 16)[0]
    if field == "database_time_u64_hex":
        return Hex(struct.unpack_from("<Q", data, 16)[0], 16)
    st = u32(52)
    if field.endswith("state_name") or (field in ("database_state", "db_state", "dbstate", "state")
                                        and _wants_name(ctx)):
        return _STATES.get(st, "unknown_%d" % st)
    if field in ("database_state", "db_state", "dbstate", "state"):
        return st
    if field in ("is_dirty", "dirty_shutdown"):
        return st == 2
    if field in ("is_clean_shutdown", "clean_shutdown"):
        return st == 3
    ft = u32(12)
    if field == "file_type_name" or (field == "file_type" and _wants_name(ctx)):
        return _FTYPES.get(ft, "unknown_%d" % ft)
    if field == "file_type":
        return ft
    if field in ("page_count", "number_of_pages", "total_pages"):
        return len(data) // ps
    if field in ("header_shadow_match", "shadow_header_match"):
        if len(data) < 2 * ps:
            return "none"
        return bytes(data[:ps]) == bytes(data[ps:2 * ps])
    m = re.match(r"^(.*?)_time(?:_utc)?$", field)
    if m and m.group(1) in _TIMES:
        o = _TIMES[m.group(1)]
        return _logtime(h[o:o + 8])
    if field == "computer_name":
        v = h[36:52].split(b"\0", 1)[0].decode("latin-1").strip()
        return v or "none"
    if field == "os_major_version":
        return u32(216)
    if field == "os_minor_version":
        return u32(220)
    if field == "os_build_number":
        return u32(224)
    if field == "os_service_pack":
        return u32(228)
    if field in ("os_version", "windows_version"):
        return "%d.%d.%d" % (u32(216), u32(220), u32(224)) if u32(216) else "none"
    return None
