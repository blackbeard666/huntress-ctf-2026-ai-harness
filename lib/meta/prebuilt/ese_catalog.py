"""ESE / JET Blue catalog walk (SRUDB.dat, WebCacheV01.dat, Windows.edb, *.edb) -- prebuilt, SPECULATIVE (never
GM-asked).  Format tokens: ese (aliases edb, esedb, jet, srum, webcache).  ese.py covers the file header only.

Layout (open-source ESE daedef.hxx / cpage.hxx as carried by dissect.esedb 3.18 and the libesedb format doc):
  cbPageSize u32 @236 of the header; logical page n lives at file offset (n + 1) * page_size (pages 0/1 of the
  file are the header and its shadow).  PGHDR (40 B): checksum u64, dbtime u64, pgnoPrev u32 @16, pgnoNext u32 @20,
  objidFDP u32 @24, cbFree u16, cbUncommitted u16, ibMicFree u16 @32, itagState u16 @34 (low 12 bits = tag count),
  fFlags u32 @36 (root 0x1, leaf 0x2, parent-of-leaf 0x4, empty 0x8, space tree 0x20, index 0x40, long value 0x80,
  new record format 0x2000).  Pages > 8 KiB add PGHDR2 (40 B) -> data starts at 80.  Tags at the page end, tag i at
  end - 4*(i+1) = {cb u16, ib u16} relative to the data start: <= 8 KiB pages mask 0x1FFF with the 3 node flags in
  ib's top bits; large pages mask 0x7FFF with the flags in the top 3 bits of the node's first u16.  Tag 0 = page
  external header; nodes from tag 1: [prefix-cb u16 if fCompressed 0x4] [suffix-cb u16][key suffix][data].
  Branch node data = child pgno u32.  Deleted nodes (0x2) are skipped.
Record (leaf data): fidFixedLastInRec u8, fidVarLastInRec u8, ibEndOfFixedData u16; fixed columns from offset 4
  in column-id order (width = catalog SpaceUsage, else the coltyp width), then the fixed-null bitmap (bit = NULL)
  ending at ibEndOfFixedData; then (fidVarLast - 127) u16 end offsets (0x8000 = NULL) and the variable data; then
  the tagged area: TAGFLD u32 array {columnid u16, ib u16}, the first ib = array size.  <= 8 KiB pages: ib & 0x1FFF,
  0x4000 = one TAGFLD_HEADER byte precedes the value, 0x2000 = NULL; large pages: ib & 0x7FFF, header byte always.
  Header bits: 0x2 compressed (7-bit ASCII / 7-bit UTF-16 decoded here; XPRESS not), 0x4 separated (value lives in
  the long-value tree: not followed -> that value is skipped), 0x8/0x10 multi-value (first instance), 0x20 NULL.
Catalog = MSysObjects, FDP rooted at logical page 4: fixed ObjidTable i32 (1), Type u16 (2: 1 table, 2 column,
  3 index, 4 long value), Id i32 (3), ColtypOrPgnoFDP i32 (4), SpaceUsage (5), Flags (6), PagesOrLocale (7 =
  codepage for text columns: 1200 UTF-16LE, else cp1252), variable Name (128).  Records follow the table record, in
  catalog key order (= column id order for columns).
Fields: table_names = sorted JSON of the user tables (MSys* only for all_/catalog_/system_ names), table_count;
  column_names_<table> (column-id order), column_count_<table>, table_record_count_<table> = leaf records of the
  table's FDP (<table> matched case/punctuation-insensitively; SRUM friendly names map to their GUID tables);
  srum_app_names = sorted unique UTF-16 IdBlob strings of SruDbIdMapTable rows with IdType != 3 (3 = user SID ->
  srum_user_sids, S-1-... text); srum_tables_present = sorted friendly names of the known SRUM GUID tables present;
  webcache_container_names / container_directories = Containers.Name / .Directory in stored (ContainerId) order.
Not ESE (wrong magic) -> "none"; ESE but the catalog / table / column is absent -> "none"; unreadable -> None."""
import re
import struct

FIELDS = {
    ("ese", "table_names"): "catalog_value",
    ("ese", "user_table_names"): "catalog_value",
    ("ese", "table_names_sorted"): "catalog_value",
    ("ese", "all_table_names"): "catalog_value",
    ("ese", "catalog_table_names"): "catalog_value",
    ("ese", "system_table_names"): "catalog_value",
    ("ese", "msys_table_names"): "catalog_value",
    ("ese", "table_count"): "catalog_value",
    ("ese", "user_table_count"): "catalog_value",
    ("ese", "all_table_count"): "catalog_value",
    ("ese", "catalog_table_count"): "catalog_value",
    ("ese", "column_names_*"): "catalog_value",
    ("ese", "table_column_names_*"): "catalog_value",
    ("ese", "column_count_*"): "catalog_value",
    ("ese", "table_record_count_*"): "catalog_value",
    ("ese", "record_count_*"): "catalog_value",
    ("ese", "row_count_*"): "catalog_value",
    ("ese", "table_row_count_*"): "catalog_value",
    ("ese", "srum_app_names"): "catalog_value",
    ("ese", "srum_application_names"): "catalog_value",
    ("ese", "app_names"): "catalog_value",
    ("ese", "application_names"): "catalog_value",
    ("ese", "srum_user_sids"): "catalog_value",
    ("ese", "user_sids"): "catalog_value",
    ("ese", "srum_id_map_count"): "catalog_value",
    ("ese", "id_map_entry_count"): "catalog_value",
    ("ese", "srum_tables_present"): "catalog_value",
    ("ese", "srum_table_names"): "catalog_value",
    ("ese", "srum_table_guids"): "catalog_value",
    ("ese", "webcache_container_names"): "catalog_value",
    ("ese", "container_names"): "catalog_value",
    ("ese", "container_count"): "catalog_value",
    ("ese", "webcache_container_count"): "catalog_value",
    ("ese", "container_directories"): "catalog_value",
    ("ese", "webcache_container_directories"): "catalog_value",
    ("edb", "table_names"): "catalog_value",
    ("edb", "user_table_names"): "catalog_value",
    ("edb", "table_names_sorted"): "catalog_value",
    ("edb", "all_table_names"): "catalog_value",
    ("edb", "catalog_table_names"): "catalog_value",
    ("edb", "system_table_names"): "catalog_value",
    ("edb", "msys_table_names"): "catalog_value",
    ("edb", "table_count"): "catalog_value",
    ("edb", "user_table_count"): "catalog_value",
    ("edb", "all_table_count"): "catalog_value",
    ("edb", "catalog_table_count"): "catalog_value",
    ("edb", "column_names_*"): "catalog_value",
    ("edb", "table_column_names_*"): "catalog_value",
    ("edb", "column_count_*"): "catalog_value",
    ("edb", "table_record_count_*"): "catalog_value",
    ("edb", "record_count_*"): "catalog_value",
    ("edb", "row_count_*"): "catalog_value",
    ("edb", "table_row_count_*"): "catalog_value",
    ("edb", "srum_app_names"): "catalog_value",
    ("edb", "srum_application_names"): "catalog_value",
    ("edb", "app_names"): "catalog_value",
    ("edb", "application_names"): "catalog_value",
    ("edb", "srum_user_sids"): "catalog_value",
    ("edb", "user_sids"): "catalog_value",
    ("edb", "srum_id_map_count"): "catalog_value",
    ("edb", "id_map_entry_count"): "catalog_value",
    ("edb", "srum_tables_present"): "catalog_value",
    ("edb", "srum_table_names"): "catalog_value",
    ("edb", "srum_table_guids"): "catalog_value",
    ("edb", "webcache_container_names"): "catalog_value",
    ("edb", "container_names"): "catalog_value",
    ("edb", "container_count"): "catalog_value",
    ("edb", "webcache_container_count"): "catalog_value",
    ("edb", "container_directories"): "catalog_value",
    ("edb", "webcache_container_directories"): "catalog_value",
    ("esedb", "table_names"): "catalog_value",
    ("esedb", "user_table_names"): "catalog_value",
    ("esedb", "table_names_sorted"): "catalog_value",
    ("esedb", "all_table_names"): "catalog_value",
    ("esedb", "catalog_table_names"): "catalog_value",
    ("esedb", "system_table_names"): "catalog_value",
    ("esedb", "msys_table_names"): "catalog_value",
    ("esedb", "table_count"): "catalog_value",
    ("esedb", "user_table_count"): "catalog_value",
    ("esedb", "all_table_count"): "catalog_value",
    ("esedb", "catalog_table_count"): "catalog_value",
    ("esedb", "column_names_*"): "catalog_value",
    ("esedb", "table_column_names_*"): "catalog_value",
    ("esedb", "column_count_*"): "catalog_value",
    ("esedb", "table_record_count_*"): "catalog_value",
    ("esedb", "record_count_*"): "catalog_value",
    ("esedb", "row_count_*"): "catalog_value",
    ("esedb", "table_row_count_*"): "catalog_value",
    ("esedb", "srum_app_names"): "catalog_value",
    ("esedb", "srum_application_names"): "catalog_value",
    ("esedb", "app_names"): "catalog_value",
    ("esedb", "application_names"): "catalog_value",
    ("esedb", "srum_user_sids"): "catalog_value",
    ("esedb", "user_sids"): "catalog_value",
    ("esedb", "srum_id_map_count"): "catalog_value",
    ("esedb", "id_map_entry_count"): "catalog_value",
    ("esedb", "srum_tables_present"): "catalog_value",
    ("esedb", "srum_table_names"): "catalog_value",
    ("esedb", "srum_table_guids"): "catalog_value",
    ("esedb", "webcache_container_names"): "catalog_value",
    ("esedb", "container_names"): "catalog_value",
    ("esedb", "container_count"): "catalog_value",
    ("esedb", "webcache_container_count"): "catalog_value",
    ("esedb", "container_directories"): "catalog_value",
    ("esedb", "webcache_container_directories"): "catalog_value",
    ("jet", "table_names"): "catalog_value",
    ("jet", "user_table_names"): "catalog_value",
    ("jet", "table_names_sorted"): "catalog_value",
    ("jet", "all_table_names"): "catalog_value",
    ("jet", "catalog_table_names"): "catalog_value",
    ("jet", "system_table_names"): "catalog_value",
    ("jet", "msys_table_names"): "catalog_value",
    ("jet", "table_count"): "catalog_value",
    ("jet", "user_table_count"): "catalog_value",
    ("jet", "all_table_count"): "catalog_value",
    ("jet", "catalog_table_count"): "catalog_value",
    ("jet", "column_names_*"): "catalog_value",
    ("jet", "table_column_names_*"): "catalog_value",
    ("jet", "column_count_*"): "catalog_value",
    ("jet", "table_record_count_*"): "catalog_value",
    ("jet", "record_count_*"): "catalog_value",
    ("jet", "row_count_*"): "catalog_value",
    ("jet", "table_row_count_*"): "catalog_value",
    ("jet", "srum_app_names"): "catalog_value",
    ("jet", "srum_application_names"): "catalog_value",
    ("jet", "app_names"): "catalog_value",
    ("jet", "application_names"): "catalog_value",
    ("jet", "srum_user_sids"): "catalog_value",
    ("jet", "user_sids"): "catalog_value",
    ("jet", "srum_id_map_count"): "catalog_value",
    ("jet", "id_map_entry_count"): "catalog_value",
    ("jet", "srum_tables_present"): "catalog_value",
    ("jet", "srum_table_names"): "catalog_value",
    ("jet", "srum_table_guids"): "catalog_value",
    ("jet", "webcache_container_names"): "catalog_value",
    ("jet", "container_names"): "catalog_value",
    ("jet", "container_count"): "catalog_value",
    ("jet", "webcache_container_count"): "catalog_value",
    ("jet", "container_directories"): "catalog_value",
    ("jet", "webcache_container_directories"): "catalog_value",
    ("srum", "table_names"): "catalog_value",
    ("srum", "user_table_names"): "catalog_value",
    ("srum", "table_names_sorted"): "catalog_value",
    ("srum", "all_table_names"): "catalog_value",
    ("srum", "catalog_table_names"): "catalog_value",
    ("srum", "system_table_names"): "catalog_value",
    ("srum", "msys_table_names"): "catalog_value",
    ("srum", "table_count"): "catalog_value",
    ("srum", "user_table_count"): "catalog_value",
    ("srum", "all_table_count"): "catalog_value",
    ("srum", "catalog_table_count"): "catalog_value",
    ("srum", "column_names_*"): "catalog_value",
    ("srum", "table_column_names_*"): "catalog_value",
    ("srum", "column_count_*"): "catalog_value",
    ("srum", "table_record_count_*"): "catalog_value",
    ("srum", "record_count_*"): "catalog_value",
    ("srum", "row_count_*"): "catalog_value",
    ("srum", "table_row_count_*"): "catalog_value",
    ("srum", "srum_app_names"): "catalog_value",
    ("srum", "srum_application_names"): "catalog_value",
    ("srum", "app_names"): "catalog_value",
    ("srum", "application_names"): "catalog_value",
    ("srum", "srum_user_sids"): "catalog_value",
    ("srum", "user_sids"): "catalog_value",
    ("srum", "srum_id_map_count"): "catalog_value",
    ("srum", "id_map_entry_count"): "catalog_value",
    ("srum", "srum_tables_present"): "catalog_value",
    ("srum", "srum_table_names"): "catalog_value",
    ("srum", "srum_table_guids"): "catalog_value",
    ("srum", "webcache_container_names"): "catalog_value",
    ("srum", "container_names"): "catalog_value",
    ("srum", "container_count"): "catalog_value",
    ("srum", "webcache_container_count"): "catalog_value",
    ("srum", "container_directories"): "catalog_value",
    ("srum", "webcache_container_directories"): "catalog_value",
    ("webcache", "table_names"): "catalog_value",
    ("webcache", "user_table_names"): "catalog_value",
    ("webcache", "table_names_sorted"): "catalog_value",
    ("webcache", "all_table_names"): "catalog_value",
    ("webcache", "catalog_table_names"): "catalog_value",
    ("webcache", "system_table_names"): "catalog_value",
    ("webcache", "msys_table_names"): "catalog_value",
    ("webcache", "table_count"): "catalog_value",
    ("webcache", "user_table_count"): "catalog_value",
    ("webcache", "all_table_count"): "catalog_value",
    ("webcache", "catalog_table_count"): "catalog_value",
    ("webcache", "column_names_*"): "catalog_value",
    ("webcache", "table_column_names_*"): "catalog_value",
    ("webcache", "column_count_*"): "catalog_value",
    ("webcache", "table_record_count_*"): "catalog_value",
    ("webcache", "record_count_*"): "catalog_value",
    ("webcache", "row_count_*"): "catalog_value",
    ("webcache", "table_row_count_*"): "catalog_value",
    ("webcache", "srum_app_names"): "catalog_value",
    ("webcache", "srum_application_names"): "catalog_value",
    ("webcache", "app_names"): "catalog_value",
    ("webcache", "application_names"): "catalog_value",
    ("webcache", "srum_user_sids"): "catalog_value",
    ("webcache", "user_sids"): "catalog_value",
    ("webcache", "srum_id_map_count"): "catalog_value",
    ("webcache", "id_map_entry_count"): "catalog_value",
    ("webcache", "srum_tables_present"): "catalog_value",
    ("webcache", "srum_table_names"): "catalog_value",
    ("webcache", "srum_table_guids"): "catalog_value",
    ("webcache", "webcache_container_names"): "catalog_value",
    ("webcache", "container_names"): "catalog_value",
    ("webcache", "container_count"): "catalog_value",
    ("webcache", "webcache_container_count"): "catalog_value",
    ("webcache", "container_directories"): "catalog_value",
    ("webcache", "webcache_container_directories"): "catalog_value",
}

_MAGIC = b"\xef\xcd\xab\x89"
_MAX_PAGES = 20000
# fixed widths of the JET column types (bit, ubyte, short, long, currency, single, double, datetime, ..., ulong,
# longlong, guid, ushort)
_CT_SIZE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 4, 7: 8, 8: 8, 14: 4, 15: 8, 16: 16, 17: 2}
_CAT_FIXED = [(1, 4), (2, 2), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 1), (9, 2), (10, 4), (11, 2), (12, 4)]
_SRUM = {
    "{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}": "App Resource Usage",
    "{973F5D5C-1D90-4944-BE8E-24B94231A174}": "Network Usage",
    "{DD6636C4-8929-4683-974E-22C046A43763}": "Network Connectivity",
    "{5C8CF1C7-7257-4F13-B223-970EF5939312}": "App Timeline",
    "{FEE4E14F-02A9-4550-B5CE-5FA2DA202E37}": "Energy Usage",
}


def _norm(s):
    return re.sub(r"[^0-9a-z]", "", str(s or "").lower())


def _sevenbit(buf, wide):
    out, acc, nbits = bytearray(), 0, 0
    for b in buf:
        acc |= b << nbits
        nbits += 8
        while nbits >= 7:
            out.append(acc & 0x7F)
            acc >>= 7
            nbits -= 7
    return bytes(b2 for c in out for b2 in ((c, 0) if wide else (c,)))


class _Db:
    def __init__(self, data):
        self.data = data
        self.ps = struct.unpack_from("<I", data, 236)[0] or 4096
        if self.ps not in (2048, 4096, 8192, 16384, 32768):
            raise ValueError("page size")
        self.small = self.ps <= 8192
        self.cache = {}

    def page(self, n):
        if n in self.cache:
            return self.cache[n]
        off = (n + 1) * self.ps
        buf = self.data[off:off + self.ps]
        if n < 1 or len(buf) < self.ps:
            return None
        prev, nxt, _objid = struct.unpack_from("<III", buf, 16)
        ibmic, itag, flags = struct.unpack_from("<HHI", buf, 32)
        start = 40 if self.small else 80
        ntag = itag & 0x0FFF
        mask = 0x1FFF if self.small else 0x7FFF
        nodes = []
        for i in range(1, ntag):
            to = self.ps - 4 * (i + 1)
            if to < start:
                break
            cb, ib = struct.unpack_from("<HH", buf, to)
            d = buf[start + (ib & mask):start + (ib & mask) + (cb & mask)]
            if not d:
                continue
            tf = (ib >> 13) if self.small else (d[1] >> 5 if len(d) > 1 else 0)
            if tf & 0x2:                      # fNDDeleted
                continue
            o = 2 if tf & 0x4 else 0          # fNDCompressed: key-prefix length first
            if len(d) < o + 2:
                continue
            ks = struct.unpack_from("<H", d, o)[0] & 0x1FFF
            nodes.append(d[o + 2 + ks:])
        pg = (flags, nxt, nodes)
        self.cache[n] = pg
        return pg

    def leaf_records(self, root):
        """Data of every leaf node under the FDP root `root` (branch walk + the last leaf's next chain)."""
        out, seen, stack, last = [], set(), [root], None
        while stack:
            n = stack.pop()
            if n in seen or len(seen) > _MAX_PAGES:
                continue
            seen.add(n)
            pg = self.page(n)
            if pg is None:
                continue
            flags, nxt, nodes = pg
            if flags & 0x2:
                out.extend(nodes)
                last = (n, nxt)
            else:
                stack.extend(struct.unpack_from("<I", d, 0)[0] for d in reversed(nodes) if len(d) >= 4)
        while last and last[1] and last[1] not in seen and len(seen) <= _MAX_PAGES:
            seen.add(last[1])
            pg = self.page(last[1])
            if pg is None or not pg[0] & 0x2:
                break
            out.extend(pg[2])
            last = (last[1], pg[1])
        return out

    def columns(self, rec, cols):
        """{column id: raw bytes} of one record; cols = [(id, coltyp, size)] (fixed widths from the catalog)."""
        if len(rec) < 4:
            return {}
        flast, vlast, ibend = struct.unpack_from("<BBH", rec, 0)
        out = {}
        off = 4
        nbm = (flast + 7) // 8
        bm = rec[ibend - nbm:ibend]
        for cid, ct, size in sorted(c for c in cols if c[0] <= 127):
            w = size or _CT_SIZE.get(ct, 0)
            if cid <= flast and len(bm) == nbm and not bm[(cid - 1) // 8] & (1 << ((cid - 1) % 8)):
                out[cid] = rec[off:off + w]
            off += w
        nvar = max(vlast - 127, 0)
        vds = ibend + 2 * nvar
        ends = struct.unpack_from("<%dH" % nvar, rec, ibend) if nvar and len(rec) >= vds else ()
        prev = 0
        for i, e in enumerate(ends):
            if not e & 0x8000:
                out[128 + i] = rec[vds + prev:vds + (e & 0x7FFF)]
            prev = e & 0x7FFF
        ts = vds + (ends[-1] & 0x7FFF if ends else 0)
        if len(rec) >= ts + 4:
            first = struct.unpack_from("<HH", rec, ts)[1]
            mask = 0x1FFF if self.small else 0x7FFF
            cnt = (first & mask) // 4
            tf = [struct.unpack_from("<HH", rec, ts + 4 * i) for i in range(cnt) if ts + 4 * i + 4 <= len(rec)]
            for i, (cid, ib) in enumerate(tf):
                s = ts + (ib & mask)
                e = ts + (tf[i + 1][1] & mask) if i + 1 < len(tf) else len(rec)
                if self.small and ib & 0x2000:
                    continue
                hdr = 0
                if not self.small or ib & 0x4000:
                    hdr = rec[s] if s < len(rec) else 0x20
                    s += 1
                if hdr & 0x24:                # NULL / separated (long-value tree: not followed)
                    continue
                v = rec[s:e]
                if hdr & 0x10 and v:                 # two values: u8 length of the first
                    v = v[1:1 + v[0]]
                elif hdr & 0x8 and len(v) >= 2:      # multi-value: u16 offsets array, first instance
                    o0 = struct.unpack_from("<H", v, 0)[0] & 0x7FFF
                    o1 = struct.unpack_from("<H", v, 2)[0] & 0x7FFF if o0 >= 4 else len(v)
                    v = v[o0:o1]
                if hdr & 0x2 and v:
                    scheme = v[0] >> 3
                    if scheme in (1, 2):
                        v = _sevenbit(v[1:], scheme == 2)
                    else:
                        continue
                out[cid] = v
        return out


def _text(b, cp):
    if b is None:
        return None
    if cp == 1200:
        return b[:len(b) // 2 * 2].decode("utf-16-le", "replace").rstrip("\x00")
    return b.decode("cp1252", "replace").rstrip("\x00")


def _int(b, signed=True):
    return int.from_bytes(b, "little", signed=signed) if b else None


def _catalog(data):
    """[{name, pgno, cols: [(id, name, coltyp, codepage, size)]}] in catalog order, or None."""
    db = _Db(data)
    cat_cols = [(i, 0, w) for i, w in _CAT_FIXED] + [(128, 10, 0)]
    tables, cur = [], None
    for rec in db.leaf_records(4):
        v = db.columns(rec, cat_cols)
        typ, name = _int(v.get(2)), _text(v.get(128), 0)
        if typ == 1 and name:
            cur = {"name": name, "pgno": _int(v.get(4)), "cols": []}
            tables.append(cur)
        elif typ == 2 and cur is not None and name:
            cur["cols"].append((_int(v.get(3)), name, _int(v.get(4)), _int(v.get(7)) or 0, _int(v.get(5)) or 0))
    return db, tables


def _find(tables, param):
    want = _norm(param)
    if not want:
        return None
    for t in tables:
        if _norm(t["name"]) == want:
            return t
    for guid, friendly in _SRUM.items():
        if _norm(friendly) == want or _norm(friendly + "table") == want:
            for t in tables:
                if _norm(t["name"]) == _norm(guid):
                    return t
    return None


def _rows(db, t):
    """[{column name: decoded value}] of table t."""
    cols = [(c[0], c[2], c[4]) for c in t["cols"]]
    out = []
    for rec in db.leaf_records(t["pgno"]):
        raw = db.columns(rec, cols)
        row = {}
        for cid, name, ct, cp, _size in t["cols"]:
            b = raw.get(cid)
            if b is None:
                continue
            if ct in (10, 12):
                row[name] = _text(bytes(b), cp)
            elif ct in (1, 2, 3, 4, 15):
                row[name] = _int(b, ct not in (1, 2))
            elif ct in (14, 17):
                row[name] = _int(b, False)
            else:
                row[name] = bytes(b)
        out.append(row)
    return out


def _sid(b):
    if len(b) < 8 or b[0] != 1 or len(b) < 8 + 4 * b[1]:
        return None
    auth = int.from_bytes(b[2:8], "big")
    subs = struct.unpack_from("<%dI" % b[1], b, 8)
    return "S-1-%d" % auth + "".join("-%d" % s for s in subs)


def catalog_value(data, ctx):
    """ese.<catalog field>: see the module docstring."""
    if data is None:
        return None
    if len(data) < 8 or data[4:8] != _MAGIC:
        return "none"
    field = (ctx.get("field") or "").lower()
    param = ctx.get("param")
    try:
        return _answer(data, field, param)
    except Exception:                         # damaged pages: never raise past the extractor
        return None


def _answer(data, field, param):
    db, tables = _catalog(data)
    if not tables:
        return None
    names = [t["name"] for t in tables]
    user = [n for n in names if not n.startswith("MSys")]
    if field in ("table_names", "user_table_names", "table_names_sorted"):
        return sorted(user)
    if field in ("all_table_names", "catalog_table_names"):
        return sorted(names)
    if field in ("system_table_names", "msys_table_names"):
        return sorted(n for n in names if n.startswith("MSys"))
    if field in ("table_count", "user_table_count"):
        return len(user)
    if field in ("all_table_count", "catalog_table_count"):
        return len(names)
    if param is not None:
        t = _find(tables, param)
        if t is None:
            return "none"
        if field.startswith(("column_names_", "table_column_names_")):
            return [c[1] for c in sorted(t["cols"], key=lambda c: c[0])]
        if field.startswith("column_count_"):
            return len(t["cols"])
        if t["pgno"] is None:
            return None
        return len(db.leaf_records(t["pgno"]))
    if field.startswith("srum_table") or field == "srum_tables_present":
        present = [g for g in _SRUM if any(n.upper() == g for n in names)]
        if field == "srum_table_guids":
            return sorted(n for n in names if n.upper() in _SRUM)
        return sorted(_SRUM[g] for g in present) if present else "none"
    if field.startswith(("srum_", "app_", "application_", "user_sids", "id_map")):
        t = _find(tables, "SruDbIdMapTable")
        if t is None:
            return "none"
        rows = _rows(db, t)
        if field in ("srum_id_map_count", "id_map_entry_count"):
            return len(rows)
        apps, sids = set(), set()
        for r in rows:
            blob = r.get("IdBlob")
            if not isinstance(blob, bytes) or not blob:
                continue
            if r.get("IdType") == 3:
                s = _sid(blob)
                if s:
                    sids.add(s)
            else:
                s = _text(blob, 1200)
                if s:
                    apps.add(s)
        return sorted(sids if "sid" in field else apps)
    if "container" in field:
        t = _find(tables, "Containers")
        if t is None:
            return "none"
        rows = _rows(db, t)
        if field.endswith("_count"):
            return len(rows)
        key = "Directory" if "director" in field else "Name"
        return [r[key] for r in rows if isinstance(r.get(key), str)]
    return None
