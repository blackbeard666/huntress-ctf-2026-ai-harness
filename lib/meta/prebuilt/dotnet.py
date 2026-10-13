""".NET (CLI) metadata: Assembly / Module / TypeDef rows + the BSJB root version (prebuilt, SPECULATIVE).

Reuses lib/meta/dotnet.py's PE -> CLI header -> BSJB stream parser (D12 mvid). Here: the #~ (or #-) table stream is
walked with full ECMA-335 II.22 row sizes (heap-size flags + simple/coded index widths) up to Assembly (0x20).
  metadata_version     BSJB root Version string (NUL-padded), e.g. "v4.0.30319"
  module_name          Module row 1 Name (#Strings), e.g. "Foo.dll"
  type_count           TypeDef row count (includes the <Module> pseudo-type, like MetadataReader.TypeDefinitions.Count)
  assembly_name        Assembly row Name
  assembly_version     Assembly row Major.Minor.Build.Revision
  assembly_culture     Assembly row Culture; an empty culture is spelled "neutral" (AssemblyName.FullName style)
  public_key_token_hex Assembly PublicKey blob -> last 8 bytes of SHA-1, reversed (lowercase hex, no 0x); an
                       unsigned assembly (empty blob) -> "none"
Not a .NET PE (decoy / native PE / renamed) or no Assembly row (a .netmodule) -> "none"."""
import hashlib
import struct

from ..dotnet import cli_metadata

FIELDS = {
    ("dotnet", "assembly_name"): "assembly_name",
    ("dotnet", "assembly_def_name"): "assembly_name",
    ("dotnet", "assembly_version"): "assembly_version",
    ("dotnet", "assembly_def_version"): "assembly_version",
    ("dotnet", "assembly_culture"): "assembly_culture",
    ("dotnet", "culture"): "assembly_culture",
    ("dotnet", "public_key_token_hex"): "public_key_token",
    ("dotnet", "assembly_public_key_token_hex"): "public_key_token",
    ("dotnet", "public_key_token"): "public_key_token",
    ("dotnet", "metadata_version"): "metadata_version",
    ("dotnet", "metadata_root_version"): "metadata_version",
    ("dotnet", "metadata_version_string"): "metadata_version",
    ("dotnet", "runtime_version"): "metadata_version",
    ("dotnet", "module_name"): "module_name",
    ("dotnet", "module_def_name"): "module_name",
    ("dotnet", "type_count"): "type_count",
    ("dotnet", "typedef_count"): "type_count",
    ("dotnet", "type_def_count"): "type_count",
    ("dotnet", "typedef_row_count"): "type_count",
    ("dotnet", "type_def_row_count"): "type_count",
}

# coded index: (tag bits, tables)
_TDOR = (2, (0x02, 0x01, 0x1B))
_HASCONST = (2, (0x04, 0x08, 0x17))
_HASCA = (5, (0x06, 0x04, 0x01, 0x02, 0x08, 0x09, 0x0A, 0x00, 0x0E, 0x17, 0x14, 0x11, 0x1A, 0x1B, 0x20, 0x23,
              0x26, 0x27, 0x28, 0x2A, 0x2C, 0x2B))
_HASFM = (1, (0x04, 0x08))
_HASDS = (2, (0x02, 0x06, 0x20))
_MRP = (3, (0x02, 0x01, 0x1A, 0x06, 0x1B))
_HASSEM = (1, (0x14, 0x17))
_MDOR = (1, (0x06, 0x0A))
_MFWD = (1, (0x04, 0x06))
_CAT = (3, (0x06, 0x0A))
_RSCOPE = (2, (0x00, 0x1A, 0x23, 0x01))

# column kinds: int = fixed bytes, "s"/"g"/"b" = heap index, ("t", n) = table index, tuple = coded index
_COLS = {
    0x00: (2, "s", "g", "g", "g"),
    0x01: (_RSCOPE, "s", "s"),
    0x02: (4, "s", "s", _TDOR, ("t", 0x04), ("t", 0x06)),
    0x03: (("t", 0x04),),
    0x04: (2, "s", "b"),
    0x05: (("t", 0x06),),
    0x06: (4, 2, 2, "s", "b", ("t", 0x08)),
    0x07: (("t", 0x08),),
    0x08: (2, 2, "s"),
    0x09: (("t", 0x02), _TDOR),
    0x0A: (_MRP, "s", "b"),
    0x0B: (2, _HASCONST, "b"),
    0x0C: (_HASCA, _CAT, "b"),
    0x0D: (_HASFM, "b"),
    0x0E: (2, _HASDS, "b"),
    0x0F: (2, 4, ("t", 0x02)),
    0x10: (4, ("t", 0x04)),
    0x11: ("b",),
    0x12: (("t", 0x02), ("t", 0x14)),
    0x13: (("t", 0x14),),
    0x14: (2, "s", _TDOR),
    0x15: (("t", 0x02), ("t", 0x17)),
    0x16: (("t", 0x17),),
    0x17: (2, "s", "b"),
    0x18: (2, ("t", 0x06), _HASSEM),
    0x19: (("t", 0x02), _MDOR, _MDOR),
    0x1A: ("s",),
    0x1B: ("b",),
    0x1C: (2, _MFWD, "s", ("t", 0x1A)),
    0x1D: (4, ("t", 0x04)),
    0x1E: (4, 4),
    0x1F: (4,),
    0x20: (4, 2, 2, 2, 2, 4, "b", "s", "s"),
}


def _parse(data):
    """{"m": root offset, "st": streams, "rows": {table: count}, "tbl": {table: (row offset, [col widths])},
    "hs": heap-size flags} of a .NET PE, or None."""
    md = cli_metadata(data)
    if not md:
        return None
    m, st = md
    ts = st.get("#~") or st.get("#-")
    if not ts:
        return None
    t = ts[0]
    hs = data[t + 6]
    valid, = struct.unpack_from("<Q", data, t + 8)
    p = t + 24
    rows = {}
    for i in range(64):
        if valid >> i & 1:
            rows[i], = struct.unpack_from("<I", data, p)
            p += 4
    if hs & 0x20:
        p += 4
    heap = {"s": 4 if hs & 1 else 2, "g": 4 if hs & 2 else 2, "b": 4 if hs & 4 else 2}

    def width(c):
        if isinstance(c, int):
            return c
        if isinstance(c, str):
            return heap[c]
        if c[0] == "t":
            return 2 if rows.get(c[1], 0) < 0x10000 else 4
        bits, tabs = c
        return 2 if max(rows.get(x, 0) for x in tabs) < (1 << (16 - bits)) else 4

    tbl = {}
    for i in range(64):
        if not valid >> i & 1:
            continue
        cols = _COLS.get(i)
        if cols is None:          # a table past Assembly we cannot size: everything we need is already placed
            break
        ws = [width(c) for c in cols]
        tbl[i] = (p, ws)
        p += sum(ws) * rows[i]
    return {"m": m, "st": st, "rows": rows, "tbl": tbl}


def _row(data, P, table, idx=0):
    """List of column values (ints) of row idx of table, or None."""
    if table not in P["tbl"] or P["rows"].get(table, 0) <= idx:
        return None
    p, ws = P["tbl"][table]
    p += sum(ws) * idx
    out = []
    for w in ws:
        out.append(int.from_bytes(data[p:p + w], "little"))
        p += w
    if p > len(data):
        return None
    return out


def _string(data, P, i):
    s = P["st"].get("#Strings")
    if not s:
        return None
    o = s[0] + i
    e = data.find(b"\0", o)
    if e < 0:
        return None
    return data[o:e].decode("utf-8", "replace")


def _blob(data, P, i):
    b = P["st"].get("#Blob")
    if not b or not i:
        return b""
    o = b[0] + i
    x = data[o]
    if x & 0x80 == 0:
        n, o = x, o + 1
    elif x & 0xC0 == 0x80:
        n, o = ((x & 0x3F) << 8) | data[o + 1], o + 2
    else:
        n, o = ((x & 0x1F) << 24) | (data[o + 1] << 16) | (data[o + 2] << 8) | data[o + 3], o + 4
    return bytes(data[o:o + n])


def _safe(fn):
    def wrap(data, ctx):
        if data is None:
            return None
        try:
            P = _parse(data)
            if not P:
                return "none"
            v = fn(data, P)
        except (struct.error, IndexError, ValueError, KeyError, TypeError):
            return "none"
        return "none" if v is None else v
    wrap.__name__ = fn.__name__
    wrap.__doc__ = fn.__doc__
    return wrap


@_safe
def assembly_name(data, P):
    r = _row(data, P, 0x20)
    return _string(data, P, r[7]) if r else None


@_safe
def assembly_version(data, P):
    r = _row(data, P, 0x20)
    return "%d.%d.%d.%d" % tuple(r[1:5]) if r else None


@_safe
def assembly_culture(data, P):
    r = _row(data, P, 0x20)
    if not r:
        return None
    return _string(data, P, r[8]) or "neutral"


@_safe
def public_key_token(data, P):
    r = _row(data, P, 0x20)
    if not r:
        return None
    key = _blob(data, P, r[6])
    if not key:
        return None
    if len(key) == 8 and not r[5] & 1:     # flags without afPublicKey: the blob already is the token
        return key
    return hashlib.sha1(key).digest()[-8:][::-1]


@_safe
def metadata_version(data, P):
    m = P["m"]
    vlen, = struct.unpack_from("<I", data, m + 12)
    v = data[m + 16:m + 16 + vlen].split(b"\0", 1)[0].decode("utf-8", "replace").strip()
    return v or None


@_safe
def module_name(data, P):
    r = _row(data, P, 0x00)
    return _string(data, P, r[1]) if r else None


@_safe
def type_count(data, P):
    return P["rows"].get(0x02, 0)
