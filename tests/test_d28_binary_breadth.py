"""D28 post-mortem item 13 ("zero-residual binary"), offline: lib.binary.generic_field + the day28 binary solver's
empty-field fallback. No GM, no network; reads (never writes) the day28 binary solver's regression cases.

1. unit rules on corpus members: ELF e_shnum vs PE NumberOfSections, .symtab-only symbol counts, stripped -> [], the
   predicate / join / sort grammar, answer_format validation, register_generic ordering;
2. the 24 earlier-family fields Day 28's cumulative solver left EMPTY on the single: generic_field alone must answer
   each with the GM-confirmed value (single_solve/expected.json);
3. the solve.py fallback never overrides a non-empty answer, fills only empties, and is off with
   HCTF_BINARY_GENERIC_FIELDS=0;
4. the "known family, new field" matrix: for every family x format of the corpus sample, synthetic GM-style questions
   for each generic field family; every applicable cell must be answered and agree with an independent parser
   (pyelftools / pefile / dnfile / lief / objdump / zipfile / the solver's own classfile parser);
5. tests/data/binary_fixtures/generic/*.json (kind generic_field): each replays to its independent-oracle value --
   the gate for `hctf prebuild --lane binary` "generic field" targets.

Run:  source bin/env.sh && .venv/bin/python tests/test_d28_binary_breadth.py [--full]
      (--full: every case container of the day28 corpus instead of the 3-container sample; exit 0 = all pass)
"""
import hashlib
import io
import json
import os
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDIR = ROOT / "challenges/day28/binary-family-resemblance/solver"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SDIR))
os.environ.setdefault("HCTF_SOLVER_PARALLEL", "0")

import lib.binary as B  # noqa: E402
import solve as S  # noqa: E402

FULL = "--full" in sys.argv
failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


CASES = SDIR / "cases"
SAMPLE = [CASES / "single_solve/artifacts/evidence.zip",
          CASES / "auto-mastery-042de578/artifacts/delivery 10: evidence.zip",   # with delivery 12: every family x
          CASES / "auto-mastery-042de578/artifacts/delivery 12: evidence.zip"]   # format of the corpus (ELF+PE d02/04/10)


def groups_of(container):
    """{dNN: [(name, bytes)]} in archive order."""
    ms = S.resolve(S.unzip(open(container, "rb").read(), lazy=False)) or []
    out = defaultdict(list)
    for n, b in ms:
        m = re.match(r"(d\d\d)", os.path.basename(n))
        if m:
            out[m.group(1)].append((n, b))
    return out


def fmt_of(b):
    return B._gf_fmt(b) or "other"


# ------------------------------------------------------------------------------------------------ 1. unit rules
single = groups_of(SAMPLE[0])
d12 = groups_of(SAMPLE[2])
from elftools.elf.elffile import ELFFile  # noqa: E402
from elftools.elf.sections import SymbolTableSection  # noqa: E402
import pefile  # noqa: E402

SEC_Q = ("In evidence.zip, Use all d10-- members in ZIP central-directory order. Read ELF e_shnum and count the "
         "corresponding section-header-table entries, including section index 0. Submit the count in base 10.")
INT = {"kind": "integer", "syntax": "base-10 integer"}
elf10 = next(b for n, b in single["d10"] if b[:4] == b"\x7fELF")
pe10 = next((b for n, b in d12["d10"] if b[:2] == b"MZ"), None)
check("d10 ELF section_count = e_shnum incl. index 0 (GM 27)",
      B.generic_field(elf10, "section_count", SEC_Q, answer_format=INT) == "27" ==
      str(ELFFile(io.BytesIO(elf10)).num_sections()))
check("d10 PE member present in the sample", pe10 is not None)
if pe10 is not None:
    check("d10 PE section_count = COFF NumberOfSections (GM 9), even though the question says ELF e_shnum",
          B.generic_field(pe10, "section_count", SEC_Q, answer_format=INT) ==
          str(pefile.PE(data=pe10, fast_load=True).FILE_HEADER.NumberOfSections) == "9")
check("ELF section_count excluding index 0 when the question says so",
      B.generic_field(elf10, "section_count", "Count the section-header-table entries, excluding section index 0.")
      == "26")

d13 = single["d13"][0][1]
CRY_Q = ("From ELF symbol-table entries with nonempty resolved names, count names that match "
         "/Crystal|crystal|__crystal|GC_/. Submit the count in base 10.")
both = sum(1 for n in (B.elf_symbol_names(d13, (2, 11), ()) or []) if re.search(r"Crystal|crystal|__crystal|GC_", n))
check("d13 crystal_symbol_count = .symtab only (GM 771, not .symtab+.dynsym)",
      B.generic_field(d13, "crystal_symbol_count", CRY_Q, answer_format=INT) == "771" and both == 1255,
      f"{B.generic_field(d13, 'crystal_symbol_count', CRY_Q)} both={both}")
e13 = ELFFile(io.BytesIO(d13))
pyel = [s.name for sec in e13.iter_sections() if sec["sh_type"] == "SHT_SYMTAB" for s in sec.iter_symbols() if s.name]
check("elf_symbol_names == pyelftools SHT_SYMTAB nonempty names (d13)", B.elf_symbol_names(d13) == pyel)
check("dynamic symbol_count when the question names .dynsym",
      B.generic_field(d13, "dynamic_symbol_count", "Count the nonempty .dynsym symbol names.") ==
      str(sum(1 for sec in e13.iter_sections() if sec["sh_type"] == "SHT_DYNSYM" for s in sec.iter_symbols() if s.name)))
stripped = next(b for n, b in single["d15"] if b".symtab\0" not in b)
check("stripped ELF: symbols [] (SHT_SYMTAB only, no .dynsym fallback; GM D28 Mastery stripped d01)",
      B.generic_field(stripped, "symbols", "What is the exact analysis symbols value?") == "[]")

P = lambda pred: f"Evaluate this public predicate and submit lowercase true or false: true exactly when {pred}."  # noqa
blob = b"\x7fELF" + b"\0" * 60 + b"xx NimMain yy " + "decoy".encode("utf-16-le")
check("predicate: final bytes contain A or B", B.generic_field(blob, "has_nim_runtime",
                                                               P("the final bytes contain NimString or NimMain")) == "true")
check("predicate: Latin-1 or UTF-16LE text",
      B.generic_field(blob, "has_decoy_branch", P("the final bytes interpreted as Latin-1 or UTF-16LE contain the "
                                                  "case-sensitive text decoy")) == "true")
check("predicate: Latin-1 only misses a UTF-16LE-only text",
      B.generic_field(blob, "has_decoy_branch", P("the final bytes contain the case-sensitive Latin-1 text decoy"))
      == "false")
check("predicate: case-sensitive", B.generic_field(blob, "has_x", P("the final bytes contain nimmain")) == "false")
check("predicate: unparseable clause -> None (unsure)",
      B.generic_field(blob, "has_x", P("the program would print hello when run with no arguments")) is None)
d12m = single["d12"][0][1]
check("predicate: bytes OR symbol clause (d12 FPC, GM true)",
      B.generic_field(d12m, "has_fpc_runtime", P("the final bytes contain FPC or any nonempty ELF symbol name "
                                                 "contains FPC_")) == "true")
check("predicate: section membership vs substring",
      B.generic_field(single["d14"][0][1], "has_hcfg_section", P("the parsed ELF section names contain .hcfg")) == "true"
      and B.generic_field(single["d01"][0][1], "has_hcfg_section", P("any parsed executable section name contains the "
                                                                     "lowercase substring hcfg")) == "false")
check("join grammar", B._gf_join("join those digests with ASCII colon characters and no trailing newline") ==
      (":", False) and B._gf_join("join with one LF byte and no trailing LF") == ("\n", False)
      and B._gf_join("join with one LF byte and a trailing LF") == ("\n", True))
d18 = single["d18"][0][1]
pyel18 = [s.name for sec in ELFFile(io.BytesIO(d18)).iter_sections() if sec["sh_type"] == "SHT_SYMTAB"
          for s in sec.iter_symbols() if s.name]
names = sorted(n for n in pyel18 if re.search(r"^_?main$|init", n))
SHA_Q = ("Collect every nonempty ELF symbol name matching /^_?main$|init/, sort strings by ascending code-unit order, "
         "join with one LF byte and no trailing LF, then SHA-256 those UTF-8 bytes.")
check("name-set sha256: regex, sorted, LF-joined, no trailing LF",
      B.generic_field(d18, "init_symbols_sha256", SHA_Q) == hashlib.sha256("\n".join(names).encode()).hexdigest())
check("answer_format: enum value outside accepted_values dropped",
      B._gf_valid("maybe", {"kind": "enum", "accepted_values": ["true", "false"]}) is None)
check("answer_format: integer kind rejects 'none' / text", B._gf_valid("none", INT) is None and
      B._gf_valid("12", INT) == "12")
check("answer_format: 64-hex pattern", B._gf_valid("ABC", {"kind": "pattern", "syntax": "exactly 64 lowercase "
                                                           "hexadecimal characters"}) is None)
check("HCFG fields are never answered generically", B.generic_field(elf10, "config_campaign", "x") is None and
      B.generic_field(elf10, "analysis_xor_key_hex", "x") is None)

calls = []
B.register_generic("t-late", r"zz_probe", lambda ctx, m: calls.append("late") or "LATE")
B.register_generic("t-first", r"section_count", lambda ctx, m: calls.append("first") or "999", first=True)
check("register_generic first=True runs before the built-ins",
      B.generic_field(elf10, "section_count", SEC_Q) == "999" and calls == ["first"])
check("registered late rule answers an otherwise-unknown field", B.generic_field(elf10, "zz_probe", "") == "LATE")
B.GENERIC_FIELDS[:] = [e for e in B.GENERIC_FIELDS if not e[0].startswith("t-")]
check("register_generic entries removable", B.generic_field(elf10, "section_count", SEC_Q) == "27")

# ------------------------------------------------------------------------------------- 2. tonight's residual
RESIDUAL = ["d01_structural_artifact_count", "d01_structural_ordered_set_sha256", "d02_analysis_vtable_symbol",
            "d03_analysis_cli_runtime", "d03_analysis_has_decoy_branch", "d05_analysis_symbol_count",
            "d06_analysis_class_count", "d06_analysis_class_name", "d09_analysis_has_nim_runtime",
            "d10_analysis_section_count", "d11_analysis_d_symbol_count", "d12_analysis_has_fpc_runtime",
            "d13_analysis_crystal_symbol_count", "d17_analysis_conditional_branch_opcode_count",
            "d17_analysis_has_gnat_runtime", "d18_analysis_handler_symbol_count",
            "d18_analysis_handler_symbols_sha256", "d19_analysis_packing_key_1_hex", "d19_analysis_packing_key_2_hex",
            "d20_analysis_overlay_size", "d22_analysis_cli_runtime", "d23_analysis_cli_runtime",
            "d23_analysis_has_decoy_branch", "d26_analysis_method_names_sha256"]
case = CASES / "single_solve"
contract = json.loads((case / "contract.json").read_text())
expected = json.loads((case / "expected.json").read_text())
confirmed = json.loads((SDIR.parent / "single_solve/confirmed.json").read_text())
conf = next(iter(confirmed.values()))
qmap = {q["id"]: q for q in contract["questions"]}
ok = 0
for aid in RESIDUAL:
    day, field = re.match(r"(d\d\d)_(.+)$", aid).groups()
    v = S.generic_answer(field, single[day], qmap[aid])
    good = v == conf[aid] == expected[aid]
    ok += good
    if not good:
        print(f"     residual miss {aid}: got {v!r} want {conf[aid]!r}")
check(f"residual: generic_field alone answers {ok}/24 of tonight's earlier-family empties GM-correctly", ok == 24)

# ------------------------------------------------------------------------------------- 3. never overrides
pairs = [(a, qmap[a]) for a in contract.get("answer_ids") or [q["id"] for q in contract["questions"]]]
art = str(case / "artifacts")
orig_answer = S.answer
S._C = contract
full = S._solve_pairs((art, S._want_shas(contract), pairs))
emptied = set(RESIDUAL)


def run(answer_fn, generic=True):
    S.answer, S.GENERIC = answer_fn, generic
    try:
        return S._solve_pairs((art, S._want_shas(contract), pairs))
    finally:
        S.answer, S.GENERIC = orig_answer, True


def gaps(field, group, q):   # the lane solver without tonight's d28_extra handlers: the 24 residual fields empty
    return None if q.get("id") in emptied else orig_answer(field, group, q)


t0 = time.time()
gap_out = run(gaps)
t_fb = time.time() - t0
check("fallback fills every emptied residual field with the GM value",
      all(gap_out.get(a) == expected[a] for a in RESIDUAL), {a: gap_out.get(a) for a in RESIDUAL
                                                             if gap_out.get(a) != expected[a]})
check("fallback leaves every lane-solver answer byte-identical",
      all(gap_out.get(a) == v for a, v in full.items() if a not in emptied))
off = run(gaps, generic=False)
check("HCTF_BINARY_GENERIC_FIELDS off: emptied fields stay empty", not any(a in off for a in RESIDUAL))
seen = []
real_generic = S.generic_answer
S.generic_answer = lambda *a, **k: seen.append(a) or "GENERIC"
sent = run(lambda field, group, q: "LANE")
S.generic_answer = real_generic
check("a non-empty lane answer is never replaced (generic not even called)",
      not seen and set(sent.values()) == {"LANE"} and len(sent) == len(pairs))
print(f"     single (392 ids, 24 emptied): solve with fallback {t_fb:.2f} s")

# ------------------------------------------------------------------------------- 4. known family x new field
import dnfile  # noqa: E402
import lief  # noqa: E402

try:
    lief.logging.disable()
except Exception:  # noqa: BLE001
    pass
U = "In evidence.zip, Use all {d}-- members in ZIP central-directory order. "
VAGUE = "What is the exact analysis {h} value for field {d}_analysis_{f} in the delivered evidence set?"
LANGS = ("nim", "fpc", "gnat", "go", "rust", "crystal", "d", "swift", "zig")
OWN = {"d04": "go", "d05": "rust", "d08": "swift", "d09": "nim", "d11": "d", "d12": "fpc", "d13": "crystal",
       "d17": "gnat"}
NATIVE = ("elf", "pe", "pe_cli", "macho", "wasm")


def pyelf_syms(b, t):
    return [s.name for sec in ELFFile(io.BytesIO(b)).iter_sections() if sec["sh_type"] == t for s in sec.iter_symbols()
            if s.name]


def text_bytes(b, f):
    if f == "elf":
        s = ELFFile(io.BytesIO(b)).get_section_by_name(".text")
        return None if s is None else s.data()
    pe = pefile.PE(data=b, fast_load=True)
    s = next((x for x in pe.sections if x.Name.rstrip(b"\0") == b".text"), None)
    if s is None:
        return None
    n = min(s.Misc_VirtualSize, s.SizeOfRawData) if s.Misc_VirtualSize else s.SizeOfRawData
    return b[s.PointerToRawData:s.PointerToRawData + n]


def jcc(tx):
    return sum(1 for c in tx if 0x70 <= c <= 0x7f) + sum(1 for i in range(len(tx) - 1)
                                                        if tx[i] == 0x0f and 0x80 <= tx[i + 1] <= 0x8f)


def main_class(jar):
    z = zipfile.ZipFile(io.BytesIO(jar))
    mf = z.read("META-INF/MANIFEST.MF").decode()
    mc = re.search(r"Main-Class:\s*(\S+)", mf).group(1).replace(".", "/") + ".class"
    return S.class_layout(z.read(mc)), z.namelist()


def objdump_sections(b):
    """objdump -h section names (resolves PE "/N" long names through the COFF string table)."""
    import subprocess
    import tempfile
    with tempfile.NamedTemporaryFile(dir=str(ROOT / ".run"), suffix=".bin") as t:
        t.write(b)
        t.flush()
        r = subprocess.run(["objdump", "-h", t.name], capture_output=True, text=True, timeout=30)
    return [ln.split()[1] for ln in r.stdout.splitlines() if re.match(r"^\s*\d+\s+\S", ln)]


def unit_primary_methods(b):
    """Method names of the unit's primary classfile: scalac `object X` -> X$.class (has MODULE$), Clojure gen-class
    -> X__init.class, else the Main-Class itself (parsed with the solver's own classfile reader)."""
    (_, this, meth), names = main_class(b)
    z = zipfile.ZipFile(io.BytesIO(b))
    for alt in (this + "$.class", this + "__init.class"):
        if alt in names and (not alt.endswith("$.class") or b"MODULE$" in z.read(alt)):
            return S.class_layout(z.read(alt))[2]
    return meth


def oracle_overlay(b, f, d):
    for mg in (b"PK19", b"RS20"):
        if mg in b and d in ("d19", "d20"):
            return str(len(b) - b.rfind(mg))
    if f == "elf":
        return str(len(bytes(lief.parse(b).overlay)))
    if f in ("pe", "pe_cli"):
        o = pefile.PE(data=b).get_overlay_data_start_offset()
        return "0" if o is None else str(len(b) - o)
    return None


# (field, question template, applicable formats, oracle(b, fmt, day, group) -> expected str | None (no oracle))
MATRIX = [
    ("section_count", U + "Read ELF e_shnum and count the corresponding section-header-table entries, including section "
                          "index 0. Submit the count in base 10.", NATIVE,
     lambda b, f, d, g: str(ELFFile(io.BytesIO(b)).num_sections()) if f == "elf" else
     str(pefile.PE(data=b, fast_load=True).FILE_HEADER.NumberOfSections) if f in ("pe", "pe_cli") else None),
    ("symbol_count", U + "Count ELF symbol-table entries whose resolved name is nonempty, across the parsed symbol "
                         "tables used by the ELF parser. Submit the count in base 10.", ("elf", "pe", "pe_cli", "macho"),
     lambda b, f, d, g: str(len(pyelf_syms(b, "SHT_SYMTAB"))) if f == "elf" else None),
    ("dynamic_symbol_count", U + "Count the nonempty .dynsym symbol names.", ("elf",),
     lambda b, f, d, g: str(len(pyelf_syms(b, "SHT_DYNSYM")))),
    ("main_symbol_count", U + "Count the nonempty ELF symbol names matching /main/.", ("elf",),
     lambda b, f, d, g: str(sum(1 for n in pyelf_syms(b, "SHT_SYMTAB") if "main" in n))),
    ("init_symbols_sha256", U + SHA_Q, ("elf",),
     lambda b, f, d, g: hashlib.sha256("\n".join(sorted(n for n in pyelf_syms(b, "SHT_SYMTAB")
                                                        if re.search(r"^_?main$|init", n))).encode()).hexdigest()),
    ("has_symtab", U + P("the ELF section-header name table contains .symtab"), ("elf",),
     lambda b, f, d, g: "true" if ELFFile(io.BytesIO(b)).get_section_by_name(".symtab") is not None else "false"),
    ("program_header_count", VAGUE, ("elf",), lambda b, f, d, g: str(ELFFile(io.BytesIO(b)).num_segments())),
    ("overlay_size", U + "Submit the member byte length minus the located overlay magic's zero-based offset.",
     ("elf", "pe", "pe_cli"), lambda b, f, d, g: oracle_overlay(b, f, d)),
    ("conditional_branch_opcode_count", U + "In the ELF .text bytes, count every 0x70..0x7f byte and every two-byte "
                                            "sequence 0x0f followed by 0x80..0x8f; overlapping byte positions are "
                                            "considered by a single left-to-right byte scan.", ("elf", "pe", "pe_cli"),
     lambda b, f, d, g: None if text_bytes(b, f) is None else str(jcc(text_bytes(b, f)))),
    ("text_section_size", VAGUE, ("elf",),
     lambda b, f, d, g: str(ELFFile(io.BytesIO(b)).get_section_by_name(".text")["sh_size"])),
    ("section_names", VAGUE, ("elf", "pe", "pe_cli"),
     lambda b, f, d, g: json.dumps([s.name for s in ELFFile(io.BytesIO(b)).iter_sections()], separators=(",", ":"))
     if f == "elf" else json.dumps(objdump_sections(b), separators=(",", ":"))),
    ("machine", VAGUE, ("elf", "pe", "pe_cli"),
     lambda b, f, d, g: str(int.from_bytes(b[18:20], "little")) if f == "elf" else
     str(pefile.PE(data=b, fast_load=True).FILE_HEADER.Machine)),
    ("file_size", VAGUE, None, lambda b, f, d, g: str(len(b))),
    ("structural_artifact_count", U + "Count the {d}-- members in the ZIP central directory.", None,
     lambda b, f, d, g: str(len(g))),
    ("structural_ordered_set_sha256", U + "Compute each {d}-- member's lowercase SHA-256 in ZIP central-directory "
                                          "order, join those digests with ASCII colon characters and no trailing "
                                          "newline, then SHA-256 the resulting UTF-8 bytes.", None,
     lambda b, f, d, g: hashlib.sha256(":".join(hashlib.sha256(x).hexdigest() for _, x in g).encode()).hexdigest()),
    ("structural_sorted_set_sha256", U + "Compute each {d}-- member's lowercase SHA-256, sort the digests, join them "
                                         "with one LF byte and no trailing LF, then SHA-256 the UTF-8 bytes.", None,
     lambda b, f, d, g: hashlib.sha256("\n".join(sorted(hashlib.sha256(x).hexdigest() for _, x in g)).encode())
     .hexdigest()),
    ("class_count", U + "Count JAR central-directory entries whose names end .class.", ("jar",),
     lambda b, f, d, g: str(sum(1 for n in zipfile.ZipFile(io.BytesIO(b)).namelist() if n.endswith(".class")))),
    ("class_name", U + "Read Main-Class from META-INF/MANIFEST.MF, locate that .class entry, resolve its this_class "
                       "constant-pool name, and submit the exact internal class name.", ("jar",),
     lambda b, f, d, g: main_class(b)[0][1]),
    ("method_count", VAGUE, ("jar",), lambda b, f, d, g: str(len(main_class(b)[0][2]))),
    ("method_names_sha256", U + "Take the primary classfile's unique method names, sort strings by ascending "
                                "code-unit order, join with one LF byte and no trailing LF, then SHA-256 those UTF-8 "
                                "bytes.", ("jar",),
     lambda b, f, d, g: hashlib.sha256("\n".join(sorted(set(unit_primary_methods(b)))).encode()).hexdigest()),
    ("cli_runtime", U + "Read the CLI header major and minor runtime bytes and submit major.minor in base-10 with one "
                        "dot.", ("pe_cli",),
     lambda b, f, d, g: (lambda s: f"{s.MajorRuntimeVersion}.{s.MinorRuntimeVersion}")(dnfile.dnPE(data=b).net.struct)),
    ("metadata_version", VAGUE, ("pe_cli",),
     lambda b, f, d, g: dnfile.dnPE(data=b).net.metadata.struct.Version.rstrip(b"\0").decode()),
] + [(f"has_{lang}_runtime", VAGUE, NATIVE, None) for lang in LANGS]

conts = SAMPLE if not FULL else sorted({p for p in CASES.glob("*/artifacts/**/*.zip")}, key=str)
cells, bad, empty, consist, own_ok = Counter(), [], [], defaultdict(set), []
t_gf = Counter()
seen_sha = set()
for cont in conts:
    for day, grp in groups_of(cont).items():
        if day == "d28":
            continue
        # the member a lane solver picks: the first binary (d03/d22/d23: the primary .dll, not runtimeconfig/FSharp.Core)
        name, b = next(((n, x) for n, x in grp if S.is_binary(x)), grp[0])
        h = hashlib.sha256(b).hexdigest()
        if h in seen_sha and not FULL:
            continue
        seen_sha.add(h)
        f = fmt_of(b)
        for field, tmpl, fmts, oracle in MATRIX:
            if fmts is not None and f not in fmts:
                continue
            q = {"question": tmpl.format(d=day, h=field.replace("_", " "), f=field),
                 "answer_format": INT if field.endswith(("_count", "_size")) or field == "machine" else {}}
            t0 = time.time()
            v = S.generic_answer(field if field.startswith("structural_") else "analysis_" + field, grp, q)
            t_gf[field] += time.time() - t0
            cells[(field, f, "n")] += 1
            if v in (None, ""):
                empty.append((day, f, field))
                continue
            cells[(field, f, "answered")] += 1
            consist[(field, day, f)].add(v)
            if field.startswith("has_") and field == f"has_{OWN.get(day)}_runtime":
                own_ok.append((day, field, v))
            if oracle is not None:
                try:
                    want = oracle(b, f, day, grp)
                except Exception as e:  # noqa: BLE001
                    want = None
                    print(f"     oracle error {day} {f} {field}: {e!r}")
                if want is not None:
                    cells[(field, f, "oracle")] += 1
                    if v != want:
                        bad.append((day, f, field, v[:60], want[:60]))
                    else:
                        cells[(field, f, "agree")] += 1

print("     field x format: answered/n (oracle agree/checked)")
for field, _, fmts, _ in MATRIX:
    row = []
    for f in sorted({k[1] for k in cells if k[0] == field}):
        row.append(f"{f} {cells[(field, f, 'answered')]}/{cells[(field, f, 'n')]}"
                   + (f" ({cells[(field, f, 'agree')]}/{cells[(field, f, 'oracle')]})" if cells[(field, f, 'oracle')]
                      else ""))
    print(f"     {field:34s} " + "; ".join(row) + f"  [{t_gf[field] * 1000:.0f} ms]")
check("matrix: every applicable family x format x field answered (0 empties)", not empty, empty[:12])
check("matrix: every oracle-checked cell agrees with the independent parser", not bad, bad[:12])
check("matrix: each family's own runtime predicate is true",
      all(v == "true" for _, _, v in own_ok) and {d for d, _, _ in own_ok} >= set(OWN), own_ok)
multi = {k: v for k, v in consist.items() if len(v) > 1 and not k[0].startswith(("file_size", "structural"))}
print(f"     {len(consist)} (field, family, format) cells; {len(multi)} vary across members (variant builds): "
      f"{sorted({k[0] for k in multi})}")

# ------------------------------------------------- 5. generic-field fixtures (prebuild "generic field" targets)
FIX = ROOT / "tests/data/binary_fixtures/generic"
fx = sorted(FIX.glob("*.json"))
bad_fx = []
for p in fx:
    try:
        d = json.loads(p.read_text())
        if d.get("kind") != "generic_field":
            continue
        got = B.generic_field((FIX / d["member"]).read_bytes(), d["field"], d.get("question", ""),
                              member=d.get("member_name") or d["member"], answer_format=d.get("answer_format"))
        if got != d["expected"]:
            bad_fx.append((p.name, got, d["expected"]))
    except Exception as e:  # noqa: BLE001
        bad_fx.append((p.name, repr(e), None))
check(f"generic fixtures: {len(fx) - len(bad_fx)}/{len(fx)} replay to their independent-oracle value", not bad_fx,
      bad_fx[:8])
check("generic fixtures: at least one decoy (expected null) present",
      any(json.loads(p.read_text()).get("decoy") for p in fx))

if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall pass")
