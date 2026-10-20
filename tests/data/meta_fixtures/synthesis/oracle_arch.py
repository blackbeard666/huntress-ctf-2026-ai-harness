"""Independent oracle for the synthesis_arch fixtures: pyelftools (ELF header, cross-checked against `readelf -h`),
pefile (COFF Machine), macholib (Mach-O cputype), `file -b` for "is it a binary at all". Prints every field as JSON.
usage: oracle_arch.py <kit.zip>"""
import io
import json
import subprocess
import sys
import tempfile
import zipfile

import pefile
from elftools.elf.elffile import ELFFile
from elftools.elf.enums import ENUM_E_MACHINE
from macholib.mach_o import mach_header

ELF_ARCH = {("EM_X86_64", 64, True): "x86_64", ("EM_386", 32, True): "i386", ("EM_AARCH64", 64, True): "aarch64",
            ("EM_AARCH64", 64, False): "aarch64_be"}
PE_ARCH = {0x14C: "i386", 0x8664: "x86_64", 0xAA64: "aarch64"}
MACHO_ARCH = {0x0100000C: "aarch64", 0x01000007: "x86_64"}

z = zipfile.ZipFile(sys.argv[1])
rows = []
for n in z.namelist():
    b = z.read(n)
    with tempfile.NamedTemporaryFile() as t:
        t.write(b)
        t.flush()
        kind = subprocess.run(["file", "-b", t.name], capture_output=True, text=True).stdout
        re_ = subprocess.run(["readelf", "-h", t.name], capture_output=True, text=True).stdout
    if kind.startswith("ELF"):
        e = ELFFile(io.BytesIO(b))
        bits = e.elfclass
        assert ("big endian" in re_) == (not e.little_endian)
        rows.append((n, "elf", ENUM_E_MACHINE[e["e_machine"]], ELF_ARCH[(e["e_machine"], bits, e.little_endian)]))
    elif kind.startswith("PE32"):
        m = pefile.PE(data=b, fast_load=True).FILE_HEADER.Machine
        rows.append((n, "pe", m, PE_ARCH[m]))
    elif kind.startswith("Mach-O"):
        h = mach_header.from_str(b[:28], _endian_="<")
        rows.append((n, "macho", h.cputype, MACHO_ARCH[h.cputype]))
    else:
        rows.append((n, "data", None, None))


def groups(sel):
    g = {}
    for n, _, _, a in sel:
        g.setdefault(a, []).append(n)
    return g


elf = [r for r in rows if r[1] == "elf"]
binr = [r for r in rows if r[1] != "data"]
ga, ge = groups(binr), groups(elf)
lone = [v[0] for v in ga.values() if len(v) == 1]
print(json.dumps({
    "deployment_groups": list(ge.values()) or "none",
    "architecture_groups": list(ga.values()) or "none",
    "architecture_group_map": ga or "none",
    "elf_members": [r[0] for r in elf] or "none",
    "non_elf_members": [r[0] for r in rows if r[1] != "elf"] or "none",
    "machine_order": [r[0] for r in sorted(binr, key=lambda r: (r[2], r[0]))] or "none",
    "count_i386": sum(1 for r in binr if r[3] == "i386"),
    "odd_architecture_member": lone[0] if len(lone) == 1 and any(len(v) > 1 for v in ga.values()) else "none",
}, separators=(",", ":")))
