"""Non-libpcap capture files: Sun snoop, Microsoft Network Monitor 1.x/2.x, Endace ERF, and any of them gzip/zstd/
lz4/xz-wrapped (prebuilt, SPECULATIVE). Pure struct. fmt `capture` answers any capture (pcap/pcapng via the pcap
module, then snoop/NetMon/ERF); fmts `snoop` / `netmon` / `erf` answer their own container only. A file that is not the
asked container (wrong / unknown magic, text, renamed impostor) -> "none" -- never a guessed count.

Sun snoop (RFC 1761): magic b"snoop\\0\\0\\0" @0, version u32 BE @8 (2), datalink u32 BE @12 (snoop DL_ codes: 4 =
Ethernet; the STORED value is returned, not the pcap LINKTYPE). Records: orig_len, incl_len, rec_len (padded), drops,
ts_sec, ts_usec (u32 BE each) + data; walk by rec_len; a cut-short tail record is not counted (capinfos).
NetMon 2.x: b"GMBU" @0, minor u8 @4, major u8 @5 (version "major.minor"), MAC type u16 LE @6 (1 = Ethernet),
SYSTEMTIME start @8 (8 x u16 LE: year, month, dow, day, h, m, s, ms), frame table offset u32 @0x18, length u32 @0x1c;
frame count = table length / 4. Frame: ts_delta u64 usec, frame_len u32, bytes_avail u32. NetMon 1.x: b"RTSS", same
header layout; frame: ts_delta u32 msec, frame_len u16, bytes_avail u16. Frame time = start SYSTEMTIME (read as UTC,
as Wireshark/capinfos do) + delta; fraction at the file's resolution (usec 2.x, msec 1.x).
ERF (no magic): 16-byte record header = ts u64 LE (32.32 fixed point; ns rounded the way Wireshark's reader does),
type u8 (low 7 bits; 0x80 = extension headers follow), flags u8, rlen u16 BE, lctr u16 BE, wlen u16 BE; walk by rlen.
Accepted as ERF only when every walked record has a known type (1..48) and rlen >= 16, and the walk lands on EOF (a
partial tail is tolerated after >= 2 good records). Every record counts as a packet, META (27) included (capinfos).
Times -> 'YYYY-MM-DDTHH:MM:SS[.frac]Z' (pcap module's renderer: fraction dropped when zero or a seconds-only format)."""
import datetime
import struct

FIELDS = {
    ("snoop", "packet_count"): "capture_value",
    ("snoop", "packets"): "capture_value",
    ("snoop", "number_of_packets"): "capture_value",
    ("snoop", "num_packets"): "capture_value",
    ("snoop", "packet_record_count"): "capture_value",
    ("snoop", "record_count"): "capture_value",
    ("snoop", "packet_records"): "capture_value",
    ("snoop", "frame_count"): "capture_value",
    ("snoop", "packets_count"): "capture_value",
    ("snoop", "total_packets"): "capture_value",
    ("snoop", "number_of_frames"): "capture_value",
    ("snoop", "frames"): "capture_value",
    ("snoop", "frame_table_entry_count"): "capture_value",
    ("snoop", "number_of_records"): "capture_value",
    ("snoop", "records_count"): "capture_value",
    ("snoop", "linktype"): "capture_value",
    ("snoop", "link_type"): "capture_value",
    ("snoop", "datalink"): "capture_value",
    ("snoop", "data_link"): "capture_value",
    ("snoop", "datalink_type"): "capture_value",
    ("snoop", "data_link_type"): "capture_value",
    ("snoop", "dlt"): "capture_value",
    ("snoop", "network"): "capture_value",
    ("snoop", "mac_type"): "capture_value",
    ("snoop", "media_type"): "capture_value",
    ("snoop", "network_type"): "capture_value",
    ("snoop", "encapsulation_type"): "capture_value",
    ("snoop", "link_layer_type"): "capture_value",
    ("snoop", "linktype_id"): "capture_value",
    ("snoop", "version"): "capture_value",
    ("snoop", "format_version"): "capture_value",
    ("snoop", "file_format_version"): "capture_value",
    ("snoop", "header_version"): "capture_value",
    ("snoop", "first_packet_time_utc"): "capture_value",
    ("snoop", "first_packet_time"): "capture_value",
    ("snoop", "first_packet_timestamp"): "capture_value",
    ("snoop", "earliest_packet_time_utc"): "capture_value",
    ("snoop", "first_timestamp_utc"): "capture_value",
    ("snoop", "first_record_time_utc"): "capture_value",
    ("snoop", "first_frame_time_utc"): "capture_value",
    ("snoop", "last_packet_time_utc"): "capture_value",
    ("snoop", "last_packet_time"): "capture_value",
    ("snoop", "last_packet_timestamp"): "capture_value",
    ("snoop", "latest_packet_time_utc"): "capture_value",
    ("snoop", "last_timestamp_utc"): "capture_value",
    ("snoop", "last_record_time_utc"): "capture_value",
    ("snoop", "last_frame_time_utc"): "capture_value",
    ("snoop", "first_packet_time_unix"): "capture_value",
    ("snoop", "first_packet_ts_sec"): "capture_value",
    ("snoop", "first_packet_epoch"): "capture_value",
    ("snoop", "file_format"): "capture_value",
    ("snoop", "capture_format"): "capture_value",
    ("snoop", "file_type"): "capture_value",
    ("snoop", "container_format"): "capture_value",
    ("netmon", "packet_count"): "capture_value",
    ("netmon", "packets"): "capture_value",
    ("netmon", "number_of_packets"): "capture_value",
    ("netmon", "num_packets"): "capture_value",
    ("netmon", "packet_record_count"): "capture_value",
    ("netmon", "record_count"): "capture_value",
    ("netmon", "packet_records"): "capture_value",
    ("netmon", "frame_count"): "capture_value",
    ("netmon", "packets_count"): "capture_value",
    ("netmon", "total_packets"): "capture_value",
    ("netmon", "number_of_frames"): "capture_value",
    ("netmon", "frames"): "capture_value",
    ("netmon", "frame_table_entry_count"): "capture_value",
    ("netmon", "number_of_records"): "capture_value",
    ("netmon", "records_count"): "capture_value",
    ("netmon", "linktype"): "capture_value",
    ("netmon", "link_type"): "capture_value",
    ("netmon", "datalink"): "capture_value",
    ("netmon", "data_link"): "capture_value",
    ("netmon", "datalink_type"): "capture_value",
    ("netmon", "data_link_type"): "capture_value",
    ("netmon", "dlt"): "capture_value",
    ("netmon", "network"): "capture_value",
    ("netmon", "mac_type"): "capture_value",
    ("netmon", "media_type"): "capture_value",
    ("netmon", "network_type"): "capture_value",
    ("netmon", "encapsulation_type"): "capture_value",
    ("netmon", "link_layer_type"): "capture_value",
    ("netmon", "linktype_id"): "capture_value",
    ("netmon", "version"): "capture_value",
    ("netmon", "format_version"): "capture_value",
    ("netmon", "file_format_version"): "capture_value",
    ("netmon", "header_version"): "capture_value",
    ("netmon", "first_packet_time_utc"): "capture_value",
    ("netmon", "first_packet_time"): "capture_value",
    ("netmon", "first_packet_timestamp"): "capture_value",
    ("netmon", "earliest_packet_time_utc"): "capture_value",
    ("netmon", "first_timestamp_utc"): "capture_value",
    ("netmon", "first_record_time_utc"): "capture_value",
    ("netmon", "first_frame_time_utc"): "capture_value",
    ("netmon", "last_packet_time_utc"): "capture_value",
    ("netmon", "last_packet_time"): "capture_value",
    ("netmon", "last_packet_timestamp"): "capture_value",
    ("netmon", "latest_packet_time_utc"): "capture_value",
    ("netmon", "last_timestamp_utc"): "capture_value",
    ("netmon", "last_record_time_utc"): "capture_value",
    ("netmon", "last_frame_time_utc"): "capture_value",
    ("netmon", "first_packet_time_unix"): "capture_value",
    ("netmon", "first_packet_ts_sec"): "capture_value",
    ("netmon", "first_packet_epoch"): "capture_value",
    ("netmon", "capture_start_time_utc"): "capture_value",
    ("netmon", "start_time_utc"): "capture_value",
    ("netmon", "header_start_time_utc"): "capture_value",
    ("netmon", "netmon_start_time_utc"): "capture_value",
    ("netmon", "file_format"): "capture_value",
    ("netmon", "capture_format"): "capture_value",
    ("netmon", "file_type"): "capture_value",
    ("netmon", "container_format"): "capture_value",
    ("netmon", "frame_table_offset"): "capture_value",
    ("netmon", "frametable_offset"): "capture_value",
    ("netmon", "frame_table_length"): "capture_value",
    ("netmon", "frame_table_size"): "capture_value",
    ("netmon", "frametable_length"): "capture_value",
    ("erf", "packet_count"): "capture_value",
    ("erf", "packets"): "capture_value",
    ("erf", "number_of_packets"): "capture_value",
    ("erf", "num_packets"): "capture_value",
    ("erf", "packet_record_count"): "capture_value",
    ("erf", "record_count"): "capture_value",
    ("erf", "packet_records"): "capture_value",
    ("erf", "frame_count"): "capture_value",
    ("erf", "packets_count"): "capture_value",
    ("erf", "total_packets"): "capture_value",
    ("erf", "number_of_frames"): "capture_value",
    ("erf", "frames"): "capture_value",
    ("erf", "frame_table_entry_count"): "capture_value",
    ("erf", "number_of_records"): "capture_value",
    ("erf", "records_count"): "capture_value",
    ("erf", "first_packet_time_utc"): "capture_value",
    ("erf", "first_packet_time"): "capture_value",
    ("erf", "first_packet_timestamp"): "capture_value",
    ("erf", "earliest_packet_time_utc"): "capture_value",
    ("erf", "first_timestamp_utc"): "capture_value",
    ("erf", "first_record_time_utc"): "capture_value",
    ("erf", "first_frame_time_utc"): "capture_value",
    ("erf", "last_packet_time_utc"): "capture_value",
    ("erf", "last_packet_time"): "capture_value",
    ("erf", "last_packet_timestamp"): "capture_value",
    ("erf", "latest_packet_time_utc"): "capture_value",
    ("erf", "last_timestamp_utc"): "capture_value",
    ("erf", "last_record_time_utc"): "capture_value",
    ("erf", "last_frame_time_utc"): "capture_value",
    ("erf", "first_packet_time_unix"): "capture_value",
    ("erf", "first_packet_ts_sec"): "capture_value",
    ("erf", "first_packet_epoch"): "capture_value",
    ("erf", "file_format"): "capture_value",
    ("erf", "capture_format"): "capture_value",
    ("erf", "file_type"): "capture_value",
    ("erf", "container_format"): "capture_value",
    ("erf", "record_types"): "capture_value",
    ("erf", "erf_record_types"): "capture_value",
    ("erf", "erf_types"): "capture_value",
    ("erf", "first_record_type"): "capture_value",
    ("erf", "erf_type"): "capture_value",
    ("erf", "record_type"): "capture_value",
    ("capture", "packet_count"): "capture_value",
    ("capture", "packets"): "capture_value",
    ("capture", "number_of_packets"): "capture_value",
    ("capture", "num_packets"): "capture_value",
    ("capture", "packet_record_count"): "capture_value",
    ("capture", "record_count"): "capture_value",
    ("capture", "packet_records"): "capture_value",
    ("capture", "frame_count"): "capture_value",
    ("capture", "packets_count"): "capture_value",
    ("capture", "total_packets"): "capture_value",
    ("capture", "number_of_frames"): "capture_value",
    ("capture", "frames"): "capture_value",
    ("capture", "frame_table_entry_count"): "capture_value",
    ("capture", "number_of_records"): "capture_value",
    ("capture", "records_count"): "capture_value",
    ("capture", "linktype"): "capture_value",
    ("capture", "link_type"): "capture_value",
    ("capture", "datalink"): "capture_value",
    ("capture", "data_link"): "capture_value",
    ("capture", "datalink_type"): "capture_value",
    ("capture", "data_link_type"): "capture_value",
    ("capture", "dlt"): "capture_value",
    ("capture", "network"): "capture_value",
    ("capture", "mac_type"): "capture_value",
    ("capture", "media_type"): "capture_value",
    ("capture", "network_type"): "capture_value",
    ("capture", "encapsulation_type"): "capture_value",
    ("capture", "link_layer_type"): "capture_value",
    ("capture", "linktype_id"): "capture_value",
    ("capture", "version"): "capture_value",
    ("capture", "format_version"): "capture_value",
    ("capture", "file_format_version"): "capture_value",
    ("capture", "header_version"): "capture_value",
    ("capture", "first_packet_time_utc"): "capture_value",
    ("capture", "first_packet_time"): "capture_value",
    ("capture", "first_packet_timestamp"): "capture_value",
    ("capture", "earliest_packet_time_utc"): "capture_value",
    ("capture", "first_timestamp_utc"): "capture_value",
    ("capture", "first_record_time_utc"): "capture_value",
    ("capture", "first_frame_time_utc"): "capture_value",
    ("capture", "last_packet_time_utc"): "capture_value",
    ("capture", "last_packet_time"): "capture_value",
    ("capture", "last_packet_timestamp"): "capture_value",
    ("capture", "latest_packet_time_utc"): "capture_value",
    ("capture", "last_timestamp_utc"): "capture_value",
    ("capture", "last_record_time_utc"): "capture_value",
    ("capture", "last_frame_time_utc"): "capture_value",
    ("capture", "first_packet_time_unix"): "capture_value",
    ("capture", "first_packet_ts_sec"): "capture_value",
    ("capture", "first_packet_epoch"): "capture_value",
    ("capture", "file_format"): "capture_value",
    ("capture", "capture_format"): "capture_value",
    ("capture", "file_type"): "capture_value",
    ("capture", "container_format"): "capture_value",
}

_ALIASES = {
 "packet_count": [
  "packet_count",
  "packets",
  "number_of_packets",
  "num_packets",
  "packet_record_count",
  "record_count",
  "packet_records",
  "frame_count",
  "packets_count",
  "total_packets",
  "number_of_frames",
  "frames",
  "frame_table_entry_count",
  "number_of_records",
  "records_count"
 ],
 "linktype": [
  "linktype",
  "link_type",
  "datalink",
  "data_link",
  "datalink_type",
  "data_link_type",
  "dlt",
  "network",
  "mac_type",
  "media_type",
  "network_type",
  "encapsulation_type",
  "link_layer_type",
  "linktype_id"
 ],
 "version": [
  "version",
  "format_version",
  "file_format_version",
  "header_version"
 ],
 "first_time": [
  "first_packet_time_utc",
  "first_packet_time",
  "first_packet_timestamp",
  "earliest_packet_time_utc",
  "first_timestamp_utc",
  "first_record_time_utc",
  "first_frame_time_utc"
 ],
 "last_time": [
  "last_packet_time_utc",
  "last_packet_time",
  "last_packet_timestamp",
  "latest_packet_time_utc",
  "last_timestamp_utc",
  "last_record_time_utc",
  "last_frame_time_utc"
 ],
 "first_unix": [
  "first_packet_time_unix",
  "first_packet_ts_sec",
  "first_packet_epoch"
 ],
 "start_time": [
  "capture_start_time_utc",
  "start_time_utc",
  "header_start_time_utc",
  "netmon_start_time_utc"
 ],
 "file_format": [
  "file_format",
  "capture_format",
  "file_type",
  "container_format"
 ],
 "record_types": [
  "record_types",
  "erf_record_types",
  "erf_types"
 ],
 "first_record_type": [
  "first_record_type",
  "erf_type",
  "record_type"
 ],
 "frame_table_offset": [
  "frame_table_offset",
  "frametable_offset"
 ],
 "frame_table_length": [
  "frame_table_length",
  "frame_table_size",
  "frametable_length"
 ]
}
_FIELD_KIND = {f: kind for kind, names in _ALIASES.items() for f in names}
_EPOCH = datetime.datetime(1970, 1, 1)


def _snoop(b):
    if len(b) < 16 or b[:8] != b"snoop\x00\x00\x00":
        return None
    ver, dl = struct.unpack_from(">II", b, 8)
    p = {"kind": "snoop", "version": ver, "linktype": dl, "times": []}
    off = 16
    while off + 24 <= len(b):
        _orig, incl, rec, _drops, sec, usec = struct.unpack_from(">6I", b, off)
        if rec < 24 + incl or off + 24 + incl > len(b):
            break
        p["times"].append((sec, usec, 10 ** 6))
        off += min(rec, len(b) - off)
    p["packets"] = len(p["times"])
    return p


def _systemtime(b, off):
    y, mo, _dow, d, h, mi, s, ms = struct.unpack_from("<8H", b, off)
    t = datetime.datetime(y, mo, d, h, mi, s, ms * 1000)
    return int((t - _EPOCH).total_seconds() // 1), ms


def _netmon(b):
    if len(b) < 32 or b[:4] not in (b"GMBU", b"RTSS"):
        return None
    v2 = b[:4] == b"GMBU"
    vmin, vmaj, mac = b[4], b[5], struct.unpack_from("<H", b, 6)[0]
    tbl_off, tbl_len = struct.unpack_from("<II", b, 0x18)
    if tbl_off + tbl_len > len(b) or tbl_len % 4:
        return None
    p = {"kind": "netmon2" if v2 else "netmon1", "version": "%d.%d" % (vmaj, vmin), "linktype": mac,
         "packets": tbl_len // 4, "tbl_off": tbl_off, "tbl_len": tbl_len, "times": []}
    try:
        ssec, sms = _systemtime(b, 8)
    except (ValueError, OverflowError):
        return p
    p["start"] = (ssec, sms, 1000)
    base_us = ssec * 10 ** 6 + sms * 1000
    for i in range(p["packets"]):
        fo, = struct.unpack_from("<I", b, tbl_off + 4 * i)
        if v2:
            if fo + 16 > len(b):
                continue
            t = base_us + struct.unpack_from("<Q", b, fo)[0]
            p["times"].append((t // 10 ** 6, t % 10 ** 6, 10 ** 6))
        else:
            if fo + 8 > len(b):
                continue
            t = ssec * 1000 + sms + struct.unpack_from("<I", b, fo)[0]
            p["times"].append((t // 1000, t % 1000, 1000))
    return p


def _erf(b):
    n, off, times, types = len(b), 0, [], []
    while off + 16 <= n:
        ts, typ, _fl, rlen = struct.unpack_from("<QBBH", b, off)
        rlen = struct.unpack_from(">H", b, off + 10)[0]
        t = typ & 0x7F
        if not 1 <= t <= 48 or rlen < 16:
            return None
        if off + rlen > n:
            break
        ns = (ts & 0xFFFFFFFF) * 10 ** 9
        ns += (ns & 0x80000000) << 1
        times.append((ts >> 32, ns >> 32, 10 ** 9))
        types.append(t)
        off += rlen
    if not times or (off != n and len(times) < 2):
        return None
    return {"kind": "erf", "packets": len(times), "times": times, "types": types}


def _parse_own(b, kinds):
    for kind, fn in (("snoop", _snoop), ("netmon", _netmon), ("erf", _erf)):
        if kind in kinds:
            p = fn(b)
            if p:
                return p
    return None


def _parse(b, fmt):
    from .pcap import _parse as _pcap_parse, _unwrap
    kinds = ("snoop", "netmon", "erf") if fmt == "capture" else (fmt,)
    if fmt == "capture" and _pcap_parse(b):
        return "pcap"
    p = _parse_own(b, kinds)
    if p is None:
        inner = _unwrap(b)
        if inner:
            if fmt == "capture" and _pcap_parse(inner):
                return "pcap"
            p = _parse_own(inner, kinds)
    return p


_PCAP_FIELD = {"packet_count": "packet_count", "linktype": "linktype", "version": "version",
               "first_time": "first_packet_time_utc", "last_time": "last_packet_time_utc",
               "first_unix": "first_packet_time_unix"}


def capture_value(data, ctx):
    """snoop./netmon./erf./capture.<field>: header / record-walk values (see module doc)."""
    if not data:
        return None
    fmt = ctx.get("fmt") or "capture"
    field = ctx.get("field") or ""
    kind = _FIELD_KIND.get(field)
    try:
        p = _parse(bytes(data), fmt)
    except (struct.error, ValueError, OverflowError, IndexError):
        p = None
    if p is None:
        return "none"
    if p == "pcap":
        if kind == "file_format":
            from .pcap import _parse as _pcap_parse, _unwrap
            q = _pcap_parse(bytes(data)) or _pcap_parse(_unwrap(bytes(data)) or b"") or {}
            return q.get("kind") or "none"
        if kind not in _PCAP_FIELD:
            return "none"
        from .pcap import pcap_value
        return pcap_value(data, dict(ctx, field=_PCAP_FIELD[kind]))
    if kind == "packet_count":
        return p["packets"]
    if kind == "file_format":
        return p["kind"]
    if kind in ("linktype", "version"):
        return p.get(kind, "none")
    if kind in ("first_time", "last_time", "first_unix", "start_time"):
        from .pcap import _iso
        if kind == "start_time":
            t = p.get("start")
        else:
            t = (p["times"][0] if kind != "last_time" else p["times"][-1]) if p["times"] else None
        if t is None:
            return "none"
        return t[0] if kind == "first_unix" else _iso(t, ctx.get("question"))
    if kind == "record_types":
        return p.get("types") or "none"
    if kind == "first_record_type":
        return p["types"][0] if p.get("types") else "none"
    if kind == "frame_table_offset":
        return p.get("tbl_off", "none")
    if kind == "frame_table_length":
        return p.get("tbl_len", "none")
    return None
