"""usage: python3 macho_fat64_pack.py out.bin thin1.o thin2.o -- hand-packs a FAT_MAGIC_64 (0xcafebabf) header:
fat_arch_64 {cputype, cpusubtype, u64 offset, u64 size, u32 align=14, u32 reserved}, slices 16 KiB aligned."""
import struct, sys
out, thins = sys.argv[1], [open(p, "rb").read() for p in sys.argv[2:]]
hdr, body, off = struct.pack(">II", 0xcafebabf, len(thins)), b"", 0x4000
for t in thins:
    cpu, sub = struct.unpack("<II", t[4:12])
    hdr += struct.pack(">IIQQII", cpu, sub, off, len(t), 14, 0)
    off += -(-len(t) // 0x4000) * 0x4000
blob = bytearray(hdr.ljust(0x4000, b"\0"))
for t in thins:
    blob += t.ljust(-(-len(t) // 0x4000) * 0x4000, b"\0")
open(out, "wb").write(bytes(blob))
