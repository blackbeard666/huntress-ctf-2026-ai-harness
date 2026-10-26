# binary-reverse-engineering — technique log (days 1-26; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
- One `evidence.zip` (AES, password `infected`), CUMULATIVE from D3: one group per past day (`dNN--sample.<ext>`, `variant-000`
  before D22) + ONE new container/language per day: D1 C ELF, D2 C++ (ELF/MinGW PE32+), D3 .NET, D4 Go, D5 Rust, D6 Java jar,
  D7 Kotlin jar, D8 Swift (67 MB), D9 Nim, D10 Zig, D11 D, D12 FPC, D13 Crystal, D14 ObjC, D15 C `-stripped`/`-symbolized`, D16
  WASM `-compact`/`-direct`, D17 Ada, D18 Fortran, D19 GnuCOBOL + `PK19` overlay, D20 Haskell + `RS20` overlay, D21 OCaml
  `-loader.elf` + `-plugin.cmxs`, D22 F# (+ `FSharp.Core.dll`), D23 VB.NET, D24 Scala jar PAIR `-vulnerable`/`-corrected`, D25
  Clojure jar PAIR, **D26 Groovy jar (one member + a `crash/trace.json` entry)**.
  Since D18 each day = a THEME on a new language: call graph (D18), packing (D19), resources/overlays (D20), shared libraries
  (D21), managed<->native bridge (D22), anti-analysis (D23), PATCH DIFFING (D24), BOUNDS-ERROR ROOT CAUSE + reachability (D25),
  CRASH TRIAGE (D26 "the dump is a confession. Unwind the stack, find the faulting instruction, and triage what went wrong").
  D24-D26 = a VULN-RESEARCH arc (null deref -> OOB read -> crash triage; next: a NATIVE crash artifact -- core/minidump/
  sanitizer report --, exploitability/mitigations, another bug class, or a capstone/backfill). D22-D26 = "new language on an
  old runtime" 5x (F#, VB.NET, Scala, Clojure, Groovy -- all predicted); JVM languages left are niche (JRuby, Jython, Ceylon),
  then C++/CLI, Elixir/BEAM, Haxe->Neko (`neko_bytecode` still in the enum, unseen).
  Ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`; multi-member groups add `dNN_analysis_<tag>_<field>` (D15/D16/D21/D24/
  D25) and unqualified ids whose QUESTION names the member (D21) or demands consensus of both twins (D24/D25).
- From D2 every new member embeds the **HCFG** blob `'HCFG' | u8 ver | u8 xor_key | u16le len | u32le crc32(plain) | xor'd JSON
  @12`; only its STORAGE changes (see Variant axes). Scan raw bytes for `HCFG` AND base64 `SENGR...`, crc-gate every hit; when
  both miss, look past the image end (overlay) and read the question. Parse the whole JSON dict (never-asked keys exist).
- The hard part is the GM's label for `exact_text` fields; **the organizers RE-ISSUE the contract** when a label is unguessable
  (D17 `hcfg_storage` -> enum + ordered rules). Since D24 EVERY question is a full SPEC (sha256 "ZIP central-directory order ...
  member K (1-based)", format rule list, HCFG layout + carrier rule, JAR "Base64-alphabet UTF-8 constants >= 80 characters ...
  first CRC32-valid", D26 "Parse crash/trace.json and submit the exact first string in its frames array").
- **The contract LEAKS future days**: D19 "RS20 for Day 20", d07 "for Day 26 use the primary classfile named by that unit" (both
  came true). Open after D26: enum `neko_bytecode`. Grep each contract for `[A-Z]{2}\d\d`, `Day NN`, unseen enum values.
- **Theme asked on its own group only sometimes**: D19/D20 yes (overlay fields), D21-D25 NO, **D26 YES** (`crash_fault_method`,
  `crash_frames_match_methods`) -- from a JSON SIDECAR inside the member, cross-checked against the classfile.
- **Every member embeds a `huntress.binary.dynamic_trace.v1` template** (unasked) {branch, event_count, campaign, family
  `<lang>_<theme>_trace`, effects, network none} gated on env `HUNTRESS_HOST_MODEL` (analysis/sandbox/workstation); D25-D26 add
  `HUNTRESS_TRIGGER_FAULT`. D25 `clojure_bounds_root_cause_trace`/`bounded_synthetic_fault_only`; D26 `groovy_synthetic_crash_
  trace`/`bounded_caught_exception_only` + `fault_kind`/`fault_method`, plus the separate `huntress.synthetic_crash.v1` sidecar.
- Question count: 80 on D8, +10/day to 160, D17 204 (backfill #2), then +12/day: **D26 312**. Mastery = `setN.` copies, +1
  set/day (**D26 10 sets = 3120 ids, ~36 MB per delivery**). Timed: D25 TT 10.5 s / Mastery ~2 min (cross-wired first POST);
  **D26 TT 5.3 s / Mastery 8.2 s first try** (the D25 cache-identity fix held at 10 sets).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, storage per container: `.hcfg` section (D2/D10/D14), .NET FieldRVA (D3), Go/Rust
  rodata, base64 in a jar constant pool (Java/Kotlin, D24 Scala `$` module, D25 Clojure `<ns>__init.class` `encoded-config` Var,
  D26 Groovy `static final String encodedConfig` in the Main-Class) / Swift/Nim/D/Crystal literal, RAW FPC `.data`, WASM data seg 0, Ada/Fortran `.rodata`, D19 packed overlay, D20 RS20 overlay,
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
  core/mesh/relay/stage, D25-D26 also edge/cache/vault/proxy/node), mutex `Global\HuntressBRNN_00V` -> `Global\Huntress<12 uppercase
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
- **Theme sidecar inside the member (D26)** -- the jar carries a non-class entry `crash/trace.json` = `{"schema":
  "huntress.synthetic_crash.v1","kind":"IllegalStateException","frames":["stageThree","stageTwo","stageOne"]}` (innermost
  first). Values were IDENTICAL in all 12 deliveries (single, TT, 10 Mastery sets) while config re-rolled. Rule: open the
  member's zip, pick the entry whose name ends `trace.json` (never a fixed path), `json.loads`, answer frames[0] verbatim;
  predicates ("every frame is in the primary classfile method-name set") = set inclusion over method_info names; a missing
  sidecar = `none`/`false`. Expect the same sidecar idea in other containers (ELF section, PE resource, separate member).
- **Primary classfile (D7 vs D26)** -- d07 = manifest Main-Class; d26 "primary classfile named by that unit" = also the
  Main-Class (`Day26Variant000`, SourceFile `Day26Variant000.groovy`), NOT the `$_main_closure1` closure class. method_count =
  ALL method_info rows incl. Groovy synthetics (`<init>`, 3 stages, main, `$getStaticMetaClass`, get/setMetaClass, `$getLookup`,
  `getEncodedConfig` = 10). Inner class names keep `Variant000` although basenames say `sample`.
- **Member basename vocabulary (D22)** -- `dNN--variant-000.*` -> `dNN--sample.*`; group by `dNN--` + extension/role tag only.
- **Primary vs support members (D3, D22, D23)** -- primary assembly + `.runtimeconfig.json` (+ D22 `FSharp.Core.dll`); question:
  "primary managed assembly ... runtimeconfig and dependency DLL members are delivery support only". Primary = the `.dll` whose
  name is not a framework/dependency (FSharp.Core, System.*, Microsoft.*), i.e. the one carrying HCFG; hash ALL members.
- **Stripped carry-over d01** -- re-rolls stripped in some sets (D15-D17 Mastery, D17/D19 TT, D23 Mastery set6): symbols/
  disassembly `[]`, has_symtab `false`, recover_code `none` (GM-confirmed; leaf-heuristic constants rejected). Pair by sha256.
- **Mastery packaging** -- `setN.` ids (2-10 sets; D26 10 x ~36 MB), each its own delivery; each set's 1st question ends `Evidence
  case: dNN-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]` (TT `dNN-tt-...`) = set->delivery map. Per-member caches key on
  (delivery, member name) or sha256, never `id(bytes)` (D25: 5/9 sets cross-wired, see Pitfalls).
- **kind / field sets per group** -- `elf_class`/`machine` exact_text on d01 but INTEGER (`64`/`62`) on d08/d15/d21 (dispatch on
  `answer_format.kind`, which can change between fetches, D17); `has_<x>` = a structural marker of <x> in THIS member; old groups
  gain ids over days (D8, D17): answer by field name from THAT member's facts dict.
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

**D22 "Bridge Troll"** (T+47 s): F# `sample.dll` + runtimeconfig + 5.7 MB `FSharp.Core.dll` support member; P/Invoke theme
unasked; HCFG RAW twice ("FIRST record that validates"); basenames renamed `variant-000` -> `sample`. **D23 "Trust Issues"**
(T+84 s): VB.NET, HCFG RAW only as PE overlay; anti-analysis predicates unasked; timed modes re-shaped values. **D24 "Spot the
Difference"** (T+35 s): Scala twin jars `-vulnerable`/`-corrected` (only `score(String)I` changed, CWE-476); 12 ids = 2 sha256 +
`<role>_format` + 4 consensus config_* + 4 `corrected_config_*`; HCFG `ldc` in the `Foo$` module. **D25 "Out of Bounds"** (T+80 s,
zero new code): Clojure AOT twins, `parse-frame` unguarded `(nth frame 4)` (CWE-125) gated by `HUNTRESS_TRIGGER_FAULT`; same 12-id
template; Mastery 9 sets first POST cross-wired 55 ids (`id(bytes)` caches) -> CORRECT ~2 min via localize + live worker.

**D26 "Crash Course"** (slug `crash-triage`; 312 Qs; **CORRECT T+76 s, 0 wrong**; TT 5.3 s / Mastery 10 sets 8.2 s first try).
- Artifact: ONE `d26--sample.jar` (4.5 KB, Groovy 4 `groovyc`): `Day26Variant000.class` (Main-Class, `GroovyObject`, static
  `stageOne`->`stageTwo`->`stageThree`, `stageThree` does `new IllegalStateException`+`athrow`; `main` compares
  `HUNTRESS_HOST_MODEL` via `ScriptBytecodeAdapter.compareEqual`; `encodedConfig` = base64 HCFG) + `Day26Variant000$_main_closure1`
  + **`crash/trace.json`** `{"schema":"huntress.synthetic_crash.v1","kind":"IllegalStateException","frames":["stageThree",
  "stageTwo","stageOne"]}`.
- 12 new ids = the d06/d07 jar family (sha256, `format` jar, config_* x4, crc32/version/xor) + `method_count` (10, the d07
  "Day 26" leak) + the THEME: `crash_fault_method` ("exact first string in its frames array" -> `stageThree`) and
  `crash_frames_match_methods` ("every frame present in the primary classfile method-name set" -> `true`).
- Timeline: the race harness's carried-over solver banked 300 old ids at T+41 s and the 10 header/HCFG/method_count d26 ids at
  T+45 s (generic jar paths, no new code); a worker added ~15 lines (find `*trace.json` in the jar, frames[0], set inclusion vs
  `class_layout(main_class)`) and the 2 theme ids went CORRECT at T+76 s.
- Insight: first theme-asked day since D20, and it came as a tiny JSON sidecar + one structural predicate -- the "dump" was
  synthetic, no core/minidump parsing needed. The question text was the full spec; read it before reversing anything.

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
| format / arch per container (language never changes the label) | compiled ELF (D8-D21) `elf`/`x86-64`; WASM `wasm`/`wasm32`; .NET any language (C#, F#, VB.NET) `pe_cli`/`i386`; any JVM jar (Java, Kotlin, Scala D24, Clojure D25, Groovy D26, `<role>_format` too) `jar` | x86 for PE i386 |
| C++ symbols (ELF) incl. `mangled_score_symbol`, `typeinfo_symbol` (D17) | bare Itanium mangled name (`_ZNK15DiscoveryEngine5scoreEPKc`, `_ZTI15DiscoveryEngine`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` / `.rdata$<mangled>` | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` (D17 text: omitting it also accepted) | list without "" (pre-D17) |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates | hex imm, `"ret "` |
| methods / access_flags / method_count (jar, D17; d26 D26) | Main-Class `method_info` names in table order incl. `<init>` (JSON) / decimal `49` / count incl. `<init>`/`<clinit>` and compiler synthetics (Groovy `$getStaticMetaClass`, `$getLookup`, getters: d26 = 10) | — |
| crash_fault_method / crash_frames_match_methods (D26) | trace.json `frames[0]` verbatim (bare method name `stageThree`) / `true`/`false` = every frame in the primary class's method-name set | — |
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
- **Reversing what the question already specifies** (D19): the questions gave offsets, transform and hash check; guessing from
  bytes produced a spurious partial HCFG. Read the longest question of each new family FIRST. Size fields = the exact header
  field the layout names (D20 `hcfg_resource_size` = u32 @+8, not overlay/JSON length).
- **Absence vs hidden**: `none`/`[]`/`false` is right when the thing is ABSENT (stripped d01, a re-asked field inherits it),
  wrong when it is merely HIDDEN (D19 config: packed; the race harness's `none` placeholders were rejected).
- **A multi-field POST is all-or-nothing.** One wrong field fails the set and hides which one (D2). Submit unconfirmed/new fields
  ALONE; batch the bytes-derived ones. Old groups carry over by sha256: POST the known ids first (they bank as `accepted`).
- **Support members** (D3, D22): answer only from the PRIMARY assembly/classfile, but hash every member in archive order; skip
  a 5.7 MB framework DLL in brute passes.
- **"The theme is never asked" is NOT a rule** (D26): after 5 unasked days the crash theme was asked via a JSON sidecar inside
  the jar; the carried-over solver had no field for it (+31 s for a worker). On every new day list the member's NON-code entries
  (`unzip -l`, sections, resources, overlays) and parse any JSON/text sidecar up front.
- **Theme facts / must-not-run samples**: record each day's theme facts (stub, overlay header, NEEDED/exports, ImplMap, D23
  predicates + branch words, D24-D25 changed method + bug class + trigger + gating env, D26 trace + call chain + thrower) in
  NOTES.md. PROVE statically (bytecode path that derefs/indexes/throws on a named input; reachability = the env compares),
  never by running the jar/ELF; a branch/verdict id = evaluate the predicate table per host model.
- **Per-member caches keyed on `id(bytes)`** (D25 Mastery, 55 wrong ids in 5/9 sets): CPython reuses a freed object's address,
  so a later member inherits an earlier member's facts. Symptom: wrong values that are VALID answers for another `dNN--` group
  of the same delivery. Key on (delivery, member name) / sha256 or pin the bytes (fixed; D26 10 sets clean).
- **Formatting**: build submit JSON with python/jq (mutex = ONE backslash); capstone `ret` -> strip trailing space; decimal imms.
- **Id shape / kind / routing**: peel a member qualifier off the front before declaring a field unknown (D15); a
  question-named-member router runs AFTER that peel (D21: first dropped 26 ids); read `answer_format.kind` per id (D8).
- **Archives**: never unzip recursively (nested .jar/.apk lose their `dNN--` prefix); jar members are deflated, so `grep HCFG
  file.jar` finds nothing -- inflate every class (Scala `$` module, Clojure `__init`, Groovy static field) and non-class entry.
  Huge members (D8 67 MB Swift): no per-key brute force or per-field re-parse; cheap encodings first, crc-gate every hit.
- **Decoy magics** (D9 Nim): code that CHECKS the magic embeds `"HCFG"` literals; len 0 => crc32(b"")==0 passes! Require non-empty
  JSON that parses, keep scanning. Overlays: "final" -> `rfind`, verify the stated sha256. Offsets from `re.finditer().start()`
  on BOTH raw and base64 paths (D12), not `strings -t d` (off by 1).
- **Timed windows**: download dominates (D16 TT 52 s of 64 s; D25 single ~69 s of 80 s). WASM sizes = 5-byte PADDED LEB128;
  PE machine map must include 0x8664 -> `x86-64` (a replay emitted `0x8664` and failed TT twice).
