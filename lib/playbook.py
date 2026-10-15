"""Per-lane field playbooks: the GM's label GRAMMAR per field family.

The dominant failure on the binary and script lanes is not analysis, it is spelling the GM's synthetic
label (e.g. `pe_cli`, `if_guard`, `.text$<sym>`) under coarse per-set feedback. `lib/knowledge.py` holds the
confirmed VALUES and `lib/vocab.json` the confirmed label lists; this module adds, per (lane, field-family):
the derivation RULE, the known-REJECTED spellings, and worked examples, and exposes them to the two consumers
that need them up front:

  - for_lane(lane)                         -> markdown block injected into the worker prompts (point: start
                                              from the rule, not blind synonyms)
  - entry_for(lane, aid)                   -> the PlaybookEntry matching a field by its ending, or None
  - rejected(lane, aid)                    -> spellings already proven wrong for this family (never reprobe)
  - seed_candidates(lane, aid, terms, v)   -> high-priority label candidates for `hctf labels`, built from the
                                              rule (closed vocab, or container+runtime / keyword+ending compounds)

Single source of truth for the confirmed values stays in lib/knowledge.py (imported below). Add a new family
here the moment the GM confirms one, next to the knowledge.py entry.
"""
import re
from dataclasses import dataclass, field

from . import knowledge as K

BINARY = "binary-reverse-engineering"
SCRIPT = "script-analysis"
METADATA = "metadata-forensics"


def field_family(aid):
    """Group fields by their trailing token: 'batch-launcher-control'->'control', 'd03_analysis_format'->'format',
    'set2.cpp-mangled_score_symbol'->'symbol'. Mirrors hctf.labels.ending so the resolver and playbook agree."""
    last = str(aid).rsplit(".", 1)[-1]
    parts = [p for p in re.split(r"[-_]", last) if p]
    return parts[-1].lower() if parts else last.lower()


@dataclass
class PlaybookEntry:
    lanes: tuple           # lanes this applies to
    families: tuple        # field-family endings (field_family(aid)) it covers
    rule: str              # the derivation rule, one or two sentences
    confirmed: tuple = ()  # GM-accepted values seen so far (closed vocab = the whole set)
    rejected: tuple = ()   # GM-rejected spellings: never reprobe these
    examples: tuple = ()   # worked (artifact-feature -> label) notes
    closed: bool = False   # True: confirmed is the COMPLETE allowed set (probe only these)
    derive: object = None  # optional fn(terms, solver_value) -> [candidate, ...] for compound labels


def _symbol_derive(terms, solver_value):
    """PE/COFF wants the COMDAT section-name form; ELF keeps the bare Itanium mangled name. If a PE container is
    in play (a 'pe'/'coff'/'comdat' term) and we have a bare symbol, offer both COMDAT forms first."""
    v = (solver_value or "").strip()
    out = []
    pe = any(t.lower() in ("pe", "coff", "comdat", "pe_cli") for t in terms)
    if v and not v.startswith((".text$", ".rdata$")):
        if pe:
            out += [f".text${v}", f".rdata${v}"]
    return out


def _vbs_control_derive(terms, solver_value):
    """VBScript run-once wrappers outside the confirmed set: seed the unconfirmed candidate spellings (in order) when
    the solver value or an artifact term points at that construct (On Error .. / For p = 0 To 0)."""
    v = (solver_value or "").strip().lower()
    ts = {t.lower() for t in terms}
    out = []
    if v in K.VBS_CONTROL_ON_ERROR_CANDIDATES + K.VBS_CONTROL_ON_ERROR_REJECTED[1:] or ts & {"on", "error", "resume", "err"}:
        out += list(K.VBS_CONTROL_ON_ERROR_CANDIDATES)
    if v in K.VBS_CONTROL_FOR_ONCE_CANDIDATES or "for" in ts:
        out += list(K.VBS_CONTROL_FOR_ONCE_CANDIDATES)
    return out


def _hex_width_derive(terms, solver_value):
    """Metadata `*_hex` header fields are zero-padded to the struct field's width (D9 u16 '0x014c', D10 u32
    '0x00065bd0'; unpadded '0x65bd0' GM-rejected). For an unpadded solver value offer the padded widths it fits."""
    v = (solver_value or "").strip().lower()
    m = re.fullmatch(r"0x([0-9a-f]+)", v)
    if not m:
        return []
    n = int(m.group(1), 16)
    return [f"0x{n:0{w}x}" for w in (4, 8, 16) if n < 16 ** w and f"0x{n:0{w}x}" != v]


PLAYBOOK = [
    # ---- binary-reverse-engineering --------------------------------------------------------------
    PlaybookEntry(
        lanes=(BINARY,), families=("format",),
        rule="Lowercase family name. NATIVE binary = the container only (elf/pe/macho). MANAGED binary = a "
             "container+runtime COMPOUND naming the real-spec terms (a .NET PE is `pe_cli`: PE container + CLI/"
             "ECMA-335 runtime), NOT an analyst synonym.",
        confirmed=tuple(sorted(set(K.BINARY_FORMAT.values()) | {K.DOTNET_FORMAT})),
        rejected=tuple(K.DOTNET_FORMAT_REJECTED) + ("ELF", "ELF64", "elf64-x86-64", "PE32", "PE32+"),
        examples=("ELF->elf", "native PE->pe", ".NET PE->pe_cli (pe+cli)"),
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("symbol",),
        rule="ELF: the BARE Itanium mangled name (_ZNK.., _ZTV..). PE/COFF (MinGW): the COMDAT SECTION-NAME form "
             "— functions `.text$<mangled>`, vtables/typeinfo `.rdata$<mangled>`. Pick by the container, not the OS.",
        examples=("ELF vtable->_ZTV..", "PE function->.text$_ZN..", "PE vtable->.rdata$_ZTV.."),
        derive=_symbol_derive,
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("disassembly",),
        rule="Capstone INTEL syntax, `\"{mnemonic} {op_str}\"` with the default ', ' operand separator, but render "
             "IMMEDIATES IN DECIMAL (e.g. 'mov eax, 8100', not 0x1fa4). One string per instruction.",
        examples=("mov eax,0x1fa4 -> 'mov eax, 8100'",),
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("endianness",),
        rule="Bare word: 'little' / 'big' (NOT 'little endian').",
        confirmed=tuple(sorted(set(K.ELF_ENDIANNESS.values()))), rejected=("little endian", "big endian", "lsb", "msb"),
        closed=True,
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("machine",),
        rule="ELF e_machine -> x86-64 / x86 / AArch64 / ARM (not the EM_* constant). PE FILE_HEADER.Machine 0x14c "
             "-> 'i386' (NOT 'x86' for a PE). answer_format.kind integer (D8): the decimal e_machine, e.g. 62.",
        confirmed=tuple(sorted(set(K.ELF_MACHINE.values()) | set(K.PE_MACHINE.values()) | {"62"})),
        rejected=("EM_X86_64", "x86_64", "amd64"), examples=("PE32 i386 .NET -> i386",),
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("class",),
        rule="readelf style: 'ELF32' / 'ELF64' (not the ELFCLASS* constant). answer_format.kind integer (D8): the bit "
             "width '32' / '64' -- NOT the raw EI_CLASS byte 1 / 2.",
        confirmed=tuple(sorted(set(K.ELF_CLASS.values()) | {"32", "64"})), rejected=("ELFCLASS64", "ELFCLASS32", "1", "2"),
        closed=True,
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("type",),
        rule="e_type submitted AS THE CONSTANT, e.g. 'ET_EXEC', 'ET_DYN' (not 'EXEC').",
        examples=("ET_EXEC", "ET_DYN"),
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("architecture",),
        rule="Container MACHINE vocabulary (same words as `machine`: x86-64/x86/AArch64/ARM/i386), NOT the toolchain "
             "arch token. Go ELF: use ELF e_machine `x86-64`, NEVER the Go buildinfo GOARCH `amd64`.",
        confirmed=tuple(sorted(set(K.ELF_MACHINE.values()) | set(K.PE_MACHINE.values()))),
        rejected=tuple(K.ARCHITECTURE_REJECTED) + ("arm64", "386", "x86_64"),
        examples=("Go ELF GOARCH=amd64 -> x86-64", "Go PE .exe Machine 0x8664 -> x86-64 (D4/D5/D7 Mastery set2)"),
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("names",),
        rule="ELF section_names = pyelftools [s.name for s in iter_sections()] INCLUDING the leading \"\" NULL section "
             "(dropping it is rejected). Preserve table order.",
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("symbols",),
        rule="ELF symbols = [s.name for s in .symtab] in table order, dupes kept; drop only the empty \"\" names. "
             ".NET assemblies use metadata, not .symtab.",
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("version",),
        rule=".NET metadata_version = the CLI metadata root (BSJB) version string, e.g. `v4.0.30319` — NOT net8.0 / the "
             "target-framework moniker / the assembly version.",
        examples=("BSJB root -> v4.0.30319",),
    ),
    PlaybookEntry(
        lanes=(BINARY,), families=("offset",),
        rule="`hcfg_offset` = plain decimal FILE offset (not VA) of the stored config's first byte: base64-stored blob -> "
             "the first base64 char (after any length/cap header); RAW blob -> the 'H' of the b'HCFG' magic. Never "
             "'none' when a config was decoded.",
        examples=("Nim b64 text at 0x77e8 -> 30696 (D9)", "D b64 text -> 368272 (D11)", "FPC raw HCFG at 0x143f0 -> 82928 (D12)",
                  "Crystal String literal: b64 text at 0x88c3c (header 12 B earlier) -> 560188 (D13)"),
    ),
    # ---- metadata-forensics ----------------------------------------------------------------------
    PlaybookEntry(
        lanes=(METADATA,), families=("guid",),
        rule="A GUID's spelling follows its SOURCE, not answer_format. `dotnet-mvid-guid` = Module table Mvid -> #GUID "
             "heap (1-based, 16 B) as .NET Guid.ToString(): first three groups little-endian, lowercase 8-4-4-4-12, no "
             "braces (uuid.UUID(bytes_le=...)). `msi-product-code-guid` = MSI Property table ProductCode string "
             "VERBATIM: uppercase WITH braces (not UpgradeCode / ComponentId / SummaryInfo PackageCode).",
        rejected=tuple(K.MSI_PRODUCT_CODE_GUID_REJECTED),
        examples=("#GUID f3 10 e4 21 77 c9 5c 46 .. -> 21e410f3-c977-465c-.. (D12)",
                  "Property ProductCode -> {DD1A80D5-0250-4F4D-B289-13096D633C61} (D13; bare form rejected)"),
    ),
    PlaybookEntry(
        lanes=(METADATA,), families=("hex",),
        rule="Header integer `<fmt>.<field>_hex` = `0x` + LOWERCASE hex ZERO-PADDED to the struct field's width (u16 -> 4, "
             "u32 -> 8, u64 -> 16 digits), even when the id names no width and answer_format only says 'lowercase "
             "hexadecimal with a 0x prefix'; on PE32+ too (the width is the field's, not the PE flavour). Read the raw "
             "field (an `_rva` is the RVA, not ImageBase+RVA). Byte-prefix fields (`magic_prefix_hex_N`) have NO `0x`.",
        rejected=tuple(K.PE_ENTRY_POINT_RVA_HEX_REJECTED),
        examples=("COFF Machine u16 0x14c -> 0x014c (D9)", "AddressOfEntryPoint u32 0x65bd0 -> 0x00065bd0 (D10)"),
        derive=_hex_width_derive,
    ),
    PlaybookEntry(
        lanes=(METADATA,), families=("filename",),
        rule="A `..-filename` id is the member's OWN name (basename after '->') ONLY when no `version` token precedes it; "
             "`<fmt>.version_<field>` (`d09-pe-NNN-pe-version-original-filename`) = the PE VS_VERSIONINFO StringFileInfo "
             "string verbatim (OriginalFilename), never the randomized member name. The id holds `-pe-` twice: take the "
             "field after the LAST one.",
        examples=("telemetry-agent-001.exe OriginalFilename -> pe-base-386.exe (D11)",),
    ),
    PlaybookEntry(
        lanes=(METADATA,), families=("windows", "path"),
        rule="`lnk.target_path_windows` = the shortcut's LinkInfo LocalBasePath (+ CommonPathSuffix; Unicode offsets "
             "when LinkInfoHeaderSize >= 0x24) VERBATIM with backslashes, else the LinkTargetIDList path (drive item + "
             "file-entry long names). Never the WorkingDir / RelativePath / the .lnk member name.",
        examples=("shortcut-001.lnk LinkInfo -> C:\\Windows\\System32\\cmd.exe (D14; IDList agreed)",),
    ),
    PlaybookEntry(
        lanes=(METADATA,), families=("targets",),
        rule="`ooxml.external_relationship_targets` = every TargetMode=\"External\" Relationship Target across ALL "
             "*.rels parts of the package, compact JSON list SORTED by target string -- never the rels (rId) order. "
             "Internal relationships (no TargetMode) are the decoys.",
        rejected=('["https://example.test/evidence/d87ca62c5bb7","https://example.test/control"]',),
        examples=("document-15-001.docx word/_rels/document.xml.rels rId9 evidence/<hex>, rId10 control -> "
                  "[control, evidence/<hex>] (D15)",),
    ),
    PlaybookEntry(
        lanes=(METADATA,), families=("order",),
        rule="`metadata-day-NN-synthesis-<algo>-order` = the question's `Files: [...]` (members of the artifact's own "
             "container, list varies per Mastery set) sorted by full-file <algo> hex digest ascending (descending only "
             "if the text says so) -> compact JSON list of the names (lib.meta.synthesis.digest_order).",
        examples=("evidence.zip Files [note, camera, agent, docx] by sha256 -> [camera, agent, note, docx] (D15 TT)",),
    ),
    # ---- script-analysis -------------------------------------------------------------------------
    PlaybookEntry(
        lanes=(SCRIPT,), families=("control",),
        rule="CLOSED vocab, named after the cmd grammar on the executed path: `direct` (no construct), "
             "`errorlevel_guard` (`if errorlevel`), `goto_dispatch` (`goto :LABEL`), `call_subroutine` "
             "(`call :LABEL`), `if_guard` (`if defined X` / any `if` test). Name by the IF/GOTO/CALL keyword, "
             "never a descriptive synonym. VBScript (construct wrapping the Decode_<id>() call in Recover_<id>): "
             "`direct`, `select_case` (Select Case 1), `do_once` (Do .. Exit Do .. Loop), `while_once` (While p<1 "
             ".. Wend); an outer `If True Then` block and single-line opaque `If (2 > 1) Then` junk are noise. "
             "VBS `On Error Resume Next` .. Decode_ .. `On Error GoTo 0` (NOT direct / on_error_resume, both GM-rejected) "
             "is `error_guard` — the VBS twin of Batch `errorlevel_guard`: it checks Err after the Decode call and bails "
             "(GM-confirmed Day 4 TT+Mastery). VBS `For p = 0 To 0` -> `for_once` (GM-confirmed D5/D6).",
        confirmed=tuple(K.BATCH_CONTROL_VOCAB) + tuple(c for c in K.VBS_CONTROL_VOCAB if c != "direct")
                 + (K.VBS_CONTROL_ON_ERROR_CONFIRMED,),   # error_guard: GM-confirmed Day 4
        rejected=tuple(K.BATCH_DEFINED_GUARD_REJECTED) + ("linear", "straight_line", "sequential", "goto",
                 "double_pipe", "pipe", "dead_label", "opaque_predicate", "defined_guard", "flag_guard",
                 "do_loop", "do_exit", "while_wend", "while_loop", "on_error_resume"),
        closed=False, derive=_vbs_control_derive,   # batch set is closed; the VBS set is still growing
        examples=("`if defined READY ..`->if_guard", "`if errorlevel 1`->errorlevel_guard",
                  "VBS Do..Exit Do->do_once", "VBS While p < 1..Wend->while_once"),
    ),
    PlaybookEntry(
        lanes=(SCRIPT,), families=("representation",),
        rule="material representation = field 1 of the declared codec (`Codec_<id>`/`CODEC_<id> = \"rep|transform|key\"`) "
             "copied VERBATIM -- never re-describe it. Spelling grammar: <decimal|hex>_<separator name> "
             "(pipe/dash/colon/comma/dot/space/csv), hex_compact/hex_pairs/hex_escape/hex_literal/percent_hex, "
             "base64_literal/base64_chunks/urlsafe_base64, integer_list/integer_tuple, reversed_<x> = loaded in reverse. "
             "`lib.codec.REPS` lists every name seen D3-D6.",
        confirmed=tuple(K.VBS_REPRESENTATION_VOCAB) + tuple(K.VBS_REPRESENTATION_SEEN),
    ),
    PlaybookEntry(
        lanes=(SCRIPT,), families=("transform",),
        rule="reversible byte transform = field 2 of the declared codec, copied VERBATIM, named for the ENCODE side "
             "(subtract_modulo_256 decodes by ADDING the key). `lib.codec.TRANSFORMS` lists every name seen D3-D6.",
        confirmed=tuple(K.VBS_TRANSFORM_VOCAB) + tuple(K.VBS_TRANSFORM_SEEN),
    ),
    PlaybookEntry(
        lanes=(SCRIPT,), families=("expansion",),
        rule="CLOSED vocab, decided by the fragment POOL NAME + the JOIN form in :HUNTRESS_INSPECT (mined from every "
             "GM-verified D3-D6 single/TT case, 0 conflicts in 545): fragments named `h<N>` AND joined with `call set` "
             "(bare or inside `for %%G in (..) do call set`) = `call_double` (33/33); a `for %%G in (..) do call set` "
             "join over any OTHER pool (v_a/item/fragment/FrAg..) = `for_indirect` (122/122); everything else = "
             "`delayed` (390/390) -- including h-pools joined with `!h0!!h1!..` (why D6's h-pools were delayed). "
             "EXCEPT contract run_for_time:false (D15 regular untimed pool, 54/54): the join STATEMENT alone -- FOR = "
             "`for_indirect` over ANY pool, `call set` over h = `call_double`, other `call set` = `percent`, "
             "`!x!` = `delayed`, `%x%` = `percent` (K.BATCH_EXPANSION_STATEMENT_RULE).",
        confirmed=tuple(K.BATCH_EXPANSION_VOCAB),
        rejected=("percent_expansion", "immediate", "call-double", "double_call"),
        closed=True, examples=("h0..h3 + call set->call_double", "h0..h3 + !h0!!h1!->delayed",
                                "for %%G .. call set over v_a/item->for_indirect"),
    ),
    PlaybookEntry(
        lanes=(SCRIPT,), families=("style",),
        rule="JScript code-style labels (closed sets in the question text; GM-confirmed D2-D6): "
             "FUNCTION-style of the named function: `function f(` = declaration, `var f = function(` = "
             "anonymous_expression, `var f = function f_body(` = named_expression. INVOCATION-style = how the "
             "recover/inspect body invokes the next top-level function: plain `f(x)` = direct, `f.call(..)` (also via a "
             "local `invoke` helper that does `block.call`) = call, `f.apply(..)` = apply. PROPERTY-style of the "
             "descriptor reads: only `o.k` = dot, only `o[\"k\"]` = bracket_literal, both = mixed.",
        confirmed=("declaration", "named_expression", "anonymous_expression", "direct", "call", "apply", "dot",
                   "bracket_literal", "mixed"),
        closed=True, examples=("var decode_x = function decode_x_body(s)->named_expression",
                               "invoke.call(null, decode_x, s)->call", "o.steps + o[\"adapter\"]->mixed"),
    ),
    PlaybookEntry(
        lanes=(SCRIPT,), families=("attack",),
        rule="MITRE ATT&CK technique id from the step-graph ROLE. Execution roles map to the host language: batch "
             "launcher/staged_chain=T1059.003, JScript launcher/staged_chain=T1059.007, VBScript launcher/staged_chain="
             "=T1059.005, bash=T1059.004, python=T1059.006, powershell=T1059.001, Node.js=T1059.007 (JavaScript, like "
             "JScript). A graph ending in a handoff is `staged_chain` even if next_stage is a .js file (not 'relay'). "
             "Non-execution roles map by ROLE, never by adapter: persistence_descriptor (build_schedule>"
             "register_descriptor) = T1053.003 even with a systemd_descriptor/npm_lifecycle adapter; bash "
             "advanced_syntax (recognize_syntax>reconstruct_intent) = T1059.004 (Day 7-9). v=3 cross-language plans "
             "(PHP/WSF/HTA D8, Lua/SCT/OpenResty D9) STATE attack=: the PARENT ids T1059/T1053, verbatim.",
        rejected=tuple(sum((list(v) for v in K.JSCRIPT_ATTACK_REJECTED.values()), [])) + ("T1005", "T1560", "T1119"),
        examples=("batch launcher->T1059.003", "jscript staged_chain->T1059.007", "vbscript launcher->T1059.005",
                  "downloader/stager->T1105", "dropper->T1140", "uploader->T1041", "impact->T1486",
                  "nodejs launcher->T1059.007", "nodejs persistence_descriptor->T1053.003"),
    ),
]


def entries_for_lane(lane):
    return [e for e in PLAYBOOK if lane in e.lanes]


def entry_for(lane, aid):
    fam = field_family(aid)
    for e in PLAYBOOK:
        if lane in e.lanes and fam in e.families:
            return e
    return None


def rejected(lane, aid):
    """Spellings proven wrong for this field family, MINUS any that are confirmed-correct in another context within
    the same family (e.g. 'pe' is rejected for a .NET assembly but correct for a native PE; 'direct' is rejected for
    the defined-guard construct but is itself a valid control form). Never skip a value that is sometimes right."""
    e = entry_for(lane, aid)
    return (set(e.rejected) - set(e.confirmed)) if e else set()


def seed_candidates(lane, aid, terms=(), solver_value=None):
    """High-priority label candidates for `hctf labels`, from the playbook RULE: a closed vocab in order, plus any
    derive()-built compound forms. Returns [] when no entry matches (resolver falls back to its own ranking)."""
    e = entry_for(lane, aid)
    if not e:
        return []
    out = []
    if e.derive:
        out += [c for c in e.derive(tuple(terms), solver_value) if c]
    # Closed vocab: probe exactly the allowed set (most-confirmed first); open families: offer confirmed values.
    out += [c for c in e.confirmed if c not in out]
    return out


ENUM_NOTE = (
    "FIRST check each question's `answer_format.kind`. If it is `enum`, the GM HANDS you the closed vocabulary in "
    "`accepted_values` — pick the right one from that list, NEVER probe or guess its spelling (role, scenario, and "
    "true/false fields are all enums). If it is `mitre_attack_id`, submit a `T####`/`T####.###` id (literal `none` "
    "only if permitted). The HARD labels below are always `exact_text` (no list given) — those are the ones that need "
    "the derivation rule + `hctf labels`.")


# The GM's exact_text labels are a small `<short-keyword>_<suffix>` algebra composed from real spec/keyword tokens in
# the bytes — NEVER an analyst's descriptive synonym. Encoding the LAWS (not just per-family lists) lets a worker
# derive the spelling of a NEW construct/host-language before it costs a clock. Proven on pe_cli, if_guard, error_guard.
NAMING_LAWS = (
    "\nGenerator naming LAWS — when an exact_text label is REJECTED, DERIVE the next spelling from these; do NOT "
    "brainstorm descriptive synonyms (every synonym below was GM-rejected):\n"
    "- `<keyword>_guard`: a conditional / error bail-out is named by the SHORT language keyword that opens it — batch "
    "`if errorlevel`->errorlevel_guard, batch `if defined`->if_guard, VBS `On Error Resume Next`->error_guard. The "
    "spelled-out statement is ALWAYS wrong (if_defined, on_error_resume, defined_guard, flag_guard rejected).\n"
    "- `<keyword>_once`: a run-once loop = loop keyword + `_once` — Do..Exit Do->do_once, While..Wend->while_once, "
    "`For p=0 To 0`->for_once (do_exit/while_wend/for_next rejected).\n"
    "- control transfer = `<keyword>_<action>`: `goto :L`->goto_dispatch, `call :L`->call_subroutine.\n"
    "- format = container[_runtime]: native = container only (elf/pe/macho); managed = container + the real runtime-spec "
    "token (.NET PE = pe_cli, from PE + ECMA-335 CLI); msil/dotnet/managed/cil all rejected.\n"
    "- representation = `<numbase>_<separator-name>` (decimal_pipe, hex_colon) or `<base64|hex>_<variant>`; transform is "
    "named for the ENCODE direction (subtract_modulo_256 decodes by ADDING).\n"
    "- ATT&CK execution role scales by host language: launcher/staged_chain -> T1059.{003 batch, 004 bash, "
    "005 vbscript, 006 python, 007 jscript/node.js, 001 powershell}; downloader/stager T1105, dropper T1140, uploader T1041, "
    "impact T1486, persistence_descriptor T1053.003 (by role, not adapter).")


def for_lane(lane):
    """Markdown block for the worker prompt: the label grammar it needs for THIS lane's synthetic fields."""
    es = entries_for_lane(lane)
    if not es:
        return (ENUM_NOTE + "\nNo exact_text synthetic-label family is known for this lane: its remaining answers are "
                "derived VALUES (hashes, decoded strings, manifest fields) in canonical form — derive from the bytes.")
    lines = [ENUM_NOTE,
             "Field-label playbook for this lane's exact_text labels (generator vocabulary — match the RULE, do not "
             "guess synonyms; resolve with `hctf labels` which already seeds from these):"]
    for e in es:
        fam = "/".join(e.families)
        line = f"- **{fam}**: {e.rule}"
        if e.confirmed:
            line += f" Confirmed{' (CLOSED set)' if e.closed else ''}: {', '.join(e.confirmed)}."
        rej = sorted(set(e.rejected) - set(e.confirmed))
        if rej:
            line += f" Already REJECTED (never resubmit): {', '.join(rej[:14])}."
        if e.examples:
            line += f" e.g. {'; '.join(e.examples)}."
        lines.append(line)
    return "\n".join(lines) + NAMING_LAWS
