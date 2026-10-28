"""PCAP / PCAPNG capture-file header fields (prebuilt, SPECULATIVE; pcap.packet_count is GM-verified D27 via
lib/meta/pcap.py, which calls pcap_value here). Pure struct.

Classic pcap (libpcap file format): 24-byte global header = magic u32 @0, version_major u16 @4, version_minor u16 @6,
thiszone i32 @8, sigfigs u32 @12, snaplen u32 @16, network (LINKTYPE_*) u32 @20; then records = ts_sec u32,
ts_usec|ts_nsec u32, incl_len u32, orig_len u32 + incl_len bytes. The magic sets byte order AND time resolution:
0xa1b2c3d4 microseconds, 0xa1b23c4d nanoseconds, 0xa1b2cd34 Kuznetzov (24-byte record header) -- written in the
writer's byte order, so `d4 c3 b2 a1` on disk is a little-endian 0xa1b2c3d4 file.
PCAPNG: blocks = type u32, total length u32, body, total length u32. SHB 0x0a0d0d0a: byte-order magic 0x1a2b3c4d
(sets endianness), major u16, minor u16, section length i64, options (shb_comment 1, shb_hardware 2, shb_os 3,
shb_userappl 4). IDB 0x00000001: linktype u16, reserved u16, snaplen u32, options (if_name 2, if_description 3,
if_tsresol 9: high bit set -> 2^-n s, else 10^-n s; default 10^-6). Packets: EPB 6 (if_id, ts high/low), obsolete
PB 2 (u16 if_id, u16 drops, ts high/low), SPB 3 (no timestamp, counted).
Options: code u16, length u16, value padded to 4; opt_endofopt 0.

magic_u32_hex = the magic read in the FILE's byte order (the value the writer packed: 0xa1b2c3d4 / 0xa1b23c4d; pcapng
-> its byte-order magic 0x1a2b3c4d, block_type_u32_hex -> 0x0a0d0d0a). version = "major.minor" ("2.4", pcapng "1.0").
linktype / snaplen = the pcap global header values; pcapng -> the FIRST IDB's (capinfos -I "Encapsulation" number /
"Capture length"). packet_count = complete packet records (capinfos "Number of packets"); a truncated tail record is
not counted. first/last_packet_time_utc: the record timestamp (unix epoch, UTC) -> 'YYYY-MM-DDTHH:MM:SS[.frac]Z',
the fraction at the file's own resolution (6 digits usec, 9 nsec, as capinfos prints it), dropped when it is zero or
when the answer_format spells a seconds-only 'HH:MM:SS' pattern; *_unix -> integer epoch seconds.
if_names = every IDB's if_name in IDB order (all sections; IDBs without one are skipped) -> JSON list.
Both fmts read both containers (a pcapng asked as "pcap" is still answered from its bytes). A gzip/zstd/lz4/xz-wrapped
capture (`capture-001.pcap.gz`; capinfos opens it transparently) is decompressed first. Classic-pcap version numbers
are not checked (AIX 2.2/2.3 and other writers' versions still parse with the magic's record layout); a 0-byte record
counts. PCAPNG counts EPB 6 + SPB 3 + obsolete PB 2 across every section (each SHB re-sets byte order); IDB/ISB/NRB/
DSB/custom 0xbad/0x40000bad blocks are not packets. Anything else (snoop/ERF/
renamed impostor) -> "none"; an option/field the file lacks (if_names of a classic pcap, absent shb_os) -> "none"."""
import datetime
import json
import re
import struct

from ..spell import Hex

_PCAP_MAGIC = {0xA1B2C3D4: (16, 6), 0xA1B23C4D: (16, 9), 0xA1B2CD34: (24, 6)}   # magic -> (record hdr len, ts digits)

_ALIASES = {
    "magic": ["magic_u32_hex", "magic_number_u32_hex", "header_magic_u32_hex", "global_header_magic_u32_hex",
              "magic_hex", "magic_number_hex", "file_magic_u32_hex"],
    "bom": ["byte_order_magic_u32_hex", "shb_byte_order_magic_u32_hex", "shb_magic_u32_hex"],
    "block_type": ["block_type_u32_hex", "shb_block_type_u32_hex", "first_block_type_u32_hex"],
    "version": ["version", "header_version", "global_header_version", "format_version", "file_format_version",
                "shb_version", "pcap_version", "pcapng_version"],
    "major": ["major_version", "version_major", "shb_major_version", "shb_version_major"],
    "minor": ["minor_version", "version_minor", "shb_minor_version", "shb_version_minor"],
    "linktype": ["linktype", "link_type", "network", "linktype_id", "data_link_type", "dlt", "global_header_network",
                 "global_header_linktype", "header_linktype", "idb_linktype", "idb_link_type", "first_idb_linktype",
                 "interface_linktype", "link_layer_type", "encapsulation_type"],
    "linktypes": ["linktypes", "link_types", "idb_linktypes", "interface_linktypes"],
    "snaplen": ["snaplen", "snap_len", "snapshot_length", "global_header_snaplen", "header_snaplen", "idb_snaplen",
                "idb_snap_len", "interface_snaplen", "max_packet_length"],
    "thiszone": ["thiszone", "this_zone", "timezone_offset"],
    "sigfigs": ["sigfigs", "timestamp_accuracy"],
    "packet_count": ["packet_count", "packets", "number_of_packets", "num_packets", "packet_record_count",
                     "record_count", "packet_records", "frame_count", "packets_count", "total_packets"],
    "block_count": ["block_count", "number_of_blocks"],
    "first_time": ["first_packet_time_utc", "first_packet_time", "first_packet_timestamp", "first_packet_timestamp_utc",
                   "first_timestamp_utc", "earliest_packet_time_utc", "capture_start_time_utc", "first_packet_ts_utc",
                   "first_record_time_utc", "start_time_utc"],
    "last_time": ["last_packet_time_utc", "last_packet_time", "last_packet_timestamp", "latest_packet_time_utc",
                  "capture_end_time_utc", "last_record_time_utc", "end_time_utc"],
    "first_unix": ["first_packet_time_unix", "first_packet_ts_sec", "first_packet_epoch"],
    "if_names": ["if_names", "interface_names", "idb_if_names", "idb_names", "idb_interface_names"],
    "if_name": ["if_name", "interface_name", "idb_if_name", "first_if_name"],
    "if_count": ["interface_count", "number_of_interfaces", "idb_count", "if_count", "interfaces_count"],
    "shb_os": ["shb_os", "os", "capture_os", "operating_system", "capture_oper_sys"],
    "shb_hardware": ["shb_hardware", "hardware", "capture_hardware"],
    "shb_userappl": ["shb_userappl", "user_application", "capture_application", "shb_user_appl", "application"],
    "shb_comment": ["shb_comment", "capture_comment", "section_comment"],
}
# FIELDS must be a literal dict (the registry reads it with ast): every _ALIASES name, per fmt.
FIELDS = {
    ("pcap", "magic_u32_hex"): "pcap_value", ("pcapng", "magic_u32_hex"): "pcap_value",
    ("pcap", "magic_number_u32_hex"): "pcap_value", ("pcapng", "magic_number_u32_hex"): "pcap_value",
    ("pcap", "header_magic_u32_hex"): "pcap_value", ("pcapng", "header_magic_u32_hex"): "pcap_value",
    ("pcap", "global_header_magic_u32_hex"): "pcap_value", ("pcapng", "global_header_magic_u32_hex"): "pcap_value",
    ("pcap", "magic_hex"): "pcap_value", ("pcapng", "magic_hex"): "pcap_value",
    ("pcap", "magic_number_hex"): "pcap_value", ("pcapng", "magic_number_hex"): "pcap_value",
    ("pcap", "file_magic_u32_hex"): "pcap_value", ("pcapng", "file_magic_u32_hex"): "pcap_value",
    ("pcap", "byte_order_magic_u32_hex"): "pcap_value", ("pcapng", "byte_order_magic_u32_hex"): "pcap_value",
    ("pcap", "shb_byte_order_magic_u32_hex"): "pcap_value", ("pcapng", "shb_byte_order_magic_u32_hex"): "pcap_value",
    ("pcap", "shb_magic_u32_hex"): "pcap_value", ("pcapng", "shb_magic_u32_hex"): "pcap_value",
    ("pcap", "block_type_u32_hex"): "pcap_value", ("pcapng", "block_type_u32_hex"): "pcap_value",
    ("pcap", "shb_block_type_u32_hex"): "pcap_value", ("pcapng", "shb_block_type_u32_hex"): "pcap_value",
    ("pcap", "first_block_type_u32_hex"): "pcap_value", ("pcapng", "first_block_type_u32_hex"): "pcap_value",
    ("pcap", "version"): "pcap_value", ("pcapng", "version"): "pcap_value",
    ("pcap", "header_version"): "pcap_value", ("pcapng", "header_version"): "pcap_value",
    ("pcap", "global_header_version"): "pcap_value", ("pcapng", "global_header_version"): "pcap_value",
    ("pcap", "format_version"): "pcap_value", ("pcapng", "format_version"): "pcap_value",
    ("pcap", "file_format_version"): "pcap_value", ("pcapng", "file_format_version"): "pcap_value",
    ("pcap", "shb_version"): "pcap_value", ("pcapng", "shb_version"): "pcap_value",
    ("pcap", "pcap_version"): "pcap_value", ("pcapng", "pcapng_version"): "pcap_value",
    ("pcap", "major_version"): "pcap_value", ("pcapng", "major_version"): "pcap_value",
    ("pcap", "version_major"): "pcap_value", ("pcapng", "version_major"): "pcap_value",
    ("pcap", "shb_major_version"): "pcap_value", ("pcapng", "shb_major_version"): "pcap_value",
    ("pcap", "shb_version_major"): "pcap_value", ("pcapng", "shb_version_major"): "pcap_value",
    ("pcap", "minor_version"): "pcap_value", ("pcapng", "minor_version"): "pcap_value",
    ("pcap", "version_minor"): "pcap_value", ("pcapng", "version_minor"): "pcap_value",
    ("pcap", "shb_minor_version"): "pcap_value", ("pcapng", "shb_minor_version"): "pcap_value",
    ("pcap", "shb_version_minor"): "pcap_value", ("pcapng", "shb_version_minor"): "pcap_value",
    ("pcap", "linktype"): "pcap_value", ("pcapng", "linktype"): "pcap_value",
    ("pcap", "link_type"): "pcap_value", ("pcapng", "link_type"): "pcap_value",
    ("pcap", "network"): "pcap_value", ("pcapng", "network"): "pcap_value",
    ("pcap", "linktype_id"): "pcap_value", ("pcapng", "linktype_id"): "pcap_value",
    ("pcap", "data_link_type"): "pcap_value", ("pcapng", "data_link_type"): "pcap_value",
    ("pcap", "dlt"): "pcap_value", ("pcapng", "dlt"): "pcap_value",
    ("pcap", "global_header_network"): "pcap_value", ("pcapng", "global_header_network"): "pcap_value",
    ("pcap", "global_header_linktype"): "pcap_value", ("pcapng", "global_header_linktype"): "pcap_value",
    ("pcap", "header_linktype"): "pcap_value", ("pcapng", "header_linktype"): "pcap_value",
    ("pcap", "idb_linktype"): "pcap_value", ("pcapng", "idb_linktype"): "pcap_value",
    ("pcap", "idb_link_type"): "pcap_value", ("pcapng", "idb_link_type"): "pcap_value",
    ("pcap", "first_idb_linktype"): "pcap_value", ("pcapng", "first_idb_linktype"): "pcap_value",
    ("pcap", "interface_linktype"): "pcap_value", ("pcapng", "interface_linktype"): "pcap_value",
    ("pcap", "link_layer_type"): "pcap_value", ("pcapng", "link_layer_type"): "pcap_value",
    ("pcap", "encapsulation_type"): "pcap_value", ("pcapng", "encapsulation_type"): "pcap_value",
    ("pcap", "linktypes"): "pcap_value", ("pcapng", "linktypes"): "pcap_value",
    ("pcap", "link_types"): "pcap_value", ("pcapng", "link_types"): "pcap_value",
    ("pcap", "idb_linktypes"): "pcap_value", ("pcapng", "idb_linktypes"): "pcap_value",
    ("pcap", "interface_linktypes"): "pcap_value", ("pcapng", "interface_linktypes"): "pcap_value",
    ("pcap", "snaplen"): "pcap_value", ("pcapng", "snaplen"): "pcap_value",
    ("pcap", "snap_len"): "pcap_value", ("pcapng", "snap_len"): "pcap_value",
    ("pcap", "snapshot_length"): "pcap_value", ("pcapng", "snapshot_length"): "pcap_value",
    ("pcap", "global_header_snaplen"): "pcap_value", ("pcapng", "global_header_snaplen"): "pcap_value",
    ("pcap", "header_snaplen"): "pcap_value", ("pcapng", "header_snaplen"): "pcap_value",
    ("pcap", "idb_snaplen"): "pcap_value", ("pcapng", "idb_snaplen"): "pcap_value",
    ("pcap", "idb_snap_len"): "pcap_value", ("pcapng", "idb_snap_len"): "pcap_value",
    ("pcap", "interface_snaplen"): "pcap_value", ("pcapng", "interface_snaplen"): "pcap_value",
    ("pcap", "max_packet_length"): "pcap_value", ("pcapng", "max_packet_length"): "pcap_value",
    ("pcap", "thiszone"): "pcap_value", ("pcap", "this_zone"): "pcap_value", ("pcap", "timezone_offset"): "pcap_value",
    ("pcap", "sigfigs"): "pcap_value", ("pcap", "timestamp_accuracy"): "pcap_value",
    ("pcapng", "packet_count"): "pcap_value",
    ("pcap", "packets"): "pcap_value", ("pcapng", "packets"): "pcap_value",
    ("pcap", "number_of_packets"): "pcap_value", ("pcapng", "number_of_packets"): "pcap_value",
    ("pcap", "num_packets"): "pcap_value", ("pcapng", "num_packets"): "pcap_value",
    ("pcap", "packet_record_count"): "pcap_value", ("pcapng", "packet_record_count"): "pcap_value",
    ("pcap", "record_count"): "pcap_value", ("pcapng", "record_count"): "pcap_value",
    ("pcap", "packet_records"): "pcap_value", ("pcapng", "packet_records"): "pcap_value",
    ("pcap", "frame_count"): "pcap_value", ("pcapng", "frame_count"): "pcap_value",
    ("pcap", "packets_count"): "pcap_value", ("pcapng", "packets_count"): "pcap_value",
    ("pcap", "total_packets"): "pcap_value", ("pcapng", "total_packets"): "pcap_value",
    ("pcapng", "block_count"): "pcap_value", ("pcapng", "number_of_blocks"): "pcap_value",
    ("pcap", "first_packet_time_utc"): "pcap_value", ("pcapng", "first_packet_time_utc"): "pcap_value",
    ("pcap", "first_packet_time"): "pcap_value", ("pcapng", "first_packet_time"): "pcap_value",
    ("pcap", "first_packet_timestamp"): "pcap_value", ("pcapng", "first_packet_timestamp"): "pcap_value",
    ("pcap", "first_packet_timestamp_utc"): "pcap_value", ("pcapng", "first_packet_timestamp_utc"): "pcap_value",
    ("pcap", "first_timestamp_utc"): "pcap_value", ("pcapng", "first_timestamp_utc"): "pcap_value",
    ("pcap", "earliest_packet_time_utc"): "pcap_value", ("pcapng", "earliest_packet_time_utc"): "pcap_value",
    ("pcap", "capture_start_time_utc"): "pcap_value", ("pcapng", "capture_start_time_utc"): "pcap_value",
    ("pcap", "first_packet_ts_utc"): "pcap_value", ("pcapng", "first_packet_ts_utc"): "pcap_value",
    ("pcap", "first_record_time_utc"): "pcap_value", ("pcapng", "first_record_time_utc"): "pcap_value",
    ("pcap", "start_time_utc"): "pcap_value", ("pcapng", "start_time_utc"): "pcap_value",
    ("pcap", "last_packet_time_utc"): "pcap_value", ("pcapng", "last_packet_time_utc"): "pcap_value",
    ("pcap", "last_packet_time"): "pcap_value", ("pcapng", "last_packet_time"): "pcap_value",
    ("pcap", "last_packet_timestamp"): "pcap_value", ("pcapng", "last_packet_timestamp"): "pcap_value",
    ("pcap", "latest_packet_time_utc"): "pcap_value", ("pcapng", "latest_packet_time_utc"): "pcap_value",
    ("pcap", "capture_end_time_utc"): "pcap_value", ("pcapng", "capture_end_time_utc"): "pcap_value",
    ("pcap", "last_record_time_utc"): "pcap_value", ("pcapng", "last_record_time_utc"): "pcap_value",
    ("pcap", "end_time_utc"): "pcap_value", ("pcapng", "end_time_utc"): "pcap_value",
    ("pcap", "first_packet_time_unix"): "pcap_value", ("pcapng", "first_packet_time_unix"): "pcap_value",
    ("pcap", "first_packet_ts_sec"): "pcap_value", ("pcapng", "first_packet_ts_sec"): "pcap_value",
    ("pcap", "first_packet_epoch"): "pcap_value", ("pcapng", "first_packet_epoch"): "pcap_value",
    ("pcap", "if_names"): "pcap_value", ("pcapng", "if_names"): "pcap_value",
    ("pcap", "interface_names"): "pcap_value", ("pcapng", "interface_names"): "pcap_value",
    ("pcap", "idb_if_names"): "pcap_value", ("pcapng", "idb_if_names"): "pcap_value",
    ("pcap", "idb_names"): "pcap_value", ("pcapng", "idb_names"): "pcap_value",
    ("pcap", "idb_interface_names"): "pcap_value", ("pcapng", "idb_interface_names"): "pcap_value",
    ("pcap", "if_name"): "pcap_value", ("pcapng", "if_name"): "pcap_value",
    ("pcap", "interface_name"): "pcap_value", ("pcapng", "interface_name"): "pcap_value",
    ("pcap", "idb_if_name"): "pcap_value", ("pcapng", "idb_if_name"): "pcap_value",
    ("pcap", "first_if_name"): "pcap_value", ("pcapng", "first_if_name"): "pcap_value",
    ("pcap", "interface_count"): "pcap_value", ("pcapng", "interface_count"): "pcap_value",
    ("pcap", "number_of_interfaces"): "pcap_value", ("pcapng", "number_of_interfaces"): "pcap_value",
    ("pcap", "idb_count"): "pcap_value", ("pcapng", "idb_count"): "pcap_value",
    ("pcap", "if_count"): "pcap_value", ("pcapng", "if_count"): "pcap_value",
    ("pcap", "interfaces_count"): "pcap_value", ("pcapng", "interfaces_count"): "pcap_value",
    ("pcap", "shb_os"): "pcap_value", ("pcapng", "shb_os"): "pcap_value",
    ("pcap", "os"): "pcap_value", ("pcapng", "os"): "pcap_value",
    ("pcap", "capture_os"): "pcap_value", ("pcapng", "capture_os"): "pcap_value",
    ("pcap", "operating_system"): "pcap_value", ("pcapng", "operating_system"): "pcap_value",
    ("pcap", "capture_oper_sys"): "pcap_value", ("pcapng", "capture_oper_sys"): "pcap_value",
    ("pcap", "shb_hardware"): "pcap_value", ("pcapng", "shb_hardware"): "pcap_value",
    ("pcap", "hardware"): "pcap_value", ("pcapng", "hardware"): "pcap_value",
    ("pcap", "capture_hardware"): "pcap_value", ("pcapng", "capture_hardware"): "pcap_value",
    ("pcap", "shb_userappl"): "pcap_value", ("pcapng", "shb_userappl"): "pcap_value",
    ("pcap", "user_application"): "pcap_value", ("pcapng", "user_application"): "pcap_value",
    ("pcap", "capture_application"): "pcap_value", ("pcapng", "capture_application"): "pcap_value",
    ("pcap", "shb_user_appl"): "pcap_value", ("pcapng", "shb_user_appl"): "pcap_value",
    ("pcap", "application"): "pcap_value", ("pcapng", "application"): "pcap_value",
    ("pcap", "shb_comment"): "pcap_value", ("pcapng", "shb_comment"): "pcap_value",
    ("pcap", "capture_comment"): "pcap_value", ("pcapng", "capture_comment"): "pcap_value",
    ("pcap", "section_comment"): "pcap_value", ("pcapng", "section_comment"): "pcap_value",
}
_FIELD_KIND = {f: kind for kind, names in _ALIASES.items() for f in names}


def _opts(b, off, end, e):
    """pcapng options [(code, raw value)] in [off, end)."""
    out = []
    while off + 4 <= end:
        code, ln = struct.unpack_from(e + "HH", b, off)
        if code == 0:
            break
        off += 4
        if off + ln > end:
            break
        out.append((code, bytes(b[off:off + ln])))
        off += (ln + 3) & ~3
    return out


def _text(v):
    return v.split(b"\0", 1)[0].decode("utf-8", "replace").strip()


def _parse_pcap(b):
    if len(b) < 24:
        return None
    for e in "<>":
        magic, = struct.unpack_from(e + "I", b, 0)
        if magic in _PCAP_MAGIC:
            break
    else:
        return None
    rh, digits = _PCAP_MAGIC[magic]
    vmaj, vmin, zone, sigf, snap, net = struct.unpack_from(e + "HHiIII", b, 4)
    p = {"kind": "pcap", "magic": magic, "major": vmaj, "minor": vmin, "thiszone": zone, "sigfigs": sigf,
         "snaplen": snap, "linktype": net & 0x0FFFFFFF, "linktypes": [net & 0x0FFFFFFF], "if_count": 1,
         "if_names": None, "times": [], "digits": digits, "packets": 0}
    off = 24
    while off + rh <= len(b):
        sec, frac, incl, _orig = struct.unpack_from(e + "IIII", b, off)
        if off + rh + incl > len(b):
            break
        p["packets"] += 1
        p["times"].append((sec, frac, 10 ** digits))
        off += rh + incl
    return p


def _parse_pcapng(b):
    if len(b) < 28 or bytes(b[:4]) != b"\x0a\x0d\x0d\x0a":
        return None
    if bytes(b[8:12]) == b"\x4d\x3c\x2b\x1a":
        e = "<"
    elif bytes(b[8:12]) == b"\x1a\x2b\x3c\x4d":
        e = ">"
    else:
        return None
    p = {"kind": "pcapng", "magic": 0x1A2B3C4D, "block_type": 0x0A0D0D0A, "packets": 0, "blocks": 0, "times": [],
         "linktypes": [], "snaplens": [], "if_names": [], "shb": {}}
    off, idbs = 0, []
    while off + 12 <= len(b):
        btype, = struct.unpack_from(e + "I", b, off)
        if btype == 0x0A0D0D0A:          # a new section: its own byte order and interface numbering
            bom = bytes(b[off + 8:off + 12])
            e = "<" if bom == b"\x4d\x3c\x2b\x1a" else ">" if bom == b"\x1a\x2b\x3c\x4d" else None
            if e is None:
                break
            idbs = []
        blen, = struct.unpack_from(e + "I", b, off + 4)
        if blen < 12 or blen % 4 or off + blen > len(b):
            break
        body, end = off + 8, off + blen - 4
        p["blocks"] += 1
        if btype == 0x0A0D0D0A and end - body >= 16:
            maj, mnr = struct.unpack_from(e + "HH", b, body + 4)
            p.setdefault("major", maj)
            p.setdefault("minor", mnr)
            for code, v in _opts(b, body + 16, end, e):
                p["shb"].setdefault(code, _text(v))
        elif btype == 1 and end - body >= 8:
            lt, _res, snap = struct.unpack_from(e + "HHI", b, body)
            name, tsres = None, 10 ** 6
            for code, v in _opts(b, body + 8, end, e):
                if code == 2 and name is None:
                    name = _text(v)
                elif code == 9 and v:
                    tsres = (1 << (v[0] & 0x7F)) if v[0] & 0x80 else 10 ** (v[0] & 0x7F)
            idbs.append(tsres)
            p["linktypes"].append(lt)
            p["snaplens"].append(snap)
            if name is not None:
                p["if_names"].append(name)
        elif btype in (6, 2) and end - body >= 20:
            if btype == 6:
                ifid, hi, lo = struct.unpack_from(e + "III", b, body)
            else:
                ifid, _drops, hi, lo = struct.unpack_from(e + "HHII", b, body)
            p["packets"] += 1
            res = idbs[ifid] if ifid < len(idbs) else 10 ** 6
            ts = (hi << 32) | lo
            p["times"].append((ts // res, ts % res, res))
        elif btype == 3:
            p["packets"] += 1
        off += blen
    if "major" not in p:
        return None
    p["if_count"] = len(p["linktypes"])
    return p


_MAX_UNPACKED = 64 << 20


def _unwrap(b):
    """A compressed capture (Wireshark opens these transparently: `.pcap.gz`, `.pcapng.zst`, `.lz4`, `.xz`) -> its
    decompressed bytes (bounded); concatenated gzip members are all read; a cut-short stream keeps what inflated."""
    head = bytes(b[:6])
    try:
        if head[:2] == b"\x1f\x8b":
            import zlib
            out, rest = b"", bytes(b)
            while rest[:2] == b"\x1f\x8b" and len(out) < _MAX_UNPACKED:
                d = zlib.decompressobj(31)
                try:
                    out += d.decompress(rest, _MAX_UNPACKED - len(out))
                except zlib.error:
                    break
                if not d.eof:
                    break
                rest = d.unused_data
            return out
        if head[:4] == b"\x28\xb5\x2f\xfd":
            import io
            import zstandard
            return zstandard.ZstdDecompressor().stream_reader(io.BytesIO(bytes(b))).read(_MAX_UNPACKED)
        if head[:4] == b"\x04\x22\x4d\x18":
            import lz4.frame
            return lz4.frame.decompress(bytes(b))[:_MAX_UNPACKED]
        if head == b"\xfd7zXZ\x00":
            import lzma
            return lzma.LZMADecompressor().decompress(bytes(b), _MAX_UNPACKED)
    except Exception:     # noqa: BLE001 -- a damaged wrapper is "not a capture", never a raise
        return None
    return None


def _parse(b):
    if not b:
        return None
    p = _parse_pcapng(b) or _parse_pcap(b)
    if p is None:
        inner = _unwrap(b)
        if inner:
            p = _parse_pcapng(inner) or _parse_pcap(inner)
    return p


def _iso(t, q):
    """(sec, frac, ticks/s) -> ISO-8601 UTC; fraction at the file's resolution unless zero / a seconds-only format."""
    sec, frac, res = t
    s = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=sec)).strftime("%Y-%m-%dT%H:%M:%S")
    fmt = json.dumps((q or {}).get("answer_format") or "")
    secs_only = re.search(r"HH:MM:SS", fmt, re.I) and not re.search(r"SS[.,]f|fraction|micro|nano|sub-?second|"
                                                                     r"\.\d{3}", fmt, re.I)
    if frac and not secs_only:
        digits = len(str(res - 1)) if res > 1 else 0
        if res != 10 ** digits:     # a power-of-two resolution: express it in nanoseconds
            frac, digits = frac * 10 ** 9 // res, 9
        s += ".%0*d" % (digits, frac)
    return s + "Z"


def pcap_value(data, ctx):
    """pcap.<field> / pcapng.<field>: global header / SHB / IDB / packet-record values (see module doc)."""
    try:
        p = _parse(data)
    except (struct.error, ValueError, OverflowError):
        p = None
    if p is None:
        return "none" if data else None
    field = ctx.get("field") or ""
    kind = _FIELD_KIND.get(field)
    ng = p["kind"] == "pcapng"
    if kind in ("magic", "bom"):
        return Hex(p["magic"], 8)
    if kind == "block_type":
        return Hex(p["block_type"], 8) if ng else "none"
    if kind == "version":
        return "%d.%d" % (p["major"], p["minor"])
    if kind in ("major", "minor"):
        return p[kind]
    if kind == "linktype":
        return p["linktypes"][0] if p["linktypes"] else "none"
    if kind == "linktypes":
        return p["linktypes"] or "none"
    if kind == "snaplen":
        return (p["snaplens"][0] if p["snaplens"] else "none") if ng else p["snaplen"]
    if kind in ("thiszone", "sigfigs"):
        return p[kind] if not ng else "none"
    if kind == "packet_count":
        return p["packets"]
    if kind == "block_count":
        return p.get("blocks", "none")
    if kind in ("first_time", "last_time", "first_unix"):
        if not p["times"]:
            return "none"
        t = p["times"][0] if kind != "last_time" else p["times"][-1]
        return t[0] if kind == "first_unix" else _iso(t, ctx.get("question"))
    if kind == "if_names":
        return p["if_names"] or "none"
    if kind == "if_name":
        return p["if_names"][0] if p["if_names"] else "none"
    if kind == "if_count":
        return p["if_count"]
    code = {"shb_hardware": 2, "shb_os": 3, "shb_userappl": 4, "shb_comment": 1}.get(kind)
    if code:
        return (p["shb"].get(code) or "none") if ng else "none"
    return None
