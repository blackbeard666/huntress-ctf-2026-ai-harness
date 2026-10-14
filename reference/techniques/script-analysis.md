# script-analysis — technique log (days 1-14; updated after every day)

How this lane has looked so far (these are observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- There is one AES zip, `evidence.zip` (password `infected`), of inert "Huntress Script Triage" fixtures. **The contract is CUMULATIVE.** Each day keeps every earlier language's files and questions and adds ONE new host language or host format. The bytes and values re-roll every day:
  PS (d1, 15 ids) -> +JScript (d2, 87) -> +Batch (d3, 159) -> +VBScript (d4, 231) -> +Python (d5, 357) -> +Bash (d6, 399)
  -> +Node.js `.mjs` and 2 Bash advanced-syntax fixtures (d7, 469) -> +8 PHP "polyglot" files, 4 WSF/HTA/PHP-webshell "host"
  files and 2 more Bash advanced fixtures (d8, 615) -> +4 Lua polyglot, 2 host files (SCT scriptlet, Lua OpenResty), 2 more
  Bash advanced (d9, 695) -> +4 WMI MOF polyglot + 2 Bash advanced (d10, 753) -> +4 TypeScript `.ts` polyglot + 2 Bash
  advanced (d11, 811) -> +4 AutoIt `.au3` polyglot (d12, 855; no new Bash fixture) -> +4 AppleScript `.applescript` polyglot + 2 Bash
  advanced (d13, 913; 105 members) -> +4 MSBuild `.proj` polyglot + 2 Bash advanced (d14, 971; 111 members). The title
  names the new language; the prompt names its NEW roles.
- From day 2 on, every fixture hides a **self-describing plan**: `v=N|steps=a,b|adapter=..|stage_count=..|campaign_id=..|<indicators>`. It sits behind a codec, usually named in a `Codec_<id>` / `CODEC_<id>` / `rem HUNTRESS-CODEC:` const of the form `rep|transform|key`. Most exact_text answers are plan values copied verbatim.
  From D8 there is also a **`v=3` plan**: it carries `role=` and `attack=` itself, and sits behind a `HUNTRESS_ANALYSIS_V1:<TAG>-` comment.
- The hard part is **naming CODE SHAPE**: control-flow, expansion, and function/invocation/property styles. These are GM synthetic labels that are not in the plan. Role and scenario are enums, so read `accepted_values`.
- Files are named by behaviour (host-context, memory-stage, embedded-write, remote-write, local-dispatch, staged-handoff/-chain, outbound-transfer, impact-plan, relay-handoff, schedule-descriptor). The answer-id is `<lang>-<role>-<field>`, and the artifact path picks the file. Don't trust the file name over the plan `steps`.
- The D8-D11 prompts are narrative ("find the one that doesn't match its siblings", "expose the stage whose claimed family
  tree is impossible", D10 "name the subscription that would really survive a reboot", D11 "flag the call whose claimed
  purpose the evidence doesn't support"). No question asked for that outlier/impossible stage. Answer the contract ids only.
- Time Trial windows are about 5-13 s (30 s on d1). Mastery has `setN.` ids: 2 sets on d2-d7, **5 sets on d8 (3075 ids, 22 s)
  and d9 (3475 ids, 30 s)**, 2 sets again on d10 (1506 ids, 32 s), d11 (1622 ids, 11 s), d12 (1710 ids, 30 s), d13 (1826 ids, 80 s) and d14 (1942 ids, 30 s). The artifact was `evidence-0N.zip`, or (d6) `delivery N: evidence.zip`, or (d7-d9) ONE download
  `evidence-01.zip` that holds every `evidence-0N.zip`. Same-named deliveries: pair them by sha256. Timed question texts
  carry `[assigned-artifact-sha256:<hex>]` per member -- usable to verify the bytes you got.

## Variant axes (what differs between the single, Time Trial and Mastery variants of the SAME day -- parse every value listed)
Each miss below cost one failed timed attempt + a ~45-90 s generalize cycle (D6 replay: 4 cycles; D7: 1 cycle; D8-D11: 0).
- **Codec per file** -- rep x transform x key re-rolls per variant; never bind a role to the sample's codec. **NEW rep
  NAMES appear only on variants** (D7 TT: `unicode_escapes` `\u00XX..`, `json_numbers` `[232,241,..]`,
  `reversed_base64`, Bash `xor_hex|cd`). Decode by the material's SHAPE (escapes / int array / hex / base64, each also
  reversed) x the named transform, and accept only output starting `v=`; the name only orders the tries.
  D9: the 7 deliveries (single + TT + 5 sets) used no rep/transform beyond lib.codec's D3-D8 vocabulary (0 decode failures).
- **Codec spec arity** -- 3 fields `rep|transform|key`, 2 fields `rep|` (empty transform = identity; D7-D9 bash advanced
  fixtures), or the transform folded into the rep with the key second (`xor_hex|cd`, D8 `xor_hex|11`, D9 `xor_hex|95/6f/c0`).
  Split on `|`, never index blindly. lib.codec (`_spec`) normalises both short forms.
- **Plan carrier tag (v=3, D8-D9)** -- `HUNTRESS_ANALYSIS_V1:<TAG>-<data>`, plus the same data in `descriptor_<id> = ".."`.
  Values: `B64` (base64), `HEX` (plain hex), `HB64` (hex of base64 text = 2 layers), `FRAG` (hex split by `.` every 24 chars).
  Across all 7 deliveries of D8 and of D9 the tag stayed fixed per file; only the values re-rolled. Parse rule: ignore the tag
  name. Peel by shape and recurse (max 3 layers): if the text is only hex digits plus `.:,-_ |\x%` separators, strip the
  separators and unhex; otherwise base64 (also reversed). Accept only a result starting `v=`. The tag = `obfuscation_profile`.
  `lib.codec.find_codecs(src)` returns the v=3 plan (tag -> rep: B64 base64_literal, HEX/FRAG hex_compact, HB64 hex_base64).
- **Plan carrier host syntax (v=3)** -- the marker sits in whatever comment the host uses: `//` (PHP, JS, HTA, WSF, SCT CDATA,
  MOF, TS), `--` (Lua D9, AppleScript D13), `;` (AutoIt, D12), `<!-- -->` (MSBuild XML, D14), and the descriptor as `$descriptor_<id>`, `var descriptor_<id>`, `local
  descriptor_<id>`, `Global Const $descriptor_<id> = ".."` (AutoIt), `property descriptor_<id> : ".."` (AppleScript), an XML property element `<PropertyGroup><HuntressDescriptor>..</HuntressDescriptor>`
  (MSBuild, D14 -- no `descriptor_` name at all). Parse rule: regex
  `HUNTRESS_ANALYSIS_V\d+\s*:\s*(\w*)-?\s*([^\s"'<>\]]+)` over the raw bytes, independent of comment syntax and extension.
- **Numeric literal radix** -- the same array/constant may be decimal `23,7`, hex `0x17,0x07`, or a separator-joined
  string decoded with `parseInt(x, R)` / `int(x, R)`: READ THE RADIX FROM THE CODE, never guess it from the digits
  (D6: JScript material array hex on TT; Mastery dash-joined DECIMALS with `parseInt(..,10)`). Applies to keys too.
- **Base64 alphabet** -- standard and urlsafe (`-` `_`) both occur; strip/whitelist accordingly and pad (D6 Python TT).
- **Reversal level** -- `reversed_hex/_decimal/_integer_list` reverse the loaded LIST; `reversed_base64` reverses the
  TEXT before decoding (`==Adu..`). Try both orders.
- **Carrier of the same language** -- plain source vs a frozen executable (D6: Python plan inside a cx_Freeze build on
  a TT variant). Locate the material by its markers (`MATERIAL_`/`CODEC_`/`v=`/`HUNTRESS_ANALYSIS_`), not by file type.
- **Material layout** -- one literal, split chunks, `+=` concatenation, adjacent quoted strings, `.`-separated FRAG
  fragments; join before decoding.
- **Adapter values** re-roll within a role (Node stager http_then_module/https_then_vm/fetch_then_function; launcher
  execfile_node/fork_module/spawn_file; persistence systemd_descriptor/npm_lifecycle_descriptor) -- always plan-verbatim.
- **No-new-axis days**: D8 (TT 129bf46a, Mastery 07d5051a), D9 (TT dfcfb51e, Mastery 1dfd4cf6), D10, D11 (TT f99ea9ec,
  Mastery 2d722b36; the 4 TS files kept FRAG/HEX/B64/HB64 + adapters + next_language in every delivery) and D12 (TT d629142e,
  Mastery 635241de; the 4 `.au3` files the same), D13 (TT c739141b, Mastery 78b00cf3; 4 `.applescript` + 2 Bash), D14 (TT
  b7cd2e36, Mastery 8a650537; 4 `.proj` kept HB64/FRAG/HEX/B64 + steps + next_language in all 4 deliveries): structure, tags,
  role/attack/steps/profiles identical to the single; only values re-rolled. All CORRECT first try.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "method=AES Encrypted" | Already extracted by triage (`work/extracted/`, password `infected`) and every plan decoded in triage.md -- start from that, BUT diff the extracted member list against the contract's `artifact` names. **Triage silently skips each day's new extension**: D7 `.mjs`, D8 `.php` (HB64 peeled 1 layer only), D9 `.lua` (5 files, no decode lines). In solve.py open members with `lib.common.read_member` (Python zipfile cannot read AES). Mastery may be a zip inside a zip; walk it once. |
| Prior-day languages in the contract | Cumulative: derive every family from TODAY's bytes with the shared codec method below. Spend thinking on the new language. If yesterday's solver routes by plan MARKER (not extension) it may already cover today (D9: unchanged D8 solver, 695/695). |
| `.ps1` with `$encodedMaterial = [Convert]::FromBase64String('..')` + `$reconstruct` + `$nativeTypes` | `base64 -d` -> JSON descriptor (short keys a/b/c..): url/wallet/mutex/UA/file/ext/note. Match indicators by SHAPE, not key. `$nativeTypes` gives the scenario: Process/Registry+wallet=resource, ZipFile/HttpWebRequest=collection, Aes/DirectoryInfo=impact. |
| `.js` WSH, `decode_*`/`recover_*`/`inspect_*`, XOR key arrays, `"52:90:.."` strings | Run each file in an empty `node` `vm` context (no require/ActiveXObject), `eval` swapped for a capture. Call the top-level functions and keep the first object that has `steps`. Read the styles off the `inspect_*` body. |
| `.bat/.cmd` with `rem HUNTRESS-CODEC:` / `HUNTRESS-MATERIAL:`, `set "itemN=v=1|steps=..`, `:HUNTRESS_INSPECT` | Plan is in plain `set` fragments. Emulate cmd expansion in Python (`%v%`, `!v!`, `call set %%..%%`, `for %%G in (..)`). The MATERIAL line is a 2nd encoded copy to cross-check. Never run cmd. |
| `.vbs` with `Const Material_<id>`, `Const Codec_<id> = "rep|transform|key"`, `Load_/Decode_/Recover_<id>` | Decode in Python from the Codec const, cross-check against the Load/Decode code (no cscript). rep/transform answers = Codec fields 1/2 verbatim. Control = the construct wrapping the `Decode_` call inside `Recover_`. |
| `.py` `*-recovered.py` with `MATERIAL_<id>`, `CODEC_<id>`, `load_/decode_/surface_/plan_<id>` | Already-recovered source (no decompile on d5). Decode from CODEC or run `decode_(load_(MATERIAL))` under an AST whitelist. Plan v=2 carries syntax/obfuscation/carrier/windows_chain verbatim. |
| `.sh` `readonly Material_<id>='..'` + `readonly Codec_<id>='rep|transform|key'` | Decode from the Codec const (key hex; multi-byte key = COMMA list). Re-join split/`+=`/adjacent-quoted chunks. Never run bash. |
| `.sh` with `Feature_<id>()` (`${!pointer}`, `local -a parts=('cu' 'rl')`, `local -A`, `${arr[@]:1:2}`, `trap 'return 0' RETURN`, a self-calling `walk_fixture`), plan `v=1|feature=..|primitive=..` | Role `advanced_syntax` (closed enum value). feature/primitive/campaign/stage_count/steps are plan-verbatim; attack = T1059.004. The `Feature_` body is the feature; never name it from the code, copy the plan. |
| `.mjs` ESM: `const Material_<id> = ".."; const Codec_<id> = "rep|transform|key"`, async `load_/decode_/recover_/inspect_/plan_<id>`, `process.env.HUNTRESS_INSPECT_ONLY` | Static decode with `lib.codec.find_codecs` + shape fallback (reps hex_buffer, hex_array, escaped_octets `\\xNN`, decimal_array, unicode_escapes, json_numbers). Don't run it (top-level await, Buffer/vm). Plan fields verbatim; role from `steps`. |
| `// HUNTRESS_ANALYSIS_V1:<B64|HEX|HB64|FRAG>-..` or `-- HUNTRESS_ANALYSIS_V1:..` + `descriptor_<id> = ".."` (`.php`; `.lua` `local descriptor_..` + `build_plan_<id>`, OpenResty `inert_handler_<id>` returning `{status=200,..}`; `.js` that is really HTA `<hta:application>`, WSF `<job><script language="JScript">` or SCT `<?xml?><scriptlet><registration progid=..>` CDATA; `.vbs` that is a WSF job; `.au3` AutoIt `; HUNTRESS_ANALYSIS_V1:` + `Global Const $descriptor_..`; `.proj` MSBuild `<!-- HUNTRESS_ANALYSIS_V1:..-->` + `<HuntressDescriptor>`) | **Route by the marker, before the extension** (the extension lies). Peel the descriptor by shape to `v=3|language=..|role=..|verdict=..|attack=..|adapter=..|host_profile=..|obfuscation_profile=..|stage_profile=..|next_language=..|stage_count=..|steps=..|campaign_id=..|url=..|file_path=..`. EVERY answer, including role and attack, is plan-verbatim. Python `-I` + base64/bytes.fromhex is enough. |
| Real `.pyc` / PyInstaller / pyarmor (not seen yet) | `lib.pyc.recover_python(path)` (pyinstxtractor-ng + decompyle3, `dis` fallback). See skills/script-analysis. |
| Any `Codec_` key like `ba` / `0a` | A hex byte, not text. Transforms are named for the ENCODE side: `subtract_modulo_256` decodes by ADDING, `add_modulo_256` by SUBTRACTING. `rolling_xor` = c ^ previous CIPHER byte, seeded with the key. |

## Codec table (`Codec_<id>='<rep>|<transform>|<key>'`, batch `rem HUNTRESS-CODEC:<rep>|<transform>`; seen D3-D9)
**Already done for you:** triage.md's "Decoded payloads" runs `lib.codec` on every declared codec (and a node vm
sandbox on JScript). In solve.py call `lib.codec.find_codecs(text)` / `lib.codec.decode(material, rep, transform, key)`
(pure Python, Homebase-safe, unknown names -> None). A line `NOT decoded by lib.codec` = new rep/transform/arity: decode
it by material shape yourself and list it under `## Proposed lib additions` in NOTES.md. D9 added nothing new.
- Reps (how the bytes are WRITTEN): base64_literal/_chunks, urlsafe_base64, reversed_base64 (D7); hex_pairs/_compact/
  _colon/_dash/_escape (`\x`)/_literal (`0x`)/_buffer/_array (`["69","22"]`), percent_hex (`%xx`), escaped_octets
  (`\\xNN`), unicode_escapes (`\\u00NN`); decimal_bytes/_comma/_dash/_pipe/_dot/_colon/_space/_csv/_array, json_numbers,
  integer_list/_tuple, octal_space; reversed_text/_hex/_decimal/_integer_list; plain_fragments/split_fragments;
  v=3 hex_base64 (D8).
- Transforms (ENCODE-side names; key hex, multi-byte = COMMA list): identity (also EMPTY field), reverse/reverse_bytes,
  single_byte_xor, repeating_key_xor, reverse_then_xor, rolling_xor (2 flavours), add_modulo_256 (decode SUBTRACTS),
  subtract_modulo_256 (decode ADDS); batch carries the parameter in the name: xor_5a, add_7 (decimal), rotate_left
  (undo = rotate right), reverse_xor; bash `xor_hex|<key>` = hex then XOR key (D7-D9).
- Check: the decoded plaintext starts `v=` (or `{` JSON). If not, the codec reading is wrong.

## Day by day
**D1 Power Play (PS, 15)**: base64 JSON descriptors. Collection ATT&CK cost 5 wrong before `T1555.003` (tell: `Login
Data`/`Cookies`). **Map the SPECIFIC artifact, not the generic tactic.** ~15 min.
**D2 Host With the Most (+JScript, 87)**: plans behind base64/XOR/reverse/byte-shift, eval'd by `inspect_*`; node `vm` +
eval capture. Handoff = `staged_chain` (`relay` REJECTED). 7 wrong, all ATT&CK guesses. ~22 min.
**D3 Expansion Pack (+Batch, 159): the costly day, ~1 h 45 min, ~127 rejected probes.** expansion/control are GM labels,
not surface reading; `if defined X` burned ~40 synonyms before `if_guard` -> NAMING LAWS.
**D4 Dim and Dimmer (+VBScript, 231)**: Codec const + small VBS interpreter; control probed one field at a time. 4 wrong, ~7 min.
**D5 Hatch Careful (+Python, 357)**: `*-recovered.py` source, plan v=2 gave every label. 0 wrong, ~4 min.
**D6 Shell We Begin (+Bash, 399)**: stage-count = plan stage_count (NOT len(steps)); steps `>`-joined. 0 wrong, ~4 min.
**D7 Node by Node (+Node `.mjs` + 2 Bash advanced, 469)**: same Material_/Codec_ pattern in ESM; new roles
persistence_descriptor (T1053.003) and advanced_syntax (T1059.004). 469/469 first submit, ~100 s. TT: attempt 5ab8013f
missed 15 ids (new reps unicode_escapes/json_numbers/`xor_hex|cd`); 26b7da83 saved `{"error":"rate_limited"}` as the zip;
3rd CORRECT. Mastery CORRECT first try. Lesson: **diagnose EVERY failed attempt, not only the latest.**
**D8 Lost in Translation (+8 PHP polyglot, +4 host formats, +2 Bash advanced; 615)**: new files carry the v=3 plan
(`HUNTRESS_ANALYSIS_V1:<TAG>-` + `descriptor_<id>`, byte-identical); role/attack/adapter/profiles stated, **copy, don't
derive**. New fields host-profile, obfuscation, stage-profile, next-language. ~2 min 10 s, 2 submits, 0 wrong (6 ids lost
to hyphenated family names -> longest-known-suffix field parse). TT 2.1 s / Mastery 5.6 s in-window, both 1st try.

**D9-D13 (+Lua/SCT/OpenResty, +WMI MOF, +TypeScript, +AutoIt, +AppleScript polyglots; +2 Bash advanced most days; 695 ->
913 ids)**: every new file is an ordinary v=3 fixture (`HUNTRESS_ANALYSIS_V1:<TAG>-` in `--`/`//`/`;` comments + `descriptor_<id>`);
the narrative prompts ("impossible family tree", "subscription that survives a reboot", D13 "archive delivery chain") were
never asked. Polyglot set per language: role benign_utility/downloader/launcher/staged_chain, attack none/T1105/T1059/T1059,
adapter local_parser/http_client/process_builder/operation_graph, obfuscation plain_hex/base64/hex_base64/fragmented_hex,
next_language powershell/jscript/batch/vbscript, campaign `<LANG>-<8hex>`, url `https://<lang>-<10hex>.example.invalid/stage`,
file_path `/tmp/huntress-<lang>/.<16hex>.stage`. Bash advanced campaign `BASHX-<8HEX>`, codec `hex_compact|` / `decimal_csv|`.
The marker-routed carried-over solver answered every day unchanged, 0 wrong, all modes first try (TT 4-7 s elapsed, most of it
GM start/submit latency on ~900 ids).
**D14 Trust the Process (+4 MSBuild `.proj` polyglot, +2 Bash advanced; 971 ids, 111 members)**: prompt "follow the MSBuild
properties into its targets ... where a trusted toolchain does untrusted work" -- flavour only; nothing asked about Targets/Tasks
or MSBuild ATT&CK (T1127.001 was NOT the answer; the plan said `attack=T1059`).
- New: `polyglot-msbuild_xml-{benign-utility,downloader,launcher,staged-chain}.proj` = `<?xml?>` + `<!-- HUNTRESS_ANALYSIS_V1:<TAG>-.. -->`
  + `<Project xmlns=".../msbuild/2003"><PropertyGroup><HuntressDescriptor>` holding the same data. Family name has an UNDERSCORE
  (`polyglot-msbuild_xml-...`), campaign `MSBUILD_XML-<8hex>`, host `msbuild_xml-<10hex>.example.invalid`.
- New Bash advanced: `getopts-state.sh` (getopts_state|option_parser_state), `brace-expansion.sh` (brace_expansion|
  cartesian_brace_expansion).
- Method: carried-over solver, no code change; harness probe 971/971 CORRECT at T+11 s (single submit). TT 30 s window, 3.09 s
  elapsed (solve 1.0 s); Mastery 2 sets / 1942 ids, 4.17 s. 0 wrong in every mode.

## GM answer conventions learned
- **Check `answer_format.kind` first.** `enum` gives the list (scenario, role). `mitre_attack_id` takes `T####[.###]` or literal `none` (benign_utility). `integer`/`ordered_tokens` (d6+). `exact_text` = plan value or synthetic label.
- **Plan-verbatim fields** (copy exactly):
  - adapter: COM ProgIDs `MSXML2.ServerXMLHTTP.6.0`, LOLBins `CertReq.exe`, batch `call`/`set`/`for`, Node
    `console_report`/`typed_array_to_file`/`stream_pipeline`, v=3 local_parser/runtime_loader/file_writer/http_client/
    process_builder/schedule_builder/operation_graph.
  - indicators: campaign_id, host_id, url, file_path, upload_url, next_stage, extension, note_name, handoff_id, cron_path,
    schedule_path, service_name. Indicator questions read "exact X indicator", where X is the plan key.
  - per-language labels: batch `graph` (D9 confirmed linear/single/diamond/fan_out/fallback_retry/cross_language/
    same_language), Python syntax/obfuscation/carrier/windows_chain, Bash feature/primitive, v=3 host_profile/
    obfuscation_profile/stage_profile/next_language.
  - v=3 host_profile seen: standalone, wsf_jscript, wsf_mixed, hta_jscript, php_webshell (D8), sct_scriptlet, lua_openresty
    (D9). obfuscation: base64/plain_hex/hex_base64/fragmented_hex. stage_profile: single_descriptor/
    two_stage_download_execute/three_stage_decode_write_launch/cross_language_handoff.
  - Bash advanced feature|primitive (always plan-verbatim; 14 seen D7-D14), e.g. indirect_expansion|parameter_indirection,
    associative_arrays|declare_associative, heredoc_reconstruction|quoted_heredoc, getopts_state|option_parser_state (D14),
    brace_expansion|cartesian_brace_expansion (D14). Family = `bash-advanced-<file-stem>` (D7 short forms: `indirect`, `tokens`).
  - **v=3 role and attack too.** GM accepted the plan's PARENT technique ids: `T1059` (launcher, staged_chain -- PHP, WSF,
    HTA, SCT, Lua alike) and `T1053` (persistence_descriptor), NOT the host-language sub-technique. The role->ATT&CK table
    below is for v=1/v=2 plans only. **v=3 role does NOT follow `steps`** (D14 MSBuild: benign_utility had steps
    `decode_embedded>write_file>dispatch_process`, launcher `decode_configuration>return_configuration`) -- copy role= and steps=
    independently; never "fix" one from the other.
- **Role from `steps`** (v=1/v=2 plans; v=3 states `role=`):

  | steps | role |
  |---|---|
  | decode_configuration,return_configuration | benign_utility |
  | acquire_remote + dispatch_memory/dispatch_pipe | stager |
  | acquire_remote,write_file | downloader |
  | decode_embedded,write_file | dropper |
  | locate_local,dispatch_process | launcher |
  | read_file/upload,transmit_remote | uploader |
  | transform + recovery_note | impact |
  | build_schedule,register_descriptor (Node d7) | persistence_descriptor |
  | recognize_syntax,reconstruct_intent + plan `feature=` (Bash d7-d9) | advanced_syntax |
  | ends in handoff_script (JS/Batch/VBS) or profile_host..dispatch_process | staged_chain |
  | dispatch_next_stage (Python) | relay |

  cron_path/service_name on a staged_chain are indicators only, NOT persistence.
- **Role -> ATT&CK** (GM-confirmed d2-d9; `lib.scripts.role_attack(role, lang)` has the table):
  - benign `none`; downloader and stager T1105; dropper T1140; uploader T1041; impact T1486; persistence_descriptor
    T1053.003 (by role, whatever the adapter); advanced_syntax T1059.004.
  - launcher/staged_chain/relay follow the HOST LANGUAGE: T1059.003 batch, .004 bash, .005 VBS, .006 python, .007
    JScript AND Node.js (.001 PS predicted, never asked).
  - PS scenarios: resource_hijacking T1496, synthetic_collection T1555.003, synthetic_impact T1486.
  - REJECTED: T1218.010, T1620, T1027.009, T1005, T1560, T1119, T1074(.001); stager T1059.007; dropper T1105.
- **Batch expansion** (closed set; mined from EVERY GM-verified D3-D6 case, 0 conflicts in 545):
  - fragments named `h<N>` AND joined with `call set` (bare, or `for %%G in (..) do call set`) = `call_double`
  - `for %%G in (..) do call set "cfg=%%cfg%%%%<pool>%%G%%"` over any OTHER pool (v_a/item/fragment/FrAg) = `for_indirect`
  - everything else = `delayed`, INCLUDING h-pools joined with `!h0!!h1!..` (the "h-pool = call_double" shortcut failed).
  - Fragment JOINER pitfall: `set "item9=%item0%%item1%..."` is the JOIN, not fragment 9 -- skip `set` lines whose
    value references the other fragments (a wrong Mastery answer on D6).
  - REJECTED: percent_expansion, immediate, call-double, double_call.
- **Batch control**: direct (separator lines and `:HUNTRESS_UNUSED` dead labels are NOT control), errorlevel_guard
  (`ver >nul` + `if errorlevel 1 exit /b 1`), goto_dispatch, call_subroutine, if_guard (`if defined X`). REJECTED:
  linear, straight_line, sequential, goto, goto_label, double_pipe, pipe, ampersand, call_label, dead_label, errorlevel,
  opaque_branch, + ~40 "if defined" synonyms.
- **VBS control**: direct, select_case, do_once, while_once, error_guard (`On Error Resume Next`..`Err.Raise`),
  for_once. REJECTED: do_loop, do_exit, while_wend, while_loop, on_error_resume.
- **Codec labels**: representation/transform = the codec const's fields 1/2 copied VERBATIM; spellings differ per
  language (Python `decimal_csv`, batch `decimal_bytes|reverse_xor`): read the const, never translate.
- **JScript styles** (closed sets in the question text; GM-confirmed D2-D9):
  - function-style: `function f(` = declaration; `var f = function(` = anonymous_expression; `var f = function f_body(` = named_expression.
  - invocation-style: how recover/inspect invokes the next top-level function: `f(x)` = direct, `f.call(..)` (also via
    a local `invoke` helper doing `block.call`) = call, `f.apply(..)` = apply.
  - property-style: only `o.k` = dot, only `o["k"]` = bracket_literal, both = mixed. triage's `shape:` line counts them.
- **NAMING LAWS** (proven on if_guard, error_guard, do_once, pe_cli). Compose unknown labels from the SHORT language keyword:
  - conditional/bail-out = `<keyword>_guard`; run-once loop = `<keyword>_once`; control transfer = `<keyword>_<action>`.
  - The spelled-out statement (if_defined, on_error_resume, do_exit, while_wend) and descriptive synonyms (flag_guard, defined_guard, opaque_predicate) have ALWAYS been rejected.

## Pitfalls that cost time
- **Probing synonyms instead of deriving.** D3 lost ~1.5 h and two fields hit the 6-wrong cap on `if defined`. Apply the naming laws first; `hctf labels` seeds candidates from lib/playbook.py.
- **Per-set POST is all-or-nothing.** One wrong field fails the whole batch; `--from-solver` bisects and prints the rejected id(s). Probe uncertain label fields ONE per submit; the wrong cap is per field.
- **Generic ATT&CK guesses** (d1 collection, d2 launcher/stager/dropper): use the role->ATT&CK table. Adapter names (regsvr32, systemd_descriptor) do NOT change the technique.
  Exception: a plan that states `attack=` (v=3) is authoritative even when it is a parent id (T1059, T1053).
- **Routing by file extension** (D8-D9): `.js` held HTA/WSF/SCT-scriptlet markup and `.vbs` held a WSF job with
  VBScript+JScript. Check for the plan marker first; use the extension only as a fallback. Marker-first routing is why
  the D8 solver needed no change on D9.
- **Answer-id field parsing** (D8, 6 ids lost on the 1st submit): new family names contain hyphens
  (`bash-advanced-associative-arrays-feature`, `polyglot-php-persistence-descriptor-stage-profile`). Resolve the field
  as the longest known `-<field>` suffix (`stage-count`/`stage-profile` before `stage`), not by a prefix-strip regex.
- **GM error body saved as the artifact** (D7 TT 26b7da83, one timed attempt lost): `{"error":"rate_limited"}` (24 B)
  landed as `evidence.zip`, so every field came out None/default and the submit failed. Before solving or diagnosing,
  check artifact size + sha256 against the start response (`artifacts[].sha256`, or the `[assigned-artifact-sha256:..]`
  tag in timed question texts). A tiny JSON `{"error":..}` = transport failure (retry the download), NOT a variant.
  Solvers should exit non-zero on it (the D7-D9 solver does). Don't harvest it as a regression case.
- **Stale notes travel with copied solvers** (D8-D14 `solver/NOTES.md` is still the D7 copy). Date every VARIANT AXIS line
  by day + attempt id, and diagnose EVERY failed attempt (D7's "none" looked only at the rate-limited one).
- **Unknown codec rep name -> silent no-plan** (D7 TT: 15 ids unanswered). Fall back to material-shape readings x the
  named transform; never let an unknown NAME stop the decode.
- **cmd arg parsing**: `%item0%` is a variable, not `%0`+`item`. CRLF/LF mixes and `SeT` casing occur.
- **Bash Codec key**: comma-separated multi-byte keys parsed as contiguous hex give key [0] (`lib.scripts.codec_key()`).
  **stage_count != len(steps)** (d6): read the plan field.
- **Timed modes are a transport race.** D2 Mastery expired (downloads ate 4-5 s of 6 s; sets submitted serially). D7 TT
  spent 13.5 s for 0.4 s of solving (start 3.9, download 3.1, submit 6.0); D8-D9 transport was fast (start 0.6-1.5 s,
  download 0.3-1.3 s). Solver ~0.2-4 s (D9 Mastery: 5 sets in 1.8 s, forked per set); submit all sets in one call.
- **Same-name deliveries.** Pair Mastery files by sha256; if delivery 2 is missing, leave set 2 unanswered rather than
  reuse set 1's members (confidently wrong 42-174 times in regression cases).
- **Re-walking nested AES zips per question** cost ~1.3 s (903 PBKDF2 runs). Index the tree once, and don't decrypt
  script leaves to sniff for a nested zip (keep the leaf-extension list current: `.lua` missing D9; still missing on D14:
  `.lua .mof .ts .au3 .applescript .proj` -- speed only, solve stayed ~1 s).
- **Never execute fixtures.** Every decode so far worked from the Codec const plus a restricted interpreter of the
  Load/Decode bodies. Cross-check two decoders; accept a plan only if it parses as `k=v|..` with `steps` (or `feature`).
