"""Windows shortcut (MS-SHLLINK) fields. COPIED from the GM-verified D14 solver
(challenges/day14/metadata-the-shortcut-home/solver/solve.py).
lnk.target_path_windows = LinkInfo LocalBasePath (+ CommonPathSuffix; the Unicode offsets when LinkInfoHeaderSize >=
0x24), else the path the LinkTargetIDList spells (volume item + file-entry long names from the 0xBEEF0004 extension),
joined with backslashes VERBATIM (D14: a System32 executable in all 4 variants; LinkInfo and IDList agreed).
The other lnk.* fields stay speculative in lib/meta/prebuilt/lnk.py."""


def _cstr(b, off, wide=False):
    if wide:
        end = off
        while end + 1 < len(b) and b[end:end + 2] != b"\0\0":
            end += 2
        return b[off:end].decode("utf-16-le", "replace")
    end = b.find(b"\0", off)
    return b[off:end if end >= 0 else len(b)].decode("cp1252", "replace")


def _idlist_path(b, off, end):
    """Rebuild a filesystem path from the shell IDList: volume item ('/C:\\') + file-entry items (long name)."""
    parts = []
    while off + 2 <= end:
        n = int.from_bytes(b[off:off + 2], "little")
        if n < 2:
            break
        it = b[off:off + n]
        t = it[2] if len(it) > 2 else 0
        if t & 0x70 == 0x20 and len(it) > 3:          # volume / drive
            parts = [_cstr(it, 3).rstrip("\\")]
        elif t & 0x70 == 0x30 and len(it) > 14:       # file entry: short name, then beef0004 long name
            name = _cstr(it, 14, bool(t & 0x04))
            k = it.find(b"\x04\x00\xef\xbe")
            if k >= 4:
                ver = int.from_bytes(it[k - 2:k], "little")
                # extension block: size(2) ver(2) sig(4) ctime(4) atime(4) id(2) [unk 2 + mft 8 if ver>=7]
                # [nameoff 2 if ver>=3] [4 if ver>=9]
                lo = k + 4 + 4 + 4 + 2 + (10 if ver >= 7 else 0) + (2 if ver >= 3 else 0) + (4 if ver >= 9 else 0)
                ln = _cstr(it, lo, True) if lo < len(it) else ""
                if ln:
                    name = ln
            parts.append(name)
        off += n
    return "\\".join(parts) if parts else None


def lnk_target_path(b):
    """The shortcut's target path, or None (not a shell link / no LinkInfo local path and no IDList path)."""
    if len(b) < 0x4C or b[:4] != b"\x4c\0\0\0":
        return None
    flags = int.from_bytes(b[0x14:0x18], "little")
    off = 0x4C
    idl = None
    if flags & 1:
        n = int.from_bytes(b[off:off + 2], "little")
        idl = (off + 2, off + 2 + n)
        off += 2 + n
    if flags & 2 and off + 0x1C <= len(b):
        li = b[off:off + int.from_bytes(b[off:off + 4], "little")]
        hs = int.from_bytes(li[4:8], "little")
        lflags = int.from_bytes(li[8:12], "little")
        if lflags & 1:
            if hs >= 0x24 and int.from_bytes(li[0x1C:0x20], "little"):
                base = _cstr(li, int.from_bytes(li[0x1C:0x20], "little"), True)
            else:
                base = _cstr(li, int.from_bytes(li[0x10:0x14], "little"))
            if hs >= 0x24 and int.from_bytes(li[0x20:0x24], "little"):
                suf = _cstr(li, int.from_bytes(li[0x20:0x24], "little"), True)
            else:
                so = int.from_bytes(li[0x18:0x1C], "little")
                suf = _cstr(li, so) if so else ""
            if base or suf:
                return base + ("\\" if base and suf and not base.endswith("\\") else "") + suf
    if idl:
        return _idlist_path(b, *idl)
    return None


def target_path(data, ctx):
    if data is None:
        return None
    try:
        return lnk_target_path(bytes(data))
    except Exception:  # noqa: BLE001 - malformed link: no answer
        return None
