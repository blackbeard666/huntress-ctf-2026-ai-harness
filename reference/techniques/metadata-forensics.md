# metadata-forensics — technique log (days 1-25; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
  **D23 mutated the WHOLE carry-over kit** (values that sat constant D13-D22 re-rolled: PE/ELF arch, audio codec, video
  dims, Mach-O became FAT, zip CD order shuffled) -- every carried extractor must parse the general case, not D-day's sample.
- Every day = ONE evidence zip (plain Deflate, no password). D1-7: one tiny member, one fact; D8-9: cumulative kit in
  every mode; D10-14: one field everywhere. **D15+ split the modes**: single = 1 field (the new member), TT = cumulative
  kit (D15 20 -> D25 30 fields, +1/day), Mastery = N kits x the TT set (N=5 to D21, 6 D22, 7 D23, 8 D24, 9 D25), incl. a
  cross-member "synthesis" question. Pre-arm EVERY earlier family AND the synthesis before the timed run.
- Member families: note/text -> jpg -> png -> pdf -> inner zip -> Go PE (D9-11) -> .NET dll (D12) -> MSI (D13) -> LNK
  (D14) -> OOXML `.docx` (D15) -> `.eml` (D16) -> WAV (D17) -> MP4 (D18) -> ELF (D19) -> Mach-O `macos-001.bin` (D20)
  -> APK `mobile-001.apk` (D21) -> JAR `application-001.jar` (D22) -> SQLite `database-001.sqlite` (D23) -> EVTX
  `events-001.evtx` (D24) -> registry hive `hive-001.hiv` (D25). D19-22 = runnable formats; D23 APPLICATION DATA (db
  header); D24-25 = the WINDOWS DFIR block (D24 first STRUCTURE WALK; D25 first POINTER FOLLOW: header offset -> cell).
  fmt word = an ABSTRACT namespace sometimes (`email` not `eml`; `media` for audio D17 AND video D18, ffprobe
  vocabulary), else the plain format (`pe` `msi` `lnk` `elf` `macho` `apk` `jar` `sqlite` `evtx`) -- read it from the question.
- Fields, one new per day (full list in "Day by day"; D25 = `registry.hive_root_name`).
  Question `Determine <fmt>.<field> for <member>`; id `dNN-<family>-NNN-<fmt>-<field>` (`.`/`_` -> `-`), `dNN` = the
  family's first day; `<family>` != `<fmt>` only for media (`d17-audio-001-media-`, `d18-video-...`). D25 fmt word
  `registry` (NOT the magic/lib name `regf`) -- the GM names the DOMAIN, the library may name the file format.
- Flavor text promises extra findings that are NEVER asked (collisions, crops, D19 deployment groups, D20 fleet, D21
  clones, D22 nested launchers, D23 "truncated, embedded ... impossible claim", D24 "duplicated ... selectively
  shortened timeline", D25 "renamed and separated from host labels ... regroup the systems, and isolate the planted
  hive"); the single sample delivers less. Graded = the
  STRUCTURAL truth; names/extensions/secondary metadata are the lie. Titles pun on the field (D19 "Little Endian" =
  EI_DATA; D20 "Universal Appeal" = fat; D21 "Package Deal"; D22 "Main Character Energy" = `Main-Class`; D23 "Page Me
  Maybe" = page size; D24 "Event Horizon" = how far the records reach = record count; D25 "Hive Mind" = the hive's
  root key name). Flavor's "true root" = the field; "renamed" = the base-block name decoy. The flavor's depth shows up in
  the TIMED carry-over mutations (D23 fat Mach-O, D24 M4A/FLAC audio), not in new fields.
- Singles: D1-9 first-submit ~27-60 s; D10, D13, D15 lost ONE submit to a convention (padding, braces, list order);
  D16 lost TWO (`none`, stripped `<>`); D20 lost ONE (`["arm64"]` -> hex won). Race probe from the prebuilt `lib.meta`
  registry: D18 ~5 s, D19 ~13 s, D22 ~19 s, D23 ~29 s (`lib/meta/prebuilt/sqlite.py`); registry MISS -> live worker D17
  ~24 s, D21 ~32 s; D24 live worker ~21 s (own struct chunk walk); D25 live worker ~17 s (race MISS: `regf.py` had
  `regf.root_key_name`, GM asked `registry.hive_root_name`).
  TT/Mastery: CORRECT every day; D15-17 + D19 after an offline generalize (synthesis dispatch missing); D23 after one
  wrong TT submit + generalize (list ORDER under mutation); D18, D20-22, D24 in-window first try
  (D24: TT 29 fields 8.4 s, Mastery 232 5.6 s; D25: TT 30 fields 2.1 s, Mastery 270 = 9 sets 2.7 s; zero generalize).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen". Names drift: D1-14 `metadata-day-NN-evidence[-0N].zip`; D15-25 TT
  `evidence.zip`, Mastery `evidence-01.zip` holding `evidence-01..0N.zip` (N=5; D22 6; D23 7; D24 8; D25 9). Route by
  the ref's text before `->` and by sha256, never a hard-coded name.
- **Field-set / set count** -- D7 TT 11 / Mastery 22; D8-9 12-13 everywhere; D10-14 one; D15 1/20/100 ... D21 1/26/130
  (+1 field/day); D22 1/27/162 (6 sets); D23 1/28/196 (7 sets); D24 1/29/232 (8 sets); D25 1/30/270 (9 sets).
  Enumerate `setN.` prefixes from the live ids. Families: identity + `d04-jpeg` `d05-png` `d06-pdf` `d07-zip` (eocd,
  CD names) `d09-pe` (machine, entry RVA, OriginalFilename) `d12-dotnet` `d13-msi` `d14-lnk` `d15-ooxml` `d16-email` `d17-audio` `d18-video` `d19-elf`
  `d20-macho` `d21-apk` `d22-jar` `d23-sqlite` `d24-evtx` `d25-registry` + synthesis. Dispatch on the answer-id SUFFIX
  (reference solver answering all 30: `challenges/day25/metadata-hive-mind/solver/solve.py`; lane seed `local_answer` +
  `synthesis_answer` + lib.meta).
- **fmt word vs registry key vs id family** -- D16 `email.*` (prebuilt said `eml`); D17/D18 `media.*` ids
  `d17-audio-`/`d18-video-`; D19 `elf.e_machine_u16_hex` (spec name keeps its underscore -> `e-machine`); D20
  `macho.cpu_type_set`; D21 `apk.package_name`; D22 `jar.main_class` (container word, attribute snake_cased); D23
  `sqlite.page_size_bytes` (plain format word; unit suffix `_bytes` on an integer); D24 `evtx.record_count` (plain);
  D25 `registry.hive_root_name` (DOMAIN word, lib/magic say `regf`; field prefixed `hive_`, lib had `root_key_name`).
  Vocabulary = the field's home tool (ffprobe) or the spec struct/attribute; binary-header codes ALWAYS raw `0x` hex,
  even without `_hex` (D20). Rule: take `<fmt>.<field>` from the question (or the slug after `-NNN-`), map fmt synonyms
  (`email`<->`eml`/`mime`; `media`<->`audio`/`video`/`av`; `jar`<->`java_archive`/`war`; `sqlite`<->`sqlite3`/`db`;
  `evtx`<->`evt`/`eventlog`; `registry`<->`regf`/`hive`/`reg`), and field synonyms (`hive_root_name` = `root_key_name`
  = root nk name), route the extractor by MAGIC + member names, fall back to the same field under any fmt.
- **Member values (D23-25: EVERYTHING re-rolls, new values every day)** -- never cache across sets/modes. Seen
  re-rolling: identity member sizes (D15-22 33/29 B; D23 72-378 B, CRLF or LF rosters, BOM `true` in some sets), jpg/png
  dims, PDF header `1.0`-`2.0`, D7 entry count 2-13, PE Machine (`0x014c` `0x8664` `0xaa64` earlier; D23
  also `0x01c0` ARM, `0x01c2` Thumb, `0x01c4` ARMNT, `0x01f0` PowerPC, `0x0ebc` EFI byte code, `0x5064` RISCV64; D24 +
  `0x0266` MIPS16), entry RVA, MVID, ProductCode, LNK target (C:/D:, varied dirs), docx targets (1-5), Message-ID, audio
  codec (`pcm_s16le` -> D23 also `mp3`, `opus`, `vorbis`; D24 + `aac` from `ftyp M4A ` and `flac` from `fLaC`, all still
  named `audio-001.wav`), video dims (no longer 320x180), ELF e_machine (`0x003e` -> D23 `0x0003`, `0x0028`, `0x002b`
  SPARCV9, `0x0102` LoongArch; D24 + `0x0016` S390, `0x00b7` AArch64, `0x00f3` RISC-V), Mach-O thin -> D23 FAT with 2-3
  slices of {`0x00000007` `0x0000000c` `0x00000012` `0x01000007` `0x0100000c` `0x01000012` `0x0200000c`} (D24 also a
  60-B THIN LE-32 `ce fa ed fe` ARM -> `["0x0000000c"]`), APK package (`io.*`/`net.*`/`org.*`/`com.*`), JAR Main-Class
  (dotted, 1-4 parts), SQLite page size 512-65536 (65536 stored as `1`; D24 + 2048), EVTX record count 3-119 (one
  64 KiB chunk so far), registry root name (single CamelCase; timed random `[A-Za-z0-9]{6,32}`, ASCII compressed name,
  root cell @0x20 in all 11 D25 hives -- follow the pointer anyway). Rule: decode the general structure (byte order
  from the file, walk every slice/chunk/stream, follow every offset, map every tag), never the D-day sample's constant.
- **List ORDER under mutation (D23)** -- D8-D22 zips stored CD entries already sorted, so "CD order" and "sorted"
  coincided; D23 shuffled the CD and the GM REJECTED CD order, accepted ascending sort. Fat Mach-O slices: ascending
  `0x%08x` accepted (fat_arch order != the accepted answer). Rule: every `json` list answer = values sorted ascending
  (string sort of the emitted spelling; dedupe sets), EXCEPT synthesis (= order by digest) and anything whose question
  states an order. Always `json.dumps(sorted(v), separators=(",",":"))` -- a Python list `str()`'d to repr is wrong.
- **Identity member roster** (D15+) -- THREE small text members (`evidence-note*.txt`, `evidence-note-copy*.txt`,
  `roster*.csv`; D24-25 timed names carry a random `-<6hex>` suffix, e.g. `roster-236466.csv`, ids keep the bare stem);
  ids `<member-stem>-{filename,size-bytes,md5,sha1,sha256,magic-prefix-hex-16,text-utf8-bom-present}`. Filename
  question artifact = the container only -> map the stem by PREFIX. D25 Mastery: 2 of 9 sets had no roster member
  (a different kit: macos/docx/inner-zip) -> answer only the ids each set's contract lists.
- **Synthesis / cross-member** (D15+) -- id `metadata-day-NN-synthesis-<algo>-order` (TODAY's NN), kind `json`, norm
  `case_insensitive`, text "Compute the full-file SHA-256 digest of each named file, then submit a compact JSON array of
  their filenames in ascending digest order. Files: [...]". Rule: regex `Files:\s*(\[.*?\])`, resolve each under the
  ref's container, `hashlib.new(algo)` over raw bytes, sort by hex digest, emit names --
  `lib.meta.synthesis.digest_order(question, get_bytes, algo)` with get_bytes bound INSIDE the per-set worker. Shape:
  note + re-picked kit members + TODAY's member; 4 names D15-20, FIVE D21-25 (D24: note/pdf/elf/lnk/evtx; D25
  note/pdf/elf/lnk/hiv, some sets note/macos/docx/zip/hiv). The list
  differs between the 409 contract and the live attempt AND between sets of one Mastery (D23: note/png/msi/mp4/sqlite vs
  note/pdf/lnk/mp4/sqlite) -- parse each set's own text. Only sha256 seen.
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

**Days 15-24** (single = 1 new-family field; TT/Mastery = cumulative kit + synthesis): D15 `ooxml.external_relationship_
targets` (rels `TargetMode="External"` Targets SORTED; rels order REJECTED). D16 `email.message_id` (VERBATIM with `<>`;
2 lost: id regex -> `none`, stripped brackets). D17 `media.primary_audio_codec_name` (WAV PCM16 -> `pcm_s16le`). D18
`media.primary_video_dimensions` (first `vide` trak stsd -> `320x180`). D19 "Little Endian" `elf.e_machine_u16_hex`
(@18 in EI_DATA order -> `0x003e`). D20 "Universal Appeal" `macho.cpu_type_set` (THIN arm64 -> `["0x0100000c"]`;
`["arm64"]` REJECTED). D21 "Package Deal" `apk.package_name` (binary-AXML `<manifest package=>` verbatim, NOT
`android:label`). D22 "Main Character Energy" `jar.main_class` (MANIFEST.MF `Main-Class` verbatim, dotted, no
`.class`; an unwired-template `none` submit landed after CORRECT -- harmless that time). D23 "Page Me Maybe"
`sqlite.page_size_bytes` (u16 BE @16, `1` = 65536; prebuilt race hit ~29 s; timed kit MUTATED for the first time ->
1 wrong TT submit on CD-order names, Mastery generalize for sorted compact JSON). D24 "Event Horizon"
`evtx.record_count` (integer; `events-001.evtx` = 4 KiB header + one 64 KiB chunk; count = walk `**\0\0` records of
EVERY chunk up to its free-space offset u32 @48 -- not the chunk count, not the header's next id; header
`next_record_id-1` agreed in all 9 files; live struct walk ~21 s; TT/Mastery first try). Timed D15-17 + D19:
synthesis dispatch missing -> `solver_incomplete` -> offline generalize; D18, D20-22, D24 first try.

**Day 25 — Hive Mind** (`registry.hive_root_name`, kind `exact_text`, norm `trim`, id
`d25-registry-001-registry-hive-root-name`; syntax "use the literal none only when the requested field is absent").
Prompt: "Registry hives from multiple systems have been renamed and separated from host labels. Identify each true
root, regroup the systems, and isolate the planted hive."
- Artifact: `metadata-day-25-evidence.zip` (657 B) -> `hive-001.hiv` (8192 B = 4 KiB base block + ONE 4 KiB `hbin`;
  `file`: "MS Windows registry file, NT/2000 or above"). seq1 == seq2, v1.3, file type 0, root cell 0x20, root nk
  flags 0x2c (HIVE_ENTRY|NO_DELETE|COMP_NAME), 0 subkeys, 2 values. Regrouping / planted hive: unasked in every mode.
- Insight: "true root" = the ROOT KEY's name -- follow base block u32 @0x24 -> cell at 0x1000+off -> `nk` -> name
  (len u16 @nk+0x48, bytes @nk+0x4c; ASCII when flag 0x20). The base-block FileName (UTF-16 @0x30, 64 B) is the
  "renamed" DECOY: single = truncated kebab path `ress-artifact-assembly-line.hiv` vs root `HuntressArtifactAssemblyLine`;
  timed = unrelated `<word>-<8hex>.hiv` vs a random alnum root. Verbatim, case kept, no path/backslash.
- Tools: `xxd -l 128 f` (base block), `xxd -s 0x1000 -l 160 f` (hbin + root nk -- the name is readable in the dump);
  ~15-line struct parser for solve.py; regipy `RegistryHive(path).root.name` = cross-check (worker-only).
- Time: live worker GM CORRECT ~17 s after start, 0 wrong (race MISS: lib `regf.root_key_name`, no `registry` fmt /
  `hive_root_name` spelling). TT 30 fields 2.1 s, Mastery 270 fields = NINE sets 2.7 s, both first submit, no generalize.

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes: base-10 integer, no units. Hashes: hex, case ignored.
- Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`). Booleans: enum `true` / `false`.
- Pixel dimensions (JPEG SOF, PNG IHDR, video D18): `<width>x<height>`, lowercase `x`, no spaces. Video = ffprobe
  width/height of v:0 (coded size, NOT rotated, not the tkhd display size).
- PDF header version: bare `x.y`; absent -> literal `none` (wording; `none` not yet GM-confirmed). Counts: plain integer.
  Struct sizes with a `_bytes` suffix (D23 page size): the decoded integer in bytes (`1` on disk -> `65536`).
  Record counts (`evtx.record_count`, D24): number of records actually present (chunk walk), base-10.
- Registry key names (`registry.hive_root_name`, D25): the root `nk` cell's stored name VERBATIM (case kept, no
  leading `\`, no `HKEY_*`/`ROOT` prefix, not the base-block FileName). GM-confirmed in all 3 modes.
- JSON lists -- compact, double quotes, no spaces, values SORTED ascending:
  - `zip.central_directory_member_names`: full stored paths, sorted (D23 TT: CD order REJECTED; D8-22 disk order was sorted).
  - `ooxml.external_relationship_targets`: Target strings sorted (D15; rels-file order REJECTED).
  - `macho.cpu_type_set`: `"0x%08x"` per slice, deduped, sorted (D20 thin = one element; D23 fat 2-3 slices).
  - `*-synthesis-<algo>-order`: member names ordered by hex digest ascending (the one ORDER field; `case_insensitive`).
- Header integers as hex (`*_hex`): `0x` + lowercase hex ZERO-PADDED to the struct field's width: u16 PE Machine
  `0x014c`/`0x5064`, u16 ELF e_machine `0x003e`/`0x0102`, u32 AddressOfEntryPoint `0x00065bd0`, u32 Mach-O cputype
  `0x0100000c` (inside a JSON list, even without `_hex`). Width from the STRUCT / the `_uNN_` in the id; the value from
  the file's own byte order. (Magic-prefix hex has NO `0x`; the binary lane wants `i386` -- different generator.)
- GUIDs: .NET MVID `Guid.ToString()` lowercase no braces (D12); MSI ProductCode the stored string uppercase WITH braces
  (D13). Spelling follows the source, not answer_format.
- Stored strings VERBATIM (no quotes, case kept, delimiters kept): LNK LinkInfo path (D14), PE StringFileInfo value
  (D11), OOXML Target URL (D15), Message-ID WITH `<>` (D16), Android manifest `package` (D21), JAR `Main-Class` (D22),
  registry root key name (D25).
- Media codec names (`media.*codec_name`): ffprobe `codec_name`: WAV tag 1 -> `pcm_u8`/`pcm_s16le`/`pcm_s24le`/
  `pcm_s32le` by bits, 3 `pcm_f32le`, 6 `pcm_alaw`, 7 `pcm_mulaw`, 0x55 `mp3`; MP3 `mp3`; Ogg `opus` / `vorbis` (all
  four GM-accepted D23 timed).
- Rejected spellings: `0x65bd0` (D10, unpadded); brace-less MSI GUID (D13); rels-file-order targets (D15); bracket-less
  Message-ID (D16); `["arm64"]` (D20); CD-order member names (D23); Python repr `['a', 'b']` for any json (D23).
- Inference: the field id IS the spec name (`sof_`, `eocd_total_entries` = the EOCD's own claim, `e_machine`,
  `page_size`) -- read it literally to pick the structure. A claimed count is NOT a CD walk; CD names are NOT
  local-header names; `_uNN_hex` fixes read+print width. Header CODES are raw `0x` hex, never tool names.

## Delivery layouts seen (resolve these before parsing)
- Single / TT: one zip; members named in `artifact` after `->` (filename questions: artifact = the zip only). Mastery
  (most days, all of D15-25): ONE download holding `-01.zip`..`-0N.zip` (D7 three levels; D15-21 five kits, D22 six, D23
  seven, D24 eight, D25 nine); refs `<set zip> -> <member>`, names reused per set -> resolve by (set zip, member). D9: download
  `<id>-mastery.zip` vs refs `...-evidence-0N.zip` -> resolve by sha256 (`lib.common.container_by_sha`). D6: two
  same-named downloads -> `delivery N: <zip>` refs. Member numbering shifts between pre-fetched contract and live attempt.

## Pitfalls that cost time
- **Carry-over mutation (D23, 1 wrong TT submit + a Mastery generalize)**: an extractor that only ever saw one sample
  value is untested. Before a timed run, ask of every carried field "what if this is the multi-element / other-endian
  / other-codec case?" -- fat Mach-O, shuffled CD, Ogg audio, non-x86 PE/ELF machines all arrived the same day.
- **json list output**: sort + compact `json.dumps` at ONE choke point (D23 Mastery: a local Python list got `str()`'d).
- **Synthesis dispatch** (lost D15, D16, D17, D19): the timed kit always adds `metadata-day-NN-synthesis-sha256-order`.
  Start the day's solver from the previous day's solve.py (lane seed `local_answer` + `synthesis_answer` ->
  `lib.meta.synthesis.digest_order`, artifacts root set INSIDE `_solve_pairs`; Mastery forks one process per set).
- Registry misses: D14 key one suffix short; D16 fmt `eml` vs GM `email`; D17 `wav.*` vs `media.*`; D21 no `apk` fmt
  (a new CONTAINER family needs its own fmt word); D25 `regf.root_key_name` existed but GM said `registry.hive_root_name`
  (domain fmt word + `hive_` prefix) -- grep the lib for the field's last words (`root`+`name`) under every fmt. D22
  `jar` / D23 `sqlite` prebuilt -> race hits. Check
  `python3 -c "import lib.meta as m; print([k for k in m.known_fields() if k[0]=='<fmt>'])"`, grep
  `lib/meta/prebuilt/*.py` for the FIELD. D20 substring trap: `cpu_type_set` hit scalar `cpu_type` -> check the SHAPE
  vs answer_format (`_set`/`_list`/`_names` = a list).
- Unwired day template (D22): `hctf submit --from-solver` before today's field is dispatched emits literal `none`.
  Only submit from the solver once `solve.py` prints a real value for EVERY id.
- Id-slug parsing (D16, 1 wrong): ids repeat the fmt word (`d16-email-001-email-message-id`); anchor `-\d+-<fmt>-(.+)$`.
  Never submit `none` without grepping the bytes -- `none` = absent in the artifact, not "my parser returned None".
- Byte order: ELF EI_DATA @5 / the Mach-O magic decide (fat headers ALWAYS BE, slices carry their own magic); SQLite
  header is ALWAYS big-endian. Fat cputype is in BOTH fat_arch and the slice header -- may disagree in a variant: the
  set field reads fat_arch. Video geometry has FOUR sources (stsd, SPS crop = ffprobe, tkhd, matrix); trust SPS-cropped.
- EVTX (D24): count by WALKING records in every chunk (a chunk's free-space offset ends it; slack after it is not a
  record); header next_record_id is a claim that a dirty/truncated/shortened log can break; a log may hold several
  chunks and a non-first chunk may be empty or zeroed. EventRecordID gaps = the "shortened timeline" sibling.
- Registry hives (D25): two "names" live in the file -- base-block FileName @0x30 (renamed/truncated, last 31 UTF-16
  chars of the original path) and the root nk name. `root`/`key` fields = the nk; `file_name` fields = @0x30. Offsets
  in cells are relative to 0x1000 (first hbin); every cell starts with an i32 size, so `nk` sits at 0x1000+off+4.
- SQLite: page size `1` = 65536 (u16 overflow); WAL (`@18/@19 == 2`) does not change the page size; a truncated or
  embedded copy keeps a valid header -- read the header of the NAMED member, don't infer from file length.
- A pre-fetched TT/Mastery `contract.json` is the 409 `start_required` body (questions, NO `answer_ids`); answer under
  the live ids. Only the named field is graded -- the flavor never widens it.
- Container-of-containers: a naive `rfind(PK\x05\x06)` reads the OUTER EOCD. Resolve the named member's bytes first
  (recurse), then parse. Hostile CD names (`../`, dupes) as-is.
- Decoys: `*-with-bom.txt`, `.exe` that is text, `.bin` that is PDF, friendly APK filenames: bytes win. Require the
  format's magic before any field of that format (else `none`; a jar WITHOUT `Main-Class` is `none`).
- Timed windows are seconds, mostly GM round-trips (D23 Mastery start 3.2 + download 2.2 + solve 1.3 + submit 2.4 s
  for 196 fields). Parse in memory, never shell out in-window; decompress each member once, cache by (set zip, member).
- Tools installed: exiftool, poppler, qpdf, mutool, pdf-parser, pdfid, pngcheck, zsteg, steghide, binwalk, foremost,
  mediainfo, sqlite3 (CLI + python; `sqlite3` module is worker-only, not in the prebuild gate), ImageMagick,
  readelf/objdump, aapt + apktool/jadx (`source bin/env.sh`), olevba/oleid, olefile, pefile, pyelftools, LnkParse3,
  dnfile, mutagen, androguard, python-evtx `Evtx` + `evtx_dump.py`, regipy (.venv); msitools under tools/msitools; ffmpeg
  7.0.2 at `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2` (not on PATH). NOT: ffprobe, sox.
