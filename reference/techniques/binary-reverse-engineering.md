# binary-reverse-engineering — technique log (days 1-24; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
- One `evidence.zip` (AES, password `infected`), CUMULATIVE from D3: one group per past day (`dNN--variant-XXX.<ext>`, renamed
  `dNN--sample.<ext>` since D22) + ONE new container/language per day: D1 C ELF, D2 C++ (ELF or MinGW PE32+), D3 .NET, D4 Go,
  D5 Rust, D6 Java jar, D7 Kotlin jar, D8 Swift (67 MB), D9 Nim, D10 Zig (PE in Mastery), D11 D, D12 Free Pascal, D13 Crystal,
  D14 ObjC, D15 C pair `-stripped`/`-symbolized`, D16 WASM pair `-compact`/`-direct`, D17 Ada, D18 Fortran, D19 GnuCOBOL + `PK19`
  packed overlay, D20 Haskell + `RS20` overlay, D21 OCaml `-loader.elf` + `-plugin.cmxs` (HCFG only in the plugin), D22 F# .NET
  (+ `FSharp.Core.dll` support member), D23 VB.NET (`sample.dll` + `runtimeconfig.json`), **D24 Scala jar PAIR**
  (`-vulnerable.jar` + `-corrected.jar`, 4 KB each).
  Since D18 each day = a structure/behaviour THEME on a new language: call graph (D18), packing (D19), resources/overlays (D20),
  shared libraries (D21), managed<->native bridge (D22), anti-analysis predicates (D23), PATCH DIFFING (D24: "Two builds,
  one fix. Diff the vulnerable function against its corrected twin ... prove the old one was really broken"). D22-D24 = "new
  language on an old runtime" 3x (F#, VB.NET, Scala): expect Clojure/Groovy (JVM; d07 text still leaks "Day 26 ... primary
  classfile named by that unit"), C++/CLI, Elixir/BEAM, Haxe->Neko.
  Ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`; multi-member groups add `dNN_analysis_<tag>_<field>` (D15/D16/D21) and
  D21 also had UNQUALIFIED ids whose QUESTION names the member.
- From D2 every new member embeds the **HCFG** blob `'HCFG' | u8 ver | u8 xor_key | u16le len | u32le crc32(plain) | xor'd JSON
  @12`; only its STORAGE changes (see Variant axes). Scan raw bytes for `HCFG` AND base64 `SENGR...`, crc-gate every hit; when
  both miss, look past the image end (overlay) and read the question -- it spells the unpacker. The JSON has never-asked keys
  too (ipv4, windows_path, linux_path, service, host_model): parse the whole dict.
- The analysis is easy; the hard part is the GM's label for `exact_text` fields. **The organizers RE-ISSUE the contract** when a
  label is unguessable (D17 `hcfg_storage` -> enum + ordered rules). Since D17 question texts are SPECS (D19 spelled the stub).
  `format` is `kind: enum` on d12+: `elf, pe, pe_cli, jar, wasm, neko_bytecode`.
- **The contract LEAKS future days**: D19 named "RS20 for Day 20" (came true). Still open after D24: enum `neko_bytecode`, d07
  `method_count` "for Day 26 use the primary classfile named by that unit". Grep each contract for `[A-Z]{2}\d\d`, `Day NN`,
  unseen enum values (D21-D24: nothing new).
- **Theme asked on its own group only sometimes**: D5-D18 never; D19 (`overlay_offset`/`overlay_size`), D20
  (`hcfg_resource_size`) yes; D21-D24 NO (D24: 2 sha256 + `<role>_format` + config_* x2). Imports/exports/dlopen/ImplMap/
  predicates/the D24 method diff = backfill candidates (D17 precedent).
- **Every member since D2 embeds a `huntress.binary.dynamic_trace.v1` template** (unasked) {branch, event_count, campaign, family
  `<lang>_<theme>_trace`, effects, network none} gated on env `HUNTRESS_HOST_MODEL` (analysis/sandbox/workstation). Recent
  family/effects: D20 `haskell_resource_overlay_trace`, D21 `ocaml_controlled_dynlink_trace`, D22 `fsharp_managed_native_bridge_
  trace`/`inert_native_process_id_bridge`, D23 `vbnet_anti_analysis_predicate_trace`/`inert_predicate_only` (branches `success`/
  `decoy`/`failure`, extra field `analysis_detected`), D24 `scala_patch_diff_trace`/`benign_control_and_reversion_only` (extra
  boolean `control_positive`).
- Question count: 80 on D8, +10/day to 160 (D16), D17 204 (backfill #2), then +12/day: D23 276, **D24 288**, no backfill since D17.
  Mastery = `setN.` copies (+1 set/day lately: D23 7 sets, **D24 8 sets = 2304 ids**), artifacts `delivery N: evidence.zip`.
  Timed end to end: D19-D21 TT ~4 s / M ~10 s; D22 12.3 / 18.2 s; D23 13.0 / 7.9 s; D24 TT 5.0 s / M 8.4 s (solve 4.2, submit 3.9).
- **D24 contract re-wording (all groups)**: questions are now full SPECS -- sha256 "Use all dNN-- members in ZIP central-directory
  order ... member K (1-based)"; format lists every enum token with its rule; config questions spell the whole HCFG layout and
  the carrier rule per container (JAR: "Base64-alphabet UTF-8 constants of at least 80 characters ... first CRC32-valid").

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, storage per container: `.hcfg` section (D2/D10/D14), .NET FieldRVA (D3), Go/Rust
  rodata, base64 in a jar constant pool (Java/Kotlin, D24 Scala `$` module `ldc`) / Swift/Nim/D/Crystal literal, RAW FPC `.data`,
  WASM data seg 0, Ada/Fortran `.rodata`, D19 packed overlay, D20 RS20 overlay, D21 OCaml plugin `.data`, D22 F# RAW twice
  (`.text` + PE overlay: "FIRST record that validates"), D23 VB.NET RAW PE overlay only. Rule: scan for `HCFG` and `SENGR[A-Za-z0-9+/_-]*=*`, accept only crc32(plain) match AND parsing JSON, keep
  scanning past failures (D9 Nim decoys); never a fixed offset. Storage never changed WITHIN a day (single/TT/all Mastery sets).
- **Overlay layout per day (D19 PK19, D20 RS20)** -- appended at `e_shoff + e_shnum*e_shentsize`, magic `<2 caps><day>`, header
  spelled by the QUESTION. PK19 = `magic|ver|k1|k2|pad|u32le packed_len @8|sha256(unpacked) @12|packed @44`, unpack
  `ror8(b^k2,3)^k1`. RS20 = `magic|ver @4|u32le resource_len @8|u16le scratch_len @12|sha256(scratch) @16|HCFG @48 raw|scratch`,
  verify `48+res+scratch == len-o`. Rule: `o = data.rfind(magic)` ("final"), parse the listed widths, verify bounds + hash, HCFG
  at the stated offset; unspecified transform -> known-plaintext `HCFG` over (xor, rotate, xor). Field with no named magic:
  the `<2 caps><NN>` token whose digits = the group's day.
- **Location-as-answer** -- `hcfg_offset`: decimal FILE offset (base64 -> the `S`, RAW -> the `H`); `overlay_offset` = the magic;
  `overlay_size` = len - offset (header incl.); `hcfg_resource_size` = the u32le header field @+8 (380), not the overlay size.
- **Storage-as-answer (`hcfg_storage`, D17 enum)** -- in order: `base64` (carrier decoded) -> `raw_hcfg_section` (section `.hcfg`)
  -> `wasm_data_segment` -> `raw_const_array` (other native data section) -> `raw`. Unknown future token: read the rule list.
- **Any other encoding -> `lib.binary.hcfg_scan(data)`** (hex/base32/85/UTF-16/reversed/xor/zlib/multibyte+rolling xor/byte maps/
  custom b64/split/int-array/strided/RC4/AES/TEA/ChaCha/stack-built); `hcfg_find` = first valid hit. Not the PK19 stub.
- **xor key / config VALUE SHAPES** -- crc, key byte and campaign/domain/mutex/url re-roll per variant. Timed modes change the
  SHAPE too: D23 campaign `BRNN-00V` -> `BRNN-<8 uppercase hex>`, d01 marker `BR01-CATALOG-00V` -> `BR01-<8hex>`, d01 FILE symbol
  `variant-000.c` -> `sample.c`; D24 also domain `node-00V.dayNN...` -> `<word>-<8hex>.dayNN.example.invalid` (word: sync/hub/
  core/mesh/relay/stage), mutex `Global\HuntressBRNN_00V` -> `Global\Huntress<12 uppercase hex>`, url `.../api/BRNN-00V` ->
  `https://<word>-<8hex>.dayNN.example.invalid/<word>/<10hex>`. Rule: copy values verbatim from the decoded JSON/symtab; never
  regex-check a value shape or key on `00V` indices.
- **Container per member** -- ELF vs PE32+ re-rolls per member in Mastery (d02, d04, d10 `pe`); labels from THIS member's header;
  dispatch on MAGIC (`7f454c46`, `MZ`, `PK`, `\0asm`, next `NEKO`). PE symbol fields = COMDAT `.text$<mangled>`. Extensions lie
  about role, not container (D21 `.cmxs` = ELF ET_DYN).
- **Member qualifier in the id (D15/D16/D21/D24)** -- peel the longest field prefix that is a `[^a-z0-9]+` token of exactly one
  member name (`stripped`/`symbolized`, `compact`/`direct`, `loader`/`plugin`, `vulnerable`/`corrected`); the token can sit
  BEFORE the field family (D24 `d24_analysis_corrected_format`, `..._corrected_config_url`). `sha256_K` = ARCHIVE order, never
  sorted (D24: vulnerable is member 1).
- **Member named in the QUESTION (D21)** -- after the qualifier peel, if >1 member remains, keep the one whose basename ends with
  the token after `basename ends` / `Use the dNN--`. ORDER MATTERS (running it first dropped 26 ids on D21).
- **Unqualified id over a twin pair (D24)** -- "Decode both dNN-- role members and require their config objects to be
  byte-for-byte equal before using the common value": decode EVERY member, assert equal JSON, answer the common value (a
  first-member pick also passed because the twins always shared the config, but a mismatch should raise, not guess).
- **Member basename vocabulary (D22)** -- `dNN--variant-000.*` -> `dNN--sample.*` (questions reworded with it; inner names keep
  `variant-000`). Group by `dNN--` + extension/role tag only.
- **Primary vs support members (D3, D22, D23)** -- primary assembly + `.runtimeconfig.json` (+ D22 `FSharp.Core.dll`); question:
  "primary managed assembly ... runtimeconfig and dependency DLL members are delivery support only". Primary = the `.dll` whose
  name is not a framework/dependency (FSharp.Core, System.*, Microsoft.*), i.e. the one carrying HCFG; hash ALL members.
- **Stripped carry-over d01** -- re-rolls stripped in some sets (D15-D17 Mastery, D17/D19 TT, D23 Mastery set6): symbols/
  disassembly `[]`, has_symtab `false`, recover_code `none` (GM-confirmed; leaf-heuristic constants rejected). Pair by sha256.
- **Contract wording per fetch (D17)** -- question/answer_format of an id can change between fetches; read `answer_format` per id.
- **Mastery packaging** -- `setN.` ids (2-7 sets), each its own delivery; each set's 1st question ends `Evidence case:
  dNN-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]` (TT `dNN-tt-...`) = set->delivery map.
- **kind for the same field name** -- `elf_class`/`machine` exact_text on d01 but INTEGER (`64`/`62`) on d08/d15/d21: dispatch on kind.
- **Feature-presence / per-group field sets** -- `has_<x>` = a structural marker of <x> in THIS member (`has_hcfg_section`, D17
  `has_go_runtime` etc.); old groups gain ids over days (D8, D17): answer by field name from THAT member's facts dict.
- **Speed flags (no answer change)** -- CPU contention: re-measure with `taskset -c 0,1 /usr/bin/time python3 solve.py`.

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
| F# assembly (AssemblyRef `FSharp.Core`, resources `FSharpSignatureData.*`/`FSharpOptimizationData.*`, types `$Program`, `<>f__AnonymousType<n>`, closures `name@<line>`) + a big `FSharp.Core.dll` member | Same as C#: format `pe_cli`, machine `i386` (AnyCPU ILONLY = 0x14c), metadata `v4.0.30319`; answer from the PRIMARY dll only; raw `grep -abo HCFG` -> first crc-valid hit (D22: `.text` copy + identical overlay copy) |
| P/Invoke / "bridge" / "crossing" (`DllImportAttribute`, ModuleRef `libc`/`kernel32.dll`, `System.Runtime.InteropServices`) | dnfile: `md.ModuleRef` names, `md.ImplMap` rows (ImportName, ImportScope -> ModuleRef, MemberForwarded -> MethodDef, MappingFlags callconv/charset/SetLastError); `ilspycmd` shows the `[DllImport]` signatures (D22: `getpid`@libc, `GetCurrentProcessId`@kernel32.dll, Winapi) |
| VB.NET assembly (AssemblyRef `Microsoft.VisualBasic.Core`, `StandardModuleAttribute`, `VB$AnonymousType_<n>`, `Microsoft.VisualBasic.CompilerServices.Operators::CompareString`) | Same .NET labels (`pe_cli`/`i386`/`v4.0.30319`); HCFG RAW as a PE overlay after the last section (D23) -- raw `grep -abo HCFG` + crc-gate |
| Anti-analysis predicates ("checks the clock, sniffs the environment", TypeRefs `System.Diagnostics.Debugger` (`get_IsAttached`), `Stopwatch` (`StartNew`/`get_ElapsedTicks`), `Environment` (`get_ProcessorCount`, `GetEnvironmentVariable`), env `HUNTRESS_HOST_MODEL` = workstation/analysis/sandbox, branch words success/decoy/failure) | NEVER run it: the asked ids are header + HCFG (static). Record the predicate list for a backfill: dnfile TypeRef/MemberRef names + `ilspycmd` for the compare constants; native analogues = `ptrace`, `TracerPid`, `rdtsc`/`clock_gettime`, `cpuid`, `IsDebuggerPresent` |
| Go ("build info, function names, file paths") | `go version -m file`; `lib.binary.go_buildinfo` / `go_pclntab_funcs` (stripped names survive in `.gopclntab`) |
| Rust (mangled `_R`/`_ZN..17h<hash>E`, panic strings) | `readelf -hS` + `HCFG` scan; `rustfilt` / `lib.binary.rustfilt` if symbols are asked |
| `.jar` / "constant pool" / methods / access flags | unzip the jar, `META-INF/MANIFEST.MF` Main-Class, `javap -v -p Main.class` (method table order, `flags: (0x0031)`); `ConstantValue: String` base64 config |
| Kotlin fat jar (`kotlin/`, `X$fn$1 extends ContinuationImpl`) | Parse the Main-Class first, skip `kotlin/`/`org/jetbrains/`; coroutine runtime = `kotlin/coroutines/` entries |
| Scala jar (D24: `Foo.class` static forwarder + `Foo$.class` module with `MODULE$`, `Lscala/reflect/ScalaSignature;`/`ScalaSig` attr, `scala/Predef$`/`StringOps$`/`Option$` refs, manifest `Created-By: Huntress deterministic Scala factory`; scala-library NOT bundled) | format `jar`; the logic + HCFG base64 `ldc` live in `Foo$.class` (the `$` module), not the Main-Class forwarder; `javap -p -c -constants 'Foo$.class'` |
| Two members `-vulnerable` / `-corrected` (or patched/unpatched, old/new, v1/v2) -- "diff the vulnerable function against its corrected twin" | Route `<role>_` ids by the name token; answer header+HCFG per member; for the (unasked so far) diff: `javap -p -c` both `$` classes and `diff`, or compare per-method Code attributes -- D24 only `score(String)I` changed; native twins: `objdump -d` per symbol + `diff`, `rz-diff -t functions a b` |
| Swift ELF (`swift5_*` sections, `$s<len><Module>` symbols, 60+ MB) | Never eager-parse symbols; regex `SENGR` base64 in `.rodata`; `bin/swift-demangle` |
| Nim / D / Crystal / Free Pascal / ObjC / Ada / Fortran ELF (`NimMain`; `_D4core`; `Crystal:H`; `FPC 3.2.2`; `__objc_*`; `GNAT Version`; `libgfortran.so.5`) | Plain ELF (`elf`/`x86-64`/`62`), carried-over solver; HCFG base64 `SENGR...` (Nim/D/Crystal, offset = the `S`; Nim has raw decoys) or RAW (FPC `.data`, ObjC `.hcfg`, Ada/Fortran `.rodata`; offset = the `H`) |
| GnuCOBOL (`libcob.so.1`, `cob_init`) / Haskell GHC (`Main_main*_closure`, z-encoded `ghczminternal_*`, `GHC 9.x`) / OCaml (`caml_startup`, `camlStdlib__*`, `4.02.3`; `.cmxs` = natdynlink ET_DYN plugin, dynsyms `caml_plugin_header`, magic `Caml2007D002`) | Plain ELF for header ids; config NOT in the image for COBOL/Haskell (PK19/RS20 overlay past the section-header table, D19/D20); OCaml: HCFG RAW in the plugin `.data`; `nm -D --defined-only`, `readelf -dW` for exports/NEEDED |
| File size > `e_shoff + e_shnum*e_shentsize` (or > max section end), with or without a crc-valid HCFG | Appended OVERLAY: `xxd -s <image_end> F`; magic `<2 caps><day>` (`PK19` D19, `RS20` D20); parse the header fields the question lists, verify its bounds/sha256, run its transform if any, HCFG at the stated offset. A raw HCFG hit INSIDE the overlay (D20) still needs the header fields (`hcfg_resource_size`, offsets) |
| Two members differing by a name tag (D15/D16 builds, D21 loader+plugin), ids `dNN_analysis_<tag>_<field>` | Route each id to the member whose file name carries `<tag>`; UNqualified ids -> the member the QUESTION names; a role member (loader) may carry no HCFG |
| `00 61 73 6d 01 00 00 00` (`\0asm`), `.wasm` | `lib.binary.wasm_layout(data)` or `wasm-objdump -x f.wasm`; format `wasm`, architecture `wasm32`; HCFG RAW in data segment 0 |
| `NEKO` magic / `.n` file (format enum lists `neko_bytecode` since D19) | Neko VM bytecode (Haxe/nekoc): `neko`/`haxe` are apt-installable; globals table holds the string constants -> HCFG scan; format `neko_bytecode` |
| `answer_format.kind: enum` + `accepted_values`, question says "Apply these mutually exclusive rules in order" | The question IS the spec: implement the rules top-down over the parsed facts, emit one listed token (D17 hcfg_storage) |
| Question text describing bytes ("Read k1 at +5 ... compute ror8(byte XOR k2,3) XOR k1 ... verify the SHA-256") | Implement it literally from the text (D19); don't reverse the stub first -- the text is GM ground truth |
| Packed / high entropy / `UPX!` | `lib.binary.packer_info` → `upx -d` on a COPY (UPX not seen yet; D19's packer was a custom overlay) |
| Real code-reversing question (not seen yet) | `rizin -q -c "aaa; pdf @ sym.<fn>"`; Ghidra headless `lib.binary.ghidra_decompile` (heavy, last resort) |

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

**D22 "Bridge Troll"** (T+47 s, 0 wrong): F# .NET `sample.dll` + `runtimeconfig.json` + 5.7 MB `FSharp.Core.dll` support member;
bridge = 2 P/Invoke ImplMap rows (unasked); HCFG RAW twice (`.text` + PE overlay, "FIRST record that validates"); basenames
renamed `variant-000` -> `sample`. **D23 "Trust Issues"** (T+84 s, 0 wrong, zero new code): VB.NET `sample.dll` 8 KB, HCFG RAW
only as the PE overlay after `.reloc`; anti-analysis predicates (`Debugger.IsAttached`, `Stopwatch`, `ProcessorCount`,
`HUNTRESS_HOST_MODEL` -> success/decoy/failure) UNASKED -- a must-not-run sample answered statically; timed modes re-shaped values.

**D24 "Spot the Difference"** (slug `patch-diffing`; 288 Qs; **CORRECT T+35 s by the race harness's carried-over solver, 0
wrong, zero new code** -- solve.py byte-identical to D23's; TT 5.0 s / Mastery 8 sets 8.4 s, all first try).
- Artifact: new group of TWO Scala jars, `d24--sample-vulnerable.jar` (member 1) + `d24--sample-corrected.jar` (member 2), ~4 KB
  each, stored by Scala 2.13 (`ScalaSignature`, `Day24<Role>000.scala`): `META-INF/MANIFEST.MF` (Main-Class `Day24<Role>000`),
  `Day24<Role>000.class` (static forwarder) + `Day24<Role>000$.class` (module: `MODULE$`, `encodedConfig` = base64 `SENGR...`
  `ldc` in `<clinit>`, `decodeConfig()` = `Base64.getDecoder().decode`, `score(String)I`, `main`). scala-library not bundled.
- The diff (theme, UNASKED): only `score(String)I` changed. Vulnerable = `if (StringOps.nonEmpty(augmentString(s))) s.charAt(0)
  else -1` -> a NULL input throws NPE (CWE-476, null dereference); corrected = `Option(s).filter(_.nonEmpty).map(_.charAt(0))
  .getOrElse(-1)` (3 extra invokedynamic lambdas; the `$` class grows 4660 -> 5628 B). `main` identical in both: `HUNTRESS_HOST_
  MODEL` lookupswitch on String.hashCode -> analysis=(decoy,32) / workstation=(success,49) / sandbox=(failure,27) / default
  (failure,1), then `score("benign") + decodeConfig().length`; trace `scala_patch_diff_trace`/`benign_control_and_reversion_only`
  + `control_positive`. Found with `javap -p -c -constants` on both `$` classes; never executed.
- 12 new ids = 2 sha256 + `vulnerable_format`/`corrected_format` (`jar`) + 4 UNQUALIFIED config_* ("decode both role members,
  require byte-for-byte equal config") + 4 `corrected_config_*`. HCFG = base64 constant-pool string (the d06/d07 path).
- Insight: a theme that SOUNDS like real reversing (patch diff + "prove it was broken") again asked only header + HCFG; the
  generic qualifier peel + the jar constant-pool decoder covered a brand-new pair shape with zero code. Record the diff facts.

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class (`kind` exact_text) | `ELF64` / `ELF32` (readelf style) | ELFCLASS64 |
| elf_class (`kind: integer`, D8) | the bit width `64` / `32` | `2` / `1` (raw EI_CLASS byte) |
| machine (`kind: integer`, D8-D9, D15, D21 loader/plugin) | decimal e_machine (`62` = x86-64), also for an ET_DYN `.cmxs` | — |
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
| format / architecture (any compiled language ELF, D8-D19 incl. Ada, Fortran, COBOL) | `elf` / `x86-64` (language never changes the label) | — |
| format / architecture (WebAssembly, D16) | `wasm` / `wasm32` | — |
| format / machine (.NET any language: C# D3, F# D22, VB.NET D23) | `pe_cli` / `i386` (PE Machine 0x14c of an AnyCPU ILONLY assembly) | x86 |
| format (any JVM language jar: Java D6, Kotlin D7, Scala D24 incl. `<role>_format` of a twin pair) | `jar` | — |
| C++ symbols (ELF) incl. `mangled_score_symbol`, `typeinfo_symbol` (D17) | bare Itanium mangled name (`_ZNK15DiscoveryEngine5scoreEPKc`, `_ZTI15DiscoveryEngine`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` / `.rdata$<mangled>` | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` (D17 text: omitting it also accepted) | list without "" (pre-D17) |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates | hex imm, `"ret "` |
| methods / access_flags / method_count (jar, D17) | Main-Class `method_info` names in table order incl. `<init>` (JSON) / decimal `49` / count incl. `<init>`/`<clinit>` | — |
| metadata_version (d03, d22 F#, d23 VB.NET) | BSJB root string `v4.0.30319` (same for every .NET language) | net8.0 / TFM |
| config_* | values verbatim from the decoded HCFG JSON (mutex keeps ONE backslash); D19: from the UNPACKED overlay's HCFG; D21: from the member the question names (plugin) | JSON-escaped `\\`; `none` when the blob is merely hidden (D19) |
| hcfg_version / xor_key_hex | header byte 4 decimal / header byte 5 as `0x%02x` | — |
| has_hcfg_section (enum) | `true` when a section is literally named `.hcfg` | — |
| hcfg_offset (integer) | decimal FILE offset: base64 text start (`S`), RAW = the `HCFG` magic | — |
| overlay_offset / overlay_size (integer, D19-D20) | offset of the LAST occurrence of the day's overlay magic (`PK19`, `RS20`) / file length - that offset (header included) | — |
| hcfg_resource_size (integer, D20) | the overlay header's u32le resource-length field (RS20+8) in base 10 = the HCFG record length (12 + payload) | overlay size, payload-only length (not tried, but distinct values) |
| hcfg_storage (enum, D17) | `base64`, `raw_hcfg_section`, `raw_const_array`, `wasm_data_segment`, `raw` | every free-text spelling (~10.9k probes) -- closed token set |
| compression_methods (jar, json) | sorted distinct ZIP method ids, compact: `[0,8]` (names also accepted) | — |
Naming law (from playbook.py): native format = container only; a managed .NET binary = container_runtime (pe+cli).
Java broke the compound law (`jar`); bytecode VMs get `<vm>_bytecode` (`neko_bytecode` in the D19 enum).

## Pitfalls that cost time
- **A synthetic label with no derivable spelling** (D3 .NET format ~1.5 h; D17 raw `hcfg_storage`, ~10.9k POSTs over 3.5 h,
  solved only by the organizers' contract revision): stop after ~10 single-id probes plus one `hctf labels` run, write HELP.md,
  then RE-PULL THE CONTRACT periodically and diff each id's question/answer_format. Never mass-probe an exact_text label.
- **Reversing what the question already specifies** (D19, ~1 min): the config questions gave offsets, transform and hash check;
  guessing the transform from bytes produced a spurious partial HCFG. Read the longest question of each new family FIRST.
- **Size fields name a specific header field** (D20): `hcfg_resource_size` = the length field at +8, not the overlay length, not
  the JSON length. For every `*_size`/`*_length` id, map it to the exact header field the config question's layout names.
- **Absence vs hidden**: `none`/`[]`/`false` is right when the thing is ABSENT (stripped d01, D1 TT, D2 Mastery set2; a re-asked
  field inherits it), wrong when it is merely HIDDEN (D19 config: packed, the race harness's `none` placeholders were rejected).
- **A multi-field POST is all-or-nothing.** One wrong field fails the set and hides which one (D2). Submit unconfirmed/new fields
  ALONE; batch the bytes-derived ones (D17: 10 new fields in one POST; D19: 8 in one POST).
- **Support members** (D3, D22): a managed group can hold several `.dll`s; answer only from the PRIMARY assembly (the question
  says so), but hash every member in archive order. A 5.7 MB framework DLL would dominate a naive HCFG/brute pass -- skip it.
- **Theme facts**: D5-D18 and D21-D23 themes were not asked on their own day, D19/D20's were, and D17 backfilled old themes -- always
  record the day's theme facts (stub, overlay header, call graph, NEEDED/exports/dlopen handshake, P/Invoke ImplMap, D23 predicate
  list + branch words, D24 changed method + bug class + triggering input, trace family) in NOTES.md.
- **Anti-analysis samples** (D23): never execute to "force the truth out" -- the predicates gate only the inert trace, the
  scored config is static bytes. If a future id asks a branch/verdict, evaluate the predicate table statically per host model.
- **"Prove the old one was broken"** (D24): prove it STATICALLY (the bytecode path that dereferences/overflows on a named input,
  e.g. `null` -> NPE), never by running the vulnerable jar/ELF; the scored ids were header + HCFG.
- **Formatting**: build submit JSON with python/jq (`Global\Huntress...` mutex = ONE backslash); capstone `ret` has an empty
  op_str (`"ret "` -> strip), immediates in decimal.
- **Cumulative zip**: old groups' answers carry over when their sha256 match; POST the known ids first (they bank as `accepted`),
  then the new/unknown ids.
- **Id shape / kind / routing**: peel a member qualifier off the front before declaring a field unknown (D15
  `analysis_stripped_machine`); a question-named-member router runs AFTER that peel (D21: running it first dropped 26 ids); the
  same field name can change `kind` (D8 elf_class/machine integer) -- read `answer_format.kind` per id.
- **Archives**: never unzip recursively (nested .jar/.apk lose their `dNN--` prefix); jar members are deflated, so `grep HCFG
  file.jar` finds nothing -- inflate every class (Scala: the `$` module too) and read constant-pool strings. Huge members (D8
  67 MB Swift): no per-key xor brute force or per-field re-parse; cheap encodings first, crc-gate every hit.
- **Decoy magics** (D9 Nim): code that CHECKS the magic embeds `"HCFG"` literals; len 0 => crc32(b"")==0 passes! Require non-empty
  JSON that parses, keep scanning. Overlays: the question says "final" -> `rfind`, and verify the stated sha256.
- **Location fields per scan path** (D12): a decoder with raw AND base64 branches must return the hit offset (and encoding) from
  BOTH; take offsets from `grep -abo` / `re.finditer().start()`, not `strings -t d` (off by 1).
- **Timed windows**: download dominates (D16 TT 52 s of 64 s). WASM sizes are 5-byte PADDED LEB128 (`lib.binary.wasm_layout`).
  PE machine map must include 0x8664 → `x86-64` (a replay emitted `0x8664` and failed TT twice).
