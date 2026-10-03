#!/usr/bin/env python3
"""C++ orientation solver (Day 02 binary "Mangled").

evidence.zip (AES, pw 'infected') holds a plain C build (`*c.elf`) and a C++ build (`*cpp.elf`, maybe PE in variants).
Answer ids are `<prefix>_<field>` (c_*, cpp_*) or bare config fields; Mastery adds `setN.`.

  c_sha256 / cpp_sha256   sha256 of the member
  c_marker                .huntress section string (up to NUL)
  c_has_symtab            .symtab present (PE: COFF symbol table non-empty)
  c_recover_code          immediate returned by `recover_code` (mov eax, imm; ret); stripped -> leaf b8 imm32 c3 in .text
  c_machine               ELF e_machine in GM vocabulary (x86-64 confirmed)
  cpp_xor_key             HCFG blob: 'HCFG' u8 ver, u8 xor key, u16 len, u32 crc32(plaintext), xored JSON
  cpp_config_crc32        crc32 of the decoded config (== header crc)
  campaign/domain/url/... keys of the decoded JSON config (absent -> none)
  has_cpp_vtable          any vtable symbol (_ZTV / ??_7) or vtable RTTI
  has_cpp_typeinfo        any typeinfo (_ZTI/_ZTS) or MSVC type descriptor (.?AV)
  mangled_score_symbol    mangled symbol whose demangled name is <Class>::score(...)
  vtable_symbol           mangled vtable symbol of the program's own class (not __cxxabiv1); PE variants are MinGW: names come from the COFF symbol table
  cpp_format              container format, lowercase: "elf" (GM-confirmed; rejected ELF, ELF64, HCFG, elf64-x86-64, json); PE -> "pe" by analogy
"""
import argparse, hashlib, io, json, os, re, struct, subprocess, sys, zipfile, zlib

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

PASSWORDS = [b"infected", b"flare", b"malware", b"virus"]
MACHINE_NAMES = {"EM_X86_64": "x86-64", "EM_386": "x86", "EM_AARCH64": "AArch64", "EM_ARM": "ARM"}
PE_MACHINE = {0x8664: "x86-64", 0x14c: "x86", 0xaa64: "AArch64", 0x1c0: "ARM"}
# cpp_format: GM wants the lowercase container name ("elf" confirmed Day 02; "pe" follows the same scheme).
FORMAT_NAMES = {"ELF": "elf", "PE": "pe", "MACHO": "macho"}


def log(*a):
    print(*a, file=sys.stderr)


def unzip(data):
    """[(name, bytes)] of every member, recursing into nested zips; AES zips via pyzipper."""
    if data[:2] != b"PK":
        return [("", data)]
    try:
        import pyzipper
        Z = pyzipper.AESZipFile
    except ImportError:
        Z = zipfile.ZipFile
    out = []
    with Z(io.BytesIO(data)) as z:
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
                except Exception:
                    continue
            if b is None:
                log(f"[!] cannot read {i.filename}")
                continue
            out += [(n or i.filename, x) for n, x in unzip(b)] if b[:2] == b"PK" else [(i.filename, b)]
    return out


def find_artifact(adir, name):
    cands = [name, os.path.basename(name), name.split(":", 1)[-1].strip()]
    files = [os.path.join(r, f) for r, _, fs in os.walk(adir) for f in fs if f != "manifest.json"]
    for c in cands:
        for p in files:
            if os.path.basename(p) == c:
                return p
    m = re.search(r"delivery\s*(\d+)", name, re.I)
    zips = sorted(p for p in files if p.lower().endswith(".zip"))
    if m and len(zips) >= int(m.group(1)):
        return zips[int(m.group(1)) - 1]
    return files[0] if len(files) == 1 else None


# ---------- per-binary facts ----------

def demangle(names):
    try:
        r = subprocess.run(["c++filt"], input="\n".join(names), capture_output=True, text=True, timeout=10)
        d = r.stdout.splitlines()
        if len(d) == len(names):
            return dict(zip(names, d))
    except Exception:
        pass
    return {n: n for n in names}


def elf_info(data):
    elf = ELFFile(io.BytesIO(data))
    syms = []
    for sec in elf.iter_sections():
        if isinstance(sec, SymbolTableSection):
            for s in sec.iter_symbols():
                if s.name:
                    syms.append((s.name.split("@")[0], s["st_value"], s["st_size"], s["st_info"]["type"],
                                 s["st_shndx"] != "SHN_UNDEF"))
    hs = elf.get_section_by_name(".huntress")

    def va2off(va):
        for seg in elf.iter_segments():
            if seg["p_type"] == "PT_LOAD" and seg["p_vaddr"] <= va < seg["p_vaddr"] + seg["p_filesz"]:
                return va - seg["p_vaddr"] + seg["p_offset"]
    return {
        "kind": "ELF", "bits": elf.elfclass,
        "machine": MACHINE_NAMES.get(elf["e_machine"], elf["e_machine"]), "e_machine": elf["e_machine"],
        "has_symtab": elf.get_section_by_name(".symtab") is not None,
        "marker": hs.data().split(b"\0", 1)[0].decode("utf-8", "replace") if hs else None,
        "syms": syms, "va2off": va2off,
        "text": elf.get_section_by_name(".text").data() if elf.get_section_by_name(".text") else None,
    }


def coff_symbols(pe, data):
    """MinGW PEs keep a COFF symbol table (18-byte entries + string table) with Itanium-mangled names."""
    fh = pe.FILE_HEADER
    ptr, n = fh.PointerToSymbolTable, fh.NumberOfSymbols
    if not ptr or not n or ptr + 18 * n > len(data):
        return []
    strtab = ptr + 18 * n
    secs = pe.sections
    out, i = [], 0
    while i < n:
        e = data[ptr + 18 * i:ptr + 18 * (i + 1)]
        raw, value, secno, typ, _cls, naux = struct.unpack("<8sIhHBB", e)
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


def pe_info(data):
    import pefile
    pe = pefile.PE(data=data, fast_load=False)
    syms = []
    exp = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
    for e in (exp.symbols if exp else []):
        if e.name:
            syms.append((e.name.decode(), pe.OPTIONAL_HEADER.ImageBase + e.address, 0, "STT_FUNC", True))
    syms += coff_symbols(pe, data)
    marker = None
    for s in pe.sections:
        if s.Name.rstrip(b"\0").decode(errors="replace").startswith(".huntres"):
            marker = s.get_data().split(b"\0", 1)[0].decode("utf-8", "replace")

    def va2off(va):
        try:
            return pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)
        except Exception:
            return None
    return {
        "kind": "PE", "bits": 64 if pe.FILE_HEADER.Machine in (0x8664, 0xaa64) else 32,
        "machine": PE_MACHINE.get(pe.FILE_HEADER.Machine, hex(pe.FILE_HEADER.Machine)), "e_machine": pe.FILE_HEADER.Machine,
        "has_symtab": pe.FILE_HEADER.PointerToSymbolTable != 0 and pe.FILE_HEADER.NumberOfSymbols > 0,
        "marker": marker, "syms": syms, "va2off": va2off,
        "text": next((x.get_data() for x in pe.sections if x.Name.rstrip(b"\0") == b".text"), None),
    }


def info(data):
    if data[:4] == b"\x7fELF":
        return elf_info(data)
    if data[:2] == b"MZ":
        return pe_info(data)
    raise ValueError("not ELF/PE")


def return_const(data, inf, name):
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_MODE_32
    sym = next((s for s in inf["syms"] if s[0] == name and s[4]), None)
    if sym is None:
        return stripped_return_const(data, inf)
    off = inf["va2off"](sym[1])
    if off is None:
        return None
    md = Cs(CS_ARCH_X86, CS_MODE_64 if inf["bits"] == 64 else CS_MODE_32)
    regs = {}
    for ins in md.disasm(data[off:off + (sym[2] or 64)], sym[1]):
        ops = ins.op_str.replace(" ", "")
        m = re.match(r"(\w+),(-?(?:0x[0-9a-f]+|\d+))$", ops)
        if ins.mnemonic in ("mov", "movabs") and m:
            regs[m.group(1)] = int(m.group(2), 0)
        elif ins.mnemonic == "xor" and re.match(r"(\w+),\1$", ops):
            regs[ops.split(",")[0]] = 0
        if ins.mnemonic in ("ret", "retq"):
            for r in ("eax", "rax"):
                if r in regs:
                    v = regs[r]
                    return v - 2**32 if 2**31 <= v < 2**32 else v
            return None
    return None


def stripped_return_const(data, inf):
    """Stripped build: no recover_code symbol. Find the leaf `mov eax, imm32; ret` (b8 imm32 c3) in the code
    section; main inlines the same immediate (`mov eax, imm; cmp ...`), which breaks ties between candidates."""
    code = inf.get("text")
    if not code:
        return None
    imms = [struct.unpack("<i", m.group(1))[0] for m in re.finditer(rb"\xb8(.{4})\xc3", code, re.S)]
    imms = list(dict.fromkeys(imms))
    if len(imms) > 1:
        inlined = [v for v in imms if len(re.findall(re.escape(b"\xb8" + struct.pack("<i", v)), code)) > 1]
        imms = inlined or imms
    if len(imms) != 1:
        log(f"[!] stripped recover_code: ambiguous candidates {imms}")
        return None
    log(f"[*] stripped binary: recover_code recovered from leaf mov eax,imm; ret -> {imms[0]}")
    return imms[0]


def hcfg(data):
    """Locate and decode the HCFG config blob. Returns dict(key, crc, config, raw) or None."""
    for m in re.finditer(rb"HCFG", data):
        o = m.start()
        if o + 12 > len(data):
            continue
        ver, key, n, crc = struct.unpack_from("<BBHI", data, o + 4)
        enc = data[o + 12:o + 12 + n]
        plain = bytes(b ^ key for b in enc)
        if zlib.crc32(plain) == crc or plain[:1] == b"{":
            try:
                cfg = json.loads(plain.decode())
            except Exception:
                cfg = None
            return {"key": key, "crc": zlib.crc32(plain), "hdr_crc": crc, "config": cfg, "raw": plain}
    # fallback: single-byte xor JSON anywhere ('{"' xored)
    for k in range(1, 256):
        pat = bytes([ord("{") ^ k, ord('"') ^ k])
        for m in re.finditer(re.escape(pat), data):
            end = data.find(bytes([ord("}") ^ k]), m.start())
            while end != -1:
                plain = bytes(b ^ k for b in data[m.start():end + 1])
                try:
                    cfg = json.loads(plain.decode())
                    return {"key": k, "crc": zlib.crc32(plain), "hdr_crc": None, "config": cfg, "raw": plain}
                except Exception:
                    end = data.find(bytes([ord("}") ^ k]), end + 1)
    return None


def cpp_facts(data, inf):
    names = [s[0] for s in inf["syms"]]
    dm = demangle(names)
    own = lambda n: "__cxxabiv1" not in n and "std::" not in dm.get(n, n)
    vt = [n for n in names if (n.startswith("_ZTV") or n.startswith("??_7")) and own(n)]
    ti = [n for n in names if n.startswith(("_ZTI", "_ZTS")) and own(n)]
    score = [n for n in names if re.search(r"::score\(", dm.get(n, "")) or re.match(r"\?score@", n)]
    has_vt = bool(vt) or b"??_7" in data or b"_ZTV" in data
    has_ti = bool(ti) or b".?AV" in data or b"_ZTI" in data
    # prefer the vtable of the class that owns score(): _ZNK15DiscoveryEngine5score... -> _ZTV15DiscoveryEngine
    for sc in score:
        m = re.match(r"_ZN[KVR]*(\d+)", sc)
        if m:
            cls = sc[len(m.group(0)) - len(m.group(1)):][:len(m.group(1)) + int(m.group(1))]
            vt.sort(key=lambda n: n != "_ZTV" + cls)
            break
    vt = list(dict.fromkeys(vt))
    return {"vtable": vt, "typeinfo": ti, "score": score, "has_vt": has_vt, "has_ti": has_ti}


def is_cpp(name, data):
    b = os.path.basename(name).lower()
    if re.search(r"(^|[^a-z])(cpp|cxx|c\+\+)([^a-z]|$)", b):
        return True
    if re.search(r"(^|[^a-z])c([^a-z]|$)", b):
        return False
    return b"_ZTV" in data or b".?AV" in data or b"HCFG" in data


# ---------- answers ----------

def answer(field, prefix, members, q):
    """field e.g. 'sha256', prefix 'c'/'cpp'/'' -> string or None."""
    fmt = (q.get("answer_format") or {})
    if prefix == "c":
        pick = [m for m in members if not m[2]]
    elif prefix == "cpp":
        pick = [m for m in members if m[2]]
    else:
        pick = sorted(members, key=lambda m: not m[2])  # config fields live in the C++ build
    if not pick:
        return None
    name, data, _cpp = pick[0]
    if field == "sha256":
        return hashlib.sha256(data).hexdigest()
    inf = info(data)
    if field == "marker":
        return inf["marker"] or "none"
    if field == "has_symtab":
        return "true" if inf["has_symtab"] else "false"
    if field == "machine":
        return inf["machine"]
    if field == "recover_code":
        v = return_const(data, inf, "recover_code")
        return str(v) if v is not None else ("none" if fmt.get("kind") != "integer" else None)
    if field == "format":
        return FORMAT_NAMES.get(inf["kind"], inf["kind"].lower())
    cfg = hcfg(data)
    if field in ("xor_key", "key"):
        return hex(cfg["key"]) if cfg else "none"
    if field in ("config_crc32", "crc32"):
        return f"0x{cfg['crc']:08x}" if cfg else "none"
    cf = cpp_facts(data, inf)
    if field == "has_cpp_vtable":
        return "true" if cf["has_vt"] else "false"
    if field == "has_cpp_typeinfo":
        return "true" if cf["has_ti"] else "false"
    if field == "mangled_score_symbol":
        return cf["score"][0] if cf["score"] else "none"
    if field == "vtable_symbol":
        return cf["vtable"][0] if cf["vtable"] else "none"
    if cfg and cfg["config"] is not None:
        v = cfg["config"].get(field)
        if v is not None:
            return str(v)
        return "none"
    return None


def split_id(aid):
    """'set2.cpp_xor_key' -> (set 'set2', prefix 'cpp', field 'xor_key')."""
    s, _, rest = aid.rpartition(".")
    for p in ("cpp", "c"):
        if rest.startswith(p + "_"):
            return s, p, rest[len(p) + 1:]
    return s, "", rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    c = json.load(open(a.contract))
    qs = c.get("questions") or []
    ids = c.get("answer_ids") or [q["id"] for q in qs]
    byid = {q.get("id"): q for q in qs}
    out, cache = {}, {}
    for i, aid in enumerate(ids):
        q = byid.get(aid) or (qs[i] if i < len(qs) else {})
        _s, prefix, field = split_id(aid)
        path = find_artifact(a.artifacts, q.get("artifact", "evidence.zip"))
        if not path:
            log(f"[!] no artifact for {aid}")
            continue
        if path not in cache:
            cache[path] = [(n, b, is_cpp(n, b)) for n, b in unzip(open(path, "rb").read())
                           if b[:4] == b"\x7fELF" or b[:2] == b"MZ"]
            log(f"[*] {path}: {[(n, cp) for n, _, cp in cache[path]]}")
        try:
            v = answer(field, prefix, cache[path], q)
        except Exception as e:
            log(f"[!] {aid}: {e!r}")
            continue
        if v is None:
            log(f"[!] {aid}: no confirmed answer, omitted")
            continue
        out[aid] = v
    print(json.dumps(out))
    if not out:
        sys.exit(1)


if __name__ == "__main__":
    main()
