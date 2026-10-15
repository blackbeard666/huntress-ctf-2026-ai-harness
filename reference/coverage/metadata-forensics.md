# metadata-forensics — coverage atlas (as of D15, 2026-10-15)

What the lane might ask next vs what we can already answer. Grammar is always `Determine <fmt>.<field> for <member>`;
id `dNN-<fmt>-NNN-<fmt>-<field>`; the registry is `lib.meta` (built-ins = verified/speculative, plus
`lib/meta/prebuilt/*.py` speculative modules ranked in `lib/meta/prebuilt/TARGETS.json`). Check what exists with
`python3 -c "import lib.meta as m; print(sorted(k for k in m.known_fields() if k[0]=='<fmt>'))"`.

**Status:** `seen Dn` = GM-verified that day (built-in, verified tier) · `prebuilt <module>` = speculative extractor
registered (gate passed) · `partial` = some sibling fields registered · `gap` = nothing registered (TARGET name given
when one exists but is not built yet).
**Tools:** (I) = installed (`.venv/bin/python` import or on the `source bin/env.sh` PATH), (M) = missing.
In-window extractors may only import the prebuild gate's `ALLOWED_IMPORTS` (`hctf/prebuild.py:82`: stdlib subset +
`pefile elftools capstone Crypto androguard pyzipper lib`) and may NOT call `open()` -- so Evtx / regipy / olefile /
oletools / dnfile / LnkParse3 / lief / cryptography / asn1crypto / dpkt / PIL / `sqlite3` / `mailbox` / `wave` are
worker-only (LLM side) until the allowlist is widened. See gaps `gate-allowlist-*`.
**Likelihood** reasoning: D9-D15 walked Windows binaries/installers/shortcuts/Office (PE -> PE version -> .NET -> MSI
-> LNK -> OOXML); the next steps are most plausibly other Windows DFIR artifacts and legacy-Office/CFB siblings,
plus deeper fields of already-seen families (timed kits are cumulative, D15 added cross-file synthesis).

## 1. Atlas

| # | Concept / field | Status | Recognition cues | Standard tool / lib + exact call | D16+ likelihood |
|---|---|---|---|---|---|
| 1 | Identity: filename / size / md5 / sha1 / sha256 | seen D1 (+D15 member roster) | any member; id stem names WHICH member | `hashlib.<algo>(b).hexdigest()`; `sha256sum` (I) | high -- every timed kit |
| 2 | `file.magic_prefix_hex_N` | seen D2 | first N bytes | `xxd -p -l 16` (I); `b[:N].hex()` | high (carry-over) |
| 3 | `text.utf8_bom_present` (utf16 sibling speculative) | seen D3 | `ef bb bf` / `ff fe` / `fe ff` | `b.startswith(codecs.BOM_UTF8)` | high (carry-over) |
| 4 | `jpeg.sof_dimensions_pixels` | seen D4 | `ff d8 ff`; SOFn `ffc0..ffcf` minus c4/c8/cc | segment walk; `identify -format %wx%h` (I) | high (carry-over) |
| 5 | `png.ihdr_dimensions_pixels` | seen D5 | `89 50 4e 47 0d 0a 1a 0a`; IHDR @12 | `struct.unpack('>II', b[16:24])`; `pngcheck -v` (I) | high (carry-over) |
| 6 | `pdf.header_version` | seen D6 | `%PDF-x.y` @0 | `b[5:8]`; `pdfinfo` (I) | high (carry-over) |
| 7 | `zip.eocd_total_entries` | seen D7 | `PK\x05\x06` last; u16 @+10 | struct; `7z l -slt` (I) | high (carry-over) |
| 8 | `zip.central_directory_member_names` (CD order) | seen D8 | `PK\x01\x02` walk, name @+46 | `zipfile.ZipFile(io.BytesIO(b)).namelist()` | high (carry-over) |
| 9 | `pe.coff_machine_u16_hex` | seen D9 | `MZ`, e_lfanew @0x3C, `PE\0\0` | `pefile.PE(data=b).FILE_HEADER.Machine` (I) | high (carry-over) |
| 10 | `pe.address_of_entry_point_rva_hex` | seen D10 | opt hdr +16 | `pe.OPTIONAL_HEADER.AddressOfEntryPoint` (I) | high (carry-over) |
| 11 | `pe.version_original_filename` (+ `pe.version_*` family) | seen D11 | RT_VERSION, `VS_VERSION_INFO` UTF-16 | `pe.FileInfo[..].StringTable[0].entries` (I); `exiftool -j` (I) | high (carry-over) |
| 12 | `dotnet.mvid_guid` | seen D12 | data dir 14 -> `BSJB` -> `#GUID` | `lib.meta.dotnet`; `dnfile.dnPE(data=b)` (I) | high (carry-over) |
| 13 | `msi.product_code_guid` (+ Property siblings speculative) | seen D13 | `d0 cf 11 e0 a1 b1 1a e1` + `!_StringPool` | `lib.meta.msi`; `tools/msitools/usr/bin/msiinfo export x.msi Property` (I, not on PATH) | high (carry-over) |
| 14 | `lnk.target_path_windows` | seen D14 | `4c 00 00 00` + CLSID `01 14 02 00 ...46` | `lib.meta.lnk`; `LnkParse3.lnk_file(io.BytesIO(b)).get_json()` (I) | high (carry-over) |
| 15 | `ooxml.external_relationship_targets` (sorted) | seen D15 | `PK` + `[Content_Types].xml`; `*.rels` `TargetMode="External"` | `zipfile` + `xml.etree` over every `.rels` | high (carry-over) |
| 16 | Synthesis: `metadata-day-NN-synthesis-sha256-order` | seen D15 | id `*-synthesis-<algo>-order`, `Files: [...]` in text | day15 solver `_digest_order`; `hashlib.new(algo)` | high -- expect md5/sha1/size siblings |
| 17 | PE COFF/optional header: TimeDateStamp, NumberOfSections, Subsystem, Characteristics, DllCharacteristics, SizeOfImage, CheckSum, section names | prebuilt pe | COFF @e_lfanew+4; opt @+24 | `pe.FILE_HEADER.TimeDateStamp`, `[s.Name.rstrip(b'\0') for s in pe.sections]` (I) | high -- natural PE sibling |
| 18 | PE VS_FIXEDFILEINFO file/product version, flags, OS | prebuilt pe | `bd 04 ef fe` signature in RT_VERSION | `pe.VS_FIXEDFILEINFO[0].FileVersionMS` (I) | med |
| 19 | .NET assembly name/version/culture/PKT, module name, runtime `v4.0.30319`, TypeDef count | prebuilt dotnet | `BSJB` root, `#~` stream | `dnfile.dnPE(data=b).net.mdtables.Assembly[0]` (I); `ilspycmd` (I) | high -- .NET sibling |
| 20 | MSI SummaryInformation: PackageCode (PID 9), Title, Author, Template `Intel;1033`, PageCount; ProductVersion/UpgradeCode | prebuilt msi | `\x05SummaryInformation` stream in CFB | `olefile.OleFileIO(b).get_metadata()` (I); `msiinfo suminfo` (I) | med-high |
| 21 | CAB CFHEADER folders/files/setID/cbCabinet/version, CFFILE names | prebuilt cab | `MSCF` @0 | struct; `7z l -slt x.cab` (I); `gcab -t` (I msitools) | med (MSI embeds cabs) |
| 22 | LNK header: LinkFlags, FileAttributes, C/A/W FILETIMEs, FileSize, show cmd, hotkey, args, working dir | prebuilt lnk | header 0x4C bytes; times @0x1C/0x24/0x2C | `LnkParse3` (I); `exiftool -j` (I) | high -- LNK siblings |
| 23 | LNK LinkInfo volume label/serial/drive type, net path, IDList path, env block, icon, TrackerDataBlock machine id/droid | prebuilt lnk | LinkInfo flags; ExtraData sigs `0xA0000001` env, `0xA0000003` tracker | `LnkParse3 ... ['link_info']`, `['extra']` (I) | high |
| 24 | Windows `.url` InternetShortcut `URL=` / `IconFile=` | gap | text `[InternetShortcut]` | `configparser` / regex | med (shortcut sibling) |
| 25 | EVTX file header: chunk count, next record id, first record id, version | prebuilt evtx | `ElfFile\0` @0; `ElfChnk\0` @0x1000 | struct; `evtx_info` (I) | high |
| 26 | EVTX records: count, EventID, TimeCreated, Provider, Channel, Computer, EventRecordID | gap (target evtx-records) | record magic `2a 2a 00 00`; BinXML | `Evtx.Evtx.FileHeader(b,0).chunks()` -> `rec.xml()` (I, worker-only); `evtx_dump.py` (I) | high -- top DFIR artifact |
| 27 | EVTX semantic: 4624 LogonType/TargetUserName/IpAddress, 4688 NewProcessName/CommandLine, 7045 ServiceName/ImagePath, 4104 ScriptBlockText, 1102 clear | gap | `<EventID>4624</EventID>` in record XML | as #26 + `xml.etree` on `rec.xml()`; `evtx_filter_records` (I) | med-high |
| 28 | Registry hive base block: seq numbers, last written, hive name, version, root key | prebuilt regf | `regf` @0; FILETIME @0x0C; name @0x30 UTF-16; `hbin` @0x1000 | struct; `regipy` (I, path-only) | high |
| 29 | Registry values: Run/RunOnce, key last-write, subkey/value counts, specific value data | gap (target regf-values) | `nk`/`vk`/`lf`/`lh`/`ri` cells | `RegistryHive(path).get_key(r'\Software\...\Run').get_values()` (I, needs a path); `python-registry` (M) | high |
| 30 | UserAssist (ROT13 names, run count, focus, last run), RecentDocs MRU, ShellBags, TypedPaths, WordWheelQuery | gap | NTUSER.DAT / UsrClass.dat; GUID `{CEBFF5CD-...}\Count` | `codecs.decode(name,'rot13')`; regipy plugins `regipy-plugins-run` (I) | med |
| 31 | SYSTEM/SOFTWARE facts: ComputerName, TimeZoneKeyName, USBSTOR serials, ProductName/InstallDate, network profiles | gap | SYSTEM `ControlSet001\...`; SOFTWARE `Microsoft\Windows NT\CurrentVersion` | regipy `get_key().get_value('ComputerName')` (I) | med |
| 32 | ShimCache (AppCompatCache value; Win10 entries tagged `10ts`) | gap | SYSTEM `...\Session Manager\AppCompatCache` binary blob | regipy `shimcache` plugin (I) | med |
| 33 | Amcache.hve InventoryApplicationFile: FileId `0000<sha1>`, LowerCaseLongPath, LinkDate | gap | regf named Amcache.hve; `Root\InventoryApplicationFile` | regipy `amcache` plugin (I) | med |
| 34 | `.reg` export text (`Windows Registry Editor Version 5.00`, UTF-16LE) | gap | `ff fe 57 00 69 00` | `b.decode('utf-16')` + regex | low-med |
| 35 | Prefetch: exe name, run count, last-run times (1 or 8), volume serial/path, prefetch hash | gap (target prefetch) | `SCCA` @4, version @0 (17/23/26/30/31); Win10 `MAM\x04` compressed | struct after decompress; `pyscca`/`windowsprefetch` (M); LZXpress-Huffman needs `dissect.util` (M) | high -- classic exec artifact |
| 36 | Recycle Bin `$I`: original path, deletion FILETIME, original size | gap (target jumplist-recycle-mft) | v1 `01 00..` path @24 (520 B); v2 `02 00..` len @24 path @28 | `struct.unpack_from('<QQQ', b)`; UTF-16 path | high -- tiny, deterministic |
| 37 | Jump list AutomaticDestinations: AppID (filename 16 hex), DestList entries (path, access time, pin), embedded LNK streams | gap | CFB `d0cf11e0` with `DestList` stream + hex-named streams | `olefile.OleFileIO(b).listdir()` (I) + #22 on each stream; `JLECmd` (M) | med-high (OLE+LNK combo) |
| 38 | CustomDestinations-ms (concatenated LNKs) | gap | `ab fb bf ba` footer; LNK headers inside | carve `4c000000 01140200` then #22 | low-med |
| 39 | $MFT FILE record: $SI vs $FN MACB (timestomp), name, record #, parent ref, resident data | gap | `FILE0` @0, 1024 B; attrs 0x10/0x30/0x80 | struct; `analyzeMFT` / `mft` (M) | med |
| 40 | $UsnJrnl:$J USN_RECORD_V2: filename, reason flags, timestamp | gap | RecordLength u32, MajorVersion 2 @4, name off @0x3A | struct walk (skip zero runs) | low-med |
| 41 | SRUM (SRUDB.dat ESE): app/network usage | gap | ESE magic `ef cd ab 89` @4 | `libesedb`/`dissect.esedb` (M) | low (no lib) |
| 42 | Scheduled task XML: Actions/Exec/Command+Arguments, Author, RegistrationInfo/Date, URI, Triggers, Principal | gap | UTF-16LE BOM + `<Task version=` `mit/task` ns | `xml.etree.ElementTree.fromstring(b.decode('utf-16'))` | high -- persistence, trivial |
| 43 | WMI repository persistence (CommandLineEventConsumer, FilterToConsumerBinding) | gap | `OBJECTS.DATA`; ASCII/UTF-16 consumer strings | `strings -e l` + regex; PyWMIPersistenceFinder (M) | low |
| 44 | Thumbs.db / thumbcache_*.db entries | gap | Thumbs.db = CFB `Catalog` stream; thumbcache `CMMM` | olefile (I); struct for CMMM | low |
| 45 | Windows Timeline ActivitiesCache.db (Activity AppId/StartTime) | gap | SQLite + `Activity` table | `sqlite3` deserialize (I, worker-only) | low |
| 46 | PE debug dir CodeView RSDS: PDB path, GUID, age | gap (target pe-debug-rich-imports REJECTED: `import ordlookup`) | data dir 6; `RSDS` + GUID + age + path | `pe.DIRECTORY_ENTRY_DEBUG[0].entry.PdbFileName` (I) | high -- classic PE attribution |
| 47 | PE Rich header (comp ids, xor key, rich hash md5) | gap (same rejected target) | `Rich` + key after DOS stub; `DanS` xor | `pe.parse_rich_header()`, `pe.get_rich_header_hash()` (I) | med-high |
| 48 | PE imports/exports: imphash, import DLL names, export names, DLL name | gap (same rejected target) | data dirs 0/1 | `pe.get_imphash()`; `pe.DIRECTORY_ENTRY_IMPORT` (I) | high |
| 49 | PE Authenticode: signer CN, issuer, serial, signing time, cert thumbprint, `is signed` | gap | data dir 4 = FILE OFFSET; `WIN_CERTIFICATE` rev 0x0200 type 2 | `lief.parse(b).signatures[0].signers[0]` (I); `asn1crypto.cms` (I); `osslsigncode` (M) | high -- next PE step |
| 50 | PE resources: manifest requestedExecutionLevel, resource types/langs, icon hash | gap | data dir 2; RT_MANIFEST 24 | `pe.DIRECTORY_ENTRY_RESOURCE.entries` (I) | med |
| 51 | PE section entropy / overlay offset+size / TLS callbacks | gap | sections; data beyond last raw end | `s.get_entropy()`, `pe.get_overlay_data_start_offset()` (I) | med |
| 52 | OLE CFB legacy Office SummaryInformation / DocumentSummaryInformation (Company, Category) | prebuilt ole (DocSummary = gap) | `d0cf11e0`; `\x05SummaryInformation`, `\x05DocumentSummaryInformation` | `olefile.OleFileIO(b).get_metadata()` (I); `exiftool -j` (I) | high -- CFB sibling of MSI/OOXML |
| 53 | OLE directory: stream names, root CLSID, entry mtimes, sector size | partial (ole `stream_names`) | CFB header @0, dir sector | `ole.listdir()`, `ole.root.clsid`, `ole.getmtime(name)` (I) | med |
| 54 | VBA project: module names, `AutoOpen`/`Document_Open`, PROJECT stream, VBA stomping (p-code vs source), `vbaProject.bin` in OOXML | gap | `_VBA_PROJECT`, `dir` stream (compressed), `Attribut` | `oletools.olevba.VBA_Parser('x', data=b).extract_macros()` (I); `olevba --json` (I venv) | high -- malware-doc staple |
| 55 | OOXML custom props (`docProps/custom.xml`), remote template injection (`settings.xml.rels` attachedTemplate), `vbaProject.bin` presence, content-type of main part | partial (core/app prebuilt; custom/template gap) | `PK` + `docProps/custom.xml`; `word/_rels/settings.xml.rels` | `zipfile` + `xml.etree` | high -- direct D15 sibling |
| 56 | OOXML embedded objects / OLE (`word/embeddings/oleObject1.bin`), DDE fields | gap | zip member under `embeddings/` | `msodde` (I venv); olefile on member (I) | med |
| 57 | RTF: `\objdata` OLE1 objects (class name, payload), `\*\template`, `{\info \author}` | gap | `{\rtf1` | `oletools.rtfobj.RtfObjParser(b).parse()` (I); `rtfobj` (I venv) | med |
| 58 | OneNote `.one` embedded file (FileDataStoreObject) | gap | GUID `e4525c7b-8cd8-a74d-aeb1-5378d02996d3` header; `e716e3bd 6526 1145 a4c4 8d4d0b7a9eac` | struct carve | low-med |
| 59 | PDF Info dict (Title/Author/Creator/Producer/CreationDate), page count, catalog /Version, %%EOF count (incremental updates), /Encrypt | gap (target pdf-info) | `trailer`/`/Info N 0 R`; xref streams need zlib | `pdfinfo`, `qpdf --json` (I); `pypdf` (M) | med-high -- D6 family |
| 60 | PDF active content: /JavaScript, /OpenAction, /Launch, /EmbeddedFile names, /URI | gap | names in objects (maybe in ObjStm) | `pdfid` / `pdf-parser -s javascript` (I); `mutool show` (I) | med |
| 61 | JPEG EXIF: Make/Model/DateTimeOriginal/Orientation/Software, GPS lat/lon | gap (target exif) | APP1 `ff e1 .. Exif\0\0` + TIFF `II*\0`/`MM\0*` | `PIL.Image.open(io.BytesIO(b)).getexif().get_ifd(0x8825)` (I, worker-only); `exiftool -j -n` (I) | high -- D4 family, classic CTF |
| 62 | XMP packet (CreatorTool, DocumentID, InstanceID, history) + ICC profile desc | gap | `<x:xmpmeta` / `http://ns.adobe.com/xap/1.0/`; APP2 `ICC_PROFILE` | regex on bytes; `exiftool -XMP:all -j` (I) | med |
| 63 | PNG ancillary: tEXt/iTXt/zTXt, tIME, chunk order, bit depth/colour type, data after IEND | gap (target png-text-time) | chunk walk after sig | struct + zlib; `pngcheck -t -v` (I) | med-high -- D5 family |
| 64 | GIF version / logical screen / frame count / comment ext; BMP DIB dims; ICO count | gap (target gif-bmp-ico-wav) | `GIF89a` w,h u16LE @6; `BM`; `00 00 01 00` | struct; `identify` (I) | med |
| 65 | MP4/MOV: ftyp major brand, mvhd creation_time (1904 epoch), duration, `©xyz` GPS, `©too` encoder | gap | `ftyp` @4 | box walk struct; `mediainfo --Output=JSON` (I); `pymediainfo`/`ffprobe` (M) | low-med |
| 66 | Audio tags: ID3v2 TIT2/TPE1/COMM/APIC, ID3v1; WAV fmt + LIST/INFO; FLAC STREAMINFO + VORBIS_COMMENT | gap | `ID3` @0 / `TAG` @-128; `RIFF..WAVE`; `fLaC` | `mutagen.File(io.BytesIO(b))` (M); `wave` stdlib; `exiftool -j` (I) | low-med |
| 67 | GZIP header: FNAME, MTIME, OS, ISIZE; BZ2/XZ magic | gap (target archives) | `1f 8b 08`, flags @3, mtime u32LE @4, OS @9 | struct; `gzip -lv` | med |
| 68 | TAR: member names, ustar magic, mtime, uname/gname, mode | gap | `ustar` @257 | `tarfile.open(fileobj=io.BytesIO(b))` | med |
| 69 | 7z signature header version / RAR4 vs RAR5 / encrypted headers | gap | `37 7a bc af 27 1c` ver @6; `Rar!\x1a\x07\x00` / `\x01\x00` | `7z l -slt` (I); `py7zr`/`rarfile` (M) | med (D7 title punned 7z) |
| 70 | ZIP deeper: per-member CRC/method/DOS mtime/sizes/flags/encryption, comment, extra field IDs (0x5455 UT, 0x000a NTFS, 0x9901 AES, ZIP64) | prebuilt zip (extra-field VALUES, local-vs-CD mismatch = gap) | `PK\x03\x04` vs `PK\x01\x02` | `zipfile.ZipInfo` (`date_time`, `extra`, `flag_bits`) | high -- the container itself |
| 71 | ISO9660 PVD: volume id, system id, creation date, publisher; UDF/Joliet | gap | `CD001` @0x8001 | struct @0x8000; `isoinfo -d` (M); `7z l` (I); `pycdlib` (M) | med (ISO/IMG MOTW-bypass delivery) |
| 72 | VHD/VHDX/VMDK/QCOW2 headers (disk size, creator app, UUID, timestamp) | gap | VHD `conectix` in last 512 B; `vhdxfile`; `KDMV`/`# Disk DescriptorFile`; `QFI\xfb` | struct; `qemu-img info --output=json` (I) | low-med |
| 73 | MSIX/AppX: AppxManifest Identity Name/Publisher/Version, signature | gap | zip with `AppxManifest.xml`, `AppxSignature.p7x` | `zipfile` + `xml.etree` | med (installer line after MSI) |
| 74 | EML headers: Received chain (first hop/IP), Message-ID, Return-Path, X-Mailer, Date, Subject (RFC 2047), attachment names, DKIM `d=` | gap | text `Received:`/`From:`/`MIME-Version` | `email.message_from_bytes(b, policy=email.policy.default)` | high -- phishing staple |
| 75 | Outlook MSG (CFB): subject `__substg1.0_0037001F`, sender, transport headers `007D001F`, attachments; MBOX message count | gap | CFB with `__substg1.0_` streams; MBOX `From ` lines | olefile streams (I); `extract_msg` (M); `mailbox.mbox` (stdlib, path) | med |
| 76 | SQLite header: page size (u16BE @16, 1=65536), encoding @56, user_version @60, app id @68, tables, row counts | gap | `SQLite format 3\0` | struct; `sqlite3.connect(':memory:').deserialize(b)` (I, worker-only); `sqlite3` CLI (I) | med |
| 77 | Browser history: Chrome `urls`/`visits` (WebKit µs since 1601), Firefox `moz_places` (PRTime µs), downloads | gap | SQLite + table names | `sqlite3` queries | med |
| 78 | PCAP/PCAPNG header: magic/endianness, linktype, snaplen, packet count, IDB if_name, SHB hardware/OS | gap | `d4 c3 b2 a1`/`4d 3c b2 a1` (ns); `0a 0d 0d 0a` | struct; `dpkt.pcap.Reader(io.BytesIO(b))` (I, worker-only); `capinfos -M` (I) | med |
| 79 | PCAP content: DNS qnames, HTTP Host/User-Agent, TLS SNI, first/last timestamp | gap | as #78 | `tshark -r f -T fields -e dns.qry.name` (I); dpkt (I) | low-med (network lane overlap) |
| 80 | X.509: subject/issuer CN, serial, notBefore/notAfter, SHA-256/SHA-1 fingerprint, SAN | gap | `-----BEGIN CERTIFICATE-----` / DER `30 82` | `cryptography.x509.load_der_x509_certificate(b)` (I, worker-only); `openssl x509 -noout -text` (I) | med (Authenticode sibling) |
| 81 | PFX/PKCS#12 contents; PEM/DER key type+size; SSH pubkey fingerprint | gap | DER with pkcs12 OIDs; `ssh-ed25519 AAAA`; `-----BEGIN OPENSSH PRIVATE KEY-----` | `pkcs12.load_key_and_certificates(b, pw)`, `load_ssh_public_key` (I) | low-med |
| 82 | ELF header: e_machine, e_entry (speculative built-ins), class/data/type/shnum/phnum/flags, PT_INTERP, build-id, section names | partial (machine/entry) / gap (target elf-header) | `7f 45 4c 46`; EI_CLASS @4, EI_DATA @5, e_machine @18 | `elftools.elf.elffile.ELFFile(io.BytesIO(b))` (I); `readelf -hn` (I) | med (D9 flavor promised archs) |
| 83 | Mach-O thin/fat: cputype, filetype, ncmds, flags, LC_UUID, min OS / build version | gap (target macho-header) | `cf fa ed fe`/`ce fa ed fe`; fat `ca fe ba be` | struct; `lief.MachO.parse` (I); `rabin2 -I` (I); `macholib` (M) | low-med |
| 84 | Cross-file: md5/sha1 ordering, size ordering, duplicate detection (same hash, different names), magic-vs-extension liar | partial (D15 sha256 order only) | id `*-synthesis-*`, text "duplicate", "Files:" | `hashlib`, `collections.Counter` over member digests | high -- D15 opened the family |
| 85 | Cross-file timeline: sort members by embedded time (EXIF DateTimeOriginal, PE TimeDateStamp, LNK/zip mtime, OOXML created) | gap | text "earliest", "chronological", "timeline" | combine per-family extractors, ISO-8601 sort | med |

## Recognition cues (worker quick-reference)

```
4d 5a (MZ) .. "PE\0\0"@e_lfanew   PE      pefile.PE(data=b): FILE_HEADER / OPTIONAL_HEADER / DIRECTORY_ENTRY_{DEBUG,IMPORT,RESOURCE,SECURITY}
  + data dir 14 / "BSJB"          .NET    lib.meta.dotnet / dnfile.dnPE(data=b).net
  + data dir 4 non-zero           signed  lief.parse(b).signatures ; data dir 4 VirtualAddress is a FILE OFFSET
  + "RSDS"                        PDB     pe.DIRECTORY_ENTRY_DEBUG[i].entry.PdbFileName
  + "Rich" before PE              rich    pe.parse_rich_header(), pe.get_rich_header_hash()
7f 45 4c 46                       ELF     elftools ELFFile(io.BytesIO(b)); readelf -hn
cf fa ed fe / ce fa ed fe / ca fe ba be  Mach-O / fat   struct; rabin2 -I; lief
d0 cf 11 e0 a1 b1 1a e1           CFB     olefile.OleFileIO(b).listdir() then route by streams:
  !_StringPool + !Property          MSI     lib.meta.msi ; msiinfo (tools/msitools/usr/bin)
  WordDocument/Workbook/PowerPoint  Office  ole.get_metadata(); olevba (Macros/_VBA_PROJECT)
  DestList + hex streams            JumpList AppID = filename; streams = LNK
  __substg1.0_*                     MSG     subject 0037001F, headers 007D001F
  Catalog                           Thumbs.db
50 4b 03 04 (PK)                  ZIP     zipfile; then route by member names:
  [Content_Types].xml               OOXML   rels / docProps core,app,custom / settings.xml.rels template
  AppxManifest.xml                  MSIX    Identity Name/Publisher/Version
  META-INF/MANIFEST.MF / classes.dex  JAR/APK (mobile lane)
  mimetype=application/epub+zip     EPUB    META-INF/container.xml -> OPF dc:*
4c 00 00 00 01 14 02 00           LNK     lib.meta.lnk / LnkParse3; LinkInfo vs IDList may disagree
[InternetShortcut]                .url    URL= line
45 6c 66 46 69 6c 65 00 (ElfFile) EVTX    Evtx FileHeader(b,0).chunks() -> records -> rec.xml()
72 65 67 66 (regf)                Hive    struct base block; regipy (needs path) for keys/values
.. .. .. .. 53 43 43 41 (SCCA@4)  Prefetch v17/23/26/30; "MAM\x04"@0 = Win10 compressed (LZXpress Huffman)
01/02 00 00 00 00 00 00 00 + size $I      RecycleBin: size@8, FILETIME@16, path@24 (v1) / len@24 path@28 (v2)
46 49 4c 45 (FILE0)               $MFT    1024-B records; attr 0x10 $SI, 0x30 $FN (compare -> timestomp)
ff fe 3c 00 3f 00 78 00 (<?x)     UTF-16 XML: `<Task` + mit/task ns = TaskXML -> Actions/Exec/Command
ff fe 57 00 69 00 6e 00 (Win)     .reg    "Windows Registry Editor Version 5.00"
4d 53 43 46 (MSCF)                CAB     CFHEADER; 7z l -slt
25 50 44 46 2d (%PDF-)            PDF     header ver @5; trailer /Info; count %%EOF; pdfinfo / qpdf --json / pdfid
7b 5c 72 74 66 ({\rtf)            RTF     rtfobj (oletools) for \objdata
e4 52 5c 7b 8c d8 a7 4d           OneNote carve FileDataStoreObject
ff d8 ff                          JPEG    SOF dims; APP1 Exif -> PIL getexif()/get_ifd(0x8825) or exiftool -j -n
89 50 4e 47 0d 0a 1a 0a           PNG     IHDR@16; chunk walk tEXt/iTXt/zTXt/tIME; bytes after IEND
47 49 46 38 37/39 61              GIF     w,h u16LE @6/@8; 21 fe comment
42 4d (BM) / 00 00 01 00          BMP/ICO DIB w,h @18/@22 (i32) / count u16 @4
.. .. .. .. 66 74 79 70 (ftyp@4)  MP4/MOV box walk -> moov/mvhd creation_time (secs since 1904-01-01)
49 44 33 (ID3) / "TAG"@-128       MP3     ID3v2 frames TIT2/TPE1/COMM
52 49 46 46 .. 57 41 56 45        WAV     fmt (rate@24, ch@22), LIST/INFO
66 4c 61 43 (fLaC)                FLAC    STREAMINFO, block 4 VORBIS_COMMENT
1f 8b 08                          GZIP    FNAME if flg&8, MTIME u32LE@4, OS@9, ISIZE = last 4
"ustar" @257                      TAR     tarfile.open(fileobj=io.BytesIO(b))
37 7a bc af 27 1c                 7z      major/minor @6/@7; 7z l -slt
52 61 72 21 1a 07 00 / 01 00      RAR4/5
"CD001" @0x8001                   ISO     PVD @0x8000: system id @+8, volume id @+40, creation date @+813
"conectix" last 512 / vhdxfile / KDMV / QFI\xfb  VHD/VHDX/VMDK/QCOW2   qemu-img info --output=json
53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00  SQLite page size u16BE@16; sqlite3 .deserialize(b)
d4 c3 b2 a1 / a1 b2 c3 d4 / 0a 0d 0d 0a  PCAP/PCAPNG  linktype u32 @20; capinfos -M; dpkt
-----BEGIN CERTIFICATE----- / 30 82 ..  X.509   cryptography x509 load_*; openssl x509 -noout -text -fingerprint -sha256
Received: / Message-ID: / MIME-Version:  EML  email.message_from_bytes(b, policy=default); first hop = LAST Received
ef bb bf / ff fe / fe ff          BOM     text.*_bom_present
Time fields: FILETIME = 100ns since 1601 (/1e7 - 11644473600); WebKit = us since 1601; PRTime = us since 1970;
  Mac/MP4 = s since 1904; DOS date/time = 2-s resolution, local. Spelling unverified -> prefer ISO-8601 `Z` for `_utc`.
Hex fields: `0x` + lowercase, zero-padded to the STRUCT width (`_u16_hex` 4 digits, `_u32_hex` 8). GUIDs follow source.
```

## Readiness gaps

Ranking: priority 1 = plausible D16-D18 question with no extractor, or a harness blocker that silently fails a
whole family of prebuilds. TARGETS-style `fmt`/`fields` given in `detail` for prebuild items.

```json
[
  {"id": "gate-allowlist-dfir-libs", "concept": "Prebuild gate refuses installed DFIR libs", "priority": 1, "action": "note",
   "detail": "hctf/prebuild.py ALLOWED_IMPORTS lacks Evtx, regipy, olefile, oletools, dnfile, LnkParse3, lief, cryptography, asn1crypto, dpkt, PIL, sqlite3, wave, ordlookup. Targets evtx-records (python-evtx) and regf-values (regipy) as written will fail the gate exactly like pe-debug-rich-imports did (import ordlookup). Either widen the allowlist (all are in .venv) or rewrite those goals as stdlib/struct parsers. Also `open` is banned: regipy RegistryHive needs a path -> use a struct nk/vk walker."},
  {"id": "pe-debug-rich-imports", "concept": "PE PDB path / Rich header / imphash / imports / exports / Authenticode", "priority": 1, "action": "prebuild",
   "detail": "Re-run the REJECTED target without `import ordlookup` (pefile.PE.get_imphash already handles ordinals). fmt pe, fields debug_pdb_path, debug_codeview_guid, debug_codeview_age, rich_header_hash_md5, rich_header_xor_key_u32_hex, imphash, import_dll_names, export_names, export_dll_name. Do not re-register time_date_stamp_u32_hex (exists)."},
  {"id": "pe-authenticode", "concept": "PE Authenticode signer / cert serial / thumbprint / signing time", "priority": 1, "action": "prebuild",
   "detail": "fmt pe, fields is_signed, security_dir_size_u32_hex, signer_subject_cn, signer_issuer_cn, signer_serial_hex, signer_cert_sha1, signer_cert_sha256, signing_time_utc. Data dir 4 VirtualAddress is a file offset; WIN_CERTIFICATE (len u32, rev 0x0200, type 2) + PKCS#7 SignedData. Needs asn1crypto/cryptography in ALLOWED_IMPORTS or a minimal stdlib DER walker."},
  {"id": "evtx-records", "concept": "EVTX record fields (EventID, TimeCreated, Provider, Channel, Computer, count)", "priority": 1, "action": "prebuild",
   "detail": "Existing TARGET (fmt evtx: record_count, first_event_id, first_time_created_utc, provider_names, channel, computer_name) + event_ids (ordered list), last_event_record_id, event_data_<name> family. Blocked by gate-allowlist-dfir-libs unless a stdlib BinXML walker is written (template substitution makes that ~400 lines; widening the allowlist for Evtx is cheaper)."},
  {"id": "regf-values", "concept": "Registry key/value lookups (Run keys, last-write, counts, UserAssist)", "priority": 1, "action": "prebuild",
   "detail": "Existing TARGET (fmt regf: run_key_values, last_written_utc, subkey_count, value_count, userassist_entries) + value_<path> family, computer_name, timezone_key_name. Use a struct nk/vk/lf/lh/ri walker over hbins (stdlib) since regipy needs a file path and is not allowlisted."},
  {"id": "recycle-bin-i", "concept": "Recycle Bin $I original path / deletion time / size", "priority": 1, "action": "prebuild",
   "detail": "Split from target jumplist-recycle-mft so it lands alone: fmt recycle (also alias fmt recyclebin), fields original_path, deleted_time_utc, original_size, format_version. v1: header=1, size u64@8, FILETIME@16, UTF-16 path 520 B@24; v2: header=2, path chars u32@24, path@28. Pure struct, ~40 lines."},
  {"id": "prefetch", "concept": "Prefetch exe name / run count / last run times / volume info", "priority": 1, "action": "prebuild",
   "detail": "Existing TARGET (fmt prefetch: executable_name, run_count, last_run_time_utc, format_version, prefetch_hash_u32_hex, volume_serial_u32_hex) + last_run_times_utc (list of 8), volume_device_path, referenced_file_count. Uncompressed SCCA v17/23/26/30 is struct-only; Win10 MAM\\x04 needs an LZXpress-Huffman decoder (stdlib port ~120 lines, or tool dissect.util)."},
  {"id": "task-xml", "concept": "Scheduled task XML (Command, Arguments, Author, Date, URI, Triggers)", "priority": 1, "action": "prebuild",
   "detail": "fmt task (aliases scheduled_task, task_xml), fields exec_command, exec_arguments, registration_author, registration_date, uri, principal_user_id, run_level, trigger_types, hidden. UTF-16LE BOM XML, ns http://schemas.microsoft.com/windows/2004/02/mit/task; xml.etree with local-name matching."},
  {"id": "ole-vba", "concept": "VBA macro project (module names, auto-exec, stomping)", "priority": 1, "action": "prebuild",
   "detail": "fmt vba (and ole alias fields), fields module_names, project_name, has_macros, autoexec_keywords, vba_stream_names, code_page. Reuse lib/meta/cfb.py cfb_streams; dir stream is MS-OVBA RLE-compressed (port the ~40-line decompressor, stdlib). Covers .doc/.xls CFB and OOXML word/vbaProject.bin."},
  {"id": "ooxml-siblings", "concept": "OOXML custom props / remote template / embeddings / internal rel targets", "priority": 1, "action": "prebuild",
   "detail": "fmt ooxml, fields custom_properties (JSON name->value), attached_template_target, internal_relationship_targets, relationship_types, embedded_object_names, has_vba_project, main_part_content_type, hyperlink_count. Mirror D15 conventions (compact JSON, sorted for gathered sets). external_relationship_targets is verified -- do not re-register."},
  {"id": "synthesis-siblings", "concept": "Cross-file md5/sha1/size ordering, duplicates, timeline", "priority": 1, "action": "note",
   "detail": "Generalize the day15 `_digest_order` into lib.meta (fmt synthesis): <algo>-order for md5/sha1/sha256/sha512, size-order, duplicate-groups, earliest/latest by embedded timestamp. Parse algo + direction from id/text; treat any unrecognized `metadata-day-NN-synthesis-*` id as a worker escalation, never a lookup."},
  {"id": "eml-headers", "concept": "EML headers (Received chain, Message-ID, Return-Path, attachments)", "priority": 2, "action": "prebuild",
   "detail": "fmt eml, fields message_id, return_path, from_address, subject, date_utc, first_received_ip (last Received header), received_hops, x_mailer, attachment_names, dkim_domain. stdlib email.message_from_bytes(b, policy=email.policy.default)."},
  {"id": "jumplist", "concept": "Jump list AutomaticDestinations AppID + DestList + embedded LNK targets", "priority": 2, "action": "prebuild",
   "detail": "fmt jumplist, fields app_id (from member filename), destlist_entry_count, destlist_paths, lnk_stream_names, first_target_path. cfb_streams + reuse prebuilt lnk parser on each numeric stream. DestList v3/v4 entry layout struct."},
  {"id": "pdf-info", "concept": "PDF Info dict / page count / %%EOF count / Encrypt / JS", "priority": 2, "action": "prebuild",
   "detail": "Existing TARGET (fmt pdf: info_title ... encrypted) + has_javascript, open_action_present, embedded_file_names, xmp_creator_tool. Handle /ObjStm via zlib. pdf.header_version is verified -- don't touch."},
  {"id": "exif", "concept": "JPEG EXIF Make/Model/DateTimeOriginal/GPS", "priority": 2, "action": "prebuild",
   "detail": "Existing TARGET (fmt jpeg: exif_make ... app_segments) + exif_software, exif_gps_longitude, exif_gps_decimal, xmp_creator_tool. Pure-Python TIFF IFD walker (II/MM), GPS rationals -> decimal degrees; spelling unknown -> also store DMS."},
  {"id": "png-text-time", "concept": "PNG tEXt/iTXt/zTXt/tIME, chunk order, trailing data", "priority": 2, "action": "prebuild",
   "detail": "Existing TARGET (fmt png: text_chunks, time_chunk, chunk_names, ihdr_bit_depth, ihdr_color_type) + trailing_bytes_after_iend, text_<keyword> family."},
  {"id": "mft-record", "concept": "$MFT FILE record $SI vs $FN timestamps, name, parent", "priority": 2, "action": "prebuild",
   "detail": "fmt mft, fields file_name, record_number, parent_record_number, si_created_utc, si_modified_utc, fn_created_utc, fn_modified_utc, timestomp_suspected, is_directory, resident_data_hex_16. Apply update-sequence fixups first."},
  {"id": "elf-header", "concept": "ELF header / PT_INTERP / build-id / sections", "priority": 2, "action": "prebuild",
   "detail": "Existing TARGET (fmt elf); pyelftools is allowlisted. Don't re-register e_machine_u16_hex / e_entry_hex / entry_point_hex."},
  {"id": "archives", "concept": "GZIP/TAR/7z/RAR/ISO headers", "priority": 2, "action": "prebuild",
   "detail": "Existing TARGET (fmt gzip) + separate modules tar (member_names, ustar_magic, member_mtimes_utc, member_unames), 7z (signature_version, next_header_offset), rar (version), iso (primary_volume_id, system_id, volume_creation_date, publisher_id). Headers only."},
  {"id": "x509-cert", "concept": "X.509 subject/issuer/serial/validity/fingerprint", "priority": 2, "action": "prebuild",
   "detail": "fmt x509 (alias cert), fields subject_cn, issuer_cn, serial_hex, not_before_utc, not_after_utc, sha256_fingerprint, sha1_fingerprint, san_dns_names. Shares the DER walker with pe-authenticode; cryptography needs the allowlist."},
  {"id": "sqlite-header", "concept": "SQLite header + table names + browser history", "priority": 2, "action": "prebuild",
   "detail": "fmt sqlite, fields page_size, text_encoding, user_version, application_id_u32_hex, table_names, page_count. Header is pure struct; table names via sqlite_master page-1 b-tree walk (stdlib), or allowlist sqlite3 (`connect(':memory:').deserialize(b)`, Py3.12 has it)."},
  {"id": "pcap-header", "concept": "PCAP/PCAPNG global header, linktype, packet count, interfaces", "priority": 3, "action": "prebuild",
   "detail": "fmt pcap / pcapng, fields magic_u32_hex, version, linktype, snaplen, packet_count, first_packet_time_utc, if_names (pcapng IDB if_name option 2), shb_os. Pure struct."},
  {"id": "media-tags", "concept": "MP4 mvhd / ID3 / WAV INFO / FLAC Vorbis", "priority": 3, "action": "prebuild",
   "detail": "Modules mp4 (ftyp_major_brand, mvhd_creation_time_utc, duration_seconds), mp3 (id3_title, id3_artist, id3_comment, id3_version), wav (fmt_sample_rate, fmt_channels, info_<tag>), flac (streaminfo_sample_rate, vorbis_<tag>). Pure struct."},
  {"id": "macho-header", "concept": "Mach-O cputype/filetype/ncmds/LC_UUID", "priority": 3, "action": "prebuild",
   "detail": "Existing TARGET (fmt macho)."},
  {"id": "rtf-onenote", "concept": "RTF \\objdata OLE1 objects, OneNote embedded files", "priority": 3, "action": "prebuild",
   "detail": "fmt rtf: object_class_names, object_count, template_target, info_author; fmt onenote: embedded_file_count, embedded_file_sha256s. Hex-decode \\objdata, OLE1 header (class name len-prefixed)."},
  {"id": "tool-mutagen-pypdf", "concept": "Media tag + PDF python libs for the worker", "priority": 2, "action": "tool",
   "detail": "uv pip install mutagen pypdf pymediainfo exifread (all pure-Python; worker-side convenience -- exiftool already covers most fields)."},
  {"id": "tool-dfir-parsers", "concept": "Prefetch / MFT / MSG / archive libs", "priority": 2, "action": "tool",
   "detail": "uv pip install dissect.util (LZXpress Huffman for Win10 prefetch), python-registry, extract_msg, py7zr, rarfile, pycdlib, analyzeMFT, windowsprefetch. apt: genisoimage (isoinfo), libscca-utils (sccainfo), osslsigncode."},
  {"id": "msitools-path", "concept": "msitools present but not on PATH", "priority": 3, "action": "note",
   "detail": "tools/msitools/usr/bin/{msiinfo,msidump,msiextract,gcab} exist but `source bin/env.sh` doesn't expose them; add a bin/ shim. reference/techniques/metadata-forensics.md still says 'Not installed: msitools, LnkParse3, dnfile' -- all three are now present (LnkParse3 + dnfile in .venv)."}
]
```
