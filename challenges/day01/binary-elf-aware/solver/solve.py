#!/usr/bin/env python3
"""ELF orientation solver (Day 01 binary "ELF Aware").

Per set (single, or Mastery setN.*), from the ELF inside the named zip:
  elf_class        e_ident[EI_CLASS]  -> "ELF32"/"ELF64"           (GM-confirmed style: readelf name)
  endianness       e_ident[EI_DATA]   -> ENDIAN_NAMES              (UNCONFIRMED vocabulary)
  machine          e_machine          -> MACHINE_NAMES             (UNCONFIRMED; "EM_X86_64" was judged incorrect)
  elf_type         e_type             -> "ET_EXEC"/"ET_DYN"/...    (GM-confirmed style: spec constant)
  marker           .huntress section bytes up to first NUL
  has_symtab       "true"/"false"
  exported_symbol  the non-toolchain GLOBAL FUNC in .symtab/.dynsym (e.g. recover_code)
  recover_code     immediate returned by the function named in the question (mov eax, imm; ret)
  entry_point      hex(e_entry)
"""
import argparse, io, json, os, re, sys, zipfile

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

def log(*a):
    print(*a, file=sys.stderr)

# EI_DATA -> answer. Unconfirmed by the GM; adjust here once confirmed.
ENDIAN_NAMES = {"ELFDATA2LSB": "little", "ELFDATA2MSB": "big"}  # confirmed: GM wants "little"/"big"
# e_machine -> answer. Unconfirmed ("EM_X86_64" rejected); readelf-style short names.
MACHINE_NAMES = {"EM_X86_64": "x86-64", "EM_386": "x86", "EM_AARCH64": "AArch64", "EM_ARM": "ARM",
                 "EM_RISCV": "RISC-V", "EM_MIPS": "MIPS", "EM_PPC": "PowerPC", "EM_PPC64": "PowerPC64",
                 "EM_S390": "S/390", "EM_SPARCV9": "SPARC v9", "EM_LOONGARCH": "LoongArch"}

TOOLCHAIN = {"main", "_start", "_init", "_fini", "frame_dummy", "register_tm_clones", "deregister_tm_clones",
             "__do_global_dtors_aux", "_dl_relocate_static_pie", "__libc_csu_init", "__libc_csu_fini"}


def find_artifact(adir, name):
    """Contract names look like 'evidence.zip' or 'delivery 2: evidence.zip'."""
    cands = [name, os.path.basename(name), name.split(":", 1)[-1].strip()]
    files = [os.path.join(r, f) for r, _, fs in os.walk(adir) for f in fs if f != "manifest.json"]
    for c in cands:
        for p in files:
            if os.path.basename(p) == c:
                return p
    m = re.search(r"delivery\s*(\d+)", name, re.I)
    if m:
        n = m.group(1)
        hit = [p for p in files if re.search(rf"(delivery|set|artifact)[^0-9]*0*{n}\b", os.path.basename(p), re.I)]
        if len(hit) == 1:
            return hit[0]
        zips = sorted(p for p in files if p.lower().endswith(".zip"))
        if len(zips) >= int(n):
            log(f"[!] {name}: picking zip #{n} of {zips}")
            return zips[int(n) - 1]
    if len(files) == 1:
        return files[0]
    return None


def elf_members(data, prefix=""):
    """All (name, ELF bytes) in a bare ELF or a (nested) zip, in archive order."""
    if data[:4] == b"\x7fELF":
        return [(prefix, data)]
    out = []
    if data[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for i in z.infolist():
                if not i.is_dir():
                    out += elf_members(z.read(i), i.filename)
    return out


def load_elf_bytes(path, slot=None):
    """slot = (label, n) from an answer-id prefix like 'slot0_' / 'set2.' -> pick the matching member."""
    mems = elf_members(open(path, "rb").read(), os.path.basename(path))
    if not mems:
        raise ValueError(f"no ELF in {path}")
    if slot is None or len(mems) == 1:
        if len(mems) > 1:
            log(f"[!] {path}: {len(mems)} ELFs, no slot -> first {mems[0][0]}")
        return mems[0][1]
    label, n, base = slot
    for rx in (rf"{re.escape(label)}[^a-z0-9]*0*{n}(?!\d)", rf"(?<!\d)0*{n}(?!\d)"):
        hit = [b for name, b in mems if re.search(rx, os.path.basename(name).lower())]
        if len(hit) == 1:
            return hit[0]
    i = n - base
    if 0 <= i < len(mems):
        log(f"[!] {path}: slot {label}{n} by position #{i} of {[m[0] for m in mems]}")
        return mems[i][1]
    raise ValueError(f"no member for slot {label}{n} in {path}")


def symbols(elf):
    out = []
    for sec in elf.iter_sections():
        if isinstance(sec, SymbolTableSection):
            for s in sec.iter_symbols():
                out.append((sec.name, s))
    return out


def func_return_const(elf, data, name):
    """Find FUNC symbol `name`, disassemble it, return the last immediate moved into eax/rax/x0/w0/r0 before ret."""
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_MODE_32, CS_ARCH_ARM64, CS_ARCH_ARM, CS_MODE_ARM
    sym = next((s for _, s in symbols(elf) if s.name == name and s["st_info"]["type"] == "STT_FUNC"), None)
    if sym is None:
        return None
    addr, size = sym["st_value"], sym["st_size"] or 64
    off = None
    for seg in elf.iter_segments():
        if seg["p_type"] == "PT_LOAD" and seg["p_vaddr"] <= addr < seg["p_vaddr"] + seg["p_filesz"]:
            off = addr - seg["p_vaddr"] + seg["p_offset"]
    if off is None:
        return None
    code = data[off:off + size]
    m = elf["e_machine"]
    if m == "EM_X86_64":
        md = Cs(CS_ARCH_X86, CS_MODE_64)
    elif m == "EM_386":
        md = Cs(CS_ARCH_X86, CS_MODE_32)
    elif m == "EM_AARCH64":
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    elif m == "EM_ARM":
        md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    else:
        return None
    regs = {}
    last = None
    for ins in md.disasm(code, addr):
        mnem, ops = ins.mnemonic, ins.op_str.replace(" ", "")
        mm = re.match(r"(\w+),(?:#)?(-?(?:0x[0-9a-f]+|\d+))$", ops)
        if mnem in ("mov", "movz", "movabs") and mm:
            regs[mm.group(1)] = int(mm.group(2), 0)
        elif mnem == "movk" and re.match(r"(\w+),#(0x[0-9a-f]+|\d+),lsl#(\d+)", ops):
            r, v, sh = re.match(r"(\w+),#(0x[0-9a-f]+|\d+),lsl#(\d+)", ops).groups()
            regs[r] = (regs.get(r, 0) & ~(0xffff << int(sh))) | (int(v, 0) << int(sh))
        elif mnem == "xor" and re.match(r"(\w+),\1$", ops):
            regs[ops.split(",")[0]] = 0
        if mnem in ("ret", "retq", "bx") or (mnem == "pop" and "pc" in ops):
            for r in ("eax", "rax", "w0", "x0", "r0"):
                if r in regs:
                    last = regs[r]
                    break
            break
    if last is not None and m in ("EM_X86_64", "EM_386", "EM_AARCH64", "EM_ARM") and last >= 2**31 and last < 2**32:
        last -= 2**32  # int return
    return last


def designated_symbol(elf):
    """The one GLOBAL FUNC defined in the program that isn't toolchain/CRT glue."""
    cands = []
    for _, s in symbols(elf):
        i = s["st_info"]
        if i["type"] == "STT_FUNC" and i["bind"] in ("STB_GLOBAL", "STB_WEAK") and s["st_shndx"] != "SHN_UNDEF" \
                and s.name and s.name not in TOOLCHAIN and not s.name.startswith("_"):
            if s.name not in cands:
                cands.append(s.name)
    log(f"[*] designated symbol candidates: {cands}")
    return cands[0] if cands else "none"


def solve_one(data, key, q):
    elf = ELFFile(io.BytesIO(data))
    h = elf.header
    if key == "elf_class":
        return {"ELFCLASS32": "ELF32", "ELFCLASS64": "ELF64"}.get(h["e_ident"]["EI_CLASS"], h["e_ident"]["EI_CLASS"])
    if key == "endianness":
        d = h["e_ident"]["EI_DATA"]
        return ENDIAN_NAMES.get(d, d)
    if key == "machine":
        return MACHINE_NAMES.get(h["e_machine"], h["e_machine"])
    if key == "elf_type":
        return h["e_type"]
    if key == "marker":
        sec = elf.get_section_by_name(".huntress")
        if sec is None:
            return "none"
        return sec.data().split(b"\0", 1)[0].decode("utf-8", "replace")
    if key == "has_symtab":
        return "true" if elf.get_section_by_name(".symtab") is not None else "false"
    if key == "exported_symbol":
        return designated_symbol(elf)
    if key == "entry_point":
        return hex(h["e_entry"])
    # constant returned by <func>
    m = re.search(r"returned by\s+`?([A-Za-z_][\w]*)", q.get("question", ""))
    fname = m.group(1) if m else key
    v = func_return_const(elf, data, fname)
    if v is None:
        named_absent = m is not None and not any(s.name == fname for _, s in symbols(elf))
        if named_absent and (q.get("answer_format") or {}).get("kind") != "integer":
            # Variant: question names a function the binary doesn't contain and the format allows the literal none.
            log(f"[*] {fname} absent from symbols -> none")
            return "none"
        v = func_return_const(elf, data, designated_symbol(elf))
    return None if v is None else str(v)


KEYS = {"elf_class", "endianness", "machine", "elf_type", "marker", "has_symtab", "exported_symbol", "entry_point"}


def pair_ids(ids, qs):
    """Map each answer id to its question: exact id, else the question id that the answer id ends with
    (variant: answer_ids 'slot0_marker'..'slot3_marker' share one 'marker' question), else by position."""
    out = []
    for i, aid in enumerate(ids):
        q = next((q for q in qs if q.get("id") == aid), None)
        if q is None:
            sufs = [q for q in qs if q.get("id") and re.search(rf"(^|[._-]){re.escape(q['id'].split('.')[-1])}$", aid)]
            q = max(sufs, key=lambda q: len(q["id"]), default=None)
        if q is None and len(ids) == len(qs):
            q = qs[i]
        if q is None:
            log(f"[!] no question for {aid}")
            continue
        out.append((aid, q))
    return out


def slot_of(aid, q):
    """Per-member prefix of an answer id ('slot0_x' -> ('slot', 0)) not already carried by the question id."""
    qid = (q.get("id") or "").split(".")[-1]
    pre = aid[: len(aid) - len(qid)] if qid and aid.endswith(qid) else ""
    m = re.match(r"([a-z]+)[^a-z0-9]*(\d+)[._-]?$", pre.lower())
    if not m or q.get("id") == aid:
        return None
    return (m.group(1), int(m.group(2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    c = json.load(open(a.contract))
    qs = c.get("questions") or []
    ids = c.get("answer_ids") or [q["id"] for q in qs]
    pairs = pair_ids(ids, qs)
    slots = {aid: slot_of(aid, q) for aid, q in pairs}
    base = 0 if any(s and s[1] == 0 for s in slots.values()) else 1
    out, cache = {}, {}
    for aid, q in pairs:
        key = (q.get("id") or aid).split(".")[-1]
        txt = q.get("question", "").lower()
        if key not in KEYS and "returned by" not in txt:
            continue
        art = q.get("artifact", "")
        path = find_artifact(a.artifacts, art)
        if not path:
            log(f"[!] artifact {art!r} not found for {aid}")
            continue
        slot = slots[aid] and slots[aid] + (base,)
        try:
            if (path, slot) not in cache:
                cache[(path, slot)] = load_elf_bytes(path, slot)
            v = solve_one(cache[(path, slot)], key, q)
        except Exception as e:
            log(f"[!] {aid}: {e}")
            continue
        if v is not None:
            out[aid] = v
    if not out:
        log("[!] nothing answered")
        print(json.dumps(out))
        sys.exit(1)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
