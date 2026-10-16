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
Not ELF / truncated header -> "none"; a field the file lacks (no PT_INTERP, no build-id note) -> "none"."""
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
}

_CLASS = {1: "ELFCLASS32", 2: "ELFCLASS64"}
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
         "phnum": phn, "shentsize": shes, "shnum": shn, "shstrndx": shx}
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


def _enum(name, ctx):
    """The constant name, or the accepted_values entry that spells the same constant."""
    fmt = ((ctx or {}).get("question") or {}).get("answer_format") or {}
    acc = fmt.get("accepted_values") or fmt.get("values") or []
    if not isinstance(acc, (list, tuple)) or not acc:
        return name
    cands = [name.lower()] + [a.lower() for a in _ALIASES.get(name, [])]
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
    if "type" in f:
        return Hex(h["type"], 4) if f.endswith("_hex") else h["type"]
    if "flags" in f:
        return Hex(h["flags"], 8)
    if "class" in f:
        return _enum(_CLASS[h["class"]], ctx)
    if f in ("ei_data", "e_ident_data", "data_encoding", "endianness"):
        return _enum(_DATA[h["data"]], ctx)
    if "osabi" in f:
        return _OSABI.get(h["osabi"], str(h["osabi"]))
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
