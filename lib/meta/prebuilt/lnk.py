"""Windows shortcut (MS-SHLLINK) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

ShellLinkHeader (0x4C bytes, little-endian): HeaderSize u32 (=0x4C), LinkCLSID (00021401-0000-0000-C000-000000000046),
LinkFlags u32 @0x14, FileAttributes u32 @0x18, CreationTime/AccessTime/WriteTime FILETIME u64 @0x1C/0x24/0x2C,
FileSize u32 @0x34, IconIndex i32 @0x38, ShowCommand u32 @0x3C, HotKey u16 @0x40.
Then, by LinkFlags: LinkTargetIDList (0x1, u16 size), LinkInfo (0x2, u32 size; LocalBasePath + CommonPathSuffix,
Unicode variants when LinkInfoHeaderSize >= 0x24), StringData in spec order NAME (0x4), RELATIVE_PATH (0x8),
WORKING_DIR (0x10), COMMAND_LINE_ARGUMENTS (0x20), ICON_LOCATION (0x40) -- u16 char count, UTF-16LE when IsUnicode
(0x80) else cp1252 -- then ExtraData blocks (u32 size, u32 signature; size < 4 terminates).
TrackerDataBlock = signature 0xA0000003, size 0x60: Length u32, Version u32, MachineID char[16] (NetBIOS name, NUL-
padded), Droid 2xGUID, DroidBirth 2xGUID.
Times: FILETIME (100 ns since 1601-01-01 UTC) -> ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ' (sub-second part dropped, same
spelling as pe.time_date_stamp_utc); a zero FILETIME = not set -> "none".
target_path: LinkInfo LocalBasePath(+CommonPathSuffix), else EnvironmentVariableDataBlock target, else the path the
LinkTargetIDList spells (drive + file-entry long names). Not a shell link / absent structure -> "none"."""
import datetime
import struct

from ..spell import Hex

FIELDS = {
    ("lnk", "target_path"): "lnk_value",
    ("lnk", "local_base_path"): "lnk_value",
    ("lnk", "link_info_local_base_path"): "lnk_value",
    ("lnk", "linkinfo_local_base_path"): "lnk_value",
    ("lnk", "link_flags_u32_hex"): "lnk_value",
    ("lnk", "header_link_flags_u32_hex"): "lnk_value",
    ("lnk", "flags_u32_hex"): "lnk_value",
    ("lnk", "file_attributes_u32_hex"): "lnk_value",
    ("lnk", "header_file_attributes_u32_hex"): "lnk_value",
    ("lnk", "target_file_attributes_u32_hex"): "lnk_value",
    ("lnk", "creation_time"): "lnk_value",
    ("lnk", "creation_time_utc"): "lnk_value",
    ("lnk", "creation_time_iso8601"): "lnk_value",
    ("lnk", "header_creation_time"): "lnk_value",
    ("lnk", "target_creation_time"): "lnk_value",
    ("lnk", "access_time"): "lnk_value",
    ("lnk", "access_time_utc"): "lnk_value",
    ("lnk", "header_access_time"): "lnk_value",
    ("lnk", "write_time"): "lnk_value",
    ("lnk", "write_time_utc"): "lnk_value",
    ("lnk", "header_write_time"): "lnk_value",
    ("lnk", "modification_time"): "lnk_value",
    ("lnk", "modified_time"): "lnk_value",
    ("lnk", "file_size"): "lnk_value",
    ("lnk", "file_size_bytes"): "lnk_value",
    ("lnk", "header_file_size"): "lnk_value",
    ("lnk", "target_file_size"): "lnk_value",
    ("lnk", "target_file_size_bytes"): "lnk_value",
    ("lnk", "icon_index"): "lnk_value",
    ("lnk", "show_command"): "lnk_value",
    ("lnk", "show_command_u32_hex"): "lnk_value",
    ("lnk", "hot_key_u16_hex"): "lnk_value",
    ("lnk", "working_dir"): "lnk_value",
    ("lnk", "working_directory"): "lnk_value",
    ("lnk", "string_data_working_dir"): "lnk_value",
    ("lnk", "arguments"): "lnk_value",
    ("lnk", "command_line_arguments"): "lnk_value",
    ("lnk", "string_data_arguments"): "lnk_value",
    ("lnk", "name_string"): "lnk_value",
    ("lnk", "description"): "lnk_value",
    ("lnk", "relative_path"): "lnk_value",
    ("lnk", "icon_location"): "lnk_value",
    ("lnk", "machine_id"): "lnk_value",
    ("lnk", "tracker_machine_id"): "lnk_value",
    ("lnk", "tracker_data_machine_id"): "lnk_value",
    ("lnk", "tracker_data_block_machine_id"): "lnk_value",
    ("lnk", "netbios_name"): "lnk_value",
}

_CLSID = bytes.fromhex("0114020000000000c000000000000046")
_STRS = ("name", "relative_path", "working_dir", "arguments", "icon_location")   # flag bits 0x4 .. 0x40


def _cstr(b, off, wide=False):
    if off <= 0 or off >= len(b):
        return None
    if wide:
        end = off
        while end + 1 < len(b) and b[end:end + 2] != b"\0\0":
            end += 2
        return b[off:end].decode("utf-16-le", "replace")
    end = b.find(b"\0", off)
    return b[off:end if end >= 0 else len(b)].decode("cp1252", "replace")


def _filetime(v):
    if not v:
        return "none"
    t = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=v // 10)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _idlist_path(idl):
    """Best-effort path from a LinkTargetIDList: drive item (0x2F) + file-entry items (0x30..0x3F) long names."""
    parts, off = [], 0
    while off + 2 <= len(idl):
        sz, = struct.unpack_from("<H", idl, off)
        if sz < 2:
            break
        it = idl[off:off + sz]
        off += sz
        if len(it) < 3:
            continue
        t = it[2]
        if t == 0x2F and len(it) >= 5:
            parts.append(it[3:].split(b"\0", 1)[0].decode("cp1252", "replace").rstrip("\\"))
        elif 0x30 <= t <= 0x3F and len(it) > 14:
            name = None
            e = it.find(b"\x04\x00\xef\xbe")                 # BEEF0004 extension block: long name UTF-16LE
            if e >= 4:
                xs, = struct.unpack_from("<H", it, e - 4)
                xv, = struct.unpack_from("<H", it, e - 2)
                lo = e - 4 + (0x2E if xv >= 9 else 0x2A if xv >= 8 else 0x26 if xv >= 7 else 0x14)   # libfwsi layout
                if lo < e - 4 + xs:
                    name = _cstr(it, lo, True)
            if not name:
                name = _cstr(it, 14, bool(t & 0x04))
            if name:
                parts.append(name)
    if not parts:
        return None
    return "\\".join(parts) if len(parts) > 1 else (parts[0] + "\\" if parts[0].endswith(":") else parts[0])


def parse(b):
    """The shell link's fields as a dict, or None (not an MS-SHLLINK file / truncated header)."""
    if not b or len(b) < 0x4C or b[:4] != b"\x4c\0\0\0" or b[4:20] != _CLSID:
        return None
    flags, attrs, ct, at, wt, fsize, icon, show, hot = struct.unpack_from("<IIQQQIiIH", b, 0x14)
    r = {"link_flags": flags, "file_attributes": attrs, "creation_time": ct, "access_time": at, "write_time": wt,
         "file_size": fsize, "icon_index": icon, "show_command": show, "hot_key": hot}
    off, idlist = 0x4C, None
    if flags & 0x1:
        n, = struct.unpack_from("<H", b, off)
        idlist = b[off + 2:off + 2 + n]
        off += 2 + n
    if flags & 0x2 and off + 28 <= len(b):
        li = b[off:]
        lsz, hsz, lflags, _, lbp, _, cps = struct.unpack_from("<7I", li, 0)
        li = li[:lsz]
        base = suffix = None
        if hsz >= 0x24 and len(li) >= 36:
            lbpu, cpsu = struct.unpack_from("<II", li, 28)
            if lflags & 1:
                base = _cstr(li, lbpu, True)
            suffix = _cstr(li, cpsu, True)
        if lflags & 1 and base is None:
            base = _cstr(li, lbp, False)
        if suffix is None:
            suffix = _cstr(li, cps, False)
        if base is not None:
            r["local_base_path"] = base + (suffix or "")
        off += lsz
    wide = bool(flags & 0x80)
    for i, key in enumerate(_STRS):
        if flags & (0x4 << i):
            if off + 2 > len(b):
                return r
            n, = struct.unpack_from("<H", b, off)
            raw = b[off + 2:off + 2 + n * (2 if wide else 1)]
            r[key] = raw.decode("utf-16-le" if wide else "cp1252", "replace")
            off += 2 + len(raw)
    while off + 8 <= len(b):
        sz, sig = struct.unpack_from("<II", b, off)
        if sz < 8:
            break
        blk = b[off:off + sz]
        if sig == 0xA0000003 and len(blk) >= 32:
            r["machine_id"] = blk[16:32].split(b"\0", 1)[0].decode("cp1252", "replace")
        elif sig == 0xA0000001 and len(blk) >= 0x314:
            r["env_target"] = (_cstr(blk, 0x10C, True) or _cstr(blk, 8, False) or "") or None
        off += sz
    if idlist is not None:
        r["idlist_path"] = _idlist_path(idlist)
    return r


def _pick(r, f):
    if f.endswith("_u32_hex") or f.endswith("_u16_hex"):
        w = 4 if f.endswith("_u16_hex") else 8
        for k in ("link_flags", "file_attributes", "show_command", "hot_key"):
            if k in f or (k == "link_flags" and f == "flags_u32_hex"):
                return Hex(r[k], w)
        return None
    if f.endswith("_time") or "_time_" in f:
        k = "creation_time" if "creat" in f else "access_time" if "access" in f else "write_time"
        return _filetime(r[k])
    if "file_size" in f:
        return r["file_size"]
    if f == "icon_index":
        return r["icon_index"]
    if f == "show_command":
        return r["show_command"]
    if "machine_id" in f or f == "netbios_name":
        return r.get("machine_id") or "none"
    if "working_dir" in f:
        return r.get("working_dir", "none")
    if "arguments" in f:
        return r.get("arguments", "none")
    if f in ("name_string", "description"):
        return r.get("name", "none")
    if f in ("relative_path", "icon_location"):
        return r.get(f, "none")
    if f in ("local_base_path", "link_info_local_base_path", "linkinfo_local_base_path"):
        return r.get("local_base_path") or "none"
    if f == "target_path":
        return r.get("local_base_path") or r.get("env_target") or r.get("idlist_path") or "none"
    return None


def lnk_value(data, ctx):
    if data is None:
        return None
    try:
        r = parse(bytes(data))
        if r is None:
            return "none"
        return _pick(r, ctx.get("field") or "")
    except Exception:
        return None
