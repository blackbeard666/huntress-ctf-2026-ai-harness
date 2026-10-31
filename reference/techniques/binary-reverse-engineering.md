# binary-reverse-engineering — technique log (days 1-30; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
- One `evidence.zip` (AES, password `infected`), CUMULATIVE from D3: one group per past day (`dNN--sample.<ext>`, `variant-000`
  before D22) + ONE new container/language per day: D1 C ELF, D2 C++ (ELF/MinGW PE32+), D3 .NET, D4 Go, D5 Rust, D6 Java jar,
  D7 Kotlin jar, D8 Swift (67 MB), D9 Nim, D10 Zig, D11 D, D12 FPC, D13 Crystal, D14 ObjC, D15 C `-stripped`/`-symbolized`, D16
  WASM `-compact`/`-direct`, D17 Ada, D18 Fortran, D19 GnuCOBOL + `PK19` overlay, D20 Haskell + `RS20` overlay, D21 OCaml
  `-loader.elf` + `-plugin.cmxs`, D22 F# (+ `FSharp.Core.dll`), D23 VB.NET, D24 Scala jar PAIR `-vulnerable`/`-corrected`, D25
  Clojure jar PAIR, D26 Groovy jar (+ `crash/trace.json`), D27 V ELF PAIR `-gcc.elf`/`-tcc.elf`, D28 Odin ELF TRIO `-family-a`/
  `-family-b`/`-false-friend`, **D29 FreeBASIC ELF PAIR `-O0.elf`/`-O3.elf` (43.9 KB each, glibc, not stripped, differ in 12
  bytes), D30 Haxe->Neko bytecode TRIO `-loader.n`/`-library.n`/`-config.n` (~20.9 KB each, magic `NEKO`; first VM-bytecode
  member since WASM; the D19 enum token `neko_bytecode` finally shipped)**.
  Since D18 each day = a THEME on a new language: call graph, packing, overlays, shared libs, managed<->native bridge, anti-
  analysis, PATCH DIFF (D24), BOUNDS ROOT CAUSE (D25), CRASH TRIAGE (D26), COMPILER ATTRIBUTION (D27), FAMILY CLUSTERING (D28),
  **OPTIMIZATION EQUIVALENCE (D29 "Two binaries, same source, different compiler moods ... prove they're semantically the same
  program"), CAMPAIGN GRAPH (D30 "Reconstruct the loader, library, and config graph across the whole set and map the operation
  end to end")**. D31 is the LAST day: expect a capstone "across the whole set" (D30's wording already says it) and/or backfill #4.
- Ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`; multi-member groups add `dNN_analysis_<tag>_<field>`. **The `<tag>` is NOT
  always the basename token**: D21-D28 tag = basename role (`family-a` -> `family_a`), but D29 `unoptimized_`/`optimized_` route to
  `-O0.elf`/`-O3.elf` and D30 `config_capsule_` routes to `-config.n` -- the QUESTION says "Use the unique dNN-- member whose
  basename ends O3.elf": route on that sentence first, tag second. Unqualified ids = consensus of the members the question names.
- From D2 every new member embeds the **HCFG** blob `'HCFG' | u8 ver | u8 xor_key | u16le len | u32le crc32(plain) | xor'd JSON
  @12`; only its STORAGE changes (Variant axes). **D30 changed the MAGIC: `HGRF` (same 12-byte layout) carrying a campaign-graph
  JSON with the config NESTED under `config`** -- scan for any `[A-Z]{4}` + this header that crc-validates, not only `HCFG`.
- The hard part is the GM's label for `exact_text` fields; **the organizers RE-ISSUE the contract** when a label is unguessable
  (D17 `hcfg_storage` -> enum). Since D24 EVERY question is a full SPEC (layout, scan direction, member choice, JSON path).
- **The contract LEAKS future days**: D19 "RS20 for Day 20", d07 "for Day 26 use the primary classfile", enum `neko_bytecode`
  (D19 -> shipped D30). All came true. After D30 no unseen token/day number remains -- re-grep the D31 contract anyway.
- **Theme asked on its own group only sometimes**: D19/D20 yes, D21-D25 no, D26 yes (JSON sidecar), D27 no, D28/D29/D30 ONLY via
  routing + consensus (no similarity, optimization or graph-edge id; D30 asked graph.config.* but not nodes/edges/load_order).
  14 ids per group since D28 (sha256 per member + `<role>_format`/`<role>_machine` + 4 consensus config_* + role config_*).
- **Every member embeds a `huntress.binary.dynamic_trace.v1` template** (unasked) whose `family` names the theme: D25
  `clojure_bounds_root_cause_trace`, D26 `groovy_synthetic_crash_trace`, D27 `v_cross_backend_attribution_trace`, D28
  `odin_family_cluster_trace`, D29 `freebasic_optimization_variant_trace`/`semantic_equivalence_only`; D30 puts the theme in the
  HGRF record itself (`schema huntress.binary.campaign_graph.v1`, `effects isolated_multi_process_event_graph_only`).
- Question count: 80 on D8, +10/day to 160, D17 204, +12/day to D27 324, D28 392 = 28 x 14 (backfill #3), **D29 406, D30 420
  (+14/day, no new backfill)**. Mastery = `setN.` copies, +1 set/day (D28 12, D29 13 = 5278 ids, D30 14 = 5880 ids). Timed:
  D28 TT 54 s; **D29 TT 3.0 s / M 5.7 s; D30 TT 3.1 s / M 6.1 s (all CORRECT first POST)**.
- **Bonus flag challenge (D30 "SHA1-Hulud", separate slug)**: ONE `flag` answer, per-team build, 3 wrong submissions max, a
  hardened Rust PE64 crackme (self-hashing `.text`, anti-debug, env fingerprint FED INTO THE KEYS, CBC-style two-pass cipher,
  OR-verdict with decoys). Organizers: Day-30 only. Method is in Pitfalls (`reference/D30_SHA1HULUD_LESSONS.md` = full write-up).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, storage per container: `.hcfg` section (D2/D10/D14), .NET FieldRVA (D3), Go/Rust
  rodata, base64 in a jar constant pool (Java/Kotlin; Scala `$` module, Clojure `<ns>__init` `encoded-config`, Groovy
  `encodedConfig`) / Swift/Nim/D/Crystal literal, RAW FPC `.data`, WASM data seg 0, Ada/Fortran `.rodata`, D19 packed overlay,
  D20 RS20 overlay, D21 plugin `.data`, D22 RAW twice (`.text` + PE overlay), D23 PE overlay, D27-D29 RAW appended at
  `e_shoff+e_shnum*e_shentsize` (file ends with the record; "Scan backward from the end ... first CRC32-valid"), **D30 HGRF RAW at
  the END of each Neko `.n` (tail 0 bytes, no ELF section table to compute image_end)**. Rule: scan for `HCFG`/`SENGR...` (jars:
  every class's constant pool) AND any record magic the question names, accept only crc32(plain) match AND parsing JSON, keep
  scanning past failures (D9 decoys); scan in the DIRECTION the question states. Storage never changed WITHIN a day.
- **Record magic / payload schema (D30)** -- `HGRF` = `HCFG` layout ("byte-4 version, byte-5 XOR key, little-endian length and
  CRC32 ... same 12-byte layout as HCFG"); JSON = `{schema, campaign_id, nodes[], edges["a->b"], load_order[], config{campaign,
  domain, ipv4, url, mutex, windows_path, linux_path, service, host_model}, this_role, network, effects}`. The question's path
  `graph.config.campaign` names the RECORD first: `graph` is NOT a JSON key -> drop a leading segment that is not a key and names
  the record (graph/record/root/<magic>), then walk the dots. Consensus: "confirm all three canonical campaign graphs match when
  this_role is omitted" = drop `this_role`, compare canonical JSON of all members, answer from the member named (loader.n).
- **Overlay layout per day (D19 PK19, D20 RS20)** -- appended at image end, magic `<2 caps><day>`, header spelled by the QUESTION:
  PK19 `magic|ver|k1|k2|pad|u32le packed_len @8|sha256 @12|packed @44`, unpack `ror8(b^k2,3)^k1`; RS20 `magic|ver|u32le
  resource_len @8|u16le scratch_len @12|sha256(scratch) @16|HCFG @48|scratch`. Rule: `rfind(magic)`, parse listed widths, verify.
- **Location / storage as answer** -- `hcfg_offset` = decimal FILE offset (base64 -> the `S`, RAW -> the `H`); `overlay_offset`
  = the magic, `overlay_size` = len - offset; `hcfg_resource_size` = u32le @+8. `hcfg_storage` enum in order: `base64` ->
  `raw_hcfg_section` -> `wasm_data_segment` -> `raw_const_array` -> `raw`.
- **Any other encoding -> `lib.binary.hcfg_scan(data)`** (hex/b32/b85/UTF-16/reversed/xor/zlib/rolling xor/custom b64/split/
  int-array/strided/RC4/AES/TEA/ChaCha/stack-built); `hcfg_find` = first valid hit.
- **Config VALUE SHAPES** -- crc, key and values re-roll per variant; timed modes change the SHAPE: campaign `BRNN-000` ->
  `BRNN-<8 HEX>` (D28 false friend `FF28-`), domain `variant-000.dayNN...` (D29) / `campaign-000.day30...` (D30) ->
  `<word>-<8hex>.dayNN.example.invalid`, mutex `Global\HuntressBRNN-000[_000]` -> `Global\Huntress<12 HEX>`, url `.../v/BR29-000`
  / `.../stage/BR30-000` -> `https://<word>-<8hex>.dayNN.example.invalid/<word>/<10hex>`; one word pool (sync/hub/core/mesh/relay/
  stage/edge/cache/vault/proxy/node/gate) drawn independently for domain, url host, url path. Extra keys appear without warning
  (D28 `host_model`/`ipv4`; D30 `windows_path`/`linux_path`/`service`). Rule: copy verbatim; never regex-check a shape.
- **Container per member** -- ELF vs PE32+ re-rolls per member in Mastery (d02, d04, d10); dispatch on MAGIC (`7f454c46`, `MZ`,
  `PK`, `\0asm`, `NEKO`). The format question spells the rule ("Classify final bytes by magic and parsed container ... neko_bytecode
  for NEKO bytecode"). ELF-worded ids still apply to a PE re-roll (D28 TT d10: `section_count` = NumberOfSections).
- **Member routing** -- (1) id tag = longest `[^a-z0-9]+` token naming exactly one member (multi-word: `family_a`, `false_friend`,
  `config_capsule`); (2) the question's "basename ends X" / "Use the dNN-- X member" wins when the tag is a SEMANTIC word that is
  not in any basename (D29 `optimized` -> `O3.elf`, `unoptimized` -> `O0.elf`, substring trap: `unoptimized` contains `optimized`;
  D30 `config_capsule` -> `config.n`); (3) the tag can precede the field family (`corrected_config_url`) and the field can itself
  start with `config` (`config_capsule_graph_config_campaign` = member `config.n`, field `graph.config.campaign`). `sha256_K` =
  ARCHIVE order, never sorted. Question-named routing runs AFTER the tag peel (D21 dropped 26 ids otherwise).
- **Unqualified id over a named subset (D24-D30)** -- "Decode both dNN-- role members and require their config objects to be
  byte-for-byte equal" (D24/D25/D27/D29), D28 "Decode family-a.elf and family-b.elf ... do not use false-friend.elf", D30 "Use
  loader.n's decoded HGRF graph.config object after confirming all three ... match when this_role is omitted": decode exactly the
  named members, normalise as told, assert equal, answer from the named one. The excluded look-alike has its OWN valid config.
- **Theme sidecar inside the member (D26)** -- jar entry `crash/trace.json` (`huntress.synthetic_crash.v1`, frames innermost-
  first); entry whose name ends `trace.json`, answer frames[0]; "every frame in the primary classfile method-name set" = inclusion.
- **Primary vs support members (D3, D22, D23)** -- primary assembly = the `.dll` that is not a framework/dependency (FSharp.Core,
  System.*, Microsoft.*); hash ALL members. Basenames: `dNN--variant-000.*` -> `dNN--sample.*` since D22.
- **Stripped carry-over d01** -- re-rolls stripped in some sets: symbols/disassembly `[]`, has_symtab `false`, recover_code `none`.
- **Mastery packaging** -- `setN.` ids (D30 14 sets), each its own delivery; each set's 1st question ends `Evidence case:
  dNN-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]` = set->delivery map. Per-member caches key on (delivery, member name)
  or sha256, never `id(bytes)` (D25: 5/9 sets cross-wired).
- **kind / field sets per group** -- `elf_class`/`machine` exact_text on d01 but INTEGER on d08/d15/d21+ (dispatch on
  `answer_format.kind`); old groups gain ids over days (D8, D17, D28): answer by field name from THAT member's facts dict.
- **Backfill #3 spec grammar (D28, 54 ids on d01-d27)** -- public substring predicates (Latin-1 [+UTF-16LE]), regex counts over
  NONEMPTY `.symtab` names (`.dynsym` only when no `.symtab`: d13 771 not 1255), sorted LF-join sha256 (UNIQUE names for
  `method_names_sha256`), colon-join of member digests, Jcc byte scans in `.text`, `cli_runtime` Major.Minor, `section_count`,
  PK19 keys, size ids w/o a named magic = the day's own overlay magic (d20 `overlay_size` = len - rfind(`RS20`)). Rule:
  implement the sentence literally (`lib.binary.generic_field`). No backfill #4 on D29/D30.
- **Speed flags (no answer change)** -- CPU contention: re-measure with `taskset -c 0,1 /usr/bin/time python3 solve.py`;
  floor = inflate + sha256 of every member (all asked); D30 single solve phase 1.3 s, 14-set Mastery 1.5 s.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "AES Encrypted" | `7z x -pinfected -y evidence.zip` (Python: `pyzipper`); `sha256sum *` for every `artifact_sha256_K` (archive order within the group) |
| `readelf -h -S` hint, ELF header questions | `readelf -hSW`, `readelf -sW`; `readelf -p .huntress` for the custom-section `marker` (D1, re-asked D17) |
| "constant returned by recover_code" / `disassembly` | `objdump -d -M intel --no-show-raw-insn` around `<recover_code>`; capstone on the FUNC symbol's bytes |
| Stripped C build, no `.symtab` | answer the absence the question defines (`[]`/`none`); recon only: leaf `b8 imm32 c3` (`lib.binary.recover_return_constants`) |
| C++ / "mangled" / "vtable" / "RTTI" | `nm -C` / `c++filt`; `_ZTV`/`_ZTI`/`_ZTS`; PE: `objdump -t file.exe` (COMDAT `.text$<mangled>`) |
| `PE32+` MinGW `.exe` | `objdump -t` (COFF symbols), `pefile` (Machine, OPTIONAL_HEADER.Magic, sections incl. `.hcfg`) |
| .NET (`BSJB`, `.runtimeconfig.json`; F# `FSharp.Core`, VB.NET `Microsoft.VisualBasic.Core`) | `ilspycmd` / `dnfile`; `pe_cli`/`i386`/`v4.0.30319`; PRIMARY dll only; raw `grep -abo HCFG` -> first crc-valid hit |
| P/Invoke / "bridge" (`DllImportAttribute`, ModuleRef) | dnfile `md.ModuleRef`, `md.ImplMap` rows; `ilspycmd` for `[DllImport]` signatures |
| Anti-analysis predicates (Debugger/Stopwatch/Environment TypeRefs, env `HUNTRESS_HOST_MODEL`) | NEVER run it: asked ids are header + HCFG (static); record the predicate list |
| Go / Rust | `go version -m f`, `lib.binary.go_buildinfo`/`go_pclntab_funcs`; Rust: header + `HCFG` scan, `rustfilt` |
| `.jar` (Java/Kotlin/Scala/Clojure/Groovy, `Created-By: Huntress deterministic <Lang> factory`) | unzip, Main-Class, `javap -v -p`; HCFG base64 `ldc` may be in Scala `Foo$`, Clojure `<ns>__init`, Groovy `encodedConfig`; `unzip -l` for NON-class sidecars |
| Crash artifact (`crash/trace.json`, `core`, `*.dmp`, hs_err, ASan) | `jq . trace.json` (frames innermost-first); native: `readelf -n core` -> RIP -> `addr2line -f -e bin`; capstone the faulting insn |
| Twin/role members (`-stripped`/`-symbolized`, `-loader`/`-plugin`, `-vulnerable`/`-corrected`, `-gcc`/`-tcc`, `-O0`/`-O3`) | route `<tag>_` ids (tag may be a semantic word: `optimized` = `-O3`); diff if asked: `javap -p -c` / `objdump -d` per symbol + `diff`, `rz-diff -t functions a b` |
| N look-alikes (`-family-a`/`-family-b`/`-false-friend`) | `cmp -l A B \| wc -l` per pair (D28 twins 1 byte, stranger ~2k), per-member HCFG (stranger `FF28-`); consensus = NAMED members only |
| V / Odin / FreeBASIC ELF (`main__main`+`builtin__*`; `/odin/base/runtime/*.odin`; fbc rtlib `dev_scrn_init.c`/`dev_scrn_write.c` FILE syms, `fb_*`) | plain ELF (`elf`/62); HCFG RAW at image_end (`grep -abo HCFG F`), "scan backward from the end" |
| **`NEKO` magic / `.n` members (D30: Haxe 4.3.7 build, strings `std/neko/*.hx`, globals `@classes`/`@Loader`/`@String`; header `NEKO` + u32le nglobals/nfields/codesize)** | format `neko_bytecode`; config record RAW at EOF: `grep -abo 'HGRF\|HCFG' F`, rfind + crc gate; JSON path from the question (`graph.config.X` -> obj["config"]["X"]); `nekoc`/`haxe` only for theme facts |
| Record magic you have not seen (`HGRF`, next ???) "uses the same 12-byte layout as HCFG" | generic 4-byte-magic record decoder: magic\|ver\|key\|u16 len\|u32 crc\|xor payload; scan direction + member from the question |
| Backfill "Evaluate this public predicate", "count names that match /re/", "sort ... SHA-256" | `lib.binary.generic_field(blob, suffix, question, member)`; `.symtab` only (`.dynsym` if none) |
| Same-source builds named by COMPILER or FLAGS, "name the toolchain", "account for every optimization" | header + consensus HCFG (asked D27/D29). Facts if asked: `readelf --debug-dump=info F \| grep -m2 producer`, `.comment`, gcc IPA suffixes, tcc `.stab`, PT_INTERP libc; O-level: function count/inlining, `.text` size |
| Swift ELF (`swift5_*`, 60+ MB) | never eager-parse symbols; regex `SENGR` base64 in `.rodata`; `bin/swift-demangle` |
| Nim / D / Crystal / FPC / ObjC / Ada / Fortran / COBOL / Haskell / OCaml ELF | plain ELF for header ids; base64 `SENGR` (offset = the `S`) or RAW (offset = the `H`); COBOL/Haskell config in PK19/RS20 overlay; OCaml HCFG in plugin `.data` |
| File size > `e_shoff + e_shnum*e_shentsize` | OVERLAY: `xxd -s <image_end> F`; magic `<2 caps><day>` or bare record; parse header fields the question lists, verify hash |
| `\0asm` | `lib.binary.wasm_layout` / `wasm-objdump -x`; `wasm`/`wasm32`; HCFG RAW in data segment 0 |
| `kind: enum` + rule list, or text describing bytes | the question IS the spec (D17, D19, D30): implement it literally, emit one listed token |
| **Single `flag` answer, "crackme", per-team build, 3 wrong max (D30 SHA1-Hulud)** | static strings/decoders first (answer-first), then EMULATE (Speakeasy / unicorn) with a PLAUSIBLE host, hook the final compare, differential probes; see Pitfalls |
| Packed / `UPX!` / real code reversing | `lib.binary.packer_info` -> `upx -d` on a COPY; `rizin -q -c "aaa; pdf @ sym.<fn>"`; Ghidra headless (last resort) |

## Day by day
**D1-D16** (one language/day): D1 C ELF headers/`.huntress`/recover_code (~14 min, 4 wrong); D2 C++ ELF/MinGW PE, first HCFG,
PE symbols = COMDAT `.text$<mangled>`; D3 .NET `pe_cli` after ~50 synonyms (~1 h 48 min); D4 Go `amd64` REJECTED -> `x86-64`;
D6 jar constant-pool base64; D8 Swift 67 MB + backfill #1 + integer elf_class/machine; D9 Nim raw decoys + `hcfg_offset`; D10
`has_hcfg_section`; D12 HCFG RAW; D14 ObjC `.hcfg`; D15 stripped/symbolized `<qualifier>_` ids; D16 wasm pair `wasm`/`wasm32`.
**D17 "Decoder Ring"**: Ada + backfill #2; `hcfg_storage` burned ~10.9k POSTs / 3.5 h until the contract revision (enum).
**D18-D23** (T+11 s .. T+2:25): Fortran; GnuCOBOL + `PK19` overlay (questions spelled the stub); Haskell + `RS20`
(`hcfg_resource_size`); OCaml loader + `.cmxs` (question-named routing AFTER the tag peel); F# + support DLL ("FIRST record that
validates"); VB.NET PE overlay (timed modes re-shaped values).
**D24-D27** (T+35..80 s, 0 wrong): Scala/Clojure twin jars (12-id twin template; D25 Mastery `id(bytes)` cache cross-wiring);
Groovy + `crash/trace.json` theme ASKED; V gcc/tcc twins, RAW HCFG at image_end, "scan backward from the end" (zero new code).
**D28 "Family Resemblance"** (392 Qs; T+3:23, 6 rejected POSTs): Odin trio, family consensus "do not use false-friend.elf";
BACKFILL #3 (54 spec-worded ids) sank 4 all-or-nothing batches on d20 `overlay_size` and d13 `crystal_symbol_count`.

**D29 "Fraternal Twins"** (406 Qs; **CORRECT T+1:20, 0 rejected**; TT 3.0 s / Mastery 13 sets 5.7 s, first POST).
- Artifact: FreeBASIC (fbc) ELF pair `d29--sample-O0.elf`, `-O3.elf` (43,931 B each, glibc dynamic, not stripped, `crtstuff.c` +
  fbc rtlib FILE symbols; the two differ in only 12 bytes despite the O-level names). HCFG RAW appended at EOF-387.
- 14 new ids: 2 sha256, `unoptimized_`/`optimized_` format + machine (integer 62), 4 consensus config_* ("Decode both d29-- role
  members and require ... byte-for-byte equal"), 4 `optimized_config_*`. Insight: the id tags are WORDS, the basenames carry `O0`/
  `O3`; the question's "basename ends O3.elf" routed them. Theme (optimization accounting / semantic equivalence) unasked; trace
  family `freebasic_optimization_variant_trace`. Carried-over solver banked 392, then 6 + 8 new ids.

**D30 "Campaign Trail"** (420 Qs; **CORRECT T+1:18**, 10 rejected = the race harness's `none` placeholder probes on the d30
config ids, 0 real wrong answers; TT 3.1 s / Mastery 14 sets (5880 ids) 6.1 s, first POST).
- Artifact: Haxe 4.3.7 -> Neko bytecode trio in archive order `d30--sample-loader.n`, `-library.n`, `-config.n` (= load order; 20.9 KB each,
  `NEKO` header identical, Haxe std paths `std/neko/*.hx` leak the organizer's build dir). Each ends with a RAW `HGRF` record
  (ver 1, xor key e.g. 0xf1, ~695 B JSON, 0 bytes after it): `huntress.binary.campaign_graph.v1` {campaign_id `DAY30-000`, nodes
  [loader.n, library.n, config.n], edges `loader.n->library.n`, `library.n->config.n`, load_order, config{...}, this_role
  loader/library/config, network none, effects `isolated_multi_process_event_graph_only`}; no HCFG in any member.
- 14 new ids: 3 sha256, `loader_`/`library_`/`config_capsule_` format (`neko_bytecode`, first try), 4 consensus config_* ("Use
  loader.n's decoded HGRF graph.config object after confirming all three canonical campaign graphs match when this_role is
  omitted"), 4 `config_capsule_graph_config_*` (config.n's own record).
- Key insight: read the record path literally but resolve `graph.` as the record name (JSON top level has `config`, no `graph`);
  normalise by deleting `this_role` before the 3-way equality. Tools: `xxd -l 16`, `grep -abo HGRF`, a 15-line rfind+crc+xor
  decoder; ~40 lines added to the cumulative solver (`graph_record`, `d30_graph`). Graph edges/load order NOT asked.
- **Bonus "SHA1-Hulud"** (flag crackme, see header): our 4 worker launches (~1 h 45 min, 0 wrong submits) did not get the flag;
  a reviewer's manual analysis solved it in ~5 min (CORRECT T+2:21 after release). Lost time: an emulator with "clean = not found"
  env stubs ran to completion SILENTLY on every input (env answers feed the keys -> poisoned target), read as "gate bailed";
  25 min modelling SHA-1 stub variants that only needed to execute; byte-at-a-time attack defeated by the backwards second pass.

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class | exact_text: `ELF64`/`ELF32`; `kind: integer` (D8+): `64`/`32` | ELFCLASS64; `2`/`1` |
| machine (`kind: integer`, role members D15-D30) | decimal e_machine (`62`), also ET_DYN `.cmxs`, every compiler/O-level | — |
| endianness | `little` / `big` | little endian, lsb, msb |
| machine (ELF exact_text) | `x86-64`, `x86`, `AArch64`, `ARM` (D19+ text: tool labels and codes also accepted) | EM_X86_64, x86_64, amd64 |
| machine (PE FILE_HEADER) | 0x14c -> `i386`; 0x8664 -> `x86-64` | x86 (PE i386); raw `0x8664` |
| architecture | the same machine words (Go amd64 -> `x86-64`) | amd64, arm64, 386, x86_64 |
| elf_type | `ET_EXEC` / `ET_DYN` | EXEC |
| entry_point, crc32_hex, xor_key_hex | lowercase hex with `0x` (crc `0x%08x`, key `0x%02x`) | — |
| recover_code (`kind: integer`) | base-10 integer (`mov eax, 0x1fa4` -> 8100); `none` if the symbol is absent | the stripped leaf's constant |
| has_* | enum `true`/`false` | — |
| marker | exact `.huntress` string without the NUL; `none` if missing | — |
| format (enum) | `elf`, `pe`, `pe_cli`, `jar`, `wasm`, **`neko_bytecode` (D30 Haxe->Neko `.n`, CONFIRMED)** | ELF, ELF64, exe, pe32+, jar_jvm, ~50 .NET synonyms |
| format / arch per container | compiled ELF any language/compiler/O-level `elf`/`x86-64`; WASM `wasm`/`wasm32`; .NET any language `pe_cli`/`i386`; any JVM jar `jar`; Neko `neko_bytecode` | x86 for PE i386 |
| C++ symbols ELF / PE | bare Itanium mangled name / COMDAT section name `.text$<mangled>` | demangled; bare on PE |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` | list without "" (pre-D17) |
| symbols / disassembly (JSON) | non-empty .symtab names, table order, dupes kept / capstone intel `"mov eax, 8100"`, `"ret"` | hex imm, `"ret "` |
| methods / access_flags / method_count (jar) | Main-Class method_info names incl. `<init>` / decimal `49` / count incl. synthetics (d26 = 10) | — |
| crash_fault_method / crash_frames_match_methods | trace.json `frames[0]` verbatim / set inclusion `true`/`false` | — |
| metadata_version | BSJB root string `v4.0.30319` | net8.0 / TFM |
| config_* (HCFG) | verbatim from decoded JSON (mutex ONE backslash); consensus of the NAMED members; D19 from the unpacked overlay | JSON-escaped `\\`; `none` when merely hidden |
| config_* (HGRF, D30) | `graph.config.<key>` = decoded record JSON `["config"][key]` verbatim; unqualified = loader.n after this_role-less 3-way match; `config_capsule_graph_config_*` = config.n's own record | `none` placeholders (10 rejected) |
| hcfg_version / xor_key_hex / hcfg_offset | header byte 4 decimal / byte 5 `0x%02x` / decimal FILE offset (`S` base64, `H` raw) | — |
| overlay_offset / overlay_size / hcfg_resource_size | last occurrence of the day's magic / len - that offset / RS20 u32le @+8 | non-day magic (19) |
| hcfg_storage (enum, D17) | `base64`, `raw_hcfg_section`, `raw_const_array`, `wasm_data_segment`, `raw` | every free-text spelling (~10.9k probes) |
| compression_methods (jar, json) | sorted distinct ZIP method ids `[0,8]` | — |
| backfill #3 counts / hashes / header text (D28) | `.symtab` nonempty names (`.dynsym` only if none); `section_count` = e_shnum incl. 0 (PE: NumberOfSections); sorted LF-join sha256; colon-join of member digests; `cli_runtime` `2.5`; `packing_key_1/2_hex` `0x%02x` | d13 count with `.dynsym` (1255) |
| flag (bonus crackme, D30) | the accepted INPUT itself, `flag{<32 hex>}` (program prints "correct, the flag is " + input) | decoys that also print correct (`your flag is in another castle`, short `flag{nic...`) -- never submitted |
Naming law: native format = container only; managed .NET = `pe_cli`; Java broke it (`jar`); VM bytecode = `<vm>_bytecode`.

## Pitfalls that cost time
- **A synthetic label with no derivable spelling** (D3 ~1.5 h; D17 `hcfg_storage` ~10.9k POSTs): stop after ~10 single-id probes
  plus one `hctf labels` run, write HELP.md, RE-PULL THE CONTRACT periodically and diff each id. Never mass-probe exact_text.
- **Reversing what the question already specifies** (D19): read the longest question of each new family FIRST; size fields =
  the exact header field the layout names. D30: the HGRF layout, scan direction and normalisation were all in the question.
- **Absence vs hidden**: `none`/`[]`/`false` only when ABSENT (stripped d01), wrong when merely HIDDEN (D19 packed config; D30
  race-harness `none` placeholders for the HGRF config ids -> 10 rejected probes, harmless but useless: a new record magic means
  "decode it", not "absent").
- **A multi-field POST is all-or-nothing** (D2, D28): POST carried-over ids first (they bank), then each NEW field family alone
  or bisect on the first rejection; a heuristic answer to a new spec is a guess until accepted.
- **Routing**: peel the longest multi-word member tag, but when the tag is a semantic word (`optimized`, `config_capsule`) map it
  through the question's "basename ends X"; mind substring tags (`unoptimized` ⊃ `optimized`); a field that starts with `config`
  after a role tag (`config_capsule_graph_config_url`) is still a role field. Read `answer_format.kind` per id.
- **JSON paths in questions** (D30 `graph.config.campaign`): the first segment may name the RECORD, not a key -- resolve against
  the decoded object, dropping a non-key leading segment; never answer `none` because `obj["graph"]` is missing.
- **"The theme is never asked" is NOT a rule** (D26): list every member's NON-code entries (`unzip -l`, sections, resources,
  overlays, tail records) and parse any JSON sidecar up front. Unasked D27-D30 beyond routing; record theme facts in NOTES.md.
- **Per-member caches keyed on `id(bytes)`** (D25 Mastery, 55 wrong ids): key on (delivery, member name) / sha256. Symptom: a
  rejected value that is VALID for another group of the same delivery.
- **Archives**: never unzip recursively; jar members are deflated (`grep HCFG file.jar` finds nothing) -- inflate every entry.
  Huge members (D8 67 MB): cheap encodings first, crc-gate every hit.
- **Decoy magics** (D9): code that checks the magic embeds `"HCFG"` literals; len 0 => crc32(b"")==0 passes. Require non-empty
  JSON; scan DIRECTION per question (D22 first-from-start, D27-D30 backward from EOF); offsets from `re.finditer().start()`.
- **ELF-worded id on a PE re-roll** (D28 TT d10): every ELF header/section/symbol field needs a PE mapping.
- **Crackme with no oracle (D30 SHA1-Hulud)**: (1) SILENCE on every input under emulation = environment answers feed the keys,
  not "my input is wrong": make every fingerprint report a PLAUSIBLE real host (4+ CPUs, 8 GB, 1920x1080, no hypervisor bit
  CPUID 0x40000000, no tool processes/drivers/registry markers, coherent RDTSC/QPC/KUSER clocks, sane LastError) -- a "not found"
  stub is a value; (2) MEASURE before reversing: run two different probes, diff every operand stream at the final compare
  (inputs-invariant streams = stored target/masks), then ask which keys depend on input; (3) chained-block ciphers (key_j from
  plaintext block j-1): decode block 0 from any probe, extend the probe progressively (8 -> 24 -> 38 chars; probe length must
  equal the target's length word); (4) OR-verdicts carry decoys: enumerate every accepted group, submit only the `flag{32hex}`
  one; (5) self-hashing `.text`: never byte-patch, hook in the emulator or shadow `.text`; (6) don't re-implement a hash you
  only need to execute; skip deliberate slow loops instead. Speakeasy (Windows PE emulator with API/PEB/TEB stubs) saves the
  scaffolding; never run the sample natively.
- **Timed windows**: download dominates (D16 TT 52 s of 64 s). WASM sizes = 5-byte PADDED LEB128; PE machine map must include
  0x8664 -> `x86-64`.
