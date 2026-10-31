"""multi-frame-seq-nonce-reorder (atlas row 114) -> snr_*.{apk,json}: magic-prefixed frames carrying seq + nonce
fields, arriving out of order with a replayed duplicate, a stale (reused) nonce and a bad-checksum decoy frame.

Writer: python zipfile + this file's own bitwise CRC32 / CRC16 / sum8 (no zlib/binascii checksum calls).
Oracle: each fixture's `oracle_cmd` is an independent shell pipeline (unzip -p | jq | python3 -I -c using zlib.crc32 /
binascii.crc_hqx) that parses that one layout, VERIFIES each frame's checksum, keeps the first frame per nonce, orders by
seq, joins and prints the token (NOMATCH when the join is not a token); this generator runs it and asserts it equals the
rolled token (decoys: NOMATCH). expected = the oracle output.
Run:  python3 tests/data/android_fixtures/snr_src/gen_snr.py   (from the repo root; deterministic seed)
"""
import base64, json, random, re, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "tests/data/android_fixtures"
rng = random.Random(0x114)
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


def crc16(b, init):  # CCITT poly 0x1021, MSB-first (init 0 = XMODEM)
    c = init
    for x in b:
        c ^= x << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c


def pz(codec, **kw):
    d = {"schema": "huntress.mobile.puzzle.v1", "day": 31, "codec": codec}
    d.update(kw)
    return json.dumps(d, separators=(",", ":")).encode()


def apk(path, puzzle, extra=()):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", MANIFEST)
        z.writestr("assets/huntress_puzzle.json", puzzle)
        for n, b in extra:
            z.writestr(n, b)


def pieces(s, n):
    w = -(-len(s) // n)
    return [s[i:i + w] for i in range(0, len(s), w)]


PY = "python3 -I -c"
fx = []

# A. assets/stream.bin: "HF" | seq u8 | nonce u32 BE | len u8 | payload | CRC16-XMODEM BE over the whole frame.
#    Arrival: seq2, seq0, seq3 BAD-CRC (junk), seq2 replay (same nonce), seq3 stale (reused nonce of seq0, junk), seq3, seq1
def fa(seq, nonce, pay, bad=False):
    b = b"HF" + bytes([seq]) + nonce.to_bytes(4, "big") + bytes([len(pay)]) + pay
    return b + (crc16(b, 0) ^ (0x0100 if bad else 0)).to_bytes(2, "big")


def stream_a(t, drop1=False):
    pc = [x.encode() for x in pieces(t, 4)]
    nn = [rng.randrange(1, 1 << 32) for _ in range(4)]
    fr = [fa(2, nn[2], pc[2]), fa(0, nn[0], pc[0]), fa(3, rng.randrange(1, 1 << 32), b"ANS-0", bad=True),
          fa(2, nn[2], pc[2]), fa(3, nn[0], b"FFFFF"), fa(3, nn[3], pc[3]), fa(1, nn[1], pc[1], bad=drop1)]
    return b"".join(fr)


ORA_A = ("unzip -p {f} assets/stream.bin | " + PY + " 'import sys,binascii,re\nb=sys.stdin.buffer.read();i=0;seen=set();got={}\n"
         "while i<len(b):\n n=b[i+7];f=b[i:i+8+n];c=b[i+8+n:i+10+n];i+=10+n\n"
         " if binascii.crc_hqx(f,0).to_bytes(2,\"big\")!=c or f[3:7] in seen: continue\n"
         " seen.add(f[3:7]);got.setdefault(f[2],f[8:].decode())\n"
         "j=\"\".join(got[k] for k in sorted(got));print(j if re.fullmatch(\"ANS-[0-9A-F]{16}\",j) else \"NOMATCH\")'")
t = tok()
st = stream_a(t)
fx.append(("snr_u8seq_crc16_asset", t, False,
           "assets/stream.bin: HF | seq u8 | nonce u32be | len u8 | piece | CRC16-XMODEM BE; 7 frames out of order: "
           "bad-CRC decoy, replayed duplicate, stale reused-nonce frame",
           lambda p, st=st: apk(p, pz("frames", data="stream.bin"), [("assets/stream.bin", st)]), ORA_A))

# B. regression: 4-frame blob (puzzle data = hex): A5 5A 01 | len u16 LE | seq u16 LE | nonce 8 bytes | piece |
#    CRC32 LE over everything after the magic. Arrival: seq0 BAD-CRC (junk), seq1, seq0, seq1 replay.
def fb(seq, nonce, pay, bad=False):
    body = len(pay).to_bytes(2, "little") + seq.to_bytes(2, "little") + nonce + pay
    return b"\xa5\x5a\x01" + body + ((crc32(body) ^ (1 if bad else 0)).to_bytes(4, "little"))


t = tok()
pc = [x.encode() for x in pieces(t, 2)]
n0, n1 = rng.randbytes(8), rng.randbytes(8)
bl = fb(0, rng.randbytes(8), b"ANS-FFFFFFFF", bad=True) + fb(1, n1, pc[1]) + fb(0, n0, pc[0]) + fb(1, n1, pc[1])
fx.append(("snr_u16le_crc32_replay4", t, False,
           "4-frame hex blob: A5 5A 01 | u16le len | u16le seq | 8-byte nonce | piece | CRC32 LE after magic; "
           "frame 1 bad CRC, frame 4 a replay of frame 2",
           lambda p, bl=bl: apk(p, pz("frames", data=bl.hex())),
           "unzip -p {f} assets/huntress_puzzle.json | jq -r .data | " + PY + " 'import sys,zlib,re\n"
           "b=bytes.fromhex(sys.stdin.read().strip());i=0;seen=set();got={}\n"
           "while i<len(b):\n n=int.from_bytes(b[i+3:i+5],\"little\");body=b[i+3:i+15+n];c=b[i+15+n:i+19+n];i+=19+n\n"
           " if zlib.crc32(body).to_bytes(4,\"little\")!=c or body[4:12] in seen: continue\n"
           " seen.add(body[4:12]);got.setdefault(int.from_bytes(body[2:4],\"little\"),body[12:].decode())\n"
           "j=\"\".join(got[k] for k in sorted(got));print(j if re.fullmatch(\"ANS-[0-9A-F]{16}\",j) else \"NOMATCH\")'"))

# C. puzzle `frames` = list of base64 frames: "NF" | nonce u16 BE | seq u8 | len u8 | piece of base64(token) | sum8 of
#    the frame. Arrival: seq3, seq1, seq0 replay-to-come, seq2 bad sum, seq0 replay, seq2, seq1 stale (reused nonce)
def fc(seq, nonce, pay, bad=False):
    b = b"NF" + nonce.to_bytes(2, "big") + bytes([seq, len(pay)]) + pay
    return base64.b64encode(b + bytes([(sum(b) + (1 if bad else 0)) & 255])).decode()


t = tok()
pc = [x.encode() for x in pieces(base64.b64encode(t.encode()).decode(), 4)]
nn = rng.sample(range(1, 65536), 5)
fl = [fc(3, nn[3], pc[3]), fc(1, nn[1], pc[1]), fc(0, nn[0], pc[0]), fc(2, nn[4], b"QU5TLTAw", bad=True),
      fc(0, nn[0], pc[0]), fc(2, nn[2], pc[2]), fc(1, nn[3], b"AAAAAAA")]
fx.append(("snr_b64frames_sum8_list", t, False,
           "puzzle frames[] = base64 frames NF | nonce u16be | seq u8 | len u8 | piece of base64(token) | sum8; "
           "bad-sum frame, replay, stale reused nonce",
           lambda p, fl=fl: apk(p, pz("frames", frames=fl)),
           "unzip -p {f} assets/huntress_puzzle.json | jq -r \".frames[]\" | " + PY + " 'import sys,base64,re\n"
           "seen=set();got={}\nfor l in sys.stdin.read().split():\n f=base64.b64decode(l)\n"
           " if sum(f[:-1])&255!=f[-1] or f[2:4] in seen: continue\n"
           " seen.add(f[2:4]);got.setdefault(f[4],f[6:-1].decode())\n"
           "j=base64.b64decode(\"\".join(got[k] for k in sorted(got))).decode();print(j if re.fullmatch(\"ANS-[0-9A-F]{16}\",j) else \"NOMATCH\")'"))

# D. DECOY: layout of A, but the only seq1 frame carries a bad CRC -> the join misses a piece
t = tok()
st = stream_a(t, drop1=True)
fx.append(("snr_decoy_missing_piece", None, True,
           "DECOY: stream of A, the only seq-1 frame has a bad CRC16 -> no complete token",
           lambda p, st=st: apk(p, pz("frames", data="stream.bin"), [("assets/stream.bin", st)]), ORA_A))

for name, t, decoy, why, build, oracle in fx:
    path = OUT / f"{name}.apk"
    build(path)
    oc = oracle.replace("{f}", f"tests/data/android_fixtures/{name}.apk")
    got = subprocess.run(["bash", "-c", oc], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if decoy:
        assert got == "NOMATCH", (name, got)
    else:
        assert got == t, (name, got, t)
    (OUT / f"{name}.json").write_text(json.dumps({
        "entry": "puzzle_candidates", "expected": None if decoy else got, "decoy": decoy, "_why": why,
        "generator_cmd": f"python3 tests/data/android_fixtures/snr_src/gen_snr.py  # {name}; python zipfile + bitwise CRC32/CRC16/sum8",
        "oracle_cmd": oc}, indent=1) + "\n")
    print(name, got)
