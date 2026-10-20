"""`archive.<field>`: the format-neutral alias for the tar / iso prebuilt modules (prebuilt, SPECULATIVE).

The GM may name the family instead of the container ("Determine archive.member_names ..."). Route by MAGIC, never by
the member's extension: ar ("!<arch>"/"!<thin>" or a fat wrapper of ar slices) -> ar.py; ISO 9660 = "CD001" @0x8001 -> iso.py; tar = a header that tarfile accepts (checksum-verified)
-> tar.py. Field spelling and rendering are exactly those modules' (see their docstrings). Neither -> "none"."""
from . import ar as _ar
from . import iso as _iso
from . import tar as _tar

_TAR = ("ustar_magic", "ustar_version", "tar_format", "member_sizes", "member_sizes_bytes", "member_mtimes_utc",
        "member_mtimes", "member_mtimes_unix", "member_modes_octal", "member_modes", "member_unames", "member_gnames",
        "member_uids", "member_gids", "typeflags", "member_typeflags", "member_types", "member_linknames")
_ISO = ("system_id", "volume_id", "volume_label", "volume_set_id", "publisher_id", "data_preparer_id",
        "application_id", "volume_creation_date_utc", "volume_modification_date_utc", "volume_space_size",
        "logical_block_size", "joliet_present", "udf_present", "root_member_names")

FIELDS = {
    ("archive", "member_names"): "archive_value",
    ("archive", "member_count"): "archive_value",
    ("archive", "entry_count"): "archive_value",
    ("archive", "ustar_magic"): "archive_value",
    ("archive", "ustar_version"): "archive_value",
    ("archive", "tar_format"): "archive_value",
    ("archive", "member_sizes"): "archive_value",
    ("archive", "member_sizes_bytes"): "archive_value",
    ("archive", "member_mtimes_utc"): "archive_value",
    ("archive", "member_mtimes"): "archive_value",
    ("archive", "member_mtimes_unix"): "archive_value",
    ("archive", "member_modes_octal"): "archive_value",
    ("archive", "member_modes"): "archive_value",
    ("archive", "member_unames"): "archive_value",
    ("archive", "member_gnames"): "archive_value",
    ("archive", "member_uids"): "archive_value",
    ("archive", "member_gids"): "archive_value",
    ("archive", "typeflags"): "archive_value",
    ("archive", "member_typeflags"): "archive_value",
    ("archive", "member_types"): "archive_value",
    ("archive", "member_linknames"): "archive_value",
    ("archive", "system_id"): "archive_value",
    ("archive", "volume_id"): "archive_value",
    ("archive", "volume_label"): "archive_value",
    ("archive", "volume_set_id"): "archive_value",
    ("archive", "publisher_id"): "archive_value",
    ("archive", "data_preparer_id"): "archive_value",
    ("archive", "application_id"): "archive_value",
    ("archive", "volume_creation_date_utc"): "archive_value",
    ("archive", "volume_modification_date_utc"): "archive_value",
    ("archive", "volume_space_size"): "archive_value",
    ("archive", "logical_block_size"): "archive_value",
    ("archive", "joliet_present"): "archive_value",
    ("archive", "udf_present"): "archive_value",
    ("archive", "root_member_names"): "archive_value",
}


def archive_value(data, ctx):
    try:
        if data is None:
            return None
        f = (ctx or {}).get("field") or ""
        if _ar.archives(data):
            ok = f in ("member_names", "member_count", "entry_count", "member_sizes", "member_sizes_bytes",
                        "member_mtimes_utc", "member_mtimes", "member_mtimes_unix", "member_modes",
                        "member_modes_octal", "member_uids", "member_gids")
            return _ar.ar_value(data, dict(ctx or {}, field=f)) if ok else "none"
        if len(data) >= 0x8006 and bytes(data[0x8001:0x8006]) == b"CD001":
            if f in ("member_names",):
                f = "root_member_names"
            return _iso.iso_value(data, dict(ctx or {}, field=f)) if (f in _ISO or f.endswith("_names")) else "none"
        if _tar.parse_tar(data) is not None:
            if f in ("member_names", "member_count", "entry_count") or f in _TAR:
                return _tar.tar_value(data, dict(ctx or {}, field=f))
            return "none"
        return "none"
    except Exception:  # noqa: BLE001 -- defensive: a hostile member never raises past the extractor
        return None
