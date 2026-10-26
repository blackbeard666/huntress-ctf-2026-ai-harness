# metadata-forensics — technique log (days 1-26; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
  **D23 mutated the WHOLE carry-over kit** (values that sat constant D13-D22 re-rolled: PE/ELF arch, audio codec, video
  dims, Mach-O became FAT, zip CD order shuffled) -- every carried extractor must parse the general case, not D-day's sample.
- Every day = ONE evidence zip (plain Deflate, no password). D1-7: one tiny member, one fact; D8-9: cumulative kit in
  every mode; D10-14: one field everywhere. **D15+ split the modes**: single = 1 field (the new member), TT = cumulative
  kit (D15 20 -> D26 31 fields, +1/day), Mastery = N kits x the TT set (N=5 to D21, then +1/day: 9 D25, 10 D26), incl. a
  cross-member "synthesis" question. Pre-arm EVERY earlier family AND the synthesis before the timed run.
- Member families: note/text -> jpg -> png -> pdf -> inner zip -> Go PE (D9-11) -> .NET dll (D12) -> MSI (D13) -> LNK
  (D14) -> OOXML `.docx` (D15) -> `.eml` (D16) -> WAV (D17) -> MP4 (D18) -> ELF (D19) -> Mach-O `macos-001.bin` (D20)
  -> APK `mobile-001.apk` (D21) -> JAR `application-001.jar` (D22) -> SQLite `database-001.sqlite` (D23) -> EVTX
  `events-001.evtx` (D24) -> registry hive `hive-001.hiv` (D25) -> Prefetch `trace-001.pf` (D26). D19-22 = runnable
  formats; D23 APPLICATION DATA (db header); D24-26 = the WINDOWS DFIR block (D24 first STRUCTURE WALK; D25 first
  POINTER FOLLOW: header offset -> cell; D26 first DECOMPRESS-THEN-PARSE: single was `MAM\x04` Xpress-Huffman-wrapped).
  fmt word = an ABSTRACT namespace sometimes (`email` not `eml`; `media` for audio D17 AND video D18, ffprobe
  vocabulary), else the plain format (`pe` `msi` `lnk` `elf` `macho` `apk` `jar` `sqlite` `evtx` `prefetch`) -- read it from the question.
- Fields, one new per day (full list in "Day by day"; D25 `registry.hive_root_name`, D26 `prefetch.executable_name`).
  Question `Determine <fmt>.<field> for <member>`; id `dNN-<family>-NNN-<fmt>-<field>` (`.`/`_` -> `-`), `dNN` = the
  family's first day; `<family>` != `<fmt>` only for media (`d17-audio-001-media-`, `d18-video-...`). D25 fmt word
  `registry` (NOT the magic/lib name `regf`) -- the GM names the DOMAIN, the library may name the file format.
- Flavor text promises extra findings that are NEVER asked (D19 deployment groups, D20 fleet, D21 clones, D22 nested
  launchers, D23 "truncated, embedded ... impossible claim", D24 "selectively shortened timeline", D25 "regroup the
  systems, isolate the planted hive", D26 "connect execution traces to the correct hosts"). Graded = the STRUCTURAL
  truth; names/extensions/secondary metadata are the lie ("renamed" D25 = base-block name decoy; "even after filenames
  changed" D26 = `trace-001.pf` instead of `NAME-HASH.pf`). Titles pun on the field (D19 "Little Endian" = EI_DATA;
  D20 "Universal Appeal" = fat; D21 "Package Deal"; D22 "Main Character Energy" = `Main-Class`; D23 "Page Me Maybe";
  D24 "Event Horizon" = record count; D25 "Hive Mind" = root key name; D26 "Before You Go" = Prefetch, what Windows
  prepares BEFORE an exe runs). The flavor's depth shows up as TIMED carry-over mutations, not new fields.
- Singles: D1-9 ~27-60 s; one convention submit lost D10, D13, D15, D20; two D16. Prebuilt `lib.meta` race HITS: D18
  ~5 s, D19 ~13 s, D22 ~19 s, D23 ~29 s, D26 ~29 s (`prefetch.py`; worker cross-checked, `--from-solver`). MISSES ->
  live worker: D17 ~24 s, D21 ~32 s, D24 ~21 s, D25 ~17 s (fmt word `registry` vs lib `regf`).
  TT/Mastery: CORRECT every day; D15-17 + D19 after a generalize (synthesis dispatch); D23 after one wrong TT submit
  (list ORDER); since D24 first try in seconds (D26: TT 31 fields 4.7 s, Mastery 310 = 10 sets 8.0 s).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen". Names drift: D1-14 `metadata-day-NN-evidence[-0N].zip`; D15-25 TT
  `evidence.zip`, Mastery `evidence-01.zip` holding `evidence-01..NN.zip` (N=5; D22 6 ... D25 9; D26 10 -> `-10.zip`). Route by
  the ref's text before `->` and by sha256, never a hard-coded name.
- **Field-set / set count** -- D7 TT 11 / Mastery 22; D8-9 12-13 everywhere; D10-14 one; D15 1/20/100 ... D21 1/26/130
  (+1 field/day); D22 1/27/162 (6 sets); D23 1/28/196 (7 sets); D24 1/29/232 (8 sets); D25 1/30/270 (9 sets); D26
  1/31/310 (10 sets -- `set10.` sorts before `set2.` as a string: order sets numerically).
  Enumerate `setN.` prefixes from the live ids. Families: identity + `d04-jpeg` `d05-png` `d06-pdf` `d07-zip` (eocd,
  CD names) `d09-pe` (machine, entry RVA, OriginalFilename) `d12-dotnet` `d13-msi` `d14-lnk` `d15-ooxml` `d16-email` `d17-audio` `d18-video` `d19-elf`
  `d20-macho` `d21-apk` `d22-jar` `d23-sqlite` `d24-evtx` `d25-registry` `d26-prefetch` + synthesis. Dispatch on the answer-id SUFFIX
  (reference solver answering all 31: `challenges/day26/metadata-before-you-go/solver/solve.py`; lane seed `local_answer` +
  `synthesis_answer` + lib.meta).
- **fmt word vs registry key vs id family** -- D16 `email.*` (lib said `eml`); D17/D18 `media.*` with ids
  `d17-audio-`/`d18-video-`; D19 `elf.e_machine_u16_hex` (-> `e-machine`); D20 `macho.cpu_type_set`; D21
  `apk.package_name`; D22 `jar.main_class`; D23 `sqlite.page_size_bytes`; D24 `evtx.record_count`; D25
  `registry.hive_root_name` (DOMAIN word, lib/magic `regf`, lib field `root_key_name` -> MISS); D26
  `prefetch.executable_name` (domain word = lib fmt, libscca field name -> HIT). Vocabulary = the home tool (ffprobe)
  or the spec struct; header codes ALWAYS raw `0x` hex. Rule: take `<fmt>.<field>` from the question (or the slug
  after `-NNN-`), map fmt synonyms (`email`~`eml`/`mime`; `media`~`audio`/`video`/`av`; `jar`~`war`; `sqlite`~`db`;
  `evtx`~`evt`/`eventlog`; `registry`~`regf`/`hive`; `prefetch`~`pf`/`scca`) and field synonyms, route the extractor
  by MAGIC + member names, fall back to the same field under any fmt.
- **Member values (D23+: EVERYTHING re-rolls every day)** -- never cache across sets/modes. Seen: identity sizes
  (D23+ 72-378 B, CRLF/LF, BOM `true` in some sets), jpg/png dims, PDF `1.0`-`2.0`, zip entries 2-13, PE Machine
  (`0x014c` `0x8664` `0xaa64` `0x01c0` `0x01c2` `0x01c4` `0x01f0` `0x0ebc` `0x5064` `0x0266`), audio codec under
  `audio-001.wav` (`pcm_s16le` `mp3` `opus` `vorbis` `aac` from `ftyp M4A `, `flac`), video dims, ELF e_machine (`0x003e`
  `0x0003` `0x0028` `0x002b` `0x0102` `0x0016` `0x00b7` `0x00f3`), Mach-O thin/FAT 2-3 slices (`0x00000007` `0x0000000c`
  `0x00000012` `0x01000007` `0x0100000c` `0x01000012` `0x0200000c`; thin LE-32 `ce fa ed fe`), APK `io.`/`net.`/`org.`/
  `com.*`, Main-Class 1-4 parts, SQLite page 512-65536, EVTX 3-119 records (one chunk so far), registry root
  `[A-Za-z0-9]{6,32}` (root cell @0x20 so far -- follow the pointer anyway), Prefetch WRAPPER (D26 single `MAM\x04`
  Xpress-Huffman 3896 B -> SCCA v30; TT + all 10 Mastery sets UNCOMPRESSED SCCA v30 `1e 00 00 00 SCCA` ~15.3 KB; names
  `<WORD>[NN].EXE` uppercase). Rule: decode the general structure (byte order from the file, walk every slice/chunk/
  stream, follow every offset, decompress any wrapper by its magic), never the D-day sample's constant.
- **List ORDER under mutation (D23)** -- D8-D22 zips stored CD entries already sorted, so "CD order" and "sorted"
  coincided; D23 shuffled the CD and the GM REJECTED CD order, accepted ascending sort. Fat Mach-O slices: ascending
  `0x%08x` accepted (fat_arch order != the accepted answer). Rule: every `json` list answer = values sorted ascending
  (string sort of the emitted spelling; dedupe sets), EXCEPT synthesis (= order by digest) and anything whose question
  states an order. Always `json.dumps(sorted(v), separators=(",",":"))` -- a Python list `str()`'d to repr is wrong.
- **Identity member roster** (D15+) -- THREE small text members (`evidence-note*.txt`, `evidence-note-copy*.txt`,
  `roster*.csv`; D24-25 timed names carry a random `-<6hex>` suffix, e.g. `roster-236466.csv`, ids keep the bare stem);
  ids `<member-stem>-{filename,size-bytes,md5,sha1,sha256,magic-prefix-hex-16,text-utf8-bom-present}`. Filename
  question artifact = the container only -> map the stem by PREFIX. D25 Mastery: 2 of 9 sets had no roster member
  (a different kit: macos/docx/inner-zip) -> answer only the ids each set's contract lists. D26 Mastery: every set has
  all three members but asks a DIFFERENT 7 of the 21 identity ids (31 ids/set throughout) -- enumerate per set.
- **Synthesis / cross-member** (D15+) -- id `metadata-day-NN-synthesis-<algo>-order` (TODAY's NN), kind `json`, norm
  `case_insensitive`, "Compute the full-file SHA-256 digest of each named file, then submit a compact JSON array of
  their filenames in ascending digest order. Files: [...]". Rule: regex `Files:\s*(\[.*?\])`, hash each under the
  ref's container, sort by hex digest -- `lib.meta.synthesis.digest_order(question, get_bytes, algo)`, get_bytes bound
  INSIDE the per-set worker. Shape: note + re-picked kit members + TODAY's member; 4 names D15-20, FIVE D21-26 (D26
  note/{`evidence-drop-001.zip`|`document-001.pdf`}/`document-15-001.docx`/macos/pf). The list differs between the 409
  contract and the live attempt AND between sets of one Mastery -- parse each set's own text. Only sha256 seen.
- **Decoys** -- renamed copies, misleading extensions, secondary metadata (EXIF, catalog /Version, D25 regf base-block
  FileName @0x30 -- `<word>-<8hex>.hiv` or a truncated kebab path, never the root): answer from the structure the
  field names. Kits pool `collector-001.elf` with `MZ` members: `elf.*` of a non-ELF = `none`.
- **Answer kinds** -- `exact_text`, `integer`, `pattern` (hashes case-insensitive; `0x`-hex `trim` only -> lowercase),
  `enum` (`accepted_values`), `json` (compact array, "exact values and order" -- see List ORDER above).
  `*_set`/`*_names`/`*_targets` under `json` = a list even with ONE element (D20 `["0x0100000c"]`).
- **Question-text tags** -- D9 timed ` [assigned-artifact-sha256:<64 hex>]` suffix; D15+ timed ``Inspect `<member>`. ``
  prefix. Strip both before reading names; route by id + `artifact`.
- **Nesting depth** -- the asked file may sit 2-3 zips deep (Mastery D7); resolve by the name after `->`, never answer
  from an enclosing zip. OOXML/APK/JAR members ARE zips -- parse them as the asked member, don't descend as a wrapper.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `<zip> -> <member>` in `questions[].artifact` | python `zipfile` read of the member in memory (`7z l -slt` for orientation) |
| filename / size / md5 / sha1 / sha256 | `stat -c %s`, `md5sum sha1sum sha256sum` on the member bytes; the id stem names WHICH member |
| "first sixteen bytes", "magic", "extension claims" | `xxd -p -l 16 <member>` (lowercase, no spaces); `file -k` only for orientation |
| `text.*_bom_present` | `xxd -l 4`: UTF-8 BOM `ef bb bf` (UTF-16LE `ff fe`, BE `fe ff`) -> `true`/`false` |
| `jpeg.*dimensions*` / SOF | walk segments from `ffd8` by length to SOFn (`ffc0..ffcf` minus c4/c8/cc): P, Y=height, X=width |
| `png.ihdr_*` | `xxd -s 16 -l 8` = width,height (BE u32). Chunk walk = len/type/data/CRC (`lib.stego.png_chunks`) |
| `zip.eocd_*` | of the NAMED zip: last `PK\x05\x06` whose comment len reaches EOF; u16 @+10 total entries, u32 @+12 cd size, @+16 cd offset. `0xFFFF` -> ZIP64 (`PK\x06\x07` -> `PK\x06\x06` u64 @+32) |
| `zip.central_directory_*` | walk `PK\x01\x02` from cd offset: name len @+28, extra @+30, comment @+32, name @+46. Raw stored paths, then SORT ascending (D23: CD order REJECTED); UTF-8 if flag 0x800 else cp437 |
| `pdf.header_version` | `head -c 16 f | xxd` -> `%PDF-x.y` at offset 0; catalog `/Version` is a diagnostic only |
| `pe.coff_*` | `MZ` -> e_lfanew u32 @0x3C -> require `PE\0\0` -> Machine u16 @+4 (any IMAGE_FILE_MACHINE_*, D23 saw 7 values); OptionalHeader magic @+24 (`0x10b`/`0x20b`) |
| `pe.address_of_entry_point_*` / `pe.image_base*` | opt = e_lfanew+24: AddressOfEntryPoint u32 @opt+16 (RVA); ImageBase @opt+28 (PE32) / u64 @opt+24 (PE32+). objdump "start address" is the VA |
| `pe.version_*` | `pefile` resource dir only -> `FileInfo..StringTable..entries`; id tail -> key ignoring case/`-_`. Shell: `strings -e l f.exe \| grep -A1 OriginalFilename` |
| `elf.*` (`7f 45 4c 46`) | EI_CLASS @4 (1=32, 2=64), EI_DATA @5 (1=LSB `<`, 2=MSB `>`) picks the byte order for EVERYTHING after @16: e_type u16 @16, e_machine u16 @18, e_entry @24. `xxd -s 16 -l 4 f` + `readelf -h f`. `lib.meta` fmt `elf` |
| `macho.*` (`cf fa ed fe` LE-64, `ce fa ed fe` LE-32, `fe ed fa ce/cf` BE; fat `ca fe ba be` / fat64 `ca fe ba bf`, always BE) | thin: cputype u32 @4 (byte order from the magic). Fat: nfat_arch u32 @4, then 20-B (fat64 32-B) fat_arch {cputype, cpusubtype, offset, size, align}; Java class shares `cafebabe` (major @6 >= 45). `cpu_type_set` = JSON list `"0x%08x"`, deduped, SORTED ascending (D23 fat 2-3 slices). `lib.meta` fmt `macho` |
| `apk.*` / `.apk` (`PK` + `AndroidManifest.xml` + `classes.dex`) | manifest is BINARY AXML (`03 00 08 00`): `aapt dump badging f.apk \| head -1`; stdlib `lib/meta/apk.py manifest_attr(axml, 'manifest', 'package')`. Triage routes APKs to `$mobile-android` -- ignore it |
| `jar.*` / `.jar/.war/.ear` (`PK` + `META-INF/MANIFEST.MF`) | `unzip -p f.jar META-INF/MANIFEST.MF` (CRLF, 72-B lines, ONE-space continuations); main section up to the first blank line; `Main-Class` verbatim. Spring Boot: `Start-Class` = app. `lib/meta/prebuilt/jar.py` |
| `sqlite.*` / `.sqlite/.db/.sqlite3` (`SQLite format 3\0` @0) | 100-B header, BIG-endian: page size u16 @16 (`1` = 65536), write/read ver @18/@19 (2 = WAL), file change counter @24, in-header db size (pages) @28, freelist @32/@36, encoding u32 @56 (1 UTF-8, 2 UTF-16le, 3 UTF-16be), user_version @60, application_id @68, version-valid-for @92, SQLITE_VERSION_NUMBER @96. `xxd -s 16 -l 2 f`; `file f` prints the summary; `sqlite3 f 'PRAGMA page_size'`. In-window `lib/meta/prebuilt/sqlite.py` (header + stdlib sqlite_master walk + browser history) |
| `evtx.*` / `.evtx` (`ElfFile\0` @0, `ElfChnk\0` @0x1000) | LE everywhere. File header: next_record_id u64 @24, chunk count u16 @42, version @36/@38 (3.2), flags u32 @120 (1 dirty, 2 full). Each 64 KiB chunk: first/last record number @8/@16, ids @24/@32, free-space offset u32 @48; records `2a 2a 00 00` from chunk+0x200, size u32 @+4, EventRecordID u64 @+8, FILETIME @+16. `record_count` = walk EVERY chunk's records up to its free offset (D24); `file f` prints chunks + next record no.; python-evtx `Evtx.Evtx` (worker-only). `lib/meta/prebuilt/evtx.py` |
| `registry.*` / `regf.*` / `.hiv` `NTUSER.DAT` `SYSTEM` (`regf` @0) | base block 4 KiB LE: seq1/seq2 u32 @4/@8, last written FILETIME @12, ver @20/@24 (1.3), root cell off u32 @0x24 (rel. to 0x1000), bins size @0x28, FileName UTF-16 @0x30 (64 B; DECOY for the root). Cell = i32 size (neg = used) + `nk`: flags u16 @+2 (0x20 COMP_NAME -> latin-1 else UTF-16LE; 0x04 HIVE_ENTRY = root), FILETIME @+4, subkeys @+0x14, list off @+0x1c, values @+0x24, value list @+0x28, name len u16 @+0x48, name @+0x4c (offsets after the size). `hive_root_name` = root nk name verbatim (D25). `xxd -s $((0x1000+root)) -l 128`; regipy (worker-only) |
| `prefetch.*` / `.pf` (`SCCA` @4, version u32 @0: 17/23/26/30/31; `MAM` @0 = Win10+ compressed) | `MAM` + type byte (low nibble 4 = Xpress-Huffman; 0x80 = CRC32 u32 follows), uncompressed size u32 @4, stream @8 (@12 with CRC) -> decompress FIRST. SCCA: file size u32 @12, exe name UTF-16LE @16 (60 B, NUL-terminated), path hash u32 @0x4C; run count / 8 last-run FILETIMEs / volumes per version. `.venv` `dissect.util.compression.lzxpress_huffman.decompress(b[8:])` (worker), `lib/meta/prebuilt/prefetch.py` (pure-Python, in-window) |
| `dotnet.*` / Mono assembly | data dir 14 -> CLI header -> `BSJB` -> `#~` -> Module row 0 Mvid (1-based #GUID idx) -> `uuid.UUID(bytes_le=..)`. `lib/meta/dotnet.py` |
| `msi.*` / `.msi` (OLE `d0 cf 11 e0`) | fast: `strings -n 6 x.msi \| grep -aoE 'ProductCode\{[0-9A-F-]{36}\}'`; exact: CFB `!_StringPool`/`!_StringData` -> `!Property`. `olefile` in venv |
| `lnk.*` / `.lnk` (`4c 00 00 00` + CLSID 00021401) | LinkFlags @0x14 (0x1 IDList, 0x2 LinkInfo, 0x80 Unicode); target = LinkInfo LocalBasePath (+CommonPathSuffix) verbatim, else IDList. `lib.meta.lnk:target_path` |
| `ooxml.*` / `.docx/.xlsx/.pptx` (`PK` + `[Content_Types].xml`) | External = `TargetMode="External"` in EVERY `*.rels` part; `unzip -p f.docx '*.rels' \| grep -o 'Target="[^"]*" TargetMode="External"'`; sorted |
| `email.*` / `.eml` | `grep -ai '^message-id' f.eml`; `lib.meta.prebuilt.eml.eml_value(data, {"field": f})`. Values VERBATIM (Message-ID keeps `<...>`) |
| `media.*` audio (`RIFF..WAVE`, `ID3`/`ff fb`, `OggS`, `fLaC`, `ftyp`, `1a 45 df a3`, `FORM..AIFF`) | route by MAGIC (D23 TT/Mastery: WAV, MP3, Ogg Opus, Ogg Vorbis all appeared under `audio-001.*`). WAV tag -> FFmpeg names (Conventions); Ogg: first packet `OpusHead` -> `opus`, `\x01vorbis` -> `vorbis`. Truth: bundled `ffmpeg -hide_banner -i f` |
| `media.*video*` / MP4-MOV (`....ftyp`), MKV/WebM, AVI | box walk `moov` -> first `trak` whose `mdia/hdlr` = `vide` -> `stsd` entry: w,h u16 BE @entry+32; cross-check tkhd, SPS crop. `lib.meta` fmt `media` |
| `*-synthesis-<algo>-order` / "Files: [...]" in the question | parse the list from the question text, hash each member of the same container, sort by digest, compact JSON of names |
| GUID field (`*-guid`) | spelling follows the SOURCE: stored string (MSI) verbatim braces+uppercase; binary (.NET) -> lowercase, no braces |
| exe-extension decoy (`MZ` without `PE\0\0` at e_lfanew) | literal `none` if the syntax offers it; never fall back to a later `PE\0\0` hit |
| "impostor", "renamed", "mislabeled", "embedded" | trust magic bytes at offset 0 of the NAMED member; a matching string deeper in the file is a decoy |
| answer_format kind `json` | `json.dumps(sorted(v), separators=(",",":"), ensure_ascii=False)` unless the field is an order (synthesis) |
| Mastery `set1.`..`setN.` ids | resolve each set's container separately; see delivery layouts |

## Day by day
**Days 1-14** (one field each, all timed first try): D1 identity -> D2 `magic-prefix-hex-16` -> D3 BOM -> D4 JPEG SOFn
`<w>x<h>` -> D5 PNG IHDR -> D6 `pdf.header_version` `x.y` -> D7 `zip.eocd_total_entries` of the INNER zip -> D8 CD names
(compact JSON; disk order happened to be sorted) -> D9-11 one Go PE: `coff_machine_u16_hex` `0x014c`, entry RVA
`0x%08x` (unpadded REJECTED), `version_original_filename` verbatim -> D12 `dotnet.mvid_guid` (`uuid.UUID(bytes_le)`
lowercase, no braces) -> D13 `msi.product_code_guid` (stored WITH braces; brace-less REJECTED) -> D14 `lnk.target_path_windows`.

**Days 15-25** (single = 1 new-family field; TT/Mastery = cumulative kit + synthesis): D15 `ooxml.external_relationship_
targets` (rels `TargetMode="External"` Targets SORTED; rels order REJECTED). D16 `email.message_id` (VERBATIM with `<>`;
2 lost: id regex -> `none`, stripped brackets). D17 `media.primary_audio_codec_name` (WAV PCM16 -> `pcm_s16le`). D18
`media.primary_video_dimensions` (first `vide` trak stsd -> `320x180`). D19 "Little Endian" `elf.e_machine_u16_hex`
(@18 in EI_DATA order -> `0x003e`). D20 "Universal Appeal" `macho.cpu_type_set` (THIN arm64 -> `["0x0100000c"]`;
`["arm64"]` REJECTED). D21 "Package Deal" `apk.package_name` (binary-AXML `<manifest package=>` verbatim, NOT
`android:label`). D22 "Main Character Energy" `jar.main_class` (MANIFEST.MF `Main-Class` verbatim, dotted, no
`.class`). D23 "Page Me Maybe" `sqlite.page_size_bytes` (u16 BE @16, `1` = 65536; timed kit MUTATED for the first
time -> 1 wrong TT submit on CD-order names). D24 "Event Horizon" `evtx.record_count` (walk `**\0\0` records of EVERY
chunk to its free-space offset u32 @48; live struct walk ~21 s). D25 "Hive Mind" `registry.hive_root_name` (base block
u32 @0x24 -> nk @0x1000+off+4 -> name len u16 @+0x48, name @+0x4c, ASCII if flag 0x20; base-block FileName @0x30 =
"renamed" DECOY; race MISS on fmt word, live ~17 s). Timed D15-17 + D19: synthesis dispatch missing -> generalize;
D18, D20-22, D24-25 first try.

**Day 26 — Before You Go** (`prefetch.executable_name`, kind `exact_text`, norm `trim`, id
`d26-prefetch-001-prefetch-executable-name`; syntax "use the literal none only when the requested field is absent").
Prompt: "Prefetch evidence records what Windows prepared to execute even after filenames changed. Recover executable
identities and connect execution traces to the correct hosts."
- Artifact: `metadata-day-26-evidence.zip` (3943 B) -> `trace-001.pf` (3896 B, `file`: "data"). Bytes @0 =
  `4d 41 4d 04` (`MAM\x04` = Win10+ Xpress-Huffman wrapper), uncompressed size u32 @4, compressed stream @8 ->
  SCCA v30 (`1e 00 00 00 53 43 43 41`). Host linking (volume serial/path) unasked in every mode.
- Insight: "even after filenames changed" = the member is `trace-001.pf`, not `NAME-<HASH>.pf`; the identity lives
  in the SCCA HEADER: exe name UTF-16LE @16 (60 B, cut at the first NUL), stored UPPERCASE with extension (`CMD.EXE`).
  Decompress first or the header is gibberish (`file` says "data"; `strings -el` finds nothing).
- Tools: `xxd -l 16` (spot `MAM`), `.venv/bin/python -I -c "from dissect.util.compression import lzxpress_huffman as L;
  d=L.decompress(b[8:]); print(d[16:76].decode('utf-16le'))"` (dissect.util IS installed), `lib.meta.answer(id, q, data)`
  -> prebuilt `prefetch.py` (pure-Python MS-XCA decoder) -- both agreed.
- Time: GM CORRECT ~29 s after start, 0 wrong (prebuilt hit; worker cross-checked then `--from-solver`). TT 31 fields
  4.7 s, Mastery 310 = TEN sets 8.0 s, first submit, no generalize; timed .pf were all UNCOMPRESSED SCCA v30.

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes/counts: base-10 integer, no units. Hashes: hex, any
  case. Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`). Booleans: enum `true` / `false`.
- Pixel dimensions (JPEG SOF, PNG IHDR, video D18): `<width>x<height>`, lowercase `x`; video = ffprobe v:0 coded size.
- PDF header version: bare `x.y` (absent -> `none`, unconfirmed). `_bytes` sizes = decoded integer (`1` -> `65536`, D23).
  `evtx.record_count` = records actually present (chunk walk, D24).
- Stored strings VERBATIM (no quotes, case kept, delimiters kept): PE StringFileInfo (D11), LNK LinkInfo path (D14),
  OOXML Target URL (D15), Message-ID WITH `<>` (D16), manifest `package` (D21), `Main-Class` (D22), registry ROOT nk
  name (D25: no leading `\`, no `HKEY_*`, not the base-block FileName), Prefetch SCCA header exe name (D26: UTF-16LE
  @16 to the first NUL, uppercase as stored, `.EXE` kept, no path, not the `.pf` filename stem / `-HASH`).
- JSON lists -- compact, double quotes, no spaces, values SORTED ascending: `zip.central_directory_member_names`
  (D23 CD order REJECTED), `ooxml.external_relationship_targets` (D15 rels order REJECTED), `macho.cpu_type_set`
  (`"0x%08x"`, deduped). The one ORDER field: `*-synthesis-<algo>-order` = names by hex digest ascending.
- Header integers as hex (`*_hex`): `0x` + lowercase hex ZERO-PADDED to the struct field's width (u16 `0x014c`
  `0x003e`, u32 `0x00065bd0`, Mach-O `0x0100000c` even without `_hex`). Width from the STRUCT / `_uNN_`; value in the
  file's own byte order. (Magic-prefix hex has NO `0x`; the binary lane wants `i386` -- different generator.)
- GUIDs follow the source: .NET MVID lowercase no braces (D12); MSI ProductCode stored string uppercase WITH braces (D13).
- Media codec names: ffprobe `codec_name` (WAV tag 1 -> `pcm_u8`/`pcm_s16le`/`pcm_s24le`/`pcm_s32le` by bits, 3
  `pcm_f32le`, 6 `pcm_alaw`, 7 `pcm_mulaw`, 0x55 `mp3`; MP3 `mp3`; Ogg `opus`/`vorbis` -- all GM-accepted).
- Rejected: `0x65bd0` (D10 unpadded); brace-less MSI GUID (D13); rels-order targets (D15); bracket-less Message-ID
  (D16); `["arm64"]` (D20); CD-order names (D23); Python repr `['a', 'b']` for any json (D23).
- Inference: the field id IS the spec name (`sof_`, `eocd_total_entries` = the EOCD's own claim, `e_machine`,
  `page_size`, libscca `executable_name`) -- read it literally to pick the structure; header CODES are raw `0x` hex.

## Delivery layouts seen (resolve these before parsing)
- Single / TT: one zip; members named in `artifact` after `->` (filename questions: artifact = the zip only). Mastery:
  ONE download holding `-01.zip`..`-NN.zip` (D7 three levels deep); refs `<set zip> -> <member>`, names reused per set
  -> resolve by (set zip, member). D9: download `<id>-mastery.zip` vs refs `...-evidence-0N.zip` -> resolve by sha256
  (`lib.common.container_by_sha`). D6: two same-named downloads -> `delivery N: <zip>` refs.

## Pitfalls that cost time
- **Carry-over mutation (D23, 1 wrong TT submit + a Mastery generalize)**: an extractor that only ever saw one sample
  value is untested. Before a timed run, ask of every carried field "what if this is the multi-element / other-endian
  / other-codec / compressed-or-not case?" -- fat Mach-O, shuffled CD, Ogg audio, non-x86 machines arrived the same day.
- **json list output**: sort + compact `json.dumps` at ONE choke point (D23 Mastery: a local Python list got `str()`'d).
- **Synthesis dispatch** (lost D15-17, D19): start the day's solver from the lane seed (`local_answer` +
  `synthesis_answer` -> `lib.meta.synthesis.digest_order`, artifacts root set INSIDE `_solve_pairs`; one process/set).
- **Registry misses** (D14 suffix, D16 `eml`/`email`, D17 `wav`/`media`, D21 no `apk`, D25 `regf.root_key_name` vs
  `registry.hive_root_name`): grep the lib for the field's last words under EVERY fmt --
  `python3 -c "import lib.meta as m; print([k for k in m.known_fields() if k[0]=='<fmt>'])"` + grep
  `lib/meta/prebuilt/*.py`. Shape trap (D20): `cpu_type_set` hit scalar `cpu_type` -- `_set`/`_list`/`_names` = a list.
- Unwired template (D22) / id slugs (D16, 1 wrong): `--from-solver` before today's field is dispatched emits `none`;
  ids repeat the fmt word (`d16-email-001-email-message-id`) -> anchor `-\d+-<fmt>-(.+)$`. `none` = absent in the
  bytes, never "my parser returned None".
- Format traps: byte order from the file (ELF EI_DATA @5, Mach-O magic; fat headers + SQLite ALWAYS BE); fat cputype
  lives in fat_arch AND the slice (set field = fat_arch); video geometry has 4 sources (trust SPS-cropped); EVTX count
  = WALK records per chunk to its free offset (header next id is a claim; chunks may be empty); regf cell offsets are
  relative to 0x1000 and start with an i32 size (FileName @0x30 != root name); SQLite `1` = 65536, WAL keeps the
  page size, truncated copies keep a valid header; Prefetch: test `MAM` @0 BEFORE `SCCA` @4 (compressed .pf has no
  readable strings; the wrapper came and went between modes on D26 -- branch on magic, not mode; version 17/23/26/30/31
  moves run count / last-run slots, name @16 and hash @0x4C are fixed).
- A pre-fetched TT/Mastery `contract.json` is the 409 `start_required` body (questions, NO `answer_ids`; Files lists
  and member numbering differ from the live attempt); answer under the live ids. The flavor never widens the field.
- Container-of-containers: a naive `rfind(PK\x05\x06)` reads the OUTER EOCD -- resolve the named member first.
  Decoys (`*-with-bom.txt`, `.exe` that is text, `.bin` that is PDF): bytes win; require the format's magic (else `none`).
- Timed windows are seconds, mostly GM round-trips (D23 Mastery start 3.2 + download 2.2 + solve 1.3 + submit 2.4 s;
  D26 Mastery download 6.8 MB / 9 s). Parse in memory, never shell out in-window; decompress each member once.
- Tools: exiftool, poppler, qpdf, mutool, pdf-parser, pdfid, pngcheck, zsteg, steghide, binwalk, foremost, mediainfo,
  sqlite3, ImageMagick, readelf/objdump, aapt + apktool/jadx (`source bin/env.sh`); .venv: olevba/oleid, olefile,
  pefile, pyelftools, LnkParse3, dnfile, mutagen, androguard, python-evtx, regipy, dissect.util (lzxpress_huffman,
  lznt1, lz4, lzo) -- all worker-only, not in the prebuild gate; msitools under tools/msitools; ffmpeg 7.0.2 at
  `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2` (not on PATH). NOT: ffprobe, sox.
