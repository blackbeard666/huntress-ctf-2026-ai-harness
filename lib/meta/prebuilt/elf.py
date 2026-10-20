"""ELF header / PT_INTERP / .note.gnu.build-id fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Ehdr (System V gABI): e_ident[16] (EI_CLASS @4: 1 ELFCLASS32 / 2 ELFCLASS64, EI_DATA @5: 1 ELFDATA2LSB /
2 ELFDATA2MSB, EI_OSABI @7), then e_type u16, e_machine u16, e_version u32, e_entry/e_phoff/e_shoff (u32 or u64 by
class), e_flags u32, e_ehsize/e_phentsize/e_phnum/e_shentsize/e_shnum/e_shstrndx u16, in the EI_DATA byte order.
Extended numbering (gABI): e_shnum == 0 with e_shoff != 0 -> the real count is shdr[0].sh_size; e_phnum == 0xffff
(PN_XNUM) -> shdr[0].sh_info; e_shstrndx == 0xffff (SHN_XINDEX) -> shdr[0].sh_link. The *_count / e_shnum fields
report the REAL count (what readelf prints as "Number of section headers").
interpreter = the PT_INTERP segment's path without its NUL (readelf "[Requesting program interpreter: ...]").
build_id_hex = the NT_GNU_BUILD_ID (type 3, name "GNU") note's desc as lowercase hex without 0x (readelf -n
"Build ID:", `file` "BuildID[sha1]="); found via the .note.gnu.build-id section, else any SHT_NOTE section, else
PT_NOTE segments (a section-stripped binary). section_names = sh_name strings in section-header-table order, the
SHT_NULL entry [0] (empty name) dropped (readelf -S order). ei_class / ei_data = the gABI constant names
(ELFCLASS64, ELFDATA2LSB), mapped onto answer_format.accepted_values when the contract lists another spelling.
Not ELF / truncated header -> "none"; a field the file lacks (no PT_INTERP, no build-id note) -> "none".

Header hex grammar (D19 elf.e_machine_u16_hex = "0x003e" GM-verified: the RAW Elf_Ehdr member, `0x` + lowercase,
zero-padded to the struct width, read in EI_DATA order): every member has a `<member>_uNN_hex` sibling --
ei_class/ei_data/ei_version/ei_osabi/ei_abiversion (also e_ident_*) u8 -> "0x02"; e_type/e_machine/e_ehsize/
e_phentsize/e_phnum/e_shentsize/e_shnum/e_shstrndx u16 -> "0x0040" (RAW header value, no extended-numbering fix-up);
e_version/e_flags u32 -> "0x00000001"; e_entry/e_phoff/e_shoff `_u64_hex` (16 digits) / `_u32_hex` (8) by the NAME,
bare `_hex` by EI_CLASS (ELF64 16, ELF32 8). A value wider than the named width -> None.
Vocabularies (each remapped onto answer_format.accepted_values when the contract lists another spelling):
e_type_name ET_NONE/ET_REL/ET_EXEC/ET_DYN/ET_CORE; machine_name = readelf "Machine:" text ("Advanced Micro Devices
X86-64", "MIPS R3000", "ARM", "IBM S/390", "AArch64"); e_machine_name = the EM_* constant; architecture / arch =
uname -m style (x86_64, i386, aarch64, arm, mips/mipsel/mips64/mips64el, ppc/ppc64/ppc64le, s390/s390x, riscv64,
loongarch64 -- endianness/class pick the variant); goarch = Go GOARCH (amd64, 386, arm64, arm, mips/mipsle/mips64/
mips64le, ppc64/ppc64le, s390x, riscv64, loong64; none for an arch Go lacks -> None); endianness / byte_order =
little/big; bitness = 32/64 (int); elf_class = readelf "Class:" (ELF32/ELF64) while ei_class stays ELFCLASS64."""
import re
import struct

from ..spell import Hex

FIELDS = {
    ("elf", "e_type_u16_hex"): "elf_value",
    ("elf", "type_u16_hex"): "elf_value",
    ("elf", "elf_type_u16_hex"): "elf_value",
    ("elf", "e_type"): "elf_value",
    ("elf", "e_shnum"): "elf_value",
    ("elf", "section_count"): "elf_value",
    ("elf", "number_of_sections"): "elf_value",
    ("elf", "section_header_count"): "elf_value",
    ("elf", "e_phnum"): "elf_value",
    ("elf", "program_header_count"): "elf_value",
    ("elf", "number_of_program_headers"): "elf_value",
    ("elf", "segment_count"): "elf_value",
    ("elf", "ei_class"): "elf_value",
    ("elf", "e_ident_class"): "elf_value",
    ("elf", "elf_class"): "elf_value",
    ("elf", "ei_data"): "elf_value",
    ("elf", "e_ident_data"): "elf_value",
    ("elf", "data_encoding"): "elf_value",
    ("elf", "endianness"): "elf_value",
    ("elf", "ei_osabi"): "elf_value",
    ("elf", "e_ident_osabi"): "elf_value",
    ("elf", "e_flags_u32_hex"): "elf_value",
    ("elf", "flags_u32_hex"): "elf_value",
    ("elf", "e_version"): "elf_value",
    ("elf", "e_shstrndx"): "elf_value",
    ("elf", "interpreter"): "elf_value",
    ("elf", "program_interpreter"): "elf_value",
    ("elf", "pt_interp"): "elf_value",
    ("elf", "interp"): "elf_value",
    ("elf", "interp_path"): "elf_value",
    ("elf", "interpreter_path"): "elf_value",
    ("elf", "pt_interp_path"): "elf_value",
    ("elf", "build_id_hex"): "elf_value",
    ("elf", "build_id"): "elf_value",
    ("elf", "gnu_build_id"): "elf_value",
    ("elf", "gnu_build_id_hex"): "elf_value",
    ("elf", "note_gnu_build_id_hex"): "elf_value",
    ("elf", "section_names"): "elf_value",
    ("elf", "section_header_names"): "elf_value",
    ("elf", "shdr_names"): "elf_value",
    ("elf", "ei_class_u8_hex"): "elf_value",
    ("elf", "e_ident_class_u8_hex"): "elf_value",
    ("elf", "ei_data_u8_hex"): "elf_value",
    ("elf", "e_ident_data_u8_hex"): "elf_value",
    ("elf", "ei_version_u8_hex"): "elf_value",
    ("elf", "e_ident_version_u8_hex"): "elf_value",
    ("elf", "ei_osabi_u8_hex"): "elf_value",
    ("elf", "e_ident_osabi_u8_hex"): "elf_value",
    ("elf", "ei_abiversion_u8_hex"): "elf_value",
    ("elf", "e_ident_abiversion_u8_hex"): "elf_value",
    ("elf", "ei_version"): "elf_value",
    ("elf", "e_ident_version"): "elf_value",
    ("elf", "ei_abiversion"): "elf_value",
    ("elf", "e_ident_abiversion"): "elf_value",
    ("elf", "abi_version"): "elf_value",
    ("elf", "e_version_u32_hex"): "elf_value",
    ("elf", "e_machine"): "elf_value",
    ("elf", "e_ehsize_u16_hex"): "elf_value",
    ("elf", "e_phentsize_u16_hex"): "elf_value",
    ("elf", "e_phnum_u16_hex"): "elf_value",
    ("elf", "e_shentsize_u16_hex"): "elf_value",
    ("elf", "e_shnum_u16_hex"): "elf_value",
    ("elf", "e_shstrndx_u16_hex"): "elf_value",
    ("elf", "e_entry_u64_hex"): "elf_value",
    ("elf", "e_entry_u32_hex"): "elf_value",
    ("elf", "entry_point_u64_hex"): "elf_value",
    ("elf", "entry_point_u32_hex"): "elf_value",
    ("elf", "e_phoff_u64_hex"): "elf_value",
    ("elf", "e_phoff_u32_hex"): "elf_value",
    ("elf", "e_shoff_u64_hex"): "elf_value",
    ("elf", "e_shoff_u32_hex"): "elf_value",
    ("elf", "e_phoff_hex"): "elf_value",
    ("elf", "e_shoff_hex"): "elf_value",
    ("elf", "e_type_name"): "elf_value",
    ("elf", "type_name"): "elf_value",
    ("elf", "elf_type"): "elf_value",
    ("elf", "e_type_constant"): "elf_value",
    ("elf", "machine_name"): "elf_value",
    ("elf", "machine"): "elf_value",
    ("elf", "machine_description"): "elf_value",
    ("elf", "e_machine_description"): "elf_value",
    ("elf", "e_machine_name"): "elf_value",
    ("elf", "e_machine_constant"): "elf_value",
    ("elf", "machine_constant"): "elf_value",
    ("elf", "architecture"): "elf_value",
    ("elf", "arch"): "elf_value",
    ("elf", "cpu_architecture"): "elf_value",
    ("elf", "cpu_arch"): "elf_value",
    ("elf", "uname_arch"): "elf_value",
    ("elf", "target_arch"): "elf_value",
    ("elf", "goarch"): "elf_value",
    ("elf", "go_arch"): "elf_value",
    ("elf", "byte_order"): "elf_value",
    ("elf", "endian"): "elf_value",
    ("elf", "bitness"): "elf_value",
    ("elf", "bits"): "elf_value",
    ("elf", "elf_bits"): "elf_value",
    ("elf", "class_bits"): "elf_value",
    ("elf", "os_abi"): "elf_value",
    ("elf", "osabi"): "elf_value",
}

_CLASS = {1: "ELFCLASS32", 2: "ELFCLASS64"}
_ETYPE = {0: "ET_NONE", 1: "ET_REL", 2: "ET_EXEC", 3: "ET_DYN", 4: "ET_CORE"}
_ETYPE_ALIASES = {"ET_NONE": ["NONE", "NONE (None)"], "ET_REL": ["REL", "REL (Relocatable file)", "relocatable"],
                  "ET_EXEC": ["EXEC", "EXEC (Executable file)", "executable"],
                  "ET_DYN": ["DYN", "DYN (Shared object file)", "DYN (Position-Independent Executable file)",
                             "shared object", "shared_object", "pie"],
                  "ET_CORE": ["CORE", "CORE (Core file)", "core"]}
# e_machine -> (EM_* constant, readelf "Machine:" text, `file` text). Arch/GOARCH come from _arch().
_MACHINE = {0: ("EM_NONE", "None", "no machine"), 2: ("EM_SPARC", "Sparc", "SPARC"),
            3: ("EM_386", "Intel 80386", "Intel 80386"), 4: ("EM_68K", "MC68000", "Motorola m68k"),
            6: ("EM_IAMCU", "Intel MCU", "Intel MCU"), 8: ("EM_MIPS", "MIPS R3000", "MIPS"),
            10: ("EM_MIPS_RS3_LE", "MIPS R4000 big-endian", "MIPS"), 15: ("EM_PARISC", "HPPA", "PA-RISC"),
            18: ("EM_SPARC32PLUS", "Sparc v8+", "SPARC32PLUS"), 20: ("EM_PPC", "PowerPC", "PowerPC or cisco 4500"),
            21: ("EM_PPC64", "PowerPC64", "64-bit PowerPC or cisco 7500"), 22: ("EM_S390", "IBM S/390", "IBM S/390"),
            40: ("EM_ARM", "ARM", "ARM"), 42: ("EM_SH", "Renesas / SuperH SH", "Renesas SH"),
            43: ("EM_SPARCV9", "Sparc v9", "SPARC V9"), 50: ("EM_IA_64", "Intel IA-64", "IA-64"),
            62: ("EM_X86_64", "Advanced Micro Devices X86-64", "x86-64"), 183: ("EM_AARCH64", "AArch64", "ARM aarch64"),
            243: ("EM_RISCV", "RISC-V", "UCB RISC-V"), 247: ("EM_BPF", "Linux BPF", "eBPF"),
            258: ("EM_LOONGARCH", "LoongArch", "LoongArch"), 0x9026: ("EM_ALPHA", "Alpha", "Alpha")}
_DATA = {1: "ELFDATA2LSB", 2: "ELFDATA2MSB"}
_OSABI = {0: "ELFOSABI_NONE", 1: "ELFOSABI_HPUX", 2: "ELFOSABI_NETBSD", 3: "ELFOSABI_GNU", 6: "ELFOSABI_SOLARIS",
          7: "ELFOSABI_AIX", 8: "ELFOSABI_IRIX", 9: "ELFOSABI_FREEBSD", 12: "ELFOSABI_OPENBSD", 97: "ELFOSABI_ARM",
          255: "ELFOSABI_STANDALONE"}
# other spellings an accepted_values list may use for the same constant (readelf / `file` / bare numbers)
_ALIASES = {"ELFCLASS32": ["ELF32", "32", "32-bit", "1", "class32"], "ELFCLASS64": ["ELF64", "64", "64-bit", "2",
            "class64"],
            "ELFDATA2LSB": ["LSB", "little", "little_endian", "little-endian", "2's complement, little endian", "1",
                            "le"],
            "ELFDATA2MSB": ["MSB", "big", "big_endian", "big-endian", "2's complement, big endian", "2", "be"]}


def _ehdr(b):
    """The parsed ELF header as a dict, or None (not ELF / truncated / bad class or data byte)."""
    if not b or len(b) < 52 or bytes(b[:4]) != b"\x7fELF" or b[4] not in (1, 2) or b[5] not in (1, 2):
        return None
    e, is64 = "<" if b[5] == 1 else ">", b[4] == 2
    if is64:
        if len(b) < 64:
            return None
        (typ, mach, ver, entry, phoff, shoff, flags, ehsz, phes, phn, shes, shn, shx) = \
            struct.unpack_from(e + "HHIQQQIHHHHHH", b, 16)
    else:
        (typ, mach, ver, entry, phoff, shoff, flags, ehsz, phes, phn, shes, shn, shx) = \
            struct.unpack_from(e + "HHIIIIIHHHHHH", b, 16)
    h = {"e": e, "is64": is64, "class": b[4], "data": b[5], "osabi": b[7], "type": typ, "machine": mach,
         "version": ver, "entry": entry, "phoff": phoff, "shoff": shoff, "flags": flags, "phentsize": phes,
         "phnum": phn, "shentsize": shes, "shnum": shn, "shstrndx": shx, "ehsize": ehsz, "ei_version": b[6],
         "abiversion": b[8], "raw": {"phnum": phn, "shnum": shn, "shstrndx": shx}}
    s0 = _shdr_at(b, h, shoff) if shoff else None
    if s0:
        if shn == 0:
            h["shnum"] = s0["size"]
        if phn == 0xFFFF:
            h["phnum"] = s0["info"]
        if shx == 0xFFFF:
            h["shstrndx"] = s0["link"]
    return h


def _shdr_at(b, h, off):
    if h["is64"]:
        if off + 64 > len(b):
            return None
        name, typ, _, _, soff, size, link, info = struct.unpack_from(h["e"] + "IIQQQQII", b, off)
    else:
        if off + 40 > len(b):
            return None
        name, typ, _, _, soff, size, link, info = struct.unpack_from(h["e"] + "IIIIIIII", b, off)
    return {"name": name, "type": typ, "offset": soff, "size": size, "link": link, "info": info}


def _sections(b, h):
    """[(name, shdr)] in section-header-table order (index 0 included), [] when absent/truncated."""
    if not h["shoff"] or h["shentsize"] < (64 if h["is64"] else 40):
        return []
    out = []
    for i in range(min(h["shnum"], 65536)):
        s = _shdr_at(b, h, h["shoff"] + i * h["shentsize"])
        if s is None:
            break
        out.append(s)
    strtab = b""
    if 0 < h["shstrndx"] < len(out):
        st = out[h["shstrndx"]]
        strtab = bytes(b[st["offset"]:st["offset"] + st["size"]])
    res = []
    for s in out:
        n = strtab[s["name"]:].split(b"\0", 1)[0] if s["name"] < len(strtab) else b""
        res.append((n.decode("utf-8", "replace"), s))
    return res


def _segments(b, h):
    """[(p_type, p_offset, p_filesz)] of the program header table."""
    if not h["phoff"] or h["phentsize"] < (56 if h["is64"] else 32):
        return []
    out = []
    for i in range(min(h["phnum"], 65536)):
        off = h["phoff"] + i * h["phentsize"]
        if h["is64"]:
            if off + 56 > len(b):
                break
            typ, _, poff, _, _, fsz = struct.unpack_from(h["e"] + "IIQQQQ", b, off)
        else:
            if off + 32 > len(b):
                break
            typ, poff, _, _, fsz = struct.unpack_from(h["e"] + "IIIII", b, off)
        out.append((typ, poff, fsz))
    return out


def _notes(blob, e):
    """[(name, type, desc)] of an ELF note area (4-byte aligned name/desc, the GNU layout for both classes)."""
    out, off = [], 0
    while off + 12 <= len(blob):
        nsz, dsz, typ = struct.unpack_from(e + "III", blob, off)
        off += 12
        name = blob[off:off + nsz].rstrip(b"\0")
        off += (nsz + 3) & ~3
        if off + dsz > len(blob):
            break
        out.append((name, typ, blob[off:off + dsz]))
        off += (dsz + 3) & ~3
    return out


def _build_id(b, h, secs):
    areas = [bytes(b[s["offset"]:s["offset"] + s["size"]]) for n, s in secs if n == ".note.gnu.build-id"]
    areas += [bytes(b[s["offset"]:s["offset"] + s["size"]]) for n, s in secs
              if s["type"] == 7 and n != ".note.gnu.build-id"]
    if not secs:
        areas += [bytes(b[o:o + sz]) for t, o, sz in _segments(b, h) if t == 4]
    for a in areas:
        for name, typ, desc in _notes(a, h["e"]):
            if name == b"GNU" and typ == 3 and desc:
                return desc.hex()
    return "none"


def _interp(b, h):
    for t, o, sz in _segments(b, h):
        if t == 3:
            raw = bytes(b[o:o + sz]).split(b"\0", 1)[0]
            return raw.decode("utf-8", "replace") if raw else "none"
    return "none"


def _arch(h):
    """(uname -m style arch, Go GOARCH or None) for the header's machine + class + data, or (None, None)."""
    m, w64, le = h["machine"], h["is64"], h["data"] == 1
    if m == 62:
        return "x86_64", ("amd64" if w64 else "amd64p32")
    if m in (3, 6):
        return "i386", "386"
    if m == 183:
        return ("aarch64" if le else "aarch64_be"), ("arm64" if le else None)
    if m == 40:
        return ("arm" if le else "armeb"), ("arm" if le else None)
    if m in (8, 10):
        a = "mips64" if w64 else "mips"
        return a + ("el" if le else ""), a + ("le" if le else "")
    if m == 21:
        return ("ppc64le", "ppc64le") if le else ("ppc64", "ppc64")
    if m == 20:
        return ("ppcle" if le else "ppc"), None
    if m == 22:
        return ("s390x", "s390x") if w64 else ("s390", None)
    if m == 243:
        return ("riscv64", "riscv64") if w64 else ("riscv32", None)
    if m == 258:
        return ("loongarch64", "loong64") if w64 else ("loongarch32", None)
    if m == 43:
        return "sparc64", "sparc64"
    if m in (2, 18):
        return "sparc", None
    other = {50: "ia64", 4: "m68k", 42: "sh", 15: "parisc64" if w64 else "parisc", 0x9026: "alpha", 247: "bpf"}
    return other.get(m), None


def _hexf(f, h):
    """<member>[_uNN]_hex -> Hex of the raw Elf_Ehdr member (width from the name, else the struct width)."""
    m = re.match(r"^(.*?)(?:_u(8|16|32|64))?_hex$", f)
    base = m.group(1).replace("e_ident_", "ei_")
    base = {"entry_point": "e_entry", "ei_abi_version": "ei_abiversion"}.get(base, base)
    addr = 16 if h["is64"] else 8
    raw = h["raw"]
    members = {"ei_class": (h["class"], 2), "ei_data": (h["data"], 2), "ei_version": (h["ei_version"], 2),
               "ei_osabi": (h["osabi"], 2), "ei_abiversion": (h["abiversion"], 2), "e_type": (h["type"], 4),
               "e_machine": (h["machine"], 4), "e_version": (h["version"], 8), "e_entry": (h["entry"], addr),
               "e_phoff": (h["phoff"], addr), "e_shoff": (h["shoff"], addr), "e_flags": (h["flags"], 8),
               "e_ehsize": (h["ehsize"], 4), "e_phentsize": (h["phentsize"], 4), "e_phnum": (raw["phnum"], 4),
               "e_shentsize": (h["shentsize"], 4), "e_shnum": (raw["shnum"], 4),
               "e_shstrndx": (raw["shstrndx"], 4)}
    if base not in members:
        return None
    v, width = members[base]
    if m.group(2):
        width = int(m.group(2)) // 4
    return Hex(v, width) if v < (1 << (4 * width)) else None


def _enum(name, ctx, aliases=None):
    """The constant name, or the accepted_values entry that spells the same constant."""
    fmt = ((ctx or {}).get("question") or {}).get("answer_format") or {}
    acc = fmt.get("accepted_values") or fmt.get("values") or []
    if not isinstance(acc, (list, tuple)) or not acc:
        return name
    cands = [name.lower()] + [a.lower() for a in (aliases if aliases is not None else _ALIASES.get(name, []))]
    low = {str(a).strip().lower(): str(a) for a in acc}
    for c in cands:
        if c in low:
            return low[c]
    return name


def elf_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, ctx)
    except Exception:  # noqa: BLE001 -- a malformed ELF never raises past the extractor
        return None


def _value(b, ctx):
    f = (ctx or {}).get("field") or ""
    h = _ehdr(b)
    if h is None:
        return "none"
    if f in ("type_u16_hex", "elf_type_u16_hex", "flags_u32_hex"):
        f = "e_" + f.replace("elf_", "")
    if f.endswith("_hex") and "build_id" not in f:
        return _hexf(f, h)
    if f == "e_type":
        return h["type"]
    if f in ("e_type_name", "type_name", "elf_type", "e_type_constant"):
        n = _ETYPE.get(h["type"])
        return _enum(n, ctx, _ETYPE_ALIASES.get(n, [])) if n else str(h["type"])
    if f == "e_machine":
        return h["machine"]
    if f in ("architecture", "arch", "cpu_architecture", "cpu_arch", "uname_arch", "target_arch", "goarch",
             "go_arch"):
        a, g = _arch(h)
        v = g if "go" in f else a
        if v is None:
            return None
        mt = _MACHINE.get(h["machine"], ("", "", ""))
        return _enum(v, ctx, [x for x in (g, a) + mt if x])
    if "machine" in f:
        mt = _MACHINE.get(h["machine"])
        if mt is None:
            return None
        a, g = _arch(h)
        v = mt[0] if f in ("e_machine_name", "e_machine_constant", "machine_constant") else mt[1]
        return _enum(v, ctx, [x for x in mt + (a, g) if x])
    if f in ("endianness", "byte_order", "endian"):
        v = "little" if h["data"] == 1 else "big"
        return _enum(v, ctx, _ALIASES[_DATA[h["data"]]] + [_DATA[h["data"]]])
    if f in ("bitness", "bits", "elf_bits", "class_bits"):
        return 64 if h["is64"] else 32
    if f == "elf_class":
        v = "ELF64" if h["is64"] else "ELF32"
        return _enum(v, ctx, _ALIASES[_CLASS[h["class"]]] + [_CLASS[h["class"]]])
    if "class" in f:
        return _enum(_CLASS[h["class"]], ctx)
    if f in ("ei_data", "e_ident_data", "data_encoding"):
        return _enum(_DATA[h["data"]], ctx)
    if f in ("ei_abiversion", "e_ident_abiversion", "abi_version"):
        return h["abiversion"]
    if f in ("ei_version", "e_ident_version"):
        return h["ei_version"]
    if "osabi" in f or f == "os_abi":
        n = _OSABI.get(h["osabi"], str(h["osabi"]))
        return _enum(n, ctx, ["UNIX - System V", "SYSV", "System V", "none", "0"] if h["osabi"] == 0 else
                     ["UNIX - GNU", "GNU", "Linux", "3"] if h["osabi"] == 3 else [])
    if f == "e_version":
        return h["version"]
    if f == "e_shstrndx":
        return h["shstrndx"]
    if f in ("e_shnum", "section_count", "number_of_sections", "section_header_count"):
        return h["shnum"]
    if f in ("e_phnum", "program_header_count", "number_of_program_headers", "segment_count"):
        return h["phnum"]
    if "interp" in f:
        return _interp(b, h)
    secs = _sections(b, h)
    if "build_id" in f:
        return _build_id(b, h, secs)
    if "names" in f:
        return [n for i, (n, s) in enumerate(secs) if not (i == 0 and s["type"] == 0)]
    return None
