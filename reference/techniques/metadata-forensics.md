# metadata-forensics — technique log (days 1-13; updated after every day)

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every day = ONE evidence zip (`metadata-day-NN-evidence.zip`, plain Deflate, no password so far). Days 1-7: one tiny
  member (33 B - 3 KB) and ONE structural fact. Day 8+: the zip carries the whole cumulative kit (note + jpg + png + pdf +
  inner zip [+ D9 a 1.26 MB PE `.exe`]) and even the SINGLE contract asks every field (D8 12, D9 13 = identity + every
  earlier day's field + the new one). The member can itself be a container (D7/8: an inner ZIP whose own EOCD / CD is
  the asked field). Each day adds ONE member + ONE field; the previous kit members are byte-identical except the case id.
- Day 9 crossed into EXECUTABLE headers (`pe.coff_machine_u16_hex`): the metadata lane now parses binaries too, but only
  the raw header field -- answer the u16 as hex, not the binary lane's machine word (`i386`). Day 10 stayed on the SAME
  PE (`pe.address_of_entry_point_rva_hex`) and DE-escalated: zip = the exe only, contract = 1 field (TT 1, Mastery 2x1).
  Day 11 kept that shape and moved INTO the PE's resources (`pe.version_original_filename`, VS_VERSIONINFO string).
  Day 12 switched to a NEW member family -- a 5 KB .NET dll (`d12-dotnet-NNN-dotnet-mvid-guid`) -- and went into the CLI
  METADATA tables (Module.Mvid via the #GUID heap); same 1-field / TT 1 / Mastery 2x1 shape. Day 13 another NEW
  family -- a 9.7 KB MSI (OLE/CFB, `d13-msi-NNN-msi-product-code-guid`) -> the Property table; same 1-field shape.
- A new `<fmt>.<field>` family each day: identity (name/size/hashes) -> magic prefix -> `text.utf8_bom_present` ->
  `jpeg.sof_dimensions_pixels` -> `png.ihdr_dimensions_pixels` -> `pdf.header_version` -> `zip.eocd_total_entries` ->
  `zip.central_directory_member_names` -> `pe.coff_machine_u16_hex` -> `pe.address_of_entry_point_rva_hex` ->
  `pe.version_original_filename` -> `dotnet.mvid_guid` -> `msi.product_code_guid`. Since Day 3 the question literally names the field
  (`Determine <fmt>.<field> for <member>`); answer ids read `dNN-<fmt>-NNN-<fmt>-<field>` (`.`/`_` -> `-`). NOTE the
  `dNN` is the drop/member family, not the day the field appeared: Day 8's new field came as `d07-zip-001-zip-central-
  directory-member-names`; Day 9's as `d09-pe-001-pe-coff-machine-u16-hex` (new member family -> new `dNN`); Day 10's as `d09-pe-001-pe-address-of-entry-point-rva-hex` (same exe family), Day 11's as
  `d09-pe-001-pe-version-original-filename`, Day 12's as `d12-dotnet-001-dotnet-mvid-guid` (new family -> new `dNN`).
- The prompt's flavor text describes decoys (impostors, renamed copies, "-with-bom" names, EXIF/presentation lies, chunk
  "passengers", catalog /Version overrides, "impossible provenance" names). The asked field so far was always the
  STRUCTURAL truth from the header/record bytes; names/extensions/secondary metadata are the lie. Singles D1-D9 were
  first-submit CORRECT in ~27-60 s; D10 took one wrong spelling (unpadded hex). Every TT/Mastery since D4 CORRECT first try.
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
  all 7 copies but the exe's sha256 differs per set (re-built per variant). D10: the entry RVA re-rolled per variant
  (single 0x00065bd0, TT 0x00063a80, Mastery 0x00063510 / 0x00065bd0). D11: the PE's ARCHITECTURE re-rolled per variant
  (single 386 0x014c, TT amd64 0x8664, Mastery arm64 0xaa64 + 386) and OriginalFilename follows it (`pe-base-<goarch>.exe`).
  D12: every dll is 5,120 B with the same layout; the MVID, the sha256 and the `Huntress.Managed.<12HEX>` type name re-roll
  per variant (managed-001..004). D13: four installer-00N.msi with DIFFERENT bytes/sha256 (same 9,728 B) but the SAME
  ProductCode in every mode -- the "collision" is the point; the answer can legitimately repeat across sets.
  Never cache a value across sets.
- **Field-set size** -- grows AND shrinks: D7 TT/Mastery went 1 -> 11 fields (Mastery 22); D8 12 in every mode (Mastery
  5 x 12); D9 13 (Mastery 5 x 13); D10 back to ONE field everywhere (Mastery 2 sets x 1, zip = the lone exe). Families: the day's field +
  `evidence-note-{filename,size-bytes,md5,sha1,sha256,magic-prefix-hex-16,text-utf8-bom-present}` + carry-overs
  `d04-jpeg-*-sof-dimensions-pixels`, `d05-png-*-ihdr-dimensions-pixels`, `d06-pdf-*-header-version`, `d07-zip-*-eocd-
  total-entries`, `d07-zip-*-central-directory-member-names`, `d09-pe-*-pe-coff-machine-u16-hex`. Dispatch on the
  answer-id SUFFIX and keep EVERY earlier family answerable (reference: `challenges/day09/metadata-built-different/
  solver/solve.py` answers all 13; `day10/metadata-where-do-we-begin/solver/solve.py` = those + entry/image-base/opt-magic
  /ELF e_entry branches).
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
| `pe.address_of_entry_point_*` / `pe.image_base*` / "start addresses" | opt = e_lfanew+24: AddressOfEntryPoint u32 @opt+16 (an RVA); ImageBase u32 @opt+28 (PE32) / u64 @opt+24 (PE32+). `od -An -tx4 -j$((lfanew+40)) -N4 f`. objdump's "start address" = ImageBase+RVA (a VA, NOT the RVA) |
| `elf.*` / `macho.*` siblings (promised "several architectures", not yet asked) | ELF: `\x7fELF`, EI_DATA @5 picks endianness, e_machine u16 @18. Mach-O: `feedface`/`feedfacf` (either byte order) cputype u32 @4; fat `cafebabe` = BE nfat_arch @4 + 20-B entries (Java .class shares `cafebabe`; small nfat_arch = fat). Emit hex in the same `0x%0Nx` width as the field's `uNN` |
| `dotnet.*` / `.dll` "Mono/.Net assembly" / "module identities", "rebuilds vs renames" | CLI metadata, stdlib only (no dnfile in-window): PE data dir 14 (CLI header) -> MetaData RVA -> `BSJB` root -> stream headers (`#~`, `#Strings`, `#GUID`, `#Blob`). `#~`: HeapSizes byte @+6 (bit1 = 4-byte GUID index), Valid u64 @+8, row counts @+24; Module row 0 = Generation u16, Name (str idx), **Mvid (guid idx, 1-based)** -> 16 B at #GUID+(i-1)*16 -> `str(uuid.UUID(bytes_le=..))`. Cross-check: `monodis`/`ilspycmd -il` print `.module` + `// MVID: {..}` |
| `pe.version_*` / "version resources remember what the binaries called themselves" | VS_VERSIONINFO StringFileInfo: `pefile.PE(data=b, fast_load=True)`; `pe.parse_data_directories(directories=[DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])`; walk `pe.FileInfo[..][..].StringTable[..].entries` (bytes keys). Match the id tail to the key ignoring case/`-_` (`original-filename` -> `OriginalFilename`). Shell: `strings -e l f.exe | grep -A1 OriginalFilename` |
| `msi.*` / `.msi` / "installers copied, renamed, repackaged", "stable product identities" | OLE CFB (`d0 cf 11 e0`). Fast path: `strings -n 6 x.msi \| grep -aoE 'ProductCode\{[0-9A-F-]{36}\}'`. Exact: CFB streams -> demangle names (0x3800-0x4840 base-64 packing) -> `!_StringPool`/`!_StringData` (refs 3 B wide if pool header bit 0x80000000) -> `!Property` column-major (all keys, then all values). `msiinfo`/`msidump` NOT installed; `olefile` is in the venv. Reference: `challenges/day13/metadata-product-placement/solver/solve.py` `msi_property` |
| GUID field (`*-guid`) | spelling follows the SOURCE: a stored STRING (MSI ProductCode) verbatim, braces + uppercase; a binary GUID (.NET #GUID) -> `uuid.UUID(bytes_le=..)` lowercase, no braces. answer_format ("8-4-4-4-12 including hyphens") does not settle braces |
| exe-extension decoy (`.exe` that is text/zip/PNG, `MZ` with no/garbled `PE\0\0` at e_lfanew) | header absent -> literal `none` if the syntax offers it; never fall back to a later `PE\0\0` hit or the extension |
| "impostor", "renamed", "disguise" | trust magic bytes at offset 0; a matching string deeper in the file is a decoy |
| answer_format syntax "use the literal none only when the requested field is absent" | field missing (e.g. no header) -> `none` |
| answer_format kind `json` | `json.dumps(v, separators=(",",":"), ensure_ascii=False)` -- compact, no spaces, no Markdown |
| Mastery `set1.`..`setN.` ids, artifact `delivery N: <zip> -> <member>` or `<zip>-0N.zip -> <member>` | resolve each set's member separately; see delivery layouts below |

## Day by day
**Days 1-8** (one field each, all first-try ~27-57 s unless noted): D1 identity (filename/size/md5/sha1/sha256; Mastery
zip-of-zips first seen) -> D2 `magic-prefix-hex-16` (TT `readme.exe` was text, Mastery `.bin` a PDF; stale question member ->
`find_artifact_hinted`) -> D3 `text.utf8_bom_present` (`*-with-bom.txt` really had one -- bytes, not name) -> D4 JPEG SOFn
`<w>x<h>` -> D5 PNG IHDR `<w>x<h>` -> D6 `pdf.header_version` bare `x.y` (Mastery two same-named `delivery N:` downloads) -> D7
`zip.eocd_total_entries` of the INNER zip (stdlib EOCD parse; TT 3, Mastery 4/5) -> D8 `zip.central_directory_member_names`
compact JSON of full CD paths in CD order (5-member kit, 12 fields).

**Day 9 — Built Different** (`pe.coff_machine_u16_hex`, `pattern` lowercase `0x`): kit + `telemetry-agent-001.exe`, an
honest Go 1.22 386 PE32 (e_lfanew 0x80, 7 sections, opt magic 0x10b). COFF Machine u16 -> `0x014c` (padded; not `i386`,
the binary lane's word). "Several architectures + decoys" flavor unexercised. ~47 s first try; TT/Mastery 5 x 13 in-window.

**Day 10 — Where Do We Begin?** (`pe.address_of_entry_point_rva_hex`, id `d09-pe-001-...`): zip = the D9 Go 386 PE
alone, 1 field everywhere. OptionalHeader.AddressOfEntryPoint (u32 @ e_lfanew+40) `0x%08x` -> `0x00065bd0`; unpadded
`0x65bd0` REJECTED (lane's first wrong submit). objdump's start address is the VA, not the RVA. ~75 s, 1 wrong; TT/Mastery
first try (RVA re-rolled per variant). "Lying report" flavour unexercised.

**Day 11 — What's My Name Again?** (`pe.version_original_filename`, id `d09-pe-001-pe-version-original-filename`): same
lone Go PE; VS_VERSIONINFO OriginalFilename VERBATIM (`pe-base-386.exe`), not the randomized member name
(`telemetry-agent-001.exe` = the "impersonator"). pefile resource walk, ONE command, ~25 s first try; TT amd64 / Mastery
arm64 + 386 variants, both first try.

**Day 12 — Managed Expectations** (`dotnet.mvid_guid`, kind `pattern`, syntax "canonical GUID text in 8-4-4-4-12
hexadecimal form, including hyphens", norm `trim`, id `d12-dotnet-001-dotnet-mvid-guid`). Prompt: "The .NET assemblies
share names, versions, and source ancestry -- but their module identities remain distinct. Separate rebuilds from renames."
- Artifact: 2 KB zip -> `managed-001.dll`, 5,120 B PE32 i386 .NET (BSJB `v4.0.30319`; `<Module>`, a
  `Huntress.Managed.<12HEX>` type and a `get_ModuleVersionId` memberref -- the hint). One dll per delivery; the "renames vs
  rebuilds" comparison was never asked, only the MVID.
- Key insight: MVID = Module table row 0, 3rd column (guid-heap index, 1-based) -> 16 bytes in `#GUID` rendered as .NET
  `Guid.ToString()` = mixed-endian (`uuid.UUID(bytes_le=...)`), lowercase, no braces: `21e410f3-c977-465c-80eb-6890ddd3085c`.
- Worker: the solver was the bare skeleton; it typed a ~90-line stdlib PE -> CLI header -> BSJB streams -> `#~` -> `#GUID`
  parser + the old identity/PE branches and submitted in ONE command (2 tool calls; most of the ~55 s launch->CORRECT was
  generation). First try. Reference parser: `challenges/day12/metadata-managed-expectations/solver/solve.py` `dotnet_mvid`.
- TT window 30 s, in_window 0.95 s (managed-002); Mastery 2 sets (003/004), in_window 1.5 s. Both CORRECT first try.

**Day 13 — Product Placement** (`msi.product_code_guid`, kind `pattern` "canonical GUID text in 8-4-4-4-12 hexadecimal
form, including hyphens", norm `trim`, id `d13-msi-001-msi-product-code-guid`). Prompt: "Installers were copied, renamed,
and repackaged. Recover stable product identities, distinguish revisions from different products, and find the collision."
- Artifact: 3.3 KB zip -> `installer-001.msi` (9,728 B, msitools 0.103 OLE/CFB with an embedded `artifact.cab`).
- Key insight: answer = Property table `ProductCode` row VERBATIM `{DD1A80D5-0250-4F4D-B289-13096D633C61}`. Decoys in the
  same file: UpgradeCode, Component.ComponentId, SummaryInformation RevisionNumber (= PackageCode).
- Worker: stdlib CFB + MSI string-pool reader (regex `ProductCode(\{...\})` fallback). First submit stripped the braces
  (answer_format never mentions them) -> REJECTED; braced -> CORRECT. Start -> CORRECT ~76 s, 1 wrong (~19 s lost).
- TT (50 s window, in_window 0.96 s) and Mastery 2 sets (80 s, 2.55 s) CORRECT first try; every variant had the same
  ProductCode. "Revisions vs products" / "collision" were never asked -- only the ProductCode.

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
- Header integers as hex (`*_hex`): `0x` + lowercase hex ZERO-PADDED to the struct field's width: u16 Machine ->
  `0x014c` (D9), u32 AddressOfEntryPoint -> `0x00065bd0` (D10, all modes). The width comes from the STRUCT, not the id
  (D10's id has no `u32`). Contrast: magic-prefix hex has NO `0x`; binary-lane `machine` wants the word (`i386`), and the
  binary lane's `entry_point` was accepted UNPADDED (`0x401040`) -- different lane, different generator.
- GUIDs (`dotnet.mvid_guid`): .NET `Guid.ToString()` form -- first 3 groups byte-swapped from the heap bytes (bytes_le),
  lowercase, hyphenated, no braces (D12 all modes; `knowledge.DOTNET_MVID_GUID`, playbook metadata `guid` entry).
- MSI GUIDs (`msi.product_code_guid`): the Property string VERBATIM -- uppercase WITH braces `{DD1A80D5-...}` (D13 all
  modes; `knowledge.MSI_PRODUCT_CODE_GUID`). Bare form REJECTED. GUID spelling follows the source, not answer_format.
- Version-resource strings (`pe.version_<field>`): the StringFileInfo value verbatim, incl. extension (`pe-base-386.exe`,
  D11 all modes). `knowledge.PE_VERSION_STRING_KEY` maps id tail -> resource key.
- Rejected spellings: `0x65bd0` for pe.address_of_entry_point_rva_hex (D10 single; unpadded); brace-less
  `DD1A80D5-0250-4F4D-B289-13096D633C61` for msi.product_code_guid (D13 single).
- `knowledge.py`: `JPEG_DIMENSIONS_FMT`, `PNG_DIMENSIONS_FMT`, `PDF_HEADER_VERSION_FMT`, `ZIP_EOCD_TOTAL_ENTRIES_FMT`,
  `ZIP_CD_MEMBER_NAMES_FMT`, `PE_COFF_MACHINE_U16_HEX_FMT`, `PE_ENTRY_POINT_RVA_HEX_FMT` (+`_REJECTED`), `BOOL`;
  `playbook` metadata `hex` entry carries the padding rule.
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
- Mastery day 10: TWO sets only, refs `metadata-day-10-evidence-0N.zip -> telemetry-agent-00N.exe` (003/004).
  Day 11 identical shape (`metadata-day-11-evidence-0N.zip`, one download nesting both set zips).
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
- Fresh member family = skeleton solver (D10, D12): copy the previous day's solver first, then add the new family's
  handler -- D12's worker re-typed the identity/PE branches next to the .NET parser (~50 s of generation).
- Executable fields: don't take `file`'s "Intel i386" / `pefile` machine names / the Go GOARCH token as the answer; the
  metadata field is the raw u16. And require `PE\0\0` exactly at e_lfanew -- an `MZ` stub alone is not a PE (decoy).
- Normalizing a stored value (D13, cost a wrong submit + 19 s): the solver's `_guid()` stripped MSI braces because
  answer_format said "8-4-4-4-12". When the field is a stored string, emit it verbatim; reshape only what the format
  explicitly forbids.
- Hex width (D10, cost a wrong submit + 17 s): `"0x%x"` drops leading zeros; print `0x%0{2*size}x` for the field's
  struct size. RVA vs VA: `_rva` = the raw field, never ImageBase + it.
- Fastest path for a new carry-over day: copy the previous day's solver (which already answers every earlier family) and
  add only the new suffix handler -- D8 27 s, D9 47 s that way. The harness skeleton in `solver/solve.py` is NOT the
  previous day's solver; `cp challenges/day<NN-1>/metadata-*/solver/solve.py` over it (D10 spliced by sed instead).
- Pre-fetched TT/Mastery `contract.json` is the HTTP 409 `start_required` body: `questions` (with ids, no sha tag) but
  NO `answer_ids` -- `jq '.answer_ids|map(..)'` errors; read `questions[].id` to preview the field set.
- Harness: re-running `hctf start` on an already-solved challenge overwrote `single_solve/start.json` and made the stop gate
  think it was incomplete (Day 2, ~2 min lost) — restore start.json from `log.jsonl`.
- Tools installed (2026-10-07): exiftool, pdfinfo/pdftotext (poppler), qpdf, mutool, pdf-parser, pdfid, pngcheck,
  zsteg, steghide, binwalk, foremost, mediainfo, sqlite3, identify/convert (ImageMagick), olevba/oleid.
