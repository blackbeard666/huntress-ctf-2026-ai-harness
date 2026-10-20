# metadata-forensics — technique log (days 1-20; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every day = ONE evidence zip (plain Deflate, no password so far). D1-7: one tiny member, ONE structural fact. D8-9:
  the cumulative kit, every field in every mode. D10-14: one member + one field everywhere. **D15+ split the modes**:
  single = 1 field (the new member), TT = cumulative kit (D15 20 -> D20 25 fields, +1 per day = the day's new member),
  Mastery = 5 kits x the TT set, incl. a cross-member "synthesis" question every day. Pre-arm EVERY earlier family AND
  the synthesis before the timed run; the timed field set is not the single's.
- Member families: note/text -> jpg -> png -> pdf -> inner zip -> Go PE (D9-11) -> .NET dll (D12) -> MSI (D13) -> LNK
  (D14) -> OOXML `.docx` (D15) -> `.eml` (D16) -> RIFF/WAVE audio (D17) -> MP4 h264+aac video (D18) -> Linux ELF (D19)
  -> Mach-O `macos-001.bin` (D20). Executables now span PE/ELF/Mach-O, one header field each (the "architecture" trio).
  The fmt word is sometimes an ABSTRACT namespace (`email` not `eml`; `media` for BOTH audio D17 and video D18, with
  ffprobe vocabulary) and sometimes the plain format (`elf` D19, `macho` D20, like `pe`/`msi`/`lnk`) -- read it.
- A new `<fmt>.<field>` each day: identity -> magic prefix -> `text.utf8_bom_present` -> `jpeg.sof_dimensions_pixels` ->
  `png.ihdr_dimensions_pixels` -> `pdf.header_version` -> `zip.eocd_total_entries` -> `zip.central_directory_member_names`
  -> `pe.coff_machine_u16_hex` -> `pe.address_of_entry_point_rva_hex` -> `pe.version_original_filename` ->
  `dotnet.mvid_guid` -> `msi.product_code_guid` -> `lnk.target_path_windows` -> `ooxml.external_relationship_targets` ->
  `email.message_id` -> `media.primary_audio_codec_name` -> `media.primary_video_dimensions` -> `elf.e_machine_u16_hex`
  -> `macho.cpu_type_set` (first SET-valued header field: JSON list of raw hex cputypes, one per slice).
  The question names the field (`Determine <fmt>.<field> for <member>`); ids `dNN-<family>-NNN-<fmt>-<field>` (`.`/`_`
  -> `-`); `dNN` = the family's first day; `<family>` != `<fmt>` for media (`d17-audio-001-media-`, `d18-video-...`).
- The flavor text promises extra findings ("the collision", "the impossible destination", "equivalent recordings",
  "crops ... the claimed device", D19 "several systems ... rebuild deployment groups", D20 "thin and universal binaries
  mixed with archives ... what truly supports the advertised fleet") that were NEVER asked; the sample delivers less (D9
  "several architectures" -> one i386 PE; D19 -> one x86-64 ELF; D20 "universal" -> one THIN arm64 header). The graded
  field is the STRUCTURAL truth from header bytes; names/extensions/secondary metadata are the lie. Pre-arm siblings
  without guessing spellings. Titles are puns (D19 "Little Endian" = EI_DATA; D20 "Universal Appeal" = universal/fat).
- Singles: D1-9 first-submit CORRECT ~27-60 s; D10, D13, D15 lost ONE submit to a convention (padding, braces, list
  order); D16 lost TWO (parser -> `none`, stripped brackets); D17 ~24 s; D18 ~5 s and D19 ~13 s (race probe answered
  from the prebuilt `lib.meta` registry before any LLM work); D20 lost ONE to vocabulary (`["arm64"]` name -> hex won,
  ~39 s). TT/Mastery: CORRECT every day, but D15-D17 AND D19 only after an offline generalize (synthesis dispatch
  missing from the day's solver); D18 and D20 in-window first try (D20 TT 3.9 s / Mastery 5.8 s in window).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen". Container NAMES drift: D1-14 `metadata-day-NN-evidence[-0N].zip`;
  D15-20 TT `evidence.zip`, Mastery `evidence-01.zip` holding `evidence-01..05.zip`. Route by the ref's text before
  `->` and by sha256, never a hard-coded name.
- **Field-set size** -- per mode: D7 TT 11 / Mastery 22; D8-9 12-13 everywhere; D10-14 one; D15 1/20/100; D16 1/21/105;
  D17 1/22/110; D18 1/23/115; D19 1/24/120; D20 1/25/125. Families: identity + `d04-jpeg-*`, `d05-png-*`, `d06-pdf-*`,
  `d07-zip-*` (eocd + CD names), `d09-pe-*` (machine, entry RVA, OriginalFilename), `d12-dotnet-*`, `d13-msi-*`,
  `d14-lnk-*`, `d15-ooxml-*`, `d16-email-*`, `d17-audio-*`, `d18-video-*`, `d19-elf-*`, `d20-macho-*` + synthesis.
  Dispatch on the answer-id SUFFIX (reference solver answering all 25:
  `challenges/day20/metadata-universal-appeal/solver/solve.py`).
- **fmt word vs registry key vs id family word** (D16-D20) -- D16 `email.*` (prebuilt said `eml`); D17
  `media.primary_audio_codec_name` id `d17-audio-...`; D18 `media.primary_video_dimensions` id `d18-video-...` (one
  `media` namespace spans two families); D19 plain `elf.e_machine_u16_hex` id `d19-elf-001-elf-e-machine-u16-hex`
  (family = fmt; spec name `e_machine` keeps its own underscore -> `e-machine`); D20 plain `macho.cpu_type_set` id
  `d20-macho-001-macho-cpu-type-set`. Vocabulary = the field's home tool (ffprobe for media) or the spec struct
  (`e_machine`, `coff_machine`, Mach-O `cputype`) -- for binary headers ALWAYS the raw struct integer in `0x` hex, even
  when the id has no `_hex` suffix (D20 `cpu_type_set` -> `0x0100000c`, name `arm64` REJECTED). Rule: take `<fmt>.<field>` from the QUESTION
  text (or the slug after `-NNN-`), map fmt synonyms (`email`<->`eml`/`mime`; `media`<->`audio`/`video`/`av`/...),
  route the extractor by the member's MAGIC, fall back to the same field under any fmt.
- **Identity member roster** (D15+) -- THREE small text members (`evidence-note.txt` 33 B, `evidence-note-copy.txt`
  33 B, `roster.csv` 29 B); EACH identity question picks one at random per set: ids `<member-stem>-{filename,size-bytes,
  md5,sha1,sha256,magic-prefix-hex-16,text-utf8-bom-present}`. The filename question's artifact = the container only
  ("the exact filename of the roster") -> map the id stem to the member. Never assume `evidence-note-*`.
- **Synthesis / cross-member** (D15+) -- id `metadata-day-NN-synthesis-<algo>-order` (TODAY's NN), kind `json`, norm
  `case_insensitive`: "Compute the full-file SHA-256 digest of each named file, then submit a compact JSON array of
  their filenames in ascending digest order. Files: [...]". The `artifact` names ONE member; the inputs are the
  `Files:` list, same container. Rule: regex `Files:\s*(\[.*?\])`, resolve each under the ref's container,
  `hashlib.new(algo)` over raw bytes, sort by hex digest (descending only if said), emit names --
  `lib.meta.synthesis.digest_order(question, get_bytes, algo)`, get_bytes bound to the artifacts root INSIDE the per-set
  worker. Shape: note + 2 re-picked kit members (jpg/exe/docx D15, png/dll D17, png/msi D18, pdf/lnk D19) + TODAY's
  member (D20 live: pdf/lnk + `macos-001.bin`; the pre-fetched contract listed zip/docx -- Files differ between the 409
  body and the live attempt, always read the live text); order re-rolls per set. Only sha256 seen so far.
- **Decoys** -- renamed copies, misleading extensions, secondary metadata (EXIF, catalog /Version) that disagree with the
  header: answer from the structural bytes of the member the question names. D19 kit pools `collector-001.elf` with
  `MZ` members (`telemetry-agent-001.exe`, `managed-001.dll`): an `elf.*` field of a non-ELF = literal `none`.
- **Member values** -- re-roll per variant; never cache across sets. Seen re-rolled: note case id; D7 entry count
  2-5; jpg/png dims per set (423x1089, 1255x1059); D10 entry RVA; D11 PE arch (0x014c/0x8664/0xaa64, OriginalFilename
  `pe-base-<goarch>.exe` follows); D12 MVID; synthesis order. Constant so far (don't rely on it): D13 ProductCode,
  D14 lnk target, D15 docx targets, kit exe/dll/msi/lnk, D17 codec `pcm_s16le`, D18 video `320x180`, D19 ELF (the same
  14 408-B x86-64 LSB ELF64 ET_EXEC in single, TT and all 5 Mastery sets), D20 Mach-O (the same 56-B thin MH_MAGIC_64
  arm64 header + one LC_UUID everywhere) -- the flavors' transcodes/crops/"several systems"/"universal" (BE MIPS/PPC,
  fat x86_64+arm64) are still due: read with the file's own EI_CLASS/EI_DATA / Mach-O magic, walk every fat slice.
- **Answer kinds** -- `exact_text`, `integer`, `pattern` (hashes case-insensitive; `0x`-hex is `trim` only -> lowercase),
  `enum` (`accepted_values`), `json` ("compact valid JSON array with exact values and order"). Emit per kind; read
  `syntax` for prefix/case. JSON ORDER is field-specific -- see conventions. A `json` kind on a field that is a scalar
  in the struct (`*_set`, `*_names`, `*_targets`) = a list even with ONE element (D20 thin -> `["0x0100000c"]`).
- **Question-text tags** -- D9 timed: ` [assigned-artifact-sha256:<64 hex>]` suffix; D15+ timed: ``Inspect `<member>`. ``
  prefix. Strip both before reading names; route by id + `artifact`.
- **Nesting depth** -- the asked file may sit 2-3 zips deep (Mastery D7); resolve by the name after `->`, never answer
  from an enclosing zip. An OOXML member is itself a zip -- parse it as the asked member, not as a wrapper to descend.

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

**Days 15-19** (single = 1 new-family field; TT/Mastery = cumulative kit + synthesis): D15 `ooxml.external_relationship_
targets` (rels `TargetMode="External"` Targets SORTED; rels order REJECTED). D16 `email.message_id` (VERBATIM with `<>`;
2 lost: id regex -> `none`, stripped brackets). D17 `media.primary_audio_codec_name` (WAV PCM16 -> `pcm_s16le`). D18
`media.primary_video_dimensions` (first `vide` trak stsd -> `320x180`; prebuilt hit ~5 s). D19 "Little Endian"
`elf.e_machine_u16_hex` (e_machine @18 in EI_DATA order -> `0x003e`; i386 `0x0003`, MIPS `0x0008`, PPC `0x0014`, ARM
`0x0028`, AArch64 `0x00b7`, RISC-V `0x00f3`; prebuilt hit ~13 s). Timed D15-D17 + D19: synthesis dispatch missing from
the day's template -> `solver_incomplete` -> offline generalize -> CORRECT; D18 pre-wired -> first try.

**Day 20 — Universal Appeal** (`macho.cpu_type_set`, kind `json` "compact valid JSON array with exact values and
order", norm `trim`, id `d20-macho-001-macho-cpu-type-set`). Prompt: "A macOS deployment includes thin and universal
binaries mixed with archives. Enumerate every CPU type and identify what truly supports the advertised fleet."
- Artifact: `macos-001.bin`, 56 B, header-only THIN Mach-O: `cffaedfe` (MH_MAGIC_64, LE), cputype `0c 00 00 01` =
  0x0100000c (ARM 12 | ABI64 0x01000000 = CPU_TYPE_ARM64), subtype 0, filetype 2 EXECUTE, ncmds 1 (LC_UUID 0x1b).
  Identical in single, TT and all 5 Mastery sets; universal/archives/fleet were flavor only.
- Insight: "universal" = fat -> a SET field (one cputype per fat_arch slice); thin -> one element. Spelling = the raw
  u32 struct value like D9/D19: `["0x0100000c"]` (8 padded digits, ABI64 bit kept). `["arm64"]` was REJECTED.
- Tools: `xxd -l 32 f` (cputype @4, byte order from the magic); `rabin2 -I` / lief for orientation. Prebuilt `macho`
  matched `cpu_type_set` via its scalar `cpu_type` branch (bare hex) -> the worker wrapped it in a list. Fat order
  (fat_arch order vs sorted, dedupe) is NOT yet GM-verified.
- Single: wrong `["arm64"]` +34 s, CORRECT +39 s. TT 25 / Mastery 125 CORRECT in-window first try (solver carried the
  D19 synthesis dispatch forward; no generalize).

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
- Windows paths (`lnk.target_path_windows`): stored LinkInfo path verbatim (backslashes, case, drive letter, no quotes).
- Version-resource strings (`pe.version_<field>`): StringFileInfo value verbatim incl. extension.
- URLs (`ooxml` Targets): the attribute value verbatim -- scheme, host, path as stored; no trailing-slash or case fixups.
- E-mail headers (`email.<field>`): header value as stored after RFC 5322 unfolding; Message-ID WITH `<>` (D16).
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
  (most days, all of D15-20): ONE download holding `-01.zip`..`-0N.zip` (D7 three levels; D15+ five full kits); refs
  `<set zip> -> <member>`, names reused per set -> resolve by (set zip, member). D9: download `<id>-mastery.zip` vs refs
  `...-evidence-0N.zip` -> resolve by sha256 (`lib.common.container_by_sha`). D6: two same-named downloads ->
  `delivery N: <zip>` refs. Member numbering shifts between pre-fetched contract and live attempt -- never hardcode.

## Pitfalls that cost time
- **Synthesis dispatch lost AGAIN (D15, D16, D17, D19)**: every day the single's `solve.py` answers the new field but the
  timed kit adds `metadata-day-NN-synthesis-sha256-order` -> `solver_incomplete` -> an offline generalize (~1 min per
  mode). D18 was clean only because the single worker pre-wired it. Right after single CORRECT: `grep -n synthesis
  solver/solve.py` must show a dispatch calling `lib.meta.synthesis.digest_order`, with the artifacts root set INSIDE
  the per-set worker (`_solve_pairs`; Mastery forks one process per set), plus identity for ANY member stem and every
  carry-over family. Start from the previous day's solver, not a fresh template.
- Id-slug parsing (D16, 1 wrong): ids repeat the fmt word (`d16-email-001-email-message-id`); a regex on the first
  `email-` yields `001-email-message-id` -> lookup miss -> `none`. Anchor `-\d+-<fmt>-(.+)$`. Never submit `none`
  without grepping the bytes for the field -- `none` means absent in the artifact, not "my parser returned None".
- Registry misses (D14 key one suffix short `lnk.target_path`; D16 fmt `eml` vs GM `email`; D17 `wav.*` vs `media.*`):
  `python3 -c "import lib.meta as m; print([k for k in m.known_fields() if k[0]=='<fmt>'])"` and grep
  `lib/meta/prebuilt/*.py` for the FIELD name; call the nearest extractor directly. D18-D20 HIT the registry. D20
  substring trap: `cpu_type_set` fell into macho's scalar `cpu_type` branch -> bare hex where `json` wants a list --
  check the SHAPE vs answer_format; `_set`/`_list`/`_names` = one entry per slice/member (wrap a thin value in `[...]`).
- Endianness (D19 pun): never `struct.unpack('<H')` an ELF/Mach-O field blindly -- EI_DATA (ELF @5) / the Mach-O magic
  byte order decide (`cffaedfe` = LE; fat headers are ALWAYS BE, their slices carry their own magic); ELF32 vs ELF64
  moves every offset after e_version. Fat: cputype is in BOTH fat_arch and the slice header -- they may disagree in a
  variant ("what truly supports"): the set field reads fat_arch; note the slice header if they differ.
- Video geometry has FOUR sources (stsd w/h, SPS crop = ffprobe width/height, tkhd display w/h, tkhd matrix rotation);
  D18 they agreed. If a variant's stsd and SPS disagree, trust the SPS-cropped size.
- Field suffix picks the spelling: `_u16_hex` = the raw struct value (D9: not `i386`/GOARCH; D19: not `x86-64`);
  `_codec_name` = the tool vocabulary (D17: `pcm_s16le`, not the raw format tag `1` nor mediainfo's `PCM`). NO suffix
  on a binary-header code (D20 `cpu_type_set`, 1 wrong + 5 s): still the raw struct hex (`0x0100000c`), not `arm64`.
  Only a field that SAYS `_name`/`_arch_names` gets a name.
- JSON list ORDER (D15, 1 wrong + ~26 s): "exact values and order" does not say WHICH order. File order was rejected
  for rels targets; sorted won. Decide per field (conventions above) before the first submit.
- A pre-fetched TT/Mastery `contract.json` is the 409 `start_required` body (questions, NO `answer_ids`); answer under
  the live `answer_ids`. Don't let the flavor widen the question: only the named field is graded.
- Container-of-containers: a naive `rfind(PK\x05\x06)` on the downloaded zip reads the OUTER EOCD, a name lookup on
  zip-of-zips returned `PK` as the "magic". Resolve the named member's bytes first (recurse), then parse.
- Name-list fields: emit CD bytes as-is for hostile names (`../`, `/abs`, `\`, dupes). Decoy names (`*-with-bom.txt`,
  `.exe` that is text, `.bin` that is PDF): bytes win every time.
- Timed windows are seconds; most of it is GM round-trips (D20 start 1.4-4.0 s + download 0-2 s + submit 2-2.3 s;
  solve ~1.6 s). Parse in memory, never shell out/extract to disk in-window; decompress each member once, cache by
  (set zip, member).
- Don't reshape a stored string (D13 braces). Hex width (D10): `"0x%x"` drops zeros; print `0x%0{2*size}x`; `_rva` =
  raw field. Require `PE\0\0` / `\x7fELF` / a Mach-O magic before any field of that format (else `none`).
- Tools installed: exiftool, poppler, qpdf, mutool, pdf-parser, pdfid, pngcheck, zsteg, steghide, binwalk, foremost,
  mediainfo, sqlite3, ImageMagick, readelf/objdump, olevba/oleid, olefile, pefile, pyelftools, LnkParse3, dnfile,
  mutagen (.venv); msitools under tools/msitools; ffmpeg 7.0.2 (no ffprobe) at
  `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2` (not on PATH). NOT installed: ffprobe, sox.
