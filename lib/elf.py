"""ELF field extraction for the binary lane, emitting the GM's confirmed vocabulary (see lib/knowledge.py).
Needs pyelftools (in the project venv)."""
import io

from elftools.elf.elffile import ELFFile

from . import knowledge as K

TOOLCHAIN = {"_start", "__libc_start_main", "main", "register_tm_clones", "deregister_tm_clones",
             "frame_dummy", "__do_global_dtors_aux", "__libc_csu_init", "__libc_csu_fini", "_init", "_fini"}


def fields(data):
    """Dict of the common header fields in GM vocabulary. Pass raw ELF bytes."""
    elf = ELFFile(io.BytesIO(data))
    h = elf.header
    out = {
        "elf_class": K.ELF_CLASS.get(h["e_ident"]["EI_CLASS"], h["e_ident"]["EI_CLASS"]),
        "endianness": K.ELF_ENDIANNESS.get(h["e_ident"]["EI_DATA"], h["e_ident"]["EI_DATA"]),
        "machine": K.ELF_MACHINE.get(h["e_machine"], h["e_machine"]),
        "elf_type": h["e_type"],                       # e.g. ET_EXEC (as-is)
        "entry_point": hex(h["e_entry"]),              # lowercase 0x
        "has_symtab": K.BOOL[elf.get_section_by_name(".symtab") is not None],
    }
    return elf, out


def section_string(data, name):
    elf = ELFFile(io.BytesIO(data))
    sec = elf.get_section_by_name(name)
    return sec.data().split(b"\0", 1)[0].decode("utf-8", "replace") if sec else None


def exported_symbol(data):
    """The one defined GLOBAL/WEAK FUNC that isn't toolchain/CRT glue."""
    elf = ELFFile(io.BytesIO(data))
    for secname in (".symtab", ".dynsym"):
        sec = elf.get_section_by_name(secname)
        if not sec:
            continue
        for s in sec.iter_symbols():
            i = s["st_info"]
            if (i["type"] == "STT_FUNC" and i["bind"] in ("STB_GLOBAL", "STB_WEAK")
                    and s["st_shndx"] != "SHN_UNDEF" and s.name and s.name not in TOOLCHAIN
                    and not s.name.startswith("_")):
                return s.name
    return "none"
