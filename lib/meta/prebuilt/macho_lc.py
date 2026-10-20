"""Mach-O load-command depth + code signature (prebuilt, SPECULATIVE -- never GM-asked yet). Header/UUID/minos live in
macho.py; this module adds what the load commands and the LC_CODE_SIGNATURE SuperBlob say.

Dylibs (<mach-o/loader.h> dylib_command {cmd, cmdsize, name.offset u32, timestamp, current_version,
compatibility_version}): load_dylib_names = every LC_LOAD_DYLIB (0xc) / LC_LOAD_WEAK_DYLIB (0x80000018) /
LC_REEXPORT_DYLIB (0x8000001f) / LC_LAZY_LOAD_DYLIB (0x20) / LC_LOAD_UPWARD_DYLIB (0x80000023) path in LOAD-COMMAND
order (otool -L order minus the LC_ID_DYLIB line), JSON list. weak_/reexport_dylib_names = that kind only.
id_dylib = LC_ID_DYLIB (0xd) install name. rpaths = LC_RPATH (0x8000001c) paths, command order.
main_entryoff_u64_hex = LC_MAIN (0x80000028) entryoff u64 (file offset of main in the slice; otool prints decimal).
segment_names = LC_SEGMENT(_64) segname in command order (incl. __PAGEZERO/__LINKEDIT); section_names =
"segname,sectname" (`__TEXT,__text`, the otool -s / ld spelling) in command order.
source_version = LC_SOURCE_VERSION (0x2a) u64 A24.B10.C10.D10.E10, rendered like otool -l (A.B always, then .C.D.E
only as far as the last non-zero part: 0 -> "0.0").
Code signature (ALL big-endian, <Kernel/kern/cs_blobs.h>): LC_CODE_SIGNATURE (0x1d) dataoff (slice-relative) ->
SuperBlob 0xfade0cc0 {length, count, [type, offset]...} -> CodeDirectory 0xfade0c02 (slot 0; alternates 0x1000+)
{version, flags, hashOffset, identOffset, nSpecial, nCode, codeLimit, hashSize u8, hashType u8, platform, pageSize,
spare2, scatterOffset (>=0x20100), teamOffset (>=0x20200)}. identifier = C string at identOffset; team_id at
teamOffset (absent / ad-hoc -> "none"). hash_type = the CD hashType name (sha1/sha256/sha256_truncated/sha384, as
codesign -dv prints "Hash type=sha256"). cdhash = hashType-digest of the WHOLE CD blob truncated to 20 bytes, lowercase
hex (codesign "CDHash="); with several CDs the strongest hash type wins (kernel rank sha384 > sha256 >
sha256_truncated > sha1). cdhash_full = the untruncated digest. entitlements = keys of the 0xfade7171 XML plist (slot
5) in stored order, JSON list. is_adhoc_signed = CD flags & CS_ADHOC (0x2); an unsigned Mach-O -> false.
Fat files: the slice named in the question text (arm64 / arm64e / x86_64 / i386 / armv7 / "slice N", the member name
masked out), else the first slice (otool / `file` order) -- except signature fields fall back to the first SIGNED
slice when the first one carries no LC_CODE_SIGNATURE (zig/ld sign arm64 only). Not Mach-O -> "none"."""
import hashlib
import plistlib
import re
import struct

from ..spell import Hex

FIELDS = {
    ("macho", "load_dylib_names"): "macho_lc_value",
    ("macho", "load_dylib_paths"): "macho_lc_value",
    ("macho", "load_dylibs"): "macho_lc_value",
    ("macho", "dylib_names"): "macho_lc_value",
    ("macho", "dylib_paths"): "macho_lc_value",
    ("macho", "linked_dylibs"): "macho_lc_value",
    ("macho", "linked_libraries"): "macho_lc_value",
    ("macho", "imported_dylibs"): "macho_lc_value",
    ("macho", "dependent_libraries"): "macho_lc_value",
    ("macho", "lc_load_dylib_names"): "macho_lc_value",
    ("macho", "load_dylib_count"): "macho_lc_value",
    ("macho", "dylib_count"): "macho_lc_value",
    ("macho", "weak_dylib_names"): "macho_lc_value",
    ("macho", "load_weak_dylib_names"): "macho_lc_value",
    ("macho", "reexport_dylib_names"): "macho_lc_value",
    ("macho", "id_dylib"): "macho_lc_value",
    ("macho", "id_dylib_name"): "macho_lc_value",
    ("macho", "lc_id_dylib"): "macho_lc_value",
    ("macho", "lc_id_dylib_name"): "macho_lc_value",
    ("macho", "install_name"): "macho_lc_value",
    ("macho", "dylib_install_name"): "macho_lc_value",
    ("macho", "id_dylib_current_version"): "macho_lc_value",
    ("macho", "id_dylib_compatibility_version"): "macho_lc_value",
    ("macho", "rpaths"): "macho_lc_value",
    ("macho", "rpath_list"): "macho_lc_value",
    ("macho", "rpath_paths"): "macho_lc_value",
    ("macho", "lc_rpaths"): "macho_lc_value",
    ("macho", "lc_rpath_paths"): "macho_lc_value",
    ("macho", "rpath_count"): "macho_lc_value",
    ("macho", "main_entryoff_u64_hex"): "macho_lc_value",
    ("macho", "lc_main_entryoff_u64_hex"): "macho_lc_value",
    ("macho", "entryoff_u64_hex"): "macho_lc_value",
    ("macho", "entry_point_offset_u64_hex"): "macho_lc_value",
    ("macho", "main_entryoff"): "macho_lc_value",
    ("macho", "lc_main_entryoff"): "macho_lc_value",
    ("macho", "entryoff"): "macho_lc_value",
    ("macho", "entry_point_offset"): "macho_lc_value",
    ("macho", "main_stacksize"): "macho_lc_value",
    ("macho", "segment_names"): "macho_lc_value",
    ("macho", "segments"): "macho_lc_value",
    ("macho", "segment_count"): "macho_lc_value",
    ("macho", "section_names"): "macho_lc_value",
    ("macho", "sections"): "macho_lc_value",
    ("macho", "section_count"): "macho_lc_value",
    ("macho", "source_version"): "macho_lc_value",
    ("macho", "lc_source_version"): "macho_lc_value",
    ("macho", "code_signature_present"): "macho_lc_value",
    ("macho", "has_code_signature"): "macho_lc_value",
    ("macho", "is_signed"): "macho_lc_value",
    ("macho", "is_code_signed"): "macho_lc_value",
    ("macho", "code_signature_dataoff"): "macho_lc_value",
    ("macho", "code_signature_dataoff_u32_hex"): "macho_lc_value",
    ("macho", "code_signature_datasize"): "macho_lc_value",
    ("macho", "code_signature_offset"): "macho_lc_value",
    ("macho", "code_signature_size"): "macho_lc_value",
    ("macho", "identifier"): "macho_lc_value",
    ("macho", "cs_identifier"): "macho_lc_value",
    ("macho", "code_directory_identifier"): "macho_lc_value",
    ("macho", "codesign_identifier"): "macho_lc_value",
    ("macho", "code_signing_identifier"): "macho_lc_value",
    ("macho", "signing_identifier"): "macho_lc_value",
    ("macho", "signature_identifier"): "macho_lc_value",
    ("macho", "team_id"): "macho_lc_value",
    ("macho", "team_identifier"): "macho_lc_value",
    ("macho", "cs_team_id"): "macho_lc_value",
    ("macho", "code_directory_team_id"): "macho_lc_value",
    ("macho", "codesign_team_id"): "macho_lc_value",
    ("macho", "hash_type"): "macho_lc_value",
    ("macho", "cd_hash_type"): "macho_lc_value",
    ("macho", "code_directory_hash_type"): "macho_lc_value",
    ("macho", "cdhash"): "macho_lc_value",
    ("macho", "cd_hash"): "macho_lc_value",
    ("macho", "code_directory_hash"): "macho_lc_value",
    ("macho", "cdhash_hex"): "macho_lc_value",
    ("macho", "cdhash_full"): "macho_lc_value",
    ("macho", "cs_flags_u32_hex"): "macho_lc_value",
    ("macho", "code_directory_flags_u32_hex"): "macho_lc_value",
    ("macho", "cd_flags_u32_hex"): "macho_lc_value",
    ("macho", "code_directory_version_u32_hex"): "macho_lc_value",
    ("macho", "cd_version_u32_hex"): "macho_lc_value",
    ("macho", "entitlements"): "macho_lc_value",
    ("macho", "entitlement_keys"): "macho_lc_value",
    ("macho", "entitlements_keys"): "macho_lc_value",
    ("macho", "entitlements_key_names"): "macho_lc_value",
    ("macho", "has_entitlements"): "macho_lc_value",
    ("macho", "entitlements_present"): "macho_lc_value",
    ("macho", "is_adhoc_signed"): "macho_lc_value",
    ("macho", "is_ad_hoc_signed"): "macho_lc_value",
    ("macho", "adhoc_signed"): "macho_lc_value",
    ("macho", "ad_hoc_signed"): "macho_lc_value",
    ("macho", "is_adhoc"): "macho_lc_value",
}

_THIN = {0xfeedface: ("<", False), 0xfeedfacf: ("<", True), 0xcefaedfe: (">", False), 0xcffaedfe: (">", True)}
_DYLIB_KINDS = {0xc: "load", 0x80000018: "weak", 0x8000001f: "reexport", 0x20: "lazy", 0x80000023: "upward"}
_ARCH = {"x86_64": (0x01000007, None), "x86-64": (0x01000007, None), "amd64": (0x01000007, None),
         "i386": (7, None), "x86": (7, None), "arm64e": (0x0100000c, 2), "arm64": (0x0100000c, None),
         "aarch64": (0x0100000c, None), "arm64_32": (0x0200000c, None), "armv7": (12, None), "ppc": (18, None)}
_HASH = {1: ("sha1", 1), 2: ("sha256", 3), 3: ("sha256_truncated", 2), 4: ("sha384", 4)}


def _cstr(b, off):
    if not 0 <= off < len(b):
        return None
    end = b.find(b"\0", off)
    return b[off:end if end >= 0 else len(b)].decode("utf-8", "replace")


def _thin(b, base, limit):
    """{"e", "cpu", "sub", "cmds": [(cmd, body)], "base", "end"} of the thin image at `base`, or None."""
    if base + 28 > len(b):
        return None
    magic, = struct.unpack_from("<I", b, base)
    if magic not in _THIN:
        return None
    e, is64 = _THIN[magic]
    cpu, sub, _ft, ncmds = struct.unpack_from(e + "4I", b, base + 4)
    off, cmds = base + (32 if is64 else 28), []
    for _ in range(min(ncmds, 4096)):
        if off + 8 > len(b):
            break
        cmd, csz = struct.unpack_from(e + "II", b, off)
        cmds.append((cmd, bytes(b[off:off + max(csz, 8)])))
        if csz < 8:
            break
        off += csz
    return {"e": e, "cpu": cpu, "sub": sub & 0xffffff, "cmds": cmds, "base": base, "end": min(limit, len(b))}


def _slices(b):
    """[thin header dict] -- one for a thin file, one per Mach-O slice of a fat file; [] when not Mach-O."""
    if len(b) >= 8:
        magic, n = struct.unpack_from(">II", b, 0)
        if magic in (0xcafebabe, 0xcafebabf) and 0 < n < 20:
            w, out = (20 if magic == 0xcafebabe else 32), []
            for i in range(n):
                o = 8 + i * w
                if o + w > len(b):
                    break
                if magic == 0xcafebabe:
                    _c, _s, off, size = struct.unpack_from(">4I", b, o)
                else:
                    _c, _s, off, size = struct.unpack_from(">IIQQ", b, o)
                h = _thin(b, off, off + size)
                if h:
                    out.append(h)
            return out
    h = _thin(b, 0, len(b))
    return [h] if h else []


def _selector(ctx):
    """(cputype, cpusubtype|None) or ("index", n) named in the question text (member name masked), else None."""
    q = (ctx or {}).get("question") or {}
    text = " ".join(str(q.get(k) or "") for k in ("question", "prompt", "text"))
    member = str((ctx or {}).get("member") or "")
    if member:
        text = text.replace(member, " ")
    text = text.lower()
    m = re.search(r"\b(?:slice|arch(?:itecture)?)\s*(?:index\s*)?#?(\d+)\b", text)
    if m:
        return ("index", int(m.group(1)))
    for name in sorted(_ARCH, key=len, reverse=True):
        if re.search(r"(?<![a-z0-9_])" + re.escape(name) + r"(?![a-z0-9_])", text):
            return _ARCH[name]
    return None


def _pick(slices, ctx, want_sig):
    sel = _selector(ctx)
    if sel and sel[0] == "index":
        return slices[sel[1]] if sel[1] < len(slices) else None
    if sel:
        hit = [h for h in slices if h["cpu"] == sel[0] and (sel[1] is None or h["sub"] == sel[1])]
        if sel[1] is None and sel[0] == 0x0100000c:
            hit.sort(key=lambda h: h["sub"] == 2)   # plain "arm64" prefers the non-arm64e slice
        if hit:
            return hit[0]
    if want_sig:
        for h in slices:
            if any(c == 0x1d for c, _ in h["cmds"]):
                return h
    return slices[0]


def _ver3(v):
    return "%d.%d.%d" % (v >> 16, (v >> 8) & 0xff, v & 0xff)


def _source_version(v):
    a, parts = v >> 40, [(v >> s) & 0x3ff for s in (30, 20, 10, 0)]
    out = [str(a), str(parts[0])]
    last = max([i for i in (1, 2, 3) if parts[i]], default=0)
    out += [str(parts[i]) for i in range(1, last + 1)]
    return ".".join(out)


def _signature(b, h):
    """{"dataoff", "datasize", "cds": [cd blob], "ent": xml bytes|None} or None (no LC_CODE_SIGNATURE)."""
    body = next((bd for c, bd in h["cmds"] if c == 0x1d and len(bd) >= 16), None)
    if body is None:
        return None
    dataoff, datasize = struct.unpack_from(h["e"] + "II", body, 8)
    start = h["base"] + dataoff
    sb = b[start:start + datasize]
    out = {"dataoff": dataoff, "datasize": datasize, "cds": [], "ent": None}
    if len(sb) < 12 or struct.unpack_from(">I", sb, 0)[0] != 0xfade0cc0:
        return out
    length, count = struct.unpack_from(">II", sb, 4)
    sb = sb[:length] if 12 <= length <= len(sb) else sb
    for i in range(min(count, 64)):
        if 12 + i * 8 + 8 > len(sb):
            break
        typ, off = struct.unpack_from(">II", sb, 12 + i * 8)
        if off + 8 > len(sb):
            continue
        magic, blen = struct.unpack_from(">II", sb, off)
        blob = sb[off:off + blen]
        if magic == 0xfade0c02 and len(blob) >= 44 and (typ == 0 or 0x1000 <= typ < 0x1010):
            out["cds"].append(blob)
        elif magic == 0xfade7171 and out["ent"] is None:
            out["ent"] = blob[8:]
    return out


def _cd(sig):
    """The primary CodeDirectory: the strongest hash type (kernel rank), first on ties."""
    best = None
    for cd in sig["cds"]:
        rank = _HASH.get(cd[37], ("", 0))[1]
        if best is None or rank > best[0]:
            best = (rank, cd)
    return best[1] if best else None


def macho_lc_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), ctx)
    except Exception:
        return None


def _value(b, ctx):
    f = (ctx or {}).get("field") or ""
    slices = _slices(b)
    if not slices:
        return "none"
    sigf = any(k in f for k in ("sign", "identifier", "team", "hash", "cd_", "code_directory", "entitle", "adhoc",
                                "ad_hoc", "cs_"))
    h = _pick(slices, ctx, sigf)
    if h is None:
        return "none"
    e, cmds = h["e"], h["cmds"]

    if ("dylib" in f or "librar" in f) and "id_dylib" not in f and f != "dylib_install_name":
        kinds = {"weak": ("weak",), "reexport": ("reexport",)}.get(f.split("_")[0], tuple(_DYLIB_KINDS.values()))
        if f.startswith("load_weak"):
            kinds = ("weak",)
        names = [_cstr(bd, struct.unpack_from(e + "I", bd, 8)[0]) for c, bd in cmds
                 if _DYLIB_KINDS.get(c) in kinds and len(bd) >= 24]
        return len(names) if f.endswith("_count") else names
    if "id_dylib" in f or "install_name" in f:
        bd = next((x for c, x in cmds if c == 0xd and len(x) >= 24), None)
        if bd is None:
            return "none"
        off, _ts, cur, compat = struct.unpack_from(e + "4I", bd, 8)
        if f.endswith("current_version"):
            return _ver3(cur)
        if f.endswith("compatibility_version"):
            return _ver3(compat)
        return _cstr(bd, off)
    if "rpath" in f:
        paths = [_cstr(bd, struct.unpack_from(e + "I", bd, 8)[0]) for c, bd in cmds if c == 0x8000001c and len(bd) >= 12]
        return len(paths) if f.endswith("_count") else paths
    if "entryoff" in f or "entry_point_offset" in f or f == "main_stacksize":
        bd = next((x for c, x in cmds if c == 0x80000028 and len(x) >= 24), None)
        if bd is None:
            return "none"
        entryoff, stack = struct.unpack_from(e + "QQ", bd, 8)
        if f == "main_stacksize":
            return stack
        return Hex(entryoff, 16) if f.endswith("_hex") else entryoff
    if f.startswith("segment") or f.startswith("section"):
        segs, sects = [], []
        for c, bd in cmds:
            if c not in (0x1, 0x19):
                continue
            is64 = c == 0x19
            hdr, ssz = (72, 80) if is64 else (56, 68)
            if len(bd) < hdr:
                continue
            segs.append(bd[8:24].split(b"\0")[0].decode("latin-1"))
            nsects, = struct.unpack_from(e + "I", bd, hdr - 8)
            for i in range(min(nsects, 1024)):
                o = hdr + i * ssz
                if o + 32 > len(bd):
                    break
                sects.append("%s,%s" % (bd[o + 16:o + 32].split(b"\0")[0].decode("latin-1"),
                                        bd[o:o + 16].split(b"\0")[0].decode("latin-1")))
        lst = segs if f.startswith("segment") else sects
        return len(lst) if f.endswith("_count") else lst
    if "source_version" in f:
        bd = next((x for c, x in cmds if c == 0x2a and len(x) >= 16), None)
        return _source_version(struct.unpack_from(e + "Q", bd, 8)[0]) if bd else "none"

    sig = _signature(b, h)
    if f in ("code_signature_present", "has_code_signature", "is_signed", "is_code_signed"):
        return bool(sig and sig["cds"])
    if f.startswith("code_signature_"):
        if sig is None:
            return "none"
        if "dataoff" in f or f.endswith("_offset"):
            return Hex(sig["dataoff"], 8) if f.endswith("_hex") else sig["dataoff"]
        return sig["datasize"]
    cd = _cd(sig) if sig else None
    if "adhoc" in f or "ad_hoc" in f:
        return bool(cd is not None and struct.unpack_from(">I", cd, 12)[0] & 0x2)
    if "entitle" in f:
        if f in ("has_entitlements", "entitlements_present"):
            return bool(sig and sig["ent"])
        if not sig or not sig["ent"]:
            return "none"
        pl = plistlib.loads(sig["ent"])
        return list(pl.keys()) if isinstance(pl, dict) else "none"
    if cd is None:
        return "none"
    version, flags, _hoff, ident_off = struct.unpack_from(">4I", cd, 8)
    if f.endswith("flags_u32_hex"):
        return Hex(flags, 8)
    if f.endswith("version_u32_hex"):
        return Hex(version, 8)
    if "identifier" in f and "team" not in f:
        return _cstr(cd, ident_off) or "none"
    if "team" in f:
        if version < 0x20200 or len(cd) < 52:
            return "none"
        toff, = struct.unpack_from(">I", cd, 48)
        return (_cstr(cd, toff) or "none") if toff else "none"
    name = _HASH.get(cd[37], (None, 0))[0]
    if "hash_type" in f:
        return name or str(cd[37])
    if "hash" in f:
        if name is None:
            return None
        dg = hashlib.new(name.replace("_truncated", ""), cd).hexdigest()
        return dg if f.endswith("_full") else dg[:40]
    return None
