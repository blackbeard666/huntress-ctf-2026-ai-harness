"""Central store of GM vocabulary and answer conventions CONFIRMED by correct submissions.

Add to this whenever the Game Master accepts/rejects a specific spelling, so future solvers emit the
exact wording the GM wants instead of re-hitting the wrong-answer cap. Each entry notes where it was proven.
"""

# ELF header fields (binary-reverse-engineering), confirmed Day 1 "ELF Aware".
ELF_ENDIANNESS = {"ELFDATA2LSB": "little", "ELFDATA2MSB": "big"}        # GM rejected "little endian"
ELF_MACHINE = {"EM_X86_64": "x86-64", "EM_386": "x86", "EM_AARCH64": "AArch64", "EM_ARM": "ARM"}  # not "EM_X86_64"
ELF_CLASS = {"ELFCLASS32": "ELF32", "ELFCLASS64": "ELF64"}             # readelf style, not "ELFCLASS64"
ELF_TYPE_AS_IS = True   # e_type submitted as the constant, e.g. "ET_EXEC" (not "EXEC")
# Binary container "format" field (Day 2 "Mangled" cpp_format): bare lowercase family name.
# CONFIRMED PER-FIELD (single-field submits, 2026-10-04): ELF -> "elf", PE -> "pe".
# The earlier "every PE spelling rejected" lore was a MEASUREMENT ARTIFACT: a per-SET POST is all-or-nothing, so
# "pe" always looked rejected only because the SAME PE set also had wrong mangled_score_symbol / vtable_symbol
# (the GM wants their COFF COMDAT section-name form '.text$<sym>' / '.rdata$<sym>' for PE, not the bare symbol).
# Once those two are fixed, "pe" is accepted and the PE set completes. Rejected ELF spellings: ELF, ELF64,
# elf64-x86-64, HCFG, json.
BINARY_FORMAT = {"ELF": "elf", "PE": "pe", "MACHO": "macho"}


def binary_format(kind, member_name="", pe_magic=None):
    """GM `*_format` answer for a parsed container kind ("ELF"/"PE"/...); pe_magic = OPTIONAL_HEADER.Magic."""
    return BINARY_FORMAT.get(kind, kind.lower())

# Day 3 "Table Manners" (binary, managed-configuration), confirmed per-field 2026-10-04:
PE_MACHINE = {0x14c: "i386"}            # PE FILE_HEADER.Machine; "x86" REJECTED for a PE32 i386 .NET assembly
# ELF `section_names`: pyelftools [s.name for s in iter_sections()] INCLUDING the "" NULL section (without it: rejected).
# ELF `symbols`: [s.name for s in .symtab if s.name] in table order, dupes kept (with the "" entries: rejected).
# .NET `metadata_version`: CLI metadata root (BSJB) version string, e.g. "v4.0.30319".
# ELF `disassembly` CONFIRMED 2026-10-04 (Table Manners single): the recover_code leaf rendered as capstone intel
# "{mnemonic} {op_str}" with the DEFAULT ', ' separator but immediates in DECIMAL, e.g. ["mov eax, 8100","ret"]
# (8100 == 0x1fa4). Hex immediates / no-space-after-comma / "ret " / main / whole .text / _start..hlt all REJECTED.
# .NET assembly `format` CONFIRMED 2026-10-04 (GM accepted): "pe_cli" — a PE container holding CLI (Common Language
# Infrastructure / ECMA-335) metadata. The compound names the container + managed runtime, parallel to elf/pe for
# native binaries. Methodology lesson: the generator composes real-spec terms (pe + cli), it does NOT use the common
# analyst synonyms (msil/cil/dotnet/.net/managed were ALL wrong). Same discipline cracked batch control = if_guard.
DOTNET_FORMAT = "pe_cli"
# Day 4 "Go Fish" (Go ELF, go1.25 buildinfo GOARCH=amd64): `architecture` CONFIRMED "x86-64" = the ELF machine
# vocabulary (ELF_MACHINE above), NOT the Go GOARCH token ("amd64" REJECTED). Go config was the same HCFG blob.
ARCHITECTURE_USES_MACHINE_VOCAB = True
ARCHITECTURE_REJECTED = ["amd64"]
DOTNET_FORMAT_REJECTED = [
    "pe", "pe32", "PE", "PE32", "PE32+", "pei-i386", "coff", "winpe", "portable executable",
    "dotnet", "DOTNET", ".net", ".NET", ".Net", "net", "cil", "CIL", "msil", "MSIL", "il", "IL",
    "clr", "clr4", "cor", "COR", "managed", "managed code", "managed pe", "pe-managed", "pe-dotnet",
    "mono", "Mono/.Net assembly", "ilonly", "assembly", "dll", "coreclr", "netcore", "netcoreapp",
    ".NETCoreApp", "net8.0", "dotnetcore", "dotnet assembly", "msil assembly", "ecma-335",
    ".NET Framework", ".NET Core", "framework", "core", "none",
]

# Day 4 "Picture This" (metadata-forensics), confirmed 2026-10-04: jpeg.sof_dimensions_pixels is the SOFn frame
# header size as '<width>x<height>' (X then Y, lowercase 'x', no spaces), e.g. "257x146" — not EXIF/filename dims.
JPEG_DIMENSIONS_FMT = "{width}x{height}"

# Day 5 "Chunk Norris" (metadata-forensics), confirmed 2026-10-05: png.ihdr_dimensions_pixels is the IHDR width/height
# as '<width>x<height>' (same form as the JPEG SOF field), e.g. "269x153".
PNG_DIMENSIONS_FMT = "{width}x{height}"

# MITRE ATT&CK technique the GM expects per scripting scenario (script-analysis), confirmed Day 1 "Power Play".
SCENARIO_ATTACK = {
    "resource_hijacking": "T1496",     # crypto-mining / resource hijacking
    "synthetic_collection": "T1555.003",  # Credentials from Web Browsers (Login Data/Cookies). GM rejected T1005/T1560/T1119
    "synthetic_impact": "T1486",       # data encrypted for impact (ransomware)
}

# Boolean answers are the lowercase words.
BOOL = {True: "true", False: "false"}

# WSH JScript plan roles (script-analysis), confirmed Day 2 "Host With the Most". Role comes from the ordered steps:
# any graph ending in handoff_script is "staged_chain" even when next_stage is a .js file (GM rejected "relay").
JSCRIPT_ROLE_ATTACK_CONFIRMED = {
    "benign_utility": "none", "downloader": "T1105", "stager": "T1105",  # acquire_remote(+write | +dispatch_memory)
    "impact": "T1486", "dropper": "T1140",          # decode_embedded+write_file = Deobfuscate/Decode Files
    "launcher": "T1059.007", "staged_chain": "T1059.007",  # dispatch_process / handoff graphs = JScript execution
    "uploader": "T1041",                            # upload_remote (adapter CertReq.exe)
}
# GM-rejected: launcher T1218.010 (even with adapter regsvr32.exe); stager T1059.007/T1620; dropper T1105/T1027.009
JSCRIPT_ATTACK_REJECTED = {"launcher": ["T1218.010"], "stager": ["T1059.007", "T1620"], "dropper": ["T1105", "T1027.009"]}

# Batch (cmd) plan roles (script-analysis), confirmed Day 3 "Expansion Pack" single solve: same step-graph roles as the
# JScript fixtures; execution-type roles map to the Windows Command Shell instead of JScript.
BATCH_ROLE_ATTACK_CONFIRMED = {
    "benign_utility": "none", "stager": "T1105", "downloader": "T1105", "impact": "T1486", "dropper": "T1140",
    "uploader": "T1041", "launcher": "T1059.003", "staged_chain": "T1059.003",  # relay (handoff to .js) = staged_chain
}
# Batch "expansion form" vocabulary (Day 3): GM accepted bare `delayed`, `for_indirect`, `call_double`.
# Rejected spellings/values: percent, percent_expansion, immediate, call-double, double_call. The GM's per-file value is
# NOT the naive join-line form (percent/CALL joins were `delayed`); see challenges/day03/scripting-expansion-pack notes.
BATCH_EXPANSION_VOCAB = ("percent", "delayed", "call_double", "for_indirect")
# Batch "control-flow form" vocabulary (Day 3 "Expansion Pack", GM-confirmed): `direct` (no control construct on the
# executed path), `errorlevel_guard` (`ver >nul` + `if errorlevel 1 exit /b 1`), `goto_dispatch` (`goto :LABEL` +
# `:LABEL`), `call_subroutine` (`call :LABEL` ... `exit /b 0`). Rejected for `direct`: linear, straight_line,
# sequential, goto, double_pipe, pipe, dead_label (the separator lines and :HUNTRESS_UNUSED are not the control form).
# UNRESOLVED: `set "HUNTRESS_READY=1"` + `if defined HUNTRESS_READY <stmt>`. GM rejected: if_defined, "if defined",
# defined_guard, if_defined_guard, flag_guard, defined_flag, variable_guard, environment_probe, direct, for_loop.
BATCH_CONTROL_VOCAB = ("direct", "errorlevel_guard", "goto_dispatch", "call_subroutine", "if_guard")
# CONFIRMED 2026-10-04: the `set "X=1"` + `if defined X <stmt>` construct = "if_guard" (named after the cmd `if`
# keyword, like errorlevel_guard=`if errorlevel`). This resolved batch-launcher-control + batch-relay-control.
# Methodology: enumerate by the cmd IF grammar (errorlevel/exist/defined comparisons + the `if` keyword), not by
# inventing descriptive synonyms (defined_guard/flag_guard/opaque_* were all wrong).
BATCH_DEFINED_GUARD_REJECTED = ("if_defined", "if defined", "defined_guard", "if_defined_guard", "flag_guard",
                                "defined_flag", "variable_guard", "environment_probe", "direct", "for_loop")
BATCH_DEFINED_GUARD_CANDIDATES = ("environment_guard", "env_guard", "ready_flag", "ready_guard", "sentinel_guard",
                                  "opaque_predicate", "defined_check", "flag_check", "conditional_guard")
# Operator sweep 2026-10-04 ALSO rejected (so ~24 total, field is a synthetic label like .NET `format`): environment_guard,
# env_guard, ready_flag, ready_guard, sentinel_guard, opaque_predicate, defined_check, flag_check, conditional_guard,
# opaque_guard, readiness_guard, define_guard, always_true, tautology_guard. Needs generator source / organizer vocab,
# NOT more probing. Both batch-launcher-control and batch-relay-control take this one (identical `if defined` construct).

# VBScript fixtures (Day 4 "Dim and Dimmer", GM-confirmed single solve 2026-10-04). Plan roles as JScript/Batch;
# execution-type roles map to Visual Basic.
VBS_ROLE_ATTACK_CONFIRMED = {
    "benign_utility": "none", "stager": "T1105", "downloader": "T1105", "impact": "T1486", "dropper": "T1140",
    "uploader": "T1041", "launcher": "T1059.005", "staged_chain": "T1059.005",  # relay (handoff to .vbs) = staged_chain
}
# "control-flow form" = the construct wrapping the Decode_<id>() call in Recover_<id>(), named `<keyword>_once` for the
# run-once loops: `direct`, `select_case` (Select Case 1 / Case 1), `do_once` (Do .. Exit Do .. Loop), `while_once`
# (While p < 1 .. p = p + 1 .. Wend). An outer `If True Then .. End If` wrapper and single-line opaque
# `If (2 > 1) Then x = "left" Else ...` junk are NOISE (still select_case / do_once / direct).
# Rejected: do_loop, do_exit (Do form); while_wend, while_loop (While form).
VBS_CONTROL_VOCAB = ("direct", "select_case", "do_once", "while_once")
# The `On Error Resume Next` / Decode_ / `Err.Number` capture / `On Error GoTo 0` / `If e <> 0 Then Err.Raise ..`
# error-trap wrapping the Decode call. CONFIRMED by the GM: **error_guard** (Day 4 Time Trial + Mastery, attempt
# 03ab2787, 2026-10-04) -- the VBS twin of Batch `errorlevel_guard` (`if errorlevel 1 exit /b`): the construct
# checks Err after the call and bails out. The generator does NOT spell the statement out (cf. do_exit/while_wend/
# if_defined, all rejected). REJECTED spellings: direct (TT 0663ae04), on_error_resume (TT d60a2262).
# How it was found: the generalize worker inferred error_guard from the `<keyword>_guard` sibling grammar; the
# confirm-on-correct sync (labels.record_from_confirmed) now caches it in lib/vocab.json so hb_timed._localize
# fixes this construct IN-WINDOW on future variants with no generalize cycle. Candidates kept for the resolver.
VBS_CONTROL_ON_ERROR_CONFIRMED = "error_guard"
VBS_CONTROL_ON_ERROR_REJECTED = ("direct", "on_error_resume")
VBS_CONTROL_ON_ERROR_CANDIDATES = ("error_guard", "on_error_guard", "err_guard", "on_error_resume_next", "on_error",
                                   "resume_next", "error_trap", "error_resume", "try_catch", "error_handler")
VBS_CONTROL_ON_ERROR = VBS_CONTROL_ON_ERROR_CONFIRMED
# `For pass = 0 To 0` around the Decode_ call (TT 0663ae04 memory-stage.vbs); not yet GM-judged. Named like the other
# run-once loops (`<keyword>_once`).
VBS_CONTROL_FOR_ONCE_CANDIDATES = ("for_once", "for_next", "for_loop")
VBS_CONTROL_FOR_ONCE = VBS_CONTROL_FOR_ONCE_CANDIDATES[0]
# "material representation" / "reversible byte transform" = the first two fields of `Const Codec_<id> = "rep|transform|key"`
# (all GM-confirmed): decimal_pipe, decimal_dash, hex_compact, hex_colon, reversed_decimal (comma list loaded in reverse);
# subtract_modulo_256 (decode ADDS the key), repeating_key_xor, rolling_xor (previous = cipher byte), single_byte_xor,
# reverse_bytes.
VBS_REPRESENTATION_VOCAB = ("decimal_pipe", "decimal_dash", "hex_compact", "hex_colon", "reversed_decimal")
VBS_TRANSFORM_VOCAB = ("subtract_modulo_256", "repeating_key_xor", "rolling_xor", "single_byte_xor", "reverse_bytes")
# Seen in Time Trial 3fd867ae's Codec_ consts (not yet GM-judged): base64_literal (Load_ = Base64_<id>(Material)),
# base64_chunks (Load_ re-joins 4 Mid() slices, then Base64_), hex_dash; reverse_then_xor (result(UBound-i) = s(i) Xor k),
# identity (result(i) = s(i)).
VBS_REPRESENTATION_SEEN = ("base64_literal", "base64_chunks", "hex_dash")
VBS_TRANSFORM_SEEN = ("reverse_then_xor", "identity")

# cmd percent expansion: only %N, %~<mods>N and %* are batch arguments. `%item0%` is a VARIABLE even though the name
# ends in a digit. Time-trial variants name their fragments item0..itemN (Expansion Pack TT fde517bd).
# Python "recovered" fixtures (Day 5 "Hatch Careful", GM-confirmed single solve 2026-10-05, 357/357, no wrong answer).
# The decoded plan (k=v|...) carries adapter/campaign_id/syntax/obfuscation/carrier/windows_chain + indicators verbatim;
# those plan strings are the GM labels. Roles from plan steps: `dispatch_next_stage` graph = **relay** (no handoff_script
# step, unlike JS/Batch/VBS relay files which are staged_chain); profile_host,acquire_remote,decode_embedded,write_file,
# dispatch_process = staged_chain; collect_local,encode_archive,transmit_remote = uploader.
# Execution-type roles map to the Python interpreter, T1059.006.
PY_ROLE_ATTACK_CONFIRMED = {
    "benign_utility": "none", "stager": "T1105", "downloader": "T1105", "impact": "T1486", "dropper": "T1140",
    "uploader": "T1041", "launcher": "T1059.006", "staged_chain": "T1059.006", "relay": "T1059.006",
}
