"""Cross-member join: HOST CLAIMS vs CAPTURE TRAFFIC (prebuilt, SPECULATIVE -- no field here was ever GM-verified).
Coverage-atlas row "host-vs-network-synthesis" (D27 flavor "find the host narrative missing network evidence").
Ids `metadata-day-NN-synthesis-<key>`; members come from the question's `Files: [...]` list / the container zip
(synthesis_media._source), each member classified by CONTENT (names are never trusted):
  CAPTURE  classic pcap / pcapng (pcap_flows._parse; gz/zst wrappers via pcap._unwrap). Evidence = every TCP/UDP
           endpoint seen on EITHER side of a packet {(ip, port, proto)} + every IP seen + DNS query names (UDP/TCP 53
           QNAMEs, lowercase, no trailing dot). A capture with a broken header still contributes what decodes.
  HOST     Sysmon EID 3 (remote side = Destination, Source when Initiated == "false"; Protocol kept),
           Security 5156 (same rule as host_net.py), Sysmon EID 22 QueryName (a DNS claim);
           netstat tables (host_net._netstat, proto from the row); Windows pfirewall.log ALLOW rows (remote side =
           dst for SEND, src for RECEIVE); Zeek conn rows (id.resp_h:id.resp_p, proto); shell history IP literals.
A claim MATCHES when (ip, port) is in the capture endpoint set (proto must agree when both sides know it); a claim
without a port matches on the IP alone. Spelling `ip:port` (IPv6 `[ip]:port`), port-less claims bare `ip`.
Fields (lists sorted Python-text order -> compact JSON; an empty answer -> "none"; no capture or no host member ->
"none" from a zip / None otherwise):
  host_claims_missing_network_evidence / claims_missing_network_evidence / unmatched_claims / orphan_claims /
    missing_network_evidence / claims_without_network_evidence / ... = distinct unmatched claim endpoints;
  matched_claim_count / unmatched_claim_count / host_claim_count = distinct claim endpoints (all host members);
  matched_claims = the matched endpoints;
  *_member(s) / *_file(s) / lying_member / narrative_without_packets = host members whose claims ALL lack packets
    (fallback: members with ANY unmatched claim); singular names -> the name when exactly one, else the sorted list;
  lying_host / lying_hostname / host_missing_network_evidence = EVTX <Computer> of those members (else the member
    name);
  capture_without_host_evidence / captures_without_host_evidence / unclaimed_captures = capture members no host claim
    matches (singular: the one name);
  unclaimed_capture_endpoints / capture_endpoints_without_host_evidence = capture SERVER endpoints (TCP SYN dst, else
    the lower-port side of the flow) no host claim names;
  capture_dns_names; dns_claims_missing_network_evidence = host DNS query names the captures never asked;
  malformed_capture (singular) = pcap_integrity's lone malformed capture name;
  total_packets / total_packet_count / valid_capture_packet_count / ... = packets summed over the captures
    pcap_integrity calls valid (no reason flagged)."""
import ipaddress
import struct

_F = "network_synthesis_value"
_MISSING = ("host_claims_missing_network_evidence", "claims_missing_network_evidence", "unmatched_claims",
            "unmatched_host_claims", "orphan_claims", "orphaned_claims", "missing_network_evidence",
            "claims_without_network_evidence", "claims_without_packets", "host_claims_without_packets",
            "unsupported_claims", "unverified_claims", "unmatched_endpoints", "missing_endpoints",
            "host_endpoints_missing_from_capture", "endpoints_missing_from_capture", "claims_missing_from_capture",
            "host_claims_missing_from_capture", "unmatched_connections", "connections_without_packets",
            "connections_missing_network_evidence", "host_connections_missing_network_evidence")
_MEMBERS = ("host_member_missing_network_evidence", "host_members_missing_network_evidence",
            "member_missing_network_evidence", "members_missing_network_evidence",
            "host_artifact_missing_network_evidence", "host_artifacts_missing_network_evidence",
            "artifact_missing_network_evidence", "file_missing_network_evidence", "files_missing_network_evidence",
            "host_file_missing_network_evidence", "lying_member", "lying_members", "lying_file", "lying_artifact",
            "narrative_without_packets", "narrative_missing_network_evidence", "host_narrative_missing_network_evidence",
            "member_without_network_evidence", "members_without_network_evidence", "unmatched_member",
            "unmatched_members", "orphan_member", "orphan_members", "host_log_missing_network_evidence",
            "log_missing_network_evidence", "unsupported_member", "unsupported_host_member")
_HOSTS = ("lying_host", "lying_hostname", "host_missing_network_evidence", "hostname_missing_network_evidence",
          "host_without_network_evidence", "hostname_without_network_evidence", "unmatched_host", "orphan_host")
_CAPS = ("capture_without_host_evidence", "captures_without_host_evidence", "capture_missing_host_evidence",
         "captures_missing_host_evidence", "unclaimed_capture", "unclaimed_captures", "orphan_capture",
         "orphan_captures", "unmatched_capture", "unmatched_captures", "capture_without_host_claims")
_CAP_EPS = ("unclaimed_capture_endpoints", "capture_endpoints_without_host_evidence",
            "capture_endpoints_missing_host_evidence", "unclaimed_endpoints", "traffic_without_host_evidence",
            "network_endpoints_without_host_evidence", "unmatched_capture_endpoints", "orphan_capture_endpoints")
_COUNTS = ("matched_claim_count", "matched_claims_count", "unmatched_claim_count", "unmatched_claims_count",
           "missing_claim_count", "host_claim_count", "claim_count", "total_claim_count")
_TOTALS = ("total_packets", "total_packet_count", "valid_capture_packet_count", "valid_capture_total_packets",
           "total_packets_valid_captures", "total_valid_packets", "packets_across_valid_captures",
           "total_packets_across_valid_captures", "valid_packet_count", "total_packet_count_valid_captures")
_OTHER = ("matched_claims", "matched_host_claims", "capture_dns_names", "dns_claims_missing_network_evidence",
          "dns_names_missing_network_evidence", "unmatched_dns_claims", "malformed_capture",
          "malformed_capture_member", "malformed_capture_file", "corrupt_capture", "invalid_capture",
          "total_packets", "total_packet_count", "valid_capture_packet_count", "valid_capture_total_packets",
          "total_packets_valid_captures", "total_valid_packets", "packets_across_valid_captures",
          "total_packets_across_valid_captures", "valid_packet_count", "total_packet_count_valid_captures")

FIELDS = {
    ("synthesis", "host_claims_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "claims_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "unmatched_claims"): "network_synthesis_value",
    ("synthesis", "unmatched_host_claims"): "network_synthesis_value",
    ("synthesis", "orphan_claims"): "network_synthesis_value",
    ("synthesis", "orphaned_claims"): "network_synthesis_value",
    ("synthesis", "missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "claims_without_network_evidence"): "network_synthesis_value",
    ("synthesis", "claims_without_packets"): "network_synthesis_value",
    ("synthesis", "host_claims_without_packets"): "network_synthesis_value",
    ("synthesis", "unsupported_claims"): "network_synthesis_value",
    ("synthesis", "unverified_claims"): "network_synthesis_value",
    ("synthesis", "unmatched_endpoints"): "network_synthesis_value",
    ("synthesis", "missing_endpoints"): "network_synthesis_value",
    ("synthesis", "host_endpoints_missing_from_capture"): "network_synthesis_value",
    ("synthesis", "endpoints_missing_from_capture"): "network_synthesis_value",
    ("synthesis", "claims_missing_from_capture"): "network_synthesis_value",
    ("synthesis", "host_claims_missing_from_capture"): "network_synthesis_value",
    ("synthesis", "unmatched_connections"): "network_synthesis_value",
    ("synthesis", "connections_without_packets"): "network_synthesis_value",
    ("synthesis", "connections_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "host_connections_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "host_member_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "host_members_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "member_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "members_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "host_artifact_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "host_artifacts_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "artifact_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "file_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "files_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "host_file_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "lying_member"): "network_synthesis_value",
    ("synthesis", "lying_members"): "network_synthesis_value",
    ("synthesis", "lying_file"): "network_synthesis_value",
    ("synthesis", "lying_artifact"): "network_synthesis_value",
    ("synthesis", "narrative_without_packets"): "network_synthesis_value",
    ("synthesis", "narrative_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "host_narrative_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "member_without_network_evidence"): "network_synthesis_value",
    ("synthesis", "members_without_network_evidence"): "network_synthesis_value",
    ("synthesis", "unmatched_member"): "network_synthesis_value",
    ("synthesis", "unmatched_members"): "network_synthesis_value",
    ("synthesis", "orphan_member"): "network_synthesis_value",
    ("synthesis", "orphan_members"): "network_synthesis_value",
    ("synthesis", "host_log_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "log_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "unsupported_member"): "network_synthesis_value",
    ("synthesis", "unsupported_host_member"): "network_synthesis_value",
    ("synthesis", "lying_host"): "network_synthesis_value",
    ("synthesis", "lying_hostname"): "network_synthesis_value",
    ("synthesis", "host_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "hostname_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "host_without_network_evidence"): "network_synthesis_value",
    ("synthesis", "hostname_without_network_evidence"): "network_synthesis_value",
    ("synthesis", "unmatched_host"): "network_synthesis_value",
    ("synthesis", "orphan_host"): "network_synthesis_value",
    ("synthesis", "capture_without_host_evidence"): "network_synthesis_value",
    ("synthesis", "captures_without_host_evidence"): "network_synthesis_value",
    ("synthesis", "capture_missing_host_evidence"): "network_synthesis_value",
    ("synthesis", "captures_missing_host_evidence"): "network_synthesis_value",
    ("synthesis", "unclaimed_capture"): "network_synthesis_value",
    ("synthesis", "unclaimed_captures"): "network_synthesis_value",
    ("synthesis", "orphan_capture"): "network_synthesis_value",
    ("synthesis", "orphan_captures"): "network_synthesis_value",
    ("synthesis", "unmatched_capture"): "network_synthesis_value",
    ("synthesis", "unmatched_captures"): "network_synthesis_value",
    ("synthesis", "capture_without_host_claims"): "network_synthesis_value",
    ("synthesis", "unclaimed_capture_endpoints"): "network_synthesis_value",
    ("synthesis", "capture_endpoints_without_host_evidence"): "network_synthesis_value",
    ("synthesis", "capture_endpoints_missing_host_evidence"): "network_synthesis_value",
    ("synthesis", "unclaimed_endpoints"): "network_synthesis_value",
    ("synthesis", "traffic_without_host_evidence"): "network_synthesis_value",
    ("synthesis", "network_endpoints_without_host_evidence"): "network_synthesis_value",
    ("synthesis", "unmatched_capture_endpoints"): "network_synthesis_value",
    ("synthesis", "orphan_capture_endpoints"): "network_synthesis_value",
    ("synthesis", "matched_claim_count"): "network_synthesis_value",
    ("synthesis", "matched_claims_count"): "network_synthesis_value",
    ("synthesis", "unmatched_claim_count"): "network_synthesis_value",
    ("synthesis", "unmatched_claims_count"): "network_synthesis_value",
    ("synthesis", "missing_claim_count"): "network_synthesis_value",
    ("synthesis", "host_claim_count"): "network_synthesis_value",
    ("synthesis", "claim_count"): "network_synthesis_value",
    ("synthesis", "total_claim_count"): "network_synthesis_value",
    ("synthesis", "matched_claims"): "network_synthesis_value",
    ("synthesis", "matched_host_claims"): "network_synthesis_value",
    ("synthesis", "capture_dns_names"): "network_synthesis_value",
    ("synthesis", "dns_claims_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "dns_names_missing_network_evidence"): "network_synthesis_value",
    ("synthesis", "unmatched_dns_claims"): "network_synthesis_value",
    ("synthesis", "malformed_capture"): "network_synthesis_value",
    ("synthesis", "malformed_capture_member"): "network_synthesis_value",
    ("synthesis", "malformed_capture_file"): "network_synthesis_value",
    ("synthesis", "corrupt_capture"): "network_synthesis_value",
    ("synthesis", "invalid_capture"): "network_synthesis_value",
    ("synthesis", "total_packets"): "network_synthesis_value",
    ("synthesis", "total_packet_count"): "network_synthesis_value",
    ("synthesis", "valid_capture_packet_count"): "network_synthesis_value",
    ("synthesis", "valid_capture_total_packets"): "network_synthesis_value",
    ("synthesis", "total_packets_valid_captures"): "network_synthesis_value",
    ("synthesis", "total_valid_packets"): "network_synthesis_value",
    ("synthesis", "packets_across_valid_captures"): "network_synthesis_value",
    ("synthesis", "total_packets_across_valid_captures"): "network_synthesis_value",
    ("synthesis", "valid_packet_count"): "network_synthesis_value",
    ("synthesis", "total_packet_count_valid_captures"): "network_synthesis_value",
}


def _ipn(s):
    try:
        return ipaddress.ip_address(str(s).strip().strip("[]").split("%")[0])
    except ValueError:
        return None


def _port(p):
    p = str(p).strip() if p is not None else ""
    return int(p) if p.isdigit() and int(p) < 65536 else None


def _proto(p):
    p = str(p or "").strip().lower().rstrip("46")
    return p if p in ("tcp", "udp") else None


def _spell(ip, port):
    if port is None:
        return str(ip)
    return ("[%s]:%d" % (ip, port)) if ip.version == 6 else "%s:%d" % (ip, port)


# ------------------------------------------------------------------------------------------------------ captures

def _qname(d, o):
    labels, n = [], 0
    while o < len(d) and n < 64:
        ln = d[o]
        if ln == 0 or ln >= 0xC0:
            break
        labels.append(bytes(d[o + 1:o + 1 + ln]).decode("ascii", "replace"))
        o += 1 + ln
        n += 1
    return ".".join(labels).lower().rstrip(".") or None


def _capture(b):
    """{"eps": {(ip, port, proto)}, "ips": set, "dns": set, "servers": {(ip, port, proto)}} or None (not a capture)."""
    from .pcap_flows import _parse, _l3, _ip
    recs = _parse(b)
    if recs is None:
        return None
    eps, ips, dns, servers, flows = set(), set(), set(), set(), {}
    for lt, _s, _f, _r, _i, _o, d in recs:
        try:
            l3 = _l3(lt, d)
            ip = _ip(d, l3[1], l3[0]) if l3 and l3[0] in (0x0800, 0x86DD) else None
        except (struct.error, IndexError, ValueError):
            ip = None
        if ip is None:
            continue
        src, dst, proto, l4 = ip
        ips.update((src, dst))
        if proto not in (6, 17) or l4 is None or l4 + (20 if proto == 6 else 8) > len(d):
            continue
        pn = "tcp" if proto == 6 else "udp"
        sp, dp = struct.unpack_from("!HH", d, l4)
        eps.add((src, sp, pn))
        eps.add((dst, dp, pn))
        key = (pn, frozenset(((src, sp), (dst, dp))))
        if proto == 6 and d[l4 + 13] & 0x12 == 0x02:
            flows[key] = (dst, dp, pn)
        elif key not in flows:
            flows[key] = None
        if 53 in (sp, dp):
            q = l4 + (8 if proto == 17 else ((d[l4 + 12] >> 4) * 4 + 2))
            if q + 12 <= len(d) and struct.unpack_from("!H", d, q + 4)[0]:
                nm = _qname(d, q + 12)
                if nm:
                    dns.add(nm)
    for (pn, pair), syn in flows.items():
        if syn is not None:
            servers.add(syn)
            continue
        ends = sorted(pair, key=lambda e: (e[1], e[0].version, int(e[0])))
        servers.add((ends[0][0], ends[0][1], pn))
    return {"eps": eps, "ips": ips, "dns": dns, "servers": servers}


# --------------------------------------------------------------------------------------------------------- hosts

def _claim(out, host, port, proto=None):
    a = _ipn(host)
    if a is not None and not a.is_unspecified:
        out.append((a, _port(port), _proto(proto)))


def _host_evtx(b):
    from .evtx_binxml import events
    claims, dns, comp = [], [], None
    for e in events(b):
        eid, d = e.get("event_id"), e.get("data") or {}
        prov, chan = (e.get("provider") or "").lower(), (e.get("channel") or "").lower()
        sysmon = "sysmon" in prov or "sysmon" in chan
        hit = False
        if eid == 3 and sysmon:
            side = "Source" if (d.get("Initiated") or "").strip().lower() == "false" else "Destination"
            _claim(claims, d.get(side + "Ip"), d.get(side + "Port"), d.get("Protocol"))
            hit = True
        elif eid == 22 and sysmon:
            q = (d.get("QueryName") or "").strip().lower().rstrip(".")
            if q:
                dns.append(q)
            hit = True
        elif eid == 5156 and "security-auditing" in prov:
            pre = "Source" if (d.get("Direction") or "").strip() in ("%%14592", "Inbound") else "Dest"
            pr = {"6": "tcp", "17": "udp"}.get(str(d.get("Protocol") or "").strip())
            _claim(claims, d.get(pre + "Address"), d.get(pre + "Port"), pr)
            hit = True
        if hit and comp is None and e.get("computer"):
            comp = e["computer"].strip()
    if not claims and not dns:
        return None
    return {"claims": claims, "dns": dns, "host": comp}


def _host_text(b):
    from .host_net import _text, _netstat, _history
    from .netlogs import parse_pfirewall, parse_zeek
    t = _text(b)
    if t is None:
        return None
    claims = []
    ns = _netstat(t)
    if ns is not None:                       # netstat rows: protocol not kept by host_net -> matched on either
        for c in ns["conns"]:
            _claim(claims, c.host, c.port)
        return {"claims": claims, "dns": [], "host": None}
    fw = parse_pfirewall(b)
    if fw is not None:
        for r in fw["rows"]:
            if (r.get("action") or "").upper() not in ("ALLOW", "ALLOWED", "ACCEPT", "PERMIT"):
                continue
            recv = (r.get("path") or "").upper() == "RECEIVE"
            pre = "src" if recv else "dst"
            _claim(claims, r.get(pre + "-ip"), r.get(pre + "-port"), r.get("protocol"))
        return {"claims": claims, "dns": [], "host": None}
    zk = parse_zeek(b)
    if zk is not None:
        rows = [r for r in zk["rows"] if r.get("id.resp_h")]
        if not rows:
            return None
        for r in rows:
            _claim(claims, r.get("id.resp_h"), r.get("id.resp_p"), r.get("proto"))
        return {"claims": claims, "dns": [], "host": None}
    hi = _history(t)
    if hi is not None:
        for c in hi["conns"]:
            _claim(claims, c.host, c.port)
        return {"claims": claims, "dns": [], "host": None} if claims else None
    return None


# --------------------------------------------------------------------------------------------------------- join

def _members(names, read):
    caps, hosts = {}, {}
    for n in names:
        b = read(n)
        if b is None:
            return None
        b = bytes(b)
        if b[:8] == b"ElfFile\x00":
            h = _host_evtx(b)
            if h is not None:
                hosts[n] = h
            continue
        c = _capture(b)
        if c is not None:
            caps[n] = (c, b)
            continue
        h = _host_text(b)
        if h is not None and (h["claims"] or h["dns"]):
            hosts[n] = h
    return caps, hosts


def _matches(claim, ev):
    a, p, pr = claim
    if p is None:
        return a in ev["ips"]
    return any((a, p, x) in ev["eps"] for x in ((pr,) if pr else ("tcp", "udp")))


def _single_or_list(field, names):
    names = sorted(names)
    if not names:
        return "none"
    plural = field.endswith(("members", "files", "artifacts", "captures", "hosts", "names", "logs"))
    if plural or len(names) > 1:
        return names
    return names[0]


def _packets_valid(caps):
    from .pcap_integrity import analyse
    total, any_valid = 0, False
    for _n, (c, b) in caps.items():
        a = analyse(b)
        if a is None or a.get("reason"):
            continue
        any_valid = True
        total += a.get("complete") or 0
    return total if any_valid else "none"


def network_synthesis_value(data, ctx):
    """synthesis.<host-vs-capture field> (see the module docstring)."""
    try:
        from .synthesis_media import _source
        field = ctx.get("field") or ""
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        if field in ("malformed_capture", "malformed_capture_member", "malformed_capture_file", "corrupt_capture",
                     "invalid_capture"):
            from .pcap_integrity import integrity_synthesis_value
            v = integrity_synthesis_value(data, dict(ctx, field="malformed_capture_names"))
            if isinstance(v, list):
                return v[0] if len(v) == 1 else (v or "none")
            return v
        m = _members(names, read)
        if m is None:
            return None
        caps, hosts = m
        if field in _TOTALS:
            return _packets_valid(caps) if caps else ("none" if from_zip else None)
        if not caps or not hosts:
            return "none" if from_zip else None
        ev = {"eps": set(), "ips": set(), "dns": set()}
        for c, _b in caps.values():
            for k in ev:
                ev[k] |= c[k]
        if field == "capture_dns_names":
            return sorted(ev["dns"]) or "none"
        if field in ("dns_claims_missing_network_evidence", "dns_names_missing_network_evidence",
                     "unmatched_dns_claims"):
            return sorted({q for h in hosts.values() for q in h["dns"] if q not in ev["dns"]}) or "none"
        allc = {(a, p): pr for h in hosts.values() for a, p, pr in h["claims"]}
        matched = {k for k, pr in allc.items() if _matches((k[0], k[1], pr), ev)}
        miss = set(allc) - matched
        spell = lambda ks: sorted({_spell(a, p) for a, p in ks}) or "none"   # noqa: E731
        if field in _MISSING:
            return spell(miss)
        if field in ("matched_claims", "matched_host_claims"):
            return spell(matched)
        if field in _COUNTS:
            if field.startswith(("unmatched", "missing")):
                return len(miss)
            return len(matched) if field.startswith("matched") else len(allc)
        if field in _MEMBERS or field in _HOSTS:
            per = {}
            for n, h in hosts.items():
                cl = h["claims"]
                if not cl:
                    continue
                per[n] = [_matches(c, ev) for c in cl]
            liars = [n for n, r in per.items() if not any(r)] or [n for n, r in per.items() if not all(r)]
            if field in _HOSTS:
                liars = [hosts[n]["host"] or n for n in liars]
            return _single_or_list(field, set(liars))
        if field in _CAPS:
            claims = [c for h in hosts.values() for c in h["claims"]]
            orphan = [n for n, (c, _b) in caps.items() if not any(_matches(x, c) for x in claims)]
            return _single_or_list(field, orphan)
        if field in _CAP_EPS:
            servers = set()
            for c, _b in caps.values():
                servers |= c["servers"]
            out = {(a, p) for a, p, pr in servers
                   if (a, p) not in allc and (a, None) not in allc}
            return spell(out)
        return None
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
