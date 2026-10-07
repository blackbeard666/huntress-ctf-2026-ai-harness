# script-analysis — technique log (days 1-6; updated after every day)

How this lane has looked so far (these are observations, not guarantees):
- There is one AES zip, `evidence.zip` (password `infected`), of inert "Huntress Script Triage" fixtures. **The contract is CUMULATIVE.** Each day keeps every earlier language's files and questions and adds ONE new host language. The bytes and values re-roll every day:
  PS (d1, 15 ids) -> +JScript (d2, 87) -> +Batch (d3, 159) -> +VBScript (d4, 231) -> +Python (d5, 357) -> +Bash (d6, 399).
- From day 2 on, every fixture hides a **self-describing plan**: `v=N|steps=a,b|adapter=..|stage_count=..|campaign_id=..|<indicators>`. It sits behind a codec, usually named in a `Codec_<id>` / `CODEC_<id>` / `rem HUNTRESS-CODEC:` const of the form `rep|transform|key`. Most exact_text answers are plan values copied verbatim.
- The hard part is **naming CODE SHAPE**: control-flow, expansion, and function/invocation/property styles. These are GM synthetic labels that are not in the plan. Role and scenario are enums, so read `accepted_values`.
- Files are named by behaviour (host-context, memory-stage, embedded-write, remote-write, local-dispatch, staged-handoff/-chain, outbound-transfer, impact-plan, relay-handoff). The answer-id is `<lang>-<role>-<field>`, and the artifact path picks the file. Don't trust the file name over the plan `steps`.
- Time Trial windows are about 5-7 s (30 s on d1). Mastery is 2 sets: `setN.` ids, and the artifact is `evidence-0N.zip` or (d6) `delivery N: evidence.zip`. Both deliveries can have the same filename, so pair them by sha256.

## Variant axes (what differs between the single, Time Trial and Mastery variants of the SAME day -- parse every value listed)
Each miss below cost one failed timed attempt + a ~45 s generalize cycle in the D6 from-scratch replay (4 cycles, ~3:20).
- **Numeric literal radix** -- the same array/constant may be decimal `23,7`, hex `0x17,0x07`, or a separator-joined
  string decoded with `parseInt(x, R)` / `int(x, R)`: READ THE RADIX FROM THE CODE, never guess it from the digits
  (D6: JScript material array in hex on a TT variant; JScript decoder constants `^ 0x56` hex on another; a Mastery set
  packed dash-separated DECIMALS with `parseInt(..,10)` that a hex-assuming parser misread). Applies to keys too.
- **Base64 alphabet** -- standard and urlsafe (`-` `_`) both occur; strip/whitelist accordingly and pad (D6 Python TT
  variant: urlsafe material, solver dropped `-`/`_`).
- **Carrier of the same language** -- plain source vs a frozen executable (D6: Python plan inside a cx_Freeze build on
  a TT variant). Locate the material by its markers (`MATERIAL_`/`CODEC_`/`v=`), not by the file type of the sample.
- **Codec per file** -- rep x transform x key re-rolls per variant (see the codec table); never bind a role to the
  sample's codec.
- **Material layout** -- one literal, split chunks, `+=` concatenation, adjacent quoted strings; join before decoding.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "method=AES Encrypted" | `7z x -pinfected -o<dir> evidence.zip` (Python zipfile cannot read AES). Mastery may be a zip inside a zip; walk it once. |
| Prior-day languages in the contract | The contract is cumulative, but derive every family from TODAY's bytes with the shared codec method below (never copy/run an old solver). The prior-day families are mechanical once the codec table is applied; spend thinking on the new language. |
| `.ps1` with `$encodedMaterial = [Convert]::FromBase64String('..')` + `$reconstruct` + `$nativeTypes` | Run `base64 -d` -> JSON descriptor (short keys a/b/c..), giving url/wallet/mutex/UA/file/ext/note. Match indicators by SHAPE, not key. `$nativeTypes` gives the scenario: Process/Registry+wallet=resource, ZipFile/HttpWebRequest=collection, Aes/DirectoryInfo=impact. `$reconstruct` was usually identity, sometimes reverse/XOR. |
| `.js` WSH, `decode_*`/`recover_*`/`inspect_*`, XOR key arrays, `"52:90:.."` strings | Run each file in an empty `node` `vm` context (no require/ActiveXObject), with `eval` swapped for a capture. Call the top-level functions and keep the first object that has `steps`. Read the styles off the `inspect_*` body. |
| `.bat/.cmd` with `rem HUNTRESS-CODEC:` / `HUNTRESS-MATERIAL:`, `set "itemN=v=1|steps=..`, `:HUNTRESS_INSPECT` | The plan is in plain `set` fragments. Emulate cmd expansion in Python (`%v%`, `!v!`, `call set %%..%%`, `for %%G in (..)`). The MATERIAL line is a 2nd encoded copy you can cross-check. Never run cmd. |
| `.vbs` with `Const Material_<id>`, `Const Codec_<id> = "rep|transform|key"`, `Load_/Decode_/Recover_<id>` | Decode in Python from the Codec const, and cross-check against the Load/Decode code (there's no cscript). rep/transform answers = Codec fields 1/2 verbatim. Control = the construct that wraps the `Decode_` call inside `Recover_`. |
| `.py` `*-recovered.py` with `MATERIAL_<id>`, `CODEC_<id>`, `load_/decode_/surface_/plan_<id>` | This is source the generator already "recovered", so no decompile was needed on d5. Run `decode_(load_(MATERIAL))` under an AST whitelist (no imports or dunders), or decode from CODEC. Plan v=2 carries syntax/obfuscation/carrier/windows_chain verbatim. |
| `.sh` `readonly Material_<id>='..'` + `readonly Codec_<id>='rep|transform|key'` | Decode from the Codec const (key is hex; a multi-byte key is a COMMA list `55,51,..`). Re-join split/`+=`/adjacent-quoted Material chunks. Never run bash. |
| Real `.pyc` / PyInstaller / pyarmor (not seen yet) | `lib.pyc.recover_python(path)` (pyinstxtractor-ng + decompyle3, `dis` fallback). See skills/script-analysis. |
| Any `Codec_` key like `ba` / `0a` | This is a hex byte, not text. Transforms are named for the ENCODE side: `subtract_modulo_256` decodes by ADDING, `add_modulo_256` by SUBTRACTING. `rolling_xor` = c ^ previous CIPHER byte, seeded with the key. |

## Codec table (`Codec_<id>='<rep>|<transform>|<key>'`; reps and transforms combine freely; seen D2-D6)
Rep = how the Material is written -> decode it to bytes first:
- `base64_literal` / `base64_chunks` (join chunks in order) -> `base64 -d`
- `hex` / `hex_colon` / `hex_dash` -> strip separators, `xxd -r -p`
- `integer_tuple` (decimal list) -> bytes of the integers
- `plain_fragments` (batch `set fragN=`) -> join in index order, SKIP the join line (see pitfall below)
Transform = then undo it, key is hex:
- `identity` -> nothing; `reverse` -> reverse the bytes; `reverse_then_xor` -> reverse, then xor
- `single_byte_xor` -> xor every byte with the key
- `repeating_key_xor` -> cycle the key; a multi-byte key may be written as a COMMA list `55,51,74` (D6 bash)
- `add_modulo_256` -> SUBTRACT the key mod 256
- `rolling_xor` -> key changes per byte (try both variants; the right one makes the plaintext start `v=`)
Check: the decoded plaintext starts `v=` (or `{` JSON). If not, the codec reading is wrong.

## Day by day
**D1 Power Play (PowerShell, 15 ids)**: 3 PS fixtures (resource/collection/impact), each with a base64 JSON descriptor.
- Indicators were plain after one `base64 -d`. Scenario is an enum; the GM gives the closed list.
- ATT&CK: resource T1496 and impact T1486 were accepted at once. **Collection cost 5 wrong answers** (T1005, T1560, T1119, T1074, T1074.001) before `T1555.003` (Credentials from Web Browsers). The tell was `Login Data` / `Cookies` in the descriptor's file list. **Lesson: map the SPECIFIC artifact names, not the generic tactic.**
- About 15 min to CORRECT (worker sessions of 288 s + 163 s).

**D2 Host With the Most (+9 JScript, 87 ids)**: plans behind custom base64 / XOR arrays / reverse / byte-shift layers, eval'd by `inspect_*`.
- Fix: node `vm` + eval capture (`solver/jsdecode.js`; it takes N files in one node process).
- Role comes from the `steps` graph. A handoff graph is `staged_chain` even when next_stage is .js (`relay` was REJECTED for the JS relay file).
- Styles (closed sets, given in the question text):
  - function-style: `function f(` = declaration; `x = function(` = anonymous_expression; `x = function name(` = named_expression. `var x = function x_body(` is named_expression.
  - invocation-style: the first call to another top-level function: direct / call / apply.
  - property-style: descriptor access by `d.k` only = dot, `d["k"]` only = bracket_literal, both = mixed.
- 7 wrong, all ATT&CK guesses: launcher T1218.010 (even with adapter regsvr32.exe), stager T1059.007/T1620, dropper T1105/T1027.009. The accepted map is below. About 22 min.

**D3 Expansion Pack (+9 Batch, 159 ids): the costly day, ~1 h 45 min and ~127 rejected probes.**
- PS+JS reused; the batch plan fragments were readable. 150/159 were accepted fast.
- `graph` = plan `graph=` value verbatim (single/linear/diamond/fan_out/fallback_retry/same_language/cross_language).
- **expansion** is NOT the surface join. Per-file GM truth contradicted the naive reading: `%` joins and CALL joins were `delayed`. The rule was reverse-engineered after a subagent study (see GM conventions).
- **control**: direct / errorlevel_guard / goto_dispatch / call_subroutine came from probing one field per submit.
- The `set "HUNTRESS_READY=1"` + `if defined HUNTRESS_READY <stmt>` construct burned **~40 rejected spellings** across two fields (if_defined, defined_guard, flag_guard, environment_guard, ready_guard, opaque_predicate, conditional_*, defined_*...). It hit the per-field wrong cap and needed an operator. The answer was **`if_guard`**, named after the cmd `if` keyword.
- **Lesson → NAMING LAWS below: derive from the language keyword; never brainstorm descriptive synonyms.**
- Pitfall: `%item0%` is a VARIABLE. Only `%N`, `%~modsN`, `%*` are batch args (a TT variant broke the parser).

**D4 Dim and Dimmer (+9 VBScript, 231 ids)**: decode via the Codec const plus a small VBS-subset interpreter of Load/Decode (they agreed on all 9).
- 222 non-control ids accepted in one submit.
- Control, probed one field at a time:
  - `direct`. Single-line `If (2 > 1) Then .. Else ..` junk is noise.
  - `select_case` (Select Case 1). An outer `If True Then` wrapper is noise.
  - Do..Exit Do..Loop = `do_once` (do_loop and do_exit REJECTED).
  - While p<1..Wend = `while_once` (while_wend and while_loop REJECTED).
- Later TT variants added more forms:
  - `On Error Resume Next`..Decode..`On Error GoTo 0`..`If e<>0 Then Err.Raise` = **`error_guard`** (direct and on_error_resume REJECTED).
  - `For p = 0 To 0` = `for_once` (GM-confirmed by d6).
  - New reps base64_literal/base64_chunks/hex_dash; new transforms reverse_then_xor/identity.
- 4 wrong; about 7 min to CORRECT (673 s worker total including solver work).

**D5 Hatch Careful (+14 Python "carriers", 357 ids)**: prompt says pyc/wheel/zipapp/PyInstaller/py2exe/cx_Freeze/pyarmor. The zip actually held `*-recovered.py` source plus `invoke-python-stage.ps1`, which has no questions (its HandoffId = the pyarmor-pyinstaller plan's handoff_id).
- Plan v=2 gives syntax/obfuscation/carrier/windows_chain/adapter verbatim, so there was nothing to name by hand.
- Submit order: 231 old ids -> 98 plan-verbatim ids -> roles/attack separately. **0 wrong**, about 4 min to CORRECT.
- New role facts: a `dispatch_next_stage` graph = `relay` (unlike JS/Batch/VBS relay files). 5-step profile_host..dispatch_process = staged_chain. Python execution = T1059.006.

**D6 Shell We Begin (+6 Bash, 399 ids)**: same Material/Codec/Load/Decode/Recover pattern. Recover wraps Decode in noise (`if ! ..; then return`, `case 1 in 1)`, `for p in 1`, indirect `"$decode_target"`).
- New fields:
  - `stage-count` (integer) = plan `stage_count`, NOT len(steps). A 2-step file had stage_count 1.
  - `steps` (ordered_tokens) = plan steps joined with `>`.
- Roles: acquire_remote>dispatch_pipe (`wget -qO- | bash -s`) = stager. cron_path is just an indicator, NOT a persistence role. Bash execution = T1059.004.
- **399/399 on the FIRST submit**, about 4 min. The worker checked that the old-language bytes differed from day 5 (values re-rolled) and grepped solver.log for decode errors before submitting.

## GM answer conventions learned
- **Check `answer_format.kind` first.** `enum` gives the list (scenario, role). `mitre_attack_id` takes `T####[.###]` or literal `none` (benign_utility). `integer`/`ordered_tokens` (d6). `exact_text` = plan value or synthetic label.
- **Plan-verbatim fields** (copy exactly, no normalization): adapter (COM ProgIDs like `MSXML2.ServerXMLHTTP.6.0`, LOLBins like `CertReq.exe`, odd tokens like `call`/`set`/`for` in batch), campaign_id, host_id, url, file_path, upload_url, next_stage, extension, note_name, handoff_id, cron_path, batch `graph`, Python syntax/obfuscation/carrier/windows_chain. Indicator questions read "exact X indicator", where X is the plan key.
- **Role from `steps`**:

  | steps | role |
  |---|---|
  | decode_configuration,return_configuration | benign_utility |
  | acquire_remote + memory/dispatch_pipe | stager |
  | acquire_remote,write_file | downloader |
  | decode_embedded,write_file | dropper |
  | locate_local,dispatch_process | launcher |
  | upload/transmit_remote | uploader |
  | transform + recovery_note | impact |
  | ends in handoff_script (JS/Batch/VBS) or profile_host..dispatch_process | staged_chain |
  | dispatch_next_stage (Python) | relay |

  `persistence_descriptor` and `advanced_syntax` are in the enum but have never been seen.
- **Role -> ATT&CK** (GM-confirmed d2-d6):
  - benign `none`; downloader and stager T1105; dropper T1140; uploader T1041; impact T1486.
  - launcher/staged_chain/relay follow the HOST LANGUAGE: T1059.003 batch, .004 bash, .005 VBS, .006 python, .007 JScript (.001 PS predicted, never asked).
  - PS scenarios: resource_hijacking T1496, synthetic_collection T1555.003, synthetic_impact T1486.
  - REJECTED: T1218.010, T1620, T1027.009, T1005, T1560, T1119, T1074(.001); stager T1059.007; dropper T1105.
- **Batch expansion** (closed set: percent/delayed/call_double/for_indirect; the GM chooses by generator template):
  - GM-confirmed counts: D3-D5 had exactly ONE `call_double` per day (the `h`-fragment pool fixture), D6 had NONE --
    its h-pool fixtures were `delayed`. So "h-pool = call_double" is NOT reliable. Seen consistently: a FOR loop over a
    fragment pool = for_indirect; plain `%` joins = delayed. Treat expansion as an uncertain label: submit it alone.
  - Fragment JOINER pitfall (D6): a line like `set "item9=%item0%%item1%..."` is the JOIN of the fragments, not
    fragment 9 -- skip `set` lines whose value references the other fragments, or the decoded value gets the
    `%item0%...` tail glued on (a wrong Mastery answer on D6).
  - REJECTED: percent_expansion, immediate, call-double, double_call.
- **Batch control**:
  - direct (no construct on the executed path; separator lines and `:HUNTRESS_UNUSED` dead labels are NOT control)
  - errorlevel_guard (`ver >nul` + `if errorlevel 1 exit /b 1`)
  - goto_dispatch; call_subroutine; if_guard (`if defined X`)
  - REJECTED: linear, straight_line, sequential, goto, goto_label, double_pipe, pipe, ampersand, call_label, dead_label, errorlevel, opaque_branch, + ~40 "if defined" synonyms.
- **VBS control**: direct, select_case, do_once, while_once, error_guard, for_once. REJECTED: do_loop, do_exit, while_wend, while_loop, on_error_resume.
- **Codec labels**: representation/transform = Codec const fields 1/2 verbatim. Accepted so far:
  - representation: decimal_pipe/_dash/_comma, hex_compact/_colon/_dash, reversed_decimal/_hex, base64_chunks
  - transform: subtract_modulo_256, repeating_key_xor, rolling_xor, single_byte_xor, reverse_bytes, reverse_then_xor, identity
  - Spellings differ per language (Python showed `decimal_csv`, batch `decimal_bytes|reverse_xor`), so read the const, don't translate.
- **NAMING LAWS** (proven on if_guard, error_guard, do_once, pe_cli). When an exact_text label is unknown, compose it from the SHORT language keyword:
  - conditional/bail-out = `<keyword>_guard` (errorlevel_guard, if_guard, error_guard)
  - run-once loop = `<keyword>_once` (do_once, while_once, for_once)
  - control transfer = `<keyword>_<action>` (goto_dispatch, call_subroutine)
  - The spelled-out statement (if_defined, on_error_resume, do_exit, while_wend) and descriptive synonyms (flag_guard, defined_guard, opaque_predicate) have ALWAYS been rejected.

## Pitfalls that cost time
- **Probing synonyms instead of deriving.** D3 lost ~1.5 h and two fields hit the 6-wrong cap on `if defined`. Apply the naming laws first; `hctf labels` seeds candidates from lib/playbook.py.
- **Per-set POST is all-or-nothing.** One wrong field makes every value in that submit look rejected locally (d2: a multi-80 batch failed, so retry singly with `--force`). Bulk-submit the confident fields, then probe uncertain label fields ONE per submit. The wrong cap is per field, so spread probes across files of the same construct.
- **Generic ATT&CK guesses** (d1 collection, d2 launcher/stager/dropper): use the role->ATT&CK table. LOLBin adapter names (regsvr32) do NOT change the technique.
- **Naive surface reading of batch expansion** gave wrong answers. Trust the GM-measured template rule above.
- **cmd arg parsing**: `%item0%` is a variable, not `%0`+`item`. CRLF/LF mixes and `SeT` casing occur.
- **Bash Codec key**: comma-separated multi-byte keys parsed as contiguous hex silently give key [0] and garbage. Use `lib.scripts.codec_key()`.
- **stage_count != len(steps)** (d6). Read the plan field.
- **Timed modes are a transport race, not an analysis problem.** D2 Mastery attempts expired because downloads ate 4-5 s of a 6 s window, and sets were submitted serially (set1 accepted, set2 expired). Solver runtime is about 0.2 s, so submit all sets in one call.
- **Same-name deliveries.** Mastery sends two files both named `evidence.zip` while the questions say `evidence-0N.zip` / `delivery N:`. Pair them by sha256 in contract `artifacts[]`. If delivery 2 is missing, leave set 2 unanswered rather than reuse set 1's same-named members (that was confidently wrong 42-174 times in regression cases).
- **Re-walking nested AES zips per question** cost about 1.3 s (903 PBKDF2 runs). Index the tree once.
- **Never execute fixtures.** Every decode so far worked from the Codec const plus a restricted interpreter of the Load/Decode bodies. Cross-check two decoders and accept a plan only if it parses as `k=v|..` with `steps`.
