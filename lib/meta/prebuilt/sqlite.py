"""SQLite 3 database fields (prebuilt, SPECULATIVE -- page_size_bytes GM-verified D23, registered in lib.meta._BUILTIN).

Header (sqlite.org/fileformat2.html, 100 bytes, BIG-endian): "SQLite format 3\\0" @0, page size u16 @16 (1 = 65536),
write/read version u8 @18/@19 (1 legacy, 2 WAL), reserved bytes per page u8 @20, file change counter u32 @24, in-header
database size in pages u32 @28, first freelist trunk page u32 @32, freelist page count u32 @36, schema cookie u32 @40,
schema format number u32 @44, default page cache size u32 @48, largest root b-tree page u32 @52 (auto-vacuum), text
encoding u32 @56 (1 UTF-8, 2 UTF-16le, 3 UTF-16be), user version u32 @60, incremental-vacuum u32 @64, application id
u32 @68, version-valid-for u32 @92, SQLITE_VERSION_NUMBER u32 @96.
page_size = the int in bytes. text_encoding = PRAGMA encoding's spelling ("UTF-8" / "UTF-16le" / "UTF-16be");
*_u32 / *_code / *_id variants give the raw int. user_version = PRAGMA user_version (the u32 read SIGNED, as the pragma
does); application_id_u32_hex = Hex(u32, 8). page_count = PRAGMA page_count: the in-header size when it is valid
(non-zero and change counter == version-valid-for), else file size // page size (legacy writers).
Schema (stdlib, no sqlite3 needed): table b-tree walk from page 1 (interior 0x05 / leaf 0x0D, overflow chains) over
sqlite_master rows (type, name, tbl_name, rootpage, sql) in rowid = stored order. table_names = every type='table' name
(incl. sqlite_sequence / sqlite_stat1 -- `SELECT name FROM sqlite_master WHERE type='table'`); user_table_names (or a
question saying "user"/"excluding internal") drops sqlite_* names. index/view/trigger names likewise.
Browser history (Chrome `urls` / Firefox `moz_places`, rows in rowid order via the same walker, columns named from the
CREATE TABLE sql): history_urls list, url_count, most_visited_url (max visit_count, first on ties), last_visited_url
(max last_visit_time / last_visit_date); last_visit_time_utc: Chrome = WebKit us since 1601, Firefox = PRTime us
since 1970 -> 'YYYY-MM-DDTHH:MM:SSZ'. row_count = rows of the table named in the question.
Not "SQLite format 3\\0" (decoy / renamed impostor) -> "none"; a valid header with an unreadable schema -> None."""
import datetime
import re
import struct

from ..spell import Hex

FIELDS = {
    ("sqlite", "page_size"): "sqlite_value",
    ("sqlite", "header_page_size"): "sqlite_value",
    ("sqlite", "database_page_size"): "sqlite_value",
    ("sqlite", "text_encoding"): "sqlite_value",
    ("sqlite", "header_text_encoding"): "sqlite_value",
    ("sqlite", "database_text_encoding"): "sqlite_value",
    ("sqlite", "encoding"): "sqlite_value",
    ("sqlite", "text_encoding_u32"): "sqlite_value",
    ("sqlite", "text_encoding_code"): "sqlite_value",
    ("sqlite", "text_encoding_id"): "sqlite_value",
    ("sqlite", "user_version"): "sqlite_value",
    ("sqlite", "header_user_version"): "sqlite_value",
    ("sqlite", "user_version_u32_hex"): "sqlite_value",
    ("sqlite", "application_id_u32_hex"): "sqlite_value",
    ("sqlite", "header_application_id_u32_hex"): "sqlite_value",
    ("sqlite", "application_id_hex"): "sqlite_value",
    ("sqlite", "application_id"): "sqlite_value",
    ("sqlite", "page_count"): "sqlite_value",
    ("sqlite", "database_size_pages"): "sqlite_value",
    ("sqlite", "database_size_in_pages"): "sqlite_value",
    ("sqlite", "header_database_size"): "sqlite_value",
    ("sqlite", "header_page_count"): "sqlite_value",
    ("sqlite", "in_header_database_size"): "sqlite_value",
    ("sqlite", "file_change_counter"): "sqlite_value",
    ("sqlite", "change_counter"): "sqlite_value",
    ("sqlite", "schema_cookie"): "sqlite_value",
    ("sqlite", "schema_format_number"): "sqlite_value",
    ("sqlite", "schema_format"): "sqlite_value",
    ("sqlite", "freelist_page_count"): "sqlite_value",
    ("sqlite", "freelist_count"): "sqlite_value",
    ("sqlite", "first_freelist_trunk_page"): "sqlite_value",
    ("sqlite", "reserved_bytes"): "sqlite_value",
    ("sqlite", "reserved_space"): "sqlite_value",
    ("sqlite", "write_version"): "sqlite_value",
    ("sqlite", "read_version"): "sqlite_value",
    ("sqlite", "file_format_write_version"): "sqlite_value",
    ("sqlite", "file_format_read_version"): "sqlite_value",
    ("sqlite", "journal_mode"): "sqlite_value",
    ("sqlite", "wal_mode"): "sqlite_value",
    ("sqlite", "is_wal"): "sqlite_value",
    ("sqlite", "default_cache_size"): "sqlite_value",
    ("sqlite", "auto_vacuum"): "sqlite_value",
    ("sqlite", "largest_root_btree_page"): "sqlite_value",
    ("sqlite", "incremental_vacuum"): "sqlite_value",
    ("sqlite", "version_valid_for"): "sqlite_value",
    ("sqlite", "sqlite_version_number"): "sqlite_value",
    ("sqlite", "version_number"): "sqlite_value",
    ("sqlite", "sqlite_version"): "sqlite_value",
    ("sqlite", "library_version"): "sqlite_value",
    ("sqlite", "table_names"): "schema_value",
    ("sqlite", "sqlite_master_table_names"): "schema_value",
    ("sqlite", "schema_table_names"): "schema_value",
    ("sqlite", "tables"): "schema_value",
    ("sqlite", "user_table_names"): "schema_value",
    ("sqlite", "table_count"): "schema_value",
    ("sqlite", "user_table_count"): "schema_value",
    ("sqlite", "index_names"): "schema_value",
    ("sqlite", "view_names"): "schema_value",
    ("sqlite", "trigger_names"): "schema_value",
    ("sqlite", "index_count"): "schema_value",
    ("sqlite", "schema_object_count"): "schema_value",
    ("sqlite", "sqlite_master_row_count"): "schema_value",
    ("sqlite", "row_count"): "schema_value",
    ("sqlite", "table_row_count"): "schema_value",
    ("sqlite", "history_urls"): "history_value",
    ("sqlite", "urls"): "history_value",
    ("sqlite", "url_list"): "history_value",
    ("sqlite", "visited_urls"): "history_value",
    ("sqlite", "url_count"): "history_value",
    ("sqlite", "history_url_count"): "history_value",
    ("sqlite", "history_entry_count"): "history_value",
    ("sqlite", "most_visited_url"): "history_value",
    ("sqlite", "last_visited_url"): "history_value",
    ("sqlite", "most_recent_url"): "history_value",
    ("sqlite", "last_visit_time"): "history_value",
    ("sqlite", "last_visit_time_utc"): "history_value",
    ("sqlite", "browser"): "history_value",
    ("sqlite", "browser_type"): "history_value",
}

_MAGIC = b"SQLite format 3\x00"
_ENC = {1: "UTF-8", 2: "UTF-16le", 3: "UTF-16be"}
_PYENC = {1: "utf-8", 2: "utf-16-le", 3: "utf-16-be"}


def _header(b):
    if not b or len(b) < 100 or bytes(b[:16]) != _MAGIC:
        return None
    ps, = struct.unpack_from(">H", b, 16)
    ps = 65536 if ps == 1 else ps
    if ps < 512 or ps & (ps - 1):
        return None
    u = struct.unpack_from(">18I", b, 24)
    h = {"page_size": ps, "write_version": b[18], "read_version": b[19], "reserved": b[20],
         "change_counter": u[0], "db_size": u[1], "freelist_trunk": u[2], "freelist_count": u[3],
         "schema_cookie": u[4], "schema_format": u[5], "cache_size": struct.unpack_from(">i", b, 48)[0],
         "largest_root": u[7], "encoding": u[8], "user_version": u[9], "incr_vacuum": u[10], "app_id": u[11],
         "valid_for": struct.unpack_from(">I", b, 92)[0], "sqlite_version": struct.unpack_from(">I", b, 96)[0]}
    if h["db_size"] and h["change_counter"] == h["valid_for"]:
        h["page_count"] = h["db_size"]
    else:
        h["page_count"] = len(b) // ps
    return h


def _varint(b, off):
    v = 0
    for i in range(8):
        c = b[off + i]
        v = (v << 7) | (c & 0x7F)
        if not c & 0x80:
            return v, off + i + 1
    return (v << 8) | b[off + 8], off + 9


def _record(p, enc):
    hlen, off = _varint(p, 0)
    types = []
    while off < hlen:
        t, off = _varint(p, off)
        types.append(t)
    out, d = [], hlen
    for t in types:
        if t == 0:
            out.append(None)
        elif 1 <= t <= 6:
            n = (1, 2, 3, 4, 6, 8)[t - 1]
            out.append(int.from_bytes(p[d:d + n], "big", signed=True))
            d += n
        elif t == 7:
            out.append(struct.unpack_from(">d", p, d)[0])
            d += 8
        elif t in (8, 9):
            out.append(t - 8)
        elif t >= 12:
            n = (t - 12) // 2
            raw = bytes(p[d:d + n])
            out.append(raw.decode(enc, "replace") if t & 1 else raw)
            d += n
        else:
            out.append(None)
    return out


def _table_rows(b, h, root):
    """[(rowid, [values])] of the table b-tree at page `root`, in rowid order (cell order of an in-order walk)."""
    ps = h["page_size"]
    usable = ps - h["reserved"]
    enc = _PYENC.get(h["encoding"], "utf-8")
    npages = len(b) // ps
    rows, stack, seen = [], [root], set()
    order = []
    while stack:
        pg = stack.pop()
        if pg in seen:
            continue
        if not 1 <= pg <= npages:
            raise ValueError("b-tree page %d outside the %d-page file (truncated)" % (pg, npages))
        seen.add(pg)
        base = (pg - 1) * ps
        ho = base + (100 if pg == 1 else 0)
        kind = b[ho]
        n, = struct.unpack_from(">H", b, ho + 3)
        if kind == 0x05:
            ptrs = [struct.unpack_from(">H", b, ho + 12 + 2 * i)[0] for i in range(n)]
            kids = [struct.unpack_from(">I", b, base + p)[0] for p in ptrs]
            kids.append(struct.unpack_from(">I", b, ho + 8)[0])
            stack.extend(reversed(kids))
        elif kind == 0x0D:
            for i in range(n):
                co = base + struct.unpack_from(">H", b, ho + 8 + 2 * i)[0]
                plen, o = _varint(b, co)
                rowid, o = _varint(b, o)
                x = usable - 35
                if plen <= x:
                    payload = bytes(b[o:o + plen])
                else:
                    m = ((usable - 12) * 32 // 255) - 23
                    k = m + ((plen - m) % (usable - 4))
                    local = k if k <= x else m
                    payload = bytearray(b[o:o + local])
                    nxt, = struct.unpack_from(">I", b, o + local)
                    hops = 0
                    while nxt and len(payload) < plen and hops < npages:
                        ob = (nxt - 1) * ps
                        payload += b[ob + 4:ob + usable]
                        nxt, = struct.unpack_from(">I", b, ob)
                        hops += 1
                    payload = bytes(payload[:plen])
                order.append((rowid, _record(payload, enc)))
        else:
            raise ValueError("not a table b-tree page %d (0x%02x)" % (pg, kind))
    rows.extend(order)
    return rows


def _schema(b, h):
    """sqlite_master rows [(type, name, tbl_name, rootpage, sql)] in stored order, or None."""
    if len(b) < h["page_size"]:
        return None
    try:
        rows = _table_rows(b, h, 1)
        return [tuple((r + [None] * 5)[:5]) for _, r in rows]
    except Exception:  # noqa: BLE001
        pass
    try:   # fallback: the real library (WAL header bytes patched to legacy so an in-memory open works)
        import sqlite3
        c = sqlite3.connect(":memory:")
        bb = bytearray(b)
        bb[18:20] = b"\x01\x01"
        c.deserialize(bytes(bb))
        rows = [tuple(r) for r in c.execute("SELECT type, name, tbl_name, rootpage, sql FROM sqlite_master")]
        return rows or None       # our walker failed: an empty answer from the library is not evidence
    except Exception:  # noqa: BLE001
        return None


def sqlite_value(data, ctx):
    try:
        if not data or bytes(data[:16]) != _MAGIC:
            return "none"
        h = _header(data)
        if h is None:
            return None
        f = ctx.get("field") or ""
        if f.startswith("text_encoding") or f.startswith("header_text_encoding") or f in ("encoding",
                                                                                           "database_text_encoding"):
            if f.endswith(("_u32", "_code", "_id")):
                return h["encoding"]
            return _ENC.get(h["encoding"], h["encoding"])
        if "application_id" in f:
            return Hex(h["app_id"], 8) if f.endswith("_hex") else struct.unpack(">i", struct.pack(">I", h["app_id"]))[0]
        if "user_version" in f:
            if f.endswith("_hex"):
                return Hex(h["user_version"], 8)
            return struct.unpack(">i", struct.pack(">I", h["user_version"]))[0]
        if "page_size" in f:
            return h["page_size"]
        if f in ("page_count", "header_page_count"):
            return h["page_count"]
        if f.startswith(("database_size", "header_database_size", "in_header_database_size")):
            return h["db_size"]
        if "change_counter" in f:
            return h["change_counter"]
        if f == "schema_cookie":
            return h["schema_cookie"]
        if f.startswith("schema_format"):
            return h["schema_format"]
        if f.startswith("freelist"):
            return h["freelist_count"]
        if f == "first_freelist_trunk_page":
            return h["freelist_trunk"]
        if f.startswith("reserved"):
            return h["reserved"]
        if "write_version" in f:
            return h["write_version"]
        if "read_version" in f:
            return h["read_version"]
        if f == "journal_mode":
            return "wal" if h["write_version"] == 2 else "delete"
        if f in ("wal_mode", "is_wal"):
            return h["write_version"] == 2 and h["read_version"] == 2
        if f == "default_cache_size":
            return h["cache_size"]
        if f in ("auto_vacuum", "largest_root_btree_page"):
            return h["largest_root"]
        if f == "incremental_vacuum":
            return h["incr_vacuum"]
        if f == "version_valid_for":
            return h["valid_for"]
        if f in ("sqlite_version_number", "version_number"):
            return h["sqlite_version"]
        if f in ("sqlite_version", "library_version"):
            v = h["sqlite_version"]
            return "%d.%d.%d" % (v // 1000000, v // 1000 % 1000, v % 1000) if v else "none"
        return None
    except Exception:  # noqa: BLE001
        return None


def _qtext(ctx):
    """The question text (ctx["question"] is the GM question dict; a bare string is accepted too)."""
    q = ctx.get("question") or ""
    return str(q.get("question") or "") if isinstance(q, dict) else str(q)


def _quoted_names(q):
    return re.findall(r"[`'\"\[]([A-Za-z_][\w$ ]*)[`'\"\]]", q or "")


def schema_value(data, ctx):
    try:
        if not data or bytes(data[:16]) != _MAGIC:
            return "none"
        h = _header(data)
        sch = _schema(data, h) if h else None
        if sch is None:
            return None
        f = ctx.get("field") or ""
        q = _qtext(ctx).lower()
        user = f.startswith("user_") or "user table" in q or "exclud" in q
        if f in ("schema_object_count", "sqlite_master_row_count"):
            return len(sch)
        if f in ("row_count", "table_row_count"):
            tables = {r[1].lower(): r for r in sch if r[0] == "table" and isinstance(r[1], str)}
            for name in _quoted_names(_qtext(ctx)):
                r = tables.get(name.lower())
                if r and isinstance(r[3], int) and r[3] > 0:
                    return len(_table_rows(data, h, r[3]))
            return None
        kind = "index" if f.startswith("index") else "view" if f.startswith("view") else \
            "trigger" if f.startswith("trigger") else "table"
        names = [r[1] for r in sch if r[0] == kind and isinstance(r[1], str)]
        if user or kind == "index" and "auto" in q and "exclud" in q:
            names = [n for n in names if not n.startswith("sqlite_")]
        return len(names) if f.endswith("_count") else names
    except Exception:  # noqa: BLE001
        return None


def _columns(sql):
    """Column names of a CREATE TABLE statement (first identifier of each top-level comma part)."""
    m = re.search(r"\((.*)\)", sql or "", re.S)
    if not m:
        return []
    body, depth, part, parts = m.group(1), 0, "", []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(part)
            part = ""
        else:
            part += ch
    parts.append(part)
    cols = []
    for p in parts:
        w = p.strip().split(None, 1)
        if not w or w[0].upper() in ("PRIMARY", "UNIQUE", "CHECK", "FOREIGN", "CONSTRAINT"):
            continue
        cols.append(w[0].strip("`\"[]'").lower())
    return cols


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def history_value(data, ctx):
    try:
        if not data or bytes(data[:16]) != _MAGIC:
            return "none"
        h = _header(data)
        sch = _schema(data, h) if h else None
        if sch is None:
            return None
        tables = {r[1]: r for r in sch if r[0] == "table" and isinstance(r[1], str)}
        if "urls" in tables:
            browser, r, tcol = "chrome", tables["urls"], "last_visit_time"
        elif "moz_places" in tables:
            browser, r, tcol = "firefox", tables["moz_places"], "last_visit_date"
        else:
            return "none"
        f = ctx.get("field") or ""
        if f.startswith("browser"):
            return browser
        cols = _columns(r[4])
        rows = _table_rows(data, h, r[3])
        recs = []
        for rowid, vals in rows:
            d = dict(zip(cols, vals))
            if "id" in d and d["id"] is None:
                d["id"] = rowid          # INTEGER PRIMARY KEY alias is stored as NULL
            recs.append(d)
        urls = [d.get("url") for d in recs if isinstance(d.get("url"), str)]
        if f in ("history_urls", "urls", "url_list", "visited_urls"):
            return urls
        if f.endswith("_count"):
            return len(urls)
        if f == "most_visited_url":
            best = max(recs, key=lambda d: d.get("visit_count") or 0, default=None)
            return best.get("url") if best and best.get("url") else "none"
        timed = [d for d in recs if isinstance(d.get(tcol), int) and d.get(tcol) > 0]
        if not timed:
            return "none"
        last = max(timed, key=lambda d: d[tcol])
        if f in ("last_visited_url", "most_recent_url"):
            return last.get("url") or "none"
        us = last[tcol]
        epoch = datetime.datetime(1601, 1, 1) if browser == "chrome" else datetime.datetime(1970, 1, 1)
        return _iso(epoch + datetime.timedelta(microseconds=us))
    except Exception:  # noqa: BLE001
        return None
