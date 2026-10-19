"""TAR (POSIX ustar / GNU / pax / v7) member-table fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Read with stdlib tarfile on io.BytesIO (mode "r:", no decompression): header checksums are verified, so a zip / gzip /
random impostor fails to open -> "none". Lists keep the STORED order (`tar tf` order, no sorting); directory names get
the trailing "/" every writer stores (GNU tar and CPython's tarfile both write `dir/`; tarfile strips it on read, `tar
tf` shows it). pax / GNU long names are already merged by tarfile (the real name, not `././@LongLink`).
ustar_magic = the 6-byte magic of the FIRST header @257 trimmed of NUL/space ("ustar" for both POSIX `ustar\\0` + "00"
and GNU `ustar  \\0`); ustar_version = the 2 bytes @263 trimmed ("00" POSIX, "" GNU -> "none"); tar_format = "gnu" |
"pax" | "ustar" | "v7" (GNU = `ustar  \\0`; pax = ustar with an x/g header anywhere).
Times: member_mtimes_utc = header mtime (octal Unix seconds, UTC) as ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' (same spelling as
gzip/lnk *_utc); *_unix = raw ints. Modes: member_modes_octal = permission bits as 4-digit octal text ("0644", the
`%04o` of the stored mode & 0o7777). typeflags = the stored typeflag chars ("0" file, "5" dir, "2" symlink, ...;
NUL (old v7 regular file) -> "0")."""
import datetime
import io
import tarfile

FIELDS = {
    ("tar", "ustar_magic"): "tar_value",
    ("tar", "magic"): "tar_value",
    ("tar", "header_magic"): "tar_value",
    ("tar", "ustar_version"): "tar_value",
    ("tar", "tar_format"): "tar_value",
    ("tar", "format"): "tar_value",
    ("tar", "member_names"): "tar_value",
    ("tar", "member_name_list"): "tar_value",
    ("tar", "file_names"): "tar_value",
    ("tar", "entry_names"): "tar_value",
    ("tar", "names"): "tar_value",
    ("tar", "member_count"): "tar_value",
    ("tar", "entry_count"): "tar_value",
    ("tar", "file_count"): "tar_value",
    ("tar", "number_of_members"): "tar_value",
    ("tar", "member_sizes"): "tar_value",
    ("tar", "member_sizes_bytes"): "tar_value",
    ("tar", "member_mtimes_utc"): "tar_value",
    ("tar", "member_mtimes"): "tar_value",
    ("tar", "member_mtimes_unix"): "tar_value",
    ("tar", "member_modes_octal"): "tar_value",
    ("tar", "member_modes"): "tar_value",
    ("tar", "member_unames"): "tar_value",
    ("tar", "member_gnames"): "tar_value",
    ("tar", "member_uids"): "tar_value",
    ("tar", "member_gids"): "tar_value",
    ("tar", "typeflags"): "tar_value",
    ("tar", "member_typeflags"): "tar_value",
    ("tar", "member_types"): "tar_value",
    ("tar", "member_linknames"): "tar_value",
    ("tar", "symlink_targets"): "tar_value",
}

_MAX_MEMBERS = 5000


def _iso(t):
    return datetime.datetime.fromtimestamp(int(t), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_tar(b):
    """{"magic", "version", "format", "members": [TarInfo]} or None (not an uncompressed tar)."""
    if not b or len(b) < 512:
        return None
    try:
        tf = tarfile.open(fileobj=io.BytesIO(bytes(b)), mode="r:")
    except Exception:  # noqa: BLE001
        return None
    members = []
    try:
        for m in tf:
            members.append(m)
            if len(members) >= _MAX_MEMBERS:
                break
    except Exception:  # noqa: BLE001 -- truncated tail: keep what parsed
        pass
    if not members:
        return None
    raw_magic, raw_ver = bytes(b[257:263]), bytes(b[263:265])
    magic = raw_magic.strip(b"\0 ").decode("latin-1")
    pax = bool(tf.pax_headers) or any(m.pax_headers for m in members)
    if raw_magic + raw_ver == b"ustar  \0":
        fmt = "gnu"
    elif magic == "ustar":
        fmt = "pax" if pax else "ustar"
    else:
        fmt = "v7"
    return {"magic": magic or None, "version": raw_ver.strip(b"\0 ").decode("latin-1") or None, "format": fmt,
            "members": members}


def tar_value(data, ctx):
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- defensive: a hostile member never raises past the extractor
        return None


def _name(m):
    return m.name + "/" if m.isdir() and not m.name.endswith("/") else m.name


def _type(m):
    t = m.type.decode("latin-1") if isinstance(m.type, bytes) else str(m.type)
    return "0" if t in ("\0", "") else t


def _value(data, f):
    if data is None:
        return None
    t = parse_tar(data)
    if t is None:
        return "none"
    ms = t["members"]
    if f in ("ustar_magic", "magic", "header_magic"):
        return t["magic"] or "none"
    if f == "ustar_version":
        return t["version"] or "none"
    if f in ("tar_format", "format"):
        return t["format"]
    if f.endswith("_count") or f == "number_of_members":
        return len(ms)
    if "name" in f and "uname" not in f and "gname" not in f and "link" not in f:
        return [_name(m) for m in ms]
    if "size" in f:
        return [m.size for m in ms]
    if "mtime" in f:
        return [int(m.mtime) for m in ms] if f.endswith("_unix") else [_iso(m.mtime) for m in ms]
    if "mode" in f:
        return ["%04o" % (m.mode & 0o7777) for m in ms]
    if "uname" in f:
        return [m.uname for m in ms]
    if "gname" in f:
        return [m.gname for m in ms]
    if f.endswith("uids"):
        return [m.uid for m in ms]
    if f.endswith("gids"):
        return [m.gid for m in ms]
    if "type" in f:
        return [_type(m) for m in ms]
    if "link" in f or "symlink" in f:
        return [m.linkname for m in ms if m.issym() or m.islnk()]
    return None
