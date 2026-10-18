"""Build http-redirect-dns-resolve fixtures for lib.codec.resolve_chain / resolve_hosts / reconcile (no lib.*).
HAR written with stdlib json, pcap with the dpkt writer; `expected` comes from the independent readers run below
(jq over the HAR, tshark over the pcap), never from lib.codec.
Run: python3 -I tests/data/script_fixtures/redirect/rd_gen.py"""
import json, socket, subprocess
from pathlib import Path

import dpkt

HERE = Path(__file__).resolve().parent
GEN = "python3 -I tests/data/script_fixtures/redirect/rd_gen.py  "


def sh(cmd, stdin=None):
    return subprocess.run(["bash", "-c", cmd], input=stdin, capture_output=True, text=True, check=True,
                          cwd=HERE).stdout


def write(name, fx):
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")


# --- A: HAR, 302 (relative Location) -> 301 (redirectURL, final hop never requested) ----------------------------------
A_PLANS = {"loader.ps1": "v=3|role=downloader|url=http://dl-a.example.invalid/get?id=7|file_path=C:\\Users\\Public\\s.bin",
           "beacon.js": "v=3|role=beacon|url=https://c2-b.example.invalid/ping|host_id=host-0042"}


def entry(url, status, loc=None, redirect=None):
    hdr = [{"name": "Location", "value": loc}] if loc else []
    return {"request": {"method": "GET", "url": url, "headers": [{"name": "User-Agent", "value": "Mozilla/5.0"}]},
            "response": {"status": status, "headers": hdr, "redirectURL": redirect or ""}}


har_a = {"log": {"version": "1.2", "creator": {"name": "rd_gen", "version": "1"}, "entries": [
    entry("http://dl-a.example.invalid/get?id=7", 302, loc="/s/stage.bin"),
    entry("http://dl-a.example.invalid/s/stage.bin", 301, redirect="https://cdn-z.example.invalid/stage.bin"),
    entry("https://c2-b.example.invalid/ping", 200)]}}
har_a_txt = json.dumps(har_a)
JQ_A = ("jq -r '.log.entries[] | [.request.url, (.response.status|tostring), (.response.redirectURL // \"\"), "
        "((.response.headers[]? | select(.name|ascii_downcase==\"location\") | .value) // \"\")] | @tsv'")
rows = [(ln.split("\t") + ["", "", ""])[:4] for ln in sh(JQ_A, har_a_txt).splitlines() if ln.strip()]
nxt = {}
for u, st, red, loc in rows:
    if st.startswith("3") and (red or loc):
        t = red or loc
        nxt[u] = t if "://" in t else u.split("/", 3)[0] + "//" + u.split("/", 3)[2] + t   # absolute-path Location
chain = {}
for u in nxt:
    c, cur = [], u
    while cur in nxt:
        cur = nxt[cur]
        c.append(cur)
    chain[u] = c
declared = {p.split("url=")[1].split("|")[0] for p in A_PLANS.values()}
seen = {r[0] for r in rows} | set(nxt.values())
write("rd_har_chain", {
    "entry": "resolve_chain+reconcile", "plans": A_PLANS, "observed": har_a_txt, "decoy": False,
    "expected": {"resolve_chain": chain, "urls.observed_only": sorted(seen - declared),
                 "urls.declared_only": sorted(declared - seen), "unfetched": [],
                 "final_urls": {"http://dl-a.example.invalid/get?id=7": chain["http://dl-a.example.invalid/get?id=7"][-1]}},
    "generator_cmd": GEN + "(HAR via json.dumps: 302 Location '/s/stage.bin' -> 301 redirectURL https://cdn-z.., final "
                           "hop never requested)",
    "oracle_cmd": JQ_A + " <HAR  -> 3xx rows url->(redirectURL|Location) joined by hand; observed = request urls + "
                         "targets, comm against plan urls"})

# --- B: pcap, DNS CNAME chains + HTTP 302 + SYN-only HTTPS to a resolved IP ---------------------------------------------
B_PLANS = {"stager.vbs": "v=3|role=downloader|url=http://dl-b.example.invalid/x",
           "tls.ps1": "v=3|role=downloader|url=https://tls-d.example.invalid/payload.dat",
           "ghost.bat": "v=3|role=downloader|url=https://never-e.example.invalid/n.bin"}
CLI, DNS_SRV = "10.0.0.5", "10.0.0.53"
pkts, t = [], 1792240000.0


def eth(ip):
    return bytes(dpkt.ethernet.Ethernet(src=b"\x02" * 6, dst=b"\x04" * 6, type=dpkt.ethernet.ETH_TYPE_IP, data=ip))


def ip4(src, dst, p, l4):
    i = dpkt.ip.IP(src=socket.inet_aton(src), dst=socket.inet_aton(dst), p=p, ttl=64, data=l4)
    i.len = len(bytes(i))
    return i


def add(frame):
    global t
    t += 0.01
    pkts.append((t, frame))


def dns(qid, qname, chain):
    q = dpkt.dns.DNS(id=qid, qd=[dpkt.dns.DNS.Q(name=qname, type=dpkt.dns.DNS_A, cls=dpkt.dns.DNS_IN)])
    add(eth(ip4(CLI, DNS_SRV, 17, udp(50000 + qid, 53, bytes(q)))))
    an, owner = [], qname
    for v in chain:
        if v[0].isdigit():
            an.append(dpkt.dns.DNS.RR(name=owner, type=dpkt.dns.DNS_A, cls=dpkt.dns.DNS_IN, ttl=60,
                                      ip=socket.inet_aton(v)))
        else:
            an.append(dpkt.dns.DNS.RR(name=owner, type=dpkt.dns.DNS_CNAME, cls=dpkt.dns.DNS_IN, ttl=60, cname=v))
            owner = v
    r = dpkt.dns.DNS(id=qid, qd=q.qd, an=an)
    r.qr, r.rd, r.ra = dpkt.dns.DNS_R, 1, 1   # flag properties: not settable through the constructor
    add(eth(ip4(DNS_SRV, CLI, 17, udp(53, 50000 + qid, bytes(r)))))


def udp(sp, dp, data):
    u = dpkt.udp.UDP(sport=sp, dport=dp, data=data)
    u.ulen = len(bytes(u))
    return u


def tcp(src, dst, sp, dp, seq, ack, flags, data=b""):
    return eth(ip4(src, dst, 6, dpkt.tcp.TCP(sport=sp, dport=dp, seq=seq, ack=ack, flags=flags, off=5, win=65535,
                                             data=data)))


dns(1, "dl-b.example.invalid", ["edge-b.cdn.example.invalid", "198.51.100.20"])
dns(2, "tls-d.example.invalid", ["tls-edge.cdn.example.invalid", "edge2.cdn.example.invalid", "198.51.100.30"])
S, A, P = dpkt.tcp.TH_SYN, dpkt.tcp.TH_ACK, dpkt.tcp.TH_PUSH
srv = "198.51.100.20"
req = b"GET /x HTTP/1.1\r\nHost: dl-b.example.invalid\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n\r\n"
body = b"<a href='http://drop-c.example.invalid/p.bin'>moved</a>"
rsp = (b"HTTP/1.1 302 Found\r\nLocation: http://drop-c.example.invalid/p.bin\r\nContent-Type: text/html\r\n"
       b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
add(tcp(CLI, srv, 49200, 80, 1000, 0, S))
add(tcp(srv, CLI, 80, 49200, 5000, 1001, S | A))
add(tcp(CLI, srv, 49200, 80, 1001, 5001, A))
add(tcp(CLI, srv, 49200, 80, 1001, 5001, P | A, req))
add(tcp(srv, CLI, 80, 49200, 5001, 1001 + len(req), P | A, rsp))
add(tcp(CLI, "198.51.100.30", 49201, 443, 7000, 0, S))     # HTTPS to the resolved IP: SYN only, no ClientHello
add(tcp("198.51.100.30", CLI, 443, 49201, 9000, 7001, S | A))
with open(HERE / "rd_pcap_redirect_cname.pcap", "wb") as f:
    w = dpkt.pcap.Writer(f)
    for ts, fr in pkts:
        w.writepkt(fr, ts)

TS_HTTP = ("tshark -r rd_pcap_redirect_cname.pcap -Y http.response -T fields -E separator=/t "
           "-e http.request_in -e http.response.code -e http.location")
TS_DNS = ("tshark -r rd_pcap_redirect_cname.pcap -Y 'dns.flags.response==1' -T fields -E separator=/t "
          "-e dns.qry.name -e dns.cname -e dns.a")
TS_SYN = ("tshark -r rd_pcap_redirect_cname.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields "
          "-e ip.dst -e tcp.dstport")
TS_REQ = ("tshark -r rd_pcap_redirect_cname.pcap -Y http.request -T fields -E separator=/t -e frame.number "
          "-e http.request.full_uri")
req_by_frame = dict(ln.split("\t") for ln in sh(TS_REQ).splitlines() if ln.strip())
req_uris = list(req_by_frame.values())
http_rows = [(ln.split("\t") + ["", ""])[:3] for ln in sh(TS_HTTP).splitlines() if ln.strip()]
chain_b = {req_by_frame[fr]: [loc] for fr, code, loc in http_rows if code.startswith("3") and loc}
hosts_b = {}
for ln in sh(TS_DNS).strip().splitlines():
    q, cn, a = (ln.split("\t") + ["", ""])[:3]
    hosts_b[q] = [x for x in cn.split(",") if x] + [x for x in a.split(",") if x]
syn = [ln.split("\t") for ln in sh(TS_SYN).strip().splitlines()]
req_hosts = {u.split("/")[2] for u in req_uris}
syn_ips = {ip for ip, port in syn}
declared_b = {m: p.split("url=")[1].split("|")[0] for m, p in B_PLANS.items()}
via = {u: "ip" for u in declared_b.values() if u.split("/")[2] not in req_hosts
       and set(hosts_b.get(u.split("/")[2], ())) & syn_ips}
seen_b = set(req_uris) | {loc for v in chain_b.values() for loc in v} | set(via)
write("rd_pcap_redirect_cname", {
    "entry": "resolve_chain+reconcile", "file": "rd_pcap_redirect_cname.pcap", "plans": B_PLANS, "decoy": False,
    "expected": {"resolve_chain": chain_b, "resolve_hosts": hosts_b,
                 "urls.observed_only": sorted(seen_b - set(declared_b.values())),
                 "urls.declared_only": sorted(set(declared_b.values()) - seen_b),
                 "unfetched": sorted(m for m, u in declared_b.items() if u not in seen_b), "fetched_via": via},
    "generator_cmd": GEN + "(dpkt.pcap.Writer: DNS dl-b CNAME edge-b -> A 198.51.100.20, GET /x -> 302 Location "
                           "http://drop-c../p.bin (never requested); DNS tls-d CNAME x2 -> 198.51.100.30, SYN-only :443)",
    "oracle_cmd": " ; ".join([TS_HTTP, TS_DNS, TS_SYN, TS_REQ]) + "  -> 3xx rows give hops; a declared https url "
                  "with no request to its host counts as fetched when a SYN dst is one of its DNS answers"})

# --- decoys -----------------------------------------------------------------------------------------------------------
har_d = {"log": {"version": "1.2", "creator": {"name": "rd_gen", "version": "1"}, "entries": [
    entry("http://dl-a.example.invalid/get?id=7", 201, loc="/s/created/9"),          # 201 Created + Location
    entry("https://c2-b.example.invalid/ping", 200, redirect=""),
    entry("https://c2-b.example.invalid/ping2", 200, loc="https://elsewhere.example.invalid/")]}}
har_d_txt = json.dumps(har_d)
rows_d = [(ln.split("\t") + ["", "", ""])[:4] for ln in sh(JQ_A, har_d_txt).splitlines() if ln.strip()]
assert not [r for r in rows_d if r[1].startswith("3")]
write("rd_decoy_201_location", {
    "entry": "resolve_chain+reconcile", "plans": A_PLANS, "observed": har_d_txt, "decoy": True,
    "expected": {"resolve_chain": {}, "urls.observed_only": ["https://c2-b.example.invalid/ping2"],
                 "urls.declared_only": [], "unfetched": []},
    "generator_cmd": GEN + "(HAR via json.dumps: Location on 201 / 200 responses, empty redirectURL -> no redirect)",
    "oracle_cmd": JQ_A + " <HAR  -> no 3xx status row, so no hop; observed-only = request urls minus plan urls"})
(HERE / "rd_decoy_renamed.pcap").write_bytes(b"HTTP/1.1 302 Found\r\nLocation: http://x.example.invalid/\r\n\r\n")
write("rd_decoy_renamed_pcap", {
    "entry": "resolve_chain", "file": "rd_decoy_renamed.pcap", "decoy": True, "expected": {"resolve_chain": {}},
    "generator_cmd": GEN + "(printf of a bare HTTP 302 response saved as .pcap: no capture magic, no request)",
    "oracle_cmd": "file rd_decoy_renamed.pcap  -> 'ASCII text' (not a capture); capinfos fails"})
print("ok")
