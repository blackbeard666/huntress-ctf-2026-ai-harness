# script-analysis — technique log (days 1-27; updated after every day)

How this lane has looked so far (these are observations, not guarantees):
- **Timed variants MUTATE** (organizer D8: "new, dynamic variations/mutations"): solvers derive structure and degrade per
  field. D23-D26 timed contracts had a DIFFERENT SHAPE from the single (hashed members, per-file ids, composite fields, `LYR-`
  tags; the carried solver answered 593/1495 TT ids on D23); **D27 flipped back** to the single grammar. Keep both paths.
- One AES zip `evidence.zip` (password `infected`) of inert "Huntress Script Triage" fixtures. **The single contract is
  CUMULATIVE**: each day keeps every earlier file/question and adds one language; bytes and values re-roll daily. PS (d1, 15
  ids) -> JScript, Batch, VBScript, Python (d5, 357), Bash, Node + Bash advanced (d7, 469) -> PHP + WSF/HTA/webshell hosts (d8,
  615) -> Lua/SCT, MOF, TypeScript, AutoIt, AppleScript, MSBuild (d14, 971) -> Perl, Ruby (d16, 1095), AutoHotkey, Apps Script,
  C# `.csx` + ASPX (d19, 1249) -> Groovy + Jenkins + classic ASP (d20, 1329) -> GitHub Actions (d21), NSIS (d22, 1417) ->
  GDScript (d23, 1461) -> JSP + host (d24, 1516) -> Elixir + Phoenix host (d25, 1571) -> Erlang (d26, 1615) -> **Dockerfile
  (d27, 1659 = +44, 175 members, no host)**. Bash advanced +2 on some days (none d26-d27). Since D8 the TITLE is a pun and the
  base id names the theme (D22 "Next, Next, Finish" -> NSIS; D24 "Web of Lies" -> JSP; D26 "Mixed Signals"/`beam-message-flow`
  -> Erlang; D27 "FROM Whence It Came"/`docker-build-attribution` -> Dockerfile); D25-D27 prompts NAMED the language.
- **Forecast cue (4/4 hits D24-D27, then GONE)**: the D23-D26 timed plans' `next_language` pool held only never-shipped
  languages and each day's new one left it (jsp, elixir, erlang, dockerfile). D27's timed plans carry only the 8 base
  languages -- no pool for D28. Remaining 13 = awk, beanshell, fish, kotlin, makefile, nim, rust, sed, swift, tcl,
  terraform_hcl, xslt, zsh (4 days left). Fallback = siblings (D25 Elixir -> D26 Erlang; D27 Dockerfile -> Makefile?).
- From day 2 every fixture hides a **self-describing plan** `v=N|steps=a,b|adapter=..|stage_count=..|campaign_id=..|<indicators>`
  behind a `Codec_<id>` / `CODEC_<id>` / `rem HUNTRESS-CODEC:` const (`rep|transform|key`); most exact_text answers are plan
  values verbatim. From D8 a **`v=3` plan** carries `role=`/`attack=` itself behind a `HUNTRESS_ANALYSIS_V1:<TAG>-` comment.
- The hard part is **naming CODE SHAPE** (control-flow, expansion, function/invocation/property styles): GM synthetic labels
  not in the plan. Role and scenario are enums -- read `accepted_values`. Single files are named by behaviour (host-context,
  memory-stage, embedded-write, remote-write, local-dispatch, staged-handoff, outbound-transfer, impact-plan, relay-handoff).
- Narrative prompts (D8, D15-D27: equivalence, network/process reconcile, outlier, request order, config drift, collision
  decoys, D27 "sharing strings doesn't mean sharing parents ... attribute each specimen") have NEVER been asked. Only D23's
  "correlate with the corpus" surfaced once, as the cross-file `python-<6hex>-handoff-id` (= PS `$HandoffId`).
- TT windows ~5-17 s when the solver fits. Mastery = `setN.` ids, +1 set/day since D21 (6 sets D22 ... 10 D26, **11 D27 =
  18249**) in one outer `evidence-01.zip` of inner `evidence-0N.zip`; set loop count-agnostic; pair same-named deliveries by
  sha256. Timed questions carry `[assigned-artifact-sha256:<hex>]`; from D15 timed = untimed regular pool (`run_for_time:false`).

## Variant axes (what differs between the single, Time Trial and Mastery variants of the SAME day -- parse every value listed)
Each miss cost one failed timed attempt + a generalize cycle (D6: 4; D7: 1; D15: 1; **D23: TT 5 workers + Mastery 3, ~25 min**;
all other days 0). Auto cases D20-D22, D24-D26 = value re-rolls; D23 (TT b10c4da4, M e24c070d) = per-file shape; D27 (TT
6daf90f0, M ee4eeb7f) = semantic shape again. No `VARIANT AXIS:` line written D24-D27 (NOTES.md: D7-D8 lines + speed notes).
- **CONTRACT SHAPE (single vs timed; D23-D26 per-file, D27 back to semantic)** -- single: ids `<lang>-<role>-<field>` over
  behaviour-named members. D23-D26 timed: members `<6hex>.<ext>`, ids `<family>-<6hex>-<field>` (families `powershell`,
  `jscript`, `batch`, `vbscript`, `python`, `bash`, `bash-advanced`, `nodejs`, `polyglot-<lang>`); **composite `style`** =
  labels joined by `|` (JS `function|invocation|property`; batch `graph|control|expansion`; VBS `representation|transform|
  control`; python `carrier|windows_chain`, `syntax|obfuscation`); **`indicator`** = FIRST plan indicator present in the
  question's order; **`campaign-token`** = after the first hyphen; **`url-host`**; **`path-leaf`** = last segment of file_path;
  PS `url`/`secondary`/`tertiary` by scenario; python **`handoff-id`** (cross-file). New language = ONE `polyglot-<lang>`
  family, +13 ids/member, a host folds in as a 5th member (TT 1495 -> 1560 -> 1625 -> 1677). **D27 timed = the single's
  grammar** (TT 1659 = single, Mastery `setN.` x 11; 0 `<6hex>` ids). Parse rule: detect the grammar PER CONTRACT (an id
  matching `^(?P<fam>.+?)-(?P<stem>[0-9a-f]{6})-(?P<field>[a-z][a-z0-9-]*)$` with stem == a member stem => per-file
  `PF_ID`/`pf_value` path, else semantic); route by field name; READ the question for join order / precedence.
- **Plan carrier tag (v=3)** -- single D8-D27: `HUNTRESS_ANALYSIS_V1:<TAG>-<data>`, tags `B64`/`HEX`/`HB64`/`FRAG` (=
  obfuscation base64/plain_hex/hex_base64/fragmented_hex; FRAG = `.`-separated hex), D18 `SPLIT` = layout tag (data in the
  next `[..].join("")` array). **D23-D26 timed: `LYR-<l1>_<l2>[_<l3>]-<data>`**, layers {`b64`,`b32`,`hex`,`rev`,`frag`} in
  ENCODE order (decode last-first; obfuscation answer = the layer string, 87 distinct per Mastery). **D27 timed: no LYR**,
  single tags again. Parse rule: tag-directed peel when the tag parses as a layer list, else shape peel (max 4); accept `v=`.
- **Plan VOCABULARY (D23-D26 timed)** -- stage_profile `<colour>_<shape>`, next_language = never-shipped pool, stage_count
  2-8, all 8 roles, new python syntax/obfuscation names. **D27 timed: single vocabulary again** (4 stage_profiles, 8 base
  next_languages). Parse rule: plan-verbatim; never validate plan values against a known list.
- **GM label regime (batch `expansion`)** -- SAME bytes, DIFFERENT label by key. Old regime (D3-D14 + D15 single): whole
  handoff, `echo(!var!)` => delayed unless a FOR/h-pool rule fires. Statement regime (D15 timed, D16+ every mode; `run_for_time
  is False` OR `started_at >= 2026-10-16`; `lib.codec.label_regime`): label the JOIN STATEMENT -- `!a!!b!` = delayed; `for ..
  do call set` = for_indirect; bare `call set "x=%%h0%%.."` = call_double; `call set` over other pools = percent; plain `set
  "x=%a%%b%"` = percent. **D23 FIELD-keyed: inside the composite `-style` triple a `call set "..%%x%%.."` second pass is
  `call_double` on ANY pool** (TT b10c4da4 4 ids, Mastery e24c070d 12 ids rejected as `percent`), while the stand-alone
  `-expansion` field keeps `percent` for the same construct. When byte-identical constructs get different labels, tabulate
  (construct, label) against EVERY contract key (started_at, run_for_time, variant_fresh) AND the asking field at once.
- **Mastery set scoping (D23)** -- the same member stem recurs in every set with set-distinct values; a bundle-wide index
  returned set1's handoff id for sets 2-7 (6 rejected). Parse rule: resolve cross-file references PER inner `evidence-0N.zip`.
- **Codec per file** -- rep x transform x key re-roll per variant; NEW rep names appear only on variants (D7 TT
  `unicode_escapes`, `json_numbers`, `reversed_base64`, Bash `xor_hex|cd`). Decode by material SHAPE x named transform; accept
  only `v=`. Spec arity: `rep|transform|key`, `rep|` (empty = identity), or transform folded into the rep (`xor_hex|cd`).
- **Plan carrier NESTING (D10 MOF, D19 ASPX)** -- inner script as an escaped string of the host; unescape (`\n \" \\`, `""`,
  `&quot;`/CDATA, `"`) and rescan; call `lib.codec.v3_plan` before anything else.
- **Plan carrier host syntax (v=3)** -- marker in the host's comment: `//`, `--`, `;`, `<!-- -->`, `#`, `'` in `<% %>`, D26
  Erlang `%`. Descriptor forms: `$descriptor_<id>`, `var/local/const/final String/my descriptor_<id> =`, AutoIt `Global
  Const`, AppleScript `property ..:`, AHK `:=`, `DESCRIPTOR_<8HEX> =`, `<HuntressDescriptor>`, ASP `Dim`, builder maps, YAML
  `env: HUNTRESS_DESCRIPTOR:`, GDScript `const DESCRIPTOR_<8HEX>: String =`, Elixir `descriptor_<8hex> = ".."` + `%{..}`;
  NAMELESS: NSIS `StrCpy $0 ".."`, Erlang `build_plan() -> "<data>".`; **D27 Dockerfile `ARG HUNTRESS_DESCRIPTOR="<data>"`
  + indirect use `LABEL huntress.analysis.descriptor=$HUNTRESS_DESCRIPTOR`** (first split of declaration from use). Parse
  rule: regex the MARKER `HUNTRESS_ANALYSIS_V\d+\s*:\s*(\w*)-?\s*([^\s"'<>\]]+)` over raw bytes; never anchor on `=`/`:=`/`set`.
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
| **Timed contract ids `<family>-<6hex>-<field>`, members `<6hex>.<ext>` (D23-D26; D27 back to semantic ids)** | Contract-shape change, not a decode failure. Count ids answered vs asked FIRST; route by `PF_ID` + field name; composite fields join with `\|` in the question's order; indicator by the question's precedence list; resolve cross-file ids (`handoff-id`) per set. |
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
| D24-D27 one-file languages: `.jsp` `<%-- marker --%>` + `<%! private static final String DESCRIPTOR_<8HEX> = "..";` / `.exs` `# marker` + `descriptor_<8hex> = ".."` + `%{descriptor: ..}` / `.escript` `% marker` + `-module(plan_<8hex>).` + `build_plan() -> "<data>".` (no descriptor NAME) / **`.dockerfile` `# marker` + `FROM scratch AS analysis_<8hex>` + `ARG HUNTRESS_DESCRIPTOR=".."` + `LABEL ..=$HUNTRESS_DESCRIPTOR`** | Carried solver, unpatched: the MARKER regex is the anchor. Plan-verbatim: `language=<lang>`, campaign `<LANG>-<8hex>`, host `<lang>-<10hex>.example.invalid`, `/tmp/huntress-<lang>/`. Hosts `host-jsp-webshell-jsp` (`jsp_webshell`) / `host-elixir-phoenix-elixir` (`elixir_phoenix`) are inert stubs (`"inert-analysis-fixture"`), role staged_chain -- copy role=. No request/exec/spawn/`receive` code shipped despite the prompts. |
| `<%@ Language=VBScript %>` + `<% ' HUNTRESS_ANALYSIS_V1:..` in a `.vbs` (D20) | v=3 host for an OLD language (`language=vbscript`, host_profile `classic_asp`). Route by the marker. |
| Prompt about fetch targets vs network evidence (D17) / process tree (D18) / "level that doesn't belong" (D23) / "order of requests and stages, inert fixture vs real execution primitives" (D24) / "the setting that didn't survive" (D25) / "message flow, true cross-language indicators vs collision decoys" (D26) / "sharing strings doesn't mean sharing parents; attribute each specimen" (D27) | Flavour unless a question or an evidence file asks. Network: `lib.codec.network_indicators`/`reconcile`; process: `process_events`/`reconcile_processes`; outlier: `lib.codec.plan_canonical`. |
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
**D24 Web of Lies (JSP, +55 incl. `host-jsp-webshell-jsp`)**, **D25 Ashes to Assets (Elixir `.exs`, +55 incl.
`host-elixir-phoenix-elixir`)** and **D26 Mixed Signals (Erlang `.escript`, +44, no host)**: carried D23 solver unpatched
(marker routing); single T+31 s / T+14 s / T+39 s (race wins), TT and Mastery first try, 0 wrong, 0 generalize workers. Hosts
were inert stubs (`"inert-analysis-fixture"`); v=3 role independent of steps -- copy role=. D26 Erlang had a NEW comment char
(`%`) and a nameless function-return literal (`build_plan() -> "<data>".`) -- free, because the marker regex is
comment-syntax-agnostic. All three narrative prompts were flavour.
**D27 FROM Whence It Came (base `docker-build-attribution`; 1659 ids = +44, 175 members)**: +4 `polyglot-dockerfile-*.dockerfile`
(benign-utility/downloader/launcher/staged-chain), no host, no new bash. Artifact: 4-line Dockerfiles --
`# HUNTRESS_ANALYSIS_V1:<B64|HEX|HB64|FRAG>-<data>`, `FROM scratch AS analysis_<8hex>`, `ARG HUNTRESS_DESCRIPTOR="<data>"`,
`LABEL huntress.analysis.descriptor=$HUNTRESS_DESCRIPTOR`; no RUN/COPY/ENV, no multi-stage, no shared strings despite the prompt. Plans
`language=dockerfile`, `DOCKERFILE-<8hex>`, `dockerfile-<10hex>.example.invalid/stage`, `/tmp/huntress-dockerfile/`,
`standalone`, attack none/T1105/T1059, an unasked `verdict=` key; role independent of steps again. Insight: none needed on the
single (marker-first routing ignores the ARG/LABEL indirection); the twist was TIMED -- TT/Mastery returned to the single's
semantic grammar and the D23 solver (byte-identical D26 copy, both grammars kept) answered it. Prompt ("sharing strings doesn't
mean sharing parents ... attribute each specimen using build-stage, semantic, and static-handoff evidence") = flavour, 14th
narrative. Commands: race reuse of the carried `solve.py` -> `hctf submit --from-solver` (worker's own submit: `already_solved`).
**Single CORRECT ~T+22 s, 0 wrong**; TT 6daf90f0 1659/1659 first try (solve 1.9 s, total 5.7 s); Mastery ee4eeb7f (11 sets,
18249) first try (solve 5.8 s, total 14.9 s). No VARIANT AXIS lines, no generalize workers.

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
  polyglots `standalone`, incl. D26 erlang, D27 dockerfile),
  obfuscation (single: base64/plain_hex/hex_base64/fragmented_hex; timed D23: LYR layer string), stage_profile (single:
  single_descriptor/two_stage_download_execute/three_stage_decode_write_launch/cross_language_handoff; timed D23 `<colour>_
  <shape>`), next_language. **Derived D23 fields**: campaign-token (after FIRST hyphen), url-host (hostname, underscores kept),
  path-leaf (last `/` or `\` segment, leading dot kept), indicator (first present in the stated order).
- **v=3 role and attack too.** GM accepts the plan's PARENT ids `T1059` (launcher, staged_chain, hosts) and `T1053`
  (persistence_descriptor) for every v=3 language through D27 Dockerfile. The attack question TEXT states the precedence ("parent
  technique also accepted ...; for a staged chain or relay the earlier ingress-transfer technique is also accepted; none for a
  relay") -- read it before probing. **v=3 role does NOT follow `steps`** (D14-D27) -- copy role=, steps=, stage_profile=.
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
  The reverse also happens (D27 timed went back to semantic ids): never delete the older grammar path when patching for a new one.
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
  known comment char: D22 NSIS and D26 Erlang (`%`, `build_plan() -> ".."`) carry only the marker + a bare literal; D27
  Dockerfile's use site is `$HUNTRESS_DESCRIPTOR` (a reference, not data) -- read the declaration/literal, never the use.
- **Answer-id field parsing** (D8): family names contain hyphens/underscores; longest known `-<field>` suffix (`stage-count`/
  `stage-profile` before `stage`, `campaign-token` before `campaign`).
- **GM error body saved as the artifact** (D7 TT): check size + sha256 first; tiny `{"error":..}` = re-download, exit non-zero.
- **Stale notes travel with copied solvers** (D8-D26 `solver/NOTES.md` still opens with the D7 heading): date every VARIANT
  AXIS line by day + attempt id; diagnose EVERY failed attempt.
- **cmd parsing**: `%item0%` is a variable, not `%0`+`item`; CRLF/LF mixes and `SeT` casing occur. **stage_count != len(steps)**.
- **Timed modes are a transport race**: fork per set, submit all sets in one call (GM D26 guidance: one request may carry
  4 MiB of JSON, enough for the largest Mastery; split only above that); pair
  same-named Mastery deliveries by sha256; index nested AES zips once, never decrypt script leaves to sniff for PK.
- **Reading the narrative prompt as the task** (D8, D15-D27): fourteen prompts promised comparison/reconciliation/outlier questions
  that never came. Diff `answer_ids` first; spend time only on ids the carried solver cannot answer.
- **Never execute fixtures.** Decode from the Codec const / descriptor plus a restricted interpreter; accept a plan only if it
  parses as `k=v|..` with `steps` (or `feature`).
