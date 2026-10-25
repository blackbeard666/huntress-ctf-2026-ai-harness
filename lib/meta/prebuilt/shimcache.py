"""ShimCache / AppCompatCache execution evidence (prebuilt, SPECULATIVE -- never GM-asked yet).

Source: SYSTEM hive value ControlSet00N\\Control\\Session Manager\\AppCompatCache\\AppCompatCache (REG_BINARY, usually
> 16 KB so stored as big data `db`), read with the regf.py cell helpers; a member that IS the raw value blob (exported
.bin) is parsed directly. Control set: the one Select\\Current names, else the lowest ControlSet00N that has the value.
Win10/11 layout: u32 header size @0 (0x30, or 0x34 since 1703 Creators Update); entries from that offset:
  "10ts" sig, u32 unknown (CRC/hash), u32 entry data size, then data = u16 path len (bytes), UTF-16LE path,
  FILETIME u64 (the file's $SI last-modified time, NOT an execution time), u32 data size, data bytes.
Win8.x ("00ts"/"10ts" @0x80) and Win7 (0xBADC0FEE) layouts are not parsed -> None (cannot answer).

Fields (shimcache / appcompatcache fmts; distinctive names also under regf):
  entry_count          = number of entries.
  paths                = entry paths in CACHE ORDER (most-recently-inserted first) -- an ORDER field: emitted as
                         stored, NOT sorted.
  first_path / last_path = first / last entry path in cache order.
  last_modified_times  = FILETIMEs in cache order as 'YYYY-MM-DDTHH:MM:SSZ' (zero FILETIME -> "none" in the list);
  first_last_modified_time = of the first entry. header_size = u32 @0.
Not regf and not a Win10 blob -> "none"; regf without an AppCompatCache value (e.g. NTUSER, Amcache) -> "none"."""
import struct

from .regf import _filetime, _find, _root, _values

FIELDS = {
    ("shimcache", "entry_count"): "shim_value",
    ("shimcache", "entries_count"): "shim_value",
    ("shimcache", "number_of_entries"): "shim_value",
    ("shimcache", "paths"): "shim_value",
    ("shimcache", "entry_paths"): "shim_value",
    ("shimcache", "file_paths"): "shim_value",
    ("shimcache", "first_path"): "shim_value",
    ("shimcache", "first_entry_path"): "shim_value",
    ("shimcache", "last_path"): "shim_value",
    ("shimcache", "last_entry_path"): "shim_value",
    ("shimcache", "last_modified_times"): "shim_value",
    ("shimcache", "last_modified_times_utc"): "shim_value",
    ("shimcache", "first_last_modified_time"): "shim_value",
    ("shimcache", "header_size"): "shim_value",
    ("appcompatcache", "entry_count"): "shim_value",
    ("appcompatcache", "entries_count"): "shim_value",
    ("appcompatcache", "number_of_entries"): "shim_value",
    ("appcompatcache", "paths"): "shim_value",
    ("appcompatcache", "entry_paths"): "shim_value",
    ("appcompatcache", "file_paths"): "shim_value",
    ("appcompatcache", "first_path"): "shim_value",
    ("appcompatcache", "first_entry_path"): "shim_value",
    ("appcompatcache", "last_path"): "shim_value",
    ("appcompatcache", "last_entry_path"): "shim_value",
    ("appcompatcache", "last_modified_times"): "shim_value",
    ("appcompatcache", "last_modified_times_utc"): "shim_value",
    ("appcompatcache", "first_last_modified_time"): "shim_value",
    ("appcompatcache", "header_size"): "shim_value",
    ("regf", "shimcache_entry_count"): "shim_value",
    ("regf", "shimcache_paths"): "shim_value",
    ("regf", "shimcache_first_path"): "shim_value",
    ("regf", "shimcache_last_modified_times"): "shim_value",
    ("regf", "appcompatcache_entry_count"): "shim_value",
    ("regf", "appcompatcache_paths"): "shim_value",
}


def parse_win10(blob):
    """(header size, [(path, FILETIME)]) of a Win10/11 AppCompatCache blob, or None (other layout)."""
    if len(blob) < 0x38:
        return None
    hs, = struct.unpack_from("<I", blob, 0)
    if hs not in (0x30, 0x34) or blob[hs:hs + 4] != b"10ts":
        return None
    out, p = [], hs
    while p + 12 <= len(blob) and blob[p:p + 4] == b"10ts":
        size, = struct.unpack_from("<I", blob, p + 8)
        e = blob[p + 12:p + 12 + size]
        if len(e) < 2:
            break
        plen, = struct.unpack_from("<H", e, 0)
        path = e[2:2 + plen].decode("utf-16-le", "replace")
        ft = struct.unpack_from("<Q", e, 2 + plen)[0] if len(e) >= 10 + plen else 0
        out.append((path, ft))
        p += 12 + size
    return hs, out


def _blob(b):
    """The AppCompatCache value bytes of a SYSTEM hive (or `b` itself when not regf); None = no value."""
    if bytes(b[:4]) != b"regf":
        return bytes(b)
    h, root = _root(b)
    if h is None or root is None:
        return None
    sets = []
    sel = _find(b, root, ("Select",))
    for n, _t, d in _values(b, sel) if sel else []:
        if n.lower() == "current" and len(d) >= 4:
            sets.append("ControlSet%03d" % struct.unpack_from("<I", d)[0])
    sets += ["ControlSet%03d" % i for i in range(1, 10)] + ["CurrentControlSet"]
    for cs in sets:
        k = _find(b, root, (cs, "Control", "Session Manager", "AppCompatCache"))
        for n, _t, d in _values(b, k) if k else []:
            if n.lower() == "appcompatcache":
                return d
    return None


def shim_value(data, ctx):
    """shimcache.<field>: Win10/11 AppCompatCache entries (cache order)."""
    if data is None:
        return None
    try:
        blob = _blob(data)
        if not blob:
            return "none"
        r = parse_win10(blob)
        if r is None:
            # a real AppCompatCache in an older layout (XP/2003/Win7/Win8) -> cannot answer; anything else -> "none"
            magic = struct.unpack_from("<I", blob, 0)[0] if len(blob) >= 4 else 0
            known = magic in (0xDEADBEEF, 0xBADC0FFE, 0xBADC0FEE) or blob[0x80:0x84] in (b"00ts", b"10ts")
            return None if known or bytes(data[:4]) == b"regf" else "none"
        hs, ents = r
        f = (ctx.get("field") or "").replace("shimcache_", "").replace("appcompatcache_", "")
        if f == "header_size":
            return hs
        if f.endswith("_count") or f == "number_of_entries":
            return len(ents)
        if not ents:
            return "none"
        if f in ("paths", "entry_paths", "file_paths"):
            return [p for p, _ in ents]
        if f in ("first_path", "first_entry_path"):
            return ents[0][0]
        if f in ("last_path", "last_entry_path"):
            return ents[-1][0]
        if f.startswith("last_modified_times"):
            return [_filetime(t) for _, t in ents]
        if f == "first_last_modified_time":
            return _filetime(ents[0][1])
    except Exception:
        return None
    return None
