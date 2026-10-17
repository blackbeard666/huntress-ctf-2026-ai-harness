# binary-reverse-engineering — technique log (days 1-16; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- One `evidence.zip` (AES, password `infected`). From Day 3 on it is CUMULATIVE: members `dNN--variant-XXX.<ext>`, one group per
  past day, plus ONE new container/language per day: D1 C ELF, D2 C++ (ELF or MinGW PE32+), D3 .NET dll (+runtimeconfig.json),
  D4 static stripped Go ELF, D5 static Rust ELF (debug_info), D6 Java .jar, D7 Kotlin fat .jar (5 MB, ~3300 entries), D8 Swift ELF
  (67 MB, static stdlib+Foundation+ICU, not stripped), D9 Nim ELF (60 KB, dynamic glibc, not stripped), D10 Zig ELF (134 KB,
  dynamic glibc, stripped, clang/LLD 19 zig-bootstrap in `.comment`) -- a Zig PE `.exe` in Mastery set2, D11 D-language ELF (1 MB,
  DMD, druntime static + dynamic glibc, not stripped, debug_info), D12 Free Pascal ELF (100 KB, FPC 3.2.2, static, stripped), D13
  Crystal ELF (749 KB, dynamic glibc + libgc, not stripped), D14 Objective-C ELF (17 KB, GNUstep libobjc ABI, dynamic, not stripped),
  D15 a PAIR of C ELFs from one source (`dNN--variant-XXX-stripped.elf` 14 KB + `-symbolized.elf` 16 KB, identical `.text`/`.hcfg`),
  D16 a PAIR of WebAssembly modules from one source (`-compact.wasm` 561 B / `-direct.wasm` 570 B: same data, different code) --
  the first NON-native container since D7 (format `wasm`, architecture `wasm32`). From D15 on the twist is "one source, two builds".
  Answer ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`; a multi-member group adds a member qualifier:
  `dNN_analysis_<qualifier>_<field>` (D15 `stripped_`/`symbolized_`, D16 `compact_`/`direct_`).
- From Day 2 on, every new-day member carries the same embedded **HCFG** config blob: `'HCFG' | u8 ver | u8 xor_key | u16 len (LE) |
  u32 crc32 | xor'd JSON` (JSON at offset 12; crc32 is over the decoded plaintext). Only its storage location changes
  (`.hcfg` section on D2/D10/D14, .NET FieldRVA array, Go/Rust rodata, base64'd in a Java/Kotlin constant pool, base64 Swift/Nim/D/
  Crystal String literal in `.rodata` on D8/D9/D11/D13, RAW in FPC `.data` on D12, RAW in WASM data segment 0 on D16). Scan raw bytes for `HCFG` AND for its base64
  form `SENGR...` (raw `HCFG` can also be a false hit inside code: check crc).
  The JSON also carries never-asked keys (ipv4, windows_path, linux_path, service, host_model on D7): parse the whole dict so a new `config_<key>` id is free.
- The analysis is easy (headers, symbols, one config blob). The hard part is the GM's exact label for a few `exact_text` fields (format,
  machine, disassembly, symbol). The question set grows +10/day from D8 (80 → 90 → ... → 160 on D16); old groups reuse the same
  bytes, but D8 BACKFILLED old groups to 10 ids each (new: has_symtab, has_cpp_typeinfo/vtable, xor_key_hex, hcfg_version, compression_methods).
- **The prompt's language theme has NOT been asked since D4** (Rust panics, Kotlin "state machine", Swift "protocols", Nim
  "runtime fingerprints", D "templates", Pascal "record layouts", Crystal "DNS labels", ObjC "classes/selectors/persistence
  descriptor", D15 "calling conventions", D16 wasm "imports, memory, indirect calls"). The new group gets sha256, format, architecture, machine, config_campaign/domain/mutex/url/crc32_hex + ONE
  rotating extra id from a small pool: hcfg_version (D6-D7), `hcfg_offset` (D9, D11-D13), `has_hcfg_section` (D10, D14),
  elf_class/machine as INTEGERS (D8-D9, D15 `machine` = `62`). D11-D16 introduced NO never-seen field NAME (D15/D16 novelty =
  the qualifier prefix and a new container LABEL, not a field): grep the new group's ids against the solver's
  field table before anything else; if all are known, run the carried-over solver and submit.
- Time Trial ≈ 6-16 s early; Mastery = `setN.` prefixed copies, 2 sets through D7, 5 sets / 400-450 ids on D8-D9, 3 sets / 300-420
  ids on D10-D14, 5 sets / 750 ids on D15, 5 sets / 800 ids on D16 (TT 30 s; D13 TT 80 s / Mastery 200 s; D14 both 30 s); artifacts are named
  `delivery N: evidence.zip`.
- **D10 RELAXED the label fields**: 36 ids are now `kind: pattern` whose syntax ACCEPTS equivalents (format: "ELF or PE; case,
  ELF32/ELF64/PE32/PE32+ accepted"; machine/architecture: "standard tool or symbolic label, or decimal/hex code"; e_type and
  endianness: symbolic constant / readelf label / numeric code; .NET format: any container_runtime token with CLI/CLR/.NET). D8-D9's
  integer machine became pattern. Keep emitting the GM-confirmed spellings; the old REJECTED lists may be stale for pattern ids.
  (D14: `dNN_analysis_format` is still `exact_text` -> `elf`.)

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, different storage per container (`.hcfg` section, .NET FieldRVA, Go/Rust rodata,
  base64 inside a Java/Kotlin constant pool, base64 Swift/Nim/D/Crystal string literal in ELF `.rodata`, raw FPC `.data`, RAW as the
  first payload byte of WASM active data segment 0 (`i32.const 1024`; file 116/125, D16)): scan raw
  bytes for `HCFG` and for `SENGR[A-Za-z0-9+/_-]*=*` (base64 of `HCFG`, std or urlsafe), decode, accept only if crc32(plain)
  matches AND the JSON parses -- keep scanning past a failing hit (D9 Nim had two raw `HCFG` decoys); never a fixed offset.
  Storage did NOT change across a day's variants on any day so far (D14 `.hcfg` at file 0xfa0 in single/TT/all 3 sets).
- **Location-as-answer (`hcfg_offset`, D9/D11-D13)** -- base-10 FILE offset of the first byte of the stored blob as it sits in
  the member: base64 form -> the `S` of `SENGR...` (D9 Nim 30696, D11 D 368272, D13 Crystal 560188 -- the text, not the String
  header 12 B before it); RAW form -> the `H` of `HCFG` (D12 FPC 82928). Constant across a day's variants although shas differ --
  still compute it: record `m.start()` of whichever scan hit (raw OR base64) validated, on BOTH paths (D12's raw path returned `none`).
- **Any other storage encoding -> `lib.binary.hcfg_scan(data, deadline=None)`** (pure stdlib, ~15 ms / 2 MB, ~0.6 s / 67 MB).
  Returns every `HcfgHit` (offset, encoding, version, key, length, crc, crc_ok, config, plain, speculative, detail) best first;
  take `lib.binary.hcfg_find(data)` (first crc-valid + JSON-parsing hit). Covers raw, base64 (std/url/wrapped), hex (plain, `48 43`,
  `48:43`, `\x48`, `0x48, `), base32, base85, ascii85, UTF-16LE/BE of those, reversed raw/base64, single-byte xor'd base64/raw,
  zlib, gzip, raw deflate (+ prebuilt multibyte/rolling xor, byte maps, custom/rot13 base64, split/int-array/strided, RC4, AES/TEA/
  ChaCha, stack-built). Decoys come back `valid=False`. `hcfg_offset` per encoding: raw = the `H` (GM D12), base64 = the `S` (GM
  D9/D11/D13); every other encoding = first stored byte/char (`<` of `<~`, BE UTF-16 its `00`, lowest offset of a reversed region)
  -- SPECULATIVE: if rejected, try the container header in front of the stored form. Kill switch `HCTF_HCFG_SCAN_EXT=0`.
- **xor key / config values** -- re-roll per variant (`BRNN-00V`, `node-00V.dayNN...`, crc); derive from the header byte, never
  from the sample. D13 key = 0x91+N; D14 single BR14-000 key 0xa1, TT BR14-002, Mastery BR14-002/007/004.
- **Container per member** -- ELF vs PE32+ `.exe` re-rolls per member: Mastery set2 had d02 C++ as `.exe` (D3-D5, D7, D10) and d04
  Go as `.exe` (D4, D5, D7, D10); D10 set2 had the NEW d10 Zig member as a PE too (format `pe`). Labels come from the header of
  THIS member (Go PE: format `pe`, architecture `x86-64` from Machine). Dispatch on MAGIC, not extension: `7f454c46` ELF, `MZ`
  PE, `PK` jar, `\0asm` + u32 version 1 WASM (D16: `wasm`/`wasm32`; `wasm64` only if a memory has limits flag 0x04 -- unconfirmed).
- **Member qualifier in the id (multi-member group, D15-D16)** -- `dNN_analysis_<qualifier>_<field>` names ONE member of the day's
  group by a token of its FILE NAME (`d15--variant-000-stripped.elf` -> `stripped_*`, `-symbolized.elf` -> `symbolized_*`). Rule:
  if the group has >= 2 members, split the field at the first `_`; if that token (not `variant`/`elf`/`has`/`hcfg`/`config`/
  digits...) is a `[^a-z0-9]+`-separated token of exactly one member name, answer `<field>` from THAT member only. Tags seen:
  `stripped`/`symbolized` (D15), `compact`/`direct` (D16, two codegens of one wasm function: `select` chain vs nested
  `if/else`, identical data section). Fallback if names stop carrying the tag: stripped = no `.symtab`; compact = the smaller
  file / shorter code section. Config ids were asked only for ONE tag (D15 `stripped_`, D16 `compact_` -- both times the
  alphabetically-first tag; the blob is identical in both members anyway). `sha256_K` = ARCHIVE order, which was reverse-
  alphabetical both days (symbolized, stripped; direct, compact): read the zip central directory, never sort names. Grep new ids for an
  unknown first token after `dNN_analysis_` before declaring a field unknown (pre-D15 groups were only indexed by `sha256_K`).
- **Variant index per group** -- `dNN--variant-XXX` re-rolls per group and mode; sizes and config values change, names/layout
  don't. TT often == Mastery set1 bytes (D7, D9, D14: TT and set1 both BR14-002) but not always (D15: TT BR15-005, Mastery
  BR15-004/003/002/001/000 -- set5 == the single; D16: TT == the single BR16-000, Mastery BR16-001..005); a
  carry-over d01 can differ (D9 Mastery d01 `mov eax, 8104`; D15-D16 Mastery set1 d01 STRIPPED -> symbols/disassembly `[]`,
  has_symtab `false`; set1 d02 a PE). Pair by sha256, never index.
- **Mastery packaging** -- `setN.` prefixed ids, each set its own `delivery N: evidence.zip` (same filename): pair by sha256.
  Set count re-rolls: 2 (D2-D7), 5 (D8-D9), 3 (D10-D14), 5 (D15-D16): loop over every `setN.`. From D9 each set's 1st question ends
  `Evidence case: dNN-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]` (TT: `dNN-tt-...`): an explicit set -> delivery map;
  it is question TEXT, never part of an answer.
- **answer_format.kind for the same field name** -- D8: `d01_analysis_elf_class`/`machine` exact_text (`ELF64`/`x86-64`) and
  `d08_analysis_elf_class`/`machine` integer (`64`/`62`) in ONE contract; D15 again: `d15_analysis_*_machine` integer `62` while
  `d01_analysis_machine` is pattern `x86-64`. Rule: dispatch on `kind`, not on the field name.
- **Feature-presence fields** -- `has_<thing>_section` (D10 Zig, D14 ObjC: enum `true`) for ELF AND PE: answer from the member's
  section-name table (`.hcfg` literally; PE names are 8-byte NUL-padded), generic over `<thing>` (regex `has_(\w+?)_section`).
  Don't confuse with the many `__objc_*` sections on D14 -- only the literal name counts.
- **Field set per old group** -- old groups gain ids over days (D8 padded every group to 10). Answer by field name from the
  parsed facts dict of THAT member; an unknown field must log and fall through, never crash.
- **Speed flags (no answer change)** -- per-case timings ("4.11 s on single_solve") are usually CPU contention from parallel
  solver-tests: re-measure with `taskset -c 0,1 /usr/bin/time python3 solve.py ...` first. Floor = AES-CTR+inflate+sha256 of the
  67 MB d08 member (~0.35 s/set); the timed windows are dominated by DOWNLOAD (D16 TT 52 s of 64 s), not by the solve.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "AES Encrypted" | `7z x -pinfected -y evidence.zip` (Python: `pyzipper`); `sha256sum *` for every `artifact_sha256_K` (K = archive order within the group) |
| `readelf -h -S` hint, ELF header questions | `readelf -hSW`, `readelf -sW`; `readelf -x .huntress` / `readelf -p .huntress` for the custom-section marker |
| "constant returned by recover_code" / `disassembly` | `objdump -d -M intel --no-show-raw-insn` around `<recover_code>`; capstone on the FUNC symbol's st_value..st_size bytes |
| Stripped C build, no `.symtab` | answer the absence the question defines (`[]`/`none`); only as recon find the leaf `b8 imm32 c3` (`lib.binary.recover_return_constants`) |
| C++ / "mangled" / "vtable" / "RTTI" | `nm -C` / `c++filt`; `_ZTV<class>` (vtable), `_ZTI`/`_ZTS` (typeinfo); the PE COFF symtab: `objdump -t file.exe` |
| `PE32+` MinGW `.exe` | `objdump -t` (COFF symbols + string table), `pefile` (Machine, OPTIONAL_HEADER.Magic, sections incl. `.hcfg`) |
| "CLI metadata", `.dll` + `runtimeconfig.json`, `BSJB` | `ilspycmd file.dll` or Python `dnfile`; config = `<PrivateImplementationDetails>` FieldRVA static array; `BSJB v4.0.30319` |
| Go ("build info, function names, file paths") | `go version -m file`; `lib.binary.go_buildinfo` / `go_pclntab_funcs` (stripped names survive in `.gopclntab`) |
| Rust (mangled `_R`/`_ZN..17h<hash>E`, panic strings) | `readelf -hS` + `HCFG` scan was enough on D5; `rustfilt` / `lib.binary.rustfilt` if symbols are asked |
| `.jar` / "constant pool" | unzip the jar, `META-INF/MANIFEST.MF` Main-Class, `javap -v -p Main.class`; `ConstantValue: String` base64 config |
| Kotlin fat jar (`kotlin/`, `X$fn$1 extends ContinuationImpl` with `int label`) | Parse the Main-Class first, skip `kotlin/`/`org/jetbrains/`. Coroutine "state machine" = `invokeSuspend` switching on `label` |
| Swift ELF (`swift5_*` sections, `$s<len><Module>` symbols, 60+ MB static stdlib) | Never eager-parse symbols; regex `SENGR` base64 in `.rodata` (getter: `movabs rax,0xd0000000000001fc` → chars at X+0x20); `bin/swift-demangle` |
| Nim ELF (`NimMain`, `TM__<hash>_N`, `<proc>__<mod>_u<N>`, `fatal.nim`) | Plain ELF; config literal = `u64 cap\|0x40..` then chars (text = X+8); two raw `HCFG` decoys -> regex `SENGR`, crc-gate |
| D ELF (`_D<len><module>...`, `_D2rt`/`_D4core`, `DMDH`) | Plain ELF; `decodeConfig()` returns a NUL-terminated base64 `SENGR...` literal in `.rodata` |
| Free Pascal ELF (`FPC 3.2.2 ... x86_64 - Linux`, `.fpcdata`, static stripped) | Plain ELF; HCFG RAW in `.data` -- `grep -abo HCFG`, crc-gate, offset = the magic |
| Crystal ELF (`Crystal:H`, Boehm `GC_malloc`, `*crystal*` symbols) | Plain ELF; base64 `SENGR...` String literal behind a 12-byte header (`type_id=1, bytesize, length`); offset = the `S` |
| Objective-C ELF (`__objc_selectors`/`__objc_classes`/`__objc_cats`/`__objc_protocols` sections, `objc_msg_lookup_super`/`__objc_load` imports = GNUstep libobjc, `._OBJC_CLASS_<Name>`, `_i_<Class>__<sel>_` method symbols) | Plain ELF: readelf header ids as usual. HCFG RAW in its own `.hcfg` PROGBITS section (`readelf -x .hcfg`); `has_hcfg_section` = `true`. The ObjC class/selector "persistence descriptor" (`TriggerDescriptor initWithTrigger:`) was flavour, unasked. If ObjC metadata is ever asked: `readelf -sW \| grep -E '_OBJC_CLASS_\|objc_sel_name_'` |
| Two members of one day differing by a name tag (`-stripped.elf` / `-symbolized.elf`, D15), ids `dNN_analysis_<tag>_<field>` | Same header ids per member; route each id to the member whose file name carries `<tag>` (fallback: `.symtab` absent = stripped). HCFG RAW in `.hcfg` (`grep -abo HCFG`, crc-gate) in both. The prompt's "reconstruct the stripped functions / calling conventions" was NOT asked |
| `00 61 73 6d 01 00 00 00` (`\0asm`), `.wasm`, ids `dNN_analysis_<tag>_format/architecture` (D16) | `lib.binary.wasm_layout(data)` (sections, memories, data_segments with file + memory offsets; handles 5-byte padded LEB128) or `wasm-objdump -x f.wasm` / `wasm2wat f.wasm` (wabt installed); format `wasm`, architecture `wasm32`. HCFG RAW in data segment 0 (`grep -abo HCFG`, crc-gate); segment 1 = a NUL-terminated `huntress.binary.dynamic_trace.v1.sandboxed_module_inventory` marker (unasked). D16 module had NO import/table/elem section despite the "imports, indirect calls" prompt |
| Packed / high entropy / `UPX!` | `lib.binary.packer_info` → `upx -d` on a COPY (not seen yet) |
| Real code-reversing question (not seen yet) | `rizin -q -c "aaa; pdf @ sym.<fn>"`; Ghidra headless `lib.binary.ghidra_decompile` (heavy, last resort) |

## Day by day
**D1 "ELF Aware"** (~14 min, 4 wrong): C ELF64 headers, `.huntress`, recover_code; spellings by rejection. **D2 "Mangled"** (~22 min,
5 wrong): C++ ELF/MinGW PE, first HCFG; PE symbols = COMDAT `.text$<mangled>` (hidden for hours by all-or-nothing POSTs).
**D3 "Table Manners"** (~1 h 48 min, ~60 wrong): .NET dll, FieldRVA HCFG, format `pe_cli` after ~50 synonyms. **D4 "Go Fish"**
(1.5 min): stripped Go, `amd64` REJECTED → `x86-64`. **D5 "Rust Belt"** (7 s). **D6 "Pool Party"** (~5 min, 1 wrong): jar
constant-pool base64 HCFG, `jar`; keep nested jars whole. **D7 "Routine Check"** (3 min): Kotlin fat jar, scan Main-Class first.
**D8 "Swift Justice"**: 67 MB Swift; old groups backfilled to 10 ids; integer elf_class/machine `64`/`62`; eager symbol parsing
and xor brute force cost 60 s+; Mastery d01 STRIPPED → `[]`/`false`. **D9 "Nimble"** (86 s): two raw `HCFG` decoys, base64 blob,
NEW `hcfg_offset`. **D10 "Zig Zag"** (33 s): `.hcfg` section, NEW `has_hcfg_section`; Mastery Zig PE. **D11 "D-Day"** (36 s).
**D12 "Pascal's Wager"** (54 s, 2 wrong): HCFG RAW, raw-scan branch lacked its offset → bisect POSTs. **D13 "Crystal Clear"** (14 s).
**D14 "Selective Memory"** (9 s, carried-over solver): GNUstep ObjC ELF, HCFG RAW in `.hcfg` → `has_hcfg_section` `true`.
**D15 "Stripped"** (74 s, 0 wrong): stripped + symbolized C ELF pair, identical `.text`/`.hcfg`; only novelty = the `<qualifier>_`
inside the field name (file-name token → member router, `.symtab` fallback); `machine` integer `62`. Mastery 5 sets 9.35 s.

**D16 "Wasm Up"** (internal slug `webassembly-optimization-equivalence`; 160 Qs; GM CORRECT 91 s after start, 0 wrong POSTs;
TT + Mastery first try). Prompt: "WebAssembly runs in a sandbox, but the sandbox has doors: imports, memory, indirect calls. Map
every door in this module and inventory what passes through." New group = TWO wasm MVP modules from one source:
`d16--variant-000-compact.wasm` (561 B) and `-direct.wasm` (570 B). Sections type/function/memory(min 1)/export(`memory`,
`evaluate`)/code/data, LLVM-style 5-byte padded LEB128 sizes; ONE function `evaluate(i32)->i32` mapping 0/1/2 to constants --
compact = `select` chain, direct = nested `if/else` (the "optimization equivalence"). NO import, table or element section.
Data seg 0 (mem 1024) = RAW HCFG (`01 c1` = ver 1, key 0xc1), seg 1 (mem 2048) = trace-marker string.
- d16 ids: `sha256_1`/`_2` (archive order: direct, compact), `compact_`/`direct_` × format `wasm` + architecture `wasm32` (both
  `exact_text`), `compact_config_campaign/domain/mutex/url` only. No machine/hcfg_offset/import/export/table id.
- How it went: race-harness POSTs banked the 150 old ids at T+25 s and the shas + configs at T+27 s (generic qualifier router +
  raw HCFG scan already worked on wasm bytes); the worker added a 6-line `\0asm` branch to the solver's container dispatch that
  calls the prebuilt `lib.binary.wasm_layout` (format `wasm`, machine `wasm32`), and the 4 label ids went CORRECT on the
  first try at T+91 s. The prebuild (`wasm-hcfg-data-segment`) paid for itself: no label guessing. The "doors" theme was NOT
  asked (12th day the theme is decoration); a later day may ask `imports`/`exports`/`memory_min`/`has_table` style ids.
- TT correct, 64 s in-window of which download 52 s (bundle 32 MB; the solve was 7.6 s); Mastery 5 sets / 800 ids, 23 s in-window
  (download 14.6 s, solve 2.9 s); Mastery set1 d01 STRIPPED again, set1 d02 a PE.

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class (`kind` exact_text) | `ELF64` / `ELF32` (readelf style) | ELFCLASS64 |
| elf_class (`kind: integer`, D8) | the bit width `64` / `32` | `2` / `1` (raw EI_CLASS byte) |
| machine (`kind: integer`, D8-D9, D15) | decimal e_machine (`62` = x86-64; u16 at offset 18 in EI_DATA order) | — |
| endianness | `little` / `big` | little endian, lsb, msb |
| machine (ELF) | `x86-64`, `x86`, `AArch64`, `ARM` | EM_X86_64, x86_64, amd64 |
| machine (PE FILE_HEADER) | 0x14c → `i386`; 0x8664 → `x86-64` | x86 (for PE i386); raw `0x8664` |
| architecture | the same machine words (Go ELF amd64 → `x86-64`; Go PE 0x8664 → `x86-64`) | amd64, arm64, 386, x86_64 |
| elf_type | the constant `ET_EXEC` / `ET_DYN` | EXEC |
| entry_point, crc32_hex, xor_key_hex | lowercase hex with `0x` (crc `0x%08x`, key `0x%02x`) | — |
| recover_code | base-10 integer (`mov eax, 0x1fa4` → 8100); `none` if the named function is absent and the format allows it | the renamed function's constant |
| has_symtab / has_cpp_* | enum `true`/`false` | — |
| marker | exact `.huntress` string without the NUL; `none` if the section is missing | — |
| format (native) | lowercase container: `elf`, `pe` (`macho` presumed) | ELF, ELF64, elf64-x86-64, HCFG, json, exe, pe32+, coff, mz |
| format (.NET) | `pe_cli` | ~50 synonyms — lib/knowledge.py DOTNET_FORMAT_REJECTED |
| format (Java/Kotlin jar) | `jar` (D6 Java, D7 Kotlin) | jar_jvm |
| format / architecture (Swift, Nim, Zig, D, FPC, Crystal, ObjC ELF, stripped/symbolized C pair; D8-D15) | `elf` / `x86-64` (source language never changes the container label) | — |
| format / architecture (WebAssembly module, D16, exact_text) | `wasm` / `wasm32` (lowercase; first try) | — (not tried: WebAssembly, wasm-mvp, wasm32-unknown) |
| C++ symbols (ELF) | bare Itanium mangled name (`_ZNK...`, `_ZTV...`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` (function), `.rdata$<mangled>` (vtable) | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` | list without "" |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates | hex imm, `"ret "`, `mov eax,0x..` |
| metadata_version | BSJB root string `v4.0.30319` | net8.0 / TFM / assembly version |
| config_* | values verbatim from the decoded HCFG JSON (mutex keeps ONE backslash) | JSON-escaped `\\` |
| hcfg_version | header byte 4 as a decimal integer | — |
| has_hcfg_section (D10, D14, enum) | `true` when a section is literally named `.hcfg` (Zig ELF/PE, ObjC ELF) | — |
| hcfg_offset (`kind: integer`, D9, D11-D13) | decimal FILE offset of the stored blob's first byte: base64 text start (`30696`, `368272`, `560188`), RAW = the `HCFG` magic (`82928`) | — (not tried: VA, struct start, `strings -t d` offset-1) |
| xor_key_hex | HCFG header byte 5 as `0x%02x` | — |
| compression_methods (jar, `kind: json`) | sorted distinct ZIP `compress_type` ids, compact: `[0,8]` | — |
Naming law (from playbook.py): native format = container only; a managed .NET binary = container_runtime from the spec tokens (pe+cli).
Java broke the compound law (`jar`), so when a label is new, try the plain container name AND the compound, one per POST.

## Pitfalls that cost time
- **A multi-field POST is all-or-nothing.** One wrong field fails the set and hides which field was wrong (D2: correct `pe` looked
  rejected for hours). Submit unconfirmed/new fields ALONE; batch only the known ones.
- **Guessing synonyms for a synthetic label** (D3 .NET format: ~50 tries, ~1.5 h). Derive from spec tokens and the playbook naming laws,
  use `hctf labels`, and read the question `syntax` first: the GM embeds hints.
- **Chasing the prompt's theme** (D5-D16): the flavour (selectors, protocols, coroutines, record layouts, D15 "calling conventions",
  D16 wasm "imports, memory, indirect calls") has never been asked since D4. Read the contract ids first; reverse only what an id asks for.
- **Shell/JSON quoting** of `Global\Huntress...` mutexes: build the submit JSON with python/jq, not by hand in a shell string.
- **capstone `ret` has an empty op_str**: `f"{m} {o}"` gives `"ret "`. Strip it, and convert immediates to decimal.
- **Cumulative zip**: old groups' answers carry over when their sha256 match; spend the time on the NEW group only. POST the
  known ids first (they bank as `accepted`), then the new group alone (D15: 140 banked at T+17 s, the 8 new ids at T+74 s).
- **A new id shape on an old field** (D15 `analysis_stripped_machine`): a field-table lookup on the whole suffix misses it. Peel
  a member qualifier off the front before declaring the field unknown; never answer it from the "first" member of the group.
- **Recursive unzip** destroys nested containers (.jar/.apk) and their `dNN--` prefix; keep them whole.
- **Same field name, different `kind`** (D8 elf_class/machine): read `answer_format.kind` per id.
- **Huge members** (D8: 67 MB Swift): any per-key xor brute force or per-field re-parse blows a timed window. Cheap encodings first
  (raw magic, base64 `SENGR`), crc-gate every hit, parse each member once.
- **Decoy magics** (D9 Nim): code that CHECKS the magic embeds `"HCFG"` literals. Empty len 0 => crc32(b"")==0 passes! Require
  non-empty JSON that parses, keep scanning, then try the base64 form.
- **Location fields per scan path** (D12): a decoder with raw AND base64 branches must return the hit offset from BOTH. Before
  submitting, assert no `none` where a config was decoded.
- **`strings -t d` offsets on Nim/Swift literals**: a printable byte before the text shifts the offset by 1. Use `grep -abo` /
  `re.finditer(...).start()` on the exact token.
- **Jar members are deflated**: `grep HCFG file.jar` finds nothing. Inflate the class, read constant-pool strings, base64-decode.
- **Stripped builds / renamed functions** in variants (D1 TT, D2 Mastery set2, D8 Mastery d01): answer what the question defines
  for absence (`[]`, `none`, has_symtab=false); never substitute a heuristic constant.
- **Tool parity**: ilspycmd, dotnet, rustfilt, GoReSym, rabin2, swift-demangle are in `bin/`; monodis/de4dot are not.
- **Timed windows**: download dominates (D16 TT: 52 s of 64 s in-window on the 32 MB bundle; solve 7.6 s); early expiries were
  download/orchestration latency, not solver speed. After editing hctf/*.py, restart the orchestrator (D1/D2 ran stale modules).
- **WASM parsing**: section/segment sizes are 5-byte PADDED LEB128 (`86 80 80 80 00`); a parser that assumes 1-byte sizes or
  minimal LEBs misreads every offset. Read LEB128 generically (`lib.binary.wasm_layout`); validate the whole module, not just the magic.
- **PE machine map must include 0x8664 → `x86-64`**: a from-scratch replay once emitted `0x8664` and failed TT twice.
