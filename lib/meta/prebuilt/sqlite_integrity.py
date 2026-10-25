"""SQLite 3 header-vs-file consistency (prebuilt, SPECULATIVE; D23 "Page Me Maybe" flavor: databases "copied,
truncated, embedded, and mislabeled ... find the impossible claim"). The verified page_size_bytes path stays in
lib.meta._BUILTIN / sqlite.py; this module only adds integrity fields (+ the sqlite3 / db / database format aliases).

Header (sqlite.org/fileformat2.html, BIG-endian): magic "SQLite format 3\\0" @0, page size u16 @16 (1 = 65536;
otherwise a power of two 512..32768), write/read version u8 @18/@19 (1 legacy rollback journal, 2 WAL), reserved bytes
u8 @20, max/min/leaf payload fractions u8 @21/@22/@23 (MUST be 64/32/32), file change counter u32 @24, in-header
database size in pages u32 @28, first freelist trunk page u32 @32, freelist page count u32 @36, schema cookie u32 @40,
schema format u32 @44 (1..4), text encoding u32 @56 (1/2/3), version-valid-for u32 @92, SQLITE_VERSION_NUMBER u32 @96.

SQLite trusts the in-header size @28 only when it is non-zero AND change counter @24 == version-valid-for @92
(header_size_valid); otherwise the size is file length // page size (legacy writers). expected_size_bytes = @28 x page
size; file_page_count = len // page size; trailing_bytes = len - expected when > 0 (else 0); is_truncated = a valid
in-header size the file does not cover (len < expected) or a partial last page (len % page size != 0).
journal_mode_claim follows the READ version @19 ("wal" = 2, "legacy" = 1) -- btree.c opens the WAL when page1[19]==2.
impossible_claims = sorted JSON list of the failed rule names:
  page_size          @16 not a power of two 512..32768 nor 1
  payload_fractions  @21/@22/@23 != 64/32/32 (SQLite refuses the file: SQLITE_NOTADB)
  schema_format      @44 not 1..4 (0 allowed only for an empty schema, schema cookie @40 == 0)
  encoding           @56 not 1/2/3 (0 allowed only for an empty schema)
  size_vs_file       a VALID in-header size claims more bytes than the file has
  freelist_range     first trunk page > file pages, freelist count > file pages - 1, or exactly one of them zero
  version_valid_for  @92 != change counter @24 (stale header: @28 must not be trusted)
Not "SQLite format 3\\0" (decoy / renamed impostor) -> "none"; magic with < 100 header bytes -> None."""
import struct

from ..spell import Hex

FIELDS = {
    ("sqlite", "file_size_bytes"): "integrity_value",
    ("sqlite", "actual_size_bytes"): "integrity_value",
    ("sqlite", "expected_size_bytes"): "integrity_value",
    ("sqlite", "expected_file_size_bytes"): "integrity_value",
    ("sqlite", "header_size_bytes"): "integrity_value",
    ("sqlite", "in_header_size_bytes"): "integrity_value",
    ("sqlite", "file_page_count"): "integrity_value",
    ("sqlite", "actual_page_count"): "integrity_value",
    ("sqlite", "physical_page_count"): "integrity_value",
    ("sqlite", "in_header_page_count"): "integrity_value",
    ("sqlite", "is_truncated"): "integrity_value",
    ("sqlite", "truncated"): "integrity_value",
    ("sqlite", "is_padded"): "integrity_value",
    ("sqlite", "trailing_bytes"): "integrity_value",
    ("sqlite", "trailing_bytes_count"): "integrity_value",
    ("sqlite", "trailing_byte_count"): "integrity_value",
    ("sqlite", "has_trailing_bytes"): "integrity_value",
    ("sqlite", "trailing_bytes_present"): "integrity_value",
    ("sqlite", "missing_bytes"): "integrity_value",
    ("sqlite", "header_size_valid"): "integrity_value",
    ("sqlite", "in_header_size_valid"): "integrity_value",
    ("sqlite", "header_database_size_valid"): "integrity_value",
    ("sqlite", "page_size_valid"): "integrity_value",
    ("sqlite", "page_size_raw_u16_hex"): "integrity_value",
    ("sqlite", "page_size_u16_hex"): "integrity_value",
    ("sqlite", "journal_mode_claim"): "integrity_value",
    ("sqlite", "journal_mode_claimed"): "integrity_value",
    ("sqlite", "max_payload_fraction"): "integrity_value",
    ("sqlite", "min_payload_fraction"): "integrity_value",
    ("sqlite", "leaf_payload_fraction"): "integrity_value",
    ("sqlite", "payload_fractions_valid"): "integrity_value",
    ("sqlite", "freelist_trunk_beyond_eof"): "integrity_value",
    ("sqlite", "schema_format_valid"): "integrity_value",
    ("sqlite", "encoding_valid"): "integrity_value",
    ("sqlite", "text_encoding_valid"): "integrity_value",
    ("sqlite", "impossible_claims"): "integrity_value",
    ("sqlite", "impossible_header_claims"): "integrity_value",
    ("sqlite", "failed_rules"): "integrity_value",
    ("sqlite", "impossible_claim"): "integrity_value",
    ("sqlite", "header_consistent"): "integrity_value",
    # format aliases (the GM may spell the token sqlite3 / db / database): the integrity fields + the header basics
    ("sqlite3", "file_size_bytes"): "integrity_value",
    ("sqlite3", "expected_size_bytes"): "integrity_value",
    ("sqlite3", "file_page_count"): "integrity_value",
    ("sqlite3", "in_header_page_count"): "integrity_value",
    ("sqlite3", "is_truncated"): "integrity_value",
    ("sqlite3", "trailing_bytes"): "integrity_value",
    ("sqlite3", "header_size_valid"): "integrity_value",
    ("sqlite3", "page_size_valid"): "integrity_value",
    ("sqlite3", "page_size_raw_u16_hex"): "integrity_value",
    ("sqlite3", "page_size_bytes"): "integrity_value",
    ("sqlite3", "page_size"): "integrity_value",
    ("sqlite3", "sqlite_version"): "integrity_value",
    ("sqlite3", "sqlite_version_number"): "integrity_value",
    ("sqlite3", "write_version"): "integrity_value",
    ("sqlite3", "read_version"): "integrity_value",
    ("sqlite3", "journal_mode_claim"): "integrity_value",
    ("sqlite3", "reserved_bytes"): "integrity_value",
    ("sqlite3", "max_payload_fraction"): "integrity_value",
    ("sqlite3", "min_payload_fraction"): "integrity_value",
    ("sqlite3", "leaf_payload_fraction"): "integrity_value",
    ("sqlite3", "payload_fractions_valid"): "integrity_value",
    ("sqlite3", "freelist_trunk_beyond_eof"): "integrity_value",
    ("sqlite3", "schema_format"): "integrity_value",
    ("sqlite3", "impossible_claims"): "integrity_value",
    ("db", "file_size_bytes"): "integrity_value",
    ("db", "expected_size_bytes"): "integrity_value",
    ("db", "file_page_count"): "integrity_value",
    ("db", "in_header_page_count"): "integrity_value",
    ("db", "is_truncated"): "integrity_value",
    ("db", "trailing_bytes"): "integrity_value",
    ("db", "header_size_valid"): "integrity_value",
    ("db", "page_size_valid"): "integrity_value",
    ("db", "page_size_raw_u16_hex"): "integrity_value",
    ("db", "page_size_bytes"): "integrity_value",
    ("db", "page_size"): "integrity_value",
    ("db", "sqlite_version"): "integrity_value",
    ("db", "sqlite_version_number"): "integrity_value",
    ("db", "write_version"): "integrity_value",
    ("db", "read_version"): "integrity_value",
    ("db", "journal_mode_claim"): "integrity_value",
    ("db", "reserved_bytes"): "integrity_value",
    ("db", "max_payload_fraction"): "integrity_value",
    ("db", "min_payload_fraction"): "integrity_value",
    ("db", "leaf_payload_fraction"): "integrity_value",
    ("db", "payload_fractions_valid"): "integrity_value",
    ("db", "freelist_trunk_beyond_eof"): "integrity_value",
    ("db", "schema_format"): "integrity_value",
    ("db", "impossible_claims"): "integrity_value",
    ("database", "file_size_bytes"): "integrity_value",
    ("database", "expected_size_bytes"): "integrity_value",
    ("database", "file_page_count"): "integrity_value",
    ("database", "in_header_page_count"): "integrity_value",
    ("database", "is_truncated"): "integrity_value",
    ("database", "trailing_bytes"): "integrity_value",
    ("database", "header_size_valid"): "integrity_value",
    ("database", "page_size_valid"): "integrity_value",
    ("database", "page_size_raw_u16_hex"): "integrity_value",
    ("database", "page_size_bytes"): "integrity_value",
    ("database", "page_size"): "integrity_value",
    ("database", "sqlite_version"): "integrity_value",
    ("database", "sqlite_version_number"): "integrity_value",
    ("database", "write_version"): "integrity_value",
    ("database", "read_version"): "integrity_value",
    ("database", "journal_mode_claim"): "integrity_value",
    ("database", "reserved_bytes"): "integrity_value",
    ("database", "max_payload_fraction"): "integrity_value",
    ("database", "min_payload_fraction"): "integrity_value",
    ("database", "leaf_payload_fraction"): "integrity_value",
    ("database", "payload_fractions_valid"): "integrity_value",
    ("database", "freelist_trunk_beyond_eof"): "integrity_value",
    ("database", "schema_format"): "integrity_value",
    ("database", "impossible_claims"): "integrity_value",
}

_MAGIC = b"SQLite format 3\x00"


def _facts(b):
    """Every header/file fact as a dict (page size may be invalid), or None when the 100-byte header is short."""
    if len(b) < 100:
        return None
    raw, = struct.unpack_from(">H", b, 16)
    ps = 65536 if raw == 1 else raw
    ps_ok = raw == 1 or (512 <= raw <= 32768 and not raw & (raw - 1))
    cc, npg, trunk, nfree, cookie, sfmt = struct.unpack_from(">6I", b, 24)
    enc, = struct.unpack_from(">I", b, 56)
    vvf, ver = struct.unpack_from(">2I", b, 92)
    n = len(b)
    hdr_ok = npg != 0 and cc == vvf
    expected = npg * ps if ps_ok else None
    fpages = n // ps if ps_ok else None
    f = {"raw": raw, "ps": ps, "ps_ok": ps_ok, "w": b[18], "r": b[19], "reserved": b[20],
         "fr": (b[21], b[22], b[23]), "cc": cc, "npg": npg, "trunk": trunk, "nfree": nfree, "cookie": cookie,
         "sfmt": sfmt, "enc": enc, "vvf": vvf, "ver": ver, "len": n, "hdr_ok": hdr_ok, "expected": expected,
         "fpages": fpages}
    f["fr_ok"] = f["fr"] == (64, 32, 32)
    f["trailing"] = n - expected if expected and npg and n > expected else 0
    f["missing"] = expected - n if expected and hdr_ok and n < expected else 0
    f["truncated"] = bool(ps_ok and ((hdr_ok and n < expected) or n % ps))
    f["trunk_eof"] = bool(ps_ok and trunk and trunk > fpages)
    empty = cookie == 0
    bad = []
    if not ps_ok:
        bad.append("page_size")
    if not f["fr_ok"]:
        bad.append("payload_fractions")
    if not (1 <= sfmt <= 4 or (sfmt == 0 and empty)):
        bad.append("schema_format")
    if enc not in (1, 2, 3) and not (enc == 0 and empty):
        bad.append("encoding")
    if ps_ok and hdr_ok and expected > n:
        bad.append("size_vs_file")
    if ps_ok and (f["trunk_eof"] or nfree > max(fpages - 1, 0) or (trunk == 0) != (nfree == 0)):
        bad.append("freelist_range")
    if vvf != cc:
        bad.append("version_valid_for")
    f["bad"] = sorted(bad)
    return f


def integrity_value(data, ctx):
    try:
        if not data or bytes(data[:16]) != _MAGIC:
            return "none"
        f = _facts(bytes(data))
        if f is None:
            return None
        fld = ctx.get("field") or ""
        if fld in ("file_size_bytes", "actual_size_bytes"):
            return f["len"]
        if fld in ("expected_size_bytes", "expected_file_size_bytes", "header_size_bytes", "in_header_size_bytes"):
            return f["expected"]
        if fld in ("file_page_count", "actual_page_count", "physical_page_count"):
            return f["fpages"]
        if fld == "in_header_page_count":
            return f["npg"]
        if fld in ("is_truncated", "truncated"):
            return f["truncated"]
        if fld == "is_padded":
            return f["trailing"] > 0
        if fld in ("has_trailing_bytes", "trailing_bytes_present"):
            return f["trailing"] > 0
        if fld.startswith("trailing_byte"):
            return f["trailing"]
        if fld == "missing_bytes":
            return f["missing"]
        if fld in ("header_size_valid", "in_header_size_valid", "header_database_size_valid"):
            return f["hdr_ok"]
        if fld == "page_size_valid":
            return f["ps_ok"]
        if fld in ("page_size_raw_u16_hex", "page_size_u16_hex"):
            return Hex(f["raw"], 4)
        if fld in ("page_size", "page_size_bytes"):
            return f["ps"] if f["ps_ok"] else None
        if fld in ("journal_mode_claim", "journal_mode_claimed"):
            return {1: "legacy", 2: "wal"}.get(f["r"])
        if fld == "write_version":
            return f["w"]
        if fld == "read_version":
            return f["r"]
        if fld == "reserved_bytes":
            return f["reserved"]
        if fld == "max_payload_fraction":
            return f["fr"][0]
        if fld == "min_payload_fraction":
            return f["fr"][1]
        if fld == "leaf_payload_fraction":
            return f["fr"][2]
        if fld == "payload_fractions_valid":
            return f["fr_ok"]
        if fld == "freelist_trunk_beyond_eof":
            return f["trunk_eof"]
        if fld == "schema_format":
            return f["sfmt"]
        if fld == "schema_format_valid":
            return "schema_format" not in f["bad"]
        if fld in ("encoding_valid", "text_encoding_valid"):
            return "encoding" not in f["bad"]
        if fld == "sqlite_version_number":
            return f["ver"]
        if fld == "sqlite_version":
            v = f["ver"]
            return "%d.%d.%d" % (v // 1000000, v // 1000 % 1000, v % 1000) if v else "none"
        if fld in ("impossible_claims", "impossible_header_claims", "failed_rules"):
            return f["bad"]
        if fld == "impossible_claim":      # singular: the one failed rule; none when clean, None when ambiguous
            return f["bad"][0] if len(f["bad"]) == 1 else ("none" if not f["bad"] else None)
        if fld == "header_consistent":
            return not f["bad"]
        return None
    except Exception:  # noqa: BLE001
        return None
