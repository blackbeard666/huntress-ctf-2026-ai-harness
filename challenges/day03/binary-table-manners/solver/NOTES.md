# Table Manners (Day 03 binary, managed-configuration) solver notes

Concept: evidence.zip (AES, pw `infected`) = per-day groups `d01--*` (Day 1 C ELF), `d02--*` (Day 2 C++ build with
HCFG config; ELF or MinGW PE in variants), `d03--*.dll` + `d03--*.runtimeconfig.json` (.NET 8 assembly). Answer ids
`dNN_artifact_sha256_K` (K-th member of the group, archive order) and `dNN_analysis_<field>`; Mastery adds `setN.`.

.NET config: HCFG blob ('HCFG' u8 ver, u8 xor key, u16 len, u32 crc32, xor'd JSON) stored as the
`<PrivateImplementationDetails>` FieldRVA static array (`__StaticArrayInitTypeSize=N`); `Campaign()` IL reads
key=blob[5], len=blob[6]|blob[7]<<8 and xors from blob[12]. The solver just scans for the HCFG magic in the file.

GM-confirmed (single solve 2026-10-04): section_names = pyelftools iter_sections() INCLUDING "" (NULL section);
symbols = non-empty .symtab names in order (dupes kept); PE machine 0x14c = `i386`; metadata_version = BSJB root
version string; d02 values identical to Day 2.

UNRESOLVED: d01 disassembly (capstone intel recover_code / main / whole .text rejected) and the .NET `format`
(pe, dotnet, pe32, .net, cil rejected). See single_solve/notes.md.
