"""Windows registry hive base block + ROOT key, under the GM's D25 format word `registry` and its aliases (hive, reg,
windows_registry, ntuser, regf) with the `hive_*` spellings (prebuilt, SPECULATIVE except what lib.meta._BUILTIN
already verified: registry.hive_root_name). Only keys no other module registers; helpers come from prebuilt/regf.py.

D25 "Hive Mind" hives (single / TT / 9 Mastery sets): 8 KiB, v1.3, primary file type, one hbin, root nk at hbin 0x20
(flags 0x2c), random root name that differs from the base-block file name, 2 root values (Marker, Ordinal), 0 subkeys,
base-block FILETIME != root nk FILETIME on the single solve.
- root name: base block root cell offset u32 @0x24 + 0x1000 -> cell (i32 size) -> "nk", flags u16 (0x20 COMP_NAME
  latin-1 else UTF-16LE), name len u16 @nk+0x48, name @nk+0x4c. The cell must carry KEY_HIVE_ENTRY (0x04); if the
  offset points at garbage / a non-root nk, scan the hbins (8-byte aligned cells) for the first nk with flag 0x04.
- file name: UTF-16LE @0x30, 64 bytes, up to the first NUL (empty -> "none").
- times: FILETIME (100 ns since 1601-01-01 UTC) -> 'YYYY-MM-DDTHH:MM:SSZ', sub-seconds DROPPED (the GM answer_format
  text and regf.py/regf_integrity.py's house spelling; every D25 hive has a non-zero fraction, so a fractional
  spelling would never match that format). hive_last_written_* = base block u64 @12; root_last_written_* = root nk.
- sequence numbers u32 @4/@8 (int); *_sequence_numbers_match bool. version "major.minor" (u32 @20/@24);
  *_major_version / *_minor_version int. file_type u32 @28 int (0 primary, 1 log, 2 volatile, 6 log new).
  hive_bins_data_size_bytes u32 @40.
- root subkey/value counts: the nk header counts (@nk+0x14 / @nk+0x24); *_names: the walked list SORTED
  (case-sensitive) as compact JSON, [] when the key has none.
- hive_checksum_u32_hex: CALCULATED XOR of the 127 dwords 0x000..0x1F8 (libregf: 0 -> 1, 0xFFFFFFFF -> 0xFFFFFFFE);
  plain checksum_u32_hex on the new aliases = same; checksum_valid = calculated == stored u32 @0x1FC.
Not "regf" -> "none"; regf without any readable root nk -> None."""
import datetime
import struct

from ..spell import Hex
from .regf import _nk, _subkeys, _values, base_block

FIELDS = {
    ("registry", "root_key_name"): "root_name",
    ("registry", "root_name"): "root_name",
    ("registry", "root_nk_name"): "root_name",
    ("registry", "root_cell_key_name"): "root_name",
    ("registry", "hive_root_key_name"): "root_name",
    ("registry", "hive_file_name"): "file_name",
    ("registry", "base_block_file_name"): "file_name",
    ("registry", "file_name"): "file_name",
    ("registry", "hive_name"): "file_name",
    ("registry", "hive_last_written_utc"): "last_written",
    ("registry", "hive_last_written_time_utc"): "last_written",
    ("registry", "base_block_last_written_utc"): "last_written",
    ("registry", "root_last_written_utc"): "last_written",
    ("registry", "root_key_last_written_utc"): "last_written",
    ("registry", "hive_root_last_written_utc"): "last_written",
    ("registry", "hive_primary_sequence_number"): "sequence",
    ("registry", "hive_secondary_sequence_number"): "sequence",
    ("registry", "hive_sequence_numbers_match"): "sequence",
    ("registry", "sequence_numbers_match"): "sequence",
    ("registry", "hive_version"): "version",
    ("registry", "version"): "version",
    ("registry", "format_version"): "version",
    ("registry", "hive_major_version"): "version",
    ("registry", "hive_minor_version"): "version",
    ("registry", "hive_file_type"): "header_u32",
    ("registry", "hive_root_subkey_count"): "root_list",
    ("registry", "root_subkey_count"): "root_list",
    ("registry", "root_key_subkey_count"): "root_list",
    ("registry", "hive_root_value_count"): "root_list",
    ("registry", "root_value_count"): "root_list",
    ("registry", "root_key_value_count"): "root_list",
    ("registry", "hive_root_value_names"): "root_list",
    ("registry", "root_value_names"): "root_list",
    ("registry", "root_key_value_names"): "root_list",
    ("registry", "hive_root_subkey_names"): "root_list",
    ("registry", "root_subkey_names"): "root_list",
    ("registry", "root_key_subkey_names"): "root_list",
    ("registry", "hive_checksum_u32_hex"): "checksum",
    ("registry", "hive_checksum_valid"): "checksum",
    ("hive", "hive_root_name"): "root_name",
    ("hive", "root_key_name"): "root_name",
    ("hive", "root_name"): "root_name",
    ("hive", "root_nk_name"): "root_name",
    ("hive", "root_cell_key_name"): "root_name",
    ("hive", "hive_root_key_name"): "root_name",
    ("hive", "hive_file_name"): "file_name",
    ("hive", "base_block_file_name"): "file_name",
    ("hive", "file_name"): "file_name",
    ("hive", "hive_name"): "file_name",
    ("hive", "hive_last_written_utc"): "last_written",
    ("hive", "hive_last_written_time_utc"): "last_written",
    ("hive", "base_block_last_written_utc"): "last_written",
    ("hive", "root_last_written_utc"): "last_written",
    ("hive", "root_key_last_written_utc"): "last_written",
    ("hive", "hive_root_last_written_utc"): "last_written",
    ("hive", "hive_primary_sequence_number"): "sequence",
    ("hive", "hive_secondary_sequence_number"): "sequence",
    ("hive", "hive_sequence_numbers_match"): "sequence",
    ("hive", "sequence_numbers_match"): "sequence",
    ("hive", "hive_version"): "version",
    ("hive", "version"): "version",
    ("hive", "format_version"): "version",
    ("hive", "hive_major_version"): "version",
    ("hive", "hive_minor_version"): "version",
    ("hive", "hive_file_type"): "header_u32",
    ("hive", "hive_root_subkey_count"): "root_list",
    ("hive", "root_subkey_count"): "root_list",
    ("hive", "root_key_subkey_count"): "root_list",
    ("hive", "hive_root_value_count"): "root_list",
    ("hive", "root_value_count"): "root_list",
    ("hive", "root_key_value_count"): "root_list",
    ("hive", "hive_root_value_names"): "root_list",
    ("hive", "root_value_names"): "root_list",
    ("hive", "root_key_value_names"): "root_list",
    ("hive", "hive_root_subkey_names"): "root_list",
    ("hive", "root_subkey_names"): "root_list",
    ("hive", "root_key_subkey_names"): "root_list",
    ("hive", "hive_checksum_u32_hex"): "checksum",
    ("hive", "hive_checksum_valid"): "checksum",
    ("reg", "hive_root_name"): "root_name",
    ("reg", "root_key_name"): "root_name",
    ("reg", "root_name"): "root_name",
    ("reg", "root_nk_name"): "root_name",
    ("reg", "root_cell_key_name"): "root_name",
    ("reg", "hive_root_key_name"): "root_name",
    ("reg", "hive_file_name"): "file_name",
    ("reg", "base_block_file_name"): "file_name",
    ("reg", "file_name"): "file_name",
    ("reg", "hive_name"): "file_name",
    ("reg", "hive_last_written_utc"): "last_written",
    ("reg", "hive_last_written_time_utc"): "last_written",
    ("reg", "base_block_last_written_utc"): "last_written",
    ("reg", "root_last_written_utc"): "last_written",
    ("reg", "root_key_last_written_utc"): "last_written",
    ("reg", "hive_root_last_written_utc"): "last_written",
    ("reg", "hive_primary_sequence_number"): "sequence",
    ("reg", "hive_secondary_sequence_number"): "sequence",
    ("reg", "hive_sequence_numbers_match"): "sequence",
    ("reg", "sequence_numbers_match"): "sequence",
    ("reg", "hive_version"): "version",
    ("reg", "version"): "version",
    ("reg", "format_version"): "version",
    ("reg", "hive_major_version"): "version",
    ("reg", "hive_minor_version"): "version",
    ("reg", "hive_file_type"): "header_u32",
    ("reg", "hive_root_subkey_count"): "root_list",
    ("reg", "root_subkey_count"): "root_list",
    ("reg", "root_key_subkey_count"): "root_list",
    ("reg", "hive_root_value_count"): "root_list",
    ("reg", "root_value_count"): "root_list",
    ("reg", "root_key_value_count"): "root_list",
    ("reg", "hive_root_value_names"): "root_list",
    ("reg", "root_value_names"): "root_list",
    ("reg", "root_key_value_names"): "root_list",
    ("reg", "hive_root_subkey_names"): "root_list",
    ("reg", "root_subkey_names"): "root_list",
    ("reg", "root_key_subkey_names"): "root_list",
    ("reg", "hive_checksum_u32_hex"): "checksum",
    ("reg", "hive_checksum_valid"): "checksum",
    ("windows_registry", "hive_root_name"): "root_name",
    ("windows_registry", "root_key_name"): "root_name",
    ("windows_registry", "root_name"): "root_name",
    ("windows_registry", "root_nk_name"): "root_name",
    ("windows_registry", "root_cell_key_name"): "root_name",
    ("windows_registry", "hive_root_key_name"): "root_name",
    ("windows_registry", "hive_file_name"): "file_name",
    ("windows_registry", "base_block_file_name"): "file_name",
    ("windows_registry", "file_name"): "file_name",
    ("windows_registry", "embedded_file_name"): "file_name",
    ("windows_registry", "hive_name"): "file_name",
    ("windows_registry", "hive_last_written_utc"): "last_written",
    ("windows_registry", "hive_last_written_time_utc"): "last_written",
    ("windows_registry", "base_block_last_written_utc"): "last_written",
    ("windows_registry", "last_written_time_utc"): "last_written",
    ("windows_registry", "root_last_written_utc"): "last_written",
    ("windows_registry", "root_key_last_written_utc"): "last_written",
    ("windows_registry", "hive_root_last_written_utc"): "last_written",
    ("windows_registry", "hive_primary_sequence_number"): "sequence",
    ("windows_registry", "primary_sequence_number"): "sequence",
    ("windows_registry", "hive_secondary_sequence_number"): "sequence",
    ("windows_registry", "secondary_sequence_number"): "sequence",
    ("windows_registry", "hive_sequence_numbers_match"): "sequence",
    ("windows_registry", "sequence_numbers_match"): "sequence",
    ("windows_registry", "hive_version"): "version",
    ("windows_registry", "version"): "version",
    ("windows_registry", "format_version"): "version",
    ("windows_registry", "hive_major_version"): "version",
    ("windows_registry", "hive_minor_version"): "version",
    ("windows_registry", "major_version"): "version",
    ("windows_registry", "minor_version"): "version",
    ("windows_registry", "hive_file_type"): "header_u32",
    ("windows_registry", "file_type"): "header_u32",
    ("windows_registry", "hive_bins_data_size_bytes"): "header_u32",
    ("windows_registry", "hive_root_subkey_count"): "root_list",
    ("windows_registry", "root_subkey_count"): "root_list",
    ("windows_registry", "root_key_subkey_count"): "root_list",
    ("windows_registry", "hive_root_value_count"): "root_list",
    ("windows_registry", "root_value_count"): "root_list",
    ("windows_registry", "root_key_value_count"): "root_list",
    ("windows_registry", "hive_root_value_names"): "root_list",
    ("windows_registry", "root_value_names"): "root_list",
    ("windows_registry", "root_key_value_names"): "root_list",
    ("windows_registry", "hive_root_subkey_names"): "root_list",
    ("windows_registry", "root_subkey_names"): "root_list",
    ("windows_registry", "root_key_subkey_names"): "root_list",
    ("windows_registry", "hive_checksum_u32_hex"): "checksum",
    ("windows_registry", "checksum_u32_hex"): "checksum",
    ("windows_registry", "hive_checksum_valid"): "checksum",
    ("windows_registry", "checksum_valid"): "checksum",
    ("ntuser", "hive_root_name"): "root_name",
    ("ntuser", "root_key_name"): "root_name",
    ("ntuser", "root_name"): "root_name",
    ("ntuser", "root_nk_name"): "root_name",
    ("ntuser", "root_cell_key_name"): "root_name",
    ("ntuser", "hive_root_key_name"): "root_name",
    ("ntuser", "hive_file_name"): "file_name",
    ("ntuser", "base_block_file_name"): "file_name",
    ("ntuser", "file_name"): "file_name",
    ("ntuser", "hive_name"): "file_name",
    ("ntuser", "hive_last_written_utc"): "last_written",
    ("ntuser", "hive_last_written_time_utc"): "last_written",
    ("ntuser", "base_block_last_written_utc"): "last_written",
    ("ntuser", "root_last_written_utc"): "last_written",
    ("ntuser", "root_key_last_written_utc"): "last_written",
    ("ntuser", "hive_root_last_written_utc"): "last_written",
    ("ntuser", "hive_primary_sequence_number"): "sequence",
    ("ntuser", "hive_secondary_sequence_number"): "sequence",
    ("ntuser", "hive_sequence_numbers_match"): "sequence",
    ("ntuser", "sequence_numbers_match"): "sequence",
    ("ntuser", "hive_version"): "version",
    ("ntuser", "version"): "version",
    ("ntuser", "format_version"): "version",
    ("ntuser", "hive_major_version"): "version",
    ("ntuser", "hive_minor_version"): "version",
    ("ntuser", "hive_file_type"): "header_u32",
    ("ntuser", "hive_root_subkey_count"): "root_list",
    ("ntuser", "root_subkey_count"): "root_list",
    ("ntuser", "root_key_subkey_count"): "root_list",
    ("ntuser", "hive_root_value_count"): "root_list",
    ("ntuser", "root_value_count"): "root_list",
    ("ntuser", "root_key_value_count"): "root_list",
    ("ntuser", "hive_root_value_names"): "root_list",
    ("ntuser", "root_value_names"): "root_list",
    ("ntuser", "root_key_value_names"): "root_list",
    ("ntuser", "hive_root_subkey_names"): "root_list",
    ("ntuser", "root_subkey_names"): "root_list",
    ("ntuser", "root_key_subkey_names"): "root_list",
    ("ntuser", "hive_checksum_u32_hex"): "checksum",
    ("ntuser", "hive_checksum_valid"): "checksum",
    ("regf", "hive_root_name"): "root_name",
    ("regf", "root_name"): "root_name",
    ("regf", "hive_root_key_name"): "root_name",
    ("regf", "hive_last_written_utc"): "last_written",
    ("regf", "hive_last_written_time_utc"): "last_written",
    ("regf", "base_block_last_written_utc"): "last_written",
    ("regf", "root_last_written_utc"): "last_written",
    ("regf", "hive_root_last_written_utc"): "last_written",
    ("regf", "hive_primary_sequence_number"): "sequence",
    ("regf", "hive_secondary_sequence_number"): "sequence",
    ("regf", "hive_sequence_numbers_match"): "sequence",
    ("regf", "hive_major_version"): "version",
    ("regf", "hive_minor_version"): "version",
    ("regf", "hive_file_type"): "header_u32",
    ("regf", "hive_root_subkey_count"): "root_list",
    ("regf", "hive_root_value_count"): "root_list",
    ("regf", "hive_root_value_names"): "root_list",
    ("regf", "root_value_names"): "root_list",
    ("regf", "root_key_value_names"): "root_list",
    ("regf", "hive_root_subkey_names"): "root_list",
    ("regf", "root_subkey_names"): "root_list",
    ("regf", "root_key_subkey_names"): "root_list",
    ("regf", "hive_checksum_u32_hex"): "checksum",
    ("regf", "hive_checksum_valid"): "checksum",
}


def _hdr(b):
    """(base block dict, raw bytes) or (None, None) when not regf."""
    h = base_block(b)
    return (h, bytes(b[:512])) if h else (None, None)


def _flags(b, off):
    p = 0x1000 + off + 4
    return struct.unpack_from("<H", b, p + 2)[0] if p + 4 <= len(b) else 0


def _root(b, h):
    """The root nk dict (regf._nk shape): the base-block root cell if it is a HIVE_ENTRY nk, else the first one found
    scanning the hbin area, or None."""
    k = _nk(b, h["root"]) if h["root"] < len(b) else None
    if k is not None and _flags(b, h["root"]) & 0x04:
        return k
    pos = b.find(b"nk", 0x1020)
    while pos != -1:
        off = pos - 4 - 0x1000
        if off % 8 == 0 and _flags(b, off) & 0x04:
            k = _nk(b, off)
            if k is not None:
                return k
        pos = b.find(b"nk", pos + 1)
    return None


def _filetime(v):
    # FILETIME -> ISO-8601 UTC, seconds precision (see module doc); zero -> "none".
    if not v:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=v // 10)
    except (OverflowError, ValueError):
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _guard(fn):
    def run(data, ctx):
        if data is None:
            return None
        try:
            data = bytes(data)
            h, _ = _hdr(data)
            if h is None:
                return "none"
            return fn(data, h, ctx.get("field") or "")
        except Exception:  # noqa: BLE001 - truncated / malformed hive
            return None
    run.__name__ = fn.__name__
    return run


@_guard
def root_name(b, h, f):
    """<fmt>.hive_root_name / root_key_name / root_name: the root nk's name."""
    k = _root(b, h)
    return k["name"] if k else None


@_guard
def file_name(b, h, f):
    """<fmt>.hive_file_name / base_block_file_name: UTF-16LE @0x30 up to the first NUL."""
    return h["name"] or "none"


@_guard
def last_written(b, h, f):
    """<fmt>.hive_last_written_utc (base block) / root_last_written_utc (root nk)."""
    if "root" in f:
        k = _root(b, h)
        return _filetime(k["ts"]) if k else None
    return _filetime(h["ts"])


@_guard
def sequence(b, h, f):
    """<fmt>.hive_primary/secondary_sequence_number, hive_sequence_numbers_match."""
    if "match" in f:
        return h["seq1"] == h["seq2"]
    return h["seq1"] if "primary" in f else h["seq2"]


@_guard
def version(b, h, f):
    """<fmt>.hive_version ("1.3"), *_major_version / *_minor_version (int)."""
    if "major" in f:
        return h["major"]
    if "minor" in f:
        return h["minor"]
    return "%d.%d" % (h["major"], h["minor"])


@_guard
def header_u32(b, h, f):
    """<fmt>.hive_file_type (u32 @28), hive_bins_data_size_bytes (u32 @40)."""
    return struct.unpack_from("<I", b, 40 if "bins" in f else 28)[0]


@_guard
def root_list(b, h, f):
    """<fmt>.hive_root_{subkey,value}_{count,names}."""
    k = _root(b, h)
    if k is None:
        return None
    if f.endswith("_count"):
        return k["nsub"] if "subkey" in f else k["nval"]
    if "subkey" in f:
        return sorted(c["name"] for c in _subkeys(b, k))
    return sorted(n for n, _, _ in _values(b, k))


@_guard
def checksum(b, h, f):
    """<fmt>.hive_checksum_u32_hex (calculated), hive_checksum_valid."""
    c = 0
    for (d,) in struct.iter_unpack("<I", b[:508]):
        c ^= d
    c = {0: 1, 0xFFFFFFFF: 0xFFFFFFFE}.get(c, c)
    if f.endswith("_valid"):
        return c == struct.unpack_from("<I", b, 508)[0]
    return Hex(c, 8)
