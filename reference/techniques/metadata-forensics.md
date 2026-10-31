# metadata-forensics — technique log (days 1-30; updated after every day)

## Delivery layouts seen (resolve these before parsing)
- Single / TT: one zip; members named in `artifact` after `->` (filename questions: artifact = the zip only). Mastery:
  ONE download holding `-01.zip`..`-NN.zip` (D7 three levels deep); refs `<set zip> -> <member>`, names reused per set
  -> resolve by (set zip, member). D9: download `<id>-mastery.zip` vs refs `...-evidence-0N.zip` -> resolve by sha256
  (`lib.common.container_by_sha`). D6: two same-named downloads -> `delivery N: <zip>` refs.

How this lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (D8 organizer: "dynamic variations/mutations"; D23 re-rolled the WHOLE carried kit): every
  carried extractor must parse the general case, not D-day's sample (see "Member values").
- Every day = ONE evidence zip (plain Deflate, no password). D1-7: one tiny member, one fact; D8-9: cumulative kit in
  every mode; D10-14: one field everywhere. **D15+ split the modes**: single = 1 field (the new member), TT = cumulative
  kit (D15 20 -> D28 33 fields, +1/day), Mastery = N kits x the TT set (N=5 to D21, then +1/day: 11 D27, 12 D28), incl. a
  cross-member "synthesis" question. Pre-arm EVERY earlier family AND the synthesis before the timed run.
- Member families (one per day, each lasting ONE day as the single's field, then carried in the timed kit): note ->
  jpg -> png -> pdf -> inner zip -> Go PE (D9-11) -> .NET (D12) -> MSI -> LNK -> OOXML -> `.eml` -> WAV -> MP4 -> ELF
  (D19) -> Mach-O -> APK -> JAR -> SQLite (D23) -> EVTX -> regf hive -> Prefetch (D24-26 Windows DFIR: structure walk,
  pointer follow, decompress-then-parse) -> PCAP (D27, network) -> raw GPT DISK image `disk-001.img` (D28: one layer
  DOWN, the container of every earlier family) -> X.509 PEM `certificate-001.pem` (D29) -> a CORPUS zip
  `cluster-001.zip` (D30: `relation.*` = relationships BETWEEN ~30 members, not one member's struct). Member name
  `<family>-001.<ext>`.
- fmt word = the DOMAIN, read it from the question: `email` (not eml), `media` (audio D17 AND video D18, ffprobe
  vocabulary), `registry` (not regf), `disk` (raw image, not vhd), `relation` (D30, id family `cluster`), else the
  plain format (`pe` `msi` `lnk` `elf` `macho` `apk` `jar` `sqlite` `evtx` `prefetch` `pcap` `x509`). Question `Determine <fmt>.<field> for <member>`; id
  `dNN-<family>-NNN-<fmt>-<field>` (`.`/`_` -> `-`), `dNN` = the family's first day; `<family>` != `<fmt>` only for
  media (`d17-audio-001-media-`) and relation (`d30-cluster-001-relation-`). Field = the spec struct's name.
- Flavor text promises extra findings that are NEVER asked (D19-D30 every day: clones, "impossible claim", "planted
  hive", "reject malformed captures", "rebuilt from an incomplete source", "collapse duplicates", "expose the fabricated
  cluster"). Graded = the STRUCTURAL truth; names/extensions/secondary metadata are the lie. Titles pun on the field
  (D19 "Little Endian" = EI_DATA; D20 "Universal Appeal" = fat; D22 "Main Character Energy" = Main-Class; D24 "Event
  Horizon" = record count; D25 "Hive Mind" = root key; D26 "Before You Go" = Prefetch; D27 "Packet Loss Prevention" =
  packet COUNT; D28 "Where It All Began" = partition START LBA; D29 "Trust Issues" = cert fingerprint; D30 "Seeing
  Double" = identical-hash groups). Flavor depth shows up as TIMED mutations, not fields -- but D30's timed clusters
  physically CONTAIN the unasked flavor (near-duplicate copies, bad-CRC inner zips): next fields may ask for them.
- Singles: D1-9 ~27-60 s; one convention submit lost D10, D13, D15, D20; two D16. Prebuilt race HITS: D18 ~5 s, D19
  ~13, D22 ~19, D23 ~29, D26 ~29, D27 ~22, D29 ~23 s. MISSES -> live worker: D17 ~24, D21 ~32, D24 ~21, D25 ~17
  (`registry` vs `regf`), D28 ~22 (`disk` vs `gpt`), D30 ~88 s (no `relation` fmt + 3 wrong on the member LABEL).
  TT/Mastery: CORRECT every day; D15-17 + D19 after a generalize (synthesis dispatch); D23 after one wrong TT submit
  (list ORDER); since D24 first try in seconds (D30: TT 35 fields 4.3 s, Mastery 490 = 14 sets 4.7 s).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Delivery layout** -- names drift: D1-14 `metadata-day-NN-evidence[-0N].zip`; D15+ TT `evidence.zip`, Mastery
  `evidence-01.zip` holding `evidence-01..NN.zip` (see "Question-text tags / nesting"). Route by the ref's text before
  `->` and by sha256, never a hard-coded name.
- **Field-set / set count** -- D7 TT 11 / Mastery 22; D8-9 12-13 everywhere; D10-14 one; D15 1/20/100, then +1
  field/day and (from D22) +1 set/day: D22 1/27/162 (6 sets) ... D26 1/31/310 (10 -- `set10.` string-sorts before
  `set2.`: order numerically) ... D30 1/35/490 (14 sets). Enumerate `setN.` prefixes from the live ids. Families: identity + `d04-jpeg` `d05-png` `d06-pdf` `d07-zip` (eocd,
  CD names) `d09-pe` (machine, entry RVA, OriginalFilename) `d12-dotnet` `d13-msi` `d14-lnk` `d15-ooxml` `d16-email` `d17-audio` `d18-video` `d19-elf`
  `d20-macho` `d21-apk` `d22-jar` `d23-sqlite` `d24-evtx` `d25-registry` `d26-prefetch` `d27-pcap` `d28-disk`
  `d29-x509` `d30-cluster` + synthesis. Dispatch on the answer-id SUFFIX (reference solver answering all 35:
  `challenges/day30/metadata-seeing-double/solver/solve.py`; lane seed `local_answer` + `synthesis_answer` + lib.meta).
- **fmt word vs registry key vs id family** -- MISSES: D16 `email` (lib `eml`), D17/18 `media` (lib `wav`), D25
  `registry.hive_root_name` (lib `regf.root_key_name`), D28 `disk.partition_start_lba_sequence` (lib `disk` = VHD/VMDK;
  GPT walk under `gpt`.`partition_start_lbas`), D30 `relation.identical_sha256_groups` (no `relation` fmt). HITS: D26
  `prefetch.executable_name`, D27 `pcap.packet_count`, D29 `x509.sha256_fingerprint`.
  Vocabulary = the home tool (ffprobe, capinfos, sfdisk) or the spec struct; header codes ALWAYS raw `0x` hex. Rule:
  take `<fmt>.<field>` from the question (or the slug after `-NNN-`), map fmt synonyms (`email`~`eml`/`mime`;
  `media`~`audio`/`video`/`av`; `jar`~`war`; `sqlite`~`db`; `evtx`~`evt`/`eventlog`; `registry`~`regf`/`hive`;
  `prefetch`~`pf`/`scca`; `pcap`~`pcapng`/`capture`; `disk`~`gpt`/`mbr`/`partition_table`/`image`; `x509`~`cert`;
  `relation`~`corpus`/`cluster`/`dedup`/`inventory`) and field synonyms
  (`_sequence`~`_list`/plural `s`), route the extractor by MAGIC + member names, fall back to the field under any fmt.
- **Member values (D23+: EVERYTHING re-rolls every day)** -- never cache across sets/modes. Seen: identity sizes
  72-378 B (CRLF/LF, BOM in some sets), PDF `1.0`-`2.0`, zip entries 2-13, PE Machine (9 values incl. `0xaa64`
  `0x01c4` `0x5064`), audio under `audio-001.wav` (`pcm_s16le` `mp3` `opus` `vorbis` `aac` `flac`), ELF e_machine (8
  values incl. `0x0028` `0x00b7` `0x00f3`), Mach-O
  thin (LE-32/64) or FAT 2-3 slices, Main-Class 1-4 parts, SQLite page 512-65536, EVTX 3-119 records (one chunk),
  regf root `[A-Za-z0-9]{6,32}`, Prefetch WRAPPER flips (D26 single `MAM\x04` Xpress-Huffman, timed plain SCCA v30),
  PCAP classic v2.4 only (LE-us / LE-ns `4d 3c b2 a1` / BE-us `a1 b2 c3 d4`; linktype 1/101/105/147; 3-39 records,
  snapped ones count), DISK (D28, 14 images): protective MBR `ee` + GPT rev 1.0, 512-B sectors, entries @LBA2 128x128,
  valid CRCs, backup hdr at the last LBA, 61-582 KiB, 1-6 used entries contiguous from slot 0, starts 34-367, table
  order == ascending, partitions ALL ZERO (no FS/EBR/4Kn yet); X.509 (D29, 15 certs): one LF PEM block, Ed25519; corpus
  clusters (D30): see "Corpus member LABELS". Rule: decode the
  general structure (byte order from the file, every slice/chunk/entry, follow every offset, decompress any wrapper
  by its magic), never the D-day sample's constant.
- **Corpus member LABELS (D30 `relation.*`)** -- single: `delivery-manifest.json` (schema
  `huntress.artifact_delivery_manifest.v1`, per artifact `id filename path content_type family producer_id size_bytes
  sha256`; copies `producer_id: duplicate_ref`) + `artifacts/<id>.<ext>` (txt/ps1/json/png/zip, 30 members = 5 groups
  x 6, claims all TRUE). Timed (15 clusters): NO manifest, members `artifacts/<word>-NN` WITHOUT extension, CD order
  shuffled, 19-32 members, 2-5 groups of 2-6 + many singletons, each group shadowed by one NEAR-duplicate (1-2 bytes
  edited, e.g. `$ErrorActionPrfference`) and some inner zips holding a BAD-CRC member. Rule: label = manifest `id`
  (map by `path`, then `filename`), else basename minus extension; hash the REAL bytes (manifest `sha256` is a claim);
  skip the manifest; keep groups len>=2; sort inside, sort groups; compact JSON. Hash inner zips as blobs -- opening
  one with `zipfile` raises `BadZipFile` (Bad CRC) -> read raw if you must open it.
- **List ORDER under mutation (D23)** -- D8-D22 zips stored CD entries already sorted; D23 shuffled the CD and the GM
  REJECTED CD order, accepted ascending sort; fat Mach-O slices ascending `0x%08x` (fat_arch order rejected). Rule:
  `_names`/`_set`/`_targets` = sorted ascending + deduped (string sort of the emitted spelling); EXCEPT synthesis
  (digest order) and `_sequence`/"in order" fields (D28: partition-TABLE order -- integers, NEVER string-sorted:
  `[86,117]` string-sorts to `[117,86]`). Always `json.dumps(v, separators=(",",":"))` -- never `str()` a list.
- **Identity member roster** (D15+) -- `evidence-note*.txt`, `evidence-note-copy*.txt`, `roster*.csv` (timed names
  may carry `-<6hex>`; ids keep the bare stem): ids `<stem>-{filename,size-bytes,md5,sha1,sha256,magic-prefix-hex-16,
  text-utf8-bom-present}`; filename artifact = the container only -> map the stem by PREFIX. Sets may lack a member
  (D25) or ask a DIFFERENT 7 of the 21 identity ids (D26+) -- answer exactly the ids each set lists.
- **Synthesis / cross-member** (D15+) -- id `metadata-day-NN-synthesis-<algo>-order` (TODAY's NN), kind `json`, norm
  `case_insensitive`, "Compute the full-file SHA-256 digest of each named file, then submit a compact JSON array of
  their filenames in ascending digest order. Files: [...]". Rule: regex `Files:\s*(\[.*?\])`, hash each under the
  ref's container, sort by hex digest -- `lib.meta.synthesis.digest_order(question, get_bytes, algo)`, get_bytes bound
  INSIDE the per-set worker. 4-6 names (note + kit members + TODAY's member), differing per set and vs the 409
  contract -- parse each set's own text, never assume a length. Only sha256 seen.
- **Decoys** -- renamed copies, misleading extensions, secondary metadata (EXIF, catalog /Version, regf FileName
  @0x30): answer from the structure the field names; `elf.*` of an `MZ` member = `none`.
- **Answer kinds** -- `exact_text`, `integer`, `pattern` (hashes case-insensitive; `0x`-hex `trim` only -> lowercase),
  `enum` (`accepted_values`), `json` (compact array; `*_set`/`*_names`/`*_sequence` = a list even with ONE element).
- **Question-text tags / nesting** -- D9 ` [assigned-artifact-sha256:<hex>]` suffix, D15+ ``Inspect `<member>`. ``
  prefix: strip, route by id + `artifact`. The asked file may sit 2-3 zips deep (D7): resolve by the name after `->`;
  OOXML/APK/JAR members ARE zips -- parse them as the member (Mastery layout: see "Delivery layouts").

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
| `prefetch.*` / `.pf` (`SCCA` @4, version u32 @0: 17/23/26/30/31; `MAM` @0 = Win10+ compressed) | `MAM` + type byte (low nibble 4 = Xpress-Huffman; 0x80 = CRC32 u32 follows), uncompressed size u32 @4, stream @8 (@12 with CRC) -> decompress FIRST. SCCA: file size u32 @12, exe name UTF-16LE @16 (60 B, NUL-terminated), path hash u32 @0x4C; run count / 8 last-run FILETIMEs / volumes per version. `.venv` `dissect.util.compression.lzxpress_huffman.decompress(b[8:])` (worker), `lib/meta/prebuilt/prefetch.py` (pure-Python, in-window) |
| `pcap.*` / `.pcap` `.cap` (`d4 c3 b2 a1` LE-us, `4d 3c b2 a1` LE-ns, `a1 b2 c3 d4` / `a1 b2 3c 4d` BE; pcapng `0a 0d 0d 0a`) | byte order FROM THE MAGIC; 24-B global hdr: ver u16 @4/@6 (2.4), snaplen u32 @16, linktype u32 @20; records = 16-B hdr {ts_sec, ts_frac, incl_len @+8, orig_len @+12} + incl_len bytes -> `packet_count` = complete records walked (D27). pcapng: walk blocks {type u32, len u32 ... len}, SHB `0a0d0d0a` BOM `1a2b3c4d` @8 sets order per section, count EPB 6 / SPB 3 / OPB 2. `capinfos -M f` / `tshark -r f \| wc -l` cross-check; `lib/meta/prebuilt/pcap.py` |
| `disk.*` / `gpt.*` / `mbr.*` / `.img` `.dd` `.raw` `.001` (`55 aa` @0x1FE; `EFI PART` @512 or @4096) | protective MBR type `ee` @0x1C2 -> GPT: entry LBA u64 @hdr+72, count u32 @+80, size u32 @+84; each entry {type GUID 16, unique 16, first LBA u64 @+32, last @+40, attrs @+48, name UTF-16LE @+56}; skip all-zero type GUID; keep TABLE order (D28 `partition_start_lba_sequence` = JSON ints). No GPT -> MBR 4x16 B @0x1BE {type @+4, start u32 @+8, count @+12}, types 05/0f/85 -> walk the EBR chain (logical start = EBR LBA + rel). `sfdisk -d f.img` / `fdisk -l f.img` / `sgdisk -p f.img` / `mmls f.img` cross-check. In-window: `lib/meta/prebuilt/vbr.py` (`gpt`/`mbr` fmts) + the D28 solver's `disk_partition_starts` |
| `dotnet.*` / Mono assembly | data dir 14 -> CLI header -> `BSJB` -> `#~` -> Module row 0 Mvid (1-based #GUID idx) -> `uuid.UUID(bytes_le=..)`. `lib/meta/dotnet.py` |
| `msi.*` / `.msi` (OLE `d0 cf 11 e0`) | fast: `strings -n 6 x.msi \| grep -aoE 'ProductCode\{[0-9A-F-]{36}\}'`; exact: CFB `!_StringPool`/`!_StringData` -> `!Property`. `olefile` in venv |
| `lnk.*` / `.lnk` (`4c 00 00 00` + CLSID 00021401) | LinkFlags @0x14 (0x1 IDList, 0x2 LinkInfo, 0x80 Unicode); target = LinkInfo LocalBasePath (+CommonPathSuffix) verbatim, else IDList. `lib.meta.lnk:target_path` |
| `ooxml.*` / `.docx/.xlsx/.pptx` (`PK` + `[Content_Types].xml`) | External = `TargetMode="External"` in EVERY `*.rels` part; `unzip -p f.docx '*.rels' \| grep -o 'Target="[^"]*" TargetMode="External"'`; sorted |
| `email.*` / `.eml` | `grep -ai '^message-id' f.eml`; `lib.meta.prebuilt.eml.eml_value(data, {"field": f})`. Values VERBATIM (Message-ID keeps `<...>`) |
| `media.*` audio (`RIFF..WAVE`, `ID3`/`ff fb`, `OggS`, `fLaC`, `ftyp`, `1a 45 df a3`, `FORM..AIFF`) | route by MAGIC (D23 TT/Mastery: WAV, MP3, Ogg Opus, Ogg Vorbis all appeared under `audio-001.*`). WAV tag -> FFmpeg names (Conventions); Ogg: first packet `OpusHead` -> `opus`, `\x01vorbis` -> `vorbis`. Truth: bundled `ffmpeg -hide_banner -i f` |
| `media.*video*` / MP4-MOV (`....ftyp`), MKV/WebM, AVI | box walk `moov` -> first `trak` whose `mdia/hdlr` = `vide` -> `stsd` entry: w,h u16 BE @entry+32; cross-check tkhd, SPS crop. `lib.meta` fmt `media` |
| `*-synthesis-<algo>-order` / "Files: [...]" in the question | parse the list from the question text, hash each member of the same container, sort by digest, compact JSON of names |
| `x509.*` / `.pem .crt .cer .der` (`-----BEGIN CERTIFICATE-----` or DER `30 82`) | fingerprint = hash of the DER (decode the PEM base64 body), lowercase hex, no colons: `openssl x509 -in f -noout -fingerprint -sha256`; fields via `openssl x509 -noout -text`; `lib/meta/prebuilt/x509.py` (D29 HIT) |
| `relation.*` / a corpus zip (`cluster-NNN.zip`, `delivery-manifest.json`, many `artifacts/*`) | one pass over `infolist()`: sha256 of REAL bytes per member, label = manifest `id` (by path/filename) else extensionless basename; skip the manifest; groups len>=2 sorted inside + sorted; compact JSON. Manifest `sha256`/`size_bytes`/`producer_id` are CLAIMS to check, not answers (D30) |
| GUID field (`*-guid`) | spelling follows the SOURCE: stored string (MSI) verbatim braces+uppercase; binary (.NET) -> lowercase, no braces |
| exe-extension decoy (`MZ` without `PE\0\0` at e_lfanew) | literal `none` if the syntax offers it; never fall back to a later `PE\0\0` hit |
| "impostor", "renamed", "mislabeled", "embedded" | trust magic bytes at offset 0 of the NAMED member; a matching string deeper in the file is a decoy |
| answer_format kind `json` | `json.dumps(sorted(v), separators=(",",":"), ensure_ascii=False)` unless the field is an order (synthesis, `_sequence`); integer lists stay ints |
| Mastery `set1.`..`setN.` ids | resolve each set's container separately; see delivery layouts |

## Day by day
**Days 1-14** (one field each, all timed first try): D1 identity -> D2 `magic-prefix-hex-16` -> D3 BOM -> D4 JPEG SOFn
`<w>x<h>` -> D5 PNG IHDR -> D6 `pdf.header_version` `x.y` -> D7 `zip.eocd_total_entries` of the INNER zip -> D8 CD names
(compact JSON; disk order happened to be sorted) -> D9-11 one Go PE: `coff_machine_u16_hex` `0x014c`, entry RVA
`0x%08x` (unpadded REJECTED), `version_original_filename` verbatim -> D12 `dotnet.mvid_guid` (`uuid.UUID(bytes_le)`
lowercase, no braces) -> D13 `msi.product_code_guid` (stored WITH braces; brace-less REJECTED) -> D14 `lnk.target_path_windows`.

**Days 15-28** (single = 1 new-family field; TT/Mastery = cumulative kit + synthesis): D15 `ooxml.external_relationship_
targets` (rels `TargetMode="External"` Targets SORTED). D16 `email.message_id` (VERBATIM with `<>`; 2 lost). D17
`media.primary_audio_codec_name` (`pcm_s16le`). D18 `media.primary_video_dimensions` (`320x180`). D19 "Little Endian"
`elf.e_machine_u16_hex` (`0x003e`). D20 "Universal Appeal" `macho.cpu_type_set` (`["0x0100000c"]`). D21 "Package Deal"
`apk.package_name` (AXML `package`, not label). D22 `jar.main_class` (verbatim). D23 "Page Me Maybe"
`sqlite.page_size_bytes` (u16 BE @16, `1` = 65536; timed kit MUTATED -> 1 wrong TT on CD-order names). D24 "Event
Horizon" `evtx.record_count` (walk every chunk). D25 "Hive Mind" `registry.hive_root_name` (root nk name; FileName
@0x30 = DECOY). D26 "Before You Go" `prefetch.executable_name` (`MAM\x04` -> SCCA, `CMD.EXE`). D27 "Packet Loss
Prevention" `pcap.packet_count` (record walk). D28 "Where It All Began" `disk.partition_start_lba_sequence` (protective
MBR `ee` -> `EFI PART` @LBA1 -> entries from the HEADER's lba/count/size, non-zero type GUID, first LBA u64 @+32 in
TABLE order as JSON ints `[34]`; partitions all zero; race MISS: lib `disk` = VHD/VMDK detector). Live ~17-32 s, race
hits ~13-29 s; timed first try since D24.

**Day 29 — Trust Issues** (`x509.sha256_fingerprint` of `certificate-001.pem`, kind `pattern` 64 hex,
`case_insensitive`). Artifact: 709-B PEM, ONE `BEGIN CERTIFICATE` block, LF, Ed25519 (`06 03 2b 65 70`) self-made
cert; timed 15 certs all the same shape. Answer = sha256 of the DER (base64 body between the armor lines, decoded) --
`openssl x509 -in f.pem -noout -fingerprint -sha256 | tr -d :` lowercase. Prebuilt `lib/meta/prebuilt/x509.py` HIT the
race: CORRECT ~23 s, 0 wrong; TT 34 / Mastery 442 (13 sets) first try. Flavor (unasked): "Certificates appear in
binaries, packages, mail, captures, and disk images. Fingerprint each one, collapse duplicates, and identify the trust
claim unsupported by evidence."

**Day 30 — Seeing Double** (`relation.identical_sha256_groups` for `cluster-001.zip`, id
`d30-cluster-001-relation-identical-sha256-groups`, kind `json` "compact valid JSON array with exact values and
order", `case_insensitive`). Prompt: "The corpus is too large for manual browsing. Build a relationship map from exact
identity, semantic identity, containment, and claimed provenance -- then expose the fabricated cluster."
- Artifact: `metadata-day-30-evidence.zip` (2 KB) -> `cluster-001.zip` (18 000 B, STORED) = `delivery-manifest.json`
  + 30 `artifacts/{alpha,bravo,charlie,delta,echo}-0[1-6].{txt,ps1,json,png,zip}`; each family's 6 files byte-identical
  (manifest: `-01` producer `text_template`/`structured_image`/`structured_zip`, `-02..06` `duplicate_ref`; every
  claimed sha256/size matched the bytes). Answer = 5 groups of 6 manifest ids.
- Insight: the corpus question is about RELATIONS between members; the label of a member is the manifest's `id`
  (no `artifacts/` path, no extension). Group by sha256 of real bytes, drop singletons, sort.
- Tools: python `zipfile` + `hashlib` over `infolist()` (one pass); `unzip -l`, `sha256sum artifacts/* | sort` to eyeball;
  `jq -c '.artifacts[] | [.id,.sha256,.producer_id]' delivery-manifest.json`.
- GM spelling: `[["alpha-01",...,"alpha-06"],...]` ACCEPTED; `"artifacts/alpha-01.txt"` paths REJECTED; `"alpha-01.txt"`
  basenames REJECTED. Timed (no manifest) labels = the extensionless member basename `["copper-25","estuary-14",...]`.
- Time: race had no `relation` fmt (complete=false) -> live worker CORRECT ~88 s with 3 wrong (path, basename, and an
  EMPTY submit from a jq path typo). TT 35 / Mastery 490 (14 sets) first try, 4.3 / 4.7 s, no generalize.

## GM answer conventions learned
- Filenames: exact base name incl. extension, no directory. Sizes/counts: base-10 integer, no units. Hashes: hex, any
  case. Byte prefixes: lowercase hex, contiguous, exactly 2N chars (`xxd -p -l N`). Booleans: enum `true` / `false`.
- Pixel dimensions (JPEG SOF, PNG IHDR, video D18): `<width>x<height>`, lowercase `x`; video = ffprobe v:0 coded size.
- PDF header version: bare `x.y` (absent -> `none`, unconfirmed). `_bytes` sizes = decoded integer (`1` -> `65536`, D23).
  `evtx.record_count` = records actually present (chunk walk, D24); `pcap.packet_count` = complete libpcap records
  walked (D27; snapped incl_len < orig_len records count; pcapng = EPB+SPB+OPB, unverified).
- Stored strings VERBATIM (no quotes, case kept, delimiters kept): PE StringFileInfo (D11), LNK path (D14), OOXML
  Target (D15), Message-ID WITH `<>` (D16), `package` (D21), `Main-Class` (D22), root nk name (D25: no `\`/`HKEY_*`),
  SCCA exe name (D26: uppercase as stored, `.EXE` kept, not the `.pf` stem).
- JSON lists -- compact, double quotes, SORTED (CD names D23, rels targets D15, `cpu_type_set` `"0x%08x"`); ORDER
  fields keep their order (synthesis = digest order; D28 `_sequence` = TABLE order, JSON INTEGER sectors `[34]`).
- Header integers as hex (`*_hex`): `0x` + lowercase hex ZERO-PADDED to the struct field's width (u16 `0x014c`
  `0x003e`, u32 `0x00065bd0`, Mach-O `0x0100000c` even without `_hex`). Width from the STRUCT / `_uNN_`; value in the
  file's own byte order. (Magic-prefix hex has NO `0x`; the binary lane wants `i386` -- different generator.)
- GUIDs follow the source: .NET MVID lowercase no braces (D12); MSI ProductCode stored string uppercase WITH braces (D13).
- Media codec names: ffprobe `codec_name` (WAV tag 1 -> `pcm_u8`/`pcm_s16le`/`pcm_s24le`/`pcm_s32le` by bits, 3
  `pcm_f32le`, 6 `pcm_alaw`, 7 `pcm_mulaw`, 0x55 `mp3`; MP3 `mp3`; Ogg `opus`/`vorbis` -- all GM-accepted).
- Corpus labels (D30): a member is named by its manifest `id` (`alpha-01`), never the zip path (`artifacts/alpha-01.txt`)
  or the basename (`alpha-01.txt`) -- both REJECTED; no manifest -> the extensionless basename. Groups = JSON array of
  arrays, each inner list sorted, outer list sorted (by first id). Cert fingerprints (D29): DER sha256, hex, no `:`.
- Rejected: `0x65bd0` (D10 unpadded); brace-less MSI GUID (D13); rels-order targets (D15); bracket-less Message-ID
  (D16); `["arm64"]` (D20); CD-order names (D23); Python repr `['a', 'b']` for any json (D23); zip paths and
  basenames as corpus labels (D30).
- Inference: the field id IS the spec name (`sof_`, `eocd_total_entries` = the EOCD's own claim, `e_machine`,
  `page_size`, libscca `executable_name`) -- read it literally to pick the structure; header CODES are raw `0x` hex.

## Pitfalls that cost time
- **Carry-over mutation (D23, 1 wrong TT submit + a Mastery generalize)**: an extractor that only ever saw one sample
  value is untested. Before a timed run, ask of every carried field "what if this is the multi-element / other-endian
  / other-codec / compressed-or-not case?" -- fat Mach-O, shuffled CD, Ogg audio, non-x86 machines arrived the same day.
- **json list output**: sort + compact `json.dumps` at ONE choke point (D23 Mastery: a local Python list got `str()`'d).
- **Corpus LABEL guessing (D30, 2 wrong + 1 empty, ~60 s)**: when the answer names members of a set, look for a
  manifest/index inside the container FIRST and use its `id` key; print the exact string you will submit and refuse to
  submit an empty value (a jq path typo sent `""` -- it counts as a wrong attempt).
- **Synthesis dispatch** (lost D15-17, D19): start the day's solver from the lane seed (`local_answer` +
  `synthesis_answer` -> `lib.meta.synthesis.digest_order`, artifacts root set INSIDE `_solve_pairs`; one process/set).
- **Registry misses** (6 days, see the fmt-word axis; D28 fmt COLLISION -- a fmt hit is not enough, its detector must
  accept today's MAGIC; D30 a corpus-level field has no single-member magic at all): grep the field's last words under
  EVERY fmt -- `python3 -c "import lib.meta as m; print([k for k in m.known_fields() if k[0]=='<fmt>'])"` + grep
  `lib/meta/prebuilt/*.py`. Shape trap (D20): `cpu_type_set` hit scalar `cpu_type` -- `_set`/`_list`/`_names` = a list.
- Unwired template (D22) / id slugs (D16, 1 wrong): `--from-solver` before today's field is dispatched emits `none`;
  ids repeat the fmt word (`d16-email-001-email-message-id`) -> anchor `-\d+-<fmt>-(.+)$`. `none` = absent in the
  bytes, never "my parser returned None".
- Format traps (details in the cue table): byte order from the file (fat + SQLite always BE, MBR/GPT always LE); EVTX
  = walk every chunk; regf offsets +0x1000; Prefetch `MAM` before `SCCA`; GPT geometry from the HEADER (512/4096).
- A pre-fetched TT/Mastery `contract.json` is the 409 `start_required` body (questions, NO `answer_ids`; Files lists
  and member numbering differ from the live attempt); answer under the live ids. The flavor never widens the field.
- Container-of-containers: a naive `rfind(PK\x05\x06)` reads the OUTER EOCD -- resolve the named member first.
  Decoys (`*-with-bom.txt`, `.exe` that is text, `.bin` that is PDF): bytes win; require the format's magic (else `none`).
- Timed windows are seconds, mostly GM round-trips: parse in memory, never shell out in-window, decompress once.
- Tools: exiftool, poppler, qpdf, mutool, pdf-parser, pdfid, pngcheck, zsteg, binwalk, foremost, mediainfo, sqlite3,
  readelf/objdump, aapt/apktool/jadx, openssl, sfdisk/fdisk/sgdisk, TSK `mmls`/`fls`/`icat`, qemu-img (`source
  bin/env.sh`); .venv (worker-only, not in the prebuild gate): olefile, oletools, pefile, pyelftools, LnkParse3, dnfile,
  mutagen, androguard, python-evtx, regipy, dissect.util. ffmpeg 7.0.2 under `tools/imageio_ffmpeg_pkg/` (not on
  PATH). NOT installed: ffprobe, sox, parted, ewfinfo, pytsk3, ssdeep/ppdeep/tlsh (fuzzy hashing -> write it).
