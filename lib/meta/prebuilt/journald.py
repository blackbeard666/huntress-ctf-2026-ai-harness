"""systemd journal files (*.journal / *.journal~) -- the HEADER (prebuilt, SPECULATIVE: never GM-asked).
fmt tokens: journald, systemd_journal, journal (the last only for names the SQLite rollback-journal module does not
own -- journal.record_count / page_count / ... stay with it).

Layout per systemd docs/JOURNAL_FILE_FORMAT.md (all little-endian):
  @0 signature "LPKSHHRH"  @8 compatible_flags u32  @12 incompatible_flags u32  @16 state u8 (0 offline, 1 online,
  2 archived)  @24 file_id  @40 machine_id  @56 tail_entry_boot_id (the doc's old name: boot_id)  @72 seqnum_id
  (16-byte ids -> 32 lowercase hex, the journalctl --header spelling; machine_id = the HOST identity)
  @88 header_size u64  @96 arena_size  @104/112 data_hash_table offset/size  @120/128 field_hash_table offset/size
  @136 tail_object_offset  @144 n_objects  @152 n_entries  @160 tail_entry_seqnum  @168 head_entry_seqnum
  @176 entry_array_offset  @184 head_entry_realtime  @192 tail_entry_realtime  @200 tail_entry_monotonic
  -- added later, so gated on header_size: @208 n_data  @216 n_fields  @224 n_tags  @232 n_entry_arrays
  @240 data_hash_chain_depth  @248 field_hash_chain_depth  @256 tail_entry_array_offset u32
  @260 tail_entry_array_n_entries u32  @264 tail_entry_offset u64.
compatible flags: bit0 SEALED, bit1 TAIL_ENTRY_BOOT_ID, bit2 SEALED_CONTINUOUS. incompatible: bit0 COMPRESSED-XZ,
bit1 COMPRESSED-LZ4, bit2 KEYED-HASH, bit3 COMPRESSED-ZSTD, bit4 COMPACT (names as journalctl --header prints them).
Timestamps: realtime is CLOCK_REALTIME microseconds since the unix epoch; *_utc renders it like the rest of the lane
("YYYY-MM-DDTHH:MM:SSZ", seconds truncated); the bare *_realtime names give the stored integer microseconds;
tail_entry_monotonic is CLOCK_MONOTONIC microseconds (int). Only the header is read, so a file cut after the header
still answers. Not a journal / field absent (old short header, empty file with zero timestamps) -> "none"."""
import datetime
import struct

from ..spell import Hex

_SIG = b"LPKSHHRH"
_STATES = {0: "offline", 1: "online", 2: "archived"}
_COMPAT = ((0, "SEALED"), (1, "TAIL_ENTRY_BOOT_ID"), (2, "SEALED_CONTINUOUS"))
_INCOMPAT = ((0, "COMPRESSED-XZ"), (1, "COMPRESSED-LZ4"), (2, "KEYED-HASH"), (3, "COMPRESSED-ZSTD"), (4, "COMPACT"))
# u64 counters: name -> offset (the end offset gates them on header_size)
_U64 = {"header_size": 88, "arena_size": 96, "data_hash_table_offset": 104, "data_hash_table_size": 112,
        "field_hash_table_offset": 120, "field_hash_table_size": 128, "tail_object_offset": 136, "n_objects": 144,
        "n_entries": 152, "tail_entry_seqnum": 160, "head_entry_seqnum": 168, "entry_array_offset": 176,
        "head_entry_realtime": 184, "tail_entry_realtime": 192, "tail_entry_monotonic": 200, "n_data": 208,
        "n_fields": 216, "n_tags": 224, "n_entry_arrays": 232, "data_hash_chain_depth": 240,
        "field_hash_chain_depth": 248, "tail_entry_offset": 264}
_U32 = {"tail_entry_array_offset": 256, "tail_entry_array_n_entries": 260}
_IDS = {"file_id": 24, "machine_id": 40, "tail_entry_boot_id": 56, "seqnum_id": 72}

# field name -> canonical key
_ALIAS = {
    "signature": "signature", "magic": "signature",
    "compatible_flags_u32_hex": "compatible_flags", "compatible_flags": "compatible_flags",
    "incompatible_flags_u32_hex": "incompatible_flags", "incompatible_flags": "incompatible_flags",
    "compatible_flag_names": "compatible_names", "incompatible_flag_names": "incompatible_names",
    "compression": "compression", "compression_algorithm": "compression",
    "is_compressed": "is_compressed", "compressed": "is_compressed",
    "is_compact": "is_compact", "compact": "is_compact", "keyed_hash": "keyed_hash", "has_keyed_hash": "keyed_hash",
    "is_sealed": "is_sealed", "sealed": "is_sealed",
    "state": "state", "file_state": "state", "state_u8": "state_u8",
    "file_id": "file_id", "machine_id": "machine_id", "host": "machine_id", "host_id": "machine_id",
    "header_machine_id": "machine_id",
    "tail_entry_boot_id": "tail_entry_boot_id", "boot_id": "tail_entry_boot_id",
    "seqnum_id": "seqnum_id", "sequential_number_id": "seqnum_id",
    "header_size": "header_size", "arena_size": "arena_size",
    "data_hash_table_offset": "data_hash_table_offset", "data_hash_table_size": "data_hash_table_size",
    "field_hash_table_offset": "field_hash_table_offset", "field_hash_table_size": "field_hash_table_size",
    "tail_object_offset": "tail_object_offset", "entry_array_offset": "entry_array_offset",
    "n_objects": "n_objects", "object_count": "n_objects", "objects": "n_objects",
    "n_entries": "n_entries", "entry_count": "n_entries", "entry_objects": "n_entries",
    "number_of_entries": "n_entries", "num_entries": "n_entries",
    "head_entry_seqnum": "head_entry_seqnum", "first_seqnum": "head_entry_seqnum",
    "head_sequential_number": "head_entry_seqnum",
    "tail_entry_seqnum": "tail_entry_seqnum", "last_seqnum": "tail_entry_seqnum",
    "tail_sequential_number": "tail_entry_seqnum",
    "head_entry_realtime": "head_entry_realtime", "head_entry_realtime_us": "head_entry_realtime",
    "tail_entry_realtime": "tail_entry_realtime", "tail_entry_realtime_us": "tail_entry_realtime",
    "head_entry_realtime_utc": "head_utc", "head_realtime_timestamp_utc": "head_utc",
    "first_entry_time_utc": "head_utc", "first_entry_utc": "head_utc", "earliest_entry_time_utc": "head_utc",
    "tail_entry_realtime_utc": "tail_utc", "tail_realtime_timestamp_utc": "tail_utc",
    "last_entry_time_utc": "tail_utc", "last_entry_utc": "tail_utc", "latest_entry_time_utc": "tail_utc",
    "tail_entry_monotonic": "tail_entry_monotonic", "tail_entry_monotonic_us": "tail_entry_monotonic",
    "n_data": "n_data", "data_objects": "n_data", "data_object_count": "n_data",
    "n_fields": "n_fields", "field_objects": "n_fields", "field_object_count": "n_fields",
    "n_tags": "n_tags", "tag_objects": "n_tags",
    "n_entry_arrays": "n_entry_arrays", "entry_array_objects": "n_entry_arrays",
    "data_hash_chain_depth": "data_hash_chain_depth", "field_hash_chain_depth": "field_hash_chain_depth",
    "tail_entry_array_offset": "tail_entry_array_offset",
    "tail_entry_array_n_entries": "tail_entry_array_n_entries", "tail_entry_offset": "tail_entry_offset",
}
# names the SQLite rollback-journal module already owns under fmt "journal"
_JOURNAL_TAKEN = {"page_count", "page_size", "record_count", "sector_size"}

FIELDS = {
    ("journald", "signature"): "journald_value", ("journald", "magic"): "journald_value",
    ("journald", "compatible_flags_u32_hex"): "journald_value", ("journald", "compatible_flags"): "journald_value",
    ("journald", "incompatible_flags_u32_hex"): "journald_value", ("journald", "incompatible_flags"): "journald_value",
    ("journald", "compatible_flag_names"): "journald_value", ("journald", "incompatible_flag_names"): "journald_value",
    ("journald", "compression"): "journald_value", ("journald", "compression_algorithm"): "journald_value",
    ("journald", "is_compressed"): "journald_value", ("journald", "compressed"): "journald_value",
    ("journald", "is_compact"): "journald_value", ("journald", "compact"): "journald_value",
    ("journald", "keyed_hash"): "journald_value", ("journald", "has_keyed_hash"): "journald_value",
    ("journald", "is_sealed"): "journald_value", ("journald", "sealed"): "journald_value",
    ("journald", "state"): "journald_value", ("journald", "file_state"): "journald_value",
    ("journald", "state_u8"): "journald_value",
    ("journald", "file_id"): "journald_value", ("journald", "machine_id"): "journald_value",
    ("journald", "host"): "journald_value", ("journald", "host_id"): "journald_value",
    ("journald", "header_machine_id"): "journald_value",
    ("journald", "tail_entry_boot_id"): "journald_value", ("journald", "boot_id"): "journald_value",
    ("journald", "seqnum_id"): "journald_value", ("journald", "sequential_number_id"): "journald_value",
    ("journald", "header_size"): "journald_value", ("journald", "arena_size"): "journald_value",
    ("journald", "data_hash_table_offset"): "journald_value", ("journald", "data_hash_table_size"): "journald_value",
    ("journald", "field_hash_table_offset"): "journald_value",
    ("journald", "field_hash_table_size"): "journald_value",
    ("journald", "tail_object_offset"): "journald_value", ("journald", "entry_array_offset"): "journald_value",
    ("journald", "n_objects"): "journald_value", ("journald", "object_count"): "journald_value",
    ("journald", "objects"): "journald_value",
    ("journald", "n_entries"): "journald_value", ("journald", "entry_count"): "journald_value",
    ("journald", "entry_objects"): "journald_value", ("journald", "number_of_entries"): "journald_value",
    ("journald", "num_entries"): "journald_value",
    ("journald", "head_entry_seqnum"): "journald_value", ("journald", "first_seqnum"): "journald_value",
    ("journald", "head_sequential_number"): "journald_value",
    ("journald", "tail_entry_seqnum"): "journald_value", ("journald", "last_seqnum"): "journald_value",
    ("journald", "tail_sequential_number"): "journald_value",
    ("journald", "head_entry_realtime"): "journald_value", ("journald", "head_entry_realtime_us"): "journald_value",
    ("journald", "tail_entry_realtime"): "journald_value", ("journald", "tail_entry_realtime_us"): "journald_value",
    ("journald", "head_entry_realtime_utc"): "journald_value",
    ("journald", "head_realtime_timestamp_utc"): "journald_value",
    ("journald", "first_entry_time_utc"): "journald_value", ("journald", "first_entry_utc"): "journald_value",
    ("journald", "earliest_entry_time_utc"): "journald_value",
    ("journald", "tail_entry_realtime_utc"): "journald_value",
    ("journald", "tail_realtime_timestamp_utc"): "journald_value",
    ("journald", "last_entry_time_utc"): "journald_value", ("journald", "last_entry_utc"): "journald_value",
    ("journald", "latest_entry_time_utc"): "journald_value",
    ("journald", "tail_entry_monotonic"): "journald_value", ("journald", "tail_entry_monotonic_us"): "journald_value",
    ("journald", "n_data"): "journald_value", ("journald", "data_objects"): "journald_value",
    ("journald", "data_object_count"): "journald_value",
    ("journald", "n_fields"): "journald_value", ("journald", "field_objects"): "journald_value",
    ("journald", "field_object_count"): "journald_value",
    ("journald", "n_tags"): "journald_value", ("journald", "tag_objects"): "journald_value",
    ("journald", "n_entry_arrays"): "journald_value", ("journald", "entry_array_objects"): "journald_value",
    ("journald", "data_hash_chain_depth"): "journald_value", ("journald", "field_hash_chain_depth"): "journald_value",
    ("journald", "tail_entry_array_offset"): "journald_value",
    ("journald", "tail_entry_array_n_entries"): "journald_value", ("journald", "tail_entry_offset"): "journald_value",

    ("systemd_journal", "signature"): "journald_value",
    ("systemd_journal", "compatible_flags_u32_hex"): "journald_value",
    ("systemd_journal", "incompatible_flags_u32_hex"): "journald_value",
    ("systemd_journal", "incompatible_flag_names"): "journald_value",
    ("systemd_journal", "compression"): "journald_value", ("systemd_journal", "is_compact"): "journald_value",
    ("systemd_journal", "state"): "journald_value",
    ("systemd_journal", "file_id"): "journald_value", ("systemd_journal", "machine_id"): "journald_value",
    ("systemd_journal", "host"): "journald_value",
    ("systemd_journal", "tail_entry_boot_id"): "journald_value", ("systemd_journal", "boot_id"): "journald_value",
    ("systemd_journal", "seqnum_id"): "journald_value",
    ("systemd_journal", "header_size"): "journald_value", ("systemd_journal", "arena_size"): "journald_value",
    ("systemd_journal", "n_objects"): "journald_value", ("systemd_journal", "object_count"): "journald_value",
    ("systemd_journal", "n_entries"): "journald_value", ("systemd_journal", "entry_count"): "journald_value",
    ("systemd_journal", "head_entry_seqnum"): "journald_value",
    ("systemd_journal", "tail_entry_seqnum"): "journald_value",
    ("systemd_journal", "head_entry_realtime"): "journald_value",
    ("systemd_journal", "tail_entry_realtime"): "journald_value",
    ("systemd_journal", "head_entry_realtime_utc"): "journald_value",
    ("systemd_journal", "tail_entry_realtime_utc"): "journald_value",
    ("systemd_journal", "first_entry_time_utc"): "journald_value",
    ("systemd_journal", "last_entry_time_utc"): "journald_value",
    ("systemd_journal", "tail_entry_monotonic"): "journald_value",
    ("systemd_journal", "n_data"): "journald_value", ("systemd_journal", "n_fields"): "journald_value",
    ("systemd_journal", "n_tags"): "journald_value", ("systemd_journal", "n_entry_arrays"): "journald_value",

    ("journal", "signature"): "journald_value",
    ("journal", "compatible_flags_u32_hex"): "journald_value",
    ("journal", "incompatible_flags_u32_hex"): "journald_value",
    ("journal", "incompatible_flag_names"): "journald_value",
    ("journal", "compression"): "journald_value", ("journal", "is_compact"): "journald_value",
    ("journal", "state"): "journald_value",
    ("journal", "file_id"): "journald_value", ("journal", "machine_id"): "journald_value",
    ("journal", "tail_entry_boot_id"): "journald_value", ("journal", "boot_id"): "journald_value",
    ("journal", "seqnum_id"): "journald_value",
    ("journal", "header_size"): "journald_value", ("journal", "arena_size"): "journald_value",
    ("journal", "n_objects"): "journald_value", ("journal", "object_count"): "journald_value",
    ("journal", "n_entries"): "journald_value", ("journal", "entry_count"): "journald_value",
    ("journal", "head_entry_seqnum"): "journald_value", ("journal", "tail_entry_seqnum"): "journald_value",
    ("journal", "head_entry_realtime"): "journald_value", ("journal", "tail_entry_realtime"): "journald_value",
    ("journal", "head_entry_realtime_utc"): "journald_value",
    ("journal", "tail_entry_realtime_utc"): "journald_value",
    ("journal", "first_entry_time_utc"): "journald_value", ("journal", "last_entry_time_utc"): "journald_value",
    ("journal", "tail_entry_monotonic"): "journald_value",
    ("journal", "n_data"): "journald_value", ("journal", "n_fields"): "journald_value",
    ("journal", "n_entry_arrays"): "journald_value",
}


def _utc(us):
    if not us:
        return None
    try:
        return datetime.datetime.fromtimestamp(us // 1000000, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, OSError, ValueError):
        return None


def header(b):
    """{canonical name: raw value} of a journal file header, or None when `b` is not one."""
    if not isinstance(b, (bytes, bytearray)) or len(b) < 96 or bytes(b[:8]) != _SIG:
        return None
    hs = struct.unpack_from("<Q", b, 88)[0]
    if hs < 96:
        return None
    lim = min(hs, len(b))
    compat, incompat, state = struct.unpack_from("<IIB", b, 8)
    h = {"signature": _SIG.decode(), "compatible_flags": Hex(compat, 8), "incompatible_flags": Hex(incompat, 8),
         "compatible_names": [n for bit, n in _COMPAT if compat >> bit & 1],
         "incompatible_names": [n for bit, n in _INCOMPAT if incompat >> bit & 1],
         "is_compressed": bool(incompat & 0b1011), "is_compact": bool(incompat & 16),
         "keyed_hash": bool(incompat & 4), "is_sealed": bool(compat & 1),
         "state_u8": state, "state": _STATES.get(state)}
    comp = [n for bit, n in ((0, "xz"), (1, "lz4"), (3, "zstd")) if incompat >> bit & 1]
    h["compression"] = comp[0] if len(comp) == 1 else ("none" if not comp else None)
    for k, o in _IDS.items():
        h[k] = bytes(b[o:o + 16]).hex()
    for k, o in _U64.items():
        if o + 8 <= lim:
            h[k] = struct.unpack_from("<Q", b, o)[0]
    for k, o in _U32.items():
        if o + 4 <= lim:
            h[k] = struct.unpack_from("<I", b, o)[0]
    if h.get("n_entries"):     # an empty journal has no head/tail entry: leave its zero stamps absent
        h["head_utc"] = _utc(h.get("head_entry_realtime"))
        h["tail_utc"] = _utc(h.get("tail_entry_realtime"))
    else:
        for k in ("head_entry_realtime", "tail_entry_realtime", "tail_entry_monotonic", "head_entry_seqnum",
                  "tail_entry_seqnum"):
            h.pop(k, None)
    return h


def journald_value(data, ctx):
    if data is None:
        return None
    try:
        h = header(data)
    except (struct.error, TypeError, ValueError):
        return None
    if h is None:
        return "none"
    key = _ALIAS.get(ctx.get("field") or "")
    v = h.get(key) if key else None
    return "none" if v is None else v
