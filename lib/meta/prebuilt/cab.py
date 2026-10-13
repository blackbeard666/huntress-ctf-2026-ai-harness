"""Microsoft Cabinet (MSCF) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

CFHEADER (MS-CAB 2.1, all little-endian): "MSCF" signature u32, reserved1 u32, cbCabinet u32 (total cabinet size),
reserved2 u32, coffFiles u32 (ABSOLUTE offset of the first CFFILE), reserved3 u32, versionMinor u8, versionMajor u8
(always 1.3), cFolders u16, cFiles u16, flags u16 (1 PREV_CABINET, 2 NEXT_CABINET, 4 RESERVE_PRESENT), setID u16,
iCabinet u16. CFFILE = cbFile u32, uoffFolderStart u32, iFolder u16, date u16, time u16, attribs u16, szName (NUL).
szName is the STORED name (backslash separators kept, like `gcab -t`; 7-Zip rewrites them to '/'); attrib 0x80
(_A_NAME_IS_UTF) = UTF-8, else the spec's "current code page" (cp1252 here).
Header values come from CFHEADER, not from counting (cFolders/cFiles are the asked fields; a spanned cabinet's
CFFILE count can differ from what a lister shows). Not MSCF / truncated header -> "none"."""
import struct

from ..spell import Hex

FIELDS = {
    ("cab", "cfheader_folder_count"): "header_value",
    ("cab", "folder_count"): "header_value",
    ("cab", "cfolders"): "header_value",
    ("cab", "cfheader_cfolders"): "header_value",
    ("cab", "cfheader_file_count"): "header_value",
    ("cab", "file_count"): "header_value",
    ("cab", "cfiles"): "header_value",
    ("cab", "cfheader_cfiles"): "header_value",
    ("cab", "cfheader_set_id_u16_hex"): "header_value",
    ("cab", "set_id_u16_hex"): "header_value",
    ("cab", "setid_u16_hex"): "header_value",
    ("cab", "cfheader_setid_u16_hex"): "header_value",
    ("cab", "cabinet_size_bytes"): "header_value",
    ("cab", "cfheader_cabinet_size_bytes"): "header_value",
    ("cab", "cb_cabinet"): "header_value",
    ("cab", "cfheader_cb_cabinet"): "header_value",
    ("cab", "version"): "header_value",
    ("cab", "cfheader_version"): "header_value",
    ("cab", "format_version"): "header_value",
    ("cab", "cfheader_flags_u16_hex"): "header_value",
    ("cab", "flags_u16_hex"): "header_value",
    ("cab", "cfheader_cabinet_index"): "header_value",
    ("cab", "cabinet_index"): "header_value",
    ("cab", "member_names"): "member_names",
    ("cab", "cffile_names"): "member_names",
    ("cab", "file_names"): "member_names",
}

_HDR = "<4sIIIIIBBHHHHH"   # 36 bytes


def cfheader(b):
    """CFHEADER as a dict, or None (not a cabinet / truncated)."""
    if not b or len(b) < 36 or bytes(b[:4]) != b"MSCF":
        return None
    (_, _, cb, _, coff, _, vmin, vmaj, nfold, nfile, flags, setid, icab) = struct.unpack_from(_HDR, b, 0)
    return {"cb_cabinet": cb, "coff_files": coff, "version": "%d.%d" % (vmaj, vmin), "folders": nfold,
            "files": nfile, "flags": flags, "set_id": setid, "index": icab}


def header_value(data, ctx):
    if data is None:
        return None
    try:
        h = cfheader(data)
    except Exception:
        return None
    if h is None:
        return "none"
    f = ctx.get("field") or ""
    if "folder" in f:
        return h["folders"]
    if "file" in f:
        return h["files"]
    if "set" in f:
        return Hex(h["set_id"], 4)
    if "size" in f or "cb_cabinet" in f:
        return h["cb_cabinet"]
    if "flags" in f:
        return Hex(h["flags"], 4)
    if "index" in f:
        return h["index"]
    if "version" in f:
        return h["version"]
    return None


def cffile_names(b):
    """Stored CFFILE szName values in table order, or None."""
    h = cfheader(b)
    if h is None:
        return None
    off, out = h["coff_files"], []
    for _ in range(h["files"]):
        if off + 16 > len(b):
            break
        attribs, = struct.unpack_from("<H", b, off + 14)
        end = b.find(b"\x00", off + 16, off + 16 + 1024)
        if end < 0:
            break
        raw = bytes(b[off + 16:end])
        out.append(raw.decode("utf-8" if attribs & 0x80 else "cp1252", "replace"))
        off = end + 1
    return out


def member_names(data, ctx):
    if data is None:
        return None
    try:
        names = cffile_names(data)
    except Exception:
        return None
    return "none" if names is None else names
