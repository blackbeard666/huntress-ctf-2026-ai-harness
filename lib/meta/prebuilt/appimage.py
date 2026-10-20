"""AppImage fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Type 2 AppImage = ELF runtime + appended SquashFS. The ELF e_ident bytes 8..10 carry the AppImage magic "AI" + type
byte (0x02; type 1 = ISO 9660 payload). The SquashFS starts where the ELF ends = e_shoff + e_shnum * e_shentsize
(the section header table is the last ELF structure; this is what the runtime's `--appimage-offset` prints).
Payload superblock fields reuse lib.meta.prebuilt.squashfs (inode_count, mkfs_time_utc, block_size, compression, ...).
Not ELF / no "AI" magic -> "none" (a plain ELF with an appended squashfs is not an AppImage); no "hsqs" at the
computed offset -> "none" for the squashfs fields."""
from .elf import _ehdr
from .squashfs import sb_field, superblock

FIELDS = {
    ("appimage", "type"): "ai_value",
    ("appimage", "appimage_type"): "ai_value",
    ("appimage", "magic_type"): "ai_value",
    ("appimage", "squashfs_offset"): "ai_value",
    ("appimage", "payload_offset"): "ai_value",
    ("appimage", "appimage_offset"): "ai_value",
    ("appimage", "runtime_size_bytes"): "ai_value",
    ("appimage", "elf_size_bytes"): "ai_value",
    ("appimage", "squashfs_*"): "ai_value",
    ("appimage", "inode_count"): "ai_value",
    ("appimage", "mkfs_time_utc"): "ai_value",
    ("appimage", "block_size"): "ai_value",
    ("appimage", "compression"): "ai_value",
    ("appimage", "compression_id"): "ai_value",
}

_OFFSET = ("squashfs_offset", "payload_offset", "appimage_offset", "runtime_size_bytes", "elf_size_bytes")


def appimage(b):
    """(type, squashfs_offset) of an AppImage, or None (not ELF / no AI magic)."""
    h = _ehdr(b)
    if h is None or bytes(b[8:10]) != b"AI":
        return None
    return b[10], h["shoff"] + h["shnum"] * h["shentsize"]


def ai_value(data, ctx):
    if data is None:
        return None
    try:
        ai = appimage(data)
        if ai is None:
            return "none"
        typ, off = ai
        field = ctx.get("field") or ""
        if field in ("type", "appimage_type", "magic_type"):
            return typ
        if field in _OFFSET:
            return off
        sb = superblock(data, off)
        if sb is None:
            return "none"
        f = field[len("squashfs_"):] if field.startswith("squashfs_") else field
        return sb_field(sb, f)
    except Exception:  # noqa: BLE001
        return None
