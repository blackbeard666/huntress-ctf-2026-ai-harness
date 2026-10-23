"""Independent oracle for crypt_*.bin: constants DERIVED from their definitions (not copied from lib.binary's table),
located with bytes.find (LE / BE / byte string / UTF-16LE); an algorithm counts when >= 2 of its derived words (or
its table / single defining constant) are present.  usage: python3 -I crypt_oracle.py <file>  -> JSON
{"algorithms": [...], "first_offset": {alg: first offset of any derived constant}}"""
import base64, json, math, sys
from decimal import Decimal, getcontext
getcontext().prec = 80
M32, M64 = (1 << 32) - 1, (1 << 64) - 1
primes = [p for p in range(2, 400) if all(p % q for q in range(2, int(p ** .5) + 1))]


def iroot(n, k):   # floor(n ** (1/k)) for big ints
    x = int(Decimal(n) ** (Decimal(1) / k))
    while (x + 1) ** k <= n:
        x += 1
    while x ** k > n:
        x -= 1
    return x


def gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = ((a << 1) ^ 0x11b) if a & 0x80 else a << 1
        b >>= 1
    return r


inv = [0] + [next(y for y in range(1, 256) if gf_mul(x, y) == 1) for x in range(1, 256)]
sbox = bytes(b ^ ((b << 1 | b >> 7) & 255) ^ ((b << 2 | b >> 6) & 255) ^ ((b << 3 | b >> 5) & 255) ^ ((b << 4 | b >> 4) & 255) ^ 0x63
             for b in inv)
crc = []
for i in range(256):
    c = i
    for _ in range(8):
        c = (c >> 1) ^ (int("{:032b}".format(0x04C11DB7)[::-1], 2) if c & 1 else 0)
    crc.append(c)
fnv0 = 0
for ch in b"chongo <Landon Curt Noll> /\\../\\":
    fnv0 = ((fnv0 * 0x01000193) & M32) ^ ch
phi = (1 + Decimal(5).sqrt()) / 2
words = {   # alg -> (size, [derived words])
    "md5": (4, [int(abs(math.sin(i + 1)) * 2 ** 32) for i in range(64)]),
    "sha1": (4, [iroot(n << 60, 2) for n in (2, 3, 5, 10)]),
    "sha256": (4, [iroot(p << 96, 3) & M32 for p in primes[:64]] + [iroot(p << 64, 2) & M32 for p in primes[:8]]),
    "sha512": (8, [iroot(p << 192, 3) & M64 for p in primes[:80]] + [iroot(p << 128, 2) & M64 for p in primes[:8]]),
    "tea": (4, [int(Decimal(2 ** 32) / phi), -int(Decimal(2 ** 32) / phi) & M32, 32 * int(Decimal(2 ** 32) / phi) & M32]),
    "crc32": (4, [crc[128]] + crc[1:8]),
    "fnv": (4, [fnv0]),
}
tables = {"aes": [sbox[:16]], "chacha": [b"expand 32-byte k", b"expand 16-byte k"],
          "base64": [base64.b64encode(bytes.fromhex("00108310518720928b30d38f41149351559761969b71d79f8218a39259a7a29aabb2dbafc31cb3d35db7e39ebbf3dfbf"))]}
data = open(sys.argv[1], "rb").read()
found, first = [], {}
for alg, (n, ws) in words.items():
    offs, hit = [], 0
    for w in ws:
        o = [data.find(w.to_bytes(n, e)) for e in ("little", "big")]
        o = [x for x in o if x >= 0]
        hit += bool(o)
        offs += o
    if hit >= (1 if alg in ("crc32", "tea", "fnv") else 2):
        found.append(alg)
        first[alg] = min(offs)
for alg, pats in tables.items():
    o = [x for p in pats for x in (data.find(p), data.find(p.decode("latin-1").encode("utf-16-le"))) if x >= 0]
    if alg == "chacha":   # the sigma as 4 LE immediates (compiled "expand 32-byte k" initialiser)
        sw = [data.find(pats[0][i:i + 4]) for i in range(0, 16, 4)]
        o += [x for x in sw if x >= 0] if min(sw) >= 0 else []
    if o:
        found.append(alg)
        first[alg] = min(o)
print(json.dumps({"algorithms": sorted(found), "first_offset": dict(sorted(first.items()))}))
