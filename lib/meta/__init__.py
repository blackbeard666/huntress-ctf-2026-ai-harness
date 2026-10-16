"""lib.meta -- the cumulative metadata-forensics field registry (race-only: the lane solver
challenges/_lane/metadata-forensics/solver/solve.py runs it BESIDE the LLM worker via the reuse race; it never blocks
or replaces the worker).

  REGISTRY  {(fmt, field): Extractor(fn="module:func", tier="verified"|"speculative", days=(N, ...))}
            fmt/field come from the GM question grammar "Determine `<fmt>.<field>` for <member>." (D3+) or the answer id
            `dNN-<fmt>-NNN-<fmt>-<field>` -- keyed on <fmt>-<field>, NEVER on dNN (D10/D11 reused `d09-pe-...`).
            Identity fields (any file) live under fmt "file": filename, size_bytes, md5, sha1, sha256,
            magic_prefix_hex_<N>. A field ending in `_*` is a family (`pe.version_*`, `file.magic_prefix_hex_*`).
  parse_field(aid, q)          -> Field(fmt, field, param) | None
  lookup(fmt, field)           -> (Extractor, param) | (None, None)   (exact key first; verified beats speculative)
  answer(aid, q, data, member) -> (value, tier) | (None, None)         value spelled by lib.meta.spell

Tiers: `verified` = GM-confirmed on that day (days); `speculative` = never asked yet (copied extras from our day
solvers, or LLM-prebuilt modules in lib/meta/prebuilt/). Verified entries live ONLY in _BUILTIN below; a prebuilt
module declares a literal `FIELDS = {("fmt", "field"): "func_name", ...}` (read with ast, imported lazily) and may not
register a key that already has a built-in entry -- such keys are skipped and listed in CONFLICTS (the prebuild gate
and tests/test_meta_lane.py fail on any conflict).

HCTF_META_MAX_DAY=N (fair runs): drop every entry whose first verified day is >= N (speculative entries stay).
Runs inside timed windows on the Homebase VM: stdlib + pip libs only, no subprocess, lazy imports.
"""
import ast
import importlib
import os
import re
from collections import namedtuple
from pathlib import Path

from . import spell as _spell

Extractor = namedtuple("Extractor", "fn tier days")
Field = namedtuple("Field", "fmt field param")
VERIFIED, SPECULATIVE = "verified", "speculative"


def _v(fn, *days):
    return Extractor(f"lib.meta.{fn}", VERIFIED, tuple(days))


def _s(fn):
    return Extractor(f"lib.meta.{fn}", SPECULATIVE, ())


# Every GM-verified field family D1-D15 (+ the never-asked extras the day solvers already carried, speculative).
_BUILTIN = {
    ("file", "filename"): _v("identity:filename", 1),
    ("file", "size_bytes"): _v("identity:size_bytes", 1),
    ("file", "md5"): _v("identity:md5", 1),
    ("file", "sha1"): _v("identity:sha1", 1),
    ("file", "sha256"): _v("identity:sha256", 1),
    ("file", "magic_prefix_hex_*"): _v("identity:magic_prefix_hex", 2),
    ("text", "utf8_bom_present"): _v("identity:utf8_bom_present", 3),
    ("text", "utf16_bom_present"): _s("identity:utf16_bom_present"),
    ("jpeg", "sof_dimensions_pixels"): _v("images:jpeg_sof_dimensions", 4),
    ("png", "ihdr_dimensions_pixels"): _v("images:png_ihdr_dimensions", 5),
    ("pdf", "header_version"): _v("pdf:header_version", 6),
    ("zip", "eocd_total_entries"): _v("zipx:eocd_total_entries", 7),
    ("zip", "central_directory_member_names"): _v("zipx:central_directory_member_names", 8),
    ("pe", "coff_machine_u16_hex"): _v("pe:coff_machine", 9),
    ("pe", "address_of_entry_point_rva_hex"): _v("pe:entry_point_rva", 10),
    ("pe", "version_original_filename"): _v("pe:version_string", 11),
    ("pe", "version_*"): _s("pe:version_string"),
    ("pe", "image_base_hex"): _s("pe:image_base"),
    ("pe", "optional_header_magic_u16_hex"): _s("pe:optional_header_magic"),
    ("elf", "e_machine_u16_hex"): _s("pe:elf_machine"),
    ("elf", "e_entry_hex"): _s("pe:elf_entry"),
    ("elf", "entry_point_hex"): _s("pe:elf_entry"),
    ("dotnet", "mvid_guid"): _v("dotnet:mvid", 12),
    ("msi", "product_code_guid"): _v("msi:property_value", 13),
    ("msi", "upgrade_code_guid"): _s("msi:property_value"),
    ("msi", "product_version"): _s("msi:property_value"),
    ("msi", "product_name"): _s("msi:property_value"),
    ("msi", "manufacturer"): _s("msi:property_value"),
    ("msi", "product_language"): _s("msi:property_value"),
    ("lnk", "target_path_windows"): _v("lnk:target_path", 14),
    ("ooxml", "external_relationship_targets"): _v("ooxml:external_relationship_targets", 15),
    # D16: the GM's format token is `email` (prebuilt eml.py keys `eml`); Message-ID verbatim, angle brackets KEPT
    ("email", "message_id"): _v("eml:message_id", 16),
}

PREBUILT_DIR = Path(__file__).resolve().parent / "prebuilt"
CONFLICTS = []      # [(module, key, reason)] -- prebuilt registrations refused at import


def _prebuilt_fields(path):
    """The literal FIELDS dict of a prebuilt module, read with ast (no import), or {}."""
    try:
        tree = ast.parse(Path(path).read_text())
    except (OSError, SyntaxError, ValueError):
        return {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FIELDS" for t in node.targets):
            try:
                val = ast.literal_eval(node.value)
            except ValueError:
                return {}
            return val if isinstance(val, dict) else {}
    return {}


def _load_prebuilt(base):
    out = {}
    if os.environ.get("HCTF_META_PREBUILT", "1") == "0" or not PREBUILT_DIR.is_dir():
        return out
    for p in sorted(PREBUILT_DIR.glob("*.py")):
        if p.name.startswith("_"):
            continue
        for key, fn in _prebuilt_fields(p).items():
            if not (isinstance(key, tuple) and len(key) == 2 and all(isinstance(k, str) for k in key)
                    and isinstance(fn, str) and fn.isidentifier()):
                CONFLICTS.append((p.stem, key, "malformed FIELDS entry"))
                continue
            if key in base:
                CONFLICTS.append((p.stem, key, f"already registered ({base[key].tier})"))
                continue
            if key in out:
                CONFLICTS.append((p.stem, key, f"also registered by {out[key].fn}"))
                continue
            out[key] = Extractor(f"lib.meta.prebuilt.{p.stem}:{fn}", SPECULATIVE, ())
    return out


REGISTRY = dict(_BUILTIN)
REGISTRY.update(_load_prebuilt(_BUILTIN))


def max_day():
    try:
        return int(os.environ.get("HCTF_META_MAX_DAY", "0"))
    except ValueError:
        return 0


def active():
    """REGISTRY minus entries first verified on/after HCTF_META_MAX_DAY (fair runs)."""
    n = max_day()
    if not n:
        return REGISTRY
    return {k: e for k, e in REGISTRY.items() if not e.days or min(e.days) < n}


def lookup(fmt, field):
    """(Extractor, param) for <fmt>.<field>: the exact key, else the longest matching `_*` family. (None, None)."""
    reg = active()
    e = reg.get((fmt, field))
    if e is not None:
        return e, None
    best = None
    for (f, fld), ext in reg.items():
        if f == fmt and fld.endswith("_*") and field.startswith(fld[:-1]):
            if best is None or len(fld) > len(best[0]) or (len(fld) == len(best[0]) and ext.tier == VERIFIED):
                best = (fld, ext)
    if best:
        return best[1], field[len(best[0]) - 1:]
    return None, None


# Rendering suffixes the GM appends to a field we may already extract under the bare name (D14: it asked
# lnk.target_path_windows; the prebuilt lnk.target_path held the right value and the race lost on the name alone --
# +43 s by the LLM worker instead of ~+3 s).
_RENDER_SUFFIXES = ("_windows", "_posix", "_utc", "_iso8601", "_unix", "_text", "_string", "_str", "_value", "_bytes")
ALIASES = os.environ.get("HCTF_META_ALIASES", "1") != "0"
# Format tokens the GM spells differently from a prebuilt module's key (D16 asked `email.message_id`; prebuilt eml.py
# registers `eml.*`): resolve() retries the same field under the alias format, SPECULATIVE.
_FMT_ALIASES = {"email": ("eml",), "eml": ("email",)}


def resolve(fmt, field):
    """(Extractor, param, field the extractor computes): lookup(), else a NEAR-MISS name, always SPECULATIVE (race-only;
    banking probes absorb a wrong guess): a rendering suffix stripped (`target_path_windows` -> `target_path`), else
    the longest registered same-format field the requested one extends (`<field>_...`). (None, None, None)."""
    ext, param = lookup(fmt, field)
    if ext is not None:
        return ext, param, field
    if not ALIASES:
        return None, None, None
    reg = active()
    cands = [field[:-len(s)] for s in _RENDER_SUFFIXES if field.endswith(s) and len(field) > len(s)]
    cands += sorted((fld for f, fld in reg if f == fmt and not fld.endswith("_*") and field.startswith(fld + "_")),
                    key=len, reverse=True)
    for c in cands:
        e = reg.get((fmt, c))
        if e is not None:
            return Extractor(e.fn, SPECULATIVE, e.days), None, c
    for alt in _FMT_ALIASES.get(fmt, ()):
        e, param = lookup(alt, field)
        if e is not None:
            return Extractor(e.fn, SPECULATIVE, e.days), param, field
    return None, None, None


_TAG = re.compile(r"\s*\[assigned-artifact-sha256:[^\]]*\]")
_Q = re.compile(r"\bDetermine\s+`?([a-z][a-z0-9]*)\.([a-z0-9_]+)`?\s+(?:for|of|in)\b", re.I)
_ID = re.compile(r"^d\d{2}[-_]([a-z0-9]+)[-_]\d+[-_]\1[-_]([a-z0-9-]+)$")
_IDENT = ((re.compile(r"(?:^|-)magic-prefix-hex-(\d+)$"), "magic_prefix_hex_{0}"),
          (re.compile(r"(?:^|-)magic-prefix-hex$"), "magic_prefix_hex_"),
          (re.compile(r"(?:^|-)size-bytes$"), "size_bytes"),
          (re.compile(r"(?:^|-)sha256$"), "sha256"),
          (re.compile(r"(?:^|-)sha1$"), "sha1"),
          (re.compile(r"(?:^|-)md5$"), "md5"),
          (re.compile(r"(?:^|-)filename$"), "filename"))
_SET = re.compile(r"^(?:set|slot)[._-]?\d+[._-]")


def _field(fmt, field):
    return Field(fmt, field, None)


_ID_PATTERNS = []


def _id_patterns():
    """[(fmt, field, compiled `-<fmt>-<field>$` id-suffix regex, size)] of every non-identity REGISTRY key, compiled
    ONCE: ~700 keys x 2 re.search per answer id overflowed re's cache (D16 lane Mastery: 68k compiles, 1 s of 1.05 s)."""
    if not _ID_PATTERNS:
        for fmt, fld in REGISTRY:
            if fmt == "file":
                continue
            dashed = fld.replace("_", "-")
            if fld.endswith("_*"):
                rx = re.compile(rf"(?:^|-){re.escape(fmt)}-{re.escape(dashed[:-1])}([a-z0-9-]+)$")
                _ID_PATTERNS.append((fmt, fld, rx, len(dashed) - 1))
            else:
                _ID_PATTERNS.append((fmt, fld, re.compile(rf"(?:^|-){re.escape(fmt)}-{re.escape(dashed)}$"),
                                     len(dashed)))
    return _ID_PATTERNS


def parse_field(aid, q=None):
    """Field(fmt, field, param) of an answer id (+ its question), or None. Order: the question grammar
    "Determine fmt.field for ...", the id `dNN-<fmt>-NNN-<fmt>-<field>`, an id ending in a registered `-<fmt>-<field>`,
    then the identity suffixes (-filename/-size-bytes/-md5/-sha1/-sha256/-magic-prefix-hex-N)."""
    q = q or {}
    text = _TAG.sub("", str(q.get("question") or ""))
    m = _Q.search(text)
    if m:
        return _field(m.group(1).lower(), m.group(2).lower())
    tail = _SET.sub("", (aid or "").lower()).split(".")[-1]
    m = _ID.match(tail)
    if m:
        return _field(m.group(1), m.group(2).replace("-", "_"))
    best = None
    for fmt, fld, rx, size in _id_patterns():
        mm = rx.search(tail)
        if not mm:
            continue
        hit = (fmt, fld[:-1] + mm.group(1).replace("-", "_")) if fld.endswith("_*") else (fmt, fld)
        if best is None or size > best[0]:
            best = (size, hit)
    if best:
        return _field(*best[1])
    for rx, name in _IDENT:
        mm = rx.search(tail)
        if mm:
            return _field("file", name.format(*mm.groups()))
    return None


def _load(fn):
    mod, _, func = fn.partition(":")
    return getattr(importlib.import_module(mod), func)


def answer(aid, q=None, data=None, member=None):
    """(value, tier) for one answer id from its artifact bytes (`member` = the name after '->'), else (None, None)."""
    q = q or {}
    f = parse_field(aid, q)
    if f is None:
        return None, None
    ext, param, used = resolve(f.fmt, f.field)
    if ext is None:
        return None, None
    if member is None:
        member = str(q.get("artifact") or "").partition("->")[2].strip()
    ctx = {"aid": aid, "question": q, "fmt": f.fmt, "field": used, "param": param, "member": member,
           "artifact": q.get("artifact") or "", "asked": f.field}
    raw = _load(ext.fn)(data, ctx)
    if raw is None:
        return None, None
    return _spell.spell(f.fmt, f.field, raw, q), ext.tier


def known_fields():
    """Every (fmt, field) the active registry can answer, with its tier (docs / prompts)."""
    return {k: e.tier for k, e in sorted(active().items())}
