"""Generator for ovspec_rs20_*.{bin,json}: Day-20 `RS20` overlay guesses appended to a REAL gcc-built ELF
(rs20_host.elf = `gcc -Os -s -o rs20_host.elf rs20_host.c`; its .rodata holds an earlier 'RS20 stub' string, so the
FINAL magic is the overlay). Each packed stream is ENCODED forward here with independent primitives (pycryptodome
ARC4, stdlib zlib/hashlib, hand-written PackBits / rolling-key encoders) -- never with lib.binary. expected_* come from
rs20_oracle.py (lief overlay start + PIL PackBits decoder + pycryptodome + hand decoders).
usage (repo root): python3 tests/data/binary_fixtures/rs20_gen.py && python3 tests/data/binary_fixtures/rs20_oracle.py"""
import hashlib, json, pathlib, struct, zlib
from Crypto.Cipher import ARC4

HERE = pathlib.Path(__file__).parent
ELF = (HERE / "rs20_host.elf").read_bytes()
rol = lambda b, r: ((b << r) | (b >> (8 - r))) & 255
GEN = ("gcc -Os -s -o tests/data/binary_fixtures/rs20_host.elf tests/data/binary_fixtures/rs20_host.c && "
       "python3 tests/data/binary_fixtures/rs20_gen.py")
ORA = "python3 tests/data/binary_fixtures/rs20_oracle.py"
PRE = "In evidence.zip, Use all d20-- members in ZIP central-directory order. "
TAIL = (" Locate the unique CRC32-valid HCFG record: bytes 0..3 are ASCII HCFG, byte 4 is version, byte 5 is the XOR key,"
        " bytes 6..7 are the little-endian payload length, bytes 8..11 are the little-endian CRC32 of the decoded payload,"
        " and the payload begins at byte 12. XOR every payload byte with the one-byte key, verify CRC32, then parse the"
        " decoded UTF-8 JSON.")
assert ELF.find(b"RS20") >= 0


def hcfg(cfg, key=0x5A):
    p = json.dumps(cfg, separators=(",", ":")).encode()
    return b"HCFG" + bytes([1, key]) + struct.pack("<HI", len(p), zlib.crc32(p)) + bytes(b ^ key for b in p)


def cfg(n):
    return {"campaign": f"BR20-{n:03d}", "domain": f"rs-{n:03d}.day20.example.invalid",
            "mutex": f"Global\\HuntressRS20_{n:03d}", "url": f"https://rs-{n:03d}.day20.example.invalid/api/BR20-{n:03d}"}


def emit(name, overlay, question, expected, decoy=False, note=""):
    data = ELF + overlay
    (HERE / f"ovspec_rs20_{name}.bin").write_bytes(data)
    (HERE / f"ovspec_rs20_{name}.json").write_text(json.dumps({
        "entry": "overlay_spec+overlay_spec_unpack", "question": PRE + question + TAIL,
        "expected_offset": None if decoy else len(ELF), "expected_size": None if decoy else len(overlay),
        "expected_config": "none" if decoy else expected, "decoy": decoy, "note": note,
        "generator_cmd": GEN, "oracle_cmd": f"{ORA} ovspec_rs20_{name}"}, indent=1) + "\n")


def packbits(b):   # TIFF/Apple PackBits encoder (runs >= 3 -> repeat packet, else literal packets of <= 128)
    out, i, lit = bytearray(), 0, bytearray()

    def flush():
        while lit:
            ch = lit[:128]
            out.append(len(ch) - 1); out.extend(ch); del lit[:128]
    while i < len(b):
        n = 1
        while i + n < len(b) and b[i + n] == b[i] and n < 128:
            n += 1
        if n >= 3:
            flush(); out += bytes([257 - n, b[i]]); i += n
        else:
            lit.extend(b[i:i + n]); i += n
    flush()
    return bytes(out)


def pad_hcfg(c, key):   # a record with long runs so PackBits actually compresses
    return hcfg(c, key) + b"\x00" * 40 + b"\xcc" * 300


def hdr32(u):
    return struct.pack("<I", 0) + hashlib.sha256(u).digest()


# (a) PackBits after XOR k1
c = cfg(21); u = pad_hcfg(c, 0x2B); k1 = 0x6D
pk = bytes(b ^ k1 for b in packbits(u))
ov = b"RS20" + bytes([1, k1, 0, 0]) + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
Q_PB = ("Find the final RS20 overlay. Read k1 at +5, packed length u32le at +8, the 32-byte unpacked SHA-256 at +12, "
        "and packed bytes at +44. For each packed byte compute byte XOR k1; then PackBits-decode the result (n<128: copy "
        "n+1 literal bytes; n>128: repeat the next byte 257-n times), verify the unpacked SHA-256 and use the HCFG record "
        "at unpacked offset 0.")
emit("packbits", ov, Q_PB, c)

# (a') DECOY: same layout, the stored SHA-256 is of a different record
bad = hashlib.sha256(pad_hcfg(cfg(99), 0x2B)).digest()
emit("decoy_packbits_hash", ov[:12] + bad + ov[44:], Q_PB, None, decoy=True, note="SHA-256 field belongs to another record")

# (b) rolling key: key = (key * mul + inc) mod 256 after each byte, starting at k0
c = cfg(22); u = hcfg(c, 0x31); k0, mul, inc = 0xA7, 0x1D, 0x53
pk, key = bytearray(), k0
for b in u:
    pk.append(b ^ key); key = (key * mul + inc) % 256
ov = b"RS20" + bytes([1, k0, mul, inc]) + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + bytes(pk)
emit("roll_lcg8", ov, "Find the final RS20 overlay. Read k0 at +5, mul at +6, inc at +7, packed length u32le at +8, the "
     "32-byte unpacked SHA-256 at +12, and packed bytes at +44. For each packed byte compute byte XOR key, where key "
     "starts at k0 and key = (key * mul + inc) mod 256 after each byte; verify the unpacked SHA-256 and use the HCFG "
     "record at unpacked offset 0.", c)

# (b') rolling key chained on the cipher: key ^= previous packed byte
c = cfg(23); u = hcfg(c, 0x42); k0 = 0x3E
pk, key = bytearray(), k0
for b in u:
    e = rol(b, 1) ^ key; pk.append(e); key ^= e
ov = b"RS20" + bytes([1, k0, 0, 0]) + struct.pack("<I", len(pk)) + struct.pack("<I", zlib.crc32(u)) + bytes(pk)
emit("roll_xorprev", ov, "Find the final RS20 overlay. Read k0 at +5, packed length u32le at +8, the CRC32 of the "
     "unpacked bytes u32le at +12, and packed bytes at +16. For each packed byte compute ror8(byte XOR key, 1), where "
     "key starts at k0 and, after each byte, key ^= previous packed byte; verify the CRC32 and use the HCFG record at "
     "unpacked offset 0.", c)

# (c) RC4 with the key bytes in the header, prose form
c = cfg(24); u = hcfg(c, 0x13); key = bytes(range(0xB0, 0xC0))
pk = ARC4.new(key).encrypt(u)
ov = b"RS20" + b"\x01\x10\x00\x00" + key + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
emit("rc4_prose", ov, "Find the final RS20 overlay. Read the 16-byte RC4 key at +8, packed length u32le at +24, the "
     "32-byte unpacked SHA-256 at +28, and packed bytes at +60. RC4-decrypt the packed bytes with the key, verify the "
     "unpacked SHA-256 and use the HCFG record at unpacked offset 0.", c)

# (d) reverse-shuffle: each block of `block` bytes reversed (block size in the header), then ror8/xor
c = cfg(25); u = hcfg(c, 0x24); bs, k1 = 13, 0x9B
enc = bytes(rol(b ^ k1, 3) for b in u)
pk = b"".join(enc[k:k + bs][::-1] for k in range(0, len(enc), bs))
ov = b"RS20" + bytes([1, bs, k1, 0]) + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
emit("blockrev", ov, "Find the final RS20 overlay. Read the block size u8 at +5, k1 at +6, packed length u32le at +8, "
     "the 32-byte unpacked SHA-256 at +12, and packed bytes at +44. Reverse each block of the packed bytes (the last "
     "block may be short), then for each byte compute ror8(byte, 3) XOR k1; verify the unpacked SHA-256 and use the "
     "HCFG record at unpacked offset 0.", c)

# (e) rotate by index
c = cfg(26); u = hcfg(c, 0x35); k1 = 0x4C
pk = bytes(rol(b ^ k1, i % 8) for i, b in enumerate(u))
ov = b"RS20" + bytes([1, k1, 0, 0]) + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
emit("ror_idx", ov, "Find the final RS20 overlay. Read k1 at +5, packed length u32le at +8, the 32-byte unpacked SHA-256 "
     "at +12, and packed bytes at +44. For each packed byte compute ror8(byte, i % 8) XOR k1; verify the unpacked "
     "SHA-256 and use the HCFG record at unpacked offset 0.", c)

# (f) byte map (256-byte substitution table in the header) then zlib
c = cfg(27); u = hcfg(c, 0x46)
perm = [(i * 167 + 59) % 256 for i in range(256)]        # odd multiplier -> a permutation; table = inverse map
inv = [0] * 256
for i, v in enumerate(perm):
    inv[v] = i
z = zlib.compress(u, 9); pk = bytes(perm[b] for b in z)
ov = b"RS20" + b"\x01\x00\x00\x00" + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + bytes(inv) + pk
emit("sbox_zlib", ov, "Find the final RS20 overlay. Read packed length u32le at +8, the 32-byte unpacked SHA-256 at +12, "
     "the 256-byte table at +44, and packed bytes at +300. For each packed byte compute table[byte]; then "
     "zlib-decompress, verify the unpacked SHA-256 and use the HCFG record at unpacked offset 0.", c)

# known-plaintext: the question names k but no header field stores it
c = cfg(28); u = hcfg(c, 0x57); k = 0xD2
pk = bytes(b ^ k ^ (i % 7) for i, b in enumerate(u))
ov = b"RS20" + b"\x01\x00\x00\x00" + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + pk
Q_KP = ("Find the final RS20 overlay. Read packed length u32le at +8, the 32-byte unpacked SHA-256 at +12, and packed "
        "bytes at +44. For each packed byte compute byte XOR k XOR (i mod 7); verify the unpacked SHA-256 and use the "
        "HCFG record at unpacked offset 0.")
emit("unstated_key", ov, Q_KP, c, note="k is not stored; recoverable only from the HCFG/ver-1 known plaintext + hash")

# known-plaintext DECOY: same question, hash of other bytes -> must stay None (no guess)
emit("decoy_unstated_hash", ov[:12] + hashlib.sha256(u + b"\0").digest() + ov[44:], Q_KP, None, decoy=True,
     note="unstated k recovers an HCFG prefix but the SHA-256 does not verify")

# rolling key with an unstated start value
c = cfg(29); u = hcfg(c, 0x68); key, mul, inc = 0x5E, 0x05, 0x11
pk = bytearray()
for b in u:
    pk.append((b + key) & 255); key = (key * mul + inc) & 255
ov = b"RS20" + bytes([1, 0, mul, inc]) + struct.pack("<I", len(pk)) + hashlib.sha256(u).digest() + bytes(pk)
emit("roll_unstated", ov, "Find the final RS20 overlay. Read mul at +6, inc at +7, packed length u32le at +8, the 32-byte "
     "unpacked SHA-256 at +12, and packed bytes at +44. For each packed byte compute byte SUB key; key = (key * mul + "
     "inc) mod 256 after each byte; verify the unpacked SHA-256 and use the HCFG record at unpacked offset 0.", c,
     note="initial key unstated: known-plaintext recovery")

# DECOY: the ELF alone (its .rodata 'RS20 stub' string is not an overlay)
emit("decoy_noverlay", b"", Q_PB, None, decoy=True, note="no overlay; only the .rodata 'RS20 stub v1' string")
