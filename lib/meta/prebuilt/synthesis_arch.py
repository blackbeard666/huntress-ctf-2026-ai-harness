"""Cross-FILE architecture / deployment-group synthesis over ELF + PE + Mach-O members (prebuilt, SPECULATIVE; the
spelling was never GM-verified). Coverage-atlas row "elf-arch-synthesis": the D19 prompt read "Linux binaries from
several systems have been pooled with Windows executables and renamed data. Determine architecture directly from the
ELF header and rebuild deployment groups" (the D19 synthesis id itself was still sha256-order).
Members come from the question's `Files: [...]` list (parsed like lib.meta.synthesis.digest_order), read through
ctx["read"], else from `data` when the artifact IS the container zip (all members when no Files list is given).
Each member is classified by MAGIC only (the extension is never trusted; a renamed non-binary is format `data`):
  * ELF  \\x7fELF: EI_CLASS -> bits, EI_DATA -> endianness, e_machine (u16 at 18, read in THAT endianness), os linux
    (EI_OSABI 9 freebsd / 12 openbsd / 2 netbsd / 6 solaris);
  * PE   MZ + PE\\0\\0 at e_lfanew: COFF Machine (u16 LE), optional-header magic 0x20b -> 64-bit, os windows;
  * Mach-O feedface/feedfacf (either byte order): cputype u32, os macos; fat cafebabe/cafebabf (nfat_arch < 64, so a
    Java class file is not one) -> arch `universal`;
  * anything else -> `data` (no arch).
Arch names are uname / Debian-triplet style and fold endianness + bitness into the name so groups split on them:
i386 x86_64 arm armeb aarch64 aarch64_be mips mipsel mips64 mips64el ppc ppcle ppc64 ppc64le s390 s390x sparc
sparc64 riscv32 riscv64 loongarch64 ia64 ...; an unknown machine -> `<fmt>_0x<machine hex>`. The same CPU in two
formats shares the arch name (PE 0x8664 and ELF 0x3e are both x86_64).
Scope: deployment_* / elf_* group fields use the ELF members only (the Linux deployments; Windows executables and
renamed data are the pool's distractors); architecture_* / machine_* / odd_* / count_* use every binary member,
narrowed to ELF when the question text names the ELF header / e_machine and no PE / Mach-O / Windows wording.
Values: *_groups = compact JSON list of lists, members in Files order, groups ordered by first appearance;
*_group_map / *_by_arch = {arch: [names]} (first-appearance key order); elf_members / non_elf_members / *_members =
names in Files order; machine_order = names sorted by (raw machine value, name), "descending" reverses the key;
odd_architecture_member = the lone member of the only singleton group (other groups must hold >= 2), else "none";
count_<arch|elf|pe|macho|data> = int (arm64/x86_64/i386 aliases: members SUPPORTING it, fat slices and archive
objects included -- synthesis_fleet.count_supporting). Nothing classifiable -> "none" from a zip artifact, else None."""
import re
import struct

FIELDS = {
    ("synthesis", "architecture_groups"): "arch_value",
    ("synthesis", "arch_groups"): "arch_value",
    ("synthesis", "machine_groups"): "arch_value",
    ("synthesis", "cpu_architecture_groups"): "arch_value",
    ("synthesis", "deployment_groups"): "arch_value",
    ("synthesis", "elf_architecture_groups"): "arch_value",
    ("synthesis", "elf_machine_groups"): "arch_value",
    ("synthesis", "e_machine_groups"): "arch_value",
    ("synthesis", "architecture_group_map"): "arch_value",
    ("synthesis", "architecture_groups_by_arch"): "arch_value",
    ("synthesis", "members_by_architecture"): "arch_value",
    ("synthesis", "files_by_architecture"): "arch_value",
    ("synthesis", "deployment_group_map"): "arch_value",
    ("synthesis", "deployment_groups_by_arch"): "arch_value",
    ("synthesis", "endianness_groups"): "arch_value",
    ("synthesis", "elf_members"): "arch_value",
    ("synthesis", "elf_files"): "arch_value",
    ("synthesis", "elf_filenames"): "arch_value",
    ("synthesis", "non_elf_members"): "arch_value",
    ("synthesis", "non_elf_files"): "arch_value",
    ("synthesis", "non_elf_filenames"): "arch_value",
    ("synthesis", "pe_members"): "arch_value",
    ("synthesis", "macho_members"): "arch_value",
    ("synthesis", "data_members"): "arch_value",
    ("synthesis", "non_binary_members"): "arch_value",
    ("synthesis", "binary_members"): "arch_value",
    ("synthesis", "big_endian_members"): "arch_value",
    ("synthesis", "little_endian_members"): "arch_value",
    ("synthesis", "elf_member_count"): "arch_value",
    ("synthesis", "non_elf_member_count"): "arch_value",
    ("synthesis", "architecture_count"): "arch_value",
    ("synthesis", "distinct_architecture_count"): "arch_value",
    ("synthesis", "deployment_group_count"): "arch_value",
    ("synthesis", "odd_architecture_member"): "arch_value",
    ("synthesis", "odd_architecture_file"): "arch_value",
    ("synthesis", "odd_arch_member"): "arch_value",
    ("synthesis", "odd_machine_member"): "arch_value",
    ("synthesis", "architecture_outlier"): "arch_value",
    ("synthesis", "odd_endianness_member"): "arch_value",
    ("synthesis", "machine_order"): "arch_value",
    ("synthesis", "e_machine_order"): "arch_value",
    ("synthesis", "architecture_order"): "arch_value",
    ("synthesis", "count_*"): "arch_value",
}

_ELF_OS = {0: "linux", 3: "linux", 2: "netbsd", 6: "solaris", 9: "freebsd", 12: "openbsd"}


def _elf_arch(m, b64, be):
    if m == 0x03 or m == 0x06:
        return "i386"
    if m == 0x3E:
        return "x86_64"
    if m == 0xB7:
        return "aarch64_be" if be else "aarch64"
    if m == 0x28:
        return "armeb" if be else "arm"
    if m in (0x08, 0x0A):
        return ("mips64" if b64 else "mips") + ("" if be else "el")
    if m == 0x14:
        return "ppc" if be else "ppcle"
    if m == 0x15:
        return "ppc64" if be else "ppc64le"
    if m == 0x16:
        return "s390x" if b64 else "s390"
    if m in (0x02, 0x12):
        return "sparc64" if b64 else "sparc"
    if m == 0x2B:
        return "sparc64"
    if m == 0xF3:
        return "riscv64" if b64 else "riscv32"
    if m == 0x102:
        return "loongarch64" if b64 else "loongarch32"
    return {0x32: "ia64", 0x2A: "sh", 0x04: "m68k", 0x0F: "parisc", 0x9026: "alpha", 0x29: "alpha",
            0x5C: "or1k", 0x53: "avr", 0x5E: "xtensa", 0xF7: "bpf"}.get(m, "elf_0x%04x" % m)


_PE_ARCH = {0x14C: "i386", 0x8664: "x86_64", 0xAA64: "aarch64", 0x1C0: "arm", 0x1C2: "arm", 0x1C4: "arm",
            0x200: "ia64", 0x5032: "riscv32", 0x5064: "riscv64", 0x6264: "loongarch64", 0xA641: "arm64ec",
            0x166: "mipsel", 0x1F0: "ppcle", 0x1F1: "ppcle"}
_MACHO_ARCH = {7: "i386", 0x01000007: "x86_64", 12: "arm", 0x0100000C: "aarch64", 0x0200000C: "arm64_32",
               18: "ppc", 0x01000012: "ppc64"}


def classify(b):
    """{format, machine, bits, endianness, os, arch} by magic; format `data` (machine/arch None) otherwise."""
    b = bytes(b or b"")
    if b[:4] == b"\x7fELF" and len(b) >= 20 and b[4] in (1, 2) and b[5] in (1, 2):
        be = b[5] == 2
        m = struct.unpack_from(">H" if be else "<H", b, 18)[0]
        b64 = b[4] == 2
        return {"format": "elf", "machine": m, "bits": 64 if b64 else 32, "endianness": "big" if be else "little",
                "os": _ELF_OS.get(b[7], "osabi_%d" % b[7]), "arch": _elf_arch(m, b64, be)}
    if b[:2] == b"MZ" and len(b) >= 0x40:
        pe = struct.unpack_from("<I", b, 0x3C)[0]
        if pe + 26 <= len(b) and b[pe:pe + 4] == b"PE\x00\x00":
            m = struct.unpack_from("<H", b, pe + 4)[0]
            opt = struct.unpack_from("<H", b, pe + 24)[0]
            return {"format": "pe", "machine": m, "bits": 64 if opt == 0x20B else 32, "endianness": "little",
                    "os": "windows", "arch": _PE_ARCH.get(m, "pe_0x%04x" % m)}
    if len(b) >= 8:
        for fmt, end in ((">", "big"), ("<", "little")):
            magic, cpu = struct.unpack_from(fmt + "II", b, 0)
            if magic in (0xFEEDFACE, 0xFEEDFACF):
                return {"format": "macho", "machine": cpu, "bits": 64 if magic == 0xFEEDFACF else 32,
                        "endianness": end, "os": "macos", "arch": _MACHO_ARCH.get(cpu, "macho_0x%08x" % cpu)}
        magic, n = struct.unpack_from(">II", b, 0)
        if magic in (0xCAFEBABE, 0xCAFEBABF) and 0 < n < 64:
            return {"format": "macho-fat", "machine": 0, "bits": 64 if magic == 0xCAFEBABF else 32,
                    "endianness": "big", "os": "macos", "arch": "universal"}
    return {"format": "data", "machine": None, "bits": None, "endianness": None, "os": None, "arch": None}


# ---------------------------------------------------------------- the solver-facing call

_DESC = re.compile(r"\b(descending|highest first|largest first|reverse)\b", re.I)
_ELF_TEXT = re.compile(r"\bELF\b|e_machine", re.I)
_OTHER_TEXT = re.compile(r"\bPE\b|COFF|Mach-?O|Windows|\bexe\b", re.I)


def _text(question):
    return str(((question or {}).get("question") if isinstance(question, dict) else question) or "")


def _groups(rows, key):
    out = {}
    for n, c in rows:
        out.setdefault(key(c), []).append(n)
    return out


def arch_value_of(names, get_bytes, field, text="", param=None):
    """The raw value for `field` over `names`; None = a member can't be read, "none" = nothing applies."""
    rows = []
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        rows.append((n, classify(b)))
    f = field or ""
    elf = [(n, c) for n, c in rows if c["format"] == "elf"]
    binaries = [(n, c) for n, c in rows if c["format"] != "data"]
    instr = re.sub(r"Files:\s*\[.*?\]", "", text, flags=re.S)   # member names (`.exe`) are not instructions
    scope = elf if (_ELF_TEXT.search(instr) and not _OTHER_TEXT.search(instr)) else binaries
    if f.startswith(("deployment", "elf_arch", "elf_machine", "e_machine")):
        scope = elf
    if f in ("elf_members", "elf_files", "elf_filenames"):
        return [n for n, _ in elf] or "none"
    if f in ("non_elf_members", "non_elf_files", "non_elf_filenames"):
        return [n for n, c in rows if c["format"] != "elf"] or "none"
    if f == "elf_member_count":
        return len(elf)
    if f == "non_elf_member_count":
        return len(rows) - len(elf)
    if f in ("pe_members", "macho_members", "data_members", "non_binary_members", "binary_members"):
        want = {"pe_members": ("pe",), "macho_members": ("macho", "macho-fat"), "data_members": ("data",),
                "non_binary_members": ("data",)}.get(f)
        return [n for n, c in rows if (c["format"] in want if want else c["format"] != "data")] or "none"
    if f in ("big_endian_members", "little_endian_members"):
        return [n for n, c in scope if c["endianness"] == f.split("_")[0]] or "none"
    if f.startswith("count_") or f == "count":
        p = (param if param is not None else f[len("count_"):]).lower().replace("-", "_")
        if p in ("elf", "pe", "macho", "data"):
            return sum(1 for _, c in rows if c["format"].split("-")[0] == p)
        from .synthesis_fleet import COUNT_ALIASES, count_supporting
        if p in COUNT_ALIASES:   # macho-fleet: fat slices / ar + zip object members count toward the arch they cover
            return count_supporting([n for n, _ in (elf if scope is elf else rows)], get_bytes, p)
        return sum(1 for _, c in scope if c["arch"] == p)
    if not scope:
        return "none"
    if f == "endianness_groups":
        return list(_groups(scope, lambda c: c["endianness"]).values())
    if f == "odd_endianness_member":
        g = _groups(scope, lambda c: c["endianness"])
        lone = [v[0] for v in g.values() if len(v) == 1]
        return lone[0] if len(g) == 2 and len(lone) == 1 and len(scope) >= 3 else "none"
    g = _groups(scope, lambda c: c["arch"])
    if "order" in f:
        keyed = sorted(((c["machine"], n) for n, c in scope),
                       key=(lambda k: (-k[0], k[1])) if _DESC.search(text) else (lambda k: k))
        return [n for _, n in keyed]
    if f.endswith(("_map", "_by_arch")) or f.startswith(("members_by", "files_by")):
        return g
    if f.endswith("_count"):
        return len(g)
    if f.startswith("odd") or "outlier" in f:
        lone = [v[0] for v in g.values() if len(v) == 1]
        return lone[0] if len(lone) == 1 and len(g) >= 2 and any(len(v) >= 2 for v in g.values()) else "none"
    return list(g.values())


def arch_value_for(question, get_bytes, field):
    """Solver-facing: the `field` value over the question's Files list read via get_bytes(name), or None."""
    from .synthesis_media import file_list
    names = file_list(question)
    if not names:
        return None
    return arch_value_of(names, get_bytes, field, _text(question))


def arch_value(data, ctx):
    """synthesis.<architecture / deployment field> (see the module docstring)."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        if not names:
            return "none"
        v = arch_value_of(names, read, ctx.get("field") or "", _text(ctx.get("question")), ctx.get("param"))
        return v if (v != "none" or from_zip) else None
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
