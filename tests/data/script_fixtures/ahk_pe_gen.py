"""Stdlib-only PE32+ writer for the Ahk2Exe carrier fixtures: one .rsrc section holding RT_RCDATA (10) named
`>AUTOHOTKEY SCRIPT<` (lang 0x409) = the script bytes (UTF-8 BOM, comments stripped as Ahk2Exe does).
usage: python3 -I ahk_pe_gen.py <script.ahk> <out.exe> [resource name]"""
import struct
import sys

src, out = open(sys.argv[1], "rb").read(), sys.argv[2]
rname = (sys.argv[3] if len(sys.argv) > 3 else ">AUTOHOTKEY SCRIPT<").encode("utf-16-le")
script = b"\xef\xbb\xbf" + b"\n".join(l for l in src.splitlines() if not l.lstrip().startswith(b";")) + b"\n"
RVA, FOFF = 0x1000, 0x200
# resource tree at .rsrc+0: root dir (1 id entry: type 10) @0x00, type dir (1 named entry) @0x18, name dir (1 id
# entry: lang 0x409) @0x30, data entry @0x48, then the name string (u16 length + UTF-16LE), then the data (16-aligned)
string = struct.pack("<H", len(rname) // 2) + rname
name_off = 0x58
data_off = (name_off + len(string) + 15) & ~15
rsrc = struct.pack("<IIHHHH", 0, 0, 0, 0, 0, 1) + struct.pack("<II", 10, 0x80000000 | 0x18)
rsrc += struct.pack("<IIHHHH", 0, 0, 0, 0, 1, 0) + struct.pack("<II", 0x80000000 | name_off, 0x80000000 | 0x30)
rsrc += struct.pack("<IIHHHH", 0, 0, 0, 0, 0, 1) + struct.pack("<II", 0x409, 0x48)
rsrc += struct.pack("<IIII", RVA + data_off, len(script), 65001, 0)
rsrc = (rsrc + string).ljust(data_off, b"\0") + script
raw_size = (len(rsrc) + 0x1ff) & ~0x1ff
virt_size = len(rsrc)
dos = b"MZ" + b"\0" * 0x3a + struct.pack("<I", 0x40)
coff = b"PE\0\0" + struct.pack("<HHIIIHH", 0x8664, 1, 0, 0, 0, 240, 0x22)
opt = struct.pack("<HBBIIIII", 0x20b, 14, 0, 0, 0, 0, 0, 0)          # magic .. BaseOfCode (no code)
opt += struct.pack("<QIIHHHHHHIIIIHHQQQQII", 0x140000000, 0x1000, 0x200, 6, 0, 0, 0, 6, 0, 0,
                   RVA + ((virt_size + 0xfff) & ~0xfff), FOFF, 0, 2, 0x8160, 0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
dirs = [(0, 0)] * 16
dirs[2] = (RVA, virt_size)
opt += b"".join(struct.pack("<II", *d) for d in dirs)
sec = struct.pack("<8sIIIIIIHHI", b".rsrc", virt_size, RVA, raw_size, FOFF, 0, 0, 0, 0, 0x40000040)
hdr = (dos + coff + opt + sec).ljust(FOFF, b"\0")
open(out, "wb").write(hdr + rsrc.ljust(raw_size, b"\0"))
