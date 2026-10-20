"""Independent oracle for ovspec_rs20_* fixtures (no lib.binary): overlay start from lief (Binary.overlay = bytes past
the ELF image) must hold the final b'RS20'; each stream decoded by HAND-WRITTEN code per layout, PackBits via PIL's
C 'packbits' decoder, RC4 via pycryptodome. Prints the decoded HCFG JSON (or 'none'); exit 1 on any disagreement.
usage (repo root): python3 tests/data/binary_fixtures/rs20_oracle.py [ovspec_rs20_<name> ...]"""
import hashlib, json, pathlib, struct, sys, zlib
import lief
from Crypto.Cipher import ARC4
from PIL import Image

HERE = pathlib.Path(__file__).parent
ror = lambda b, r: ((b >> r) | (b << (8 - r))) & 255


def rec(u):
    if not u or u[:4] != b"HCFG":
        return None
    k, n, crc = u[5], *struct.unpack_from("<HI", u, 6)
    p = bytes(b ^ k for b in u[12:12 + n])
    return json.loads(p) if zlib.crc32(p) == crc else None


def sha(d, o, u):
    return u if hashlib.sha256(u).digest() == d[o + 12:o + 44] else None


def pil_packbits(b, n):
    return Image.frombytes("L", (n, 1), b, "packbits", "L").tobytes()


def packbits(d, o):
    k1 = d[o + 5]; n, = struct.unpack_from("<I", d, o + 8)
    r = bytes(b ^ k1 for b in d[o + 44:o + 44 + n])
    for size in range(len(r), 64 * len(r)):    # PIL needs the decoded width: take the shortest that consumes it all
        try:
            u = pil_packbits(r, size)
        except Exception:
            continue
        if sha(d, o, u):
            return u
    return None


def roll_lcg8(d, o):
    key, mul, inc = d[o + 5], d[o + 6], d[o + 7]; n, = struct.unpack_from("<I", d, o + 8); u = bytearray()
    for b in d[o + 44:o + 44 + n]:
        u.append(b ^ key); key = (key * mul + inc) % 256
    return sha(d, o, bytes(u))


def roll_xorprev(d, o):
    key = d[o + 5]; n, = struct.unpack_from("<I", d, o + 8); u = bytearray()
    for b in d[o + 16:o + 16 + n]:
        u.append(ror(b ^ key, 1)); key ^= b
    return bytes(u) if zlib.crc32(u) == struct.unpack_from("<I", d, o + 12)[0] else None


def rc4_prose(d, o):
    n, = struct.unpack_from("<I", d, o + 24)
    u = ARC4.new(d[o + 8:o + 24]).decrypt(d[o + 60:o + 60 + n])
    return u if hashlib.sha256(u).digest() == d[o + 28:o + 60] else None


def blockrev(d, o):
    bs, k1 = d[o + 5], d[o + 6]; n, = struct.unpack_from("<I", d, o + 8); p = d[o + 44:o + 44 + n]
    p = b"".join(p[k:k + bs][::-1] for k in range(0, len(p), bs))
    return sha(d, o, bytes(ror(b, 3) ^ k1 for b in p))


def ror_idx(d, o):
    k1 = d[o + 5]; n, = struct.unpack_from("<I", d, o + 8)
    return sha(d, o, bytes(ror(b, i % 8) ^ k1 for i, b in enumerate(d[o + 44:o + 44 + n])))


def sbox_zlib(d, o):
    n, = struct.unpack_from("<I", d, o + 8); t = d[o + 44:o + 300]
    return sha(d, o, zlib.decompress(bytes(t[b] for b in d[o + 300:o + 300 + n])))


def unstated_key(d, o):
    n, = struct.unpack_from("<I", d, o + 8); p = d[o + 44:o + 44 + n]
    k = p[0] ^ ord("H")                       # known plaintext: out[0] == 'H' at i = 0
    return sha(d, o, bytes(b ^ k ^ (i % 7) for i, b in enumerate(p)))


def roll_unstated(d, o):
    mul, inc = d[o + 6], d[o + 7]; n, = struct.unpack_from("<I", d, o + 8); p = d[o + 44:o + 44 + n]
    key = (p[0] - ord("H")) & 255              # known plaintext fixes the start key
    u = bytearray()
    for b in p:
        u.append((b - key) & 255); key = (key * mul + inc) & 255
    return sha(d, o, bytes(u))


DEC = {"packbits": packbits, "decoy_packbits_hash": packbits, "roll_lcg8": roll_lcg8, "roll_xorprev": roll_xorprev,
       "rc4_prose": rc4_prose, "blockrev": blockrev, "ror_idx": ror_idx, "sbox_zlib": sbox_zlib,
       "unstated_key": unstated_key, "decoy_unstated_hash": unstated_key, "roll_unstated": roll_unstated,
       "decoy_noverlay": packbits}
bad = 0
for stem in sys.argv[1:] or sorted(p.stem for p in HERE.glob("ovspec_rs20_*.json")):
    f = json.loads((HERE / f"{stem}.json").read_text()); d = (HERE / f"{stem}.bin").read_bytes()
    elf = lief.parse(str(HERE / f"{stem}.bin")); ov = bytes(elf.overlay)   # keep elf alive: overlay is a view
    o = len(d) - len(ov) if ov[:4] == b"RS20" else None
    got = rec(DEC[stem[len("ovspec_rs20_"):]](d, o)) if o is not None else None
    exp = f["expected_config"]
    ok = (got is None and exp == "none" or got == exp) and (
        got is None or (o, len(ov)) == (f["expected_offset"], f["expected_size"]) and o == d.rfind(b"RS20"))
    bad += not ok
    print(("ok  " if ok else "BAD ") + stem, o, len(ov), json.dumps(got) if got else "none")
sys.exit(1 if bad else 0)
