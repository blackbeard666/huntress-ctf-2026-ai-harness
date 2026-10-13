"""PE COFF file-header / optional-header fields + the section table (prebuilt, SPECULATIVE).

Layout (PE/COFF spec): e_lfanew -> 'PE\\0\\0'; COFF header at +4: Machine(+0) NumberOfSections(+2) TimeDateStamp(+4)
PointerToSymbolTable(+8) NumberOfSymbols(+12) SizeOfOptionalHeader(+16) Characteristics(+18). Optional header at +24:
the fields below sit at the SAME offset in PE32 (0x10b) and PE32+ (0x20b): SectionAlignment 32, FileAlignment 36,
SizeOfImage 56, SizeOfHeaders 60, CheckSum 64, Subsystem 68, DllCharacteristics 70. Section table = optional header +
SizeOfOptionalHeader, 40-byte entries, Name = 8 bytes NUL-padded (a COFF "/4" long-name reference is kept as stored,
like pefile / objdump -h on an image). Values are the STORED header fields (CheckSum is not recomputed).
No MZ -> PE signature (decoy / renamed / truncated) -> "none"."""
import struct

from ..pe import pe_offsets
from ..spell import Hex

FIELDS = {
    ("pe", "time_date_stamp_u32_hex"): "time_date_stamp",
    ("pe", "coff_time_date_stamp_u32_hex"): "time_date_stamp",
    ("pe", "timedatestamp_u32_hex"): "time_date_stamp",
    ("pe", "time_date_stamp_utc"): "time_date_stamp_utc",
    ("pe", "time_date_stamp_iso8601"): "time_date_stamp_utc",
    ("pe", "coff_time_date_stamp_utc"): "time_date_stamp_utc",
    ("pe", "number_of_sections"): "number_of_sections",
    ("pe", "coff_number_of_sections"): "number_of_sections",
    ("pe", "section_count"): "number_of_sections",
    ("pe", "characteristics_u16_hex"): "characteristics",
    ("pe", "coff_characteristics_u16_hex"): "characteristics",
    ("pe", "file_header_characteristics_u16_hex"): "characteristics",
    ("pe", "subsystem_u16_hex"): "subsystem",
    ("pe", "optional_header_subsystem_u16_hex"): "subsystem",
    ("pe", "dll_characteristics_u16_hex"): "dll_characteristics",
    ("pe", "optional_header_dll_characteristics_u16_hex"): "dll_characteristics",
    ("pe", "size_of_image_u32_hex"): "size_of_image",
    ("pe", "optional_header_size_of_image_u32_hex"): "size_of_image",
    ("pe", "size_of_image_bytes"): "size_of_image_bytes",
    ("pe", "checksum_u32_hex"): "checksum",
    ("pe", "check_sum_u32_hex"): "checksum",
    ("pe", "optional_header_checksum_u32_hex"): "checksum",
    ("pe", "size_of_headers_u32_hex"): "size_of_headers",
    ("pe", "section_alignment_u32_hex"): "section_alignment",
    ("pe", "file_alignment_u32_hex"): "file_alignment",
    ("pe", "section_names"): "section_names",
    ("pe", "section_table_names"): "section_names",
    ("pe", "fixed_file_version"): "fixed_file_version",
    ("pe", "fixed_file_info_file_version"): "fixed_file_version",
    ("pe", "vs_fixedfileinfo_file_version"): "fixed_file_version",
    ("pe", "fixed_file_version_number"): "fixed_file_version",
    ("pe", "file_version_number"): "fixed_file_version",
    ("pe", "fixed_product_version"): "fixed_product_version",
    ("pe", "fixed_file_info_product_version"): "fixed_product_version",
    ("pe", "vs_fixedfileinfo_product_version"): "fixed_product_version",
    ("pe", "fixed_product_version_number"): "fixed_product_version",
    ("pe", "product_version_number"): "fixed_product_version",
    ("pe", "fixed_file_flags_u32_hex"): "fixed_file_flags",
    ("pe", "fixed_file_info_file_flags_u32_hex"): "fixed_file_flags",
    ("pe", "vs_fixedfileinfo_file_flags_u32_hex"): "fixed_file_flags",
    ("pe", "fixed_file_flags_mask_u32_hex"): "fixed_file_flags_mask",
    ("pe", "fixed_file_os_u32_hex"): "fixed_file_os",
    ("pe", "fixed_file_info_file_os_u32_hex"): "fixed_file_os",
    ("pe", "vs_fixedfileinfo_file_os_u32_hex"): "fixed_file_os",
    ("pe", "fixed_file_type_u32_hex"): "fixed_file_type",
    ("pe", "fixed_file_subtype_u32_hex"): "fixed_file_subtype",
}


def _coff(d, off, fmt):
    """struct field at COFF-header offset `off` (after 'PE\\0\\0'), or None (no PE / truncated)."""
    try:
        p = pe_offsets(d)
        if p is None or p[0] + 24 > len(d):
            return None
        return struct.unpack_from(fmt, d, p[0] + 4 + off)[0]
    except (struct.error, TypeError, IndexError):
        return None


def _opt(d, off, fmt):
    """struct field at optional-header offset `off` (PE32/PE32+ common prefix), or None."""
    try:
        p = pe_offsets(d)
        if p is None or p[1] + off + struct.calcsize(fmt) > len(d):
            return None
        if struct.unpack_from("<H", d, p[1])[0] not in (0x10B, 0x20B, 0x107):
            return None
        return struct.unpack_from(fmt, d, p[1] + off)[0]
    except (struct.error, TypeError, IndexError):
        return None


def _hex(v, w):
    return "none" if v is None else Hex(v, w)


def time_date_stamp(data, ctx):
    return None if data is None else _hex(_coff(data, 4, "<I"), 8)


def time_date_stamp_utc(data, ctx):
    """TimeDateStamp is a u32 UNIX epoch (seconds since 1970-01-01 UTC) -> ISO-8601 'YYYY-MM-DDTHH:MM:SSZ'.
    (Reproducible builds store a hash here; it is still rendered as the epoch value it claims to be.)"""
    if data is None:
        return None
    v = _coff(data, 4, "<I")
    if v is None:
        return "none"
    import datetime
    return datetime.datetime.fromtimestamp(v, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def number_of_sections(data, ctx):
    if data is None:
        return None
    v = _coff(data, 2, "<H")
    return "none" if v is None else v


def characteristics(data, ctx):
    return None if data is None else _hex(_coff(data, 18, "<H"), 4)


def subsystem(data, ctx):
    return None if data is None else _hex(_opt(data, 68, "<H"), 4)


def dll_characteristics(data, ctx):
    return None if data is None else _hex(_opt(data, 70, "<H"), 4)


def size_of_image(data, ctx):
    return None if data is None else _hex(_opt(data, 56, "<I"), 8)


def size_of_image_bytes(data, ctx):
    if data is None:
        return None
    v = _opt(data, 56, "<I")
    return "none" if v is None else v


def checksum(data, ctx):
    return None if data is None else _hex(_opt(data, 64, "<I"), 8)


def size_of_headers(data, ctx):
    return None if data is None else _hex(_opt(data, 60, "<I"), 8)


def section_alignment(data, ctx):
    return None if data is None else _hex(_opt(data, 32, "<I"), 8)


def file_alignment(data, ctx):
    return None if data is None else _hex(_opt(data, 36, "<I"), 8)


def section_names(data, ctx):
    """Section-table Name fields in table order (JSON list), NUL padding stripped; a truncated table -> None."""
    if data is None:
        return None
    try:
        p = pe_offsets(data)
        if p is None or p[0] + 24 > len(data):
            return "none"
        n = struct.unpack_from("<H", data, p[0] + 6)[0]
        sopt = struct.unpack_from("<H", data, p[0] + 20)[0]
        base = p[1] + sopt
        if base + 40 * n > len(data):
            return None
        out = []
        for i in range(n):
            raw = data[base + 40 * i:base + 40 * i + 8].split(b"\0", 1)[0]
            out.append(raw.decode("utf-8", "replace"))
        return out
    except (struct.error, TypeError, IndexError):
        return None


# VS_FIXEDFILEINFO (the binary half of VS_VERSIONINFO; the StringFileInfo strings are pe.version_* in lib/meta/pe.py).
# 13 DWORDs: dwSignature 0xFEEF04BD, dwStrucVersion, dwFileVersionMS, LS, dwProductVersionMS, LS, dwFileFlagsMask,
# dwFileFlags, dwFileOS, dwFileType, dwFileSubtype, dwFileDateMS, LS. Versions are MS hi.lo . LS hi.lo in base 10 --
# NOT the StringFileInfo FileVersion/ProductVersion text (often "x.y.z+commit" or a stale string: the classic decoy).
# Flags are the raw stored dwFileFlags (not masked with dwFileFlagsMask), like exiftool -n / pefile.
_FFI_SIG = b"\xbd\x04\xef\xfe"
_VSKEY = "VS_VERSION_INFO\0".encode("utf-16-le")


def _ffi_pefile(d):
    import pefile
    pe = pefile.PE(data=d, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
    for f in getattr(pe, "VS_FIXEDFILEINFO", None) or []:
        if getattr(f, "Signature", None) == 0xFEEF04BD:
            return tuple(getattr(f, n) for n in ("StrucVersion", "FileVersionMS", "FileVersionLS", "ProductVersionMS",
                                                  "ProductVersionLS", "FileFlagsMask", "FileFlags", "FileOS",
                                                  "FileType", "FileSubtype"))
    return None


def _ffi_scan(d):
    """Fallback (pefile refused a damaged resource tree): 'VS_VERSION_INFO' key -> DWORD-aligned Value."""
    i = d.find(_VSKEY)
    while i >= 6:
        o = (i + len(_VSKEY) + 3) & ~3
        if d[o:o + 4] == _FFI_SIG and o + 52 <= len(d):
            return struct.unpack_from("<10I", d, o + 4)
        i = d.find(_VSKEY, i + 2)
    return None


def _ffi(d):
    """The 10 DWORDs after dwSignature, "none" (a PE with no version resource / not a PE) or None."""
    if d is None:
        return None
    if pe_offsets(d) is None:
        return "none"
    try:
        v = _ffi_pefile(d)
    except Exception:
        v = None
    if v is None:
        try:
            v = _ffi_scan(d)
        except (struct.error, TypeError, ValueError):
            v = None
    return "none" if v is None else v


def _ver(ms, ls):
    return "%d.%d.%d.%d" % (ms >> 16, ms & 0xFFFF, ls >> 16, ls & 0xFFFF)


def fixed_file_version(data, ctx):
    v = _ffi(data)
    return v if not isinstance(v, tuple) else _ver(v[1], v[2])


def fixed_product_version(data, ctx):
    v = _ffi(data)
    return v if not isinstance(v, tuple) else _ver(v[3], v[4])


def _ffi_hex(data, i):
    v = _ffi(data)
    return v if not isinstance(v, tuple) else Hex(v[i], 8)


def fixed_file_flags_mask(data, ctx):
    return _ffi_hex(data, 5)


def fixed_file_flags(data, ctx):
    return _ffi_hex(data, 6)


def fixed_file_os(data, ctx):
    return _ffi_hex(data, 7)


def fixed_file_type(data, ctx):
    return _ffi_hex(data, 8)


def fixed_file_subtype(data, ctx):
    return _ffi_hex(data, 9)
