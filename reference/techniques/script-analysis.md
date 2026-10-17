# script-analysis — technique log (days 1-16; updated after every day)

How this lane has looked so far (these are observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- One AES zip `evidence.zip` (password `infected`) of inert "Huntress Script Triage" fixtures. **The contract is CUMULATIVE**:
  each day keeps every earlier file/question and adds one language; bytes and values re-roll daily. PS (d1, 15 ids) ->
  +JScript (d2, 87) -> +Batch (d3, 159) -> +VBScript (d4, 231) -> +Python (d5, 357) -> +Bash (d6, 399) -> +Node `.mjs` + Bash
  advanced (d7, 469) -> +PHP polyglot + WSF/HTA/PHP-webshell hosts (d8, 615) -> +Lua + SCT/OpenResty hosts (d9, 695) -> +WMI MOF
  (d10, 753) -> +TypeScript (d11, 811) -> +AutoIt (d12, 855) -> +AppleScript (d13, 913) -> +MSBuild `.proj` (d14, 971) -> +Perl
  + perl_cgi host (d15, 1026) -> +Ruby `.rb` + ruby_rack host (d16, 1095; 123 members). Most days also add 2 Bash advanced
  fixtures (not d12, d15). Since D8 the TITLE/PROMPT is a pun or narrative; the new language shows up only in the member list
  (D16 "Same Same, But Different" = "obfuscation equivalence", and the new files were Ruby). Diff the contract ids against yesterday's.
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
  equivalent, expose the variant that quietly changed the plot") have NEVER been asked as a question. Answer the contract ids only.
- Time Trial windows ~5-17 s. Mastery has `setN.` ids: 2 sets d2-d7 and d10-d14, **5 sets d8, d9, d15 (5130 ids) and d16 (5475
  ids)**. The artifact was `evidence-0N.zip`, `delivery N: evidence.zip` (d6), or one `evidence-01.zip` holding every
  `evidence-0N.zip` (d7-d9). Same-named deliveries: pair by sha256. Timed questions carry `[assigned-artifact-sha256:<hex>]`.
  From D15 the timed contracts are the untimed regular pool (`run_for_time:false`, `variant_fresh:true`, no deadline).

## Variant axes (what differs between the single, Time Trial and Mastery variants of the SAME day -- parse every value listed)
Each miss cost one failed timed attempt + a ~45-90 s generalize cycle (D6: 4 cycles; D7: 1; D8-D14: 0; D15: TT localize + 1
Mastery cycle; D16: 0 answer misses -- the Mastery failures were runner timeouts, no bytes reached a verdict).
- **GM label regime (batch `expansion`; D15 pool-keyed, D16 DATE-keyed)** -- SAME bytes, SAME question text, DIFFERENT label.
  Old regime (every D3-D14 case + the D15 single): the whole handoff is labelled, `echo(!var!)` => `delayed` unless a FOR/h-pool
  rule fires. Statement regime (D15 TT/Mastery `run_for_time:false`; **D16 single with NO run_for_time key**; D16 TT a719c002):
  label the JOIN STATEMENT alone -- `!a!!b!` join = delayed; `for %%G in (..) do call set` = for_indirect for ANY pool (incl. an h
  pool); bare `call set "x=%%h0%%.."` (h pool) = call_double; bare `call set` over item/v_a/FrAg pools = percent; plain
  `set "x=%a%%b%"` = percent. D16 single GM labels: benign for_indirect, stager/dropper delayed, downloader call_double,
  uploader/launcher/impact/chain/relay percent. The D15 rule "branch on run_for_time" was keyed on the wrong thing and cost 5
  rejected probes on the D16 single. Parse rule: **statement regime is the default** (`run_for_time is False` OR
  `started_at >= 2026-10-16`); the old regime only for older replayed cases. When byte-identical constructs get different GM
  labels across cases, tabulate (construct, label) against EVERY contract key (started_at, run_for_time, variant_fresh,
  hall_of_fame_eligible) at once instead of diffing bytes. Expect other synthetic labels (control/style) to flip the same way.
- **Codec per file** -- rep x transform x key re-rolls per variant; never bind a role to the sample's codec. **NEW rep NAMES
  appear only on variants** (D7 TT: `unicode_escapes`, `json_numbers`, `reversed_base64`, Bash `xor_hex|cd`). Decode by the
  material's SHAPE (escapes / int array / hex / base64, each also reversed) x the named transform; accept only output starting
  `v=`; the name only orders the tries. D9-D16: nothing beyond lib.codec's vocabulary (0 decode failures).
- **Codec spec arity** -- `rep|transform|key`, `rep|` (empty transform = identity; Bash advanced D7-D16), or transform folded
  into the rep with the key second (`xor_hex|cd`, D16 `xor_hex|ec`). Split on `|`, never index blindly (lib.codec `_spec`).
- **Plan carrier tag (v=3, D8-D16)** -- `HUNTRESS_ANALYSIS_V1:<TAG>-<data>` + the same data in a descriptor literal. Tags `B64`,
  `HEX`, `HB64` (hex of base64), `FRAG` (hex split by `.` every 24 chars); stayed fixed per file in every delivery D8-D16, only
  values re-rolled. Parse rule: ignore the tag name; peel by shape, recurse (max 3-4 layers); accept only `v=`. Tag =
  `obfuscation_profile` (B64 base64, HEX plain_hex, HB64 hex_base64, FRAG fragmented_hex). `lib.codec.find_codecs(src)` returns it.
- **Plan carrier host syntax (v=3)** -- marker in whatever comment the host uses: `//` (PHP, JS, HTA, WSF, SCT, MOF, TS), `--`
  (Lua, AppleScript), `;` (AutoIt), `<!-- -->` (MSBuild), `#` (Perl D15, Ruby D16). Descriptor forms: `$descriptor_<id>`,
  `var/local descriptor_<id>`, `Global Const $descriptor_<id>`, `property descriptor_<id> :`, `<HuntressDescriptor>` element
  (MSBuild, no name), `my $descriptor_<id> = "..";` (Perl), **`DESCRIPTOR_<8HEX> = ".."` uppercase Ruby constant (D16)**. Parse rule:
  regex `HUNTRESS_ANALYSIS_V\d+\s*:\s*(\w*)-?\s*([^\s"'<>\]]+)` over raw bytes, independent of comment syntax, case and extension.
- **Numeric literal radix** -- decimal `23,7`, hex `0x17`, or a joined string read with `parseInt(x, R)` / `int(x, R)`: READ THE
  RADIX FROM THE CODE (D6 JScript TT hex; Mastery dash-joined DECIMALS). Applies to keys too.
- **Base64 alphabet** -- standard and urlsafe (`-` `_`) both occur; whitelist and pad (D6 Python TT).
- **Reversal level** -- `reversed_hex/_decimal/_integer_list` reverse the LIST; `reversed_base64` reverses the TEXT. Try both.
- **Carrier of the same language** -- plain source vs a frozen executable (D6 TT: Python plan in a cx_Freeze build). Locate
  material by markers (`MATERIAL_`/`CODEC_`/`v=`/`HUNTRESS_ANALYSIS_`), not by file type.
- **Material layout** -- one literal, split chunks, `+=`, adjacent quoted strings, `.`-separated FRAG; join before decoding.
- **Adapter values** re-roll within a role (Node stager http_then_module/https_then_vm/fetch_then_function; launcher
  execfile_node/fork_module/spawn_file; persistence systemd_descriptor/npm_lifecycle_descriptor) -- always plan-verbatim.
- **Transport/runner, not variant** -- D7 TT saved `{"error":"rate_limited"}` as the zip; D8 TT start 503
  `training_rotation_invalid`; D16 Mastery (5 sets, 5475 ids, 3.2-3.7 MB status bodies at 5-8 s each) hit the 60 s local
  `hb_timed` cap on all 5 attempts (`exec_error`, nothing submitted). None of these is a solver change; never harvest them as cases.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "method=AES Encrypted" | Triage already extracted it (`work/extracted/`) and decoded every plan. Diff the member list / contract ids against yesterday's to find the new language (D16: 4 `polyglot-ruby-*.rb` + `host-ruby-rack-ruby.rb` + 2 `.sh`). Triage used to skip new extensions (D7 `.mjs`, D8 `.php`, D9 `.lua`); D15-D16 it decoded them. Open members with `lib.common.read_member` (zipfile can't read AES). |
| Prior-day languages in the contract | Cumulative: rerun the carried marker-routed solver FIRST (D9-D16: it covered each new v=3 language unchanged). Spend thinking on the new language and on synthetic-label regimes. |
| `.ps1` `$encodedMaterial = [Convert]::FromBase64String('..')` + `$nativeTypes` | `base64 -d` -> JSON descriptor: url/wallet/mutex/UA/file/ext/note by SHAPE. `$nativeTypes` gives the scenario: Process/Registry+wallet=resource, ZipFile/HttpWebRequest=collection, Aes/DirectoryInfo=impact. |
| `.js` WSH, `decode_*`/`recover_*`/`inspect_*`, XOR key arrays, `"52:90:.."` | Run each file in an empty `node` `vm` (no require/ActiveXObject, `eval` -> capture); keep the first object with `steps`. Styles come off the `inspect_*` body. |
| `.bat/.cmd` `rem HUNTRESS-CODEC:` / `HUNTRESS-MATERIAL:`, `set "itemN=..`, `:HUNTRESS_INSPECT` | Plan is in `set` fragments. Emulate cmd expansion in Python. MATERIAL = second encoded copy to cross-check. Expansion label: statement regime by default (Variant axes). Never run cmd. |
| `.vbs` `Const Material_<id>`, `Const Codec_<id> = "rep|transform|key"` | Decode from the Codec const; rep/transform answers = Codec fields 1/2 verbatim. Control = construct wrapping `Decode_` inside `Recover_`. |
| `.py` `*-recovered.py` with `MATERIAL_<id>`, `CODEC_<id>` | Decode from CODEC (or AST-whitelisted `decode_(load_(..))`). Plan v=2 carries syntax/obfuscation/carrier/windows_chain verbatim. |
| `.sh` `readonly Material_<id>` + `readonly Codec_<id>` (+ `Feature_<id>()`) | Decode from the Codec const (multi-byte key = COMMA list). `Feature_` fixtures: role `advanced_syntax`, feature/primitive/campaign/stage_count/steps plan-verbatim, attack T1059.004. Never run bash. |
| `.mjs` ESM `const Material_<id>`, async `load_/decode_/recover_/inspect_/plan_<id>` | Static decode (`lib.codec.find_codecs` + shape fallback). Don't run it. Plan fields verbatim; role from `steps`. |
| `HUNTRESS_ANALYSIS_V1:<B64|HEX|HB64|FRAG>-..` in any comment + a descriptor literal (`.php .lua .js(HTA/WSF/SCT) .vbs(WSF) .mof .ts .au3 .applescript .proj .pl .rb`) | **Route by the marker before the extension.** Peel to `v=3|language=..|role=..|attack=..|adapter=..|host_profile=..|obfuscation_profile=..|stage_profile=..|next_language=..|stage_count=..|steps=..|campaign_id=..|url=..|file_path=..`. EVERY answer incl. role/attack is plan-verbatim. |
| Timed contract `run_for_time:false`, or any contract started on/after 2026-10-16 | Batch `expansion` = statement-only table. Check the contract keys before trusting labels harvested from older cases. |
| Real `.pyc` / PyInstaller / pyarmor (not seen yet) | `lib.pyc.recover_python(path)` (pyinstxtractor-ng + decompyle3, `dis` fallback). |
| `Codec_` key like `ba` / `0a` / `ec` | A hex byte. Transforms are ENCODE-side names: `subtract_modulo_256` decodes by ADDING; `rolling_xor` = c ^ previous CIPHER byte, seeded with the key. |

## Codec table (`Codec_<id>='<rep>|<transform>|<key>'`, batch `rem HUNTRESS-CODEC:<rep>|<transform>`; seen D3-D16)
**Already done for you:** triage.md's "Decoded payloads" runs `lib.codec` on every declared codec (and a node vm sandbox on
JScript). In solve.py: `lib.codec.find_codecs(text)` / `lib.codec.decode(material, rep, transform, key)` (pure Python,
unknown names -> None). `NOT decoded by lib.codec` = new rep/transform/arity: decode by shape, note it under `## Proposed lib additions`.
- Reps: base64_literal/_chunks, urlsafe_base64, reversed_base64; hex_pairs/_compact/_colon/_dash/_escape (`\x`)/_literal (`0x`)/
  _buffer/_array, percent_hex, escaped_octets, unicode_escapes; decimal_bytes/_comma/_dash/_pipe/_dot/_colon/_space/_csv/_array,
  json_numbers, integer_list/_tuple, octal_space; reversed_text/_hex/_decimal/_integer_list; plain/split_fragments; v=3 hex_base64.
- Transforms (key hex, multi-byte = COMMA list): identity (also EMPTY), reverse/reverse_bytes, single_byte_xor, repeating_key_xor,
  reverse_then_xor, rolling_xor (2 flavours), add_modulo_256 (decode SUBTRACTS), subtract_modulo_256 (decode ADDS); batch names
  carry the parameter: xor_5a, add_7 (decimal), rotate_left, reverse_xor; bash `xor_hex|<key>` = unhex then XOR.
- Check: plaintext starts `v=` (or `{` JSON). If not, the codec reading is wrong.

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
**D16 Same Same, But Different (`obfuscation-equivalence`; +4 Ruby `.rb` polyglot + `host-ruby-rack-ruby.rb` + Bash advanced
`ansi-c-quoting.sh`, `regex-conditional.sh`; 1095 ids, 123 members)**:
- Prompt: "several obfuscation families scrambled the same logic ... prove which are truly equivalent, expose the variant that
  quietly changed the plot". Flavour only: no equivalence/outlier question; every id was the usual per-file family.
- Ruby fixture: `# HUNTRESS_ANALYSIS_V1:<TAG>-..` + `DESCRIPTOR_<8HEX> = ".."` (uppercase constant). Plan v=3 `language=ruby`;
  host_profile `standalone` / `ruby_rack` (host = staged_chain/T1059/operation_graph). `steps` answers are `>`-joined
  (ordered_tokens), e.g. `profile_host>decode_configuration>dispatch_language`; stage_count is the plan field (benign = 2).
  next_language values seen: powershell, jscript, batch, vbscript. All plan-verbatim; the carried solver decoded them unchanged.
- Bash advanced (plan-verbatim): `ansi_c_quoting|ansi_c_escape_string` (`$'node\nbash\tfixture'`), `regex_conditional|
  bash_regex_match` (`[[ $v =~ ^node-[0-9]+$ ]]`); codecs `hex_compact|` and `xor_hex|ec`.
- Single: worker decided "carried solver covers Ruby" at T+33 s; the bisecting submit then hit 5 `incorrect` probes on
  batch-{uploader,launcher,impact,chain,relay}-expansion (`delayed` -> GM `percent`): the single has NO run_for_time key yet used
  the statement regime. Duel worker switched the regime on `started_at >= 2026-10-16`; CORRECT at T+4 min 23 s.
- TT a719c002 (`run_for_time:false`): CORRECT first try, 16.7 s (start 6.3, download 2.1, solve 1.4, submit 6.9).
- Mastery (5 sets, 5475 ids): 5/5 attempts `exec_error` "local hb_timed timed out" (60 s runner cap) -- the start/download/
  submit of a 5475-id bundle does not fit the cap; no answers reached the GM, so no variant axis could be observed.

## GM answer conventions learned
- **Check `answer_format.kind` first.** `enum` lists values (scenario, role). `mitre_attack_id` takes `T####[.###]` or literal
  `none` (benign_utility). `integer`/`ordered_tokens` (d6+; steps joined with `>`). `exact_text` = plan value or synthetic label.
- **Plan-verbatim fields** (copy exactly): adapter (COM ProgIDs `MSXML2.ServerXMLHTTP.6.0`, LOLBins `CertReq.exe`/`curl.exe`/
  `cipher.exe`, batch `call`/`set`/`for`, Node `console_report`.., v=3 local_parser/runtime_loader/file_writer/http_client/
  process_builder/schedule_builder/operation_graph); indicators (campaign_id, host_id, url, file_path, upload_url, next_stage,
  extension, note_name, handoff_id, cron_path, schedule_path, service_name -- question reads "exact X indicator", X = plan key);
  batch `graph` (linear/single/diamond/fan_out/fallback_retry/cross_language/same_language); Python syntax/obfuscation/carrier/
  windows_chain; Bash feature/primitive (16 seen D7-D16); v=3 host_profile (standalone, wsf_jscript, wsf_mixed, hta_jscript,
  php_webshell, sct_scriptlet, lua_openresty, perl_cgi, ruby_rack), obfuscation (base64/plain_hex/hex_base64/fragmented_hex),
  stage_profile (single_descriptor/two_stage_download_execute/three_stage_decode_write_launch/cross_language_handoff), next_language.
- **v=3 role and attack too.** GM accepted the plan's PARENT ids `T1059` (launcher, staged_chain, every host) and `T1053`
  (persistence_descriptor). **v=3 role does NOT follow `steps`** (D14 MSBuild, D16 Ruby downloader steps
  `acquire_remote>dispatch_process`) -- copy role= and steps= independently.
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
- **Regime keyed on the wrong contract field** (D16 single, 5 incorrect probes, ~1.5 min): yesterday's fix branched on
  `run_for_time is False`; the GM moved the single solve to the statement regime too. When a carried label table breaks on
  byte-identical constructs, assume the GM generator changed and re-check against EVERY contract key incl. `started_at`.
- **Diffing bytes when the regime changed** (D15 Mastery, ~5 min): tabulate (construct, GM label) per contract key at once.
- **Big Mastery bundles vs the local runner cap** (D16: 5475 ids, 5 x exec_error at 60 s). Status/contract bodies are 3-4 MB and
  take 5-8 s each; a 5-set bundle needs start + download + solve + chunked submit (each <= 500 answers / 512 KiB). Report it to the
  orchestrator as a budget problem; it is not a solver bug.
- **Probing synonyms instead of deriving.** D3 lost ~1.5 h; apply the naming laws first; `hctf labels` seeds candidates.
- **Per-set POST is all-or-nothing.** `--from-solver` bisects and prints the rejected id(s); probe uncertain label fields ONE
  per submit (wrong cap is per field).
- **Generic ATT&CK guesses** (d1, d2): use the role->ATT&CK table; a v=3 `attack=` is authoritative even as a parent id; a
  prompt's ATT&CK hint (D14 T1127.001) is not.
- **Routing by file extension** (D8-D9 `.js` held HTA/WSF/SCT, `.vbs` a WSF job): route by the plan marker first.
- **Answer-id field parsing** (D8, 6 ids): family names contain hyphens/underscores; resolve the field as the longest known
  `-<field>` suffix (`stage-count`/`stage-profile` before `stage`).
- **GM error body saved as the artifact** (D7 TT): check size + sha256 against the start response first; tiny `{"error":..}` =
  transport failure (re-download, exit non-zero), never a regression case.
- **Stale notes travel with copied solvers** (D8-D16 `solver/NOTES.md` is still the D7 copy; D15-D16 regime fixes live only in
  solve.py comments). Date every VARIANT AXIS line by day + attempt id; diagnose EVERY failed attempt.
- **Unknown codec rep name -> silent no-plan** (D7 TT, 15 ids): fall back to material-shape readings.
- **cmd parsing**: `%item0%` is a variable, not `%0`+`item`; CRLF/LF mixes and `SeT` casing occur. **Bash Codec key** comma
  lists (`lib.scripts.codec_key()`). **stage_count != len(steps)**: read the plan field.
- **Timed modes are a transport race** (D2 Mastery expired on downloads; D7 TT 13.5 s for 0.4 s of solving; D16 TT 16.7 s for
  1.4 s). Fork per set and submit all sets in one call.
- **Same-name deliveries**: pair Mastery files by sha256; if delivery 2 is missing, leave set 2 unanswered.
- **Nested AES zips**: index the tree once; don't decrypt script leaves to sniff for PK (leaf-ext list still lacks `.lua .mof
  .ts .au3 .applescript .proj .pl .rb` -- speed only).
- **Never execute fixtures.** Decode from the Codec const / descriptor plus a restricted interpreter; accept a plan only if it
  parses as `k=v|..` with `steps` (or `feature`).
