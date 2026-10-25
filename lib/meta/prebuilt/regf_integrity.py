"""Registry hive INTEGRITY fields (prebuilt, SPECULATIVE; the D24 "truncated / shortened" flavor applied to regf):
dirty hive (sequence mismatch), base-block checksum, hbin walk vs declared size, transaction logs (.LOG1/.LOG2 HvLE,
legacy .LOG DIRT). fmt regf (new fields only -- prebuilt/regf.py owns the base-block/key fields under `regf`) plus
the format aliases registry / hive / ntuser / reg (base-block fields included there). All little-endian.

Base block (libregf spec / python-registry REGFBlock): "regf" @0, primary sequence u32 @4, secondary sequence u32 @8,
last written FILETIME u64 @12, major u32 @20, minor u32 @24, file type u32 @28 (0 primary, 1 transaction log
(old), 2 volatile/alternate, 6 transaction log (new)), file format u32 @32, root cell offset u32 @36, hive bins data
size u32 @40, clustering factor u32 @44, file name 64 B UTF-16LE @48, checksum u32 @0x1FC = XOR of the 127 dwords
0x000..0x1F8 (0 -> 1, 0xFFFFFFFF -> 0xFFFFFFFE).
- is_dirty: primary != secondary sequence. checksum_u32_hex: the STORED value; calculated_checksum_u32_hex: ours.
- hbin walk (primary only): from 0x1000, while the block carries "hbin", its size u32 @8 is a non-zero multiple of
  0x1000, and the walk stays below 0x1000 + data size; a last hbin whose header is present but whose body runs past
  EOF is still counted (python-registry's hbins() does the same). hbin_walk_size_bytes = sum of the declared sizes.
  truncated: len(file) < 0x1000 + hive bins data size. Log files: hbin/truncated fields -> "none".
- Transaction log (base block file type 1/6, 512-byte base block): at 512 either "HvLE" log entries (size u32 @4,
  flags u32 @8, sequence u32 @12, hive bins data size u32 @16, dirty pages count u32 @20, hash-1 u64 @24, hash-2 u64
  @32, then count x (offset u32, size u32) refs, then the pages) walked by size until a non-HvLE block (regipy
  recovery semantics), or a "DIRT" dirty vector of (data size / 4096) bytes, one bit per 512-byte sector.
  log_entry_count, log_first/last_sequence (file order), dirty_page_count (HvLE: sum of all entries' counts; DIRT:
  set bits = sectors). Marvin32 hash-1/hash-2 are NOT verified (no independent oracle).
- last_written_time_utc: FILETIME (100 ns since 1601) -> 'YYYY-MM-DDTHH:MM:SSZ', sub-seconds dropped (regf.py's
  house spelling); zero -> "none".
Not "regf" (e.g. a carved "hbin" block, a Win9x CREG hive) -> "none"; regf shorter than 512 bytes -> None."""
import datetime
import struct

from ..spell import Hex

FIELDS = {
    ("regf", "is_dirty"): "integrity_value",
    ("regf", "dirty"): "integrity_value",
    ("regf", "is_dirty_hive"): "integrity_value",
    ("regf", "sequence_numbers_match"): "integrity_value",
    ("regf", "sequence_mismatch"): "integrity_value",
    ("regf", "checksum_u32_hex"): "integrity_value",
    ("regf", "header_checksum_u32_hex"): "integrity_value",
    ("regf", "base_block_checksum_u32_hex"): "integrity_value",
    ("regf", "stored_checksum_u32_hex"): "integrity_value",
    ("regf", "calculated_checksum_u32_hex"): "integrity_value",
    ("regf", "computed_checksum_u32_hex"): "integrity_value",
    ("regf", "checksum_valid"): "integrity_value",
    ("regf", "header_checksum_valid"): "integrity_value",
    ("regf", "base_block_checksum_valid"): "integrity_value",
    ("regf", "is_checksum_valid"): "integrity_value",
    ("regf", "hive_bins_data_size_bytes"): "integrity_value",
    ("regf", "hive_bins_data_size"): "integrity_value",
    ("regf", "hbins_data_size_bytes"): "integrity_value",
    ("regf", "hbins_size_bytes"): "integrity_value",
    ("regf", "hbin_count"): "integrity_value",
    ("regf", "number_of_hbins"): "integrity_value",
    ("regf", "hive_bin_count"): "integrity_value",
    ("regf", "hbin_walk_size_bytes"): "integrity_value",
    ("regf", "hbin_total_size_bytes"): "integrity_value",
    ("regf", "hbin_walk_matches"): "integrity_value",
    ("regf", "hbins_size_matches"): "integrity_value",
    ("regf", "truncated"): "integrity_value",
    ("regf", "is_truncated"): "integrity_value",
    ("regf", "expected_file_size_bytes"): "integrity_value",
    ("regf", "missing_bytes"): "integrity_value",
    ("regf", "embedded_file_name"): "integrity_value",
    ("regf", "base_block_file_type"): "integrity_value",
    ("regf", "file_type"): "integrity_value",
    ("regf", "file_type_name"): "integrity_value",
    ("regf", "is_transaction_log"): "integrity_value",
    ("regf", "file_format"): "integrity_value",
    ("regf", "clustering_factor"): "integrity_value",
    ("regf", "log_format"): "integrity_value",
    ("regf", "log_entry_count"): "integrity_value",
    ("regf", "hvle_entry_count"): "integrity_value",
    ("regf", "number_of_log_entries"): "integrity_value",
    ("regf", "log_first_sequence"): "integrity_value",
    ("regf", "log_first_sequence_number"): "integrity_value",
    ("regf", "first_log_sequence_number"): "integrity_value",
    ("regf", "log_last_sequence"): "integrity_value",
    ("regf", "log_last_sequence_number"): "integrity_value",
    ("regf", "last_log_sequence_number"): "integrity_value",
    ("regf", "log_sequence_numbers"): "integrity_value",
    ("regf", "dirty_page_count"): "integrity_value",
    ("regf", "log_dirty_page_count"): "integrity_value",
    ("regf", "dirty_pages_count"): "integrity_value",
    # format aliases: every field above plus the base-block ones regf.py answers under `regf`
    ("registry", "is_dirty"): "integrity_value",
    ("registry", "checksum_u32_hex"): "integrity_value",
    ("registry", "checksum_valid"): "integrity_value",
    ("registry", "hive_bins_data_size_bytes"): "integrity_value",
    ("registry", "hbin_count"): "integrity_value",
    ("registry", "hbin_walk_size_bytes"): "integrity_value",
    ("registry", "truncated"): "integrity_value",
    ("registry", "embedded_file_name"): "integrity_value",
    ("registry", "file_type"): "integrity_value",
    ("registry", "log_entry_count"): "integrity_value",
    ("registry", "log_first_sequence"): "integrity_value",
    ("registry", "log_last_sequence"): "integrity_value",
    ("registry", "dirty_page_count"): "integrity_value",
    ("registry", "primary_sequence_number"): "integrity_value",
    ("registry", "secondary_sequence_number"): "integrity_value",
    ("registry", "last_written_time_utc"): "integrity_value",
    ("registry", "major_version"): "integrity_value",
    ("registry", "minor_version"): "integrity_value",
    ("hive", "is_dirty"): "integrity_value",
    ("hive", "checksum_u32_hex"): "integrity_value",
    ("hive", "checksum_valid"): "integrity_value",
    ("hive", "hive_bins_data_size_bytes"): "integrity_value",
    ("hive", "hbin_count"): "integrity_value",
    ("hive", "hbin_walk_size_bytes"): "integrity_value",
    ("hive", "truncated"): "integrity_value",
    ("hive", "embedded_file_name"): "integrity_value",
    ("hive", "file_type"): "integrity_value",
    ("hive", "log_entry_count"): "integrity_value",
    ("hive", "log_first_sequence"): "integrity_value",
    ("hive", "log_last_sequence"): "integrity_value",
    ("hive", "dirty_page_count"): "integrity_value",
    ("hive", "primary_sequence_number"): "integrity_value",
    ("hive", "secondary_sequence_number"): "integrity_value",
    ("hive", "last_written_time_utc"): "integrity_value",
    ("hive", "major_version"): "integrity_value",
    ("hive", "minor_version"): "integrity_value",
    ("ntuser", "is_dirty"): "integrity_value",
    ("ntuser", "checksum_u32_hex"): "integrity_value",
    ("ntuser", "checksum_valid"): "integrity_value",
    ("ntuser", "hive_bins_data_size_bytes"): "integrity_value",
    ("ntuser", "hbin_count"): "integrity_value",
    ("ntuser", "hbin_walk_size_bytes"): "integrity_value",
    ("ntuser", "truncated"): "integrity_value",
    ("ntuser", "embedded_file_name"): "integrity_value",
    ("ntuser", "file_type"): "integrity_value",
    ("ntuser", "log_entry_count"): "integrity_value",
    ("ntuser", "log_first_sequence"): "integrity_value",
    ("ntuser", "log_last_sequence"): "integrity_value",
    ("ntuser", "dirty_page_count"): "integrity_value",
    ("ntuser", "primary_sequence_number"): "integrity_value",
    ("ntuser", "secondary_sequence_number"): "integrity_value",
    ("ntuser", "last_written_time_utc"): "integrity_value",
    ("ntuser", "major_version"): "integrity_value",
    ("ntuser", "minor_version"): "integrity_value",
    ("reg", "is_dirty"): "integrity_value",
    ("reg", "checksum_u32_hex"): "integrity_value",
    ("reg", "checksum_valid"): "integrity_value",
    ("reg", "hive_bins_data_size_bytes"): "integrity_value",
    ("reg", "hbin_count"): "integrity_value",
    ("reg", "hbin_walk_size_bytes"): "integrity_value",
    ("reg", "truncated"): "integrity_value",
    ("reg", "embedded_file_name"): "integrity_value",
    ("reg", "file_type"): "integrity_value",
    ("reg", "log_entry_count"): "integrity_value",
    ("reg", "log_first_sequence"): "integrity_value",
    ("reg", "log_last_sequence"): "integrity_value",
    ("reg", "dirty_page_count"): "integrity_value",
    ("reg", "primary_sequence_number"): "integrity_value",
    ("reg", "secondary_sequence_number"): "integrity_value",
    ("reg", "last_written_time_utc"): "integrity_value",
    ("reg", "major_version"): "integrity_value",
    ("reg", "minor_version"): "integrity_value",
}

_FILE_TYPES = {0: "primary", 1: "log_old_1", 2: "log_old_2", 6: "log_new"}   # python-registry FileType names


def _filetime(v):
    if not v:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=v // 10)
    except (OverflowError, ValueError):
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _checksum(b):
    x = 0
    for d in struct.unpack_from("<127I", b, 0):
        x ^= d
    return 1 if x == 0 else 0xFFFFFFFE if x == 0xFFFFFFFF else x


def _hbins(b, size):
    """(count, summed declared size) of the hbin walk from 0x1000."""
    off, end, n, tot = 0x1000, 0x1000 + size, 0, 0
    while off + 12 <= len(b) and off < end and bytes(b[off:off + 4]) == b"hbin":
        sz, = struct.unpack_from("<I", b, off + 8)
        if sz == 0 or sz % 0x1000:
            break
        n, tot, off = n + 1, tot + sz, off + sz
    return n, tot


def _log(b, size):
    """{'format', 'seqs', 'dirty'} of a transaction log's body at 512, or None (no HvLE / DIRT)."""
    sig = bytes(b[512:516])
    if sig == b"HvLE":
        off, seqs, dirty = 512, [], 0
        while off + 40 <= len(b) and bytes(b[off:off + 4]) == b"HvLE":
            ln, _flags, seq, _hsz, cnt = struct.unpack_from("<IIIII", b, off + 4)
            seqs.append(seq)
            dirty += cnt
            if ln < 40:
                break
            off += ln
        return {"format": "HvLE", "seqs": seqs, "dirty": dirty}
    if sig == b"DIRT":
        vec = bytes(b[516:516 + size // 4096])
        return {"format": "DIRT", "seqs": [], "dirty": sum(bin(c).count("1") for c in vec)}
    return None


def integrity_value(data, ctx):
    """<regf|registry|hive|ntuser|reg>.<integrity field> (see module doc)."""
    if data is None:
        return None
    try:
        b = bytes(data)
        if b[:4] != b"regf":
            return "none"
        if len(b) < 512:
            return None
        s1, s2, ts, major, minor, ftype, ffmt, _root, size, clus = struct.unpack_from("<IIQIIIIIII", b, 4)
        stored, = struct.unpack_from("<I", b, 0x1FC)
        f = ctx.get("field") or ""
        is_log = ftype in (1, 2, 6)
        if f == "primary_sequence_number":
            return s1
        if f == "secondary_sequence_number":
            return s2
        if f.startswith("last_written_time"):
            return _filetime(ts)
        if f == "major_version":
            return major
        if f == "minor_version":
            return minor
        if f in ("is_dirty", "dirty", "is_dirty_hive", "sequence_mismatch"):
            return s1 != s2
        if f == "sequence_numbers_match":
            return s1 == s2
        if f.startswith(("calculated_checksum", "computed_checksum")):
            return Hex(_checksum(b), 8)
        if f.endswith("checksum_u32_hex"):
            return Hex(stored, 8)
        if "checksum_valid" in f:
            return _checksum(b) == stored
        if f in ("hive_bins_data_size_bytes", "hive_bins_data_size", "hbins_data_size_bytes", "hbins_size_bytes"):
            return size
        if f in ("embedded_file_name", "file_name", "hive_file_name"):
            return b[48:112].decode("utf-16-le", "replace").split("\x00", 1)[0].strip() or "none"
        if f in ("file_type", "base_block_file_type"):
            return ftype
        if f == "file_type_name":
            return _FILE_TYPES.get(ftype, "unknown")
        if f == "is_transaction_log":
            return is_log
        if f == "file_format":
            return ffmt
        if f == "clustering_factor":
            return clus
        if f.startswith(("hbin", "number_of_hbins", "hive_bin_count")) or f in (
                "truncated", "is_truncated", "expected_file_size_bytes", "missing_bytes"):
            if is_log:
                return "none"
            if f in ("truncated", "is_truncated"):
                return len(b) < 0x1000 + size
            if f == "expected_file_size_bytes":
                return 0x1000 + size
            if f == "missing_bytes":
                return max(0, 0x1000 + size - len(b))
            n, tot = _hbins(b, size)
            if f.endswith("_matches"):
                return tot == size
            return tot if f.endswith("size_bytes") else n
        if "log" in f or "dirty_page" in f or "hvle" in f:
            lg = _log(b, size) if is_log else None
            if lg is None:
                return "none"
            if f == "log_format":
                return lg["format"]
            if "dirty_page" in f:
                return lg["dirty"]
            if lg["format"] != "HvLE":
                return "none"
            if f in ("log_entry_count", "hvle_entry_count", "number_of_log_entries"):
                return len(lg["seqs"])
            if f == "log_sequence_numbers":
                return lg["seqs"]
            if not lg["seqs"]:
                return "none"
            return lg["seqs"][0] if "first" in f else lg["seqs"][-1]
    except Exception:
        return None
    return None
