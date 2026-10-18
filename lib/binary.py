"""Advanced binary-RE helpers — the hardening layer on top of lib/elf.py's header/symbol reads.

Covers what the audit flagged as missing: packer detection + UPX unpacking, stripped-Go function-name
recovery from .gopclntab (names survive stripping there), Mach-O facts (lief), robust constant recovery via
capstone disassembly (replacing the fragile `b8..c3` byte regex), and a Ghidra headless decompile helper
(now that JDK 21 is wired). Everything is static. Pure-stdlib + capstone/lief/pyelftools from the venv.

hcfg_scan() (Day 14 prep) finds the lane's HCFG config blob in ANY of the storage encodings below and crc-gates it;
it is pure stdlib (no subprocess) so in-window solvers can call it on the Homebase VM.
"""
import array
import base64
import binascii
import bisect
import io
import json
import math
import os
import re
import shutil
import struct
import subprocess
import tempfile
import time
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path

GHIDRA_SCRIPT = Path(__file__).resolve().parent / "ghidra_scripts" / "DecompileDump.java"


# --- JVM jars ------------------------------------------------------------------------------------
# Bundled runtime/library packages in a fat jar. Kotlin builds ship the whole kotlin stdlib (~18k classes on Day 7):
# a solver that scans every class constant spent 5.9 s per run there (blind D7 replay: Time Trial "too slow").
JVM_LIBRARY = re.compile(r"(^|/)(kotlinx?|java|javax|androidx?|scala|org/jetbrains|org/intellij|com/google|okhttp3|okio)/")


def jar_app_classes(jar, include_nested=True):
    """[(entry name, class bytes)] for the APPLICATION classes of a jar (bytes or path): bundled library packages
    (JVM_LIBRARY: kotlin, java, androidx, ...) and META-INF are skipped; nested jars are searched too."""
    import zipfile
    data = jar if isinstance(jar, (bytes, bytearray)) else Path(jar).read_bytes()
    out = []
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return out
    for n in z.namelist():
        if n.endswith(".class") and not n.startswith("META-INF/") and not JVM_LIBRARY.search(n):
            out.append((n, z.read(n)))
        elif include_nested and n.endswith(".jar") and not JVM_LIBRARY.search(n):
            out += [(f"{n}!{m}", b) for m, b in jar_app_classes(z.read(n), include_nested=False)]
    return out


def class_utf8(cls):
    """Every CONSTANT_Utf8 string of a .class file (names, descriptors, string literals) in constant-pool order --
    a direct parse, ~50x faster than javap. [] if it isn't a class file."""
    b = bytes(cls)
    if b[:4] != b"\xca\xfe\xba\xbe" or len(b) < 10:
        return []
    count, i, k, out = int.from_bytes(b[8:10], "big"), 10, 1, []
    sizes = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
    while k < count and i < len(b):
        tag = b[i]
        if tag == 1:
            ln = int.from_bytes(b[i + 1:i + 3], "big")
            out.append(b[i + 3:i + 3 + ln].decode("utf-8", "replace"))
            i += 3 + ln
        elif tag in sizes:
            i += 1 + sizes[tag]
            k += 1 if tag in (5, 6) else 0   # long/double take two pool slots
        else:
            break   # unknown tag: stop rather than misparse
        k += 1
    return out


# JVMS 4: full ClassFile facts (D17 re-asked D6/D7 jars: Main-Class methods in table order incl <init>, access_flags
# decimal 49, method_count incl <init>/<clinit>). Values are answer strings: decimal ints, compact JSON lists in
# table order, internal (slash) class names as javap -v prints them; "none" when the field is absent.
_CP_SIZES = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
_CLASS_ACC = ((0x0001, "ACC_PUBLIC"), (0x0010, "ACC_FINAL"), (0x0020, "ACC_SUPER"), (0x0200, "ACC_INTERFACE"),
              (0x0400, "ACC_ABSTRACT"), (0x1000, "ACC_SYNTHETIC"), (0x2000, "ACC_ANNOTATION"), (0x4000, "ACC_ENUM"),
              (0x8000, "ACC_MODULE"))


def _jv(v):
    return json.dumps(v, separators=(",", ":"), ensure_ascii=False)


def _mutf8(raw):
    """JVMS 4.4.7 modified UTF-8: NUL is C0 80, supplementary chars are CESU-8 surrogate pairs (Kotlin d1 strings
    are protobuf bytes stored as chars, full of both)."""
    try:
        s = raw.replace(b"\xc0\x80", b"\0").decode("utf-8", "surrogatepass")
        return s.encode("utf-16-le", "surrogatepass").decode("utf-16-le")
    except UnicodeError:
        return raw.decode("utf-8", "replace")


def classfile_parse(cls):
    """Parse a .class (JVMS 4.1) -> dict of raw structures, or None if it is not a well-formed class file (a Mach-O
    fat header shares 0xcafebabe: its 'major' is a small arch count, rejected by major < 45)."""
    import struct
    b = bytes(cls)
    try:
        if b[:4] != b"\xca\xfe\xba\xbe":
            return None
        minor, major, cpn = struct.unpack_from(">HHH", b, 4)
        if not 45 <= major <= 80:
            return None
        cp, o, k = [None] * cpn, 10, 1
        while k < cpn:
            t = b[o]
            if t == 1:
                ln = struct.unpack_from(">H", b, o + 1)[0]
                if o + 3 + ln > len(b):
                    return None
                cp[k] = (1, _mutf8(b[o + 3:o + 3 + ln]))
                o += 3 + ln
            elif t in _CP_SIZES:
                raw = b[o + 1:o + 1 + _CP_SIZES[t]]
                if len(raw) < _CP_SIZES[t]:
                    return None
                if t == 3:
                    v = struct.unpack(">i", raw)[0]
                elif t == 4:
                    v = struct.unpack(">f", raw)[0]
                elif t == 5:
                    v = struct.unpack(">q", raw)[0]
                elif t == 6:
                    v = struct.unpack(">d", raw)[0]
                elif t == 15:
                    v = (raw[0], struct.unpack(">H", raw[1:])[0])
                elif len(raw) == 2:
                    v = struct.unpack(">H", raw)[0]
                else:
                    v = struct.unpack(">HH", raw)
                cp[k] = (t, v)
                o += 1 + _CP_SIZES[t]
                k += 1 if t in (5, 6) else 0   # long/double take two pool slots
            else:
                return None
            k += 1

        def u(i):
            e = cp[i] if 0 < i < cpn else None
            return e[1] if e and e[0] == 1 else None

        def cname(i):
            e = cp[i] if 0 < i < cpn else None
            return u(e[1]) if e and e[0] == 7 else None

        def attrs(o):
            n = struct.unpack_from(">H", b, o)[0]
            o += 2
            out = []
            for _ in range(n):
                ni, ln = struct.unpack_from(">HI", b, o)
                if o + 6 + ln > len(b):
                    raise ValueError("attr overrun")
                out.append((u(ni), b[o + 6:o + 6 + ln]))
                o += 6 + ln
            return out, o

        acc, this, sup, ni = struct.unpack_from(">HHHH", b, o)
        o += 8
        ifaces = [cname(struct.unpack_from(">H", b, o + 2 * j)[0]) for j in range(ni)]
        o += 2 * ni
        members = []
        for _ in range(2):
            n = struct.unpack_from(">H", b, o)[0]
            o += 2
            ms = []
            for _ in range(n):
                fa, nm, ds = struct.unpack_from(">HHH", b, o)
                at, o = attrs(o + 6)
                ms.append({"access": fa, "name": u(nm), "descriptor": u(ds), "attributes": at})
            members.append(ms)
        cattrs, o = attrs(o)
    except (struct.error, IndexError, ValueError):
        return None
    return {"minor": minor, "major": major, "cp_count": cpn, "cp": cp, "access": acc, "this": cname(this),
            "super": cname(sup) if sup else None, "interfaces": ifaces, "fields": members[0],
            "methods": members[1], "attributes": cattrs, "_u": u, "_cname": cname, "trailing": len(b) - o}


def _annotations(raw, u):
    """RuntimeVisible/InvisibleAnnotations attribute -> [(type descriptor, {element name: value})] (JVMS 4.7.16)."""
    import struct
    pos = [0]

    def u2():
        v = struct.unpack_from(">H", raw, pos[0])[0]
        pos[0] += 2
        return v

    def value(cp):
        tag = chr(raw[pos[0]])
        pos[0] += 1
        if tag in "BCIJSZDF":
            e = cp[u2()]
            return e[1] if e else None
        if tag == "s":
            return u(u2())
        if tag == "e":
            return [u(u2()), u(u2())]
        if tag == "c":
            return u(u2())
        if tag == "@":
            return ann(cp)
        if tag == "[":
            return [value(cp) for _ in range(u2())]
        raise ValueError(tag)

    def ann(cp):
        t = u(u2())
        return t, {u(u2()): value(cp) for _ in range(u2())}
    return ann, u2


def classfile_facts(cls):
    """{field: answer string} for one .class -- javap -v -p parity: minor/major_version, constant_pool_count (header
    value = entries + 1), access_flags (decimal) / _hex / access_flag_names, this_class, super_class, interfaces,
    fields (+descriptors/count), methods (+descriptors/count, table order incl <init>/<clinit>), attributes,
    source_file, signature, string_constants, kotlin metadata (kotlin_k/mv/d1/d2/xi/xs/pn). None if not a class."""
    p = classfile_parse(cls)
    if not p:
        return None
    u = p["_u"]
    acc = p["access"]
    f = {"magic": "0xcafebabe", "minor_version": str(p["minor"]), "major_version": str(p["major"]),
         "class_version": f"{p['major']}.{p['minor']}",
         "java_version": str(p["major"] - 44) if p["major"] >= 49 else "1." + str(p["major"] - 44),
         "constant_pool_count": str(p["cp_count"]),
         "constant_pool_entries": str(sum(1 for e in p["cp"] if e)),
         "access_flags": str(acc), "access_flags_hex": f"0x{acc:04x}",
         "access_flag_names": _jv([n for m, n in _CLASS_ACC if acc & m]),
         "this_class": p["this"] or "none", "this_class_dotted": (p["this"] or "none").replace("/", "."),
         "super_class": p["super"] or "none", "super_class_dotted": (p["super"] or "none").replace("/", "."),
         "interfaces": _jv(p["interfaces"]), "interface_count": str(len(p["interfaces"])),
         "fields": _jv([m["name"] for m in p["fields"]]), "field_count": str(len(p["fields"])),
         "field_descriptors": _jv([m["descriptor"] for m in p["fields"]]),
         "methods": _jv([m["name"] for m in p["methods"]]), "method_count": str(len(p["methods"])),
         "method_descriptors": _jv([m["descriptor"] for m in p["methods"]]),
         "method_signatures": _jv([f"{m['name']}{m['descriptor']}" for m in p["methods"]]),
         "method_access_flags": _jv([m["access"] for m in p["methods"]]),
         "attributes": _jv([a for a, _ in p["attributes"]]), "attribute_count": str(len(p["attributes"])),
         "string_constants": _jv([u(e[1]) for e in p["cp"] if e and e[0] == 8]),
         "has_clinit": _jv(any(m["name"] == "<clinit>" for m in p["methods"])),
         "has_main": _jv(any(m["name"] == "main" and m["descriptor"] == "([Ljava/lang/String;)V"
                             for m in p["methods"]))}
    ca = dict(p["attributes"])
    sf = ca.get("SourceFile")
    f["source_file"] = (u(int.from_bytes(sf[:2], "big")) or "none") if sf and len(sf) >= 2 else "none"
    sg = ca.get("Signature")
    f["signature"] = (u(int.from_bytes(sg[:2], "big")) or "none") if sg and len(sg) >= 2 else "none"
    f["has_kotlin_metadata"] = "false"
    for key in ("kotlin_k", "kotlin_mv", "kotlin_bv", "kotlin_d1", "kotlin_d2", "kotlin_xi", "kotlin_xs", "kotlin_pn"):
        f[key] = "none"
    for an in ("RuntimeVisibleAnnotations", "RuntimeInvisibleAnnotations"):
        raw = ca.get(an)
        if not raw:
            continue
        try:
            ann, u2 = _annotations(raw, u)
            anns = [ann(p["cp"]) for _ in range(u2())]
        except (ValueError, IndexError, TypeError):
            continue
        for t, ev in anns:
            if t == "Lkotlin/Metadata;":
                f["has_kotlin_metadata"] = "true"
                for k, v in ev.items():
                    f[f"kotlin_{k}"] = _jv(v) if isinstance(v, list) else str(v)
    f["is_suspend_lambda"] = _jv(any(m["name"] == "invokeSuspend" for m in p["methods"]))
    return f


def jar_jvm_facts(data, member=None):
    """{field: answer string} for a jar (or a bare .class): jar-level main_class (Manifest Main-Class, dotted as
    written), created_by, class_count (.class entries), entry_count (all zip entries incl directories), plus
    classfile_facts of `member` (entry name or dotted class name) or else of the Main-Class. None if neither."""
    import zipfile
    b = bytes(data)
    if b[:4] == b"\xca\xfe\xba\xbe":
        return classfile_facts(b)
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
        names = z.namelist()
        mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace") if "META-INF/MANIFEST.MF" in names else ""
    except (zipfile.BadZipFile, KeyError, OSError, EOFError, RuntimeError, ValueError):
        return None
    mf = re.sub(r"\r?\n ", "", mf)   # manifest continuation lines (72-byte wrap)
    man = dict(re.findall(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", mf, re.M))
    out = {"main_class": man.get("Main-Class") or "none", "created_by": man.get("Created-By") or "none",
           "manifest_version": man.get("Manifest-Version") or "none",
           "class_count": str(sum(n.endswith(".class") for n in names)), "entry_count": str(len(names)),
           "app_class_count": str(sum(n.endswith(".class") and not n.startswith("META-INF/")
                                      and not JVM_LIBRARY.search(n) for n in names)),
           "has_kotlin_runtime": _jv(any(n.startswith("kotlin/") for n in names)),
           "has_coroutine_runtime": _jv(any(n.startswith(("kotlin/coroutines/", "kotlinx/coroutines/"))
                                             for n in names))}   # D7/D17: stdlib kotlin/coroutines/ counts (GM true)
    target = member or (out["main_class"] if out["main_class"] != "none" else None)
    if target:
        ent = target if target.endswith(".class") else target.replace(".", "/") + ".class"
        try:
            cf = classfile_facts(z.read(ent)) if ent in names else None
        except (zipfile.BadZipFile, OSError, EOFError, RuntimeError, ValueError):
            cf = None
        if cf:
            out = {**cf, **out}
    return out


def jvm_field(data, field, member=None):
    """One JVM fact as an answer string; "none" when the container parses but the field is absent, None when the
    bytes are neither a jar nor a class file. Never raises."""
    try:
        f = jar_jvm_facts(data, member)
    except Exception:  # noqa: BLE001
        return None
    if f is None:
        return None
    return f.get(field, "none")


# --- packing -------------------------------------------------------------------------------------
def entropy(data):
    """Shannon entropy (bits/byte, 0-8). Packed/encrypted payloads sit ~7.8+; normal code ~5-6.5."""
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in freq if c)


def packer_info(data):
    """Detect packing. Returns {packer, entropy, packed(bool)}. Catches UPX by magic and anything else by
    high whole-file entropy (a gate before analysis — a packed binary's symbols/sections are meaningless)."""
    e = round(entropy(data), 2)
    packer = None
    if b"UPX!" in data[:4096] or b"UPX0" in data or b"UPX1" in data or _upx_sniff(data):
        packer = "upx"   # _upx_sniff: the layout alone (scrubbed `UPX!`, renamed UPX0/1); unpack: upx_unpack(data)
    elif b"PEtite" in data[:4096]:
        packer = "petite"
    elif b"ASPack" in data[:4096]:
        packer = "aspack"
    packed = bool(packer) or e >= 7.2
    return {"packer": packer, "entropy": e, "packed": packed}


def unpack_upx(path):
    """Unpack a UPX binary to a sibling file, return its path (or the original if upx is absent/fails)."""
    if not shutil.which("upx"):
        return str(path)
    out = str(path) + ".unpacked"
    shutil.copy(path, out)
    r = subprocess.run(["upx", "-d", "-q", out], capture_output=True, timeout=120)
    return out if r.returncode == 0 else str(path)



# --- UPX, pure Python (in-window: no `upx -d` subprocess) ----------------------------------------------------------
# What answers from which bytes (a UPX'd artifact): sha256 / md5 / size = the PACKED artifact as handed out (that is the
# file the GM hashed); format / machine / has_hcfg_section / section names / the HCFG blob + its offset = the UNPACKED
# image (= `upx -d` output: the packed file has no .hcfg section, only UPX0/UPX1 or bare ELF segments). The magic may
# be scrubbed (`UPX!` zeroed, UPX0/1 renamed): nothing below needs it -- ELF: l_info/p_info/b_info sit right after the
# phdrs; PE: the first section is virtual-only (raw size 0) and the next one starts with the NRV stream.
HCFG_UPX_MAX = int(os.environ.get("HCTF_HCFG_UPX_MAX", str(24 << 20)))   # unpacked bytes (pure-Python NRV ~MB/s)
_NRV = {2: "b", 5: "d", 8: "e"}   # UPX M_NRV2B_LE32 / M_NRV2D_LE32 / M_NRV2E_LE32 (upx -1..-9 default methods)


def _nrv(src, ip, kind, cap, end=None):
    """UCL NRV2B/2D/2E (LE32 bit buffer) from src[ip:] -> (out, ip_after) or None (bad stream / over cap / late)."""
    out, n, bb, bc, last = bytearray(), len(src), 0, 0, 1
    try:
        def gb():
            nonlocal bb, bc, ip
            if not bc:
                if ip + 4 > n:
                    raise IndexError
                bb, bc, ip = int.from_bytes(src[ip:ip + 4], "little"), 32, ip + 4
            bc -= 1
            return (bb >> bc) & 1
        while True:
            while gb():
                out.append(src[ip])
                ip += 1
            off = 1
            while True:
                off = off * 2 + gb()
                if gb():
                    break
                if kind != "b":
                    off = (off - 1) * 2 + gb()
            if off == 2:
                off, ln = last, (gb() if kind != "b" else 0)
            else:
                off = ((off - 3) * 256 + src[ip]) & 0xFFFFFFFF
                ip += 1
                if off == 0xFFFFFFFF:
                    return bytes(out), ip
                if kind == "b":
                    ln, off = 0, off + 1
                else:
                    ln, off = (off ^ 0xFFFFFFFF) & 1, (off >> 1) + 1
                last = off
            if kind == "e":
                if ln:
                    ln = 1 + gb()
                elif gb():
                    ln = 3 + gb()
                else:
                    ln = 1
                    while True:
                        ln = ln * 2 + gb()
                        if gb():
                            break
                    ln += 3
            else:
                ln = ln * 2 + gb() if kind == "d" else gb() * 2 + gb()
                if not ln:
                    ln = 1
                    while True:
                        ln = ln * 2 + gb()
                        if gb():
                            break
                    ln += 2
            ln += 1 + (off > (0xD00 if kind == "b" else 0x500))
            st = len(out) - off
            if st < 0 or len(out) + ln > cap or (end is not None and time.time() > end):
                return None
            if off >= ln:
                out += out[st:st + ln]
            else:
                for k in range(ln):
                    out.append(out[st + k])
    except IndexError:
        return None


def _upx_block(data, p, end, cap):
    """b_info at p: (u_len, c_len, method, filter, cto) + payload -> (plain, next_p) or None."""
    if p + 12 > len(data):
        return None
    u, c, meth, flt, _cto, z = struct.unpack_from("<IIBBBB", data, p)
    if not (0 < c <= u <= cap) or z or p + 12 + c > len(data):
        return None
    if meth == 0 or c == u:   # stored
        return (data[p + 12:p + 12 + u], p + 12 + c) if c == u else None
    if meth not in _NRV:
        return None
    r = _nrv(data, p + 12, _NRV[meth], u, end)
    return (r[0], p + 12 + c) if r and len(r[0]) == u else None


def _upx_elf(data, end, cap):
    """UPX'd ELF64 LE -> the unpacked file bytes (`upx -d` layout; filtered code blocks left filtered) or None."""
    if data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        return None
    phoff, = struct.unpack_from("<Q", data, 0x20)
    phent, phnum = struct.unpack_from("<HH", data, 0x36)
    p = phoff + phent * phnum   # l_info (12) + p_info (12)
    if p + 36 > len(data) or phnum > 16:
        return None
    fsize, = struct.unpack_from("<I", data, p + 16)
    if not 64 <= fsize <= cap:
        return None
    r = _upx_block(data, p + 24, end, cap)
    if not r or r[0][:4] != b"\x7fELF" or r[0][4] != 2:
        return None
    hdr, p = r
    img = bytearray(fsize)
    o_phoff, = struct.unpack_from("<Q", hdr, 0x20)
    o_phent, o_phnum = struct.unpack_from("<HH", hdr, 0x36)
    loads = []
    for k in range(o_phnum):
        q = o_phoff + k * o_phent
        if q + 56 > len(hdr):
            return None
        ptype, _fl, off, _va, _pa, filesz = struct.unpack_from("<IIQQQQ", hdr, q)
        if ptype == 1 and filesz:
            loads.append((off, filesz))
    covered, first = [], True
    for off, filesz in loads:
        pos = off
        while pos < off + filesz:
            if first:
                blk, first = hdr, False
            else:
                r = _upx_block(data, p, end, cap)
                if not r:
                    return None
                blk, p = r
            if pos + len(blk) > fsize:
                return None
            img[pos:pos + len(blk)] = blk
            pos += len(blk)
        covered.append((off, pos))
    gaps, cur = [], 0   # non-PT_LOAD pieces (padding, .comment/.symtab/section headers) follow the loader stub
    for a, b in sorted(covered) + [(fsize, fsize)]:
        if a > cur:
            gaps.append((cur, a))
        cur = max(cur, b)
    q, lim = p, min(len(data), p + (64 << 10))
    while gaps and q < lim:
        a, b = gaps[0]
        if struct.unpack_from("<I", data, q)[0] == b - a if q + 4 <= len(data) else False:
            r = _upx_block(data, q, end, cap)
            if r:
                img[a:b] = r[0]
                gaps.pop(0)
                q = r[1]
                continue
        q += 1
    return bytes(img)


def _upx_pe(data, end, cap):
    """UPX'd PE32/PE32+ -> the unpacked file bytes (original headers + sections at their original raw offsets)."""
    if data[:2] != b"MZ" or len(data) < 0x200:
        return None
    e = int.from_bytes(data[0x3C:0x40], "little")
    if data[e:e + 4] != b"PE\0\0":
        return None
    nsec, = struct.unpack_from("<H", data, e + 6)
    opt, = struct.unpack_from("<H", data, e + 20)
    st = e + 24 + opt
    secs = [struct.unpack_from("<8sIIII", data, st + 40 * k) for k in range(min(nsec, 96))]
    if len(secs) < 2 or secs[0][3] or not secs[0][1] or not secs[1][3]:
        return None   # UPX0: virtual only; UPX1: the compressed stream at its raw start
    base, raw1 = secs[0][2], secs[1][4]
    meths = list(_NRV.values())
    ph = data.rfind(b"UPX!", 0, raw1)
    if ph >= 0 and ph + 12 <= len(data) and data[ph + 6] in _NRV:
        meths.remove(_NRV[data[ph + 6]])
        meths.insert(0, _NRV[data[ph + 6]])
    for kind in meths:
        r = _nrv(data, raw1, kind, cap, end)
        if not r:
            continue
        u = r[0]
        k = u.rfind(b"PE\0\0")
        while k >= 0:   # the original PE header + section table ride after the image
            onsec, = struct.unpack_from("<H", u, k + 6) if k + 24 <= len(u) else (0,)
            oopt, = struct.unpack_from("<H", u, k + 20) if k + 24 <= len(u) else (0,)
            ost = k + 24 + oopt
            if 0 < onsec <= 96 and ost + 40 * onsec <= len(u):
                osecs = [struct.unpack_from("<8sIIII", u, ost + 40 * j) for j in range(onsec)]
                size = max(rp + rs for _n, _vs, _va, rs, rp in osecs)
                if size <= cap and all(va >= base for _n, _vs, va, _rs, _rp in osecs):
                    hdr = ost + 40 * onsec - k
                    img = bytearray(max(size, e + hdr))
                    img[:e] = data[:e]
                    img[e:e + hdr] = u[k:k + hdr]
                    for _n, vs, va, rs, rp in osecs:
                        piece = u[va - base:va - base + rs]
                        img[rp:rp + len(piece)] = piece
                    return bytes(img)
            k = u.rfind(b"PE\0\0", 0, k)
    return None


def _upx_sniff(data):
    """Cheap UPX layout check (no decompression): ELF l_info/p_info/b_info after the phdrs, or PE whose first section
    is virtual-only and whose entry point lies in the second."""
    try:
        if data[:4] == b"\x7fELF" and data[4] == 2 and data[5] == 1:
            phoff, = struct.unpack_from("<Q", data, 0x20)
            phent, phnum = struct.unpack_from("<HH", data, 0x36)
            p = phoff + phent * phnum
            fsize, = struct.unpack_from("<I", data, p + 16)
            u, c, meth, _f, _c, z = struct.unpack_from("<IIBBBB", data, p + 24)
            return phnum <= 16 and data[p + 11] in (0x16, 0x17) and 0 < c <= u <= fsize and meth in _NRV and not z
        if data[:2] == b"MZ":
            e = int.from_bytes(data[0x3C:0x40], "little")
            if data[e:e + 4] != b"PE\0\0":
                return False
            opt, = struct.unpack_from("<H", data, e + 20)
            ep, = struct.unpack_from("<I", data, e + 40)
            (_n0, vs0, va0, rs0, _p0), (_n1, vs1, va1, rs1, _p1) = (
                struct.unpack_from("<8sIIII", data, e + 24 + opt + 40 * k) for k in range(2))
            return not rs0 and vs0 > 0 and rs1 > 0 and va1 == va0 + vs0 and va1 <= ep < va1 + vs1
    except (struct.error, IndexError):
        pass
    return False


def upx_unpack(data, *, deadline=None, cap=None):
    """The `upx -d` image of a UPX'd ELF64/PE (NRV2B/2D/2E; magic may be scrubbed) as bytes, or None. Pure Python.
    ELF code blocks under a UPX call/jmp filter stay filtered (data sections -- .hcfg, .rodata -- are exact)."""
    data, cap = bytes(data), cap or HCFG_UPX_MAX
    try:
        return _upx_elf(data, _ends(deadline), cap) or _upx_pe(data, _ends(deadline), cap)
    except (struct.error, IndexError, ValueError, MemoryError):
        return None


def upx_hcfg(data, **kw):
    """(unpacked image, first crc-valid HcfgHit inside it) for a UPX'd artifact, else (None, None). The hit's offset
    is an offset in the UNPACKED image."""
    img = upx_unpack(data, deadline=kw.get("deadline"))
    return (img, hcfg_find(img, **kw)) if img else (None, None)

# --- Go / Rust symbol recovery -------------------------------------------------------------------
def go_buildinfo(data):
    """Go version string from the `\\xff Go buildinf:` blob (present even when stripped), or None."""
    m = re.search(rb"go1\.\d+(\.\d+)?", data)
    return m.group(0).decode() if m else None


def go_pclntab_funcs(data, limit=4000):
    """Recover Go function names from .gopclntab — they survive symbol stripping. Version-agnostic: pulls
    the section (or scans for the pclntab magic) and extracts Go-symbol-shaped null-terminated strings
    (package-qualified: main.*, runtime.*, path/pkg.*). Returns a sorted de-duped list."""
    from elftools.elf.elffile import ELFFile
    blob = b""
    try:
        elf = ELFFile(io.BytesIO(data))
        for sname in (".gopclntab", ".data.rel.ro.gopclntab", ".data.rel.ro"):
            s = elf.get_section_by_name(sname)
            if s:
                blob += s.data()
    except Exception:  # noqa: BLE001 - not an ELF / no sections: fall back to a raw magic scan
        pass
    if not blob:
        for magic in (b"\xf0\xff\xff\xff", b"\xf1\xff\xff\xff", b"\xfa\xff\xff\xff", b"\xfb\xff\xff\xff"):
            i = data.find(magic)
            if i >= 0:
                blob = data[i:i + 4_000_000]
                break
    names = set()
    # Go symbol names: package-path-qualified, ASCII, contain a '.', may carry * ( ) [ ] / and digits.
    for m in re.finditer(rb"[A-Za-z_][\w./*()\[\]<>,;$-]{2,120}", blob):
        s = m.group(0)
        try:
            t = s.decode("ascii")
        except UnicodeDecodeError:
            continue
        if "." in t and ("/" in t or t.split(".")[0] in ("main", "runtime", "fmt", "os", "net", "sync",
                                                          "internal", "crypto", "encoding", "reflect")
                         or re.match(r"^[a-z][\w]*\.[A-Za-z]", t)):
            names.add(t)
    return sorted(names)[:limit]


def rustfilt(symbol):
    """Demangle a Rust v0/legacy symbol if `rustfilt` is on PATH, else return it unchanged."""
    if not shutil.which("rustfilt"):
        return symbol
    r = subprocess.run(["rustfilt"], input=symbol, capture_output=True, text=True, timeout=10)
    return r.stdout.strip() or symbol


# --- Mach-O --------------------------------------------------------------------------------------
def macho_facts(data):
    """Header facts for a Mach-O (fat or thin): macho_layout() (pure struct: machine(s), sections, has_hcfg_section,
    every slice) enriched by lief (first slice: cpu type, file type, flags, dylibs, entry). {} if not a Mach-O."""
    lay = macho_layout(data)
    if not lay:
        return {}
    out = dict(lay)
    try:
        import lief
        try:
            lief.logging.disable()
        except Exception:  # noqa: BLE001
            pass
        fat = lief.MachO.parse(bytes(data))
        if fat is not None and fat.size:
            b = fat.at(0)
            h = b.header
            out.update({
                "cpu_type": str(h.cpu_type).split(".")[-1].lower(),
                "file_type": str(h.file_type).split(".")[-1].lower(),
                "nb_cmds": h.nb_cmds,
                "pie": bool(h.has(lief.MachO.Header.FLAGS.PIE)) if hasattr(h, "has") else None,
                "libraries": [lib.name for lib in b.libraries][:40],
                "entrypoint": hex(b.entrypoint) if hasattr(b, "entrypoint") else None,
            })
    except Exception:  # noqa: BLE001  (lief missing / API drift / malformed: keep the struct facts)
        pass
    return out


_MO_MAGIC = {b"\xce\xfa\xed\xfe": ("little", 32), b"\xcf\xfa\xed\xfe": ("little", 64),
             b"\xfe\xed\xfa\xce": ("big", 32), b"\xfe\xed\xfa\xcf": ("big", 64)}


def _macho_thin(data, base=0):
    """One thin Mach-O slice at data[base:] -> {machine, machine_num, cputype, endian, bits, slice_offset, sections:
    [{segment, section, name "SEG,sect", offset (file offset, fat-absolute), size}]} or None. Pure struct, bounded."""
    mo = _MO_MAGIC.get(bytes(data[base:base + 4]))
    if not mo or len(data) < base + 28:
        return None
    end, bits = mo
    u32 = lambda o: int.from_bytes(data[o:o + 4], end)   # noqa: E731
    cpu, ncmds, sizeofcmds = u32(base + 4), u32(base + 16), u32(base + 20)
    p = base + (32 if bits == 64 else 28)
    stop = min(len(data), p + sizeofcmds)
    secs = []
    for _ in range(min(ncmds, 4096)):
        if p + 8 > stop:
            break
        cmd, size = u32(p), u32(p + 4)
        if size < 8:
            break
        if cmd in (0x1, 0x19):   # LC_SEGMENT / LC_SEGMENT_64
            w = 8 if cmd == 0x19 else 4
            nsects = u32(p + 24 + 4 * w + 8)
            q, ssz = p + 24 + 4 * w + 16, 80 if w == 8 else 68   # section_64 / section
            for _ in range(min(nsects, 1024)):
                if q + ssz > min(stop, p + size):
                    break
                sect = bytes(data[q:q + 16]).split(b"\0")[0].decode("latin-1")
                seg = bytes(data[q + 16:q + 32]).split(b"\0")[0].decode("latin-1")
                sz = int.from_bytes(data[q + 32 + w:q + 32 + 2 * w], end)
                off = u32(q + 32 + 2 * w)
                secs.append({"segment": seg, "section": sect, "name": f"{seg},{sect}",
                             "offset": base + off if off else 0, "size": sz, "flags": u32(q + 48 + 2 * w)})
                q += ssz
        p += size
    return {"machine": MACHO_CPU_LABEL.get(cpu, str(cpu)), "machine_num": str(cpu), "cputype": f"0x{cpu:08x}",
            "endian": end, "bits": bits, "slice_offset": base, "sections": secs}


def macho_layout(data):
    """Pure-struct Mach-O facts for thin AND fat/universal files: {format "mach-o", fat, slices [_macho_thin...],
    machine / machine_num / bits (first slice), machines (every slice), section_names ["__DATA,__hcfg", ...] and
    section_names_short ["__hcfg", ...] over all slices, has_hcfg_section "true"/"false" (a section whose sectname is
    __hcfg / .hcfg / hcfg, any segment)}; None if not a Mach-O. A Java .class shares the fat magic 0xcafebabe: it is
    rejected because its u32 at +4 (minor<<16|major, major >= 45) is not a small slice count and/or its "fat_arch"
    entries do not point inside the file at a thin Mach-O."""
    try:
        data = memoryview(data) if not isinstance(data, memoryview) else data
        slices, fat = [], False
        head = bytes(data[:4])
        if head in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
            n = int.from_bytes(data[4:8], "big")
            if not 0 < n < 32:
                return None
            w = 32 if head[3] == 0xbf else 20   # fat_arch_64 / fat_arch
            for k in range(n):
                e = 8 + k * w
                if e + w > len(data):
                    return None
                off = int.from_bytes(data[e + 8:e + 16] if w == 32 else data[e + 8:e + 12], "big")
                s = _macho_thin(data, off) if 0 < off < len(data) else None
                if s is not None:   # a truncated tail slice is skipped; no thin slice at all -> not fat (Java)
                    slices.append(s)
            if not slices:
                return None
            fat = True
        else:
            s = _macho_thin(data)
            if s is None:
                return None
            slices.append(s)
        names = [x["name"] for s in slices for x in s["sections"]]
        short = [x["section"] for s in slices for x in s["sections"]]
        return {"format": "mach-o", "fat": fat, "slices": slices, "machine": slices[0]["machine"],
                "machine_num": slices[0]["machine_num"], "bits": slices[0]["bits"],
                "machines": [s["machine"] for s in slices],
                "section_names": list(dict.fromkeys(names)), "section_names_short": list(dict.fromkeys(short)),
                "has_hcfg_section": "true" if any(x.lstrip("_.").lower() == "hcfg" for x in short) else "false"}
    except (IndexError, ValueError, TypeError):
        return None


def macho_hcfg_section(data):
    """[(slice machine, file offset, bytes)] of every __hcfg-named section in a thin/fat Mach-O ([] if none)."""
    lay = macho_layout(data) or {}
    out = []
    for s in lay.get("slices", ()):
        for x in s["sections"]:
            if x["section"].lstrip("_.").lower() == "hcfg" and x["offset"]:
                out.append((s["machine"], x["offset"], bytes(data[x["offset"]:x["offset"] + x["size"]])))
    return out


WASM_SECTION_NAMES = {0: "custom", 1: "type", 2: "import", 3: "function", 4: "table", 5: "memory", 6: "global",
                      7: "export", 8: "start", 9: "element", 10: "code", 11: "data", 12: "datacount", 13: "tag"}


def _leb(data, p, signed=False, cap=10):
    """(value, next position) of the (s)LEB128 at p; IndexError past the end / ValueError when longer than cap bytes."""
    v = sh = 0
    for _ in range(cap):
        b = data[p]
        p += 1
        v |= (b & 0x7f) << sh
        sh += 7
        if not b & 0x80:
            if signed and b & 0x40:
                v -= 1 << sh
            return v, p
    raise ValueError("leb128 too long")


def wasm_layout(data):
    """Pure-struct WebAssembly module facts: {format "wasm", machine "wasm32" ("wasm64" when a defined/imported
    memory has the memory64 limits flag 0x04; SPECULATIVE label, not GM-verified), version, sections [{id, name,
    offset (payload file offset), size}], section_names (custom sections by their own name), memories [{index,
    memory64, min, max, imported}], data_segments [{index, mode active/passive, memory, mem_offset (int, None when
    the init expr is a global.get e.g. Emscripten __memory_base), file_offset (first payload byte), size}]}; None if
    not a version-1 wasm binary (the '\\0asm' magic alone does not count: every section must parse to the end).
    Plus the _wasm_inventory keys (imports/exports/tables/elems/start/globals/custom_names/...; see wasm_fields)."""
    try:
        data = memoryview(data) if not isinstance(data, memoryview) else data
        if bytes(data[:4]) != b"\0asm" or len(data) < 8 or int.from_bytes(data[4:8], "little") != 1:
            return None
        p, end = 8, len(data)
        secs, mems, segs = [], [], []

        def limits(q):
            fl, q = _leb(data, q)
            mn, q = _leb(data, q)
            mx = None
            if fl & 1:
                mx, q = _leb(data, q)
            if fl & 8:   # custom-page-sizes proposal: page size log2
                q = _leb(data, q)[1]
            return fl, mn, mx, q

        while p < end:
            sid = data[p]
            size, q = _leb(data, p + 1, cap=5)
            if sid > 13 or q + size > end:
                return None
            e = q + size
            name = WASM_SECTION_NAMES[sid]
            if sid == 0:
                n, r = _leb(data, q, cap=5)
                if r + n > e:
                    return None
                name = bytes(data[r:r + n]).decode("utf-8", "replace")
            secs.append({"id": sid, "name": name, "offset": q, "size": size})
            if sid == 2:     # imports: only memory imports matter (memory index space starts with them)
                n, r = _leb(data, q, cap=5)
                for _ in range(n):
                    for _f in range(2):
                        ln, r = _leb(data, r, cap=5)
                        r += ln
                    kind = data[r]
                    r += 1
                    if kind == 0:
                        r = _leb(data, r)[1]
                    elif kind == 1:
                        r = limits(r + 1)[3]
                    elif kind == 2:
                        fl, mn, mx, r = limits(r)
                        mems.append({"index": len(mems), "memory64": bool(fl & 4), "min": mn, "max": mx,
                                     "imported": True, "shared": bool(fl & 2)})
                    elif kind == 3:
                        r += 2
                    elif kind == 4:
                        r = _leb(data, r + 1)[1]
                    else:
                        return None
            elif sid == 5:
                n, r = _leb(data, q, cap=5)
                for _ in range(n):
                    fl, mn, mx, r = limits(r)
                    mems.append({"index": len(mems), "memory64": bool(fl & 4), "min": mn, "max": mx,
                                 "imported": False, "shared": bool(fl & 2)})
            elif sid == 11:
                n, r = _leb(data, q, cap=5)
                for k in range(n):
                    fl, r = _leb(data, r, cap=5)
                    mem, moff = 0, None
                    if fl == 2:
                        mem, r = _leb(data, r, cap=5)
                    if fl in (0, 2):   # active: constant init expr, then 0x0b
                        op = data[r]
                        if op in (0x41, 0x42):          # i32.const / i64.const (sLEB; addresses are unsigned)
                            moff, r = _leb(data, r + 1, signed=True)
                            moff &= (1 << (32 if op == 0x41 else 64)) - 1
                        elif op == 0x23:                # global.get
                            r = _leb(data, r + 1)[1]
                        else:
                            return None
                        while data[r] != 0x0b:          # extended-const tails (i32.add ...): offset unknown
                            moff, r = None, r + 1
                        r += 1
                    elif fl != 1:
                        return None
                    ln, r = _leb(data, r, cap=5)
                    if r + ln > e:
                        return None
                    segs.append({"index": k, "mode": "passive" if fl == 1 else "active", "memory": mem,
                                 "mem_offset": moff, "file_offset": r, "size": ln})
                    r += ln
            p = e
        out = {"format": "wasm", "machine": "wasm64" if any(m["memory64"] for m in mems) else "wasm32",
               "version": 1, "sections": secs, "section_names": [s["name"] for s in secs], "memories": mems,
               "data_segments": segs}
    except (IndexError, ValueError, TypeError):
        return None
    out.update(_wasm_inventory(data, secs))
    return out


WASM_EXTERN_KINDS = {0: "func", 1: "table", 2: "memory", 3: "global", 4: "tag"}
WASM_VALTYPES = {0x7f: "i32", 0x7e: "i64", 0x7d: "f32", 0x7c: "f64", 0x7b: "v128", 0x70: "funcref",
                 0x6f: "externref"}


def _wasm_const(data, q):
    """(value, next position after the 0x0b) of a constant init expr: int for i32/i64.const, ('global', i) for
    global.get, ('func', i) for ref.func, None for ref.null / floats / extended-const arithmetic."""
    val, ops = None, 0
    while True:
        op = data[q]
        q += 1
        if op == 0x0b:
            return (val if ops == 1 else None), q
        ops += 1
        if op in (0x41, 0x42):
            v, q = _leb(data, q, signed=True)
            val = v & ((1 << (32 if op == 0x41 else 64)) - 1)
        elif op == 0x23:
            v, q = _leb(data, q)
            val = ("global", v)
        elif op == 0xd2:
            v, q = _leb(data, q)
            val = ("func", v)
        elif op == 0xd0:
            q = _leb(data, q, signed=True)[1]    # heap type (0x70 / 0x6f or a type index)
            val = None
        elif op == 0x43:
            q += 4
        elif op == 0x44:
            q += 8
        elif op == 0xfd:                          # v128.const
            q = _leb(data, q)[1] + 16
        elif op in (0x6a, 0x6b, 0x6c, 0x7c, 0x7d, 0x7e):   # extended-const add/sub/mul
            pass
        else:
            raise ValueError("init expr op %#x" % op)


def _wasm_name(data, q):
    n, q = _leb(data, q, cap=5)
    return bytes(data[q:q + n]).decode("utf-8", "replace"), q + n


def _wasm_inventory(data, secs):
    """The module's 'doors' (wasm_layout extras): imports [{module, name, kind, index}] (index in its kind's index
    space), import_names ["module.name"] in section order, exports [{name, kind, index}], export_names, tables
    [{index, reftype, min, max, imported}], elems [{index, mode active/passive/declarative, table, offset,
    func_indices (None = ref.null)}], start (func index or None), globals [{index, valtype, mutable, imported,
    init}], type_count, function_count (defined), code_count, data_count (DataCount section or None),
    custom_names, func_names {index: name} (name section, else the linking symbol table), module_name, producers
    {field: [[name, version]]}, inventory_ok (False when some section failed to parse -> fields partial)."""
    imps, exps, tabs, elems, globs, fnames, prod = [], [], [], [], [], {}, {}
    inv = {"imports": imps, "import_names": [], "exports": exps, "export_names": [], "tables": tabs, "elems": elems,
           "start": None, "globals": globs, "type_count": 0, "function_count": 0, "code_count": 0, "data_count": None,
           "custom_names": [s["name"] for s in secs if s["id"] == 0], "func_names": fnames, "module_name": None,
           "producers": prod, "inventory_ok": True}
    cnt = {k: 0 for k in WASM_EXTERN_KINDS.values()}

    def limits(q):
        fl, q = _leb(data, q)
        mn, q = _leb(data, q)
        mx = None
        if fl & 1:
            mx, q = _leb(data, q)
        if fl & 8:
            q = _leb(data, q)[1]
        return mn, mx, q

    def reftype(q):
        b = data[q]
        if b in (0x63, 0x64):                       # (ref null? ht) typed reference
            return "ref", _leb(data, q + 1, signed=True)[1]
        return WASM_VALTYPES.get(b, "0x%02x" % b), q + 1

    for s in secs:
        sid, q = s["id"], s["offset"]
        e = q + s["size"]
        try:
            if sid == 1:
                inv["type_count"] = _leb(data, q, cap=5)[0]
            elif sid == 3:
                inv["function_count"] = _leb(data, q, cap=5)[0]
            elif sid == 10:
                inv["code_count"] = _leb(data, q, cap=5)[0]
            elif sid == 12:
                inv["data_count"] = _leb(data, q, cap=5)[0]
            elif sid == 8:
                inv["start"] = _leb(data, q, cap=5)[0]
            elif sid == 2:
                n, r = _leb(data, q, cap=5)
                for _ in range(n):
                    mod, r = _wasm_name(data, r)
                    nm, r = _wasm_name(data, r)
                    kind = WASM_EXTERN_KINDS.get(data[r], None)
                    r += 1
                    if kind == "func":
                        r = _leb(data, r)[1]
                    elif kind == "table":
                        rt, r = reftype(r)
                        mn, mx, r = limits(r)
                        tabs.append({"index": cnt["table"], "reftype": rt, "min": mn, "max": mx, "imported": True})
                    elif kind == "memory":
                        r = limits(r)[2]
                    elif kind == "global":
                        vt = WASM_VALTYPES.get(data[r], "0x%02x" % data[r])
                        globs.append({"index": cnt["global"], "valtype": vt, "mutable": bool(data[r + 1] & 1),
                                      "imported": True, "init": None})
                        r += 2
                    elif kind == "tag":
                        r = _leb(data, r + 1)[1]
                    else:
                        raise ValueError("import kind")
                    imps.append({"module": mod, "name": nm, "kind": kind, "index": cnt[kind]})
                    inv["import_names"].append(mod + "." + nm)
                    cnt[kind] += 1
            elif sid == 4:
                n, r = _leb(data, q, cap=5)
                for _ in range(n):
                    init = None
                    if data[r] == 0x40 and data[r + 1] == 0:   # function-references: table with an init expr
                        rt, r = reftype(r + 2)
                        mn, mx, r = limits(r)
                        init, r = _wasm_const(data, r)
                    else:
                        rt, r = reftype(r)
                        mn, mx, r = limits(r)
                    tabs.append({"index": len(tabs), "reftype": rt, "min": mn, "max": mx, "imported": False})
            elif sid == 6:
                n, r = _leb(data, q, cap=5)
                for _ in range(n):
                    b = data[r]
                    if b in (0x63, 0x64):
                        vt, r = reftype(r)
                    else:
                        vt, r = WASM_VALTYPES.get(b, "0x%02x" % b), r + 1
                    mut = bool(data[r] & 1)
                    init, r = _wasm_const(data, r + 1)
                    globs.append({"index": len(globs), "valtype": vt, "mutable": mut, "imported": False,
                                  "init": init if isinstance(init, int) else None})
            elif sid == 7:
                n, r = _leb(data, q, cap=5)
                for _ in range(n):
                    nm, r = _wasm_name(data, r)
                    kind = WASM_EXTERN_KINDS.get(data[r], "0x%02x" % data[r])
                    idx, r = _leb(data, r + 1, cap=5)
                    exps.append({"name": nm, "kind": kind, "index": idx})
                    inv["export_names"].append(nm)
            elif sid == 9:
                n, r = _leb(data, q, cap=5)
                for k in range(n):
                    fl, r = _leb(data, r, cap=5)
                    tab, off = 0, None
                    mode = "passive" if fl & 3 == 1 else "declarative" if fl & 3 == 3 else "active"
                    if fl & 2 and not fl & 1:
                        tab, r = _leb(data, r, cap=5)
                    if mode == "active":
                        off, r = _wasm_const(data, r)
                        off = off if isinstance(off, int) else None
                    if fl & 3:                       # elemkind (0x00) / reftype byte
                        r = reftype(r)[1] if fl & 4 else r + 1
                    m, r = _leb(data, r, cap=5)
                    fi = []
                    for _i in range(m):
                        if fl & 4:
                            v, r = _wasm_const(data, r)
                            fi.append(v[1] if isinstance(v, tuple) and v[0] == "func" else None)
                        else:
                            v, r = _leb(data, r, cap=5)
                            fi.append(v)
                    elems.append({"index": k, "mode": mode, "table": tab, "offset": off, "func_indices": fi})
            elif sid == 0 and s["name"] == "name":
                r = _wasm_name(data, q)[1]
                while r < e:
                    sub = data[r]
                    sz, r = _leb(data, r + 1, cap=5)
                    if sub == 0:
                        inv["module_name"] = _wasm_name(data, r)[0]
                    elif sub == 1:
                        n, t = _leb(data, r, cap=5)
                        for _ in range(n):
                            i, t = _leb(data, t, cap=5)
                            fnames[i], t = _wasm_name(data, t)
                    r += sz
            elif sid == 0 and s["name"] == "producers":
                r = _wasm_name(data, q)[1]
                n, r = _leb(data, r, cap=5)
                for _ in range(n):
                    fld, r = _wasm_name(data, r)
                    m, r = _leb(data, r, cap=5)
                    vals = []
                    for _i in range(m):
                        a, r = _wasm_name(data, r)
                        b, r = _wasm_name(data, r)
                        vals.append([a, b])
                    prod[fld] = vals
            elif sid == 0 and s["name"] == "linking" and not fnames:
                r = _leb(data, _wasm_name(data, q)[1], cap=5)[1]          # version
                while r < e:
                    sub = data[r]
                    sz, r = _leb(data, r + 1, cap=5)
                    if sub == 8:                                          # WASM_SYMBOL_TABLE
                        n, t = _leb(data, r, cap=5)
                        for _ in range(n):
                            kind = data[t]
                            fl, t = _leb(data, t + 1, cap=5)
                            if kind in (0, 2, 4, 5):                      # func / global / tag / table
                                idx, t = _leb(data, t, cap=5)
                                nm = None
                                if not fl & 0x10 or fl & 0x40:            # defined, or explicit name
                                    nm, t = _wasm_name(data, t)
                                if kind == 0 and nm is not None:
                                    fnames.setdefault(idx, nm)
                            elif kind == 1:                               # data
                                t = _wasm_name(data, t)[1]
                                if not fl & 0x10:
                                    for _i in range(3):
                                        t = _leb(data, t)[1]
                            elif kind == 3:                               # section
                                t = _leb(data, t, cap=5)[1]
                            else:
                                break
                    r += sz
        except (IndexError, ValueError, TypeError, KeyError):
            inv["inventory_ok"] = False
    return inv


def wasm_fields(data):
    """Flat answer-field candidates for a wasm module's 'doors' (None if not wasm). Lists are in section order
    (render as JSON); absent singletons are "none"; counts are ints; booleans are True/False. Imports render as
    "module.name"; functions by their name-section / linking-symbol name, else "module.name" for imports, else the
    index. *_count = entries of that section (defined), total_*_count = the index space incl. imports; has_table
    counts an imported table too. memory_* = memory 0 (pages, 64 KiB each). indirect_targets = the funcs placed in tables by active elem
    segments (call_indirect targets) in segment/slot order. hcfg_offset = FILE offset of the 'H' of the first crc-valid
    blob in a data segment (else a custom section, else the wasm-split/init/store hcfg_scan hit), hcfg_mem_offset = its
    linear-memory address (passive segments: where memory.init copies it; "none" if never / custom section);
    has_hcfg_section = a custom section named hcfg/.hcfg exists; hcfg_section = the custom section holding the blob;
    hcfg_storage = active/passive/custom/split/init/store (SPECULATIVE names)."""
    lay = wasm_layout(data)
    if not lay:
        return None
    imps, fn = lay["imports"], lay["func_names"]
    nimpf = sum(1 for i in imps if i["kind"] == "func")
    impf = {i["index"]: i["module"] + "." + i["name"] for i in imps if i["kind"] == "func"}

    def fname(i):
        return fn.get(i) or impf.get(i) or i

    def nz(v):
        return "none" if v is None or v == [] or v == {} else v

    mem = (lay["memories"] or [None])[0]
    tab = (lay["tables"] or [None])[0]
    act = [e for e in lay["elems"] if e["mode"] == "active"]
    tgt = [fname(i) for e in act for i in e["func_indices"] if i is not None]
    segs = lay["data_segments"]
    hc = next(iter(wasm_hcfg_segment(data)), {})
    st = lay["start"]
    return {
        "format": "wasm", "machine": lay["machine"],
        "import_count": len(imps), "imports": nz(lay["import_names"]),
        "import_modules": nz(list(dict.fromkeys(i["module"] for i in imps))),
        "imported_functions": nz([i["module"] + "." + i["name"] for i in imps if i["kind"] == "func"]),
        "imported_function_count": nimpf,
        "export_count": len(lay["exports"]), "exports": nz(lay["export_names"]),
        "exported_functions": nz([e["name"] for e in lay["exports"] if e["kind"] == "func"]),
        "function_count": lay["function_count"], "total_function_count": nimpf + lay["function_count"],
        "type_count": lay["type_count"],
        "memory_count": len(lay["memories"]), "has_memory": bool(lay["memories"]),
        "memory_min": nz(mem and mem["min"]), "memory_max": nz(mem and mem["max"]),
        "memory_shared": bool(mem and mem["shared"]), "memory64": bool(mem and mem["memory64"]),
        "memory_imported": bool(mem and mem["imported"]),
        "has_table": bool(lay["tables"]), "total_table_count": len(lay["tables"]),
        "table_count": sum(1 for t in lay["tables"] if not t["imported"]),
        "table_min": nz(tab and tab["min"]), "table_max": nz(tab and tab["max"]),
        "table_reftype": nz(tab and tab["reftype"]), "table_imported": bool(tab and tab["imported"]),
        "elem_count": len(lay["elems"]), "active_elem_count": len(act),
        "indirect_targets": nz(tgt), "indirect_target_count": len(tgt),
        "has_start": st is not None, "start_index": nz(st), "start_function": nz(None if st is None else fname(st)),
        "global_count": sum(1 for g in lay["globals"] if not g["imported"]), "total_global_count": len(lay["globals"]),
        "mutable_global_count": sum(1 for g in lay["globals"] if g["mutable"]),
        "imported_global_count": sum(1 for g in lay["globals"] if g["imported"]),
        "data_segment_count": len(segs),
        "active_data_segment_count": sum(1 for d in segs if d["mode"] == "active"),
        "passive_data_segment_count": sum(1 for d in segs if d["mode"] == "passive"),
        "data_offsets": nz([d["mem_offset"] for d in segs if d["mode"] == "active"]),
        "data_count": nz(lay["data_count"]),
        "custom_sections": nz(lay["custom_names"]), "custom_section_count": len(lay["custom_names"]),
        "has_name_section": "name" in lay["custom_names"], "module_name": nz(lay["module_name"]),
        "producers": nz(lay["producers"]),
        "hcfg_offset": nz(hc.get("file_offset")), "hcfg_mem_offset": nz(hc.get("mem_offset")),
        "hcfg_segment": nz(hc.get("segment")),
        "has_hcfg_section": any(n.lower().lstrip(".") == "hcfg" for n in lay["custom_names"]),
        "hcfg_section": nz(hc.get("section")), "hcfg_storage": nz(hc.get("mode")),
    }


def wasm_field(data, name):
    """One wasm_fields value; "none" when the input is not wasm or the field is unknown/absent."""
    try:
        return (wasm_fields(data) or {}).get(name, "none")
    except Exception:  # noqa: BLE001 -- untrusted bytes: never raise past the field
        return "none"


def wasm_hcfg_segment(data):
    """[{segment, mode, file_offset, mem_offset, segment_file_offset, segment_mem_offset}] for every crc-valid raw
    HCFG blob inside a wasm data segment ([] if none / not wasm). file_offset = the 'H' in the file (= hcfg_scan's raw
    offset); mem_offset = segment memory offset + the blob's position in the segment (linear-memory address, None for
    passive / global-based segments)."""
    lay = wasm_layout(data) or {}
    out = []
    inits = {}   # passive segment file offset -> linear address it is memory.init'ed to (first such copy)
    if any(s["mode"] == "passive" for s in lay.get("data_segments", ())):
        for a, _b, fo, k in wasm_memory_writes(data, lay):
            if k == "init":
                inits.setdefault(fo, a)
    for s in lay.get("data_segments", ()):
        lo = s["file_offset"]
        seg = bytes(data[lo:lo + s["size"]])
        i = seg.find(HCFG_MAGIC)
        while i >= 0:
            blob = seg[i:]
            r = _parse_blob(blob[:_need(blob[:8])]) if len(blob) >= 12 else None
            if r and r[5]:
                mo = s["mem_offset"]
                if mo is None and s["mode"] == "passive":   # memory.init'ed copy covering the blob start
                    mo = next((a - (f - lo) for f, a in inits.items() if lo <= f <= lo + i), None)
                out.append({"segment": s["index"], "mode": s["mode"], "file_offset": lo + i,
                            "mem_offset": None if mo is None else mo + i, "segment_file_offset": lo,
                            "segment_mem_offset": mo})
            i = seg.find(HCFG_MAGIC, i + 1)
    for s in lay.get("sections", ()):   # custom section (e.g. `hcfg`): no linear-memory address
        if s["id"] == 0:
            lo, e = s["offset"], s["offset"] + s["size"]
            i = bytes(data[lo:e]).find(HCFG_MAGIC)
            while i >= 0:
                blob = bytes(data[lo + i:e])
                r = _parse_blob(blob[:_need(blob[:8])]) if len(blob) >= 12 else None
                if r and r[5]:
                    out.append({"segment": None, "mode": "custom", "section": s["name"], "file_offset": lo + i,
                                "mem_offset": None, "segment_file_offset": lo, "segment_mem_offset": None})
                i = bytes(data[lo:e]).find(HCFG_MAGIC, i + 1)
    if not out:   # not contiguous in the file: split over segments / memory.init'ed / built by const stores
        got = []
        _wasm_mem_scan(bytes(data), lambda off, enc, blob, det="": got.append((off, enc, det)), None, 0)
        for off, enc, det in got[:1]:
            out.append({"segment": None, "mode": enc.split("-")[1], "file_offset": off,
                        "mem_offset": int(det.split("mem=")[1].split()[0]), "segment_file_offset": None,
                        "segment_mem_offset": None})
    return out


def bpf_layout(data):
    """Pure-struct eBPF ELF object facts (clang -target bpf -c; e_machine 247 EM_BPF, either byte order), None if not
    an ELF with e_machine 247 or its section table does not parse. {format "elf", elf_type ET_* (readelf constant),
    machine "Linux BPF" (GNU readelf spelling), machine_num "247", entry_point hex, bits, endian, section_names
    (header order, NULL section skipped), sections [{name, type, flags, offset, size}], programs (non-empty
    SHF_EXECINSTR PROGBITS sections except .text = libbpf's SEC() names, e.g. "xdp", "kprobe/do_sys_openat2"),
    program_names (the GLOBAL FUNC symbols defined in them, program order), license (the `license` section string),
    maps (OBJECT symbols in `.maps` (BTF-defined) then legacy `maps`), has_btf (.BTF section)}."""
    if data[:4] != b"\x7fELF" or data[4:5] not in (b"\x01", b"\x02") or data[5:6] not in (b"\x01", b"\x02"):
        return None
    b64, E = data[4] == 2, "<" if data[5] == 1 else ">"
    u16 = lambda o: struct.unpack_from(E + "H", data, o)[0]
    u32 = lambda o: struct.unpack_from(E + "I", data, o)[0]
    uw = (lambda o: struct.unpack_from(E + "Q", data, o)[0]) if b64 else u32
    if len(data) < (64 if b64 else 52) or u16(18) != 247:
        return None
    et, entry = u16(16), uw(24)
    shoff = uw(40) if b64 else u32(32)
    p = 52 if b64 else 40
    shes, shnum, shstr = u16(p + 6), u16(p + 8), u16(p + 10)
    if not shoff or shes < (64 if b64 else 40) or not 0 < shnum <= 4096 or shoff + shes * shnum > len(data):
        return None
    raw = []   # (name_off, type, flags, offset, size, link, info, entsize)
    for k in range(shnum):
        o = shoff + k * shes
        if b64:
            raw.append((u32(o), u32(o + 4), uw(o + 8), uw(o + 24), uw(o + 32), u32(o + 40), u32(o + 44), uw(o + 56)))
        else:
            raw.append((u32(o), u32(o + 4), u32(o + 8), u32(o + 16), u32(o + 20), u32(o + 24), u32(o + 28),
                        u32(o + 36)))

    def cstr(i, off):
        if not 0 <= i < len(raw) or raw[i][1] == 8:
            return ""
        s = raw[i][3] + off
        e = data.find(b"\0", s, s + 4096)
        return bytes(data[s:e]).decode("utf-8", "replace") if s < len(data) and e >= s else ""

    names = [cstr(shstr, r[0]) for r in raw]
    progs = [i for i, r in enumerate(raw) if r[1] == 1 and r[2] & 4 and r[4] and names[i] != ".text"]
    pnames, maps = {i: [] for i in progs}, {}
    mapsec = [i for n in (".maps", "maps") for i, m in enumerate(names) if m == n]
    for t, off, size, link, ent in ((r[1], r[3], r[4], r[5], r[7]) for r in raw):
        if t != 2 or not ent:   # SHT_SYMTAB
            continue
        for k in range(1, min(size // ent, 50000)):
            o = off + k * ent
            if o + ent > len(data):
                break
            nm, info, shndx = (u32(o), data[o + 4], u16(o + 6)) if b64 else (u32(o), data[o + 12], u16(o + 14))
            if shndx in pnames and info & 15 == 2 and info >> 4 == 1:
                pnames[shndx].append(cstr(link, nm))
            elif shndx in mapsec and info & 15 == 1:
                maps.setdefault(shndx, []).append(cstr(link, nm))
        break
    lic = next((bytes(data[r[3]:r[3] + r[4]]).split(b"\0")[0].decode("utf-8", "replace")
                for r, n in zip(raw, names) if n == "license" and r[1] != 8), None)
    return {"format": "elf", "elf_type": ELF_TYPE_NAME.get(et, str(et)), "machine": "Linux BPF",
            "machine_num": "247", "entry_point": hex(entry), "bits": 64 if b64 else 32,
            "endian": "little" if E == "<" else "big", "section_names": names[1:],
            "sections": [{"name": n, "type": r[1], "flags": r[2], "offset": r[3], "size": r[4]}
                         for n, r in zip(names[1:], raw[1:])],
            "programs": [names[i] for i in progs], "program_names": [x for i in progs for x in pnames[i] if x],
            "license": lic, "maps": [x for i in mapsec for x in maps.get(i, []) if x],
            "has_btf": ".BTF" in names}


def bpf_fields(data):
    """Flat answer-field candidates for an eBPF object (None if not EM_BPF). Lists in header order (render as JSON);
    absent singletons "none". program_types = the SEC() prefix before the first '/' (xdp, kprobe, tracepoint, ...).
    hcfg_offset = FILE offset of the 'H' of the first crc-valid raw blob inside a section (= hcfg_scan raw offset),
    hcfg_section = that section's name (".hcfg", ".rodata", ...), hcfg_section_offset = the blob's offset inside it;
    has_hcfg_section = a section named hcfg/.hcfg exists. Field names other than format/elf_type/machine/entry_point
    are SPECULATIVE (GM vocabulary for BPF not seen)."""
    try:
        lay = bpf_layout(data)
    except (struct.error, IndexError, ValueError, TypeError):   # truncated / hostile header: cannot answer
        return None
    if not lay:
        return None

    def nz(v):
        return "none" if v is None or v == [] else v

    hc = {}
    for s in lay["sections"]:
        if s["type"] == 8 or hc:
            continue
        lo, e = s["offset"], s["offset"] + s["size"]
        seg = bytes(data[lo:e])
        i = seg.find(HCFG_MAGIC)
        while i >= 0 and not hc:
            blob = seg[i:]
            r = _parse_blob(blob[:_need(blob[:8])]) if len(blob) >= 12 else None
            if r and r[5]:
                hc = {"hcfg_offset": lo + i, "hcfg_section": s["name"], "hcfg_section_offset": i}
            i = seg.find(HCFG_MAGIC, i + 1)
    out = {k: lay[k] for k in ("format", "elf_type", "machine", "machine_num", "entry_point", "bits", "endian")}
    out.update({
        "section_names": lay["section_names"], "section_count": len(lay["section_names"]),
        "programs": nz(lay["programs"]), "program_count": len(lay["programs"]),
        "program_types": nz(list(dict.fromkeys(p.split("/")[0] for p in lay["programs"]))),
        "program_names": nz(lay["program_names"]), "license": nz(lay["license"]),
        "maps": nz(lay["maps"]), "map_count": len(lay["maps"]), "has_btf": lay["has_btf"],
        "has_hcfg_section": any(n.lower().lstrip(".") == "hcfg" for n in lay["section_names"]),
        "hcfg_offset": hc.get("hcfg_offset", "none"), "hcfg_section": hc.get("hcfg_section", "none"),
        "hcfg_section_offset": hc.get("hcfg_section_offset", "none")})
    return out


def bpf_field(data, name):
    """One bpf_fields value; "none" when the input is not an eBPF object or the field is unknown/absent."""
    try:
        return (bpf_fields(data) or {}).get(name, "none")
    except Exception:  # noqa: BLE001 -- untrusted bytes: never raise past the field
        return "none"

def elf_header_facts(data, hcfg=True):
    """ELF facts from the raw header structs only, for sstrip'd / corrupted images that make pyelftools / readelf -S
    fail (e_shnum 0, e_shoff past EOF, garbage e_shstrndx, renamed sections). None if the 52/64-byte ELF header is not
    all there. Header fields always come from the ELF header: format, elf_class ELF32/ELF64 (+ elf_class_int),
    endianness little/big, machine label (+ machine_num / machine_int decimal), elf_type ET_*, entry_point hex,
    program_header_count, has_interp. Section table: has_section_headers "true" only when e_shoff/e_shentsize/e_shnum
    describe a table inside the file (SHN_UNDEF count / SHN_XINDEX index read from section 0); section_names = header
    order, NULL section skipped, [] when there is no table OR no usable name table (e_shstrndx out of range / not
    SHT_STRTAB / past EOF: readelf's "<no-strings>"); section_count = table entries minus the NULL one; has_symtab =
    an SHT_SYMTAB section (by type, like readelf -S); has_hcfg_section = a section literally named hcfg/.hcfg (a renamed
    impostor counts; the blob need not be in it). hcfg_* = the first crc-valid blob of hcfg_find (raw scan over the
    whole file, independent of sections): hcfg_offset, hcfg_encoding, hcfg_config, hcfg_section = the named section
    whose file range holds it ("none" without names); hcfg=False skips that scan (header fields only). Never raises on
    malformed input."""
    try:
        if data[:4] != b"\x7fELF" or data[4:5] not in (b"\x01", b"\x02") or data[5:6] not in (b"\x01", b"\x02"):
            return None
        b64, E = data[4] == 2, "<" if data[5] == 1 else ">"
        if len(data) < (64 if b64 else 52):
            return None
        u16 = lambda o: struct.unpack_from(E + "H", data, o)[0]
        u32 = lambda o: struct.unpack_from(E + "I", data, o)[0]
        uw = (lambda o: struct.unpack_from(E + "Q", data, o)[0]) if b64 else u32
        et, m, entry = u16(16), u16(18), uw(24)
        phoff, shoff = (uw(32), uw(40)) if b64 else (u32(28), u32(32))
        p = 52 if b64 else 40
        phes, phn, shes, shn, shstr = u16(p + 2), u16(p + 4), u16(p + 6), u16(p + 8), u16(p + 10)
        ptypes = []
        if phoff and phes >= (56 if b64 else 32):
            for k in range(min(phn, 4096)):
                o = phoff + k * phes
                if o + phes > len(data):
                    break
                ptypes.append(u32(o))
        sw = 64 if b64 else 40
        secs = []   # (name_off, type, offset, size)

        def sec(o):
            return (u32(o), u32(o + 4), uw(o + 24), uw(o + 32)) if b64 else (u32(o), u32(o + 4), u32(o + 16),
                                                                               u32(o + 20))
        if shoff and shes >= sw and shoff + shes <= len(data):
            s0 = sec(shoff)
            n = shn or s0[3]                                  # e_shnum 0 + table: real count in section 0 sh_size
            if shstr == 0xffff:                               # SHN_XINDEX: real index in section 0 sh_link
                shstr = u32(shoff + (40 if b64 else 24))
            if 0 < n <= 65535 and shoff + n * shes <= len(data):
                secs = [sec(shoff + k * shes) for k in range(n)]
        names = []
        if secs and 0 < shstr < len(secs) and secs[shstr][1] == 3 and secs[shstr][2] + secs[shstr][3] <= len(data):
            so, sn = secs[shstr][2], secs[shstr][3]
            tab = bytes(data[so:so + sn])
            names = [tab[s[0]:tab.find(b"\0", s[0]) if tab.find(b"\0", s[0]) >= 0 else sn].decode("utf-8", "replace")
                     if s[0] < sn else "" for s in secs[1:]]
        hit = hcfg_find(data) if hcfg else None
        hsec = "none"
        if hit is not None and names:
            hsec = next((nm for nm, s in zip(names, secs[1:]) if s[1] != 8 and s[2] <= hit.offset < s[2] + s[3]),
                        "none")
        cls = "ELF64" if b64 else "ELF32"
        return {"format": "elf", "elf_class": cls, "elf_class_int": "64" if b64 else "32", "bits": 64 if b64 else 32,
                "endianness": "little" if E == "<" else "big", "endian": "little" if E == "<" else "big",
                "machine": ELF_MACHINE_LABEL.get(m, str(m)), "machine_num": str(m), "machine_int": str(m),
                "elf_type": ELF_TYPE_NAME.get(et, str(et)), "entry_point": hex(entry),
                "program_header_count": len(ptypes), "has_interp": "true" if 3 in ptypes else "false",
                "has_section_headers": "true" if secs else "false", "section_count": max(len(secs) - 1, 0),
                "section_names": names, "has_symtab": "true" if any(s[1] == 2 for s in secs) else "false",
                "has_hcfg_section": "true" if any(x.lower().lstrip(".") == "hcfg" for x in names) else "false",
                "hcfg_offset": hit.offset if hit else "none", "hcfg_encoding": hit.encoding if hit else "none",
                "hcfg_config": hit.config if hit else "none", "hcfg_section": hsec}
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def elf_header_field(data, name):
    """One elf_header_facts value; "none" when the input is no (complete-header) ELF or the field is unknown."""
    try:
        return (elf_header_facts(data, hcfg=name.startswith("hcfg")) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


PE_SUBSYSTEM = {1: ("native", "IMAGE_SUBSYSTEM_NATIVE"), 2: ("gui", "IMAGE_SUBSYSTEM_WINDOWS_GUI"),
                3: ("console", "IMAGE_SUBSYSTEM_WINDOWS_CUI"), 5: ("os2_console", "IMAGE_SUBSYSTEM_OS2_CUI"),
                7: ("posix_console", "IMAGE_SUBSYSTEM_POSIX_CUI"), 9: ("wince_gui", "IMAGE_SUBSYSTEM_WINDOWS_CE_GUI"),
                10: ("efi_application", "IMAGE_SUBSYSTEM_EFI_APPLICATION"),
                11: ("efi_boot_service_driver", "IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER"),
                12: ("efi_runtime_driver", "IMAGE_SUBSYSTEM_EFI_RUNTIME_DRIVER"), 13: ("efi_rom", "IMAGE_SUBSYSTEM_EFI_ROM"),
                14: ("xbox", "IMAGE_SUBSYSTEM_XBOX"), 16: ("windows_boot_application",
                                                         "IMAGE_SUBSYSTEM_WINDOWS_BOOT_APPLICATION")}
PE_FILE_CHAR = {0x1: "RELOCS_STRIPPED", 0x2: "EXECUTABLE_IMAGE", 0x4: "LINE_NUMS_STRIPPED", 0x8: "LOCAL_SYMS_STRIPPED",
                0x10: "AGGRESIVE_WS_TRIM", 0x20: "LARGE_ADDRESS_AWARE", 0x80: "BYTES_REVERSED_LO", 0x100: "32BIT_MACHINE",
                0x200: "DEBUG_STRIPPED", 0x400: "REMOVABLE_RUN_FROM_SWAP", 0x800: "NET_RUN_FROM_SWAP", 0x1000: "SYSTEM",
                0x2000: "DLL", 0x4000: "UP_SYSTEM_ONLY", 0x8000: "BYTES_REVERSED_HI"}   # IMAGE_FILE_* (pefile names)
PE_DLL_CHAR = {0x20: "HIGH_ENTROPY_VA", 0x40: "DYNAMIC_BASE", 0x80: "FORCE_INTEGRITY", 0x100: "NX_COMPAT",
               0x200: "NO_ISOLATION", 0x400: "NO_SEH", 0x800: "NO_BIND", 0x1000: "APPCONTAINER", 0x2000: "WDM_DRIVER",
               0x4000: "GUARD_CF", 0x8000: "TERMINAL_SERVER_AWARE"}   # IMAGE_DLLCHARACTERISTICS_* (pefile names)


def pe_header_facts(data):
    """PE/COFF facts from the raw MZ/PE/optional/section headers (no pefile; MinGW, Go, Zig, .NET, MSVC alike), the
    PE counterpart of elf_header_facts. None if the DOS header / PE signature / COFF header / optional-header magic is
    not there. format "pe", pe_type PE32/PE32+ (+ bits), machine (PE_MACHINE_LABEL) / machine_num (decimal) /
    machine_hex, entry_point = hex(ImageBase + AddressOfEntryPoint) (+ entry_rva hex, entry_point_int decimal),
    image_base hex (+ image_base_int), timestamp = TimeDateStamp decimal (+ timestamp_hex), characteristics /
    dll_characteristics hex (+ *_int decimal, *_flags = pefile-style IMAGE_FILE_* / IMAGE_DLLCHARACTERISTICS_* names in
    bit order), subsystem short label console/gui/native/efi_* (+ subsystem_const IMAGE_SUBSYSTEM_*, subsystem_int
    decimal), is_dll, section_names (header order, NUL-trimmed, "/N" long names resolved through the COFF string table
    like objdump/pefile do), section_count, has_symtab ("true" when PointerToSymbolTable and NumberOfSymbols are set;
    Go/MinGW keep one, MSVC/.NET/stripped don't) + number_of_symbols, size_of_image / checksum / linker_version /
    os_version / subsystem_version, is_dotnet (CLR data directory), import_dlls (import-directory order). Never raises."""
    try:
        if data[:2] != b"MZ" or len(data) < 0x40:
            return None
        pe = int.from_bytes(data[0x3c:0x40], "little")
        if data[pe:pe + 4] != b"PE\0\0" or len(data) < pe + 26:
            return None
        m, nsec, ts, symp, nsym, optsz, ch = struct.unpack_from("<HHIIIHH", data, pe + 4)
        opt = pe + 24
        magic = struct.unpack_from("<H", data, opt)[0]
        if magic not in (0x10b, 0x20b) or len(data) < opt + (112 if magic == 0x20b else 96):
            return None
        p64 = magic == 0x20b
        lmaj, lmin = data[opt + 2], data[opt + 3]
        aep = struct.unpack_from("<I", data, opt + 16)[0]
        base = struct.unpack_from("<Q", data, opt + 24)[0] if p64 else struct.unpack_from("<I", data, opt + 28)[0]
        osmaj, osmin, _, _, ssmaj, ssmin = struct.unpack_from("<6H", data, opt + 40)
        soi, _, csum, sub, dch = struct.unpack_from("<IIIHH", data, opt + 56)
        strtab = symp + 18 * nsym if symp and nsym else 0

        def secname(raw):
            nm = raw.split(b"\0", 1)[0]
            if nm[:1] == b"/" and nm[1:].isdigit() and strtab and strtab + int(nm[1:]) < len(data):
                o = strtab + int(nm[1:])
                e = data.find(b"\0", o, o + 4096)
                nm = bytes(data[o:e if e >= 0 else o + 4096])
            return nm.decode("utf-8", "replace")
        secs = []   # (name, va, vsize, raw_ptr, raw_size)
        for k in range(min(nsec, 96)):
            o = opt + optsz + 40 * k
            if o + 40 > len(data):
                break
            vsize, va, rsize, rptr = struct.unpack_from("<IIII", data, o + 8)
            secs.append((secname(bytes(data[o:o + 8])), va, vsize, rptr, rsize))
        dd = opt + (112 if p64 else 96)
        ndd = min(16, struct.unpack_from("<I", data, dd - 4)[0])
        dirs = [struct.unpack_from("<II", data, dd + 8 * k) for k in range(ndd)
                if dd + 8 * k + 8 <= min(opt + optsz, len(data))]
        dlls = []
        if len(dirs) > 1 and dirs[1][0]:
            o = _pe_rva(secs, dirs[1][0])
            while o is not None and o + 20 <= len(data) and len(dlls) < 4096:
                ilt, _, _, nrva, iat = struct.unpack_from("<5I", data, o)
                if not (ilt or nrva or iat):
                    break
                no = _pe_rva(secs, nrva)
                if no is None or no >= len(data):
                    break
                e = data.find(b"\0", no, no + 512)
                dlls.append(bytes(data[no:e if e >= 0 else no + 512]).decode("utf-8", "replace"))
                o += 20
        sl, sc = PE_SUBSYSTEM.get(sub, (str(sub), str(sub)))
        flags = lambda v, tab, pre: [pre + n for b, n in sorted(tab.items()) if v & b]
        return {"format": "pe", "pe_type": "PE32+" if p64 else "PE32", "bits": 64 if p64 else 32,
                "machine": PE_MACHINE_LABEL.get(m, f"0x{m:x}"), "machine_num": str(m), "machine_hex": f"0x{m:x}",
                "entry_point": hex(base + aep), "entry_point_int": str(base + aep), "entry_rva": hex(aep),
                "image_base": hex(base), "image_base_int": str(base), "timestamp": str(ts), "timestamp_hex": hex(ts),
                "characteristics": hex(ch), "characteristics_int": str(ch),
                "characteristics_flags": flags(ch, PE_FILE_CHAR, "IMAGE_FILE_"),
                "dll_characteristics": hex(dch), "dll_characteristics_int": str(dch),
                "dll_characteristics_flags": flags(dch, PE_DLL_CHAR, "IMAGE_DLLCHARACTERISTICS_"),
                "subsystem": sl, "subsystem_const": sc, "subsystem_int": str(sub),
                "is_dll": "true" if ch & 0x2000 else "false", "section_names": [s[0] for s in secs],
                "section_count": len(secs), "has_symtab": "true" if symp and nsym else "false",
                "number_of_symbols": nsym, "size_of_image": hex(soi), "checksum": hex(csum),
                "linker_version": f"{lmaj}.{lmin}", "os_version": f"{osmaj}.{osmin}",
                "subsystem_version": f"{ssmaj}.{ssmin}",
                "is_dotnet": "true" if len(dirs) > 14 and dirs[14][0] else "false", "import_dlls": dlls}
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def pe_header_field(data, name):
    """One pe_header_facts value; "none" when the input is no (complete-header) PE or the field is unknown."""
    try:
        return (pe_header_facts(data) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


def header_field(data, name):
    """elf_header_field for ELF input, pe_header_field for PE input, else "none" (same field names where shared:
    format, machine, machine_num, bits, entry_point, section_names, section_count, has_symtab)."""
    try:
        if data[:2] == b"MZ":
            return pe_header_field(data, name)
        return elf_header_field(data, name)
    except Exception:  # noqa: BLE001
        return "none"


_WASM_MEMARG = set(range(0x28, 0x3f))            # loads/stores: memarg (align [+memidx], offset)
_WASM_STORE = {0x36: 4, 0x37: 8, 0x38: 4, 0x39: 8, 0x3a: 1, 0x3b: 2, 0x3c: 1, 0x3d: 2, 0x3e: 4}
_WASM_LEB1 = {0x0c, 0x0d, 0x10, 0x12, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x3f, 0x40, 0xd2, 0xd0}
_WASM_LEB2 = {0x11, 0x13}
_WASM_FC = {8: 2, 9: 1, 10: 2, 11: 1, 12: 2, 13: 1, 14: 2, 15: 1, 16: 1, 17: 1}   # 0xfc sub-op -> LEB immediates


def wasm_memory_writes(data, lay=None, max_ops=500_000):
    """What instantiating + running the module's const-address code would put in linear memory, WITHOUT executing it:
    [(mem_addr, bytes, file_offset, kind)] in application order. kind "segment" = an active data segment at a constant
    offset (file_offset = its first payload byte); "init" = a passive segment copied by `i32.const dst; i32.const src;
    i32.const n; memory.init seg` (file_offset = the copied segment byte); "store" = `<const addr>; <const imm>;
    iNN.store[8/16/32] offset=k` (file_offset = the address const's opcode). A tiny const-only stack tracker over
    every function body: any non-const op forgets the tracked consts (no locals/globals/branches are modeled)."""
    lay = lay or wasm_layout(data)
    if not lay:
        return []
    segs = lay["data_segments"]
    out = [(s["mem_offset"], bytes(data[s["file_offset"]:s["file_offset"] + s["size"]]), s["file_offset"], "segment")
           for s in segs if s["mode"] == "active" and s["mem_offset"] is not None and s["size"]]
    code = next((s for s in lay["sections"] if s["id"] == 10), None)
    if not code:
        return out
    ops = 0
    try:
        n, p = _leb(data, code["offset"], cap=5)
        for _ in range(n):
            sz, p = _leb(data, p, cap=5)
            fe = p + sz
            nl, q = _leb(data, p, cap=5)
            for _l in range(nl):
                q = _leb(data, q, cap=5)[1] + 1
            st = []   # (value, opcode file offset) of the consecutive consts just pushed
            while q < fe and ops < max_ops:
                ops += 1
                op, at = data[q], q
                q += 1
                if op in (0x41, 0x42):
                    v, q = _leb(data, q, signed=True)
                    st.append((v & ((1 << (32 if op == 0x41 else 64)) - 1), at))
                    continue
                if op in _WASM_MEMARG:
                    al, q = _leb(data, q, cap=5)
                    if al & 0x40:
                        q = _leb(data, q, cap=5)[1]
                    mo, q = _leb(data, q)
                    w = _WASM_STORE.get(op)
                    if w and len(st) >= 2:
                        (a, aat), (v, _) = st[-2], st[-1]
                        out.append((a + mo, (v & ((1 << 8 * w) - 1)).to_bytes(w, "little"), aat, "store"))
                elif op in _WASM_LEB1:
                    q = _leb(data, q)[1]
                elif op in _WASM_LEB2:
                    q = _leb(data, _leb(data, q)[1])[1]
                elif op in (0x02, 0x03, 0x04):
                    q = _leb(data, q, signed=True, cap=5)[1]
                elif op == 0x0e:
                    k, q = _leb(data, q, cap=5)
                    for _b in range(k + 1):
                        q = _leb(data, q, cap=5)[1]
                elif op == 0x1c:
                    k, q = _leb(data, q, cap=5)
                    q += k
                elif op == 0x43:
                    q += 4
                elif op == 0x44:
                    q += 8
                elif op == 0xfc:
                    sub, q = _leb(data, q, cap=5)
                    imm = []
                    for _b in range(_WASM_FC.get(sub, 0) if sub <= 17 else -1):
                        v, q = _leb(data, q)
                        imm.append(v)
                    if sub > 17:
                        break
                    if sub == 8 and len(st) >= 3 and imm[0] < len(segs):   # memory.init seg: dst src n
                        s, d, src, ln = segs[imm[0]], st[-3][0], st[-2][0], st[-1][0]
                        if src + ln <= s["size"] and ln:
                            fo = s["file_offset"] + src
                            out.append((d, bytes(data[fo:fo + ln]), fo, "init"))
                elif not (op in (0x00, 0x01, 0x05, 0x0b, 0x0f, 0x1a, 0x1b, 0xd1) or 0x45 <= op <= 0xc4):
                    break   # SIMD/atomics/GC/unknown: stop this body (immediates not modeled)
                st = []
            p = fe
    except (IndexError, ValueError):
        pass
    return out


def wasm_memory_runs(data, lay=None, max_bytes=64 << 20):
    """The reassembled linear-memory image as contiguous runs [(base_addr, bytes, writes)] (writes = the
    wasm_memory_writes entries that built the run, application order: later writes win). Runs touching/adjacent
    writes are merged, so a blob split over adjacent segments or built by stores reads back contiguous."""
    ws = [w for w in wasm_memory_writes(data, lay) if w[1]]
    if sum(len(w[1]) for w in ws) > max_bytes:
        return []
    runs, cur = [], None
    for w in sorted(ws, key=lambda w: w[0]):
        if cur and w[0] <= cur[1]:
            cur[1] = max(cur[1], w[0] + len(w[1]))
            cur[2].append(w)
        else:
            cur = [w[0], w[0] + len(w[1]), [w]]
            runs.append(cur)
    out = []
    for lo, hi, mem in runs:
        mem.sort(key=ws.index) if len(mem) > 1 else None
        img = bytearray(hi - lo)
        for a, b, _fo, _k in mem:
            img[a - lo:a - lo + len(b)] = b
        out.append((lo, bytes(img), mem))
    return out


def _wasm_mem_src(writes, addr):
    """(file offset, kind) of the byte at linear-memory `addr` per the last write covering it."""
    for a, b, fo, k in reversed(writes):
        if a <= addr < a + len(b):
            return (fo + addr - a if k != "store" else fo), k
    return None, None


def _wasm_mem_scan(data, emit, deadline, _depth):
    """hcfg_scan pass for wasm: a blob not contiguous in the file (split over adjacent active segments, a passive
    segment placed by memory.init next to another, or built by const stores in code) -> scan every COMPOSITE run of the
    reassembled linear memory. Encoding wasm-<split|init|store>-<inner>; offset = the file byte that the blob's first
    stored byte came from (store: the address i32.const opcode); detail mem=<linear address>."""
    for lo, img, ws in wasm_memory_runs(data):
        if len(ws) < 2 or len(img) > 8 << 20:
            continue   # a single-source run is already plain bytes in the file
        for h in hcfg_scan(img, deadline=deadline, stop_on_valid=True, _depth=_depth + 1):
            if h.valid:
                fo, k = _wasm_mem_src(ws, lo + h.offset)
                if fo is not None:
                    kind = {"segment": "split"}.get(k, k)
                    emit(fo, f"wasm-{kind}-{h.encoding}", struct.pack("<4sBBHI", HCFG_MAGIC, h.version, h.key, h.length, h.crc) +
                         bytes(c ^ h.key for c in h.plain), (f"mem={lo + h.offset} " + h.detail).strip())
                return


# ------------------------------------------------------------------ LLVM bitcode string constants
_BC_MAGIC = b"BC\xc0\xde"
_BC_WRAPPER = b"\xde\xc0\x17\x0b"   # 0x0B17C0DE LE: {magic, version, offset, size, cputype} then the raw bitcode
_BC_CHAR6 = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._"
_BC_ENTER = {0, 8, 11}   # BLOCKINFO, MODULE, module-level CONSTANTS (global strings): every other block skipped by length


def bitcode_strings(data, start=0, max_ops=2_000_000):
    """[(bit offset of the first element, bytes, element bit width or None for vbr)] of every i8 string constant (CST_CODE_STRING 8 / CSTRING 9 / DATA 22
    with all elements < 256) in the LLVM bitstream at data[start:] ('BC' 0xC0DE magic). Pure Python LLVM bitstream
    reader (abbrevs + BLOCKINFO); [] if it does not parse. Bit offsets are absolute in `data`."""
    out = []
    n_bits = len(data) * 8
    pos = [start * 8 + 32]
    budget = [max_ops]

    def rd(w):
        p = pos[0]
        if w == 0:
            return 0
        if p + w > n_bits:
            raise IndexError
        pos[0] = p + w
        return (int.from_bytes(data[p >> 3:(p + w + 7 >> 3) + 1], "little") >> (p & 7)) & ((1 << w) - 1)

    def vbr(w):
        hi, v, s = 1 << (w - 1), 0, 0
        while True:
            c = rd(w)
            v |= (c & (hi - 1)) << s
            if not c & hi:
                return v
            s += w - 1
            if s > 64:
                raise ValueError

    def align():
        pos[0] = (pos[0] + 31) & ~31

    def scalar(op):
        kind, w = op
        return rd(w) if kind == 1 else vbr(w) if kind == 2 else _BC_CHAR6[rd(6)] if kind == 4 else None

    blockinfo = {}

    def block(bid, width, end):
        abbrevs = list(blockinfo.get(bid, ()))
        cur = None   # BLOCKINFO SETBID target
        while pos[0] < end:
            budget[0] -= 1
            if budget[0] < 0:
                raise ValueError
            a = rd(width)
            if a == 0:
                align()
                return
            if a == 1:
                sub, w2 = vbr(8), vbr(4)
                align()
                n = rd(32)
                e2 = pos[0] + 32 * n
                if e2 > n_bits or not w2:
                    raise ValueError
                if sub in _BC_ENTER:
                    block(sub, w2, e2)
                pos[0] = e2
                continue
            if a == 2:
                ops = []
                for _ in range(vbr(5)):
                    if rd(1):
                        ops.append((0, vbr(8)))
                    else:
                        k = rd(3)
                        if k not in (1, 2, 3, 4, 5):
                            raise ValueError
                        ops.append((k, vbr(5) if k in (1, 2) else 0))
                (blockinfo.setdefault(cur, []) if bid == 0 else abbrevs).append(ops)
                continue
            first, ew = None, None
            if a == 3:
                code, n = vbr(6), vbr(6)
                first = pos[0]
                vals = [vbr(6) for _ in range(n)]
            else:
                if a - 4 >= len(abbrevs):
                    raise ValueError
                ops, vals, i = abbrevs[a - 4], [], 0
                while i < len(ops):
                    kind, v = ops[i]
                    if kind == 0:
                        vals.append(v)
                    elif kind == 3:
                        n, el = vbr(6), ops[i + 1]
                        first, ew = pos[0], {0: 0, 1: el[1], 4: 6}.get(el[0])
                        vals.extend(el[1] if el[0] == 0 else scalar(el) for _ in range(n))
                        budget[0] -= n
                        i += 1
                    elif kind == 5:
                        n = vbr(6)
                        align()
                        first, ew = pos[0], 8
                        vals.extend(data[pos[0] >> 3:(pos[0] >> 3) + n])
                        pos[0] += 8 * n
                        align()
                    else:
                        vals.append(scalar(ops[i]))
                    i += 1
                code, vals = vals[0], vals[1:]
            if bid == 0 and code == 1 and vals:
                cur = vals[0]
            elif bid == 11 and code in (8, 9, 22) and vals and all(0 <= c < 256 for c in vals):
                out.append((first if first is not None else pos[0], bytes(vals), ew))

    try:
        while pos[0] + 36 <= n_bits:
            if rd(2) != 1:
                break
            sub, w2 = vbr(8), vbr(4)
            align()
            n = rd(32)
            e2 = pos[0] + 32 * n
            if e2 > n_bits or not w2:
                break
            if sub in _BC_ENTER:
                block(sub, w2, e2)
            pos[0] = e2
    except (IndexError, ValueError, TypeError, RecursionError):
        pass
    return out


def _bitcode_scan(data, emit, deadline, _depth):
    """hcfg_scan pass for LLVM bitcode (raw 'BC' 0xC0DE, the 0x0B17C0DE wrapper, or an embedded .llvmbc copy):
    decode every i8 string constant and scan them. Encoding bitcode-<inner> (bitcode-raw = the blob bytes are the
    string); offset (SPECULATIVE) = the file byte holding the first bit of the blob's first stored element."""
    i, n = data.find(_BC_MAGIC), 0
    while i >= 0 and n < 8:
        strs = bitcode_strings(data, i)
        if strs:
            buf, marks, p = bytearray(), [], 0
            for bit, s, w in strs:
                marks.append((p, bit, w))
                buf += s + b"\n"
                p += len(s) + 1
            for h in hcfg_scan(bytes(buf), deadline=deadline, stop_on_valid=True, _depth=_depth + 1):
                if h.valid:
                    for p0, bit, w in reversed(marks):
                        if p0 <= h.offset:
                            break
                    # fixed-width elements (Fixed 8/7, char6, blob 8): exact; vbr6: the string's first element
                    emit((bit + (h.offset - p0) * (w or 0)) // 8, f"bitcode-{h.encoding}",
                         struct.pack("<4sBBHI", HCFG_MAGIC, h.version, h.key, h.length, h.crc) +
                         bytes(c ^ h.key for c in h.plain), (f"str+{h.offset - p0} " + h.detail).strip())
                    return
        i, n = data.find(_BC_MAGIC, i + 4), n + 1


# --- robust constant recovery (replaces the fragile b8..c3 regex) --------------------------------
def recover_return_constants(data, max_funcs=400):
    """Find functions that return an immediate constant, via capstone linear disassembly from the ELF's
    symbol/section entry points — robust where the old `\\xb8(.{4})\\xc3` whole-.text regex went ambiguous.
    Returns {addr: const} for `mov eax/rax, imm; ret` leaves. Works stripped (scans .text) and unstripped."""
    try:
        import capstone
        from elftools.elf.elffile import ELFFile
    except ImportError:
        return {}
    try:
        elf = ELFFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001
        return {}
    text = elf.get_section_by_name(".text")
    if not text:
        return {}
    code, base = text.data(), text["sh_addr"]
    bits = 64 if elf.elfclass == 64 else 32
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64 if bits == 64 else capstone.CS_MODE_32)
    out = {}
    last_imm = None
    last_addr = None
    for ins in md.disasm(code, base):
        if ins.mnemonic == "mov" and ins.op_str.split(",")[0].strip() in ("eax", "rax", "al", "ax"):
            m = re.search(r",\s*(?:0x[0-9a-fA-F]+|\d+)$", ins.op_str)
            if m:
                last_imm = int(m.group(0).lstrip(", ").strip(), 0)
                last_addr = ins.address
        elif ins.mnemonic == "ret" and last_imm is not None and last_addr is not None:
            out[hex(last_addr)] = last_imm
            last_imm = last_addr = None
            if len(out) >= max_funcs:
                break
        elif ins.mnemonic not in ("nop",):
            # only a mov-imm immediately followed by ret counts as a return-constant leaf
            if ins.mnemonic != "mov":
                last_imm = last_addr = None
    return out


_EMU_RELATIVE = {62: 8, 183: 1027, 3: 8}   # e_machine -> R_*_RELATIVE (x86-64, AArch64, i386 REL)


def emulate_return_value(data, symbol="recover_code", *, signed=False, max_insns=200_000, timeout_ms=300):
    """Return value of ELF function `symbol` (FUNC symbol name or vaddr int) by emulation, for computed returns that
    are not a `mov eax, imm; ret` leaf (xor of immediates, table lookup, flattened switch, internal helper calls).
    unicorn x86-64 / i386 / AArch64: PT_LOADs mapped at their vaddrs (ET_DYN rebased, R_*_RELATIVE applied), scratch
    stack, return address = sentinel page; eax / w0 at the sentinel (unsigned 32-bit unless signed=True).
    -> int; "none" if the ELF has no such FUNC symbol; None if not an ELF / unsupported arch / refused (syscall,
    int/svc, call through the PLT or an unrelocated GOT slot into libc, fetch outside an executable segment,
    instruction cap or timeout)."""
    try:
        import unicorn as U
        from elftools.elf.elffile import ELFFile
    except ImportError:
        return None
    try:
        elf = ELFFile(io.BytesIO(data))
        mach = elf["e_machine"]
        mach = {"EM_X86_64": 62, "EM_AARCH64": 183, "EM_386": 3}.get(mach, mach)
        if mach not in _EMU_RELATIVE or (mach == 3) != (elf.elfclass == 32):
            return None
        e = "<" if elf.little_endian else ">"
        b64 = elf.elfclass == 64
        secs = list(elf.iter_sections())
        if isinstance(symbol, int):
            addr = symbol
        else:
            addr, want = None, symbol.encode()
            for sec in secs:   # raw structs: pyelftools symbol iteration is seconds on a 50k-symbol Go/Rust binary
                if sec["sh_type"] not in ("SHT_SYMTAB", "SHT_DYNSYM") or addr is not None:
                    continue
                strs = secs[sec["sh_link"]].data() if 0 <= sec["sh_link"] < len(secs) else b""
                hits, i = set(), strs.find(b"\0" + want + b"\0")
                while i >= 0:
                    hits.add(i + 1)
                    i = strs.find(b"\0" + want + b"\0", i + 1)
                if strs.startswith(want + b"\0"):
                    hits.add(0)
                if not hits:
                    continue
                fmt, ent = (e + "IBxHQQ", 24) if b64 else (e + "IIIBxH", 16)
                raw = sec.data()
                for t in struct.iter_unpack(fmt, raw[:len(raw) // ent * ent]):
                    nm, val, info, shndx = (t[0], t[3], t[1], t[2]) if b64 else (t[0], t[1], t[3], t[4])
                    if nm in hits and info & 0xF == 2 and val and shndx:
                        addr = val
                        break
            if addr is None:
                return "none"
        base = 0x10000000 if elf["e_type"] == "ET_DYN" else 0
        pages = {}   # page -> prot
        loads = []
        for seg in elf.iter_segments():
            if seg["p_type"] != "PT_LOAD" or not seg["p_memsz"]:
                continue
            va, msz = seg["p_vaddr"] + base, seg["p_memsz"]
            if msz > 64 << 20:
                return None
            prot = U.UC_PROT_READ | U.UC_PROT_WRITE | (U.UC_PROT_EXEC if seg["p_flags"] & 1 else 0)
            for p in range(va & ~0xfff, (va + msz + 0xfff) & ~0xfff, 0x1000):
                pages[p] = pages.get(p, 0) | prot
            off, fsz = seg["p_offset"], min(seg["p_filesz"], max(0, len(data) - seg["p_offset"]))
            loads.append((va, data[off:off + fsz]))
        if not pages or len(pages) > 32768:
            return None
        rel_type = _EMU_RELATIVE[mach]
        rels = []
        if base:
            for sec in secs:
                rela = sec["sh_type"] == "SHT_RELA"
                if not rela and sec["sh_type"] != "SHT_REL":
                    continue
                fmt = e + ("QQq" if b64 else "Iii") if rela else e + ("QQ" if b64 else "II")
                ent = struct.calcsize(fmt)
                raw = sec.data()
                for t in struct.iter_unpack(fmt, raw[:len(raw) // ent * ent]):
                    if (t[1] & 0xffffffff if b64 else t[1] & 0xff) == rel_type:
                        rels.append((t[0] + base, t[2] if rela else None))
                        if len(rels) >= 500_000:
                            return None
        plt = [(s["sh_addr"] + base, s["sh_addr"] + base + s["sh_size"]) for s in secs
               if s.name.startswith(".plt") and s["sh_size"]]
    except Exception:  # noqa: BLE001 -- hostile / truncated ELF
        return None
    if mach == 183:
        uc = U.Uc(U.UC_ARCH_ARM64, U.UC_MODE_ARM)
        A = U.arm64_const
        SP, RET = A.UC_ARM64_REG_SP, A.UC_ARM64_REG_W0
    else:
        uc = U.Uc(U.UC_ARCH_X86, U.UC_MODE_64 if mach == 62 else U.UC_MODE_32)
        X = U.x86_const
        SP, RET = (X.UC_X86_REG_RSP, X.UC_X86_REG_EAX) if mach == 62 else (X.UC_X86_REG_ESP, X.UC_X86_REG_EAX)
    w = 4 if mach == 3 else 8
    bad = []
    try:
        run = []
        for p in sorted(pages):
            if run and p == run[-1][0] + run[-1][1] and pages[p] == run[-1][2]:
                run[-1][1] += 0x1000
            else:
                run.append([p, 0x1000, pages[p]])
        for p, n, prot in run:
            uc.mem_map(p, n, prot)
        for va, blob in loads:
            uc.mem_write(va, blob)
        for off, add in rels:
            if add is None:   # REL (i386): addend in place
                add = int.from_bytes(uc.mem_read(off, w), "little")
            uc.mem_write(off, ((add + base) & ((1 << (8 * w)) - 1)).to_bytes(w, "little"))
        top = (max(pages) + 0x100000 + 0xfffff) & ~0xfffff
        stk, sent = top, top + 0x40000
        uc.mem_map(stk, 0x40000)
        uc.mem_map(sent, 0x1000, U.UC_PROT_READ | U.UC_PROT_EXEC)
        sp = stk + 0x30000
        if mach == 183:
            uc.reg_write(A.UC_ARM64_REG_X30, sent)
            uc.reg_write(A.UC_ARM64_REG_X29, sp)
        else:
            sp -= w
            uc.mem_write(sp, sent.to_bytes(w, "little"))
        uc.reg_write(SP, sp)

        def refuse(why):
            def cb(uc, *a):
                bad.append(why)
                uc.emu_stop()
            return cb
        uc.hook_add(U.UC_HOOK_INTR, refuse("int/svc"))
        if mach == 62:
            uc.hook_add(U.UC_HOOK_INSN, refuse("syscall"), None, 1, 0, U.x86_const.UC_X86_INS_SYSCALL)
            uc.hook_add(U.UC_HOOK_INSN, refuse("sysenter"), None, 1, 0, U.x86_const.UC_X86_INS_SYSENTER)
        for lo, hi in plt:
            uc.hook_add(U.UC_HOOK_CODE, refuse("plt"), None, lo, hi - 1)
        uc.hook_add(U.UC_HOOK_MEM_INVALID, refuse("mem"))
        uc.emu_start(addr + base, sent, timeout=timeout_ms * 1000, count=max_insns)
        if bad or uc.reg_read(U.arm64_const.UC_ARM64_REG_PC if mach == 183 else
                              (X.UC_X86_REG_RIP if mach == 62 else X.UC_X86_REG_EIP)) != sent:
            return None
        v = uc.reg_read(RET) & 0xffffffff
    except Exception:  # noqa: BLE001 -- unicorn on hostile bytes: never raise past the caller
        return None
    return v - (1 << 32) if signed and v >> 31 else v


# --- Ghidra headless decompile -------------------------------------------------------------------
def ghidra_decompile(path, timeout=300):
    """Decompile every function with Ghidra headless (JDK 21 wired in launch.properties) and return the C
    text. Empty string on failure. Heavy (~minutes) — use only when symbol/pattern reads don't suffice."""
    headless = Path(__file__).resolve().parents[1] / "bin" / "analyzeHeadless"
    if not headless.exists() or not GHIDRA_SCRIPT.exists():
        return ""
    with tempfile.TemporaryDirectory() as proj, tempfile.NamedTemporaryFile(suffix=".c") as outf:
        # Output must live OUTSIDE the project dir: -deleteProject wipes the project tree on exit.
        subprocess.run(
            [str(headless), proj, "P", "-import", str(path), "-scriptPath", str(GHIDRA_SCRIPT.parent),
             "-postScript", GHIDRA_SCRIPT.name, outf.name, "-deleteProject"],
            capture_output=True, text=True, timeout=timeout)
        return Path(outf.name).read_text(errors="replace")


# --- HCFG config blob: every storage encoding -----------------------------------------------------
# Blob layout (D2-D13, every language): b'HCFG' | u8 version | u8 xor_key | u16 len (LE) | u32 crc32 (LE) | len bytes
# of JSON ^ xor_key; crc32 is over the PLAIN JSON. Storage seen so far: raw (.hcfg section, .NET FieldRVA, rodata, FPC
# .data) and base64 text (jar constant pool, Swift/Nim/D/Crystal string literals). hcfg_scan() also covers the next
# plausible mutations: hex (plain / with separators / \x / 0x), base64url, base32, base85, ascii85, UTF-16LE/BE text of
# raw/base64/hex/base32/base85, reversed raw / reversed base64, single-byte-xor'd base64 / raw, zlib/gzip/raw-deflate,
# multi-byte xor: multixor-body (plain header, body ^ repeating 1-16 B key) / multixor-raw (whole blob ^ 2-16 B key
# stored right before it; offset = first xor'd byte, detail key@<key offset>), base64-custom (base64 under a shuffled
# 64-char alphabet stored as a literal in the binary; offset = first char of the text, detail alphabet@<its offset>).
# rot13-/swapcase-/rot13-swapcase-base64 (letters transformed), linerev-[<x>-]base64 / reversed-<x>-base64 (each line of
# the wrapped text reversed; offset = first stored char). split-base64/-base64url/-base32/-hex: the text cut into several
# string literals in FILE order (NUL/padding/short separators between; offset = first char of the first chunk).
# int arrays: u32le-/u32be-/u64le-/u64be-array (one blob byte per 32/64-bit element; offset = first byte of the first
# element, BE: its leading 0x00), u16be-/u32be-/u64be-packed (blob packed big-endian into 16/32/64-bit words that a LE
# compiler stored byte-swapped, e.g. uint32_t a[] = {0x48434647, ...}; offset = first stored byte), decimal-list
# ('72,67,70,71,...' / '72 67 70 71' char codes, signed bytes -128..-1 allowed; offset = the '7' of '72').
# byte maps: nibswap-/rolN-/add-raw, nibswap-/rolN-/add-base64 (base64 text then mapped), base64-nibswap/-rolN/-not/
# -add (base64 of the mapped blob); add detail add=0xNN (a sub k is add 256-k); offset = first stored byte/char.
#
# OFFSET LAW (Hit.offset, decimal FILE offset -- what `hcfg_offset` asks for):
#   raw              the 'H' of the magic                          GM-confirmed (D12 FPC 82928)
#   base64           the first base64 char ('S' of 'SENGR...')     GM-confirmed (D9 30696, D11 368272, D13 560188)
#   everything else  the first byte of the STORED encoded form, i.e. the lowest file offset the stored bytes occupy:
#                    hex -> first char of the text (the '\' of '\x48' / the '0' of '0x48'); base32/base85/base64url ->
#                    first char; ascii85 -> the '<' of a '<~' prefix if present; UTF-16 -> first byte of the first code
#                    unit (BE: its 0x00 byte); reversed -> lowest byte of the reversed region (= where the blob's LAST
#                    byte sits); xor'd/RC4 -> first stored byte; zlib/gzip/deflate -> first byte of the compressed stream
#                    (0x78 CMF / 0x1f gzip magic; a zlib/gzip stream that holds the blob further in: still the
#                    stream start, detail "at+N"). These are SPECULATIVE (Hit.speculative=True): not GM-verified yet.
#   container slots  (D16 prep) a blob in a PE RT_RCDATA resource, a .NET manifest resource, a STORED zip/jar entry or
#                    an overlay is plain bytes in the file -> still "raw" at the magic; hcfg_locate(data, off) names the
#                    slot and its start (resource data start / overlay start) so a resource-relative ask can use delta.
#                    A DEFLATED jar/zip entry -> "deflate" at the entry's compressed-data start, detail "at+N zip=<name>"
#                    (= what the fixed-Huffman anchor reports); a text form inside an entry -> "zip-<enc>" at the
#                    offset INSIDE the inflated entry (like upx-<enc>), detail "zip=<name> data@<compressed start>".
#                    .NET single-file bundle: a stored entry is plain bytes (raw at the magic; hcfg_locate -> container
#                    "dotnet-bundle", slot = the embedded dll's offset); a COMPRESSED entry -> "deflate" / "bundle-<enc>"
#                    exactly like a zip entry (detail "bundle=<path>").
HCFG_MAGIC = b"HCFG"
HCFG_SCAN_EXT = os.environ.get("HCTF_HCFG_SCAN_EXT", "1") != "0"   # 0: only the D13 encodings (_LEGACY)
HCFG_DEFLATE_BRUTE_MAX = int(os.environ.get("HCTF_HCFG_DEFLATE_MAX", str(1 << 20)))   # headerless deflate brute cap
HCFG_B64ALPHA_MAX = int(os.environ.get("HCTF_HCFG_B64ALPHA_MAX", str(32 << 20)))   # alphabet-run chars examined
HCFG_MXOR_MAX = int(os.environ.get("HCTF_HCFG_MXOR_MAX", str(8 << 20)))   # whole-blob multi-byte xor cap (~65 ms/MiB)
HCFG_RC4_KEYS = int(os.environ.get("HCTF_HCFG_RC4_KEYS", "100000"))   # C-string RC4 keys tried (~6 us each)
_CONFIRMED = ("raw", "base64")
_LEGACY = ("raw", "base64", "base64url", "hex")   # what the D13 solver's native scan already decodes


@dataclass
class HcfgHit:
    offset: int              # file offset per the OFFSET LAW above
    encoding: str            # raw/base64/base64url/hex/hex-sep/base32/base85/ascii85/reversed-raw/zlib/... (+utf16le-)
    version: int
    key: int
    length: int
    crc: int                 # header crc32
    crc_ok: bool             # crc32(plain) == header crc: the TRUE blob (decoys / truncated copies fail)
    config: "dict | None"    # json.loads(plain), None if it does not parse
    plain: bytes = field(repr=False, default=b"")
    speculative: bool = True  # offset semantics not GM-confirmed (everything but raw/base64)
    detail: str = ""          # e.g. "xor=0x5a", "altchars"

    @property
    def valid(self):
        return self.crc_ok and isinstance(self.config, dict)

    def as_solver(self):
        """The binary solvers' hcfg() dict shape."""
        return {"key": self.key, "crc": zlib.crc32(self.plain), "config": self.config, "version": self.version,
                "offset": self.offset, "encoding": self.encoding, "speculative": self.speculative}


Hit = HcfgHit


def _parse_blob(blob):
    """(version, key, length, crc, plain, crc_ok, config) for bytes starting with the magic, else None."""
    if len(blob) < 12 or blob[:4] != HCFG_MAGIC:
        return None
    ver, key, n, crc = struct.unpack_from("<BBHI", blob, 4)
    plain = bytes(b ^ key for b in blob[12:12 + n])
    ok = 0 < n == len(plain) and zlib.crc32(plain) == crc   # n=0: a bare magic string ("HCFG"\0...) is no blob
    try:
        cfg = json.loads(plain.decode())
    except (ValueError, UnicodeDecodeError):
        cfg = None
    return ver, key, n, crc, plain, ok, cfg


def _need(blob_head):
    """Total blob size (12-byte header + body) from its first 8 bytes."""
    return 12 + int.from_bytes(blob_head[6:8], "little")


class _Text:
    """Character-count codec for one text encoding: chars(nbytes) -> characters encoding the first nbytes; dec(text)."""
    def __init__(self, name, alphabet, chars, dec):
        self.name, self.rx, self.chars, self.dec = name, re.compile(alphabet), chars, dec


def _b64dec(t):
    t = t.replace(b"-", b"+").replace(b"_", b"/").rstrip(b"=")
    return binascii.a2b_base64(t + b"=" * (-len(t) % 4))


def _b32dec(t):
    t = t.rstrip(b"=").upper()
    return base64.b32decode(t + b"=" * (-len(t) % 8))


_B64 = _Text("base64", rb"[A-Za-z0-9+/_\-\r\n]+={0,2}", lambda n: -(-n * 4 // 3), _b64dec)
_B32 = _Text("base32", rb"(?:[A-Z2-7]+|[a-z2-7]+)={0,6}", lambda n: -(-n * 8 // 5), _b32dec)
_G85 = lambda n: n // 4 * 5 + (n % 4 + 1 if n % 4 else 0)   # noqa: E731 - base85/ascii85 chars for n bytes
_B85 = _Text("base85", rb"[0-9A-Za-z!#$%&()*+\-;<=>?@^_`{|}~]+", _G85, base64.b85decode)
_A85 = _Text("ascii85", rb"[!-u]+", _G85, lambda t: base64.a85decode(t))
# anchors: the encoded form of the 4 magic bytes alone (base64 30 bits = 5 chars, base32 6 chars, base85 1 group)
_TEXT_ANCHORS = ((b"SENGR", _B64), (b"JBBUMR", _B32), (b"jbbumr", _B32), (base64.b85encode(HCFG_MAGIC), _B85),
                 (base64.a85encode(HCFG_MAGIC), _A85))
_HEX_ANCHOR = re.compile(rb"48[ \t:,;\-]*(?:\\[xX]|0[xX])?43[ \t:,;\-]*(?:\\[xX]|0[xX])?46[ \t:,;\-]*"
                         rb"(?:\\[xX]|0[xX])?47")
_HEX_RUN = re.compile(rb"(?:(?:\\[xX]|0[xX])?[0-9A-Fa-f]{2}[ \t\r\n:,;\-]*)+")
_HEX_PAIR = re.compile(rb"(?:\\[xX]|0[xX])?([0-9A-Fa-f]{2})")
_U16LE = re.compile(rb"(?:[\x09-\x7e]\x00)+")
_U16BE = re.compile(rb"(?:\x00[\x09-\x7e])+")
_B64REV = re.compile(rb"[A-Za-z0-9+/_\-]+={0,2}")


def _widen(s, be=False):
    return b"".join((b"\0" + bytes([c])) if be else (bytes([c]) + b"\0") for c in s)


def _decode_text(codec, run):
    """(blob, chars consumed) decoding the blob at the start of `run` (whitespace already stripped), or None."""
    try:
        head = codec.dec(run[:codec.chars(12)])
        if head[:4] != HCFG_MAGIC or len(head) < 8:
            return None
        k = codec.chars(_need(head))
        return codec.dec(run[:k]), k
    except (binascii.Error, ValueError):
        return None


def _text_at(buf, i, codec, emit, prefix=""):
    """Decode the `codec` text whose magic anchor sits at buf[i]; emit(pos, encoding, blob, detail)."""
    m = codec.rx.match(buf, i)
    run = re.sub(rb"[\r\n]", b"", m.group(0)) if m else b""
    r = _decode_text(codec, run)
    if r:
        name, pos = codec.name, i
        if codec is _B64 and re.search(rb"[-_]", run[:r[1]]):
            name = "base64url"
        if codec is _A85 and buf[max(0, i - 2):i] == b"<~":
            pos = i - 2
        emit(pos, prefix + name, r[0], "")


def _hex_at(buf, s, emit, prefix=""):
    """Decode the hex text (plain, or separated / \\x / 0x) whose '48' sits at buf[s]."""
    if buf[max(0, s - 2):s] in (b"\\x", b"\\X", b"0x", b"0X"):
        s -= 2
    pairs = _HEX_PAIR.findall(_HEX_RUN.match(buf, s).group(0))
    if len(pairs) < 12:
        return
    head = bytes.fromhex(b"".join(pairs[:12]).decode())
    blob = bytes.fromhex(b"".join(pairs[:_need(head)]).decode())
    sep = not re.fullmatch(rb"[0-9A-Fa-f]+", buf[s:s + 2 * len(blob)])
    emit(s, prefix + ("hex-sep" if sep else "hex"), blob, "")


def _text_hits(buf, emit, prefix=""):
    """Every text encoding (base64/url, base32, base85, ascii85, hex) inside a SMALL buffer (a narrowed UTF-16 run)."""
    for anchor, codec in _TEXT_ANCHORS:
        i = buf.find(anchor)
        while i >= 0:
            _text_at(buf, i, codec, emit, prefix)
            i = buf.find(anchor, i + 1)
    for m in _HEX_ANCHOR.finditer(buf):
        _hex_at(buf, m.start(), emit, prefix)


def _ends(deadline):
    ends = [d for d in (deadline,) if d]
    try:
        ends.append(float(os.environ["HCTF_SOLVE_DEADLINE"]))   # set by the timed runner (lib.decode.solve_deadline)
    except (KeyError, ValueError):
        pass
    return min(ends) if ends else None


def _fixed_deflate_anchors():
    """First 4 bytes of a fixed-Huffman deflate block that starts with literals 'HCFG' (BFINAL=1 and BFINAL=0)."""
    c = zlib.compressobj(6, zlib.DEFLATED, -15, 8, zlib.Z_FIXED)
    z = (c.compress(HCFG_MAGIC + bytes(8)) + c.flush())[:4]
    return (z, bytes([z[0] & 0xFE]) + z[1:])


_DEFLATE_FIXED = _fixed_deflate_anchors()
# dynamic-Huffman final block: low 3 bits 101 (BFINAL=1, BTYPE=10) and HLIT (bits 3-7) <= 29
_DEFLATE_DYN = re.compile(b"[" + b"".join(re.escape(bytes([5 + 8 * h])) for h in range(30)) + b"]")


def _trie(words):
    """Regex alternation of literal byte strings, factored by first byte (no word may be a prefix of another)."""
    groups = {}
    for w in words:
        groups.setdefault(w[:1], []).append(w[1:])
    parts = []
    for c, rests in sorted(groups.items()):
        parts.append(re.escape(c) + (b"(?:" + _trie(rests) + b")" if len(rests) > 1 else re.escape(rests[0])))
    return b"|".join(parts)


_UP, _LO = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ", b"abcdefghijklmnopqrstuvwxyz"
_ROT13 = bytes.maketrans(_UP + _LO, _UP[13:] + _UP[:13] + _LO[13:] + _LO[:13])
_SWAPC = bytes.maketrans(_UP + _LO, _LO + _UP)
# letter-only transforms of base64 text (involutions: the same table decodes); anchor -> (name, table, line-reversed)
_ROTB64 = {b"RGNES": ("", None, True)}   # plain base64 reversed per line: shares the rev-b64 anchor
for _n, _t in (("rot13", _ROT13), ("swapcase", _SWAPC), ("rot13-swapcase", _ROT13.translate(_SWAPC))):
    _ROTB64[b"SENGR".translate(_t)] = (_n, _t, False)
    _ROTB64[b"SENGR".translate(_t)[::-1]] = (_n, _t, True)
_B64LINES = re.compile(rb"[A-Za-z0-9+/_\-=\r\n]+")


def _rotb64_at(data, i, a, emit):
    """ROT13 / case-swapped base64 (any line wrapping) whose transformed 'SENGR' sits at data[i]; or the same text --
    plain base64 too -- with EVERY LINE reversed (anchor = the reversed 'SENGR' ending the first stored line). Offset =
    first stored char (the first line's first char); one-line reversal is 'reversed-<x>', multi-line 'linerev-<x>'
    (plain one-line = the existing 'reversed-base64', not re-emitted)."""
    name, tbl, rev = _ROTB64[a]
    if not rev:
        m = _B64.rx.match(data, i, i + 90000)
        r = _decode_text(_B64, re.sub(rb"[\r\n]", b"", m.group(0)).translate(tbl)) if m else None
        if r:
            emit(i, name + "-base64", r[0], "")
        return
    e = i + 5
    mm = _B64REV.match(data[max(0, e - 90000):e][::-1])   # back to the start of the first stored line
    s = e - len(mm.group(0)) if mm else e
    m = _B64LINES.match(data, s, s + 90000)
    lines = re.findall(rb"[^\r\n]+", m.group(0)) if m else []
    if not lines or s + len(lines[0]) != e:
        return
    text = b"".join(ln[::-1] for ln in lines)
    r = _decode_text(_B64, text.translate(tbl) if tbl else text)
    if r and (r[1] > len(lines[0].strip(b"=")) or name):
        multi = r[1] > len(lines[0].strip(b"="))
        emit(s, ("linerev-" if multi else "reversed-") + (name + "-" if name else "") + "base64", r[0], "")


_HEXT = _Text("hex", rb"[0-9A-Fa-f]+", lambda n: 2 * n, binascii.unhexlify)
# split literals: anchor -> codec; chunks = maximal alphabet runs joined across gaps of <= _SPLIT_GAP non-alphabet bytes
_SPLIT = ((b"SENGR", _B64), (b"JBBUMR", _B32), (b"jbbumr", _B32), (b"48434647", _HEXT))
_SPLIT_GAP = 32


def _split_at(data, i, codec, emit):
    """Encoded text cut into several string literals laid out in FILE ORDER (C `const char *parts[]` / char[][N]
    tables: NUL terminators + alignment padding, or any short non-alphabet separator between chunks) whose first chunk
    holds the magic anchor at data[i]. Joins up to 512 chunks until the header's length is covered; only multi-chunk
    texts are emitted ('split-<codec>', offset = first char of the first chunk, detail chunks=N)."""
    parts, need, p = [], None, i
    while len(parts) < 512:
        m = codec.rx.match(data, p, p + 90000)
        if not m:
            break
        parts.append(re.sub(rb"[\r\n]", b"", m.group(0)))
        text = b"".join(parts)
        if need is None and len(text) >= codec.chars(12):
            try:
                head = codec.dec(text[:codec.chars(12)])
            except (binascii.Error, ValueError):
                return
            if head[:4] != HCFG_MAGIC:
                return
            need = codec.chars(_need(head))
        if need is not None and len(text) >= need:
            break
        nxt = codec.rx.search(data, m.end(), m.end() + _SPLIT_GAP + 1)
        if not nxt:
            break
        p = nxt.start()
    if len(parts) < 2 or need is None or len(b"".join(parts[:-1])) >= need:
        return
    r = _decode_text(codec, b"".join(parts))
    if r:
        name = codec.name
        if codec is _B64 and re.search(rb"[-_]", b"".join(parts)[:r[1]]):
            name = "base64url"
        emit(i, "split-" + name, r[0], f"chunks={len(parts)}")


def _split_raw_at(data, i, emit, left):
    """RAW blob cut into consecutive NUL-terminated literals (GnuCOBOL WORKING-STORAGE `05 F-n PIC X(k) VALUE X"..."`
    fields at cobc -O0 = memcpy sources in .rodata; C `char p[][k]`): the NUL runs between chunks are terminators +
    alignment, but the blob itself holds NULs too (length high byte, crc, key-equal chars) -> DFS over how many NULs of
    each run (<= _SPLIT_GAP) are gap, body bytes must xor to printable JSON text, crc decides. 'split-raw', offset =
    first byte of the first chunk (the magic), detail chunks=N. Bounded: blobs <= 16 KiB, `left` = [DFS nodes] shared
    by every anchor of one scan."""
    win = data[i:i + 0x4000 + 64 * _SPLIT_GAP]

    def walk(p, out, gaps):
        left[0] -= 1
        if left[0] < 0:
            return None
        while True:
            if len(out) >= 12:
                n = _need(out)
                if n > 0x4000:
                    return None
                if len(out) >= n:
                    r = _parse_blob(bytes(out[:n]))
                    return (bytes(out[:n]), gaps) if r and r[5] and gaps else None
            if p >= len(win):
                return None
            c = win[p]
            if c:
                if len(out) >= 12 and not (0x20 <= c ^ out[5] <= 0x7e or c ^ out[5] in (9, 10, 13)):
                    return None
                out.append(c)
                p += 1
                continue
            q = p
            while q < len(win) and not win[q]:
                q += 1
            r_ = q - p
            for s in range(min(r_, _SPLIT_GAP) + 1):   # s NULs of this run are gap, the rest is blob content
                nxt = out + b"\0" * (r_ - s)
                if len(nxt) > 12 and not 0x20 <= nxt[5] <= 0x7e and max(len(out), 12) < len(nxt):
                    continue   # a NUL in the body xors to the key: only printable keys allow body NULs
                got = walk(q, nxt, gaps + (s > 0))
                if got or left[0] < 0:
                    return got
            return None

    got = walk(4, bytearray(win[:4]), 0)
    if got:
        emit(i, "split-raw", got[0], f"chunks={got[1] + 1}")


def _wide_at(data, i, w, emit, budget):
    """One blob byte per w-byte array element ('H' + (w-1) NULs + 'C'... at i): LE starts at i, BE at i-(w-1). A run
    of such elements reads both ways with the same bytes -- keep the w-aligned start (compilers align int arrays),
    LE when both/neither are."""
    cands = [(False, i), (True, i - w + 1)]
    cands.sort(key=lambda c: (c[1] % w != 0, c[0]))
    for be, st in cands:
        off = w - 1 if be else 0
        if st < 0 or budget[0] <= 0:
            continue
        budget[0] -= 1
        n = _need(data[st + off:st + off + 8 * w:w])
        span = data[st:st + n * w]
        lo = span[off::w]
        if len(lo) == n and span.count(0) == len(span) - n + lo.count(0):   # every non-value byte is 0x00
            emit(st, f"u{8 * w}{'be' if be else 'le'}-array", lo)
            return


_SWAP_TC = {2: "H", 4: "I", 8: "Q"}


def _swapped_at(data, st, w, emit, budget):
    """Blob packed big-endian into w-byte words stored little-endian (each word's bytes reversed) starting at st.
    budget: [candidates left] -- 'GFCH'/'CHGF' floods (decoy tables) stay bounded."""
    tc = _SWAP_TC[w]
    if st < 0 or budget[0] <= 0 or array.array(tc).itemsize != w:
        return
    def unswap(buf):
        a = array.array(tc, buf[:len(buf) // w * w])
        a.byteswap()
        return a.tobytes()
    head = unswap(data[st:st + 16])
    if head[:4] != HCFG_MAGIC:
        return
    n = _need(head)
    budget[0] -= 1
    emit(st, f"u{8 * w}be-packed", unswap(data[st:st + -(-n // w) * w])[:n])


_DEC_SEP = rb"(?:[ \t\r\n]*[,;][ \t\r\n]*|[ \t\r\n]+)"
_DEC_ANCHOR = re.compile(rb"72" + _DEC_SEP + rb"67" + _DEC_SEP + rb"70" + _DEC_SEP + rb"71(?![0-9])")
_DEC_RUN = re.compile(rb"-?[0-9]{1,3}(?:" + _DEC_SEP + rb"-?[0-9]{1,3})*")
_DEC_NUM = re.compile(rb"-?[0-9]+")


def _decimal_at(data, s, emit):
    """Decode the decimal char-code list whose '72' sits at data[s] (not preceded by a digit / '-')."""
    if s and data[s - 1] in b"0123456789-":
        return
    nums = _DEC_NUM.findall(_DEC_RUN.match(data, s, s + 256).group(0))
    if len(nums) < 12:
        return
    n = _need(bytes(int(x) & 0xFF for x in nums[:8]))
    nums = _DEC_NUM.findall(_DEC_RUN.match(data, s, s + 16 * n + 64).group(0))[:n]
    vals = [int(x) for x in nums]
    if len(vals) == n and all(-128 <= v <= 255 for v in vals):
        emit(s, "decimal-list", bytes(v & 0xFF for v in vals))


def _anchor_table():
    lit = {HCFG_MAGIC: ("raw", None), b"GFCH": ("rev-raw", None), b"RGNES": ("rev-b64", None)}
    for a, codec in _TEXT_ANCHORS:
        lit[a] = ("text", codec)
        lit[_widen(a)[:-1]] = ("u16text", None)   # 'S\0E\0N\0G\0R': LE at i, BE at i-1
    lit[_widen(b"48")[:-1]] = ("u16text", None)
    lit[_widen(HCFG_MAGIC)[:-1]] = ("u16raw", None)
    for w in (4, 8):
        lit[(b"\0" * (w - 1)).join(bytes([c]) for c in HCFG_MAGIC)] = ("wide", None)   # 'H\0\0\0C\0\0\0F\0\0\0G'
    lit[b"CHGF"] = ("swap16", None)
    z = {b"\x78\x01": (15, "zlib"), b"\x78\x5e": (15, "zlib"), b"\x78\x9c": (15, "zlib"), b"\x78\xda": (15, "zlib"),
         b"\x1f\x8b\x08": (31, "gzip"), _DEFLATE_FIXED[0]: (-15, "deflate"), _DEFLATE_FIXED[1]: (-15, "deflate")}
    for a in z:
        lit[a] = ("z", None)
    # first-byte trie (H(?:CFG|\0C\0F\0G)|S(?:...)...): one branch per position, ~20% faster than a flat alternation;
    # NO named groups (8x slower: 135 vs 16 ms on 1.8 MB) -- the matched bytes identify the anchor
    rx = re.compile(_HEX_ANCHOR.pattern + b"|" + _trie(list(lit)))
    return rx, {a: k for a, (k, _) in lit.items()}, {a: c for a, (_, c) in lit.items() if c}, z


_ANCHORS, _ANCHOR_KIND, _ANCHOR_CODEC, _ANCHOR_Z = _anchor_table()


def _inflate(mv, p, wbits, budget=None):
    """(decompressed bytes from the 'HCFG' on, its position in the stream's output) for the stream at p, or None.
    Raw deflate must START with the magic; a zlib/gzip stream may also CONTAIN it (a compressed section/resource): those
    are inflated up to 1 MiB each, charged to budget[0] (bytes left for the whole scan)."""
    try:
        d = zlib.decompressobj(wbits)
        head = d.decompress(mv[p:p + 512], 4)
        if len(head) < 4 and not d.eof:
            head += d.decompress(mv[p + 512:p + (64 << 10)], 4 - len(head))
    except zlib.error:
        return None
    if head == HCFG_MAGIC:
        at = 0
    elif wbits < 0 or len(head) < 4 or not budget or budget[0] <= 0:
        return None
    else:
        at = -1
    try:
        d = zlib.decompressobj(wbits)
        out = d.decompress(mv[p:p + (2 << 20)], 70000 if at == 0 else (1 << 20))
    except zlib.error:
        return None
    if at < 0:
        budget[0] -= len(out)
        at = out.find(HCFG_MAGIC)
        if at < 0:
            return None
        out = out[at:at + 70000]
    return out, at


# compressed stream (zlib/gzip/xz/bz2/lzma-alone) stored as base64 / plain hex text, or xz/bz2/lzma raw in the file
# (zlib/gzip/deflate raw are anchors above). One bytes.find per needle (~0.5 ms/MiB each; a regex alternation was 20 ms/
# MiB): base64 of the stream header 78 9c -> eJ[w-z], 78 da -> eN[o-r], 1f 8b 08 -> H4sI, xz -> /Td6WFoA, 'BZh' ->
# Qlpo, 5d 00 00 -> XQAA; lowercase+uppercase hex of zlib/gzip; raw xz magic, bz2 block magic (4 bytes past 'BZh9'),
# lzma-alone props 5d 00 00 (header-checked before inflating); zstd (28 b5 2f fd -> KLUv/) and LZ4 frame (04 22 4d 18 ->
# BCJNG) raw / base64 / hex (speculative: offset = first stored byte). (needle, bytes before the stream start, form)
_ZPACK = ((b"eJ", 0, "b64"), (b"eN", 0, "b64"), (b"H4sI", 0, "b64"), (b"/Td6WFoA", 0, "b64"), (b"Qlpo", 0, "b64"),
          (b"XQAA", 0, "b64"), (b"789c", 0, "hex"), (b"78da", 0, "hex"), (b"1f8b08", 0, "hex"), (b"789C", 0, "hex"),
          (b"1F8B08", 0, "hex"), (b"\xfd7zXZ\x00", 0, "raw"), (b"1AY&SY", 4, "raw"), (b"]\x00\x00", 0, "raw"),
          (b"\x28\xb5\x2f\xfd", 0, "raw"), (b"KLUv/", 0, "b64"), (b"28b52ffd", 0, "hex"),
          (b"\x04\x22\x4d\x18", 0, "raw"), (b"BCJNG", 0, "b64"), (b"04224d18", 0, "hex"))
_ZPACK_B64 = re.compile(rb"[A-Za-z0-9+/_\-\r\n]+")
_ZPACK_HEX = re.compile(rb"[0-9A-Fa-f]+")


def _zpack_kind(head):
    """Container name for decoded stream bytes, or None."""
    if head[:2] in (b"\x78\x9c", b"\x78\xda", b"\x78\x01", b"\x78\x5e"):
        return "zlib"
    if head[:3] == b"\x1f\x8b\x08":
        return "gzip"
    if head[:6] == b"\xfd7zXZ\x00":
        return "xz"
    if re.match(rb"BZh[1-9]1AY&SY", head):
        return "bz2"
    if head[:3] == b"\x5d\x00\x00" and len(head) >= 13:   # lzma-alone: props, dict size, u64 size (-1 or sane)
        dic, size = int.from_bytes(head[1:5], "little"), int.from_bytes(head[5:13], "little")
        if dic >= 1 << 16 and (dic & (dic - 1) == 0 or dic & (dic - 1) & (dic - 2) == 0) and (
                size == (1 << 64) - 1 or 12 <= size < 64 << 20):
            return "lzma"
    if head[:4] == b"\x28\xb5\x2f\xfd" and len(head) > 4 and not head[4] & 0x08:   # frame header reserved bit 0
        return "zstd"
    if head[:4] == b"\x04\x22\x4d\x18" and len(head) > 5 and head[4] >> 6 == 1 and not head[4] & 0x02:   # FLG v01
        return "lz4"
    return None


def _zpack_open(kind, buf, budget):
    """(output from the 'HCFG' on, its position) for the `kind` stream at buf[0], or None; output charged to budget."""
    import bz2
    import lzma
    if kind in ("zstd", "lz4"):
        try:
            if kind == "zstd":
                import zstandard
                out = zstandard.ZstdDecompressor().stream_reader(io.BytesIO(bytes(buf)), read_across_frames=False).read(
                    1 << 20)
            else:
                import lz4.frame
                out = lz4.frame.LZ4FrameDecompressor().decompress(bytes(buf), max_length=1 << 20)
        except Exception:   # noqa: BLE001 - ImportError / ZstdError / LZ4 RuntimeError on a truncated or fake frame
            return None
        budget[0] -= len(out)
        at = out.find(HCFG_MAGIC)
        return (out[at:at + 70000], at) if at >= 0 else None
    if kind in ("zlib", "gzip"):
        d = zlib.decompressobj(15 if kind == "zlib" else 31)
    elif kind == "bz2":
        d = bz2.BZ2Decompressor()
    else:
        d = lzma.LZMADecompressor(lzma.FORMAT_XZ if kind == "xz" else lzma.FORMAT_ALONE)
    try:
        out = d.decompress(bytes(buf), 1 << 20)
    except (zlib.error, OSError, EOFError, ValueError, lzma.LZMAError):
        return None
    budget[0] -= len(out)
    at = out.find(HCFG_MAGIC)
    return (out[at:at + 70000], at) if at >= 0 else None


def _zpack_at(data, i, form, emit, budget):
    """Decode the compressed stream stored at data[i] as `form` (b64 / hex text, or raw) and emit its blob."""
    if form == "raw":
        stream, pre = data[i:i + 16], ""
    else:
        m = (_ZPACK_HEX if form == "hex" else _ZPACK_B64).match(data, i, i + 32)
        if not m or len(m.group(0)) < 32:   # a 12-byte blob compresses to >= 20 bytes (>= 27 b64 chars)
            return
        head = m.group(0).replace(b"\r", b"").replace(b"\n", b"")
        try:
            stream = bytes.fromhex(head[:24].decode()) if form == "hex" else _b64dec(head[:24])
        except (binascii.Error, ValueError):
            return
        pre = "hex-" if form == "hex" else "base64-"
    kind = _zpack_kind(stream)
    if not kind or budget[0] <= 0:
        return
    if form == "raw":
        stream = data[i:i + (2 << 20)]
    else:
        run = (_ZPACK_HEX if form == "hex" else _ZPACK_B64).match(data, i, i + (3 << 20)).group(0)
        try:
            if form == "hex":
                stream = bytes.fromhex(run[:len(run) & ~1].decode())
            else:
                run = run.replace(b"\r", b"").replace(b"\n", b"")
                stream = _b64dec(run[:len(run) & ~3] if len(run) % 4 == 1 else run)
        except (binascii.Error, ValueError):
            return
    r = _zpack_open(kind, stream, budget)
    if r:
        emit(i, pre + kind, r[0], f"at+{r[1]}" if r[1] else "")


_PRINTABLE = frozenset(range(0x20, 0x7f)) | {9, 10, 13}
_PMASK = [sum(1 << k for k in range(256) if b ^ k in _PRINTABLE) for b in range(256)]   # keys keeping b printable
_JSONW = {**{c: 2 for c in b"bcfgkmpquvwxyz0123456789:,._-/ "}, **{c: 4 for c in b'etaoinsrhld"'},
          **{c: 1 for c in b"ABCDEFGHIJKLMNOPQRSTUVWXYZ{}[]\\\n"}}   # JSON config byte weights (key ranking)


def _xor_rep(buf, key):
    """buf ^ key repeated from buf[0]."""
    k = (key * (len(buf) // len(key) + 1))[:len(buf)]
    return (int.from_bytes(buf, "little") ^ int.from_bytes(k, "little")).to_bytes(len(buf), "little")


def _rc4(key, buf):
    """RC4(key) applied to buf (pycryptodome when present, else pure Python)."""
    try:
        from Crypto.Cipher import ARC4
        return ARC4.new(key).encrypt(bytes(buf))
    except Exception:  # noqa: BLE001 - missing module / unsupported key length: pure-Python fallback
        S, j, kl = list(range(256)), 0, len(key)
        for i in range(256):
            j = (j + S[i] + key[i % kl]) & 255
            S[i], S[j] = S[j], S[i]
        out, i, j = bytearray(buf), 0, 0
        for n in range(len(out)):
            i = (i + 1) & 255
            j = (j + S[i]) & 255
            S[i], S[j] = S[j], S[i]
            out[n] ^= S[(S[i] + S[j]) & 255]
        return bytes(out)


_RC4_KEY = re.compile(rb"\0([\x21-\x7e][\x20-\x7e]{3,63})(?=\0)")   # NUL-delimited 4-64 char C string (~0.1 s / 48 MiB)


def _mxor_body(data, i):
    """(blob, key) for a plain HCFG header at data[i] whose body is JSON ^ a repeating 1-16 byte key (any header xor
    byte folded in), body at +12 or after the key stored at +12; crc-confirmed. Key per column: the bytes that keep the
    whole column printable, best JSON-looking first (top pick, then one-column swaps). None if nothing checks out."""
    head = data[i:i + 12]
    if len(head) < 12 or not head[6:8].strip(b"\0"):
        return None
    n, crc, k1 = int.from_bytes(head[6:8], "little"), int.from_bytes(head[8:12], "little"), head[5]

    def ok(body, key):
        if len(key) != kl:
            return None
        x = _xor_rep(body, key)   # body = JSON ^ key, or JSON ^ header xor byte ^ key (stored key, k1 not folded in)
        for plain in (x, x.translate(bytes(c ^ k1 for c in range(256)))):
            if len(plain) == n and zlib.crc32(plain) == crc:
                return head + bytes(p ^ k1 for p in plain), key
        return None

    for kl in range(1, 17):
        for kat, bat in ((i + 12, i + 12 + kl), (i - kl, i + 12), (i + 12 + n, i + 12)):   # key stored next to it:
            r = ok(data[bat:bat + n], data[max(0, kat):kat + kl])   # between header and body / before magic / after
            if r:
                return r
        body, cols = data[i + 12:i + 12 + n], []
        if len(body) < max(n, 2 * kl):
            continue
        for j in range(kl):
            col, m = body[j::kl], -1
            for b in set(col):
                m &= _PMASK[b]
            # known plaintext of a JSON object: '{' first, '}' last, '"' second (compact) -- pinned / preferred
            pin = [x for x, at in ((body[0] ^ 0x7B, 0), (body[-1] ^ 0x7D, (n - 1) % kl)) if at == j]
            if pin:
                m &= 1 << pin[0] if all(x == pin[0] for x in pin) else 0
            if not m:
                break
            cand = sorted((k for k in range(256) if m >> k & 1),
                          key=lambda k, col=col: -sum(_JSONW.get(b ^ k, 0) for b in col))[:4]
            q = body[1] ^ 0x22
            if j == 1 % kl and q in cand[1:]:
                cand.remove(q)
                cand.insert(0, q)
            cols.append(cand)
        else:
            best = bytes(c[0] for c in cols)
            alts = [(j, alt) for j, c in enumerate(cols) for alt in c[1:]]
            tries = [best] + [best[:j] + bytes([alt]) + best[j + 1:] for j, alt in alts]
            tries += [bytes(alt if j == a else alt2 if j == a2 else c for j, c in enumerate(best))
                      for x, (a, alt) in enumerate(alts) for a2, alt2 in alts[x + 1:] if a2 != a][:400]
            for key in tries:
                r = ok(body, key)
                if r:
                    return r
    return None


_B64STD = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_B64ALPHA_CLS = bytes(int(c in b"+/-_.!~*$@#%&?:;," or chr(c).isalnum() and c < 0x80) for c in range(256))


def _b64_alphabets(data, budget, late):
    """64-char windows of 64 DISTINCT characters (custom base64 alphabets) in `data`: [(offset, alphabet)], at most 4 per
    run and 32 overall, skipping standard / url-safe ones (and their rotations); examines at most `budget` run characters. Runs of
    alphabet-class bytes via translate + find (a {64,} regex was 1.2 s / 67 MB); every 64-window contains a whole
    aligned 32-block, so only blocks of 32 distinct chars get the per-char sliding check."""
    out, seen = [], {_B64STD, _B64STD[:62] + b"-_"}
    t, ones = data.translate(_B64ALPHA_CLS), b"\x01" * 64
    p = t.find(ones)
    while p >= 0 and len(out) < 32:
        e = t.find(b"\0", p)
        e = len(data) if e < 0 else e
        run, wins = data[p:e], []
        budget -= len(run)
        if budget < 0 or late():
            break
        for k in range(0, len(run) - 31, 32):
            if len(set(run[k:k + 32])) < 32:
                continue
            base, last, lo = max(0, k - 32), {}, 0   # sliding window without repeats over [k-32, k+64)
            for j, c in enumerate(run[base:k + 64]):
                lo = max(lo, last.get(c, -1) + 1)
                last[c] = j
                if j - lo >= 63 and base + j - 63 not in wins:
                    wins.append(base + j - 63)
            if len(wins) >= 4:
                break
        for w in wins[:4]:
            a = run[w:w + 64]
            if a not in seen and a not in _B64STD * 2 and a not in (_B64STD[:62] + b"-_") * 2:   # std rotations
                seen.add(a)
                out.append((p + w, a))
        p = t.find(ones, e)
    return out[:32]


# byte-map transforms of the stored form: stored = t(x) for x = the raw blob ('<t>-raw'), its base64 text
# ('<t>-base64', transform AFTER base64) or base64 of t(blob) ('base64-<t>', transform BEFORE base64). t = nibswap,
# rol1-3/5-7 (rotate each byte left; rorN = rol(8-N), nibswap = rol4), not (raw/after-base64 NOT is xor 0xff: the
# single-byte xor pass reports those), add (stored = x + k mod 256, a 'sub k' = add 256-k; detail add=0xNN).
# Offset = first stored byte / char.
def _rolb(b, r):
    return ((b << r) | (b >> (8 - r))) & 0xFF


_BYTEID = bytes(range(256))
_BYTEMAPS = {"nibswap": bytes(_rolb(b, 4) for b in range(256)), "not": bytes(b ^ 0xFF for b in range(256))}
_BYTEMAPS.update((f"rol{r}", bytes(_rolb(b, r) for b in range(256))) for r in (1, 2, 3, 5, 6, 7))
_BYTEMAP_ANCHORS = {}   # stored anchor -> (name, inverse table, form)
for _n, _t in _BYTEMAPS.items():
    _inv = bytes.maketrans(_t, _BYTEID)
    if _n != "not":
        _BYTEMAP_ANCHORS[HCFG_MAGIC.translate(_t)] = (_n, _inv, "raw")
        _BYTEMAP_ANCHORS[b"SENGR".translate(_t)] = (_n, _inv, "after")
    _BYTEMAP_ANCHORS[base64.b64encode(HCFG_MAGIC.translate(_t))[:5]] = (_n, _inv, "before")
_BYTEMAP_RX = re.compile(_trie(list(_BYTEMAP_ANCHORS)))
HCFG_ADDK_MAX = int(os.environ.get("HCTF_HCFG_ADDK_MAX", str(96 << 20)))   # add-constant passes (~1 s / 67 MB)
_B64RUN = re.compile(rb"[A-Za-z0-9+/]{32,}")   # a header (16 chars) + any JSON body


def _subdiff(buf):
    """D with D[i] = (buf[i] - buf[i+1]) % 256 (key-free under a per-byte add): SWAR big-int lane subtraction."""
    n = len(buf)
    x, h = int.from_bytes(buf, "little"), int.from_bytes(b"\x80" * n, "little")
    y = x >> 8
    return ((((x | h) - (y & ~h)) ^ ((x ^ ~y) & h)) & ((1 << 8 * n) - 1)).to_bytes(n, "little")


def _diffpat(plain):
    return bytes((a - b) % 256 for a, b in zip(plain, plain[1:]))


def _bytemap_at(data, i, form, inv, name, emit, detail=""):
    """Undo the byte map `inv` on the stored form at data[i] (form raw / after / before base64) and emit the blob."""
    if form == "raw":
        emit(i, name + "-raw", data[i:i + _need(data[i:i + 8].translate(inv))].translate(inv), detail)
    elif form == "after":
        m = _B64.rx.match(data[i:i + 90000].translate(inv))
        r = _decode_text(_B64, re.sub(rb"[\r\n]", b"", m.group(0))) if m else None
        if r:
            emit(i, name + "-base64", r[0], detail)
    else:
        m = _B64.rx.match(data, i, i + 90000)
        run = re.sub(rb"[\r\n]", b"", m.group(0)) if m else b""
        try:
            head = _b64dec(run[:16]).translate(inv)
            blob = _b64dec(run[:_B64.chars(_need(head))]).translate(inv)
        except (binascii.Error, ValueError):
            return
        emit(i, "base64-" + name, blob, detail)


def _addk_scan(data, emit, late):
    """add/sub-constant stored forms: raw + after-base64 via the key-free byte difference of the file, before-base64 via
    the difference of every base64 run decoded at each of its 4 phases (runs joined per phase: one decode)."""
    diff = _subdiff(data)
    for plain, form in ((HCFG_MAGIC, "raw"), (b"SENGR", "after")):
        pat, i, n = _diffpat(plain), 0, 0
        i = diff.find(pat)
        while i >= 0 and n < 4096 and not late():
            k = (data[i] - plain[0]) % 256
            if k:
                _bytemap_at(data, i, form, bytes((b - k) % 256 for b in range(256)), "add", emit, f"add={k:#04x}")
            i, n = diff.find(pat, i + 1), n + 1
    runs = [m.span() for m in _B64RUN.finditer(data)]
    pat = _diffpat(HCFG_MAGIC)
    for ph in range(4):
        if late():
            return
        starts, segs, at = [], [], 0
        for a, b in runs:
            seg = (b - a - ph) // 4 * 4
            if seg >= 16:
                starts.append((at, a + ph))
                segs.append(data[a + ph:a + ph + seg])
                at += seg // 4 * 3
        dec = binascii.a2b_base64(b"".join(segs))
        diff = _subdiff(dec)
        j, n = diff.find(pat), 0
        while j >= 0 and n < 4096 and not late():
            if j % 3 == 0 and dec[j] != HCFG_MAGIC[0]:
                at, a = starts[bisect.bisect_right(starts, (j, float("inf"))) - 1]
                k = (dec[j] - HCFG_MAGIC[0]) % 256
                _bytemap_at(data, a + (j - at) // 3 * 4, "before", bytes((b - k) % 256 for b in range(256)), "add",
                            emit, f"add={k:#04x}")
            j, n = diff.find(pat, j + 1), n + 1


# Index-dependent xor of the whole stored blob (key from the known plaintext 'HCFG'; offset = first stored byte;
# crc-valid hits only): rollxor-raw stored[j] = blob[j] ^ (k0 + step*j) (key+i, key-i, any step != 0; detail
# key=0xNN step=0xNN), xoridx-raw stored[j] = blob[j] ^ k0 ^ j, xorcbc-raw stored[j] = blob[j] ^ stored[j-1] (ciphertext
# feedback, stored[-1] = k0), xorchain-raw stored[j] = blob[j] ^ blob[j-1] (plaintext feedback, blob[-1] = k0).
HCFG_ROLLXOR_MAX = int(os.environ.get("HCTF_HCFG_ROLLXOR_MAX", str(96 << 20)))   # rolling-xor pass (~0.6 s / 64 MB)
_XORIDX_PAT = bytes(HCFG_MAGIC[j] ^ HCFG_MAGIC[j + 1] ^ j ^ (j + 1) for j in range(3))
_XTBL = [bytes(c ^ k for c in range(256)) for k in range(256)]


def _crc_fast(blob):
    """_parse_blob's crc_ok via translate (no per-byte Python loop): random-candidate filter."""
    if len(blob) < 12 or blob[:4] != HCFG_MAGIC:
        return False
    _, key, n, crc = struct.unpack_from("<BBHI", blob, 4)
    return 0 < n == len(blob) - 12 and zlib.crc32(blob[12:].translate(_XTBL[key])) == crc


def _rollxor_scan(data, emit, late):
    def ks_try(s, ks, enc, detail):   # ks: the 256-periodic keystream from s
        need = _need(_xor_rep(data[s:s + 8], ks[:8]))
        blob = _xor_rep(data[s:s + need], ks) if s + need <= len(data) else b""
        if _crc_fast(blob):
            emit(s, enc, blob, detail)

    def fb_try(s, enc, cbc):   # feedback modes: blob[0] = 'H' fixes k0
        k0, head = data[s] ^ HCFG_MAGIC[0], data[s:s + 12]
        if len(head) < 12:
            return
        if cbc:
            dec = lambda c: bytes([c[0] ^ k0]) + _xorb(c[1:], c[:-1])
        else:   # prefix xor of k0 + stored: lane-wise doubling (xor carries nothing across bytes)
            def dec(c):
                x, sh = int.from_bytes(c, "little") ^ k0, 8
                while sh < 8 * len(c):
                    x, sh = x ^ (x << sh), sh * 2
                return (x & ((1 << 8 * len(c)) - 1)).to_bytes(len(c), "little")
        need = _need(dec(head))
        blob = dec(data[s:s + need]) if s + need <= len(data) else b""
        if _crc_fast(blob):
            emit(s, enc, blob, f"iv={k0:#04x}")

    pat = bytes(a ^ b for a, b in zip(HCFG_MAGIC, HCFG_MAGIC[1:]))   # plaintext feedback: stored[s+1..s+3]
    t, n = data.find(pat, 1), 0
    while t >= 1 and n < 4096 and not late():
        fb_try(t - 1, "xorchain-raw", False)
        t, n = data.find(pat, t + 1), n + 1
    # 1 MiB chunks (+3 bytes overlap), one big int each: diff[i] = stored[i] ^ stored[i+1] for xorcbc ('CFG') / xoridx;
    # rolling add key: k_j = stored[s+j] ^ 'HCFG'[j] has equal first differences (SWAR lane subtraction)
    size, cache, cand = 1 << 20, {}, [0, 0, 0]
    for lo in range(0, max(0, len(data) - 3), size):
        if late():
            return
        n = min(size, len(data) - 3 - lo)
        if n not in cache:
            m, h = (1 << 8 * n) - 1, int.from_bytes(b"\x80" * n, "little")
            cache[n] = m, h, m ^ h, [int.from_bytes(bytes([c]) * n, "little") for c in HCFG_MAGIC]
        m, h, nh, C = cache[n]
        x = int.from_bytes(data[lo:lo + n + 3], "little")
        diff = ((x ^ (x >> 8)) & (m << 16 | 0xFFFF)).to_bytes(n + 2, "little")   # patterns STARTING in the chunk
        for k, pat in enumerate((b"CFG", _XORIDX_PAT)):
            t = diff.find(pat, 0, n + 2)
            while 0 <= t < n and cand[k] < 4096:
                s, cand[k] = lo + t, cand[k] + 1
                if k == 0:
                    fb_try(s, "xorcbc-raw", True)
                else:
                    k0 = data[s] ^ HCFG_MAGIC[0]
                    ks_try(s, bytes(k0 ^ j for j in range(256)), "xoridx-raw", f"key={k0:#04x}")
                t = diff.find(pat, t + 1)
        X = [((x >> 8 * j) & m) ^ C[j] for j in range(4)]

        def sub(a, b):
            return ((a | h) - (b & nh)) ^ ((a ^ b ^ m) & h)
        d2 = sub(X[2], X[1])
        e = ((sub(X[1], X[0]) ^ d2) | (d2 ^ sub(X[3], X[2]))).to_bytes(n, "little")
        i = e.find(b"\0")
        while i >= 0 and cand[2] < 4096:
            s = lo + i
            k0, st = data[s] ^ HCFG_MAGIC[0], ((data[s + 1] ^ HCFG_MAGIC[1]) - (data[s] ^ HCFG_MAGIC[0])) & 255
            if st:   # step 0 = the single-byte xor pass
                cand[2] += 1
                ks_try(s, bytes((k0 + st * j) & 255 for j in range(256)), "rollxor-raw", f"key={k0:#04x} step={st:#04x}")
            i = e.find(b"\0", i + 1)


# Block / stream ciphers (D16 prep): AES-128/192/256 ECB/CBC/CTR, ChaCha20/Salsa20, XTEA ECB/CBC -- run only when the
# cipher's constants are in the file (AES S-box / inv S-box / Te0, TEA delta 0x9e3779b9 / -delta, 'expand 32-byte k').
# Keys: NUL-delimited strings (the string itself when 16/24/32 chars, its hex when 32/64 hex digits, sha256 / sha256[:16]
# / md5 of it; far from every constant hit: literal keys before derived ones), plus raw 16/32-byte keys (8-aligned)
# within 4 KB of a constant hit with the ciphertext right after them (or after a 16-byte IV after them). AES/ChaCha:
# ciphertext anywhere within 4 KB of a string key; XTEA: right after the key (or after an 8-byte IV). IV / nonce: zero,
# prepended to the ciphertext (CBC / CTR), the string or 16 raw bytes next to the key. crc-valid hits only; offset =
# first ciphertext byte (after a prepended IV); detail key=.. iv=.. / nonce=..
HCFG_BLOCK_KEYS = int(os.environ.get("HCTF_HCFG_BLOCK_KEYS", "500"))   # AES/ChaCha string keys tried (~0.6 ms each)
HCFG_XTEA_KEYS = int(os.environ.get("HCTF_HCFG_XTEA_KEYS", "150"))   # XTEA string keys tried (pure Python, ~0.2 ms each)
HCFG_BLOCK_SECS = float(os.environ.get("HCTF_HCFG_BLOCK_SECS", "1.5"))   # time box of the whole cipher pass
_BLK_WIN = 4096
_BLK_CONST = {bytes.fromhex("637c777bf26b6fc5"): "aes", bytes.fromhex("52096ad53036a538"): "aes",   # S-box, inv S-box
              bytes.fromhex("c66363a5f87c7c84"): "aes", bytes.fromhex("a56363c6847c7cf8"): "aes",   # Te0 BE / LE
              b"\xb9\x79\x37\x9e": "tea", b"\x9e\x37\x79\xb9": "tea", b"\x47\x86\xc8\x61": "tea",   # delta / -delta
              b"\x61\xc8\x86\x47": "tea", b"expand 32-byte k": "chacha", b"expand 16-byte k": "chacha"}
_BLK_HEX = re.compile(rb"(?:[0-9a-fA-F]{32}){1,2}")


def _xorb(a, b):
    n = min(len(a), len(b))
    return (int.from_bytes(a[:n], "little") ^ int.from_bytes(b[:n], "little")).to_bytes(n, "little")


def _find16(buf, pat, n, shift=0):
    """(alignment, block offset) of every block-aligned buf[p:p+len(pat)] == pat in a concatenation of n-byte segments
    (alignment a = segment index); shift=16: buf is xor'd against the previous block (skip segment-crossing pairs)."""
    p = buf.find(pat)
    while p >= 0:
        q = p + shift
        if p % 16 == 0 and not (shift and q % n == 0):
            yield q // n, q % n
        p = buf.find(pat, p + 1)


def _blk_crc_ok(blob):
    r = _parse_blob(blob)
    return bool(r and r[5])


def _aes_try(AES, data, key, lo, hi, ivs, emit, tag, aligns=tuple(range(16))):
    """AES ECB / CBC / CTR under `key`, ciphertext starting in [lo, hi); ivs = candidate 16-byte IVs / counter blocks.
    The window is decrypted / encrypted at every byte alignment in ONE call (segments concatenated)."""
    E, Z = AES.new(key, AES.MODE_ECB), bytes(16)
    ivs = [iv for iv in ivs if len(iv) == 16]
    cands = []   # (t, mode, iv)
    n = (min(hi + 32, len(data)) - lo - max(aligns)) // 16 * 16   # blocks starting in the window
    if n >= 16:
        segs = b"".join(data[lo + a:lo + a + n] for a in aligns)
        D, X = E.decrypt(segs), E.encrypt(segs)
        at = (lambda a, o: lo + aligns[a] + o)
        for a, o in _find16(D, HCFG_MAGIC, n):   # ECB / CBC with a zero IV
            cands += [(at(a, o), "ecb", Z), (at(a, o), "cbc", Z)]
        for iv in ivs:   # CBC with a stored IV
            if iv != Z:
                cands += [(at(a, o), "cbc", iv) for a, o in _find16(D, _xorb(HCFG_MAGIC, iv), n)]
        for a, o in _find16(_xorb(D[16:], segs), HCFG_MAGIC, n, 16):   # CBC, IV prepended to the ciphertext
            cands.append((at(a, o), "cbc", data[at(a, o) - 16:at(a, o)]))
        for a, o in _find16(_xorb(X, segs[16:]), HCFG_MAGIC, n, 16):   # CTR, initial counter block prepended
            cands.append((at(a, o), "ctr", data[at(a, o) - 16:at(a, o)]))
        cands = [c for c in cands if c[0] < hi]
    for iv in ivs:   # CTR with a stored / zero counter block (16-byte IV, or 8-byte nonce || 0 / 12-byte nonce || 1)
        pat = _xorb(HCFG_MAGIC, E.encrypt(iv))
        t = data.find(pat, lo, hi + 3)
        while 0 <= t < hi:
            cands.append((t, "ctr", iv))
            t = data.find(pat, t + 1, hi + 3)
    for t, mode, iv in cands:
        if mode == "ecb":
            head = E.decrypt(data[t:t + 16])
        elif mode == "cbc":
            head = _xorb(E.decrypt(data[t:t + 16]), iv)
        else:
            head = _xorb(data[t:t + 16], E.encrypt(iv))
        need = _need(head)
        ct = data[t:t + (need + 15) // 16 * 16]
        if len(ct) % 16 or len(ct) < need:
            continue
        if mode == "ecb":
            blob = E.decrypt(ct)
        elif mode == "cbc":
            blob = AES.new(key, AES.MODE_CBC, iv=iv).decrypt(ct)
        else:
            blob = AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=iv).decrypt(ct)
        if _blk_crc_ok(blob[:need]):
            emit(t, "aes-" + mode, blob[:need], f"{tag} iv={iv.hex()}")
            return True
    return False


def _chacha_try(mods, data, key, lo, hi, nonces, emit, tag):
    """ChaCha20 (8/12-byte nonce, block counter 0 or 1; a 16-byte nonce = RFC 7539 LE counter || 12-byte nonce) and
    Salsa20 (8-byte nonce) under a 32-byte key: keystream 'HCFG' -> one find in the window."""
    ChaCha20, Salsa20 = mods
    for nz in nonces:
        for name, mk in (("chacha20", lambda nz=nz: ChaCha20.new(key=key, nonce=nz)),
                         ("salsa20", lambda nz=nz: Salsa20.new(key=key, nonce=nz))):
            if (name == "salsa20" and len(nz) != 8) or len(nz) not in (8, 12, 16):
                continue
            for ctr in ((int.from_bytes(nz[:4], "little"),) if len(nz) == 16 else (0, 1)):
                def stream(n, ctr=ctr, nz=nz, mk=mk):
                    c = ChaCha20.new(key=key, nonce=nz[4:]) if len(nz) == 16 else mk()
                    if ctr:
                        c.seek(64 * ctr)
                    return c.encrypt(bytes(n))
                if name == "salsa20" and ctr:
                    continue
                ks = stream(8)
                pat = _xorb(HCFG_MAGIC, ks)
                t = data.find(pat, lo, hi + 3)
                while 0 <= t < hi:
                    need = _need(_xorb(data[t:t + 8], ks))
                    blob = _xorb(data[t:t + need], stream(need))
                    if len(blob) == need and _blk_crc_ok(blob):
                        emit(t, name, blob, f"{tag} nonce={nz.hex()} ctr={ctr}")
                        return True
                    t = data.find(pat, t + 1, hi + 3)
    return False


def _xtea_dec(key, blk, be):
    f = ">" if be else "<"
    k = struct.unpack(f + "4I", key)
    v0, v1 = struct.unpack(f + "2I", blk)
    s, d, m = (0x9E3779B9 * 32) & 0xFFFFFFFF, 0x9E3779B9, 0xFFFFFFFF
    for _ in range(32):
        v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + k[(s >> 11) & 3]))) & m
        s = (s - d) & m
        v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + k[s & 3]))) & m
    return struct.pack(f + "2I", v0, v1)


def _xtea_try(data, key, starts, emit, tag):
    """XTEA (32 cycles, LE or BE words) ECB / CBC (zero or prepended 8-byte IV) at the candidate ciphertext starts."""
    for t in starts:
        blk = data[t:t + 8]
        if len(blk) < 8:
            continue
        for be in (False, True):
            d0 = _xtea_dec(key, blk, be)
            for mode, iv in (("ecb", bytes(8)), ("cbc", data[max(0, t - 8):t])):
                if len(iv) < 8 or _xorb(d0, iv)[:4] != HCFG_MAGIC:
                    continue
                need = _need(_xorb(d0, iv))
                ct = data[t:t + (need + 7) // 8 * 8]
                if len(ct) % 8 or len(ct) < need:
                    continue
                out, prev = bytearray(), iv
                for j in range(0, len(ct), 8):
                    c = ct[j:j + 8]
                    out += _xorb(_xtea_dec(key, c, be), prev if mode == "cbc" else bytes(8))
                    prev = c
                if _blk_crc_ok(bytes(out[:need])):
                    emit(t, "xtea-" + mode, bytes(out[:need]), f"{tag} {'be' if be else 'le'}"
                         + (f" iv={iv.hex()}" if mode == "cbc" else ""))
                    return True
    return False


def _block_scan(data, emit, late):
    """AES / ChaCha20 / Salsa20 / XTEA pass (see the block comment above); True once a crc-valid blob was emitted."""
    import hashlib
    try:
        from Crypto.Cipher import AES, ChaCha20, Salsa20
    except Exception:  # noqa: BLE001 - no pycryptodome: XTEA only
        AES = ChaCha20 = Salsa20 = None
    hits = {}
    for c, kind in _BLK_CONST.items():   # one bytes.find per constant (~10 ms / 40 MB; a regex alternation was 0.5 s)
        i, n = data.find(c), 0
        while i >= 0 and n < 64:
            hits.setdefault(kind, []).append(i)
            i, n = data.find(c, i + 1), n + 1
    for v in hits.values():
        v.sort()
    if not hits or (AES is None and "tea" not in hits):
        return False
    box, outer = time.time() + HCFG_BLOCK_SECS, late
    late = (lambda: outer() or time.time() > box)
    near = sorted(o for v in hits.values() for o in v[:16])
    strs = []
    for m in _RC4_KEY.finditer(data):
        s, o = m.group(1), m.start(1)
        j = bisect.bisect_left(near, o - 2 * _BLK_WIN)
        strs.append((not (j < len(near) and near[j] <= o + 2 * _BLK_WIN), len(strs), s, o, m.end() + 1))
    strs.sort()
    by_off = sorted((o, s) for _, _, s, o, _ in strs)
    offs = [o for o, _ in by_off]
    nkeys = nxtea = 0

    def jobs():   # strings near a constant hit: every key; then far strings' literal keys; then their derived keys
        for tier in (0, 1, 2):
            for far, _, s, o, e in strs:
                if far != (tier > 0):
                    continue
                keys = []
                if tier < 2 and len(s) in (16, 24, 32):
                    keys.append(("str", s))
                if tier < 2 and _BLK_HEX.fullmatch(s):
                    keys.append(("hex", binascii.unhexlify(s)))
                if tier != 1:
                    h = hashlib.sha256(s).digest()
                    keys += [("sha256", h), ("sha256[:16]", h[:16]), ("md5", hashlib.md5(s).digest())]
                if keys:
                    yield s, o, e, keys

    for s, o, e, keys in jobs():
        if late() or (nkeys >= HCFG_BLOCK_KEYS and nxtea >= HCFG_XTEA_KEYS):
            break
        lo, hi = max(0, o - _BLK_WIN), min(len(data), e + _BLK_WIN)
        j = bisect.bisect_left(offs, o)
        neigh = [by_off[x][1] for x in (j - 1, j + 1) if 0 <= x < len(by_off) and abs(by_off[x][0] - o) <= 256]
        raw16 = [data[e:e + 16], data[max(0, o - 17):o - 1]]
        for how, key in keys:
            tag = f"key={how}({s.decode('latin-1')!r}) key@{o}"
            if AES is not None and "aes" in hits and nkeys < HCFG_BLOCK_KEYS:
                nkeys += 1
                ivs = [bytes(16)] + [v for v in neigh + raw16 if len(v) == 16]
                ivs += [v + bytes(8) for v in neigh if len(v) == 8] + [v + b"\0\0\0\1" for v in neigh if len(v) == 12]
                if _aes_try(AES, data, key, lo, hi, list(dict.fromkeys(ivs)), emit, tag):
                    return True
            if AES is not None and "chacha" in hits and len(key) == 32 and nkeys < HCFG_BLOCK_KEYS:
                nkeys += 1
                nz = [bytes(8), bytes(12)] + [v for v in neigh + raw16 if len(v) in (8, 12, 16)]
                nz += [v[:12] for v in raw16] + [v[:8] for v in raw16]
                if _chacha_try((ChaCha20, Salsa20), data, key, lo, hi, list(dict.fromkeys(nz)), emit, tag):
                    return True
            if "tea" in hits and len(key) == 16 and nxtea < HCFG_XTEA_KEYS:
                nxtea += 1
                starts = {e, (e + 7) & ~7, e + 8, ((e + 7) & ~7) + 8}
                if _xtea_try(data, key, sorted(starts), emit, tag):
                    return True
    # raw 16/32-byte keys stored next to the ciphertext, within 4 KB of a constant hit
    for kind, offs_ in hits.items():
        if kind == "aes" and AES is None:
            continue
        for c in offs_[:2 if kind == "tea" else 4]:
            for k in range(max(0, c - _BLK_WIN) & ~7, min(len(data), c + _BLK_WIN), 8):
                if late():
                    return False
                for kl in ((16,) if kind == "tea" else (32,) if kind == "chacha" else (16, 32)):
                    key = data[k:k + kl]
                    if len(key) < kl or len(set(key)) < kl * 5 // 8:
                        continue
                    e, tag = k + kl, f"key=raw key@{k}"
                    if kind == "aes":
                        iv = data[e:e + 16]
                        if _aes_try(AES, data, key, e, e + 17, [bytes(16), iv], emit, tag, (0,)):   # [key][iv?][ct]
                            return True
                    elif kind == "chacha":
                        if any(_chacha_try((ChaCha20, Salsa20), data, key, e + d, e + d + 1, [data[e:e + d]], emit, tag)
                               for d in (12, 8)) or \
                                _chacha_try((ChaCha20, Salsa20), data, key, e, e + 1, [bytes(12)], emit, tag):
                            return True
                    elif _xtea_try(data, key, [e, e + 8], emit, tag):
                        return True
    return False


def hcfg_scan(data, *, deadline=None, ext=None, stop_on_valid=False, _depth=0):
    """Every HCFG blob in `data` (any storage encoding), best first: crc-valid + parsed JSON, then GM-confirmed
    encodings (raw, base64), then file order. Decoys (bad crc, truncated, unparsable JSON) are returned too with
    crc_ok/valid False -- callers take `next(h for h in hits if h.valid)`. Offsets follow the OFFSET LAW above.

    Bounded: cheap anchor finds first (encoded forms of the magic), then -- only while no valid blob was found -- the
    xor'd base64/raw pass (one big-int xor of the file, ~10 ms / 4 MB) and the headerless raw-deflate brute force
    (files <= HCTF_HCFG_DEFLATE_MAX, default 1 MiB). `deadline` (epoch seconds; HCTF_SOLVE_DEADLINE also honoured)
    stops the expensive passes early. ext=False (or HCTF_HCFG_SCAN_EXT=0): raw/base64/base64url/plain hex only (= the
    D13 solver's encodings)."""
    data = bytes(data)
    ext = HCFG_SCAN_EXT if ext is None else ext
    end = _ends(deadline)
    late = (lambda: end is not None and time.time() > end)
    hits, seen = [], set()

    def emit(off, enc, blob, detail=""):
        r = _parse_blob(blob)
        if r and (off, enc) not in seen and (ext or enc in _LEGACY):
            seen.add((off, enc))
            ver, key, n, crc, plain, ok, cfg = r
            hits.append(HcfgHit(off, enc, ver, key, n, crc, ok, cfg, plain, enc not in _CONFIRMED, detail))

    def valid():
        return any(h.valid for h in hits)

    def done():
        return stop_on_valid and valid()

    # ONE regex pass over the file finds every anchor (one bytes.find per anchor was ~2 ms / 4 MB each, ~38 ms total)
    mv = memoryview(data)
    u16_runs, zbudget = set(), [16 << 20]   # zbudget: total inflate output for streams that merely CONTAIN the blob
    ibudget = [256]   # int-array / word-swap candidates decoded
    for m in _ANCHORS.finditer(data):
        i, a = m.start(), m.group(0)
        kind = _ANCHOR_KIND.get(a, "hex")
        if not ext and kind not in ("raw", "hex") and _ANCHOR_CODEC.get(a) is not _B64:
            continue   # kill-switch: the D13 solver's encodings only (raw, base64/url, hex)
        if kind == "raw":
            blob = data[i:i + _need(data[i:i + 8])]
            emit(i, "raw", blob)
            if ext and not (_parse_blob(blob) or (0,) * 6)[5]:   # big-endian len/crc header (BE target's C struct)
                be = _be_raw_at(data, i)
                if be:
                    emit(i, "raw-be", be)
        elif kind == "hex":
            _hex_at(data, i, emit)
        elif kind == "text":
            _text_at(data, i, _ANCHOR_CODEC[a], emit)
        elif kind == "rev-raw":   # 'GFCH' = the last 4 bytes of the reversed blob
            e = i + 4
            if e >= 12:
                st = max(0, e - _need(data[e - 12:e][::-1]))
                emit(st, "reversed-raw", data[st:e][::-1])
            _swapped_at(data, i, 4, emit, ibudget)       # uint32 words 0x48434647 stored LE
            _swapped_at(data, i - 4, 8, emit, ibudget)   # uint64 words 0x48434647vvkkllll stored LE
        elif kind == "wide":      # uint32/uint64 element per blob byte
            _wide_at(data, i, (len(a) - 1) // 3, emit, ibudget)
        elif kind == "swap16":    # uint16 words 0x4843 0x4647 stored LE
            _swapped_at(data, i, 2, emit, ibudget)
        elif kind == "rev-b64":   # 'RGNES' = the last 5 chars of the reversed base64 text
            e = i + 5
            mm = _B64REV.match(data[max(0, e - 90000):e][::-1])   # reversed window: a linear forward match
            run = mm.group(0) if mm else b""
            r = _decode_text(_B64, run)
            if r:   # stored text starts with the '=' padding that ends the (un-reversed) base64
                tail = run[r[1]:r[1] + 2]
                emit(e - r[1] - (len(tail) - len(tail.lstrip(b"="))), "reversed-base64", r[0])
            _rotb64_at(data, i, a, emit)   # the same text reversed per LINE (multi-line only)
        elif kind == "u16raw":    # 'H\0C\0F\0G' (LE at i, BE at i-1): latin-1 widened raw blob
            for be, st in ((False, i), (True, i - 1)):
                if st < 0 or (be and data[st] != 0) or (not be and data[i + 7:i + 8] != b"\0"):
                    continue
                head = data[st:st + 24][1::2] if be else data[st:st + 24][0::2]
                span = data[st:st + 2 * _need(head)]
                hi, lo = (span[0::2], span[1::2]) if be else (span[1::2], span[0::2])
                if not hi.strip(b"\0"):
                    emit(st, ("utf16be-" if be else "utf16le-") + "raw", lo)
        elif kind == "u16text":   # widened text anchor: narrow the whole UTF-16 run, decode it as text
            for be, st in ((False, i), (True, i - 1)):
                if st < 0 or (be and data[st] != 0):
                    continue
                while st >= 2 and i - st < 6 and (data[st - 2] == 0 and 9 <= data[st - 1] <= 0x7e if be
                                                  else data[st - 1] == 0 and 9 <= data[st - 2] <= 0x7e):
                    st -= 2
                if (st, be) in u16_runs:
                    continue
                u16_runs.add((st, be))
                run = (_U16BE if be else _U16LE).match(data, st)
                if run:
                    narrow = run.group(0)[1::2] if be else run.group(0)[0::2]
                    _text_hits(narrow, lambda o, e, b, d="", st=st: emit(st + 2 * o, e, b, d),
                               "utf16be-" if be else "utf16le-")
        else:                     # compressed stream header: zlib / gzip / fixed-Huffman raw deflate
            wbits, name = _ANCHOR_Z[a]
            r = _inflate(mv, i, wbits, zbudget)
            if r:
                emit(i, name, r[0], f"at+{r[1]}" if r[1] else "")
        if late() or done():
            break
    if not ext or done():
        return _rank(hits)
    # expensive passes, only while nothing valid was found
    if not valid() and not late() and _depth == 0 and data[:4] == b"\0asm":
        # wasm: blob split over adjacent data segments / placed by memory.init / built by const stores -> linear memory
        _wasm_mem_scan(data, emit, deadline, _depth)
    if not valid() and not late() and _depth == 0 and _BC_MAGIC in data:
        # LLVM bitcode (.bc / wrapper / embedded .llvmbc): string constants are bit-packed, never verbatim in the file
        _bitcode_scan(data, emit, deadline, _depth)
    if not valid() and not late() and _depth < 2 and b"PK\x05\x06" in data[-65600:]:
        # jar/zip/apk: a compressed NON-class entry (config.bin, assets/...) the deflate anchors/brute miss (dynamic
        # Huffman in a > 1 MiB jar, or a text form inside) -> inflate it and look inside (offsets: OFFSET LAW)
        _zip_scan(data, emit, hits, deadline, late, _depth)
    if not valid() and not late() and _depth < 2 and _BUNDLE_SIG in data:
        # .NET single-file bundle with EnableCompressionInSingleFile: each entry (app dll, config) is raw deflate
        _bundle_scan(data, emit, hits, deadline, late, _depth)
    if not valid() and not late():
        # base64/hex text of a zlib/gzip/xz/bz2/lzma stream, or an xz/bz2/lzma stream raw in the file (offset = first
        # stored byte of the text / stream; detail at+N when the blob sits further into the output)
        for needle, back, form in _ZPACK:
            i, n = data.find(needle), 0
            while i >= 0 and n < 4096 and zbudget[0] > 0 and not late():
                if i >= back:
                    _zpack_at(data, i - back, form, emit, zbudget)
                i, n = data.find(needle, i + 1), n + 1
            if valid() or late():
                break
    if not valid() and not late():
        # ROT13 / case-swapped base64, optionally reversed per line: one bytes.find per transformed 'SENGR' (kept out
        # of the anchor regex -- first bytes e/r/s/f made that pass ~33% slower)
        for a in [a for a in _ROTB64 if a != b"RGNES"]:
            i = data.find(a)
            while i >= 0 and not late():
                _rotb64_at(data, i, a, emit)
                i = data.find(a, i + 1)
    if not valid() and not late():
        # decimal char-code list '72,67,70,71,...' (C/JS/Python source, String.fromCharCode, config text)
        for n, m in enumerate(_DEC_ANCHOR.finditer(data)):
            if late() or n >= 256:
                break
            _decimal_at(data, m.start(), emit)
    if not valid() and not late():
        # base64/base32/hex text split across several adjacent literals (NUL / padding / short separators between)
        for a, codec in _SPLIT:
            i, n = data.find(a), 0
            while i >= 0 and n < 256 and not late():   # cap: anchor floods (decoy tables) stay bounded
                _split_at(data, i, codec, emit)
                i, n = data.find(a, i + 1), n + 1
            if valid():
                break
    if not valid() and not late():
        # raw blob cut into consecutive NUL-terminated literals (GnuCOBOL PIC X VALUE fields, C char[][k] tables)
        i, n, left = data.find(HCFG_MAGIC), 0, [8192]
        while i >= 0 and n < 256 and left[0] > 0 and not late():
            _split_raw_at(data, i, emit, left)
            i, n = data.find(HCFG_MAGIC, i + 1), n + 1
            if valid():
                break
    if not valid() and not late() and len(data) <= HCFG_STRIDE_MAX:
        # every k-th byte (junk filler) / zipped halves / even-then-odd bytes of the blob or its base64
        _stride_scan(data, emit, late)
    if not valid() and not late():
        # blob assembled at runtime by mov-immediate stores / pushes: emulate the builder from its first 'H' store
        _stack_scan(data, emit, late)
    if not valid() and not late():
        # GnuCOBOL WORKING-STORAGE VALUE init: movabs / movdqa-from-.rodata stores between two PLT calls
        _cob_store_scan(data, emit, late)
    if not valid() and not late():
        # single-byte xor of the stored form: x[i]^x[i+1] is key-independent -> find the xor-diff of 'SENGR' / 'HCFG'
        x = int.from_bytes(data, "little")
        diff = (x ^ (x >> 8)).to_bytes(len(data), "little")
        for plain, name in ((b"SENGR", "xor-base64"), (HCFG_MAGIC, "xor-raw")):
            pat = bytes(a ^ b for a, b in zip(plain, plain[1:]))
            i = diff.find(pat)
            while i >= 0 and not late():
                k = data[i] ^ plain[0]
                if k:
                    tbl = bytes(c ^ k for c in range(256))
                    if name == "xor-raw":
                        n = _need(data[i:i + 12].translate(tbl))
                        emit(i, name, data[i:i + n].translate(tbl), f"xor={k:#04x}")
                    else:
                        m = _B64.rx.match(data[i:i + 90000].translate(tbl))
                        r = _decode_text(_B64, re.sub(rb"[\r\n]", b"", m.group(0))) if m else None
                        if r:
                            emit(i, name, r[0], f"xor={k:#04x}")
                i = diff.find(pat, i + 1)
    if not valid() and not late():
        # nibble swap / rotate-left / NOT of the raw blob, of its base64 text, or before base64: one anchor regex pass
        for n, m in enumerate(_BYTEMAP_RX.finditer(data)):
            if n >= 4096 or late():
                break
            name, inv, form = _BYTEMAP_ANCHORS[m.group(0)]
            _bytemap_at(data, m.start(), form, inv, name, emit)
    if not valid() and not late():
        # repeating 1-16 byte xor of the BODY under a plain header (a raw hit whose crc failed): key from known plaintext
        for h in [h for h in hits if h.encoding == "raw" and not h.crc_ok][:64]:
            r = _mxor_body(data, h.offset)
            if r:
                emit(h.offset, "multixor-body", r[0], f"key={r[1].hex()}")
            if valid() or late():
                break
    if not valid() and not late() and len(data) <= HCFG_MXOR_MAX:
        # whole blob ^ repeating 2-16 byte key stored right BEFORE it: data[t]^data[t+L] is key-free over [key][blob^key]
        x = int.from_bytes(data, "little")
        for kl in (4, 8, 16, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15):
            if late():
                break
            pat = bytes(HCFG_MAGIC[j] ^ (HCFG_MAGIC[j - kl] if j >= kl else 0) for j in range(4))
            diff = (x ^ (x >> 8 * kl)).to_bytes(len(data), "little")
            t = diff.find(pat)
            while 0 <= t and not late():
                key, s = data[t:t + kl], t + kl
                blob = _xor_rep(data[s:s + _need(_xor_rep(data[s:s + 12], key))], key)
                if any(key) and (_parse_blob(blob) or (0,) * 6)[5]:   # crc-valid only: zero runs match trivially
                    emit(s, "multixor-raw", blob, f"key={key.hex()} key@{t}")
                t = diff.find(pat, t + 1)
            if valid():
                break
    if not valid() and not late():
        # base64 under a custom alphabet stored as a 64-char literal: map 'SENGR' through it, decode back to standard
        for aoff, alpha in _b64_alphabets(data, HCFG_B64ALPHA_MAX, late):
            anchor, back = b"SENGR".translate(bytes.maketrans(_B64STD, alpha)), bytes.maketrans(alpha, _B64STD)
            rx = re.compile(b"[" + b"".join(re.escape(bytes([c])) for c in alpha) + rb"\r\n]+")
            i = data.find(anchor)
            while i >= 0 and not late():
                m = rx.match(data, i, i + 90000)
                r = _decode_text(_B64, re.sub(rb"[\r\n]", b"", m.group(0)).translate(back))
                if r:
                    emit(i, "base64-custom", r[0], f"alphabet@{aoff}")
                i = data.find(anchor, i + 1)
            if valid() or late():
                break
    if ext and not valid() and not late():
        # UPX'd program (magic maybe scrubbed): the blob is compressed -> scan the pure-Python `upx -d` image; the
        # offset is in the UNPACKED image (encoding "upx-<inner>")
        img = upx_unpack(data, deadline=deadline) if len(data) >= 0x200 else None
        for h in hcfg_scan(img, deadline=deadline, stop_on_valid=True) if img else ():
            if h.valid:
                h.encoding, h.detail = "upx-" + h.encoding, ("upx " + h.detail).strip()
                hits.append(h)
                break
    if not valid() and not late():
        # RC4 under a C-string key stored within 4 KB: the key's keystream gives the stored form of 'HCFG' (whole blob
        # encrypted) -> one bytes.find in the window; or a plain header (raw hit, crc failed) over an RC4'd body
        bodies = [h for h in hits if h.encoding == "raw" and not h.crc_ok][:64]
        ks_of = {}
        for n, m in enumerate(_RC4_KEY.finditer(data)):
            if n >= HCFG_RC4_KEYS or late():
                break
            key, lo, hi = m.group(1), max(0, m.start(1) - 4096), m.end() + 4096
            ks = ks_of.get(key) or _rc4(key, bytes(8))
            if len(ks_of) < 1 << 16:
                ks_of[key] = ks
            pat = bytes(a ^ b for a, b in zip(HCFG_MAGIC, ks))
            t = data.find(pat, lo, hi)
            while t >= 0:
                blob = _rc4(key, data[t:t + _need(bytes(a ^ b for a, b in zip(data[t:t + 8], ks)))])
                if (_parse_blob(blob) or (0,) * 6)[5]:   # crc-valid only
                    emit(t, "rc4", blob, f"key={key.decode('latin-1')!r} key@{m.start(1)}")
                t = data.find(pat, t + 1, hi)
            for h in bodies:
                if lo <= h.offset < hi:
                    head = data[h.offset:h.offset + 12]
                    dec = _rc4(key, data[h.offset + 12:h.offset + 12 + h.length])
                    for plain in (dec, bytes(b ^ h.key for b in dec)):   # header xor byte applied before / not at all
                        if len(plain) == h.length and zlib.crc32(plain) == h.crc:
                            emit(h.offset, "rc4-body", head + bytes(b ^ h.key for b in plain),
                                 f"key={key.decode('latin-1')!r} key@{m.start(1)}")
                            break
            if valid():
                break
    if not valid() and not late():
        # AES ECB/CBC/CTR, ChaCha20/Salsa20, XTEA: only when the cipher's constants are in the file (see _block_scan)
        try:
            _block_scan(data, emit, late)
        except Exception:  # noqa: BLE001 - a malformed / hostile input never raises past the scan
            pass
    if not valid() and not late() and len(data) <= HCFG_ADDK_MAX:
        # add/sub a constant per byte (raw, after or before base64): key-free byte differences
        _addk_scan(data, emit, late)
    if not valid() and not late() and len(data) <= HCFG_ROLLXOR_MAX:
        # index-dependent xor (key+i / key-i / key^i / ciphertext or plaintext feedback): known-plaintext 'HCFG'
        _rollxor_scan(data, emit, late)
    if not valid() and not late() and len(data) <= HCFG_DEFLATE_BRUTE_MAX:
        # headerless dynamic-Huffman deflate (what zlib emits for a ~400 B blob): try every plausible block start
        for m in _DEFLATE_DYN.finditer(data):
            if late():
                break
            r = _inflate(mv, m.start(), -15)
            if r:
                emit(m.start(), "deflate", r[0])
                if valid():
                    break
    if not valid() and not late():
        # decoded at load time by an ELF .init_array constructor: emulate the constructors (see _ctor_scan)
        _ctor_scan(data, emit, late)
    return _rank(hits)


HCFG_STRIDE_MAX = int(os.environ.get("HCTF_HCFG_STRIDE_MAX", str(96 << 20)))   # strided passes (~0.2 s / 70 MB)
# blob byte (or base64 char) every k-th byte, ANY filler between ('H?C?F?G'): zero-filled strides are already the
# u32/u64-array and UTF-16/32 anchors; this is the junk-filled / odd-stride / interleaved-halves form
_STRIDES = (2, 4, 3, 8)
_STRIDE_RX = [(k, form, re.compile(b"".join(re.escape(bytes([c])) + (b"." * (k - 1) if j < len(a) - 1 else b"")
                                            for j, c in enumerate(a)), re.S))
              for k in _STRIDES for a, form in ((HCFG_MAGIC, "raw"), (b"SENGR", "base64"))]


def _deinterleave(s, h):
    """Undo zip-interleaving of blob[:h] and blob[h:] (A0 B0 A1 B1 ..., the longer half's tail appended)."""
    m = min(h, len(s) - h)
    a, b = s[0:2 * m:2], s[1:2 * m:2]
    return a + (s[2 * m:] if h > m else b"") + b + (s[2 * m:] if len(s) - h > m else b"")


def _stride_scan(data, emit, late):
    """Strided storage, crc-valid hits only (any filler matches trivially): every k-th byte of the raw blob or of its
    base64 text (k = 2/3/4/8, offset = first stored byte); stride-2 'H?C?F?G' read as the two blob halves zipped
    together; 'HF' = the blob's even bytes followed by its odd bytes."""
    def ok(blob):
        return (_parse_blob(blob) or (0,) * 6)[5]
    for k, form, rx in _STRIDE_RX:
        for n, m in enumerate(rx.finditer(data)):
            if n >= 4096 or late():
                return
            i = m.start()
            if form == "base64":
                mm = _B64.rx.match(data[i:i + 90000 * k:k])
                r = _decode_text(_B64, re.sub(rb"[\r\n]", b"", mm.group(0))) if mm else None
                if r and ok(r[0]):
                    emit(i, f"stride{k}-base64", r[0], f"stride={k}")
                continue
            t = _need(data[i:i + 8 * k:k])
            blob = data[i:i + t * k:k]
            if ok(blob):
                emit(i, f"stride{k}-raw", blob, f"stride={k}")
            elif k == 2:
                for h in sorted({t // 2, (t + 1) // 2}, reverse=True):
                    blob = _deinterleave(data[i:i + t], h)
                    if ok(blob):
                        emit(i, "interleaved-halves", blob, f"half={h}")
                        break
    i, n = data.find(b"HF"), 0
    while i >= 0 and n < 1 << 16 and not late():
        for hi in range(4):   # body < 1 KiB: the length's high byte sits in the odd half
            t = 12 + data[i + 3] + 256 * hi if i + 3 < len(data) else 0
            e = (t + 1) // 2
            if t and data[i + e:i + e + 2] == b"CG" and data[i + e + 3:i + e + 4] == bytes([hi]):
                blob = bytearray(t)
                blob[0::2], blob[1::2] = data[i:i + e], data[i + e:i + t]
                if ok(bytes(blob)):
                    emit(i, "even-odd-split", bytes(blob), f"half={e}")
        i, n = data.find(b"HF", i + 1), n + 1


HCFG_STACK_SITES = int(os.environ.get("HCTF_HCFG_STACK_SITES", "64"))   # builder sites emulated (~3-5 ms each)
# x86 mov-immediate store to any [base(+sib)(+disp)] (REX optional) ending in the immediate byte; matched BACKWARD from
# a literal find (a leading class in a 64 MB regex scan costs ~2 s): movb $0x48 directly followed by the next movb
_STK_X86_MODRM = rb"(?:[\x00-\x03\x06\x07]|\x04.|\x05....|[\x40-\x43\x45-\x47].|\x44..|[\x80-\x83\x85-\x87]....|\x84.....)"
_STK_X86B = re.compile(rb"[\x40-\x4f]?\xc6" + _STK_X86_MODRM + rb"\Z", re.S)        # movb up to (excl.) the imm
_STK_X86L = re.compile(rb"[\x40-\x4f]?\xc7" + _STK_X86_MODRM + rb"\Z", re.S)        # movl/movq imm32 up to the imm
_STK_X86N = re.compile(rb"[\x40-\x4f]?\xc6" + _STK_X86_MODRM + rb"C", re.S)         # the next store: movb $0x43
_STK_A64 = (b"\x09\x80\x52", b"\x09\x80\xd2", b"\x69\x88\x52", b"\x69\x88\xd2")   # movz wN/xN, #0x48 / #0x4348 (bytes 1-3)
_STK_A64_C = re.compile(rb"[\x60-\x7e]\x08\x80[\x52\xd2]")   # movz #0x43: the 'C' that follows a byte-wise 'H'



def _arch_of(data):
    """'x86-64' / 'x86' / 'aarch64' from the ELF / PE / Mach-O header, None if unknown (try both families)."""
    try:
        if data[:4] == b"\x7fELF":
            m = int.from_bytes(data[18:20], "little" if data[5] == 1 else "big")
            return {0x3e: "x86-64", 3: "x86", 0xb7: "aarch64"}.get(m)
        if data[:2] == b"MZ":
            pe = int.from_bytes(data[0x3c:0x40], "little")
            if data[pe:pe + 4] == b"PE\0\0":
                return {0x8664: "x86-64", 0x14c: "x86", 0xaa64: "aarch64"}.get(int.from_bytes(data[pe + 4:pe + 6], "little"))
        if data[:4] == b"\xcf\xfa\xed\xfe":
            return {0x01000007: "x86-64", 0x0100000c: "aarch64"}.get(int.from_bytes(data[4:8], "little"))
    except (IndexError, ValueError):
        pass
    return None


# Machine labels beyond lib.knowledge's 4 (x86-64/x86/AArch64/ARM = the GM-confirmed vocabulary, kept). Others are
# GNU readelf's `Machine:` spelling (SPECULATIVE, not GM-verified). kind:integer -> answer "e_machine" (decimal).
ELF_MACHINE_LABEL = {2: "Sparc", 3: "x86", 4: "MC68000", 8: "MIPS R3000", 10: "MIPS R4000 big-endian",
                     18: "Sparc v8+", 20: "PowerPC", 21: "PowerPC64", 22: "IBM S/390", 40: "ARM", 43: "Sparc v9",
                     50: "Intel IA-64", 62: "x86-64", 183: "AArch64", 243: "RISC-V", 247: "Linux BPF",
                     258: "LoongArch"}
PE_MACHINE_LABEL = {0x14c: "i386", 0x8664: "x86-64", 0xaa64: "AArch64", 0x1c0: "ARM", 0x1c4: "ARM", 0x166: "MIPS",
                    0x1f0: "PowerPC", 0x1f1: "PowerPC", 0x200: "Intel IA-64", 0x5032: "RISC-V", 0x5064: "RISC-V",
                    0x5128: "RISC-V"}   # 0x14c "i386" GM-confirmed (Day 3); 0x1c4 = ARMNT (Thumb-2)
MACHO_CPU_LABEL = {7: "x86", 0x01000007: "x86-64", 12: "ARM", 0x0100000c: "AArch64", 0x0200000c: "AArch64",
                   18: "PowerPC", 0x01000012: "PowerPC64"}


def machine_facts(data):
    """{format, machine, machine_num (decimal str: ELF e_machine / PE Machine / Mach-O cputype), endian, bits} from
    the header bytes alone (any byte order, ET_REL .o included); None if not an ELF / PE / Mach-O. Unknown numbers
    keep machine = the number as a string."""
    try:
        if data[:4] == b"\x7fELF" and data[5:6] in (b"\x01", b"\x02") and len(data) >= 20:
            end = "little" if data[5] == 1 else "big"
            m = int.from_bytes(data[18:20], end)
            return {"format": "elf", "machine": ELF_MACHINE_LABEL.get(m, str(m)), "machine_num": str(m),
                    "endian": end, "bits": 64 if data[4] == 2 else 32}
        if data[:2] == b"MZ" and len(data) >= 0x40:
            pe = int.from_bytes(data[0x3c:0x40], "little")
            if data[pe:pe + 4] == b"PE\0\0" and len(data) >= pe + 26:
                m = int.from_bytes(data[pe + 4:pe + 6], "little")
                magic = int.from_bytes(data[pe + 24:pe + 26], "little")
                return {"format": "pe", "machine": PE_MACHINE_LABEL.get(m, f"0x{m:x}"), "machine_num": str(m),
                        "endian": "little", "bits": 64 if magic == 0x20b else 32}
            return None
        mo = {b"\xce\xfa\xed\xfe": ("little", 32), b"\xcf\xfa\xed\xfe": ("little", 64),
              b"\xfe\xed\xfa\xce": ("big", 32), b"\xfe\xed\xfa\xcf": ("big", 64)}.get(bytes(data[:4]))
        if data[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):   # fat/fat64: first slice (Java .class shares 0xcafebabe)
            lay = macho_layout(data)
            return machine_facts(data[lay["slices"][0]["slice_offset"]:]) if lay else bytecode_facts(data)
        if mo and len(data) >= 8:
            m = int.from_bytes(data[4:8], mo[0])
            return {"format": "mach-o", "machine": MACHO_CPU_LABEL.get(m, str(m)), "machine_num": str(m),
                    "endian": mo[0], "bits": mo[1]}
        if data[:4] == b"\0asm":   # WebAssembly: no machine number; wasm32 unless a memory is memory64
            lay = wasm_layout(data)
            if lay:
                return {"format": "wasm", "machine": lay["machine"], "machine_num": "none", "endian": "little",
                        "bits": 64 if lay["machine"] == "wasm64" else 32}
        return bytecode_facts(data)
    except (IndexError, ValueError, TypeError):
        pass
    return None


# Bytecode containers (group members next to native builds). Labels SPECULATIVE (GM vocabulary not seen): format is
# the first of `format_candidates`; machine/machine_num "none" (VM bytecode has no target; an Apple bitcode wrapper's
# cputype -> MACHO_CPU_LABEL). pyc: the version whose FINAL magic it is (CPython Lib/importlib/_bootstrap_external.py).
PYC_MAGIC_VERSION = {3379: "3.6", 3394: "3.7", 3413: "3.8", 3425: "3.9", 3439: "3.10", 3495: "3.11", 3531: "3.12",
                     3571: "3.13", 3627: "3.14"}
_BYTECODE_CANDIDATES = {"llvm_bitcode": ["llvm_bitcode", "bitcode", "llvm-bc", "bc"], "pyc": ["pyc", "python_bytecode"],
                        "luac": ["luac", "lua", "lua_bytecode"], "class": ["class", "java_class", "jvm"],
                        "dex": ["dex", "dalvik"]}


def bytecode_facts(data):
    """{format, format_candidates, machine "none", machine_num "none", endian, bits "none", + format version} for an
    LLVM bitcode file (raw 'BC' 0xC0DE or the 0x0B17C0DE wrapper), CPython .pyc, Lua luac, Java .class or Android
    .dex; None otherwise (header fields must be consistent: a bare magic is no container)."""
    try:
        d = bytes(data[:0x70])
        out = None
        if d[:4] == _BC_MAGIC and len(data) >= 8:
            out = {"format": "llvm_bitcode", "wrapper": "false"}
        elif d[:4] == _BC_WRAPPER and len(d) >= 20:
            ver, off, size, cpu = struct.unpack_from("<IIII", d, 4)
            if off >= 20 and size >= 4 and off + size <= len(data) and data[off:off + 4] == _BC_MAGIC:
                out = {"format": "llvm_bitcode", "wrapper": "true"}
                if cpu:
                    out.update(machine=MACHO_CPU_LABEL.get(cpu, str(cpu)), machine_num=str(cpu))
        elif d[2:4] == b"\r\n" and len(d) >= 17 and 3000 <= int.from_bytes(d[:2], "little") < 4000 \
                and int.from_bytes(d[4:8], "little") <= 3 and d[16] & 0x7f == 0x63:   # flags, marshal TYPE_CODE
            m = int.from_bytes(d[:2], "little")
            out = {"format": "pyc", "pyc_magic": str(m), "python_version": PYC_MAGIC_VERSION.get(m, "3.x")}
        elif d[:4] == b"\x1bLua" and len(d) >= 12 and d[4] in (0x50, 0x51, 0x52, 0x53, 0x54, 0x55) and d[5] == 0:
            out = {"format": "luac", "lua_version": f"{d[4] >> 4}.{d[4] & 15}"}
            if d[4] in (0x53, 0x54) and d[6:12] == b"\x19\x93\r\n\x1a\n":   # LUAC_DATA, sizes, then LUAC_INT 0x5678
                q, n = (17, d[15]) if d[4] == 0x53 else (15, d[13])   # LUAC_INT offset, sizeof(lua_Integer)
                if n in (4, 8) and len(d) >= q + n:
                    v = d[q:q + n]
                    out["endian"] = "little" if v[:2] == b"\x78\x56" else "big" if v[-2:] == b"\x56\x78" else "none"
        elif d[:4] == b"\xca\xfe\xba\xbe" and len(d) >= 10 and macho_layout(data) is None:
            major = int.from_bytes(d[6:8], "big")
            if 45 <= major <= 120 and int.from_bytes(d[8:10], "big") >= 2:   # constant_pool_count
                out = {"format": "class", "class_major": str(major),
                       "java_version": str(major - 44) if major >= 49 else f"1.{major - 44}"}
                out["endian"] = "big"
        elif d[:4] == b"dex\n" and len(d) >= 0x70 and d[7] == 0 and d[4:7].isdigit() \
                and int.from_bytes(d[0x24:0x28], "little") == 0x70 and d[0x28:0x2c] in (b"\x78\x56\x34\x12",
                                                                                        b"\x12\x34\x56\x78"):
            out = {"format": "dex", "dex_version": d[4:7].decode(),
                   "endian": "little" if d[0x28] == 0x78 else "big"}
        if out is None:
            return None
        base = {"format_candidates": _BYTECODE_CANDIDATES[out["format"]], "machine": "none", "machine_num": "none",
                "endian": "little", "bits": "none"}
        base.update(out)
        return base
    except (IndexError, ValueError, TypeError, struct.error):
        return None


ELF_TYPE_NAME = {0: "ET_NONE", 1: "ET_REL", 2: "ET_EXEC", 3: "ET_DYN", 4: "ET_CORE"}
_NOT_EXPORTS = {"_init", "_fini", "_edata", "_end", "__bss_start", "_DYNAMIC", "_GLOBAL_OFFSET_TABLE_"}


def _elf_object_facts(data, max_syms):
    le = data[5] == 1
    b64 = data[4] == 2
    E = "<" if le else ">"
    u16 = lambda o: struct.unpack_from(E + "H", data, o)[0]
    u32 = lambda o: struct.unpack_from(E + "I", data, o)[0]
    uw = (lambda o: struct.unpack_from(E + "Q", data, o)[0]) if b64 else u32
    et = u16(16)
    entry = uw(24)
    phoff, shoff = (uw(32), uw(40)) if b64 else (u32(28), u32(32))
    p = 52 if b64 else 40
    phentsize, phnum, shentsize, shnum = u16(p + 2), u16(p + 4), u16(p + 6), u16(p + 8)
    interp = any(phoff + i * phentsize + 4 <= len(data) and u32(phoff + i * phentsize) == 3
                 for i in range(min(phnum, 256))) if phoff else False
    secs = []   # (type, offset, size, link, entsize)
    if shoff and shentsize >= (64 if b64 else 40):
        for i in range(min(shnum, 4096)):
            o = shoff + i * shentsize
            if o + shentsize > len(data):
                break
            if b64:
                secs.append((u32(o + 4), uw(o + 24), uw(o + 32), u32(o + 40), uw(o + 56)))
            else:
                secs.append((u32(o + 4), u32(o + 16), u32(o + 20), u32(o + 24), u32(o + 36)))

    def cstr(sec_i, off):
        if not 0 <= sec_i < len(secs):
            return ""
        s = secs[sec_i][1] + off
        e = data.find(b"\0", s, s + 4096)
        return data[s:e].decode("utf-8", "replace") if s < len(data) and e > 0 else ""

    soname = "none"
    for t, off, size, link, _ in secs:
        if t == 6:   # SHT_DYNAMIC: DT_SONAME (14) -> string in the linked strtab
            w = 16 if b64 else 8
            for o in range(off, min(off + size, len(data) - w + 1), w):
                tag = uw(o)
                if tag == 0:
                    break
                if tag == 14:
                    soname = cstr(link, uw(o + w // 2)) or "none"
            break
    # exported = defined GLOBAL/WEAK/UNIQUE FUNC/OBJECT/TLS/IFUNC, default/protected visibility, not SHN_ABS/COMMON:
    # .dynsym for linked images (a .symtab-only executable exports nothing), .symtab for ET_REL.
    # == `nm -D --defined-only` / `nm -g --defined-only` types T/D/R/B/W/V.
    want = 2 if et == 1 else 11
    names = set()
    for t, off, size, link, ent in secs:
        if t != want or not ent:
            continue
        for k in range(1, min(size // ent, max_syms)):
            o = off + k * ent
            if o + ent > len(data):
                break
            if b64:
                nm, info, other, shndx = u32(o), data[o + 4], data[o + 5], u16(o + 6)
            else:
                nm, info, other, shndx = u32(o), data[o + 12], data[o + 13], u16(o + 14)
            if (info >> 4) in (1, 2, 10) and (info & 15) in (1, 2, 6, 10) and 0 < shndx < 0xff00 \
                    and other & 3 in (0, 3):
                n = cstr(link, nm)
                if n and n not in _NOT_EXPORTS:
                    names.add(n)
    exports = sorted(names)
    return {"format": "elf", "elf_type": ELF_TYPE_NAME.get(et, str(et)), "entry_point": hex(entry),
            "soname": soname, "has_interp": "true" if interp else "false",
            "pie": "true" if et == 3 and interp else "false", "is_shared_object": "true" if et == 3 and not interp
            else "false", "is_dll": "false", "dll_name": "none", "exports": exports or "none",
            "export_count": str(len(exports))}


def _pe_object_facts(data, max_syms):
    import pefile
    pe = pefile.PE(data=bytes(data), fast_load=True)
    dll = bool(pe.FILE_HEADER.Characteristics & 0x2000)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
    ed = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
    name = "none"
    exports = []
    if ed is not None:
        if ed.name:
            name = ed.name.decode("utf-8", "replace")
        exports = sorted({s.name.decode("utf-8", "replace") for s in ed.symbols[:max_syms] if s.name})
    return {"format": "pe", "pe_type": "DLL" if dll else "EXE", "is_dll": "true" if dll else "false",
            "entry_point": "0x{:08x}".format(pe.OPTIONAL_HEADER.AddressOfEntryPoint),   # RVA, lib.knowledge fmt
            "dll_name": name, "soname": "none", "exports": exports or "none", "export_count": str(len(exports))}


def object_facts(data, max_syms=50000):
    """Shared-library / relocatable-object facts from the bytes (pure header + symbol-table walk, no subprocess).
    ELF: {format, elf_type ET_DYN/ET_REL/ET_EXEC (readelf constant), entry_point hex (0x0 for .o and most .so),
    soname (DT_SONAME), has_interp, pie (ET_DYN + PT_INTERP), is_shared_object (ET_DYN, no INTERP), exports (sorted
    defined global FUNC/OBJECT names = `nm -D --defined-only`, `nm -g --defined-only` for ET_REL), export_count}.
    PE: {format, pe_type DLL/EXE, is_dll, entry_point (AddressOfEntryPoint RVA 0x%08x), dll_name (export dir Name),
    exports (sorted export names = `objdump -p`), export_count}. Absent field -> "none"; not an ELF/PE -> None."""
    try:
        if data[:4] == b"\x7fELF" and data[4:5] in (b"\x01", b"\x02") and data[5:6] in (b"\x01", b"\x02") \
                and len(data) >= 52:
            return _elf_object_facts(data, max_syms)
        if data[:2] == b"MZ" and len(data) >= 0x40:
            pe = int.from_bytes(data[0x3c:0x40], "little")
            if data[pe:pe + 4] == b"PE\0\0":
                return _pe_object_facts(data, max_syms)
    except Exception:   # truncated / hostile headers: cannot answer
        pass
    return None


# --- native import / export tables (D15 symbolized getenv/strcmp/printf; D17 backfill re-asks old days per group).

def _elf_import_facts(data):
    f = _elf_pair_facts(data)   # imports (UND named .dynsym, table order) + needed (DT_NEEDED order)
    E, b64 = ("<" if data[5] == 1 else ">"), data[4] == 2
    u16 = lambda o: struct.unpack_from(E + "H", data, o)[0]
    u32 = lambda o: struct.unpack_from(E + "I", data, o)[0]
    uw = (lambda o: struct.unpack_from(E + "Q", data, o)[0]) if b64 else u32
    phoff, p = (uw(32), 52) if b64 else (u32(28), 40)
    phes, phn = u16(p + 2), u16(p + 4)
    interp = "none"
    for k in range(min(phn, 256) if phoff and phes >= (56 if b64 else 32) else 0):
        o = phoff + k * phes
        if o + phes > len(data):
            break
        if u32(o) == 3:   # PT_INTERP: p_offset / p_filesz -> path, NUL dropped
            off, sz = (uw(o + 8), uw(o + 32)) if b64 else (u32(o + 4), u32(o + 16))
            interp = bytes(data[off:off + min(sz, 4096)]).split(b"\0")[0].decode("utf-8", "replace") or "none"
            break
    of = _elf_object_facts(data, 50000)
    imports = list(dict.fromkeys(n.split("@")[0] for n in f["imports"]))
    return {"format": "elf", "needed": f["needed"], "imports": imports, "interpreter": interp,
            "exports": of["exports"] if of["exports"] != "none" else [], "soname": of["soname"]}


def _pe_import_facts(data):
    import pefile
    pe = pefile.PE(data=bytes(data), fast_load=True)
    D = pefile.DIRECTORY_ENTRY
    pe.parse_data_directories(directories=[D["IMAGE_DIRECTORY_ENTRY_IMPORT"], D["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                                           D["IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT"]])
    dlls, funcs, qual, delay = [], [], [], []
    for ent in getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])[:4096]:
        dll = ent.dll.decode("utf-8", "replace")
        dlls.append(dll)
        for imp in ent.imports[:65536]:
            fn = imp.name.decode("utf-8", "replace") if imp.name else f"ord{imp.ordinal}"
            funcs.append(fn)
            qual.append(f"{dll}!{fn}")
    for ent in getattr(pe, "DIRECTORY_ENTRY_DELAY_IMPORT", [])[:4096]:
        delay.append(ent.dll.decode("utf-8", "replace"))
    ed = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
    exports = sorted({s.name.decode("utf-8", "replace") for s in ed.symbols[:65536] if s.name}) if ed else []
    try:
        imphash = pe.get_imphash() or "none"
    except Exception:  # noqa: BLE001
        imphash = "none"
    return {"format": "pe", "needed": dlls, "import_dlls": dlls, "imports": funcs, "imports_qualified": qual,
            "delay_import_dlls": delay, "interpreter": "none", "exports": exports, "imphash": imphash,
            "dll_name": ed.name.decode("utf-8", "replace") if ed is not None and ed.name else "none"}


_MO_DYLIB_CMDS = {0xc: "load", 0x80000018: "weak", 0x8000001f: "reexport", 0x20: "lazy", 0x80000023: "upward"}


def _macho_import_facts(data):
    lay = macho_layout(data)
    if not lay:
        return None
    base = lay["slices"][0]["slice_offset"]   # fat: first slice (lipo order), like `otool -L` without -arch
    end, bits = _MO_MAGIC[bytes(data[base:base + 4])]
    u32 = lambda o: int.from_bytes(data[o:o + 4], end)   # noqa: E731
    ncmds, sizeofcmds = u32(base + 16), u32(base + 20)
    p = base + (32 if bits == 64 else 28)
    stop = min(len(data), p + sizeofcmds)

    def lcstr(lc, size, at):
        o = u32(lc + at)
        return bytes(data[lc + o:lc + size]).split(b"\0")[0].decode("utf-8", "replace") if 0 < o < size else ""
    dylibs, weak, rpaths, interp, idname, symtab = [], [], [], "none", "none", None
    for _ in range(min(ncmds, 4096)):
        if p + 8 > stop:
            break
        cmd, size = u32(p), u32(p + 4)
        if size < 8:
            break
        if cmd in _MO_DYLIB_CMDS:
            dylibs.append(lcstr(p, size, 8))
            if cmd == 0x80000018:
                weak.append(dylibs[-1])
        elif cmd == 0xd:   # LC_ID_DYLIB: the install name of this dylib itself (not a dependency)
            idname = lcstr(p, size, 8) or "none"
        elif cmd == 0xe:   # LC_LOAD_DYLINKER
            interp = lcstr(p, size, 8) or "none"
        elif cmd == 0x8000001c:   # LC_RPATH
            rpaths.append(lcstr(p, size, 8))
        elif cmd == 0x2:   # LC_SYMTAB: symoff, nsyms, stroff, strsize (slice-relative)
            symtab = (u32(p + 8), u32(p + 12), u32(p + 16), u32(p + 20))
        p += size
    imports, exports = [], set()
    if symtab:
        symoff, nsyms, stroff, strsize = symtab
        ent = 16 if bits == 64 else 12
        strs = bytes(data[base + stroff:base + stroff + strsize])
        for k in range(min(nsyms, 400_000)):
            o = base + symoff + k * ent
            if o + ent > len(data):
                break
            strx, ty = u32(o), data[o + 4]
            if ty & 0xe0 or not ty & 1 or ty & 0x10 or not 0 < strx < len(strs):   # stab / not N_EXT / N_PEXT
                continue
            e = strs.find(b"\0", strx)
            n = strs[strx:e if e >= 0 else len(strs)].decode("utf-8", "replace")
            if n:
                (exports.add(n) if ty & 0x0e else imports.append(n))   # N_UNDF -> import, else defined
    return {"format": "mach-o", "needed": dylibs, "weak_dylibs": weak, "rpaths": rpaths, "install_name": idname,
            "interpreter": interp, "imports": list(dict.fromkeys(imports)), "exports": sorted(exports)}


def native_import_facts(data):
    """Import / dependency / export lists of a native image (pure header + table walk, no subprocess):
    needed = dependencies in load order (ELF DT_NEEDED, PE import descriptor DLL names as stored, Mach-O
    LC_LOAD_DYLIB/WEAK/REEXPORT/LAZY/UPWARD paths; LC_ID_DYLIB excluded -> install_name), imports (ELF: undefined
    named .dynsym symbols in table order, @version stripped, = readelf --dyn-syms UND; PE: function names in
    descriptor order, ordinal-only -> ord<N>, + imports_qualified "DLL!func"; Mach-O: undefined external nlist names
    in symtab order = `nm -u -p`, leading `_` kept), interpreter (ELF PT_INTERP / Mach-O LC_LOAD_DYLINKER, NUL
    dropped; PE "none"), exports (sorted: ELF defined dynamic symbols = object_facts; PE export names; Mach-O defined
    external = `nm -gU`), PE imphash (pefile), import_dlls / delay_import_dlls, Mach-O weak_dylibs / rpaths. Each list
    also as *_sorted, *_count and *_csv; an empty list -> "none". Not ELF/PE/Mach-O or unparseable -> None."""
    try:
        if data[:4] == b"\x7fELF" and data[4:5] in (b"\x01", b"\x02") and data[5:6] in (b"\x01", b"\x02") \
                and len(data) >= 64 and data[6] == 1:
            f = _elf_import_facts(data)
        elif data[:2] == b"MZ" and len(data) >= 0x40 and \
                data[int.from_bytes(data[0x3c:0x40], "little"):][:4] == b"PE\0\0":
            f = _pe_import_facts(data)
        elif bytes(data[:4]) in _MO_MAGIC or bytes(data[:4]) in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
            f = _macho_import_facts(data)
        else:
            return None
        if not f:
            return None
        for k in [k for k, v in f.items() if isinstance(v, list)]:
            v = f[k]
            f[k + "_count"] = str(len(v))
            f[k + "_sorted"] = sorted(v) or "none"
            f[k + "_csv"] = ",".join(v) or "none"
            f[k] = v or "none"
        for a, b in (("dependencies", "needed"), ("libraries", "needed"), ("dylibs", "needed"),
                     ("imported_functions", "imports"), ("import_count", "imports_count"),
                     ("export_count", "exports_count"), ("interp", "interpreter")):
            if b in f:
                f.setdefault(a, f[b])
        return f
    except Exception:  # noqa: BLE001 -- truncated / hostile tables: cannot answer
        return None


def native_import_field(data, name):
    """One native_import_facts value; "none" when the input is not a native image or the field is unknown/absent."""
    try:
        return (native_import_facts(data) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


def _be_raw_at(data, i):
    """Raw blob at i whose len/crc header fields are BIG-endian (a C struct compiled for mips/ppc/sparc/s390): the
    blob re-packed with an LE header (so _parse_blob reads it), only when crc32(plain) matches; else None."""
    if len(data) < i + 12:
        return None
    n, crc = struct.unpack_from(">HI", data, i + 6)
    body = data[i + 12:i + 12 + n]
    if not n or len(body) != n or zlib.crc32(body.translate(_XOR_TBL[data[i + 5]])) != crc:
        return None
    return data[i:i + 6] + struct.pack("<HI", n, crc) + body


_XOR_TBL = [bytes(b ^ k for b in range(256)) for k in range(256)]


def _func_start(data, s):
    """Best-effort start of the AArch64 function holding file offset `s` (-O2 hoists the builder's constants into
    registers there): the nearest prologue (sub sp,sp,#n / stp x29,x30,[sp,#-n]!), else just past a ret / br xN."""
    lo = max(0, s - 0x4000)
    t = s - 4
    while t >= lo:
        w = int.from_bytes(data[t:t + 4], "little")
        if w & 0xff8003ff == 0xd10003ff or w & 0xffc07fff == 0xa9807bfd:
            return t
        if w & 0xfffffc1f == 0xd61f0000 or w == 0xd65f03c0:
            break
        t -= 4
    t += 4
    while t < s and data[t:t + 4] in (b"\x1f\x20\x03\xd5", b"\0\0\0\0"):   # nop / zero padding
        t += 4
    return t if t >= lo + 4 else None


def _stack_emu(data, start, arch, upto=None):
    """Emulate (unicorn, no syscalls, unmapped data -> zero pages) the code at file offset `start` mapped at vaddr =
    file offset with sp/fp mid-stack; a call that leaves the window returns 0 to its caller. Every crc-valid HCFG blob
    left in memory."""
    import unicorn as U
    if arch == "aarch64":
        uc = U.Uc(U.UC_ARCH_ARM64, U.UC_MODE_ARM)
        regs = (U.arm64_const.UC_ARM64_REG_SP, U.arm64_const.UC_ARM64_REG_X29)
    else:
        uc = U.Uc(U.UC_ARCH_X86, U.UC_MODE_32 if arch == "x86" else U.UC_MODE_64)
        x = U.x86_const
        regs = (x.UC_X86_REG_ESP, x.UC_X86_REG_EBP) if arch == "x86" else (x.UC_X86_REG_RSP, x.UC_X86_REG_RBP)
    lo, hi = max(0, (start - 0x1000) & ~0xfff), min(len(data), max(start, upto or 0) + 0x10000)
    hi_pg = (hi + 0xfff) & ~0xfff
    stk = 0x7ff00000 if hi_pg <= 0x7ff00000 else (hi_pg + 0xfffff) & ~0xfffff   # 256 KB, sp/fp in the middle
    uc.mem_map(lo, hi_pg - lo)
    uc.mem_write(lo, data[lo:hi])
    uc.mem_map(stk, 0x40000)
    for r in regs:
        uc.reg_write(r, stk + 0x20000)
    extra = [0]

    def unmapped(uc, access, addr, size, value, ud):
        if access == U.UC_MEM_FETCH_UNMAPPED or extra[0] >= 32:
            return False
        extra[0] += 1
        try:
            uc.mem_map(addr & ~0xfff, 0x2000 if (addr & 0xfff) + size > 0x1000 else 0x1000)
        except U.UcError:
            return False
        return True
    uc.hook_add(U.UC_HOOK_MEM_UNMAPPED, unmapped)
    uc.hook_add(U.UC_HOOK_INTR, lambda uc, n, ud: uc.emu_stop())
    if arch == "x86-64":
        uc.hook_add(U.UC_HOOK_INSN, lambda uc, ud: uc.emu_stop(), None, 1, 0, U.x86_const.UC_X86_INS_SYSCALL)
    pc, left = start, 30000
    for _ in range(8):
        try:
            uc.emu_start(pc, hi_pg, timeout=50000, count=left)
            break
        except U.UcError as e:
            if e.errno != U.UC_ERR_FETCH_UNMAPPED:
                break
        left -= 2000   # (count is not reported back: charge each resume)
        if arch == "aarch64":   # bl / PLT stub out of the window: return 0 to the caller
            pc = uc.reg_read(U.arm64_const.UC_ARM64_REG_X30)
            uc.reg_write(U.arm64_const.UC_ARM64_REG_X0, 0)
        else:
            w = 4 if arch == "x86" else 8
            sp = uc.reg_read(regs[0])
            try:
                pc = int.from_bytes(uc.mem_read(sp, w), "little")
            except U.UcError:
                break
            uc.reg_write(regs[0], sp + w)
            uc.reg_write(U.x86_const.UC_X86_REG_EAX if arch == "x86" else U.x86_const.UC_X86_REG_RAX, 0)
        if not lo <= pc < hi or left <= 0:
            break
    out = []
    for b, e, _ in uc.mem_regions():
        buf = bytes(uc.mem_read(b, e - b + 1))
        i = buf.find(HCFG_MAGIC)
        while i >= 0 and len(out) < 8:
            blob = buf[i:i + _need(buf[i:i + 8])]
            if (_parse_blob(blob) or (0,) * 6)[5]:
                out.append(blob)
            i = buf.find(HCFG_MAGIC, i + 1)
    return out


def _stack_scan(data, emit, late):
    """Blob built at runtime from immediates (C `volatile char b[N]; b[0]='H'; ...`, stack strings): x86 movb/movw/movl
    $imm stores, movabs+push / push imm32 runs, AArch64 movz+strb. Emulate from the first instruction that puts 'H'
    (walking back over a push run), crc-valid hits only; offset = that instruction's file offset (speculative)."""
    try:
        import unicorn   # noqa: F401
    except ImportError:
        return
    arch = _arch_of(data)
    sites = []

    def back(rx, i, a):   # instruction start(s) for an immediate at offset i
        for k in range(2, 10):
            if i >= k and rx.match(data, i - k, i):
                st = i - k
                sites.append((st, a))
                if 0x40 <= data[st] <= 0x4f and data[st + 1] in (0xc6, 0xc7):
                    sites.append((st + 1, a))   # that 0x4X may be the previous instruction's last byte
                return
    if arch in (None, "x86-64", "x86"):
        a = arch or "x86-64"
        for pat in (b"H\xc6", b"H\x41\xc6"):
            i, n = data.find(pat), 0
            while i >= 0 and n < 1 << 16 and len(sites) < 4 * HCFG_STACK_SITES and not late():
                if _STK_X86N.match(data, i + 1):
                    back(_STK_X86B, i, a)
                i, n = data.find(pat, i + 1), n + 1
        i, n = data.find(HCFG_MAGIC), 0
        while i >= 0 and n < 4096 and len(sites) < 4 * HCFG_STACK_SITES and not late():
            if i >= 1 and data[i - 1] == 0x68:   # i386 push 'HCFG' is the LAST push: walk back over the push imm32 run
                s = i - 1
                while s >= 5 and data[s - 5] == 0x68 and i - s < 0x4000:
                    s -= 5
                sites.append((s, "x86"))
            elif i >= 2 and data[i - 2] in (0x48, 0x49) and 0xb8 <= data[i - 1] <= 0xbf:   # movabs r64 ; push r64
                s = i - 2
                while s >= 11 and data[s - 11] in (0x48, 0x49) and 0xb8 <= data[s - 10] <= 0xbf \
                        and 0x50 <= data[s - 1] <= 0x57 and i - s < 0x4000:
                    s -= 11
                sites.append((s, a))
            else:                                # movl $0x47464348 / movq $imm32 to memory
                back(_STK_X86L, i, a)
            i, n = data.find(HCFG_MAGIC, i + 1), n + 1
    if arch in (None, "aarch64"):
        for pat in _STK_A64:
            i, n = data.find(pat), 0
            while i >= 0 and n < 1 << 16 and len(sites) < 4 * HCFG_STACK_SITES and not late():
                s = i - 1
                if s % 4 == 0 and data[s] < 0x1f and (pat[0] == 0x69 or _STK_A64_C.search(data, s + 4, s + 48)):
                    sites.append((s, "aarch64"))
                i, n = data.find(pat, i + 1), n + 1
    sites = sorted(set(sites))
    done = set()
    for s, a in sites[:HCFG_STACK_SITES]:
        if late():
            return
        blobs = []
        for st in (s, _func_start(data, s) if a == "aarch64" else None):   # then the function (hoisted consts)
            if st is None or blobs or late():
                continue
            try:
                blobs = _stack_emu(data, st, a, s)
            except Exception:   # noqa: BLE001 -- unicorn on hostile bytes: never raise past the scan
                pass
        for blob in blobs:
            if blob not in done:
                done.add(blob)
                emit(s, "stack-built", blob, f"{a} emu@{s}")
        if done:
            return


_COB_LD = re.compile(rb"(?:[\x66\xf3]|[\x40-\x4f])?\x0f[\x10\x28\x6f][\x05\x0d\x15\x1d\x25\x2d\x35\x3d]"
                     rb"|\xc5[\xf8-\xfa\xfc-\xfe]\x10|\xc5[\xf8-\xfa\xfc-\xfe][\x28\x6f]", re.S)


def _cob_store_scan(data, emit, late):
    """GnuCOBOL module init (x86-64 ELF64 LE, libcob cue): WORKING-STORAGE VALUE literals are copied into the static
    b_N storage by gcc-expanded memcpy = movabs/movl immediates (cobc -O0) or movdqa/movups loads of 16-byte .rodata
    constants interleaved with movabs (cobc -O2), in any order. Sites: a movabs/movl immediate starting 'HCFG', or a
    rip-relative SSE/AVX load of a .rodata 'HCFG'. Emulate (unicorn, PT_LOAD-mapped, zero pages elsewhere) from just
    after the last PLT call before the site up to the next call/ret (<= 4096 insns); crc-valid blobs only -> encoding
    'stack-built', offset = the site instruction (speculative)."""
    if data[:4] != b"\x7fELF" or data[4:6] != b"\x02\x01" or data[18:20] != b"\x3e\x00" or len(data) < 64:
        return
    if b"cob_init" not in data and b"libcob" not in data:
        return
    try:
        import unicorn as U
    except ImportError:
        return
    phoff = struct.unpack_from("<Q", data, 32)[0]
    phentsz, phnum = struct.unpack_from("<HH", data, 54)
    loads = []
    for k in range(min(phnum, 64)):
        p = phoff + k * phentsz
        if p + 56 <= len(data):
            typ, flg, off, va, _pa, fsz, msz = struct.unpack_from("<IIQQQQQ", data, p)
            if typ == 1 and 0 < msz < 1 << 30:
                loads.append((va, off, fsz, msz, flg))
    if not loads:
        return
    o2v = lambda o: next((va + o - off for va, off, fsz, _m, _f in loads if off <= o < off + fsz), None)  # noqa: E731
    x = [(va, off, fsz) for va, off, fsz, _m, f in loads if f & 1]
    sites = []
    i, n = data.find(HCFG_MAGIC), 0
    while i >= 0 and n < 256 and len(sites) < 16:
        if i >= 2 and data[i - 2] in (0x48, 0x49) and 0xb8 <= data[i - 1] <= 0xbf:
            sites.append(i - 2)                              # movabs $'HCFG....', r64
        elif i >= 6 and data[i - 6] == 0xc7 and data[i - 5] == 0x05:
            sites.append(i - 6)                              # movl $'HCFG', disp(%rip)
        else:
            v = o2v(i)
            for va, off, fsz in x if v is not None else ():  # rip-relative 16-byte load of a .rodata HCFG
                for m in _COB_LD.finditer(data, off, min(off + fsz, off + (16 << 20))):
                    e = m.end()
                    if e + 4 <= len(data) and va + e + 4 - off + struct.unpack_from("<i", data, e)[0] == v:
                        sites.append(m.start())
                    if late():
                        return
        i, n = data.find(HCFG_MAGIC, i + 1), n + 1
    done = set()
    for s in sites[:16]:
        if late():
            return
        st = s
        for k in range(s - 5, max(0, s - 4096), -1):   # just after the last `call rel32` into code before the site
            if data[k] == 0xe8:
                t = k + 5 + struct.unpack_from("<i", data, k + 1)[0]   # same exec segment: file delta = va delta
                if any(off <= t < off + fsz for _va, off, fsz in x) and (
                        data[t:t + 4] == b"\xf3\x0f\x1e\xfa" or data[t:t + 2] == b"\xff\x25" or
                        data[t:t + 3] == b"\xf2\xff\x25"):   # PLT / .plt.sec stub (endbr64 / jmp *GOT)
                    st = k + 5
                    break
        try:
            uc = U.Uc(U.UC_ARCH_X86, U.UC_MODE_64)
            mapped = set()

            def page(addr):
                pg = addr & ~0xfff
                if pg in mapped or len(mapped) > 512:
                    return pg in mapped
                uc.mem_map(pg, 0x1000)
                mapped.add(pg)
                for va, off, fsz, msz, _f in loads:
                    a, b = max(pg, va), min(pg + 0x1000, va + fsz)
                    if a < b:
                        uc.mem_write(a, data[off + a - va:off + b - va])
                return True

            def unmapped(uc, access, addr, size, value, ud):
                if access == U.UC_MEM_FETCH_UNMAPPED:
                    return False
                return page(addr) and page(addr + size - 1)

            def code(uc, addr, size, ud):
                b = bytes(uc.mem_read(addr, min(size, 3)))
                if b[:1] in (b"\xe8", b"\xc3") or b[:2] in (b"\xff\x15", b"\xf2\xc3") or \
                        (b[:1] == b"\xff" and len(b) > 1 and 0xd0 <= b[1] <= 0xd7):
                    uc.emu_stop()
            pva = o2v(st)
            if pva is None:
                continue
            page(pva), page(pva + 0x1000)
            uc.mem_map(0x7ff00000, 0x40000)
            uc.reg_write(U.x86_const.UC_X86_REG_RSP, 0x7ff20000)
            uc.reg_write(U.x86_const.UC_X86_REG_RBP, 0x7ff20000)
            uc.hook_add(U.UC_HOOK_MEM_UNMAPPED, unmapped)
            uc.hook_add(U.UC_HOOK_CODE, code)
            try:
                uc.emu_start(pva, 0, timeout=100000, count=4096)
            except U.UcError:
                pass
            for b, e, _ in uc.mem_regions():
                buf = bytes(uc.mem_read(b, e - b + 1))
                j = buf.find(HCFG_MAGIC)
                while j >= 0:
                    blob = buf[j:j + _need(buf[j:j + 8])]
                    if blob not in done and (_parse_blob(blob) or (0,) * 6)[5]:
                        done.add(blob)
                        emit(s, "stack-built", blob, f"x86-64 cob-init emu@{s}")
                    j = buf.find(HCFG_MAGIC, j + 1)
        except Exception:   # noqa: BLE001 -- unicorn on hostile bytes: never raise past the scan
            continue
        if done:
            return


HCFG_CTOR_MAX = int(os.environ.get("HCTF_HCFG_CTOR_MAX", "16"))   # .init_array targets emulated (~2-20 ms each)
# ELF relocation types: RELATIVE / GLOB_DAT / JUMP_SLOT per machine (x86-64 62, AArch64 183)
_CTOR_ARCH = {62: ("x86-64", 8, (6, 7)), 183: ("aarch64", 1027, (1025, 1026))}
_CTOR_STUBS = ("malloc", "calloc", "free", "memcpy", "memmove", "memset", "strlen", "strcpy", "__memcpy_chk",
               "__memset_chk", "__memmove_chk")


def _elf_ctors(data):
    """(arch, base, loads, init_targets, relocs, imports, v2o) of a little-endian ELF64 x86-64/AArch64 image, else None.
    loads = [(vaddr, offset, filesz, memsz, flags)]; init_targets = .init_array function vaddrs (RELATIVE addends for a
    PIE whose slots are 0 in the file); relocs = [(r_offset, type, sym_index, addend)]; imports = {sym_index: name}."""
    if data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1 or len(data) < 64:
        return None
    mach = struct.unpack_from("<H", data, 18)[0]
    if mach not in _CTOR_ARCH:
        return None
    phoff, shoff = struct.unpack_from("<QQ", data, 32)
    phentsz, phnum, shentsz, shnum = struct.unpack_from("<HHHH", data, 54)
    loads, dyn = [], None
    for k in range(min(phnum, 64)):
        p = phoff + k * phentsz
        if p + 56 > len(data):
            break
        typ, flg, off, va, _pa, fsz, msz = struct.unpack_from("<IIQQQQQ", data, p)
        if typ == 1 and msz and msz < 1 << 30:
            loads.append((va, off, fsz, msz, flg))
        elif typ == 2:
            dyn = (off, fsz)
    if not loads:
        return None
    base = 0x400000 if min(l[0] for l in loads) < 0x10000 else 0   # PIE: rebase off page 0

    def v2o(va):
        for lva, off, fsz, _m, _f in loads:
            if lva <= va < lva + fsz:
                return off + va - lva
        return None
    init, rels, syms = None, [], {}
    # section headers first (sh_link of a RELA section -> its symtab -> strtab), PT_DYNAMIC when stripped of them
    secs = []
    if shoff and shentsz == 64 and shoff + shnum * 64 <= len(data):
        secs = [struct.unpack_from("<IIQQQQIIQQ", data, shoff + k * 64) for k in range(min(shnum, 4096))]
    tabs = []
    for s in secs:
        if s[1] == 14 and init is None:                       # SHT_INIT_ARRAY
            init = (s[3], s[4], s[5])
        elif s[1] == 4 and s[9] == 24:                        # SHT_RELA
            tabs.append((s[4], s[5], s[6]))
    if not secs and dyn:
        d = {}
        for k in range(0, min(dyn[1], 8192), 16):
            t, v = struct.unpack_from("<qQ", data, dyn[0] + k) if dyn[0] + k + 16 <= len(data) else (0, 0)
            if t == 0:
                break
            d.setdefault(t, v)
        if 25 in d and 27 in d:
            init = (d[25], v2o(d[25]), d[27])
        for a, n in ((7, 8), (23, 2)):                        # DT_RELA/RELASZ, DT_JMPREL/PLTRELSZ
            if a in d and n in d and v2o(d[a]) is not None:
                tabs.append((v2o(d[a]), d[n], None))
    if not init or init[1] is None or not init[2]:
        return None
    for off, sz, link in tabs[:16]:
        for q in range(off, min(off + sz, len(data) - 23, off + (24 << 16)), 24):
            ro, info, add = struct.unpack_from("<QQq", data, q)
            rels.append((ro, info & 0xffffffff, info >> 32, add))
        if link is not None and link < len(secs) and not syms:   # dynsym -> dynstr names (import stubs)
            sy = secs[link]
            st = secs[sy[6]] if sy[6] < len(secs) else None
            if sy[9] == 24 and st:
                for j in range(1, min(sy[5] // 24, 1 << 14)):
                    nm = struct.unpack_from("<I", data, sy[4] + j * 24)[0]
                    e = data.find(b"\0", st[4] + nm, st[4] + nm + 128)
                    if e > 0:
                        syms[j] = data[st[4] + nm:e].decode("latin-1")
    rmap = {r[0]: r[3] for r in rels if r[1] == _CTOR_ARCH[mach][1]}
    tg = []
    for k in range(min(init[2] // 8, HCFG_CTOR_MAX * 2)):
        va = init[0] + 8 * k
        f = struct.unpack_from("<Q", data, init[1] + 8 * k)[0] if init[1] + 8 * k + 8 <= len(data) else 0
        f = f or rmap.get(va, 0)
        if f and f not in (0xffffffffffffffff,) and v2o(f) is not None:
            tg.append(f)
    return _CTOR_ARCH[mach][0], base, loads, tg, rels, syms, v2o


def _ctor_emu(info, fns, end, srcs=None):
    """Emulate the .init_array targets `fns` IN ORDER in one address space (= what the loader does: unicorn, image mapped
    once at its link address + base, RELATIVE relocs applied, GOT imports -> stubs for malloc/mem*/str*, anything else
    returns 0) until `end` (epoch s). (index, blobs): crc-valid HCFG blobs NOT stored verbatim in the file that sit in
    writable memory after the last target (index None: none). srcs (a set; the re-run after a hit): memory is checked
    after EVERY target, index = the first that left a blob, srcs = the file offsets of the bytes THAT target read (a
    Python hook per read, and a 37 MB .bss copy per check on a Go/Rust image: only worth it once something hit)."""
    import unicorn as U
    arch, base, loads, _tg, rels, syms, v2o, data = info
    a64 = arch == "aarch64"
    uc = U.Uc(U.UC_ARCH_ARM64, U.UC_MODE_ARM) if a64 else U.Uc(U.UC_ARCH_X86, U.UC_MODE_64)
    if a64:
        R = U.arm64_const
        SP, RET, ARGS, PC = R.UC_ARM64_REG_SP, R.UC_ARM64_REG_X0, (R.UC_ARM64_REG_X0, R.UC_ARM64_REG_X1,
                                                                     R.UC_ARM64_REG_X2), R.UC_ARM64_REG_PC
    else:
        R = U.x86_const
        SP, RET, ARGS, PC = R.UC_X86_REG_RSP, R.UC_X86_REG_RAX, (R.UC_X86_REG_RDI, R.UC_X86_REG_RSI,
                                                                   R.UC_X86_REG_RDX), R.UC_X86_REG_RIP
    spans = {}
    for va, off, fsz, msz, flg in loads:
        lo, hi = (base + va) & ~0xfff, (base + va + msz + 0xfff) & ~0xfff
        for pg in range(lo, hi, 0x1000):
            spans[pg] = flg
    pages = sorted(spans)
    if len(pages) > (96 << 20) >> 12:
        return []
    run = [pages[0]]
    for pg in pages[1:] + [None]:
        if pg is not None and pg == run[-1] + 0x1000:
            run.append(pg)
            continue
        uc.mem_map(run[0], len(run) * 0x1000)
        if pg is not None:
            run = [pg]
    for va, off, fsz, msz, flg in loads:
        uc.mem_write(base + va, data[off:off + fsz])
    STUB, STK, HEAP, DONE = 0x7e000000, 0x7f000000, 0x7c000000, 0x7dfff000
    uc.mem_map(STK, 0x40000)
    uc.mem_map(HEAP, 0x100000)
    uc.mem_map(STUB, 0x10000, U.UC_PROT_READ)   # not executable: a jump there = fetch-protected -> stub
    uc.mem_map(DONE, 0x1000, U.UC_PROT_READ)
    stubs = {}
    rel_t, imp_t = _CTOR_ARCH[183 if a64 else 62][1:]
    for ro, t, si, add in rels:
        try:
            if t == rel_t:
                uc.mem_write(base + ro, struct.pack("<Q", base + add))
            elif t in imp_t:
                slot = STUB + 16 * (len(stubs) % 0x1000)
                stubs[slot] = syms.get(si, "")
                uc.mem_write(base + ro, struct.pack("<Q", slot))
        except U.UcError:
            pass
    heap, extra = [HEAP], [0]
    exe = [(base + va, base + va + fsz, off) for va, off, fsz, msz, flg in loads]

    def unmapped(uc, access, addr, size, value, ud):
        if access == U.UC_MEM_FETCH_UNMAPPED or extra[0] >= 64:
            return False
        extra[0] += 1
        try:
            uc.mem_map(addr & ~0xfff, 0x2000 if (addr & 0xfff) + size > 0x1000 else 0x1000)
        except U.UcError:
            return False
        return True

    def rd(uc, access, addr, size, value, ud):
        for lo, hi, off in exe:
            if lo <= addr < hi and len(srcs) < 1 << 16:
                srcs.update(range(off + addr - lo, off + addr - lo + size))
                return
    uc.hook_add(U.UC_HOOK_MEM_UNMAPPED, unmapped)
    uc.hook_add(U.UC_HOOK_INTR, lambda uc, n, ud: uc.emu_stop())
    if not a64:
        uc.hook_add(U.UC_HOOK_INSN, lambda uc, ud: uc.emu_stop(), None, 1, 0, U.x86_const.UC_X86_INS_SYSCALL)
    for idx, fn in enumerate(fns):
        if time.time() > end:
            break
        if srcs is not None:
            srcs.clear()
            hk = uc.hook_add(U.UC_HOOK_MEM_READ, rd, None, min(e[0] for e in exe), max(e[1] for e in exe))
        sp = STK + 0x30000
        if a64:
            uc.reg_write(R.UC_ARM64_REG_X30, DONE)
        else:
            sp -= 8
            uc.mem_write(sp, struct.pack("<Q", DONE))
        uc.reg_write(SP, sp)
        _ctor_run(uc, U, R, a64, fn + base, stubs, heap, HEAP, DONE, SP, RET, ARGS, PC, end)
        if srcs is not None:
            uc.hook_del(hk)
        elif idx < len(fns) - 1 and time.time() <= end:
            continue
        out = []
        for b, e, perm in uc.mem_regions():
            if not perm & U.UC_PROT_WRITE or b == STUB or e - b > 96 << 20:
                continue
            buf = bytes(uc.mem_read(b, e - b + 1))
            i = buf.find(HCFG_MAGIC)
            while i >= 0 and len(out) < 8:
                blob = buf[i:i + _need(buf[i:i + 8])]
                if (_parse_blob(blob) or (0,) * 6)[5] and blob not in data:
                    out.append(blob)
                i = buf.find(HCFG_MAGIC, i + 1)
        if out:
            return idx, out
    return None, []


def _ctor_run(uc, U, R, a64, pc, stubs, heap, HEAP, DONE, SP, RET, ARGS, PC, end):
    """Run one constructor from pc to the DONE return address; a call into an import stub is served here (malloc/
    calloc bump heap, memcpy/memmove/memset, strlen/strcpy; anything else returns 0) and resumed at the caller."""
    left = 300000
    for _ in range(64):
        try:
            uc.emu_start(pc, DONE, timeout=max(1000, int((end - time.time()) * 1e6)), count=left)
            break
        except U.UcError as e:
            if e.errno not in (U.UC_ERR_FETCH_UNMAPPED, U.UC_ERR_FETCH_PROT):
                break
        left -= 3000
        cur = uc.reg_read(PC)
        if cur == DONE or left <= 0 or time.time() > end:
            break
        a = [uc.reg_read(r) for r in ARGS]
        name, rv = stubs.get(cur & ~0xf, ""), 0
        try:
            if name in ("malloc", "calloc"):
                n = (a[0] * (a[1] if name == "calloc" else 1) + 15) & ~15
                if n < 0x80000 and heap[0] + n < HEAP + 0x100000:
                    rv, heap[0] = heap[0], heap[0] + n
            elif name in ("memcpy", "memmove", "__memcpy_chk", "__memmove_chk") and a[2] < 1 << 20:
                uc.mem_write(a[0], bytes(uc.mem_read(a[1], a[2])))
                rv = a[0]
            elif name in ("memset", "__memset_chk") and a[2] < 1 << 20:
                uc.mem_write(a[0], bytes([a[1] & 0xff]) * a[2])
                rv = a[0]
            elif name in ("strlen", "strcpy"):
                q, s = a[1] if name == "strcpy" else a[0], b""
                while b"\0" not in s and len(s) < 1 << 16:   # page by page: a string near a mapping's end
                    s += bytes(uc.mem_read(q + len(s), 0x1000 - ((q + len(s)) & 0xfff)))
                n = s.find(b"\0")
                if name == "strcpy":
                    uc.mem_write(a[0], s[:n + 1])
                rv = a[0] if name == "strcpy" else n
        except U.UcError:
            rv = 0
        uc.reg_write(RET, rv)
        if a64:
            pc = uc.reg_read(R.UC_ARM64_REG_X30)
        else:
            sp = uc.reg_read(SP)
            pc = struct.unpack("<Q", bytes(uc.mem_read(sp, 8)))[0]
            uc.reg_write(SP, sp + 8)
        if pc == DONE:
            break


HCFG_CTOR_SECS = float(os.environ.get("HCTF_HCFG_CTOR_SECS", "0.4"))   # wall budget of the whole constructor pass


def _ctor_scan(data, emit, late):
    """Blob DECODED at load time by an ELF constructor (C __attribute__((constructor)), C++ static initialiser: the
    .init_array targets, x86-64/AArch64 ELF64) into a global/heap buffer under any per-binary scheme (LCG keystream,
    keyed tables, ...): emulate the targets in order, crc-valid blobs absent from the file bytes only. Offset = the
    first file byte of the longest contiguous run of file bytes the hitting constructor READ (= the stored encoded
    blob; speculative), else the constructor's own file offset; detail names the init_array slot."""
    try:
        import unicorn   # noqa: F401
        info = _elf_ctors(data)
    except Exception:   # noqa: BLE001 -- hostile headers
        return
    if not info or not info[3]:
        return
    info = info + (data,)
    fns = info[3][:HCFG_CTOR_MAX]
    end = time.time() + HCFG_CTOR_SECS
    try:
        k, blobs = _ctor_emu(info, fns, end)
    except Exception:   # noqa: BLE001 -- unicorn on hostile bytes: never raise past the scan
        return
    if k is None or late():
        return
    srcs = set()
    try:   # re-run checking after each constructor, reads hooked: which one decoded it, where the stored form sits
        k2, b2 = _ctor_emu(info, fns[:k + 1], time.time() + HCFG_CTOR_SECS, srcs=srcs)
        if k2 is not None:
            k, blobs = k2, b2
        else:
            srcs.clear()
    except Exception:   # noqa: BLE001
        srcs.clear()
    best, cur = (0, info[6](fns[k])), None
    for o in sorted(srcs):
        cur = (cur[0], o) if cur and o == cur[1] + 1 else (o, o)
        if cur[1] - cur[0] + 1 > best[0]:
            best = (cur[1] - cur[0] + 1, cur[0])
    for blob in blobs:
        emit(best[1], "init-decoded", blob, f"{info[0]} init_array[{k}] fn@{info[6](fns[k])} src={best[0]}B")


def _rank(hits):
    """Best first. A NUL-delimited UTF-16 string reads as BOTH LE (at o) and BE (at o-1) with the same text: keep the
    reading that starts 2-byte aligned (compilers align wide strings), LE when both/neither are; the loser is dropped
    and named in the winner's detail."""
    by = {(h.offset, h.encoding): h for h in hits}
    for h in list(hits):
        if h.encoding.startswith("utf16le-"):
            be = by.get((h.offset - 1, "utf16be-" + h.encoding[8:]))
            if be is not None and be.plain == h.plain and be in hits:
                win, lose = (be, h) if (be.offset % 2 == 0 and h.offset % 2) else (h, be)
                hits.remove(lose)
                win.detail = (win.detail + " " if win.detail else "") + f"alt={lose.encoding}@{lose.offset}"
    return sorted(hits, key=lambda h: (not h.valid, h.speculative, h.offset))


def hcfg_find(data, **kw):
    """The first crc-valid HCFG blob (HcfgHit) in `data`, or None."""
    return next((h for h in hcfg_scan(data, stop_on_valid=True, **kw) if h.valid), None)


HCFG_ZIP_MAX = int(os.environ.get("HCTF_HCFG_ZIP_MAX", str(32 << 20)))   # inflated bytes over all zip entries
_ZIP_METHOD = {8: "deflate", 12: "bz2", 14: "lzma"}


def _zip_scan(data, emit, hits, deadline, late, depth):
    """Inflate every compressed non-.class entry of the zip in `data` and report an HCFG inside (see OFFSET LAW)."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
        infos = zf.infolist()[:20000]
    except Exception:  # noqa: BLE001 - not a (readable) zip
        return
    budget = HCFG_ZIP_MAX
    for zi in infos:
        if late() or budget <= 0:
            break
        if (zi.compress_type not in _ZIP_METHOD or zi.filename.endswith(("/", ".class")) or zi.file_size > budget
                or zi.file_size < 12):
            continue
        budget -= zi.file_size
        p = zi.header_offset
        if data[p:p + 4] != b"PK\x03\x04":
            continue
        dstart = p + 30 + int.from_bytes(data[p + 26:p + 28], "little") + int.from_bytes(data[p + 28:p + 30], "little")
        try:
            buf = zf.read(zi)
        except Exception:  # noqa: BLE001 - encrypted / corrupt / unsupported entry
            continue
        tag = f"zip={zi.filename}"
        i, n = buf.find(HCFG_MAGIC), 0
        while i >= 0 and n < 64:
            emit(dstart, _ZIP_METHOD[zi.compress_type], buf[i:i + _need(buf[i:i + 8])], f"at+{i} {tag}" if i else tag)
            i, n = buf.find(HCFG_MAGIC, i + 1), n + 1
        if any(h.valid for h in hits):
            return
        if len(buf) <= 4 << 20:
            for h in hcfg_scan(buf, deadline=deadline, stop_on_valid=True, _depth=depth + 1):
                if h.valid and h.encoding != "raw":
                    h.encoding, h.detail = "zip-" + h.encoding, f"{tag} data@{dstart} {h.detail}".strip()
                    hits.append(h)
                    return


# .NET single-file bundle (`dotnet publish -p:PublishSingleFile=true`): an apphost (ELF / PE / Mach-O) whose data holds
# [i64 manifest offset][the 32-byte '.net core bundle' sha256 signature]; offset 0 = an unbundled apphost. Manifest (.NET
# runtime src/native/corehost/bundle/header.cpp): u32 major, u32 minor, i32 count, str bundle id, v2+: i64 deps offset/size,
# i64 runtimeconfig offset/size, u64 flags; then per file i64 offset, i64 size, v6+: i64 compressed size (0 = stored),
# u8 type, str path (str = 7-bit varint length + UTF-8). Compressed entries (EnableCompressionInSingleFile) = raw deflate.
_BUNDLE_SIG = bytes.fromhex("8b1202b96a612038727b930214d7a03213f5b9e6efae3318ee3b2dce24b36aae")
_BUNDLE_TYPES = {0: "unknown", 1: "assembly", 2: "native", 3: "deps_json", 4: "runtimeconfig_json", 5: "symbols"}
_BUNDLE_FW = re.compile(r"(System|Microsoft|netstandard|mscorlib|WindowsBase)[./]|.*\.(so|dylib|pdb)$")   # no deep scan
HCFG_BUNDLE_MAX = int(os.environ.get("HCTF_HCFG_BUNDLE_MAX", str(32 << 20)))   # inflated bytes over all bundle entries


def dotnet_bundle(data, limit=20000):
    """{"header_offset", "version" ("6.0"), "bundle_id", "flags", "files": [{path, type, offset, size, compressed_size}]}
    of a .NET single-file bundle (offset = file offset of the entry's stored bytes; compressed_size 0 = stored as is),
    None when `data` is no bundle (no signature / unbundled apphost placeholder / manifest out of range)."""
    data = bytes(data)
    s = data.find(_BUNDLE_SIG)
    while s >= 8:
        hdr = int.from_bytes(data[s - 8:s], "little")
        if 0 < hdr < len(data) - 12:
            break
        s = data.find(_BUNDLE_SIG, s + 1)
    else:
        return None
    p = [hdr]

    def u(fmt):
        v = struct.unpack_from(fmt, data, p[0])
        p[0] += struct.calcsize(fmt)
        return v[0] if len(v) == 1 else v

    def s7():
        n = sh = 0
        while True:
            b = data[p[0]]
            p[0] += 1
            n |= (b & 0x7f) << sh
            sh += 7
            if b < 0x80 or sh > 28:
                break
        if p[0] + n > len(data):
            raise ValueError("string past end")
        p[0] += n
        return data[p[0] - n:p[0]].decode("utf-8", "replace")

    try:
        major, minor, count = u("<IIi")
        if not 1 <= major <= 64 or not 0 <= count <= limit:
            return None
        out = {"header_offset": hdr, "version": f"{major}.{minor}", "bundle_id": s7(), "flags": 0, "files": []}
        if major >= 2:
            u("<qqqq")
            out["flags"] = u("<Q")
        for _ in range(count):
            off, size = u("<qq")
            csize = u("<q") if major >= 6 else 0
            typ = u("<B")
            path = s7()
            stored = csize or size
            if off < 0 or size < 0 or csize < 0 or off + stored > len(data):
                return None
            out["files"].append({"path": path, "type": _BUNDLE_TYPES.get(typ, str(typ)), "offset": off, "size": size,
                                 "compressed_size": csize})
        return out
    except _PARSE_ERR:
        return None


def _bundle_scan(data, emit, hits, deadline, late, depth):
    """Inflate every compressed entry of the .NET single-file bundle in `data` and report an HCFG inside: raw -> "deflate"
    at the entry's compressed-data start, detail "at+N bundle=<path>"; any other form -> "bundle-<enc>" at the offset
    INSIDE the inflated entry, detail "bundle=<path> data@<compressed start>" (the zip-entry convention, OFFSET LAW)."""
    b = dotnet_bundle(data)
    budget = HCFG_BUNDLE_MAX
    for f in (b or {}).get("files", ()):
        if late() or budget <= 0:
            break
        if not f["compressed_size"] or f["size"] < 12 or f["size"] > budget:
            continue
        budget -= f["size"]
        try:
            d = zlib.decompressobj(-15)
            buf = d.decompress(data[f["offset"]:f["offset"] + f["compressed_size"]], f["size"])
        except zlib.error:
            continue
        tag, dstart = f"bundle={f['path']}", f["offset"]
        i, n = buf.find(HCFG_MAGIC), 0
        while i >= 0 and n < 64:
            emit(dstart, "deflate", buf[i:i + _need(buf[i:i + 8])], f"at+{i} {tag}" if i else tag)
            i, n = buf.find(HCFG_MAGIC, i + 1), n + 1
        if any(h.valid for h in hits):
            return
        if len(buf) <= 8 << 20 and f["type"] != "native" and not _BUNDLE_FW.match(f["path"]):   # app entries only
            for h in hcfg_scan(buf, deadline=deadline, stop_on_valid=True, _depth=depth + 1):
                if h.valid and h.encoding != "raw":
                    h.encoding, h.detail = "bundle-" + h.encoding, f"{tag} data@{dstart} {h.detail}".strip()
                    hits.append(h)
                    return


_R2R_OS_XOR = {"windows": 0, "linux": 0x7B79, "osx": 0x4644, "freebsd": 0xADC4, "netbsd": 0x1993, "sunos": 0x1992}
_AOT_SECTIONS = {"__managedcode", ".managedcode", "__modules", ".dotnet_eh_table", ".hydrated", "hydrated", ".managed"}


def dotnet_build_facts(data):
    """How a .NET program was published, from the bytes alone: {"format" (container label: "elf" / "pe" / "mach-o", or
    "pe_cli" for a CLI assembly -- a ReadyToRun dll is still pe_cli), "dotnet_build": "singlefile" (apphost + bundle) |
    "apphost" (unbundled host) | "readytorun" (CLI header flag IL_LIBRARY + ManagedNativeHeader 'RTR') | "il" (plain CLI)
    | "nativeaot" (native image: __managedcode/__modules/hydrated sections, no CLI header) | "none"; R2R adds r2r_os +
    the real machine/machine_num (the header's Machine is xor'd with an OS cookie); "main_assembly" /
    "main_assembly_offset" / "bundle_version" / "bundle_files" for a bundle}; None when not an ELF / PE / Mach-O."""
    data = bytes(data)
    mf = machine_facts(data)
    if not mf or mf.get("format") not in ("elf", "pe", "mach-o"):
        return None
    out = {"format": mf["format"], "dotnet_build": "none"}
    pe = _pe_layout(data) if mf["format"] == "pe" else None
    if pe and len(pe[2]) > 14 and pe[2][14][0]:
        out["format"] = "pe_cli"
        try:
            cli = _pe_rva(pe[1], pe[2][14][0])
            flags = struct.unpack_from("<I", data, cli + 16)[0]
            mnh = struct.unpack_from("<I", data, cli + 64)[0]
            mo = _pe_rva(pe[1], mnh) if mnh else None
            r2r = mo is not None and data[mo:mo + 4] == b"RTR\0"
        except _PARSE_ERR:
            flags, r2r = 0, False
        out["dotnet_build"] = "readytorun" if r2r or flags & 0x4 else "il"
        if out["dotnet_build"] == "readytorun":   # crossgen2 stores Machine ^ per-OS cookie (Windows: plain Machine)
            m = int(mf["machine_num"])
            for osn, x in _R2R_OS_XOR.items():
                if (m ^ x) in PE_MACHINE_LABEL:
                    out.update({"r2r_os": osn, "machine": PE_MACHINE_LABEL[m ^ x], "machine_num": str(m ^ x)})
                    break
        return out
    b = dotnet_bundle(data)
    if b:
        asm = [f for f in b["files"] if f["type"] == "assembly"]
        main = b["bundle_id"] and asm and asm[0]
        for f in asm:   # the app's own dll is named like the runtimeconfig.json/deps.json entries
            stem = f["path"].rsplit(".", 1)[0]
            if any(g["path"] in (stem + ".runtimeconfig.json", stem + ".deps.json") for g in b["files"]):
                main = f
                break
        out.update({"dotnet_build": "singlefile", "bundle_version": b["version"], "bundle_files": len(b["files"]),
                    "main_assembly": main["path"] if main else "none",
                    "main_assembly_offset": main["offset"] if main else None,
                    "main_assembly_compressed": bool(main and main["compressed_size"])})
        return out
    if _BUNDLE_SIG in data:
        out["dotnet_build"] = "apphost"
        return out
    if pe:
        names = {n for n, *_ in pe[1]}
    elif mf["format"] == "elf":
        names = {n for n, _, _ in (_elf_layout(data) or (0, []))[1]}
    else:
        names = set((macho_layout(data) or {}).get("section_names_short") or ())
    if names & _AOT_SECTIONS:
        out["dotnet_build"] = "nativeaot"
    return out


# .NET metadata facts (d03 family: a plain IL dll/exe). Lists are compact JSON in metadata TABLE order, names exactly as
# stored (`<Module>`, `<PrivateImplementationDetails>`, nested `__StaticArrayInitTypeSize=N`, `.ctor`/`.cctor` kept).
_DN_ATTR_FACTS = {"TargetFrameworkAttribute": "target_framework", "AssemblyFileVersionAttribute": "file_version",
                  "AssemblyInformationalVersionAttribute": "informational_version", "AssemblyTitleAttribute": "title",
                  "AssemblyCompanyAttribute": "company", "AssemblyProductAttribute": "product",
                  "AssemblyConfigurationAttribute": "configuration", "AssemblyDescriptionAttribute": "description",
                  "AssemblyCopyrightAttribute": "copyright", "GuidAttribute": "guid_attribute"}
_DN_TFM = {".NETCoreApp": "net", ".NETFramework": "net", ".NETStandard": "netstandard"}


def _dn_serstr(blob):
    """First fixed arg of a custom-attribute blob when it is a SerString (prolog 01 00, compressed len, UTF-8)."""
    if len(blob) < 3 or blob[:2] != b"\x01\x00" or blob[2] == 0xFF:
        return None
    n, p = blob[2], 3
    if n & 0x80:
        n, p = (((n & 0x3F) << 8) | blob[3], 4) if not n & 0x40 else (((n & 0x1F) << 24) | int.from_bytes(blob[3:6], "big"), 6)
    return blob[p:p + n].decode("utf-8", "replace") if p + n <= len(blob) else None


def _dn_tfm(tf):
    """'.NETCoreApp,Version=v10.0' -> 'net10.0'; '.NETFramework,Version=v4.7.2' -> 'net472'; netstandard2.0."""
    m = re.match(r"(\.NET\w+),Version=v(\d+(?:\.\d+)*)$", tf or "")
    if not m or m.group(1) not in _DN_TFM:
        return "none"
    v = m.group(2)
    return "net" + v.replace(".", "") if m.group(1) == ".NETFramework" else _DN_TFM[m.group(1)] + v


def dotnet_meta_facts(data):
    """ECMA-335 metadata facts of a .NET (CLI) PE via dnfile: assembly_name / assembly_version (a.b.c.d) / assembly_culture,
    module_name, mvid (lowercase dashed guid), runtime_version (metadata 'v4.0.30319'), typedefs / typedefs_full
    (Namespace.Name) / typedef_count, methods / method_count, fields / field_count, field_rva_count / has_field_rva
    ("true"/"false"), entry_point_token ("0x06000001", "none" for a library), entry_point (Namespace.Type.Method),
    assembly_refs, target_framework ('.NETCoreApp,Version=v10.0') + tfm ('net10.0', the runtimeconfig form), and the
    assembly-level string attributes (file_version, informational_version, title, company, product, configuration, ...).
    All values are strings; absent -> "none". None when the bytes are not a CLI assembly."""
    try:
        import dnfile
        pe = dnfile.dnPE(data=bytes(data), fast_load=False)
        net = pe.net
        if net is None or net.mdtables is None:
            return None
        t = net.mdtables
    except Exception:   # noqa: BLE001 -- hostile/truncated PE: cannot answer
        return None
    out = {}
    js = lambda xs: json.dumps(list(xs), separators=(",", ":"), ensure_ascii=False)   # noqa: E731
    rows = lambda tab: list(getattr(t, tab, None) or ())   # noqa: E731

    def nm(x):
        return "" if x is None else str(x)

    def step(key, fn):
        try:
            out[key] = fn()
        except Exception:   # noqa: BLE001 -- one broken table must not hide the others
            out.setdefault(key, "none")
    asm = rows("Assembly")
    a = asm[0] if asm else None
    step("assembly_name", lambda: nm(a.Name) if a else "none")
    step("assembly_version", lambda: f"{a.MajorVersion}.{a.MinorVersion}.{a.BuildNumber}.{a.RevisionNumber}" if a else "none")
    step("assembly_culture", lambda: (nm(a.Culture) or "none") if a else "none")
    mods = rows("Module")
    step("module_name", lambda: nm(mods[0].Name) if mods else "none")
    step("mvid", lambda: str(mods[0].Mvid).lower() if mods and mods[0].Mvid is not None else "none")
    step("runtime_version", lambda: bytes(net.metadata.struct.Version).split(b"\0")[0].decode("ascii", "replace") or "none")
    tds = rows("TypeDef")
    full = [(nm(r.TypeNamespace) + "." if nm(r.TypeNamespace) else "") + nm(r.TypeName) for r in tds]
    step("typedefs", lambda: js(nm(r.TypeName) for r in tds))
    step("typedefs_full", lambda: js(full))
    out["typedef_count"] = str(len(tds))
    mds = rows("MethodDef")
    step("methods", lambda: js(nm(r.Name) for r in mds))
    out["method_count"] = str(len(mds))
    fds = rows("Field")
    step("fields", lambda: js(nm(r.Name) for r in fds))
    out["field_count"] = str(len(fds))
    rv = [r for r in rows("FieldRva") if getattr(r, "Rva", 0)]
    out["field_rva_count"] = str(len(rv))
    out["has_field_rva"] = "true" if rv else "false"
    step("assembly_refs", lambda: js(nm(r.Name) for r in rows("AssemblyRef")))

    def us_heap():   # #US: [compressed len][UTF-16LE][1 trailing flag byte]; empty entries skipped
        h, p, got = bytes(getattr(net.user_strings, "__data__", b"") or b""), 1, []
        while p < len(h) and len(got) < 20000:
            n, q = h[p], p + 1
            if n & 0x80:
                n, q = (((n & 0x3F) << 8) | h[p + 1], p + 2) if not n & 0x40 else \
                    (((n & 0x1F) << 24) | int.from_bytes(h[p + 1:p + 4], "big"), p + 4)
            if n == 0 and h[p] == 0:
                break   # zero padding at the end of the heap
            if n > 1:
                got.append(h[q:q + n - 1].decode("utf-16-le", "replace"))
            p = q + n
        return js(got)
    step("user_strings", us_heap)

    def entry():
        tok = int(net.struct.EntryPointTokenOrRva or 0)
        if not tok or net.Flags.CLR_NATIVE_ENTRYPOINT:
            out["entry_point_token"] = "none" if not tok else f"0x{tok:08x}"
            return "none"
        out["entry_point_token"] = f"0x{tok:08x}"
        idx = tok & 0xFFFFFF
        if tok >> 24 != 6 or not 0 < idx <= len(mds):
            return "none"
        owner = None   # dnfile expands each TypeDef's MethodList run (ECMA-335 II.22.37)
        for i, r in enumerate(tds):
            if r.MethodList and any(x.row_index == idx for x in r.MethodList):
                owner = full[i]
                break
        return f"{owner}.{nm(mds[idx - 1].Name)}" if owner else nm(mds[idx - 1].Name)
    out["entry_point_token"] = "none"
    step("entry_point", entry)
    for k in _DN_ATTR_FACTS.values():
        out[k] = "none"
    try:
        for ca in rows("CustomAttribute"):
            par, ty = ca.Parent, ca.Type
            if not par or not ty or getattr(par.table, "name", "") != "Assembly":
                continue
            r = ty.row
            cls = getattr(r, "Class", None) if getattr(ty.table, "name", "") == "MemberRef" else None
            tn = nm(getattr(cls.row, "TypeName", None)) if cls is not None and cls.row is not None else ""
            key = _DN_ATTR_FACTS.get(tn)
            if key and out[key] == "none":
                v = _dn_serstr(bytes(ca.Value.value or b""))
                if v is not None:
                    out[key] = v
    except Exception:   # noqa: BLE001
        pass
    out["tfm"] = _dn_tfm(out["target_framework"])
    return out


_DN_FIELD_ALIASES = {"name": "assembly_name", "version": "assembly_version", "types": "typedefs",
                     "type_names": "typedefs", "typedef_names": "typedefs", "type_count": "typedef_count",
                     "method_names": "methods", "methoddef_names": "methods", "field_names": "fields",
                     "entry_point_token_hex": "entry_point_token", "entrypoint_token": "entry_point_token",
                     "target_framework_moniker": "tfm", "runtimeconfig_tfm": "tfm", "module_mvid": "mvid"}


def dotnet_meta_field(data, name):
    """One dotnet_meta_facts value by name (aliases: version, types, method_names, ...); "none" when the field is absent,
    None when `data` is not a CLI assembly or the name is unknown."""
    f = dotnet_meta_facts(data)
    if f is None:
        return None
    return f.get(_DN_FIELD_ALIASES.get(name, name))


# ------------------------------------------------------------------ container slots: PE/.NET resources, overlay
_PARSE_ERR = (struct.error, IndexError, OverflowError, ValueError, TypeError)   # hostile header fields
_RT_NAMES = {1: "CURSOR", 2: "BITMAP", 3: "ICON", 4: "MENU", 5: "DIALOG", 6: "STRING", 7: "FONTDIR", 8: "FONT",
             9: "ACCELERATOR", 10: "RCDATA", 11: "MESSAGETABLE", 12: "GROUP_CURSOR", 14: "GROUP_ICON", 16: "VERSION",
             17: "DLGINCLUDE", 19: "PLUGPLAY", 20: "VXD", 21: "ANICURSOR", 22: "ANIICON", 23: "HTML", 24: "MANIFEST"}


def _pe_layout(data):
    """(optional-header end, [(name, va, vsize, raw_ptr, raw_size)], [(rva, size)] data dirs) or None."""
    try:
        if data[:2] != b"MZ":
            return None
        pe = int.from_bytes(data[0x3c:0x40], "little")
        if data[pe:pe + 4] != b"PE\0\0":
            return None
        nsec, optsz = struct.unpack_from("<H12xH", data, pe + 6)
        opt = pe + 24
        magic = struct.unpack_from("<H", data, opt)[0]
        dd = opt + (112 if magic == 0x20b else 96)
        ndd = min(16, struct.unpack_from("<I", data, dd - 4)[0])
        dirs = [struct.unpack_from("<II", data, dd + 8 * k) for k in range(ndd) if dd + 8 * k + 8 <= opt + optsz]
        secs = []
        for k in range(min(nsec, 96)):
            o = opt + optsz + 40 * k
            name = data[o:o + 8].rstrip(b"\0").decode("latin-1")
            vsize, va, rsize, rptr = struct.unpack_from("<IIII", data, o + 8)
            secs.append((name, va, vsize, rptr, rsize))
        return opt + optsz, secs, dirs
    except _PARSE_ERR:
        return None


def _pe_rva(secs, rva):
    for _, va, vsize, rptr, rsize in secs:
        if va <= rva < va + max(vsize, rsize):
            return rva - va + rptr
    return rva if not secs or rva < min(s[1] for s in secs) else None


def _elf_layout(data):
    """(end of everything the headers describe, [(name, offset, size)] sections) or None."""
    try:
        if data[:4] != b"\x7fELF" or data[4] not in (1, 2) or data[5] not in (1, 2):
            return None
        e = "<" if data[5] == 1 else ">"
        if data[4] == 1:
            phoff, shoff = struct.unpack_from(e + "II", data, 28)
            ehsize, phes, phn, shes, shn, shstr = struct.unpack_from(e + "6H", data, 40)
            ph, sh = (e + "4xI4xI"), (e + "I4x4x4x4xII")   # p_offset, p_filesz ; sh_name .. sh_offset, sh_size
        else:
            phoff, shoff = struct.unpack_from(e + "QQ", data, 32)
            ehsize, phes, phn, shes, shn, shstr = struct.unpack_from(e + "6H", data, 52)
            ph, sh = (e + "8xQ8x8xQ"), (e + "I4x8x8xQQ")
        end = max(ehsize, phoff + phn * phes if phn else 0, shoff + shn * shes if shn else 0)
        for k in range(min(phn, 4096)):
            o, n = struct.unpack_from(ph, data, phoff + k * phes)
            end = max(end, o + n)
        raw = []
        for k in range(min(shn, 65535)):
            b = shoff + k * shes
            nm, o, n = struct.unpack_from(sh, data, b)
            if struct.unpack_from(e + "I", data, b + 4)[0] != 8:   # SHT_NOBITS occupies no file bytes
                end = max(end, o + n)
                raw.append((nm, o, n))
        names = b""
        if shn and shstr < shn:
            _, so, sn = struct.unpack_from(sh, data, shoff + shstr * shes)
            names = data[so:so + sn]
        secs = [(names[nm:names.find(b"\0", nm)].decode("latin-1") if nm < len(names) else "", o, n) for nm, o, n in raw]
        return end, secs
    except _PARSE_ERR:
        return None


def overlay_info(data):
    """{"has_overlay", "overlay_offset" (None when absent), "overlay_size"} for an ELF or PE, None for anything else.
    PE: bytes past every header-described region (optional header, section raw data, data directories other than the
    certificate table) = pefile's get_overlay_data_start_offset(). ELF: bytes past the ELF header, program/section
    header tables, every PT_* segment's file bytes and every non-NOBITS section (lief's Binary.overlay)."""
    data = bytes(data)
    pe = _pe_layout(data)
    if pe:
        hdr_end, secs, dirs = pe
        end = hdr_end
        for _, _, _, rptr, rsize in secs:
            if end < rptr + rsize <= len(data):
                end = rptr + rsize
        for k, (rva, size) in enumerate(dirs):
            o = _pe_rva(secs, rva) if k != 4 and (rva or size) else None
            if o is not None and end < o + size <= len(data):
                end = o + size
    else:
        el = _elf_layout(data)
        if not el:
            return None
        end = el[0]
    has = len(data) > end
    return {"has_overlay": has, "overlay_offset": end if has else None, "overlay_size": max(0, len(data) - end)}


def pe_resources(data, limit=4096):
    """[{type, type_name, name, lang, offset, size}] for every leaf of the PE resource tree (offset = file offset of
    the resource DATA start; ids are ints, named entries are str), [] when there is none / not a PE."""
    data = bytes(data)
    pe = _pe_layout(data)
    if not pe or len(pe[2]) < 3 or not pe[2][2][0]:
        return []
    secs = pe[1]
    base = _pe_rva(secs, pe[2][2][0])
    out = []
    if base is None:
        return out

    def ident(v):
        if v & 0x80000000:
            o = base + (v & 0x7fffffff)
            n = int.from_bytes(data[o:o + 2], "little")
            return data[o + 2:o + 2 + 2 * n].decode("utf-16-le", "replace")
        return v

    def walk(off, path, depth):
        try:
            nn, ni = struct.unpack_from("<HH", data, base + off + 12)
            for k in range(min(nn + ni, limit)):
                v, child = struct.unpack_from("<II", data, base + off + 16 + 8 * k)
                if len(out) >= limit:
                    return
                if child & 0x80000000:
                    if depth < 3:
                        walk(child & 0x7fffffff, path + [ident(v)], depth + 1)
                else:
                    rva, size = struct.unpack_from("<II", data, base + child)
                    p = path + [ident(v)] + [None] * 3
                    o = _pe_rva(secs, rva)
                    out.append({"type": p[0], "type_name": _RT_NAMES.get(p[0], p[0]), "name": p[1], "lang": p[2],
                                "offset": o, "size": size})
        except _PARSE_ERR:
            return

    walk(0, [], 0)
    return out


def dotnet_resources(data, limit=4096):
    """[{offset, size}] of the .NET manifest resources embedded in the CLI Resources blob (offset = first DATA byte,
    i.e. past each resource's u32 length prefix; Roslyn 8-aligns them), [] when there is none / not a .NET PE."""
    data = bytes(data)
    pe = _pe_layout(data)
    if not pe or len(pe[2]) < 15 or not pe[2][14][0]:
        return []
    cli = _pe_rva(pe[1], pe[2][14][0])
    try:
        rva, size = struct.unpack_from("<II", data, cli + 24)
    except _PARSE_ERR:
        return []
    lo = _pe_rva(pe[1], rva) if rva else None
    out = []
    if lo is None:
        return out
    p, end = lo, min(lo + size, len(data))
    while p + 4 <= end and len(out) < limit:
        n = int.from_bytes(data[p:p + 4], "little")
        if not n or p + 4 + n > end:
            if (p - lo) % 8 and not n:   # alignment padding between resources
                p += 8 - (p - lo) % 8
                continue
            break
        out.append({"offset": p + 4, "size": n})
        p += 4 + n
    return out


def hcfg_locate(data, off):
    """Which container slot holds file offset `off` (a Hit.offset): {"container": "pe-resource" | "dotnet-resource" |
    "dotnet-bundle" | "overlay" | "section", "slot_offset" (resource data start / bundle entry start = the embedded
    dll's offset / overlay start / section start), "delta" (off - slot), + type_name/name/lang | path/file_type (+ inner
    = the slot inside a stored bundled dll) | section}, or None. For a resource/entry/overlay-relative offset question."""
    data = bytes(data)
    for r in pe_resources(data):
        if r["offset"] is not None and r["offset"] <= off < r["offset"] + r["size"]:
            return {"container": "pe-resource", "slot_offset": r["offset"], "delta": off - r["offset"],
                    "type_name": r["type_name"], "name": r["name"], "lang": r["lang"], "size": r["size"]}
    for r in dotnet_resources(data):
        if r["offset"] <= off < r["offset"] + r["size"]:
            return {"container": "dotnet-resource", "slot_offset": r["offset"], "delta": off - r["offset"],
                    "size": r["size"]}
    for f in (dotnet_bundle(data) or {}).get("files", ()):   # .NET single-file bundle entry (stored or compressed bytes)
        if f["offset"] <= off < f["offset"] + (f["compressed_size"] or f["size"]):
            r = {"container": "dotnet-bundle", "slot_offset": f["offset"], "delta": off - f["offset"], "path": f["path"],
                 "file_type": f["type"], "size": f["size"], "compressed_size": f["compressed_size"]}
            if not f["compressed_size"] and f["type"] == "assembly":   # resource/section inside the embedded dll
                inner = hcfg_locate(data[f["offset"]:f["offset"] + f["size"]], off - f["offset"])
                if inner:
                    r["inner"] = inner
            return r
    ov = overlay_info(data)
    if ov and ov["has_overlay"] and off >= ov["overlay_offset"]:
        return {"container": "overlay", "slot_offset": ov["overlay_offset"], "delta": off - ov["overlay_offset"],
                "size": ov["overlay_size"]}
    pe = _pe_layout(data)
    secs = [(n, rp, rs) for n, _, _, rp, rs in pe[1]] if pe else (_elf_layout(data) or (0, []))[1]
    for n, o, size in secs:
        if o <= off < o + size and n:
            return {"container": "section", "section": n, "slot_offset": o, "delta": off - o, "size": size}
    return None



# Day 17 `hcfg_storage` (kind enum): the GM's rule list, applied IN ORDER -- base64 (crc-valid HCFG only after decoding a
# printable base64 carrier; d08/d09/d11/d13, jars d06/d07) -> raw_hcfg_section (literal HCFG starts in a native section
# named exactly .hcfg; d14, also d02/d10/d15) -> wasm_data_segment (inside a wasm data segment; d16) -> raw_const_array
# (any OTHER native data section: d12 FPC .data, d04 Go .noptrdata, d05/d17 .rodata) -> raw. GM-confirmed: d08/d09/d11-d14.
HCFG_STORAGE_TOKENS = ("raw", "base64", "raw_const_array", "raw_hcfg_section", "wasm_data_segment")
_HCFG_B64_ENC = ("base64", "base64url")


def hcfg_section_of(data, off):
    """{container elf/pe/mach-o/wasm, section, data (bool: a native DATA section), flags} of the section holding file
    offset `off`; {container, section None} when the container parses but no section holds it; None for an unknown
    container. Data = ELF SHF_ALLOC && !SHF_EXECINSTR (not NOBITS); PE IMAGE_SCN_CNT_INITIALIZED_DATA && !MEM_EXECUTE;
    Mach-O no S_ATTR_*_INSTRUCTIONS and segment __DATA* or __TEXT,__const/__cstring/__literal*; wasm = data segment."""
    try:
        data = bytes(data)
        if data[:4] == b"\x7fELF":
            e, b64 = ("<" if data[5] == 1 else ">"), data[4] == 2
            shoff = struct.unpack_from(e + ("Q" if b64 else "I"), data, 40 if b64 else 32)[0]
            shes, shn, shstr = struct.unpack_from(e + "3H", data, 58 if b64 else 46)
            fmt = e + ("IIQQQQ" if b64 else "IIIIII")   # name, type, flags, addr, offset, size
            secs = [struct.unpack_from(fmt, data, shoff + k * shes) for k in range(min(shn, 65535))] if shoff else []
            names = b""
            if shstr < len(secs):
                names = data[secs[shstr][4]:secs[shstr][4] + secs[shstr][5]]
            for nm, t, fl, _, o, n in secs:
                if t != 8 and t != 0 and o <= off < o + n:   # SHT_NOBITS / SHT_NULL hold no file bytes
                    name = names[nm:names.find(b"\0", nm)].decode("latin-1") if nm < len(names) else ""
                    return {"container": "elf", "section": name, "flags": fl, "data": bool(fl & 2 and not fl & 4)}
            return {"container": "elf", "section": None}
        lay = _pe_layout(data)
        if lay:
            pe = int.from_bytes(data[0x3c:0x40], "little")
            first = pe + 24 + struct.unpack_from("<H", data, pe + 20)[0]
            for k, (name, _, _, rp, rs) in enumerate(lay[1]):
                if rs and rp <= off < rp + rs:
                    ch = struct.unpack_from("<I", data, first + 40 * k + 36)[0]
                    return {"container": "pe", "section": name, "flags": ch,
                            "data": bool(ch & 0x40 and not ch & 0x20000020)}
            return {"container": "pe", "section": None}
        mo = macho_layout(data)
        if mo:
            for x in (x for s in mo["slices"] for x in s["sections"]):
                if x["offset"] and x["offset"] <= off < x["offset"] + x["size"] and x["flags"] & 0xff not in (1, 0xc):
                    seg, sect, fl = x["segment"], x["section"], x["flags"]
                    dat = not fl & 0x80000400 and (seg.startswith("__DATA") or seg == "__TEXT" and (
                        sect in ("__const", "__cstring") or sect.startswith("__literal")))
                    return {"container": "mach-o", "section": sect, "segment": seg, "flags": fl, "data": bool(dat)}
            return {"container": "mach-o", "section": None}
        wl = wasm_layout(data)
        if wl:
            for sg in wl["data_segments"]:
                if sg["file_offset"] <= off < sg["file_offset"] + sg["size"]:
                    return {"container": "wasm", "section": "data", "segment_index": sg["index"], "data": True}
            return {"container": "wasm", "section": None}
    except _PARSE_ERR:
        return None
    return None


# --- file offset -> container location (likely next ids: hcfg_section, hcfg_va/hcfg_vaddr, hcfg_rva, hcfg_segment,
# hcfg_mem_offset). Spellings tried first: section name verbatim (".rodata"), addresses lowercase 0x hex (as
# entry_point). SPECULATIVE: ELF rva = vaddr - lowest PT_LOAD (p_vaddr - p_offset) base; Mach-O rva = vaddr - vmaddr
# of the segment mapping file offset 0 (__TEXT).
_ELF_SHF = ((1, "W"), (2, "A"), (4, "X"), (0x10, "M"), (0x20, "S"), (0x40, "I"), (0x80, "L"), (0x100, "O"),
            (0x200, "G"), (0x400, "T"), (0x800, "C"), (0x80000000, "E"))
LOCATE_KEYS = ("container", "section", "section_flags", "segment", "segment_index", "segment_flags", "vaddr", "rva",
               "wasm_data_index", "wasm_mem_offset")


def _hx(v):
    return "none" if v is None else f"0x{v:x}"


def _locate_elf(data, off, out):
    e, b64 = ("<" if data[5] == 1 else ">"), data[4] == 2
    if b64:
        phoff, shoff = struct.unpack_from(e + "QQ", data, 32)
        phes, phn, shes, shn, shstr = struct.unpack_from(e + "5H", data, 54)
    else:
        phoff, shoff = struct.unpack_from(e + "II", data, 28)
        phes, phn, shes, shn, shstr = struct.unpack_from(e + "5H", data, 42)
    loads, seg = [], None
    for k in range(min(phn, 4096) if phoff else 0):
        o = phoff + k * phes
        if o + (56 if b64 else 32) > len(data):
            break
        if b64:
            t, fl, po, va, _, fs = struct.unpack_from(e + "IIQQQQ", data, o)
        else:
            t, po, va, _, fs, _, fl = struct.unpack_from(e + "7I", data, o)
        if t != 1:   # PT_LOAD only: the mapping that gives a file byte its address
            continue
        loads.append(va - po)
        if seg is None and fs and po <= off < po + fs:
            seg = (k, fl, va + off - po)
    sec = None
    if shoff and shes >= (64 if b64 else 40):
        fmt = e + ("IIQQQQ" if b64 else "6I")   # name, type, flags, addr, offset, size
        rows = []
        for k in range(min(shn, 65535)):
            b = shoff + k * shes
            if b + shes > len(data):
                break
            rows.append(struct.unpack_from(fmt, data, b))
        names = b""
        if shstr < len(rows):
            names = bytes(data[rows[shstr][4]:rows[shstr][4] + rows[shstr][5]])
        for nm, t, fl, ad, o, n in rows:
            if t not in (0, 8) and o <= off < o + n:   # SHT_NULL / SHT_NOBITS hold no file bytes
                z = names.find(b"\0", nm)
                sec = (names[nm:z if z >= 0 else len(names)].decode("latin-1") if nm < len(names) else "", fl, ad, o)
                break
    out["container"] = "elf"
    if sec:
        out["section"] = sec[0]
        out["section_flags"] = "".join(c for bit, c in _ELF_SHF if sec[1] & bit)
    va = sec[2] + off - sec[3] if sec and sec[1] & 2 and sec[2] else (seg[2] if seg else None)
    if seg:
        out["segment"], out["segment_index"] = "LOAD", seg[0]
        out["segment_flags"] = "".join(c for bit, c in ((4, "R"), (2, "W"), (1, "E")) if seg[1] & bit)
    if va is not None:
        out["vaddr"] = _hx(va)
        out["rva"] = _hx(va - min(loads)) if loads and va >= min(loads) else "none"


def _locate_pe(data, off, lay, out):
    pe = int.from_bytes(data[0x3c:0x40], "little")
    opt = pe + 24
    base = struct.unpack_from("<Q" if struct.unpack_from("<H", data, opt)[0] == 0x20b else "<I", data,
                              opt + (24 if struct.unpack_from("<H", data, opt)[0] == 0x20b else 28))[0]
    first = opt + struct.unpack_from("<H", data, pe + 20)[0]
    out["container"] = "pe"
    for k, (name, va, vs, rp, rs) in enumerate(lay[1]):
        if rs and rp <= off < rp + rs:
            out["section"] = name
            out["section_flags"] = _hx(struct.unpack_from("<I", data, first + 40 * k + 36)[0])
            out["segment_index"] = k
            out["rva"], out["vaddr"] = _hx(va + off - rp), _hx(base + va + off - rp)
            return
    if off < lay[0] or (lay[1] and off < min((s[3] for s in lay[1] if s[4]), default=0)):
        out["rva"], out["vaddr"] = _hx(off), _hx(base + off)   # headers map 1:1 at the image base


def _locate_macho(data, off, out):
    mo = macho_layout(data)
    if not mo:
        return False
    out["container"] = "mach-o"
    sl = None
    for s in mo["slices"]:
        if s["slice_offset"] <= off:
            sl = s if sl is None or s["slice_offset"] >= sl["slice_offset"] else sl
    if sl is None:
        return True
    end, base = sl["endian"], sl["slice_offset"]
    u32 = lambda o: int.from_bytes(data[o:o + 4], end)   # noqa: E731
    p = base + (32 if sl["bits"] == 64 else 28)
    stop = min(len(data), p + u32(base + 20))
    text_va = None
    for _ in range(min(u32(base + 16), 4096)):
        if p + 8 > stop:
            break
        cmd, size = u32(p), u32(p + 4)
        if size < 8:
            break
        if cmd in (0x1, 0x19):
            w = 8 if cmd == 0x19 else 4
            uw = lambda o: int.from_bytes(data[o:o + w], end)   # noqa: E731
            segname = bytes(data[p + 8:p + 24]).split(b"\0")[0].decode("latin-1")
            vmaddr, fileoff, filesize = uw(p + 24), uw(p + 24 + 2 * w), uw(p + 24 + 3 * w)
            if fileoff == 0 and filesize:
                text_va = vmaddr if text_va is None else text_va
            if filesize and base + fileoff <= off < base + fileoff + filesize and out["segment"] == "none":
                out["segment"], out["vaddr"] = segname, _hx(vmaddr + off - base - fileoff)
                out["segment_flags"] = _hx(u32(p + 24 + 4 * w + 4))   # initprot
                nsects = u32(p + 24 + 4 * w + 8)
                q, ssz = p + 24 + 4 * w + 16, 80 if w == 8 else 68
                for _s in range(min(nsects, 1024)):
                    if q + ssz > min(stop, p + size):
                        break
                    addr, sz, so = uw(q + 32), uw(q + 32 + w), u32(q + 32 + 2 * w)
                    fl = u32(q + 48 + 2 * w)
                    if so and fl & 0xff not in (1, 0xc) and base + so <= off < base + so + sz:
                        out["section"] = bytes(data[q:q + 16]).split(b"\0")[0].decode("latin-1")
                        out["section_flags"] = _hx(fl)
                        if not segname:   # MH_OBJECT: one unnamed segment, the section names its own segname
                            out["segment"] = bytes(data[q + 16:q + 32]).split(b"\0")[0].decode("latin-1") or "none"
                        out["vaddr"] = _hx(addr + off - base - so)
                        break
                    q += ssz
        p += size
    if out["vaddr"] != "none" and text_va is not None:
        out["rva"] = _hx(int(out["vaddr"], 16) - text_va)
    return True


def locate_offset(data, off):
    """Map file offset `off` to its container location -> {container elf/pe/mach-o/wasm, section (name verbatim:
    ".rodata", PE ".data", Mach-O sectname "__const", wasm section name "data"/"code"/custom name), section_flags (ELF
    readelf letters "WA"/"AX"; PE characteristics / Mach-O section flags as 0x hex), segment (ELF "LOAD", Mach-O
    segment name "__DATA"), segment_index (ELF program-header index of the PT_LOAD holding it; PE section index),
    segment_flags (ELF "R"/"RW"/"RE"; Mach-O initprot hex), vaddr / rva (lowercase 0x hex), wasm_data_index,
    wasm_mem_offset (int: segment memory offset + delta, "none" for a passive / global-based segment)}. Absent fields
    are the literal "none". ELF works on sstripped files (no section headers -> program headers only). None for an
    unknown container or an offset outside the file. Pure struct parsing, never raises."""
    try:
        data = bytes(data) if not isinstance(data, (bytes, bytearray)) else data
        if not isinstance(off, int) or not 0 <= off < len(data):
            return None
        out = dict.fromkeys(LOCATE_KEYS, "none")
        if data[:4] == b"\x7fELF" and len(data) >= 52 and data[4] in (1, 2) and data[5] in (1, 2):
            _locate_elf(data, off, out)
            return out
        lay = _pe_layout(data)
        if lay:
            _locate_pe(data, off, lay, out)
            return out
        if _MO_MAGIC.get(bytes(data[:4])) or data[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
            if _locate_macho(data, off, out):
                return out
        wl = wasm_layout(data) if data[:4] == b"\0asm" else None
        if wl:
            out["container"] = "wasm"
            for s in wl["sections"]:
                if s["offset"] <= off < s["offset"] + s["size"]:
                    out["section"] = s["name"]
            for sg in wl["data_segments"]:
                if sg["file_offset"] <= off < sg["file_offset"] + sg["size"]:
                    out["wasm_data_index"] = sg["index"]
                    mo = sg["mem_offset"]
                    out["wasm_mem_offset"] = "none" if mo is None else mo + off - sg["file_offset"]
            return out
    except _PARSE_ERR:
        return None
    return None


def hcfg_storage(data, hit=None):
    """GM `hcfg_storage` token (HCFG_STORAGE_TOKENS) for the validated HCFG `hit` (HcfgHit or a dict with offset +
    encoding; found with hcfg_find when omitted -- a zip/jar scans its application classes / entries). "none" when no
    crc-valid HCFG exists; None (not a guess) when the hit's encoding is outside the rule list (hex, xor, zlib, ...),
    or a literal HCFG lies in no section of a parsed native/wasm container (header, overlay, wasm code). A jar's
    literal HCFG (class constant pool, no native section) and a blob in an unknown container -> "raw". SPECULATIVE
    edges: d03 .NET FieldRVA in PE .text (code section) -> "raw" (alternative raw_const_array); Mach-O __hcfg counts as
    the .hcfg section."""
    try:
        data = bytes(data)
        if hit is None:
            if data[:2] == b"PK":
                for _, cls in jar_app_classes(data):
                    tok = hcfg_storage(cls)
                    if tok != "none":
                        return tok
                try:
                    zf = zipfile.ZipFile(io.BytesIO(data))
                    for i in zf.infolist()[:2000]:
                        if not i.filename.endswith(".class") and 0 < i.file_size <= HCFG_ZIP_MAX:
                            tok = hcfg_storage(zf.read(i))
                            if tok != "none":
                                return tok
                except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError, EOFError, zlib.error):
                    pass
                return "none"
            hit = hcfg_find(data)
            if hit is None:
                return "none"
        g = hit.get if isinstance(hit, dict) else lambda k: getattr(hit, k, None)
        enc, off = g("encoding"), g("offset")
        if enc in _HCFG_B64_ENC:
            return "base64"
        if enc not in ("raw", "split-raw") or not isinstance(off, int) or data[off:off + 4] != HCFG_MAGIC:
            return None
        loc = hcfg_section_of(data, off)
        if loc is None:
            return "raw"
        if loc["section"] is None:
            return None
        if loc["container"] != "wasm" and loc["section"] in (".hcfg", "__hcfg"):
            return "raw_hcfg_section"
        if loc["container"] == "wasm":
            return "wasm_data_segment"
        return "raw_const_array" if loc["data"] else "raw"
    except _PARSE_ERR:
        return None


# --- same-source build pairs (D15 stripped/symbolized, D16 compact/direct; D17+ O0/O2, static/dynamic, pie/nopie,
# debug/release, packed/unpacked, plain/obfuscated). Ids are `dNN_analysis_<tag>_<field>`: the tag names ONE member.

def _elf_pair_facts(data):
    E = "<" if data[5] == 1 else ">"
    b64 = data[4] == 2
    u16 = lambda o: struct.unpack_from(E + "H", data, o)[0]
    u32 = lambda o: struct.unpack_from(E + "I", data, o)[0]
    uw = (lambda o: struct.unpack_from(E + "Q", data, o)[0]) if b64 else u32
    et, entry = u16(16), uw(24)
    phoff, shoff = (uw(32), uw(40)) if b64 else (u32(28), u32(32))
    p = 52 if b64 else 40
    phes, phn, shes, shn, shstr = u16(p + 2), u16(p + 4), u16(p + 6), u16(p + 8), u16(p + 10)
    ptypes, xseg = [], 0
    for k in range(min(phn, 256) if phoff else 0):
        o = phoff + k * phes
        if o + (56 if b64 else 32) > len(data):
            break
        t = u32(o)
        ptypes.append(t)
        flags, filesz = (u32(o + 4), uw(o + 32)) if b64 else (u32(o + 24), u32(o + 16))
        if t == 1 and flags & 1:   # PT_LOAD + PF_X
            xseg += filesz
    secs = []   # (name_off, type, flags, offset, size, link, entsize)
    if shoff and shes >= (64 if b64 else 40):
        for k in range(min(shn, 4096)):
            o = shoff + k * shes
            if o + shes > len(data):
                break
            if b64:
                secs.append((u32(o), u32(o + 4), uw(o + 8), uw(o + 24), uw(o + 32), u32(o + 40), uw(o + 56)))
            else:
                secs.append((u32(o), u32(o + 4), u32(o + 8), u32(o + 16), u32(o + 20), u32(o + 24), u32(o + 36)))

    def cstr(i, off):
        if not 0 <= i < len(secs):
            return ""
        s = secs[i][3] + off
        e = data.find(b"\0", s, s + 4096)
        return data[s:e].decode("utf-8", "replace") if s < len(data) and e >= s else ""

    names = [cstr(shstr, s[0]) if shstr < len(secs) else "" for s in secs]
    imports, needed = [], []
    for i, (_, t, _, off, size, link, ent) in enumerate(secs):
        if t == 11 and ent:   # .dynsym: undefined (SHN_UNDEF) named symbols = what the image imports
            for k in range(1, min(size // ent, 50000)):
                o = off + k * ent
                if o + ent > len(data):
                    break
                nm, shndx = (u32(o), u16(o + 6)) if b64 else (u32(o), u16(o + 14))
                n = cstr(link, nm) if shndx == 0 else ""
                if n:
                    imports.append(n)
        elif t == 6:   # .dynamic: DT_NEEDED (1)
            w = 16 if b64 else 8
            for o in range(off, min(off + size, len(data) - w + 1), w):
                tag = uw(o)
                if tag == 0:
                    break
                if tag == 1:
                    needed.append(cstr(link, uw(o + w // 2)))
    interp = 3 in ptypes
    code = sum(s[4] for s in secs if s[2] & 4 and s[1] != 8) or xseg   # SHF_EXECINSTR, else PF_X segments
    return {"format": "elf", "elf_type": ELF_TYPE_NAME.get(et, str(et)), "entry_point": hex(entry),
            "section_names": names, "has_symtab": "true" if any(s[1] == 2 for s in secs) else "false",
            "has_interp": "true" if interp else "false", "linking": "dynamic" if interp else "static",
            "is_static": "false" if interp else "true", "is_pie": "true" if et == 3 and interp else "false",
            "has_debug_info": "true" if {".debug_info", ".zdebug_info"} & set(names) else "false",
            "imports": imports, "needed": needed, "code_size": code}


def pair_member_facts(data):
    """Per-member facts that DIFFER inside a same-source build pair, pure header walk (no subprocess):
    ELF {format, elf_type ET_* (readelf constant), entry_point hex (e_entry), section_names (header-table order,
    index 0 = ""), has_symtab, has_interp, linking static/dynamic + is_static (no PT_INTERP), is_pie (ET_DYN +
    PT_INTERP), has_debug_info (.debug_info), imports (undefined named .dynsym symbols, .dynsym order, no @version),
    needed (DT_NEEDED order), code_size (SHF_EXECINSTR bytes, else PF_X filesz), is_packed (UPX)}
    + machine_facts {machine (label), machine_num (decimal e_machine / PE Machine), bits, endian} (ELF and PE).
    PE: {format, entry_point (ImageBase+AddressOfEntryPoint), section_names, code_size, is_packed}. Else None."""
    try:
        head = bytes(data[:4096])
        packed = b"UPX!" in head or b"UPX0" in head or b"UPX1" in head
        if data[:4] == b"\x7fELF" and data[4:5] in (b"\x01", b"\x02") and data[5:6] in (b"\x01", b"\x02") \
                and len(data) >= 52:
            if data[6] != 1:   # EI_VERSION: a garbage / impostor header, not a build
                return None
            f = _elf_pair_facts(data)
        else:
            lay = _pe_layout(data)
            if not lay:
                return None
            pe = int.from_bytes(data[0x3c:0x40], "little")
            opt = pe + 24
            magic, aep = struct.unpack_from("<H", data, opt)[0], struct.unpack_from("<I", data, opt + 16)[0]
            base = struct.unpack_from("<Q", data, opt + 24)[0] if magic == 0x20b else \
                struct.unpack_from("<I", data, opt + 28)[0]
            secs = lay[1]
            chars = [struct.unpack_from("<I", data, lay[0] + 40 * k + 36)[0] for k in range(len(secs))]
            f = {"format": "pe", "entry_point": hex(base + aep), "section_names": [s[0] for s in secs],
                 "code_size": sum(s[4] for s, c in zip(secs, chars) if c & 0x20000000)}
            packed = packed or any(s[0].startswith("UPX") for s in secs)
        f["is_packed"] = "true" if packed else "false"
        mf = machine_facts(data) or {}   # cross-arch pairs: machine label / e_machine decimal / bits / endian
        for k in ("machine", "machine_num", "bits", "endian"):
            if k in mf:
                f[k] = mf[k]
        return f
    except Exception:   # truncated / hostile headers: cannot answer
        return None


_PAIR_NEG = {"no", "non", "not", "un"}
_PAIR_SKIP = {"variant", "elf", "exe", "jar", "dll", "bin", "so", "config", "has", "hcfg", "analysis", "artifact",
              "is", "entry", "section"}
# tag (tokens joined) -> structural predicates tried in order until one picks exactly one member:
# (fact, value) = that fact equals value; ("code_size", "max"/"min") = the largest / smallest code.
_PAIR_FAMILY = {}
for _t, _p in (
        (("static", "statically", "staticlink"), [("is_static", "true")]),
        (("dynamic", "dynamically", "shared", "dyn"), [("is_static", "false")]),
        (("pie",), [("is_pie", "true")]),
        (("nopie", "nonpie", "notpie", "exec", "fixed"), [("is_pie", "false")]),
        (("packed", "upx", "upxed", "compressed", "packer"), [("is_packed", "true")]),
        (("unpacked", "original", "unpack"), [("is_packed", "false")]),
        (("debug", "g", "dbg", "debuginfo", "dwarf"), [("has_debug_info", "true"), ("has_symtab", "true")]),
        (("release", "nodebug", "rel"), [("has_debug_info", "false"), ("has_symtab", "false"), ("code_size", "min")]),
        (("stripped", "strip"), [("has_symtab", "false"), ("has_debug_info", "false")]),
        (("symbolized", "unstripped", "symbolic", "symbols", "nostrip"), [("has_symtab", "true")]),
        (("plain", "clean", "normal"), [("is_packed", "false"), ("code_size", "min")]),
        (("obfuscated", "obf", "obfus", "ollvm"), [("code_size", "max")]),
        (("o0", "unoptimized", "noopt", "o0g"), [("code_size", "max")]),
        (("o1", "o2", "o3", "os", "oz", "og", "optimized", "opt", "compact", "small", "size", "fast"),
         [("code_size", "min")]),
        # cross-arch pairs (tag tokens joined: `x86_64` -> x8664); an alias tag (`arm64` vs a `-aarch64` name) or a
        # renamed member falls through the name match to the e_machine number (62 / 183 / 243 / 40 / 3)
        (("x8664", "amd64", "x64", "x86x64"), [("machine_num", "62")]),
        (("aarch64", "arm64", "armv8", "a64"), [("machine_num", "183")]),
        (("riscv", "riscv64", "rv64", "riscv32", "rv32", "rv64gc", "rv64imac"), [("machine_num", "243")]),
        (("arm", "arm32", "armv7", "armv7a", "armhf", "armel", "aarch32", "thumb"), [("machine_num", "40")]),
        (("x86", "i386", "i686", "x8632", "ia32"), [("machine_num", "3")])):
    for _k in _t:
        _PAIR_FAMILY[_k] = _p
del _t, _p, _k


def _pair_tokens(name):
    stem = name.lower().replace("\\", "/").rsplit("/", 1)[-1]
    stem = re.sub(r"\.[a-z]{1,5}$", "", stem)   # extension never carries the tag (`-no-pie.elf` != `no_pie_elf`)
    return [t for t in re.split(r"[^a-z0-9]+", stem) if t]


def _pair_name_hit(want, toks):
    """True if `want` (tag tokens joined) equals whole adjacent name tokens joined, not after a negation token."""
    for s in range(len(toks)):
        acc = ""
        for e in range(s, len(toks)):
            acc += toks[e]
            if acc == want:
                if s and toks[s - 1] in _PAIR_NEG:
                    break
                return True
            if len(acc) >= len(want) or not want.startswith(acc):
                break
    return False


def pair_route(field, members):
    """Route `<tag>_<field>` (the part after `analysis_`) to ONE member of a build pair.
    members = [(name, bytes)] of the day's group. Returns (index, rest_field, how) or None (not a pair field).
    1) the LONGEST leading tag (1..n-1 tokens; `no_pie` == `nopie` == `no-pie`) found in exactly one member's file
       name as whole tokens (`pie` does not match `no-pie`); 2) renamed members: the tag family's structural
       predicate over pair_member_facts (no INTERP = static, ET_DYN+INTERP = pie, UPX = packed, .debug_info = debug,
       no .symtab = stripped, smaller code = O1-Os/compact/optimized, larger = O0/obfuscated)."""
    try:
        parts = [p for p in field.lower().split("_") if p]
        if len(members) < 2 or len(parts) < 2 or parts[0] in _PAIR_SKIP or parts[0].isdigit():
            return None
        toks = [_pair_tokens(n) for n, _ in members]
        for k in range(len(parts) - 1, 0, -1):
            if parts[k - 1] in _PAIR_SKIP:
                continue
            want = "".join(parts[:k])
            hit = [i for i, t in enumerate(toks) if _pair_name_hit(want, t)]
            if len(hit) == 1:
                return hit[0], "_".join(parts[k:]), "name"
            if hit:
                break   # a shorter tag can only hit more members
        for k in range(len(parts) - 1, 0, -1):
            preds = _PAIR_FAMILY.get("".join(parts[:k]))
            if not preds:
                continue
            fx = [pair_member_facts(b) if isinstance(b, (bytes, bytearray, memoryview)) else None for _, b in members]
            for fact, want in preds:
                vals = [f.get(fact) if f else None for f in fx]
                if fact == "code_size":
                    sizes = [v for v in vals if isinstance(v, int) and v > 0]
                    if len(sizes) < 2 or len(set(sizes)) < len(sizes):
                        continue
                    pick = (max if want == "max" else min)(sizes)
                    hit = [i for i, v in enumerate(vals) if v == pick]
                else:
                    hit = [i for i, v in enumerate(vals) if v == want]
                if len(hit) == 1:
                    return hit[0], "_".join(parts[k:]), "struct:" + fact
            return None
    except Exception:   # noqa: BLE001 -- never raise past the router
        pass
    return None


def zip_cd_sha256(data, pwd=None, prefix=None):
    """[(name, sha256 hex)] of the archive's file members in CENTRAL-DIRECTORY order (= `dNN_artifact_sha256_K`
    numbering, K 1-based), optionally only names starting with `prefix` (path-insensitive). AES zips via pyzipper.
    None if not a readable zip."""
    import hashlib
    try:
        try:
            import pyzipper
            z = pyzipper.AESZipFile(io.BytesIO(data))
        except ImportError:
            z = zipfile.ZipFile(io.BytesIO(data))
        if pwd:
            z.setpassword(pwd if isinstance(pwd, bytes) else pwd.encode())
        out = []
        for zi in z.infolist():
            base = zi.filename.rsplit("/", 1)[-1]
            if zi.is_dir() or (prefix and not base.lower().startswith(prefix.lower())):
                continue
            out.append((zi.filename, hashlib.sha256(z.read(zi)).hexdigest()))
        return out
    except Exception:   # noqa: BLE001
        return None


# --- per-language identity facts (D8-D17 groups: Swift / Nim / Zig / D / FPC / Crystal / ObjC / Ada / Go / Rust) ----
LANG_ORDER = ("swift", "objc", "nim", "zig", "d", "fpc", "crystal", "gnat", "go", "rust")
_LANG_BYTES = {   # one raw-byte marker per runtime (only scanned when sections/symbols did not already decide it)
    "swift": b"swift_retain", "objc": b"objc_msg", "nim": b"NimMain", "zig": b"ziglang", "d": b"_D4core",
    "fpc": b"FPC 3.", "crystal": b"Crystal::", "gnat": b"__gnat_", "go": b"\xff Go buildinf:", "rust": b"/rustc/",
}
_SWIFT_SYS = {"Swift", "Foundation", "FoundationEssentials", "FoundationInternationalization", "FoundationNetworking",
              "FoundationXML", "Dispatch", "Glibc", "Musl", "SwiftGlibc", "Synchronization", "Observation",
              "Distributed", "RegexBuilder", "CoreFoundation", "Darwin", "ObjectiveC", "SwiftShims", "XCTest",
              "Cxx", "CxxStdlib", "SwiftOnoneSupport", "os", "WinSDK", "Android", "Testing"}
_D_SYS = {"core", "std", "rt", "object", "gc", "etc", "ldc", "gcc", "TypeInfo"}
_ADA_SYS = ("ada", "system", "gnat", "interfaces", "_ada", "__gnat", "_gnat")
_SWIFT_KIND = {"V": "struct", "C": "class", "O": "enum", "P": "protocol"}
_D_ID = re.compile(r"(\d+)")
_NIM_SYM = re.compile(r"^(.+?)__([A-Za-z0-9]+)_u\d+$")
_RUST_LEGACY = re.compile(r"^_ZN.*17h[0-9a-f]{16}E$")
_SWIFT_MANGLED = re.compile(r"^_?\$[sS](?:s|[1-9])")   # `$Slice:0` (Crystal) is no Swift mangling
_SWIFT_MOD = re.compile(r"_?\$[sS]([1-9]\d*)")


def _elf_symbols(data, cap=400_000):
    """[(name, st_info type, defined)] from SHT_SYMTAB + SHT_DYNSYM (raw structs, capped); [] when absent."""
    b64, e = data[4] == 2, "<" if data[5] == 1 else ">"
    shoff = struct.unpack_from(e + ("Q" if b64 else "I"), data, 40 if b64 else 32)[0]
    shes, shn = struct.unpack_from(e + "HH", data, 58 if b64 else 46)
    sh = (e + "4xI8x8xQQIi8xQ") if b64 else (e + "4xI4x4xIIIi4xI")   # type, offset, size, link, -, entsize
    if not shoff or shes < (64 if b64 else 40) or shoff + shn * shes > len(data):
        return []
    secs = [struct.unpack_from(sh, data, shoff + k * shes) for k in range(min(shn, 65535))]
    out = []
    for ty, off, size, link, _, ent in secs:
        if ty not in (2, 11) or not 0 <= link < len(secs) or off + size > len(data):
            continue
        so, sn = secs[link][1], secs[link][2]
        ent = ent or (24 if b64 else 16)
        for k in range(min(size // ent, cap - len(out))):
            o = off + k * ent
            if b64:
                nm, info, shndx = struct.unpack_from(e + "IBxH", data, o)
            else:
                nm, info, shndx = struct.unpack_from(e + "I8xBxH", data, o)
            if not nm or nm >= sn:
                continue
            z = data.find(b"\0", so + nm, so + sn)
            out.append((bytes(data[so + nm:z if z >= 0 else so + sn]).decode("latin-1"), info & 0xF, shndx != 0))
    return out


def _swift_ids(s, p):
    """[(identifier, kind letter after it)] from offset p of a Swift `$s` mangling (plain <len><ident> runs only)."""
    out = []
    while p < len(s) and s[p].isdigit() and s[p] != "0":
        m = _D_ID.match(s, p)
        n, p = int(m.group(1)), m.end()
        if p + n > len(s):
            break
        out.append((s[p:p + n], s[p + n:p + n + 1]))
        p += n
    return out


def lang_facts(data, max_syms=400_000):
    """Language identity + theme facts of an ELF / PE / Mach-O / wasm image (bytes only, no subprocess).
    has_<lang>_runtime "true"/"false" for swift (swift5_* sections, `$s` symbols, Swift runtime strings), objc
    (__objc_* / .objc_* sections or symbols, objc_msg_lookup/objc_msgSend), nim (NimMain), zig (.comment zig / zig std
    paths), d (_D4core/_D2rt symbols, druntime), fpc (FPC banner, .fpcdata), crystal (Crystal:: symbols, crystal/src),
    gnat (+ alias has_ada_runtime: GNAT Version, __gnat_, adainit), go (buildinfo, runtime.goexit), rust (rust_panic,
    /rustc/ paths); has_wasm_module. has_<lang>_mangled_symbol: swift `$s`/`$S`/`_$s`, d `_D<digit>`, nim
    `<proc>__<mod>_u<N>`, rust legacy `_ZN..17h<hash>E` / v0 `_R`, cpp `_Z` (not rust). language = first runtime hit in
    LANG_ORDER ("c"/"wasm" fallback). User-module names (stdlib/runtime modules dropped, MANGLED forms kept alongside):
    swift_module, swift_types {name: struct/class/enum/protocol}, swift_protocols, swift_functions (+ _mangled);
    nim_module, nim_procs (+ _mangled); d_module, d_functions (qualified mod.name, + _mangled); objc_classes (defined
    ._OBJC_CLASS_ / _OBJC_CLASS_$_), objc_selectors (objc_sel_name_ / __objc_methname), objc_methods "-[C sel]";
    ada_subprograms (pkg__sub, + _mangled). Absent -> "none" / "false" / []; not an executable image -> None."""
    try:
        d = memoryview(data) if not isinstance(data, (bytes, bytearray)) else data
        d = bytes(d) if isinstance(d, memoryview) else d
        if d[:4] == b"\x7fELF" and len(d) >= 64 and d[4] in (1, 2) and d[5] in (1, 2):
            fmt = "elf"
        elif d[:2] == b"MZ" and len(d) >= 0x40 and d[int.from_bytes(d[0x3c:0x40], "little"):][:4] == b"PE\0\0":
            fmt = "pe"
        elif d[:4] in _MO_MAGIC or d[:4] in (b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"):
            fmt = "macho"
        elif d[:4] == b"\0asm" and len(d) >= 8:
            fmt = "wasm"
        else:
            return None
        secnames, syms, comment = [], [], b""
        if fmt == "elf":
            lay = _elf_layout(d)
            if lay:
                for nm, o, n in lay[1]:
                    secnames.append(nm)
                    if nm == ".comment":
                        comment = bytes(d[o:o + min(n, 4096)])
            try:
                syms = _elf_symbols(d, max_syms)
            except _PARSE_ERR:
                syms = []
        elif fmt == "macho":
            try:
                secnames = [s.get("sectname", s.get("name", "")) for s in (macho_layout(d) or {}).get("sections", [])]
            except Exception:   # noqa: BLE001
                secnames = []
        elif fmt == "pe":
            try:
                secnames = [s[0] for s in (_pe_layout(d) or (0, []))[1]]
            except Exception:   # noqa: BLE001
                secnames = []
        names = [s[0] for s in syms]
        nset = set(names)
        hit = {k: False for k in LANG_ORDER}
        hit["swift"] = any(s.startswith("swift5_") or s.startswith("__swift5_") for s in secnames)
        hit["objc"] = any(s.startswith("__objc_") or s.startswith(".objc_") for s in secnames)
        hit["nim"] = "NimMain" in nset or "NimMainModule" in nset
        hit["zig"] = b"zig" in comment.lower()
        hit["fpc"] = ".fpcdata" in secnames
        hit["go"] = ".gopclntab" in secnames or ".go.buildinfo" in secnames or "runtime.goexit" in nset
        mang = {"swift": False, "d": False, "nim": False, "rust": False, "cpp": False}
        for n in names:
            c = n[:1]
            if c == "$" or c == "_" and n[1:2] == "$":
                if _SWIFT_MANGLED.match(n):
                    mang["swift"] = True
            elif c == "_":
                if n[1:2] == "D" and n[2:3].isdigit():
                    mang["d"] = True
                    if n.startswith(("_D4core", "_D2rt", "_D6object")):
                        hit["d"] = True
                elif n[1:2] == "R" and n[2:3].isupper() or n[1:3] == "ZN" and _RUST_LEGACY.match(n):
                    mang["rust"] = True
                elif n[1:2] == "Z":
                    mang["cpp"] = True
                elif n.startswith(("__objc_load", "_OBJC_CLASS_$_")):
                    hit["objc"] = True
                elif n.startswith("__gnat_"):
                    hit["gnat"] = True
            elif c == "." and n.startswith("._OBJC_") or c == "o" and n.startswith("objc_msg"):
                hit["objc"] = True
            elif c in "C*" and n.startswith(("Crystal::", "*Crystal::")):
                hit["crystal"] = True
            elif c in "Ff" and n.startswith(("FPC_", "fpc_")):
                hit["fpc"] = True
            elif c == "r" and n.startswith(("rust_panic", "rust_begin_unwind")):
                hit["rust"] = True
            elif c == "a" and n.startswith(("adainit", "ada__")):
                hit["gnat"] = True
            if not mang["nim"] and "_u" in n and _NIM_SYM.match(n):
                mang["nim"] = True
        hit["swift"] = hit["swift"] or mang["swift"]
        if fmt != "wasm":
            for lang in LANG_ORDER:
                if not hit[lang] and _LANG_BYTES[lang] in d:
                    hit[lang] = True
        lang = next((k for k in LANG_ORDER if hit[k]), "wasm" if fmt == "wasm" else ("cpp" if mang["cpp"] else "c"))
        tf = lambda b: "true" if b else "false"   # noqa: E731
        out = {"format": fmt, "language": lang, "has_wasm_module": tf(fmt == "wasm")}
        for k in LANG_ORDER:
            out[f"has_{k}_runtime"] = tf(hit[k])
        out["has_ada_runtime"] = out["has_gnat_runtime"]
        for k, v in mang.items():
            out[f"has_{k}_mangled_symbol"] = tf(v)
        # --- user-module names ---
        sw_t, sw_f, sw_fm, mods = {}, set(), set(), {}
        if mang["swift"]:
            for n, ty, dfn in syms:
                m = _SWIFT_MOD.match(n)
                if not m:
                    continue
                k = int(m.group(1))
                mod = n[m.end():m.end() + k]
                if mod in _SWIFT_SYS or mod[:1] == "_" or mod.startswith("Foundation") or len(mod) < k:
                    continue
                ids = _swift_ids(n, m.start(1))
                chain = []
                for ident, kind in ids[1:]:
                    if kind in _SWIFT_KIND:
                        sw_t.setdefault(ident, _SWIFT_KIND[kind])
                        chain.append(ident)
                        continue
                    if dfn and ty == 2 and ident[:1].isalpha():
                        sw_f.add(".".join(chain + [ident]))
                        sw_fm.add(n)
                        mods[mod] = mods.get(mod, 0) + 1
                    break
        out["swift_module"] = max(mods, key=mods.get) if mods else "none"
        out["swift_types"] = dict(sorted(sw_t.items()))
        out["swift_protocols"] = sorted(k for k, v in sw_t.items() if v == "protocol")
        out["swift_functions"], out["swift_functions_mangled"] = sorted(sw_f), sorted(sw_fm)
        nim_p, nim_m, nmods = set(), set(), {}
        dfun, dfm, dmods = set(), set(), {}
        ada_p, ada_m = set(), set()
        cls, sels, meth = set(), set(), []
        for n, ty, dfn in syms:
            if not dfn:
                continue
            m = _NIM_SYM.match(n) if "_u" in n else None
            if m and ty == 2 and m.group(2) != "system" and "Z" not in m.group(2) \
                    and not (m.group(1).startswith("eq") and m.group(1).endswith("_")):   # =destroy/=copy hooks
                nim_p.add(m.group(1))
                nim_m.add(n)
                nmods[m.group(2)] = nmods.get(m.group(2), 0) + 1
            if n[:2] == "_D" and n[2:3].isdigit():
                ids, p = [], 2
                while p < len(n) and n[p].isdigit() and n[p] != "0":
                    mm = _D_ID.match(n, p)
                    k, p = int(mm.group(1)), mm.end()
                    ids.append(n[p:p + k])
                    p += k
                if ty == 2 and len(ids) >= 2 and ids[0] not in _D_SYS and n[p:p + 1] in ("F", "M") \
                        and not ids[-1].startswith("__"):
                    dfun.add(".".join(ids))
                    dfm.add(n)
                    dmods[ids[0]] = dmods.get(ids[0], 0) + 1
            for pre in ("._OBJC_CLASS_", "_OBJC_CLASS_$_", "__objc_class_name_"):
                if n.startswith(pre):
                    cls.add(n[len(pre):])
            for pre in (".objc_sel_name_", "objc_sel_name_"):
                if n.startswith(pre):
                    sels.add(n[len(pre):])
            if n[:3] in ("_i_", "_c_") and "__" in n[3:]:
                meth.append(n)
            if hit["gnat"] and ty == 2 and "__" in n.strip("_") and n == n.lower() and not n.startswith(_ADA_SYS):
                pkg, _, sub = n.partition("__")
                if pkg and sub and not sub.startswith("_") and pkg.isidentifier():
                    ada_p.add(f"{pkg}.{sub.replace('__', '.')}")
                    ada_m.add(n)
        if fmt == "macho":
            try:
                for s in (macho_layout(d) or {}).get("sections", []):
                    if s.get("sectname", s.get("name")) == "__objc_methname":
                        o, z = s.get("offset", 0), s.get("size", 0)
                        sels.update(x.decode("latin-1") for x in bytes(d[o:o + z]).split(b"\0") if x)
            except Exception:   # noqa: BLE001
                pass
        omethods = set()
        for n in meth:
            c, _, rest = n[3:].partition("_")
            cat, _, sel = rest.partition("_")
            want = sel.replace("_", ":")
            sel = next((s for s in sels if s.replace(":", "_") == sel), want)
            omethods.add(f"{'-' if n[1] == 'i' else '+'}[{c}{'(' + cat + ')' if cat else ''} {sel}]")
        out["nim_module"] = max(nmods, key=nmods.get) if nmods else "none"
        out["nim_procs"], out["nim_procs_mangled"] = sorted(nim_p), sorted(nim_m)
        out["d_module"] = max(dmods, key=dmods.get) if dmods else "none"
        out["d_functions"], out["d_functions_mangled"] = sorted(dfun), sorted(dfm)
        out["objc_classes"] = sorted(c for c in cls if f"._OBJC_METACLASS_{c}" in nset or
                                     f"_OBJC_METACLASS_$_{c}" in nset or fmt != "elf")   # defined here, not imported
        out["objc_selectors"], out["objc_methods"] = sorted(sels), sorted(omethods)
        out["ada_subprograms"], out["ada_subprograms_mangled"] = sorted(ada_p), sorted(ada_m)
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def lang_field(data, name):
    """One lang_facts value (lists as JSON-able lists); "none" when the input is no executable image or the field is
    unknown, so a decoy never raises."""
    try:
        return (lang_facts(data) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- gnat_facts: Ada / GNAT deep facts (D17 ada_br17_main theme) ------------------------------------------------------
_DW_LANG = {0x01: "C89", 0x02: "C", 0x03: "Ada83", 0x04: "C_plus_plus", 0x0c: "C99", 0x0d: "Ada95", 0x1d: "C11",
            0x21: "C_plus_plus_14", 0x2c: "C17", 0x2e: "Ada2005", 0x2f: "Ada2012", 0x1c: "Rust", 0x16: "Go"}
_DW_FIXED = {0x01: -1, 0x05: 2, 0x06: 4, 0x07: 8, 0x0b: 1, 0x0c: 1, 0x0e: -2, 0x10: -2, 0x11: 1, 0x12: 2, 0x13: 4,
             0x14: 8, 0x17: -2, 0x19: 0, 0x1c: 4, 0x1d: -2, 0x1e: 16, 0x1f: -2, 0x20: 8, 0x21: 0, 0x24: 8, 0x25: 1,
             0x26: 2, 0x27: 3, 0x28: 4, 0x29: 1, 0x2a: 2, 0x2b: 3, 0x2c: 4}   # -1 = addr size, -2 = offset size
_ADA_STD_EXC = ("constraint_error", "program_error", "storage_error", "tasking_error", "numeric_error")
_ADA_EXC_SYS = ("ADA.", "SYSTEM.", "GNAT.", "INTERFACES.", "_ABORT_SIGNAL", "_STANDARD.")


def _dwarf_top_dies(d, secs, e, cap=4096):
    """[(producer, language code, name)] of each compile/partial unit's top DIE (raw .debug_info walk; strx forms and
    compressed sections -> None values)."""
    sec = {n: (o, z) for n, o, z in secs}
    if ".debug_info" not in sec or ".debug_abbrev" not in sec:
        return []
    io_, iz = sec[".debug_info"]
    ao, az = sec[".debug_abbrev"]
    strs = {k: sec.get(n) for k, n in ((0x0e, ".debug_str"), (0x1f, ".debug_line_str"))}

    def cstr(form, off):
        s = strs.get(form)
        if s is None or off >= s[1]:
            return None
        z = d.find(b"\0", s[0] + off, s[0] + s[1])
        return bytes(d[s[0] + off:z if z >= 0 else s[0] + s[1]]).decode("latin-1")
    out, p, end, abbr = [], io_, io_ + iz, {}
    while p + 11 <= end and len(out) < cap:
        ln, osz = struct.unpack_from(e + "I", d, p)[0], 4
        p += 4
        if ln == 0xffffffff:
            ln, osz = struct.unpack_from(e + "Q", d, p)[0], 8
            p += 8
        nxt = p + ln
        ver = struct.unpack_from(e + "H", d, p)[0]
        q = p + 2
        try:
            if ver >= 5:
                ut, asz = d[q], d[q + 1]
                aoff = int.from_bytes(d[q + 2:q + 2 + osz], "little" if e == "<" else "big")
                q += 2 + osz + (8 if ut in (4, 5) else 0)
                if ut not in (1, 3, 4, 5):
                    p = nxt
                    continue
            elif 2 <= ver <= 4:
                aoff = int.from_bytes(d[q:q + osz], "little" if e == "<" else "big")
                asz, q = d[q + osz], q + osz + 1
            else:
                break
            code, q = _leb(d, q)
            tab, a = abbr.get(aoff) or ({}, ao + aoff)
            if code not in tab:
                while a < ao + az and len(tab) < 4096:
                    c, a = _leb(d, a)
                    if not c:
                        break
                    _, a = _leb(d, a)
                    a += 1
                    specs = []
                    while True:
                        at, a = _leb(d, a)
                        fm, a = _leb(d, a)
                        ic = None
                        if fm == 0x21:
                            ic, a = _leb(d, a, True)
                        if not at and not fm:
                            break
                        specs.append((at, fm, ic))
                    tab[c] = specs
                    if c == code:
                        break
                abbr[aoff] = (tab, a)
            prod = lang = name = None
            for at, fm, ic in tab.get(code, ()):
                while fm == 0x16:
                    fm, q = _leb(d, q)
                val = None
                if fm == 0x08:
                    z = d.find(b"\0", q, nxt)
                    val, q = bytes(d[q:z]).decode("latin-1"), z + 1
                elif fm in (0x0f, 0x15, 0x1a, 0x1b, 0x22, 0x23, 0x0d):
                    val, q = _leb(d, q, fm == 0x0d)
                elif fm in (0x09, 0x18):
                    n, q = _leb(d, q)
                    q += n
                elif fm in (0x03, 0x04, 0x0a):
                    k = {0x03: 2, 0x04: 4, 0x0a: 1}[fm]
                    q += k + int.from_bytes(d[q:q + k], "little" if e == "<" else "big")
                elif fm == 0x21:
                    val = ic
                elif fm in _DW_FIXED:
                    k = _DW_FIXED[fm]
                    k = asz if k == -1 else osz if k == -2 else k
                    val, q = int.from_bytes(d[q:q + k], "little" if e == "<" else "big"), q + k
                else:
                    break
                if at in (0x25, 0x03):
                    s = val if isinstance(val, str) else cstr(fm, val) if fm in strs and val is not None else None
                    if at == 0x25:
                        prod = s
                    else:
                        name = s
                elif at == 0x13 and isinstance(val, int):
                    lang = val
            out.append((prod, lang, name))
        except (IndexError, ValueError, struct.error, KeyError):
            pass
        p = nxt
    return out


def _ada_name(sym):
    """GNAT-encoded symbol -> Ada name: `_ada_main` -> main, `pkg__sub__2` -> pkg.sub, `x.cold`/`x.0` suffix dropped."""
    s = re.sub(r"\.(cold|part|isra|constprop|\d+)(\.\d+)*$", "", sym)
    s = s[5:] if s.startswith("_ada_") else s
    s = re.sub(r"__\d+$", "", s)
    return s.replace("__", ".")


def gnat_facts(data, max_syms=400_000, decoder=True, hit=None):
    """Ada / GNAT deep facts of an ELF/PE/Mach-O image (bytes only): has_gnat_runtime (__gnat_ / ada__ / system__
    symbols or bytes, `GNAT Version:`, adainit+adafinal), gnat_version ("14.2.0" from the binder's `GNAT Version: 14.2.0`)
    + gnat_version_string; ada_main_symbol (`_ada_<main>`: FUNC symbol, else the binder's .rodata main-program-name
    string) + ada_main (Ada name); main_source (`<main>.adb`); has_adainit/has_adafinal/has_gnat_main, binder_symbols
    (defined adainit/adafinal/main/ada_main___elabb/...), elab_symbols (non-runtime `*___elab[bs]`);
    ada_subprograms (pkg.sub + the main, user units only) + _mangled; dwarf_producer ("GNU Ada 14.2.0"),
    dwarf_producer_full, dwarf_producer_version, dwarf_language ("DW_LANG_Ada95", Ada CUs preferred) + _code,
    dwarf_languages; ada_exceptions / user_exceptions (Exception_Data structs: Lang 'A' + Name_Length + Full_Name
    pointer -> "PKG.NAME"), standard_exceptions (defined constraint_error/...); decoder_function (+ _ada name), decoder_key
    (0x..), decoder_algorithm, decoder_key_equals_header (decoder_facts over `hit` or hcfg_find; decoder=False skips it,
    a 0.3 s scan deadline bounds a corrupted blob). Absent -> "none"/"false"/[]; not an executable image -> None."""
    try:
        d = bytes(data)
        if d[:4] == b"\x7fELF" and len(d) >= 64 and d[4] in (1, 2) and d[5] in (1, 2):
            fmt = "elf"
        elif d[:2] == b"MZ" and len(d) >= 0x40 and d[int.from_bytes(d[0x3c:0x40], "little"):][:4] == b"PE\0\0":
            fmt = "pe"
        elif d[:4] in _MO_MAGIC or d[:4] in (b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"):
            fmt = "macho"
        else:
            return None
        tf = lambda b: "true" if b else "false"   # noqa: E731
        syms, secs, e = [], [], "<"
        if fmt == "elf":
            e = "<" if d[5] == 1 else ">"
            secs = (_elf_layout(d) or (0, []))[1]
            try:
                syms = _elf_symbols(d, max_syms)
            except _PARSE_ERR:
                syms = []
        dfn = {n for n, _, k in syms if k}
        funcs = {n for n, ty, k in syms if k and ty == 2}
        out = {"format": fmt}
        m = re.search(rb"GNAT Version: ([^\0\r\n]{1,80})", d)
        out["gnat_version_string"] = m.group(0).decode("latin-1").strip() if m else "none"
        vm = re.match(rb"\s*(\d+(?:\.\d+)*)", m.group(1)) if m else None
        out["gnat_version"] = vm.group(1).decode() if vm else (m.group(1).decode("latin-1").strip() if m else "none")
        rt = any(n.startswith(("__gnat_", "ada__", "system__")) for n in dfn) or \
            ("adainit" in dfn and "adafinal" in dfn) or m is not None or b"__gnat_" in d
        out["has_gnat_runtime"] = out["has_ada_runtime"] = tf(rt)
        # main program: `_ada_<unit>` FUNC symbol, else binder's main-program-name string (sits beside GNAT Version)
        mains = sorted(n for n in funcs if n.startswith("_ada_") and "." not in n)
        main = mains[0] if mains else None
        if main is None and rt:
            lo = max(0, m.start() - 512) if m else 0
            ms = list(re.finditer(rb"\0(_ada_[a-z][a-z0-9_]{0,120})\0", d[lo:m.end() + 512] if m else d))
            main = ms[-1].group(1).decode() if ms else None
        out["ada_main_symbol"] = main or "none"
        out["ada_main"] = _ada_name(main) if main else "none"
        src = None
        if main:
            src = f"{main[5:]}.adb" if f"{main[5:]}.adb".encode() in d else None
        out["main_source"] = src or "none"
        out["has_adainit"], out["has_adafinal"] = tf("adainit" in dfn), tf("adafinal" in dfn)
        out["has_gnat_main"] = tf("__gnat_main" in dfn)
        if not syms and rt and fmt != "elf":
            out["has_adainit"] = tf(b"adainit\0" in d)
            out["has_adafinal"] = tf(b"adafinal\0" in d)
        out["binder_symbols"] = sorted(n for n in dfn if n in ("adainit", "adafinal", "main", "__gnat_main",
                                                               "ada_main___elabb", "ada_main__finalize_library",
                                                               "__gnat_ada_main_program_name", "gnat_envp", "gnat_argv",
                                                               "gnat_argc", "gnat_exit_status")) if rt else []
        out["elab_symbols"] = sorted(n for n in dfn if re.search(r"___elab[bs]$", n) and
                                     not n.startswith(_ADA_SYS)) if rt else []
        ada_p, ada_m = set(), set()
        if rt:
            for n in funcs:
                if n == main:
                    ada_p.add(_ada_name(n))
                    ada_m.add(n)
                elif "__" in n.strip("_") and n == n.lower() and not n.startswith(_ADA_SYS) and \
                        not n.startswith("ada_main_") and "." not in n and not re.search(r"___elab[bs]$", n):
                    pkg, _, sub = n.partition("__")
                    if pkg and sub and not sub.startswith("_") and pkg.isidentifier():
                        ada_p.add(_ada_name(n))
                        ada_m.add(n)
        out["ada_subprograms"], out["ada_subprograms_mangled"] = sorted(ada_p), sorted(ada_m)
        # DWARF compile units
        cus = _dwarf_top_dies(d, secs, e) if fmt == "elf" else []
        langs = [c[1] for c in cus if c[1] is not None]
        ada = [c for c in cus if c[1] in (0x03, 0x0d, 0x2e, 0x2f)]
        prods = [c[0] for c in cus if c[0]]
        if not prods and fmt == "elf" and ".debug_str" in {s[0] for s in secs}:
            prods = [x.decode("latin-1") for x in re.findall(rb"GNU Ada [0-9][^\0]{0,400}", d)[:1]]
        mcu = next((c for c in ada if main and c[2] and c[2].startswith(main[5:] + ".")), None)
        pfull = (mcu and mcu[0]) or next((c[0] for c in ada if c[0]), None) or \
            next((p for p in prods if p.startswith("GNU Ada")), None) or (prods[0] if prods else None)
        out["dwarf_producer_full"] = pfull or "none"
        pm = re.match(r"(.*?\d+(?:\.\d+)+)", pfull or "")
        out["dwarf_producer"] = pm.group(1) if pm else (pfull or "none")
        vm2 = re.search(r"(\d+(?:\.\d+)+)", pfull or "")
        out["dwarf_producer_version"] = vm2.group(1) if vm2 else "none"
        lc = (mcu or (ada[0] if ada else None) or (None, max(set(langs), key=langs.count) if langs else None))[1]
        out["dwarf_language_code"] = lc if lc is not None else "none"
        out["dwarf_language"] = f"DW_LANG_{_DW_LANG.get(lc, hex(lc))}" if lc is not None else "none"
        out["dwarf_languages"] = sorted({f"DW_LANG_{_DW_LANG.get(x, hex(x))}" for x in langs})
        out["dwarf_compile_units"] = len(cus)
        # exception ids: Exception_Data = {Not_Handled_By_Others u8, Lang 'A', Name_Length u32, Full_Name ptr, ...}
        exc = set()
        if rt and fmt == "elf":
            mp = _exec_map(d) if d[18] in (3, 62) or d[19] in (3, 62) else None
            vsec = [(va, off, size) for nm, va, off, size, _ in (mp[1] if mp else []) if size]
            b64 = d[4] == 2
            for nm, va, off, size, _x in (mp[1] if mp else []):
                if nm not in (".data", ".rodata", ".data.rel.ro") or size > 32 << 20:
                    continue
                for mm in re.finditer(rb"[\0\1]A", d[off:off + size]):
                    q = off + mm.start()
                    if (q - off) % (8 if b64 else 4) or q + (16 if b64 else 12) > off + size:
                        continue
                    nl = struct.unpack_from(e + "I", d, q + 4)[0] if b64 else struct.unpack_from(e + "I", d, q + 4)[0]
                    ptr = struct.unpack_from(e + ("Q" if b64 else "I"), d, q + (8 if b64 else 8))[0]
                    if not 2 <= nl <= 256:
                        continue
                    po = next((o + ptr - v for v, o, z in vsec if v <= ptr < v + z), None)
                    if po is None:
                        continue
                    s = d[po:po + nl]
                    if s[-1:] == b"\0" and re.fullmatch(rb"[A-Z_][A-Z0-9_]*(\.[A-Z_][A-Z0-9_]*)*", s[:-1]):
                        exc.add(s[:-1].decode())
        out["ada_exceptions"] = sorted(exc)
        out["user_exceptions"] = sorted(x for x in exc if "." in x and not x.startswith(_ADA_EXC_SYS))
        out["standard_exceptions"] = sorted(n for n in _ADA_STD_EXC if n in dfn) if rt else []
        # decoder routine (the function whose code references the stored HCFG blob)
        df = None
        if rt and decoder:
            hit = hit or hcfg_find(d, deadline=time.time() + 0.3)
            df = decoder_facts(d, hit=hit) if hit is not None else None
        fn = (df or {}).get("function", "none")
        out["decoder_function"] = fn
        out["decoder_function_ada"] = _ada_name(fn) if fn != "none" else "none"
        out["decoder_function_va"] = hex(df["function_va"]) if df else "none"
        out["decoder_algorithm"] = (df or {}).get("algorithm", "none")
        k = (df or {}).get("key", "none")
        out["decoder_key"] = hex(k) if isinstance(k, int) else "none"
        out["decoder_key_equals_header"] = (df or {}).get("key_equals_header", "none")
        hk = (df or {}).get("header_key", "none")
        out["header_key"] = hex(hk) if isinstance(hk, int) else "none"
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def gnat_field(data, name):
    """One gnat_facts value; "none" when the input is no executable image or the field is unknown (never raises)."""
    try:
        return (gnat_facts(data, decoder=name.startswith(("decoder_", "header_key"))) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- gfortran_facts: Fortran / GNU Fortran identity + entity facts (next-day candidate after Ada) ---------------------
# gfortran mangling: module entity `__<mod>_MOD_<name>` (module procedure / module variable), COMMON block and external
# procedure `<name>_` (lowercase + one trailing underscore), blank COMMON `__BLNK__`, main program `MAIN__` (+ a libc
# `main` stub calling _gfortran_set_args/_gfortran_set_options), SAVE'd / DATA locals `<name>.<N>`, BLOCK DATA unit
# `<name>_` (8-byte .bss marker, absent from DWARF). Runtime: DT_NEEDED libgfortran.so.N, `_gfortran_*` imports.
_DW_LANG_F = {**_DW_LANG, 0x08: "Fortran77", 0x09: "Fortran90", 0x0e: "Fortran95", 0x22: "Fortran03",
              0x23: "Fortran08", 0x2d: "Fortran18", 0x30: "Fortran23"}
_DW_FORTRAN = (0x08, 0x09, 0x0e, 0x22, 0x23, 0x2d, 0x30)
_GF_EXT = re.compile(r"^[a-z][a-z0-9_$]{0,62}_$")


def _gf_elf(d):
    """([(name, sh_type, addr, offset, size)], [(name, type, bind, shndx, value, size)]) of an ELF (raw structs)."""
    b64, e = d[4] == 2, "<" if d[5] == 1 else ">"
    shoff = struct.unpack_from(e + ("Q" if b64 else "I"), d, 40 if b64 else 32)[0]
    shes, shn, shstr = struct.unpack_from(e + "HHH", d, 58 if b64 else 46)
    if not shoff or shes < (64 if b64 else 40) or shoff + shn * shes > len(d):
        return [], []
    f = (e + "II8xQQQI4x8xQ") if b64 else (e + "II4xIIII4x4xI")   # name type [flags] addr off size link .. entsize
    raw = [struct.unpack_from(f, d, shoff + k * shes) for k in range(min(shn, 65535))]
    so = raw[shstr][3] if shstr < len(raw) else 0

    def nm(base, lim, o):
        z = d.find(b"\0", base + o, lim)
        return bytes(d[base + o:z if z >= 0 else lim]).decode("latin-1")
    secs = [(nm(so, len(d), r[0]) if so else "", r[1], r[2], r[3], r[4]) for r in raw]
    syms = []
    for _, ty, _, off, size, link, ent in raw:
        if ty not in (2, 11) or not 0 <= link < len(raw) or off + size > len(d):
            continue
        sb, sz = raw[link][3], raw[link][4]
        ent = ent or (24 if b64 else 16)
        for k in range(min(size // ent, 400_000 - len(syms))):
            o = off + k * ent
            if b64:
                n, info, shndx, val, ssz = struct.unpack_from(e + "IBxHQQ", d, o)
            else:
                n, val, ssz, info, shndx = struct.unpack_from(e + "IIIBxH", d, o)
            if n and n < sz:
                syms.append((nm(sb, sb + sz, n), info & 0xF, info >> 4, shndx, val, ssz))
    return secs, syms


def _gf_name(sym):
    """gfortran symbol -> Fortran entity: `__m_MOD_x` -> m::x, `blk_` -> blk, `__BLNK__` -> blank, `buf.0` -> buf."""
    if sym == "__BLNK__":
        return "blank"
    if sym.startswith("__") and "_MOD_" in sym:
        mod, _, name = sym[2:].partition("_MOD_")
        return f"{mod}::{name}"
    if _GF_EXT.match(sym):
        return sym[:-1]
    return re.sub(r"\.\d+$", "", sym)


def gfortran_facts(data, hcfg=True):
    """Fortran / GNU Fortran facts of an ELF image (bytes only): format, architecture, has_gfortran_runtime (+ alias
    has_fortran_runtime; DT_NEEDED libgfortran / `_gfortran_*` or MAIN__ symbols; raw-byte cues only count when the
    image has no symbol table), has_libgfortran_needed, libgfortran_soname, needed, gfortran_imports (sorted
    `_gfortran_*` names), has_main_program (MAIN__ defined), program_name (DWARF DW_AT_main_subprogram), main_source (CU
    name); fortran_modules, module_procedures `mod::name` (+ _mangled `__mod_MOD_name`), module_variables (+ _mangled),
    common_blocks (`name_` / blank, + _mangled), block_data, external_procedures (`name_` FUNCs, + _mangled),
    save_variables (`name.N` locals); dwarf_producer ("GNU Fortran2008 15.2.0") + _full / _version, dwarf_language
    ("DW_LANG_Fortran08") + _code, dwarf_languages; hcfg_symbol / hcfg_entity / hcfg_entity_kind (module_variable,
    common_block, save_variable, symbol) / hcfg_section for the raw HCFG (hcfg=False skips the scan). Absent ->
    "none" / "false" / []; not an ELF -> None."""
    try:
        d = bytes(data)
        if not (d[:4] == b"\x7fELF" and len(d) >= 64 and d[4] in (1, 2) and d[5] in (1, 2)):
            return None
        tf = lambda b: "true" if b else "false"   # noqa: E731
        e = "<" if d[5] == 1 else ">"
        try:
            secs, syms = _gf_elf(d)
        except _PARSE_ERR:
            secs, syms = [], []
        try:
            needed = list(_elf_pair_facts(d).get("needed") or [])
        except Exception:   # noqa: BLE001
            needed = []
        out = {"format": "elf", "architecture": _arch_of(d) or "none", "needed": needed}
        gfso = next((n for n in needed if n.startswith("libgfortran.so")), None)
        out["has_libgfortran_needed"] = tf(gfso)
        out["libgfortran_soname"] = gfso or "none"
        names = {s[0] for s in syms}
        imps = sorted({n.split("@")[0] for n in names if n.startswith("_gfortran_")})
        out["gfortran_imports"] = imps
        dfn = [s for s in syms if s[3] != 0]
        out["has_main_program"] = tf(any(s[0] == "MAIN__" and s[1] == 2 for s in dfn))
        rt = bool(gfso or imps or out["has_main_program"] == "true" or any("_MOD_" in s[0] for s in dfn))
        if not syms and not rt:
            rt = b"libgfortran.so" in d and b"_gfortran_" in d
        out["has_gfortran_runtime"] = out["has_fortran_runtime"] = tf(rt)
        sec_type = {k: s[1] for k, s in enumerate(secs)}
        mods, mp, mpm, mv, mvm, cb, cbm, ext, extm, sav, bd = ({}, set(), set(), set(), set(), set(), set(), set(),
                                                               set(), set(), set())
        dstr = b""
        if rt:
            for s in secs:
                if s[0] == ".debug_str" and s[1] != 8:
                    dstr = d[s[3]:s[3] + s[4]]
            cand = []
            for n, ty, bind, shndx, val, sz in dfn:
                if n.startswith("__") and "_MOD_" in n:
                    mod, _, nm_ = n[2:].partition("_MOD_")
                    if not mod or not nm_ or nm_.startswith("_"):   # __vtab_ / __def_init_ / __copy_ internals
                        continue
                    mods[mod] = mods.get(mod, 0) + 1
                    if ty == 2:
                        mp.add(f"{mod}::{nm_}")
                        mpm.add(n)
                    elif ty == 1:
                        mv.add(f"{mod}::{nm_}")
                        mvm.add(n)
                elif n == "__BLNK__" and ty == 1:
                    cb.add("blank")
                    cbm.add(n)
                elif _GF_EXT.match(n) and bind in (1, 2):
                    if ty == 2:
                        ext.add(n[:-1])
                        extm.add(n)
                    elif ty == 1:
                        cand.append((n, shndx, sz))
                elif ty == 1 and bind == 0 and re.match(r"^[a-z][a-z0-9_]*\.\d+$", n) and \
                        not n.startswith(("options.", "completed.")):
                    sav.add(n.split(".")[0])
            # BLOCK DATA unit marker vs COMMON block: DWARF linkage names list the commons; else an 8-byte .bss
            # object beside an initialised (PROGBITS) common is the BLOCK DATA marker
            indw = [c for c in cand if b"\0" + c[0].encode() + b"\0" in dstr]
            init = any(sec_type.get(c[1]) == 1 for c in cand)
            for c in cand:
                is_bd = (c not in indw) if indw else (init and sec_type.get(c[1]) == 8 and c[2] == (8 if d[4] == 2 else 4))
                if is_bd:
                    bd.add(c[0][:-1])
                else:
                    cb.add(c[0][:-1])
                    cbm.add(c[0])
        out["fortran_modules"] = sorted(mods)
        out["module_procedures"], out["module_procedures_mangled"] = sorted(mp), sorted(mpm)
        out["module_variables"], out["module_variables_mangled"] = sorted(mv), sorted(mvm)
        out["common_blocks"], out["common_blocks_mangled"] = sorted(cb), sorted(cbm)
        out["block_data"] = sorted(bd)
        out["external_procedures"], out["external_procedures_mangled"] = sorted(ext), sorted(extm)
        out["save_variables"] = sorted(sav)
        # DWARF
        lay = [(s[0], s[3], s[4]) for s in secs if s[1] != 8]
        cus = _dwarf_top_dies(d, lay, e) if lay else []
        langs = [c[1] for c in cus if c[1] is not None]
        fcu = [c for c in cus if c[1] in _DW_FORTRAN]
        pfull = next((c[0] for c in fcu if c[0]), None) or next((c[0] for c in cus if c[0]), None)
        if not pfull and rt and dstr:
            m = re.search(rb"GNU Fortran[0-9]* [0-9][^\0]{0,400}", dstr)
            pfull = m.group(0).decode("latin-1") if m else None
        out["dwarf_producer_full"] = pfull or "none"
        pm = re.match(r"(.*?\d+(?:\.\d+)+)", pfull or "")
        out["dwarf_producer"] = pm.group(1) if pm else (pfull or "none")
        vm = re.search(r"(\d+(?:\.\d+)+)", pfull or "")
        out["dwarf_producer_version"] = vm.group(1) if vm else "none"
        lc = fcu[0][1] if fcu else (max(set(langs), key=langs.count) if langs else None)
        out["dwarf_language_code"] = lc if lc is not None else "none"
        out["dwarf_language"] = f"DW_LANG_{_DW_LANG_F.get(lc, hex(lc))}" if lc is not None else "none"
        out["dwarf_languages"] = sorted({f"DW_LANG_{_DW_LANG_F.get(x, hex(x))}" for x in langs})
        out["main_source"] = next((c[2] for c in fcu if c[2]), "none")
        out["program_name"] = _gf_program(d) if fcu else "none"
        # HCFG holder
        hs = {"hcfg_symbol": "none", "hcfg_entity": "none", "hcfg_entity_kind": "none", "hcfg_section": "none"}
        if hcfg:
            hit = hcfg_find(d)
            off = getattr(hit, "offset", None) if hit is not None else None
            if isinstance(off, int) and d[off:off + 4] == HCFG_MAGIC:
                k = next((k for k, s in enumerate(secs) if s[1] != 8 and s[2] and s[3] <= off < s[3] + s[4]), None)
                if k is not None:
                    hs["hcfg_section"] = secs[k][0] or "none"
                    va = secs[k][2] + off - secs[k][3]
                    best = [s for s in dfn if s[1] in (0, 1) and s[3] == k and s[4] <= va < s[4] + max(s[5], 1)
                            and s[0] and not s[0].startswith(".")]
                    if best:
                        n = min(best, key=lambda s: (s[1] != 1, va - s[4]))[0]
                        hs["hcfg_symbol"], hs["hcfg_entity"] = n, _gf_name(n)
                        hs["hcfg_entity_kind"] = "module_variable" if "_MOD_" in n else (
                            "common_block" if n in cbm else ("save_variable" if re.search(r"\.\d+$", n)
                                                             else "symbol"))
        out.update(hs)
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def _gf_program(d):
    """Fortran main program name (DW_TAG_subprogram with DW_AT_main_subprogram) via pyelftools; "none" when absent
    or .debug_info is larger than 4 MB (bounded)."""
    try:
        from elftools.elf.elffile import ELFFile
        ef = ELFFile(io.BytesIO(d))
        s = ef.get_section_by_name(".debug_info")
        if s is None or s["sh_size"] > (4 << 20) or not ef.has_dwarf_info():
            return "none"
        for cu in ef.get_dwarf_info().iter_CUs():
            top = cu.get_top_DIE()
            lang = top.attributes.get("DW_AT_language")
            if lang is None or lang.value not in _DW_FORTRAN:
                continue
            for die in top.iter_children():
                if die.tag == "DW_TAG_subprogram" and "DW_AT_main_subprogram" in die.attributes:
                    nm = die.attributes.get("DW_AT_name")
                    if nm is not None:
                        v = nm.value
                        return v.decode("latin-1") if isinstance(v, bytes) else str(v)
        return "none"
    except Exception:  # noqa: BLE001
        return "none"


def gfortran_field(data, name):
    """One gfortran_facts value; "none" when the input is no ELF or the field is unknown (never raises)."""
    try:
        return (gfortran_facts(data, hcfg=name.startswith("hcfg_")) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- cobol_facts: GnuCOBOL (cobc) identity facts (next-day candidate) -------------------------------------------------
# cobc emits one C module per PROGRAM-ID: cob_module.module_name -> "<PROGRAM-ID>\0" followed by the
# module_formatted_date "Mmm dd yyyy hh:mm:ss\0" in .rodata (kept by strip), local symbols PID / PID_ /
# PID_module_init, imports cob_init / cob_module_global_enter / cob_check_version ..., DT_NEEDED libcob.so.N.
_COB_MOD = re.compile(rb"\0([A-Za-z0-9][A-Za-z0-9_-]{0,62})\0([A-Z][a-z]{2} [ 0-3]\d \d{4} \d\d:\d\d:\d\d)\0")
_COB_SRC = re.compile(rb"\0([^\0/\\]{1,120}\.(?:cob|cbl|cobol|ccp|cpy|pco))\0", re.I)


def cobol_facts(data):
    """GnuCOBOL facts of an ELF image (bytes only): format, architecture, needed, has_libcob_needed, libcob_soname,
    cob_imports (sorted `cob_*` dynamic symbols), has_cobol_runtime (+ alias has_gnucobol_runtime; libcob NEEDED or
    cob_init / cob_module_* imports; raw-byte cues only when the image has no symbol table), program_id (first module
    name of the .rodata module-name/compile-date pair, else the `<PID>_module_init` symbol), program_ids (all, file
    order), compile_date ("Oct 18 2026 12:23:53"), source_file (cobc input name). HCFG: hcfg_scan (split-raw /
    stack-built cover WORKING-STORAGE VALUE fields). Absent -> "none" / "false" / []; not an ELF -> None."""
    try:
        d = bytes(data)
        if not (d[:4] == b"\x7fELF" and len(d) >= 64 and d[4] in (1, 2) and d[5] in (1, 2)):
            return None
        tf = lambda b: "true" if b else "false"   # noqa: E731
        try:
            secs, syms = _gf_elf(d)
        except _PARSE_ERR:
            secs, syms = [], []
        try:
            needed = list(_elf_pair_facts(d).get("needed") or [])
        except Exception:   # noqa: BLE001
            needed = []
        out = {"format": "elf", "architecture": _arch_of(d) or "none", "needed": needed}
        so = next((n for n in needed if n.startswith("libcob.so")), None)
        out["has_libcob_needed"], out["libcob_soname"] = tf(so), so or "none"
        imps = sorted({s[0].split("@")[0] for s in syms if s[3] == 0 and s[0].startswith("cob_")})
        out["cob_imports"] = imps
        rt = bool(so or any(n in ("cob_init", "cob_module_enter", "cob_module_global_enter", "cob_check_version")
                            for n in imps))
        if not syms and not rt:
            rt = b"libcob.so" in d and b"cob_init\0" in d
        out["has_cobol_runtime"] = out["has_gnucobol_runtime"] = tf(rt)
        pids, date, src = [], "none", "none"
        if rt:
            ro = [(s[3], s[4]) for s in secs if s[0] == ".rodata" and s[1] == 1] or [(0, min(len(d), 64 << 20))]
            for off, sz in ro:
                blk = d[max(0, off - 1):off + sz]
                for m in _COB_MOD.finditer(blk):
                    if m.group(1).decode() not in pids:
                        pids.append(m.group(1).decode())
                    date = m.group(2).decode() if date == "none" else date
                ms = _COB_SRC.search(blk)
                if ms and src == "none":
                    src = ms.group(1).decode("latin-1")
            if not pids:
                pids = [s[0][:-12] for s in syms if s[0].endswith("_module_init") and s[3] != 0 and len(s[0]) > 12]
        out["program_id"] = pids[0] if pids else "none"
        out["program_ids"] = pids
        out["compile_date"], out["source_file"] = date, src
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def cobol_field(data, name):
    """One cobol_facts value; "none" when the input is no ELF or the field is unknown (never raises)."""
    try:
        return (cobol_facts(data) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- ghc_facts: Haskell / GHC identity + z-encoded closure facts (next-day candidate) ---------------------------------
# GHC symbol = [<unit>_]<Module>_<name>_<kind>, every part z-encoded (zi '.', zm '-', zd '$', ZC ':', zu '_', zh '#',
# z<hex>U code point, Z<n>T tuple ...); the `main` unit drops the prefix (Main_main_closure; ZCMain_main_closure is
# the :Main.main wrapper). Kinds: closure, info, con_info, entry, bytes (Addr# / ByteString literal: the HCFG holder),
# srt, ... rts: hs_main, hs_init_ghc, stg_* ; `+RTS --info` pairs ("GHC version", "<ver>"), ("RTS way", "rts_thr").
# Info tables keep con_desc strings "<unit>:<Module>.<Con>" even in strip'd images.
_Z_UP = {"L": "(", "R": ")", "M": "[", "N": "]", "C": ":", "Z": "Z"}
_Z_LO = {"z": "z", "a": "&", "b": "|", "c": "^", "d": "$", "e": "=", "g": ">", "h": "#", "i": ".", "l": "<", "m": "-",
         "n": "!", "p": "+", "q": "'", "r": "\\", "s": "/", "t": "*", "u": "_", "v": "%"}
_Z_TOK = re.compile(r"z([0-9a-f][0-9a-f]*)U|Z(\d+)([TH])|Z([LRMNCZ])|z([zabcdeghilmnpqrstuv])")
_GHC_SYM = re.compile(r"^(?:([a-z][A-Za-z0-9]*)_)?([A-Z][A-Za-z0-9]*)_(\w+?)_(closure|info|con_info|con_entry|"
                      r"static_info|entry|bytes|srt|slow|fast|str)$")
_GHC_MOD = re.compile(r"^[A-Z][\w']*(?:\.[A-Z][\w']*)*$")
_GHC_CONDESC = re.compile(rb":((?:[A-Z][\w']{0,80}\.){1,12})[^\0\s.][^\0\s]{0,63}\0")   # ':' prefix = fast search
_GHC_UNIT = re.compile(rb"(?:^|[^\w.:-])([a-z][A-Za-z0-9._-]{0,80})$")
_GHC_VER = re.compile(r"\d+\.\d+(?:\.\d+){0,2}")


def ghc_zdecode(s):
    """GHC z-decoding (compiler/GHC/Utils/Encoding.hs): 'ghczmprim' -> 'ghc-prim', 'GHCziBase' -> 'GHC.Base',
    'zdwmain' -> '$wmain', 'Z3T' -> '(,,)', 'z2192U' -> U+2192. Unknown escapes are kept verbatim."""
    def rep(m):
        if m.group(1):
            try:
                return chr(int(m.group(1), 16))
            except (ValueError, OverflowError):
                return m.group(0)
        if m.group(2):
            n = int(m.group(2))
            if m.group(3) == "T":
                return "(" + "," * max(n - 1, 0) + ")"
            return "(# #)" if n == 1 else "(#" + "," * (n - 1) + "#)"
        if m.group(4):
            return _Z_UP[m.group(4)]
        return _Z_LO[m.group(5)]
    return _Z_TOK.sub(rep, s)


def _ghc_sym(n):
    """(unit|None, Module, name, kind) of a z-encoded GHC closure symbol, else None."""
    m = _GHC_SYM.match(n)
    if not m:
        return None
    mod = ghc_zdecode(m.group(2))
    if not _GHC_MOD.match(mod):
        return None
    return (ghc_zdecode(m.group(1)) if m.group(1) else None), mod, ghc_zdecode(m.group(3)), m.group(4)


def ghc_facts(data, hcfg=True):
    """Haskell / GHC facts of an ELF image (bytes only): format, architecture, has_ghc_runtime (+ alias
    has_haskell_runtime; rts / z-encoded closure symbols in .symtab/.dynsym, or -- only when the image has no .symtab
    -- 2+ raw rts cues), has_hs_main, ghc_version (DWARF "Glorious Glasgow Haskell Compilation System <v>", the
    rts --info ("GHC version", "<v>") pair, a "GHC <v>" banner, a ghc-<v> libdir), rts_way ("rts_thr"...) +
    has_threaded_rts, haskell_modules (z-decoded, symbols + con_desc strings), user_modules (the `main` unit),
    haskell_packages (z-decoded unit ids, `main` excluded), main_module ("Main" when Main.main / :Main.main exist),
    closure_count, bytes_literals (z-decoded `<Mod>.<name>` of *_bytes literals); hcfg_symbol / hcfg_closure
    ("Config.hcfgBlob1") / hcfg_module / hcfg_unit / hcfg_kind / hcfg_section for the hcfg_find hit (hcfg=False skips
    the scan). Absent -> "none" / "false" / []; not an ELF -> None."""
    try:
        d = bytes(data)
        if not (d[:4] == b"\x7fELF" and len(d) >= 64 and d[4] in (1, 2) and d[5] in (1, 2)):
            return None
        tf = lambda b: "true" if b else "false"   # noqa: E731
        try:
            secs, syms = _gf_elf(d)
        except _PARSE_ERR:
            secs, syms = [], []
        out = {"format": "elf", "architecture": _arch_of(d) or "none"}
        names = {s[0] for s in syms}
        dfn = [s for s in syms if s[3] != 0]
        parsed = {}
        for s in syms:
            if s[0] not in parsed:
                p = _ghc_sym(s[0])
                if p:
                    parsed[s[0]] = p
        rts = names & {"hs_main", "hs_init_ghc", "hs_init", "hs_exit", "rts_evalLazyIO", "stg_ap_0_fast",
                       "stg_upd_frame_info", "ZCMain_main_closure"}
        wired = any(p[0] in ("ghc-prim", "base", "ghc-internal", "ghc-bignum") for p in parsed.values())
        rt = bool(rts or wired)
        if not rt and not any(s[1] == 2 for s in secs):   # strip'd (.dynsym holds libc imports only): raw cues
            cues = (b"GHC RTS\0", b"+RTS", b"ghc-prim:GHC.", b"Glasgow Haskell", b"base:GHC.", b"GHC version\0")
            rt = sum(c in d for c in cues) >= 2
        out["has_ghc_runtime"] = out["has_haskell_runtime"] = tf(rt)
        out["has_hs_main"] = tf(any(s[0] == "hs_main" for s in dfn))
        mods, user, pkgs, lits = set(), set(), set(), set()
        ver = way = None
        if rt:
            for unit, mod, nm_, kind in parsed.values():
                mods.add(mod)
                if unit is None or unit == "main":
                    user.add(mod)
                else:
                    pkgs.add(unit)
                if kind == "bytes":
                    lits.add(f"{mod}.{nm_}")
            ro = [(s[3], s[4]) for s in secs if s[1] == 1 and s[4] and s[0] not in (".text", ".plt", ".init", ".fini")]
            area = [d[o:o + n] for o, n in ro] if ro else [d]
            budget = 96 << 20
            for blk in area:
                blk = blk[:budget]
                budget -= len(blk)
                for m in _GHC_CONDESC.finditer(blk):
                    u = _GHC_UNIT.search(blk, max(0, m.start() - 82), m.start())
                    if not u:
                        continue
                    unit, mod = u.group(1).decode("latin-1"), m.group(1)[:-1].decode("latin-1")
                    mods.add(mod)
                    if unit == "main":
                        user.add(mod)
                    else:
                        pkgs.add(unit)
                if ver is None:
                    m = re.search(rb"Glorious Glasgow Haskell Compilation System,? (?:[Vv]ersion )?(\d+\.\d+[\d.]*)", blk)
                    m = m or re.search(rb"GHC version\0{1,64}(\d+\.\d+(?:\.\d+){0,2})\0", blk)
                    for rx in (rb"GHC (\d+\.\d+\.\d+(?:\.\d+)?)(?![\w.])", rb"ghc-(\d+\.\d+\.\d+(?:\.\d+)?)(?![\w.])"):
                        m = m or next((x for x in re.finditer(rx, blk)
                                       if not x.start() or blk[x.start() - 1:x.start()] not in b".-_" and
                                       not blk[x.start() - 1:x.start()].isalnum()), None)
                    if m:
                        ver = m.group(1).decode("latin-1").rstrip(".")
                if way is None:
                    m = re.search(rb"RTS way\0{1,64}(rts[A-Za-z0-9_]{0,24})\0", blk)
                    way = m.group(1).decode("latin-1") if m else None
                if budget <= 0:
                    break
        out["ghc_version"] = ver or "none"
        out["rts_way"] = way or "none"
        out["has_threaded_rts"] = tf(way and "thr" in way)
        out["haskell_modules"] = sorted(mods)
        out["user_modules"] = sorted(user)
        out["haskell_packages"] = sorted(pkgs)
        out["main_module"] = "Main" if rt and names & {"ZCMain_main_closure", "Main_main_closure", "Main_main_info"} \
            else "none"
        out["closure_count"] = sum(1 for p in parsed.values() if p[3] == "closure") if rt else 0
        out["bytes_literals"] = sorted(lits)
        hs = {"hcfg_symbol": "none", "hcfg_closure": "none", "hcfg_module": "none", "hcfg_unit": "none",
              "hcfg_kind": "none", "hcfg_section": "none"}
        if hcfg:
            hit = hcfg_find(d)
            off = getattr(hit, "offset", None) if hit is not None else None
            if isinstance(off, int) and 0 <= off < len(d):
                k = next((k for k, s in enumerate(secs) if s[1] != 8 and s[2] and s[3] <= off < s[3] + s[4]), None)
                if k is not None:
                    hs["hcfg_section"] = secs[k][0] or "none"
                    va = secs[k][2] + off - secs[k][3]
                    cand = [s for s in dfn if s[1] in (0, 1) and s[3] == k and s[0] and not s[0].startswith(".")
                            and (s[4] <= va < s[4] + s[5] or (not s[5] and 0 <= va - s[4] < 4096))]
                    if cand:
                        n = min(cand, key=lambda s: (not s[5], s[0] not in parsed, va - s[4]))[0]
                        hs["hcfg_symbol"] = n
                        p = parsed.get(n)
                        if p:
                            hs["hcfg_closure"], hs["hcfg_module"] = f"{p[1]}.{p[2]}", p[1]
                            hs["hcfg_unit"], hs["hcfg_kind"] = p[0] or "main", p[3]
        out.update(hs)
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def ghc_field(data, name):
    """One ghc_facts value; "none" when the input is no ELF or the field is unknown (never raises)."""
    try:
        return (ghc_facts(data, hcfg=name.startswith("hcfg_")) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- ocaml_facts: OCaml native (ocamlopt) identity + module / string-block facts (next-day candidate) -----------------
# Module M links caml<M><sep>{entry,code_begin,code_end,data_begin,data_end,frametable,gc_roots} + caml<M> (the module
# block) + functions caml<M><sep><fn>_<stamp>; sep is "__" up to 5.0, "." from 5.1 ("$" on targets without '.').
# dune executables wrap every module as Dune__exe__<M>; the stdlib is Stdlib / Stdlib__<M> / Camlinternal*.
# Runtime: caml_startup, caml_main, caml_program, caml_start_program; OCAMLRUNPARAM / CAMLRUNPARAM strings.
# Structured string constants are blocks: header word (wosize<<10 | color<<8 | 252 String_tag) then the payload; the
# data label (caml<M><sep><n>) sits AT the payload, whose last byte is the pad count (wosize*W-1-len, zero-filled).
# HCFG offset convention: the payload start (the 'H'), never the header word.
_OCAML_MODSYM = re.compile(r"^caml([A-Z][A-Za-z0-9_']*?)(__|\.|\$)(entry|code_begin|code_end|data_begin|data_end|"
                           r"frametable|gc_roots)$")
_OCAML_RT = {"caml_startup", "caml_main", "caml_program", "caml_start_program", "caml_startup_exn",
             "caml_startup_pooled", "caml_init_gc", "caml_alloc_shr", "caml_raise_exn", "caml_call_gc"}
_OCAML_VER = re.compile(rb"(?:\.opam/|/ocaml/|/ocaml-|ocaml-base-compiler\.|ocaml-variants\.|OCaml version |"
                        rb"The OCaml [a-z]+, version )(\d+\.\d{1,2}\.\d{1,2})(?![\d])")


def ocaml_string_block(d, off, word=8, little=True):
    """(header_offset, wosize, color, tag, pad) when `off` is the payload of a well-formed OCaml String_tag block
    (header word right before it, tag 252, last payload byte = pad count < word with zero padding before it), else None."""
    try:
        if off < word or off > len(d):
            return None
        hdr = int.from_bytes(d[off - word:off], "little" if little else "big")
        wo, tag = hdr >> 10, hdr & 0xFF
        if tag != 252 or not 0 < wo <= (len(d) - off) // word:
            return None
        end = off + wo * word
        pad = d[end - 1]
        if pad >= word or any(d[end - 1 - pad:end - 1]):
            return None
        return off - word, wo, (hdr >> 8) & 3, tag, pad
    except _PARSE_ERR:
        return None


def ocaml_facts(data, hcfg=True):
    """OCaml native (ocamlopt) facts of an ELF image (bytes only): format, architecture, has_ocaml_runtime (runtime /
    caml<M><sep>entry-family symbols in .symtab/.dynsym, or -- only without .symtab -- 2+ raw runtime cues),
    has_caml_main, ocaml_version (opam switch / libdir path), symbol_separator ("__" / "." / "$"), ocaml_modules (raw
    linked module names: Dune__exe__Main, Stdlib__Printf, ...), user_modules (no Stdlib / Camlinternal / Std_exit,
    Dune__exe__ prefix dropped), stdlib_modules, entry_symbols (caml<M><sep>entry), has_dune_exe, main_module ("Main"
    when linked, else the only user module), function_count; hcfg_symbol / hcfg_module / hcfg_section for the hcfg_find
    hit and its String_tag block (hcfg_in_ocaml_block, hcfg_block_header_offset = offset - word, hcfg_block_wosize,
    hcfg_block_tag, hcfg_block_pad; hcfg=False skips the scan). Absent -> "none" / "false" / [] / 0; not ELF -> None."""
    try:
        d = bytes(data)
        if not (d[:4] == b"\x7fELF" and len(d) >= 64 and d[4] in (1, 2) and d[5] in (1, 2)):
            return None
        tf = lambda b: "true" if b else "false"   # noqa: E731
        try:
            secs, syms = _gf_elf(d)
        except _PARSE_ERR:
            secs, syms = [], []
        out = {"format": "elf", "architecture": _arch_of(d) or "none"}
        dfn = [s for s in syms if s[3] != 0]
        names = {s[0] for s in dfn}
        mods, seps, entries = set(), [], set()
        for n in names:
            m = _OCAML_MODSYM.match(n) if n.startswith("caml") else None
            if m:
                mods.add(m.group(1))
                seps.append(m.group(2))
                if m.group(3) == "entry":
                    entries.add(n)
        rt = bool(names & _OCAML_RT) or len(mods) >= 2
        if not rt and not any(s[1] == 2 for s in secs):   # strip'd: raw runtime cues
            cues = (b"OCAMLRUNPARAM\0", b"CAMLRUNPARAM\0", b"Fatal error: exception ", b"caml_startup",
                    b"Stdlib.Exit", b"Out of memory\0")
            rt = sum(c in d for c in cues) >= 2
        if not rt:
            mods, seps, entries = set(), [], set()
        out["has_ocaml_runtime"] = tf(rt)
        out["has_caml_main"] = tf(rt and "caml_main" in names)
        ver = None
        if rt:
            ro = [(s[3], s[4]) for s in secs if s[1] == 1 and s[4] and s[0] not in (".text", ".plt", ".init", ".fini")]
            budget = 96 << 20
            for o, n in (ro or [(0, len(d))]):
                m = _OCAML_VER.search(d, o, o + min(n, max(budget, 0)))
                budget -= n
                if m:
                    ver = m.group(1).decode("latin-1")
                    break
        out["ocaml_version"] = ver or "none"
        out["symbol_separator"] = max(set(seps), key=seps.count) if seps else "none"
        std = {m for m in mods if m == "Stdlib" or m.startswith(("Stdlib__", "Camlinternal", "Std_exit"))}
        user = {m[11:] if m.startswith("Dune__exe__") else m for m in mods - std}
        out["ocaml_modules"] = sorted(mods)
        out["user_modules"] = sorted(user)
        out["stdlib_modules"] = sorted(std)
        out["entry_symbols"] = sorted(entries)
        out["has_dune_exe"] = tf(any(m.startswith("Dune__exe__") for m in mods))
        out["main_module"] = "Main" if "Main" in user else (next(iter(user)) if len(user) == 1 else "none")
        fn = 0
        if mods:
            pre = {"caml" + m + s for m in mods for s in set(seps)}
            fn = sum(1 for s in dfn if s[1] == 2 and s[0][:4] == "caml" and _OCAML_MODSYM.match(s[0]) is None
                     and re.search(r"_\d+$", s[0]) and any(s[0].startswith(p) for p in pre))
        out["function_count"] = fn
        hs = {"hcfg_symbol": "none", "hcfg_module": "none", "hcfg_section": "none", "hcfg_in_ocaml_block": "false",
              "hcfg_block_header_offset": "none", "hcfg_block_wosize": "none", "hcfg_block_tag": "none",
              "hcfg_block_pad": "none"}
        if hcfg:
            hit = hcfg_find(d)
            off = getattr(hit, "offset", None) if hit is not None else None
            if isinstance(off, int) and 0 <= off < len(d):
                blk = ocaml_string_block(d, off, 8 if d[4] == 2 else 4, d[5] == 1) if rt else None
                if blk:
                    hs["hcfg_in_ocaml_block"] = "true"
                    hs["hcfg_block_header_offset"], hs["hcfg_block_wosize"] = blk[0], blk[1]
                    hs["hcfg_block_tag"], hs["hcfg_block_pad"] = blk[3], blk[4]
                k = next((k for k, s in enumerate(secs) if s[1] != 8 and s[2] and s[3] <= off < s[3] + s[4]), None)
                if k is not None:
                    hs["hcfg_section"] = secs[k][0] or "none"
                    va = secs[k][2] + off - secs[k][3]
                    cand = [s for s in dfn if s[1] in (0, 1) and s[0] and not s[0].startswith(".")
                            and (s[3] == k or s[3] == 0xFFF1) and (s[4] == va or s[4] < va < s[4] + s[5])]
                    if cand:
                        n = min(cand, key=lambda s: (s[4] != va, not s[0].startswith("caml"), va - s[4]))[0]
                        hs["hcfg_symbol"] = n
                        ms = [m for m in mods if any(n.startswith("caml" + m + sp) for sp in ("__", ".", "$"))]
                        if ms:
                            hs["hcfg_module"] = max(ms, key=len)
        out.update(hs)
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def ocaml_field(data, name):
    """One ocaml_facts value; "none" when the input is no ELF or the field is unknown (never raises)."""
    try:
        return (ocaml_facts(data, hcfg=name.startswith("hcfg_")) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- dart_facts: Dart AOT (`dart compile exe`) snapshot identity + HCFG placement (next-day candidate) ---------------
# The AOT snapshot is an ELF whose .dynsym exports _kDartVmSnapshotData/Instructions, _kDartIsolateSnapshotData/
# Instructions (+ _kDart*SnapshotBss, _kDartSnapshotBuildId). Packaging: dart2native appends it to dartaotruntime
# (PE/ELF/Mach-O): runtime ++ pad to 4096 ++ snapshot ELF ++ uint64 LE snapshot offset ++ dc dc f6 f6 00 00 00 00; or
# the snapshot symbols sit in the image's own ELF (standalone). Each *SnapshotData opens with runtime/vm/snapshot.h's
# header: int32 magic 0xdcdcf5f5, int64 length, int64 kind (0 full, 1 full-core, 2 full-jit, 3 full-aot), the 32-char
# version hash, then the NUL-terminated features string ("product ... x64 compressed-pointers null-safety").
# String literals are OneByteString objects (latin-1 payload after a tags word + Smi length) -> hcfg_find's raw /
# base64 scan sees them; HCFG offset stays the payload start. Runtime cues: Dart_* API names, "<ver> (<channel>) (...)
# on \"<os>_<arch>\"". The version hash ties the image to an SDK build (provenance).
_DART_TRAILER = b"\xdc\xdc\xf6\xf6\0\0\0\0"
_DART_SNAP_MAGIC = b"\xf5\xf5\xdc\xdc"
_DART_SYMS = ("_kDartVmSnapshotData", "_kDartVmSnapshotInstructions", "_kDartIsolateSnapshotData",
              "_kDartIsolateSnapshotInstructions")
_DART_KIND = {0: "full", 1: "full-core", 2: "full-jit", 3: "full-aot"}
_DART_ARCH = ("x64", "ia32", "arm64", "arm", "riscv64", "riscv32", "simarm", "simarm64")
_DART_VER = re.compile(rb"(\d+\.\d+\.\d+(?:-[\w.]+)?) \((stable|beta|dev|main|be)\) \([^)]{0,80}\) on \"(\w{1,40})\"")


def _dart_snap_elf(d, base):
    """(symbols {name: file offset in d}, secs, syms, base) of an ELF at d[base:] exporting _kDart* symbols, else None."""
    sub = d[base:] if base else d
    if sub[:4] != b"\x7fELF" or len(sub) < 64 or sub[4] not in (1, 2) or sub[5] not in (1, 2):
        return None
    try:
        secs, syms = _gf_elf(sub)
    except _PARSE_ERR:
        return None
    out = {}
    for n, _ty, _b, shndx, val, _sz in syms:
        if n.startswith("_kDart") and n not in out and 0 < shndx < len(secs):
            s = secs[shndx]
            out[n] = base + s[3] + val - s[2] if s[1] != 8 and s[2] <= val <= s[2] + s[4] else None
    return (out, secs, syms, base) if any(k in out for k in _DART_SYMS) else None


def _dart_header(d, off):
    """(length, kind, hash, features) of a snapshot header at d[off], else None."""
    if not isinstance(off, int) or off < 0 or d[off:off + 4] != _DART_SNAP_MAGIC:
        return None
    ln, kind = struct.unpack_from("<qq", d, off + 4)
    h = bytes(d[off + 20:off + 52])
    if not re.fullmatch(rb"[0-9a-f]{32}", h):
        return None
    z = d.find(b"\0", off + 52, off + 52 + 2048)
    feat = bytes(d[off + 52:z]).decode("latin-1") if z > 0 else ""
    return ln, kind, h.decode(), feat if all(32 <= ord(c) < 127 for c in feat) else ""


def dart_facts(data, hcfg=True):
    """Dart AOT facts of an executable (bytes only): format, architecture, has_dart_runtime (Dart_* API strings or
    snapshot symbols), is_dart_aot (snapshot ELF exporting _kDart* found), packaging ("appended" dart2native trailer /
    "standalone" own .dynsym / "embedded" ELF inside / "none"), snapshot_offset + snapshot_size (embedded ELF; 0 +
    file size standalone), snapshot_symbols (sorted _kDart*), vm/isolate_snapshot_data/instructions_offset (file
    offsets), snapshot_build_id (GNU build-id note of the snapshot ELF, hex), snapshot_hash (32-hex version hash of the
    isolate -- else vm -- data header), snapshot_kind ("full-aot"), snapshot_features, snapshot_arch,
    compressed_pointers, null_safety, product_mode, dart_version / dart_channel / dart_target ("3.5.4" "stable"
    "linux_x64"); hcfg_symbol (_kDart* region holding the hcfg_find hit) / hcfg_section (snapshot ELF section) /
    hcfg_in_snapshot (hcfg=False skips the scan). Absent -> "none" / "false" / []; not PE/ELF/Mach-O -> None."""
    try:
        d = bytes(data)
        fmt = ("elf" if d[:4] == b"\x7fELF" else "pe" if d[:2] == b"MZ" else
               "macho" if d[:4] in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe") else None)
        if fmt is None or len(d) < 64:
            return None
        tf = lambda b: "true" if b else "false"   # noqa: E731
        out = {"format": fmt, "architecture": _arch_of(d) or "none"}
        snap, pack, size = None, "none", "none"
        if d[-8:] == _DART_TRAILER and len(d) >= 80:
            off = struct.unpack_from("<Q", d, len(d) - 16)[0]
            if 0 < off < len(d) - 16:
                snap = _dart_snap_elf(d[:len(d) - 16], off)
                if snap:
                    pack, size = "appended", len(d) - 16 - off
        if snap is None and fmt == "elf":
            snap = _dart_snap_elf(d, 0)
            if snap:
                pack, size = "standalone", len(d)
        if snap is None and b"_kDartIsolateSnapshotData" in d:
            p, tries = d.find(b"\x7fELF", 1), 0
            while 0 < p and tries < 64:
                tries += 1
                if p % 16 == 0:
                    snap = _dart_snap_elf(d, p)
                    if snap:
                        pack, size = "embedded", len(d) - p
                        break
                p = d.find(b"\x7fELF", p + 1)
        syms, secs, base = (snap[0], snap[1], snap[3]) if snap else ({}, [], 0)
        api = len(set(re.findall(rb"\bDart_(?:Initialize|CreateIsolateGroup\w*|RunLoop|ShutdownIsolate|Cleanup|"
                                 rb"IsolateMakeRunnable|InvokeMain\w*|NewStringFromCString|SetVMFlags)\b", d[:96 << 20])))
        out["is_dart_aot"] = tf(snap)
        out["packaging"] = pack
        out["snapshot_offset"] = base if snap else "none"
        out["snapshot_size"] = size
        out["snapshot_symbols"] = sorted(syms)
        for k, n in (("vm_snapshot_data_offset", "_kDartVmSnapshotData"),
                     ("vm_snapshot_instructions_offset", "_kDartVmSnapshotInstructions"),
                     ("isolate_snapshot_data_offset", "_kDartIsolateSnapshotData"),
                     ("isolate_snapshot_instructions_offset", "_kDartIsolateSnapshotInstructions")):
            out[k] = syms[n] if isinstance(syms.get(n), int) else "none"
        bid = "none"
        for nm_, ty, _a, so, sz in secs:
            if ty == 7 and nm_ == ".note.gnu.build-id" and sz >= 16:
                o = base + so
                nsz, dsz, nty = struct.unpack_from("<III", d, o)
                if nty == 3 and 0 < dsz <= 64:
                    bid = d[o + 12 + ((nsz + 3) & ~3):][:dsz].hex()
        out["snapshot_build_id"] = bid
        hdr = (_dart_header(d, out["isolate_snapshot_data_offset"]) or
               _dart_header(d, out["vm_snapshot_data_offset"]))
        if hdr is None and snap is None and api >= 2:   # symbols lost: one bounded header scan
            p, tries = d.find(_DART_SNAP_MAGIC), 0
            while p >= 0 and hdr is None and tries < 256:
                tries += 1
                hdr = _dart_header(d, p)
                p = d.find(_DART_SNAP_MAGIC, p + 1)
        out["has_dart_runtime"] = tf(snap or hdr)   # Dart_* strings alone (a literal) never decide
        out = {k: out[k] for k in ("format", "architecture", "has_dart_runtime")} | out
        feats = hdr[3].split() if hdr else []
        out["snapshot_hash"] = hdr[2] if hdr else "none"
        out["snapshot_kind"] = _DART_KIND.get(hdr[1], str(hdr[1])) if hdr else "none"
        out["snapshot_features"] = hdr[3] if hdr and hdr[3] else "none"
        out["snapshot_arch"] = next((t for t in feats if t in _DART_ARCH), "none")
        out["compressed_pointers"] = ("true" if "compressed-pointers" in feats else "false") if feats else "none"
        out["null_safety"] = ("true" if "null-safety" in feats else "false" if "no-null-safety" in feats else "none") \
            if feats else "none"
        out["product_mode"] = tf("product" in feats) if feats else "none"
        m = _DART_VER.search(d, 0, base if snap and base else min(len(d), 96 << 20)) if out["has_dart_runtime"] == \
            "true" else None
        out["dart_version"] = m.group(1).decode() if m else "none"
        out["dart_channel"] = m.group(2).decode() if m else "none"
        out["dart_target"] = m.group(3).decode() if m else "none"
        hs = {"hcfg_symbol": "none", "hcfg_section": "none", "hcfg_in_snapshot": "none"}
        if hcfg:
            hit = hcfg_find(d)
            off = getattr(hit, "offset", None) if hit is not None else None
            if isinstance(off, int) and 0 <= off < len(d):
                inside = bool(snap) and base <= off < base + (size if isinstance(size, int) else 0)
                hs["hcfg_in_snapshot"] = tf(inside)
                if inside:
                    rel = off - base
                    k = next((k for k, s in enumerate(secs) if s[1] != 8 and s[4] and s[3] <= rel < s[3] + s[4]), None)
                    if k is not None:
                        hs["hcfg_section"] = secs[k][0] or "none"
                        own = [(o, n) for n, o in syms.items() if isinstance(o, int) and o <= off and
                               any(s[0] == n and s[3] == k for s in snap[2])]
                        if own:
                            hs["hcfg_symbol"] = max(own)[1]
        out.update(hs)
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def dart_field(data, name):
    """One dart_facts value; "none" when the input is no executable or the field is unknown (never raises)."""
    try:
        return (dart_facts(data, hcfg=name.startswith("hcfg_")) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- kotlin_native_facts: Kotlin/Native (konanc) identity + kfun / KString facts (next-day candidate) -----------------
# konanc symbols: kfun:<owner>#<name>(<params>){}<ret> (owner = package or package.Class, "" at the root:
# kfun:#main(){}), kclass:<fq>, ktype:<fq> (TypeInfo), kvar:/kobjref:. Runtime: Konan_main / Konan_start /
# Kotlin_initRuntimeIfNeeded. String literals are static KString arrays: ArrayHeader {TypeInfo* (low bits = tags),
# uint32 count} (16 bytes on 64-bit, 8 on 32-bit) then count UTF-16 code units, no terminator -> an HCFG stored as text
# sits in a utf16le-* hit whose offset (= first stored byte) is the KString payload.
_KN_RT = {"Konan_main", "Konan_start", "Konan_run_start", "Kotlin_initRuntimeIfNeeded", "Kotlin_initRuntime",
          "Kotlin_deinitRuntimeIfNeeded", "Kotlin_main"}
_KN_CUES = (b"kotlin.native.internal", b"Kotlin_initRuntimeIfNeeded", b"Konan_main", b"Konan_start",
            b"kotlin.native.concurrent", b"kfun:")
_KN_STD = ("kotlin.", "kotlinx.", "kotlin#", "kotlinx#")


def _kn_fun(n):
    """'kfun:com.x.Cfg#decode(kotlin.String){}kotlin.Int' -> ('com.x.Cfg', 'decode') or None."""
    owner, sep, rest = n[5:].partition("#")
    name = re.match(r"[^(]*", rest).group(0) if sep else ""
    return (owner, name) if name else None


def kotlin_native_facts(data, hcfg=True):
    """Kotlin/Native (konanc) facts of an ELF image (bytes only): format, architecture, has_kotlin_native_runtime
    (Konan_main / Kotlin_initRuntimeIfNeeded / kfun:/kclass:/ktype: symbols in .symtab/.dynsym, or -- only without
    .symtab -- 2+ raw runtime cues, ASCII or UTF-16LE), has_konan_main, kfun_symbols (defined kfun: names, raw),
    user_kfun_symbols (no kotlin./kotlinx. owner), kotlin_functions (user owner.name, root -> name), kfun_owners,
    kclass_names / ktype_names (user, prefix dropped), main_function (the root `main` kfun symbol), function_count
    (user kfuns), stdlib_function_count; hcfg_encoding / hcfg_symbol / hcfg_section for the hcfg_find hit and its
    KString (hcfg_in_kstring when the uint32 count before the payload covers the UTF-16 text, hcfg_kstring_header_offset
    = offset - 16 (64-bit) / - 8, hcfg_kstring_length = count, hcfg_kstring_type = symbol the TypeInfo pointer & ~3
    names; hcfg=False skips the scan). Absent -> "none" / "false" / [] / 0; not ELF -> None."""
    try:
        d = bytes(data)
        if not (d[:4] == b"\x7fELF" and len(d) >= 64 and d[4] in (1, 2) and d[5] in (1, 2)):
            return None
        tf = lambda b: "true" if b else "false"   # noqa: E731
        try:
            secs, syms = _gf_elf(d)
        except _PARSE_ERR:
            secs, syms = [], []
        out = {"format": "elf", "architecture": _arch_of(d) or "none"}
        dfn = [s for s in syms if s[3] != 0]
        names = {s[0] for s in dfn}
        kfun = sorted(n for n in names if n.startswith("kfun:"))
        kcls = {n for n in names if n.startswith(("kclass:", "ktype:"))}
        rt = bool(names & _KN_RT) or bool(kfun) and bool(kcls or len(kfun) >= 2)
        if not rt and not any(s[1] == 2 for s in secs):   # strip'd: raw runtime cues (TypeInfo names are KStrings)
            rt = sum(c in d or _widen(c) in d for c in _KN_CUES) >= 2
        if not rt:
            kfun, kcls = [], set()
        out["has_kotlin_native_runtime"] = tf(rt)
        out["has_konan_main"] = tf(rt and "Konan_main" in names)
        user = [n for n in kfun if not n[5:].startswith(_KN_STD)]
        parsed = [p for p in map(_kn_fun, user) if p]
        out["kfun_symbols"], out["user_kfun_symbols"] = kfun, user
        out["kotlin_functions"] = sorted({f"{o}.{m}" if o else m for o, m in parsed})
        out["kfun_owners"] = sorted({o for o, _ in parsed if o})
        for pre, key in (("kclass:", "kclass_names"), ("ktype:", "ktype_names")):
            out[key] = sorted(n[len(pre):] for n in kcls if n.startswith(pre) and not n[len(pre):].startswith(_KN_STD))
        out["main_function"] = next((n for n in user if n.startswith("kfun:#main(")), "none")
        out["function_count"], out["stdlib_function_count"] = len(user), len(kfun) - len(user)
        hs = {"hcfg_encoding": "none", "hcfg_symbol": "none", "hcfg_section": "none", "hcfg_in_kstring": "false",
              "hcfg_kstring_header_offset": "none", "hcfg_kstring_length": "none", "hcfg_kstring_type": "none"}
        if hcfg:
            hit = hcfg_find(d)
            off = getattr(hit, "offset", None) if hit is not None else None
            if isinstance(off, int) and 0 <= off < len(d):
                hs["hcfg_encoding"] = hit.encoding
                w, e = (8, "<Q") if d[4] == 2 else (4, "<I")
                e = e if d[5] == 1 else ">" + e[1]
                ue = "<I" if d[5] == 1 else ">I"
                run = re.match(rb"(?:[\x09-\x7e]\x00)*", d[off:off + (2 << 20)]).group(0)
                # sizeof(ArrayHeader) = 2 words (count, then pad on 64-bit); packed 12-byte header as fallback
                for ho, co in ((off - 2 * w, off - w), (off - 12, off - 4)) if w == 8 else ((off - 8, off - 4),):
                    if not (rt and hit.encoding.startswith("utf16le-") and ho >= 0):
                        break
                    cnt = struct.unpack_from(ue, d, co)[0]
                    if 0 < cnt <= len(run) // 2 and not any(d[co + 4:off]):
                        hs["hcfg_in_kstring"] = "true"
                        hs["hcfg_kstring_header_offset"], hs["hcfg_kstring_length"] = ho, cnt
                        ti = struct.unpack_from(e, d, ho)[0] & ~3
                        tn = [s[0] for s in dfn if s[4] == ti and ti and s[1] in (0, 1) and s[0].startswith("ktype:")]
                        hs["hcfg_kstring_type"] = tn[0] if tn else "none"
                        break
                k = next((k for k, s in enumerate(secs) if s[1] != 8 and s[2] and s[3] <= off < s[3] + s[4]), None)
                if k is not None:
                    hs["hcfg_section"] = secs[k][0] or "none"
                    va = secs[k][2] + off - secs[k][3]
                    cand = [s for s in dfn if s[1] in (0, 1) and s[0] and not s[0].startswith(".")
                            and (s[3] == k or s[3] == 0xFFF1) and (s[4] == va or s[4] < va < s[4] + s[5])]
                    if cand:
                        hs["hcfg_symbol"] = min(cand, key=lambda s: (s[4] != va, va - s[4]))[0]
        out.update(hs)
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def kotlin_native_field(data, name):
    """One kotlin_native_facts value; "none" when the input is no ELF or the field is unknown (never raises)."""
    try:
        return (kotlin_native_facts(data, hcfg=name.startswith("hcfg_")) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- language_of: ONE consistent source-language / toolchain token per image (17 seen D1-D17 + next candidates) ----
# Seen (expected = the day's theme): d01/d15 c, d02 cpp, d03 csharp (.NET dll), d04 go, d05 rust, d06 java, d07 kotlin,
# d08 swift, d09 nim, d10 zig, d11 d, d12 pascal, d13 crystal, d14 objc, d16 wasm, d17 ada.
LANG_TOKEN = {"gnat": "ada", "fpc": "pascal"}            # lang_facts runtime keys -> language_of tokens
LANG_ALIASES = {"c": ["c"], "cpp": ["cpp", "c++"], "csharp": ["csharp", "c#", "dotnet", ".net"],
                "fsharp": ["fsharp", "f#", "dotnet"], "vbnet": ["vbnet", "vb.net", "dotnet"], "go": ["go", "golang"],
                "rust": ["rust"], "java": ["java", "jvm"], "kotlin": ["kotlin", "jvm"], "scala": ["scala", "jvm"],
                "groovy": ["groovy", "jvm"], "clojure": ["clojure", "jvm"], "swift": ["swift"], "nim": ["nim"],
                "zig": ["zig"], "d": ["d", "dlang"], "pascal": ["pascal", "fpc", "freepascal", "delphi", "objectpascal"],
                "crystal": ["crystal"], "objc": ["objc", "objective-c"], "wasm": ["wasm", "wat", "webassembly"],
                "ada": ["ada", "gnat"], "haskell": ["haskell", "ghc"], "ocaml": ["ocaml"], "fortran": ["fortran"],
                "cobol": ["cobol"], "odin": ["odin"], "v": ["v", "vlang"], "dart": ["dart"], "julia": ["julia"],
                "kotlin-native": ["kotlin-native", "kotlin", "konan"], "python": ["python"], "vb6": ["vb6", "visualbasic"],
                "autoit": ["autoit"]}
# candidate runtimes lang_facts does not know: (token, toolchain, kind, cues). kind "sym" = a symbol-name cue: it only
# decides when found in .strtab/.dynstr (or the image has no symbol table); a hit elsewhere in the bytes (string
# literal) is logged under `ambiguous`. kind "str" = a runtime string / magic that is decisive anywhere.
_LANG_CUES = (
    ("kotlin-native", "konan", "sym", (b"kfun:", b"Konan_main", b"Kotlin_initRuntime")),
    ("haskell", "ghc", "sym", (b"ghczmprim_GHC", b"base_GHCziTopHandler", b"hs_init_ghc", b"stg_ap_0_fast")),
    ("ocaml", "ocamlopt", "sym", (b"caml_startup", b"caml_main", b"camlStdlib", b"caml_program")),
    ("fortran", "gfortran", "sym", (b"_gfortran_set_args", b"_gfortran_st_write", b"_gfortran_set_options")),
    ("cobol", "gnucobol", "sym", (b"cob_init", b"cob_module_enter", b"cob_resolve")),
    ("julia", "julia", "sym", (b"jl_init_with_image", b"jl_atexit_hook", b"libjulia")),
    ("dart", "dart", "sym", (b"_kDartVmSnapshotData", b"_kDartIsolateSnapshotInstructions")),
    ("odin", "odin", "sym", (b"__$startup_runtime", b"__$cleanup_runtime", b"runtime.default_allocator_proc")),
    ("v", "v", "sym", (b"_vinit", b"_vcleanup", b"builtin__panic")),
    ("python", "pyinstaller", "str", (b"MEI\x0c\x0b\x0a\x0b\x0e", b"_MEIPASS2", b"pyi-runtime-tmpdir")),
    ("python", "nuitka", "str", (b"__nuitka_", b"NUITKA_ONEFILE", b"nuitka-version")),
    ("python", "py2exe", "str", (b"PYTHONSCRIPT\0",)),
    ("csharp", "nativeaot", "sym", (b"S_P_CoreLib_System_", b"__managed__Main")),
    ("vb6", "msvbvm", "str", (b"MSVBVM60.DLL", b"MSVBVM50.DLL")),
    ("autoit", "autoit", "str", (b"AU3!EA06", b">>>AUTOIT SCRIPT<<<")),
    ("pascal", "delphi", "str", (b"Embarcadero Delphi", b"Borland Delphi", b"SOFTWARE\\Borland\\Delphi\\RTL")),
)
_TC_NATIVE = {"go": "gc", "rust": "rustc", "swift": "swiftc", "nim": "nim", "zig": "zig", "pascal": "fpc",
              "crystal": "crystal", "ada": "gnat"}
_WASM_PRODUCERS = ((b"rustc", "rustc", "rust"), (b"Emscripten", "emscripten", "c"), (b"TinyGo", "tinygo", "go"),
                   (b"AssemblyScript", "assemblyscript", "assemblyscript"), (b"clang", "clang", "c"),
                   (b"wit-component", "wit-component", "none"))


def _jvm_lang(names, read):
    """(language, evidence) for a jar's entry names / class-bytes reader (None, []) when no JVM content."""
    cls = [n for n in names if n.endswith(".class")]
    if not cls:
        return None, []
    for tok, pre in (("kotlin", "kotlin/"), ("scala", "scala/"), ("clojure", "clojure/"), ("groovy", "groovy/")):
        if any(n.startswith(pre) for n in names):
            return tok, [f"jar entries {pre}*"]
    if any(n.endswith(".kotlin_module") for n in names):
        return "kotlin", ["META-INF/*.kotlin_module"]
    for n in cls[:64]:
        b = read(n)
        for tok, cue in (("kotlin", b"Lkotlin/Metadata;"), ("scala", b"Lscala/reflect/ScalaSignature;"),
                         ("groovy", b"groovy/lang/GroovyObject"), ("clojure", b"clojure/lang/")):
            if cue in b:
                return tok, [f"{n}: {cue.decode()}"]
    return "java", [f"{len(cls)} .class entries, no kotlin/scala/groovy/clojure marker"]


def language_of(data):
    """Source language + toolchain of a compiled member, with evidence (bytes only, no subprocess).
    -> {format, language, toolchain, aliases, evidence [..], candidates [every language with a cue], ambiguous
    "true"/"false", ambiguous_with [..], source_language (wasm producers / .NET flavour, else "none")}.
    language tokens: c cpp csharp fsharp vbnet go rust java kotlin scala groovy clojure swift nim zig d pascal crystal
    objc wasm ada + candidates haskell ocaml fortran cobol odin v dart julia kotlin-native python vb6 autoit.
    Native images: lang_facts runtime hit (gnat->ada, fpc->pascal) wins; a candidate cue table refines c/cpp
    (C-runtime languages). .NET PE (CLI header + BSJB) -> csharp unless FSharp.Core / Microsoft.VisualBasic.
    jar / bare .class -> java unless kotlin/scala/groovy/clojure markers. wasm stays "wasm" (D16), its producers
    section only fills toolchain/source_language. None for anything that is not an executable image / jar / class."""
    try:
        d = bytes(data)
        ev, cands = [], []
        out = {"format": "none", "language": "none", "toolchain": "none", "source_language": "none"}
        if d[:4] == b"\xca\xfe\xba\xbe" and len(d) >= 10 and int.from_bytes(d[6:8], "big") >= 45 \
                and int.from_bytes(d[4:8], "big") >= 45:
            out["format"] = "class"
            lang, ev = _jvm_lang(["x.class"], lambda n: d)
        elif d[:2] == b"PK":
            import zipfile
            try:
                z = zipfile.ZipFile(io.BytesIO(d))
                names = z.namelist()
            except (zipfile.BadZipFile, OSError, EOFError, RuntimeError, ValueError, struct.error):
                return None

            def read(n):
                try:
                    zi = z.getinfo(n)
                    return z.read(n) if zi.file_size < (4 << 20) else b""
                except Exception:   # noqa: BLE001 -- encrypted / broken entry
                    return b""
            lang, ev = _jvm_lang(names, read)
            if lang is None:
                return None
            out["format"] = "jar"
        else:
            lang = None
            lay = _pe_layout(d) if d[:2] == b"MZ" else None
            if lay and len(lay[2]) > 14 and lay[2][14][0] and b"BSJB" in d:
                out["format"] = "pe"
                lang = "fsharp" if b"FSharp.Core" in d else ("vbnet" if b"Microsoft.VisualBasic" in d else "csharp")
                ev = ["PE CLI header (data dir 14) + BSJB metadata"] + \
                     ([f"assembly ref {'FSharp.Core' if lang == 'fsharp' else 'Microsoft.VisualBasic'}"]
                      if lang != "csharp" else [])
                out["toolchain"] = "dotnet"
                if b"<CrtImplementationDetails>" in d:
                    lang, ev = "cpp", ev + ["C++/CLI <CrtImplementationDetails>"]
                    out["toolchain"] = "msvc"
                out["source_language"] = lang
        if lang is not None:
            out["toolchain"] = out["toolchain"] if out["toolchain"] != "none" else \
                {"kotlin": "kotlinc", "scala": "scalac", "groovy": "groovyc", "clojure": "clojure"}.get(lang, "javac")
            cands = [lang]
        else:
            f = lang_facts(d)
            if not f:
                return None
            fmt = out["format"] = f["format"]
            hits = [LANG_TOKEN.get(k, k) for k in LANG_ORDER if f.get(f"has_{k}_runtime") == "true"]
            ev = [f"has_{k}_runtime" for k in LANG_ORDER if f.get(f"has_{k}_runtime") == "true"]
            ev += [k for k in ("has_cpp_mangled_symbol",) if f.get(k) == "true" and not hits]
            lang, cands = f["language"], list(hits)
            lang = LANG_TOKEN.get(lang, lang)
            # symbol-string region (where a "sym" cue is decisive) + .comment banner
            symtxt, comment, has_symtab = d, b"", fmt != "elf"
            if fmt == "elf":
                lay = _elf_layout(d)
                parts = []
                for nm, o, n in (lay[1] if lay else []):
                    if nm in (".strtab", ".dynstr"):
                        parts.append(d[o:o + n])
                        has_symtab = has_symtab or nm == ".strtab"
                    elif nm == ".comment":
                        comment = d[o:o + min(n, 4096)]
                symtxt = b"\0".join(parts)
            weak = []
            for tok, tc, kind, cues in (_LANG_CUES if lang in ("c", "cpp") else ()):   # C-runtime languages only
                hay = symtxt if kind == "sym" and has_symtab else d
                if tok == "dart" and d[-8:] == _DART_TRAILER:   # dart2native: the cue is the appended snapshot's .dynstr
                    hay = d
                cue = next((c for c in cues if c in hay), None)
                strong = cue is not None
                if cue is None and hay is not d and len(d) <= (8 << 20):   # bounded string-literal (decoy) pass
                    cue = next((c for c in cues if c in d), None)
                if cue is None:
                    continue
                (cands if strong else weak).append(tok)
                ev.append(f"{tok}: {cue.decode('latin-1')!r}" + ("" if strong else " (string literal only)"))
                if strong and lang in ("c", "cpp") and (lang == "c" or tok != "pascal"):
                    lang, out["toolchain"] = tok, tc
            if fmt == "wasm":
                sec = d.find(b"\x09producers")
                body = d[sec:sec + 512] if sec >= 0 else b""
                for cue, tc, src in _WASM_PRODUCERS:
                    if cue in body:
                        out["toolchain"], out["source_language"] = tc, src
                        ev.append(f"producers section: {cue.decode()}")
                        break
            elif out["toolchain"] == "none":
                low = comment.lower()
                if lang in _TC_NATIVE:
                    out["toolchain"] = _TC_NATIVE[lang]
                elif lang == "d":
                    out["toolchain"] = "ldc" if b"ldc" in low or b"_D3ldc" in d else ("gdc" if b"gdc" in low else "dmd")
                elif b"clang" in low:
                    out["toolchain"] = "clang"
                elif b"gcc:" in low:
                    out["toolchain"] = "gcc"
                elif fmt == "pe" and b"Rich" in d[:0x400]:
                    out["toolchain"] = "msvc"
                elif fmt == "pe" and b"GCC: (" in d:
                    out["toolchain"] = "mingw"
                if comment:
                    ev.append(".comment " + comment.split(b"\0")[0][:60].decode("latin-1"))
            for t in weak:
                if t not in cands and t != lang:
                    out.setdefault("_weak", []).append(t)
            if lang not in cands:
                cands.insert(0, lang)
        amb = sorted({c for c in cands if c != lang} | set(out.pop("_weak", [])))
        out.update(language=lang, aliases=LANG_ALIASES.get(lang, [lang]), evidence=ev, candidates=cands,
                   ambiguous="true" if amb else "false", ambiguous_with=amb)
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def language_field(data, name="language"):
    """One language_of value; "none" when the input is no executable image / jar / class or the field is unknown."""
    try:
        return (language_of(data) or {}).get(name, "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- build provenance (who/what/when built it): GNU build-id, .comment banners, DWARF CU producer/language/comp_dir,
# PE TimeDateStamp / CodeView RSDS pdb / Rich header / linker version, Go + Rust toolchain versions.
_GO_BUILDINF = re.compile(rb"\xff Go buildinf:.{8,24}?(go1\.\d+(?:\.\d+)?(?:[a-z]+\d*)?)", re.S)
_RUSTC_PATH = re.compile(rb"/rustc/([0-9a-f]{40})/")
_VER = re.compile(r"(\d+\.\d+(?:\.\d+)?)")


def _elf_notes(data, e, secs_raw):
    """[(name, type, desc)] from SHT_NOTE sections (else PT_NOTE segments) of an ELF; bounded."""
    out = []
    for o, n in secs_raw:
        p, end = o, min(o + n, len(data), o + 65536)
        while p + 12 <= end:
            nsz, dsz, typ = struct.unpack_from(e + "III", data, p)
            q = p + 12 + ((nsz + 3) & ~3)
            if q + dsz > end or nsz > 256:
                break
            out.append((bytes(data[p + 12:p + 12 + nsz]).rstrip(b"\0"), typ, bytes(data[q:q + dsz])))
            p = q + ((dsz + 3) & ~3)
    return out


def _elf_prov(d, out):
    e = "<" if d[5] == 1 else ">"
    lay = _elf_layout(d)
    secs = lay[1] if lay else []
    if d[4] == 1:
        phoff, shoff = struct.unpack_from(e + "II", d, 28)
        _, phes, phn, shes, shn, _ = struct.unpack_from(e + "6H", d, 40)
        shf, phf = (e + "4xI8xII"), (e + "II8xI")   # sh_type .. sh_offset, sh_size ; p_type, p_offset, p_filesz
    else:
        phoff, shoff = struct.unpack_from(e + "QQ", d, 32)
        _, phes, phn, shes, shn, _ = struct.unpack_from(e + "6H", d, 52)
        shf, phf = (e + "4xI16xQQ"), (e + "I4xQ16xQ")
    notes = [(o, n) for t, o, n in (struct.unpack_from(shf, d, shoff + k * shes) for k in range(min(shn, 4096)))
             if t == 7] if shn and shoff + shn * shes <= len(d) else []
    if not notes and phn and phoff + phn * phes <= len(d):
        notes = [(o, n) for t, o, n in (struct.unpack_from(phf, d, phoff + k * phes) for k in range(min(phn, 256)))
                 if t == 4]
    bid = gid = "none"
    for nm, typ, desc in _elf_notes(d, e, notes):
        if nm == b"GNU" and typ == 3 and bid == "none" and desc:
            bid = desc.hex()
        elif nm == b"Go" and typ == 4 and gid == "none" and desc:
            gid = desc.decode("latin-1")
    out["build_id"], out["go_build_id"] = bid, gid
    names = {nm: (o, n) for nm, o, n in secs}
    cm = []
    if ".comment" in names:
        o, n = names[".comment"]
        for s in bytes(d[o:o + min(n, 65536)]).split(b"\0"):
            s = s.decode("utf-8", "replace").strip()
            if s and s not in cm:
                cm.append(s)
    out["compiler"] = cm[0] if cm else "none"
    out["comment_strings"] = cm
    has_dwarf = ".debug_info" in names and names[".debug_info"][1] > 0
    out["has_dwarf"] = "true" if has_dwarf else "false"
    if has_dwarf:
        _dwarf_prov(d, out)


def _dwarf_prov(d, out, max_cus=4000, budget=0.6):
    """First-CU DW_AT_producer / language / comp_dir / name (+ the distinct producers / languages over <= max_cus
    CUs) via pyelftools. A DWARF the library cannot walk leaves the first-CU fields "none"."""
    try:
        from elftools.elf.elffile import ELFFile
        from elftools.dwarf.enums import ENUM_DW_LANG
    except ImportError:
        return
    lang_name = {v: k for k, v in ENUM_DW_LANG.items()}
    prods, langs, t0 = [], [], time.time()
    try:
        dw = ELFFile(io.BytesIO(d)).get_dwarf_info(relocate_dwarf_sections=False)
        for i, cu in enumerate(dw.iter_CUs()):
            if i >= max_cus or time.time() - t0 > budget:
                break
            at = cu.get_top_DIE().attributes
            g = lambda k: at[k].value if k in at else None   # noqa: E731
            s = lambda v: v.decode("utf-8", "replace") if isinstance(v, bytes) else \
                ("none" if v is None else str(v))  # noqa: E731
            pr, ln = s(g("DW_AT_producer")), g("DW_AT_language")
            ln = lang_name.get(ln, f"0x{ln:x}") if isinstance(ln, int) else "none"
            if i == 0:
                out["dwarf_producer"], out["dwarf_language"] = pr, ln
                out["dwarf_language_num"] = str(ENUM_DW_LANG.get(ln, "none")) if ln != "none" else "none"
                out["dwarf_language_short"] = ln[len("DW_LANG_"):] if ln.startswith("DW_LANG_") else ln
                out["dwarf_comp_dir"], out["dwarf_name"] = s(g("DW_AT_comp_dir")), s(g("DW_AT_name"))
                m = _VER.search(pr)
                out["dwarf_producer_version"] = m.group(1) if m else "none"
                out["dwarf_version"] = str(cu.header.get("version", "none"))
            if pr != "none" and pr not in prods:
                prods.append(pr)
            if ln != "none" and ln not in langs:
                langs.append(ln)
    except Exception:   # noqa: BLE001 -- odd / truncated DWARF: keep what the first CUs gave
        pass
    out["dwarf_producers"], out["dwarf_languages"] = prods, langs


def _pe_prov(d, out):
    lay = _pe_layout(d)
    pe = int.from_bytes(d[0x3c:0x40], "little")
    ts = struct.unpack_from("<I", d, pe + 8)[0]
    out["timestamp"], out["timestamp_hex"] = str(ts), f"0x{ts:08x}"
    out["timestamp_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))
    out["timestamp_utc"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))
    opt = pe + 24
    out["linker_version"] = f"{d[opt + 2]}.{d[opt + 3]:02d}"
    pdb = {"pdb_path": "none", "pdb_name": "none", "pdb_guid": "none", "pdb_age": "none", "pdb_signature": "none"}
    if lay and len(lay[2]) > 6 and lay[2][6][0] and lay[2][6][1]:
        rva, size = lay[2][6]
        base = _pe_rva(lay[1], rva)
        for k in range(min(size // 28, 64) if base is not None else 0):
            typ, _, _, ptr = struct.unpack_from("<IIII", d, base + 28 * k + 12)
            if typ == 2 and d[ptr:ptr + 4] == b"RSDS":
                g = d[ptr + 4:ptr + 20]
                a, b, c = struct.unpack_from("<IHH", g)
                guid = f"{a:08x}-{b:04x}-{c:04x}-{g[8:10].hex()}-{g[10:16].hex()}"
                age = struct.unpack_from("<I", d, ptr + 20)[0]
                path = bytes(d[ptr + 24:ptr + 24 + 1024]).split(b"\0")[0].decode("utf-8", "replace")
                pdb = {"pdb_path": path, "pdb_name": re.split(r"[\\/]", path)[-1] or "none", "pdb_guid": guid,
                       "pdb_age": str(age), "pdb_signature": guid.replace("-", "").upper() + f"{age:X}"}
                break
    out.update(pdb)
    rich = []
    r = bytes(d[0x40:pe]).find(b"Rich")
    if r >= 0 and r % 4 == 0:
        r += 0x40
        key = struct.unpack_from("<I", d, r + 4)[0]
        p = r - 4
        while p >= 0x40 and struct.unpack_from("<I", d, p)[0] ^ key != 0x536e6144:   # "DanS"
            p -= 4
        if p >= 0x40:
            for q in range(p + 16, r, 8):
                cid, cnt = struct.unpack_from("<II", d, q)
                cid, cnt = cid ^ key, cnt ^ key
                rich.append([cid >> 16, cid & 0xffff, cnt])
            out["rich_xor_key"] = f"0x{key:08x}"
    out["has_rich"] = "true" if rich else "false"
    out.setdefault("rich_xor_key", "none")
    out["rich_entries"], out["rich_count"] = rich, str(len(rich))   # [prod_id, build, count] in header order


def provenance_facts(data):
    """Build-provenance facts of an ELF or PE image (bytes only; pyelftools for DWARF). Values are strings / lists;
    an absent field is "none" (not an ELF/PE at all -> None).
    ELF: build_id (lowercase hex of the NT_GNU_BUILD_ID desc, no 0x), go_build_id (Go note), compiler (first `.comment`
    string) + comment_strings, has_dwarf; first DWARF CU: dwarf_producer, dwarf_language (DW_LANG_* name),
    dwarf_language_short (C99/Ada95/..), dwarf_language_num, dwarf_comp_dir, dwarf_name, dwarf_version,
    dwarf_producer_version (first x.y[.z] of the producer), plus
    dwarf_producers / dwarf_languages (distinct, CU order).
    PE: timestamp (TimeDateStamp decimal) / timestamp_hex / timestamp_iso (UTC ...Z) / timestamp_utc, linker_version,
    CodeView RSDS pdb_path / pdb_name / pdb_guid / pdb_age / pdb_signature (symstore GUIDAGE), has_rich,
    rich_xor_key, rich_entries [[prod_id, build, count]], rich_count.
    Both: gcc_version, clang_version, rustc_version (+ rustc_commit from /rustc/<sha>/ paths), go_version
    (buildinfo), toolchain_version (go > rustc > clang > gcc > DWARF producer version)."""
    try:
        d = bytes(data) if not isinstance(data, (bytes, bytearray)) else data
        out = {}
        if d[:4] == b"\x7fELF" and len(d) >= 64 and d[4] in (1, 2) and d[5] in (1, 2):
            out["format"] = "elf"
            _elf_prov(d, out)
        elif d[:2] == b"MZ" and len(d) >= 0x40 and d[int.from_bytes(d[0x3c:0x40], "little"):][:4] == b"PE\0\0":
            out["format"] = "pe"
            _pe_prov(d, out)
        else:
            return None
        cm = out.get("comment_strings", [])
        gcc = next((s for s in cm if s.startswith("GCC:")), "")
        m = _VER.findall(gcc.rpartition(")")[2] or gcc)
        out["gcc_version"] = m[-1] if m else "none"
        m = next((_VER.search(s[s.find("clang version"):]) for s in cm if "clang version" in s), None)
        out["clang_version"] = m.group(1) if m else "none"
        m = next((_VER.search(s[s.find("rustc version"):]) for s in cm if "rustc version" in s), None)
        out["rustc_version"] = m.group(1) if m else "none"
        m = _RUSTC_PATH.search(d)
        out["rustc_commit"] = m.group(1).decode() if m else "none"
        m = _GO_BUILDINF.search(d)
        if not m and out.get("go_build_id", "none") != "none":
            m = re.search(rb"(go1\.\d+(?:\.\d+)?)", d)
        out["go_version"] = m.group(1).decode() if m else "none"
        out["toolchain_version"] = next((out[k] for k in ("go_version", "rustc_version", "clang_version",
                                                          "gcc_version", "dwarf_producer_version")
                                         if out.get(k, "none") != "none"), "none")
        for k in ("build_id", "go_build_id", "compiler", "dwarf_producer", "dwarf_language", "dwarf_language_short",
                  "dwarf_language_num", "dwarf_comp_dir", "dwarf_name", "dwarf_version", "dwarf_producer_version",
                  "timestamp", "timestamp_hex", "timestamp_iso", "timestamp_utc", "linker_version", "pdb_path",
                  "pdb_name", "pdb_guid", "pdb_age", "pdb_signature", "has_rich", "rich_xor_key", "rich_count",
                  "has_dwarf"):
            out.setdefault(k, "none")
        for k in ("comment_strings", "dwarf_producers", "dwarf_languages", "rich_entries"):
            out.setdefault(k, [])
        return out
    except Exception:   # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


_PROV_ALIASES = {"buildid": "build_id", "gnu_build_id": "build_id", "producer": "dwarf_producer",
                 "language": "dwarf_language", "comp_dir": "dwarf_comp_dir", "pdb": "pdb_path",
                 "time_date_stamp": "timestamp", "timedatestamp": "timestamp", "compile_time": "timestamp_iso",
                 "comment": "compiler", "rust_version": "rustc_version"}


def provenance_field(data, name):
    """One provenance_facts value; "none" when the input is no ELF/PE or the field is unknown (a decoy never raises)."""
    try:
        return (provenance_facts(data) or {}).get(_PROV_ALIASES.get(name, name), "none")
    except Exception:  # noqa: BLE001
        return "none"


# --- config DECODER locator (D17 "recover the reversible decoder"; speculative facts): from the HCFG hit's file offset
# -> blob VA -> code xrefs (RIP-relative disp32 / absolute imm32 to [VA, VA+stored len)) -> containing function (FUNC
# symbol, else the nearest endbr64 / push rbp;mov rbp,rsp) -> its loops (backward jcc) -> the data op between the
# loop's first byte load and its byte store: xor/add/sub/rol/ror imm (key), xor reg,reg + add imm (rolling-xor, key =
# start), xor reg,reg beside a 256-bound loop (rc4). loop_length = the cmp bound (+1 under jle/jbe). x86 / x86-64 only.

def _exec_map(data):
    """(bits, [(name, va, file_off, size, executable)], pie) for an x86/x86-64 ELF or PE, else None."""
    if data[:4] == b"\x7fELF" and data[5] == 1:
        b64 = data[4] == 2
        mach = struct.unpack_from("<H", data, 18)[0]
        if mach not in (3, 62):
            return None
        shoff = struct.unpack_from("<Q" if b64 else "<I", data, 40 if b64 else 32)[0]
        shes, shn, shstr = struct.unpack_from("<HHH", data, 58 if b64 else 46)
        fmt = "<IIQQQQ" if b64 else "<IIIIII"
        raw = [struct.unpack_from(fmt, data, shoff + k * shes) for k in range(min(shn, 4096))]
        names = b""
        if shstr < len(raw):
            names = data[raw[shstr][4]:raw[shstr][4] + raw[shstr][5]]
        secs = [(names[nm:names.find(b"\0", nm)].decode("latin-1"), va, off, size if ty != 8 else 0, bool(fl & 4))
                for nm, ty, fl, va, off, size in raw if va]
        return (64 if b64 else 32), secs, struct.unpack_from("<H", data, 16)[0] == 3
    pe = _pe_layout(data)
    if not pe:
        return None
    p = int.from_bytes(data[0x3c:0x40], "little")
    mach, opt = struct.unpack_from("<H", data, p + 4)[0], p + 24
    if mach not in (0x14c, 0x8664):
        return None
    b64 = struct.unpack_from("<H", data, opt)[0] == 0x20b
    base = struct.unpack_from("<Q", data, opt + 24)[0] if b64 else struct.unpack_from("<I", data, opt + 28)[0]
    nsec, optsz = struct.unpack_from("<H12xH", data, p + 6)
    secs = []
    for k, (n, va, vs, rp, rs) in enumerate(pe[1]):
        ch = struct.unpack_from("<I", data, opt + optsz + 40 * k + 36)[0]
        secs.append((n, base + va, rp, min(vs or rs, rs), bool(ch & 0x20000000)))
    return (64 if b64 else 32), secs, False


def _elf_funcs(data):
    """[(value, size, name)] FUNC symbols (symtab + dynsym), sorted; [] when stripped / not ELF."""
    if data[:4] != b"\x7fELF" or data[5] != 1:
        return []
    b64 = data[4] == 2
    shoff = struct.unpack_from("<Q" if b64 else "<I", data, 40 if b64 else 32)[0]
    shes, shn = struct.unpack_from("<HH", data, 58 if b64 else 46)
    sh = "<4xI8x8xQQIi8xQ" if b64 else "<4xI4x4xIIIi4xI"
    secs = [struct.unpack_from(sh, data, shoff + k * shes) for k in range(min(shn, 4096))]
    out = []
    for ty, off, size, link, _, ent in secs:
        if ty not in (2, 11) or not 0 <= link < len(secs):
            continue
        so, sn = secs[link][1], secs[link][2]
        ent = ent or (24 if b64 else 16)
        for k in range(min(size // ent, 400_000)):
            o = off + k * ent
            if b64:
                nm, info, val, sz = struct.unpack_from("<IB3xQQ", data, o)
            else:
                nm, val, sz, info = struct.unpack_from("<IIIB", data, o)
            if info & 0xF == 2 and val and nm < sn:
                z = data.find(b"\0", so + nm, so + sn)
                out.append((val, sz, bytes(data[so + nm:z if z >= 0 else so + sn]).decode("latin-1")))
    return sorted(set(out))


_JCC_LEN = {"jle": 1, "jbe": 1, "jng": 1, "jna": 1}   # bound + 1 (inclusive compare)


def _decoder_xrefs(data, bits, secs, pie, lo, hi, chunk=65536, cap=4096):
    """Code VAs (approximate instruction starts) whose RIP-relative disp32 (last in the instruction, mod=00 rm=101) /
    absolute imm32 lands in [lo, hi). Inside a 64 KB window of .text the disp's top 16 bits take 1-2 values, so the scan
    is a few bytes.find per window (no per-instruction Python loop over 15+ MB of code); capstone re-checks each."""
    out = []
    for _, va, off, size, ex in secs:
        if not ex or not size:
            continue
        end = min(off + size, len(data))
        if bits == 64:
            for a in range(off + 2, end - 4, chunk):
                b = min(a + chunk, end - 4)                 # disp starts p in [a, b)
                ea = va + (a - off) + 4                     # next-insn VA for a disp at file offset a
                dmin, dmax = lo - (ea + (b - a)), hi - 1 - ea
                for h in range(dmin >> 16, (dmax >> 16) + 1):
                    pat = (h & 0xFFFF).to_bytes(2, "little")
                    i = data.find(pat, a + 2, b + 2)
                    while i >= 0:
                        p = i - 2
                        if data[p - 1] & 0xC7 == 5:
                            t = va + (p - off) + 4 + int.from_bytes(data[p:p + 4], "little", signed=True)
                            if lo <= t < hi:
                                out.append(va + (p - off) - 3)
                        i = data.find(pat, i + 1, b + 2)
                if len(out) > cap:
                    break
        if not pie:
            for h in range(lo >> 8, ((hi - 1) >> 8) + 1):
                pat = (h & 0xFFFFFF).to_bytes(3, "little")
                i = data.find(pat, off + 1, end)
                while i >= 0 and len(out) < cap:
                    if lo <= int.from_bytes(data[i - 1:i + 3], "little") < hi:
                        out.append(va + i - 1 - off)
                    i = data.find(pat, i + 1, end)
    return sorted(set(out))


def _va_off(secs, va):
    for _, sva, off, size, _ in secs:
        if sva <= va < sva + size:
            return va - sva + off
    return None


def _guess_start(data, secs, va):
    """Nearest function prologue at/before code VA `va` (endbr64, else push rbp; mov rbp,rsp / push ebp; mov ebp,esp)."""
    o = _va_off(secs, va)
    if o is None:
        return None
    lo = max(0, o - 0x4000)
    win = data[lo:o + 1]
    cands = [win.rfind(b"\xf3\x0f\x1e\xfa"), win.rfind(b"\xf3\x0f\x1e\xfb"), win.rfind(b"\x55\x48\x89\xe5"),
             win.rfind(b"\x55\x89\xe5")]
    best = max(cands)
    if best < 0:
        return None
    if best >= 4 and win[best - 4:best] == b"\xf3\x0f\x1e\xfa":   # endbr64 heads the push rbp frame
        best -= 4
    return va - (o - (lo + best))


def _rfam(name):
    """x86 register family: al/ax/eax/rax -> ax, sil/esi/rsi -> si, r8b/r8d/r8 -> r8 ("" for none)."""
    name = name or ""
    if name[:1] == "r" and name[1:2].isdigit():
        return name.rstrip("bwd")
    n = name[1:] if len(name) == 3 and name[0] in "re" else name
    return {"al": "ax", "ah": "ax", "bl": "bx", "bh": "bx", "cl": "cx", "ch": "cx", "dl": "dx", "dh": "dx",
            "sil": "si", "dil": "di", "bpl": "bp", "spl": "sp"}.get(n, n)


def _decoder_loop(insns, start, end, refs):
    """(algorithm, key, immediates, loop_length) from the function's loops; None when no loop does a byte op."""
    import capstone
    import capstone.x86 as X
    byaddr = [i.address for i in insns]
    loops = []
    for k, i in enumerate(insns):
        if i.group(capstone.CS_GRP_JUMP) and i.operands and i.operands[0].type == X.X86_OP_IMM:
            t = i.operands[0].imm
            if start <= t <= i.address and i.mnemonic != "jmp":
                loops.append((t, k, i))
    bound256 = False
    best = None
    rank = {"rol": 0, "ror": 0, "xor": 1, "rolling-xor": 2, "add": 3, "sub": 3, "not": 4}
    for t, kj, jcc in loops:
        body = insns[bisect.bisect_left(byaddr, t):kj + 1]
        cmp_imm = None
        for i in body:   # the cmp/test feeding the backward jcc (an earlier `cmp x, 0xff` is no bound)
            if i.mnemonic in ("cmp", "test"):
                cmp_imm = i.operands[1].imm if i.mnemonic == "cmp" and len(i.operands) == 2 and \
                    i.operands[1].type == X.X86_OP_IMM else None
        if cmp_imm is not None and cmp_imm + _JCC_LEN.get(jcc.mnemonic, 0) == 256 and \
                jcc.mnemonic in ("jne", "jnz", "jb", "jl", "jbe", "jle", "jna", "jng") and \
                sum(len(i.operands) == 2 and i.operands[0].type == X.X86_OP_MEM and i.operands[0].size == 1
                    for i in body if i.mnemonic == "mov") >= 2:   # the KSA swap stores S[i] and S[j]
            bound256 = True
        # the data window: first byte-sized memory load .. the next byte-sized memory store
        win, st = [], None
        for i in body:
            ops = i.operands
            if st is None:
                if len(ops) == 2 and ops[1].type == X.X86_OP_MEM and ops[1].size == 1 and \
                        i.mnemonic in ("movzx", "movsx", "mov"):
                    st = i
                continue
            if len(ops) == 2 and ops[0].type == X.X86_OP_MEM and ops[0].size == 1 and i.mnemonic == "mov":
                break
            win.append(i)
        if st is None:
            continue
        found, imms = None, []
        xvar = add = kadd = None
        data_r = {_rfam(st.reg_name(st.operands[0].reg))}   # registers holding the loaded byte (simple data flow)
        for i in win:
            ops, m = i.operands, i.mnemonic
            d0 = _rfam(i.reg_name(ops[0].reg)) if ops and ops[0].type == X.X86_OP_REG else None
            r1 = _rfam(i.reg_name(ops[1].reg)) if len(ops) == 2 and ops[1].type == X.X86_OP_REG else None
            if d0 is None:
                continue
            if m in ("mov", "movzx", "movsx", "lea") and len(ops) == 2:
                if r1 in data_r or (m == "lea" and _rfam(i.reg_name(ops[1].mem.base)) in data_r):
                    data_r.add(d0)
                else:
                    data_r.discard(d0)
            if d0 not in data_r:
                if m in ("add", "sub") and len(ops) == 2 and ops[1].type == X.X86_OP_IMM:
                    kadd = kadd or (m, ops[1].imm)   # key-register update (rolling key start)
                continue
            if m in ("rol", "ror") and len(ops) == 2 and ops[1].type == X.X86_OP_IMM:
                found = found or (m, ops[1].imm & 7)
                imms.append(ops[1].imm)
            elif m == "xor" and len(ops) == 2 and ops[1].type == X.X86_OP_IMM and ops[1].imm & 0xFF:
                found = found if found and rank[found[0]] <= 1 else ("xor", ops[1].imm & 0xFF)
                imms.append(ops[1].imm & 0xFFFFFFFF)
            elif m == "xor" and len(ops) == 2 and ops[1].type in (X.X86_OP_REG, X.X86_OP_MEM) and r1 != d0:
                xvar = True
                if kadd:
                    imms.append(kadd[1] & 0xFFFFFFFF)
            elif m in ("add", "sub") and len(ops) == 2 and ops[1].type == X.X86_OP_IMM:
                add = add or (m, ops[1].imm)
                imms.append(ops[1].imm & 0xFFFFFFFF)
            elif m == "lea" and ops[1].type == X.X86_OP_MEM and ops[1].mem.index == 0 and ops[1].mem.disp and \
                    _rfam(i.reg_name(ops[1].mem.base)) in data_r:
                d = ops[1].mem.disp
                add = add or (("sub", -d) if d < 0 else ("add", d))
                imms.append(abs(d))
            elif m == "not":
                found = found or ("not", 0xFF)
        if not found and xvar:
            found = ("rolling-xor", kadd[1] & 0xFF) if kadd else ("xor-var", None)
        if not found and add:
            found = (add[0], add[1] & 0xFF)
        if not found:
            continue
        n = None
        if cmp_imm is not None and 0 < cmp_imm < 1 << 24:
            n = cmp_imm + _JCC_LEN.get(jcc.mnemonic, 0)
        cand = (rank.get(found[0], 5), found[0], found[1], imms, n)
        if best is None or cand[0] < best[0]:
            best = cand
    if best is None:
        return None
    alg = best[1]
    if alg == "xor-var":   # xor with a register / memory key (the header key byte, a key table): `xor` speculative
        alg = "rc4" if bound256 else "xor"
    return alg, best[2], best[3], best[4]


def decoder_facts(data, offset=None, hit=None):
    """Speculative facts about the routine that decodes the stored HCFG blob: {blob_va, xrefs (code VAs), function
    (FUNC symbol, "none" when stripped), function_va, algorithm (xor/add/sub/rol/ror/not/rolling-xor/rc4 or
    "none" = referenced but no decode loop), key (the loop's immediate), immediates, loop_length, header_key,
    key_equals_header ("true"/"false"/"none")}. `hit` (an HcfgHit) or `offset` (file offset of the stored blob) --
    default hcfg_find(data). None when not an x86 ELF/PE, no blob, or no code reference."""
    try:
        import capstone
        import capstone.x86 as X
        data = bytes(data)
        mp = _exec_map(data)
        if not mp:
            return None
        bits, secs, pie = mp
        if hit is None and offset is None:
            hit = hcfg_find(data)
        if hit is not None:
            offset = hit.offset
        if offset is None:
            return None
        bva = next((va + offset - off for _, va, off, size, _ in secs if off <= offset < off + size and size), None)
        if bva is None:
            return None
        hi = bva + (12 + hit.length if hit is not None else 64)
        lo = bva - 32   # Swift large-string objects point 0x20 before the bytes (lea rsi,[blob-0x10] + flags)
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64 if bits == 64 else capstone.CS_MODE_32)
        md.detail = True
        funcs = _elf_funcs(data)
        fstarts = [f[0] for f in funcs]
        seen, refs, out = set(), [], None
        for xva in _decoder_xrefs(data, bits, secs, pie, lo, hi):
            k = bisect.bisect_right(fstarts, xva) - 1
            if k >= 0 and funcs[k][0] <= xva < funcs[k][0] + max(funcs[k][1], 1):
                start, size, name = funcs[k]
            else:
                start, size, name = _guess_start(data, secs, xva), 0x2000, "none"
                if start is None:
                    continue
            if start in seen:
                continue
            o = _va_off(secs, start)
            if o is None:
                continue
            insns, real, fwd = [], [], start
            for i in md.disasm(data[o:o + min(size, 0x4000)], start):
                insns.append(i)
                for op in i.operands:
                    t = None
                    if op.type == X.X86_OP_MEM:
                        t = op.mem.disp + (i.address + i.size if op.mem.base == X.X86_REG_RIP else 0)
                    elif op.type == X.X86_OP_IMM:
                        t = op.imm
                        if i.group(capstone.CS_GRP_JUMP) and t > fwd:
                            fwd = t
                    if t is not None and lo <= t < hi and not i.group(capstone.CS_GRP_JUMP):
                        real.append(i.address)
                if name == "none" and i.mnemonic in ("ret", "jmp") and i.address >= max(xva, fwd) and \
                        (i.mnemonic == "ret" or i.operands[0].type != X.X86_OP_IMM or
                         not start <= i.operands[0].imm < i.address):
                    break
                if len(insns) > 8000:
                    break
            if not real:
                continue
            seen.add(start)
            refs += real
            lp = _decoder_loop(insns, start, insns[-1].address + 1, real) if out is None or \
                out["algorithm"] == "none" else None
            if out is None or lp:
                out = {"blob_va": bva, "function": name, "function_va": start, "algorithm": "none", "key": "none",
                       "immediates": [], "loop_length": "none"}
                if lp:
                    out.update(algorithm=lp[0], key=lp[1] if lp[1] is not None else "none", immediates=lp[2],
                               loop_length=lp[3] if lp[3] is not None else "none")
            if len(seen) > 64:
                break
        if out is None:
            return None
        out["xrefs"] = sorted(set(refs))
        out["header_key"] = hit.key if hit is not None else "none"
        out["key_equals_header"] = ("true" if out["key"] == hit.key else "false") \
            if hit is not None and isinstance(out["key"], int) else "none"
        out["speculative"] = True
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def decoder_field(data, name, **kw):
    """One decoder_facts value as an answer string (VAs / key as 0x-hex, loop_length decimal); "none" when absent."""
    try:
        f = decoder_facts(data, **kw)
        v = (f or {}).get(name, "none")
        if isinstance(v, bool):
            return str(v).lower()
        if isinstance(v, int) and name != "loop_length":
            return hex(v)
        return v if isinstance(v, (str, list)) else str(v)
    except Exception:  # noqa: BLE001
        return "none"


# --- API HASHING resolver (speculative facts): imports resolved by a 32-bit name hash instead of by name. Precomputed
# tables of common libc / kernel32 / ntdll / user32 / advapi32 / ws2_32 / wininet export names under the usual shellcode
# / loader algorithms; hits are imm32s in executable sections (x86: capstone-confirmed instruction immediates, any
# other arch: raw LE dwords) plus 4-aligned dwords of the read-only / data sections (hash tables). The algorithm is the
# variant with the most distinct names hit; resolved_apis = its names in file (code) order, first occurrence.

_APIH_NAMES = (
    # libc
    "getenv setenv putenv printf fprintf sprintf snprintf vprintf puts fputs fgets gets scanf sscanf fopen fclose "
    "fread fwrite fseek ftell fflush open close read write lseek stat fstat unlink rename mkdir rmdir chdir getcwd "
    "malloc calloc realloc free memcpy memmove memset memcmp strlen strcpy strncpy strcat strcmp strncmp strchr strrchr "
    "strstr strdup strtok strtol strtoul atoi atol exit _exit abort atexit system popen pclose fork vfork execve execv "
    "execvp execl execlp waitpid wait kill signal sigaction raise getpid getppid getuid geteuid getgid setuid setgid "
    "sleep usleep nanosleep time gettimeofday clock_gettime localtime gmtime strftime rand srand random srandom "
    "socket connect bind listen accept send recv sendto recvfrom setsockopt getsockopt shutdown gethostbyname "
    "getaddrinfo freeaddrinfo inet_addr inet_pton inet_ntoa inet_ntop htons htonl ntohs ntohl select poll ioctl fcntl "
    "mmap munmap mprotect ptrace prctl dup dup2 pipe opendir readdir closedir dlopen dlsym dlclose dlerror "
    "pthread_create pthread_join pthread_mutex_lock pthread_mutex_unlock syscall uname chmod chown access readlink "
    "isatty getline perror strerror qsort bsearch toupper tolower "
    # kernel32 / kernelbase
    "LoadLibraryA LoadLibraryW LoadLibraryExA LoadLibraryExW GetProcAddress GetModuleHandleA GetModuleHandleW "
    "GetModuleFileNameA GetModuleFileNameW FreeLibrary ExitProcess ExitThread TerminateProcess WinExec CreateProcessA "
    "CreateProcessW OpenProcess GetCurrentProcess GetCurrentProcessId GetCurrentThread GetCurrentThreadId "
    "VirtualAlloc VirtualAllocEx VirtualFree VirtualProtect VirtualProtectEx VirtualQuery WriteProcessMemory "
    "ReadProcessMemory CreateRemoteThread CreateThread ResumeThread SuspendThread OpenThread GetThreadContext "
    "SetThreadContext QueueUserAPC WaitForSingleObject WaitForMultipleObjects Sleep SleepEx CloseHandle CreateFileA "
    "CreateFileW ReadFile WriteFile DeleteFileA DeleteFileW CopyFileA CopyFileW MoveFileA MoveFileW GetFileSize "
    "SetFilePointer FindFirstFileA FindFirstFileW FindNextFileA FindNextFileW FindClose CreateDirectoryA "
    "CreateDirectoryW GetTempPathA GetTempPathW GetTempFileNameA GetWindowsDirectoryA GetSystemDirectoryA "
    "CreateFileMappingA CreateFileMappingW MapViewOfFile UnmapViewOfFile HeapAlloc HeapFree HeapCreate GetProcessHeap "
    "LocalAlloc LocalFree GlobalAlloc GlobalFree CreateMutexA CreateMutexW OpenMutexA ReleaseMutex CreateEventA "
    "SetEvent GetLastError SetLastError GetTickCount GetTickCount64 QueryPerformanceCounter GetSystemTime "
    "GetLocalTime GetSystemInfo GetVersionExA GetComputerNameA GetComputerNameW GetEnvironmentVariableA "
    "GetEnvironmentVariableW ExpandEnvironmentStringsA GetCommandLineA GetCommandLineW IsDebuggerPresent "
    "CheckRemoteDebuggerPresent OutputDebugStringA CreateToolhelp32Snapshot Process32First Process32FirstW "
    "Process32Next Process32NextW Module32First Module32Next Thread32First Thread32Next lstrlenA lstrlenW lstrcpyA "
    "lstrcmpA lstrcmpiA MultiByteToWideChar WideCharToMultiByte FindResourceA LoadResource LockResource "
    "SizeofResource DeviceIoControl CreatePipe PeekNamedPipe CreateNamedPipeA ConnectNamedPipe SetHandleInformation "
    "GetStartupInfoA FlushInstructionCache AddVectoredExceptionHandler SetUnhandledExceptionFilter "
    "GetNativeSystemInfo IsWow64Process Wow64DisableWow64FsRedirection VirtualAllocExNuma "
    # ntdll
    "NtAllocateVirtualMemory NtProtectVirtualMemory NtWriteVirtualMemory NtReadVirtualMemory NtFreeVirtualMemory "
    "NtCreateThreadEx NtCreateThread NtQueueApcThread NtResumeThread NtOpenProcess NtClose NtCreateSection "
    "NtMapViewOfSection NtUnmapViewOfSection NtQueryInformationProcess NtQuerySystemInformation NtSetInformationThread "
    "NtDelayExecution NtWaitForSingleObject NtCreateFile NtReadFile NtWriteFile NtTerminateProcess NtContinue "
    "NtTestAlert NtGetContextThread NtSetContextThread NtQueryVirtualMemory NtOpenThread NtSuspendThread "
    "ZwAllocateVirtualMemory ZwProtectVirtualMemory ZwWriteVirtualMemory ZwCreateThreadEx ZwMapViewOfSection "
    "ZwUnmapViewOfSection ZwQueryInformationProcess RtlMoveMemory RtlCopyMemory RtlZeroMemory RtlFillMemory "
    "RtlCreateUserThread RtlExitUserThread RtlGetVersion RtlInitUnicodeString RtlAdjustPrivilege "
    "RtlDecompressBuffer LdrLoadDll LdrGetProcedureAddress LdrGetDllHandle EtwEventWrite "
    # user32 / advapi32 / shell32 / ws2_32 / wininet / urlmon / msvcrt
    "MessageBoxA MessageBoxW GetAsyncKeyState GetKeyState SetWindowsHookExA SetWindowsHookExW UnhookWindowsHookEx "
    "CallNextHookEx GetForegroundWindow GetWindowTextA FindWindowA ShowWindow GetDC EnumWindows "
    "RegOpenKeyExA RegOpenKeyExW RegSetValueExA RegSetValueExW RegQueryValueExA RegCreateKeyExA RegCloseKey "
    "RegDeleteValueA OpenProcessToken AdjustTokenPrivileges LookupPrivilegeValueA GetUserNameA GetUserNameW "
    "CryptAcquireContextA CryptCreateHash CryptHashData CryptDeriveKey CryptDecrypt CryptEncrypt CryptReleaseContext "
    "OpenSCManagerA CreateServiceA StartServiceA ShellExecuteA ShellExecuteW ShellExecuteExA "
    "WSAStartup WSACleanup WSASocketA WSASocketW WSAConnect WSAGetLastError closesocket ioctlsocket "
    "InternetOpenA InternetOpenW InternetOpenUrlA InternetOpenUrlW InternetConnectA HttpOpenRequestA "
    "HttpSendRequestA InternetReadFile InternetCloseHandle URLDownloadToFileA URLDownloadToFileW "
    "CoInitialize CoInitializeEx CoCreateInstance"
).split()
_APIH_MODULES = ("kernel32.dll", "ntdll.dll", "kernelbase.dll", "user32.dll", "advapi32.dll", "ws2_32.dll",
                 "wininet.dll", "shell32.dll", "msvcrt.dll", "urlmon.dll")
_M32 = 0xFFFFFFFF


def _ror32(v, r):
    return ((v >> r) | (v << (32 - r))) & _M32


def _h_ror13(s):
    h = 0
    for c in s:
        h = (_ror32(h, 13) + c) & _M32
    return h


def _h_djb2(s, seed=5381):
    h = seed
    for c in s:
        h = (h * 33 + c) & _M32
    return h


def _h_djb2x(s, seed=5381):
    h = seed
    for c in s:
        h = ((h * 33) ^ c) & _M32
    return h


def _h_sdbm(s):
    h = 0
    for c in s:
        h = (c + (h << 6) + (h << 16) - h) & _M32
    return h


def _h_fnv1a(s, seed=0x811C9DC5):
    h = seed
    for c in s:
        h = ((h ^ c) * 0x01000193) & _M32
    return h


def _h_fnv1(s, seed=0x811C9DC5):
    h = seed
    for c in s:
        h = ((h * 0x01000193) ^ c) & _M32
    return h


def _h_joaat(s):
    h = 0
    for c in s:
        h = (h + c) & _M32
        h = (h + (h << 10)) & _M32
        h ^= h >> 6
    h = (h + (h << 3)) & _M32
    h ^= h >> 11
    return (h + (h << 15)) & _M32


def _h_murmur3(s, seed=0):
    h, n = seed, len(s)
    for k in range(0, n - n % 4, 4):
        x = (int.from_bytes(s[k:k + 4], "little") * 0xCC9E2D51) & _M32
        h ^= (_ror32(x, 17) * 0x1B873593) & _M32
        h = (_ror32(h, 19) * 5 + 0xE6546B64) & _M32
    t = s[n - n % 4:]
    if t:
        x = (int.from_bytes(t, "little") * 0xCC9E2D51) & _M32
        h ^= (_ror32(x, 17) * 0x1B873593) & _M32
    h ^= n
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & _M32
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & _M32
    return h ^ (h >> 16)


def _msf_mod(m):
    """Metasploit block_api module hash: ror13 over the UTF-16LE module name (bytes upper-cased) + its null wchar."""
    return _h_ror13(m.upper().encode("utf-16-le") + b"\0\0")


# (algorithm token, seed, variant, fn(name bytes) -> hash). variant: "" plain name, "null" incl. the terminator,
# "lower"/"upper" case-folded name, "msf_block_api" module hash + ror13(name incl null) (handled in _apih_table).
_APIH_ALGOS = (
    ("ror13", 0, "", _h_ror13), ("ror13", 0, "null", lambda s: _h_ror13(s + b"\0")),
    ("ror13", 0, "upper", lambda s: _h_ror13(s.upper())), ("ror13", 0, "lower", lambda s: _h_ror13(s.lower())),
    ("djb2", 5381, "", _h_djb2), ("djb2", 5381, "lower", lambda s: _h_djb2(s.lower())),
    ("djb2", 5381, "upper", lambda s: _h_djb2(s.upper())), ("djb2a", 5381, "", _h_djb2x),
    ("sdbm", 0, "", _h_sdbm), ("fnv1a", 0x811C9DC5, "", _h_fnv1a),
    ("fnv1a", 0x811C9DC5, "lower", lambda s: _h_fnv1a(s.lower())), ("fnv1", 0x811C9DC5, "", _h_fnv1),
    ("crc32", 0xFFFFFFFF, "", zlib.crc32), ("crc32", 0xFFFFFFFF, "lower", lambda s: zlib.crc32(s.lower())),
    ("crc32", 0xFFFFFFFF, "noxor", lambda s: zlib.crc32(s) ^ _M32),
    ("murmur3", 0, "", _h_murmur3), ("jenkins_oaat", 0, "", _h_joaat),
)
# implementation constants: corroborate the algorithm even when no table name hits
_APIH_CONSTS = {5381: "djb2", 0x811C9DC5: "fnv1a", 0x01000193: "fnv1a", 0xEDB88320: "crc32", 0x04C11DB7: "crc32",
                0xCC9E2D51: "murmur3", 0x1B873593: "murmur3", 0xE6546B64: "murmur3", 0x85EBCA6B: "murmur3"}
_APIH_TABLE = None
_BIG_HOST = struct.pack("=I", 1) != struct.pack("<I", 1)
_APIH_SKIP = re.compile(r"^\.(gnu\.hash|hash|dynsym|dynstr|symtab|strtab|shstrtab|rela?\b.*|eh_frame.*|gcc_except"
                        r"|note.*|debug.*|gnu\.version.*|interp|dynamic|got.*|plt.*|reloc|pdata|xdata|idata|edata)",
                        re.I)
HCFG_APIH_MAX = int(os.environ.get("HCTF_APIH_MAX", str(12 << 20)))   # bytes scanned (~40 ms / MiB of code)


def _apih_table():
    """{hash: [(algo, seed, variant, api)]} over every name x algorithm (+ msf module+function sums); built once."""
    global _APIH_TABLE
    if _APIH_TABLE is None:
        t = {}
        names = [n.encode() for n in _APIH_NAMES]
        for algo, seed, var, fn in _APIH_ALGOS:
            for n in names:
                t.setdefault(fn(n), []).append((algo, seed, var, n.decode()))
        mods = [(m, _msf_mod(m)) for m in _APIH_MODULES]
        for n in names:
            fh = _h_ror13(n + b"\0")
            for m, mh in mods:
                t.setdefault((mh + fh) & _M32, []).append(("ror13", 0, "msf_block_api", m + "!" + n.decode()))
        t.pop(0, None)
        _APIH_TABLE = t
    return _APIH_TABLE


def _apih_regions(data):
    """[(file_off, size, executable, va, bits_or_None)] to scan: x86 ELF/PE sections via _exec_map, other ELF/PE/Mach-O
    via lief-free fallbacks (whole file as data) -- None when the input is not a native image."""
    em = _exec_map(data)
    if em:
        bits, secs, _pie = em
        out = [(off, size, ex, va, bits) for name, va, off, size, ex in secs
               if size and off and off + size <= len(data) and not _APIH_SKIP.match(name or "")]
        return out
    if data[:4] == b"\x7fELF" or data[:2] == b"MZ" or data[:4] in _MO_MAGIC or data[:4] == b"\xca\xfe\xba\xbe":
        return [(0, len(data), False, 0, None)]
    return None


def _apih_imm_ok(md, data, p, val, lo):
    """Does an x86 instruction ending at p+4 (or with its imm32 at p) carry `val` as an immediate operand?"""
    for back in range(1, 11):
        s = p - back
        if s < lo:
            break
        try:
            for ins in md.disasm(bytes(data[s:p + 8]), 0, 1):
                if ins.size >= back + 4 and any(op.type == 2 and op.imm & _M32 == val for op in ins.operands):
                    return True
        except Exception:  # noqa: BLE001
            pass
    return False


def api_hash_facts(data, max_bytes=None):
    """Hash-resolved imports: {"algorithm", "variant", "seed", "seed_hex", "resolved_apis", "hashes", "hash_count",
    "api_count", "offsets", "candidates", "algorithm_constants", "speculative"}; resolved_apis / hashes in file (code)
    order, first occurrence. {"algorithm": "none", ...} when a native image carries no known hash; None when the input
    is not a native image."""
    try:
        regs = _apih_regions(data)
        if regs is None:
            return None
        table = _apih_table()
        keys = set(table)
        budget = HCFG_APIH_MAX if max_bytes is None else max_bytes
        mv = memoryview(data)
        hits, consts = [], set()   # (file_off, value, in_code)
        for off, size, ex, va, bits in sorted(regs, key=lambda r: not r[2]):
            size = min(size, budget)
            if size < 4:
                continue
            budget -= size
            buf = bytes(mv[off:off + size])
            for a in (range(4) if ex else (0,)):
                n = (size - a) // 4
                arr = array.array("I", buf[a:a + 4 * n])
                if _BIG_HOST:
                    arr.byteswap()
                for v in keys.intersection(arr):
                    pv = struct.pack("<I", v)
                    q = buf.find(pv)
                    while q >= 0:
                        if ex or q % 4 == 0:
                            hits.append((off + q, v, ex))
                        q = buf.find(pv, q + 1)
                if ex:
                    consts.update(_APIH_CONSTS[c] for c in set(_APIH_CONSTS).intersection(arr))
            if budget <= 0:
                break
        md = None
        if hits and regs and regs[0][4] in (32, 64):
            from capstone import CS_ARCH_X86, CS_MODE_32, CS_MODE_64, Cs
            md = Cs(CS_ARCH_X86, CS_MODE_64 if regs[0][4] == 64 else CS_MODE_32)
            md.detail = True
        good = []
        for p, v, ex in sorted(set(hits)):
            if ex and md is not None:
                lo = next((o for o, s, e, _, _ in regs if o <= p < o + s), 0)
                if not _apih_imm_ok(md, mv, p, v, lo):
                    continue
            good.append((p, v))
        score = {}
        for p, v in good:
            for algo, seed, var, api in table[v]:
                score.setdefault((algo, seed, var), {}).setdefault(api, (p, v))
        out = {"algorithm": "none", "variant": "none", "seed": "none", "seed_hex": "none", "resolved_apis": [],
               "hashes": [], "hash_count": 0, "api_count": 0, "offsets": [], "candidates": [],
               "algorithm_constants": sorted(consts), "speculative": True}
        order = [(a, s, vr) for a, s, vr, _ in _APIH_ALGOS] + [("ror13", 0, "msf_block_api")]

        def cluster(apis):   # most distinct names (A/W siblings count once) within one 64 KiB span
            first = {}
            for api, (p, _) in apis.items():
                base = api[:-1] if api[-1:] in "AW" and api[-2:-1].islower() else api
                first[base] = min(p, first.get(base, p))
            ps = sorted(first.values())
            return max(bisect.bisect_right(ps, p + 0xFFFF) - k for k, p in enumerate(ps))

        ranked = sorted(score.items(), key=lambda kv: (-cluster(kv[1]), -len(kv[1]), -(kv[0][0] in consts),
                                                       order.index(kv[0]) if kv[0] in order else 99))
        if not ranked:
            return out
        (algo, seed, var), apis = ranked[0]
        # a lone dword is noise (seen: 1-hit fnv1a/crc32 in Qt / Go images); big images need a bigger cluster, one
        # fewer when the algorithm's own constants corroborate it, one more for the 10x msf key space
        need = 2 if len(data) <= (8 << 20) else 3
        if algo in consts:
            need = 2
        if var == "msf_block_api" and len(data) >= (1 << 20):
            need += 1
        if cluster(apis) < need:
            return out
        seq = sorted(apis.items(), key=lambda kv: kv[1][0])
        out.update(algorithm=algo, variant=var or "plain", seed=str(seed), seed_hex=hex(seed),
                   resolved_apis=[a for a, _ in seq], hashes=[f"0x{v:08x}" for _, (_, v) in seq],
                   offsets=[p for _, (p, _) in seq], hash_count=len({v for _, (_, v) in seq}), api_count=len(seq),
                   candidates=[f"{a}/{vr or 'plain'}:{len(x)}" for (a, _, vr), x in ranked[:5]])
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def api_hash_field(data, name):
    """One api_hash_facts value as an answer string (lists comma-joined); "none" when absent / not a native image."""
    try:
        f = api_hash_facts(data)
        v = (f or {}).get(name, "none")
        if isinstance(v, list):
            return ",".join(str(x) for x in v) if v else "none"
        return str(v)
    except Exception:  # noqa: BLE001
        return "none"


# --- per-string encryption (D17+ escalation of "encoded configuration"): every string xor/add'ed on its own and
# decoded by one shared routine dstr(ptr, len, key); the ciphertext lives in .rodata or is built on the stack.
STRDEC_MAX_S = float(os.environ.get("HCTF_STRDEC_MAX_S", "0.6"))   # linear-sweep budget (disasm_lite, x86-64 only)
_SD_ARGS = ("di", "si", "dx", "cx", "r8", "r9")                  # SysV + Win64 integer argument registers
_SD_VOLATILE = ("ax", "cx", "dx", "si", "di", "r8", "r9", "r10", "r11")
_SD_MEM = re.compile(r"(?:(byte|word|dword|qword|xmmword) ptr )?\[(\w+)(?: ([+-]) (0x[0-9a-f]+|\d+))?\]$")
_SD_W = {"byte": 1, "word": 2, "dword": 4, "qword": 8, "xmmword": 16}
_SD_OPS = {"xor": lambda c, k: c ^ k, "sub": lambda c, k: (c - k) & 255, "add": lambda c, k: (c + k) & 255}
_SD_PRINT = frozenset(range(0x20, 0x7f))
_SD_SCORE = [(1.0 if chr(c).isalnum() else 0.5 if chr(c) in " ./:\\-_()@;,%" else 0.0) if c in _SD_PRINT else -5.0
             for c in range(256)]   # text-likeness: a decode must read more like a config string than its ciphertext


def _sd_int(s):
    try:
        return int(s, 0)
    except ValueError:
        return None


def _sd_calls(data, secs, deadline):
    """[(call_va, target_va, {argreg: value})] from a register/stack-tracking linear sweep of the executable sections.
    value: ("imm", n) | ("ptr", va) | ("buf", bytes captured from the tracked stack slot the register points at)."""
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    out = []

    def rd(va, n):
        o = _va_off(secs, va)
        return data[o:o + n] if o is not None and n > 0 else b""

    for _, va, off, size, ex in secs:
        if not ex or not size:
            continue
        regs, stk = {}, {}
        for a, sz, mn, ops in md.disasm_lite(data[off:min(off + size, len(data))], va):
            if time.time() > deadline:
                return out
            if mn in ("ret", "jmp", "hlt", "endbr64", "ud2", "int3"):
                regs, stk = {}, {}
                continue
            dst, _, src = ops.partition(", ")
            if mn == "call":
                t = _sd_int(dst)
                if t is not None:
                    args = {}
                    for r in _SD_ARGS:
                        v = regs.get(r)
                        if v and v[0] == "stk":
                            m = stk.get(v[1], {})
                            buf = bytearray()
                            while len(buf) < 1024 and v[2] + len(buf) in m:
                                buf.append(m[v[2] + len(buf)])
                            v = ("buf", bytes(buf))
                        if v:
                            args[r] = v
                    out.append((a, t, args))
                for r in _SD_VOLATILE:
                    regs.pop(r, None)
                continue
            d = _rfam(dst)
            mm = _SD_MEM.match(src) if src else None
            if mn == "lea" and mm:
                base, disp = mm.group(2), _sd_int(mm.group(4) or "0") or 0
                disp = -disp if mm.group(3) == "-" else disp
                if base == "rip":
                    regs[d] = ("ptr", a + sz + disp)
                elif base in ("rsp", "rbp"):
                    regs[d] = ("stk", base, disp)
                else:
                    regs.pop(d, None)
                continue
            dm = _SD_MEM.match(dst)
            if dm and mn in ("mov", "movaps", "movups", "movdqa", "movdqu"):
                base, disp = dm.group(2), _sd_int(dm.group(4) or "0") or 0
                disp = -disp if dm.group(3) == "-" else disp
                w = _SD_W.get(dm.group(1) or "qword", 8)
                v = _sd_int(src)
                if v is not None:
                    raw = (v & ((1 << 8 * w) - 1)).to_bytes(w, "little")
                else:
                    rv = regs.get(_rfam(src))
                    raw = rv[1][:w] if rv and rv[0] == "bytes" else \
                        (rv[1] & ((1 << 8 * w) - 1)).to_bytes(w, "little") if rv and rv[0] == "imm" else None
                if base in ("rsp", "rbp"):
                    m = stk.setdefault(base, {})
                    for k in range(w):
                        if raw is not None and k < len(raw):
                            m[disp + k] = raw[k]
                        else:
                            m.pop(disp + k, None)
                continue
            if mn in ("mov", "movabs"):
                v = _sd_int(src)
                if v is not None:
                    regs[d] = ("imm", v)
                elif mm and mm.group(2) == "rip" and mm.group(1) in ("qword", "dword"):
                    w = _SD_W[mm.group(1)]
                    b = rd(a + sz + (_sd_int(mm.group(4) or "0") or 0) * (-1 if mm.group(3) == "-" else 1), w)
                    regs[d] = ("imm", int.from_bytes(b, "little")) if len(b) == w else None
                elif _rfam(src) in regs and not mm:
                    regs[d] = regs[_rfam(src)]
                else:
                    regs.pop(d, None)
                continue
            if mn in ("movdqa", "movdqu", "movaps", "movups") and mm and mm.group(2) == "rip":
                b = rd(a + sz + (_sd_int(mm.group(4) or "0") or 0) * (-1 if mm.group(3) == "-" else 1), 16)
                regs[d] = ("bytes", b) if len(b) == 16 else None
                continue
            if mn == "xor" and dst == src:
                regs[d] = ("imm", 0)
                continue
            if dst and not dm:
                regs.pop(d, None)
    return out


def string_decrypt_facts(data):
    """Speculative: strings encrypted ONE BY ONE and decoded by a shared routine called as f(ptr, len, key) (ptr into
    .rodata/.data or a stack-built array; any SysV/Win64 argument order). The routine's (ptr,len,key) triples are read
    off its call sites by a register/stack-tracking capstone sweep; the decode op (xor / sub / add of the 1-byte key)
    is the one turning every non-printable ciphertext into printable text. {decoder_va, decoder, algorithm, strings,
    keys, lengths, call_sites, storage, count} plus regex buckets (urls, domains, ips, mutexes, campaign_ids,
    registry_keys, paths, user_agents). None when not an x86-64 ELF/PE or no such routine."""
    try:
        data = bytes(data)
        mp = _exec_map(data)
        if not mp or mp[0] != 64:
            return None
        _, secs, _ = mp
        calls = _sd_calls(data, secs, time.time() + STRDEC_MAX_S)
        by = {}
        for c in calls:
            by.setdefault(c[1], []).append(c)
        best = None
        for t, cs in by.items():
            if len(cs) < 2:
                continue
            regs = [r for r in _SD_ARGS if sum(r in c[2] for c in cs) * 2 > len(cs)]
            for pr in regs:
                for lr in regs + [None]:
                    for kr in regs:
                        if len({pr, lr, kr}) < (3 if lr else 2):
                            continue
                        for opn, op in _SD_OPS.items():
                            rows = []
                            for a, _, ar in cs:
                                p, n, k = ar.get(pr), ar.get(lr) if lr else ("imm", None), ar.get(kr)
                                if not p or not n or not k or p[0] not in ("ptr", "buf") or n[0] != "imm" or \
                                        k[0] != "imm" or not 0 < k[1] < 256:
                                    continue
                                n = n[1]
                                if n is not None and not 2 < n <= 4096:
                                    continue
                                if p[0] == "ptr":
                                    o = _va_off(secs, p[1])
                                    if o is None:
                                        continue
                                    ct = data[o:o + (n or 4096)]
                                else:
                                    ct = p[1][:n or 1024]
                                if n is None:
                                    ct = ct.split(b"\0", 1)[0]
                                if len(ct) < 3 or (n is not None and len(ct) != n):
                                    continue
                                pt = bytes(op(c, k[1]) for c in ct)
                                gain = sum(_SD_SCORE[c] for c in pt) - sum(_SD_SCORE[c] for c in ct)
                                if not set(pt) <= _SD_PRINT or gain < 0:
                                    continue
                                rows.append((a, pt.decode("latin-1"), k[1], len(ct),
                                             "rodata" if p[0] == "ptr" else "stack", gain))
                            win = sum(r[5] > 0 for r in rows)
                            score = (len(rows), sum(r[5] for r in rows))
                            if win >= 2 and len(rows) * 5 >= len(cs) * 3 and score[1] > 0 and \
                                    (best is None or score > best[3]):
                                best = (rows, t, opn, score)
        if best is None:
            return None
        rows, t, opn, _ = best
        rows.sort()
        name = next((nm for v, _, nm in _elf_funcs(data) if v == t), "none")
        ss = [r[1] for r in rows]
        out = {"decoder_va": t, "decoder": name, "algorithm": opn, "strings": ss, "count": len(ss),
               "keys": [r[2] for r in rows], "lengths": [r[3] for r in rows], "call_sites": [r[0] for r in rows],
               "storage": [r[4] for r in rows]}
        url = re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s\"'<>]+", re.I)
        host = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24}\b", re.I)
        ip = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
        uniq = lambda xs: list(dict.fromkeys(xs))   # noqa: E731
        out["urls"] = uniq(m for s in ss for m in url.findall(s))
        out["domains"] = uniq(m.lower() for s in ss for m in host.findall(s)
                              if not re.fullmatch(r"[\d.]+", m) and not re.search(r"\.(exe|dll|php|sys|bat|ps1|txt|"
                                                                                   r"dat|bin|js|vbs|html?)$", m, re.I))
        out["ips"] = uniq(m.group(0) for s in ss for m in ip.finditer(s))
        out["mutexes"] = [s for s in ss if re.match(r"(?:Global|Local|Session\\\d+)\\", s)]
        out["campaign_ids"] = uniq(m for s in ss for m in re.findall(r"\b[A-Z]{2,6}-[0-9A-F]{2,}(?:-[0-9A-Z]+)*\b", s)
                                   if not s.startswith(("Global\\", "Local\\")))
        out["registry_keys"] = [s for s in ss if re.match(r"(?:HK(?:LM|CU|CR|U|EY_\w+)|SOFTWARE|SYSTEM)\\", s, re.I)]
        out["paths"] = [s for s in ss if re.match(r"(?:[A-Za-z]:\\|%\w+%\\|/(?:tmp|etc|var|usr|home|dev|opt)/)", s)]
        out["user_agents"] = [s for s in ss if s.startswith("Mozilla/")]
        out["speculative"] = True
        return out
    except Exception:  # noqa: BLE001 -- untrusted bytes: cannot answer
        return None


def string_decrypt_field(data, name):
    """One string_decrypt_facts value as an answer string: lists comma-joined, VAs/keys 0x-hex; "none" when absent."""
    try:
        f = string_decrypt_facts(data)
        if f is None:
            return "none"
        v = f.get(name, "none")
        if name in ("decoder_va",) and isinstance(v, int):
            return hex(v)
        if name in ("keys", "call_sites"):
            v = [hex(x) for x in v]
        if isinstance(v, list):
            return ",".join(str(x) for x in v) if v else "none"
        return str(v)
    except Exception:  # noqa: BLE001
        return "none"


# ------------------------------------------------------------------------------------------------ contract rule text
# D17: the organizers re-issued the contract mid-day; d12/d14 `hcfg_storage` went exact_text -> kind enum with
# `accepted_values` and "Apply these mutually exclusive rules in order: <tok> when <cond>; ...; otherwise <tok> ...".
# These helpers read that text, expose accepted_values, refuse off-list tokens, and diff two contract snapshots.
QRULE_REFUSED = []          # (id, value, accepted) for every token qrule_enforce refused (inspect after a run)
_QRULE_HEAD = re.compile(r"\b(?:apply|use)?\s*(?:these|the\s+following)?\s*(?:mutually\s+exclusive\s+)?rules?"
                         r"(?:\s+in\s+(?:this\s+)?order)?\s*:", re.I)
_QRULE_TOK = r"[A-Za-z0-9][A-Za-z0-9_.\-]*"
_QRULE_DEFAULT = re.compile(r"(?:^|[,;]?\s+)(?:otherwise|else|default)[,:]?\s+(?:use\s+|answer\s+|submit\s+)?"
                            r"[`'\"]?(" + _QRULE_TOK + r")[`'\"]?\b", re.I)
_QRULE_STOP = re.compile(r"\.\s+(?=(?:Submit|Answer|Report|Return|Respond|Use\s+the\s+literal|Do\s+not)\b)")


def _qr_questions(contract):
    """[question dict] from a contract / start / status body (dict with "questions", or a bare list)."""
    if isinstance(contract, (bytes, str)):
        try:
            contract = json.loads(contract)
        except ValueError:
            return []
    if isinstance(contract, dict):
        if isinstance(contract.get("questions"), list):
            return [q for q in contract["questions"] if isinstance(q, dict) and q.get("id")]
        for k in ("body", "contract", "attempt", "data"):
            if isinstance(contract.get(k), (dict, list)):
                r = _qr_questions(contract[k])
                if r:
                    return r
        return []
    return [q for q in contract if isinstance(q, dict) and q.get("id")] if isinstance(contract, list) else []


def qrule_accepted(q):
    """The question's `answer_format.accepted_values` as a list of strings, or None (free-form answer)."""
    af = q.get("answer_format") if isinstance(q, dict) else None
    av = af.get("accepted_values") if isinstance(af, dict) else None
    if isinstance(av, list) and av:
        return [str(v) for v in av]
    return None


def contract_accepted(contract):
    """{answer_id: [accepted token]} for every id whose answer_format lists accepted_values."""
    return {q["id"]: av for q in _qr_questions(contract) if (av := qrule_accepted(q))}


def qrule_rules(q, accepted=None):
    """[(token, condition)] in the question's stated order, parsed from 'rules in order: A when x; B when y; ...;
    otherwise C ...'. The default rule's condition starts with "otherwise". `q` is a question dict (its
    accepted_values anchor the tokens) or the bare text. [] when the text states no rule list. Never raises."""
    try:
        text = q.get("question", "") if isinstance(q, dict) else str(q or "")
        if accepted is None and isinstance(q, dict):
            accepted = qrule_accepted(q)
        acc = set(accepted or ())
        m = _QRULE_HEAD.search(text)
        if not m:
            return []
        body = text[m.end():]
        st = _QRULE_STOP.search(body)
        body = (body[:st.start()] if st else body).strip().rstrip(".").strip()
        tok_ok = (lambda t: t in acc) if acc else (lambda t: True)
        start = re.compile(r"^(?:use\s+|answer\s+)?[`'\"]?(" + _QRULE_TOK + r")[`'\"]?\s+(?:when|if|whenever)\b\s*(.*)$",
                           re.I | re.S)
        rules, default = [], None
        for seg in re.split(r"\s*;\s*", body):
            if not seg:
                continue
            d = re.match(r"^(?:otherwise|else|default)[,:]?\s+(?:use\s+|answer\s+|submit\s+)?[`'\"]?(" + _QRULE_TOK +
                         r")[`'\"]?\b\s*(.*)$", seg, re.I | re.S)
            if d and tok_ok(d.group(1)):
                default = (d.group(1), ("otherwise " + d.group(2).strip()).strip())
                continue
            s = start.match(seg)
            if s and tok_ok(s.group(1)) and default is None:
                rules.append([s.group(1), s.group(2).strip()])
            elif rules and default is None:
                rules[-1][1] += "; " + seg          # a ';' inside one condition (D17 raw_const_array)
        if rules and default is None:               # "... when x, otherwise C" inside the last segment
            d = _QRULE_DEFAULT.search(rules[-1][1])
            if d and tok_ok(d.group(1)):
                default = (d.group(1), ("otherwise " + rules[-1][1][d.end():].strip()).strip())
                rules[-1][1] = rules[-1][1][:d.start()].strip()
        out = [(t, c.strip()) for t, c in rules]
        return out + [default] if default else out
    except Exception:  # noqa: BLE001 -- untrusted contract text: no rules
        return []


def contract_rules(contract):
    """{answer_id: [(token, condition)]} for every question that states an ordered rule list."""
    return {q["id"]: r for q in _qr_questions(contract) if (r := qrule_rules(q))}


def qrule_pick(rules, holds):
    """First token whose condition holds (`holds` = {token: bool} or callable(token, condition) -> bool), else
    the "otherwise" token, else None. Encodes 'mutually exclusive rules in order'."""
    for tok, cond in rules or ():
        if cond.startswith("otherwise"):
            return tok
        try:
            ok = holds(tok, cond) if callable(holds) else bool(holds.get(tok))
        except Exception:  # noqa: BLE001
            ok = False
        if ok:
            return tok
    return None


def qrule_enforce(q, value, log=None):
    """`value` if the question accepts it, else "" (and the refusal is logged): never emit a token outside
    accepted_values. Free-form questions pass through. Surrounding whitespace is trimmed only when that makes it
    an accepted token; case is folded only when the stated normalization is not "exact"."""
    av = qrule_accepted(q)
    if av is None or value is None:
        return value
    v = str(value)
    if v in av:
        return v
    if v.strip() in av:
        return v.strip()
    if str(q.get("normalization", "exact")).lower() not in ("exact", "", "none"):
        hit = [a for a in av if a.casefold() == v.strip().casefold()]
        if len(hit) == 1:
            return hit[0]
    rec = (q.get("id"), v, list(av))
    QRULE_REFUSED.append(rec)
    if callable(log):
        try:
            log(f"qrule: refused {v!r} for {rec[0]} (accepted: {', '.join(av)})")
        except Exception:  # noqa: BLE001
            pass
    return ""


def contract_enforce(contract, answers, log=None):
    """{id: value} with every enum id passed through qrule_enforce (ids not in the contract pass unchanged)."""
    qs = {q["id"]: q for q in _qr_questions(contract)}
    return {k: (qrule_enforce(qs[k], v, log) if k in qs else v) for k, v in (answers or {}).items()}


_QR_DIFF_KEYS = ("question", "answer_format", "normalization", "artifact")


def contract_diff(old, new):
    """Per-id revision between two contract snapshots: {id: {"changed": [keys], "old": {...}, "new": {...}}} for
    every id whose question/answer_format/normalization/artifact differs, plus "_added"/"_removed" id lists when
    any. Order-insensitive (ids keyed); {} when nothing changed."""
    a = {q["id"]: q for q in _qr_questions(old)}
    b = {q["id"]: q for q in _qr_questions(new)}
    out = {}
    for k, qb in b.items():
        qa = a.get(k)
        if qa is None:
            continue
        ch = [f for f in _QR_DIFF_KEYS if qa.get(f) != qb.get(f)]
        if ch:
            out[k] = {"changed": ch, "old": {f: qa.get(f) for f in ch}, "new": {f: qb.get(f) for f in ch}}
    added, removed = [k for k in b if k not in a], [k for k in a if k not in b]
    if added:
        out["_added"] = added
    if removed:
        out["_removed"] = removed
    return out


def contract_revision_lines(old, new):
    """One human line per revised id (what a stuck worker needs to see first)."""
    d = contract_diff(old, new)
    b = {q["id"]: q for q in _qr_questions(new)}
    lines = []
    for k, v in d.items():
        if k.startswith("_"):
            lines.append(f"{k[1:]}: {', '.join(v)}")
            continue
        parts = []
        if "answer_format" in v["changed"]:
            ok = (v["old"]["answer_format"] or {}).get("kind") if isinstance(v["old"]["answer_format"], dict) else None
            nk = (v["new"]["answer_format"] or {}).get("kind") if isinstance(v["new"]["answer_format"], dict) else None
            av = qrule_accepted(b.get(k, {}))
            parts.append(f"answer_format {ok}->{nk}" + (f" accepted={av}" if av else ""))
        if "question" in v["changed"]:
            r = qrule_rules(b.get(k, {}))
            parts.append("question text changed" + (f"; rules in order: {' > '.join(t for t, _ in r)}" if r else ""))
        parts += [f"{f} changed" for f in v["changed"] if f in ("normalization", "artifact")]
        lines.append(f"{k}: " + "; ".join(parts))
    return lines
