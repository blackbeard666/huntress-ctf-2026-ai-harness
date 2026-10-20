"""Unix `ar` archives: .a static libraries (GNU / BSD-darwin / thin), universal (fat) static libs, Windows .lib
(prebuilt, SPECULATIVE -- never GM-asked yet; D20 flavor "thin and universal binaries mixed with archives").

Layout: magic "!<arch>\\n" (thin archive: "!<thin>\\n") @0, then per member a 60-byte ASCII header -- name[16]
date[12] (decimal unix seconds) uid[6] gid[6] mode[8] (octal text) size[10] (decimal) fmag "`\\n" -- and the data
padded to an even offset. Thin archives store NO member data (except the symbol / long-name tables): the size is the
external file's.
Names: GNU "name/" (trailing '/' stripped), "/" = symbol table (u32 BE count, u32 BE member offsets, NUL strings;
"/SYM64/" = u64 variant), "//" = long-name table, "/<off>" = reference into it (entries end "/\\n").
BSD/darwin "#1/<len>": the real name is the first <len> bytes of the data (counted in size, NUL-padded);
"__.SYMDEF" / "__.SYMDEF SORTED" (/"_64") = ranlib table: u32 LE byte size of ranlib[] {u32 strx, u32 off}
(ranlib_64: u64, u64), u32 LE strtab size, strings. MS .lib: two "/" linker members (first = GNU layout) + "//".
Symbol / long-name tables are EXCLUDED from member_* lists; symbol_names come from the first table, stored order.

A universal static library is a FAT wrapper (0xcafebabe / 0xcafebabf, big-endian fat_arch table) whose slices are ar
archives: each slice is parsed and the member lists concatenated in fat_arch order (member_names / member_count over
all slices; *_set fields dedupe keeping the first occurrence).
Renderings: member_names = JSON list in archive order; member_mtimes_utc = ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' of the
decimal unix epoch (ar dates are unix seconds, UTC); member_modes = the stored octal text verbatim ("100644");
member_modes_octal = "%04o" of mode & 0o7777 (tar.py convention); member_sizes = data sizes in bytes (a BSD name
prefix is NOT counted). member_cpu_type_set = Mach-O members' cputype "0x%08x"; member_e_machine_set = ELF members'
e_machine "0x%04x"; member_coff_machine_set = COFF .obj (and short-import) Machine "0x%04x". No such member -> "none".
Not an ar archive (and not a fat wrapper of one) -> "none"."""
import datetime
import json
import struct

FIELDS = {
    ("ar", "member_names"): "ar_value",
    ("ar", "member_name_list"): "ar_value",
    ("ar", "names"): "ar_value",
    ("ar", "member_count"): "ar_value",
    ("ar", "number_of_members"): "ar_value",
    ("ar", "entry_count"): "ar_value",
    ("ar", "symbol_table_present"): "ar_value",
    ("ar", "has_symbol_table"): "ar_value",
    ("ar", "symbol_names"): "ar_value",
    ("ar", "symbol_count"): "ar_value",
    ("ar", "symbol_table_name"): "ar_value",
    ("ar", "member_mtimes_utc"): "ar_value",
    ("ar", "member_mtimes"): "ar_value",
    ("ar", "member_mtimes_unix"): "ar_value",
    ("ar", "member_sizes"): "ar_value",
    ("ar", "member_sizes_bytes"): "ar_value",
    ("ar", "member_modes"): "ar_value",
    ("ar", "member_modes_octal"): "ar_value",
    ("ar", "member_uids"): "ar_value",
    ("ar", "member_gids"): "ar_value",
    ("ar", "member_cpu_type_set"): "ar_value",
    ("ar", "member_cputype_set"): "ar_value",
    ("ar", "member_e_machine_set"): "ar_value",
    ("ar", "member_machine_set"): "ar_value",
    ("ar", "member_coff_machine_set"): "ar_value",
    ("ar", "archive_format"): "ar_value",
    ("ar", "variant"): "ar_value",
    ("ar", "is_thin"): "ar_value",
    ("ar", "is_universal"): "ar_value",
    ("ar", "slice_count"): "ar_value",
    ("static_lib", "member_names"): "ar_value",
    ("static_lib", "member_count"): "ar_value",
    ("static_lib", "symbol_table_present"): "ar_value",
    ("static_lib", "symbol_names"): "ar_value",
    ("static_lib", "member_mtimes_utc"): "ar_value",
    ("static_lib", "member_sizes"): "ar_value",
    ("static_lib", "member_modes"): "ar_value",
    ("static_lib", "member_cpu_type_set"): "ar_value",
    ("static_lib", "member_e_machine_set"): "ar_value",
    ("static_lib", "member_coff_machine_set"): "ar_value",
    ("static_lib", "archive_format"): "ar_value",
    ("a", "member_names"): "ar_value",
    ("a", "member_count"): "ar_value",
    ("a", "symbol_table_present"): "ar_value",
    ("a", "symbol_names"): "ar_value",
    ("a", "member_mtimes_utc"): "ar_value",
    ("a", "member_sizes"): "ar_value",
    ("a", "member_modes"): "ar_value",
    ("a", "member_cpu_type_set"): "ar_value",
    ("a", "member_e_machine_set"): "ar_value",
    ("a", "member_coff_machine_set"): "ar_value",
    ("lib", "member_names"): "ar_value",
    ("lib", "member_count"): "ar_value",
    ("lib", "symbol_table_present"): "ar_value",
    ("lib", "symbol_names"): "ar_value",
    ("lib", "member_mtimes_utc"): "ar_value",
    ("lib", "member_sizes"): "ar_value",
    ("lib", "member_modes"): "ar_value",
    ("lib", "member_coff_machine_set"): "ar_value",
    ("lib", "member_cpu_type_set"): "ar_value",
    ("lib", "member_e_machine_set"): "ar_value",
}

_MAGIC, _THIN = b"!<arch>\n", b"!<thin>\n"
_SYMTABS = ("/", "/SYM64/", "__.SYMDEF", "__.SYMDEF SORTED", "__.SYMDEF_64", "__.SYMDEF_64 SORTED")


def _int(b, base=10):
    s = (b if isinstance(b, str) else bytes(b).decode("ascii", "replace")).strip()
    return int(s, base) if s else 0


def _gnu_symbols(d, wide=False):
    w = 8 if wide else 4
    n = int.from_bytes(d[:w], "big")
    if n > len(d) // w:
        return []
    raw = d[w + n * w:]
    return [s.decode("latin-1") for s in raw.split(b"\0")[:n]]


def _bsd_symbols(d, wide=False):
    w = 8 if wide else 4
    fmt = "<Q" if wide else "<I"
    sz, = struct.unpack_from(fmt, d, 0)
    if sz > len(d):
        return []
    ents = [struct.unpack_from(fmt, d, w + i)[0] for i in range(0, sz, 2 * w)]
    so = w + sz
    strsz, = struct.unpack_from(fmt, d, so)
    strs = d[so + w:so + w + strsz]
    out = []
    for x in ents:
        if x < len(strs):
            e = strs.find(b"\0", x)
            out.append(strs[x:e if e >= 0 else len(strs)].decode("latin-1"))
    return out


def parse_ar(b):
    """{'thin', 'format', 'members': [...], 'symtab': name|None, 'symbols': [...]} of one ar archive, or None."""
    b = bytes(b)
    if not (b.startswith(_MAGIC) or b.startswith(_THIN)):
        return None
    thin = b.startswith(_THIN)
    off, longnames, members, symtab, symbols, fmt = 8, b"", [], None, [], "gnu"
    while off + 60 <= len(b):
        h = b[off:off + 60]
        if h[58:60] != b"`\n":
            break
        raw = h[:16].decode("latin-1").rstrip(" ")
        size = _int(h[48:58])
        doff = off + 60
        name, data_skip = raw, 0
        if raw.startswith("#1/"):
            fmt = "bsd"
            ln = _int(raw[3:])
            name = b[doff:doff + ln].rstrip(b"\0").decode("latin-1")
            data_skip = ln
        elif raw == "//":
            longnames = b[doff:doff + size]
        elif raw.startswith("/") and raw[1:].isdigit():
            o = int(raw[1:])
            e = longnames.find(b"\n", o)
            name = longnames[o:e if e >= 0 else len(longnames)].decode("latin-1").rstrip("/")
        elif raw not in ("/", "/SYM64/") and raw.endswith("/"):
            name = raw[:-1]
        special = raw in ("/", "//", "/SYM64/") or name in _SYMTABS
        if special:
            payload = b[doff + data_skip:doff + size]
            if symtab is None and (raw in ("/", "/SYM64/") or name.startswith("__.SYMDEF")):
                symtab = name
                try:
                    if name.startswith("__.SYMDEF"):
                        symbols = _bsd_symbols(payload, "_64" in name)
                    else:
                        symbols = _gnu_symbols(payload, raw == "/SYM64/")
                except (struct.error, ValueError):
                    symbols = []
        else:
            stored = thin and not raw.startswith("#1/")
            data = b"" if stored else b[doff + data_skip:doff + size]
            members.append({"name": name, "mtime": _int(h[16:28]), "uid": _int(h[28:34]), "gid": _int(h[34:40]),
                            "mode": h[40:48].decode("latin-1").strip(), "size": size - data_skip, "data": data})
        if thin and not special:
            off = doff + data_skip
        else:
            off = doff + size
        off += off & 1
    return {"thin": thin, "format": "thin" if thin else fmt, "members": members, "symtab": symtab,
            "symbols": symbols}


def _fat_slices(b):
    """[bytes] of the slices of a Mach-O fat wrapper, or None."""
    if len(b) < 8 or b[:4] not in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
        return None
    wide = b[3] == 0xbf
    n, = struct.unpack_from(">I", b, 4)
    if not 0 < n < 45:      # 0xcafebabe is also the Java class magic (major >= 45)
        return None
    out = []
    for i in range(n):
        if wide:
            _c, _s, o, sz, _a, _r = struct.unpack_from(">iiQQII", b, 8 + 32 * i)
        else:
            _c, _s, o, sz, _a = struct.unpack_from(">iiIII", b, 8 + 20 * i)
        out.append(b[o:o + sz])
    return out


def archives(b):
    """[(parsed ar)] for a plain ar archive or each ar slice of a universal static lib, else None."""
    b = bytes(b)
    a = parse_ar(b)
    if a is not None:
        return [a]
    sl = _fat_slices(b)
    if not sl:
        return None
    parsed = [parse_ar(s) for s in sl]
    parsed = [p for p in parsed if p is not None]
    return parsed or None


def _macho_cpu(d):
    if len(d) < 8:
        return None
    m = d[:4]
    if m in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe"):
        return struct.unpack_from("<I", d, 4)[0]
    if m in (b"\xfe\xed\xfa\xcf", b"\xfe\xed\xfa\xce"):
        return struct.unpack_from(">I", d, 4)[0]
    return None


def _elf_machine(d):
    if len(d) < 20 or d[:4] != b"\x7fELF":
        return None
    return struct.unpack_from("<H" if d[5] != 2 else ">H", d, 18)[0]


_COFF_MACHINES = {0x014c, 0x8664, 0x01c0, 0x01c2, 0x01c4, 0xaa64, 0xa641, 0xa64e, 0x0200, 0x5032, 0x5064, 0x0166,
                  0x0168, 0x01a2, 0x01a6, 0x01f0, 0x01f1, 0x0ebc, 0x9041, 0x6232, 0x0184}


def _coff_machine(d):
    if len(d) < 20 or d[:4] == b"\x7fELF" or _macho_cpu(d) is not None:
        return None
    s1, s2 = struct.unpack_from("<HH", d, 0)
    if s1 == 0 and s2 == 0xFFFF:    # short import object / anon (bigobj) object: Machine @6
        m, = struct.unpack_from("<H", d, 6)
        return m if m in _COFF_MACHINES or m == 0 else None
    return s1 if s1 in _COFF_MACHINES else None


def _iso(t):
    return datetime.datetime.fromtimestamp(int(t), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dedupe(xs):
    return list(dict.fromkeys(xs))


def ar_value(data, ctx):
    try:
        if data is None:
            return None
        f = (ctx or {}).get("field") or ""
        arcs = archives(data)
        if not arcs:
            return "none"
        ms = [m for a in arcs for m in a["members"]]
        if f in ("member_names", "member_name_list", "names"):
            return [m["name"] for m in ms]
        if f in ("member_count", "number_of_members", "entry_count"):
            return len(ms)
        if f in ("symbol_table_present", "has_symbol_table"):
            return any(a["symtab"] is not None for a in arcs)
        if f == "symbol_table_name":
            return next((a["symtab"] for a in arcs if a["symtab"]), "none")
        if f in ("symbol_names", "symbol_count"):
            if not any(a["symtab"] is not None for a in arcs):
                return "none"
            syms = [s for a in arcs for s in a["symbols"]]
            return syms if f == "symbol_names" else len(syms)
        if "mtime" in f:
            return [m["mtime"] for m in ms] if f.endswith("_unix") else [_iso(m["mtime"]) for m in ms]
        if f in ("member_sizes", "member_sizes_bytes"):
            return [m["size"] for m in ms]
        if f == "member_modes":
            return [m["mode"] for m in ms]
        if f == "member_modes_octal":
            return ["%04o" % (int(m["mode"] or "0", 8) & 0o7777) for m in ms]
        if f == "member_uids":
            return [m["uid"] for m in ms]
        if f == "member_gids":
            return [m["gid"] for m in ms]
        if f in ("member_cpu_type_set", "member_cputype_set"):
            v = _dedupe("0x%08x" % c for c in (_macho_cpu(m["data"]) for m in ms) if c is not None)
            return v or "none"
        if f in ("member_e_machine_set", "member_machine_set"):
            v = _dedupe("0x%04x" % c for c in (_elf_machine(m["data"]) for m in ms) if c is not None)
            return v or "none"
        if f == "member_coff_machine_set":
            v = _dedupe("0x%04x" % c for c in (_coff_machine(m["data"]) for m in ms) if c is not None)
            return v or "none"
        if f in ("archive_format", "variant"):
            return arcs[0]["format"]
        if f == "is_thin":
            return any(a["thin"] for a in arcs)
        if f == "is_universal":
            return parse_ar(data) is None
        if f == "slice_count":
            return len(arcs)
        return "none"
    except Exception:  # noqa: BLE001 -- defensive: a hostile member never raises past the extractor
        return None
