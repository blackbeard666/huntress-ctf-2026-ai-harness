# metadata-forensics — technique log (days 1-6; updated after every day)

How this lane has looked so far (observations, not guarantees):
- Every day = ONE evidence zip (`metadata-day-NN-evidence.zip`, plain Deflate, no password so far) holding a tiny member
  (33 B - 3 KB). The question asks ONE structural fact about a named member, read from the raw bytes.
- A new `<fmt>.<field>` family each day: identity (name/size/hashes) -> magic prefix -> `text.utf8_bom_present` ->
  `jpeg.sof_dimensions_pixels` -> `png.ihdr_dimensions_pixels` -> `pdf.header_version`. Since Day 3 the question literally
  names the field (`Determine <fmt>.<field> for <member>`); answer ids read `dNN-<fmt>-NNN-<fmt>-<field>`.
- The prompt's flavor text describes decoys (impostors, renamed copies, "-with-bom" names, EXIF/presentation lies, chunk
  "passengers", catalog /Version overrides). The asked field so far was always the STRUCTURAL truth from the header bytes;
  names/extensions/secondary metadata are the lie. All 6 single solves were first-submit CORRECT in ~30-40 s.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- see "Delivery layouts seen" below; resolve the named member through whatever wrapper arrives.
- **Decoys** -- renamed copies, misleading extensions/names, secondary metadata (EXIF, catalog /Version) that disagree
  with the header: always answer from the structural header bytes of the member the question names.
- **Member and values** -- names, sizes and dimensions re-roll per variant; nothing about the sample is constant.

## Recognition cues -> first move
| You see | First move |
|---|---|
| `<zip> -> <member>` in `questions[].artifact` | `7z l -slt <zip>` then `7z x -o work/ <zip>`; (or python `zipfile` read of the member) |
| filename / size / md5 / sha1 / sha256 | `stat -c %s`, `md5sum sha1sum sha256sum` on the extracted member (bytes, not the zip entry name) |
| "first sixteen bytes", "magic", "extension claims" | `xxd -p -l 16 <member>` (lowercase, no spaces); `file -k` only for orientation |
| `text.*_bom_present` | `xxd -l 4`: UTF-8 BOM = `ef bb bf` (UTF-16LE `ff fe`, BE `fe ff`, UTF-32LE `ff fe 00 00`) -> `true`/`false` |
| `jpeg.*dimensions*` / SOF | walk JPEG segments from `ffd8` by length to SOFn (`ffc0..ffcf` minus c4/c8/cc): P, Y=height, X=width. `exiftool -ImageSize` cross-check only |
| `png.ihdr_*` / "walk their chunks" | `xxd -s 16 -l 8` = IHDR width,height (BE u32). Chunk walk = len/type/data/CRC loop (`lib.stego.png_chunks`) |
| `pdf.header_version` / "declared versions" | `head -c 16 <f> | xxd` -> `%PDF-x.y` at offset 0; `grep -a -o '/Version[^/>]*'` only as a diagnostic |
| "impostor", "renamed", "disguise" | trust magic bytes at offset 0; a matching string deeper in the file is a decoy |
| answer_format syntax "use the literal none only when the requested field is absent" | field missing (e.g. no header) -> `none` |
| Mastery `set1.`/`set2.` ids, artifact `delivery N: <zip> -> <member>` | resolve each set's member separately; see delivery layouts below |

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

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes: base-10 integer, no units. Hashes: hex, case ignored.
- Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`).
- Booleans: enum `true` / `false` (lowercase) — the contract hands the vocabulary; pick, don't probe.
- Pixel dimensions (JPEG SOF, PNG IHDR): `<width>x<height>` — width first, lowercase `x`, no spaces (GM-confirmed both).
- PDF header version: bare `x.y` from the leading `%PDF-x.y` (no `PDF-`/`%` prefix); absent header -> literal `none`
  (contract wording; `none` itself not yet GM-confirmed).
- Rejected spellings: none recorded in this lane (no wrong submission in any mode, days 1-6).
- `knowledge.py`: `JPEG_DIMENSIONS_FMT`, `PNG_DIMENSIONS_FMT`, `PDF_HEADER_VERSION_FMT`, `BOOL`.
- Inference: the field id IS the spec name (`sof_dimensions_pixels` = SOF frame header, `ihdr_` = IHDR chunk,
  `header_version` = file header) — read the field name literally to pick which structure to parse.

## Delivery layouts seen (resolve these before parsing)
- Single / TT: one zip, one member, member named in `artifact` after `->`.
- Mastery days 1,2,4,5: ONE download named `...-evidence-01.zip` that is an outer zip containing `...-01.zip` and
  `...-02.zip` (zip-of-zips); each inner zip holds its set's member.
- Mastery day 6: two downloads with identical filenames -> `delivery 1: <zip>` / `delivery 2: <zip>` in artifact refs.
- Member numbering shifts between pre-fetched contract and live attempt (003/004 vs 006/007) — never hardcode names.

## Pitfalls that cost time
- Name lookup by zip filename alone breaks on zip-of-zips (returned `PK` bytes as the "magic") — recurse into nested zips.
- Contract question text can be stale vs `answer_ids` (Day 2 TT): answer under `answer_ids`, locate the member that exists.
- Don't let the flavor text widen the question: prompts mention impostors/passengers/orientation, but only the named
  field is graded. Answer it; keep extra checks as diagnostics.
- Decoys by name: `*-with-bom.txt`, `.exe` that is text, `.bin` that is PDF, `.pdf` that is PNG — bytes win every time.
- Timed windows are ~5-6 s and most of it is GM start/download/submit round-trips (solve ~0.1 s): never do anything slow
  (extraction to disk, exiftool) in-window; parse in memory.
- Harness: re-running `hctf start` on an already-solved challenge overwrote `single_solve/start.json` and made the stop gate
  think it was incomplete (Day 2, ~2 min lost) — restore start.json from `log.jsonl`.
- Tools installed (2026-10-07): exiftool, pdfinfo/pdftotext (poppler), qpdf, mutool, pdf-parser, pdfid, pngcheck,
  zsteg, steghide, binwalk, foremost, mediainfo, sqlite3, identify/convert (ImageMagick), olevba/oleid.
