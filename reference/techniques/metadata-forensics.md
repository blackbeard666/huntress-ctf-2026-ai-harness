# metadata-forensics — technique log (days 1-18; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every day = ONE evidence zip (plain Deflate, no password so far). D1-7: one tiny member, ONE structural fact. D8-9:
  the cumulative kit, every field in every mode. D10-14: one member + one field everywhere. **D15+ split the modes**:
  single = 1 field (the new member), TT = cumulative kit (D15 20 -> D18 23 fields, +1 per day = the day's new member),
  Mastery = 5 kits x the TT set, incl. a cross-member "synthesis" question every day. Pre-arm EVERY earlier family AND
  the synthesis before the timed run; the timed field set is not the single's.
- Member families: note/text -> jpg -> png -> pdf -> inner zip -> Go PE (D9-11) -> .NET dll (D12) -> MSI (D13) -> LNK
  (D14) -> OOXML `.docx` (D15) -> `.eml` (D16) -> RIFF/WAVE audio (D17) -> MP4 h264+aac video (D18). The fmt word is
  the GM's ABSTRACT namespace, not the container: `email` (not `eml`), `media` for BOTH audio (D17) and video (D18) --
  and media fields use ffprobe's vocabulary.
- A new `<fmt>.<field>` each day: identity -> magic prefix -> `text.utf8_bom_present` -> `jpeg.sof_dimensions_pixels` ->
  `png.ihdr_dimensions_pixels` -> `pdf.header_version` -> `zip.eocd_total_entries` -> `zip.central_directory_member_names`
  -> `pe.coff_machine_u16_hex` -> `pe.address_of_entry_point_rva_hex` -> `pe.version_original_filename` ->
  `dotnet.mvid_guid` -> `msi.product_code_guid` -> `lnk.target_path_windows` -> `ooxml.external_relationship_targets` ->
  `email.message_id` -> `media.primary_audio_codec_name` -> `media.primary_video_dimensions`. The question names the
  field (`Determine <fmt>.<field> for <member>`); ids `dNN-<family>-NNN-<fmt>-<field>` (`.`/`_` -> `-`); `dNN` = the
  family's first day; `<family>` != `<fmt>` for media (`d17-audio-001-media-`, `d18-video-001-media-`).
- The flavor text promises extra findings ("the collision", "the impossible destination", "equivalent recordings",
  "crops, the recording that could not have come from the claimed device") that were NEVER asked; the sample usually
  delivers less (D9 "several architectures" -> one i386 PE). The graded field is the STRUCTURAL truth from header bytes;
  names/extensions/secondary metadata are the lie. Pre-arm siblings without guessing spellings. Titles are puns.
- Singles: D1-9 first-submit CORRECT ~27-60 s; D10, D13, D15 lost ONE submit to a convention (padding, braces, list
  order); D16 lost TWO (parser -> `none`, stripped brackets); D17 ~24 s; D18 ~5 s (race probe answered from the prebuilt
  `lib.meta` registry before any LLM work). TT/Mastery: first GM submit CORRECT since D4, but D15-D17 only after an
  offline generalize (synthesis missing); D18 in-window first try (single worker pre-wired the synthesis).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen". Container NAMES drift: D1-14 `metadata-day-NN-evidence[-0N].zip`;
  D15-18 TT `evidence.zip`, Mastery `evidence-01.zip` holding `evidence-01..05.zip`. Route by the ref's text before
  `->` and by sha256, never a hard-coded name.
- **Field-set size** -- per mode: D7 TT 11 / Mastery 22; D8-9 12-13 everywhere; D10-14 one; D15 1/20/100; D16 1/21/105;
  D17 1/22/110; D18 1/23/115. Families: identity + `d04-jpeg-*`, `d05-png-*`, `d06-pdf-*`, `d07-zip-*` (eocd + CD
  names), `d09-pe-*` (machine, entry RVA, OriginalFilename), `d12-dotnet-*`, `d13-msi-*`, `d14-lnk-*`, `d15-ooxml-*`,
  `d16-email-*`, `d17-audio-*`, `d18-video-*` + synthesis. Dispatch on the answer-id SUFFIX (reference solver answering
  all 23: `challenges/day18/metadata-frame-of-reference/solver/solve.py`).
- **fmt word vs registry key vs id family word** (D16-D18) -- D16 `email.*` (prebuilt said `eml`); D17
  `media.primary_audio_codec_name` id `d17-audio-...`; D18 `media.primary_video_dimensions` id `d18-video-...` (one
  `media` namespace spans two families). Vocabulary = ffprobe (`primary_<type>_` = first stream of that type in
  container order, `codec_name` = FFmpeg id, `dimensions` = `<width>x<height>`). Rule: take `<fmt>.<field>` from the
  QUESTION text (or the slug after `-NNN-`), map fmt synonyms (`email`<->`eml`/`mime`; `media`<->`audio`/`video`/`av`/
  `wav`/`mp4`/...), route the extractor by the member's MAGIC, fall back to the same field under any fmt.
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
  worker. Shape: note + 2 re-picked kit members (jpg/exe/docx D15, png/dll D17, png/msi D18) + TODAY's member; order
  re-rolls per set. Only sha256 seen so far -- expect md5/sha1/size/time siblings.
- **Decoys** -- renamed copies, misleading extensions, secondary metadata (EXIF, catalog /Version) that disagree with the
  header: answer from the structural bytes of the member the question names.
- **Member values** -- re-roll per variant; never cache across sets. Seen re-rolled: note case id; D7 entry count
  2-5; jpg/png dims per set (423x1089, 1255x1059); D10 entry RVA; D11 PE arch (0x014c/0x8664/0xaa64, OriginalFilename
  `pe-base-<goarch>.exe` follows); D12 MVID; synthesis order. Constant so far (don't rely on it): D13 ProductCode,
  D14 lnk target, D15 docx targets, kit exe/dll/msi/lnk, D17 codec `pcm_s16le`, D18 video `320x180` (h264 High 10 fps;
  stsd = tkhd = SPS, identity matrix, pasp 1:1 in every set) -- the flavor's transcodes/crops/rotations are still due.
- **Answer kinds** -- `exact_text`, `integer`, `pattern` (hashes case-insensitive; `0x`-hex is `trim` only -> lowercase),
  `enum` (`accepted_values`), `json` ("compact valid JSON array with exact values and order"). Emit per kind; read
  `syntax` for prefix/case. JSON ORDER is field-specific -- see conventions.
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
| `elf.*` / `macho.*` (promised, not yet asked) | ELF `\x7fELF`, EI_DATA @5, e_machine u16 @18. Mach-O `feedface`/`feedfacf` cputype @4; fat `cafebabe` BE nfat_arch @4 |
| `dotnet.*` / Mono assembly | data dir 14 -> CLI header -> `BSJB` -> `#~` (HeapSizes @+6, Valid @+8, rows @+24) -> Module row 0 Mvid (1-based #GUID idx) -> `uuid.UUID(bytes_le=..)`. `lib/meta/dotnet.py` |
| `msi.*` / `.msi` (OLE `d0 cf 11 e0`) | fast: `strings -n 6 x.msi \| grep -aoE 'ProductCode\{[0-9A-F-]{36}\}'`; exact: CFB streams -> `!_StringPool`/`!_StringData` -> `!Property` (column-major). `olefile` in venv; `day13/.../solve.py msi_property` |
| `lnk.*` / `.lnk` (`4c 00 00 00` + CLSID 00021401) | LinkFlags @0x14 (0x1 IDList, 0x2 LinkInfo, 0x80 Unicode); target = LinkInfo LocalBasePath (+CommonPathSuffix) verbatim, else IDList. `lib.meta.lnk:target_path` |
| `ooxml.*` / `.docx/.xlsx/.pptx` (`PK` + `[Content_Types].xml`) | it's a zip of XML parts. Relationships live in EVERY `*.rels` part (`_rels/.rels`, `word/_rels/document.xml.rels`, header/footer/settings rels). External = `TargetMode="External"` (case-insensitive; absent = Internal). `unzip -p f.docx '*.rels' \| grep -o 'Target="[^"]*" TargetMode="External"'`; solver: `zipfile` + ElementTree over every `.rels`, local-name `Relationship`. Core props (`docProps/core.xml`) prebuilt in `lib/meta/prebuilt/ooxml.py`; external rels NOT prebuilt as of D15 |
| `email.*` / `.eml` (text `From:`/`Message-ID:`/`MIME-Version:`, CRLF) | `grep -ai '^message-id' f.eml` to see the stored value; solver: `lib.meta.prebuilt.eml.eml_value(data, {"field": f})` (stdlib `email` parser, unfolded raw header). Header values VERBATIM (Message-ID keeps `<...>`). Threading cues ("replies, forwards, duplicates") = `In-Reply-To`/`References`/`Message-ID` |
| `media.*` / audio (`RIFF..WAVE`, `ID3`/`ff fb`, `OggS`, `fLaC`, `ftyp`, `1a 45 df a3`, `FORM..AIFF`, `#!AMR`) | route by MAGIC (names/extensions lie: "renamed, transcoded"). WAV: walk RIFF chunks from @12 to `fmt ` -> wFormatTag u16 @+8, bits u16 @+22 (0xFFFE -> SubFormat GUID's first u16 @+32); map to FFmpeg names (Conventions). ground truth = FFmpeg vocabulary: no ffprobe, but `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2 -hide_banner -i f` prints `Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 16000 Hz, mono, s16` + format tags (worker-side; `mediainfo` says `PCM` = wrong vocabulary). In-window: `lib.meta` fmt `media`/`audio`/`av` (~500 prebuilt fields since D17 night). LIST/INFO `INAM` carried `Huntress audio evidence <12 hex>` (correlation id candidate) |
| `media.*video*` / MP4-MOV (`....ftyp`), MKV/WebM (`1a 45 df a3`), AVI (`RIFF..AVI `) | box walk `moov` -> `trak` whose `mdia/hdlr` type = `vide` (first one = `primary_video_`) -> `stsd` sample entry: w,h u16 BE @entry+32 (`avc1`/`hvc1`/`vp09`/`av01`); also read tkhd w/h (16.16 @end) + matrix (rotation), `pasp` (SAR), `clap`, avcC SPS crop -- in a variant these may DISAGREE (see Pitfalls). In-window: `lib.meta` fmt `media`/`video`/`av` (`prebuilt/media_video.py`, ~100 video fields). Truth: bundled `ffmpeg -hide_banner -i f` -> `Video: h264 (High) (avc1 / 0x31637661), yuv420p(progressive), 320x180 [SAR 1:1 DAR 16:9], 10 fps` |
| `*-synthesis-<algo>-order` / "Files: [...]" in the question | parse the list from the question text, hash each member of the same container, sort by digest, compact JSON of names |
| GUID field (`*-guid`) | spelling follows the SOURCE: stored string (MSI) verbatim braces+uppercase; binary (.NET) -> lowercase, no braces |
| exe-extension decoy (`MZ` without `PE\0\0` at e_lfanew) | literal `none` if the syntax offers it; never fall back to a later `PE\0\0` hit |
| "impostor", "renamed", "disguise" | trust magic bytes at offset 0; a matching string deeper in the file is a decoy |
| answer_format kind `json` | `json.dumps(v, separators=(",",":"), ensure_ascii=False)`; decide ORDER per field (conventions) |
| Mastery `set1.`..`setN.` ids | resolve each set's container separately; see delivery layouts |

## Day by day
**Days 1-14** (one field each, all timed first try): D1 identity -> D2 `magic-prefix-hex-16` -> D3 BOM -> D4 JPEG SOFn
`<w>x<h>` -> D5 PNG IHDR -> D6 `pdf.header_version` `x.y` -> D7 `zip.eocd_total_entries` of the INNER zip -> D8 CD names
(compact JSON, CD order) -> D9-11 one Go PE: `coff_machine_u16_hex` `0x014c`, entry RVA `0x%08x` (unpadded REJECTED),
`version_original_filename` verbatim -> D12 `dotnet.mvid_guid` (`uuid.UUID(bytes_le)` lowercase, no braces) -> D13
`msi.product_code_guid` (stored WITH braces; brace-less REJECTED) -> D14 `lnk.target_path_windows` (LinkInfo path).

**Days 15-17** (single = 1 new-family field; TT/Mastery = cumulative kit + synthesis): D15 "A Word to the Wise"
`ooxml.external_relationship_targets` (`.docx` rels `TargetMode="External"` -> Targets SORTED; rels order REJECTED,
+50 s). D16 "Return to Sender" `email.message_id` (`message-001.eml`; VERBATIM with `<>`; lost 2 submits: id regex hit
the first `email-` -> `none`, then stripped brackets). D17 "Hear Me Out" `media.primary_audio_codec_name` (`audio-001.wav`
RIFF PCM 16-bit mono 16 kHz + LIST/INFO `INAM` -> ffprobe name `pcm_s16le`, not `PCM`/`0x0001`; ~24 s; flavor
"transcoded, renamed, embedded in mail, equivalent recordings" never asked). All three: `synthesis-sha256-order`
missing from the day's template -> `solver_incomplete` -> offline generalize -> CORRECT (D17 Mastery also needed the
artifacts root set inside the per-set worker).

**Day 18 — Frame of Reference** (`media.primary_video_dimensions`, kind `exact_text` "... use the literal none only when
the requested field is absent", norm `trim`, id `d18-video-001-media-primary-video-dimensions`). Prompt: "Clips,
previews, and screen recordings have been mixed together. Use stream geometry to identify originals, crops, and the
recording that could not have come from the claimed device." (originals/crops/impossible-device flavor -- NOT asked;
one MP4 only).
- Artifact: 18.7 KB zip -> `video-001.mp4` (19 775 B, `ftyp isom` minor 512, brands `isomiso2avc1mp41`, Lavf layout
  `moov` before `mdat`): trak 1 `vide` h264 High `avc1` 320x180 (`avcC`+`pasp` 1:1+`btrt`, 10 fps, 5 frames, encoder
  `Lavc libx264`), trak 2 `soun` aac LC 44.1 kHz stereo; `udta/meta` mdta `title` = `Huntress MP4 evidence <12 HEX>`.
  stsd w/h = tkhd 320.0/180.0 = SPS; tkhd matrix identity (rotation 0).
- Key insight: it's ffprobe `width`x`height` of stream v:0 spelled like D4/D5 (`<w>x<h>`, lowercase `x`). The audio
  trak in the same file must not be picked; the first `vide` handler wins.
- Tools: none needed by hand -- the race probe answered from the prebuilt `lib.meta` `media_video.py` (D17-night
  `media-video-streams` gap). Manual check: box walk to `stsd` (entry+32) or the bundled ffmpeg `-i` line above.
- Single CORRECT on the first submit ~5 s after start (submit RTT 1.2 s). The single worker then PRE-WIRED the
  `synthesis-<algo>-order` dispatch (+ artifacts-root global set in `_solve_pairs`) before the timed runs -> TT 23
  (in-window 3.5 s) and Mastery 5x23 = 115 (in-window 6.8 s) CORRECT first try, no generalize -- first clean timed day
  since D14.

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes: base-10 integer, no units. Hashes: hex, case ignored.
- Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`). Booleans: enum `true` / `false`.
- Pixel dimensions (JPEG SOF, PNG IHDR, video `media.primary_video_dimensions` D18): `<width>x<height>`, lowercase
  `x`, no spaces. Video = ffprobe width/height of v:0 (coded size, NOT rotated, not the tkhd display size).
- PDF header version: bare `x.y`; absent -> literal `none` (wording; `none` not yet GM-confirmed). Counts: plain integer.
- JSON lists -- compact, double quotes, no spaces; ORDER depends on the field:
  - `zip.central_directory_member_names`: full stored paths in CD order (`["room-01/item-1.txt","room-02/item-1.txt"]`).
  - `ooxml.external_relationship_targets`: Target strings SORTED ascending (D15 all modes); rels-file order REJECTED.
  - `*-synthesis-<algo>-order`: member names ordered by hex digest ascending (D15 TT/Mastery; norm `case_insensitive`).
  Heuristic: a list read off one on-disk structure that the field name calls "names in the directory" keeps disk
  order; a set gathered across parts ("targets", "dependencies") is sorted. If an order is rejected, try the other.
- Header integers as hex (`*_hex`): `0x` + lowercase hex ZERO-PADDED to the struct field's width: u16 Machine
  `0x014c`, u32 AddressOfEntryPoint `0x00065bd0`. Width from the STRUCT, not the id. (Magic-prefix hex has NO `0x`;
  the binary lane's machine wants `i386` and accepted unpadded entry points -- different generator.)
- GUIDs: .NET MVID `Guid.ToString()` lowercase no braces (D12); MSI ProductCode the stored string uppercase WITH braces
  (D13). Spelling follows the source, not answer_format.
- Windows paths (`lnk.target_path_windows`): stored LinkInfo path verbatim (backslashes, case, drive letter, no quotes).
- Version-resource strings (`pe.version_<field>`): StringFileInfo value verbatim incl. extension.
- URLs (`ooxml` Targets): the attribute value verbatim -- scheme, host, path as stored; no trailing-slash or case fixups.
- E-mail headers (`email.<field>`): header value as stored after RFC 5322 unfolding; Message-ID WITH `<>` (D16).
  Unverified siblings: address fields likely bare `addr-spec` when the field says `_address`, else the full header.
- Media codec names (`media.*codec_name`, D17): FFmpeg/ffprobe `codec_name`, lowercase: WAV tag 1 -> `pcm_u8` (8-bit) /
  `pcm_s16le` / `pcm_s24le` / `pcm_s32le` (RIFX -> `..be`); tag 3 -> `pcm_f32le`/`pcm_f64le`; 6 `pcm_alaw`; 7
  `pcm_mulaw`; 2 `adpcm_ms`; 0x11 `adpcm_ima_wav`; 0x55 `mp3`; 0xFFFE -> SubFormat GUID first u16. Others: `mp3`, `aac`,
  `opus`, `vorbis`, `flac`, `alac`, `amr_nb`/`amr_wb`, `ac3`. Only `pcm_s16le` is GM-verified. `primary_audio_` = first
  audio stream in container order (ffprobe `a:0`).
- Rejected spellings: `0x65bd0` (D10, unpadded); brace-less MSI GUID (D13); rels-file-order target list (D15);
  bracket-less Message-ID (D16). Pattern: delimiters that are part of the stored value (`{}`, `<>`) stay.
- Inference: the field id IS the spec name (`sof_` = SOF header, `eocd_total_entries` = the EOCD's own claim,
  `external_relationship_targets` = rels `Target` where `TargetMode=External`) -- read it literally to pick the
  structure. A claimed count is NOT a CD walk; CD names are NOT local-header names; `_uNN_hex` fixes read+print width.

## Delivery layouts seen (resolve these before parsing)
- Single / TT: one zip; members named in `artifact` after `->` (filename questions: artifact = the zip only).
- Mastery zip-of-zips (days 1,2,4,5,7,8,10,11,14,15): ONE download (`...-evidence-01.zip`; D15 `evidence-01.zip`)
  holding `-01.zip`..`-0N.zip`, each holding its set's member(s) (D7 three levels; D8/D15 five full kits, D15 ~606 KB
  each). Refs `<set zip> -> <member>`; every set reuses member names -> resolve by (set zip, member).
- Mastery day 9: download named `<challenge-id>-mastery.zip` while refs say `metadata-day-09-evidence-0N.zip` ->
  resolve the bundle by sha256 (`lib.common.container_by_sha`), not its filename.
- Mastery day 6: two downloads with identical filenames -> `delivery 1: <zip>` / `delivery 2: <zip>` refs.
- Member numbering shifts between pre-fetched contract and live attempt (003/004 vs 006/007) -- never hardcode names.

## Pitfalls that cost time
- Id-slug parsing (D16, 1 wrong): ids repeat the fmt word (`d16-email-001-email-message-id`); a regex on the first
  `email-` yields `001-email-message-id` -> lookup miss -> `none`. Anchor `-\d+-<fmt>-(.+)$`. Never submit `none`
  without grepping the bytes for the field -- `none` means absent in the artifact, not "my parser returned None".
- Registry misses (D14 key one suffix short `lnk.target_path`; D16 fmt `eml` vs GM `email`; D17 `wav.*` vs `media.*`;
  new families arrive under ABSTRACT fmt words -- D18 reused `media` for video and the prebuilt registry HIT; expect
  `image`/`archive`/`disk`/`log` next):
  `python3 -c "import lib.meta as m; print([k for k in m.known_fields() if k[0]=='<fmt>'])"` and grep
  `lib/meta/prebuilt/*.py` for the FIELD name; call the nearest extractor directly before writing one.
- Timed field set != single field set, and the synthesis handler is NOT inherited (D15-D17 lost it ->
  `solver_incomplete` + offline generalize; D18 the single worker pre-wired it right after CORRECT -> both timed modes
  first try -- keep doing that): `grep -n synthesis solver/solve.py` must show a dispatch calling
  `lib.meta.synthesis.digest_order`, with the artifacts root set INSIDE the per-set worker (`_solve_pairs`; Mastery
  forks one process per set), plus identity for ANY member stem and every carry-over family.
- Video geometry has FOUR sources (D18 they agreed; "crops / impossible device" flavor says variants won't): stsd
  sample-entry w/h, codec SPS (h264 frame_cropping -> ffprobe `width`/`height`; MB-aligned size = `coded_width`),
  tkhd 16.16 display w/h (post-SAR/clap), tkhd matrix rotation (ffprobe keeps coded dims; `rotation` = -90 for
  portrait phones). `primary_video_dimensions` = ffprobe width x height; prebuilt `media_video.py` reads stsd (+SPS
  only for pix_fmt/profile) -- if a variant's stsd and SPS disagree, trust the SPS-cropped size and say so in NOTES.
- Field suffix picks the spelling: `_u16_hex` = the raw struct value (D9: not `i386`/GOARCH); `_codec_name` = the
  tool vocabulary (D17: `pcm_s16le`, not the raw format tag `1` nor mediainfo's `PCM`).
- JSON list ORDER (D15, 1 wrong + ~26 s): "exact values and order" does not say WHICH order. File order was rejected
  for rels targets; sorted won. Decide per field (conventions above) before the first submit.
- Contract question text can be stale vs `answer_ids` (D2 TT); a pre-fetched TT/Mastery `contract.json` is the 409
  `start_required` body (questions, NO `answer_ids`). Answer under the live `answer_ids`.
- Don't let the flavor text widen the question: only the named field is graded; extra checks are diagnostics.
- Container-of-containers: a naive `rfind(PK\x05\x06)` on the downloaded zip reads the OUTER EOCD, a name lookup on
  zip-of-zips returned `PK` as the "magic". Resolve the named member's bytes first (recurse), then parse.
- Name-list fields: emit CD bytes as-is for hostile names (`../`, `/abs`, `\`, dupes). Decoy names (`*-with-bom.txt`,
  `.exe` that is text, `.bin` that is PDF): bytes win every time.
- Timed windows are seconds; most of it is GM round-trips (D15 start 1.0 s + submit 1.1 s). Parse in memory, never
  shell out/extract to disk in-window; decompress each member once and cache by (set zip, member) (1.2 MB exe x5).
- Fresh member family = copy the previous day's solver first (it answers every earlier family), then add only the new
  handler -- D8 27 s / D9 47 s that way; re-typing older branches cost D12 ~50 s.
- Normalizing a stored value (D13): don't strip braces/reshape a stored string because answer_format sounds generic.
- Hex width (D10): `"0x%x"` drops leading zeros; print `0x%0{2*size}x`. `_rva` = raw field, never ImageBase + it.
  Require `PE\0\0` at e_lfanew before any PE field.
- Harness: `hctf start` on a solved challenge overwrote `single_solve/start.json` (D2) -- restore from `log.jsonl`.
- Tools installed: exiftool, poppler, qpdf, mutool, pdf-parser, pdfid, pngcheck, zsteg, steghide, binwalk, foremost,
  mediainfo, sqlite3, ImageMagick, olevba/oleid, olefile, pefile, LnkParse3, dnfile, mutagen (.venv); msitools under
  tools/msitools; ffmpeg 7.0.2 (no ffprobe) at `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2` (not on PATH). NOT installed: ffprobe, sox.
