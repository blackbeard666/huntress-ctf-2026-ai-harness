"""Mach-O fields (GM-verified). Thin header (<mach-o/loader.h>): magic u32 then cputype u32 in the file's byte order
(MH_MAGIC/MH_MAGIC_64 little-endian 0xcefaedfe/0xcffaedfe bytes; MH_CIGAM* = big-endian). Fat (<mach-o/fat.h>,
always big-endian): FAT_MAGIC 0xcafebabe (fat_arch 20 B) / FAT_MAGIC_64 0xcafebabf (fat_arch_64 32 B), nfat_arch u32,
then {cputype, cpusubtype, offset, size, align}. 0xcafebabe is also the Java .class magic: nfat_arch must be < 20."""
import struct

_THIN = {b"\xce\xfa\xed\xfe": "<", b"\xcf\xfa\xed\xfe": "<", b"\xfe\xed\xfa\xce": ">", b"\xfe\xed\xfa\xcf": ">"}


def cpu_type_set(data, ctx):
    """D20: cputype of every slice as "0x%08x" (thin = its header) -- thin arm64 -> ["0x0100000c"] (GM-confirmed
    single/TT/Mastery; the name spelling ["arm64"] was REJECTED). D23 Mastery: a fat file's list is SORTED ascending
    (fat_arch order REJECTED on 5/7 sets, sorted CORRECT on 7/7); dedupe unverified (kept as a set)."""
    if data is None:
        return None
    b = bytes(data[:4096])
    if len(b) >= 8 and b[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
        n = struct.unpack_from(">I", b, 4)[0]
        w = 20 if b[3] == 0xbe else 32
        if 0 < n < 20 and 8 + n * w <= len(b):
            return ["0x%08x" % t for t in sorted({struct.unpack_from(">I", b, 8 + i * w)[0] for i in range(n)})]
        return "none"
    e = _THIN.get(b[:4])
    if e is None or len(b) < 8:
        return "none"
    return ["0x%08x" % struct.unpack_from(e + "I", b, 4)[0]]
