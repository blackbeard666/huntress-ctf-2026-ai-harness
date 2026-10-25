"""SQLite sidecar files: write-ahead log (`-wal`), rollback journal (`-journal`) and wal-index (`-shm`) (prebuilt,
SPECULATIVE). Format words: sqlite_wal / wal, sqlite_journal / journal, sqlite_shm / shm; under `sqlite`
only the keys no other module owns (a main database file answers "none" here).

WAL (sqlite wal.c): 32-B header, every field u32 BIG-endian: magic @0 (0x377f0682 = little-endian checksum words,
0x377f0683 = big-endian), format version @4 (3007000), page size @8, checkpoint sequence @12, salt-1 @16, salt-2 @20,
checksum-1/2 @24/@28 (over header bytes 0..23). Frames follow: 24-B header {page number, db size in pages after
commit (non-zero = commit frame), salt-1, salt-2, cksum-1, cksum-2} + one page.
  frame_count = (len - 32) // (24 + page size) (whole frames physically present, stale ones included).
  commit_frame_count = frames with a non-zero db-size field.
  valid_frame_count = frames from frame 1 up to the first one whose salts differ from the header OR whose cumulative
    checksum (seeded with the header checksum; over frame-header bytes 0..7 + the page) mismatches -- the walk stops
    there, as wal.c's recovery does. It does NOT additionally drop trailing uncommitted valid frames (sqlite's mxFrame
    does; with every fixture ending on a commit frame both agree).
  pages_written = sorted unique page numbers of the valid frames (compact JSON list).
  last_commit_db_size_pages = db-size field of the last VALID commit frame (0 frames -> "none").
  checksum: s0 += x0 + s1; s1 += x1 + s0 (mod 2^32) over u32 pairs, words read in the magic's byte order.
Rollback journal (pager.c): magic d9 d5 05 f9 20 a1 63 d7, then u32 BE: record count @8 (0xffffffff = no-sync writer:
  computed as (len - sector size) // (page size + 8)), nonce @12, initial db size in pages @16, sector size @20, page
  size @24. A journal whose magic is still zero (header not yet synced) or any other bytes -> "none".
wal-index (-shm): WalIndexHdr in NATIVE byte order (version 3007000 @0 decides LE vs BE): iChange @8, isInit u8 @12,
  bigEndCksum u8 @13, szPage u16 @14 (65536 stored as 1), mxFrame u32 @16, nPage u32 @20, salts @32/@36 (raw copy of
  the WAL header bytes -> read BE like the WAL). Not a wal-index -> "none"."""
import struct

from ..spell import Hex

FIELDS = {
    ("sqlite_wal", "wal_page_size_bytes"): "wal_value",
    ("sqlite_wal", "wal_format_version"): "wal_value",
    ("sqlite_wal", "checkpoint_sequence"): "wal_value",
    ("sqlite_wal", "wal_checkpoint_sequence"): "wal_value",
    ("sqlite_wal", "salt1_u32_hex"): "wal_value",
    ("sqlite_wal", "salt2_u32_hex"): "wal_value",
    ("sqlite_wal", "salt_1_u32_hex"): "wal_value",
    ("sqlite_wal", "salt_2_u32_hex"): "wal_value",
    ("sqlite_wal", "wal_salt1_u32_hex"): "wal_value",
    ("sqlite_wal", "wal_salt2_u32_hex"): "wal_value",
    ("sqlite_wal", "wal_magic_u32_hex"): "wal_value",
    ("sqlite_wal", "frame_count"): "wal_value",
    ("sqlite_wal", "wal_frame_count"): "wal_value",
    ("sqlite_wal", "commit_frame_count"): "wal_value",
    ("sqlite_wal", "wal_commit_frame_count"): "wal_value",
    ("sqlite_wal", "valid_frame_count"): "wal_value",
    ("sqlite_wal", "wal_valid_frame_count"): "wal_value",
    ("sqlite_wal", "pages_written"): "wal_value",
    ("sqlite_wal", "wal_pages_written"): "wal_value",
    ("sqlite_wal", "last_commit_db_size_pages"): "wal_value",
    ("sqlite_wal", "wal_last_commit_db_size_pages"): "wal_value",
    ("sqlite_wal", "checksum1_u32_hex"): "wal_value",
    ("sqlite_wal", "checksum2_u32_hex"): "wal_value",
    ("sqlite_wal", "checksum_1_u32_hex"): "wal_value",
    ("sqlite_wal", "checksum_2_u32_hex"): "wal_value",
    ("sqlite_wal", "wal_checksum_big_endian"): "wal_value",
    ("sqlite_wal", "header_checksum_valid"): "wal_value",
    ("sqlite_wal", "wal_header_checksum_valid"): "wal_value",
    ("sqlite_wal", "page_size_bytes"): "wal_value",
    ("sqlite_wal", "page_size"): "wal_value",
    ("sqlite_wal", "format_version"): "wal_value",
    ("sqlite_wal", "version"): "wal_value",
    ("sqlite_wal", "magic_u32_hex"): "wal_value",
    ("sqlite_wal", "checksum_big_endian"): "wal_value",
    ("sqlite_wal", "big_endian_checksums"): "wal_value",
    ("wal", "wal_page_size_bytes"): "wal_value",
    ("wal", "wal_format_version"): "wal_value",
    ("wal", "checkpoint_sequence"): "wal_value",
    ("wal", "wal_checkpoint_sequence"): "wal_value",
    ("wal", "salt1_u32_hex"): "wal_value",
    ("wal", "salt2_u32_hex"): "wal_value",
    ("wal", "salt_1_u32_hex"): "wal_value",
    ("wal", "salt_2_u32_hex"): "wal_value",
    ("wal", "wal_salt1_u32_hex"): "wal_value",
    ("wal", "wal_salt2_u32_hex"): "wal_value",
    ("wal", "wal_magic_u32_hex"): "wal_value",
    ("wal", "frame_count"): "wal_value",
    ("wal", "wal_frame_count"): "wal_value",
    ("wal", "commit_frame_count"): "wal_value",
    ("wal", "wal_commit_frame_count"): "wal_value",
    ("wal", "valid_frame_count"): "wal_value",
    ("wal", "wal_valid_frame_count"): "wal_value",
    ("wal", "pages_written"): "wal_value",
    ("wal", "wal_pages_written"): "wal_value",
    ("wal", "last_commit_db_size_pages"): "wal_value",
    ("wal", "wal_last_commit_db_size_pages"): "wal_value",
    ("wal", "checksum1_u32_hex"): "wal_value",
    ("wal", "checksum2_u32_hex"): "wal_value",
    ("wal", "checksum_1_u32_hex"): "wal_value",
    ("wal", "checksum_2_u32_hex"): "wal_value",
    ("wal", "wal_checksum_big_endian"): "wal_value",
    ("wal", "header_checksum_valid"): "wal_value",
    ("wal", "wal_header_checksum_valid"): "wal_value",
    ("wal", "page_size_bytes"): "wal_value",
    ("wal", "page_size"): "wal_value",
    ("wal", "format_version"): "wal_value",
    ("wal", "version"): "wal_value",
    ("wal", "magic_u32_hex"): "wal_value",
    ("wal", "checksum_big_endian"): "wal_value",
    ("wal", "big_endian_checksums"): "wal_value",
    ("sqlite", "wal_page_size_bytes"): "wal_value",
    ("sqlite", "wal_format_version"): "wal_value",
    ("sqlite", "checkpoint_sequence"): "wal_value",
    ("sqlite", "wal_checkpoint_sequence"): "wal_value",
    ("sqlite", "salt1_u32_hex"): "wal_value",
    ("sqlite", "salt2_u32_hex"): "wal_value",
    ("sqlite", "salt_1_u32_hex"): "wal_value",
    ("sqlite", "salt_2_u32_hex"): "wal_value",
    ("sqlite", "wal_salt1_u32_hex"): "wal_value",
    ("sqlite", "wal_salt2_u32_hex"): "wal_value",
    ("sqlite", "wal_magic_u32_hex"): "wal_value",
    ("sqlite", "frame_count"): "wal_value",
    ("sqlite", "wal_frame_count"): "wal_value",
    ("sqlite", "commit_frame_count"): "wal_value",
    ("sqlite", "wal_commit_frame_count"): "wal_value",
    ("sqlite", "valid_frame_count"): "wal_value",
    ("sqlite", "wal_valid_frame_count"): "wal_value",
    ("sqlite", "pages_written"): "wal_value",
    ("sqlite", "wal_pages_written"): "wal_value",
    ("sqlite", "last_commit_db_size_pages"): "wal_value",
    ("sqlite", "wal_last_commit_db_size_pages"): "wal_value",
    ("sqlite", "checksum1_u32_hex"): "wal_value",
    ("sqlite", "checksum2_u32_hex"): "wal_value",
    ("sqlite", "checksum_1_u32_hex"): "wal_value",
    ("sqlite", "checksum_2_u32_hex"): "wal_value",
    ("sqlite", "wal_checksum_big_endian"): "wal_value",
    ("sqlite", "wal_header_checksum_valid"): "wal_value",
    ("sqlite_journal", "journal_page_count"): "journal_value",
    ("sqlite_journal", "journal_record_count"): "journal_value",
    ("sqlite_journal", "journal_page_size_bytes"): "journal_value",
    ("sqlite_journal", "journal_sector_size"): "journal_value",
    ("sqlite_journal", "journal_sector_size_bytes"): "journal_value",
    ("sqlite_journal", "journal_nonce_u32_hex"): "journal_value",
    ("sqlite_journal", "journal_initial_db_size_pages"): "journal_value",
    ("sqlite_journal", "initial_db_size_pages"): "journal_value",
    ("sqlite_journal", "initial_database_size_pages"): "journal_value",
    ("sqlite_journal", "page_count"): "journal_value",
    ("sqlite_journal", "record_count"): "journal_value",
    ("sqlite_journal", "page_size_bytes"): "journal_value",
    ("sqlite_journal", "page_size"): "journal_value",
    ("sqlite_journal", "sector_size"): "journal_value",
    ("sqlite_journal", "sector_size_bytes"): "journal_value",
    ("sqlite_journal", "nonce_u32_hex"): "journal_value",
    ("journal", "journal_page_count"): "journal_value",
    ("journal", "journal_record_count"): "journal_value",
    ("journal", "journal_page_size_bytes"): "journal_value",
    ("journal", "journal_sector_size"): "journal_value",
    ("journal", "journal_sector_size_bytes"): "journal_value",
    ("journal", "journal_nonce_u32_hex"): "journal_value",
    ("journal", "journal_initial_db_size_pages"): "journal_value",
    ("journal", "initial_db_size_pages"): "journal_value",
    ("journal", "initial_database_size_pages"): "journal_value",
    ("journal", "page_count"): "journal_value",
    ("journal", "record_count"): "journal_value",
    ("journal", "page_size_bytes"): "journal_value",
    ("journal", "page_size"): "journal_value",
    ("journal", "sector_size"): "journal_value",
    ("journal", "sector_size_bytes"): "journal_value",
    ("journal", "nonce_u32_hex"): "journal_value",
    ("sqlite", "journal_page_count"): "journal_value",
    ("sqlite", "journal_record_count"): "journal_value",
    ("sqlite", "journal_page_size_bytes"): "journal_value",
    ("sqlite", "journal_sector_size"): "journal_value",
    ("sqlite", "journal_sector_size_bytes"): "journal_value",
    ("sqlite", "journal_nonce_u32_hex"): "journal_value",
    ("sqlite", "journal_initial_db_size_pages"): "journal_value",
    ("sqlite", "initial_db_size_pages"): "journal_value",
    ("sqlite", "initial_database_size_pages"): "journal_value",
    ("sqlite_shm", "wal_index_version"): "shm_value",
    ("sqlite_shm", "shm_version"): "shm_value",
    ("sqlite_shm", "mx_frame"): "shm_value",
    ("sqlite_shm", "max_frame"): "shm_value",
    ("sqlite_shm", "shm_mx_frame"): "shm_value",
    ("sqlite_shm", "n_page"): "shm_value",
    ("sqlite_shm", "shm_n_page"): "shm_value",
    ("sqlite_shm", "db_size_pages"): "shm_value",
    ("sqlite_shm", "shm_page_size_bytes"): "shm_value",
    ("sqlite_shm", "shm_change_counter"): "shm_value",
    ("sqlite_shm", "change_counter"): "shm_value",
    ("sqlite_shm", "version"): "shm_value",
    ("sqlite_shm", "page_size_bytes"): "shm_value",
    ("sqlite_shm", "page_size"): "shm_value",
    ("sqlite_shm", "page_count"): "shm_value",
    ("sqlite_shm", "salt1_u32_hex"): "shm_value",
    ("sqlite_shm", "salt2_u32_hex"): "shm_value",
    ("shm", "wal_index_version"): "shm_value",
    ("shm", "shm_version"): "shm_value",
    ("shm", "mx_frame"): "shm_value",
    ("shm", "max_frame"): "shm_value",
    ("shm", "shm_mx_frame"): "shm_value",
    ("shm", "n_page"): "shm_value",
    ("shm", "shm_n_page"): "shm_value",
    ("shm", "db_size_pages"): "shm_value",
    ("shm", "shm_page_size_bytes"): "shm_value",
    ("shm", "shm_change_counter"): "shm_value",
    ("shm", "change_counter"): "shm_value",
    ("shm", "version"): "shm_value",
    ("shm", "page_size_bytes"): "shm_value",
    ("shm", "page_size"): "shm_value",
    ("shm", "page_count"): "shm_value",
    ("shm", "salt1_u32_hex"): "shm_value",
    ("shm", "salt2_u32_hex"): "shm_value",
    ("sqlite", "wal_index_version"): "shm_value",
    ("sqlite", "shm_version"): "shm_value",
    ("sqlite", "mx_frame"): "shm_value",
    ("sqlite", "shm_mx_frame"): "shm_value",
    ("sqlite", "shm_n_page"): "shm_value",
    ("sqlite", "shm_page_size_bytes"): "shm_value",
}

_WAL_MAGICS = (0x377F0682, 0x377F0683)
_JOURNAL_MAGIC = b"\xd9\xd5\x05\xf9\x20\xa1\x63\xd7"
_WAL_INDEX_VERSION = 3007000
_M = 0xFFFFFFFF


def _cksum(buf, big, s0=0, s1=0):
    """sqlite walChecksumBytes: buf length a multiple of 8, words in the magic's byte order."""
    n = len(buf) // 4
    words = struct.unpack((">" if big else "<") + "%dI" % n, buf[:n * 4])
    for i in range(0, n - 1, 2):
        s0 = (s0 + words[i] + s1) & _M
        s1 = (s1 + words[i + 1] + s0) & _M
    return s0, s1


def parse_wal(b):
    """The WAL header + frame walk as a dict, or None when b is not a WAL."""
    if not b or len(b) < 32:
        return None
    magic, ver, ps, seq, salt1, salt2, c1, c2 = struct.unpack_from(">8I", b, 0)
    if magic not in _WAL_MAGICS:
        return None
    if ps == 1:
        ps = 65536    # wal.c stores 65536 as (ps & 0xff00) | (ps >> 16) = 1
    if ps < 512 or ps > 65536 or ps & (ps - 1):
        return None
    big = bool(magic & 1)
    hdr_ck = _cksum(b[:24], big)
    fsz = 24 + ps
    nframes = (len(b) - 32) // fsz
    commits = 0
    valid, pages, last_commit = 0, set(), None
    s0, s1 = c1, c2
    chain = True
    for i in range(nframes):
        off = 32 + i * fsz
        pgno, dbsz, fs1, fs2, fc1, fc2 = struct.unpack_from(">6I", b, off)
        if dbsz:
            commits += 1
        if not chain:
            continue
        if pgno == 0 or (fs1, fs2) != (salt1, salt2):
            chain = False
            continue
        s0, s1 = _cksum(b[off:off + 8], big, s0, s1)
        s0, s1 = _cksum(b[off + 24:off + fsz], big, s0, s1)
        if (s0, s1) != (fc1, fc2):
            chain = False
            continue
        valid += 1
        pages.add(pgno)
        if dbsz:
            last_commit = dbsz
    return {"magic": magic, "version": ver, "page_size": ps, "seq": seq, "salt1": salt1, "salt2": salt2,
            "c1": c1, "c2": c2, "hdr_ok": hdr_ck == (c1, c2), "big": big, "frames": nframes, "commits": commits,
            "valid": valid, "pages": sorted(pages), "last_commit": last_commit}


def wal_value(data, ctx):
    f = (ctx.get("field") or "").lower()
    w = parse_wal(data)
    if w is None:
        return None if data is None else "none"
    f = f[4:] if f.startswith("wal_") else f
    if f in ("page_size_bytes", "page_size"):
        return w["page_size"]
    if f in ("format_version", "version"):
        return w["version"]
    if f == "checkpoint_sequence":
        return w["seq"]
    if f in ("salt1_u32_hex", "salt_1_u32_hex"):
        return Hex(w["salt1"], 8)
    if f in ("salt2_u32_hex", "salt_2_u32_hex"):
        return Hex(w["salt2"], 8)
    if f == "magic_u32_hex":
        return Hex(w["magic"], 8)
    if f in ("checksum1_u32_hex", "checksum_1_u32_hex"):
        return Hex(w["c1"], 8)
    if f in ("checksum2_u32_hex", "checksum_2_u32_hex"):
        return Hex(w["c2"], 8)
    if f in ("checksum_big_endian", "big_endian_checksums"):
        return w["big"]
    if f == "header_checksum_valid":
        return w["hdr_ok"]
    if f == "frame_count":
        return w["frames"]
    if f == "commit_frame_count":
        return w["commits"]
    if f == "valid_frame_count":
        return w["valid"]
    if f == "pages_written":
        return w["pages"]
    if f == "last_commit_db_size_pages":
        return w["last_commit"] if w["last_commit"] is not None else "none"
    return None


def parse_journal(b):
    if not b or len(b) < 28 or b[:8] != _JOURNAL_MAGIC:
        return None
    nrec, nonce, init_sz, sector, ps = struct.unpack_from(">5I", b, 8)
    if ps < 512 or ps > 65536 or ps & (ps - 1) or sector < 32 or sector & (sector - 1):
        return None
    if nrec == _M:    # no-sync writer: the record count is the journal size (pager.c pager_playback)
        nrec = max(0, (len(b) - sector) // (ps + 8))
    return {"pages": nrec, "nonce": nonce, "init": init_sz, "sector": sector, "page_size": ps}


def journal_value(data, ctx):
    f = (ctx.get("field") or "").lower()
    j = parse_journal(data)
    if j is None:
        return None if data is None else "none"
    f = f[8:] if f.startswith("journal_") else f
    if f in ("page_count", "record_count"):
        return j["pages"]
    if f in ("page_size_bytes", "page_size"):
        return j["page_size"]
    if f in ("sector_size", "sector_size_bytes"):
        return j["sector"]
    if f == "nonce_u32_hex":
        return Hex(j["nonce"], 8)
    if f in ("initial_db_size_pages", "initial_database_size_pages"):
        return j["init"]
    return None


def parse_shm(b):
    if not b or len(b) < 48:
        return None
    for e in ("<", ">"):
        if struct.unpack_from(e + "I", b, 0)[0] == _WAL_INDEX_VERSION:
            break
    else:
        return None
    ver, _unused, change = struct.unpack_from(e + "3I", b, 0)
    szpage, = struct.unpack_from(e + "H", b, 14)
    mx, npage = struct.unpack_from(e + "2I", b, 16)
    salt1, salt2 = struct.unpack_from(">2I", b, 32)
    ps = 65536 if szpage == 1 else szpage
    return {"version": ver, "change": change, "page_size": ps, "mx": mx, "npage": npage,
            "salt1": salt1, "salt2": salt2}


def shm_value(data, ctx):
    f = (ctx.get("field") or "").lower()
    s = parse_shm(data)
    if s is None:
        return None if data is None else "none"
    f = f[4:] if f.startswith("shm_") else f
    if f in ("wal_index_version", "version"):
        return s["version"]
    if f in ("mx_frame", "max_frame"):
        return s["mx"]
    if f in ("n_page", "db_size_pages", "page_count"):
        return s["npage"]
    if f in ("page_size_bytes", "page_size"):
        return s["page_size"]
    if f == "change_counter":
        return s["change"]
    if f == "salt1_u32_hex":
        return Hex(s["salt1"], 8)
    if f == "salt2_u32_hex":
        return Hex(s["salt2"], 8)
    return None
