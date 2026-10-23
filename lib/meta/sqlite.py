"""SQLite 3 fields (GM-verified). Header (sqlite.org/fileformat2.html, 100 bytes, BIG-endian): "SQLite format 3\\0" @0,
page size u16 @16 where the stored value 1 means 65536. The other SQLite fields stay SPECULATIVE in
lib.meta.prebuilt.sqlite until the GM verifies them; this module holds only what it has."""
import struct

_MAGIC = b"SQLite format 3\x00"


def page_size_bytes(data, ctx):
    """D23 "Page Me Maybe": the page size in bytes as a base-10 int (TT b604de80 + Mastery 6762559b GM-verified; a
    stored 1 = 65536). Promoted from prebuilt sqlite.sqlite_value with identical results: not SQLite (decoy / renamed
    impostor) -> "none"; a header that isn't a valid power-of-two page size >= 512 -> None."""
    if data is None:
        return None
    b = bytes(data[:100])
    if b[:16] != _MAGIC:
        return "none"
    if len(b) < 100:
        return None
    ps, = struct.unpack_from(">H", b, 16)
    ps = 65536 if ps == 1 else ps
    if ps < 512 or ps & (ps - 1):
        return None
    return ps
