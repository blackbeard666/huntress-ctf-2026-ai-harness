# binary-reverse-engineering — technique log (days 1-18; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- One `evidence.zip` (AES, password `infected`). From Day 3 on it is CUMULATIVE: members `dNN--variant-XXX.<ext>`, one group per
  past day, plus ONE new container/language per day: D1 C ELF, D2 C++ (ELF or MinGW PE32+), D3 .NET dll, D4 static stripped Go,
  D5 static Rust, D6 Java .jar, D7 Kotlin fat .jar, D8 Swift ELF (67 MB), D9 Nim, D10 Zig (PE `.exe` in Mastery), D11 D (DMD),
  D12 Free Pascal, D13 Crystal, D14 Objective-C (GNUstep), D15 a PAIR of C ELFs (`-stripped`/`-symbolized`), D16 a PAIR of WASM
  modules (`-compact`/`-direct`), D17 Ada ELF (1.4 MB, GNAT 14.2, dynamic, not stripped, DWARF) -- back to ONE member, D18
  Fortran ELF (16 KB gfortran, dynamic `libgfortran.so.5`, not stripped, `MAIN__` + `variant-000.f90`).
  Answer ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`; a multi-member group adds a member qualifier:
  `dNN_analysis_<qualifier>_<field>` (D15 `stripped_`/`symbolized_`, D16 `compact_`/`direct_`).
- From Day 2 on, every new-day member carries the same embedded **HCFG** config blob: `'HCFG' | u8 ver | u8 xor_key | u16 len (LE) |
  u32 crc32 | xor'd JSON` (JSON at offset 12; crc32 is over the decoded plaintext). Only its storage location changes
  (`.hcfg` section on D2/D10/D14, .NET FieldRVA array, Go/Rust rodata, base64'd in a Java/Kotlin constant pool, base64 Swift/Nim/D/
  Crystal String literal on D8/D9/D11/D13, RAW in FPC `.data` on D12, RAW in WASM data segment 0 on D16, RAW in Ada `.rodata` on
  D17, RAW in gfortran `.rodata` symbol `encoded_config.N` on D18). Scan raw bytes for `HCFG` AND its base64 form `SENGR...`
  (raw `HCFG` can be a false hit inside code: check crc).
  The JSON carries never-asked keys too (ipv4, windows_path, linux_path, service, host_model): parse the whole dict.
- The analysis is easy (headers, symbols, one config blob). The hard part is the GM's exact label for `exact_text` fields
  (format, machine, symbol, D17 `hcfg_storage`). **The organizers RE-ISSUE the contract mid-day** when a label is unguessable:
  D17's `hcfg_storage` became `kind: enum` + `accepted_values` + an ordered rule list in the question text (and 20 other ids got
  rule text that accepts equivalents). Re-pull the contract while stuck; never out-guess it. (D10 had already relaxed many ids
  to `kind: pattern`; keep emitting the GM-confirmed spellings.) Question count: 80 on D8, +10/day to 160 on D16, **D17 = 204**: 2nd
  BACKFILL (like D8): every old group padded to 11 ids, re-asking EARLIER DAYS' single-solve facts (D1 marker/recover_code, D2
  mangled symbols, D4/D5 runtime-identity booleans + section_names, D6/D7 class-file facts) plus NEW `hcfg_storage`.
- **The NEW day's prompt theme is still never asked** (D5-D18: Rust panics, Kotlin coroutines, Swift protocols, ..., D16 wasm
  "doors", D17 "recover the reversible decoder", D18 "reconstruct the call graph, API intent, no injection" -- only the standard
  header + HCFG ids). BUT the D17 backfill showed a day's theme CAN be asked later, against that day's old group (D2 C++ symbols,
  D6/D7 class layout, D7 coroutines). New group ids: sha256, format, architecture, machine, config_campaign/domain/mutex/url/
  crc32_hex + hcfg_offset/hcfg_version/xor_key_hex (D17 and D18: all 11).
- **Every member since D2 also embeds a "dynamic trace" template** (unasked so far): `{"schema":"huntress.binary.dynamic_trace.v1",
  "branch":"<b>","event_count":<n>,"campaign":...,"family":"<lang>_<theme>_trace","effects":"...","network":"none"}`, printed per
  host model read from env `HUNTRESS_HOST_MODEL` (`analysis`/`sandbox`/`workstation`). family/effects name the day's theme
  (D17 `ada_encoded_config_trace`; D18 `fortran_indirect_flow_trace`, effects `modeled_process_access_no_injection`).
- Time Trial ≈ 6-16 s early; Mastery = `setN.` prefixed copies (2 sets D2-D7, 5 D8-D9, 3 D10-D14, 5 D15-D17, **4 on D18**: 4 x 216
  = 864 ids); artifacts are named `delivery N: evidence.zip`. Timed end to end: D17 TT 5 s / Mastery 14 s; D18 TT 8 s / Mastery 14 s.
  Question count D18 = **216** = 204 + the 12-id d18 group (no backfill on D18).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, different storage per container (`.hcfg` section, .NET FieldRVA, Go/Rust rodata,
  base64 in a Java/Kotlin constant pool, base64 Swift/Nim/D/Crystal string literal, raw FPC `.data`, RAW first payload byte of WASM
  active data segment 0, RAW Ada `.rodata` (D17 file 207432)): scan raw bytes for `HCFG` and for `SENGR[A-Za-z0-9+/_-]*=*`,
  decode, accept only if crc32(plain) matches AND the JSON parses -- keep scanning past a failing hit (D9 Nim had two raw decoys);
  never a fixed offset. Storage did NOT change across a day's variants on any day so far (D18: offset 8512 in the single, TT and
  all 4 Mastery sets while key 0x31/0x34/0x36/0x37 and BR18-00V re-rolled -- the blob length is constant, so layout is stable).
- **Location-as-answer (`hcfg_offset`, D9/D11-D14, D17 on every group)** -- base-10 FILE offset of the first byte of the stored
  blob: base64 form -> the `S` of `SENGR...` (D9 30696, D11 368272, D13 560188 -- the text, not a String header before it); RAW
  form -> the `H` of `HCFG` (D12 82928, D14 4000, D17 207432; D8 Swift 18366768). Record `m.start()` of whichever scan hit validated
  on BOTH paths (D12's raw path once returned `none`).
- **Storage-as-answer (`hcfg_storage`, NEW D17, asked on d08/d09/d11/d12/d13/d14)** -- revised contract: `kind: enum`,
  `accepted_values` [raw, base64, raw_const_array, raw_hcfg_section, wasm_data_segment], rules applied IN ORDER: `base64` if the
  crc-valid HCFG appears only after decoding a printable base64 carrier (d08 Swift, d09 Nim, d11 D, d13 Crystal) ->
  `raw_hcfg_section` if literal `HCFG` starts inside a section named exactly `.hcfg` (d14 ObjC; section headers suffice) ->
  `wasm_data_segment` if inside a WASM data segment -> `raw_const_array` if inside any OTHER native data section (d12 FPC `.data`;
  by the rule also Ada/Go/Rust `.rodata`) -> else `raw`. Rule: take the validated hit's encoding + `section containing its
  file offset` (map offset -> section header; PE/Mach-O the same) and walk the list; jars = base64 (constant-pool literal).
  Unknown future token: read the question's rule list first -- the enum is the answer space.
- **Any other storage encoding -> `lib.binary.hcfg_scan(data, deadline=None)`** (pure stdlib, ~15 ms / 2 MB, ~0.6 s / 67 MB).
  Returns every `HcfgHit` best first; `lib.binary.hcfg_find(data)` = first crc-valid + JSON-parsing hit. Covers raw, base64
  (std/url/wrapped), hex variants, base32/85/a85, UTF-16, reversed, xor'd base64/raw, zlib/gzip/deflate (+ prebuilt multibyte/
  rolling xor, byte maps, custom/rot13 base64, split/int-array/strided, RC4, AES/TEA/ChaCha, stack-built). Offset for other
  encodings = first stored byte -- SPECULATIVE. Kill switch `HCTF_HCFG_SCAN_EXT=0`.
- **xor key / config values** -- re-roll per variant (`BRNN-00V`, `node-00V.dayNN...`, crc, key); derive from the header byte.
- **Container per member** -- ELF vs PE32+ `.exe` re-rolls per member in Mastery: d02 C++ `.exe` (D3-D5, D7, D10, D16), d04 Go
  `.exe`, D10 Zig PE (format `pe`). Labels come from THIS member's header. Dispatch on MAGIC, not extension: `7f454c46` ELF,
  `MZ` PE, `PK` jar, `\0asm` + u32 1 WASM. A re-asked symbol field on a PE member (D17 `mangled_score_symbol`/`typeinfo_symbol`)
  follows the D2 PE convention: COMDAT section name `.text$<mangled>` / `.rdata$<mangled>` (unconfirmed for these two ids).
- **Member qualifier in the id (multi-member group, D15-D16)** -- `dNN_analysis_<qualifier>_<field>` names ONE member by a token of
  its FILE NAME (`-stripped.elf` -> `stripped_*`). Rule: if the group has >= 2 members, peel the longest field prefix that is a
  `[^a-z0-9]+`-separated token of exactly one member name; answer from THAT member. Tags seen: `stripped`/`symbolized`,
  `compact`/`direct`. Fallback: stripped = no `.symtab`; compact = smaller code. D17 backfill asked config ids for the OTHER tag
  too (`d15_stripped_config_mutex/url`, `d16_direct_config_campaign/domain`) -- same blob in both members. `sha256_K` = ARCHIVE
  order (reverse-alphabetical both days): read the zip central directory, never sort names.
- **Variant index per group** -- `dNN--variant-XXX` re-rolls per group and mode; TT often == Mastery set1 bytes but not always
  (D15 TT BR15-005; D16 TT == the single); a carry-over d01 can differ (D9 Mastery `mov eax, 8104`; D15-D16 Mastery set1 d01
  STRIPPED -> symbols/disassembly `[]`, has_symtab `false`). D17 CONFIRMED: TT d01 and all 5 Mastery d01s stripped ->
  `recover_code` = `none` although `kind: integer` (the leaf heuristic's 8114/8106 were rejected). D18: TT + all 4 Mastery d01
  NOT stripped (`8100`) -- stripping is a per-attempt re-roll, not a trend; keep both paths. Pair by sha256, never index.
- **Contract wording per fetch (D17)** -- the SAME id's question text/answer_format changed between the morning and the revised
  contract (exact_text -> enum for hcfg_storage; section_names now "leading \"\" optional"; compression_methods codes OR names;
  format/machine "bitness-qualified labels accepted"). Rule: the solver reads `answer_format` per id at run time
  (`accepted_values` = closed answer set; assert the emitted token is in it); keep the GM-confirmed spelling when both pass.
- **Mastery packaging** -- `setN.` prefixed ids, each set its own `delivery N: evidence.zip`: pair by sha256. From D9 each set's
  1st question ends `Evidence case: dNN-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]` (TT `dNN-tt-...`) = set->delivery map.
- **answer_format.kind for the same field name** -- D8/D15: `elf_class`/`machine` exact_text/pattern on d01 but INTEGER (`64`/`62`)
  on d08/d15 in ONE contract. Rule: dispatch on `kind`, not on the field name.
- **Feature-presence fields** -- `has_<thing>_section` (D10, D14: literal section name `.hcfg`, PE names NUL-padded);
  D17 adds runtime-identity booleans on old groups: `has_go_runtime` (d04: `\xff Go buildinf:` / `.gopclntab` / `runtime.`),
  `has_rust_mangled_symbol` (d05: `_ZN..17h<16hex>E` or `_R` v0 in .symtab), `has_coroutine_runtime` (d07: jar entries under
  `kotlin/coroutines/`), `has_cpp_typeinfo/vtable` (d02, D8). Generic rule: `has_<x>` = a structural marker of <x> in THIS member;
  expect `has_swift_*`/`has_nim_*`/`has_objc_*`/`has_gnat_*`-style ids on the D8-D17 groups next.
- **Field set per old group** -- old groups gain ids over days (D8 padded to 10, D17 to 11 + hcfg_offset/hcfg_version spread to
  every HCFG group). Answer by field name from the parsed facts dict of THAT member; unknown field -> log and fall through.
- **Speed flags (no answer change)** -- per-case timings are usually CPU contention from parallel solver-tests: re-measure with
  `taskset -c 0,1 /usr/bin/time python3 solve.py ...`. Floor = AES-CTR+inflate+sha256 of the 67 MB d08 member (~0.35 s/set); timed
  windows are dominated by DOWNLOAD (D16 TT 52 s of 64 s), not by the solve.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "AES Encrypted" | `7z x -pinfected -y evidence.zip` (Python: `pyzipper`); `sha256sum *` for every `artifact_sha256_K` (K = archive order within the group) |
| `readelf -h -S` hint, ELF header questions | `readelf -hSW`, `readelf -sW`; `readelf -p .huntress` for the custom-section `marker` (D1, re-asked D17) |
| "constant returned by recover_code" / `disassembly` | `objdump -d -M intel --no-show-raw-insn` around `<recover_code>`; capstone on the FUNC symbol's st_value..st_size bytes |
| Stripped C build, no `.symtab` | answer the absence the question defines (`[]`/`none`); only as recon find the leaf `b8 imm32 c3` (`lib.binary.recover_return_constants`) |
| C++ / "mangled" / "vtable" / "RTTI" | `nm -C` / `c++filt`; `_ZTV<class>` (vtable), `_ZTI`/`_ZTS` (typeinfo); `score` method `_ZNK<len><Class>5scoreEPKc`; PE: `objdump -t file.exe` (COMDAT names) |
| `PE32+` MinGW `.exe` | `objdump -t` (COFF symbols + string table), `pefile` (Machine, OPTIONAL_HEADER.Magic, sections incl. `.hcfg`) |
| "CLI metadata", `.dll` + `runtimeconfig.json`, `BSJB` | `ilspycmd file.dll` or Python `dnfile`; config = `<PrivateImplementationDetails>` FieldRVA static array; `BSJB v4.0.30319` |
| Go ("build info, function names, file paths") | `go version -m file`; `lib.binary.go_buildinfo` / `go_pclntab_funcs` (stripped names survive in `.gopclntab`) |
| Rust (mangled `_R`/`_ZN..17h<hash>E`, panic strings) | `readelf -hS` + `HCFG` scan; `rustfilt` / `lib.binary.rustfilt` if symbols are asked |
| `.jar` / "constant pool" / methods / access flags | unzip the jar, `META-INF/MANIFEST.MF` Main-Class, `javap -v -p Main.class` (method table order, `flags: (0x0031)`); `ConstantValue: String` base64 config |
| Kotlin fat jar (`kotlin/`, `X$fn$1 extends ContinuationImpl` with `int label`) | Parse the Main-Class first, skip `kotlin/`/`org/jetbrains/`; coroutine runtime = `kotlin/coroutines/` entries |
| Swift ELF (`swift5_*` sections, `$s<len><Module>` symbols, 60+ MB) | Never eager-parse symbols; regex `SENGR` base64 in `.rodata`; `bin/swift-demangle` |
| Nim / D / Crystal ELF (`NimMain`; `_D4core`,`DMDH`; `Crystal:H`,`GC_malloc`) | Plain ELF; base64 `SENGR...` literal (Nim: two raw `HCFG` decoys -> crc-gate); offset = the `S` |
| Free Pascal ELF (`FPC 3.2.2`, `.fpcdata`, static stripped) | Plain ELF; HCFG RAW in `.data` -- `grep -abo HCFG`, crc-gate, offset = the magic |
| Objective-C ELF (`__objc_selectors`/`__objc_classes`, `objc_msg_lookup`, `._OBJC_CLASS_<Name>`) | Plain ELF; HCFG RAW in its own `.hcfg` section (symbol `huntress_config`); `has_hcfg_section` = `true` |
| Fortran ELF (`libgfortran.so.5` NEEDED, `_gfortran_*` imports, `MAIN__`, `*.f90` FILE symbol, internal procs `name.N`, `jumptable.N.M` = `_gfortran_select_string` case table) | Plain ELF: carried-over solver answers it (`elf`/`x86-64`/`62`). HCFG RAW in `.rodata` (symbol `encoded_config.N`; `grep -abo HCFG`, crc-gate, offset = the `H`). SELECT CASE on `HUNTRESS_HOST_MODEL` -> `mov eax, <event_fn>; call rax` (indirect calls) -- the "flow" theme, unasked |
| Ada ELF (`GNAT Version: 14.2.0`, `ada__*`/`system__*`/`__gnat_*` symbols, `ADA.STRINGS.*_ERROR` names, `.gcc_except_table`, debug_info) | Plain ELF: header ids as usual (`elf`/`x86-64`/`62`). HCFG RAW in `.rodata` (`grep -abo HCFG`, crc-gate, offset = the `H`). The "decoder ring" (reversible xor decoder) was NOT asked; the trace marker JSON (`family":"ada_encoded_config_trace"`) is flavour |
| Two members differing by a name tag (`-stripped`/`-symbolized`, `-compact`/`-direct`), ids `dNN_analysis_<tag>_<field>` | Route each id to the member whose file name carries `<tag>`; same HCFG in both |
| `00 61 73 6d 01 00 00 00` (`\0asm`), `.wasm` | `lib.binary.wasm_layout(data)` or `wasm-objdump -x f.wasm`; format `wasm`, architecture `wasm32`; HCFG RAW in data segment 0 |
| `answer_format.kind: enum` + `accepted_values`, question says "Apply these mutually exclusive rules in order" | The question IS the spec: implement the rules top-down over the parsed facts, emit one listed token (D17 hcfg_storage) |
| Packed / high entropy / `UPX!` | `lib.binary.packer_info` → `upx -d` on a COPY (not seen yet) |
| Real code-reversing question (not seen yet) | `rizin -q -c "aaa; pdf @ sym.<fn>"`; Ghidra headless `lib.binary.ghidra_decompile` (heavy, last resort) |

## Day by day
**D1 "ELF Aware"** (~14 min, 4 wrong): C ELF64 headers, `.huntress`, recover_code. **D2 "Mangled"** (~22 min): C++ ELF/MinGW PE,
first HCFG; PE symbols = COMDAT `.text$<mangled>`. **D3 "Table Manners"** (~1 h 48 min, ~60 wrong): .NET, format `pe_cli` after ~50
synonyms. **D4 "Go Fish"** (1.5 min): `amd64` REJECTED → `x86-64`. **D5 "Rust Belt"** (7 s). **D6 "Pool Party"** (~5 min): jar
constant-pool base64 HCFG. **D7 "Routine Check"** (3 min): Kotlin fat jar. **D8 "Swift Justice"**: 67 MB Swift; backfill #1 to 10
ids/group; integer elf_class/machine. **D9 "Nimble"** (86 s): raw decoys, NEW `hcfg_offset`. **D10 "Zig Zag"** (33 s): NEW
`has_hcfg_section`. **D11 "D-Day"** (36 s). **D12 "Pascal's Wager"** (54 s): HCFG RAW. **D13 "Crystal Clear"** (14 s). **D14
"Selective Memory"** (9 s): ObjC, `.hcfg`. **D15 "Stripped"** (74 s): stripped/symbolized pair, `<qualifier>_` ids. **D16 "Wasm
Up"** (91 s, 0 wrong, TT+Mastery first try): compact/direct wasm pair; labels `wasm`/`wasm32` first try thanks to the prebuilt
`wasm_layout`; HCFG RAW in data segment 0; "doors" theme unasked.

**D17 "Decoder Ring"** (204 Qs; CORRECT T+4:03; TT 2nd try, Mastery after 5 per-set fixes): ONE Ada ELF (GNAT 14.2), HCFG RAW
in `.rodata`; decoder never asked. Carry-over + d17 ids banked at T+18 s with zero new code. Backfill #2 (32 ids on old groups,
10 needed code, all accepted in ONE POST). `hcfg_storage` raw ids (d12/d14) burned ~10.9k rejected POSTs / 3.5 h until the
organizers revised the contract to an enum (`raw_const_array` / `raw_hcfg_section`). TT/Mastery d01 stripped -> `recover_code`
`none` (the leaf heuristic 8114/8106 was rejected: a re-asked field must inherit its family's absence rule).

**D18 "Flow State"** (slug `control-flow-reconstruction`; 216 Qs; **CORRECT at T+11 s**, 0 wrong; TT and Mastery CORRECT first
try). Prompt: "Follow the calls ... Reconstruct the call graph, read the API intent at each edge, and prove no injection hides in
the flow." New group = ONE Fortran ELF (16.5 KB, gfortran, dynamic `libgfortran.so.5`/libm/libgcc_s, not stripped): `main` ->
`MAIN__` -> `_gfortran_get_environment_variable_i4("HUNTRESS_HOST_MODEL")` -> `_gfortran_select_string` over the case table
`jumptable.0.5` (default + `analysis`/`sandbox`/`workstation`) -> `mov eax, <event_decoy|sandbox|failure|success>; call rax`
(indirect calls to the internal procedures `event_*.N`) -> xor-sum guard over `encoded_config.4` vs 9999 (`unreachable`) ->
`_gfortran_st_write` of the trace JSON (`fortran_indirect_flow_trace`, `modeled_process_access_no_injection`). HCFG RAW at
`.rodata` file offset 8512 (= symbol `encoded_config.4`), ver 1, key 0x31.
- Contract = the D17 204 ids unchanged + 12 d18 ids (sha256, architecture, format, machine, config_*, crc32_hex, hcfg_offset,
  hcfg_version, xor_key_hex) -- no backfill, no new field name, call-graph/API/injection theme unasked.
- The race harness (answer-first) POSTed the carried-over solver's full 216-answer set at T+11 s: zero code, zero lookups. The
  `fortran-gfortran-member` prebuild (built the night before from the D17 forecast) had already put the cues in place.
- TT window 80 s, done in 8 s (download 4 s, solve 0.9 s); Mastery (4 sets) window 265 s, done in 14 s (download 7.5 s, solve 1.4 s).

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class (`kind` exact_text) | `ELF64` / `ELF32` (readelf style) | ELFCLASS64 |
| elf_class (`kind: integer`, D8) | the bit width `64` / `32` | `2` / `1` (raw EI_CLASS byte) |
| machine (`kind: integer`, D8-D9, D15) | decimal e_machine (`62` = x86-64) | — |
| endianness | `little` / `big` | little endian, lsb, msb |
| machine (ELF) | `x86-64`, `x86`, `AArch64`, `ARM` | EM_X86_64, x86_64, amd64 |
| machine (PE FILE_HEADER) | 0x14c → `i386`; 0x8664 → `x86-64` | x86 (for PE i386); raw `0x8664` |
| architecture | the same machine words (Go amd64 → `x86-64`) | amd64, arm64, 386, x86_64 |
| elf_type | `ET_EXEC` / `ET_DYN` | EXEC |
| entry_point, crc32_hex, xor_key_hex | lowercase hex with `0x` (crc `0x%08x`, key `0x%02x`) | — |
| recover_code (`kind: integer`) | base-10 integer (`mov eax, 0x1fa4` → 8100); `none` if the symbol is absent (stripped d01, D17 TT+Mastery CONFIRMED) | the stripped/renamed leaf's constant (8114, 8106) |
| has_symtab / has_cpp_* / has_go_runtime / has_rust_mangled_symbol / has_coroutine_runtime | enum `true`/`false` | — |
| marker | exact `.huntress` string without the NUL; `none` if the section is missing | — |
| format (native) | lowercase container: `elf`, `pe` (`macho` presumed) | ELF, ELF64, elf64-x86-64, HCFG, json, exe, pe32+, coff, mz |
| format (.NET) | `pe_cli` | ~50 synonyms — lib/knowledge.py DOTNET_FORMAT_REJECTED |
| format (Java/Kotlin jar) | `jar` | jar_jvm |
| format / architecture (any compiled language ELF, D8-D18 incl. Ada, Fortran) | `elf` / `x86-64` (language never changes the label) | — |
| format / architecture (WebAssembly, D16) | `wasm` / `wasm32` | — |
| C++ symbols (ELF) incl. `mangled_score_symbol`, `typeinfo_symbol` (D17) | bare Itanium mangled name (`_ZNK15DiscoveryEngine5scoreEPKc`, `_ZTI15DiscoveryEngine`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` / `.rdata$<mangled>` | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` (D17 revised text: omitting it also accepted) | list without "" |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates | hex imm, `"ret "` |
| methods (jar, JSON, D17) | Main-Class `method_info` names in class-file table order incl. `<init>`, compact JSON | — |
| access_flags (jar, integer, D17) | ClassFile `access_flags` in decimal (`49` = PUBLIC\|FINAL\|SUPER) | — |
| method_count (jar, integer, D17) | number of `method_info` entries of the Main-Class incl. `<init>`/`<clinit>` (`7`) | — |
| metadata_version | BSJB root string `v4.0.30319` | net8.0 / TFM |
| config_* | values verbatim from the decoded HCFG JSON (mutex keeps ONE backslash) | JSON-escaped `\\` |
| hcfg_version / xor_key_hex | header byte 4 decimal / header byte 5 as `0x%02x` | — |
| has_hcfg_section (enum) | `true` when a section is literally named `.hcfg` | — |
| hcfg_offset (integer) | decimal FILE offset: base64 text start (`S`), RAW = the `HCFG` magic | — |
| hcfg_storage (enum, D17 revised contract; re-confirmed D18 single/TT/Mastery) | `base64` (SENGR literal), `raw_hcfg_section` (in a `.hcfg` section), `raw_const_array` (other native data section, e.g. FPC `.data`), `wasm_data_segment`, `raw` (else) | every free-text spelling for raw-stored (raw, raw_data, section, .hcfg, bytes, blob, ... ~10.9k probes) -- the token set is closed |
| compression_methods (jar, json) | sorted distinct ZIP method ids, compact: `[0,8]` (D17 text: Stored/Deflate names, any order also accepted) | — |
Naming law (from playbook.py): native format = container only; a managed .NET binary = container_runtime (pe+cli).
Java broke the compound law (`jar`), so when a label is new, try the plain container name AND the compound, one per POST.

## Pitfalls that cost time
- **A synthetic label with no derivable spelling** (D3 .NET format ~1.5 h; D17 raw `hcfg_storage`, ~10.9k POSTs over 3.5 h,
  NEVER guessed -- solved only by the organizers' contract revision to an enum): stop after ~10 single-id probes plus one `hctf
  labels` run, write HELP.md, then RE-PULL THE CONTRACT periodically and diff each id's question/answer_format. Never put the
  unknown id into a batch with other open ids; mass automated grouptests on an exact_text label are wasted POSTs.
- **Absence rule, always** (D1 TT, D2 Mastery set2, D8/D15-D17 Mastery d01 stripped/renamed): answer what the question defines for
  absence (`[]`, `none`, `false`); a re-asked field inherits it (D17 `recover_code` leaf heuristic 8114/8106 was rejected).
- **A multi-field POST is all-or-nothing.** One wrong field fails the set and hides which field was wrong (D2). Submit
  unconfirmed/new fields ALONE; batch only the known ones (D17: 10 new derivable fields in one POST was fine -- all bytes-derived).
- **Chasing the prompt's theme** (D5-D18): the NEW day's flavour has never been asked (D18's call graph / "prove no injection"
  included); read the contract ids first. But keep the facts you learn about each language/theme: a later backfill re-asks old
  days' facts (D17 re-asked D1/D2/D4-D7), so record the theme facts in NOTES.md for the backfill day.
- **Formatting**: build submit JSON with python/jq (`Global\Huntress...` mutex = ONE backslash); capstone `ret` has an empty
  op_str (`"ret "` -> strip), immediates in decimal.
- **Cumulative zip**: old groups' answers carry over when their sha256 match; POST the known ids first (they bank as
  `accepted`), then the new/unknown ids alone (D15: 140 banked at T+17 s; D17: 188 at T+18 s; D18 all 216 at T+11 s).
- **Id shape / kind**: peel a member qualifier off the front before declaring a field unknown (D15 `analysis_stripped_machine`);
  the same field name can change `kind` (D8 elf_class/machine integer) -- read `answer_format.kind` per id.
- **Archives**: never unzip recursively (nested .jar/.apk lose their `dNN--` prefix); jar members are deflated, so `grep HCFG
  file.jar` finds nothing -- inflate the class and read constant-pool strings.
- **Huge members** (D8: 67 MB Swift): no per-key xor brute force or per-field re-parse; cheap encodings first, crc-gate every hit,
  parse each member once.
- **Decoy magics** (D9 Nim): code that CHECKS the magic embeds `"HCFG"` literals; len 0 => crc32(b"")==0 passes! Require non-empty
  JSON that parses, keep scanning, then try the base64 form.
- **Location fields per scan path** (D12): a decoder with raw AND base64 branches must return the hit offset (and the hit's
  encoding for `hcfg_storage`) from BOTH; take offsets from `grep -abo` / `re.finditer().start()`, not `strings -t d` (off by 1).
- **Timed windows**: download dominates (D16 TT 52 s of 64 s on the 32 MB bundle). After editing hctf/*.py, restart the
  orchestrator (D1/D2 ran stale modules).
- **WASM parsing**: section sizes are 5-byte PADDED LEB128; read LEB128 generically (`lib.binary.wasm_layout`).
- **PE machine map must include 0x8664 → `x86-64`**: a from-scratch replay once emitted `0x8664` and failed TT twice.
