"""Stdlib NSIS 3 installer writer for the nsis_exe_* fixtures (no makensis on the host).

python3 -I nsis_exe_gen.py spec.json out.exe
spec: {"unicode": bool, "comp": "deflate"|"lzma", "solid": bool, "truncate": int|null,
       "strcpy": ["..."],            # Section: StrCpy $0 "<s>" per item
       "files": [["name", "text"]]}  # Section: SetOutPath $INSTDIR / File name
Layout (NSIS fileform.h): PE32 stub padded to 512 | firstheader (flags, 0xDEADBEEF, "NullsoftInst", header_size,
archive_size) | header block (u32 len | 0x80000000 compressed) | data blocks (u32 len | compressed) | CRC32.
Header: flags + 8 block headers (pages, sections, entries, strings, langtables, ctlcolors, bgfont, data) + fields;
entries are {which, offsets[6]} (EW_RET 1, EW_CREATEDIR 11, EW_EXTRACTFILE 20, EW_ASSIGNVAR 25); strings are
UTF-16LE (Unicode True) with NS 3 codes 1-4 (LANG/SHELL/VAR/SKIP) + one CODE_SHORT(idx) char.
"""
import json
import lzma
import struct
import sys
import zlib

spec, out = json.load(open(sys.argv[1])), sys.argv[2]
uni = spec.get("unicode", True)
VAR, INSTDIR = 3, 21


class Strings:
    def __init__(self):
        self.buf = bytearray(b"\0\0" if uni else b"\0")

    def add(self, s):
        unit = 2 if uni else 1
        ptr = len(self.buf) // unit
        for i, part in enumerate(s.split("$INSTDIR")):
            if i:
                self.buf += struct.pack("<HH", VAR, 0x8080 | (INSTDIR & 0x7f) | (INSTDIR >> 7) << 8) if uni else bytes(
                    [VAR, 0x80 | (INSTDIR & 0x7f), 0x80 | (INSTDIR >> 7)])
            self.buf += part.encode("utf-16-le" if uni else "latin-1")
        self.buf += b"\0" * unit
        return ptr


def comp(b):
    c = spec.get("comp", "deflate")
    if c == "lzma":
        props = {"id": lzma.FILTER_LZMA1, "dict_size": 1 << 16, "lc": 3, "lp": 0, "pb": 2}
        return bytes([0x5D]) + struct.pack("<I", 1 << 16) + lzma.compress(b, format=lzma.FORMAT_RAW, filters=[props])
    co = zlib.compressobj(9, zlib.DEFLATED, -15)                          # NSIS zlib: raw deflate
    return co.compress(b) + co.flush()


st, ent, data = Strings(), [], bytearray()
if spec.get("files"):
    ent.append((11, [st.add("$INSTDIR"), 1, 0, 0, 0, 0]))               # SetOutPath $INSTDIR
for name, text in spec.get("files", []):
    raw = text.encode()
    off = len(data)
    if spec.get("solid"):
        data += struct.pack("<I", len(raw)) + raw
    else:
        cb = comp(raw)
        data += struct.pack("<I", 0x80000000 | len(cb)) + cb
    ent.append((20, [3, st.add(name), off, 0, 0, 0]))                    # File (EW_EXTRACTFILE)
for s in spec.get("strcpy", []):
    ent.append((25, [0, st.add(s), 0, 0, 0, 0]))                         # StrCpy $0 "s" (EW_ASSIGNVAR)
ent.append((1, [0] * 6))                                                  # SectionEnd -> Return
st.add("Huntress Analysis")

entries = b"".join(struct.pack("<7i", w, *o) for w, o in ent)
sname = (b"\0" * (2048 if uni else 1024))
section = struct.pack("<6i", 0, 0, len(ent), 0, 0, 0) + sname             # name_ptr code code_size size_kb flags itypes
langtab = struct.pack("<Hii", 0x409, 0, 0)
fields = struct.pack("<3i", 0, 0, 0) + struct.pack("<6i", -1, -1, -1, -1, -1, -1) + struct.pack("<10i", *[-1] * 10) \
    + struct.pack("<33i", *[0] * 33) + struct.pack("<2i", 0, 0) + struct.pack("<3i", 0, 0, 0)
hsize = 4 + 64 + len(fields)
offs, cur = [], hsize
for blob, num in ((b"", 0), (section, 1), (entries, len(ent)), (bytes(st.buf), 0), (langtab, 1), (b"", 0), (b"", 0),
                  (b"", 0)):
    offs.append((cur, num))
    cur += len(blob)
header = struct.pack("<i", 0) + b"".join(struct.pack("<ii", o, n) for o, n in offs) + fields + section + entries \
    + bytes(st.buf) + langtab
assert len(header) == cur

if spec.get("solid"):
    body = comp(struct.pack("<I", len(header)) + header + bytes(data))
else:
    hb = comp(header)
    body = struct.pack("<I", 0x80000000 | len(hb)) + hb + bytes(data)
total = 28 + len(body) + 4
first = struct.pack("<II", 0, 0xDEADBEEF) + b"NullsoftInst" + struct.pack("<II", len(header), total)
arc = first + body
arc += struct.pack("<I", zlib.crc32(arc[0:]) & 0xffffffff)
if spec.get("truncate"):
    arc = arc[:spec["truncate"]]

# PE32 i386 stub: one .text section (ret), file alignment 0x200 -> the overlay starts 512-aligned
dos = b"MZ" + b"\0" * 0x3a + struct.pack("<I", 0x40)
coff = b"PE\0\0" + struct.pack("<HHIIIHH", 0x14c, 1, 0, 0, 0, 224, 0x102)
opt = struct.pack("<HBBIIIIIII", 0x10b, 6, 0, 0x200, 0, 0, 0x1000, 0x1000, 0x2000, 0x400000)
opt += struct.pack("<IIHHHHHHIIIIHHIIIIII", 0x1000, 0x200, 4, 0, 0, 0, 4, 0, 0, 0x2000, 0x200, 0, 2, 0x8140,
                   0x100000, 0x1000, 0x100000, 0x1000, 0, 16) + b"\0" * 128
sec = struct.pack("<8sIIIIIIHHI", b".text", 1, 0x1000, 0x200, 0x200, 0, 0, 0, 0, 0x60000020)
pe = (dos + coff + opt + sec).ljust(0x200, b"\0") + b"\xc3".ljust(0x200, b"\0")
open(out, "wb").write(pe + arc)
