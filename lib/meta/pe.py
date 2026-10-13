"""PE (and ELF header) fields. COPIED from the GM-verified D9 (pe.coff_machine_u16_hex), D10
(pe.address_of_entry_point_rva_hex) and D11 (pe.version_<key> via pefile) solvers. No real PE header -> "none" (decoys).
The image_base / optional-header magic / ELF fields were in the D10 solver but never asked: speculative tier."""
import re
import struct

from .spell import Hex


def pe_offsets(d):
    """(e_lfanew, optional-header offset) or None when MZ -> e_lfanew -> 'PE\\0\\0' is absent."""
    if not d or d[:2] != b"MZ" or len(d) < 0x40:
        return None
    o = struct.unpack_from("<I", d, 0x3C)[0]
    if o + 6 > len(d) or d[o:o + 4] != b"PE\0\0":
        return None
    return o, o + 24


def coff_machine(data, ctx):
    if data is None:
        return None
    p = pe_offsets(data)
    return Hex(struct.unpack_from("<H", data, p[0] + 4)[0], 4) if p else "none"


def _opt(d):
    p = pe_offsets(d)
    if p is None or p[1] + 20 > len(d):
        return None
    return p[1]


def entry_point_rva(data, ctx):
    if data is None:
        return None
    o = _opt(data)
    return Hex(struct.unpack_from("<I", data, o + 16)[0], 8) if o is not None else "none"


def image_base(data, ctx):
    if data is None:
        return None
    o = _opt(data)
    if o is None:
        return "none"
    if struct.unpack_from("<H", data, o)[0] == 0x20B:
        return Hex(struct.unpack_from("<Q", data, o + 24)[0], 16)
    return Hex(struct.unpack_from("<I", data, o + 28)[0], 8)


def optional_header_magic(data, ctx):
    if data is None:
        return None
    o = _opt(data)
    return Hex(struct.unpack_from("<H", data, o)[0], 4) if o is not None else "none"


def _key(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def version_strings(data):
    """VS_VERSIONINFO StringFileInfo {key: value} via pefile (fast_load + the RESOURCE directory only)."""
    import pefile
    pe = pefile.PE(data=data, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
    out = {}
    for fi in getattr(pe, "FileInfo", None) or []:
        for e in (fi if isinstance(fi, list) else [fi]):
            for st in getattr(e, "StringTable", []) or []:
                for k, v in st.entries.items():
                    k = k.decode("utf-8", "replace") if isinstance(k, bytes) else k
                    v = v.decode("utf-8", "replace") if isinstance(v, bytes) else v
                    out.setdefault(k, v)
    return out


def version_string(data, ctx):
    """pe.version_<key>: the StringFileInfo entry whose key matches <key> case/separator-insensitively, VERBATIM."""
    if data is None:
        return None
    if data[:2] != b"MZ":
        return "none"
    field = ctx.get("field") or ""
    want = _key(ctx.get("param") or field.split("version_", 1)[-1])
    for k, v in version_strings(data).items():
        if _key(k) == want:
            return v
    return "none"


def elf_machine(data, ctx):
    if data is None:
        return None
    if data[:4] != b"\x7fELF" or len(data) < 20:
        return "none"
    return Hex(struct.unpack_from("<H" if data[5] != 2 else ">H", data, 18)[0], 4)


def elf_entry(data, ctx):
    if data is None:
        return None
    if data[:4] != b"\x7fELF" or len(data) < 0x40:
        return "none"
    e = "<" if data[5] != 2 else ">"
    if data[4] == 2:
        return Hex(struct.unpack_from(e + "Q", data, 24)[0], 16)
    return Hex(struct.unpack_from(e + "I", data, 24)[0], 8)
