# metadata-forensics — technique log (days 1-22; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, D8: "new, dynamic variations/mutations"): solvers derive structure, degrade per field.
- Every day = ONE evidence zip (plain Deflate, no password). D1-7: one tiny member, one fact; D8-9: cumulative kit in
  every mode; D10-14: one field everywhere. **D15+ split the modes**: single = 1 field (the new member), TT = cumulative
  kit (D15 20 -> D22 27 fields, +1/day), Mastery = 5 kits (D22: SIX) x the TT set, incl. a cross-member "synthesis"
  question. Pre-arm EVERY earlier family AND the synthesis before the timed run.
- Member families: note/text -> jpg -> png -> pdf -> inner zip -> Go PE (D9-11) -> .NET dll (D12) -> MSI (D13) -> LNK
  (D14) -> OOXML `.docx` (D15) -> `.eml` (D16) -> WAV (D17) -> MP4 (D18) -> ELF (D19) -> Mach-O `macos-001.bin` (D20)
  -> APK `mobile-001.apk` (D21) -> JAR `application-001.jar` (D22). Executables PE/ELF/Mach-O one header field each;
  D21-22 = zip-based PACKAGES (APK binary-AXML manifest; JAR text `META-INF/MANIFEST.MF`), one identity/launch field.
  fmt word = an ABSTRACT namespace sometimes (`email` not `eml`; `media` for audio D17 AND video D18, ffprobe
  vocabulary), else the plain format (`pe` `msi` `lnk` `elf` `macho` `apk` `jar`) -- read it from the question.
- Fields, one new per day: identity -> magic prefix -> `text.utf8_bom_present` -> `jpeg.sof_dimensions_pixels` ->
  `png.ihdr_dimensions_pixels` -> `pdf.header_version` -> `zip.eocd_total_entries` -> `zip.central_directory_member_names`
  -> `pe.coff_machine_u16_hex` -> `pe.address_of_entry_point_rva_hex` -> `pe.version_original_filename` ->
  `dotnet.mvid_guid` -> `msi.product_code_guid` -> `lnk.target_path_windows` -> `ooxml.external_relationship_targets` ->
  `email.message_id` -> `media.primary_audio_codec_name` -> `media.primary_video_dimensions` -> `elf.e_machine_u16_hex`
  -> `macho.cpu_type_set` (JSON list, one raw hex cputype per slice) -> `apk.package_name` -> `jar.main_class`.
  Question `Determine <fmt>.<field> for <member>`; id `dNN-<family>-NNN-<fmt>-<field>` (`.`/`_` -> `-`), `dNN` = the
  family's first day; `<family>` != `<fmt>` only for media (`d17-audio-001-media-`, `d18-video-...`).
- Flavor text promises extra findings that are NEVER asked (collisions, equivalent recordings, crops/claimed device,
  D19 deployment groups, D20 advertised fleet, D21 rebuilds vs clones, D22 "nested dependencies whose manifests disagree
  with their launchers"); the sample delivers less (D20 "universal" -> one THIN header; D22 "libraries ... nested" ->
  one flat 4-entry JAR). Graded = the STRUCTURAL truth; names/extensions/secondary metadata are the lie. Titles are
  puns on the field (D19 "Little Endian" = EI_DATA; D20 "Universal Appeal" = fat; D21 "Package Deal" = package name;
  D22 "Main Character Energy" = `Main-Class`).
- Singles: D1-9 first-submit ~27-60 s; D10, D13, D15 lost ONE submit to a convention (padding, braces, list order);
  D16 lost TWO (`none`, stripped `<>`); D20 lost ONE (`["arm64"]` -> hex won). Race probe from the prebuilt `lib.meta`
  registry: D18 ~5 s, D19 ~13 s, D22 ~19 s (`lib/meta/prebuilt/jar.py`); registry MISS -> live worker D17 ~24 s, D21 ~32 s.
  TT/Mastery: CORRECT every day; D15-17 + D19 only after an offline generalize (synthesis dispatch missing); D18,
  D20-22 in-window first try (D22 TT 5.4 s / Mastery 5.9 s in window).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen". Names drift: D1-14 `metadata-day-NN-evidence[-0N].zip`; D15-22
  TT `evidence.zip`, Mastery `evidence-01.zip` holding `evidence-01..0N.zip` (N=5; D22 N=6). Route by the ref's text
  before `->` and by sha256, never a hard-coded name.
- **Field-set / set count** -- D7 TT 11 / Mastery 22; D8-9 12-13 everywhere; D10-14 one; D15 1/20/100 ... D21 1/26/130
  (+1 field/day); D22 1/27/162 = SIX sets x 27 (first non-5). Enumerate `setN.` prefixes from the live ids. Families:
  identity + `d04-jpeg` `d05-png` `d06-pdf` `d07-zip` (eocd, CD names) `d09-pe` (machine, entry RVA, OriginalFilename)
  `d12-dotnet` `d13-msi` `d14-lnk` `d15-ooxml` `d16-email` `d17-audio` `d18-video` `d19-elf` `d20-macho` `d21-apk`
  `d22-jar` + synthesis. Dispatch on the answer-id SUFFIX (reference solver answering all 27:
  `challenges/day22/metadata-main-character-energy/solver/solve.py`; lane seed `local_answer` + `synthesis_answer` + lib.meta).
- **fmt word vs registry key vs id family** -- D16 `email.*` (prebuilt said `eml`); D17/D18 `media.*` ids
  `d17-audio-`/`d18-video-`; D19 `elf.e_machine_u16_hex` (spec name keeps its underscore -> `e-machine`); D20
  `macho.cpu_type_set`; D21 `apk.package_name` (container word, not `android`/`axml`); D22 `jar.main_class` (container
  word, not `java`/`manifest`; field = manifest attribute `Main-Class` snake_cased). Vocabulary = the field's home tool
  (ffprobe) or the spec struct/attribute; binary-header codes ALWAYS raw `0x` hex, even without `_hex` (D20). Rule: take
  `<fmt>.<field>` from the question (or the slug after `-NNN-`), map fmt synonyms (`email`<->`eml`/`mime`;
  `media`<->`audio`/`video`/`av`; `jar`<->`java_archive`/`war`), route the extractor by MAGIC + member names, fall back
  to the same field under any fmt.
- **Identity member roster** (D15+) -- THREE small text members (`evidence-note.txt` 33 B, `evidence-note-copy.txt`
  33 B, `roster.csv` 29 B); each identity question picks one per set: ids `<member-stem>-{filename,size-bytes,md5,sha1,
  sha256,magic-prefix-hex-16,text-utf8-bom-present}`. Filename question artifact = the container only -> map the stem.
- **Synthesis / cross-member** (D15+) -- id `metadata-day-NN-synthesis-<algo>-order` (TODAY's NN), kind `json`, norm
  `case_insensitive`, text "Compute the full-file SHA-256 digest of each named file, then submit a compact JSON array
  of their filenames in ascending digest order. Files: [...]". Rule: regex `Files:\s*(\[.*?\])`, resolve each under the
  ref's container, `hashlib.new(algo)` over raw bytes, sort by hex digest, emit names --
  `lib.meta.synthesis.digest_order(question, get_bytes, algo)` with get_bytes bound INSIDE the per-set worker. Shape:
  note + re-picked kit members + TODAY's member; 4 names D15-20, FIVE D21-22. The list differs between the 409
  contract and the live attempt (D20, D22) AND, D22, between sets of ONE Mastery (TT + set1-4 note/png/msi/wav/jar;
  set5-6 note/pdf/msi/wav/jar) -- parse each set's own text; order re-rolls per set. Only sha256 seen.
- **Decoys** -- renamed copies, misleading extensions, secondary metadata (EXIF, catalog /Version): answer from the
  structural bytes of the named member. Kits pool `collector-001.elf` with `MZ` members: `elf.*` of a non-ELF = `none`.
- **Member values** -- re-roll per variant; never cache across sets. Re-rolled: note case id; D7 entry count 2-5;
  jpg/png dims per set; D10 entry RVA; D11 PE arch (0x014c/0x8664/0xaa64, OriginalFilename follows); D12 MVID;
  synthesis order. Constant so far (don't rely on it): ProductCode, lnk target, docx targets, codec `pcm_s16le`, video
  `320x180`, the D19 ELF, the D20 thin arm64 Mach-O, the D21 APK, the D22 JAR (1 146 B, one Main-Class) in every
  mode/set. The flavors' BE/fat/nested/launcher variants are still due: read byte order from the file, walk every
  slice, parse the whole manifest.
- **Answer kinds** -- `exact_text`, `integer`, `pattern` (hashes case-insensitive; `0x`-hex `trim` only -> lowercase),
  `enum` (`accepted_values`), `json` (compact array, "exact values and order" -- ORDER is field-specific, see
  conventions). `*_set`/`*_names`/`*_targets` under `json` = a list even with ONE element (D20 `["0x0100000c"]`).
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
| `zip.central_directory_*` | walk `PK\x01\x02` from cd offset: name len @+28, extra @+30, comment @+32, name @+46. Raw stored path, CD order, no dedupe/sort; UTF-8 if flag 0x800 else UTF-8-then-cp437 |
| `pdf.header_version` | `head -c 16 f | xxd` -> `%PDF-x.y` at offset 0; catalog `/Version` is a diagnostic only |
| `pe.coff_*` | `MZ` -> e_lfanew u32 @0x3C -> require `PE\0\0` -> Machine u16 @+4; OptionalHeader magic @+24 (`0x10b`/`0x20b`) |
| `pe.address_of_entry_point_*` / `pe.image_base*` | opt = e_lfanew+24: AddressOfEntryPoint u32 @opt+16 (RVA); ImageBase @opt+28 (PE32) / u64 @opt+24 (PE32+). objdump "start address" is the VA |
| `pe.version_*` | `pefile` resource dir only -> `FileInfo..StringTable..entries`; id tail -> key ignoring case/`-_`. Shell: `strings -e l f.exe \| grep -A1 OriginalFilename` |
| `elf.*` (`7f 45 4c 46`) | EI_CLASS @4 (1=32, 2=64), EI_DATA @5 (1=LSB `<`, 2=MSB `>`) picks the struct byte order for EVERYTHING after @16: e_type u16 @16, e_machine u16 @18, e_version u32 @20, e_entry @24 (u32/u64 by class). `xxd -s 16 -l 4 f` + `readelf -h f`. In-window: `lib.meta` fmt `elf` (~45 fields: ei_*, e_type, e_entry_hex, e_flags, interp, build-id, section names). D19 `3e 00` LSB -> `0x003e` |
| `macho.*` (`cf fa ed fe` LE-64, `ce fa ed fe` LE-32, `fe ed fa ce/cf` BE; fat `ca fe ba be` / fat64 `ca fe ba bf`, always BE) | thin: cputype u32 @4, cpusubtype @8, filetype @12, ncmds @16 (byte order from the magic). Fat: nfat_arch u32 @4, then 20-B (fat64 32-B) fat_arch {cputype, cpusubtype, offset, size, align}; Java class shares `cafebabe` (major @6 >= 45). D20 `cpu_type_set` = JSON list `"0x%08x"` per slice (thin = 1). `xxd -l 32 f`; `rabin2 -I f`; `lipo -archs` (M). `lib.meta` fmt `macho` |
| `apk.*` / `.apk` (`PK` + `AndroidManifest.xml` + `classes.dex`, `META-INF/*.RSA/.SF/MANIFEST.MF`) | manifest is BINARY AXML (`03 00 08 00`): `aapt dump badging f.apk \| head -1` -> `package: name='..' versionCode versionName platformBuild..` (on PATH after `source bin/env.sh`); `androguard` `APK(b, raw=True).get_package()`; stdlib: `lib/meta/apk.py manifest_attr(axml, 'manifest', 'package')` (string pool + START_ELEMENT walk). `strings -e l AndroidManifest.xml` for orientation. Triage routes APKs to `$mobile-android` -- ignore it, the question is a header field |
| `jar.*` / `.jar/.war/.ear` (`PK` + `META-INF/MANIFEST.MF` + `*.class` `cafebabe`) | `unzip -p f.jar META-INF/MANIFEST.MF` (text, CRLF, 72-B lines, continuation = ONE leading space joined); main section = up to the first blank line; attr names case-insensitive. D22 `main_class` = `Main-Class` value verbatim (dotted name, no `.class`). Cross-check `<name with / >.class` exists + `javap -v` (or u16 BE major @6) only as a diagnostic. Spring Boot: `Main-Class` = `org.springframework.boot.loader.*Launcher`, app = `Start-Class`; nested `BOOT-INF/lib/*.jar`. In-window: `lib/meta/prebuilt/jar.py` (fmt `jar`, ~40 manifest/class-version fields). Triage routes `.class` to `$binary-re` -- ignore |
| `dotnet.*` / Mono assembly | data dir 14 -> CLI header -> `BSJB` -> `#~` (HeapSizes @+6, Valid @+8, rows @+24) -> Module row 0 Mvid (1-based #GUID idx) -> `uuid.UUID(bytes_le=..)`. `lib/meta/dotnet.py` |
| `msi.*` / `.msi` (OLE `d0 cf 11 e0`) | fast: `strings -n 6 x.msi \| grep -aoE 'ProductCode\{[0-9A-F-]{36}\}'`; exact: CFB streams -> `!_StringPool`/`!_StringData` -> `!Property` (column-major). `olefile` in venv; `day13/.../solve.py msi_property` |
| `lnk.*` / `.lnk` (`4c 00 00 00` + CLSID 00021401) | LinkFlags @0x14 (0x1 IDList, 0x2 LinkInfo, 0x80 Unicode); target = LinkInfo LocalBasePath (+CommonPathSuffix) verbatim, else IDList. `lib.meta.lnk:target_path` |
| `ooxml.*` / `.docx/.xlsx/.pptx` (`PK` + `[Content_Types].xml`) | zip of XML parts. Relationships live in EVERY `*.rels` part. External = `TargetMode="External"` (case-insensitive; absent = Internal). `unzip -p f.docx '*.rels' \| grep -o 'Target="[^"]*" TargetMode="External"'`; solver: `zipfile` + ElementTree over every `.rels`, local-name `Relationship` |
| `email.*` / `.eml` (text `From:`/`Message-ID:`/`MIME-Version:`, CRLF) | `grep -ai '^message-id' f.eml`; solver: `lib.meta.prebuilt.eml.eml_value(data, {"field": f})` (stdlib `email`, unfolded raw header). Values VERBATIM (Message-ID keeps `<...>`). Threading = `In-Reply-To`/`References`/`Message-ID` |
| `media.*` / audio (`RIFF..WAVE`, `ID3`/`ff fb`, `OggS`, `fLaC`, `ftyp`, `1a 45 df a3`, `FORM..AIFF`, `#!AMR`) | route by MAGIC. WAV: RIFF chunks from @12 to `fmt ` -> wFormatTag u16 @+8, bits u16 @+22 (0xFFFE -> SubFormat GUID first u16 @+32) -> FFmpeg names (Conventions). Truth: `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2 -hide_banner -i f` (no ffprobe; `mediainfo` says `PCM` = wrong vocabulary). In-window: `lib.meta` fmt `media`/`audio`/`av` |
| `media.*video*` / MP4-MOV (`....ftyp`), MKV/WebM, AVI | box walk `moov` -> first `trak` whose `mdia/hdlr` = `vide` -> `stsd` entry: w,h u16 BE @entry+32; cross-check tkhd w/h + matrix, `pasp`, `clap`, SPS crop (may DISAGREE in a variant). In-window: `lib.meta` fmt `media`/`video` (`prebuilt/media_video.py`). Truth: bundled `ffmpeg -i` -> `Video: h264 (High) ..., 320x180 [SAR 1:1 DAR 16:9]` |
| `*-synthesis-<algo>-order` / "Files: [...]" in the question | parse the list from the question text, hash each member of the same container, sort by digest, compact JSON of names |
| GUID field (`*-guid`) | spelling follows the SOURCE: stored string (MSI) verbatim braces+uppercase; binary (.NET) -> lowercase, no braces |
| exe-extension decoy (`MZ` without `PE\0\0` at e_lfanew) | literal `none` if the syntax offers it; never fall back to a later `PE\0\0` hit |
| "impostor", "renamed", "disguise", "pooled with ... renamed data" | trust magic bytes at offset 0; a matching string deeper in the file is a decoy |
| answer_format kind `json` | `json.dumps(v, separators=(",",":"), ensure_ascii=False)`; decide ORDER per field (conventions) |
| Mastery `set1.`..`setN.` ids | resolve each set's container separately; see delivery layouts |

## Day by day
**Days 1-14** (one field each, all timed first try): D1 identity -> D2 `magic-prefix-hex-16` -> D3 BOM -> D4 JPEG SOFn
`<w>x<h>` -> D5 PNG IHDR -> D6 `pdf.header_version` `x.y` -> D7 `zip.eocd_total_entries` of the INNER zip -> D8 CD names
(compact JSON, CD order) -> D9-11 one Go PE: `coff_machine_u16_hex` `0x014c`, entry RVA `0x%08x` (unpadded REJECTED),
`version_original_filename` verbatim -> D12 `dotnet.mvid_guid` (`uuid.UUID(bytes_le)` lowercase, no braces) -> D13
`msi.product_code_guid` (stored WITH braces; brace-less REJECTED) -> D14 `lnk.target_path_windows` (LinkInfo path).

**Days 15-21** (single = 1 new-family field; TT/Mastery = cumulative kit + synthesis): D15 `ooxml.external_relationship_
targets` (rels `TargetMode="External"` Targets SORTED; rels order REJECTED). D16 `email.message_id` (VERBATIM with `<>`;
2 lost: id regex -> `none`, stripped brackets). D17 `media.primary_audio_codec_name` (WAV PCM16 -> `pcm_s16le`). D18
`media.primary_video_dimensions` (first `vide` trak stsd -> `320x180`; prebuilt hit ~5 s). D19 "Little Endian"
`elf.e_machine_u16_hex` (e_machine @18 in EI_DATA order -> `0x003e`; i386 `0x0003`, MIPS `0x0008`, PPC `0x0014`, ARM
`0x0028`, AArch64 `0x00b7`, RISC-V `0x00f3`; prebuilt hit ~13 s). D20 "Universal Appeal" `macho.cpu_type_set` (56-B
THIN `cffaedfe` arm64 header, cputype u32 @4 -> `["0x0100000c"]`: raw struct hex in a JSON list, thin = one element;
`["arm64"]` REJECTED +5 s; fat/archives/fleet flavor only; ~39 s). D21 "Package Deal" `apk.package_name` (8 535-B
APK, binary-AXML `<manifest package=>` verbatim `com.huntress.arena.p<8 digits>` -- NOT the inline `android:label`, NOT
the filename; `aapt dump badging | head -1`; registry MISS -> ~32 s live). Timed D15-D17 + D19: synthesis dispatch
missing from the day's template -> `solver_incomplete` -> offline generalize -> CORRECT; D18, D20, D21 pre-wired -> first try.

**Day 22 — Main Character Energy** (`jar.main_class`, kind `exact_text`, norm `trim`, id `d22-jar-001-jar-main-class`).
Prompt: "Java archives contain libraries, applications, and nested dependencies whose manifests disagree with their
launchers. Determine what is runnable and where execution begins."
- Artifact: `metadata-day-22-evidence.zip` (741 B) -> `application-001.jar` (1 146 B, 4 deflated entries):
  `META-INF/MANIFEST.MF` (111 B, CRLF: `Manifest-Version: 1.0` / `Main-Class: arena.evidence.ArtifactMain` /
  `Created-By: Huntress Artifact Assembly Line` + blank line), `arena/evidence/ArtifactMain.class` (370 B, major 52 =
  Java 8 -- the class the manifest names DOES exist), filler `evidence/header.bin` (`HUNTRESS`) + `evidence/marker.txt`
  (12 hex chars). No nested jars, no Spring Boot launcher, no signature, no Class-Path: the "disagree" flavor was unasked.
- Insight: `main_class` = the manifest's `Main-Class` attribute value verbatim (binary name with dots, no `.class`, no
  `/`, CRLF/trailing space trimmed). Not the class path in the zip, not `Created-By`, not a decompiled `main` hunt.
- Tools: `unzip -p f.jar META-INF/MANIFEST.MF`; stdlib `zipfile` + manifest parse (continuations, case-insensitive
  keys). Prebuilt `lib/meta/prebuilt/jar.py` (D21-night `jar-manifest-class-versions` gap) answered it in the race probe
  -> GM CORRECT at +19 s. A `--from-solver` submit of `none` from the unwired day template landed at +28 s, AFTER the
  CORRECT (`already_solved`, harmless) -- it would have been a wrong submit had the probe missed.
- Timed: TT 27 / Mastery 162 (six sets) CORRECT first try in-window (5.4 s / 5.9 s); synthesis Files varied per set.
  Spelling confirmed: dotted binary name verbatim; nothing rejected. Time to CORRECT: single ~19 s, 0 wrong.

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes: base-10 integer, no units. Hashes: hex, case ignored.
- Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`). Booleans: enum `true` / `false`.
- Pixel dimensions (JPEG SOF, PNG IHDR, video `media.primary_video_dimensions` D18): `<width>x<height>`, lowercase
  `x`, no spaces. Video = ffprobe width/height of v:0 (coded size, NOT rotated, not the tkhd display size).
- PDF header version: bare `x.y`; absent -> literal `none` (wording; `none` not yet GM-confirmed). Counts: plain integer.
- JSON lists -- compact, double quotes, no spaces; ORDER depends on the field:
  - `zip.central_directory_member_names`: full stored paths in CD order (`["room-01/item-1.txt","room-02/item-1.txt"]`).
  - `ooxml.external_relationship_targets`: Target strings SORTED ascending (D15 all modes); rels-file order REJECTED.
  - `*-synthesis-<algo>-order`: member names ordered by hex digest ascending (D15-D20 TT/Mastery; `case_insensitive`).
  - `macho.cpu_type_set`: `["0x%08x", ...]` one per slice; thin = one element (D20). Fat: fat_arch order (unverified).
  Heuristic: a list read off one on-disk structure that the field name calls "names in the directory" keeps disk
  order; a set gathered across parts ("targets", "dependencies") is sorted. If an order is rejected, try the other.
- Header integers as hex (`*_hex`): `0x` + lowercase hex ZERO-PADDED to the struct field's width: u16 PE Machine
  `0x014c`, u16 ELF e_machine `0x003e` (D19), u32 AddressOfEntryPoint `0x00065bd0`, u32 Mach-O cputype `0x0100000c`
  (D20, inside a JSON list, even without `_hex` in the id; ABI64 bit kept, no name). Width from the STRUCT / the
  `_uNN_` in the id; the value from the file's own byte order (ELF EI_DATA). (Magic-prefix hex has NO `0x`; the
  binary lane's machine wants `i386` and accepted unpadded entry points -- different generator.)
- GUIDs: .NET MVID `Guid.ToString()` lowercase no braces (D12); MSI ProductCode the stored string uppercase WITH braces
  (D13). Spelling follows the source, not answer_format.
- Stored strings VERBATIM (no quotes, case kept, delimiters kept): LNK LinkInfo path (backslashes, drive letter; D14),
  PE StringFileInfo value incl. extension (D11), OOXML Target URL as stored (D15), e-mail header after RFC 5322
  unfolding -- Message-ID WITH `<>` (D16), Android manifest `package` attribute (dotted applicationId, D21), JAR
  manifest `Main-Class` value after continuation-joining (dotted binary name, no `.class`, D22).
- Media codec names (`media.*codec_name`, D17): ffprobe `codec_name`: WAV tag 1 -> `pcm_u8`/`pcm_s16le`/`pcm_s24le`/
  `pcm_s32le` by bits (RIFX `..be`), 3 `pcm_f32le`, 6 `pcm_alaw`, 7 `pcm_mulaw`, 0x55 `mp3`; only `pcm_s16le` verified.
- Rejected spellings: `0x65bd0` (D10, unpadded); brace-less MSI GUID (D13); rels-file-order target list (D15);
  bracket-less Message-ID (D16); `["arm64"]` arch name for `macho.cpu_type_set` (D20). Pattern: delimiters that are part of the stored value (`{}`, `<>`) stay.
- Inference: the field id IS the spec name (`sof_` = SOF header, `eocd_total_entries` = the EOCD's own claim,
  `e_machine` = Elf_Ehdr member) -- read it literally to pick the structure. A claimed count is NOT a CD walk; CD
  names are NOT local-header names; `_uNN_hex` fixes read+print width. Unverified ELF siblings: bare enum-ish fields
  (`ei_data`, `e_type`) have no GM spelling yet -- lib emits `ELFDATA2LSB` / `2`; prefer the `_hex` form if offered.
  D20 extends it: header CODES (machine, cputype, subtype, filetype) are emitted as raw `0x` hex, never as tool names.

## Delivery layouts seen (resolve these before parsing)
- Single / TT: one zip; members named in `artifact` after `->` (filename questions: artifact = the zip only). Mastery
  (most days, all of D15-22): ONE download holding `-01.zip`..`-0N.zip` (D7 three levels; D15-21 five kits, D22 six); refs
  `<set zip> -> <member>`, names reused per set -> resolve by (set zip, member). D9: download `<id>-mastery.zip` vs refs
  `...-evidence-0N.zip` -> resolve by sha256 (`lib.common.container_by_sha`). D6: two same-named downloads ->
  `delivery N: <zip>` refs. Member numbering shifts between pre-fetched contract and live attempt -- never hardcode.

## Pitfalls that cost time
- **Synthesis dispatch** (lost D15, D16, D17, D19 -> `solver_incomplete` -> ~1 min offline generalize per mode): the
  timed kit always adds `metadata-day-NN-synthesis-sha256-order`. Use the lane seed (`local_answer` +
  `synthesis_answer` -> `lib.meta.synthesis.digest_order`, artifacts root set INSIDE `_solve_pairs`; Mastery forks one
  process per set) and only add today's field -- D18, D20-D22 were clean that way. Identity must accept ANY member stem.
- Registry misses: D14 key one suffix short (`lnk.target_path`); D16 fmt `eml` vs GM `email`; D17 `wav.*` vs `media.*`;
  D21 no `apk` fmt at all (prebuilt had `dex`/`jar`/`java` -- a new CONTAINER family needs its own fmt word, not just
  its inner members) -> ~32 s LLM solve instead of ~5-19 s. D22 HIT: the D21-night gap built fmt `jar` (container
  word + manifest fields) -> probe CORRECT ~19 s. Check `python3 -c "import lib.meta as m; print([k for k in
  m.known_fields() if k[0]=='<fmt>'])"`, grep `lib/meta/prebuilt/*.py` for the FIELD, call the nearest extractor.
  D20 substring trap: `cpu_type_set` hit macho's scalar `cpu_type` -> bare hex where `json` wants a list: check the
  SHAPE vs answer_format (`_set`/`_list`/`_names` = one entry per slice/member; wrap a thin value in `[...]`).
- Unwired day template (D22): `hctf submit --from-solver` before today's field is dispatched emits literal `none`
  for it. Only submit from the solver once `solve.py` prints a real value for EVERY id (the race probe saved D22).
- Manifest attributes (D22): text, but parse it properly -- CRLF, 72-byte wrap with ONE-space continuations, case-
  insensitive names, main section only (per-entry `Name:` sections after the first blank line are NOT main attrs).
  Spring Boot / launcher jars: `Main-Class` is the launcher, `Start-Class` the app -- answer the attribute the field names.
- Id-slug parsing (D16, 1 wrong): ids repeat the fmt word (`d16-email-001-email-message-id`); anchor `-\d+-<fmt>-(.+)$`.
  Never submit `none` without grepping the bytes -- `none` = absent in the artifact, not "my parser returned None".
- Field suffix picks the spelling: `_u16_hex` = raw struct value (D9 not `i386`; D19 not `x86-64`); `_codec_name` =
  tool vocabulary (D17 `pcm_s16le`, not tag `1`/mediainfo `PCM`); NO suffix on a binary-header code (D20, 1 wrong) is
  still raw hex, not `arm64`. Only a field that SAYS `_name`/`_arch_names`/`_label` gets a name; `apk.package_name` is
  the applicationId, not the human label (`android:label` = the "product name").
- Byte order (D19 pun): ELF EI_DATA @5 / the Mach-O magic decide (`cffaedfe` = LE; fat headers ALWAYS BE, slices carry
  their own magic); ELF32 vs ELF64 moves every offset after e_version. Fat cputype is in BOTH fat_arch and the slice
  header -- may disagree in a variant: the set field reads fat_arch. Video geometry has FOUR sources (stsd, SPS crop =
  ffprobe, tkhd display, tkhd matrix); D18 agreed; on disagreement trust the SPS-cropped size.
- JSON list ORDER (D15, 1 wrong + ~26 s): "exact values and order" does not say WHICH order -- decide per field
  (conventions) before the first submit. Don't reshape stored strings (D13 braces); hex width (D10) `0x%0{2*size}x`.
- A pre-fetched TT/Mastery `contract.json` is the 409 `start_required` body (questions, NO `answer_ids`); answer under
  the live ids. Only the named field is graded -- the flavor never widens it.
- Container-of-containers: a naive `rfind(PK\x05\x06)` reads the OUTER EOCD; a name lookup on zip-of-zips returned `PK`
  as the "magic". Resolve the named member's bytes first (recurse), then parse. Hostile CD names (`../`, dupes) as-is.
- Decoys: `*-with-bom.txt`, `.exe` that is text, `.bin` that is PDF, friendly APK filenames: bytes win. Require
  `PE\0\0` / `\x7fELF` / a Mach-O magic / `AndroidManifest.xml` / `META-INF/MANIFEST.MF` before any field of that
  format (else `none`; a jar WITHOUT a `Main-Class` -- a library -- is `none` for `main_class`).
- Timed windows are seconds, mostly GM round-trips (D22 TT start 1.9 s + solve 3.3 s + submit 2.1 s; Mastery 2.0 +
  2.6 + 3.3 s for 162 fields). Parse in memory, never shell out in-window; decompress each member once, cache by (set zip, member).
- Tools installed: exiftool, poppler, qpdf, mutool, pdf-parser, pdfid, pngcheck, zsteg, steghide, binwalk, foremost,
  mediainfo, sqlite3, ImageMagick, readelf/objdump, aapt + apktool/jadx (`source bin/env.sh`), olevba/oleid, olefile,
  pefile, pyelftools, LnkParse3, dnfile, mutagen, androguard (.venv; androguard is gate-allowed in-window); msitools
  under tools/msitools; ffmpeg 7.0.2 (no ffprobe) at `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/
  ffmpeg-linux-x86_64-v7.0.2` (not on PATH). NOT installed: ffprobe, sox.
