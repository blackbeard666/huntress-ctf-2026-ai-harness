#!/usr/bin/env python3
"""Day-independent LANE solver for binary-reverse-engineering (prototype, review5).

CLI (same as every solver):  binary_lane.py --contract contract.json --artifacts <dir>
  -> last stdout line = JSON {answer_id: value}; diagnostics on stderr.
Deps: stdlib + pyzipper (AES zips) + pyelftools + pefile + capstone.  No subprocess (Homebase has no apt tools).

Pipeline
  1. evidence loader   question.artifact ('evidence.zip' | 'delivery N: evidence.zip' | 'evidence-02.zip') -> file,
                       resolving delivery N by contract.artifacts[N-1].sha256 first (per-set same-named downloads), then
                       by path name, then by zip order; a set whose bytes were never fetched is NOT answered from
                       another set.  Zip members are read with pw infected/...; nested *.zip wrappers are flattened,
                       any other nested archive (jar/apk/...) stays one member.
  2. id router         [setN.]dNN_artifact_sha256_K | [setN.]dNN_analysis_<field>       (Day 3+ grammar)
                       [setN.]slotK_<field>                                             (Day 1 TT)
                       [setN.](c|cpp)_<field> | bare <field>                            (Day 1/2)
  3. analyzers         ELF (pyelftools + capstone), PE / .NET (pefile + BSJB root), JAR/class (pure-python constant
                       pool), Go buildinfo, Rust .comment -- each lazily computed and cached per member sha256.
  4. HCFG hunter       container-agnostic: raw bytes -> nested zip members -> zlib/gzip streams -> ASCII/UTF-16 strings
                       decoded as base64/urlsafe/hex (and reversed) -> JVM constant pool / <clinit> arrays;
                       'HCFG' u8 ver u8 xor u16 len u32 crc32 + xor'd JSON, accepted only when crc32 validates
                       (CRC-less JSON hits are a last resort; header-less xor brute force after that).

Experiment flag  HCTF_BIN_DISABLE=jar,rust,go,dotnet,legacy  turns off a container-specific analyzer so the generic
residue (sha256s, HCFG, magic-sniffed format) can be measured on a day the solver "has never seen".
"""
import argparse, base64, binascii, gzip, hashlib, io, json, os, re, struct, sys, zipfile, zlib

ROOT = os.environ.get("HCTF_ROOT") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
if os.path.isdir(os.path.join(ROOT, "lib")) and ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    from lib import knowledge as K
except Exception:  # pragma: no cover - standalone copy on a VM
    K = None
try:
    import pyzipper
    _AES = pyzipper.AESZipFile
except ImportError:  # pragma: no cover
    _AES = None

DISABLED = {t.strip().lower() for t in os.environ.get("HCTF_BIN_DISABLE", "").split(",") if t.strip()}
PASSWORDS = [b"infected", b"flare", b"malware", b"virus", b"huntress"]

# ---- GM-confirmed vocabulary (knowledge.py is the source of truth; literals are the fallback) ----
ELF_CLASS = getattr(K, "ELF_CLASS", {"ELFCLASS32": "ELF32", "ELFCLASS64": "ELF64"})
ELF_ENDIAN = getattr(K, "ELF_ENDIANNESS", {"ELFDATA2LSB": "little", "ELFDATA2MSB": "big"})
ELF_MACHINE = dict(getattr(K, "ELF_MACHINE", {}) or {"EM_X86_64": "x86-64", "EM_386": "x86", "EM_AARCH64": "AArch64", "EM_ARM": "ARM"})
PE_MACHINE = dict(getattr(K, "PE_MACHINE", {}) or {0x14c: "i386", 0x8664: "x86-64", 0xaa64: "AArch64", 0x1c0: "ARM"})
PE_MACHINE.setdefault(0x8664, "x86-64")
DOTNET_FORMAT = getattr(K, "DOTNET_FORMAT", "pe_cli")
JAR_FORMAT = getattr(K, "JAR_FORMAT", "jar")
BINARY_FORMAT = dict(getattr(K, "BINARY_FORMAT", {}) or {"ELF": "elf", "PE": "pe", "MACHO": "macho"})
# UNCONFIRMED guesses for containers the GM has not asked about yet (bare lowercase family name law).
GUESS_FORMAT = {"MACHO": "macho", "CLASS": "class", "DEX": "dex", "APK": "apk", "WASM": "wasm", "ZIP": "zip"}

TOOLCHAIN = {"main", "_start", "_init", "_fini", "frame_dummy", "register_tm_clones", "deregister_tm_clones",
             "__do_global_dtors_aux", "_dl_relocate_static_pie", "__libc_csu_init", "__libc_csu_fini"}


def log(*a):
    print(*a, file=sys.stderr)


def sha(b):
    return hashlib.sha256(b).hexdigest()


# =====================================================================================================================
# 1. evidence loader
# =====================================================================================================================

def _zip_members(data, depth=0):
    """[(name, bytes)] archive order. Nested *.zip wrappers are flattened; jars/apks/etc. stay whole."""
    readers = ([_AES] if _AES else []) + [zipfile.ZipFile]
    best = []
    for Z in readers:
        try:
            with Z(io.BytesIO(data)) as z:
                out, complete = [], True
                for i in z.infolist():
                    if i.is_dir():
                        continue
                    b = None
                    for pw in [None] + PASSWORDS:
                        try:
                            b = z.read(i.filename, pwd=pw) if pw else z.read(i.filename)
                            break
                        except Exception:  # noqa: BLE001
                            continue
                    if b is None:
                        complete = False
                        continue
                    if b[:2] == b"PK" and i.filename.lower().endswith(".zip") and depth < 4:
                        out += _zip_members(b, depth + 1) or [(i.filename, b)]
                    else:
                        out.append((i.filename, b))
                if complete and out:
                    return out
                if len(out) > len(best):
                    best = out
        except Exception:  # noqa: BLE001
            continue
    return best


class Evidence:
    def __init__(self, adir, contract):
        self.adir, self.c = adir, contract
        self.files = sorted(os.path.join(r, f) for r, _, fs in os.walk(adir) for f in fs if f != "manifest.json")
        self._sha = {}
        self._members = {}

    def fsha(self, p):
        if p not in self._sha:
            with open(p, "rb") as fh:
                self._sha[p] = sha(fh.read())
        return self._sha[p]

    def _hashes(self):
        return [a.get("sha256", "").lower() for a in (self.c.get("artifacts") or []) if isinstance(a, dict)]

    def _containers(self):
        names = []
        for q in self.c.get("questions") or []:
            n = (q.get("artifact") or "").strip()
            if n and n not in names:
                names.append(n)
        return names

    def resolve(self, art):
        """Path of the file behind a question's artifact string, or None (never another set's bytes)."""
        files = self.files
        if not files:
            return None
        art = (art or "evidence.zip").split("->")[0].strip()
        bare = art.split(":", 1)[-1].strip()
        for p in files:   # exact saved name ('delivery 2: evidence.zip')
            if os.path.basename(p) == art:
                return p
        hashes = self._hashes()
        m = re.search(r"delivery\s*(\d+)", art, re.I)
        idx = int(m.group(1)) - 1 if m else None
        if idx is None:   # 'evidence-02.zip' style: pair unique container names with artifacts[] by order
            names = self._containers()
            if len(names) > 1 and len(names) == len(hashes) and art in names:
                idx = names.index(art)
        if idx is not None and 0 <= idx < len(hashes) and hashes[idx]:
            hit = [p for p in files if self.fsha(p) == hashes[idx]]
            if hit:
                return hit[0]
        if m:
            n = m.group(1)
            hit = [p for p in files if re.search(rf"(delivery|set)[^0-9/]*0*{n}(?!\d)", p, re.I)]
            if len(hit) == 1:
                return hit[0]
            if len(hashes) >= 2 and all(hashes):   # hashed deliveries and none matched: that set was never fetched
                known = {self.fsha(p) for p in files}
                if hashes[idx] not in known and len(files) < len(hashes):
                    return None
            zips = [p for p in files if p.lower().endswith(".zip")]
            if 0 <= idx < len(zips) and len(zips) > 1:
                return zips[idx]
        for p in files:
            if os.path.basename(p) in (bare, os.path.basename(bare)):
                return p
        if len(hashes) == 1 and hashes[0]:
            hit = [p for p in files if self.fsha(p) == hashes[0]]
            if hit:
                return hit[0]
        return files[0] if len(files) == 1 else None

    def members(self, path):
        if path not in self._members:
            with open(path, "rb") as fh:
                data = fh.read()
            mem = _zip_members(data) if data[:2] == b"PK" and path.lower().endswith(".zip") else []
            self._members[path] = mem or [(os.path.basename(path), data)]
            log(f"[*] {os.path.basename(path)}: {[n for n, _ in self._members[path]]}")
        return self._members[path]


# =====================================================================================================================
# 3. analyzers (lazy, cached per member)
# =====================================================================================================================

def is_zip_jar(b):
    if b[:2] != b"PK":
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            names = z.namelist()
    except Exception:  # noqa: BLE001
        return False
    return any(n.endswith(".class") for n in names) or "META-INF/MANIFEST.MF" in names and "AndroidManifest.xml" not in names


def sniff(b):
    """Container kind from magic bytes."""
    if b[:4] == b"\x7fELF":
        return "ELF"
    if b[:2] == b"MZ":
        return "PE"
    if b[:4] in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xfe\xed\xfa\xce"):
        return "MACHO"
    if b[:4] == b"\xca\xfe\xba\xbe":
        major = struct.unpack_from(">H", b, 6)[0] if len(b) >= 8 else 0
        return "CLASS" if major >= 45 else "MACHO"   # fat Mach-O shares the magic (small arch count)
    if b[:4] == b"dex\n":
        return "DEX"
    if b[:4] == b"\0asm":
        return "WASM"
    if b[:2] == b"PK":
        try:
            names = zipfile.ZipFile(io.BytesIO(b)).namelist()
        except Exception:  # noqa: BLE001
            names = []
        if "AndroidManifest.xml" in names or "classes.dex" in names:
            return "APK"
        if "jar" not in DISABLED and (any(n.endswith(".class") for n in names) or "META-INF/MANIFEST.MF" in names):
            return "JAR"
        return "ZIP"
    return None


def is_binary(b):
    return sniff(b) not in (None, "ZIP")


# ---------------- ELF ----------------

class Lazy(dict):
    """dict whose Lazy.of(fn) values are computed on first access (Go/Rust symtabs are thousands of entries)."""
    class of:
        def __init__(self, fn):
            self.fn = fn

    def __getitem__(self, k):
        v = dict.__getitem__(self, k)
        if isinstance(v, Lazy.of):
            v = v.fn()
            dict.__setitem__(self, k, v)
        return v

    def get(self, k, d=None):
        return self[k] if k in self else d

def _x86_md(bits):
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_MODE_64
    return Cs(CS_ARCH_X86, CS_MODE_64 if bits == 64 else CS_MODE_32)


def elf_disassembly(elf):
    """GM-CONFIRMED (Day 3): capstone intel of recover_code, 'mnemonic op_str' with ', ' kept, immediates DECIMAL,
    up to the first ret. Stripped build: last leaf `mov eax, imm32; ret` in .text."""
    if elf["e_machine"] not in ("EM_X86_64", "EM_386"):
        return None
    text = elf.get_section_by_name(".text")
    if text is None:
        return []
    tdata, taddr = text.data(), text["sh_addr"]
    start = size = None
    st = elf.get_section_by_name(".symtab")
    if st is not None:
        s = st.get_symbol_by_name("recover_code")
        if s:
            start, size = s[0]["st_value"], s[0]["st_size"]
    if start is None:
        hits = [m.start() for m in re.finditer(rb"\xb8.{4}\xc3", tdata, re.S)]
        if not hits:
            return []
        start, size = taddr + hits[-1], 6
    off = start - taddr
    out = []
    for i in _x86_md(elf.elfclass).disasm(tdata[off:off + (size or 64)], start):
        op = re.sub(r"0x[0-9a-fA-F]+", lambda m: str(int(m.group(0), 16)), i.op_str)
        out.append(f"{i.mnemonic} {op}".strip())
        if i.mnemonic.startswith("ret"):
            break
    return out


def _all_syms(elf):
    from elftools.elf.sections import SymbolTableSection
    out = []
    for sec in elf.iter_sections():
        if isinstance(sec, SymbolTableSection):
            out += [(sec.name, s) for s in sec.iter_symbols()]
    return out


def _designated_symbol(elf):
    for _, s in _all_syms(elf):
        i = s["st_info"]
        if (i["type"] == "STT_FUNC" and i["bind"] in ("STB_GLOBAL", "STB_WEAK") and s["st_shndx"] != "SHN_UNDEF"
                and s.name and s.name not in TOOLCHAIN and not s.name.startswith("_")):
            return s.name
    return "none"


def _va2off_elf(elf, va):
    for seg in elf.iter_segments():
        if seg["p_type"] == "PT_LOAD" and seg["p_vaddr"] <= va < seg["p_vaddr"] + seg["p_filesz"]:
            return va - seg["p_vaddr"] + seg["p_offset"]
    return None


def _ret_const(md, code, addr):
    regs = {}
    for ins in md.disasm(code, addr):
        ops = ins.op_str.replace(" ", "")
        m = re.match(r"(\w+),#?(-?(?:0x[0-9a-f]+|\d+))$", ops)
        if ins.mnemonic in ("mov", "movz", "movabs") and m:
            regs[m.group(1)] = int(m.group(2), 0)
        elif ins.mnemonic == "xor" and re.match(r"(\w+),\1$", ops):
            regs[ops.split(",")[0]] = 0
        if ins.mnemonic in ("ret", "retq"):
            for r in ("eax", "rax", "w0", "x0"):
                if r in regs:
                    v = regs[r]
                    return v - 2**32 if 2**31 <= v < 2**32 else v
            return None
    return None


def _stripped_leaf_const(text):
    """Stripped build: the leaf `mov eax, imm32; ret`; main inlines the same immediate (tie-break)."""
    if not text:
        return None
    imms = list(dict.fromkeys(struct.unpack("<i", m.group(1))[0] for m in re.finditer(rb"\xb8(.{4})\xc3", text, re.S)))
    if len(imms) > 1:
        imms = [v for v in imms if len(re.findall(re.escape(b"\xb8" + struct.pack("<i", v)), text)) > 1] or imms
    return imms[0] if len(imms) == 1 else None


def elf_facts(data):
    from elftools.elf.elffile import ELFFile
    elf = ELFFile(io.BytesIO(data))
    h = elf.header
    st = elf.get_section_by_name(".symtab")
    hs = elf.get_section_by_name(".huntress")
    mach = ELF_MACHINE.get(h["e_machine"], h["e_machine"])
    text = elf.get_section_by_name(".text")
    syms = lambda: [(s.name.split("@")[0], s["st_value"], s["st_size"], s["st_info"]["type"],
                     s["st_shndx"] != "SHN_UNDEF") for _, s in _all_syms(elf) if s.name]
    f = Lazy({
        "kind": "ELF", "format": BINARY_FORMAT.get("ELF", "elf"), "bits": elf.elfclass,
        "elf_class": ELF_CLASS.get(h["e_ident"]["EI_CLASS"], h["e_ident"]["EI_CLASS"]),
        "class": ELF_CLASS.get(h["e_ident"]["EI_CLASS"], h["e_ident"]["EI_CLASS"]),
        "endianness": ELF_ENDIAN.get(h["e_ident"]["EI_DATA"], h["e_ident"]["EI_DATA"]),
        "machine": mach, "architecture": mach,
        "elf_type": h["e_type"], "type": h["e_type"],
        "entry_point": hex(h["e_entry"]),
        "section_names": [s.name for s in elf.iter_sections()],
        "symbols": Lazy.of(lambda: [s.name for s in st.iter_symbols() if s.name] if st is not None else []),
        "has_symtab": "true" if st is not None else "false",
        "marker": hs.data().split(b"\0", 1)[0].decode("utf-8", "replace") if hs is not None else "none",
        "exported_symbol": Lazy.of(lambda: _designated_symbol(elf)),
        "_syms": Lazy.of(syms), "_text": Lazy.of(lambda: text.data() if text is not None else b""),
        "_disasm": lambda: elf_disassembly(elf),
        "_va2off": lambda va: _va2off_elf(elf, va),
        "_md": (lambda: _x86_md(elf.elfclass)) if h["e_machine"] in ("EM_X86_64", "EM_386") else None,
    })
    comment = elf.get_section_by_name(".comment")
    if comment is not None:
        f["compiler"] = comment.data().split(b"\0")[0].decode("utf-8", "replace") or "none"
        if "rust" not in DISABLED:
            m = re.search(rb"rustc version (\S+)", comment.data())
            if m:
                f["rust_version"] = f["rustc_version"] = m.group(1).decode()
    return f


# ---------------- PE / .NET ----------------

def cli_metadata_version(data):
    for m in re.finditer(rb"BSJB", data):
        o = m.start()
        if o + 16 > len(data):
            continue
        n = struct.unpack_from("<I", data, o + 12)[0]
        if 0 < n <= 256:
            return data[o + 16:o + 16 + n].split(b"\0", 1)[0].decode("ascii", "replace")
    return None


def _coff_symbols(pe, data):
    fh = pe.FILE_HEADER
    ptr, n = fh.PointerToSymbolTable, fh.NumberOfSymbols
    if not ptr or not n or ptr + 18 * n > len(data):
        return []
    strtab, secs, out, i = ptr + 18 * n, pe.sections, [], 0
    while i < n:
        raw, value, secno, typ, _cls, naux = struct.unpack_from("<8sIhHBB", data, ptr + 18 * i)
        if raw[:4] == b"\0\0\0\0":
            o = strtab + struct.unpack_from("<I", raw, 4)[0]
            name = data[o:data.find(b"\0", o)].decode(errors="replace")
        else:
            name = raw.split(b"\0", 1)[0].decode(errors="replace")
        if name and 0 < secno <= len(secs):
            va = pe.OPTIONAL_HEADER.ImageBase + secs[secno - 1].VirtualAddress + value
            out.append((name, va, 0, "STT_FUNC" if typ & 0x20 else "STT_OBJECT", True))
        i += 1 + naux
    return out


def pe_facts(data):
    import pefile
    pe = pefile.PE(data=data, fast_load=True)
    dd = pe.OPTIONAL_HEADER.DATA_DIRECTORY
    clr = dd[14].VirtualAddress if len(dd) > 14 else 0
    mdv = cli_metadata_version(data) if clr else None
    dotnet = bool(clr) and mdv is not None and "dotnet" not in DISABLED
    mach = PE_MACHINE.get(pe.FILE_HEADER.Machine, hex(pe.FILE_HEADER.Machine))
    syms = _coff_symbols(pe, data)
    try:
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
        exp = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
        syms = [(e.name.decode(), pe.OPTIONAL_HEADER.ImageBase + e.address, 0, "STT_FUNC", True)
                for e in (exp.symbols if exp else []) if e.name] + syms
    except Exception:  # noqa: BLE001
        pass
    marker = "none"
    for s in pe.sections:
        if s.Name.rstrip(b"\0").decode(errors="replace").startswith(".huntres"):
            marker = s.get_data().split(b"\0", 1)[0].decode("utf-8", "replace")
    ib = pe.OPTIONAL_HEADER.ImageBase

    def va2off(va):
        try:
            return pe.get_offset_from_rva(va - ib)
        except Exception:  # noqa: BLE001
            return None
    return {
        "kind": "PE", "bits": 64 if pe.OPTIONAL_HEADER.Magic == 0x20b else 32,
        "format": DOTNET_FORMAT if dotnet else BINARY_FORMAT.get("PE", "pe"),
        "machine": mach, "architecture": mach,
        "metadata_version": mdv if mdv is not None and "dotnet" not in DISABLED else "none",
        "entry_point": hex(ib + pe.OPTIONAL_HEADER.AddressOfEntryPoint),
        "section_names": [s.Name.rstrip(b"\0").decode(errors="replace") for s in pe.sections],
        "has_symtab": "true" if pe.FILE_HEADER.PointerToSymbolTable and pe.FILE_HEADER.NumberOfSymbols else "false",
        "marker": marker, "_syms": syms, "_va2off": va2off,
        "_text": next((x.get_data() for x in pe.sections if x.Name.rstrip(b"\0") == b".text"), b""),
        "_md": lambda: _x86_md(64 if pe.FILE_HEADER.Machine == 0x8664 else 32),
        "timestamp": pe.FILE_HEADER.TimeDateStamp,
    }


# ---------------- JVM ----------------

_CP_SIZE = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 16: 2, 19: 2, 20: 2, 9: 4, 10: 4, 11: 4, 12: 4, 17: 4, 18: 4, 15: 3}


def class_utf8(cls):
    """Constant-pool Utf8 entries of a class file, pool order."""
    if cls[:4] != b"\xca\xfe\xba\xbe" or len(cls) < 10:
        return []
    n = struct.unpack_from(">H", cls, 8)[0]
    o, i, out = 10, 1, []
    try:
        while i < n:
            t = cls[o]
            o += 1
            if t == 1:
                ln = struct.unpack_from(">H", cls, o)[0]
                out.append(cls[o + 2:o + 2 + ln])
                o += 2 + ln
            elif t in _CP_SIZE:
                o += _CP_SIZE[t]
                i += t in (5, 6)
            else:
                break
            i += 1
    except (IndexError, struct.error):
        pass
    return out


def clinit_byte_arrays(cls):
    """Byte arrays built element-wise in bytecode (dup; push idx; push val; bastore)."""
    push = rb"(?:[\x02-\x08]|\x10.|\x11..)"
    run = re.compile(rb"(?:\x59" + push + push + rb"\x54)+", re.S)
    elem = re.compile(rb"\x59(" + push + rb")(" + push + rb")\x54", re.S)

    def val(p):
        if p[0] == 0x10:
            return struct.unpack(">b", p[1:2])[0]
        if p[0] == 0x11:
            return struct.unpack(">h", p[1:3])[0]
        return p[0] - 3
    out = []
    for m in run.finditer(cls):
        arr = {val(e.group(1)): val(e.group(2)) & 0xff for e in elem.finditer(m.group(0))}
        if len(arr) >= 12 and set(arr) == set(range(len(arr))):
            out.append(bytes(arr[k] for k in range(len(arr))))
    return out


def jar_classes(data):
    if data[:4] == b"\xca\xfe\xba\xbe":
        return [("", data)]
    out = []
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for n in z.namelist():
                b = z.read(n)
                if n.endswith(".class") or b[:4] == b"\xca\xfe\xba\xbe":
                    out.append((n, b))
                elif b[:2] == b"PK":
                    out += jar_classes(b)
    except Exception:  # noqa: BLE001
        pass
    return out


def jar_main_class(data):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
        m = re.search(r"^Main-Class:\s*(\S+)", mf, re.M)
        return m.group(1) if m else None
    except Exception:  # noqa: BLE001
        return None


def jar_facts(data):
    classes = jar_classes(data)
    majors = [struct.unpack_from(">H", c, 6)[0] for _, c in classes if len(c) >= 8]
    return {"kind": "JAR", "format": JAR_FORMAT, "main_class": jar_main_class(data) or "none",
            "class_names": [n for n, _ in classes],
            "class_major_version": str(max(majors)) if majors else "none"}


# ---------------- Go ----------------

def go_facts(data):
    """Go buildinfo ('\\xff Go buildinf:' header, Go >= 1.18 inline varint strings). UNCONFIRMED field names."""
    o = data.find(b"\xff Go buildinf:")
    if o < 0 or "go" in DISABLED:
        return {}
    flags = data[o + 15] if len(data) > o + 15 else 0
    f = {"go": True}
    if flags & 2:
        p = o + 32

        def rd(p):
            n = s = 0
            while True:
                b = data[p]
                n |= (b & 0x7f) << s
                p += 1
                s += 7
                if b < 0x80:
                    return data[p:p + n].decode("utf-8", "replace"), p + n
        try:
            ver, p = rd(p)
            mod, p = rd(p)
            f["go_version"] = ver
            for line in mod.splitlines():
                parts = line.split("\t")
                if parts[0] == "path" and len(parts) > 1:
                    f["go_module_path"] = parts[1]
                elif parts[0] == "mod" and len(parts) > 1:
                    f["go_module"] = parts[1]
                elif parts[0] == "build" and len(parts) > 1 and "=" in parts[1]:
                    k, v = parts[1].split("=", 1)
                    f["go_build_" + k.lower()] = v
        except Exception:  # noqa: BLE001
            pass
    return f


# =====================================================================================================================
# 4. HCFG hunter
# =====================================================================================================================

def _hcfg_at(data, strict):
    for m in re.finditer(rb"HCFG", data):
        o = m.start()
        if o + 12 > len(data):
            continue
        ver, key, n, crc = struct.unpack_from("<BBHI", data, o + 4)
        enc = data[o + 12:o + 12 + n]
        if len(enc) < n:
            continue
        plain = bytes(b ^ key for b in enc)
        ok = zlib.crc32(plain) == crc
        if strict and not ok:
            continue
        if not strict and plain[:1] != b"{":
            continue
        try:
            cfg = json.loads(plain.decode("utf-8"))
        except Exception:  # noqa: BLE001
            cfg = None
        if not ok and cfg is None:
            continue
        return {"key": key, "crc": zlib.crc32(plain), "version": ver, "length": n, "config": cfg, "crc_ok": ok}
    return None


_B64 = re.compile(rb"[A-Za-z0-9+/_-]{16,}={0,2}")
_HEX = re.compile(rb"(?:[0-9a-fA-F]{2}){12,}")
_U16 = re.compile(rb"(?:[\x20-\x7e]\x00){16,}")


def _decodes(s):
    outs = []
    for cand in (s, s[::-1]):
        if _B64.fullmatch(cand):
            for dec in (base64.b64decode, base64.urlsafe_b64decode):
                try:
                    outs.append(dec(cand + b"=" * (-len(cand) % 4)))
                except (binascii.Error, ValueError):
                    pass
        if len(cand) % 2 == 0 and _HEX.fullmatch(cand):
            outs.append(bytes.fromhex(cand.decode()))
    return outs


def _layers(data, depth=0):
    """Candidate byte layers to scan for HCFG, cheapest first (generator; stops when the caller has a hit)."""
    yield data
    if depth >= 3:
        return
    if data[:2] == b"PK":   # nested archive (jar/apk/zip), any password
        for _, b in _zip_members(data, 99):
            yield from _layers(b, depth + 1)
    if data[:2] == b"\x1f\x8b":
        try:
            yield from _layers(gzip.decompress(data), depth + 1)
        except Exception:  # noqa: BLE001
            pass
    # JVM constant pool + <clinit> arrays (container-specific; disabled with HCTF_BIN_DISABLE=jar)
    if data[:4] == b"\xca\xfe\xba\xbe" and "jar" not in DISABLED:
        utf8 = class_utf8(data)
        for s in utf8:
            yield from _decodes(re.sub(rb"\s+", b"", s))
        b64 = [s for s in utf8 if re.fullmatch(rb"[A-Za-z0-9+/=_-]{8,}", s)]
        if len(b64) > 1:
            yield from _decodes(b"".join(b64))
        yield from clinit_byte_arrays(data)
    # generic: encoded strings anywhere (ASCII + UTF-16LE), base64 / urlsafe / hex, also reversed
    for m in _B64.finditer(data):
        yield from _decodes(m.group(0))
    for m in _HEX.finditer(data):
        yield from _decodes(m.group(0))
    for m in _U16.finditer(data):
        s = m.group(0)[::2]
        yield from _decodes(s)
    for m in re.finditer(rb"\x78[\x01\x5e\x9c\xda]", data):   # embedded zlib streams
        try:
            d = zlib.decompressobj().decompress(data[m.start():m.start() + (1 << 20)])
            if len(d) >= 12:
                yield d
        except Exception:  # noqa: BLE001
            pass


def _headerless(data):
    for k in range(1, 256):
        pat = bytes([ord("{") ^ k, ord('"') ^ k])
        for m in re.finditer(re.escape(pat), data):
            end = data.find(bytes([ord("}") ^ k]), m.start())
            while end != -1:
                plain = bytes(b ^ k for b in data[m.start():end + 1])
                try:
                    return {"key": k, "crc": zlib.crc32(plain), "version": None, "length": len(plain),
                            "config": json.loads(plain.decode()), "crc_ok": False}
                except Exception:  # noqa: BLE001
                    end = data.find(bytes([ord("}") ^ k]), end + 1)
    return None


_HCFG_CACHE = {}


def hunt_hcfg(data):
    key = sha(data)
    if key in _HCFG_CACHE:
        return _HCFG_CACHE[key]
    loose = None
    res = None
    for layer in _layers(data):
        h = _hcfg_at(layer, strict=True)
        if h:
            res = h
            break
        if loose is None:
            loose = _hcfg_at(layer, strict=False)
    if res is None:
        res = loose or _headerless(data)
    _HCFG_CACHE[key] = res
    return res


# =====================================================================================================================
# 2. router
# =====================================================================================================================

_FACTS = {}


def facts(data, name=""):
    k = sha(data)
    if k not in _FACTS:
        kind = sniff(data)
        f = {}
        try:
            if kind == "ELF":
                f = elf_facts(data)
                f.update(go_facts(data))
            elif kind == "PE":
                f = pe_facts(data)
            elif kind in ("JAR", "CLASS") and "jar" not in DISABLED:
                f = jar_facts(data)
        except Exception as e:  # noqa: BLE001
            log(f"[!] facts({kind}): {e!r}")
        ext = os.path.splitext(name)[1].lstrip(".").lower()
        if "format" not in f and kind in (None, "ZIP") and ext and ext not in ("zip", "bin", "dat", "raw", "blob"):
            f["format"] = ext   # UNCONFIRMED: unknown container -> member extension (bare lowercase family law)
        elif "format" not in f and kind:
            f["format"] = BINARY_FORMAT.get(kind) or GUESS_FORMAT.get(kind, kind.lower())
        f.setdefault("kind", kind)
        _FACTS[k] = f
    return _FACTS[k]


def fmt(v):
    if v is None:
        return "none"
    if isinstance(v, (list, dict)):
        return json.dumps(v, separators=(",", ":"), ensure_ascii=False)
    return str(v)


CONFIG_META = {"xor_key_hex", "hcfg_xor_key_hex", "xor_key", "key", "config_crc32_hex", "config_crc32", "crc32_hex",
               "crc32", "hcfg_version", "config_version", "config_length", "hcfg_length", "config_xor_key_hex"}


def config_answer(f, members):
    """HCFG-derived field, searching the given members (first binary first)."""
    h = None
    for _, b in sorted(members, key=lambda nb: not is_binary(nb[1])):
        h = hunt_hcfg(b)
        if h:
            break
    if not h:
        return "none"
    if f in ("xor_key_hex", "hcfg_xor_key_hex", "config_xor_key_hex"):
        return f"0x{h['key']:02x}"
    if f in ("xor_key", "key"):          # Day 2 legacy id: Python hex() (GM-confirmed spelling there)
        return hex(h["key"])
    if f in ("config_crc32_hex", "config_crc32", "crc32_hex", "crc32"):
        return f"0x{h['crc']:08x}"
    if f in ("hcfg_version", "config_version"):
        return str(h["version"]) if h.get("version") is not None else "none"
    if f in ("config_length", "hcfg_length"):
        return str(h["length"])
    key = f[len("config_"):] if f.startswith("config_") else f
    cfg = h.get("config") or {}
    return fmt(cfg.get(key)) if key in cfg else "none"


def cpp_facts(fx, data):
    """Day 2 C++ facts without c++filt."""
    names = [s[0] for s in fx.get("_syms", [])]
    own = lambda n: "__cxxabiv1" not in n and not re.match(r"_ZT[VIS](N?St|Ss|Sa|Si|So|Sd)", n)
    vt = list(dict.fromkeys(n for n in names if (n.startswith("_ZTV") or n.startswith("??_7")) and own(n)))

    def nested(name):
        m = re.match(r"_ZN[KVRO]*", name)
        if not m:
            return []
        i, parts = m.end(), []
        while i < len(name) and name[i].isdigit():
            n = re.match(r"\d+", name[i:]).group(0)
            i += len(n)
            parts.append(name[i:i + int(n)])
            i += int(n)
        return parts if name[i:i + 1] == "E" else []
    score = list(dict.fromkeys(n for n in names if re.match(r"\?score@", n) or nested(n)[-1:] == ["score"]))
    for sc in score:
        p = nested(sc)
        if len(p) >= 2:
            cls = f"_ZTV{len(p[-2])}{p[-2]}"
            vt.sort(key=lambda n: n != cls)
            break
    return {"vtable": vt, "score": score,
            "has_vt": bool(vt) or b"??_7" in data or b"_ZTV" in data,
            "has_ti": any(n.startswith(("_ZTI", "_ZTS")) and own(n) for n in names) or b".?AV" in data or b"_ZTI" in data}


def recover_code(fx, q, fallback_stripped):
    m = re.search(r"returned by\s+`?([A-Za-z_]\w*)", (q or {}).get("question", ""))
    fname = m.group(1) if m else "recover_code"
    syms = fx.get("_syms", [])
    sym = next((s for s in syms if s[0] == fname and s[4]), None)
    if sym is None and m and not any(s[0] == fname for s in syms) and not fallback_stripped:
        return "none"   # Day 1: the named function is absent (stripped / other profile) -> none
    if sym is None:
        if fallback_stripped:
            v = _stripped_leaf_const(fx.get("_text"))
            return str(v) if v is not None else "none"
        d = fx.get("exported_symbol")
        sym = next((s for s in syms if s[0] == d and s[4]), None)
        if sym is None:
            return "none"
    off = fx["_va2off"](sym[1])
    if off is None or not fx.get("_md"):
        return "none"
    return None, off, sym   # resolved by caller (needs raw bytes)


def field_answer(field, sel, group, q, legacy):
    """field: normalized field name; sel: (name, bytes) primary member; group: [(name, bytes)]."""
    name, data = sel
    if field in ("sha256", "artifact_sha256"):
        return sha(data)
    if field.startswith("config_") or field in CONFIG_META:
        return config_answer(field, group)
    if legacy and field not in ELF_LIKE:   # Day 2 bare config keys; unknown bare ids stay unanswered (worker residue)
        r = config_answer(field, group)
        if r != "none" or field in ("campaign", "domain", "url", "mutex"):
            return r
    fx = facts(data, name)
    if field == "disassembly":
        return fmt(fx["_disasm"]()) if "_disasm" in fx else "none"
    if field == "recover_code":
        r = recover_code(fx, q, fallback_stripped=legacy == "c")
        if isinstance(r, tuple):
            _, off, sym = r
            v = _ret_const(fx["_md"](), data[off:off + (sym[2] or 64)], sym[1])
            return str(v) if v is not None else "none"
        return r
    if field in ("has_cpp_vtable", "has_cpp_typeinfo", "mangled_score_symbol", "vtable_symbol"):
        cf = cpp_facts(fx, data)
        pe = fx.get("kind") == "PE"
        if field == "has_cpp_vtable":
            return "true" if cf["has_vt"] else "false"
        if field == "has_cpp_typeinfo":
            return "true" if cf["has_ti"] else "false"
        if field == "mangled_score_symbol":   # GM-confirmed: PE (MinGW) -> COMDAT section-name form
            return ((".text$" if pe else "") + cf["score"][0]) if cf["score"] else "none"
        return ((".rdata$" if pe else "") + cf["vtable"][0]) if cf["vtable"] else "none"
    if field in fx and not field.startswith("_"):
        return fmt(fx[field])
    return None


ELF_LIKE = {"elf_class", "endianness", "machine", "elf_type", "marker", "has_symtab", "exported_symbol",
            "entry_point", "recover_code", "format", "sha256", "has_cpp_vtable", "has_cpp_typeinfo",
            "mangled_score_symbol", "vtable_symbol", "architecture", "section_names", "symbols", "disassembly",
            "metadata_version"}


def group_of(members, day):
    rx = re.compile(rf"(^|/){re.escape(day)}(?!\d)", re.I)
    return [(n, b) for n, b in members if rx.search(n)]


def slot_member(members, k, base):
    for rx in (rf"slot[^a-z0-9]*0*{k}(?!\d)", rf"(?<!\d)0*{k}(?!\d)"):
        hit = [m for m in members if re.search(rx, os.path.basename(m[0]).lower())]
        if len(hit) == 1:
            return hit[0]
    i = k - base
    return members[i] if 0 <= i < len(members) else None


def is_cpp(name, data):
    b = os.path.basename(name).lower()
    if re.search(r"(^|[^a-z])(cpp|cxx|c\+\+)([^a-z]|$)", b):
        return True
    if re.search(r"(^|[^a-z])c([^a-z]|$)", b):
        return False
    return b"_ZTV" in data or b".?AV" in data or b"HCFG" in data


def solve(contract, adir):
    qs = contract.get("questions") or []
    ids = contract.get("answer_ids") or [q.get("id") for q in qs]
    byid = {q.get("id"): q for q in qs}
    ev = Evidence(adir, contract)
    slot_base = 0 if any(re.match(r"(set\d+\.)?slot0_", a or "") for a in ids) else 1
    out = {}
    for i, aid in enumerate(ids):
        q = byid.get(aid) or (qs[i] if i < len(qs) and len(qs) == len(ids) else None)
        if q is None:   # Day 1 variant: answer ids 'slotN_x' share one question 'x'
            base = aid.rpartition(".")[2]
            q = next((x for x in qs if x.get("id") and base.endswith(x["id"].split(".")[-1])), {}) or {}
        path = ev.resolve(q.get("artifact") or "evidence.zip")
        if not path:
            log(f"[!] {aid}: artifact {q.get('artifact')!r} not delivered -> skip")
            continue
        mem = ev.members(path)
        base = aid.rpartition(".")[2]
        try:
            v = route(base, mem, q, slot_base)
        except Exception as e:  # noqa: BLE001
            log(f"[!] {aid}: {e!r}")
            v = None
        if v is None:
            log(f"[!] {aid}: unanswered")
            continue
        norm = q.get("normalization")
        out[aid] = v.strip().lower() if norm == "case_insensitive" else v.strip() if norm == "trim" else v
    return out


def route(base, mem, q, slot_base):
    m = re.match(r"(d\d+)_(.+)$", base)
    if m:   # Day 3+ grammar
        day, field = m.groups()
        group = group_of(mem, day) or ([x for x in mem if is_binary(x[1])][:1] if len(mem) == 1 else [])
        if not group:
            log(f"[!] no members for {day}")
            return None
        k = re.fullmatch(r"artifact_sha256_(\d+)", field)
        if k:
            n = int(k.group(1))
            return sha(group[n - 1][1]) if len(group) >= n else "none"
        field = field[len("analysis_"):] if field.startswith("analysis_") else field
        bins = [x for x in group if is_binary(x[1])]
        return field_answer(field, (bins or group)[0], group, q, legacy=None)
    if "legacy" in DISABLED:
        return None
    bins = [x for x in mem if is_binary(x[1])]
    m = re.match(r"slot(\d+)_(.+)$", base)
    if m:   # Day 1 TT: slot-K.elf
        sel = slot_member(bins, int(m.group(1)), slot_base)
        return field_answer(m.group(2), sel, [sel], q, legacy="slot") if sel else None
    m = re.match(r"(cpp|c)_(.+)$", base)
    tagged = [(n, b, is_cpp(n, b)) for n, b in bins]
    if m:   # Day 2: c_* / cpp_*
        want_cpp = m.group(1) == "cpp"
        pick = [(n, b) for n, b, cp in tagged if cp == want_cpp]
        if not pick:
            return None
        return field_answer(m.group(2), pick[0], pick[:1], q, legacy=m.group(1))
    # bare legacy id (Day 1 single / Day 2 config + cpp facts): config & C++ facts live in the C++ build if any
    order = sorted(tagged, key=lambda t: not t[2]) if len(tagged) > 1 else tagged
    if not order:
        return None
    sel = order[0][:2]
    return field_answer(base, sel, [sel], q, legacy="bare")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    with open(a.contract) as fh:
        c = json.load(fh)
    out = solve(c, a.artifacts)
    print(json.dumps(out))
    if not out:
        sys.exit(1)


if __name__ == "__main__":
    main()
