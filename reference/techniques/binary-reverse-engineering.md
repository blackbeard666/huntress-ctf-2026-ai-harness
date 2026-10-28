# binary-reverse-engineering — technique log (days 1-28; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
- One `evidence.zip` (AES, password `infected`), CUMULATIVE from D3: one group per past day (`dNN--sample.<ext>`, `variant-000`
  before D22) + ONE new container/language per day: D1 C ELF, D2 C++ (ELF/MinGW PE32+), D3 .NET, D4 Go, D5 Rust, D6 Java jar,
  D7 Kotlin jar, D8 Swift (67 MB), D9 Nim, D10 Zig, D11 D, D12 FPC, D13 Crystal, D14 ObjC, D15 C `-stripped`/`-symbolized`, D16
  WASM `-compact`/`-direct`, D17 Ada, D18 Fortran, D19 GnuCOBOL + `PK19` overlay, D20 Haskell + `RS20` overlay, D21 OCaml
  `-loader.elf` + `-plugin.cmxs`, D22 F# (+ `FSharp.Core.dll`), D23 VB.NET, D24 Scala jar PAIR `-vulnerable`/`-corrected`, D25
  Clojure jar PAIR, D26 Groovy jar (+ `crash/trace.json` entry), D27 V-language ELF PAIR `-gcc.elf`/`-tcc.elf` (one V source,
  two C backends, both musl-dynamic x86-64), **D28 Odin ELF TRIO `-family-a.elf`/`-family-b.elf`/`-false-friend.elf` (22 KB
  glibc PIEs, stripped, same size and layout; a/b differ in ONE byte, the false friend in ~2k bytes + its own config)**.
  Since D18 each day = a THEME on a new language: call graph (D18), packing (D19), resources/overlays (D20), shared libraries
  (D21), managed<->native bridge (D22), anti-analysis (D23), PATCH DIFFING (D24), BOUNDS-ERROR ROOT CAUSE + reachability (D25),
  CRASH TRIAGE (D26), COMPILER ATTRIBUTION (D27 "name the toolchain"), **FAMILY CLUSTERING (D28 "These binaries might be related
  -- or they might just look alike. Cluster them by behavior, watch out for false friends, and sort the family from the
  strangers")**. D24-D26 = vuln arc (3 days); D27-D28 = ATTRIBUTION arc (toolchain -> family). 3 days left: expect the arc's
  3rd step (variant/lineage ordering, shared-code/similarity measures, YARA-style family signature) or a capstone/backfill on
  D31. Language track: D27 V and D28 Odin = niche native languages (both predicted by the atlas). Left: Hare, Vala/Genie, C3,
  Cython, hxcpp, Haxe->Neko (`neko_bytecode` still in the enum, unseen), Elixir/BEAM, niche JVM.
  Ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`; multi-member groups add `dNN_analysis_<tag>_<field>` (D15/D16/D21/D24/
  D25/D27/D28; hyphenated roles become underscores: `family-a.elf` -> `d28_analysis_family_a_machine`, `false_friend_*`) and
  unqualified ids whose QUESTION names the member (D21) or demands consensus of the NAMED subset (D24/D25/D27 both twins; D28
  "Decode family-a.elf and family-b.elf ... do not use false-friend.elf").
- From D2 every new member embeds the **HCFG** blob `'HCFG' | u8 ver | u8 xor_key | u16le len | u32le crc32(plain) | xor'd JSON
  @12`; only its STORAGE changes (see Variant axes). Scan raw bytes for `HCFG` AND base64 `SENGR...`, crc-gate every hit; when
  both miss, look past the image end (overlay) and read the question. Parse the whole JSON dict (never-asked keys exist).
- The hard part is the GM's label for `exact_text` fields; **the organizers RE-ISSUE the contract** when a label is unguessable
  (D17 `hcfg_storage` -> enum + ordered rules). Since D24 EVERY question is a full SPEC (sha256 "ZIP central-directory order ...
  member K (1-based)", format rule list, HCFG layout + carrier rule, JAR "Base64-alphabet UTF-8 constants >= 80 characters ...
  first CRC32-valid", D26 "Parse crash/trace.json ... first string in its frames array", D27 "Scan backward from the end").
- **The contract LEAKS future days**: D19 "RS20 for Day 20", d07 "for Day 26 use the primary classfile named by that unit" (both
  came true). Open after D28: enum `neko_bytecode` (D22-D28 added no new token/day). Grep each contract for `[A-Z]{2}\d\d`, `Day NN`, unseen enum values.
- **Theme asked on its own group only sometimes**: D19/D20 yes (overlay fields), D21-D25 NO, D26 YES (`crash_fault_method`,
  `crash_frames_match_methods`, from a JSON SIDECAR inside the member), D27 NO (compiler fingerprints unasked), **D28 ONLY via
  routing** (family consensus config_* + `false_friend_config_campaign`; no similarity/cluster field). 14 ids = 3 sha256 +
  `<role>_format`/`<role>_machine` x3 + 4 family-consensus config_* + 1 false_friend config.
- **Every member embeds a `huntress.binary.dynamic_trace.v1` template** (unasked) {branch, event_count, campaign, family
  `<lang>_<theme>_trace`, effects, network none} gated on env `HUNTRESS_HOST_MODEL` (+ `HUNTRESS_TRIGGER_FAULT` D25-D26); family
  NAMES THE THEME: D25 `clojure_bounds_root_cause_trace`, D26 `groovy_synthetic_crash_trace` (+ `huntress.synthetic_crash.v1`
  sidecar), D27 `v_cross_backend_attribution_trace`/`equivalent_behavior_only`, D28 `odin_family_cluster_trace`/
  `behavior_cluster_only` + `cluster_marker_positive` (4 records per member; the false friend's event_counts differ) -- grep
  `_trace"` to read the day's theme.
- Question count: 80 on D8, +10/day to 160, D17 204 (backfill #2), +12/day to D27 324, **D28 392 = 28 groups x 14 (BACKFILL #3:
  54 new ids pad EVERY old group to 14, all spelled as specs -- public predicates, regex counts, sorted-join sha256)**. Mastery =
  `setN.` copies, +1 set/day (**D28 12 sets = 4704 ids, ~17 MB per delivery**). Timed: D26 TT 5.3 s / M 8.2 s; D27 TT 5.4 s /
  M 14.5 s; **D28 TT 54 s (live worker: d10 re-rolled to PE) / Mastery CORRECT first POST (solve 2.4 s, submit 4.9 s)**.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, storage per container: `.hcfg` section (D2/D10/D14), .NET FieldRVA (D3), Go/Rust
  rodata, base64 in a jar constant pool (Java/Kotlin, D24 Scala `$` module, D25 Clojure `<ns>__init.class` `encoded-config` Var,
  D26 Groovy `static final String encodedConfig` in the Main-Class) / Swift/Nim/D/Crystal literal, RAW FPC `.data`, WASM data seg 0, Ada/Fortran `.rodata`, D19 packed overlay, D20 RS20 overlay,
  D21 OCaml plugin `.data`, D22 F# RAW twice (`.text` + PE overlay: "FIRST record that validates"), D23 VB.NET RAW PE overlay,
  D27 V gcc+tcc RAW appended EXACTLY at `e_shoff+e_shnum*e_shentsize` with NO day magic (the file ends with the record) and the
  question rule reversed: "Scan backward from the end of the member for literal HCFG magic and accept the first CRC32-valid".
  Rule: scan for `HCFG` and `SENGR[A-Za-z0-9+/_-]*=*` (jars: every class's constant pool), accept only crc32(plain) match AND
  parsing JSON, keep scanning past failures (D9 Nim decoys); scan in the DIRECTION the question states (D22 first-from-start,
  D27 `rfind` loop from EOF); never a fixed offset or a fixed class. Storage never changed WITHIN a day (single/TT/all Mastery sets).
- **Overlay layout per day (D19 PK19, D20 RS20)** -- appended at `e_shoff + e_shnum*e_shentsize`, magic `<2 caps><day>`, header
  spelled by the QUESTION: PK19 `magic|ver|k1|k2|pad|u32le packed_len @8|sha256(unpacked) @12|packed @44`, unpack `ror8(b^k2,3)^k1`;
  RS20 `magic|ver @4|u32le resource_len @8|u16le scratch_len @12|sha256(scratch) @16|HCFG @48 raw|scratch`. Rule: `o =
  data.rfind(magic)` ("final"), parse the listed widths, verify bounds + hash; unspecified transform -> known-plaintext `HCFG`.
- **Location / storage as answer** -- `hcfg_offset` = decimal FILE offset (base64 -> the `S`, RAW -> the `H`); `overlay_offset` =
  the magic, `overlay_size` = len - offset; `hcfg_resource_size` = the u32le @+8 (380). `hcfg_storage` (D17 enum) in order:
  `base64` -> `raw_hcfg_section` -> `wasm_data_segment` -> `raw_const_array` (other native data section) -> `raw`.
- **Any other encoding -> `lib.binary.hcfg_scan(data)`** (hex/base32/85/UTF-16/reversed/xor/zlib/multibyte+rolling xor/byte maps/
  custom b64/split/int-array/strided/RC4/AES/TEA/ChaCha/stack-built); `hcfg_find` = first valid hit. Not the PK19 stub.
- **xor key / config VALUE SHAPES** -- crc, key byte and campaign/domain/mutex/url re-roll per variant. Timed modes change the
  SHAPE too: D23 campaign `BRNN-00V` -> `BRNN-<8 uppercase hex>`, d01 marker `BR01-CATALOG-00V` -> `BR01-<8hex>`, d01 FILE symbol
  `variant-000.c` -> `sample.c`; D24 also domain `node-00V.dayNN...` -> `<word>-<8hex>.dayNN.example.invalid` (word: sync/hub/
  core/mesh/relay/stage, D25-D26 also edge/cache/vault/proxy/node), mutex `Global\HuntressBRNN_00V` -> `Global\Huntress<12 uppercase
  hex>`, url `.../api/BRNN-00V` -> `https://<word>-<8hex>.dayNN.example.invalid/<word>/<10hex>`; D27 shows ONE word pool for
  domain, url host and url path (sync/hub/core/mesh/relay/stage/edge/cache/vault/proxy/node/gate), each drawn independently.
  D28 false friend: campaign prefix `FF28-` (`FF28-000` single, `FF28-<8HEX>` timed) vs the family's `BR28-`; new keys
  `host_model` (`workstation`) and `ipv4` (TEST-NET dotted quad) are asked too.
  Rule: copy values verbatim from the decoded JSON/symtab; never regex-check a value shape or key on `00V` indices.
- **Container per member** -- ELF vs PE32+ re-rolls per member in Mastery (d02, d04, d10 `pe`); labels from THIS member's header;
  dispatch on MAGIC (`7f454c46`, `MZ`, `PK`, `\0asm`, next `NEKO`). PE symbol fields = COMDAT `.text$<mangled>`. Extensions lie
  about role, not container (D21 `.cmxs` = ELF ET_DYN). **ELF-worded backfill ids still apply to a PE re-roll** (D28 TT d10 `.exe`:
  "Read ELF e_shnum ... including index 0" -> GM took FILE_HEADER.NumberOfSections, 9, no +1): map each ELF field to its PE twin.
- **Member qualifier in the id (D15/D16/D21/D24)** -- peel the longest field prefix that is a `[^a-z0-9]+` token of exactly one
  member name (`stripped`/`symbolized`, `compact`/`direct`, `loader`/`plugin`, `vulnerable`/`corrected` D24+D25, `gcc`/`tcc` D27,
  `family_a`/`family_b`/`false_friend` D28 = basename `-`->`_`, MULTI-WORD; roles can be compiler names, so never hard-code the
  vocabulary; `family` alone names TWO members -> take the longest token naming exactly one); the token can sit
  BEFORE the field family (D24 `d24_analysis_corrected_format`, `..._corrected_config_url`). `sha256_K` = ARCHIVE order, never
  sorted (D24: vulnerable is member 1).
- **Member named in the QUESTION (D21)** -- after the qualifier peel, if >1 member remains, keep the one whose basename ends with
  the token after `basename ends` / `Use the dNN--`. ORDER MATTERS (running it first dropped 26 ids on D21).
- **Unqualified id over a twin pair / named subset (D24, D25, D27; D28)** -- "Decode both dNN-- role members and require their
  config objects to be byte-for-byte equal before using the common value"; D28 "Decode family-a.elf and family-b.elf ...
  common FAMILY value; do not use false-friend.elf": decode the members the question NAMES, drop the excluded one, assert equal
  JSON, answer the common value. The excluded look-alike carries a DIFFERENT valid config (campaign `FF28-...` vs `BR28-...`), so
  "first member" or "all members agree" logic is wrong here -- parse the include/exclude names from the question.
- **Theme sidecar inside the member (D26)** -- jar entry `crash/trace.json` (`huntress.synthetic_crash.v1`, `kind`, `frames`
  innermost-first), IDENTICAL in all 12 deliveries while config re-rolled. Rule: entry whose name ends `trace.json` (never a
  fixed path), answer frames[0] verbatim; "every frame in the primary classfile method-name set" = set inclusion; missing =
  `none`/`false`. Primary classfile (d07 and d26) = the manifest Main-Class, never a `$_main_closure1`; method_count = ALL
  method_info rows incl. Groovy synthetics (10). Inner class names keep `Variant000` although basenames say `sample`.
- **Member basename vocabulary (D22)** -- `dNN--variant-000.*` -> `dNN--sample.*`; group by `dNN--` + extension/role tag only.
- **Primary vs support members (D3, D22, D23)** -- primary assembly + `.runtimeconfig.json` (+ D22 `FSharp.Core.dll`); question:
  "primary managed assembly ... runtimeconfig and dependency DLL members are delivery support only". Primary = the `.dll` whose
  name is not a framework/dependency (FSharp.Core, System.*, Microsoft.*), i.e. the one carrying HCFG; hash ALL members.
- **Stripped carry-over d01** -- re-rolls stripped in some sets (D15-D17 Mastery, D17/D19 TT, D23 Mastery set6): symbols/
  disassembly `[]`, has_symtab `false`, recover_code `none` (GM-confirmed; leaf-heuristic constants rejected). Pair by sha256.
- **Mastery packaging** -- `setN.` ids (2-12 sets; D27 11 x ~36 MB, D28 12 x ~17 MB), each its own delivery; each set's 1st question ends `Evidence
  case: dNN-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]` (TT `dNN-tt-...`) = set->delivery map. Per-member caches key on
  (delivery, member name) or sha256, never `id(bytes)` (D25: 5/9 sets cross-wired, see Pitfalls).
- **kind / field sets per group** -- `elf_class`/`machine` exact_text on d01 but INTEGER (`64`/`62`) on d08/d15/d21 (dispatch on
  `answer_format.kind`, which can change between fetches, D17); `has_<x>` = a structural marker of <x> in THIS member; old groups
  gain ids over days (D8, D17, D28): answer by field name from THAT member's facts dict.
- **Backfill #3 spec grammar (D28, 54 ids on d01-d27)** -- every new old-group id spells its rule: "Evaluate this public predicate
  ... true exactly when the final bytes [as Latin-1 or UTF-16LE] contain X [or any nonempty ELF symbol name contains Y]"
  (`has_nim/fpc/gnat_runtime`, `has_decoy_branch`); "From ELF symbol-table entries with nonempty resolved names, count names that
  match /re/" (`d_symbol_count`, `crystal_symbol_count`, `handler_symbol_count`, `symbol_count`); "sort ... join with one LF ...
  SHA-256" (`handler_symbols_sha256`, `method_names_sha256` over UNIQUE names); "join digests with ':' ... SHA-256"
  (`structural_ordered_set_sha256`); byte scans (`conditional_branch_opcode_count`: 0x70-0x7f and 0f 80-8f in `.text`, one
  left-to-right pass); header reads (`cli_runtime` = CLI header Major.Minor, `section_count`, PK19 `packing_key_1/2_hex`); new
  config keys (`host_model`, `ipv4`); role-member config ids for the twin NOT asked before (`vulnerable_`, `symbolized_`,
  `direct_`, `plugin_`, `gcc_`). Rule: implement the sentence literally (`lib.binary.generic_field` covers all of them); "ELF
  symbol-table entries" = `.symtab` only (dupes kept), `.dynsym` ONLY when there is no `.symtab` (d13: 771 accepted, 1255 with
  .dynsym rejected); a size id whose question names no magic = the day's own overlay magic (d20 `overlay_size` = len -
  rfind(`RS20`) = 463; a generic `<2 caps><2 digits>` match gave 19, rejected).
- **Speed flags (no answer change)** -- CPU contention: re-measure with `taskset -c 0,1 /usr/bin/time python3 solve.py`; D25 TT
  solve phase 8.0 s at 300 ids under load, D26 3.2 s (TT) / 3.9 s (10-set Mastery); isolated single ~0.6-1.2 s.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "AES Encrypted" | `7z x -pinfected -y evidence.zip` (Python: `pyzipper`); `sha256sum *` for every `artifact_sha256_K` (K = archive order within the group) |
| `readelf -h -S` hint, ELF header questions | `readelf -hSW`, `readelf -sW`; `readelf -p .huntress` for the custom-section `marker` (D1, re-asked D17) |
| "constant returned by recover_code" / `disassembly` | `objdump -d -M intel --no-show-raw-insn` around `<recover_code>`; capstone on the FUNC symbol's st_value..st_size bytes |
| Stripped C build, no `.symtab` | answer the absence the question defines (`[]`/`none`); only as recon find the leaf `b8 imm32 c3` (`lib.binary.recover_return_constants`) |
| C++ / "mangled" / "vtable" / "RTTI" | `nm -C` / `c++filt`; `_ZTV`/`_ZTI`/`_ZTS`; `score` method `_ZNK<len><Class>5scoreEPKc`; PE: `objdump -t file.exe` (COMDAT names) |
| `PE32+` MinGW `.exe` | `objdump -t` (COFF symbols + string table), `pefile` (Machine, OPTIONAL_HEADER.Magic, sections incl. `.hcfg`) |
| "CLI metadata", `.dll` + `runtimeconfig.json`, `BSJB` | `ilspycmd file.dll` or Python `dnfile`; config = `<PrivateImplementationDetails>` FieldRVA static array; `BSJB v4.0.30319` |
| F# (AssemblyRef `FSharp.Core`, `FSharpSignatureData.*` resources, `$Program`, closures `name@<line>`) + big `FSharp.Core.dll` member / VB.NET (AssemblyRef `Microsoft.VisualBasic.Core`, `StandardModuleAttribute`, `VB$AnonymousType_<n>`, `Operators::CompareString`) | Same as C#: `pe_cli` / `i386` (AnyCPU ILONLY 0x14c) / `v4.0.30319`; answer from the PRIMARY dll only; raw `grep -abo HCFG` -> first crc-valid hit (D22 `.text` + overlay copy; D23 PE overlay only) |
| P/Invoke / "bridge" / "crossing" (`DllImportAttribute`, ModuleRef `libc`/`kernel32.dll`, `System.Runtime.InteropServices`) | dnfile: `md.ModuleRef` names, `md.ImplMap` rows (ImportName, ImportScope -> ModuleRef, MemberForwarded -> MethodDef, MappingFlags callconv/charset/SetLastError); `ilspycmd` shows the `[DllImport]` signatures (D22: `getpid`@libc, `GetCurrentProcessId`@kernel32.dll, Winapi) |
| Anti-analysis predicates ("checks the clock, sniffs the environment", TypeRefs `System.Diagnostics.Debugger` (`get_IsAttached`), `Stopwatch` (`StartNew`/`get_ElapsedTicks`), `Environment` (`get_ProcessorCount`, `GetEnvironmentVariable`), env `HUNTRESS_HOST_MODEL` = workstation/analysis/sandbox, branch words success/decoy/failure) | NEVER run it: the asked ids are header + HCFG (static). Record the predicate list for a backfill: dnfile TypeRef/MemberRef names + `ilspycmd` for the compare constants; native analogues = `ptrace`, `TracerPid`, `rdtsc`/`clock_gettime`, `cpuid`, `IsDebuggerPresent` |
| Go ("build info, function names") / Rust (`_R`/`_ZN..17h<hash>E`, panic strings) | `go version -m f`, `lib.binary.go_buildinfo`/`go_pclntab_funcs` (names survive stripping); Rust: header + `HCFG` scan, `rustfilt` if symbols are asked |
| `.jar` / "constant pool" / methods / access flags (Kotlin fat jar: skip `kotlin/`/`org/jetbrains/`) | unzip, `META-INF/MANIFEST.MF` Main-Class, `javap -v -p Main.class` (method table order, `flags: (0x0031)`); base64 config in a `ConstantValue`/`ldc` String |
| Scala jar (D24: `Foo.class` static forwarder + `Foo$.class` module with `MODULE$`, `Lscala/reflect/ScalaSignature;`/`ScalaSig` attr, `scala/Predef$`/`StringOps$`/`Option$` refs, manifest `Created-By: Huntress deterministic Scala factory`; scala-library NOT bundled) | format `jar`; the logic + HCFG base64 `ldc` live in `Foo$.class` (the `$` module), not the Main-Class forwarder; `javap -p -c -constants 'Foo$.class'` |
| Clojure jar (D25: manifest `Created-By: Huntress deterministic Clojure factory`, `Main-Class: day25.<role>000`, classes `<ns>__init.class` (Vars + constants), `<ns>$<fn>.class` per defn extending `clojure.lang.AFunction` (`invokeStatic`), `<ns>$_main` (RestFn), gensym classes `fn__269`, `loading__6812__auto____267`; `RT.var`/`RT.nth`/`Util.equiv`; clojure.jar NOT bundled) | format `jar`; HCFG base64 is the `encoded-config` Var's `ldc` in `<ns>__init.class` (not the Main-Class stub); `javap -p -c -constants '<ns>$<fn>.class'` per function; Clojure names munge `-`->`_` (`parse-frame` -> `parse_frame`), gensym numbers are build-specific -- match twins by Var name |
| Groovy jar (D26: manifest `Created-By: Huntress deterministic Groovy factory`, class `implements groovy.lang.GroovyObject`, `$getStaticMetaClass`/`metaClass`/`$staticClassInfo`/`__$stMC`, `$getLookup` (Groovy 4 indy), closures `<Main>$_main_closure1 extends groovy.lang.Closure` (`doCall`), `ScriptBytecodeAdapter.compareEqual`, `Compiled from "X.groovy"`; groovy jar NOT bundled) | format `jar`; primary = the Main-Class (not the closure); HCFG base64 = `private static final String encodedConfig` (`getEncodedConfig` getter) -- the generic constant-pool b64 rule finds it; `javap -p -v` for method_info names/count |
| Crash artifact ("it crashed", "dump", "unwind the stack", "faulting instruction"): a `crash/trace.json` / `*.dmp` / `core` / `hs_err_pid*.log` / ASan text next to or INSIDE the member | `unzip -l` the jar (non-class entries!), `jq . trace.json` (schema `huntress.synthetic_crash.v1`: `kind` = exception class, `frames` innermost-first); cross-check frames against `javap -p` method names and the static call chain (`javap -c`: stageOne->stageTwo->stageThree `invokestatic`, `new IllegalStateException`+`athrow` in frame 0). Native: `readelf -n core` (NT_PRSTATUS signal/RIP), map RIP -> symbol (`addr2line -f -e bin`), capstone the faulting insn |
| Two members differing by a name tag (D15/D16 builds, D21 loader+plugin: a role member may carry no HCFG; unqualified ids -> the member the QUESTION names) or `-vulnerable` / `-corrected` twins (D24/D25; patched/unpatched, old/new, v1/v2) -- "diff the vulnerable function against its corrected twin", "prove the bounds error is real, trace its reachability" | Route `<role>_` ids by the name token; answer header+HCFG per member; for the (unasked so far) diff: `javap -p -c` per class of both jars and `diff` after stripping the role token from class names -- D24 Scala `score(String)I`, D25 Clojure `parse_frame` (unguarded `RT.nth(v,4)` vs `(< 4 (count v))` guard -> -1); reachability = the env compares in `-main`; native twins: `objdump -d` per symbol + `diff`, `rz-diff -t functions a b` |
| V language ELF (D27: `main__main`, `_vinit`/`_vcleanup`, `builtin__*`/`strconv__*`/`Array_string_*`, `_const_<mod>__<name>` data symbols, `V panic: `, bundled Boehm `GC_*` + `GC_TRACE`, `builtin__print_backtrace*`) | C-backend language: plain ELF (`elf`/62) for header ids; HCFG RAW appended at image_end (`grep -abo HCFG F` = EOF-379); a gcc `-flto -Os` build keeps ~200 syms (main__main inlined away), the tcc build ~1900 |
| Odin ELF (D28: strings `/odin/base/runtime/*.odin`, `base/runtime: getrandom failed`; glibc PIE, NEEDED libm/libc/ld-linux-x86-64, STRIPPED (~20 `.dynsym` entries, no `.symtab`), ~22 KB) | Plain ELF (`elf`/62) for header ids; HCFG RAW appended exactly at image_end (`e_shoff+e_shnum*64`, `grep -abo HCFG F`), same "scan backward from the end" rule as D27 |
| N look-alike members (`-family-a`/`-family-b`/`-false-friend`, same size + section table) or "cluster by behavior", "false friends", "family vs strangers" | Per pair `cmp -l A B \| wc -l` (D28: a vs b = 1 byte, the role string `huntress-role-<role>`; false friend ~2k bytes from `.text` on), sha256 of `.text`/`.rodata` per member, HCFG per member (the false friend has its OWN valid config, campaign `FF28-` vs `BR28-`), trace records (`branch`/`event_count`). Route ids by role; family consensus = the NAMED members only |
| Backfill question "Evaluate this public predicate ...", "count names that match /re/", "sort ..., join with one LF ..., SHA-256", "join those digests with ASCII colon" | The sentence is the spec: `lib.binary.generic_field(blob, suffix, question, member)`; ELF symbol names = `.symtab` (`.dynsym` only if no `.symtab`); "final bytes contain" = Latin-1 (+ UTF-16LE when stated) substring |
| Same-source builds named by their COMPILER (`-gcc.elf`/`-tcc.elf`; next clang / zig cc / msvc / mingw) or "name the toolchain", "runtime and linker fingerprints" | Header + consensus HCFG per member as usual (D27 asked nothing else). Attribution facts if asked: `readelf --debug-dump=info F \| grep -m2 producer` (gcc: `GNU C99 12.2.1 20220924 ... -Os -std=c99`, `GNU AS 2.40`); `.comment` was ABSENT on both; gcc = DWARF 5 (`.debug_line_str`/`.debug_loclists`), IPA suffixes `.lto_priv.N`/`.constprop.N`/`.isra.N`, FILE `crtstuff.c`, `.eh_frame_hdr`+`.gnu.hash`; tcc = STABS (`.stab`/`.stabstr`, no DWARF), `.hash` only, unmerged input sections (`.text._start_c`, `.rodata.str1.1`, `.data.ro`, `.data.rel.ro.local`), one NT_GNU_PROPERTY note per input object (4), `tcc_backtrace`/`tcc_state`, 4x the size; libc = PT_INTERP `/lib/ld-musl-x86_64.so.1` + NEEDED `libc.musl-x86_64.so.1`, musl src path `/home/buildozer/aports/main/musl/src/1.2.4` (Alpine) |
| Swift ELF (`swift5_*` sections, `$s<len><Module>` symbols, 60+ MB) | Never eager-parse symbols; regex `SENGR` base64 in `.rodata`; `bin/swift-demangle` |
| Nim / D / Crystal / Free Pascal / ObjC / Ada / Fortran ELF (`NimMain`; `_D4core`; `Crystal:H`; `FPC 3.2.2`; `__objc_*`; `GNAT Version`; `libgfortran.so.5`) | Plain ELF (`elf`/`x86-64`/`62`), carried-over solver; HCFG base64 `SENGR...` (Nim/D/Crystal, offset = the `S`; Nim has raw decoys) or RAW (FPC `.data`, ObjC `.hcfg`, Ada/Fortran `.rodata`; offset = the `H`) |
| GnuCOBOL (`libcob.so.1`, `cob_init`) / Haskell GHC (`Main_main*_closure`, z-encoded `ghczminternal_*`, `GHC 9.x`) / OCaml (`caml_startup`, `camlStdlib__*`, `4.02.3`; `.cmxs` = natdynlink ET_DYN plugin, dynsyms `caml_plugin_header`, magic `Caml2007D002`) | Plain ELF for header ids; config NOT in the image for COBOL/Haskell (PK19/RS20 overlay past the section-header table, D19/D20); OCaml: HCFG RAW in the plugin `.data`; `nm -D --defined-only`, `readelf -dW` for exports/NEEDED |
| File size > `e_shoff + e_shnum*e_shentsize` (or > max section end), with or without a crc-valid HCFG | Appended OVERLAY: `xxd -s <image_end> F`; magic `<2 caps><day>` (`PK19` D19, `RS20` D20); parse the header fields the question lists, verify its bounds/sha256, run its transform if any, HCFG at the stated offset. A raw HCFG hit INSIDE the overlay (D20) still needs the header fields (`hcfg_resource_size`, offsets) |
| `00 61 73 6d 01 00 00 00` (`\0asm`), `.wasm` | `lib.binary.wasm_layout(data)` or `wasm-objdump -x f.wasm`; format `wasm`, architecture `wasm32`; HCFG RAW in data segment 0 |
| `NEKO` magic / `.n` file (format enum lists `neko_bytecode` since D19) | Neko VM bytecode (Haxe/nekoc): `neko`/`haxe` are apt-installable; globals table holds the string constants -> HCFG scan; format `neko_bytecode` |
| `kind: enum` + `accepted_values` + "Apply these mutually exclusive rules in order", or text describing bytes ("Read k1 at +5 ... ror8(byte XOR k2,3) XOR k1 ... verify the SHA-256") | The question IS the spec (D17, D19): implement it literally over the parsed facts, emit one listed token; don't reverse the stub first |
| Packed / high entropy / `UPX!`; or a real code-reversing question | `lib.binary.packer_info` -> `upx -d` on a COPY (UPX unseen); `rizin -q -c "aaa; pdf @ sym.<fn>"`; Ghidra headless `lib.binary.ghidra_decompile` (last resort) |

## Day by day
**D1 "ELF Aware"** (~14 min, 4 wrong): C ELF64 headers, `.huntress`, recover_code. **D2 "Mangled"** (~22 min): C++ ELF/MinGW PE,
first HCFG; PE symbols = COMDAT `.text$<mangled>`. **D3 "Table Manners"** (~1 h 48 min, ~60 wrong): .NET, format `pe_cli` after ~50
synonyms. **D4 "Go Fish"** (1.5 min): `amd64` REJECTED → `x86-64`. **D5 "Rust Belt"** (7 s). **D6 "Pool Party"** (~5 min): jar
constant-pool base64 HCFG. **D7 "Routine Check"** (3 min): Kotlin fat jar. **D8 "Swift Justice"**: 67 MB Swift; backfill #1 to 10
ids/group; integer elf_class/machine. **D9 "Nimble"** (86 s): raw decoys, NEW `hcfg_offset`. **D10 "Zig Zag"** (33 s): NEW
`has_hcfg_section`. **D11 "D-Day"** (36 s). **D12 "Pascal's Wager"** (54 s): HCFG RAW. **D13 "Crystal Clear"** (14 s). **D14
"Selective Memory"** (9 s): ObjC, `.hcfg`. **D15 "Stripped"** (74 s): stripped/symbolized pair, `<qualifier>_` ids. **D16 "Wasm
Up"** (91 s): compact/direct wasm pair, `wasm`/`wasm32` first try via the prebuilt `wasm_layout`.
**D17 "Decoder Ring"** (204 Qs): Ada; backfill #2; `hcfg_storage` burned ~10.9k POSTs / 3.5 h until revised to an enum.
**D18 "Flow State"** (T+11 s): Fortran, call-graph theme unasked. **D19 "Jack in the Box"** (T+2:25): GnuCOBOL + `PK19` packed
overlay; NEW `overlay_offset`/`overlay_size`; the questions spelled the stub. **D20 "Resourceful"** (T+49 s): Haskell + `RS20`
overlay; NEW `hcfg_resource_size`. **D21 "Shared Custody"** (T+1:33): OCaml loader + `.cmxs` plugin; question-named member
routing AFTER the qualifier peel (running it first dropped 26 ids).

**D22 "Bridge Troll"** (T+47 s): F# dll + runtimeconfig + `FSharp.Core.dll` support member; HCFG RAW twice ("FIRST record
that validates"); basenames `variant-000` -> `sample`. **D23 "Trust Issues"** (T+84 s): VB.NET, HCFG as PE overlay; timed modes
re-shaped values. **D24 "Spot the Difference"** (T+35 s): Scala twin jars `-vulnerable`/`-corrected`, the 12-id twin template
(role `<role>_format`, consensus config_*). **D25 "Out of Bounds"** (T+80 s): Clojure twins; Mastery 9 sets first POST
cross-wired 55 ids (`id(bytes)` caches) -> CORRECT ~2 min via localize + live worker.

**D26 "Crash Course"** (312 Qs; T+76 s, 0 wrong): Groovy 4 jar + `crash/trace.json` sidecar; theme ASKED (`crash_fault_method` =
frames[0], `crash_frames_match_methods`); ~15 lines for the sidecar. Insight: read the question before reversing. **D27 "Compiler
Says What"** (324 Qs; T+56 s, 0 wrong, ZERO new code): V-language gcc/tcc twin ELFs, HCFG RAW appended at image_end, "scan
backward from the end"; attribution theme UNASKED (facts in Recognition cues).

**D28 "Family Resemblance"** (slug `family-clustering`; 392 Qs; **CORRECT T+3:23, 6 rejected POSTs (4 batches + 2 single-id)**; TT 54 s / Mastery
12 sets (4704 ids) CORRECT first POST).
- Artifact: an Odin ELF TRIO in archive order `d28--sample-false-friend.elf`, `-family-a.elf`, `-family-b.elf` (~22.9 KB each,
  glibc PIE, stripped, identical section table). a vs b differ in ONE byte (role string); the false friend differs in ~2k bytes
  from `.text` on and carries its own valid HCFG (campaign `FF28-`). HCFG RAW appended at e_shoff+e_shnum*64 in all three.
- 14 new ids: 3 sha256, `<role>_format`/`<role>_machine` for `false_friend`/`family_a`/`family_b` (integer 62), 4 unqualified
  config_* = consensus of family-a + family-b ("do not use false-friend.elf"), `false_friend_config_campaign`. The cluster/
  similarity theme itself was NOT asked beyond that routing.
- BACKFILL #3 was the real work: 54 new spec-worded ids padded d01-d27 to 14 each (see Variant axes). The D27 solver answered
  361/392; the race harness banked 324 carried-over ids at T+1:06 and 36 more by T+1:23 (bisected batches); a worker added
  the 31 missing fields (generic spec-grammar fallback) and POSTed at T+2:34; last id at T+3:23.
- Lost time: four all-or-nothing batches sank on ONE wrong backfill field each -- d20 `overlay_size` (generic `<2 caps><2
  digits>` match -> 19; right = len - rfind(`RS20`) = 463) and d13 `crystal_symbol_count` (1255 with `.dynsym` added; right =
  771 from `.symtab` only, re-derived in 44 s). TT: d10 re-rolled to a PE `.exe` and the ELF-worded
  `section_count` was empty -> a live worker answered NumberOfSections (9). Mastery: the post-run replay of 10-12-set
  cases hit the 8 s timeout under load (pyelftools `.symtab` parse ~1 s/set) -> struct-parsed symtab reader, ~1 s/set total.

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class | exact_text: `ELF64`/`ELF32` (readelf style); `kind: integer` (D8+): the bit width `64`/`32` | ELFCLASS64; `2`/`1` |
| machine (`kind: integer`, D8-D9, D15, D21 loader/plugin, D27 gcc/tcc) | decimal e_machine (`62` = x86-64), also for an ET_DYN `.cmxs`; same for every compiler of one source | — |
| endianness | `little` / `big` | little endian, lsb, msb |
| machine (ELF) | `x86-64`, `x86`, `AArch64`, `ARM` (D19 text: tool labels and decimal/hex codes also accepted) | EM_X86_64, x86_64, amd64 (pre-D17 exact_text) |
| machine (PE FILE_HEADER) | 0x14c → `i386`; 0x8664 → `x86-64` | x86 (for PE i386); raw `0x8664` |
| architecture | the same machine words (Go amd64 → `x86-64`) | amd64, arm64, 386, x86_64 |
| elf_type | `ET_EXEC` / `ET_DYN` | EXEC |
| entry_point, crc32_hex, xor_key_hex | lowercase hex with `0x` (crc `0x%08x`, key `0x%02x`) | — |
| recover_code (`kind: integer`) | base-10 integer (`mov eax, 0x1fa4` → 8100); `none` if the symbol is absent (stripped d01) | the stripped/renamed leaf's constant (8114, 8106) |
| has_symtab / has_cpp_* / has_go_runtime / has_rust_mangled_symbol / has_coroutine_runtime | enum `true`/`false` | — |
| marker | exact `.huntress` string without the NUL; `none` if the section is missing | — |
| format (enum since D17-D19 on d12+) | `elf`, `pe`, `pe_cli` (.NET), `jar`, `wasm`, `neko_bytecode` (listed, unseen) | ELF, ELF64, elf64-x86-64, exe, pe32+, jar_jvm, ~50 .NET synonyms |
| format / arch per container (language/compiler never changes the label) | compiled ELF (D8-D21, D27 V via gcc AND tcc) `elf`/`x86-64`; WASM `wasm`/`wasm32`; .NET any language (C#, F#, VB.NET) `pe_cli`/`i386`; any JVM jar (Java, Kotlin, Scala D24, Clojure D25, Groovy D26, `<role>_format` too) `jar` | x86 for PE i386 |
| C++ symbols (ELF) incl. `mangled_score_symbol`, `typeinfo_symbol` (D17) | bare Itanium mangled name (`_ZNK15DiscoveryEngine5scoreEPKc`, `_ZTI15DiscoveryEngine`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` / `.rdata$<mangled>` | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` (D17 text: omitting it also accepted) | list without "" (pre-D17) |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates | hex imm, `"ret "` |
| methods / access_flags / method_count (jar, D17; d26 D26) | Main-Class `method_info` names in table order incl. `<init>` (JSON) / decimal `49` / count incl. `<init>`/`<clinit>` and compiler synthetics (Groovy `$getStaticMetaClass`, `$getLookup`, getters: d26 = 10) | — |
| crash_fault_method / crash_frames_match_methods (D26) | trace.json `frames[0]` verbatim (bare method name `stageThree`) / `true`/`false` = every frame in the primary class's method-name set | — |
| metadata_version (d03, d22 F#, d23 VB.NET) | BSJB root string `v4.0.30319` (same for every .NET language) | net8.0 / TFM |
| config_* | values verbatim from the decoded HCFG JSON (mutex keeps ONE backslash); D19: from the UNPACKED overlay's HCFG; D21: from the member the question names (plugin); D24/D25/D27 unqualified = consensus of both twins | JSON-escaped `\\`; `none` when the blob is merely hidden (D19) |
| hcfg_version / xor_key_hex | header byte 4 decimal / header byte 5 as `0x%02x` | — |
| has_hcfg_section (enum) | `true` when a section is literally named `.hcfg` | — |
| hcfg_offset (integer) | decimal FILE offset: base64 text start (`S`), RAW = the `HCFG` magic | — |
| overlay_offset / overlay_size (integer, D19-D20) | offset of the LAST occurrence of the day's overlay magic (`PK19`, `RS20`) / file length - that offset (header included) | — |
| hcfg_resource_size (integer, D20) | the overlay header's u32le resource-length field (RS20+8) in base 10 = the HCFG record length (12 + payload) | overlay size, payload-only length (not tried, but distinct values) |
| hcfg_storage (enum, D17) | `base64`, `raw_hcfg_section`, `raw_const_array`, `wasm_data_segment`, `raw` | every free-text spelling (~10.9k probes) -- closed token set |
| compression_methods (jar, json) | sorted distinct ZIP method ids, compact: `[0,8]` (names also accepted) | — |
| D28 backfill #3 counts (integer) | `symbol_count`/`d_symbol_count`/`crystal_symbol_count`/`handler_symbol_count` over NONEMPTY `.symtab` names (dupes kept; `.dynsym` only when no `.symtab`); `section_count` = ELF e_shnum incl. index 0 (PE re-roll: FILE_HEADER.NumberOfSections); `class_count` = `.class` entries in the jar CD; `structural_artifact_count` = group members | d13 count with `.dynsym` added (1255) |
| D28 hashes / predicates | `handler_symbols_sha256` = sha256(LF-join(sorted matches)), `method_names_sha256` over UNIQUE names; `structural_ordered_set_sha256` = sha256(":".join(member sha256 hex in CD order)); `has_*_runtime`/`has_decoy_branch` = literal substring predicate as stated -> `true`/`false` | — |
| D28 header / identity text | `cli_runtime` = CLI header `Major.Minor` (`2.5` for every .NET group); `vtable_symbol` = first symtab name matching the regex, bare on ELF (`_ZTV15DiscoveryEngine`), section-prefixed on PE; `class_name` = Main-Class `this_class` internal name (`Day06Variant000`); `packing_key_1/2_hex` = PK19 k1/k2 `0x%02x`; `plugin_hcfg_offset` = the `H` | d20 `overlay_size` from a non-day magic (19) |
| machine / format wording (D28 reworded) | machine (pattern): label, readelf/objdump/file label, or decimal/hex code all accepted; d10 format: ELF/PE in any case or ELF64/PE32+/"Portable Executable"; `<role>_machine` integer stays decimal (`62`) | — |
Naming law (from playbook.py): native format = container only; a managed .NET binary = container_runtime (pe+cli).
Java broke the compound law (`jar`); bytecode VMs get `<vm>_bytecode` (`neko_bytecode` in the D19 enum).

## Pitfalls that cost time
- **A synthetic label with no derivable spelling** (D3 .NET format ~1.5 h; D17 raw `hcfg_storage`, ~10.9k POSTs over 3.5 h,
  solved only by the organizers' contract revision): stop after ~10 single-id probes plus one `hctf labels` run, write HELP.md,
  then RE-PULL THE CONTRACT periodically and diff each id's question/answer_format. Never mass-probe an exact_text label.
- **Reversing what the question already specifies** (D19): the questions gave offsets, transform and hash check; guessing from
  bytes produced a spurious partial HCFG. Read the longest question of each new family FIRST. Size fields = the exact header
  field the layout names (D20 `hcfg_resource_size` = u32 @+8, not overlay/JSON length).
- **Absence vs hidden**: `none`/`[]`/`false` is right when the thing is ABSENT (stripped d01, a re-asked field inherits it),
  wrong when it is merely HIDDEN (D19 config: packed; the race harness's `none` placeholders were rejected).
- **A multi-field POST is all-or-nothing.** One wrong field fails the set and hides which one (D2; D28: 4 batches sank on 2
  generic-heuristic backfill fields, T+3:23 instead of ~T+1:30). POST carried-over ids first (they bank as `accepted`), then
  each NEW field family ALONE or bisect on the first rejection; a heuristic answer to a new spec is a guess until accepted.
- **Support members** (D3, D22): answer only from the PRIMARY assembly/classfile, but hash every member in archive order; skip
  a 5.7 MB framework DLL in brute passes.
- **"The theme is never asked" is NOT a rule** (D26): after 5 unasked days the crash theme was asked via a JSON sidecar inside
  the jar; the carried-over solver had no field for it (+31 s for a worker). On every new day list the member's NON-code entries
  (`unzip -l`, sections, resources, overlays) and parse any JSON/text sidecar up front. Unasked again on D27 (attribution).
- **Theme facts / must-not-run samples**: record each day's theme facts (D21 NEEDED/exports ... D26 trace + thrower, D27 producer/
  linker/libc per build) in NOTES.md; PROVE statically, never run the jar/ELF; a verdict id = evaluate the predicate table.
- **Per-member caches keyed on `id(bytes)`** (D25 Mastery, 55 wrong ids in 5/9 sets): CPython reuses a freed object's address,
  so a later member inherits an earlier member's facts. Symptom: wrong values that are VALID answers for another `dNN--` group
  of the same delivery. Key on (delivery, member name) / sha256 or pin the bytes (fixed; D26 10 sets clean).
- **Formatting / routing**: build submit JSON with python/jq (mutex = ONE backslash); capstone `ret` without trailing space,
  decimal imms; peel the (longest, multi-word) member qualifier before declaring a field unknown (D15, D28 `family_a`), the
  question-named-member router runs AFTER that peel (D21 dropped 26 ids), read `answer_format.kind` per id (D8).
- **Archives**: never unzip recursively (nested .jar/.apk lose their `dNN--` prefix); jar members are deflated, so `grep HCFG
  file.jar` finds nothing -- inflate every class (Scala `$` module, Clojure `__init`, Groovy static field) and non-class entry.
  Huge members (D8 67 MB Swift): no per-key brute force or per-field re-parse; cheap encodings first, crc-gate every hit.
- **Decoy magics** (D9 Nim): code that CHECKS the magic embeds `"HCFG"` literals; len 0 => crc32(b"")==0 passes! Require non-empty
  JSON that parses, keep scanning. Scan DIRECTION is part of the spec (D22 "first ... that validates" from the start, D27 "scan
  backward from the end"): with two valid records they pick different ones -- follow the question per id. Overlays: "final" -> `rfind`, verify the stated sha256. Offsets from `re.finditer().start()`
  on BOTH raw and base64 paths (D12), not `strings -t d` (off by 1).
- **ELF-worded id on a PE re-roll** (D28 TT d10 `.exe`): the solver left `section_count` empty -> live worker (+~40 s). Every
  ELF header/section/symbol field needs a PE mapping (NumberOfSections, COFF symbols, OptionalHeader) because members re-roll.
- **Timed windows**: download dominates (D16 TT 52 s of 64 s; D25 single ~69 s of 80 s). WASM sizes = 5-byte PADDED LEB128;
  PE machine map must include 0x8664 -> `x86-64` (a replay emitted `0x8664` and failed TT twice).
