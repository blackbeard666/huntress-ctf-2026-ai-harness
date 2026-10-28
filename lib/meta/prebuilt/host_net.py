"""Host artifacts that NARRATE network activity (prebuilt, SPECULATIVE -- no field here was ever GM-verified; D27
flavor "find the host narrative missing network evidence"). One content-sniffing dispatcher behind every fmt token
(evtx / sysmon / netstat / ipconfig / dns_cache / hosts / bash_history / zsh_history / shell_history): the GM's
token for a host text dump is a guess, the bytes are not.

Sources (in sniff order):
  EVTX (ElfFile magic; records via evtx_binxml.events, the stdlib BinXML reader):
    Sysmon EID 3 NetworkConnect  Image, Protocol, Initiated, SourceIp/Port, DestinationIp/Port, DestinationHostname,
                                 UtcTime. Remote side = Destination when Initiated != "false", else Source (inbound).
    Sysmon EID 22 DNSEvent       QueryName, QueryResults, Image.
    Security 5156 (WFP permitted) Application, Direction (%%14592 inbound -> Source side), DestAddress/DestPort,
                                 SourceAddress/SourcePort. Counted as a connection like EID 3.
    TerminalServices 1149        UserData Param3 = RDP source IP (-> remote_ips, rdp_source_ips; not a connection).
    Sysmon EID 3/22 are only taken when the provider is Microsoft-Windows-Sysmon (or the channel is Sysmon's) -- a
    Security 4624 never contributes. An EVTX with none of these events -> "none".
  netstat   a `Proto  Local Address  Foreign Address  State  PID` table (Windows -ano / -anob) or the Linux
            `netstat -tunap` layout (Recv-Q/Send-Q columns; "PID/Program name"). A connection row = TCP/UDP with a
            concrete foreign address (not 0.0.0.0 / :: / *, port not 0 / *) and a state other than LISTEN(ING).
            Images: `-b` bracket lines ("[chrome.exe]", the first one after the row) or the Linux program name.
  ipconfig  `ipconfig /displaydns`: dns_query_names = distinct "Record Name" values, remote_ips = "A (Host) Record" /
            "AAAA Record" values.
  hosts     hosts file: every non-comment line is `<ip> <name> [aliases]` -> remote_ips / hostnames / entry_count.
  history   bash/zsh/PowerShell ConsoleHost history: ssh/scp/sftp/rsync/curl/wget/nc/ncat/netcat/telnet/ftp
            targets + URLs (Invoke-WebRequest etc.). Ports: explicit (-p / -P / URL / nc port arg) else the scheme
            default (ssh/scp/sftp/rsync 22, http 80, https 443, ftp 21, telnet 23). connecting_images = the tool names;
            hostname targets -> dns_query_names. Timestamps: bash `#<unix>` lines / zsh `: <unix>:<d>;` prefixes.

Value conventions (match pcap_flows.py / netlogs.py): sets are JSON lists, Python sorted() of the TEXT spellings
(IPs lexicographic as text, endpoints `ip:port`, IPv6 `[ip]:port`; remote_ips / remote_endpoints hold IP LITERALS
only -- a hostname target (history scp/ssh) goes to dns_query_names); ports sorted ints; counts base-10 ints.
first/last_connection_time_utc: Sysmon UtcTime ("YYYY-MM-DD HH:MM:SS.fff", already UTC) / 5156 System TimeCreated /
history unix epoch, rendered "YYYY-MM-DDTHH:MM:SSZ" (seconds, like evtx.first_time_created_utc). Loopback endpoints
are KEPT (they are what the host recorded). Not one of these artifacts / field absent -> "none"; EVTX parse failure
or deadline -> None."""
import datetime
import ipaddress
import re

_FIELD_NAMES = {
    "remote_ips": ("remote_ips", "destination_ips", "dest_ips", "remote_addresses", "remote_ip_addresses",
                   "foreign_ips", "foreign_addresses", "remote_hosts_ips"),
    "remote_endpoints": ("remote_endpoints", "destination_endpoints", "foreign_endpoints", "remote_ip_ports",
                         "established_remote_endpoints", "remote_ip_port_pairs"),
    "remote_ports": ("remote_ports", "destination_ports", "dest_ports", "foreign_ports"),
    "dns_query_names": ("dns_query_names", "query_names", "dns_queries", "queried_domains", "dns_names",
                        "record_names", "queried_names"),
    "connecting_images": ("connecting_images", "connection_images", "network_images", "connecting_processes",
                          "network_process_images"),
    "connection_count": ("connection_count", "network_connection_count", "connections_count",
                         "established_connection_count", "number_of_connections"),
    "first_connection_time_utc": ("first_connection_time_utc", "first_connection_utc", "earliest_connection_time_utc"),
    "last_connection_time_utc": ("last_connection_time_utc", "last_connection_utc", "latest_connection_time_utc"),
    "destination_hostnames": ("destination_hostnames", "remote_hostnames"),
    "dns_query_count": ("dns_query_count",),
    "rdp_source_ips": ("rdp_source_ips", "rdp_client_ips"),
    "hostnames": ("hostnames", "mapped_hostnames", "hosts_hostnames"),
    "entry_count": ("hosts_entry_count", "mapping_count"),
}

FIELDS = {
    ("evtx", "remote_ips"): "host_net_value",
    ("evtx", "destination_ips"): "host_net_value",
    ("evtx", "remote_endpoints"): "host_net_value",
    ("evtx", "destination_endpoints"): "host_net_value",
    ("evtx", "remote_ports"): "host_net_value",
    ("evtx", "destination_ports"): "host_net_value",
    ("evtx", "dns_query_names"): "host_net_value",
    ("evtx", "query_names"): "host_net_value",
    ("evtx", "dns_queries"): "host_net_value",
    ("evtx", "connecting_images"): "host_net_value",
    ("evtx", "network_images"): "host_net_value",
    ("evtx", "connection_count"): "host_net_value",
    ("evtx", "network_connection_count"): "host_net_value",
    ("evtx", "first_connection_time_utc"): "host_net_value",
    ("evtx", "last_connection_time_utc"): "host_net_value",
    ("evtx", "destination_hostnames"): "host_net_value",
    ("evtx", "dns_query_count"): "host_net_value",
    ("evtx", "rdp_source_ips"): "host_net_value",
    ("sysmon", "remote_ips"): "host_net_value",
    ("sysmon", "destination_ips"): "host_net_value",
    ("sysmon", "remote_endpoints"): "host_net_value",
    ("sysmon", "destination_endpoints"): "host_net_value",
    ("sysmon", "remote_ports"): "host_net_value",
    ("sysmon", "destination_ports"): "host_net_value",
    ("sysmon", "dns_query_names"): "host_net_value",
    ("sysmon", "query_names"): "host_net_value",
    ("sysmon", "dns_queries"): "host_net_value",
    ("sysmon", "connecting_images"): "host_net_value",
    ("sysmon", "network_images"): "host_net_value",
    ("sysmon", "connection_count"): "host_net_value",
    ("sysmon", "network_connection_count"): "host_net_value",
    ("sysmon", "first_connection_time_utc"): "host_net_value",
    ("sysmon", "last_connection_time_utc"): "host_net_value",
    ("sysmon", "destination_hostnames"): "host_net_value",
    ("sysmon", "dns_query_count"): "host_net_value",
    ("netstat", "remote_ips"): "host_net_value",
    ("netstat", "foreign_ips"): "host_net_value",
    ("netstat", "foreign_addresses"): "host_net_value",
    ("netstat", "remote_endpoints"): "host_net_value",
    ("netstat", "foreign_endpoints"): "host_net_value",
    ("netstat", "established_remote_endpoints"): "host_net_value",
    ("netstat", "remote_ports"): "host_net_value",
    ("netstat", "connecting_images"): "host_net_value",
    ("netstat", "connection_count"): "host_net_value",
    ("netstat", "established_connection_count"): "host_net_value",
    ("netstat", "first_connection_time_utc"): "host_net_value",
    ("ipconfig", "dns_query_names"): "host_net_value",
    ("ipconfig", "record_names"): "host_net_value",
    ("ipconfig", "dns_names"): "host_net_value",
    ("ipconfig", "remote_ips"): "host_net_value",
    ("ipconfig", "connection_count"): "host_net_value",
    ("dns_cache", "dns_query_names"): "host_net_value",
    ("dns_cache", "record_names"): "host_net_value",
    ("dns_cache", "dns_names"): "host_net_value",
    ("dns_cache", "remote_ips"): "host_net_value",
    ("hosts", "remote_ips"): "host_net_value",
    ("hosts", "hostnames"): "host_net_value",
    ("hosts", "mapped_hostnames"): "host_net_value",
    ("hosts", "entry_count"): "host_net_value",
    ("hosts", "mapping_count"): "host_net_value",
    ("hosts", "dns_query_names"): "host_net_value",
    ("bash_history", "remote_ips"): "host_net_value",
    ("bash_history", "remote_endpoints"): "host_net_value",
    ("bash_history", "remote_ports"): "host_net_value",
    ("bash_history", "dns_query_names"): "host_net_value",
    ("bash_history", "connecting_images"): "host_net_value",
    ("bash_history", "connection_count"): "host_net_value",
    ("bash_history", "first_connection_time_utc"): "host_net_value",
    ("zsh_history", "remote_ips"): "host_net_value",
    ("zsh_history", "remote_endpoints"): "host_net_value",
    ("zsh_history", "remote_ports"): "host_net_value",
    ("zsh_history", "dns_query_names"): "host_net_value",
    ("zsh_history", "connecting_images"): "host_net_value",
    ("zsh_history", "connection_count"): "host_net_value",
    ("zsh_history", "first_connection_time_utc"): "host_net_value",
    ("shell_history", "remote_ips"): "host_net_value",
    ("shell_history", "remote_endpoints"): "host_net_value",
    ("shell_history", "remote_ports"): "host_net_value",
    ("shell_history", "dns_query_names"): "host_net_value",
    ("shell_history", "connecting_images"): "host_net_value",
    ("shell_history", "connection_count"): "host_net_value",
    ("shell_history", "first_connection_time_utc"): "host_net_value",
}

_CANON = {alias: canon for canon, names in _FIELD_NAMES.items() for alias in names}
_CANON["entry_count"] = "entry_count"


def _ip(s):
    try:
        return ipaddress.ip_address(str(s).strip().strip("[]").split("%")[0])
    except ValueError:
        return None


def _unspecified(host):
    a = _ip(host)
    return host in ("", "*") or (a is not None and a.is_unspecified)


def _endpoint(host, port):
    a = _ip(host)
    return ("[%s]:%s" % (host, port)) if a is not None and a.version == 6 else "%s:%s" % (host, port)


class _Conn:
    __slots__ = ("host", "port", "image", "time")

    def __init__(self, host, port=None, image=None, time=None):
        self.host, self.port, self.image, self.time = host, port, image, time


def _iso(t):
    """'YYYY-MM-DD HH:MM:SS[.fff]' / ISO 'YYYY-MM-DDTHH:MM:SS[.fffffff]Z' / unix int -> 'YYYY-MM-DDTHH:MM:SSZ'."""
    if t is None:
        return None
    if isinstance(t, int):
        try:
            return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except (OverflowError, OSError, ValueError):
            return None
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})", str(t))
    return "%sT%sZ" % m.groups() if m else None


# ------------------------------------------------------------------------------------------------- EVTX (Sysmon)


def _evtx(b):
    from .evtx_binxml import events
    evs = events(b)
    out = {"conns": [], "dns": [], "dns_images": [], "rdp": [], "dhost": []}
    for e in evs:
        eid, d = e.get("event_id"), e.get("data") or {}
        prov, chan = (e.get("provider") or "").lower(), (e.get("channel") or "").lower()
        sysmon = "sysmon" in prov or "sysmon" in chan
        if eid == 3 and sysmon:
            inbound = (d.get("Initiated") or "").strip().lower() == "false"
            side = "Source" if inbound else "Destination"
            host = (d.get(side + "Ip") or "").strip()
            if host:
                out["conns"].append(_Conn(host, (d.get(side + "Port") or "").strip() or None,
                                          (d.get("Image") or "").strip() or None, d.get("UtcTime") or e.get("time")))
            dh = (d.get("DestinationHostname") or "").strip()
            if dh and dh != "-":
                out["dhost"].append(dh)
        elif eid == 22 and sysmon:
            q = (d.get("QueryName") or "").strip()
            if q:
                out["dns"].append(q)
            img = (d.get("Image") or "").strip()
            if img:
                out["dns_images"].append(img)
        elif eid == 5156 and "security-auditing" in prov:
            inbound = (d.get("Direction") or "").strip() in ("%%14592", "Inbound")
            pre = "Source" if inbound else "Dest"
            host = (d.get(pre + "Address") or "").strip()
            if host:
                out["conns"].append(_Conn(host, (d.get(pre + "Port") or "").strip() or None,
                                          (d.get("Application") or "").strip() or None, e.get("time")))
        elif eid == 1149 and "terminalservices" in prov:
            ip = (d.get("Param3") or "").strip()
            if _ip(ip) is not None:
                out["rdp"].append(ip)
    if not (out["conns"] or out["dns"] or out["rdp"]):
        return None
    return out


# ------------------------------------------------------------------------------------------------------ netstat

_NETSTAT_ROW = re.compile(r"^\s*(tcp6?|udp6?|TCP|UDP)\s+(.*)$")


def _split_addr(a):
    a = a.strip()
    if a.startswith("["):
        host, _, rest = a[1:].partition("]")
        return host, rest.lstrip(":")
    if a.count(":") > 1:                 # Linux netstat IPv6 "::1:443" / ":::*": last colon is the port
        host, _, port = a.rpartition(":")
        return host, port
    host, _, port = a.rpartition(":")
    return host, port


def _netstat(text):
    lines = text.splitlines()
    if not any(re.search(r"Local Address\s+Foreign Address", ln) for ln in lines):
        return None
    conns, last = [], None
    for ln in lines:
        m = _NETSTAT_ROW.match(ln)
        if not m:
            br = re.match(r"^\s*\[(.+?)\]\s*$", ln)
            if br and last is not None and last.image is None:
                last.image = br.group(1)
            continue
        last = None
        proto, toks = m.group(1).lower(), m.group(2).split()
        if len(toks) >= 4 and toks[0].isdigit() and toks[1].isdigit():    # Linux: Recv-Q Send-Q
            toks = toks[2:]
        if len(toks) < 2:
            continue
        host, port = _split_addr(toks[1])
        rest = toks[2:]
        state = rest[0] if rest and proto.startswith("tcp") and not rest[0].replace("/", "").isdigit() else None
        if state is not None:
            rest = rest[1:]
        if _unspecified(host) or port in ("", "*", "0") or (state or "").upper() in ("LISTEN", "LISTENING"):
            continue
        img = None
        if rest and "/" in rest[0]:
            img = rest[0].split("/", 1)[1].rstrip(":") or None
        c = _Conn(host, port, img)
        conns.append(c)
        last = c
    return {"conns": conns, "dns": [], "dns_images": [], "rdp": [], "dhost": []}


# ---------------------------------------------------------------------------------------- ipconfig /displaydns


def _displaydns(text):
    if not re.search(r"Record Name[ .]*:", text):
        return None
    names = re.findall(r"Record Name[ .]*:\s*(\S+)", text)
    ips = [m for m in re.findall(r"(?:A \(Host\) Record|AAAA Record)[ .]*:\s*(\S+)", text) if _ip(m) is not None]
    return {"conns": None, "dns": names, "dns_images": [], "rdp": [], "dhost": [], "ips": ips}


# --------------------------------------------------------------------------------------------------- hosts file


def _hosts(text):
    ips, names, n = [], [], 0
    for ln in text.splitlines():
        ln = ln.split("#", 1)[0].strip()
        if not ln:
            continue
        toks = ln.split()
        if len(toks) < 2 or _ip(toks[0]) is None:
            return None
        n += 1
        ips.append(toks[0])
        names += toks[1:]
    if not n:
        return None
    return {"hosts": True, "ips": ips, "names": names, "n": n}


# ------------------------------------------------------------------------------------------------ shell history

_TOOLS = {"ssh": 22, "scp": 22, "sftp": 22, "rsync": 22, "curl": None, "wget": None, "nc": None, "ncat": None,
          "netcat": None, "telnet": 23, "ftp": 21}
_SCHEME_PORT = {"http": 80, "https": 443, "ftp": 21, "ssh": 22, "sftp": 22, "ws": 80, "wss": 443}
_SSH_ARG = set("bcDEeFIiJLlmOoQRSWw")
_NC_ARG = set("pswecixXqIOT")
_URL = re.compile(r"\b([a-zA-Z][a-zA-Z0-9+.-]*)://(?:[^/\s@]*@)?(\[[0-9A-Fa-f:.]+\]|[A-Za-z0-9.-]+)(?::(\d+))?")


def _host_of(tok):
    """'user@host:path' / 'host:path' / 'user@host' -> host (None for a local path)."""
    tok = tok.split("@", 1)[1] if "@" in tok else tok
    if tok.startswith("["):
        return tok[1:].split("]", 1)[0]
    return tok.split(":", 1)[0] or None


def _cmd_conns(cmd):
    toks = cmd.split()
    i = 0
    while i < len(toks) and (toks[i] in ("sudo", "nohup", "time", "exec") or "=" in toks[i].split("/")[0]):
        i += 1
    out = []
    for u in _URL.finditer(cmd):
        host = u.group(2).strip("[]")
        port = u.group(3) or _SCHEME_PORT.get(u.group(1).lower())
        tool = toks[i].rsplit("/", 1)[-1] if i < len(toks) else None
        out.append((host, port, tool))
    if i >= len(toks):
        return out
    tool = toks[i].rsplit("/", 1)[-1].lower()
    if tool not in _TOOLS or tool in ("curl", "wget"):
        return out
    args, port, j = [], None, i + 1
    opt_args = _NC_ARG if tool in ("nc", "ncat", "netcat") else _SSH_ARG
    while j < len(toks):
        t = toks[j]
        if t in ("|", ";", "&&", "||", ">", ">>", "<"):
            break
        if t.startswith("-") and len(t) > 1:
            flag = t[1:]
            if tool in ("nc", "ncat", "netcat") and "l" in flag:
                return out                                   # a listener, not an outbound connection
            if flag in ("p", "P") and j + 1 < len(toks) and tool not in ("nc", "ncat", "netcat"):
                port = toks[j + 1]
                j += 2
                continue
            if len(flag) == 1 and flag in opt_args or flag in ("e",) and tool == "rsync":
                j += 2
                continue
            j += 1
            continue
        args.append(t)
        j += 1
    if not args:
        return out
    if tool in ("nc", "ncat", "netcat", "telnet", "ftp"):
        host = args[0]
        port = args[1] if len(args) > 1 and args[1].isdigit() else (_TOOLS[tool] if tool != "ftp" or
                                                                    len(args) == 1 else _TOOLS[tool])
        if port is None:
            return out
        return out + [(host, port, tool)]
    if tool == "ssh":
        return out + [(_host_of(args[0]), port or 22, tool)]
    for a in args:                                           # scp / sftp / rsync: every remote spec
        if ":" in a or tool == "sftp":
            h = _host_of(a)
            if h:
                out.append((h, port or 22, tool))
    return out


def _history(text):
    conns, stamp = [], None
    for ln in text.splitlines():
        s = ln.strip()
        m = re.match(r"^#(\d{9,11})$", s)                    # bash HISTTIMEFORMAT
        if m:
            stamp = int(m.group(1))
            continue
        m = re.match(r"^: (\d{9,11}):\d+;(.*)$", s)          # zsh EXTENDED_HISTORY
        t = stamp
        if m:
            t, s = int(m.group(1)), m.group(2)
        stamp = None
        if not s or s.startswith("#"):
            continue
        for host, port, tool in _cmd_conns(s):
            if host:
                conns.append(_Conn(host, str(port) if port is not None else None, tool, t))
    if not conns:
        return None
    dns = [c.host for c in conns if _ip(c.host) is None]
    return {"conns": conns, "dns": dns, "dns_images": [], "rdp": [], "dhost": [], "history": True}


# ------------------------------------------------------------------------------------------------- dispatcher


def _text(b):
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


def _sset(vals):
    return sorted({v for v in vals if v not in (None, "", "-")}) or "none"


def host_net_value(data, ctx):
    if data is None:
        return None
    field = ctx.get("field") or ""
    canon = _CANON.get(field)
    if canon is None:
        return None
    b = bytes(data)
    if b[:8] == b"ElfFile\x00":
        try:
            r = _evtx(b)
        except Exception:   # noqa: BLE001 -- BinXML parse failure / deadline: cannot answer
            return None
    else:
        t = _text(b)
        if t is None:
            return "none"
        r = _netstat(t) or _displaydns(t) or _hosts(t) or _history(t)
    if r is None:
        return "none"
    if r.get("hosts"):
        if canon == "remote_ips":
            return _sset(r["ips"])
        if canon == "hostnames":
            return _sset(r["names"])
        if canon == "entry_count":
            return r["n"]
        return "none"
    if canon == "entry_count" or canon == "hostnames":
        return "none"
    conns = r.get("conns")
    if canon == "dns_query_names":
        return _sset(r["dns"])
    if canon == "dns_query_count":
        return len(r["dns"]) if r["dns"] else "none"
    if canon == "destination_hostnames":
        return _sset(r["dhost"])
    if canon == "rdp_source_ips":
        return _sset(r["rdp"])
    if conns is None:                                       # displaydns: only names and answer IPs
        return _sset(r["ips"]) if canon == "remote_ips" else "none"
    if canon == "remote_ips":
        return _sset([c.host for c in conns if _ip(c.host) is not None] + r["rdp"])
    if canon == "remote_endpoints":
        return _sset([_endpoint(c.host, c.port) for c in conns if c.port and _ip(c.host) is not None])
    if canon == "remote_ports":
        ports = {int(c.port) for c in conns if c.port and str(c.port).isdigit()}
        return sorted(ports) or "none"
    if canon == "connecting_images":
        return _sset([c.image for c in conns])
    if canon == "connection_count":
        return len(conns) if conns or not r.get("history") else "none"
    if canon in ("first_connection_time_utc", "last_connection_time_utc"):
        ts = [x for x in (_iso(c.time) for c in conns) if x]
        if not ts:
            return "none"
        return min(ts) if canon.startswith("first") else max(ts)
    return None
