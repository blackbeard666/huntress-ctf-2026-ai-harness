"""ELF hardening flags, checksec style (prebuilt, SPECULATIVE -- never GM-asked yet).

Format tokens `elf`, `binary`, `linux`. Read from the program headers, .dynamic and the symbol tables in the file's
EI_CLASS / EI_DATA layout (helpers shared with prebuilt/elf.py and prebuilt/elf_dynamic.py).
- pie: e_type ET_DYN with a PT_INTERP segment or DT_FLAGS_1 & DF_1_PIE (0x08000000) -> true (readelf "DYN
  (Position-Independent Executable file)", `file` "pie executable"); ET_EXEC -> false; an ET_DYN shared object
  without either -> true (position independent; checksec prints "DSO" -- that spelling when accepted_values lists it).
- nx: PT_GNU_STACK present and its p_flags lack PF_X (1) -> true (readelf GNU_STACK "RW"); PF_X set ("RWE") or no
  PT_GNU_STACK at all (legacy default: executable stack) -> false. executable_stack / execstack = not nx.
- relro: no PT_GNU_RELRO -> "none"; PT_GNU_RELRO plus DT_BIND_NOW (24), DT_FLAGS & DF_BIND_NOW (8) or DT_FLAGS_1 &
  DF_1_NOW (1) -> "full"; else "partial" (checksec "Full RELRO" / "Partial RELRO" / "No RELRO" when accepted_values
  uses those). bind_now = the BIND_NOW test alone (bool).
- canary: `__stack_chk_fail` (or `__stack_chk_guard`, `__intel_security_cookie`) named in .dynsym, else .symtab
  (a static binary) -> true. fortify: any `__*_chk` import other than the stack-protector ones -> true;
  fortified_functions = those names (no @VERSION) in .dynsym order, a JSON list; fortified_function_count = len.
- textrel: DT_TEXTREL (22) or DT_FLAGS & DF_TEXTREL (4) -> true.
Booleans render "true"/"false". Not ELF / truncated header -> "none"; a malformed body never raises (None)."""
import struct

from .elf import _ehdr
from .elf_dynamic import _dynamic, _phdrs, _sections, _symbols

_KINDS = {
    "pie": ["pie", "is_pie", "pie_enabled", "has_pie", "pie_executable", "position_independent",
            "position_independent_executable"],
    "nx": ["nx", "nx_enabled", "has_nx", "is_nx", "nx_bit", "dep", "non_executable_stack", "stack_non_executable"],
    "execstack": ["executable_stack", "execstack", "stack_executable", "has_executable_stack",
                  "is_stack_executable", "gnu_stack_executable"],
    "relro": ["relro", "relro_level", "relro_status", "relro_type", "relro_mode"],
    "bind_now": ["bind_now", "has_bind_now", "dt_bind_now"],
    "canary": ["canary", "stack_canary", "has_canary", "has_stack_canary", "canary_enabled", "stack_protector",
               "has_stack_protector", "stack_chk_fail_present"],
    "fortify": ["fortify", "fortify_source", "fortified", "has_fortify", "is_fortified", "fortify_enabled",
                "has_fortify_source"],
    "fortified_functions": ["fortified_functions", "fortified_function_names", "fortify_functions",
                            "chk_functions", "chk_imports"],
    "fortified_count": ["fortified_function_count", "fortified_functions_count", "fortify_function_count"],
    "textrel": ["textrel", "has_textrel", "dt_textrel", "text_relocations", "has_text_relocations"],
}
_FIELD2KIND = {f: k for k, fs in _KINDS.items() for f in fs}

FIELDS = {
    ("elf", "pie"): "hardening_value",
    ("elf", "is_pie"): "hardening_value",
    ("elf", "pie_enabled"): "hardening_value",
    ("elf", "has_pie"): "hardening_value",
    ("elf", "pie_executable"): "hardening_value",
    ("elf", "position_independent"): "hardening_value",
    ("elf", "position_independent_executable"): "hardening_value",
    ("elf", "nx"): "hardening_value",
    ("elf", "nx_enabled"): "hardening_value",
    ("elf", "has_nx"): "hardening_value",
    ("elf", "is_nx"): "hardening_value",
    ("elf", "nx_bit"): "hardening_value",
    ("elf", "dep"): "hardening_value",
    ("elf", "non_executable_stack"): "hardening_value",
    ("elf", "stack_non_executable"): "hardening_value",
    ("elf", "executable_stack"): "hardening_value",
    ("elf", "execstack"): "hardening_value",
    ("elf", "stack_executable"): "hardening_value",
    ("elf", "has_executable_stack"): "hardening_value",
    ("elf", "is_stack_executable"): "hardening_value",
    ("elf", "gnu_stack_executable"): "hardening_value",
    ("elf", "relro"): "hardening_value",
    ("elf", "relro_level"): "hardening_value",
    ("elf", "relro_status"): "hardening_value",
    ("elf", "relro_type"): "hardening_value",
    ("elf", "relro_mode"): "hardening_value",
    ("elf", "bind_now"): "hardening_value",
    ("elf", "has_bind_now"): "hardening_value",
    ("elf", "dt_bind_now"): "hardening_value",
    ("elf", "canary"): "hardening_value",
    ("elf", "stack_canary"): "hardening_value",
    ("elf", "has_canary"): "hardening_value",
    ("elf", "has_stack_canary"): "hardening_value",
    ("elf", "canary_enabled"): "hardening_value",
    ("elf", "stack_protector"): "hardening_value",
    ("elf", "has_stack_protector"): "hardening_value",
    ("elf", "stack_chk_fail_present"): "hardening_value",
    ("elf", "fortify"): "hardening_value",
    ("elf", "fortify_source"): "hardening_value",
    ("elf", "fortified"): "hardening_value",
    ("elf", "has_fortify"): "hardening_value",
    ("elf", "is_fortified"): "hardening_value",
    ("elf", "fortify_enabled"): "hardening_value",
    ("elf", "has_fortify_source"): "hardening_value",
    ("elf", "fortified_functions"): "hardening_value",
    ("elf", "fortified_function_names"): "hardening_value",
    ("elf", "fortify_functions"): "hardening_value",
    ("elf", "chk_functions"): "hardening_value",
    ("elf", "chk_imports"): "hardening_value",
    ("elf", "fortified_function_count"): "hardening_value",
    ("elf", "fortified_functions_count"): "hardening_value",
    ("elf", "fortify_function_count"): "hardening_value",
    ("elf", "textrel"): "hardening_value",
    ("elf", "has_textrel"): "hardening_value",
    ("elf", "dt_textrel"): "hardening_value",
    ("elf", "text_relocations"): "hardening_value",
    ("elf", "has_text_relocations"): "hardening_value",
    ("binary", "pie"): "hardening_value",
    ("binary", "is_pie"): "hardening_value",
    ("binary", "nx"): "hardening_value",
    ("binary", "nx_enabled"): "hardening_value",
    ("binary", "executable_stack"): "hardening_value",
    ("binary", "relro"): "hardening_value",
    ("binary", "relro_level"): "hardening_value",
    ("binary", "bind_now"): "hardening_value",
    ("binary", "canary"): "hardening_value",
    ("binary", "stack_canary"): "hardening_value",
    ("binary", "fortify"): "hardening_value",
    ("binary", "fortify_source"): "hardening_value",
    ("binary", "fortified_functions"): "hardening_value",
    ("binary", "textrel"): "hardening_value",
    ("linux", "pie"): "hardening_value",
    ("linux", "is_pie"): "hardening_value",
    ("linux", "nx"): "hardening_value",
    ("linux", "nx_enabled"): "hardening_value",
    ("linux", "executable_stack"): "hardening_value",
    ("linux", "relro"): "hardening_value",
    ("linux", "relro_level"): "hardening_value",
    ("linux", "bind_now"): "hardening_value",
    ("linux", "canary"): "hardening_value",
    ("linux", "stack_canary"): "hardening_value",
    ("linux", "fortify"): "hardening_value",
    ("linux", "fortify_source"): "hardening_value",
    ("linux", "fortified_functions"): "hardening_value",
    ("linux", "textrel"): "hardening_value",
}

_CANARY_SYMS = ("__stack_chk_fail", "__stack_chk_guard", "__stack_chk_fail_local", "__intel_security_cookie")
_RELRO_ALIASES = {"full": ["Full RELRO", "full_relro", "FULL"], "partial": ["Partial RELRO", "partial_relro",
                  "PARTIAL"], "none": ["No RELRO", "no_relro", "NONE", "disabled", "no"]}


def _accept(name, aliases, ctx):
    """name, or its spelling in the contract's answer_format.accepted_values."""
    fmt = ((ctx or {}).get("question") or {}).get("answer_format") or {}
    acc = fmt.get("accepted_values") or fmt.get("values") or []
    if not isinstance(acc, (list, tuple)) or not acc:
        return name
    low = {str(a).strip().lower(): str(a) for a in acc}
    for c in [name] + aliases:
        if c.lower() in low:
            return low[c.lower()]
    return name


def _gnu_stack_flags(b, h):
    """p_flags of the PT_GNU_STACK phdr, or None (absent)."""
    esz = 56 if h["is64"] else 32
    if not h["phoff"] or h["phentsize"] < esz:
        return None
    for i in range(min(h["phnum"], 65536)):
        off = h["phoff"] + i * h["phentsize"]
        if off + esz > len(b):
            break
        typ, = struct.unpack_from(h["e"] + "I", b, off)
        if typ == 0x6474E551:
            return struct.unpack_from(h["e"] + "I", b, off + (4 if h["is64"] else 24))[0]
    return None


def _kind(field):
    if field in _FIELD2KIND:
        return _FIELD2KIND[field]
    for suf in ("_enabled", "_present", "_flag", "_status"):
        if field.endswith(suf) and field[:-len(suf)] in _FIELD2KIND:
            return _FIELD2KIND[field[:-len(suf)]]
    return None


def _value(b, h, kind, ctx):
    phs = _phdrs(b, h)
    if kind in ("nx", "execstack"):
        fl = _gnu_stack_flags(b, h)
        nx = fl is not None and not fl & 1
        return nx if kind == "nx" else not nx
    secs = _sections(b, h)
    ents, _ = _dynamic(b, h, secs, phs)
    dyn = {}
    for t, v in ents or []:
        dyn.setdefault(t, v)
    flags, flags1 = dyn.get(30, 0), dyn.get(0x6FFFFFFB, 0)
    bind_now = 24 in dyn or bool(flags & 8) or bool(flags1 & 1)
    if kind == "pie":
        if h["type"] == 2:
            return False
        if h["type"] != 3:
            return "none"
        if any(p["type"] == 3 for p in phs) or flags1 & 0x08000000:
            return True
        dso = _accept("dso", ["DSO", "shared object", "shared_object"], ctx)
        return dso if dso != "dso" else True   # a shared library: position independent, checksec "DSO"
    if kind == "bind_now":
        return bind_now
    if kind == "relro":
        lvl = "none" if not any(p["type"] == 0x6474E552 for p in phs) else ("full" if bind_now else "partial")
        return _accept(lvl, _RELRO_ALIASES[lvl], ctx)
    if kind == "textrel":
        return 22 in dyn or bool(flags & 4)
    n, syms = _symbols(b, h, secs, 11)
    names = [s.split("@", 1)[0] for s, _, _ in syms if s]
    if kind == "canary":
        if any(s in _CANARY_SYMS for s in names):
            return True
        _, ssyms = _symbols(b, h, secs, 2)
        return any(s.split("@", 1)[0] in _CANARY_SYMS for s, _, _ in ssyms)
    chk = []
    for s, ndx, _ in syms:
        s = s.split("@", 1)[0]
        if s.startswith("__") and s.endswith("_chk") and s not in _CANARY_SYMS and ndx == 0 and s not in chk:
            chk.append(s)
    if kind == "fortify":
        return bool(chk)
    if kind == "fortified_count":
        return len(chk)
    return chk


def hardening_value(data, ctx):
    if data is None:
        return None
    try:
        h = _ehdr(data)
        if h is None:
            return "none"
        kind = _kind((ctx or {}).get("field") or "")
        return _value(data, h, kind, ctx) if kind else None
    except Exception:  # noqa: BLE001 -- a malformed ELF never raises past the extractor
        return None
