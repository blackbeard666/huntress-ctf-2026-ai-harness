"""Generator for ovspec_*.{bin,json}: RS20-style packed overlays, each ENCODED forward with independent primitives
(pycryptodome ARC4, stdlib zlib/lzma/hashlib, hand-written encoders) -- never with lib.binary. The real D19 PK19 members
are copied from the cached Day-19 deliveries (GM-confirmed configs).
usage (repo root): python3 tests/data/binary_fixtures/ovspec_gen.py [<d19 single.elf> <d19 set2.elf>]"""
import hashlib, json, lzma, pathlib, random, struct, sys, zlib
from Crypto.Cipher import ARC4

HERE = pathlib.Path(__file__).parent
rol = lambda b, r: ((b << r) | (b >> (8 - r))) & 255
GEN = "python3 tests/data/binary_fixtures/ovspec_gen.py"
ORA = "python3 tests/data/binary_fixtures/ovspec_oracle.py"


def hcfg(cfg, key=0x5A):
    p = json.dumps(cfg, separators=(",", ":")).encode()
    return b"HCFG" + bytes([1, key]) + struct.pack("<HI", len(p), zlib.crc32(p)) + bytes(b ^ key for b in p)


def cfg(n):
    return {"campaign": f"BR20-{n:03d}", "domain": f"node-{n:03d}.day20.example.invalid",
            "mutex": f"Global\\HuntressBR20_{n:03d}", "url": f"https://node-{n:03d}.day20.example.invalid/api/BR20-{n:03d}"}


def host(seed):
    r = random.Random(seed)
    # an ELF-ish prefix with an early decoy magic occurrence (the question asks for the FINAL one)
    return b"\x7fELF\x02\x01\x01" + bytes(r.randrange(256) for _ in range(900)) + b"RS20-decoy-string" + \
        bytes(r.randrange(256) for _ in range(300))


def emit(name, data, off, question, expected, decoy=False, note=""):
    (HERE / f"ovspec_{name}.bin").write_bytes(data)
    (HERE / f"ovspec_{name}.json").write_text(json.dumps({
        "entry": "overlay_spec+overlay_spec_unpack", "question": question, "expected_offset": off if not decoy else None,
        "expected_size": len(data) - off if not decoy else None, "expected_config": expected if not decoy else "none",
        "decoy": decoy, "note": note, "generator_cmd": GEN, "oracle_cmd": f"{ORA} ovspec_{name}"}, indent=1) + "\n")


def lcg_bytes(seed, a, c, n, shift, pre):
    st, out = seed, []
    for _ in range(n):
        if pre:
            st = (a * st + c) & 0xFFFFFFFF
        out.append((st >> shift) & 255)
        if not pre:
            st = (a * st + c) & 0xFFFFFFFF
    return out


TAIL = (" Locate the unique CRC32-valid HCFG record: bytes 0..3 are ASCII HCFG, byte 4 is version, byte 5 is the XOR key,"
        " bytes 6..7 are the little-endian payload length, bytes 8..11 are the little-endian CRC32 of the decoded payload,"
        " and the payload begins at byte 12. XOR every payload byte with the one-byte key, verify CRC32, then parse the"
        " decoded UTF-8 JSON.")
PRE = "In evidence.zip, Use all d20-- members in ZIP central-directory order. "

# 1. index terms + SUB + multi-byte key, big-endian length, CRC32 hash
c = cfg(1); u = hcfg(c); key = bytes([0x13, 0x37, 0xC0, 0xDE]); seed = 0x6B
pk = bytes((((b ^ (i % 251) ^ seed) + key[i % 4]) & 255) for i, b in enumerate(u))
h = host(1); o = len(h)
d = h + b"RS20" + bytes([seed]) + key + struct.pack(">I", len(pk)) + struct.pack("<I", zlib.crc32(u)) + pk
emit("idx_sub_crc", d, o, PRE + "Find the final RS20 overlay. Read seed u8 at +4, the 4-byte key at +5, packed length u32be at +9, "
     "the CRC32 of the unpacked bytes u32le at +13, and packed bytes at +17. For each packed byte compute "
     "(byte SUB key[i % 4]) XOR seed XOR (i mod 251); verify the CRC32 and use the HCFG record at unpacked offset 0." + TAIL, c)

# 2. rol8 + NOT + nibble swap, sha256
c = cfg(2); u = hcfg(c, 0x33); k = 0xA5
sw = lambda x: ((x << 4) | (x >> 4)) & 255
pk = bytes(rol(sw(~(b ^ k) & 255), 3) for b in u)  # inverse of: swap(NOT ror8(byte,3)) XOR k
h = host(2); o = len(h)
d = h + b"RS20" + b"\x00" + bytes([k]) + b"\x00\x00" + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
emit("rot_not_swap", d, o, PRE + "Find the final RS20 overlay. Read k at +5, packed length u32le at +8, the 32-byte unpacked "
     "SHA-256 at +12, and packed bytes at +44. For each packed byte compute swap(NOT ror8(byte,3)) XOR k; verify the "
     "unpacked SHA-256 and use the HCFG record at unpacked offset 0." + TAIL, c)

# 3. previous-cipher chaining with an IV field
c = cfg(3); u = hcfg(c, 0x21); iv, k1 = 0x9C, 0x47
pk, prev = bytearray(), iv
for b in u:
    e = b ^ k1 ^ prev
    pk.append(e); prev = e
h = host(3); o = len(h)
d = h + b"RS20" + bytes([iv, k1]) + b"\x00\x00" + struct.pack("<I", len(pk)) + hashlib.md5(u).digest() + bytes(pk)
emit("prev_cipher_md5", d, o, PRE + "Find the final RS20 overlay. Read iv at +4, k1 at +5, packed length u32le at +8, the "
     "16-byte unpacked MD5 at +12, and packed bytes at +28. For each packed byte compute byte XOR previous packed byte "
     "XOR k1 (the first byte uses iv); verify the unpacked MD5 and use the HCFG record at unpacked offset 0." + TAIL, c)

# 4. previous-plain chaining (ADD), sequential prose
c = cfg(4); u = hcfg(c, 0x11); k1 = 0x2E
pk, prev = bytearray(), 0
for b in u:
    pk.append(((b ^ k1) - prev) & 255); prev = b
h = host(4); o = len(h)
d = h + b"RS20" + bytes([0, k1, 0, 0]) + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + bytes(pk)
emit("prev_plain", d, o, PRE + "Find the final RS20 overlay. Read k1 at +5, packed length u32le at +8, the 32-byte unpacked "
     "SHA-256 at +12, and packed bytes at +44. For each packed byte compute (byte ADD previous unpacked byte) XOR k1, "
     "where the previous unpacked byte starts at 0; verify the unpacked SHA-256 and use the HCFG record at unpacked offset 0."
     + TAIL, c)

# 5. reversed packed order
c = cfg(5); u = hcfg(c, 0x44); k1 = 0x71
pk = bytes(b ^ k1 for b in u)[::-1]
h = host(5); o = len(h)
d = h + b"RS20" + bytes([0, k1, 0, 0]) + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
emit("reversed", d, o, PRE + "Find the final RS20 overlay. Read k1 at +5, packed length u32le at +8, the 32-byte unpacked "
     "SHA-256 at +12, and packed bytes at +44. Reverse the packed bytes, then for each byte compute byte XOR k1; verify "
     "the unpacked SHA-256 and use the HCFG record at unpacked offset 0." + TAIL, c)

# 6. RC4(key) keystream + zlib
c = cfg(6); u = hcfg(c, 0x55); key = b"Rs20kEy!"
pk = ARC4.new(key).encrypt(zlib.compress(u, 9))
h = host(6); o = len(h)
d = h + b"RS20" + b"\x00\x00" + key + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
emit("rc4_zlib", d, o, PRE + "Find the final RS20 overlay. Read the 8-byte key at +6, packed length u32le at +14, the "
     "32-byte unpacked SHA-256 at +18, and packed bytes at +50. For each packed byte compute byte XOR RC4(key); then "
     "zlib-decompress, verify the unpacked SHA-256 and use the HCFG record at unpacked offset 0." + TAIL, c)

# 7. LCG(seed, a, c) keystream (explicit >> 16) + lzma
c = cfg(7); u = hcfg(c, 0x66); sd = 0xC0FFEE11
z = lzma.compress(u)
pk = bytes(b ^ s for b, s in zip(z, lcg_bytes(sd, 1103515245, 12345, len(z), 16, True)))
h = host(7); o = len(h)
d = h + b"RS20" + struct.pack("<I", sd) + struct.pack("<I", len(pk)) + hashlib.sha1(u).digest() + pk
emit("lcg_lzma", d, o, PRE + "Find the final RS20 overlay. Read seed u32le at +4, packed length u32le at +8, the 20-byte "
     "unpacked SHA-1 at +12, and packed bytes at +32. For each packed byte compute byte XOR (LCG(seed, 1103515245, 12345) "
     ">> 16); then LZMA-decompress, verify the unpacked SHA-1 and use the HCFG record at unpacked offset 0." + TAIL, c)

# 8. sequential prose steps + RLE (count, value)
c = cfg(8); u = hcfg(c, 0x77); k1 = 0x3C
rle = bytearray(); j = 0
while j < len(u):
    n = 1
    while j + n < len(u) and u[j + n] == u[j] and n < 255:
        n += 1
    rle += bytes([n, u[j]]); j += n
pk = bytes(rol(b, 2) ^ k1 for b in rle)
h = host(8); o = len(h)
d = h + b"RS20" + bytes([0, k1, 0, 0]) + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
emit("steps_rle", d, o, PRE + "Find the final RS20 overlay. Read k1 at +5, packed length u32le at +8, the 32-byte unpacked "
     "SHA-256 at +12, and packed bytes at +44. For each packed byte, XOR with k1, then rotate right by 2; then RLE-decode "
     "the (count, value) pairs, verify the unpacked SHA-256 and use the HCFG record at unpacked offset 0." + TAIL, c)

# 9. DECOY: stored hash corrupted (the transform still yields HCFG at 0 -- must be rejected, never guessed)
c = cfg(9); u = hcfg(c, 0x12); k1, k2 = 0x5D, 0xE1
ror = lambda b, r: ((b >> r) | (b << (8 - r))) & 255
pk = bytes(rol(b ^ k1, 3) ^ k2 for b in u)
bad = bytearray(hashlib.sha256(u).digest()); bad[7] ^= 1
h = host(9); o = len(h)
d = h + b"RS20" + bytes([0, k1, k2, 0]) + struct.pack("<I", len(pk)) + bytes(bad) + pk
emit("decoy_badhash", d, o, PRE + "Find the final RS20 overlay. Read k1 at +5, k2 at +6, packed length u32le at +8, the "
     "32-byte unpacked SHA-256 at +12, and packed bytes at +44. For each packed byte compute ror8(byte XOR k2,3) XOR k1; "
     "verify the unpacked SHA-256 and use the HCFG record at unpacked offset 0." + TAIL, None, decoy=True,
     note="stored SHA-256 has one flipped bit")

# 10. DECOY: PK19-layout overlay but the question names RS20 (wrong magic) + truncated length
c = cfg(10); u = hcfg(c, 0x12)
pk = bytes(rol(b ^ k1, 3) ^ k2 for b in u)
h = host(10); o = len(h)
d = h.replace(b"RS20", b"XX20") + b"PK19" + bytes([0, k1, k2, 0]) + struct.pack("<I", len(pk) + 999) + \
    hashlib.sha256(u).digest() + pk
emit("decoy_wrongmagic", d, o, PRE + "Find the final RS20 overlay. Read k1 at +5, k2 at +6, packed length u32le at +8, the "
     "32-byte unpacked SHA-256 at +12, and packed bytes at +44. For each packed byte compute ror8(byte XOR k2,3) XOR k1; "
     "verify the unpacked SHA-256 and use the HCFG record at unpacked offset 0." + TAIL, None, decoy=True,
     note="only a PK19 overlay present, length field overruns EOF")

# real D19 members (GM-confirmed: single = variant-000, mastery delivery 2 = variant-007)
if len(sys.argv) == 3:
    q19 = ("In evidence.zip, Use all d19-- members in ZIP central-directory order. Find the final PK19 overlay. Read k1 at "
           "+5, k2 at +6, packed length u32le at +8, the 32-byte unpacked SHA-256 at +12, and packed bytes at +44. For "
           "each packed byte compute ror8(byte XOR k2,3) XOR k1; verify the unpacked SHA-256 and use the HCFG record at "
           "unpacked offset 0." + TAIL)
    for nm, src, n in (("d19_single", sys.argv[1], 0), ("d19_mastery_set2", sys.argv[2], 7)):
        b = pathlib.Path(src).read_bytes()
        exp = {"campaign": f"BR19-{n:03d}", "domain": f"node-{n:03d}.day19.example.invalid",
               "mutex": f"Global\\HuntressBR19_{n:03d}", "url": f"https://node-{n:03d}.day19.example.invalid/api/BR19-{n:03d}"}
        emit(nm, b, 10808, q19, exp, note="GM-confirmed D19 answers (config_* + overlay_offset 10808 / size 424)")
        j = json.loads((HERE / f"ovspec_{nm}.json").read_text())
        j["generator_cmd"] = (f"{GEN} <d19 single.elf> <d19 set2.elf>  (d19--variant-00{n}.elf from the cached D19 "
                              "evidence.zip, AES-zip member)")
        j["oracle_cmd"] = (f"GM CORRECT (challenges/day19/binary-jack-in-the-box confirmed.json / case expected.json) + "
                           f"{ORA} ovspec_{nm}")
        (HERE / f"ovspec_{nm}.json").write_text(json.dumps(j, indent=1) + "\n")
