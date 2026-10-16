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
                             "offset": base + off if off else 0, "size": sz})
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
    not a version-1 wasm binary (the '\\0asm' magic alone does not count: every section must parse to the end)."""
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
                                     "imported": True})
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
                                 "imported": False})
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
        return {"format": "wasm", "machine": "wasm64" if any(m["memory64"] for m in mems) else "wasm32",
                "version": 1, "sections": secs, "section_names": [s["name"] for s in secs], "memories": mems,
                "data_segments": segs}
    except (IndexError, ValueError, TypeError):
        return None


def wasm_hcfg_segment(data):
    """[{segment, mode, file_offset, mem_offset, segment_file_offset, segment_mem_offset}] for every crc-valid raw
    HCFG blob inside a wasm data segment ([] if none / not wasm). file_offset = the 'H' in the file (= hcfg_scan's raw
    offset); mem_offset = segment memory offset + the blob's position in the segment (linear-memory address, None for
    passive / global-based segments)."""
    lay = wasm_layout(data) or {}
    out = []
    for s in lay.get("data_segments", ()):
        lo = s["file_offset"]
        seg = bytes(data[lo:lo + s["size"]])
        i = seg.find(HCFG_MAGIC)
        while i >= 0:
            blob = seg[i:]
            r = _parse_blob(blob[:_need(blob[:8])]) if len(blob) >= 12 else None
            if r and r[5]:
                mo = s["mem_offset"]
                out.append({"segment": s["index"], "mode": s["mode"], "file_offset": lo + i,
                            "mem_offset": None if mo is None else mo + i, "segment_file_offset": lo,
                            "segment_mem_offset": mo})
            i = seg.find(HCFG_MAGIC, i + 1)
    return out


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
    if not valid() and not late() and _depth < 2 and b"PK\x05\x06" in data[-65600:]:
        # jar/zip/apk: a compressed NON-class entry (config.bin, assets/...) the deflate anchors/brute miss (dynamic
        # Huffman in a > 1 MiB jar, or a text form inside) -> inflate it and look inside (offsets: OFFSET LAW)
        _zip_scan(data, emit, hits, deadline, late, _depth)
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
    if not valid() and not late() and len(data) <= HCFG_STRIDE_MAX:
        # every k-th byte (junk filler) / zipped halves / even-then-odd bytes of the blob or its base64
        _stride_scan(data, emit, late)
    if not valid() and not late():
        # blob assembled at runtime by mov-immediate stores / pushes: emulate the builder from its first 'H' store
        _stack_scan(data, emit, late)
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
            return machine_facts(data[lay["slices"][0]["slice_offset"]:]) if lay else None
        if mo and len(data) >= 8:
            m = int.from_bytes(data[4:8], mo[0])
            return {"format": "mach-o", "machine": MACHO_CPU_LABEL.get(m, str(m)), "machine_num": str(m),
                    "endian": mo[0], "bits": mo[1]}
        if data[:4] == b"\0asm":   # WebAssembly: no machine number; wasm32 unless a memory is memory64
            lay = wasm_layout(data)
            if lay:
                return {"format": "wasm", "machine": lay["machine"], "machine_num": "none", "endian": "little",
                        "bits": 64 if lay["machine"] == "wasm64" else 32}
    except (IndexError, ValueError, TypeError):
        pass
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
    "overlay" | "section", "slot_offset" (resource data start / overlay start / section start), "delta" (off - slot),
    + type_name/name/lang | section}, or None. For a resource-relative or overlay-relative offset question."""
    data = bytes(data)
    for r in pe_resources(data):
        if r["offset"] is not None and r["offset"] <= off < r["offset"] + r["size"]:
            return {"container": "pe-resource", "slot_offset": r["offset"], "delta": off - r["offset"],
                    "type_name": r["type_name"], "name": r["name"], "lang": r["lang"], "size": r["size"]}
    for r in dotnet_resources(data):
        if r["offset"] <= off < r["offset"] + r["size"]:
            return {"container": "dotnet-resource", "slot_offset": r["offset"], "delta": off - r["offset"],
                    "size": r["size"]}
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

