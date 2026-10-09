# metadata-forensics — technique log (days 1-9; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every day = ONE evidence zip (`metadata-day-NN-evidence.zip`, plain Deflate, no password so far). Days 1-7: one tiny
  member (33 B - 3 KB) and ONE structural fact. Day 8+: the zip carries the whole cumulative kit (note + jpg + png + pdf +
  inner zip [+ D9 a 1.26 MB PE `.exe`]) and even the SINGLE contract asks every field (D8 12, D9 13 = identity + every
  earlier day's field + the new one). The member can itself be a container (D7/8: an inner ZIP whose own EOCD / CD is
  the asked field). Each day adds ONE member + ONE field; the previous kit members are byte-identical except the case id.
- Day 9 crossed into EXECUTABLE headers (`pe.coff_machine_u16_hex`): the metadata lane now parses binaries too, but only
  the raw header field -- answer the u16 as hex, not the binary lane's machine word (`i386`).
- A new `<fmt>.<field>` family each day: identity (name/size/hashes) -> magic prefix -> `text.utf8_bom_present` ->
  `jpeg.sof_dimensions_pixels` -> `png.ihdr_dimensions_pixels` -> `pdf.header_version` -> `zip.eocd_total_entries` ->
  `zip.central_directory_member_names` -> `pe.coff_machine_u16_hex`. Since Day 3 the question literally names the field
  (`Determine <fmt>.<field> for <member>`); answer ids read `dNN-<fmt>-NNN-<fmt>-<field>` (`.`/`_` -> `-`). NOTE the
  `dNN` is the drop/member family, not the day the field appeared: Day 8's new field came as `d07-zip-001-zip-central-
  directory-member-names`; Day 9's as `d09-pe-001-pe-coff-machine-u16-hex` (new member family -> new `dNN`).
- The prompt's flavor text describes decoys (impostors, renamed copies, "-with-bom" names, EXIF/presentation lies, chunk
  "passengers", catalog /Version overrides, "impossible provenance" names). The asked field so far was always the
  STRUCTURAL truth from the header/record bytes; names/extensions/secondary metadata are the lie. All 9 single solves were
  first-submit CORRECT in ~27-60 s; every TT/Mastery since Homebase (D4+) CORRECT first try.
- The flavor promises MORE than the sample delivers (D9: "executables for several architectures, plus decoys wearing
  executable extensions" -> one honest i386 PE, no ELF/Mach-O/decoy in any mode). Expect the promised cases to arrive
  later as mutations; pre-arm the sibling parsers (ELF/Mach-O/decoy -> `none`) without guessing their spellings.
- Titles are puns, not format hints: Day 7 "Seven-Zip, No Relation" was plain ZIP (PKWARE), no .7z anywhere.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen" below; resolve the named member through whatever wrapper arrives.
- **Decoys** -- renamed copies, misleading extensions/names, secondary metadata (EXIF, catalog /Version) that disagree
  with the header: always answer from the structural header bytes of the member the question names.
- **Member and values** -- names, sizes, dimensions and counts re-roll per variant; nothing about the sample is
  constant (Day 7 entry count went 2/3/4/5 with drop number 001-004; member names `room-NN/item-K.txt`). Day 8 re-rolled
  ONLY the note's case id (`Case <hex> evidence note.`, 33 B) -> md5/sha1/sha256/magic differ per set; jpg 257x146, png
  269x153, pdf 1.4, eocd 2, CD names identical across single/TT/5 Mastery sets. D9 same, plus the PE: Machine 0x014c in
  all 7 copies but the exe's sha256 differs per set (re-built per variant). Never cache a value across sets anyway.
- **ESCALATED field set** -- the contract grows over time: D7 TT/Mastery went 1 -> 11 fields (Mastery 22); D8 started at
  12 already in single (TT 12, Mastery 5 sets x 12 = 60); D9 13 (TT 13, Mastery 5 x 13 = 65). Families: the day's field +
  `evidence-note-{filename,size-bytes,md5,sha1,sha256,magic-prefix-hex-16,text-utf8-bom-present}` + carry-overs
  `d04-jpeg-*-sof-dimensions-pixels`, `d05-png-*-ihdr-dimensions-pixels`, `d06-pdf-*-header-version`, `d07-zip-*-eocd-
  total-entries`, `d07-zip-*-central-directory-member-names`, `d09-pe-*-pe-coff-machine-u16-hex`. Dispatch on the
  answer-id SUFFIX and keep EVERY earlier family answerable (reference: `challenges/day09/metadata-built-different/
  solver/solve.py` answers all 13 + a pre-armed `elf-e-machine-u16-hex` branch).
- **Answer kinds** -- `exact_text`, `integer`, `pattern` (hashes, case-insensitive; D9 also `0x`-hex with `trim` only,
  so case MATTERS -> lowercase), `enum` (`accepted_values`), and since D8 `json` ("compact valid JSON array with exact
  values and order"). Emit per `answer_format.kind`; read `syntax` for prefix/case (`0x` yes for u16_hex, no for magic).
- **Question-text tags** (D9 TT/Mastery, new): the first question gets ` [assigned-artifact-sha256:<64 hex>]` appended
  (Mastery: the bundle's sha, same for every set). Strip `\s*\[[^\]]*\]$` before reading a member name from question
  text; route by `answer_id` + `artifact` instead (the D9 solver was unaffected for that reason).
- **Nesting depth** -- the asked file may sit 2-3 zips deep (Mastery D7: outer -> `...-evidence-0N.zip` ->
  `evidence-drop-00N.zip`); resolve by the name after `->`, never answer from an enclosing zip.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `<zip> -> <member>` in `questions[].artifact` | `7z l -slt <zip>` then `7z x -o work/ <zip>`; (or python `zipfile` read of the member) |
| filename / size / md5 / sha1 / sha256 | `stat -c %s`, `md5sum sha1sum sha256sum` on the extracted member (bytes, not the zip entry name) |
| "first sixteen bytes", "magic", "extension claims" | `xxd -p -l 16 <member>` (lowercase, no spaces); `file -k` only for orientation |
| `text.*_bom_present` | `xxd -l 4`: UTF-8 BOM = `ef bb bf` (UTF-16LE `ff fe`, BE `fe ff`, UTF-32LE `ff fe 00 00`) -> `true`/`false` |
| `jpeg.*dimensions*` / SOF | walk JPEG segments from `ffd8` by length to SOFn (`ffc0..ffcf` minus c4/c8/cc): P, Y=height, X=width. `exiftool -ImageSize` cross-check only |
| `png.ihdr_*` / "walk their chunks" | `xxd -s 16 -l 8` = IHDR width,height (BE u32). Chunk walk = len/type/data/CRC loop (`lib.stego.png_chunks`) |
| `zip.eocd_*` / "count what the archives claim" | of the NAMED inner zip (not the evidence zip): last `PK\x05\x06` whose comment len reaches EOF; u16 @+8 disk entries, @+10 total, u32 @+12 cd size, @+16 cd offset, u16 @+20 comment len. `0xFFFF` -> ZIP64 locator `PK\x06\x07` (EOCD-20) -> `PK\x06\x06` u64 @+32. Cross-check: count `PK\x01\x02` walking from cd offset, `PK\x03\x04` |
| `zip.central_directory_*` / "inventory every stored path, preserve directory context" | walk `PK\x01\x02` from EOCD cd-offset (fallback `EOCD - cd_size` if data prepended): name len u16 @+28, extra @+30, comment @+32, name at +46; next = +46+n+e+c. Raw stored path, CD order, no basename/dedupe/sort; decode UTF-8 (flag bit 11 `0x800`, else try UTF-8 then cp437). `7z l -slt` / `zipinfo -1` as cross-check |
| `pdf.header_version` / "declared versions" | `head -c 16 <f> | xxd` -> `%PDF-x.y` at offset 0; `grep -a -o '/Version[^/>]*'` only as a diagnostic |
| `pe.coff_*` / "executables for several architectures", `.exe`/`.dll`/`.sys` | `MZ`@0 -> e_lfanew u32 LE @0x3C -> require `PE\0\0` there -> COFF FileHeader: Machine u16 @+4, NumberOfSections @+6, TimeDateStamp @+8, SizeOfOptionalHeader @+20, Characteristics @+22; OptionalHeader magic @+24 (`0x10b` PE32 / `0x20b` PE32+). `xxd -s $((0x3c)) -l 4` then `xxd -s <lfanew> -l 8`. `file`/`pefile` cross-check only |
| `elf.*` / `macho.*` siblings (promised "several architectures", not yet asked) | ELF: `\x7fELF`, EI_DATA @5 picks endianness, e_machine u16 @18. Mach-O: `feedface`/`feedfacf` (either byte order) cputype u32 @4; fat `cafebabe` = BE nfat_arch @4 + 20-B entries (Java .class shares `cafebabe`; small nfat_arch = fat). Emit hex in the same `0x%0Nx` width as the field's `uNN` |
| exe-extension decoy (`.exe` that is text/zip/PNG, `MZ` with no/garbled `PE\0\0` at e_lfanew) | header absent -> literal `none` if the syntax offers it; never fall back to a later `PE\0\0` hit or the extension |
| "impostor", "renamed", "disguise" | trust magic bytes at offset 0; a matching string deeper in the file is a decoy |
| answer_format syntax "use the literal none only when the requested field is absent" | field missing (e.g. no header) -> `none` |
| answer_format kind `json` | `json.dumps(v, separators=(",",":"), ensure_ascii=False)` -- compact, no spaces, no Markdown |
| Mastery `set1.`..`setN.` ids, artifact `delivery N: <zip> -> <member>` or `<zip>-0N.zip -> <member>` | resolve each set's member separately; see delivery layouts below |

## Day by day
**Day 1 — You Must Be This Hash to Ride** (identity inventory). One text member (TT `roster.csv`, Mastery a renamed
`evidence-note-copy.txt` + original). filename / size-bytes / md5 / sha1 / sha256 via `zipfile` + `hashlib`; CORRECT
~36 s first try. Mastery zip-of-zips first seen.

**Day 2 — Looks Can Be Deceiving** (`<member>-magic-prefix-hex-16`): first 16 bytes, lowercase hex, no `0x`. CORRECT ~34 s.
- Variants: TT `readme.exe` that was UTF-8 text; Mastery set2 `disguised-report.bin` that was a PDF.
- TT question text named `roster.csv` while `answer_ids` said `readme-executable-...` and the zip held only `readme.exe`
  -> `lib.common.find_artifact_hinted` (member ~ answer-id stem). TT `expired` = pre-Homebase latency, not analysis.
- Mastery zip-of-zips broke name lookup (returned the inner zip's `PK..`) -> `find_artifact` recurses nested zips.

**Day 3 — BOM Voyage** (`text.utf8_bom_present` enum `true`/`false`). First 3 bytes == `EF BB BF`; CORRECT ~28 s.
Mastery `export-001-with-bom.txt` really had a BOM -- decide from bytes, never the name. utf16/32 variants unconfirmed.

**Day 4 — Picture This** (`jpeg.sof_dimensions_pixels`). Walk segments by declared length to SOFn (one SOF0 @0x88) ->
`<width>x<height>` (GM-confirmed; not EXIF/filename dims). Rotation flavor not asked. CORRECT ~38 s; TT/Mastery in-window.

**Day 5 — Chunk Norris** (`png.ihdr_dimensions_pixels`). IHDR @0x10 BE u32 width,height -> `<width>x<height>` (Day 4
form by analogy, accepted). IDAT/CRC/after-IEND "passenger" checks were diagnostics only. CORRECT ~33 s, first try.

**Day 6 — Portable Deception** (PDF). `pdf.header_version` exact_text.
- `xxd -l 16` -> `%PDF-1.4` -> answer bare `x.y`. Only one `%PDF-` marker; no catalog `/Version`; exiftool PDFVersion agreed.
- Rules adopted (synthetic, NOT GM-judged): header must be at file start; `%PDF-` deeper (impostor) -> `none`; catalog
  `/Version` (incl. incremental updates) never changes header_version.
- Mastery: two same-named downloads addressed `delivery N: metadata-day-06-evidence.zip -> document-00N.pdf`; pre-fetched
  contract listed 003/004, live asked 006/007 -> read the live start. CORRECT ~34 s; TT in_window 2.7 s.

**Day 7 — Seven-Zip, No Relation** (ZIP EOCD census). `zip.eocd_total_entries` integer, id `d07-zip-001-zip-eocd-total-entries`.
- Evidence zip held `evidence-drop-001.zip` (410 B, Stored, data-descriptor flag) with `room-01/item-1.txt`,
  `room-02/item-1.txt` (identical 48 B text). EOCD total-entries u16 @+10 = 2 -> answer `2` (base-10, no units).
- All variants were honest: EOCD disk/total == CD headers == LFHs, no comment/trailing bytes. The prompt's "empty space"
  / "census that does not add up" (claim vs real walk, padding, dir entries) was flavor only — not exercised, so it is
  still unknown whether the GM wants the claimed or the walked count when they differ. Answer the field = the CLAIM.
- Worker: `xxd | tail` + `7z l -slt` on triage's pre-extracted inner zip, then stdlib `struct` EOCD parser in solve.py
  (ZIP64 aware). CORRECT 57 s after start, first try. TT 3 entries (in_window 0.89 s / 7 s); Mastery set1 4, set2 5
  (1.33 s / 7 s). Pre-fetched mastery contract (003/004) matched live this time.

**Day 8 — What's in the Box?** (`zip.central_directory_member_names`, kind `json`, id
`d07-zip-001-zip-central-directory-member-names`). Prompt: "The count was only the beginning. Inventory every stored
path, preserve directory context, and identify the archive whose names reveal an impossible provenance claim."
- Artifact: 3308 B evidence zip with 5 members (`evidence-note.txt` 33 B, `camera-001.jpg`, `panel-001.png`,
  `document-001.pdf`, and the SAME 410 B `evidence-drop-001.zip` as Day 7). Single contract = 12 fields at once.
- Key insight: the field = the inner zip's central-directory filename fields, verbatim and in CD order:
  `["room-01/item-1.txt","room-02/item-1.txt"]` -- the two basenames collide, so "preserve directory context" means keep
  the full stored path (never basename/dedupe/sort). No `../`, absolute, backslash or UTF-8/cp437 oddities appeared in
  any variant (UT extra, 2026-10-01 09:00, unix attrs); the "impossible provenance" decoy was NOT exercised -- still answer
  the raw CD names (the field says central_directory, not LFH, not sanitized).
- Worker: 3 tool calls -- read contract + Day 7 solver, `7z l -slt` + `xxd | tail` on the pre-extracted inner zip, then
  copied the Day 7 solve.py and added a CD walker + `json.dumps(names, separators=(",",":"), ensure_ascii=False)`.
  Start 15:43:55Z -> CORRECT 15:44:22Z (~27 s), first try, all 12 confirmed.
- TT: 8 s window, in_window 1.15 s (solve 0.13 s), CORRECT. Mastery: 5 sets / 60 answers, 10 s window, in_window 1.34 s,
  CORRECT. Only the note's case id differed between variants.
- LIB (ratchet D8): spelling recorded as `knowledge.ZIP_CD_MEMBER_NAMES_FMT` -> `json.dumps(names, separators=(",",":"))`.

**Day 9 — Built Different** (`pe.coff_machine_u16_hex`, kind `pattern`, syntax "lowercase hexadecimal with a 0x prefix",
norm `trim`, id `d09-pe-001-pe-coff-machine-u16-hex`). Prompt: "A software drop contains executables for several
architectures, plus decoys wearing executable extensions. Determine what can actually run where."
- Artifact: 598 KB evidence zip = the D8 kit (byte-identical apart from the case id) + `telemetry-agent-001.exe`
  (1,257,984 B, Deflate). It was an honest Go 1.22.2 PE32 console exe (buildinfo `GOOS=windows GOARCH=386`, path
  `huntress.generated/windows-pe`): e_lfanew 0x80, `PE\0\0`, Machine `0x014c`, 7 sections incl. `.symtab`, opt magic
  0x10b, TimeDateStamp 0. No ELF/Mach-O, no decoy exe in single, TT or any Mastery set -- the flavor was unexercised.
- Key insight: the field name is the spec -- COFF FileHeader.Machine read as a u16 and printed `0x%04x` (zero-padded to 4
  digits: `0x014c`, not `0x14c`, not `i386`). The binary lane's `machine` word (`knowledge.PE_MACHINE` -> `i386`) is a
  DIFFERENT field; don't reuse it here.
- Worker: 4 tool calls -- grep D8 solver's handlers + `jq` the pre-fetched TT/Mastery contracts (both errored: pre-start
  contracts have no `answer_ids`, harmless), `file` + `xxd -l 64` + 3-line python `struct` (0x3C -> PE sig -> u16), then
  `cp` the D8 solve.py and append a `pe-coff-machine-u16-hex` suffix branch (+ pre-armed ELF `e_machine` branch, `none`
  for MZ-without-PE decoys). Start 13:00:07.1Z -> CORRECT 13:00:54.5Z (~47 s), first try, all 13 confirmed.
- TT: 6 s window, in_window 2.88 s (submit round-trip 2.31 s, solve 0.14 s), CORRECT. Mastery: 5 sets / 65 answers, 7 s
  window, in_window 2.49 s (solve 0.86 s -- 3 MB of nested Stored zips with 1.2 MB exes), CORRECT. Only the case id (note
  hashes/magic) and exe bytes varied; Machine 0x014c everywhere.

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes: base-10 integer, no units. Hashes: hex, case ignored.
- Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`).
- Booleans: enum `true` / `false` (lowercase) — the contract hands the vocabulary; pick, don't probe.
- Pixel dimensions (JPEG SOF, PNG IHDR): `<width>x<height>` — width first, lowercase `x`, no spaces (GM-confirmed both,
  re-confirmed D8 `257x146` / `269x153`).
- PDF header version: bare `x.y` from the leading `%PDF-x.y` (no `PDF-`/`%` prefix); absent header -> literal `none`
  (contract wording; `none` itself not yet GM-confirmed).
- Counts (`zip.eocd_total_entries`): plain base-10 integer string, e.g. `2` (GM-confirmed D7 + D8 all modes).
- JSON lists (`zip.central_directory_member_names`): compact array, no spaces after `,`, double quotes, full stored path
  with `/` dirs, CD order -- `["room-01/item-1.txt","room-02/item-1.txt"]` (GM-confirmed D8 single/TT/Mastery x5).
  Whether the GM's `trim` normalization also tolerates `", "` spacing is untested -- always emit compact.
- Header integers as hex (`pe.coff_machine_u16_hex`): `0x` + lowercase hex zero-padded to the field width named in the
  id (`u16` -> 4 digits): `0x014c` (GM-confirmed D9 single/TT/Mastery x5). Unpadded `0x14c` untested -- don't emit it.
  Contrast: magic-prefix hex has NO `0x`; binary-lane `machine` wants the word (`i386`/`x86-64`).
- Rejected spellings: none recorded in this lane (no wrong submission in any mode, days 1-9).
- `knowledge.py`: `JPEG_DIMENSIONS_FMT`, `PNG_DIMENSIONS_FMT`, `PDF_HEADER_VERSION_FMT`, `ZIP_EOCD_TOTAL_ENTRIES_FMT`,
  `ZIP_CD_MEMBER_NAMES_FMT`, `BOOL` (PE u16-hex form not there yet -- proposed D9).
- Inference: the field id IS the spec name (`sof_dimensions_pixels` = SOF frame header, `ihdr_` = IHDR chunk,
  `header_version` = file header, `eocd_total_entries` = EOCD record's own claim, `central_directory_member_names` = CD
  file-name fields, `coff_machine_u16_hex` = COFF FileHeader.Machine as u16 hex) — read the field name literally to
  pick which structure to parse; a claimed count is NOT a CD walk / `zipfile` len, and CD names are NOT local-header
  names (they happened to agree on D7/D8). A `_uNN_hex` suffix fixes both the read width and the printed width.

## Delivery layouts seen (resolve these before parsing)
- Single / TT: one zip; members named in `artifact` after `->` (D8: 5 members, filename question's artifact = zip only).
- Mastery days 1,2,4,5: ONE download named `...-evidence-01.zip` that is an outer zip containing `...-01.zip` and
  `...-02.zip` (zip-of-zips); each inner zip holds its set's member.
- Mastery day 7: zip-of-zips again, three levels (outer `-01.zip` holds `-01.zip` + `-02.zip`, each holding the asked
  `evidence-drop-00N.zip`); artifact ref `metadata-day-07-evidence-0N.zip -> evidence-drop-00N.zip` (no `delivery N:`).
- Mastery day 8: same shape, FIVE sets: one 17 KB download `metadata-day-08-evidence-01.zip` (Stored, UTF-8 flag) holding
  `-01.zip`..`-05.zip`, each a full 5-member kit (incl. its own `evidence-drop-001.zip`). Refs `...-evidence-0N.zip ->
  <member>`; every set reuses the same member names, so resolve by (set zip, member), never member name alone.
- Mastery day 9: same five-set shape, but the GM download is named `<challenge-id>-mastery.zip`
  (`metadata-forensics-day-09-built-different-mastery.zip`, 2.99 MB, Stored) while refs say `metadata-day-09-evidence-0N.zip
  -> <member>` -- resolve the bundle by sha256 (`lib.common.container_by_sha`), not by its filename.
- Mastery day 6: two downloads with identical filenames -> `delivery 1: <zip>` / `delivery 2: <zip>` in artifact refs.
- Member numbering shifts between pre-fetched contract and live attempt (003/004 vs 006/007) — never hardcode names.

## Pitfalls that cost time
- Name lookup by zip filename alone breaks on zip-of-zips (returned `PK` bytes as the "magic") — recurse into nested zips.
- Contract question text can be stale vs `answer_ids` (Day 2 TT): answer under `answer_ids`, locate the member that exists.
- Don't let the flavor text widen the question: prompts mention impostors/passengers/orientation/provenance, but only the
  named field is graded. Answer it; keep extra checks as diagnostics.
- Container-of-containers: when the asked file is itself a zip, a naive `rfind(PK\x05\x06)` on the downloaded evidence
  zip reads the OUTER EOCD / CD (D8 outer CD = the 5 kit members, Mastery outer = 5 set zips). Resolve the named member's
  bytes first, then parse.
- Name-list fields: `zipfile.namelist()` is CD order but decodes non-UTF-8-flagged names as cp437 and is fine for honest
  zips; for hostile names (`../`, `/abs`, `C:\`, `\` separators, LFH != CD name, duplicates) emit the CD bytes as-is --
  don't let an extractor's sanitizing (7z/unzip strip `../` and leading `/`) rewrite the answer.
- Decoys by name: `*-with-bom.txt`, `.exe` that is text, `.bin` that is PDF, `.pdf` that is PNG — bytes win every time.
- Timed windows are ~5-10 s (D8: TT 8 s / Mastery 10 s; D9 shrank to 6 s / 7 s) and most of it is GM start/download/
  submit round-trips (D9 TT submit alone 2.3 s): never do anything slow (extraction to disk, exiftool, `pefile` full
  parse, subprocess) in-window; parse fixed offsets in memory. Big members (1.2 MB exe x5) pushed Mastery solve to 0.86 s
  -- decompress each member once and cache by (set zip, member).
- Executable fields: don't take `file`'s "Intel i386" / `pefile` machine names / the Go GOARCH token as the answer; the
  metadata field is the raw u16. And require `PE\0\0` exactly at e_lfanew -- an `MZ` stub alone is not a PE (decoy).
- Fastest path for a new carry-over day: copy the previous day's solver (which already answers every earlier family) and
  add only the new suffix handler -- D8 27 s, D9 47 s that way. The harness skeleton in `solver/solve.py` is NOT the
  previous day's solver; copy from `challenges/day<NN-1>/metadata-*/solver/solve.py`.
- Pre-fetched TT/Mastery `contract.json` is the HTTP 409 `start_required` body: `questions` (with ids, no sha tag) but
  NO `answer_ids` -- `jq '.answer_ids|map(..)'` errors; read `questions[].id` to preview the field set.
- Harness: re-running `hctf start` on an already-solved challenge overwrote `single_solve/start.json` and made the stop gate
  think it was incomplete (Day 2, ~2 min lost) — restore start.json from `log.jsonl`.
- Tools installed (2026-10-07): exiftool, pdfinfo/pdftotext (poppler), qpdf, mutool, pdf-parser, pdfid, pngcheck,
  zsteg, steghide, binwalk, foremost, mediainfo, sqlite3, identify/convert (ImageMagick), olevba/oleid.
