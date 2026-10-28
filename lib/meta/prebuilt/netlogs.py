"""Network EXPORTS that sit beside a capture (prebuilt, SPECULATIVE -- no field here was ever GM-verified; D27 flavor
"Packet captures, exports, and host artifacts"). stdlib only (no csv module: the gate bans it -> manual split);
dpkt only to pull NetFlow export packets out of a pcap/pcapng wrapper.

Formats (GM fmt token -> parser):
  zeek          Zeek/Bro log, TSV (`#separator \\x09` escaped, `#set_separator`, `#empty_field` "(empty)",
                `#unset_field` "-", `#path`, `#open`, `#fields`, `#types`, `#close`) or JSON lines (flat dotted keys
                "id.orig_h", as `LogAscii::use_json=T` writes). gzip-wrapped logs are unwrapped.
  suricata      Suricata eve.json: one JSON object per line with "event_type" (alert/dns/http/tls/flow/...).
  netflow       NetFlow v5 (24 B header + 48 B records), v9 (template FlowSet 0, data FlowSets >= 256) and IPFIX
                (v10; template Set 2, data Sets >= 256, enterprise bit + PEN, variable-length IEs). Raw export
                packets back to back, or UDP payloads inside a pcap/pcapng (first u16 of the payload in 5/9/10).
                Templates persist across packets (same stream). Options templates (v9 set 1 / IPFIX set 3) and
                their data records are NOT counted as flows.
  csv_flows     Wireshark "Export Packet Dissections -> As CSV": header "No.","Time","Source","Destination",
                "Protocol","Length","Info" (RFC 4180 quoting, "" escape).
  firewall_log  Windows Defender Firewall pfirewall.log (W3C-ish: #Version / #Software / #Time Format /
                `#Fields: date time action protocol src-ip dst-ip src-port dst-port size tcpflags ... path`), space
                separated, "-" = absent.

Value conventions (match pcap_flows.py): sets are JSON lists, Python sorted() of the TEXT spellings (IPs
lexicographic as text); port / id sets are sorted ints; counts and byte totals are base-10 ints; *_counts objects
have sorted keys; "first"/"last" timestamps are the STORED text of the min/max record (zeek ts epoch float text,
eve ISO text, firewall "date time"); netflow export_time_utc = header unix_secs (v5/v9) / export time (IPFIX) of the
first packet as ISO-8601 "YYYY-MM-DDTHH:MM:SSZ" (unix epoch: the only epoch these headers carry).
Not that format (pcap, an IIS W3C log for firewall_log, eve lines for zeek, ...) -> "none"; an absent field -> "none".
NOT DONE: the export-vs-capture packet-count cross-check (needs the sibling capture, not in the member bytes)."""
import collections
import datetime
import gzip
import io
import ipaddress
import json
import struct

# ----------------------------------------------------------------------------------------------- shared helpers


def _text(data):
    if not isinstance(data, (bytes, bytearray)) or not data:
        return None
    b = bytes(data)
    if b[:2] == b"\x1f\x8b":
        try:
            b = gzip.decompress(b)
        except (OSError, EOFError, ValueError):
            return None
    if b[:3] == b"\xef\xbb\xbf":
        b = b[3:]
    elif b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        try:
            return b.decode("utf-16")
        except UnicodeDecodeError:
            return None
    if b"\x00" in b[:4096]:
        return None
    return b.decode("utf-8", "replace")


def _ip_ok(s):
    try:
        ipaddress.ip_address(str(s).strip())
        return True
    except ValueError:
        return False


def _sset(vals):
    return sorted({str(v) for v in vals if v not in (None, "", "-", "(empty)")})


def _iset(vals):
    out = set()
    for v in vals:
        try:
            out.add(int(str(v).strip()))
        except (TypeError, ValueError):
            pass
    return sorted(out)


def _isum(vals):
    t = 0
    for v in vals:
        try:
            t += int(float(str(v).strip()))
        except (TypeError, ValueError):
            pass
    return t


def _counts(vals):
    c = collections.Counter(str(v) for v in vals if v not in (None, "", "-"))
    return {k: c[k] for k in sorted(c)}


def _top(vals):
    c = collections.Counter(str(v) for v in vals if v not in (None, "", "-"))
    if not c:
        return "none"
    best = max(c.values())
    return sorted(k for k, n in c.items() if n == best)[0]


def _canon(field, table):
    f = (field or "").lower()
    for canon, names in table.items():
        if f in names:
            return canon
    return None


def _json_lines(txt):
    out = []
    for ln in txt.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except ValueError:
            return None
        if not isinstance(o, dict):
            return None
        out.append(o)
    return out


# ------------------------------------------------------------------------------------------------------- zeek

def _zeek_unescape(s):
    try:
        return s.encode("latin-1", "backslashreplace").decode("unicode_escape")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


def parse_zeek(data):
    """{"meta": {...}, "rows": [ {field: value-or-None} ]} or None (not a Zeek log)."""
    txt = _text(data)
    if txt is None:
        return None
    lines = txt.splitlines()
    if any(ln.startswith("#separator") or ln.startswith("#fields") for ln in lines[:20]):
        sep, setsep, empty, unset = "\t", ",", "(empty)", "-"
        meta, fields, rows = {}, None, []
        for ln in lines:
            if not ln:
                continue
            if ln.startswith("#"):
                if ln.startswith("#separator"):
                    sep = _zeek_unescape(ln[len("#separator"):].strip()) or "\t"
                    continue
                key, _, val = ln[1:].partition(sep)
                if key == "fields":
                    fields = val.split(sep)
                    meta["fields"] = fields
                elif key == "types":
                    meta["types"] = val.split(sep)
                elif key == "set_separator":
                    setsep = val
                elif key == "empty_field":
                    empty = val
                elif key == "unset_field":
                    unset = val
                else:
                    meta[key] = val
                continue
            if not fields:
                continue
            vals = ln.split(sep)
            row = {}
            for k, v in zip(fields, vals):
                row[k] = None if v == unset else ("" if v == empty else v)
            rows.append(row)
        if fields is None:
            return None
        meta["set_separator"] = setsep
        return {"meta": meta, "rows": rows}
    objs = _json_lines(txt)
    if not objs:
        return None
    if any("event_type" in o for o in objs):        # Suricata eve, not Zeek
        return None
    if not all("ts" in o and ("uid" in o or "id.orig_h" in o or "_path" in o or "fuid" in o) for o in objs):
        return None
    rows = []
    for o in objs:
        r = {}
        for k, v in o.items():
            if isinstance(v, list):
                v = ",".join(str(x) for x in v)
            r[k] = None if v is None else str(v) if not isinstance(v, bool) else ("T" if v else "F")
        rows.append(r)
    meta = {}
    paths = {o.get("_path") for o in objs if o.get("_path")}
    if len(paths) == 1:
        meta["path"] = paths.pop()
    return {"meta": meta, "rows": rows}


_ZEEK = {
    "record_count": {"record_count", "row_count", "entry_count", "log_entry_count", "line_count", "records_count",
                     "number_of_records", "total_records", "num_records", "connection_count", "conn_count",
                     "log_record_count", "event_count", "data_line_count"},
    "path": {"path", "log_path", "log_type", "log_name"},
    "open": {"open", "open_time", "log_open_time", "open_timestamp"},
    "close": {"close", "close_time", "log_close_time", "close_timestamp"},
    "fields": {"fields", "field_names", "column_names", "columns"},
    "types": {"types", "field_types", "column_types"},
    "separator": {"separator", "field_separator"},
    "set_separator": {"set_separator"},
    "uid_count": {"unique_uid_count", "uid_count", "distinct_uid_count", "unique_uids_count"},
    "uids": {"uids", "unique_uids", "distinct_uids"},
    "orig_hosts": {"orig_hosts", "unique_orig_hosts", "orig_h_set", "id_orig_h_set", "unique_orig_h",
                   "unique_id_orig_h", "originator_hosts", "source_ips", "src_ips", "unique_src_ips",
                   "unique_source_ips"},
    "resp_hosts": {"resp_hosts", "unique_resp_hosts", "resp_h_set", "id_resp_h_set", "unique_resp_h",
                   "unique_id_resp_h", "responder_hosts", "destination_ips", "dst_ips", "unique_dst_ips",
                   "unique_destination_ips"},
    "orig_host_count": {"unique_orig_host_count", "orig_host_count", "unique_orig_h_count", "unique_src_ip_count",
                        "unique_source_ip_count", "src_ip_count"},
    "resp_host_count": {"unique_resp_host_count", "resp_host_count", "unique_resp_h_count", "unique_dst_ip_count",
                        "unique_destination_ip_count", "dst_ip_count"},
    "ips": {"unique_ips", "ip_addresses", "hosts", "unique_hosts"},
    "ip_count": {"unique_ip_count", "ip_count", "host_count", "unique_host_count"},
    "resp_ports": {"resp_ports", "unique_resp_ports", "id_resp_p_set", "dst_ports", "destination_ports",
                   "unique_dst_ports"},
    "services": {"services", "service_set", "unique_services", "service_names"},
    "protos": {"protos", "protocols", "proto_set", "unique_protocols", "transport_protocols"},
    "conn_states": {"conn_states", "conn_state_set", "unique_conn_states"},
    "orig_bytes": {"total_orig_bytes", "orig_bytes", "orig_bytes_total", "sum_orig_bytes", "bytes_sent"},
    "resp_bytes": {"total_resp_bytes", "resp_bytes", "resp_bytes_total", "sum_resp_bytes", "bytes_received"},
    "total_bytes": {"total_bytes", "bytes_total", "total_payload_bytes"},
    "orig_pkts": {"total_orig_pkts", "orig_pkts", "total_orig_packets"},
    "resp_pkts": {"total_resp_pkts", "resp_pkts", "total_resp_packets"},
    "dns_queries": {"dns_queries", "queries", "query_set", "unique_queries", "unique_dns_queries", "dns_query_set",
                    "query_names"},
    "dns_query_count": {"unique_dns_query_count", "unique_query_count", "dns_query_count"},
    "http_hosts": {"http_hosts", "hosts_http", "host_set", "unique_http_hosts", "http_host_set", "http_hostnames"},
    "http_host_count": {"unique_http_host_count", "http_host_count"},
    "http_uris": {"http_uris", "uris", "unique_uris"},
    "user_agents": {"user_agents", "http_user_agents", "unique_user_agents"},
    "first_ts": {"first_ts", "first_timestamp", "earliest_ts", "min_ts"},
    "last_ts": {"last_ts", "last_timestamp", "latest_ts", "max_ts"},
    "top_resp_host": {"top_resp_host", "top_destination_ip", "most_common_resp_h", "top_dst_ip"},
    "top_orig_host": {"top_orig_host", "top_source_ip", "most_common_orig_h", "top_src_ip"},
}


def zeek_value(data, ctx):
    if data is None:
        return None
    z = parse_zeek(data)
    if z is None:
        return "none"
    c = _canon(ctx.get("field"), _ZEEK)
    m, rows = z["meta"], z["rows"]
    col = lambda k: [r.get(k) for r in rows]  # noqa: E731
    orig, resp = col("id.orig_h"), col("id.resp_h")
    if c == "record_count":
        return len(rows)
    if c in ("path", "open", "close", "set_separator"):
        return m.get(c) or "none"
    if c == "separator":
        return "\\x09" if "fields" in m else "none"
    if c in ("fields", "types"):
        return list(m[c]) if c in m else "none"
    if c == "uid_count":
        return len(_sset(col("uid")))
    if c == "uids":
        return _sset(col("uid"))
    if c == "orig_hosts":
        return _sset(orig)
    if c == "resp_hosts":
        return _sset(resp)
    if c == "orig_host_count":
        return len(_sset(orig))
    if c == "resp_host_count":
        return len(_sset(resp))
    if c == "ips":
        return _sset(orig + resp)
    if c == "ip_count":
        return len(_sset(orig + resp))
    if c == "resp_ports":
        return _iset(v for v in col("id.resp_p") if v)
    if c == "services":
        return _sset(col("service"))
    if c == "protos":
        return _sset(col("proto"))
    if c == "conn_states":
        return _sset(col("conn_state"))
    if c == "orig_bytes":
        return _isum(col("orig_bytes"))
    if c == "resp_bytes":
        return _isum(col("resp_bytes"))
    if c == "total_bytes":
        return _isum(col("orig_bytes")) + _isum(col("resp_bytes"))
    if c == "orig_pkts":
        return _isum(col("orig_pkts"))
    if c == "resp_pkts":
        return _isum(col("resp_pkts"))
    if c == "dns_queries":
        return _sset(col("query"))
    if c == "dns_query_count":
        return len(_sset(col("query")))
    if c == "http_hosts":
        return _sset(col("host"))
    if c == "http_host_count":
        return len(_sset(col("host")))
    if c == "http_uris":
        return _sset(col("uri"))
    if c == "user_agents":
        return _sset(col("user_agent"))
    if c in ("first_ts", "last_ts"):
        ts = []
        for v in col("ts"):
            try:
                ts.append((float(v), v))
            except (TypeError, ValueError):
                pass
        if not ts:
            return "none"
        return (min(ts) if c == "first_ts" else max(ts))[1]
    if c == "top_resp_host":
        return _top(resp)
    if c == "top_orig_host":
        return _top(orig)
    return None


# -------------------------------------------------------------------------------------------------- suricata

def parse_eve(data):
    txt = _text(data)
    if txt is None:
        return None
    objs = _json_lines(txt)
    if not objs or not all(isinstance(o.get("event_type"), str) for o in objs):
        return None
    return objs


def _g(o, *path):
    for p in path:
        if not isinstance(o, dict):
            return None
        o = o.get(p)
    return o


_EVE = {
    "event_count": {"event_count", "record_count", "line_count", "entry_count", "events_count", "total_events",
                    "number_of_events", "row_count"},
    "event_types": {"event_types", "unique_event_types", "event_type_set"},
    "event_type_counts": {"event_type_counts", "events_by_type", "event_type_histogram"},
    "alert_count": {"alert_count", "alerts_count", "number_of_alerts", "total_alerts", "alert_event_count"},
    "signatures": {"alert_signatures", "signatures", "unique_signatures", "signature_names", "alert_signature_set",
                   "unique_alert_signatures", "alert_names"},
    "signature_count": {"unique_signature_count", "signature_count", "unique_alert_signature_count",
                        "distinct_signature_count"},
    "signature_ids": {"signature_ids", "alert_signature_ids", "sids", "unique_sids", "signature_id_set",
                      "unique_signature_ids"},
    "categories": {"alert_categories", "categories", "unique_categories"},
    "severities": {"alert_severities", "severities"},
    "top_signature": {"top_signature", "most_common_signature", "top_alert_signature", "most_frequent_signature"},
    "src_ips": {"src_ips", "source_ips", "unique_src_ips", "unique_source_ips"},
    "dest_ips": {"dest_ips", "dst_ips", "destination_ips", "unique_dest_ips", "unique_dst_ips",
                 "unique_destination_ips"},
    "src_ip_count": {"unique_src_ip_count", "src_ip_count", "unique_source_ip_count"},
    "dest_ip_count": {"unique_dest_ip_count", "unique_dst_ip_count", "dest_ip_count", "dst_ip_count"},
    "alert_src_ips": {"alert_src_ips", "alert_source_ips"},
    "alert_dest_ips": {"alert_dest_ips", "alert_dst_ips", "alert_destination_ips"},
    "dest_ports": {"dest_ports", "dst_ports", "destination_ports", "unique_dest_ports"},
    "protos": {"protos", "protocols", "proto_set", "unique_protocols"},
    "app_protos": {"app_protos", "app_protocols", "application_protocols"},
    "dns_queries": {"dns_queries", "dns_rrnames", "rrnames", "unique_dns_queries", "queries"},
    "http_hosts": {"http_hostnames", "http_hosts", "hostnames", "unique_http_hosts"},
    "tls_snis": {"tls_snis", "sni_set", "tls_sni", "snis", "unique_snis"},
    "flow_count": {"flow_count", "flow_event_count", "flows_count"},
    "first_ts": {"first_timestamp", "first_ts", "earliest_timestamp", "first_event_time"},
    "last_ts": {"last_timestamp", "last_ts", "latest_timestamp", "last_event_time"},
}


def suricata_value(data, ctx):
    if data is None:
        return None
    ev = parse_eve(data)
    if ev is None:
        return "none"
    c = _canon(ctx.get("field"), _EVE)
    al = [o for o in ev if o.get("event_type") == "alert"]
    typ = lambda t: [o for o in ev if o.get("event_type") == t]  # noqa: E731
    if c == "event_count":
        return len(ev)
    if c == "event_types":
        return _sset(o["event_type"] for o in ev)
    if c == "event_type_counts":
        return _counts(o["event_type"] for o in ev)
    if c == "alert_count":
        return len(al)
    if c == "signatures":
        return _sset(_g(o, "alert", "signature") for o in al)
    if c == "signature_count":
        return len(_sset(_g(o, "alert", "signature") for o in al))
    if c == "signature_ids":
        return _iset(_g(o, "alert", "signature_id") for o in al)
    if c == "categories":
        return _sset(_g(o, "alert", "category") for o in al)
    if c == "severities":
        return _iset(_g(o, "alert", "severity") for o in al)
    if c == "top_signature":
        return _top(_g(o, "alert", "signature") for o in al)
    if c == "src_ips":
        return _sset(o.get("src_ip") for o in ev)
    if c == "dest_ips":
        return _sset(o.get("dest_ip") for o in ev)
    if c == "src_ip_count":
        return len(_sset(o.get("src_ip") for o in ev))
    if c == "dest_ip_count":
        return len(_sset(o.get("dest_ip") for o in ev))
    if c == "alert_src_ips":
        return _sset(o.get("src_ip") for o in al)
    if c == "alert_dest_ips":
        return _sset(o.get("dest_ip") for o in al)
    if c == "dest_ports":
        return _iset(o.get("dest_port") for o in ev if o.get("dest_port") is not None)
    if c == "protos":
        return _sset(o.get("proto") for o in ev)
    if c == "app_protos":
        return _sset(o.get("app_proto") for o in ev)
    if c == "dns_queries":
        q = [_g(o, "dns", "rrname") for o in typ("dns")]
        for o in typ("dns"):                                  # eve v2 "queries": [{rrname}] (Suricata 7+)
            for qq in (_g(o, "dns", "queries") or []):
                if isinstance(qq, dict):
                    q.append(qq.get("rrname"))
        return _sset(q)
    if c == "http_hosts":
        return _sset(_g(o, "http", "hostname") for o in ev)
    if c == "tls_snis":
        return _sset(_g(o, "tls", "sni") for o in ev)
    if c == "flow_count":
        return len(typ("flow"))
    if c in ("first_ts", "last_ts"):
        ts = [o.get("timestamp") for o in ev if isinstance(o.get("timestamp"), str)]
        if not ts:
            return "none"
        return min(ts) if c == "first_ts" else max(ts)
    return None


# --------------------------------------------------------------------------------------------------- netflow

def _udp_payloads(b):
    """NetFlow-looking UDP payloads of a pcap/pcapng, or None (not a capture)."""
    if b[:4] not in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d",
                     b"\x0a\x0d\x0d\x0a"):
        return None
    try:
        import dpkt
        rd = dpkt.pcapng.Reader(io.BytesIO(b)) if b[:4] == b"\x0a\x0d\x0d\x0a" else dpkt.pcap.Reader(io.BytesIO(b))
        dl = rd.datalink()
        out = []
        for _ts, buf in rd:
            try:
                if dl == 1:
                    ip = dpkt.ethernet.Ethernet(buf).data
                elif dl in (101, 12, 14, 228, 229):
                    ip = dpkt.ip.IP(buf) if buf[:1] and buf[0] >> 4 == 4 else dpkt.ip6.IP6(buf)
                elif dl == 113:
                    ip = dpkt.sll.SLL(buf).data
                else:
                    continue
                udp = getattr(ip, "data", None)
                if isinstance(udp, dpkt.udp.UDP):
                    p = bytes(udp.data)
                    if len(p) >= 16 and struct.unpack(">H", p[:2])[0] in (5, 9, 10):
                        out.append(p)
            except (dpkt.dpkt.Error, struct.error, ValueError, AttributeError):
                continue
        return out
    except Exception:  # noqa: BLE001  (a damaged capture -> treat as no exports)
        return []


def _ipstr(raw):
    try:
        return str(ipaddress.ip_address(raw))
    except ValueError:
        return None


# IE -> flow key (v9 and IPFIX share 1..~80)
_IE = {1: "bytes", 2: "pkts", 4: "prot", 7: "sport", 8: "src", 11: "dport", 12: "dst", 27: "src", 28: "dst",
       85: "bytes", 86: "pkts", 6: "tcp_flags", 10: "input", 14: "output"}


def _decode_rec(tpl, body, off):
    """(flow dict, new offset) for one data record of template `tpl` [(ie, len, pen)], or (None, off)."""
    f = {}
    for ie, ln, pen in tpl:
        if ln == 0xFFFF:                         # IPFIX variable length
            if off >= len(body):
                return None, off
            ln = body[off]
            off += 1
            if ln == 255:
                if off + 2 > len(body):
                    return None, off
                ln = struct.unpack_from(">H", body, off)[0]
                off += 2
        if off + ln > len(body):
            return None, off
        v = body[off:off + ln]
        off += ln
        k = _IE.get(ie) if pen is None else None
        if k in ("src", "dst"):
            if ln in (4, 16):
                f[k] = _ipstr(v)
        elif k:
            f[k] = int.from_bytes(v, "big")
    return f, off


def parse_netflow(data):
    """{"version", "packets": [header dicts], "flows": [dicts], "header_count"} or None (not NetFlow)."""
    if not isinstance(data, (bytes, bytearray)) or len(data) < 16:
        return None
    b = bytes(data)
    pkts = _udp_payloads(b)
    if pkts is None:
        pkts, off = [], 0
        while off + 16 <= len(b):              # split a raw stream into export packets
            ver = struct.unpack_from(">H", b, off)[0]
            if ver == 5:
                cnt = struct.unpack_from(">H", b, off + 2)[0]
                ln = 24 + 48 * cnt
                if not 1 <= cnt <= 30 or off + ln > len(b):
                    break
            elif ver == 10:
                ln = struct.unpack_from(">H", b, off + 2)[0]
                if ln < 16 or off + ln > len(b):
                    break
            elif ver == 9:
                p = off + 20                     # FlowSet ids 2..255 are reserved: id 9 = the next v9 header
                while p + 4 <= len(b):
                    sid, sl = struct.unpack_from(">HH", b, p)
                    if sid == 9 or sl < 4 or p + sl > len(b):
                        break
                    p += sl
                ln = p - off
            else:
                break
            pkts.append(b[off:off + ln])
            off += ln
        if not pkts or off != len(b):
            return None
    if not pkts:
        return None
    versions = {struct.unpack(">H", p[:2])[0] for p in pkts}
    if len(versions) != 1:
        return None
    ver = versions.pop()
    heads, flows, templates, hcount = [], [], {}, 0
    for p in pkts:
        if ver == 5:
            if len(p) < 24:
                return None
            cnt, up, secs, nsecs, seq, et, eid, smp = struct.unpack_from(">HIIIIBBH", p, 2)
            heads.append({"count": cnt, "sys_uptime": up, "unix_secs": secs, "unix_nsecs": nsecs,
                          "flow_sequence": seq, "engine_type": et, "engine_id": eid,
                          "sampling_interval": smp & 0x3FFF})
            hcount += cnt
            for i in range(cnt):
                o = 24 + 48 * i
                if o + 48 > len(p):
                    return None
                r = struct.unpack_from(">4s4s4sHHIIIIHHBBBBHHBBH", p, o)
                flows.append({"src": _ipstr(r[0]), "dst": _ipstr(r[1]), "nexthop": _ipstr(r[2]), "input": r[3],
                              "output": r[4], "pkts": r[5], "bytes": r[6], "first": r[7], "last": r[8],
                              "sport": r[9], "dport": r[10], "tcp_flags": r[12], "prot": r[13], "tos": r[14]})
            continue
        if ver == 9:
            cnt, up, secs, seq, src_id = struct.unpack_from(">HIIII", p, 2)
            heads.append({"count": cnt, "sys_uptime": up, "unix_secs": secs, "flow_sequence": seq,
                          "source_id": src_id})
            hcount += cnt
            off, tset = 20, 0
        else:
            ln, secs, seq, dom = struct.unpack_from(">HIII", p, 2)
            heads.append({"length": ln, "unix_secs": secs, "flow_sequence": seq, "source_id": dom})
            off, tset = 16, 2
        while off + 4 <= len(p):
            sid, sl = struct.unpack_from(">HH", p, off)
            if sl < 4 or off + sl > len(p):
                break
            body = p[off + 4:off + sl]
            if sid == tset:
                q = 0
                while q + 4 <= len(body):
                    tid, fc = struct.unpack_from(">HH", body, q)
                    q += 4
                    if tid < 256:
                        break
                    tpl = []
                    for _ in range(fc):
                        if q + 4 > len(body):
                            break
                        ie, fl = struct.unpack_from(">HH", body, q)
                        q += 4
                        pen = None
                        if ver == 10 and ie & 0x8000:
                            pen = struct.unpack_from(">I", body, q)[0] if q + 4 <= len(body) else 0
                            q += 4
                            ie &= 0x7FFF
                        tpl.append((ie, fl, pen))
                    templates[tid] = tpl
            elif sid >= 256 and sid in templates:
                tpl = templates[sid]
                fixed = sum(fl for _, fl, _ in tpl if fl != 0xFFFF)
                q = 0
                minlen = max(fixed, 1)
                while q + minlen <= len(body):
                    f, q2 = _decode_rec(tpl, body, q)
                    if f is None or q2 == q:
                        break
                    flows.append(f)
                    q = q2
            off += sl
    return {"version": ver, "packets": heads, "flows": flows, "header_count": hcount}


_NF = {
    "version": {"version", "netflow_version", "export_version", "header_version"},
    "record_count": {"record_count", "flow_count", "flow_record_count", "number_of_records", "records_count",
                     "num_records", "total_records", "number_of_flows", "flows_count", "data_record_count",
                     "entry_count", "row_count"},
    "header_count": {"header_count", "count", "header_record_count", "count_field", "header_flow_count"},
    "packet_count": {"packet_count", "export_packet_count", "export_count", "pdu_count", "datagram_count",
                     "number_of_packets", "number_of_exports"},
    "total_packets": {"total_packets", "total_dpkts", "dpkts_total", "sum_dpkts", "packets_total", "total_pkts",
                      "flow_packets_total"},
    "total_bytes": {"total_bytes", "total_doctets", "doctets_total", "sum_doctets", "bytes_total", "octets_total",
                    "total_octets"},
    "dst_ips": {"unique_dst_ips", "dst_ips", "unique_destination_ips", "destination_ips", "dstaddrs",
                "unique_dstaddrs", "dstaddr_set"},
    "src_ips": {"unique_src_ips", "src_ips", "unique_source_ips", "source_ips", "srcaddrs", "unique_srcaddrs",
                "srcaddr_set"},
    "dst_ip_count": {"unique_dst_ip_count", "unique_dst_count", "dst_ip_count", "unique_destination_count",
                     "unique_destination_ip_count", "unique_dstaddr_count", "unique_dst"},
    "src_ip_count": {"unique_src_ip_count", "unique_src_count", "src_ip_count", "unique_source_count",
                     "unique_source_ip_count", "unique_srcaddr_count", "unique_src"},
    "dst_ports": {"dst_ports", "unique_dst_ports", "dstports", "destination_ports"},
    "src_ports": {"src_ports", "unique_src_ports", "srcports", "source_ports"},
    "protocols": {"protocols", "protocol_numbers", "prot_set", "unique_protocols", "ip_protocols"},
    "sys_uptime": {"sys_uptime", "sysuptime", "system_uptime", "uptime_ms"},
    "unix_secs": {"unix_secs", "unix_seconds", "export_time", "export_time_unix", "export_timestamp"},
    "export_time_utc": {"export_time_utc", "unix_secs_utc", "header_time_utc", "export_timestamp_utc"},
    "unix_nsecs": {"unix_nsecs"},
    "flow_sequence": {"flow_sequence", "sequence", "sequence_number", "package_sequence"},
    "engine_type": {"engine_type"},
    "engine_id": {"engine_id"},
    "sampling_interval": {"sampling_interval"},
    "source_id": {"source_id", "observation_domain_id", "domain_id"},
    "top_dst_ip": {"top_dst_ip", "top_destination_ip", "most_common_dst_ip"},
    "top_src_ip": {"top_src_ip", "top_source_ip", "most_common_src_ip", "top_talker_ip", "top_talker"},
}


def netflow_value(data, ctx):
    if data is None:
        return None
    nf = parse_netflow(data)
    if nf is None:
        return "none"
    c = _canon(ctx.get("field"), _NF)
    fl, h0 = nf["flows"], nf["packets"][0]
    if c == "version":
        return nf["version"]
    if c == "record_count":
        return len(fl)
    if c == "header_count":
        return nf["header_count"] if nf["version"] != 10 else "none"
    if c == "packet_count":
        return len(nf["packets"])
    if c == "total_packets":
        return sum(f.get("pkts", 0) for f in fl)
    if c == "total_bytes":
        return sum(f.get("bytes", 0) for f in fl)
    if c == "dst_ips":
        return _sset(f.get("dst") for f in fl)
    if c == "src_ips":
        return _sset(f.get("src") for f in fl)
    if c == "dst_ip_count":
        return len(_sset(f.get("dst") for f in fl))
    if c == "src_ip_count":
        return len(_sset(f.get("src") for f in fl))
    if c == "dst_ports":
        return _iset(f.get("dport") for f in fl if "dport" in f)
    if c == "src_ports":
        return _iset(f.get("sport") for f in fl if "sport" in f)
    if c == "protocols":
        return _iset(f.get("prot") for f in fl if "prot" in f)
    if c == "export_time_utc":
        return datetime.datetime.fromtimestamp(h0["unix_secs"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if c == "top_dst_ip":
        return _top(f.get("dst") for f in fl)
    if c == "top_src_ip":
        return _top(f.get("src") for f in fl)
    if c in h0:
        return h0[c]
    if c is not None:
        return "none"
    return None


# ------------------------------------------------------------------------------------------ Wireshark CSV

def _csv_rows(txt):
    """RFC 4180 rows (quoted fields, "" escape, newlines inside quotes)."""
    rows, row, fld, q, i, n = [], [], [], False, 0, len(txt)
    while i < n:
        ch = txt[i]
        if q:
            if ch == '"':
                if i + 1 < n and txt[i + 1] == '"':
                    fld.append('"')
                    i += 1
                else:
                    q = False
            else:
                fld.append(ch)
        elif ch == '"':
            q = True
        elif ch == ",":
            row.append("".join(fld))
            fld = []
        elif ch in "\r\n":
            if ch == "\r" and i + 1 < n and txt[i + 1] == "\n":
                i += 1
            row.append("".join(fld))
            fld = []
            if any(x != "" for x in row):
                rows.append(row)
            row = []
        else:
            fld.append(ch)
        i += 1
    if fld or row:
        row.append("".join(fld))
        if any(x != "" for x in row):
            rows.append(row)
    return rows


def parse_ws_csv(data):
    txt = _text(data)
    if txt is None:
        return None
    rows = _csv_rows(txt)
    if len(rows) < 1:
        return None
    hdr = [h.strip() for h in rows[0]]
    if "No." not in hdr or "Protocol" not in hdr or not ({"Source", "Destination"} & set(hdr)):
        return None
    out = []
    for r in rows[1:]:
        out.append({h: (r[i] if i < len(r) else "") for i, h in enumerate(hdr)})
    return out


_CSV = {
    "row_count": {"row_count", "packet_count", "record_count", "frame_count", "number_of_packets", "packets",
                  "entry_count", "line_count", "num_packets", "total_packets", "rows_count"},
    "protocols": {"protocols", "unique_protocols", "protocol_set", "protocol_names", "distinct_protocols"},
    "protocol_count": {"protocol_count", "unique_protocol_count", "distinct_protocol_count"},
    "protocol_counts": {"protocol_counts", "packets_per_protocol", "protocol_histogram", "protocol_hierarchy"},
    "top_protocol": {"top_protocol", "most_common_protocol", "most_frequent_protocol", "dominant_protocol"},
    "sources": {"sources", "unique_sources", "source_set", "unique_source_addresses", "source_addresses",
                "unique_src_ips", "src_ips", "source_ips"},
    "destinations": {"destinations", "unique_destinations", "destination_set", "unique_destination_addresses",
                     "destination_addresses", "unique_dst_ips", "dst_ips", "destination_ips"},
    "endpoints": {"unique_ips", "endpoints", "unique_addresses", "addresses"},
    "endpoint_count": {"unique_ip_count", "endpoint_count", "unique_address_count"},
    "total_length": {"total_length", "total_bytes", "length_total", "sum_length", "bytes_total", "total_frame_length"},
    "max_length": {"max_length", "largest_frame", "max_frame_length"},
    "first_time": {"first_time", "first_timestamp"},
    "last_time": {"last_time", "last_timestamp", "duration", "capture_duration"},
    "columns": {"columns", "column_names", "header", "header_columns", "fields", "field_names"},
    "last_number": {"last_frame_number", "last_no", "max_frame_number"},
    "top_source": {"top_source", "top_talker", "top_source_ip", "most_common_source"},
    "top_destination": {"top_destination", "top_destination_ip", "most_common_destination"},
}


def csv_flows_value(data, ctx):
    if data is None:
        return None
    rows = parse_ws_csv(data)
    if rows is None:
        return "none"
    c = _canon(ctx.get("field"), _CSV)
    col = lambda k: [r.get(k, "") for r in rows]  # noqa: E731
    if c == "row_count":
        return len(rows)
    if c == "protocols":
        return _sset(col("Protocol"))
    if c == "protocol_count":
        return len(_sset(col("Protocol")))
    if c == "protocol_counts":
        return _counts(col("Protocol"))
    if c == "top_protocol":
        return _top(col("Protocol"))
    if c == "sources":
        return _sset(col("Source"))
    if c == "destinations":
        return _sset(col("Destination"))
    if c == "endpoints":
        return _sset(col("Source") + col("Destination"))
    if c == "endpoint_count":
        return len(_sset(col("Source") + col("Destination")))
    if c == "total_length":
        return _isum(col("Length"))
    if c == "max_length":
        v = _iset(col("Length"))
        return v[-1] if v else "none"
    if c in ("first_time", "last_time"):
        t = [x for x in col("Time") if x]
        if not t:
            return "none"
        return t[0] if c == "first_time" else t[-1]
    if c == "columns":
        return list(rows[0].keys()) if rows else "none"
    if c == "last_number":
        v = _iset(col("No."))
        return v[-1] if v else "none"
    if c == "top_source":
        return _top(col("Source"))
    if c == "top_destination":
        return _top(col("Destination"))
    return None


# ------------------------------------------------------------------------------- Windows Firewall pfirewall.log

def parse_pfirewall(data):
    txt = _text(data)
    if txt is None:
        return None
    meta, fields, rows = {}, None, []
    for ln in txt.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            k, _, v = s[1:].partition(":")
            k, v = k.strip().lower(), v.strip()
            if k == "fields":
                fields = v.split()
            else:
                meta[k] = v
            continue
        if not fields:
            continue
        vals = s.split()
        rows.append({f: (vals[i] if i < len(vals) and vals[i] != "-" else None) for i, f in enumerate(fields)})
    if not fields or "action" not in fields or "src-ip" not in fields or "dst-ip" not in fields:
        return None
    return {"meta": meta, "fields": fields, "rows": rows}


_FW = {
    "record_count": {"record_count", "row_count", "entry_count", "line_count", "event_count", "log_entry_count",
                     "number_of_records", "total_records", "num_records", "connection_count"},
    "drop_count": {"drop_count", "dropped_count", "drops", "blocked_count", "block_count", "denied_count",
                   "drop_entries", "dropped_connections"},
    "allow_count": {"allow_count", "allowed_count", "allows", "permitted_count", "accept_count", "allowed_connections"},
    "action_counts": {"action_counts", "actions_count", "counts_by_action"},
    "actions": {"actions", "unique_actions", "action_set"},
    "dst_ips": {"unique_dst_ips", "dst_ips", "unique_destination_ips", "destination_ips", "unique_dst"},
    "src_ips": {"unique_src_ips", "src_ips", "unique_source_ips", "source_ips", "unique_src"},
    "dst_ip_count": {"unique_dst_ip_count", "dst_ip_count", "unique_destination_ip_count", "unique_dst_count",
                     "unique_destination_count"},
    "src_ip_count": {"unique_src_ip_count", "src_ip_count", "unique_source_ip_count", "unique_src_count"},
    "drop_dst_ips": {"dropped_dst_ips", "drop_dst_ips", "blocked_dst_ips", "dropped_destination_ips"},
    "drop_src_ips": {"dropped_src_ips", "drop_src_ips", "blocked_src_ips", "dropped_source_ips"},
    "dst_ports": {"dst_ports", "unique_dst_ports", "destination_ports"},
    "drop_dst_ports": {"dropped_dst_ports", "drop_dst_ports", "blocked_ports", "blocked_dst_ports"},
    "src_ports": {"src_ports", "unique_src_ports", "source_ports"},
    "protocols": {"protocols", "unique_protocols", "protocol_set"},
    "paths": {"paths", "directions", "path_set"},
    "send_count": {"send_count", "outbound_count"},
    "receive_count": {"receive_count", "inbound_count"},
    "total_size": {"total_size", "total_bytes", "size_total"},
    "version": {"version", "log_version", "w3c_version"},
    "software": {"software", "log_software"},
    "time_format": {"time_format", "timestamp_format"},
    "fields": {"fields", "field_names", "columns", "column_names"},
    "first_ts": {"first_timestamp", "first_time", "first_entry_time", "earliest_timestamp"},
    "last_ts": {"last_timestamp", "last_time", "last_entry_time", "latest_timestamp"},
    "top_dst_ip": {"top_dst_ip", "top_destination_ip", "most_common_dst_ip"},
    "top_src_ip": {"top_src_ip", "top_source_ip", "most_common_src_ip", "top_talker"},
    "top_dropped_src_ip": {"top_dropped_src_ip", "most_dropped_src_ip", "top_blocked_source_ip"},
}


def firewall_log_value(data, ctx):
    if data is None:
        return None
    fw = parse_pfirewall(data)
    if fw is None:
        return "none"
    c = _canon(ctx.get("field"), _FW)
    rows, meta = fw["rows"], fw["meta"]
    col = lambda k, rs=rows: [r.get(k) for r in rs]  # noqa: E731
    act = lambda a: [r for r in rows if (r.get("action") or "").upper() == a]  # noqa: E731
    drops = act("DROP")
    if c == "record_count":
        return len(rows)
    if c == "drop_count":
        return len(drops)
    if c == "allow_count":
        return len(act("ALLOW"))
    if c == "action_counts":
        return _counts(col("action"))
    if c == "actions":
        return _sset(col("action"))
    if c == "dst_ips":
        return _sset(col("dst-ip"))
    if c == "src_ips":
        return _sset(col("src-ip"))
    if c == "dst_ip_count":
        return len(_sset(col("dst-ip")))
    if c == "src_ip_count":
        return len(_sset(col("src-ip")))
    if c == "drop_dst_ips":
        return _sset(col("dst-ip", drops))
    if c == "drop_src_ips":
        return _sset(col("src-ip", drops))
    if c == "dst_ports":
        return _iset(col("dst-port"))
    if c == "drop_dst_ports":
        return _iset(col("dst-port", drops))
    if c == "src_ports":
        return _iset(col("src-port"))
    if c == "protocols":
        return _sset(col("protocol"))
    if c == "paths":
        return _sset(col("path"))
    if c == "send_count":
        return sum(1 for v in col("path") if (v or "").upper() == "SEND")
    if c == "receive_count":
        return sum(1 for v in col("path") if (v or "").upper() == "RECEIVE")
    if c == "total_size":
        return _isum(col("size"))
    if c in ("version", "software", "time_format"):
        return meta.get(c.replace("_", " ")) or "none"
    if c == "fields":
        return list(fw["fields"])
    if c in ("first_ts", "last_ts"):
        ts = [f"{r.get('date')} {r.get('time')}" for r in rows if r.get("date") and r.get("time")]
        if not ts:
            return "none"
        return min(ts) if c == "first_ts" else max(ts)
    if c == "top_dst_ip":
        return _top(col("dst-ip"))
    if c == "top_src_ip":
        return _top(col("src-ip"))
    if c == "top_dropped_src_ip":
        return _top(col("src-ip", drops))
    return None


# FIELDS: generated from the alias tables above (literal, read with ast by lib.meta).
FIELDS = {
    # zeek
    ("zeek", "bytes_received"): "zeek_value",
    ("zeek", "bytes_sent"): "zeek_value",
    ("zeek", "bytes_total"): "zeek_value",
    ("zeek", "close"): "zeek_value",
    ("zeek", "close_time"): "zeek_value",
    ("zeek", "close_timestamp"): "zeek_value",
    ("zeek", "column_names"): "zeek_value",
    ("zeek", "column_types"): "zeek_value",
    ("zeek", "columns"): "zeek_value",
    ("zeek", "conn_count"): "zeek_value",
    ("zeek", "conn_state_set"): "zeek_value",
    ("zeek", "conn_states"): "zeek_value",
    ("zeek", "connection_count"): "zeek_value",
    ("zeek", "data_line_count"): "zeek_value",
    ("zeek", "destination_ips"): "zeek_value",
    ("zeek", "destination_ports"): "zeek_value",
    ("zeek", "distinct_uid_count"): "zeek_value",
    ("zeek", "distinct_uids"): "zeek_value",
    ("zeek", "dns_queries"): "zeek_value",
    ("zeek", "dns_query_count"): "zeek_value",
    ("zeek", "dns_query_set"): "zeek_value",
    ("zeek", "dst_ip_count"): "zeek_value",
    ("zeek", "dst_ips"): "zeek_value",
    ("zeek", "dst_ports"): "zeek_value",
    ("zeek", "earliest_ts"): "zeek_value",
    ("zeek", "entry_count"): "zeek_value",
    ("zeek", "event_count"): "zeek_value",
    ("zeek", "field_names"): "zeek_value",
    ("zeek", "field_separator"): "zeek_value",
    ("zeek", "field_types"): "zeek_value",
    ("zeek", "fields"): "zeek_value",
    ("zeek", "first_timestamp"): "zeek_value",
    ("zeek", "first_ts"): "zeek_value",
    ("zeek", "host_count"): "zeek_value",
    ("zeek", "host_set"): "zeek_value",
    ("zeek", "hosts"): "zeek_value",
    ("zeek", "hosts_http"): "zeek_value",
    ("zeek", "http_host_count"): "zeek_value",
    ("zeek", "http_host_set"): "zeek_value",
    ("zeek", "http_hostnames"): "zeek_value",
    ("zeek", "http_hosts"): "zeek_value",
    ("zeek", "http_uris"): "zeek_value",
    ("zeek", "http_user_agents"): "zeek_value",
    ("zeek", "id_orig_h_set"): "zeek_value",
    ("zeek", "id_resp_h_set"): "zeek_value",
    ("zeek", "id_resp_p_set"): "zeek_value",
    ("zeek", "ip_addresses"): "zeek_value",
    ("zeek", "ip_count"): "zeek_value",
    ("zeek", "last_timestamp"): "zeek_value",
    ("zeek", "last_ts"): "zeek_value",
    ("zeek", "latest_ts"): "zeek_value",
    ("zeek", "line_count"): "zeek_value",
    ("zeek", "log_close_time"): "zeek_value",
    ("zeek", "log_entry_count"): "zeek_value",
    ("zeek", "log_name"): "zeek_value",
    ("zeek", "log_open_time"): "zeek_value",
    ("zeek", "log_path"): "zeek_value",
    ("zeek", "log_record_count"): "zeek_value",
    ("zeek", "log_type"): "zeek_value",
    ("zeek", "max_ts"): "zeek_value",
    ("zeek", "min_ts"): "zeek_value",
    ("zeek", "most_common_orig_h"): "zeek_value",
    ("zeek", "most_common_resp_h"): "zeek_value",
    ("zeek", "num_records"): "zeek_value",
    ("zeek", "number_of_records"): "zeek_value",
    ("zeek", "open"): "zeek_value",
    ("zeek", "open_time"): "zeek_value",
    ("zeek", "open_timestamp"): "zeek_value",
    ("zeek", "orig_bytes"): "zeek_value",
    ("zeek", "orig_bytes_total"): "zeek_value",
    ("zeek", "orig_h_set"): "zeek_value",
    ("zeek", "orig_host_count"): "zeek_value",
    ("zeek", "orig_hosts"): "zeek_value",
    ("zeek", "orig_pkts"): "zeek_value",
    ("zeek", "originator_hosts"): "zeek_value",
    ("zeek", "path"): "zeek_value",
    ("zeek", "proto_set"): "zeek_value",
    ("zeek", "protocols"): "zeek_value",
    ("zeek", "protos"): "zeek_value",
    ("zeek", "queries"): "zeek_value",
    ("zeek", "query_names"): "zeek_value",
    ("zeek", "query_set"): "zeek_value",
    ("zeek", "record_count"): "zeek_value",
    ("zeek", "records_count"): "zeek_value",
    ("zeek", "resp_bytes"): "zeek_value",
    ("zeek", "resp_bytes_total"): "zeek_value",
    ("zeek", "resp_h_set"): "zeek_value",
    ("zeek", "resp_host_count"): "zeek_value",
    ("zeek", "resp_hosts"): "zeek_value",
    ("zeek", "resp_pkts"): "zeek_value",
    ("zeek", "resp_ports"): "zeek_value",
    ("zeek", "responder_hosts"): "zeek_value",
    ("zeek", "row_count"): "zeek_value",
    ("zeek", "separator"): "zeek_value",
    ("zeek", "service_names"): "zeek_value",
    ("zeek", "service_set"): "zeek_value",
    ("zeek", "services"): "zeek_value",
    ("zeek", "set_separator"): "zeek_value",
    ("zeek", "source_ips"): "zeek_value",
    ("zeek", "src_ip_count"): "zeek_value",
    ("zeek", "src_ips"): "zeek_value",
    ("zeek", "sum_orig_bytes"): "zeek_value",
    ("zeek", "sum_resp_bytes"): "zeek_value",
    ("zeek", "top_destination_ip"): "zeek_value",
    ("zeek", "top_dst_ip"): "zeek_value",
    ("zeek", "top_orig_host"): "zeek_value",
    ("zeek", "top_resp_host"): "zeek_value",
    ("zeek", "top_source_ip"): "zeek_value",
    ("zeek", "top_src_ip"): "zeek_value",
    ("zeek", "total_bytes"): "zeek_value",
    ("zeek", "total_orig_bytes"): "zeek_value",
    ("zeek", "total_orig_packets"): "zeek_value",
    ("zeek", "total_orig_pkts"): "zeek_value",
    ("zeek", "total_payload_bytes"): "zeek_value",
    ("zeek", "total_records"): "zeek_value",
    ("zeek", "total_resp_bytes"): "zeek_value",
    ("zeek", "total_resp_packets"): "zeek_value",
    ("zeek", "total_resp_pkts"): "zeek_value",
    ("zeek", "transport_protocols"): "zeek_value",
    ("zeek", "types"): "zeek_value",
    ("zeek", "uid_count"): "zeek_value",
    ("zeek", "uids"): "zeek_value",
    ("zeek", "unique_conn_states"): "zeek_value",
    ("zeek", "unique_destination_ip_count"): "zeek_value",
    ("zeek", "unique_destination_ips"): "zeek_value",
    ("zeek", "unique_dns_queries"): "zeek_value",
    ("zeek", "unique_dns_query_count"): "zeek_value",
    ("zeek", "unique_dst_ip_count"): "zeek_value",
    ("zeek", "unique_dst_ips"): "zeek_value",
    ("zeek", "unique_dst_ports"): "zeek_value",
    ("zeek", "unique_host_count"): "zeek_value",
    ("zeek", "unique_hosts"): "zeek_value",
    ("zeek", "unique_http_host_count"): "zeek_value",
    ("zeek", "unique_http_hosts"): "zeek_value",
    ("zeek", "unique_id_orig_h"): "zeek_value",
    ("zeek", "unique_id_resp_h"): "zeek_value",
    ("zeek", "unique_ip_count"): "zeek_value",
    ("zeek", "unique_ips"): "zeek_value",
    ("zeek", "unique_orig_h"): "zeek_value",
    ("zeek", "unique_orig_h_count"): "zeek_value",
    ("zeek", "unique_orig_host_count"): "zeek_value",
    ("zeek", "unique_orig_hosts"): "zeek_value",
    ("zeek", "unique_protocols"): "zeek_value",
    ("zeek", "unique_queries"): "zeek_value",
    ("zeek", "unique_query_count"): "zeek_value",
    ("zeek", "unique_resp_h"): "zeek_value",
    ("zeek", "unique_resp_h_count"): "zeek_value",
    ("zeek", "unique_resp_host_count"): "zeek_value",
    ("zeek", "unique_resp_hosts"): "zeek_value",
    ("zeek", "unique_resp_ports"): "zeek_value",
    ("zeek", "unique_services"): "zeek_value",
    ("zeek", "unique_source_ip_count"): "zeek_value",
    ("zeek", "unique_source_ips"): "zeek_value",
    ("zeek", "unique_src_ip_count"): "zeek_value",
    ("zeek", "unique_src_ips"): "zeek_value",
    ("zeek", "unique_uid_count"): "zeek_value",
    ("zeek", "unique_uids"): "zeek_value",
    ("zeek", "unique_uids_count"): "zeek_value",
    ("zeek", "unique_uris"): "zeek_value",
    ("zeek", "unique_user_agents"): "zeek_value",
    ("zeek", "uris"): "zeek_value",
    ("zeek", "user_agents"): "zeek_value",
    # suricata
    ("suricata", "alert_categories"): "suricata_value",
    ("suricata", "alert_count"): "suricata_value",
    ("suricata", "alert_dest_ips"): "suricata_value",
    ("suricata", "alert_destination_ips"): "suricata_value",
    ("suricata", "alert_dst_ips"): "suricata_value",
    ("suricata", "alert_event_count"): "suricata_value",
    ("suricata", "alert_names"): "suricata_value",
    ("suricata", "alert_severities"): "suricata_value",
    ("suricata", "alert_signature_ids"): "suricata_value",
    ("suricata", "alert_signature_set"): "suricata_value",
    ("suricata", "alert_signatures"): "suricata_value",
    ("suricata", "alert_source_ips"): "suricata_value",
    ("suricata", "alert_src_ips"): "suricata_value",
    ("suricata", "alerts_count"): "suricata_value",
    ("suricata", "app_protocols"): "suricata_value",
    ("suricata", "app_protos"): "suricata_value",
    ("suricata", "application_protocols"): "suricata_value",
    ("suricata", "categories"): "suricata_value",
    ("suricata", "dest_ip_count"): "suricata_value",
    ("suricata", "dest_ips"): "suricata_value",
    ("suricata", "dest_ports"): "suricata_value",
    ("suricata", "destination_ips"): "suricata_value",
    ("suricata", "destination_ports"): "suricata_value",
    ("suricata", "distinct_signature_count"): "suricata_value",
    ("suricata", "dns_queries"): "suricata_value",
    ("suricata", "dns_rrnames"): "suricata_value",
    ("suricata", "dst_ip_count"): "suricata_value",
    ("suricata", "dst_ips"): "suricata_value",
    ("suricata", "dst_ports"): "suricata_value",
    ("suricata", "earliest_timestamp"): "suricata_value",
    ("suricata", "entry_count"): "suricata_value",
    ("suricata", "event_count"): "suricata_value",
    ("suricata", "event_type_counts"): "suricata_value",
    ("suricata", "event_type_histogram"): "suricata_value",
    ("suricata", "event_type_set"): "suricata_value",
    ("suricata", "event_types"): "suricata_value",
    ("suricata", "events_by_type"): "suricata_value",
    ("suricata", "events_count"): "suricata_value",
    ("suricata", "first_event_time"): "suricata_value",
    ("suricata", "first_timestamp"): "suricata_value",
    ("suricata", "first_ts"): "suricata_value",
    ("suricata", "flow_count"): "suricata_value",
    ("suricata", "flow_event_count"): "suricata_value",
    ("suricata", "flows_count"): "suricata_value",
    ("suricata", "hostnames"): "suricata_value",
    ("suricata", "http_hostnames"): "suricata_value",
    ("suricata", "http_hosts"): "suricata_value",
    ("suricata", "last_event_time"): "suricata_value",
    ("suricata", "last_timestamp"): "suricata_value",
    ("suricata", "last_ts"): "suricata_value",
    ("suricata", "latest_timestamp"): "suricata_value",
    ("suricata", "line_count"): "suricata_value",
    ("suricata", "most_common_signature"): "suricata_value",
    ("suricata", "most_frequent_signature"): "suricata_value",
    ("suricata", "number_of_alerts"): "suricata_value",
    ("suricata", "number_of_events"): "suricata_value",
    ("suricata", "proto_set"): "suricata_value",
    ("suricata", "protocols"): "suricata_value",
    ("suricata", "protos"): "suricata_value",
    ("suricata", "queries"): "suricata_value",
    ("suricata", "record_count"): "suricata_value",
    ("suricata", "row_count"): "suricata_value",
    ("suricata", "rrnames"): "suricata_value",
    ("suricata", "severities"): "suricata_value",
    ("suricata", "sids"): "suricata_value",
    ("suricata", "signature_count"): "suricata_value",
    ("suricata", "signature_id_set"): "suricata_value",
    ("suricata", "signature_ids"): "suricata_value",
    ("suricata", "signature_names"): "suricata_value",
    ("suricata", "signatures"): "suricata_value",
    ("suricata", "sni_set"): "suricata_value",
    ("suricata", "snis"): "suricata_value",
    ("suricata", "source_ips"): "suricata_value",
    ("suricata", "src_ip_count"): "suricata_value",
    ("suricata", "src_ips"): "suricata_value",
    ("suricata", "tls_sni"): "suricata_value",
    ("suricata", "tls_snis"): "suricata_value",
    ("suricata", "top_alert_signature"): "suricata_value",
    ("suricata", "top_signature"): "suricata_value",
    ("suricata", "total_alerts"): "suricata_value",
    ("suricata", "total_events"): "suricata_value",
    ("suricata", "unique_alert_signature_count"): "suricata_value",
    ("suricata", "unique_alert_signatures"): "suricata_value",
    ("suricata", "unique_categories"): "suricata_value",
    ("suricata", "unique_dest_ip_count"): "suricata_value",
    ("suricata", "unique_dest_ips"): "suricata_value",
    ("suricata", "unique_dest_ports"): "suricata_value",
    ("suricata", "unique_destination_ips"): "suricata_value",
    ("suricata", "unique_dns_queries"): "suricata_value",
    ("suricata", "unique_dst_ip_count"): "suricata_value",
    ("suricata", "unique_dst_ips"): "suricata_value",
    ("suricata", "unique_event_types"): "suricata_value",
    ("suricata", "unique_http_hosts"): "suricata_value",
    ("suricata", "unique_protocols"): "suricata_value",
    ("suricata", "unique_sids"): "suricata_value",
    ("suricata", "unique_signature_count"): "suricata_value",
    ("suricata", "unique_signature_ids"): "suricata_value",
    ("suricata", "unique_signatures"): "suricata_value",
    ("suricata", "unique_snis"): "suricata_value",
    ("suricata", "unique_source_ip_count"): "suricata_value",
    ("suricata", "unique_source_ips"): "suricata_value",
    ("suricata", "unique_src_ip_count"): "suricata_value",
    ("suricata", "unique_src_ips"): "suricata_value",
    # netflow
    ("netflow", "bytes_total"): "netflow_value",
    ("netflow", "count"): "netflow_value",
    ("netflow", "count_field"): "netflow_value",
    ("netflow", "data_record_count"): "netflow_value",
    ("netflow", "datagram_count"): "netflow_value",
    ("netflow", "destination_ips"): "netflow_value",
    ("netflow", "destination_ports"): "netflow_value",
    ("netflow", "doctets_total"): "netflow_value",
    ("netflow", "domain_id"): "netflow_value",
    ("netflow", "dpkts_total"): "netflow_value",
    ("netflow", "dst_ip_count"): "netflow_value",
    ("netflow", "dst_ips"): "netflow_value",
    ("netflow", "dst_ports"): "netflow_value",
    ("netflow", "dstaddr_set"): "netflow_value",
    ("netflow", "dstaddrs"): "netflow_value",
    ("netflow", "dstports"): "netflow_value",
    ("netflow", "engine_id"): "netflow_value",
    ("netflow", "engine_type"): "netflow_value",
    ("netflow", "entry_count"): "netflow_value",
    ("netflow", "export_count"): "netflow_value",
    ("netflow", "export_packet_count"): "netflow_value",
    ("netflow", "export_time"): "netflow_value",
    ("netflow", "export_time_unix"): "netflow_value",
    ("netflow", "export_time_utc"): "netflow_value",
    ("netflow", "export_timestamp"): "netflow_value",
    ("netflow", "export_timestamp_utc"): "netflow_value",
    ("netflow", "export_version"): "netflow_value",
    ("netflow", "flow_count"): "netflow_value",
    ("netflow", "flow_packets_total"): "netflow_value",
    ("netflow", "flow_record_count"): "netflow_value",
    ("netflow", "flow_sequence"): "netflow_value",
    ("netflow", "flows_count"): "netflow_value",
    ("netflow", "header_count"): "netflow_value",
    ("netflow", "header_flow_count"): "netflow_value",
    ("netflow", "header_record_count"): "netflow_value",
    ("netflow", "header_time_utc"): "netflow_value",
    ("netflow", "header_version"): "netflow_value",
    ("netflow", "ip_protocols"): "netflow_value",
    ("netflow", "most_common_dst_ip"): "netflow_value",
    ("netflow", "most_common_src_ip"): "netflow_value",
    ("netflow", "netflow_version"): "netflow_value",
    ("netflow", "num_records"): "netflow_value",
    ("netflow", "number_of_exports"): "netflow_value",
    ("netflow", "number_of_flows"): "netflow_value",
    ("netflow", "number_of_packets"): "netflow_value",
    ("netflow", "number_of_records"): "netflow_value",
    ("netflow", "observation_domain_id"): "netflow_value",
    ("netflow", "octets_total"): "netflow_value",
    ("netflow", "package_sequence"): "netflow_value",
    ("netflow", "packet_count"): "netflow_value",
    ("netflow", "packets_total"): "netflow_value",
    ("netflow", "pdu_count"): "netflow_value",
    ("netflow", "prot_set"): "netflow_value",
    ("netflow", "protocol_numbers"): "netflow_value",
    ("netflow", "protocols"): "netflow_value",
    ("netflow", "record_count"): "netflow_value",
    ("netflow", "records_count"): "netflow_value",
    ("netflow", "row_count"): "netflow_value",
    ("netflow", "sampling_interval"): "netflow_value",
    ("netflow", "sequence"): "netflow_value",
    ("netflow", "sequence_number"): "netflow_value",
    ("netflow", "source_id"): "netflow_value",
    ("netflow", "source_ips"): "netflow_value",
    ("netflow", "source_ports"): "netflow_value",
    ("netflow", "src_ip_count"): "netflow_value",
    ("netflow", "src_ips"): "netflow_value",
    ("netflow", "src_ports"): "netflow_value",
    ("netflow", "srcaddr_set"): "netflow_value",
    ("netflow", "srcaddrs"): "netflow_value",
    ("netflow", "srcports"): "netflow_value",
    ("netflow", "sum_doctets"): "netflow_value",
    ("netflow", "sum_dpkts"): "netflow_value",
    ("netflow", "sys_uptime"): "netflow_value",
    ("netflow", "system_uptime"): "netflow_value",
    ("netflow", "sysuptime"): "netflow_value",
    ("netflow", "top_destination_ip"): "netflow_value",
    ("netflow", "top_dst_ip"): "netflow_value",
    ("netflow", "top_source_ip"): "netflow_value",
    ("netflow", "top_src_ip"): "netflow_value",
    ("netflow", "top_talker"): "netflow_value",
    ("netflow", "top_talker_ip"): "netflow_value",
    ("netflow", "total_bytes"): "netflow_value",
    ("netflow", "total_doctets"): "netflow_value",
    ("netflow", "total_dpkts"): "netflow_value",
    ("netflow", "total_octets"): "netflow_value",
    ("netflow", "total_packets"): "netflow_value",
    ("netflow", "total_pkts"): "netflow_value",
    ("netflow", "total_records"): "netflow_value",
    ("netflow", "unique_destination_count"): "netflow_value",
    ("netflow", "unique_destination_ip_count"): "netflow_value",
    ("netflow", "unique_destination_ips"): "netflow_value",
    ("netflow", "unique_dst"): "netflow_value",
    ("netflow", "unique_dst_count"): "netflow_value",
    ("netflow", "unique_dst_ip_count"): "netflow_value",
    ("netflow", "unique_dst_ips"): "netflow_value",
    ("netflow", "unique_dst_ports"): "netflow_value",
    ("netflow", "unique_dstaddr_count"): "netflow_value",
    ("netflow", "unique_dstaddrs"): "netflow_value",
    ("netflow", "unique_protocols"): "netflow_value",
    ("netflow", "unique_source_count"): "netflow_value",
    ("netflow", "unique_source_ip_count"): "netflow_value",
    ("netflow", "unique_source_ips"): "netflow_value",
    ("netflow", "unique_src"): "netflow_value",
    ("netflow", "unique_src_count"): "netflow_value",
    ("netflow", "unique_src_ip_count"): "netflow_value",
    ("netflow", "unique_src_ips"): "netflow_value",
    ("netflow", "unique_src_ports"): "netflow_value",
    ("netflow", "unique_srcaddr_count"): "netflow_value",
    ("netflow", "unique_srcaddrs"): "netflow_value",
    ("netflow", "unix_nsecs"): "netflow_value",
    ("netflow", "unix_seconds"): "netflow_value",
    ("netflow", "unix_secs"): "netflow_value",
    ("netflow", "unix_secs_utc"): "netflow_value",
    ("netflow", "uptime_ms"): "netflow_value",
    ("netflow", "version"): "netflow_value",
    # csv_flows
    ("csv_flows", "addresses"): "csv_flows_value",
    ("csv_flows", "bytes_total"): "csv_flows_value",
    ("csv_flows", "capture_duration"): "csv_flows_value",
    ("csv_flows", "column_names"): "csv_flows_value",
    ("csv_flows", "columns"): "csv_flows_value",
    ("csv_flows", "destination_addresses"): "csv_flows_value",
    ("csv_flows", "destination_ips"): "csv_flows_value",
    ("csv_flows", "destination_set"): "csv_flows_value",
    ("csv_flows", "destinations"): "csv_flows_value",
    ("csv_flows", "distinct_protocol_count"): "csv_flows_value",
    ("csv_flows", "distinct_protocols"): "csv_flows_value",
    ("csv_flows", "dominant_protocol"): "csv_flows_value",
    ("csv_flows", "dst_ips"): "csv_flows_value",
    ("csv_flows", "duration"): "csv_flows_value",
    ("csv_flows", "endpoint_count"): "csv_flows_value",
    ("csv_flows", "endpoints"): "csv_flows_value",
    ("csv_flows", "entry_count"): "csv_flows_value",
    ("csv_flows", "field_names"): "csv_flows_value",
    ("csv_flows", "fields"): "csv_flows_value",
    ("csv_flows", "first_time"): "csv_flows_value",
    ("csv_flows", "first_timestamp"): "csv_flows_value",
    ("csv_flows", "frame_count"): "csv_flows_value",
    ("csv_flows", "header"): "csv_flows_value",
    ("csv_flows", "header_columns"): "csv_flows_value",
    ("csv_flows", "largest_frame"): "csv_flows_value",
    ("csv_flows", "last_frame_number"): "csv_flows_value",
    ("csv_flows", "last_no"): "csv_flows_value",
    ("csv_flows", "last_time"): "csv_flows_value",
    ("csv_flows", "last_timestamp"): "csv_flows_value",
    ("csv_flows", "length_total"): "csv_flows_value",
    ("csv_flows", "line_count"): "csv_flows_value",
    ("csv_flows", "max_frame_length"): "csv_flows_value",
    ("csv_flows", "max_frame_number"): "csv_flows_value",
    ("csv_flows", "max_length"): "csv_flows_value",
    ("csv_flows", "most_common_destination"): "csv_flows_value",
    ("csv_flows", "most_common_protocol"): "csv_flows_value",
    ("csv_flows", "most_common_source"): "csv_flows_value",
    ("csv_flows", "most_frequent_protocol"): "csv_flows_value",
    ("csv_flows", "num_packets"): "csv_flows_value",
    ("csv_flows", "number_of_packets"): "csv_flows_value",
    ("csv_flows", "packet_count"): "csv_flows_value",
    ("csv_flows", "packets"): "csv_flows_value",
    ("csv_flows", "packets_per_protocol"): "csv_flows_value",
    ("csv_flows", "protocol_count"): "csv_flows_value",
    ("csv_flows", "protocol_counts"): "csv_flows_value",
    ("csv_flows", "protocol_hierarchy"): "csv_flows_value",
    ("csv_flows", "protocol_histogram"): "csv_flows_value",
    ("csv_flows", "protocol_names"): "csv_flows_value",
    ("csv_flows", "protocol_set"): "csv_flows_value",
    ("csv_flows", "protocols"): "csv_flows_value",
    ("csv_flows", "record_count"): "csv_flows_value",
    ("csv_flows", "row_count"): "csv_flows_value",
    ("csv_flows", "rows_count"): "csv_flows_value",
    ("csv_flows", "source_addresses"): "csv_flows_value",
    ("csv_flows", "source_ips"): "csv_flows_value",
    ("csv_flows", "source_set"): "csv_flows_value",
    ("csv_flows", "sources"): "csv_flows_value",
    ("csv_flows", "src_ips"): "csv_flows_value",
    ("csv_flows", "sum_length"): "csv_flows_value",
    ("csv_flows", "top_destination"): "csv_flows_value",
    ("csv_flows", "top_destination_ip"): "csv_flows_value",
    ("csv_flows", "top_protocol"): "csv_flows_value",
    ("csv_flows", "top_source"): "csv_flows_value",
    ("csv_flows", "top_source_ip"): "csv_flows_value",
    ("csv_flows", "top_talker"): "csv_flows_value",
    ("csv_flows", "total_bytes"): "csv_flows_value",
    ("csv_flows", "total_frame_length"): "csv_flows_value",
    ("csv_flows", "total_length"): "csv_flows_value",
    ("csv_flows", "total_packets"): "csv_flows_value",
    ("csv_flows", "unique_address_count"): "csv_flows_value",
    ("csv_flows", "unique_addresses"): "csv_flows_value",
    ("csv_flows", "unique_destination_addresses"): "csv_flows_value",
    ("csv_flows", "unique_destinations"): "csv_flows_value",
    ("csv_flows", "unique_dst_ips"): "csv_flows_value",
    ("csv_flows", "unique_ip_count"): "csv_flows_value",
    ("csv_flows", "unique_ips"): "csv_flows_value",
    ("csv_flows", "unique_protocol_count"): "csv_flows_value",
    ("csv_flows", "unique_protocols"): "csv_flows_value",
    ("csv_flows", "unique_source_addresses"): "csv_flows_value",
    ("csv_flows", "unique_sources"): "csv_flows_value",
    ("csv_flows", "unique_src_ips"): "csv_flows_value",
    # firewall_log
    ("firewall_log", "accept_count"): "firewall_log_value",
    ("firewall_log", "action_counts"): "firewall_log_value",
    ("firewall_log", "action_set"): "firewall_log_value",
    ("firewall_log", "actions"): "firewall_log_value",
    ("firewall_log", "actions_count"): "firewall_log_value",
    ("firewall_log", "allow_count"): "firewall_log_value",
    ("firewall_log", "allowed_connections"): "firewall_log_value",
    ("firewall_log", "allowed_count"): "firewall_log_value",
    ("firewall_log", "allows"): "firewall_log_value",
    ("firewall_log", "block_count"): "firewall_log_value",
    ("firewall_log", "blocked_count"): "firewall_log_value",
    ("firewall_log", "blocked_dst_ips"): "firewall_log_value",
    ("firewall_log", "blocked_dst_ports"): "firewall_log_value",
    ("firewall_log", "blocked_ports"): "firewall_log_value",
    ("firewall_log", "blocked_src_ips"): "firewall_log_value",
    ("firewall_log", "column_names"): "firewall_log_value",
    ("firewall_log", "columns"): "firewall_log_value",
    ("firewall_log", "connection_count"): "firewall_log_value",
    ("firewall_log", "counts_by_action"): "firewall_log_value",
    ("firewall_log", "denied_count"): "firewall_log_value",
    ("firewall_log", "destination_ips"): "firewall_log_value",
    ("firewall_log", "destination_ports"): "firewall_log_value",
    ("firewall_log", "directions"): "firewall_log_value",
    ("firewall_log", "drop_count"): "firewall_log_value",
    ("firewall_log", "drop_dst_ips"): "firewall_log_value",
    ("firewall_log", "drop_dst_ports"): "firewall_log_value",
    ("firewall_log", "drop_entries"): "firewall_log_value",
    ("firewall_log", "drop_src_ips"): "firewall_log_value",
    ("firewall_log", "dropped_connections"): "firewall_log_value",
    ("firewall_log", "dropped_count"): "firewall_log_value",
    ("firewall_log", "dropped_destination_ips"): "firewall_log_value",
    ("firewall_log", "dropped_dst_ips"): "firewall_log_value",
    ("firewall_log", "dropped_dst_ports"): "firewall_log_value",
    ("firewall_log", "dropped_source_ips"): "firewall_log_value",
    ("firewall_log", "dropped_src_ips"): "firewall_log_value",
    ("firewall_log", "drops"): "firewall_log_value",
    ("firewall_log", "dst_ip_count"): "firewall_log_value",
    ("firewall_log", "dst_ips"): "firewall_log_value",
    ("firewall_log", "dst_ports"): "firewall_log_value",
    ("firewall_log", "earliest_timestamp"): "firewall_log_value",
    ("firewall_log", "entry_count"): "firewall_log_value",
    ("firewall_log", "event_count"): "firewall_log_value",
    ("firewall_log", "field_names"): "firewall_log_value",
    ("firewall_log", "fields"): "firewall_log_value",
    ("firewall_log", "first_entry_time"): "firewall_log_value",
    ("firewall_log", "first_time"): "firewall_log_value",
    ("firewall_log", "first_timestamp"): "firewall_log_value",
    ("firewall_log", "inbound_count"): "firewall_log_value",
    ("firewall_log", "last_entry_time"): "firewall_log_value",
    ("firewall_log", "last_time"): "firewall_log_value",
    ("firewall_log", "last_timestamp"): "firewall_log_value",
    ("firewall_log", "latest_timestamp"): "firewall_log_value",
    ("firewall_log", "line_count"): "firewall_log_value",
    ("firewall_log", "log_entry_count"): "firewall_log_value",
    ("firewall_log", "log_software"): "firewall_log_value",
    ("firewall_log", "log_version"): "firewall_log_value",
    ("firewall_log", "most_common_dst_ip"): "firewall_log_value",
    ("firewall_log", "most_common_src_ip"): "firewall_log_value",
    ("firewall_log", "most_dropped_src_ip"): "firewall_log_value",
    ("firewall_log", "num_records"): "firewall_log_value",
    ("firewall_log", "number_of_records"): "firewall_log_value",
    ("firewall_log", "outbound_count"): "firewall_log_value",
    ("firewall_log", "path_set"): "firewall_log_value",
    ("firewall_log", "paths"): "firewall_log_value",
    ("firewall_log", "permitted_count"): "firewall_log_value",
    ("firewall_log", "protocol_set"): "firewall_log_value",
    ("firewall_log", "protocols"): "firewall_log_value",
    ("firewall_log", "receive_count"): "firewall_log_value",
    ("firewall_log", "record_count"): "firewall_log_value",
    ("firewall_log", "row_count"): "firewall_log_value",
    ("firewall_log", "send_count"): "firewall_log_value",
    ("firewall_log", "size_total"): "firewall_log_value",
    ("firewall_log", "software"): "firewall_log_value",
    ("firewall_log", "source_ips"): "firewall_log_value",
    ("firewall_log", "source_ports"): "firewall_log_value",
    ("firewall_log", "src_ip_count"): "firewall_log_value",
    ("firewall_log", "src_ips"): "firewall_log_value",
    ("firewall_log", "src_ports"): "firewall_log_value",
    ("firewall_log", "time_format"): "firewall_log_value",
    ("firewall_log", "timestamp_format"): "firewall_log_value",
    ("firewall_log", "top_blocked_source_ip"): "firewall_log_value",
    ("firewall_log", "top_destination_ip"): "firewall_log_value",
    ("firewall_log", "top_dropped_src_ip"): "firewall_log_value",
    ("firewall_log", "top_dst_ip"): "firewall_log_value",
    ("firewall_log", "top_source_ip"): "firewall_log_value",
    ("firewall_log", "top_src_ip"): "firewall_log_value",
    ("firewall_log", "top_talker"): "firewall_log_value",
    ("firewall_log", "total_bytes"): "firewall_log_value",
    ("firewall_log", "total_records"): "firewall_log_value",
    ("firewall_log", "total_size"): "firewall_log_value",
    ("firewall_log", "unique_actions"): "firewall_log_value",
    ("firewall_log", "unique_destination_count"): "firewall_log_value",
    ("firewall_log", "unique_destination_ip_count"): "firewall_log_value",
    ("firewall_log", "unique_destination_ips"): "firewall_log_value",
    ("firewall_log", "unique_dst"): "firewall_log_value",
    ("firewall_log", "unique_dst_count"): "firewall_log_value",
    ("firewall_log", "unique_dst_ip_count"): "firewall_log_value",
    ("firewall_log", "unique_dst_ips"): "firewall_log_value",
    ("firewall_log", "unique_dst_ports"): "firewall_log_value",
    ("firewall_log", "unique_protocols"): "firewall_log_value",
    ("firewall_log", "unique_source_ip_count"): "firewall_log_value",
    ("firewall_log", "unique_source_ips"): "firewall_log_value",
    ("firewall_log", "unique_src"): "firewall_log_value",
    ("firewall_log", "unique_src_count"): "firewall_log_value",
    ("firewall_log", "unique_src_ip_count"): "firewall_log_value",
    ("firewall_log", "unique_src_ips"): "firewall_log_value",
    ("firewall_log", "unique_src_ports"): "firewall_log_value",
    ("firewall_log", "version"): "firewall_log_value",
    ("firewall_log", "w3c_version"): "firewall_log_value",
}
