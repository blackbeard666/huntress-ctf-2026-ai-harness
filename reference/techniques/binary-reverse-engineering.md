# binary-reverse-engineering — technique log (days 1-25; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
- One `evidence.zip` (AES, password `infected`), CUMULATIVE from D3: one group per past day (`dNN--sample.<ext>`, `variant-000`
  before D22) + ONE new container/language per day: D1 C ELF, D2 C++ (ELF/MinGW PE32+), D3 .NET, D4 Go, D5 Rust, D6 Java jar,
  D7 Kotlin jar, D8 Swift (67 MB), D9 Nim, D10 Zig (PE in Mastery), D11 D, D12 FPC, D13 Crystal, D14 ObjC, D15 C `-stripped`/
  `-symbolized`, D16 WASM `-compact`/`-direct`, D17 Ada, D18 Fortran, D19 GnuCOBOL + `PK19` overlay, D20 Haskell + `RS20` overlay,
  D21 OCaml `-loader.elf` + `-plugin.cmxs`, D22 F# (+ `FSharp.Core.dll`), D23 VB.NET, D24 Scala jar PAIR `-vulnerable`/
  `-corrected`, **D25 Clojure jar PAIR** (same role names, ~8 KB each).
  Since D18 each day = a structure/behaviour THEME on a new language: call graph (D18), packing (D19), resources/overlays (D20),
  shared libraries (D21), managed<->native bridge (D22), anti-analysis predicates (D23), PATCH DIFFING (D24 "diff the vulnerable
  function against its corrected twin ... prove the old one was really broken"), BOUNDS-ERROR ROOT CAUSE (D25 "the code reaches
  where it shouldn't. Prove the bounds error is real, trace its reachability, and compare against the corrected twin").
  D24-D25 = a VULN-RESEARCH arc on twins (null deref -> OOB read; next: another bug class -- integer overflow, UAF, format
  string, injection, race -- or a NATIVE twin). D22-D25 = "new language on an old runtime" 4x (F#, VB.NET, Scala, Clojure --
  predicted): Groovy is the last obvious JVM language (d07 still leaks "Day 26 ... primary classfile named by that unit"), then
  C++/CLI, Elixir/BEAM, Haxe->Neko.
  Ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`; multi-member groups add `dNN_analysis_<tag>_<field>` (D15/D16/D21/D24/
  D25) and unqualified ids whose QUESTION names the member (D21) or demands consensus of both twins (D24/D25).
- From D2 every new member embeds the **HCFG** blob `'HCFG' | u8 ver | u8 xor_key | u16le len | u32le crc32(plain) | xor'd JSON
  @12`; only its STORAGE changes (see Variant axes). Scan raw bytes for `HCFG` AND base64 `SENGR...`, crc-gate every hit; when
  both miss, look past the image end (overlay) and read the question. The JSON has never-asked keys (ipv4, windows_path,
  linux_path, service, host_model): parse the whole dict.
- The analysis is easy; the hard part is the GM's label for `exact_text` fields. **The organizers RE-ISSUE the contract** when a
  label is unguessable (D17 `hcfg_storage` -> enum + ordered rules). Since D24 EVERY question is a full SPEC (sha256 "ZIP
  central-directory order ... member K (1-based)", format rule list, HCFG layout + carrier rule per container, JAR: "Base64-
  alphabet UTF-8 constants of at least 80 characters ... first CRC32-valid"). `format` enum d12+: `elf, pe, pe_cli, jar, wasm,
  neko_bytecode`.
- **The contract LEAKS future days**: D19 named "RS20 for Day 20" (came true). Still open after D25: enum `neko_bytecode`, d07
  `method_count` "for Day 26 use the primary classfile named by that unit". Grep each contract for `[A-Z]{2}\d\d`, `Day NN`,
  unseen enum values (D21-D25: nothing new).
- **Theme asked on its own group only sometimes**: D5-D18 never; D19 (`overlay_offset`/`overlay_size`), D20
  (`hcfg_resource_size`) yes; D21-D25 NO (twins: 2 sha256 + `<role>_format` + config_* x2). Imports/ImplMap/predicates/the
  D24-D25 diffs + triggers = backfill candidates (D17 precedent).
- **Every member embeds a `huntress.binary.dynamic_trace.v1` template** (unasked) {branch, event_count, campaign, family
  `<lang>_<theme>_trace`, effects, network none} gated on env `HUNTRESS_HOST_MODEL` (analysis/sandbox/workstation). Recent:
  D23 `vbnet_anti_analysis_predicate_trace`/`inert_predicate_only` (+`analysis_detected`), D24 `scala_patch_diff_trace`/
  `benign_control_and_reversion_only` (+`control_positive`), D25 `clojure_bounds_root_cause_trace`/`bounded_synthetic_fault_only`
  (+ 2nd env var `HUNTRESS_TRIGGER_FAULT`).
- Question count: 80 on D8, +10/day to 160 (D16), D17 204 (backfill #2), then +12/day: D24 288, **D25 300**, no backfill since D17.
  Mastery = `setN.` copies (+1 set/day: D24 8 sets, **D25 9 sets = 2700 ids, ~36 MB per delivery**). Timed end to end: D23
  13.0 / 7.9 s; D24 5.0 / 8.4 s; **D25 TT 10.5 s; Mastery first POST 54 s INCORRECT (55 ids cross-wired, see Pitfalls), CORRECT
  ~2 min after start via localize + a live worker.**

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, storage per container: `.hcfg` section (D2/D10/D14), .NET FieldRVA (D3), Go/Rust
  rodata, base64 in a jar constant pool (Java/Kotlin, D24 Scala `$` module, D25 Clojure `<ns>__init.class` `encoded-config` Var)
  / Swift/Nim/D/Crystal literal, RAW FPC `.data`, WASM data seg 0, Ada/Fortran `.rodata`, D19 packed overlay, D20 RS20 overlay,
  D21 OCaml plugin `.data`, D22 F# RAW twice (`.text` + PE overlay: "FIRST record that validates"), D23 VB.NET RAW PE overlay.
  Rule: scan for `HCFG` and `SENGR[A-Za-z0-9+/_-]*=*` (jars: every class's constant pool), accept only crc32(plain) match AND
  parsing JSON, keep scanning past failures (D9 Nim decoys); never a fixed offset or a fixed class. Storage never changed WITHIN a day (single/TT/all Mastery sets).
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
  core/mesh/relay/stage, D25 also edge/cache/vault/proxy/node), mutex `Global\HuntressBRNN_00V` -> `Global\Huntress<12 uppercase
  hex>`, url `.../api/BRNN-00V` -> `https://<word>-<8hex>.dayNN.example.invalid/<word>/<10hex>` (path words vault/edge/stage/sync/
  gate); the url host word is independent of the domain word. Rule: copy values verbatim from the decoded JSON/symtab; never
  regex-check a value shape or key on `00V` indices.
- **Container per member** -- ELF vs PE32+ re-rolls per member in Mastery (d02, d04, d10 `pe`); labels from THIS member's header;
  dispatch on MAGIC (`7f454c46`, `MZ`, `PK`, `\0asm`, next `NEKO`). PE symbol fields = COMDAT `.text$<mangled>`. Extensions lie
  about role, not container (D21 `.cmxs` = ELF ET_DYN).
- **Member qualifier in the id (D15/D16/D21/D24)** -- peel the longest field prefix that is a `[^a-z0-9]+` token of exactly one
  member name (`stripped`/`symbolized`, `compact`/`direct`, `loader`/`plugin`, `vulnerable`/`corrected` D24+D25); the token can sit
  BEFORE the field family (D24 `d24_analysis_corrected_format`, `..._corrected_config_url`). `sha256_K` = ARCHIVE order, never
  sorted (D24: vulnerable is member 1).
- **Member named in the QUESTION (D21)** -- after the qualifier peel, if >1 member remains, keep the one whose basename ends with
  the token after `basename ends` / `Use the dNN--`. ORDER MATTERS (running it first dropped 26 ids on D21).
- **Unqualified id over a twin pair (D24, D25 identical wording)** -- "Decode both dNN-- role members and require their config objects to be
  byte-for-byte equal before using the common value": decode EVERY member, assert equal JSON, answer the common value (a
  first-member pick also passed because the twins always shared the config, but a mismatch should raise, not guess).
- **Member basename vocabulary (D22)** -- `dNN--variant-000.*` -> `dNN--sample.*`; group by `dNN--` + extension/role tag only.
- **Primary vs support members (D3, D22, D23)** -- primary assembly + `.runtimeconfig.json` (+ D22 `FSharp.Core.dll`); question:
  "primary managed assembly ... runtimeconfig and dependency DLL members are delivery support only". Primary = the `.dll` whose
  name is not a framework/dependency (FSharp.Core, System.*, Microsoft.*), i.e. the one carrying HCFG; hash ALL members.
- **Stripped carry-over d01** -- re-rolls stripped in some sets (D15-D17 Mastery, D17/D19 TT, D23 Mastery set6): symbols/
  disassembly `[]`, has_symtab `false`, recover_code `none` (GM-confirmed; leaf-heuristic constants rejected). Pair by sha256.
- **Contract wording per fetch (D17)** -- question/answer_format of an id can change between fetches; read `answer_format` per id.
- **Mastery packaging** -- `setN.` ids (2-9 sets; D25 9 x ~36 MB), each its own delivery; each set's 1st question ends `Evidence
  case: dNN-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]` (TT `dNN-tt-...`) = set->delivery map. **Member-bytes identity
  (D25)**: with 9 sets x ~34 members, per-member caches keyed on `id(bytes)` returned ANOTHER member's facts once the first was
  freed and CPython reused the address (5/9 sets wrong: d23 <- d03 config, d22/d15 <- d10 PE header, d06/d24 <- d16 wasm). Rule:
  key every per-member cache on (delivery, member name) or sha256, or keep the bytes alive for the whole run -- never `id()`.
- **kind for the same field name** -- `elf_class`/`machine` exact_text on d01 but INTEGER (`64`/`62`) on d08/d15/d21: dispatch on kind.
- **Feature-presence / per-group field sets** -- `has_<x>` = a structural marker of <x> in THIS member (`has_hcfg_section`, D17
  `has_go_runtime` etc.); old groups gain ids over days (D8, D17): answer by field name from THAT member's facts dict.
- **Speed flags (no answer change)** -- CPU contention: re-measure with `taskset -c 0,1 /usr/bin/time python3 solve.py`; D25 TT
  solve phase 8.0 s at 300 ids under load (single ~1.2 s isolated on D24).

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
| Two members differing by a name tag (D15/D16 builds, D21 loader+plugin: a role member may carry no HCFG; unqualified ids -> the member the QUESTION names) or `-vulnerable` / `-corrected` twins (D24/D25; patched/unpatched, old/new, v1/v2) -- "diff the vulnerable function against its corrected twin", "prove the bounds error is real, trace its reachability" | Route `<role>_` ids by the name token; answer header+HCFG per member; for the (unasked so far) diff: `javap -p -c` per class of both jars and `diff` after stripping the role token from class names -- D24 Scala `score(String)I`, D25 Clojure `parse_frame` (unguarded `RT.nth(v,4)` vs `(< 4 (count v))` guard -> -1); reachability = the env compares in `-main`; native twins: `objdump -d` per symbol + `diff`, `rz-diff -t functions a b` |
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

**D22 "Bridge Troll"** (T+47 s): F# `sample.dll` + runtimeconfig + 5.7 MB `FSharp.Core.dll` support member; 2 P/Invoke ImplMap
rows (unasked); HCFG RAW twice ("FIRST record that validates"); basenames renamed `variant-000` -> `sample`. **D23 "Trust Issues"**
(T+84 s, zero new code): VB.NET 8 KB, HCFG RAW only as the PE overlay; anti-analysis predicates UNASKED; timed modes re-shaped values.
**D24 "Spot the Difference"** (T+35 s, zero new code): Scala 2.13 twin jars `-vulnerable`/`-corrected`; only `score(String)I`
changed (nonEmpty-then-charAt NPEs on null, CWE-476 -> `Option(s)...getOrElse(-1)`); 12 new ids = 2 sha256 + `<role>_format` +
4 unqualified "both members must agree" config_* + 4 `corrected_config_*`; HCFG base64 `ldc` in the `Foo$` module.

**D25 "Out of Bounds"** (slug `synthetic-vulnerability-root-cause`; 300 Qs; **CORRECT T+80 s by the race harness's carried-over
solver, 0 wrong, zero new code** -- ~69 s of it was the 36 MB download; TT 10.5 s first try; Mastery 9 sets see below).
- Artifact: `d25--sample-vulnerable.jar` (member 1) + `-corrected.jar` (member 2), ~8.3 KB CLOJURE AOT jars: `day25/<role>000.class`
  (gen-class Main stub), `<role>000__init.class` (ns loader; Vars `encoded-config` = base64 `SENGR...` ldc, `parse-frame`,
  `-main`), `<role>000$parse_frame.class`, `<role>000$_main.class`, gensym `fn__269`/`loading__6812__auto____267`; no clojure.jar.
- The bug (theme, UNASKED): `parse-frame` = `(nth frame 4)` -> `RT.nth(Object,int)` with NO bound -> IndexOutOfBoundsException
  on a short frame (CWE-125 OOB read / CWE-129 unchecked index); corrected = `(if (< 4 (count frame)) (nth frame 4) -1)`
  (`RT.count` + `lcmp`/`ifge` -> const `-1`). Reachability: `-main` reads `HUNTRESS_HOST_MODEL` (workstation...) and
  `HUNTRESS_TRIGGER_FAULT` == `"1"`, then picks a 2-element frame `[1 2]` (faults) or the 5-element `[1 2 3 4 5]`; trace family
  `clojure_bounds_root_cause_trace`, effects `bounded_synthetic_fault_only`. Found with `javap -p -c -constants` per class.
- 12 new ids, SAME shape and wording as D24 (2 sha256, `vulnerable_format`/`corrected_format` = `jar`, 4 unqualified consensus
  config_*, 4 `corrected_config_*`); JAR carrier rule "Base64-alphabet UTF-8 constants >= 80 chars" covered `__init.class`.
- Mastery (9 sets, 2700 ids): the daemon's first POST was INCORRECT -- 55 ids in 5 sets carried values of a DIFFERENT group of
  the same delivery (solver caches keyed on `id(member bytes)`, see Pitfalls); GM per-set feedback + localize fixed 9 label ids, a
  live worker re-derived the other 46 by a direct per-member HCFG scan (pyzipper `infected`) -> CORRECT ~2 min after start.
- Insight: the theme ("prove the bounds error", "trace its reachability") again asked only header + HCFG; the twin shape is now
  a template. The day's real risk was solver plumbing at 9 sets, not reversing.

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class | exact_text: `ELF64`/`ELF32` (readelf style); `kind: integer` (D8+): the bit width `64`/`32` | ELFCLASS64; `2`/`1` |
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
| format / arch per container (language never changes the label) | compiled ELF (D8-D21) `elf`/`x86-64`; WASM `wasm`/`wasm32`; .NET any language (C#, F#, VB.NET) `pe_cli`/`i386`; any JVM jar (Java, Kotlin, Scala D24, Clojure D25, `<role>_format` too) `jar` | x86 for PE i386 |
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
- **Theme facts / must-not-run samples**: themes were asked only D19/D20 (D17 backfilled old ones) -- record each day's theme
  facts (stub, overlay header, call graph, NEEDED/exports, ImplMap, D23 predicates + branch words, D24/D25 changed method + bug
  class + trigger + gating env, trace family) in NOTES.md. Never execute to "force the truth out" (D23): predicates gate only
  the inert trace; if an id asks a branch/verdict, evaluate the predicate table statically per host model.
- **"Prove the old one was broken" / "prove the bounds error is real"** (D24, D25): prove it STATICALLY (the bytecode path that
  dereferences / indexes past the end on a named input: `null` -> NPE, a 2-element frame -> `RT.nth(v,4)` IOOBE; reachability =
  the env compares gating that input), never by running the jar/ELF; the scored ids were header + HCFG both days.
- **Per-member caches keyed on `id(bytes)`** (D25 Mastery, 55 wrong ids in 5/9 sets): CPython reuses a freed object's address, so
  a later member silently inherits an earlier member's facts/config (a d22 .NET dll answered as the d10 PE: `pe`/`x86-64`/`none`
  + BR10 config). Symptom: wrong values that are VALID answers for another `dNN--` group of the same delivery. Key caches on
  (delivery, member name) / sha256 or pin the bytes; re-check after any set-count jump.
- **Formatting**: build submit JSON with python/jq (mutex = ONE backslash); capstone `ret` -> strip trailing space; decimal imms.
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
- **Timed windows**: download dominates (D16 TT 52 s of 64 s; D25 single ~69 s of 80 s). WASM sizes = 5-byte PADDED LEB128;
  PE machine map must include 0x8664 → `x86-64` (a replay emitted `0x8664` and failed TT twice).
