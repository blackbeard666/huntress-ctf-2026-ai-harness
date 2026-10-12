"""Central store of GM vocabulary and answer conventions CONFIRMED by correct submissions.

Add to this whenever the Game Master accepts/rejects a specific spelling, so future solvers emit the
exact wording the GM wants instead of re-hitting the wrong-answer cap. Each entry notes where it was proven.
"""

# ELF header fields (binary-reverse-engineering), confirmed Day 1 "ELF Aware".
ELF_ENDIANNESS = {"ELFDATA2LSB": "little", "ELFDATA2MSB": "big"}        # GM rejected "little endian"
ELF_MACHINE = {"EM_X86_64": "x86-64", "EM_386": "x86", "EM_AARCH64": "AArch64", "EM_ARM": "ARM"}  # not "EM_X86_64"
ELF_CLASS = {"ELFCLASS32": "ELF32", "ELFCLASS64": "ELF64"}             # readelf style, not "ELFCLASS64"
# Day 8 "Swift Justice": answer_format.kind "integer" on the SAME field names -> elf_class = bit width "64" (not EI_CLASS
# byte 2), machine = decimal e_machine "62" (single + TT + Mastery, 0 wrong; d01 text ELF64/x86-64 accepted alongside).
ELF_CLASS_BITS = {"ELFCLASS32": "32", "ELFCLASS64": "64"}
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
PE_MACHINE = {0x14c: "i386", 0x8664: "x86-64", 0xaa64: "AArch64", 0x1c0: "ARM"}  # PE FILE_HEADER.Machine; "x86" REJECTED for a PE32 i386 .NET assembly; x86-64 GM-confirmed on c_machine/slot*_machine (the lib copy lacked it -> from-scratch replay emitted "0x8664" and failed binary TT twice)
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
# Day 6 "Pool Party" (binary, java-bytecode-loader), confirmed 2026-10-06: a Java .jar's `format` is plain "jar"
# (the archive/container name, like elf/pe). The container_runtime compound "jar_jvm" was REJECTED, so the pe_cli
# law does NOT extend to Java. The HCFG config sat base64'd in a constant-pool String (static final CONFIG).
# Day 7 "Routine Check" re-confirmed "jar" for a Kotlin fat jar (single 22f8c079, TT, Mastery; 0 wrong): the JVM
# source language does not change the container label. HCFG `hcfg_version` = the blob's version as plain decimal ("1",
# D6+D7 confirmed).
# Day 9 "Nimble" (Nim ELF; single + TT + Mastery 5 sets, 0 wrong): NEW field `hcfg_offset` = plain decimal FILE offset of
# the stored blob's first byte -- for a base64 Nim string literal, where the base64 TEXT starts ("30696" = 0x77e8: after
# the 8-byte cap/flag word at 0x77e0, NOT that header and NOT the VA 0x4077e8). Raw/hex-blob offsets still unconfirmed.
HCFG_OFFSET_FMT = "{n}"
# Day 10 "Zig Zag" (Zig cross-compiled ELF + PE; alt single + TT 46625ef1 + Mastery 0c0733e6 3 sets, 0 wrong): NEW enum field
# `has_hcfg_section` = "true" when a section NAMED `.hcfg` exists (ELF section header table / PE section table; the
# Zig PE set had .hcfg between .pdata and .tls). Zig PE x86-64 -> format "pe", machine/architecture "x86-64" (same
# vocab as every native build). crc32_hex "0x%08x" re-confirmed. "false" not yet seen.
JAR_FORMAT = "jar"
JAR_FORMAT_REJECTED = ["jar_jvm"]
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

# Day 6 "Portable Deception" (metadata-forensics), confirmed 2026-10-06: pdf.header_version is the bare x.y of the leading
# `%PDF-x.y` magic (e.g. "1.4"), not the catalog /Version override; an impostor (no header) -> literal "none".
PDF_HEADER_VERSION_FMT = "{major}.{minor}"

# Day 7 "Seven-Zip, No Relation" (metadata-forensics), confirmed 2026-10-07 (single "2", TT "3", Mastery "4"/"5", 0
# wrong): zip.eocd_total_entries is the plain base-10 "total entries" u16 (+10) of the End-Of-Central-Directory record
# (PK\x05\x06) of the zip NAMED after '->' (an inner zip, nested up to 3 deep) -- not the outer download's EOCD. Despite
# the "Seven-Zip" title there was no 7z. Claimed vs walked counts always agreed, so which one wins on a mismatch is OPEN.
ZIP_EOCD_TOTAL_ENTRIES_FMT = "{n}"

# Day 8 "What's in the Box?" (metadata-forensics), confirmed 2026-10-08 (single, TT 6379d17c, Mastery 5 sets; 0 wrong):
# zip.central_directory_member_names (answer_format.kind "json") is the compact JSON array of the FULL stored paths in
# central-directory order -- no basename, dedupe or sort, e.g. ["room-01/item-1.txt","room-02/item-1.txt"] (basenames
# collide, so the directory part is load-bearing). Eocd total entries re-confirmed "2" on the same zip.
ZIP_CD_MEMBER_NAMES_FMT = {"separators": (",", ":")}   # json.dumps(names, **FMT); non-ASCII names not seen yet

# Day 9 "Built Different" (metadata-forensics), confirmed 2026-10-09 (single, TT, Mastery 5 sets; 0 wrong):
# pe.coff_machine_u16_hex is IMAGE_FILE_HEADER.Machine (u16 LE at e_lfanew+4, after 'PE\0\0') as "0x" + 4 zero-padded
# LOWERCASE hex digits: Go 386 PE32 -> "0x014c". NOT the binary lane's word ("i386", PE_MACHINE) -- a `_u16_hex` suffix
# asks for the raw constant. Unpadded "0x14c" never tried; only i386 seen (every "several architectures" decoy was i386).
PE_COFF_MACHINE_U16_HEX_FMT = "0x{:04x}"

# Day 10 "Where Do We Begin?" (metadata-forensics), confirmed 2026-10-12 (single, TT, Mastery 2 sets): id
# d09-pe-NNN-pe-address-of-entry-point-rva-hex = OptionalHeader.AddressOfEntryPoint (u32 LE at e_lfanew+24+16, the raw
# RVA -- not ImageBase+RVA) as "0x" + 8 zero-padded lowercase hex digits, e.g. "0x00065bd0". The id names no width:
# pad to the STRUCT field's size (u32 -> 8), same law as the D9 u16. Unpadded "0x65bd0" REJECTED (D10 single).
# Rehearsal D10 (TT d5b62c7e, Mastery 1f84320c): PE32+ x86-64/AArch64 too ("0x00063a80", "0x00063510") -- the width is the
# FIELD's (u32), not the PE32/PE32+ flavour, while answer_format only says "lowercase hexadecimal with a 0x prefix".
PE_ENTRY_POINT_RVA_HEX_FMT = "0x{:08x}"
PE_ENTRY_POINT_RVA_HEX_REJECTED = ["0x65bd0"]

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
# RULE (mined 2026-10-07 from every GM-verified D3-D6 case, 0 conflicts): `h<N>` pool + `call set` join = call_double;
# `for %%G .. do call set` over any other pool = for_indirect; everything else (incl. h-pool `!h0!!h1!` joins) = delayed.
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
VBS_CONTROL_VOCAB = ("direct", "select_case", "do_once", "while_once", "for_once")
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
# `For pass = 0 To 0` around the Decode_ call = `for_once` -- GM-CONFIRMED (D5/D6 confirmed.json, 13+ fields). Named
# like the other run-once loops (`<keyword>_once`).
VBS_CONTROL_FOR_ONCE_CANDIDATES = ("for_once", "for_next", "for_loop")
VBS_CONTROL_FOR_ONCE = VBS_CONTROL_FOR_ONCE_CANDIDATES[0]
# "material representation" / "reversible byte transform" = the first two fields of `Const Codec_<id> = "rep|transform|key"`
# (all GM-confirmed): decimal_pipe, decimal_dash, hex_compact, hex_colon, reversed_decimal (comma list loaded in reverse);
# subtract_modulo_256 (decode ADDS the key), repeating_key_xor, rolling_xor (previous = cipher byte), single_byte_xor,
# reverse_bytes.
VBS_REPRESENTATION_VOCAB = ("decimal_pipe", "decimal_dash", "hex_compact", "hex_colon", "reversed_decimal")
VBS_TRANSFORM_VOCAB = ("subtract_modulo_256", "repeating_key_xor", "rolling_xor", "single_byte_xor", "reverse_bytes")
# GM-CONFIRMED since (D4-D6 vbscript-*-representation/-transform in confirmed.json): base64_literal, base64_chunks,
# hex_dash, decimal_comma, reversed_hex; reverse_then_xor, identity, add_modulo_256. The answer is ALWAYS the codec
# const's field verbatim; lib.codec.REPS/TRANSFORMS hold every name seen in the evidence (D3-D6).
VBS_REPRESENTATION_SEEN = ("base64_literal", "base64_chunks", "hex_dash", "decimal_comma", "reversed_hex")
VBS_TRANSFORM_SEEN = ("reverse_then_xor", "identity", "add_modulo_256")

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

# Bash "behavior graph" fixtures (Day 6 "Shell We Begin", GM-confirmed single solve 2026-10-06, 399/399 first submit;
# same role->ATT&CK table re-confirmed by Time Trial 9dbb8b8f/5b2a45dd and both sets of Mastery 368acf67).
# `readonly Material_<id>` + `readonly Codec_<id>='rep|transform|key'` (key hex; add_modulo_256 decodes by SUBTRACTING)
# decode to `v=1|steps=..|adapter=..|stage_count=..|campaign_id=..|<indicators>`; plan values verbatim are the answers,
# `steps` joined with '>' is the ordered behavior graph, stage-count = plan stage_count (NOT len(steps)).
# Roles: decode_configuration,return_configuration = benign_utility; acquire_remote,dispatch_pipe (wget -qO- | bash -s)
# = stager; decode_embedded,write_file = dropper; acquire_remote,write_file = downloader; locate_local,dispatch_process
# = launcher; profile_host,acquire_remote,write_file,change_mode,dispatch_process = staged_chain (cron_path/service_name
# are indicators only, NOT a persistence role). Execution-type roles map to the Unix shell, T1059.004.
BASH_ROLE_ATTACK_CONFIRMED = {
    "benign_utility": "none", "stager": "T1105", "downloader": "T1105", "dropper": "T1140",
    "launcher": "T1059.004", "staged_chain": "T1059.004",
    # Day 7 "Node by Node" (single 25ef1864 + TT 516aa6d1 + Mastery 2c52d50f, all first-submit CORRECT): the
    # indirect-expansion.sh / token-fragmentation fixtures decode to steps=recognize_syntax>reconstruct_intent ->
    # role advanced_syntax (feature indirect_expansion|token_fragmentation, primitive parameter_indirection|
    # array_token_construction, plan values verbatim) = Unix shell execution. Day 9 re-confirmed it for
    # trap-handler.sh (trap_handler|function_local_trap) and recursive-walk.sh (recursive_walk|bounded_recursive_function).
    # Day 10 (alt single 30eaee77 + TT + Mastery, 0 wrong): here-string.sh (here_string|here_string_read) and
    # heredoc-reconstruction.sh (heredoc_reconstruction|quoted_heredoc), stage_count 1.
    "advanced_syntax": "T1059.004",
}
# Node.js "operation graph" fixtures (Day 7 "Node by Node", GM-confirmed single 25ef1864, TT 516aa6d1, Mastery
# 2c52d50f; 0 wrong). Same step-graph roles as JScript (Node is JavaScript -> T1059.007 for execution roles) plus a
# NEW role: steps build_schedule>register_descriptor = persistence_descriptor -> T1053.003 (Cron) for EVERY adapter
# seen (systemd_descriptor, npm_lifecycle_descriptor; the schedule_path is /etc/cron.d/...) -- the GM maps the ROLE,
# not the adapter, so don't switch to T1543.002/T1053.006 on a systemd adapter. read_file>transmit_remote = uploader.
NODE_ROLE_ATTACK_CONFIRMED = {
    "benign_utility": "none", "stager": "T1105", "downloader": "T1105", "dropper": "T1140",
    "uploader": "T1041", "launcher": "T1059.007", "staged_chain": "T1059.007",
    "persistence_descriptor": "T1053.003",
}
# Day 8 "Lost in Translation" cross-language v=3 fixtures (polyglot-php-*, host-{php-webshell,wsf-jscript,wsf-mixed,
# hta-jscript}-*; GM-confirmed single + TT 129bf46a + Mastery 07d5051a, 0 wrong). The plan (`HUNTRESS_ANALYSIS_V1:` /
# `descriptor_<id>`, lib.codec.find_codecs) STATES role= and attack= -- submit both verbatim. The GM wants the PARENT
# ids here: execution roles T1059 (even WSF-JScript / WSF-VBScript hosts, NOT .007/.005) and persistence T1053 (NOT
# Node's .003). Steps don't predict the role on v=3 (php webshell decode>return_configuration = staged_chain).
# Day 9 "All the World's a Stager" (single + TT dfcfb51e + Mastery 1dfd4cf6, 0 wrong) extended the same table to Lua
# (polyglot-lua-*, host_profile "standalone") and hosts host_profile "sct_scriptlet" (SCT saved as .js) / "lua_openresty":
# launcher+staged_chain = T1059 again. Lua benign_utility had steps acquire_remote>dispatch_process and Lua staged_chain
# decode_configuration>return_configuration -- take role/attack from the plan, never from the steps.
# Day 10 "Bind Over Matter" (alt single 30eaee77 + TT + Mastery, 0 wrong) added WMI MOF hosts (polyglot-wmi_mof-*.mof,
# plan in a `// HUNTRESS_ANALYSIS_V1:FRAG-..` comment, language=wmi_mof, host_profile "standalone"): launcher+staged_chain =
# T1059 again; MOF benign_utility had steps decode_embedded>write_file>dispatch_process (plan wins again).
V3_ROLE_ATTACK_CONFIRMED = {
    "benign_utility": "none", "stager": "T1105", "downloader": "T1105", "dropper": "T1140", "uploader": "T1041",
    "launcher": "T1059", "staged_chain": "T1059", "persistence_descriptor": "T1053",
}
# Codec_ key field spellings seen in the generator's bytes (Bash, Day 6): contiguous hex for one-byte keys ('1b'), and
# comma-separated hex bytes for multi-byte repeating_key_xor keys ('55,51,74,dd,3a'; Mastery 3bc5446b + GM-correct
# 368acf67). Parsing the comma form as contiguous hex yields key [0] and silently breaks the decode. Use
# lib.scripts.codec_key(), which accepts both (and ':'/space/';'/'-' separators, not yet seen in the bytes).
CODEC_KEY_FORMS = {"hex_contiguous": "1b", "hex_comma": "55,51,74,dd,3a"}
CODEC_KEY_COMMA_TRANSFORMS = ("repeating_key_xor",)
