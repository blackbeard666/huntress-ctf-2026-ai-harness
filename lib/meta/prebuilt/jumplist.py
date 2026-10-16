"""Windows Jump List (`<AppID>.automaticDestinations-ms`) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

An AutomaticDestinations jump list is a CFB (OLE2) file: one `DestList` stream + one MS-SHLLINK stream per entry, named
by the entry number in lowercase hex ("1", "2", "a", ...). The AppID is NOT stored inside: it is the 16-hex-digit
member file name stem (CRC-64 of the AppUserModelID).
DestList (libyal "Jump lists format" / plaso automatic_destinations.yaml), little-endian:
  header 32 B: format_version u32 (1 = Win7/8, 3/4 = Win10/11), number_of_entries u32, number_of_pinned_entries u32,
    unknown f32, last_entry_number u32, unknown u32, last_revision_number u32, unknown u32.
  entry v1: checksum u64, droid volume/file + birth volume/file GUIDs (4 x 16), hostname char[16] (NUL-padded),
    entry_number u32 @0x58, unknown u32, unknown f32, last_modification_time FILETIME u64, pin_status i32,
    path_size u16 (chars) @0x70, path UTF-16LE.
  entry v2+: as v1 up to pin_status, then unknown i32, access_count u32, unknown u64, path_size u16 @0x80,
    path UTF-16LE, trailing u32.
Lists keep stored order (DestList = MRU order); lnk_stream_names are in CFB directory order = numeric (shorter name
first, then upper-case compare -- i.e. hex value). first_target_path = the target of the lowest-numbered LNK stream
(lnk.target_path rules: LinkInfo LocalBasePath+suffix, else env block, else IDList path).
Not a CFB / no DestList and no LNK stream -> "none"."""
import re
import struct

from ..cfb import cfb_streams
from . import lnk as _lnk

FIELDS = {
    ("jumplist", "app_id"): "jumplist_value",
    ("jumplist", "appid"): "jumplist_value",
    ("jumplist", "application_id"): "jumplist_value",
    ("jumplist", "app_id_hex"): "jumplist_value",
    ("jumplist", "destlist_entry_count"): "jumplist_value",
    ("jumplist", "destlist_entries_count"): "jumplist_value",
    ("jumplist", "destlist_number_of_entries"): "jumplist_value",
    ("jumplist", "destlist_header_number_of_entries"): "jumplist_value",
    ("jumplist", "destlist_header_entry_count"): "jumplist_value",
    ("jumplist", "entry_count"): "jumplist_value",
    ("jumplist", "number_of_entries"): "jumplist_value",
    ("jumplist", "destlist_pinned_entry_count"): "jumplist_value",
    ("jumplist", "destlist_number_of_pinned_entries"): "jumplist_value",
    ("jumplist", "pinned_entry_count"): "jumplist_value",
    ("jumplist", "destlist_version"): "jumplist_value",
    ("jumplist", "destlist_format_version"): "jumplist_value",
    ("jumplist", "destlist_header_version"): "jumplist_value",
    ("jumplist", "format_version"): "jumplist_value",
    ("jumplist", "destlist_last_entry_number"): "jumplist_value",
    ("jumplist", "destlist_last_revision_number"): "jumplist_value",
    ("jumplist", "destlist_paths"): "jumplist_value",
    ("jumplist", "destlist_entry_paths"): "jumplist_value",
    ("jumplist", "destlist_path_list"): "jumplist_value",
    ("jumplist", "entry_paths"): "jumplist_value",
    ("jumplist", "destlist_first_path"): "jumplist_value",
    ("jumplist", "destlist_first_entry_path"): "jumplist_value",
    ("jumplist", "destlist_entry_numbers"): "jumplist_value",
    ("jumplist", "destlist_hostnames"): "jumplist_value",
    ("jumplist", "destlist_netbios_names"): "jumplist_value",
    ("jumplist", "destlist_machine_ids"): "jumplist_value",
    ("jumplist", "lnk_stream_names"): "jumplist_value",
    ("jumplist", "lnk_stream_count"): "jumplist_value",
    ("jumplist", "lnk_count"): "jumplist_value",
    ("jumplist", "embedded_lnk_count"): "jumplist_value",
    ("jumplist", "first_target_path"): "jumplist_value",
    ("jumplist", "first_lnk_target_path"): "jumplist_value",
    ("jumplist", "lnk_target_paths"): "jumplist_value",
    ("jumplist", "target_paths"): "jumplist_value",
}

_HEX = re.compile(r"[0-9a-fA-F]{1,8}")
_APPID = re.compile(r"(?:^|[\\/])([0-9a-fA-F]{16})\.(?:automatic|custom)destinations-ms$", re.I)


def destlist(d):
    """DestList header + entries as a dict, or None."""
    if not d or len(d) < 32:
        return None
    ver, n, pinned, _, last, _, rev, _ = struct.unpack_from("<IIIfIIII", d, 0)
    if not 1 <= ver <= 8:
        return None
    fixed = 0x70 if ver == 1 else 0x80
    ents, off = [], 32
    while off + fixed + 2 <= len(d) and len(ents) < 100000:
        num, = struct.unpack_from("<I", d, off + 0x58)
        plen, = struct.unpack_from("<H", d, off + fixed)
        raw = d[off + fixed + 2:off + fixed + 2 + plen * 2]
        if len(raw) < plen * 2:
            break
        host = d[off + 0x48:off + 0x58].split(b"\0", 1)[0].decode("cp1252", "replace")
        ents.append((num, host, raw.decode("utf-16-le", "replace").rstrip("\0")))
        off += fixed + 2 + plen * 2 + (0 if ver == 1 else 4)
    return {"version": ver, "count": n, "pinned": pinned, "last": last, "rev": rev, "entries": ents}


def parse(b):
    st = cfb_streams(b, demangle=False)
    if not st:
        return None
    names = sorted((k for k in st if _HEX.fullmatch(k)), key=lambda k: (len(k), k.upper()))
    lnks = [(k, _lnk.parse(st[k])) for k in names]
    lnks = [(k, r) for k, r in lnks if r is not None]
    dl = destlist(st.get("DestList"))
    if dl is None and not lnks:
        return None
    return {"destlist": dl, "lnks": lnks}


def _pick(j, f, member):
    dl, lnks = j["destlist"], j["lnks"]
    if f.startswith("app") or f == "application_id":
        m = _APPID.search(member or "")
        return m.group(1).lower() if m else "none"
    if "lnk" in f or "target_path" in f:
        if f.endswith("_count"):
            return len(lnks)
        if f == "lnk_stream_names":
            return [k for k, _ in lnks]
        paths = [_lnk._pick(r, "target_path") for _, r in lnks]
        if f.startswith("first"):
            return paths[0] if paths else "none"
        return paths
    if dl is None:
        return "none"
    ents = dl["entries"]
    if "pinned" in f:
        return dl["pinned"]
    if "version" in f:
        return dl["version"]
    if "last_entry" in f:
        return dl["last"]
    if "revision" in f:
        return dl["rev"]
    if f.endswith("count") or f.endswith("number_of_entries"):
        return dl["count"]
    if "first" in f:
        return ents[0][2] if ents else "none"
    if "path" in f:
        return [e[2] for e in ents]
    if "entry_numbers" in f:
        return [e[0] for e in ents]
    if "host" in f or "netbios" in f or "machine" in f:
        return [e[1] for e in ents]
    return None


def jumplist_value(data, ctx):
    if data is None:
        return None
    try:
        j = parse(bytes(data))
        if j is None:
            return "none"
        return _pick(j, ctx.get("field") or "", ctx.get("member") or "")
    except Exception:
        return None
