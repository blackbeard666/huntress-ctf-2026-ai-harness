# script-analysis — technique log (days 1-20; updated after every day)

How this lane has looked so far (these are observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- One AES zip `evidence.zip` (password `infected`) of inert "Huntress Script Triage" fixtures. **The contract is CUMULATIVE**:
  each day keeps every earlier file/question and adds one language; bytes and values re-roll daily. PS (d1, 15 ids) ->
  +JScript (d2, 87) -> +Batch (d3, 159) -> +VBScript (d4, 231) -> +Python (d5, 357) -> +Bash (d6, 399) -> +Node `.mjs` + Bash
  advanced (d7, 469) -> +PHP polyglot + WSF/HTA/PHP-webshell hosts (d8, 615) -> +Lua + SCT/OpenResty hosts (d9, 695) -> +WMI MOF
  (d10, 753) -> +TypeScript (d11, 811) -> +AutoIt (d12, 855) -> +AppleScript (d13, 913) -> +MSBuild `.proj` (d14, 971) -> +Perl
  + perl_cgi host (d15, 1026) -> +Ruby `.rb` + ruby_rack host (d16, 1095; 123 members) -> +AutoHotkey `.ahk` (d17, 1139; 127
  members, no host file, no new Bash) -> +Google Apps Script `.gs` + `google_docs_sidebar` host (d18, 1194; 132 members, no new
  Bash) -> +Roslyn C# script `.csx` + `aspx_inline_csharp` host (d19, 1249; 137 members, no new Bash) -> +Groovy `.groovy` +
  `jenkins_pipeline` host + a `classic_asp` host for OLD VBScript + 2 Bash (d20, 1329; 145 members). Most days also add 2
  Bash advanced fixtures (not d12, d15, d17-d19). Since D8 the TITLE/PROMPT is a pun or narrative; the new language shows up
  only in the member list (D16 "Same Same, But Different" -> Ruby; D17 "Fetch Quest" -> AutoHotkey; D18 "Orphan Process" ->
  Apps Script; D19 "Sharp Practice" / base `managed-assembly-bridge` -> C#; D20 "The Butler Did It" (= Jenkins) / base
  `jenkins-pipeline-intrusion` -> Groovy). Diff the contract ids against yesterday's.
- From day 2 on, every fixture hides a **self-describing plan**: `v=N|steps=a,b|adapter=..|stage_count=..|campaign_id=..|<indicators>`.
  It sits behind a codec, usually named in a `Codec_<id>` / `CODEC_<id>` / `rem HUNTRESS-CODEC:` const of the form `rep|transform|key`.
  Most exact_text answers are plan values copied verbatim. From D8 there is also a **`v=3` plan**: it carries `role=` and `attack=`
  itself, and sits behind a `HUNTRESS_ANALYSIS_V1:<TAG>-` comment.
- The hard part is **naming CODE SHAPE**: control-flow, expansion, and function/invocation/property styles. These are GM synthetic
  labels that are not in the plan. Role and scenario are enums, so read `accepted_values`.
- Files are named by behaviour (host-context, memory-stage, embedded-write, remote-write, local-dispatch, staged-handoff/-chain,
  outbound-transfer, impact-plan, relay-handoff, schedule-descriptor). Answer-id = `<lang>-<role>-<field>`; the artifact path picks
  the file. Don't trust the file name over the plan `steps`.
- Narrative prompts (D8 "doesn't match its siblings", D15 "a store that was never there", D16 "prove which ones are truly
  equivalent, expose the variant that quietly changed the plot", D17 "reconcile source fetch targets with the generated network
  evidence ... the indicator on only one side", D18 "native telemetry keeps its own record ... reconstruct the static process
  tree, catch the child claiming a parent it never had", D19 "work out where the bridge actually leads" = just the per-file
  `next-language` id, D20 "separate controller semantics from agent semantics, trace the build into its prior-language stages") have NEVER been asked as a question; no network/process telemetry has shipped. Answer the contract ids.
- Time Trial windows ~5-17 s. Mastery has `setN.` ids: 2 sets d2-d7 and d10-d14, **5 sets d8, d9, d15 (5130 ids) and d16 (5475
  ids), d17 (5695), d18 (5970), d19 (6245), d20 (6645)**. The artifact was `evidence-0N.zip`, `delivery N: evidence.zip` (d6), or one
  `evidence-01.zip` holding every `evidence-0N.zip` (d7-d9). Same-named deliveries: pair by sha256. Timed questions carry `[assigned-artifact-sha256:<hex>]`.
  From D15 the timed contracts are the untimed regular pool (`run_for_time:false`, `variant_fresh:true`, no deadline).

## Variant axes (what differs between the single, Time Trial and Mastery variants of the SAME day -- parse every value listed)
Each miss cost one failed timed attempt + a ~45-90 s generalize cycle (D6: 4 cycles; D7: 1; D8-D14: 0; D15: TT localize + 1
Mastery cycle; D16: runner timeouts only). **D17-D20: no axis** -- TT/Mastery first try, 0 new VARIANT AXIS lines, `novel_labels:
{}`; each day's new carrier shape (D18 SPLIT array, D19 escaped-nested ASPX, D20 plain Groovy/ASP one-liners) was identical in
every mode, only values re-rolled. D20 auto cases (TT 717b8371, Mastery 1478867c) are value re-rolls only.
- **GM label regime (batch `expansion`; D15 pool-keyed, D16 DATE-keyed)** -- SAME bytes, SAME question text, DIFFERENT label.
  Old regime (every D3-D14 case + the D15 single): the whole handoff is labelled, `echo(!var!)` => `delayed` unless a FOR/h-pool
  rule fires. Statement regime (D15 TT/Mastery `run_for_time:false`; D16+ every mode incl. the single): label the JOIN
  STATEMENT alone -- `!a!!b!` join = delayed; `for %%G in (..) do call set` = for_indirect for ANY pool; bare `call set
  "x=%%h0%%.."` (h pool) = call_double; bare `call set` over item/v_a/FrAg pools = percent; plain `set "x=%a%%b%"` = percent.
  Parse rule: **statement regime is the default** (`run_for_time is False` OR `started_at >= 2026-10-16`; `lib.codec.
  label_regime`/`label_expansion`); old regime only for older replayed cases. When byte-identical constructs get different
  labels, tabulate (construct, label) against EVERY contract key (started_at, run_for_time, variant_fresh) at once.
- **Codec per file** -- rep x transform x key re-rolls per variant; never bind a role to the sample's codec. **NEW rep NAMES
  appear only on variants** (D7 TT: `unicode_escapes`, `json_numbers`, `reversed_base64`, Bash `xor_hex|cd`). Decode by the
  material's SHAPE (escapes / int array / hex / base64, each also reversed) x the named transform; accept only output starting
  `v=`; the name only orders the tries. D9-D16: nothing beyond lib.codec's vocabulary (0 decode failures).
- **Codec spec arity** -- `rep|transform|key`, `rep|` (empty transform = identity; Bash advanced D7-D16), or transform folded
  into the rep with the key second (`xor_hex|cd`, D16 `xor_hex|ec`). Split on `|`, never index blindly (lib.codec `_spec`).
- **Plan carrier tag (v=3, D8-D16)** -- `HUNTRESS_ANALYSIS_V1:<TAG>-<data>` + the same data in a descriptor literal. Tags `B64`,
  `HEX`, `HB64` (hex of base64), `FRAG` (hex split by `.` every 24 chars); stayed fixed per file in every delivery D8-D17, only
  values re-rolled. Parse rule: ignore the tag name; peel by shape, recurse (max 3-4 layers); accept only `v=`. Tag =
  `obfuscation_profile` (B64 base64, HEX plain_hex, HB64 hex_base64, FRAG fragmented_hex). `lib.codec.find_codecs(src)` returns it.
  **D18 `SPLIT` is a LAYOUT tag, not an encoding**: `// HUNTRESS_ANALYSIS_V1:SPLIT` stands alone on its line and the data is the
  next multi-line literal array `const HUNTRESS_ANALYSIS_V1_SPLIT_<8hex> = ["<TAG>-chunk", "chunk", ..].join("")`; the real tag
  (FRAG/HEX/HB64/B64) is the first chunk's prefix, and `buildAnalysisPlan_<id>()` holds an untagged copy (`const encoded_<id> =
  [..].join("")`). Parse rule: if the marker match has no data, join every all-literal array / concat run in the file
  (quotes `"` `'` and backticks), strip a leading `[A-Za-z0-9_]{1,12}-`, peel; keep the one that yields `v=`. Patched in the
  D18 solve.py (`_v3` candidates); lib.codec.v3_plan handles it since the D18-night prebuild.
- **Plan carrier NESTING (D10 MOF ScriptText, D19 ASPX)** -- the whole inner script is a string literal of the host:
  `<%@ Page Language="C#" %><script runat="server"> private static readonly string EmbeddedCsx_<8hex> = "// HUNTRESS_ANALYSIS_V1:
  HEX-<data>\n#nullable enable\n..string descriptor_<id> = \"<data>\";\n";`. In raw bytes the marker data runs on into a
  literal `\n#nullable` and the descriptor is `\"`-quoted, so the carried regexes find nothing. Parse rule: when a v=3 file
  yields no plan, unescape string-literal escapes (`\n \" \\ \t`, C# verbatim `""`, VB `""`, XML `&quot;`/CDATA, JSON
  `\u0022`) and rescan; or stop marker data at `\`. `lib.codec.v3_plan` already decoded the D19 ASPX file at solve time
  (the carried solve.py did not call it) -- **fall back to lib.codec.v3_plan before anything else**.
- **Plan carrier host syntax (v=3)** -- marker in whatever comment the host uses: `//` (PHP, JS, HTA, WSF, SCT, MOF, TS), `--`
  (Lua, AppleScript), `;` (AutoIt, AutoHotkey), `<!-- -->` (MSBuild), `#` (Perl D15, Ruby D16). Descriptor forms: `$descriptor_<id>`,
  `var/local descriptor_<id>`, `Global Const $descriptor_<id>`, `property descriptor_<id> :`, `<HuntressDescriptor>` element
  (MSBuild, no name), `my $descriptor_<id> = "..";` (Perl), `DESCRIPTOR_<8HEX> = ".."` uppercase Ruby constant (D16),
  **`descriptor_<8hex> := ".."` AutoHotkey v2 (D17)**, C# `string descriptor_<8hex> = "..";` + `BuildPlan_<id>() => new
  Dictionary<string,string> { ["descriptor"] = .. }` (D19), Apps Script `const HUNTRESS_ANALYSIS_V1_SPLIT_<id> = [..].join("")` +
  `Object.freeze({ descriptor: encoded_<id> })` (D18), Groovy `final String descriptor_<8hex> = ".."` + `def buildPlan_<id> = { ->
  [descriptor: ..].asImmutable() }` (D20), classic ASP `Dim descriptor_<8hex>` then `descriptor_<8hex> = ".."` on the NEXT line
  inside `<% %>` with a `'` marker (D20). Never anchor on `=` / `:=` / `set` / `<-` -- parse rule: regex
  `HUNTRESS_ANALYSIS_V\d+\s*:\s*(\w*)-?\s*([^\s"'<>\]]+)` over raw bytes, any comment syntax/case/extension; if the data group
  is empty (`SPLIT`), fall through to the literal-array join above.
- **Literal shapes (D6-D7)** -- radix: decimal `23,7`, hex `0x17`, or a joined string read by `parseInt(x, R)`/`int(x, R)` --
  READ THE RADIX FROM THE CODE (keys too); base64 standard AND urlsafe (whitelist + pad); reversal of the LIST
  (`reversed_hex/_decimal/_integer_list`) vs the TEXT (`reversed_base64`) -- try both; material as one literal, split chunks,
  `+=`, adjacent strings, `.`-FRAG, D18 multi-line `[..].join("")` -- join first; same-language carrier may be a frozen exe (D6
  cx_Freeze) -- locate by markers (`MATERIAL_`/`CODEC_`/`v=`/`HUNTRESS_ANALYSIS_`), never by file type.
- **Adapter values** re-roll within a role (Node stager http_then_module/https_then_vm/fetch_then_function; launcher
  execfile_node/fork_module/spawn_file; persistence systemd_descriptor/npm_lifecycle_descriptor) -- always plan-verbatim.
- **Transport/runner, not variant** -- D7 TT saved `{"error":"rate_limited"}` as the zip; D8 TT start 503
  `training_rotation_invalid`; D16 Mastery hit the 60 s local `hb_timed` cap (fixed: D17-D19 Mastery 12-18 s, start+submit
  ~70 % of it, solve 0.5-5.6 s). None of these is a solver change; never harvest them as cases.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "method=AES Encrypted" | Triage already extracted it (`work/extracted/`) and decoded every plan. Diff the member list / contract ids against yesterday's to find the new language (D16: 4 `polyglot-ruby-*.rb` + `host-ruby-rack-ruby.rb` + 2 `.sh`). Triage used to skip new extensions (D7 `.mjs`, D8 `.php`, D9 `.lua`); D15-D16 it decoded them. Open members with `lib.common.read_member` (zipfile can't read AES). |
| Prior-day languages in the contract | Cumulative: rerun the carried marker-routed solver FIRST (D9-D17 and D20: it covered each new v=3 language unchanged; D18 and D19 each needed a CARRIER patch). Any file it leaves planless: try `lib.codec.v3_plan(text)` next (it had D19's fix already). Spend thinking on the new language and on synthetic-label regimes. |
| `.ps1` `$encodedMaterial = [Convert]::FromBase64String('..')` + `$nativeTypes` | `base64 -d` -> JSON descriptor: url/wallet/mutex/UA/file/ext/note by SHAPE. `$nativeTypes` gives the scenario: Process/Registry+wallet=resource, ZipFile/HttpWebRequest=collection, Aes/DirectoryInfo=impact. |
| `.js` WSH, `decode_*`/`recover_*`/`inspect_*`, XOR key arrays, `"52:90:.."` | Run each file in an empty `node` `vm` (no require/ActiveXObject, `eval` -> capture); keep the first object with `steps`. Styles come off the `inspect_*` body. |
| `.bat/.cmd` `rem HUNTRESS-CODEC:` / `HUNTRESS-MATERIAL:`, `set "itemN=..`, `:HUNTRESS_INSPECT` | Plan is in `set` fragments. Emulate cmd expansion in Python. MATERIAL = second encoded copy to cross-check. Expansion label: statement regime by default (Variant axes). Never run cmd. |
| `.vbs` `Const Material_<id>`, `Const Codec_<id> = "rep|transform|key"` | Decode from the Codec const; rep/transform answers = Codec fields 1/2 verbatim. Control = construct wrapping `Decode_` inside `Recover_`. |
| `.py` `*-recovered.py` with `MATERIAL_<id>`, `CODEC_<id>` | Decode from CODEC (or AST-whitelisted `decode_(load_(..))`). Plan v=2 carries syntax/obfuscation/carrier/windows_chain verbatim. |
| `.sh` `readonly Material_<id>` + `readonly Codec_<id>` (+ `Feature_<id>()`) | Decode from the Codec const (multi-byte key = COMMA list). `Feature_` fixtures: role `advanced_syntax`, feature/primitive/campaign/stage_count/steps plan-verbatim, attack T1059.004. Never run bash. |
| `.mjs` ESM `const Material_<id>`, async `load_/decode_/recover_/inspect_/plan_<id>` | Static decode (`lib.codec.find_codecs` + shape fallback). Don't run it. Plan fields verbatim; role from `steps`. |
| `HUNTRESS_ANALYSIS_V1:<B64|HEX|HB64|FRAG>-..` in any comment + a descriptor literal (`.php .lua .js(HTA/WSF/SCT) .vbs(WSF) .mof .ts .au3 .applescript .proj .pl .rb .ahk`) | **Route by the marker before the extension.** Peel to `v=3|language=..|role=..|attack=..|adapter=..|host_profile=..|obfuscation_profile=..|stage_profile=..|next_language=..|stage_count=..|steps=..|campaign_id=..|url=..|file_path=..`. EVERY answer incl. role/attack is plan-verbatim. |
| Prompt about fetch targets vs "network evidence" / "only one side" (D17), zip holds only scripts | Flavour: answer the per-file ids. If a pcap/HAR/Zeek/proxy/DNS/Sysmon file ships: `lib.codec.network_indicators(bytes)`, `reconcile({member: plan}, bytes)` -> `reconcile_answer(r, kind, accepted_values, what=)` (original spelling); declared side `fetch_sites(src)`; chain/root/leaf ids `download_graph(plans)` + `download_graph_answer`; tshark = oracle only. |
| `HUNTRESS_ANALYSIS_V1:SPLIT` (marker with NO data on its line) + `const HUNTRESS_ANALYSIS_V1_SPLIT_<id> = [ "FRAG-..", "..", ..].join("")` (D18 `.gs`) | Multi-line literal-array carrier. Join the array's literals, drop the `<TAG>-` head of chunk 1, peel as usual (lib.codec.v3_plan and the D18+ solve.py `_v3` loop both do). If the 44 new ids come back unanswered, fix the CARRIER read first -- never walk the role enum. |
| `.csx` `#nullable enable` / `using System..;` / `string descriptor_<8hex> = ".."` / `BuildPlan_<id>() =>` (D19 Roslyn C# script) | Ordinary v=3 marker + descriptor: plan-verbatim. `language=csharp_script`, campaign `CSHARP_SCRIPT-<8hex>`, url host `csharp_script-<10hex>` (underscore kept), attack T1059/T1105/none. |
| `<%@ Page Language="C#" %>` + `<script runat="server">` + `EmbeddedCsx_<id> = "// HUNTRESS_ANALYSIS_V1:..\n..\"..\";"` (D19 host `aspx_inline_csharp`, file `.csx`) | NESTED carrier: the inner script is an escaped string. Unescape `\n`/`\"`/`\\` (and `""`, `&quot;`, CDATA for siblings: .ashx/.asmx/.cshtml/.jsp/classic .asp) and rescan; `lib.codec.v3_plan` already does. The `InertRequest_<id>` method and `<%= .. %>` output are noise. |
| `.groovy` `final String descriptor_<8hex> = ".."` / `def buildPlan_<id> = { -> [descriptor: ..].asImmutable() }` / `pipeline { agent none; stages { stage(..) { steps { echo .. } } } }` (D20 Groovy + `jenkins_pipeline` host) | Ordinary one-line v=3 (`//` marker): plan-verbatim, carried solver answered all. `language=groovy`, campaign `GROOVY-<8hex>`, url host `groovy-<10hex>`, attack T1059/T1105/none. The `pipeline {}` block is inert noise; controller/agent split never asked. |
| `<%@ Language=VBScript %>` + `<% ' HUNTRESS_ANALYSIS_V1:..` + `Dim descriptor_<id>` / `Response.Write` in a `.vbs` (D20 `host-classic-asp-vbscript`) | A v=3 host for an OLD language: the marker plan says `language=vbscript`, campaign `VBSCRIPT-`, host_profile `classic_asp`. Route by the marker before `.vbs` (there is no Codec_ const); plan-verbatim. |
| Prompt about a process tree / "native telemetry" / "child claiming a parent it never had" (D18) | Flavour so far. If Sysmon EID 1 / 4688 / auditd / ps-forest evidence ships: `lib.codec.process_events(bytes)` -> `process_tree` -> `process_tree_answer`; declared side `declared_spawns(plans, sources)` (+ `spawn_parent_candidates` for WMI/COM/schtasks proxy parents); liar = `reconcile_processes(declared, observed)` -> `reconcile_processes_answer` (PPID spoofing T1134.004). |
| An id whose field suffix is a plan key never asked before (`-verdict`, `-language`, ...) | `lib.codec.plan_answer(answer_id, plan, q)` / `plan_key_for` (longest suffix, hyphen->underscore, aliases). Copy plan-verbatim. |
| Timed contract `run_for_time:false`, or any contract started on/after 2026-10-16 | Batch `expansion` = statement-only table. Check the contract keys before trusting labels harvested from older cases. |
| Real `.pyc` / PyInstaller / pyarmor (not seen yet) | `lib.pyc.recover_python(path)` (pyinstxtractor-ng + decompyle3, `dis` fallback). |
| `Codec_` key like `ba` / `0a` / `ec` | A hex byte. Transforms are ENCODE-side names: `subtract_modulo_256` decodes by ADDING; `rolling_xor` = c ^ previous CIPHER byte, seeded with the key. |

## Codec table (`Codec_<id>='<rep>|<transform>|<key>'`, batch `rem HUNTRESS-CODEC:<rep>|<transform>`; seen D3-D16)
triage.md "Decoded payloads" already runs `lib.codec` on every declared codec; in solve.py use `lib.codec.find_codecs(text)` /
`lib.codec.decode(material, rep, transform, key)` (unknown names -> None => decode by shape, note it in `## Proposed lib additions`).
Reps: base64 (literal/chunks/urlsafe/reversed), hex (pairs/compact/colon/dash/`\x`/`0x`/buffer/array), percent_hex,
escaped_octets, unicode_escapes, decimal lists (any separator)/json_numbers/integer_list/tuple, octal_space, reversed_text/_hex/
_decimal/_integer_list, plain/split_fragments, v=3 hex_base64. Transforms (key hex; multi-byte = COMMA list): identity (also
EMPTY), reverse, single_byte_xor, repeating_key_xor, reverse_then_xor, rolling_xor, add_modulo_256 (decode SUBTRACTS),
subtract_modulo_256 (decode ADDS); batch names carry the parameter (xor_5a, add_7 decimal); bash `xor_hex|<key>` = unhex then
XOR. Check: plaintext starts `v=` (or `{`), else the codec reading is wrong.

## Day by day
**D1-D7 (PS -> +JScript -> +Batch -> +VBScript -> +Python -> +Bash -> +Node, 469 ids)**: D1 collection ATT&CK cost 5 wrong before
`T1555.003`; D2 handoff = `staged_chain`, 7 wrong ATT&CK guesses; **D3 ~1 h 45 min, ~127 rejected probes** on batch
expansion/control labels -> NAMING LAWS; D4 VBS control probed one field at a time (4 wrong); D5-D6 0 wrong (~4 min; stage_count =
plan field); D7 469/469 in ~100 s, TT missed 15 ids on new reps + one `rate_limited` body saved as the zip.
**D8-D15 (+PHP polyglot & hosts, Lua/SCT/OpenResty, MOF, TS, AutoIt, AppleScript, MSBuild, Perl; 615 -> 1026 ids)**: D8 introduced
v=3 (copy role/attack/adapter/profiles, don't derive); 6 ids lost once to hyphenated family names. Each new language = 4 polyglots
(benign_utility/downloader/launcher/staged_chain; attack none/T1105/T1059/T1059; adapter local_parser/http_client/process_builder/
operation_graph; campaign `<LANG>-<8hex>`, url `https://<lang>-<10hex>.example.invalid/stage`, file_path
`/tmp/huntress-<lang>/.<16hex>.stage`) + sometimes one `host-<profile>-<lang>` file. D14 family had an underscore (`msbuild_xml`)
and its prompt's ATT&CK (T1127.001) was NOT the answer (plan said T1059). D8-D14 all modes first try. D15: single 1026/1026 at
T+17 s; TT and Mastery (5 sets) missed ~25 batch-expansion ids -> the label-regime axis; CORRECT ~5.5 min after start.
**D16-D17 (+Ruby `.rb` + `ruby_rack` host + 2 Bash; then +AutoHotkey `.ahk`, no host; 1095 -> 1139 ids)**: equivalence and
network-reconcile prompts never asked. Ruby `DESCRIPTOR_<8HEX> = ".."`, AHK `descriptor_<8hex> := ".."`, plan-verbatim. D16
single lost 5 probes on batch expansion (statement regime keyed on `started_at`), CORRECT T+4 min 23 s; D17 carried solver T+13 s.
**D18 Orphan Process (+4 Apps Script `.gs` + `google_docs_sidebar` host; 1194 ids)**: process-tree prompt = flavour. Twist =
SPLIT carrier (marker without data + multi-line `[..].join("")` array). Carried solver left 55 ids planless -> ~30 rejected enum
probes; array-join patch -> CORRECT T+54 s; TT 11.7 s, Mastery 17.7 s first try.
**D19 Sharp Practice (base `managed-assembly-bridge`; +4 `.csx` + `host-aspx-inline-csharp-csharp-script.csx`; 1249 ids)**:
"where the bridge leads" = per-file `next-language`. Twist = NESTED escaped carrier (ASPX `EmbeddedCsx_<id>` C# string holding
the inner csx with `\n`/`\"`) -> 11 host ids planless; a guessed role/attack in a 46-id bulk POST sank the whole POST;
unescape-and-rescan patch -> CORRECT T+39 s (2 wrong probes). `lib.codec.v3_plan` already read it. TT 5.3 s, Mastery 12.2 s.
**D20 The Butler Did It (base `jenkins-pipeline-intrusion`; 1329 ids, 145 members)**: +4 `polyglot-groovy-*.groovy`,
`host-jenkins-pipeline-groovy.groovy` (profile `jenkins_pipeline`), **`host-classic-asp-vbscript.vbs`** (profile `classic_asp`,
`language=vbscript` -- first host file for a PRIOR language, and first day with TWO host files), + Bash `coprocess-block`
(feature `coprocess_block`, primitive `coproc_declaration`) and `mapfile-process` (`mapfile_process`,
`mapfile_process_substitution`). Artifact: all one-line v=3 carriers (`//` marker + `final String descriptor_<8hex>` in Groovy;
`'` marker inside `<% %>` + `Dim`/assign in ASP); tags HEX/B64/HB64/FRAG as usual; no twist. Prompt ("controller vs agent
semantics, trace the modeled build into its prior-language stages") = flavour; nothing asked beyond the per-file ids.
Plans: Groovy attack T1059 parent (not a sub-id), launcher steps `decode_embedded>write_file>dispatch_process`, staged_chain
`profile_host>decode_configuration>dispatch_language`; both hosts staged_chain/T1059/operation_graph. Carried solver (with the
D19 unescape patch + lib fallback) answered 1329/1329: race harness CORRECT **T+13 s, 0 wrong**; TT 717b8371 5.0 s (solve
0.95 s), Mastery 1478867c (6645 ids) 11.9 s, first try.

## GM answer conventions learned
- **Check `answer_format.kind` first.** `enum` lists values (scenario, role). `mitre_attack_id` takes `T####[.###]` or literal
  `none` (benign_utility). `integer`/`ordered_tokens` (d6+; steps joined with `>`). `exact_text` = plan value or synthetic label.
- **Plan-verbatim fields** (copy exactly): adapter (COM ProgIDs `MSXML2.ServerXMLHTTP.6.0`, LOLBins `CertReq.exe`/`curl.exe`/
  `cipher.exe`, batch `call`/`set`/`for`, Node `console_report`.., v=3 local_parser/runtime_loader/file_writer/http_client/
  process_builder/schedule_builder/operation_graph); indicators (campaign_id, host_id, url, file_path, upload_url, next_stage,
  extension, note_name, handoff_id, cron_path, schedule_path, service_name -- question reads "exact X indicator", X = plan key);
  batch `graph` (linear/single/diamond/fan_out/fallback_retry/cross_language/same_language); Python syntax/obfuscation/carrier/
  windows_chain; Bash feature/primitive (16 seen D7-D16); v=3 host_profile (standalone, wsf_jscript, wsf_mixed, hta_jscript,
  php_webshell, sct_scriptlet, lua_openresty, perl_cgi, ruby_rack, google_docs_sidebar (D18), aspx_inline_csharp (D19),
  jenkins_pipeline + classic_asp (D20)),
  obfuscation (base64/plain_hex/hex_base64/fragmented_hex), stage_profile (single_descriptor/two_stage_download_execute/three_stage_decode_write_launch/cross_language_handoff), next_language.
- **v=3 role and attack too.** GM accepted the plan's PARENT ids `T1059` (launcher, staged_chain, every host) and `T1053`
  (persistence_descriptor); AutoHotkey (D17) too, not `.010`; Apps Script (D18) too, not `.007`; C# script (D19); Groovy + classic ASP (D20). The attack
  question TEXT explains it: "the parent Command and Scripting Interpreter technique is also accepted when a language-specific
  sub-technique is canonical; for a staged chain or relay the earlier ingress-transfer technique is also accepted; none is
  also accepted for a relay" -- read the question's precedence text before probing ATT&CK. **v=3 role does NOT follow
  `steps`** (D14 MSBuild, D16 Ruby, D17 AHK benign_utility with `acquire_remote>dispatch_process`; D18 GAS benign_utility with
  `decode_embedded>write_file>dispatch_process`, launcher with `decode_configuration>return_configuration`; D19 ASPX host staged_chain with the same) -- copy role=,
  steps=, stage_profile= independently.
- **Role from `steps`** (v=1/v=2 only): decode_configuration,return_configuration = benign_utility; acquire_remote +
  dispatch_memory/pipe = stager; acquire_remote,write_file = downloader; decode_embedded,write_file = dropper; locate_local,
  dispatch_process = launcher; read_file/upload,transmit_remote = uploader; transform + recovery_note = impact;
  build_schedule,register_descriptor = persistence_descriptor; recognize_syntax,reconstruct_intent + `feature=` = advanced_syntax;
  ends in handoff_script or profile_host..dispatch_process = staged_chain; dispatch_next_stage (Python) = relay.
  cron_path/service_name on a staged_chain are indicators only, NOT persistence.
- **Role -> ATT&CK** (v=1/v=2; `lib.scripts.role_attack(role, lang)`): benign `none`; downloader/stager T1105; dropper T1140;
  uploader T1041; impact T1486; persistence_descriptor T1053.003; advanced_syntax T1059.004; launcher/staged_chain/relay = host
  language T1059.003 batch / .004 bash / .005 VBS / .006 python / .007 JScript and Node. PS scenarios: resource_hijacking T1496,
  synthetic_collection T1555.003, synthetic_impact T1486. REJECTED: T1218.010, T1620, T1027.009, T1005, T1560, T1119, T1074(.001);
  stager T1059.007; dropper T1105.
- **Batch expansion** (enum percent/delayed/call_double/for_indirect; question "Classify only the expansion form used by the
  descriptor reconstruction statement"): statement regime = Variant axes table (default from D16). Old regime (D3-D14 cases):
  h-pool + `call set` = call_double; `for .. do call set` over other pools = for_indirect; everything else delayed (incl.
  `!h0!!h1!`). Fragment JOINER pitfall: `set "item9=%item0%%item1%.."` is the JOIN, not fragment 9. REJECTED: percent_expansion,
  immediate, call-double, double_call.
- **Batch control**: direct, errorlevel_guard (`ver >nul` + `if errorlevel 1 exit /b 1`), goto_dispatch, call_subroutine,
  if_guard (`if defined X`); separators and `:HUNTRESS_UNUSED` dead labels are NOT control. ~45 synonyms rejected (D3).
- **VBS control**: direct, select_case, do_once, while_once, error_guard (`On Error Resume Next`..`Err.Raise`), for_once.
- **Codec labels**: representation/transform = the codec const's fields 1/2 VERBATIM (per-language spellings differ).
- **JScript styles**: function-style `function f(` declaration / `var f = function(` anonymous_expression / `var f = function
  f_body(` named_expression; invocation-style direct / call (`.call`, also via a local invoke helper) / apply; property-style
  dot / bracket_literal / mixed (triage's `shape:` line counts them).
- **NAMING LAWS** (proven on if_guard, error_guard, do_once, pe_cli): conditional/bail-out = `<keyword>_guard`; run-once loop =
  `<keyword>_once`; control transfer = `<keyword>_<action>`. Spelled-out statements (if_defined, on_error_resume, do_exit,
  while_wend) and descriptive synonyms (flag_guard, opaque_predicate) have ALWAYS been rejected.

## Pitfalls that cost time
- **Enum-walking when the plan did not decode** (D18 ~30 rejected probes; D19 2 probes + a poisoned bulk): a v=3 file that
  yields no plan is a CARRIER problem (D18 marker without data + array; D19 inner file inside an escaped string). Call
  `lib.codec.v3_plan` (D19: it already worked), else read the bytes around the marker and fix join/unescape/peel. Enum probes
  can never answer the exact_text majority, and a GUESSED value inside a bulk POST rejects the whole bulk (D19 46-id POST)
  (POSTs are all-or-nothing; `--from-solver` bisects) -- submit derived ids alone, probe guesses ONE per submit.
- **Regime keyed on the wrong contract field** (D16 single, 5 incorrect probes; D15 Mastery ~5 min diffing bytes): when a
  carried label table breaks on byte-identical constructs, the GM generator changed -- tabulate (construct, GM label) against
  EVERY contract key incl. `started_at` at once.
- **Probing synonyms instead of deriving.** D3 lost ~1.5 h; apply the naming laws first; `hctf labels` seeds candidates.
- **Generic ATT&CK guesses** (d1, d2): use the role->ATT&CK table; a v=3 `attack=` is authoritative even as a parent id; a
  prompt's ATT&CK hint (D14 T1127.001) is not.
- **Routing by file extension** (D8-D9 `.js` held HTA/WSF/SCT, `.vbs` a WSF job; D19 `.csx` an ASPX page; D20 `.vbs` a
  classic ASP page, `host-<profile>-<lang>` naming an OLD language): route by the plan marker first.
- **Answer-id field parsing** (D8, 6 ids): family names contain hyphens/underscores; resolve the field as the longest known
  `-<field>` suffix (`stage-count`/`stage-profile` before `stage`).
- **GM error body saved as the artifact** (D7 TT): check size + sha256 against the start response first; tiny `{"error":..}` =
  transport failure (re-download, exit non-zero), never a regression case.
- **Stale notes travel with copied solvers** (D8-D20 `solver/NOTES.md` is still the D7 copy; D15-D16 regime fixes live only in
  solve.py comments). Date every VARIANT AXIS line by day + attempt id; diagnose EVERY failed attempt.
- **Unknown codec rep name -> silent no-plan** (D7 TT, 15 ids): fall back to material-shape readings.
- **cmd parsing**: `%item0%` is a variable, not `%0`+`item`; CRLF/LF mixes and `SeT` casing occur. **Bash Codec key** comma
  lists (`lib.scripts.codec_key()`). **stage_count != len(steps)**: read the plan field.
- **Timed modes are a transport race** (D7 TT 13.5 s for 0.4 s of solving; D16 5-set Mastery hit the 60 s runner cap): fork
  per set, submit all sets in one call (chunks <= 500 answers / 512 KiB); pair same-named Mastery deliveries by sha256; index
  nested AES zips once, never decrypt script leaves to sniff for PK.
- **Reading the narrative prompt as the task** (D8, D15-D20): seven prompts promised comparison/reconciliation/tree questions
  that never came. Diff `answer_ids` first; spend time only on ids the carried solver cannot answer.
- **Never execute fixtures.** Decode from the Codec const / descriptor plus a restricted interpreter; accept a plan only if it
  parses as `k=v|..` with `steps` (or `feature`).
