"""Build network-evidence fixtures for lib.codec.network_indicators (stdlib struct writer, no lib.*): pcap / pcapng
captures built from the GM-verified D17 single (Fetch Quest) plan urls with one url removed and one added; expected
from tshark (the independent reader), never from lib.codec.
Run: python3 -I tests/data/script_fixtures/network/net_gen.py"""
import json, struct, subprocess, zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D17 = ROOT / "challenges/day17/scripting-fetch-quest"
c = json.loads((D17 / "single_solve/contract.json").read_text())
e = json.loads((D17 / "solver/cases/single_solve/expected.json").read_text())
plans = {}
for q in c["questions"]:
    i = q["id"]
    if i in e and i.endswith("-url") and not i.endswith("-upload-url"):
        m = q["artifact"].split("->")[-1].strip()
        plans[m] = f"v=3|role=unknown|url={e[i]}|host_id=host-{zlib.crc32(m.encode()):010d}"
members = sorted(plans)[:8]
plans = {m: plans[m] for m in members}
urls = [p.split("url=")[1].split("|")[0] for p in plans.values()]
DROP, ADD = urls[3], "https://cdn-ffee00aa11.example.invalid/0badc0ffee00.bin"


def csum(b):
    if len(b) % 2:
        b += b"\0"
    s = sum(struct.unpack(f">{len(b) // 2}H", b))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


def ip4(src, dst, proto, pay):
    h = struct.pack(">BBHHHBBH4s4s", 0x45, 0, 20 + len(pay), 1, 0x4000, 64, proto, 0, bytes(src), bytes(dst))
    return h[:10] + struct.pack(">H", csum(h)) + h[12:] + pay


def ip6(src, dst, nh, pay):
    return struct.pack(">IHBB16s16s", 0x60000000, len(pay), nh, 64, bytes(src), bytes(dst)) + pay


def tcp(sp, dp, seq, ack, fl, pay=b""):
    return struct.pack(">HHIIBBHHH", sp, dp, seq, ack, 5 << 4, fl, 65535, 0, 0) + pay


def udp(sp, dp, pay):
    return struct.pack(">HHHH", sp, dp, 8 + len(pay), 0) + pay


def eth(l3, et=0x0800):
    return b"\x00\x11\x22\x33\x44\x55" + b"\x66\x77\x88\x99\xaa\xbb" + struct.pack(">H", et) + l3


def qname(h):
    return b"".join(bytes([len(x)]) + x.encode() for x in h.split(".")) + b"\0"


def dns(h, ip=None, tid=1):
    q = qname(h) + struct.pack(">HH", 1, 1)
    if ip is None:
        return struct.pack(">HHHHHH", tid, 0x0100, 1, 0, 0, 0) + q
    a = b"\xc0\x0c" + struct.pack(">HHIH", 1, 1, 60, 4) + bytes(ip)
    return struct.pack(">HHHHHH", tid, 0x8180, 1, 1, 0, 0) + q + a


def client_hello(sni):
    n = sni.encode()
    ext = struct.pack(">HHHBH", 0, len(n) + 5, len(n) + 3, 0, len(n)) + n
    body = b"\x03\x03" + bytes(32) + b"\x00" + struct.pack(">H", 2) + b"\x13\x01" + b"\x01\x00" + \
        struct.pack(">H", len(ext)) + ext
    hs = b"\x01" + len(body).to_bytes(3, "big") + body
    return b"\x16\x03\x01" + struct.pack(">H", len(hs)) + hs


def split(u):
    host, _, path = u.split("://", 1)[1].partition("/")
    return host, "/" + path


def frames(obs, v6=False):
    """Each observed url: DNS query+answer, then a TCP handshake to :80 with a plaintext GET (even index) or to
    :443 with a TLS ClientHello carrying the SNI (odd index; GET split over two segments for even index)."""
    out, cli = [], [10, 0, 0, 5]
    for n, u in enumerate(obs):
        host, path = split(u)
        srv = [203, 0, 113, 10 + n]
        out.append(eth(ip4(cli, [10, 0, 0, 1], 17, udp(50000 + n, 53, dns(host, tid=n + 1)))))
        out.append(eth(ip4([10, 0, 0, 1], cli, 17, udp(53, 50000 + n, dns(host, srv, tid=n + 1)))))
        sp, dp = 40000 + n, (80 if n % 2 == 0 else 443)
        out.append(eth(ip4(cli, srv, 6, tcp(sp, dp, 1000, 0, 0x02))))
        out.append(eth(ip4(srv, cli, 6, tcp(dp, sp, 5000, 1001, 0x12))))
        out.append(eth(ip4(cli, srv, 6, tcp(sp, dp, 1001, 5001, 0x10))))
        if dp == 80:
            req = (f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0 (fq-{n})\r\n"
                   f"Accept: */*\r\n\r\n").encode()
            cut = len(req) // 2 if n % 4 == 0 else len(req)
            out.append(eth(ip4(cli, srv, 6, tcp(sp, dp, 1001, 5001, 0x18, req[:cut]))))
            if cut < len(req):
                out.append(eth(ip4(cli, srv, 6, tcp(sp, dp, 1001 + cut, 5001, 0x18, req[cut:]))))
        else:
            out.append(eth(ip4(cli, srv, 6, tcp(sp, dp, 1001, 5001, 0x18, client_hello(host)))))
    if v6:   # one extra IPv6 HTTP request (pcapng only)
        s6, d6 = bytes.fromhex("20010db8" + "0" * 23 + "5"), bytes.fromhex("20010db8" + "0" * 22 + "99")
        req = b"POST /upload/v6 HTTP/1.1\r\nHost: v6-sink.example.invalid\r\nContent-Length: 4\r\n\r\nGET "
        out.append(eth(ip6(s6, d6, 6, tcp(41000, 8080, 1, 0, 0x02)), 0x86DD))
        out.append(eth(ip6(s6, d6, 6, tcp(41000, 8080, 2, 1, 0x18, req)), 0x86DD))
    return out


def pcap(frs):
    b = struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    for i, f in enumerate(frs):
        b += struct.pack("<IIII", 1792240000 + i, 0, len(f), len(f)) + f
    return b


def pcapng(frs):
    def blk(t, body):
        body += b"\0" * (-len(body) % 4)
        return struct.pack("<II", t, len(body) + 12) + body + struct.pack("<I", len(body) + 12)
    b = blk(0x0A0D0D0A, struct.pack("<IHHq", 0x1A2B3C4D, 1, 0, -1))
    b += blk(1, struct.pack("<HHI", 1, 0, 65535))
    for i, f in enumerate(frs):
        b += blk(6, struct.pack("<IIIII", 0, 0, i, len(f), len(f)) + f)
    return b


def tshark(path):
    def f(flt, *fs):
        cmd = ["tshark", "-r", str(path), "-Y", flt, "-T", "fields", "-E", "separator=|"] + \
            [x for fl in fs for x in ("-e", fl)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return [ln for ln in r.stdout.splitlines() if ln.strip()]
    return {"http_urls": sorted({"http://" + ln.replace("|", "") for ln in f("http.request", "http.host",
                                                                            "http.request.uri")}),
            "tls_sni": sorted(set(f("tls.handshake.type == 1", "tls.handshake.extensions_server_name"))),
            "dns_qnames": sorted(set(f("dns", "dns.qry.name"))),
            "dns_a": sorted(set(f("dns.flags.response == 1", "dns.qry.name", "dns.a"))),
            "syn_dst": sorted(set(f("tcp.flags.syn == 1 && tcp.flags.ack == 0", "ip.dst", "ipv6.dst", "tcp.dstport")))}


TS = ("tshark -r {f} -Y http.request -T fields -e http.host -e http.request.uri; -Y 'tls.handshake.type == 1' "
      "-e tls.handshake.extensions_server_name; -Y dns -e dns.qry.name; -Y 'dns.flags.response == 1' -e dns.qry.name "
      "-e dns.a; -Y 'tcp.flags.syn == 1 && tcp.flags.ack == 0' -e ip.dst -e ipv6.dst -e tcp.dstport")


def write(name, blob, ext, gen, decoy=False, recon=True):
    p = HERE / f"{name}.{ext}"
    p.write_bytes(blob)
    exp = tshark(p)
    fx = {"entry": "network_indicators", "file": p.name, "expected": exp, "decoy": decoy,
          "generator_cmd": "python3 -I tests/data/script_fixtures/network/net_gen.py  (" + gen + ")",
          "oracle_cmd": TS.format(f=p.name) + "  -> expected (sets)"}
    if recon:
        dec = {split(u)[0] for u in urls}
        seen = {split(u)[0] for u in exp["http_urls"]} | set(exp["tls_sni"]) | set(exp["dns_qnames"])
        fx["plans"] = plans
        fx["expected_reconcile"] = {"hosts_declared_only": sorted(dec - seen), "hosts_observed_only": sorted(seen - dec)}
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")
    print(name, json.dumps(exp)[:300])


obs = [u for u in urls if u != DROP] + [ADD]
write("net_pcap_d17", pcap(frames(obs)), "pcap",
      f"classic LE pcap, Ethernet/IPv4; D17 plan urls minus {DROP}, plus {ADD}; even urls plaintext GET :80 "
      "(some split over 2 segments), odd urls TLS ClientHello SNI :443, DNS query+A answer for each")
write("net_pcapng_d17", pcapng(frames(obs[::-1], v6=True)), "pcapng",
      "pcapng SHB+IDB+EPB, Ethernet; same observed set reversed + one IPv6 POST with a body that starts 'GET '")
write("net_decoy_renamed_txt", b"This is not a capture.\nGET /index.html HTTP/1.1 is just prose here.\n", "pcap",
      "plain text renamed .pcap, no URL / Host header", decoy=True, recon=False)
write("net_decoy_arp_only", pcap([b"\xff" * 6 + b"\x66\x77\x88\x99\xaa\xbb\x08\x06" + bytes(28)] * 3), "pcap",
      "valid pcap carrying only ARP frames: no fetch indicator", decoy=True, recon=False)
