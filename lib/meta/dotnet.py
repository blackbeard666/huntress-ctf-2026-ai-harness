""".NET (CLI) metadata fields. COPIED from the GM-verified D12 solver
(challenges/day12/metadata-managed-expectations/solver/solve.py): own PE + CLI header + #~ table parser, no pefile.
dotnet.mvid_guid = Module row 1 Mvid -> #GUID heap entry rendered as .NET Guid.ToString() (bytes_le, lowercase)."""
import struct

from .spell import Guid


def pe_sections(data):
    """(e_lfanew, opt_off, sections[(va, vsize, raw, rawsize)], is_pe32plus) or None."""
    if not data or data[:2] != b"MZ" or len(data) < 0x40:
        return None
    lf = struct.unpack_from("<I", data, 0x3C)[0]
    if data[lf:lf + 4] != b"PE\0\0":
        return None
    nsec, = struct.unpack_from("<H", data, lf + 6)
    optsz, = struct.unpack_from("<H", data, lf + 20)
    opt = lf + 24
    plus = struct.unpack_from("<H", data, opt)[0] == 0x20B
    secs = []
    for i in range(nsec):
        o = opt + optsz + 40 * i
        vsize, va, rsize, raw = struct.unpack_from("<IIII", data, o + 8)
        secs.append((va, vsize, raw, rsize))
    return lf, opt, secs, plus


def rva2off(secs, rva):
    for va, vs, raw, rs in secs:
        if va <= rva < va + max(vs, rs):
            return rva - va + raw
    return rva


def cli_metadata(data):
    """(metadata_root_offset, {stream_name: (off, size)}) of a .NET PE, or None."""
    pe = pe_sections(data)
    if not pe:
        return None
    lf, opt, secs, plus = pe
    dd = opt + (112 if plus else 96)
    cli_rva, cli_sz = struct.unpack_from("<II", data, dd + 14 * 8)
    if not cli_rva:
        return None
    c = rva2off(secs, cli_rva)
    md_rva, md_sz = struct.unpack_from("<II", data, c + 8)
    m = rva2off(secs, md_rva)
    if data[m:m + 4] != b"BSJB":
        return None
    vlen, = struct.unpack_from("<I", data, m + 12)
    p = m + 16 + vlen
    nstreams, = struct.unpack_from("<H", data, p + 2)
    p += 4
    streams = {}
    for _ in range(nstreams):
        off, size = struct.unpack_from("<II", data, p)
        e = data.index(b"\0", p + 8)
        name = data[p + 8:e].decode("latin-1")
        p = (e + 4) & ~3
        streams[name] = (m + off, size)
    return m, streams


def mvid_bytes(data):
    md = cli_metadata(data)
    if not md:
        return None
    _, st = md
    tbl = st.get("#~") or st.get("#-")
    gh = st.get("#GUID")
    if not tbl or not gh:
        return None
    t = tbl[0]
    heap_sizes = data[t + 6]
    valid, = struct.unpack_from("<Q", data, t + 8)
    if not valid & 1:
        return None
    p = t + 24 + 4 * bin(valid).count("1")
    if heap_sizes & 0x20:  # extra data (#- uncompressed)
        p += 4
    sidx = 4 if heap_sizes & 1 else 2
    gidx = 4 if heap_sizes & 2 else 2
    p += 2 + sidx  # Generation, Name
    g, = struct.unpack_from("<I" if gidx == 4 else "<H", data, p)
    if not g:
        return None
    o = gh[0] + (g - 1) * 16
    return bytes(data[o:o + 16])


def mvid(data, ctx):
    if data is None:
        return None
    b = mvid_bytes(data)
    return Guid("bytes_le", b) if b and len(b) == 16 else None
