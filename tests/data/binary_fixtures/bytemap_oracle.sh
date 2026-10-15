#!/bin/sh
# usage: sh bytemap_oracle.sh <file.bin> [<map> <form>]  (python3 -I stdlib script below; never imports lib.binary)
exec python3 -I - "$@" <<'PYEOF'
# Independent oracle for the bytemap_* fixtures (stdlib only; does NOT import lib.binary). Usage:
#   python3 -I bytemap_oracle.sh <file.bin> [<map> <form>]   map: nib | rolN | not | addK (K decimal); form: raw|after|before
# Without map/form: try every map x form (decoy check). Prints JSON {offset, config} for each crc-valid HCFG, or "none".
# Search is exhaustive: every file offset (raw/after) / every base64 char position (before), not anchor-driven.
import base64, binascii, json, re, struct, sys, zlib

def table(m):
    if m == "nib": f = lambda b: ((b << 4) | (b >> 4)) & 255
    elif m == "not": f = lambda b: b ^ 255
    elif m.startswith("rol"): r = int(m[3:]); f = lambda b: ((b << r) | (b >> (8 - r))) & 255
    else: k = int(m[3:]); f = lambda b: (b + k) % 256
    fwd = bytes(f(b) for b in range(256))
    return bytes(fwd.index(b) for b in range(256))   # inverse: stored -> plain

def blob_ok(b):
    if b[:4] != b"HCFG" or len(b) < 12: return None
    v, k, n, crc = struct.unpack_from("<BBHI", b, 4)
    p = bytes(c ^ k for c in b[12:12 + n])
    if n and len(p) == n and zlib.crc32(p) == crc:
        return json.loads(p)

def b64(text):
    text = re.sub(rb"\s", b"", text)
    return binascii.a2b_base64(text[:len(text) // 4 * 4])

def scan(data, m, form):
    inv, out = table(m), []
    if form in ("raw", "after"):
        plain = data.translate(inv)
        for s in range(len(plain)):
            if form == "raw":
                c = blob_ok(plain[s:s + 70000])
            else:
                mm = re.match(rb"[A-Za-z0-9+/\n]+=*", plain[s:s + 90000])
                c = blob_ok(b64(mm.group(0))) if mm and plain[s:s + 4] == b"SENG" else None
            if c: out.append({"offset": s, "config": c})
    else:
        for mm in re.finditer(rb"[A-Za-z0-9+/\n]{16,}=*", data):
            run = mm.group(0)
            for s in range(len(run) - 15):
                try:
                    c = blob_ok(b64(run[s:]).translate(inv))
                except binascii.Error:
                    c = None
                if c: out.append({"offset": mm.start() + s, "config": c})
    return out

data = open(sys.argv[1], "rb").read()
combos = [(sys.argv[2], sys.argv[3])] if len(sys.argv) > 3 else \
    [(m, f) for m in ["nib", "not"] + [f"rol{r}" for r in (1, 2, 3, 5, 6, 7)] + [f"add{k}" for k in range(1, 256)]
     for f in ("raw", "after", "before")]
hits = [h for m, f in combos for h in scan(data, m, f)]
print(json.dumps(hits[0] if len(hits) == 1 else hits) if hits else "none")
PYEOF
