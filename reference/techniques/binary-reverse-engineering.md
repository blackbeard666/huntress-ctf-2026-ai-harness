# binary-reverse-engineering — technique log (days 1-19; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- One `evidence.zip` (AES, password `infected`). From Day 3 on it is CUMULATIVE: members `dNN--variant-XXX.<ext>`, one group per
  past day, plus ONE new container/language per day: D1 C ELF, D2 C++ (ELF or MinGW PE32+), D3 .NET dll, D4 static stripped Go,
  D5 static Rust, D6 Java .jar, D7 Kotlin fat .jar, D8 Swift ELF (67 MB), D9 Nim, D10 Zig (PE `.exe` in Mastery), D11 D (DMD),
  D12 Free Pascal, D13 Crystal, D14 Objective-C (GNUstep), D15 a PAIR of C ELFs (`-stripped`/`-symbolized`), D16 a PAIR of WASM
  modules (`-compact`/`-direct`), D17 Ada ELF (GNAT 14.2), D18 Fortran ELF (gfortran), **D19 GnuCOBOL ELF** (11 KB, dynamic
  `libcob.so.1` + libvbisam/libgmp/libncurses, stripped, `variant-000.cob`) **with a packed `PK19` overlay appended**.
  Answer ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`; a multi-member group adds a member qualifier:
  `dNN_analysis_<qualifier>_<field>` (D15 `stripped_`/`symbolized_`, D16 `compact_`/`direct_`).
- From Day 2 on, every new-day member carries the same embedded **HCFG** config blob: `'HCFG' | u8 ver | u8 xor_key | u16 len (LE) |
  u32 crc32 | xor'd JSON` (JSON at offset 12; crc32 is over the decoded plaintext). Only its storage changes (`.hcfg` section
  D2/D10/D14, .NET FieldRVA, Go/Rust rodata, base64 in a Java/Kotlin constant pool, base64 Swift/Nim/D/Crystal literal, RAW in FPC
  `.data`, WASM data segment 0, Ada/Fortran `.rodata`) -- **D19: NOT byte-visible at all**: the HCFG is the unpacked payload of
  the appended PK19 overlay. Scan raw bytes for `HCFG` AND its base64 form `SENGR...` (crc-gate every hit); when both miss, look
  for an overlay past the ELF image and read the question text -- it spells the unpacker.
  The JSON carries never-asked keys too (ipv4, windows_path, linux_path, service, host_model): parse the whole dict.
- The analysis is easy (headers, symbols, one config blob). The hard part is the GM's exact label for `exact_text` fields
  (format, machine, symbol, D17 `hcfg_storage`). **The organizers RE-ISSUE the contract mid-day** when a label is unguessable
  (D17 `hcfg_storage` -> `kind: enum` + ordered rule list). Since D17 the question texts are SPECS: D19's config questions give
  the whole unpacking algorithm byte by byte. `format` is now `kind: enum` on d12-d19: `elf, pe, pe_cli, jar, wasm, neko_bytecode`.
- **The contract LEAKS future days**: D19's `format` enum already lists `neko_bytecode` (never seen -> a Neko VM member is coming)
  and `overlay_offset` says "the final overlay magic named by this unit (PK19 for Day 19 or RS20 for Day 20)". Grep every new
  contract for tokens / day numbers that are not today's.
- **D19 broke the "theme never asked" streak**: D5-D18 never asked the new day's prompt theme (Rust panics, coroutines, wasm doors,
  D17 decoder, D18 call graph), but D19's theme ("decoder stub ... catch what's inside -- statically") IS the d19 group: config_*
  only after unpacking + NEW `overlay_offset` / `overlay_size`. The D17 backfill also re-asked old days' themes on their groups.
- **Every member since D2 also embeds a "dynamic trace" template** (unasked so far): `{"schema":"huntress.binary.dynamic_trace.v1",
  "branch":"<b>","event_count":<n>,"campaign":...,"family":"<lang>_<theme>_trace","effects":"...","network":"none"}` gated on env
  `HUNTRESS_HOST_MODEL` (`analysis`/`sandbox`/`workstation`). D18 `fortran_indirect_flow_trace`; D19 `cobol_static_unpack_trace`,
  effects `memory_only_inert_payload_hash`.
- Question count: 80 on D8, +10/day to 160 on D16, D17 = 204 (backfill #2: every old group padded to 11 ids), then +12/day:
  D18 216, **D19 228**, no backfill on D18/D19. Mastery = `setN.` prefixed copies (2 sets D2-D7, 5 D8-D9, 3 D10-D14, 5 D15-D17,
  4 D18, **5 on D19** = 1140 ids); artifacts named `delivery N: evidence.zip`. Timed end to end: D18 TT 8 s / Mastery 14 s; D19 TT
  4.2 s / Mastery 10 s.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, different storage per container (`.hcfg` section, .NET FieldRVA, Go/Rust rodata,
  base64 in a constant pool / string literal, raw FPC `.data`, WASM data segment 0, Ada/Fortran `.rodata`, D19 packed overlay):
  scan raw bytes for `HCFG` and `SENGR[A-Za-z0-9+/_-]*=*`, decode, accept only if crc32(plain) matches AND the JSON parses -- keep
  scanning past a failing hit (D9 Nim had two raw decoys); never a fixed offset. Storage did NOT change across a day's variants on
  any day (D18 offset 8512, D19 overlay 10808/424 in single, TT and all Mastery sets while key/campaign/crc re-rolled).
- **Packed overlay (NEW D19)** -- `'PK19' | u8 ver(1) | u8 k1 | u8 k2 | u8 pad | u32le packed_len | sha256(unpacked)[32] | packed`
  (header 44 bytes) appended right after the ELF section-header table (= end of the image). Unpack: `out[i] = ror8(packed[i] ^ k2, 3)
  ^ k1`; verify sha256(out); HCFG record at out[0] (then the normal xor/crc/JSON). Rule: take `data.rfind(magic)` ("final"
  overlay), implement the transform the QUESTION states, verify the stated hash; fallback for a mutated transform = known-plaintext
  `HCFG` at out[0] over (xor a, rotate r, xor c) -- the solver does both. The magic is per day (`PK19`, `RS20` named for Day 20):
  pick the `<2 caps><NN>` token whose digits = the group's day (the `overlay_size` question names no magic).
- **Location-as-answer** -- `hcfg_offset` (D9/D11-D14, D17-D18): base-10 FILE offset of the stored blob: base64 -> the `S` of
  `SENGR...`, RAW -> the `H`. `overlay_offset` (D19): offset of the overlay MAGIC (`P` of PK19); `overlay_size` = file length -
  that offset (header included: 424 = 44 + 380). Record `m.start()` of the validated hit on every scan path.
- **Storage-as-answer (`hcfg_storage`, D17, enum)** -- rules IN ORDER: `base64` if the crc-valid HCFG appears only after decoding a
  printable base64 carrier -> `raw_hcfg_section` if literal `HCFG` starts in a section named exactly `.hcfg` -> `wasm_data_segment`
  -> `raw_const_array` if in any other native data section -> else `raw`. Map offset -> section header; jars = base64. Unknown
  future token (a packed overlay is in NO section: `raw`? or a new token): read the question's rule list -- the enum is the space.
- **Any other storage encoding -> `lib.binary.hcfg_scan(data, deadline=None)`** (raw, base64 std/url/wrapped, hex, base32/85,
  UTF-16, reversed, xor'd, zlib/gzip, multibyte/rolling xor, byte maps, custom/rot13 b64, split/int-array/strided, RC4, AES/TEA/
  ChaCha, stack-built); `hcfg_find(data)` = first crc-valid + JSON-parsing hit. Kill switch `HCTF_HCFG_SCAN_EXT=0`. It does NOT
  know the PK19 rotate stub: packer overlays need their own unpack step before the scan.
- **xor key / config values** -- re-roll per variant (`BRNN-00V`, `node-00V.dayNN...`, crc, key); derive from the header byte.
- **Container per member** -- ELF vs PE32+ `.exe` re-rolls per member in Mastery (d02 C++, d04 Go, d10 Zig PE `pe`). Labels come
  from THIS member's header. Dispatch on MAGIC, not extension: `7f454c46` ELF, `MZ` PE, `PK` jar, `\0asm` WASM (next: `NEKO`).
  A re-asked symbol field on a PE member follows the D2 PE convention: COMDAT section name `.text$<mangled>`.
- **Member qualifier in the id (multi-member group, D15-D16)** -- `dNN_analysis_<qualifier>_<field>` names ONE member by a token of
  its FILE NAME. Rule: peel the longest field prefix that is a `[^a-z0-9]+`-separated token of exactly one member name. Tags seen:
  `stripped`/`symbolized`, `compact`/`direct`; same HCFG in both. `sha256_K` = ARCHIVE order (central directory), never sorted.
- **Variant index per group** -- `dNN--variant-XXX` re-rolls per group and mode; a carry-over d01 can re-roll STRIPPED (D15-D17
  Mastery, D17 TT) -> symbols/disassembly `[]`, has_symtab `false`, `recover_code` `none` (D17 CONFIRMED; the leaf heuristic's
  8106/8114 rejected); D18 not stripped; D19 TT d01 stripped again (`none` accepted). Pair by sha256, never index.
- **Contract wording per fetch (D17)** -- the same id's question/answer_format can change between fetches (exact_text -> enum,
  "equivalents accepted"). The solver reads `answer_format` per id at run time; assert enum tokens are in `accepted_values`.
- **Mastery packaging** -- `setN.` prefixed ids, each set its own `delivery N: evidence.zip`: pair by sha256. Each set's 1st question
  ends `Evidence case: dNN-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]` (TT `dNN-tt-...`) = set->delivery map.
- **answer_format.kind for the same field name** -- D8/D15: `elf_class`/`machine` exact_text on d01 but INTEGER (`64`/`62`) on
  d08/d15 in ONE contract. Dispatch on `kind`, not on the field name.
- **Feature-presence fields** -- `has_<thing>_section` (D10/D14 literal `.hcfg`), D17 runtime-identity booleans on old groups
  (`has_go_runtime`, `has_rust_mangled_symbol`, `has_coroutine_runtime`, `has_cpp_typeinfo/vtable`). Generic rule: `has_<x>` = a
  structural marker of <x> in THIS member; expect `has_overlay`, `has_cobol_runtime`, `has_gnat_*`-style ids next.
- **Field set per old group** -- old groups gain ids over days (D8 to 10, D17 to 11). Answer by field name from the parsed facts
  dict of THAT member; unknown field -> log and fall through.
- **Speed flags (no answer change)** -- per-case timings are usually CPU contention from parallel solver-tests: re-measure with
  `taskset -c 0,1 /usr/bin/time python3 solve.py ...`. Floor = AES-CTR+inflate+sha256 of the 67 MB d08 member (~0.35 s/set).

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
| Go ("build info, function names, file paths") | `go version -m file`; `lib.binary.go_buildinfo` / `go_pclntab_funcs` (stripped names survive in `.gopclntab`) |
| Rust (mangled `_R`/`_ZN..17h<hash>E`, panic strings) | `readelf -hS` + `HCFG` scan; `rustfilt` / `lib.binary.rustfilt` if symbols are asked |
| `.jar` / "constant pool" / methods / access flags | unzip the jar, `META-INF/MANIFEST.MF` Main-Class, `javap -v -p Main.class` (method table order, `flags: (0x0031)`); `ConstantValue: String` base64 config |
| Kotlin fat jar (`kotlin/`, `X$fn$1 extends ContinuationImpl`) | Parse the Main-Class first, skip `kotlin/`/`org/jetbrains/`; coroutine runtime = `kotlin/coroutines/` entries |
| Swift ELF (`swift5_*` sections, `$s<len><Module>` symbols, 60+ MB) | Never eager-parse symbols; regex `SENGR` base64 in `.rodata`; `bin/swift-demangle` |
| Nim / D / Crystal ELF (`NimMain`; `_D4core`,`DMDH`; `Crystal:H`,`GC_malloc`) | Plain ELF; base64 `SENGR...` literal (Nim: two raw `HCFG` decoys -> crc-gate); offset = the `S` |
| Free Pascal / Objective-C / Ada / Fortran ELF (`FPC 3.2.2`; `__objc_*`; `GNAT Version`; `libgfortran.so.5`, `MAIN__`) | Plain ELF, carried-over solver answers it (`elf`/`x86-64`/`62`); HCFG RAW (`grep -abo HCFG`, crc-gate, offset = the `H`): FPC `.data`, ObjC own `.hcfg` section, Ada/Fortran `.rodata` |
| GnuCOBOL ELF (`libcob.so.1` NEEDED, `cob_init`/`cob_set_programid`/`cob_display`/`cob_get_environment` imports, `variant-000.cob`, libvbisam/libgmp/libncurses) | Plain ELF for the header ids; config is NOT in the image: look past the end of the section-header table (D19) |
| No crc-valid `HCFG`/`SENGR` anywhere + file size > `e_shoff + e_shnum*e_shentsize` (or > max section end) | Appended OVERLAY: `xxd -s <image_end> F`; magic like `PK19` (D19) / `RS20` (D20 named); parse the header fields the question lists, run its byte transform, check the stated sha256, then HCFG at out[0] |
| Two members differing by a name tag, ids `dNN_analysis_<tag>_<field>` | Route each id to the member whose file name carries `<tag>`; same HCFG in both |
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
**D17 "Decoder Ring"** (204 Qs; CORRECT T+4:03): ONE Ada ELF, HCFG RAW `.rodata`; backfill #2 (32 ids on old groups, all accepted in
ONE POST); `hcfg_storage` raw ids burned ~10.9k rejected POSTs / 3.5 h until the organizers revised the contract to an enum.
TT/Mastery d01 stripped -> `recover_code` `none`. **D18 "Flow State"** (216 Qs; CORRECT T+11 s, 0 wrong; TT/Mastery first try):
ONE Fortran ELF (gfortran), HCFG RAW `.rodata` (`encoded_config.4`, 8512); call-graph/API/"no injection" theme unasked; the
race harness POSTed the carried-over solver's answers with zero new code.

**D19 "Jack in the Box"** (slug `static-unpacking`; 228 Qs; **CORRECT at T+2:25**; TT and Mastery CORRECT first try). Prompt:
"There's a payload hiding inside this binary, and a little decoder stub wound up to pop it out. Find the stub, watch it work, and
catch what's inside -- statically." New group = ONE GnuCOBOL ELF (11232 B, dynamic: libcob.so.1, libvbisam.so.1, libgmp.so.10,
libncurses.so.5, libdl, libm; stripped; old-GCC layout with `.jcr`; `cob_check_version` string `1.5.2`, source `variant-000.cob`,
host models + trace JSON `cobol_static_unpack_trace` / `memory_only_inert_payload_hash` in `.rodata`). No HCFG/SENGR anywhere in
the image; a 424-byte `PK19` overlay starts at 10808 = e_shoff 0x2378 + 27*64 (end of the section-header table).
- Contract = the 216 D18 ids unchanged + 12 d19 ids: sha256, architecture, format (enum incl. `neko_bytecode`), machine,
  config_campaign/domain/mutex/url/crc32_hex, hcfg_version (all "after unpacking"), NEW `overlay_offset`, `overlay_size`.
  The config questions spell the whole stub: k1 +5, k2 +6, u32le packed length +8, 32-byte unpacked SHA-256 +12, packed bytes
  +44, `ror8(byte XOR k2, 3) XOR k1`, verify sha256, HCFG at unpacked offset 0 (k1 0x21, k2 0xa4, len 380 = 12 + 368 JSON).
- Timeline: race harness banked the 216 carried-over ids at T+26 s; its 9 `none` placeholders for the d19 config/version ids
  were rejected (harmless probes). The worker first guessed the transform from bytes (xor k1 then ror 3 -> garbage / a spurious
  partial HCFG at +28) for ~1 min before reading the question text; then implemented it literally + an `overlay_magic()` helper
  (question-named magic, or the `<2 caps><day>` token for `overlay_size`) -> the 8 open ids accepted in one POST.
- TT: 4.2 s end to end (download 0.8, solve 1.0); Mastery 5 sets / 1140 ids: 10 s (solve 5.5 s). Overlay 10808/424 identical in
  every variant; campaign BR19-00V / crc re-rolled; TT d01 stripped again.

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class (`kind` exact_text) | `ELF64` / `ELF32` (readelf style) | ELFCLASS64 |
| elf_class (`kind: integer`, D8) | the bit width `64` / `32` | `2` / `1` (raw EI_CLASS byte) |
| machine (`kind: integer`, D8-D9, D15) | decimal e_machine (`62` = x86-64) | — |
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
| C++ symbols (ELF) incl. `mangled_score_symbol`, `typeinfo_symbol` (D17) | bare Itanium mangled name (`_ZNK15DiscoveryEngine5scoreEPKc`, `_ZTI15DiscoveryEngine`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` / `.rdata$<mangled>` | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` (D17 text: omitting it also accepted) | list without "" (pre-D17) |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates | hex imm, `"ret "` |
| methods / access_flags / method_count (jar, D17) | Main-Class `method_info` names in table order incl. `<init>` (JSON) / decimal `49` / count incl. `<init>`/`<clinit>` | — |
| metadata_version | BSJB root string `v4.0.30319` | net8.0 / TFM |
| config_* | values verbatim from the decoded HCFG JSON (mutex keeps ONE backslash); D19: from the UNPACKED overlay's HCFG | JSON-escaped `\\`; `none` when the blob is merely hidden (D19) |
| hcfg_version / xor_key_hex | header byte 4 decimal / header byte 5 as `0x%02x` | — |
| has_hcfg_section (enum) | `true` when a section is literally named `.hcfg` | — |
| hcfg_offset (integer) | decimal FILE offset: base64 text start (`S`), RAW = the `HCFG` magic | — |
| overlay_offset / overlay_size (integer, D19) | offset of the LAST occurrence of the day's overlay magic (`PK19`) / file length - that offset (header included) | — |
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
- **Absence vs hidden**: `none`/`[]`/`false` is right when the thing is ABSENT (stripped d01, D1 TT, D2 Mastery set2; a re-asked
  field inherits it), wrong when it is merely HIDDEN (D19 config: packed, the race harness's `none` placeholders were rejected).
- **A multi-field POST is all-or-nothing.** One wrong field fails the set and hides which one (D2). Submit unconfirmed/new fields
  ALONE; batch the bytes-derived ones (D17: 10 new fields in one POST; D19: 8 in one POST).
- **Theme facts**: D5-D18 themes were not asked on their own day, but D19's was, and D17 backfilled old themes -- always record the
  day's theme facts (stub, overlay header, call graph, trace family) in NOTES.md and expose them in the facts dict.
- **Formatting**: build submit JSON with python/jq (`Global\Huntress...` mutex = ONE backslash); capstone `ret` has an empty
  op_str (`"ret "` -> strip), immediates in decimal.
- **Cumulative zip**: old groups' answers carry over when their sha256 match; POST the known ids first (they bank as `accepted`),
  then the new/unknown ids (D17: 188 at T+18 s; D18 all 216 at T+11 s; D19 216 at T+26 s).
- **Id shape / kind**: peel a member qualifier off the front before declaring a field unknown (D15 `analysis_stripped_machine`);
  the same field name can change `kind` (D8 elf_class/machine integer) -- read `answer_format.kind` per id.
- **Archives**: never unzip recursively (nested .jar/.apk lose their `dNN--` prefix); jar members are deflated, so `grep HCFG
  file.jar` finds nothing -- inflate the class and read constant-pool strings.
- **Huge members** (D8: 67 MB Swift): no per-key xor brute force or per-field re-parse; cheap encodings first, crc-gate every hit.
- **Decoy magics** (D9 Nim): code that CHECKS the magic embeds `"HCFG"` literals; len 0 => crc32(b"")==0 passes! Require non-empty
  JSON that parses, keep scanning. Overlays: the question says "final" -> `rfind`, and verify the stated sha256.
- **Location fields per scan path** (D12): a decoder with raw AND base64 branches must return the hit offset (and encoding) from
  BOTH; take offsets from `grep -abo` / `re.finditer().start()`, not `strings -t d` (off by 1).
- **Timed windows**: download dominates (D16 TT 52 s of 64 s). After editing hctf/*.py, restart the orchestrator.
- **WASM parsing**: section sizes are 5-byte PADDED LEB128; read LEB128 generically (`lib.binary.wasm_layout`).
- **PE machine map must include 0x8664 → `x86-64`**: a from-scratch replay once emitted `0x8664` and failed TT twice.
