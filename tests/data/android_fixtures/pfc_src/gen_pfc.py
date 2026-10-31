"""packet-frame-codec-family (atlas row 113) -> pfc_*.{apk,json}: D28 `packet` mutations (u16/varint length, CRC16 /
CRC32 / sum8 checksums, encoded payloads, frame streams with a bad-checksum decoy frame, TLV records).

Writer: python zipfile + this file's own bitwise CRC32 / CRC16 / sum8 (no zlib/binascii checksum calls).
Oracle: each fixture's `oracle_cmd` is an independent shell pipeline (unzip -p | jq | python3 -I -c using zlib.crc32 /
binascii.crc_hqx) that parses that one layout, VERIFIES the checksum and prints the payload; this generator runs it and
asserts it equals the rolled token (decoys: the oracle prints BADSUM). expected = the oracle output.
Run:  python3 tests/data/android_fixtures/pfc_src/gen_pfc.py   (from the repo root; deterministic seed)
"""
import base64, json, random, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "tests/data/android_fixtures"
rng = random.Random(0x113)
MANIFEST = b'<?xml version="1.0" encoding="utf-8"?>\n<manifest package="com.huntress.arena" />\n'


def tok():
    return "ANS-" + "".join(rng.choice("0123456789ABCDEF") for _ in range(16))


def crc32(b):
    c = 0xFFFFFFFF
    for x in b:
        c ^= x
        for _ in range(8):
            c = (c >> 1) ^ 0xEDB88320 if c & 1 else c >> 1
    return c ^ 0xFFFFFFFF


def crc16(b, init):  # CCITT poly 0x1021, MSB-first (init 0xFFFF = CCITT-FALSE, 0 = XMODEM)
    c = init
    for x in b:
        c ^= x << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c


def varint(n):
    o = bytearray()
    while True:
        o.append((n & 0x7F) | (0x80 if n > 0x7F else 0))
        n >>= 7
        if not n:
            return bytes(o)


def pz(day, codec, **kw):
    d = {"schema": "huntress.mobile.puzzle.v1", "day": day, "codec": codec}
    d.update(kw)
    return json.dumps(d, separators=(",", ":")).encode()


def apk(path, puzzle, extra=()):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", MANIFEST)
        z.writestr("assets/huntress_puzzle.json", puzzle)
        for n, b in extra:
            z.writestr(n, b)


J = "unzip -p {f} assets/huntress_puzzle.json | jq -r"
PY = "python3 -I -c"
fx = []

# 1. HA | u16 BE len | payload = token ^ (key+i) | CRC32 BE over header+payload; data = hex
t, k = tok(), rng.randrange(1, 256)
pay = bytes(x ^ ((k + i) & 255) for i, x in enumerate(t.encode()))
hdr = b"HA" + len(pay).to_bytes(2, "big")
fr = hdr + pay + crc32(hdr + pay).to_bytes(4, "big")
fx.append(("pfc_u16be_crc32_xor", t, False, f"HA | u16 BE len | token^(key+i), key {k} | CRC32 BE over header+payload (hex)",
           lambda p, fr=fr, k=k: apk(p, pz(31, "frame", data=fr.hex(), key=k)),
           J + " '.data, .key' | " + PY + " 'import sys,zlib;d,k=sys.stdin.read().split();b=bytes.fromhex(d);n=int.from_bytes(b[2:4],\"big\");p=b[4:4+n];ok=zlib.crc32(b[:4+n]).to_bytes(4,\"big\")==b[4+n:8+n];print(bytes(x^((int(k)+i)&255) for i,x in enumerate(p)).decode() if ok else \"BADSUM\")'"))

# 2. HA 0x02 | u16 LE len | payload = base64(token) | CRC16-CCITT-FALSE LE over payload only; data = base64(frame)
t = tok()
pay = base64.b64encode(t.encode())
fr = b"HA\x02" + len(pay).to_bytes(2, "little") + pay + crc16(pay, 0xFFFF).to_bytes(2, "little")
fx.append(("pfc_ver_u16le_crc16_b64", t, False, "HA ver=2 | u16 LE len | base64(token) | CRC16-CCITT-FALSE LE over payload (base64 frame)",
           lambda p, fr=fr: apk(p, pz(31, "wire", data=base64.b64encode(fr).decode())),
           J + " .data | base64 -d | " + PY + " 'import sys,binascii,base64;b=sys.stdin.buffer.read();n=int.from_bytes(b[3:5],\"little\");p=b[5:5+n];ok=binascii.crc_hqx(p,0xFFFF).to_bytes(2,\"little\")==b[5+n:7+n];print(base64.b64decode(p).decode() if ok else \"BADSUM\")'"))

# 3. stream of CA FE | varint len | payload ^ (key+i) | sum8 frames: hello, DECOY token with a bad sum8, real token
t, d, k = tok(), tok(), rng.randrange(1, 200)


def f3(p, bad=False):
    b = b"\xca\xfe" + varint(len(p)) + p
    return b + bytes([(sum(b) + (1 if bad else 0)) & 255])


enc = lambda s: bytes(x ^ ((k + i) & 255) for i, x in enumerate(s.encode()))  # noqa: E731
st = f3(b"seq=1;hello-arena") + f3(enc(d), bad=True) + f3(enc(t))
fx.append(("pfc_stream_varint_sum8", t, False,
           f"stream of CA FE | varint len | payload^(key+i) | sum8 frames; frame 2 = decoy {d} with a bad sum8 (int list)",
           lambda p, st=st, k=k: apk(p, pz(31, "packet", frames=list(st), key=k)),
           "unzip -p {f} assets/huntress_puzzle.json | " + PY + " 'import sys,json\nj=json.load(sys.stdin);b=bytes(j[\"frames\"]);k=j[\"key\"];i=0\nwhile i<len(b):\n n=b[i+2];p=b[i+3:i+3+n]\n if sum(b[i:i+3+n])&255==b[i+3+n] and p[:3]!=b\"seq\": print(bytes(x^((k+j)&255) for j,x in enumerate(p)).decode())\n i+=4+n'",
           ))

# 4. HA | TLV (u8 type, u8 len): 0x01 seq, 0x02 nonce, 0x10 base64(token reversed) | CRC16-XMODEM BE over all; an asset
t = tok()
tlv = b"".join(bytes([ty, len(v)]) + v for ty, v in
               ((1, (7).to_bytes(4, "big")), (2, bytes(rng.randrange(256) for _ in range(8))),
                (0x10, base64.b64encode(t[::-1].encode()))))
body = b"HA" + tlv
pkt = body + crc16(body, 0).to_bytes(2, "big")
fx.append(("pfc_tlv_crc16_asset", t, False, "assets/session.pkt = HA | TLV{seq, nonce, 0x10: base64(reversed token)} | CRC16-XMODEM BE",
           lambda p, pkt=pkt: apk(p, pz(31, "tlv", data="session.pkt"), [("assets/session.pkt", pkt)]),
           "unzip -p {f} assets/session.pkt | " + PY + " 'import sys,binascii,base64\nb=sys.stdin.buffer.read();ok=binascii.crc_hqx(b[:-2],0).to_bytes(2,\"big\")==b[-2:];i=2\nwhile ok and i<len(b)-2:\n t,n=b[i],b[i+1]\n if t==16: print(base64.b64decode(b[i+2:i+2+n]).decode()[::-1])\n i+=2+n\nprint(\"\" if ok else \"BADSUM\",end=\"\")'"))

# 5. DECOY: layout of #1 (payload token ^ (key+i)) but the CRC32 is off by one
t, k = tok(), rng.randrange(1, 256)
pay = bytes(x ^ ((k + i) & 255) for i, x in enumerate(t.encode()))
hdr = b"HA" + len(pay).to_bytes(2, "big")
fr = hdr + pay + ((crc32(hdr + pay) + 1) & 0xFFFFFFFF).to_bytes(4, "big")
fx.append(("pfc_decoy_badcrc32", None, True, f"DECOY: HA | u16 BE len | token^(key+i), key {k} | CRC32 off by one -> reject the frame",
           lambda p, fr=fr, k=k: apk(p, pz(31, "frame", data=fr.hex(), key=k)), fx[0][5]))

# 6. DECOY: TLV of #4 with a CRC16 off by one
t = tok()
tlv = b"".join(bytes([ty, len(v)]) + v for ty, v in ((1, b"\x00\x00\x00\x08"), (0x10, base64.b64encode(t[::-1].encode()))))
body = b"HA" + tlv
pkt = body + ((crc16(body, 0) ^ 1)).to_bytes(2, "big")
fx.append(("pfc_decoy_tlv_badcrc16", None, True, "DECOY: HA | TLV{seq, 0x10: base64(reversed token)} | CRC16-XMODEM off by one",
           lambda p, pkt=pkt: apk(p, pz(31, "tlv", data="session.pkt"), [("assets/session.pkt", pkt)]), fx[3][5]))

for name, t, decoy, why, build, oracle in fx:
    path = OUT / f"{name}.apk"
    build(path)
    oc = oracle.format(f=f"tests/data/android_fixtures/{name}.apk")
    got = subprocess.run(["bash", "-c", oc], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if decoy:
        assert got == "BADSUM", (name, got)
    else:
        assert got == t, (name, got, t)
    (OUT / f"{name}.json").write_text(json.dumps({
        "entry": "puzzle_candidates", "expected": None if decoy else got, "decoy": decoy, "_why": why,
        "generator_cmd": f"python3 tests/data/android_fixtures/pfc_src/gen_pfc.py {name}  # python zipfile + bitwise CRC32/CRC16/sum8",
        "oracle_cmd": oc}, indent=1) + "\n")
    print(name, got)
