#!/bin/sh
# usage: sh rollxor_oracle.sh <file.bin>  (python3 -I stdlib script below; never imports lib.binary)
exec python3 -I - "$@" <<'PYEOF'
# Independent oracle for the rollxor_* fixtures: at EVERY file offset, derive the key from stored[0..1] under each
# mode (add-step, xor-index, ciphertext feedback, plaintext feedback), decode byte-by-byte, keep crc-valid HCFG blobs.
# Prints JSON {offset, mode, config} (one hit) / a list / "none".
import json, struct, sys, zlib

def ok(b):
    if len(b) < 12 or b[:4] != b"HCFG": return None
    v, k, n, crc = struct.unpack_from("<BBHI", b, 4)
    p = bytes(c ^ k for c in b[12:12 + n])
    return json.loads(p) if n and len(p) == n and zlib.crc32(p) == crc else None

def dec(c, mode, k0, st=0):
    out, prev = bytearray(), k0
    for j, x in enumerate(c):
        if mode == "roll": out.append(x ^ ((k0 + st * j) % 256))
        elif mode == "idx": out.append(x ^ k0 ^ (j % 256))
        elif mode == "cbc": out.append(x ^ prev); prev = x
        else: prev = x ^ prev; out.append(prev)
    return bytes(out)

data, hits = open(sys.argv[1], "rb").read(), []
for s in range(len(data) - 12):
    c = data[s:s + 12]
    k0 = c[0] ^ 0x48
    for mode, st in [("roll", ((c[1] ^ 0x43) - k0) % 256), ("idx", 0), ("cbc", 0), ("chain", 0)]:
        if mode == "roll" and st == 0: continue
        h = dec(c, mode, k0, st)
        if h[:4] != b"HCFG": continue
        n = 12 + struct.unpack_from("<H", h, 6)[0]
        cfg = ok(dec(data[s:s + n], mode, k0, st))
        if cfg is not None: hits.append({"offset": s, "mode": mode, "config": cfg})
print(json.dumps(hits[0] if len(hits) == 1 else hits) if hits else "none")
PYEOF
