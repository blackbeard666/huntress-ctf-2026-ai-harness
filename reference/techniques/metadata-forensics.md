# metadata-forensics — technique log (days 1-8; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every day = ONE evidence zip (`metadata-day-NN-evidence.zip`, plain Deflate, no password so far). Days 1-7: one tiny
  member (33 B - 3 KB) and ONE structural fact. Day 8: the zip carried the whole cumulative kit (note + jpg + png + pdf +
  inner zip, 3.3 KB) and even the SINGLE contract asked all 12 fields (identity + every earlier day's field + the new one).
  The member can itself be a container (Day 7/8: an inner ZIP whose own EOCD / central directory is the asked field).
- A new `<fmt>.<field>` family each day: identity (name/size/hashes) -> magic prefix -> `text.utf8_bom_present` ->
  `jpeg.sof_dimensions_pixels` -> `png.ihdr_dimensions_pixels` -> `pdf.header_version` -> `zip.eocd_total_entries` ->
  `zip.central_directory_member_names`. Since Day 3 the question literally names the field (`Determine <fmt>.<field> for
  <member>`); answer ids read `dNN-<fmt>-NNN-<fmt>-<field>` (`.`/`_` -> `-`). NOTE the `dNN` is the drop/member family,
  not the day the field appeared: Day 8's new field came as `d07-zip-001-zip-central-directory-member-names`.
- The prompt's flavor text describes decoys (impostors, renamed copies, "-with-bom" names, EXIF/presentation lies, chunk
  "passengers", catalog /Version overrides, "impossible provenance" names). The asked field so far was always the
  STRUCTURAL truth from the header/record bytes; names/extensions/secondary metadata are the lie. All 8 single solves were
  first-submit CORRECT in ~27-60 s; every TT/Mastery since Homebase (D4+) CORRECT first try.
- Titles are puns, not format hints: Day 7 "Seven-Zip, No Relation" was plain ZIP (PKWARE), no .7z anywhere.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen" below; resolve the named member through whatever wrapper arrives.
- **Decoys** -- renamed copies, misleading extensions/names, secondary metadata (EXIF, catalog /Version) that disagree
  with the header: always answer from the structural header bytes of the member the question names.
- **Member and values** -- names, sizes, dimensions and counts re-roll per variant; nothing about the sample is
  constant (Day 7 entry count went 2/3/4/5 with drop number 001-004; member names `room-NN/item-K.txt`). Day 8 re-rolled
  ONLY the note's case id (`Case <hex> evidence note.`, 33 B) -> md5/sha1/sha256/magic differ per set; jpg 257x146, png
  269x153, pdf 1.4, eocd 2, CD names identical across single/TT/5 Mastery sets. Never cache a value across sets anyway.
- **ESCALATED field set** -- the contract grows over time: D7 TT/Mastery went 1 -> 11 fields (Mastery 22); D8 started at
  12 already in single (TT 12, Mastery 5 sets x 12 = 60). Families: the day's field +
  `evidence-note-{filename,size-bytes,md5,sha1,sha256,magic-prefix-hex-16,text-utf8-bom-present}` + carry-overs
  `d04-jpeg-*-sof-dimensions-pixels`, `d05-png-*-ihdr-dimensions-pixels`, `d06-pdf-*-header-version`, `d07-zip-*-eocd-
  total-entries`, `d07-zip-*-central-directory-member-names`. Dispatch on the answer-id SUFFIX and keep EVERY earlier
  family answerable (reference: `challenges/day08/metadata-whats-in-the-box/solver/solve.py` answers all 12).
- **Answer kinds** -- `exact_text`, `integer`, `pattern` (hashes, case-insensitive), `enum` (`accepted_values`), and
  since D8 `json` ("compact valid JSON array with exact values and order"). Emit per `answer_format.kind`.
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
| "impostor", "renamed", "disguise" | trust magic bytes at offset 0; a matching string deeper in the file is a decoy |
| answer_format syntax "use the literal none only when the requested field is absent" | field missing (e.g. no header) -> `none` |
| answer_format kind `json` | `json.dumps(v, separators=(",",":"), ensure_ascii=False)` -- compact, no spaces, no Markdown |
| Mastery `set1.`..`setN.` ids, artifact `delivery N: <zip> -> <member>` or `<zip>-0N.zip -> <member>` | resolve each set's member separately; see delivery layouts below |

## Day by day
**Day 1 — You Must Be This Hash to Ride** (identity inventory). Zip with one text member (prompt says "three files";
only one present in single; TT used `roster.csv`, Mastery a renamed `evidence-note-copy.txt` + original).
- Asked: filename (base name with extension), size-bytes (integer), md5, sha1, sha256 (hex, case ignored).
- Worker: python `zipfile` + `hashlib`; submitted at step 4, CORRECT ~36 s after launch, first try.
- Mastery layout first seen: ONE download named after set1's zip, containing BOTH per-set zips (zip-of-zips).

**Day 2 — Looks Can Be Deceiving** (magic prefix vs extension). Field `<member>-magic-prefix-hex-16`.
- Answer = first 16 bytes of the member, lowercase hex, 32 chars, no `0x`/spaces. Single member was honest text.
- Variants: TT `readme.exe` that was actually UTF-8 text; Mastery set2 `disguised-report.bin` that was a PDF.
- TT quirk: contract question text named `roster.csv` while `answer_ids` said `readme-executable-...` and the zip held
  only `readme.exe` -> fix was `lib.common.find_artifact_hinted` (match member to answer-id stem, exe~executable). Always
  answer under `answer_ids`, trust the zip contents.
- TT submits all came back `expired` (5 s window, harness latency, pre-Homebase) — not an analysis error.
- Mastery zip-of-zips broke name lookup (outer zip has set1's name but not the member) -> returned the inner zip's
  `PK..` bytes. Fix: `find_artifact` recurses nested zips (depth 4), prefers member whose parent zip is the named one.
- Single CORRECT in ~34 s.

**Day 3 — BOM Voyage** (text encoding). `text.utf8_bom_present` enum `true`/`false`.
- Read first 3 bytes for `EF BB BF`; single member started `Case` -> false. CORRECT ~28 s, first try.
- Mastery set2 member named `export-001-with-bom.txt`: decide from bytes, never the name (that one did have a BOM).
- Solver also covers utf16/utf32 `_bom_present` variants (unconfirmed spellings).

**Day 4 — Picture This** (JPEG). `jpeg.sof_dimensions_pixels` exact_text.
- Walk segments by declared length (no fixed offsets) to the SOFn frame header; one SOF0 at 0x88; P=8, H, W.
- GM-confirmed form `<width>x<height>` (X first, lowercase x, no spaces). Not EXIF/filename dims.
- Prompt hinted rotation/"presentation vs structure" mismatch — not asked; solver carries best-effort exif_orientation /
  display dims (unconfirmed). CORRECT ~38 s. TT/Mastery CORRECT in-window (solve phase 0.12 s of a 6 s window).

**Day 5 — Chunk Norris** (PNG). `png.ihdr_dimensions_pixels` exact_text.
- IHDR at offset 0x10: BE u32 width, height -> `<width>x<height>` (same form as Day 4, applied by analogy, accepted).
- Verified geometry: inflated IDAT length == H*(1+W*bpp); chunks IHDR/IDAT/IEND, CRCs ok, no trailing data (the
  "structural passenger" = extra chunk / data after IEND, not in the asked file). Tools: `7z x`, `xxd`, `dd`.
- CORRECT ~33 s, first try.

**Day 6 — Portable Deception** (PDF). `pdf.header_version` exact_text.
- `xxd -l 16` -> `%PDF-1.4` -> answer bare `x.y`. Only one `%PDF-` marker; no catalog `/Version`; exiftool PDFVersion agreed.
- Rules adopted: header must be at file start (BOM/whitespace prefix tolerated); `%PDF-` deeper in the file (decoy in an
  impostor) is NOT the header -> `none`; catalog `/Version` (PDF 32000 §7.2.2, incl. incremental updates) never changes
  header_version. The impostor/`none` and override cases are synthetic (built by the worker), NOT GM-judged yet.
- Mastery delivery changed: two downloads with the SAME filename, saved/addressed as `delivery 1: <zip>` /
  `delivery 2: <zip>`; artifact field `delivery N: metadata-day-06-evidence.zip -> document-00N.pdf`.
- Pre-fetched mastery contract.json listed document-003/004; the live attempt asked 006/007 -> read the live start.
- CORRECT ~34 s; TT in_window 2.7 s (GM start call itself took 23 s that day — latency is outside the window).

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
- Rejected spellings: none recorded in this lane (no wrong submission in any mode, days 1-8).
- `knowledge.py`: `JPEG_DIMENSIONS_FMT`, `PNG_DIMENSIONS_FMT`, `PDF_HEADER_VERSION_FMT`, `ZIP_EOCD_TOTAL_ENTRIES_FMT`, `BOOL`.
- Inference: the field id IS the spec name (`sof_dimensions_pixels` = SOF frame header, `ihdr_` = IHDR chunk,
  `header_version` = file header, `eocd_total_entries` = EOCD record's own claim, `central_directory_member_names` = CD
  file-name fields) — read the field name literally to pick which structure to parse; a claimed count is NOT a CD walk /
  `zipfile` len, and CD names are NOT local-header names (they happened to agree on D7/D8).

## Delivery layouts seen (resolve these before parsing)
- Single / TT: one zip; members named in `artifact` after `->` (D8: 5 members, filename question's artifact = zip only).
- Mastery days 1,2,4,5: ONE download named `...-evidence-01.zip` that is an outer zip containing `...-01.zip` and
  `...-02.zip` (zip-of-zips); each inner zip holds its set's member.
- Mastery day 7: zip-of-zips again, three levels (outer `-01.zip` holds `-01.zip` + `-02.zip`, each holding the asked
  `evidence-drop-00N.zip`); artifact ref `metadata-day-07-evidence-0N.zip -> evidence-drop-00N.zip` (no `delivery N:`).
- Mastery day 8: same shape, FIVE sets: one 17 KB download `metadata-day-08-evidence-01.zip` (Stored, UTF-8 flag) holding
  `-01.zip`..`-05.zip`, each a full 5-member kit (incl. its own `evidence-drop-001.zip`). Refs `...-evidence-0N.zip ->
  <member>`; every set reuses the same member names, so resolve by (set zip, member), never member name alone.
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
- Timed windows are ~5-10 s (D8: TT 8 s, Mastery 10 s for 60 answers) and most of it is GM start/download/submit
  round-trips (solve ~0.1-0.2 s): never do anything slow (extraction to disk, exiftool) in-window; parse in memory.
- Fastest path for a new carry-over day: copy the previous day's solver (which already answers every earlier family) and
  add only the new suffix handler -- D8 went start -> CORRECT in 27 s that way.
- Harness: re-running `hctf start` on an already-solved challenge overwrote `single_solve/start.json` and made the stop gate
  think it was incomplete (Day 2, ~2 min lost) — restore start.json from `log.jsonl`.
- Tools installed (2026-10-07): exiftool, pdfinfo/pdftotext (poppler), qpdf, mutool, pdf-parser, pdfid, pngcheck,
  zsteg, steghide, binwalk, foremost, mediainfo, sqlite3, identify/convert (ImageMagick), olevba/oleid.
