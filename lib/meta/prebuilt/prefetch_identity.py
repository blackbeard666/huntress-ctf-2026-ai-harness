"""Windows Prefetch identity beyond the header name (prebuilt, SPECULATIVE): full executable path, all volumes,
directory strings, the member-name hash and a recomputed SCCA path hash. D26 flavour: "even after filenames changed
... recover executable identities" (every D26 TT/Mastery member was a renamed `trace-001.pf`).

Container handling (MAM Xpress-Huffman / Xpress / LZNT1 -> SCCA) is shared with prefetch.py (`_scca`). Layout per
libscca "Windows Prefetch File (PF) format", little-endian, offsets in the decompressed SCCA:
  file information @84: filename strings offset/size u32 @100/@104, volumes information offset u32 @108,
  number of volumes u32 @112. Filename strings = UTF-16LE NUL-separated full paths.
  volume entry (40 B v17, 104 B v23/v26, 96 B v30/v31; first 36 bytes common): device path offset u32 @0 (relative
  to the volumes block) + chars u32 @4, creation FILETIME @8, serial u32 @16, file refs offset/size @20/@24,
  directory strings offset u32 @28 (relative to the volumes block) + count u32 @32; each directory string = u16
  chars + UTF-16LE chars + NUL.
Fields:
  executable_path = the filename-strings entry whose basename == header executable name (case-insensitive), kept
    verbatim (e.g. `\\VOLUME{01d7...-a1b2c3d4}\\WINDOWS\\SYSTEM32\\CMD.EXE`); the header name is truncated to 29
    chars, so a basename that merely starts with a 29-char header name also counts. No entry -> "none".
  executable_directory = executable_path minus the last `\\component`.
  executable_device_path = executable_path in `\\DEVICE\\HARDDISKVOLUME<n>\\...` form (the string the kernel hashes).
  filename_strings_count = number of filename strings (NOT prefetch.file_count = metrics entries).
  directory_strings = every volume's directory strings, JSON sorted; directory_count = their total.
  volume_serials / volume_device_paths / volume_creation_times_utc = every volume entry, stored order
    (serial "0x%08x", FILETIME -> ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ', zero -> "none").
  filename_hash_from_name = the -XXXXXXXX of a `NAME-XXXXXXXX.pf` member name -> "0x" + lowercase; "none" when the
    member was renamed (`trace-001.pf`). filename_stem_matches_header = NAME (or the whole stem) == header name,
    case-insensitive. filename_hash_matches_header = name hash == header hash u32 @76 ("none" without a name hash).
  computed_path_hash_u32_hex = SCCA hash (libscca "Prefetch hash") of the upper-cased UTF-16LE device path:
    v17 XP: h=0; h=h*37+byte; h=h*314159269; h>0x80000000 -> 2^32-h; h %= 1000000007.
    v23 Vista/7: h=314159; h=(h*37+byte) & 0xffffffff.  v26/v30/v31 '2008' 8-byte-block variant (identical value:
    442596621 = 37^7, -803794207 = 37^8 mod 2^32). Checked on real names: XP CMD.EXE-087B4001 / NOTEPAD.EXE-336351A9
    (HARDDISKVOLUME1), Win7 CMD.EXE-4A81B364 / NOTEPAD.EXE-D8414F97 (HARDDISKVOLUME2), D26 single CMD.EXE-CD245F9E
    (\\VOLUME{01dac5d8...} = HARDDISKVOLUME4). Win10 files store `\\VOLUME{guid-serial}` paths, not the volume
    number: the device form is then the first `\\DEVICE\\HARDDISKVOLUME<n>` (n = 0..64) whose hash equals the header
    hash; none matches (the D26 TT/Mastery kit re-randomised the header hash) -> computed hash None (unknowable).
  path_hash_matches = computed == header hash (bool). Hosting executables (DLLHOST.EXE, RUNDLL32.EXE, MMC.EXE,
    ...) hash the command line too, so they legitimately answer false (note only; not special-cased).
Decoys: not SCCA/MAM -> "none" (every field); MAM that does not decompress / truncated tables -> None."""
import datetime
import re
import struct

from ..spell import Hex
from .prefetch import _scca

FIELDS = {
    ("prefetch", "executable_path"): "pf_identity",
    ("prefetch", "executable_full_path"): "pf_identity",
    ("prefetch", "full_path"): "pf_identity",
    ("prefetch", "exe_path"): "pf_identity",
    ("prefetch", "image_path"): "pf_identity",
    ("prefetch", "executable_directory"): "pf_identity",
    ("prefetch", "executable_dir"): "pf_identity",
    ("prefetch", "exe_directory"): "pf_identity",
    ("prefetch", "executable_device_path"): "pf_identity",
    ("prefetch", "device_path"): "pf_identity",
    ("prefetch", "filename_strings_count"): "pf_identity",
    ("prefetch", "filename_count"): "pf_identity",
    ("prefetch", "file_name_count"): "pf_identity",
    ("prefetch", "filenames_count"): "pf_identity",
    ("prefetch", "number_of_filenames"): "pf_identity",
    ("prefetch", "number_of_filename_strings"): "pf_identity",
    ("prefetch", "directory_strings"): "pf_identity",
    ("prefetch", "directory_names"): "pf_identity",
    ("prefetch", "directories"): "pf_identity",
    ("prefetch", "directory_count"): "pf_identity",
    ("prefetch", "directory_strings_count"): "pf_identity",
    ("prefetch", "number_of_directory_strings"): "pf_identity",
    ("prefetch", "volume_serials"): "pf_identity",
    ("prefetch", "volume_serial_numbers"): "pf_identity",
    ("prefetch", "volume_serials_u32_hex"): "pf_identity",
    ("prefetch", "volume_device_paths"): "pf_identity",
    ("prefetch", "volume_paths"): "pf_identity",
    ("prefetch", "volume_creation_times_utc"): "pf_identity",
    ("prefetch", "volume_creation_times"): "pf_identity",
    ("prefetch", "filename_hash_from_name"): "pf_identity",
    ("prefetch", "filename_hash"): "pf_identity",
    ("prefetch", "file_name_hash"): "pf_identity",
    ("prefetch", "filename_hash_u32_hex"): "pf_identity",
    ("prefetch", "name_hash_u32_hex"): "pf_identity",
    ("prefetch", "filename_stem_matches_header"): "pf_identity",
    ("prefetch", "filename_matches_header"): "pf_identity",
    ("prefetch", "file_name_matches_header"): "pf_identity",
    ("prefetch", "name_matches_header"): "pf_identity",
    ("prefetch", "filename_hash_matches_header"): "pf_identity",
    ("prefetch", "computed_path_hash_u32_hex"): "pf_identity",
    ("prefetch", "computed_prefetch_hash_u32_hex"): "pf_identity",
    ("prefetch", "computed_hash_u32_hex"): "pf_identity",
    ("prefetch", "recomputed_path_hash_u32_hex"): "pf_identity",
    ("prefetch", "path_hash_matches"): "pf_identity",
    ("prefetch", "prefetch_hash_matches"): "pf_identity",
    ("prefetch", "hash_matches"): "pf_identity",
    ("prefetch", "computed_hash_matches"): "pf_identity",
}

_M32 = 0xFFFFFFFF
_VOL_SIZE = {17: 40, 23: 104, 26: 104, 30: 96, 31: 96}
_NAME_RE = re.compile(r"^(.+)-([0-9A-Fa-f]{8})\.pf$", re.I)
_VOLUME_RE = re.compile(r"^\\VOLUME\{[^}]*\}", re.I)


def _u32(b, o):
    return struct.unpack_from("<I", b, o)[0] if 0 <= o and o + 4 <= len(b) else None


def _filetime(v):
    if not v:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=v // 10)
    except OverflowError:
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_xp(bs):
    """libscca 'Prefetch hash' -- Windows XP (SCCA v17)."""
    h = 0
    for c in bs:
        h = (h * 37 + c) & _M32
    h = (h * 314159269) & _M32
    if h > 0x80000000:
        h = 0x100000000 - h
    return (abs(h) % 1000000007) & _M32


def hash_vista(bs):
    """libscca 'Prefetch hash' -- Vista / 7 (SCCA v23)."""
    h = 314159
    for c in bs:
        h = (h * 37 + c) & _M32
    return h


def hash_2008(bs):
    """libscca 'Prefetch hash' -- the Windows 2008 / 8+ 8-byte-block variant (SCCA v26/v30/v31)."""
    h, i, n = 314159, 0, len(bs)
    while i + 8 < n:
        v = bs[i + 1] * 37 + bs[i + 2]
        for k in (3, 4, 5, 6):
            v = v * 37 + bs[i + k]
        v = v * 37 + bs[i] * 442596621 + bs[i + 7]
        h = (v - h * 803794207) & _M32
        i += 8
    while i < n:
        h = (37 * h + bs[i]) & _M32
        i += 1
    return h


def path_hash(path, ver):
    bs = path.upper().encode("utf-16-le")
    return hash_xp(bs) if ver == 17 else hash_vista(bs) if ver == 23 else hash_2008(bs)


def _file_names(b):
    off, size = _u32(b, 100), _u32(b, 104)
    if off is None or size is None or off + size > len(b):
        return None
    s = b[off:off + size]
    out, i = [], 0
    while i + 1 < len(s):
        j = i
        while j + 1 < len(s) and s[j:j + 2] != b"\0\0":
            j += 2
        out.append(s[i:j].decode("utf-16-le", "replace"))
        i = j + 2
    return out


def _utf16(b, o, chars):
    if o < 0 or o + 2 * chars > len(b):
        return None
    return b[o:o + 2 * chars].decode("utf-16-le", "replace").split("\0")[0]


def _volumes(b, ver):
    """[{path, serial, ctime, dirs}] of every volume entry, or None when unreadable."""
    voff, nvol, esz = _u32(b, 108), _u32(b, 112), _VOL_SIZE.get(ver)
    if voff is None or nvol is None or esz is None or nvol > 4096 or voff + esz * nvol > len(b):
        return None
    out = []
    for k in range(nvol):
        e = voff + esz * k
        dp, dn, ctime, serial, ds, dc = struct.unpack_from("<IIQI8xII", b, e)
        path = _utf16(b, voff + dp, dn)
        dirs, p = [], voff + ds
        if dc > 65536:
            return None
        for _ in range(dc):
            if p + 2 > len(b):
                return None
            n = b[p] | b[p + 1] << 8
            s = _utf16(b, p + 2, n)
            if s is None:
                return None
            dirs.append(s)
            p += 2 + 2 * n + 2
        out.append({"path": path, "serial": serial, "ctime": ctime, "dirs": dirs})
    return out


def _header_name(b):
    s = b[16:76]
    for i in range(0, len(s) - 1, 2):
        if s[i:i + 2] == b"\0\0":
            s = s[:i]
            break
    return s.decode("utf-16-le", "replace").strip()


def _exe_path(b):
    names, hdr = _file_names(b), _header_name(b).upper()
    if names is None:
        return None
    if not hdr:
        return "none"
    base = lambda p: p.rsplit("\\", 1)[-1].upper()  # noqa: E731
    hit = [p for p in names if base(p) == hdr] or \
        ([p for p in names if base(p).startswith(hdr)] if len(hdr) >= 29 else [])
    return hit[0] if hit else "none"


def _device_path(b, ver, path):
    """(device-form path, computed hash) or (None, None) when the volume number cannot be recovered."""
    hdr = _u32(b, 76)
    if not _VOLUME_RE.match(path):
        return path, path_hash(path, ver)
    rest = _VOLUME_RE.sub("", path)
    for v in _volumes(b, ver) or []:   # a volume entry that already names the device form
        dev = v["path"] or ""
        if dev.upper().startswith("\\DEVICE\\") and v["serial"] is not None and \
                path.upper().startswith("\\VOLUME{") and path[:path.find("}")].upper().endswith("%08X" % v["serial"]):
            q = dev + rest
            return q, path_hash(q, ver)
    for n in range(65):
        q = "\\DEVICE\\HARDDISKVOLUME%d%s" % (n, rest)
        h = path_hash(q, ver)
        if h == hdr:
            return q, h
    return None, None


def _member_name(ctx):
    m = str((ctx or {}).get("member") or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    return m


def _value(b, f, ctx):
    ver = _u32(b, 0)
    if f in ("filename_hash_from_name", "filename_hash", "file_name_hash", "filename_hash_u32_hex",
             "name_hash_u32_hex", "filename_hash_matches_header"):
        m = _NAME_RE.match(_member_name(ctx))
        if not m:
            return "none"
        h = int(m.group(2), 16)
        if f == "filename_hash_matches_header":
            return h == _u32(b, 76)
        return Hex(h, 8)
    if f in ("filename_stem_matches_header", "filename_matches_header", "file_name_matches_header",
             "name_matches_header"):
        mem = _member_name(ctx)
        if not mem:
            return None
        m = _NAME_RE.match(mem)
        stem = m.group(1) if m else re.sub(r"\.pf$", "", mem, flags=re.I)
        return stem.upper() == _header_name(b).upper()
    if f in ("filename_strings_count", "filename_count", "file_name_count", "filenames_count",
             "number_of_filenames", "number_of_filename_strings"):
        names = _file_names(b)
        return len(names) if names is not None else None
    if f.startswith("volume") or f.startswith("director"):
        vols = _volumes(b, ver)
        if vols is None:
            return None
        if f in ("volume_serials", "volume_serial_numbers", "volume_serials_u32_hex"):
            return ["0x%08x" % v["serial"] for v in vols]
        if f in ("volume_device_paths", "volume_paths"):
            return [v["path"] for v in vols] if all(v["path"] is not None for v in vols) else None
        if f in ("volume_creation_times_utc", "volume_creation_times"):
            return [_filetime(v["ctime"]) for v in vols]
        dirs = sorted(d for v in vols for d in v["dirs"])
        return len(dirs) if f.endswith("count") else dirs
    path = _exe_path(b)
    if path is None or path == "none":
        if f in ("path_hash_matches", "prefetch_hash_matches", "hash_matches", "computed_hash_matches") \
                and path == "none":
            return None
        return path
    if f in ("executable_path", "executable_full_path", "full_path", "exe_path", "image_path"):
        return path
    if f in ("executable_directory", "executable_dir", "exe_directory"):
        return path.rsplit("\\", 1)[0] if "\\" in path else "none"
    if ver not in _VOL_SIZE:
        return None   # unknown SCCA version: which hash family applies is unknown
    dev, h = _device_path(b, ver, path)
    if f in ("executable_device_path", "device_path"):
        return dev
    if f in ("computed_path_hash_u32_hex", "computed_prefetch_hash_u32_hex", "computed_hash_u32_hex",
             "recomputed_path_hash_u32_hex"):
        return Hex(h, 8) if h is not None else None
    if f in ("path_hash_matches", "prefetch_hash_matches", "hash_matches", "computed_hash_matches"):
        return h is not None and h == _u32(b, 76)
    return None


def pf_identity(data, ctx):
    """prefetch.<identity field> of an SCCA / MAM-compressed .pf member (see module docstring)."""
    try:
        s = _scca(data)
        if not isinstance(s, tuple):
            return s
        b = s[0]
        if len(b) < 116:
            return None
        return _value(b, (ctx or {}).get("field") or "", ctx)
    except (struct.error, ValueError, IndexError, TypeError, OverflowError, UnicodeError):
        return None
