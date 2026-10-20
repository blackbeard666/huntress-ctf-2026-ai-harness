"""ELF kernel-module `.modinfo` and core-dump (ET_CORE) note fields (prebuilt, SPECULATIVE -- never GM-asked yet).

.ko (ET_REL): the `.modinfo` section is NUL-separated `key=value` strings (MODULE_INFO / MODULE_LICENSE / ...;
kmod `modinfo` reads the same bytes). elf.modinfo_<key> = the value of the FIRST `<key>=` string, trimmed (the
kernel's vermagic carries a trailing space; normalization trims it); a key stored several times (alias, parm,
parmtype, firmware, softdep) -> the list of values in stored order. modinfo_keys = the keys in stored order
(duplicates dropped). Under fmt `ko` the bare key works too (`ko.vermagic`).
An empty value (`depends=` of a module without deps) or a missing key / missing .modinfo -> "none".

core (e_type 4 ET_CORE): every PT_NOTE segment's notes (namesz/descsz/type, 4-byte aligned, as the kernel's
binfmt_elf writes them). NT_PRPSINFO (3): pr_fname[16] / pr_psargs[80] are the LAST 96 bytes of the desc on every
arch (x86_64 136 B, i386/arm 124 B), pr_pid/pr_ppid = the two i32 before uid/gid... read at desc_len-112 / -108
(readelf -n / `file` "from '<psargs>'"); psargs = NUL-trimmed, trailing spaces dropped. NT_PRSTATUS (1) count =
thread count (one per thread, readelf -n). NT_FILE (0x46494c45): count, page_size, count*(start,end,pgoff) words,
then NUL-separated paths; mapped_file_paths = the paths de-duplicated in stored order, nt_file_entry_paths = every
entry (duplicates kept), nt_file_count = entry count. NT_AUXV (6): word pairs; AT_EXECFN (31) / AT_PLATFORM (15)
are user-space POINTERS, resolved through the core's PT_LOAD segments (file-backed bytes) to the NUL-terminated
string (`file` "execfn: './x'"); unresolvable -> None. signal = NT_SIGINFO si_signo, else NT_PRSTATUS pr_cursig.
Not ELF -> "none"; ELF but not ET_CORE for a core field -> "none".
Fixtures: gcc 13 (`__attribute__((section(".modinfo")))` MODULE_INFO strings) + kernel core dump of a static
3-thread program (coredump_filter=0); oracles kmod `modinfo -F`, readelf -n, `file`, pyelftools."""
import struct

FIELDS = {
    ("elf", "modinfo_*"): "modinfo_value",
    ("elf", "modinfo_keys"): "modinfo_value",
    ("elf", "modinfo_key_names"): "modinfo_value",
    ("elf", "modinfo_vermagic"): "modinfo_value",
    ("elf", "modinfo_srcversion"): "modinfo_value",
    ("elf", "modinfo_license"): "modinfo_value",
    ("elf", "modinfo_name"): "modinfo_value",
    ("elf", "modinfo_depends"): "modinfo_value",
    ("elf", "modinfo_author"): "modinfo_value",
    ("elf", "modinfo_description"): "modinfo_value",
    ("elf", "modinfo_version"): "modinfo_value",
    ("elf", "modinfo_alias"): "modinfo_value",
    ("elf", "modinfo_retpoline"): "modinfo_value",
    ("elf", "modinfo_intree"): "modinfo_value",
    ("elf", "vermagic"): "modinfo_value",
    ("elf", "srcversion"): "modinfo_value",
    ("elf", "module_name"): "modinfo_value",
    ("elf", "module_license"): "modinfo_value",
    ("elf", "module_author"): "modinfo_value",
    ("elf", "module_depends"): "modinfo_value",
    ("elf", "module_version"): "modinfo_value",
    ("elf", "module_description"): "modinfo_value",
    ("elf", "module_vermagic"): "modinfo_value",
    ("elf", "module_srcversion"): "modinfo_value",
    ("ko", "modinfo_*"): "modinfo_value",
    ("ko", "modinfo_keys"): "modinfo_value",
    ("ko", "vermagic"): "modinfo_value",
    ("ko", "srcversion"): "modinfo_value",
    ("ko", "license"): "modinfo_value",
    ("ko", "name"): "modinfo_value",
    ("ko", "depends"): "modinfo_value",
    ("ko", "author"): "modinfo_value",
    ("ko", "description"): "modinfo_value",
    ("ko", "version"): "modinfo_value",
    ("ko", "alias"): "modinfo_value",
    ("elf", "pr_fname"): "core_value",
    ("elf", "prpsinfo_pr_fname"): "core_value",
    ("elf", "prpsinfo_fname"): "core_value",
    ("elf", "nt_prpsinfo_pr_fname"): "core_value",
    ("elf", "core_pr_fname"): "core_value",
    ("elf", "core_process_name"): "core_value",
    ("elf", "core_fname"): "core_value",
    ("elf", "pr_psargs"): "core_value",
    ("elf", "prpsinfo_pr_psargs"): "core_value",
    ("elf", "prpsinfo_psargs"): "core_value",
    ("elf", "nt_prpsinfo_pr_psargs"): "core_value",
    ("elf", "core_pr_psargs"): "core_value",
    ("elf", "core_psargs"): "core_value",
    ("elf", "core_command_line"): "core_value",
    ("elf", "core_cmdline"): "core_value",
    ("elf", "pr_pid"): "core_value",
    ("elf", "prpsinfo_pr_pid"): "core_value",
    ("elf", "core_pid"): "core_value",
    ("elf", "pr_ppid"): "core_value",
    ("elf", "prpsinfo_pr_ppid"): "core_value",
    ("elf", "nt_prstatus_count"): "core_value",
    ("elf", "prstatus_count"): "core_value",
    ("elf", "prstatus_note_count"): "core_value",
    ("elf", "thread_count"): "core_value",
    ("elf", "core_thread_count"): "core_value",
    ("elf", "num_threads"): "core_value",
    ("elf", "number_of_threads"): "core_value",
    ("elf", "nt_file_paths"): "core_value",
    ("elf", "nt_file_mapped_paths"): "core_value",
    ("elf", "nt_file_filenames"): "core_value",
    ("elf", "mapped_file_paths"): "core_value",
    ("elf", "mapped_files"): "core_value",
    ("elf", "mapped_paths"): "core_value",
    ("elf", "core_mapped_files"): "core_value",
    ("elf", "core_mapped_file_paths"): "core_value",
    ("elf", "nt_file_entry_paths"): "core_value",
    ("elf", "nt_file_entries"): "core_value",
    ("elf", "nt_file_count"): "core_value",
    ("elf", "nt_file_entry_count"): "core_value",
    ("elf", "mapped_file_count"): "core_value",
    ("elf", "nt_file_page_size"): "core_value",
    ("elf", "at_execfn"): "core_value",
    ("elf", "auxv_at_execfn"): "core_value",
    ("elf", "nt_auxv_at_execfn"): "core_value",
    ("elf", "execfn"): "core_value",
    ("elf", "core_execfn"): "core_value",
    ("elf", "at_platform"): "core_value",
    ("elf", "auxv_at_platform"): "core_value",
    ("elf", "nt_auxv_at_platform"): "core_value",
    ("elf", "core_signal"): "core_value",
    ("elf", "signal"): "core_value",
    ("elf", "si_signo"): "core_value",
    ("elf", "pr_cursig"): "core_value",
    ("elf", "core_note_types"): "core_value",
    ("core", "pr_fname"): "core_value",
    ("core", "pr_psargs"): "core_value",
    ("core", "prpsinfo_pr_fname"): "core_value",
    ("core", "prpsinfo_pr_psargs"): "core_value",
    ("core", "process_name"): "core_value",
    ("core", "command_line"): "core_value",
    ("core", "pr_pid"): "core_value",
    ("core", "nt_prstatus_count"): "core_value",
    ("core", "thread_count"): "core_value",
    ("core", "nt_file_paths"): "core_value",
    ("core", "mapped_file_paths"): "core_value",
    ("core", "mapped_files"): "core_value",
    ("core", "nt_file_entry_paths"): "core_value",
    ("core", "nt_file_count"): "core_value",
    ("core", "at_execfn"): "core_value",
    ("core", "auxv_at_execfn"): "core_value",
    ("core", "execfn"): "core_value",
    ("core", "at_platform"): "core_value",
    ("core", "signal"): "core_value",
}

_NT_PRSTATUS, _NT_PRPSINFO, _NT_AUXV, _NT_FILE, _NT_SIGINFO = 1, 3, 6, 0x46494C45, 0x53494749
_MULTI = ("alias", "parm", "parmtype", "firmware", "softdep", "import_ns")


def _ehdr(b):
    if not b or len(b) < 52 or b[:4] != b"\x7fELF" or b[4] not in (1, 2) or b[5] not in (1, 2):
        return None
    e = "<" if b[5] == 1 else ">"
    w = 8 if b[4] == 2 else 4
    if len(b) < (64 if w == 8 else 52):
        return None
    q = "Q" if w == 8 else "I"
    etype, = struct.unpack_from(e + "H", b, 16)
    phoff, shoff = struct.unpack_from(e + q + q, b, 24 + w)
    phentsize, phnum, shentsize, shnum, shstrndx = struct.unpack_from(e + "5H", b, 24 + 3 * w + 4 + 2)
    return dict(e=e, w=w, q=q, type=etype, phoff=phoff, shoff=shoff, phentsize=phentsize, phnum=phnum,
                shentsize=shentsize, shnum=shnum, shstrndx=shstrndx)


def _sections(b, h):
    """[(name, type, offset, size)] or []."""
    e, q, w = h["e"], h["q"], h["w"]
    out = []
    n, off, es = h["shnum"], h["shoff"], h["shentsize"]
    if not off or es < (64 if w == 8 else 40) or off + es > len(b):
        return out
    if n == 0:
        n = struct.unpack_from(e + q, b, off + 16 + 2 * w)[0]
    n = min(n, (len(b) - off) // es)
    raw = []
    for i in range(n):
        o = off + i * es
        name, typ = struct.unpack_from(e + "II", b, o)
        so, sz = struct.unpack_from(e + q + q, b, o + 8 + 2 * w)
        raw.append((name, typ, so, sz))
    si = h["shstrndx"]
    if si == 0xFFFF and raw:
        si = struct.unpack_from(e + "I", b, off + 24 + 3 * w)[0]
    strtab = b""
    if 0 <= si < len(raw):
        strtab = b[raw[si][2]:raw[si][2] + raw[si][3]]
    for name, typ, so, sz in raw:
        nm = strtab[name:strtab.find(b"\0", name)] if name < len(strtab) else b""
        out.append((nm.decode("latin-1"), typ, so, sz))
    return out


def _modinfo(b):
    h = _ehdr(b)
    if h is None:
        return None
    for nm, typ, so, sz in _sections(b, h):
        if nm == ".modinfo" and typ != 8:          # SHT_NOBITS carries no bytes
            pairs = []
            for s in b[so:so + sz].split(b"\0"):
                if b"=" in s:
                    k, _, v = s.decode("utf-8", "replace").partition("=")
                    pairs.append((k, v))
            return pairs
    return []


def modinfo_value(data, ctx):
    try:
        return _mod(data, ctx)
    except Exception:
        return None


def _mod(b, ctx):
    if b is None:
        return None
    pairs = _modinfo(b)
    if not pairs:
        return "none"
    f = ctx.get("field") or ""
    if f in ("modinfo_keys", "modinfo_key_names"):
        return list(dict.fromkeys(k for k, _ in pairs))
    for p in ("modinfo_", "module_"):
        if f.startswith(p):
            f = f[len(p):]
            break
    vals = [v.strip() for k, v in pairs if k == f]
    if not vals:
        return "none"
    if f in _MULTI and len(vals) > 1:
        return vals
    return vals[0] or "none"


def _notes(b, h):
    """[(name, type, desc)] of every PT_NOTE segment, plus [(vaddr, offset, filesz)] of the PT_LOAD segments."""
    e, q, w = h["e"], h["q"], h["w"]
    notes, loads = [], []
    es = h["phentsize"]
    if not h["phoff"] or es < (56 if w == 8 else 32):
        return notes, loads
    for i in range(min(h["phnum"], 65535)):
        o = h["phoff"] + i * es
        if o + es > len(b):
            break
        if w == 8:
            pt, _fl, off, va, _pa, fsz = struct.unpack_from(e + "IIQQQQ", b, o)
        else:
            pt, off, va, _pa, fsz = struct.unpack_from(e + "IIIII", b, o)
        if pt == 1:
            loads.append((va, off, fsz))
        elif pt == 4:
            blob = b[off:off + fsz]
            p = 0
            while p + 12 <= len(blob):
                nsz, dsz, typ = struct.unpack_from(e + "III", blob, p)
                p += 12
                name = blob[p:p + nsz].rstrip(b"\0").decode("latin-1")
                p += (nsz + 3) & ~3
                desc = blob[p:p + dsz]
                p += (dsz + 3) & ~3
                if len(desc) < dsz:
                    break
                notes.append((name, typ, desc))
    return notes, loads


def _cstr_at(b, loads, va):
    for base, off, fsz in loads:
        if base <= va < base + fsz:
            s = b[off + va - base:off + fsz]
            s = s[:s.find(b"\0")] if b"\0" in s else None
            return s.decode("utf-8", "replace") if s is not None else None
    return None


def core_value(data, ctx):
    try:
        return _core(data, ctx)
    except Exception:
        return None


def _core(b, ctx):
    if b is None:
        return None
    h = _ehdr(b)
    if h is None or h["type"] != 4:
        return "none"
    e, q, w = h["e"], h["q"], h["w"]
    notes, loads = _notes(b, h)
    core = [(t, d) for n, t, d in notes if n in ("CORE", "LINUX")]
    f = (ctx.get("field") or "")
    for p in ("nt_prpsinfo_", "prpsinfo_", "nt_auxv_", "auxv_", "core_"):
        if f.startswith(p) and f not in ("core_note_types",):
            f = f[len(p):]
            break
    f = {"fname": "pr_fname", "process_name": "pr_fname", "psargs": "pr_psargs", "command_line": "pr_psargs",
         "cmdline": "pr_psargs", "pid": "pr_pid", "ppid": "pr_ppid", "execfn": "at_execfn",
         "platform": "at_platform", "prstatus_count": "nt_prstatus_count",
         "prstatus_note_count": "nt_prstatus_count", "thread_count": "nt_prstatus_count",
         "num_threads": "nt_prstatus_count", "number_of_threads": "nt_prstatus_count",
         "mapped_files": "mapped_file_paths", "mapped_paths": "mapped_file_paths",
         "nt_file_paths": "mapped_file_paths", "nt_file_mapped_paths": "mapped_file_paths",
         "nt_file_filenames": "mapped_file_paths", "nt_file_entries": "nt_file_entry_paths",
         "nt_file_entry_count": "nt_file_count", "mapped_file_count": "nt_file_count",
         "si_signo": "signal", "pr_cursig": "signal"}.get(f, f)
    if f == "note_types" or f == "core_note_types":
        return [n + ":" + ("0x%x" % t) for n, t, _ in notes]
    if f == "nt_prstatus_count":
        return sum(1 for t, _ in core if t == _NT_PRSTATUS)
    if f in ("pr_fname", "pr_psargs", "pr_pid", "pr_ppid"):
        d = next((d for t, d in core if t == _NT_PRPSINFO), None)
        if d is None or len(d) < 112:
            return "none"
        if f == "pr_fname":
            return d[-96:-80].split(b"\0", 1)[0].decode("utf-8", "replace") or "none"
        if f == "pr_psargs":
            return d[-80:].split(b"\0", 1)[0].decode("utf-8", "replace").rstrip() or "none"
        return struct.unpack_from(e + "i", d, len(d) - 112 + (4 if f == "pr_ppid" else 0))[0]
    if f in ("mapped_file_paths", "nt_file_entry_paths", "nt_file_count", "nt_file_page_size"):
        d = next((d for t, d in core if t == _NT_FILE), None)
        if d is None or len(d) < 2 * w:
            return "none"
        cnt, page = struct.unpack_from(e + q + q, d, 0)
        if f == "nt_file_count":
            return cnt
        if f == "nt_file_page_size":
            return page
        names = d[2 * w + 3 * w * cnt:].split(b"\0")[:cnt]
        paths = [n.decode("utf-8", "replace") for n in names]
        return paths if f == "nt_file_entry_paths" else list(dict.fromkeys(paths))
    if f in ("at_execfn", "at_platform"):
        d = next((d for t, d in core if t == _NT_AUXV), None)
        if d is None:
            return "none"
        want = 31 if f == "at_execfn" else 15
        for i in range(0, len(d) - 2 * w + 1, 2 * w):
            at, val = struct.unpack_from(e + q + q, d, i)
            if at == 0:
                break
            if at == want:
                return _cstr_at(b, loads, val)
        return "none"
    if f == "signal":
        d = next((d for t, d in core if t == _NT_SIGINFO), None)
        if d is not None and len(d) >= 4:
            return struct.unpack_from(e + "i", d, 0)[0]
        d = next((d for t, d in core if t == _NT_PRSTATUS), None)
        if d is not None and len(d) >= 14:
            return struct.unpack_from(e + "h", d, 12)[0]
        return "none"
    return None
