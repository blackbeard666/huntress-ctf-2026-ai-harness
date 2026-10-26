# script-analysis — technique log (days 1-26; updated after every day)

How this lane has looked so far (these are observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field. **D23 proved it hard: the timed
  contract had a DIFFERENT SHAPE from the single** (hashed member names, per-file ids, composite fields, `LYR-` carrier tags;
  see Variant axes) -- the carried solver answered only 593/1495 TT ids.
- One AES zip `evidence.zip` (password `infected`) of inert "Huntress Script Triage" fixtures. **The single contract is
  CUMULATIVE**: each day keeps every earlier file/question and adds one language; bytes and values re-roll daily. PS (d1, 15
  ids) -> +JScript (d2, 87) -> +Batch (d3) -> +VBScript (d4) -> +Python (d5, 357) -> +Bash (d6) -> +Node `.mjs` + Bash advanced
  (d7, 469) -> +PHP + WSF/HTA/webshell hosts (d8, 615) -> +Lua/SCT/OpenResty (d9) -> MOF (d10) -> TypeScript (d11) -> AutoIt
  (d12) -> AppleScript (d13) -> MSBuild `.proj` (d14, 971) -> Perl + perl_cgi (d15) -> Ruby + ruby_rack (d16, 1095) ->
  AutoHotkey (d17) -> Apps Script + google_docs_sidebar (d18) -> C# `.csx` + ASPX (d19, 1249) -> Groovy + jenkins_pipeline +
  classic_asp + 2 Bash (d20, 1329) -> GitHub Actions `.yml` (d21, 1373) -> NSIS `.nsi` (d22, 1417) -> GDScript `.gd` (d23,
  1461 = +44, no host) -> JSP `.jsp` (d24, 1516 = +55, 4 polyglots + `host-jsp-webshell-jsp`) -> Elixir `.exs` (d25, 1571 =
  +55, + `host-elixir-phoenix-elixir`) -> **Erlang `.escript` (d26, 1615 = +44, 171 members, 4 polyglots, NO host)**. Bash
  advanced +2 most days (not d12, d15, d17-d19, d21-d23, d26). Since D8 the TITLE is a pun and the base id names the theme
  (D20 "The Butler Did It" -> Jenkins; D22 "Next, Next, Finish" -> NSIS; D23 "Press Start to Decode" -> GDScript; D24 "Web of
  Lies" -> JSP; D25 "Ashes to Assets"/`phoenix-stage-chain` -> Elixir; D26 "Mixed Signals"/`beam-message-flow` -> Erlang);
  **D25-D26 prompts NAMED the language**. Diff contract ids against yesterday's.
- **Forecast cue (3/3 hits, D24-D26)**: the timed plans' `next_language` pool holds only never-shipped languages; each day's
  new language leaves it (jsp -> D24, elixir -> D25, erlang -> D26; each pool lost exactly that one). Remaining 14 after D26 =
  awk, beanshell, dockerfile, fish, kotlin, makefile, nim, rust, sed, swift, tcl, terraform_hcl, xslt, zsh (5 days left, so
  ~9 never ship). Rebuild it nightly from the auto-* expected.json. Siblings pair up (D25 Elixir -> D26 Erlang, both BEAM).
- From day 2 on, every fixture hides a **self-describing plan** `v=N|steps=a,b|adapter=..|stage_count=..|campaign_id=..|<indicators>`
  behind a codec named in a `Codec_<id>` / `CODEC_<id>` / `rem HUNTRESS-CODEC:` const (`rep|transform|key`); most exact_text answers
  are plan values verbatim. From D8 a **`v=3` plan** carries `role=`/`attack=` itself behind a `HUNTRESS_ANALYSIS_V1:<TAG>-` comment.
- The hard part is **naming CODE SHAPE**: control-flow, expansion, and function/invocation/property styles. These are GM synthetic
  labels that are not in the plan. Role and scenario are enums, so read `accepted_values`.
- Single-solve files are named by behaviour (host-context, memory-stage, embedded-write, remote-write, local-dispatch,
  staged-handoff, outbound-transfer, impact-plan, relay-handoff); answer-id = `<lang>-<role>-<field>`. **Timed D23: members are
  `<6hex>.<ext>` and ids `<family>-<6hex>-<field>`** -- no behaviour name anywhere; role comes from the plan only.
- Narrative prompts (D8, D15-D26: equivalence, network/process reconcile, outlier level, request order, config drift, D26
  "message flow ... true cross-language indicators vs collision decoys") have NEVER been asked as a compare/outlier question.
  Only D23's "correlate with the corpus" surfaced once, as the cross-file `python-<6hex>-handoff-id` (= PS `$HandoffId`).
- Time Trial windows ~5-17 s when the solver fits. Mastery = `setN.` ids; 2 sets d2-d7/d10-d14, 5 sets d8-d9/d15-d21, 6 sets
  D22 (8502), 7 sets D23 (10465), 8 sets D24 (12480), 9 sets D25 (14625), **10 sets D26 (16770 = 10 x 1677)** -- +1 set/day since D21 -- in one outer `evidence-01.zip` holding `evidence-01..07.zip`; the set loop is
  count-agnostic. Same-named deliveries: pair by sha256. Timed questions carry `[assigned-artifact-sha256:<hex>]`. From D15 the
  timed contracts are the untimed regular pool (`run_for_time:false`, `variant_fresh:true`, no deadline).

## Variant axes (what differs between the single, Time Trial and Mastery variants of the SAME day -- parse every value listed)
Each miss cost one failed timed attempt + a generalize cycle (D6: 4 cycles; D7: 1; D8-D14: 0; D15: 1; D16-D22: 0). **D23: TT
5 generalize workers, Mastery 3 -- ~14 min + ~11 min to CORRECT**; D24-D26: 0 (per-file shape persisted, solver fit). Auto cases
D20-D22 (TT 717b8371/f01e0ff9/c355207f, M 1478867c/2620b793/c8d60ca4), D24 (TT 1c3f64b8, M 2afec5c3), D25 (TT b59af3dd,
M 9fd70fc3) and D26 (TT 0e1b4db2, M 704c5911) are value re-rolls; D23 TT b10c4da4 / M e24c070d carry the new shape.
No `VARIANT AXIS:` line was written D24-D26 (the D26 NOTES.md still carries only the D7-D8 lines).
- **CONTRACT SHAPE (D23 NEW; single vs timed)** -- single: semantic ids `<lang>-<role>-<field>` over behaviour-named members
  (1461). Timed: members renamed `<6hex>.<ext>`, ids `<family>-<6hex>-<field>` (families `powershell`, `jscript`, `batch`,
  `vbscript`, `python`, `bash`, `bash-advanced`, `nodejs`, `polyglot-<lang>` incl. `polyglot-javascript/jscript/vbscript` for
  the hosts). New/changed fields: **composite `style`** = labels joined by `|` (JS `function|invocation|property`; batch
  `graph|control|expansion`; VBS `representation|transform|control`); python `carrier` = `carrier|windows_chain`, python
  `obfuscation` = `syntax|obfuscation`; **`indicator`** = FIRST plan indicator present in the question's order (url, upload_url,
  next_stage, file_path, schedule_path, note/recovery-note name, host_id); **`campaign-token`** = campaign after its first
  hyphen; **`url-host`** = hostname of the plan url; **`path-leaf`** = last segment of file_path; PS `url`/`secondary`/
  `tertiary` chosen by scenario (resource: wallet/mutex; collection: staged file/UA; impact: note/extension); python
  **`handoff-id`** (cross-file, below). Parse rule: match `^(?P<fam>.+?)-(?P<stem>[0-9a-f]{6})-(?P<field>[a-z][a-z0-9-]*)$`,
  require stem == member stem, route by field name; READ the question text for join order / precedence -- it states both.
  Diff a timed contract's id SHAPE against the single's before trusting the carried solver (D23 solve.py `PF_ID`/`pf_value`).
  **D24-D26: same grammar** (TT 1560 -> 1625 -> 1677): each new language joins as ONE `polyglot-<lang>` family, +13 ids per
  member (role, attack, steps, stage-count, stage-profile, obfuscation, next-language, campaign, url, file-path, url-host,
  path-leaf, campaign-token); a single-mode host file folds in as a 5th member (D24 jsp, D25 elixir: +65; D26 erlang, no host: +52).
- **Plan carrier tag (v=3)** -- D8-D22 `HUNTRESS_ANALYSIS_V1:<TAG>-<data>` with tags `B64`/`HEX`/`HB64`/`FRAG` (= obfuscation
  profile base64/plain_hex/hex_base64/fragmented_hex), fixed per file in every delivery. D18 `SPLIT` = layout tag (no data;
  the data is the next multi-line `[..].join("")` array). **D23 timed: `LYR-<l1>_<l2>[_<l3>]-<data>`**, layers from {`b64`,
  `b32`, `hex`, `rev`, `frag`} in ENCODE order (decode last-first: frag = drop `.`, rev = reverse, b32 = upper+pad); the
  obfuscation answer is the layer string itself (`hex_hex_hex`, `b64_b32`, `b32_rev`, 54 distinct seen). Apps Script splits the
  LYR string across an array -> join first, then LYR-peel. The single still used B64/HEX/HB64/FRAG. Parse rule: tag-directed
  peel when the tag parses as a layer list, else shape peel (max 4 layers); accept only `v=`.
  D24-D26 timed: same 5 layer names, 1-3 layers, 87 distinct strings per Mastery (single-layer `b32`/`b64`/`hex` included);
  no new layer name in 4 days.
- **Plan VOCABULARY re-roll (D23-D24 timed)** -- stage_profile `<colour>_<shape>` (amber/cobalt/ivory/onyx/ruby/slate/teal/umber x
  braid/ladder/lattice/pivot/spindle/weave), next_language anything (awk, beanshell, dockerfile, elixir, erlang, fish, jsp,
  kotlin, makefile, nim, rust, sed, swift, tcl, terraform_hcl, xslt, zsh; D24 -jsp, D25 -elixir, D26 -erlang), stage_count 2-8, timed polyglot
  roles span all 8 (persistence_descriptor/T1053, uploader/T1041, dropper/T1140, stager/T1105 included), python syntax/obfuscation new
  (match_case, walrus_binding, class_staticmethod, marshal_envelope_plan, closure_cells, string_table, lambda_indirection).
  Parse rule: plan-verbatim; never validate plan values against a known list.
- **GM label regime (batch `expansion`)** -- SAME bytes, DIFFERENT label by key. Old regime (D3-D14 + D15 single): whole
  handoff, `echo(!var!)` => delayed unless a FOR/h-pool rule fires. Statement regime (D15 timed, D16+ every mode; `run_for_time
  is False` OR `started_at >= 2026-10-16`; `lib.codec.label_regime`): label the JOIN STATEMENT -- `!a!!b!` = delayed; `for ..
  do call set` = for_indirect; bare `call set "x=%%h0%%.."` = call_double; `call set` over other pools = percent; plain `set
  "x=%a%%b%"` = percent. **D23 FIELD-keyed: inside the composite `-style` triple a `call set "..%%x%%.."` second pass is
  `call_double` on ANY pool** (TT b10c4da4 4 ids, Mastery e24c070d 12 ids rejected as `percent`), while the stand-alone
  `-expansion` field keeps `percent` for the same construct. When byte-identical constructs get different labels, tabulate
  (construct, label) against EVERY contract key (started_at, run_for_time, variant_fresh) AND the asking field at once.
- **Mastery set scoping (D23)** -- the same member stem (`4c1097.py`) recurs in all 7 sets with a different precursor value per
  set; a cross-file lookup indexed over the whole bundle returned set1's handoff id for sets 2-7 (6 rejected). Parse rule: index
  and resolve cross-file references PER SET (inner `evidence-0N.zip`), never per outer artifact. D24-D26: stems identical across
  all sets and the TT (D26 erlang `0640aa`/`2d7c2a`/`9d22ec`/`c348b2` in set1..set10) with set-distinct plans.
- **Codec per file** -- rep x transform x key re-roll per variant; NEW rep names appear only on variants (D7 TT
  `unicode_escapes`, `json_numbers`, `reversed_base64`, Bash `xor_hex|cd`). Decode by material SHAPE x named transform; accept
  only `v=`. Spec arity: `rep|transform|key`, `rep|` (empty = identity), or transform folded into the rep (`xor_hex|cd`).
- **Plan carrier NESTING (D10 MOF, D19 ASPX)** -- inner script as an escaped string of the host; unescape (`\n \" \\`, `""`,
  `&quot;`/CDATA, `"`) and rescan; call `lib.codec.v3_plan` before anything else.
- **Plan carrier host syntax (v=3)** -- marker in the host's comment: `//`, `--`, `;`, `<!-- -->`, `#` (Perl, Ruby, YAML,
  **GDScript**), `'` in `<% %>`. Descriptor forms: `$descriptor_<id>`, `var/local/const/final String/my descriptor_<id> =`,
  AutoIt `Global Const`, AppleScript `property ..:`, AHK `:=`, Ruby `DESCRIPTOR_<8HEX> =`, `<HuntressDescriptor>`, ASP `Dim`
  then assign, builder maps, YAML `env: HUNTRESS_DESCRIPTOR:` (no id), NSIS `StrCpy $0 ".."` (no name), **GDScript typed const
  `const DESCRIPTOR_<8HEX>: String = ".."`** (type annotation between name and `=`). Parse rule: regex the MARKER
  `HUNTRESS_ANALYSIS_V\d+\s*:\s*(\w*)-?\s*([^\s"'<>\]]+)` over raw bytes; never anchor on `=`/`:=`/`set`/`<-`.
  D25 Elixir: `#` marker + a plain lowercase binding `descriptor_<8hex> = ".."` (NOT the forecast `@descriptor` attribute or a
  `~s()` sigil) + `_plan_<8hex> = %{descriptor: ..}` map. **D26 Erlang: NEW comment char `%` (single, not `%%`), and NO
  descriptor name at all** -- `-module(plan_<8hex>).` / `-export([build_plan/0]).` / `build_plan() -> "<data>".` (the data
  is a FUNCTION RETURN literal, like D22 NSIS `StrCpy $0`); no shebang, no `-define`, no `<<"..">>` binary, no spawn/`!`/
  `receive`. Second form (after NSIS) where only the marker regex finds the data -- keep the marker as the primary anchor.
- **Literal shapes (D6-D7)** -- radix from the code; base64 std AND urlsafe; reverse the LIST vs the TEXT (try both); join
  split chunks / `+=` / adjacent strings / `.`-FRAG / `[..].join("")` first; carriers may be frozen exes (D6 cx_Freeze).
- **Transport/runner, not variant** -- D7 TT `{"error":"rate_limited"}` saved as the zip; D8 TT 503; D16 60 s runner cap; D23
  one TT generalize worker died "Prompt is too long" (1.39 M tokens: the 1495-id contract + artifacts inlined). Never harvest
  these as cases.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "method=AES Encrypted" | Triage already extracted it (`work/extracted/`) and decoded every plan. Diff the member list / contract ids against yesterday's to find the new language. Open members with `lib.common.read_member` (zipfile can't read AES). |
| Prior-day languages in the contract | Cumulative: rerun the carried marker-routed solver FIRST (D9-D23 single: it covered each new v=3 language unchanged except D18/D19 carrier patches). Any planless file: `lib.codec.v3_plan(text)`. Spend thinking on the new language and on label regimes. |
| **Timed contract ids `<family>-<6hex>-<field>`, members `<6hex>.<ext>` (D23)** | Contract-shape change, not a decode failure. Count ids answered vs asked FIRST; route by `PF_ID` + field name; composite fields join with `\|` in the question's order; indicator by the question's precedence list; resolve cross-file ids (`handoff-id`) per set. |
| `HUNTRESS_ANALYSIS_V1:LYR-<l>_<l>-..` (D23 timed) | Tag = encode layers (b64/b32/hex/rev/frag); undo last-first; obfuscation answer = the layer string verbatim. |
| `.ps1` `$encodedMaterial = [Convert]::FromBase64String('..')` + `$nativeTypes` | `base64 -d` -> JSON descriptor: url/wallet/mutex/UA/file/ext/note by SHAPE. `$nativeTypes`: Process/Registry+wallet=resource, ZipFile/HttpWebRequest=collection, Aes/DirectoryInfo=impact. `invoke-python-stage.ps1` carries `$HandoffId = 'PSPY-<16HEX>'` + `$NextStage`. |
| `.js` WSH, `decode_*`/`recover_*`/`inspect_*`, XOR key arrays | Run each file in an empty `node` `vm` (no require/ActiveXObject, `eval` -> capture); keep the first object with `steps`. Styles from the `inspect_*` body. |
| `.bat/.cmd` `rem HUNTRESS-CODEC:` / `set "itemN=..` / `:HUNTRESS_INSPECT` | Plan in `set` fragments; emulate cmd expansion in Python. Expansion label: statement regime, but `call set %%x%%` inside a `-style` triple = call_double (Variant axes). Never run cmd. |
| `.vbs` `Const Material_<id>`, `Const Codec_<id> = "rep|transform|key"` | Decode from the Codec const; rep/transform = Codec fields 1/2 verbatim. Control = construct wrapping `Decode_` inside `Recover_`. |
| `.py` `*-recovered.py` with `MATERIAL_<id>`, `CODEC_<id>` | Decode from CODEC (or AST-whitelisted `decode_(load_(..))`). Plan v=2 carries syntax/obfuscation/carrier/windows_chain verbatim. |
| `.sh` `readonly Material_<id>` + `readonly Codec_<id>` (+ `Feature_<id>()`) | Decode from the Codec const (multi-byte key = COMMA list). `Feature_` fixtures: role `advanced_syntax`, feature/primitive/campaign/stage_count/steps plan-verbatim, T1059.004. Never run bash. |
| `.mjs` ESM `const Material_<id>`, async `load_/decode_/recover_/inspect_/plan_<id>` | Static decode (`lib.codec.find_codecs` + shape fallback). Plan fields verbatim. |
| `HUNTRESS_ANALYSIS_V1:<TAG>-..` in any comment + a descriptor literal (`.php .lua .js .vbs .mof .ts .au3 .applescript .proj .pl .rb .ahk .gs .csx .groovy .yml .nsi .gd`) | **Route by the marker before the extension.** Peel to `v=3|language=..|role=..|attack=..|adapter=..|host_profile=..|obfuscation_profile=..|stage_profile=..|next_language=..|stage_count=..|steps=..|campaign_id=..|url=..|file_path=..`. EVERY answer incl. role/attack is plan-verbatim. |
| `HUNTRESS_ANALYSIS_V1:SPLIT` (no data) + `const HUNTRESS_ANALYSIS_V1_SPLIT_<id> = [..].join("")` (D18) | Join the array literals, drop the `<TAG>-` head, peel. 44 new ids unanswered = CARRIER bug; never walk the role enum. |
| ASPX `<script runat="server">` + `EmbeddedCsx_<id> = "// HUNTRESS..\n..\"..\";"` (D19) | NESTED carrier: unescape `\n`/`\"`/`\\` (and `""`, `&quot;`, CDATA) and rescan; `lib.codec.v3_plan` does. |
| New language, plain one-line marker: `.csx` (D19), `.groovy` (D20), `.yml` (D21 `env: HUNTRESS_DESCRIPTOR`), `.nsi` (D22 `StrCpy $0`), `.exs` (D25, next row), **`.gd` (D23: line-1 `# HUNTRESS_ANALYSIS_V1:<TAG>-..`, `extends RefCounted`, `const DESCRIPTOR_<8HEX>: String = ".."`, `func build_plan_<id>() -> Dictionary: return {"descriptor": ..}`)** | Carried solver answers unpatched: plan-verbatim. Spellings: `language=<family>` (csharp_script / groovy / github_actions / nsis / gdscript), campaign `<FAMILY_UPPER>-<8hex>`, url host `<family>-<10hex>.example.invalid`, file_path `/tmp/huntress-<family>/.<16hex>.stage`, attack T1059 parent / T1105 / none, host_profile `standalone`. Host syntax (pipeline, triggers, Section, `extends`) is inert noise. Don't YAML-parse (PyYAML turns `on:` into `True`). |
| D24-D26 one-file languages: `.jsp` `<%-- marker --%>` + `<%! private static final String DESCRIPTOR_<8HEX> = "..";` / `.exs` `# marker` + `descriptor_<8hex> = ".."` + `%{descriptor: ..}` / **`.escript` `% marker` + `-module(plan_<8hex>).` + `build_plan() -> "<data>".` (no descriptor NAME)** | Carried solver, unpatched: the MARKER regex is the anchor. Plan-verbatim: `language=<lang>`, campaign `<LANG>-<8hex>`, host `<lang>-<10hex>.example.invalid`, `/tmp/huntress-<lang>/`. Hosts `host-jsp-webshell-jsp` (`jsp_webshell`) / `host-elixir-phoenix-elixir` (`elixir_phoenix`) are inert stubs (`"inert-analysis-fixture"`), role staged_chain -- copy role=. No request/exec/spawn/`receive` code shipped despite the prompts. |
| `<%@ Language=VBScript %>` + `<% ' HUNTRESS_ANALYSIS_V1:..` in a `.vbs` (D20) | v=3 host for an OLD language (`language=vbscript`, host_profile `classic_asp`). Route by the marker. |
| Prompt about fetch targets vs network evidence (D17) / process tree (D18) / "level that doesn't belong" (D23) / "order of requests and stages, inert fixture vs real execution primitives" (D24) / "the setting that didn't survive" (D25) / "message flow, true cross-language indicators vs collision decoys" (D26) | Flavour unless a question or an evidence file asks. Network: `lib.codec.network_indicators`/`reconcile`; process: `process_events`/`reconcile_processes`; outlier: `lib.codec.plan_canonical`. |
| An id whose field suffix is a plan key never asked before | `lib.codec.plan_answer(answer_id, plan, q)` / `plan_key_for` (longest suffix, hyphen->underscore). |
| `Codec_` key like `ba` / `0a` / `ec` | A hex byte. Transforms are ENCODE-side names: `subtract_modulo_256` decodes by ADDING; `rolling_xor` = c ^ previous CIPHER byte. |

## Codec table (`Codec_<id>='<rep>|<transform>|<key>'`, batch `rem HUNTRESS-CODEC:<rep>|<transform>`; seen D3-D23)
`lib.codec.find_codecs(text)` / `lib.codec.decode(material, rep, transform, key)` (unknown names -> None => decode by shape).
Reps: base64 (literal/chunks/urlsafe/reversed), hex (pairs/compact/colon/dash/`\x`/`0x`/buffer/array), percent_hex,
escaped_octets, unicode_escapes, decimal lists/json_numbers/integer_list/tuple, octal_space, reversed_text/_hex/_decimal/
_integer_list, plain/split_fragments, v=3 hex_base64, D23 LYR stacks. Transforms (key hex; multi-byte = COMMA list): identity
(also EMPTY), reverse(_bytes), single_byte_xor, repeating_key_xor, reverse_then_xor, rolling_xor, add_modulo_256 (decode
SUBTRACTS), subtract_modulo_256 (decode ADDS); batch names carry the parameter (xor_5a, add_7); bash `xor_hex|<key>`.

## Day by day
**D1-D7 (PS -> Node, 469 ids)**: D1 collection ATT&CK cost 5 wrong before `T1555.003`; D2 7 wrong ATT&CK guesses; **D3 ~1 h 45
min, ~127 rejected probes** on batch labels -> NAMING LAWS; D4 VBS control 4 wrong; D5-D6 0 wrong; D7 TT missed 15 ids on new reps.
**D8-D15 (PHP .. Perl; 615 -> 1026)**: D8 introduced v=3 (copy role/attack/adapter/profiles); each language = 4 polyglots
(benign_utility/downloader/launcher/staged_chain) + sometimes a `host-<profile>-<lang>`. D14 prompt ATT&CK (T1127.001) was NOT
the answer. D15 timed missed ~25 batch-expansion ids -> the label-regime axis.
**D16-D22 (Ruby, AHK, Apps Script, C#, Groovy, GHA, NSIS; 1095 -> 1417)**: carried marker-routed solver each day; twists D18
SPLIT array (~30 rejected enum probes, CORRECT T+54 s) and D19 escaped nested carrier (guessed value sank a 46-id bulk; T+39
s). D20-D22 no twist: CORRECT T+13-25 s 0 wrong; TT 5-9 s, Mastery 8.5-18 s first try (D22 first 6-set Mastery).
**D23 Press Start to Decode (GDScript `.gd`; 1461 = +44)**: single carried solver T+52 s; the twist was the TIMED contract
reshape (hashed members, per-file ids, composite fields, `LYR-` tags, re-rolled vocab, cross-file `handoff-id`): 593/1495
answered -> `PF_ID`/`pf_value` + LYR peel -> TT CORRECT T+14 min (4 batch `-style` ids -> call_double); Mastery lost 12
`-style` + 6 handoff-id (set1 value reused) -> per-set lookup -> T+11 min.
**D24 Web of Lies (JSP, +55 incl. `host-jsp-webshell-jsp`)** and **D25 Ashes to Assets (Elixir `.exs`, +55 incl.
`host-elixir-phoenix-elixir`)**: carried D23 solver unpatched (marker routing); single T+31 s / T+14 s (race win), TT and
Mastery first try, 0 wrong, 0 generalize workers. Hosts were inert (`<%= "inert-analysis-fixture" %>`; a Phoenix controller
`def show(_conn, _params), do: {:ok, "inert-analysis-fixture"}`); v=3 role independent of steps -- copy role=. Both
narrative prompts (request/primitive order; "setting that didn't survive the rebirth") were flavour.
**D26 Mixed Signals (base `beam-message-flow`; 1615 ids = +44, 171 members)**: +4 `polyglot-erlang-{benign-utility,
downloader,launcher,staged-chain}.escript`, no host (like D23). Artifact: 4-line Erlang modules -- `% HUNTRESS_ANALYSIS_V1:
<B64|HEX|HB64|FRAG>-<data>`, `-module(plan_<8hex>).`, `-export([build_plan/0]).`, `build_plan() -> "<same data>".` -- no
shebang, no named descriptor, no spawn/`!`/`receive`, no decoy indicators. Plans `language=erlang`, `ERLANG-<8hex>`,
`erlang-<10hex>.example.invalid/stage`, `/tmp/huntress-erlang/.<16hex>.stage`, `standalone`, attack none/T1105/T1059 (parent
accepted); role again independent of steps (benign_utility with `decode_embedded>write_file>dispatch_process`) -- copy role=.
Insight: none needed -- the marker regex is comment-syntax-agnostic, so a NEW comment char (`%`) and a nameless
function-return literal cost nothing. Prompt ("passes messages between processes ... separate true cross-language indicators
from deterministic collision decoys planted to look like old friends") = flavour, 13th narrative never asked. Commands: reuse
race of the carried `solve.py` -> `hctf submit --from-solver` (the worker's own submit was refused "nothing new"). **Single
CORRECT T+39 s, 0 wrong, one submit**; TT 0e1b4db2 1677/1677 first try (solve 4.5 s, total 8.1 s); Mastery 704c5911 (10 sets,
16770) first try (solve 6.2 s, total 14.1 s). No VARIANT AXIS lines, no generalize workers.

## GM answer conventions learned
- **Check `answer_format.kind` first.** `enum` lists values (scenario, role). `mitre_attack_id` takes `T####[.###]` or literal
  `none` (benign_utility). `integer`/`ordered_tokens` (d6+; steps joined with `>`). `exact_text` = plan value or synthetic label.
  **D23 composite exact_text** = labels joined by `|` with NO spaces, in the order the question lists.
- **Plan-verbatim fields** (copy exactly): adapter (COM ProgIDs `MSXML2.ServerXMLHTTP.6.0`, LOLBins `CertReq.exe`/`curl.exe`,
  batch `call`/`set`/`for`, v=3 local_parser/runtime_loader/file_writer/http_client/process_builder/schedule_builder/
  operation_graph); indicators (campaign_id, host_id, url, file_path, upload_url, next_stage, extension, note_name, handoff_id,
  cron_path, schedule_path, service_name -- "exact X indicator", X = plan key); batch `graph` (linear/single/diamond/fan_out/
  fallback_retry/cross_language/same_language); Python syntax/obfuscation/carrier/windows_chain; Bash feature/primitive; v=3
  host_profile (standalone, wsf_jscript, wsf_mixed, hta_jscript, php_webshell, sct_scriptlet, lua_openresty, perl_cgi,
  ruby_rack, google_docs_sidebar, aspx_inline_csharp, jenkins_pipeline, classic_asp, jsp_webshell (D24), elixir_phoenix (D25);
  polyglots `standalone`, incl. D26 erlang),
  obfuscation (single: base64/plain_hex/hex_base64/fragmented_hex; timed D23: LYR layer string), stage_profile (single:
  single_descriptor/two_stage_download_execute/three_stage_decode_write_launch/cross_language_handoff; timed D23 `<colour>_
  <shape>`), next_language. **Derived D23 fields**: campaign-token (after FIRST hyphen), url-host (hostname, underscores kept),
  path-leaf (last `/` or `\` segment, leading dot kept), indicator (first present in the stated order).
- **v=3 role and attack too.** GM accepts the plan's PARENT ids `T1059` (launcher, staged_chain, hosts) and `T1053`
  (persistence_descriptor) for every v=3 language through D26 Erlang. The attack question TEXT states the precedence ("parent
  technique also accepted ...; for a staged chain or relay the earlier ingress-transfer technique is also accepted; none for a
  relay") -- read it before probing. **v=3 role does NOT follow `steps`** (D14-D26) -- copy role=, steps=, stage_profile=.
- **Role from `steps`** (v=1/v=2 only): decode_configuration,return_configuration = benign_utility; acquire_remote +
  dispatch_memory/pipe = stager; acquire_remote,write_file = downloader; decode_embedded,write_file = dropper; locate_local,
  dispatch_process = launcher; read_file/upload,transmit_remote = uploader; transform + recovery_note = impact;
  build_schedule,register_descriptor = persistence_descriptor; recognize_syntax,reconstruct_intent + `feature=` = advanced_syntax;
  ends in handoff_script or profile_host..dispatch_process = staged_chain; dispatch_next_stage (Python) = relay.
- **Role -> ATT&CK** (v=1/v=2; `lib.scripts.role_attack(role, lang)`): benign `none`; downloader/stager T1105; dropper T1140;
  uploader T1041; impact T1486; persistence_descriptor T1053.003; advanced_syntax T1059.004; launcher/staged_chain/relay = host
  language T1059.003 batch / .004 bash / .005 VBS / .006 python / .007 JScript and Node. PS scenarios: resource_hijacking T1496,
  synthetic_collection T1555.003, synthetic_impact T1486. REJECTED: T1218.010, T1620, T1027.009, T1005, T1560, T1119, T1074.
- **Batch expansion** (enum percent/delayed/call_double/for_indirect): statement regime = Variant axes (default from D16), and
  the D23 `-style` triple's call_double rule. Fragment JOINER pitfall: `set "item9=%item0%%item1%.."` is the JOIN, not fragment
  9. REJECTED spellings: percent_expansion, immediate, call-double, double_call.
- **Batch control**: direct, errorlevel_guard (`ver >nul` + `if errorlevel 1 exit /b 1`), goto_dispatch, call_subroutine,
  if_guard (`if defined X`); separators and `:HUNTRESS_UNUSED` dead labels are NOT control.
- **VBS control**: direct, select_case, do_once, while_once, error_guard (`On Error Resume Next`..`Err.Raise`), for_once.
- **JScript styles**: function-style declaration / anonymous_expression / named_expression; invocation-style direct / call /
  apply; property-style dot / bracket_literal / mixed.
- **NAMING LAWS**: conditional/bail-out = `<keyword>_guard`; run-once loop = `<keyword>_once`; control transfer =
  `<keyword>_<action>`. Spelled-out statements and descriptive synonyms have ALWAYS been rejected.

## Pitfalls that cost time
- **Trusting the single's contract shape in timed modes** (D23: 593/1495 answered, two ~11-14 min recoveries): before a timed
  run, compare the id GRAMMAR (not just the count) of the timed contract with the single's; an unknown `<fam>-<6hex>-<field>`
  shape or a new field suffix means route-by-field work, not decoding work. Composite answers: read the order from the question.
- **Cross-file lookups across Mastery sets** (D23, 6 ids): the same member stem exists in every set; index per inner zip.
  **A label fix that lands in only one field/mode** (D23: Mastery lost 12 more ids on the same construct over other pools):
  generalize a label rule over EVERY construct instance and every asking field, then re-run all cases.
- **Generalize workers dying on context size** (D23 1.39 M-token prompt): never inline a 1500-id contract or the extracted
  corpus; point at paths and summarise the id grammar.
- **Enum-walking when the plan did not decode** (D18 ~30 probes; D19 2 + a poisoned bulk): a planless v=3 file is a CARRIER
  problem; `lib.codec.v3_plan`, else read the bytes around the marker. A GUESSED value in a bulk POST rejects the whole bulk.
- **Probing synonyms instead of deriving.** D3 lost ~1.5 h; apply the naming laws first; `hctf labels` seeds candidates.
- **Generic ATT&CK guesses** (d1, d2): use the role->ATT&CK table; a v=3 `attack=` is authoritative; a prompt's hint is not.
- **Routing by file extension or name** (D8-D9 `.js` held HTA/WSF/SCT; D19 `.csx` an ASPX page; D20 `.vbs` classic ASP; D23
  timed members are bare `<6hex>.<ext>`): route by the plan marker, role from the plan. Never REQUIRE a descriptor name or a
  known comment char: D22 NSIS and D26 Erlang (`%`, `build_plan() -> ".."`) carry only the marker + a bare literal.
- **Answer-id field parsing** (D8): family names contain hyphens/underscores; longest known `-<field>` suffix (`stage-count`/
  `stage-profile` before `stage`, `campaign-token` before `campaign`).
- **GM error body saved as the artifact** (D7 TT): check size + sha256 first; tiny `{"error":..}` = re-download, exit non-zero.
- **Stale notes travel with copied solvers** (D8-D26 `solver/NOTES.md` still opens with the D7 heading): date every VARIANT
  AXIS line by day + attempt id; diagnose EVERY failed attempt.
- **cmd parsing**: `%item0%` is a variable, not `%0`+`item`; CRLF/LF mixes and `SeT` casing occur. **stage_count != len(steps)**.
- **Timed modes are a transport race**: fork per set, submit all sets in one call (GM D26 guidance: one request may carry
  4 MiB of JSON, enough for the largest Mastery; split only above that); pair
  same-named Mastery deliveries by sha256; index nested AES zips once, never decrypt script leaves to sniff for PK.
- **Reading the narrative prompt as the task** (D8, D15-D26): thirteen prompts promised comparison/reconciliation/outlier questions
  that never came. Diff `answer_ids` first; spend time only on ids the carried solver cannot answer.
- **Never execute fixtures.** Decode from the Codec const / descriptor plus a restricted interpreter; accept a plan only if it
  parses as `k=v|..` with `steps` (or `feature`).
