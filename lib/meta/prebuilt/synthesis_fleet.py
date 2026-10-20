"""Cross-FILE architecture-SUPPORT synthesis over Mach-O thin / fat (universal) / ar / zip / ELF / PE members (prebuilt,
SPECULATIVE; the spelling was never GM-verified). Coverage-atlas row "macho-fleet-synthesis": "which of these files
actually run on arm64 / which are really universal / which names lie". Ids `metadata-day-NN-synthesis-<key>`.
Members come from the question's `Files: [...]` list (parsed like lib.meta.synthesis.digest_order), read through
ctx["read"], else from `data` when the artifact IS the container zip (all members, zip order, when no Files list).
Each member's SUPPORTED cpu types (first-seen order), by MAGIC only (names / extensions are never trusted):
  * fat 0xcafebabe / 0xcafebabf (always big-endian, 0 < nfat_arch < 64 so a Java .class is not one): every fat_arch
    cputype in table order (a slice's own header is not consulted -- lipo / `file` report the table);
  * thin Mach-O feedface / feedfacf (either byte order): the header cputype;
  * ELF e_machine / PE COFF Machine mapped onto the Mach-O cputype of the same CPU (D20 spelling "0x%08x"):
    arm64 = Mach-O 0x0100000c / ELF 0x00b7 / PE 0xaa64; x86_64 = 0x01000007 / 0x003e / 0x8664; i386 = 7 / 0x0003 /
    0x014c; arm = 12 / 0x0028 / 0x01c0,0x01c2,0x01c4; ppc = 18 / 0x0014; ppc64 = 0x01000012 / 0x0015 (other
    machines carry no cpu type);
  * archives expand to their object members: `!<arch>` ar (GNU `/` `//` and BSD `#1/<len>` names; symbol tables
    `/`, `/SYM64/`, `__.SYMDEF*` skipped) and zip -- the union of the members' types (nested up to 3 levels);
  * anything else supports nothing.
Fields (names in Files order unless the instruction text says sorted / ascending / alphabetical; descending only
when stated; an empty result -> "none"):
  files_supporting_<arch> / <arch>_files / <arch>_supporting_files / arch_support_files (arch named in the text);
  universal_files = fat with >= 2 DISTINCT cputypes; thin_files = non-fat Mach-O; *_count of those = int;
  cpu_type_groups = {"0x%08x": sorted names} (keys ascending) -- a member is listed under every type it supports;
  extension_or_name_liars = names claiming universal/fat or an arch (arm64/aarch64, x86_64/amd64/x64, i386/x86/
  ia32/i686) whose slices disagree (claimed universal but not >= 2 distinct fat types, or a claimed arch absent);
  union_cpu_type_set = every supported type, first-seen over Files order (sorted only if the text says so).
synthesis.count_<arch> (already registered by synthesis_arch.py) calls count_supporting() for these arch aliases."""
import io
import re
import struct

FIELDS = {
    ("synthesis", "files_supporting_*"): "fleet_value",
    ("synthesis", "arch_support_files"): "fleet_value",
    ("synthesis", "architecture_support_files"): "fleet_value",
    ("synthesis", "supporting_files"): "fleet_value",
    ("synthesis", "arm64_files"): "fleet_value",
    ("synthesis", "x86_64_files"): "fleet_value",
    ("synthesis", "i386_files"): "fleet_value",
    ("synthesis", "arm64_supporting_files"): "fleet_value",
    ("synthesis", "x86_64_supporting_files"): "fleet_value",
    ("synthesis", "i386_supporting_files"): "fleet_value",
    ("synthesis", "universal_files"): "fleet_value",
    ("synthesis", "universal_filenames"): "fleet_value",
    ("synthesis", "universal_binaries"): "fleet_value",
    ("synthesis", "fat_files"): "fleet_value",
    ("synthesis", "universal_file_count"): "fleet_value",
    ("synthesis", "universal_count"): "fleet_value",
    ("synthesis", "thin_files"): "fleet_value",
    ("synthesis", "thin_filenames"): "fleet_value",
    ("synthesis", "thin_binaries"): "fleet_value",
    ("synthesis", "thin_file_count"): "fleet_value",
    ("synthesis", "thin_count"): "fleet_value",
    ("synthesis", "cpu_type_groups"): "fleet_value",
    ("synthesis", "cputype_groups"): "fleet_value",
    ("synthesis", "cpu_type_group_map"): "fleet_value",
    ("synthesis", "files_by_cpu_type"): "fleet_value",
    ("synthesis", "extension_or_name_liars"): "fleet_value",
    ("synthesis", "name_liars"): "fleet_value",
    ("synthesis", "filename_liars"): "fleet_value",
    ("synthesis", "extension_liars"): "fleet_value",
    ("synthesis", "name_mismatch_files"): "fleet_value",
    ("synthesis", "mislabeled_files"): "fleet_value",
    ("synthesis", "union_cpu_type_set"): "fleet_value",
    ("synthesis", "cpu_type_union"): "fleet_value",
    ("synthesis", "union_cpu_types"): "fleet_value",
    ("synthesis", "cpu_type_set"): "fleet_value",
}

ARM64, X86_64, I386 = 0x0100000C, 0x01000007, 7
ARCH_ALIASES = {"arm64": ARM64, "aarch64": ARM64, "arm_64": ARM64, "x86_64": X86_64, "amd64": X86_64,
                "x64": X86_64, "x86_64h": X86_64, "i386": I386, "x86": I386, "ia32": I386, "i686": I386,
                "arm": 12, "armv7": 12, "ppc": 18, "powerpc": 18, "ppc64": 0x01000012}
# aliases synthesis_arch.count_* routes here (aarch64 keeps its exact-name meaning there: aarch64_be stays apart)
COUNT_ALIASES = ("arm64", "arm_64", "x86_64", "amd64", "x64", "i386", "x86", "ia32", "i686")
_ELF_CPU = {0xB7: ARM64, 0x3E: X86_64, 0x03: I386, 0x28: 12, 0x14: 18, 0x15: 0x01000012}
_PE_CPU = {0xAA64: ARM64, 0x8664: X86_64, 0x14C: I386, 0x1C0: 12, 0x1C2: 12, 0x1C4: 12}


def _uniq(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def _ar_members(b):
    """Object members' bytes of a `!<arch>` archive (symbol tables skipped)."""
    out, off = [], 8
    while off + 60 <= len(b):
        hdr = b[off:off + 60]
        if hdr[58:60] != b"`\n":
            break
        name = hdr[:16].rstrip(b" ")
        try:
            size = int(hdr[48:58].strip() or b"0")
        except ValueError:
            break
        body = b[off + 60:off + 60 + size]
        if name.startswith(b"#1/"):           # BSD: the name is the first <len> bytes of the body
            try:
                nl = int(name[3:])
            except ValueError:
                nl = 0
            name, body = body[:nl].rstrip(b"\0"), body[nl:]
        if name not in (b"/", b"//", b"/SYM64/", b"/SYM64") and not name.startswith(b"__.SYMDEF"):
            out.append(body)
        off += 60 + size + (size & 1)
    return out


def _zip_members(b):
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
        return [z.read(i) for i in z.infolist()[:256] if not i.is_dir() and i.file_size < 64 << 20]
    except Exception:  # noqa: BLE001 - damaged zip -> no members
        return []


def profile(b, depth=0):
    """(kind, [cputype ...] first-seen) -- kind fat / thin / elf / pe / archive / data."""
    b = bytes(b or b"")
    if len(b) >= 8 and b[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
        n = struct.unpack_from(">I", b, 4)[0]
        w = 20 if b[3] == 0xBE else 32
        if 0 < n < 64 and 8 + n * w <= len(b):
            return "fat", [struct.unpack_from(">I", b, 8 + i * w)[0] for i in range(n)]
    if len(b) >= 8:
        for e in (">", "<"):
            magic, cpu = struct.unpack_from(e + "II", b, 0)
            if magic in (0xFEEDFACE, 0xFEEDFACF):
                return "thin", [cpu]
    if b[:4] == b"\x7fELF" and len(b) >= 20 and b[5] in (1, 2):
        m = struct.unpack_from(">H" if b[5] == 2 else "<H", b, 18)[0]
        return "elf", [_ELF_CPU[m]] if m in _ELF_CPU else []
    if b[:2] == b"MZ" and len(b) >= 0x40:
        pe = struct.unpack_from("<I", b, 0x3C)[0]
        if pe + 6 <= len(b) and b[pe:pe + 4] == b"PE\x00\x00":
            m = struct.unpack_from("<H", b, pe + 4)[0]
            return "pe", [_PE_CPU[m]] if m in _PE_CPU else []
    if depth < 3 and (b[:8] == b"!<arch>\n" or b[:4] == b"PK\x03\x04"):
        mem = _ar_members(b) if b[:1] == b"!" else _zip_members(b)
        return "archive", _uniq(c for m in mem for c in profile(m, depth + 1)[1])
    return "data", []


_UNIVERSAL_WORD = re.compile(r"(?:^|[^a-z0-9])(universal|fat|univ)(?:[^a-z0-9]|$)")
_ARCH_WORDS = ((ARM64, re.compile(r"(?:^|[^a-z0-9])(arm64e?|aarch64|apple[-_]?silicon)(?:[^a-z0-9]|$)")),
               (X86_64, re.compile(r"(?:^|[^a-z0-9])(x86[-_]?64h?|amd64|x64|intel64)(?:[^a-z0-9]|$)")),
               (I386, re.compile(r"(?:^|[^a-z0-9])(i[3-6]86|x86|ia32|win32)(?:[^a-z0-9_-]|$)")))


def claims(name):
    """(says_universal, {cputypes the NAME claims})."""
    low = (name or "").rsplit("/", 1)[-1].lower()
    want = {c for c, rx in _ARCH_WORDS if rx.search(low)}
    if X86_64 in want and re.search(r"x86[-_]64", low) and not re.search(r"x86(?![-_]?64)", low):
        want.discard(I386)
    return bool(_UNIVERSAL_WORD.search(low)), want


def is_liar(name, kind, cpus):
    uni, want = claims(name)
    if uni and not (kind == "fat" and len(set(cpus)) >= 2):
        return True
    return any(c not in cpus for c in want)


# ---------------------------------------------------------------- field logic

def _instr(text):
    return re.sub(r"Files:\s*\[.*?\]", "", text or "", flags=re.S)


def _arch_param(field, param, text):
    """The asked cputype, from the field name / wildcard param, else the instruction text; None if unknown."""
    p = (param if param is not None else "").lower().replace("-", "_")
    if not p:
        m = re.match(r"(?:files_supporting_(\w+)|(arm64|x86_64|i386)_)", field or "")
        p = (m.group(1) or m.group(2)) if m else ""
    if p in ARCH_ALIASES:
        return ARCH_ALIASES[p]
    low = _instr(text).lower()
    hits = [(m.start(), c) for c, rx in _ARCH_WORDS for m in [rx.search(low)] if m]
    return min(hits)[1] if hits else None


def _order(names, text):
    t = _instr(text)
    if re.search(r"\bdescending\b|\breverse\b", t, re.I):
        return sorted(names, reverse=True)
    if re.search(r"\b(sorted|ascending|alphabetical(?:ly)?|lexicographic(?:al)?(?:ly)?)\b", t, re.I):
        return sorted(names)
    return names


def count_supporting(names, get_bytes, arch):
    """synthesis.count_<arch>: how many named members support `arch`; None when unreadable / unknown arch."""
    cpu = ARCH_ALIASES.get((arch or "").lower().replace("-", "_"))
    if cpu is None:
        return None
    n = 0
    for nm in names:
        b = get_bytes(nm)
        if b is None:
            return None
        n += cpu in profile(b)[1]
    return n


def fleet_value_of(names, get_bytes, field, text="", param=None):
    """The raw value for `field` over `names`; None = unreadable / unanswerable, "none" = nothing applies."""
    rows = []
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        rows.append((n,) + profile(b))
    f = field or ""
    if f.startswith(("universal", "fat_files")):
        out = [n for n, k, c in rows if k == "fat" and len(set(c)) >= 2]
        return len(out) if f.endswith("count") else (_order(out, text) or "none")
    if f.startswith("thin"):
        out = [n for n, k, c in rows if k == "thin"]
        return len(out) if f.endswith("count") else (_order(out, text) or "none")
    if f in ("cpu_type_groups", "cputype_groups", "cpu_type_group_map", "files_by_cpu_type"):
        g = {}
        for n, _, cs in rows:
            for c in cs:
                g.setdefault("0x%08x" % c, []).append(n)
        desc = bool(re.search(r"\bdescending\b", _instr(text), re.I))
        return {k: sorted(set(g[k]), reverse=desc) for k in sorted(g)} or "none"
    if "liar" in f or f in ("name_mismatch_files", "mislabeled_files"):
        return _order([n for n, k, c in rows if is_liar(n, k, c)], text) or "none"
    if f in ("union_cpu_type_set", "cpu_type_union", "union_cpu_types", "cpu_type_set"):
        u = _uniq(c for _, _, cs in rows for c in cs)
        if re.search(r"\b(sorted|ascending)\b", _instr(text), re.I):
            u = sorted(u)
        elif re.search(r"\bdescending\b", _instr(text), re.I):
            u = sorted(u, reverse=True)
        return ["0x%08x" % c for c in u] or "none"
    cpu = _arch_param(f, param, text)
    if cpu is None:
        return None
    return _order([n for n, _, cs in rows if cpu in cs], text) or "none"


def fleet_value(data, ctx):
    """synthesis.<architecture-support field> (see the module docstring)."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        if not names:
            return "none"
        q = ctx.get("question")
        text = str((q.get("question") if isinstance(q, dict) else q) or "")
        v = fleet_value_of(names, read, ctx.get("field") or "", text, ctx.get("param"))
        return v if (v != "none" or from_zip) else None
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
