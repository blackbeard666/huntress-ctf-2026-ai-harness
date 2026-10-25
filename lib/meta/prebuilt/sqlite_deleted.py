"""SQLite 3 deleted / unallocated content: freelist, freeblocks, carved rows (prebuilt, SPECULATIVE). Pure byte walk,
no sqlite3 import (a damaged / carved database still answers).

Header (sqlite.org/fileformat2.html, BIG-endian): page size u16 @16 (1 = 65536), reserved bytes u8 @20 (usable size =
page size - reserved), first freelist trunk page u32 @32, freelist page count u32 @36, text encoding u32 @56.
Freelist: trunk page = next trunk u32 @0, leaf count u32 @4, leaf page numbers u32 @8.. . The chain is walked from
@32 (loop / out-of-file / over-long leaf count stops the walk -- what was reached is reported).
  freelist_trunk_pages       chain order from @32 (JSON list)
  freelist_leaf_pages        sorted (JSON list); freelist_pages = sorted trunks + leaves
  freelist_page_count_walked trunks + leaves reached; freelist_count_mismatch = walked != header @36
B-tree pages: every in-file page NOT on the freelist whose type byte (page 1: @100) is 0x0d (table leaf) with a sane
header: first freeblock u16 @1, cell count u16 @3, cell content start u16 @5 (0 = 65536), fragmented bytes u8 @7, cell
pointer array after the 8-byte header. Freeblock = {next u16, size u16} chain, ascending offsets (btree.c freeSpace).
  freeblock_count     freeblocks summed over all table leaf pages; freeblock_bytes = their sizes summed
  unallocated_bytes   sum over table leaf pages of (content start - end of cell pointer array)
  fragmented_bytes    sum of u8 @7
  carved_strings      printable runs (UTF-8 decoded, str.isprintable, >= 6 chars) from each freeblock's bytes after its
                      4-byte header + every freelist LEAF page (whole page); JSON sorted unique
  deleted_row_candidates  one row per freeblock (page order, then chain order): record parse of the bytes at
      freeblock +4. Tried first literally (varint header length @+4, serial types, body that fills the freeblock); else
      as a real SQLite delete, where the 4-byte freeblock header overwrote payload-length + rowid + header-length (+ the
      first serial type): the serial types still present at +4 are followed by the body, the lost first column's
      length is what the body leaves over (0 -> null: an INTEGER PRIMARY KEY alias). The column count of a live cell
      on the same page picks the split when there is one. Values: int / float / text / blob as lowercase hex.
  secure_delete       true when something was freed (freelist pages or freeblocks) and every freed byte is zero
                      (freelist leaf pages whole, trunk pages after their leaf array, freeblock bodies after +4) --
                      PRAGMA secure_delete / SQLITE_SECURE_DELETE zero-fill; false otherwise.
Not "SQLite format 3\\0" (decoy, SQLite 2, renamed impostor) -> "none"; < 100 header bytes / bad page size -> None."""
import re
import struct

FIELDS = {
    ("sqlite", "freelist_trunk_pages"): "deleted_value",
    ("sqlite", "freelist_trunk_page_list"): "deleted_value",
    ("sqlite", "freelist_trunk_page_numbers"): "deleted_value",
    ("sqlite", "freelist_trunk_chain"): "deleted_value",
    ("sqlite", "freelist_leaf_pages"): "deleted_value",
    ("sqlite", "freelist_leaf_page_list"): "deleted_value",
    ("sqlite", "freelist_leaf_page_numbers"): "deleted_value",
    ("sqlite", "freelist_pages"): "deleted_value",
    ("sqlite", "freelist_page_numbers"): "deleted_value",
    ("sqlite", "freelist_trunk_count"): "deleted_value",
    ("sqlite", "freelist_trunk_page_count"): "deleted_value",
    ("sqlite", "freelist_leaf_count"): "deleted_value",
    ("sqlite", "freelist_leaf_page_count"): "deleted_value",
    ("sqlite", "freelist_page_count_walked"): "deleted_value",
    ("sqlite", "freelist_walked_page_count"): "deleted_value",
    ("sqlite", "walked_freelist_page_count"): "deleted_value",
    ("sqlite", "freelist_count_walked"): "deleted_value",
    ("sqlite", "freelist_count_mismatch"): "deleted_value",
    ("sqlite", "freelist_page_count_mismatch"): "deleted_value",
    ("sqlite", "freelist_mismatch"): "deleted_value",
    ("sqlite", "freeblock_count"): "deleted_value",
    ("sqlite", "freeblocks_count"): "deleted_value",
    ("sqlite", "total_freeblock_count"): "deleted_value",
    ("sqlite", "freeblock_bytes"): "deleted_value",
    ("sqlite", "freeblock_total_bytes"): "deleted_value",
    ("sqlite", "unallocated_bytes"): "deleted_value",
    ("sqlite", "unallocated_space_bytes"): "deleted_value",
    ("sqlite", "unallocated_byte_count"): "deleted_value",
    ("sqlite", "fragmented_bytes"): "deleted_value",
    ("sqlite", "fragmented_free_bytes"): "deleted_value",
    ("sqlite", "carved_strings"): "deleted_value",
    ("sqlite", "deleted_strings"): "deleted_value",
    ("sqlite", "recovered_strings"): "deleted_value",
    ("sqlite", "deleted_row_candidates"): "deleted_value",
    ("sqlite", "deleted_rows"): "deleted_value",
    ("sqlite", "carved_rows"): "deleted_value",
    ("sqlite", "recovered_rows"): "deleted_value",
    ("sqlite", "deleted_records"): "deleted_value",
    ("sqlite", "deleted_row_count"): "deleted_value",
    ("sqlite", "deleted_row_candidate_count"): "deleted_value",
    ("sqlite", "secure_delete"): "deleted_value",
    ("sqlite", "secure_delete_hint"): "deleted_value",
    ("sqlite", "secure_delete_suspected"): "deleted_value",
    ("sqlite", "secure_delete_likely"): "deleted_value",
    ("sqlite", "secure_delete_enabled"): "deleted_value",
    ("sqlite", "freelist_pages_zeroed"): "deleted_value",
    ("sqlite", "freelist_zeroed"): "deleted_value",
}

_MAGIC = b"SQLite format 3\x00"
_RUN = re.compile(r"[^\x00-\x1f\x7f-\x9f�]{6,}")


def _varint(b, i, end):
    """(value, next index) of an SQLite varint at b[i], or (None, i) when it runs past `end`."""
    v = 0
    for k in range(9):
        if i + k >= end:
            return None, i
        c = b[i + k]
        if k == 8:
            return (v << 8) | c, i + 9
        v = (v << 7) | (c & 0x7F)
        if c < 0x80:
            return v, i + k + 1
    return None, i


def _stlen(t):
    if t in (0, 8, 9):
        return 0
    if 1 <= t <= 6:
        return (1, 2, 3, 4, 6, 8)[t - 1]
    if t == 7:
        return 8
    if t >= 12:
        return (t - 12) // 2 if t % 2 == 0 else (t - 13) // 2
    return None   # 10, 11 reserved


def _value(t, raw, enc):
    if t == 0:
        return None
    if t == 8:
        return 0
    if t == 9:
        return 1
    if 1 <= t <= 6:
        return int.from_bytes(raw, "big", signed=True)
    if t == 7:
        return struct.unpack(">d", raw)[0]
    if t % 2 == 0:
        return raw.hex()
    return raw.decode(enc, "replace")


def _guess(raw, enc):
    """Value of the lost first column from its bytes alone."""
    if not raw:
        return None
    try:
        s = raw.decode(enc)
        if s.isprintable():
            return s
    except UnicodeDecodeError:
        pass
    if len(raw) in (1, 2, 3, 4, 6, 8):
        return int.from_bytes(raw, "big", signed=True)
    return raw.hex()


def _types(r, p, count=None, end=None):
    """Serial types parsed from r[p:end] (count of them, or until `end`) -> (types, index) or None."""
    out, end = [], len(r) if end is None else end
    while (count is None and p < end) or (count is not None and len(out) < count):
        t, q = _varint(r, p, end)
        if t is None or _stlen(t) is None:
            return None
        out.append(t)
        p = q
    return out, p


def _body(r, p, types, enc):
    vals = []
    for t in types:
        n = _stlen(t)
        vals.append(_value(t, bytes(r[p:p + n]), enc))
        p += n
    return vals


def _row(r, ncols, enc):
    """Best-effort record at a freeblock's +4 bytes `r` (see module doc), or None."""
    hl, p = _varint(r, 0, len(r))                       # literal: a full record header at +4
    if hl is not None and p <= hl <= len(r):
        ts = _types(r, p, end=hl)
        if ts and ts[1] == hl and sum(map(_stlen, ts[0])) == len(r) - hl and (ncols is None or len(ts[0]) == ncols):
            return _body(r, hl, ts[0], enc)
    best = None                                        # real delete: header-length (+ first type) overwritten
    for t in range(1, min(len(r), 64) + 1):
        ts = _types(r, 0, count=t)
        if ts is None:
            break
        types, p = ts
        left = len(r) - p - sum(map(_stlen, types))
        if left < 0:
            break
        for lost in (1, 0):
            if lost == 0 and left:
                continue
            if ncols is not None and t + lost != ncols:
                continue
            rank = (0 if lost and not left else 1 if not lost else 2, t)
            if best is None or rank < best[0]:
                first = [_guess(bytes(r[p:p + left]), enc)] if lost else []
                best = (rank, first + _body(r, p + left, types, enc))
    return best[1] if best else None


def _ncols(pg, hdr, ptr, usable, enc):
    """Column count of the first parseable live cell on a table leaf page, or None."""
    _ = enc
    off, = struct.unpack_from(">H", pg, ptr)
    if not hdr < off < usable:
        return None
    _pl, i = _varint(pg, off, usable)
    _rid, i = _varint(pg, i, usable)
    hl, j = _varint(pg, i, usable)
    if hl is None or hl < 1 or i + hl > usable:
        return None
    ts = _types(pg, j, end=i + hl)
    return len(ts[0]) if ts and ts[1] == i + hl else None


def _strings(chunk):
    s = bytes(chunk).decode("utf-8", "replace")
    return _RUN.findall(s)


def _facts(b):
    if len(b) < 100:
        return None
    raw, = struct.unpack_from(">H", b, 16)
    ps = 65536 if raw == 1 else raw
    if not (raw == 1 or (512 <= raw <= 32768 and not raw & (raw - 1))):
        return None
    usable = ps - b[20]
    if usable < 480:
        return None
    trunk0, nfree = struct.unpack_from(">2I", b, 32)
    enc = {2: "utf-16-le", 3: "utf-16-be"}.get(struct.unpack_from(">I", b, 56)[0], "utf-8")
    npages = len(b) // ps

    def page(n):
        return b[(n - 1) * ps:(n - 1) * ps + ps]

    trunks, leaves, seen, zero = [], [], set(), True
    t = trunk0
    while t and 1 <= t <= npages and t not in seen and len(seen) <= npages:
        seen.add(t)
        trunks.append(t)
        pg = page(t)
        nxt, k = struct.unpack_from(">2I", pg, 0)
        if k > (usable - 8) // 4:
            break
        for (lf,) in struct.iter_unpack(">I", pg[8:8 + 4 * k]):
            if 1 <= lf <= npages and lf not in seen:
                seen.add(lf)
                leaves.append(lf)
        if any(pg[8 + 4 * k:usable]):
            zero = False
        t = nxt
    carved = set()
    for lf in leaves:
        pg = page(lf)
        if any(pg):
            zero = False
        carved.update(_strings(pg))
    nfb = fbytes = unalloc = frag = 0
    rows = []
    for n in range(1, npages + 1):
        if n in seen:
            continue
        pg = page(n)
        hdr = 100 if n == 1 else 0
        if pg[hdr] != 0x0D:
            continue
        first, ncell, cstart = struct.unpack_from(">3H", pg, hdr + 1)
        cstart = cstart or 65536
        end_ptrs = hdr + 8 + 2 * ncell
        if not end_ptrs <= cstart <= usable or (first and not cstart <= first < usable):
            continue
        unalloc += cstart - end_ptrs
        frag += pg[hdr + 7]
        ncols = _ncols(pg, end_ptrs, hdr + 8, usable, enc) if ncell else None
        fb, hops = first, 0
        while fb and fb + 4 <= usable and hops < usable // 4:
            nxt, size = struct.unpack_from(">2H", pg, fb)
            if size < 4 or fb + size > usable:
                break
            body = pg[fb + 4:fb + size]
            nfb += 1
            fbytes += size
            if any(body):
                zero = False
            carved.update(_strings(body))
            row = _row(body, ncols, enc)
            if row is not None:
                rows.append(row)
            if nxt and nxt <= fb:
                break
            fb, hops = nxt, hops + 1
    return {"trunks": trunks, "leaves": sorted(leaves), "nfree": nfree, "walked": len(trunks) + len(leaves),
            "nfb": nfb, "fbytes": fbytes, "unalloc": unalloc, "frag": frag, "carved": sorted(carved), "rows": rows,
            "secure": bool((trunks or nfb) and zero)}


def deleted_value(data, ctx):
    try:
        if not data or bytes(data[:16]) != _MAGIC:
            return "none"
        f = _facts(bytes(data))
        if f is None:
            return None
        fld = ctx.get("field") or ""
        if fld in ("freelist_trunk_pages", "freelist_trunk_page_list", "freelist_trunk_page_numbers",
                   "freelist_trunk_chain"):
            return f["trunks"]
        if fld in ("freelist_leaf_pages", "freelist_leaf_page_list", "freelist_leaf_page_numbers"):
            return f["leaves"]
        if fld in ("freelist_pages", "freelist_page_numbers"):
            return sorted(f["trunks"] + f["leaves"])
        if fld in ("freelist_trunk_count", "freelist_trunk_page_count"):
            return len(f["trunks"])
        if fld in ("freelist_leaf_count", "freelist_leaf_page_count"):
            return len(f["leaves"])
        if fld in ("freelist_page_count_walked", "freelist_walked_page_count", "walked_freelist_page_count",
                   "freelist_count_walked"):
            return f["walked"]
        if fld in ("freelist_count_mismatch", "freelist_page_count_mismatch", "freelist_mismatch"):
            return f["walked"] != f["nfree"]
        if fld in ("freeblock_count", "freeblocks_count", "total_freeblock_count"):
            return f["nfb"]
        if fld in ("freeblock_bytes", "freeblock_total_bytes"):
            return f["fbytes"]
        if fld in ("unallocated_bytes", "unallocated_space_bytes", "unallocated_byte_count"):
            return f["unalloc"]
        if fld in ("fragmented_bytes", "fragmented_free_bytes"):
            return f["frag"]
        if fld in ("carved_strings", "deleted_strings", "recovered_strings"):
            return f["carved"]
        if fld in ("deleted_row_candidates", "deleted_rows", "carved_rows", "recovered_rows", "deleted_records"):
            return f["rows"]
        if fld in ("deleted_row_count", "deleted_row_candidate_count"):
            return len(f["rows"])
        if fld.startswith("secure_delete") or fld in ("freelist_pages_zeroed", "freelist_zeroed"):
            return f["secure"]
        return None
    except Exception:  # noqa: BLE001 -- defensive: never raise past the extractor
        return None
