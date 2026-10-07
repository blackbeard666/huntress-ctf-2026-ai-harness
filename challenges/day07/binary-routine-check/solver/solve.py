#!/usr/bin/env python3
"""Composite binary solver (Day 07 binary "Routine Check" / kotlin-staging-logic; extends Days 01-06).

Day 07: `d07--*.jar` is a Kotlin fat jar (~3100 runtime classes); same base64 HCFG constant in the main class.

evidence.zip (AES, pw 'infected') holds one group of members per day-prefix: `d01--*.elf` (Day 1 C build),
`d02--*.elf|exe` (Day 2 C++ build with an HCFG config), `d03--*.dll` + `d03--*.runtimeconfig.json` (.NET assembly
whose HCFG config sits in a <PrivateImplementationDetails> FieldRVA static array), `d04--*.elf` (static Go build,
go1.25 buildinfo, HCFG blob in rodata), `d05--*.elf` (Rust ELF, HCFG in rodata), `d06--*.jar` (Java jar whose
main class keeps the HCFG blob BASE64'd in a constant-pool String: `static final String CONFIG`, decoded by
decodeConfig(): checks 'HCFG', key = b[5], len = b[6]|b[7]<<8, plain[i] = b[12+i] ^ key). Answer ids are
`dNN_artifact_sha256_K` / `dNN_analysis_<field>`, with `setN.` prefixes in Mastery (`delivery N: evidence.zip`).

  artifact_sha256_K        sha256 of the K-th member of group dNN (archive order)
  analysis_elf_class       ELF64/ELF32                          (GM-confirmed)
  analysis_endianness      little/big                           (GM-confirmed)
  analysis_machine         ELF: x86-64; PE i386 -> "i386"       (both GM-confirmed)
  analysis_architecture    container machine, same vocabulary (Go ELF amd64 -> "x86-64" GM-confirmed Day 4;
                           the buildinfo GOARCH "amd64" was REJECTED)
  analysis_elf_type        e_type as-is (ET_EXEC)               (GM-confirmed)
  analysis_section_names   pyelftools iter_sections() names INCLUDING the empty NULL section name (GM-confirmed)
  analysis_symbols         non-empty .symtab names, table order, duplicates kept (GM-confirmed)
  analysis_disassembly     capstone intel of recover_code, decimal immediates (GM-confirmed)
  analysis_format          ELF -> elf (confirmed, Go too); native PE -> pe (Day 2); .NET -> pe_cli (Day 3)
  analysis_metadata_version  CLI metadata root version string (v4.0.30319, GM-confirmed)
  analysis_config_<key>    key of the decoded HCFG JSON config ('HCFG' u8 ver, u8 xor, u16 len, u32 crc32, xor'd JSON)
  analysis_config_crc32_hex  crc32 of the decoded config, 0x%08x
  analysis_xor_key_hex     HCFG xor key, 0x%02x
  analysis_hcfg_version    HCFG header version byte (b[4]), base-10
  analysis_format          jar -> JAR_FORMAT (see knowledge.py)
"""
import argparse, hashlib, io, json, os, re, struct, sys, zipfile, zlib

from elftools.elf.elffile import ELFFile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    from lib import knowledge as K
except ImportError:  # pragma: no cover
    K = None

PASSWORDS = [b"infected", b"flare", b"malware", b"virus", b"huntress"]
ELF_MACHINE = {"EM_X86_64": "x86-64", "EM_386": "x86", "EM_AARCH64": "AArch64", "EM_ARM": "ARM"}
PE_MACHINE = {0x14c: "i386", 0x8664: "x86-64", 0xaa64: "AArch64", 0x1c0: "ARM"}   # 0x14c "i386" GM-confirmed (Day 3)
# .NET assembly `format`: "pe_cli" (GM-confirmed Day 3).
DOTNET_FORMAT = getattr(K, "DOTNET_FORMAT", "pe_cli")
JAR_FORMAT = getattr(K, "JAR_FORMAT", "jar")
NESTED_OK = (".jar", ".war", ".ear", ".aar", ".apk", ".docx", ".xlsx", ".pptx")   # keep these members whole


def log(*a):
    print(*a, file=sys.stderr)


# ---------- archive ----------

def unzip(data):
    """[(name, bytes)] of every member, archive order, recursing into nested zips (AES or legacy)."""
    if data[:2] != b"PK":
        return [("", data)]
    readers = []
    try:
        import pyzipper
        readers.append(pyzipper.AESZipFile)
    except ImportError:
        pass
    readers.append(zipfile.ZipFile)
    best, err = [], None
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
                            if pw:
                                z.setpassword(pw)
                            b = z.read(i.filename)
                            break
                        except Exception as e:  # noqa: BLE001
                            err = e
                    if b is None:
                        complete = False
                        continue
                    nest = b[:2] == b"PK" and not i.filename.lower().endswith(NESTED_OK)
                    out += [(n or i.filename, x) for n, x in unzip(b)] if nest else [(i.filename, b)]
                if complete and out:
                    return out
                if len(out) > len(best):
                    best = out
        except Exception as e:  # noqa: BLE001
            err = e
    if not best:
        log(f"[!] cannot read zip ({err})")
    return best


def find_artifact(adir, name):
    cands = [name, os.path.basename(name), name.split(":", 1)[-1].strip()]
    files = sorted(os.path.join(r, f) for r, _, fs in os.walk(adir) for f in fs if f != "manifest.json")
    m = re.search(r"delivery\s*(\d+)", name, re.I)
    if m:   # 'delivery N: evidence.zip' -> prefer a path mentioning delivery N, else the N-th zip
        n = int(m.group(1))
        hit = [p for p in files if re.search(rf"(delivery|set)[^0-9]*0*{n}(?!\d)", p, re.I)]
        if len(hit) == 1:
            return hit[0]
    for c in cands:
        for p in files:
            if os.path.basename(p) == c and not m:
                return p
    zips = [p for p in files if p.lower().endswith(".zip")]
    if m and len(zips) >= int(m.group(1)):
        return zips[int(m.group(1)) - 1]
    for c in cands:
        for p in files:
            if os.path.basename(p) == c:
                return p
    return files[0] if len(files) == 1 else None


def group_members(members, day):
    """Members belonging to group 'd01' etc.: name starts with the prefix (d01--x, d01_x, d01-x)."""
    rx = re.compile(rf"(^|/){re.escape(day)}(?!\d)", re.I)
    return [(n, b) for n, b in members if rx.search(n)]


def is_binary(b):
    return (b[:4] in (b"\x7fELF", b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe")
            or b[:2] == b"MZ" or is_jar(b))


def is_jar(b):
    if b[:2] != b"PK":
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            return any(n.endswith(".class") or n == "META-INF/MANIFEST.MF" for n in z.namelist())
    except Exception:  # noqa: BLE001
        return False


# ---------- config ----------

def hcfg(data, fallback=True):
    for m in re.finditer(rb"HCFG", data):
        o = m.start()
        if o + 12 > len(data):
            continue
        ver, key, n, crc = struct.unpack_from("<BBHI", data, o + 4)
        plain = bytes(b ^ key for b in data[o + 12:o + 12 + n])
        if zlib.crc32(plain) == crc or plain[:1] == b"{":
            try:
                cfg = json.loads(plain.decode())
            except Exception:
                cfg = None
            return {"key": key, "crc": zlib.crc32(plain), "config": cfg, "version": ver}
    if not fallback:
        return None
    for k in range(1, 256):   # fallback: xor'd JSON without a header
        pat = bytes([ord("{") ^ k, ord('"') ^ k])
        for m in re.finditer(re.escape(pat), data):
            end = data.find(bytes([ord("}") ^ k]), m.start())
            while end != -1:
                plain = bytes(b ^ k for b in data[m.start():end + 1])
                try:
                    return {"key": k, "crc": zlib.crc32(plain), "config": json.loads(plain.decode())}
                except Exception:
                    end = data.find(bytes([ord("}") ^ k]), end + 1)
    return None


# ---------- java ----------

def class_constants(cls):
    """JVM class-file constant pool -> [(tag, bytes)] for Utf8 (1) / Integer (3) / Long (5) entries, pool order."""
    if cls[:4] != b"\xca\xfe\xba\xbe" or len(cls) < 10:
        return []
    n = struct.unpack_from(">H", cls, 8)[0]
    o, i, out = 10, 1, []
    size = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 16: 2, 19: 2, 20: 2, 9: 4, 10: 4, 11: 4, 12: 4, 17: 4, 18: 4, 15: 3}
    try:
        while i < n:
            t = cls[o]
            o += 1
            if t == 1:
                ln = struct.unpack_from(">H", cls, o)[0]
                out.append((1, cls[o + 2:o + 2 + ln]))
                o += 2 + ln
            elif t in size:
                if t in (3, 5):
                    out.append((t, cls[o:o + size[t]]))
                o += size[t]
                i += t in (5, 6)   # long/double take two slots
            else:
                break
            i += 1
    except (IndexError, struct.error):
        pass
    return out


def clinit_byte_arrays(cls):
    """Byte arrays built element-wise in bytecode (dup; push idx; push val; bastore) -> [bytes]."""
    push = rb"(?:[\x02-\x08]|\x10.|\x11..)"
    run = re.compile(rb"(?:\x59" + push + push + rb"\x54)+", re.S)
    elem = re.compile(rb"\x59(" + push + rb")(" + push + rb")\x54", re.S)

    def val(p):
        if p[0] == 0x10:
            return struct.unpack(">b", p[1:2])[0]
        if p[0] == 0x11:
            return struct.unpack(">h", p[1:3])[0]
        return p[0] - 3

    arrays = []
    for m in run.finditer(cls):
        arr = {}
        for e in elem.finditer(m.group(0)):
            arr[val(e.group(1))] = val(e.group(2)) & 0xff
        if len(arr) >= 12 and set(arr) == set(range(len(arr))):
            arrays.append(bytes(arr[k] for k in range(len(arr))))
    return arrays


def decodings(s):
    """Plausible byte decodings of a constant-pool string: raw, base64 (std/url, also reversed), hex."""
    import base64, binascii
    t = re.sub(rb"\s+", b"", s)
    outs = [s]
    for cand in (t, t[::-1]):
        if len(cand) >= 16 and re.fullmatch(rb"[A-Za-z0-9+/_-]+={0,2}", cand):
            for dec in (base64.b64decode, base64.urlsafe_b64decode):
                try:
                    outs.append(dec(cand + b"=" * (-len(cand) % 4)))
                except (binascii.Error, ValueError):
                    pass
        if len(cand) >= 24 and len(cand) % 2 == 0 and re.fullmatch(rb"[0-9a-fA-F]+", cand):
            outs.append(bytes.fromhex(cand.decode()))
    return outs


def jar_classes(data):
    """[(name, bytes)] of the .class entries of a jar (nested jars flattened), archive order."""
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


def jar_hcfg(data):
    """HCFG config hidden in a jar: constant-pool strings (base64/hex/raw), then bytecode-built arrays, then raw.
    Main class first, bundled runtimes (kotlin/, org/jetbrains/, ...) last; returns at the first decoded config
    (a Kotlin fat jar carries ~3000 runtime classes)."""
    classes = jar_classes(data)
    main = (jar_main_class(data) or "").replace(".", "/") + ".class"
    lib_rx = re.compile(r"^(META-INF/|kotlin/|kotlinx/|org/jetbrains/|org/intellij/|java/|javax/)")
    classes.sort(key=lambda nb: (nb[0] != main, bool(lib_rx.match(nb[0]))))
    blobs = []
    for _, cls in classes:
        cb = []
        utf8 = [v for t, v in class_constants(cls) if t == 1]
        for s in utf8:
            cb += decodings(s)
        b64 = [s for s in utf8 if re.fullmatch(rb"[A-Za-z0-9+/=_-]{8,}", s)]
        if len(b64) > 1:   # a blob split across several constants
            cb += decodings(b"".join(b64))
        cb += clinit_byte_arrays(cls)
        cb.append(cls)
        for b in cb:
            h = hcfg(b, fallback=False)
            if h and h["config"] is not None:
                return h
        blobs += cb
    blobs.append(data)
    for b in blobs:
        h = hcfg(b)
        if h:
            return h
    return None


def jar_facts(data):
    classes = [(n, b) for n, b in jar_classes(data) if not n.startswith(("kotlin/", "META-INF/"))]
    majors = [struct.unpack_from(">H", c, 6)[0] for _, c in classes if len(c) >= 8]
    return {
        "format": JAR_FORMAT,
        "main_class": jar_main_class(data),
        "class_names": [n for n, _ in classes],
        "class_major_version": max(majors) if majors else None,
    }


# ---------- binary facts ----------

def cli_metadata_version(data):
    """Version string of the CLI metadata root ('BSJB' u16 major u16 minor u32 reserved u32 len, version)."""
    for m in re.finditer(rb"BSJB", data):
        o = m.start()
        n = struct.unpack_from("<I", data, o + 12)[0]
        if 0 < n <= 256:
            return data[o + 16:o + 16 + n].split(b"\0", 1)[0].decode("ascii", "replace")
    return None


def disassembly(elf, data):
    """CONFIRMED (GM accepted ["mov eax, 8100","ret"] for recover_code): capstone intel mnemonic+op_str, keep the
    default ', ' separator, but render immediates in DECIMAL (0x1fa4 -> 8100). Just the recover_code leaf, up to its ret.
    Refuted earlier: hex immediates, no-space-after-comma, 'ret '/trailing space, main by size, whole .text, _start..hlt."""
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_MODE_32
    md = Cs(CS_ARCH_X86, CS_MODE_64 if elf.elfclass == 64 else CS_MODE_32)
    text = elf.get_section_by_name(".text")
    if text is None:
        return []
    tdata, taddr = text.data(), text["sh_addr"]
    start, size = None, None
    st = elf.get_section_by_name(".symtab")
    if st is not None:
        s = st.get_symbol_by_name("recover_code")
        if s:
            start, size = s[0]["st_value"], s[0]["st_size"]
    if start is None:   # stripped: last leaf `mov eax, imm32; ret`
        hits = [m.start() for m in re.finditer(rb"\xb8.{4}\xc3", tdata, re.S)]
        if not hits:
            return []
        start, size = taddr + hits[-1], 6
    off = start - taddr
    out = []
    for i in md.disasm(tdata[off:off + (size or 64)], start):
        op = re.sub(r"0x[0-9a-fA-F]+", lambda m: str(int(m.group(0), 16)), i.op_str)
        out.append(f"{i.mnemonic} {op}".strip())
        if i.mnemonic.startswith("ret"):
            break
    return out


def elf_facts(data):
    elf = ELFFile(io.BytesIO(data))
    h = elf.header
    st = elf.get_section_by_name(".symtab")
    return {
        "format": "elf",
        "elf_class": {"ELFCLASS32": "ELF32", "ELFCLASS64": "ELF64"}.get(h["e_ident"]["EI_CLASS"], h["e_ident"]["EI_CLASS"]),
        "endianness": {"ELFDATA2LSB": "little", "ELFDATA2MSB": "big"}.get(h["e_ident"]["EI_DATA"], h["e_ident"]["EI_DATA"]),
        "machine": ELF_MACHINE.get(h["e_machine"], h["e_machine"]),
        "architecture": ELF_MACHINE.get(h["e_machine"], h["e_machine"]),
        "elf_type": h["e_type"],
        "entry_point": hex(h["e_entry"]),
        "section_names": [s.name for s in elf.iter_sections()],
        "symbols": [s.name for s in st.iter_symbols() if s.name] if st is not None else [],
        "_disasm": lambda: disassembly(elf, data),
    }


def pe_facts(data):
    import pefile
    pe = pefile.PE(data=data, fast_load=True)
    mdv = cli_metadata_version(data)
    clr = pe.OPTIONAL_HEADER.DATA_DIRECTORY[14].VirtualAddress if len(pe.OPTIONAL_HEADER.DATA_DIRECTORY) > 14 else 0
    dotnet = bool(clr) and mdv is not None
    return {
        "format": DOTNET_FORMAT if dotnet else "pe",
        "machine": PE_MACHINE.get(pe.FILE_HEADER.Machine, hex(pe.FILE_HEADER.Machine)),
        "architecture": PE_MACHINE.get(pe.FILE_HEADER.Machine, hex(pe.FILE_HEADER.Machine)),
        "metadata_version": mdv,
        "entry_point": hex(pe.OPTIONAL_HEADER.ImageBase + pe.OPTIONAL_HEADER.AddressOfEntryPoint),
        "section_names": [s.Name.rstrip(b"\0").decode(errors="replace") for s in pe.sections],
    }


def facts(data):
    if data[:4] == b"\x7fELF":
        return elf_facts(data)
    if data[:2] == b"MZ":
        return pe_facts(data)
    if is_jar(data) or data[:4] == b"\xca\xfe\xba\xbe":
        return jar_facts(data)
    return {}


# ---------- answers ----------

def fmt(v):
    if v is None:
        return "none"
    if isinstance(v, (list, dict)):
        return json.dumps(v, separators=(",", ":"), ensure_ascii=False)
    return str(v)


def answer(field, group, q):
    m = re.fullmatch(r"artifact_sha256_(\d+)", field)
    if m:
        k = int(m.group(1))
        return hashlib.sha256(group[k - 1][1]).hexdigest() if len(group) >= k else "none"
    if not field.startswith("analysis_"):
        return None
    f = field[len("analysis_"):]
    binaries = [b for _, b in group if is_binary(b)]
    blob = binaries[0] if binaries else (group[0][1] if group else b"")
    if f.startswith("config_") or f in ("xor_key_hex", "hcfg_version", "hcfg_xor_key_hex"):
        h = None
        for _, b in group:
            h = jar_hcfg(b) if (is_jar(b) or b[:4] == b"\xca\xfe\xba\xbe") else hcfg(b)
            if h:
                break
        if not h:
            return "none"
        if f in ("xor_key_hex", "hcfg_xor_key_hex"):
            return f"0x{h['key']:02x}"
        if f == "hcfg_version":
            return str(h["version"]) if h.get("version") is not None else "none"
        if f == "config_crc32_hex":
            return f"0x{h['crc']:08x}"
        key = f[len("config_"):]
        v = (h["config"] or {}).get(key)
        return fmt(v)
    fx = facts(blob)
    if f == "disassembly":
        return fmt(fx["_disasm"]()) if "_disasm" in fx else "none"
    if f in fx:
        return fmt(fx[f])
    log(f"[!] unknown field {field}")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    c = json.load(open(a.contract))
    qs = c.get("questions", [])
    ids = c.get("answer_ids") or [q["id"] for q in qs]
    qmap = {q.get("id"): q for q in qs}
    cache, out = {}, {}
    for i, aid in enumerate(ids):
        q = qmap.get(aid) or (qs[i] if i < len(qs) else {})
        prefix, _, base = aid.rpartition(".")
        m = re.match(r"(d\d+)_(.+)$", base)
        if not m:
            log(f"[!] skip {aid}")
            continue
        day, field = m.groups()
        art = q.get("artifact") or "evidence.zip"
        if art not in cache:
            p = None
            try:   # pair same-named per-set deliveries by the contract's sha256 first
                from lib.common import container_by_sha
                p = container_by_sha(a.artifacts, c, art)
            except Exception:  # noqa: BLE001
                p = None
            p = str(p) if p else find_artifact(a.artifacts, art)
            if not p:
                log(f"[!] artifact {art} not found")
                continue
            cache[art] = unzip(open(p, "rb").read())
            log(f"[*] {art} -> {p}: {[n for n, _ in cache[art]]}")
        group = group_members(cache[art], day)
        if not group:
            log(f"[!] no members for {day} in {art}")
            continue
        try:
            v = answer(field, group, q)
        except Exception as e:  # noqa: BLE001
            log(f"[!] {aid}: {e!r}")
            continue
        if v is not None:
            out[aid] = v.strip() if q.get("normalization") == "trim" else v
    print(json.dumps(out))


if __name__ == "__main__":
    main()
