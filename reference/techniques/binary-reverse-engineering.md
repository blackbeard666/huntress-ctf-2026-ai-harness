# binary-reverse-engineering — technique log (days 1-10; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- One `evidence.zip` (AES, password `infected`). From Day 3 on it is CUMULATIVE: members `dNN--variant-XXX.<ext>`, one group per
  past day, plus ONE new container/language per day: D1 C ELF, D2 C++ (ELF or MinGW PE32+), D3 .NET dll (+runtimeconfig.json),
  D4 static stripped Go ELF, D5 static Rust ELF (debug_info), D6 Java .jar, D7 Kotlin fat .jar (5 MB, ~3300 entries), D8 Swift ELF
  (67 MB, static stdlib+Foundation+ICU, not stripped), D9 Nim ELF (60 KB, dynamic glibc, not stripped), D10 Zig ELF (134 KB,
  dynamic glibc, stripped, clang/LLD 19 zig-bootstrap in `.comment`) -- a Zig PE `.exe` in Mastery set2.
  Answer ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`.
- From Day 2 on, every new-day member carries the same embedded **HCFG** config blob: `'HCFG' | u8 ver | u8 xor_key | u16 len (LE) |
  u32 crc32 | xor'd JSON` (JSON at offset 12; crc32 is over the decoded plaintext). Only its storage location changes
  (`.hcfg` section, .NET FieldRVA array, Go/Rust rodata, base64'd in a Java/Kotlin constant pool, base64 Swift String literal in
  `.rodata` on D8, base64 Nim string literal in `.rodata` on D9). Scan raw bytes for `HCFG` AND for its base64 form `SENGR...` (raw `HCFG` can also be a false hit inside code: check crc).
  The JSON also carries never-asked keys (ipv4, windows_path, linux_path, service, host_model on D7): parse the whole dict so a new `config_<key>` id is free.
- The analysis is easy (headers, symbols, one config blob). The hard part is the GM's exact label for a few `exact_text` fields (format,
  machine, disassembly, symbol). The question set grows each day (9 → 17 → 24 → 32 → 40 → 48 → 56 → 80 → 90 → 100 fields); old groups reuse the same bytes,
  but D8 BACKFILLED old groups to 10 ids each (new: has_symtab, has_cpp_typeinfo/vtable, xor_key_hex, hcfg_version, compression_methods).
- The prompt's theme (Rust panics, D7 "coroutine state machine", D8 Swift "protocols", D9 Nim "runtime fingerprints") has NOT
  been asked since D4: the new group gets sha256, format, config_campaign/domain/mutex/url/crc32_hex + 1-3 extra ids
  (architecture D4-D5/D8-D10, hcfg_version D6-D7, elf_class/machine as INTEGERS D8-D9, `hcfg_offset` D9, `has_hcfg_section`
  D10). Usually exactly ONE
  never-seen field per day: grep the new group's ids against the solver's field table before anything else.
- Time Trial ≈ 6-16 s; Mastery = `setN.` prefixed copies, 2 sets (7-12 s) through D7, 5 sets / 400-450 ids / 20-27 s on D8-D9,
  3 sets / 300 ids / 28 s on D10; artifacts are named `delivery N: evidence.zip`.
- **D10 RELAXED the label fields**: 36 ids are now `kind: pattern` whose syntax ACCEPTS equivalents (format: "ELF or PE; case,
  ELF32/ELF64/PE32/PE32+ accepted"; machine/architecture: "standard tool or symbolic label, or decimal/hex code"; e_type and
  endianness: symbolic constant / readelf label / numeric code; .NET format: any container_runtime token with CLI/CLR/.NET). D8-D9's
  integer machine became pattern. Keep emitting the GM-confirmed spellings; the old REJECTED lists may be stale for pattern ids.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, different storage per container (`.hcfg` section, .NET FieldRVA, Go/Rust rodata,
  base64 inside a Java/Kotlin constant pool, base64 Swift/Nim string literal in ELF `.rodata` on D8/D9): scan raw bytes for `HCFG`
  and for `SENGR[A-Za-z0-9+/_-]*=*` (base64 of `HCFG`, std or urlsafe), decode, accept only if crc32(plain) matches AND the JSON
  parses -- keep scanning past a failing hit (D9 Nim had two raw `HCFG` decoys); never a fixed offset.
- **Location-as-answer (`hcfg_offset`, D9)** -- base-10 FILE offset of the first byte of the stored blob as it sits in the member
  (D9: the `S` of the base64 text). 30696 in all 6 D9 variants (single, TT, Mastery x5) but compute it: record `m.start()` of
  whichever scan hit (raw or base64) validated. For a raw-blob member it would presumably be the `HCFG` offset (unconfirmed).
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

**D4 "Go Fish"** (32 Qs; ~1.5 min, 1 wrong). New d04 = static, stripped Go ELF (go1.25 buildinfo). Reused the D3 solver unchanged for d01-d03.
- `go version -m` → GOARCH; HCFG blob sat in Go rodata (magic scan). `d04_analysis_architecture`: `amd64` (GOARCH) REJECTED → `x86-64`
  (ELF e_machine vocabulary). Lesson: "architecture" uses the container machine words, not the toolchain token.

**D5 "Rust Belt"** (40 Qs; 7 s, 0 wrong, no LLM). New d05 = static Rust ELF with debug_info. The D4 composite solver passed all 40
unchanged: format `elf`, architecture `x86-64`, HCFG config by magic scan. The Rust-specific theme (v0/legacy mangling, panic strings,
trait objects) was never asked; there is still no Rust-aware path (see reference/HARDENING.md).

**D6 "Pool Party"** (48 Qs; ~5 min, 1 wrong). New d06 = `d06--variant-000.jar` (Main-Class, class major 65).
- `7z x` the jar → `javap -v -p <Main>.class` → `static final String CONFIG` ConstantValue = base64 → HCFG blob (decodeConfig() checks the
  magic, key=b[5], len=b[6..7], b[12+i]^key). New field `hcfg_version` = header byte 4 (base-10 integer).
- `d06_analysis_format`: `jar_jvm` REJECTED (so the pe_cli container_runtime compound does NOT extend to Java) → `jar`.
- Solver bug fixed: recursive unzip dissolved the .jar into META-INF/... and lost the `d06--` prefix. Keep nested .jar/.apk/.war members whole.
- The D6 question text was REWRITTEN for formerly ambiguous fields: d01 disassembly now says "Intel or AT&T spelling accepted";
  d03 format says "one container_runtime token; CLI, CLR or .NET accepted; separators/case accepted". Read each question's full text and `syntax`.

**D7 "Routine Check"** (56 Qs; 3 min start→CORRECT, 1 POST, 0 wrong). New d07 = `d07--variant-000.jar`, a 5 MB Kotlin fat jar
(Main-Class `Day07Variant000`, class major 65, ~3300 entries incl. the kotlin/ runtime). d01-d06 bytes identical to D6 (sha256 match).
- `javap -v -p Day07Variant000.class` → `private static final String CONFIG` ConstantValue base64 → HCFG (ver 1, key 0x31, len 368,
  crc32 checked). Answers: format `jar` (again), config values verbatim, hcfg_version `1`. Copied the D6 solver; only change: jar
  scan visits the Main-Class first and runtime packages last, returning at the first valid HCFG (D6 code scanned every class).
- Unasked "state machine": `main` reads env `HUNTRESS_HOST_MODEL` → `evaluate()` lookupswitch (workstation→`success`/13 events,
  analysis→`decoy`/7, sandbox→`failure`/3); trace JSON `huntress.binary.dynamic_trace.v1`. If asked: read `javap -c`, never run it.
- TT 5.8 s of an 11 s window, Mastery 6.4 s of 12 s, both first-try CORRECT (set2 had d02/d04 as PE `.exe`).

**D8 "Swift Justice"** (80 Qs). New d08 = 67 MB static Swift ELF (~290k symbols, not stripped); old groups backfilled to 10 ids.
- **Read `answer_format.kind` first:** d08 elf_class/machine were `integer` → bit width `64` (not EI_CLASS `2`) and `62`.
- Eager `pyelftools` `iter_symbols()` and the headerless-XOR brute force each took 60 s+ on it (worker lost 120 s + a 66 s
  profile). Recon with `readelf`/`nm`/`strings`; config = base64 HCFG in `.rodata` (`strings -n 40 | grep -m3 '^SENGR'`).
- Mastery: 5 deliveries x ~31 MB; download ~4.6-10 s + solve ~8 s inside a 27 s window.
- **Mastery mutated a carry-over ELF:** a STRIPPED d01 (no .symtab). The question says "If that symbol is absent, submit []";
  the old "last `mov eax, imm32; ret` leaf" fallback answered `["mov eax, 8102","ret"]` and failed all 5 sets. Absent →
  `[]`, has_symtab `false`, symbols `[]`. Never substitute a heuristic for an absence the question defines.
- LIB: `lib.elf.fields(data)[1]` returns `elf_class_int`/`machine_int` for `kind == "integer"`.

**D9 "Nimble"** (90 Qs; 86 s start→CORRECT, 1 POST, 0 wrong). New d09 = `d09--variant-000.elf`, a 60 KB Nim-compiled ELF64
x86-64 EXEC (dynamic glibc, `.symtab` kept, 333 symbols, no `.comment`). d01-d08 answered unchanged by the copied D8 solver (89/90).
- Recon (worker, 6 tool calls): `grep -abo HCFG` → 2 hits (30633 = assert text ``raw[0 .. 3] == "HCFG"``, 30664 = the Nim literal
  `"HCFG"` used by the magic check; neither decodes); `grep -ao 'SENGR[A-Za-z0-9+/=_-]*'` → 508-char base64 → HCFG ver 1,
  key 0x51; `objdump -d -M intel --start-address=...` on `encodedConfig__v000_u31` (`mov eax,0x1fc; lea rdx,[rip+..] <TM__..._25>; ret`)
  and `decodeConfig__v000_u33` confirmed the layout. Unasked: config keys ipv4/paths/service/host_model and Nim procs
  `evaluate__v000_u7` / `campaign__v000_u82` (D7-style branch logic; read statically if ever asked).
- New field `d09_analysis_hcfg_offset` (`kind: integer`) = **30696 = 0x77e8 = file offset of the base64 text's first byte**
  (literal struct at 0x77e0 = 8-byte cap `fc01..0040`, VA 0x4077e8). Solver change: record `m.start()` of the validated
  `SENGR` match. Answers: format `elf`, architecture `x86-64`, machine `62` (integer).
- Lost time: one jq call selected `.answer_id` (null); contract questions use `.id`.
- TT 10 s window: 6.95 s in-window (download 3.45, solve 2.92), CORRECT first try. Mastery 20 s window, 5 sets / 450 ids:
  12.87 s in-window (download 6.62, solve 5.38), CORRECT first try.

**D10 "Zig Zag"** (100 Qs; ~33 s start→CORRECT, 1 POST, 0 wrong). Prompt: "Zig promises one binary for every platform. Compare the
ELF and PE service descriptors side by side". New d10 = `d10--variant-000.elf`, 134 KB Zig-built ELF64 x86-64 (dynamic glibc,
stripped; `.comment` = clang/LLD 19.1.7 zig-bootstrap). The copied D9 solver answered everything else unchanged (d01-d09 + d10 sha/format/arch/machine/config).
- HCFG sits RAW in a writable `.hcfg` section (`objdump -s -j .hcfg`: `HCFG 01 61 7001 ad03dace` = ver 1, key 0x61, len 368,
  crc 0xceda03ad) -- the generic magic scan found it. Config `BR10-000` / `node-000.day10.example.invalid`.
- The ONE new field: `d10_analysis_has_hcfg_section` (enum) = `true`. Worker: `readelf -SW | grep hcfg`, grep the solver's field
  dispatch, add a generic `has_(\w+?)_section` branch over the parsed section names (ELF and PE). 3 tool calls.
- The prompt's "ELF and PE side by side" only materialised in Mastery set2 (d10 as a Zig PE: format `pe`, machine `x86-64`,
  has_hcfg_section `true`). No cross-container comparison field was asked.
- TT 16 s window: in_window 2.85 s (download 0.92, solve 1.31). Mastery 3 sets / 300 ids, 28 s window: in_window 5.59 s (download
  1.37, solve 3.62). Both CORRECT first try (BR10-007 / -001 / -004).

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
| format / architecture (Swift D8, Nim D9 ELF) | `elf` / `x86-64`; D9 machine integer `62` (source language never changes the container label) | — |
| C++ symbols (ELF) | bare Itanium mangled name (`_ZNK...`, `_ZTV...`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` (function), `.rdata$<mangled>` (vtable) | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` | list without "" |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates (D6 text says AT&T is also accepted) | hex imm, `"ret "`, `mov eax,0x..` |
| metadata_version | BSJB root string `v4.0.30319` | net8.0 / TFM / assembly version |
| config_* | values verbatim from the decoded HCFG JSON (mutex keeps ONE backslash) | JSON-escaped `\\` |
| hcfg_version | header byte 4 as a decimal integer | — |
| has_hcfg_section (D10, enum) | `true` when a section is literally named `.hcfg` (ELF Zig + PE Zig both `true`) | — |
| hcfg_offset (`kind: integer`, D9) | decimal FILE offset of the stored blob's first byte (base64 text start: `30696`), single+TT+Mastery x5 | — (not tried: VA 0x4077e8, struct 0x77e0, `strings -t d` 30695) |
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
