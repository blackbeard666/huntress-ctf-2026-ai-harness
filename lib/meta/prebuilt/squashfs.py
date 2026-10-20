"""SquashFS 4.x superblock fields (prebuilt, SPECULATIVE -- never GM-asked yet); also the AppImage type-2 payload.

Superblock (96 bytes, little-endian): magic "hsqs" u32 @0, inode_count u32 @4, modification_time u32 @8 (unix
seconds = mkfs time, `unsquashfs -s` "Creation or last append time"), block_size u32 @12, fragment_entry_count u32
@16, compression_id u16 @20 (1 gzip 2 lzma 3 lzo 4 xz 5 lz4 6 zstd -- the names `unsquashfs -s` prints), block_log
u16 @22, flags u16 @24, id_count u16 @26, version_major u16 @28, version_minor u16 @30, root_inode_ref u64 @32,
bytes_used u64 @40, then the table starts.
mkfs_time_utc: the unix u32 rendered ISO-8601 UTC "YYYY-MM-DDTHH:MM:SSZ" (no other epoch in the format).
AppImage (type 2): an ELF runtime with "AI\\x02" at e_ident[8..10]; the squashfs image starts at the end of the ELF
section header table (e_shoff + e_shnum * e_shentsize), which is how the runtime finds its own payload.
No "hsqs" at the expected offset (wrong magic / big-endian "sqsh" / truncated) -> "none"."""
import datetime
import struct

from ..spell import Hex

_SB = ("inode_count", "modification_time", "block_size", "fragment_entry_count", "compression_id", "block_log",
       "flags", "id_count", "version_major", "version_minor", "root_inode_ref", "bytes_used")

FIELDS = {
    ("squashfs", "inode_count"): "sb_value",
    ("squashfs", "superblock_inode_count"): "sb_value",
    ("squashfs", "inodes"): "sb_value",
    ("squashfs", "mkfs_time_utc"): "sb_value",
    ("squashfs", "mkfs_time"): "sb_value",
    ("squashfs", "modification_time_utc"): "sb_value",
    ("squashfs", "modification_time"): "sb_value",
    ("squashfs", "creation_time_utc"): "sb_value",
    ("squashfs", "superblock_mkfs_time_utc"): "sb_value",
    ("squashfs", "mkfs_time_unix"): "sb_value",
    ("squashfs", "modification_time_unix"): "sb_value",
    ("squashfs", "block_size"): "sb_value",
    ("squashfs", "block_size_bytes"): "sb_value",
    ("squashfs", "superblock_block_size"): "sb_value",
    ("squashfs", "block_log"): "sb_value",
    ("squashfs", "compression"): "sb_value",
    ("squashfs", "compression_name"): "sb_value",
    ("squashfs", "compressor"): "sb_value",
    ("squashfs", "compression_algorithm"): "sb_value",
    ("squashfs", "compression_id"): "sb_value",
    ("squashfs", "compressor_id"): "sb_value",
    ("squashfs", "version"): "sb_value",
    ("squashfs", "superblock_version"): "sb_value",
    ("squashfs", "version_major"): "sb_value",
    ("squashfs", "version_minor"): "sb_value",
    ("squashfs", "fragment_entry_count"): "sb_value",
    ("squashfs", "fragment_count"): "sb_value",
    ("squashfs", "fragments"): "sb_value",
    ("squashfs", "id_count"): "sb_value",
    ("squashfs", "flags_u16_hex"): "sb_value",
    ("squashfs", "superblock_flags_u16_hex"): "sb_value",
    ("squashfs", "bytes_used"): "sb_value",
    ("squashfs", "filesystem_size_bytes"): "sb_value",
    ("squashfs", "magic"): "sb_value",
}

_COMP = {1: "gzip", 2: "lzma", 3: "lzo", 4: "xz", 5: "lz4", 6: "zstd"}


def superblock(b, off=0):
    """SquashFS 4 superblock at `off` as a dict, or None."""
    if not b or off < 0 or len(b) < off + 48 or bytes(b[off:off + 4]) != b"hsqs":
        return None
    v = struct.unpack_from("<IIIIHHHHHHQQ", b, off + 4)
    return dict(zip(_SB, v))


def _iso(t):
    return datetime.datetime.fromtimestamp(int(t), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sb_field(sb, field):
    """GM-spelled value of a superblock field (shared with the appimage module), or "none"."""
    f = field[len("superblock_"):] if field.startswith("superblock_") else field
    f = f[len("squashfs_"):] if f.startswith("squashfs_") else f
    if f in ("inode_count", "inodes"):
        return sb["inode_count"]
    if f in ("mkfs_time_utc", "mkfs_time", "modification_time_utc", "modification_time", "creation_time_utc"):
        return _iso(sb["modification_time"])
    if f in ("mkfs_time_unix", "modification_time_unix"):
        return sb["modification_time"]
    if f in ("block_size", "block_size_bytes"):
        return sb["block_size"]
    if f == "block_log":
        return sb["block_log"]
    if f in ("compression", "compression_name", "compressor", "compression_algorithm"):
        return _COMP.get(sb["compression_id"], "none")
    if f in ("compression_id", "compressor_id"):
        return sb["compression_id"]
    if f == "version":
        return "%d.%d" % (sb["version_major"], sb["version_minor"])
    if f in ("version_major", "version_minor", "id_count", "bytes_used", "fragment_entry_count"):
        return sb[f]
    if f in ("fragment_count", "fragments"):
        return sb["fragment_entry_count"]
    if f == "filesystem_size_bytes":
        return sb["bytes_used"]
    if f == "flags_u16_hex":
        return Hex(sb["flags"], 4)
    if f == "magic":
        return "hsqs"
    return None


def sb_value(data, ctx):
    if data is None:
        return None
    try:
        sb = superblock(data, 0)
        return sb_field(sb, ctx.get("field") or "") if sb else "none"
    except Exception:  # noqa: BLE001
        return None
