# binary-reverse-engineering — technique log (days 1-8; updated after every day)

How this lane has looked so far (OBSERVATIONS, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- One `evidence.zip` (AES, password `infected`). From Day 3 on it is CUMULATIVE: members `dNN--variant-XXX.<ext>`, one group per
  past day, plus ONE new container/language per day: D1 C ELF, D2 C++ (ELF or MinGW PE32+), D3 .NET dll (+runtimeconfig.json),
  D4 static stripped Go ELF, D5 static Rust ELF (debug_info), D6 Java .jar, D7 Kotlin fat .jar (5 MB, ~3300 entries), D8 Swift ELF
  (67 MB, static stdlib+Foundation+ICU, not stripped). Answer ids `dNN_artifact_sha256_K` / `dNN_analysis_<field>`.
- From Day 2 on, every new-day member carries the same embedded **HCFG** config blob: `'HCFG' | u8 ver | u8 xor_key | u16 len (LE) |
  u32 crc32 | xor'd JSON` (JSON at offset 12; crc32 is over the decoded plaintext). Only its storage location changes
  (`.hcfg` section, .NET FieldRVA array, Go/Rust rodata, base64'd in a Java/Kotlin constant pool, base64 Swift String literal in
  `.rodata` on D8). Scan raw bytes for `HCFG` AND for its base64 form `SENGR...` (raw `HCFG` can also be a false hit inside code: check crc).
  The JSON also carries never-asked keys (ipv4, windows_path, linux_path, service, host_model on D7): parse the whole dict so a new `config_<key>` id is free.
- The analysis is easy (headers, symbols, one config blob). The hard part is the GM's exact label for a few `exact_text` fields (format,
  machine, disassembly, symbol). The question set grows each day (9 → 17 → 24 → 32 → 40 → 48 → 56 → 80 fields); old groups reuse the same bytes,
  but D8 BACKFILLED old groups to 10 ids each (new: has_symtab, has_cpp_typeinfo/vtable, xor_key_hex, hcfg_version, compression_methods).
- The prompt's theme (Rust panics, D7 "coroutine state machine", D8 Swift "protocols") has NOT been asked since D4: the new group
  gets sha256, format, config_campaign/domain/mutex/url/crc32_hex + 1-3 header ids (architecture D4-D5/D8, hcfg_version D6-D7,
  elf_class+machine as INTEGERS D8). Read the ids AND each `answer_format.kind` first.
- Time Trial ≈ 6-11 s; Mastery = `setN.` prefixed copies, 2 sets (7-12 s) through D7, 5 sets / 400 ids / 27 s on D8; artifacts are
  named `delivery N: evidence.zip`.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **HCFG location / encoding** -- same blob, different storage per container (`.hcfg` section, .NET FieldRVA, Go/Rust rodata,
  base64 inside a Java/Kotlin constant pool, base64 Swift String literal in ELF `.rodata` on D8): scan raw bytes for `HCFG` and
  for `SENGR[A-Za-z0-9+/_-]*=*` (base64 of `HCFG`, std or urlsafe), decode, accept only if crc32(plain) matches; never a fixed offset.
- **xor key / config values** -- re-roll per variant; derive from the header byte, never from the sample.
- **Container per member** -- ELF vs PE32+ `.exe` re-rolls per member: Mastery set2 had d02 C++ as `.exe` (D3-D5, D7) and d04 Go as
  `.exe` (D4, D5, D7); D6 set2 had both as ELF. Labels come from the header of THIS member (Go PE: format `pe`, architecture `x86-64` from Machine).
- **Variant index per group** -- `dNN--variant-XXX` re-rolls per group and mode (D7 TT: d03-001, d04-006, d07-005 ...); sizes
  and config values change, names/layout don't. D7 TT bytes were identical to Mastery set1; D8 TT re-used exactly the D7 TT
  old-group indices and its d08 member was variant-000 (= single-solve sha256).
- **Mastery packaging** -- `setN.` prefixed ids, each set its own `delivery N: evidence.zip` (same filename): pair by sha256.
  Set count re-rolls: 2 (D2-D7), 5 on D8 (d08 variant-000..004 = set1..5, set2/set4 had d02/d04 as PE): loop over every `setN.`.
- **answer_format.kind for the same field name** -- D8: `d01_analysis_elf_class`/`machine` exact_text (`ELF64`/`x86-64`) and
  `d08_analysis_elf_class`/`machine` integer (`64`/`62`) in ONE contract. Rule: dispatch on `kind`, not on the field name.
- **Field set per old group** -- old groups gain ids over days (D8 padded every group to 10). Answer by field name from the
  parsed facts dict of THAT member; an unknown field must log and fall through, never crash. Keep the older 56/112-id cases passing.

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
| Packed / high entropy / `UPX!` | `lib.binary.packer_info` → `upx -d` on a COPY (not seen yet) |
| Real code-reversing question (not seen yet) | `rizin -q -c "aaa; pdf @ sym.<fn>"`; Ghidra headless `lib.binary.ghidra_decompile` (heavy, last resort) |

## Day by day
**D1 "ELF Aware"** (9 Qs; ~14 min of submits, 4 wrong). One plain C ELF64 x86-64 EXEC, not stripped. Fields: class, endianness,
machine, e_type, `.huntress` marker (NUL-terminated string), has_symtab, exported (designated) symbol, recover_code constant, entry point.
- Tools: readelf -h/-S/-x, objdump (`mov $imm,%eax; ret`), pyelftools + capstone in the solver.
- Spelling laws learned the hard way: `ELF64` (not ELFCLASS64), `ET_EXEC` (not EXEC), `x86-64` (not EM_X86_64), `little` (not "little endian").
  The local wrong-answer cap (3 at the time) was hit on machine/endianness and needed operator probing.
- TT variants: 4-member "slot" bundle (`slot-0.elf`..`slot-3.elf`) with 36 answer ids `slotN_<qid>` → match ids to members by slot number.
  Profiles: stripped (has_symtab=false), "section-beacon" (designated fn renamed `inspect_section`; recover_code format turned
  exact_text with `none` allowed; submitting the renamed fn's constant was WRONG → `none` derived, still unconfirmed).

**D2 "Mangled"** (17 Qs; ~22 min, 5 wrong). Zip = `day01-c.elf` + C++ build (`day02-cpp.elf`, or MinGW PE32+ `.exe` in variants).
- C++ config in section `.hcfg` = HCFG blob (first sighting). Decode: key=b[5], len=b[6]|b[7]<<8, plain=b[12+i]^key, verify crc32.
- Symbols: `mangled_score_symbol` = the mangled `<Class>::score` (`_ZNK..5scoreEPKc`), `vtable_symbol` = `_ZTV<class owning score>`
  (an unused base class has only _ZTI/_ZTS, no _ZTV → not the answer). Answer the MANGLED form, not the demangled one.
- `cpp_format`: ELF, ELF64, HCFG, elf64-x86-64, json all rejected → `elf`.
- PE sets kept failing in Mastery for hours: pe, exe, pe32+, coff, mz, elf were "refuted" one by one. Root cause: a set POST is
  all-or-nothing, and the real errors were the PE SYMBOL fields. For PE/COFF the GM wants the COMDAT section-name form
  `.text$<mangled>` (functions) / `.rdata$<mangled>` (vtable/typeinfo). With those fixed, `pe` was accepted.
- Pitfall: the mutex `Global\HuntressBR02_NNN` was sent with a doubled backslash (shell quoting), so the whole first batch failed.

**D3 "Table Manners"** (24 Qs; ~1 h 48 min, ~60 wrong, the costliest binary day). Cumulative: d01 C ELF, d02 C++ ELF (same bytes as D2,
so the D2 answers carried over after a sha256 match), d03 .NET 8 PE32 i386 dll.
- .NET: `dnfile` gave the BSJB metadata version (`metadata_version` = root version string, e.g. v4.0.30319) and the FieldRVA blob;
  the `Campaign()` IL confirmed the HCFG layout. machine `i386` (x86 REJECTED for PE 0x14c).
- New d01 JSON fields: section_names = pyelftools `iter_sections()` names INCLUDING the leading "" NULL section; symbols = non-empty
  .symtab names in table order, dupes kept; disassembly = recover_code as capstone intel `"{mnemonic} {op_str}"` with DECIMAL immediates.
  Rejected disassembly forms: hex immediates, `"ret "` (trailing space from empty op_str), no space after comma, AT&T, main, whole .text, _start..hlt.
- `d03_analysis_format` = `pe_cli` (container + ECMA-335 CLI runtime). It took ~50 rejected synonyms first (pe, dotnet, .net, cil,
  msil, clr, managed, assembly, bsjb, dotnet_pe, ...). Worker spent 73 turns / 13.6 min plus operator probing. Lesson: compose labels from spec tokens.

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
- Unasked "state machine": `staged$1 extends ContinuationImpl {int label; Object L$0}`; `main` reads env `HUNTRESS_HOST_MODEL`
  (default `workstation`) → `evaluate()` lookupswitch: workstation→`success`/13 events, analysis→`decoy`/7, sandbox→`failure`/3,
  else `failure`/1; prints trace JSON `huntress.binary.dynamic_trace.v1` {branch, event_count, campaign, family
  `loopback_stage_transfer`}. If branch/event questions appear: read them statically from `javap -c`, never run the jar.
- TT 5.8 s of an 11 s window, Mastery 6.4 s of 12 s, both first-try CORRECT (set2 had d02/d04 as PE `.exe`).

## Day 8 — Swift Justice (Swift ELF, 67 MB)
- **Read `answer_format.kind` first:** the same field family changes form by kind (D8 elf_class went exact_text → integer;
  the answer became the bit width `64`, not EI_CLASS `2`).
- Huge Swift ELF (~290k symbols): eager `pyelftools` `iter_symbols()` and the D7 headerless-XOR brute force each take
  60 s+ (the worker lost 120 s + a 66 s profile). Use `readelf`/`nm`/`strings` for recon; in solve.py only look up the
  symbols you need (lazy). The config is a base64 HCFG blob in the binary (`strings -n 40 | grep -m3 '^SENGR'`).
- Mastery: 5 deliveries x ~31 MB; download ~4.6-10 s + solve ~8 s on Homebase inside a 27 s window.
- **Mastery mutates the carry-over ELFs:** variant d7c5e016 shipped a STRIPPED d01 ELF (no .symtab). The question says
  "If that symbol is absent, submit []" -- the solvers' old "last `mov eax, imm32; ret` leaf" fallback answered
  `["mov eax, 8102","ret"]` in every set and failed all 5 sets. Absent symbol -> `[]`, has_symtab `false`, symbols `[]`.
  Never substitute a heuristic for an absence the question defines.
- LIB (ratchet D8): `lib.elf.fields(data)[1]` also returns `elf_class_int` ("64") and `machine_int` ("62") for
  `answer_format.kind == "integer"`; text forms stay in `elf_class`/`machine` (`knowledge.ELF_CLASS_BITS`).

## GM answer conventions learned
| Field family | Accepted form | Rejected (never resubmit) |
|---|---|---|
| elf_class (`answer_format.kind` exact_text) | `ELF64` / `ELF32` (readelf style) | ELFCLASS64 |
| elf_class (`kind: integer`, D8 `d08_analysis_elf_class`) | the bit width `64` / `32` (single, TT, Mastery x5) | `2` / `1` (raw EI_CLASS byte; GM-rejected D8) |
| machine (`kind: integer`, D8 `d08_analysis_machine`) | decimal e_machine (`62` = x86-64; read u16 at offset 18 in EI_DATA order) | — |
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
| format / architecture (Swift ELF, D8) | `elf` / `x86-64` (source language never changes the container label) | — |
| C++ symbols (ELF) | bare Itanium mangled name (`_ZNK...`, `_ZTV...`) | the demangled form |
| C++ symbols (PE/MinGW) | COMDAT section name `.text$<mangled>` (function), `.rdata$<mangled>` (vtable) | bare mangled name |
| section_names (JSON) | pyelftools order INCLUDING the leading `""` | list without "" |
| symbols (JSON) | non-empty .symtab names, table order, dupes kept | list with the "" entries |
| disassembly (JSON) | capstone intel `"mov eax, 8100"`, `"ret"`, decimal immediates (D6 text says AT&T is also accepted) | hex imm, `"ret "`, `mov eax,0x..` |
| metadata_version | BSJB root string `v4.0.30319` | net8.0 / TFM / assembly version |
| config_* | values verbatim from the decoded HCFG JSON (mutex keeps ONE backslash) | JSON-escaped `\\` |
| hcfg_version | header byte 4 as a decimal integer | — |
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
- **Jar members are deflated**: `grep HCFG file.jar` finds nothing. Inflate the class, read constant-pool strings, base64-decode.
  In a fat jar (Kotlin/Scala/shaded) scan the Main-Class first; a full scan of ~3000 runtime classes eats timed windows.
- **Stripped builds** in variants (D1 slot, D2 Mastery set2, D8 Mastery d01): no recover_code symbol. Answer what the question
  defines for absence (`[]` for the disassembly, `none` where allowed), has_symtab=false. The old leaf `mov eax, imm; ret` guess
  failed all 5 D8 Mastery sets.
- **Renamed designated function** (D1 TT section-beacon): the question still says recover_code. Answer `none` (when the format allows it), not the other function's constant.
- **Tool parity** (2026-10-07): ilspycmd, dotnet, rustfilt, GoReSym (`GoReSym -t -p file`), rabin2 are installed in
  `bin/`; monodis/de4dot are not (dnfile covers .NET metadata).
- **Timed windows are ~6-12 s**: D2 TT/Mastery attempts expired from download/orchestration latency, not solver speed (the solver ran in 0.3-0.5 s).
  After editing hctf/*.py, restart the orchestrator. D1/D2 runs used stale modules and kept sending only the slot0 ids.
- **PE machine map must include 0x8664 → `x86-64`**: a from-scratch replay once emitted `0x8664` and failed TT twice.
