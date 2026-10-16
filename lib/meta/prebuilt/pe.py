"""PE COFF file-header / optional-header fields + the section table (prebuilt, SPECULATIVE).

Layout (PE/COFF spec): e_lfanew -> 'PE\\0\\0'; COFF header at +4: Machine(+0) NumberOfSections(+2) TimeDateStamp(+4)
PointerToSymbolTable(+8) NumberOfSymbols(+12) SizeOfOptionalHeader(+16) Characteristics(+18). Optional header at +24:
the fields below sit at the SAME offset in PE32 (0x10b) and PE32+ (0x20b): SectionAlignment 32, FileAlignment 36,
SizeOfImage 56, SizeOfHeaders 60, CheckSum 64, Subsystem 68, DllCharacteristics 70. Section table = optional header +
SizeOfOptionalHeader, 40-byte entries, Name = 8 bytes NUL-padded (a COFF "/4" long-name reference is kept as stored,
like pefile / objdump -h on an image). Values are the STORED header fields (CheckSum is not recomputed).
No MZ -> PE signature (decoy / renamed / truncated) -> "none"."""
import hashlib
import struct

from ..pe import pe_offsets
from ..spell import Guid, Hex

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
    ("pe", "timestamp_u32_hex"): "time_date_stamp",
    ("pe", "coff_timestamp_u32_hex"): "time_date_stamp",
    ("pe", "file_header_time_date_stamp_u32_hex"): "time_date_stamp",
    ("pe", "debug_pdb_path"): "debug_pdb_path",
    ("pe", "pdb_path"): "debug_pdb_path",
    ("pe", "codeview_pdb_path"): "debug_pdb_path",
    ("pe", "debug_codeview_pdb_path"): "debug_pdb_path",
    ("pe", "debug_codeview_path"): "debug_pdb_path",
    ("pe", "codeview_path"): "debug_pdb_path",
    ("pe", "rsds_pdb_path"): "debug_pdb_path",
    ("pe", "debug_pdb_file_name"): "debug_pdb_path",
    ("pe", "pdb_file_name"): "debug_pdb_path",
    ("pe", "debug_codeview_guid"): "debug_codeview_guid",
    ("pe", "codeview_guid"): "debug_codeview_guid",
    ("pe", "debug_pdb_guid"): "debug_codeview_guid",
    ("pe", "pdb_guid"): "debug_codeview_guid",
    ("pe", "rsds_guid"): "debug_codeview_guid",
    ("pe", "debug_guid"): "debug_codeview_guid",
    ("pe", "debug_codeview_signature_guid"): "debug_codeview_guid",
    ("pe", "debug_codeview_age"): "debug_codeview_age",
    ("pe", "codeview_age"): "debug_codeview_age",
    ("pe", "debug_pdb_age"): "debug_codeview_age",
    ("pe", "pdb_age"): "debug_codeview_age",
    ("pe", "rsds_age"): "debug_codeview_age",
    ("pe", "debug_age"): "debug_codeview_age",
    ("pe", "rich_header_hash_md5"): "rich_header_hash_md5",
    ("pe", "rich_header_md5"): "rich_header_hash_md5",
    ("pe", "rich_hash_md5"): "rich_header_hash_md5",
    ("pe", "rich_header_hash"): "rich_header_hash_md5",
    ("pe", "rich_hash"): "rich_header_hash_md5",
    ("pe", "rich_header_key_u32_hex"): "rich_header_key",
    ("pe", "rich_header_checksum_u32_hex"): "rich_header_key",
    ("pe", "rich_header_xor_key_u32_hex"): "rich_header_key",
    ("pe", "imphash"): "imphash",
    ("pe", "imphash_md5"): "imphash",
    ("pe", "import_hash"): "imphash",
    ("pe", "import_hash_md5"): "imphash",
    ("pe", "import_table_hash_md5"): "imphash",
    ("pe", "import_dll_names"): "import_dll_names",
    ("pe", "imported_dll_names"): "import_dll_names",
    ("pe", "import_library_names"): "import_dll_names",
    ("pe", "import_directory_dll_names"): "import_dll_names",
    ("pe", "import_table_dll_names"): "import_dll_names",
    ("pe", "import_descriptor_names"): "import_dll_names",
    ("pe", "import_names"): "import_dll_names",
    ("pe", "imported_dlls"): "import_dll_names",
    ("pe", "import_dlls"): "import_dll_names",
    ("pe", "import_dll_count"): "import_dll_count",
    ("pe", "import_descriptor_count"): "import_dll_count",
    ("pe", "export_names"): "export_names",
    ("pe", "exported_names"): "export_names",
    ("pe", "export_function_names"): "export_names",
    ("pe", "exported_function_names"): "export_names",
    ("pe", "export_directory_names"): "export_names",
    ("pe", "export_name_table"): "export_names",
    ("pe", "export_symbol_names"): "export_names",
    ("pe", "export_dll_name"): "export_dll_name",
    ("pe", "export_directory_name"): "export_dll_name",
    ("pe", "export_directory_dll_name"): "export_dll_name",
    ("pe", "export_count"): "export_count",
    ("pe", "export_name_count"): "export_count",
    ("pe", "export_number_of_names"): "export_count",
    ("pe", "is_signed"): "is_signed",
    ("pe", "has_authenticode_signature"): "is_signed",
    ("pe", "authenticode_is_signed"): "is_signed",
    ("pe", "is_authenticode_signed"): "is_signed",
    ("pe", "has_signature"): "is_signed",
    ("pe", "security_dir_size_u32_hex"): "security_dir_size",
    ("pe", "security_directory_size_u32_hex"): "security_dir_size",
    ("pe", "certificate_table_size_u32_hex"): "security_dir_size",
    ("pe", "data_directory_security_size_u32_hex"): "security_dir_size",
    ("pe", "security_dir_size_bytes"): "security_dir_size_bytes",
    ("pe", "security_directory_size_bytes"): "security_dir_size_bytes",
    ("pe", "certificate_table_size_bytes"): "security_dir_size_bytes",
    ("pe", "security_dir_offset_u32_hex"): "security_dir_offset",
    ("pe", "security_directory_offset_u32_hex"): "security_dir_offset",
    ("pe", "certificate_table_offset_u32_hex"): "security_dir_offset",
    ("pe", "signer_subject_cn"): "signer_subject_cn",
    ("pe", "signer_cn"): "signer_subject_cn",
    ("pe", "signer_common_name"): "signer_subject_cn",
    ("pe", "signer_cert_subject_cn"): "signer_subject_cn",
    ("pe", "signer_certificate_subject_cn"): "signer_subject_cn",
    ("pe", "authenticode_signer_cn"): "signer_subject_cn",
    ("pe", "authenticode_signer_subject_cn"): "signer_subject_cn",
    ("pe", "signer_issuer_cn"): "signer_issuer_cn",
    ("pe", "signer_cert_issuer_cn"): "signer_issuer_cn",
    ("pe", "signer_certificate_issuer_cn"): "signer_issuer_cn",
    ("pe", "authenticode_issuer_cn"): "signer_issuer_cn",
    ("pe", "authenticode_signer_issuer_cn"): "signer_issuer_cn",
    ("pe", "signer_serial_hex"): "signer_serial",
    ("pe", "signer_serial_number_hex"): "signer_serial",
    ("pe", "signer_cert_serial_hex"): "signer_serial",
    ("pe", "signer_cert_serial_number_hex"): "signer_serial",
    ("pe", "signer_certificate_serial_hex"): "signer_serial",
    ("pe", "signer_certificate_serial_number_hex"): "signer_serial",
    ("pe", "authenticode_signer_serial_hex"): "signer_serial",
    ("pe", "signer_cert_sha1"): "signer_cert_sha1",
    ("pe", "signer_cert_thumbprint"): "signer_cert_sha1",
    ("pe", "signer_cert_thumbprint_sha1"): "signer_cert_sha1",
    ("pe", "signer_thumbprint"): "signer_cert_sha1",
    ("pe", "signer_thumbprint_sha1"): "signer_cert_sha1",
    ("pe", "signer_certificate_sha1"): "signer_cert_sha1",
    ("pe", "signer_certificate_thumbprint"): "signer_cert_sha1",
    ("pe", "signer_cert_sha256"): "signer_cert_sha256",
    ("pe", "signer_thumbprint_sha256"): "signer_cert_sha256",
    ("pe", "signer_cert_thumbprint_sha256"): "signer_cert_sha256",
    ("pe", "signer_certificate_sha256"): "signer_cert_sha256",
    ("pe", "signing_time_utc"): "signing_time_utc",
    ("pe", "signing_time"): "signing_time_utc",
    ("pe", "signer_signing_time_utc"): "signing_time_utc",
    ("pe", "authenticode_signing_time_utc"): "signing_time_utc",
    ("pe", "signature_timestamp_utc"): "signing_time_utc",
    ("pe", "countersignature_time_utc"): "signing_time_utc",
    ("pe", "timestamp_time_utc"): "signing_time_utc",
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


# Data directories (debug / Rich / imports / exports), hand-parsed: e_lfanew -> optional header -> DataDirectory[]
# (PE32 at opt+96, PE32+ at opt+112; NumberOfRvaAndSizes just before) -> RVA -> file offset through the section table.
# Not a PE -> "none"; a PE without the directory -> "none"; a directory pointing outside the file -> None.
_DIR_EXPORT, _DIR_IMPORT, _DIR_DEBUG = 0, 1, 6


class _PE:
    def __init__(self, d):
        p = pe_offsets(d)
        if p is None or p[1] + 2 > len(d):
            raise ValueError("not a PE")
        self.d, opt = d, p[1]
        magic = struct.unpack_from("<H", d, opt)[0]
        self.pe64 = magic == 0x20B
        dd = opt + (112 if self.pe64 else 96)
        nrva = struct.unpack_from("<I", d, dd - 4)[0] if dd <= len(d) else 0
        self.dirs = []
        for i in range(min(nrva, 16)):
            if dd + 8 * i + 8 > len(d):
                break
            self.dirs.append(struct.unpack_from("<II", d, dd + 8 * i))
        self.size_of_headers = struct.unpack_from("<I", d, opt + 60)[0] if opt + 64 <= len(d) else 0
        falign = struct.unpack_from("<I", d, opt + 36)[0] if opt + 40 <= len(d) else 0
        self.amask = ~0x1FF if falign >= 0x200 else ~0     # PointerToRawData rounds down to 512 (loader/pefile rule)
        n = struct.unpack_from("<H", d, p[0] + 6)[0]
        base = opt + struct.unpack_from("<H", d, p[0] + 20)[0]
        self.secs = []
        for i in range(n):
            o = base + 40 * i
            if o + 40 > len(d):
                break
            vsize, va, rsize, rptr = struct.unpack_from("<IIII", d, o + 8)
            self.secs.append((va, max(vsize, rsize), rptr, rsize))

    def dir(self, i):
        """(rva, size) of data directory i, or None when absent/empty."""
        if i < len(self.dirs) and self.dirs[i][0]:
            return self.dirs[i]
        return None

    def off(self, rva):
        for va, span, rptr, rsize in self.secs:
            if va <= rva < va + span:
                o = rva - va + (rptr & self.amask)
                return o if o < len(self.d) else None
        return rva if rva < max(self.size_of_headers, 1) else None

    def u32(self, o):
        return struct.unpack_from("<I", self.d, o)[0]

    def cstr(self, rva_or_off, is_rva=True, limit=512):
        o = self.off(rva_or_off) if is_rva else rva_or_off
        if o is None or o >= len(self.d):
            return None
        return self.d[o:o + limit].split(b"\0", 1)[0]


def _pe(data):
    """_PE or "none" (not a PE) -- a parse error on a real PE is caught by each caller."""
    try:
        return _PE(data)
    except (ValueError, struct.error, TypeError, IndexError):
        return "none"


def _codeview(data):
    """(pdb_path_bytes, guid16|None, age) of the first IMAGE_DEBUG_TYPE_CODEVIEW (2) entry; "none" / None.
    RSDS (PDB 7.0): 'RSDS' GUID[16] Age(u32) PdbFileName(UTF-8, NUL); NB10 (PDB 2.0): 'NB10' Offset Signature Age path.
    The record is located by PointerToRawData (file offset) like dumpbin/pefile; AddressOfRawData is the fallback."""
    if data is None:
        return None
    pe = _pe(data)
    if pe == "none":
        return "none"
    try:
        dd = pe.dir(_DIR_DEBUG)
        if dd is None:
            return "none"
        base = pe.off(dd[0])
        if base is None:
            return None
        for i in range(max(dd[1], 28) // 28):
            o = base + 28 * i
            if o + 28 > len(data):
                break
            typ, size, rva, ptr = struct.unpack_from("<IIII", data, o + 12)
            if typ != 2:
                continue
            for c in (ptr, pe.off(rva) if rva else None):
                if c is None or c + 24 > len(data):
                    continue
                sig = data[c:c + 4]
                if sig == b"RSDS":
                    age = pe.u32(c + 20)
                    return data[c + 24:c + max(size, 25)].split(b"\0", 1)[0], data[c + 4:c + 20], age
                if sig == b"NB10" and c + 16 <= len(data):
                    return data[c + 16:c + max(size, 17)].split(b"\0", 1)[0], None, pe.u32(c + 12)
        return "none"
    except (struct.error, TypeError, IndexError):
        return None


def debug_pdb_path(data, ctx):
    """The PDB path exactly as stored in the CodeView record (no basename / case change)."""
    cv = _codeview(data)
    if not isinstance(cv, tuple):
        return cv
    return cv[0].decode("utf-8", "replace").strip() or "none"


def debug_codeview_guid(data, ctx):
    """RSDS Signature GUID: binary Windows GUID -> lowercase 8-4-4-4-12 (Data1-3 little-endian), no braces."""
    cv = _codeview(data)
    if not isinstance(cv, tuple):
        return cv
    return "none" if cv[1] is None else Guid("bytes_le", bytes(cv[1]))


def debug_codeview_age(data, ctx):
    """RSDS/NB10 Age (u32) in base 10."""
    cv = _codeview(data)
    return cv if not isinstance(cv, tuple) else cv[2]


def _rich(data):
    """(clear_data, key) as pefile/VirusTotal define it: 'Rich' searched from 0x80 up to the optional header, key =
    the u32 after it, clear_data = data[0x80:Rich] XOR key (repeating). The hash covers the DanS marker and padding."""
    if data is None:
        return None
    p = pe_offsets(data)
    if p is None:
        return "none"
    r = data.find(b"Rich", 0x80, p[1])
    if r < 0 or r + 8 > len(data) or (r - 0x80) % 4:
        return "none"
    key = data[r + 4:r + 8]
    raw = data[0x80:r]
    return bytes(b ^ key[i & 3] for i, b in enumerate(raw)), struct.unpack("<I", key)[0]


def rich_header_hash_md5(data, ctx):
    rh = _rich(data)
    if not isinstance(rh, tuple):
        return rh
    if not rh[0].startswith(b"DanS"):
        return "none"
    return hashlib.md5(rh[0]).hexdigest()


def rich_header_key(data, ctx):
    rh = _rich(data)
    return rh if not isinstance(rh, tuple) else Hex(rh[1], 8)


def _imports(data):
    """[(dll_bytes, [name_bytes | ordinal_int, ...])] of the import directory in descriptor order; "none" / None."""
    if data is None:
        return None
    pe = _pe(data)
    if pe == "none":
        return "none"
    try:
        dd = pe.dir(_DIR_IMPORT)
        if dd is None:
            return "none"
        o = pe.off(dd[0])
        if o is None:
            return None
        tsz, flag = (8, 1 << 63) if pe.pe64 else (4, 1 << 31)
        out = []
        while o + 20 <= len(data) and len(out) < 4096:
            oft, _, _, name, ft = struct.unpack_from("<IIIII", data, o)
            o += 20
            if not (oft or name or ft):
                break
            dll = pe.cstr(name) if name else None
            if not dll:
                continue
            funcs, t = [], pe.off(oft or ft)
            while t is not None and t + tsz <= len(data) and len(funcs) < 65536:
                v = int.from_bytes(data[t:t + tsz], "little")
                t += tsz
                if not v:
                    break
                if v & flag:
                    funcs.append(v & 0xFFFF)
                else:
                    nm = pe.cstr((v & 0x7FFFFFFF) + 2)
                    if nm:
                        funcs.append(nm)
            out.append((dll, funcs))
        return out
    except (struct.error, TypeError, IndexError):
        return None


def import_dll_names(data, ctx):
    """Import-descriptor DLL names in table order, as stored (case kept). Delay-load imports are not included."""
    imp = _imports(data)
    if not isinstance(imp, list):
        return imp
    return [d.decode("latin-1") for d, _ in imp] if imp else "none"


def import_dll_count(data, ctx):
    imp = _imports(data)
    return imp if not isinstance(imp, list) else len(imp)


def imphash(data, ctx):
    """Mandiant imphash as pefile.get_imphash(): md5 of ','.join('lib.func') over descriptors/thunks in order, lib =
    lowercased DLL name minus a .dll/.ocx/.sys extension, func lowercased; ordinals via ordlookup (ws2_32/wsock32/
    oleaut32 names, else 'ordN')."""
    imp = _imports(data)
    if not isinstance(imp, list):
        return imp
    if not imp:
        return "none"
    parts = []
    for dll, funcs in imp:
        lib = dll.decode("latin-1").lower()
        stem, dot, ext = lib.rpartition(".")
        if dot and ext in ("ocx", "sys", "dll"):
            lib = stem
        for f in funcs:
            if isinstance(f, int):
                from ordlookup import ordLookup
                f = ordLookup(dll.lower(), f, make_name=True)
                if not f:
                    return None
            if isinstance(f, bytes):
                f = f.decode("latin-1")
            parts.append("%s.%s" % (lib, f.lower()))
    return hashlib.md5(",".join(parts).encode()).hexdigest() if parts else "none"


def _exports(data):
    """(dll_name_bytes, [name_bytes in AddressOfNames order]) of the export directory; "none" / None."""
    if data is None:
        return None
    pe = _pe(data)
    if pe == "none":
        return "none"
    try:
        dd = pe.dir(_DIR_EXPORT)
        if dd is None:
            return "none"
        o = pe.off(dd[0])
        if o is None or o + 40 > len(data):
            return None
        name, _, _, nnames, _, aon = struct.unpack_from("<IIIIII", data, o + 12)
        names, t = [], pe.off(aon) if nnames else None
        for i in range(min(nnames, 65536)):
            if t is None or t + 4 * i + 4 > len(data):
                return None
            nm = pe.cstr(pe.u32(t + 4 * i))
            if nm is None:
                return None
            names.append(nm)
        return pe.cstr(name) if name else b"", names
    except (struct.error, TypeError, IndexError):
        return None


def export_names(data, ctx):
    """Export Name Pointer Table names in stored order (lexically sorted by the linker); no export directory -> none."""
    ex = _exports(data)
    return ex if not isinstance(ex, tuple) else [n.decode("utf-8", "replace") for n in ex[1]]


def export_dll_name(data, ctx):
    ex = _exports(data)
    return ex if not isinstance(ex, tuple) else (ex[0].decode("utf-8", "replace") or "none")


def export_count(data, ctx):
    ex = _exports(data)
    return ex if not isinstance(ex, tuple) else len(ex[1])


# ---- Authenticode (data directory 4, IMAGE_DIRECTORY_ENTRY_SECURITY) ----
# The Security directory's VirtualAddress is a FILE OFFSET (not an RVA). It points at WIN_CERTIFICATE records:
# dwLength(u32, includes the 8-byte header) wRevision(u16, 0x0200) wCertificateType(u16, 2 = PKCS_SIGNED_DATA) bCertificate
# = DER PKCS#7 ContentInfo(SignedData). Only the FIRST record / FIRST SignerInfo is the "signer" (a nested signature in
# the unauthenticated attribute 1.3.6.1.4.1.311.2.4.1 is ignored). The signer certificate = the certificate whose
# issuer+serial (or SubjectKeyIdentifier) matches SignerInfo.sid -- never just certificates[0], which can be the CA.
# Unsigned PE -> is_signed "false", the signer fields "none"; not a PE -> "none".
_DIR_SECURITY = 4


def _security(data):
    """(file_offset, size) of the Security directory; "none" (not a PE / no directory) or None (no data)."""
    if data is None:
        return None
    pe = _pe(data)
    if pe == "none":
        return "none"
    if _DIR_SECURITY >= len(pe.dirs):
        return "none"
    off, size = pe.dirs[_DIR_SECURITY]
    return (off, size) if off and size else "none"


def _pkcs7(data):
    """bCertificate bytes of the first WIN_CERTIFICATE of type PKCS_SIGNED_DATA; "none" / None."""
    sec = _security(data)
    if not isinstance(sec, tuple):
        return sec
    off, size = sec
    if off + 8 > len(data):
        return "none"
    ln, rev, typ = struct.unpack_from("<IHH", data, off)
    if typ != 2 or ln < 8:
        return "none"
    return bytes(data[off + 8:off + min(ln, size)])


def _signer(data):
    """(SignedData, SignerInfo, signer Certificate|None) of the first signature; "none" / None."""
    blob = _pkcs7(data)
    if not isinstance(blob, bytes):
        return blob
    try:
        from asn1crypto import cms
        ci = cms.ContentInfo.load(blob, strict=False)
        if ci["content_type"].native != "signed_data":
            return "none"
        sd = ci["content"]
        sis = sd["signer_infos"]
        if not len(sis):
            return "none"
        si = sis[0]
        sid = si["sid"]
        certs = [c.chosen for c in (sd["certificates"] or []) if c.name == "certificate"]
        cert = None
        for c in certs:
            if sid.name == "issuer_and_serial_number":
                ias = sid.chosen
                if c.serial_number == ias["serial_number"].native and c.issuer == ias["issuer"]:
                    cert = c
                    break
            elif sid.name == "subject_key_identifier" and c.key_identifier == sid.chosen.native:
                cert = c
                break
        return sd, si, cert
    except Exception:
        return None


def is_signed(data, ctx):
    """True iff data directory 4 is non-empty and holds a WIN_CERTIFICATE header inside the file."""
    sec = _security(data)
    if sec is None:
        return None
    if sec == "none":
        return "none" if _pe(data) == "none" else False
    off, size = sec
    if off + 8 > len(data):
        return False
    ln, rev, typ = struct.unpack_from("<IHH", data, off)
    return ln >= 8 and rev in (0x0100, 0x0200) and typ in (1, 2, 3, 4)


def security_dir_size(data, ctx):
    """Data directory 4 Size as stored (the certificate table size, 8-byte aligned)."""
    sec = _security(data)
    return sec if not isinstance(sec, tuple) else Hex(sec[1], 8)


def security_dir_size_bytes(data, ctx):
    sec = _security(data)
    return sec if not isinstance(sec, tuple) else sec[1]


def security_dir_offset(data, ctx):
    sec = _security(data)
    return sec if not isinstance(sec, tuple) else Hex(sec[0], 8)


def _cn(name):
    try:
        for rdn in name.chosen:
            for atv in rdn:
                if atv["type"].native == "common_name":
                    return str(atv["value"].native).strip()
    except Exception:
        return None
    return "none"


def _cert(data):
    s = _signer(data)
    if not isinstance(s, tuple):
        return s
    return s[2] if s[2] is not None else None


def signer_subject_cn(data, ctx):
    c = _cert(data)
    return c if c is None or c == "none" else _cn(c.subject)


def signer_issuer_cn(data, ctx):
    """Issuer CN of the signer certificate (falls back to SignerInfo.sid's issuer when the cert is not embedded)."""
    s = _signer(data)
    if not isinstance(s, tuple):
        return s
    if s[2] is not None:
        return _cn(s[2].issuer)
    sid = s[1]["sid"]
    return _cn(sid.chosen["issuer"]) if sid.name == "issuer_and_serial_number" else None


def signer_serial(data, ctx):
    """Signer cert serial as lowercase hex of its unsigned big-endian bytes (even length, no 0x / colons; a DER sign
    byte 00 is dropped) -- the openssl/certutil digits. Falls back to SignerInfo.sid's serial."""
    s = _signer(data)
    if not isinstance(s, tuple):
        return s
    try:
        if s[2] is not None:
            n = s[2].serial_number
        elif s[1]["sid"].name == "issuer_and_serial_number":
            n = s[1]["sid"].chosen["serial_number"].native
        else:
            return None
        if n < 0:
            return None
        h = "%x" % n
        return "0" * (len(h) % 2) + h
    except Exception:
        return None


def _cert_hash(data, algo):
    c = _cert(data)
    if c is None or c == "none":
        return c
    try:
        return hashlib.new(algo, c.dump()).hexdigest()
    except Exception:
        return None


def signer_cert_sha1(data, ctx):
    """Thumbprint = SHA-1 over the signer certificate's DER (lowercase hex)."""
    return _cert_hash(data, "sha1")


def signer_cert_sha256(data, ctx):
    return _cert_hash(data, "sha256")


def _utc(dt):
    import datetime
    if dt.tzinfo is not None:
        dt = dt.astimezone(datetime.timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _attr(attrs, oid):
    for a in attrs or []:
        if a["type"].dotted == oid:
            return a["values"]
    return None


def signing_time_utc(data, ctx):
    """Signing time, ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ' (fraction dropped), first found of:
    1. the SignerInfo authenticated attribute signingTime (1.2.840.113549.1.9.5, UTCTime/GeneralizedTime);
    2. a legacy countersignature (unauthenticated 1.2.840.113549.1.9.6) -> its signingTime;
    3. an RFC 3161 timestamp token (unauthenticated 1.3.6.1.4.1.311.3.3.1) -> TSTInfo.genTime.
    signtool-signed binaries carry only 2/3 (the timestamp), openssl/osslsigncode-made ones carry 1. None of them -> none."""
    s = _signer(data)
    if not isinstance(s, tuple):
        return s
    si = s[1]
    try:
        v = _attr(si["signed_attrs"], "1.2.840.113549.1.9.5")
        if v:
            return _utc(v[0].chosen.native if hasattr(v[0], "chosen") else v[0].native)
        ua = si["unsigned_attrs"]
        v = _attr(ua, "1.2.840.113549.1.9.6")
        if v:
            t = _attr(v[0]["signed_attrs"], "1.2.840.113549.1.9.5")
            if t:
                return _utc(t[0].native)
        v = _attr(ua, "1.3.6.1.4.1.311.3.3.1")
        if v:
            from asn1crypto import tsp
            raw = v[0]["content"]["encap_content_info"]["content"]
            tst = tsp.TSTInfo.load(raw.native if isinstance(raw.native, bytes) else raw.contents, strict=False)
            return _utc(tst["gen_time"].native)
    except Exception:
        return None
    return "none"
