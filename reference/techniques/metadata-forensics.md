# metadata-forensics — technique log (days 1-17; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every day = ONE evidence zip (plain Deflate, no password so far). Days 1-7: one tiny member and ONE structural fact.
  Day 8-9: the zip carries the whole cumulative kit and every mode asks every field (D9 13). Days 10-14 DE-escalated to
  one member + one field in every mode (TT 1, Mastery 2x1). **Day 15 split the modes**: single = 1 field (the new
  docx), but TT = the 12-member cumulative kit with 20 fields and Mastery = 5 kits x 20 = 100 -- incl. a brand-new
  cross-member "synthesis" question. **D16 and D17 repeated that split** (single 1 field; TT 21/22; Mastery 5x21/5x22,
  synthesis every time). Always pre-arm every earlier family AND the synthesis; the timed field set is not the single's.
- Member families so far: note/text -> jpg -> png -> pdf -> inner zip -> Go PE `.exe` (D9-11) -> .NET dll (D12) -> MSI
  (D13) -> LNK (D14) -> OOXML `.docx` (D15) -> RFC 5322 `.eml` (D16) -> RIFF/WAVE `.wav` audio (D17, first media
  family). Each new family arrives with its own `dNN` id prefix, and its fmt word is the GM's ABSTRACT namespace, not
  the container: `email` (not `eml`), `media` (not `wav`/`audio`) -- and the field uses ffprobe's vocabulary.
- A new `<fmt>.<field>` each day: identity (name/size/hashes) -> magic prefix -> `text.utf8_bom_present` ->
  `jpeg.sof_dimensions_pixels` -> `png.ihdr_dimensions_pixels` -> `pdf.header_version` -> `zip.eocd_total_entries` ->
  `zip.central_directory_member_names` -> `pe.coff_machine_u16_hex` -> `pe.address_of_entry_point_rva_hex` ->
  `pe.version_original_filename` -> `dotnet.mvid_guid` -> `msi.product_code_guid` -> `lnk.target_path_windows` ->
  `ooxml.external_relationship_targets` -> `email.message_id` -> `media.primary_audio_codec_name`. The question literally
  names the field (`Determine <fmt>.<field> for <member>`); ids read `dNN-<family>-NNN-<fmt>-<field>` (`.`/`_` -> `-`);
  `dNN` = the member family's first day, not today; `<family>` usually = `<fmt>` but NOT always (D17 `d17-audio-001-media-`).
- The prompt's flavor text describes decoys and promises extra findings ("find the collision", "the impossible
  destination", "the document reaching somewhere it should not") that were NEVER asked. The graded field is always the
  STRUCTURAL truth from header/record bytes; names/extensions/secondary metadata are the lie.
- Singles: D1-D9 first-submit CORRECT ~27-60 s; D10, D13, D15 lost ONE submit to a spelling/ordering convention
  (padding, braces, list order); D16 lost TWO (parser bug -> `none`, then stripped brackets); D17 first submit ~24 s.
  Every TT/Mastery since D4 CORRECT on its first GM submit -- but D15 TT, D16 and D17 TT+Mastery only after an offline
  generalize because the day's solver lacked the synthesis dispatch (see Pitfalls: it is now a 2-day repeat).
- The flavor promises MORE than the sample delivers (D9 "several architectures" -> one i386 PE). Pre-arm siblings
  (ELF/Mach-O/decoy -> `none`) without guessing spellings. Titles are puns, not format hints (D7 "Seven-Zip" was ZIP).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen"; resolve the named member through whatever wrapper arrives. Container
  NAMES drift too: D1-D14 `metadata-day-NN-evidence[-0N].zip`; D15-D17 TT `evidence.zip`, Mastery `evidence-01.zip` holding
  `evidence-01..05.zip`. Route by the ref's text before `->` and by sha256, never a hard-coded name.
- **Field-set size** -- grows AND shrinks per mode: D7 TT 11 / Mastery 22; D8-9 12-13 everywhere; D10-14 one; D15 single
  1 vs TT 20 vs Mastery 100; D16 single 1 vs TT 21 vs Mastery 105 (kit + `d16-email-*`); D17 1 / 22 / 110 (+ `d17-audio-*`). Families: the day's field + identity + carry-overs `d04-jpeg-*`, `d05-png-*`, `d06-pdf-*`,
  `d07-zip-*` (eocd + CD names), `d09-pe-*` (machine, entry RVA, version OriginalFilename), `d12-dotnet-*`, `d13-msi-*`,
  `d14-lnk-*`, `d15-ooxml-*`, `d16-email-*`, `d17-audio-*`. Dispatch on the answer-id SUFFIX; keep EVERY earlier family
  answerable (reference: `challenges/day17/metadata-hear-me-out/solver/solve.py` answers all 22 incl. synthesis).
- **fmt word vs registry key vs id family word** (D16, D17) -- the GM's `<fmt>` is an abstract namespace: D16
  `email.message_id` (prebuilt said `eml`); D17 `media.primary_audio_codec_name` with id `d17-audio-001-media-...`
  (family word `audio`, fmt `media`; prebuilt only had `wav.*` fmt-chunk fields). Field vocabulary = ffprobe
  (`primary_audio_` = first audio stream, `codec_name` = FFmpeg codec id). Rule: take `<fmt>.<field>` from the
  QUESTION text (or the slug after `-NNN-`), map fmt synonyms (`email`<->`eml`/`mime`; `media`<->`audio`/`wav`/`mp3`/
  `mp4`/...), route the extractor by the member's MAGIC, and fall back to the same field under any fmt.
- **Identity member roster** (D15 new; D16 Mastery added `evidence-note-filename`, `-size-bytes`, `roster-md5`) -- the kit holds THREE small text members (`evidence-note.txt` 33 B,
  `evidence-note-copy.txt` 33 B, `roster.csv` 29 B) and EACH identity question picks one at random per set:
  ids `<member-stem>-{filename,size-bytes,md5,sha1,sha256,magic-prefix-hex-16,text-utf8-bom-present}` (`roster-sha1`,
  `evidence-note-copy-filename`...). The filename question has artifact = the container only and asks "the exact
  filename of the roster" -> map the id stem to the member whose stem matches. Never assume `evidence-note-*`.
- **Synthesis / cross-member questions** (D15 new) -- id `metadata-day-NN-synthesis-<algo>-order`, kind `json`, norm
  `case_insensitive`: "Compute the full-file SHA-256 digest of each named file, then submit a compact JSON array of their
  filenames in ascending digest order. Files: [...]". The `artifact` names only ONE member; the real inputs are the
  `Files:` JSON list in the question text, all in the same container. Rule: regex `Files:\s*(\[.*?\])`, resolve each
  name under the ref's container, `hashlib.new(algo)` over the raw member bytes, sort by hex digest (descending only if
  the text says so), emit names. Expect siblings (md5/sha1 order, size order) -- parse the algo from the id/text.
  D16: id became `metadata-day-16-...` (TODAY's day, unlike `dNN` family ids), the list was 4 names incl. today's new
  member (`message-001.eml`) and set order re-rolls per Mastery set. D17: `["evidence-note.txt","panel-001.png",
  "managed-001.dll","audio-001.wav"]` -- shape so far = the note + 2 kit members (re-picked daily: jpg/exe/docx D15,
  png/dll D17) + TODAY's new member. `lib.meta.synthesis.digest_order(question, get_bytes, algo)` implements it --
  call it from every day's solver with get_bytes bound to the artifacts root INSIDE the per-set worker (Mastery forks
  one process per set: a root global set only in `main()` stays None; the D17 Mastery generalize had to set it there).
- **Decoys** -- renamed copies, misleading extensions, secondary metadata (EXIF, catalog /Version) that disagree with the
  header: always answer from the structural bytes of the member the question names.
- **Member values** -- re-roll per variant; never cache across sets. Seen: note case id (all days); D7 entry count
  2/3/4/5; jpg/png dimensions (D15 every set different, e.g. 423x1089, 1255x1059); D10 entry RVA; D11 PE architecture
  (386 0x014c / amd64 0x8664 / arm64 0xaa64, OriginalFilename `pe-base-<goarch>.exe` follows); D12 MVID; D15 synthesis
  order (driven by the re-rolled note/jpg hashes; D16-17 differs per set). Constant so far but don't rely on it: D13 ProductCode
  (identical in every mode -- "collision" by design), D14 lnk target, D15 docx targets, the kit's exe/dll/msi/lnk, D17
  audio codec (`pcm_s16le` -- 16-bit mono 16 kHz PCM WAV -- in single, TT and all 5 Mastery sets despite the
  "transcoded" flavor; expect other codecs/containers once the family deepens).
- **Answer kinds** -- `exact_text`, `integer`, `pattern` (hashes case-insensitive; `0x`-hex is `trim` only -> lowercase),
  `enum` (`accepted_values`), `json` ("compact valid JSON array with exact values and order"). Emit per
  `answer_format.kind`; read `syntax` for prefix/case. JSON ORDER is field-specific -- see conventions.
- **Question-text tags** -- D9 TT/Mastery appended ` [assigned-artifact-sha256:<64 hex>]` to the first question; D15
  timed questions are prefixed ``Inspect `<member>`. `` Strip both before reading names; route by id + `artifact`.
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
| `*-synthesis-<algo>-order` / "Files: [...]" in the question | parse the list from the question text, hash each member of the same container, sort by digest, compact JSON of names |
| GUID field (`*-guid`) | spelling follows the SOURCE: stored string (MSI) verbatim braces+uppercase; binary (.NET) -> lowercase, no braces |
| exe-extension decoy (`MZ` without `PE\0\0` at e_lfanew) | literal `none` if the syntax offers it; never fall back to a later `PE\0\0` hit |
| "impostor", "renamed", "disguise" | trust magic bytes at offset 0; a matching string deeper in the file is a decoy |
| answer_format kind `json` | `json.dumps(v, separators=(",",":"), ensure_ascii=False)`; decide ORDER per field (conventions) |
| Mastery `set1.`..`setN.` ids | resolve each set's container separately; see delivery layouts |

## Day by day
**Days 1-11** (one field each, first try ~25-75 s): D1 identity -> D2 `magic-prefix-hex-16` -> D3 BOM -> D4 JPEG SOFn
`<w>x<h>` -> D5 PNG IHDR -> D6 `pdf.header_version` `x.y` -> D7 `zip.eocd_total_entries` of the INNER zip -> D8 CD names
(compact JSON, CD order) -> D9-11 one Go PE: `coff_machine_u16_hex` `0x014c`, entry RVA `0x%08x` (unpadded REJECTED),
`version_original_filename` verbatim.

**Days 12-14** (one new member family each, 1 field everywhere, all timed first try): D12 `dotnet.mvid_guid` (#GUID
heap -> `uuid.UUID(bytes_le)` lowercase no braces, ~55 s); D13 `msi.product_code_guid` (Property ProductCode VERBATIM
with braces; brace-less REJECTED, ~76 s); D14 `lnk.target_path_windows` (LinkInfo LocalBasePath, ~40 s; prebuilt key was
one suffix short).

**Days 15-16** (single = 1 new-family field; TT/Mastery = cumulative kit + synthesis): D15 "A Word to the Wise"
`ooxml.external_relationship_targets` (`.docx` rels `TargetMode="External"` -> Targets SORTED; rels order REJECTED,
+50 s). D16 "Return to Sender" `email.message_id` (`message-001.eml` multipart; Message-ID VERBATIM with `<>`; lost 2
submits: own id regex hit the first `email-` -> `none`, then stripped brackets). Both: first `synthesis-sha256-order`
missing from the template -> `solver_incomplete` -> offline generalize -> CORRECT.

**Day 17 — Hear Me Out** (`media.primary_audio_codec_name`, kind `exact_text` "... use the literal none only when the
requested field is absent", norm `trim`, id `d17-audio-001-media-primary-audio-codec-name`). Prompt: "Voice notes have
been transcoded, renamed, and embedded in mail. Determine the actual codecs, connect equivalent recordings, and find
the stream that breaks the sender's story." (equivalence/odd-stream/mail-embedding flavor -- NOT asked; one WAV only).
- Artifact: 1.3 KB zip -> `audio-001.wav` (40 102 B): `RIFF`/`WAVE`, `fmt ` 16 B (tag 1 PCM, 1 ch, 16000 Hz, 32000 B/s,
  align 2, 16 bit), `LIST`/`INFO` with `INAM` = `Huntress audio evidence <12 hex>`, then `data`.
- Key insight: the field is ffprobe's `codec_name` of stream a:0, spelled FFmpeg-style: PCM + 16 bit + RIFF (LE) ->
  `pcm_s16le`. Not `PCM`/`WAVE_FORMAT_PCM`/`0x0001`/`wav`.
- Tools: `xxd -l 48 audio-001.wav` is enough; cross-check with the bundled `ffmpeg-linux-x86_64-v7.0.2 -hide_banner -i` (ffprobe names). Solver `_audio_codec` (magic-routed: RIFF/RIFX/RF64, AIFF/AIFC, fLaC, Ogg
  Opus/Vorbis/FLAC/Speex, AMR, `.snd`, MP4 `stsd`, Matroska CodecID, MPEG frame sync incl. ADTS). No ffprobe on PATH;
  prebuilt `wav.py` then exposed only `wav.fmt_*` raw fields (no `media` fmt) -- the D17-night prebuild added fmt
  `media` (aliases `audio`, `av`) with codec/stream/format/tag/odd-stream fields, `email.attachment_audio_*`, and
  `synthesis.*equivalence*`/`odd_one_out*` groupings.
- Single: answer-first worker, first submit CORRECT at ~24 s. TT 22 / Mastery 5x22 = 110: all non-synthesis fields in
  window (TT 2.6 s, Mastery 2.7 s in-window); `metadata-day-17-synthesis-sha256-order` missing AGAIN -> generalize ported
  the D16 dispatch (TT CORRECT +55 s after start), Mastery also needed the artifacts-root global set inside the per-set
  `_solve_pairs` worker -> CORRECT 110/110.

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes: base-10 integer, no units. Hashes: hex, case ignored.
- Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`). Booleans: enum `true` / `false`.
- Pixel dimensions (JPEG SOF, PNG IHDR): `<width>x<height>`, lowercase `x`, no spaces.
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
  each new family so far arrived under an ABSTRACT fmt word the prebuild hadn't used -- expect `image`/`video`/`archive`/`disk`):
  `python3 -c "import lib.meta as m; print([k for k in m.known_fields() if k[0]=='<fmt>'])"` and grep
  `lib/meta/prebuilt/*.py` for the FIELD name; call the nearest extractor directly before writing one.
- The synthesis handler is not inherited (D16 AND D17 lost it -> `solver_incomplete` + offline generalize in BOTH
  timed modes, two days running). Before the timed run: `grep -n synthesis solver/solve.py` must show a dispatch that
  calls `lib.meta.synthesis.digest_order`, AND the artifacts root it reads siblings from must be set inside the per-set
  worker (`_solve_pairs`), not only in `main()` -- Mastery forks one process per set. Run the D16/D17 compound cases.
- Field suffix picks the spelling: `_u16_hex` = the raw struct value (D9: not `i386`/GOARCH); `_codec_name` = the
  tool vocabulary (D17: `pcm_s16le`, not the raw format tag `1` nor mediainfo's `PCM`).
- JSON list ORDER (D15, 1 wrong + ~26 s): "exact values and order" does not say WHICH order. File order was rejected
  for rels targets; sorted won. Decide per field (conventions above) before the first submit.
- Timed field set != single field set (D15+): keep the cumulative solver (identity for ANY member stem, every
  carry-over family, synthesis) in place before the timed run.
- Contract question text can be stale vs `answer_ids` (D2 TT): answer under `answer_ids`, locate the member that exists.
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
- Pre-fetched TT/Mastery `contract.json` is the HTTP 409 `start_required` body: `questions` but NO `answer_ids`.
- Harness: `hctf start` on a solved challenge overwrote `single_solve/start.json` (D2) -- restore from `log.jsonl`.
- Tools installed: exiftool, poppler, qpdf, mutool, pdf-parser, pdfid, pngcheck, zsteg, steghide, binwalk, foremost,
  mediainfo, sqlite3, ImageMagick, olevba/oleid, olefile, pefile, LnkParse3, dnfile, mutagen (.venv); msitools under
  tools/msitools; ffmpeg 7.0.2 (no ffprobe) at `tools/imageio_ffmpeg_pkg/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2` (not on PATH). NOT installed: ffprobe, sox.
