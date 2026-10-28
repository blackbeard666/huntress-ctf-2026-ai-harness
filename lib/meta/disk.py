"""Raw disk-image (partition table) fields, GM-verified (virtual-disk containers stay speculative in prebuilt/disk.py)."""
import struct


def partition_start_lba_sequence(data, ctx=None):
    """D28 "Where It All Began": GPT (`EFI PART` at LBA1, sector 512/4096/1024/2048) -> StartingLBA u64 @+32 of every
    non-empty entry (16 zero type-GUID bytes = empty) in partition-array order; else MBR primary entries' u32 @+8
    (zero type skipped) + the EBR chain for 05/0f/85 -- [34] single, [60,93,148] TT, 12/12 Mastery sets (1..6 parts).
    A list of ints (spelled as compact JSON)."""
    if not data or len(data) < 512:
        return None
    for ss in (512, 4096, 1024, 2048):
        if data[ss:ss + 8] == b"EFI PART":
            ent_lba, n, esz = struct.unpack_from("<QII", data, ss + 72)
            base, out = ent_lba * ss, []
            for i in range(min(n, 4096)):
                off = base + i * esz
                if off + 48 > len(data):
                    break
                if data[off:off + 16] == b"\0" * 16:
                    continue
                out.append(struct.unpack_from("<Q", data, off + 32)[0])
            return out
    out = []
    for i in range(4):
        e = 446 + 16 * i
        typ, start = data[e + 4], struct.unpack_from("<I", data, e + 8)[0]
        if typ == 0:
            continue
        out.append(start)
        if typ in (0x05, 0x0F, 0x85):
            ext, cur, seen = start, start, set()
            while cur not in seen and cur * 512 + 512 <= len(data):
                seen.add(cur)
                b = cur * 512
                if data[b + 510:b + 512] != b"\x55\xaa":
                    break
                t1, s1 = data[b + 446 + 4], struct.unpack_from("<I", data, b + 446 + 8)[0]
                if t1:
                    out.append(cur + s1)
                t2, s2 = data[b + 462 + 4], struct.unpack_from("<I", data, b + 462 + 8)[0]
                if not t2:
                    break
                cur = ext + s2
    return out
