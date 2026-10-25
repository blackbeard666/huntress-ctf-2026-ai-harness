"""SQLite 3 databases embedded in / appended to another file (prebuilt, SPECULATIVE; D23 "Page Me Maybe" flavor:
databases "copied, truncated, embedded, and mislabeled"). The plain sqlite.* fields keep their @0-or-"none" rule
(lib.meta.sqlite / prebuilt sqlite*.py: a decoy must still answer "none"); ONLY the embedded_* family below looks past
offset 0, so a PNG/PE/ZIP carrying a database answers here and "none" there.

A header hit = "SQLite format 3\\0" with >= 100 header bytes after it and a valid page size u16 @+16 (BIG-endian;
1 = 65536, else a power of two 512..32768) -- the page-size check keeps the bare magic STRING that every binary
linking sqlite3 carries in .rdata from counting. For a PE host the hits at/after the overlay start
(max(PointerToRawData + SizeOfRawData), prefixed_zip.pe_overlay = pefile's get_overlay_data_start_offset) are
preferred; with none there, any hit counts.
  embedded_offset / embedded_offset_hex: file offset of the FIRST hit (0 for a plain database); _hex -> '0x' + lowercase,
    no padding (an offset has no struct width).
  embedded_count: number of hits (all header hits whose page size is valid; a dump of two DBs -> 2).
  embedded_page_size_bytes: the first hit's page size.
  embedded_carved_length: in-header database size in pages u32 @+28 x page size, clipped to EOF (a truncated carve
    keeps what is there); @+28 == 0 (legacy writer) -> the bytes to EOF.
  embedded_sha256: sha256 (lowercase hex) of those carved bytes.
  host_magic_prefix_hex_16: the first 16 bytes of the CONTAINER, lowercase hex without 0x (file.magic_prefix_hex_*
    spelling; a plain database -> the SQLite magic itself).
  declared_extension_matches: the member name's extension is sqlite/db/sqlite3/sqlitedb (case-insensitive) AND the
    content @0 is a SQLite header -- a PNG renamed .sqlite with a DB appended is still mislabeled (false); a .png
    carrying a DB -> false; database.db -> true. No member name -> None.
No hit anywhere (decoy / impostor) -> "none" for every field except declared_extension_matches (a bool: an impostor is
exactly the mislabel case).

Nested members: the artifact grammar may chain `x.zip -> app.apk -> assets/data.db`; the lane resolves the leaf by
basename, but when the bytes handed in are still a ZIP container (APK/JAR/ZIP) the `->` parts of ctx.member are
walked here (each part looked up by exact name, then by basename) before scanning."""
import hashlib
import io
import struct
import zipfile


FIELDS = {
    ("sqlite", "embedded_offset"): "embedded_value",
    ("sqlite", "embedded_offset_hex"): "embedded_value",
    ("sqlite", "embedded_offset_bytes"): "embedded_value",
    ("sqlite", "embedded_database_offset"): "embedded_value",
    ("sqlite", "embedded_count"): "embedded_value",
    ("sqlite", "embedded_database_count"): "embedded_value",
    ("sqlite", "embedded_page_size_bytes"): "embedded_value",
    ("sqlite", "embedded_page_size"): "embedded_value",
    ("sqlite", "embedded_carved_length"): "embedded_value",
    ("sqlite", "embedded_carved_length_bytes"): "embedded_value",
    ("sqlite", "embedded_carved_size_bytes"): "embedded_value",
    ("sqlite", "embedded_sha256"): "embedded_value",
    ("sqlite", "embedded_carved_sha256"): "embedded_value",
    ("sqlite", "host_magic_prefix_hex_16"): "embedded_value",
    ("sqlite", "host_magic_prefix_hex_*"): "embedded_value",
    ("sqlite", "declared_extension_matches"): "embedded_value",
    ("sqlite", "extension_matches_content"): "embedded_value",
    ("sqlite3", "embedded_offset"): "embedded_value",
    ("sqlite3", "embedded_offset_hex"): "embedded_value",
    ("sqlite3", "embedded_count"): "embedded_value",
    ("sqlite3", "embedded_page_size_bytes"): "embedded_value",
    ("sqlite3", "embedded_carved_length"): "embedded_value",
    ("sqlite3", "embedded_sha256"): "embedded_value",
    ("sqlite3", "host_magic_prefix_hex_16"): "embedded_value",
    ("sqlite3", "declared_extension_matches"): "embedded_value",
    ("database", "embedded_offset"): "embedded_value",
    ("database", "embedded_offset_hex"): "embedded_value",
    ("database", "embedded_count"): "embedded_value",
    ("database", "embedded_page_size_bytes"): "embedded_value",
    ("database", "embedded_carved_length"): "embedded_value",
    ("database", "embedded_sha256"): "embedded_value",
    ("database", "host_magic_prefix_hex_16"): "embedded_value",
    ("database", "declared_extension_matches"): "embedded_value",
}

_MAGIC = b"SQLite format 3\x00"
_EXTS = {"sqlite", "db", "sqlite3", "sqlitedb"}


def _page_size(b, off):
    if off + 100 > len(b):
        return None
    ps, = struct.unpack_from(">H", b, off + 16)
    ps = 65536 if ps == 1 else ps
    return ps if 512 <= ps <= 65536 and not ps & (ps - 1) else None


def _hits(b):
    """[(offset, page_size)] of every valid header hit, PE-overlay hits first when the host is a PE."""
    out, i = [], b.find(_MAGIC)
    while i >= 0:
        ps = _page_size(b, i)
        if ps:
            out.append((i, ps))
        i = b.find(_MAGIC, i + 1)
    if out and b[:2] == b"MZ":
        try:
            from .prefixed_zip import pe_overlay
            ov = pe_overlay(b)
        except Exception:  # noqa: BLE001 - not a parseable PE: plain scan order
            ov = None
        if ov is not None:
            late = [h for h in out if h[0] >= ov]
            if late:
                return late
    return out


def _descend(b, member):
    """Walk `a -> b -> c` member parts through ZIP containers (bytes handed in may be any level of the chain)."""
    parts = [p.strip() for p in str(member or "").split("->") if p.strip()]
    for part in parts:
        if b[:2] != b"PK":
            break
        try:
            z = zipfile.ZipFile(io.BytesIO(b))
            names = z.namelist()
        except Exception:  # noqa: BLE001 - not a readable zip: scan as is
            break
        name = part if part in names else next((n for n in names if n.rsplit("/", 1)[-1] == part.rsplit("/", 1)[-1]),
                                               None)
        if name is None:
            continue   # this level was already resolved by the lane
        try:
            b = z.read(name)
        except Exception:  # noqa: BLE001 - encrypted / damaged member
            return None
    return b


def _ext_matches(b, member):
    leaf = str(member or "").split("->")[-1].strip().rsplit("/", 1)[-1]
    if not leaf:
        return None
    ext = leaf.rsplit(".", 1)[-1].lower() if "." in leaf else ""
    return ext in _EXTS and b[:16] == _MAGIC and _page_size(b, 0) is not None


def _value(b, ctx):
    field = ctx.get("field") or ""
    member = ctx.get("member") or ""
    b = _descend(bytes(b), member)
    if b is None:
        return None
    if field in ("declared_extension_matches", "extension_matches_content"):
        return _ext_matches(b, member)
    hits = _hits(b)
    if not hits:
        return "none"
    if field.startswith("host_magic_prefix_hex"):
        try:
            n = int(field.rsplit("_", 1)[-1])
        except ValueError:
            n = 16
        return b[:n].hex() if 0 < n <= len(b) else None
    off, ps = hits[0]
    if field in ("embedded_offset", "embedded_offset_bytes", "embedded_database_offset"):
        return off
    if field == "embedded_offset_hex":
        return hex(off)
    if field in ("embedded_count", "embedded_database_count"):
        return len(hits)
    if field in ("embedded_page_size_bytes", "embedded_page_size"):
        return ps
    pages, = struct.unpack_from(">I", b, off + 28)
    end = min(len(b), off + pages * ps) if pages else len(b)
    carved = b[off:end]
    if field in ("embedded_carved_length", "embedded_carved_length_bytes", "embedded_carved_size_bytes"):
        return len(carved)
    if field in ("embedded_sha256", "embedded_carved_sha256"):
        return hashlib.sha256(carved).hexdigest()
    return None


def embedded_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, ctx)
    except Exception:  # noqa: BLE001 - defensive: never raise past the extractor
        return None
