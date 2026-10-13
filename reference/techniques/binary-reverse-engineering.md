# binary-reverse-engineering — technique log (days 1-13; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- One `evidence.zip` (AES, password `infected`). From Day 3 on it is CUMULATIVE: members `dNN--variant-XXX.<ext>`, one group per
  past day, plus ONE new container/language per day: D1 C ELF, D2 C++ (ELF or MinGW PE32+), D3 .NET dll (+runtimeconfig.json),
  D4 static stripped Go ELF, D5 static Rust ELF (debug_info), D6 Java .jar, D7 Kotlin fat .jar (5 MB, ~3300 entries), D8 Swift ELF
  (67 MB, static stdlib+Foundation+ICU, not stripped), D9 Nim ELF (60 KB, dynamic glibc, not stripped), D10 Zig ELF (134 KB,
  dynamic glibc, stripped, clang/LLD 19 zig-bootstrap in `.comment`) -- a Zig PE `.exe` in Mastery set2, D11 D-language ELF (1 MB,
  DMD, druntime static + dynamic glibc, not stripped, debug_info), D12 Free Pascal ELF (100 KB, FPC 3.2.2, static, stripped), D13 Crystal ELF (749 KB, dynamic glibc + libgc, not
  stripped).
  Answer ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`.
- From Day 2 on, every new-day member carries the same embedded **HCFG** config blob: `'HCFG' | u8 ver | u8 xor_key | u16 len (LE) |
  u32 crc32 | xor'd JSON` (JSON at offset 12; crc32 is over the decoded plaintext). Only its storage location changes
  (`.hcfg` section, .NET FieldRVA array, Go/Rust rodata, base64'd in a Java/Kotlin constant pool, base64 Swift String literal in
  `.rodata` on D8, base64 Nim/D string literal in `.rodata` on D9/D11, RAW in FPC `.data` on D12, base64 Crystal String literal in `.rodata` on D13). Scan raw bytes for `HCFG` AND for its base64 form `SENGR...` (raw `HCFG` can also be a false hit inside code: check crc).
  The JSON also carries never-asked keys (ipv4, windows_path, linux_path, service, host_model on D7): parse the whole dict so a new `config_<key>` id is free.
- The analysis is easy (headers, symbols, one config blob). The hard part is the GM's exact label for a few `exact_text` fields (format,
  machine, disassembly, symbol). The question set grows each day (9 → 17 → 24 → 32 → 40 → 48 → 56 → 80 → 90 → 100 → 110 → 120 → 130 fields); old groups reuse the same bytes,
  but D8 BACKFILLED old groups to 10 ids each (new: has_symtab, has_cpp_typeinfo/vtable, xor_key_hex, hcfg_version, compression_methods).
- The prompt's theme (Rust panics, D7 "coroutine state machine", D8 Swift "protocols", D9 Nim "runtime fingerprints") has NOT
  been asked since D4: the new group gets sha256, format, config_campaign/domain/mutex/url/crc32_hex + 1-3 extra ids
  (architecture D4-D5/D8-D12, hcfg_version D6-D7, elf_class/machine as INTEGERS D8-D9, `hcfg_offset` D9 + D11 + D12, `has_hcfg_section`
  D10). D11/D12/D13 added NO new field (D12 = hcfg_offset on a RAW blob; D13 "follow the DNS labels" = just the
  config domain/url). Usually exactly ONE
  never-seen field per day: grep the new group's ids against the solver's field table before anything else.
- Time Trial ≈ 6-16 s; Mastery = `setN.` prefixed copies, 2 sets (7-12 s) through D7, 5 sets / 400-450 ids / 20-27 s on D8-D9,
  3 sets / 300-390 ids / 28-30 s on D10-D12 (TT 30 s too; D13 TT 80 s / Mastery 200 s); artifacts are named `delivery N: evidence.zip`.
- **D10 RELAXED the label fields**: 36 ids are now `kind: pattern` whose syntax ACCEPTS equivalents (format: "ELF or PE; case,
  ELF32/ELF64/PE32/PE32+ accepted"; machine/architecture: "standard tool or symbolic label, or decimal/hex code"; e_type and
  endianness: symbolic constant / readelf label / numeric code; .NET format: any container_runtime token with CLI/CLR/.NET). D8-D9's
  integer machine became pattern. Keep emitting the GM-confirmed spellings; the old REJECTED lists may be stale for pattern ids.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, different storage per container (`.hcfg` section, .NET FieldRVA, Go/Rust rodata,
  base64 inside a Java/Kotlin constant pool, base64 Swift/Nim string literal in ELF `.rodata` on D8/D9): scan raw bytes for `HCFG`
  and for `SENGR[A-Za-z0-9+/_-]*=*` (base64 of `HCFG`, std or urlsafe), decode, accept only if crc32(plain) matches AND the JSON
  parses -- keep scanning past a failing hit (D9 Nim had two raw `HCFG` decoys); never a fixed offset.
- **Location-as-answer (`hcfg_offset`, D9/D11/D12)** -- base-10 FILE offset of the first byte of the stored blob as it sits in
  the member: base64 form -> the `S` of `SENGR...` (D9 Nim 30696, D11 D 368272, D13 Crystal 560188 -- the text, not the String header 12 B before it); RAW form -> the `H` of `HCFG` (D12 FPC 82928 =
  0x143f0 in `.data`, GM-confirmed single+TT+Mastery x3). Constant across a day's variants although shas differ -- still
  compute it: record `m.start()` of whichever scan hit (raw OR base64) validated, on BOTH paths (D12's raw path returned `none`).
- **xor key / config values** -- re-roll per variant; derive from the header byte, never from the sample.
- **Container per member** -- ELF vs PE32+ `.exe` re-rolls per member: Mastery set2 had d02 C++ as `.exe` (D3-D5, D7, D10) and d04
  Go as `.exe` (D4, D5, D7, D10); D6 set2 had both as ELF; D10 set2 had the NEW d10 Zig member as a PE too (format `pe`). Labels come from the header of THIS member (Go PE: format `pe`, architecture `x86-64` from Machine).
- **Variant index per group** -- `dNN--variant-XXX` re-rolls per group and mode (D7 TT: d03-001, d04-006, d07-005 ...); sizes
  and config values change, names/layout don't. TT == Mastery set1 bytes on D7; D8 TT re-used the D7 TT old-group indices
  (d08 = variant-000); D9 TT == set1 for d02-d09 (d09 BR09-003) but d01 differed (TT variant-000 `8100`, all 5 Mastery sets one
  other d01 with `mov eax, 8104`, symtab present). Mastery d09 = BR09-003/006/001/004/007; d08 stayed variant-000..004.
- **Mastery packaging** -- `setN.` prefixed ids, each set its own `delivery N: evidence.zip` (same filename): pair by sha256.
  Set count re-rolls: 2 (D2-D7), 5 on D8-D9 (set2/set4 had d02/d04 as PE both days), 3 on D10: loop over every `setN.`. From D9 (all
  lanes) the first question of each set ends `Evidence case: d09-m-<16hex>. [assigned-artifact-sha256:<zip sha256>]`
  (TT: `d09-tt-...`): an explicit set -> delivery map; it is question TEXT, never part of an answer.
- **answer_format.kind for the same field name** -- D8: `d01_analysis_elf_class`/`machine` exact_text (`ELF64`/`x86-64`) and
  `d08_analysis_elf_class`/`machine` integer (`64`/`62`) in ONE contract; D9 `d09_analysis_machine` integer again. Rule:
  dispatch on `kind`, not on the field name.
- **Feature-presence fields** -- `has_<thing>_section` (D10 `has_hcfg_section`, enum true/false) for ELF AND PE: answer from the
  member's section-name table (`.hcfg` literally; PE names are 8-byte NUL-padded), generic over `<thing>` (regex `has_(\w+?)_section`).
- **Field set per old group** -- old groups gain ids over days (D8 padded every group to 10). Answer by field name from the
  parsed facts dict of THAT member; an unknown field must log and fall through, never crash. Keep the older 56/112-id cases passing.
  D9 kept D8's 10 ids for d01-d08 (d08: sha, architecture, elf_class, format, machine, 5 config) and added d09 with `hcfg_offset`.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `evidence.zip`, "AES Encrypted" | `7z x -pinfected -y evidence.zip` (Python: `pyzipper`); `sha256sum *` for every `artifact_sha256_K` (K = archive order within the group) |
| `readelf -h -S` hint, ELF header questions | `readelf -hSW`, `readelf -sW`; `readelf -x .huntress` / `readelf -p .huntress` for the custom-section marker |
| "constant returned by recover_code" / `disassembly` | `objdump -d -M intel --no-show-raw-insn` around `<recover_code>`; capstone on the FUNC symbol's st_value..st_size bytes |
| Stripped C build, no `.symtab` | find the leaf `b8 imm32 c3` (`mov eax, imm; ret`) in `.text` (`lib.binary.recover_return_constants`) and check it against what `main` inlines |
| C++ / "mangled" / "vtable" / "RTTI" | `nm -C` / `c++filt`; look for `_ZTV<class>` (vtable), `_ZTI`/`_ZTS` (typeinfo), `_ZNK<cls>5scoreEPKc`; the PE COFF symtab: `objdump -t file.exe` |
| `PE32+` MinGW `.exe` | `objdump -t` (COFF symbols + string table), `pefile` (Machine, OPTIONAL_HEADER.Magic, sections incl. `.hcfg`) |
| "CLI metadata", `.dll` + `runtimeconfig.json`, `BSJB` in strings | `ilspycmd file.dll` (decompile to C#; installed 2026-10-07) or Python `dnfile`; config = `<PrivateImplementationDetails>` FieldRVA static array; `strings` shows `BSJB v4.0.30319` |
| Go ("build info, function names, file paths") | `go version -m file` (buildinfo: go1.x, GOARCH); `lib.binary.go_buildinfo` / `go_pclntab_funcs` (stripped names survive in `.gopclntab`) |
| Rust ("mangled symbols with a distinct accent", panic strings) | `readelf -hS` + `HCFG` scan was enough on D5; demangle with `rustfilt` (installed) or `lib.binary.rustfilt` (binary) if symbols are asked |
| `.jar` / "constant pool" | unzip the jar, read `META-INF/MANIFEST.MF` Main-Class, `javap -v -p Main.class`; look for `ConstantValue: String` (`static final String CONFIG`) |
| Kotlin fat jar (`kotlin/` runtime, `META-INF/main.kotlin_module`, `X$fn$1 extends ContinuationImpl` with `int label`) | Same as `.jar`: parse the Main-Class first, skip `kotlin/`/`org/jetbrains/`. Coroutine "state machine" = `invokeSuspend` switching on `label`; branch logic is plain `javap -c` (`lookupswitch` on String.hashCode + `ldc` results) |
| Swift ELF (`swift5_*` sections, `$s<len><Module>...` symbols, clang `swiftlang` in `.comment`, huge 60+ MB static stdlib) | `nm FILE \| grep '\$s[0-9]*<Module>'` (app symbols sit just after `frame_dummy`); `bin/swift-demangle`; config getter = `lea rax,[rip+X]; movabs rax,0xd0000000000001fc; ret` → literal chars at X+0x20, count = low 48 bits (0x1fc); or simply regex `SENGR` base64 |
| Nim ELF (`NimMain`/`NimMainModule`/`PreMain`, `TM__<hash>_N` literals, `<proc>__<mod>_u<N>` mangling e.g. `encodedConfig__v000_u31`, `@m..@snim@slib@s...nim.c` / `fatal.nim` strings, `nimZeroMem`/`nimCopyMem`) | It is plain C-compiled ELF: header ids via readelf as usual. Config proc returns a string literal: `mov eax,0x1fc; lea rdx,[rip+X]` (len, `TM__` ptr); the literal is `u64 cap\|0x4000000000000000` then the chars, so text = X+8 (file off = VA - segment base). Or regex `SENGR` |
| D ELF (`_D<len><module>...` mangling e.g. `_D4v00012decodeConfigFZAya`, `_D2rt`/`_D4core` druntime symbols, `DMDH`/`DMDI` strings, no `.comment`) | Plain native ELF: readelf header ids as usual. Config = `decodeConfig()` returning a D string (`Aya` = immutable(char)[]); the base64 `SENGR...` literal is NUL-terminated in `.rodata` -- regex it. `evaluate`/`campaign` funcs exist but were never asked |
| Free Pascal ELF (`FPC 3.2.2 [...] for x86_64 - Linux` string, `.fpcdata` section, static + stripped, `FPC_`/`fpc_` RTL names in strings) | Plain native ELF: readelf header ids as usual. HCFG sits RAW (magic + header + XOR'd JSON) in `.data` -- `grep -abo HCFG`, crc-gate, offset = the magic's offset. Pascal "record layouts" flavour unasked |
| Crystal ELF (`Crystal:H` strings, Boehm GC exports `GC_malloc`/`GC_world_stopped`, `*crystal*` symbols via `nm`) | Plain native ELF: readelf header ids as usual. Config = base64 `SENGR...` Crystal String literal in `.rodata` behind a 12-byte header (`u32 type_id=1, u32 bytesize, u32 length`) -- regex it; offset = the `S`. "DNS labels" = the config's domain/url, no DNS wire format anywhere |
| Packed / high entropy / `UPX!` | `lib.binary.packer_info` → `upx -d` on a COPY (not seen yet) |
| Real code-reversing question (not seen yet) | `rizin -q -c "aaa; pdf @ sym.<fn>"`; Ghidra headless `lib.binary.ghidra_decompile` (heavy, last resort) |

## Day by day
**D1 "ELF Aware"** (9 Qs; ~14 min, 4 wrong). C ELF64: class, endianness, machine, e_type, `.huntress` marker, has_symtab,
recover_code constant, entry point (readelf/objdump; pyelftools + capstone). Spellings learned by rejection. TT "slot" bundle
(`slotN_<qid>`): stripped profile and a renamed designated fn (→ `none`, unconfirmed).

**D2 "Mangled"** (17 Qs; ~22 min, 5 wrong). + C++ (ELF or MinGW PE32+). First HCFG (`.hcfg` section). vtable = `_ZTV<class owning
score>`; PE symbol fields want COMDAT `.text$<mangled>` / `.rdata$<mangled>` (all-or-nothing set POSTs hid this for hours).

**D3 "Table Manners"** (24 Qs; ~1 h 48 min, ~60 wrong). + .NET 8 PE32 i386 dll: `dnfile` → BSJB `v4.0.30319`, FieldRVA HCFG.
`d03_analysis_format` = `pe_cli` after ~50 rejected synonyms: compose labels from spec tokens.

**D4 "Go Fish"** (32 Qs; ~1.5 min, 1 wrong). Static stripped Go ELF; HCFG in rodata. `architecture` `amd64` (GOARCH) REJECTED →
`x86-64`: "architecture" uses the container's machine words, not the toolchain token.

**D5 "Rust Belt"** (40 Qs; 7 s, 0 wrong, no LLM). Static Rust ELF; the D4 solver passed unchanged. Rust theme never asked.

**D6 "Pool Party"** (48 Qs; ~5 min, 1 wrong). `.jar`: Main-Class `javap -v -p` → `static final String CONFIG` base64 → HCFG. New
`hcfg_version` (byte 4, base-10). Format `jar_jvm` REJECTED → `jar`. Keep nested .jar/.apk members whole (recursive unzip lost the
`d06--` prefix). Question texts got rewritten to name accepted spellings: read each `syntax`.

**D7 "Routine Check"** (56 Qs; 3 min, 0 wrong). 5 MB Kotlin fat jar, same constant-pool base64 HCFG; scan the Main-Class first
(not ~3300 runtime classes). Unasked "state machine": `evaluate()` lookupswitch on env `HUNTRESS_HOST_MODEL`.

**D8 "Swift Justice"** (80 Qs). New d08 = 67 MB static Swift ELF (~290k symbols, not stripped); old groups backfilled to 10 ids.
- **Read `answer_format.kind` first:** d08 elf_class/machine were `integer` → bit width `64` (not EI_CLASS `2`) and `62`.
- Eager `pyelftools` `iter_symbols()` and the headerless-XOR brute force each took 60 s+ on it (worker lost 120 s + a 66 s
  profile). Recon with `readelf`/`nm`/`strings`; config = base64 HCFG in `.rodata` (`strings -n 40 | grep -m3 '^SENGR'`).
- Mastery: 5 deliveries x ~31 MB; download ~4.6-10 s + solve ~8 s inside a 27 s window.
- **Mastery mutated a carry-over ELF:** a STRIPPED d01 (no .symtab). The question says "If that symbol is absent, submit []";
  the old "last `mov eax, imm32; ret` leaf" fallback answered `["mov eax, 8102","ret"]` and failed all 5 sets. Absent →
  `[]`, has_symtab `false`, symbols `[]`. Never substitute a heuristic for an absence the question defines.
- LIB: `lib.elf.fields(data)[1]` returns `elf_class_int`/`machine_int` for `kind == "integer"`.

**D9 "Nimble"** (90 Qs; 86 s, 0 wrong). 60 KB Nim ELF (`.symtab` kept). Two raw `HCFG` DECOYS (assert text + magic-check
literal) -> the real blob is base64 `SENGR...` in a Nim literal (8-byte cap header before the text). NEW `hcfg_offset` = 30696 =
first base64 char. Lost: a jq `.answer_id` (contract questions use `.id`). TT 10 s / Mastery 5 sets 20 s, both first try.

**D10 "Zig Zag"** (100 Qs; ~33 s, 0 wrong). 134 KB stripped Zig ELF; HCFG raw in a writable `.hcfg` section. NEW enum
`has_hcfg_section` = `true` (generic `has_(\w+?)_section` over section names, ELF and PE). "ELF and PE side by side" only meant
Mastery set2's d10 was a Zig PE (format `pe`). TT in_window 2.85 s, Mastery 3 sets 5.59 s.

**D11 "D-Day"** (110 Qs; ~36 s, 0 wrong). 1 MB DMD ELF; base64 HCFG NUL-terminated in `.rodata` after `.debug_line\0`,
hcfg_offset 368272. Carried-over solver answered everything (2 tool calls); "template expansions" flavour unasked.

**D12 "Pascal's Wager"** (120 Qs; ~54 s start->CORRECT, 2 wrong POSTs). Prompt: "Pascal is betting you won't read its record
layouts ... read the configuration straight from memory's own filing cabinet." New d12 = `d12--variant-000.elf`, 100,976 B Free
Pascal 3.2.2 ELF64 x86-64, static, stripped. d12 ids: sha, architecture, format, machine, 5 config, hcfg_offset (no new field).
- HCFG RAW in `.data` at file offset 0x143f0 (`HCFG 01 81 7001 f881fce4` = ver 1, key 0x81, len 368) -> `hcfg_offset` **82928**
  (offset of the magic itself); config `BR12-000` / `node-000.day12.example.invalid` / crc `0xe4fc81f8`.
- The copied D11 solver decoded the raw blob but its raw-scan branch did not record the offset -> `none`. POST 1 (120 ids)
  incorrect; the harness bisect POSTed d01-d06 (accepted) then d07-d12 (incorrect); worker `xxd -s 82900`, patched the raw
  branch to return its offset (+ keep scanning past a raw decoy whose crc fails), CORRECT. Lesson: every scan path must
  fill every location field.
- TT 30 s window, in_window 2.9 s (BR12-004); Mastery 3 sets / 360 ids, in_window 5.14 s (BR12-004/005/006, offset 82928 in
  all). Both CORRECT first try.

**D13 "Crystal Clear"** (130 Qs; ~14 s start->CORRECT, 0 wrong, no worker tool call). Prompt: "Crystal compiles to native code
with a distinctive shine. Fingerprint the runtime, then follow the DNS labels". New d13 = `d13--variant-000.elf`, 749,208 B
Crystal ELF64 x86-64 (dynamic, libgc, symtab). d13 ids: sha, architecture, machine, format, 5 config, hcfg_offset (no new field).
- Base64 HCFG in a Crystal String literal (`01000000 fc010000 fc010000` header, 508 chars) -> `hcfg_offset` **560188** (0x88c3c,
  first base64 char); `BR13-000` / `node-000.day13.example.invalid` / crc `0xa69b7e61`, key 0x91. Domain never in plaintext.
- The carried-over solver's `SENGR` regex + `m.start()` answered every field. TT (80 s window) in_window 2.41 s; Mastery 3 sets /
  390 ids in_window 5.99 s (variants 007/002/005; key = 0x91+N; offset constant). Both CORRECT first try.

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class (`answer_format.kind` exact_text) | `ELF64` / `ELF32` (readelf style) | ELFCLASS64 |
| elf_class (`kind: integer`, D8 `d08_analysis_elf_class`) | the bit width `64` / `32` (single, TT, Mastery x5) | `2` / `1` (raw EI_CLASS byte; GM-rejected D8) |
| machine (`kind: integer`, D8-D9 `d08`/`d09_analysis_machine`) | decimal e_machine (`62` = x86-64; read u16 at offset 18 in EI_DATA order) | — |
| endianness | `little` / `big` | little endian, lsb, msb |
| machine (ELF) | `x86-64`, `x86`, `AArch64`, `ARM` | EM_X86_64, x86_64, amd64 |
| machine (PE FILE_HEADER) | 0x14c → `i386`; 0x8664 → `x86-64` | x86 (for PE i386); raw `0x8664` |
| architecture | the same machine words (Go ELF amd64 → `x86-64`; Go PE `.exe` 0x8664 → `x86-64`) | amd64, arm64, 386, x86_64 |
| elf_type | the constant `ET_EXEC` / `ET_DYN` | EXEC |
| entry_point, crc32_hex, xor_key_hex | lowercase hex with `0x` (crc `0x%08x`, key `0x%02x`) | — |
| recover_code | base-10 integer (`mov eax, 0x1fa4` → 8100); `none` if the named function is absent and the format allows it (inferred) | the renamed function's constant |
| has_symtab / has_cpp_* | enum `true`/`false` | — |
| marker | exact `.huntress` string without the NUL; `none` if the section is missing | — |
| format (native) | lowercase container: `elf`, `pe` (`macho` presumed) | ELF, ELF64, elf64-x86-64, HCFG, json, exe, pe32+, coff, mz |
| format (.NET) | `pe_cli` | ~50 synonyms (pe, pe32, dotnet, .net, cil, msil, clr, managed, assembly, ...) — lib/knowledge.py DOTNET_FORMAT_REJECTED |
| format (Java/Kotlin jar) | `jar` (D6 Java, D7 Kotlin) | jar_jvm |
| format / architecture (Swift D8, Nim D9, Zig D10, D D11, FPC D12, Crystal D13 ELF) | `elf` / `x86-64`; D9 machine integer `62` (source language never changes the container label) | — |
| C++ symbols (ELF) | bare Itanium mangled name (`_ZNK...`, `_ZTV...`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` (function), `.rdata$<mangled>` (vtable) | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` | list without "" |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates (D6 text says AT&T is also accepted) | hex imm, `"ret "`, `mov eax,0x..` |
| metadata_version | BSJB root string `v4.0.30319` | net8.0 / TFM / assembly version |
| config_* | values verbatim from the decoded HCFG JSON (mutex keeps ONE backslash) | JSON-escaped `\\` |
| hcfg_version | header byte 4 as a decimal integer | — |
| has_hcfg_section (D10, enum) | `true` when a section is literally named `.hcfg` (ELF Zig + PE Zig both `true`) | — |
| hcfg_offset (`kind: integer`, D9, D11-D13) | decimal FILE offset of the stored blob's first byte: base64 text start (Nim `30696`, D `368272`, Crystal `560188`), RAW blob = the `HCFG` magic (FPC `82928`), all modes | — (not tried: VA 0x4077e8, struct 0x77e0, `strings -t d` 30695) |
| xor_key_hex | HCFG header byte 5 as `0x%02x` (D8: 0x51/0x61/0x71/0x31 for d04-d07) | — |
| compression_methods (jar, `kind: json`) | sorted distinct ZIP `compress_type` ids, compact: `[0,8]` | — |
Naming law (from playbook.py): native format = container only; a managed .NET binary = container_runtime from the spec tokens (pe+cli).
Java broke the compound law (`jar`), so when a label is new, try the plain container name AND the compound, one per POST.

## Pitfalls that cost time
- **A multi-field POST is all-or-nothing.** One wrong field fails the set and hides which field was wrong. On D2 this made the correct `pe`
  look rejected for hours (the real error was the symbol form). Submit unconfirmed/new fields ALONE; batch only the known ones.
- **Guessing synonyms for a synthetic label** (D3 .NET format: ~50 tries, ~1.5 h). Derive from spec tokens and the playbook naming laws,
  use `hctf labels` (it ranks candidates from the playbook), and read the question `syntax` first: the GM has started embedding hints.
- **Shell/JSON quoting** of `Global\Huntress...` mutexes: build the submit JSON with python/jq, not by hand in a shell string.
- **capstone `ret` has an empty op_str**: `f"{m} {o}"` gives `"ret "`. Strip it, and convert immediates to decimal.
- **Cumulative zip**: check whether the old groups' sha256 match a previous day's confirmed bytes. If yes, those answers carry over;
  spend the time on the NEW group only (D4-D6 took minutes because of this).
- **Recursive unzip** destroys nested containers (.jar/.apk) and their `dNN--` prefix; keep them whole.
- **Same field name, different `kind`** (D8 elf_class/machine): a solver keyed only on the field name emits `ELF64` for an integer
  question. Read `answer_format.kind` per id.
- **Huge members** (D8: 67 MB Swift static-stdlib ELF): any per-key xor brute force or per-field re-parse blows a 10 s window.
  Cheap encodings first (raw magic, base64 magic `SENGR`), crc-gate every hit, parse each member once.
- **Decoy magics** (D9 Nim): the code that CHECKS the magic embeds `"HCFG"` (and an assert message) as literals, so the first
  raw hit is not the blob. A decoder that returns on the first crc-"valid" hit (empty len 0 => crc32(b"")==0 passes!) stops
  early; require non-empty JSON that parses, then keep scanning, then try the base64 form.
- **Location fields per scan path** (D12): a decoder with raw AND base64 branches must return the hit offset from BOTH;
  the raw branch's missing offset cost 2 POSTs. Before submitting, assert no `none` where a config was decoded.
- **`strings -t d` offsets on Nim/Swift literals**: the byte before the text can be printable (Nim's strlit flag 0x40 = `@`), so
  `strings` reports offset-1 (30695). Take offsets from `grep -abo`/`re.finditer(...).start()` on the exact token.
- **Jar members are deflated**: `grep HCFG file.jar` finds nothing. Inflate the class, read constant-pool strings, base64-decode.
  In a fat jar (Kotlin/Scala/shaded) scan the Main-Class first; a full scan of ~3000 runtime classes eats timed windows.
- **Stripped builds** in variants (D1 slot, D2 Mastery set2, D8 Mastery d01): no recover_code symbol. Answer what the question
  defines for absence (`[]` for the disassembly, `none` where allowed), has_symtab=false. The old leaf `mov eax, imm; ret` guess
  failed all 5 D8 Mastery sets.
- **Renamed designated function** (D1 TT section-beacon): the question still says recover_code. Answer `none` (when the format allows it), not the other function's constant.
- **Tool parity** (2026-10-07): ilspycmd, dotnet, rustfilt, GoReSym (`GoReSym -t -p file`), rabin2 are installed in
  `bin/`; monodis/de4dot are not (dnfile covers .NET metadata).
- **Timed windows are ~6-12 s** (TT; D9 TT 10 s, Mastery 20-27 s for 5 sets, download is ~half of it): D2 TT/Mastery attempts expired from download/orchestration latency, not solver speed (the solver ran in 0.3-0.5 s).
  After editing hctf/*.py, restart the orchestrator. D1/D2 runs used stale modules and kept sending only the slot0 ids.
- **PE machine map must include 0x8664 → `x86-64`**: a from-scratch replay once emitted `0x8664` and failed TT twice.
