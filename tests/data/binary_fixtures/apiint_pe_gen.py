"""Minimal PE32+ (AMD64 console EXE) whose only content is an import directory: stdlib struct writer, no pefile.
usage: python3 apiint_pe_gen.py out.bin dll:func,func [dll:func ...]"""
import struct, sys

out, specs = sys.argv[1], [a.split(":") for a in sys.argv[2:]]
SA, FA, RVA = 0x1000, 0x200, 0x1000   # one .idata section at RVA 0x1000, file 0x200
n = len(specs)
desc = 20 * (n + 1)
thunks, cur = [], desc
for dll, fs in specs:
    k = len(fs.split(",")) + 1
    thunks.append((cur, cur + 8 * k))   # ILT, IAT
    cur += 16 * k
body = bytearray(cur)
strs = bytearray()


def sadd(b):
    global strs
    o = cur + len(strs)
    strs += b
    if len(strs) % 2:
        strs += b"\0"
    return o


for i, (dll, fs) in enumerate(specs):
    ilt, iat = thunks[i]
    for j, f in enumerate(fs.split(",")):
        hn = sadd(struct.pack("<H", 0) + f.encode() + b"\0")
        struct.pack_into("<Q", body, ilt + 8 * j, RVA + hn)
        struct.pack_into("<Q", body, iat + 8 * j, RVA + hn)
    nm = sadd(dll.encode() + b"\0")
    struct.pack_into("<IIIII", body, 20 * i, RVA + ilt, 0, 0, RVA + nm, RVA + iat)
sec = bytes(body + strs)
raw = (len(sec) + FA - 1) // FA * FA
dos = b"MZ" + b"\0" * 0x3a + struct.pack("<I", 0x40)
coff = struct.pack("<HHIIIHH", 0x8664, 1, 0, 0, 0, 240, 0x22)
opt = struct.pack("<HBBIIIII", 0x20b, 14, 0, 0, raw, 0, RVA, RVA)
opt += struct.pack("<QIIHHHHHHIIIIHHQQQQII", 0x140000000, SA, FA, 6, 0, 0, 0, 6, 0, 0,
                   RVA + ((len(sec) + SA - 1) // SA) * SA, FA, 0, 3, 0x8160, 0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
dd = [(0, 0)] * 16
dd[1] = (RVA, desc)
dd[12] = (RVA + thunks[0][1], 8)
opt += b"".join(struct.pack("<II", *d) for d in dd)
sh = struct.pack("<8sIIIIIIHHI", b".idata", len(sec), RVA, raw, FA, 0, 0, 0, 0, 0xC0000040)
hdr = dos + b"PE\0\0" + coff + opt + sh
open(out, "wb").write(hdr.ljust(FA, b"\0") + sec.ljust(raw, b"\0"))
