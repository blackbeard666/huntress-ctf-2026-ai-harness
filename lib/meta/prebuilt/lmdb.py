"""LMDB data.mdb meta-page fields (fmt `lmdb`) -- prebuilt, SPECULATIVE (never asked yet).

Pages 0 and 1 are the two meta pages (mdb.c MDB_meta after the page header; 64-bit build: 16-byte header so
mm_magic 0xBEEFC0DE u32 LE @16, mm_version u32 @20, mm_address @24, mm_mapsize u64 @32, mm_dbs[FREE, MAIN] 48 B each
@40/@88 (md_pad u32 = page size in the FREE db, md_flags u16, md_depth u16, branch/leaf/overflow pages, entries, root
u64), mm_last_pg u64 @136, mm_txnid u64 @144). A 32-bit build uses a 12-byte header and 4-byte size_t; both are read.
The CURRENT meta is the one with the larger txnid (mdb_env_pick_meta), which is what `mdb_stat -e` / env.info() show.
Wrong magic -> "none". Fixtures: python `lmdb` 2.1.1 writer; oracle = the same binding's reader (env.info()/stat())
on a read-only reopen (map_size=0 so mdb_env_open adopts the stored mm_mapsize)."""
import struct

FIELDS = {
    ("lmdb", "magic_u32_hex"): "lmdb_value",
    ("lmdb", "mm_magic_u32_hex"): "lmdb_value",
    ("lmdb", "meta_magic_u32_hex"): "lmdb_value",
    ("lmdb", "version"): "lmdb_value",
    ("lmdb", "mm_version"): "lmdb_value",
    ("lmdb", "format_version"): "lmdb_value",
    ("lmdb", "data_version"): "lmdb_value",
    ("lmdb", "meta_version"): "lmdb_value",
    ("lmdb", "map_size"): "lmdb_value",
    ("lmdb", "map_size_bytes"): "lmdb_value",
    ("lmdb", "mapsize"): "lmdb_value",
    ("lmdb", "mm_mapsize"): "lmdb_value",
    ("lmdb", "last_txn_id"): "lmdb_value",
    ("lmdb", "last_txnid"): "lmdb_value",
    ("lmdb", "txn_id"): "lmdb_value",
    ("lmdb", "txnid"): "lmdb_value",
    ("lmdb", "mm_txnid"): "lmdb_value",
    ("lmdb", "last_transaction_id"): "lmdb_value",
    ("lmdb", "last_page_number"): "lmdb_value",
    ("lmdb", "last_pgno"): "lmdb_value",
    ("lmdb", "last_page"): "lmdb_value",
    ("lmdb", "mm_last_pg"): "lmdb_value",
    ("lmdb", "page_size"): "lmdb_value",
    ("lmdb", "page_size_bytes"): "lmdb_value",
    ("lmdb", "psize"): "lmdb_value",
    ("lmdb", "entries"): "lmdb_value",
    ("lmdb", "entry_count"): "lmdb_value",
    ("lmdb", "main_db_entries"): "lmdb_value",
    ("lmdb", "md_entries"): "lmdb_value",
    ("lmdb", "depth"): "lmdb_value",
    ("lmdb", "main_db_depth"): "lmdb_value",
    ("lmdb", "branch_pages"): "lmdb_value",
    ("lmdb", "leaf_pages"): "lmdb_value",
    ("lmdb", "overflow_pages"): "lmdb_value",
    ("lmdb", "root_page"): "lmdb_value",
    ("lmdb", "main_db_root"): "lmdb_value",
    ("lmdb", "main_db_flags_u16_hex"): "lmdb_value",
    ("lmdb", "current_meta_page"): "lmdb_value",
}

MAGIC = 0xBEEFC0DE


def _meta(b, base, hdr, w):
    """One MDB_meta at page offset `base` (hdr = page-header size, w = sizeof(size_t)), or None."""
    o = base + hdr
    if len(b) < o + 8 + w * 2 + 2 * (8 + 5 * w) + 2 * w:
        return None
    magic, ver = struct.unpack_from("<II", b, o)
    if magic != MAGIC:
        return None
    sz = "<Q" if w == 8 else "<I"
    rd = lambda off: struct.unpack_from(sz, b, off)[0]  # noqa: E731
    mapsize = rd(o + 8 + w)
    dbs = o + 8 + 2 * w
    dbsz = 8 + 5 * w

    def db(i):
        p = dbs + i * dbsz
        pad, flags, depth = struct.unpack_from("<IHH", b, p)
        br, lf, ov, ent, root = (rd(p + 8 + k * w) for k in range(5))
        return {"pad": pad, "flags": flags, "depth": depth, "branch": br, "leaf": lf, "overflow": ov,
                "entries": ent, "root": root}
    end = dbs + 2 * dbsz
    return {"magic": magic, "version": ver, "mapsize": mapsize, "free": db(0), "main": db(1),
            "last_pg": rd(end), "txnid": rd(end + w)}


def parse_lmdb(b):
    """The current meta (larger txnid of pages 0/1) with its page index, or None."""
    for hdr, w in ((16, 8), (12, 4)):
        m0 = _meta(b, 0, hdr, w)
        if m0 is None:
            continue
        psize = m0["free"]["pad"] or 4096
        m1 = _meta(b, psize, hdr, w) if 512 <= psize <= 65536 else None
        cur, idx = (m1, 1) if m1 is not None and m1["txnid"] > m0["txnid"] else (m0, 0)
        cur["page"], cur["psize"] = idx, psize
        return cur
    return None


_KEY = {"version": "version", "mm_version": "version", "format_version": "version", "data_version": "version",
        "meta_version": "version", "map_size": "mapsize", "map_size_bytes": "mapsize", "mapsize": "mapsize",
        "mm_mapsize": "mapsize", "last_txn_id": "txnid", "last_txnid": "txnid", "txn_id": "txnid",
        "txnid": "txnid", "mm_txnid": "txnid", "last_transaction_id": "txnid", "last_page_number": "last_pg",
        "last_pgno": "last_pg", "last_page": "last_pg", "mm_last_pg": "last_pg", "page_size": "psize",
        "page_size_bytes": "psize", "psize": "psize", "current_meta_page": "page"}
_MAIN = {"entries": "entries", "entry_count": "entries", "main_db_entries": "entries", "md_entries": "entries",
         "depth": "depth", "main_db_depth": "depth", "branch_pages": "branch", "leaf_pages": "leaf",
         "overflow_pages": "overflow", "root_page": "root", "main_db_root": "root"}


def lmdb_value(data, ctx):
    if not data:
        return None
    try:
        from ..spell import Hex
        m = parse_lmdb(bytes(data))
        if m is None:
            return "none"   # no 0xBEEFC0DE meta page: not an LMDB data file
        f = (ctx or {}).get("field") or ""
        if f.endswith("magic_u32_hex"):
            return Hex(m["magic"], 8)
        if f == "main_db_flags_u16_hex":
            return Hex(m["main"]["flags"], 4)
        if f in _KEY:
            return m[_KEY[f]]
        if f in _MAIN:
            return m["main"][_MAIN[f]]
        return None
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None
