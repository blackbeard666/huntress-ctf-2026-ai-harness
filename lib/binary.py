"""Advanced binary-RE helpers — the hardening layer on top of lib/elf.py's header/symbol reads.

Covers what the audit flagged as missing: packer detection + UPX unpacking, stripped-Go function-name
recovery from .gopclntab (names survive stripping there), Mach-O facts (lief), robust constant recovery via
capstone disassembly (replacing the fragile `b8..c3` byte regex), and a Ghidra headless decompile helper
(now that JDK 21 is wired). Everything is static. Pure-stdlib + capstone/lief/pyelftools from the venv.

hcfg_scan() (Day 14 prep) finds the lane's HCFG config blob in ANY of the storage encodings below and crc-gates it;
it is pure stdlib (no subprocess) so in-window solvers can call it on the Homebase VM.
"""
import base64
import binascii
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
    if b"UPX!" in data[:4096] or b"UPX0" in data or b"UPX1" in data:
        packer = "upx"
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
    """Header facts for a Mach-O (fat or thin) via lief: cpu type, file type, flags, dylibs, entry. {} if
    not a Mach-O or lief missing. Closes the lane's Mach-O gap (previously facts() returned {})."""
    try:
        import lief
    except ImportError:
        return {}
    try:
        fat = lief.MachO.parse(raw=list(data))
    except Exception:  # noqa: BLE001
        return {}
    if fat is None or fat.size == 0:
        return {}
    b = fat.at(0)
    h = b.header
    return {
        "format": "mach-o",
        "cpu_type": str(h.cpu_type).split(".")[-1].lower(),
        "file_type": str(h.file_type).split(".")[-1].lower(),
        "nb_cmds": h.nb_cmds,
        "pie": bool(h.has(lief.MachO.Header.FLAGS.PIE)) if hasattr(h, "has") else None,
        "libraries": [lib.name for lib in b.libraries][:40],
        "entrypoint": hex(b.entrypoint) if hasattr(b, "entrypoint") else None,
    }


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
#
# OFFSET LAW (Hit.offset, decimal FILE offset -- what `hcfg_offset` asks for):
#   raw              the 'H' of the magic                          GM-confirmed (D12 FPC 82928)
#   base64           the first base64 char ('S' of 'SENGR...')     GM-confirmed (D9 30696, D11 368272, D13 560188)
#   everything else  the first byte of the STORED encoded form, i.e. the lowest file offset the stored bytes occupy:
#                    hex -> first char of the text (the '\' of '\x48' / the '0' of '0x48'); base32/base85/base64url ->
#                    first char; ascii85 -> the '<' of a '<~' prefix if present; UTF-16 -> first byte of the first code
#                    unit (BE: its 0x00 byte); reversed -> lowest byte of the reversed region (= where the blob's LAST
#                    byte sits); xor'd -> first stored byte; zlib/gzip/deflate -> first byte of the compressed stream
#                    (0x78 CMF / 0x1f gzip magic; a zlib/gzip stream that holds the blob further in: still the
#                    stream start, detail "at+N"). These are SPECULATIVE (Hit.speculative=True): not GM-verified yet.
HCFG_MAGIC = b"HCFG"
HCFG_SCAN_EXT = os.environ.get("HCTF_HCFG_SCAN_EXT", "1") != "0"   # 0: only the D13 encodings (_LEGACY)
HCFG_DEFLATE_BRUTE_MAX = int(os.environ.get("HCTF_HCFG_DEFLATE_MAX", str(1 << 20)))   # headerless deflate brute cap
HCFG_B64ALPHA_MAX = int(os.environ.get("HCTF_HCFG_B64ALPHA_MAX", str(32 << 20)))   # alphabet-run chars examined
HCFG_MXOR_MAX = int(os.environ.get("HCTF_HCFG_MXOR_MAX", str(8 << 20)))   # whole-blob multi-byte xor cap (~65 ms/MiB)
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


def _anchor_table():
    lit = {HCFG_MAGIC: ("raw", None), b"GFCH": ("rev-raw", None), b"RGNES": ("rev-b64", None)}
    for a, codec in _TEXT_ANCHORS:
        lit[a] = ("text", codec)
        lit[_widen(a)[:-1]] = ("u16text", None)   # 'S\0E\0N\0G\0R': LE at i, BE at i-1
    lit[_widen(b"48")[:-1]] = ("u16text", None)
    lit[_widen(HCFG_MAGIC)[:-1]] = ("u16raw", None)
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


_PRINTABLE = frozenset(range(0x20, 0x7f)) | {9, 10, 13}
_PMASK = [sum(1 << k for k in range(256) if b ^ k in _PRINTABLE) for b in range(256)]   # keys keeping b printable
_JSONW = {**{c: 2 for c in b"bcfgkmpquvwxyz0123456789:,._-/ "}, **{c: 4 for c in b'etaoinsrhld"'},
          **{c: 1 for c in b"ABCDEFGHIJKLMNOPQRSTUVWXYZ{}[]\\\n"}}   # JSON config byte weights (key ranking)


def _xor_rep(buf, key):
    """buf ^ key repeated from buf[0]."""
    k = (key * (len(buf) // len(key) + 1))[:len(buf)]
    return (int.from_bytes(buf, "little") ^ int.from_bytes(k, "little")).to_bytes(len(buf), "little")


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


def hcfg_scan(data, *, deadline=None, ext=None, stop_on_valid=False):
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
    for m in _ANCHORS.finditer(data):
        i, a = m.start(), m.group(0)
        kind = _ANCHOR_KIND.get(a, "hex")
        if not ext and kind not in ("raw", "hex") and _ANCHOR_CODEC.get(a) is not _B64:
            continue   # kill-switch: the D13 solver's encodings only (raw, base64/url, hex)
        if kind == "raw":
            emit(i, "raw", data[i:i + _need(data[i:i + 8])])
        elif kind == "hex":
            _hex_at(data, i, emit)
        elif kind == "text":
            _text_at(data, i, _ANCHOR_CODEC[a], emit)
        elif kind == "rev-raw":   # 'GFCH' = the last 4 bytes of the reversed blob
            e = i + 4
            if e >= 12:
                st = max(0, e - _need(data[e - 12:e][::-1]))
                emit(st, "reversed-raw", data[st:e][::-1])
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
    if not valid() and not late():
        # ROT13 / case-swapped base64, optionally reversed per line: one bytes.find per transformed 'SENGR' (kept out
        # of the anchor regex -- first bytes e/r/s/f made that pass ~33% slower)
        for a in [a for a in _ROTB64 if a != b"RGNES"]:
            i = data.find(a)
            while i >= 0 and not late():
                _rotb64_at(data, i, a, emit)
                i = data.find(a, i + 1)
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
    return _rank(hits)


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
