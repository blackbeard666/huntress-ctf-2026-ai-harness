# script-analysis — technique log (days 1-7; updated after every day)

How this lane has looked so far (these are observations, not guarantees):
- There is one AES zip, `evidence.zip` (password `infected`), of inert "Huntress Script Triage" fixtures. **The contract is CUMULATIVE.** Each day keeps every earlier language's files and questions and adds ONE new host language. The bytes and values re-roll every day:
  PS (d1, 15 ids) -> +JScript (d2, 87) -> +Batch (d3, 159) -> +VBScript (d4, 231) -> +Python (d5, 357) -> +Bash (d6, 399)
  -> +Node.js `.mjs` and 2 Bash advanced-syntax fixtures (d7, 469). The title names the new language; the prompt names its NEW roles.
- From day 2 on, every fixture hides a **self-describing plan**: `v=N|steps=a,b|adapter=..|stage_count=..|campaign_id=..|<indicators>`. It sits behind a codec, usually named in a `Codec_<id>` / `CODEC_<id>` / `rem HUNTRESS-CODEC:` const of the form `rep|transform|key`. Most exact_text answers are plan values copied verbatim.
- The hard part is **naming CODE SHAPE**: control-flow, expansion, and function/invocation/property styles. These are GM synthetic labels that are not in the plan. Role and scenario are enums, so read `accepted_values`.
- Files are named by behaviour (host-context, memory-stage, embedded-write, remote-write, local-dispatch, staged-handoff/-chain, outbound-transfer, impact-plan, relay-handoff, schedule-descriptor). The answer-id is `<lang>-<role>-<field>`, and the artifact path picks the file. Don't trust the file name over the plan `steps`.
- Time Trial windows are about 5-13 s (30 s on d1). Mastery is 2 sets: `setN.` ids, and the artifact is `evidence-0N.zip` or (d6) `delivery N: evidence.zip`, or (d7) ONE download holding both `evidence-01.zip` + `evidence-02.zip`. Same-named deliveries: pair them by sha256.

## Variant axes (what differs between the single, Time Trial and Mastery variants of the SAME day -- parse every value listed)
Each miss below cost one failed timed attempt + a ~45-90 s generalize cycle (D6 replay: 4 cycles; D7: 1 cycle).
- **Codec per file** -- rep x transform x key re-rolls per variant; never bind a role to the sample's codec. **NEW rep
  NAMES appear only on variants** (D7 TT: `unicode_escapes` `\u00XX..`, `json_numbers` `[232,241,..]`,
  `reversed_base64`, Bash `xor_hex|cd`). Decode by the material's SHAPE (escapes / int array / hex / base64, each also
  reversed) x the named transform, and accept only output starting `v=`; the name only orders the tries.
- **Codec spec arity** -- 3 fields `rep|transform|key`, 2 fields `rep|` (empty transform = identity; D7 bash advanced
  fixtures), or the transform folded into the rep with the key second (`xor_hex|cd`). Split on `|`, never index blindly.
  lib.codec (`_spec`) now normalises both short forms and decodes every D7 rep (json_numbers, unicode_escapes,
  reversed_base64, xor_hex): 336/336 D7 codecs.
- **Numeric literal radix** -- the same array/constant may be decimal `23,7`, hex `0x17,0x07`, or a separator-joined
  string decoded with `parseInt(x, R)` / `int(x, R)`: READ THE RADIX FROM THE CODE, never guess it from the digits
  (D6: JScript material array hex on TT; decoder constants `^ 0x56`; Mastery dash-joined DECIMALS with
  `parseInt(..,10)`). Applies to keys too.
- **Base64 alphabet** -- standard and urlsafe (`-` `_`) both occur; strip/whitelist accordingly and pad (D6 Python TT).
- **Reversal level** -- `reversed_hex/_decimal/_integer_list` reverse the loaded LIST; `reversed_base64` reverses the
  TEXT before decoding (`==Adu..`). Try both orders.
- **Carrier of the same language** -- plain source vs a frozen executable (D6: Python plan inside a cx_Freeze build on
  a TT variant). Locate the material by its markers (`MATERIAL_`/`CODEC_`/`v=`), not by the file type of the sample.
- **Material layout** -- one literal, split chunks, `+=` concatenation, adjacent quoted strings; join before decoding.
- **Adapter values** re-roll within a role (Node stager http_then_module/https_then_vm/fetch_then_function; launcher
  execfile_node/fork_module/spawn_file; persistence systemd_descriptor/npm_lifecycle_descriptor) -- always plan-verbatim.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "method=AES Encrypted" | Already extracted by triage (`work/extracted/`, password `infected`) and every plan decoded in triage.md -- start from that, BUT diff the extracted member list against the contract's `artifact` names: triage silently skipped D7's new `.mjs` extension (no decode lines at all). In solve.py open members with `lib.common.read_member` (Python zipfile cannot read AES). Mastery may be a zip inside a zip; walk it once. |
| Prior-day languages in the contract | Cumulative: derive every family from TODAY's bytes with the shared codec method below (never copy/run an old solver). Spend thinking on the new language. |
| `.ps1` with `$encodedMaterial = [Convert]::FromBase64String('..')` + `$reconstruct` + `$nativeTypes` | `base64 -d` -> JSON descriptor (short keys a/b/c..): url/wallet/mutex/UA/file/ext/note. Match indicators by SHAPE, not key. `$nativeTypes` gives the scenario: Process/Registry+wallet=resource, ZipFile/HttpWebRequest=collection, Aes/DirectoryInfo=impact. |
| `.js` WSH, `decode_*`/`recover_*`/`inspect_*`, XOR key arrays, `"52:90:.."` strings | Run each file in an empty `node` `vm` context (no require/ActiveXObject), `eval` swapped for a capture. Call the top-level functions and keep the first object that has `steps`. Read the styles off the `inspect_*` body. |
| `.bat/.cmd` with `rem HUNTRESS-CODEC:` / `HUNTRESS-MATERIAL:`, `set "itemN=v=1|steps=..`, `:HUNTRESS_INSPECT` | Plan is in plain `set` fragments. Emulate cmd expansion in Python (`%v%`, `!v!`, `call set %%..%%`, `for %%G in (..)`). The MATERIAL line is a 2nd encoded copy to cross-check. Never run cmd. |
| `.vbs` with `Const Material_<id>`, `Const Codec_<id> = "rep|transform|key"`, `Load_/Decode_/Recover_<id>` | Decode in Python from the Codec const, cross-check against the Load/Decode code (no cscript). rep/transform answers = Codec fields 1/2 verbatim. Control = the construct wrapping the `Decode_` call inside `Recover_`. |
| `.py` `*-recovered.py` with `MATERIAL_<id>`, `CODEC_<id>`, `load_/decode_/surface_/plan_<id>` | Already-recovered source (no decompile on d5). Decode from CODEC or run `decode_(load_(MATERIAL))` under an AST whitelist. Plan v=2 carries syntax/obfuscation/carrier/windows_chain verbatim. |
| `.sh` `readonly Material_<id>='..'` + `readonly Codec_<id>='rep|transform|key'` | Decode from the Codec const (key hex; multi-byte key = COMMA list). Re-join split/`+=`/adjacent-quoted chunks. Never run bash. |
| `.sh` with `Feature_<id>()` (`${!pointer}`, `local -a parts=('cu' 'rl')`), plan `v=1|feature=..|primitive=..` | Role `advanced_syntax` (closed enum value). feature/primitive/campaign/stage_count/steps are plan-verbatim; attack = T1059.004. |
| `.mjs` ESM: `const Material_<id> = ".."; const Codec_<id> = "rep|transform|key"`, async `load_/decode_/recover_/inspect_/plan_<id>`, `process.env.HUNTRESS_INSPECT_ONLY` | Static decode with `lib.codec.find_codecs` + shape fallback (reps hex_buffer, hex_array, escaped_octets `\\xNN`, decimal_array, unicode_escapes, json_numbers). Don't run it (top-level await, Buffer/vm). Plan fields verbatim; role from `steps`. |
| Real `.pyc` / PyInstaller / pyarmor (not seen yet) | `lib.pyc.recover_python(path)` (pyinstxtractor-ng + decompyle3, `dis` fallback). See skills/script-analysis. |
| Any `Codec_` key like `ba` / `0a` | A hex byte, not text. Transforms are named for the ENCODE side: `subtract_modulo_256` decodes by ADDING, `add_modulo_256` by SUBTRACTING. `rolling_xor` = c ^ previous CIPHER byte, seeded with the key. |

## Codec table (`Codec_<id>='<rep>|<transform>|<key>'`, batch `rem HUNTRESS-CODEC:<rep>|<transform>`; seen D3-D7)
**Already done for you:** triage.md's "Decoded payloads" runs `lib.codec` on every declared codec (and a node vm
sandbox on JScript). In solve.py call `lib.codec.find_codecs(text)` / `lib.codec.decode(material, rep, transform, key)`
(pure Python, Homebase-safe, unknown names -> None). A line `NOT decoded by lib.codec` = new rep/transform/arity: decode
it by material shape yourself and list it under `## Proposed lib additions` in NOTES.md.
- Reps (how the bytes are WRITTEN): base64_literal/_chunks, urlsafe_base64, reversed_base64 (D7); hex_pairs/_compact/
  _colon/_dash/_escape (`\x`)/_literal (`0x`)/_buffer/_array (`["69","22"]`), percent_hex (`%xx`), escaped_octets
  (`\\xNN`), unicode_escapes (`\\u00NN`); decimal_bytes/_comma/_dash/_pipe/_dot/_colon/_space/_csv/_array, json_numbers,
  integer_list/_tuple, octal_space; reversed_text/_hex/_decimal/_integer_list; plain_fragments/split_fragments.
- Transforms (ENCODE-side names; key hex, multi-byte = COMMA list): identity (also EMPTY field), reverse/reverse_bytes,
  single_byte_xor, repeating_key_xor, reverse_then_xor, rolling_xor (2 flavours), add_modulo_256 (decode SUBTRACTS),
  subtract_modulo_256 (decode ADDS); batch carries the parameter in the name: xor_5a, add_7 (decimal), rotate_left
  (undo = rotate right), reverse_xor; bash D7 `xor_hex|cd` = hex then XOR key cd.
- Check: the decoded plaintext starts `v=` (or `{` JSON). If not, the codec reading is wrong.

## Day by day
**D1 Power Play (PS, 15 ids)**: 3 PS fixtures, base64 JSON descriptors. Collection ATT&CK cost 5 wrong (T1005, T1560,
T1119, T1074, T1074.001) before `T1555.003` -- tell was `Login Data`/`Cookies`. **Map the SPECIFIC artifact, not the
generic tactic.** ~15 min.

**D2 Host With the Most (+9 JScript, 87)**: plans behind base64/XOR arrays/reverse/byte-shift, eval'd by `inspect_*`;
node `vm` + eval capture. Handoff graph = `staged_chain` even with a .js next_stage (`relay` REJECTED). 7 wrong, all
ATT&CK guesses (see table). ~22 min.

**D3 Expansion Pack (+9 Batch, 159): the costly day, ~1 h 45 min, ~127 rejected probes.** expansion/control are GM
labels, not surface reading; `if defined X` burned ~40 synonyms before `if_guard`. -> NAMING LAWS. `%item0%` is a
variable, not `%0`.

**D4 Dim and Dimmer (+9 VBScript, 231)**: Codec const + small VBS-subset interpreter. Control probed one field at a
time (direct/select_case/do_once/while_once; TT added error_guard/for_once). 4 wrong, ~7 min.

**D5 Hatch Careful (+14 Python "carriers", 357)**: prompt promised pyc/PyInstaller/pyarmor but the zip held
`*-recovered.py` source; plan v=2 gave every label verbatim. 0 wrong, ~4 min. `dispatch_next_stage` = relay.

**D6 Shell We Begin (+6 Bash, 399)**: Material/Codec/Load/Decode/Recover with noise wrappers. New fields stage-count
(= plan stage_count, NOT len(steps)) and steps (`>`-joined). 399/399 first submit, ~4 min.

**D7 Node by Node (+8 Node.js `.mjs` + 2 Bash advanced-syntax, 469 ids)**: prompt "Eight Node.js operation graphs
that will never execute. Spot the indirect expansions and token fragmentation, then sort each graph into its role".
- Artifact: one AES `evidence.zip`, 61 members (D6 set + `node-*.mjs` + `indirect-expansion.sh`/`token-fragmentation.sh`).
- Node files = same Material_/Codec_ pattern as VBS/Bash, in ESM JS. Static decode via lib.codec + shape fallback;
  answers plan-verbatim. Fields: role, attack, adapter, campaign, <indicator>, stage-count, steps.
- New roles: `build_schedule>register_descriptor` = `persistence_descriptor` -> **T1053.003** (by ROLE: adapter was
  systemd_descriptor / npm_lifecycle_descriptor, schedule_path `/etc/cron.d/node-xxxxxx`). Bash fixtures with plan
  `feature=` (steps recognize_syntax>reconstruct_intent, stage_count 1) = `advanced_syntax` -> T1059.004; feature
  indirect_expansion|token_fragmentation, primitive parameter_indirection|array_token_construction.
- New indicator keys (plan-verbatim): schedule_path, service_name (`node-xxxxxx.service`, on staged_chain).
- 469/469 first submit, ~100 s (D6 solver copied + Node/advanced branch; triage had no `.mjs` decodes).
- TT (11 s window): attempt 5ab8013f missed 15 ids -- new reps unicode_escapes/json_numbers/`xor_hex|cd`; harvested
  variant 7d6f8d53 added `reversed_base64|`. Attempt 26b7da83 got a 24 B `{"error":"rate_limited"}` saved as
  evidence.zip. 3rd attempt 516aa6d1 CORRECT (9.5 s in-window: start 3.9 + download 3.1 + submit 6.0). Mastery
  2c52d50f (13 s) CORRECT first try, 3.9 s in-window; 938 ids, one bundle holding evidence-01.zip + evidence-02.zip.
- NOTES.md's "VARIANT AXIS: none" came from the 2nd generalize worker, which looked only at the rate-limited attempt.
  The real axis was the new reps found by the 1st worker. **Diagnose EVERY failed attempt, not only the latest.**

## GM answer conventions learned
- **Check `answer_format.kind` first.** `enum` gives the list (scenario, role). `mitre_attack_id` takes `T####[.###]` or literal `none` (benign_utility). `integer`/`ordered_tokens` (d6+). `exact_text` = plan value or synthetic label.
- **Plan-verbatim fields** (copy exactly): adapter (COM ProgIDs `MSXML2.ServerXMLHTTP.6.0`, LOLBins `CertReq.exe`, batch `call`/`set`/`for`, Node `console_report`/`typed_array_to_file`/`stream_pipeline`), campaign_id, host_id, url, file_path, upload_url, next_stage, extension, note_name, handoff_id, cron_path, schedule_path, service_name, batch `graph`, Python syntax/obfuscation/carrier/windows_chain, Bash feature/primitive. Indicator questions read "exact X indicator", where X is the plan key.
- **Role from `steps`**:

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
  | recognize_syntax,reconstruct_intent + plan `feature=` (Bash d7) | advanced_syntax |
  | ends in handoff_script (JS/Batch/VBS) or profile_host..dispatch_process | staged_chain |
  | dispatch_next_stage (Python) | relay |

  cron_path/service_name on a staged_chain are indicators only, NOT persistence.
- **Role -> ATT&CK** (GM-confirmed d2-d7; `lib.scripts.role_attack(role, lang)` has the table):
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
- **JScript styles** (closed sets in the question text; GM-confirmed D2-D7):
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
- **GM error body saved as the artifact** (D7 TT 26b7da83): `{"error":"rate_limited"}` (24 B) landed as `evidence.zip`,
  so every field came out None/default. Before solving/diagnosing, check artifact size + sha256 against the contract
  `sha256`; a tiny JSON `{"error":..}` = transport failure (retry), NOT a variant. Solvers should exit non-zero on it.
- **Unknown codec rep name -> silent no-plan** (D7 TT: 15 ids unanswered). Fall back to material-shape readings x the
  named transform; never let an unknown NAME stop the decode.
- **Batch expansion shortcuts** ("h-pool = call_double", "`%` join = percent") were wrong. Use the mined rule above.
- **cmd arg parsing**: `%item0%` is a variable, not `%0`+`item`. CRLF/LF mixes and `SeT` casing occur.
- **Bash Codec key**: comma-separated multi-byte keys parsed as contiguous hex silently give key [0]. Use `lib.scripts.codec_key()`.
- **stage_count != len(steps)** (d6). Read the plan field.
- **Timed modes are a transport race.** D2 Mastery expired (downloads ate 4-5 s of 6 s; sets submitted serially). D7 TT
  spent 13.5 s for 0.4 s of solving (start 3.9, download 3.1, submit 6.0). Solver ~0.2-1.5 s; submit all sets in one call.
- **Same-name deliveries.** Pair Mastery files by sha256; if delivery 2 is missing, leave set 2 unanswered rather than
  reuse set 1's members (confidently wrong 42-174 times in regression cases).
- **Re-walking nested AES zips per question** cost ~1.3 s (903 PBKDF2 runs). Index the tree once.
- **Never execute fixtures.** Every decode so far worked from the Codec const plus a restricted interpreter of the
  Load/Decode bodies. Cross-check two decoders; accept a plan only if it parses as `k=v|..` with `steps` (or `feature`).
