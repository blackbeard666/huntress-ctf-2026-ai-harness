"""Stdlib OLE / Compound File Binary reader. COPIED from the GM-verified D13 solver
(challenges/day13/metadata-product-placement/solver/solve.py). Used by msi.py; reusable for any OLE container
(.doc/.xls/.msg SummaryInformation, thumbs.db, ...)."""
import struct

MAGIC = bytes.fromhex("d0cf11e0a1b11ae1")


def msi_name(n):
    """De-mangle an MSI stream name (base-64-ish packing into U+3800..U+4840)."""
    m = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._"
    r = []
    for ch in n:
        c = ord(ch)
        if c == 0x4840:
            r.append("!")
        elif 0x4800 <= c < 0x4840:
            r.append(m[c - 0x4800])
        elif 0x3800 <= c < 0x4800:
            c -= 0x3800
            r.append(m[c & 0x3F] + m[(c >> 6) & 0x3F])
        else:
            r.append(ch)
    return "".join(r)


def cfb_streams(b, demangle=True):
    """{stream name: bytes} of a CFB file (MSI names de-mangled when `demangle`; tables keep the '!' prefix), or None."""
    if not b or b[:8] != MAGIC:
        return None
    ss = 1 << struct.unpack_from("<H", b, 0x1E)[0]
    mss = 1 << struct.unpack_from("<H", b, 0x20)[0]
    nfat, dir0 = struct.unpack_from("<II", b, 0x2C)
    cutoff, mf0, nmf, dif0, ndif = struct.unpack_from("<IIIII", b, 0x38)
    sec = lambda n: b[512 + n * ss: 512 + (n + 1) * ss]  # noqa: E731
    difat = list(struct.unpack_from("<109I", b, 0x4C))
    d = dif0
    while ndif and d < 0xFFFFFFFA:
        e = struct.unpack("<%dI" % (ss // 4), sec(d))
        difat += e[:-1]
        d = e[-1]
        ndif -= 1
    fat = []
    for f in difat[:nfat]:
        fat += struct.unpack("<%dI" % (ss // 4), sec(f))

    def chain(start, tbl, get):
        out, n, seen = [], start, set()
        while n < 0xFFFFFFFA and n < len(tbl) and n not in seen:
            seen.add(n)
            out.append(get(n))
            n = tbl[n]
        return b"".join(out)
    dirb = chain(dir0, fat, sec)
    x = chain(mf0, fat, sec)
    minifat = list(struct.unpack("<%dI" % (len(x) // 4), x[:len(x) // 4 * 4])) if x else []
    ents = []
    for i in range(0, len(dirb) - 127, 128):
        nl, typ = struct.unpack_from("<HB", dirb, i + 64)
        start, size = struct.unpack_from("<II", dirb, i + 116)
        ents.append((dirb[i:i + max(nl - 2, 0)].decode("utf-16le", "replace"), typ, start, size))
    mini = chain(ents[0][2], fat, sec) if ents and ents[0][1] == 5 else b""
    out = {}
    for name, typ, start, size in ents:
        if typ != 2:
            continue
        if size < cutoff:
            data = chain(start, minifat, lambda n: mini[n * mss:(n + 1) * mss])[:size]
        else:
            data = chain(start, fat, sec)[:size]
        out[msi_name(name) if demangle else name] = data
    return out
