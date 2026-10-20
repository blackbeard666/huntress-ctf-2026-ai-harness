"""Independent oracle for ovspec_* fixtures: a HAND-WRITTEN decoder per fixture (pycryptodome ARC4, stdlib zlib/lzma/
hashlib), no lib.binary. Prints the decoded HCFG JSON (or 'none') and exits 1 if it disagrees with the fixture json.
usage (repo root): python3 tests/data/binary_fixtures/ovspec_oracle.py ovspec_<name>"""
import hashlib, json, lzma, pathlib, struct, sys, zlib
from Crypto.Cipher import ARC4

HERE = pathlib.Path(__file__).parent
ror = lambda b, r: ((b >> r) | (b << (8 - r))) & 255
sw = lambda x: ((x << 4) | (x >> 4)) & 255


def rec(u):
    if u[:4] != b"HCFG":
        return None
    k, n, crc = u[5], *struct.unpack_from("<HI", u, 6)
    p = bytes(b ^ k for b in u[12:12 + n])
    return json.loads(p) if zlib.crc32(p) == crc else None


def d19(d):
    o = d.rfind(b"PK19"); k1, k2 = d[o + 5], d[o + 6]; n, = struct.unpack_from("<I", d, o + 8)
    u = bytes(ror(b ^ k2, 3) ^ k1 for b in d[o + 44:o + 44 + n])
    return o, u if hashlib.sha256(u).digest() == d[o + 12:o + 44] else None


def rs(d):
    return d.rfind(b"RS20")


def idx_sub_crc(d):
    o = rs(d); seed, key = d[o + 4], d[o + 5:o + 9]; n, = struct.unpack_from(">I", d, o + 9)
    u = bytes(((b - key[i % 4]) & 255) ^ seed ^ (i % 251) for i, b in enumerate(d[o + 17:o + 17 + n]))
    return o, u if zlib.crc32(u) == struct.unpack_from("<I", d, o + 13)[0] else None


def rot_not_swap(d):
    o = rs(d); k = d[o + 5]; n, = struct.unpack_from("<I", d, o + 8)
    u = bytes(sw(~ror(b, 3) & 255) ^ k for b in d[o + 44:o + 44 + n])
    return o, u if hashlib.sha256(u).digest() == d[o + 12:o + 44] else None


def prev_cipher_md5(d):
    o = rs(d); prev, k1 = d[o + 4], d[o + 5]; n, = struct.unpack_from("<I", d, o + 8); u = bytearray()
    for b in d[o + 28:o + 28 + n]:
        u.append(b ^ prev ^ k1); prev = b
    return o, bytes(u) if hashlib.md5(u).digest() == d[o + 12:o + 28] else None


def prev_plain(d):
    o = rs(d); k1 = d[o + 5]; n, = struct.unpack_from("<I", d, o + 8); u, prev = bytearray(), 0
    for b in d[o + 44:o + 44 + n]:
        prev = ((b + prev) & 255) ^ k1; u.append(prev)
    return o, bytes(u) if hashlib.sha256(u).digest() == d[o + 12:o + 44] else None


def reversed_(d):
    o = rs(d); k1 = d[o + 5]; n, = struct.unpack_from("<I", d, o + 8)
    u = bytes(b ^ k1 for b in d[o + 44:o + 44 + n][::-1])
    return o, u if hashlib.sha256(u).digest() == d[o + 12:o + 44] else None


def rc4_zlib(d):
    o = rs(d); key = d[o + 6:o + 14]; n, = struct.unpack_from("<I", d, o + 14)
    u = zlib.decompress(ARC4.new(key).decrypt(d[o + 50:o + 50 + n]))
    return o, u if hashlib.sha256(u).digest() == d[o + 18:o + 50] else None


def lcg_lzma(d):
    o = rs(d); st, = struct.unpack_from("<I", d, o + 4); n, = struct.unpack_from("<I", d, o + 8); z = bytearray()
    for b in d[o + 32:o + 32 + n]:
        st = (1103515245 * st + 12345) % 2 ** 32; z.append(b ^ ((st >> 16) & 255))
    u = lzma.decompress(bytes(z))
    return o, u if hashlib.sha1(u).digest() == d[o + 12:o + 32] else None


def steps_rle(d):
    o = rs(d); k1 = d[o + 5]; n, = struct.unpack_from("<I", d, o + 8)
    r = bytes(ror(b ^ k1, 2) for b in d[o + 44:o + 44 + n])
    u = b"".join(bytes([r[i + 1]]) * r[i] for i in range(0, len(r), 2))
    return o, u if hashlib.sha256(u).digest() == d[o + 12:o + 44] else None


def decoy(d):
    o = rs(d)
    if o < 0:
        return None, None
    k1, k2 = d[o + 5], d[o + 6]; n, = struct.unpack_from("<I", d, o + 8)
    u = bytes(ror(b ^ k2, 3) ^ k1 for b in d[o + 44:o + 44 + n])
    return o, u if len(u) == n and hashlib.sha256(u).digest() == d[o + 12:o + 44] else None


DEC = {"d19_single": d19, "d19_mastery_set2": d19, "idx_sub_crc": idx_sub_crc, "rot_not_swap": rot_not_swap,
       "prev_cipher_md5": prev_cipher_md5, "prev_plain": prev_plain, "reversed": reversed_, "rc4_zlib": rc4_zlib,
       "lcg_lzma": lcg_lzma, "steps_rle": steps_rle, "decoy_badhash": decoy, "decoy_wrongmagic": decoy}
bad = 0
for stem in sys.argv[1:] or sorted(p.stem for p in HERE.glob("ovspec_*.json")):
    f = json.loads((HERE / f"{stem}.json").read_text()); d = (HERE / f"{stem}.bin").read_bytes()
    o, u = DEC[stem[len("ovspec_"):]](d)
    got = rec(u) if u else None
    exp = f["expected_config"]
    ok = (got is None and exp == "none" or isinstance(got, dict) and isinstance(exp, dict) and
          all(got.get(k) == v for k, v in exp.items())) and (got is None or o == f["expected_offset"])
    bad += not ok
    print(("ok  " if ok else "BAD ") + stem, o, json.dumps(got) if got else "none")
sys.exit(1 if bad else 0)
