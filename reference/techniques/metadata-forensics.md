# metadata-forensics — technique log (days 1-23; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
  **D23 mutated the WHOLE carry-over kit** (values that sat constant D13-D22 re-rolled: PE/ELF arch, audio codec, video
  dims, Mach-O became FAT, zip CD order shuffled) -- every carried extractor must parse the general case, not D-day's sample.
- Every day = ONE evidence zip (plain Deflate, no password). D1-7: one tiny member, one fact; D8-9: cumulative kit in
  every mode; D10-14: one field everywhere. **D15+ split the modes**: single = 1 field (the new member), TT = cumulative
  kit (D15 20 -> D23 28 fields, +1/day), Mastery = N kits x the TT set (N=5 to D21, 6 D22, SEVEN D23), incl. a
  cross-member "synthesis" question. Pre-arm EVERY earlier family AND the synthesis before the timed run.
- Member families: note/text -> jpg -> png -> pdf -> inner zip -> Go PE (D9-11) -> .NET dll (D12) -> MSI (D13) -> LNK
  (D14) -> OOXML `.docx` (D15) -> `.eml` (D16) -> WAV (D17) -> MP4 (D18) -> ELF (D19) -> Mach-O `macos-001.bin` (D20)
  -> APK `mobile-001.apk` (D21) -> JAR `application-001.jar` (D22) -> SQLite `database-001.sqlite` (D23). D19-22 =
  runnable formats (one header/identity/launch field each); D23 turned to APPLICATION DATA (a database header field).
  fmt word = an ABSTRACT namespace sometimes (`email` not `eml`; `media` for audio D17 AND video D18, ffprobe
  vocabulary), else the plain format (`pe` `msi` `lnk` `elf` `macho` `apk` `jar` `sqlite`) -- read it from the question.
- Fields, one new per day: identity -> magic prefix -> `text.utf8_bom_present` -> `jpeg.sof_dimensions_pixels` ->
  `png.ihdr_dimensions_pixels` -> `pdf.header_version` -> `zip.eocd_total_entries` -> `zip.central_directory_member_names`
  -> `pe.coff_machine_u16_hex` -> `pe.address_of_entry_point_rva_hex` -> `pe.version_original_filename` ->
  `dotnet.mvid_guid` -> `msi.product_code_guid` -> `lnk.target_path_windows` -> `ooxml.external_relationship_targets` ->
  `email.message_id` -> `media.primary_audio_codec_name` -> `media.primary_video_dimensions` -> `elf.e_machine_u16_hex`
  -> `macho.cpu_type_set` -> `apk.package_name` -> `jar.main_class` -> `sqlite.page_size_bytes`.
  Question `Determine <fmt>.<field> for <member>`; id `dNN-<family>-NNN-<fmt>-<field>` (`.`/`_` -> `-`), `dNN` = the
  family's first day; `<family>` != `<fmt>` only for media (`d17-audio-001-media-`, `d18-video-...`).
- Flavor text promises extra findings that are NEVER asked (collisions, crops/claimed device, D19 deployment groups,
  D20 fleet, D21 rebuilds vs clones, D22 nested launchers, D23 "copied, truncated, embedded, and mislabeled ... connect
  databases to parent applications, and find the impossible claim"); the single sample delivers less. Graded = the
  STRUCTURAL truth; names/extensions/secondary metadata are the lie. Titles pun on the field (D19 "Little Endian" =
  EI_DATA; D20 "Universal Appeal" = fat; D21 "Package Deal"; D22 "Main Character Energy" = `Main-Class`; D23 "Page Me
  Maybe" = page size). The flavor's depth shows up in the TIMED carry-over mutations (D23 fat Mach-O), not new fields.
- Singles: D1-9 first-submit ~27-60 s; D10, D13, D15 lost ONE submit to a convention (padding, braces, list order);
  D16 lost TWO (`none`, stripped `<>`); D20 lost ONE (`["arm64"]` -> hex won). Race probe from the prebuilt `lib.meta`
  registry: D18 ~5 s, D19 ~13 s, D22 ~19 s, D23 ~29 s (`lib/meta/prebuilt/sqlite.py`); registry MISS -> live worker D17
  ~24 s, D21 ~32 s. TT/Mastery: CORRECT every day; D15-17 + D19 after an offline generalize (synthesis dispatch
  missing); D23 after one wrong TT submit + generalize (list ORDER under mutation); D18, D20-22 in-window first try.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen". Names drift: D1-14 `metadata-day-NN-evidence[-0N].zip`; D15-23
  TT `evidence.zip`, Mastery `evidence-01.zip` holding `evidence-01..0N.zip` (N=5; D22 6; D23 7). Route by the ref's
  text before `->` and by sha256, never a hard-coded name.
- **Field-set / set count** -- D7 TT 11 / Mastery 22; D8-9 12-13 everywhere; D10-14 one; D15 1/20/100 ... D21 1/26/130
  (+1 field/day); D22 1/27/162 (6 sets); D23 1/28/196 (7 sets). Enumerate `setN.` prefixes from the live ids. Families:
  identity + `d04-jpeg` `d05-png` `d06-pdf` `d07-zip` (eocd, CD names) `d09-pe` (machine, entry RVA, OriginalFilename)
  `d12-dotnet` `d13-msi` `d14-lnk` `d15-ooxml` `d16-email` `d17-audio` `d18-video` `d19-elf` `d20-macho` `d21-apk`
  `d22-jar` `d23-sqlite` + synthesis. Dispatch on the answer-id SUFFIX (reference solver answering all 28:
  `challenges/day23/metadata-page-me-maybe/solver/solve.py`; lane seed `local_answer` + `synthesis_answer` + lib.meta).
- **fmt word vs registry key vs id family** -- D16 `email.*` (prebuilt said `eml`); D17/D18 `media.*` ids
  `d17-audio-`/`d18-video-`; D19 `elf.e_machine_u16_hex` (spec name keeps its underscore -> `e-machine`); D20
  `macho.cpu_type_set`; D21 `apk.package_name`; D22 `jar.main_class` (container word, attribute snake_cased); D23
  `sqlite.page_size_bytes` (plain format word; unit suffix `_bytes` on an integer). Vocabulary = the field's home tool
  (ffprobe) or the spec struct/attribute; binary-header codes ALWAYS raw `0x` hex, even without `_hex` (D20). Rule: take
  `<fmt>.<field>` from the question (or the slug after `-NNN-`), map fmt synonyms (`email`<->`eml`/`mime`;
  `media`<->`audio`/`video`/`av`; `jar`<->`java_archive`/`war`; `sqlite`<->`sqlite3`/`db`), route the extractor by MAGIC
  + member names, fall back to the same field under any fmt.
- **Member values (D23: EVERYTHING re-rolls)** -- never cache across sets/modes. Seen re-rolling: identity member sizes
  (D15-22 33/29 B; D23 72-378 B, CRLF or LF rosters, BOM `true` in some sets), jpg/png dims, PDF header `1.0`/`1.4`/
  `1.5`/`2.0`, D7 entry count 2-13, PE Machine (`0x014c` `0x8664` `0xaa64` earlier; D23 also `0x01c0` ARM, `0x01c2`
  Thumb, `0x01c4` ARMNT, `0x01f0` PowerPC, `0x0ebc` EFI byte code, `0x5064` RISCV64), entry RVA, MVID, ProductCode,
  LNK target (C:/D:, varied dirs), docx targets (1-5), Message-ID, audio codec (`pcm_s16le` -> D23 also `mp3`, `opus`,
  `vorbis`), video dims (no longer 320x180), ELF e_machine (`0x003e` -> D23 `0x0003`, `0x0028`, `0x002b` SPARCV9,
  `0x0102` LoongArch), Mach-O thin -> D23 FAT with 2-3 slices of {`0x00000007` `0x0000000c` `0x00000012` `0x01000007`
  `0x0100000c` `0x01000012` `0x0200000c`}, APK package (`io.*`/`net.*`/`org.*`/`com.*`), JAR Main-Class (dotted,
  1-4 parts), SQLite page size 512-65536 (65536 stored as `1`). Rule: decode the general structure (byte order from the
  file, walk every slice/chunk/stream, map every tag), never the D-day sample's constant.
- **List ORDER under mutation (D23)** -- D8-D22 zips stored CD entries already sorted, so "CD order" and "sorted"
  coincided; D23 shuffled the CD and the GM REJECTED CD order, accepted ascending sort. Fat Mach-O slices: ascending
  `0x%08x` accepted (fat_arch order != the accepted answer). Rule: every `json` list answer = values sorted ascending
  (string sort of the emitted spelling; dedupe sets), EXCEPT synthesis (= order by digest) and anything whose question
  states an order. Always `json.dumps(sorted(v), separators=(",",":"))` -- a Python list `str()`'d to repr is wrong.
- **Identity member roster** (D15+) -- THREE small text members (`evidence-note.txt`, `evidence-note-copy.txt`,
  `roster.csv`); each identity question picks one per set: ids `<member-stem>-{filename,size-bytes,md5,sha1,sha256,
  magic-prefix-hex-16,text-utf8-bom-present}`. Filename question artifact = the container only -> map the stem.
- **Synthesis / cross-member** (D15+) -- id `metadata-day-NN-synthesis-<algo>-order` (TODAY's NN), kind `json`, norm
  `case_insensitive`, text "Compute the full-file SHA-256 digest of each named file, then submit a compact JSON array
  of their filenames in ascending digest order. Files: [...]". Rule: regex `Files:\s*(\[.*?\])`, resolve each under the
  ref's container, `hashlib.new(algo)` over raw bytes, sort by hex digest, emit names --
  `lib.meta.synthesis.digest_order(question, get_bytes, algo)` with get_bytes bound INSIDE the per-set worker. Shape:
  note + re-picked kit members + TODAY's member; 4 names D15-20, FIVE D21-23. The list differs between the 409 contract
  and the live attempt AND between sets of one Mastery (D23: note/png/msi/mp4/sqlite vs note/pdf/lnk/mp4/sqlite) --
  parse each set's own text. Only sha256 seen.
- **Decoys** -- renamed copies, misleading extensions, secondary metadata (EXIF, catalog /Version): answer from the
  structural bytes of the named member. Kits pool `collector-001.elf` with `MZ` members: `elf.*` of a non-ELF = `none`.
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

**Days 15-22** (single = 1 new-family field; TT/Mastery = cumulative kit + synthesis): D15 `ooxml.external_relationship_
targets` (rels `TargetMode="External"` Targets SORTED; rels order REJECTED). D16 `email.message_id` (VERBATIM with `<>`;
2 lost: id regex -> `none`, stripped brackets). D17 `media.primary_audio_codec_name` (WAV PCM16 -> `pcm_s16le`). D18
`media.primary_video_dimensions` (first `vide` trak stsd -> `320x180`). D19 "Little Endian" `elf.e_machine_u16_hex`
(@18 in EI_DATA order -> `0x003e`). D20 "Universal Appeal" `macho.cpu_type_set` (THIN arm64 -> `["0x0100000c"]`;
`["arm64"]` REJECTED). D21 "Package Deal" `apk.package_name` (binary-AXML `<manifest package=>` verbatim, NOT
`android:label`). D22 "Main Character Energy" `jar.main_class` (MANIFEST.MF `Main-Class` verbatim, dotted, no
`.class`; prebuilt `jar.py` race hit ~19 s; an unwired-template `none` submit landed after CORRECT -- harmless that
time). Timed D15-17 + D19: synthesis dispatch missing -> `solver_incomplete` -> offline generalize; D18, D20-22 first try.

**Day 23 — Page Me Maybe** (`sqlite.page_size_bytes`, kind `integer`, norm `trim`, id
`d23-sqlite-001-sqlite-page-size-bytes`). Prompt: "Application databases have been copied, truncated, embedded, and
mislabeled. Validate page geometry, connect databases to parent applications, and find the impossible claim."
- Artifact: `metadata-day-23-evidence.zip` (536 B) -> `database-001.sqlite` (12 288 B = 3 x 4096-B pages; `file`:
  "SQLite 3.x database, application id 1213485652 (`0x48545254` "HTRT"), user version 7, last written using SQLite
  version 3046000, file counter 9, database pages 3"). Header consistent (in-header size 3 x 4096 = file length,
  change counter == version-valid-for) -- the truncation / embedding / parent-app / "impossible claim" flavor was unasked.
- Insight: page size = u16 BIG-endian @16 of the 100-byte header (`10 00` -> 4096); the value `1` means 65536 (seen in a
  Mastery set). Answer the integer in bytes. Not `PRAGMA page_count`, not file size / pages.
- Tools: `xxd -s 16 -l 2 f`; `file f`; `sqlite3 f 'PRAGMA page_size'`; in-window `lib/meta/prebuilt/sqlite.py` (built
  D16-night `sqlite-header` gap) answered in the race probe -> GM CORRECT ~29 s, 0 wrong.
- Timed: TT 28 fields / Mastery 196 (SEVEN sets); sqlite values 512/1024/4096/8192/16384/32768/65536 all read right.
  The carry-over kit MUTATED (see Variant axes). TT lost ONE submit: `zip.central_directory_member_names` in stored CD
  order REJECTED (CD shuffled for the first time) -> ascending sort CORRECT. Mastery: the pre-submit guard caught the
  same CD list emitted as a Python repr and fat Mach-O cputypes in fat_arch order -> `solver_incomplete` -> 3 generalize
  workers -> sorted compact JSON -> CORRECT on the single GM submit (in-window 5.9 s). Spelling confirmed: page size =
  plain base-10 bytes; sorted lists for CD names and cputype sets.

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes: base-10 integer, no units. Hashes: hex, case ignored.
- Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`). Booleans: enum `true` / `false`.
- Pixel dimensions (JPEG SOF, PNG IHDR, video D18): `<width>x<height>`, lowercase `x`, no spaces. Video = ffprobe
  width/height of v:0 (coded size, NOT rotated, not the tkhd display size).
- PDF header version: bare `x.y`; absent -> literal `none` (wording; `none` not yet GM-confirmed). Counts: plain integer.
  Struct sizes with a `_bytes` suffix (D23 page size): the decoded integer in bytes (`1` on disk -> `65536`).
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
  (D11), OOXML Target URL (D15), Message-ID WITH `<>` (D16), Android manifest `package` (D21), JAR `Main-Class` (D22).
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
  (most days, all of D15-23): ONE download holding `-01.zip`..`-0N.zip` (D7 three levels; D15-21 five kits, D22 six, D23
  seven, 4.6 MB); refs `<set zip> -> <member>`, names reused per set -> resolve by (set zip, member). D9: download
  `<id>-mastery.zip` vs refs `...-evidence-0N.zip` -> resolve by sha256 (`lib.common.container_by_sha`). D6: two
  same-named downloads -> `delivery N: <zip>` refs. Member numbering shifts between pre-fetched contract and live attempt.

## Pitfalls that cost time
- **Carry-over mutation (D23, 1 wrong TT submit + a Mastery generalize)**: an extractor that only ever saw one sample
  value is untested. Before a timed run, ask of every carried field "what if this is the multi-element / other-endian
  / other-codec case?" -- fat Mach-O, shuffled CD, Ogg audio, non-x86 PE/ELF machines all arrived the same day.
- **json list output**: sort + `json.dumps(..., separators=(",",":"))` at ONE choke point for every `json` id; a local
  override that returns a Python list gets `str()`'d to a repr (D23 Mastery). Check the emitted string, not the value.
- **Synthesis dispatch** (lost D15, D16, D17, D19): the timed kit always adds `metadata-day-NN-synthesis-sha256-order`.
  Start the day's solver from the previous day's solve.py (lane seed `local_answer` + `synthesis_answer` ->
  `lib.meta.synthesis.digest_order`, artifacts root set INSIDE `_solve_pairs`; Mastery forks one process per set).
- Registry misses: D14 key one suffix short; D16 fmt `eml` vs GM `email`; D17 `wav.*` vs `media.*`; D21 no `apk` fmt
  (a new CONTAINER family needs its own fmt word). D22 `jar` and D23 `sqlite` were prebuilt -> race-probe hits. Check
  `python3 -c "import lib.meta as m; print([k for k in m.known_fields() if k[0]=='<fmt>'])"`, grep
  `lib/meta/prebuilt/*.py` for the FIELD. D20 substring trap: `cpu_type_set` hit scalar `cpu_type` -> check the SHAPE
  vs answer_format (`_set`/`_list`/`_names` = a list).
- Unwired day template (D22): `hctf submit --from-solver` before today's field is dispatched emits literal `none`.
  Only submit from the solver once `solve.py` prints a real value for EVERY id.
- Id-slug parsing (D16, 1 wrong): ids repeat the fmt word (`d16-email-001-email-message-id`); anchor `-\d+-<fmt>-(.+)$`.
  Never submit `none` without grepping the bytes -- `none` = absent in the artifact, not "my parser returned None".
- Field suffix picks the spelling: `_u16_hex` = raw struct value (D9 not `i386`); `_codec_name` = tool vocabulary
  (`pcm_s16le`, not tag `1`); NO suffix on a binary-header code (D20) is still raw hex; `_bytes` = decoded integer.
- Byte order: ELF EI_DATA @5 / the Mach-O magic decide (fat headers ALWAYS BE, slices carry their own magic); SQLite
  header is ALWAYS big-endian. Fat cputype is in BOTH fat_arch and the slice header -- may disagree in a variant: the
  set field reads fat_arch. Video geometry has FOUR sources (stsd, SPS crop = ffprobe, tkhd, matrix); trust SPS-cropped.
- SQLite: page size `1` = 65536 (u16 overflow); WAL (`@18/@19 == 2`) does not change the page size; a truncated or
  embedded copy keeps a valid header -- read the header of the NAMED member, don't infer from file length.
- Manifest attributes (D22): CRLF, 72-byte wrap with ONE-space continuations, case-insensitive names, main section only.
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
  dnfile, mutagen, androguard (.venv); msitools under tools/msitools; ffmpeg 7.0.2 (no ffprobe) at
  `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2` (not on PATH). NOT installed: ffprobe, sox.
