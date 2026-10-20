"""ELF dynamic section / notes / symbol-table / .comment fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Format tokens `elf`, `binary`, `linux` (the same fields under each). Every struct is read in the file's EI_CLASS
(Elf32 / Elf64 layout) and EI_DATA byte order (header helpers shared with prebuilt/elf.py).
- dt_needed / needed_libraries: DT_NEEDED strings in .dynamic order (readelf -d "Shared library: [..]"), a compact
  JSON list; *_count -> len. dt_soname / dt_runpath / dt_rpath: the first DT_SONAME (14) / DT_RUNPATH (29) /
  DT_RPATH (15) string verbatim; absent -> "none". Strings come from DT_STRTAB (vaddr mapped through PT_LOAD), else
  the .dynamic section's sh_link string table. dynamic_entry_count = entries up to and including the first DT_NULL
  (readelf "Dynamic section at offset .. contains N entries"). init/fini_array_count = DT_INIT_ARRAYSZ /
  DT_FINI_ARRAYSZ / pointer size, else the .init_array / .fini_array section size; neither -> 0.
- abi_tag_*: the NT_GNU_ABI_TAG (type 1, owner "GNU") note, desc u32[4] = os, major, minor, sub; abi_tag_os = readelf's
  name (0 Linux, 1 Hurd, 2 Solaris, 3 FreeBSD, 4 NetBSD, 5 Syllable, 6 NaCl -- or the accepted_values spelling,
  e.g. GNU/Hurd), abi_tag_os_id = the int, abi_tag_kernel / min_kernel_version = "major.minor.sub" ("3.2.0").
- gnu_property_*: NT_GNU_PROPERTY_TYPE_0 (type 5) pr_type/pr_datasz pairs (8-byte padded in ELF64, 4 in ELF32);
  x86 FEATURE_1_AND (0xc0000002: IBT, SHSTK, LAM_U48, LAM_U57) and ISA_1_NEEDED (0xc0008002 bits ->
  x86-64-baseline/-v2/-v3/-v4), rendered like readelf -n ("IBT, SHSTK", "x86-64-baseline"); aarch64 FEATURE_1_AND
  (0xc0000000: BTI, PAC, GCS). Absent / zero -> "none".
- comment / comment_strings: the .comment section NUL-split, empties dropped, verbatim (readelf -p .comment);
  `comment` is the single string when there is one, else the list.
- is_stripped: no SHT_SYMTAB section (`file` "stripped"); has_symtab is its inverse. dynsym_count / symtab_count =
  sh_size / sh_entsize of the SHT_DYNSYM / SHT_SYMTAB section INCLUDING the null entry 0 (readelf --syms "contains
  N entries"); symtab absent -> 0. dynamic_symbol_names = the named .dynsym entries in table order (no @VERSION
  suffix); imported/undefined_* = only st_shndx == SHN_UNDEF; exported_* = defined GLOBAL/WEAK; *_sorted = sorted.
- e_phentsize / e_ehsize / e_shentsize / e_phoff / e_shoff: ints from the header. pt_load_count = PT_LOAD phdrs.
  program_header_types = p_type names in phdr order with the PT_ prefix (PT_PHDR, PT_INTERP, PT_LOAD, ...,
  PT_GNU_STACK); an unknown type -> 0x%08x.
Not ELF / truncated header -> "none"; a malformed body never raises (None)."""
import struct

from .elf import _ehdr

FIELDS = {
    ("elf", "dt_needed"): "dyn_value",
    ("elf", "dt_needed_libraries"): "dyn_value",
    ("elf", "needed"): "dyn_value",
    ("elf", "needed_libraries"): "dyn_value",
    ("elf", "needed_libs"): "dyn_value",
    ("elf", "needed_library_names"): "dyn_value",
    ("elf", "shared_library_dependencies"): "dyn_value",
    ("elf", "dt_needed_count"): "dyn_value",
    ("elf", "needed_library_count"): "dyn_value",
    ("elf", "dt_soname"): "dyn_value",
    ("elf", "soname"): "dyn_value",
    ("elf", "dt_runpath"): "dyn_value",
    ("elf", "runpath"): "dyn_value",
    ("elf", "dt_rpath"): "dyn_value",
    ("elf", "rpath"): "dyn_value",
    ("elf", "dynamic_entry_count"): "dyn_value",
    ("elf", "dynamic_section_entry_count"): "dyn_value",
    ("elf", "init_array_count"): "dyn_value",
    ("elf", "dt_init_array_count"): "dyn_value",
    ("elf", "fini_array_count"): "dyn_value",
    ("elf", "dt_fini_array_count"): "dyn_value",
    ("elf", "abi_tag_os"): "note_value",
    ("elf", "abi_tag_os_name"): "note_value",
    ("elf", "note_abi_tag_os"): "note_value",
    ("elf", "gnu_abi_tag_os"): "note_value",
    ("elf", "abi_tag_os_id"): "note_value",
    ("elf", "abi_tag_kernel"): "note_value",
    ("elf", "abi_tag_kernel_version"): "note_value",
    ("elf", "abi_tag_version"): "note_value",
    ("elf", "abi_tag_abi_version"): "note_value",
    ("elf", "note_abi_tag_kernel"): "note_value",
    ("elf", "gnu_abi_tag_kernel"): "note_value",
    ("elf", "min_kernel_version"): "note_value",
    ("elf", "minimum_kernel_version"): "note_value",
    ("elf", "gnu_property_x86_isa_needed"): "note_value",
    ("elf", "x86_isa_needed"): "note_value",
    ("elf", "gnu_property_x86_isa_1_needed"): "note_value",
    ("elf", "gnu_property_x86_feature_1"): "note_value",
    ("elf", "gnu_property_x86_feature_1_and"): "note_value",
    ("elf", "x86_feature_1"): "note_value",
    ("elf", "x86_features"): "note_value",
    ("elf", "gnu_property_aarch64_feature_1"): "note_value",
    ("elf", "gnu_property_aarch64_feature_1_and"): "note_value",
    ("elf", "aarch64_feature_1"): "note_value",
    ("elf", "comment"): "sect_value",
    ("elf", "comment_strings"): "sect_value",
    ("elf", "comment_section"): "sect_value",
    ("elf", "comment_section_strings"): "sect_value",
    ("elf", "compiler_comment"): "sect_value",
    ("elf", "is_stripped"): "sect_value",
    ("elf", "stripped"): "sect_value",
    ("elf", "has_symtab"): "sect_value",
    ("elf", "dynsym_count"): "sect_value",
    ("elf", "dynsym_entry_count"): "sect_value",
    ("elf", "dynamic_symbol_count"): "sect_value",
    ("elf", "symtab_count"): "sect_value",
    ("elf", "symtab_entry_count"): "sect_value",
    ("elf", "symbol_count"): "sect_value",
    ("elf", "dynamic_symbol_names"): "sect_value",
    ("elf", "dynamic_symbol_names_sorted"): "sect_value",
    ("elf", "dynsym_names"): "sect_value",
    ("elf", "dynsym_names_sorted"): "sect_value",
    ("elf", "imported_symbol_names"): "sect_value",
    ("elf", "imported_symbol_names_sorted"): "sect_value",
    ("elf", "imported_symbols"): "sect_value",
    ("elf", "imported_symbols_sorted"): "sect_value",
    ("elf", "import_names"): "sect_value",
    ("elf", "import_names_sorted"): "sect_value",
    ("elf", "undefined_symbol_names"): "sect_value",
    ("elf", "undefined_symbol_names_sorted"): "sect_value",
    ("elf", "exported_symbol_names"): "sect_value",
    ("elf", "exported_symbol_names_sorted"): "sect_value",
    ("elf", "e_phentsize"): "hdr_value",
    ("elf", "e_ehsize"): "hdr_value",
    ("elf", "e_shentsize"): "hdr_value",
    ("elf", "e_phoff"): "hdr_value",
    ("elf", "e_shoff"): "hdr_value",
    ("elf", "pt_load_count"): "hdr_value",
    ("elf", "load_segment_count"): "hdr_value",
    ("elf", "program_header_types"): "hdr_value",
    ("elf", "segment_types"): "hdr_value",
    ("elf", "phdr_types"): "hdr_value",
    ("binary", "dt_needed"): "dyn_value",
    ("binary", "dt_needed_libraries"): "dyn_value",
    ("binary", "needed"): "dyn_value",
    ("binary", "needed_libraries"): "dyn_value",
    ("binary", "needed_libs"): "dyn_value",
    ("binary", "needed_library_names"): "dyn_value",
    ("binary", "shared_library_dependencies"): "dyn_value",
    ("binary", "dt_needed_count"): "dyn_value",
    ("binary", "needed_library_count"): "dyn_value",
    ("binary", "dt_soname"): "dyn_value",
    ("binary", "soname"): "dyn_value",
    ("binary", "dt_runpath"): "dyn_value",
    ("binary", "runpath"): "dyn_value",
    ("binary", "dt_rpath"): "dyn_value",
    ("binary", "rpath"): "dyn_value",
    ("binary", "dynamic_entry_count"): "dyn_value",
    ("binary", "dynamic_section_entry_count"): "dyn_value",
    ("binary", "init_array_count"): "dyn_value",
    ("binary", "dt_init_array_count"): "dyn_value",
    ("binary", "fini_array_count"): "dyn_value",
    ("binary", "dt_fini_array_count"): "dyn_value",
    ("binary", "abi_tag_os"): "note_value",
    ("binary", "abi_tag_os_name"): "note_value",
    ("binary", "note_abi_tag_os"): "note_value",
    ("binary", "gnu_abi_tag_os"): "note_value",
    ("binary", "abi_tag_os_id"): "note_value",
    ("binary", "abi_tag_kernel"): "note_value",
    ("binary", "abi_tag_kernel_version"): "note_value",
    ("binary", "abi_tag_version"): "note_value",
    ("binary", "abi_tag_abi_version"): "note_value",
    ("binary", "note_abi_tag_kernel"): "note_value",
    ("binary", "gnu_abi_tag_kernel"): "note_value",
    ("binary", "min_kernel_version"): "note_value",
    ("binary", "minimum_kernel_version"): "note_value",
    ("binary", "gnu_property_x86_isa_needed"): "note_value",
    ("binary", "x86_isa_needed"): "note_value",
    ("binary", "gnu_property_x86_isa_1_needed"): "note_value",
    ("binary", "gnu_property_x86_feature_1"): "note_value",
    ("binary", "gnu_property_x86_feature_1_and"): "note_value",
    ("binary", "x86_feature_1"): "note_value",
    ("binary", "x86_features"): "note_value",
    ("binary", "gnu_property_aarch64_feature_1"): "note_value",
    ("binary", "gnu_property_aarch64_feature_1_and"): "note_value",
    ("binary", "aarch64_feature_1"): "note_value",
    ("binary", "comment"): "sect_value",
    ("binary", "comment_strings"): "sect_value",
    ("binary", "comment_section"): "sect_value",
    ("binary", "comment_section_strings"): "sect_value",
    ("binary", "compiler_comment"): "sect_value",
    ("binary", "is_stripped"): "sect_value",
    ("binary", "stripped"): "sect_value",
    ("binary", "has_symtab"): "sect_value",
    ("binary", "dynsym_count"): "sect_value",
    ("binary", "dynsym_entry_count"): "sect_value",
    ("binary", "dynamic_symbol_count"): "sect_value",
    ("binary", "symtab_count"): "sect_value",
    ("binary", "symtab_entry_count"): "sect_value",
    ("binary", "symbol_count"): "sect_value",
    ("binary", "dynamic_symbol_names"): "sect_value",
    ("binary", "dynamic_symbol_names_sorted"): "sect_value",
    ("binary", "dynsym_names"): "sect_value",
    ("binary", "dynsym_names_sorted"): "sect_value",
    ("binary", "imported_symbol_names"): "sect_value",
    ("binary", "imported_symbol_names_sorted"): "sect_value",
    ("binary", "imported_symbols"): "sect_value",
    ("binary", "imported_symbols_sorted"): "sect_value",
    ("binary", "import_names"): "sect_value",
    ("binary", "import_names_sorted"): "sect_value",
    ("binary", "undefined_symbol_names"): "sect_value",
    ("binary", "undefined_symbol_names_sorted"): "sect_value",
    ("binary", "exported_symbol_names"): "sect_value",
    ("binary", "exported_symbol_names_sorted"): "sect_value",
    ("binary", "e_phentsize"): "hdr_value",
    ("binary", "e_ehsize"): "hdr_value",
    ("binary", "e_shentsize"): "hdr_value",
    ("binary", "e_phoff"): "hdr_value",
    ("binary", "e_shoff"): "hdr_value",
    ("binary", "pt_load_count"): "hdr_value",
    ("binary", "load_segment_count"): "hdr_value",
    ("binary", "program_header_types"): "hdr_value",
    ("binary", "segment_types"): "hdr_value",
    ("binary", "phdr_types"): "hdr_value",
    ("linux", "dt_needed"): "dyn_value",
    ("linux", "dt_needed_libraries"): "dyn_value",
    ("linux", "needed"): "dyn_value",
    ("linux", "needed_libraries"): "dyn_value",
    ("linux", "needed_libs"): "dyn_value",
    ("linux", "needed_library_names"): "dyn_value",
    ("linux", "shared_library_dependencies"): "dyn_value",
    ("linux", "dt_needed_count"): "dyn_value",
    ("linux", "needed_library_count"): "dyn_value",
    ("linux", "dt_soname"): "dyn_value",
    ("linux", "soname"): "dyn_value",
    ("linux", "dt_runpath"): "dyn_value",
    ("linux", "runpath"): "dyn_value",
    ("linux", "dt_rpath"): "dyn_value",
    ("linux", "rpath"): "dyn_value",
    ("linux", "dynamic_entry_count"): "dyn_value",
    ("linux", "dynamic_section_entry_count"): "dyn_value",
    ("linux", "init_array_count"): "dyn_value",
    ("linux", "dt_init_array_count"): "dyn_value",
    ("linux", "fini_array_count"): "dyn_value",
    ("linux", "dt_fini_array_count"): "dyn_value",
    ("linux", "abi_tag_os"): "note_value",
    ("linux", "abi_tag_os_name"): "note_value",
    ("linux", "note_abi_tag_os"): "note_value",
    ("linux", "gnu_abi_tag_os"): "note_value",
    ("linux", "abi_tag_os_id"): "note_value",
    ("linux", "abi_tag_kernel"): "note_value",
    ("linux", "abi_tag_kernel_version"): "note_value",
    ("linux", "abi_tag_version"): "note_value",
    ("linux", "abi_tag_abi_version"): "note_value",
    ("linux", "note_abi_tag_kernel"): "note_value",
    ("linux", "gnu_abi_tag_kernel"): "note_value",
    ("linux", "min_kernel_version"): "note_value",
    ("linux", "minimum_kernel_version"): "note_value",
    ("linux", "gnu_property_x86_isa_needed"): "note_value",
    ("linux", "x86_isa_needed"): "note_value",
    ("linux", "gnu_property_x86_isa_1_needed"): "note_value",
    ("linux", "gnu_property_x86_feature_1"): "note_value",
    ("linux", "gnu_property_x86_feature_1_and"): "note_value",
    ("linux", "x86_feature_1"): "note_value",
    ("linux", "x86_features"): "note_value",
    ("linux", "gnu_property_aarch64_feature_1"): "note_value",
    ("linux", "gnu_property_aarch64_feature_1_and"): "note_value",
    ("linux", "aarch64_feature_1"): "note_value",
    ("linux", "comment"): "sect_value",
    ("linux", "comment_strings"): "sect_value",
    ("linux", "comment_section"): "sect_value",
    ("linux", "comment_section_strings"): "sect_value",
    ("linux", "compiler_comment"): "sect_value",
    ("linux", "is_stripped"): "sect_value",
    ("linux", "stripped"): "sect_value",
    ("linux", "has_symtab"): "sect_value",
    ("linux", "dynsym_count"): "sect_value",
    ("linux", "dynsym_entry_count"): "sect_value",
    ("linux", "dynamic_symbol_count"): "sect_value",
    ("linux", "symtab_count"): "sect_value",
    ("linux", "symtab_entry_count"): "sect_value",
    ("linux", "symbol_count"): "sect_value",
    ("linux", "dynamic_symbol_names"): "sect_value",
    ("linux", "dynamic_symbol_names_sorted"): "sect_value",
    ("linux", "dynsym_names"): "sect_value",
    ("linux", "dynsym_names_sorted"): "sect_value",
    ("linux", "imported_symbol_names"): "sect_value",
    ("linux", "imported_symbol_names_sorted"): "sect_value",
    ("linux", "imported_symbols"): "sect_value",
    ("linux", "imported_symbols_sorted"): "sect_value",
    ("linux", "import_names"): "sect_value",
    ("linux", "import_names_sorted"): "sect_value",
    ("linux", "undefined_symbol_names"): "sect_value",
    ("linux", "undefined_symbol_names_sorted"): "sect_value",
    ("linux", "exported_symbol_names"): "sect_value",
    ("linux", "exported_symbol_names_sorted"): "sect_value",
    ("linux", "e_phentsize"): "hdr_value",
    ("linux", "e_ehsize"): "hdr_value",
    ("linux", "e_shentsize"): "hdr_value",
    ("linux", "e_phoff"): "hdr_value",
    ("linux", "e_shoff"): "hdr_value",
    ("linux", "pt_load_count"): "hdr_value",
    ("linux", "load_segment_count"): "hdr_value",
    ("linux", "program_header_types"): "hdr_value",
    ("linux", "segment_types"): "hdr_value",
    ("linux", "phdr_types"): "hdr_value",
}

_PT = {0: "PT_NULL", 1: "PT_LOAD", 2: "PT_DYNAMIC", 3: "PT_INTERP", 4: "PT_NOTE", 5: "PT_SHLIB", 6: "PT_PHDR",
       7: "PT_TLS", 0x6474E550: "PT_GNU_EH_FRAME", 0x6474E551: "PT_GNU_STACK", 0x6474E552: "PT_GNU_RELRO",
       0x6474E553: "PT_GNU_PROPERTY", 0x6474E554: "PT_GNU_SFRAME", 0x65A3DBE6: "PT_OPENBSD_RANDOMIZE",
       0x65A3DBE7: "PT_OPENBSD_WXNEEDED", 0x65A41BE6: "PT_OPENBSD_BOOTDATA"}
_PT_PROC = {40: {0x70000001: "PT_ARM_EXIDX"},
            8: {0x70000000: "PT_MIPS_REGINFO", 0x70000001: "PT_MIPS_RTPROC", 0x70000002: "PT_MIPS_OPTIONS",
                0x70000003: "PT_MIPS_ABIFLAGS"},
            183: {0x70000002: "PT_AARCH64_MEMTAG_MTE"}, 243: {0x70000003: "PT_RISCV_ATTRIBUTES"}}
_ABI_OS = {0: "Linux", 1: "Hurd", 2: "Solaris", 3: "FreeBSD", 4: "NetBSD", 5: "Syllable", 6: "NaCl"}
_ABI_OS_ALIASES = {"Linux": ["GNU/Linux", "ELF_NOTE_OS_LINUX", "GNU_ABI_TAG_LINUX", "0"],
                   "Hurd": ["GNU/Hurd", "GNU", "ELF_NOTE_OS_GNU", "GNU_ABI_TAG_HURD", "1"],
                   "Solaris": ["Solaris2", "ELF_NOTE_OS_SOLARIS2", "GNU_ABI_TAG_SOLARIS", "2"],
                   "FreeBSD": ["kFreeBSD", "ELF_NOTE_OS_FREEBSD", "GNU_ABI_TAG_FREEBSD", "3"]}
_X86_FEAT = ((1, "IBT"), (2, "SHSTK"), (4, "LAM_U48"), (8, "LAM_U57"))
_X86_ISA = ((1, "x86-64-baseline"), (2, "x86-64-v2"), (4, "x86-64-v3"), (8, "x86-64-v4"))
_A64_FEAT = ((1, "BTI"), (2, "PAC"), (4, "GCS"))


def _sections(b, h):
    """[{name, type, addr, offset, size, link, align, entsize}] in section-header-table order ([] if absent)."""
    e, is64 = h["e"], h["is64"]
    esz = 64 if is64 else 40
    if not h["shoff"] or h["shentsize"] < esz:
        return []
    raw = []
    for i in range(min(h["shnum"], 65536)):
        off = h["shoff"] + i * h["shentsize"]
        if off + esz > len(b):
            break
        if is64:
            nm, typ, _, addr, soff, size, link, info, al, es = struct.unpack_from(e + "IIQQQQIIQQ", b, off)
        else:
            nm, typ, _, addr, soff, size, link, info, al, es = struct.unpack_from(e + "IIIIIIIIII", b, off)
        raw.append({"nm": nm, "type": typ, "addr": addr, "offset": soff, "size": size, "link": link,
                    "align": al, "entsize": es})
    strtab = b""
    if 0 < h["shstrndx"] < len(raw):
        st = raw[h["shstrndx"]]
        strtab = bytes(b[st["offset"]:st["offset"] + st["size"]])
    for s in raw:
        s["name"] = strtab[s["nm"]:].split(b"\0", 1)[0].decode("utf-8", "replace") if s["nm"] < len(strtab) else ""
    return raw


def _phdrs(b, h):
    """[{type, offset, vaddr, filesz, align}] in phdr order."""
    e, is64 = h["e"], h["is64"]
    esz = 56 if is64 else 32
    if not h["phoff"] or h["phentsize"] < esz:
        return []
    out = []
    for i in range(min(h["phnum"], 65536)):
        off = h["phoff"] + i * h["phentsize"]
        if off + esz > len(b):
            break
        if is64:
            typ, _, poff, va, _, fsz, _, al = struct.unpack_from(e + "IIQQQQQQ", b, off)
        else:
            typ, poff, va, _, fsz, _, _, al = struct.unpack_from(e + "IIIIIIII", b, off)
        out.append({"type": typ, "offset": poff, "vaddr": va, "filesz": fsz, "align": al})
    return out


def _blob(b, off, size):
    return bytes(b[off:off + size]) if off < len(b) else b""


def _v2off(phs, va):
    for p in phs:
        if p["type"] == 1 and p["vaddr"] <= va < p["vaddr"] + p["filesz"]:
            return p["offset"] + (va - p["vaddr"])
    return None


def _dynamic(b, h, secs, phs):
    """([(tag, val)] up to and including DT_NULL, strtab bytes) or (None, b"")."""
    area, link = None, None
    for s in secs:
        if s["type"] == 6:   # SHT_DYNAMIC
            area, link = _blob(b, s["offset"], s["size"]), s["link"]
            break
    if area is None:
        for p in phs:
            if p["type"] == 2:
                area = _blob(b, p["offset"], p["filesz"])
                break
    if area is None:
        return None, b""
    fmt, step = (h["e"] + "qQ", 16) if h["is64"] else (h["e"] + "iI", 8)
    ents = []
    for o in range(0, len(area) - step + 1, step):
        tag, val = struct.unpack_from(fmt, area, o)
        ents.append((tag, val))
        if tag == 0:
            break
    strtab = b""
    d = dict((t, v) for t, v in reversed(ents))
    if 5 in d:
        off = _v2off(phs, d[5])
        if off is not None:
            strtab = _blob(b, off, d.get(10, len(b) - off))
    if not strtab and link is not None and 0 < link < len(secs):
        strtab = _blob(b, secs[link]["offset"], secs[link]["size"])
    return ents, strtab


def _str(tab, i):
    if i >= len(tab):
        return None
    return tab[i:].split(b"\0", 1)[0].decode("utf-8", "replace")


def _notes(b, h, secs, phs):
    """[(owner, type, desc)] of every SHT_NOTE section (else PT_NOTE segment); 8-byte padding when aligned to 8."""
    areas = [(_blob(b, s["offset"], s["size"]), s["align"]) for s in secs if s["type"] == 7]
    if not secs:
        areas = [(_blob(b, p["offset"], p["filesz"]), p["align"]) for p in phs if p["type"] == 4]
    out = []
    for blob, al in areas:
        a = 8 if al == 8 else 4
        off = 0
        while off + 12 <= len(blob):   # desc / next note aligned relative to the note start (gABI + GNU)
            nsz, dsz, typ = struct.unpack_from(h["e"] + "III", blob, off)
            name = blob[off + 12:off + 12 + nsz].rstrip(b"\0")
            doff = off + ((12 + nsz + a - 1) & ~(a - 1))
            if doff + dsz > len(blob):
                break
            out.append((name, typ, blob[doff:doff + dsz]))
            off = off + ((doff - off + dsz + a - 1) & ~(a - 1))
    return out


def _gnu_props(h, notes):
    """{pr_type: u32 data} of the NT_GNU_PROPERTY_TYPE_0 notes."""
    props, pad = {}, 8 if h["is64"] else 4
    for name, typ, desc in notes:
        if name != b"GNU" or typ != 5:
            continue
        off = 0
        while off + 8 <= len(desc):
            pt, sz = struct.unpack_from(h["e"] + "II", desc, off)
            off += 8
            if sz >= 4 and off + 4 <= len(desc):
                props.setdefault(pt, struct.unpack_from(h["e"] + "I", desc, off)[0])
            off += (sz + pad - 1) & ~(pad - 1)
    return props


def _bits(v, table):
    if not v:
        return "none"
    names = [n for bit, n in table if v & bit]
    rest = v & ~sum(bit for bit, _ in table)
    if rest:
        names.append("<unknown: %x>" % rest)
    return ", ".join(names)


def _accepted(name, aliases, ctx):
    fmt = ((ctx or {}).get("question") or {}).get("answer_format") or {}
    acc = fmt.get("accepted_values") or fmt.get("values") or []
    if not isinstance(acc, (list, tuple)) or not acc:
        return name
    low = {str(a).strip().lower(): str(a) for a in acc}
    for c in [name] + aliases.get(name, []):
        if c.lower() in low:
            return low[c.lower()]
    return name


def _symbols(b, h, secs, styp):
    """(entry count incl. null, [(name, shndx, bind)]) of the first section of type styp, or (None, [])."""
    for s in secs:
        if s["type"] != styp:
            continue
        esz = s["entsize"] or (24 if h["is64"] else 16)
        n = s["size"] // esz if esz else 0
        tab = _blob(b, secs[s["link"]]["offset"], secs[s["link"]]["size"]) if 0 < s["link"] < len(secs) else b""
        syms = []
        for i in range(min(n, 1 << 20)):
            off = s["offset"] + i * esz
            if off + (24 if h["is64"] else 16) > len(b):
                break
            if h["is64"]:
                nm, info, _, shndx = struct.unpack_from(h["e"] + "IBBH", b, off)
            else:
                nm, _, _, info, _, shndx = struct.unpack_from(h["e"] + "IIIBBH", b, off)
            syms.append((_str(tab, nm) or "", shndx, info >> 4))
        return n, syms
    return None, []


def _guard(fn):
    def run(data, ctx):
        if data is None:
            return None
        try:
            h = _ehdr(data)
            if h is None:
                return "none"
            return fn(data, h, (ctx or {}).get("field") or "", ctx)
        except Exception:  # noqa: BLE001 -- a malformed ELF never raises past the extractor
            return None
    return run


@_guard
def _dyn(b, h, f, ctx):
    secs = _sections(b, h)
    phs = _phdrs(b, h)
    ents, strtab = _dynamic(b, h, secs, phs)
    if "array_count" in f:
        ptr = 8 if h["is64"] else 4
        tag, sec = (27, ".init_array") if f.startswith(("init", "dt_init")) else (28, ".fini_array")
        for t, v in ents or []:
            if t == tag:
                return v // ptr
        for s in secs:
            if s["name"] == sec:
                return s["size"] // ptr
        return 0
    if f.startswith("dynamic"):
        return len(ents) if ents is not None else "none"
    if ents is None:
        return [] if "need" in f and "count" not in f else (0 if "count" in f else "none")
    if "need" in f or "shared_library" in f:
        libs = [_str(strtab, v) for t, v in ents if t == 1]
        libs = [x for x in libs if x is not None]
        return len(libs) if "count" in f else libs
    tag = {"soname": 14, "runpath": 29, "rpath": 15}[f.replace("dt_", "")]
    for t, v in ents:
        if t == tag:
            s = _str(strtab, v)
            return s if s is not None else None
    return "none"


@_guard
def _note(b, h, f, ctx):
    notes = _notes(b, h, _sections(b, h), _phdrs(b, h))
    if "abi_tag" in f or "kernel" in f:
        for name, typ, desc in notes:
            if name == b"GNU" and typ == 1 and len(desc) >= 16:
                os_, a, c, d = struct.unpack_from(h["e"] + "IIII", desc, 0)
                if f.endswith("os_id"):
                    return os_
                if f.endswith(("_os", "os_name")):
                    return _accepted(_ABI_OS.get(os_, "Unknown OS %d" % os_), _ABI_OS_ALIASES, ctx)
                return "%d.%d.%d" % (a, c, d)
        return "none"
    props = _gnu_props(h, notes)
    if "aarch64" in f:
        return _bits(props.get(0xC0000000, 0), _A64_FEAT)
    if "isa" in f:
        return _bits(props.get(0xC0008002, 0), _X86_ISA)
    return _bits(props.get(0xC0000002, 0), _X86_FEAT)


@_guard
def _sect(b, h, f, ctx):
    secs = _sections(b, h)
    if "comment" in f:
        for s in secs:
            if s["name"] == ".comment" and s["type"] != 8:
                parts = [p.decode("utf-8", "replace").strip() for p in _blob(b, s["offset"], s["size"]).split(b"\0")]
                parts = [p for p in parts if p]
                if not parts:
                    return "none"
                return parts[0] if f in ("comment", "comment_section", "compiler_comment") and len(parts) == 1 \
                    else parts
        return "none"
    has_symtab = any(s["type"] == 2 for s in secs)
    if "stripped" in f:
        return not has_symtab
    if f == "has_symtab":
        return has_symtab
    if "count" in f:
        n, _ = _symbols(b, h, secs, 11 if "dyn" in f else 2)
        return n if n is not None else 0
    n, syms = _symbols(b, h, secs, 11)
    if n is None:
        return "none"
    if f.startswith(("import", "undefined")):
        names = [s for s, ndx, _ in syms if s and ndx == 0]
    elif f.startswith("export"):
        names = [s for s, ndx, bind in syms if s and ndx != 0 and bind in (1, 2)]
    else:
        names = [s for s, _, _ in syms if s]
    return sorted(names) if f.endswith("_sorted") else names


@_guard
def _hdr(b, h, f, ctx):
    if f.startswith("e_"):
        return {"e_phentsize": h["phentsize"], "e_shentsize": h["shentsize"], "e_phoff": h["phoff"],
                "e_shoff": h["shoff"], "e_ehsize": struct.unpack_from(h["e"] + "H", b, 52 if h["is64"] else 40)[0]}[f]
    phs = _phdrs(b, h)
    if "load" in f:
        return sum(1 for p in phs if p["type"] == 1)
    proc = _PT_PROC.get(h["machine"], {})
    return [_PT.get(p["type"]) or proc.get(p["type"]) or "0x%08x" % p["type"] for p in phs]


def dyn_value(data, ctx):
    return _dyn(data, ctx)


def note_value(data, ctx):
    return _note(data, ctx)


def sect_value(data, ctx):
    return _sect(data, ctx)


def hdr_value(data, ctx):
    return _hdr(data, ctx)
