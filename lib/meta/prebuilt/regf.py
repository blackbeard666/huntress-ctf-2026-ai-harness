"""Windows Registry hive (regf) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Base block (libregf spec, little-endian, 4096 bytes): "regf" signature, primary sequence number u32 @4, secondary
sequence number u32 @8 (they differ in a dirty hive), last written time FILETIME u64 @12, major version u32 @20 (1),
minor version u32 @24 (3 NT4..XP, 5 Vista+), file type u32 @28, file format u32 @32, root cell offset u32 @36
(relative to the first hbin at 0x1000), hive bins data size u32 @40, clustering factor u32 @44, file name 64 bytes
UTF-16LE @48 (the last 31 chars of the hive's path, NUL-padded), XOR-32 checksum of bytes 0..507 @508.
Root key = the nk cell at 0x1000 + root cell offset (cell-relative): i32 size, "nk" @4, flags u16 @6 (0x20 COMP_NAME = name
is ASCII/latin-1, else UTF-16LE), FILETIME @8, subkeys u32 @0x18, values u32 @0x28, name len u16 @0x4C, name @0x50.
Times: FILETIME (100 ns since 1601-01-01 UTC) -> ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ' (same spelling as lnk.*_time);
zero FILETIME -> "none". Versions: the u32 as int (major_version "1", minor_version "5"); `version`/`format_version`
-> "major.minor". Values are as stored (no checksum gate: a dirty/edited hive is still answered).
Not "regf" (e.g. a Win9x "CREG" hive renamed .dat) -> "none"; regf with an unreadable root cell -> None.

Key/value lookups (target regf-values; pure struct walk of nk -> lf/lh/li/ri -> nk, nk -> value list -> vk):
  subkey_count / value_count / last_written_utc: of the key named in the question (a backslash path, root-relative,
  case-insensitive; a leading root/HKCU/HKLM\\SOFTWARE prefix is dropped), else of the ROOT key. last_written_utc
  is the key node's FILETIME (the target spec says "root key last-written"; the base-block time stays
  regf.last_written_time) -> 'YYYY-MM-DDTHH:MM:SSZ'.
  run_key_values: {value name: data} of ...\\Microsoft\\Windows\\CurrentVersion\\Run (NTUSER: under Software\\,
  SOFTWARE hive: at the root), stored value-list order; REG_SZ/EXPAND_SZ = UTF-16LE up to the first NUL,
  DWORD/QWORD = int, other types = hex. run_key_value_names / run_key_value_data: the two halves as lists.
  userassist_entries: the ROT13-decoded value names of every UserAssist\\{GUID}\\Count key, stored order, minus the
  UEME_CTLSESSION bookkeeping value. Key/values absent -> "none"."""
import codecs
import datetime
import re
import struct

FIELDS = {
    ("regf", "primary_sequence_number"): "base_value",
    ("regf", "base_block_primary_sequence_number"): "base_value",
    ("regf", "sequence_number_1"): "base_value",
    ("regf", "primary_sequence"): "base_value",
    ("regf", "secondary_sequence_number"): "base_value",
    ("regf", "base_block_secondary_sequence_number"): "base_value",
    ("regf", "sequence_number_2"): "base_value",
    ("regf", "secondary_sequence"): "base_value",
    ("regf", "last_written_time"): "base_value",
    ("regf", "last_written_time_utc"): "base_value",
    ("regf", "last_written_timestamp"): "base_value",
    ("regf", "base_block_last_written_time"): "base_value",
    ("regf", "last_modification_time"): "base_value",
    ("regf", "hive_file_name"): "base_value",
    ("regf", "file_name"): "base_value",
    ("regf", "base_block_file_name"): "base_value",
    ("regf", "hive_name"): "base_value",
    ("regf", "major_version"): "base_value",
    ("regf", "base_block_major_version"): "base_value",
    ("regf", "format_major_version"): "base_value",
    ("regf", "minor_version"): "base_value",
    ("regf", "base_block_minor_version"): "base_value",
    ("regf", "format_minor_version"): "base_value",
    ("regf", "version"): "base_value",
    ("regf", "format_version"): "base_value",
    ("regf", "hive_version"): "base_value",
    ("regf", "root_key_name"): "root_value",
    ("regf", "root_nk_name"): "root_value",
    ("regf", "root_cell_key_name"): "root_value",
    ("regf", "root_key_last_written_time"): "root_value",
    ("regf", "root_key_subkey_count"): "root_value",
    ("regf", "root_key_number_of_subkeys"): "root_value",
    ("regf", "root_key_value_count"): "root_value",
    ("regf", "root_key_number_of_values"): "root_value",
    ("regf", "root_cell_offset_u32_hex"): "base_value",
    ("regf", "last_written_utc"): "key_value",
    ("regf", "last_written"): "key_value",
    ("regf", "key_last_written_utc"): "key_value",
    ("regf", "key_last_written_time"): "key_value",
    ("regf", "root_key_last_written_utc"): "key_value",
    ("regf", "subkey_count"): "key_value",
    ("regf", "number_of_subkeys"): "key_value",
    ("regf", "key_subkey_count"): "key_value",
    ("regf", "root_subkey_count"): "key_value",
    ("regf", "value_count"): "key_value",
    ("regf", "number_of_values"): "key_value",
    ("regf", "key_value_count"): "key_value",
    ("regf", "root_value_count"): "key_value",
    ("regf", "run_key_values"): "run_values",
    ("regf", "run_values"): "run_values",
    ("regf", "run_key_entries"): "run_values",
    ("regf", "run_key_value_names"): "run_values",
    ("regf", "run_key_value_data"): "run_values",
    ("regf", "run_key_commands"): "run_values",
    ("regf", "userassist_entries"): "userassist",
    ("regf", "userassist_names"): "userassist",
    ("regf", "userassist_entry_names"): "userassist",
    ("regf", "userassist_entry_count"): "userassist",
}


def _filetime(v):
    if not v:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=v // 10)
    except (OverflowError, ValueError):
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def base_block(b):
    """The regf base block as a dict, or None (not regf / truncated)."""
    if not b or len(b) < 512 or bytes(b[:4]) != b"regf":
        return None
    seq1, seq2, ts, major, minor, ftype, ffmt, root, size, clus = struct.unpack_from("<IIQIIIIIII", b, 4)
    name = bytes(b[48:112]).decode("utf-16-le", "replace").split("\x00", 1)[0].strip()
    return {"seq1": seq1, "seq2": seq2, "ts": ts, "major": major, "minor": minor, "root": root, "name": name}


def root_nk(b, h):
    """(name, last written FILETIME, subkey count, value count) of the root nk cell, or None."""
    off = 0x1000 + h["root"]
    if len(b) < off + 0x50 or bytes(b[off + 4:off + 6]) != b"nk":
        return None
    flags, ts = struct.unpack_from("<HQ", b, off + 6)
    nsub, = struct.unpack_from("<I", b, off + 0x18)
    nval, = struct.unpack_from("<I", b, off + 0x28)
    nlen, = struct.unpack_from("<H", b, off + 0x4C)
    raw = bytes(b[off + 0x50:off + 0x50 + nlen])
    if len(raw) < nlen:
        return None
    name = raw.decode("latin-1") if flags & 0x20 else raw.decode("utf-16-le", "replace")
    return name, ts, nsub, nval


def base_value(data, ctx):
    """regf.<base block field>."""
    if data is None:
        return None
    try:
        h = base_block(data)
        if h is None:
            return "none"
        f = ctx.get("field") or ""
        if "primary" in f or f.endswith("_1"):
            return h["seq1"]
        if "secondary" in f or f.endswith("_2"):
            return h["seq2"]
        if "time" in f:
            return _filetime(h["ts"])
        if "name" in f:
            return h["name"] or "none"
        if "major" in f:
            return h["major"]
        if "minor" in f:
            return h["minor"]
        if f.startswith("root_cell_offset"):
            return h["root"]
        if "version" in f:
            return "%d.%d" % (h["major"], h["minor"])
    except Exception:
        return None
    return None


def root_value(data, ctx):
    """regf.root_key_<field>: from the root nk cell."""
    if data is None:
        return None
    try:
        h = base_block(data)
        if h is None:
            return "none"
        r = root_nk(data, h)
        if r is None:
            return None
        f = ctx.get("field") or ""
        if "time" in f:
            return _filetime(r[1])
        if "subkey" in f:
            return r[2]
        if "value" in f:
            return r[3]
        return r[0]
    except Exception:
        return None


def _cell(b, off):
    """Payload offset of the cell at hbin-relative `off` (skips the i32 size), or None."""
    if off in (None, 0xFFFFFFFF):
        return None
    p = 0x1000 + off + 4
    return p if 0x1000 <= p - 4 and p + 2 <= len(b) else None


def _nk(b, off):
    p = _cell(b, off)
    if p is None or bytes(b[p:p + 2]) != b"nk" or p + 0x4C > len(b):
        return None
    flags, ts = struct.unpack_from("<HQ", b, p + 2)
    nsub, = struct.unpack_from("<I", b, p + 0x14)
    sub, = struct.unpack_from("<I", b, p + 0x1C)
    nval, vlist = struct.unpack_from("<II", b, p + 0x24)
    nlen, = struct.unpack_from("<H", b, p + 0x48)
    raw = bytes(b[p + 0x4C:p + 0x4C + nlen])
    name = raw.decode("latin-1") if flags & 0x20 else raw.decode("utf-16-le", "replace")
    return {"name": name, "ts": ts, "nsub": nsub, "sub": sub, "nval": nval, "vlist": vlist}


def _subkeys(b, nk, depth=0):
    """Child nk dicts of `nk` in stored index order (lf/lh/li, ri of those)."""
    out = []

    def walk(off, d):
        p = _cell(b, off)
        if p is None or d > 4 or p + 4 > len(b):
            return
        sig = bytes(b[p:p + 2])
        n, = struct.unpack_from("<H", b, p + 2)
        step = 8 if sig in (b"lf", b"lh") else 4 if sig in (b"li", b"ri") else 0
        if not step:
            return
        for i in range(min(n, (len(b) - p - 4) // step)):
            o, = struct.unpack_from("<I", b, p + 4 + i * step)
            if sig == b"ri":
                walk(o, d + 1)
            else:
                k = _nk(b, o)
                if k is not None:
                    out.append(k)

    if nk["nsub"]:
        walk(nk["sub"], 0)
    return out


def _values(b, nk):
    """[(name, type, data bytes)] of `nk`'s value list in stored order."""
    out = []
    p = _cell(b, nk["vlist"]) if nk["nval"] else None
    if p is None:
        return out
    for i in range(min(nk["nval"], (len(b) - p) // 4)):
        o, = struct.unpack_from("<I", b, p + i * 4)
        v = _cell(b, o)
        if v is None or bytes(b[v:v + 2]) != b"vk" or v + 0x14 > len(b):
            continue
        nlen, size, doff, typ, flags = struct.unpack_from("<HIIIH", b, v + 2)
        raw = bytes(b[v + 0x14:v + 0x14 + nlen])
        name = raw.decode("latin-1") if flags & 1 else raw.decode("utf-16-le", "replace")
        if size & 0x80000000:
            data = struct.pack("<I", doff)[:min(size & 0x7FFFFFFF, 4)]
        else:
            dp = _cell(b, doff)
            data = bytes(b[dp:dp + size]) if dp is not None else b""
            if data[:2] == b"db":   # big data: segment list of 16344-byte chunks
                n, seg = struct.unpack_from("<HI", data, 2) if len(data) >= 8 else (0, 0)
                sp, chunks = _cell(b, seg), []
                for j in range(n if sp is not None else 0):
                    co, = struct.unpack_from("<I", b, sp + j * 4)
                    cp = _cell(b, co)
                    if cp is not None:
                        chunks.append(bytes(b[cp:cp + 16344]))
                data = b"".join(chunks)[:size]
        out.append((name, typ, data))
    return out


def _data(typ, data):
    if typ in (1, 2, 6):
        s = data.decode("utf-16-le", "replace")
        return s.split("\x00", 1)[0]
    if typ in (4, 11) and len(data) >= (4 if typ == 4 else 8):
        return struct.unpack_from("<I" if typ == 4 else "<Q", data)[0]
    if typ == 7:
        return [x for x in data.decode("utf-16-le", "replace").split("\x00") if x]
    return data.hex()


def _find(b, root, path):
    """The nk at root-relative `path` (list of names, case-insensitive), or None."""
    k = root
    for part in path:
        k = next((c for c in _subkeys(b, k) if c["name"].lower() == part.lower()), None)
        if k is None:
            return None
    return k


_PREFIX = re.compile(r"^(?:HKEY_CURRENT_USER|HKCU|HKEY_LOCAL_MACHINE\\(?:SOFTWARE|SYSTEM)|HKLM\\(?:SOFTWARE|SYSTEM)|"
                     r"HKEY_LOCAL_MACHINE|HKLM|HKEY_USERS\\[^\\]+|HKU\\[^\\]+)(?:\\|$)", re.I)
_TAGRX = re.compile(r"\[assigned-artifact-sha256:[^\]]*\]")


def _asked_path(ctx):
    """Root-relative key path named in the question (list of names), [] = root key."""
    q = ctx.get("question")
    text = _TAGRX.sub("", str(q.get("question") if isinstance(q, dict) else q or ""))
    for m in (ctx.get("member") or "", (ctx.get("member") or "").replace("/", "\\")):
        text = text.replace(m, " ") if m else text   # a zip member path like Users\\ana\\NTUSER.DAT is not a key
    m = re.search(r"[`'\"]([^`'\"]*\\[^`'\"]*)[`'\"]", text) or re.search(r"(\S+\\\S+)", text)
    if not m:
        return []
    p = _PREFIX.sub("", m.group(1).strip().strip("\\").rstrip(".,;:"))
    return [x for x in p.split("\\") if x]


def _root(b):
    h = base_block(b)
    if h is None:
        return None, None
    return h, _nk(b, h["root"])


def key_value(data, ctx):
    """regf.{last_written_utc,subkey_count,value_count}: of the asked key, else the root key."""
    if data is None:
        return None
    try:
        h, root = _root(data)
        if h is None:
            return "none"
        if root is None:
            return None
        path = _asked_path(ctx)
        if path and path[0].lower() == root["name"].lower() and _find(data, root, path) is None:
            path = path[1:]
        k = _find(data, root, path) if path else root
        if k is None:
            return "none"
        f = ctx.get("field") or ""
        if "subkey" in f:
            return k["nsub"]
        if "value" in f:
            return k["nval"]
        return _filetime(k["ts"])
    except Exception:
        return None


_RUN = ("Microsoft", "Windows", "CurrentVersion", "Run")


def run_values(data, ctx):
    """regf.run_key_values: {name: data} of the CurrentVersion\\Run key."""
    if data is None:
        return None
    try:
        h, root = _root(data)
        if h is None:
            return "none"
        if root is None:
            return None
        k = _find(data, root, ("Software",) + _RUN) or _find(data, root, _RUN)
        if k is None:
            return "none"
        vals = [(n, _data(t, d)) for n, t, d in _values(data, k)]
        if not vals:
            return "none"
        f = ctx.get("field") or ""
        if f.endswith("_names"):
            return [n for n, _ in vals]
        if f.endswith(("_data", "_commands")):
            return [v for _, v in vals]
        return dict(vals)
    except Exception:
        return None


def userassist(data, ctx):
    """regf.userassist_entries: ROT13-decoded UserAssist\\{GUID}\\Count value names."""
    if data is None:
        return None
    try:
        h, root = _root(data)
        if h is None:
            return "none"
        if root is None:
            return None
        ua = _find(data, root, ("Software", "Microsoft", "Windows", "CurrentVersion", "Explorer", "UserAssist"))
        names = []
        for g in _subkeys(data, ua) if ua else []:
            cnt = next((c for c in _subkeys(data, g) if c["name"].lower() == "count"), None)
            for n, _, _ in _values(data, cnt) if cnt else []:
                d = codecs.decode(n, "rot13")
                if d != "UEME_CTLSESSION":
                    names.append(d)
        if not names:
            return "none"
        return len(names) if (ctx.get("field") or "").endswith("_count") else names
    except Exception:
        return None
