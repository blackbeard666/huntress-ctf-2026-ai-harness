"""Windows Jump List (`<AppID>.customDestinations-ms`) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

A CustomDestinations jump list is NOT a CFB: it is a flat little-endian stream of concatenated MS-SHLLINK files
(libyal "Jump lists format" / plaso custom_destinations.yaml + custom_destinations.py):
  file header 12 B: format_version u32 (= 2), number_of_categories u32, unknown u32.
  per category: category_type u32 --
    0 custom:  name_chars u16, name UTF-16LE, number_of_entries u32
    1 known:   category_identifier u32 (1 = KDC_FREQUENT, 2 = KDC_RECENT), no entries
    2 tasks:   number_of_entries u32
  then entries: 16-B CLSID 00021401-0000-0000-C000-000000000046 (`01 14 02 00 .. 46`) + a full LNK each;
  each category ends with the footer signature `ab fb bf ba`.
The AppID is NOT stored inside: it is the 16-hex-digit member file name stem (CRC-64 of the AppUserModelID).
LNK size = walked from its own structure (header, IDList, LinkInfo, StringData, ExtraData until the terminal block).
When the structural walk breaks (damaged/odd category), fall back to carving every `4c000000 + LNK CLSID` header in
file order. Lists keep file order, except category_names which is sorted (a set of labels; GM spec note).
target_path per LNK = lnk.target_path rules (LinkInfo LocalBasePath+suffix, else env block, else IDList path).
Not a v2 custom-destinations stream / no LNK and no category -> "none"."""
import re
import struct

from . import lnk as _lnk

FIELDS = {
    ("customdestinations", "app_id"): "customdestinations_value",
    ("customdestinations", "appid"): "customdestinations_value",
    ("customdestinations", "application_id"): "customdestinations_value",
    ("customdestinations", "app_id_hex"): "customdestinations_value",
    ("customdestinations", "format_version"): "customdestinations_value",
    ("customdestinations", "version"): "customdestinations_value",
    ("customdestinations", "header_version"): "customdestinations_value",
    ("customdestinations", "file_header_version"): "customdestinations_value",
    ("customdestinations", "category_count"): "customdestinations_value",
    ("customdestinations", "number_of_categories"): "customdestinations_value",
    ("customdestinations", "header_category_count"): "customdestinations_value",
    ("customdestinations", "categories_count"): "customdestinations_value",
    ("customdestinations", "entry_count"): "customdestinations_value",
    ("customdestinations", "number_of_entries"): "customdestinations_value",
    ("customdestinations", "entries_count"): "customdestinations_value",
    ("customdestinations", "lnk_count"): "customdestinations_value",
    ("customdestinations", "lnk_entry_count"): "customdestinations_value",
    ("customdestinations", "embedded_lnk_count"): "customdestinations_value",
    ("customdestinations", "lnk_target_paths"): "customdestinations_value",
    ("customdestinations", "target_paths"): "customdestinations_value",
    ("customdestinations", "entry_paths"): "customdestinations_value",
    ("customdestinations", "entry_target_paths"): "customdestinations_value",
    ("customdestinations", "first_target_path"): "customdestinations_value",
    ("customdestinations", "first_lnk_target_path"): "customdestinations_value",
    ("customdestinations", "first_entry_target_path"): "customdestinations_value",
    ("customdestinations", "category_names"): "customdestinations_value",
    ("customdestinations", "custom_category_names"): "customdestinations_value",
    ("customdestinations", "category_types"): "customdestinations_value",
    ("customdestinations", "known_category_ids"): "customdestinations_value",
    ("customdestinations", "known_categories"): "customdestinations_value",
    ("customdestinations", "task_count"): "customdestinations_value",
    ("customdestinations", "task_entry_count"): "customdestinations_value",
    ("customdestinations", "tasks_entry_count"): "customdestinations_value",
    ("customdestinations", "has_footer"): "customdestinations_value",
    ("customdestinations", "footer_present"): "customdestinations_value",
    ("customdestinations", "has_category_footer"): "customdestinations_value",
    ("custom_destinations", "app_id"): "customdestinations_value",
    ("custom_destinations", "appid"): "customdestinations_value",
    ("custom_destinations", "application_id"): "customdestinations_value",
    ("custom_destinations", "app_id_hex"): "customdestinations_value",
    ("custom_destinations", "format_version"): "customdestinations_value",
    ("custom_destinations", "version"): "customdestinations_value",
    ("custom_destinations", "header_version"): "customdestinations_value",
    ("custom_destinations", "file_header_version"): "customdestinations_value",
    ("custom_destinations", "category_count"): "customdestinations_value",
    ("custom_destinations", "number_of_categories"): "customdestinations_value",
    ("custom_destinations", "header_category_count"): "customdestinations_value",
    ("custom_destinations", "categories_count"): "customdestinations_value",
    ("custom_destinations", "entry_count"): "customdestinations_value",
    ("custom_destinations", "number_of_entries"): "customdestinations_value",
    ("custom_destinations", "entries_count"): "customdestinations_value",
    ("custom_destinations", "lnk_count"): "customdestinations_value",
    ("custom_destinations", "lnk_entry_count"): "customdestinations_value",
    ("custom_destinations", "embedded_lnk_count"): "customdestinations_value",
    ("custom_destinations", "lnk_target_paths"): "customdestinations_value",
    ("custom_destinations", "target_paths"): "customdestinations_value",
    ("custom_destinations", "entry_paths"): "customdestinations_value",
    ("custom_destinations", "entry_target_paths"): "customdestinations_value",
    ("custom_destinations", "first_target_path"): "customdestinations_value",
    ("custom_destinations", "first_lnk_target_path"): "customdestinations_value",
    ("custom_destinations", "first_entry_target_path"): "customdestinations_value",
    ("custom_destinations", "category_names"): "customdestinations_value",
    ("custom_destinations", "custom_category_names"): "customdestinations_value",
    ("custom_destinations", "category_types"): "customdestinations_value",
    ("custom_destinations", "known_category_ids"): "customdestinations_value",
    ("custom_destinations", "known_categories"): "customdestinations_value",
    ("custom_destinations", "task_count"): "customdestinations_value",
    ("custom_destinations", "task_entry_count"): "customdestinations_value",
    ("custom_destinations", "tasks_entry_count"): "customdestinations_value",
    ("custom_destinations", "has_footer"): "customdestinations_value",
    ("custom_destinations", "footer_present"): "customdestinations_value",
    ("custom_destinations", "has_category_footer"): "customdestinations_value",
    ("jumplist_custom", "app_id"): "customdestinations_value",
    ("jumplist_custom", "appid"): "customdestinations_value",
    ("jumplist_custom", "application_id"): "customdestinations_value",
    ("jumplist_custom", "app_id_hex"): "customdestinations_value",
    ("jumplist_custom", "format_version"): "customdestinations_value",
    ("jumplist_custom", "version"): "customdestinations_value",
    ("jumplist_custom", "header_version"): "customdestinations_value",
    ("jumplist_custom", "file_header_version"): "customdestinations_value",
    ("jumplist_custom", "category_count"): "customdestinations_value",
    ("jumplist_custom", "number_of_categories"): "customdestinations_value",
    ("jumplist_custom", "header_category_count"): "customdestinations_value",
    ("jumplist_custom", "categories_count"): "customdestinations_value",
    ("jumplist_custom", "entry_count"): "customdestinations_value",
    ("jumplist_custom", "number_of_entries"): "customdestinations_value",
    ("jumplist_custom", "entries_count"): "customdestinations_value",
    ("jumplist_custom", "lnk_count"): "customdestinations_value",
    ("jumplist_custom", "lnk_entry_count"): "customdestinations_value",
    ("jumplist_custom", "embedded_lnk_count"): "customdestinations_value",
    ("jumplist_custom", "lnk_target_paths"): "customdestinations_value",
    ("jumplist_custom", "target_paths"): "customdestinations_value",
    ("jumplist_custom", "entry_paths"): "customdestinations_value",
    ("jumplist_custom", "entry_target_paths"): "customdestinations_value",
    ("jumplist_custom", "first_target_path"): "customdestinations_value",
    ("jumplist_custom", "first_lnk_target_path"): "customdestinations_value",
    ("jumplist_custom", "first_entry_target_path"): "customdestinations_value",
    ("jumplist_custom", "category_names"): "customdestinations_value",
    ("jumplist_custom", "custom_category_names"): "customdestinations_value",
    ("jumplist_custom", "category_types"): "customdestinations_value",
    ("jumplist_custom", "known_category_ids"): "customdestinations_value",
    ("jumplist_custom", "known_categories"): "customdestinations_value",
    ("jumplist_custom", "task_count"): "customdestinations_value",
    ("jumplist_custom", "task_entry_count"): "customdestinations_value",
    ("jumplist_custom", "tasks_entry_count"): "customdestinations_value",
    ("jumplist_custom", "has_footer"): "customdestinations_value",
    ("jumplist_custom", "footer_present"): "customdestinations_value",
    ("jumplist_custom", "has_category_footer"): "customdestinations_value",
}

_CLSID = bytes.fromhex("0114020000000000c000000000000046")
_LNK_HDR = b"\x4c\0\0\0" + _CLSID
_FOOTER = b"\xab\xfb\xbf\xba"
_APPID = re.compile(r"(?:^|[\\/])([0-9a-fA-F]{16})\.customdestinations-ms$", re.I)
_KNOWN = {1: "KDC_FREQUENT", 2: "KDC_RECENT"}


def lnk_size(b, off):
    """Byte length of the MS-SHLLINK starting at b[off], walked from its own structure, or None."""
    if b[off:off + 20] != _LNK_HDR:
        return None
    flags, = struct.unpack_from("<I", b, off + 0x14)
    p = off + 0x4C
    if flags & 0x1:
        n, = struct.unpack_from("<H", b, p)
        p += 2 + n
    if flags & 0x2:
        n, = struct.unpack_from("<I", b, p)
        if n < 4:
            return None
        p += n
    unit = 2 if flags & 0x80 else 1
    for bit in (0x4, 0x8, 0x10, 0x20, 0x40):
        if flags & bit:
            n, = struct.unpack_from("<H", b, p)
            p += 2 + n * unit
    while True:
        sz, = struct.unpack_from("<I", b, p)
        p += 4
        if sz < 4:
            break
        p += sz - 4
    return p - off if p <= len(b) else None


def _walk(b):
    """Structural walk per plaso custom_destinations: dict or None when the stream does not follow the layout."""
    ver, ncat, _ = struct.unpack_from("<III", b, 0)
    if ver != 2 or ncat > 4096:
        return None
    off, cats, lnks = 12, [], []
    for _ in range(ncat):
        ctype, = struct.unpack_from("<I", b, off)
        off += 4
        name = cid = None
        if ctype == 0:
            nch, = struct.unpack_from("<H", b, off)
            raw = b[off + 2:off + 2 + nch * 2]
            if len(raw) < nch * 2:
                return None
            name = raw.decode("utf-16-le", "replace").rstrip("\0")
            off += 2 + nch * 2
            nent, = struct.unpack_from("<I", b, off)
            off += 4
        elif ctype == 1:
            cid, = struct.unpack_from("<I", b, off)
            off += 4
            nent = 0
        elif ctype == 2:
            nent, = struct.unpack_from("<I", b, off)
            off += 4
        else:
            return None
        got = 0
        for _ in range(nent):
            if b[off:off + 16] != _CLSID:
                break
            n = lnk_size(b, off + 16)
            if n is None:
                return None
            lnks.append(b[off + 16:off + 16 + n])
            off += 16 + n
            got += 1
        if b[off:off + 4] != _FOOTER:
            return None
        off += 4
        cats.append({"type": ctype, "name": name, "id": cid, "entries": got})
    return {"version": ver, "ncat": ncat, "cats": cats, "lnks": lnks}


def _carve(b):
    """Fallback: every embedded LNK header in file order (ver must still be 2)."""
    ver, ncat, _ = struct.unpack_from("<III", b, 0)
    if ver != 2:
        return None
    lnks, i = [], b.find(_LNK_HDR, 12)
    while i >= 0:
        n = None
        try:
            n = lnk_size(b, i)
        except struct.error:
            pass
        j = b.find(_LNK_HDR, i + 20)
        lnks.append(b[i:i + n] if n else b[i:j if j > 0 else len(b)])
        i = b.find(_LNK_HDR, i + (n or 20))
    if not lnks:
        return None
    return {"version": ver, "ncat": ncat, "cats": None, "lnks": lnks}


def parse(b):
    if not b or len(b) < 12:
        return None
    try:
        j = _walk(b)
    except struct.error:
        j = None
    if j is None or (not j["lnks"] and not j["cats"]):
        j = _carve(b)
    if j is None:
        return None
    j["footer"] = b.endswith(_FOOTER)
    return j


def _pick(j, f, member):
    if f.startswith("app") or f == "application_id":
        m = _APPID.search(member or "")
        return m.group(1).lower() if m else "none"
    if "version" in f:
        return j["version"]
    if f.startswith("categor") or f in ("number_of_categories", "header_category_count"):
        if f.endswith("count") or f == "number_of_categories":
            return j["ncat"]
    if "footer" in f:
        return j["footer"]
    paths = [_lnk._pick(r, "target_path") if r is not None else "none" for r in map(_lnk.parse, j["lnks"])]
    if "path" in f:
        if f.startswith("first"):
            return paths[0] if paths else "none"
        return paths
    if f.startswith("task"):
        if j["cats"] is None:
            return None
        return sum(c["entries"] for c in j["cats"] if c["type"] == 2)
    if f.endswith("count") or f == "number_of_entries":
        return len(j["lnks"])
    if j["cats"] is None:
        return None
    if "names" in f:
        return sorted(c["name"] for c in j["cats"] if c["type"] == 0)
    if f == "category_types":
        return [c["type"] for c in j["cats"]]
    if f == "known_category_ids":
        return [c["id"] for c in j["cats"] if c["type"] == 1]
    if f == "known_categories":
        return [_KNOWN.get(c["id"], str(c["id"])) for c in j["cats"] if c["type"] == 1]
    return None


def customdestinations_value(data, ctx):
    if data is None:
        return None
    try:
        j = parse(bytes(data))
        if j is None:
            return "none"
        return _pick(j, ctx.get("field") or "", ctx.get("member") or "")
    except Exception:
        return None
