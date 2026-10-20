"""Minimal aPLib PACKER (greedy; literals, 4-bit short literal-zero, gamma long matches, 0x00 end marker) -- written
from the aPLib bitstream spec, independent of lib.binary's depacker. pack(data) -> raw aPLib stream (no AP32 header);
pack_ap32(data) -> with the 24-byte 'AP32' safe header (aPPack's format)."""
import struct, zlib


class _W:
    def __init__(self):
        self.out, self.tag, self.n = bytearray(), None, 0

    def bit(self, b):
        if self.n == 0:
            self.tag, self.n = len(self.out), 8
            self.out.append(0)
        self.n -= 1
        if b:
            self.out[self.tag] |= 1 << self.n

    def gamma(self, v):
        bits = bin(v)[3:]
        for k, c in enumerate(bits):
            self.bit(int(c))
            self.bit(k < len(bits) - 1)

    def byte(self, c):
        self.out.append(c)


def pack(data):
    w, i, lwm = _W(), 1, 0
    w.byte(data[0])
    while i < len(data):
        best_l, best_o = 0, 0
        for o in range(1, min(i, 0x7FFF) + 1):
            l = 0
            while i + l < len(data) and data[i + l] == data[i + l - o] and l < 255:
                l += 1
            adj = (o >= 32000) + (o >= 1280) + (2 if o < 128 else 0)
            if l >= 2 + adj and l > best_l:
                best_l, best_o = l, o
        if best_l:
            o = best_o
            adj = (o >= 32000) + (o >= 1280) + (2 if o < 128 else 0)
            w.bit(1); w.bit(0)
            w.gamma((o >> 8) + (2 if lwm else 3))
            w.byte(o & 255)
            w.gamma(best_l - adj)
            i, lwm = i + best_l, 1
        elif data[i] == 0:
            for b in (1, 1, 1, 0, 0, 0, 0):
                w.bit(b)
            i, lwm = i + 1, 0
        else:
            w.bit(0)
            w.byte(data[i])
            i, lwm = i + 1, 0
    w.bit(1); w.bit(1); w.bit(0)
    w.byte(0)
    return bytes(w.out)


def pack_ap32(data):
    p = pack(data)
    return b"AP32" + struct.pack("<IIIII", 24, len(p), zlib.crc32(p), len(data), zlib.crc32(data)) + p
